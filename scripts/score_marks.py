#!/usr/bin/env python3
"""Score a session against chalk-marked contacts: how far is each camera from where the ball hit?

Review of defed68, TODO-12: the far-half bias must be measured on court before calibration code
changes. Drill: mark spots with chalk (or tape) where balls will land, measure each mark's court
position (tape measure from the nearest corner: x across, y along, metres; the court centre is
0, 0 and side A is negative y), and drop or hit balls onto them during the session.

    .venv/bin/python scripts/score_marks.py data/live/sessions/<id> marks.json [--radius 0.5]

marks.json: [{"name": "far-left corner", "x": -3.0, "y": 6.6}, ...]

For each mark, every bounce report within --radius metres is attributed to it (per camera and
fused decisions). Printed per camera: n, mean error along x and y (bias), spread, and the error
in pixels at that camera (from its calibration), which separates a calibration problem (bias
that grows with distance) from detection noise. Uses the reports logged live (events.jsonl).
Unlike `bt report --marks` (one chalk mark measured after each bounce, fused calls matched in
order), this measures each camera separately around fixed target spots.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from balltracker.live.replay import load_session  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("marks")
    ap.add_argument("--radius", type=float, default=0.5)
    a = ap.parse_args()
    s = load_session(a.session)
    marks = json.loads(Path(a.marks).read_text())
    reports = [e for e in s["events"] if e.get("type") == "report" and not e.get("excluded")]
    decisions = [e for e in s["events"] if e.get("type") == "decision" and not e.get("suppressed")]
    models = {n: (c["timeline"][-1][1] if c.get("timeline") else c["camera"]) for n, c in s["cameras"].items()}
    for m in marks:
        mx, my = float(m["x"]), float(m["y"])
        print(f"\n{m.get('name', '')} ({mx:+.2f}, {my:+.2f})")
        rows = [("fused", [(d["x"], d["y"]) for d in decisions if np.hypot(d["x"] - mx, d["y"] - my) <= a.radius])]
        for cam in sorted({r["camera"] for r in reports}):
            rows.append((cam, [(r["x"], r["y"]) for r in reports if r["camera"] == cam
                               and np.hypot(r["x"] - mx, r["y"] - my) <= a.radius]))
        for name, pts in rows:
            if not pts:
                print(f"  {name:14s} no bounces within {a.radius} m")
                continue
            e = np.array(pts) - [mx, my]
            line = (f"  {name:14s} n={len(e):3d}  bias x {100 * e[:, 0].mean():+6.1f} cm, y {100 * e[:, 1].mean():+6.1f} cm"
                    f"  spread {100 * e[:, 0].std():5.1f} / {100 * e[:, 1].std():5.1f} cm")
            cam = models.get(name)
            if cam is not None:
                r = s["court"].ball_radius
                p_true = cam.project(np.array([[mx, my, r]]))[0]
                p_meas = cam.project(np.array([[mx + e[:, 0].mean(), my + e[:, 1].mean(), r]]))[0]
                dist = float(np.hypot(*(np.array([mx, my]) - cam.position[:2])))
                line += f"  = {np.hypot(*(p_meas - p_true)):.1f} px at {dist:.0f} m"
            print(line)


if __name__ == "__main__":
    main()
