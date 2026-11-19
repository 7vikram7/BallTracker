"""Pinhole camera model, calibration from court keypoints, ray casting.

A camera is described by intrinsics K (focal length, principal point), lens
distortion, and extrinsics (R, t) mapping court coordinates to camera
coordinates:  X_cam = R @ X_court + t.

Why a full camera model rather than just a ground-plane homography: at the
moment of a bounce the ball's CENTRE is one ball-radius above the ground, not
on it. Mapping the ball centre through a ground homography lands the point
beyond the true contact point along the viewing ray (by r / tan(elevation), e.g.
~10 cm for a camera at 20 degrees elevation). With a full camera we intersect the
viewing ray with the plane z = r and drop straight down to the contact point.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np


@dataclass
class Camera:
    K: np.ndarray  # 3x3
    dist: np.ndarray  # (5,) OpenCV distortion coeffs
    R: np.ndarray  # 3x3 court->camera rotation
    t: np.ndarray  # (3,) court->camera translation
    image_size: tuple[int, int]  # (width, height)
    camera_id: str = "cam0"
    reprojection_rms_px: float | None = None

    # ------------------------------------------------------------ factories
    @staticmethod
    def intrinsics_from_fov(image_size: tuple[int, int], hfov_deg: float) -> np.ndarray:
        w, h = image_size
        f = (w / 2) / math.tan(math.radians(hfov_deg) / 2)
        return np.array([[f, 0, w / 2], [0, f, h / 2], [0, 0, 1]], dtype=float)

    @classmethod
    def look_at(
        cls,
        position: np.ndarray,
        target: np.ndarray,
        image_size: tuple[int, int],
        hfov_deg: float = 65.0,
        camera_id: str = "cam0",
    ) -> "Camera":
        """Camera at ``position`` looking at ``target`` (court coords), z-up world."""
        position = np.asarray(position, float)
        target = np.asarray(target, float)
        fwd = target - position
        fwd /= np.linalg.norm(fwd)
        up_world = np.array([0.0, 0.0, 1.0])
        right = np.cross(fwd, up_world)
        if np.linalg.norm(right) < 1e-9:
            right = np.array([1.0, 0.0, 0.0])
        right /= np.linalg.norm(right)
        down = np.cross(fwd, right)
        # OpenCV camera axes: x right, y down, z forward.
        R = np.stack([right, down, fwd])
        t = -R @ position
        K = cls.intrinsics_from_fov(image_size, hfov_deg)
        return cls(K=K, dist=np.zeros(5), R=R, t=t, image_size=image_size, camera_id=camera_id)

    # ------------------------------------------------------------ properties
    @property
    def position(self) -> np.ndarray:
        """Camera centre in court coordinates."""
        return -self.R.T @ self.t

    @property
    def focal_px(self) -> float:
        return float((self.K[0, 0] + self.K[1, 1]) / 2)

    # ------------------------------------------------------------ projection
    def project(self, pts: np.ndarray) -> np.ndarray:
        """Project Nx3 court points to Nx2 pixel coordinates (with distortion)."""
        pts = np.asarray(pts, float).reshape(-1, 3)
        rvec, _ = cv2.Rodrigues(self.R)
        img, _ = cv2.projectPoints(pts, rvec, self.t.astype(float), self.K, self.dist)
        return img.reshape(-1, 2)

    def depth(self, pts: np.ndarray) -> np.ndarray:
        pts = np.asarray(pts, float).reshape(-1, 3)
        return (pts @ self.R.T + self.t)[:, 2]

    def undistort_points(self, px: np.ndarray) -> np.ndarray:
        """Pixel -> normalised camera coordinates (x/z, y/z)."""
        px = np.asarray(px, float).reshape(-1, 1, 2)
        n = cv2.undistortPoints(px, self.K, self.dist)
        return n.reshape(-1, 2)

    def rays(self, px: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Viewing rays (origin, unit directions) in court coordinates."""
        n = self.undistort_points(px)
        d_cam = np.column_stack([n, np.ones(len(n))])
        d = d_cam @ self.R  # R.T @ d for each row
        d /= np.linalg.norm(d, axis=1, keepdims=True)
        return self.position, d

    def intersect_plane_z(self, px: np.ndarray, z: float = 0.0) -> np.ndarray:
        """Intersect viewing rays through pixels with the horizontal plane Z = z.

        Returns Nx3 points. Rays parallel to / pointing away from the plane give NaN.
        """
        o, d = self.rays(px)
        with np.errstate(divide="ignore", invalid="ignore"):
            s = (z - o[2]) / d[:, 2]
        s = np.where(s > 0, s, np.nan)
        return o[None, :] + s[:, None] * d

    def ground_homography(self) -> np.ndarray:
        """Homography mapping ground-plane (X, Y) to undistorted pixels."""
        H = self.K @ np.column_stack([self.R[:, 0], self.R[:, 1], self.t])
        return H / H[2, 2]

    # ------------------------------------------------------------ persistence
    def to_dict(self) -> dict:
        return {
            "schema": "balltracker.camera/v1",
            "camera_id": self.camera_id,
            "image_size": list(self.image_size),
            "K": self.K.tolist(),
            "dist": self.dist.tolist(),
            "R": self.R.tolist(),
            "t": self.t.tolist(),
            "reprojection_rms_px": self.reprojection_rms_px,
            "position_court_m": self.position.tolist(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Camera":
        return cls(
            K=np.array(d["K"], float),
            dist=np.array(d["dist"], float),
            R=np.array(d["R"], float),
            t=np.array(d["t"], float),
            image_size=tuple(d["image_size"]),
            camera_id=d.get("camera_id", "cam0"),
            reprojection_rms_px=d.get("reprojection_rms_px"),
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "Camera":
        return cls.from_dict(json.loads(Path(path).read_text()))


class CalibrationError(RuntimeError):
    pass


def calibrate_from_points(
    object_pts: np.ndarray,
    image_pts: np.ndarray,
    image_size: tuple[int, int],
    *,
    hfov_guess_deg: float = 65.0,
    estimate_focal: bool = True,
    camera_id: str = "cam0",
) -> Camera:
    """Calibrate a camera from >= 4 court keypoints and their pixel positions.

    * Always solves the pose (R, t) with PnP.
    * If ``estimate_focal`` and >= 6 points are given, also refines a single focal
      length (principal point fixed at the image centre, no distortion), which
      removes the need to know the phone's field of view. Points with z != 0
      (net-post tops) make the focal estimate much better conditioned.

    For best accuracy, calibrate intrinsics separately with a ChArUco board and
    pass them in; this function is the "click the court corners" path.
    """
    object_pts = np.asarray(object_pts, float).reshape(-1, 3)
    image_pts = np.asarray(image_pts, float).reshape(-1, 2)
    if len(object_pts) < 4:
        raise CalibrationError("Need at least 4 point correspondences")
    if len(object_pts) != len(image_pts):
        raise CalibrationError("object/image point count mismatch")

    K0 = Camera.intrinsics_from_fov(image_size, hfov_guess_deg)
    dist = np.zeros(5)

    def solve_pose(K: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
        ok, rvec, tvec = cv2.solvePnP(object_pts, image_pts, K, dist, flags=cv2.SOLVEPNP_ITERATIVE)
        if not ok:
            raise CalibrationError("solvePnP failed")
        rvec, tvec = cv2.solvePnPRefineLM(object_pts, image_pts, K, dist, rvec, tvec)
        proj, _ = cv2.projectPoints(object_pts, rvec, tvec, K, dist)
        rms = float(np.sqrt(np.mean(np.sum((proj.reshape(-1, 2) - image_pts) ** 2, axis=1))))
        return rvec, tvec, rms

    K = K0
    if estimate_focal and len(object_pts) >= 6:
        # 1-D search over focal length: robust and needs no special OpenCV flags.
        w, h = image_size
        best = None
        for hfov in np.linspace(25, 120, 96):
            Kc = Camera.intrinsics_from_fov(image_size, float(hfov))
            try:
                _, _, rms = solve_pose(Kc)
            except (CalibrationError, cv2.error):
                continue
            if best is None or rms < best[0]:
                best = (rms, float(hfov))
        if best is not None:
            # Golden-section refine around the best grid value.
            lo, hi = best[1] - 1.0, best[1] + 1.0

            def cost(hf: float) -> float:
                try:
                    return solve_pose(Camera.intrinsics_from_fov(image_size, hf))[2]
                except (CalibrationError, cv2.error):
                    return float("inf")

            g = (math.sqrt(5) - 1) / 2
            a, b = lo, hi
            c, d = b - g * (b - a), a + g * (b - a)
            for _ in range(40):
                if cost(c) < cost(d):
                    b = d
                else:
                    a = c
                c, d = b - g * (b - a), a + g * (b - a)
            K = Camera.intrinsics_from_fov(image_size, (a + b) / 2)

    rvec, tvec, rms = solve_pose(K)
    R, _ = cv2.Rodrigues(rvec)
    cam = Camera(K=K, dist=dist, R=R, t=tvec.reshape(3), image_size=image_size, camera_id=camera_id)
    cam.reprojection_rms_px = rms
    if cam.position[2] <= 0:
        raise CalibrationError("Calibrated camera is below the court plane; check point labels")
    return cam
