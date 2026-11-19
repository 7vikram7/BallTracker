"""Automatic court calibration (experimental): works on clean synthetic courts; real footage
(field test 2) still gives 10-25 px errors at far corners, so it is not offered in the dashboard yet."""

import numpy as np

from balltracker.geometry.autocal import autocalibrate, line_mask, refine_from
from balltracker.synthetic import SynthConfig, build_scene, calibration_clicks, frames


def _scene(preset):
    scene = build_scene(SynthConfig(fps=30, width=1280, height=720, n_shots=1, seed=3, camera_preset=preset))
    return scene, next(iter(frames(scene)))[2], calibration_clicks(scene)["points"]


def _err(pts, truth):
    e = [np.hypot(*(np.array(pts[k]) - np.array(truth[k]))) for k in pts if k in truth]
    return np.median(e), len(e)


def test_snap_from_four_rough_clicks_finds_every_keypoint():
    scene, img, truth = _scene("behind_baseline_high")
    rng = np.random.default_rng(0)
    four = [k for k in truth if "corner" in k][:4]
    res = refine_from(img, scene.court, {k: (np.array(truth[k]) + rng.normal(0, 15, 2)).tolist() for k in four})
    med, n = _err(res.points, truth)
    assert res.ok and n >= 10 and med < 4.0, (med, n, res.message)


def test_fully_automatic_finds_the_court_up_to_the_side_ambiguity():
    scene, img, truth = _scene("side_mid")
    res = autocalibrate(img, scene.court)
    assert res.ok
    best = min(_err(res.points, truth)[0], _err(res.flipped_points, truth)[0])  # A/B needs a marker
    assert best < 5.0
    assert res.ambiguous and res.side_from == "nearest-half"


def test_line_mask_keeps_paint_drops_blank_court():
    scene, img, truth = _scene("behind_baseline_high")
    m = line_mask(img)
    u, v = map(int, truth["A_centre_kitchen"])
    assert m[max(0, v - 6):v + 6, max(0, u - 6):u + 6].any()
    assert 0.002 < (m > 0).mean() < 0.15
