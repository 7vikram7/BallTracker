# Roadmap: React Native camera app with on-phone processing

**Goal:** each phone tracks the ball itself at 120–240 fps and sends the Mac
only coordinates with a confidence score. Images are sent only when a call is
close. The Mac stays the judge: it fuses the cameras, makes the call, and runs
the dashboard and voice. Nothing in the judge has to change for this, because
it already works on bounce reports and doesn't care where they were computed.

## Status (2026-11-18)

| Phase | State |
|---|---|
| 0.5 server side | **Done.** Protocol 2 (detections + previews) on `/ws/edge`; Python and JavaScript simulated app phones; `bt live-demo --edge`: 8/8 bounces, 0.76 cm median, 0.33 s latency, Mac CPU 0.34 cores for 2 cameras (was about 2.6) |
| 1 app shell | **Code written** (mobile/): Connect + Camera screens, QR scan, settings, server link with reconnect, simulated camera for Expo Go. Core logic tested in Node; screens not yet type-checked |
| 2 detector on the phone | **Code written.** C++ detector matches the Python reference exactly on synthetic and real 240 fps video; Swift (AVFoundation, 240 fps, stabilisation off, fixed shutter) and Kotlin (CameraX, RGBA) capture written but **not compiled yet**. 11.5 ms per 1080p frame on the Intel Mac, so expect a few ms on an iPhone |
| 3–5 | Not started |

Next: install Xcode at home, build on the iPhones, run the checklist in mobile/README.md.

## How we proceed (updated 2026-11-18)

**One change to the plan.** Moving only the *detector* to the phone already took the Mac from
about 1.3 cores to about 0.17 cores per camera. Tracking, bounce fitting, fusion and calls stay on the Mac,
where they are easy to change, are replayed exactly from recorded detections (`bt replay`), and are
protected by the golden tests. So **phase 3 (whole pipeline on the phone) moves to "only if
needed"** (e.g. if Wi-Fi drops cause lost bounces), and the effort goes to accuracy and setup instead.

| Step | What | Done when |
|---|---|---|
| **A. Device bring-up** (now) | Build on iPhone 16/17 (and one Android); fix compile errors; run the checklist in mobile/README.md; measure *detect ms* at 120 and 240 fps | Both iPhones stream 240 fps (or 120 if 240 can't keep up) for 20 min without drops or overheating |
| **B. Field test 1, twice** | Same court and drill: one session with browser phones (60 fps), one with the app (120/240 fps), both `--record`; score with `bt report --marks` | Numbers for 60 vs 240 fps on real bounces; 0 wrong OUT in both |
| **C. Data loop** | Every session recorded and kept; good drill sessions become golden fixtures; `bt replay` on all of them before any logic change is accepted | A bank of real drills that every change is checked against |
| **D. Close calls** (phase 4) | Ring buffer of ball crops on the phone; clip request; image-based ball-to-line gap; replay on the dashboard | Close drill marks (within 5 cm) called right ≥ 90 % |
| **E. Setup without clicking** (phase 5 part) | Automatic court-line detection for calibration; bump detection from the phone's motion sensor; recalibrate prompt | Two phones set up in under 10 minutes by someone new |
| **F. Stats** | Keep thinned ball tracks in the session log (already computed on the Mac); shot speed, depth, bounce heatmaps per session | Report shows per-rally stats |
| **G. Club pilot** | Distribution decision (iOS $99 vs browser vs Android), multi-court, setup guide | One club court running a full session unattended |

Housekeeping before B: make the first git commit (the repo has none yet), so every session
records the exact code it ran (`session.json` stores the commit).

## 1. Why, in numbers

| | Today (browser page) | Native app, on-phone processing |
|---|---|---|
| Frame rate | 60 fps max (browser limit) | 120–240 fps on the iPhone 16/17 main camera |
| Timestamps | Browser-rounded to 1 ms (seen in today's test log) | Sensor timestamp of each frame (microseconds) |
| Wi-Fi per phone | about 7 MB/s (124 KB JPEG × 60) | about 5–20 KB/s of detections and events; about 1–2 MB burst per close call |
| Mac CPU per camera | about 1.3 cores (JPEG decode + detection) | about 0.02 cores (fusion only) |
| Cameras per Intel Mac | about 2 at 60 fps | 8+ (Wi-Fi and the judge are the limit, not the Mac) |
| Exposure / focus / stabilisation | Whatever Safari picks | Locked: short shutter, fixed focus, stabilisation **off** |
| Latency | 0.4–1.3 s (encode, send, decode, queue) | about 0.2–0.4 s (bounce confirmation time dominates) |

Our experiments showed accuracy improves with frame rate and short shutter (PHASE0_RESULTS: 240 fps
gave 0.7 cm median on the chalk marks). The app's main gain is
**240 fps live**, not only taking load off the Mac.

## 2. What the phone sends: two steps, not one

Your question was whether the phone could send coordinates plus a confidence score. Yes,
and I recommend getting there in two steps:

**Step 1: per-frame ball detections** (2D pixel position, size and score of
each candidate, about 40 bytes each). The phone runs only the detector, the expensive
part. The Mac keeps the tracking, bounce fit and physics check it already
has, now fed with detections instead of JPEGs.
* Small code to put on the phone (the detector is about 150 lines of Python).
* Removes the whole Mac bottleneck: JPEG decode plus detection is about 95 % of the CPU.
* Every algorithm change after the detector is still a server-only change, with no app re-install.

**Step 2: bounce events** (court position x, y with its 2×2 covariance,
contact time with its uncertainty, confidence, physics diagnostics), plus a
thinned trajectory (about 30 points per second) for stats and coaching later.
* Lower latency, and bounces survive Wi-Fi hiccups because the phone keeps the
  full-rate data.
* Needs the whole tracking, bounce and physics pipeline running on the phone (section 5).

Even after step 2, the phone keeps sending **heartbeats** with
"ball seen from t1 to t2". The Mac's rule that an OUT needs two cameras when two can see the spot relies on
the second camera's silence meaning *"I was watching and saw no bounce"*. That
is only true if the Mac knows the camera was actually processing frames at that moment.

## 3. Close calls: send the pictures

**When it's a close call:**
* p(out) between 0.05 and 0.95;
* the ball is within 3σ of the line;
* the cameras disagree (fusion inflated the uncertainty);
* or the call was downgraded to *unconfirmed*.

**What the phone keeps:**
* **A RAM ring buffer of ball crops**: a 256×256 patch around every detection for the
  last 3 s. At 240 fps that's about 700 crops, about 70 MB raw, which iPhones handle comfortably.
* **One full frame every 0.5 s**, so the lines around the ball are always available.
* **Optional: continuous HEVC recording** (hardware encoder) in rolling segments
  on the phone's storage for full slow-motion replay.

**How it flows:**
1. The Mac makes the fast-path decision. If it's confident (p ≥ 0.95), it announces
   immediately, as today.
2. For a close call it sends `clip_request(t_bounce ± 0.25 s)` to **every
   camera that could see the spot**.
3. Each phone replies within about 0.5 s with about 120 crops (JPEG, about 10 KB each) plus the
   nearest full frame: roughly 1.3 MB per camera.
4. The Mac re-judges using the images, then announces or stays silent. The total is still inside your
   1–3 s budget.

**What the images are used for:**
* **Image-based line check.** Find the tape edge and the ball's edge in the same
  crop at the contact frame and measure the gap in pixels, converted to cm at that spot.
  This is independent of calibration error, which is the largest remaining
  error source.
* **Human review:** a slow-motion replay of the bounce on the dashboard, as a "challenge" button.
* **Training data:** every close call becomes a labelled example for improving the detector later.

## 4. Architecture

```
PHONE (React Native app)                                        MAC (bt serve)
┌─────────────────────────────────────────────┐                ┌─────────────────────────────┐
│ UI (React Native / TypeScript)               │  control       │ ws/edge ingest  (new)       │
│  connect (QR / Bonjour) · settings · status  │◀──────────────▶│  clock sync (as today)      │
│                                              │                │                             │
│ Capture (native: Swift / Kotlin)             │  detections    │ step 1: tracker+bounce+     │
│  240 fps, locked shutter/focus/WB, no stab.  │───────────────▶│   physics (existing Python) │
│        │ every frame (no JavaScript)         │  or bounces    │ step 2: skip to fusion      │
│        ▼                                     │───────────────▶│                             │
│ Ball core (C++, shared iOS + Android)        │  heartbeat     │ LiveJudge (unchanged):      │
│  detect → track → bounce → physics → court   │───────────────▶│  fuse · corroborate · call  │
│        │                                     │                │        │ close call?        │
│        ▼                                     │  clip_request  │        ▼                    │
│ Evidence ring buffer (crops + keyframes)     │◀───────────────│ clip store + image line     │
│                                              │  clip (binary) │ check + replay on dashboard │
│                                              │───────────────▶│                             │
│ Low-rate preview (1 fps) / full still        │  preview       │ dashboard thumbnails,       │
│  for dashboard and calibration               │───────────────▶│ calibration (as today)      │
└─────────────────────────────────────────────┘                └─────────────────────────────┘
```

**Key rule:** frames never pass through JavaScript. React Native draws the UI
and holds settings. The camera and ball code run natively on their own threads
and send events up to the UI only for display.

## 5. What we need to build

### 5.1 Ball core in C++ (shared by iOS and Android)

A port of what runs in Python today, with Python kept as the **reference**.

| Python today | C++ port | Notes |
|---|---|---|
| `detection.py` | colour gate + connected components | Work on the camera's native YUV frame. Yellow is a chroma property, so threshold the half-size Cb/Cr plane (4× fewer pixels). After lock-on, search only a window around the prediction; full-frame search every Nth frame. Budget at 240 fps: < 2 ms per frame. |
| `tracking.py` | same association, gates, costs | Small fixed-size arrays; Hungarian assignment on at most ~10×10. |
| `bounce.py` | two-quadratic fit, F-test, bootstrap, `ballistic_check` | Eigen for least squares. A bootstrap of 80 fits is about 1 ms in C++. |
| `geometry/camera.py`, `court.py` | projection, ray to plane, court lines | The camera model comes **from the Mac** after calibration. |
| `line_calling.py` | optional on the phone | Only for a local display; the Mac stays the official judge. |

**Parity tests** are the safety net. The same recorded frames (from `--record`
sessions and the slow-mo originals) go through Python and C++; detections must match
within 0.3 px and bounces within 1 mm and 0.2 ms. These run on the Mac (C++ built
natively) on every change, so a phone isn't needed for most testing.

### 5.2 Native capture: iOS (Swift)

* AVFoundation: choose the main camera's 1080p 240 fps format (or 120 fps, our choice
  per session). Deliver frames with `AVCaptureVideoDataOutput` straight to the C++
  core.
* **Lock** shutter (for example 1/1000–1/2000 s outdoors), ISO, focus, white balance after a
  short auto-adjust. **Turn off** video stabilisation: it warps the image frame by frame,
  so the calibration would no longer hold. Turn off HDR. Use only the 1× lens.
* Timestamps: each frame's presentation time (host clock, about µs), mapped to session
  time with the clock sync we already have.
* Keep the screen on, monitor `thermalState` and step 240 → 120 → 60 fps when the
  phone gets hot rather than letting iOS throttle unpredictably.
* Permissions: camera; **Local Network** (iOS asks before the app can talk to the Mac,
  and needs the Bonjour service name declared); allow plain `ws://` on the local
  network so we can drop the certificate step.
* iOS stops the camera when the app isn't on screen. The phone stays a dedicated
  camera while in use, as now.

### 5.3 Native capture: Android (Kotlin)

* Camera2 / CameraX at 30–60 fps with ImageAnalysis: works on most phones.
* **Caveat:** on most Android phones, **120/240 fps frames can't reach the CPU**.
  Android's high-speed mode only feeds the screen and the video encoder. Getting them
  would need GPU processing (OpenGL/Vulkan), which is heavy work and varies by phone.
  **Plan: the spare Androids are 60 fps helper cameras; the iPhones are the
  240 fps main cameras.** The fusion already weights each camera by its accuracy, so mixing is fine.
* Sensor timestamps (`SENSOR_TIMESTAMP`, check its time base per device).

### 5.4 React Native app (TypeScript)

* **Expo with a development build** (not Expo Go, which can't load our native
  code). Our Swift, Kotlin and C++ are Expo native modules. Builds run **locally on the Mac**
  (`npx expo run:ios --device`), which works with a free Apple ID.
* Screens:
  * **Connect:** scan the QR code from the dashboard, or auto-discover the Mac via Bonjour.
  * **Camera setup:** name/position, fps, lock exposure, live preview with the ball marked.
  * **Streaming:** status, fps, temperature, clock quality.
* Camera library: first test whether **react-native-vision-camera** (MIT) can do
  everything in 5.2 (240 fps to a native plugin, locked shutter, stabilisation off).
  If it can't, we write our own small capture module; the UI is the same either way.
* Settings and calibration are cached on the phone so a reconnect is instant.

### 5.5 Server (Mac) changes

* `ws/edge` endpoint speaking **protocol v2**, alongside today's browser endpoint, so
  browser phones and app phones can mix in one session.
* Messages, versioned:

  | Message | Direction | Contents |
  |---|---|---|
  | `hello` | phone → Mac | device, model, lens, fps, resolution, app and algorithm versions |
  | `ping` / `pong` | both | clock sync, as today |
  | `detections` | phone → Mac | batch every 50 ms: frame time plus candidates (u, v, r, score) |
  | `bounce` | phone → Mac | step 2: bounce report with diagnostics |
  | `track` | phone → Mac | step 2: thinned trajectory |
  | `heartbeat` | phone → Mac | every second: fps captured/processed, drops, temperature, battery, *ball seen* intervals |
  | `calibration` | Mac → phone | camera model after calibration |
  | `config` | Mac → phone | colour gate, thresholds |
  | `still_request` / `still` | both | full-resolution frame for calibration |
  | `preview` | phone → Mac | 1 fps thumbnail |
  | `clip_request` / `clip` | both | close-call evidence (binary) |

* The edge camera has no worker process. Its detections feed the existing
  `LiveCameraPipeline` minus the detector (step 1), or go straight to `LiveJudge` (step 2).
* Close-call path in the judge: hold the decision, request clips, run the image line check,
  then decide. Clip store and replay on the dashboard.
* **A Python "edge phone" simulator** (an extension of `bt fakephone`) that runs the
  Python core and speaks protocol v2. With it, the whole server side is built and
  tested before any app code exists.

## 6. Phases

Each phase has an exit test. We don't start the next phase until it passes.

| Phase | What | Exit test |
|---|---|---|
| **0.5: server side, in Python** (now, no phone code) | Protocol v2, `ws/edge`, edge simulator, session scoring against the marks sheet | `bt live-demo` through the edge path gives the same accuracy as today; Mac CPU per camera < 0.1 core; 4 simulated cameras on the Intel Mac without drops |
| **1: app shell and capture spike** | Expo app; connect, clock sync, preview, still for calibration; iOS capture spike (240 fps buffers, shutter lock, stabilisation off, timestamps); Android at 60 fps | Installed on iPhone 16, iPhone 17 and one Android; connected for 30 min; spike confirms the 240 fps settings, or tells us to write our own capture module |
| **2: detector on the phone** (step 1) | C++ detector + parity tests; phone sends detections | Parity ≥ 99 % within 0.3 px; 240 fps sustained for 20 min (in shade); chalk drill **beats Field test 1** |
| **3: full pipeline on the phone** (step 2) | Tracking, bounce, physics, projection in C++; bounce and track messages; heartbeats | Same accuracy as phase 2; bounce-to-call latency < 0.5 s; survives a 5 s Wi-Fi dropout without losing bounces |
| **4: close-call evidence** | Ring buffer, clip protocol, image line check, dashboard replay | Clips from every camera that saw the spot within 1.5 s; image check agrees with chalk on ≥ 90 % of the close drill marks |
| **5: club-ready** | Automatic court-line detection (no clicking); bump detection from the phone's motion sensor → "recalibrate" warning; setup wizard; multi-court; diagnostics upload; distribution | A newcomer sets up 2 phones and calibrates in under 10 minutes with no help |
| **Later** | One phone acts as the hub (no Mac); stats from trajectories; coaching | — |

## 7. What you'll need

**Software (all free):**
* Xcode, with a free Apple ID signed in (it needs to support iOS 26 for the iPhone 17; check it installs on this Mac).
* Android Studio, Node.js, the Expo CLI.

**Accounts:**
* No paid accounts while developing.
* Free Apple ID limits: an app installed from Xcode **expires after 7 days** (re-install from the Mac, about
  2 minutes), up to 3 such apps per phone. Fine for us, not for a club.

**Hardware:**
* Tripods or clamps reaching 1.5–2.5 m.
* USB-C power banks (240 fps with a dim screen is roughly 15–25 % battery per hour, so plan on power).
* Sun shades for the phones.
* A good Wi-Fi router near the court, 5 GHz. Phase 2+ needs very little bandwidth, but a steady signal still matters.

**Test data:** the recordings from field tests. Every session recorded with
`--record` becomes test material for the parity tests and for tuning.

**Who does what:**
* I write the code: C++, Swift, Kotlin, TypeScript and the server.
* You do the on-device steps I can't:
  * install builds on the phones (and re-install weekly);
  * approve the camera and network permission prompts;
  * run the field tests;
  * report how the phones behave (heat, battery, mounting).

## 8. Risks

| Risk | Plan |
|---|---|
| A 240 fps library can't lock shutter or turn off stabilisation | Phase 1 spike answers this in days; fallback is our own Swift capture module |
| Android can't do 120/240 fps processing | Accept 60 fps helper cameras; iPhones lead |
| Phones overheat in sun at 240 fps | Shade, power, automatic 240 → 120 fps step-down, a heartbeat warning on the dashboard |
| C++ drifts from the Python reference | Parity tests on recorded data in every build; algorithm versions in every message |
| A phone gets knocked and the calibration is wrong without anyone noticing | Motion-sensor bump detection plus a periodic line-overlay self-check on the phone; until recalibrated, that camera's reports are ignored for calls |
| Clock sync in the app | Same ping/pong method (works to about 1 ms today); sensor timestamps remove the browser's 1 ms rounding |

## 9. Decisions for you (not needed yet)

1. **iPhones at a club.** Installing on players' iPhones without the $99 account
   only works through Xcode with the 7-day expiry. Options:
   * pay the $99 when going to the club (TestFlight / App Store);
   * club cameras are Android plus your own iPhones;
   * keep the **browser page** as the no-install option for iPhones.

   The server supports both, so this can wait until phase 5.
2. **Expo vs plain React Native:** I recommend Expo with a development build
   (faster to set up, same native power). Say if you prefer otherwise.
3. **Should phones announce calls too** (each phone speaks), or only the Mac or a
   speaker? It's easy to add later.
