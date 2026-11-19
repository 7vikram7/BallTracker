# BallTracker Cam (React Native / Expo app)

The phone films the court, **finds the ball itself** (C++ detector, up to 240 fps
on iPhone) and sends the Mac only the ball positions (about 10 KB/s instead of about
7 MB/s of video), plus one full-size picture per second for the dashboard and
calibration. The Mac (`bt serve`) still tracks, fuses the cameras and makes the
calls. Browser phones and app phones can be mixed in one session.

```
mobile/
  App.tsx, src/screens/      UI (TypeScript): Connect screen, Camera screen
  src/core/*.js              app logic, plain JS + JSDoc types, runs in Node too:
                             protocol.js (wire format), edgeClient.js (WebSocket + clock sync replies),
                             session.js (camera <-> server), serverAddress.js, simCamera.js
  modules/ball-camera/       local Expo native module
    cpp/ballcore.{h,cpp}     the detector (C++), shared by iOS, Android and the Mac tests
    ios/                     Swift: AVFoundation capture (CaptureEngine), preview view; BCDetector.mm bridge
    android/                 Kotlin: CameraX capture, preview view; JNI bridge + CMake
    src/                     TypeScript API; falls back to a simulated camera if the native code isn't built in
  test/                      Node tests (no npm packages needed): `node --test test/*.test.js`
```

## What is tested, and what isn't yet

| Part | Status |
|---|---|
| C++ detector | Built on the Mac; matches the Python reference exactly (all candidates, < 0.0001 px) on synthetic video and on the real 240 fps clip, in BGR, BGRA (iOS) and RGBA (Android) layouts |
| JNI bridge + Android CMake | Builds for Android (arm64) in the APK |
| `src/core` (protocol, client, session) | Unit tests with mock camera and mock WebSocket; integration test against the real Python server (8/8 bounces, OUT calls reach the app) |
| Swift (iOS) | Syntax-checked only. **Not compiled yet**: needs Xcode 26.4+ (Expo 58), which needs macOS Tahoe on this Mac |
| Kotlin (Android) | **Compiles**: `assembleDebug` succeeded (2026-11-18); not yet run on a phone |
| Screens (TSX) | Type-checked (`npm run typecheck`, strict, including the JS core) |

Expect a few compile fixes on the first build; send me the errors.

## Set up at home (one time)

Requirements found during setup: **Node ≥ 22.13** (Expo 58; Homebrew's Node 26 is used via `scripts/env.sh`),
**iOS 16.4+** on the phones, **JDK 17**, Android SDK platform 37, build tools 37.0.0, NDK 27.1.12297006.


1. **Xcode** from the App Store. Open it once, then Xcode › Settings › Accounts › add your
   Apple ID (free; no $99 needed for your own phones). Install CocoaPods: `brew install cocoapods`.
2. **Android** (optional, for the spare phones): Android Studio, which installs the SDK and asks
   you to accept its licences. JDK 17 is bundled with Android Studio.
3. In this folder (every new terminal: `source scripts/env.sh` first; it selects Node 26,
   Java 17 and the Android SDK installed on this Mac, without changing system settings):
   ```bash
   cd mobile
   source scripts/env.sh
   npm install
   npx expo install --fix     # aligns package versions with the Expo SDK
   npm test                   # core tests (also run by the Python test suite)
   npm run typecheck          # TypeScript check of screens + core
   ```

## Install on an iPhone (free Apple ID)

1. iPhone: Settings › Privacy & Security › **Developer Mode** on (it restarts). Connect it by cable.
2. `npx expo run:ios --device` and pick the iPhone. The first time, if signing fails:
   open `ios/BallTrackerCam.xcworkspace` in Xcode › target › Signing & Capabilities ›
   Team = *your name (Personal Team)*. If the bundle ID is taken, change
   `ios.bundleIdentifier` in `app.json` (e.g. add your initials) and run again.
3. iPhone: Settings › General › VPN & Device Management › trust your developer certificate.
4. With a free Apple ID the app **stops opening after 7 days**: just run step 2 again.

Android: enable USB debugging, then `npx expo run:android --device`.

Quick check without building anything: `npx expo start` and open it in **Expo Go**. The
native module isn't in Expo Go, so the app uses a **simulated camera**; that's enough to test
connecting to the server and the dashboard.

## Use

1. On the Mac: `bt serve` (as before). The dashboard shows a second QR code, **"Add a phone
   with the app"**.
2. In the app: **Scan QR** (or type the Mac's address), enter the camera name
   (its mounting position, e.g. `baseline-A-left`), choose resolution and frame rate, **Start camera**.
3. Dashboard: the camera appears with an *app* tag. **Calibrate** it as before (the snapshot is
   the phone's full-size preview).
4. In bright light, tap the exposure button to **Shutter 1/1000** (or 1/2000): it fixes a short
   shutter and raises ISO, so the ball doesn't smear. The button shows if ISO hit its limit (too dark).
5. Leave the app in front with the screen on (it keeps the screen awake).

The camera screen shows camera fps, processed fps, detection time per frame, ball
candidates per second, uplink, temperature and battery, and flashes **OUT / FAULT** when
the Mac calls one. Warnings appear if the phone can't keep up, gets hot, isn't calibrated,
or loses the connection.

## First device test: checklist

1. It builds and opens; the Connect screen remembers your settings.
2. Camera screen: preview visible; *camera fps* ≈ the chosen rate (try 60, then 120, 240).
3. *processed fps* = *camera fps*, and *detect ms* well under the frame interval
   (4.2 ms at 240 fps, 8.3 ms at 120). If not, use 120 fps (or tell me: there are speed-ups ready,
   e.g. 4×4 binning at 240 fps).
4. Dashboard: the card says *app*, the thumbnail updates every second, *server fps* ≈ phone fps.
5. Calibrate; throw a ball: the yellow ball marker follows it on the thumbnail, and bounces appear.
6. Shutter 1/1000 outdoors: the ball looks round, not streaked, in the preview.
7. Run 20 minutes: temperature stays *nominal/fair*, no dropped frames.

## Notes

* Frames stay in the camera's native landscape orientation; the app locks the screen to one
  landscape orientation so the calibration never rotates. Recalibrate if you re-mount the phone.
* Phone timestamps come from the camera sensor, in the same clock the app answers the
  server's clock-sync pings with, so cameras line up to about a millisecond.
* The app talks plain `ws://` to the Mac on the local network (port 8080): no certificate needed.
* Android phones usually can't process more than 60 fps; use them as extra 30–60 fps cameras.
