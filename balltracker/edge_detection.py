"""Phone-side ball detector: the reference implementation.

The native app (mobile/modules/ball-camera/cpp/ballcore) runs a C++ port of
exactly this algorithm on the phone. This file is the specification: every
step uses integer maths or float32 operations in a fixed order, so the C++
port can reproduce it and ``tests/test_ballcore_parity.py`` checks that it does.

It is the same idea as ``MotionColorBallDetector`` (moving AND ball-coloured
pixels -> blobs -> refined centroid), with two changes so it is cheap enough
for 240 fps on a phone and exactly reproducible:

* **Background model**: one running Gaussian per pixel (mean colour + one
  variance, the single-component case of OpenCV's MOG2) instead of MOG2's
  mixture. It is updated at ``bg_update_hz`` (default 60 Hz) whatever the frame
  rate; the foreground test runs on every frame.
* **Colour gate in integers**: the OpenCV-style HSV range test is evaluated
  with integer cross-multiplication, without computing H and S, so there's no
  rounding to reproduce.

Steps per frame (image W x H, BGR or BGRA, uint8):

1. Bin k x k (default k = 2): ``small = (sum of block + k*k//2) // (k*k)``.
2. Flicker compensation: per-channel gain = slow average mean / this frame's
   mean, applied with a float32 lookup table (as the Mac detector does).
3. Colour gate on ``small`` (integer HSV test, see ``gate``).
4. Foreground: ``d2 = (dB*dB + dG*dG) + dR*dR`` with ``d = small - mean``;
   foreground where ``d2 > var_threshold * var``. Then, on update frames,
   ``mean += a*(small - mean)``, ``var += a*(d2 - var)`` clipped to
   [var_min, var_max], with ``a = 1/min(updates, history)``.
5. mask = gate AND foreground (AND roi); dilate with a 3x3 cross.
6. 8-connected blobs; keep by area, border distance, elongation.
7. Refine each blob at full resolution: centroid of ball-coloured pixels in
   its padded bounding box, radius from their count.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import cv2
import numpy as np

from .detection import Candidate

ALGO = "edge_color_motion"
ALGO_VERSION = "1.0.0"


@dataclass
class EdgeDetectorConfig:
    bin: int = 2
    hsv_low: tuple[int, int, int] = (25, 100, 90)  # OpenCV units (H 0-180)
    hsv_high: tuple[int, int, int] = (55, 255, 255)
    var_threshold: float = 24.0
    var_init: float = 15.0
    var_min: float = 4.0
    var_max: float = 75.0
    bg_history_s: float = 2.0
    bg_update_hz: float = 60.0
    fps: float = 60.0  # nominal capture rate (sets how often the background updates)
    min_radius_px: float = 1.5
    max_radius_px: float = 80.0
    max_elongation: float = 6.0
    max_candidates: int = 12
    flicker_compensation: bool = True
    flicker_alpha: float = 0.02
    roi_mask: np.ndarray | None = field(default=None, repr=False)  # full-res uint8, 255 = search

    @property
    def update_every(self) -> int:
        return max(1, int(round(self.fps / self.bg_update_hz)))

    @property
    def history_updates(self) -> int:
        return max(1, int(round(self.bg_history_s * self.bg_update_hz)))

    def to_dict(self) -> dict:
        """Wire/native form (what the phone app receives in a ``config`` message)."""
        return {
            "bin": self.bin, "hsv_low": list(self.hsv_low), "hsv_high": list(self.hsv_high),
            "var_threshold": self.var_threshold, "var_init": self.var_init, "var_min": self.var_min,
            "var_max": self.var_max, "bg_history_s": self.bg_history_s, "bg_update_hz": self.bg_update_hz,
            "fps": self.fps, "min_radius_px": self.min_radius_px, "max_radius_px": self.max_radius_px,
            "max_elongation": self.max_elongation, "max_candidates": self.max_candidates,
            "flicker_compensation": self.flicker_compensation, "flicker_alpha": self.flicker_alpha,
        }


def gate(img: np.ndarray, low, high) -> np.ndarray:
    """OpenCV-convention HSV range test in integers. img: (..., >=3) BGR uint8 -> bool.

    V = max(B,G,R); S in [Slo,Shi] <=> Slo*V <= 255*(V-min) <= Shi*V;
    hue (degrees) = h6/diff with h6 as below; H (OpenCV) = hue/2.
    """
    b = img[..., 0].astype(np.int32)
    g = img[..., 1].astype(np.int32)
    r = img[..., 2].astype(np.int32)
    v = np.maximum(np.maximum(b, g), r)
    mn = np.minimum(np.minimum(b, g), r)
    diff = v - mn
    hlo, slo, vlo = (int(x) for x in low)
    hhi, shi, vhi = (int(x) for x in high)
    ok_v = (v >= vlo) & (v <= vhi)
    s255 = 255 * diff
    ok_s = np.where(v == 0, slo == 0, (s255 >= slo * v) & (s255 <= shi * v))
    h6 = np.where(v == r, 60 * (g - b), np.where(v == g, 120 * diff + 60 * (b - r), 240 * diff + 60 * (r - g)))
    h6 = np.where(h6 < 0, h6 + 360 * diff, h6)
    ok_h = np.where(diff == 0, hlo == 0, (h6 >= 2 * hlo * diff) & (h6 <= 2 * hhi * diff))
    return ok_v & ok_s & ok_h


def bin_image(img: np.ndarray, k: int) -> np.ndarray:
    """k x k block average with round-half-up, on the first 3 channels. Crops to multiples of k."""
    h, w = img.shape[0] // k * k, img.shape[1] // k * k
    if k == 1:
        return np.ascontiguousarray(img[:h, :w, :3])
    blk = img[:h, :w, :3].reshape(h // k, k, w // k, k, 3).astype(np.uint32).sum(axis=(1, 3))
    return ((blk + (k * k) // 2) // (k * k)).astype(np.uint8)


def dilate_cross(mask: np.ndarray) -> np.ndarray:
    """3x3 cross dilation; pixels outside the image don't contribute."""
    out = mask.copy()
    out[1:, :] |= mask[:-1, :]
    out[:-1, :] |= mask[1:, :]
    out[:, 1:] |= mask[:, :-1]
    out[:, :-1] |= mask[:, 1:]
    return out


class EdgeBallDetector:
    name = ALGO
    version = ALGO_VERSION

    def __init__(self, cfg: EdgeDetectorConfig | None = None):
        self.cfg = cfg or EdgeDetectorConfig()
        self.reset()

    def reset(self) -> None:
        self._mu: np.ndarray | None = None
        self._var: np.ndarray | None = None
        self._updates = 0
        self._frame = 0
        self._ref_mean: np.ndarray | None = None
        self._roi_small: np.ndarray | None = None

    def params(self) -> dict:
        return {"algorithm": ALGO, "version": ALGO_VERSION, **self.cfg.to_dict()}

    _ramp = np.arange(256, dtype=np.float32)

    def _deflicker(self, small: np.ndarray) -> np.ndarray:
        # Channel means in float64 (sums of integers: exact), gain cast to float32.
        m = small.reshape(-1, 3).sum(axis=0, dtype=np.float64) / (small.shape[0] * small.shape[1]) + 1e-3
        if self._ref_mean is None:
            self._ref_mean = m.copy()
        gain = self._ref_mean / m
        a = self.cfg.flicker_alpha
        self._ref_mean = (1 - a) * self._ref_mean + a * m
        if np.all(np.abs(gain - 1) < 0.01):
            return small
        g32 = gain.astype(np.float32)
        lut = np.minimum(self._ramp[:, None] * g32[None, :], np.float32(255)).astype(np.uint8)  # floor
        return np.stack([lut[small[..., c], c] for c in range(3)], axis=-1)

    def detect(self, image: np.ndarray) -> list[Candidate]:
        c = self.cfg
        k = c.bin
        H, W = image.shape[:2]
        small = bin_image(image, k)
        if c.flicker_compensation:
            small = self._deflicker(small)
        sh, sw = small.shape[:2]
        col = gate(small, c.hsv_low, c.hsv_high)
        x = small.astype(np.float32)
        if self._mu is None:
            self._mu = x.copy()
            self._var = np.full((sh, sw), np.float32(c.var_init), np.float32)
            fg = np.zeros((sh, sw), bool)
            d2 = np.zeros((sh, sw), np.float32)
        else:
            d = x - self._mu
            d2 = (d[..., 0] * d[..., 0] + d[..., 1] * d[..., 1]) + d[..., 2] * d[..., 2]
            fg = d2 > np.float32(c.var_threshold) * self._var
        if self._frame % c.update_every == 0:
            self._updates += 1
            a = np.float32(1.0 / min(self._updates, c.history_updates))
            if self._updates > 1:  # the first update is the initialisation above
                self._mu = self._mu + a * (x - self._mu)
                self._var = np.clip(self._var + a * (d2 - self._var), np.float32(c.var_min), np.float32(c.var_max))
        self._frame += 1

        mask = col & fg
        if c.roi_mask is not None:
            if self._roi_small is None:
                self._roi_small = c.roi_mask[: sh * k : k, : sw * k : k] > 0
            mask &= self._roi_small
        mask = dilate_cross(mask)
        if not mask.any():
            return []
        n, _, stats, cents = cv2.connectedComponentsWithStats(mask.astype(np.uint8), connectivity=8)
        min_area = max(1.0, np.pi * (c.min_radius_px / k) ** 2 * 0.3)
        max_area = np.pi * (c.max_radius_px / k) ** 2 * 3
        out: list[Candidate] = []
        pad = 3
        for i in range(1, n):
            bx, by, bw, bh, area = (int(v) for v in stats[i])
            if area < min_area or area > max_area:
                continue
            if bx <= 2 or by <= 2 or bx + bw >= sw - 2 or by + bh >= sh - 2:
                continue
            elong = max(bw, bh) / max(1, min(bw, bh))
            if elong > c.max_elongation:
                continue
            X0, Y0 = max(0, (bx - pad) * k), max(0, (by - pad) * k)
            X1, Y1 = min(W, (bx + bw + pad) * k), min(H, (by + bh + pad) * k)
            m = gate(image[Y0:Y1, X0:X1], c.hsv_low, c.hsv_high)
            cnt = int(m.sum())
            if cnt == 0:
                u = (float(cents[i][0]) + 0.5) * k - 0.5
                v = (float(cents[i][1]) + 0.5) * k - 0.5
                r = 1.0
            else:
                ys, xs = np.nonzero(m)
                u = float(int(xs.sum())) / cnt + X0
                v = float(int(ys.sum())) / cnt + Y0
                r = float(np.sqrt(cnt / np.pi))
            if not (c.min_radius_px * 0.5 <= r <= c.max_radius_px * 1.5):
                continue
            fill = area / max(1, bw * bh)
            score = float(min(max(0.5 * fill / 0.785 + 0.5 / elong, 0.0), 1.0))
            out.append(Candidate(u=u, v=v, radius_px=r, score=score, area_px=float(area * k * k), elongation=float(elong)))
        out.sort(key=lambda q: -q.score)
        return out[: c.max_candidates]
