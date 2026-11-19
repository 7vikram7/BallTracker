import numpy as np
import pytest

from balltracker.geometry.court import FT, INCH, CourtSpec, ServiceSide, Side


def test_regulation_dimensions():
    c = CourtSpec.pickleball()
    assert c.width == pytest.approx(20 * FT)
    assert c.length == pytest.approx(44 * FT)
    assert c.kitchen_depth == pytest.approx(7 * FT)
    assert c.line_width == pytest.approx(2 * INCH)


def test_scaled_keeps_ball_and_tape_real_size():
    c = CourtSpec.pickleball().scaled(0.5)
    assert c.width == pytest.approx(10 * FT)
    assert c.ball_radius == CourtSpec().ball_radius
    assert c.line_width == CourtSpec().line_width


def test_load_custom_yaml(tmp_path):
    p = tmp_path / "c.yaml"
    p.write_text("base: pickleball\nunits: cm\nwidth: 250\nlength: 540\nkitchen_depth: 85\n")
    c = CourtSpec.load(p)
    assert c.width == pytest.approx(2.5)
    assert c.length == pytest.approx(5.4)
    assert c.kitchen_depth == pytest.approx(0.85)


def test_serve_targets_are_diagonal():
    c = CourtSpec()
    # Server on side A in their right court (+X) serves to B's right court (-X).
    r = c.serve_target(Side.A, ServiceSide.RIGHT)
    assert r.y0 == pytest.approx(c.kitchen_depth) and r.y1 == pytest.approx(c.half_l)
    assert r.x0 == pytest.approx(-c.half_w)
    assert r.x1 == pytest.approx(c.line_width / 2)  # centreline belongs to both courts
    # Server on B in their right court (-X from B's view... B faces -Y, right is -X) -> A's right (+X).
    r2 = c.serve_target(Side.B, ServiceSide.RIGHT)
    assert r2.x1 == pytest.approx(c.half_w) and r2.y1 == pytest.approx(-c.kitchen_depth)


def test_kitchen_line_not_part_of_service_court():
    c = CourtSpec()
    r = c.serve_target(Side.A, ServiceSide.RIGHT)
    # A point in the middle of the kitchen line (on B) is outside the service court.
    y_on_kitchen_line = c.kitchen_depth - c.line_width / 2
    assert not r.contains(np.array(-1.0), np.array(y_on_kitchen_line))


def test_signed_distance():
    c = CourtSpec()
    r = c.half_rect(Side.B)
    assert float(r.signed_distance(np.array(0.0), np.array(c.half_l + 0.05))) == pytest.approx(0.05)
    assert float(r.signed_distance(np.array(0.0), np.array(c.half_l - 0.05))) == pytest.approx(-0.05)
