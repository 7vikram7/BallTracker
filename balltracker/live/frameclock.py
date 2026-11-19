"""Snap jittery frame timestamps back onto the camera's fixed frame grid.

A camera captures on a regular beat (e.g. every 16.67 ms), but browsers report frame
times with a few ms of jitter (seen: ±3–4 ms in Safari and in headless Chrome). The
picture content still advances exactly one frame per frame, so a jittered timestamp means
the ball's position and time disagree: about 3 cm at 10 m/s per 3 ms. Bounce fits
then fail or shift.

``FrameClock.fit(t)`` returns the timestamp on the regular grid:

* each frame gets an integer frame number: the previous one plus the whole number of
  periods since it (more than one when frames were dropped);
* a straight line t = a + T*k is fitted to the last few seconds of (frame number,
  observed time): the jitter averages out, and slow drift is followed;
* an observation more than 0.45 T off the line is passed through unchanged and not learned
  from (a glitch); two in a row (frame-rate change, pause) start a new segment there.

Accurate timestamps (app cameras, synthetic tests) come through unchanged (to ~1 us).
"""

from __future__ import annotations

from collections import deque

import numpy as np


class FrameClock:
    def __init__(self, window: int = 180, min_points: int = 12, max_offgrid: float = 0.45):
        self.window = window
        self.min_points = min_points
        self.max_offgrid = max_offgrid
        self.reanchors = 0
        self.reset()

    def reset(self) -> None:
        self._k: deque[int] = deque(maxlen=self.window)
        self._t: deque[float] = deque(maxlen=self.window)
        self._dts: deque[float] = deque(maxlen=30)
        self._fit: tuple[float, float] | None = None  # (a, T) of t = a + T*k
        self._offgrid = 0
        self.period: float | None = None

    def _rough_period(self) -> float | None:
        if len(self._dts) < 5:
            return None
        d = np.array(self._dts)
        m = float(np.median(d))
        d = d[d < 1.5 * m]
        return float(np.median(d)) if len(d) >= 3 else m

    def fit(self, t: float) -> float:
        if not self._t:
            self._k.append(0)
            self._t.append(t)
            return t
        if t <= self._t[-1]:
            return t
        self._dts.append(t - self._t[-1])
        if self._fit is not None:
            a, T = self._fit
            k = max(self._k[-1] + 1, int(round((t - a) / T)))
            pred = a + T * k
            if abs(t - pred) > self.max_offgrid * T:
                self._offgrid += 1
                if self._offgrid < 2:
                    self._dts.pop()  # a single glitch: don't learn from it
                    return t
                self.reanchors += 1
                self.reset()
                self._k.append(0)
                self._t.append(t)
                return t
            self._offgrid = 0
        else:
            T = self._rough_period()
            if T is None:
                k = self._k[-1] + 1
            else:
                k = self._k[-1] + max(1, int(round((t - self._t[-1]) / T)))
        self._k.append(k)
        self._t.append(t)
        if len(self._t) >= self.min_points:
            k0, t0 = self._k[-1], self._t[-1]
            x = np.fromiter((k - k0 for k in self._k), float, len(self._k))  # centred for precision
            y = np.fromiter((v - t0 for v in self._t), float, len(self._t))
            xm, ym = x.mean(), y.mean()
            sxx = float(((x - xm) ** 2).sum())
            T = float(((x - xm) * (y - ym)).sum() / sxx) if sxx > 0 else (self._rough_period() or 0.0)
            a0 = ym - T * xm  # fitted time of the newest frame, relative to t0
            self._fit = (t0 + a0 - T * k0, T)
            self.period = T
            return float(t0 + a0)
        return t
