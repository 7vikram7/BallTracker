"""Live server pieces: clock sync, wire format, fusion, judge, certificates, end to end."""

import numpy as np
import pytest

from balltracker.events import BounceEvent, Point3, Provenance
from balltracker.geometry.court import CourtSpec, ServiceSide, Side
from balltracker.live.clocksync import ClockSync
from balltracker.live.fusion import LiveJudge, fuse
from balltracker.live.protocol import pack_frame, unpack_frame
from balltracker.sports.pickleball.line_calling import ServeContext


def test_clock_sync_recovers_offset_and_drift_under_jittery_wifi():
    rng = np.random.default_rng(0)
    offset, drift = 1234.5678, 40e-6  # phone = (server - offset) * (1 - drift) roughly
    cs = ClockSync()
    t = 1000.0
    for _ in range(120):
        up = 0.002 + rng.exponential(0.015)  # bursty, asymmetric delays
        down = 0.002 + rng.exponential(0.015)
        ts0 = t
        tp = (ts0 + up - offset) * (1 + drift)
        ts1 = ts0 + up + down
        cs.add(ts0, tp, ts1)
        t += 0.5
    # Map a phone timestamp back and compare with the truth.
    for ts_true in (1010.0, 1030.0, 1059.0):
        tp = (ts_true - offset) * (1 + drift)
        assert abs(cs.to_server(tp) - ts_true) < 0.003
    assert cs.ready and cs.uncertainty < 0.01


def test_frame_roundtrip():
    msg = pack_frame(42, 12345.678901, 1280, 720, b"\xff\xd8jpeg")
    f = unpack_frame(msg)
    assert (f.seq, f.width, f.height, f.jpeg) == (42, 1280, 720, b"\xff\xd8jpeg")
    assert abs(f.t_phone - 12345.678901) < 1e-9
    with pytest.raises(ValueError):
        unpack_frame(b"XXXX" + msg[4:])


def _ev(x, y, sx, sy, t=1.0, cam="c1", conf=0.9):
    return BounceEvent(t=t, t_std=0.002, position=Point3(x=x, y=y), cov_xy=[[sx**2, 0], [0, sy**2]], pixel=(0, 0),
                       camera_ids=[cam], confidence=conf, supporting_observations=[],
                       provenance=Provenance(algorithm="test", version="0"))


def test_fusion_weights_by_covariance_and_inflates_on_disagreement():
    # Camera 1 precise in x, camera 2 precise in y.
    a = _ev(3.00, 6.00, 0.01, 0.10, cam="c1")
    b = _ev(3.05, 6.05, 0.10, 0.01, cam="c2")
    f, d = fuse([a, b])
    assert abs(f.position.x - 3.00) < 0.002 and abs(f.position.y - 6.05) < 0.002
    assert d["inflation"] == 1.0 and f.camera_ids == ["c1", "c2"]
    # Two confident cameras 30 cm apart: not believable, so uncertainty grows.
    f2, d2 = fuse([_ev(3.0, 6.0, 0.01, 0.01, cam="c1"), _ev(3.3, 6.0, 0.01, 0.01, cam="c2")])
    assert d2["inflation"] > 10
    assert np.sqrt(f2.cov_xy[0][0]) > 0.05


def test_judge_groups_cameras_suppresses_secondary_and_uses_serve_once():
    court = CourtSpec.pickleball()
    j = LiveJudge(court, hold_s=0.5)
    hw, hl = court.half_w, court.half_l
    # Bounce 1: clearly out past baseline B, seen by two cameras 20 ms apart.
    j.add(_ev(0.0, hl + 0.30, 0.02, 0.02, t=1.00, cam="c1"), now=1.2)
    j.add(_ev(0.0, hl + 0.31, 0.02, 0.02, t=1.02, cam="c2"), now=1.3)
    out = j.poll(1.31, expected_cameras={"c1", "c2"})  # complete -> released immediately
    assert len(out) == 1 and out[0].call.call_text == "OUT" and len(out[0].bounce.camera_ids) == 2
    # Its second bounce, further from the net, 0.4 s later: suppressed.
    j.add(_ev(0.0, hl + 1.5, 0.02, 0.02, t=1.40, cam="c1"), now=1.6)
    out = j.poll(2.2)
    assert out[0].call is None and out[0].suppressed
    # Serve context applies to the next bounce only.
    j.serve = ServeContext(Side.A, ServiceSide.RIGHT)
    j.add(_ev(-1.0, court.kitchen_depth - 0.2, 0.01, 0.01, t=5.0), now=5.1)  # lands in the kitchen: fault
    out = j.poll(6.0)
    assert out[0].call.call_text == "FAULT" and j.serve is None
    j.add(_ev(0.0, -hl + 1.0, 0.01, 0.01, t=8.0), now=8.1)
    assert j.poll(9.0)[0].call.context.value == "rally"


def test_certificates(tmp_path):
    from cryptography import x509

    from balltracker.live.certs import ensure_server_cert

    crt, key, hosts = ensure_server_cert(tmp_path)
    pem = crt.read_bytes()
    leaf = x509.load_pem_x509_certificate(pem)
    ca = x509.load_pem_x509_certificate((tmp_path / "ca.crt").read_bytes())
    leaf.verify_directly_issued_by(ca)
    san = leaf.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    assert "localhost" in san.get_values_for_type(x509.DNSName)
    assert any(str(ip) == "127.0.0.1" for ip in san.get_values_for_type(x509.IPAddress))
    assert ensure_server_cert(tmp_path)[2] == hosts  # reused, not re-issued


@pytest.mark.slow
def test_live_server_end_to_end_two_phones(tmp_path):
    """Two simulated phones with different clock offsets/drifts film one rally."""
    from balltracker.live.fakephone import run_live_demo

    res = run_live_demo(["behind_baseline_high", "side_mid"], seed=11, shots=5, width=960, height=540, fps=60,
                        data_dir=tmp_path, port=8197, clock_offsets=[0.0, 52.3], drift_ppm=[30.0, -45.0], verbose=False)
    s = res["summary"]
    # Browser path decodes JPEGs on the Mac: allow one miss under load, otherwise tight.
    assert s["first_bounces_called"] >= s["true_first_bounces"] - 1
    assert s["median_err_cm"] < 2.5 and s["p90_err_cm"] < 6.0
    assert s["multi_camera"] >= 2  # fixed scene: 3 of 5 bounces are visible to both cameras
    assert s["wrong_out"] == 0 and s["false_decisions"] == 0
    assert s["median_latency_s"] < 1.5
    assert abs(s["median_abs_dt_ms"]) < 5  # clock sync across offset + drifting phone clocks


def test_out_needs_a_second_camera_when_two_can_see_it():
    court = CourtSpec.pickleball()
    hl = court.half_l
    j = LiveJudge(court, hold_s=0.3, can_see=lambda cam, x, y: True)
    j.poll(0.0, expected_cameras={"c1", "c2"})
    j.add(_ev(0.0, hl + 0.4, 0.02, 0.02, t=1.0, cam="c1"), now=1.1)
    d = j.poll(1.5, expected_cameras={"c1", "c2"})[0]
    assert d.call.result.value == "UNCERTAIN" and not d.call.announce
    assert d.diagnostics["unconfirmed_by"] == ["c2"]
    # If only c1 can see that spot, its report alone is enough.
    j2 = LiveJudge(court, hold_s=0.3, can_see=lambda cam, x, y: cam == "c1")
    j2.poll(0.0, expected_cameras={"c1", "c2"})
    j2.add(_ev(0.0, hl + 0.4, 0.02, 0.02, t=1.0, cam="c1"), now=1.1)
    assert j2.poll(1.5, expected_cameras={"c1", "c2"})[0].call.call_text == "OUT"


def test_low_confidence_bounce_is_never_announced():
    court = CourtSpec.pickleball()
    j = LiveJudge(court, hold_s=0.1)
    j.add(_ev(0.0, court.half_l + 1.0, 0.02, 0.02, t=1.0, conf=0.4), now=1.0)
    d = j.poll(2.0)[0]
    assert d.call.result.value == "UNCERTAIN" and not d.call.announce


def test_frame_clock_removes_browser_timestamp_jitter():
    from balltracker.live.frameclock import FrameClock

    rng = np.random.default_rng(1)
    true = 1000.0 + np.arange(900) / 60
    keep = rng.random(900) > 0.1  # 10 % dropped frames
    obs = true + rng.uniform(-0.004, 0.004, 900)  # ±4 ms jitter (seen in browsers)
    fc = FrameClock()
    err = np.abs([fc.fit(o) - t for o, t, k in zip(obs, true, keep) if k][60:]) * 1e3  # after ~1 s warm-up
    assert np.median(err) < 0.6 and err.max() < 2.0, (np.median(err), err.max())
    fc = FrameClock()  # accurate timestamps pass through unchanged
    assert max(abs(fc.fit(t) - t) for t in true) < 1e-6
    # Frame-rate change 60 -> 30 fps with an off-grid phase: re-anchors and follows.
    t2 = np.concatenate([np.arange(300) / 60, 5.007 + np.arange(300) / 30])
    fc = FrameClock()
    out = np.array([fc.fit(x) for x in t2 + rng.uniform(-0.002, 0.002, 600)])
    assert np.median(np.abs(out[340:] - t2[340:])) < 0.6e-3


def test_cameras_that_disagree_do_not_announce():
    # Field 2026-11-20: one camera was labelled from the other end, so the two cameras put the same
    # bounce up to 2.5 m apart. Fusion inflates the covariance on disagreement; that alone does not
    # stop a call: here a precise camera says OUT by 30 cm, another says IN by 50 cm, and the
    # inflated fusion still gave p(out) 0.97 -> spoken OUT. Now: silent unless both say OUT.
    from balltracker.live.playstate import PlayConfig

    court = CourtSpec.pickleball()
    hl = court.half_l
    j = LiveJudge(court, hold_s=0.3, play=PlayConfig(enabled=False))
    j.add(_ev(0.0, hl + 0.30, 0.01, 0.01, t=1.0, cam="c1"), now=1.05)
    j.add(_ev(0.0, hl - 0.50, 0.04, 0.04, t=1.0, cam="c2"), now=1.06)
    d = j.poll(2.0)[0]
    assert d.diagnostics["inflation"] > 100 and d.call.p_out > 0.95
    assert not d.call.announce and d.diagnostics.get("cameras_disagree")
    # Disagreeing on the exact spot but both clearly OUT: still announced.
    j2 = LiveJudge(court, hold_s=0.3, play=PlayConfig(enabled=False))
    j2.add(_ev(0.0, hl + 0.30, 0.02, 0.02, t=1.0, cam="c1"), now=1.05)
    j2.add(_ev(0.0, hl + 0.50, 0.02, 0.02, t=1.0, cam="c2"), now=1.06)
    d2 = j2.poll(2.0)[0]
    assert d2.diagnostics["inflation"] > 1 and d2.call.call_text == "OUT"
