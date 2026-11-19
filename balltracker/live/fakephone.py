"""A simulated phone: streams a video file or a synthetic scene to the live server.

Speaks exactly the phone page's protocol (hello, ping/pong clock sync, binary
JPEG frames with capture timestamps), so the whole server path can be tested
without real phones. Each fake phone can have its own clock offset and drift,
to check that clock sync really maps every camera onto one session clock.

``stream_edge_phone`` simulates the native app instead (protocol 2): it runs
the phone detector (``EdgeBallDetector``, the reference of the app's C++ code)
locally and sends only detections, plus a full-resolution preview JPEG once a
second.

Also provides ``run_live_demo``: an in-process server plus several fake phones
filming the same synthetic rally from different positions, scored against
ground truth.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

from .protocol import DetFrame, pack_detections, pack_frame, pack_preview


@dataclass
class PhoneClock:
    """Phone clock = (server monotonic + offset) * (1 + drift)."""

    offset_s: float = 0.0
    drift_ppm: float = 0.0

    def now(self) -> float:
        return self.at(time.monotonic())

    def at(self, mono: float) -> float:
        return (mono + self.offset_s) * (1 + self.drift_ppm * 1e-6)


def encode_frames(frames: Iterable[tuple[int, float, np.ndarray]], quality: int = 85) -> list[tuple[float, bytes, int, int]]:
    import cv2

    out = []
    for _, t, img in frames:
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if ok:
            out.append((t, buf.tobytes(), img.shape[1], img.shape[0]))
    return out


async def stream_phone(url: str, name: str, frames: list[tuple[float, bytes, int, int]], *, fps: float,
                       clock: PhoneClock | None = None, insecure: bool = True, sync_s: float = 1.5,
                       on_start=None, linger_s: float = 0.5) -> dict:
    """Connect, sync clocks, then send pre-encoded frames in real time.

    ``frames`` items are (t_in_clip, jpeg, width, height). Returns stats.
    ``on_start(mono_t0)`` is called with the monotonic time of clip t = 0.
    """
    import aiohttp

    clock = clock or PhoneClock()
    ssl = False if insecure else None
    stats = {"sent": 0, "late": 0}
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url, ssl=ssl, max_msg_size=0, heartbeat=15) as ws:
            w, h = (frames[0][2], frames[0][3]) if frames else (0, 0)
            await ws.send_json({"type": "hello", "proto": 1, "name": name, "device": "fakephone",
                                "width": w, "height": h, "fps": fps, "ts_source": "simulated"})

            async def receiver() -> None:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        m = json.loads(msg.data)
                        if m.get("type") == "ping":
                            await ws.send_json({"type": "pong", "id": m["id"], "tp": clock.now()})

            rx = asyncio.create_task(receiver())
            await asyncio.sleep(sync_s)
            t0 = time.monotonic() + 0.2
            if on_start is not None:
                on_start(t0)
            for seq, (t, jpeg, fw, fh) in enumerate(frames):
                target = t0 + t
                delay = target - time.monotonic()
                if delay > 0:
                    await asyncio.sleep(delay)
                elif delay < -0.05:
                    stats["late"] += 1
                await ws.send_bytes(pack_frame(seq, clock.at(target), fw, fh, jpeg))
                stats["sent"] += 1
            await asyncio.sleep(linger_s)
            rx.cancel()
    return stats


def edge_detections(frames: list[tuple[float, bytes, int, int]], fps: float,
                    detector_cfg: dict | None = None) -> list[tuple[float, list[tuple[float, float, float, float]]]]:
    """Run the phone detector over encoded frames: [(t, [(u, v, r, score), ...]), ...]."""
    import cv2

    from ..edge_detection import EdgeBallDetector, EdgeDetectorConfig

    cfg = EdgeDetectorConfig(fps=fps)
    for k, v in (detector_cfg or {}).items():
        if hasattr(cfg, k):
            setattr(cfg, k, tuple(v) if isinstance(v, list) else v)
    det = EdgeBallDetector(cfg)
    out = []
    for t, jpeg, _w, _h in frames:
        img = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
        out.append((t, [(c.u, c.v, c.radius_px, c.score) for c in det.detect(img)]))
    return out


async def stream_edge_phone(url: str, name: str, frames: list[tuple[float, bytes, int, int]],
                            dets: list[tuple[float, list]], *, fps: float, clock: PhoneClock | None = None,
                            insecure: bool = True, sync_s: float = 1.5, on_start=None, linger_s: float = 0.5,
                            batch_s: float = 0.05, preview_every_s: float = 1.0) -> dict:
    """Like ``stream_phone`` but speaks protocol 2 as the native app does."""
    import aiohttp

    clock = clock or PhoneClock()
    ssl = False if insecure else None
    stats = {"sent_frames": 0, "batches": 0, "previews": 0, "bytes": 0, "config": None}
    w, h = (frames[0][2], frames[0][3]) if frames else (0, 0)
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(url, ssl=ssl, max_msg_size=0, heartbeat=15) as ws:
            await ws.send_json({"type": "hello", "proto": 2, "mode": "edge", "name": name, "device": "fake-edge-phone",
                                "platform": "simulator", "width": w, "height": h, "fps": fps,
                                "ts_source": "simulated", "algo": "edge_color_motion", "algo_version": "1.0.0",
                                "app_version": "sim"})

            async def receiver() -> None:
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        m = json.loads(msg.data)
                        if m.get("type") == "ping":
                            await ws.send_json({"type": "pong", "id": m["id"], "tp": clock.now()})
                        elif m.get("type") == "config":
                            stats["config"] = m.get("detector")

            rx = asyncio.create_task(receiver())
            await asyncio.sleep(sync_s)
            t0 = time.monotonic() + 0.2
            if on_start is not None:
                on_start(t0)
            pending: list[DetFrame] = []
            next_send = t0 + batch_s
            next_preview = t0
            for seq, ((t, jpeg, fw, fh), (_, cands)) in enumerate(zip(frames, dets)):
                target = t0 + t
                if target >= next_send and pending:
                    delay = next_send - time.monotonic()
                    if delay > 0:
                        await asyncio.sleep(delay)
                    msg = pack_detections(fw, fh, pending)
                    await ws.send_bytes(msg)
                    stats["batches"] += 1
                    stats["bytes"] += len(msg)
                    pending = []
                    while next_send <= target:
                        next_send += batch_s
                pending.append(DetFrame(seq, clock.at(target), list(cands)))
                stats["sent_frames"] += 1
                if target >= next_preview:
                    delay = target - time.monotonic()
                    if delay > 0:
                        await asyncio.sleep(delay)
                    msg = pack_preview(seq, clock.at(target), fw, fh, jpeg)
                    await ws.send_bytes(msg)
                    stats["previews"] += 1
                    stats["bytes"] += len(msg)
                    next_preview += preview_every_s
            if pending:
                await asyncio.sleep(max(0.0, next_send - time.monotonic()))
                msg = pack_detections(w, h, pending)
                await ws.send_bytes(msg)
                stats["batches"] += 1
                stats["bytes"] += len(msg)
            await asyncio.sleep(linger_s)
            rx.cancel()
    return stats


async def _node_edge_phone(url: str, name: str, frames, dets, *, fps: float, offset_s: float, workdir: Path,
                           on_start, preview_every_s: float = 1.0) -> dict:
    """Run mobile/test/replay_to_server.js (the app's JS core) as one phone."""
    import base64
    import shutil

    node = shutil.which("node")
    if node is None:
        raise RuntimeError("node not found")
    previews, nxt = [], 0.0
    for t, jpeg, _w, _h in frames:
        if t >= nxt:
            previews.append([t, base64.b64encode(jpeg).decode()])
            nxt += preview_every_s
    w, h = frames[0][2], frames[0][3]
    f = Path(workdir) / f"{name}_dets.json"
    f.write_text(json.dumps({"width": w, "height": h, "fps": fps, "previews": previews,
                             "frames": [[t, [list(c) for c in cl]] for t, cl in dets]}))
    script = Path(__file__).resolve().parents[2] / "mobile" / "test" / "replay_to_server.js"
    proc = await asyncio.create_subprocess_exec(node, "--experimental-websocket", str(script), "--url", url,
                                                "--name", name, "--dets", str(f), "--offset", str(offset_s),
                                                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    result: dict = {}
    assert proc.stdout is not None
    async for raw in proc.stdout:
        line = raw.decode().strip()
        if line.startswith("START "):
            wall0 = float(line.split()[1])
            on_start(time.monotonic() - (time.time() - wall0))  # wall clock -> monotonic
        elif line.startswith("DONE "):
            result = json.loads(line[5:])
    err = (await proc.stderr.read()).decode() if proc.stderr else ""
    await proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"node phone failed ({proc.returncode}): {err[-2000:]}")
    return result


def synthetic_phone_frames(preset: str, *, seed: int, shots: int, width: int, height: int, fps: float,
                           quality: int = 85, court_scale: float = 1.0):
    """Render a synthetic scene for one camera preset. Returns (scene, encoded frames)."""
    from ..synthetic import SynthConfig, build_scene, frames

    cfg = SynthConfig(fps=fps, width=width, height=height, camera_preset=preset, n_shots=shots, seed=seed,
                      court_scale=court_scale)
    scene = build_scene(cfg)
    return scene, encode_frames(frames(scene), quality)


def run_live_demo(presets: list[str], *, seed: int = 11, shots: int = 8, width: int = 1280, height: int = 720,
                  fps: float = 60.0, data_dir: Path | str = "data/live_demo", port: int = 8090,
                  clock_offsets: list[float] | None = None, drift_ppm: list[float] | None = None,
                  keep_running: bool = False, verbose: bool = True, edge: bool = False,
                  edge_client: str = "python", record: bool = False) -> dict:
    """In-process server + one fake phone per preset filming the same synthetic rally.

    Calibrates each camera from simulated clicks, streams in real time, and
    scores the fused line calls against the synthetic ground truth. With
    ``edge=True`` the phones behave like the native app: they run the detector
    themselves and send detections (protocol 2) instead of JPEG frames.
    ``edge_client="node"`` runs the app's own JavaScript (CameraSession +
    EdgeClient, mobile/src/core) with a mock camera replaying the detections.
    """
    from aiohttp import web

    from ..evaluate import _truth_call
    from ..geometry.camera import calibrate_from_points
    from ..synthetic import calibration_clicks
    from .server import LiveServer

    data_dir = Path(data_dir)
    (data_dir / "calibration").mkdir(parents=True, exist_ok=True)
    rendered = []
    import pickle

    cache = data_dir / "render_cache"
    cache.mkdir(exist_ok=True)
    for p in presets:
        a = time.monotonic()
        key = cache / f"{p}_s{seed}_n{shots}_{width}x{height}_{fps:g}.pkl"
        if key.exists():
            scene, enc = pickle.loads(key.read_bytes())
        else:
            scene, enc = synthetic_phone_frames(p, seed=seed, shots=shots, width=width, height=height, fps=fps)
            key.write_bytes(pickle.dumps((scene, enc)))
        clicks = calibration_clicks(scene)
        kp = scene.court.keypoints()
        names = [k for k in clicks["points"] if k in kp]
        cam = calibrate_from_points(np.array([kp[k] for k in names]), np.array([clicks["points"][k] for k in names]),
                                    (width, height), camera_id=f"sim-{p}")
        cam.save(data_dir / "calibration" / f"sim-{p}.json")
        dets = None
        if edge:
            dkey = cache / f"{key.stem}_edgedets_v1.pkl"
            if dkey.exists():
                dets = pickle.loads(dkey.read_bytes())
            else:
                b = time.monotonic()
                dets = edge_detections(enc, fps)
                dkey.write_bytes(pickle.dumps(dets))
                if verbose:
                    print(f"  phone detector on {p}: {1e3 * (time.monotonic() - b) / len(enc):.1f} ms/frame (Python reference)")
        rendered.append((p, scene, enc, dets))
        if verbose:
            print(f"rendered {p}: {len(enc)} frames in {time.monotonic() - a:.1f}s; calibration RMS {cam.reprojection_rms_px:.2f}px")
    court = rendered[0][1].court
    cpu0 = _cpu_times()
    srv = LiveServer(court, data_dir, record=record)
    starts: dict[str, float] = {}
    offsets = clock_offsets or [0.0] * len(presets)
    drifts = drift_ppm or [0.0] * len(presets)

    async def main() -> dict:
        app = srv.make_app()
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "127.0.0.1", port).start()
        srv.app_urls = [f"ws://127.0.0.1:{port}/ws/edge"]
        if verbose:
            print(f"dashboard: http://localhost:{port}/dashboard")
        url = f"ws://127.0.0.1:{port}/ws/{'edge' if edge else 'camera'}"
        tasks = []
        for (p, scene, enc, dets), off, dr in zip(rendered, offsets, drifts):
            if edge and edge_client == "node":
                tasks.append(_node_edge_phone(url, f"sim-{p}", enc, dets, fps=fps, offset_s=off, workdir=data_dir,
                                              on_start=lambda t0, p=p: starts.__setitem__(p, t0)))
            elif edge:
                tasks.append(stream_edge_phone(url, f"sim-{p}", enc, dets, fps=fps, clock=PhoneClock(off, dr),
                                               on_start=lambda t0, p=p: starts.__setitem__(p, t0)))
            else:
                tasks.append(stream_phone(url, f"sim-{p}", enc, fps=fps, clock=PhoneClock(off, dr),
                                          on_start=lambda t0, p=p: starts.__setitem__(p, t0)))
        async def sample_stats():
            while True:
                await asyncio.sleep(1.0)
                for c in srv.cams.values():
                    if c.stats.get("proc_fps"):
                        peak[c.name] = max(peak.get(c.name, 0.0), c.stats.get("latency_ms") or 0.0)
        peak: dict[str, float] = {}
        st = asyncio.create_task(sample_stats())
        res = await asyncio.gather(*tasks)
        st.cancel()
        print("peak processing latency ms:", {k: round(v) for k, v in peak.items()}) if verbose else None
        await asyncio.sleep(srv.judge.hold_s + 1.5)
        if keep_running:
            print("demo finished; server still running (Ctrl+C to stop)")
            while True:
                await asyncio.sleep(3600)
        await runner.cleanup()
        return {"phones": res}

    out = asyncio.run(main())
    decisions = [e for e in srv.recent if e.get("type") == "decision"]
    reports = [e for e in srv.recent if e.get("type") == "report"]
    # Session clock -> clip clock: clip t = 0 was at monotonic starts[p] (same for all phones within ms).
    shift = float(np.mean(list(starts.values()))) - srv.t0
    truth = rendered[0][1].bounces
    rows, used = [], set()
    for tb in truth:
        best, bd = None, 0.08
        for i, d in enumerate(decisions):
            dt = abs((d["t"] - shift) - tb.t)
            if i not in used and dt < bd:
                best, bd = i, dt
        tcall, sd = _truth_call(court, tb.x, tb.y)
        row = {"t": tb.t, "x": tb.x, "y": tb.y, "truth": tcall, "truth_dist_cm": 100 * sd, "matched": best is not None,
               "first": tb.bounce_index_in_shot == 0}
        if best is not None:
            used.add(best)
            d = decisions[best]
            row.update(pred=d.get("result"), suppressed=d.get("suppressed"), err_cm=100 * float(np.hypot(d["x"] - tb.x, d["y"] - tb.y)),
                       dt_ms=1e3 * ((d["t"] - shift) - tb.t), cams=len(d["cameras"]), latency_s=d["latency_s"], p_out=d.get("p_out"))
        rows.append(row)
    first = [r for r in rows if r["first"] and r.get("matched") and not r.get("suppressed")]
    summary = {
        "true_bounces": len(truth), "true_first_bounces": sum(r["first"] for r in rows),
        "first_bounces_called": len(first), "decisions": len(decisions), "reports": len(reports), "matched": sum(r["matched"] for r in rows),
        "false_decisions": len(decisions) - len(used),
        "median_err_cm": float(np.median([r["err_cm"] for r in first])) if first else None,
        "p90_err_cm": float(np.percentile([r["err_cm"] for r in first], 90)) if first else None,
        "median_abs_dt_ms": float(np.median([abs(r["dt_ms"]) for r in first])) if first else None,
        "median_latency_s": float(np.median([r["latency_s"] for r in first])) if first else None,
        "multi_camera": sum(1 for r in first if r["cams"] > 1),
        "wrong_out": sum(1 for r in first if r.get("pred") == "OUT" and r["truth"] == "IN"),
        "missed_out": sum(1 for r in rows if r["first"] and r["truth"] == "OUT" and not (r.get("matched") and r.get("pred") == "OUT")),
        "phones": out["phones"],
        "mode": "edge" if edge else "browser",
        "server_cpu_cores": _cpu_cores_since(cpu0),
        "cameras": {c.name: {"frames_in": c.frames_in, "server_drops": c.drops, "unsynced": c.unsynced,
                             "proc_fps": c.stats.get("proc_fps"), "busy": c.stats.get("busy"),
                             "latency_ms": c.stats.get("latency_ms"), "clock": c.clock.summary()} for c in srv.cams.values()},
    }
    if verbose:
        print(json.dumps(summary, indent=2))
    return {"summary": summary, "rows": rows, "decisions": decisions, "session_dir": str(srv.session_dir),
            "clip_to_session_s": shift}


def _cpu_times() -> tuple[float, float]:
    """(CPU seconds of this process and its children, wall time)."""
    import resource

    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime, time.monotonic()


def _cpu_cores_since(t0: tuple[float, float]) -> float:
    """Average cores used by the server process and its (finished) workers since ``t0``."""
    c1, w1 = _cpu_times()
    return round((c1 - t0[0]) / max(w1 - t0[1], 1e-6), 2)
