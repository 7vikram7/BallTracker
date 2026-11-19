# Phase 0: synthetic results (no real footage yet)

All numbers below come from **synthetic** scenes. They are an upper bound: no
players or occlusion, no spin or skid at the bounce, no rolling shutter, no lens
distortion, no shadows. They answer design questions, not "does it work".

Raw data: `data/experiments/*.json`. Regenerate with `bt sweep ...` and
`python -c "from balltracker.experiments import run_track_noise_sweep; run_track_noise_sweep()"`.

## 1. Full rendered pipeline (detector → tracker → bounce → call)

Camera: `behind_baseline_high` (5 m behind the baseline, 4 m high), 1280x720,
simulated click-calibration with 1 px noise and a deliberately wrong FOV guess.
70% of shots aimed within ±15 cm of a line. Bounce detector v0.1 (independent fits).

| fps | shutter | recall | false bounces | position error median / p90 | wrong OUT | missed OUT |
|---|---|---|---|---|---|---|
| 30  | 1/1000 | 20/20 | 0 | 0.7 / 1.5 cm | 0 | 0 |
| 60  | 1/1000 | 20/20 | 0 | 0.8 / 3.3 cm | 0 | 0 |
| 120 | 1/1000 | 18/20 | 0 | 0.7 / 2.6 cm | 0 | 0 |
| 240 | 1/1000 | 20/20 | 3 | 0.9 / 2.8 cm | 0 | 0 |
| 30  | auto (½ frame), noise 6 | 14/15 | 0 | 1.1 / 2.6 cm | 0 | 0 |
| 60  | auto, noise 6 | 15/15 | 0 | 1.3 / 3.3 cm | 0 | 0 |
| 120 | auto, noise 6 | 15/15 | 0 | 1.4 / 2.6 cm | 0 | 0 |
| 240 | auto, noise 6 | 15/15 | 0 | 1.4 / 2.8 cm | 0 | 1 |

Calibration from clicked keypoints: about 1.5 px RMS, focal length within 0.1%,
camera position within 1 cm.

**Reading**: in clean renders the detector's positions are nearly noise-free
(~0.1–0.5 px), so even 30 fps works. That is not realistic. Section 2 adds
realistic detection noise.

## 2. Robustness to detection noise and missed frames (bounce detector v0.2)

Trajectories projected analytically (no rendering), then per-frame Gaussian
pixel jitter and random dropped detections, 40 shots per row, 1920x1080, same camera.

| fps | 0.5 px | 1 px | 2 px | 4 px |
|---|---|---|---|---|
| 30  | 97% · 1.3 cm | 97% · 2.0 cm | 97% · 4.3 cm | 90% · 8.5 cm |
| 60  | 100% · 0.8 cm | 100% · 1.6 cm | 97% · 6.2 cm | 60% · 10.8 cm |
| 120 | 100% · 0.6 cm | 100% · 1.3 cm | 100% · 3.2 cm | 50% · 7.2 cm |
| 240 | 100% · 0.4 cm | 100% · 0.9 cm* | 100% · 3.1 cm* | 85% · 12 cm |

(recall · median position error; no dropped frames. *after the refine-window fix in §3; 90th percentile 3.3 cm at 1 px and 8.1 cm at 2 px.) False bounces per 40 shots:
30 fps 7–32, 60 fps 7–9, 120 fps 3–4, 240 fps 0–2.

**Reading**:

- **Detection precision matters more than frame rate.** Going from 1 px to 4 px of
  detector jitter costs far more than going from 240 to 60 fps. The detector
  (and image sharpness: fast shutter, 1080p, a closer camera) is where effort pays.
- **Higher frame rate mainly buys fewer false bounces and smaller tail errors.**
  False bounces fall from 7–32 per 40 shots at 30 fps to 0–2 at 240 fps. A
  false bounce is how a wrong "OUT" would happen, so this matters for the
  "silent unless sure" policy.
- The F-test threshold (`BounceConfig.gain_threshold`, now 6) trades recall
  against false bounces. Tune it on real footage.

## 3. What changed during these experiments

- v0.1 fitted the before/after curves independently and required them to meet
  inside one frame gap. It failed at high fps with noisy detections (240 fps, 2 px: 53% recall).
- v0.2 fits both curves **jointly, sharing the contact point**, searches the
  contact time continuously, then refines with a window centred on the contact.
  At 120 fps, 2 px: recall went from 47% to 100%.
- The refine step originally searched only ±1.5 frames (±6 ms at 240 fps); now at
  least ±15 ms. At 240 fps, 2 px: median error went from 10.9 to 3.1 cm.
- Border blobs are now dropped: a ball cut off by the frame edge produced a fake kink.
- Camera framing: a phone 1 m behind the baseline with the 1x lens does not see
  the near sidelines. The presets and the recording guide reflect that.

## 4. Not yet known (needs real footage)

- Real detector noise on 240 fps iPhone footage (sets which column above applies).
- Effect of bounce skid and spin (the bounce is not an instantaneous kink).
- False bounce rate in real play (paddle hits, players, net).
- Real contact-patch size (chalk drill).

## 5. First real clip (2026-11-17, iPhone 17 Slo-mo, courtyard)

Clip: `TestData/iPhone17SlowMo/SlowMo.MOV`. Tennis ball, red tape line on a
tiled floor, yellow powder around the line, camera low (~0.5 m) and close
(1–3 m), portrait. Night, mains lighting. Scripts:
`scripts/realclip_2026-11-17/`, outputs: `data/real/2026-11-17/`.

**What the file turned out to be**

- An *exported* Slo-mo copy, not the original: H.264, 30 fps, 172 s. The
  start (~frame 0–110) and end (~4900–5160) are real time; frames ~250–4870
  are slowed 4×.
- The 100 Hz light flicker gives the true capture rate in the slowed part:
  it aliases to 0.1671 cycles/frame, i.e. **120.06 fps**, not 240. So
  either Slo-mo was set to 120 fps or the export dropped every other frame.
- Analysed with `--fps 120` (only valid inside the slowed section).

**Detection and tracking on real footage**

- Clutter: the yellow-striped snake plant (H 19–35, S ~100, sways in wind)
  and the yellow powder (H 20–24, S ~145) both passed the old colour gate
  (H 18–50, S ≥ 70). The ball is H 36–43, S ~190. Gate tightened to H 25–55,
  S ≥ 100 (configurable: `--ball-hsv`).
- Mains flicker made the whole frame "move" for the background model.
  Added per-frame brightness/colour normalisation (`flicker_compensation`).
- With those, the ball was detected in **every frame** of the flights checked.
- The tracker split flights at the bounce and lost the first points. Causes:
  low camera so the bounce reverses image velocity (gate too small); 3-point
  extrapolation amplifying jitter; one-point tracks with no velocity gate; and
  small clutter tracks stealing the ball. Fixed with a least-squares
  predictor, gates that scale with ball size and allow full reversal, and
  size-consistency matching. Synthetic sweep after the fix: 20/20 recall
  and 0 false bounces at 30/60/120/240 fps (was 18/20 at 120, 3 false at 240).

**Bounces**

8 flights in the slowed section → **8/8 floor bounces found**, sub-frame
contact time ±1–2 ms (one at ±6.5 ms). One extra event: the ball hitting the
flower pot (a real impact, not a floor bounce; with a proper calibration a
floor-plane / ball-size consistency check would reject it, and secondary-
bounce suppression already silences it).

Residual of the two-parabola fit around each bounce: **3.6–7.5 px per axis**
(one flight 11 px). The ball is 30–46 px in radius here, so 1 px ≈ 1 mm:
~4–8 mm. This is an upper bound on detector jitter, since it also absorbs
perspective curvature at close range and any timing irregularity from the
export.

**Line**: all 8 floor bounces landed right of the tape. Gaps from the tape's
right edge to the ball's nearest edge, using the ball itself as a ruler
(6.7 cm diameter, so roughly ±15%): 3.3, 8.7, 13.3, 14.6, 27.5, 28.9, 30.3,
31.1 cm. No ground truth was recorded for these, so this is not yet an
accuracy number.

**Not possible from this clip**

- Metric 3D: no calibration points (needs ≥ 6 known floor points).
- Accuracy: no measured marks to compare against.

## 6. Same session, original 240 fps file + chalk-mark photos

Original: `TestData/iPhone17SlowMo/AllPhotosData/IMG_5017.MOV`, HEVC 1080p,
11,449 frames in 55.9 s (nominal 240 fps, variable; average 204.8 fps, timed
from PTS). Ground truth: 9 stills taken during recording
(`IMG_5008`–`IMG_5016`, same viewpoint, camera moved < 1 px between them).
Each new mark was found by aligning consecutive stills and looking for loss
of yellow powder. Video shutter (from photo EXIF): 1/248 s, ISO 3200, f/1.6.

**Detection / tracking / bounces**

- 12 throws in the clip, **12/12 tracked, 12/12 floor bounces found**. Two
  landed outside the powder (0.79 s, 20.60 s), so they have no mark.
- Detector jitter (two-parabola residual near the bounce): **2.0–3.5 px**
  (one very close ball: 6.7 px). Roughly half the exported clip's 4–8 px.
- Contact-time uncertainty: ±0.5–1.6 ms (one at ±3.7 ms).
- Extra events: the pot impact again (conf 0.40), and one duplicate of the
  16.3 s bounce from a split track. Fixed: cross-track de-duplication in the
  pipeline (`dedupe_bounces`).

**Against the chalk marks** (10 marks: 9 photos, one of which shows two new marks)

The detected ball centre at contact vs. mark centroid. A constant offset of
~0.5 ball radius straight down the image is expected: the contact point lies
below the ball centre as seen by a low camera. A calibrated camera
computes this exactly; here it is not counted as error. The tape runs nearly
vertically in the image, so the horizontal component is the across-the-line
error that decides calls. It is converted with the ball as ruler
(6.7 cm = 2r px).

| photo | bounce t (s) | across-line error |
|---|---|---|
| 5008 | 5.609 | 1.6 cm |
| 5009 | 9.366 | 0.0 cm |
| 5010 | 16.346 | 0.0 cm |
| 5011 | 24.738 | 0.0 cm |
| 5012 | 28.436 | 0.6 cm |
| 5013 | 37.512 | 0.9 cm |
| 5014 | 41.321 | 1.5 cm (mark elongated, at the powder edge) |
| 5015 | 45.943 | 0.9 cm |
| 5015 (2nd mark) | 49.568 | 0.3 cm |
| 5016 | 52.907 | 0.8 cm |

**Median 0.7 cm, worst 1.6 cm.** The along-the-floor component, after the
constant offset, scatters ±0.2 r (about ±1.4 cm). Part of that is the offset
really varying with image position, which calibration would remove.

**Caveats**: close camera (ball 30–60 px radius, ~1 mm/px), a tennis ball,
one line, 10 marks, mark centroids from 1080p stills (marks are 3–9 cm
smears), and the scale comes from the ball, not a measured floor. This
validates the detector → tracker → sub-frame bounce chain on real 240 fps
footage. It does not yet validate a court-scale camera (ball 5–10 px),
calibration from court lines, or a pickleball.

## 7. Phone detector (for the app) on the same real clip (2026-11-18)

The app runs a simpler detector than the Mac: one running Gaussian per pixel instead of
OpenCV's MOG2 mixture, and an integer colour test (`balltracker/edge_detection.py`; C++ port in
`mobile/modules/ball-camera/cpp`). It was checked on the 240 fps original (IMG_5017.MOV, 11,449
frames) against the Mac detector, with the same tracker and bounce detector:

* **C++ vs Python reference:** identical candidates on every frame (differences < 0.0001 px),
  also in the BGRA (iPhone) and RGBA (Android) pixel layouts.
* **Phone detector vs Mac detector:** the same 11 bounced throws found, the same bounces matched to the
  chalk photos, and bounce pixel positions within 1.4 px on 7 of 8 matched bounces (7.6 px,
  about 0.4 cm, on the closest, largest-looking one, where the phone detector is slightly nearer the mark).
* **Speed:** C++ 11.5 ms per 1080p frame on the 2020 Intel Mac (while other work was running),
  versus about 200 ms for the Python reference. An iPhone 16/17 core should be several times faster;
  to be measured on the phone (the app shows *detect ms*).

Script: `scripts/realclip_2026-11-17/edge_detect.py ... --native`.
