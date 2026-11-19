# Product evolution log

Written automatically by `scripts/hooks/evolution_log.py` (Claude Code hooks): each request, then the conclusions of the work on it.

The entries below up to 2026-11-19 were written by hand when the hook was set up (the hooks start
working in the next Claude Code session); later entries are automatic.

## 2026-11-15 → 2026-11-18 · summary of earlier sessions

* Brief: multi-sport CV platform, pickleball line calls first (speak OUT/FAULT only, 1-3 s delay ok),
  iPhones 16/17 + Androids, 2020 Intel MacBook server, no AGPL/GPL.
* Built: offline pipeline (detection → tracking → kink bounce detection → line call), validated on a
  240 fps clip vs chalk marks (0.7 cm median); live server with browser phones; phone-side detector
  (C++ core shared by iOS, Android, WebAssembly, Mac tests); Expo/React Native app; replay/report tools;
  golden tests.
* Field test 1 (5x scaled yard court): Android could not join (no Wi-Fi, wrong browser), a snake plant
  was detected as the ball, serves missed in evening light; scaled court needs `--court`.

## 2026-11-19 · iOS app on device, field test 2

> Build and install the app on the iPhone; fix orientation and status-bar overlap; field test on a
> full-size court (2 cameras).

### outcome

* iOS app installed via Xcode 26.6 on iOS 27.2 (Developer Mode + trust profile); preview rotation and
  safe-area fixes; Wi-Fi drop counter fixed.
* Hotspot on an IPv6-only carrier: server now listens/advertises IPv6.
* Field test 2 analysed: calibration spoiled by net-top clicks; OUT calls for dead balls/second
  bounces; Mac overloaded by the bounce search; Samsung slow and overheating; cameras badly placed.

## 2026-11-19 · after field test 2

> Explain the net-top issue; why did the Mac get overwhelmed with the native app; send only needed
> data from the phone; why was the Samsung slow; weaker Androids for sections?; auto calibration with
> markers for side A/B; an evolution-log hook; fix the logging gap; a git repo with code, decision
> logs, docs and sample data; build the play state.

### outcome

* Mac: batched bounce search + still-track skip (11.8 → 5.2 ms/frame); phone-side reducer (27% fewer
  frames, 49/50 bounces identical); `--full-rate` to disable.
* Play state + single-camera OUT gate: on a 550 s replay 7 → 3 announced OUTs (all two-camera).
* Calibration: net tops removed, mis-click detection; auto-calibration experimental (synthetic ok,
  real frames 10-25 px off: not in the dashboard yet).
* Android: detection thread priority, 16:9 capture, ARM-only APK.
* Repo committed locally with docs/DECISIONS.md, docs/FIELD_TEST_2_RESULTS.md, data/samples/.

