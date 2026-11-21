# Decision log: request → analysis → decision → next

The project's history as a chain of requests from the owner, in order. Each entry records what
was asked, what the analysis found, what was decided, and what the roadmap looked like
afterwards. Read it top to bottom to understand why the system looks the way it does.

[DECISIONS.md](DECISIONS.md) has the same decisions as a reference table, newest first.
[PROJECT_BRIEF.md](PROJECT_BRIEF.md) is the original brief. The current roadmap is at the end.

---

## 1. Digest the brief, look for existing solutions and gaps (2026-11-15)

**Request.** Read the project brief: a multi-sport computer-vision platform, pickleball first,
with phones as cameras, an Intel Mac server and a Raspberry Pi. Look for existing solutions and
gaps. "None of it is set in stone."

**Analysis.**
* The brief's architecture is sound: four layers, observations kept separate from physical
  events and sport events, and a modular monolith rather than a distributed system.
* The risk is elsewhere. The brief says little about physics, timing and data. As written, it
  builds plumbing first and only finds out in phase 3-4 whether phone footage can support line
  calls at all.
* Existing products:
  * PlayReplay: cameras on the net posts looking down the lines, used on pro tours.
  * Owl AI: broadcast cameras plus AI.
  * PB Vision: one camera, uploaded clips, stats and coaching.
* None is open, cheap and live for a club.
* The machine: a 2020 Intel MacBook with no usable GPU for ML. PyTorch and ONNX Runtime have
  dropped or are dropping Intel Macs.

**Decision.** Keep the brief's shape, but **flip the order**: first prove, on recorded footage,
that phones can locate a bounce to a few centimetres; build the platform after that.

**Next.** Answer the owner's questions on phones, apps and licensing.

## 2. Why does the phone matter? More devices = more accuracy? Licences? (2026-11-15)

**Request.** The owner has two recent iPhones and some spare Android phones, and wants to test
with 2-3 devices and add more later. The goal is a learning project that may become a club
installation; nothing commercial yet. Live calls are required. Do any open-source libraries
limit commercial use? Is there a cheaper server than a new Mac?

**Analysis.**
* What makes a phone usable as a line-calling camera:
  * Frame rate: at 30 fps a fast ball moves about 60 cm between frames; at 240 fps about 7 cm.
  * Camera control: locked focus and exposure, a fast shutter, stabilisation off.
  * Frame timestamps accurate to about 1 ms.
  * One platform or two: each one needs its own capture app.
* More cameras help with coverage (a blocked or invisible line) and with overlap (cross-checking
  a bounce from two views). They do not fix a poor camera.
* Licences: Ultralytics YOLO is AGPL, which would force the whole product open if distributed.

**Decision.**
* The two iPhones are the main cameras; the Androids are extra test angles.
* No AGPL, GPL or non-commercial dependencies; prefer MIT, BSD and Apache.
* Priorities: live line calls, then stats, then coaching.

**Next.** Decide whether custom apps are needed.

## 3. Custom apps or existing streaming apps? What runs on the Mac? Phones do the tracking? (2026-11-15)

**Request.** Why build custom apps (the Apple developer programme costs $99/year)? What software
runs on the Mac? Could the phones track the ball themselves and send x, y and time with a
confidence ("approach B")? A 1-3 s delay is fine. Only OUT or FAULT needs to be said; otherwise
stay silent.

**Analysis.**
* Testing needs no paid account. A free Apple ID installs your own app for 7 days at a time.
* Accuracy tests run on recorded clips (Slo-mo 240 fps), so no app is needed for them.
* Streaming apps send 30-60 fps, heavily compressed, with stream timestamps rather than capture
  timestamps, and rarely lock camera settings.
* Approach B means code running on the phone, so it requires a custom app by definition.
* The Mac runs a long-running Python application, not a native macOS app.

**Decision.**
* The phones run the detector; the Mac fuses the cameras and calls. Only coordinates and a
  confidence are sent, images only when useful.
* The system speaks only OUT or FAULT, with a 1-3 s delay acceptable, and is silent unless sure.
* Python modular monolith on the Mac.

**Next.** Build phase 0: an offline pipeline that works on a scaled floor court and on a real
court.

## 4. Build a system for a scaled indoor court and a real court (2026-11-16)

**Request.** Testing may happen on a smaller, scaled floor court or directly on a real hard
court; build for both. Install whatever is needed.

**Analysis.** There was no footage yet, so the pipeline was built and tested on synthetic scenes
with ground truth.
* Frame-rate sweep: detection noise matters more than frame rate. Going from 1 px to 4 px of
  jitter costs far more than going from 240 to 60 fps.
* Higher fps mainly buys fewer false bounces: 7-32 per 40 shots at 30 fps, 0-2 at 240 fps.

**Decision.**
* Pipeline: detection → tracking → sub-frame bounce (both sides of the contact fitted jointly) →
  line call with uncertainty (IN, OUT or UNCERTAIN).
* Court dimensions are scalable.
* Sharp frames (fast shutter) are prioritised over frame rate.

**Next.** Record real footage with a 240 fps camera.

## 5. The camera app only reaches 60 fps; resolution can't be changed; use a dyed ball? (2026-11-16)

**Request.** The third-party camera app is capped at 60 fps on the owner's phone, even in HD with
HDR off. Instead of chalk, use a sponge ball dipped in dye?

**Analysis.**
* The stock Camera app's Slo-mo records real 240 fps (1080p) with true timestamps, but the
  shutter can't be set.
* Exported or messaged copies are re-encoded to 30 fps, so only originals are usable.
* A sponge ball bounces, marks and looks different from a pickleball, so it tests the wrong
  thing. A real ball that leaves a mark works: damp, thinned paint, or carbon paper over the line.

**Decision.**
* Record with stock Slo-mo, with exposure and focus locked by long-press, and send originals.
* Ground truth from a real ball that leaves a mark.
* Both written into RECORDING_GUIDE.md.

## 6. First real clip (2026-11-17)

**Request.** Analyse a first Slo-mo clip: a ball thrown at a taped line on a tiled floor.

**Analysis.**
* The file was an exported copy: 30 fps, with the slowed middle captured at 120 fps (worked out
  from the 100 Hz mains flicker).
* Clutter: a yellow plant and yellow powder passed the colour gate, and the flicker made the
  whole frame "move".
* Tracking split flights at the bounce.
* After fixes, 8 of 8 floor bounces were found, with contact time to ±1-2 ms.

**Decision.**
* Upright rotation for portrait clips.
* Flicker compensation.
* Tighter ball colour gate, configurable.
* Tracker: least-squares prediction, gates that scale with ball size, size consistency.

**Next.** Ground truth (measured marks) and the original 240 fps file.

## 7. Does this prove tracking works? Chalk-mark photos and the original file (2026-11-17)

**Request.** Compare with chalk marks: photos were taken after each bounce, and the original
240 fps file is included. In the real product, calibration must come from the court lines, not a
taped line.

**Analysis.**
* 12 of 12 throws were tracked and 12 of 12 bounces found.
* Against 10 chalk marks, the across-line error was **0.7 cm median, 1.6 cm worst** (the ball
  was used as the ruler, so about ±15 % scale).
* Detector jitter was 2-3.5 px.
* Not yet proven: a court-distance camera (ball 5-10 px instead of 30-60 px), a pickleball, and
  calibration from court lines.

**Decision.** Accuracy is good enough to move on (the owner agreed). The per-frame detections of
this clip are the regression data for real footage: `data/real/2026-11-17/clip_240fps/` and
`tests/test_real_clip.py`.

**Next.** Live: a Mac server accepting several phones.

## 8. Build the live server for multiple phones (2026-11-17)

**Request.** Run a server on the Mac that accepts feeds from several phones.

**Analysis.**
* No app or developer account is needed if the phones stream from a web page.
* Phone cameras in a browser need HTTPS, so the server uses a local certificate authority.
* Clock sync by ping-pong.
* Simulated two-phone test: 8 of 8 bounces called, 0 false calls, 0.8 cm median error, about
  0.4 s from bounce to call.
* One wrong OUT in testing: a kink in the ball's path that was not a bounce.

**Decision.**
* Browser phone page, dashboard on the Mac, calibration by clicking court points.
* Multi-camera fusion weighted by uncertainty.
* **Corroboration rule:** if two cameras can see the spot and only one reported a bounce, an
  OUT stays silent.

**Next.** First field test on a scaled court.

## 9. Field test 1 objectives; a React Native app with on-phone processing (2026-11-18)

**Request.** A scaled court will be taped in a yard. What are the objectives of the first test?
Plan a React Native app (rather than two native apps) that processes frames on the phone and
sends coordinates with a confidence, plus images only for close calls.

**Analysis.**
* From a connection test: 59 fps arrived steadily, but at 124 KB per frame (about 60 Mbit/s per
  phone), two phones would overload outdoor Wi-Fi.
* Grass gives a dead bounce, shows no marks, and sunlit blades look like the ball.

**Decision.**
* Test objectives, in order (FIELD_TEST_1.md):
  1. Never a wrong OUT spoken.
  2. Accuracy: median ≤ 2 cm, 90 % within 5 cm.
  3. ≥ 90 % of bounces seen by at least one camera.
  4. Stays up for 20 minutes.
  5. Calibration under 2 px.
  6. Call within 1.5 s.
  7. Everything recorded.
* A hard surface, not grass.
* App roadmap: React Native (Expo) UI, with native code only for the camera and the detector
  (ROADMAP_MOBILE_APP.md).

## 10. Build the React Native app now (2026-11-18)

**Request.** No recording possible while travelling; build the app in the meantime.

**Analysis.**
* One C++ detector core can serve iOS, Android and Mac tests.
* Its results are bit-exact with a Python reference (floating-point contraction is switched off).
* On the real 240 fps clip it found the same bounces as the Mac detector; 11.5 ms per 1080p
  frame on the Mac.
* Simulated app phones: same accuracy as browser phones, and the Mac's CPU load fell from about
  2.6 cores to 0.34 for 2 cameras.

**Decision.** Protocol 2: app phones send detections (every candidate, every frame) plus a
preview image every 1-2 s. Browser and app phones can be mixed.

## 11. Tighter tests; logging and reports to learn from past tests; roadmap (2026-11-18)

**Analysis.** A field test is only worth something if it can be re-examined later with new code.

**Decision.**
* Every session folder holds `session.json` (code version, settings, devices, summary) plus
  every calibration and camera health event.
* `bt sessions`, `bt report` (accuracy against marks) and `bt replay` (re-run a session with the
  current code and list changed calls).
* Golden tests pin exact outputs: real rally decisions, Python and C++ detector agreement, and
  identical messages between server and app.

## 12. Toolchains; Xcode on an Intel Mac (2026-11-18)

**Request.** Install the Android toolchain while Xcode installs. Can Xcode be installed from the
command line? Which Xcode version works?

**Analysis.**
* Downloading Xcode needs the owner's Apple ID, so it can't be done for them.
* Expo 58 needs Xcode 26.4 or newer, which needs macOS 26 (Tahoe).
* Xcode 27, which matches the phones' iOS, needs Apple silicon.
* Xcode 26.6 on Tahoe might still install on newer iOS. (It did, later.)

**Decision.** Upgrade the Mac to Tahoe and use Xcode 26.6; Android first in the meantime. The
owner types every password and accepts every licence.

**Roadmap note.** An Apple silicon Mac would also be a much faster server. Intel support ends
with macOS 27.

## 13. The C++ detector in the browser page too (2026-11-18)

**Request.** Run the same detector in the phone web page, to test with several phones without
installing apps.

**Decision.**
* The C++ core compiled to WebAssembly (43 KB), running in a worker thread.
* The page sends detections plus a preview, falling back to sending video.
* iPhone: 2.4-2.8 ms per frame.

**Found on the way.** Browser frame timestamps jitter by ±3 ms, which randomly lost bounces.
**Decision:** snap browser timestamps onto the camera's frame grid, which cut timing error from
about 2 ms to 0.2-0.3 ms.

## 14. An Android phone could not join; Wi-Fi at the court; scaled courts (2026-11-18)

**Request.**
* An Android phone could not join from the QR code.
* The court has no Wi-Fi: will a phone hotspot work?
* Does Expo Go support 240 fps? How much space does `--record` use?
* Why worry about a smaller court?

**Analysis.**
* Expo Go can't load custom native code, so it can't run the detector or reach 240 fps.
* The Android phone used a vendor browser; Chrome works.
* A phone hotspot works.
* On a court 5 times smaller with the full-size model, the implied gravity is 5 times too high,
  so the physics check rejects real bounces. A scaled court needs its own court model.

**Decision.**
* Standalone Android APK served by the Mac.
* Hotspot steps in the field-test checklist.
* `--court` for custom courts (later `--court-scale`).
* Detections are always recorded (about 40 MB per camera-hour); video only with `--record`.

## 15. iOS app on the phone; orientation, status bar, exposure (2026-11-18 → 19)

**Analysis.**
* Xcode 26.6 installs on newer iOS; the free account needs Developer Mode and trusting the
  profile.
* First real app run: a steady 120 fps, detection 3.9 ms per frame (the budget is 8 ms).
* The preview was sideways (frames sent were correct), and the UI ran under the camera cut-out.

**Decision.**
* Fix the preview rotation after the camera starts; safe-area insets on both platforms.
* Shutter guidance: 1/1000 s in daylight, auto only indoors or for setup. Don't change it
  mid-session.

## 16. Calibration when not all court points are visible (2026-11-19, asked before playing)

**Request.** Can calibration cope when a camera near the kitchen can't see every court point?
No changes before today's game; otherwise the cameras go at the corners.

**Decision.** No change before the game; corner placement for the test. This led to "Snap to
lines" (entry 20), which needs only the near half.

## 17. On court: the hotspot, IPv6, and the Android install (2026-11-19)

**Analysis.**
* The APK download failed: Android's downloader rejects the Mac's self-made certificate.
* The hotspot was on a carrier giving only IPv6 addresses, so the Mac's only IPv4 address was
  unreachable.
* An iPhone can't reach devices on its own hotspot over that path.

**Decision.**
* The server listens on IPv6 too and advertises an IPv6 address when there is no usable IPv4.
* The hotspot phone should not also be a camera; an Android hotspot is preferred.
* APK over plain http, with a QR code on the dashboard.

## 18. Field test 2: full-size court, 2 cameras (2026-11-19)

**Request.** A session was played with 2 cameras on a full-size court. Close the server and
report the findings.

**Analysis** (FIELD_TEST_2_RESULTS.md):
1. **Calibration:** clicks on the portable net's post tops were 13-32 px off. The post tops are
   not where the model expects the net to cross the sideline.
2. **OUTs for balls not in play:** a cluster of OUTs 1.4-1.9 m behind the far baseline.
   * Recalibrating barely moved them, so the bounces were real.
   * Most were second bounces of unreturned balls, or dead balls: a server bouncing the ball
     before serving, pickups.
3. **Mac overload:** 19 000 frames dropped and delays up to 9 s. The Mac's bounce search over
   every track (clutter included) took 88 % of its time.
4. **Samsung slow and hot:** 12-27 ms per frame against 4 ms on the iPhone; battery fell from
   45 % to 3 %.
5. **Placement:** one far phone looking along the court has ±25 cm depth precision.

**Decision.** See entry 19.

## 19. Questions after field test 2; phone-side data reduction (2026-11-19)

**Request.**
* What was wrong with the net-top points?
* Why was the Mac overwhelmed when the app does the heavy work?
* Send only what is needed: if the ball is in the air for 100 frames, send about 10, and the
  frames around the contact in full.
* Why was the Samsung slow? Would weaker Androids help for parts of the court?
* Calibration markers for the two sides.
* A log of requests and conclusions, and a git repository with code, decision logs, docs and
  sample data.

**Decision.**
* **Play state:** only bounces of a ball in play are announced. Dead balls, second bounces and
  slow non-shots at the start of play stay silent. Replaying 550 s: 7 → 3 spoken OUTs, all seen
  by both cameras.
* **A single camera may not announce an OUT** if its uncertainty across the line is above 15 cm.
* **Net-top points removed** from calibration; likely mis-clicks are named.
* **Batched bounce search, still tracks skipped:** 11.8 → 5.2 ms per frame, identical results.
* **Phone-side reducer:** still clutter dropped; full frame rate only around direction changes,
  about 30 fps elsewhere. 27 % fewer frames, 49 of 50 bounces identical; stricter settings lost
  bounces. `--full-rate` disables it.
* **Android:** detection thread at display priority, 16:9 capture (to verify on device).
* An evolution-log hook (evolution/LOG.md) and the git repository.

## 20. Repository, auto-commit, auto-calibration, lobs, mini court (2026-11-19)

**Request.**
* Commit as the given name to the given GitHub repo, and commit and push after every passing
  test run.
* Attempt auto-calibration, and after one camera is confirmed, refine the others.
* A detailed analysis of lobs through all of the logic, on mock data.
* Would mini-court tests help? Add a court-scale option to the start command.

**Analysis.**
* **Calibration:** fully automatic line detection fails at the real venue (neighbouring courts,
  nets). Starting from 4 rough taps of the near half, a search across each predicted line plus a
  robust fit puts the lines within 0.5-1.1 px of the paint.
* **Cross-camera:** in field test 2 the cameras agreed within 6-18 cm on one half but differed
  by 0.7-1.5 m on the Samsung's far half. Refining that camera from about 15 shared bounces cut
  it to 21-49 cm on bounces not used in the fit.
* **Lobs** (LOB_STUDY.md):
  * Bounce detection and position were fine (about 1 cm).
  * But one camera measures velocity along its line of sight badly (1-2 m/s median error).
  * Physics checks treated that as exact, so cameras rejected true lob bounces.
  * The play state took the speed from one camera, so lobs were labelled "dead ball" or "not a
    shot".

**Decision.**
* "Snap to lines" in the dashboard. Fully automatic calibration stays experimental.
* After a save, the other cameras are re-snapped and refined from shared bounces, always as a
  proposal to review, never applied silently.
* The bounce physics returns a velocity covariance; turn and speed-change checks reject only
  beyond 2 standard deviations; the restitution check stays strict (paddle hits fail it).
* The play state combines cameras by covariance, with lob rules: a fast fall counts as a shot,
  and the rally window grows with flight time.
* Lob results: OUT lobs announced 11 → 19 of 21; wrong OUTs 0 → 0.
* `--court-scale`: lines scale; the play state's speed and time thresholds scale by
  sqrt(scale), distances by scale. Practice-court calibrations are stored separately.
* Mini court: useful for centimetre ground truth, calibration on tape, high balls and phone
  endurance; not for real speeds, distances or venue lighting (MINI_COURT.md).
* Public repo: commits use a no-reply address, and a camera named after a person was renamed.
  Auto-commit only commits the exact tree a full passing test run recorded.

## 21. Would a couple of weak 30 fps Android cameras help? Share the data for other agents (2026-11-20)

**Request.** Would weak 30 fps Android phones on the court help? Put logs, test data and
motivation in the repository so other agents can analyse it and suggest improvements.

**Analysis.** A simulation of camera set-ups (CAMERA_RIGS.md):
* 2 good phones: 20 of 27 OUTs announced.
* Plus 2 ok weak phones: **24 of 27**, mostly bounces only 3 cm out. Each extra camera shrinks
  the combined uncertainty.
* Weak phones instead of the second good phone: 15 of 27, and weak cameras that missed the
  bounce **vetoed 3 correct OUTs**.
* No set-up produced a wrong OUT.

**Decision.**
* Weak phones are extras, never a replacement for a main camera.
* Proposed (not built): weight the "another camera saw nothing" veto by each camera's measured
  recall.
* Data shared without images:
  * real sessions as detections (`data/field/`);
  * the 240 fps clip as per-frame candidates (`data/real/2026-11-17/clip_240fps/`).
* The conversation itself is condensed into this decision log; raw transcripts and videos are
  not published.
* Found while replaying the full field test: velocity covariances could come out slightly
  negative, giving a camera negative weight in fusion. Fixed with an eigenvalue-floored inverse
  and zero weight for broken values. No spoken call changed.

---

## 22. Remove personal details from the repository's history (2026-11-20)

**Request.** Approved: remove the earlier published transcripts and personal details from the
history as well, not only from the latest version.

**Analysis.** Deleting a file in a new commit leaves it in every older commit. A scan of all
12 commits found the transcript folder, owner-specific words in an export script and in early
versions of the evolution log, and one home-folder path in a sample session. All commits
already used a no-reply author address.

**Decision.**
* History rewritten: the transcript folder dropped from every commit; files and commit messages
  passed through `scripts/hooks/privacy.py`; force-pushed. The latest files are unchanged except
  that one path.
* Commit IDs changed. Anyone with an older clone should re-clone, not merge.
* From now on, scrubbing happens before anything is written (the hook and the export), so a
  rewrite should not be needed again.

---

## 23. Night session on the mini court, two iPhones (2026-11-20)

**Request.** Analyse a night session under limited light: iPhone 17 and iPhone 16 (the spare
Redmi saw nothing and was not calibrated). Did the load optimisations work? And how should side A
be chosen when calibrating several cameras?

**Analysis.**
* **Side A differed between the cameras.** Each phone was calibrated with its own nearest end as
  "A". The second phone's bounces were exactly the first phone's turned 180° about the court
  centre (median disagreement score chi² about 3 400; after swapping its labels, 0.2). The judge
  correctly refused to call: 33 UNCERTAIN, 1 spoken OUT.
* **Mini-court size applied twice.** `court.json` stores the scaled sizes plus the factor;
  `CourtSpec.from_dict` scaled them again. The judge used the right court, but each camera's
  worker process and every replay used a 0.04-scale court.
* **Search region not scaled.** The image region where the ball is searched was the court plus a
  fixed 2.5 m margin and 6 m height. On a correct mini court that takes in lights and people
  around it, and bounces get lost: 4 bounces seen by both cameras instead of 20. The shared-bounce
  refinement needed 2 m of spread, which a 1.2 m-wide court cannot give.
* **Disagreeing cameras could still speak OUT.** On disagreement, fusion inflates the covariance.
  A precise camera saying OUT by 30 cm and another saying IN by 50 cm still gave p(out) 0.97.
* **Load: fine.** The iPhone 17 ran a steady 120 fps with no dropped frames, about 12% worker load
  and 8 ms median latency (the last field test dropped 19 000 frames). Phone-side reduction on the
  newly installed iPhone 16 sent 49% of frames at 5 kbit/s. The iPhone 17 still runs an older
  build without it (3.8 Mbit/s) and finished at 5% battery; both phones reached "serious" thermal
  state.
* The Redmi 8A in the dark: 10-30 fps, 35 ms detection per frame, almost no candidates.

**Decision.**
* Side A is one fixed end for every camera; the docs and the calibration dialog now say so. The
  server also detects a camera labelled from the other end from 3 shared bounces and proposes the
  swapped labels (in this session it would have fired about 2 minutes into play).
* Saved court sizes are final (`from_dict` only records the factor). The search margin and height
  scale with the court (at least 0.5 m and 2 m), and so does the refinement's required spread.
* When cameras disagree beyond their uncertainties, an OUT is spoken only if each camera on its
  own report calls OUT.
* Smaller fixes: frame rate is robust to clock-sync steps (a Redmi showed −1202 fps); the report
  shows the phone's capture rate rather than the reduced send rate.
* Replay with the second camera's labels swapped and all fixes: 20 bounces seen by both cameras,
  UNCERTAIN 33 → 13, 6 OUTs spoken. There is no ground truth for this session.

**Next.** Reinstall the app on the iPhone 17; keep phones charged and cooler. Next session: mark
contacts so the calls can be scored.

---

## 24. Field test 3: full court in morning sun, three cameras (2026-11-21)

**Request.** A detailed analysis of a 68-minute session on a club's full-size court
(`data/field/20261121-071625/`).

**Setup.**
* iPhone 17 behind the A-left corner: 1080p at 120 fps.
* Samsung SM-S948B behind the B-right corner: asked for 120 fps and delivered 58.
* Nothing A009P behind the A-right corner: 720p at 30 fps.
* The fourth phone was not connected.
* The Mac was on the iPhone 17's hotspot, which was IPv6-only. The app on the hotspot phone
  itself first stuck on "connecting".
* Setup took 23 minutes before all three cameras were calibrated, leaving about 45 minutes of
  play.

**Results.**
* 1 740 single-camera reports gave 1 286 decisions, 425 of them seen by 2 or more cameras.
* IN 608, OUT 22 (all spoken), UNCERTAIN 344; 312 later bounces were suppressed.
* Bounce to call: median 1.38 s, p90 1.7 s.
* There is no ground truth.

**Analysis.**
* **Clock sync is fine.** The pessimistic sync estimate was ±80-114 ms over the hotspot. Matched
  bounces show the real offsets: median 1 ms, interquartile range within ±10 ms.
* **Two cameras agree well.** iPhone 17 and Nothing agreed to 5 cm right after calibration and
  11-22 cm later.
* **The Samsung disagreed.** It was 48 cm off the iPhone right after calibration and about
  100 cm by the end.
  * Its clicked calibration had RMS 6.9 px; one point was 18 px off.
  * The dashboard's court-line snap (11 px move, 0.6 px line fit) and later the shared-bounce
    refinement (123 → 62 cm) were proposed but not accepted.
  * Re-projecting its bounces with the snapped calibration: on the A half, 90 cm → 17 cm. The
    remaining 37 cm on the B half is mostly the iPhone's own far-court error, which grows from
    13 cm at 8-12 m to 45 cm at 16-25 m from it.
  * It is not a frame crop mismatch: the Android preview JPEG comes from the analysed buffer.
* **Cameras move during play.** Snapshots were registered against each camera's calibration
  frame:
  * iPhone: 17 px sideways at about 33 minutes.
  * Samsung: a slow tilt of 8-15 px, then a 23-29 px jump at about 43 minutes.
  * Nothing: within 3 px for most of the session.
  * The calibration is never updated, so the error grows over the session.
* **Coverage gap on the right sideline.**
  * Only 34% of the strip 1 m outside the right sideline was seen by 2 or more cameras.
    Baselines: 84%. Left sideline: 100%.
  * The two right-side cameras had that sideline at the edge of their frames. Right-sideline
    OUTs were judged by the iPhone alone, from 9-10 m away and nearly edge-on (about 3 cm per
    pixel; a 17 px shift is tens of cm).
* **Spoken OUTs.**
  * 10 two-camera OUTs. The cameras' own positions agree closely, e.g. 3.42/3.44 m and
    3.78/3.79 m.
  * 12 single-camera OUTs, 11 of them from the iPhone, 0.6-1.9 m out. Three of these had an
    incoming speed of 28-48 m/s (rally bounces: median 7 m/s), which is physically implausible,
    so they are tracking errors.
  * Three "start of play" OUTs fell on the same spot, 1.5 m outside the right sideline where
    players stand between points: ball handling, not play.
* **Load.**
  * The Mac in total was fine: 1.6-1.9 of 4 cores.
  * The iPhone's worker process hit 100% of a core 63 times after calibration, backlogged up to
    3.4 s, when candidates reached the cap (8-12 per frame, 15-25 tracks: sun stripes, shadows,
    players).
  * Frame drops were 0.1%, all during setup.
* **Phones.**
  * iPhone 17 (also the hotspot): "serious" thermal state from minute 25, battery 80% → 30%.
  * Samsung: "fair", 100% → 71%.
  * Nothing: nominal.
  * The Nothing at 30 fps produced 145 reports, against 864 from the iPhone.

**Decision (proposed, not yet built).**
1. Apply the court-line snap automatically when the lines fit well, and refuse to treat a
   calibration over 3 px RMS as ready.
2. Drift tracking: register each snapshot against the calibration frame and re-snap when the
   camera has moved by more than 3 px. This was checked offline on this session.
3. Coverage map in the dashboard, including 1 m outside each line, with a warning when only one
   camera sees outside a line. Aim each camera to include 1-1.5 m beyond its own sideline.
4. Plausibility gates before speaking:
   * incoming speed above about 25 m/s → silent;
   * a single camera viewing a line from beyond about 8 m, nearly edge-on → no single-camera
     OUT;
   * "start of play" bounces far outside the court → silent.
5. Worker backlog: drop stale frames past 0.3 s and tighten the per-frame candidate cap.
6. Network: don't use a camera phone as the hotspot.

**Next.** Build items 1-5 and replay this session to measure the effect. Then score calls with
marked contacts.

---

## Current roadmap (as of 2026-11-21)

**Now: make the full-court calls trustworthy (from field test 3)**
* Auto line snap, drift tracking, a coverage map, plausibility gates for OUT, and a cap on worker
  backlog (entry 24). Replay `data/field/20261121-071625` before and after.

**Then: validate on real courts**
1. Mini-court session with marked contacts (20-30 bounces per line, 1-5 cm in and out). This
   gives accuracy ground truth at the line.
2. Next full-court session with 2 good phones plus weak phones in the empty corners, all at
   1/1000 s. Check:
   * the Samsung changes (detection under 8 ms);
   * the snap calibration and refinement proposals in the dashboard;
   * high balls against the background.
3. Rebuild and reinstall the iOS app on the iPhone 17 (older build without phone-side reduction;
   7-day free signing) and the latest APK.
4. Calibrate every camera with the same side A; confirm the "other end" check on the dashboard.

**Next: accuracy and trust**
* Far-half calibration bias under 10 cm (shared-bounce refinement, more cameras).
* Calibrated uncertainties: covariances currently underestimate errors by about 3x.
* The veto weighted by camera recall.
* Serve and fault calls (FAULT) driven by play state rather than dashboard buttons.

**Later (from the brief)**
* Player tracking, then stats (winners, errors, rallies), then coaching.
* Other racket sports reuse the perception layers.
* Hardware: an Apple silicon Mac as the server. A club installation needs fixed cameras, paid
  app signing and a dedicated network.
