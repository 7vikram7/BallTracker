"""Find the clicks that spoil a calibration.

Field test 2: two cameras calibrated at ~9.4 px RMS because a few clicked points did
not match the court model (net "tops" clicked on the portable net's posts, which stand
outside the sidelines and higher than the net; one corner mis-clicked). Without them
the same clicks gave 2.7 px. This module finds such points automatically: a point
whose removal makes the rest fit much better is reported as suspect, so the dashboard
can say "re-click A_left_corner" instead of just "RMS 9.5 px".
"""

from __future__ import annotations

import numpy as np

from .camera import CalibrationError, calibrate_from_points

# Points defined in the air above the sidelines: easy to click wrongly on a portable net
# (its posts stand outside the court and higher). Not offered for clicking by default.
NET_TOP_POINTS = ("net_left_top", "net_right_top", "net_centre_top")


def _rms(cam, obj, img) -> float:
    return float(np.sqrt(np.mean(np.linalg.norm(cam.project(obj) - img, axis=1) ** 2)))


def suspect_points(names: list[str], obj: np.ndarray, img: np.ndarray, size: tuple[int, int],
                   min_err_px: float = 4.0, min_gain: float = 0.25, max_suspects: int = 3) -> list[dict]:
    """Greedy leave-one-out: repeatedly take out the point whose removal lowers the RMS of the
    others the most, while that lowers it by more than ``min_gain`` and the point is off by
    more than ``min_err_px``. Returns the removed points (worst first)."""
    keep = list(range(len(names)))
    out: list[dict] = []
    while len(keep) >= 7 and len(out) < max_suspects:
        cam = calibrate_from_points(obj[keep], img[keep], size, estimate_focal=True)
        rms_now = _rms(cam, obj[keep], img[keep])
        errs = np.linalg.norm(cam.project(obj[keep]) - img[keep], axis=1)
        best = None
        for j in np.argsort(-errs)[:4]:
            if errs[j] < min_err_px:
                break
            rest = [k for i, k in enumerate(keep) if i != j]
            try:
                c2 = calibrate_from_points(obj[rest], img[rest], size, estimate_focal=True)
            except CalibrationError:
                continue
            r2 = _rms(c2, obj[rest], img[rest])
            if r2 < (1 - min_gain) * rms_now and (best is None or r2 < best[1]):
                best = (j, r2, c2)
        if best is None:
            break
        j, r2, c2 = best
        i = keep[j]
        pred = c2.project(obj[i:i + 1])[0]
        out.append({"name": names[i], "err_px": round(float(errs[j]), 1), "rms_without_px": round(r2, 2),
                    "expected_px": [round(float(pred[0]), 1), round(float(pred[1]), 1)]})
        keep.pop(j)
    return out
