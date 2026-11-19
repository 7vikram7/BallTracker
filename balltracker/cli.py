"""Command-line interface:  ``bt <command> ...``  (or ``python -m balltracker``).

Commands
--------
court      Draw a court diagram (check a scaled/custom court config).
synth      Generate a synthetic test video + ground truth + calibration clicks.
calibrate  Click court keypoints on a frame (or use a points file) -> camera.json.
analyze    Run the pipeline on a video -> results.json (+ optional annotated video).
evaluate   Compare results.json with ground truth (synthetic JSON or chalk CSV).
sweep      Synthetic experiment: accuracy vs frame rate / camera / resolution.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from .geometry.camera import Camera, calibrate_from_points
from .geometry.court import CourtSpec, ServiceSide, Side


def _court(path: str | None) -> CourtSpec:
    return CourtSpec.load(path) if path else CourtSpec.pickleball()


def _parse_serve(s: str | None):
    if not s:
        return None
    from .sports.pickleball.line_calling import ServeContext

    side, half = s.split(":")
    return ServeContext(Side(side.upper()), ServiceSide(half.lower()))


# ----------------------------------------------------------------- court
def cmd_court(a: argparse.Namespace) -> None:
    import cv2

    from .synthetic import render_court_texture

    court = _court(a.court)
    tex, _ = render_court_texture(court, mm_per_px=10.0, margin_m=1.0)
    cv2.imwrite(a.out, tex)
    print(json.dumps(court.to_dict(), indent=2))
    print(f"wrote {a.out}")


# ----------------------------------------------------------------- synth
def cmd_synth(a: argparse.Namespace) -> None:
    from .synthetic import SynthConfig, build_scene, write_scene

    w, h = (int(x) for x in a.res.split("x"))
    cfg = SynthConfig(fps=a.fps, width=w, height=h, camera_preset=a.camera, n_shots=a.shots, seed=a.seed,
                      court_scale=a.scale, shutter_s=1 / a.shutter, noise_sigma=a.noise)
    scene = build_scene(cfg)
    paths = write_scene(scene, a.out)
    print(f"{len(scene.bounces)} true bounces; files:")
    for k, p in paths.items():
        print(f"  {k}: {p}")


# ----------------------------------------------------------------- calibrate
def _first_frame(video: str, at_s: float) -> np.ndarray:
    from .video import VideoFileSource

    for f in VideoFileSource(video).frames(start_s=at_s):
        return f.image
    raise SystemExit("could not read a frame")


def click_points(image: np.ndarray, names: list[str]) -> dict[str, list[float]]:
    """Interactive: click each named keypoint; s = skip, u = undo, q/Enter = done."""
    import cv2

    pts: dict[str, list[float]] = {}
    order: list[str] = []
    i = 0
    win = "calibrate - click keypoint (s=skip, u=undo, q=done)"
    state = {"click": None}

    def on_mouse(ev, x, y, *_):
        if ev == cv2.EVENT_LBUTTONDOWN:
            state["click"] = (x, y)

    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win, on_mouse)
    while i < len(names):
        vis = image.copy()
        for n, (u, v) in pts.items():
            cv2.circle(vis, (int(u), int(v)), 5, (0, 0, 255), 2)
            cv2.putText(vis, n, (int(u) + 6, int(v) - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.putText(vis, f"Click: {names[i]}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        cv2.imshow(win, vis)
        k = cv2.waitKey(30) & 0xFF
        if state["click"] is not None:
            pts[names[i]] = [float(state["click"][0]), float(state["click"][1])]
            order.append(names[i])
            state["click"] = None
            i += 1
        elif k == ord("s"):
            i += 1
        elif k == ord("u") and order:
            last = order.pop()
            pts.pop(last, None)
            i = names.index(last)
        elif k in (ord("q"), 13):
            break
    cv2.destroyWindow(win)
    return pts


def cmd_calibrate(a: argparse.Namespace) -> None:
    court = _court(a.court)
    kp = court.keypoints()
    if a.points:
        data = json.loads(Path(a.points).read_text())
        pts, size = data["points"], tuple(data["image_size"])
    else:
        img = _first_frame(a.video, a.at)
        size = (img.shape[1], img.shape[0])
        pts = click_points(img, list(kp))
        out_pts = Path(a.out).with_name(Path(a.out).stem + "_points.json")
        out_pts.write_text(json.dumps({"schema": "balltracker.calibration_points/v1", "image_size": list(size), "points": pts}, indent=2))
        print(f"saved clicked points to {out_pts}")
    names = [n for n in pts if n in kp]
    cam = calibrate_from_points([kp[n] for n in names], [pts[n] for n in names], size,
                                hfov_guess_deg=a.hfov, estimate_focal=not a.fixed_fov, camera_id=a.camera_id)
    cam.save(a.out)
    hfov = float(np.degrees(2 * np.arctan(size[0] / 2 / cam.focal_px)))
    print(f"{len(names)} points, reprojection RMS {cam.reprojection_rms_px:.2f} px, "
          f"hfov {hfov:.1f} deg, camera at {np.round(cam.position, 2).tolist()} m -> {a.out}")
    if cam.reprojection_rms_px and cam.reprojection_rms_px > 3:
        print("WARNING: RMS > 3 px - check point labels / lens distortion (try the main 1x lens).")


# ----------------------------------------------------------------- analyze
def annotate(video: str, out: str, result, camera: Camera, court: CourtSpec, tracks) -> None:
    import cv2

    from .video import VideoFileSource, write_video

    src = VideoFileSource(video)
    obs_by_frame: dict[int, list] = {}
    for tr in tracks:
        for p in tr.points:
            obs_by_frame.setdefault(p.frame_index, []).append(p)
    calls = {c.bounce_id: c for c in result.calls}
    marks = []
    for b in result.bounces:
        c = calls.get(b.id)
        marks.append((b, c))
    lines3d = []
    for seg in court.lines():
        r = seg.rect
        lines3d.append(np.array([[r.x0, r.y0, 0], [r.x1, r.y0, 0], [r.x1, r.y1, 0], [r.x0, r.y1, 0]]))

    def gen():
        for f in src.frames():
            img = f.image
            for poly in lines3d:
                if np.all(camera.depth(poly) > 0):
                    cv2.polylines(img, [camera.project(poly).astype(np.int32)], True, (255, 0, 255), 1, cv2.LINE_AA)
            for p in obs_by_frame.get(f.index, []):
                cv2.circle(img, (int(p.u), int(p.v)), max(3, int(p.radius_px) + 3), (0, 255, 0), 1, cv2.LINE_AA)
            for b, c in marks:
                if 0 <= f.t - b.t < 1.5:
                    col = (0, 0, 255) if c and c.result.value == "OUT" else (0, 200, 255) if c and c.result.value == "UNCERTAIN" else (0, 255, 0)
                    u, v = b.pixel
                    cv2.drawMarker(img, (int(u), int(v)), col, cv2.MARKER_CROSS, 24, 2)
                    label = f"{c.result.value} p_out={c.p_out:.2f} d={c.signed_distance_m*100:+.1f}cm" if c else "bounce"
                    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
                    lx = int(min(max(4, u + 12), img.shape[1] - tw - 4))
                    ly = int(min(max(th + 4, v - 12), img.shape[0] - 4))
                    cv2.putText(img, label, (lx, ly), cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)
            cv2.putText(img, f"t={f.t:.3f}s", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            yield img

    # High-fps clips are written at <= 60 fps playback, i.e. shown in slow motion.
    write_video(out, gen(), min(src.info.fps, 60.0), (src.info.width, src.info.height))


def cmd_analyze(a: argparse.Namespace) -> None:
    from .pipeline import PipelineConfig, analyze_frames
    from .video import VideoFileSource

    court = _court(a.court)
    cam = Camera.load(a.calib)
    src = VideoFileSource(a.video, fps_override=a.fps)
    if not a.fps and src.info.fps <= 61:
        print(f"note: file reports {src.info.fps:.2f} fps. If this is an off-speed / slo-mo clip "
              f"(e.g. Blackmagic OFF/SPEED at 240), rerun with --fps 240 or the timings will be wrong.")
    cfg = PipelineConfig(serve=_parse_serve(a.serve))
    cfg.detector.use_color = not a.no_color
    if a.max_radius:
        cfg.detector.max_radius_px = a.max_radius
    if a.ball_hsv:
        h = [int(x) for x in a.ball_hsv.split(",")]
        if len(h) != 6:
            raise SystemExit("--ball-hsv needs 6 comma-separated numbers")
        cfg.detector.hsv_low, cfg.detector.hsv_high = tuple(h[:3]), tuple(h[3:])
    frames = ((f.index, f.t, f.image) for f in src.frames(start_s=a.start, end_s=a.end))
    out = analyze_frames(frames, cam, court, cfg, source=a.video, fps=src.info.fps)
    Path(a.out).write_text(out.result.model_dump_json(indent=2))
    r = out.result
    print(f"{r.frame_count} frames at {r.timings['frames_per_s']:.0f} fps processing; "
          f"{len(out.tracks)} tracks, {len(r.bounces)} bounces")
    for c in r.calls:
        b = next(b for b in r.bounces if b.id == c.bounce_id)
        s = np.sqrt(np.linalg.eigvalsh(np.array(b.cov_xy)).max()) * 100
        flag = f"  <-- {c.call_text}" if c.announce else ""
        print(f"  t={c.t:7.3f}s  ({b.position.x:+.3f}, {b.position.y:+.3f}) m ±{s:.1f}cm  {c.result.value:9s} "
              f"p_out={c.p_out:.2f}  {c.nearest_line} {c.signed_distance_m*100:+.1f}cm{flag}")
    print(f"wrote {a.out}")
    if a.annotate:
        annotate(a.video, a.annotate, r, cam, court, out.tracks)
        print(f"wrote {a.annotate}")


# ----------------------------------------------------------------- evaluate
def cmd_evaluate(a: argparse.Namespace) -> None:
    from .evaluate import load_truth, match, summarise, visible_truth
    from .events import AnalysisResult

    res = AnalysisResult.model_validate_json(Path(a.results).read_text())
    court = CourtSpec(**{k: v for k, v in res.court.items()})
    truth = load_truth(a.truth, court)
    if a.truth.endswith(".json") and not a.all_truth:
        truth = visible_truth(truth, json.loads(Path(a.truth).read_text()), court)
    ms = match(res, truth)
    summ = summarise(ms)
    print(json.dumps(summ, indent=2))
    if a.details:
        for m in ms:
            print(m)


# ----------------------------------------------------------------- sweep
def cmd_sweep(a: argparse.Namespace) -> None:
    from .experiments import run_sweep

    run_sweep(fps_list=[float(x) for x in a.fps.split(",")], cameras=a.cameras.split(","),
              res=a.res, shots=a.shots, seeds=[int(s) for s in a.seeds.split(",")], scale=a.scale,
              out=a.out, hfov_prior=a.hfov_prior, shutter=a.shutter, noise=a.noise)


# ----------------------------------------------------------------- live
def _hsv_overrides(spec: str | None) -> dict:
    if not spec:
        return {}
    h = [int(x) for x in spec.split(",")]
    if len(h) != 6:
        raise SystemExit("--ball-hsv needs 6 comma-separated numbers")
    return {"hsv_low": h[:3], "hsv_high": h[3:]}


def cmd_serve(a: argparse.Namespace) -> None:
    from .live.server import run

    run(_court(a.court), Path(a.data), host=a.host, https_port=a.https_port, http_port=a.http_port,
        tls=not a.no_tls, record=a.record, detector_overrides=_hsv_overrides(a.ball_hsv))


def cmd_fakephone(a: argparse.Namespace) -> None:
    import asyncio

    from .live.fakephone import PhoneClock, encode_frames, stream_phone, synthetic_phone_frames
    from .video import VideoFileSource

    w, h = (int(x) for x in a.res.split("x"))
    if a.synth:
        scene, frames = synthetic_phone_frames(a.synth, seed=a.seed, shots=a.shots, width=w, height=h, fps=a.fps)
        print(f"rendered {len(frames)} frames of synthetic camera '{a.synth}'")
    elif a.video:
        src = VideoFileSource(a.video, fps_override=a.fps_override)
        frames = encode_frames((f.index, f.t, f.image) for f in src.frames(start_s=a.start, end_s=a.end))
        print(f"encoded {len(frames)} frames from {a.video}")
    else:
        raise SystemExit("give --video or --synth")
    url = a.server.rstrip("/") + "/ws/camera"
    while True:
        stats = asyncio.run(stream_phone(url, a.name, frames, fps=a.fps, clock=PhoneClock(a.clock_offset, a.drift_ppm)))
        print(stats)
        if not a.loop:
            break


def cmd_replay(a: argparse.Namespace) -> None:
    from .live.replay import format_comparison, replay, save_replay

    res = replay(a.session, detector_overrides=_hsv_overrides(a.ball_hsv) or None)
    print(format_comparison(res))
    if not a.no_save:
        print(f"saved {save_replay(res)}")
    if a.strict and not res["comparison"]["identical"]:
        raise SystemExit(1)


def cmd_report(a: argparse.Namespace) -> None:
    from .live.report import write_report

    p = write_report(a.session, a.marks)
    print(p.read_text() if a.print else f"wrote {p}")


def cmd_sessions(a: argparse.Namespace) -> None:
    from .live.report import list_sessions

    rows = list_sessions(a.data)
    if not rows:
        print(f"no sessions in {a.data}/sessions")
    print(f"{'session':17} {'length':>7} {'cams':>4} {'decisions':>9} {'spoken':>6} {'recorded':>8}  commit")
    for r in rows:
        dur = f"{r['duration_s']:.0f}s" if r["duration_s"] is not None else "?"
        print(f"{r['session']:17} {dur:>7} {r['cameras']:>4} {r['decisions']:>9} {str(r['spoken'] if r['spoken'] is not None else '?'):>6} "
              f"{'yes' if r['recorded'] else 'no':>8}  {r['commit']}")


def cmd_live_demo(a: argparse.Namespace) -> None:
    from .live.fakephone import run_live_demo

    w, h = (int(x) for x in a.res.split("x"))
    presets = a.cameras.split(",")
    run_live_demo(presets, seed=a.seed, shots=a.shots, width=w, height=h, fps=a.fps, port=a.port,
                  clock_offsets=[37.0 * i for i in range(len(presets))], drift_ppm=[40.0 * (-1) ** i for i in range(len(presets))],
                  keep_running=a.keep, edge=a.edge, record=a.record)


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="bt", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("court", help="draw a court diagram")
    s.add_argument("--court", help="court YAML (default: regulation pickleball)")
    s.add_argument("--out", default="court.png")
    s.set_defaults(fn=cmd_court)

    s = sub.add_parser("synth", help="generate synthetic test video")
    s.add_argument("--out", required=True)
    s.add_argument("--fps", type=float, default=240)
    s.add_argument("--res", default="1920x1080")
    s.add_argument("--camera", default="behind_baseline_high")
    s.add_argument("--shots", type=int, default=20)
    s.add_argument("--scale", type=float, default=1.0, help="court scale, e.g. 0.5 for a half-size floor court")
    s.add_argument("--shutter", type=float, default=1000, help="shutter speed denominator (1/N s)")
    s.add_argument("--noise", type=float, default=2.5)
    s.add_argument("--seed", type=int, default=7)
    s.set_defaults(fn=cmd_synth)

    s = sub.add_parser("calibrate", help="calibrate a camera from court keypoints")
    s.add_argument("video", nargs="?")
    s.add_argument("--court")
    s.add_argument("--points", help="points JSON instead of clicking")
    s.add_argument("--at", type=float, default=0.0, help="time (s) of the frame to click on")
    s.add_argument("--hfov", type=float, default=65.0, help="horizontal FOV guess (deg)")
    s.add_argument("--fixed-fov", action="store_true", help="don't estimate focal length")
    s.add_argument("--camera-id", default="cam0")
    s.add_argument("--out", default="camera.json")
    s.set_defaults(fn=cmd_calibrate)

    s = sub.add_parser("analyze", help="analyse a video")
    s.add_argument("video")
    s.add_argument("--calib", required=True)
    s.add_argument("--court")
    s.add_argument("--out", default="results.json")
    s.add_argument("--annotate", help="write annotated MP4 here")
    s.add_argument("--serve", help="judge every bounce as a serve, e.g. A:right")
    s.add_argument("--start", type=float, default=0.0)
    s.add_argument("--end", type=float)
    s.add_argument("--fps", type=float, help="override capture fps (if timestamps are wrong)")
    s.add_argument("--no-color", action="store_true", help="disable the yellow/green colour gate")
    s.add_argument("--max-radius", type=float)
    s.add_argument("--ball-hsv", help="ball colour gate as Hlo,Slo,Vlo,Hhi,Shi,Vhi (OpenCV units, H 0-180), "
                   "default 25,100,90,55,255,255")
    s.set_defaults(fn=cmd_analyze)

    s = sub.add_parser("evaluate", help="compare results with ground truth")
    s.add_argument("results")
    s.add_argument("--truth", required=True, help="ground_truth.json (synthetic) or chalk CSV")
    s.add_argument("--all-truth", action="store_true", help="don't drop out-of-view synthetic bounces")
    s.add_argument("--details", action="store_true")
    s.set_defaults(fn=cmd_evaluate)

    s = sub.add_parser("sweep", help="synthetic accuracy experiment")
    s.add_argument("--fps", default="30,60,120,240")
    s.add_argument("--cameras", default="behind_baseline_high")
    s.add_argument("--res", default="1280x720")
    s.add_argument("--shots", type=int, default=25)
    s.add_argument("--seeds", default="1")
    s.add_argument("--scale", type=float, default=1.0)
    s.add_argument("--hfov-prior", type=float, default=60.0, help="deliberately-wrong FOV guess for calibration")
    s.add_argument("--shutter", choices=["fast", "auto"], default="fast",
                   help="fast = 1/1000 s; auto = half frame interval (phone auto-exposure)")
    s.add_argument("--noise", type=float, default=2.5, help="image noise sigma (grey levels)")
    s.add_argument("--out", default="sweep.json")
    s.set_defaults(fn=cmd_sweep)

    s = sub.add_parser("serve", help="run the live server (phones stream to it, calls on the dashboard)")
    s.add_argument("--court", help="court YAML (default: regulation pickleball)")
    s.add_argument("--data", default="data/live", help="calibrations, certificates and sessions go here")
    s.add_argument("--host", default=None, help="address to listen on (default: all IPv4 and IPv6)")
    s.add_argument("--https-port", type=int, default=8443)
    s.add_argument("--http-port", type=int, default=8080)
    s.add_argument("--no-tls", action="store_true", help="plain HTTP only (phone cameras will NOT work)")
    s.add_argument("--record", action="store_true", help="save every received frame for later replay")
    s.add_argument("--ball-hsv", help="ball colour gate Hlo,Slo,Vlo,Hhi,Shi,Vhi")
    s.set_defaults(fn=cmd_serve)

    s = sub.add_parser("fakephone", help="stream a video or synthetic scene to the live server like a phone")
    s.add_argument("--server", default="ws://localhost:8080", help="ws://host:port or wss://host:port")
    s.add_argument("--name", default="fake-cam")
    s.add_argument("--video")
    s.add_argument("--synth", help="synthetic camera preset, e.g. behind_baseline_high")
    s.add_argument("--fps", type=float, default=60)
    s.add_argument("--fps-override", type=float, help="for --video: true capture fps if timestamps are wrong")
    s.add_argument("--res", default="1280x720")
    s.add_argument("--shots", type=int, default=10)
    s.add_argument("--seed", type=int, default=11)
    s.add_argument("--start", type=float, default=0.0)
    s.add_argument("--end", type=float)
    s.add_argument("--clock-offset", type=float, default=0.0, help="simulated phone clock offset (s)")
    s.add_argument("--drift-ppm", type=float, default=0.0)
    s.add_argument("--loop", action="store_true")
    s.set_defaults(fn=cmd_fakephone)

    s = sub.add_parser("live-demo", help="server + simulated phones on one synthetic rally, scored vs truth")
    s.add_argument("--cameras", default="behind_baseline_high,side_mid")
    s.add_argument("--shots", type=int, default=10)
    s.add_argument("--seed", type=int, default=11)
    s.add_argument("--res", default="1280x720")
    s.add_argument("--fps", type=float, default=60)
    s.add_argument("--port", type=int, default=8090)
    s.add_argument("--keep", action="store_true", help="keep the server running afterwards (look at the dashboard)")
    s.add_argument("--edge", action="store_true", help="simulate the native app: phones send detections, not video")
    s.add_argument("--record", action="store_true", help="record the demo session (for bt replay / bt report)")
    s.set_defaults(fn=cmd_live_demo)

    s = sub.add_parser("replay", help="re-run a recorded live session with the current code and compare the calls")
    s.add_argument("session", help="session folder, e.g. data/live/sessions/20261118-101500")
    s.add_argument("--ball-hsv", help="try a different ball colour gate Hlo,Slo,Vlo,Hhi,Shi,Vhi")
    s.add_argument("--no-save", action="store_true", help="don't save the result under <session>/replays/")
    s.add_argument("--strict", action="store_true", help="exit 1 if anything differs from the live session")
    s.set_defaults(fn=cmd_replay)

    s = sub.add_parser("report", help="summarise a live session (report.md), optionally scored against chalk marks")
    s.add_argument("session")
    s.add_argument("--marks", help="marks sheet CSV (docs/field_test_marks.csv format)")
    s.add_argument("--print", action="store_true", help="print the report instead of only writing it")
    s.set_defaults(fn=cmd_report)

    s = sub.add_parser("sessions", help="list past live sessions")
    s.add_argument("--data", default="data/live")
    s.set_defaults(fn=cmd_sessions)

    a = p.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main(sys.argv[1:])
