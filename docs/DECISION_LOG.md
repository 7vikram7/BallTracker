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

## 25. Building the field-test-3 fixes; serves; a court screen; can the Mac take another camera? (2026-11-21)

**Request.**
* Build the fixes proposed in entry 24.
* Serves were never recognised: a serve should be called out over the centre line.
* The dashboard should be readable from the corner of the court: the whole screen red for OUT,
  yellow for a service fault, green otherwise.
* How loaded was the server during play, and can this Mac take one more camera?

**Analysis and decisions.**
* **Serves.** In the session, points start the same way: players bounce the ball behind a
  baseline, there is a short pause, then a ball comes over the net and lands deep in the
  diagonal service court.
  * Between points (after a call, a second bounce, ball handling, or 5 s without play, and at
    least 3 s after the last ball in play), a bounce is a serve if the incoming flight is
    clearly over the net (|vy| >= 3 m/s, 3 sd).
  * Traced back along its arc, the ball must be at a plausible contact height at the server's
    baseline (-2 to 3 m; the session's serves were -0.8 to 1.2 m, a kitchen shot -13 m).
  * The server must stand within the sideline extensions (0.5 m tolerance).
  * The ball must not land more than 1 m into the server's own side: serves go cross-court.
  * The server's half comes from where the trace meets the baseline, or from the pre-serve
    bounce. Unknown half: judged against the whole service area (kitchen, baseline and sideline
    faults only).
  * Replaying the session: 76 serves recognised, 7 FAULTs: four just over the centre line
    (32, 22, 20, 5 cm), two long, one wide.
  * In a drill, every feed from the baseline looks like a serve, so there is a Match / Drill
    mode (`bt serve --drill`, dashboard). The synthetic test rally and the live demo are drills.
* **Calibration upkeep** (`live/upkeep.py`, `geometry/drift.py`).
  * A click calibration is snapped to the painted lines automatically when they fit (≤ 1 px,
    ≥ 4 lines, ≤ 30 px move); so are the other cameras after a calibration, and a calibration
    loaded from an earlier session on its first frame.
  * A calibration above 3 px RMS is not used for calls.
  * Drift tracking compares the camera's picture with its calibration frame every 10 s
    (similarity transform on the static background). A move of ≥ 3 px median, seen on two checks
    in a row, is followed (moved points, then line snap); more than 80 px is flagged.
    Re-referencing after each correction let noise pile up (73 corrections in an hour); always
    comparing with the calibration frame gave 24, matching the real moves.
* **Uncertainties made honest.** Every bounce's covariance gains 2 px of calibration
  uncertainty projected to the ground. Without it, cameras 14 cm apart scored chi2 44 and the
  judge silenced them as disagreeing (71% of two-camera bounces). With it, 6%.
* **Gates before speaking.**
  * The ball's speed lower bound (2 sd) above 25 m/s.
  * "Start of play" more than 1 m outside the court (ball handling).
  * One camera alone, more than 8 m away, looking across the line.
* **Replay of the session.**
  * As recorded with the new code: the Samsung (6.9 px) is left out, and only iPhone 17 +
    Nothing call.
  * With the calibration history the new server would have produced (auto snap at each
    calibration and drift tracking on the recorded snapshots), camera agreement is:
    Samsung–iPhone 87 → 14 cm, Samsung–Nothing 164 → 9 cm, iPhone–Nothing 12 → 4 cm.
  * Calls in that replay: 21 OUT and 7 FAULT spoken. The single-camera OUTs on the far right
    sideline are gone. There is still no ground truth.
* **Worker speed.** The bounce search's per-split screening and contact-time search are batched
  (one solve for all splits); the tracker scores candidates per track at once and predicts by
  normal equations. Same bounces on the field data, bit for bit. (The golden rally fixture
  *did* change in this commit, but because of the calibration floor above, not the batching;
  see "Checks after review" below.) Busiest 2 minutes: iPhone
  64 → 33% of a core, Samsung 61 → 19%. Over the whole session, per 5 s (typical / p90 /
  peak): iPhone 0.25 / 0.55 / 0.87 cores (live: 0.46 / 1.00 / saturated 20% of the time),
  Samsung 0.25 / 0.33 / 0.51, Nothing 0.01 / 0.03 / 0.11. A worker more than 0.3 s behind skips
  periodic bounce checks; more than 1.5 s behind, it drops stale frames.
* **One more camera?** Yes. A fourth 120 fps iPhone adds about 0.25 cores typically and 0.55 at
  p90, so all four need about 1.5 cores at p90 of 4. No single camera reaches a whole core.
  Conditions: close heavy apps (the editor), keep the Mac on power, and use a separate hotspot
  phone.
* **Load during play (live).** The Mac as a whole was not overloaded: the camera workers used
  0.9 cores typically and 1.9 at most, of 4 cores / 8 threads. But the iPhone's worker was
  saturated 20% of the time and more than 0.5 s behind 12% of the time. A code editor's window
  used 1.4 cores while idle in the background. The server now logs the Mac's load every 10 s
  (`host_stats`), and the dashboard shows it.
* **Dashboard.**
  * Court screen (button, key B, `?court`): the whole window is green IN / red OUT / yellow
    FAULT (held 6 s), grey when not ready, with camera status at the bottom.
  * Setup view: a status pill, a warnings bar (rough calibration, camera moved, hot phone,
    processing behind, coverage gaps), a last-call tile, a coverage-gaps map, the Mac's load,
    and serve / gate reasons in the calls table.
* **Replay** now follows the calibration history over time (connect-time model, every
  `calibrated` event), leaves out bounces from a camera whose calibration was too rough at the
  time, and applies the match/drill mode.

**Checks after review** (an outside review of the commit raised two points).
* **The golden fixture changed, and the commit said "identical bounces".** Both are true, for
  different reasons. Replaying `tests/golden/edge_rally` on the new code with the calibration
  floor switched off (`calib_sigma_px=0`) reproduces the old `expected.json` exactly, all 8
  decisions and every field: the batching changed nothing. The whole change comes from the
  2 px floor, which is an intended logic change. Positions move by up to 5.5 mm (the two
  cameras are weighted differently), and one call goes IN → UNCERTAIN: the ball at 11.12 s,
  truly 5.8 cm in, estimated 3.1 cm in, p_out 0.023 → 0.098. Silent rather than a confident
  IN, 3 cm from the line: that is the intended behaviour.
* **Is the 5 cm centre-line FAULT inside the noise?** By the model, no: p_out 0.994, σ across
  the line 2.1 cm (2.5 σ, two cameras). Is σ honest? The cameras' independent estimates of the
  same bounce, compared across the line, measure that without ground truth. With the 2 px floor
  the normalised differences across x (centre line and sidelines) have a robust sd of 0.99 for
  Samsung–iPhone (0.80 near the centre line, 91 bounces), 0.73 for iPhone–Nothing and 0.37 for
  Samsung–Nothing: honest, or slightly cautious. Along y (baselines, kitchen) Samsung–iPhone is
  still 1.6 too tight. A 3 px floor fixes y, but every spoken call stays the same (21 OUT,
  7 FAULT) and four more INs go silent, so the floor stays at 2 px. What this cannot see: an
  error shared by both cameras (for example both snapped to the same mis-drawn line). Only
  marked contacts measure that.
* Serve FAULTs are still unchecked against what players saw (see Next).

**Next.** On court: Match mode, Court screen, one phone as a non-filming hotspot. Then check the
FAULT calls against what players saw, and mark contacts on one line for ground truth.

---

## 26. Did the 30 fps Android help? A weak camera's silence weighed by its hit rate (2026-11-21)

**Request.** Did the 30 fps Android help in the last two sessions, and should it stay? Then:
build the veto weighted by camera hit rate (proposed in entry 21). Tomorrow both weak phones
(the Nothing and the Redmi) are used, each aimed at its own end.

**Analysis.**
* Night session (entry 23): the Redmi saw almost nothing in the dark and was never calibrated.
  No contribution.
* Field test 3, the Nothing (720p, 30 fps, behind the A-right corner):
  * It caught 56 of the 318 bounces the iPhone saw inside the court on the A half (18%), and 2 of
    260 on the B half.
  * Re-judged without it (best-calibration replay): it was the second camera for 2 right-sideline
    OUTs that the iPhone alone, 9 m away and looking across that line, could not make. That
    sideline was the session's coverage gap.
  * Its silence counted as a full veto: 46 decisions were marked unconfirmed by it, including a
    two-camera OUT 1.6 m wide (at 4027.5 s), where its hit rate at that distance was 2%.
  * Cost: 0.01 cores of the Mac; the phone stayed cool.
* Hit rates learned during the session, per distance band from the camera (near < 8 m,
  mid 8-14 m, far beyond): iPhone 75 / 75 / 74%, Samsung 77 / 66 / 48%, Nothing 17 / 5 / 0%.
  Even the good cameras catch only 50-77% of the bounces the other cameras report. Part of that
  is real misses, and part is other cameras' false bounces counted as misses.
* Weighting every veto by its hit rate (veto when P(all silent cameras miss a real bounce)
  <= 0.3) was tried first. It unlocked 26 more lone-camera OUTs on the best-calibration replay
  (21 → 47 spoken), because the good cameras' vetoes weakened too. Rejected: a wrong OUT costs
  more than a missed one.

**Decision.**
* `fusion.CameraRecall`: the judge counts, for each camera that could see a bounce spot, whether
  it also reported a bounce that other cameras saw (two others, or one other on a ball in play).
  Kept per distance band, with a prior of 75% worth 5 bounces, so a new camera vetoes as before.
* A silent camera that catches fewer than 40% at that distance no longer vetoes (logged as
  `silent_weak` with its rate); any other silent camera still vetoes (`unconfirmed_by`).
* A camera that reported the bounce counts as seeing it, even at the edge of its modelled view.
  Two cameras that both reported a bounce are never vetoed.
* One camera alone whose flight fit leaves the speed unknown (sd above 25 m/s) is not announced.
  At 2610.9 s a Samsung-only bounce 2 m out read 60 +- 64 m/s, and only the weak camera's veto
  had been stopping it.
* Considered and dropped: silencing every lone-camera "start of play" bounce. "Start of play"
  means no recent bounce is known. That includes a lob after a volley exchange and drill feeds,
  which tests protect on purpose, and the data can't tell those from ball handling.
* The dashboard's camera card shows each camera's hit rate by distance. LIVE_SETUP has a section
  on aiming weak phones at their own end only.

**Effect** (no ground truth):
* Best-calibration replay (the setup tomorrow should give): still 21 OUT and 7 FAULT spoken, with
  one swap. The two-camera OUT at 4027.5 s is now spoken. A lone iPhone OUT at 3596.2 s, at the
  edge of its view 1.7 m behind its baseline, is now silent: the Samsung could see that spot,
  catches about half of the bounces there, and reported nothing.
* Replay as recorded (the Samsung's reports excluded, so the iPhone is the only good camera):
  more lone-camera calls. **Corrected in entry 29:** the "9 → 30" first written here came from a
  mixed run (recorded reports, camera geometry from the counterfactual calibrations). Measured
  with `scripts/replay_counts.py`, as recorded: 9 spoken at defed68 (8 OUT, 1 FAULT), 30 at
  b715f6a (27 OUT, 3 FAULT). The weak Nothing's silence had been holding back iPhone-only OUTs,
  mostly on the left sideline (which the iPhone looks along) and baseline A. **With only one good
  camera, more lone-camera calls are spoken.** That is the same treatment a spot gets when only
  one camera can see it at all.

**Next.** Tomorrow: two good phones well calibrated (the readiness check and auto-snap help),
weak phones at their own ends. Compare the hit rates on the camera cards. Mark contacts on one
line so lone-camera calls can be scored.

---

## 27. An outside review of defed68: what was fixed, what was not, and why (2026-11-21)

**Request.** Another agent reviewed origin/main at defed68 and listed 29 items (P0: can speak a
wrong call or silence a correct one; P1: accuracy and reproducibility; P2: tests and hygiene).
Implement the ones that hold up; answer the others. Each fix starts from a test that failed
before it (against 7d6db25, which already had entry 26).

**Fixed** (`tests/test_judge_review.py` unless noted):
* **A fused OUT one camera itself disputes (TODO-1).** Two cameras within their uncertainties
  could still fuse to OUT while one of them, on its own, favoured IN. The proposed rule (every
  camera must itself call OUT) was measured first. On the field-test-3 replay it silences 7 of 27
  multi-camera calls. In 2 of them the doubtful camera was a coin flip (p_out 0.47, 0.49), and in
  4 its own estimate was also outside, just less certain. Built instead: silent when any camera's
  own p_out is below 1/3 (it favours IN 2:1). That catches the review's example (0.31) and the
  one real case in the session, the 18.6 cm FAULT at 3735.8 s (Samsung 16.5 cm inside, p_out 0.16).
* **Readiness without an RMS (TODO-2).** A model without a measured RMS, or NaN, is not ready.
  An explicit `max_rms_px=inf` still means "don't gate" (old sample sessions).
* **Serve context (TODO-3).** A serve set from the dashboard is used up by the next bounce even
  when that bounce is suppressed; it could otherwise make a later rally ball in the kitchen a FAULT.
* **Second bounce without flight data (TODO-4).** If neither bounce has flight data, a later bounce
  on the same half, further from the net, within the play state's 3 s window is a second bounce.
  The judge's coarse 1.2 s check stays as it is. Widening it to 3 s for every bounce would also
  silence real rally bounces whenever the bounce on the other half was missed.
* **Late reports (TODO-5).** A report arriving after its bounce was decided is dropped and counted
  (`late_reports`), not judged as a second decision.
* **Chi-square limit (TODO-7).** The 99.9% quantile for the actual degrees of freedom (18.5 for
  three cameras, was 27.6).
* **Serve with the server's half unknown (TODO-8c).** FAULT only if the ball is out of the whole
  receiving half (long or wide: out whatever the shot was). In the kitchen it stays UNCERTAIN: it
  may be a rally ball taken for a serve. (This reverses a test from entry 25.)
* **p_out reproducible (TODO-9).** The Monte Carlo generator is seeded from the bounce itself, so
  p_out no longer depends on what was called before.
* **Drift tracking follows pans (TODO-13).** The image motion is a homography, not a similarity:
  exact for any rotation and for the ground plane under any move. With a similarity, a 3 degree
  pan left court corners 9 px off (test in `test_field3.py`). A recalibration from moved points
  rougher than 3 px is not used; the dashboard asks for a new one.
* **Counted instead of silent:** bounces whose calibration floor could not be added
  (`no_calib_floor`, TODO-10) and frames skipped for out-of-order timestamps (`skipped_frames`,
  TODO-15) are in each camera's stats in the session log.
* **Tests (TODO-20):**
  * the lone-camera golden test asserts the announce, and its comment says why it is announced;
  * detector candidates are compared unrounded within exactly the fixture's rounding;
  * the golden guard catches a 1.2 mm change (was 5 mm);
  * the ROI test has a positive control;
  * the browser test's comment matches its 21 fps bar;
  * the speed-gate test asserts what it means;
  * the deferral test checks that the deferred search runs when the track ends;
  * two stale references to a test file that doesn't exist now point to `test_edge.py`.
* **Skips (TODO-21).** `BT_REQUIRE_ALL=1` turns every skip into a failure, including the C++ leg of
  the golden detector test.
* **Base64 (TODO-26).** Characters outside the alphabet are rejected (whitespace is still allowed).
* `refine_with_bounces` documents that its before/after numbers are in-sample (TODO-29).

**Effect on the field-test-3 replay** (best calibration; no ground truth): 21 OUT and 6 FAULT spoken,
was 21 and 7 (the 3735.8 s FAULT above). **Golden fixture:** no call moved; p_out changed at two
bounces, from seeding per call (5.02 s: 0.0135 → 0.0113; 11.12 s: 0.0978 → 0.1088).

**Not done, with reasons:**
* **TODO-6 (veto whenever any camera that could see the spot is silent).** The part that was a gap,
  a reporting camera at the edge of its modelled view not counted as seeing, was fixed in entry 26.
  The rest would let one silent camera overrule two that agree. Even the good cameras catch only
  50-77% of each other's bounces (entry 26), so that would silence most multi-camera calls. The
  expected cameras already survive `flush()` (test added).
* **TODO-8a (z0 lower bound -0.3 m).** Of the 76 recognised serves, the traced height at the
  baseline has median -0.06 m and is below -0.3 m for 29 (38%), including 2 of the FAULTs: the
  trace ignores air drag, so it comes out low. That bound would reject real serves. Kept at -2 m.
  **TODO-8b** (a lob after volleys taken for a serve) was already handled: its trace lands metres
  below the ground (test added).
* **TODO-10/11 (floor scaled by RMS; position covariance scale).** Measured in entry 25 from
  cross-camera residuals: with the 2 px floor, the stated sd matches the disagreement across the
  sidelines and centre line (robust z-sd 0.99, 0.80 near the centre line), and along the court one
  pair is 1.6x too tight. A larger factor did not change any spoken call. The "about 3x" in the
  old roadmap predates the floor. RMS scaling waits for marked contacts.
* **TODO-12 (far-half bias).** Agreed, and it needs field measurement (marked contacts on the far
  half). In field test 3 the Samsung's rough calibration and drift explained most of the
  disagreement on the near half (90 → 17 cm once snapped). The 37 cm left on the far half is the
  part this item is about.
* **TODO-15 (frame clock).** Confirmed: with +-4 ms jitter, 12% of frames are skipped at 240 fps and
  0.5% at 120 fps. A quick fix (grid time on a single glitch) changed nothing, because the skips
  come from re-anchoring when the jitter is as large as the frame period. Frame numbers can't be
  taken from such timestamps at all, which is a design change. The clock is only used for browser
  cameras, which don't reach 240 fps; app cameras use sensor timestamps. Skips are counted now.
* **TODO-14, 16, 17, 18, 19, 27 (replay of load decisions, detector parity on a stopped ball,
  clutter tracks, flush on stalls, per-camera processed coverage, reducer in busy scenes).**
  Agreed as real issues. Each is a design change with its own investigation, so they go on the
  roadmap rather than being rushed before a field session.
* **TODO-22 (native builds in CI).** There is no CI yet. `BT_REQUIRE_ALL=1` is the first step.
* **TODO-23-25 (phone app: capture rate and clock source, Android native errors, an iOS data
  race and buffer hold).** Agreed. They need an app rebuild and reinstall on every phone, so they
  wait until after the next field session. The server already shows each camera's measured
  frame rate.
* **TODO-28.** `build/` is gitignored, so the runtime C++ build doesn't touch the repository. The
  evolution log's publication is the owner's decision and stays as is (entry 26). The `Prompt`
  file and the auto-commit hook are the owner's to keep or drop. Commit messages: entry 25 records
  the 22aef8d mismatch.

---

## 28. Second round on the review of defed68: the larger items and the phone apps (2026-11-21)

**Request.** Implement the items left for later in entry 27 (TODO-12, 14, 16-19, 22, 27) and the
phone app items (TODO-23-25); the owner reinstalls both apps. A point-by-point answer for the
reviewing agent is in `docs/reviews/2026-11-21-response-to-defed68-review.md`.

**Built** (tests: `tests/test_worker_replay.py`, `mobile/test/*.test.js`):
* **Replay reproduces load-dependent decisions (TODO-14).** The worker's batch logic is one
  function (`handle_dets`). Drops, deferrals and silence flushes are logged as `worker_ctl` events
  with frame numbers, and replay applies them at the same frames.
* **Stalls (TODO-18).** Flush after 1 s of silence (was 0.4 s). A bounce cut by a flush less than
  settle_s after it is `unsettled`; an OUT resting only on unsettled reports is silent. The first
  version also marked tracks that ended by themselves. It silenced 2 two-camera OUTs in a session
  with no stalls, so it was narrowed to flushes.
* **Processed coverage (TODO-19).** Gaps (frames > 0.25 s apart, dropped batches) and progress go
  to the server. A camera that hadn't processed a bounce's frames neither vetoes it nor counts as a
  miss.
* **Detector parity (TODO-16).** JPEG cameras run the phone's C++ detector on the Mac: 5.2 ms per
  frame, against 3.6 for MOG2. It keeps a stopped ball 2 s like the phone does (MOG2: 0.22 s).
  Older sessions replay with MOG2. Time-based track ending (`max_miss_s`) is built but off; the
  field-test-3 numbers are in the response file. It reshuffles calls with no way to tell which
  set is better without ground truth.
* **Clutter (TODO-17).** For each bounce, the blob radius divided by the radius a ball would have
  there (`r_ratio`). Field test 3: median 0.9-1.0, largest 2.81. Capped at 3.0, which removes
  shirt-sized clutter (5-6x) and no real bounce; blobs about 2x a ball's size can't be separated
  by size.
* **Reducer (TODO-27).** With all track slots taken, a track too slow for the change detector
  gives its slot to the new candidate.
* **Phone apps (TODO-23-25):**
  * Android checks its timestamp clock and converts if it doesn't match, and reports native
    detector errors;
  * iOS: the battery race is fixed, previews encode from a copied buffer, and a missing session
    clock is flagged;
  * the app sends the real clock source and retunes the detector to the delivered fps (asked 120,
    got 58);
  * the server warns about all three.
* **CI (TODO-22).** `.github/workflows/ci.yml` (GitHub Actions, on every push to main): the full suite with `BT_REQUIRE_ALL=1` on Linux.
  On Apple silicon: the C++ detector built with the podspec and CMake flags, checked for no fused
  multiply-add instructions (with control builds that do show them; the NDK contracts by default),
  the parity tests on arm64, and the wasm built from source and tested.
* **Far-half bias (TODO-12).**
  * The contact geometry is right (ray meets z = ball radius).
  * The detector centre on synthetic small, blurred, top-lit balls is within 0.1 px across and
    0.02-0.3 px high: 0.4-5 cm at the far baseline.
  * So the detector explains centimetres, not the 0.7-1.5 m of field test 2.
  * `scripts/score_marks.py` measures each camera's bias around chalked spots on court.

**Field test 3 replay:** 21 OUT and 6 FAULT, unchanged by this round. **Golden fixture:**
unchanged.

**Also found:** the Samsung and the Nothing joined field test 3 over mobile data, not the iPhone's
hotspot. Clock round trip: 100 and 155 ms, against 5 ms for the hotspot iPhone. The IPv6-only
hotspot gave the Mac a public IPv6 address, which the QR code advertised. It worked, but by luck
of carrier and IPv6, and the server was reachable from the internet. Next session: one
non-filming hotspot phone for everything; every camera's clock round trip under ~20 ms.

**Next.** Reinstall both apps. Next session: chalked target spots for `score_marks.py`; one local
hotspot; watch the camera cards for "asked/delivers" fps and clock warnings. Then decide
`max_miss_s` from the marked contacts.

---

## 29. Review of round 2: reproducible field numbers, a safer clutter check, a strict-veto switch (2026-11-22)

**Request.** The reviewing agent checked f91483f, 4e119db and b715f6a (response:
`docs/reviews/2026-11-22-response-to-round-2-review.md`). Build what holds up; no phone app
changes before the next session.

**Reproducible field numbers.**
* The best-calibration replay is a counterfactual. Its calibration history is now committed:
  `data/field/20261121-071625/counterfactual/calibrations.jsonl`, with a README. It was made by
  `scripts/counterfactual_calibration.py` from local snapshots, which aren't committed.
* `bt replay --calibrations` and `replay(calibrations=)` use it. `--workers` replays the cameras
  in parallel.
* Every field-test-3 figure is now produced by `scripts/replay_counts.py`:
  * counterfactual: 1 212 decisions, 21 OUT and 6 FAULT spoken; reports iPhone 874, Nothing 152,
    Samsung 720;
  * as recorded: 940 decisions, 27 OUT and 3 FAULT spoken; reports iPhone 860, Nothing 152,
    Samsung 0 (calibration too rough).
* Same script at b715f6a: 940 / 30 (27 OUT, 3 FAULT), the same calls one by one. At defed68: 940 / 9.
* Entry 26's "9 → 30" came from a mixed run; it is corrected there.
* **Added after the review of a9fbde6 (entry 33):** these figures are from the owner's Mac (Python
  3.12.13, numpy 2.5.5, scipy 1.18.1, OpenCV 5.0.0, x86_64) and reproduce there at e34bc6e,
  a9fbde6 and later. The reviewer's environment gives one iPhone report fewer with the same code
  and data: 939 / 29 as recorded (iPhone 859), 1 211 counterfactual (iPhone 873). The cause is
  not found; `replay_counts.py` now prints its environment with every count.
* "Every figure is produced by `replay_counts.py`" holds for the replay step. The counterfactual
  calibration history itself was made from local snapshots that show people and aren't committed,
  so it can be replayed but not regenerated.

**Clutter check.**
* The detector adds about 1.5-2 px to every radius. A far ball of 1 px measured 2.6-2.9 px
  (ratio up to 3.5), so the pure ratio cap from entry 28 could silence a real far bounce on a
  low-resolution camera.
* New rule: not a ball if the blob radius > 3 × the ball's radius there + 2 px.
* Real detector measurements of 1-1.5 px balls all pass (test); the shirt-sized blob still fails.
* Field test 3 per camera and distance band (`scripts/ball_size_report.py`): the smallest margin
  to the limit is 2.6 px, a far Samsung bounce.

**Stalls.**
* The worker loop's silence flush is a class (`SilenceFlusher`), tested with a simulated clock.
* A 0.5 s stall after a bounce keeps the track. A 1.2 s stall cuts it, and the cut bounce makes
  no OUT.
* With the old 0.4 s flush the test fails. (It replaces a test that only checked a constant.)

**The weak-camera veto.**
* The owner asked for it on 2026-11-21, so it stays the default.
* Its 40% threshold was chosen on field test 3, so it's unevaluated until the next session.
* `bt serve --strict-veto` restores the old rule (any silent camera vetoes). It's logged in the
  manifest, and replay honours it.

**Verified elsewhere.**
* CI run 44935813595 passed both jobs: Android NDK and iOS flags with 0 fused multiply-add
  instructions (controls: 10), arm64 parity, and the wasm built from source.
* The app builds were checked by hand; the commands are in the response file. App builds are not
  in CI.

**Flaky test.** `test_live_server_end_to_end_edge_phones` is real-time. Failure rate after this
change: 10 of 10 passed on an idle Mac. A deterministic version needs a frame-driven server clock (roadmap).

**Not changed, the owner's decisions:** commit 4e119db's message (a rewrite needs a force push);
the public evolution log and the auto-commit hook.

---

## 30. Field test 4: four phones on a router; calls on every phone, Stop session, faster calls (2026-11-22)

**Session** (`20261122-071401`, 61 min, code e34bc6e + log commit, `bt serve --record`, router, no
internet). iPhone 17 (1080p 120 fps) behind baseline A, left; Samsung S948B (1080p 120) behind
baseline B, right; Nothing (720p 30) behind baseline A, right; Redmi 8A (720p 30) behind baseline B,
centre, 1.6 m high. Cameras calibrated at 13, 18, 25 and 34 minutes: 27 minutes with all four.

**What it called.** 1 121 decisions (393 seen by 2+ cameras), 25 OUT spoken, no FAULT (62 serves
recognised, all landed in). Every two-camera OUT had both cameras saying OUT on their own.
Delay bounce → call: 0.6-0.7 s with one camera, 1.2-1.6 s with two.

**Findings.**
* Router: clock round trips iPhone 9 ms, Samsung 25, Nothing 33, Redmi 59 (field test 3 on
  mobile data: 100-155 ms). The Samsung's bounce times run a steady 14.6 ms ahead of the iPhone's
  (clock offset; within the 80 ms grouping window, no effect on positions).
* Redmi: 0 bounces in 33 minutes. It delivered 19 fps (asked 30), detection took 46 ms a frame,
  0.04 candidates a frame, and its mount moved 25-220 px again and again. Not useful as it is.
* Nothing: 139 reports, catches 10-14% of bounces others saw on its half, none far away.
* Far-half bias: on half B the iPhone (13-17 m away) puts bounces 30-50 cm further from itself
  than the Samsung (near) does; on half A the Samsung (far) differs from the iPhone (near) by
  about 10 cm. Fusion trusts the near camera (±1-3 cm against ±10-20), so two-camera calls follow
  it, but a lone iPhone call near a far line can be wrong: 1010.3 s, sideline right, +16 cm, iPhone
  alone (the Samsung wasn't calibrated yet), where the iPhone reads +15 to +36 cm more out than the
  Samsung on the same line. Likely a wrong OUT. Which camera is biased needs marked contacts.
* Close calls (both cameras OUT but within 5 cm on the near camera): 1371.0 s (+4 cm), 2151.8 s
  (+3 cm), 3389.2 s (+5 cm).
* The two calls before the Samsung's calibration (929.8 s, 974.1 s) were iPhone alone, while the
  Samsung ran on yesterday's saved calibration (not used for calls).
* The session was not closed cleanly: no summary was written (Stop session, below, closes it properly).

**Replay didn't match live: fixed.** `scripts/replay_counts.py` at e34bc6e gave 23 calls; live
spoke 25. Two causes:
* the replay judge used each camera's last calibration for the whole session, so the Samsung's
  final calibration vetoed the two early calls;
* it decided a held bounce at the next report's arrival (sometimes many seconds later, on another
  calibration), not when its wait ran out.
Now it uses the calibration in use and the connection state at the time (sessions logged from
2026-11-21 on; older ones as before) and decides each bounce at its due time. Same reports:
25 calls, identical to live call by call (time, text, line; p(out) differs by up to 0.002 on two:
entry 33). Test:
`test_replay_judges_with_the_calibration_in_use_at_the_time`. (The Samsung gives 619 reports in
replay, 666 live: unexplained, no call affected; roadmap.)

**Faster calls.** The judge waited `hold_s` (0.6 s) for every calibrated camera, so the Redmi,
which never reported, held every two-camera call. Now it doesn't wait for a camera that can't see
the spot, and waits 0.25 s (`weak_wait_s`) for one that catches fewer than `weak_rate` of bounces
there. A late report from such a camera is still dropped (one decision per bounce) but corrects
its hit rate, so a slow camera doesn't drift into "weak" because its reports come late. Same
reports, replay: the 25 calls go out 0.35 s sooner; the calls are the same. `--strict-veto`
keeps the full wait. **Corrected (review of a9fbde6):** the saving applies to two-camera calls,
so live they would come about 0.85-1.25 s after the bounce instead of 1.2-1.6 s (not "about 0.9 s
instead of 1.3 s"). **Changed in entry 33:** skipping a camera that can't see the spot let a lone
wrong report release its bounce early, and added one OUT on field test 3 (3694.55 s); a camera is
now skipped only once two reports agree.

**Every phone says the call.** The server already sent each call to the phones (they flashed it).
Now the app says it ("Out"): iOS AVSpeechSynthesizer (plays with the silent switch on), Android
TextToSpeech (media volume; manifest declares the TTS service for Android 11+). *Say calls out
loud* / *Silent* on the start screen. Browser phones speak it too (speech unlocked by the Start tap).
Old app builds ignore the speech and still flash.

**Stop session.** Dashboard button (with a confirmation): the server sends `session_end` to every
phone and dashboard; app phones stop the camera, go back to the start screen with a notice and
don't reconnect; browser phones stop. After 1 s (last detections) the server shuts down: workers
flushed, last decisions, summary, and now `report.md` written, process exits. Ctrl+C saves the same
but leaves phones retrying (to restart the server with other options).

**Checked.** 139 Python tests, 18 app tests, `tsc` clean (also fixed 5 older type errors). The
Android release APK and the iOS Release build compile.

---

## 31. Why the last minutes went quiet; is the project worth pursuing? (2026-11-22)

**Request.** In the last 10-15 minutes of field test 4 the server seemed silent and missed OUTs:
was it overwhelmed (then add a pipeline reset button)? Why was the Redmi's recalibration ignored?
Are we improving, and is the project worth building? Four good cameras seem a must.

**Analysis** (full study: [STUDY_2026-11-22.md](STUDY_2026-11-22.md)).
* Not overwhelmed: Mac at most 51% busy, no frames deferred or dropped, same bounce and call rates
  as before (8 OUTs spoken in the last 15 minutes).
* What changed: from minute 54 the Samsung caught 53% of the iPhone's rally bounces (62-80%
  before). Its silence vetoed lone OUTs: 7 of the session's 13 vetoed in-rally lone OUTs came in
  the last 7 minutes, 5 of them iPhone OUTs vetoed by the Samsung. The veto rule is right for one
  half-reliable second camera; more good cameras are the fix.
* A reset button wouldn't have helped (the cause was a camera), so it isn't built.
* The 31 two-camera OUTs that play state silenced were servers bouncing the ball before serving
  (about 1 m/s, 1.5 s before the serve): correct.
* Redmi: the recalibration used 5 points at 3.6 px (above the 3 px limit for calls); a later snap
  was never confirmed. It detected no bounces even with a 1.0 px calibration: retire it.
* Progress: the engineering is solved session by session (load, clocks, automatic calibration
  and drift, dead balls). Accuracy has never been measured on a full court.
* Market: PlayReplay and Owl AI call lines on the pro tours in 2026; SwingVision does it from one
  iPhone. The niche left is a low-cost permanent installation, or a base for the analytics.
  (Press reports, listed with links in the study's section 5; not checked independently.)

**Decision.** Continue, as measurement sessions: four good cameras at the corners, firm mounts, a
person logging real calls, chalk marks for the far half. Go/no-go after three such sessions
(targets in the study): a fixed installation, or post-match review instead of live calls.

---

## 32. Why no service FAULT was called in field test 4 (2026-11-22)

**Request.** Not one service fault was called although serve recognition was built (entry 25).
Why? (Also: is the evolution log recording the conversation? Yes: every request and Claude's final
reply to it; very short replies and the work in between are not, the reasoning is in this log.)

**Analysis** (judge replayed on the recorded reports, recording why each candidate was or wasn't a
serve):
* 272 bounces could have been serves (between points, 3 s or more after the last ball in play).
  59 were recognised (62 live). All 59 landed in a service court; 57 of them clearly cross-court,
  2 within the 1 m allowed of the centre line. None landed in the kitchen or out. **Corrected
  (entry 33):** 58 were called IN and 1 UNCERTAIN, not all IN. Reproduce at a9fbde6 with
  `scripts/serve_study.py data/field/20261122-071401` (committed in entry 33).
* No recognised serve landed in a fault zone, so there was no FAULT to call. In field test 3 the
  same code path spoke 3 FAULTs as recorded, 6 with the counterfactual calibrations.
* Long serves were called, but as "OUT": the probable faulty serves at 1520 s, 2433 s and 3370 s
  weren't recognised as serves, were judged as the first ball of a point, and two cameras called
  them OUT. Same outcome for the players, wrong word.
* A serve into the net, the commonest fault, makes no bounce on the other side: nothing to call.
* **Weakness found: no air drag in the trace back to the server.** A serve is recognised if its
  arc, traced back from the landing to the server's baseline, was at a plausible height there
  (-2 to 3 m). The trace ignores drag, and a pickleball loses about half its speed over a court
  length.
  * Recognised serves trace to -0.4 m median, below the ground.
  * 58 candidates were rejected at -2 to -34 m; 47 of them were the first shot after a pause
    landing in a service court.
  * With quadratic drag (k = 0.03 per metre), the recognised serves trace to 0.2-1.7 m, a real
    contact height. 10-20 of the 47 rejected bounces then fall in a plausible range; the others
    are probably balls hit back to the server between points. (These drag figures are an estimate
    from a scratch calculation, not committed; they need re-doing with the drag-aware trace.)
  * So some slower serves were missed. A wrong-court or kitchen serve among them would have been
    judged as a rally ball.

**Proposed, not built.** Trace serves back with drag and tighten the height band to about 0-2 m.
The risk is false FAULTs: a ball hit back to the server between points can look like a serve that
landed in the wrong court. Check on field tests 3 and 4 (recognised serves, any FAULT spoken
between points), then against the logged real calls in the next measured session (a FAULT tap).

---

## 33. Review of a9fbde6: credential lines out of the public log, a lone report can't cut the wait, guarded POSTs (2026-11-22)

**Request.** The reviewing agent checked the field-test-4 push (e34bc6e to a9fbde6) and listed
P0-P3 items. The owner chose, in writing: keep auto-committing the evolution log, with filters;
don't rewrite history; every phone keeps saying the calls; the wait rule is mine to choose from
the tests so far. Response with every item: `docs/reviews/2026-11-22-response-to-a9fbde6-review.md`.

**P0, the public log.** It described where a credential was kept, what it could do and how pushes
were made (no secret value). Now every line that mentions credentials is replaced by a note, when
the log is written and again before each commit (`scripts/hooks/privacy.py`); 53 lines replaced.
Commit subjects are built from file names, never from conversation text. History is not rewritten
(owner).

**A lone report can't cut the wait (field test 3, 3694.55 s).**
* d930a60 stopped waiting for cameras that can't see the spot, judged from the report in hand. A
  lone iPhone report 1.44 m past the right sideline made the other two cameras "unable to see", so
  the bounce was released 4 ms after it arrived and their reports, 4 and 13 ms later and inside
  the court, were dropped as late. One extra OUT was spoken in the counterfactual replay.
* Choice between A (wait for every calibrated camera, 0.35 s slower two-camera calls) and B (skip
  a camera only after two reports agree). B: on field test 3 the skip's only effect was this wrong
  call; on field test 4 the speed-up came from two agreeing cameras not waiting for weak ones,
  which B keeps. A lone or contradicted report now always waits for every calibrated camera, up to
  `hold_s`. This also covers the review's weak-camera probe: a weak camera's agreeing report 0.4 s
  late is waited for, because until it arrives there is only one report.
* Tests (each failed at a9fbde6): the three field-3 reports; the weak camera's late agreement; two
  disagreeing reports wait for every camera. Kept: two agreeing reports still skip a weak camera.
* Calls, same cached reports, `scratchpad` judge runs mirroring `replay()` (headline numbers also by
  `scripts/replay_counts.py`, below):

| Session | e34bc6e | a9fbde6 | now | Calls that moved |
|---|---|---|---|---|
| Field 3, counterfactual | 1 212 / 27 (21 OUT, 6 FAULT) | 1 212 / 28 (22 OUT, 6 FAULT) | 1 212 / 27 (21 OUT, 6 FAULT) | 3694.55 s OUT sideline right, +143.8 cm, iPhone alone, p(out) 1.00 → three cameras, UNCERTAIN, p(out) 0.44, silent |
| Field 3, as recorded | 940 / 30 | 940 / 30 | 940 / 30 | none |
| Field 4 | 1 118 / 23 (old replay timing) | 1 118 / 25 | 1 118 / 25 | none |

* The cost is time on lone calls: replay bounce → decision p50/p90, spoken calls, field 4: one
  camera 0.50/0.50 s at a9fbde6, 0.50/0.85 s now; two cameras 0.50/0.53 s, now 0.50/0.84 s.
* Field 4, replay against live: the same 25 calls (time, text, line); p(out) differs by up to
  0.002 on two (1010.31 s, 2073.99 s). 1 118 decisions in replay, 1 121 live; the Samsung gives
  619 reports in replay, 666 live (still unexplained). Entry 30's "identical call by call" means
  this.

**Second bounce without flight data (review P1-2).** The play state's rule (a later bounce on the
same half, further out, within 3 s, without flight data, is the unreturned ball) applied only when
the earlier bounce also lacked flight data. Now it applies whatever the earlier bounce had. Test:
a 2.0 s second bounce after one with flight data is suppressed; a first bounce 4 s later is still
called. Not changed: the judge's own 1.2 s check; with flight data the play state's trajectory
check tells a return from a second bounce, and a 3 s window there would silence real returns.

**POST routes guarded (review P1-4).** Calibrate, snap, proposal, context, play mode and stop now
need the `X-BallTracker` header, and a browser Origin other than the server's own is refused
(403). A web page elsewhere can't send the header without a preflight the server never grants. A
device on the network that crafts its own requests still can: a per-session secret shown on the
dashboard would close that (not built). Test: every POST route without the header, or from
another origin, is refused and the session keeps running.

**Ball-size check margin (review P1-5).** From committed code (`scripts/ball_size_report.py`,
output below): field 3 counterfactual, largest ratio per camera iPhone 2.26,
Nothing 2.21, Samsung 2.81; smallest margin to the limit 4.3, 5.6 and 2.6 px. With the 2 px slack
the effective ratio limit at those ball sizes is 3.3-3.7. With the check switched off, the same
session gives the same reports from every camera (874, 152, 720) and the same 27 calls: on field
test 3 it removes no bounce at all, so no change to the cap or the slack.
Test: a 1.2 px ball at the far baseline of a 640×360 camera, measured 2.5 px too large (ratio
3.0), keeps its bounce, and with a near camera's report the call is OUT.

**Field-test-4 data in the repo (review P1-6).** `data/field/20261122-071401` (39 MB: detections of
every frame, events, calibrations; no images; names scrubbed; the Mac's process names dropped from
`host_stats`), exported by `scripts/export_for_repo.py --session`. Replay reads the compressed
`events.jsonl.gz`. Entry 32's serve counts are now reproduced by `scripts/serve_study.py`: 272
candidates, 59 serves at a9fbde6 (58 IN, 1 UNCERTAIN: entry 32 said all IN); 273 and 60 now (the
second-bounce change moves one point boundary). Its drag estimates came from a scratch calculation
and are marked so.

**Field-3 figures (review P1-7).** They reproduce on the owner's Mac (940 / 30 as recorded, 1 212
counterfactual, at e34bc6e, a9fbde6 and now); the reviewer's environment gives one iPhone report
fewer (939 / 29, 1 211). Cause not found; `replay_counts.py` prints the environment line now.

**Smaller items.**
* A late report credits the released bounce it was counted missing from, not just the first one in
  the window (test with two released bounces). The credit corrects the hit rate only; a call
  already made stays.
* `can_see` with a calibration 15 cm off at the court centre (30 cm on the far half): the answer
  changes only within 0.4 m of the edge of the camera's view, 0.4% of the area (test). There the
  camera's silence neither waits nor vetoes.
* Android speech runs on the main thread, shuts a failed engine down, logs a missing voice. iOS
  reactivates the audio session for every call (after a phone call or Siri) and releases it after.
  Both compile (Release); neither has run on a device since.
* Flaky end-to-end test (`test_live_server_end_to_end_edge_phones`): 10 of 10 passed in a row on
  an idle Mac (about 70 s each), and it passed in a full run under load. Still real-time; a
  frame-driven server clock stays on the roadmap.
* Market claims (entry 31, study section 5) now list their sources; the club price, which only an
  aggregator gave, is cut.

**Headline numbers, committed tools at 4c44c4a** (environment line as printed: python 3.12.13
numpy 2.5.5 scipy 1.18.1 opencv 5.0.0 x86_64 Darwin 25.6.0). The calls are identical (time, text,
line, p(out)) to the cached-report runs in the table above.

```
.venv/bin/python scripts/replay_counts.py data/field/20261121-071625 --calibrations data/field/20261121-071625/counterfactual/calibrations.jsonl
decisions 1212  spoken 27 {'FAULT': 6, 'OUT': 21}  reports {iphone17: 874, nothing: 152, samsung: 720}
.venv/bin/python scripts/replay_counts.py data/field/20261121-071625
decisions 940  spoken 30 {'OUT': 27, 'FAULT': 3}  reports {iphone17: 860, nothing: 152, samsung: 0}
.venv/bin/python scripts/replay_counts.py data/field/20261122-071401 --workers 4
decisions 1118  spoken 25 {'OUT': 25}  reports {iphone17: 773, nothing: 139, redmi: 0, samsung: 619}
.venv/bin/python scripts/ball_size_report.py data/field/20261121-071625 --calibrations data/field/20261121-071625/counterfactual/calibrations.jsonl
camera     band m     n median  p99.5   max  ball px min margin px
iphone17   14-99    294   0.94   1.97  2.26      3.3           4.3
nothing     8-14     57   0.85   2.20  2.21      4.0           5.6
samsung    14-99    218   0.89   1.80  2.81      3.4           2.6   (the smallest margin per camera)
.venv/bin/python scripts/serve_study.py data/field/20261122-071401
serve candidates 273, recognised serves 60 (59 IN, 1 UNCERTAIN); at a9fbde6: 272 and 59
```

**Checked.** Python tests: 133 at e34bc6e, 139 at a9fbde6, 156 now. App tests 18 of 18; `tsc`
(TypeScript 6.0.3) clean. Android `./gradlew --offline :app:assembleRelease` and iOS `xcodebuild
... -configuration Release -sdk iphoneos CODE_SIGNING_ALLOWED=NO build` succeed. CI run 45045310997
(b36f9e1): both jobs passed; the native-flags job found the NDK on macos-latest, 0 fused
multiply-adds with the app flags (10 without) for iOS and Android.

---

## 34. Field test 5: the cameras kept moving; a moved camera is out of the calls (2026-11-26)

**Request.** Analyse yesterday's session in detail and learn from it. The cameras kept moving;
a sturdy mount is needed that fits horizontal and vertical bars of various widths.

**Session** (`20261125-194731`, 73 min, code 3e96b4f, `bt serve --record`, indoor hall with a steel
frame). iPhone 17 (1080p, 120 fps), Samsung S948B (1080p, asked 120, delivered 30-60), iPhone 15 Pro
(1080p, 120, joined at minute 25). All app phones. 1 321 decisions (405 seen by 2+ cameras), 29
spoken (26 OUT, 3 FAULT), 68 serves recognised; bounce → call median 1.27 s.

**How the cameras moved** (`scripts/camera_motion.py`: every 2 s snapshot registered against the
frame of the last hand calibration, 150+ background matches required, 5-snapshot median; output in
`data/field/20261125-194731/motion/`).
* Samsung: tilted down slowly (5 px after 5 min, 7 after 10, 17 after 20), then dropped 73 px at
  minute 27; 4° of tilt in all. A friction joint giving way under the phone's weight.
* iPhone 15 Pro: turned sideways in steps (45, 200, 238 px), 8° of pan at the end. Clamp or holder
  turning around the bar when touched.
* iPhone 17: 14 px after 54 min, followed by 13 automatic corrections.
At 1080p 1° is about 23 px; at the far baseline 1° of tilt moves a bounce 1-3 m.

**What it did to the calls** (two cameras' reports of the same bounce, within 80 ms, live log):
* Samsung vs iPhone 17: 9-20 cm until the drop, 150-162 cm after it (the drift check flagged
  "moved 122.9 px: recalibrate" and kept using the old calibration).
* iPhone 15 Pro vs iPhone 17: 2.2-2.3 m for its last 35 minutes (flagged at "moved 101 px").
* 21 OUTs were spoken in the first 27 minutes, 8 in the last 46; 4 of those 8 involved a moved
  camera, 2 of them that camera alone (2587 s, 3844 s: 289 and 169 cm out).
* **The iPhone 17 called for 15 minutes on the wrong calibration.** It connected at minute 2 with a
  calibration saved in an earlier session that put it at the other end of the court (3-14 m off)
  and was calibrated by hand only at minute 17. The drift check said it couldn't match the
  calibration frame (a person was standing in front of it when the reference was taken) but the
  calibration stayed in use: all 9 of its lone OUTs in that window (627-1053 s) came from it.
* Not a problem: 300 of the 500 UNCERTAIN were bounces 1-2.5 m out at "start of play" (balls
  knocked about between points), silent by design.
* Phones: the Samsung started at 28% battery and died at minute 47; it was "critical" hot from
  minute 25 and fell from 57 to 30 fps. Both iPhones held 120 fps capture ("serious" heat).

**Changes.**
1. **A moved camera is out of the calls** (`server._suspend_if_moved`): drift status "big", or 3
   checks in a row (~30 s) without a match, takes the camera out of the judging and the expected
   cameras until it is recalibrated, followed, or back where it was. Logged as `camera_suspended` /
   `camera_resumed`; the dashboard says "not used for calls. Recalibrate, or put it back."; the
   replay follows the log (`replay.suspended_intervals`).
2. **A saved calibration must be confirmed by the lines** (`server._drift_loop`, `upkeep.auto_snap`
   with `min_move_px=0`): a calibration from an earlier session is used only once the court lines
   confirm it; the snap is retried at every check.
3. **Big moves the lines confirm are followed** (`drift.DriftTracker`): a change of more than 80 px
   is followed if the background matches well (150+ inliers) and the line snap lands within 10 px
   of the moved points; otherwise "big" (and change 1 applies).
4. Tools: `scripts/camera_motion.py`; `counterfactual_calibration.py --live-clicks` (re-runs only
   the drift checks on live's own calibrations), `--no-scrub`, and the new rules; `load_session`
   refuses a calibration history that names cameras the session doesn't have (a scrubbed file
   replayed against the local session was silently ignored: it cost me two wrong runs).

**Replayed** (counterfactual `--live-clicks` with the new rules, then replay; against the same tool
with the old drift behaviour as a control, so tool differences cancel):

| | live | control (old rules) | new rules |
|---|---|---|---|
| spoken calls | 29 | 28 | 26 |
| iPhone 15 Pro vs iPhone 17 after minute 40 | 2.2-2.3 m | 2.4-2.5 m | camera out of the calls |
| Samsung vs iPhone 17, minutes 30-47 | 150-162 cm | 36-40 cm | 38-40 cm |

* Gone with the new rules: the 9 iPhone 17 OUTs on the other-end calibration (it is out of the
  calls from minute 2 to its calibration at minute 17), and the 2 lone OUTs of the turned iPhone 15
  Pro. Added: 13 calls, mostly lone iPhone 17 OUTs in the second half that the miscalibrated iPhone
  15 Pro used to veto. Whether they are right is unknown (no ground truth).
* The Samsung's numbers move with the tool, not with the change (control = new): the
  counterfactual takes its drift reference from a different frame than live did, and followed the
  drop. So the Samsung row doesn't show what the new rules do live.
* The iPhone 15 Pro's 146 px turn was followed (lines confirmed); its 300 px turn was not and the
  camera stayed out for the last 32 minutes. In an earlier counterfactual run (re-snapped clicks)
  the same turn was confirmed and the camera agreed with the iPhone 17 to 5-10 cm. Following big
  moves helps sometimes; taking the camera out is what makes it safe.
* Outputs (scrubbed): `data/field/20261125-194731/counterfactual_calibrations.jsonl`.

**Mounts** ([MOUNTS.md](MOUNTS.md)). The two failures need different fixes: no friction joint
that sags (big ball head, or pan-tilt with separate locks, phone centred over it, a second lock
after aiming) and no clamp that turns on a round bar (V contact, screw-tightened, two clamps 10 cm
apart). Two kits that share the head and phone clamp: a super clamp for bars of 13-55 mm, and a
V-block of aluminium angle with two hose clamps or ratchet straps for posts of 40-150 mm, either
orientation. Mount high on vertical posts, away from netting and swings; mark the spot; a wiggle
test before play; cables tied down; battery packs.

**Checked.** New tests: a confirmed 6° turn is followed (median error < 1.5 px); a camera that
moved is out until recalibrated, out after 30 s without a match, back when steady, and the log
gives the replay the same intervals; a saved calibration is confirmed only where it fits; the
replay refuses a mismatched calibration history (fails without the guard). 160 Python tests pass.

---

## Current roadmap (as of 2026-11-26)

**Now (from field test 5, entry 34)**
* Mounts that don't sag or turn ([MOUNTS.md](MOUNTS.md)): build kit B (V-block) for the posts, a
  super clamp kit for thin bars; wiggle test before play. Check the next session's motion with
  `scripts/camera_motion.py`: under 5 px between drift corrections, no steps.
* A spoken or vibrating alert on the phones when a camera is taken out of the calls, so it is
  recalibrated during play (the dashboard alone isn't watched).
* Battery packs on every phone; the server warns below 30% at the start.

**Now (from field test 4, entries 30-31; see STUDY_2026-11-22.md)**
* Measure every session: a person taps the real calls (logger to build), plus 10 chalk marks
  near the far lines. Go/no-go after three measured sessions with four good cameras.
* Four good cameras at the corners (iPhone 17, Samsung, iPhone 16, one more good phone), firm
  mounts on marked spots, battery packs.
* Install the new apps (calls spoken on every phone, Stop session); end sessions with Stop session.
* Retire the Redmi (no bounces even when well calibrated); the Nothing only as a spare.
* Find which camera is biased on the far half: chalk 10 marks just inside / outside the far
  baseline and sideline, bounce on each, compare (`scripts/score_marks.py`).
* Why the Samsung gives 7% fewer reports in replay than live, and why another environment gives
  one iPhone report fewer on field test 3 (entry 33).
* Check on a device: calls spoken on Android and iOS, also after a phone call or Siri (entry 33).
* Drag-aware serve trace (entry 32), checked on field tests 3 and 4 for false FAULTs.
* If the network isn't trusted: a per-session secret on the dashboard for the POST routes (entry 33).

**Then: confirm on court (entries 24-25 are built)**
* Next session in Match mode with the Court screen: check the serve FAULT calls against what the
  players saw; watch the coverage map when placing cameras (1-1.5 m beyond each sideline).
* Ground truth: mark contacts on one line (chalk drill) during the session.

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
* From the reviews (entries 27-29): frame numbering for jittery timestamps (browser cameras);
  time-based track ending (built, off) and the weak-camera threshold, to be evaluated on the next
  session; the camera model switch in replay by frame number; a frame-driven server clock for a
  deterministic end-to-end test; app builds in CI.
* Far-half calibration bias under 10 cm (shared-bounce refinement, more cameras).
* Calibrated uncertainties: with the 2 px floor they match the cameras' disagreement across the
  sidelines and centre line; along the court one camera pair is still 1.6x too tight. Errors
  shared by all cameras are unmeasured until there is ground truth.
* Score lone-camera calls against marked contacts (entry 26 lets more of them speak when only one
  good camera covers a spot).
* Serve FAULTs (built in entry 25, from play state): validate against what players saw.

**Later (from the brief)**
* Player tracking, then stats (winners, errors, rallies), then coaching.
* Other racket sports reuse the perception layers.
* Hardware: an Apple silicon Mac as the server. A club installation needs fixed cameras, paid
  app signing and a dedicated network.
