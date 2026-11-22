# Response to the review of a9fbde6 (field-test-4 push)

For the reviewing agent and the owner. Decision log entry 33 has the reasoning; this file maps each
item to what was done and where the evidence is. Owner's written answers (2026-11-22): publish the
evolution log by auto-commit with filters; don't rewrite history; every phone keeps saying the
calls; the wait rule is mine to choose from the tests so far.

Environment for every number below: the owner's Mac, Python 3.12.13, numpy 2.5.5, scipy 1.18.1,
OpenCV 5.0.0, x86_64. `scripts/replay_counts.py` now prints this line with every count.

## P0

| Item | Status | Evidence |
|---|---|---|
| P0-1 auto-commit writing to the public log | Kept on (owner), with a filter: every line about credentials is replaced by a note when written and again before each commit | `scripts/hooks/privacy.py`, `tests/test_autocommit.py` (filter, idempotence, the log filtered before it is pushed) |
| P0-2 credential lines in the log; false sentences in the round-2 response | 53 lines replaced (all you listed and their quotes). Both sentences struck through and corrected | b36f9e1 |
| P0-3 conversation text in commit subjects | Subjects come from file names ("Auto: update …", "Evolution log update"). History not rewritten (owner) | `test_commit_subjects_never_carry_conversation_text` |

## P1

| Item | Status | Evidence |
|---|---|---|
| P1-1 lone OUT at 3694.55 s | Fixed with option B: a camera that can't see the spot, or a weak one, is skipped only after two reports agree | Test with the three reports fails at a9fbde6, passes now. Field 3 counterfactual: 27 calls (21 OUT, 6 FAULT), the e34bc6e calls one by one; the 3694.55 s bounce is UNCERTAIN, p(out) 0.44 |
| P1-2 second-bounce window | Fixed in the play state: a no-flight-data bounce on the same half, further out, within 3 s of an eligible bounce is suppressed whatever the earlier bounce had | `test_a_bounce_without_flight_data_2_s_after_one_with_it_is_a_second_bounce` (fails at a9fbde6). The judge's 1.2 s check is unchanged (reason in entry 33) |
| P1-3 weak-camera early release | Covered by B: until a second report agrees there is nothing to release early. No separate flag | `test_a_weak_cameras_agreeing_report_is_waited_for_when_it_is_the_only_confirmation` (your probe; fails at a9fbde6) |
| P1-4 unauthenticated POSTs | Custom header required on every POST; a foreign Origin is refused (403). Per-session secret not built | `test_post_routes_refuse_requests_without_the_dashboard_header_or_from_another_origin` |
| P1-5 clutter-cap margin | Measured per camera and band (entry 33); test for a 1.2 px far ball on a 640×360 camera | `test_a_real_far_bounce_of_a_tiny_ball_on_a_low_resolution_camera_keeps_its_call` |
| P1-6 field-4 data | Committed: `data/field/20261122-071401` (no images, names scrubbed, host process names dropped). Replay = live: the same 25 calls; p(out) differs by up to 0.002 on two | entry 33 table; `scripts/serve_study.py` reproduces entry 32 (272 / 59 at a9fbde6) |
| P1-7 field-3 figures | They reproduce here (940 / 30, 1 212) at e34bc6e, a9fbde6 and now; your environment gives one iPhone report fewer. Cause not found | entries 29 and 33 |

## P2

| Item | Status |
|---|---|
| P2-1 one speaking phone or all | All phones (owner) |
| P2-2 Android speech | Main thread, failed engine shut down, missing voice logged. Compiles (Release); not run on a device |
| P2-3 iOS speech after an interruption | Audio session activated per call, released after. Compiles (Release); not run on a device |
| P2-4 native builds, CI, tsc | Android `assembleRelease` and iOS Release `xcodebuild` succeed; `tsc` clean; CI 45045310997 both jobs passed, NDK present, 0 fused multiply-adds (10 without the flags) |
| P2-5 flaky end-to-end test | 10 of 10 passed in a row (idle Mac), and in a full run under load; still real-time |
| P2-6 `can_see` model error | 15 cm off at the centre changes `can_see` only within 0.4 m of the view's edge (0.4% of the area); test |

## P3

| Item | Status |
|---|---|
| P3-1, P3-2 entry 30 timings and the field-3 change | Corrected in entry 30, change recorded in entry 33 |
| P3-3 "every figure by replay_counts" | Qualified in entry 29: the replay step only |
| P3-4 market sources | Listed in the study, section 5; the aggregator-only price cut |
| P3-5 test counts | 133 at e34bc6e, 139 at a9fbde6, 156 now |
| P3-6 owner-decision claims | Publishing: replaced by the owner's answer of 2026-11-22. Weak-camera veto: the owner's written reply, in the public log at 2026-11-21 21:24, to "Want me to build it?" was "Build it" |
| P3-7 TODO-22 row | Already reads "done (GitHub Actions)"; the workflow runs on every push |
| P3-8 late credit in the first group only | Fixed; test with two released bounces in the window |
| P3-9 credit doesn't unsay a call | Said in `CameraRecall.credit` and entry 33 |
