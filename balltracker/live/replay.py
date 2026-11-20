"""Re-run a recorded live session with the current code, and compare.

    bt replay data/live/sessions/20261118-101500

Uses what the session folder holds:
  * app phones: ``<camera>/dets.jsonl`` (every frame's detections): exact replay
    of tracking, bounce detection, fusion and calls;
  * browser phones: ``<camera>/frames.bin`` + ``index.csv`` (needs ``--record``):
    the detector runs again on every frame;
  * ``calibration/<camera>.json`` (or the last ``calibrated`` event), ``court.json``,
    and serve-context changes from ``events.jsonl``.

The live run may differ from a replay for reasons that aren't logic changes: frames
the live worker dropped when the Mac was overloaded (replay processes all of
them), and report arrival order. With app phones and no drops, a replay with
unchanged code reproduces the live decisions exactly; tests rely on that.
"""

from __future__ import annotations

import csv
import gzip
import json
from pathlib import Path

import numpy as np

from ..detection import Candidate
from ..events import BounceEvent
from ..geometry.camera import Camera
from ..geometry.court import CourtSpec, ServiceSide, Side
from ..sports.pickleball.line_calling import LineCallConfig, PickleballLineCaller, ServeContext
from .fusion import LiveJudge
from .worker import LiveCameraPipeline, LiveConfig

ARRIVAL_DELAY_S = 0.25  # typical report delay after the bounce (settle time + processing)


def read_events(session: Path) -> list[dict]:
    p = Path(session) / "events.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # a line cut short by a crash
    return out


def load_session(session: Path | str) -> dict:
    session = Path(session)
    if not (session / "court.json").exists():
        raise FileNotFoundError(f"{session} is not a session folder (no court.json)")
    court = CourtSpec.from_dict(json.loads((session / "court.json").read_text()))
    events = read_events(session)
    manifest = json.loads((session / "session.json").read_text()) if (session / "session.json").exists() else None
    last_calib = {e["camera"]: e["camera_model"] for e in events if e.get("type") == "calibrated" and e.get("camera_model")}
    cams = {}
    for d in sorted(p for p in session.iterdir() if p.is_dir() and p.name not in ("calibration", "replays")):
        kind = "edge" if _dets_path(d) else ("browser" if (d / "index.csv").exists() else None)
        if kind is None:
            continue
        cam = None
        snap = session / "calibration" / f"{d.name}.json"
        if snap.exists():
            cam = Camera.load(snap)
        elif d.name in last_calib:
            cam = Camera.from_dict(last_calib[d.name])
        con = [e for e in events if e.get("type") == "camera_connected" and e.get("camera") == d.name]
        regularize = bool(con[-1].get("regularize_time")) if con else False
        cams[d.name] = {"kind": kind, "dir": d, "camera": cam, "regularize_time": regularize}
    contexts = [(e["t"], e["context"]) for e in events if e.get("type") == "context"]
    return {"dir": session, "court": court, "events": events, "manifest": manifest, "cameras": cams, "contexts": contexts}


def _dets_path(folder: Path) -> Path | None:
    """``dets.jsonl``, or ``dets.jsonl.gz`` (how large sessions are stored in git)."""
    for name in ("dets.jsonl", "dets.jsonl.gz"):
        if (folder / name).exists():
            return folder / name
    return None


def _iter_edge(folder: Path):
    path = _dets_path(folder)
    text = gzip.decompress(path.read_bytes()).decode() if path.suffix == ".gz" else path.read_text()
    for line in text.splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            continue
        yield r["seq"], r["ts"], r["c"], (r.get("w", 0), r.get("h", 0))


def _iter_browser(folder: Path):
    import cv2

    with open(folder / "index.csv") as f, open(folder / "frames.bin", "rb") as fb:
        for row in csv.DictReader(f):
            fb.seek(int(row["offset"]))
            img = cv2.imdecode(np.frombuffer(fb.read(int(row["nbytes"])), np.uint8), cv2.IMREAD_COLOR)
            if img is not None:
                yield int(row["seq"]), float(row["t_session"]), img


def camera_reports(name: str, info: dict, court: CourtSpec, detector_overrides: dict | None = None) -> list[BounceEvent]:
    """Run one camera's recording through the streaming pipeline; return its bounce reports."""
    cfg = LiveConfig()
    for k, v in (detector_overrides or {}).items():
        if hasattr(cfg.detector, k):
            setattr(cfg.detector, k, tuple(v) if isinstance(v, list) else v)
    pipe = LiveCameraPipeline(name, court, info["camera"], cfg)
    pipe.set_time_regularization(info.get("regularize_time", False))
    out: list[dict] = []
    if info["kind"] == "edge":
        for seq, ts, cl, size in _iter_edge(info["dir"]):
            cands = [Candidate(u=u, v=v, radius_px=r, score=sc, area_px=float(np.pi * r * r), elongation=1.0)
                     for u, v, r, sc in cl]
            if size == (0, 0) and info["camera"] is not None:
                size = tuple(info["camera"].image_size)
            out += pipe.process_candidates(seq, ts, cands, size)
    else:
        for seq, ts, img in _iter_browser(info["dir"]):
            out += pipe.process(seq, ts, img)
    out += pipe.flush()
    return [BounceEvent.model_validate(o["event"]) for o in out if o.get("kind") == "bounce"]


def _parse_context(ctx: str) -> ServeContext | None:
    if not ctx.startswith("serve:"):
        return None
    _, side, svc = ctx.split(":")
    return ServeContext(Side(side.upper()), ServiceSide(svc.lower()))


def judge_reports(court: CourtSpec, cameras: dict, reports: dict[str, list[BounceEvent]], contexts=(),
                  hold_s: float = 0.6) -> list[dict]:
    """Feed all cameras' reports to a LiveJudge in (estimated) arrival order."""
    from .server import camera_can_see, decision_dict

    models = {n: c["camera"] for n, c in cameras.items()}
    judge = LiveJudge(court, PickleballLineCaller(court, LineCallConfig()), hold_s=hold_s,
                      can_see=lambda n, x, y: camera_can_see(models.get(n), court, x, y))
    expected = {n for n, m in models.items() if m is not None}
    queue = sorted(((ev.t + ARRIVAL_DELAY_S, ev) for evs in reports.values() for ev in evs), key=lambda a: a[0])
    ctx = sorted(contexts)
    ci = 0
    out: list[dict] = []
    for arrival, ev in queue:
        out += [decision_dict(d, None) for d in judge.poll(arrival, expected)]
        while ci < len(ctx) and ctx[ci][0] <= arrival:
            judge.serve = _parse_context(ctx[ci][1])
            ci += 1
        judge.add(ev, arrival)
    out += [decision_dict(d, None) for d in judge.flush()]
    return out


def replay(session: Path | str, detector_overrides: dict | None = None, hold_s: float | None = None) -> dict:
    s = load_session(session)
    if hold_s is None:
        hold_s = ((s["manifest"] or {}).get("settings") or {}).get("hold_s", 0.6)
    if detector_overrides is None:
        detector_overrides = ((s["manifest"] or {}).get("settings") or {}).get("detector_overrides") or {}
    reports = {n: camera_reports(n, info, s["court"], detector_overrides) for n, info in s["cameras"].items()}
    decisions = judge_reports(s["court"], s["cameras"], reports, s["contexts"], hold_s)
    live = [e for e in s["events"] if e.get("type") == "decision"]
    return {"session": str(s["dir"]), "cameras": {n: {"kind": c["kind"], "calibrated": c["camera"] is not None,
                                                     "reports": len(reports[n])} for n, c in s["cameras"].items()},
            "decisions": decisions, "live_decisions": live, "comparison": compare(live, decisions)}


def _call(d: dict) -> str:
    if d.get("suppressed"):
        return "suppressed"
    return f"{d.get('result')}{' (spoken)' if d.get('announce') else ''}"


def compare(old: list[dict], new: list[dict], tol_s: float = 0.05, moved_cm: float = 1.0) -> dict:
    """Match decisions by bounce time; list calls that changed, moved, appeared or disappeared."""
    used: set[int] = set()
    pairs, only_old = [], []
    for o in old:
        best, bd = None, tol_s
        for j, n in enumerate(new):
            dt = abs(n["t"] - o["t"])
            if j not in used and dt <= bd:
                best, bd = j, dt
        if best is None:
            only_old.append(o)
        else:
            used.add(best)
            pairs.append((o, new[best]))
    only_new = [n for j, n in enumerate(new) if j not in used]
    changed, moved = [], []
    for o, n in pairs:
        dist = 100 * float(np.hypot(n["x"] - o["x"], n["y"] - o["y"]))
        row = {"t": o["t"], "old": _call(o), "new": _call(n), "moved_cm": round(dist, 2),
               "old_dist_cm": o.get("distance_cm"), "new_dist_cm": n.get("distance_cm")}
        if _call(o) != _call(n):
            changed.append(row)
        elif dist > moved_cm:
            moved.append(row)
    return {"matched": len(pairs), "changed": changed, "moved": moved,
            "only_live": [{"t": o["t"], "call": _call(o)} for o in only_old],
            "only_replay": [{"t": n["t"], "call": _call(n)} for n in only_new],
            "identical": not changed and not moved and not only_old and not only_new,
            "max_moved_cm": round(max((100 * float(np.hypot(n["x"] - o["x"], n["y"] - o["y"])) for o, n in pairs), default=0.0), 3)}


def format_comparison(res: dict) -> str:
    c = res["comparison"]
    lines = [f"Replay of {res['session']}"]
    for n, i in res["cameras"].items():
        lines.append(f"  {n}: {i['kind']}, {'calibrated' if i['calibrated'] else 'NOT calibrated'}, {i['reports']} bounce reports")
    lines.append(f"  decisions: live {len(res['live_decisions'])}, replay {len(res['decisions'])}, matched {c['matched']}")
    if c["identical"]:
        lines.append(f"  identical to the live session (largest shift {c['max_moved_cm']} cm)")
    for r in c["changed"]:
        lines.append(f"  CHANGED  t={r['t']:.3f}  {r['old']} -> {r['new']}  (moved {r['moved_cm']} cm)")
    for r in c["moved"]:
        lines.append(f"  moved    t={r['t']:.3f}  {r['old']}  by {r['moved_cm']} cm")
    for r in c["only_live"]:
        lines.append(f"  gone     t={r['t']:.3f}  {r['call']} (only in the live session)")
    for r in c["only_replay"]:
        lines.append(f"  new      t={r['t']:.3f}  {r['call']} (only in the replay)")
    return "\n".join(lines)


def save_replay(res: dict) -> Path:
    """Keep the replay next to the session, stamped with the code version that produced it."""
    import time

    from .session_log import algorithm_versions, git_info

    d = Path(res["session"]) / "replays"
    d.mkdir(exist_ok=True)
    p = d / f"replay-{time.strftime('%Y%m%d-%H%M%S')}.json"
    p.write_text(json.dumps({"git": git_info(), "versions": algorithm_versions(), **res}, indent=1, default=str))
    return p
