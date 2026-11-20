# BallTracker

Computer-vision line calling for pickleball (stats and coaching later), built so
other racket sports can reuse the perception layers. See
[ARCHITECTURE.md](ARCHITECTURE.md) for design and decisions, and
[docs/RECORDING_GUIDE.md](docs/RECORDING_GUIDE.md) for how to film test footage.

**Status.** Offline analysis of recordings (validated on one real 240 fps clip
against chalk marks: median 0.7 cm across the line, see
[docs/PHASE0_RESULTS.md](docs/PHASE0_RESULTS.md)), plus a **live server**: phones
stream to the Mac from a web page, calls are spoken on a dashboard. See
[docs/LIVE_SETUP.md](docs/LIVE_SETUP.md).

## Setup (macOS, Intel or Apple Silicon)

```bash
git clone <repo> && cd BallTracker
/usr/local/bin/python3.12 -m venv .venv      # any Python >= 3.12
.venv/bin/pip install -e ".[dev,live]"
source .venv/bin/activate                    # gives you the `bt` command
pytest -m "not slow"                         # fast tests (~4 min on a 2020 Intel MBP)
pytest                                       # everything: end-to-end, real-sample replay, browser test
```

Optional for some tests: Node ≥ 22 (the app's JavaScript core: `node --test mobile/test/*.test.js`),
Google Chrome (the browser end-to-end test; skipped without it). Real field data for the tests ships
in [data/samples/](data/samples/README.md); full sessions are not in git.

Where to read: [docs/DECISION_LOG.md](docs/DECISION_LOG.md) (every request, analysis, decision and the roadmap, in order),
[docs/DECISIONS.md](docs/DECISIONS.md) (the decisions as a table),
[docs/evolution/LOG.md](docs/evolution/LOG.md) (request/outcome history, written by a Claude Code
hook), [docs/FIELD_TEST_2_RESULTS.md](docs/FIELD_TEST_2_RESULTS.md) (latest field results),
[docs/LOB_STUDY.md](docs/LOB_STUDY.md) (lobs through every stage, on mock data),
[docs/MINI_COURT.md](docs/MINI_COURT.md) (what mini-court tests can and cannot show),
[docs/CAMERA_RIGS.md](docs/CAMERA_RIGS.md) (do weak 30 fps phones help?).

**Working on this from elsewhere (people or agents):** start with [docs/HANDOFF.md](docs/HANDOFF.md):
goals, the real field data in [data/field/](data/field/) (replayable), the decision log
[docs/DECISION_LOG.md](docs/DECISION_LOG.md) (request → analysis → decision → roadmap), open problems and how to
propose changes.

A passing full `pytest` run is committed and pushed automatically at the end of each Claude Code
response (`scripts/hooks/autocommit.py`; off with `BT_AUTOCOMMIT=0`).

## Try it without footage (synthetic)

```bash
bt synth --out data/synth/demo --fps 240 --res 1280x720 --shots 10
bt calibrate --points data/synth/demo/calibration_points.json --out data/synth/demo/cam.json
bt analyze data/synth/demo/video.mp4 --calib data/synth/demo/cam.json \
    --out data/synth/demo/results.json --annotate data/synth/demo/annotated.mp4
bt evaluate data/synth/demo/results.json --truth data/synth/demo/ground_truth.json
```

Other options: `--scale 0.5` (half-size floor court), `--camera corner_high|side_mid|net_post`.

Experiment: accuracy vs frame rate:

```bash
bt sweep --fps 30,60,120,240 --shutter auto --noise 6 --out data/experiments/sweep.json
```

## With real footage

```bash
bt calibrate clip.mov --court configs/court_full.yaml --out cam.json     # click keypoints, s=skip
bt analyze clip.mov --calib cam.json --court configs/court_full.yaml --annotate out.mp4
bt analyze serve.mov --calib cam.json --serve A:right                     # judge bounces as serves
bt evaluate results.json --truth data/ground_truth/session1.csv          # chalk-drill measurements
```

Court configs: `configs/court_full.yaml` (regulation), `configs/court_half_scale.yaml`,
`configs/court_custom_example.yaml` (measure your own taped court).

## Live (phones → Mac → spoken calls)

```bash
bt serve                 # then open http://localhost:8080/dashboard on the Mac
                         # (--record: also keep previews; --full-rate: app phones send every frame)
                         # and https://<mac-ip>:8443/phone on each phone
                         # (the phone page finds the ball on the phone by default: C++ -> WebAssembly)
bt serve --court-scale 0.2   # a 1/5-size practice court (lines scaled, real ball)
bt live-demo             # no phones: server + simulated phones, scored vs truth
bt live-demo --edge      # same, but the phones behave like the native app (send detections only)
```

Calibrating a camera on the dashboard: **Calibrate**, click the 4 corners of the half nearest the
camera roughly, **Snap to lines**, check the blue points, **Calibrate**. When a camera is saved,
the other cameras are re-snapped, and during play bounces seen together with that camera refine
the others; refinements appear on the camera card as proposals to review.

Full guide: [docs/LIVE_SETUP.md](docs/LIVE_SETUP.md).

**Native app (in progress):** [mobile/](mobile/README.md) is a React Native (Expo) app that
runs the ball detector on the phone (C++, up to 240 fps on iPhone) and sends only ball
positions. The server accepts it alongside browser phones (protocol 2). Plan:
[docs/ROADMAP_MOBILE_APP.md](docs/ROADMAP_MOBILE_APP.md).

## Layout

```
balltracker/
  geometry/court.py      court frame, dimensions, regions, keypoints (scalable)
  geometry/camera.py     camera model, calibration, ray casting
  video.py               timestamped frame sources (PyAV/FFmpeg)
  detection.py           ball candidates (classical baseline, swappable)
  edge_detection.py      phone-side detector: reference for the app's C++ (exact parity)
  ballcore.py            ctypes binding to the app's C++ detector (tests, benchmarks)
  tracking.py            2D ball tracks
  bounce.py              sub-frame bounce + uncertainty
  sports/pickleball/line_calling.py   rules → IN / OUT / UNCERTAIN
  events.py              versioned event schemas
  pipeline.py            wiring for one camera
  synthetic.py           synthetic scenes with ground truth
  evaluate.py            accuracy metrics vs ground truth
  experiments.py         parameter sweeps
  live/server.py         live server: phone WebSockets, dashboard, calibration API
  live/worker.py         per-camera streaming pipeline (own process per camera)
  live/fusion.py         multi-camera bounce fusion + corroboration + line call
  live/clocksync.py      phone clock -> server clock (ping/pong, drift)
  live/certs.py          local CA + HTTPS certificate (phone cameras need HTTPS)
  live/fakephone.py      simulated phones (browser and app); `bt live-demo [--edge]`
  live/protocol.py       wire format: frames (browser), detections + previews (app)
  live/static/           phone.html, dashboard.html
  cli.py                 `bt` command
mobile/                  React Native app + native module (Swift, Kotlin, shared C++)
configs/  docs/  tests/  data/
```

## Licences of dependencies

NumPy/SciPy (BSD), OpenCV (Apache-2.0), PyAV (BSD), Pydantic (MIT),
PyYAML (MIT), aiohttp (Apache-2.0), cryptography (Apache-2.0/BSD), segno (BSD).
No AGPL components. The phone and dashboard pages use no external libraries.

Caveat: PyAV's prebuilt wheels bundle an FFmpeg that includes **libx264 (GPL)**.
We only use it to *write* synthetic and annotated videos (`video.write_video`).
Before distributing anything, switch that encoder to `h264_videotoolbox`
(Apple hardware) or an LGPL-only FFmpeg build. Decoding doesn't need x264.
