# Session 20261118-171657

* **When:** 2026-11-18T17:16:57+0530 → 2026-11-18T17:42:44+0530 (1547 s)
* **Code:** commit `no commits` + 14 uncommitted files; bounce 0.3.0, fusion 0.1.0, phone detector edge_color_motion 1.0.0, protocol 2
* **Command:** `/Users/<user>/Vikram/BallTracker/.venv/bin/bt serve`
* **Court:** pickleball, 6.10 × 13.41 m
* **Settings:** {"record": false, "detector_overrides": {}, "hold_s": 0.6, "window_s": 0.08, "corroborate": true}

## Cameras

| camera | kind | device | frames | dropped | clock rtt / ± | calibration | lowest fps | worst latency | disconnects |
|---|---|---|---|---|---|---|---|---|---|
| cam-chgf | edge | Mozilla/5.0 (iPhone; CPU iPhone OS 26_6_ | 35682 | 556 (1.6%) | 4 / ±2.1 ms | 4.54 px | 41 | 6075 ms | 2 |
| cam-s0cv | edge | Mozilla/5.0 (iPhone; CPU iPhone OS 18_7  | 34912 | 0 (0.0%) | 5 / ±2.5 ms | 1.92 px | 22 | 2046 ms | 3 |

## Calls

23 single-camera reports → 21 decisions (2 seen by 2+ cameras): IN 10, OUT 3, UNCERTAIN 8
Spoken: 3. Delay bounce → call: median 1.04 s, max 2.39 s.

| t (s) | call | spoken | p(out) | line | distance | cameras | note |
|---|---|---|---|---|---|---|---|
| 560.02 | UNCERTAIN |  | 0.07 | kitchen_B | -26.5 cm | 1 |  |
| 1145.01 | IN |  | 0.00 | centreline_B | -161.7 cm | 1 |  |
| 1148.14 | IN |  | 0.00 | centreline_A | -169.6 cm | 1 |  |
| 1151.16 | IN |  | 0.00 | centreline_B | -305.3 cm | 1 |  |
| 1152.21 | IN |  | 0.00 | centreline_A | -290.3 cm | 1 |  |
| 1153.26 | IN |  | 0.00 | centreline_B | -181.1 cm | 1 |  |
| 1157.62 | IN |  | 0.00 | centreline_B | -160.0 cm | 1 |  |
| 1168.26 | IN |  | 0.00 | kitchen_A | -121.3 cm | 1 |  |
| 1230.43 | UNCERTAIN |  | 1.00 | sideline_right | 210.8 cm | 1 | unconfirmed by cam-s0cv |
| 1255.99 | UNCERTAIN |  | 0.67 | sideline_right | 20.5 cm | 1 |  |
| 1257.63 | OUT | **OUT** | 0.99 | baseline_A | 209.5 cm | 1 |  |
| 1297.07 | UNCERTAIN |  | 1.00 | sideline_right | 204.6 cm | 1 | unconfirmed by cam-s0cv |
| 1312.53 | UNCERTAIN |  | 1.00 | baseline_B | 168.1 cm | 1 | unconfirmed by cam-s0cv |
| 1370.07 | OUT | **FAULT** | 1.00 | centreline_A | 86.6 cm | 2 |  |
| 1402.28 | UNCERTAIN |  | 1.00 | centreline_A | 134.3 cm | 1 | unconfirmed by cam-s0cv |
| 1408.46 | UNCERTAIN |  | 1.00 | sideline_right | 882.9 cm | 1 | unconfirmed by cam-s0cv |
| 1413.42 | IN |  | 0.00 | baseline_A | -94.7 cm | 1 |  |
| 1454.53 | OUT | **FAULT** | 1.00 | baseline_B | 1027.4 cm | 1 |  |
| 1480.80 | UNCERTAIN |  | 1.00 | centreline_B | 490.2 cm | 1 | unconfirmed by cam-s0cv |
| 1498.41 | IN |  | 0.00 | sideline_left | -86.9 cm | 1 |  |
| 1503.55 | IN |  | 0.00 | kitchen_A | -92.4 cm | 2 |  |

## Warnings

* 1522.8 s cam-s0cv: worker restarted
* 1522.8 s cam-chgf: worker restarted

## Calibrations

* cam-s0cv at 503 s: RMS 1.92 px from 14 points; worst point A_centre_kitchen 3.1 px
* cam-chgf at 1067 s: RMS 4.54 px from 14 points; worst point B_left_corner 8.1 px
