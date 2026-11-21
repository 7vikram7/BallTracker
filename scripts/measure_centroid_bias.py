#!/usr/bin/env python3
"""How far is the phone detector's ball centre from the true centre, for small balls?

Review of defed68, TODO-12: field sessions showed far-half bounces 0.7-1.5 m off between cameras,
more than calibration explains; one suspect is a biased ball centre on a small, blurred far ball
(a sunlit top half, motion blur). The contact geometry itself is right (the contact pixel's ray
meets the plane z = ball radius, bounce.py).

This renders a ball moving across a textured background at sub-pixel positions, with a lit top
(the shaded lower half is darker and can fall outside the colour gate) and motion blur, runs the
phone's C++ detector (the code the apps run) and reports the centre error by apparent radius.
It converts the vertical error to metres along the court at the far baseline for a phone 2.4 m
high, 9.5 m behind the near baseline (the depth direction is where a pixel is worth most).

    .venv/bin/python scripts/measure_centroid_bias.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from balltracker.ballcore import NativeDetector  # noqa: E402
from balltracker.edge_detection import EdgeDetectorConfig  # noqa: E402
from balltracker.geometry.camera import Camera  # noqa: E402
from balltracker.geometry.court import CourtSpec  # noqa: E402

W, H, FPS, SS = 1920, 1080, 120, 8  # SS: supersampling for anti-aliased, sub-pixel rendering


def render(bg: np.ndarray, cx: float, cy: float, r: float, shade: float, blur_px: float) -> np.ndarray:
    """Ball centre (cx, cy), radius r (pixels), lit from above: the lower part darker by `shade`."""
    x0, y0 = int(cx - r - blur_px - 3), int(cy - r - 3)
    w, h = int(2 * r + 2 * blur_px + 7), int(2 * r + 7)
    big = cv2.resize(bg[y0:y0 + h, x0:x0 + w], (w * SS, h * SS), interpolation=cv2.INTER_NEAREST).astype(np.float32)
    # image coordinates of each supersample, OpenCV convention (pixel centres on whole numbers)
    yy, xx = np.mgrid[0:h * SS, 0:w * SS].astype(np.float32)
    xx = x0 + (xx + 0.5) / SS - 0.5
    yy = y0 + (yy + 0.5) / SS - 0.5
    acc = np.zeros_like(big)
    cov = np.zeros(big.shape[:2], np.float32)
    steps = max(1, int(blur_px * 2))
    for k in range(steps):  # motion blur: average of positions along the path (horizontal motion)
        dx = (k / max(steps - 1, 1) - 0.5) * blur_px if steps > 1 else 0.0
        bx, by = cx + dx, cy
        m = ((xx - bx) ** 2 + (yy - by) ** 2 <= r ** 2).astype(np.float32)
        lit = 1.0 - shade * np.clip((yy - by) / r * 0.5 + 0.5, 0, 1)  # 1 at the top, 1-shade at the bottom
        col = np.stack([40 * lit, 230 * lit, 220 * lit], -1)  # yellow-green (BGR)
        acc += col * m[..., None]
        cov += m
    cov /= steps
    acc /= steps
    out = big * (1 - cov[..., None]) + acc
    img = bg.copy()
    img[y0:y0 + h, x0:x0 + w] = cv2.resize(out, (w, h), interpolation=cv2.INTER_AREA).clip(0, 255).astype(np.uint8)
    return img


def measure(r: float, shade: float, blur_px: float, n: int = 120, seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    bg = cv2.add(np.full((H, W, 3), (70, 110, 60), np.uint8), rng.integers(0, 30, (H, W, 3), dtype=np.uint8))
    det = NativeDetector(EdgeDetectorConfig(fps=FPS))
    errs = []
    cx0, cy = 300.0 + rng.uniform(0, 1), 540.0 + rng.uniform(0, 1)
    for k in range(n):
        cx = cx0 + 9.37 * k  # moving: the background model needs motion; sub-pixel phases vary
        cyk = cy + 0.31 * k
        img = render(bg, cx, cyk, r, shade, blur_px)
        cands = det.detect(img)
        if k < 20 or not cands:
            continue
        c = min(cands, key=lambda c: (c.u - cx) ** 2 + (c.v - cyk) ** 2)
        if abs(c.u - cx) < 3 * r and abs(c.v - cyk) < 3 * r:
            errs.append((c.u - cx, c.v - cyk, c.radius_px - r))
    return np.array(errs)


def metres_per_px_at_far_baseline() -> float:
    court = CourtSpec.pickleball()
    cam = Camera.look_at(position=[-3.6, -court.half_l - 9.5, 2.4], target=[0.0, 0.0, 0.0], image_size=(W, H), hfov_deg=69)
    p = np.array([[0.0, court.half_l, court.ball_radius]])
    u, v = cam.project(p)[0]
    a = cam.intersect_plane_z(np.array([[u, v]]), court.ball_radius)[0]
    b = cam.intersect_plane_z(np.array([[u, v + 1.0]]), court.ball_radius)[0]
    return float(np.hypot(*(b[:2] - a[:2])))


def main() -> None:
    mpp = metres_per_px_at_far_baseline()
    print(f"one pixel down at the far baseline (phone 2.4 m high, 9.5 m behind the near baseline): {100 * mpp:.1f} cm")
    print(f"{'radius px':>9} {'shade':>5} {'blur px':>7} {'n':>4} {'du px':>7} {'dv px':>7} {'sd v':>6} {'dr px':>6} {'dv in cm':>9}")
    for r in (2.0, 3.0, 4.0, 6.0):
        for shade, blur in ((0.0, 0.0), (0.5, 0.0), (0.5, 6.0)):
            e = measure(r, shade, blur)
            if len(e) == 0:
                print(f"{r:9.1f} {shade:5.1f} {blur:7.1f}    0  (not detected)")
                continue
            du, dv, dr = np.median(e, axis=0)
            print(f"{r:9.1f} {shade:5.1f} {blur:7.1f} {len(e):4d} {du:7.2f} {dv:7.2f} {np.std(e[:, 1]):6.2f} {dr:6.2f} {100 * dv * mpp:9.1f}")


if __name__ == "__main__":
    main()
