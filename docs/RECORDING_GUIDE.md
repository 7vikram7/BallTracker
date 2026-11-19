# Recording guide: Phase 0 (accuracy tests)

Goal: record footage that lets us measure how accurately one phone can locate a
bounce, using chalk marks as ground truth. Works on a real court or a smaller
taped floor court.

## 1. What you need

- iPhone 17 and/or iPhone 16, plus tripods or clamps (higher is better: 2–4 m on a
  real court; at least 1.5 m on a floor court).
- **Blackmagic Camera** app (free), or the stock Camera app in Slo-mo mode.
- Chalk: a stick of sidewalk chalk crushed into powder, or chalk-line powder,
  in a sieve or tea strainer. Washable. Ask the venue first.
- Tape measure (metric is easiest), phone for photos of the marks.
- For a floor court: painter's tape (~48 mm wide).

## 2. Court

**Real court**: nothing to do. Use `configs/court_full.yaml`.

**Floor court**: tape a rectangle with a centre line (the "net") and kitchen
lines. Half size is 3.05 m x 6.71 m (`configs/court_half_scale.yaml`). Any size
works: measure it **to the outside edge of the tape** and edit
`configs/court_custom_example.yaml`. Measure to within 1 cm; the diagonal check
(both diagonals equal) confirms it's square.

Put a small strip of tape where the net posts would be at 0.914 m (half court:
0.457 m) height if you can (a box or a broom handle works). Points above the
ground make calibration much more accurate.

## 3. Camera placement

The camera must see the **whole region you want to call** with margin. In
simulation, a phone 1 m behind the baseline at 3 m height did NOT see the
sidelines near it with the 1x lens. Good starting positions (real court; halve
distances for a half-size court):

| Position | Where | Lens |
|---|---|---|
| Behind baseline (default) | centred, 4–5 m behind the baseline, 3–4 m high | 1x |
| Corner | 3 m outside + 3 m behind the corner, ~3 m high | 1x |
| Side | level with the middle of the half, 4–6 m outside the sideline | 1x |
| Net post | 1 m outside the sideline at the net, ~1.6 m high | 0.5x |

Prefer the **1x main lens**. The 0.5x ultra-wide has strong distortion which our
calibration does not model yet.

Check before recording: all four corners of the half you're judging plus a
little margin are in frame, and as many calibration keypoints as possible
(corners, kitchen-line ends, centre-line Ts, net-post tops).

## 4. Phone settings (important)

In Blackmagic Camera (or as close as possible in the stock app):

- Resolution 1920x1080, frame rate **240** (or 120 if 240 isn't offered).
  In Blackmagic Camera the FPS slider only goes to 60; high speed is
  **OFF/SPEED** (right of the FPS slider): set the base FPS to 30, turn on
  OFF/SPEED and pick 120 or 240. If only 15/40/60 are listed, in Settings
  set Resolution to HD and turn **HDR Video off** (HDR caps non-Pro iPhones
  at 60). If it still caps at 60, use the stock Camera app's Slo-mo
  (Settings → Camera → Record Slo-mo → 1080p 240) instead. Hold the phone
  in **landscape**.
- An off-speed clip is saved as a normal 30 fps file in which each frame is
  1/240 s of real time, so its timestamps are wrong. Always analyse it with
  the true capture rate: `bt analyze clip.mov --fps 240 ...`.
- **Shutter**: fast, 1/1000 s or faster, and **locked**. Indoors you may need
  1/500 s to get enough light. Avoid auto-shutter.
- **Stabilisation OFF**, lens correction off.
- **Focus locked** on the court, **exposure / ISO locked**, white balance locked.
- Don't zoom. Don't touch the phone once calibrated (any knock means
  recalibrating).
- Start recording a few seconds before the first ball (the detector learns the
  empty background).

### Stock Camera app Slo-mo (needed on non-Pro iPhones)

Blackmagic's OFF/SPEED tops out at 60 fps on a non-Pro iPhone 17, even with HD
and HDR off. Use the stock app instead:

- Settings → Camera → Record Slo-mo → **1080p HD at 240 fps**.
- Camera app → **Slo-Mo**, **1x** lens (the main camera is the sharpest).
- Frame the court, then **long-press on the court** until "AE/AF LOCK" appears.
  That locks focus and exposure. Drag the sun icon down slightly if the image
  looks bright: a darker exposure usually means a faster shutter and less blur.
- You can't set the shutter. The phone picks it, and it can't be slower than
  1/240 s. In bright light (outdoors, or a well-lit hall) it goes much faster.
  Dim rooms give a smeared ball, so **light matters most indoors**.
- Tap record a few seconds before the first ball.

**Transferring**: AirDrop with Options → "All Photos Data", or Image Capture on
the Mac, so the original 240 fps file arrives. Never send via Messages or
WhatsApp, and don't export from Photos: those give a re-encoded 30 fps copy.
Check with `ffprobe -v error -select_streams v:0 -show_entries stream=avg_frame_rate clip.mov`
(should be about 240). The original file plays in real time with true
timestamps, so `--fps` is not needed for it.

### Lessons from the first real clip (2026-11-17)

- **Send the original.** An exported Slo-mo copy is 30 fps with speed ramps,
  and the timing has to be reverse-engineered. AirDrop with "All Photos Data"
  or Image Capture only.
- **Check the Slo-mo setting is 240**, not the default 120.
- **Calibration points are needed even for a one-line test.** Tape small
  crosses at 6+ floor points whose positions you measure (e.g. a 1 m x 1.5 m
  rectangle with the test line as one side, plus the midpoints). Without them,
  results are pixels, not centimetres.
- **Use white chalk or flour, not yellow powder.** Yellow is the ball's colour
  family. The detector now copes, but don't make it work harder.
- **Keep yellow-green moving things out of shot** (variegated plants in wind).
- **Landscape** gives more floor in view; portrait shows mostly sky and wall.
- Mains lights flicker at 100 Hz, visible at 120–240 fps. The detector
  compensates, but daylight or a well-lit hall is cleaner.

## 5. The chalk drill (ground truth)

1. Sprinkle a thin, even band of chalk ~30 cm wide centred on the line you're
   testing (baseline first, then a sideline). A thin layer is enough.
2. Feed balls so they bounce in the band, **one at a time**. Have the feeder
   stand on the far side of the net.
3. After each bounce, photograph the mark top-down with the tape measure in the
   shot, and write down:
   - which line;
   - the signed distance in cm from the **outside edge of the line** to the
     **nearest edge of the mark** (positive = mark outside the line, negative =
     inside; 0 or negative = touching = IN);
   - roughly when it happened (the clip's on-screen timer is fine).
4. Wipe or re-chalk the spot, repeat. Aim for 50+ bounces per camera position,
   with plenty within ±5 cm of the line, since those are the calls that matter.

**Other ways to get a mark** (always with a real pickleball, never a
substitute ball: a sponge ball bounces, squashes and skids differently, and
looks different to the detector):

- **Damp ball**: dip the real pickleball in water, shake off drips, hit. On a
  dry hard court it leaves a dark spot for a minute or so; photograph it
  straight away. Leaves nothing behind. Weak on glossy indoor floors.
- **Washable paint**: dab thinned washable (tempera / poster) paint on the
  real ball with a sponge. A clear mark anywhere on the floor, cleans up with
  water. Only on surfaces you own: never on a club court. Colour the ball's
  surface lightly, or analyse with `--no-color`, since the detector's colour
  filter expects a yellow-green ball.
- **Carbon paper**: tape white paper over the line, carbon paper face-down on
  top. The impact prints the contact patch on the white sheet, and the line
  position can be marked on the paper beforehand. Very precise and clean, but
  soft drop shots may print faintly.

Record results in `data/ground_truth/chalk_template.csv` (copy it per session).
The chalk mark also tells us the real **contact patch radius** (half the mark
width), which is currently an assumption (1.0 cm) in `CourtSpec`.

## 6. Then

```bash
bt calibrate clip.mov --court configs/court_full.yaml --out cam.json   # click keypoints
bt analyze clip.mov --calib cam.json --court configs/court_full.yaml \
           --out results.json --annotate annotated.mp4
bt evaluate results.json --truth data/ground_truth/session1.csv --details
```
