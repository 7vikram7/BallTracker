"""Session records: what ran, with which code and settings, and how it went.

Every ``bt serve`` session folder gets:

* ``session.json``: manifest written at start (time, command, git commit, algorithm
  versions, court, settings), completed at the end with a summary (per-camera health,
  calls). Enough to know later exactly what produced the results.
* ``events.jsonl``: one JSON object per line: connections (with device/app details),
  calibrations (full camera model + per-point errors), camera health every 5 s,
  bounce reports, decisions, warnings.
* ``calibration/<camera>.json``: snapshot of each camera model used in the session.
* with ``--record``: ``<camera>/frames.bin + index.csv`` (browser phones: every frame;
  app phones: the 1 Hz previews) and ``<camera>/dets.jsonl`` (app phones: every frame's
  detections).

``bt replay`` re-runs a session with the current code; ``bt report`` summarises it.
"""

from __future__ import annotations

import json
import platform
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git_info() -> dict:
    def run(*args: str) -> str | None:
        try:
            r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, timeout=5)
            return r.stdout.strip() if r.returncode == 0 else None
        except (OSError, subprocess.SubprocessError):
            return None

    commit = run("rev-parse", "HEAD")
    status = run("status", "--porcelain")
    return {
        "commit": commit or "no commits",
        "branch": run("rev-parse", "--abbrev-ref", "HEAD"),
        "changed_files": len(status.splitlines()) if status else 0,
    }


def algorithm_versions() -> dict:
    from .. import bounce, edge_detection
    from ..detection import MotionColorBallDetector
    from . import fusion, protocol

    try:
        from importlib.metadata import version

        pkg = version("balltracker")
    except Exception:  # pragma: no cover - not installed
        pkg = "unknown"
    return {
        "balltracker": pkg,
        "bounce": bounce.ALGO_VERSION,
        "fusion": fusion.ALGO_VERSION,
        "mac_detector": f"{MotionColorBallDetector.name} {MotionColorBallDetector.version}",
        "phone_detector": f"{edge_detection.ALGO} {edge_detection.ALGO_VERSION}",
        "protocol": protocol.PROTO_VERSION,
    }


def build_manifest(srv) -> dict:
    return {
        "kind": "balltracker.session",
        "schema": 1,
        "session": srv.session_dir.name,
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "command": " ".join(sys.argv),
        "host": {"python": platform.python_version(), "platform": platform.platform(), "machine": platform.machine()},
        "git": git_info(),
        "versions": algorithm_versions(),
        "court": srv.court.to_dict(),
        "settings": {"record": srv.record, "detector_overrides": srv.detector_overrides, "hold_s": srv.judge.hold_s,
                     "window_s": srv.judge.window_s, "corroborate": srv.judge.corroborate},
        "summary": None,
    }


def write_manifest(srv) -> None:
    p = srv.session_dir / "session.json"
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(srv.manifest, indent=2, default=str))
    tmp.replace(p)


def camera_health(c) -> dict:
    """One camera's numbers, as logged every 5 s and in the final summary."""
    return {
        "camera": c.name, "mode": c.mode, "connected": c.connected, "frames_in": c.frames_in,
        "fps_in": round(c.fps_in(), 1), "drops": c.drops, "unsynced": c.unsynced, "seq_gaps": c.seq_gaps,
        "proc_fps": c.stats.get("proc_fps"), "busy": c.stats.get("busy"), "latency_ms": c.stats.get("latency_ms"),
        "bounces": c.stats.get("bounces"), "clock": c.clock.summary(),
        "calib_rms_px": c.camera.reprojection_rms_px if c.camera else None,
        "phone": c.phone_stats,
    }


def finalize(srv) -> None:
    decisions = [e for e in srv.all_decisions]
    calls: dict[str, int] = {}
    for d in decisions:
        k = "suppressed" if d.get("suppressed") else str(d.get("result"))
        calls[k] = calls.get(k, 0) + 1
    lat = sorted(d["latency_s"] for d in decisions if d.get("latency_s") is not None)
    srv.manifest["ended_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    srv.manifest["summary"] = {
        "duration_s": round(srv.now(), 1),
        "cameras": [camera_health(c) | {"device": c.device, "app": c.app, "width": c.width, "height": c.height,
                                        "fps_req": c.fps_req, "ts_source": c.ts_source}
                    for c in sorted(srv.cams.values(), key=lambda c: c.name)],
        "reports": srv.n_reports,
        "decisions": len(decisions),
        "calls": calls,
        "announced": sum(1 for d in decisions if d.get("announce")),
        "latency_s": {"median": lat[len(lat) // 2], "max": lat[-1]} if lat else None,
    }
    write_manifest(srv)
