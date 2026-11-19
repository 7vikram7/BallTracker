"""Is the ball in play? Only bounces of a ball in play are announced.

Field test 2 (2026-11-19) announced OUT for bounces that were not part of play: the
ball's second bounce after it had landed in and was not returned, and balls bounced
behind the baseline before serving / dropped / tossed back. A referee ignores those;
so does this module. It looks at each fused bounce together with the ball's flight
just before it (the 3D velocity the bounce detector's physics check estimated, from
each camera that saw it) and at the previous bounce:

1. Dead ball: the ball arrived with almost no horizontal speed (< 2 m/s): a pre-serve
   bounce, a ball dropped or bounced by hand. Not a shot: never announced.
2. Second bounce: the bounce is where and when the previous bounce's rebound comes down
   (position predicted from the outgoing velocity, flight time 2 * vz_out / g), on the
   same half. The point ended at the previous bounce: suppressed, at any delay
   (the old rule only caught second bounces within 1.2 s).
3. Rally: the previous announced-eligible bounce was on the other half within a few
   seconds (a shot crossed the net): called normally.
4. Start of play (none of the above): OUT is announced only if the ball arrived like a
   shot (>= 5 m/s horizontally) or the Serve button was pressed; otherwise the call is
   UNCERTAIN (silent). Silence is cheaper than a wrong OUT. Without flight data (physics
   check off) there is no evidence either way and the old behaviour is kept.

Volleys create no bounce, so a rally is still "alternating halves". Works the same in
matches and in drills (feeding balls to one half: every feed arrives like a shot).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..events import BounceEvent

ALGO = "play_state"
ALGO_VERSION = "0.1.0"
G = 9.81


@dataclass
class PlayConfig:
    enabled: bool = True
    dead_ball_mps: float = 2.0        # slower horizontal arrival: not a shot
    shot_mps: float = 5.0             # needed to announce an OUT at the start of play
    rally_gap_s: float = 4.0          # longest gap between bounces on alternating halves in a rally
    second_max_s: float = 3.0         # a second bounce comes within this time
    second_pos_tol_m: float = 1.5     # ... within this distance of the predicted landing point
    second_pos_tol_frac: float = 0.35  # ... or this fraction of the predicted travel, if larger
    second_time_tol_s: float = 0.35   # ... and this close to the predicted flight time
    second_time_tol_frac: float = 0.4


def flight(sources: list[BounceEvent]) -> dict | None:
    """3D velocity before / after the contact from the camera reports (best-fitting camera)."""
    best = None
    for e in sources:
        ph = (e.provenance.params or {}).get("physics") or {}
        if "v_in" not in ph or "v_out" not in ph:
            continue
        rms = max(ph.get("rms_in_px", 9.0), ph.get("rms_out_px", 9.0))
        if best is None or rms < best[0]:
            best = (rms, ph)
    if best is None:
        return None
    ph = best[1]
    return {"v_in": np.asarray(ph["v_in"], float), "v_out": np.asarray(ph["v_out"], float)}


@dataclass
class _Prev:
    t: float
    xy: np.ndarray
    v_out: np.ndarray | None
    eligible: bool  # was a bounce of a ball in play (rally / start of play)


class PlayState:
    def __init__(self, cfg: PlayConfig | None = None):
        self.cfg = cfg or PlayConfig()
        self.prev: _Prev | None = None
        self.last_eligible: _Prev | None = None

    def assess(self, b: BounceEvent, sources: list[BounceEvent], serve: bool) -> dict:
        """-> {"play": label, "announce_ok": bool, "suppress": str | None, ...}"""
        cfg = self.cfg
        xy = np.array([b.position.x, b.position.y])
        fl = flight(sources)
        h_in = float(np.hypot(*fl["v_in"][:2])) if fl else None
        out: dict = {"h_in_mps": None if h_in is None else round(h_in, 2)}

        label, ok, suppress = None, True, None
        p = self.prev
        if p is not None and p.v_out is not None and 0 < b.t - p.t <= cfg.second_max_s \
                and np.sign(p.xy[1]) == np.sign(xy[1]):
            dt = b.t - p.t
            vz = float(p.v_out[2])
            dt_pred = 2 * vz / G if vz > 0 else 0.0
            pred = p.xy + p.v_out[:2] * dt
            travel = float(np.hypot(*(p.v_out[:2] * dt)))
            pos_err = float(np.hypot(*(xy - pred)))
            if pos_err <= max(cfg.second_pos_tol_m, cfg.second_pos_tol_frac * travel) and \
                    abs(dt - dt_pred) <= max(cfg.second_time_tol_s, cfg.second_time_tol_frac * dt_pred):
                label, ok, suppress = "second bounce", False, "second bounce (ball not returned)"
                out.update(pred_err_m=round(pos_err, 2), dt_pred_s=round(dt_pred, 2))
        if label is None and h_in is not None and h_in < cfg.dead_ball_mps:
            label, ok = "dead ball", False
        if label is None:
            le = self.last_eligible
            if le is not None and 0 < b.t - le.t <= cfg.rally_gap_s and np.sign(le.xy[1]) != np.sign(xy[1]):
                label = "rally"
            elif serve or (h_in is not None and h_in >= cfg.shot_mps):
                label = "start of play"
            elif h_in is None:
                # No flight data (physics check off, or an older report): no evidence either way,
                # keep the behaviour from before the play state.
                label = "start of play (no flight data)"
            else:
                label, ok = "not clearly a shot", False
        cur = _Prev(b.t, xy, fl["v_out"] if fl else None, label.startswith(("rally", "start of play")))
        self.prev = cur
        if cur.eligible:
            self.last_eligible = cur
        out.update(play=label, announce_ok=ok, suppress=suppress)
        return out
