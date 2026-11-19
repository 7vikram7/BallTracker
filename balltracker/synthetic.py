"""Synthetic court videos with exact ground truth.

Purpose: exercise and measure the whole pipeline (detection -> tracking ->
bounce -> line call) BEFORE real footage exists, and answer design questions
quantitatively (frame rate, resolution, camera height/placement) under
controlled conditions.

What is simulated: pinhole camera (from a preset or explicit pose), a court
texture with real line widths, ball flight with gravity + quadratic drag, bounce
with restitution and friction, motion blur over a configurable shutter time,
sensor noise and optional calibration "click" error.

What is NOT simulated (so synthetic results are an upper bound on real-world
accuracy): players and occlusion, lighting changes, shadows, spin, rolling
shutter, lens distortion, compression artefacts beyond the encoder used, camera
shake, other balls.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

from .geometry.camera import Camera
from .geometry.court import CourtSpec

G = 9.81


# --------------------------------------------------------------------- physics
@dataclass
class BallPhysics:
    mass: float = 0.026  # kg (pickleball outdoor ball ~26 g)
    drag_cd: float = 0.45
    air_density: float = 1.2
    restitution: float = 0.62  # vertical
    friction: float = 0.82  # horizontal speed retained at bounce

    def k(self, radius: float) -> float:
        return 0.5 * self.air_density * self.drag_cd * np.pi * radius**2 / self.mass


@dataclass
class Shot:
    start: np.ndarray  # (3,) launch position
    velocity: np.ndarray  # (3,) launch velocity
    t_start: float  # session time of launch
    duration: float  # how long the ball stays in play / visible


@dataclass
class TrueBounce:
    t: float
    x: float
    y: float
    shot_index: int
    bounce_index_in_shot: int


def simulate(shot: Shot, radius: float, phys: BallPhysics, dt: float = 1 / 4800) -> tuple[np.ndarray, np.ndarray, list[tuple[float, float, float]]]:
    """Integrate a shot. Returns times, positions (N,3), bounces [(t, x, y)]."""
    k = phys.k(radius)
    n = int(np.ceil(shot.duration / dt)) + 1
    ts = shot.t_start + np.arange(n) * dt
    pos = np.zeros((n, 3))
    p = shot.start.astype(float).copy()
    v = shot.velocity.astype(float).copy()
    bounces = []
    for i in range(n):
        pos[i] = p
        sp = np.linalg.norm(v)
        a = np.array([0.0, 0.0, -G]) - k * sp * v
        v_new = v + a * dt
        p_new = p + v * dt + 0.5 * a * dt * dt
        if p_new[2] < radius and v_new[2] < 0:
            # Exact contact time inside the step (linear interpolation of height).
            frac = (p[2] - radius) / max(p[2] - p_new[2], 1e-12)
            frac = float(np.clip(frac, 0, 1))
            pc = p + (p_new - p) * frac
            tc = ts[i] + frac * dt
            bounces.append((tc, pc[0], pc[1]))
            vc = v + (v_new - v) * frac
            vc = np.array([vc[0] * phys.friction, vc[1] * phys.friction, -vc[2] * phys.restitution])
            rem = (1 - frac) * dt
            p_new = np.array([pc[0], pc[1], radius]) + vc * rem
            v_new = vc
        p, v = p_new, v_new
    return ts, pos, bounces


def aim_shot(start: np.ndarray, target_xy: np.ndarray, flight_time: float, radius: float, phys: BallPhysics) -> np.ndarray:
    """Find launch velocity so the first bounce lands on ``target_xy``."""
    d = np.array([target_xy[0] - start[0], target_xy[1] - start[1]])
    vz = (radius - start[2] + 0.5 * G * flight_time**2) / flight_time
    v = np.array([d[0] / flight_time, d[1] / flight_time, vz])
    for _ in range(25):
        _, _, b = simulate(Shot(start, v, 0.0, flight_time * 2.5 + 0.5), radius, phys, dt=1 / 2400)
        if not b:
            v[2] += 0.5
            continue
        err = np.array([target_xy[0] - b[0][1], target_xy[1] - b[0][2]])
        if np.linalg.norm(err) < 1e-4:
            break
        v[0] += err[0] / flight_time
        v[1] += err[1] / flight_time
    return v


# --------------------------------------------------------------------- scene
CAMERA_PRESETS = {
    # All presets watch side B (y > 0), the receiving half in the synthetic drills,
    # and are chosen so the whole of side B (plus ~30 cm) is in frame.
    "behind_baseline_high": "Centred 5 m behind the side-B baseline, 4 m high, main (1x) lens",
    "corner_high": "3 m out and 3 m back from the side-B corner, 3 m high, main lens",
    "side_mid": "Level with side B's middle, 6 m outside the sideline, 3.5 m high, main lens",
    "net_post": "1 m outside the sideline at the net, 1.6 m high, ultra-wide (0.5x) lens",
}


def preset_camera(court: CourtSpec, name: str, image_size: tuple[int, int], hfov_deg: float | None = None) -> Camera:
    """Camera pose for a named preset (see CAMERA_PRESETS). Offsets scale with the court."""
    hw, hl = court.half_w, court.half_l
    s = court.scale
    zs = max(s, 0.6)  # a tripod doesn't shrink as much as the court
    poses = {
        "behind_baseline_high": ((0.0, hl + 5.0 * s, 4.0 * zs), (0.0, hl * 0.6, 0.0), 65.0),
        "corner_high": ((-(hw + 3.0 * s), hl + 3.0 * s, 3.0 * zs), (0.0, hl * 0.6, 0.0), 65.0),
        "side_mid": ((-(hw + 6.0 * s), hl * 0.5, 3.5 * zs), (0.0, hl * 0.5, 0.0), 65.0),
        "net_post": ((-(hw + 1.0 * s), 0.3 * s, 1.6 * zs), (hw * 0.3, hl * 0.55, 0.0), 106.0),
    }
    if name not in poses:
        raise KeyError(f"Unknown camera preset '{name}'. Options: {sorted(poses)}")
    pos, tgt, fov = poses[name]
    return Camera.look_at(np.array(pos), np.array(tgt), image_size, hfov_deg or fov, camera_id=name)


def render_court_texture(court: CourtSpec, mm_per_px: float = 4.0, margin_m: float = 4.0,
                         floor_bgr=(110, 120, 70), out_bgr=(70, 95, 60), line_bgr=(235, 235, 235)) -> tuple[np.ndarray, np.ndarray]:
    """Top-down court image and the 3x3 matrix mapping court (x, y, 1) -> texture px."""
    s = 1000.0 / mm_per_px  # px per metre
    W = int((court.width + 2 * margin_m) * s)
    H = int((court.length + 2 * margin_m) * s)
    img = np.empty((H, W, 3), np.uint8)
    img[:] = out_bgr
    A = np.array([[s, 0, (court.half_w + margin_m) * s], [0, s, (court.half_l + margin_m) * s], [0, 0, 1]])

    def rect_px(r):
        p0 = A @ np.array([r.x0, r.y0, 1])
        p1 = A @ np.array([r.x1, r.y1, 1])
        return (int(round(p0[0])), int(round(p0[1]))), (int(round(p1[0])) - 1, int(round(p1[1])) - 1)

    a, b = rect_px(court.court_rect())
    cv2.rectangle(img, a, b, floor_bgr, -1)
    for seg in court.lines():
        a, b = rect_px(seg.rect)
        cv2.rectangle(img, a, b, line_bgr, -1)
    return img, A


@dataclass
class SynthConfig:
    fps: float = 240.0
    width: int = 1920
    height: int = 1080
    hfov_deg: float | None = None  # None = preset's lens
    camera_preset: str = "behind_baseline_high"
    shutter_s: float = 1 / 1000
    blur_samples: int = 6
    noise_sigma: float = 2.5
    n_shots: int = 20
    near_line_fraction: float = 0.7  # fraction of targets within +/-near_line_band of a line
    near_line_band_m: float = 0.15
    click_noise_px: float = 1.0
    seed: int = 7
    ball_bgr: tuple[int, int, int] = (40, 225, 235)
    court_scale: float = 1.0


@dataclass
class SynthScene:
    cfg: SynthConfig
    court: CourtSpec
    camera: Camera
    shots: list[Shot]
    bounces: list[TrueBounce]
    traj: list[tuple[np.ndarray, np.ndarray]] = field(repr=False)
    background: np.ndarray = field(repr=False)


def _random_target(court: CourtSpec, rng: np.random.Generator, cfg: SynthConfig) -> np.ndarray:
    """Targets on side B; many near the side-B boundary lines (where calls are hard)."""
    hw, hl = court.half_w, court.half_l
    if rng.random() < cfg.near_line_fraction:
        off = rng.uniform(-cfg.near_line_band_m, cfg.near_line_band_m)
        which = rng.choice(["baseline", "left", "right"])
        if which == "baseline":
            return np.array([rng.uniform(-hw * 0.9, hw * 0.9), hl + off])
        x = (-hw if which == "left" else hw) + (-off if which == "left" else off)
        return np.array([x, rng.uniform(court.kitchen_depth + 0.3, hl - 0.2)])
    return np.array([rng.uniform(-hw * 0.9, hw * 0.9), rng.uniform(court.kitchen_depth + 0.2, hl - 0.3)])


def build_scene(cfg: SynthConfig) -> SynthScene:
    rng = np.random.default_rng(cfg.seed)
    court = CourtSpec.pickleball() if cfg.court_scale == 1.0 else CourtSpec.pickleball().scaled(cfg.court_scale)
    cam = preset_camera(court, cfg.camera_preset, (cfg.width, cfg.height), cfg.hfov_deg)
    phys = BallPhysics()
    r = court.ball_radius
    shots, bounces, traj = [], [], []
    t = 0.5  # leave time for background model to settle
    for i in range(cfg.n_shots):
        start = np.array([rng.uniform(-court.half_w * 0.6, court.half_w * 0.6), -court.half_l * rng.uniform(0.3, 1.0), rng.uniform(0.4, 1.1)])
        target = _random_target(court, rng, cfg)
        dist = np.linalg.norm(target - start[:2])
        flight = float(np.clip(dist / rng.uniform(9, 18), 0.5, 2.0))
        v = aim_shot(start, target, flight, r, phys)
        shot = Shot(start, v, t, flight + 0.35)
        ts, pos, bs = simulate(shot, r, phys)
        for j, (tb, xb, yb) in enumerate(bs):
            bounces.append(TrueBounce(tb, xb, yb, i, j))
        shots.append(shot)
        traj.append((ts, pos))
        t += shot.duration + rng.uniform(0.3, 0.6)
    tex, A = render_court_texture(court)
    H_ground = cam.ground_homography()  # court xy -> image
    M = H_ground @ np.linalg.inv(A)  # texture px -> image
    bg = cv2.warpPerspective(tex, M, (cfg.width, cfg.height), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_CONSTANT, borderValue=(60, 60, 60))
    # Sky / wall above the horizon: anything mapping from behind the camera is invalid.
    _draw_net(bg, cam, court)
    return SynthScene(cfg, court, cam, shots, bounces, traj, bg)


def _draw_net(img: np.ndarray, cam: Camera, court: CourtSpec) -> None:
    hw = court.half_w + court.net_post_offset
    pts = np.array([[-hw, 0, 0], [hw, 0, 0], [hw, 0, court.net_height_sideline], [-hw, 0, court.net_height_sideline]])
    if np.any(cam.depth(pts) <= 0):
        return
    px = cam.project(pts).astype(np.int32)
    overlay = img.copy()
    cv2.fillPoly(overlay, [px], (30, 30, 30))
    cv2.addWeighted(overlay, 0.35, img, 0.65, 0, dst=img)
    cv2.line(img, tuple(px[2]), tuple(px[3]), (240, 240, 240), 2, cv2.LINE_AA)


def frames(scene: SynthScene) -> Iterator[tuple[int, float, np.ndarray]]:
    """Render frames (index, t, BGR image). Frame time = middle of exposure."""
    cfg = scene.cfg
    rng = np.random.default_rng(cfg.seed + 1)
    noise_bank = [rng.normal(0, cfg.noise_sigma, (cfg.height, cfg.width, 1)).astype(np.float32) for _ in range(8)]
    t_end = scene.shots[-1].t_start + scene.shots[-1].duration + 0.3
    n = int(t_end * cfg.fps)
    r = scene.court.ball_radius
    cam = scene.camera
    ball = np.array(cfg.ball_bgr, np.float32)
    for i in range(n):
        t = i / cfg.fps
        img = scene.background.astype(np.float32)
        for ts, pos in scene.traj:
            if t < ts[0] - cfg.shutter_s or t > ts[-1] + cfg.shutter_s:
                continue
            sub_t = t + np.linspace(-cfg.shutter_s / 2, cfg.shutter_s / 2, cfg.blur_samples)
            ok = (sub_t >= ts[0]) & (sub_t <= ts[-1])
            if not np.all(ok):  # ball only exists for the whole exposure or not at all
                continue
            P = np.stack([np.interp(sub_t[ok], ts, pos[:, k]) for k in range(3)], axis=1)
            dep = cam.depth(P)
            if np.any(dep <= 0.1):
                continue
            px = cam.project(P)
            rad = cam.focal_px * r / dep
            x0 = int(max(0, np.floor(px[:, 0].min() - rad.max() - 3)))
            y0 = int(max(0, np.floor(px[:, 1].min() - rad.max() - 3)))
            x1 = int(min(cfg.width, np.ceil(px[:, 0].max() + rad.max() + 3)))
            y1 = int(min(cfg.height, np.ceil(px[:, 1].max() + rad.max() + 3)))
            if x1 <= x0 or y1 <= y0:
                continue
            SS = 8
            acc = np.zeros(((y1 - y0) * SS, (x1 - x0) * SS), np.float32)
            for (u, v), rr in zip(px, rad):
                m = np.zeros_like(acc)
                cv2.circle(m, (int(round((u - x0) * SS)), int(round((v - y0) * SS))), max(1, int(round(rr * SS))), 1.0, -1)
                acc += m
            acc /= len(px)
            alpha = cv2.resize(acc, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA)[..., None]
            patch = img[y0:y1, x0:x1]
            img[y0:y1, x0:x1] = patch * (1 - alpha) + ball * alpha
        img += noise_bank[i % len(noise_bank)]
        yield i, t, np.clip(img, 0, 255).astype(np.uint8)


def calibration_clicks(scene: SynthScene, rng: np.random.Generator | None = None) -> dict:
    """Simulated user clicks on visible court keypoints, with pixel noise."""
    rng = rng or np.random.default_rng(scene.cfg.seed + 2)
    cam = scene.camera
    w, h = cam.image_size
    pts = {}
    for name, P in scene.court.keypoints().items():
        P = np.array(P, float)
        if cam.depth(P[None])[0] <= 0:
            continue
        uv = cam.project(P[None])[0]
        if 5 <= uv[0] < w - 5 and 5 <= uv[1] < h - 5:
            uv = uv + rng.normal(0, scene.cfg.click_noise_px, 2)
            pts[name] = [float(uv[0]), float(uv[1])]
    return {"schema": "balltracker.calibration_points/v1", "image_size": [w, h], "points": pts}


def ground_truth(scene: SynthScene) -> dict:
    return {
        "schema": "balltracker.ground_truth/v1",
        "kind": "synthetic",
        "court": scene.court.to_dict(),
        "camera_true": scene.camera.to_dict(),
        "config": {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(scene.cfg).items()},
        "bounces": [asdict(b) for b in scene.bounces],
    }


def write_scene(scene: SynthScene, out_dir: str | Path, encode: bool = True) -> dict[str, Path]:
    from .video import write_video

    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths = {
        "video": out / "video.mp4",
        "ground_truth": out / "ground_truth.json",
        "calibration_points": out / "calibration_points.json",
    }
    paths["ground_truth"].write_text(json.dumps(ground_truth(scene), indent=2))
    paths["calibration_points"].write_text(json.dumps(calibration_clicks(scene), indent=2))
    if encode:
        write_video(paths["video"], (f for _, _, f in frames(scene)), scene.cfg.fps, (scene.cfg.width, scene.cfg.height))
    return paths
