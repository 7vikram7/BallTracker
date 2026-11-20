"""End-to-end single-camera analysis: frames -> observations -> tracks -> bounces -> calls.

Stages are separate objects with narrow interfaces so each can be replaced
(e.g. the classical detector by a neural one, or this whole on-server pipeline
by on-phone processing that sends ``BallObservation``/``BounceEvent`` messages).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Iterable

import numpy as np

from .bounce import BounceConfig, BounceDetector
from .detection import BallDetector, DetectorConfig, MotionColorBallDetector
from .events import AnalysisResult, BallObservation, Provenance
from .geometry.camera import Camera
from .geometry.court import CourtSpec
from .sports.pickleball.line_calling import LineCallConfig, PickleballLineCaller, ServeContext
from .tracking import BallTracker, Track, TrackerConfig


@dataclass
class PipelineConfig:
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    tracker: TrackerConfig = field(default_factory=TrackerConfig)
    bounce: BounceConfig = field(default_factory=BounceConfig)
    line_call: LineCallConfig = field(default_factory=LineCallConfig)
    serve: ServeContext | None = None  # if set, every bounce is judged as a serve
    suppress_secondary: bool = True


@dataclass
class PipelineOutput:
    result: AnalysisResult
    tracks: list[Track]


def dedupe_bounces(bounces: list, window_s: float) -> list:
    """One ball can end up in two overlapping tracks (e.g. a split at the
    bounce), each reporting the same bounce. Keep the most confident event
    among bounces closer than ``window_s`` in time (single ball assumed)."""
    kept: list = []
    for b in sorted(bounces, key=lambda b: -b.confidence):
        if all(abs(b.t - k.t) > window_s for k in kept):
            kept.append(b)
    return sorted(kept, key=lambda b: b.t)


def court_roi_mask(camera: Camera, court: CourtSpec, margin_m: float | None = None,
                   height_m: float | None = None) -> np.ndarray:
    """Image mask covering the volume above the court (+margin) where the ball can be.

    The margin (2.5 m) and height (6 m) shrink with a practice court's scale, down to 0.5 m and
    2 m: on a 0.2 mini court the full-size box took in lights and people around the court and the
    tracker lost bounces (field 2026-11-20: 4 instead of 20 bounces seen by both cameras)."""
    import cv2

    sc = float(getattr(court, "scale", 1.0) or 1.0)
    margin_m = max(2.5 * sc, 0.5) if margin_m is None else margin_m
    height_m = max(6.0 * sc, 2.0) if height_m is None else height_m

    w, h = camera.image_size
    hw, hl = court.half_w + margin_m, court.half_l + margin_m
    corners = np.array([[x, y, z] for z in (0.0, height_m) for x in (-hw, hw) for y in (-hl, hl)])
    # Clip points behind the camera by pulling them towards the camera's front.
    dep = camera.depth(corners)
    pts = camera.project(corners[dep > 0.2]) if np.any(dep > 0.2) else np.zeros((0, 2))
    mask = np.zeros((h, w), np.uint8)
    if len(pts) >= 3:
        hull = cv2.convexHull(pts.astype(np.float32)).astype(np.int32)
        cv2.fillConvexPoly(mask, hull, 255)
    if mask.sum() == 0:
        mask[:] = 255
    return mask


def analyze_frames(
    frames: Iterable[tuple[int, float, np.ndarray]],
    camera: Camera,
    court: CourtSpec,
    cfg: PipelineConfig | None = None,
    *,
    source: str = "frames",
    fps: float = 0.0,
    detector: BallDetector | None = None,
) -> PipelineOutput:
    cfg = cfg or PipelineConfig()
    if cfg.detector.roi_mask is None:
        cfg.detector.roi_mask = court_roi_mask(camera, court)
    det = detector or MotionColorBallDetector(cfg.detector)
    prov = Provenance(algorithm=det.name, version=det.version, params=getattr(det, "params", lambda: {})())
    tracker = BallTracker(cfg.tracker)
    observations: list[BallObservation] = []
    n = 0
    t_det = 0.0
    wall0 = time.perf_counter()
    for idx, t, img in frames:
        a = time.perf_counter()
        cands = det.detect(img)
        t_det += time.perf_counter() - a
        ids = []
        for c in cands:
            o = BallObservation(
                camera_id=camera.camera_id, frame_index=idx, t=t, u=c.u, v=c.v,
                radius_px=c.radius_px, confidence=c.score, provenance=prov,
            )
            ids.append(o.id)
            observations.append(o)
        tracker.update(idx, t, cands, ids)
        n += 1
    tracks = tracker.finish()

    bd = BounceDetector(camera, court, cfg.bounce)
    bounces = dedupe_bounces([b for tr in tracks for b in bd.detect(tr)], cfg.bounce.nms_s)
    caller = PickleballLineCaller(court, cfg.line_call)
    judged = caller.suppress_secondary(bounces) if cfg.suppress_secondary else bounces
    calls = [caller.call(b, cfg.serve) for b in judged]
    wall = time.perf_counter() - wall0

    # Keep only observations that ended up in a track, to keep outputs small.
    used = {p.obs_id for tr in tracks for p in tr.points}
    result = AnalysisResult(
        source=source,
        camera_id=camera.camera_id,
        court=court.to_dict(),
        fps=fps,
        frame_count=n,
        observations=[o for o in observations if o.id in used],
        bounces=bounces,
        calls=calls,
        timings={
            "wall_s": wall,
            "detect_s": t_det,
            "frames_per_s": n / wall if wall > 0 else 0.0,
            "tracks": len(tracks),
            "raw_candidates": len(observations),
        },
    )
    return PipelineOutput(result=result, tracks=tracks)
