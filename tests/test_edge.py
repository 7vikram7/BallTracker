"""Phone-side (edge) pieces: detector reference, C++ parity, protocol 2, server edge path."""

import shutil

import cv2
import numpy as np
import pytest

from balltracker.edge_detection import EdgeBallDetector, EdgeDetectorConfig, bin_image, gate
from balltracker.live.protocol import DetFrame, pack_detections, pack_preview, unpack_detections, unpack_frame, PREVIEW_MAGIC


def _synthetic_frames(n=150, fps=60.0, w=640, h=360, seed=3):
    from balltracker.synthetic import SynthConfig, build_scene, frames

    scene = build_scene(SynthConfig(fps=fps, width=w, height=h, n_shots=2, seed=seed, camera_preset="behind_baseline_high"))
    out = []
    for _, _, img in frames(scene):
        out.append(img)
        if len(out) >= n:
            break
    return out


def test_integer_gate_matches_opencv_hsv_away_from_rounding_edges():
    rng = np.random.default_rng(0)
    img = rng.integers(0, 256, (200, 200, 3), dtype=np.uint8)
    lo, hi = (25, 100, 90), (55, 255, 255)
    ours = gate(img, lo, hi)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(int)
    cv = cv2.inRange(hsv.astype(np.uint8), np.array(lo), np.array(hi)) > 0
    # OpenCV rounds H and S; we test the exact inequality. They may only differ at the boundaries.
    edge = (np.abs(hsv[..., 0] - lo[0]) <= 1) | (np.abs(hsv[..., 0] - hi[0]) <= 1) | (np.abs(hsv[..., 1] - lo[1]) <= 1)
    assert np.all(ours[~edge] == cv[~edge])
    assert ours.sum() > 100


def test_binning_rounds_half_up():
    img = np.zeros((4, 4, 3), np.uint8)
    img[0, 0] = img[0, 1] = (1, 1, 1)  # block sum 2 of 4 -> (2 + 2) // 4 = 1
    assert bin_image(img, 2)[0, 0, 0] == 1


def test_edge_detector_finds_the_ball_on_synthetic_video():
    det = EdgeBallDetector(EdgeDetectorConfig(fps=60))
    frames = _synthetic_frames()
    hits = sum(1 for f in frames if det.detect(f))
    assert hits > 40


@pytest.mark.skipif(shutil.which("clang++") is None and shutil.which("c++") is None, reason="no C++ compiler")
@pytest.mark.parametrize("fmt", ["BGR", "BGRA", "RGBA"])
def test_cpp_detector_matches_python_reference(fmt):
    from balltracker.ballcore import NativeDetector

    py = EdgeBallDetector(EdgeDetectorConfig(fps=60))
    nat = NativeDetector(EdgeDetectorConfig(fps=60), fmt=fmt)
    conv = {"BGR": None, "BGRA": cv2.COLOR_BGR2BGRA, "RGBA": cv2.COLOR_BGR2RGBA}[fmt]
    total = 0
    for img in _synthetic_frames():
        a = py.detect(img)
        b = nat.detect(img if conv is None else cv2.cvtColor(img, conv))
        assert len(a) == len(b)
        for p, q in zip(sorted(a, key=lambda c: (c.u, c.v)), sorted(b, key=lambda c: (c.u, c.v))):
            assert abs(p.u - q.u) < 1e-3 and abs(p.v - q.v) < 1e-3
            assert abs(p.radius_px - q.radius_px) < 1e-3 and abs(p.score - q.score) < 1e-4
        total += len(a)
    assert total > 40


@pytest.mark.skipif(shutil.which("clang++") is None and shutil.which("c++") is None, reason="no C++ compiler")
def test_cpp_detector_respects_roi_and_reset():
    from balltracker.ballcore import NativeDetector

    frames = _synthetic_frames(n=90)
    h, w = frames[0].shape[:2]
    roi = np.zeros((h, w), np.uint8)  # search nowhere
    nat = NativeDetector(EdgeDetectorConfig(fps=60, roi_mask=roi))
    assert all(not nat.detect(f) for f in frames)
    py = EdgeBallDetector(EdgeDetectorConfig(fps=60, roi_mask=roi))
    assert all(not py.detect(f) for f in frames)


def test_detections_roundtrip_and_preview():
    frames = [DetFrame(7, 123.456789, [(10.5, 20.25, 3.0, 0.9), (1.0, 2.0, 1.5, 0.4)]), DetFrame(8, 123.46, [])]
    b = unpack_detections(pack_detections(1920, 1080, frames))
    assert (b.width, b.height, len(b.frames)) == (1920, 1080, 2)
    assert b.frames[0].seq == 7 and abs(b.frames[0].t_phone - 123.456789) < 1e-9
    assert b.frames[0].cands[0] == pytest.approx((10.5, 20.25, 3.0, 0.9), abs=1e-6)
    assert b.frames[1].cands == []
    with pytest.raises(ValueError):
        unpack_detections(pack_detections(1920, 1080, frames)[:-5])
    p = unpack_frame(pack_preview(3, 1.5, 640, 360, b"\xff\xd8x"), PREVIEW_MAGIC)
    assert (p.seq, p.width, p.jpeg) == (3, 640, b"\xff\xd8x")


@pytest.mark.slow
def test_live_server_end_to_end_edge_phones(tmp_path):
    """Two simulated app phones send detections only; same accuracy bar as the browser path."""
    from balltracker.live.fakephone import run_live_demo

    res = run_live_demo(["behind_baseline_high", "side_mid"], seed=11, shots=5, width=960, height=540, fps=60,
                        data_dir=tmp_path, port=8198, clock_offsets=[0.0, 52.3], drift_ppm=[30.0, -45.0],
                        verbose=False, edge=True)
    s = res["summary"]
    assert s["mode"] == "edge"
    # No video on the Mac: every first bounce, both cameras, fast.
    assert s["first_bounces_called"] == s["true_first_bounces"]
    assert s["multi_camera"] >= 3  # in this fixed scene 2 of the 5 bounces are visible to one camera only
    assert s["median_err_cm"] < 2.0 and s["p90_err_cm"] < 5.0
    assert s["wrong_out"] == 0 and s["missed_out"] == 0 and s["false_decisions"] == 0
    assert s["median_latency_s"] < 1.0
    assert abs(s["median_abs_dt_ms"]) < 5
    assert all(c["server_drops"] == 0 and c["unsynced"] == 0 for c in s["cameras"].values())
    assert all(p["config"] is not None for p in s["phones"])  # server sent the detector config


@pytest.mark.slow
@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_app_javascript_core_against_live_server(tmp_path):
    """The app's own JS (mobile/src/core) with a mock camera, against the real server."""
    from balltracker.live.fakephone import run_live_demo

    res = run_live_demo(["behind_baseline_high", "side_mid"], seed=11, shots=5, width=960, height=540, fps=60,
                        data_dir=tmp_path, port=8199, clock_offsets=[5.0, -37.0], drift_ppm=[0.0, 0.0],
                        verbose=False, edge=True, edge_client="node")
    s = res["summary"]
    assert s["first_bounces_called"] == s["true_first_bounces"]
    assert s["median_err_cm"] < 2.0 and s["wrong_out"] == 0 and s["false_decisions"] == 0
    assert s["median_latency_s"] < 1.0
    for ph in s["phones"]:
        assert ph["connection"] == "connected" and ph["calibrated"] and ph["configs"] >= 1
        assert ph["droppedFrames"] == 0 and ph["sentFrames"] > 100


def test_app_javascript_unit_tests():
    """Runs mobile/test/*.test.js with Node's built-in test runner (no npm packages needed)."""
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node not installed")
    root = Path(__file__).resolve().parents[1]
    tests = sorted(str(p) for p in (root / "mobile" / "test").glob("*.test.js"))
    r = subprocess.run(["node", "--test", *tests], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout[-3000:] + r.stderr[-2000:]


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_wasm_detector_matches_python_reference(tmp_path):
    """The browser build (static/ballcore.wasm) gives the reference's candidates, from RGBA as a canvas provides."""
    import json
    import subprocess
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    frames = _synthetic_frames(n=120)
    h, w = frames[0].shape[:2]
    raw = tmp_path / "f.rgba"
    raw.write_bytes(b"".join(cv2.cvtColor(f, cv2.COLOR_BGR2RGBA).tobytes() for f in frames))
    r = subprocess.run(["node", str(root / "tests/js/wasm_detect.js"), str(raw), str(w), str(h), str(len(frames)), "60"],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr
    got = json.loads(r.stdout)["frames"]
    py = EdgeBallDetector(EdgeDetectorConfig(fps=60))
    total = 0
    for img, flat in zip(frames, got):
        exp = sorted((c.u, c.v, c.radius_px, c.score) for c in py.detect(img))
        cands = sorted(tuple(flat[i:i + 4]) for i in range(0, len(flat), 4))
        assert len(cands) == len(exp)
        for a, b in zip(cands, exp):
            assert np.allclose(a, b, atol=1e-3)
        total += len(exp)
    assert total > 40


def test_browser_reducer_is_the_app_reducer():
    """The phone page serves a copy of the app's reducer; they must not drift apart."""
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    app = (root / "mobile" / "src" / "core" / "reducer.js").read_text()
    page = (root / "balltracker" / "live" / "static" / "reducer.js").read_text()
    assert app == page, "copy mobile/src/core/reducer.js to balltracker/live/static/reducer.js"
