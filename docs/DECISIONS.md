# Decision log

Product and engineering decisions, newest first, with the reason and the evidence. The raw
request/outcome history is in [evolution/LOG.md](evolution/LOG.md) (written automatically by a
Claude Code hook); this file keeps only what was decided and why.

## 2026-11-19 (evening) · lobs, calibration from the lines, repository

| Decision | Why / evidence |
|---|---|
| **Bounce physics gives a velocity covariance; the "turned" / "changed speed" checks only reject when out of range by > 2 standard deviations** of that camera's measurement. Restitution stays a plain range check. (`bounce.py` 0.4.0) | Lob study (`scripts/lob_study.py`): one camera measures velocity across its view to 2-8 cm/s but along its view with 1.3-2.3 m/s median error (p90 5-11 m/s). True bounces were rejected for "turning" that was measurement error (290 reports in the full study). Paddle hits still fail: every true bounce had e = 0.19-0.80 from every camera, paddle hits e = 1.5-12. The noise floor (4 px) was calibrated on the study: with 1 px the real errors were 2-5x the predicted. |
| **Play state uses the cameras combined** (inverse-covariance fusion of the flight velocities) instead of the best-fitting camera; **lob rules**: a ball falling >= 8 m/s counts as a shot (apex above ~4 m); a ball falling >= 7 m/s is never a "dead ball"; the rally window stretches with the incoming ball's flight time (up to 7 s). (`playstate.py` 0.2.0) | Single-camera horizontal speed was off by up to 12 m/s, which decided "dead ball" / "shot". Full study (54 scenarios): OUT lobs left silent 10/21 → 2/21 (the 2 are 3 cm out: UNCERTAIN at the 95 % bar, by design); wrong OUT 0 → 0. Trade-off: a ball tossed back with an apex above ~4 m at the start of play would be treated as a shot. |
| **"Snap to lines" calibration in the dashboard**: tap 4 corners of the near half roughly, the server places every keypoint on the painted lines (stripe search across each predicted line + robust fit, near half first, net excluded); the user reviews and saves. (`autocal.py` 0.2.0) | Field-test-2 frames, taps 25 px off: lines fit to 0.5-1.1 px, 95-97 % of samples on the paint, identical result from any start. The snapped corners sit on the paint where the hand clicks were ~8-10 px off. Fully automatic (no taps) still fails on those frames (neighbouring courts, nets): stays experimental. |
| **After a camera is confirmed, the others are refined**: (1) every other camera is re-snapped to its own lines; (2) bounces seen by the confirmed camera and another camera become ground points for the other camera; after 15+ spread bounces a recalibration is proposed if the cameras then agree clearly better (keypoints + bounces, or bounces alone if the camera was bumped). Always a proposal on the camera card, never applied silently. (`geometry/crosscal.py`) | Lines only constrain a camera where lines are visible; bounces land where calls are made. Synthetic: a bumped camera 16 cm → < 3 cm from the reference; few noisy clicks improved > 2x. **Field test 2 (real)**: iPhone and Samsung agreed within 6-18 cm on the Samsung's near half but the Samsung put far-half bounces 0.7-1.5 m closer to the net (median disagreement 87 cm over 29 shared bounces; snapping its lines only gave 80 cm). Refining the Samsung from 14-15 shared bounces with the iPhone as reference: 21-49 cm on the held-out bounces. A low camera's far half is its weak spot. |
| **`--court-scale`** on `bt serve` / `calibrate` / `analyze` / `court`; play thresholds scale (speeds and times by sqrt(scale), distances by scale); practice-court calibrations live in their own folder. | Mini-court sessions. Gravity does not scale, so a shot with the same arc on a court k times smaller is sqrt(k) times slower. |
| **Commits as `vikramgore2007` with the GitHub no-reply address** of the repo owner; history rewritten before the first push (camera named after a person renamed `samsung`). | The repository is public: no personal e-mail or names in it. |
| **Auto-commit + push after a passing full test run** (`scripts/hooks/autocommit.py`, Stop hook; `tests/conftest.py` records the tested working tree). Only the exact tree that passed is committed; credential-like files and files > 5 MB are refused. `BT_AUTOCOMMIT=0` turns it off. | Requested. Running the 7-minute suite inside a hook after every response would be too slow, so pytest leaves a fingerprint and the hook compares. |

## 2026-11-19 · after field test 2 (full-size court)

| Decision | Why / evidence |
|---|---|
| **Play state**: only bounces of a ball in play are announced (dead balls, second bounces and, at the start of play, slow non-shots stay silent). `balltracker/live/playstate.py` | Field test 2 announced OUT for pre-serve bounces and for second bounces of unreturned balls 1.4-1.9 m behind the baseline. Replay of 550 s: 7 announced OUTs before, 3 after (all confirmed by both cameras). |
| **One camera alone may not announce an OUT** when its uncertainty across the line is > 15 cm. | The far-baseline calls came from one phone 16 m away looking along the court: ±25 cm, possibly biased. 0 wrong OUT is objective #1; silence costs less. |
| **Net-top points removed from calibration clicking**; calibration now names likely mis-clicks (leave-one-out). | Portable net posts stand ~30 cm outside the sidelines and higher than the net; clicking them gave 13-32 px errors. iPhone 9.3 → 2.7 px RMS without them. |
| **Bounce search batched, still tracks skipped** (server). | 88% of the Mac's time was the bounce search (22 trial fits per candidate split, 12x a second, on every track, including clutter). 11.8 → 5.2 ms/frame on the field iPhone stream; identical results (golden tests unchanged). |
| **Phone-side reduction** (`mobile/src/core/reducer.js`): still clutter dropped; full frame rate only around direction changes, ~30 fps elsewhere. `bt serve --full-rate` turns it off. | The user's principle: the phone sees everything, sends only what is needed. On field data: 27% fewer frames, 49/50 bounces kept at identical positions. Stricter settings lost bounces, so the conservative one is the default. Most of the Mac's relief came from the server fix above. |
| **Server listens on IPv6 too** and shows IPv6 addresses when the hotspot gives no reachable IPv4. | An iPhone hotspot on an IPv6-only carrier gives clients only a 192.0.0.x CLAT address that peers cannot reach. A phone cannot reach a device on its *own* hotspot that way either: the hotspot phone should not be a camera (or use an Android hotspot). |
| **Android detection thread at display priority; 16:9 capture.** | Samsung flagship: 12-27 ms/frame vs iPhone 4 ms, overheated, battery 45 → 3%. Likely efficiency cores + 1920x1440 (4:3) frames. To be verified on device. |
| **Auto-calibration kept experimental** (not in the dashboard). *Superseded the same evening by "Snap to lines" (above).* | Works on synthetic courts (2-3 px); on field-test frames 10-25 px errors at far corners (net tapes, distortion). A wrong pre-fill that looks right is worse than none. |
| **Evolution log via Claude Code hooks** (`.claude/settings.json`, `scripts/hooks/evolution_log.py`). | Requested: keep a history of requests and conclusions with the code. |
| **Git repository with sample data** (`data/samples/`), large media excluded. | Any clone must be able to run the tests. Camera images are not committed (they show people). |

## 2026-11-18 · browser and app on-phone detection

| Decision | Why / evidence |
|---|---|
| C++ detector compiled to WebAssembly for the browser phone page. | Test with many phones without installing apps. iPhone: 2.4-2.8 ms/frame in the browser. |
| FrameClock snaps browser timestamps to the frame grid (browser cameras only). | ±3 ms timestamp jitter randomly lost 1-2 of 5 bounces; with the fit, 5/5. |
| Detections always recorded for on-phone cameras; video only with `--record`. | Tiny (~40 MB per camera-hour) and makes every session replayable (`bt replay`). |
| Full court model needed for scaled courts (`--court`). | With the regulation model on a 5x smaller court, implied gravity is 5x and the physics check rejects real bounces. |

## 2026-11-17 and before · foundations

| Decision | Why |
|---|---|
| Phones run the detector; the Mac fuses and calls (protocol 2: coordinates + confidence, images only when useful). | A 2020 Intel MacBook cannot decode several 60-240 fps video streams. |
| One C++ core (`ballcore`) for iOS, Android, WebAssembly and Mac tests, bit-exact with the Python reference (`-ffp-contract=off`). | One algorithm, testable everywhere; golden tests catch any drift. |
| React Native (Expo) app rather than two native apps. | One UI codebase; native code only for camera + detector. |
| Speak only OUT / FAULT; 1-3 s delay acceptable. | What players need from a line judge. |
| No AGPL/GPL dependencies (e.g. no Ultralytics YOLO). Avoid the $99 Apple fee where possible. | Licensing freedom for a future club product. |
| Priorities: line calling → stats → coaching. | |
