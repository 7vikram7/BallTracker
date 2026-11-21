"""Did a camera move since it was calibrated? If a little: follow it; if a lot: say so.

Field test 3 (2026-11-21) registered each camera's snapshots against the frame it was calibrated
on: the iPhone turned 17 px sideways after half an hour (a bump), the Samsung tilted slowly and
then jumped about 25 px. The calibration stayed as it was, so the two cameras' bounce positions
drifted apart by up to a metre.

How it works:

* At calibration the server keeps a *reference*: the calibration frame, downscaled to grey, with
  ORB features.
* Every few seconds the latest snapshot is matched against it. Players move, the court, net,
  fences and walls do not, so RANSAC on a similarity transform (shift, rotation, zoom) finds the
  camera's motion from the static background.
* The transform moves the calibration's keypoints. ``DriftTracker`` always compares with the
  original calibration frame (re-referencing after each correction let matching noise add up:
  73 corrections in an hour on the field-test recording) and acts when the points' median
  position differs from the one in use by ``min_move_px`` or more on two checks in a row (one
  check can be fooled by a player filling the view). It then snaps the moved points to the
  painted lines (``autocal.refine_from``) and recalibrates from them. Moved more than
  ``max_move_px``, or too few background matches: the dashboard asks for a recalibration
  instead of guessing.

A pure image transform is exact for a camera that only rotates (a phone turning on its mount);
for a small shift of the camera's position it is a good approximation of the ground plane's
motion, and the line snap corrects the rest.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .camera import Camera, CalibrationError, calibrate_from_points
from .court import CourtSpec


@dataclass
class DriftConfig:
    work_width: int = 960          # match on a downscaled image (precision ~0.3 px x scale)
    n_features: int = 2500
    min_inliers: int = 60          # fewer background matches: can't tell (covered, dark, moved a lot)
    ransac_px: float = 2.0         # at full resolution
    min_move_px: float = 3.0       # keypoints moved at least this much (median): recalibrate
    max_move_px: float = 80.0      # moved more: don't follow automatically, ask for a recalibration
    snap_max_fit_px: float = 1.5   # use the line snap only if the lines fit this well ...
    snap_max_change_px: float = 6.0  # ... and it agrees with the moved points this closely


class DriftReference:
    """The frame a calibration was made on, ready for matching."""

    def __init__(self, img: np.ndarray, cfg: DriftConfig | None = None):
        import cv2

        self.cfg = cfg or DriftConfig()
        self.size = (int(img.shape[1]), int(img.shape[0]))
        self.k = min(1.0, self.cfg.work_width / img.shape[1])
        self.orb = cv2.ORB_create(self.cfg.n_features)
        g = _grey(img, self.k)
        self.kp, self.des = self.orb.detectAndCompute(g, None)

    @property
    def usable(self) -> bool:
        return self.des is not None and len(self.kp) >= self.cfg.min_inliers


def _grey(img: np.ndarray, k: float) -> np.ndarray:
    import cv2

    g = img if img.ndim == 2 else cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    if k != 1.0:
        g = cv2.resize(g, (round(g.shape[1] * k), round(g.shape[0] * k)), interpolation=cv2.INTER_AREA)
    return g


def estimate_motion(ref: DriftReference, img: np.ndarray) -> dict | None:
    """Similarity transform reference -> current image (full-resolution pixels), or None when
    the background can't be matched. -> {"A": 2x3, "inliers": n, "matches": m}"""
    import cv2

    if not ref.usable or (img.shape[1], img.shape[0]) != ref.size:
        return None
    kp, des = ref.orb.detectAndCompute(_grey(img, ref.k), None)
    if des is None or len(kp) < ref.cfg.min_inliers:
        return None
    m = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(ref.des, des)
    if len(m) < ref.cfg.min_inliers:
        return None
    p0 = np.float32([ref.kp[x.queryIdx].pt for x in m]) / ref.k
    p1 = np.float32([kp[x.trainIdx].pt for x in m]) / ref.k
    A, inl = cv2.estimateAffinePartial2D(p0, p1, method=cv2.RANSAC, ransacReprojThreshold=ref.cfg.ransac_px,
                                         maxIters=4000, confidence=0.999)
    if A is None or inl is None or int(inl.sum()) < ref.cfg.min_inliers:
        return None
    return {"A": A, "inliers": int(inl.sum()), "matches": len(m)}


def move_points(A: np.ndarray, points: dict[str, list[float]]) -> dict[str, list[float]]:
    return {k: [float(A[0, 0] * u + A[0, 1] * v + A[0, 2]), float(A[1, 0] * u + A[1, 1] * v + A[1, 2])]
            for k, (u, v) in points.items()}


def max_shift_px(A: np.ndarray, points: dict[str, list[float]]) -> float:
    moved = move_points(A, points)
    return max((float(np.hypot(moved[k][0] - u, moved[k][1] - v)) for k, (u, v) in points.items()), default=0.0)


def check_drift(ref: DriftReference, img: np.ndarray, court: CourtSpec, camera: Camera,
                points: dict[str, list[float]], snap: bool = True) -> dict:
    """One drift check. Returns {"status": ...} with

    * "steady": moved less than ``min_move_px`` (``moved_px`` given);
    * "moved": followed; ``points`` (new keypoints), ``camera`` (new model), ``moved_px``, ``how``;
    * "big": moved more than ``max_move_px``: recalibrate by hand;
    * "lost": the background could not be matched (camera covered, dark, or moved very far).
    """
    cfg = ref.cfg
    mot = estimate_motion(ref, img)
    if mot is None:
        return {"status": "lost"}
    A = mot["A"]
    moved_px = max_shift_px(A, points)
    base = {"moved_px": round(moved_px, 1), "inliers": mot["inliers"]}
    if moved_px < cfg.min_move_px:
        return {"status": "steady", **base}
    if moved_px > cfg.max_move_px:
        return {"status": "big", **base}
    new_pts = move_points(A, points)
    how = "image motion"
    if snap:
        from .autocal import refine_from

        try:
            res = refine_from(img, court, new_pts)
        except Exception:  # pragma: no cover - a failed snap must not stop the tracking
            res = None
        if res is not None and res.ok and (res.debug or {}).get("fit_px", 99) <= cfg.snap_max_fit_px:
            common = [k for k in res.points if k in new_pts]
            if common and np.median([np.hypot(*(np.array(res.points[k]) - np.array(new_pts[k]))) for k in common]) \
                    <= cfg.snap_max_change_px:
                new_pts = {k: [float(a), float(b)] for k, (a, b) in res.points.items()}
                how = "image motion + line snap"
    kp = court.keypoints()
    names = [k for k in new_pts if k in kp]
    try:
        cam = calibrate_from_points(np.array([kp[k] for k in names], float), np.array([new_pts[k] for k in names], float),
                                    tuple(camera.image_size), camera_id=camera.camera_id,
                                    estimate_focal=len(names) >= 6)
    except CalibrationError:
        return {"status": "big", **base}
    return {"status": "moved", **base, "points": {k: new_pts[k] for k in names}, "camera": cam, "how": how}


def _median_dist(a: dict[str, list[float]], b: dict[str, list[float]]) -> float:
    common = [k for k in a if k in b]
    return float(np.median([np.hypot(a[k][0] - b[k][0], a[k][1] - b[k][1]) for k in common])) if common else 0.0


class DriftTracker:
    """Follows one camera from the frame it was calibrated on (see the module docstring)."""

    def __init__(self, img: np.ndarray, points: dict[str, list[float]], cfg: DriftConfig | None = None):
        self.ref = DriftReference(img, cfg)
        self.cfg = self.ref.cfg
        self.base = {k: [float(u), float(v)] for k, (u, v) in points.items()}
        self.applied = dict(self.base)  # the image-motion points the calibration in use follows
        self.pending: dict[str, list[float]] | None = None

    def check(self, img: np.ndarray, court: CourtSpec, camera: Camera, snap: bool = True) -> dict:
        """-> {"status": "steady" | "pending" | "moved" | "big" | "lost", ...}; "moved" carries
        ``points`` and ``camera`` (the new calibration) like ``check_drift``."""
        cfg = self.cfg
        mot = estimate_motion(self.ref, img)
        if mot is None:
            return {"status": "lost"}
        moved = move_points(mot["A"], self.base)
        total = max_shift_px(mot["A"], self.base)
        change = _median_dist(moved, self.applied)
        base = {"moved_px": round(change, 1), "total_px": round(total, 1), "inliers": mot["inliers"]}
        if total > cfg.max_move_px:
            self.pending = None
            return {"status": "big", **base}
        if change < cfg.min_move_px:
            self.pending = None
            return {"status": "steady", **base}
        if self.pending is None or _median_dist(moved, self.pending) > cfg.min_move_px:
            self.pending = moved
            return {"status": "pending", **base}
        self.pending = None
        self.applied = moved
        res = _recalibrate(img, court, camera, moved, snap, cfg)
        if res is None:
            return {"status": "big", **base}
        return {"status": "moved", **base, **res}


def _recalibrate(img, court, camera, new_pts, snap, cfg) -> dict | None:
    how = "image motion"
    if snap:
        from .autocal import refine_from

        try:
            res = refine_from(img, court, new_pts)
        except Exception:  # pragma: no cover
            res = None
        if res is not None and res.ok and (res.debug or {}).get("fit_px", 99) <= cfg.snap_max_fit_px:
            if _median_dist(res.points, new_pts) <= cfg.snap_max_change_px:
                new_pts = {k: [float(a), float(b)] for k, (a, b) in res.points.items()}
                how = "image motion + line snap"
    kp = court.keypoints()
    names = [k for k in new_pts if k in kp]
    try:
        cam = calibrate_from_points(np.array([kp[k] for k in names], float), np.array([new_pts[k] for k in names], float),
                                    tuple(camera.image_size), camera_id=camera.camera_id, estimate_focal=len(names) >= 6)
    except CalibrationError:
        return None
    return {"points": {k: new_pts[k] for k in names}, "camera": cam, "how": how}
