"""After one camera is confirmed, refine the others.

Two independent sources, both offered to the user as a proposal (never applied silently):

1. **Court lines** (:func:`resnap_proposal`): every camera's current calibration is snapped to
   the painted lines in its own image (``autocal.refine_from`` started from the keypoints the
   current calibration predicts). Runs right after any camera is saved. Cameras do not share
   anything here; it simply re-checks every camera while the user is at the dashboard.

2. **Shared bounces** (:class:`BouncePairs`, :func:`refine_with_bounces`): this is where the
   confirmed camera helps the others. Every bounce seen by the confirmed (reference) camera
   and by another camera gives that camera one more ground correspondence: its own pixel of
   the ball at contact <-> the court position measured by the reference camera. Court lines
   only constrain a camera where lines are visible; bounces land everywhere play happens, in
   particular near the lines being called. After enough well-spread bounces, the camera is
   recalibrated from its keypoints plus the bounces, and the proposal reports how much
   closer the two cameras now agree.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .camera import Camera, CalibrationError, calibrate_from_points
from .court import CourtSpec

ALGO = "cross_camera_refine"
ALGO_VERSION = "0.1.0"


def visible_keypoints(camera: Camera, court: CourtSpec, margin: float = 0.02) -> dict[str, list[float]]:
    """Ground keypoints the camera's current model puts inside its image."""
    w, h = camera.image_size
    out = {}
    for name, (x, y, z) in court.keypoints().items():
        if z != 0 or name.startswith("net_"):
            continue
        X = np.array([[x, y, 0.0]])
        if camera.depth(X)[0] <= 0.1:
            continue
        u, v = camera.project(X)[0]
        if -margin * w <= u <= (1 + margin) * w and -margin * h <= v <= (1 + margin) * h:
            out[name] = [float(u), float(v)]
    return out


def resnap_proposal(img: np.ndarray, court: CourtSpec, camera: Camera, min_move_px: float = 1.5) -> dict | None:
    """Snap the camera's current calibration to the court lines. -> proposal dict, or None when
    the snap is not convincing or changes nothing worth reviewing."""
    from .autocal import refine_from

    init = visible_keypoints(camera, court)
    if len(init) < 4:
        return None
    res = refine_from(img, court, init)
    if not res.ok:
        return None
    common = [k for k in res.points if k in init]
    if not common:
        return None
    moved = float(np.median([np.hypot(*(np.array(res.points[k]) - np.array(init[k]))) for k in common]))
    if moved < min_move_px:
        return None
    return {"source": "lines", "points": res.points, "moved_px": round(moved, 1),
            "fit_px": res.debug.get("fit_px"), "lines": res.debug.get("lines"),
            "message": f"Snapping to the court lines moves the points by {moved:.1f} px (median); "
                       f"lines fit to {res.debug.get('fit_px')} px."}


@dataclass
class Pair:
    t: float
    pixel: tuple[float, float]  # this camera's ball centre at contact
    ref_xy: tuple[float, float]  # court position from the reference camera
    ref_camera: str
    own_xy: tuple[float, float]  # where this camera itself put the bounce


@dataclass
class BouncePairs:
    """Bounces seen by both this camera and the reference camera, for :func:`refine_with_bounces`."""
    pairs: list[Pair] = field(default_factory=list)
    max_pairs: int = 400

    def add(self, pair: Pair) -> None:
        self.pairs.append(pair)
        if len(self.pairs) > self.max_pairs:
            self.pairs = self.pairs[-self.max_pairs:]

    def spread_m(self) -> tuple[float, float]:
        if not self.pairs:
            return 0.0, 0.0
        xy = np.array([p.ref_xy for p in self.pairs])
        return float(np.ptp(xy[:, 0])), float(np.ptp(xy[:, 1]))

    def ready(self, min_pairs: int = 15, min_spread_m: float = 2.0) -> bool:
        sx, sy = self.spread_m()
        return len(self.pairs) >= min_pairs and sx >= min_spread_m and sy >= min_spread_m

    def disagreement_cm(self) -> float | None:
        if not self.pairs:
            return None
        d = [np.hypot(p.own_xy[0] - p.ref_xy[0], p.own_xy[1] - p.ref_xy[1]) for p in self.pairs]
        return float(100 * np.median(d))


def _ground_xy(camera: Camera, px: tuple[float, float], z: float) -> np.ndarray:
    return camera.intersect_plane_z(np.array([px], float), z)[0][:2]


def refine_with_bounces(camera: Camera, court: CourtSpec, keypoints_px: dict[str, list[float]],
                        pairs: BouncePairs, min_gain: float = 0.7, max_pair_err_m: float = 2.0) -> dict | None:
    """Recalibrate ``camera`` from its keypoints (the user's points, or what its model predicts)
    plus the shared bounces. -> proposal {camera, points, before_cm, after_cm, ...} or None if it
    does not bring the cameras clearly closer (after < min_gain * before).

    ``max_pair_err_m`` is generous on purpose: pairs come from bounces the judge already grouped
    as one event, and the biases this fixes are large (field test 2: the Samsung put far-half
    bounces 0.7-1.5 m from where the iPhone did; refining from 15 shared bounces cut that to
    21-49 cm on held-out bounces)."""
    if not pairs.pairs:
        return None
    r = court.ball_radius
    kp = court.keypoints()
    names = [k for k in keypoints_px if k in kp]
    good = [p for p in pairs.pairs if np.hypot(p.own_xy[0] - p.ref_xy[0], p.own_xy[1] - p.ref_xy[1]) <= max_pair_err_m]
    if len(good) < 8:
        return None
    hfov = float(np.degrees(2 * np.arctan(camera.image_size[0] / 2 / camera.focal_px)))
    bobj = [[p.ref_xy[0], p.ref_xy[1], r] for p in good]
    bimg = [list(p.pixel) for p in good]
    # Two fits: keypoints + bounces (the keypoints were clicked on this camera's image), and
    # bounces alone (if the camera was bumped after calibration, its keypoints are stale and
    # would hold the fit back). Keep the one that agrees better with the reference camera.
    fits = []
    for obj, img in (([kp[k] for k in names] + bobj, [keypoints_px[k] for k in names] + bimg),
                     (bobj, bimg) if len(good) >= 15 else (None, None)):
        if obj is None:
            continue
        try:
            new = calibrate_from_points(np.array(obj, float), np.array(img, float), tuple(camera.image_size),
                                        hfov_guess_deg=hfov, estimate_focal=True, camera_id=camera.camera_id)
        except CalibrationError:
            continue
        err = [np.hypot(*(_ground_xy(new, p.pixel, r) - np.array(p.ref_xy))) for p in good]
        if np.all(np.isfinite(err)):
            fits.append((float(np.median(err)), new, len(obj) == len(bobj)))
    if not fits:
        return None
    a_m, new, bounces_only = min(fits, key=lambda f: f[0])
    before = [np.hypot(*(np.array(p.own_xy) - np.array(p.ref_xy))) for p in good]
    b, a = float(100 * np.median(before)), 100 * a_m
    if not a < min_gain * b:
        return None
    pts = visible_keypoints(new, court)
    return {"source": "bounces", "camera": new, "points": pts, "pairs": len(good), "before_cm": round(b, 1),
            "after_cm": round(a, 1), "ref_camera": good[-1].ref_camera, "bounces_only": bounces_only,
            "message": f"{len(good)} bounces seen together with {good[-1].ref_camera}: the two cameras disagree by "
                       f"{b:.1f} cm (median) now, {a:.1f} cm with the refined calibration."}
