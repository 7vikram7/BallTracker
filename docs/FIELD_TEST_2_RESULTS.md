# Field test 2: results (2026-11-19, full-size indoor court)

Session `20261119-070916`: 100 minutes; 2 cameras (iPhone 17 app at 120 fps, Samsung SM-S948B app
at ~40-55 fps); a Redmi 8A for 4 minutes. No ground truth (no chalk marks or referee video), so
accuracy cannot be scored. Sample: [data/samples/fieldtest2_60s](../data/samples/README.md).

## What happened

| | iPhone 17 | Samsung | Redmi 8A |
|---|---|---|---|
| Position (from calibration) | behind baseline A, corner, 2.3 m high | behind baseline B, corner, ~1.8 m | – |
| Capture / processed | 120 / 111 fps | 58 → 30 fps (asked 120) | 12 fps |
| Detection per frame | 4 ms | 12 → 27 ms | 82 ms |
| Heat / battery | serious / 85 → 40% | critical / 45 → 3% | – |
| Ball candidates per frame | 3.1 | 7.2 (a third of frames at the cap of 12) | – |
| Calibration (live) | 9.3 px RMS | 9.5 px RMS | – |

605 decisions: 368 IN, 17 OUT announced, 162 UNCERTAIN; only 51 seen by both cameras.
Latency median 1.3 s, 90th percentile 4.1 s (the Mac fell behind the 120 fps stream).

## Causes and fixes

1. **Calibration**: the net-top points assume the net top sits on the sidelines; on the portable net
   the posts stand 30 cm outside and higher. Without them: iPhone 2.7 px, Samsung 4.5 px.
   Fix: net tops no longer offered; the dashboard names probable mis-clicks.
   (Replaying with the fixed calibrations moved bounces by only 2 cm median but made 64 uncertain
   calls confident.)
2. **OUT calls that were not play**: second bounces of unreturned balls (> 1.2 s after the first)
   and dead balls (pre-serve bounces, pickups) behind the baseline. Fix: play state
   ([DECISIONS](DECISIONS.md)). Plus: one far camera alone cannot announce an OUT.
   Replay of 550 s: 7 → 3 announced OUTs, all confirmed by both cameras.
3. **Mac overload** (19 000 frames dropped, delays up to 9 s): the bounce search on every track.
   Fix: batched search + still-track skip (≈2.3x), phone-side reduction (27% fewer frames).
   A 550 s two-camera replay now takes 3 minutes of CPU.
4. **Samsung slow and hot**: see the Android changes in [DECISIONS](DECISIONS.md); verify next time
   (the card should show detect < 8 ms at 60 fps).
5. **Placement**: both cameras on the same side (x ≈ +5 m) at opposite ends; each saw only its own
   half well.

## Next session checklist (in addition to [FIELD_TEST_2_FULL_COURT.md](FIELD_TEST_2_FULL_COURT.md))

* Arrive 30 minutes early. Rebuild/reinstall the apps first (today's app changes are in the JS).
* Hotspot: if the Mac shows a `192.0.0.x` address, the carrier is IPv6-only. Use an Android
  phone's hotspot, or don't use the hotspot iPhone as a camera.
* Cameras at the 4 corners, **diagonal pairs on opposite sides**, ≥ 2 m high, each seeing its
  near corner with margin. Every line seen by two cameras.
* Exposure: Shutter 1/1000 set **before** calibrating; never change it mid-session.
* Calibrate with ground points only; redo if the dashboard names a mis-clicked point or RMS > 3 px.
* Ground truth, at least one of: 10 chalk-mark bounces into `docs/field_test_marks.csv`; a phone
  filming the court with sound (the referee); Serve button before each serve.

## Weaker Android phones covering one section

Useful **as a second opinion on the lines they see well**, with conditions:
* They must keep up: a Redmi 8A managed 12 fps (82 ms per frame) at 1280x960; ≥ 30 fps at
  1280x720 is the minimum worth having. Check the card's *detect* time (< 30 ms at 30 fps).
* Low and close (1-1.5 m, a few metres from a line, looking along it) gives very precise
  across-the-line measurements for that line: exactly what a single far camera lacks.
* Each still needs its own calibration with ≥ 6 points it can see; a narrow view of one corner
  has few points, so aim to include a corner plus the kitchen/centre T or the far sideline.
* They also add load on the hotspot (about 5 devices max on an iPhone hotspot).


## Added 2026-11-19 (evening): the two phones disagreed by ~0.9 m on the far half

Matching the 29-31 bounces both phones reported: on side B (near the Samsung) they agree within
6-18 cm; on side A (the Samsung's far half, behind the net) the Samsung puts every bounce 0.7-1.5 m
closer to the net than the iPhone (median 87 cm). Its own stated uncertainty there was 15-30 cm,
so this is a bias, ~10 px in its image, not noise. Snapping both calibrations to the court lines
reduced it only to 80 cm; refining the Samsung from shared bounces (iPhone as reference,
`geometry/crosscal.py`) reduced it to 21-49 cm on held-out bounces. Lessons: a camera placed low
measures its far half poorly; put cameras at both ends (each owns its near half) and let the
dashboard's shared-bounce refinement run during the first minutes of play.
