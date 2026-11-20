# Do weak 30 fps Android phones help? (mock-data study, 2026-11-20)

**Short answer: yes, as extra cameras next to the two good phones; no, as a replacement for the
second good phone.** Measured with `scripts/lob_study.py --rig <rig> --no-reducer` (same 54
drive/lob scenarios, same seed, as [LOB_STUDY.md](LOB_STUDY.md)); reports in
`data/experiments/lob_rig_*/report.json`.

## Set-ups

All on 2.4 m tripods at the four corners (1.5 m outside the sideline, 3 m behind the baseline).

* **2good**: the current rig. iPhone at 120 fps (B-left) and Samsung at 60 fps (A-right),
  1920x1080, detection jitter 0.4 px, 2 % missed frames.
* **+2weak**: add two budget Androids in the empty corners: 30 fps, 1280x720, jitter 1.0 px
  (motion blur), 8 % missed frames, ±3 ms uneven frame timing, coarser calibration clicks.
* **+2poor**: the same phones in a worse case: jitter 2.5 px, 20 % missed frames, ±6 ms.
* **1good+2weak**: the iPhone and the two weak phones (no Samsung).

The weak-phone numbers are assumptions, not measurements. A mini-court session with one of
the phones would replace them with real ones.

## Results

27 OUT first bounces (19 by 10 cm or more, or over a sideline; 8 by only 3 cm).

| | OUT announced | of them 3 cm out | wrong OUT | position error median / p90 | OUTs vetoed by a camera that saw nothing | second bounces found (all suppressed) |
|---|---|---|---|---|---|---|
| 2good | 20/27 | 1/8 | 0 | 0.6 / 1.2 cm | 0 | 24/54 |
| **2good + 2weak** | **24/27** | **5/8** | 0 | 0.8 / 2.1 cm | 0 | 32/54 |
| 2good + 2poor | 22/27 | 3/8 | 0 | 0.6 / 1.6 cm | 0 | 32/54 |
| 1good + 2weak | 15/27 | 0/8 | 0 | 1.2 / 2.4 cm | 3 | 11/54 |

No set-up announced a wrong OUT or any false bounce. The weak phones added 2-4 unannounced
false bounces.

## Reading

* **Where they help: close calls.** The good phones already call every clear OUT. Near the line,
  a call is announced only when the fused uncertainty is small enough (p(out) ≥ 95 %). Each extra
  camera shrinks that uncertainty, even a blurry one, because fusion weights each camera by its
  own uncertainty. With two ok weak phones, 5 of the 8 OUTs by 3 cm were called instead of 1.
* **Where they don't: as one of the two main cameras.** The weak phones found only 31-39 of 54
  first bounces (poor ones 8-10). Their physics checks reject many true bounces because 30 fps
  leaves only 2-4 points on each side of the contact. Without the Samsung, many bounces were
  seen by one good camera only, and **the weak phones vetoed 3 correct OUT calls**. A camera
  that can see the bounce spot but reports nothing silences an OUT (see `fusion.py`).
* **Also useful:** more second bounces found (rally logic), more coverage when a player blocks a
  good camera, and more pairs for the shared-bounce calibration refinement.

## Before relying on them in practice

1. **They must really run at 30 fps.** In field test 2 the Redmi 8A managed 12 fps at 1280x960.
   At 1280x720 on the app, check the dashboard: *detect* under 30 ms and *processed* ≈ 30 fps.
   A 12-15 fps phone is closer to "poor" or worse.
2. **Good light, fast shutter.** At 30 fps the camera may expose for 1/30 s and the ball becomes
   a streak. Outdoors in daylight is fine; under dim lights expect the "poor" row.
3. **Put them where the good phones are weak:** the two empty corners, or one per baseline
   looking down the lines that the good phones see at a shallow angle.
4. **Mac load:** app phones send detections only, so two more cameras cost little. Browser-page
   phones send frames: with 4 cameras, use 960x540 (see LIVE_SETUP.md).

## Suggested follow-up (not done)

The veto treats every camera as equally reliable. A camera that historically reports only ~60 %
of the bounces it can see should veto less, for example by requiring a miss from a camera with
measured recall ≥ 90 % at that spot. This only matters if a weak phone stands in for a good one.
Measure recall per camera from shared bounces first.
