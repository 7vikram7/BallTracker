"""Automatic court calibration: find the court lines, propose every keypoint, the user reviews.

Clicking 14+ points per camera was the most tedious part of field test 2. A pickleball
court has a fixed shape, so the lines can be found automatically:

1. Line pixels: white paint is bright, unsaturated and thin (top-hat filter).
2. Line segments (probabilistic Hough), merged into long lines.
3. The court's lines run in two directions; in the image each direction's lines meet at
   a vanishing point. Lines are grouped by vanishing point (RANSAC) and ordered.
4. Hypotheses: two lines of each group are matched to two model lines of each direction
   (baselines / kitchen lines across the court; sidelines / centre line along it). Each
   gives a homography court -> image, scored by how many points sampled along ALL painted
   lines land on line pixels. Mirror images (impossible for a camera above the court)
   are rejected.
5. The best homography is refined by fitting every painted line to the pixels near its
   predicted position; keypoints come from the refined fit.

Side A vs side B: the court looks the same rotated 180 degrees, so lines alone cannot tell
the halves apart. Resolved, in order of preference, by
* a printed ArUco marker (DICT_4X4_50): id 0 placed behind baseline A, id 1 behind
  baseline B (scripts/make_markers.py prints them), anywhere the camera sees it;
* the camera's previous calibration (the proposal closest to where it was);
* otherwise: side A is the half nearer the camera, and the result is marked ambiguous
  (the dashboard offers a Flip button).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

import cv2
import numpy as np

from .court import CourtSpec

ALGO = "court_lines_autocal"
ALGO_VERSION = "0.1.0"

MARKER_DICT = cv2.aruco.DICT_4X4_50
MARKER_SIDE = {0: "A", 1: "B"}


@dataclass
class AutoCalResult:
    ok: bool
    points: dict[str, list[float]] = field(default_factory=dict)  # keypoint -> pixel, for review
    score: float = 0.0  # fraction of sampled line points that landed on line pixels
    side_from: str = ""  # "marker" | "previous" | "nearest-half"
    ambiguous: bool = False
    flipped_points: dict[str, list[float]] = field(default_factory=dict)  # the 180-degree alternative
    message: str = ""
    debug: dict = field(default_factory=dict)


# ----------------------------------------------------------------------------- model
def _model(court: CourtSpec):
    """Painted line centre-lines: (direction, coordinate, extent) and sample points."""
    hw, hl, k = court.half_w, court.half_l, court.kitchen_depth
    # Centre-lines of the paint, taken from the court definition (which side of the nominal
    # position each line's width lies on matters: 5 cm is ~14 px close to a camera).
    rect = {s.name: s.rect for s in court.lines()}
    cy = {n: (r.y0 + r.y1) / 2 for n, r in rect.items()}
    cx = {n: (r.x0 + r.x1) / 2 for n, r in rect.items()}
    across = {"baseline_A": cy["baseline_A"], "kitchen_A": cy["kitchen_A"], "kitchen_B": cy["kitchen_B"],
              "baseline_B": cy["baseline_B"]}
    along = {"sideline_left": cx["sideline_left"], "centre": cx["centreline_A"], "sideline_right": cx["sideline_right"]}
    samples = []
    for y in across.values():
        for x in np.linspace(-hw, hw, 40):
            samples.append((x, y))
    for name, x in along.items():
        if name == "centre":  # centre line only in the service courts (kitchen line to baseline)
            for y in list(np.linspace(-hl, -k, 15)) + list(np.linspace(k, hl, 15)):
                samples.append((x, y))
        else:
            for y in np.linspace(-hl, hl, 60):
                samples.append((x, y))
    return across, along, np.array(samples, float)


# ----------------------------------------------------------------------------- image
def line_mask(img: np.ndarray) -> np.ndarray:
    """Pixels of white court paint: much brighter than their surroundings, unsaturated."""
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    k = max(15, int(round(w / 45)) | 1)  # wider than the widest line (near lines ~20 px at 1080p)
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    m = (tophat > 22) & (hsv[..., 1] < 80) & (hsv[..., 2] > 110)
    m = m.astype(np.uint8) * 255
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    # A paint line has two edges; netting, fences and textured backgrounds have many. Drop mask
    # pixels in areas dense with edges.
    edges = cv2.Canny(m, 50, 150)
    win = max(31, (w // 30) | 1)
    density = cv2.boxFilter((edges > 0).astype(np.float32), -1, (win, win))
    m[density > 0.12] = 0
    # Too thick to be a line (bright sky, walls, roof panels): remove what survives an opening
    # with a disc wider than any line.
    d = max(25, (w // 70) | 1)
    blobs = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (d, d)))
    blobs = cv2.dilate(blobs, np.ones((9, 9), np.uint8))
    m[blobs > 0] = 0
    return m


def _segments(mask: np.ndarray) -> np.ndarray:
    h, w = mask.shape
    segs = cv2.HoughLinesP(mask, 1, np.pi / 720, threshold=40, minLineLength=max(30, w // 30), maxLineGap=max(8, w // 90))
    if segs is None:
        return np.zeros((0, 4))
    segs = np.asarray(segs, float).reshape(-1, 4)  # OpenCV 4: (n,1,4), 5: (n,4)
    L = np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1])
    return segs[np.argsort(-L)[:300]]


def _merge(segs: np.ndarray, w: int) -> list[dict]:
    """Merge collinear segments into lines (homogeneous a x + b y + c = 0, a^2 + b^2 = 1)."""
    lines: list[dict] = []
    order = np.argsort(-np.hypot(segs[:, 2] - segs[:, 0], segs[:, 3] - segs[:, 1]))
    for i in order:
        x1, y1, x2, y2 = segs[i]
        L = float(np.hypot(x2 - x1, y2 - y1))
        a, b = (y2 - y1) / L, -(x2 - x1) / L
        c = -(a * x1 + b * y1)
        for ln in lines:
            if abs(ln["a"] * a + ln["b"] * b) > np.cos(np.radians(1.5)):
                s = np.sign(ln["a"] * a + ln["b"] * b)
                # both endpoints close to the existing line
                d1 = abs(ln["a"] * x1 + ln["b"] * y1 + ln["c"])
                d2 = abs(ln["a"] * x2 + ln["b"] * y2 + ln["c"])
                # ... and close along the line too (don't join unrelated structures far apart)
                dirv = np.array([-ln["b"], ln["a"]])
                proj = np.array(ln["pts"]) @ dirv
                lo, hi = proj.min(), proj.max()
                s1, s2 = sorted((np.array([x1, y1]) @ dirv, np.array([x2, y2]) @ dirv))
                gap = max(0.0, s1 - hi, lo - s2)
                if max(d1, d2) < max(4.0, w / 400) and gap < w / 10:
                    ln["pts"] += [(x1, y1), (x2, y2)]
                    ln["len"] += L
                    _refit(ln)
                    break
        else:
            lines.append({"a": a, "b": b, "c": c, "len": L, "pts": [(x1, y1), (x2, y2)]})
    lines = [ln for ln in lines if ln["len"] > w / 12]
    return sorted(lines, key=lambda ln: -ln["len"])[:16]


def _refit(ln: dict) -> None:
    p = np.array(ln["pts"], np.float32)
    vx, vy, x0, y0 = cv2.fitLine(p, cv2.DIST_L2, 0, 0.01, 0.01).ravel()
    a, b = vy, -vx
    ln.update(a=float(a), b=float(b), c=float(-(a * x0 + b * y0)))


def _hom(ln: dict) -> np.ndarray:
    return np.array([ln["a"], ln["b"], ln["c"]], float)


def _consistent(ln: dict, vp: np.ndarray, tol_deg: float = 1.5) -> bool:
    p = np.mean(np.array(ln["pts"]), axis=0)
    d_line = np.array([-ln["b"], ln["a"]])
    if abs(vp[2]) < 1e-9 * max(1.0, np.hypot(vp[0], vp[1])):
        d_vp = vp[:2]
    else:
        d_vp = vp[:2] / vp[2] - p
    n = np.linalg.norm(d_vp)
    if n < 1e-9:
        return True
    cos = abs(d_line @ d_vp) / n
    # short segments have uncertain directions: allow ~5 px of end-point error
    tol = max(np.radians(tol_deg), np.arctan(5.0 / max(ln["len"] / 2, 1.0)))
    return cos > np.cos(tol)


def _vp_groups(lines: list[dict]) -> list[list[dict]]:
    """Two groups of lines sharing a vanishing point (RANSAC over pairs, weighted by length)."""
    groups = []
    rest = list(lines)
    for _ in range(2):
        best, best_sup = None, 0.0
        for l1, l2 in combinations(rest, 2):
            vp = np.cross(_hom(l1), _hom(l2))
            if np.allclose(vp, 0):
                continue
            sup = sum(ln["len"] for ln in rest if _consistent(ln, vp))
            if sup > best_sup:
                best, best_sup = vp, sup
        if best is None:
            break
        g = [ln for ln in rest if _consistent(ln, best)]
        for ln in g:
            ln["vp"] = best
        groups.append(g)
        rest = [ln for ln in rest if not any(ln is x for x in g)]
    return groups


def _order(group: list[dict], w: int, h: int) -> list[dict]:
    """Order a group's lines across the image (by where they cross a transversal)."""
    vp = group[0]["vp"]
    centre = np.array([w / 2, h / 2])
    if abs(vp[2]) > 1e-9:
        d = vp[:2] / vp[2] - centre
    else:
        d = vp[:2]
    d = d / max(np.linalg.norm(d), 1e-9)
    perp = np.array([-d[1], d[0]])
    # position of each line along the perpendicular through the image centre
    keys = []
    for ln in group:
        n = np.array([ln["a"], ln["b"]])
        den = n @ perp
        t = -(n @ centre + ln["c"]) / den if abs(den) > 1e-9 else 1e9
        keys.append(t)
    return [group[i] for i in np.argsort(keys)][:7]


def _intersect(l1: dict, l2: dict) -> np.ndarray | None:
    p = np.cross(_hom(l1), _hom(l2))
    if abs(p[2]) < 1e-9:
        return None
    return p[:2] / p[2]


# ----------------------------------------------------------------------------- search
def _score_many(Hs: np.ndarray, samples: np.ndarray, dist: np.ndarray) -> np.ndarray:
    """Fraction of model samples projecting onto line pixels (dist = distance transform)."""
    h, w = dist.shape
    P = np.c_[samples, np.ones(len(samples))]  # (m, 3)
    q = np.einsum("kij,mj->kmi", Hs, P)
    z = q[..., 2]
    ok = z > 1e-9
    u = np.where(ok, q[..., 0] / np.where(ok, z, 1), -1)
    v = np.where(ok, q[..., 1] / np.where(ok, z, 1), -1)
    inside = ok & (u >= 0) & (u < w - 1) & (v >= 0) & (v < h - 1)
    ui = np.clip(u, 0, w - 1).astype(int)
    vi = np.clip(v, 0, h - 1).astype(int)
    hit = inside & (dist[vi, ui] <= 2.5)
    n_in = inside.sum(1)
    # Precision with a coverage floor: predicted line points that land on nothing count against
    # the match, and a court that maps mostly outside the image is not credible.
    return hit.sum(1) / np.maximum(n_in, 0.35 * len(samples))


def _plausible(H: np.ndarray, court: CourtSpec, w: int, h: int) -> bool:
    """The court's outline projects to a convex, reasonably large quadrilateral in front of the camera."""
    hw, hl = court.half_w, court.half_l
    C = np.array([[-hw, -hl, 1], [hw, -hl, 1], [hw, hl, 1], [-hw, hl, 1]], float)
    q = (H @ C.T).T
    if np.any(q[:, 2] <= 0):
        return False
    p = q[:, :2] / q[:, 2:]
    if np.any(np.abs(p) > 6 * max(w, h)):
        return False
    area = 0.5 * abs(np.dot(p[:, 0], np.roll(p[:, 1], 1)) - np.dot(p[:, 1], np.roll(p[:, 0], 1)))
    if area < 0.12 * w * h:  # the protocol: each camera sees most of its half
        return False
    if min(np.hypot(*(p[i] - p[j])) for i in range(4) for j in range(i + 1, 4)) < 0.08 * w:
        return False
    def cross2(a, b):
        return a[0] * b[1] - a[1] * b[0]
    cross = [cross2(p[(i + 1) % 4] - p[i], p[(i + 2) % 4] - p[(i + 1) % 4]) for i in range(4)]
    return all(c > 0 for c in cross) or all(c < 0 for c in cross)


def _orientation_ok(H: np.ndarray, court: CourtSpec) -> bool:
    """A camera above the court sees it with det(J) < 0 (image v points down)."""
    x, y = 0.0, 0.0
    q = H @ np.array([x, y, 1.0])
    if q[2] <= 0:
        return False
    eps = 0.5
    def proj(px, py):
        r = H @ np.array([px, py, 1.0])
        return r[:2] / r[2]
    p0 = proj(x, y)
    J = np.column_stack([(proj(x + eps, y) - p0) / eps, (proj(x, y + eps) - p0) / eps])
    return float(np.linalg.det(J)) < 0


def _refine(H: np.ndarray, court: CourtSpec, mask: np.ndarray, iters: int = 3,
            bands: tuple[float, ...] = (30.0, 15.0, 6.0)) -> np.ndarray:
    """Fit each painted line to the line pixels near its prediction; re-solve H from intersections."""
    across, along, _ = _model(court)
    ys, xs = np.nonzero(mask)
    pix = np.c_[xs, ys].astype(float)
    if len(pix) == 0:
        return H
    hw, hl = court.half_w, court.half_l
    for it in range(max(iters, len(bands))):
        band = bands[min(it, len(bands) - 1)]
        fitted = {}
        for name, y in across.items():
            fitted[("y", name)] = _fit_line_near(H, pix, [(-hw, y), (hw, y)], band)
        for name, x in along.items():
            ext = [(x, -hl), (x, hl)] if name != "centre" else [(x, court.kitchen_depth), (x, hl)]
            fitted[("x", name)] = _fit_line_near(H, pix, ext, band)
            if name == "centre":
                fitted[("x", "centre_A")] = _fit_line_near(H, pix, [(x, -hl), (x, -court.kitchen_depth)], band)
        src, dst = [], []
        for (_, an), yv in ((k, across[k[1]]) for k in fitted if k[0] == "y"):
            la = fitted[("y", an)]
            if la is None:
                continue
            for xn, xv in along.items():
                key = ("x", "centre_A") if (xn == "centre" and yv < 0) else ("x", xn)
                lb = fitted.get(key)
                if lb is None or (xn == "centre" and "kitchen" not in an and "baseline" not in an):
                    continue
                p = np.cross(la, lb)
                if abs(p[2]) < 1e-9:
                    continue
                src.append((xv, yv))
                dst.append(p[:2] / p[2])
        if len(src) < 4:
            break
        H2, _ = cv2.findHomography(np.array(src, np.float64), np.array(dst, np.float64), 0)
        if H2 is None:
            break
        H = H2
    return H


def _line_segments_model(court: CourtSpec) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    """Painted line centre-line segments (model coordinates), as drawn on the court."""
    across, along, _ = _model(court)
    hw, hl, k = court.half_w, court.half_l, court.kitchen_depth
    segs = [((-hw, y), (hw, y)) for y in across.values()]
    for name, x in along.items():
        if name == "centre":
            segs += [((x, -hl), (x, -k)), ((x, k), (x, hl))]
        else:
            segs.append(((x, -hl), (x, hl)))
    return segs


def refine_lsq(H: np.ndarray, court: CourtSpec, mask: np.ndarray, bands: tuple[float, ...] = (25.0, 10.0, 5.0),
               per_line: int = 400) -> np.ndarray:
    """Fit the homography to the line pixels directly: for every painted line, the pixels near its
    predicted position should lie on it (robust loss, so the net's tapes, shoes, shadows near a
    line do not pull it). Shrinking search bands make it converge from a rough start."""
    from scipy.optimize import least_squares

    ys, xs = np.nonzero(mask)
    pix = np.c_[xs, ys].astype(float)
    if len(pix) == 0:
        return H
    segs = _line_segments_model(court)
    rng = np.random.default_rng(0)
    Hn = H / H[2, 2]
    for band in bands:
        groups = []
        for (p0, p1) in segs:
            a = Hn @ np.array([*p0, 1.0])
            b = Hn @ np.array([*p1, 1.0])
            if a[2] <= 0 or b[2] <= 0:
                continue
            a, b = a[:2] / a[2], b[:2] / b[2]
            L = np.linalg.norm(b - a)
            if L < 20:
                continue
            d = (b - a) / L
            n = np.array([-d[1], d[0]])
            rel = pix - a
            al, off = rel @ d, rel @ n
            sel = np.nonzero((np.abs(off) < band) & (al > 0.03 * L) & (al < 0.97 * L))[0]
            if len(sel) < 15:
                continue
            if len(sel) > per_line:
                sel = rng.choice(sel, per_line, replace=False)
            groups.append((p0, p1, pix[sel]))
        if len(groups) < 4:
            break

        def resid(h8):
            Hm = np.append(h8, 1.0).reshape(3, 3)
            out = []
            for p0, p1, P in groups:
                a = Hm @ np.array([*p0, 1.0])
                b = Hm @ np.array([*p1, 1.0])
                if a[2] <= 1e-9 or b[2] <= 1e-9:
                    out.append(np.full(len(P), 1e3))
                    continue
                a, b = a[:2] / a[2], b[:2] / b[2]
                d = b - a
                L = np.hypot(*d)
                out.append(((P[:, 0] - a[0]) * d[1] - (P[:, 1] - a[1]) * d[0]) / max(L, 1e-9))
            return np.concatenate(out)

        r = least_squares(resid, Hn.ravel()[:8], loss="soft_l1", f_scale=2.0, max_nfev=200, x_scale="jac")
        Hn = np.append(r.x, 1.0).reshape(3, 3)
    return Hn


def _fit_line_near(H: np.ndarray, pix: np.ndarray, ends: list[tuple[float, float]], band: float = 6.0):
    a, b = (H @ np.array([*ends[0], 1.0])), (H @ np.array([*ends[1], 1.0]))
    if a[2] <= 0 or b[2] <= 0:
        return None
    a, b = a[:2] / a[2], b[:2] / b[2]
    d = b - a
    L = np.linalg.norm(d)
    if L < 20:
        return None
    d /= L
    n = np.array([-d[1], d[0]])
    rel = pix - a
    along = rel @ d
    off = rel @ n
    sel = (np.abs(off) < band) & (along > 0) & (along < L)
    if sel.sum() < max(15, 0.15 * L):
        return None
    p = pix[sel].astype(np.float32)
    vx, vy, x0, y0 = cv2.fitLine(p, cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    la, lb = vy, -vx
    return np.array([la, lb, -(la * x0 + lb * y0)], float)


def refine_from(img: np.ndarray, court: CourtSpec, init_points: dict[str, list[float]]) -> AutoCalResult:
    """Snap a rough calibration to the court lines: from >= 4 named points (rough clicks, or the
    keypoints of the camera's previous calibration) to every keypoint, precisely. The names fix
    which half is A, so there is no ambiguity."""
    h, w = img.shape[:2]
    kp = court.keypoints()
    names = [k for k in init_points if k in kp and kp[k][2] == 0 and "net_" not in k]
    if len(names) < 4:
        return AutoCalResult(False, message="need at least 4 ground points to start from")
    H0, _ = cv2.findHomography(np.array([kp[k][:2] for k in names], np.float64),
                               np.array([init_points[k] for k in names], np.float64), 0)
    if H0 is None:
        return AutoCalResult(False, message="those points do not define a court")
    mask = line_mask(img)
    _, _, samples = _model(court)
    dist = cv2.distanceTransform(255 - mask, cv2.DIST_L2, 3)
    H = refine_lsq(H0, court, mask, bands=(30.0, 15.0, 8.0, 5.0))
    score = float(_score_many(H[None], samples, dist)[0])
    score0 = float(_score_many(H0[None], samples, dist)[0])
    if score < score0:  # the snap made it worse: keep the starting point
        H, score = H0, score0
    pts = _project_keypoints(H, court, w, h)
    ok = score > 0.35 and len(pts) >= 4
    return AutoCalResult(ok, pts, round(score, 3), "given points", False, {},
                         "" if ok else f"weak match (score {score:.2f}): check the points by hand",
                         {"start_score": round(score0, 3)})


def _project_keypoints(H: np.ndarray, court: CourtSpec, w: int, h: int) -> dict[str, list[float]]:
    out = {}
    for name, (x, y, z) in court.keypoints().items():
        if z != 0 or "net_" in name:
            continue
        q = H @ np.array([x, y, 1.0])
        if q[2] > 0:
            u, v = q[:2] / q[2]
            if -0.02 * w <= u <= 1.02 * w and -0.02 * h <= v <= 1.02 * h:
                out[name] = [round(float(u), 2), round(float(v), 2)]
    return out


def detect_markers(img: np.ndarray) -> dict[int, np.ndarray]:
    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(MARKER_DICT), cv2.aruco.DetectorParameters())
    corners, ids, _ = det.detectMarkers(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY))
    out = {}
    if ids is not None:
        for c, i in zip(corners, ids.ravel()):
            if int(i) in MARKER_SIDE:
                out[int(i)] = c[0].mean(axis=0)
    return out


def autocalibrate(img: np.ndarray, court: CourtSpec, previous_position: np.ndarray | None = None,
                  max_hypotheses: int = 60000) -> AutoCalResult:
    """Propose keypoint pixels for ``img`` (BGR). See the module docstring."""
    h, w = img.shape[:2]
    mask = line_mask(img)
    lines = _merge(_segments(mask), w)
    if len(lines) < 4:
        return AutoCalResult(False, message=f"found only {len(lines)} court lines: is the court in view and lit?")
    groups = _vp_groups(lines)
    if len(groups) < 2 or min(len(g) for g in groups) < 2:
        return AutoCalResult(False, message="could not find the court's two line directions")
    g1, g2 = (_order(g, w, h) for g in groups)
    across, along, samples = _model(court)
    ys = list(across.values())
    xs = list(along.values())
    dist = cv2.distanceTransform(255 - mask, cv2.DIST_L2, 3)

    src_list, H_list = [], []
    for ga, gb in ((g1, g2), (g2, g1)):  # which group runs across the court
        for i, j in combinations(range(len(ga)), 2):
            for k, l in combinations(range(len(gb)), 2):
                P = [_intersect(ga[i], gb[k]), _intersect(ga[i], gb[l]), _intersect(ga[j], gb[k]), _intersect(ga[j], gb[l])]
                if any(p is None for p in P) or any(np.any(np.abs(p) > 20 * max(w, h)) for p in P):
                    continue
                dst = np.array(P, np.float32)
                for yi, yj in combinations(ys, 2):
                    for xk, xl in combinations(xs, 2):
                        for (ya, yb) in ((yi, yj), (yj, yi)):
                            for (xa, xb) in ((xk, xl), (xl, xk)):
                                src = np.array([(xa, ya), (xb, ya), (xa, yb), (xb, yb)], np.float32)
                                src_list.append(src)
                                H_list.append(cv2.getPerspectiveTransform(src, dst))
                if len(H_list) > max_hypotheses:
                    break
    if not H_list:
        return AutoCalResult(False, message="no consistent line arrangement found")
    Hs = np.array(H_list)
    scores = _score_many(Hs, samples, dist)
    order = np.argsort(-scores)
    chosen = []
    for idx in order[:2000]:
        if _orientation_ok(Hs[idx], court) and _plausible(Hs[idx], court, w, h):
            chosen.append(idx)
            if len(chosen) >= 1:
                break
    if not chosen:
        return AutoCalResult(False, message="no physically possible court found")
    H = refine_lsq(Hs[chosen[0]], court, mask, bands=(30.0, 15.0, 8.0, 5.0))
    score = float(_score_many(H[None], samples, dist)[0])
    # The 180-degree alternative: same lines, halves swapped.
    R = np.diag([-1.0, -1.0, 1.0])
    H_alt = H @ R
    kp = {k: v for k, v in court.keypoints().items() if v[2] == 0 and "net_" not in k}

    def pts_of(Hm):
        out = {}
        for name, (x, y, _) in kp.items():
            q = Hm @ np.array([x, y, 1.0])
            if q[2] > 0:
                u, v = q[:2] / q[2]
                if -0.02 * w <= u <= 1.02 * w and -0.02 * h <= v <= 1.02 * h:
                    out[name] = [round(float(u), 2), round(float(v), 2)]
        return out

    pts, alt = pts_of(H), pts_of(H_alt)
    side_from, ambiguous = "", False
    markers = detect_markers(img)
    if markers:
        Hi = np.linalg.inv(H)
        votes = 0
        for mid, px in markers.items():
            q = Hi @ np.array([px[0], px[1], 1.0])
            y = q[1] / q[2] if abs(q[2]) > 1e-9 else 0.0
            want_negative = MARKER_SIDE[mid] == "A"
            votes += 1 if (y < 0) == want_negative else -1
        if votes < 0:
            pts, alt = alt, pts
        side_from = "marker"
    elif previous_position is not None:
        cA, cB = _camera_xy(pts, court, (w, h)), _camera_xy(alt, court, (w, h))
        if cA is not None and cB is not None and \
                np.hypot(*(cB - previous_position[:2])) < np.hypot(*(cA - previous_position[:2])):
            pts, alt = alt, pts
        side_from = "previous"
    else:
        cA = _camera_xy(pts, court, (w, h))
        if cA is not None and cA[1] > 0:  # make side A the half nearer the camera
            pts, alt = alt, pts
        side_from, ambiguous = "nearest-half", True
    ok = score > 0.35 and len(pts) >= 4
    return AutoCalResult(ok, pts, round(score, 3), side_from, ambiguous, alt,
                         "" if ok else f"weak match (score {score:.2f}): click the points by hand",
                         {"lines": len(lines), "groups": [len(g1), len(g2)], "hypotheses": len(H_list),
                          "markers": {int(k): [float(v[0]), float(v[1])] for k, v in markers.items()}})


def _camera_xy(pts: dict[str, list[float]], court: CourtSpec, size: tuple[int, int]) -> np.ndarray | None:
    """Camera ground position from proposed keypoints (a full calibration from them)."""
    from .camera import CalibrationError, calibrate_from_points

    kp = court.keypoints()
    names = [k for k in pts if k in kp]
    if len(names) < 4:
        return None
    try:
        cam = calibrate_from_points(np.array([kp[k] for k in names]), np.array([pts[k] for k in names]), size,
                                    estimate_focal=len(names) >= 6)
    except CalibrationError:
        return None
    return np.asarray(cam.position, float)[:2]
