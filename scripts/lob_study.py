#!/usr/bin/env python3
"""What happens to lobs in the line-calling pipeline? A simulation study on mock data.

Builds a full-size court with four corner cameras (2.4 m tripods, two at 120 fps and two at
60 fps, calibrated from noisy clicks like the dashboard), simulates shots with gravity, drag
and bounce physics, projects the ball into every camera as detections (pixel noise, dropouts,
ball outside the frame = not detected), writes a normal session folder and runs the real
replay: tracking -> bounce detection + physics check -> fusion -> play state -> line call.
The same session is also replayed after the phone-side reducer (scripts/reduce_dets.mjs).

Scenarios (hitter on side A, landing on side B near the baseline, offsets inside/outside):
  drive, offensive lob (apex ~3 m), defensive lob (~6 m), moonball (~9 m), sideline lob.
Each shot is played two ways: "rally" (the ball bounced on side A 0.35 s before the lob) and
"volley" (no bounce for many seconds before: the lob was hit out of the air).
After landing the ball is not returned, so it bounces a second time.

Usage: .venv/bin/python scripts/lob_study.py [--out DIR] [--quick] [--rig 2good+2weak] [--no-reducer]
(--rig: other camera set-ups, see RIGS and docs/CAMERA_RIGS.md)
Prints a report and writes report.json in the output folder.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from balltracker import bounce as bounce_mod  # noqa: E402
from balltracker.geometry.calib_check import NET_TOP_POINTS  # noqa: E402
from balltracker.geometry.camera import Camera, calibrate_from_points  # noqa: E402
from balltracker.geometry.court import CourtSpec  # noqa: E402
from balltracker.synthetic import BallPhysics, Shot, aim_shot, simulate  # noqa: E402

W, H = 1920, 1080


# ------------------------------------------------------------------ cameras
@dataclass
class SimCam:
    name: str
    true: Camera
    fps: float
    calib: Camera | None = None
    size: tuple[int, int] = (W, H)
    px_noise: float = 0.4  # detection jitter (px)
    dropout: float = 0.02  # missed detections
    t_jitter_s: float = 0.0  # frame timestamp jitter (weak phones: uneven frame pacing)
    click_px: float = 1.5  # calibration click noise


def _fits(cam: Camera, court: CourtSpec, margin: float = 0.03) -> bool:
    W, H = cam.image_size
    hw, hl = court.half_w, court.half_l
    pts = np.array([[x, y, 0] for x in (-hw - 0.3, hw + 0.3) for y in (-hl - 0.3, hl + 0.3)], float)
    if np.any(cam.depth(pts) <= 0):
        return False
    uv = cam.project(pts)
    return bool(np.all((uv[:, 0] > margin * W) & (uv[:, 0] < (1 - margin) * W)
                       & (uv[:, 1] > margin * H) & (uv[:, 1] < (1 - margin) * H)))


def corner_camera(court: CourtSpec, name: str, sx: int, sy: int, fps: float, height: float = 2.4,
                  size: tuple[int, int] = (W, H), **quality) -> SimCam:
    """Tripod 1.5 m outside the sideline, 3 m behind the baseline, aimed so the whole court
    (+30 cm) is in frame with the main lens if possible, else the 0.5x lens."""
    hw, hl = court.half_w, court.half_l
    pos = np.array([sx * (hw + 1.5), sy * (hl + 3.0), height])
    for fov in (69.0, 80.0, 106.0):
        best = None
        for ty in np.linspace(-hl, hl, 41):
            for tx in np.linspace(-hw, hw, 9):
                cam = Camera.look_at(pos, np.array([tx, ty, 0.0]), size, fov, camera_id=name)
                if _fits(cam, court):
                    # prefer the aim that puts the court highest in the frame (more sky -> ball visible longer)
                    top = float(cam.project(np.array([[0, -sy * hl, 0.0]]))[0, 1])
                    if best is None or top > best[0]:
                        best = (top, cam)
        if best:
            return SimCam(name, best[1], fps, size=size, **quality)
    raise RuntimeError(f"court does not fit camera {name}")


def calibrate(sc: SimCam, court: CourtSpec, rng: np.random.Generator) -> Camera:
    W, H = sc.size
    kp = {k: v for k, v in court.keypoints().items() if k not in NET_TOP_POINTS}
    obj = np.array(list(kp.values()), float)
    uv = sc.true.project(obj)
    ok = (sc.true.depth(obj) > 0) & (uv[:, 0] > 0) & (uv[:, 0] < W) & (uv[:, 1] > 0) & (uv[:, 1] < H)
    clicks = uv[ok] + rng.normal(0, sc.click_px, (int(ok.sum()), 2))
    return calibrate_from_points(obj[ok], clicks, (W, H), hfov_guess_deg=65.0, camera_id=sc.name)


# ------------------------------------------------------------------ shots
SHOTS = {
    # name: (start y as fraction of half length on side A, start height, flight time to first bounce)
    "drive": (-0.95, 0.8, 0.9),
    "offensive lob": (-0.35, 0.7, 1.55),
    "defensive lob": (-0.45, 0.6, 2.2),
    "moonball": (-0.30, 0.6, 2.7),
}
OFFSETS = (-0.30, -0.10, -0.03, 0.03, 0.10, 0.30)  # landing beyond (+) / inside (-) the line, metres


@dataclass
class Scenario:
    shot: str
    target: np.ndarray
    line: str
    offset: float
    variant: str  # "rally" | "volley"


def scenarios(court: CourtSpec, quick: bool) -> list[Scenario]:
    hw, hl = court.half_w, court.half_l
    out = []
    offs = OFFSETS[1:5] if quick else OFFSETS
    for shot in SHOTS:
        for off in offs:
            for variant in ("rally", "volley"):
                out.append(Scenario(shot, np.array([0.8, hl + off]), "baseline_B", off, variant))
        if shot != "drive":  # lobs over a sideline
            for off in (-0.10, 0.10):
                out.append(Scenario(shot, np.array([hw + off, hl - 2.0]), "sideline", off, "rally"))
    return out


@dataclass
class TrueBounce:
    t: float
    x: float
    y: float
    scenario: int
    kind: str  # "feed" (side A, before the lob), "first", "second", "later" (3rd+ bounce)
    v_in: np.ndarray


def build(court: CourtSpec, scs: list[Scenario], rng: np.random.Generator):
    phys = BallPhysics()
    r = court.ball_radius
    hl = court.half_l
    segs, truth = [], []
    t = 1.0
    for i, sc in enumerate(scs):
        fy, z0, flight = SHOTS[sc.shot]
        start = np.array([rng.uniform(-1.5, 1.5), fy * hl, z0])
        if sc.variant == "rally":
            # The incoming ball: from side B, bounces on side A 0.35 s before the lob is hit.
            fstart = np.array([rng.uniform(-2, 2), hl * 0.8, 0.9])
            ftarget = start[:2] + np.array([0.0, 1.5])
            fv = aim_shot(fstart, ftarget, 1.0, r, phys)
            ts, pos, bs, vs = _sim(Shot(fstart, fv, t, 1.0 + 0.35), r, phys)
            segs.append((ts, pos))
            for (tb, xb, yb), vb in zip(bs, vs):
                truth.append(TrueBounce(tb, xb, yb, i, "feed", vb))
            start = pos[-1].copy()
            t = ts[-1] + 1 / 4800
        v = aim_shot(start, sc.target, flight, r, phys)
        ts, pos, bs, vs = _sim(Shot(start, v, t, flight + 2.6), r, phys)
        segs.append((ts, pos))
        for j, ((tb, xb, yb), vb) in enumerate(zip(bs, vs)):
            if j >= 2 and vb[2] > -1.0:
                break  # the ball is rolling to a stop: not a bounce anyone could see
            truth.append(TrueBounce(tb, xb, yb, i, ("first", "second")[j] if j < 2 else "later", vb))
        t = ts[-1] + 6.0  # the point is over; nothing in view for a while
    return segs, truth


def _sim(shot: Shot, r: float, phys: BallPhysics):
    ts, pos, bs = simulate(shot, r, phys)
    vel = np.gradient(pos, ts, axis=0)
    vs = [vel[max(int(np.searchsorted(ts, tb)) - 3, 0)] for tb, _, _ in bs]
    return ts, pos, bs, vs


# ------------------------------------------------------------------ detections
def write_session(folder: Path, court: CourtSpec, cams: list[SimCam], segs, rng: np.random.Generator) -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "court.json").write_text(json.dumps(court.to_dict()))
    (folder / "calibration").mkdir(exist_ok=True)
    (folder / "events.jsonl").write_text("")
    t_end = max(ts[-1] for ts, _ in segs) + 0.5
    vis = {}
    for sc in cams:
        sc.calib.save(folder / "calibration" / f"{sc.name}.json")
        d = folder / sc.name
        d.mkdir(exist_ok=True)
        W, H = sc.size
        frame_t = np.arange(0.0, t_end, 1 / sc.fps) + rng.uniform(0, 1 / sc.fps)
        stamp_t = frame_t + (rng.normal(0, sc.t_jitter_s, len(frame_t)) if sc.t_jitter_s else 0.0)
        seen = np.zeros(len(frame_t), bool)
        with open(d / "dets.jsonl", "w") as f:
            seg_i = 0
            for k, tf in enumerate(frame_t):
                c = []
                while seg_i < len(segs) - 1 and tf > segs[seg_i][0][-1]:
                    seg_i += 1
                ts, pos = segs[seg_i]
                if ts[0] <= tf <= ts[-1] and rng.random() > sc.dropout:
                    j = int(np.searchsorted(ts, tf))
                    j = min(max(j, 1), len(ts) - 1)
                    a = (tf - ts[j - 1]) / (ts[j] - ts[j - 1])
                    X = pos[j - 1] * (1 - a) + pos[j] * a
                    dep = float(sc.true.depth(X[None])[0])
                    if dep > 0.3:
                        u, v = sc.true.project(X[None])[0] + rng.normal(0, sc.px_noise, 2)
                        rad = float(sc.true.K[0, 0] * court.ball_radius / dep)
                        if 0 <= u < W and 0 <= v < H and rad >= 1.0:
                            c.append([round(u, 3), round(v, 3), round(rad, 3), 0.9])
                            seen[k] = True
                ts_k = round(float(stamp_t[k]), 6)
                f.write(json.dumps({"seq": k, "tp": ts_k, "ts": ts_k, "w": W, "h": H, "c": c}) + "\n")
        vis[sc.name] = (frame_t, seen)
    return vis


def visible_before(vis, cam: str, tb: float, max_s: float = 3.0) -> float:
    """How long (s) the camera saw the ball continuously right before the contact."""
    ft, seen = vis[cam]
    k = int(np.searchsorted(ft, tb)) - 1
    n, gaps = 0, 0
    while k >= 0 and tb - ft[k] <= max_s:
        if seen[k]:
            n, gaps = k, 0
        else:
            gaps += 1
            if gaps > 3:
                break
        k -= 1
    return float(tb - ft[n]) if n else 0.0


# ------------------------------------------------------------------ run + report
def reduce_session(src: Path, dst: Path, cams: list[SimCam]) -> dict:
    import shutil

    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("dets.jsonl", "replays"))
    stats = {}
    for sc in cams:
        r = subprocess.run(["node", str(ROOT / "scripts" / "reduce_dets.mjs"), str(src / sc.name / "dets.jsonl"),
                            str(dst / sc.name / "dets.jsonl")], capture_output=True, text=True, cwd=ROOT)
        if r.returncode != 0:
            raise RuntimeError(r.stderr)
        stats[sc.name] = json.loads(r.stderr.strip().splitlines()[-1])
    return stats


def run_replay(folder: Path):
    from balltracker.live.replay import replay

    rejected = []
    orig = bounce_mod.BounceDetector._plausible

    def spy(self, ph, noise):
        ok = orig(self, ph, noise)
        if not ok:
            rejected.append({"camera": self.camera.camera_id, **{k: ph.get(k) for k in
                             ("rejected", "rms_in_px", "rms_out_px", "turn_deg", "vz_in", "vz_out", "e", "h_ratio")}})
        return ok

    bounce_mod.BounceDetector._plausible = spy
    try:
        orig_fin = bounce_mod.BounceDetector._finalise

        def fin(self, c, t, uv, track):
            n0 = len(rejected)
            ev = orig_fin(self, c, t, uv, track)
            for r in rejected[n0:]:
                r["t"] = float(c["tb"])
            return ev

        bounce_mod.BounceDetector._finalise = fin
        res = replay(folder)
    finally:
        bounce_mod.BounceDetector._plausible = orig
        bounce_mod.BounceDetector._finalise = orig_fin
    return res, rejected


def truth_call(court: CourtSpec, x: float, y: float) -> str:
    d = float(court.court_rect().distance_outside(np.array(x), np.array(y)))
    return "OUT" if d > court.contact_patch_radius else "IN"


def analyse(court, scs, truth, res, rejected, vis, cams):
    dec = res["decisions"]
    rows = []
    for tb in truth:
        sc = scs[tb.scenario]
        m = min(dec, key=lambda d: abs(d["t"] - tb.t), default=None)
        matched = m is not None and abs(m["t"] - tb.t) < 0.05
        rej = [r for r in rejected if abs(r.get("t", -9) - tb.t) < 0.05]
        rows.append({
            "scenario": tb.scenario, "shot": sc.shot, "variant": sc.variant, "line": sc.line, "offset_m": sc.offset,
            "kind": tb.kind, "t": round(tb.t, 3), "x": round(tb.x, 3), "y": round(tb.y, 3),
            "truth": truth_call(court, tb.x, tb.y),
            "true_h_in": round(float(np.hypot(*tb.v_in[:2])), 2), "true_vz_in": round(float(tb.v_in[2]), 2),
            "angle_deg": round(float(np.degrees(np.arctan2(-tb.v_in[2], np.hypot(*tb.v_in[:2])))), 1),
            "visible_before_s": {c.name: round(visible_before(vis, c.name, tb.t), 2) for c in cams},
            "detected": matched,
            "cameras": sorted(m["cameras"]) if matched else [],
            "err_cm": round(100 * float(np.hypot(m["x"] - tb.x, m["y"] - tb.y)), 1) if matched else None,
            "result": m.get("result") if matched else None,
            "announce": bool(m.get("announce")) if matched else False,
            "suppressed": m.get("suppressed") if matched else None,
            "play": m.get("play") if matched else None,
            "h_in_est": m.get("h_in_mps") if matched else None,
            "unconfirmed_by": m.get("unconfirmed_by") if matched else None,
            "inflation": m.get("inflation") if matched else None,
            "rejections": [(r["camera"], r["rejected"], round(r["rms_in_px"] or 0, 1), round(r["turn_deg"] or 0))
                           for r in rej],
        })
    extra = [d for d in dec if all(abs(d["t"] - tb.t) >= 0.05 for tb in truth)]
    return rows, extra


def summarise(rows, extra, label: str) -> list[str]:
    L = [f"\n=== {label} ==="]
    first = [r for r in rows if r["kind"] == "first"]
    by = defaultdict(list)
    for r in first:
        by[(r["shot"], r["variant"])].append(r)
    L.append(f"{'shot':15s} {'variant':7s} {'n':>3s} {'det':>4s} {'2cam':>4s} {'err cm':>7s} {'wrongOUT':>8s} "
             f"{'missedOUT':>9s} {'angle':>6s} {'h_in':>5s} {'est':>5s}  play labels")
    for (shot, var), rs in by.items():
        det = [r for r in rs if r["detected"]]
        errs = [r["err_cm"] for r in det]
        wrong = sum(r["announce"] and r["result"] == "OUT" and r["truth"] == "IN" for r in rs)
        missed = sum(r["truth"] == "OUT" and not (r["announce"] and r["result"] == "OUT") for r in rs)
        n_out = sum(r["truth"] == "OUT" for r in rs)
        labels = Counter(r["play"] for r in det)
        est = [r["h_in_est"] for r in det if r["h_in_est"] is not None]
        L.append(f"{shot:15s} {var:7s} {len(rs):3d} {len(det):4d} {sum(len(r['cameras']) >= 2 for r in det):4d} "
                 f"{(np.median(errs) if errs else float('nan')):7.1f} {wrong:8d} {missed:5d}/{n_out:<3d} "
                 f"{np.median([r['angle_deg'] for r in rs]):6.0f} {np.median([r['true_h_in'] for r in rs]):5.1f} "
                 f"{(np.median(est) if est else float('nan')):5.1f}  {dict(labels)}")
    sec = [r for r in rows if r["kind"] == "second"]
    sd = [r for r in sec if r["detected"]]
    L.append(f"second bounces: {len(sec)}, detected {len(sd)}, suppressed {sum(bool(r['suppressed']) for r in sd)}, "
             f"announced {sum(r['announce'] for r in sd)} "
             f"(labels {dict(Counter(r['play'] for r in sd))})")
    later = [r for r in rows if r["kind"] == "later" and r["detected"]]
    L.append(f"later (3rd+) bounces detected: {len(later)}, announced {sum(r['announce'] for r in later)}")
    feed = [r for r in rows if r["kind"] == "feed"]
    L.append(f"feed bounces (side A): {len(feed)}, detected {sum(r['detected'] for r in feed)}")
    outs = [r for r in first if r["truth"] == "OUT" and r["detected"]]
    vetoed = [r for r in outs if r.get("unconfirmed_by")]
    L.append(f"OUT first bounces silenced by the 'another camera saw nothing' veto: {len(vetoed)} "
             f"(by {dict(Counter(c for r in vetoed for c in r['unconfirmed_by']))})")
    L.append("cameras reporting each first bounce: " + str(dict(Counter(c for r in first for c in r["cameras"]))))
    rej = Counter(x[1] for r in rows for x in r["rejections"])
    L.append(f"physics rejections at true bounces: {dict(rej)}")
    L.append(f"extra (false) decisions: {len(extra)}; announced: {sum(bool(d.get('announce')) for d in extra)}")
    return L


# Weak Android phones (e.g. a budget phone in a browser): 30 fps, 1280x720, blurrier ball (larger
# jitter), more missed frames, uneven frame pacing, coarser clicks. "ok" = a decent budget phone in
# good light; "poor" = an old phone / dim light. These are assumptions, not measurements.
WEAK = {"ok": dict(size=(1280, 720), px_noise=1.0, dropout=0.08, t_jitter_s=0.003, click_px=2.0),
        "poor": dict(size=(1280, 720), px_noise=2.5, dropout=0.20, t_jitter_s=0.006, click_px=2.5)}


def _two_good(court):
    # The current rig: iPhone (120 fps) and Samsung (60 fps) at opposite ends, diagonal corners.
    return [corner_camera(court, "B-left-120", -1, 1, 120), corner_camera(court, "A-right-60", 1, -1, 60)]


RIGS = {
    "4corner": lambda c: [corner_camera(c, "B-left-120", -1, 1, 120), corner_camera(c, "B-right-60", 1, 1, 60),
                          corner_camera(c, "A-left-120", -1, -1, 120), corner_camera(c, "A-right-60", 1, -1, 60)],
    "2good": _two_good,
    "2good+2weak": lambda c: _two_good(c) + [corner_camera(c, "B-right-30w", 1, 1, 30, **WEAK["ok"]),
                                             corner_camera(c, "A-left-30w", -1, -1, 30, **WEAK["ok"])],
    "2good+2poor": lambda c: _two_good(c) + [corner_camera(c, "B-right-30p", 1, 1, 30, **WEAK["poor"]),
                                             corner_camera(c, "A-left-30p", -1, -1, 30, **WEAK["poor"])],
    "1good+2weak": lambda c: _two_good(c)[:1] + [corner_camera(c, "B-right-30w", 1, 1, 30, **WEAK["ok"]),
                                                 corner_camera(c, "A-left-30w", -1, -1, 30, **WEAK["ok"])],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/experiments/lob_study")
    ap.add_argument("--quick", action="store_true", help="fewer scenarios")
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--rig", default="4corner", choices=sorted(RIGS), help="camera set-up (see RIGS)")
    ap.add_argument("--no-reducer", action="store_true", help="skip the phone-side reducer replay")
    a = ap.parse_args()
    out = ROOT / a.out
    rng = np.random.default_rng(a.seed)
    court = CourtSpec.pickleball()
    cams = RIGS[a.rig](court)
    for sc in cams:
        sc.calib = calibrate(sc, court, rng)
        print(f"{sc.name}: hfov {np.degrees(2 * np.arctan(sc.size[0] / 2 / sc.true.K[0, 0])):.0f} deg, "
              f"calibration rms {sc.calib.reprojection_rms_px:.2f} px", flush=True)
    scs = scenarios(court, a.quick)
    segs, truth = build(court, scs, rng)
    vis = write_session(out / "session", court, cams, segs, rng)
    print(f"{len(scs)} scenarios, {len(truth)} true bounces, {segs[-1][0][-1]:.0f} s of play", flush=True)

    report = {}
    lines = []
    runs = [("all frames", out / "session")] + ([] if a.no_reducer else [("phone-side reducer", out / "session_reduced")])
    for label, folder in runs:
        if label == "phone-side reducer":
            stats = reduce_session(out / "session", folder, cams)
            report["reducer_stats"] = stats
            lines.append("\nreducer: " + ", ".join(f"{k} {v['framesOut']}/{v['framesIn']} frames" for k, v in stats.items()))
        res, rejected = run_replay(folder)
        rows, extra = analyse(court, scs, truth, res, rejected, vis, cams)
        report[label] = {"rows": rows, "extra": extra}
        lines += summarise(rows, extra, label)
    print("\n".join(lines))
    (out / "report.json").write_text(json.dumps(report, indent=1, default=float))
    print(f"\nreport: {out / 'report.json'}")


if __name__ == "__main__":
    main()
