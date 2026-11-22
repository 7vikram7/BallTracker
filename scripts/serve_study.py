#!/usr/bin/env python3
"""Why each serve candidate of a recorded session was or wasn't recognised as a serve (decision
log 32): replays the session, records the reason at every check of PlayState.serve_of, and prints
the counts by reason and landing region.

    .venv/bin/python scripts/serve_study.py data/field/20261122-071401 [--out serves.json]

The checks below mirror PlayState.serve_of (playstate.py) step by step, to record which one
rejected a candidate; a candidate that passes them all is judged by the real serve_of.
"""

from __future__ import annotations

import argparse
import collections
import json
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from balltracker.live import playstate as P  # noqa: E402
from balltracker.live import replay as R  # noqa: E402

G = P.G
rec: list[dict] = []
def serve_of(self, b, fl):
    cfg, court = self.cfg, self.court
    r = {'t': b.t, 'x': b.position.x, 'y': b.position.y}
    rec.append(r)
    if not fl or 'v_in_cov' not in fl:
        r['why'] = 'no flight measured'; return None
    x, y = b.position.x, b.position.y
    if abs(y) < 0.05 * court.half_l: r['why'] = 'on net line'; return None
    vx, vy, vz = (float(v) for v in fl['v_in']); r['v'] = [vx, vy, vz]; C = np.asarray(fl['v_in_cov'], float); sy = float(np.sqrt(max(C[1,1],0)))
    r.update(vy=vy, sy=sy)
    if np.sign(vy) != np.sign(y): r['why'] = 'not moving away from the net'; return None
    if abs(vy) < cfg.serve_min_vy_mps: r['why'] = 'too slow along court'; return None
    if abs(vy) < cfg.serve_vy_sigmas * sy: r['why'] = 'speed too uncertain (vy < 3 sd)'; return None
    y_base = -float(np.sign(y)) * court.half_l; tau = abs(y - y_base) / abs(vy)
    z0 = court.ball_radius - vz * tau - 0.5 * G * tau * tau; r['z0'] = z0
    r['xo'] = x - vx * (y - y_base) / vy
    if not cfg.serve_z_range[0] <= z0 <= cfg.serve_z_range[1]: r['why'] = 'traced height at baseline implausible'; return None
    k = (y - y_base) / vy; xo = x - vx * k
    J = np.array([-k, vx * (y - y_base) / vy**2]); sxo = float(np.sqrt(max(J @ C[:2,:2] @ J, 0)))
    r.update(xo=xo, sxo=sxo)
    if abs(xo) - 2 * sxo > court.half_w + cfg.serve_outside_m: r['why'] = 'origin outside sideline extensions'; return None
    out = ORIG(self, b, fl)
    if out is None: r['why'] = 'lands >1 m into server\'s own side (straight ahead)'
    else: r['why'] = 'SERVE'; r['sv'] = out
    return out
ORIG = P.PlayState.serve_of
P.PlayState.serve_of = serve_of


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("session")
    ap.add_argument("--out", help="write every candidate with its reason (JSON)")
    ap.add_argument("--reports", help="cached camera reports (pickle {camera: (reports, extra)}) instead of replaying")
    a = ap.parse_args()
    s = R.load_session(a.session)
    st = (s["manifest"] or {}).get("settings") or {}
    if a.reports:
        cache = pickle.load(open(a.reports, "rb"))
    else:
        names = list(s["cameras"])
        with ProcessPoolExecutor(4) as ex:
            cache = dict(zip(names, ex.map(R._camera_reports_job, [(a.session, None, n, st.get("detector_overrides") or {}, None)
                                                                   for n in names])))
    reports = {}
    for n, (r, extra) in cache.items():
        reports[n] = r
        s["cameras"][n].update(extra)
    D = R.judge_reports(s["court"], s["cameras"], reports, s["contexts"], st.get("hold_s", 0.6), s["modes"], None,
                        st.get("weak_rate", 0.4))
    byt = {round(d["t"], 3): d for d in D}
    hw, hl, kd = s["court"].half_w, s["court"].half_l, s["court"].kitchen_depth

    def region(x, y):
        if abs(x) > hw or abs(y) > hl:
            return "out of court"
        return "kitchen" if abs(y) < kd else "service courts"

    print("serve candidates (between points, >= 3 s after play):", len(rec))
    c = collections.Counter((r["why"], region(r["x"], r["y"])) for r in rec)
    for k, v in sorted(c.items(), key=lambda a: -a[1]):
        print(f"  {v:3d}  {k[0]:50s} landed {k[1]}")
    S = [r for r in rec if r["why"] == "SERVE"]
    print("recognised serves:", len(S), "| calls on them:",
          dict(collections.Counter(byt.get(round(r["t"], 3), {}).get("result") for r in S)))
    z = [r["z0"] for r in S if "z0" in r]
    if z:
        print(f"traced height at the server's baseline, recognised serves: median {np.median(z):+.2f} m")
    if a.out:
        for r in rec:
            d = byt.get(round(r["t"], 3), {})
            r.update(call=d.get("result"), spoken=d.get("announce"), ncam=len(d.get("cameras") or []), play=d.get("play"))
        Path(a.out).write_text(json.dumps(rec, default=float))


if __name__ == "__main__":
    main()
