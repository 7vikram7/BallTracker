"""Is the ball in play? Only bounces of a ball in play are announced.

Field test 2 (2026-11-19) announced OUT for bounces that were not part of play: the
ball's second bounce after it had landed in and was not returned, and balls bounced
behind the baseline before serving / dropped / tossed back. A referee ignores those;
so does this module. It looks at each fused bounce together with the ball's flight
just before it (the 3D velocity the bounce detector's physics check estimated, from
each camera that saw it) and at the previous bounce:

1. Dead ball: the ball arrived with almost no horizontal speed (< 2 m/s) and was not
   falling fast (< 7 m/s, a drop from ~2.5 m): a pre-serve bounce, a ball dropped or bounced
   by hand. Not a shot: never announced. (A moonball lands with ~2.5 m/s horizontally but
   falls at 10+ m/s: not a dead ball.)
2. Second bounce: the bounce is where and when the previous bounce's rebound comes down
   (position predicted from the outgoing velocity, flight time 2 * vz_out / g), on the
   same half. The point ended at the previous bounce: suppressed, at any delay
   (the old rule only caught second bounces within 1.2 s).
3. Rally: the previous announced-eligible bounce was on the other half within a few
   seconds (a shot crossed the net): called normally. The window grows with the flight
   time of the incoming ball (estimated from how fast it fell), so a lob that hangs in the
   air for 2.5 s after a volley exchange is still part of the rally.
4. Start of play (none of the above): OUT is announced only if the ball arrived like a
   shot: >= 5 m/s horizontally, or a lob (falling >= 8 m/s: apex above ~4 m, which a ball
   tossed back to the server rarely reaches), or the Serve button was pressed; otherwise the
   call is UNCERTAIN (silent). Silence is cheaper than a wrong OUT. Without flight data
   (physics check off) there is no evidence either way and the old behaviour is kept.

Flight data: each camera's physics fit gives the 3D velocity before and after the contact
with its covariance. One camera measures motion across its view well and along its view
badly (errors of several m/s), so the cameras are combined weighted by their covariances
(lob study 2026-11-19: picking the single best-fitting camera gave horizontal speeds off by
up to 12 m/s).

Volleys create no bounce, so a rally is still "alternating halves". Works the same in
matches and in drills (feeding balls to one half: every feed arrives like a shot).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..bounce import information, psd_inverse
from ..events import BounceEvent

ALGO = "play_state"
ALGO_VERSION = "0.2.0"  # 0.2: fused flight, lob rules
G = 9.81


@dataclass
class PlayConfig:
    enabled: bool = True
    dead_ball_mps: float = 2.0        # slower horizontal arrival: not a shot ...
    dead_ball_vz_mps: float = 7.0     # ... unless it was falling faster than this (a lob)
    shot_mps: float = 5.0             # needed to announce an OUT at the start of play ...
    lob_vz_mps: float = 8.0           # ... or falling at least this fast (a lob, apex above ~4 m)
    rally_gap_s: float = 4.0          # longest gap between bounces on alternating halves in a rally
    rally_flight_ref_s: float = 1.0   # ... for a ball in the air this long; longer flights add to it
    rally_gap_max_s: float = 7.0
    second_max_s: float = 3.0         # a second bounce comes within this time
    second_pos_tol_m: float = 1.5     # ... within this distance of the predicted landing point
    second_pos_tol_frac: float = 0.35  # ... or this fraction of the predicted travel, if larger
    second_time_tol_s: float = 0.35   # ... and this close to the predicted flight time
    second_time_tol_frac: float = 0.4

    @classmethod
    def for_scale(cls, scale: float) -> "PlayConfig":
        """Thresholds for a scaled practice court (e.g. 0.2 for a mini court on a floor).

        Gravity does not scale, so a shot with the same arc over a court k times smaller flies
        sqrt(k) times slower and lasts sqrt(k) times shorter; distances shrink k times. The
        rally gap (players' reaction time) is not scaled."""
        c = cls()
        if scale == 1.0:
            return c
        r = scale ** 0.5
        c.dead_ball_mps *= r
        c.dead_ball_vz_mps *= r
        c.shot_mps *= r
        c.lob_vz_mps *= r
        c.rally_flight_ref_s *= r
        c.second_max_s *= r
        c.second_pos_tol_m *= scale
        c.second_time_tol_s *= r
        return c


def flight(sources: list[BounceEvent]) -> dict | None:
    """3D velocity before / after the contact, all cameras combined.

    Reports with a velocity covariance are fused by inverse-covariance weighting (each camera
    contributes what it measured); older reports without one fall back to the best-fitting
    camera."""
    with_cov, without = [], []
    for e in sources:
        ph = (e.provenance.params or {}).get("physics") or {}
        if "v_in" not in ph or "v_out" not in ph:
            continue
        if "v_in_cov" in ph and "v_out_cov" in ph:
            with_cov.append(ph)
        else:
            without.append(ph)
    if with_cov:
        out = {"n_cameras": len(with_cov)}
        for k in ("v_in", "v_out"):
            info, vec = np.zeros((3, 3)), np.zeros(3)
            for ph in with_cov:
                # A broken (non-positive) variance must not become a negative or infinite weight.
                Ci = information(np.asarray(ph[k + "_cov"], float))
                info += Ci
                vec += Ci @ np.asarray(ph[k], float)
            cov = psd_inverse(info)
            out[k] = cov @ vec
            out[k + "_cov"] = cov
        return out
    if not without:
        return None
    ph = min(without, key=lambda p: max(p.get("rms_in_px", 9.0), p.get("rms_out_px", 9.0)))
    return {"v_in": np.asarray(ph["v_in"], float), "v_out": np.asarray(ph["v_out"], float), "n_cameras": 1}


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
        vz_in = float(fl["v_in"][2]) if fl else None
        out: dict = {"h_in_mps": None if h_in is None else round(h_in, 2),
                     "vz_in_mps": None if vz_in is None else round(vz_in, 2)}

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
        lob = vz_in is not None and -vz_in >= cfg.lob_vz_mps
        if label is None and h_in is not None and h_in < cfg.dead_ball_mps and -vz_in < cfg.dead_ball_vz_mps:
            label, ok = "dead ball", False
        if label is None:
            le = self.last_eligible
            # Flight time of the incoming ball ~ 2 * fall speed / g (up and down); a lob that
            # hangs in the air longer than a drive stretches the rally window by the difference.
            flight_s = 2 * max(-vz_in, 0.0) / G if vz_in is not None else 0.0
            gap = min(cfg.rally_gap_s + max(0.0, flight_s - cfg.rally_flight_ref_s), cfg.rally_gap_max_s)
            if le is not None and 0 < b.t - le.t <= gap and np.sign(le.xy[1]) != np.sign(xy[1]):
                label = "rally"
            elif serve or (h_in is not None and h_in >= cfg.shot_mps):
                label = "start of play"
            elif lob:
                label = "start of play (lob)"
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
