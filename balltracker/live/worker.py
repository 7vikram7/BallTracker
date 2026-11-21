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
import subprocess
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
    # No frames for this long: end the open tracks and give them their final bounce check. It
    # was 0.4 s; a Wi-Fi stall that long cut tracks short, and a bounce just before it could be
    # finalised with too few points after it (review of defed68). Now one lookback.
    flush_after_s: float = 1.0
    # Frames further apart than this are a gap in what this camera processed (stall, dropped
    # batch): the judge treats the camera as "unknown" there, not as having seen nothing.
    gap_s: float = 0.25
    # Ball-likeness at the bounce (review of defed68, TODO-17: a shirt swaying and bobbing made
    # bounces in 4 of 40 synthetic trials). The blob's median radius around the bounce is
    # compared with the radius a ball would have at that spot (from the calibration): not a ball
    # if larger than max_ball_radius_ratio x that + ball_radius_slack_px. The slack is needed
    # because the detector adds ~1.5-2 px whatever the size: a far ball of 1 px measured 2.6-2.9
    # px (ratio up to 3.5) in scripts/measure_centroid_bias.py, so a pure ratio cap silenced real
    # far bounces (review of round 2). Removes the shirt bounces at 5.4-6x, not those at 2.3x
    # (size alone can't tell those). No lower bound by default (min_ball_radius_ratio). Entry 29.
    max_ball_radius_ratio: float | None = 3.0
    ball_radius_slack_px: float = 2.0
    # Detector for cameras that send JPEGs (browser page): "phone" runs the phone's own detector
    # (the C++ core, same as the app) so a browser camera and the app see the same candidates;
    # "mog2" is the Mac's older model, kept to replay sessions recorded with it. MOG2 lost a ball
    # that stopped after 0.2 s, the phone's model keeps it ~2 s (review of defed68, TODO-16).
    mac_detector: str = "phone"
    fps_hint: float = 60.0  # the phone detector's background rate follows the frame rate
    min_ball_radius_ratio: float | None = None


def _slice_track(tr: Track, t_from: float) -> Track:
    pts = [p for p in tr.points if p.t >= t_from]
    return Track(tr.track_id, pts)


class LiveCameraPipeline:
    def __init__(self, camera_id: str, court: CourtSpec, camera: Camera | None = None, cfg: LiveConfig | None = None):
        self.camera_id = camera_id
        self.court = court
        self.cfg = cfg or LiveConfig()
        self.roi: np.ndarray | None = None
        self.warnings: list[str] = []
        self._detector = None  # made on the first JPEG frame (app cameras send candidates instead)
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
               "deferred_frames": d.get("deferred", 0), "dropped_stale": d.get("dropped_stale", 0),
               "no_calib_floor": d.get("no_calib_floor", 0), "skipped_frames": d.get("skipped_frames", 0)}
        self.diag = {"frames": 0, "cands": 0, "max_tracks": 0, "check_s": 0.0, "checks": 0}
        return out

    def _make_detector(self):
        if self.cfg.mac_detector == "phone":
            from ..edge_detection import EdgeDetectorConfig

            try:
                from ..ballcore import NativeDetector

                return NativeDetector(EdgeDetectorConfig(fps=self.cfg.fps_hint, roi_mask=self.roi))
            except (RuntimeError, OSError, subprocess.CalledProcessError):  # no C++ compiler
                self.cfg.mac_detector = "mog2"
                self.warnings.append("no C++ compiler: JPEG cameras use the Mac's MOG2 detector")
        d = MotionColorBallDetector(self.cfg.detector)
        d.cfg.roi_mask = self.roi
        return d

    @property
    def detector(self):
        if self._detector is None:
            self._detector = self._make_detector()
        return self._detector

    def set_fps(self, fps: float) -> None:
        """The camera's frame rate (the phone detector's background model depends on it)."""
        if fps and abs(fps - self.cfg.fps_hint) > 0.5:
            self.cfg.fps_hint = float(fps)
            if self.cfg.mac_detector == "phone":
                self._detector = None

    def set_camera(self, camera: Camera | None) -> None:
        self.camera = camera
        if camera is None:
            self.bd = None
            self.roi = None
        else:
            from ..pipeline import court_roi_mask

            self.bd = BounceDetector(camera, self.court, self.cfg.bounce)
            self.roi = court_roi_mask(camera, self.court)
        if self.cfg.mac_detector == "phone" or self._detector is None:
            self._detector = None  # (re)made with the new ROI on the next JPEG frame
        else:
            self._detector.cfg.roi_mask = self.roi
            self._detector._roi_small = None  # rebuild the downscaled mask

    def process(self, frame_index: int, t: float, image: np.ndarray) -> list[dict]:
        """Feed one frame (t on the session clock). Returns output messages."""
        if self.frame_clock is not None:
            t = self.frame_clock.fit(t)
        if t <= self._last_t:  # out of order or duplicate: skip (counted)
            self.diag["skipped_frames"] = self.diag.get("skipped_frames", 0) + 1
            return []
        out = self._size_check(image.shape[1], image.shape[0])
        return out + self._ingest(frame_index, t, self.detector.detect(image))

    def process_candidates(self, frame_index: int, t: float, cands: list[Candidate], size: tuple[int, int]) -> list[dict]:
        """Edge camera: the phone already ran the detector. Candidates outside the
        court region (same mask the Mac detector uses) are dropped here."""
        if self.frame_clock is not None:
            t = self.frame_clock.fit(t)
        if t <= self._last_t:
            self.diag["skipped_frames"] = self.diag.get("skipped_frames", 0) + 1
            return []
        out = self._size_check(*size)
        roi = self.roi
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
        if self._last_t > -1e8 and t - self._last_t > self.cfg.gap_s:
            out.append({"kind": "gap", "camera": self.camera_id, "t0": self._last_t, "t1": t})
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
                out += self._check(tr, self._last_t, final=True, flushed=True)
        return out

    def _check(self, tr: Track, t_now: float, final: bool, flushed: bool = False) -> list[dict]:
        a = time.monotonic()
        try:
            return self._check_inner(tr, t_now, final, flushed)
        finally:
            self.diag["check_s"] += time.monotonic() - a
            self.diag["checks"] += 1

    def _check_inner(self, tr: Track, t_now: float, final: bool, flushed: bool = False) -> list[dict]:
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
            unsettled = c["tb"] > sl.points[-1].t - cfg.settle_s
            if not final and unsettled:
                continue
            # Provisional: the track was cut by a flush (no frames for a while: a stall, the
            # stream stopping) less than settle_s after the bounce. A track that ended by itself
            # (ball out of view, played) is judged on its own points and uncertainty as before.
            unsettled = unsettled and flushed
            if any(abs(c["tb"] - e) <= cfg.bounce.nms_s for e in self._emitted):
                continue
            ev = self.bd.finalise(c, t, uv, sl)  # expensive bootstrap only for bounces we emit
            if ev is None:
                continue
            size = self._ball_size(sl, c["tb"], ev.pixel)
            rr = None if size is None else size[0] / size[1]
            if size is not None and not ball_sized(size[0], size[1], cfg):
                self.diag["not_ball"] = self.diag.get("not_ball", 0) + 1  # sized like a shirt, not a ball
                continue
            ev = self._with_calibration_uncertainty(ev)
            params = dict(ev.provenance.params or {})
            if rr is not None:
                params["r_ratio"] = round(rr, 3)
                params["r_ball_px"] = round(size[1], 2)
            if unsettled:  # cut by a flush less than settle_s after the bounce
                params["unsettled"] = True
            ev = ev.model_copy(update={"provenance": ev.provenance.model_copy(update={"params": params})})
            self._emitted.append(ev.t)
            self._emitted = self._emitted[-50:]
            self.bounces += 1
            out.append({"kind": "bounce", "camera": self.camera_id, "event": ev.model_dump(mode="json")})
        return out


    def _ball_size(self, tr: Track, tb: float, px) -> tuple[float, float] | None:
        """(median blob radius within 60 ms of the bounce, a ball's radius at the bounce point), px."""
        if self.camera is None or px is None or px[0] is None:
            return None
        rs = [p.radius_px for p in tr.points if abs(p.t - tb) <= 0.06]
        if not rs:
            return None
        r = self.court.ball_radius
        try:
            P = self.camera.intersect_plane_z(np.array([px], float), r)
            depth = float(self.camera.depth(np.asarray(P, float).reshape(1, 3))[0])
        except Exception:  # pragma: no cover - a ray parallel to the court
            return None
        if not np.isfinite(depth) or depth <= 0.2:
            return None
        return float(np.median(rs)), float(self.camera.K[0, 0]) * r / depth

    def _with_calibration_uncertainty(self, ev: BounceEvent) -> BounceEvent:
        """cov += sigma^2 J J^T, J = d(ground x, y) / d(pixel u, v) at the bounce pixel."""
        sig = self.cfg.calib_sigma_px
        if not sig or self.camera is None or ev.pixel is None:
            return ev
        J = ground_jacobian(self.camera, ev.pixel, self.court.ball_radius)
        if J is None:  # the pixel's ray misses the ground: no floor added (counted, not silent)
            self.diag["no_calib_floor"] = self.diag.get("no_calib_floor", 0) + 1
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


def ball_sized(r_blob: float, r_ball: float, cfg: LiveConfig) -> bool:
    """Is a blob of radius ``r_blob`` (px) plausibly a ball whose radius there is ``r_ball``?"""
    if cfg.max_ball_radius_ratio is not None and r_blob > cfg.max_ball_radius_ratio * r_ball + cfg.ball_radius_slack_px:
        return False
    if cfg.min_ball_radius_ratio is not None and r_blob < cfg.min_ball_radius_ratio * r_ball:
        return False
    return True


def handle_dets(pipe: LiveCameraPipeline, frames: list, size: tuple[int, int], lag: float) -> list[dict]:
    """One batch of an edge camera's candidates, as the live worker handles it ``lag`` seconds
    after it arrived. Besides the pipeline's output, returns "ctl" messages recording what was
    done because of load (frames dropped, bounce checks deferred). The server logs them, and
    ``bt replay`` applies them, so a call that depended on the Mac's load replays the same."""
    cfg = pipe.cfg
    out: list[dict] = []
    if lag > cfg.drop_after_s and frames:  # far behind: drop these frames to catch up
        pipe.diag["dropped_stale"] = pipe.diag.get("dropped_stale", 0) + len(frames)
        out.append({"kind": "ctl", "camera": pipe.camera_id, "op": "drop", "seq0": frames[0][0],
                    "seq1": frames[-1][0], "t0": frames[0][1], "t1": frames[-1][1]})
        out.append({"kind": "gap", "camera": pipe.camera_id, "t0": frames[0][1], "t1": frames[-1][1]})
        frames = []
    defer = lag > cfg.defer_after_s
    if frames and defer != pipe.defer_checks:
        out.append({"kind": "ctl", "camera": pipe.camera_id, "op": "defer", "on": defer, "seq": frames[0][0]})
        pipe.defer_checks = defer
    for seq, t, cl in frames:
        cands = [Candidate(u=u, v=v, radius_px=r, score=sc, area_px=float(np.pi * r * r), elongation=1.0)
                 for u, v, r, sc in cl]
        out += pipe.process_candidates(seq, t, cands, size)
    if frames:
        out.append({"kind": "progress", "camera": pipe.camera_id, "t": pipe._last_t})
    return out


class SilenceFlusher:
    """When to end open tracks because no frames arrive (a stall, the stream stopping): after
    ``cfg.flush_after_s`` of silence, once per silence. The worker loop calls ``frames(now)``
    when frames arrive and ``idle(now)`` while waiting; ``idle`` returns the flush output."""

    def __init__(self, pipe: LiveCameraPipeline):
        self.pipe = pipe
        self.last_frame = float("-inf")
        self.flushed = True
        self.last_seq = -1

    def frames(self, now: float, last_seq: int) -> None:
        self.last_frame, self.flushed, self.last_seq = now, False, last_seq

    def idle(self, now: float) -> list[dict]:
        if self.flushed or now - self.last_frame <= self.pipe.cfg.flush_after_s:
            return []
        self.flushed = True
        return flush_ctl(self.pipe, self.last_seq)


def flush_ctl(pipe: LiveCameraPipeline, last_seq: int) -> list[dict]:
    """End all tracks (no frames for a while), recorded for replay."""
    return [{"kind": "ctl", "camera": pipe.camera_id, "op": "flush", "seq": last_seq}] + pipe.flush()


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
    last_progress = -1e9
    silence = SilenceFlusher(pipe)
    while True:
        msg = decoded.get()
        if msg is None:
            for o in silence.idle(time.monotonic()):  # no frames for a while: finish open tracks now
                out_q.put(o)
        if msg is not None:
            kind = msg[0]
            if kind == "stop":
                for o in pipe.flush():
                    out_q.put(o)
                break
            if kind == "timing":  # ("timing", regularize: bool), sent on every (re)connect
                pipe.set_time_regularization(bool(msg[1]))
            elif kind == "fps":  # ("fps", frames per second the camera was asked for)
                pipe.set_fps(float(msg[1]))
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
                    if pipe._last_t - last_progress >= 0.05:
                        out_q.put({"kind": "progress", "camera": camera_id, "t": pipe._last_t})
                        last_progress = pipe._last_t
                b = time.monotonic()
                busy += b - a
                lat_sum += b - t_recv
                silence.frames(b, last_seq)
            elif kind == "dets":
                # ("dets", [(seq, t_session, [(u, v, r, score), ...]), ...], (w, h), t_recv)
                _, frames, size, t_recv = msg
                a = time.monotonic()
                for o in handle_dets(pipe, frames, size, a - t_recv):
                    out_q.put(o)
                    if o.get("kind") == "ctl" and o.get("op") == "drop":
                        frames = []
                n += len(frames)
                if frames:
                    last_seq = frames[-1][0]
                b = time.monotonic()
                busy += b - a
                lat_sum += (b - t_recv) * len(frames)
                silence.frames(b, last_seq)
        while pipe.warnings:
            out_q.put({"kind": "warning", "camera": camera_id, "text": pipe.warnings.pop(0)})
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
