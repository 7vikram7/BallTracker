"""After one camera is confirmed, refine the others (geometry/crosscal.py)."""

import numpy as np

from balltracker.geometry.camera import Camera
from balltracker.geometry.court import CourtSpec
from balltracker.geometry.crosscal import BouncePairs, Pair, refine_with_bounces, resnap_proposal, visible_keypoints
from balltracker.synthetic import SynthConfig, build_scene, frames


def _perturbed(cam: Camera, deg: float = 0.6, focal: float = 1.03) -> Camera:
    import cv2

    R = cv2.Rodrigues(np.array([np.radians(deg), np.radians(-deg / 2), 0.0]))[0] @ cam.R
    K = cam.K.copy()
    K[0, 0] *= focal
    K[1, 1] *= focal
    return Camera(K=K, dist=cam.dist.copy(), R=R, t=cam.t.copy(), image_size=cam.image_size, camera_id=cam.camera_id)


def test_shared_bounces_fix_a_camera_bumped_after_calibration():
    court = CourtSpec.pickleball()
    truth = Camera.look_at(np.array([-4.5, 9.5, 2.4]), np.array([0.0, 1.0, 0.0]), (1920, 1080), 80.0, camera_id="b")
    wrong = _perturbed(truth)
    rng = np.random.default_rng(1)
    pairs = BouncePairs()
    r = court.ball_radius
    for i in range(40):
        xy = np.array([rng.uniform(-3.5, 3.5), rng.uniform(-6.5, 7.5)])
        px = truth.project(np.array([[xy[0], xy[1], r]]))[0] + rng.normal(0, 0.5, 2)
        own = wrong.intersect_plane_z(px[None], r)[0][:2]
        ref = xy + rng.normal(0, 0.01, 2)  # the reference camera measures to ~1 cm
        pairs.add(Pair(float(i), tuple(px), tuple(ref), "a", tuple(own)))
    assert pairs.ready()
    # the camera was bumped after calibration: its keypoints are those of the old (now wrong) pose
    kp = visible_keypoints(wrong, court)
    prop = refine_with_bounces(wrong, court, kp, pairs)
    assert prop is not None, "should propose"
    assert prop["after_cm"] < 0.5 * prop["before_cm"] and prop["after_cm"] < 3.0, prop["message"]


def test_no_proposal_when_the_cameras_already_agree():
    court = CourtSpec.pickleball()
    cam = Camera.look_at(np.array([4.5, 9.5, 2.4]), np.array([0.0, 1.0, 0.0]), (1920, 1080), 80.0, camera_id="b")
    rng = np.random.default_rng(2)
    pairs = BouncePairs()
    for i in range(30):
        xy = np.array([rng.uniform(-3, 3), rng.uniform(-6, 7)])
        px = cam.project(np.array([[xy[0], xy[1], court.ball_radius]]))[0]
        pairs.add(Pair(float(i), tuple(px), tuple(xy + rng.normal(0, 0.01, 2)), "a", tuple(xy)))
    assert refine_with_bounces(cam, court, visible_keypoints(cam, court), pairs) is None


def test_resnap_proposes_a_fix_for_a_drifted_calibration():
    scene = build_scene(SynthConfig(fps=30, width=1280, height=720, n_shots=1, seed=3, camera_preset="corner_high"))
    img = next(iter(frames(scene)))[2]
    drifted = _perturbed(scene.camera, deg=0.4, focal=1.02)
    prop = resnap_proposal(img, scene.court, drifted)
    assert prop is not None and prop["moved_px"] > 1.5
    true_kp = visible_keypoints(scene.camera, scene.court)
    err = [np.hypot(*(np.array(prop["points"][k]) - np.array(true_kp[k]))) for k in prop["points"] if k in true_kp]
    assert np.median(err) < 2.5, err
    # a correct calibration is left alone
    assert resnap_proposal(img, scene.court, scene.camera) is None


def test_shared_bounces_improve_a_calibration_from_few_noisy_clicks():
    court = CourtSpec.pickleball()
    truth = Camera.look_at(np.array([4.5, 9.5, 2.4]), np.array([0.0, 1.0, 0.0]), (1920, 1080), 80.0, camera_id="b")
    rng = np.random.default_rng(4)
    # five clicks on the near half only, 4 px noise: a poor calibration far away
    names = ["B_left_corner", "B_right_corner", "B_kitchen_left", "B_kitchen_right", "B_centre_baseline"]
    kp = court.keypoints()
    clicks = {k: (truth.project(np.array([kp[k]]))[0] + rng.normal(0, 4, 2)).tolist() for k in names}
    from balltracker.geometry.camera import calibrate_from_points
    poor = calibrate_from_points(np.array([kp[k] for k in names]), np.array([clicks[k] for k in names]),
                                 (1920, 1080), estimate_focal=False, hfov_guess_deg=76.0, camera_id="b")
    pairs = BouncePairs()
    r = court.ball_radius
    for i in range(40):
        xy = np.array([rng.uniform(-3.5, 3.5), rng.uniform(-6.5, 6.5)])
        px = truth.project(np.array([[xy[0], xy[1], r]]))[0] + rng.normal(0, 0.5, 2)
        pairs.add(Pair(float(i), tuple(px), tuple(xy + rng.normal(0, 0.01, 2)), "a",
                       tuple(poor.intersect_plane_z(px[None], r)[0][:2])))
    prop = refine_with_bounces(poor, court, clicks, pairs)
    assert prop is not None and prop["after_cm"] < 0.5 * prop["before_cm"], prop and prop["message"]


def test_dashboard_snap_then_calibrate_endpoints(tmp_path):
    import asyncio

    import cv2
    from aiohttp.test_utils import TestClient, TestServer

    from balltracker.live.server import CamState, LiveServer
    from balltracker.synthetic import calibration_clicks

    scene = build_scene(SynthConfig(fps=30, width=1280, height=720, n_shots=1, seed=3, camera_preset="corner_high"))
    img = next(iter(frames(scene)))[2]
    truth = calibration_clicks(scene)["points"]

    async def run():
        srv = LiveServer(scene.court, tmp_path)
        cam = CamState("c1")
        cam.latest_jpeg = cv2.imencode(".jpg", img)[1].tobytes()
        cam.latest_size = (1280, 720)
        srv.cams["c1"] = cam
        async with TestClient(TestServer(srv.make_app())) as cl:
            await cl.get("/api/cameras/c1/frame.jpg?cal=1")  # the dialog pins this image
            rng = np.random.default_rng(0)
            taps = {k: (np.array(truth[k]) + rng.normal(0, 20, 2)).tolist()
                    for k in ["B_left_corner", "B_right_corner", "B_kitchen_left", "B_kitchen_right"]}
            snap = await (await cl.post("/api/cameras/c1/snap", json={"points": taps})).json()
            err = [np.hypot(*(np.array(snap["points"][k]) - np.array(truth[k]))) for k in snap["points"]]
            assert snap["ok"] and np.median(err) < 2.5 and len(err) >= 8
            cal = await (await cl.post("/api/cameras/c1/calibrate",
                                       json={"points": snap["points"], "image_size": [1280, 720], "source": "snap"})).json()
            assert cal["ok"] and cal["rms_px"] < 1.5 and srv.reference_cam == "c1"

    asyncio.run(run())


def test_a_camera_labelled_from_the_other_end_is_detected_and_fixed():
    # Field 2026-11-20: the second phone stood at the B end and its nearest baseline was clicked
    # as "A". The fit is fine (the court is symmetric), but every bounce lands mirrored through
    # the centre. A few shared bounces reveal it; the proposal swaps the labels back.
    from balltracker.geometry.camera import calibrate_from_points
    from balltracker.geometry.crosscal import from_other_end, other_end_proposal

    court = CourtSpec.pickleball().scaled(0.2)
    kp = court.keypoints()
    truth = Camera.look_at(np.array([1.0, 1.6, 1.6]), np.array([0.0, 0.0, 0.0]), (1920, 1080), 70.0, camera_id="b")
    names = [k for k in visible_keypoints(truth, court)]
    seen = {k: truth.project(np.array([kp[k]]))[0].tolist() for k in names}
    clicked = from_other_end(seen)  # what the user did: labels from this camera's own end
    fit = lambda pts: calibrate_from_points(np.array([kp[k] for k in pts]), np.array([pts[k] for k in pts]),
                                            (1920, 1080), camera_id="b")
    wrong = fit(clicked)
    rng = np.random.default_rng(3)
    r = court.ball_radius

    def pairs_for(cam):
        pairs = BouncePairs()
        for i in range(6):
            xy = np.array([rng.uniform(-0.6, 0.6), rng.uniform(-1.3, 1.3)])
            px = truth.project(np.array([[xy[0], xy[1], r]]))[0]
            pairs.add(Pair(float(i), tuple(px), tuple(xy), "a", tuple(cam.intersect_plane_z(px[None], r)[0][:2])))
        return pairs

    assert other_end_proposal(BouncePairs(pairs_for(wrong).pairs[:2]), court, clicked) is None  # needs 3
    prop = other_end_proposal(pairs_for(wrong), court, clicked)
    assert prop is not None and prop["source"] == "other_end" and prop["after_cm"] < 5, prop
    fixed = fit(prop["points"])
    centre = lambda c: -c.R.T @ np.asarray(c.t).ravel()
    assert np.allclose(centre(wrong)[:2], -centre(truth)[:2], atol=0.05)  # the wrong one sits mirrored
    assert np.allclose(centre(fixed), centre(truth), atol=0.05)
    assert other_end_proposal(pairs_for(fixed), court, prop["points"]) is None  # agrees now
