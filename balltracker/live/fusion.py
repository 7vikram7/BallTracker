"""Fuse bounce reports from several cameras, then make the line call.

Each calibrated camera reports bounces independently (position on the court
with a 2x2 covariance, contact time with an uncertainty). Reports of the same
physical bounce arrive within a few tens of milliseconds of each other on the
session clock, so reports closer than ``window_s`` are grouped.

Fusion is the standard inverse-covariance (information) weighting:

    P = (sum C_i^-1)^-1,   x = P * sum C_i^-1 x_i

so a camera that sees the bounce well (small covariance) dominates. If the
cameras disagree by more than their uncertainties allow (chi-square test on
the residuals), the fused covariance is inflated by the excess, and the call
is announced only if every camera on its own report makes the same call;
otherwise it is UNCERTAIN (silent) rather than confidently wrong. Even without
inflation, a fused OUT is silent if one camera's own report favours IN by 2:1
(its own p(out) < ``lean_in_p``): a precise camera saying OUT and a vague one
saying "probably in" fuse to OUT, and that is not certain enough to speak. A
camera that can't tell (p(out) near 0.5) does not block. The chi-square limit
is the 99.9% quantile for the actual degrees of freedom (2 per extra camera). (Inflation
alone is not enough: a covariance much bigger than the court puts most of the
probability outside it, i.e. p(out) -> 1.)

A group is released ``hold_s`` after its first report arrived (waiting for
slower cameras), or as soon as every calibrated camera that could still matter
has reported: cameras that can't see the spot are not waited for, and a camera
that rarely catches bounces there (hit rate below ``weak_rate``) only for
``weak_wait_s``. Field 2026-11-22: a phone that never reported a bounce held
every two-camera call for the full 0.6 s (calls 1.3 s after the bounce instead
of 0.8 s). A report arriving after its bounce was decided is dropped and counted
(``late_reports``): judged alone it would make a second decision for one bounce;
if its camera was counted as missing that bounce, the hit rate is corrected.

Corroboration: if two or more calibrated cameras can see the bounce point but
only one reported a bounce, an OUT is downgraded to UNCERTAIN (silent). A
single camera can be fooled (a kink from a paddle hit, a dropped frame); a
second camera that saw the same spot and saw nothing is evidence against it.

How much evidence depends on how often that camera catches real bounces there
(``CameraRecall``). Field test 3 (2026-11-21): a 720p 30 fps phone reported
18% of the bounces the other cameras saw on its half and 1% on the far half,
yet its silence vetoed calls like a perfect camera's. Now the judge learns each
camera's hit rate during play, per distance band, from bounces other cameras
confirmed. A silent camera that catches fewer than ``weak_rate`` of the bounces
at that distance no longer vetoes; any other silent camera still does. (Weighting
every veto by its camera's hit rate was tried and rejected: even the good
cameras catch only 50-77% by this measure, so it also unlocked 26 more lone-camera
OUTs that nothing can check.) A camera without data yet counts as fairly reliable
(the old behaviour).

Serves: the play state recognises a serve's landing (playstate.py); the bounce is then judged
against the service court (FAULT) unless the dashboard set the serve context by hand.

Plausibility gates before anything is spoken (field test 3, 2026-11-21: 12 single-camera OUTs,
several of them ball handling or tracking errors):

* the ball arrived faster than ``PlayConfig.max_shot_mps`` even at the low end of its measured
  range (2 sd): not a ball in play;
* one camera alone whose flight fit leaves the speed unknown (sd above that same limit): it can't
  tell a shot from anything else;
* "start of play" (a shot-like bounce that is neither a recognised serve nor part of a rally)
  more than ``far_out_m`` outside the court: ball handling between points;
* one camera alone, farther than ``single_view_max_m`` from the bounce and looking across the
  line rather than along it (the in/out direction is then the camera's depth direction, where
  a few pixels of calibration drift are tens of centimetres).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

import numpy as np

from ..events import BounceEvent, CallResult, LineCallEvent, Point3, Provenance
from ..geometry.court import CourtSpec, ServiceSide, Side
from ..sports.pickleball.line_calling import PickleballLineCaller, ServeContext
from .playstate import PlayConfig, PlayState

ALGO = "bounce_fusion"
ALGO_VERSION = "0.1.0"
CHI2_2DOF_999 = 13.8  # 99.9% quantile, 2 degrees of freedom (two cameras)


def chi2_limit(dof: int) -> float:
    """99.9% quantile of chi-square with ``dof`` degrees of freedom (13.8 for 2, 18.5 for 4)."""
    from scipy.stats import chi2

    return float(chi2.ppf(0.999, dof))


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
    limit = chi2_limit(dof)
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


class CameraRecall:
    """How often each camera reports a bounce that other cameras confirmed, at a spot it can see,
    per distance band from the camera. A beta prior (``prior_rate`` worth ``prior_n`` bounces)
    keeps a camera with few observations close to "fairly reliable"."""

    def __init__(self, scale: float = 1.0, edges_m: tuple[float, ...] = (8.0, 14.0),
                 prior_rate: float = 0.75, prior_n: float = 5.0):
        self.edges = tuple(e * scale for e in edges_m)
        self.prior_rate, self.prior_n = prior_rate, prior_n
        self.counts: dict[tuple[str, int], list[float]] = {}  # (camera, band) -> [hits, trials]

    def band(self, dist: float | None) -> int:
        return 0 if dist is None else int(np.searchsorted(self.edges, dist))

    def update(self, cam: str, dist: float | None, hit: bool) -> None:
        c = self.counts.setdefault((cam, self.band(dist)), [0.0, 0.0])
        c[0] += float(hit)
        c[1] += 1.0

    def credit(self, cam: str, dist: float | None) -> None:
        """A bounce counted as missed was caught after all (its report came late): miss -> hit."""
        c = self.counts.get((cam, self.band(dist)))
        if c is not None and c[0] < c[1]:
            c[0] += 1.0

    def rate(self, cam: str, dist: float | None) -> float:
        h, n = self.counts.get((cam, self.band(dist)), (0.0, 0.0))
        return (h + self.prior_rate * self.prior_n) / (n + self.prior_n)

    def summary(self, cam: str) -> dict:
        """-> {"near": {"hits", "of", "rate"}, ...} for the bands with observations."""
        names = ("near", "mid", "far") if len(self.edges) == 2 else tuple(str(i) for i in range(len(self.edges) + 1))
        out = {}
        for i, name in enumerate(names):
            h, n = self.counts.get((cam, i), (0.0, 0.0))
            if n:
                out[name] = {"hits": int(h), "of": int(n),
                             "rate": round((h + self.prior_rate * self.prior_n) / (n + self.prior_n), 2)}
        return out


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
                 play: PlayConfig | None = None, max_single_camera_std_m: float = 0.15,
                 view: Callable[[str, float, float], tuple[float, np.ndarray] | None] | None = None,
                 single_view_max_m: float = 8.0, far_out_m: float = 1.0, weak_rate: float = 0.4,
                 lean_in_p: float = 1 / 3, processed: Callable[[str, float], bool] | None = None,
                 weak_wait_s: float = 0.25):
        self.court = court
        scale = float(getattr(court, "scale", 1.0) or 1.0)
        # a silent camera that rarely catches bounces at that distance doesn't veto (module docstring)
        self.recall = CameraRecall(scale)
        self.weak_rate = weak_rate
        self.weak_wait_s = weak_wait_s  # how long a weak camera's report is waited for
        self.lean_in_p = lean_in_p  # a camera whose own p(out) is below this blocks a fused OUT
        # processed(camera, t): did that camera's worker process the frames around t? If not, its
        # silence means nothing (it neither vetoes nor counts as a miss in its hit rate).
        self.processed = processed
        # is the ball in play? serve? (see playstate.py; thresholds follow the court's scale)
        self.play = PlayState(play or PlayConfig.for_scale(scale), court)
        # view(camera, x, y) -> (distance m, horizontal unit vector camera -> point), or None
        self.view = view
        self.single_view_max_m = single_view_max_m * scale
        self.far_out_m = far_out_m * scale
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
        # recently decided groups: (time, {camera counted as missing it: its distance}); late reports
        # join none, but correct the hit rate of a camera that was counted as missing
        self._released: list[tuple[float, dict[str, float | None]]] = []
        self._misses: dict[str, float | None] = {}  # filled by _learn_recall for the group being decided
        self.late_reports = 0
        self._last: BounceEvent | None = None
        self.serve: ServeContext | None = None  # applies to the next bounce only

    def add(self, ev: BounceEvent, now: float) -> None:
        cam = set(ev.camera_ids)
        done = [m for t, m in self._released if abs(t - ev.t) <= self.window_s]
        if done and not any(abs(g.t - ev.t) <= self.window_s for g in self._groups):
            # Its bounce was already decided without it (the report arrived after the judge stopped
            # waiting). Judging it alone would make a second decision for one bounce, so it is
            # dropped (counted). It did catch the bounce, though: undo a miss counted against it.
            self.late_reports += 1
            for c in cam:
                if c in done[0]:
                    self.recall.credit(c, done[0].pop(c))
            return
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
            complete = expected_cameras is not None and not self._still_waiting_for(g, expected_cameras, now)
            (ready if complete or now - g.first_arrival >= self.hold_s else keep).append(g)
        self._groups = keep
        out = []
        for g in sorted(ready, key=lambda g: g.t):
            self._misses = {}
            out.append(self._decide(g))
            self._released.append((g.t, self._misses))
        if ready:  # keep a few seconds of released groups (reports arrive within ~1 s)
            last = max(g.t for g in ready)
            self._released = [(t, m) for t, m in self._released if last - t <= 10.0]
        return out

    def _still_waiting_for(self, g: _Group, expected: set[str], now: float) -> set[str]:
        """The calibrated cameras whose report on this bounce could still come and matter: not those
        that can't see the spot, and a weak camera there (hit rate < weak_rate) only for weak_wait_s."""
        missing = expected - g.cameras()
        if not missing:
            return set()
        x = float(np.mean([e.position.x for e in g.events]))
        y = float(np.mean([e.position.y for e in g.events]))
        waited = now - g.first_arrival
        wait = set()
        for c in missing:
            if self.can_see is not None and not self.can_see(c, x, y):
                continue
            if self.weak_rate > 0 and waited >= self.weak_wait_s:
                v = self.view(c, x, y) if self.view is not None else None
                if self.recall.rate(c, None if v is None else float(v[0])) < self.weak_rate:
                    continue
            wait.add(c)
        return wait

    def flush(self) -> list[Decision]:
        return self.poll(float("inf"))

    def _decide(self, g: _Group) -> Decision:
        b, diag = fuse(g.events)
        # A serve context set from the dashboard applies to the next bounce only, whatever happens
        # to that bounce (suppressed or not); otherwise it would be applied to a later rally ball.
        serve, self.serve = self.serve, None
        prev = self._last
        if prev is not None:
            same_half = np.sign(prev.position.y) == np.sign(b.position.y)
            further = abs(b.position.y) > abs(prev.position.y)
            if same_half and further and 0 < b.t - prev.t < self.caller.cfg.secondary_window_s:
                self._last = b
                self.play.assess(b, list(g.events), False)  # keep the bounce chain for the play state
                return Decision(b, None, list(g.events), diag, suppressed="secondary bounce")
        self._last = b
        ps = self.play.assess(b, list(g.events), serve is not None) if self.play.cfg.enabled else None
        if ps is not None:
            diag = {**diag, "play": ps["play"], "h_in_mps": ps["h_in_mps"], "vz_in_mps": ps.get("vz_in_mps"),
                    "h_in_lo_mps": ps.get("h_in_lo_mps")}
            if ps["suppress"]:
                return Decision(b, None, list(g.events), diag, suppressed=ps["suppress"])
            if serve is None and ps.get("serve"):
                sv = ps["serve"]
                serve = ServeContext(Side(sv["server_side"]),
                                     ServiceSide(sv["service_side"]) if sv["service_side"] else None)
                diag = {**diag, "serve": sv}
        call = self.caller.call(b, serve)
        if call.announce and diag.get("inflation", 1.0) > 1.0:
            # The cameras disagree beyond their uncertainties. The inflated covariance can be far
            # bigger than the court, and then p(out) -> 1 by itself (field 2026-11-20: one camera
            # labelled from the other end, bounces 2.5 m apart, OUT spoken). Announce only if every
            # camera, on its own report, makes the same announced call.
            own = [self.caller.call(e, serve) for e in g.events]
            if not all(c.announce and c.result == call.result for c in own):
                call = call.model_copy(update={"result": CallResult.UNCERTAIN, "announce": False, "call_text": None})
                diag = {**diag, "cameras_disagree": True}
        if call.announce and all((e.provenance.params or {}).get("unsettled") for e in g.events):
            # Every report is a bounce whose track was cut by a flush (a stall, the stream stopping)
            # less than settle_s after it: too few points after the bounce to trust an OUT.
            call = call.model_copy(update={"result": CallResult.UNCERTAIN, "announce": False, "call_text": None})
            diag = {**diag, "unsettled": True}
        if call.announce and len(g.events) > 1 and diag.get("inflation", 1.0) <= 1.0:
            # The cameras agree within their uncertainties, but one of them may still, on its own,
            # favour the other side of the line: a precise camera saying OUT and a vague one saying
            # "probably in" fuse to OUT. Silent if any camera's own p(out) < lean_in_p.
            own_p = [self.caller.call(e, serve).p_out for e in g.events]
            if min(own_p) < self.lean_in_p:
                call = call.model_copy(update={"result": CallResult.UNCERTAIN, "announce": False, "call_text": None})
                diag = {**diag, "cameras_disagree": True, "own_p_out": [round(p, 3) for p in own_p]}
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
        seeing = ({c for c in self._expected if self.can_see(c, b.position.x, b.position.y)}
                  if self.can_see is not None else set())
        if self.processed is not None:
            unknown = {c for c in seeing if c not in b.camera_ids and not self.processed(c, b.t)}
            if unknown:
                seeing -= unknown
                diag = {**diag, "not_processed": sorted(unknown)}
        seeing |= set(b.camera_ids) & self._expected  # a camera that reported it saw it (edge of view)
        if call.announce and self.corroborate and seeing:
            confirmed = seeing & set(b.camera_ids)
            silent = sorted(seeing - confirmed)
            if len(seeing) >= 2 and len(confirmed) < 2:
                rates = {c: self.recall.rate(c, self._dist(c, b)) for c in silent}
                strong = [c for c in silent if rates[c] >= self.weak_rate]
                weak = {c: round(rates[c], 2) for c in silent if rates[c] < self.weak_rate}
                if strong:
                    call = call.model_copy(update={"result": CallResult.UNCERTAIN, "announce": False, "call_text": None})
                    diag = {**diag, "unconfirmed_by": strong}
                if weak:  # these rarely catch a bounce there: their silence proves little
                    diag = {**diag, "silent_weak": weak}
        self._learn_recall(b, seeing, ps)
        if call.announce:
            gate = self._gate(b, call, ps)
            if gate:
                call = call.model_copy(update={"result": CallResult.UNCERTAIN, "announce": False, "call_text": None})
                diag = {**diag, "gate": gate}
        if call.announce:
            self.play.end_point()
        return Decision(b, call, list(g.events), diag)

    def _dist(self, cam: str, b: BounceEvent) -> float | None:
        v = self.view(cam, b.position.x, b.position.y) if self.view is not None else None
        return None if v is None else float(v[0])

    def _learn_recall(self, b: BounceEvent, seeing: set[str], ps: dict | None) -> None:
        """Count, for each camera that could see this spot, whether it reported a bounce that
        other cameras saw: two others, or one other on a ball in play (one camera's tracking
        error would otherwise count as everyone else's miss)."""
        reporters = set(b.camera_ids)
        in_play = ps is None or bool(ps.get("announce_ok"))
        for c in seeing:
            others = len(reporters - {c})
            if others >= 2 or (others == 1 and in_play):
                d = self._dist(c, b)
                self.recall.update(c, d, c in reporters)
                if c not in reporters:
                    self._misses[c] = d

    def _gate(self, b: BounceEvent, call: LineCallEvent, ps: dict | None) -> str | None:
        """Plausibility checks for an OUT / FAULT about to be spoken (see the module docstring)."""
        if ps is not None:
            lo = ps.get("h_in_lo_mps")
            if lo is not None and lo > self.play.cfg.max_shot_mps:
                return f"implausible speed (at least {lo:.0f} m/s)"
            h = ps.get("h_in_mps")
            if len(b.camera_ids) == 1 and h is not None and lo is not None and (h - lo) / 2 > self.play.cfg.max_shot_mps:
                return f"one camera, flight not measured (speed {h:.0f} +- {(h - lo) / 2:.0f} m/s)"
            if str(ps.get("play", "")).startswith("start of play") and call.signed_distance_m > self.far_out_m:
                return "start of play far outside the court (ball handling?)"
        if len(b.camera_ids) == 1 and self.view is not None:
            v = self.view(b.camera_ids[0], b.position.x, b.position.y)
            line = call.nearest_line or ""
            if v is not None and line:
                dist, direction = v
                normal = np.array([1.0, 0.0]) if ("sideline" in line or "centre" in line) else np.array([0.0, 1.0])
                if dist > self.single_view_max_m and abs(float(np.dot(direction, normal))) > 0.7:
                    return f"one camera, {dist:.0f} m away, looking across the {line}"
        return None
