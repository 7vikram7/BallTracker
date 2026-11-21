"""Link per-frame ball candidates into 2D tracks.

Greedy multi-track association with a constant-acceleration predictor and a
speed-dependent gate (so tracks survive the velocity kink at a bounce). The
predictor is a least-squares quadratic over the last few points (robust to
per-frame jitter); the gate also scales with the ball's apparent size, since a
large, close ball has proportionally larger centroid noise. At a bounce the
image velocity can reverse completely (camera low, ball moving mostly
vertically in the image), so the speed term must allow ~(1 + e) * speed * dt. After
the pass, tracks that are too short or barely move are discarded (static yellow
objects, flicker). Each surviving track is a sequence of (t, u, v) samples.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy.optimize import linear_sum_assignment

from .detection import Candidate


@dataclass
class TrackPoint:
    frame_index: int
    t: float
    u: float
    v: float
    radius_px: float
    score: float
    obs_id: str | None = None


@dataclass
class Track:
    track_id: int
    points: list[TrackPoint] = field(default_factory=list)
    misses: int = 0

    def _recent(self, n: int) -> tuple[np.ndarray, np.ndarray]:
        q = self.points[-n:]
        ts = np.array([x.t for x in q]) - q[-1].t
        uv = np.array([[x.u, x.v] for x in q])
        return ts, uv

    def predict(self, t: float, window: int = 6) -> np.ndarray:
        p = self.points
        if len(p) == 1:
            return np.array([p[-1].u, p[-1].v])
        ts, uv = self._recent(window)
        deg = 2 if len(ts) >= 5 else 1
        dt = t - p[-1].t
        # Least-squares polynomial via the normal equations (np.polyfit's SVD and checks cost more
        # than the tiny fit itself; this runs for every track on every frame).
        A = np.vander(ts, deg + 1)
        try:
            coef = np.linalg.solve(A.T @ A, A.T @ uv)
        except np.linalg.LinAlgError:
            coef = np.polyfit(ts, uv, deg)
        return np.vander(np.array([dt]), deg + 1)[0] @ coef

    def speed_px_s(self, window: int = 4) -> float:
        p = self.points
        if len(p) < 2:
            return 0.0
        ts, uv = self._recent(window)
        span = ts[-1] - ts[0]
        return float(np.hypot(*(uv[-1] - uv[0])) / max(span, 1e-6))

    def radius_px(self, window: int = 5) -> float:
        return float(np.median([x.radius_px for x in self.points[-window:]]))

    def path_length_px(self) -> float:
        if len(self.points) < 2:
            return 0.0
        uv = np.array([[q.u, q.v] for q in self.points])
        return float(np.sum(np.linalg.norm(np.diff(uv, axis=0), axis=1)))


@dataclass
class TrackerConfig:
    gate_base_px: float = 25.0
    gate_radius_factor: float = 0.8  # gate >= this * apparent ball radius
    gate_speed_factor: float = 1.8  # extra gate = factor * speed * dt (bounce can reverse velocity)
    # A one-point track has no velocity yet: allow a jump of up to this many
    # ball radii (plus the base gate) to its second point.
    init_gate_radius_factor: float = 4.0
    # Apparent ball size changes slowly; a candidate more than this many times
    # larger/smaller than the track's recent radius is not the same object.
    max_radius_ratio: float = 2.5
    radius_cost: float = 0.5  # weight of |ln(r_cand / r_track)| in the match cost
    max_misses: int = 4
    # If set, a track ends when it has had no point for longer than this (seconds) instead of
    # after max_misses frames: the same tolerance at 30, 60 and 120 fps and with the phone's
    # reduced frame stream (review of defed68, TODO-16; entry 28).
    max_miss_s: float | None = None
    min_track_len: int = 6
    min_path_px: float = 30.0


class BallTracker:
    def __init__(self, cfg: TrackerConfig | None = None):
        self.cfg = cfg or TrackerConfig()
        self._active: list[Track] = []
        self._finished: list[Track] = []
        self._next_id = 0
        self._last_t: float | None = None

    def update(self, frame_index: int, t: float, cands: list[Candidate], obs_ids: list[str] | None = None) -> None:
        cfg = self.cfg
        dt = 0.0 if self._last_t is None else t - self._last_t
        self._last_t = t
        tracks = self._active
        if tracks and cands:
            cost = np.full((len(tracks), len(cands)), 1e6)
            cu = np.array([c.u for c in cands])
            cv = np.array([c.v for c in cands])
            cr = np.maximum(np.array([c.radius_px for c in cands]), 1.0)
            cs = np.array([c.score for c in cands])
            for i, tr in enumerate(tracks):
                pred = tr.predict(t)
                gap = t - tr.points[-1].t
                r_tr = tr.radius_px()
                base = max(cfg.gate_base_px, cfg.gate_radius_factor * r_tr)
                if len(tr.points) == 1:
                    gate = base + cfg.init_gate_radius_factor * max(r_tr, 3.0)
                else:
                    gate = base + cfg.gate_speed_factor * tr.speed_px_s() * max(gap, dt)
                d = np.hypot(cu - pred[0], cv - pred[1])
                ratio = cr / max(r_tr, 1.0)
                ok = (d <= gate) & (np.maximum(ratio, 1 / ratio) <= cfg.max_radius_ratio)
                if ok.any():
                    # Normalised distance + size consistency; small bonus for
                    # established tracks so new clutter tracks don't steal the ball.
                    c_i = d / gate + cfg.radius_cost * np.abs(np.log(ratio)) - 0.1 * cs \
                        - 0.1 * min(len(tr.points), 10) / 10
                    cost[i, ok] = c_i[ok]
            rows, cols = linear_sum_assignment(cost)
            assigned_t, assigned_c = set(), set()
            for r, c in zip(rows, cols):
                if cost[r, c] >= 1e5:
                    continue
                cd = cands[c]
                tracks[r].points.append(
                    TrackPoint(frame_index, t, cd.u, cd.v, cd.radius_px, cd.score, obs_ids[c] if obs_ids else None)
                )
                tracks[r].misses = 0
                assigned_t.add(r)
                assigned_c.add(c)
        else:
            assigned_t, assigned_c = set(), set()

        for i, tr in enumerate(tracks):
            if i not in assigned_t:
                tr.misses += 1
        still: list[Track] = []
        for tr in tracks:
            if cfg.max_miss_s is not None:
                ended = tr.misses > 0 and t - tr.points[-1].t > cfg.max_miss_s
            else:
                ended = tr.misses > cfg.max_misses
            (self._finished if ended else still).append(tr)
        self._active = still
        for j, cd in enumerate(cands):
            if j in assigned_c:
                continue
            tr = Track(self._next_id)
            self._next_id += 1
            tr.points.append(TrackPoint(frame_index, t, cd.u, cd.v, cd.radius_px, cd.score, obs_ids[j] if obs_ids else None))
            self._active.append(tr)

    # --- live (streaming) use ------------------------------------------------
    def active_tracks(self) -> list[Track]:
        return list(self._active)

    def end_all(self) -> None:
        """Close every active track (e.g. the video stream paused)."""
        self._finished.extend(self._active)
        self._active = []

    def pop_finished(self) -> list[Track]:
        """Tracks that ended since the last call (live mode; keeps memory bounded)."""
        out, self._finished = self._finished, []
        return out

    def finish(self) -> list[Track]:
        self._finished.extend(self._active)
        self._active = []
        cfg = self.cfg
        good = [
            tr
            for tr in self._finished
            if len(tr.points) >= cfg.min_track_len and tr.path_length_px() >= cfg.min_path_px
        ]
        good.sort(key=lambda tr: tr.points[0].t)
        return good
