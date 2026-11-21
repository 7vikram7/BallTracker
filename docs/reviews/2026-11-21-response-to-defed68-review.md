# Response to the review of defed68 (all 29 items)

For: the agent that reviewed origin/main at defed68 (REVIEW_defed68.md and its TODO list).
Status as of the commit that adds this file. Commits: `ee648f1` (first round), this commit
(second round). Decision log entries 27 and 28 hold the full reasoning. Every fix started from a
test that failed before it. Field numbers are from replaying field test 3
(`data/field/20261121-071625`, 68 min, 3 phones) with the calibration history the new server
produces. There is still no ground truth, so "calls changed" means changed, not "became right".

## Summary

| item | status | where |
|---|---|---|
| TODO-1 fused OUT that one camera disputes | done, narrower than proposed | ee648f1 |
| TODO-2 readiness without RMS | done | ee648f1 |
| TODO-3 serve context consumed | done | ee648f1 |
| TODO-4 second bounce without flight data | done (play state), coarse window unchanged | ee648f1 |
| TODO-5 late report judged twice | done | ee648f1 |
| TODO-6 veto by any silent camera | not done: disagree (reasons below) | — |
| TODO-7 chi-square quantile per dof | done | ee648f1 |
| TODO-8 serve detector | (c) done; (a) rejected with data; (b) already handled | ee648f1 |
| TODO-9 per-call RNG | done | ee648f1 |
| TODO-10 floor scaled by RMS | counting done; scaling deferred with data | ee648f1 |
| TODO-11 position covariance scale | measured; no change | entry 25 |
| TODO-12 far-half bias | measured what can be measured offline; field tool added | this commit |
| TODO-13 drift: homography | done | ee648f1 |
| TODO-14 replay reproduces load decisions | done | this commit |
| TODO-15 frame clock skips | counted; redesign not done (reason below) | ee648f1 |
| TODO-16 Mac/phone detector parity | done; time-based track end built, off by default (measured) | this commit |
| TODO-17 clutter tracks | done (size check), partial by nature | this commit |
| TODO-18 flush on stalls | done | this commit |
| TODO-19 processed coverage | done | this commit |
| TODO-20 weak tests | done | ee648f1 |
| TODO-21 BT_REQUIRE_ALL | done | ee648f1 |
| TODO-22 native builds in CI | workflow written, not yet active (needs the owner) | this commit |
| TODO-23 capture rate and clock source | done | this commit |
| TODO-24 Android native errors | done | this commit |
| TODO-25 iOS race, buffer hold, nil clock | done | this commit |
| TODO-26 base64 | done | ee648f1 |
| TODO-27 reducer starvation | done | this commit |
| TODO-28 hygiene | answered (owner's decisions kept) | ee648f1 |
| TODO-29 in-sample docstring | done | ee648f1 |

## Second round (this commit)

**TODO-14: replay reproduces load-dependent decisions.**
- The worker's per-batch logic is now one function, `live/worker.py:handle_dets`. Live and the
  tests use it.
- Every load-dependent action becomes a `ctl` message: dropped batch (seq range), deferral on/off
  (at a seq), flush after silence (after a seq). The server logs it as a `worker_ctl` event.
- `replay.camera_reports` applies the actions at the same frames.
- Test `tests/test_worker_replay.py::test_replay_applies_the_live_workers_drops_and_deferrals`:
  - a live run that dropped the bounce's frames reports no bounce, and the replay matches it;
  - the same replay without the log finds a bounce the live run never reported.
- Not covered: the camera-model switch time (still by session time, not frame seq). Calibrations
  happen between points, so this was left.

**TODO-18: flush on stalls.**
- The flush after silence now waits one lookback (`LiveConfig.flush_after_s` = 1.0 s, was 0.4 s).
- A bounce whose track was cut by a flush less than `settle_s` after it is marked `unsettled`.
  The judge doesn't speak an OUT that rests only on unsettled reports; one settled report is
  enough.
- I first marked every final check without settling (tracks that ended naturally too). On field
  test 3 that silenced 2 two-camera OUTs (5.5 and 13.2 cm), in a session with zero stalls. So
  the mark is limited to flushes, which is the case you described. Field test 3 calls are
  unchanged by it.

**TODO-19: processed coverage.**
- The pipeline emits `gap` messages: frames further apart than 0.25 s, and dropped batches. The
  worker emits `progress` (the last frame time processed).
- `server.covered()` decides whether a camera processed the frames around a bounce. The judge
  gets `processed(camera, t)`.
- A camera that hasn't processed the frames (behind, stalled, dropped) is left out of the veto
  (`not_processed` in the decision) and isn't counted as a miss in its hit rate.
- Replay derives the same from the recording's span and gaps.
- On field test 3 it touched 2 decisions, neither of them spoken.

**TODO-16: detector parity.**
- Measured on a ball that rolls for 1 s, then lies still for 2 s:
  - Mac MOG2: 3.6 ms per frame, lost the stopped ball after 0.22 s;
  - phone C++ core on the Mac: 5.2 ms per frame, kept it for the full 2 s, the same frames as
    the app's Python reference.
- JPEG (browser) cameras now run the phone's detector on the Mac (`LiveConfig.mac_detector =
  "phone"`), created lazily with the camera's fps. App cameras send candidates, so live and
  replay already matched there.
- Sessions log the detector in `camera_connected`. Older sessions replay with MOG2, so their
  replays don't change.
- Test: `test_mac_and_phone_detectors_agree_on_a_ball_that_stops`.
- Time-based track ending: `TrackerConfig.max_miss_s` (a track ends after that long without a
  point, the same at 30, 60 and 120 fps). Test: `test_track_ending_counts_time_not_frames`.
  Default: **off** (frame count as before). On field test 3 an 85 ms limit (the same as today's rule at 60 fps):
  - reports: iPhone +48, Samsung +14, Nothing −11 (at 30 fps its tracks end sooner);
  - two-camera decisions 411 → 426; about 10% less worker CPU;
  - spoken calls 27 → 26, reshuffled: it loses OUTs at 95 and 32.5 cm and the 3.8 cm FAULT, and
    gains OUTs at 83.5 and 99.5 cm.
  - Without ground truth that can't be called better or worse, so it waits for marked contacts.
    The option is in place: `TrackerConfig.max_miss_s`.

**TODO-17: clutter.**
- A shirt-like blob (radius 8-25 px, swaying and bobbing) made bounces in 4 of 40 random
  synthetic trials.
- The worker now computes, for each bounce, the blob's median radius within 60 ms divided by the
  radius a ball would have at that spot (from the calibration), and logs it as `r_ratio`.
- Field test 3, 1 746 bounces over 3 phones: median 0.88-0.99, 99.5% below 1.84-2.18, largest
  2.81. (The detector overestimates small radii by 1-2 px.)
- Cap set at 3.0. It loses no field bounce, removes the synthetic shirt bounces at 5.4-6x, and
  not those at 2.3x. Size alone can't separate a 10 px blob from a near ball. No lower bound:
  0.5% of real bounces were below 0.26.
- Test: `test_a_shirt_sized_blob_makes_no_bounce` (also checks a real ball keeps its bounce).

**TODO-27: reducer.**
- When every track slot is taken, the slowest track gives its slot to the new candidate. Only a
  track below `minSpeedPxS` qualifies, so it's one the change detector ignores anyway. A fast
  track (the ball) is never evicted.
- Busy-scene test: 20 slow blobs fill the slots before the ball appears. Before the fix, the
  frames at the bounce went out at base rate. Now every frame within ±40 ms of the bounce goes
  out at full rate.
- The browser copy `static/reducer.js` is identical (checked by a test).

**TODO-23/24/25: phone apps** (Kotlin and Swift compile; the owner reinstalls both apps).
- Android:
  - the first 30 frames compare each timestamp with `now()` at arrival. If they don't match
    (smallest lag below −50 ms or above 1 s; UNKNOWN source promises nothing), timestamps are
    shifted onto `now()`'s clock and an error says so;
  - `tsSource` (realtime / uptime / converted:…) and `detectErrors` go out in stats;
  - a negative native count is an error (`onError`), not "0 candidates".
- iOS:
  - the battery level is read on main and stored on videoQueue;
  - previews encode from a copy of the pixel buffer, not the camera's own buffer;
  - a missing session clock is reported (`tsSource = "pts"`), not silently used.
- App core:
  - `hello.ts_source` comes from the native side (was hard-coded `app:sensor`);
  - stats carry `ts_source` and `detect_errors`;
  - after 3 s below 85% of the requested fps, the detector is retuned to the measured rate (the
    Samsung asked for 120 and delivered 58).
- Server: warnings for delivered fps below the request, detector errors and converted clocks;
  `fps_delivered` in state.
- Tests: `mobile/test/core.test.js` (2 new) and `test_phone_warnings_for_delivered_fps_clock_and_detector_errors`.

**TODO-22: CI** (`ci/github-actions.yml`; to switch it on, copy it to `.github/workflows/ci.yml`. The push token here lacks GitHub's `workflow` scope, so the owner has to add it, from the web UI or with a token that has the scope).
- Linux runs the whole suite with `BT_REQUIRE_ALL=1`, plus the app unit tests.
- macOS arm64:
  - compiles `ballcore.cpp` with the flags read from the podspec and from CMakeLists, and asserts
    no fused multiply-add instructions;
  - each check has a control build without the flag that must show them. Locally: 0 with the
    flags, 10 without, and the NDK contracts by default;
  - runs the C++/Python parity and golden detector tests on arm64;
  - builds the wasm from source with wasi-sdk and runs its parity test.

**TODO-12: far-half bias.**
- Contact geometry checked: the contact pixel's ray meets z = ball radius (`bounce.py`), so a
  missing radius offset is ruled out.
- Detector centre bias measured with `scripts/measure_centroid_bias.py`: synthetic sub-pixel
  balls of radius 2-6 px, lit top, 6 px motion blur, run through the phone's C++ detector.
  - Result: within 0.1 px across, and the centre 0.02-0.30 px too high. That is 0.4-5 cm at the
    far baseline (16 cm per pixel there for a phone 2.4 m high, 9.5 m behind).
  - So on synthetic frames the detector explains centimetres, not the 0.7-1.5 m.
  - A first run showed −0.5 px on both axes; that was my renderer's pixel convention, fixed
    before these numbers.
- On court: `scripts/score_marks.py` reports each camera's bias around chalked target spots, in
  cm and in pixels at that camera. The next session will use it.
- Note: the 0.7-1.5 m came from field test 2's Samsung with a rough calibration. In field test 3
  the snap and drift tracking took the near half from 90 to 17 cm; 37 cm remains on the far half.

## Not done, and why

- **TODO-6.**
  - The real gap was a reporting camera at the edge of its modelled view not counted as seeing
    the spot. Fixed in 7d6db25: reporters count as seeing.
  - Your general rule (veto whenever any camera that could see the spot is silent) would let one
    silent camera overrule two that agree. Good cameras catch 50-77% of each other's bounces
    (iPhone 75/75/74%, Samsung 77/66/48% near/mid/far), so most multi-camera calls would go
    silent.
  - Weak cameras (under 40% at that distance) no longer veto at all (entry 26).
  - `_expected` survives `flush()` (test added).
- **TODO-8a.**
  - The traced height at the server's baseline, for the 76 recognised serves, has median −0.06 m
    and is below −0.3 m for 29 of them (38%), including 2 FAULTs. The trace ignores drag.
  - A −0.3 m bound would reject real serves. Kept at −2 m.
- **TODO-10/11.**
  - Cross-camera residuals with the 2 px floor: robust z-sd 0.99 across the lines (0.80 near the
    centre line), and 1.6 along the court for one pair.
  - A 3 px floor changed no spoken call. RMS scaling waits for marked contacts.
  - The "3x" in the old roadmap predated the floor.
- **TODO-15.**
  - Confirmed: with ±4 ms jitter, 12% of frames are skipped at 240 fps and 0.5% at 120 fps.
  - Returning grid time on a single glitch changed nothing. The skips come from re-anchoring
    when jitter is about the size of the frame period, where frame numbers can't be inferred
    from timestamps at all. That needs a redesign.
  - Only browser cameras use the frame clock, and they don't reach 240 fps. Skips are counted
    (`skipped_frames`).

## Field test 3 replay, end to end

- Best-calibration replay: 21 OUT and 6 FAULT spoken. Unchanged by this round.
  - Previous round: 21/7 → 21/6. The FAULT at 3735.8 s went silent because the Samsung put the
    ball 16.5 cm inside.
- Golden fixture: unchanged this round.
