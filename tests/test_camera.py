import numpy as np
import pytest

from balltracker.geometry.camera import Camera, calibrate_from_points
from balltracker.geometry.court import CourtSpec


@pytest.fixture
def cam():
    return Camera.look_at(np.array([0.0, 11.7, 4.0]), np.array([0.0, 4.0, 0.0]), (1920, 1080), 65.0)


def test_project_and_back(cam):
    P = np.array([[1.0, 5.0, 0.0], [-2.0, 3.0, 0.0]])
    px = cam.project(P)
    back = cam.intersect_plane_z(px, 0.0)
    assert np.allclose(back, P, atol=1e-6)


def test_ball_centre_vs_contact_correction(cam):
    """Mapping the ball CENTRE through the ground plane overshoots; z=r doesn't."""
    r = 0.0371
    contact = np.array([2.0, 6.0, 0.0])
    centre = contact + [0, 0, r]
    px = cam.project(centre[None])
    naive = cam.intersect_plane_z(px, 0.0)[0]
    corrected = cam.intersect_plane_z(px, r)[0]
    assert np.allclose(corrected[:2], contact[:2], atol=1e-6)
    assert np.linalg.norm(naive[:2] - contact[:2]) > 0.05  # > 5 cm error if not corrected


def test_calibration_recovers_pose_and_focal(cam):
    court = CourtSpec()
    kp = court.keypoints()
    names, obj, img = [], [], []
    rng = np.random.default_rng(0)
    for n, P in kp.items():
        uv = cam.project(np.array(P)[None])[0]
        if 0 <= uv[0] < 1920 and 0 <= uv[1] < 1080 and cam.depth(np.array(P)[None])[0] > 0:
            names.append(n)
            obj.append(P)
            img.append(uv + rng.normal(0, 1.0, 2))
    est = calibrate_from_points(obj, img, (1920, 1080), hfov_guess_deg=55.0)
    assert est.reprojection_rms_px < 2.0
    assert abs(est.focal_px - cam.focal_px) / cam.focal_px < 0.03
    assert np.linalg.norm(est.position - cam.position) < 0.10


def test_save_load_roundtrip(cam, tmp_path):
    p = tmp_path / "cam.json"
    cam.save(p)
    c2 = Camera.load(p)
    assert np.allclose(c2.K, cam.K) and np.allclose(c2.R, cam.R) and np.allclose(c2.t, cam.t)
