# Live line calls with phones (no app install)

Phones open a web page served by the Mac and stream their camera over Wi-Fi.
The Mac tracks the ball for every camera, fuses what they see, and the
dashboard says **"Out"** or **"Fault"** out loud. Nothing is announced when the
ball is in, or when the system isn't sure.

```
 phone (Safari / Chrome)  ──JPEG + capture time──▶  Mac: bt serve  ──▶  dashboard (speaks OUT)
 phone ...                                          one worker process per camera
```

## 1. Start the server (on the Mac)

```bash
source .venv/bin/activate
bt serve                         # add --record to keep every frame for later replay
```

It prints three addresses:

* **Dashboard**: `http://localhost:8080/dashboard`. Open it on the Mac and click
  **Enable sound** (browsers only allow speech after a click).
* **Phones**: `https://<mac-ip>:8443/phone`. The dashboard also shows a QR code.
* **CA certificate**: `http://<mac-ip>:8080/ca.crt` (optional, see step 2).

The Mac and the phones must be on the **same Wi-Fi**. The first time, macOS
asks whether Python may accept incoming connections: allow it.

## 2. Connect each phone

1. Scan the QR code on the dashboard, or type the phone address in Safari / Chrome.
2. The browser warns that the connection isn't private. That's expected: the
   Mac signs its own certificate. iPhone: *Show Details → visit this website*.
   Android Chrome: *Advanced → Proceed*.
3. Give the camera a **name that describes its mounting position**, e.g.
   `baseline-A-left`. The calibration is saved under that name, so reuse the
   name when the phone goes back to the same spot.
4. Choose 1280×720 and 60 fps (see *Capacity* below). Leave **Ball detection** on
   **On this phone** (default): the page runs the same C++ detector as the app (compiled to
   WebAssembly) and sends only ball positions plus one picture per second, so the Mac can take
   many more phones and Wi-Fi isn't a bottleneck. **On the Mac** sends video instead (the old way).
   Tap **Start streaming** and allow camera access. In phone mode the bar shows *detect* (ms per
   frame); if it is above about 15 ms the phone drops frames: use 960×540.
5. Hold or mount the phone in **landscape**. The screen stays on while streaming.
   Keep the page in front: if you switch apps or lock the phone, it stops.

**Removing the certificate warning (recommended for regular use, and if an
iPhone connects but never streams):** open `http://<mac-ip>:8080/ca.crt` on the
phone.
* iPhone: Settings → General → VPN & Device Management → install
  "BallTracker Local CA", then Settings → General → About → Certificate Trust
  Settings → turn on full trust for it.
* Android: Settings → Security → Encryption & credentials → Install a certificate → CA certificate.

The certificate is created on your Mac (`data/live/tls/`) and its private key
never leaves it. Delete that folder to start over.

### Or: phones with the BallTracker Cam app

Phones with the native app ([mobile/README.md](../mobile/README.md)) find the ball on the
phone and send only its position, so the Mac isn't the limit and iPhones can run at 120–240 fps.
In the app, tap **Scan QR** and scan the dashboard's second code (*Add a phone with the app*), or
type the Mac's address. No certificate is needed. App phones and browser phones can be mixed.

## 3. Calibrate each camera (once per mounting position)

On the dashboard, click **Calibrate** on the camera's card:

1. A snapshot from that phone appears. The list on the right names the court
   points one at a time; the small court diagram shows where each one is.
   **Side A** is the bottom of the diagram; *left/right* are as seen standing
   behind baseline A looking at the net.
   **Side A is one fixed end of the court, the same for every camera.** Pick it once (e.g. the
   end nearest the Mac, or put a towel there) and keep it for the whole session. A camera at the
   B end calibrates its nearest half as **B**, and from there B-left is on *your right* (left/right
   always as seen from behind A). Do not call each camera's own nearest end "A": the cameras then
   disagree by a 180° turn and every call they share becomes UNCERTAIN. The dashboard notices this
   after about 3 bounces both cameras saw and offers **Calibrated from the other end?** → Review
   (the labels are swapped for you) → Calibrate.
2. **Fast way:** click the 4 corners of the half nearest this camera (the two baseline
   corners, then the two kitchen-line corners, A or B as above; roughly is fine; pick the point
   in the list first if it is not the current one), then **Snap to lines**. Every point is placed on the
   painted lines (blue crosses) and the message says how well the lines fit (good: under
   1.5 px). Check the blue points with the magnifier; re-click any that are wrong.
   **By hand:** click each point where the outer edges of the lines meet; skip points you
   can't see; at least 6, spread across the image. (Net-post tops are not used: portable
   posts stand outside the sidelines.)
3. Click **Calibrate**. The server then snaps your points to the painted lines by itself and
   uses the snap when the lines fit well (it says so under the result). Aim for **RMS under
   2 px**. **Above 3 px the camera is not used for calls** (its card says *rough calibration*):
   click the 4 near corners, **Snap to lines**, check, Calibrate. Then click **Check** on the
   camera card: the court lines should sit on the real lines in the live image.

When you save a camera, the other cameras are re-snapped to their own court lines (applied by
itself when the lines fit well, otherwise offered as **Refined calibration ready** → Review).
During play the bounces they see together with the saved camera can refine them further
(also offered for review).

**If a phone moves** (wind, a bump, the mount sagging), the server notices: every 10 s it
compares the camera's picture with the frame it was calibrated on (fences, walls and the net
don't move; players are ignored). A small move (a few to ~80 pixels) is followed automatically
and the card says *moved N px, followed*. A big move, or a picture it can't match (covered, very
dark), puts a red warning at the top of the dashboard: calibrate that camera again.

**Aim each camera to include 1–1.5 m beyond the lines on its side.** Tick **camera coverage**
above the court diagram: green cells are seen by two or more cameras, amber by one, red by none.
The dashboard warns when the strip outside a line is seen by only one camera: an OUT there would
rest on one camera alone, and a camera far away looking across the line can't judge it (it then
stays silent).

A scaled-down floor court works the same way: start the server with `bt serve --court-scale 0.2`
(or `--court my_court.yaml` for a measured court); see [MINI_COURT.md](MINI_COURT.md).

## 4. Play

* **Court screen** (button at the top, or key **B**; **Esc** to leave): the whole window is the
  call, readable from across the court. **Green**: in play / the last bounce was IN. **Red**: OUT.
  **Yellow**: service FAULT. Red and yellow stay for 6 s. **Grey**: not ready (no calibrated
  camera connected). The bottom row shows each camera (green = calling). Tap the screen once to
  turn on the spoken calls.
* **Serves are recognised automatically.** Between points (after an OUT/FAULT, a second bounce,
  the ball being bounced or tossed, or 5 s without play) the next ball that comes over the net
  from behind a baseline is a serve. It is judged against the diagonal service court: kitchen
  (kitchen line included), beyond the baseline or sideline, or **over the centre line into the
  wrong court** → **FAULT**. The server's half (right/left) comes from where the ball's arc meets
  the baseline, or from where the server bounced the ball before serving; when neither is clear,
  only kitchen, baseline and sideline faults are called. **Override ▸** in the header forces the
  next bounce to be judged as a particular serve.
* Each call appears on the court diagram and in the **Calls** table (with *serve* / *rally*),
  the nearest line and the distance from it. Typical delay: 1–1.5 s.
* **When it stays silent**: the ball was in; or the estimate was too uncertain (*unsure*); or only
  one camera saw a bounce that another camera could also see (*OUT? (unconfirmed)*); or it was a
  second bounce; or a check failed (*OUT? (checked)*; hover for why): the ball would have been
  faster than 90 km/h, it was ball handling far outside the court between points, or one far
  camera was looking across the line.

### Weak extra phones (720p, 30 fps)

Use them as extras next to two good phones, never instead of one. Aim each weak phone at **its
own end only**: the near baseline, the kitchen line and the sideline on its side, plus 1-1.5 m
outside that sideline and baseline. Leave the far end out of its frame. On field test 3 the
Nothing at 30 fps caught 17% of the bounces on its own half and 1% beyond 14 m; it helped as the
second camera on the right sideline, which nothing else covered well.

The camera card shows each phone's hit rate: the share of bounces the other cameras saw that it
caught too, by distance (*catches near 17% of 208, mid 5% of 205 ...*). A camera that catches
fewer than 40% of the bounces at a given distance doesn't veto a lone camera's OUT there just by
missing it. Other cameras still do.

## 5. Capacity on this Mac (2020 Intel i5, 4 cores)

With **Ball detection: On this phone** (the app, or the browser page's on-phone mode) the Mac only
tracks and calls. Measured on field test 3's recording (2026-11-21, 45 minutes of play) with
the faster tracking of that day, in cores per camera (typical / 90% of the time below / peak):

| camera | typical | p90 | peak |
|---|---|---|---|
| iPhone, 120 fps | 0.25 | 0.55 | 0.9 |
| Android, 60 fps | 0.25 | 0.33 | 0.5 |
| Android, 30 fps | 0.01 | 0.03 | 0.1 |

Four cameras need about 1.5 cores at the 90th percentile, out of 4: they fit. Each camera has its
own process, so what matters is that no single camera reaches a whole core (the iPhone did,
20% of the time, before these changes). The dashboard shows the Mac's load under the court
diagram, and every session logs it (`host_stats`).

* **Close other heavy apps during play.** A code editor's window used 1.4 cores of the Mac while
  idle in the background on the day of field test 3: more than all cameras together.
* Each camera runs in its own process. If one camera's processing falls behind (cluttered view:
  sun stripes, yellow-green clothes), it skips its periodic bounce search until it has caught up
  (each track still gets its search when it ends), and drops frames more than 1.5 s old. The card
  shows *catching up* or *N s behind*.
* Don't use a camera phone as the Wi-Fi hotspot: it heats up, drains its battery, and (on an
  IPv6-only hotspot) the app on that phone can't reach the Mac.

In **On the Mac** (video) mode each camera needs about 1.3 CPU cores at 1280×720 / 60 fps (JPEG
decode + detection): 2 such cameras keep up; with more, use 30 fps or 960×540.

Phones in a browser can't record 240 fps; 60 fps is the practical maximum.
Our experiments (docs/PHASE0_RESULTS.md) show 60 fps gives centimetre accuracy
when the ball is sharp. **Light matters most**: bright light makes the phone
use a short exposure, so the ball doesn't smear.

## 6. Try it without phones

```bash
bt live-demo                     # server + 2 simulated phones on a synthetic rally, scored vs truth
bt live-demo --keep              # then open http://localhost:8090/dashboard
bt fakephone --server ws://localhost:8080 --video clip.mov --name test-cam   # stream a file like a phone
```

Result of `bt live-demo` on the Intel Mac (2 cameras, 60 fps, 8 bounces): 8/8
called and confirmed by both cameras, 0 false calls, median position error
0.8 cm, median delay 0.4 s.

## 7. Where things are saved

```
data/live/
  calibration/<camera>.json         camera models (reused across sessions)
  tls/                              certificate authority + server certificate
  sessions/<date-time>/events.jsonl every report, call, connection (one JSON per line)
  sessions/<date-time>/<camera>/    with --record: frames.bin + index.csv (all frames, timestamps)
```

## 8. Revisit a session later

```bash
bt sessions                                    # list sessions: length, cameras, decisions, recorded?, code commit
bt report data/live/sessions/<id> --marks docs/field_test_marks.csv   # writes <id>/report.md
bt replay data/live/sessions/<id>              # re-run with today's code; shows calls that changed
```

Each session folder keeps `session.json` (when, which code commit and algorithm versions,
settings, and a closing summary per camera), `events.jsonl` (connections with device/app
details, every calibration with its clicked points and per-point errors, camera health every
5 s, every report and call, serve-button changes) and `calibration/` (the camera models used).
Replays need `--record` (app phones always replay exactly from their detections).

## Troubleshooting

| Symptom | Fix |
|---|---|
| Phone page says camera access isn't available | Open it with **https://** (port 8443), not http. |
| iPhone page loads but status stays "connecting" | Install and trust the CA certificate (step 2). |
| Camera card: *processed* fps below *in* | The Mac can't keep up: lower fps/resolution, or fewer cameras. |
| Calls appear but none are announced | Click **Enable sound** on the dashboard. |
| "frame size differs from calibration" | The phone changed resolution or orientation: recalibrate. |
| Clock *rtt* above ~20 ms | Weak Wi-Fi. Move the router closer or use 5 GHz. |
