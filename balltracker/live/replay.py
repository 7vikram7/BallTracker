"""Re-run a recorded live session with the current code, and compare.

    bt replay data/live/sessions/20261118-101500

Uses what the session folder holds:
  * app phones: ``<camera>/dets.jsonl`` (every frame's detections): exact replay
    of tracking, bounce detection, fusion and calls;
  * browser phones: ``<camera>/frames.bin`` + ``index.csv`` (needs ``--record``):
    the detector runs again on every frame;
  * the calibration history from ``events.jsonl``: the model in use when the camera connected,
    then every ``calibrated`` event (clicks, automatic line snaps, drift corrections) from its
    time on; sessions without it use ``calibration/<camera>.json`` throughout. Bounces seen
    while the camera's calibration was too rough to be used (upkeep.MAX_RMS_PX) are left out,
    as the live server does;
  * ``court.json`` and serve-context changes from ``events.jsonl``.

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
        p = p.with_name("events.jsonl.gz")  # large sessions are stored compressed in git
        if not p.exists():
            return []
    text = gzip.decompress(p.read_bytes()).decode() if p.suffix == ".gz" else p.read_text()
    out = []
    for line in text.splitlines():
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # a line cut short by a crash
    return out


def load_session(session: Path | str, calibrations: Path | str | None = None) -> dict:
    """``calibrations``: a JSONL file of ``calibrated`` events (and ``camera_suspended`` /
    ``camera_resumed``) that replaces the session's own calibration history (a counterfactual: what
    a newer server's calibration upkeep would have used; see scripts/counterfactual_calibration.py)."""
    session = Path(session)
    if not (session / "court.json").exists():
        raise FileNotFoundError(f"{session} is not a session folder (no court.json)")
    court = CourtSpec.from_dict(json.loads((session / "court.json").read_text()))
    events = read_events(session)
    if calibrations is not None:
        sub = [json.loads(line) for line in Path(calibrations).read_text().splitlines() if line.strip()]
        kinds = {"calibrated", "camera_suspended", "camera_resumed"}
        events = [e for e in events if e.get("type") not in kinds] + [e for e in sub if e.get("type") in kinds]
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
        timeline = [(float(e["t"]), Camera.from_dict(e["camera_model"])) for e in events
                    if e.get("camera") == d.name and e.get("camera_model")
                    and e.get("type") in ("camera_connected", "calibrated")]
        ctl = [e for e in events if e.get("type") == "worker_ctl" and e.get("camera") == d.name]
        # sessions before 2026-11-21 ran MOG2 on JPEG cameras; later ones log the detector
        mac_detector = (con[-1].get("mac_detector") if con else None) or "mog2"
        fps = float(con[-1].get("fps") or 0) if con else 0.0
        # when the camera was connected (the live judge only expects connected cameras)
        online, t_on = [], None
        for e in events:
            if e.get("camera") != d.name:
                continue
            if e.get("type") == "camera_connected":
                t_on = float(e["t"]) if t_on is None else t_on
            elif e.get("type") == "camera_disconnected" and t_on is not None:
                online.append((t_on, float(e["t"])))
                t_on = None
        if t_on is not None:
            online.append((t_on, float("inf")))
        # sessions from 2026-11-21 on log the model in use at each connection; older ones don't,
        # and their judge replay keeps the last calibration throughout (as before)
        logged = bool(con) and all("camera_model" in e for e in con)
        cams[d.name] = {"kind": kind, "dir": d, "camera": cam, "regularize_time": regularize,
                        "suspended": suspended_intervals(events, d.name),
                        "timeline": sorted(timeline, key=lambda a: a[0]), "ctl": ctl,
                        "mac_detector": mac_detector, "fps": fps, "online": online if logged else None}
    if calibrations is not None:
        unknown = sorted({e.get("camera") for e in sub if e.get("type") == "calibrated"} - set(cams))
        if unknown:  # e.g. a scrubbed file (device names) against a local session (its own names)
            raise ValueError(f"{calibrations} names cameras this session doesn't have: {unknown} "
                             f"(session cameras: {sorted(cams)})")
    contexts = [(e["t"], e["context"]) for e in events if e.get("type") == "context"]
    # match (serves recognised) or drill: the mode at the start, then every change
    start_mode = ((manifest or {}).get("settings") or {}).get("play_mode", "match")
    modes = [(float("-inf"), start_mode)] + [(e["t"], e["mode"]) for e in events if e.get("type") == "play_mode"]
    return {"dir": session, "court": court, "events": events, "manifest": manifest, "cameras": cams, "contexts": contexts,
            "modes": modes}


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


def suspended_intervals(events: list[dict], name: str) -> list[tuple[float, float]]:
    """When the live server had the camera out of the calls because it moved since calibration
    (``camera_suspended`` .. ``camera_resumed``; a new calibration also resumes it)."""
    out, t0 = [], None
    for e in sorted((e for e in events if e.get("camera") == name), key=lambda e: float(e.get("t") or 0)):
        ty = e.get("type")
        if ty == "camera_suspended" and t0 is None:
            t0 = float(e["t"])
        elif ty in ("camera_resumed", "calibrated") and t0 is not None:
            out.append((t0, float(e["t"])))
            t0 = None
    if t0 is not None:
        out.append((t0, float("inf")))
    return out


def _within(spans, t: float) -> bool:
    return any(a <= t < b for a, b in spans)


def camera_reports(name: str, info: dict, court: CourtSpec, detector_overrides: dict | None = None,
                   max_rms_px: float | None = None) -> list[BounceEvent]:
    """Run one camera's recording through the streaming pipeline; return its bounce reports."""
    cfg = LiveConfig()
    cfg.mac_detector = info.get("mac_detector") or "mog2"
    if info.get("fps"):
        cfg.fps_hint = float(info["fps"])
    for k, v in (detector_overrides or {}).items():
        if hasattr(cfg.detector, k):
            setattr(cfg.detector, k, tuple(v) if isinstance(v, list) else v)
    from .upkeep import MAX_RMS_PX, calibration_ready

    lim = MAX_RMS_PX if max_rms_px is None else max_rms_px
    timeline = list(info.get("timeline") or [])
    first = timeline[0][1] if timeline else info["camera"]
    pipe = LiveCameraPipeline(name, court, first, cfg)
    pipe.set_time_regularization(info.get("regularize_time", False))
    out: list[dict] = []
    nxt = 1 if timeline else 0
    ready = calibration_ready(first, lim)
    # What the live worker did because of load (logged as worker_ctl), applied at the same frames:
    # dropped batches are skipped, bounce checks deferred, tracks flushed after silences.
    ctl = info.get("ctl") or []
    drops = [(int(e["seq0"]), int(e["seq1"])) for e in ctl if e.get("op") == "drop"]
    defers = sorted((int(e["seq"]), bool(e["on"])) for e in ctl if e.get("op") == "defer")
    flushes = {int(e["seq"]) for e in ctl if e.get("op") == "flush"}
    di = 0
    cur = [float("-inf")]  # session time of the frame being processed
    gaps: list[tuple[float, float]] = []
    span = [float("inf"), float("-inf")]

    def take(msgs: list[dict]) -> None:
        for o in msgs:
            if o.get("kind") == "gap":
                gaps.append((float(o["t0"]), float(o["t1"])))
            if o.get("kind") != "bounce":
                continue
            if ready and not _within(info.get("suspended") or (), cur[0]):
                out.append(o)
            else:
                info["excluded"] = info.get("excluded", 0) + 1

    def follow(ts: float) -> None:
        nonlocal nxt, ready
        cur[0] = ts
        while nxt < len(timeline) and timeline[nxt][0] <= ts:
            pipe.set_camera(timeline[nxt][1])
            ready = calibration_ready(timeline[nxt][1], lim)
            nxt += 1

    if info["kind"] == "edge":
        for seq, ts, cl, size in _iter_edge(info["dir"]):
            follow(ts)
            while di < len(defers) and defers[di][0] <= seq:
                pipe.defer_checks = defers[di][1]
                di += 1
            if any(a <= seq <= b for a, b in drops):
                continue
            cands = [Candidate(u=u, v=v, radius_px=r, score=sc, area_px=float(np.pi * r * r), elongation=1.0)
                     for u, v, r, sc in cl]
            if size == (0, 0) and pipe.camera is not None:
                size = tuple(pipe.camera.image_size)
            take(pipe.process_candidates(seq, ts, cands, size))
            span[0], span[1] = min(span[0], ts), max(span[1], ts)
            if seq in flushes:
                take(pipe.flush())
    else:
        for seq, ts, img in _iter_browser(info["dir"]):
            follow(ts)
            take(pipe.process(seq, ts, img))
            span[0], span[1] = min(span[0], ts), max(span[1], ts)
            if seq in flushes:
                take(pipe.flush())
    take(pipe.flush())
    info["gaps"], info["span"] = gaps, tuple(span)
    return [BounceEvent.model_validate(o["event"]) for o in out]


def _camera_reports_job(args):
    session, calibrations, name, overrides, max_rms_px = args
    s = load_session(session, calibrations)
    info = s["cameras"][name]
    r = camera_reports(name, info, s["court"], overrides, max_rms_px)
    return r, {k: info[k] for k in ("gaps", "span", "excluded") if k in info}


def _parse_context(ctx: str) -> ServeContext | None:
    if not ctx.startswith("serve:"):
        return None
    _, side, svc = ctx.split(":")
    return ServeContext(Side(side.upper()), None if svc == "?" else ServiceSide(svc.lower()))


def judge_reports(court: CourtSpec, cameras: dict, reports: dict[str, list[BounceEvent]], contexts=(),
                  hold_s: float = 0.6, modes=(), max_rms_px: float | None = None, weak_rate: float = 0.4) -> list[dict]:
    """Feed all cameras' reports to a LiveJudge in (estimated) arrival order."""
    from .server import camera_can_see, camera_view, covered, decision_dict

    from .upkeep import MAX_RMS_PX, calibration_ready

    lim = MAX_RMS_PX if max_rms_px is None else max_rms_px
    # can_see / view / expected cameras: as live, the calibration in use at the time and only while
    # the camera was connected (field 2026-11-22: a camera on yesterday's rough calibration, later
    # recalibrated, vetoed two calls in replay that live spoke). Older sessions without that log:
    # the last calibration throughout.
    last = {n: (c["timeline"][-1][1] if c.get("timeline") else c["camera"]) for n, c in cameras.items()}
    now = [float("-inf")]

    def model(n: str):
        c = cameras.get(n) or {}
        if c.get("online") is None:
            return last.get(n)
        t = now[0]
        if not any(a <= t <= b for a, b in c["online"]) or _within(c.get("suspended") or (), t):
            return None
        m = None
        for t0, cam in c.get("timeline") or ():
            if t0 > t:
                break
            m = cam
        return m

    def processed(n: str, t: float) -> bool:
        # Replay has every frame up front: covered if inside the recording and outside its gaps.
        c = cameras.get(n) or {}
        lo, hi = c.get("span", (float("-inf"), float("inf")))
        return lo <= t and covered(hi, c.get("gaps", ()), t)

    judge = LiveJudge(court, PickleballLineCaller(court, LineCallConfig()), hold_s=hold_s,
                      can_see=lambda n, x, y: camera_can_see(model(n), court, x, y),
                      view=lambda n, x, y: camera_view(model(n), x, y), processed=processed,
                      weak_rate=weak_rate)
    queue = sorted(((ev.t + ARRIVAL_DELAY_S, ev) for evs in reports.values() for ev in evs), key=lambda a: a[0])
    ctx = sorted(contexts)
    md = sorted(modes, key=lambda a: a[0])
    ci = mi = 0
    out: list[dict] = []
    def poll(t: float) -> list[dict]:
        # Decide each held bounce when live would have (the server polls every 50 ms): when its wait
        # ran out, not at the next report's arrival, which may be seconds later on another calibration.
        res = []
        while True:
            # (+1 us: first_arrival + hold_s - first_arrival can round to just under hold_s)
            due = sorted(x + 1e-6 for g in judge._groups for x in (g.first_arrival + judge.weak_wait_s,
                                                                  g.first_arrival + judge.hold_s)
                         if now[0] < x + 1e-6 < t)
            if not due:
                break
            now[0] = due[0]
            res += judge.poll(due[0], {n for n in cameras if calibration_ready(model(n), lim)})
        now[0] = t
        return res + judge.poll(t, {n for n in cameras if calibration_ready(model(n), lim)})

    for arrival, ev in queue:
        out += [decision_dict(d, None) for d in poll(arrival)]
        while ci < len(ctx) and ctx[ci][0] <= arrival:
            judge.serve = _parse_context(ctx[ci][1])
            ci += 1
        while mi < len(md) and md[mi][0] <= arrival:
            judge.play.cfg.serve_detection = md[mi][1] != "drill"
            mi += 1
        judge.add(ev, arrival)
    out += [decision_dict(d, None) for d in judge.flush()]
    return out


def replay(session: Path | str, detector_overrides: dict | None = None, hold_s: float | None = None,
           max_rms_px: float | None = None, calibrations: Path | str | None = None, workers: int = 1) -> dict:
    """``max_rms_px``: calibrations rougher than this are not used for calls (default
    upkeep.MAX_RMS_PX, as live; ``float("inf")`` to replay sessions from before that rule).
    ``calibrations``: replace the calibration history (see ``load_session``). ``workers`` > 1:
    one process per camera (a 68-minute session: about 20 minutes instead of an hour)."""
    s = load_session(session, calibrations)
    if hold_s is None:
        hold_s = ((s["manifest"] or {}).get("settings") or {}).get("hold_s", 0.6)
    if detector_overrides is None:
        detector_overrides = ((s["manifest"] or {}).get("settings") or {}).get("detector_overrides") or {}
    if workers > 1 and len(s["cameras"]) > 1:
        from concurrent.futures import ProcessPoolExecutor

        names = list(s["cameras"])
        with ProcessPoolExecutor(min(workers, len(names))) as ex:
            done = list(ex.map(_camera_reports_job, [(session, calibrations, n, detector_overrides, max_rms_px)
                                                     for n in names]))
        reports = {}
        for n, (r, extra) in zip(names, done):
            reports[n] = r
            s["cameras"][n].update(extra)
    else:
        reports = {n: camera_reports(n, info, s["court"], detector_overrides, max_rms_px)
                   for n, info in s["cameras"].items()}
    weak_rate = ((s["manifest"] or {}).get("settings") or {}).get("weak_rate", 0.4)  # bt serve --strict-veto: 0
    decisions = judge_reports(s["court"], s["cameras"], reports, s["contexts"], hold_s, s["modes"], max_rms_px,
                              weak_rate)
    live = [e for e in s["events"] if e.get("type") == "decision"]
    return {"session": str(s["dir"]), "cameras": {n: {"kind": c["kind"], "calibrated": c["camera"] is not None,
                                                     "reports": len(reports[n]), "excluded": c.get("excluded", 0),
                                                     "calibrations": len(c.get("timeline") or [])}
                                                 for n, c in s["cameras"].items()},
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
