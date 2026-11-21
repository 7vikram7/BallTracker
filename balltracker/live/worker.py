"""Per-camera live pipeline: frames in, ball positions and bounce events out.

``LiveCameraPipeline`` is the streaming counterpart of
``pipeline.analyze_frames``: the same detector, tracker and bounce detector,
but bounces are emitted while the rally goes on.

Streaming bounce detection
--------------------------
Every ``check_every_s`` the bounce detector runs on the last ``lookback_s`` of
each live track. A bounce is emitted once ``settle_s`` of track exists after
it (enough post-bounce points for a stable fit). When a track ends (ball left
the frame, occluded), it gets a final check without the settle requirement.
A bounce already emitted (within ``nms_s``) is not emitted again.

Each camera runs in its own process (``run_worker``) so several cameras use
several CPU cores.
"""

from __future__ import annotations

import queue as queue_mod
import time
from dataclasses import dataclass, field

import numpy as np

from ..bounce import BounceConfig, BounceDetector
from ..detection import Candidate, DetectorConfig, MotionColorBallDetector
from ..events import BounceEvent
from ..geometry.camera import Camera
from ..geometry.court import CourtSpec
from ..tracking import BallTracker, Track, TrackerConfig
from .frameclock import FrameClock


@dataclass
class LiveConfig:
    detector: DetectorConfig = field(default_factory=DetectorConfig)
    tracker: TrackerConfig = field(default_factory=TrackerConfig)
    bounce: BounceConfig = field(default_factory=lambda: BounceConfig(bootstrap=80))
    check_every_s: float = 0.08
    # A track that stayed within this many pixels over the lookback is a still object (clutter, a ball
    # lying on the court): it cannot bounce, so it is not searched (the search dominates the Mac's load).
    min_motion_px: float = 8.0
    lookback_s: float = 1.0
    settle_s: float = 0.15
    ball_report_hz: float = 20.0
    # Backlog guard (field test 3: the worker fell up to 3.4 s behind in clutter, so calls came
    # seconds late). Behind by more than defer_after_s: skip the periodic bounce checks (tracks are
    # still followed, and each gets its check when it ends). Behind by more than drop_after_s: drop
    # the stale frames to catch up.
    defer_after_s: float = 0.3
    drop_after_s: float = 1.5
    # Calibration uncertainty added to every bounce's position covariance: the bounce detector's
    # covariance only knows pixel noise, but a calibration is good to ~1-2 px (snap residual,
    # drift between checks). Field test 3: with 0 px, cameras 14 cm apart scored chi2 44 (2 =
    # consistent) and the judge declared them in disagreement; 2 px made them consistent
    # (median chi2 0.7-2.8, 5-7% of pairs beyond the 99.9% limit).
    calib_sigma_px: float = 2.0


def _slice_track(tr: Track, t_from: float) -> Track:
    pts = [p for p in tr.points if p.t >= t_from]
    return Track(tr.track_id, pts)


class LiveCameraPipeline:
    def __init__(self, camera_id: str, court: CourtSpec, camera: Camera | None = None, cfg: LiveConfig | None = None):
        self.camera_id = camera_id
        self.court = court
        self.cfg = cfg or LiveConfig()
        self.detector = MotionColorBallDetector(self.cfg.detector)
        self.tracker = BallTracker(self.cfg.tracker)
        self.camera: Camera | None = None
        self.bd: BounceDetector | None = None
        self._emitted: list[float] = []
        self._checked_len: dict[int, int] = {}
        self._scanned_to: dict[int, float] = {}
        self._last_check = -1e9
        self._last_t = -1e9
        self._last_ball_report = -1e9
        self.frames = 0
        self.bounces = 0
        self.diag = {"frames": 0, "cands": 0, "max_tracks": 0, "check_s": 0.0, "checks": 0}
        self.frame_clock: FrameClock | None = None  # snaps jittery (browser) timestamps to the frame grid
        self.defer_checks = False  # set by the worker loop while it is behind (see LiveConfig)
        self.set_camera(camera)

    def set_time_regularization(self, on: bool) -> None:
        self.frame_clock = FrameClock() if on else None

    def pop_diagnostics(self) -> dict:
        """Load indicators since the last call (worker stats -> camera_stats in the session log)."""
        d, n = self.diag, max(self.diag["frames"], 1)
        out = {"cands_per_frame": round(d["cands"] / n, 2), "max_tracks": d["max_tracks"],
               "check_ms_per_s": round(1e3 * d["check_s"], 1), "checks": d["checks"],
               "deferred_frames": d.get("deferred", 0), "dropped_stale": d.get("dropped_stale", 0)}
        self.diag = {"frames": 0, "cands": 0, "max_tracks": 0, "check_s": 0.0, "checks": 0}
        return out

    def set_camera(self, camera: Camera | None) -> None:
        self.camera = camera
        if camera is None:
            self.bd = None
            self.detector.cfg.roi_mask = None
        else:
            from ..pipeline import court_roi_mask

            self.bd = BounceDetector(camera, self.court, self.cfg.bounce)
            self.detector.cfg.roi_mask = court_roi_mask(camera, self.court)
        self.detector._roi_small = None  # rebuild the downscaled mask

    def process(self, frame_index: int, t: float, image: np.ndarray) -> list[dict]:
        """Feed one frame (t on the session clock). Returns output messages."""
        if self.frame_clock is not None:
            t = self.frame_clock.fit(t)
        if t <= self._last_t:  # out of order or duplicate: skip
            return []
        out = self._size_check(image.shape[1], image.shape[0])
        return out + self._ingest(frame_index, t, self.detector.detect(image))

    def process_candidates(self, frame_index: int, t: float, cands: list[Candidate], size: tuple[int, int]) -> list[dict]:
        """Edge camera: the phone already ran the detector. Candidates outside the
        court region (same mask the Mac detector uses) are dropped here."""
        if self.frame_clock is not None:
            t = self.frame_clock.fit(t)
        if t <= self._last_t:
            return []
        out = self._size_check(*size)
        roi = self.detector.cfg.roi_mask
        if roi is not None and cands:
            h, w = roi.shape
            cands = [c for c in cands if 0 <= int(c.v) < h and 0 <= int(c.u) < w and roi[int(c.v), int(c.u)]]
        return out + self._ingest(frame_index, t, cands)

    def _size_check(self, w: int, h: int) -> list[dict]:
        if self.camera is not None and tuple(self.camera.image_size) != (w, h):
            msg = {"kind": "warning", "camera": self.camera_id,
                   "text": f"frame size {w}x{h} differs from calibration "
                           f"{self.camera.image_size[0]}x{self.camera.image_size[1]}; recalibrate"}
            self.set_camera(None)
            return [msg]
        return []

    def _ingest(self, frame_index: int, t: float, cands: list[Candidate]) -> list[dict]:
        out: list[dict] = []
        self._last_t = t
        self.frames += 1
        self.diag["cands"] += len(cands)
        self.diag["frames"] += 1
        self.tracker.update(frame_index, t, cands)
        self.diag["max_tracks"] = max(self.diag["max_tracks"], len(self.tracker._active))
        if t - self._last_ball_report >= 1.0 / self.cfg.ball_report_hz:
            act = [tr for tr in self.tracker.active_tracks() if len(tr.points) >= 3 and tr.points[-1].t == t]
            if act:
                p = max(act, key=lambda tr: len(tr.points)).points[-1]
                out.append({"kind": "ball", "camera": self.camera_id, "t": t, "u": p.u, "v": p.v, "r": p.radius_px})
                self._last_ball_report = t
        if self.bd is not None:
            ended = self.tracker.pop_finished()
            for tr in ended:
                out += self._check(tr, t, final=True)
            if self.defer_checks:
                self.diag["deferred"] = self.diag.get("deferred", 0) + 1
            elif t - self._last_check >= self.cfg.check_every_s:
                self._last_check = t
                live = self.tracker.active_tracks()
                for tr in live:
                    if self._checked_len.get(tr.track_id) == len(tr.points):
                        continue  # nothing new since the last check
                    self._checked_len[tr.track_id] = len(tr.points)
                    out += self._check(tr, t, final=False)
                if len(self._checked_len) > 200:
                    ids = {tr.track_id for tr in live}
                    self._checked_len = {k: v for k, v in self._checked_len.items() if k in ids}
                    self._scanned_to = {k: v for k, v in self._scanned_to.items() if k in ids}
        else:
            self.tracker.pop_finished()
        return out

    def flush(self) -> list[dict]:
        """End all tracks and give them a final bounce check (stream paused or stopped)."""
        out: list[dict] = []
        self.tracker.end_all()
        ended = self.tracker.pop_finished()
        if self.bd is not None:
            for tr in ended:
                out += self._check(tr, self._last_t, final=True)
        return out

    def _check(self, tr: Track, t_now: float, final: bool) -> list[dict]:
        a = time.monotonic()
        try:
            return self._check_inner(tr, t_now, final)
        finally:
            self.diag["check_s"] += time.monotonic() - a
            self.diag["checks"] += 1

    def _check_inner(self, tr: Track, t_now: float, final: bool) -> list[dict]:
        cfg = self.cfg
        mtl = self.cfg.tracker.min_track_len
        if len(tr.points) < max(mtl, 2 * cfg.bounce.min_side_points):
            return []
        sl = _slice_track(tr, t_now - cfg.lookback_s)
        if len(sl.points) < 2 * cfg.bounce.min_side_points:
            return []
        us = [p.u for p in sl.points]
        vs = [p.v for p in sl.points]
        if max(us) - min(us) + max(vs) - min(vs) < cfg.min_motion_px:
            self.diag["static_skips"] = self.diag.get("static_skips", 0) + 1
            return []
        assert self.bd is not None
        out = []
        # Only splits not settled at the previous check need scanning again.
        prev = self._scanned_to.get(tr.track_id)
        t_from = None if (final or prev is None) else prev - cfg.settle_s - cfg.bounce.window_s
        cands, t, uv = self.bd.candidates(sl, t_from=t_from)
        self._scanned_to[tr.track_id] = sl.points[-1].t
        for c in cands:
            if not final and c["tb"] > sl.points[-1].t - cfg.settle_s:
                continue
            if any(abs(c["tb"] - e) <= cfg.bounce.nms_s for e in self._emitted):
                continue
            ev = self.bd.finalise(c, t, uv, sl)  # expensive bootstrap only for bounces we emit
            if ev is None:
                continue
            ev = self._with_calibration_uncertainty(ev)
            self._emitted.append(ev.t)
            self._emitted = self._emitted[-50:]
            self.bounces += 1
            out.append({"kind": "bounce", "camera": self.camera_id, "event": ev.model_dump(mode="json")})
        return out


    def _with_calibration_uncertainty(self, ev: BounceEvent) -> BounceEvent:
        """cov += sigma^2 J J^T, J = d(ground x, y) / d(pixel u, v) at the bounce pixel."""
        sig = self.cfg.calib_sigma_px
        if not sig or self.camera is None or ev.pixel is None:
            return ev
        J = ground_jacobian(self.camera, ev.pixel, self.court.ball_radius)
        if J is None:
            return ev
        C = np.asarray(ev.cov_xy, float) + sig * sig * (J @ J.T)
        params = dict(ev.provenance.params or {})
        params["calib_sigma_px"] = sig
        return ev.model_copy(update={"cov_xy": C.tolist(),
                                     "provenance": ev.provenance.model_copy(update={"params": params})})


def ground_jacobian(camera: Camera, px, z: float, h: float = 0.5) -> np.ndarray | None:
    """2x2 derivative of the ground point (at height z) seen at pixel px, by central differences."""
    def ground(u: float, v: float):
        o, d = camera.rays(np.array([[u, v]], float))
        o, d = np.asarray(o, float).reshape(-1, 3)[0], np.asarray(d, float).reshape(-1, 3)[0]
        if abs(d[2]) < 1e-9:
            return None
        k = (z - o[2]) / d[2]
        return None if k <= 0 else (o + k * d)[:2]

    u, v = float(px[0]), float(px[1])
    pts = [ground(u + h, v), ground(u - h, v), ground(u, v + h), ground(u, v - h)]
    if any(p is None for p in pts):
        return None
    return np.column_stack([(pts[0] - pts[1]) / (2 * h), (pts[2] - pts[3]) / (2 * h)])


# --------------------------------------------------------------------------
# Process entry point


def run_worker(camera_id: str, court_dict: dict, camera_dict: dict | None, in_q, out_q,
               detector_overrides: dict | None = None) -> None:
    """Loop: ("frame", seq, t, jpeg, t_recv) | ("dets", frames, size, t_recv) | ("camera", dict|None) | ("stop",)."""
    import signal

    import cv2

    # Ctrl+C in the terminal reaches every process in the group; the server stops workers
    # itself (so open tracks get their final bounce check), so ignore it here.
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    cv2.setNumThreads(1)
    court = CourtSpec.from_dict(court_dict)
    cfg = LiveConfig()
    for k, v in (detector_overrides or {}).items():
        setattr(cfg.detector, k, tuple(v) if isinstance(v, list) else v)
    cam = Camera.from_dict(camera_dict) if camera_dict else None
    pipe = LiveCameraPipeline(camera_id, court, cam, cfg)
    import threading

    # JPEG decoding runs in its own thread (OpenCV releases the GIL), overlapping
    # with detection of the previous frame.
    decoded: queue_mod.Queue = queue_mod.Queue(maxsize=4)
    STOP = object()

    def decoder() -> None:
        while True:
            try:
                msg = in_q.get(timeout=0.5)
            except queue_mod.Empty:
                decoded.put(None)
                continue
            if msg[0] == "frame":
                _, seq, t, jpeg, t_recv = msg
                img = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
                decoded.put(("frame", seq, t, img, t_recv))
            elif msg[0] == "dets":  # edge camera: nothing to decode
                decoded.put(msg)
            else:
                decoded.put(msg)
                if msg[0] == "stop":
                    return

    threading.Thread(target=decoder, daemon=True).start()
    n, busy, lat_sum, t_stats = 0, 0.0, 0.0, time.monotonic()
    last_seq = -1
    last_frame = time.monotonic()
    flushed = True
    while True:
        msg = decoded.get()
        if msg is None and not flushed and time.monotonic() - last_frame > 0.4:
            for o in pipe.flush():  # no frames for a while: finish open tracks now
                out_q.put(o)
            flushed = True
        if msg is not None:
            kind = msg[0]
            if kind == "stop":
                for o in pipe.flush():
                    out_q.put(o)
                break
            if kind == "timing":  # ("timing", regularize: bool), sent on every (re)connect
                pipe.set_time_regularization(bool(msg[1]))
            elif kind == "camera":
                pipe.set_camera(Camera.from_dict(msg[1]) if msg[1] else None)
                out_q.put({"kind": "camera_set", "camera": camera_id, "calibrated": msg[1] is not None})
            elif kind == "frame":
                _, seq, t, img, t_recv = msg
                a = time.monotonic()
                if img is not None:
                    for o in pipe.process(seq, t, img):
                        out_q.put(o)
                    n += 1
                    last_seq = seq
                b = time.monotonic()
                busy += b - a
                lat_sum += b - t_recv
                last_frame, flushed = b, False
            elif kind == "dets":
                # ("dets", [(seq, t_session, [(u, v, r, score), ...]), ...], (w, h), t_recv)
                _, frames, size, t_recv = msg
                a = time.monotonic()
                lag = a - t_recv
                if lag > cfg.drop_after_s:  # far behind: drop these frames to catch up
                    pipe.diag["dropped_stale"] = pipe.diag.get("dropped_stale", 0) + len(frames)
                    frames = []
                pipe.defer_checks = lag > cfg.defer_after_s
                for seq, t, cl in frames:
                    cands = [Candidate(u=u, v=v, radius_px=r, score=sc, area_px=float(np.pi * r * r), elongation=1.0)
                             for u, v, r, sc in cl]
                    for o in pipe.process_candidates(seq, t, cands, size):
                        out_q.put(o)
                    n += 1
                    last_seq = seq
                b = time.monotonic()
                busy += b - a
                lat_sum += (b - t_recv) * len(frames)
                last_frame, flushed = b, False
        now = time.monotonic()
        if now - t_stats >= 1.0:
            dt = now - t_stats
            out_q.put({"kind": "stats", "camera": camera_id, "proc_fps": n / dt, "busy": busy / dt,
                       "latency_ms": 1e3 * lat_sum / n if n else None, "frames": pipe.frames,
                       "bounces": pipe.bounces, "last_seq": last_seq,
                       "calibrated": pipe.camera is not None, **pipe.pop_diagnostics()})
            n, busy, lat_sum, t_stats = 0, 0.0, 0.0, now


def _event_from(msg: dict) -> BounceEvent:
    return BounceEvent.model_validate(msg["event"])
