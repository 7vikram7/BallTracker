"""Synthetic experiments: how accuracy depends on frame rate, camera and resolution.

Frames are fed to the pipeline in memory (no video encoding) to keep sweeps fast,
so compression artefacts are not included. Calibration uses simulated clicks
with pixel noise and a deliberately wrong field-of-view prior, so calibration
error is part of the result.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np

from .evaluate import load_truth, match, summarise, visible_truth
from .geometry.camera import calibrate_from_points
from .pipeline import PipelineConfig, analyze_frames
from .synthetic import SynthConfig, build_scene, calibration_clicks, frames, ground_truth


def run_one(cfg: SynthConfig, hfov_prior: float = 60.0) -> dict:
    scene = build_scene(cfg)
    clicks = calibration_clicks(scene)
    kp = scene.court.keypoints()
    names = list(clicks["points"])
    cam = calibrate_from_points([kp[n] for n in names], [clicks["points"][n] for n in names],
                                (cfg.width, cfg.height), hfov_guess_deg=hfov_prior, camera_id=cfg.camera_preset)
    t0 = time.perf_counter()
    out = analyze_frames(frames(scene), cam, scene.court, PipelineConfig(), source="synthetic", fps=cfg.fps)
    gt = ground_truth(scene)
    truth = [
        {"t": b["t"], "x": b["x"], "y": b["y"]} for b in gt["bounces"]
    ]
    # Reuse the evaluator's truth-call logic via a temp JSON round trip.
    from .evaluate import _truth_call

    for t in truth:
        t["call"], t["signed_m"] = _truth_call(scene.court, t["x"], t["y"])
    truth = visible_truth(truth, gt, scene.court)
    summ = summarise(match(out.result, truth))
    summ["calibration"] = {
        "points": len(names),
        "rms_px": cam.reprojection_rms_px,
        "focal_err_pct": 100 * (cam.focal_px - scene.camera.focal_px) / scene.camera.focal_px,
        "position_err_cm": 100 * float(np.linalg.norm(cam.position - scene.camera.position)),
    }
    summ["processing_fps"] = out.result.timings["frames_per_s"]
    summ["wall_s"] = time.perf_counter() - t0
    return summ


def run_sweep(fps_list, cameras, res="1280x720", shots=25, seeds=(1,), scale=1.0, out="sweep.json", hfov_prior=60.0,
              shutter="fast", noise=2.5):
    """shutter: "fast" = 1/1000 s (manual, e.g. Blackmagic Camera); "auto" = half the frame
    interval (typical phone auto-exposure indoors), so motion blur grows at low fps."""
    w, h = (int(x) for x in res.split("x"))
    rows = []
    for cam in cameras:
        for fps in fps_list:
            for seed in seeds:
                sh = min(1 / 1000, 1 / fps) if shutter == "fast" else 0.5 / fps
                cfg = SynthConfig(fps=fps, width=w, height=h, camera_preset=cam, n_shots=shots, seed=seed,
                                  court_scale=scale, shutter_s=sh, noise_sigma=noise, blur_samples=max(6, int(sh * 6000)))
                s = run_one(cfg, hfov_prior)
                row = {"camera": cam, "fps": fps, "seed": seed, "res": res, "scale": scale, "shutter": shutter, "noise": noise, **s}
                rows.append(row)
                pe = s["position_error_cm"] or {}
                le = s["line_distance_error_cm"] or {}
                print(f"{cam:22s} {fps:5.0f}fps {shutter:4s} seed{seed}: recall {s['recall'] or 0:.2f} "
                      f"({s['detected']}/{s['true_bounces']}), false {s['false_bounces']}, "
                      f"pos err med {pe.get('median', float('nan')):.1f}cm p90 {pe.get('p90', float('nan')):.1f}cm, "
                      f"line err med {le.get('median', float('nan')):.1f}cm, "
                      f"WRONG_OUT {s['WRONG_OUT_CALLS']}, MISSED_OUT {s['MISSED_OUT_CALLS']}, "
                      f"calib {s['calibration']['rms_px']:.2f}px/{s['calibration']['focal_err_pct']:+.1f}%f",
                      flush=True)
    Path(out).write_text(json.dumps(rows, indent=2, default=float))
    print(f"wrote {out}")
    return rows


def run_track_noise_sweep(fps_list=(30, 60, 120, 240), noise_px=(0.5, 1.0, 2.0, 4.0), dropout=(0.0, 0.2),
                          n_shots=40, seed=0, out="track_noise_sweep.json", camera_preset="behind_baseline_high"):
    """Robustness of bounce localisation to detection noise and missed frames.

    Skips rendering: true trajectories are projected analytically, then each frame's
    detection gets Gaussian pixel jitter and is dropped with probability ``dropout``.
    Targets cluster near the lines as in the rendered sweeps.
    """
    from .bounce import BounceDetector
    from .synthetic import BallPhysics, Shot, _random_target, aim_shot, preset_camera, simulate
    from .tracking import Track, TrackPoint
    from .geometry.court import CourtSpec

    rng = np.random.default_rng(seed)
    court = CourtSpec()
    cam = preset_camera(court, camera_preset, (1920, 1080))
    cam.reprojection_rms_px = 1.0
    phys = BallPhysics()
    cfg = SynthConfig()
    shots = []
    for _ in range(n_shots):
        start = np.array([rng.uniform(-2, 2), -court.half_l * rng.uniform(0.3, 1.0), rng.uniform(0.4, 1.1)])
        target = _random_target(court, rng, cfg)
        flight = float(np.clip(np.linalg.norm(target - start[:2]) / rng.uniform(9, 18), 0.5, 2.0))
        v = aim_shot(start, target, flight, court.ball_radius, phys)
        ts, pos, bs = simulate(Shot(start, v, 0.0, flight + 0.35), court.ball_radius, phys)
        shots.append((ts, pos, bs[0]))
    rows = []
    for fps in fps_list:
        for nz in noise_px:
            for dp in dropout:
                errs, found_n, false_n = [], 0, 0
                for ts, pos, (tb, xb, yb) in shots:
                    tr = Track(0)
                    phase = rng.uniform(0, 1 / fps)
                    for i in range(int((ts[-1] - ts[0]) * fps)):
                        t = ts[0] + phase + i / fps
                        if t > ts[-1] or rng.random() < dp:
                            continue
                        P = np.array([np.interp(t, ts, pos[:, k]) for k in range(3)])
                        if cam.depth(P[None])[0] <= 0:
                            continue
                        u, v = cam.project(P[None])[0] + rng.normal(0, nz, 2)
                        if not (0 <= u < 1920 and 0 <= v < 1080):
                            continue
                        tr.points.append(TrackPoint(i, t, u, v, 5.0, 1.0))
                    if len(tr.points) < 10:
                        continue
                    det = BounceDetector(cam, court).detect(tr)
                    m = [d for d in det if abs(d.t - tb) < 0.06]
                    false_n += len(det) - len(m)
                    if m:
                        found_n += 1
                        errs.append(100 * np.hypot(m[0].position.x - xb, m[0].position.y - yb))
                e = np.array(errs) if errs else np.array([np.nan])
                row = dict(fps=fps, noise_px=nz, dropout=dp, shots=len(shots), recall=found_n / len(shots),
                           false=false_n, err_med_cm=float(np.median(e)), err_p90_cm=float(np.percentile(e, 90)))
                rows.append(row)
                print(f"{fps:4.0f}fps noise {nz:3.1f}px drop {dp:.1f}: recall {row['recall']:.2f} false {false_n:2d} "
                      f"err med {row['err_med_cm']:5.1f}cm p90 {row['err_p90_cm']:5.1f}cm", flush=True)
    Path(out).write_text(json.dumps(rows, indent=2))
    return rows
