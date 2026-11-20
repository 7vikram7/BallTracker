"""Live server: phones stream frames in, line calls come out.

Run with ``bt serve``. It serves

* ``https://<mac>:8443/phone``      the capture page (open it on each phone)
* ``http://localhost:8080/``        the dashboard (open it on the Mac)
* ``http://<mac>:8080/ca.crt``      the local CA certificate (install on phones)

Data flow::

    phone --JPEG + capture time--> ws_camera --(clock sync)--> worker process (per camera)
          worker: detect -> track -> bounce --> LiveJudge (fusion + line call) --> dashboard (speaks OUT)

    app   --detections + capture time--> ws_camera (same endpoint, protocol 2, "edge" camera)
          worker: track -> bounce (no decoding, no detection: the phone did that)

Session clock: seconds since the server started (``time.monotonic``). Every
phone timestamp is mapped onto it with that phone's ``ClockSync``.
"""

from __future__ import annotations

import asyncio
import csv
import io
import json
import logging
import multiprocessing as mp
import queue as queue_mod
import re
import ssl
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from aiohttp import WSMsgType, web

from ..events import BounceEvent
from ..geometry.calib_check import NET_TOP_POINTS, suspect_points
from ..geometry.camera import CalibrationError, Camera, calibrate_from_points
from ..geometry.court import CourtSpec, ServiceSide, Side
from ..geometry.crosscal import BouncePairs, Pair, other_end_proposal, refine_with_bounces, resnap_proposal, visible_keypoints
from ..sports.pickleball.line_calling import LineCallConfig, PickleballLineCaller, ServeContext
from .clocksync import ClockSync
from .fusion import Decision, LiveJudge
from .protocol import DETS_MAGIC, FRAME_MAGIC, PREVIEW_MAGIC, PROTO_VERSION, magic_of, unpack_detections, unpack_frame

log = logging.getLogger("balltracker.live")
STATIC = Path(__file__).parent / "static"
# Android app for sideloading from the dashboard (built with `./gradlew assembleRelease` in mobile/android).
APK = Path(__file__).resolve().parents[2] / "mobile" / "android" / "app" / "build" / "outputs" / "apk" / "release" / "app-release.apk"
NAME_RE = re.compile(r"[^A-Za-z0-9_-]+")


def clean_name(s: str) -> str:
    s = NAME_RE.sub("-", (s or "").strip())[:40].strip("-")
    return s or "camera"


class Recorder:
    """Append-only per-camera recording: frames.bin (JPEGs back to back) + index.csv, and
    dets.jsonl (on-phone detections). Files are created on first write."""

    def __init__(self, folder: Path):
        self.folder = folder
        self.bin = None
        self.idx_f = None

    def write(self, seq: int, t_phone: float, t_session: float, w: int, h: int, jpeg: bytes) -> None:
        if self.bin is None:
            self.folder.mkdir(parents=True, exist_ok=True)
            self.bin = open(self.folder / "frames.bin", "ab")
            new = not (self.folder / "index.csv").exists()
            self.idx_f = open(self.folder / "index.csv", "a", newline="")
            self.idx = csv.writer(self.idx_f)
            if new:
                self.idx.writerow(["seq", "t_phone", "t_session", "offset", "nbytes", "width", "height"])
        off = self.bin.tell()
        self.bin.write(jpeg)
        self.idx.writerow([seq, f"{t_phone:.6f}", f"{t_session:.6f}", off, len(jpeg), w, h])

    def write_dets(self, seq: int, t_phone: float, t_session: float, cands: list, size: tuple[int, int] = (0, 0)) -> None:
        if not hasattr(self, "dets_f"):
            self.folder.mkdir(parents=True, exist_ok=True)
            self.dets_f = open(self.folder / "dets.jsonl", "a")
        self.dets_f.write(json.dumps({"seq": seq, "tp": round(t_phone, 6), "ts": round(t_session, 6), "w": size[0], "h": size[1],
                                      "c": [[round(x, 4) for x in c] for c in cands]}) + "\n")

    def close(self) -> None:
        if self.bin is not None:
            self.bin.close()
            self.idx_f.close()
        if hasattr(self, "dets_f"):
            self.dets_f.close()


@dataclass
class CamState:
    name: str
    clock: ClockSync = field(default_factory=ClockSync)
    ws: web.WebSocketResponse | None = None
    connected: bool = False
    device: str = ""
    width: int = 0
    height: int = 0
    fps_req: float = 0.0
    ts_source: str = ""
    proc: mp.Process | None = None
    in_q: object = None
    frames_in: int = 0
    drops: int = 0
    unsynced: int = 0
    last_seq: int = -1
    seq_gaps: int = 0
    arrivals: deque = field(default_factory=lambda: deque(maxlen=240))
    latest_jpeg: bytes | None = None
    latest_size: tuple[int, int] = (0, 0)
    camera: Camera | None = None
    stats: dict = field(default_factory=dict)
    phone_stats: dict = field(default_factory=dict)
    recorder: Recorder | None = None
    pings: dict = field(default_factory=dict)
    last_ball: dict | None = None
    mode: str = "browser"  # "browser" (JPEG frames) or "edge" (native app sends detections)
    app: dict = field(default_factory=dict)
    reduced: bool = False  # the phone sends a reduced frame stream (seq jumps are intended)
    skipped_by_phone: int = 0  # frames the phone chose not to send
    cal_jpeg: bytes | None = None  # the frame the calibration dialog shows (snap works on the same image)
    cal_points: dict = field(default_factory=dict)  # the points of the last saved calibration
    proposal: dict | None = None  # refined calibration offered for review (geometry/crosscal.py)
    pairs: BouncePairs = field(default_factory=BouncePairs)  # bounces shared with the reference camera

    def fps_in(self) -> float:
        a = self.arrivals
        # max/min, not last/first: a clock-sync correction can step the converted capture times
        # backwards (field 2026-11-20: a Redmi showed -1202 fps).
        span = (max(a) - min(a)) if len(a) >= 2 else 0.0
        return (len(a) - 1) / span if span > 0 else 0.0


class LiveServer:
    def __init__(self, court: CourtSpec, data_dir: Path, *, record: bool = False,
                 detector_overrides: dict | None = None, https_port: int = 8443, http_port: int = 8080,
                 queue_frames: int = 45, hold_s: float = 0.6, reduce: bool = True):
        self.court = court
        self.data_dir = Path(data_dir)
        # Calibrations belong to a court: a practice court gets its own folder, so a camera
        # calibrated on the mini court is never used on the full court (and vice versa).
        sc = getattr(court, "scale", 1.0)
        self.calib_dir = self.data_dir / ("calibration" if sc == 1.0 else f"calibration-scale{sc:g}")
        self.reference_cam: str | None = None  # last camera the user confirmed (crosscal bounce pairs)
        self.calib_dir.mkdir(parents=True, exist_ok=True)
        self.session_dir = self.data_dir / "sessions" / time.strftime("%Y%m%d-%H%M%S")
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.record = record
        # Phone-side data reduction (mobile/src/core/reducer.js): still clutter dropped, full frame
        # rate only around bounces / hits. Off with `bt serve --full-rate` (e.g. to collect
        # complete per-frame data for research).
        self.reduce = reduce
        self.detector_overrides = detector_overrides or {}
        self.https_port, self.http_port = https_port, http_port
        self.queue_frames = queue_frames
        self.t0 = time.monotonic()
        self.cams: dict[str, CamState] = {}
        self.dashboards: set[web.WebSocketResponse] = set()
        self.judge = LiveJudge(court, PickleballLineCaller(court, LineCallConfig()), hold_s=hold_s, can_see=self.can_see)
        self.recent: deque = deque(maxlen=300)
        self.events_f = open(self.session_dir / "events.jsonl", "a")
        self.mp = mp.get_context("spawn")
        self.out_q = self.mp.Queue()
        self.phone_urls: list[str] = []
        self.app_urls: list[str] = []  # ws:// addresses for the native app (protocol 2)
        self.ca_url: str | None = None
        self._stop = threading.Event()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._tasks: list[asyncio.Task] = []
        (self.session_dir / "court.json").write_text(json.dumps(court.to_dict(), indent=2))
        self.all_decisions: list[dict] = []  # every decision of the session (recent is bounded)
        self.n_reports = 0
        from .session_log import build_manifest, write_manifest

        self.manifest = build_manifest(self)
        write_manifest(self)

    # ------------------------------------------------------------- clocks
    def now(self) -> float:
        return time.monotonic() - self.t0

    # ------------------------------------------------------------- cameras
    def _load_calibration(self, name: str) -> Camera | None:
        p = self.calib_dir / f"{name}.json"
        if p.exists():
            try:
                return Camera.load(p)
            except Exception as e:  # pragma: no cover - corrupt file
                log.warning("could not load calibration %s: %s", p, e)
        return None

    def _ensure_worker(self, cam: CamState) -> None:
        if cam.proc is not None and cam.proc.is_alive():
            return
        from .worker import run_worker

        cam.in_q = self.mp.Queue(maxsize=self.queue_frames)
        cam.proc = self.mp.Process(
            target=run_worker, name=f"bt-worker-{cam.name}", daemon=True,
            args=(cam.name, self.court.to_dict(), cam.camera.to_dict() if cam.camera else None,
                  cam.in_q, self.out_q, self.detector_overrides),
        )
        cam.proc.start()

    def get_cam(self, name: str) -> CamState:
        if name not in self.cams:
            cam = CamState(name)
            cam.camera = self._load_calibration(name)
            self.cams[name] = cam
        return self.cams[name]

    def _snapshot_calibration(self, cam: CamState) -> None:
        """Copy the camera model in use into the session folder (for replay and reports)."""
        if cam.camera is not None:
            d = self.session_dir / "calibration"
            d.mkdir(exist_ok=True)
            cam.camera.save(d / f"{cam.name}.json")

    def set_camera_model(self, cam: CamState, camera: Camera | None) -> None:
        cam.camera = camera
        if camera is not None:
            camera.save(self.calib_dir / f"{cam.name}.json")
            self._snapshot_calibration(cam)
        if cam.mode == "edge" and cam.ws is not None and not cam.ws.closed and self._loop is not None:
            self._loop.create_task(self._send_safe(cam.ws, self._calibration_msg(cam)))
        if cam.in_q is not None:
            try:
                cam.in_q.put(("camera", camera.to_dict() if camera else None), timeout=1.0)
            except queue_mod.Full:
                log.warning("worker queue full; calibration for %s not delivered yet", cam.name)

    def _config_msg(self, cam: CamState) -> dict:
        return {"type": "config", "detector": self.edge_detector_config(cam.fps_req), "reduce": {"enabled": cam.reduced}}

    def edge_detector_config(self, fps: float) -> dict:
        from ..edge_detection import EdgeDetectorConfig

        cfg = EdgeDetectorConfig(fps=float(fps) if fps else 60.0)
        for k, v in self.detector_overrides.items():
            if hasattr(cfg, k):
                setattr(cfg, k, tuple(v) if isinstance(v, list) else v)
        return cfg.to_dict()

    def _calibration_msg(self, cam: CamState) -> dict:
        return {"type": "calibration", "camera": cam.camera.to_dict() if cam.camera else None,
                "court": self.court.to_dict()}

    @staticmethod
    async def _send_safe(ws: web.WebSocketResponse, obj: dict) -> None:
        try:
            await ws.send_json(obj)
        except (ConnectionError, RuntimeError):
            pass

    # ------------------------------------------------------------- events
    def _log_event(self, obj: dict) -> None:
        self.recent.append(obj)
        self.events_f.write(json.dumps(obj) + "\n")
        self.events_f.flush()

    async def _broadcast(self, obj: dict) -> None:
        if not self.dashboards:
            return
        data = json.dumps(obj)
        for ws in list(self.dashboards):
            try:
                await ws.send_str(data)
            except (ConnectionError, RuntimeError):
                self.dashboards.discard(ws)

    def _broadcast_soon(self, obj: dict) -> None:
        if self._loop is not None:
            self._loop.create_task(self._broadcast(obj))

    def _on_worker_msg(self, msg: dict) -> None:
        kind = msg.get("kind")
        cam = self.cams.get(msg.get("camera", ""))
        if kind == "bounce":
            ev = BounceEvent.model_validate(msg["event"])
            self.judge.add(ev, self.now())
            self.n_reports += 1
            obj = {"type": "report", "camera": msg["camera"], "t": ev.t, "x": ev.position.x, "y": ev.position.y,
                   "std_cm": 100 * float(np.sqrt(max(np.trace(np.array(ev.cov_xy)) / 2, 0))),
                   "conf": ev.confidence, "delay_s": self.now() - ev.t, "event": msg["event"]}
            self._log_event(obj)
            self._broadcast_soon({k: v for k, v in obj.items() if k != "event"})
        elif kind == "ball" and cam is not None:
            cam.last_ball = msg
            self._broadcast_soon({"type": "ball", **msg})
        elif kind == "stats" and cam is not None:
            cam.stats = msg
        elif kind == "camera_set" and cam is not None:
            log.info("worker %s calibrated=%s", cam.name, msg.get("calibrated"))
        elif kind == "warning":
            self._log_event({"type": "warning", **msg})
            self._broadcast_soon({"type": "warning", **msg})

    def _reader_thread(self) -> None:
        while not self._stop.is_set():
            try:
                msg = self.out_q.get(timeout=0.2)
            except queue_mod.Empty:
                continue
            except (EOFError, OSError):
                break
            if self._loop is not None:
                self._loop.call_soon_threadsafe(self._on_worker_msg, msg)

    def can_see(self, name: str, x: float, y: float) -> bool:
        """Does calibrated camera ``name`` see the court point (x, y)?"""
        cam = self.cams.get(name)
        return cam is not None and camera_can_see(cam.camera, self.court, x, y)

    def expected_cameras(self) -> set[str]:
        return {c.name for c in self.cams.values() if c.connected and c.camera is not None}

    def _decision_obj(self, d: Decision) -> dict:
        return decision_dict(d, self.now() - d.bounce.t)

    async def _judge_loop(self) -> None:
        while True:
            await asyncio.sleep(0.05)
            for d in self.judge.poll(self.now(), self.expected_cameras()):
                obj = self._decision_obj(d)
                try:
                    self._collect_pairs(d)
                except Exception as e:  # pragma: no cover
                    log.warning("pair collection failed: %s", e)
                self._log_event(obj)
                self.all_decisions.append(obj)
                await self._broadcast(obj)
                if obj.get("announce"):
                    for cam in self.cams.values():
                        if cam.ws is not None and not cam.ws.closed:
                            try:
                                await cam.ws.send_json({"type": "call", "text": obj.get("text")})
                            except (ConnectionError, RuntimeError):
                                pass

    def state(self) -> dict:
        cams = []
        for c in sorted(self.cams.values(), key=lambda c: c.name):
            cams.append({
                "name": c.name, "connected": c.connected, "device": c.device, "width": c.width, "height": c.height,
                "fps_req": c.fps_req, "fps_in": c.fps_in(), "frames_in": c.frames_in, "drops": c.drops,
                "unsynced": c.unsynced, "seq_gaps": c.seq_gaps, "ts_source": c.ts_source,
                "clock": c.clock.summary(), "calibrated": c.camera is not None,
                "proposal": None if c.proposal is None else {k: v for k, v in c.proposal.items() if k != "camera"},
                "shared_bounces": len(c.pairs.pairs), "shared_disagreement_cm": c.pairs.disagreement_cm(),
                "calib_rms_px": c.camera.reprojection_rms_px if c.camera else None,
                "calib_size": list(c.camera.image_size) if c.camera else None,
                "proc_fps": c.stats.get("proc_fps"), "busy": c.stats.get("busy"),
                "latency_ms": c.stats.get("latency_ms"), "bounces": c.stats.get("bounces"),
                "worker_alive": bool(c.proc and c.proc.is_alive()), "phone": c.phone_stats,
                "cands_per_frame": c.stats.get("cands_per_frame"), "max_tracks": c.stats.get("max_tracks"),
                "mode": c.mode, "app": c.app,
            })
        ctx = self.judge.serve
        return {
            "type": "state", "t": self.now(), "cameras": cams, "phone_urls": self.phone_urls,
            "app_urls": self.app_urls, "apk": APK.exists(),
            "context": "rally" if ctx is None else f"serve:{ctx.server_side.value}:{ctx.service_side.value}",
            "recording": self.record, "session_dir": str(self.session_dir), "ca_url": self.ca_url,
            "court": {"length": self.court.length, "width": self.court.width},
        }

    async def _state_loop(self) -> None:
        from .session_log import camera_health

        k = 0
        while True:
            await asyncio.sleep(0.5)
            k += 1
            if k % 10 == 0:  # camera health into the session log every 5 s
                for c in self.cams.values():
                    if c.connected:
                        self._log_event({"type": "camera_stats", "t": self.now(), **camera_health(c)})
            for c in self.cams.values():
                if c.connected and c.proc is not None and not c.proc.is_alive():
                    log.error("worker for %s died (exit code %s); restarting", c.name, c.proc.exitcode)
                    self._log_event({"type": "warning", "camera": c.name, "text": "worker restarted", "t": self.now()})
                    if c.in_q is not None:
                        c.in_q.cancel_join_thread()
                    c.proc = None
                    self._ensure_worker(c)
            st = self.state()
            await self._broadcast(st)
            for c in self.cams.values():
                if c.ws is not None and not c.ws.closed:
                    try:
                        await c.ws.send_json({"type": "status", "calibrated": c.camera is not None,
                                              "proc_fps": c.stats.get("proc_fps"), "fps_in": c.fps_in(),
                                              "drops": c.drops, "rtt_ms": c.clock.summary()["rtt_ms"],
                                              "latency_ms": c.stats.get("latency_ms")})
                    except (ConnectionError, RuntimeError):
                        pass

    # ------------------------------------------------------------- handlers
    async def ws_camera(self, request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse(max_msg_size=16 * 1024 * 1024, heartbeat=15)
        await ws.prepare(request)
        try:
            hello = await ws.receive_json(timeout=15)
        except Exception:
            await ws.close()
            return ws
        if hello.get("type") != "hello":
            await ws.close()
            return ws
        name = clean_name(hello.get("name", ""))
        cam = self.get_cam(name)
        if cam.connected and cam.ws is not None and not cam.ws.closed:
            await cam.ws.close(message=b"replaced by a new connection")
        cam.ws, cam.connected = ws, True
        cam.device = str(hello.get("device", ""))[:120]
        cam.width, cam.height = int(hello.get("width", 0)), int(hello.get("height", 0))
        cam.fps_req = float(hello.get("fps", 0) or 0)
        cam.ts_source = str(hello.get("ts_source", ""))[:40]
        cam.mode = "edge" if hello.get("mode") == "edge" else "browser"
        cam.app = {k: str(hello.get(k, ""))[:40] for k in ("app_version", "algo", "algo_version", "platform")} \
            if cam.mode == "edge" else {}
        if cam.mode == "edge" and not cam.ts_source:
            cam.ts_source = "app:sensor"
        cam.clock = ClockSync()
        cam.pings = {}
        cam.arrivals.clear()
        cam.frames_in = cam.drops = cam.unsynced = cam.seq_gaps = cam.skipped_by_phone = 0
        cam.last_seq = -1
        cam.reduced = cam.mode == "edge" and self.reduce and "reduce" in hello  # the app supports it
        cam.phone_stats = {}
        self._ensure_worker(cam)
        # Browser timestamps jitter by a few ms: snap them to the frame grid. App cameras send sensor time.
        regularize = cam.mode == "browser" or cam.app.get("platform") == "browser"
        try:
            cam.in_q.put(("timing", regularize), timeout=1.0)
        except queue_mod.Full:
            log.warning("worker queue full; timing mode for %s not set", name)
        # Detections from on-phone cameras are always recorded (tiny; makes every session replayable).
        # Video frames / previews only with --record.
        if (self.record or cam.mode == "edge") and cam.recorder is None:
            cam.recorder = Recorder(self.session_dir / name)
        await ws.send_json({"type": "welcome", "name": name, "calibrated": cam.camera is not None, "proto": PROTO_VERSION})
        if cam.mode == "edge":
            await ws.send_json(self._config_msg(cam))
            await ws.send_json(self._calibration_msg(cam))
        self._snapshot_calibration(cam)
        self._log_event({"type": "camera_connected", "camera": name, "device": cam.device, "t": self.now(),
                         "mode": cam.mode, "app": cam.app, "width": cam.width, "height": cam.height,
                         "fps": cam.fps_req, "ts_source": cam.ts_source,
                         "calibrated": cam.camera is not None, "regularize_time": regularize,
                         "reduced": cam.reduced,
                         "detector_config": self.edge_detector_config(cam.fps_req) if cam.mode == "edge" else None})
        log.info("camera connected: %s (%s) %sx%s", name, cam.device, cam.width, cam.height)

        async def pinger() -> None:
            k = 0
            while not ws.closed:
                k += 1
                cam.pings[k] = time.monotonic()
                if len(cam.pings) > 50:
                    cam.pings.pop(next(iter(cam.pings)))
                try:
                    await ws.send_json({"type": "ping", "id": k, "ts": cam.pings[k]})
                except (ConnectionError, RuntimeError):
                    return
                await asyncio.sleep(0.2 if k < 15 else 1.0)

        ptask = asyncio.create_task(pinger())
        try:
            async for msg in ws:
                if msg.type == WSMsgType.BINARY:
                    magic = magic_of(msg.data)
                    if magic == FRAME_MAGIC:
                        self._on_frame(cam, msg.data)
                    elif magic == DETS_MAGIC:
                        self._on_dets(cam, msg.data)
                    elif magic == PREVIEW_MAGIC:
                        self._on_preview(cam, msg.data)
                elif msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                    except ValueError:
                        continue
                    typ = data.get("type")
                    if typ == "pong":
                        ts1 = time.monotonic()
                        ts0 = cam.pings.pop(data.get("id"), None)
                        if ts0 is not None and isinstance(data.get("tp"), (int, float)):
                            cam.clock.add(ts0, float(data["tp"]), ts1)
                    elif typ == "stats":
                        cam.phone_stats = {k: data[k] for k in list(data)[:20] if k != "type"}
                        if data.get("ts_source"):
                            cam.ts_source = str(data["ts_source"])[:40]
                    elif typ == "hello":  # resolution changed mid-session
                        cam.width, cam.height = int(data.get("width", 0)), int(data.get("height", 0))
                        if cam.mode == "edge" and data.get("fps"):
                            cam.fps_req = float(data["fps"])
                            await ws.send_json(self._config_msg(cam))
                elif msg.type == WSMsgType.ERROR:
                    break
        finally:
            ptask.cancel()
            if cam.ws is ws:
                cam.connected, cam.ws = False, None
            self._log_event({"type": "camera_disconnected", "camera": name, "t": self.now()})
            log.info("camera disconnected: %s", name)
        return ws

    def _on_frame(self, cam: CamState, data: bytes) -> None:
        try:
            f = unpack_frame(data)
        except ValueError:
            return
        now_mono = time.monotonic()
        cam.frames_in += 1
        cam.arrivals.append(now_mono)
        if cam.last_seq >= 0 and f.seq != cam.last_seq + 1:
            cam.seq_gaps += 1
        cam.last_seq = f.seq
        cam.latest_jpeg, cam.latest_size = f.jpeg, (f.width, f.height)
        if not cam.clock.ready:
            cam.unsynced += 1
            return
        t_session = cam.clock.to_server(f.t_phone) - self.t0
        if cam.recorder is not None:
            cam.recorder.write(f.seq, f.t_phone, t_session, f.width, f.height, f.jpeg)
        try:
            cam.in_q.put_nowait(("frame", f.seq, t_session, f.jpeg, now_mono))
        except queue_mod.Full:
            cam.drops += 1

    def _on_dets(self, cam: CamState, data: bytes) -> None:
        """Edge camera: a batch of per-frame ball candidates computed on the phone."""
        try:
            batch = unpack_detections(data)
        except ValueError:
            return
        now_mono = time.monotonic()
        cam.width, cam.height = batch.width, batch.height
        frames = []
        for f in batch.frames:
            cam.frames_in += 1
            if cam.last_seq >= 0 and f.seq != cam.last_seq + 1:
                if cam.reduced and f.seq > cam.last_seq:
                    cam.skipped_by_phone += f.seq - cam.last_seq - 1  # intended: phone-side reduction
                else:
                    cam.seq_gaps += 1
            cam.last_seq = f.seq
            if not cam.clock.ready:
                cam.unsynced += 1
                continue
            t_server = cam.clock.to_server(f.t_phone)
            cam.arrivals.append(t_server)  # capture times: fps_in is the phone's processed rate
            t_session = t_server - self.t0
            frames.append((f.seq, t_session, f.cands))
            if cam.recorder is not None:
                cam.recorder.write_dets(f.seq, f.t_phone, t_session, f.cands, (batch.width, batch.height))
        if not frames:
            return
        try:
            cam.in_q.put_nowait(("dets", frames, (batch.width, batch.height), now_mono))
        except queue_mod.Full:
            cam.drops += len(frames)

    def _on_preview(self, cam: CamState, data: bytes) -> None:
        try:
            f = unpack_frame(data, PREVIEW_MAGIC)
        except ValueError:
            return
        cam.latest_jpeg, cam.latest_size = f.jpeg, (f.width, f.height)
        if self.record and cam.recorder is not None and cam.clock.ready:
            cam.recorder.write(f.seq, f.t_phone, cam.clock.to_server(f.t_phone) - self.t0, f.width, f.height, f.jpeg)

    async def ws_dashboard(self, request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse(heartbeat=15)
        await ws.prepare(request)
        self.dashboards.add(ws)
        await ws.send_json(self.state())
        for obj in list(self.recent)[-80:]:
            await ws.send_json({k: v for k, v in obj.items() if k != "event"})
        try:
            async for _ in ws:
                pass
        finally:
            self.dashboards.discard(ws)
        return ws

    async def api_state(self, request: web.Request) -> web.Response:
        return web.json_response(self.state())

    async def api_court(self, request: web.Request) -> web.Response:
        c = self.court
        return web.json_response({
            "spec": c.to_dict(), "half_w": c.half_w, "half_l": c.half_l, "kitchen": c.kitchen_depth,
            "lines": [{"name": s.name, "x0": s.rect.x0, "x1": s.rect.x1, "y0": s.rect.y0, "y1": s.rect.y1} for s in c.lines()],
            # Net-top points are left out of the click list: on a portable net the posts stand outside
            # the sidelines and higher than the net, and clicking them spoiled calibrations (field test 2).
            "keypoints": {k: list(v) for k, v in c.keypoints().items()
                          if request.query.get("all") or k not in NET_TOP_POINTS},
        })

    async def api_frame(self, request: web.Request) -> web.Response:
        cam = self.cams.get(request.match_info["name"])
        if cam is None or cam.latest_jpeg is None:
            raise web.HTTPNotFound(text="no frame yet")
        if request.query.get("cal"):
            cam.cal_jpeg = cam.latest_jpeg
        return web.Response(body=cam.latest_jpeg, content_type="image/jpeg", headers={"Cache-Control": "no-store"})

    async def api_overlay(self, request: web.Request) -> web.Response:
        import cv2

        cam = self.cams.get(request.match_info["name"])
        if cam is None or cam.latest_jpeg is None:
            raise web.HTTPNotFound(text="no frame yet")
        img = cv2.imdecode(np.frombuffer(cam.latest_jpeg, np.uint8), cv2.IMREAD_COLOR)
        if cam.camera is not None:
            draw_court(img, cam.camera, self.court)
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return web.Response(body=buf.tobytes(), content_type="image/jpeg", headers={"Cache-Control": "no-store"})

    async def api_calibrate(self, request: web.Request) -> web.Response:
        cam = self.cams.get(request.match_info["name"])
        if cam is None:
            raise web.HTTPNotFound(text="unknown camera")
        body = await request.json()
        if body.get("clear"):
            (self.calib_dir / f"{cam.name}.json").unlink(missing_ok=True)
            self.set_camera_model(cam, None)
            return web.json_response({"ok": True, "cleared": True})
        pts = body.get("points") or {}
        size = body.get("image_size") or list(cam.latest_size)
        kp = self.court.keypoints()
        names = [k for k in pts if k in kp]
        if len(names) < 4:
            return web.json_response({"ok": False, "error": "Need at least 4 points (6+ recommended)."}, status=400)
        obj = np.array([kp[k] for k in names], float)
        imgp = np.array([pts[k] for k in names], float)
        try:
            camera = calibrate_from_points(obj, imgp, (int(size[0]), int(size[1])), camera_id=cam.name,
                                           estimate_focal=len(names) >= 6)
        except CalibrationError as e:
            return web.json_response({"ok": False, "error": str(e)}, status=400)
        reproj = camera.project(obj)
        errs = np.linalg.norm(reproj - imgp, axis=1)
        try:
            suspects = suspect_points(names, obj, imgp, (int(size[0]), int(size[1])))
        except CalibrationError:
            suspects = []
        self.set_camera_model(cam, camera)
        cam.cal_points = {k: list(map(float, pts[k])) for k in names}
        cam.proposal = None
        # This camera is now the reference for the others: their shared-bounce pairs were measured
        # against older calibrations, so start collecting again; and re-snap every other camera.
        self.reference_cam = cam.name
        for other in self.cams.values():
            other.pairs = BouncePairs()
        asyncio.get_running_loop().create_task(self._refine_others(cam.name))
        pos = camera.position
        self._log_event({"type": "calibrated", "camera": cam.name, "t": self.now(), "rms_px": camera.reprojection_rms_px,
                         "source": body.get("source", "clicks"),
                         "points": len(names), "image_size": [int(size[0]), int(size[1])],
                         "clicked": {k: list(map(float, pts[k])) for k in names},
                         "per_point_px": {k: float(e) for k, e in zip(names, errs)}, "camera_model": camera.to_dict(),
                         "suspects": suspects})
        return web.json_response({
            "ok": True, "rms_px": camera.reprojection_rms_px, "points": len(names),
            "per_point_px": {k: float(e) for k, e in zip(names, errs)}, "suspects": suspects,
            "camera_position_m": [float(x) for x in pos], "focal_px": camera.focal_px,
            "hfov_deg": float(np.degrees(2 * np.arctan(camera.image_size[0] / 2 / camera.focal_px))),
        })

    def _cal_image(self, cam: CamState):
        import cv2

        jpg = cam.cal_jpeg or cam.latest_jpeg
        return None if jpg is None else cv2.imdecode(np.frombuffer(jpg, np.uint8), cv2.IMREAD_COLOR)

    async def api_snap(self, request: web.Request) -> web.Response:
        """Snap rough points (>= 4 taps, or the current calibration) to the court lines; returns
        every keypoint for review. Nothing is saved until the user presses Calibrate."""
        from ..geometry.autocal import autocalibrate, refine_from

        cam = self.cams.get(request.match_info["name"])
        if cam is None:
            raise web.HTTPNotFound(text="unknown camera")
        img = self._cal_image(cam)
        if img is None:
            return web.json_response({"ok": False, "error": "No image from this camera yet."}, status=400)
        body = await request.json()
        pts = {k: v for k, v in (body.get("points") or {}).items() if k in self.court.keypoints()}
        loop = asyncio.get_running_loop()
        if len(pts) >= 4:
            res = await loop.run_in_executor(None, refine_from, img, self.court, pts)
            how = "your points"
        elif cam.camera is not None:
            res = await loop.run_in_executor(None, refine_from, img, self.court, visible_keypoints(cam.camera, self.court))
            how = "the current calibration"
        else:
            res = await loop.run_in_executor(None, autocalibrate, img, self.court)
            how = "nothing (fully automatic, experimental)"
        d = res.debug or {}
        self._log_event({"type": "snap", "camera": cam.name, "t": self.now(), "ok": res.ok, "from": how,
                         "fit_px": d.get("fit_px"), "lines": d.get("lines"), "inliers": d.get("inliers"),
                         "points": res.points})
        return web.json_response({"ok": res.ok, "points": res.points, "from": how, "message": res.message,
                                  "fit_px": d.get("fit_px"), "lines": d.get("lines"), "inliers": d.get("inliers"),
                                  "ambiguous": res.ambiguous, "flipped_points": res.flipped_points,
                                  "image_size": [int(img.shape[1]), int(img.shape[0])]})

    async def api_proposal(self, request: web.Request) -> web.Response:
        cam = self.cams.get(request.match_info["name"])
        if cam is None:
            raise web.HTTPNotFound(text="unknown camera")
        body = await request.json()
        if body.get("action") == "dismiss":
            self._log_event({"type": "proposal_dismissed", "camera": cam.name, "t": self.now(),
                             "source": (cam.proposal or {}).get("source")})
            cam.proposal = None
            await self._broadcast(self.state())
        return web.json_response({"ok": True})

    async def _refine_others(self, confirmed: str) -> None:
        """After a camera is confirmed: snap every other calibrated camera to its court lines and
        offer the result for review (geometry/crosscal.py)."""
        loop = asyncio.get_running_loop()
        for cam in list(self.cams.values()):
            if cam.name == confirmed or cam.camera is None or cam.latest_jpeg is None:
                continue
            img = self._cal_image(cam)
            try:
                prop = await loop.run_in_executor(None, resnap_proposal, img, self.court, cam.camera)
            except Exception as e:  # pragma: no cover - never break the server for a proposal
                log.warning("re-snap of %s failed: %s", cam.name, e)
                continue
            if prop:
                cam.proposal = {**prop, "after": confirmed, "t": self.now()}
                self._log_event({"type": "proposal", "camera": cam.name, "t": self.now(),
                                 **{k: v for k, v in prop.items() if k != "camera"}})
                await self._broadcast(self.state())

    def _collect_pairs(self, d: Decision) -> None:
        """Bounces seen by the reference camera and another camera -> ground correspondences for
        the other camera; propose a refined calibration once there are enough."""
        ref = self.reference_cam
        if ref is None or d.suppressed or len(d.sources) < 2:
            return
        by_cam = {e.camera_ids[0]: e for e in d.sources if len(e.camera_ids) == 1}
        r = by_cam.get(ref)
        if r is None:
            return
        for name, e in by_cam.items():
            cam = self.cams.get(name)
            if name == ref or cam is None or cam.camera is None or e.pixel is None:
                continue
            cam.pairs.add(Pair(e.t, tuple(e.pixel), (r.position.x, r.position.y), ref, (e.position.x, e.position.y)))
            n = len(cam.pairs.pairs)
            if (cam.proposal or {}).get("source") != "other_end":
                kp = cam.cal_points or visible_keypoints(cam.camera, self.court)
                flip = other_end_proposal(cam.pairs, self.court, kp)
                if flip:
                    cam.proposal = flip | {"t": self.now()}
                    self._log_event({"type": "proposal", "camera": cam.name, "t": self.now(), **cam.proposal})
                    continue
            if cam.pairs.ready(min_spread_m=max(2.0 * float(getattr(self.court, "scale", 1.0) or 1.0), 0.3)) and (cam.proposal is None or cam.proposal.get("source") != "bounces") and n % 5 == 0:
                kp = cam.cal_points or visible_keypoints(cam.camera, self.court)
                prop = refine_with_bounces(cam.camera, self.court, kp, cam.pairs)
                if prop:
                    cam.proposal = {k: v for k, v in prop.items() if k != "camera"} | {"t": self.now()}
                    self._log_event({"type": "proposal", "camera": cam.name, "t": self.now(), **cam.proposal})

    async def api_context(self, request: web.Request) -> web.Response:
        body = await request.json()
        if body.get("mode") == "serve":
            self.judge.serve = ServeContext(Side(str(body["server_side"]).upper()), ServiceSide(str(body["service_side"]).lower()))
        else:
            self.judge.serve = None
        ctx = self.state()["context"]
        self._log_event({"type": "context", "t": self.now(), "context": ctx})  # replay re-applies these
        return web.json_response({"ok": True, "context": ctx})

    async def page(self, request: web.Request) -> web.StreamResponse:
        name = request.match_info.get("page", "index")
        f = STATIC / f"{name}.html"
        if not f.exists():
            raise web.HTTPNotFound()
        return web.FileResponse(f, headers={"Cache-Control": "no-store"})

    STATIC_TYPES = {".js": "text/javascript", ".wasm": "application/wasm"}

    async def static_file(self, request: web.Request) -> web.StreamResponse:
        """Scripts and the WebAssembly detector for the phone page (/static/ballcore.wasm, ...)."""
        name = request.match_info["name"]
        f = STATIC / name
        ctype = self.STATIC_TYPES.get(f.suffix)
        if ctype is None or "/" in name or ".." in name or not f.is_file():
            raise web.HTTPNotFound()
        return web.FileResponse(f, headers={"Content-Type": ctype, "Cache-Control": "no-cache"})

    async def apk(self, request: web.Request) -> web.StreamResponse:
        if not APK.exists():
            raise web.HTTPNotFound(text="No Android build yet: run ./gradlew assembleRelease in mobile/android")
        return web.FileResponse(APK, headers={"Content-Type": "application/vnd.android.package-archive",
                                              "Content-Disposition": 'attachment; filename="BallTrackerCam.apk"'})

    async def ca_cert(self, request: web.Request) -> web.Response:
        p = self.data_dir / "tls" / "ca.crt"
        if not p.exists():
            raise web.HTTPNotFound(text="no CA (server running without TLS)")
        return web.Response(body=p.read_bytes(), content_type="application/x-x509-ca-cert",
                            headers={"Content-Disposition": 'attachment; filename="BallTracker-CA.crt"'})

    async def qr(self, request: web.Request) -> web.Response:
        import segno

        url = request.query.get("u") or (self.phone_urls[0] if self.phone_urls else "")
        buf = io.BytesIO()
        segno.make(url, error="m").save(buf, kind="svg", scale=5, border=2, dark="#111", light="#fff")
        return web.Response(body=buf.getvalue(), content_type="image/svg+xml")

    # ------------------------------------------------------------- app
    def make_app(self) -> web.Application:
        app = web.Application(client_max_size=4 * 1024 * 1024)
        app.router.add_get("/", self.page)
        app.router.add_get("/ws/camera", self.ws_camera)
        app.router.add_get("/ws/edge", self.ws_camera)  # native app (protocol 2); same handler
        app.router.add_get("/ws/dashboard", self.ws_dashboard)
        app.router.add_get("/api/state", self.api_state)
        app.router.add_get("/api/court", self.api_court)
        app.router.add_get("/api/cameras/{name}/frame.jpg", self.api_frame)
        app.router.add_get("/api/cameras/{name}/overlay.jpg", self.api_overlay)
        app.router.add_post("/api/cameras/{name}/calibrate", self.api_calibrate)
        app.router.add_post("/api/cameras/{name}/snap", self.api_snap)
        app.router.add_post("/api/cameras/{name}/proposal", self.api_proposal)
        app.router.add_post("/api/context", self.api_context)
        app.router.add_get("/ca.crt", self.ca_cert)
        app.router.add_get("/qr.svg", self.qr)
        app.router.add_get("/static/{name}", self.static_file)
        app.router.add_get("/app.apk", self.apk)
        app.router.add_get("/{page}", self.page)
        app.on_startup.append(self._on_startup)
        app.on_cleanup.append(self._on_cleanup)
        return app

    async def _on_startup(self, app: web.Application) -> None:
        self._loop = asyncio.get_running_loop()
        threading.Thread(target=self._reader_thread, name="bt-reader", daemon=True).start()
        self._tasks = [asyncio.create_task(self._judge_loop()), asyncio.create_task(self._state_loop())]

    async def _on_cleanup(self, app: web.Application) -> None:
        for t in self._tasks:
            t.cancel()
        for c in self.cams.values():
            if c.in_q is not None:
                try:
                    c.in_q.put(("stop",), timeout=0.5)
                except queue_mod.Full:
                    pass
        for c in self.cams.values():
            if c.proc is not None:
                c.proc.join(timeout=3)
                if c.proc.is_alive():
                    c.proc.terminate()
            if c.in_q is not None:
                c.in_q.cancel_join_thread()  # don't block exit flushing frames to a stopped worker
            if c.recorder is not None:
                c.recorder.close()
        # Late bounces from flushing workers, then the last decisions.
        deadline = time.monotonic() + 0.5
        while time.monotonic() < deadline:
            try:
                msg = self.out_q.get(timeout=0.05)
            except queue_mod.Empty:
                continue
            self._on_worker_msg(msg)
        for d in self.judge.flush():
            obj = self._decision_obj(d)
            self._log_event(obj)
            self.all_decisions.append(obj)
        from .session_log import finalize

        try:
            finalize(self)
        except Exception as e:  # never lose the session because the summary failed
            log.error("could not write session summary: %s", e)
        self._stop.set()
        self.events_f.close()


def camera_can_see(camera: Camera | None, court: CourtSpec, x: float, y: float) -> bool:
    """Is the court point (x, y) inside this camera's image (with a 3 % margin)?"""
    if camera is None:
        return False
    P = np.array([[x, y, court.ball_radius]])
    if camera.depth(P)[0] <= 0.2:
        return False
    u, v = camera.project(P)[0]
    w, h = camera.image_size
    return 0.03 * w <= u <= 0.97 * w and 0.03 * h <= v <= 0.97 * h


def decision_dict(d: Decision, latency_s: float | None) -> dict:
    """The logged form of a judge decision (events.jsonl, dashboard, replay)."""
    b, c = d.bounce, d.call
    obj = {
        "type": "decision", "t": b.t, "x": b.position.x, "y": b.position.y, "cov": b.cov_xy,
        "cameras": b.camera_ids, "confidence": b.confidence, "latency_s": latency_s,
        "n_reports": d.diagnostics.get("n"), "chi2": d.diagnostics.get("chi2"),
        "inflation": d.diagnostics.get("inflation"), "suppressed": d.suppressed,
        "unconfirmed_by": d.diagnostics.get("unconfirmed_by"),
        "cameras_disagree": d.diagnostics.get("cameras_disagree"),
        "play": d.diagnostics.get("play"), "h_in_mps": d.diagnostics.get("h_in_mps"),
        "vz_in_mps": d.diagnostics.get("vz_in_mps"),
    }
    if c is not None:
        obj.update(result=c.result.value, p_out=c.p_out, line=c.nearest_line,
                   distance_cm=100 * c.signed_distance_m, announce=c.announce, text=c.call_text,
                   context=c.context.value, region=c.target_region)
    return obj


def draw_court(img: np.ndarray, camera: Camera, court: CourtSpec, color=(0, 0, 255)) -> None:
    import cv2

    for seg in court.lines():
        r = seg.rect
        corners = np.array([[r.x0, r.y0, 0], [r.x1, r.y0, 0], [r.x1, r.y1, 0], [r.x0, r.y1, 0]], float)
        # Subdivide edges so lines behind the camera are skipped piecewise.
        for a, b in zip(corners, np.roll(corners, -1, axis=0)):
            pts = np.linspace(a, b, 20)
            ok = camera.depth(pts) > 0.1
            uv = camera.project(pts)
            for i in range(len(pts) - 1):
                if ok[i] and ok[i + 1]:
                    cv2.line(img, tuple(np.int32(uv[i])), tuple(np.int32(uv[i + 1])), color, 1, cv2.LINE_AA)
    for name, P in court.keypoints().items():
        P = np.array(P, float)[None]
        if camera.depth(P)[0] > 0.1:
            u, v = camera.project(P)[0]
            cv2.circle(img, (int(u), int(v)), 4, (0, 255, 255), 1, cv2.LINE_AA)


def run(court: CourtSpec, data_dir: Path, *, host: str | None = None, https_port: int = 8443, http_port: int = 8080,
        tls: bool = True, record: bool = False, detector_overrides: dict | None = None,
        reduce: bool = True) -> None:
    """Start the server (blocking)."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    srv = LiveServer(court, data_dir, record=record, detector_overrides=detector_overrides, reduce=reduce,
                     https_port=https_port, http_port=http_port)
    app = srv.make_app()
    from .certs import ensure_server_cert, lan_addresses, url_host

    # host None: listen on every IPv4 and IPv6 address (IPv6-only phone hotspots need IPv6).
    ips = [url_host(ip) for ip in lan_addresses()]
    srv.app_urls = [f"ws://{ip}:{http_port}/ws/edge" for ip in ips]
    ssl_ctx = None
    if tls:
        crt, key, hosts = ensure_server_cert(data_dir / "tls")
        ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_ctx.load_cert_chain(str(crt), str(key))
        srv.phone_urls = [f"https://{ip}:{https_port}/phone" for ip in ips]
        srv.ca_url = f"http://{ips[0]}:{http_port}/ca.crt" if ips else None
    else:
        srv.phone_urls = [f"http://{ip}:{http_port}/phone" for ip in ips]

    async def main() -> None:
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, host, http_port).start()
        if ssl_ctx is not None:
            await web.TCPSite(runner, host, https_port, ssl_context=ssl_ctx).start()
        print("\nBallTracker live server", flush=True)
        if court.scale != 1.0:
            print(f"  Court: PRACTICE, scale {court.scale:g} ({2 * court.half_w:.2f} m x {2 * court.half_l:.2f} m);"
                  f" calibrations in {srv.calib_dir.name}/")
        print(f"  Dashboard (on this Mac):  http://localhost:{http_port}/dashboard")
        for u in srv.phone_urls:
            print(f"  Phones (same Wi-Fi):      {u}")
        for u in srv.app_urls[:1]:
            print(f"  App (BallTracker Cam):    {u.split('//')[1].split('/')[0]}  (or scan the app QR on the dashboard)")
        if tls and ips:
            print(f"  CA certificate for phones: http://{ips[0]}:{http_port}/ca.crt  (optional, removes warnings)")
        print(f"  Session folder:           {srv.session_dir}")
        print("  Ctrl+C to stop.\n", flush=True)
        try:
            while True:
                await asyncio.sleep(3600)
        finally:
            await runner.cleanup()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
