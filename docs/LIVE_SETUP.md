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
3. Click **Calibrate**. Aim for **RMS under 2 px**. Then click **Check** on the camera card: the court lines
   should sit on the real lines in the live image.

When you save a camera, the other cameras are re-checked against their own court lines, and
during play the bounces they see together with the saved camera refine them. If a better
calibration is found, the camera card shows **Refined calibration ready** with how much it
improves; **Review** opens it for checking, **Dismiss** ignores it. Nothing changes without you.

If the phone moves (knocked, re-mounted), calibrate again. A scaled-down floor court works the
same way: start the server with `bt serve --court-scale 0.2` (or `--court my_court.yaml` for a
measured court); see [MINI_COURT.md](MINI_COURT.md).

## 4. Play

* **Rally** is the default. Before a serve, click the matching **Serve**
  button (e.g. *Serve A·right*): the next bounce is judged against the
  diagonal service court (kitchen line counts as a fault), then it goes back to
  rally automatically.
* Each call appears on the court diagram and in the **Calls** table, with
  p(out), the nearest line and the distance from it. Typical delay: 0.5–2 s.
* **When it stays silent**: the ball was in; or the estimate was too
  uncertain (*unsure*); or only one camera saw a bounce that another camera
  could also see (*OUT? (unconfirmed)*); or it was a second bounce.

## 5. Capacity on this Mac (2020 Intel i5)

With **Ball detection: On this phone** (browser or app) the Mac only tracks and calls: about 0.2 cores
per camera, so the limits below apply only to phones in **On the Mac** (video) mode.


Each camera needs about 1.3 CPU cores at 1280×720 / 60 fps (JPEG decode +
detection). Measured: **2 cameras at 60 fps keep up** (no dropped frames when the
Mac isn't busy with other work). With 3–4 cameras, use 30 fps or 960×540, or
use an Apple Silicon Mac. The camera card shows *in* and *processed* fps and
*drops*: if *processed* stays below *in*, lower the frame rate.

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
