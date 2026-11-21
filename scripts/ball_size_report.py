#!/usr/bin/env python3
"""Ball-size check on a recorded session: blob radius / a ball's radius there, per camera and
distance band, and each bounce's margin to the not-a-ball limit (LiveConfig: ratio x ball + slack).

    .venv/bin/python scripts/ball_size_report.py data/field/<id> [--calibrations FILE] [--workers 3]

Replays the cameras (as bt replay does) and reads ``r_ratio`` from each bounce report.
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from balltracker.live.replay import _camera_reports_job, load_session  # noqa: E402
from balltracker.live.worker import LiveConfig  # noqa: E402

BANDS = ((0, 8), (8, 14), (14, 99))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--calibrations")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    s = load_session(a.session, a.calibrations)
    names = list(s["cameras"])
    with ProcessPoolExecutor(max(1, min(a.workers, len(names)))) as ex:
        done = list(ex.map(_camera_reports_job, [(a.session, a.calibrations, n, None, None) for n in names]))
    cfg = LiveConfig()
    r = s["court"].ball_radius
    print(f"limit: blob radius > {cfg.max_ball_radius_ratio} x ball radius + {cfg.ball_radius_slack_px} px")
    print(f"{'camera':10} {'band m':7} {'n':>4} {'median':>6} {'p99.5':>6} {'max':>5} {'ball px':>8} {'min margin px':>13}")
    for n, (reps, _) in zip(names, done):
        tl = s["cameras"][n]["timeline"] or [(0.0, s["cameras"][n]["camera"])]
        rows = []
        for e in reps:
            rr = (e.provenance.params or {}).get("r_ratio")
            if rr is None:
                continue
            cam = tl[0][1]
            for t, m in tl:
                if t <= e.t:
                    cam = m
            P = np.array([[e.position.x, e.position.y, r]])
            depth = float(cam.depth(P)[0])
            ball = float(cam.K[0, 0]) * r / depth
            dist = float(np.hypot(*(P[0, :2] - cam.position[:2])))
            rows.append((dist, rr, ball, cfg.max_ball_radius_ratio * ball + cfg.ball_radius_slack_px - rr * ball))
        rows = np.array(rows)
        for lo, hi in BANDS:
            b = rows[(rows[:, 0] >= lo) & (rows[:, 0] < hi)] if len(rows) else rows
            if not len(b):
                continue
            print(f"{n:10} {lo:2d}-{hi:<4d} {len(b):4d} {np.median(b[:, 1]):6.2f} {np.percentile(b[:, 1], 99.5):6.2f} "
                  f"{b[:, 1].max():5.2f} {np.median(b[:, 2]):8.1f} {b[:, 3].min():13.1f}")


if __name__ == "__main__":
    main()
