# Testing on a mini court

**Short answer: yes, mini-court sessions help**, as long as each one tests something specific
and the results are read in light of what a small court changes. They are cheap and repeatable
(no booking, no other players, ground truth is easy to mark), so they are the right place to
debug. They cannot replace full-court sessions for speed, distance and lighting.

## Starting the server

```bash
bt serve --court-scale 0.2 --record      # a 1/5-size court; use your own scale
```

Every line is scaled; the ball and the painted/taped line width stay real. The play-state
thresholds scale too (speeds and times by sqrt(scale), distances by scale: gravity does not
shrink). Calibrations for a practice court are stored separately (`data/live/calibration-scale0.2/`),
so they never mix with full-court ones. If your taped court is not an exact scale copy, measure
it and use `--court my_court.yaml` (see `configs/court_custom_example.yaml`).

| scale | width | length | kitchen depth | net height |
|---|---|---|---|---|
| 0.2 | 1.22 m | 2.68 m | 0.43 m | 0.18 m |
| 0.25 | 1.52 m | 3.35 m | 0.53 m | 0.23 m |
| 0.33 | 2.03 m | 4.47 m | 0.71 m | 0.30 m |
| 0.5 | 3.05 m | 6.71 m | 1.07 m | 0.46 m |

Measure the taped lines' **outer edges** to the centimetre; a 2 cm taping error at 1/5 scale is
a 10 cm error at full scale, and it shows up directly as a wrong call.

## What a mini court shows well

1. **Calibration with "Snap to lines".** Tape looks different from paint (shinier, sometimes
   wrinkled): tap the 4 near corners, snap, and check the blue points with the magnifier.
   Report any snap that lands on the wrong edge, with a screenshot.
2. **Line-call accuracy in centimetres.** The ball and the line width are real, so "how far
   from the line was the contact" is measured exactly as on a full court. The most useful
   session: 20-30 bounces near each line (1-5 cm in and out), each contact marked (chalk
   or powder on the ball, or a sheet of paper), photographed, and entered in a marks sheet
   like `docs/field_test_marks.csv`. This is the ground truth the full-court tests lack.
3. **Two cameras agreeing.** Calibrate one camera, play, and watch the second camera's card:
   after ~15 shared bounces it should offer a refined calibration (the shared-bounce
   refinement has only been tested on synthetic data so far).
4. **High balls.** Toss the ball so it leaves the top of the frame and comes back down steeply
   near a line. That tests re-acquisition, tracking a fast vertical fall, and the lob rules
   (`docs/LOB_STUDY.md`) on real footage.
5. **Phones.** Thermal throttling, battery, detection time and Wi-Fi drops over 30-60 min,
   with no court booking needed. The Samsung changes (detection priority, 16:9) need exactly
   this check: the dashboard should show detection under 8 ms.
6. **Clutter.** Shoes, bags and plants that look like the ball: the dashboard's
   candidates-per-frame number and the phone-side reducer's static-clutter filter.

## What it does not show

* **Speed and distance.** Cameras stand 1-3 m away instead of 10-17 m, so the ball is 5x
  bigger in the image and much easier to find; drives and lobs are slower and lower. A
  result that is good on the mini court is necessary, not sufficient.
* **Play-state timing.** The scaled thresholds are physics-based guesses; real rallies on a
  small court do not follow scaled timing (people react at the same speed).
* **Lighting and background** of the real venue (sky, nets, neighbouring courts).

## What to send back

The session folder (`data/live/sessions/<date>/`, recorded with `--record`), the marks sheet
if you made one, and screenshots of anything odd. Every session can be replayed with new
code (`bt replay <session>`), so one good mini-court session keeps paying off as a
regression test.
