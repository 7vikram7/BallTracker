"""Keeping calibrations good during a session: auto line snap, readiness, coverage.

Field test 3 (2026-11-21):

* A camera calibrated from rough clicks (RMS 6.9 px, one point 18 px off) disagreed with the
  others by 50-100 cm. The court-line snap the dashboard offered (median move 11 px, lines fit
  to 0.6 px) would have cut that to 17 cm on the near half, but nobody pressed Review. Now a
  snap that fits the painted lines well is applied automatically (``auto_snap``).
* A calibration that is still rough (RMS above ``MAX_RMS_PX``) is not used for calls
  (``calibration_ready``): its bounces are logged, not judged, and the dashboard says why.
* The right sideline was seen outside the line by only one camera (34% of the strip 1 m out
  seen by two), so every OUT there rested on one far camera. ``coverage`` measures this from
  the calibrations, for the dashboard's coverage map and warnings.
"""

from __future__ import annotations

import numpy as np

from ..geometry.camera import Camera, CalibrationError, calibrate_from_points
from ..geometry.court import CourtSpec

MAX_RMS_PX = 3.0          # rougher calibrations are not used for calls
SNAP_MAX_FIT_PX = 1.0     # auto-apply a line snap only if the painted lines fit this well ...
SNAP_MIN_LINES = 4        # ... from at least this many lines ...
SNAP_MAX_MOVE_PX = 30.0   # ... and it moves the points by at most this much (median; more: wrong lines?)


def calibration_ready(camera: Camera | None, max_rms_px: float = MAX_RMS_PX) -> bool:
    return camera is not None and float(camera.reprojection_rms_px or 0.0) <= max_rms_px


def auto_snap(img: np.ndarray, court: CourtSpec, camera: Camera) -> dict | None:
    """Snap the calibration to the painted lines; return the improved calibration if the snap is
    convincing: {"camera", "points", "moved_px", "fit_px", "lines"}, else None."""
    from ..geometry.crosscal import resnap_proposal

    try:
        prop = resnap_proposal(img, court, camera, min_move_px=1.0)
    except Exception:  # pragma: no cover - a snap failure never breaks calibration
        return None
    if not prop:
        return None
    fit, lines, moved = prop.get("fit_px"), prop.get("lines") or 0, prop.get("moved_px") or 0.0
    if fit is None or fit > SNAP_MAX_FIT_PX or lines < SNAP_MIN_LINES or moved > SNAP_MAX_MOVE_PX:
        return None
    kp = court.keypoints()
    names = [k for k in prop["points"] if k in kp]
    if len(names) < 6:
        return None
    try:
        cam = calibrate_from_points(np.array([kp[k] for k in names], float),
                                    np.array([prop["points"][k] for k in names], float),
                                    tuple(camera.image_size), camera_id=camera.camera_id, estimate_focal=True)
    except CalibrationError:
        return None
    if cam.reprojection_rms_px > max(1.5, camera.reprojection_rms_px):
        return None
    return {"camera": cam, "points": {k: prop["points"][k] for k in names}, "moved_px": moved,
            "fit_px": fit, "lines": lines}


def _visible(camera: Camera, court: CourtSpec, x: float, y: float) -> bool:
    P = np.array([[x, y, court.ball_radius]])
    if camera.depth(P)[0] <= 0.2:
        return False
    u, v = camera.project(P)[0]
    w, h = camera.image_size
    return 0.03 * w <= u <= 0.97 * w and 0.03 * h <= v <= 0.97 * h


def coverage(cameras: dict[str, Camera], court: CourtSpec, outside_m: float | None = None,
             cell_m: float | None = None) -> dict:
    """How many calibrated cameras see each boundary line, and the strip ``outside_m`` beyond it.

    -> {"lines": {line: {"in2": fraction seen by >= 2 cameras, "out2": same 1 m outside}},
        "grid": {"x0", "y0", "cell", "nx", "ny", "counts": [[...]]}, "warnings": [...]}"""
    s = float(getattr(court, "scale", 1.0) or 1.0)
    outside_m = 1.0 * s if outside_m is None else outside_m
    cell_m = 0.5 * s if cell_m is None else cell_m
    cams = [c for c in cameras.values() if c is not None]
    hw, hl, k = court.half_w, court.half_l, court.kitchen_depth

    def n_seeing(x: float, y: float) -> int:
        return int(sum(bool(_visible(c, court, x, y)) for c in cams))  # plain int: goes out as JSON

    xs, ys = np.linspace(-hw, hw, 13), np.linspace(-hl, hl, 25)
    lines = {
        "baseline_A": ([(x, -hl) for x in xs], (0.0, -1.0)), "baseline_B": ([(x, hl) for x in xs], (0.0, 1.0)),
        "sideline_left": ([(-hw, y) for y in ys], (-1.0, 0.0)), "sideline_right": ([(hw, y) for y in ys], (1.0, 0.0)),
        "kitchen_A": ([(x, -k) for x in xs], None), "kitchen_B": ([(x, k) for x in xs], None),
        "centreline": ([(0.0, y) for y in np.linspace(-hl, hl, 25) if abs(y) >= k], None),
    }
    out: dict = {"lines": {}, "warnings": []}
    for name, (pts, nrm) in lines.items():
        in2 = float(np.mean([n_seeing(x, y) >= 2 for x, y in pts]))
        rec = {"in2": round(in2, 2)}
        if nrm is not None:
            out2 = float(np.mean([n_seeing(x + nrm[0] * outside_m, y + nrm[1] * outside_m) >= 2 for x, y in pts]))
            rec["out2"] = round(out2, 2)
        out["lines"][name] = rec
    if len(cams) >= 2:
        for name, rec in out["lines"].items():
            if rec.get("out2", 1.0) < 0.6:
                out["warnings"].append(
                    f"{name.replace('_', ' ')}: only {round(100 * rec['out2'])}% of the strip "
                    f"{outside_m:g} m outside is seen by two cameras; turn a camera to include it")
            elif rec["in2"] < 0.8:
                out["warnings"].append(f"{name.replace('_', ' ')}: only {round(100 * rec['in2'])}% seen by two cameras")
    m = 1.5 * s
    nx, ny = int(np.ceil((2 * hw + 2 * m) / cell_m)), int(np.ceil((2 * hl + 2 * m) / cell_m))
    x0, y0 = -hw - m, -hl - m
    counts = [[n_seeing(x0 + (i + 0.5) * cell_m, y0 + (j + 0.5) * cell_m) for i in range(nx)] for j in range(ny)]
    out["grid"] = {"x0": float(x0), "y0": float(y0), "cell": float(cell_m), "nx": nx, "ny": ny, "counts": counts}
    return out
