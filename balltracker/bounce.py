"""Single-camera bounce detection with sub-frame timing and uncertainty.

Idea
----
Between contacts the ball follows a smooth (near-parabolic) path, and so does
its image. A bounce is a *kink*: the trajectory before and after are two smooth
curves meeting at the contact. For every candidate split between consecutive
frames we fit a quadratic-in-time curve to the W samples before and the W
samples after, and ask:

1. Do two curves explain the data much better than one? (``gain``)
2. Do the two curves meet between the two frames? -> sub-frame contact time
   ``tb`` and contact pixel (where the curves meet). This is how a bounce that
   happened *between* frames is recovered.
3. Is the velocity change an upward impulse? At a bounce the surface pushes the
   ball up, so the image-velocity jump must point along the image of the +Z
   direction at that spot. This rejects most paddle contacts and tracker noise.

Ground position
---------------
At contact the ball centre is one radius above the surface. The contact pixel
is turned into a viewing ray and intersected with the plane z = r; the contact
point is directly below. (Mapping the centre through a ground homography would
overshoot along the ray.)

Uncertainty
-----------
Parametric bootstrap: the fitted curves' residuals give the per-sample pixel
noise; we resample noisy tracks, re-estimate the contact, and add calibration
error (the calibration's reprojection RMS) as pixel jitter. The spread of the
resulting ground points is the reported covariance. This is a model-based
estimate - it must be validated against chalk-mark ground truth.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .events import BounceEvent, Point3, Provenance
from .geometry.camera import Camera
from .geometry.court import CourtSpec
from .tracking import Track

ALGO = "kink_bounce"
ALGO_VERSION = "0.3.0"


@dataclass
class BounceConfig:
    window_s: float = 0.06  # seconds of track used on each side of a split
    min_side_points: int = 5
    # F-statistic of "two curves" vs "one curve" (nested least squares models).
    gain_threshold: float = 6.0
    sigma0_px: float = 0.15  # residual floor so perfect fits don't give infinite F
    min_up_cos: float = 0.5
    min_dv_px_s: float = 40.0
    nms_s: float = 0.12
    max_court_margin_m: float = 4.0  # ignore "bounces" far off the court
    bootstrap: int = 200
    seed: int = 0
    # Physical plausibility of a *ground* contact (see ``ballistic_check``).
    # Limits are loose on purpose: spin and skid on real courts change speeds.
    physics_check: bool = True
    physics_window_s: float = 0.15
    min_vz_in: float = 1.0  # m/s downward before contact
    min_vz_out: float = 0.3  # m/s upward after
    e_range: tuple[float, float] = (0.1, 1.0)
    h_ratio_range: tuple[float, float] = (0.3, 2.5)  # along-the-view speed is poorly observed by one camera
    max_turn_deg: float = 60.0  # catches paddle hits (direction reverses), not spin
    max_fit_px: float = 2.5  # or 3x the 2D fit noise, whichever is larger


def _lsq(A: np.ndarray, Y: np.ndarray) -> np.ndarray:
    """Least squares via the normal equations (tiny systems: much less overhead
    than ``lstsq``). Times are seconds relative to the window, so the system is
    well conditioned; fall back to ``lstsq`` if not."""
    AtA = A.T @ A
    try:
        return np.linalg.solve(AtA, A.T @ Y)
    except np.linalg.LinAlgError:
        return np.linalg.lstsq(A, Y, rcond=None)[0]


def _fit(t: np.ndarray, uv: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """Quadratic fits for u(t), v(t); returns coeffs (2,3) highest power first, residuals, SSE."""
    A = np.column_stack([t * t, t, np.ones_like(t)])
    c = _lsq(A, uv)  # (3, 2)
    res = uv - A @ c
    return c.T.copy(), res, float(np.sum(res**2))


def _meet(cl: np.ndarray, cr: np.ndarray, lo: float, hi: float, n: int = 64) -> tuple[float, np.ndarray, float]:
    """Time in [lo, hi] where left and right curves are closest."""
    ts = np.linspace(lo, hi, n)
    pl = np.stack([np.polyval(cl[0], ts), np.polyval(cl[1], ts)], axis=1)
    pr = np.stack([np.polyval(cr[0], ts), np.polyval(cr[1], ts)], axis=1)
    gap = np.linalg.norm(pl - pr, axis=1)
    k = int(np.argmin(gap))
    return float(ts[k]), (pl[k] + pr[k]) / 2, float(gap[k])


def _vel(c: np.ndarray, t: float) -> np.ndarray:
    return np.array([np.polyval(np.polyder(c[0]), t), np.polyval(np.polyder(c[1]), t)])


def _joint_fit(t: np.ndarray, uv: np.ndarray, tb: float) -> tuple[np.ndarray, float]:
    """Two quadratics that share their value at the contact time ``tb``.

    p(t) = P0 + a1*(t-tb) + b1*(t-tb)^2   for t <  tb
    p(t) = P0 + a2*(t-tb) + b2*(t-tb)^2   for t >= tb
    Linear in (P0, a1, b1, a2, b2) for fixed tb. Returns coef (5, 2) and SSE.
    """
    d = t - tb
    lm = (d < 0).astype(float)
    rm = 1.0 - lm
    A = np.column_stack([np.ones_like(d), d * lm, d * d * lm, d * rm, d * d * rm])
    coef = _lsq(A, uv)
    res = uv - A @ coef
    return coef, float(np.sum(res**2))


def _joint_sse_batch(t: np.ndarray, uv: np.ndarray, tbs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``_joint_fit`` for many contact times at once (same normal equations, batched):
    returns coefs (k, 5, 2) and SSEs (k,). Live mode spends most of its time here."""
    d = t[None, :] - tbs[:, None]
    lm = (d < 0).astype(float)
    rm = 1.0 - lm
    A = np.stack([np.ones_like(d), d * lm, d * d * lm, d * rm, d * d * rm], axis=-1)  # (k, m, 5)
    AtA = np.einsum("kmi,kmj->kij", A, A)
    AtY = np.einsum("kmi,mc->kic", A, uv)
    coef = np.linalg.solve(AtA, AtY)  # (k, 5, 2)
    res = uv[None, :, :] - A @ coef
    return coef, np.einsum("kmc,kmc->k", res, res)


def _best_joint(t: np.ndarray, uv: np.ndarray, lo: float, hi: float, n: int = 13, refine: int = 9):
    """Continuous search for the contact time in [lo, hi] (grid + local refine)."""
    grid = np.linspace(lo, hi, n)
    try:
        coefs, sses = _joint_sse_batch(t, uv, grid)
    except np.linalg.LinAlgError:
        return _best_joint_loop(t, uv, lo, hi, n, refine)
    k = int(np.argmin(sses))  # first minimum, as the sequential search
    best = (float(grid[k]), float(sses[k]), coefs[k])
    step = (hi - lo) / max(n - 1, 1)
    fine = np.linspace(best[0] - step, best[0] + step, refine)
    fine = fine[(fine >= lo) & (fine <= hi)]
    if len(fine):
        try:
            coefs, sses = _joint_sse_batch(t, uv, fine)
        except np.linalg.LinAlgError:
            return _best_joint_loop(t, uv, lo, hi, n, refine)
        k = int(np.argmin(sses))
        if sses[k] < best[1]:
            best = (float(fine[k]), float(sses[k]), coefs[k])
    return best


def _best_joint_loop(t: np.ndarray, uv: np.ndarray, lo: float, hi: float, n: int = 13, refine: int = 9):
    """Reference (one fit at a time, with the lstsq fallback for degenerate windows)."""
    best = None
    grid = np.linspace(lo, hi, n)
    for tb in grid:
        coef, sse = _joint_fit(t, uv, tb)
        if best is None or sse < best[1]:
            best = (float(tb), sse, coef)
    step = (hi - lo) / max(n - 1, 1)
    for tb in np.linspace(best[0] - step, best[0] + step, refine):
        if lo <= tb <= hi:
            coef, sse = _joint_fit(t, uv, tb)
            if sse < best[1]:
                best = (float(tb), sse, coef)
    return best


G = 9.81


def ballistic_check(camera: Camera, t: np.ndarray, uv: np.ndarray, tb: float, P: np.ndarray) -> dict:
    """Is this kink physically a ground contact at P (ball centre, z = r)?

    Assume it is: on each side the ball then follows X(t) = P + v*(t-tb) - g/2*(t-tb)^2 * z.
    For a fixed P the projection constraints are linear in the 3D velocity v, so
    each side is a small linear least-squares problem (gravity supplies the scale).
    A true bounce gives: descending before, rising after, restitution in a sane
    range, horizontal direction roughly kept, and a good reprojection fit.
    A paddle hit, net/post hit or a mid-air kink wrongly placed on the ground
    fails one of these.
    """
    M = camera.K @ np.column_stack([camera.R, camera.t])
    out: dict = {}
    for name, m in (("in", t < tb), ("out", t >= tb)):
        if m.sum() < 3:
            return {"ok": False, "reason": f"too few points {name}"}
        d = t[m] - tb
        rows, rhs = [], []
        scale = 1.0 / max(float(M[2, :3] @ P + M[2, 3]), 1e-6)  # ~ 1/depth: algebraic -> pixel-like error
        for (u, v), di in zip(uv[m], d):
            for a in (M[0] - u * M[2], M[1] - v * M[2]):
                a3, a4 = a[:3], a[3]
                rows.append(scale * di * a3)
                rhs.append(-scale * (a3 @ P - 0.5 * G * di * di * a3[2] + a4))
        A, b = np.array(rows), np.array(rhs)
        vel = np.linalg.lstsq(A, b, rcond=None)[0]
        X = P[None, :] + d[:, None] * vel[None, :] - 0.5 * G * (d * d)[:, None] * np.array([0, 0, 1.0])
        ok_depth = camera.depth(X) > 0.1
        if not np.all(ok_depth):
            return {"ok": False, "reason": "behind camera"}
        res = camera.project(X) - uv[m]
        out[name] = (vel, float(np.sqrt(np.mean(np.sum(res**2, axis=1)) / 2)))
    vi, ri = out["in"]
    vo, ro = out["out"]
    hi, ho = np.hypot(vi[0], vi[1]), np.hypot(vo[0], vo[1])
    e = vo[2] / -vi[2] if vi[2] < 0 else float("inf")
    ang = float(np.degrees(np.arccos(np.clip((vi[:2] @ vo[:2]) / max(hi * ho, 1e-9), -1, 1)))) if hi > 0.5 and ho > 0.5 else 0.0
    return {"vz_in": float(vi[2]), "vz_out": float(vo[2]), "e": float(e), "h_ratio": float(ho / max(hi, 1e-9)),
            "turn_deg": ang, "rms_in_px": ri, "rms_out_px": ro, "v_in": vi.tolist(), "v_out": vo.tolist()}


def _image_up(camera: Camera, px: np.ndarray, z: float) -> np.ndarray | None:
    p = camera.intersect_plane_z(px.reshape(1, 2), z)[0]
    if not np.all(np.isfinite(p)):
        return None
    a, b = camera.project(np.array([p, p + np.array([0, 0, 0.25])]))
    d = b - a
    n = np.linalg.norm(d)
    return d / n if n > 0 else None


class BounceDetector:
    def __init__(self, camera: Camera, court: CourtSpec, cfg: BounceConfig | None = None):
        self.camera = camera
        self.court = court
        self.cfg = cfg or BounceConfig()
        self._rng = np.random.default_rng(self.cfg.seed)

    def provenance(self) -> Provenance:
        c = self.cfg
        return Provenance(
            algorithm=ALGO,
            version=ALGO_VERSION,
            params={k: getattr(c, k) for k in ("window_s", "min_side_points", "gain_threshold", "sigma0_px", "min_up_cos", "bootstrap")},
        )

    # ------------------------------------------------------------------
    def detect(self, track: Track) -> list[BounceEvent]:
        cands, t, uv = self.candidates(track)
        out: list[BounceEvent] = []
        for c in cands:
            ev = self.finalise(c, t, uv, track)
            if ev is not None:
                out.append(ev)
        return out

    def candidates(self, track: Track, t_from: float | None = None) -> tuple[list[dict], np.ndarray, np.ndarray]:
        """Cheap part: detected, refined contact candidates (``c['tb']`` = contact time),
        without the bootstrap uncertainty. Live mode screens these first and only
        finalises the ones it is about to emit."""
        cfg = self.cfg
        pts = track.points
        n = len(pts)
        if n < 2 * cfg.min_side_points:
            return [], np.zeros(0), np.zeros((0, 2))
        t = np.array([p.t for p in pts])
        uv = np.array([[p.u, p.v] for p in pts])
        r = self.court.ball_radius

        cands = []
        for s in range(cfg.min_side_points - 1, n - cfg.min_side_points):
            if t_from is not None and t[s + 1] < t_from:
                continue  # already scanned in an earlier (live) pass
            lo_i = int(np.searchsorted(t, t[s] - cfg.window_s, "left"))
            hi_i = int(np.searchsorted(t, t[s + 1] + cfg.window_s, "right"))
            lo_i = min(lo_i, s + 1 - cfg.min_side_points)
            hi_i = max(hi_i, s + 1 + cfg.min_side_points)
            if lo_i < 0 or hi_i > n:
                continue
            W = slice(lo_i, hi_i)
            t0 = t[s]
            tw, uvw = t[W] - t0, uv[W]
            npts = len(tw)
            dof = 2 * npts - 10  # 2 coords x 5 params (shared contact point)
            if dof <= 0:
                continue
            _, _, sse1 = _fit(tw, uvw)
            floor = cfg.sigma0_px**2 * 2 * npts
            # Cheap screen at the mid-gap before the continuous search.
            mid = 0.5 * (t[s + 1] - t0)
            _, sse_mid = _joint_fit(tw, uvw, mid)
            if ((sse1 - sse_mid) / 4) / (max(sse_mid, floor) / dof) < cfg.gain_threshold / 3:
                continue
            tb, sse2, coef = _best_joint(tw, uvw, 0.0, t[s + 1] - t0)
            gain = ((sse1 - sse2) / 4) / (max(sse2, floor) / dof)
            if gain < cfg.gain_threshold:
                continue
            pix = coef[0]
            dv = coef[3] - coef[1]
            ndv = float(np.linalg.norm(dv))
            if ndv < cfg.min_dv_px_s:
                continue
            up = _image_up(self.camera, pix, r)
            if up is None:
                continue
            cos = float(dv @ up / ndv)
            if cos < cfg.min_up_cos:
                continue
            noise = float(np.sqrt(sse2 / dof))
            cands.append(dict(s=s, gain=gain, tb=tb + t0, pix=pix, cos=cos, W=W, t0=t0, noise=noise))

        # Non-maximum suppression in time.
        cands.sort(key=lambda c: -c["gain"])
        kept: list[dict] = []
        for c in cands:
            if all(abs(c["tb"] - k["tb"]) > cfg.nms_s for k in kept):
                kept.append(c)
        kept.sort(key=lambda c: c["tb"])

        return [self._refine(c, t, uv) for c in kept], t, uv

    def finalise(self, c: dict, t: np.ndarray, uv: np.ndarray, track: Track) -> BounceEvent | None:
        return self._finalise(c, t, uv, track)

    def _plausible(self, ph: dict, noise: float) -> bool:
        cfg = self.cfg
        if ph.get("ok") is False:
            ph["rejected"] = ph.get("reason", "fit failed")
            return False
        fit_lim = max(cfg.max_fit_px, 3.0 * noise)
        checks = [
            (ph["vz_in"] <= -cfg.min_vz_in, "not descending before contact"),
            (ph["vz_out"] >= cfg.min_vz_out, "not rising after contact"),
            (cfg.e_range[0] <= ph["e"] <= cfg.e_range[1], "implausible restitution"),
            (np.hypot(*ph["v_in"][:2]) < 1.0 or cfg.h_ratio_range[0] <= ph["h_ratio"] <= cfg.h_ratio_range[1],
             "implausible horizontal speed change"),
            (ph["turn_deg"] <= cfg.max_turn_deg, "direction changed too much"),
            (max(ph["rms_in_px"], ph["rms_out_px"]) <= fit_lim, "trajectory not consistent with a ground contact"),
        ]
        for ok, why in checks:
            if not ok:
                ph["rejected"] = why
                return False
        return True

    # ------------------------------------------------------------------
    def _refine(self, c: dict, t: np.ndarray, uv: np.ndarray) -> dict:
        """Refit with a window centred on the coarse contact time, so the estimate
        doesn't depend on which shifted window happened to win the scan."""
        cfg = self.cfg
        tb0 = c["tb"]
        lo_i = int(np.searchsorted(t, tb0 - cfg.window_s, "left"))
        hi_i = int(np.searchsorted(t, tb0 + cfg.window_s, "right"))
        if hi_i - lo_i < 2 * cfg.min_side_points:
            return c
        W = slice(lo_i, hi_i)
        dt = float(np.median(np.diff(t[W])))
        tw, uvw = t[W] - tb0, uv[W]
        half = max(1.5 * dt, 0.015)  # search at least +/-15 ms around the coarse estimate
        tb, sse2, coef = _best_joint(tw, uvw, -half, half, n=25, refine=9)
        # Keep the bootstrap search range around the refined estimate.
        s = int(np.clip(np.searchsorted(t, tb0 + tb) - 1, 1, len(t) - 3))
        dof = max(1, 2 * len(tw) - 10)
        return dict(c, tb=tb + tb0, pix=coef[0], W=W, t0=tb0, s=s, noise=float(np.sqrt(sse2 / dof)))

    # ------------------------------------------------------------------
    def _finalise(self, c: dict, t: np.ndarray, uv: np.ndarray, track: Track) -> BounceEvent | None:
        cfg = self.cfg
        r = self.court.ball_radius
        P = self.camera.intersect_plane_z(c["pix"].reshape(1, 2), r)[0]
        if not np.all(np.isfinite(P)):
            return None
        rect = self.court.court_rect()
        if float(rect.distance_outside(np.array(P[0]), np.array(P[1]))) > cfg.max_court_margin_m:
            return None
        physics: dict = {}
        if cfg.physics_check:
            m = np.abs(t - c["tb"]) <= cfg.physics_window_s
            physics = ballistic_check(self.camera, t[m], uv[m], c["tb"], P)
            if not self._plausible(physics, c.get("noise", 0.0)):
                return None

        # Parametric bootstrap: resample noisy tracks, refit (contact time free to
        # move into neighbouring frame gaps), add calibration jitter.
        W, t0, s = c["W"], c["t0"], c["s"]
        tw, uvw = t[W] - t0, uv[W]
        sigma = max(c["noise"], 0.25)
        cal = float(self.camera.reprojection_rms_px or 0.0)
        lo = t[max(s - 1, 0)] - t0
        hi = t[min(s + 2, len(t) - 1)] - t0
        samples_xy, samples_t = [], []
        for _ in range(cfg.bootstrap):
            noisy = uvw + self._rng.normal(0, sigma, uvw.shape)
            tb, _, coef = _best_joint(tw, noisy, lo, hi, n=9, refine=5)
            pix = coef[0] + self._rng.normal(0, cal, 2)
            Q = self.camera.intersect_plane_z(pix.reshape(1, 2), r)[0]
            if np.all(np.isfinite(Q)):
                samples_xy.append(Q[:2])
                samples_t.append(tb + t0)
        if len(samples_xy) < 10:
            return None
        S = np.array(samples_xy)
        cov = np.cov(S.T)
        conf = float(1 / (1 + np.exp(-(c["gain"] - cfg.gain_threshold) / cfg.gain_threshold)) * min(1.0, c["cos"] / 0.9))
        obs_ids = [p.obs_id for p in track.points[W] if p.obs_id]
        return BounceEvent(
            t=float(c["tb"]),
            t_std=float(np.std(samples_t)),
            position=Point3(x=float(P[0]), y=float(P[1]), z=0.0),
            cov_xy=cov.tolist(),
            pixel=(float(c["pix"][0]), float(c["pix"][1])),
            camera_ids=[self.camera.camera_id],
            confidence=float(np.clip(conf, 0, 1)),
            supporting_observations=obs_ids,
            provenance=Provenance(algorithm=ALGO, version=ALGO_VERSION,
                                  params={**self.provenance().params,
                                          "physics": {k: (round(v, 3) if isinstance(v, float) else v) for k, v in physics.items()
                                                      if k not in ("v_in", "v_out")}}),
        )
