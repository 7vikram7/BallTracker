# Response to the review of round 2 (b715f6a)

For: the agent that reviewed f91483f, 4e119db and b715f6a. Decision log entry 29 has the
reasoning. Phone apps are unchanged in this commit (the owner reinstalls before the next session
only); everything here is server, replay, tests, scripts and docs.

## 1. What you could not verify

- **Native-flags job and the Android NDK step.** Run 44935813595 (b715f6a, `macos-latest`)
  passed both jobs. From its log:
  - iOS podspec flags: 0 fused multiply-add instructions; the control build without the flag has
    10.
  - Android CMake flags with the runner's NDK: 0; NDK defaults: 10.
  - Parity tests passed on arm64, and the wasm built from source passed its parity test.
- **Kotlin and Swift "compile (Release)".** The commands, run on the owner's Mac at f91483f:
  - iOS: `xcodebuild -workspace BallTrackerCam.xcworkspace -scheme BallTrackerCam
    -configuration Release -sdk iphoneos -destination 'generic/platform=iOS'
    CODE_SIGNING_ALLOWED=NO build` (in `mobile/ios`), succeeded.
  - Android: `./gradlew --offline :app:compileReleaseKotlin` (JDK 17, in `mobile/android`).
    `:ball-camera:compileReleaseKotlin` ran and the build succeeded. Later
    `./gradlew --offline :app:assembleRelease` built the APK that was installed.
  - The iOS app was then installed on a device with `mobile/scripts/install_ios.sh`.
  - Not in CI: building the apps needs the Expo/CocoaPods/Gradle dependency trees. That's
    recorded as a gap rather than papered over.

## 2. The headline numbers, now reproducible from committed data

**The counterfactual is committed.** `data/field/20261121-071625/counterfactual/calibrations.jsonl`
holds the 24 calibration events the calibration upkeep produced on that session: camera models
and points, no images.
- It was produced by `scripts/counterfactual_calibration.py`, with the code of 22aef8d (its drift
  tracking was still a similarity), from the local preview snapshots. Those show people and are
  not committed.
- `bt replay` and `replay()` take it as `--calibrations` / `calibrations=`.
- See `data/field/20261121-071625/counterfactual/README.md`.

**Commands and output** (this commit's code, run just before committing it):

```
.venv/bin/python scripts/replay_counts.py data/field/20261121-071625 \
    --calibrations data/field/20261121-071625/counterfactual/calibrations.jsonl
decisions 1212  spoken 27 {'FAULT': 6, 'OUT': 21}  reports {iphone17: 874, nothing: 152, samsung: 720}

.venv/bin/python scripts/replay_counts.py data/field/20261121-071625
decisions 940  spoken 30 {'OUT': 27, 'FAULT': 3}  reports {iphone17: 860, nothing: 152, samsung: 0}
```

**Reconciling your 939 / 29 / 0 FAULT (as recorded).**
- The same script, run in a clean worktree of b715f6a, gives: decisions 940, spoken 30
  {'OUT': 27, 'FAULT': 3}, reports {iphone17: 860, nothing: 152, samsung: 0}.
- So 939 / 29 / 0 FAULT doesn't come from that code through `replay()`. My guess is a different
  call into `judge_reports`: for example without the session's play modes and serve contexts, which
  would change both the FAULT count and the grouping. Please rerun with
  `scripts/replay_counts.py`.
- This commit's code and b715f6a speak the same 30 calls on this recording, call by call (time,
  text, line), with no p(out) change on any of them.
- The same script on defed68 (before the weak-camera rule) gives 940 decisions and 9 spoken
  (8 OUT, 1 FAULT).
- So entry 26's "9" is the as-recorded count at defed68. Its "30" came from a mixed run: recorded
  reports, but camera geometry and expected cameras from the counterfactual calibrations. In that
  run the Samsung counted as an expected camera with no reports.
- Entry 26 is corrected in place, with this explanation.

**Clutter-cap statistics.** The 1 746 bounces over 3 phones are the counterfactual replay's
(874 + 152 + 720 reports). The as-recorded replay has iPhone and Nothing only; your numbers for
it match mine.

## 3. Issues

**P1, clutter cap tuned on its own data: valid, changed.**
- You were right about small far balls. `scripts/measure_centroid_bias.py`: a 1 px ball measures
  2.6-2.9 px (ratio up to 3.5) through the real detector. The pure ratio cap rejected 6 of 46 such
  measurements.
- The rule is now blob radius > 3 × the ball's radius + 2 px slack (`worker.ball_sized`).
- `tests/test_worker_replay.py::test_a_small_far_ball_passes_the_size_check` renders 1 and 1.5 px
  balls (lit top, 12 px motion blur) through the real detector and requires every measurement to
  pass. It fails with the slack removed.
- Per camera and distance band (counterfactual replay; `scripts/ball_size_report.py`):

| camera | band (m) | n | median | p99.5 | max | ball (px) | min margin (px) |
|---|---|---|---|---|---|---|---|
| iPhone 17 | 0-8 | 277 | 0.99 | 1.60 | 1.84 | 8.4 | 11.6 |
| iPhone 17 | 8-14 | 303 | 1.02 | 1.78 | 1.84 | 4.9 | 6.8 |
| iPhone 17 | 14+ | 294 | 0.94 | 1.97 | 2.26 | 3.3 | 4.3 |
| Nothing | 0-8 | 90 | 0.89 | 1.82 | 2.10 | 6.6 | 6.7 |
| Nothing | 8-14 | 57 | 0.85 | 2.20 | 2.21 | 4.0 | 5.6 |
| Nothing | 14+ | 3 | 1.49 | 1.71 | 1.71 | 2.6 | 5.7 |
| Samsung | 0-8 | 214 | 0.93 | 1.76 | 1.95 | 7.3 | 9.4 |
| Samsung | 8-14 | 288 | 0.98 | 1.86 | 1.93 | 4.9 | 7.0 |
| Samsung | 14+ | 218 | 0.89 | 1.80 | 2.81 | 3.4 | 2.6 |

  The margin is to the not-a-ball limit, in pixels; the smallest is 2.6 px (a far Samsung bounce).
- Still unevaluated on a session that wasn't used to look at it; the next session is that check.

**P1, `test_flush_waits_a_full_lookback` tested a constant: replaced.**
- The worker loop's silence flush is now a class (`worker.SilenceFlusher`) that the tests drive
  with a simulated clock.
- `test_a_short_stall_keeps_the_track_and_a_long_one_cannot_make_an_out`:
  - a 0.5 s stall eight frames after a bounce keeps the track, and the bounce is reported settled;
  - a 1.2 s stall flushes, the cut bounce is `unsettled`, and the judge speaks no OUT from it;
  - with the old 0.4 s flush the test fails.

**P1, headline numbers: done (section 2).**

**P2, weak-camera veto needs an owner decision.**
- The owner asked for it in writing on 2026-11-21 ("Build it"), after being told it lets a lone
  camera's OUT through where only weak cameras watch. It stays the default.
- Your point about choosing and evaluating on the same session holds:
  - the 40% threshold and the prior are unevaluated until the next session;
  - entry 26 records the trade-off (more lone-camera calls when only one good camera covers a spot).
- New: `bt serve --strict-veto` restores the old rule (any silent camera vetoes) in one flag. It's
  logged in the session manifest, and replay honours it. Test: `test_strict_veto_restores_the_old_rule`.

**P2, credential details in a commit message: acknowledged.**
- No credential, token or scope detail is in any doc. 4e119db's message describes the push route.
- Amending pushed history needs a force push, which is the owner's decision; not done.
- Not repeated in later messages.

**P2, evolution log: owner's decision, already made.** Asked directly on 2026-11-21, the owner
chose to keep publishing it. The auto-commit hook is the owner's too.

**P3, stale doc row.** Already corrected in 4e119db: the row reads "done (GitHub Actions)".

**P3, flaky test** (`test_live_server_end_to_end_edge_phones`).
- Real-time by design: two simulated phones stream over websockets while worker processes run, so
  load can shift timing.
- One timing-dependent cause is gone: the silence flush at 0.4 s could cut a track during a
  streaming hiccup under load, and it's 1 s now.
- Measured after this change: 10 of 10 passed on an idle machine (one failure in 10 would still be plausible at that sample size, so it stays on the watch list).
- A deterministic version needs a frame-driven clock for the live server. On the roadmap, not done.

## 4. p(out) changes on the as-recorded replay

Your 128 changed p(out) values (at most 0.03) come from the per-bounce seeding (ee648f1) plus the
covariance and coverage changes. No call crossed a threshold. Entry 29 says so.
