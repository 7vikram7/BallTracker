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
        "settings": {"record": srv.record, "phone_reduction": getattr(srv, "reduce", True), "detector_overrides": srv.detector_overrides, "hold_s": srv.judge.hold_s,
                     "window_s": srv.judge.window_s, "corroborate": srv.judge.corroborate,
                     "play_mode": getattr(srv, "play_mode", "match")},
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
        "reduced": getattr(c, "reduced", False), "skipped_by_phone": getattr(c, "skipped_by_phone", 0),
        "fps_in": round(c.fps_in(), 1), "drops": c.drops, "unsynced": c.unsynced, "seq_gaps": c.seq_gaps,
        "proc_fps": c.stats.get("proc_fps"), "busy": c.stats.get("busy"), "latency_ms": c.stats.get("latency_ms"),
        "bounces": c.stats.get("bounces"), "clock": c.clock.summary(),
        # server-side load: candidates per frame after the ROI filter, tracks alive, time spent checking tracks
        "cands_per_frame": c.stats.get("cands_per_frame"), "max_tracks": c.stats.get("max_tracks"),
        "check_ms_per_s": c.stats.get("check_ms_per_s"),
        # backlog guard: frames whose periodic bounce check was skipped / frames dropped as stale
        "deferred_frames": c.stats.get("deferred_frames"), "dropped_stale": c.stats.get("dropped_stale"),
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


def host_load(prev: dict | None = None) -> dict:
    """The Mac's load, logged every 10 s as ``host_stats`` (field test 3 could only estimate it).

    * ``cpu_pct``: all processes' CPU, in % of the whole machine (100 = every logical core busy),
      from ``ps`` (a short moving average per process);
    * ``server_pct``: this server process alone (one core = 100), from its own CPU time;
    * ``load1``: 1-minute load average; ``top_other``: the busiest process that is not BallTracker.
    """
    import os
    import resource
    import subprocess

    out: dict = {"load1": round(os.getloadavg()[0], 2), "cores": os.cpu_count()}
    now = time.monotonic()
    ru = resource.getrusage(resource.RUSAGE_SELF)
    cpu_s = ru.ru_utime + ru.ru_stime
    if prev and now > prev["_t"]:
        out["server_pct"] = round(100 * (cpu_s - prev["_cpu"]) / (now - prev["_t"]), 1)
    out["_t"], out["_cpu"] = now, cpu_s
    try:
        txt = subprocess.run(["ps", "-A", "-o", "%cpu=,comm="], capture_output=True, text=True, timeout=2).stdout
        rows = []
        for ln in txt.splitlines():
            parts = ln.strip().split(None, 1)
            if len(parts) == 2:
                try:
                    rows.append((float(parts[0]), parts[1]))
                except ValueError:
                    pass
        total = sum(r[0] for r in rows)
        out["cpu_pct"] = round(total / max(os.cpu_count() or 1, 1), 1)
        others = [r for r in rows if "python" not in r[1].lower()]
        if others:
            pct, comm = max(others)
            out["top_other"] = {"name": os.path.basename(comm)[:40], "pct": round(pct, 1)}
    except (OSError, subprocess.SubprocessError):
        pass
    return out

