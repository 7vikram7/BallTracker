# Session 20261120-202244

* **When:** 2026-11-20T20:22:44+0530 → not closed cleanly (–)
* **Code:** commit `5942d70980619124b37f2b6b1bbaa893b2d83e1b` + 1 uncommitted files; bounce 0.4.0, fusion 0.1.0, phone detector edge_color_motion 1.0.0, protocol 2
* **Command:** `~/Vikram/BallTracker/.venv/bin/bt serve --court-scale 0.2`
* **Court:** pickleball_x0.2, 1.22 × 2.68 m
* **Settings:** {"record": false, "phone_reduction": true, "detector_overrides": {}, "hold_s": 0.6, "window_s": 0.08, "corroborate": true}

## Cameras

| camera | kind | device | frames | dropped | clock rtt / ± | calibration | lowest fps | worst latency | disconnects |
|---|---|---|---|---|---|---|---|---|---|
| iphone17 | edge | Apple iPhone 17 | 251355 | 0 (0.0%) | 8 / ±4.2 ms | 2.81 px | 120 | 322 ms | 1 |
| iphone16 | edge | Apple iPhone 16 | 43638 | 0 (0.0%) | 15 / ±7.4 ms | 9.29 px | 120 | 270 ms | 2 |
| redmi | edge | Xiaomi Redmi 8A Dual | 5050 | 0 (0.0%) | 14 / ±7.0 ms | – | 17 | 19 ms | 1 |

## Calls

72 single-camera reports → 61 decisions (11 seen by 2+ cameras): IN 10, OUT 1, UNCERTAIN 34, suppressed (2nd bounce) 16
Spoken: 1. Delay bounce → call: median 0.94 s, max 5.13 s.

| t (s) | call | spoken | p(out) | line | distance | cameras | note |
|---|---|---|---|---|---|---|---|
| 245.41 | UNCERTAIN |  | 0.81 | sideline_right | -10.2 cm | 1 |  |
| 350.45 | IN |  | 0.00 | baseline_A | -5.9 cm | 1 |  |
| 1670.48 | UNCERTAIN |  | 0.21 | kitchen_A | -16.9 cm | 2 |  |
| 1671.64 | UNCERTAIN |  | 1.00 | sideline_right | 5.5 cm | 1 | unconfirmed by iphone16 |
| 1708.00 | UNCERTAIN |  | 1.00 | baseline_A | 32.2 cm | 1 |  |
| 1710.79 | UNCERTAIN |  | 0.30 | kitchen_A | -7.7 cm | 2 |  |
| 1711.52 | IN |  | 0.00 | sideline_right | -5.8 cm | 1 |  |
| 1712.38 | – |  | – |  | – | 1 | secondary bounce |
| 1713.04 | – |  | – |  | – | 1 | secondary bounce |
| 1728.72 | IN |  | 0.00 | sideline_right | -10.3 cm | 1 |  |
| 1730.23 | UNCERTAIN |  | 1.00 | baseline_B | 36.2 cm | 1 |  |
| 1730.88 | UNCERTAIN |  | 1.00 | sideline_right | 24.8 cm | 1 | unconfirmed by iphone16 |
| 1751.23 | IN |  | 0.00 | kitchen_B | -10.9 cm | 1 |  |
| 1752.27 | – |  | – |  | – | 1 | secondary bounce |
| 1752.51 | – |  | – |  | – | 1 | secondary bounce |
| 1752.68 | – |  | – |  | – | 1 | secondary bounce |
| 1759.77 | IN |  | 0.00 | baseline_A | -25.3 cm | 1 |  |
| 1759.77 | IN |  | 0.00 | baseline_B | -25.2 cm | 1 |  |
| 1760.40 | – |  | – |  | – | 1 | secondary bounce |
| 1769.56 | IN |  | 0.00 | kitchen_B | -34.1 cm | 1 |  |
| 1770.25 | – |  | – |  | – | 1 | secondary bounce |
| 1770.60 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1771.41 | UNCERTAIN |  | 0.24 | kitchen_A | -1.1 cm | 1 |  |
| 1771.90 | – |  | – |  | – | 1 | secondary bounce |
| 1778.10 | UNCERTAIN |  | 0.53 | sideline_left | -5.5 cm | 2 |  |
| 1778.77 | UNCERTAIN |  | 1.00 | sideline_left | 21.7 cm | 1 | unconfirmed by iphone16 |
| 1779.24 | – |  | – |  | – | 1 | secondary bounce |
| 1799.59 | IN |  | 0.00 | sideline_left | -9.1 cm | 1 |  |
| 1800.23 | – |  | – |  | – | 1 | secondary bounce |
| 1799.59 | IN |  | 0.00 | sideline_right | -9.3 cm | 1 |  |
| 1814.21 | UNCERTAIN |  | 0.70 | sideline_left | -4.2 cm | 2 |  |
| 1814.88 | UNCERTAIN |  | 1.00 | sideline_left | 72.9 cm | 1 | unconfirmed by iphone16 |
| 1827.03 | UNCERTAIN |  | 1.00 | sideline_left | 21.3 cm | 1 | unconfirmed by iphone16 |
| 1827.03 | UNCERTAIN |  | 1.00 | sideline_right | 20.9 cm | 1 | unconfirmed by iphone17 |
| 1910.93 | OUT | **OUT** | 1.00 | sideline_left | 65.5 cm | 1 |  |
| 1920.27 | UNCERTAIN |  | 0.25 | sideline_right | -0.7 cm | 1 |  |
| 1921.58 | UNCERTAIN |  | 1.00 | baseline_B | 49.5 cm | 1 | unconfirmed by iphone16 |
| 1926.45 | UNCERTAIN |  | 1.00 | sideline_right | 64.2 cm | 1 |  |
| 1933.09 | UNCERTAIN |  | 0.28 | baseline_A | -18.3 cm | 2 |  |
| 1933.75 | UNCERTAIN |  | 1.00 | baseline_B | 110.2 cm | 1 | unconfirmed by iphone17 |
| 1944.73 | UNCERTAIN |  | 1.00 | sideline_right | 59.9 cm | 1 |  |
| 1950.91 | IN |  | 0.00 | kitchen_B | -22.3 cm | 1 |  |
| 1951.69 | – |  | – |  | – | 1 | secondary bounce |
| 1952.17 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1953.01 | UNCERTAIN |  | 0.99 | sideline_right | 2.5 cm | 1 | unconfirmed by iphone16 |
| 1963.33 | UNCERTAIN |  | 0.38 | baseline_A | -11.9 cm | 2 |  |
| 1963.93 | UNCERTAIN |  | 1.00 | baseline_B | 124.6 cm | 1 | unconfirmed by iphone17 |
| 1977.99 | UNCERTAIN |  | 0.41 | kitchen_A | -10.7 cm | 2 |  |
| 1978.77 | UNCERTAIN |  | 1.00 | baseline_B | 31.4 cm | 1 | unconfirmed by iphone16 |
| 2007.02 | UNCERTAIN |  | 0.35 | centreline_A | -18.0 cm | 2 |  |
| 2009.56 | UNCERTAIN |  | 1.00 | baseline_B | 149.8 cm | 1 | unconfirmed by iphone17 |
| 2033.59 | UNCERTAIN |  | 1.00 | baseline_A | 63.6 cm | 1 |  |
| 2035.06 | UNCERTAIN |  | 0.89 | sideline_right | 1.5 cm | 1 |  |
| 2055.08 | UNCERTAIN |  | 1.00 | baseline_B | 54.5 cm | 1 |  |
| 2067.74 | UNCERTAIN |  | 0.09 | centreline_A | -54.3 cm | 2 |  |
| 2068.59 | – |  | – |  | – | 2 | secondary bounce |
| 2069.18 | – |  | – |  | – | 2 | secondary bounce |
| 2070.35 | UNCERTAIN |  | 1.00 | baseline_B | 49.9 cm | 1 | unconfirmed by iphone17 |
| 2076.88 | UNCERTAIN |  | 0.98 | sideline_right | 42.5 cm | 1 |  |
| 2081.30 | UNCERTAIN |  | 1.00 | sideline_right | 8.1 cm | 1 | unconfirmed by iphone16 |
| 2082.15 | – |  | – |  | – | 1 | secondary bounce |

## Calibrations

* iphone17 at 174 s: RMS 1.61 px from 13 points; worst point B_centre_kitchen 3.5 px
* iphone17 at 333 s: RMS 2.81 px from 13 points; worst point B_centre_kitchen 5.6 px
* iphone16 at 1649 s: RMS 9.29 px from 13 points; worst point net_left_ground 23.0 px
