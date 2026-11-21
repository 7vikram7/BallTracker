"""Pickleball line calling: turn a reconstructed bounce into IN / OUT / UNCERTAIN.

Rules implemented
-----------------
* A ball is IN if any part of its contact with the surface touches the line
  (lines belong to the area they bound). Modelled as: IN when the distance from
  the contact centre to the target region is <= ``contact_patch_radius``.
* On a serve the target is the diagonal service court. The non-volley (kitchen)
  line belongs to the kitchen, so a serve touching it is a FAULT; the
  centreline and the baseline/sidelines are part of the service court.
* In a rally the target is the opponent's half of the court, taken here as the
  half the bounce landed in.

Decision policy (silent unless sure it's out)
---------------------------------------------
p_out = P(contact outside target | bounce estimate), from the bounce's position
covariance by Monte Carlo.

    p_out >= out_threshold   -> OUT     (announce "OUT" or "FAULT")
    p_out <= in_threshold    -> IN      (silent)
    otherwise                -> UNCERTAIN (silent, flagged for review)

A wrong "OUT" stops a rally that should have continued, so ``out_threshold`` is
deliberately high.

Known gaps (explicit, not hidden)
---------------------------------
* Who hit the ball is not known from one camera; "rally" assumes the bounce is
  the first bounce on the receiving side. A ball bouncing twice is filtered by a
  simple heuristic (``suppress_secondary``).
* Serve context (server side and court) is supplied by the caller: the live judge detects serves
  itself (live/playstate.py) or takes it from the dashboard. When the server's half (right/left)
  is not known, the serve is judged against the whole service area of the receiving side (both
  service courts, kitchen excluded): kitchen, baseline and sideline faults are called, a serve to
  the wrong service court is not.
* Kitchen (non-volley zone) *player* violations are not handled here.
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass

import numpy as np

from ...events import BounceEvent, CallResult, LineCallEvent, Provenance, ShotContext
from ...geometry.court import CourtSpec, Rect, ServiceSide, Side

ALGO = "pickleball_line_call"
ALGO_VERSION = "0.1.0"


@dataclass
class LineCallConfig:
    out_threshold: float = 0.95
    in_threshold: float = 0.05
    samples: int = 4000
    # OUT is only announced for confident bounces. Real bounces score ~1.0 on
    # real footage; false ones (pot hit, frame drops) scored 0.34-0.51.
    min_bounce_confidence: float = 0.6
    secondary_window_s: float = 1.2
    seed: int = 0


@dataclass(frozen=True)
class ServeContext:
    server_side: Side
    service_side: ServiceSide | None = None  # None: the server's half is not known


def p_outside(rect: Rect, mean: np.ndarray, cov: np.ndarray, patch_radius: float, n: int, rng: np.random.Generator) -> float:
    cov = np.asarray(cov, float)
    # Guard against degenerate covariance.
    cov = cov + np.eye(2) * 1e-10
    pts = rng.multivariate_normal(np.asarray(mean, float), cov, size=n)
    d = rect.distance_outside(pts[:, 0], pts[:, 1])
    return float(np.mean(d > patch_radius))


class PickleballLineCaller:
    def __init__(self, court: CourtSpec, cfg: LineCallConfig | None = None):
        self.court = court
        self.cfg = cfg or LineCallConfig()

    def _rng_for(self, bounce: BounceEvent) -> np.random.Generator:
        """A generator seeded from the bounce itself: the same bounce gets the same p_out whatever
        was called before it (one shared generator made p_out depend on the call history)."""
        key = f"{bounce.t:.3f}:{bounce.position.x:.4f}:{bounce.position.y:.4f}:{self.cfg.seed}"
        return np.random.default_rng(zlib.crc32(key.encode()))

    def provenance(self) -> Provenance:
        c = self.cfg
        return Provenance(
            algorithm=ALGO,
            version=ALGO_VERSION,
            params={
                "out_threshold": c.out_threshold,
                "in_threshold": c.in_threshold,
                "contact_patch_radius": self.court.contact_patch_radius,
                "line_width": self.court.line_width,
            },
        )

    def target_for(self, bounce: BounceEvent, serve: ServeContext | None) -> tuple[Rect, str, ShotContext]:
        if serve is not None:
            recv = serve.server_side.other
            if serve.service_side is None:
                k, hw, hl = self.court.kitchen_depth, self.court.half_w, self.court.half_l
                rect = Rect(-hw, hw, k, hl) if recv is Side.B else Rect(-hw, hw, -hl, -k)
                return rect, f"service_area_{recv.value}", ShotContext.SERVE
            rect = self.court.serve_target(serve.server_side, serve.service_side)
            return rect, f"service_court_{recv.value}_{serve.service_side.value}", ShotContext.SERVE
        side = Side.B if bounce.position.y >= 0 else Side.A
        return self.court.half_rect(side), f"half_{side.value}", ShotContext.RALLY

    def call(self, bounce: BounceEvent, serve: ServeContext | None = None) -> LineCallEvent:
        c = self.cfg
        rect, region, ctx = self.target_for(bounce, serve)
        mean = np.array([bounce.position.x, bounce.position.y])
        p_out = p_outside(rect, mean, np.array(bounce.cov_xy), self.court.contact_patch_radius, c.samples,
                          self._rng_for(bounce))
        if ctx is ShotContext.SERVE and serve is not None and serve.service_side is None and p_out >= c.out_threshold:
            # The server's half is unknown, so the target is the whole service area. Only call the
            # FAULT if the ball is out of the receiving half altogether (long or wide: out whatever
            # the shot was). In the kitchen it may be a rally ball taken for a serve (a dink: IN).
            half = self.court.half_rect(serve.server_side.other)
            p_half = p_outside(half, mean, np.array(bounce.cov_xy), self.court.contact_patch_radius, c.samples,
                               self._rng_for(bounce))
            if p_half < c.out_threshold:
                p_out = min(p_out, c.out_threshold - 1e-6)  # -> UNCERTAIN below
                region = region + "_kitchen_unknown_side"
        if p_out >= c.out_threshold:
            result = CallResult.OUT
        elif p_out <= c.in_threshold:
            result = CallResult.IN
        else:
            result = CallResult.UNCERTAIN
        if bounce.confidence < c.min_bounce_confidence and result is CallResult.OUT:
            result = CallResult.UNCERTAIN
        sd = float(rect.signed_distance(np.array(mean[0]), np.array(mean[1]))) - self.court.contact_patch_radius
        line, _ = self.court.nearest_line(mean[0], mean[1])
        announce = result is CallResult.OUT
        text = None
        if announce:
            text = "FAULT" if ctx is ShotContext.SERVE else "OUT"
        return LineCallEvent(
            bounce_id=bounce.id,
            t=bounce.t,
            context=ctx,
            target_region=region,
            result=result,
            p_out=p_out,
            nearest_line=line,
            signed_distance_m=sd,
            announce=announce,
            call_text=text,
            provenance=self.provenance(),
        )

    def suppress_secondary(self, bounces: list[BounceEvent]) -> list[BounceEvent]:
        """Drop a bounce that follows another on the same half, moving away from
        the net, within ``secondary_window_s`` (the ball bouncing again after its
        first, already-judged contact)."""
        out: list[BounceEvent] = []
        for b in sorted(bounces, key=lambda b: b.t):
            if out:
                p = out[-1]
                same_half = np.sign(p.position.y) == np.sign(b.position.y)
                further = abs(b.position.y) > abs(p.position.y)
                if same_half and further and (b.t - p.t) < self.cfg.secondary_window_s:
                    continue
            out.append(b)
        return out
