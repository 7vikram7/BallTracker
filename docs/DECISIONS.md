# Decision log

Product and engineering decisions, newest first, with the reason and the evidence. The raw
request/outcome history is in [evolution/LOG.md](evolution/LOG.md) (written automatically by a
Claude Code hook); this file keeps only what was decided and why.

## 2026-11-19 · after field test 2 (full-size court)

| Decision | Why / evidence |
|---|---|
| **Play state**: only bounces of a ball in play are announced (dead balls, second bounces and, at the start of play, slow non-shots stay silent). `balltracker/live/playstate.py` | Field test 2 announced OUT for pre-serve bounces and for second bounces of unreturned balls 1.4-1.9 m behind the baseline. Replay of 550 s: 7 announced OUTs before, 3 after (all confirmed by both cameras). |
| **One camera alone may not announce an OUT** when its uncertainty across the line is > 15 cm. | The far-baseline calls came from one phone 16 m away looking along the court: ±25 cm, possibly biased. 0 wrong OUT is objective #1; silence costs less. |
| **Net-top points removed from calibration clicking**; calibration now names likely mis-clicks (leave-one-out). | Portable net posts stand ~30 cm outside the sidelines and higher than the net; clicking them gave 13-32 px errors. iPhone 9.3 → 2.7 px RMS without them. |
| **Bounce search batched, still tracks skipped** (server). | 88% of the Mac's time was the bounce search (22 trial fits per candidate split, 12x a second, on every track, including clutter). 11.8 → 5.2 ms/frame on the field iPhone stream; identical results (golden tests unchanged). |
| **Phone-side reduction** (`mobile/src/core/reducer.js`): still clutter dropped; full frame rate only around direction changes, ~30 fps elsewhere. `bt serve --full-rate` turns it off. | The user's principle: the phone sees everything, sends only what is needed. On field data: 27% fewer frames, 49/50 bounces kept at identical positions. Stricter settings lost bounces, so the conservative one is the default. Most of the Mac's relief came from the server fix above. |
| **Server listens on IPv6 too** and shows IPv6 addresses when the hotspot gives no reachable IPv4. | An iPhone hotspot on an IPv6-only carrier gives clients only a 192.0.0.x CLAT address that peers cannot reach. A phone cannot reach a device on its *own* hotspot that way either: the hotspot phone should not be a camera (or use an Android hotspot). |
| **Android detection thread at display priority; 16:9 capture.** | Samsung flagship: 12-27 ms/frame vs iPhone 4 ms, overheated, battery 45 → 3%. Likely efficiency cores + 1920x1440 (4:3) frames. To be verified on device. |
| **Auto-calibration kept experimental** (not in the dashboard). | Works on synthetic courts (2-3 px); on field-test frames 10-25 px errors at far corners (net tapes, distortion). A wrong pre-fill that looks right is worse than none. |
| **Evolution log via Claude Code hooks** (`.claude/settings.json`, `scripts/hooks/evolution_log.py`). | Requested: keep a history of requests and conclusions with the code. |
| **Git repository with sample data** (`data/samples/`), large media excluded. | Any clone must be able to run the tests. Camera images are not committed (they show people). |

## 2026-11-18 · browser and app on-phone detection

| Decision | Why / evidence |
|---|---|
| C++ detector compiled to WebAssembly for the browser phone page. | Test with many phones without installing apps. iPhone: 2.4-2.8 ms/frame in the browser. |
| FrameClock snaps browser timestamps to the frame grid (browser cameras only). | ±3 ms timestamp jitter randomly lost 1-2 of 5 bounces; with the fit, 5/5. |
| Detections always recorded for on-phone cameras; video only with `--record`. | Tiny (~40 MB per camera-hour) and makes every session replayable (`bt replay`). |
| Full court model needed for scaled courts (`--court`). | With the regulation model on a 5x smaller court, implied gravity is 5x and the physics check rejects real bounces. |

## 2026-11-17 and before · foundations

| Decision | Why |
|---|---|
| Phones run the detector; the Mac fuses and calls (protocol 2: coordinates + confidence, images only when useful). | A 2020 Intel MacBook cannot decode several 60-240 fps video streams. |
| One C++ core (`ballcore`) for iOS, Android, WebAssembly and Mac tests, bit-exact with the Python reference (`-ffp-contract=off`). | One algorithm, testable everywhere; golden tests catch any drift. |
| React Native (Expo) app rather than two native apps. | One UI codebase; native code only for camera + detector. |
| Speak only OUT / FAULT; 1-3 s delay acceptable. | What players need from a line judge. |
| No AGPL/GPL dependencies (e.g. no Ultralytics YOLO). Avoid the $99 Apple fee where possible. | Licensing freedom for a future club product. |
| Priorities: line calling → stats → coaching. | |
