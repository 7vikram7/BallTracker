"""Map each phone's clock onto the server's clock.

The server sends ``ping`` at server time ``ts0``; the phone answers with its own
clock reading ``tp``; the answer arrives at ``ts1``. If the network delay is
the same both ways, ``tp`` happened at server time ``(ts0 + ts1) / 2``, so

    offset = (ts0 + ts1) / 2 - tp        (server = phone + offset)

with an error of at most ``rtt / 2``, where ``rtt = ts1 - ts0``. Wi-Fi delay is
bursty, so only the round trips with the smallest RTT are trusted. Phone clocks
also drift (typically 1-50 ppm, i.e. up to ~3 ms per minute), so with enough
history a linear drift term is fitted.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SyncSample:
    t_mid: float  # server time of the exchange midpoint
    offset: float  # server - phone, seconds
    rtt: float  # seconds


class ClockSync:
    def __init__(self, window: int = 120, best_fraction: float = 0.3, min_samples: int = 3,
                 drift_min_span_s: float = 20.0, max_drift_ppm: float = 500.0):
        self.samples: deque[SyncSample] = deque(maxlen=window)
        self.best_fraction = best_fraction
        self.min_samples = min_samples
        self.drift_min_span_s = drift_min_span_s
        self.max_drift = max_drift_ppm * 1e-6
        self._a = 0.0  # offset at t_ref
        self._b = 0.0  # drift (s/s)
        self._t_ref = 0.0
        self._rtt = float("nan")

    def add(self, ts0: float, tp: float, ts1: float) -> None:
        rtt = ts1 - ts0
        if rtt < 0:
            return
        self.samples.append(SyncSample(0.5 * (ts0 + ts1), 0.5 * (ts0 + ts1) - tp, rtt))
        self._update()

    @property
    def ready(self) -> bool:
        return len(self.samples) >= self.min_samples

    def _best(self) -> list[SyncSample]:
        s = sorted(self.samples, key=lambda x: x.rtt)
        k = max(self.min_samples, int(round(len(s) * self.best_fraction)))
        return s[:k]

    def _update(self) -> None:
        if not self.samples:
            return
        best = self._best()
        self._rtt = float(np.median([x.rtt for x in best]))
        t = np.array([x.t_mid for x in best])
        o = np.array([x.offset for x in best])
        self._t_ref = float(t.mean())
        if len(best) >= 5 and (t.max() - t.min()) >= self.drift_min_span_s:
            b, a = np.polyfit(t - self._t_ref, o, 1)
            if abs(b) <= self.max_drift:
                self._a, self._b = float(a), float(b)
                return
        self._a, self._b = float(np.median(o)), 0.0

    def offset_at(self, t_server: float) -> float:
        return self._a + self._b * (t_server - self._t_ref)

    def to_server(self, tp: float) -> float:
        # Solve ts = tp + a + b*(ts - t_ref) for ts (b is tiny, one step is exact enough).
        ts = tp + self._a
        return tp + self.offset_at(ts)

    @property
    def rtt(self) -> float:
        return self._rtt

    @property
    def uncertainty(self) -> float:
        """Rough 1-sigma error of the mapping (seconds)."""
        return 0.5 * self._rtt if np.isfinite(self._rtt) else float("inf")

    @property
    def drift_ppm(self) -> float:
        return self._b * 1e6

    def summary(self) -> dict:
        return {
            "samples": len(self.samples),
            "offset_s": self._a,
            "rtt_ms": self._rtt * 1e3 if np.isfinite(self._rtt) else None,
            "uncertainty_ms": self.uncertainty * 1e3 if np.isfinite(self._rtt) else None,
            "drift_ppm": self.drift_ppm,
        }
