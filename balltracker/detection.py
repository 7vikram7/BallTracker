"""Ball candidate detection.

``BallDetector`` is the interface. The implementation here,
``MotionColorBallDetector``, is a deliberately simple *classical baseline*:

    background subtraction (moving pixels)
      AND optional colour gate (e.g. yellow/green ball)
      -> connected blobs filtered by size and shape
      -> sub-pixel centroid at full resolution

It needs no training data and is easy to reason about, which makes it a useful
first step and a yardstick. It is NOT expected to be robust in real play
(players, shadows, other balls, clutter). The intended replacement is a
multi-frame heatmap network (TrackNetV3 / WASB family) fine-tuned on our own
labelled footage; it will implement the same interface.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

import cv2
import numpy as np


@dataclass(frozen=True)
class Candidate:
    u: float
    v: float
    radius_px: float
    score: float  # 0..1 heuristic quality
    area_px: float
    elongation: float


class BallDetector(Protocol):
    name: str
    version: str

    def detect(self, image_bgr: np.ndarray) -> list[Candidate]: ...


@dataclass
class DetectorConfig:
    downscale: float = 0.5  # process at this scale for speed, refine at full res
    history: int = 120  # background model history (frames)
    var_threshold: float = 24.0
    use_color: bool = True
    # HSV gate in OpenCV units (H 0-180). Default: optic-yellow / neon-green
    # balls (pickleball ~H 28-32, tennis ball ~H 36-43, both S > 150). H >= 25
    # and S >= 100 keep out yellow chalk/turmeric (H ~20-24) and most foliage
    # (S ~80-140). Measured on real footage, 2026-11.
    hsv_low: tuple[int, int, int] = (25, 100, 90)
    hsv_high: tuple[int, int, int] = (55, 255, 255)
    min_radius_px: float = 1.5  # full-resolution pixels
    max_radius_px: float = 80.0  # a ball 1-2 m from the camera can be ~60 px
    max_elongation: float = 6.0  # motion blur makes streaks
    max_candidates: int = 12
    # Mains-powered lights pulse at 100/120 Hz; at 120-240 fps that shows up as
    # whole-frame brightness/colour flicker that the background model sees as
    # motion everywhere. Rescale each frame's channel means to a slow average.
    flicker_compensation: bool = True
    flicker_alpha: float = 0.02  # EMA rate of the reference brightness
    roi_mask: np.ndarray | None = field(default=None, repr=False)  # uint8 HxW full-res, 255=search


class MotionColorBallDetector:
    name = "motion_color_baseline"
    version = "0.1.0"

    def __init__(self, cfg: DetectorConfig | None = None):
        self.cfg = cfg or DetectorConfig()
        self._bg = cv2.createBackgroundSubtractorMOG2(
            history=self.cfg.history, varThreshold=self.cfg.var_threshold, detectShadows=False
        )
        self._roi_small: np.ndarray | None = None
        self._kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self._ref_mean: np.ndarray | None = None

    def params(self) -> dict:
        c = self.cfg
        return {
            "downscale": c.downscale,
            "history": c.history,
            "var_threshold": c.var_threshold,
            "use_color": c.use_color,
            "hsv_low": list(c.hsv_low),
            "hsv_high": list(c.hsv_high),
            "min_radius_px": c.min_radius_px,
            "max_radius_px": c.max_radius_px,
            "flicker_compensation": c.flicker_compensation,
        }

    def detect(self, image_bgr: np.ndarray) -> list[Candidate]:
        c = self.cfg
        h, w = image_bgr.shape[:2]
        s = c.downscale
        small = cv2.resize(image_bgr, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA) if s != 1 else image_bgr
        if c.flicker_compensation:
            small = self._deflicker(small)
        fg = self._bg.apply(small)
        _, fg = cv2.threshold(fg, 127, 255, cv2.THRESH_BINARY)
        if c.use_color:
            hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
            col = cv2.inRange(hsv, np.array(c.hsv_low), np.array(c.hsv_high))
            mask = cv2.bitwise_and(fg, col)
        else:
            mask = fg
        if c.roi_mask is not None:
            if self._roi_small is None:
                self._roi_small = cv2.resize(c.roi_mask, (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST)
            mask = cv2.bitwise_and(mask, self._roi_small)
        mask = cv2.dilate(mask, self._kernel)

        n, labels, stats, cents = cv2.connectedComponentsWithStats(mask, connectivity=8)
        cands: list[Candidate] = []
        min_area = max(1.0, np.pi * (c.min_radius_px * s) ** 2 * 0.3)
        max_area = np.pi * (c.max_radius_px * s) ** 2 * 3
        for i in range(1, n):
            x, y, bw, bh, area = stats[i]
            if area < min_area or area > max_area:
                continue
            # A ball cut off by the image border has a biased centroid (looks like a kink).
            border = 2
            if x <= border or y <= border or x + bw >= small.shape[1] - border or y + bh >= small.shape[0] - border:
                continue
            elong = max(bw, bh) / max(1.0, min(bw, bh))
            if elong > c.max_elongation:
                continue
            # Refine centroid at full resolution inside the blob's bounding box.
            pad = 3
            X0 = max(0, int((x - pad) / s))
            Y0 = max(0, int((y - pad) / s))
            X1 = min(w, int((x + bw + pad) / s) + 1)
            Y1 = min(h, int((y + bh + pad) / s) + 1)
            u, v, r = self._refine(image_bgr[Y0:Y1, X0:X1], X0, Y0, cents[i] / s)
            if not (c.min_radius_px * 0.5 <= r <= c.max_radius_px * 1.5):
                continue
            fill = area / max(1.0, bw * bh)
            score = float(np.clip(0.5 * fill / 0.785 + 0.5 / elong, 0, 1))
            cands.append(Candidate(u=u, v=v, radius_px=r, score=score, area_px=float(area) / (s * s), elongation=float(elong)))
        cands.sort(key=lambda k: -k.score)
        return cands[: c.max_candidates]

    _ramp = np.arange(256, dtype=np.float32)

    def _deflicker(self, small: np.ndarray) -> np.ndarray:
        m = np.array(cv2.mean(small)[:3]) + 1e-3
        if self._ref_mean is None:
            self._ref_mean = m.copy()
        gain = self._ref_mean / m
        self._ref_mean = (1 - self.cfg.flicker_alpha) * self._ref_mean + self.cfg.flicker_alpha * m
        if np.all(np.abs(gain - 1) < 0.01):
            return small
        # Per-channel gain via a lookup table (much faster than float maths on the image).
        lut = np.clip(self._ramp[:, None] * gain[None, :].astype(np.float32), 0, 255).astype(np.uint8)
        return cv2.LUT(small, lut.reshape(256, 1, 3))

    def _refine(self, patch: np.ndarray, x0: int, y0: int, fallback: np.ndarray) -> tuple[float, float, float]:
        c = self.cfg
        if patch.size == 0:
            return float(fallback[0]), float(fallback[1]), 1.0
        if c.use_color:
            hsv = cv2.cvtColor(patch, cv2.COLOR_BGR2HSV)
            m = cv2.inRange(hsv, np.array(c.hsv_low), np.array(c.hsv_high)).astype(np.float32)
        else:
            g = cv2.cvtColor(patch, cv2.COLOR_BGR2GRAY).astype(np.float32)
            m = np.clip(g - np.median(g), 0, None)
        tot = m.sum()
        if tot <= 0:
            return float(fallback[0]), float(fallback[1]), 1.0
        ys, xs = np.mgrid[0 : m.shape[0], 0 : m.shape[1]]
        u = float((m * xs).sum() / tot) + x0
        v = float((m * ys).sum() / tot) + y0
        area = float((m > 0).sum())
        r = float(np.sqrt(area / np.pi))
        return u, v, r
