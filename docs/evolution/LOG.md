# Product evolution log

Written automatically by `scripts/hooks/evolution_log.py` (Claude Code hooks): each request, then the conclusions of the work on it.

The entries below up to 2026-11-19 were written by hand when the hook was set up (the hooks start
working in the next Claude Code session); later entries are automatic.

## 2026-11-15 → 2026-11-18 · summary of earlier sessions

* Brief: multi-sport CV platform, pickleball line calls first (speak OUT/FAULT only, 1-3 s delay ok),
  iPhones 16/17 + Androids, 2020 Intel MacBook server, no AGPL/GPL.
* Built: offline pipeline (detection → tracking → kink bounce detection → line call), validated on a
  240 fps clip vs chalk marks (0.7 cm median); live server with browser phones; phone-side detector
  (C++ core shared by iOS, Android, WebAssembly, Mac tests); Expo/React Native app; replay/report tools;
  golden tests.
* Field test 1 (5x scaled yard court): Android could not join (no Wi-Fi, wrong browser), a snake plant
  was detected as the ball, serves missed in evening light; scaled court needs `--court`.

## 2026-11-19 · iOS app on device, field test 2

> Build and install the app on the iPhone; fix orientation and status-bar overlap; field test on a
> full-size court (2 cameras).

### outcome

* iOS app installed via Xcode 26.6 on iOS 27.2 (Developer Mode + trust profile); preview rotation and
  safe-area fixes; Wi-Fi drop counter fixed.
* Hotspot on an IPv6-only carrier: server now listens/advertises IPv6.
* Field test 2 analysed: calibration spoiled by net-top clicks; OUT calls for dead balls/second
  bounces; Mac overloaded by the bounce search; Samsung slow and overheating; cameras badly placed.

## 2026-11-19 · after field test 2

> Explain the net-top issue; why did the Mac get overwhelmed with the native app; send only needed
> data from the phone; why was the Samsung slow; weaker Androids for sections?; auto calibration with
> markers for side A/B; an evolution-log hook; fix the logging gap; a git repo with code, decision
> logs, docs and sample data; build the play state.

### outcome

* Mac: batched bounce search + still-track skip (11.8 → 5.2 ms/frame); phone-side reducer (27% fewer
  frames, 49/50 bounces identical); `--full-rate` to disable.
* Play state + single-camera OUT gate: on a 550 s replay 7 → 3 announced OUTs (all two-camera).
* Calibration: net tops removed, mis-click detection; auto-calibration experimental (synthetic ok,
  real frames 10-25 px off: not in the dashboard yet).
* Android: detection thread priority, 16:9 capture, ARM-only APK.
* Repo committed locally with docs/DECISIONS.md, docs/FIELD_TEST_2_RESULTS.md, data/samples/.


### 2026-11-19 17:57 · outcome

Everything is built, tested and committed locally: 3 commits, 69 tests passing, including the slow end-to-end and JavaScript tests. Auto-calibration is the one item that isn't ready.

## Your questions

**What went wrong with the net-top points.** The software expects the point directly above where the net crosses each sideline, at the net's official height (91 cm). On your portable net, the posts stand about 30 cm outside the sidelines and are taller, so clicking the post tops gave the software points in the wrong place. The point it wanted has nothing on it to click, which makes it useless anyway. I've removed it from the click list. The dashboard now also names any click that disagrees with the others; it caught the bad net-top click in today's iPhone calibration.

**Why the Mac was overwhelmed even with the app.** The phones did their part (4 ms per frame on the iPhone). The bottleneck was a step that always stays on the Mac: searching every moving object's path for the moment of a bounce. At 120 fps, with clutter adding extra objects, that one step used 88 % of the Mac's time.
- **Mac fix:** that search is now batched, and objects that aren't moving are skipped. The same results come out more than twice as fast. Your 100-minute session used to take longer than real time to replay; 550 s of it now replays in 3 minutes.
- **Phone fix, as you asked:** the app drops still clutter and sends full frame rate only around bounces and hits, about 30 fps otherwise. On your real data it sent 27 % fewer frames and kept 49 of 50 bounces at identical positions. Stricter settings saved more but lost bounces, so I kept the safe setting. `bt serve --full-rate` turns it off if you want every frame recorded.

**Why the Samsung was slow and hot.** Probably two causes:
- Android ran our detector at normal priority, so it likely landed on the phone's slow power-saving cores.
- The camera delivered 1920×1440 instead of 1920×1080, a third more pixels per frame.

It was also on battery (45 % → 3 %). The app now runs detection at high priority and asks for 16:9 frames. This is untested on a device: check that the dashboard shows *detect* under 8 ms next time. Also keep it plugged into a power bank.

**Weaker Android phones covering one section.** Useful as long as they manage at least 30 fps at 1280×720. The Redmi managed only 12. Placed low and close, looking along one line, they measure that line very precisely, which is exactly what a single far camera can't do. Each one needs at least 6 calibration points in its view. More detail is in `docs/FIELD_TEST_2_RESULTS.md`.

**Hooks in VS Code.** Yes, they work. The evolution log is already running: each substantive request and my final conclusions go into `docs/evolution/LOG.md`, and background-task notifications are filtered out.

## What else was built

- **Play state** (based on how a referee decides):
  - a ball that arrives with almost no forward speed (a pre-serve bounce, or a dropped or picked-up ball) is never called;
  - a ball's second bounce after it wasn't returned is never called, however long it takes to land;
  - at the start of play, an OUT needs a real shot or a Serve button press;
  - feeding drills still get called.
- **One-camera rule:** a single camera can't announce an OUT if its uncertainty across the line is over 15 cm.
- **Effect on today's data:** on 550 s of your session, these two rules took announced OUTs from **7 to 3**, and all 3 were confirmed by both cameras. I still can't say which calls were right without ground truth.
- **Small fixes:**
  - the dashboard has an APK QR code using plain `http`;
  - the server works on IPv6-only hotspots;
  - the clutter numbers are now written to the session log;
  - the APK is down to 43.5 MB, from 91 MB.
- **Git repository:**
  - code, decision log (`docs/DECISIONS.md`), field results and sample data (`data/samples/`: 60 s of real detections, no images because they show people);
  - recordings, videos, screenshots and build output are left out;
  - a fresh clone runs the tests with the setup steps in the README;
  - commit author: see the git log.

## Not finished: auto-calibration

On clean synthetic courts it works:
- snapping all points from 4 rough clicks is accurate to about 2 px;
- fully automatic detection finds the court, though sides A and B need the printed markers (`docs/markers/`) to tell apart.

On your real frames, the far corners came out 15–25 px off; your careful clicks are 2–3 px. The net's white tapes behind the far lines confuse it, and lens distortion may add to it. Points that look right but are off would be worse than clicking, so it's tested but not in the dashboard yet. It's the next thing to improve, and I can use today's frames for that.

## Before the next session
- **iPhone app:** rebuild and reinstall it, since the data reduction lives in the app. Connect the iPhone by cable and tell me to go ahead.
- **Android app:** install the new APK from the dashboard QR code or WhatsApp.
- **Pushing the repository:** send me the address and credentials when you're ready.

## 2026-11-19 19:29 · request (session 1661f7c3)

> Commit name should be vikramgore2007
> 
> https://github.com/7vikram7/BallTracker
> ~/Vikram/BallTracker/Secrets
> 
> Clone the repo and move code into it 
> 
> Add to post response hook. Each time after tests are successful, you need to commit and push
> 
> Can you take a stab at auto calibration? Also, write logic that after confirmation for 1 camera, refinement should run on all cameras to futher accurately auto calibrate if possible. 
> 
> Also can you run a detailed analysis of what happens when lobs are played.  With respect to all aspects of our logic so far. Run some tests on mock data. 
> 
> Also, will tests on my mini court help you?
> I could run some tests on it helping you test and refine your logic if needed.  Add the start command to accept a parameter of court scale if needed.
