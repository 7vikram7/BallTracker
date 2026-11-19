# Field test 1: scaled court outdoors, two phones, live calls

**What this test decides:** whether the current build (phones streaming
from the browser at 60 fps to the Intel Mac) calls lines correctly on a real,
taped court outdoors. Its measurements also become the baseline that the native
app ([ROADMAP_MOBILE_APP.md](ROADMAP_MOBILE_APP.md)) has to beat. The
recordings become the test data the app's on-phone code is checked against.

## Objectives and pass marks

| # | Objective | How it's measured | Pass |
|---|---|---|---|
| 1 | **Stays up**: 2 phones stream outdoors for a whole session | Camera cards (*in* / *processed* fps, *drops*, clock *rtt*); `events.jsonl` | 20 min each, *processed* ≈ *in*, drops < 5 %, median rtt < 20 ms, any disconnect reconnects by itself |
| 2 | **Calibrates** on a taped court in daylight | RMS shown after *Calibrate*; *Check* overlay | RMS < 2 px; drawn lines sit on the tape (within one tape width) everywhere |
| 3 | **Sees the bounces** outdoors (sun, shadows, background) | Drill bounces with a report, compared with the marks sheet | ≥ 90 % reported by at least one camera, ≥ 70 % by both |
| 4 | **Accurate**: position versus chalk mark | Signed distance to the line, from the marks sheet (truth) and from the system | median error ≤ 2 cm, 90 % within 5 cm |
| 5 | **Never wrong out loud** | Every spoken OUT/FAULT checked against the mark or the referee video | **0** OUT spoken for a ball that was in. Clear outs (> 10 cm) called ≥ 80 % of the time |
| 6 | **Quick enough** | `latency_s` in `events.jsonl`, plus the referee video (bounce sound to spoken call) | median ≤ 1.5 s, worst ≤ 3 s |
| 7 | **No false alarms in play** | Soft rallies, referee video | 0 spoken OUT on balls that were in, including at paddle hits, players walking and balls rolling |
| 8 | **Collect data** for later work | `--record` | All drill and rally frames saved with timestamps |

Objectives 4 and 5 matter most. If objective 4 misses but objective 5 passes,
the system is honest but too often unsure, and 120–240 fps (native app) is the
fix. If objective 5 fails, we stop and fix that before anything else.

## Before you go out

**1. Court surface.** Use the driveway or another hard surface, not grass. Grass
deadens the bounce, chalk marks don't show on it, tape doesn't stick, and sunlit
grass is close to the ball's yellow-green, so the detector can mistake grass for the ball.

**2. Measure the taped court** (outside edge of tape to outside edge) and make its file:

```bash
cp configs/court_custom_example.yaml configs/court_yard.yaml   # then edit width, length, kitchen_depth, line_width
bt court --court configs/court_yard.yaml --out court_yard.png  # look at it: is it the shape you taped?
```

Keep the real ball (don't scale it). If you have a portable net, put it up: the
**net-post tops are the most useful calibration points**. With no net, calibration
uses only points on the ground. That works, but use every corner and line
intersection you can see.

**3. Phone settings** (on the phone page, before *Start streaming*):
* **Landscape.** Your test this morning sent portrait frames (720×1280). Turn
  the phone sideways *before* tapping Start, and lock rotation so it can't flip mid-session.
  Changing orientation after calibrating breaks the calibration.
* 1280×720, 60 fps, **1× lens** (not 0.5×, whose distortion we don't model).
* **JPEG quality about 0.6.** This morning's frames were 124 KB each, which is about 60 Mbit/s per
  phone. Two phones at that rate can saturate Wi-Fi out in the yard. 0.6 roughly halves it.

**4. Wi-Fi.** Check that the yard has strong signal, ideally 5 GHz. The clock *rtt* on
each camera card is the quickest check.

**5. Hearing the calls.** The Mac speaks the calls. If you can't hear the Mac's
speakers from the court, open `http://<mac-ip>:8080/dashboard` on a **third**
device (the spare Android works) and tap *Enable sound*. A camera phone can't
also be the speaker, because its camera page has to stay in front.

**6. Referee video.** Any extra phone, filming normal video from the side with
sound: the court, the bounces, and the spoken calls. It's the truth for the
rally part and for latency.

**7. Start the server:**

```bash
bt serve --court configs/court_yard.yaml --record
```

Recording is about 4–7 MB/s per phone, roughly 25 GB per phone-hour. That's fine:
the Mac has 680 GB free.

## Camera placement (2 phones)

Both phones must see the **same lines** you drill on, or the cross-check
between cameras (objective 5) never gets exercised.

* **Phone 1, behind baseline A, high:** tripod at 1.5–2 m (as high as
  you can manage), centred, looking down the court. Sees all lines, depth is
  compressed.
* **Phone 2, at the side near the net line, about 1 m high,** looking across
  at baseline B and the right sideline. Sees across-line distances well.
* Drill against **baseline B and sideline_right**, near where they meet. Both
  phones see that area.
* Keep the sun **behind or beside** the phones, not in front of them. Shade the phones
  if it's hot, because they throttle when hot.

## Running order (about 90 minutes)

**A. Setup and soak (15 min).** Connect both phones, calibrate both, *Check* both.
Leave them streaming for 10 minutes while you do the next steps; note the
*in*/*processed*/*drops*/*rtt* numbers. Take a photo of each phone's position.

**B. Chalk drill (40 min, 30 bounces).** This is the most important part.
* Ball marked as in the recording guide (damp ball rolled in chalk, or washable paint).
* Toss or drop the ball so it lands near **baseline B / sideline_right**:
  about 10 clearly in (more than 15 cm inside), 10 clearly out (more than 10 cm out), and
  10 **close** (within 5 cm of the line, in or out).
* After each bounce: say its number out loud (for the referee video), measure
  the **signed distance from the line's outer edge to the nearest edge of the mark**
  (positive = out, 0 or negative = touching or in), write it on the marks
  sheet, then wipe the mark.
* Fill in [field_test_marks.csv](field_test_marks.csv) (format below). No
  times are needed: bounces are matched in order.

**C. Soft rallies (15 min).** Normal soft play, players moving, balls rolling
past. Just play; the referee video is the truth.

**D. Optional stress test (10 min).** Add the spare Android as a 3rd camera at
640×480 / 30 fps and see whether the Mac keeps up (*processed* vs *in*).

**E. Stop the server** with Ctrl-C (it closes the recording cleanly).

### Marks sheet format

```
bounce,t_s,x_m,y_m,line,signed_distance_cm,notes
1,,,,baseline_B,-12,clearly in
2,,,,sideline_right,3.5,just out
3,,,,baseline_B,0,touching line
```

Line names: `baseline_A`, `baseline_B`, `sideline_left`, `sideline_right`,
`kitchen_A`, `kitchen_B`. Left and right are as seen standing behind
baseline A, looking at the net.

## What to send back

1. The session folder: `data/live/sessions/<date-time>/` (events, court, recordings).
2. `docs/field_test_marks.csv`.
3. The referee video.
4. A photo of each phone's position, and the court measurements.
5. Notes: anything odd (glare, calls you disagreed with, disconnects).

You can score it yourself right away: `bt report data/live/sessions/<id> --marks docs/field_test_marks.csv` writes `report.md` in the session folder (cameras, every call, accuracy against your marks). From these I'll score objectives 1–8. That includes replaying the recorded frames
offline to separate detection problems from timing and calibration problems.
