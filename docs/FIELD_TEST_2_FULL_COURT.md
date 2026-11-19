# Field test 2: full-size court, 4 cameras

**Goal:** the first real numbers on a regulation court: do bounces get detected, fused across
cameras and called correctly, live, with phones finding the ball themselves?

## Before leaving

* **Network (no Wi-Fi at the court): one iPhone's Personal Hotspot.**
  1. Turn on Personal Hotspot on one iPhone (it can still be a camera; plug it into a power bank).
  2. Join it from the Mac and every other phone. Older Androids that can't see it need
     **Maximize Compatibility** (2.4 GHz) turned on in the hotspot settings.
  3. **Only then** start `bt serve`: the Mac's address changes (172.20.10.x) and the QR code follows it.
  4. Phones show the certificate warning again (new address) unless the CA certificate is installed.
  * An iPhone hotspot takes about 5 devices: the Mac + 3 other cameras when the hotspot phone is the 4th.
  * Use **On this phone** mode on every camera: video mode (about 7 MB/s per phone) would overload a hotspot.
  * Camera traffic stays local (no mobile data); stop big syncs on the Mac.
  * **Try it at home first**: hotspot on, Mac and one phone joined, `bt serve`, open the phone page.
* **Android:** be on the hotspot (Wi-Fi icon showing, not just mobile data) and open links in
  **Chrome**, not the phone maker's browser; at the certificate warning: *Advanced › Proceed*.
* Charge everything; take power banks and the Mac charger. Tripods/clamps reaching 2 m or more.
* Android phones: install the app at home, in Chrome on the phone: `http://<mac-ip>:8080/app.apk`
  (the dashboard shows the link). Allow "install unknown apps" for Chrome when asked.
  If the app misbehaves, the web link works on Android too.

## At the court

1. Mac: `bt serve --record` (the regulation court is the default: no `--court` needed).
   Open the dashboard; click **Enable sound**.
2. **Placement (4 cameras):** every line should be seen by at least 2 cameras (needed for the
   "two cameras must agree before an OUT" rule).
   * 2 cameras behind the baselines, high (2 m+), centred, each looking down the court.
   * 2 cameras at the sides near the net line, ~1–1.5 m high, one looking at each half.
   * Sun behind or beside the cameras, never in front. **Nothing yellow-green in view**
     (plants, bags, shirts, balls lying around): the dashboard's *clutter* line warns when a
     camera sees more than ~2.5 ball candidates per frame.
   * Each camera sees its whole half, with a margin: no cut-off corners.
3. **Phones:**
   * iPhones: scan the dashboard's first QR (phone camera) → page → **Ball detection: On this
     phone**, 1280×720, 60 fps, **landscape**, then Start. The bar should show *capture* ≈ 60 and
     *detect* a few ms. If capture shows 30, the light is too low for 60 fps.
   * Android with the app: open it, **Scan QR** on the dashboard's *app* code (or type the Mac's
     address), name, 1280×720, 30 or 60 fps, Start, then tap the exposure button to
     **Shutter 1/1000** in daylight.
4. **Calibrate** each camera on the dashboard (net-post tops help most). Aim for RMS < 2 px; redo
   anything above 3 px. Then **Check**: the drawn lines must sit on the real lines.
5. Glance at each card: *processed* ≈ *in*, drops 0, clutter < 2.5, rtt < 20 ms.

## What to do (about 60 minutes)

* **Chalk drill (most useful, 20–30 bounces):** drop/throw near baselines and sidelines;
  10 clearly in, 10 clearly out, 10 within 5 cm. Measure each mark (signed distance to the line's
  outer edge, + = out) into `docs/field_test_marks.csv`. Say the bounce number out loud.
* **Serves (15+):** press the matching **Serve** button before each serve; include some faults
  into the kitchen and long.
* **Rallies (15 min):** normal play.
* A spare phone filming the whole thing with sound is the referee.

## Afterwards

```bash
bt sessions
bt report data/live/sessions/<id> --marks docs/field_test_marks.csv
```

Send me the session folder (detections are recorded for every on-phone camera, about 40 MB per
camera-hour; `--record` adds a preview every 2 s, about 250 MB per camera-hour), the marks sheet and the referee video. Every session can be replayed with later
code (`bt replay`), so even a rough session is useful data.
