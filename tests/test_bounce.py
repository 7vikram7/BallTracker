"""Bounce detection on analytically projected trajectories (no rendering)."""

import numpy as np
import pytest

from balltracker.bounce import BounceDetector
from balltracker.geometry.camera import Camera
from balltracker.geometry.court import CourtSpec
from balltracker.synthetic import BallPhysics, Shot, aim_shot, simulate
from balltracker.tracking import Track, TrackPoint


def make_track(cam, ts, pos, fps, t0, noise_px, rng):
    tr = Track(0)
    n = int((ts[-1] - ts[0]) * fps)
    for i in range(n):
        t = t0 + i / fps
        if t < ts[0] or t > ts[-1]:
            continue
        P = np.array([np.interp(t, ts, pos[:, k]) for k in range(3)])
        u, v = cam.project(P[None])[0] + rng.normal(0, noise_px, 2)
        tr.points.append(TrackPoint(i, t, u, v, 5.0, 1.0))
    return tr


@pytest.mark.parametrize("fps,tol_cm", [(240, 3.0), (120, 5.0), (60, 12.0)])
def test_subframe_bounce_accuracy(fps, tol_cm):
    court = CourtSpec()
    cam = Camera.look_at(np.array([0.0, 11.7, 4.0]), np.array([0.0, 4.0, 0.0]), (1920, 1080), 65.0)
    cam.reprojection_rms_px = 0.5
    rng = np.random.default_rng(3)
    phys = BallPhysics()
    errs = []
    for k in range(8):
        start = np.array([rng.uniform(-2, 2), -5.0, 0.8])
        target = np.array([rng.uniform(-2.8, 2.8), rng.uniform(3, 6.6)])
        v = aim_shot(start, target, 0.9, court.ball_radius, phys)
        ts, pos, bs = simulate(Shot(start, v, 0.0, 1.2), court.ball_radius, phys)
        # Random phase so the bounce falls between frames.
        tr = make_track(cam, ts, pos, fps, rng.uniform(0, 1 / fps), 0.4, rng)
        found = BounceDetector(cam, court).detect(tr)
        tb, xb, yb = bs[0]
        m = [f for f in found if abs(f.t - tb) < 0.03]
        assert m, f"bounce {k} not found at {fps} fps"
        errs.append(100 * np.hypot(m[0].position.x - xb, m[0].position.y - yb))
    assert np.median(errs) < tol_cm, errs


def test_no_bounce_on_smooth_flight():
    court = CourtSpec()
    cam = Camera.look_at(np.array([0.0, 11.7, 4.0]), np.array([0.0, 4.0, 0.0]), (1920, 1080), 65.0)
    rng = np.random.default_rng(1)
    start = np.array([0.0, -2.0, 1.0])
    v = np.array([0.5, 9.0, 3.0])
    ts, pos, bs = simulate(Shot(start, v, 0.0, 0.6), court.ball_radius, BallPhysics())
    assert not bs
    tr = make_track(cam, ts, pos, 240, 0.0, 0.4, rng)
    assert BounceDetector(cam, court).detect(tr) == []


def _ballistic(p0, v0, ts):
    g = np.array([0, 0, -9.81])
    return np.array([p0 + v0 * t + 0.5 * g * t * t for t in ts])


@pytest.mark.parametrize("physics", [True, False])
def test_mid_air_paddle_hit_is_not_a_bounce(physics):
    """A volley at 1 m height reverses the ball: a kink in the image, but not a
    ground contact. The ballistic check must reject it."""
    from balltracker.bounce import BounceConfig

    court = CourtSpec()
    cam = Camera.look_at(np.array([0.0, 11.7, 4.0]), np.array([0.0, 4.0, 0.0]), (1920, 1080), 65.0)
    cam.reprojection_rms_px = 0.5
    rng = np.random.default_rng(5)
    fps, th = 120, 0.35
    t1 = np.arange(0, th, 1 / fps)
    seg1 = _ballistic(np.array([0.5, 0.5, 1.2]), np.array([0.2, 8.0, 1.2]), t1)
    hit = _ballistic(np.array([0.5, 0.5, 1.2]), np.array([0.2, 8.0, 1.2]), np.array([th]))[0]
    t2 = np.arange(th, th + 0.35, 1 / fps)
    seg2 = _ballistic(hit, np.array([-0.3, -9.0, 3.0]), t2 - th)
    tr = Track(0)
    for i, (t, P) in enumerate(zip(np.r_[t1, t2], np.vstack([seg1, seg2]))):
        u, v = cam.project(P[None])[0] + rng.normal(0, 0.4, 2)
        tr.points.append(TrackPoint(i, t, u, v, 5.0, 1.0))
    found = BounceDetector(cam, court, BounceConfig(physics_check=physics)).detect(tr)
    near = [f for f in found if abs(f.t - th) < 0.05]
    if physics:
        assert near == []
