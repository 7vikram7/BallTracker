"""Judge fixes from the outside review of defed68 (decision log entry 27). Each test failed before
its fix."""

import math

import numpy as np

from balltracker.events import BounceEvent, Point3, Provenance
from balltracker.geometry.camera import Camera
from balltracker.geometry.court import CourtSpec, ServiceSide, Side
from balltracker.live.fusion import LiveJudge, fuse
from balltracker.live.playstate import PlayConfig
from balltracker.sports.pickleball.line_calling import PickleballLineCaller, ServeContext

COURT = CourtSpec.pickleball()
HL, HW, K = COURT.half_l, COURT.half_w, COURT.kitchen_depth


def ev(t, x, y, sd=0.02, cam="c1", sdx=None, sdy=None):
    sx, sy = sdx or sd, sdy or sd
    return BounceEvent(t=t, t_std=0.002, position=Point3(x=x, y=y), cov_xy=[[sx**2, 0], [0, sy**2]],
                       pixel=(0.0, 0.0), camera_ids=[cam], confidence=1.0, supporting_observations=[],
                       provenance=Provenance(algorithm="test", version="0"))


def judge(**kw):
    kw.setdefault("play", PlayConfig(enabled=False))
    return LiveJudge(COURT, hold_s=0.3, **kw)


def run(j, events, expected=None):
    """Feed (event, arrival time) pairs; poll after each; flush at the end."""
    out = []
    for e, arrival in events:
        out += j.poll(arrival, expected)
        j.add(e, arrival)
    out += j.poll(max(a for _, a in events) + 5.0, expected)
    return out


# --- TODO-1: a camera whose own view favours IN blocks a fused OUT --------------------------------

def test_fused_out_is_silent_when_one_camera_itself_favours_in():
    # cam A: 15 cm inside the baseline, sd 30 cm (its own p_out 0.31); cam B: 20 cm out, sd 3 cm.
    # Fused OUT with chi2 1.35 (no inflation), but A's view favours IN 2:1.
    a, b = ev(1.0, 0.5, HL - 0.15, sd=0.30, cam="A"), ev(1.0, 0.5, HL + 0.20, sd=0.03, cam="B")
    _, diag = fuse([a, b])
    assert diag["inflation"] == 1.0
    d = run(judge(), [(a, 1.05), (b, 1.06)])[0]
    assert not d.call.announce and d.diagnostics.get("cameras_disagree")


def test_fused_out_is_spoken_when_the_cameras_agree_or_one_knows_little():
    a, b = ev(1.0, 0.5, HL + 0.18, sd=0.10, cam="A"), ev(1.0, 0.5, HL + 0.20, sd=0.03, cam="B")
    assert run(judge(), [(a, 1.05), (b, 1.06)])[0].call.call_text == "OUT"
    # a camera that can't tell (its estimate on the line, p_out ~0.5) does not block
    a2 = ev(5.0, 0.5, HL + COURT.contact_patch_radius, sd=0.30, cam="A")
    b2 = ev(5.0, 0.5, HL + 0.20, sd=0.03, cam="B")
    assert run(judge(), [(a2, 5.05), (b2, 5.06)])[0].call.call_text == "OUT"


# --- TODO-2: a calibration without an RMS is not ready -------------------------------------------

def test_calibration_without_rms_is_not_ready():
    from balltracker.live.upkeep import calibration_ready

    cam = Camera.look_at(position=[0.0, -HL - 3.0, 4.0], target=[0.0, 0.0, 0.0], image_size=(1280, 720), hfov_deg=70)
    assert cam.reprojection_rms_px is None and not calibration_ready(cam)
    for rms, ok in ((float("nan"), False), (2.9, True), (3.1, False)):
        cam.reprojection_rms_px = rms
        assert calibration_ready(cam) is ok
    cam.reprojection_rms_px = None
    assert calibration_ready(cam, math.inf)  # an explicit "don't gate" (old sample sessions)


# --- TODO-3: an armed serve context is used up by the next bounce, even a suppressed one ---------

def test_serve_context_is_consumed_by_a_suppressed_bounce():
    j = judge()
    first = ev(1.0, 1.0, 2.0)
    d = run(j, [(first, 1.05)])
    j.serve = ServeContext(Side.A, ServiceSide.RIGHT)
    sec = ev(1.6, 1.2, 5.0)  # same half, further out, 0.6 s later: secondary bounce
    kitchen = ev(4.0, 1.0, 1.0)  # a rally ball in B's kitchen: IN
    d = run(j, [(sec, 1.65), (kitchen, 4.05)])
    assert d[0].suppressed == "secondary bounce"
    assert d[1].call.context.value == "rally" and d[1].call.result.value == "IN"


# --- TODO-4: without flight data, a later bounce further out on the same half is a second bounce --

def test_second_bounce_without_flight_data_within_the_play_window_is_suppressed():
    j = LiveJudge(COURT, hold_s=0.3)  # play state on; these reports carry no flight data
    d = run(j, [(ev(1.0, 1.0, 3.0), 1.05), (ev(3.0, 1.2, HL + 0.5), 3.05)])
    assert d[0].call is not None
    assert d[1].suppressed and not (d[1].call and d[1].call.announce)
    # a genuine first bounce 4 s after the previous one is still called
    j2 = LiveJudge(COURT, hold_s=0.3)
    d2 = run(j2, [(ev(1.0, 1.0, 3.0), 1.05), (ev(5.0, 1.2, HL + 0.5), 5.05)])
    assert d2[1].call.call_text == "OUT"


# --- TODO-5: a report arriving after its group was decided is not judged again --------------------

def test_late_report_does_not_make_a_second_decision():
    j = judge()
    a = ev(10.00, 0.5, HL + 0.3, cam="A")
    b = ev(10.02, 0.5, HL + 0.3, cam="B")  # arrives 0.8 s late, after A's group was released
    d = run(j, [(a, 10.05), (b, 10.85)])
    assert len(d) == 1


# --- TODO-6: the veto still applies after flush() (expected cameras are kept) --------------------

def test_veto_applies_after_flush():
    j = judge(can_see=lambda cam, x, y: True)
    j.poll(0.0, expected_cameras={"A", "B"})
    j.add(ev(1.0, 0.5, HL + 0.4, cam="A"), 1.05)
    d = j.flush()[0]
    assert not d.call.announce and d.diagnostics["unconfirmed_by"] == ["B"]


# --- TODO-7: chi-square limit for three cameras -----------------------------------------------------

def test_three_cameras_with_chi2_20_are_inflated():
    s = 0.01
    a = s * math.sqrt(10.0)  # chi2 = 2 a^2 / s^2 = 20, dof 4 (99.9% quantile 18.5)
    _, diag = fuse([ev(1.0, -a, 2.0, sd=s, cam="A"), ev(1.0, a, 2.0, sd=s, cam="B"), ev(1.0, 0.0, 2.0, sd=s, cam="C")])
    assert abs(diag["chi2"] - 20.0) < 0.1 and diag["inflation"] > 1.0


# --- TODO-8 (c): with the server's half unknown, a serve in the kitchen is not called FAULT --------

def test_serve_with_unknown_side_in_the_kitchen_is_uncertain_but_long_is_fault():
    caller = PickleballLineCaller(COURT)
    srv = ServeContext(Side.A, None)
    kitchen = caller.call(ev(1.0, 1.0, 1.0), srv)  # could be a mis-tagged rally ball (a dink): IN
    assert kitchen.result.value == "UNCERTAIN" and not kitchen.announce
    long = caller.call(ev(2.0, 1.0, HL + 0.3), srv)  # out of the whole half: out whatever it was
    assert long.call_text == "FAULT"
    known = caller.call(ev(3.0, 1.0, 1.0), ServeContext(Side.A, ServiceSide.RIGHT))
    assert known.call_text == "FAULT"


def test_a_lob_after_a_long_volley_exchange_is_not_taken_for_a_serve():
    # TODO-8 (b): already true: traced back to the far baseline, the lob is metres below the ground
    from balltracker.live.playstate import PlayState

    ps = PlayState(PlayConfig(), COURT)
    cov = (np.eye(3) * 0.04).tolist()
    b = ev(10.0, 0.5, 6.0).model_copy(update={"provenance": Provenance(algorithm="t", version="0", params={"physics": {
        "v_in": [0.3, 5.0, -10.0], "v_out": [0.2, 4.0, 5.0], "v_in_cov": cov, "v_out_cov": cov,
        "rms_in_px": 0.5, "rms_out_px": 0.5}})})
    r = ps.assess(b, [b], serve=False)  # nothing for > 5 s: between points
    assert r["play"] != "serve" and "serve" not in r


# --- TODO-9: p_out does not depend on what was called before ---------------------------------------

def test_p_out_is_the_same_whatever_was_called_before():
    b = ev(7.0, 0.5, HL + 0.01, sd=0.02)
    c1 = PickleballLineCaller(COURT)
    first = c1.call(b).p_out
    c2 = PickleballLineCaller(COURT)
    for k in range(5):
        c2.call(ev(1.0 + k, 0.3 * k, 2.0, sd=0.3))
    assert c2.call(b).p_out == first


# --- Review of a9fbde6, P1-2: the first bounce has flight data, the second has none -----------------

def _with_flight(e, v_in, v_out):
    return e.model_copy(update={"provenance": Provenance(algorithm="test", version="0", params={"physics": {
        "v_in": list(v_in), "v_out": list(v_out), "rms_in_px": 0.5, "rms_out_px": 0.5}})})


def test_a_bounce_without_flight_data_2_s_after_one_with_it_is_a_second_bounce():
    """The no-flight-data rule required both bounces to lack flight data, so a 2.0 s second bounce
    further out became "start of play (no flight data)" and was announced OUT."""
    first = _with_flight(ev(1.0, 1.0, 3.0), (0, 9, -5), (0, 3, 4))  # lands in, rises at 4 m/s
    j = LiveJudge(COURT, hold_s=0.3)
    d = run(j, [(first, 1.05), (ev(3.0, 1.2, HL + 0.5), 3.05)])
    assert d[0].call is not None and d[0].suppressed is None
    assert d[1].suppressed and not (d[1].call and d[1].call.announce)
    # a genuine first bounce 4 s later is still called
    j2 = LiveJudge(COURT, hold_s=0.3)
    d2 = run(j2, [(first, 1.05), (ev(5.0, 1.2, HL + 0.5), 5.05)])
    assert d2[1].call.call_text == "OUT"


# --- Review of a9fbde6, P2-6: a calibration error moves "can see" only at the edge of the view ------

def test_a_15_cm_calibration_error_changes_can_see_only_near_the_edge_of_the_view():
    """A camera whose model aims 15 cm off at the court centre (about 30 cm off on the far half) is
    judged able to see each spot correctly except in a strip along the edge of its view. There its
    silence may neither wait nor veto (decision log 33)."""
    from balltracker.live.server import camera_can_see

    true = Camera.look_at(np.array([4.6, -9.5, 2.4]), np.array([-0.5, 0.0, 0.0]), (1920, 1080), 70.0)
    model = Camera.look_at(np.array([4.6, -9.5, 2.4]), np.array([-0.35, 0.0, 0.0]), (1920, 1080), 70.0)
    flips, total = 0, 0
    for x in np.arange(-HW - 1, HW + 1.01, 0.1):
        for y in np.arange(-HL - 1, HL + 1.01, 0.1):
            total += 1
            seen = camera_can_see(true, COURT, x, y)
            if seen != camera_can_see(model, COURT, x, y):
                flips += 1
                assert any(camera_can_see(true, COURT, x + dx, y + dy) != seen
                           for dx, dy in ((0.4, 0), (-0.4, 0), (0, 0.4), (0, -0.4)))  # within 0.4 m of the edge
    assert flips / total < 0.01
