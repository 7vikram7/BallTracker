"""Regenerate the golden fixtures that tests/test_golden.py checks against.

Run this ONLY when a logic change is intended, then review the diff of tests/golden/
(git diff --stat tests/golden; the summary printed below) and commit it with the change:

    .venv/bin/python tests/golden/make_golden.py            # all fixtures
    .venv/bin/python tests/golden/make_golden.py --only expected   # just re-judge the frozen rally

Fixtures:
  edge_rally/          a recorded app-phone session (2 cameras, 8 bounces, synthetic truth):
                       dets.jsonl per camera + calibration + court  (inputs, frozen)
                       expected.json  decisions the current code makes from them
                       truth.json     true bounce positions/times on the session clock
  edge_detector_synth.json   phone detector output on a fixed synthetic clip (Python == C++)
  protocol_dets.json / .hex  a detections message: input and exact bytes (Python and JS must agree)
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))


def round_decision(d: dict) -> dict:
    keep = ("t", "x", "y", "result", "announce", "text", "line", "distance_cm", "p_out", "suppressed",
            "unconfirmed_by", "cameras", "confidence")
    out = {}
    for k in keep:
        v = d.get(k)
        out[k] = round(v, 5) if isinstance(v, float) else v
    return out


def make_rally(tmp: Path) -> None:
    from balltracker.live.fakephone import run_live_demo

    r = run_live_demo(["behind_baseline_high", "side_mid"], seed=11, shots=8, width=1280, height=720, fps=60,
                      data_dir=ROOT / "data" / "live_demo", port=8187, clock_offsets=[0.0, 37.0], drift_ppm=[0.0, 0.0],
                      verbose=False, edge=True, record=True)
    sd = Path(r["session_dir"])
    dst = HERE / "edge_rally"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir()
    shutil.copy(sd / "court.json", dst / "court.json")
    shutil.copytree(sd / "calibration", dst / "calibration")
    for cam in (p for p in sd.iterdir() if p.is_dir() and (p / "dets.jsonl").exists()):
        (dst / cam.name).mkdir()
        shutil.copy(cam / "dets.jsonl", dst / cam.name / "dets.jsonl")
    (dst / "events.jsonl").write_text("")  # no serve contexts in this rally
    shift = r["clip_to_session_s"]
    truth = [{"t": row["t"] + shift, "x": row["x"], "y": row["y"], "truth": row["truth"],
              "truth_dist_cm": row["truth_dist_cm"], "first": row["first"]} for row in r["rows"]]
    (dst / "truth.json").write_text(json.dumps(truth, indent=1))


def make_expected() -> None:
    from balltracker.live.replay import replay

    res = replay(HERE / "edge_rally")
    exp = [round_decision(d) for d in res["decisions"]]
    (HERE / "edge_rally" / "expected.json").write_text(json.dumps(exp, indent=1))
    print(f"edge_rally: {len(exp)} decisions: " + ", ".join(f"{d['t']:.2f}s {d['result']}" for d in exp))


def detector_frames(n=90, w=640, h=360):
    from balltracker.synthetic import SynthConfig, build_scene, frames

    scene = build_scene(SynthConfig(fps=60, width=w, height=h, n_shots=2, seed=3, camera_preset="behind_baseline_high"))
    out = []
    for _, _, img in frames(scene):
        out.append(img)
        if len(out) >= n:
            break
    return out


def make_detector() -> None:
    from balltracker.edge_detection import EdgeBallDetector, EdgeDetectorConfig

    det = EdgeBallDetector(EdgeDetectorConfig(fps=60))
    per_frame = [[[round(c.u, 2), round(c.v, 2), round(c.radius_px, 2), round(c.score, 3)] for c in det.detect(img)]
                 for img in detector_frames()]
    (HERE / "edge_detector_synth.json").write_text(json.dumps({"config": {"fps": 60}, "frames": per_frame}))
    print(f"edge_detector_synth: {sum(map(len, per_frame))} candidates in {len(per_frame)} frames")


def make_protocol() -> None:
    from balltracker.live.protocol import DetFrame, pack_detections

    inp = {"width": 1920, "height": 1080, "frames": [
        {"seq": 4294967295, "t": 123456.789012345, "c": [1.5, 2.25, 3.0, 0.875, 1919.75, 1079.5, 40.0, 1.0]},
        {"seq": 0, "t": -0.5, "c": []},
        {"seq": 77, "t": 1e-6, "c": [0.0, 0.0, 0.0, 0.0]},
    ]}
    frames = [DetFrame(f["seq"], f["t"], [tuple(f["c"][i:i + 4]) for i in range(0, len(f["c"]), 4)]) for f in inp["frames"]]
    (HERE / "protocol_dets.json").write_text(json.dumps(inp, indent=1))
    (HERE / "protocol_dets.hex").write_text(pack_detections(inp["width"], inp["height"], frames).hex() + "\n")
    print("protocol_dets: written")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=["rally", "expected", "detector", "protocol"])
    a = ap.parse_args()
    if a.only in (None, "rally"):
        make_rally(HERE)
    if a.only in (None, "rally", "expected"):
        make_expected()
    if a.only in (None, "detector"):
        make_detector()
    if a.only in (None, "protocol"):
        make_protocol()
