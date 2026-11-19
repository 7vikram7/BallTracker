import numpy as np

from balltracker.events import BounceEvent, CallResult, Point3, Provenance, ShotContext
from balltracker.geometry.court import CourtSpec, ServiceSide, Side
from balltracker.sports.pickleball.line_calling import PickleballLineCaller, ServeContext

PROV = Provenance(algorithm="test", version="0")


def bounce(x, y, sigma=0.01, t=1.0, conf=1.0):
    return BounceEvent(t=t, t_std=0.001, position=Point3(x=x, y=y), cov_xy=[[sigma**2, 0], [0, sigma**2]],
                       pixel=(0, 0), camera_ids=["c"], confidence=conf, supporting_observations=[], provenance=PROV)


def test_clear_in_and_out():
    c = CourtSpec()
    lc = PickleballLineCaller(c)
    assert lc.call(bounce(0, c.half_l - 0.5)).result is CallResult.IN
    out = lc.call(bounce(0, c.half_l + 0.3))
    assert out.result is CallResult.OUT and out.announce and out.call_text == "OUT"


def test_ball_touching_line_is_in():
    c = CourtSpec()
    lc = PickleballLineCaller(c)
    # Contact centre 5 mm outside the outer edge, contact patch radius 10 mm -> touches line.
    assert lc.call(bounce(0, c.half_l + 0.005, sigma=0.001)).result is CallResult.IN


def test_close_call_with_large_uncertainty_stays_silent():
    c = CourtSpec()
    lc = PickleballLineCaller(c)
    call = lc.call(bounce(0, c.half_l + 0.03, sigma=0.04))
    assert call.result is CallResult.UNCERTAIN and not call.announce


def test_serve_on_kitchen_line_is_fault():
    c = CourtSpec()
    lc = PickleballLineCaller(c)
    serve = ServeContext(Side.A, ServiceSide.RIGHT)
    # Centre of B's kitchen line, in the correct (diagonal) half.
    call = lc.call(bounce(-1.5, c.kitchen_depth - c.line_width / 2 - 0.02, sigma=0.003), serve)
    assert call.context is ShotContext.SERVE
    assert call.result is CallResult.OUT and call.call_text == "FAULT"


def test_serve_to_wrong_court_is_fault_and_correct_is_in():
    c = CourtSpec()
    lc = PickleballLineCaller(c)
    serve = ServeContext(Side.A, ServiceSide.RIGHT)
    assert lc.call(bounce(+1.5, 5.0), serve).result is CallResult.OUT  # same-side (not diagonal)
    assert lc.call(bounce(-1.5, 5.0), serve).result is CallResult.IN


def test_low_confidence_bounce_never_announces():
    c = CourtSpec()
    lc = PickleballLineCaller(c)
    assert lc.call(bounce(0, c.half_l + 0.5, conf=0.1)).result is CallResult.UNCERTAIN


def test_secondary_bounce_suppressed():
    c = CourtSpec()
    lc = PickleballLineCaller(c)
    b1, b2 = bounce(0, 5.0, t=1.0), bounce(0, 7.5, t=1.6)
    assert [b.t for b in lc.suppress_secondary([b1, b2])] == [1.0]
