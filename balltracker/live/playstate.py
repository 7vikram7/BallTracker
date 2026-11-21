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

Serves (field test 3, 2026-11-21: serves were never recognised, so a serve into the wrong
service court or the kitchen was judged like a rally ball). Between points (after a second
bounce, a dead ball / ball handling, an announced call, or 5 s without a ball in play; and at
least 3 s after the last ball in play: a new point never starts faster, in the session serves
came 4-12 s after the previous point) the next bounce is a serve if its flight came over the
net from behind the far baseline. Only in match mode: in a drill (balls fed from the baseline)
every feed would look like a serve, so ``serve_detection`` is off (``bt serve --drill``, or the
dashboard).

* the incoming ball moves towards the landing half's baseline, clearly (|vy| >= 3 m/s and at
  least 3 standard deviations of the fused measurement);
* traced back along its arc (gravity, no drag) to the server's baseline, the ball was at a
  plausible contact height there: -2 to 3 m. A rally shot from mid-court traced back that far
  is metres below the ground (in the session: serves 0.8, 0.1, -0.4 m; a drive from near the
  kitchen labelled "start of play", -13 m);
* the trace meets the baseline between the sideline extensions (0.5 m tolerance): the server must
  stand there; a drive down the line traced back lands outside them;
* serves go cross-court: a ball that lands more than 1 m into the server's own side (straight
  ahead) was a rally shot (in the session: five such "serves" landed 1.7-3 m into the wrong
  court); a serve into the wrong court is a mishit near the centre line;
* the server's half (right / left, seen from the server) is where the trace meets the baseline,
  if that is clear (>= 0.3 m and 2 sd from the centre); otherwise the pre-serve bounce behind
  that baseline in the last 10 s (players bounce the ball where they serve from); otherwise
  unknown, and the serve is judged against the whole service area of the receiving side.

Plausibility: ``h_in_lo_mps`` is the incoming horizontal speed minus 2 sd. One camera measures
speed along its line of sight badly (+-13 m/s is common), so a high single-camera speed is not
by itself impossible; a lower bound above 25 m/s (90 km/h) is (the judge stays silent then).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..bounce import information, psd_inverse
from ..events import BounceEvent
from ..geometry.court import CourtSpec, ServiceSide, Side

ALGO = "play_state"
ALGO_VERSION = "0.3.0"  # 0.2: fused flight, lob rules; 0.3: serve detection, speed lower bound
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
    # serves (see the module docstring)
    serve_detection: bool = True
    point_gap_s: float = 5.0          # this long without a ball in play: the point is over
    serve_min_gap_s: float = 3.0      # ... and a serve comes at least this long after the last ball in play
    serve_min_vy_mps: float = 3.0     # the serve comes over the net at least this fast (along the court)
    serve_vy_sigmas: float = 3.0      # ... measured to at least this many standard deviations
    serve_z_range: tuple[float, float] = (-2.0, 3.0)  # traced-back height at the server's baseline
    serve_side_min_m: float = 0.3     # trace meets the baseline this far from the centre: side known
    serve_outside_m: float = 0.5      # ... and no farther than this outside the sideline extension
    serve_wrong_court_max_m: float = 1.0  # serves go cross-court: landing farther than this on the server's own side = not a serve
    drop_lookback_s: float = 10.0     # pre-serve bounce behind the baseline within this time
    max_shot_mps: float = 25.0        # incoming horizontal speed lower bound above this: implausible

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
        c.serve_min_vy_mps *= r
        c.max_shot_mps *= r
        c.serve_side_min_m *= scale
        c.serve_outside_m *= scale
        c.serve_wrong_court_max_m *= scale
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


def h_lower_bound(fl: dict | None, sigmas: float = 2.0) -> float | None:
    """Incoming horizontal speed minus ``sigmas`` standard deviations (None without a covariance)."""
    if not fl or "v_in_cov" not in fl:
        return None
    v = np.asarray(fl["v_in"], float)[:2]
    h = float(np.hypot(*v))
    if h < 1e-6:
        return 0.0
    u = v / h
    sd = float(np.sqrt(max(u @ np.asarray(fl["v_in_cov"], float)[:2, :2] @ u, 0.0)))
    return h - sigmas * sd


class PlayState:
    def __init__(self, cfg: PlayConfig | None = None, court: CourtSpec | None = None):
        self.cfg = cfg or PlayConfig()
        self.court = court
        self.prev: _Prev | None = None
        self.last_eligible: _Prev | None = None
        self.point_over = True  # between points: the next shot-like bounce may be a serve
        self.drops: list[tuple[float, np.ndarray]] = []  # recent dead-ball bounces (pre-serve bounces)

    def end_point(self) -> None:
        """The judge announced a call: the point is over."""
        self.point_over = True

    def serve_of(self, b: BounceEvent, fl: dict | None) -> dict | None:
        """Was this bounce a serve's landing? -> {"server_side", "service_side", ...} or None."""
        cfg, court = self.cfg, self.court
        if court is None or not fl or "v_in_cov" not in fl:
            return None
        x, y = b.position.x, b.position.y
        if abs(y) < 0.05 * court.half_l:
            return None  # on the net line: no half to judge
        vx, vy, vz = (float(v) for v in fl["v_in"])
        C = np.asarray(fl["v_in_cov"], float)
        sy = float(np.sqrt(max(C[1, 1], 0.0)))
        if np.sign(vy) != np.sign(y) or abs(vy) < cfg.serve_min_vy_mps or abs(vy) < cfg.serve_vy_sigmas * sy:
            return None  # not clearly coming over the net
        y_base = -float(np.sign(y)) * court.half_l  # the server's baseline
        tau = abs(y - y_base) / abs(vy)
        z0 = court.ball_radius - vz * tau - 0.5 * G * tau * tau
        if not cfg.serve_z_range[0] <= z0 <= cfg.serve_z_range[1]:
            return None
        server = Side.A if y_base < 0 else Side.B
        k = (y - y_base) / vy
        xo = x - vx * k
        J = np.array([-k, vx * (y - y_base) / vy**2])
        sxo = float(np.sqrt(max(J @ C[:2, :2] @ J, 0.0)))
        if abs(xo) - 2 * sxo > court.half_w + cfg.serve_outside_m:
            return None  # the server stands between the sideline extensions: not a serve
        side_x, how = None, None
        if abs(xo) >= max(cfg.serve_side_min_m, 2 * sxo):
            side_x, how = xo, "flight"
        else:
            for t_d, xy_d in reversed(self.drops):
                if b.t - t_d > cfg.drop_lookback_s:
                    break
                if np.sign(xy_d[1]) == np.sign(y_base) and abs(xy_d[1]) >= court.half_l - 0.5 * court.scale \
                        and abs(xy_d[0]) >= cfg.serve_side_min_m:
                    side_x, how = float(xy_d[0]), "pre-serve bounce"
                    break
        side = None
        if side_x is not None and np.sign(x) == np.sign(side_x) and abs(x) > cfg.serve_wrong_court_max_m:
            return None  # straight ahead, metres into the server's own side: a rally shot, not a serve
        if side_x is not None:
            right = side_x > 0 if server is Side.A else side_x < 0
            side = ServiceSide.RIGHT if right else ServiceSide.LEFT
        return {"server_side": server.value, "service_side": side.value if side else None,
                "x_origin": round(xo, 2), "x_origin_sd": round(sxo, 2), "z_at_baseline": round(z0, 2),
                "side_from": how}

    def assess(self, b: BounceEvent, sources: list[BounceEvent], serve: bool) -> dict:
        """-> {"play": label, "announce_ok": bool, "suppress": str | None, ...}"""
        cfg = self.cfg
        xy = np.array([b.position.x, b.position.y])
        fl = flight(sources)
        h_in = float(np.hypot(*fl["v_in"][:2])) if fl else None
        vz_in = float(fl["v_in"][2]) if fl else None
        lo = h_lower_bound(fl)
        out: dict = {"h_in_mps": None if h_in is None else round(h_in, 2),
                     "vz_in_mps": None if vz_in is None else round(vz_in, 2),
                     "h_in_lo_mps": None if lo is None else round(lo, 2)}
        le0 = self.last_eligible
        between_points = self.point_over or le0 is None or b.t - le0.t > cfg.point_gap_s

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
        if label is None and fl is None and p is not None and p.eligible and p.v_out is None \
                and 0 < b.t - p.t <= cfg.second_max_s and np.sign(p.xy[1]) == np.sign(xy[1]) \
                and abs(xy[1]) > abs(p.xy[1]):
            # Neither bounce has flight data, so the second-bounce prediction above can't run. A
            # later bounce on the same half, further from the net, within the window is the
            # unreturned ball bouncing again (the judge's own 1.2 s check misses 1.2-3 s).
            label, ok, suppress = "second bounce", False, "second bounce (no flight data)"
        lob = vz_in is not None and -vz_in >= cfg.lob_vz_mps
        if label is None and h_in is not None and h_in < cfg.dead_ball_mps and -vz_in < cfg.dead_ball_vz_mps:
            label, ok = "dead ball", False
        recent_play = le0 is not None and b.t - le0.t < cfg.serve_min_gap_s
        if label is None and between_points and not recent_play and not serve and cfg.serve_detection:
            sv = self.serve_of(b, fl)
            if sv is not None:
                label = "serve"
                out["serve"] = sv
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
        cur = _Prev(b.t, xy, fl["v_out"] if fl else None, label.startswith(("rally", "start of play", "serve")))
        self.prev = cur
        if cur.eligible:
            self.last_eligible = cur
            self.point_over = False
        else:  # second bounce, dead ball, ball handling: the point is over
            self.point_over = True
        if label == "dead ball":
            self.drops = [d for d in self.drops if b.t - d[0] <= cfg.drop_lookback_s] + [(b.t, xy)]
        out.update(play=label, announce_ok=ok, suppress=suppress)
        return out
