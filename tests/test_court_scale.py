"""A practice court at any scale (bt serve --court-scale 0.2)."""

import numpy as np

from balltracker.cli import _court
from balltracker.live.fusion import LiveJudge
from balltracker.live.playstate import PlayConfig


def test_court_scale_scales_lines_not_the_ball():
    full, mini = _court(None), _court(None, 0.2)
    assert np.isclose(mini.half_l, 0.2 * full.half_l) and np.isclose(mini.half_w, 0.2 * full.half_w)
    assert mini.ball_radius == full.ball_radius and mini.line_width == full.line_width
    assert mini.scale == 0.2


def test_play_thresholds_follow_the_scale():
    c = PlayConfig.for_scale(0.25)
    assert np.isclose(c.shot_mps, 2.5) and np.isclose(c.second_pos_tol_m, 0.375)
    assert LiveJudge(_court(None, 0.25)).play.cfg.shot_mps == c.shot_mps
    assert LiveJudge(_court(None)).play.cfg.shot_mps == PlayConfig().shot_mps


def test_practice_court_calibrations_are_kept_apart(tmp_path):
    from balltracker.live.server import LiveServer

    a = LiveServer(_court(None), tmp_path)
    b = LiveServer(_court(None, 0.2), tmp_path)
    assert a.calib_dir.name == "calibration" and b.calib_dir.name == "calibration-scale0.2"
