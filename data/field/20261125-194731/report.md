# Session 20261125-194731

* **When:** 2026-11-25T19:47:31+0530 → 2026-11-25T21:00:41+0530 (4390 s)
* **Code:** commit `3e96b4f35ecef0f8a7110c7701e4ecd9a818c1bd`; bounce 0.4.0, fusion 0.1.0, phone detector edge_color_motion 1.0.0, protocol 2
* **Command:** `~/Vikram/BallTracker/.venv/bin/bt serve --record`
* **Court:** pickleball, 6.10 × 13.41 m
* **Settings:** {"record": true, "phone_reduction": true, "detector_overrides": {}, "hold_s": 0.6, "window_s": 0.08, "corroborate": true, "play_mode": "match", "weak_rate": 0.4}

## Cameras

| camera | kind | device | frames | dropped | clock rtt / ± | calibration | lowest fps | worst latency | disconnects |
|---|---|---|---|---|---|---|---|---|---|
| samsung | edge | samsung SM-S948B | 118950 | 0 (0.0%) | 21 / ±10.3 ms | 1.61 px | 24 | 261 ms | 2 |
| iphone17 | edge | Apple iPhone 17 | 319388 | 0 (0.0%) | 6 / ±3.2 ms | 0.05 px | 120 | 261 ms | 2 |
| iphone15pro | edge | Apple iPhone 15 Pro | 192433 | 0 (0.0%) | 16 / ±7.8 ms | 0.74 px | 120 | 458 ms | 2 |

## Calls

1769 single-camera reports → 1321 decisions (405 seen by 2+ cameras): IN 561, OUT 29, UNCERTAIN 500, suppressed (2nd bounce) 231
Spoken: 29 (OUT 26, FAULT 3); serves recognised: 68. Delay bounce → call: median 1.27 s, max 3.03 s.

| t (s) | call | spoken | p(out) | line | distance | cameras | note |
|---|---|---|---|---|---|---|---|
| 201.12 | IN |  | 0.00 | sideline_right | -103.9 cm | 1 |  |
| 211.26 | UNCERTAIN |  | 0.73 | sideline_left | -21.3 cm | 1 |  |
| 211.83 | – |  | – |  | – | 1 | secondary bounce |
| 221.50 | UNCERTAIN |  | 1.00 | sideline_left | 117.9 cm | 1 | unconfirmed by samsung |
| 223.38 | UNCERTAIN |  | 1.00 | sideline_left | 82.6 cm | 1 |  |
| 246.99 | UNCERTAIN |  | 0.06 | kitchen_B | -125.5 cm | 1 |  |
| 249.21 | IN |  | 0.00 | baseline_B | -13.7 cm | 1 |  |
| 255.59 | UNCERTAIN |  | 1.00 | baseline_A | 105.2 cm | 1 | unconfirmed by samsung |
| 259.30 | UNCERTAIN |  | 1.00 | sideline_left | 291.1 cm | 1 | silent: one camera, flight not measured (speed 36 +- 36 m/s) |
| 260.12 | UNCERTAIN |  | 0.73 | baseline_A | -85.2 cm | 1 |  |
| 402.47 | UNCERTAIN |  | 0.91 | baseline_B | 305.6 cm | 1 |  |
| 453.74 | UNCERTAIN |  | 1.00 | sideline_right | 393.0 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 455.78 | UNCERTAIN |  | 1.00 | baseline_B | 348.9 cm | 1 |  |
| 476.00 | UNCERTAIN |  | 0.95 | baseline_B | 164.3 cm | 1 |  |
| 488.53 | UNCERTAIN |  | 1.00 | sideline_left | 56.4 cm | 1 | silent: implausible speed (at least 27 m/s) |
| 626.84 | UNCERTAIN |  | 1.00 | baseline_A | 142.8 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 627.19 | OUT | **OUT** | 1.00 | baseline_A | 59.2 cm | 1 |  |
| 629.98 | UNCERTAIN |  | 0.90 | baseline_A | 12.6 cm | 1 |  |
| 634.97 | UNCERTAIN |  | 1.00 | baseline_A | 123.8 cm | 1 |  |
| 636.21 | UNCERTAIN |  | 1.00 | sideline_right | 333.7 cm | 1 | unconfirmed by iphone17 |
| 658.23 | IN |  | 0.00 | kitchen_A | -140.0 cm | 1 |  |
| 660.81 | UNCERTAIN |  | 1.00 | sideline_right | 392.2 cm | 1 | unconfirmed by iphone17 |
| 678.71 | IN |  | 0.00 | centreline_A | -231.1 cm | 1 |  |
| 691.84 | IN |  | 0.00 | sideline_left | -97.1 cm | 1 |  |
| 721.75 | IN |  | 0.00 | kitchen_B | -130.4 cm | 1 |  |
| 724.05 | IN |  | 0.04 | centreline_B | -52.0 cm | 1 |  |
| 733.15 | IN |  | 0.00 | kitchen_B | -115.3 cm | 1 |  |
| 734.07 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 759.56 | IN |  | 0.00 | kitchen_B | -125.0 cm | 1 |  |
| 766.31 | UNCERTAIN |  | 1.00 | sideline_right | 387.3 cm | 1 | unconfirmed by iphone17 |
| 766.83 | IN |  | 0.00 | sideline_right | -89.0 cm | 1 |  |
| 774.47 | UNCERTAIN |  | 1.00 | sideline_left | 53.0 cm | 1 |  |
| 784.29 | IN |  | 0.00 | sideline_left | -34.7 cm | 1 |  |
| 788.38 | IN |  | 0.00 | kitchen_B | -86.2 cm | 1 |  |
| 806.92 | IN |  | 0.00 | centreline_B | -136.0 cm | 1 |  |
| 810.34 | IN |  | 0.00 | kitchen_B | -121.2 cm | 1 |  |
| 812.45 | UNCERTAIN |  | 1.00 | baseline_A | 21.9 cm | 1 | unconfirmed by iphone17 |
| 812.70 | OUT | **OUT** | 1.00 | sideline_left | 12.8 cm | 1 |  |
| 814.32 | IN |  | 0.00 | sideline_left | -44.7 cm | 1 |  |
| 818.39 | UNCERTAIN |  | 1.00 | baseline_A | 116.7 cm | 1 |  |
| 821.64 | OUT | **OUT** | 1.00 | sideline_left | 56.7 cm | 1 |  |
| 837.23 | IN |  | 0.00 | centreline_B | -240.2 cm | 1 |  |
| 837.84 | IN |  | 0.00 | kitchen_B | -41.2 cm | 1 |  |
| 844.49 | IN |  | 0.00 | centreline_A | -164.3 cm | 2 |  |
| 844.18 | UNCERTAIN |  | 1.00 | sideline_left | 30.6 cm | 1 |  |
| 844.93 | – |  | – |  | – | 1 | secondary bounce |
| 846.08 | IN |  | 0.00 | sideline_right | -76.1 cm | 1 |  |
| 846.20 | IN |  | 0.00 | kitchen_B | -160.2 cm | 1 |  |
| 847.07 | OUT | **OUT** | 1.00 | sideline_left | 4.1 cm | 1 |  |
| 850.50 | IN |  | 0.00 | sideline_right | -23.7 cm | 1 |  |
| 860.71 | IN |  | 0.00 | sideline_right | -50.5 cm | 1 |  |
| 862.68 | IN |  | 0.00 | sideline_left | -26.1 cm | 1 |  |
| 864.33 | UNCERTAIN |  | 0.32 | sideline_left | -3.1 cm | 1 |  |
| 864.78 | – |  | – |  | – | 1 | secondary bounce |
| 871.50 | UNCERTAIN |  | 0.99 | baseline_B | 36.5 cm | 1 |  |
| 875.56 | UNCERTAIN |  | 1.00 | sideline_right | 369.0 cm | 1 |  |
| 875.90 | – |  | – |  | – | 1 | secondary bounce |
| 876.43 | – |  | – |  | – | 1 | secondary bounce |
| 879.15 | UNCERTAIN |  | 1.00 | baseline_A | 46.9 cm | 1 |  |
| 880.18 | IN |  | 0.00 | sideline_right | -69.2 cm | 1 |  |
| 883.18 | UNCERTAIN |  | 1.00 | sideline_left | 46.8 cm | 1 | unconfirmed by samsung |
| 884.15 | UNCERTAIN |  | 0.12 | centreline_A | -228.8 cm | 2 |  |
| 884.77 | IN |  | 0.00 | sideline_right | -76.0 cm | 1 |  |
| 885.41 | – |  | – |  | – | 1 | secondary bounce |
| 885.89 | – |  | – |  | – | 1 | secondary bounce |
| 893.90 | IN |  | 0.00 | centreline_A | -191.2 cm | 1 |  |
| 897.55 | UNCERTAIN |  | 1.00 | baseline_A | 69.0 cm | 1 |  |
| 898.95 | IN |  | 0.00 | baseline_B | -101.1 cm | 1 |  |
| 900.44 | IN |  | 0.00 | sideline_right | -71.6 cm | 1 |  |
| 901.28 | IN |  | 0.00 | sideline_left | -52.3 cm | 1 |  |
| 902.23 | IN |  | 0.00 | sideline_right | -116.3 cm | 1 |  |
| 912.54 | IN |  | 0.00 | baseline_A | -44.6 cm | 1 |  |
| 913.30 | IN |  | 0.00 | sideline_right | -142.1 cm | 2 |  |
| 914.98 | IN |  | 0.00 | sideline_left | -66.0 cm | 1 |  |
| 915.94 | IN |  | 0.00 | kitchen_B | -108.3 cm | 1 |  |
| 916.49 | UNCERTAIN |  | 1.00 | sideline_left | 22.1 cm | 1 |  |
| 916.73 | UNCERTAIN |  | 0.33 | kitchen_A | -2.7 cm | 1 |  |
| 918.70 | IN |  | 0.00 | centreline_A | -167.1 cm | 1 |  |
| 919.55 | IN |  | 0.00 | kitchen_A | -82.2 cm | 1 |  |
| 919.87 | OUT | **OUT** | 1.00 | sideline_left | 85.3 cm | 1 |  |
| 920.29 | IN |  | 0.00 | baseline_A | -16.7 cm | 1 |  |
| 926.13 | IN |  | 0.00 | centreline_A | -230.0 cm | 1 |  |
| 930.25 | UNCERTAIN |  | 0.72 | baseline_A | 38.3 cm | 2 |  |
| 936.84 | UNCERTAIN |  | 1.00 | sideline_left | 69.4 cm | 1 |  |
| 938.88 | IN |  | 0.00 | sideline_right | -150.0 cm | 2 |  |
| 946.68 | UNCERTAIN |  | 1.00 | baseline_A | 110.3 cm | 1 |  |
| 947.63 | UNCERTAIN |  | 1.00 | sideline_left | 17.6 cm | 1 |  |
| 948.80 | IN |  | 0.00 | sideline_left | -56.2 cm | 1 |  |
| 955.82 | UNCERTAIN |  | 1.00 | baseline_A | 119.0 cm | 1 |  |
| 957.13 | IN |  | 0.00 | centreline_B | -156.0 cm | 1 |  |
| 960.38 | IN |  | 0.00 | baseline_A | -138.9 cm | 2 |  |
| 961.63 | UNCERTAIN |  | 1.00 | sideline_right | 151.2 cm | 1 | silent: one camera, flight not measured (speed 7 +- 44 m/s) |
| 975.04 | OUT | **OUT** | 1.00 | sideline_left | 26.4 cm | 1 |  |
| 976.85 | UNCERTAIN |  | 0.18 | centreline_A | -161.7 cm | 2 |  |
| 984.49 | OUT | **OUT** | 1.00 | sideline_left | 58.7 cm | 1 |  |
| 985.46 | OUT | **OUT** | 1.00 | baseline_A | 115.8 cm | 1 |  |
| 986.73 | UNCERTAIN |  | 1.00 | sideline_right | 323.4 cm | 1 |  |
| 986.84 | – |  | – |  | – | 1 | secondary bounce |
| 987.85 | IN |  | 0.00 | sideline_left | -6.3 cm | 1 |  |
| 988.04 | UNCERTAIN |  | 1.00 | sideline_right | 222.1 cm | 1 | silent: one camera, flight not measured (speed 22 +- 60 m/s) |
| 989.14 | IN |  | 0.00 | baseline_B | -55.8 cm | 1 |  |
| 991.43 | IN |  | 0.00 | kitchen_B | -118.3 cm | 1 |  |
| 991.77 | IN |  | 0.00 | centreline_A | -217.7 cm | 1 |  |
| 994.36 | IN |  | 0.00 | sideline_right | -61.7 cm | 1 |  |
| 1001.81 | IN |  | 0.00 | sideline_right | -124.1 cm | 1 |  |
| 1002.62 | – |  | – |  | – | 2 | secondary bounce |
| 1003.44 | – |  | – |  | – | 2 | secondary bounce |
| 1004.00 | IN |  | 0.00 | sideline_left | -74.3 cm | 1 |  |
| 1005.05 | – |  | – |  | – | 1 | secondary bounce |
| 1007.04 | IN |  | 0.00 | sideline_right | -25.7 cm | 1 |  |
| 1018.13 | UNCERTAIN |  | 1.00 | baseline_A | 111.2 cm | 1 | unconfirmed by samsung |
| 1022.76 | UNCERTAIN |  | 0.82 | baseline_B | 18.7 cm | 1 |  |
| 1023.79 | IN |  | 0.00 | sideline_right | -78.8 cm | 1 |  |
| 1024.20 | IN |  | 0.00 | sideline_left | -84.4 cm | 1 |  |
| 1025.25 | IN |  | 0.00 | sideline_right | -150.5 cm | 2 |  |
| 1026.78 | UNCERTAIN |  | 0.46 | baseline_A | -23.3 cm | 2 |  |
| 1028.49 | IN |  | 0.00 | sideline_left | -30.2 cm | 1 |  |
| 1035.62 | IN |  | 0.00 | sideline_left | -62.8 cm | 1 |  |
| 1036.01 | – |  | – |  | – | 1 | secondary bounce |
| 1039.49 | IN |  | 0.00 | centreline_B | -196.6 cm | 1 |  |
| 1041.33 | UNCERTAIN |  | 1.00 | sideline_right | 44.5 cm | 1 | serve from B (half unknown); silent: one camera, 10 m away, looking across the sideline_right |
| 1042.33 | IN |  | 0.00 | sideline_right | -104.8 cm | 1 |  |
| 1042.71 | – |  | – |  | – | 1 | secondary bounce |
| 1043.68 | OUT | **OUT** | 1.00 | sideline_left | 88.6 cm | 1 |  |
| 1045.91 | UNCERTAIN |  | 1.00 | sideline_right | 331.2 cm | 1 | silent: one camera, 12 m away, looking across the sideline_right |
| 1049.86 | IN |  | 0.00 | centreline_A | -177.4 cm | 1 |  |
| 1050.25 | IN |  | 0.00 | sideline_left | -21.6 cm | 1 |  |
| 1051.15 | – |  | – |  | – | 2 | secondary bounce |
| 1050.75 | IN |  | 0.00 | sideline_left | -77.8 cm | 1 |  |
| 1051.43 | – |  | – |  | – | 1 | secondary bounce |
| 1051.67 | – |  | – |  | – | 1 | secondary bounce |
| 1051.85 | UNCERTAIN |  | 1.00 | sideline_left | 48.1 cm | 1 |  |
| 1052.83 | OUT | **OUT** | 1.00 | sideline_left | 88.9 cm | 1 |  |
| 1054.89 | IN |  | 0.00 | kitchen_B | -201.1 cm | 1 |  |
| 1057.07 | UNCERTAIN |  | 1.00 | sideline_left | 75.5 cm | 1 | unconfirmed by iphone17 |
| 1057.28 | UNCERTAIN |  | 1.00 | sideline_right | 226.8 cm | 1 | silent: one camera, 11 m away, looking across the sideline_right |
| 1059.11 | UNCERTAIN |  | 1.00 | baseline_A | 58.3 cm | 1 |  |
| 1062.13 | UNCERTAIN |  | 1.00 | baseline_A | 103.7 cm | 1 |  |
| 1063.34 | UNCERTAIN |  | 1.00 | baseline_A | 64.7 cm | 1 |  |
| 1064.61 | IN |  | 0.00 | sideline_left | -117.9 cm | 2 |  |
| 1065.85 | IN |  | 0.00 | sideline_left | -91.2 cm | 2 |  |
| 1066.46 | – |  | – |  | – | 1 | secondary bounce |
| 1068.27 | IN |  | 0.00 | sideline_right | -114.4 cm | 2 |  |
| 1069.13 | – |  | – |  | – | 1 | secondary bounce |
| 1075.93 | UNCERTAIN |  | 1.00 | sideline_right | 308.0 cm | 1 |  |
| 1076.20 | – |  | – |  | – | 1 | secondary bounce |
| 1076.41 | IN |  | 0.00 | kitchen_B | -19.3 cm | 1 |  |
| 1076.97 | – |  | – |  | – | 2 | secondary bounce |
| 1077.40 | – |  | – |  | – | 1 | secondary bounce |
| 1079.72 | UNCERTAIN |  | 1.00 | sideline_right | 378.3 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 1082.65 | UNCERTAIN |  | 1.00 | sideline_right | 355.5 cm | 1 |  |
| 1083.66 | UNCERTAIN |  | 1.00 | sideline_right | 341.4 cm | 1 |  |
| 1084.55 | – |  | – |  | – | 1 | secondary bounce |
| 1084.73 | – |  | – |  | – | 1 | secondary bounce |
| 1091.53 | IN |  | 0.00 | kitchen_A | -195.2 cm | 2 |  |
| 1091.26 | IN |  | 0.00 | kitchen_A | -126.3 cm | 1 |  |
| 1091.96 | – |  | – |  | – | 1 | secondary bounce |
| 1092.32 | – |  | – |  | – | 1 | secondary bounce |
| 1096.95 | UNCERTAIN |  | 1.00 | baseline_A | 122.2 cm | 1 |  |
| 1098.24 | IN |  | 0.00 | baseline_B | -9.6 cm | 2 |  |
| 1102.05 | IN |  | 0.02 | baseline_A | -30.6 cm | 1 |  |
| 1103.96 | IN |  | 0.00 | centreline_B | -178.2 cm | 2 |  |
| 1104.93 | IN |  | 0.00 | centreline_A | -205.0 cm | 1 |  |
| 1105.63 | – |  | – |  | – | 1 | secondary bounce |
| 1105.96 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1106.72 | – |  | – |  | – | 1 | secondary bounce |
| 1115.01 | UNCERTAIN |  | 1.00 | baseline_A | 106.7 cm | 2 |  |
| 1116.46 | IN |  | 0.00 | baseline_B | -3.8 cm | 2 | serve from A right |
| 1121.78 | UNCERTAIN |  | 1.00 | sideline_right | 311.8 cm | 1 |  |
| 1122.82 | IN |  | 0.00 | sideline_left | -30.7 cm | 2 | serve from B left |
| 1131.06 | UNCERTAIN |  | 1.00 | baseline_A | 93.6 cm | 1 |  |
| 1132.38 | IN |  | 0.00 | baseline_B | -95.1 cm | 1 |  |
| 1134.20 | IN |  | 0.00 | sideline_right | -73.3 cm | 2 |  |
| 1135.54 | IN |  | 0.00 | centreline_B | -149.4 cm | 2 |  |
| 1147.63 | OUT | **OUT** | 1.00 | sideline_left | 19.3 cm | 1 |  |
| 1149.72 | UNCERTAIN |  | 1.00 | baseline_A | 209.3 cm | 1 |  |
| 1150.76 | UNCERTAIN |  | 0.73 | baseline_B | 117.6 cm | 1 |  |
| 1152.08 | UNCERTAIN |  | 1.00 | baseline_A | 113.8 cm | 1 |  |
| 1155.27 | UNCERTAIN |  | 1.00 | baseline_A | 112.3 cm | 2 |  |
| 1156.87 | IN |  | 0.00 | kitchen_A | -72.5 cm | 2 |  |
| 1157.45 | – |  | – |  | – | 1 | secondary bounce |
| 1157.88 | – |  | – |  | – | 2 | secondary bounce |
| 1168.69 | UNCERTAIN |  | 1.00 | baseline_A | 111.3 cm | 1 |  |
| 1170.01 | IN |  | 0.00 | baseline_B | -84.1 cm | 2 | serve from A right |
| 1171.63 | OUT | **OUT** | 1.00 | sideline_right | 131.8 cm | 2 |  |
| 1175.23 | UNCERTAIN |  | 0.95 | baseline_B | 241.8 cm | 1 |  |
| 1177.82 | IN |  | 0.00 | kitchen_B | -69.7 cm | 2 |  |
| 1178.66 | – |  | – |  | – | 1 | secondary bounce |
| 1184.53 | IN |  | 0.00 | sideline_right | -82.6 cm | 1 |  |
| 1185.90 | IN |  | 0.00 | sideline_right | -69.3 cm | 1 |  |
| 1190.69 | IN |  | 0.00 | baseline_B | -70.1 cm | 1 |  |
| 1196.80 | IN |  | 0.00 | kitchen_B | -17.7 cm | 1 |  |
| 1197.34 | – |  | – |  | – | 2 | secondary bounce |
| 1198.24 | – |  | – |  | – | 1 | secondary bounce |
| 1198.42 | – |  | – |  | – | 1 | secondary bounce |
| 1205.46 | UNCERTAIN |  | 1.00 | baseline_A | 70.6 cm | 2 |  |
| 1206.92 | OUT | **OUT** | 1.00 | baseline_B | 9.6 cm | 2 |  |
| 1208.44 | IN |  | 0.00 | sideline_left | -76.0 cm | 2 |  |
| 1209.97 | IN |  | 0.00 | centreline_B | -125.3 cm | 2 |  |
| 1215.17 | UNCERTAIN |  | 0.54 | baseline_A | 1.6 cm | 1 |  |
| 1216.92 | IN |  | 0.00 | kitchen_B | -136.5 cm | 1 |  |
| 1218.51 | IN |  | 0.00 | kitchen_B | -139.5 cm | 2 |  |
| 1218.88 | – |  | – |  | – | 2 | secondary bounce |
| 1218.04 | UNCERTAIN |  | 0.15 | kitchen_B | -8.5 cm | 1 |  |
| 1219.15 | – |  | – |  | – | 1 | secondary bounce |
| 1223.14 | OUT | **FAULT** | 1.00 | baseline_A | 10.9 cm | 2 | serve from B right |
| 1224.44 | UNCERTAIN |  | 1.00 | baseline_A | 151.5 cm | 1 | unconfirmed by iphone17 |
| 1226.32 | UNCERTAIN |  | 1.00 | baseline_A | 100.5 cm | 1 |  |
| 1227.15 | IN |  | 0.03 | centreline_A | -287.2 cm | 2 |  |
| 1227.80 | OUT | **OUT** | 1.00 | sideline_left | 7.1 cm | 2 |  |
| 1228.45 | – |  | – |  | – | 1 | secondary bounce |
| 1228.92 | – |  | – |  | – | 1 | secondary bounce |
| 1229.47 | – |  | – |  | – | 1 | secondary bounce |
| 1238.10 | IN |  | 0.00 | centreline_A | -112.5 cm | 2 | serve from B left |
| 1239.69 | IN |  | 0.00 | centreline_B | -209.0 cm | 2 |  |
| 1247.90 | UNCERTAIN |  | 1.00 | baseline_A | 85.6 cm | 1 |  |
| 1249.39 | UNCERTAIN |  | 1.00 | baseline_A | 84.7 cm | 2 |  |
| 1250.82 | IN |  | 0.00 | baseline_B | -99.7 cm | 2 |  |
| 1252.46 | IN |  | 0.00 | sideline_left | -13.3 cm | 1 |  |
| 1253.38 | IN |  | 0.00 | kitchen_A | -175.0 cm | 2 |  |
| 1254.15 | IN |  | 0.00 | kitchen_A | -24.9 cm | 1 |  |
| 1254.71 | – |  | – |  | – | 1 | secondary bounce |
| 1262.46 | IN |  | 0.00 | sideline_right | -84.6 cm | 1 |  |
| 1262.66 | – |  | – |  | – | 1 | secondary bounce |
| 1274.80 | IN |  | 0.00 | sideline_left | -141.8 cm | 1 |  |
| 1276.43 | IN |  | 0.00 | centreline_B | -196.5 cm | 2 |  |
| 1277.50 | IN |  | 0.00 | centreline_A | -165.1 cm | 2 |  |
| 1278.40 | UNCERTAIN |  | 0.35 | sideline_left | -1.1 cm | 2 |  |
| 1278.95 | IN |  | 0.00 | kitchen_B | -56.2 cm | 2 |  |
| 1279.38 | – |  | – |  | – | 1 | secondary bounce |
| 1279.71 | – |  | – |  | – | 1 | secondary bounce |
| 1286.31 | IN |  | 0.00 | kitchen_B | -243.7 cm | 1 |  |
| 1286.98 | IN |  | 0.00 | centreline_A | -223.3 cm | 2 |  |
| 1288.48 | IN |  | 0.00 | centreline_B | -210.8 cm | 2 |  |
| 1290.54 | IN |  | 0.00 | kitchen_B | -126.1 cm | 2 |  |
| 1291.19 | – |  | – |  | – | 1 | secondary bounce |
| 1293.88 | UNCERTAIN |  | 1.00 | sideline_right | 181.3 cm | 1 | unconfirmed by iphone17 |
| 1299.28 | UNCERTAIN |  | 1.00 | sideline_right | 116.0 cm | 2 |  |
| 1303.82 | UNCERTAIN |  | 1.00 | baseline_A | 95.6 cm | 2 |  |
| 1305.35 | IN |  | 0.00 | baseline_B | -86.3 cm | 2 |  |
| 1306.78 | UNCERTAIN |  | 1.00 | sideline_left | 70.9 cm | 1 | unconfirmed by samsung |
| 1313.38 | IN |  | 0.00 | sideline_right | -88.2 cm | 1 |  |
| 1314.89 | IN |  | 0.00 | centreline_A | -121.3 cm | 1 |  |
| 1316.60 | IN |  | 0.00 | baseline_B | -26.5 cm | 2 |  |
| 1324.71 | IN |  | 0.00 | baseline_A | -43.3 cm | 2 |  |
| 1327.13 | UNCERTAIN |  | 1.00 | baseline_A | 132.4 cm | 1 |  |
| 1328.40 | UNCERTAIN |  | 1.00 | baseline_A | 91.0 cm | 1 |  |
| 1329.62 | IN |  | 0.00 | sideline_left | -81.1 cm | 2 |  |
| 1330.96 | IN |  | 0.00 | centreline_A | -209.5 cm | 2 |  |
| 1332.50 | UNCERTAIN |  | 1.00 | sideline_right | 33.0 cm | 1 | unconfirmed by samsung |
| 1344.15 | OUT | **FAULT** | 1.00 | sideline_right | 30.8 cm | 2 | serve from B right |
| 1348.71 | UNCERTAIN |  | 1.00 | baseline_A | 160.7 cm | 1 |  |
| 1349.84 | UNCERTAIN |  | 1.00 | baseline_A | 101.9 cm | 2 |  |
| 1351.28 | IN |  | 0.00 | sideline_left | -129.4 cm | 2 |  |
| 1352.65 | IN |  | 0.00 | sideline_left | -95.5 cm | 2 |  |
| 1355.15 | UNCERTAIN |  | 1.00 | sideline_right | 67.2 cm | 2 |  |
| 1355.49 | – |  | – |  | – | 1 | secondary bounce |
| 1355.74 | – |  | – |  | – | 1 | secondary bounce |
| 1356.14 | – |  | – |  | – | 1 | secondary bounce |
| 1356.36 | – |  | – |  | – | 1 | secondary bounce |
| 1368.66 | IN |  | 0.00 | centreline_A | -154.6 cm | 1 | serve from B (half unknown) |
| 1370.02 | IN |  | 0.00 | kitchen_B | -32.0 cm | 1 |  |
| 1377.45 | OUT | **FAULT** | 1.00 | baseline_A | 16.2 cm | 2 | serve from B left |
| 1382.15 | UNCERTAIN |  | 1.00 | baseline_A | 163.4 cm | 1 |  |
| 1386.51 | UNCERTAIN |  | 1.00 | baseline_A | 100.6 cm | 2 |  |
| 1387.97 | IN |  | 0.00 | baseline_B | -95.4 cm | 1 |  |
| 1389.68 | IN |  | 0.00 | baseline_A | -49.7 cm | 2 |  |
| 1391.19 | OUT | **OUT** | 1.00 | baseline_B | 55.6 cm | 2 |  |
| 1398.51 | IN |  | 0.00 | sideline_right | -41.2 cm | 2 | serve from B right |
| 1399.68 | UNCERTAIN |  | 1.00 | sideline_right | 199.9 cm | 1 | unconfirmed by iphone17 |
| 1400.76 | IN |  | 0.00 | kitchen_B | -136.4 cm | 1 |  |
| 1401.73 | IN |  | 0.00 | kitchen_A | -131.3 cm | 2 |  |
| 1403.23 | IN |  | 0.00 | sideline_left | -44.7 cm | 2 |  |
| 1404.38 | IN |  | 0.00 | sideline_left | -31.3 cm | 1 |  |
| 1404.91 | – |  | – |  | – | 1 | secondary bounce |
| 1405.31 | – |  | – |  | – | 1 | secondary bounce |
| 1406.18 | – |  | – |  | – | 1 | secondary bounce |
| 1411.07 | IN |  | 0.00 | baseline_A | -28.5 cm | 2 |  |
| 1414.99 | UNCERTAIN |  | 1.00 | baseline_A | 72.9 cm | 1 |  |
| 1416.45 | IN |  | 0.00 | sideline_left | -112.3 cm | 2 | serve from A right |
| 1418.05 | IN |  | 0.00 | sideline_left | -116.5 cm | 2 |  |
| 1420.50 | IN |  | 0.00 | centreline_B | -180.4 cm | 2 |  |
| 1421.84 | IN |  | 0.00 | centreline_A | -155.0 cm | 1 |  |
| 1423.05 | IN |  | 0.00 | sideline_left | -53.8 cm | 2 |  |
| 1437.48 | UNCERTAIN |  | 1.00 | baseline_A | 76.7 cm | 1 |  |
| 1438.87 | IN |  | 0.00 | baseline_B | -89.7 cm | 2 |  |
| 1440.17 | IN |  | 0.00 | centreline_A | -230.8 cm | 2 |  |
| 1441.26 | IN |  | 0.00 | centreline_B | -159.9 cm | 2 |  |
| 1442.71 | OUT | **OUT** | 1.00 | sideline_right | 91.6 cm | 2 |  |
| 1451.95 | UNCERTAIN |  | 1.00 | baseline_A | 84.2 cm | 2 |  |
| 1453.20 | IN |  | 0.00 | centreline_B | -105.5 cm | 2 | serve from A right |
| 1454.44 | UNCERTAIN |  | 0.43 | sideline_left | -2.6 cm | 1 |  |
| 1458.16 | IN |  | 0.00 | sideline_left | -64.5 cm | 2 |  |
| 1458.97 | – |  | – |  | – | 2 | secondary bounce |
| 1458.68 | IN |  | 0.00 | baseline_A | -116.2 cm | 1 |  |
| 1459.51 | UNCERTAIN |  | 0.42 | sideline_left | -0.4 cm | 1 |  |
| 1459.93 | – |  | – |  | – | 1 | secondary bounce |
| 1460.23 | – |  | – |  | – | 1 | secondary bounce |
| 1460.46 | – |  | – |  | – | 1 | secondary bounce |
| 1465.64 | UNCERTAIN |  | 1.00 | baseline_A | 148.2 cm | 1 |  |
| 1468.11 | UNCERTAIN |  | 1.00 | baseline_A | 90.9 cm | 1 |  |
| 1475.07 | UNCERTAIN |  | 0.36 | sideline_right | -2.9 cm | 1 | serve from B (half unknown) |
| 1476.89 | IN |  | 0.00 | centreline_B | -178.1 cm | 2 |  |
| 1478.12 | IN |  | 0.00 | sideline_right | -92.1 cm | 2 |  |
| 1478.73 | – |  | – |  | – | 1 | secondary bounce |
| 1479.22 | – |  | – |  | – | 1 | secondary bounce |
| 1484.63 | IN |  | 0.00 | sideline_right | -136.8 cm | 1 |  |
| 1489.64 | IN |  | 0.00 | baseline_A | -93.5 cm | 2 |  |
| 1491.03 | IN |  | 0.00 | sideline_right | -84.2 cm | 1 |  |
| 1492.59 | IN |  | 0.00 | centreline_A | -146.8 cm | 1 |  |
| 1493.79 | IN |  | 0.00 | sideline_right | -86.0 cm | 1 |  |
| 1495.56 | UNCERTAIN |  | 1.00 | sideline_right | 116.2 cm | 1 |  |
| 1500.60 | IN |  | 0.00 | sideline_left | -86.7 cm | 2 | serve from B left |
| 1503.00 | UNCERTAIN |  | 1.00 | baseline_A | 117.9 cm | 1 |  |
| 1505.87 | UNCERTAIN |  | 1.00 | baseline_A | 103.7 cm | 1 |  |
| 1507.15 | IN |  | 0.00 | centreline_B | -200.0 cm | 1 |  |
| 1508.47 | IN |  | 0.00 | centreline_A | -186.6 cm | 2 |  |
| 1511.18 | IN |  | 0.00 | sideline_left | -153.7 cm | 2 |  |
| 1512.63 | IN |  | 0.00 | sideline_right | -124.8 cm | 1 |  |
| 1513.67 | IN |  | 0.00 | kitchen_A | -121.7 cm | 1 |  |
| 1515.04 | IN |  | 0.00 | baseline_B | -71.5 cm | 1 |  |
| 1517.77 | UNCERTAIN |  | 1.00 | baseline_A | 173.1 cm | 1 |  |
| 1525.97 | UNCERTAIN |  | 1.00 | sideline_right | 30.9 cm | 1 | silent: one camera, flight not measured (speed 18 +- 37 m/s) |
| 1535.34 | UNCERTAIN |  | 1.00 | baseline_A | 159.4 cm | 1 |  |
| 1538.34 | UNCERTAIN |  | 1.00 | baseline_A | 375.5 cm | 1 |  |
| 1538.72 | – |  | – |  | – | 1 | secondary bounce |
| 1540.12 | IN |  | 0.00 | baseline_B | -84.5 cm | 2 | serve from A right |
| 1541.45 | IN |  | 0.00 | kitchen_A | -193.9 cm | 2 |  |
| 1542.66 | IN |  | 0.00 | kitchen_B | -162.2 cm | 1 |  |
| 1544.61 | UNCERTAIN |  | 1.00 | baseline_A | 95.9 cm | 1 | unconfirmed by iphone17 |
| 1560.85 | UNCERTAIN |  | 1.00 | baseline_A | 120.1 cm | 1 |  |
| 1561.21 | UNCERTAIN |  | 0.38 | sideline_left | -152.3 cm | 1 |  |
| 1562.30 | UNCERTAIN |  | 1.00 | baseline_A | 72.9 cm | 1 |  |
| 1563.13 | OUT | **OUT** | 1.00 | sideline_right | 28.6 cm | 1 |  |
| 1563.73 | IN |  | 0.00 | kitchen_B | -146.3 cm | 2 |  |
| 1564.33 | – |  | – |  | – | 1 | secondary bounce |
| 1565.27 | IN |  | 0.03 | sideline_right | -4.5 cm | 2 |  |
| 1565.86 | – |  | – |  | – | 1 | secondary bounce |
| 1566.27 | – |  | – |  | – | 1 | secondary bounce |
| 1566.59 | – |  | – |  | – | 1 | secondary bounce |
| 1566.84 | – |  | – |  | – | 1 | secondary bounce |
| 1571.08 | UNCERTAIN |  | 1.00 | baseline_A | 116.9 cm | 2 | silent: start of play far outside the court (ball handling?) |
| 1572.51 | UNCERTAIN |  | 1.00 | baseline_A | 149.8 cm | 1 |  |
| 1574.49 | UNCERTAIN |  | 1.00 | baseline_A | 68.3 cm | 2 |  |
| 1575.71 | IN |  | 0.00 | centreline_B | -106.5 cm | 2 | serve from A right |
| 1577.04 | IN |  | 0.00 | kitchen_A | -242.6 cm | 2 |  |
| 1587.34 | UNCERTAIN |  | 1.00 | baseline_A | 58.3 cm | 1 | silent: one camera, 17 m away, looking across the baseline_A |
| 1596.09 | UNCERTAIN |  | 1.00 | baseline_A | 78.3 cm | 1 |  |
| 1597.45 | IN |  | 0.00 | centreline_B | -140.2 cm | 2 | serve from A right |
| 1598.76 | IN |  | 0.00 | sideline_left | -32.2 cm | 2 |  |
| 1601.03 | UNCERTAIN |  | 1.00 | baseline_B | 30.0 cm | 1 | unconfirmed by samsung |
| 1616.01 | IN |  | 0.00 | sideline_left | -150.0 cm | 1 |  |
| 1617.57 | OUT | **OUT** | 1.00 | sideline_left | 44.6 cm | 1 |  |
| 1624.09 | IN |  | 0.00 | baseline_A | -24.4 cm | 2 |  |
| 1625.88 | IN |  | 0.00 | baseline_B | -119.9 cm | 1 |  |
| 1627.39 | IN |  | 0.00 | sideline_right | -112.5 cm | 2 |  |
| 1628.47 | IN |  | 0.00 | kitchen_B | -112.1 cm | 1 |  |
| 1630.89 | UNCERTAIN |  | 1.00 | baseline_A | 196.9 cm | 1 |  |
| 1632.16 | UNCERTAIN |  | 1.00 | baseline_A | 255.2 cm | 1 |  |
| 1632.31 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1635.89 | UNCERTAIN |  | 1.00 | baseline_A | 170.8 cm | 1 |  |
| 1638.36 | UNCERTAIN |  | 1.00 | baseline_A | 105.4 cm | 2 |  |
| 1639.70 | IN |  | 0.00 | sideline_left | -151.3 cm | 2 | serve from A right |
| 1640.84 | IN |  | 0.00 | sideline_left | -26.7 cm | 2 |  |
| 1641.77 | – |  | – |  | – | 1 | secondary bounce |
| 1642.28 | UNCERTAIN |  | 0.77 | baseline_B | 91.9 cm | 1 |  |
| 1654.77 | IN |  | 0.00 | centreline_A | -157.6 cm | 1 |  |
| 1656.22 | IN |  | 0.00 | sideline_right | -141.1 cm | 1 |  |
| 1657.91 | IN |  | 0.00 | kitchen_B | -237.2 cm | 2 |  |
| 1659.37 | UNCERTAIN |  | 0.10 | sideline_right | -53.5 cm | 2 |  |
| 1661.04 | UNCERTAIN |  | 1.00 | baseline_A | 186.1 cm | 1 |  |
| 1667.61 | IN |  | 0.00 | sideline_right | -17.5 cm | 1 | serve from A (half unknown) |
| 1675.36 | IN |  | 0.00 | sideline_left | -6.4 cm | 1 | serve from B (half unknown) |
| 1677.17 | IN |  | 0.00 | baseline_B | -127.7 cm | 1 |  |
| 1679.48 | IN |  | 0.00 | sideline_right | -59.6 cm | 1 |  |
| 1680.26 | – |  | – |  | – | 1 | secondary bounce |
| 1687.88 | UNCERTAIN |  | 1.00 | sideline_right | 52.2 cm | 1 | unconfirmed by samsung |
| 1688.60 | – |  | – |  | – | 1 | secondary bounce |
| 1695.07 | UNCERTAIN |  | 1.00 | baseline_A | 121.0 cm | 2 |  |
| 1696.60 | UNCERTAIN |  | 0.50 | baseline_B | -0.6 cm | 2 |  |
| 1698.02 | IN |  | 0.00 | centreline_A | -281.1 cm | 2 |  |
| 1703.59 | IN |  | 0.00 | kitchen_A | -79.5 cm | 1 |  |
| 1703.78 | – |  | – |  | – | 1 | secondary bounce |
| 1713.00 | UNCERTAIN |  | 0.31 | kitchen_A | -23.5 cm | 2 |  |
| 1713.54 | – |  | – |  | – | 2 | secondary bounce |
| 1713.98 | – |  | – |  | – | 1 | secondary bounce |
| 1714.75 | – |  | – |  | – | 1 | secondary bounce |
| 1718.48 | IN |  | 0.00 | centreline_B | -132.0 cm | 1 |  |
| 1722.47 | IN |  | 0.02 | baseline_A | -56.1 cm | 2 |  |
| 1723.93 | IN |  | 0.00 | sideline_right | -148.0 cm | 1 |  |
| 1725.05 | IN |  | 0.00 | centreline_A | -184.3 cm | 2 |  |
| 1734.48 | UNCERTAIN |  | 1.00 | baseline_B | 91.6 cm | 1 | unconfirmed by samsung |
| 1742.09 | UNCERTAIN |  | 0.32 | baseline_A | -22.6 cm | 2 |  |
| 1743.73 | IN |  | 0.00 | sideline_right | -134.4 cm | 1 |  |
| 1745.55 | IN |  | 0.02 | sideline_right | -81.4 cm | 2 |  |
| 1747.01 | IN |  | 0.00 | centreline_A | -259.8 cm | 1 |  |
| 1750.15 | UNCERTAIN |  | 1.00 | baseline_B | 31.1 cm | 1 | unconfirmed by samsung |
| 1755.83 | IN |  | 0.00 | sideline_left | -100.5 cm | 2 | serve from B left |
| 1757.45 | IN |  | 0.00 | sideline_right | -53.8 cm | 1 |  |
| 1758.43 | UNCERTAIN |  | 1.00 | baseline_A | 132.2 cm | 1 |  |
| 1759.39 | IN |  | 0.00 | kitchen_B | -100.2 cm | 2 |  |
| 1762.07 | UNCERTAIN |  | 1.00 | sideline_right | 97.3 cm | 2 | cameras disagree (chi2 724) |
| 1778.73 | IN |  | 0.00 | sideline_right | -74.6 cm | 1 |  |
| 1778.98 | – |  | – |  | – | 1 | secondary bounce |
| 1779.20 | – |  | – |  | – | 1 | secondary bounce |
| 1779.38 | – |  | – |  | – | 1 | secondary bounce |
| 1780.93 | UNCERTAIN |  | 1.00 | sideline_right | 114.9 cm | 1 |  |
| 1786.04 | IN |  | 0.00 | baseline_B | -68.0 cm | 1 |  |
| 1787.38 | IN |  | 0.00 | sideline_left | -141.0 cm | 2 |  |
| 1788.24 | – |  | – |  | – | 1 | secondary bounce |
| 1792.61 | UNCERTAIN |  | 1.00 | baseline_A | 202.7 cm | 1 |  |
| 1792.88 | UNCERTAIN |  | 1.00 | baseline_B | 56.6 cm | 1 |  |
| 1794.80 | UNCERTAIN |  | 1.00 | baseline_A | 162.0 cm | 1 |  |
| 1797.29 | UNCERTAIN |  | 1.00 | baseline_A | 100.6 cm | 2 |  |
| 1798.67 | IN |  | 0.00 | sideline_left | -28.7 cm | 1 |  |
| 1800.14 | IN |  | 0.00 | sideline_left | -147.4 cm | 2 |  |
| 1800.59 | UNCERTAIN |  | 1.00 | sideline_right | 191.9 cm | 1 | unconfirmed by iphone17 |
| 1801.73 | IN |  | 0.00 | sideline_left | -29.5 cm | 1 |  |
| 1803.11 | IN |  | 0.00 | kitchen_A | -207.2 cm | 2 |  |
| 1804.42 | IN |  | 0.00 | centreline_B | -229.5 cm | 2 |  |
| 1805.19 | IN |  | 0.00 | kitchen_B | -108.4 cm | 1 |  |
| 1805.68 | IN |  | 0.00 | sideline_left | -111.6 cm | 2 |  |
| 1807.17 | IN |  | 0.00 | kitchen_B | -80.3 cm | 1 |  |
| 1808.10 | IN |  | 0.00 | sideline_right | -54.0 cm | 1 |  |
| 1808.55 | IN |  | 0.00 | kitchen_A | -147.6 cm | 1 |  |
| 1809.86 | IN |  | 0.02 | sideline_left | -60.0 cm | 2 |  |
| 1809.54 | IN |  | 0.00 | kitchen_A | -48.7 cm | 1 |  |
| 1810.40 | – |  | – |  | – | 1 | secondary bounce |
| 1810.96 | – |  | – |  | – | 1 | secondary bounce |
| 1811.79 | IN |  | 0.00 | sideline_left | -16.1 cm | 1 |  |
| 1811.37 | UNCERTAIN |  | 1.00 | sideline_right | 172.2 cm | 1 | unconfirmed by iphone17 |
| 1819.61 | UNCERTAIN |  | 1.00 | baseline_B | 212.7 cm | 1 |  |
| 1821.34 | IN |  | 0.00 | centreline_A | -120.2 cm | 2 |  |
| 1823.03 | IN |  | 0.00 | centreline_B | -125.9 cm | 1 |  |
| 1824.71 | IN |  | 0.00 | centreline_A | -201.9 cm | 2 |  |
| 1825.81 | IN |  | 0.00 | centreline_A | -258.4 cm | 1 |  |
| 1826.08 | – |  | – |  | – | 1 | secondary bounce |
| 1826.69 | UNCERTAIN |  | 1.00 | sideline_right | 239.0 cm | 1 | unconfirmed by iphone17 |
| 1828.15 | UNCERTAIN |  | 1.00 | sideline_right | 198.1 cm | 1 | unconfirmed by iphone17 |
| 1834.45 | IN |  | 0.00 | sideline_left | -109.4 cm | 1 |  |
| 1835.34 | – |  | – |  | – | 1 | secondary bounce |
| 1835.91 | IN |  | 0.00 | kitchen_B | -47.2 cm | 1 |  |
| 1836.51 | – |  | – |  | – | 1 | secondary bounce |
| 1836.95 | – |  | – |  | – | 1 | secondary bounce |
| 1837.54 | – |  | – |  | – | 2 | secondary bounce |
| 1840.04 | UNCERTAIN |  | 0.46 | baseline_A | -2.4 cm | 2 |  |
| 1840.75 | – |  | – |  | – | 1 | secondary bounce |
| 1841.28 | UNCERTAIN |  | 1.00 | baseline_A | 236.9 cm | 1 |  |
| 1841.67 | – |  | – |  | – | 1 | secondary bounce |
| 1841.96 | – |  | – |  | – | 1 | secondary bounce |
| 1842.48 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1847.26 | UNCERTAIN |  | 1.00 | baseline_A | 145.2 cm | 1 |  |
| 1847.90 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1851.06 | UNCERTAIN |  | 1.00 | baseline_A | 160.5 cm | 1 |  |
| 1854.00 | UNCERTAIN |  | 1.00 | baseline_A | 119.7 cm | 1 | unconfirmed by iphone17 |
| 1855.43 | UNCERTAIN |  | 0.72 | sideline_right | -47.6 cm | 2 |  |
| 1857.01 | IN |  | 0.00 | sideline_left | -112.1 cm | 2 |  |
| 1856.90 | UNCERTAIN |  | 1.00 | sideline_right | 351.2 cm | 1 | unconfirmed by samsung |
| 1858.90 | UNCERTAIN |  | 1.00 | baseline_B | 38.0 cm | 1 | unconfirmed by samsung |
| 1867.77 | IN |  | 0.00 | sideline_left | -17.5 cm | 1 |  |
| 1868.96 | UNCERTAIN |  | 1.00 | sideline_right | 49.8 cm | 1 | unconfirmed by iphone17 |
| 1869.38 | IN |  | 0.00 | centreline_B | -235.2 cm | 2 |  |
| 1870.65 | IN |  | 0.01 | sideline_left | -36.4 cm | 2 |  |
| 1871.26 | UNCERTAIN |  | 1.00 | sideline_right | 300.1 cm | 1 | unconfirmed by samsung |
| 1871.44 | – |  | – |  | – | 1 | secondary bounce |
| 1879.27 | UNCERTAIN |  | 1.00 | baseline_B | 107.1 cm | 1 |  |
| 1882.78 | IN |  | 0.00 | centreline_A | -101.4 cm | 2 |  |
| 1884.57 | IN |  | 0.04 | centreline_B | -46.5 cm | 1 |  |
| 1890.24 | IN |  | 0.00 | baseline_A | -56.3 cm | 1 |  |
| 1891.03 | – |  | – |  | – | 1 | secondary bounce |
| 1903.79 | UNCERTAIN |  | 1.00 | sideline_right | 234.0 cm | 1 | unconfirmed by iphone17 |
| 1913.96 | UNCERTAIN |  | 1.00 | sideline_right | 239.8 cm | 1 | unconfirmed by iphone17 |
| 1926.45 | UNCERTAIN |  | 1.00 | sideline_right | 261.6 cm | 1 | unconfirmed by iphone17 |
| 1952.60 | UNCERTAIN |  | 1.00 | sideline_right | 196.8 cm | 1 |  |
| 1971.73 | UNCERTAIN |  | 1.00 | sideline_right | 203.7 cm | 1 | unconfirmed by iphone17 |
| 1974.72 | UNCERTAIN |  | 1.00 | sideline_right | 342.0 cm | 1 | unconfirmed by samsung |
| 1975.36 | – |  | – |  | – | 1 | secondary bounce |
| 1976.41 | – |  | – |  | – | 1 | secondary bounce |
| 1989.64 | UNCERTAIN |  | 1.00 | baseline_A | 136.1 cm | 2 |  |
| 2007.36 | UNCERTAIN |  | 1.00 | baseline_A | 194.0 cm | 1 |  |
| 2025.62 | UNCERTAIN |  | 1.00 | baseline_B | 83.9 cm | 1 |  |
| 2039.94 | UNCERTAIN |  | 1.00 | baseline_A | 151.5 cm | 1 | unconfirmed by iphone17 |
| 2042.85 | UNCERTAIN |  | 1.00 | baseline_A | 119.2 cm | 1 |  |
| 2044.15 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2045.54 | IN |  | 0.00 | baseline_B | -127.9 cm | 1 |  |
| 2046.85 | IN |  | 0.00 | kitchen_A | -196.7 cm | 2 |  |
| 2049.38 | UNCERTAIN |  | 0.88 | sideline_right | 48.9 cm | 2 |  |
| 2049.22 | IN |  | 0.00 | kitchen_A | -101.0 cm | 1 |  |
| 2050.54 | UNCERTAIN |  | 1.00 | sideline_right | 58.9 cm | 1 | unconfirmed by samsung |
| 2057.01 | IN |  | 0.00 | centreline_A | -244.4 cm | 2 |  |
| 2056.10 | IN |  | 0.00 | sideline_left | -90.4 cm | 1 |  |
| 2058.46 | IN |  | 0.00 | centreline_B | -190.0 cm | 2 |  |
| 2059.35 | UNCERTAIN |  | 1.00 | baseline_A | 313.2 cm | 1 |  |
| 2060.11 | UNCERTAIN |  | 0.29 | kitchen_A | -30.6 cm | 2 |  |
| 2060.72 | – |  | – |  | – | 2 | secondary bounce |
| 2061.16 | – |  | – |  | – | 1 | secondary bounce |
| 2062.69 | IN |  | 0.00 | kitchen_B | -118.8 cm | 1 |  |
| 2071.60 | IN |  | 0.00 | centreline_B | -216.5 cm | 1 |  |
| 2072.57 | IN |  | 0.00 | sideline_left | -79.5 cm | 1 |  |
| 2074.28 | IN |  | 0.01 | kitchen_A | -122.3 cm | 2 |  |
| 2074.74 | – |  | – |  | – | 2 | secondary bounce |
| 2075.34 | – |  | – |  | – | 1 | secondary bounce |
| 2076.99 | IN |  | 0.00 | centreline_B | -234.0 cm | 2 |  |
| 2077.79 | – |  | – |  | – | 1 | secondary bounce |
| 2078.55 | – |  | – |  | – | 1 | secondary bounce |
| 2083.93 | IN |  | 0.00 | sideline_left | -72.6 cm | 1 |  |
| 2084.89 | IN |  | 0.00 | centreline_A | -131.5 cm | 1 |  |
| 2085.61 | – |  | – |  | – | 1 | secondary bounce |
| 2091.50 | IN |  | 0.00 | centreline_B | -140.6 cm | 1 |  |
| 2097.67 | UNCERTAIN |  | 0.10 | centreline_A | -28.9 cm | 3 | serve from B left |
| 2099.58 | UNCERTAIN |  | 0.28 | baseline_B | -9.9 cm | 1 |  |
| 2101.77 | IN |  | 0.00 | centreline_B | -268.9 cm | 1 |  |
| 2101.89 | IN |  | 0.00 | kitchen_B | -223.1 cm | 1 |  |
| 2104.35 | IN |  | 0.00 | kitchen_B | -188.9 cm | 2 |  |
| 2106.57 | UNCERTAIN |  | 0.16 | sideline_left | -25.4 cm | 3 |  |
| 2107.58 | – |  | – |  | – | 2 | secondary bounce |
| 2107.86 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2112.92 | UNCERTAIN |  | 0.99 | sideline_right | 28.3 cm | 1 | unconfirmed by iphone17, iphone15pro |
| 2115.96 | UNCERTAIN |  | 1.00 | baseline_A | 82.1 cm | 1 |  |
| 2117.20 | IN |  | 0.01 | sideline_left | -111.6 cm | 2 | serve from A right |
| 2118.96 | IN |  | 0.00 | centreline_A | -216.5 cm | 1 |  |
| 2119.55 | IN |  | 0.00 | sideline_left | -85.6 cm | 1 |  |
| 2119.97 | UNCERTAIN |  | 1.00 | baseline_B | 112.0 cm | 1 |  |
| 2120.81 | IN |  | 0.00 | sideline_right | -55.3 cm | 1 |  |
| 2129.53 | IN |  | 0.00 | sideline_right | -139.6 cm | 2 | serve from A left |
| 2131.23 | IN |  | 0.00 | centreline_A | -155.5 cm | 2 |  |
| 2132.52 | IN |  | 0.00 | kitchen_B | -192.3 cm | 2 |  |
| 2133.18 | UNCERTAIN |  | 1.00 | baseline_A | 54.5 cm | 1 |  |
| 2134.16 | UNCERTAIN |  | 0.36 | kitchen_A | -18.1 cm | 2 |  |
| 2134.64 | IN |  | 0.00 | kitchen_B | -110.4 cm | 2 |  |
| 2135.04 | – |  | – |  | – | 1 | secondary bounce |
| 2137.43 | IN |  | 0.00 | centreline_B | -256.9 cm | 1 |  |
| 2137.61 | IN |  | 0.00 | kitchen_A | -143.0 cm | 2 |  |
| 2138.88 | UNCERTAIN |  | 1.00 | sideline_right | 190.8 cm | 1 | unconfirmed by iphone17 |
| 2139.57 | – |  | – |  | – | 1 | secondary bounce |
| 2142.45 | UNCERTAIN |  | 1.00 | baseline_A | 87.1 cm | 1 | unconfirmed by iphone17 |
| 2144.20 | UNCERTAIN |  | 0.05 | baseline_B | -47.7 cm | 3 |  |
| 2145.78 | IN |  | 0.00 | sideline_left | -59.5 cm | 1 |  |
| 2146.23 | IN |  | 0.02 | sideline_left | -12.2 cm | 1 |  |
| 2149.93 | IN |  | 0.00 | sideline_left | -103.2 cm | 2 |  |
| 2150.75 | – |  | – |  | – | 1 | secondary bounce |
| 2154.77 | IN |  | 0.00 | centreline_B | -125.3 cm | 2 | serve from A left |
| 2156.56 | UNCERTAIN |  | 0.98 | baseline_A | 32.4 cm | 1 |  |
| 2166.09 | IN |  | 0.00 | sideline_left | -79.3 cm | 2 | serve from A right |
| 2167.95 | IN |  | 0.00 | baseline_A | -80.2 cm | 2 |  |
| 2169.12 | IN |  | 0.00 | sideline_left | -50.4 cm | 1 |  |
| 2169.45 | IN |  | 0.01 | kitchen_A | -128.1 cm | 2 |  |
| 2169.78 | – |  | – |  | – | 1 | secondary bounce |
| 2170.04 | – |  | – |  | – | 1 | secondary bounce |
| 2170.26 | – |  | – |  | – | 1 | secondary bounce |
| 2172.52 | IN |  | 0.00 | centreline_A | -99.3 cm | 2 |  |
| 2173.89 | IN |  | 0.00 | kitchen_B | -180.9 cm | 1 |  |
| 2174.89 | – |  | – |  | – | 1 | secondary bounce |
| 2176.37 | UNCERTAIN |  | 1.00 | baseline_B | 191.2 cm | 1 |  |
| 2180.94 | IN |  | 0.00 | centreline_A | -182.0 cm | 2 |  |
| 2182.48 | IN |  | 0.00 | centreline_B | -168.0 cm | 3 |  |
| 2183.56 | IN |  | 0.01 | kitchen_A | -66.1 cm | 1 |  |
| 2184.38 | IN |  | 0.00 | centreline_B | -266.4 cm | 3 |  |
| 2185.66 | UNCERTAIN |  | 0.36 | sideline_right | -17.7 cm | 2 |  |
| 2186.19 | – |  | – |  | – | 1 | secondary bounce |
| 2186.65 | IN |  | 0.00 | kitchen_B | -146.8 cm | 1 |  |
| 2187.10 | – |  | – |  | – | 1 | secondary bounce |
| 2187.47 | IN |  | 0.00 | kitchen_B | -136.6 cm | 2 |  |
| 2188.72 | IN |  | 0.00 | kitchen_A | -60.3 cm | 1 |  |
| 2189.56 | – |  | – |  | – | 3 | secondary bounce |
| 2190.43 | – |  | – |  | – | 1 | secondary bounce |
| 2191.31 | IN |  | 0.00 | kitchen_A | -102.2 cm | 1 |  |
| 2193.07 | IN |  | 0.02 | centreline_B | -164.6 cm | 2 |  |
| 2194.45 | UNCERTAIN |  | 0.99 | baseline_B | 50.3 cm | 1 |  |
| 2195.94 | UNCERTAIN |  | 1.00 | baseline_B | 84.7 cm | 1 |  |
| 2200.81 | UNCERTAIN |  | 0.47 | kitchen_B | -6.3 cm | 2 |  |
| 2201.35 | – |  | – |  | – | 1 | secondary bounce |
| 2201.74 | – |  | – |  | – | 2 | secondary bounce |
| 2204.81 | IN |  | 0.00 | sideline_left | -92.0 cm | 3 |  |
| 2210.76 | IN |  | 0.00 | baseline_B | -77.5 cm | 1 |  |
| 2211.05 | IN |  | 0.00 | centreline_B | -138.0 cm | 1 |  |
| 2212.91 | IN |  | 0.00 | centreline_A | -92.1 cm | 2 |  |
| 2215.07 | UNCERTAIN |  | 0.06 | sideline_left | -9.3 cm | 1 |  |
| 2226.42 | UNCERTAIN |  | 1.00 | baseline_A | 85.8 cm | 1 |  |
| 2227.69 | IN |  | 0.00 | sideline_right | -147.4 cm | 1 |  |
| 2228.11 | IN |  | 0.00 | centreline_B | -212.8 cm | 1 |  |
| 2228.95 | IN |  | 0.00 | kitchen_A | -166.3 cm | 1 |  |
| 2229.28 | IN |  | 0.00 | kitchen_B | -94.1 cm | 1 |  |
| 2229.85 | – |  | – |  | – | 1 | secondary bounce |
| 2230.03 | – |  | – |  | – | 2 | secondary bounce |
| 2230.21 | – |  | – |  | – | 1 | secondary bounce |
| 2232.79 | IN |  | 0.00 | sideline_left | -48.5 cm | 1 |  |
| 2232.94 | – |  | – |  | – | 2 | secondary bounce |
| 2235.18 | UNCERTAIN |  | 1.00 | baseline_A | 119.5 cm | 1 |  |
| 2236.95 | UNCERTAIN |  | 1.00 | baseline_A | 126.4 cm | 1 |  |
| 2238.14 | IN |  | 0.00 | sideline_left | -19.3 cm | 1 |  |
| 2239.85 | IN |  | 0.01 | baseline_A | -79.1 cm | 2 |  |
| 2243.69 | IN |  | 0.00 | centreline_A | -205.9 cm | 2 |  |
| 2247.52 | UNCERTAIN |  | 0.20 | sideline_left | -2.4 cm | 1 |  |
| 2257.34 | IN |  | 0.00 | sideline_left | -67.7 cm | 1 |  |
| 2258.35 | IN |  | 0.00 | centreline_A | -214.7 cm | 2 |  |
| 2258.90 | IN |  | 0.00 | sideline_left | -48.8 cm | 1 |  |
| 2259.89 | IN |  | 0.00 | centreline_B | -133.9 cm | 1 |  |
| 2265.04 | UNCERTAIN |  | 1.00 | baseline_A | 124.0 cm | 2 |  |
| 2266.94 | UNCERTAIN |  | 1.00 | baseline_A | 132.1 cm | 1 |  |
| 2267.44 | IN |  | 0.00 | centreline_B | -94.6 cm | 1 | serve from A right |
| 2268.30 | – |  | – |  | – | 2 | secondary bounce |
| 2269.18 | – |  | – |  | – | 1 | secondary bounce |
| 2275.07 | IN |  | 0.00 | baseline_A | -130.3 cm | 2 |  |
| 2276.71 | IN |  | 0.00 | sideline_right | -119.7 cm | 1 |  |
| 2277.39 | IN |  | 0.00 | sideline_right | -131.1 cm | 1 |  |
| 2279.97 | UNCERTAIN |  | 0.42 | kitchen_B | -19.5 cm | 2 |  |
| 2280.41 | IN |  | 0.00 | kitchen_A | -164.8 cm | 1 |  |
| 2281.83 | IN |  | 0.00 | kitchen_A | -158.3 cm | 1 |  |
| 2289.63 | UNCERTAIN |  | 1.00 | baseline_A | 122.3 cm | 1 |  |
| 2291.74 | UNCERTAIN |  | 1.00 | baseline_A | 174.4 cm | 1 |  |
| 2293.06 | UNCERTAIN |  | 1.00 | baseline_A | 129.0 cm | 1 |  |
| 2294.42 | IN |  | 0.00 | centreline_B | -198.4 cm | 3 |  |
| 2295.96 | IN |  | 0.00 | centreline_A | -234.1 cm | 2 |  |
| 2299.22 | UNCERTAIN |  | 1.00 | sideline_right | 143.6 cm | 1 | unconfirmed by samsung |
| 2299.76 | UNCERTAIN |  | 1.00 | sideline_right | 51.1 cm | 1 | unconfirmed by iphone17 |
| 2301.76 | IN |  | 0.00 | sideline_right | -54.4 cm | 1 |  |
| 2306.01 | IN |  | 0.00 | sideline_left | -108.7 cm | 2 |  |
| 2306.73 | – |  | – |  | – | 2 | secondary bounce |
| 2307.26 | – |  | – |  | – | 1 | secondary bounce |
| 2309.80 | IN |  | 0.00 | sideline_right | -151.3 cm | 1 |  |
| 2311.49 | IN |  | 0.00 | baseline_A | -97.1 cm | 1 |  |
| 2313.33 | IN |  | 0.00 | centreline_A | -118.3 cm | 1 |  |
| 2316.04 | IN |  | 0.00 | kitchen_A | -169.6 cm | 2 |  |
| 2317.68 | UNCERTAIN |  | 0.45 | sideline_left | -14.3 cm | 2 |  |
| 2324.81 | IN |  | 0.01 | baseline_A | -118.7 cm | 2 |  |
| 2326.03 | IN |  | 0.00 | kitchen_B | -174.6 cm | 2 |  |
| 2327.60 | IN |  | 0.00 | kitchen_B | -189.4 cm | 3 |  |
| 2328.05 | – |  | – |  | – | 2 | secondary bounce |
| 2328.98 | IN |  | 0.00 | kitchen_A | -115.8 cm | 1 |  |
| 2330.09 | IN |  | 0.00 | kitchen_B | -113.7 cm | 1 |  |
| 2331.37 | IN |  | 0.00 | sideline_left | -20.3 cm | 1 |  |
| 2331.50 | IN |  | 0.00 | kitchen_A | -98.9 cm | 1 |  |
| 2332.92 | UNCERTAIN |  | 0.98 | sideline_left | 50.4 cm | 2 | cameras disagree (chi2 856) |
| 2333.69 | – |  | – |  | – | 1 | secondary bounce |
| 2358.63 | IN |  | 0.00 | centreline_B | -194.6 cm | 1 |  |
| 2359.78 | IN |  | 0.00 | sideline_left | -143.4 cm | 1 |  |
| 2361.25 | IN |  | 0.00 | centreline_B | -230.1 cm | 2 |  |
| 2362.72 | IN |  | 0.02 | sideline_left | -43.8 cm | 2 |  |
| 2363.12 | UNCERTAIN |  | 1.00 | sideline_left | 81.1 cm | 1 | unconfirmed by samsung |
| 2363.85 | UNCERTAIN |  | 1.00 | sideline_left | 154.0 cm | 2 |  |
| 2364.77 | – |  | – |  | – | 2 | secondary bounce |
| 2364.96 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2381.67 | UNCERTAIN |  | 1.00 | baseline_B | 94.2 cm | 1 |  |
| 2384.10 | IN |  | 0.00 | sideline_right | -114.6 cm | 2 |  |
| 2385.62 | IN |  | 0.00 | centreline_B | -225.5 cm | 1 |  |
| 2387.43 | IN |  | 0.00 | kitchen_B | -246.5 cm | 3 |  |
| 2388.10 | – |  | – |  | – | 1 | secondary bounce |
| 2389.10 | IN |  | 0.00 | kitchen_A | -170.6 cm | 1 |  |
| 2390.19 | IN |  | 0.00 | centreline_B | -274.2 cm | 2 |  |
| 2391.28 | – |  | – |  | – | 1 | secondary bounce |
| 2391.85 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2393.45 | IN |  | 0.00 | centreline_B | -236.1 cm | 1 |  |
| 2394.40 | – |  | – |  | – | 2 | secondary bounce |
| 2409.20 | IN |  | 0.00 | centreline_B | -239.5 cm | 1 |  |
| 2410.04 | IN |  | 0.00 | baseline_A | -56.5 cm | 1 |  |
| 2411.50 | UNCERTAIN |  | 0.08 | kitchen_B | -83.7 cm | 2 |  |
| 2411.96 | – |  | – |  | – | 1 | secondary bounce |
| 2412.74 | UNCERTAIN |  | 1.00 | baseline_A | 160.2 cm | 1 |  |
| 2415.41 | IN |  | 0.00 | kitchen_B | -123.9 cm | 1 |  |
| 2416.41 | IN |  | 0.02 | sideline_left | -62.2 cm | 1 |  |
| 2417.90 | IN |  | 0.00 | centreline_A | -149.0 cm | 1 |  |
| 2422.30 | UNCERTAIN |  | 1.00 | baseline_A | 70.8 cm | 1 |  |
| 2423.75 | UNCERTAIN |  | 1.00 | sideline_left | 38.3 cm | 1 | unconfirmed by iphone15pro |
| 2423.90 | – |  | – |  | – | 1 | secondary bounce |
| 2425.71 | UNCERTAIN |  | 1.00 | baseline_B | 25.4 cm | 1 | unconfirmed by iphone15pro |
| 2426.37 | IN |  | 0.00 | sideline_left | -117.5 cm | 1 |  |
| 2427.08 | – |  | – |  | – | 1 | secondary bounce |
| 2431.85 | UNCERTAIN |  | 0.08 | baseline_A | -19.9 cm | 1 |  |
| 2433.04 | IN |  | 0.00 | kitchen_B | -201.9 cm | 1 |  |
| 2434.07 | IN |  | 0.00 | centreline_A | -270.5 cm | 1 |  |
| 2434.99 | IN |  | 0.03 | sideline_right | -13.8 cm | 1 |  |
| 2441.17 | IN |  | 0.00 | centreline_A | -133.8 cm | 1 |  |
| 2441.60 | – |  | – |  | – | 1 | secondary bounce |
| 2448.94 | IN |  | 0.00 | kitchen_A | -74.9 cm | 1 |  |
| 2449.20 | – |  | – |  | – | 1 | secondary bounce |
| 2449.50 | IN |  | 0.00 | kitchen_A | -132.1 cm | 1 |  |
| 2449.89 | – |  | – |  | – | 1 | secondary bounce |
| 2453.45 | IN |  | 0.00 | centreline_B | -186.0 cm | 1 |  |
| 2455.90 | UNCERTAIN |  | 1.00 | baseline_B | 200.9 cm | 1 |  |
| 2456.76 | IN |  | 0.00 | baseline_B | -100.4 cm | 1 |  |
| 2457.99 | IN |  | 0.00 | centreline_A | -108.9 cm | 2 |  |
| 2459.79 | UNCERTAIN |  | 1.00 | baseline_B | 16.9 cm | 1 | unconfirmed by iphone15pro |
| 2461.52 | IN |  | 0.00 | kitchen_B | -103.6 cm | 1 |  |
| 2462.47 | UNCERTAIN |  | 0.07 | sideline_left | -87.6 cm | 2 |  |
| 2465.10 | UNCERTAIN |  | 1.00 | baseline_B | 227.5 cm | 1 |  |
| 2475.45 | UNCERTAIN |  | 0.23 | sideline_left | -16.9 cm | 3 |  |
| 2476.83 | UNCERTAIN |  | 0.12 | centreline_B | -234.9 cm | 2 |  |
| 2479.02 | UNCERTAIN |  | 1.00 | baseline_A | 170.5 cm | 1 |  |
| 2481.58 | UNCERTAIN |  | 1.00 | sideline_left | 65.8 cm | 1 |  |
| 2486.96 | UNCERTAIN |  | 0.40 | sideline_left | -7.5 cm | 2 |  |
| 2488.36 | IN |  | 0.00 | kitchen_B | -82.8 cm | 1 |  |
| 2488.81 | – |  | – |  | – | 1 | secondary bounce |
| 2489.23 | – |  | – |  | – | 1 | secondary bounce |
| 2490.65 | UNCERTAIN |  | 1.00 | baseline_B | 255.1 cm | 1 |  |
| 2491.36 | – |  | – |  | – | 1 | secondary bounce |
| 2497.09 | IN |  | 0.00 | baseline_A | -80.6 cm | 2 | serve from B right |
| 2498.72 | UNCERTAIN |  | 0.13 | centreline_B | -176.6 cm | 2 |  |
| 2500.25 | IN |  | 0.00 | kitchen_A | -124.0 cm | 2 |  |
| 2503.35 | UNCERTAIN |  | 0.22 | kitchen_A | -23.9 cm | 2 |  |
| 2504.67 | UNCERTAIN |  | 0.73 | centreline_B | 48.0 cm | 2 | serve from A left |
| 2509.01 | IN |  | 0.00 | centreline_A | -87.6 cm | 1 |  |
| 2513.90 | UNCERTAIN |  | 1.00 | sideline_left | 197.5 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 2514.35 | – |  | – |  | – | 1 | secondary bounce |
| 2515.48 | IN |  | 0.00 | sideline_right | -105.8 cm | 1 |  |
| 2516.67 | UNCERTAIN |  | 0.54 | baseline_B | 13.7 cm | 2 |  |
| 2518.84 | UNCERTAIN |  | 1.00 | baseline_B | 76.6 cm | 1 |  |
| 2526.49 | IN |  | 0.00 | baseline_A | -77.3 cm | 2 |  |
| 2529.61 | IN |  | 0.00 | centreline_B | -259.5 cm | 3 |  |
| 2531.37 | IN |  | 0.00 | centreline_A | -209.5 cm | 1 |  |
| 2532.96 | IN |  | 0.00 | kitchen_B | -218.4 cm | 1 |  |
| 2533.65 | – |  | – |  | – | 1 | secondary bounce |
| 2534.45 | UNCERTAIN |  | 0.37 | baseline_B | -6.8 cm | 1 |  |
| 2537.78 | IN |  | 0.00 | centreline_A | -219.8 cm | 1 |  |
| 2538.72 | – |  | – |  | – | 2 | secondary bounce |
| 2541.03 | UNCERTAIN |  | 1.00 | baseline_A | 121.7 cm | 1 | unconfirmed by iphone17 |
| 2544.39 | UNCERTAIN |  | 1.00 | baseline_A | 78.6 cm | 1 | unconfirmed by iphone17 |
| 2545.98 | UNCERTAIN |  | 0.39 | baseline_B | -17.4 cm | 3 |  |
| 2547.84 | UNCERTAIN |  | 1.00 | sideline_left | 7.0 cm | 1 |  |
| 2554.06 | IN |  | 0.00 | centreline_A | -203.4 cm | 1 |  |
| 2555.49 | UNCERTAIN |  | 1.00 | baseline_A | 87.8 cm | 2 |  |
| 2560.48 | UNCERTAIN |  | 0.63 | baseline_A | 4.9 cm | 1 |  |
| 2564.11 | UNCERTAIN |  | 1.00 | baseline_A | 67.4 cm | 1 |  |
| 2565.39 | UNCERTAIN |  | 0.11 | centreline_B | -201.3 cm | 2 |  |
| 2568.18 | UNCERTAIN |  | 0.26 | centreline_B | -108.7 cm | 2 |  |
| 2571.53 | IN |  | 0.00 | centreline_B | -211.5 cm | 1 |  |
| 2574.30 | IN |  | 0.00 | kitchen_B | -197.9 cm | 1 |  |
| 2575.72 | UNCERTAIN |  | 0.08 | baseline_B | -31.1 cm | 1 |  |
| 2577.44 | IN |  | 0.00 | centreline_A | -124.3 cm | 2 |  |
| 2584.64 | UNCERTAIN |  | 0.13 | kitchen_B | -121.9 cm | 3 | serve from A right |
| 2586.21 | IN |  | 0.00 | centreline_A | -206.5 cm | 2 |  |
| 2586.62 | UNCERTAIN |  | 1.00 | sideline_left | 82.7 cm | 1 |  |
| 2587.04 | OUT | **OUT** | 1.00 | sideline_left | 288.5 cm | 1 |  |
| 2587.94 | IN |  | 0.00 | centreline_A | -187.4 cm | 2 |  |
| 2597.62 | IN |  | 0.00 | centreline_A | -123.8 cm | 2 |  |
| 2601.19 | UNCERTAIN |  | 1.00 | baseline_A | 102.8 cm | 1 |  |
| 2602.46 | UNCERTAIN |  | 0.65 | centreline_B | 31.2 cm | 2 | serve from A left |
| 2605.74 | IN |  | 0.00 | centreline_A | -274.5 cm | 2 |  |
| 2607.09 | UNCERTAIN |  | 0.38 | sideline_left | -7.5 cm | 2 |  |
| 2608.27 | UNCERTAIN |  | 1.00 | sideline_left | 187.6 cm | 1 | silent: one camera, 12 m away, looking across the sideline_left |
| 2609.07 | IN |  | 0.00 | sideline_left | -51.1 cm | 1 |  |
| 2610.31 | UNCERTAIN |  | 0.39 | kitchen_A | -125.8 cm | 2 |  |
| 2611.06 | – |  | – |  | – | 2 | secondary bounce |
| 2611.68 | – |  | – |  | – | 1 | secondary bounce |
| 2621.11 | UNCERTAIN |  | 0.32 | centreline_B | -134.9 cm | 2 | serve from A right |
| 2622.71 | IN |  | 0.00 | centreline_A | -144.5 cm | 1 |  |
| 2623.78 | UNCERTAIN |  | 0.14 | baseline_B | -22.7 cm | 1 |  |
| 2624.82 | IN |  | 0.00 | kitchen_A | -94.7 cm | 3 |  |
| 2630.40 | UNCERTAIN |  | 0.34 | centreline_B | -119.0 cm | 2 | serve from A right |
| 2633.13 | IN |  | 0.00 | sideline_right | -106.9 cm | 1 |  |
| 2643.16 | IN |  | 0.00 | sideline_right | -154.4 cm | 2 |  |
| 2644.56 | IN |  | 0.00 | kitchen_B | -195.6 cm | 2 |  |
| 2646.77 | UNCERTAIN |  | 1.00 | baseline_B | 108.6 cm | 1 |  |
| 2660.15 | UNCERTAIN |  | 0.08 | kitchen_B | -83.8 cm | 2 | serve from A (half unknown) |
| 2662.01 | IN |  | 0.00 | kitchen_B | -107.5 cm | 2 |  |
| 2662.57 | UNCERTAIN |  | 1.00 | baseline_A | 363.0 cm | 1 |  |
| 2672.57 | IN |  | 0.00 | sideline_left | -96.9 cm | 1 |  |
| 2673.28 | UNCERTAIN |  | 1.00 | baseline_A | 27.0 cm | 1 | unconfirmed by iphone17 |
| 2673.64 | IN |  | 0.00 | centreline_A | -143.6 cm | 2 |  |
| 2675.02 | IN |  | 0.00 | centreline_B | -245.5 cm | 3 |  |
| 2677.71 | OUT | **OUT** | 1.00 | sideline_left | 105.1 cm | 3 |  |
| 2680.97 | UNCERTAIN |  | 1.00 | baseline_A | 89.7 cm | 2 |  |
| 2684.48 | UNCERTAIN |  | 0.36 | centreline_B | -26.1 cm | 3 | serve from A right |
| 2687.79 | UNCERTAIN |  | 0.99 | baseline_B | 52.1 cm | 1 |  |
| 2688.73 | IN |  | 0.00 | kitchen_B | -70.6 cm | 1 |  |
| 2689.06 | IN |  | 0.00 | sideline_left | -117.9 cm | 1 |  |
| 2689.89 | – |  | – |  | – | 1 | secondary bounce |
| 2692.98 | UNCERTAIN |  | 1.00 | baseline_A | 122.3 cm | 1 |  |
| 2694.25 | IN |  | 0.00 | centreline_B | -191.7 cm | 1 |  |
| 2695.46 | IN |  | 0.00 | kitchen_B | -158.2 cm | 1 |  |
| 2696.18 | IN |  | 0.00 | kitchen_A | -147.6 cm | 1 |  |
| 2696.53 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2698.27 | UNCERTAIN |  | 0.40 | kitchen_A | -49.8 cm | 2 |  |
| 2698.92 | IN |  | 0.00 | kitchen_B | -34.7 cm | 1 |  |
| 2701.31 | IN |  | 0.00 | kitchen_B | -200.2 cm | 1 |  |
| 2702.87 | UNCERTAIN |  | 0.46 | baseline_A | -2.0 cm | 2 |  |
| 2704.48 | UNCERTAIN |  | 1.00 | sideline_right | 283.5 cm | 1 |  |
| 2704.66 | – |  | – |  | – | 1 | secondary bounce |
| 2706.16 | UNCERTAIN |  | 1.00 | baseline_A | 118.9 cm | 2 |  |
| 2707.36 | IN |  | 0.00 | kitchen_B | -225.2 cm | 3 |  |
| 2708.70 | UNCERTAIN |  | 1.00 | sideline_right | 185.4 cm | 1 | unconfirmed by iphone17 |
| 2709.35 | IN |  | 0.00 | centreline_A | -145.3 cm | 2 |  |
| 2710.78 | UNCERTAIN |  | 1.00 | sideline_right | 109.8 cm | 1 | unconfirmed by iphone17 |
| 2711.16 | UNCERTAIN |  | 1.00 | baseline_B | 322.3 cm | 1 |  |
| 2711.52 | UNCERTAIN |  | 1.00 | baseline_B | 208.2 cm | 1 |  |
| 2712.29 | – |  | – |  | – | 1 | secondary bounce |
| 2718.94 | UNCERTAIN |  | 1.00 | sideline_right | 145.1 cm | 1 |  |
| 2719.77 | – |  | – |  | – | 1 | secondary bounce |
| 2719.98 | IN |  | 0.00 | kitchen_B | -208.3 cm | 1 |  |
| 2720.88 | IN |  | 0.00 | centreline_A | -65.5 cm | 1 |  |
| 2722.38 | IN |  | 0.00 | kitchen_B | -178.8 cm | 2 |  |
| 2722.63 | UNCERTAIN |  | 1.00 | sideline_right | 355.3 cm | 1 | unconfirmed by iphone17 |
| 2724.82 | IN |  | 0.00 | kitchen_B | -84.8 cm | 2 |  |
| 2726.27 | UNCERTAIN |  | 0.85 | sideline_left | 88.8 cm | 2 |  |
| 2732.36 | UNCERTAIN |  | 0.37 | baseline_B | -7.5 cm | 1 |  |
| 2733.24 | – |  | – |  | – | 1 | secondary bounce |
| 2733.41 | UNCERTAIN |  | 1.00 | sideline_right | 221.6 cm | 1 | unconfirmed by iphone17 |
| 2733.80 | UNCERTAIN |  | 1.00 | baseline_B | 81.9 cm | 1 |  |
| 2736.72 | UNCERTAIN |  | 1.00 | baseline_A | 203.4 cm | 1 | unconfirmed by iphone17 |
| 2740.05 | IN |  | 0.00 | centreline_B | -288.9 cm | 2 |  |
| 2740.97 | IN |  | 0.01 | centreline_A | -148.9 cm | 2 |  |
| 2742.21 | IN |  | 0.00 | centreline_B | -285.1 cm | 1 |  |
| 2743.53 | UNCERTAIN |  | 0.13 | kitchen_A | -124.9 cm | 2 |  |
| 2744.46 | IN |  | 0.00 | kitchen_B | -173.2 cm | 1 |  |
| 2745.73 | IN |  | 0.00 | kitchen_A | -158.5 cm | 2 |  |
| 2747.33 | IN |  | 0.00 | sideline_left | -102.1 cm | 3 |  |
| 2746.80 | IN |  | 0.00 | kitchen_A | -225.1 cm | 1 |  |
| 2747.91 | – |  | – |  | – | 1 | secondary bounce |
| 2749.17 | UNCERTAIN |  | 1.00 | sideline_right | 317.1 cm | 1 |  |
| 2755.92 | IN |  | 0.00 | sideline_left | -85.8 cm | 1 |  |
| 2756.23 | UNCERTAIN |  | 1.00 | sideline_left | 20.3 cm | 1 |  |
| 2757.10 | – |  | – |  | – | 2 | secondary bounce |
| 2759.08 | UNCERTAIN |  | 1.00 | sideline_right | 334.2 cm | 1 |  |
| 2759.63 | IN |  | 0.04 | baseline_A | -26.4 cm | 1 |  |
| 2760.67 | UNCERTAIN |  | 0.27 | sideline_left | -18.4 cm | 2 |  |
| 2764.68 | IN |  | 0.04 | baseline_A | -97.7 cm | 2 |  |
| 2765.99 | IN |  | 0.00 | centreline_B | -301.4 cm | 2 |  |
| 2767.54 | IN |  | 0.01 | kitchen_A | -215.7 cm | 3 |  |
| 2768.43 | IN |  | 0.00 | kitchen_B | -150.8 cm | 2 |  |
| 2769.82 | IN |  | 0.00 | kitchen_A | -104.4 cm | 1 |  |
| 2770.28 | – |  | – |  | – | 2 | secondary bounce |
| 2779.81 | UNCERTAIN |  | 0.14 | sideline_left | -76.9 cm | 2 |  |
| 2782.81 | UNCERTAIN |  | 0.49 | sideline_left | -2.4 cm | 3 |  |
| 2782.49 | UNCERTAIN |  | 0.50 | baseline_A | -7.8 cm | 2 |  |
| 2783.46 | UNCERTAIN |  | 1.00 | sideline_right | 396.1 cm | 1 | unconfirmed by iphone17 |
| 2788.65 | UNCERTAIN |  | 1.00 | sideline_right | 146.4 cm | 1 | silent: one camera, flight not measured (speed 39 +- 66 m/s) |
| 2792.47 | IN |  | 0.00 | centreline_A | -175.1 cm | 1 |  |
| 2793.84 | IN |  | 0.00 | centreline_B | -282.1 cm | 1 |  |
| 2793.93 | IN |  | 0.00 | kitchen_B | -124.6 cm | 1 |  |
| 2796.86 | IN |  | 0.00 | centreline_B | -185.6 cm | 1 |  |
| 2797.78 | – |  | – |  | – | 1 | secondary bounce |
| 2798.37 | IN |  | 0.00 | kitchen_B | -152.6 cm | 2 |  |
| 2801.03 | IN |  | 0.03 | sideline_left | -14.6 cm | 1 |  |
| 2801.76 | – |  | – |  | – | 1 | secondary bounce |
| 2802.16 | – |  | – |  | – | 1 | secondary bounce |
| 2802.59 | IN |  | 0.03 | sideline_right | -21.2 cm | 1 |  |
| 2803.47 | UNCERTAIN |  | 0.07 | kitchen_B | -125.5 cm | 3 |  |
| 2802.81 | IN |  | 0.00 | kitchen_B | -160.9 cm | 1 |  |
| 2804.45 | UNCERTAIN |  | 0.97 | baseline_B | 30.5 cm | 1 |  |
| 2804.83 | IN |  | 0.00 | kitchen_A | -63.8 cm | 2 |  |
| 2805.65 | UNCERTAIN |  | 1.00 | baseline_B | 63.8 cm | 1 |  |
| 2810.32 | UNCERTAIN |  | 1.00 | baseline_A | 102.6 cm | 1 |  |
| 2813.24 | UNCERTAIN |  | 0.62 | baseline_B | 5.3 cm | 1 |  |
| 2813.57 | – |  | – |  | – | 1 | secondary bounce |
| 2813.82 | – |  | – |  | – | 1 | secondary bounce |
| 2830.35 | UNCERTAIN |  | 1.00 | sideline_left | 53.8 cm | 1 |  |
| 2836.09 | IN |  | 0.03 | sideline_left | -90.1 cm | 2 | serve from B left |
| 2837.45 | IN |  | 0.00 | centreline_B | -261.0 cm | 1 |  |
| 2840.20 | IN |  | 0.00 | kitchen_B | -89.5 cm | 1 |  |
| 2844.03 | IN |  | 0.00 | centreline_A | -294.3 cm | 1 |  |
| 2849.88 | UNCERTAIN |  | 1.00 | baseline_A | 84.6 cm | 1 |  |
| 2851.20 | UNCERTAIN |  | 0.13 | sideline_left | -109.5 cm | 2 |  |
| 2852.58 | IN |  | 0.01 | centreline_A | -231.1 cm | 2 |  |
| 2854.25 | IN |  | 0.00 | sideline_right | -48.9 cm | 1 |  |
| 2858.91 | UNCERTAIN |  | 1.00 | baseline_B | 98.3 cm | 1 | unconfirmed by iphone15pro |
| 2874.75 | IN |  | 0.00 | sideline_right | -130.7 cm | 1 |  |
| 2876.07 | IN |  | 0.00 | centreline_B | -299.4 cm | 1 |  |
| 2877.74 | IN |  | 0.00 | kitchen_B | -83.9 cm | 1 |  |
| 2880.52 | UNCERTAIN |  | 0.26 | kitchen_B | -215.3 cm | 2 |  |
| 2883.85 | UNCERTAIN |  | 0.10 | centreline_B | -213.2 cm | 2 |  |
| 2885.35 | IN |  | 0.00 | kitchen_A | -147.7 cm | 1 |  |
| 2886.30 | UNCERTAIN |  | 0.44 | kitchen_B | -227.8 cm | 2 |  |
| 2887.46 | – |  | – |  | – | 1 | secondary bounce |
| 2895.81 | UNCERTAIN |  | 0.99 | baseline_A | 36.6 cm | 1 |  |
| 2899.61 | UNCERTAIN |  | 0.08 | centreline_B | -236.4 cm | 2 |  |
| 2901.07 | IN |  | 0.00 | centreline_A | -150.5 cm | 1 |  |
| 2901.85 | OUT | **OUT** | 0.99 | sideline_right | 20.4 cm | 1 |  |
| 2902.24 | IN |  | 0.00 | kitchen_A | -84.4 cm | 1 |  |
| 2907.59 | UNCERTAIN |  | 1.00 | sideline_right | 119.4 cm | 1 | unconfirmed by iphone15pro; serve from A (half unknown) |
| 2913.17 | IN |  | 0.00 | kitchen_B | -29.2 cm | 1 |  |
| 2914.10 | – |  | – |  | – | 2 | secondary bounce |
| 2914.40 | IN |  | 0.00 | kitchen_B | -114.1 cm | 1 |  |
| 2914.99 | – |  | – |  | – | 2 | secondary bounce |
| 2914.62 | IN |  | 0.00 | kitchen_B | -126.6 cm | 1 |  |
| 2917.38 | IN |  | 0.00 | centreline_A | -218.4 cm | 1 |  |
| 2918.01 | UNCERTAIN |  | 1.00 | sideline_left | 333.1 cm | 1 |  |
| 2922.95 | UNCERTAIN |  | 1.00 | baseline_A | 48.4 cm | 1 |  |
| 2924.50 | IN |  | 0.00 | baseline_B | -26.9 cm | 1 | serve from A right |
| 2926.29 | IN |  | 0.00 | centreline_A | -207.7 cm | 1 |  |
| 2927.42 | IN |  | 0.00 | kitchen_B | -79.9 cm | 1 |  |
| 2928.50 | UNCERTAIN |  | 0.39 | sideline_left | -12.8 cm | 2 |  |
| 2930.12 | UNCERTAIN |  | 1.00 | sideline_left | 178.9 cm | 1 | unconfirmed by iphone15pro |
| 2939.47 | IN |  | 0.00 | centreline_A | -161.8 cm | 1 |  |
| 2940.96 | UNCERTAIN |  | 0.21 | centreline_B | -163.7 cm | 2 |  |
| 2944.19 | UNCERTAIN |  | 0.49 | kitchen_B | -47.8 cm | 2 |  |
| 2944.82 | – |  | – |  | – | 1 | secondary bounce |
| 2946.64 | UNCERTAIN |  | 0.08 | centreline_B | -238.9 cm | 2 |  |
| 2947.69 | IN |  | 0.00 | centreline_B | -176.9 cm | 2 |  |
| 2948.63 | UNCERTAIN |  | 0.61 | sideline_left | -14.7 cm | 2 |  |
| 2950.30 | UNCERTAIN |  | 1.00 | sideline_left | 175.5 cm | 1 |  |
| 2959.09 | UNCERTAIN |  | 0.36 | baseline_A | -14.1 cm | 2 |  |
| 2965.05 | UNCERTAIN |  | 0.26 | centreline_B | -99.3 cm | 2 | serve from A (half unknown) |
| 2966.53 | IN |  | 0.00 | centreline_A | -244.2 cm | 1 |  |
| 2968.96 | IN |  | 0.00 | kitchen_B | -126.8 cm | 1 |  |
| 2976.32 | IN |  | 0.00 | centreline_A | -199.6 cm | 1 |  |
| 2987.87 | UNCERTAIN |  | 1.00 | baseline_A | 137.2 cm | 1 |  |
| 3072.89 | UNCERTAIN |  | 0.44 | baseline_B | -77.2 cm | 2 | serve from A right |
| 3074.63 | UNCERTAIN |  | 0.92 | baseline_A | 24.3 cm | 1 |  |
| 3075.81 | UNCERTAIN |  | 0.15 | centreline_B | -192.0 cm | 2 |  |
| 3077.62 | UNCERTAIN |  | 0.12 | sideline_left | -10.3 cm | 1 |  |
| 3089.14 | UNCERTAIN |  | 0.37 | centreline_B | -100.6 cm | 2 | serve from A right |
| 3090.79 | IN |  | 0.00 | centreline_A | -161.8 cm | 1 |  |
| 3109.56 | IN |  | 0.00 | sideline_right | -93.8 cm | 1 |  |
| 3119.69 | UNCERTAIN |  | 0.62 | sideline_right | 2.5 cm | 1 |  |
| 3125.34 | UNCERTAIN |  | 0.51 | baseline_B | -53.2 cm | 2 | serve from A right |
| 3134.54 | IN |  | 0.00 | centreline_A | -164.4 cm | 1 |  |
| 3136.08 | UNCERTAIN |  | 0.51 | baseline_B | 2.6 cm | 2 |  |
| 3137.66 | IN |  | 0.00 | centreline_A | -194.5 cm | 1 |  |
| 3143.98 | IN |  | 0.00 | centreline_B | -174.3 cm | 1 |  |
| 3145.28 | IN |  | 0.00 | kitchen_A | -229.2 cm | 1 |  |
| 3147.54 | IN |  | 0.00 | centreline_B | -137.0 cm | 1 |  |
| 3148.48 | IN |  | 0.04 | kitchen_B | -157.3 cm | 2 |  |
| 3149.32 | IN |  | 0.00 | sideline_left | -29.4 cm | 1 |  |
| 3152.83 | UNCERTAIN |  | 1.00 | sideline_right | 284.7 cm | 1 |  |
| 3162.10 | IN |  | 0.00 | baseline_B | -46.7 cm | 1 |  |
| 3164.38 | UNCERTAIN |  | 0.53 | baseline_A | 1.6 cm | 1 |  |
| 3168.44 | UNCERTAIN |  | 1.00 | baseline_B | 46.7 cm | 1 |  |
| 3171.64 | IN |  | 0.00 | centreline_A | -242.9 cm | 1 |  |
| 3180.88 | UNCERTAIN |  | 0.94 | baseline_A | 27.5 cm | 1 |  |
| 3181.35 | UNCERTAIN |  | 0.89 | baseline_A | 22.1 cm | 1 |  |
| 3185.11 | UNCERTAIN |  | 1.00 | baseline_A | 82.7 cm | 1 |  |
| 3185.54 | – |  | – |  | – | 1 | secondary bounce |
| 3186.41 | UNCERTAIN |  | 1.00 | baseline_A | 76.6 cm | 1 |  |
| 3189.30 | UNCERTAIN |  | 1.00 | baseline_A | 128.0 cm | 1 |  |
| 3192.27 | UNCERTAIN |  | 0.19 | kitchen_B | -152.7 cm | 2 |  |
| 3193.37 | – |  | – |  | – | 1 | secondary bounce |
| 3195.50 | UNCERTAIN |  | 0.32 | kitchen_B | -184.5 cm | 2 |  |
| 3195.93 | IN |  | 0.00 | sideline_right | -29.0 cm | 1 |  |
| 3196.78 | IN |  | 0.00 | kitchen_A | -164.0 cm | 1 |  |
| 3197.93 | UNCERTAIN |  | 0.28 | centreline_B | -256.9 cm | 2 |  |
| 3199.26 | IN |  | 0.00 | kitchen_A | -162.4 cm | 1 |  |
| 3200.21 | UNCERTAIN |  | 0.70 | kitchen_B | -30.4 cm | 2 |  |
| 3201.06 | IN |  | 0.00 | kitchen_A | -187.9 cm | 1 |  |
| 3201.91 | UNCERTAIN |  | 1.00 | sideline_left | 111.6 cm | 1 |  |
| 3203.40 | IN |  | 0.00 | kitchen_A | -165.9 cm | 1 |  |
| 3204.32 | UNCERTAIN |  | 1.00 | sideline_left | 92.1 cm | 1 | unconfirmed by iphone17 |
| 3204.96 | – |  | – |  | – | 1 | secondary bounce |
| 3205.38 | IN |  | 0.00 | centreline_B | -222.5 cm | 1 |  |
| 3206.37 | – |  | – |  | – | 1 | secondary bounce |
| 3219.98 | IN |  | 0.00 | centreline_A | -186.4 cm | 1 |  |
| 3221.17 | – |  | – |  | – | 1 | secondary bounce |
| 3222.38 | UNCERTAIN |  | 1.00 | baseline_A | 67.1 cm | 1 |  |
| 3225.72 | UNCERTAIN |  | 0.73 | centreline_B | 47.6 cm | 2 | serve from A left |
| 3227.41 | IN |  | 0.00 | centreline_A | -193.8 cm | 1 |  |
| 3227.88 | – |  | – |  | – | 1 | secondary bounce |
| 3231.68 | UNCERTAIN |  | 0.41 | sideline_left | -1.8 cm | 1 |  |
| 3233.28 | UNCERTAIN |  | 1.00 | sideline_left | 368.3 cm | 1 |  |
| 3242.18 | UNCERTAIN |  | 1.00 | baseline_A | 82.8 cm | 1 |  |
| 3243.66 | IN |  | 0.00 | baseline_B | -36.6 cm | 1 |  |
| 3245.19 | IN |  | 0.00 | centreline_A | -243.5 cm | 1 |  |
| 3245.60 | – |  | – |  | – | 1 | secondary bounce |
| 3246.49 | IN |  | 0.00 | sideline_left | -99.5 cm | 1 |  |
| 3248.29 | IN |  | 0.00 | kitchen_B | -122.9 cm | 1 |  |
| 3248.75 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3253.42 | UNCERTAIN |  | 1.00 | sideline_left | 58.8 cm | 1 |  |
| 3256.01 | UNCERTAIN |  | 0.12 | baseline_A | -56.8 cm | 2 |  |
| 3256.77 | – |  | – |  | – | 1 | secondary bounce |
| 3260.80 | UNCERTAIN |  | 1.00 | baseline_A | 140.0 cm | 1 |  |
| 3262.10 | UNCERTAIN |  | 0.74 | centreline_B | 41.7 cm | 2 | serve from A left |
| 3263.90 | IN |  | 0.00 | centreline_A | -93.5 cm | 1 |  |
| 3267.85 | UNCERTAIN |  | 0.53 | kitchen_A | -2.8 cm | 2 |  |
| 3270.58 | UNCERTAIN |  | 0.25 | baseline_B | -104.3 cm | 2 |  |
| 3273.64 | IN |  | 0.00 | centreline_A | -179.9 cm | 1 |  |
| 3275.29 | IN |  | 0.00 | centreline_B | -290.0 cm | 1 |  |
| 3275.67 | – |  | – |  | – | 1 | secondary bounce |
| 3279.60 | IN |  | 0.00 | kitchen_A | -67.2 cm | 1 |  |
| 3281.57 | IN |  | 0.00 | centreline_B | -180.1 cm | 1 |  |
| 3286.66 | UNCERTAIN |  | 0.10 | sideline_left | -59.1 cm | 2 | serve from B left |
| 3288.56 | UNCERTAIN |  | 0.44 | sideline_left | -1.1 cm | 1 |  |
| 3293.01 | IN |  | 0.00 | sideline_left | -59.2 cm | 1 |  |
| 3294.23 | IN |  | 0.02 | kitchen_A | -141.6 cm | 2 |  |
| 3295.38 | UNCERTAIN |  | 0.36 | kitchen_B | -129.8 cm | 2 |  |
| 3296.95 | UNCERTAIN |  | 1.00 | sideline_left | 41.6 cm | 1 | unconfirmed by iphone17; serve from A right |
| 3298.69 | IN |  | 0.00 | kitchen_A | -85.7 cm | 1 |  |
| 3314.49 | IN |  | 0.00 | centreline_A | -225.6 cm | 1 |  |
| 3317.43 | UNCERTAIN |  | 0.41 | kitchen_A | -190.0 cm | 2 |  |
| 3318.38 | UNCERTAIN |  | 0.50 | baseline_B | -0.6 cm | 2 |  |
| 3320.58 | UNCERTAIN |  | 0.99 | baseline_B | 40.8 cm | 1 |  |
| 3330.62 | UNCERTAIN |  | 0.21 | centreline_B | -116.9 cm | 2 |  |
| 3332.43 | UNCERTAIN |  | 0.12 | centreline_B | -240.2 cm | 2 |  |
| 3332.94 | IN |  | 0.00 | sideline_right | -108.6 cm | 1 |  |
| 3333.80 | IN |  | 0.00 | sideline_right | -78.6 cm | 1 |  |
| 3345.14 | UNCERTAIN |  | 1.00 | baseline_A | 128.4 cm | 1 |  |
| 3346.46 | UNCERTAIN |  | 1.00 | baseline_A | 81.7 cm | 1 |  |
| 3347.74 | UNCERTAIN |  | 1.00 | baseline_A | 111.2 cm | 1 |  |
| 3350.43 | UNCERTAIN |  | 0.21 | kitchen_B | -133.8 cm | 2 |  |
| 3351.98 | IN |  | 0.00 | centreline_A | -255.0 cm | 1 |  |
| 3353.14 | IN |  | 0.00 | kitchen_A | -208.6 cm | 1 |  |
| 3353.70 | IN |  | 0.00 | sideline_left | -24.8 cm | 1 |  |
| 3353.82 | IN |  | 0.00 | kitchen_A | -102.3 cm | 1 |  |
| 3354.00 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3354.54 | – |  | – |  | – | 1 | secondary bounce |
| 3356.56 | IN |  | 0.00 | centreline_A | -170.4 cm | 1 |  |
| 3362.60 | UNCERTAIN |  | 0.66 | centreline_B | 22.7 cm | 2 | serve from A left |
| 3366.48 | UNCERTAIN |  | 1.00 | sideline_right | 135.1 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 3370.05 | UNCERTAIN |  | 1.00 | sideline_left | 62.4 cm | 1 |  |
| 3373.34 | IN |  | 0.01 | centreline_A | -207.9 cm | 2 |  |
| 3374.06 | – |  | – |  | – | 1 | secondary bounce |
| 3374.26 | – |  | – |  | – | 1 | secondary bounce |
| 3378.18 | UNCERTAIN |  | 0.10 | centreline_B | -168.6 cm | 2 |  |
| 3378.91 | – |  | – |  | – | 2 | secondary bounce |
| 3381.59 | UNCERTAIN |  | 1.00 | sideline_right | 252.1 cm | 1 |  |
| 3383.04 | IN |  | 0.02 | sideline_left | -77.3 cm | 2 | serve from B left |
| 3385.10 | UNCERTAIN |  | 0.56 | baseline_B | 14.1 cm | 2 |  |
| 3387.90 | IN |  | 0.00 | centreline_B | -169.4 cm | 1 |  |
| 3389.26 | IN |  | 0.00 | kitchen_A | -186.0 cm | 1 |  |
| 3391.99 | IN |  | 0.01 | centreline_A | -214.8 cm | 2 |  |
| 3395.54 | UNCERTAIN |  | 1.00 | sideline_right | 172.3 cm | 1 |  |
| 3405.85 | UNCERTAIN |  | 0.15 | centreline_B | -220.6 cm | 2 |  |
| 3407.33 | IN |  | 0.00 | kitchen_A | -216.3 cm | 1 |  |
| 3409.24 | UNCERTAIN |  | 0.47 | kitchen_B | -48.2 cm | 2 |  |
| 3409.60 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3409.87 | – |  | – |  | – | 1 | secondary bounce |
| 3410.06 | – |  | – |  | – | 1 | secondary bounce |
| 3411.55 | IN |  | 0.00 | kitchen_A | -199.9 cm | 1 |  |
| 3414.70 | UNCERTAIN |  | 1.00 | baseline_A | 109.7 cm | 1 |  |
| 3416.54 | UNCERTAIN |  | 1.00 | baseline_A | 147.1 cm | 1 |  |
| 3419.32 | UNCERTAIN |  | 0.24 | centreline_B | -198.5 cm | 2 | serve from A (half unknown) |
| 3421.24 | UNCERTAIN |  | 1.00 | baseline_A | 62.6 cm | 1 |  |
| 3421.67 | – |  | – |  | – | 1 | secondary bounce |
| 3422.31 | – |  | – |  | – | 1 | secondary bounce |
| 3448.87 | IN |  | 0.00 | centreline_B | -132.4 cm | 1 | serve from A (half unknown) |
| 3450.58 | IN |  | 0.00 | baseline_A | -45.1 cm | 1 |  |
| 3453.50 | UNCERTAIN |  | 0.19 | kitchen_B | -196.8 cm | 2 |  |
| 3461.31 | UNCERTAIN |  | 1.00 | baseline_A | 155.6 cm | 1 |  |
| 3461.78 | – |  | – |  | – | 1 | secondary bounce |
| 3467.90 | IN |  | 0.00 | centreline_B | -50.3 cm | 1 | serve from A left |
| 3469.39 | IN |  | 0.00 | centreline_B | -235.2 cm | 1 |  |
| 3469.63 | OUT | **OUT** | 1.00 | sideline_right | 24.3 cm | 1 |  |
| 3470.42 | – |  | – |  | – | 1 | secondary bounce |
| 3473.46 | UNCERTAIN |  | 1.00 | baseline_A | 104.3 cm | 1 |  |
| 3473.88 | – |  | – |  | – | 1 | secondary bounce |
| 3474.96 | – |  | – |  | – | 1 | secondary bounce |
| 3477.68 | UNCERTAIN |  | 1.00 | baseline_A | 158.3 cm | 1 |  |
| 3481.15 | UNCERTAIN |  | 0.36 | sideline_left | -147.2 cm | 2 | serve from A right |
| 3482.80 | IN |  | 0.00 | centreline_A | -124.6 cm | 1 |  |
| 3484.41 | UNCERTAIN |  | 1.00 | baseline_A | 135.5 cm | 1 |  |
| 3487.38 | UNCERTAIN |  | 0.35 | centreline_B | -156.1 cm | 2 | serve from A (half unknown) |
| 3489.06 | UNCERTAIN |  | 0.32 | baseline_A | -7.8 cm | 1 |  |
| 3496.32 | UNCERTAIN |  | 1.00 | baseline_A | 69.7 cm | 1 |  |
| 3500.47 | UNCERTAIN |  | 0.89 | centreline_B | 26.5 cm | 2 | serve from A left |
| 3505.42 | UNCERTAIN |  | 1.00 | baseline_A | 112.4 cm | 1 |  |
| 3507.48 | UNCERTAIN |  | 1.00 | baseline_A | 91.1 cm | 1 |  |
| 3508.02 | UNCERTAIN |  | 0.98 | sideline_left | 39.0 cm | 1 |  |
| 3508.68 | UNCERTAIN |  | 0.19 | kitchen_B | -143.9 cm | 2 |  |
| 3509.58 | UNCERTAIN |  | 0.82 | sideline_right | 7.4 cm | 1 |  |
| 3510.02 | – |  | – |  | – | 1 | secondary bounce |
| 3510.52 | UNCERTAIN |  | 0.66 | sideline_left | 2.9 cm | 1 |  |
| 3510.93 | UNCERTAIN |  | 0.79 | sideline_left | -23.0 cm | 2 |  |
| 3512.12 | UNCERTAIN |  | 1.00 | sideline_left | 106.1 cm | 1 |  |
| 3522.10 | UNCERTAIN |  | 0.42 | baseline_A | -8.8 cm | 2 |  |
| 3524.43 | UNCERTAIN |  | 1.00 | baseline_A | 170.9 cm | 1 |  |
| 3527.12 | UNCERTAIN |  | 0.44 | centreline_B | -28.2 cm | 2 | serve from A left |
| 3528.76 | IN |  | 0.00 | baseline_A | -79.4 cm | 1 |  |
| 3530.12 | IN |  | 0.00 | sideline_left | -52.0 cm | 1 |  |
| 3537.85 | IN |  | 0.00 | centreline_A | -101.8 cm | 1 |  |
| 3541.09 | UNCERTAIN |  | 1.00 | baseline_A | 106.8 cm | 1 |  |
| 3542.29 | UNCERTAIN |  | 0.61 | kitchen_B | -17.6 cm | 2 | serve from A right |
| 3544.01 | IN |  | 0.00 | baseline_A | -45.6 cm | 1 |  |
| 3544.52 | UNCERTAIN |  | 1.00 | sideline_left | 90.3 cm | 1 |  |
| 3545.65 | – |  | – |  | – | 1 | secondary bounce |
| 3547.89 | UNCERTAIN |  | 1.00 | sideline_left | 142.0 cm | 1 | unconfirmed by iphone15pro |
| 3548.77 | – |  | – |  | – | 1 | secondary bounce |
| 3558.23 | IN |  | 0.00 | sideline_left | -142.2 cm | 1 |  |
| 3559.06 | OUT | **OUT** | 1.00 | sideline_right | 165.7 cm | 1 |  |
| 3561.30 | UNCERTAIN |  | 1.00 | sideline_right | 182.7 cm | 1 | silent: one camera, flight not measured (speed 23 +- 45 m/s) |
| 3565.99 | IN |  | 0.00 | centreline_B | -156.0 cm | 1 |  |
| 3570.55 | IN |  | 0.00 | centreline_A | -153.8 cm | 1 |  |
| 3572.03 | UNCERTAIN |  | 0.13 | centreline_B | -204.2 cm | 2 |  |
| 3573.92 | IN |  | 0.00 | sideline_right | -88.4 cm | 1 |  |
| 3575.37 | UNCERTAIN |  | 0.51 | kitchen_B | -17.1 cm | 2 |  |
| 3576.32 | – |  | – |  | – | 2 | secondary bounce |
| 3578.16 | UNCERTAIN |  | 1.00 | sideline_left | 19.4 cm | 1 |  |
| 3589.10 | UNCERTAIN |  | 1.00 | baseline_B | 190.9 cm | 1 |  |
| 3593.69 | IN |  | 0.00 | baseline_A | -148.0 cm | 1 |  |
| 3595.16 | IN |  | 0.00 | kitchen_B | -167.3 cm | 1 |  |
| 3599.36 | IN |  | 0.00 | centreline_A | -256.0 cm | 1 |  |
| 3601.20 | IN |  | 0.00 | centreline_A | -269.5 cm | 1 |  |
| 3601.72 | – |  | – |  | – | 1 | secondary bounce |
| 3602.43 | – |  | – |  | – | 1 | secondary bounce |
| 3606.85 | IN |  | 0.00 | sideline_left | -98.3 cm | 1 |  |
| 3607.55 | – |  | – |  | – | 1 | secondary bounce |
| 3608.80 | UNCERTAIN |  | 0.74 | baseline_B | 51.6 cm | 2 |  |
| 3608.49 | UNCERTAIN |  | 1.00 | baseline_B | 14.0 cm | 1 |  |
| 3609.47 | – |  | – |  | – | 1 | secondary bounce |
| 3612.43 | UNCERTAIN |  | 1.00 | baseline_B | 322.7 cm | 1 |  |
| 3613.36 | IN |  | 0.00 | centreline_A | -169.0 cm | 1 |  |
| 3614.91 | UNCERTAIN |  | 0.31 | centreline_B | -81.1 cm | 2 |  |
| 3616.43 | IN |  | 0.00 | kitchen_B | -78.3 cm | 1 |  |
| 3622.58 | UNCERTAIN |  | 1.00 | baseline_A | 45.5 cm | 1 |  |
| 3623.92 | UNCERTAIN |  | 0.69 | sideline_left | 29.4 cm | 2 |  |
| 3630.38 | UNCERTAIN |  | 1.00 | sideline_left | 80.8 cm | 1 | unconfirmed by iphone17 |
| 3631.95 | IN |  | 0.00 | kitchen_A | -150.4 cm | 1 |  |
| 3633.77 | IN |  | 0.00 | centreline_B | -232.7 cm | 1 |  |
| 3635.85 | IN |  | 0.00 | kitchen_A | -127.4 cm | 1 |  |
| 3644.23 | UNCERTAIN |  | 0.29 | centreline_B | -144.1 cm | 2 | serve from A right |
| 3645.60 | IN |  | 0.00 | centreline_A | -242.5 cm | 1 |  |
| 3647.02 | IN |  | 0.01 | centreline_A | -168.6 cm | 2 |  |
| 3651.93 | UNCERTAIN |  | 1.00 | baseline_A | 47.0 cm | 1 |  |
| 3660.67 | UNCERTAIN |  | 1.00 | baseline_A | 143.9 cm | 1 |  |
| 3662.04 | IN |  | 0.00 | centreline_B | -165.7 cm | 1 |  |
| 3663.49 | IN |  | 0.00 | sideline_left | -148.1 cm | 1 |  |
| 3667.31 | IN |  | 0.00 | centreline_A | -173.1 cm | 2 |  |
| 3669.16 | UNCERTAIN |  | 1.00 | sideline_left | 23.7 cm | 1 | unconfirmed by iphone17 |
| 3671.12 | IN |  | 0.00 | sideline_right | -63.0 cm | 1 |  |
| 3675.86 | UNCERTAIN |  | 1.00 | baseline_A | 129.3 cm | 1 |  |
| 3676.80 | – |  | – |  | – | 1 | secondary bounce |
| 3680.88 | UNCERTAIN |  | 0.33 | baseline_B | -55.1 cm | 2 | serve from A right |
| 3684.04 | UNCERTAIN |  | 0.68 | sideline_left | -2.7 cm | 2 |  |
| 3685.38 | UNCERTAIN |  | 0.29 | sideline_left | -3.3 cm | 1 |  |
| 3687.39 | IN |  | 0.00 | kitchen_B | -112.0 cm | 1 |  |
| 3689.56 | IN |  | 0.02 | baseline_A | -116.2 cm | 2 |  |
| 3695.85 | IN |  | 0.00 | kitchen_B | -97.9 cm | 1 |  |
| 3698.49 | IN |  | 0.00 | centreline_B | -211.7 cm | 1 |  |
| 3704.84 | IN |  | 0.00 | centreline_A | -286.4 cm | 1 |  |
| 3705.63 | – |  | – |  | – | 1 | secondary bounce |
| 3710.50 | UNCERTAIN |  | 0.76 | sideline_left | 5.5 cm | 1 |  |
| 3712.50 | UNCERTAIN |  | 1.00 | baseline_A | 107.3 cm | 1 | silent: one camera, 17 m away, looking across the baseline_A |
| 3720.95 | UNCERTAIN |  | 1.00 | baseline_A | 138.2 cm | 1 |  |
| 3724.23 | UNCERTAIN |  | 1.00 | sideline_right | 126.7 cm | 1 |  |
| 3786.81 | IN |  | 0.00 | sideline_right | -56.6 cm | 1 |  |
| 3787.80 | UNCERTAIN |  | 1.00 | sideline_right | 58.5 cm | 1 | silent: one camera, 11 m away, looking across the sideline_right |
| 3812.08 | UNCERTAIN |  | 0.78 | baseline_B | 57.8 cm | 2 |  |
| 3812.99 | – |  | – |  | – | 1 | secondary bounce |
| 3813.60 | – |  | – |  | – | 1 | secondary bounce |
| 3817.95 | IN |  | 0.00 | centreline_A | -174.1 cm | 1 |  |
| 3819.59 | UNCERTAIN |  | 0.18 | sideline_left | -116.4 cm | 2 |  |
| 3821.31 | UNCERTAIN |  | 0.18 | baseline_B | -150.2 cm | 2 |  |
| 3833.42 | IN |  | 0.00 | kitchen_A | -90.2 cm | 1 |  |
| 3833.94 | – |  | – |  | – | 2 | secondary bounce |
| 3833.71 | IN |  | 0.00 | kitchen_A | -119.2 cm | 1 |  |
| 3839.05 | UNCERTAIN |  | 1.00 | sideline_right | 378.4 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 3839.54 | UNCERTAIN |  | 0.11 | centreline_B | -158.8 cm | 2 |  |
| 3841.29 | IN |  | 0.00 | centreline_A | -217.0 cm | 1 |  |
| 3842.85 | UNCERTAIN |  | 1.00 | baseline_A | 252.3 cm | 1 |  |
| 3843.65 | OUT | **OUT** | 1.00 | sideline_left | 168.5 cm | 1 |  |
| 3848.99 | OUT | **OUT** | 1.00 | sideline_left | 76.4 cm | 2 |  |
| 3853.57 | UNCERTAIN |  | 0.23 | kitchen_B | -197.7 cm | 2 |  |
| 3854.38 | – |  | – |  | – | 2 | secondary bounce |
| 3854.95 | – |  | – |  | – | 1 | secondary bounce |
| 3857.61 | IN |  | 0.00 | centreline_B | -108.3 cm | 1 |  |
| 3860.44 | UNCERTAIN |  | 0.27 | centreline_B | -72.2 cm | 2 |  |
| 3862.46 | UNCERTAIN |  | 0.42 | baseline_B | -19.8 cm | 2 |  |
| 3864.03 | UNCERTAIN |  | 0.09 | centreline_B | -262.4 cm | 2 |  |
| 3868.20 | UNCERTAIN |  | 0.34 | kitchen_B | -147.1 cm | 2 |  |
| 3873.53 | IN |  | 0.00 | kitchen_A | -148.3 cm | 1 |  |
| 3874.01 | UNCERTAIN |  | 1.00 | sideline_left | 256.8 cm | 1 | silent: one camera, flight not measured (speed 15 +- 97 m/s) |
| 3881.62 | UNCERTAIN |  | 0.29 | baseline_B | -100.6 cm | 2 | serve from A right |
| 3883.30 | IN |  | 0.00 | centreline_A | -174.7 cm | 1 |  |
| 3885.61 | IN |  | 0.01 | kitchen_A | -129.8 cm | 2 |  |
| 3888.18 | UNCERTAIN |  | 1.00 | sideline_right | 364.0 cm | 1 |  |
| 3888.72 | – |  | – |  | – | 1 | secondary bounce |
| 3889.13 | – |  | – |  | – | 1 | secondary bounce |
| 3894.13 | UNCERTAIN |  | 0.44 | baseline_B | -20.4 cm | 2 | serve from A (half unknown) |
| 3895.90 | IN |  | 0.00 | centreline_A | -105.5 cm | 1 |  |
| 3897.23 | IN |  | 0.00 | centreline_A | -253.4 cm | 1 |  |
| 3897.67 | UNCERTAIN |  | 0.68 | sideline_left | 2.5 cm | 1 |  |
| 3898.21 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3907.21 | UNCERTAIN |  | 0.38 | baseline_B | -33.1 cm | 2 |  |
| 3912.64 | UNCERTAIN |  | 1.00 | baseline_B | 379.8 cm | 1 |  |
| 3915.30 | UNCERTAIN |  | 0.12 | centreline_B | -204.8 cm | 2 |  |
| 3916.90 | UNCERTAIN |  | 0.14 | centreline_B | -243.5 cm | 2 |  |
| 3919.05 | IN |  | 0.00 | centreline_B | -296.9 cm | 1 |  |
| 3926.25 | UNCERTAIN |  | 1.00 | sideline_right | 360.9 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 3926.87 | – |  | – |  | – | 1 | secondary bounce |
| 3930.85 | IN |  | 0.01 | baseline_A | -33.0 cm | 1 |  |
| 3932.47 | IN |  | 0.00 | kitchen_B | -185.1 cm | 1 |  |
| 3932.87 | – |  | – |  | – | 1 | secondary bounce |
| 3935.70 | IN |  | 0.02 | centreline_A | -215.5 cm | 2 |  |
| 3937.15 | UNCERTAIN |  | 0.47 | sideline_left | -83.6 cm | 2 |  |
| 3936.19 | UNCERTAIN |  | 1.00 | sideline_left | 200.7 cm | 1 | silent: one camera, flight not measured (speed 25 +- 98 m/s) |
| 3937.61 | UNCERTAIN |  | 1.00 | sideline_left | 353.5 cm | 1 | silent: one camera, flight not measured (speed 6 +- 99 m/s) |
| 3940.84 | IN |  | 0.00 | kitchen_B | -113.0 cm | 1 |  |
| 3941.12 | – |  | – |  | – | 1 | secondary bounce |
| 3942.23 | – |  | – |  | – | 1 | secondary bounce |
| 3943.08 | IN |  | 0.00 | baseline_A | -101.2 cm | 1 |  |
| 3957.04 | UNCERTAIN |  | 0.41 | baseline_B | -96.4 cm | 2 | serve from A right |
| 3958.66 | IN |  | 0.00 | centreline_A | -178.4 cm | 1 |  |
| 3960.15 | UNCERTAIN |  | 0.29 | kitchen_B | -180.0 cm | 2 |  |
| 3962.24 | UNCERTAIN |  | 1.00 | baseline_B | 30.9 cm | 1 | unconfirmed by iphone15pro |
| 3968.20 | IN |  | 0.03 | baseline_A | -101.9 cm | 2 |  |
| 3972.91 | UNCERTAIN |  | 0.27 | centreline_B | -79.6 cm | 2 |  |
| 3974.80 | UNCERTAIN |  | 0.70 | baseline_A | 9.4 cm | 1 |  |
| 3976.32 | UNCERTAIN |  | 1.00 | sideline_left | 107.4 cm | 1 |  |
| 3977.21 | – |  | – |  | – | 1 | secondary bounce |
| 3978.16 | – |  | – |  | – | 1 | secondary bounce |
| 3981.20 | IN |  | 0.00 | centreline_B | -114.5 cm | 1 |  |
| 3984.32 | UNCERTAIN |  | 1.00 | baseline_B | 357.0 cm | 1 |  |
| 3985.34 | IN |  | 0.00 | sideline_right | -108.5 cm | 1 |  |
| 3986.82 | UNCERTAIN |  | 0.06 | centreline_B | -251.9 cm | 2 |  |
| 3990.36 | UNCERTAIN |  | 0.70 | baseline_B | 39.5 cm | 2 |  |
| 3991.22 | UNCERTAIN |  | 0.07 | baseline_B | -23.6 cm | 1 |  |
| 3999.72 | IN |  | 0.00 | centreline_A | -233.7 cm | 1 |  |
| 4000.99 | IN |  | 0.00 | sideline_left | -133.2 cm | 1 |  |
| 4002.57 | IN |  | 0.00 | sideline_right | -53.0 cm | 1 |  |
| 4003.49 | IN |  | 0.00 | kitchen_B | -140.9 cm | 1 |  |
| 4003.88 | – |  | – |  | – | 1 | secondary bounce |
| 4004.85 | IN |  | 0.00 | kitchen_A | -129.7 cm | 1 |  |
| 4005.91 | UNCERTAIN |  | 0.29 | kitchen_B | -160.4 cm | 2 |  |
| 4008.87 | IN |  | 0.01 | sideline_left | -16.8 cm | 1 |  |
| 4011.36 | IN |  | 0.00 | kitchen_B | -25.9 cm | 1 |  |
| 4012.74 | IN |  | 0.02 | sideline_left | -117.2 cm | 2 |  |
| 4013.82 | UNCERTAIN |  | 1.00 | sideline_left | 393.2 cm | 1 | silent: one camera, flight not measured (speed 9 +- 26 m/s) |
| 4015.50 | IN |  | 0.03 | sideline_left | -15.3 cm | 1 |  |
| 4016.27 | IN |  | 0.00 | kitchen_A | -82.2 cm | 1 |  |
| 4017.04 | IN |  | 0.00 | sideline_right | -24.5 cm | 1 |  |
| 4017.64 | – |  | – |  | – | 2 | secondary bounce |
| 4018.09 | – |  | – |  | – | 2 | secondary bounce |
| 4022.16 | IN |  | 0.00 | kitchen_A | -111.6 cm | 1 |  |
| 4022.99 | – |  | – |  | – | 1 | secondary bounce |
| 4030.89 | UNCERTAIN |  | 0.28 | baseline_B | -108.5 cm | 2 | serve from A (half unknown) |
| 4032.55 | IN |  | 0.00 | centreline_A | -184.6 cm | 1 |  |
| 4035.06 | UNCERTAIN |  | 1.00 | sideline_right | 324.7 cm | 1 | silent: one camera, 14 m away, looking across the sideline_right |
| 4035.80 | – |  | – |  | – | 1 | secondary bounce |
| 4036.60 | – |  | – |  | – | 1 | secondary bounce |
| 4046.18 | IN |  | 0.00 | kitchen_A | -108.9 cm | 1 |  |
| 4047.17 | – |  | – |  | – | 2 | secondary bounce |
| 4047.47 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 4048.02 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 4047.70 | IN |  | 0.00 | kitchen_A | -218.2 cm | 1 |  |
| 4050.71 | UNCERTAIN |  | 1.00 | baseline_A | 70.4 cm | 1 |  |
| 4053.87 | IN |  | 0.00 | sideline_left | -106.0 cm | 1 |  |
| 4055.82 | OUT | **OUT** | 1.00 | sideline_right | 101.7 cm | 1 |  |
| 4064.20 | UNCERTAIN |  | 0.28 | centreline_B | -89.8 cm | 2 | serve from A (half unknown) |
| 4065.95 | IN |  | 0.00 | centreline_A | -222.4 cm | 1 |  |
| 4068.71 | UNCERTAIN |  | 1.00 | sideline_left | 33.4 cm | 1 |  |
| 4074.97 | IN |  | 0.00 | centreline_A | -221.0 cm | 1 |  |
| 4075.43 | – |  | – |  | – | 1 | secondary bounce |
| 4076.44 | UNCERTAIN |  | 0.43 | centreline_B | -59.6 cm | 2 | serve from A right |
| 4076.94 | UNCERTAIN |  | 1.00 | sideline_right | 322.5 cm | 1 |  |
| 4077.95 | – |  | – |  | – | 2 | secondary bounce |
| 4078.73 | IN |  | 0.00 | centreline_B | -208.2 cm | 1 |  |
| 4079.55 | UNCERTAIN |  | 1.00 | baseline_A | 373.1 cm | 1 |  |
| 4080.25 | IN |  | 0.00 | centreline_A | -262.8 cm | 2 |  |
| 4081.31 | UNCERTAIN |  | 0.14 | centreline_B | -156.5 cm | 2 |  |
| 4082.67 | IN |  | 0.00 | kitchen_A | -122.0 cm | 1 |  |
| 4083.97 | UNCERTAIN |  | 0.11 | kitchen_B | -232.4 cm | 2 |  |
| 4084.40 | UNCERTAIN |  | 1.00 | sideline_right | 98.5 cm | 1 |  |
| 4085.26 | IN |  | 0.01 | centreline_A | -270.4 cm | 2 |  |
| 4086.56 | UNCERTAIN |  | 0.09 | centreline_B | -266.8 cm | 2 |  |
| 4086.99 | – |  | – |  | – | 1 | secondary bounce |
| 4088.55 | IN |  | 0.00 | kitchen_B | -115.6 cm | 1 |  |
| 4090.87 | UNCERTAIN |  | 1.00 | baseline_B | 14.6 cm | 1 | unconfirmed by iphone15pro |
| 4095.70 | IN |  | 0.00 | baseline_B | -86.2 cm | 1 |  |
| 4101.06 | IN |  | 0.01 | centreline_A | -151.6 cm | 2 | serve from B left |
| 4102.56 | UNCERTAIN |  | 0.17 | centreline_B | -135.2 cm | 2 |  |
| 4105.73 | UNCERTAIN |  | 1.00 | baseline_B | 127.6 cm | 1 |  |
| 4106.07 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 4106.54 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 4116.39 | IN |  | 0.00 | kitchen_A | -114.0 cm | 1 |  |
| 4116.89 | – |  | – |  | – | 1 | secondary bounce |
| 4117.56 | IN |  | 0.00 | kitchen_A | -123.6 cm | 1 |  |
| 4119.15 | UNCERTAIN |  | 0.26 | kitchen_B | -184.9 cm | 2 |  |
| 4126.48 | IN |  | 0.00 | centreline_A | -200.5 cm | 1 |  |
| 4129.57 | UNCERTAIN |  | 0.32 | sideline_left | -21.4 cm | 2 |  |
| 4133.85 | UNCERTAIN |  | 0.21 | baseline_B | -147.1 cm | 2 |  |
| 4135.05 | UNCERTAIN |  | 0.56 | baseline_B | 14.2 cm | 2 |  |
| 4141.45 | IN |  | 0.00 | centreline_A | -92.0 cm | 1 |  |
| 4144.76 | UNCERTAIN |  | 0.10 | centreline_B | -175.6 cm | 2 |  |
| 4149.79 | IN |  | 0.00 | baseline_A | -125.0 cm | 1 |  |
| 4151.54 | IN |  | 0.00 | centreline_B | -237.8 cm | 1 |  |
| 4153.49 | UNCERTAIN |  | 0.16 | sideline_left | -138.4 cm | 2 |  |
| 4171.79 | IN |  | 0.00 | sideline_right | -121.2 cm | 1 |  |
| 4173.43 | UNCERTAIN |  | 0.46 | baseline_B | -12.7 cm | 2 |  |
| 4174.83 | UNCERTAIN |  | 0.57 | sideline_left | -8.0 cm | 2 |  |
| 4176.75 | IN |  | 0.00 | kitchen_A | -154.3 cm | 1 |  |
| 4177.68 | IN |  | 0.00 | kitchen_A | -111.4 cm | 1 |  |
| 4178.25 | IN |  | 0.00 | kitchen_A | -106.0 cm | 1 |  |
| 4181.19 | UNCERTAIN |  | 1.00 | sideline_right | 396.1 cm | 1 | silent: one camera, 13 m away, looking across the sideline_right |
| 4182.52 | UNCERTAIN |  | 0.99 | baseline_B | 48.5 cm | 1 |  |
| 4184.73 | UNCERTAIN |  | 1.00 | baseline_B | 28.2 cm | 1 |  |
| 4188.62 | UNCERTAIN |  | 0.20 | sideline_left | -28.0 cm | 2 | serve from B left |
| 4190.30 | UNCERTAIN |  | 0.43 | baseline_B | -20.1 cm | 2 |  |
| 4192.30 | UNCERTAIN |  | 0.43 | sideline_left | -43.6 cm | 2 |  |
| 4234.34 | UNCERTAIN |  | 1.00 | sideline_left | 109.3 cm | 1 |  |
| 4235.13 | UNCERTAIN |  | 0.14 | sideline_left | -129.2 cm | 2 |  |
| 4234.83 | UNCERTAIN |  | 1.00 | baseline_A | 390.2 cm | 1 |  |
| 4236.69 | UNCERTAIN |  | 1.00 | sideline_left | 19.6 cm | 1 | unconfirmed by iphone17 |
| 4236.84 | – |  | – |  | – | 1 | secondary bounce |
| 4238.56 | IN |  | 0.00 | centreline_A | -248.8 cm | 1 |  |
| 4240.06 | UNCERTAIN |  | 1.00 | sideline_left | 100.1 cm | 1 |  |
| 4241.83 | UNCERTAIN |  | 0.25 | kitchen_B | -178.5 cm | 2 |  |
| 4242.37 | – |  | – |  | – | 1 | secondary bounce |
| 4243.27 | IN |  | 0.00 | kitchen_A | -184.7 cm | 1 |  |
| 4244.65 | IN |  | 0.04 | centreline_B | -282.6 cm | 2 |  |
| 4246.70 | UNCERTAIN |  | 0.14 | sideline_left | -30.6 cm | 1 |  |
| 4247.70 | – |  | – |  | – | 1 | secondary bounce |
| 4249.02 | IN |  | 0.00 | sideline_left | -66.4 cm | 1 |  |
| 4249.66 | IN |  | 0.00 | sideline_left | -20.2 cm | 1 |  |
| 4254.14 | UNCERTAIN |  | 1.00 | sideline_left | 15.7 cm | 1 |  |
| 4254.27 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 4261.78 | UNCERTAIN |  | 1.00 | sideline_right | 387.7 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 4264.33 | IN |  | 0.00 | kitchen_B | -203.7 cm | 1 |  |
| 4267.60 | UNCERTAIN |  | 1.00 | sideline_right | 385.1 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 4277.44 | UNCERTAIN |  | 0.76 | baseline_B | 88.2 cm | 2 | serve from A left |
| 4279.34 | IN |  | 0.00 | centreline_A | -236.8 cm | 2 |  |
| 4280.02 | UNCERTAIN |  | 1.00 | sideline_left | 256.1 cm | 1 |  |
| 4281.11 | UNCERTAIN |  | 0.31 | kitchen_B | -173.8 cm | 2 |  |
| 4282.93 | UNCERTAIN |  | 0.84 | baseline_A | 17.0 cm | 1 |  |
| 4286.83 | UNCERTAIN |  | 1.00 | sideline_left | 66.5 cm | 1 | unconfirmed by iphone17 |
| 4287.52 | UNCERTAIN |  | 0.25 | kitchen_B | -84.7 cm | 2 |  |
| 4289.14 | IN |  | 0.00 | centreline_A | -246.3 cm | 1 |  |
| 4291.08 | IN |  | 0.00 | kitchen_A | -192.6 cm | 1 |  |
| 4292.42 | UNCERTAIN |  | 1.00 | baseline_A | 116.7 cm | 1 |  |
| 4293.22 | UNCERTAIN |  | 0.48 | kitchen_B | -29.4 cm | 2 |  |
| 4294.50 | IN |  | 0.00 | centreline_A | -190.4 cm | 2 |  |
| 4295.84 | UNCERTAIN |  | 0.15 | kitchen_B | -212.6 cm | 2 |  |
| 4297.17 | IN |  | 0.00 | kitchen_A | -54.0 cm | 1 |  |
| 4298.61 | IN |  | 0.00 | kitchen_B | -118.5 cm | 1 |  |
| 4302.44 | UNCERTAIN |  | 1.00 | sideline_left | 18.7 cm | 1 | unconfirmed by iphone15pro |
| 4307.84 | IN |  | 0.00 | centreline_A | -163.4 cm | 1 |  |
| 4313.52 | IN |  | 0.00 | centreline_B | -293.9 cm | 1 |  |
| 4315.07 | UNCERTAIN |  | 1.00 | sideline_left | 36.8 cm | 1 | unconfirmed by iphone17 |
| 4324.66 | UNCERTAIN |  | 0.92 | sideline_left | 12.7 cm | 1 |  |
| 4330.86 | IN |  | 0.00 | kitchen_B | -76.0 cm | 1 |  |
| 4333.22 | IN |  | 0.00 | kitchen_B | -83.7 cm | 1 |  |
| 4341.75 | UNCERTAIN |  | 1.00 | sideline_left | 180.6 cm | 1 | serve from B (half unknown); silent: one camera, 10 m away, looking across the sideline_left |
| 4355.64 | UNCERTAIN |  | 0.14 | sideline_left | -31.6 cm | 1 |  |
| 4356.69 | UNCERTAIN |  | 1.00 | sideline_left | 24.6 cm | 1 | unconfirmed by iphone17 |
| 4357.27 | – |  | – |  | – | 1 | secondary bounce |
| 4370.61 | IN |  | 0.00 | centreline_B | -259.7 cm | 1 |  |

## The Mac's load

* Whole machine (8 logical cores): median 17%, 90% of the time below 32%, peak 88%
* BallTracker's camera workers: median 0.33 cores, peak 1.85
* Server process: median 26% of a core
* Busiest other app: WindowServer (median 26% of a core when it was the busiest)

## Warnings

* 120.8 s iphone17: iphone17: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 212.4 s samsung: samsung: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 1651.6 s samsung: samsung moved 122.9 px since it was calibrated: recalibrate it
* 1923.5 s iphone15pro: iphone15pro: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 1944.4 s iphone15pro: iphone15pro moved 398.0 px since it was calibrated: recalibrate it
* 2027.9 s iphone15pro: iphone15pro: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2038.4 s iphone15pro: iphone15pro moved 379.6 px since it was calibrated: recalibrate it
* 2048.9 s iphone15pro: iphone15pro: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2059.5 s iphone15pro: iphone15pro moved 399.8 px since it was calibrated: recalibrate it
* 2218.4 s iphone15pro: iphone15pro moved 101.1 px since it was calibrated: recalibrate it
* 4316.6 s iphone17: iphone17: can't match the image to its calibration frame (covered, dark, or moved a lot?)

## Calibrations

* samsung at 403 s (clicks + lines (auto)): RMS 1.92 px from 12 points; worst point A_right_corner 2.8 px
* samsung at 404 s (clicks + lines (auto)): RMS 1.92 px from 12 points; worst point A_right_corner 2.8 px
* samsung at 405 s (clicks + lines (auto)): RMS 1.92 px from 12 points; worst point A_right_corner 2.8 px
* samsung at 427 s (drift): RMS 1.92 px from 12 points; moved 7.1 px
* samsung at 621 s (drift): RMS 1.68 px from 12 points; moved 4.3 px
* samsung at 1021 s (drift): RMS 1.75 px from 12 points; moved 3.1 px
* iphone17 at 1058 s (clicks + lines (auto)): RMS 0.22 px from 12 points; worst point B_right_corner 0.4 px
* iphone17 at 1073 s (drift): RMS 0.25 px from 12 points; moved 5.7 px
* samsung at 1166 s (drift): RMS 1.46 px from 12 points; moved 7.8 px
* samsung at 1600 s (drift): RMS 1.61 px from 12 points; moved 3.8 px
* iphone17 at 1663 s (drift): RMS 0.06 px from 12 points; moved 5.6 px
* iphone15pro at 1856 s (clicks): RMS 3.61 px from 8 points; worst point A_kitchen_left 5.5 px
* iphone17 at 1857 s (lines (auto, after iphone15pro)): RMS 0.25 px from 12 points; moved 7.8 px
* iphone17 at 1870 s (drift): RMS 0.27 px from 12 points; moved 8.3 px
* iphone15pro at 1877 s (clicks): RMS 3.85 px from 9 points; worst point B_right_corner 6.0 px
* iphone17 at 1879 s (lines (auto, after iphone15pro)): RMS 0.25 px from 12 points; moved 8.1 px
* iphone15pro at 1881 s (clicks): RMS 3.85 px from 9 points; worst point B_right_corner 6.0 px
* iphone17 at 1892 s (drift): RMS 0.35 px from 12 points; moved 8.0 px
* iphone15pro at 2097 s (clicks + lines (auto)): RMS 1.34 px from 12 points; worst point A_left_corner 2.3 px
* iphone17 at 2098 s (lines (auto, after iphone15pro)): RMS 0.25 px from 12 points; moved 8.2 px
* iphone17 at 2113 s (drift): RMS 0.34 px from 12 points; moved 8.8 px
* iphone15pro at 2114 s (drift): RMS 0.74 px from 12 points; moved 49.9 px
* iphone17 at 2261 s (drift): RMS 0.03 px from 12 points; moved 3.0 px
* iphone17 at 3371 s (drift): RMS 0.59 px from 12 points; moved 3.0 px
* iphone17 at 3567 s (drift): RMS 0.19 px from 12 points; moved 3.6 px
* iphone17 at 3619 s (drift): RMS 0.05 px from 12 points; moved 3.6 px
