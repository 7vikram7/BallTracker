"""Golden tests: frozen inputs -> the exact outputs the current logic produced.

They fail on ANY change to detection, tracking, bounce, fusion or line-call logic.
If the change is intended: run `.venv/bin/python tests/golden/make_golden.py`, read the
printed summary and `git diff tests/golden`, and commit the new fixtures with the change.
The accuracy checks against synthetic truth must still pass after regenerating.
"""

import json
import os
import shutil
from pathlib import Path

import numpy as np
import pytest

GOLDEN = Path(__file__).parent / "golden"
HOW = "If this change is intended, run: .venv/bin/python tests/golden/make_golden.py (then review git diff tests/golden)."


@pytest.fixture(scope="module")
def rally_replay():
    from balltracker.live.replay import replay

    return replay(GOLDEN / "edge_rally")


def test_frozen_rally_gives_the_same_decisions(rally_replay):
    exp = json.loads((GOLDEN / "edge_rally" / "expected.json").read_text())
    got = rally_replay["decisions"]
    assert len(got) == len(exp), f"{len(got)} decisions, expected {len(exp)}. {HOW}"
    for g, e in zip(got, exp):
        where = f"bounce at t={e['t']:.3f}s"
        assert (g.get("result"), g.get("announce"), g.get("suppressed"), g.get("line")) == \
               (e["result"], e["announce"], e["suppressed"], e["line"]), f"call changed at {where}. {HOW}"
        assert sorted(g["cameras"]) == sorted(e["cameras"]), f"cameras changed at {where}. {HOW}"
        assert abs(g["t"] - e["t"]) < 1e-4, f"bounce time moved at {where}. {HOW}"
        assert np.hypot(g["x"] - e["x"], g["y"] - e["y"]) < 1e-3, f"bounce position moved >1 mm at {where}. {HOW}"
        assert abs(g["p_out"] - e["p_out"]) < 0.01, f"p(out) changed at {where}. {HOW}"


def test_frozen_rally_accuracy_against_truth(rally_replay):
    """Independent of the golden values: these bars must hold even after regenerating."""
    truth = json.loads((GOLDEN / "edge_rally" / "truth.json").read_text())
    dec = [d for d in rally_replay["decisions"] if not d.get("suppressed")]
    errs, wrong_out, missed_out, unmatched = [], 0, 0, 0
    for tb in (t for t in truth if t["first"]):
        m = min(dec, key=lambda d: abs(d["t"] - tb["t"]), default=None)
        if m is None or abs(m["t"] - tb["t"]) > 0.03:
            unmatched += 1
            continue
        errs.append(100 * np.hypot(m["x"] - tb["x"], m["y"] - tb["y"]))
        wrong_out += int(m.get("announce") and m.get("result") == "OUT" and tb["truth"] == "IN")
        missed_out += int(tb["truth"] == "OUT" and not m.get("announce"))
    assert unmatched == 0, f"{unmatched} true first bounces without a decision"
    assert wrong_out == 0
    assert missed_out == 0
    assert np.median(errs) < 1.5 and np.percentile(errs, 90) < 3.5, f"errors (cm): {np.round(errs, 2)}"
    assert len(dec) == sum(t["first"] for t in truth), "extra (false) decisions"


def test_replay_with_one_camera_missing(tmp_path):
    """Replay copes with a camera whose recording is missing (single-camera decisions)."""
    from balltracker.live.replay import replay

    exp = json.loads((GOLDEN / "edge_rally" / "expected.json").read_text())
    d = tmp_path / "s"
    shutil.copytree(GOLDEN / "edge_rally", d)
    # Drop camera 2 entirely: decisions become single-camera. Camera 2 has no recording, so it is
    # not an expected camera and can't veto: the lone OUT is still called (and announced).
    shutil.rmtree(d / "sim-side_mid")
    res = replay(d)
    assert all(len(x["cameras"]) == 1 for x in res["decisions"])
    out_t = [e["t"] for e in exp if e["result"] == "OUT"]
    assert out_t, "fixture should contain an OUT"
    assert any(abs(x["t"] - out_t[0]) < 0.01 and x["result"] == "OUT" and x["announce"] for x in res["decisions"])


def test_phone_detector_golden_python_and_cpp():
    from balltracker.edge_detection import EdgeBallDetector, EdgeDetectorConfig
    from tests.golden.make_golden import detector_frames

    exp = json.loads((GOLDEN / "edge_detector_synth.json").read_text())["frames"]
    frames = detector_frames()
    dets = [("python", EdgeBallDetector(EdgeDetectorConfig(fps=60)))]
    if shutil.which("clang++") or shutil.which("c++"):
        from balltracker.ballcore import NativeDetector

        dets.append(("c++", NativeDetector(EdgeDetectorConfig(fps=60))))
    elif os.environ.get("BT_REQUIRE_ALL") == "1":
        pytest.fail("no C++ compiler: the C++ leg of this test can't run (BT_REQUIRE_ALL=1)")
    for name, det in dets:
        for i, (img, e) in enumerate(zip(frames, exp)):
            got = [[c.u, c.v, c.radius_px, c.score] for c in det.detect(img)]
            assert len(got) == len(e), f"{name}: frame {i}: {len(got)} candidates, expected {len(e)}. {HOW}"
            # the fixture stores u, v, r to 0.01 px and score to 0.001: allow exactly that rounding
            tol = np.array([0.005, 0.005, 0.005, 0.0005]) + 1e-6
            for g, x in zip(sorted(got), sorted(e)):
                assert np.all(np.abs(np.array(g) - np.array(x)) <= tol), f"{name}: frame {i}: {g} != {x}. {HOW}"


def test_protocol_bytes_are_frozen():
    from balltracker.live.protocol import DetFrame, pack_detections, unpack_detections

    inp = json.loads((GOLDEN / "protocol_dets.json").read_text())
    frames = [DetFrame(f["seq"], f["t"], [tuple(f["c"][i:i + 4]) for i in range(0, len(f["c"]), 4)]) for f in inp["frames"]]
    data = pack_detections(inp["width"], inp["height"], frames)
    assert data.hex() == (GOLDEN / "protocol_dets.hex").read_text().strip(), \
        "wire format changed: the app (mobile/src/core/protocol.js) must change with it, and PROTO_VERSION should go up"
    back = unpack_detections(data)
    assert back.frames[0].seq == 4294967295 and back.frames[1].cands == []


def test_golden_check_catches_a_small_logic_change(tmp_path):
    """Guard for the guard: a 1.2 mm change in geometry must break the frozen-rally comparison (the
    documented bar is 1 mm)."""
    from balltracker.live.replay import compare, replay

    d = tmp_path / "s"
    shutil.copytree(GOLDEN / "edge_rally", d)
    court = json.loads((d / "court.json").read_text())
    court["ball_radius"] = court["ball_radius"] + 0.0012
    (d / "court.json").write_text(json.dumps(court))
    exp = json.loads((GOLDEN / "edge_rally" / "expected.json").read_text())
    c = compare(exp, replay(d)["decisions"], moved_cm=0.1)
    assert not c["identical"] and c["moved"], c
