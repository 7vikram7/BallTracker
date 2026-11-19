"""Tracker regressions from real footage (iPhone, camera low and close)."""

import numpy as np

from balltracker.detection import Candidate
from balltracker.tracking import BallTracker


def _c(u, v, r):
    return Candidate(u=u, v=v, radius_px=r, score=1.0, area_px=np.pi * r * r, elongation=1.0)


def test_big_fast_ball_with_vertical_bounce_and_clutter_is_one_track():
    # Ball (r ~ 40 px) falls ~50 px/frame, bounces (vertical image velocity
    # reverses), then rises; small clutter blobs appear next to the bounce.
    fps = 120.0
    rng = np.random.default_rng(0)
    pts = []
    u, v, du, dv = 1000.0, 900.0, -35.0, 50.0
    for k in range(30):
        if k == 6:
            dv = -0.6 * dv  # bounce
        pts.append((u + rng.normal(0, 4), v + rng.normal(0, 4)))
        u, v, dv = u + du, v + dv, dv + 1.5
    tr = BallTracker()
    for k, (pu, pv) in enumerate(pts):
        cands = [_c(pu, pv, 40 + rng.normal(0, 4))]
        if 4 <= k <= 9:  # clutter right where the bounce happens
            cands.append(_c(pu - 20 + rng.normal(0, 5), pv + 30 + rng.normal(0, 5), 4))
        tr.update(k, k / fps, cands)
    tracks = [t for t in tr.finish() if np.median([p.radius_px for p in t.points]) > 20]
    assert len(tracks) == 1
    assert len(tracks[0].points) == 30


def test_dedupe_bounces_across_tracks():
    from types import SimpleNamespace as N

    from balltracker.pipeline import dedupe_bounces

    bs = [N(t=16.335, confidence=0.64), N(t=16.346, confidence=0.83), N(t=20.6, confidence=1.0)]
    out = dedupe_bounces(bs, 0.12)
    assert [b.t for b in out] == [16.346, 20.6]
