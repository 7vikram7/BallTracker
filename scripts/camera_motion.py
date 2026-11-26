#!/usr/bin/env python3
"""How did each camera move during a recorded session, and what would that do to the calls?

Registers every preview snapshot (one each ~2 s with ``--record``) against the frame of the last
calibration made by hand before it, from the static background (ORB + RANSAC homography, as the
live drift check does; matches with fewer than ``MIN_INLIERS`` inliers, e.g. a player filling the
view, are left out), and writes per snapshot:

* ``moved_px``: median shift of the calibration's keypoints (what the drift check acts on);
* the rotation as pan / tilt / roll in degrees (a phone on a mount moves by rotating: the
  homography of a pure rotation is K R K^-1, K from the calibration);
* ``ground_err_cm``: the error it would cause with the calibration left as it was (court corners
  mapped through the motion and back with the old calibration; max over the 4 corners).

    .venv/bin/python scripts/camera_motion.py data/live/sessions/<id> out_dir

Writes ``out_dir/motion_<camera>.csv``, ``out_dir/motion.json`` (per hand calibration: largest and
final motion, motion at 1, 5, 10 ... minutes, steps) and ``out_dir/motion.png`` (if matplotlib is
installed). No images are written; the snapshots show people and stay local.
"""

from __future__ import annotations

import csv
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from balltracker.geometry.camera import Camera  # noqa: E402
from balltracker.geometry.court import CourtSpec  # noqa: E402
from balltracker.geometry.drift import DriftReference, estimate_motion  # noqa: E402



def snapshot_index(folder: Path) -> list[tuple[float, int, int]]:
    idx = folder / "index.csv"
    if not idx.exists():
        return []
    with open(idx) as f:
        return [(float(r["t_session"]), int(r["offset"]), int(r["nbytes"])) for r in csv.DictReader(f)]


def read_snapshot(folder: Path, offset: int, nbytes: int):
    with open(folder / "frames.bin", "rb") as fb:
        fb.seek(offset)
        buf = fb.read(nbytes)
    return cv2.imdecode(np.frombuffer(buf, np.uint8), cv2.IMREAD_COLOR)


def rotation_of(H: np.ndarray, K: np.ndarray) -> np.ndarray:
    """Nearest rotation to K^-1 H K (exact when the camera only rotated)."""
    M = np.linalg.inv(K) @ H @ K
    M = M / np.cbrt(np.linalg.det(M))
    U, _, Vt = np.linalg.svd(M)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        R = -R
    return R


def angles_deg(R: np.ndarray) -> tuple[float, float, float]:
    """(pan, tilt, roll): rotation about the camera's y (vertical), x (horizontal), z (optical) axes.
    Positive pan turns the view right, positive tilt turns it down (OpenCV axes: x right, y down)."""
    rv, _ = cv2.Rodrigues(R)
    rx, ry, rz = np.degrees(rv.ravel())
    return float(ry), float(rx), float(rz)


def ground_error_cm(H: np.ndarray, cam: Camera, court: CourtSpec) -> float:
    G = cam.ground_homography()  # court (X, Y) -> pixel
    hw, hl = court.width / 2, court.length / 2
    err = 0.0
    for X, Y in ((-hw, -hl), (hw, -hl), (-hw, hl), (hw, hl)):
        p = G @ np.array([X, Y, 1.0])
        q = H @ p
        P = np.linalg.solve(G, q)
        err = max(err, float(np.hypot(P[0] / P[2] - X, P[1] / P[2] - Y)))
    return err * 100


MIN_INLIERS = 150   # weaker matches (a player filling the view) are left out
SMOOTH = 5          # running median over this many snapshots (~10 s)


def references(session: Path, name: str) -> list[tuple[float, dict, Camera]]:
    """(time, keypoints, camera) of each calibration made by hand (clicks, snaps) for this camera:
    the frame nearest that time is the reference until the next one. Automatic corrections (drift,
    re-snaps) are not references: the motion is measured against what the person set up."""
    out = []
    for line in (session / "events.jsonl").read_text().splitlines():
        e = json.loads(line)
        if e.get("type") == "calibrated" and e.get("camera") == name and e.get("camera_model") \
                and str(e.get("source", "")).startswith("click"):
            out.append((float(e["t"]), e["clicked"], Camera.from_dict(e["camera_model"])))
    if not out and (session / "calibration" / f"{name}.json").exists():
        cam = Camera.load(session / "calibration" / f"{name}.json")
        out.append((float("-inf"), None, cam))
    return out


def trace_camera(args) -> dict:
    """Motion of each snapshot against the frame of the last hand calibration before it."""
    from balltracker.geometry.crosscal import visible_keypoints
    from balltracker.geometry.drift import move_points

    session, name, court_d = args
    session = Path(session)
    folder = session / name
    court = CourtSpec.from_dict(court_d)
    refs = references(session, name)
    index = snapshot_index(folder)
    rows = []
    ri, ref, base, cam = -1, None, None, None
    for t, off, nb in index:
        while ri + 1 < len(refs) and refs[ri + 1][0] <= t + 1.0:
            ri += 1
            ref = None
        if ri < 0:
            continue  # not calibrated yet
        if ref is None:
            img = read_snapshot(folder, off, nb)
            if img is None:
                continue
            _, pts, cam = refs[ri]
            base = {k: list(map(float, v)) for k, v in (pts or visible_keypoints(cam, court)).items()}
            ref = DriftReference(img)
            rows.append({"t": round(t, 2), "epoch": ri, "ok": 1, "inliers": len(ref.kp), "moved_px": 0.0,
                         "pan_deg": 0.0, "tilt_deg": 0.0, "roll_deg": 0.0, "ground_err_cm": 0.0})
            continue
        img = read_snapshot(folder, off, nb)
        mot = estimate_motion(ref, img) if img is not None else None
        if mot is None or mot["inliers"] < MIN_INLIERS:
            rows.append({"t": round(t, 2), "epoch": ri, "ok": 0, "inliers": mot["inliers"] if mot else 0})
            continue
        H = mot["H"] / mot["H"][2, 2]
        moved = move_points(H, base)
        med = float(np.median([np.hypot(moved[k][0] - u, moved[k][1] - v) for k, (u, v) in base.items()]))
        pan, tilt, roll = angles_deg(rotation_of(H, cam.K))
        rows.append({"t": round(t, 2), "epoch": ri, "ok": 1, "inliers": mot["inliers"], "moved_px": round(med, 1),
                     "pan_deg": round(pan, 3), "tilt_deg": round(tilt, 3), "roll_deg": round(roll, 3),
                     "ground_err_cm": round(ground_error_cm(H, cam, court), 1)})
    return {"camera": name, "focal_px": float(refs[0][2].K[0, 0]) if refs else 0.0, "rows": rows}


def smoothed(rows: list[dict], key: str) -> list[float]:
    v = [r[key] for r in rows]
    h = SMOOTH // 2
    return [float(np.median(v[max(0, i - h):i + h + 1])) for i in range(len(v))]


def summarise(tr: dict) -> dict:
    """Per hand calibration (epoch): how far the camera moved from it, how fast it crept, and the
    steps (a change of >= 5 px in the smoothed motion within ~10 s that stays)."""
    out = {"camera": tr["camera"], "snapshots": len(tr["rows"]), "matched": sum(r["ok"] for r in tr["rows"]),
           "px_per_deg": round(tr["focal_px"] * np.pi / 180, 1), "epochs": []}
    for ep in sorted({r["epoch"] for r in tr["rows"]}):
        rows = [r for r in tr["rows"] if r["epoch"] == ep and r["ok"]]
        if len(rows) < SMOOTH:
            continue
        m = smoothed(rows, "moved_px")
        t = [r["t"] for r in rows]
        steps, i = [], SMOOTH
        while i < len(rows) - SMOOTH:
            before, after = np.median(m[i - SMOOTH:i]), np.median(m[i:i + SMOOTH])
            if abs(after - before) >= 5.0:
                steps.append({"t": t[i], "from_px": round(float(before), 1), "to_px": round(float(after), 1)})
                i += SMOOTH
            else:
                i += 1
        ang = [smoothed(rows, k) for k in ("pan_deg", "tilt_deg", "roll_deg")]
        out["epochs"].append({
            "from_t": t[0], "to_t": t[-1], "minutes": round((t[-1] - t[0]) / 60, 1),
            "matched": len(rows), "unmatched": sum(1 for r in tr["rows"] if r["epoch"] == ep and not r["ok"]),
            "max_px": round(max(m), 1), "end_px": round(m[-1], 1),
            "end_deg": {"pan": round(ang[0][-1], 2), "tilt": round(ang[1][-1], 2), "roll": round(ang[2][-1], 2)},
            "max_ground_err_cm": round(max(smoothed(rows, "ground_err_cm")), 1),
            "steps": steps,
            "px_at_minutes": {f"{k}": round(float(np.interp(t[0] + 60 * k, t, m)), 1)
                              for k in (1, 5, 10, 20, 30, 45, 60) if t[0] + 60 * k <= t[-1]},
        })
    return out


def plot(traces: list[dict], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(len(traces), 1, figsize=(11, 2.6 * len(traces)), sharex=True, squeeze=False)
    for ax, tr in zip(axes[:, 0], traces):
        rows = [r for r in tr["rows"] if r["ok"]]
        t = [r["t"] / 60 for r in rows]
        ax.plot(t, smoothed(rows, "moved_px"), lw=1, label="moved px (smoothed)")
        lost = [r["t"] / 60 for r in tr["rows"] if not r["ok"]]
        ax.plot(lost, [0] * len(lost), "|", color="k", ms=6, alpha=0.4, label="no match")
        ax.set_ylabel(f"{tr['camera']}\npx")
        ax.grid(alpha=0.3)
        ax.legend(loc="upper left", fontsize=7, ncol=4)
    axes[-1, 0].set_xlabel("session minute")
    fig.tight_layout()
    fig.savefig(path, dpi=110)


def main() -> None:
    session, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    court_d = json.loads((session / "court.json").read_text())
    names = sorted(p.parent.name for p in session.glob("*/index.csv"))
    with ProcessPoolExecutor(max_workers=min(3, len(names))) as ex:
        traces = list(ex.map(trace_camera, [(str(session), n, court_d) for n in names]))
    for tr in traces:
        keys = ["t", "epoch", "ok", "inliers", "moved_px", "pan_deg", "tilt_deg", "roll_deg", "ground_err_cm"]
        with open(out / f"motion_{tr['camera']}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, keys, restval="")
            w.writeheader()
            w.writerows(tr["rows"])
    summary = [summarise(tr) for tr in traces]
    (out / "motion.json").write_text(json.dumps(summary, indent=1))
    for s in summary:
        print(json.dumps({k: v for k, v in s.items() if k != "epochs"}))
        for e in s["epochs"]:
            print("   epoch", json.dumps(e))
    try:
        plot(traces, out / "motion.png")
    except ImportError:
        print("(matplotlib not installed: no plot)")


if __name__ == "__main__":
    main()
