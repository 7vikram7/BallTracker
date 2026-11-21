"""End to end in a real browser: phone page with on-phone (WebAssembly) detection -> live server.

Headless Chrome gets a fake camera that plays a synthetic rally (y4m file). The phone page
runs the C++ detector compiled to WebAssembly in a Web Worker and sends detections +
previews; the server tracks, fuses and calls. Skipped if Chrome isn't installed.
"""

import asyncio
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pytest

CHROME = os.environ.get("BT_CHROME") or next(
    (c for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", shutil.which("google-chrome") or "",
                 shutil.which("chromium") or "") if c and Path(c).exists()), "/nonexistent/chrome")
pytestmark = [pytest.mark.slow, pytest.mark.skipif(not Path(CHROME).exists(), reason="Google Chrome not installed")]


def _write_y4m(path: Path, frames, fps: int) -> None:
    h, w = frames[0].shape[:2]
    with open(path, "wb") as f:
        f.write(f"YUV4MPEG2 W{w} H{h} F{fps}:1 Ip A1:1 C420jpeg\n".encode())
        for img in frames:
            f.write(b"FRAME\n")
            f.write(cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420).tobytes())


async def _cdp_run_phone_page(url: str, name: str, user_dir: Path, y4m: Path, seconds: float, port: int) -> dict:
    import aiohttp

    linux = [] if sys.platform == "darwin" else ["--no-sandbox"]  # CI containers have no user namespaces
    proc = subprocess.Popen([CHROME, "--headless=new", *linux, f"--remote-debugging-port={port}",
                             f"--user-data-dir={user_dir}", "--use-fake-ui-for-media-stream",
                             "--use-fake-device-for-media-stream", f"--use-file-for-fake-video-capture={y4m}",
                             "--autoplay-policy=no-user-gesture-required", "--disable-background-timer-throttling",
                             "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows",
                             "--window-size=1280,800", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    errors: list[str] = []
    try:
        async with aiohttp.ClientSession() as s:
            for _ in range(100):
                try:
                    tabs = await (await s.get(f"http://127.0.0.1:{port}/json")).json()
                    break
                except Exception:
                    await asyncio.sleep(0.1)
            page = [t for t in tabs if t["type"] == "page"][0]
            async with s.ws_connect(page["webSocketDebuggerUrl"], max_msg_size=0) as ws:
                n = 0

                async def call(method, params=None):
                    nonlocal n
                    n += 1
                    my = n
                    await ws.send_json({"id": my, "method": method, "params": params or {}})
                    while True:
                        m = json.loads((await ws.receive()).data)
                        if m.get("method") == "Runtime.exceptionThrown":
                            errors.append(str(m["params"]["exceptionDetails"]))
                        if m.get("id") == my:
                            return m.get("result")

                await call("Runtime.enable")
                await call("Page.enable")
                await call("Page.bringToFront")
                await call("Emulation.setFocusEmulationEnabled", {"enabled": True})
                await call("Page.navigate", {"url": url})
                await asyncio.sleep(1.5)
                js = (f"document.getElementById('name').value = {json.dumps(name)};"
                      "document.getElementById('mode').value = 'edge';"
                      "document.getElementById('fps').value = '30';"
                      "document.getElementById('start').click(); 'ok'")
                await call("Runtime.evaluate", {"expression": js})
                t_end = time.monotonic() + seconds
                trace = []
                while time.monotonic() < t_end:
                    r = await call("Runtime.evaluate", {"expression": "JSON.stringify([document.getElementById('fcap').textContent, seq, workerBusy, dropped, document.visibilityState])", "returnByValue": True})
                    trace.append(r["result"].get("value"))
                    await asyncio.sleep(0.5)
                r = await call("Runtime.evaluate", {"expression": "JSON.stringify({err: document.getElementById('err').textContent,"
                                                                  " det: document.getElementById('fdet').textContent,"
                                                                  " cap: document.getElementById('fcap').textContent,"
                                                                  " mode: mode, ready: workerReady})", "returnByValue": True})
                info = json.loads(r["result"]["value"])
                info["exceptions"] = errors
                info["trace"] = trace[::4]
                return info
    finally:
        proc.terminate()


def test_phone_page_on_phone_detection_end_to_end(tmp_path):
    from aiohttp import web

    from balltracker.geometry.camera import calibrate_from_points
    from balltracker.live.server import LiveServer
    from balltracker.synthetic import SynthConfig, build_scene, calibration_clicks, frames

    # 30 fps: headless Chrome on the 2020 Intel Mac can't run the detector on every 60 fps frame
    # (it then drops frames in bursts and bounces next to a gap are lost). Phones are much faster.
    fps, name = 30, "browser-edge-cam"
    W, H = 960, 540  # offline, the same pipeline gets 5/5 bounces within 3.6 cm at this size (640x360 misses some)
    scene = build_scene(SynthConfig(fps=fps, width=W, height=H, n_shots=5, seed=11, camera_preset="behind_baseline_high"))
    imgs = [img for _, _, img in frames(scene)]
    y4m = tmp_path / "rally.y4m"
    _write_y4m(y4m, imgs, fps)
    clip_s = len(imgs) / fps
    clicks = calibration_clicks(scene)
    kp = scene.court.keypoints()
    names = [k for k in clicks["points"] if k in kp]
    cam = calibrate_from_points(np.array([kp[k] for k in names]), np.array([clicks["points"][k] for k in names]),
                                (W, H), camera_id=name)
    (tmp_path / "calibration").mkdir()
    cam.save(tmp_path / "calibration" / f"{name}.json")

    srv = LiveServer(scene.court, tmp_path, record=True)
    port = 8291

    async def main():
        runner = web.AppRunner(srv.make_app())
        await runner.setup()
        await web.TCPSite(runner, "127.0.0.1", port).start()
        try:
            return await _cdp_run_phone_page(f"http://127.0.0.1:{port}/phone", name, tmp_path / "chrome", y4m,
                                             2 * clip_s + 3.0, port + 1)  # the fake camera loops: one full
                                             # pass after the clock has synced (frames before sync are dropped)
        finally:
            await asyncio.sleep(1.0)
            await runner.cleanup()

    info = asyncio.run(main())
    print("page:", json.dumps(info))
    assert info["mode"] == "edge" and info["ready"], info
    assert not info["exceptions"], info["exceptions"]
    c = srv.cams[name]
    # The page drops frames it can't keep up with, by design. The clip plays twice at 30 fps; require
    # 70% of its frames processed (21 fps), which the 2020 Intel Mac's headless Chrome manages.
    assert c.mode == "edge" and c.frames_in > 0.7 * fps * 2 * clip_s, (c.frames_in, info)
    assert c.latest_jpeg is not None and c.latest_size == (W, H)  # previews arrived at detection resolution
    decisions = [d for d in srv.all_decisions if not d.get("suppressed")]
    truth = [b for b in scene.bounces if b.bounce_index_in_shot == 0]
    # The fake camera loops the clip; match each true first bounce to the nearest decision in position.
    errs = []
    for tb in truth:
        d = min(decisions, key=lambda d: np.hypot(d["x"] - tb.x, d["y"] - tb.y), default=None)
        if d is not None:
            errs.append(100 * np.hypot(d["x"] - tb.x, d["y"] - tb.y))
    found = sum(e < 10 for e in errs)
    print(f"bounces: {len(decisions)} decisions; per true first bounce, nearest error (cm): {np.round(errs, 1)}; "
          f"frames processed {c.frames_in}")
    # With the server snapping browser timestamps to the frame grid (FrameClock), every bounce is found;
    # without it, ±3 ms timestamp jitter lost 1-2 of 5 at random.
    assert found == len(truth), f"errors (cm): {np.round(errs, 1)}; page: {info}"
    assert np.median([e for e in errs if e < 10]) < 4.0
    assert not any(d.get("announce") and d.get("result") == "OUT" and
                   min(abs(100 * np.hypot(d["x"] - tb.x, d["y"] - tb.y)) for tb in truth) > 10 for d in decisions)
    assert (tmp_path / "sessions").exists() and any((tmp_path / "sessions").rglob("dets.jsonl"))
