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

### 2026-11-19 20:42 · outcome

Everything is done, tested (all 83 tests pass) and pushed to https://github.com/7vikram7/BallTracker.

## Git setup
- **Clone:** the GitHub repo was empty, so I connected your existing folder to it and pushed, rather than cloning into a new folder. The result is the same, and the history is kept.
- **Commit name:** commits are by `vikramgore2007`. The repo is public, so I used the repo owner's GitHub no-reply address instead of your gmail, which would otherwise be published. Tell me if you want a different address.
- **Personal names:** before the first push I rewrote the 3 local commits. A test camera named after a person is now called `samsung`.
- **Secrets:** your token is in the macOS keychain, and `Secrets` is excluded from git.

## Commit and push after passing tests
I didn't run the 7-minute suite inside the hook after every response; it would be too slow. Instead:
- A full test run that passes records a fingerprint of exactly the files that were tested.
- At the end of each of my responses, a hook commits and pushes if nothing has changed since that passing run.
- Untested changes wait for the next passing run.
- Files that look like credentials, and anything over 5 MB, are refused.
- I tested it end to end on a throwaway copy. `BT_AUTOCOMMIT=0` turns it off.

## Auto-calibration: tap 4 corners, then "Snap to lines"
In the calibration dialog, click the 4 corners of the half nearest the camera (roughly is fine) and press **Snap to lines**. Every point is placed on the painted lines for you to check, then you save as before.
- On both field-test frames, starting from taps 25 px off, the snapped lines matched the paint to within 1.1 px.
- Zoomed in, the snapped corners sit on the paint, while your original clicks were 8–10 px off.
- Fully automatic detection with no taps still fails on that venue (neighbouring courts and nets), so it stays experimental.

## Refining the other cameras after one is confirmed
When you save a camera:
- **Re-check:** every other camera is re-snapped to its own lines.
- **Shared bounces:** during play, bounces seen by both the saved camera and another camera become reference points for the other camera.

Better calibrations appear on the camera card as **Refined calibration ready**, with Review and Dismiss buttons. Nothing changes without you.

This found a real problem in your field-test data. The iPhone and the Samsung agreed within 6–18 cm on the Samsung's half, but on the far half the Samsung put every bounce 0.7–1.5 m closer to the net. Refining the Samsung from about 15 shared bounces cut that to 21–49 cm, measured on bounces it wasn't fitted to. A low camera measures its far half poorly; cameras at both ends cover each other.

## Lobs
I simulated 54 shots (drives and three heights of lob) with 4 cameras and ran them through the whole pipeline. The full write-up is in `docs/LOB_STUDY.md`.
- **Finding and placing bounces was fine:** every lob bounce was found, about 1 cm median error.
- **Calling them was broken.** One camera measures sideways motion precisely but motion toward or away from it badly (errors of several m/s). That made cameras throw out real lob bounces, and made the play state label lobs "dead ball" or "not clearly a shot".
- **Fixes:**
  - each camera's measurement now carries its uncertainty;
  - the cameras are combined using it;
  - a fast steep descent now counts as a real shot;
  - the rally window stretches for balls that stay in the air longer.
- **Result:** OUT lobs announced went from 11 to 19 of 21, with no wrong OUT calls before or after. The 2 still silent are only 3 cm out, below the confidence bar on purpose.
- **Not tested:** the simulation doesn't show whether the phones can see the ball against the sky or roof lights. Toss a few high balls at the next session.

## Mini court
Yes, sessions there would help, and `bt serve --court-scale 0.2` is ready. The most valuable test is 20–30 bounces near each line with the contact points marked, which gives accuracy ground truth we don't have. It's also a good place to test snap calibration on tape, high balls, and the Samsung's speed and heat. It can't show real ball speeds or distances. `docs/MINI_COURT.md` has dimensions for each scale and what to send back.

## Still to do
- Rebuild the iPhone app and reinstall it, and install the latest APK on the Android phones.
- Snap and the refinement proposals work in tests but haven't been tried on a real phone through the dashboard yet.

## 2026-11-20 13:15 · request (session 1661f7c3)

> Have you pushed on the repo all of the logs, conversations logs, test data, motivation, I want the other repository and other agent to be able to truly work on this data, crunch it, test it so that it can give you tangible suggestions for improvement. Before that, I don't remember you answering my question if a few let's say a couple of  weaker 30 FPS weaker Android camera placed on the court will help

### 2026-11-20 13:43 · outcome

Before your session ended, nothing beyond code, docs and a 60-second data sample had been pushed. The rest is now on GitHub (commit `66cf4f1`, all 84 tests pass), except camera images and video, which I held back.

## Your earlier question: do weak 30 fps Android phones help?

I hadn't answered it, sorry. **Yes, as extra cameras alongside the iPhone and Samsung. No, as a replacement for one of them.** I ran the same 54 drive-and-lob shots in the simulator with different camera setups. The weak phones were modelled as 1280×720 at 30 fps, with blur, more missed frames and uneven timing; those values are guesses, not measurements.

| Setup | OUTs announced (of 27) | Of those, only 3 cm out (of 8) | Wrong OUTs |
|---|---|---|---|
| iPhone + Samsung (today) | 20 | 1 | 0 |
| **+ 2 decent weak phones** | **24** | **5** | 0 |
| + 2 poor weak phones | 22 | 3 | 0 |
| iPhone + 2 weak phones (no Samsung) | 15 | 0 | 0 |

- **Where they help:** the two good phones already call every clear OUT. What extra cameras add is confidence on very close bounces, which the system otherwise keeps silent about.
- **Where they don't:** a weak phone catches only 30–40 of 54 bounces, because 30 fps gives too few points around the contact.
  - If one of them replaces the Samsung, calls are lost.
  - Worse, when a camera can see the spot but misses the bounce, it can silence a correct OUT from the good phone. That happened 3 times in the simulation.
  - I've written this up as a suggested fix but haven't implemented it.
- **They must really reach 30 fps.** In field test 2 the Redmi managed only 12 fps. Use good light and put them in the two empty corners.

Details are in `docs/CAMERA_RIGS.md`.

## What's on GitHub now
- **Field data:** every real session that recorded anything is in `data/field/`. It includes every frame's ball detections, all events and calibrations, and the 605 live decisions from field test 2. `bt replay data/field/20261119-070916` re-runs the whole system on it.
- **Conversations:** the full history of your requests and my replies is in `docs/conversations/`. Tool output and my internal reasoning are left out.
  - Personal details are replaced: your email, the person's name in a camera name, and the iPhone's hardware IDs.
  - Still in there, in your own words: the second iPhone, home Wi-Fi addresses, and the Apple team ID, which was already public in the app config.
- **Motivation and a guide for other agents:**
  - `docs/PROJECT_BRIEF.md` is your original brief; it had never been committed.
  - `docs/HANDOFF.md` is where another agent should start: goals, rules (zero wrong OUTs, no GPL, privacy), what each dataset is, how to run things, 6 open problems with measurable targets, and how to propose a change with before/after numbers.
- **Simulation results:** per-bounce reports from the lob study and the camera-setup study.
- **Refreshing it:** run `scripts/export_for_repo.py` after future sessions. It stops if it finds an email address, token or personal name.

## What I didn't push, and need your decision on
- **Camera images (1.7 GB) and the 240 fps Slo-mo video (900 MB).** People are visible in them and the repo is public.
  - The images are needed for detector work and fully automatic calibration.
  - A private repo or a private download link would work if you want to share them.
- **The raw conversation transcripts:** they contain your email and other personal details. The cleaned copy is the one on GitHub.

I checked the transcripts and the git history against your actual GitHub token: it appears in neither.

A full replay of field test 2 from the uploaded files is still running in the background. A test already confirms that the compressed files replay with identical results.

### 2026-11-20 14:12 · outcome

I found and fixed a bug while checking the uploaded data, and pushed the fix (commit `56b45c7`, all 87 tests pass, golden tests unchanged).

**What was wrong:** I replayed the whole hour of field test 2 from the files now on GitHub, and some of the bounce maths produced negative uncertainties. When the cameras' ball-speed estimates were combined, an affected camera got *negative* weight, which could push the combined speed the wrong way. That speed decides whether a bounce counts as "in play" or a "dead ball". The 60-second sample and the simulations never hit this; only the full real session did. A broken value now gives that camera zero weight instead, and I added tests for it.

**Also fixed:** `scripts/slice_session.py` can now cut short pieces out of the compressed sessions, which is useful because a full replay takes about 30 minutes on your Mac.

**Note for anyone using field test 2:** a replay makes about 1,060 decisions, while the live run made 605. That's because the Mac dropped about 19,000 frames during the session (fixed since), and a replay processes every frame. This is now explained in `docs/HANDOFF.md`, so another agent compares replays before and after a change, not replays against the live run.

A second full replay with the fix is still running. When it finishes I'll tell you how many of the field-test decisions it changed.

### 2026-11-20 14:34 · outcome

The second replay of field test 2 finished, and the fix doesn't change any calls you'd hear: 25 spoken OUTs before and after.

- **The error is gone:** no negative-uncertainty warnings in the hour-long replay. The first run had them.
- **What changed (17 of about 1,060 decisions, all silent ones):**
  - 9 bounces got a different label, such as "start of play" becoming "not clearly a shot", mostly moving toward the more cautious label.
  - 5 switched between IN and UNCERTAIN.
  - 3 bounces dropped out and 2 new ones appeared.

Everything is pushed and nothing is pending. Another agent can now replay this session itself and compare before and after its own changes.

## 2026-11-20 15:39 · request (session 1661f7c3)

> Hey, I certainly don't think it's right to push. Entire GBs of video and conversation transcripts that contain email and personal details. But what I wanted you to push was a decision log, okay? The request was this, the analysis was this, the decision was this, this is future roadmap, the next request was this, the decision was this, the analysis was this, this is the future roadmap. This kind of a conversation and decision log without personal details that needs to be on GitHub for anybody to understand the motivation and direction. About test data, I'm not expecting you to push the entire video, but you can certainly push a metadata out of that video that anybody can leverage to run the tests.

### 2026-11-20 16:04 · outcome

Done and pushed (commit `c1fca1f`, all 90 tests pass). You were right: transcripts and raw media don't belong in a public repo. I've swapped them for these:

**Decision log** (`docs/DECISION_LOG.md`)
- 21 entries, one per request from the first brief to today. Each has the request, the analysis, the decision, and what came next.
- It ends with the current roadmap: what to validate now, what improves accuracy next, and what comes later.
- No personal details. `docs/HANDOFF.md` and the README now send readers there first.
- `docs/conversations/` is deleted from the current version of the repo.

**Test data from the videos** (`data/real/2026-11-17/clip_240fps/`)
- The 240 fps original (600 MB, the only real footage with chalk-mark ground truth) is now 470 KB of data. For every frame: the timestamp, plus the ball positions found by both the Mac detector and the phone detector. No images.
- A new test reruns the whole validation from that data: both detectors find all 12 throws, with a 0.6 cm median error against the chalk marks.
- `scripts/extract_clip_metadata.py` does the same for any future video.
- The field sessions already in the repo (`data/field/`) follow the same idea: ball positions and events only.

**Personal details in the auto-written evolution log**
- The hook was copying requests and replies verbatim, including a mention of your wife's phone and your home folder path. Both the hook and the session export now remove personal details before writing, and I cleaned the existing log.
- The export script I pushed earlier had your name written into its own code. Names now live only in a local file excluded from git.

**One decision for you:** the earlier commits are still in the repo's history. They contain the conversation export, the old log text, and the name in the export script. Anyone can browse old commits on a public repo. I can rewrite the history to remove them all and force-push it. That replaces all of the repo's history on GitHub and can't be undone, so I haven't done it without your OK. Copies GitHub caches or that someone has already downloaded can't be fully recalled. Should I go ahead?

### 2026-11-20 17:18 · outcome

I rewrote the repo's history and force-pushed it. None of the earlier commits contain the personal details any more.

**What was removed from every commit**
- The `docs/conversations/` transcripts.
- Your name, which was written in the old export script.
- The personal phrases in early versions of the evolution log, including the line about your wife's phone.
- A home-folder path in one sample session file.
- I also ran the commit messages through the same scrubber. None needed changes.

**Checks**
- A scan of all 12 rewritten commits finds nothing private. No commit touches `docs/conversations` any more.
- The current files are identical to before, apart from that one sample path.
- The fast test set passed (79 tests). I skipped the 11 slow tests because only that path string changed.
- GitHub now shows the new history. There are no forks or pull requests that could still hold the old commits.
- I added entry 22 to the decision log recording this, and pushed it as `5942d70`.

**What you should know**
- **GitHub can still open old commits by their exact ID.** For example, the old `66cf4f1` still opens if someone has that ID. Nothing on the repo links to it, and GitHub's routine cleanup will eventually delete it. To remove it now, ask GitHub Support to clear the cached views for 7vikram7/BallTracker. Only you can file that request.
- **Commit IDs have all changed.** Anyone or any agent with an older clone should clone again rather than pull.
- **I kept a full backup of the old history** at `.git/pre-rewrite-backup.bundle`, inside the repo's git folder, so it never gets committed. It still contains the private content, so delete it once you're happy with the rewrite.

## 2026-11-20 20:29 · request (session 1661f7c3)

> <ide_selection>The user selected the lines 91 to 91 from ~/Vikram/BallTracker/docs/LIVE_SETUP.md:
> bt serve --court-scale 0.2
> 
> This may or may not be related to the current task.</ide_selection>
> install the app on the connected iphone16

### 2026-11-20 20:32 · outcome

The build is running in the background; I'll pick it up once it finishes. Meanwhile, turn on Developer Mode on the iPhone 16:

1. Open **Settings › Privacy & Security**, scroll to the bottom and open **Developer Mode**.
2. Turn it on and let the phone restart.
3. After it restarts, tap **Turn On** and enter the passcode.

If Developer Mode isn't in that menu, it will appear once the build tries to install. Reopen Settings then.

### 2026-11-20 20:34 · outcome

The app isn't on the iPhone 16 yet. The build stopped right away because Xcode won't build for a phone until Developer Mode is turned on, and it's still off. The phone itself is now paired with this Mac.

To turn it on, on the iPhone 16:
1. Go to **Settings › Privacy & Security › Developer Mode** (at the bottom of the list).
2. Turn it on and let the phone restart.
3. After the restart, tap **Turn On** and enter the passcode.

I'm checking the phone every 5 seconds for the next 30 minutes. As soon as Developer Mode is on, I'll rebuild and install. Keep the phone unlocked and on the cable.

After it installs, the phone may need to trust your developer certificate once. You do that under **Settings › General › VPN & Device Management**. I'll tell you if it does.

### 2026-11-20 20:41 · outcome

The app is installed on the iPhone 16 (BallTracker Cam 0.1.0). iOS won't open it until the phone trusts your developer certificate. That's a one-time step:

1. On the iPhone 16, open **Settings › General › VPN & Device Management**.
2. Under Developer App, tap your Apple ID.
3. Tap **Trust** and confirm.

Then open **BallTracker Cam** from the home screen. The first time, it asks for camera and local-network access; allow both.

Three more things to know:
- **Rebuild every 7 days.** With a free Apple ID, this phone's copy stops opening after 7 days, just like the iPhone 17's.
- **I had to change the build method.** The usual `npx expo run:ios` command failed because the signing profile only listed the iPhone 17. Building with Xcode directly let it add the iPhone 16 automatically. Future reinstalls on either phone can use `npx expo run:ios --device` again.
- **The phone's name is in the build log.** The phone is still called "Vishakha's iPhone", and that name appears in the local build output. Nothing from this went into the repo.

## 2026-11-20 21:00 · request (session 1661f7c3)

> Just finished a session with iPhone 16 and iPhone 17. At night, under limited lights, only two cameras used, my spare Redmi, I tried using it but it was completely not able to see anything, hence I did not calibrate it. Also a question about calibration. Always I should start with the closest left corner and the A is the A for that camera, right? Or I should remember how the first camera was calibrated, what side was A for that camera and then according to that calibrate the other camera. Try to analyze the session I just completed and see if there are any learnings and findings. See if our optimizations worked and the server was not overloaded.

### 2026-11-20 22:13 · outcome

**Calibration:** side A is one fixed end of the court, the same for every camera. Don't make A each camera's own nearest end.

- Pick A once per session, for example the end nearest the Mac, or mark it with a towel.
- A camera at the other end clicks its nearest corners as **B** points.
- Left and right are always as seen standing behind A. So from the B end, "B-left" is on your right.

That's what went wrong tonight. Each phone was calibrated with its own end as A, so the iPhone 16 put every bounce at the spot mirrored through the court centre. The two cameras disagreed by up to 2.5 m, and the judge rightly refused to call: 33 UNCERTAIN, 1 OUT. After swapping the iPhone 16's labels in a replay, the two phones agree within about 2 cm on every shared bounce.

## Did the optimisations work? Yes, the server was not overloaded

| | iPhone 17 | iPhone 16 |
|---|---|---|
| Frame rate | steady 120 fps | 120 fps captured |
| Frames dropped | 0 | 0 |
| Mac load / latency | ~12% busy, 8 ms median | ~0%, 1 ms median |
| Data sent | 3.8 Mbit/s | **5 kbit/s** |

- **The phone-side data reduction works.** The iPhone 16 skipped about half its frames because nothing moved in them, and sent almost nothing. The last field test dropped 19 000 frames; this one dropped none.
- **The iPhone 17 still has an old build of the app** without the reduction. It also finished at **5% battery**, and both phones reached "serious" heat level.
- **The Redmi in the dark** managed only 10–30 fps and found almost no ball candidates, which matches what you saw.

## Bugs this session exposed, now fixed

1. **The mini-court size was applied twice.** The line judge used the correct 1.2 × 2.7 m court. But each camera's processing used a court 5× smaller than that, and so did replays.
2. **The ball search area didn't shrink with the mini court.** It was the court plus a full-court-size margin, which took in lights and people. Shrinking it raises the bounces both cameras catch from 4 to 20 in a replay.
3. **Two disagreeing cameras could still produce a spoken OUT.** For example, one says OUT by 30 cm while the other says IN by 50 cm. Now an OUT is spoken only if each camera calls it OUT on its own.
4. **The dashboard now catches this calibration mistake.** After about 3 bounces both cameras saw, it shows **"Calibrated from the other end?"**. Review swaps the labels for you; then click Calibrate. Tonight it would have appeared about 2 minutes into play.
5. **The docs and the calibration dialog now say A is the same end for every camera.**
6. **Smaller fixes:** the Redmi's −1202 fps came from a clock-sync step and no longer happens. The report now shows each phone's capture rate rather than the rate it sent.

With your labels corrected plus these fixes, a replay of tonight gives 13 UNCERTAIN instead of 33, and 6 spoken OUTs. I can't tell you whether those OUTs were right, because there are no marks for this session.

All 93 tests pass. Everything is pushed (`41c45af`), including this session's ball detections (no video) and decision log entry 23.

## Before the next session
- **Reinstall the app on the iPhone 17**, so it gets the data reduction.
- Charge both phones and keep them out of direct heat.
- Calibrate both with the same A. If you mark a few bounces with chalk, I can score the calls.
