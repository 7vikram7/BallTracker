"""Fuse bounce reports from several cameras, then make the line call.

Each calibrated camera reports bounces independently (position on the court
with a 2x2 covariance, contact time with an uncertainty). Reports of the same
physical bounce arrive within a few tens of milliseconds of each other on the
session clock, so reports closer than ``window_s`` are grouped.

Fusion is the standard inverse-covariance (information) weighting:

    P = (sum C_i^-1)^-1,   x = P * sum C_i^-1 x_i

so a camera that sees the bounce well (small covariance) dominates. If the
cameras disagree by more than their uncertainties allow (chi-square test on
the residuals), the fused covariance is inflated by the excess: the call
becomes UNCERTAIN (silent) rather than confidently wrong.

A group is released ``hold_s`` after its first report arrived (waiting for
slower cameras), or immediately once every calibrated camera has reported.

Corroboration: if two or more calibrated cameras can see the bounce point but
only one reported a bounce, an OUT is downgraded to UNCERTAIN (silent). A
single camera can be fooled (a kink from a paddle hit, a dropped frame); a
second camera that saw the same spot and saw nothing is evidence against it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from ..events import BounceEvent, CallResult, LineCallEvent, Point3, Provenance
from ..geometry.court import CourtSpec
from ..sports.pickleball.line_calling import PickleballLineCaller, ServeContext
from .playstate import PlayConfig, PlayState

ALGO = "bounce_fusion"
ALGO_VERSION = "0.1.0"
CHI2_2DOF_999 = 13.8  # 99.9% quantile, 2 degrees of freedom


def fuse(events: list[BounceEvent]) -> tuple[BounceEvent, dict]:
    """Combine reports of one bounce. Returns the fused event and diagnostics."""
    if len(events) == 1:
        return events[0], {"n": 1, "chi2": 0.0, "inflation": 1.0}
    xs = [np.array([e.position.x, e.position.y]) for e in events]
    Cs = [np.array(e.cov_xy, float) + np.eye(2) * 1e-8 for e in events]
    Is = [np.linalg.inv(C) for C in Cs]
    P = np.linalg.inv(sum(Is))
    x = P @ sum(I @ xi for I, xi in zip(Is, xs))
    chi2 = float(sum((xi - x) @ I @ (xi - x) for I, xi in zip(Is, xs)))
    dof = 2 * (len(events) - 1)
    # Inflate if the spread exceeds what the covariances allow (keeps the call honest).
    expected = max(dof, 1)
    limit = CHI2_2DOF_999 * dof / 2
    inflation = 1.0 if chi2 <= limit else chi2 / expected
    P = P * inflation
    w = np.array([1.0 / max(e.t_std, 1e-4) ** 2 for e in events])
    t = float(np.sum(w * np.array([e.t for e in events])) / w.sum())
    t_std = float(np.sqrt(1.0 / w.sum()))
    conf = float(1.0 - np.prod([1.0 - e.confidence for e in events]))
    best = max(events, key=lambda e: e.confidence)
    cams = sorted({c for e in events for c in e.camera_ids})
    ev = BounceEvent(
        t=t, t_std=t_std, position=Point3(x=float(x[0]), y=float(x[1])), cov_xy=P.tolist(),
        pixel=best.pixel, camera_ids=cams, confidence=min(conf, 1.0),
        supporting_observations=[o for e in events for o in e.supporting_observations],
        provenance=Provenance(algorithm=ALGO, version=ALGO_VERSION,
                              params={"sources": [e.id for e in events], "chi2": chi2, "inflation": inflation}),
    )
    return ev, {"n": len(events), "chi2": chi2, "inflation": inflation}


@dataclass
class _Group:
    first_arrival: float
    events: list[BounceEvent] = field(default_factory=list)

    @property
    def t(self) -> float:
        return float(np.mean([e.t for e in self.events]))

    def cameras(self) -> set[str]:
        return {c for e in self.events for c in e.camera_ids}


@dataclass
class Decision:
    bounce: BounceEvent
    call: LineCallEvent | None  # None when suppressed (secondary bounce)
    sources: list[BounceEvent]
    diagnostics: dict
    suppressed: str | None = None


class LiveJudge:
    """Groups camera reports, fuses them, suppresses secondary bounces, calls lines."""

    def __init__(self, court: CourtSpec, caller: PickleballLineCaller | None = None,
                 window_s: float = 0.08, hold_s: float = 0.6,
                 can_see: Callable[[str, float, float], bool] | None = None, corroborate: bool = True,
                 play: PlayConfig | None = None, max_single_camera_std_m: float = 0.15):
        self.court = court
        self.play = PlayState(play)  # is the ball in play? (see playstate.py)
        # One camera alone may announce only when it measures the bounce well across the line
        # (field test 2: a camera 16 m away along the court gave +-25 cm with possible bias).
        self.max_single_camera_std_m = max_single_camera_std_m
        self.can_see = can_see
        self.corroborate = corroborate
        self._expected: set[str] = set()
        self.caller = caller or PickleballLineCaller(court)
        self.window_s = window_s
        self.hold_s = hold_s
        self._groups: list[_Group] = []
        self._last: BounceEvent | None = None
        self.serve: ServeContext | None = None  # applies to the next bounce only

    def add(self, ev: BounceEvent, now: float) -> None:
        cam = set(ev.camera_ids)
        for g in self._groups:
            if abs(g.t - ev.t) <= self.window_s:
                same = [e for e in g.events if set(e.camera_ids) & cam]
                if same:  # the same camera twice: keep the more confident
                    if ev.confidence > same[0].confidence:
                        g.events.remove(same[0])
                        g.events.append(ev)
                    return
                g.events.append(ev)
                return
        self._groups.append(_Group(now, [ev]))

    def poll(self, now: float, expected_cameras: set[str] | None = None) -> list[Decision]:
        if expected_cameras is not None:
            self._expected = set(expected_cameras)
        ready, keep = [], []
        for g in self._groups:
            complete = expected_cameras is not None and expected_cameras <= g.cameras()
            (ready if complete or now - g.first_arrival >= self.hold_s else keep).append(g)
        self._groups = keep
        out = []
        for g in sorted(ready, key=lambda g: g.t):
            out.append(self._decide(g))
        return out

    def flush(self) -> list[Decision]:
        return self.poll(float("inf"))

    def _decide(self, g: _Group) -> Decision:
        b, diag = fuse(g.events)
        prev = self._last
        if prev is not None:
            same_half = np.sign(prev.position.y) == np.sign(b.position.y)
            further = abs(b.position.y) > abs(prev.position.y)
            if same_half and further and 0 < b.t - prev.t < self.caller.cfg.secondary_window_s:
                self._last = b
                self.play.assess(b, list(g.events), False)  # keep the bounce chain for the play state
                return Decision(b, None, list(g.events), diag, suppressed="secondary bounce")
        self._last = b
        serve, self.serve = self.serve, None
        ps = self.play.assess(b, list(g.events), serve is not None) if self.play.cfg.enabled else None
        if ps is not None:
            diag = {**diag, "play": ps["play"], "h_in_mps": ps["h_in_mps"]}
            if ps["suppress"]:
                return Decision(b, None, list(g.events), diag, suppressed=ps["suppress"])
        call = self.caller.call(b, serve)
        if ps is not None and not ps["announce_ok"] and call.announce:
            # A bounce, but not of a ball in play (dead ball / not clearly a shot): stay silent.
            call = call.model_copy(update={"result": CallResult.UNCERTAIN, "announce": False, "call_text": None})
        if call.announce and len(b.camera_ids) == 1 and self.max_single_camera_std_m:
            line = call.nearest_line or ""
            C = np.asarray(b.cov_xy, float)
            std_n = float(np.sqrt(C[0, 0] if ("sideline" in line or "centre" in line or "center" in line) else C[1, 1]))
            if std_n > self.max_single_camera_std_m:
                call = call.model_copy(update={"result": CallResult.UNCERTAIN, "announce": False, "call_text": None})
                diag = {**diag, "single_camera_std_cm": round(100 * std_n, 1)}
        if call.announce and self.corroborate and self.can_see is not None:
            seeing = {c for c in self._expected if self.can_see(c, b.position.x, b.position.y)}
            confirmed = seeing & set(b.camera_ids)
            if len(seeing) >= 2 and len(confirmed) < 2:
                
                call = call.model_copy(update={"result": CallResult.UNCERTAIN, "announce": False, "call_text": None})
                diag = {**diag, "unconfirmed_by": sorted(seeing - confirmed)}
        return Decision(b, call, list(g.events), diag)
