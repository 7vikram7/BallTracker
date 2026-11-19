# Architecture

Living document. Update it when a component, interface or decision changes.

## Goal and current scope

Live line calling for pickleball (then stats, then coaching), designed so other
net/racket sports can reuse the perception layers. It starts as a learning
project and may become a club installation.

**Phase 0 (now)**: offline analysis of recorded single-camera footage, to measure
how accurately a phone can locate a bounce, before building live
infrastructure.

## Layers and modules

```
 Acquisition            Perception (sport-agnostic)                 Sport intelligence        Apps
 ───────────            ───────────────────────────                 ──────────────────        ────
 video.py        ──▶    detection.py ──▶ tracking.py ──▶ bounce.py ──▶ sports/pickleball/  ──▶ cli.py
 (FrameSource)          (BallDetector)   (BallTracker)   (BounceEvent)   line_calling.py         (later: server,
                                                                          (LineCallEvent)          phone app, UI)
                         geometry/camera.py   geometry/court.py
                         (calibration, rays)  (court model, regions, keypoints)

 events.py: versioned Pydantic schemas shared by all layers
 synthetic.py / experiments.py / evaluate.py: test harness and accuracy measurement
```

| Module | Responsibility | Must NOT know about |
|---|---|---|
| `video.py` | Decode files into `Frame(index, t, image)` with container timestamps | Balls, courts |
| `geometry/court.py` | Court frame, dimensions, lines, regions, keypoints; scaled/custom courts | Cameras, detection |
| `geometry/camera.py` | Pinhole model, calibration from keypoints, ray/plane intersection | Sport rules |
| `detection.py` | Per-frame ball candidates (`BallDetector` protocol) | Rules, tracking |
| `tracking.py` | Link candidates into 2D tracks | Rules |
| `bounce.py` | Sub-frame bounce time and contact position + covariance | IN/OUT rules |
| `sports/pickleball/line_calling.py` | Rules: target region, P(out), IN/OUT/UNCERTAIN, announce policy | Pixels, detectors |
| `pipeline.py` | Wires the stages for one camera | (glue only) |

## Coordinate systems

- **Court frame**: origin at the centre of the net on the playing surface; +X
  across the court (right when standing behind the side-A baseline facing the
  net); +Y from side A to side B; +Z up; metres. Court dimensions are measured to
  the outside edges of the lines.
- **Pixels**: (u, v), origin at the top-left of the full-resolution frame.
- **Camera**: OpenCV convention, `X_cam = R · X_court + t`.

## Time base

- Single file: seconds from the first frame's presentation timestamp (PTS).
  Frame time is treated as the middle of the exposure.
- Live, multi-camera (`live/clocksync.py`): the server pings each phone
  (5/s at first, then 1/s); the phone answers with its clock. The offset comes
  from the round trips with the smallest RTT, plus a drift term once there is
  20 s of history. Every frame carries its *capture* timestamp (from the
  browser's `requestVideoFrameCallback` metadata), mapped onto the session
  clock (seconds since the server started), never its arrival time. On the
  LAN the RTT is a few ms, so the mapping error is about 1-3 ms. Bounces from
  different cameras are grouped within 80 ms.

## Event model (`events.py`, schema 1.0)

1. `BallObservation`: one detection in one frame (camera, frame, t, u, v,
   confidence, detector provenance). Immutable.
2. `BounceEvent`: reconstructed contact: t ± t_std, court (x, y), 2x2
   covariance, supporting observation ids, algorithm provenance.
3. `LineCallEvent`: rules interpretation: context (serve/rally), target region,
   p_out, result, `announce` flag, call text.

Every derived event records its algorithm, version and parameters, so outputs
can be regenerated from raw observations when algorithms improve.

## Key technical decisions

| Decision | Rationale |
|---|---|
| Full camera model, not just a ground homography | At contact the ball centre is one radius above the ground; ray ∩ plane z=r removes a 5–10 cm bias (`tests/test_camera.py`). |
| Sub-frame bounce from two fitted curves meeting at a kink | Recovers contact time and position between frames; F-statistic picks the split; impulse direction must point "up" in the image. |
| Report uncertainty, decide by P(out) | The system stays silent unless p_out ≥ 0.95; a wrong "OUT" is the worst outcome. |
| Calibration by clicking court keypoints, estimating focal length | No phone-specific lens data needed. Net-post tops (3D points) strengthen it. |
| Classical detector first, behind an interface | No training data needed; a yardstick for the neural model (TrackNetV3/WASB family) that will replace it. |
| Synthetic scenes with exact ground truth | Pipeline tests and design experiments before real footage. Results are an upper bound (no players, spin, shadows, rolling shutter, distortion). |
| Licensing: permissive only | MIT/BSD/Apache dependencies. Ultralytics YOLO (AGPL) deliberately avoided. FFmpeg comes in through PyAV under LGPL. |
| Python 3.12 venv, no PyTorch yet | PyTorch's last Intel-Mac build is 2.2.2. Neural models will be trained on a cloud GPU and exported (ONNX → Core ML for phones). |

## Live system today (approach A: phones stream, Mac processes)

```
 phone browser (no app)                        Mac: bt serve (aiohttp, Python)
 ──────────────────────                        ──────────────────────────────
 getUserMedia 720p/60  ──JPEG + capture t──▶   ws_camera: clock sync, frame queue
 requestVideoFrameCallback timestamps          worker process per camera: detect → track → bounce
 ping/pong for clock sync                      LiveJudge: group reports (80 ms), fuse (inverse
                                                 covariance), corroborate, secondary-bounce filter,
                                                 line call → dashboard speaks OUT / FAULT
```

Guards against a wrong "OUT" (the costly error):
1. Bounce physics (`bounce.ballistic_check`): a kink is only a bounce if a
   ground contact explains it (descending before, rising after, sane
   restitution, direction roughly kept). Rejects paddle hits, net/post hits,
   apex kinks from dropped frames.
2. OUT needs bounce confidence ≥ 0.6.
3. Fusion inflates the uncertainty when cameras disagree (chi-square test).
4. If two cameras can see the spot, OUT needs both to report it.
5. p(out) ≥ 0.95, otherwise silent.

Why web pages and not apps: no $99/yr developer account, works on iPhone and
Android, nothing to install. Limits: browsers give 30-60 fps, not 240; and
the phone must keep the page open. Approach B (below) needs native apps.

## Target architecture for live calls (approach B: on-phone processing)

```
 iPhone (custom capture app, per camera)                 Central server (Python, Intel Mac OK)
 ───────────────────────────────────────                 ─────────────────────────────────────
 240 fps capture, locked exposure, no stabilisation       clock sync master
 ball detector (Core ML) + tracker + bounce.py logic ──▶  fuse BounceEvents from several phones
 sends BallObservation / BounceEvent over WebSocket       line_calling.py → announce OUT / FAULT
 keeps rolling video buffer, uploads clips on request ◀── request clip for replay / review
```

The Python `bounce.py` and `line_calling.py` are the reference implementations.
The phone ports them, and both are checked against the same test cases.

## Known limitations (Phase 0)

- Multi-camera fusion combines per-camera ground positions; no 3D
  triangulation of the flight yet.
- Classical detector: will be confused by players, shadows, other yellow
  objects. Not validated on real footage.
- No lens distortion model: use the 1x lens.
- Serve context must be supplied manually; who-hit-the-ball is unknown.
- Uncertainty is from a model-based bootstrap and must be checked against
  chalk-mark ground truth.
- Contact patch radius (1 cm) is an assumption, to be measured.
