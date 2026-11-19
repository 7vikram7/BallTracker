import json

import numpy as np
import pytest

from balltracker.events import AnalysisResult
from balltracker.synthetic import SynthConfig, build_scene, frames, write_scene
from balltracker.video import VideoFileSource


def test_video_roundtrip_timestamps(tmp_path):
    from balltracker.video import write_video

    imgs = [np.full((64, 96, 3), i * 10, np.uint8) for i in range(12)]
    p = tmp_path / "v.mp4"
    write_video(p, iter(imgs), 120.0, (96, 64))
    src = VideoFileSource(p)
    fr = list(src.frames())
    assert len(fr) == 12
    assert src.info.fps == pytest.approx(120.0, rel=0.01)
    assert np.allclose(np.diff([f.t for f in fr]), 1 / 120, atol=1e-4)


@pytest.mark.slow
def test_end_to_end_synthetic_cli(tmp_path):
    from balltracker.cli import main

    cfg = SynthConfig(fps=240, width=960, height=540, n_shots=3, seed=11)
    scene = build_scene(cfg)
    paths = write_scene(scene, tmp_path)
    main(["calibrate", "--points", str(paths["calibration_points"]), "--hfov", "55", "--out", str(tmp_path / "cam.json")])
    main(["analyze", str(paths["video"]), "--calib", str(tmp_path / "cam.json"), "--out", str(tmp_path / "res.json")])
    res = AnalysisResult.model_validate_json((tmp_path / "res.json").read_text())
    gt = json.loads(paths["ground_truth"].read_text())
    from balltracker.evaluate import load_truth, match, summarise, visible_truth
    from balltracker.geometry.court import CourtSpec

    court = CourtSpec(**res.court)
    truth = visible_truth(load_truth(paths["ground_truth"], court), gt, court)
    s = summarise(match(res, truth))
    assert s["recall"] >= 0.66
    assert s["WRONG_OUT_CALLS"] == 0
