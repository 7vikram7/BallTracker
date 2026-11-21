"""Load-dependent worker actions replay the same; stalls don't make OUTs from unsettled bounces; a
camera that didn't process a bounce's frames doesn't veto it (review of defed68: TODO-14, 18, 19;
decision log entry 28)."""

import json

import numpy as np

from balltracker.events import BounceEvent, Point3, Provenance
from balltracker.geometry.camera import Camera
from balltracker.geometry.court import CourtSpec
from balltracker.live.fusion import LiveJudge
from balltracker.live.playstate import PlayConfig
from balltracker.live.server import covered
from balltracker.live.worker import LiveCameraPipeline, LiveConfig, flush_ctl, handle_dets

COURT = CourtSpec.pickleball()
G = 9.81
FPS = 120


def camera():
    cam = Camera.look_at(position=[0.0, -9.5, 3.0], target=[0.0, 2.0, 0.0], image_size=(1280, 720), hfov_deg=60)
    cam.reprojection_rms_px = 0.5
    return cam


def flight(t0=10.0, p0=(0.5, 0.0, 1.0), v0=(0.2, 7.0, -1.0), dur=0.9, e=0.6):
    """Ball positions at FPS: a parabola down to a bounce, then up again. -> (times, xyz, t_bounce)"""
    r = COURT.ball_radius
    p, v = np.array(p0, float), np.array(v0, float)
    ts, ps, tb, dt = [], [], None, 1.0 / FPS
    t = t0
    while t < t0 + dur:
        ts.append(t)
        ps.append(p.copy())
        v[2] -= G * dt
        p = p + v * dt
        if p[2] < r and v[2] < 0:
            p[2] = r + (r - p[2]) * e
            v[2] = -v[2] * e
            tb = t + dt if tb is None else tb
        t += dt
    return np.array(ts), np.array(ps), tb


def frames_for(cam, ts, ps):
    out = []
    for k, (t, p) in enumerate(zip(ts, ps)):
        u, v = cam.project(p[None])[0]
        depth = float(cam.depth(p[None])[0])
        rad = float(cam.K[0, 0] * COURT.ball_radius / depth)
        out.append((1000 + k, float(t), [(float(u), float(v), rad, 1.0)]))
    return out


def live_run(cam, frames, lag_of):
    """Feed 6-frame batches as the live worker would, with lag_of(batch index) seconds of lag."""
    pipe = LiveCameraPipeline("c", COURT, cam, LiveConfig())
    out = []
    for i in range(0, len(frames), 6):
        out += handle_dets(pipe, frames[i:i + 6], (1280, 720), lag_of(i // 6))
    out += flush_ctl(pipe, frames[-1][0])
    return out


def write_session(tmp, cam, frames, ctl):
    d = tmp / "s"
    (d / "calibration").mkdir(parents=True)
    (d / "court.json").write_text(json.dumps(COURT.to_dict()))
    cam.save(d / "calibration" / "c.json")
    (d / "c").mkdir()
    (d / "c" / "dets.jsonl").write_text("".join(
        json.dumps({"seq": s, "ts": t, "c": [list(cand) for cand in cl], "w": 1280, "h": 720}) + "\n"
        for s, t, cl in frames))
    (d / "events.jsonl").write_text("".join(json.dumps({"type": "worker_ctl", **{k: v for k, v in o.items() if k != "kind"}})
                                            + "\n" for o in ctl))
    return d


def bounces(msgs):
    return [round(BounceEvent.model_validate(o["event"]).t, 4) for o in msgs if o.get("kind") == "bounce"]


def test_replay_applies_the_live_workers_drops_and_deferrals(tmp_path):
    from balltracker.live.replay import camera_reports, load_session

    cam = camera()
    ts, ps, tb = flight()
    frames = frames_for(cam, ts, ps)
    k = int(np.searchsorted(ts, tb)) // 6
    # live: behind (deferring) from the start, then so far behind around the bounce that its
    # batches were dropped
    live = live_run(cam, frames, lambda i: 2.0 if k - 3 <= i <= k + 3 else 0.5)
    ctl = [o for o in live if o.get("kind") == "ctl"]
    assert {o["op"] for o in ctl} >= {"drop", "defer", "flush"}
    assert bounces(live) == []  # the bounce's frames never reached the bounce search
    s = load_session(write_session(tmp_path, cam, frames, ctl))
    info = s["cameras"]["c"]
    assert [round(e.t, 4) for e in camera_reports("c", info, s["court"])] == bounces(live)
    assert info["gaps"], "the dropped stretch is a gap in what the camera processed"
    # without the log, replay would have found a bounce the live run never reported
    info["ctl"] = []
    assert len(camera_reports("c", info, s["court"])) == 1
    # and with no load at all, live and replay agree on that bounce
    calm = live_run(cam, frames, lambda i: 0.0)
    assert len(bounces(calm)) == 1 and not [o for o in calm if o.get("kind") == "ctl" and o["op"] != "flush"]


def test_a_bounce_finalised_without_settling_is_marked_and_cannot_make_an_out():
    cam = camera()
    ts, ps, tb = flight()
    frames = frames_for(cam, ts, ps)
    cut = int(np.searchsorted(ts, tb)) + 8  # the stream stops 8 frames (67 ms) after the bounce
    pipe = LiveCameraPipeline("c", COURT, cam, LiveConfig())
    out = handle_dets(pipe, frames[:cut], (1280, 720), 0.0) + flush_ctl(pipe, frames[cut - 1][0])
    evs = [BounceEvent.model_validate(o["event"]) for o in out if o.get("kind") == "bounce"]
    assert len(evs) == 1 and evs[0].provenance.params.get("unsettled") is True
    # the judge: an OUT resting only on unsettled reports is silent; one settled report is enough
    hl = COURT.half_l

    def ev(cam_id, unsettled):
        return BounceEvent(t=1.0, t_std=0.002, position=Point3(x=0.5, y=hl + 0.3), cov_xy=[[4e-4, 0], [0, 4e-4]],
                           pixel=(0.0, 0.0), camera_ids=[cam_id], confidence=1.0, supporting_observations=[],
                           provenance=Provenance(algorithm="t", version="0", params={"unsettled": unsettled}))

    for evs, spoken in (([ev("a", True)], False), ([ev("a", True), ev("b", True)], False),
                        ([ev("a", True), ev("b", False)], True)):
        j = LiveJudge(COURT, hold_s=0.3, play=PlayConfig(enabled=False))
        for e in evs:
            j.add(e, 1.05)
        d = j.flush()[0]
        assert d.call.announce is spoken, (evs, d.diagnostics)
        if not spoken:
            assert d.diagnostics.get("unsettled")


def test_flush_waits_a_full_lookback():
    assert LiveConfig().flush_after_s >= LiveConfig().lookback_s


def test_a_camera_that_has_not_processed_the_bounce_does_not_veto_it():
    hl = COURT.half_l
    ev = BounceEvent(t=5.0, t_std=0.002, position=Point3(x=0.5, y=hl + 0.4), cov_xy=[[4e-4, 0], [0, 4e-4]],
                     pixel=(0.0, 0.0), camera_ids=["A"], confidence=1.0, supporting_observations=[],
                     provenance=Provenance(algorithm="t", version="0"))
    for b_processed, spoken in ((True, False), (False, True)):
        j = LiveJudge(COURT, hold_s=0.3, play=PlayConfig(enabled=False), can_see=lambda c, x, y: True,
                      processed=lambda c, t: c != "B" or b_processed)
        j.poll(0.0, expected_cameras={"A", "B"})
        j.add(ev, 5.05)
        d = j.poll(6.0, expected_cameras={"A", "B"})[0]
        assert d.call.announce is spoken
        if not b_processed:
            assert d.diagnostics["not_processed"] == ["B"]
            assert j.recall.counts == {}  # an unknown camera isn't counted as missing it either


def test_coverage_of_a_time():
    gaps = [(10.0, 10.6)]
    assert covered(20.0, gaps, 5.0)
    assert not covered(20.0, gaps, 10.3) and not covered(20.0, gaps, 10.65)  # inside / just after a gap
    assert not covered(5.1, [], 5.0)  # the worker hasn't got that far yet


def _stopping_ball_frames(w=480, h=270, fps=60):
    import cv2

    rng = np.random.default_rng(0)
    bg = cv2.add(np.full((h, w, 3), (70, 110, 60), np.uint8), rng.integers(0, 25, (h, w, 3), dtype=np.uint8))
    out = []
    for k in range(3 * fps):
        img = bg.copy()
        x = 100 + 200 * min(k / fps, 1.0)  # rolls for 1 s, then lies still for 2 s
        cv2.circle(img, (int(x), 150), 4, (40, 230, 220), -1)
        out.append(img)
    return out


def test_mac_and_phone_detectors_agree_on_a_ball_that_stops():
    """TODO-16: JPEG cameras on the Mac run the phone's detector, so a ball that stops is seen
    for the same frames as on the phone (MOG2 dropped it after ~0.2 s, the phone keeps it ~2 s)."""
    from balltracker.edge_detection import EdgeBallDetector, EdgeDetectorConfig

    frames = _stopping_ball_frames()
    pipe = LiveCameraPipeline("c", COURT, None, LiveConfig())
    pipe.set_fps(60)
    phone = EdgeBallDetector(EdgeDetectorConfig(fps=60))  # the app's reference implementation
    mac_hits = [bool(pipe.detector.detect(f)) for f in frames]
    phone_hits = [bool(phone.detect(f)) for f in frames]
    assert mac_hits == phone_hits
    assert sum(mac_hits[60:]) > 100  # the stopped ball stays visible
    old = LiveCameraPipeline("c", COURT, None, LiveConfig(mac_detector="mog2"))  # how older sessions replay
    assert sum(bool(old.detector.detect(f)) for f in frames[60:]) < 30


def test_track_ending_counts_time_not_frames():
    from balltracker.detection import Candidate
    from balltracker.tracking import BallTracker, TrackerConfig

    def lifetime(fps, cfg):
        tr = BallTracker(cfg)
        c = [Candidate(u=100.0, v=100.0, radius_px=4, score=1, area_px=50, elongation=1)]
        for k in range(10):
            tr.update(k, k / fps, [Candidate(u=100.0 + 3 * k, v=100.0, radius_px=4, score=1, area_px=50, elongation=1)])
        k = 10
        while tr.active_tracks():
            tr.update(k, k / fps, [])
            k += 1
        return (k - 10) / fps

    by_frames = TrackerConfig()
    assert lifetime(30, by_frames) > 3 * lifetime(120, by_frames)  # 5 misses: 167 ms vs 42 ms
    by_time = TrackerConfig(max_miss_s=0.085)
    assert abs(lifetime(30, by_time) - lifetime(120, by_time)) < 0.04


def test_phone_warnings_for_delivered_fps_clock_and_detector_errors():
    """TODO-23/24: what the app reports reaches the operator."""
    from balltracker.live.server import phone_warnings

    assert phone_warnings("s", 120, {"fps_capture": 118}, "app:realtime") == []
    w = phone_warnings("s", 120, {"fps_capture": 58, "detect_errors": 3}, "app:converted:uptime")
    texts = " | ".join(x["text"] for x in w)
    assert "asked for 120 fps, the camera delivers 58" in texts
    assert "failed on 3 frames" in texts and "not on the expected clock" in texts


def test_a_shirt_sized_blob_makes_no_bounce():
    """TODO-17: a blob 5-6x a ball's size at that spot (a shirt swaying and bobbing) made bounces."""
    cam = camera()
    noise = np.random.default_rng(18).normal(0, 1, 360)
    frames = [(k, 10 + k / 120, [(float(640 + 248 * np.sin(2 * np.pi * 0.45 * k / 120)),
                                  float(310 - 95 * abs(np.sin(2 * np.pi * 1.02 * k / 120))),
                                  float(16.8 * (1 + 0.1 * noise[k])), 0.6)]) for k in range(360)]

    def run(cfg):
        pipe = LiveCameraPipeline("c", COURT, cam, cfg)
        out = handle_dets(pipe, frames, (1280, 720), 0.0) + flush_ctl(pipe, frames[-1][0])
        return [o["event"]["provenance"]["params"]["r_ratio"] for o in out if o.get("kind") == "bounce"]

    unchecked = run(LiveConfig(max_ball_radius_ratio=None))
    assert unchecked and min(unchecked) > 3.0, unchecked  # without the check: clutter bounces
    assert run(LiveConfig()) == []
    # a real ball at the same spot keeps its bounce (ratio ~1)
    ts, ps, _ = flight()
    pipe = LiveCameraPipeline("c", COURT, cam, LiveConfig())
    out = handle_dets(pipe, frames_for(cam, ts, ps), (1280, 720), 0.0) + flush_ctl(pipe, 10**6)
    rr = [o["event"]["provenance"]["params"]["r_ratio"] for o in out if o.get("kind") == "bounce"]
    assert len(rr) == 1 and 0.7 < rr[0] < 1.4
