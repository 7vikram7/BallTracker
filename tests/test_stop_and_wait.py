"""Field 2026-11-22: Stop session on the dashboard, and the judge's wait for slow cameras."""

from __future__ import annotations

import asyncio

from aiohttp.test_utils import TestClient, TestServer

from balltracker.events import BounceEvent, Point3, Provenance
from balltracker.live.fusion import LiveJudge
from balltracker.live.playstate import PlayConfig
from balltracker.geometry.court import CourtSpec

COURT = CourtSpec.pickleball()
CAMS = {"c1", "c2", "weak"}


def _ev(t, x, y, cam):
    return BounceEvent(t=t, t_std=0.002, position=Point3(x=x, y=y), cov_xy=[[0.02**2, 0], [0, 0.02**2]],
                       pixel=(0.0, 0.0), camera_ids=[cam], confidence=1.0, supporting_observations=[],
                       provenance=Provenance(algorithm="test", version="0"))


def _judge(can_see=None):
    j = LiveJudge(COURT, hold_s=0.6, play=PlayConfig(enabled=False), can_see=can_see or (lambda cam, x, y: True))
    j.poll(0.0, expected_cameras=CAMS)
    return j


def _teach_weak(j, n=20):
    """n bounces c1 and c2 both reported and "weak" never did: its hit rate drops below weak_rate."""
    for k in range(n):
        t = 1.0 + 3 * k
        for cam in ("c1", "c2"):
            j.add(_ev(t, 0.0, 2.0 if k % 2 else -2.0, cam), now=t + 0.5)
        j.poll(t + 2.0, CAMS)
    assert j.recall.rate("weak", None) < j.weak_rate <= j.recall.rate("c2", None)


def test_two_camera_bounce_is_not_held_for_a_camera_that_never_catches_bounces():
    j = _judge()
    _teach_weak(j)
    t = 100.0
    j.add(_ev(t, 0.5, 3.0, "c1"), now=t + 0.65)
    j.add(_ev(t, 0.5, 3.0, "c2"), now=t + 0.77)
    assert j.poll(t + 0.80, CAMS) == []  # the weak camera still gets weak_wait_s ...
    assert len(j.poll(t + 0.65 + j.weak_wait_s, CAMS)) == 1  # ... then the call goes out, not at hold_s


def test_a_reliable_silent_camera_is_still_waited_for():
    j = _judge()
    t = 10.0
    j.add(_ev(t, 0.5, 3.0, "c1"), now=t + 0.65)
    j.add(_ev(t, 0.5, 3.0, "weak"), now=t + 0.7)  # nothing known about it yet: prior says reliable
    assert j.poll(t + 0.65 + 0.4, CAMS) == []  # c2 can see the spot and hasn't reported
    assert len(j.poll(t + 0.65 + 0.61, CAMS)) == 1  # hold_s


def test_a_camera_that_cannot_see_the_spot_is_not_waited_for():
    j = _judge(can_see=lambda cam, x, y: cam != "weak")
    t = 10.0
    j.add(_ev(t, 0.5, 3.0, "c1"), now=t + 0.65)
    j.add(_ev(t, 0.5, 3.0, "c2"), now=t + 0.7)
    assert len(j.poll(t + 0.71, CAMS)) == 1


def test_a_late_report_corrects_the_hit_rate_it_was_counted_against():
    j = _judge()
    _teach_weak(j)
    before = list(j.recall.counts[("weak", 0)])
    t = 100.0
    j.add(_ev(t, 0.5, 3.0, "c1"), now=t + 0.65)
    j.add(_ev(t, 0.5, 3.0, "c2"), now=t + 0.66)
    (d,) = j.poll(t + 0.65 + j.weak_wait_s, CAMS)
    assert j.recall.counts[("weak", 0)] == [before[0], before[1] + 1]  # counted as a miss
    j.add(_ev(t + 0.01, 0.5, 3.0, "weak"), now=t + 1.2)  # it did see it, late
    assert j.late_reports == 1 and j.poll(t + 2.0, CAMS) == []  # no second decision
    assert j.recall.counts[("weak", 0)] == [before[0] + 1, before[1] + 1]  # miss -> hit
    j.add(_ev(t + 0.01, 0.5, 3.0, "weak"), now=t + 1.3)  # the same report again: no double credit
    assert j.recall.counts[("weak", 0)] == [before[0] + 1, before[1] + 1]


def test_stop_session_stops_every_phone_and_shuts_the_server_down(tmp_path):
    from balltracker.live.server import POST_HEADER, LiveServer

    async def run():
        srv = LiveServer(COURT, tmp_path)
        async with TestClient(TestServer(srv.make_app())) as cl:
            phone = await cl.ws_connect("/ws/edge")
            await phone.send_json({"type": "hello", "proto": 2, "mode": "edge", "name": "cam1", "width": 1280,
                                   "height": 720, "fps": 30, "algo": "edge_color_motion", "reduce": True})
            dash = await cl.ws_connect("/ws/dashboard")
            r = await (await cl.post("/api/stop", headers={POST_HEADER: "1"})).json()
            assert r["ok"] and r["report"].endswith("report.md")

            async def until_end(ws):
                while True:
                    m = await ws.receive_json(timeout=5)
                    if m.get("type") == "session_end":
                        return m

            assert "dashboard" in (await until_end(phone))["reason"]
            await until_end(dash)
            await asyncio.wait_for(srv.shutdown.wait(), timeout=5)
            again = await (await cl.post("/api/stop", headers={POST_HEADER: "1"})).json()  # a second click does nothing new
            assert again["ok"]
        stops = [line for line in (srv.session_dir / "events.jsonl").read_text().splitlines() if "session_stop" in line]
        assert len(stops) == 1

    asyncio.run(run())
    # cleanup ran (TestServer shuts the app down): the summary and the report are written
    import json

    sess = next((tmp_path / "sessions").iterdir())
    assert json.loads((sess / "session.json").read_text())["summary"] is not None
    assert (sess / "report.md").exists()


def test_replay_judges_with_the_calibration_in_use_at_the_time(monkeypatch):
    """Field 2026-11-22: a camera connected with yesterday's rough calibration (not used for calls)
    and recalibrated 9 minutes later. Live, its silence didn't count before the recalibration;
    the replay used its final calibration from the start and so vetoed two calls live had spoken."""
    import numpy as np

    from balltracker.geometry.camera import Camera
    from balltracker.live import fusion
    from balltracker.live.replay import judge_reports

    monkeypatch.setattr(fusion.PlayConfig, "for_scale", classmethod(lambda cls, s: PlayConfig(enabled=False)))
    hl = COURT.half_l

    def cam(pos, target, rms):
        c = Camera.look_at(np.array(pos), np.array(target), (1920, 1080), 70.0)
        c.reprojection_rms_px = rms
        return c

    a = cam([-4.6, -9.5, 2.4], [0.5, 0.0, 0.0], 0.5)
    b_rough, b_good = cam([4.6, 9.5, 2.4], [-0.5, 0.0, 0.0], None), cam([4.6, 9.5, 2.4], [-0.5, 0.0, 0.0], 0.8)
    inf = float("inf")
    cameras = {"a": {"camera": a, "timeline": [(0.0, a)], "online": [(0.0, inf)], "span": (0.0, 100.0), "gaps": []},
               "b": {"camera": b_good, "timeline": [(0.0, b_rough), (20.0, b_good)], "online": [(0.0, inf)],
                     "span": (0.0, 100.0), "gaps": []}}
    out = lambda t: _ev(t, 0.5, hl + 0.4, "a")  # noqa: E731 - an OUT only camera a reported
    early, late = judge_reports(COURT, cameras, {"a": [out(10.0), out(30.0)], "b": []})
    assert not early.get("unconfirmed_by")  # b's calibration wasn't in use yet: its silence doesn't veto
    assert not late["announce"] and late["unconfirmed_by"] == ["b"]  # now b could see it and didn't
    # a session from before connections logged their model: the last calibration throughout (as before)
    for c in cameras.values():
        c["online"] = None
    early, _ = judge_reports(COURT, cameras, {"a": [out(10.0), out(30.0)], "b": []})
    assert early["unconfirmed_by"] == ["b"]


def _report(t, x, y, cam, std=0.05):
    e = _ev(t, x, y, cam)
    return e.model_copy(update={"cov_xy": [[std**2, 0.0], [0.0, std**2]]})


FIELD3_CAMS = {"iphone", "nothing", "samsung"}


def _field3_3694(judge):
    """Review of a9fbde6, P1-1: field 3, bounce at 3694.55 s. The iPhone's report puts it 1.44 m past
    the right sideline; the other two cameras report the same moment inside the court, 4 and 13 ms
    later. From the iPhone's spot, the other two were judged unable to see."""
    t = 3694.55
    out = []
    for cam, x, y, arrive in (("iphone", 4.50, 5.82, 3694.798), ("nothing", -1.07, 5.49, 3694.802),
                              ("samsung", -0.86, -4.59, 3694.811)):
        judge.add(_report(t, x, y, cam), now=arrive)
        out += judge.poll(arrive, FIELD3_CAMS)
    out += judge.poll(t + 2.0, FIELD3_CAMS)
    return out


def test_a_lone_report_cannot_release_its_bounce_before_the_cameras_that_contradict_it():
    j = LiveJudge(COURT, hold_s=0.6, play=PlayConfig(enabled=False),
                  can_see=lambda cam, x, y: cam == "iphone" or x < 3.5)  # the far right edge: iPhone only
    j.poll(0.0, FIELD3_CAMS)
    (d,) = _field3_3694(j)
    assert j.late_reports == 0 and len(d.sources) == 3
    assert not d.call.announce  # a9fbde6: OUT announced on the iPhone alone, the other two dropped as late


def test_a_weak_cameras_agreeing_report_is_waited_for_when_it_is_the_only_confirmation():
    """Review of a9fbde6, P1-3: good camera OUT at the bounce; a weak camera (hit rate 0.15) reports the
    same OUT 0.4 s later. A lone report never releases early, so the call carries both cameras."""
    j = _judge()
    _teach_weak(j)
    t = 100.0
    two = {"c1", "weak"}  # the review's probe: one good camera and one weak one
    j.add(_ev(t, 0.5, COURT.half_l + 0.4, "c1"), now=t + 0.5)
    assert j.poll(t + 0.5 + j.weak_wait_s + 0.01, two) == []  # a9fbde6: released here, one camera
    j.add(_ev(t, 0.5, COURT.half_l + 0.4, "weak"), now=t + 0.9)
    (d,) = j.poll(t + 0.9, two)
    assert {e.camera_ids[0] for e in d.sources} == two


def test_two_agreeing_reports_still_skip_a_weak_camera():
    """The speed-up kept from a9fbde6: once two cameras agree, a weak one gets only weak_wait_s."""
    j = _judge()
    _teach_weak(j)
    t = 200.0
    j.add(_ev(t, 0.5, 3.0, "c1"), now=t + 0.5)
    j.add(_ev(t, 0.5, 3.0, "c2"), now=t + 0.55)
    assert len(j.poll(t + 0.5 + j.weak_wait_s, CAMS)) == 1


def test_two_disagreeing_reports_wait_for_every_camera():
    j = LiveJudge(COURT, hold_s=0.6, play=PlayConfig(enabled=False), can_see=lambda cam, x, y: cam != "weak")
    j.poll(0.0, CAMS)
    t = 300.0
    j.add(_report(t, 4.5, 3.0, "c1"), now=t + 0.5)
    j.add(_report(t, -1.0, 3.0, "c2"), now=t + 0.51)  # 5.5 m apart
    assert j.poll(t + 0.52, CAMS) == []  # "weak" can't see the spot, but the two reports don't agree
    assert len(j.poll(t + 0.5 + 0.61, CAMS)) == 1  # hold_s


def test_post_routes_refuse_requests_without_the_dashboard_header_or_from_another_origin(tmp_path):
    """Review of a9fbde6, P1-4: any device on the network could end the session with one POST, and a
    web page could send it from a browser (a body-less POST needs no CORS preflight)."""
    from balltracker.live.server import POST_HEADER, LiveServer

    async def run():
        srv = LiveServer(COURT, tmp_path)
        async with TestClient(TestServer(srv.make_app())) as cl:
            for path in ("/api/stop", "/api/context", "/api/play_mode", "/api/cameras/c1/calibrate",
                         "/api/cameras/c1/snap", "/api/cameras/c1/proposal"):
                assert (await cl.post(path, json={})).status == 403, path
                foreign = {POST_HEADER: "1", "Origin": "http://evil.example"}
                assert (await cl.post(path, json={}, headers=foreign)).status == 403, path
            assert not srv.shutdown.is_set() and not srv.stopping
            own = {POST_HEADER: "1", "Origin": str(cl.make_url("")).rstrip("/")}
            assert (await cl.post("/api/stop", headers=own)).status == 200

    asyncio.run(run())


def test_a_late_report_credits_the_released_bounce_it_was_counted_missing_from():
    """Review of a9fbde6, P3-8: two released bounces within the window of a late report; the camera
    was counted as missing only in the second. The credit used to look in the first one only."""
    j = _judge(can_see=lambda cam, x, y: cam != "weak" or y > 0)  # "weak" sees only the y > 0 half
    _teach_weak(j)
    before = list(j.recall.counts[("weak", 0)])
    t = 100.0
    for tt, y in ((t, -3.0), (t + 0.10, 3.0)):  # first: weak can't see; second: weak can and misses it
        j.add(_ev(tt, 0.5, y, "c1"), now=tt + 0.5)
        j.add(_ev(tt, 0.5, y, "c2"), now=tt + 0.5)
    assert len(j.poll(t + 2.0, CAMS)) == 2
    assert j.recall.counts[("weak", 0)] == [before[0], before[1] + 1]
    j.add(_ev(t + 0.05, 0.5, 3.0, "weak"), now=t + 2.1)  # within the window of both released bounces
    assert j.recall.counts[("weak", 0)] == [before[0] + 1, before[1] + 1]
