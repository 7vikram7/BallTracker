"""Play state: only bounces of a ball in play are announced (field test 2 lesson)."""

import numpy as np

from balltracker.events import BounceEvent, Point3, Provenance
from balltracker.geometry.court import CourtSpec
from balltracker.live.fusion import LiveJudge
from balltracker.live.playstate import PlayState


def bounce(t, x, y, v_in, v_out, cam="c1", std=0.02):
    return BounceEvent(t=t, t_std=0.002, position=Point3(x=x, y=y), cov_xy=[[std**2, 0], [0, std**2]],
                       pixel=(0.0, 0.0), camera_ids=[cam], confidence=1.0, supporting_observations=[],
                       provenance=Provenance(algorithm="test", version="0", params={"physics": {
                           "v_in": list(v_in), "v_out": list(v_out), "rms_in_px": 0.5, "rms_out_px": 0.5}}))


def judge_all(events):
    j = LiveJudge(CourtSpec.pickleball())
    out = []
    for e in events:
        j.add(e, e.t)
        out += j.poll(e.t + 1.0)
    return out + j.flush()


def test_rally_alternating_halves_is_called_and_long_ball_is_announced():
    # serve from A lands in B, return lands in A, then a drive lands long behind B's baseline
    evs = [bounce(1.0, 1.0, 4.0, (0, 9, -5), (0, 7, 3)),
           bounce(2.6, -1.0, -4.5, (0, -8, -5), (0, -6, 3)),
           bounce(4.0, 0.5, 7.4, (0, 10, -4), (0, 8, 3))]
    d = judge_all(evs)
    assert [x.diagnostics["play"] for x in d] == ["start of play", "rally", "rally"]
    assert d[2].call.result.value == "OUT" and d[2].call.announce


def test_second_bounce_of_an_unreturned_ball_is_suppressed_even_after_1_2_s():
    # lands in at y=3 rising at 6 m/s (flight ~1.2 s), comes down again 1.45 s later ~5 m further on
    first = bounce(10.0, 1.4, 3.0, (0, 8, -6), (0.6, 3.6, 7.0))
    second = bounce(11.45, 2.3, 8.2, (0.6, 3.6, -6.5), (0.5, 3.0, 4.0))
    d = judge_all([first, second])
    assert d[0].suppressed is None and d[0].call.result.value == "IN"
    assert d[1].suppressed and "second bounce" in d[1].suppressed


def test_dropped_ball_behind_the_baseline_is_never_announced():
    # pre-serve: ball bounced by hand behind baseline B (outside the court): nearly vertical arrival
    d = judge_all([bounce(20.0, 0.5, 8.1, (0.1, 0.2, -4.0), (0.1, 0.1, 3.0))])
    assert d[0].diagnostics["play"] == "dead ball"
    assert d[0].call.result.value == "UNCERTAIN" and not d[0].call.announce


def test_slow_toss_out_of_the_court_at_start_of_play_is_silent_but_a_shot_is_called():
    toss = bounce(30.0, 3.8, 2.0, (2.5, 1.0, -3.0), (2.0, 0.8, 2.0))   # 2.7 m/s: not clearly a shot
    d = judge_all([toss])
    assert d[0].diagnostics["play"] == "not clearly a shot" and not d[0].call.announce
    shot = bounce(40.0, 3.8, 2.0, (6.0, 4.0, -5.0), (5.0, 3.0, 3.0))   # 7 m/s
    d = judge_all([shot])
    assert d[0].diagnostics["play"] == "start of play" and d[0].call.announce


def test_feeding_drill_to_one_half_still_calls_every_feed():
    # drills (and the synthetic test scenes) feed balls to one half every ~1.5 s from the other side
    evs = [bounce(1.0 + 1.5 * i, x, 3.0 + 0.2 * i, (0.5, 9, -5), (0.4, 7, 3)) for i, x in enumerate([-2.9, 3.0, -1.6])]
    evs.append(bounce(5.6, -1.0, 6.9, (0.2, 10, -5), (0.2, 8, 3)))  # long
    d = judge_all(evs)
    assert all(x.suppressed is None for x in d)
    assert d[-1].call.result.value == "OUT" and d[-1].call.announce


def test_missing_flight_data_keeps_the_old_behaviour():
    ps = PlayState()
    e = BounceEvent(t=1.0, t_std=0.01, position=Point3(x=0, y=7.5), cov_xy=[[1e-4, 0], [0, 1e-4]], pixel=(0, 0),
                    camera_ids=["c"], confidence=1.0, supporting_observations=[],
                    provenance=Provenance(algorithm="t", version="0", params={}))
    r = ps.assess(e, [e], serve=True)
    assert r["play"] == "start of play" and r["announce_ok"]
    r = ps.assess(e.model_copy(update={"t": 50.0}), [e], serve=False)
    assert r["play"] == "start of play (no flight data)" and r["announce_ok"]
