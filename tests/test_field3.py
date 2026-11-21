"""Field test 3 (2026-11-21) changes: serve detection and FAULT calls, plausibility gates, drift
tracking, coverage, calibration readiness, and the faster worker."""

import numpy as np
import pytest

from balltracker.events import BounceEvent, Point3, Provenance
from balltracker.geometry.camera import Camera
from balltracker.geometry.court import CourtSpec
from balltracker.live.fusion import LiveJudge

COURT = CourtSpec.pickleball()
G = 9.81


def bounce(t, x, y, v_in, v_out=(0.0, 0.0, 3.0), cam="c1", std=0.02, vstd=0.2):
    """A bounce with a fused-quality flight measurement (small velocity covariance)."""
    cov = (np.eye(3) * vstd**2).tolist()
    return BounceEvent(t=t, t_std=0.002, position=Point3(x=x, y=y), cov_xy=[[std**2, 0], [0, std**2]],
                       pixel=(0.0, 0.0), camera_ids=[cam], confidence=1.0, supporting_observations=[],
                       provenance=Provenance(algorithm="test", version="0", params={"physics": {
                           "v_in": list(v_in), "v_out": list(v_out), "v_in_cov": cov, "v_out_cov": cov,
                           "rms_in_px": 0.5, "rms_out_px": 0.5}}))


def serve_flight(x0, y0, x1, y1, z0=0.7, h=10.0):
    """Incoming velocity at (x1, y1) of a ball hit at (x0, y0) from height z0 (gravity, no drag)."""
    d = np.array([x1 - x0, y1 - y0])
    tau = np.hypot(*d) / h
    vz = -(z0 - COURT.ball_radius + 0.5 * G * tau * tau) / tau  # z(tau) = r
    v = d / np.hypot(*d) * h
    return (float(v[0]), float(v[1]), float(vz))


def judge(events, **kw):
    j = LiveJudge(COURT, **kw)
    out = []
    for e in events:
        j.add(e, e.t)
        out += j.poll(e.t + 1.0)
    return out + j.flush()


# ------------------------------------------------------------------ serves


def test_a_serve_into_the_diagonal_court_is_recognised_and_in():
    # server behind baseline B on their right (B's right is -x), lands in A's right service court (+x)
    hl = COURT.half_l
    d = judge([bounce(10.0, 1.6, -4.6, serve_flight(-1.8, hl + 0.3, 1.6, -4.6))])[0]
    assert d.diagnostics["play"] == "serve"
    sv = d.diagnostics["serve"]
    assert sv["server_side"] == "B" and sv["service_side"] == "right" and sv["side_from"] == "flight"
    assert d.call.result.value == "IN" and d.call.context.value == "serve"


def test_a_serve_over_the_centre_line_into_the_wrong_court_is_a_fault():
    hl = COURT.half_l
    # from B right (-x), should land at +x; lands at x = -0.4 (wrong side of the centre line)
    d = judge([bounce(10.0, -0.4, -4.6, serve_flight(-1.8, hl + 0.3, -0.4, -4.6))])[0]
    assert d.diagnostics["play"] == "serve"
    assert d.call.result.value == "OUT" and d.call.announce and d.call.call_text == "FAULT"
    assert d.call.nearest_line.startswith("centreline")


def test_a_serve_into_the_kitchen_is_a_fault_even_when_the_servers_half_is_unknown():
    hl = COURT.half_l
    # served from the middle of baseline A: half unknown; lands in B's kitchen
    d = judge([bounce(10.0, 0.5, 1.2, serve_flight(0.05, -hl - 0.3, 0.5, 1.2, z0=0.9, h=7.0))])[0]
    assert d.diagnostics["play"] == "serve" and d.diagnostics["serve"]["service_side"] is None
    assert d.call.target_region == "service_area_B"
    assert d.call.announce and d.call.call_text == "FAULT"


def test_the_pre_serve_bounce_tells_the_servers_half_when_the_flight_does_not():
    hl = COURT.half_l
    drop = bounce(5.0, -1.9, -hl - 0.4, (0.1, 0.1, -3.5), (0.0, 0.0, 3.0))  # bounced by hand behind A, left half
    srv = bounce(9.0, 1.2, 4.8, serve_flight(0.1, -hl - 0.3, 1.2, 4.8), cam="c1")
    srv.provenance.params["physics"]["v_in_cov"] = np.diag([4.0, 0.04, 0.04]).tolist()  # x poorly measured
    d = judge([drop, srv])
    assert d[0].diagnostics["play"] == "dead ball"
    assert d[1].diagnostics["play"] == "serve"
    assert d[1].diagnostics["serve"]["side_from"] == "pre-serve bounce"
    assert d[1].diagnostics["serve"]["service_side"] == "left"   # A's left is -x
    # A left serves to B's left court (+x for a receiver facing -y): x = 1.2 is in
    assert d[1].call.result.value == "IN"


def test_a_rally_drive_is_not_taken_for_a_serve():
    hl = COURT.half_l
    # a 6 m/s shot from the kitchen line (like the "start of play" OUT at 2405 s in field test 3):
    # traced back to baseline A it would be metres underground. (A flat 12 m/s drive from mid-court
    # traces back to a plausible height: only "between points" keeps rally drives from being serves.)
    d = judge([bounce(10.0, 0.5, 5.5, serve_flight(0.4, -2.0, 0.5, 5.5, z0=0.8, h=6.0))])[0]
    assert d.diagnostics["play"] != "serve"
    # and a drive down the line from outside the sideline extension isn't a serve either
    d = judge([bounce(10.0, -3.0, 4.8, serve_flight(-4.6, -hl - 0.2, -3.0, 4.8))])[0]
    assert d.diagnostics["play"] != "serve"


def test_during_a_rally_a_bounce_is_not_a_serve():
    hl = COURT.half_l
    srv = bounce(10.0, 1.6, -4.6, serve_flight(-1.8, hl + 0.3, 1.6, -4.6))
    ret = bounce(11.6, 0.8, 5.0, serve_flight(1.5, -hl + 0.5, 0.8, 5.0))  # return, 1.6 s later
    d = judge([srv, ret])
    assert [x.diagnostics["play"] for x in d] == ["serve", "rally"]


# ------------------------------------------------------------------ gates


def test_an_impossibly_fast_ball_is_not_announced():
    b = bounce(10.0, 3.8, 2.0, (40.0, 5.0, -6.0))  # 40 m/s measured to +-0.2: not a pickleball
    d = judge([b])[0]
    assert not d.call.announce and "implausible speed" in d.diagnostics["gate"]
    # a fast but uncertain single-camera speed is not by itself impossible
    b2 = bounce(20.0, 3.8, 2.0, (30.0, 5.0, -6.0), vstd=6.0)
    d2 = judge([b2])[0]
    assert "implausible" not in str(d2.diagnostics.get("gate"))


def test_start_of_play_far_outside_the_court_is_ball_handling():
    b = bounce(10.0, 4.6, -5.6, (6.0, 2.0, -5.0))  # 1.5 m outside the right sideline, nothing before it
    d = judge([b])[0]
    assert d.diagnostics["play"] == "start of play"
    assert not d.call.announce and "far outside" in d.diagnostics["gate"]


def test_one_far_camera_looking_across_the_line_does_not_call_it_alone():
    cam_pos = np.array([-4.6, -9.5])  # behind the A-left corner, like the iPhone in field test 3

    def view(name, x, y):
        d = np.array([x, y]) - cam_pos
        return float(np.hypot(*d)), d / np.hypot(*d)

    hl = COURT.half_l
    rally = [bounce(10.0, 0.5, 4.0, serve_flight(0.4, -hl + 1, 0.5, 4.0)),
             bounce(11.5, 3.6, -4.0, serve_flight(1.0, hl - 1, 3.6, -4.0))]  # 55 cm out over the right sideline
    d = judge(rally, view=view)
    assert not d[1].call.announce and d[1].call.signed_distance_m > 0.3
    assert "looking across" in d[1].diagnostics["gate"]
    # close to the camera, along the line: allowed
    rally2 = [bounce(10.0, 0.5, 4.0, serve_flight(0.4, -hl + 1, 0.5, 4.0)),
              bounce(11.5, 0.5, -7.2, serve_flight(0.5, hl - 1, 0.5, -7.2))]
    d2 = judge(rally2, view=view)
    assert d2[1].call.announce


# ------------------------------------------------------------------ drift


def _scene(shift=(0.0, 0.0), w=960, h=540, seed=3):
    """A textured background (fence, wall) with court lines; shifted as a camera that turned."""
    import cv2

    rng = np.random.default_rng(seed)
    big = np.zeros((h + 200, w + 200, 3), np.uint8)
    for _ in range(900):
        c = tuple(int(v) for v in rng.integers(30, 255, 3))
        p = tuple(int(v) for v in rng.integers(0, [w + 200, h + 200]))
        cv2.circle(big, p, int(rng.integers(3, 14)), c, -1)
    for k in range(0, w + 200, 120):
        cv2.line(big, (k, 0), (k + 80, h + 200), (255, 255, 255), 3)
    M = np.float32([[1, 0, -100 + shift[0]], [0, 1, -100 + shift[1]]])
    return cv2.warpAffine(big, M, (w, h))


def test_drift_tracker_follows_a_small_turn_and_waits_for_confirmation():
    from balltracker.geometry.drift import DriftConfig, DriftTracker

    cam = Camera.look_at(position=[-4.6, -9.5, 2.4], target=[0.5, 0.0, 0.0], image_size=(960, 540), hfov_deg=70)
    pts = {k: list(map(float, cam.project(np.array([v]))[0])) for k, v in COURT.keypoints().items()
           if 0 <= cam.project(np.array([v]))[0][0] < 960 and 0 <= cam.project(np.array([v]))[0][1] < 540}
    tr = DriftTracker(_scene(), pts, DriftConfig(work_width=960, min_inliers=40))
    assert tr.check(_scene(), COURT, cam, snap=False)["status"] == "steady"
    first = tr.check(_scene((7.0, -3.0)), COURT, cam, snap=False)
    assert first["status"] == "pending"   # one check alone could be a player filling the view
    res = tr.check(_scene((7.0, -3.0)), COURT, cam, snap=False)
    assert res["status"] == "moved" and 6.0 < res["moved_px"] < 9.0
    k = next(iter(pts))
    assert np.allclose(res["points"][k], [pts[k][0] + 7.0, pts[k][1] - 3.0], atol=0.6)
    # the same position again: steady (compared with the original frame, nothing accumulates)
    assert tr.check(_scene((7.0, -3.0)), COURT, res["camera"], snap=False)["status"] == "steady"
    assert tr.check(_scene((150.0, 0.0)), COURT, res["camera"], snap=False)["status"] in ("big", "lost")


# ------------------------------------------------------------------ coverage, readiness


def test_coverage_finds_a_sideline_seen_outside_by_one_camera_only():
    from balltracker.live.upkeep import coverage

    a = Camera.look_at(position=[-4.6, -9.5, 2.4], target=[0.0, 0.0, 0.0], image_size=(1920, 1080), hfov_deg=69)
    b = Camera.look_at(position=[-4.6, 9.5, 2.4], target=[0.0, 0.0, 0.0], image_size=(1920, 1080), hfov_deg=69)
    cov = coverage({"a": a, "b": b}, COURT)
    assert cov["lines"]["sideline_left"]["out2"] > cov["lines"]["sideline_right"]["out2"]
    assert any("sideline right" in w for w in cov["warnings"])
    g = cov["grid"]
    assert g["nx"] * g["ny"] == sum(len(r) for r in g["counts"]) and max(max(r) for r in g["counts"]) == 2
    import json
    json.dumps(cov)  # goes to the dashboard as JSON (numpy ints broke it)


def test_a_rough_calibration_is_not_ready():
    from balltracker.live.upkeep import calibration_ready

    cam = Camera.look_at(position=[0, -9, 2.5], target=[0, 0, 0], image_size=(1280, 720), hfov_deg=70)
    cam.reprojection_rms_px = 6.9
    assert not calibration_ready(cam)
    cam.reprojection_rms_px = 1.2
    assert calibration_ready(cam) and not calibration_ready(None)


# ------------------------------------------------------------------ worker speed-ups


def test_batched_bounce_search_matches_the_one_by_one_search():
    from balltracker.bounce import BounceConfig, BounceDetector, _best_joint_many, _pad_splits, _screen_splits
    from balltracker.tracking import Track, TrackPoint

    cam = Camera.look_at(position=[0, -9, 2.5], target=[0, 0, 0], image_size=(1280, 720), hfov_deg=70)
    bd = BounceDetector(cam, COURT, BounceConfig(bootstrap=10))
    rng = np.random.default_rng(1)
    t = np.arange(0, 0.5, 1 / 120)
    # a ball falling then rising in the image, with noise
    v = np.where(t < 0.25, 300 + 900 * t + 1500 * t * t, 300 + 900 * 0.25 + 1500 * 0.0625 - 700 * (t - 0.25))
    u = 400 + 300 * t
    tr = Track(1, [TrackPoint(i, float(ti), float(ui + rng.normal(0, 0.3)), float(vi + rng.normal(0, 0.3)), 3.0, 1.0)
                   for i, (ti, ui, vi) in enumerate(zip(t, u, v))])
    tt = np.array([p.t for p in tr.points]); uv = np.array([[p.u, p.v] for p in tr.points])
    splits = [(s, max(0, s - 7), min(len(tt), s + 9)) for s in range(5, len(tt) - 6)]
    ref = bd._splits_one_by_one(tt, uv, splits)
    T, UV, M, gaps = _pad_splits(tt, uv, splits)
    passed, sse1 = _screen_splits(T, UV, M, gaps, bd.cfg.sigma0_px, bd.cfg.gain_threshold / 3)
    idx = np.flatnonzero(passed)
    tbs, sse2, _ = _best_joint_many(T[idx], UV[idx], M[idx], gaps[idx])
    assert [r[0] for r in ref] == [splits[i] for i in idx]
    assert np.allclose([r[2] for r in ref], tbs, atol=1e-9) and np.allclose([r[3] for r in ref], sse2, rtol=1e-6)
    assert len(bd.candidates(tr)[0]) >= 1


def test_tracker_prediction_matches_polyfit():
    from balltracker.tracking import Track, TrackPoint

    pts = [TrackPoint(i, i / 120, 100 + 3 * i + 0.1 * i * i, 50 - 2 * i, 3.0, 1.0) for i in range(8)]
    tr = Track(1, pts)
    ts = np.array([p.t for p in pts[-6:]]) - pts[-1].t
    uv = np.array([[p.u, p.v] for p in pts[-6:]])
    c = np.polyfit(ts, uv, 2)
    dt = 1 / 120
    assert np.allclose(tr.predict(pts[-1].t + dt), [np.polyval(c[:, 0], dt), np.polyval(c[:, 1], dt)], atol=1e-6)


def test_a_worker_that_is_behind_defers_bounce_checks_until_tracks_end():
    from balltracker.detection import Candidate
    from balltracker.live.worker import LiveCameraPipeline

    cam = Camera.look_at(position=[0, -9, 2.5], target=[0, 0, 0], image_size=(1280, 720), hfov_deg=70)
    pipe = LiveCameraPipeline("c", COURT, cam)
    pipe.defer_checks = True
    for i in range(40):
        pipe.process_candidates(i, i / 120, [Candidate(u=400 + 3 * i, v=300 + i, radius_px=3, score=1, area_px=28, elongation=1)],
                                (1280, 720))
    d = pipe.pop_diagnostics()
    assert d["checks"] == 0 and d["deferred_frames"] > 0


# --- a weak camera's silence (entry 26) ----------------------------------------------------------

def _plain(t, x, y, cams):
    return BounceEvent(t=t, t_std=0.002, position=Point3(x=x, y=y), cov_xy=[[0.02**2, 0], [0, 0.02**2]],
                       pixel=(0.0, 0.0), camera_ids=list(cams), confidence=1.0, supporting_observations=[],
                       provenance=Provenance(algorithm="test", version="0"))


def _judge_with_weak_camera():
    from balltracker.live.playstate import PlayConfig

    hl = COURT.half_l
    # c2 does not see beyond baseline B; "weak" sees everything but rarely reports
    j = LiveJudge(COURT, hold_s=0.3, play=PlayConfig(enabled=False),
                  can_see=lambda cam, x, y: cam != "c2" or y < hl)
    j.poll(0.0, expected_cameras={"c1", "c2", "weak"})
    return j


def _feed(j, ev):
    for cam in ev.camera_ids:
        j.add(ev.model_copy(update={"camera_ids": [cam]}), now=ev.t + 0.05)
    return j.poll(ev.t + 1.0, expected_cameras={"c1", "c2", "weak"})


def test_weak_cameras_silence_no_longer_vetoes_once_its_hit_rate_is_known():
    hl = COURT.half_l
    out = lambda t: _plain(t, 0.5, hl + 0.4, ["c1"])  # noqa: E731 - OUT seen by c1 only; c2 can't see it
    # Before anything is known, the silent camera counts as reliable: the old veto.
    d = _feed(_judge_with_weak_camera(), out(1.0))[0]
    assert not d.call.announce and d.diagnostics["unconfirmed_by"] == ["weak"]
    # 20 bounces both good cameras saw, the weak one none: its hit rate drops to ~15%.
    j = _judge_with_weak_camera()
    for k in range(20):
        _feed(j, _plain(1.0 + 3 * k, 0.0, 2.0 if k % 2 else -2.0, ["c1", "c2"]))
    assert j.recall.rate("weak", None) < j.weak_rate <= j.recall.rate("c2", None)
    d = _feed(j, out(100.0))[0]
    assert d.call.call_text == "OUT" and "weak" in d.diagnostics["silent_weak"]
    # A good camera's silence still vetoes a lone camera's OUT.
    d = _feed(j, _plain(110.0, 0.5, -hl - 0.4, ["c1"]))[0]
    assert not d.call.announce and d.diagnostics["unconfirmed_by"] == ["c2"]


def test_lone_camera_with_unmeasured_flight_is_not_announced():
    j = LiveJudge(COURT)
    b1 = _plain(1.0, 0.5, COURT.half_l + 0.3, ["c1"])
    b2 = b1.model_copy(update={"camera_ids": ["c1", "c2"]})
    call = j.caller.call(b1, None)
    assert call.announce
    assert j._gate(b1, call, {"play": "rally", "h_in_lo_mps": 5.0, "h_in_mps": 7.0}) is None
    unmeasured = {"play": "rally", "h_in_lo_mps": -67.0, "h_in_mps": 60.0}  # field 3, 2026-11-21 at 2610.9 s
    assert "flight not measured" in j._gate(b1, call, unmeasured)
    assert j._gate(b2, call, unmeasured) is None
