# Session 20261122-071401

* **When:** 2026-11-22T07:14:01+0530 → not closed cleanly (–)
* **Code:** commit `891df2b54831bb19c763f174ba3154dfc491cd92`; bounce 0.4.0, fusion 0.1.0, phone detector edge_color_motion 1.0.0, protocol 2
* **Command:** `~/Vikram/BallTracker/.venv/bin/bt serve --record`
* **Court:** pickleball, 6.10 × 13.41 m
* **Settings:** {"record": true, "phone_reduction": true, "detector_overrides": {}, "hold_s": 0.6, "window_s": 0.08, "corroborate": true, "play_mode": "match", "weak_rate": 0.4}

## Cameras

| camera | kind | device | frames | dropped | clock rtt / ± | calibration | lowest fps | worst latency | disconnects |
|---|---|---|---|---|---|---|---|---|---|
| samsung | edge | samsung SM-S948B | 173747 | 0 (0.0%) | 25 / ±12.5 ms | 2.13 px | 40 | 109 ms | 2 |
| iphone17 | edge | Apple iPhone 17 | 317058 | 0 (0.0%) | 9 / ±4.7 ms | 0.07 px | 120 | 213 ms | 1 |
| redmi | edge | Xiaomi Redmi 8A Dual | 35188 | 0 (0.0%) | 59 / ±29.3 ms | 3.62 px | 1 | 13 ms | 1 |
| nothing | edge | Nothing A009P | 49613 | 0 (0.0%) | 33 / ±16.5 ms | 1.91 px | 28 | 20 ms | 1 |

## Calls

1580 single-camera reports → 1121 decisions (393 seen by 2+ cameras): IN 561, OUT 25, UNCERTAIN 257, suppressed (2nd bounce) 278
Spoken: 25 (OUT 25, FAULT 0); serves recognised: 62. Delay bounce → call: median 1.33 s, max 2.36 s.

| t (s) | call | spoken | p(out) | line | distance | cameras | note |
|---|---|---|---|---|---|---|---|
| 116.68 | UNCERTAIN |  | 1.00 | sideline_right | 220.9 cm | 1 |  |
| 168.03 | UNCERTAIN |  | 1.00 | sideline_right | 63.8 cm | 1 | silent: one camera, 9 m away, looking across the sideline_right |
| 207.85 | UNCERTAIN |  | 1.00 | baseline_A | 9.2 cm | 1 |  |
| 439.74 | UNCERTAIN |  | 0.09 | kitchen_B | -114.7 cm | 1 |  |
| 462.14 | UNCERTAIN |  | 0.93 | baseline_A | -33.3 cm | 1 | serve from B left |
| 478.62 | UNCERTAIN |  | 1.00 | baseline_A | 140.3 cm | 1 |  |
| 480.73 | IN |  | 0.04 | centreline_A | -112.8 cm | 1 |  |
| 507.71 | UNCERTAIN |  | 1.00 | baseline_B | 226.6 cm | 1 |  |
| 781.08 | IN |  | 0.03 | sideline_right | -10.3 cm | 1 |  |
| 901.17 | UNCERTAIN |  | 1.00 | baseline_B | 120.2 cm | 1 |  |
| 903.99 | IN |  | 0.00 | sideline_right | -106.0 cm | 1 |  |
| 904.72 | – |  | – |  | – | 1 | secondary bounce |
| 906.06 | IN |  | 0.00 | baseline_A | -50.9 cm | 1 |  |
| 920.00 | IN |  | 0.00 | baseline_A | -46.1 cm | 1 |  |
| 921.48 | UNCERTAIN |  | 0.86 | baseline_B | 17.6 cm | 1 |  |
| 923.53 | UNCERTAIN |  | 1.00 | baseline_B | 155.4 cm | 1 |  |
| 927.07 | UNCERTAIN |  | 1.00 | baseline_B | 162.2 cm | 1 |  |
| 928.31 | UNCERTAIN |  | 1.00 | baseline_B | 149.2 cm | 1 |  |
| 929.76 | OUT | **OUT** | 1.00 | baseline_A | 19.5 cm | 1 |  |
| 932.42 | IN |  | 0.00 | centreline_B | -177.7 cm | 1 |  |
| 934.25 | IN |  | 0.00 | centreline_A | -282.7 cm | 1 |  |
| 935.60 | IN |  | 0.00 | kitchen_A | -19.4 cm | 1 |  |
| 935.94 | – |  | – |  | – | 1 | secondary bounce |
| 955.87 | IN |  | 0.00 | centreline_B | -210.8 cm | 1 |  |
| 957.59 | IN |  | 0.00 | centreline_A | -142.2 cm | 1 |  |
| 958.70 | UNCERTAIN |  | 0.20 | sideline_right | -6.0 cm | 1 |  |
| 960.15 | IN |  | 0.00 | kitchen_A | -108.6 cm | 1 |  |
| 963.47 | UNCERTAIN |  | 0.95 | baseline_B | 26.3 cm | 1 |  |
| 963.98 | – |  | – |  | – | 1 | secondary bounce |
| 964.79 | – |  | – |  | – | 1 | secondary bounce |
| 969.03 | UNCERTAIN |  | 1.00 | baseline_B | 125.6 cm | 1 |  |
| 970.56 | IN |  | 0.00 | centreline_A | -159.2 cm | 1 |  |
| 971.90 | IN |  | 0.00 | centreline_B | -164.0 cm | 1 |  |
| 974.09 | OUT | **OUT** | 1.00 | sideline_left | 40.6 cm | 1 |  |
| 976.45 | UNCERTAIN |  | 1.00 | baseline_A | 109.7 cm | 1 |  |
| 981.21 | IN |  | 0.00 | centreline_B | -136.6 cm | 1 |  |
| 993.46 | IN |  | 0.00 | sideline_right | -86.5 cm | 1 |  |
| 997.99 | IN |  | 0.00 | sideline_left | -72.9 cm | 1 |  |
| 998.72 | – |  | – |  | – | 1 | secondary bounce |
| 999.22 | – |  | – |  | – | 1 | secondary bounce |
| 999.44 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1001.11 | IN |  | 0.00 | kitchen_B | -122.5 cm | 1 |  |
| 1004.91 | UNCERTAIN |  | 1.00 | baseline_B | 110.7 cm | 1 |  |
| 1005.92 | – |  | – |  | – | 1 | secondary bounce |
| 1007.46 | UNCERTAIN |  | 1.00 | baseline_B | 111.8 cm | 1 |  |
| 1008.72 | IN |  | 0.00 | centreline_A | -189.9 cm | 1 |  |
| 1010.31 | OUT | **OUT** | 0.96 | sideline_right | 14.7 cm | 1 |  |
| 1012.68 | IN |  | 0.00 | centreline_B | -185.5 cm | 1 |  |
| 1014.71 | IN |  | 0.00 | kitchen_B | -152.8 cm | 1 |  |
| 1015.34 | – |  | – |  | – | 1 | secondary bounce |
| 1024.91 | UNCERTAIN |  | 0.76 | baseline_A | 6.3 cm | 1 |  |
| 1043.55 | IN |  | 0.00 | baseline_B | -44.0 cm | 1 |  |
| 1046.59 | IN |  | 0.00 | kitchen_B | -184.6 cm | 1 |  |
| 1048.81 | IN |  | 0.00 | centreline_A | -192.8 cm | 1 |  |
| 1049.48 | – |  | – |  | – | 1 | secondary bounce |
| 1050.96 | IN |  | 0.00 | baseline_A | -11.1 cm | 1 |  |
| 1051.49 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1051.86 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1052.14 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1052.36 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1060.92 | IN |  | 0.00 | kitchen_B | -73.0 cm | 1 |  |
| 1061.59 | IN |  | 0.00 | kitchen_B | -41.2 cm | 1 |  |
| 1066.36 | IN |  | 0.00 | kitchen_B | -42.4 cm | 1 |  |
| 1069.51 | UNCERTAIN |  | 1.00 | baseline_A | 95.4 cm | 1 |  |
| 1075.87 | IN |  | 0.00 | centreline_B | -188.9 cm | 1 | serve from A (half unknown) |
| 1077.36 | IN |  | 0.00 | centreline_A | -266.2 cm | 1 |  |
| 1078.48 | IN |  | 0.00 | baseline_B | -106.5 cm | 2 |  |
| 1086.38 | IN |  | 0.00 | sideline_right | -43.4 cm | 2 |  |
| 1089.74 | IN |  | 0.00 | baseline_B | -87.5 cm | 2 |  |
| 1091.19 | IN |  | 0.00 | centreline_A | -255.8 cm | 2 |  |
| 1092.56 | IN |  | 0.00 | sideline_left | -6.6 cm | 1 |  |
| 1099.06 | IN |  | 0.00 | baseline_A | -150.1 cm | 2 |  |
| 1104.60 | IN |  | 0.00 | kitchen_B | -130.5 cm | 1 |  |
| 1109.06 | IN |  | 0.00 | kitchen_A | -56.9 cm | 1 |  |
| 1111.67 | IN |  | 0.00 | centreline_A | -177.8 cm | 1 |  |
| 1112.55 | UNCERTAIN |  | 1.00 | sideline_right | 370.0 cm | 1 | silent: one camera, flight not measured (speed 23 +- 31 m/s) |
| 1118.42 | IN |  | 0.00 | sideline_left | -115.5 cm | 2 | serve from A right |
| 1120.00 | IN |  | 0.00 | centreline_A | -157.9 cm | 1 |  |
| 1121.40 | OUT | **OUT** | 1.00 | baseline_B | 59.4 cm | 2 |  |
| 1126.27 | UNCERTAIN |  | 1.00 | baseline_B | 198.1 cm | 1 |  |
| 1128.84 | UNCERTAIN |  | 1.00 | baseline_B | 63.3 cm | 2 |  |
| 1130.29 | IN |  | 0.00 | centreline_A | -144.9 cm | 2 | serve from B right |
| 1131.93 | IN |  | 0.00 | centreline_B | -186.2 cm | 1 |  |
| 1133.09 | UNCERTAIN |  | 1.00 | baseline_A | 104.0 cm | 1 |  |
| 1134.07 | IN |  | 0.00 | centreline_B | -137.1 cm | 1 |  |
| 1136.36 | UNCERTAIN |  | 1.00 | sideline_right | 41.2 cm | 1 | unconfirmed by nothing |
| 1150.18 | IN |  | 0.00 | centreline_B | -124.3 cm | 2 | serve from A right |
| 1151.73 | IN |  | 0.00 | sideline_left | -92.9 cm | 2 |  |
| 1151.97 | – |  | – |  | – | 1 | secondary bounce |
| 1153.57 | IN |  | 0.00 | centreline_A | -269.4 cm | 1 |  |
| 1155.67 | IN |  | 0.00 | sideline_left | -99.3 cm | 2 |  |
| 1156.23 | – |  | – |  | – | 2 | secondary bounce |
| 1156.63 | – |  | – |  | – | 1 | secondary bounce |
| 1166.60 | IN |  | 0.00 | sideline_right | -67.3 cm | 1 |  |
| 1167.22 | IN |  | 0.00 | kitchen_B | -150.0 cm | 2 |  |
| 1168.92 | IN |  | 0.00 | sideline_left | -123.7 cm | 2 |  |
| 1170.97 | IN |  | 0.00 | kitchen_A | -130.2 cm | 2 |  |
| 1171.65 | – |  | – |  | – | 1 | secondary bounce |
| 1172.17 | – |  | – |  | – | 1 | secondary bounce |
| 1172.52 | – |  | – |  | – | 1 | secondary bounce |
| 1172.79 | – |  | – |  | – | 1 | secondary bounce |
| 1182.92 | UNCERTAIN |  | 0.28 | centreline_B | -37.3 cm | 1 |  |
| 1185.54 | IN |  | 0.00 | centreline_B | -231.3 cm | 2 |  |
| 1193.53 | UNCERTAIN |  | 1.00 | baseline_B | 123.9 cm | 1 | unconfirmed by iphone17, nothing |
| 1195.09 | UNCERTAIN |  | 1.00 | baseline_B | 44.7 cm | 2 |  |
| 1196.60 | IN |  | 0.00 | baseline_A | -93.6 cm | 2 |  |
| 1198.22 | IN |  | 0.00 | centreline_B | -168.6 cm | 1 |  |
| 1199.72 | IN |  | 0.00 | sideline_left | -38.3 cm | 2 |  |
| 1200.87 | IN |  | 0.00 | centreline_B | -294.4 cm | 1 |  |
| 1210.31 | IN |  | 0.00 | sideline_right | -106.4 cm | 2 | serve from A left |
| 1211.83 | IN |  | 0.00 | centreline_A | -154.8 cm | 2 |  |
| 1212.92 | IN |  | 0.00 | kitchen_A | -55.6 cm | 1 |  |
| 1213.89 | IN |  | 0.00 | sideline_right | -30.7 cm | 1 |  |
| 1220.61 | UNCERTAIN |  | 1.00 | baseline_B | 132.4 cm | 1 |  |
| 1221.68 | – |  | – |  | – | 1 | secondary bounce |
| 1225.93 | UNCERTAIN |  | 1.00 | baseline_B | 78.7 cm | 2 |  |
| 1227.21 | IN |  | 0.00 | centreline_A | -77.1 cm | 2 | serve from B right |
| 1227.49 | – |  | – |  | – | 1 | secondary bounce |
| 1229.03 | IN |  | 0.00 | baseline_B | -13.6 cm | 2 |  |
| 1230.89 | IN |  | 0.00 | kitchen_B | -162.5 cm | 2 |  |
| 1232.50 | IN |  | 0.00 | sideline_right | -70.3 cm | 2 |  |
| 1234.29 | UNCERTAIN |  | 1.00 | baseline_A | 70.0 cm | 1 | unconfirmed by samsung, iphone17 |
| 1243.03 | IN |  | 0.00 | baseline_B | -10.5 cm | 1 | serve from A left |
| 1244.84 | IN |  | 0.00 | centreline_A | -264.1 cm | 2 |  |
| 1246.01 | UNCERTAIN |  | 0.72 | baseline_B | 11.3 cm | 1 |  |
| 1247.34 | IN |  | 0.00 | sideline_left | -63.8 cm | 2 |  |
| 1249.66 | IN |  | 0.00 | sideline_left | -44.5 cm | 1 |  |
| 1250.03 | IN |  | 0.00 | sideline_left | -49.0 cm | 1 |  |
| 1250.38 | – |  | – |  | – | 1 | secondary bounce |
| 1250.83 | – |  | – |  | – | 1 | secondary bounce |
| 1254.31 | IN |  | 0.00 | centreline_A | -83.5 cm | 2 |  |
| 1258.69 | IN |  | 0.00 | centreline_B | -176.1 cm | 2 |  |
| 1260.43 | IN |  | 0.00 | sideline_left | -86.2 cm | 2 |  |
| 1262.32 | IN |  | 0.00 | kitchen_A | -130.2 cm | 3 |  |
| 1263.02 | – |  | – |  | – | 1 | secondary bounce |
| 1264.36 | UNCERTAIN |  | 1.00 | baseline_B | 195.4 cm | 1 |  |
| 1265.07 | – |  | – |  | – | 1 | secondary bounce |
| 1265.66 | – |  | – |  | – | 1 | secondary bounce |
| 1269.52 | UNCERTAIN |  | 1.00 | baseline_B | 243.9 cm | 1 |  |
| 1272.08 | UNCERTAIN |  | 1.00 | baseline_B | 203.8 cm | 1 |  |
| 1274.01 | UNCERTAIN |  | 1.00 | baseline_B | 195.3 cm | 1 |  |
| 1275.76 | UNCERTAIN |  | 1.00 | baseline_B | 83.0 cm | 2 |  |
| 1277.30 | IN |  | 0.00 | centreline_A | -92.2 cm | 1 |  |
| 1278.88 | IN |  | 0.00 | centreline_B | -84.7 cm | 2 |  |
| 1280.40 | IN |  | 0.00 | baseline_A | -12.2 cm | 1 |  |
| 1285.16 | IN |  | 0.00 | sideline_right | -89.0 cm | 2 |  |
| 1286.70 | UNCERTAIN |  | 1.00 | baseline_B | 262.6 cm | 1 |  |
| 1287.24 | – |  | – |  | – | 1 | secondary bounce |
| 1287.86 | – |  | – |  | – | 1 | secondary bounce |
| 1293.18 | UNCERTAIN |  | 1.00 | baseline_B | 137.7 cm | 1 |  |
| 1294.54 | IN |  | 0.00 | sideline_left | -40.0 cm | 2 |  |
| 1295.89 | IN |  | 0.00 | centreline_B | -263.9 cm | 1 |  |
| 1297.24 | IN |  | 0.00 | sideline_right | -89.7 cm | 1 |  |
| 1303.82 | IN |  | 0.00 | centreline_B | -149.8 cm | 2 | serve from A right |
| 1305.98 | UNCERTAIN |  | 1.00 | baseline_B | 111.8 cm | 1 | unconfirmed by iphone17 |
| 1308.21 | UNCERTAIN |  | 1.00 | baseline_B | 47.1 cm | 2 |  |
| 1309.50 | IN |  | 0.01 | kitchen_B | -19.2 cm | 1 |  |
| 1310.05 | – |  | – |  | – | 1 | secondary bounce |
| 1310.72 | – |  | – |  | – | 1 | secondary bounce |
| 1320.39 | IN |  | 0.00 | centreline_A | -150.1 cm | 2 |  |
| 1326.04 | IN |  | 0.00 | baseline_B | -68.1 cm | 2 | serve from A right |
| 1327.74 | IN |  | 0.00 | centreline_A | -220.2 cm | 2 |  |
| 1329.74 | OUT | **OUT** | 1.00 | baseline_B | 113.8 cm | 2 |  |
| 1331.97 | UNCERTAIN |  | 1.00 | baseline_B | 195.5 cm | 1 |  |
| 1334.15 | UNCERTAIN |  | 1.00 | baseline_B | 74.9 cm | 2 |  |
| 1335.81 | IN |  | 0.00 | baseline_A | -55.3 cm | 1 |  |
| 1337.50 | UNCERTAIN |  | 0.73 | baseline_B | 12.4 cm | 1 |  |
| 1338.35 | UNCERTAIN |  | 0.11 | sideline_right | -10.7 cm | 1 |  |
| 1343.53 | IN |  | 0.00 | centreline_A | -181.0 cm | 1 |  |
| 1348.61 | IN |  | 0.00 | centreline_B | -90.2 cm | 2 | serve from A right |
| 1350.19 | IN |  | 0.00 | centreline_A | -189.2 cm | 2 |  |
| 1351.57 | IN |  | 0.03 | sideline_left | -11.2 cm | 1 |  |
| 1360.37 | IN |  | 0.00 | centreline_A | -159.4 cm | 2 |  |
| 1361.16 | – |  | – |  | – | 2 | secondary bounce |
| 1361.71 | – |  | – |  | – | 1 | secondary bounce |
| 1367.87 | UNCERTAIN |  | 1.00 | baseline_A | 61.7 cm | 1 | unconfirmed by samsung |
| 1370.97 | OUT | **OUT** | 1.00 | sideline_right | 3.6 cm | 2 |  |
| 1376.07 | UNCERTAIN |  | 1.00 | baseline_B | 289.7 cm | 1 |  |
| 1382.94 | UNCERTAIN |  | 1.00 | baseline_B | 54.8 cm | 2 |  |
| 1384.42 | IN |  | 0.00 | centreline_A | -181.2 cm | 2 |  |
| 1385.75 | IN |  | 0.00 | centreline_B | -149.7 cm | 2 |  |
| 1387.95 | IN |  | 0.00 | sideline_right | -76.7 cm | 2 |  |
| 1389.08 | IN |  | 0.00 | baseline_B | -35.8 cm | 2 |  |
| 1391.78 | UNCERTAIN |  | 1.00 | sideline_right | 74.7 cm | 1 |  |
| 1395.79 | IN |  | 0.00 | centreline_A | -244.3 cm | 2 |  |
| 1396.47 | – |  | – |  | – | 2 | secondary bounce |
| 1396.80 | – |  | – |  | – | 1 | secondary bounce |
| 1401.19 | UNCERTAIN |  | 1.00 | sideline_right | 30.2 cm | 1 | unconfirmed by samsung |
| 1403.25 | IN |  | 0.00 | kitchen_A | -105.9 cm | 2 |  |
| 1414.80 | UNCERTAIN |  | 1.00 | baseline_B | 213.2 cm | 1 |  |
| 1422.98 | UNCERTAIN |  | 1.00 | baseline_B | 83.4 cm | 1 |  |
| 1424.48 | IN |  | 0.00 | sideline_right | -81.8 cm | 2 |  |
| 1425.61 | UNCERTAIN |  | 0.43 | sideline_right | -1.5 cm | 1 |  |
| 1426.43 | IN |  | 0.00 | sideline_right | -42.2 cm | 1 |  |
| 1431.85 | UNCERTAIN |  | 0.76 | baseline_B | 12.8 cm | 1 |  |
| 1434.16 | UNCERTAIN |  | 1.00 | baseline_B | 154.2 cm | 1 |  |
| 1437.74 | UNCERTAIN |  | 1.00 | baseline_B | 112.2 cm | 1 |  |
| 1439.34 | IN |  | 0.00 | sideline_left | -51.8 cm | 1 |  |
| 1440.84 | UNCERTAIN |  | 1.00 | sideline_left | 39.1 cm | 1 | unconfirmed by samsung |
| 1442.43 | UNCERTAIN |  | 1.00 | baseline_B | 193.7 cm | 1 |  |
| 1446.55 | UNCERTAIN |  | 1.00 | baseline_B | 89.2 cm | 2 |  |
| 1448.11 | IN |  | 0.00 | centreline_A | -164.0 cm | 1 |  |
| 1449.36 | IN |  | 0.00 | kitchen_B | -173.7 cm | 2 |  |
| 1453.38 | IN |  | 0.00 | baseline_B | -12.5 cm | 1 |  |
| 1461.43 | IN |  | 0.00 | sideline_right | -78.4 cm | 1 |  |
| 1461.95 | – |  | – |  | – | 1 | secondary bounce |
| 1465.58 | IN |  | 0.00 | sideline_right | -103.9 cm | 2 | serve from A left |
| 1467.07 | IN |  | 0.00 | kitchen_A | -207.3 cm | 2 |  |
| 1467.41 | IN |  | 0.00 | kitchen_A | -224.3 cm | 1 |  |
| 1469.25 | IN |  | 0.00 | sideline_left | -86.4 cm | 2 |  |
| 1471.46 | IN |  | 0.00 | sideline_right | -143.2 cm | 2 |  |
| 1472.70 | UNCERTAIN |  | 0.44 | sideline_right | -6.9 cm | 2 |  |
| 1473.25 | IN |  | 0.01 | sideline_right | -77.1 cm | 3 |  |
| 1473.68 | – |  | – |  | – | 2 | secondary bounce |
| 1473.97 | – |  | – |  | – | 1 | secondary bounce |
| 1474.20 | – |  | – |  | – | 2 | secondary bounce |
| 1474.63 | – |  | – |  | – | 1 | secondary bounce |
| 1478.71 | IN |  | 0.00 | centreline_B | -184.5 cm | 2 |  |
| 1482.89 | UNCERTAIN |  | 1.00 | baseline_B | 74.4 cm | 2 |  |
| 1484.53 | IN |  | 0.00 | centreline_A | -95.5 cm | 2 |  |
| 1485.93 | IN |  | 0.00 | centreline_B | -246.6 cm | 2 |  |
| 1495.24 | IN |  | 0.00 | sideline_right | -50.7 cm | 1 | serve from A left |
| 1496.55 | IN |  | 0.00 | centreline_A | -214.5 cm | 2 |  |
| 1498.35 | UNCERTAIN |  | 0.09 | sideline_right | -6.8 cm | 1 |  |
| 1499.01 | – |  | – |  | – | 1 | secondary bounce |
| 1500.33 | UNCERTAIN |  | 1.00 | sideline_right | 177.8 cm | 1 | silent: one camera, flight not measured (speed 34 +- 48 m/s) |
| 1506.88 | UNCERTAIN |  | 1.00 | baseline_B | 125.3 cm | 1 |  |
| 1508.91 | UNCERTAIN |  | 1.00 | baseline_B | 134.0 cm | 1 | unconfirmed by iphone17 |
| 1510.44 | UNCERTAIN |  | 1.00 | baseline_B | 136.3 cm | 1 |  |
| 1512.02 | IN |  | 0.00 | baseline_A | -27.3 cm | 2 |  |
| 1513.37 | UNCERTAIN |  | 0.39 | sideline_right | -2.1 cm | 1 |  |
| 1513.85 | IN |  | 0.00 | sideline_right | -25.5 cm | 1 |  |
| 1514.68 | – |  | – |  | – | 1 | secondary bounce |
| 1520.19 | OUT | **OUT** | 1.00 | sideline_right | 41.1 cm | 2 |  |
| 1521.38 | – |  | – |  | – | 1 | secondary bounce |
| 1523.60 | UNCERTAIN |  | 1.00 | baseline_B | 240.4 cm | 1 |  |
| 1529.42 | IN |  | 0.00 | centreline_B | -70.8 cm | 2 |  |
| 1530.91 | IN |  | 0.00 | baseline_A | -43.1 cm | 1 |  |
| 1535.87 | IN |  | 0.00 | centreline_B | -184.0 cm | 2 |  |
| 1537.77 | UNCERTAIN |  | 1.00 | baseline_B | 102.0 cm | 1 | unconfirmed by iphone17 |
| 1539.75 | UNCERTAIN |  | 1.00 | baseline_B | 129.3 cm | 1 |  |
| 1541.16 | IN |  | 0.00 | sideline_right | -99.6 cm | 2 | serve from B right |
| 1542.37 | IN |  | 0.00 | sideline_right | -24.6 cm | 2 |  |
| 1544.00 | IN |  | 0.00 | kitchen_A | -179.0 cm | 2 |  |
| 1550.35 | IN |  | 0.00 | sideline_left | -128.3 cm | 3 |  |
| 1551.12 | – |  | – |  | – | 2 | secondary bounce |
| 1551.39 | – |  | – |  | – | 1 | secondary bounce |
| 1551.68 | IN |  | 0.00 | centreline_A | -169.1 cm | 1 |  |
| 1555.85 | IN |  | 0.00 | baseline_B | -59.6 cm | 1 |  |
| 1557.38 | IN |  | 0.00 | sideline_left | -146.6 cm | 2 |  |
| 1558.59 | IN |  | 0.00 | sideline_left | -63.8 cm | 2 |  |
| 1564.30 | UNCERTAIN |  | 0.89 | sideline_right | 4.6 cm | 1 |  |
| 1570.46 | IN |  | 0.00 | sideline_left | -56.3 cm | 1 |  |
| 1570.92 | – |  | – |  | – | 1 | secondary bounce |
| 1573.06 | UNCERTAIN |  | 1.00 | baseline_B | 72.2 cm | 1 |  |
| 1575.36 | UNCERTAIN |  | 1.00 | baseline_B | 228.4 cm | 1 |  |
| 1582.00 | UNCERTAIN |  | 1.00 | baseline_B | 91.5 cm | 2 |  |
| 1583.66 | IN |  | 0.00 | baseline_A | -29.4 cm | 1 |  |
| 1585.48 | IN |  | 0.00 | centreline_B | -231.3 cm | 2 |  |
| 1587.00 | IN |  | 0.00 | sideline_left | -116.3 cm | 1 |  |
| 1589.08 | IN |  | 0.00 | sideline_right | -106.1 cm | 2 |  |
| 1591.15 | IN |  | 0.00 | centreline_A | -259.9 cm | 1 |  |
| 1591.48 | IN |  | 0.00 | kitchen_A | -88.5 cm | 1 |  |
| 1591.95 | UNCERTAIN |  | 0.41 | kitchen_B | -13.9 cm | 2 |  |
| 1592.31 | IN |  | 0.00 | kitchen_A | -77.4 cm | 2 |  |
| 1592.86 | – |  | – |  | – | 1 | secondary bounce |
| 1593.03 | – |  | – |  | – | 1 | secondary bounce |
| 1595.42 | UNCERTAIN |  | 1.00 | baseline_B | 263.7 cm | 1 |  |
| 1596.06 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 1596.52 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1596.85 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1597.80 | – |  | – |  | – | 1 | secondary bounce |
| 1601.16 | UNCERTAIN |  | 1.00 | baseline_B | 142.6 cm | 1 |  |
| 1602.44 | IN |  | 0.00 | centreline_A | -171.6 cm | 1 |  |
| 1603.92 | IN |  | 0.00 | sideline_left | -107.4 cm | 2 |  |
| 1605.66 | IN |  | 0.00 | sideline_right | -71.2 cm | 1 |  |
| 1606.26 | – |  | – |  | – | 1 | secondary bounce |
| 1611.23 | IN |  | 0.00 | centreline_A | -258.4 cm | 2 |  |
| 1612.08 | – |  | – |  | – | 1 | secondary bounce |
| 1616.96 | UNCERTAIN |  | 1.00 | baseline_A | 106.2 cm | 1 | unconfirmed by samsung, iphone17 |
| 1619.17 | IN |  | 0.00 | centreline_B | -172.1 cm | 1 |  |
| 1620.86 | IN |  | 0.00 | baseline_A | -62.4 cm | 2 |  |
| 1630.42 | UNCERTAIN |  | 1.00 | baseline_B | 163.1 cm | 1 |  |
| 1633.67 | IN |  | 0.00 | baseline_B | -95.5 cm | 1 |  |
| 1640.52 | IN |  | 0.00 | sideline_left | -74.9 cm | 2 | serve from A right |
| 1642.19 | IN |  | 0.00 | sideline_right | -62.4 cm | 2 |  |
| 1643.98 | IN |  | 0.00 | centreline_A | -204.6 cm | 2 |  |
| 1646.20 | IN |  | 0.00 | kitchen_A | -142.4 cm | 2 |  |
| 1647.00 | – |  | – |  | – | 2 | secondary bounce |
| 1647.61 | – |  | – |  | – | 2 | secondary bounce |
| 1658.30 | UNCERTAIN |  | 1.00 | baseline_B | 21.2 cm | 1 | unconfirmed by iphone17 |
| 1664.76 | IN |  | 0.00 | centreline_A | -185.1 cm | 1 |  |
| 1665.96 | IN |  | 0.00 | kitchen_B | -233.8 cm | 1 |  |
| 1667.55 | IN |  | 0.00 | sideline_left | -135.4 cm | 1 |  |
| 1675.14 | UNCERTAIN |  | 0.17 | centreline_A | -20.0 cm | 1 |  |
| 1678.10 | IN |  | 0.00 | centreline_B | -165.1 cm | 1 |  |
| 1679.28 | IN |  | 0.00 | kitchen_B | -18.7 cm | 1 |  |
| 1680.04 | – |  | – |  | – | 2 | secondary bounce |
| 1683.77 | IN |  | 0.00 | centreline_B | -175.0 cm | 1 |  |
| 1685.90 | IN |  | 0.00 | kitchen_B | -150.3 cm | 1 |  |
| 1687.07 | UNCERTAIN |  | 1.00 | sideline_left | 163.0 cm | 2 |  |
| 1687.90 | – |  | – |  | – | 1 | secondary bounce |
| 1694.95 | IN |  | 0.00 | kitchen_A | -238.5 cm | 1 |  |
| 1696.05 | UNCERTAIN |  | 1.00 | sideline_left | 130.3 cm | 1 |  |
| 1697.44 | IN |  | 0.00 | kitchen_B | -103.7 cm | 1 |  |
| 1697.82 | UNCERTAIN |  | 0.96 | sideline_left | 13.8 cm | 1 | unconfirmed by iphone17 |
| 1698.77 | – |  | – |  | – | 2 | secondary bounce |
| 1701.01 | IN |  | 0.00 | kitchen_A | -147.8 cm | 1 |  |
| 1702.88 | IN |  | 0.00 | kitchen_A | -88.3 cm | 1 |  |
| 1703.55 | – |  | – |  | – | 2 | secondary bounce |
| 1709.74 | IN |  | 0.00 | sideline_right | -38.4 cm | 2 |  |
| 1710.74 | IN |  | 0.00 | kitchen_B | -58.0 cm | 1 |  |
| 1721.32 | IN |  | 0.00 | kitchen_A | -79.2 cm | 1 |  |
| 1723.14 | UNCERTAIN |  | 1.00 | baseline_A | 334.7 cm | 1 |  |
| 1723.50 | UNCERTAIN |  | 1.00 | baseline_A | 88.3 cm | 1 |  |
| 1724.98 | IN |  | 0.00 | kitchen_B | -14.2 cm | 2 |  |
| 1725.53 | – |  | – |  | – | 2 | secondary bounce |
| 1729.67 | IN |  | 0.00 | kitchen_A | -143.2 cm | 1 |  |
| 1731.88 | IN |  | 0.00 | kitchen_B | -199.7 cm | 1 |  |
| 1734.51 | IN |  | 0.00 | kitchen_B | -177.0 cm | 1 |  |
| 1735.82 | IN |  | 0.00 | kitchen_A | -162.7 cm | 1 |  |
| 1736.53 | IN |  | 0.00 | kitchen_B | -69.5 cm | 1 |  |
| 1743.85 | IN |  | 0.00 | sideline_left | -28.8 cm | 1 |  |
| 1752.40 | IN |  | 0.00 | kitchen_B | -154.1 cm | 1 |  |
| 1753.05 | – |  | – |  | – | 1 | secondary bounce |
| 1764.86 | IN |  | 0.00 | centreline_B | -262.5 cm | 1 |  |
| 1766.20 | IN |  | 0.00 | centreline_B | -153.1 cm | 1 |  |
| 1768.83 | IN |  | 0.02 | kitchen_B | -197.0 cm | 2 |  |
| 1769.54 | IN |  | 0.00 | kitchen_A | -147.5 cm | 2 |  |
| 1771.37 | UNCERTAIN |  | 0.15 | sideline_right | -2.5 cm | 1 |  |
| 1773.45 | IN |  | 0.00 | kitchen_A | -48.6 cm | 1 |  |
| 1778.05 | IN |  | 0.00 | kitchen_A | -171.4 cm | 1 |  |
| 1778.34 | – |  | – |  | – | 1 | secondary bounce |
| 1779.22 | IN |  | 0.00 | sideline_left | -56.6 cm | 1 |  |
| 1780.31 | – |  | – |  | – | 2 | secondary bounce |
| 1780.95 | – |  | – |  | – | 1 | secondary bounce |
| 1782.82 | IN |  | 0.00 | kitchen_A | -162.0 cm | 2 |  |
| 1784.01 | IN |  | 0.00 | kitchen_B | -130.9 cm | 1 |  |
| 1785.16 | UNCERTAIN |  | 0.67 | sideline_left | 5.6 cm | 1 |  |
| 1787.36 | UNCERTAIN |  | 1.00 | baseline_A | 222.9 cm | 1 |  |
| 1788.26 | IN |  | 0.00 | kitchen_B | -94.7 cm | 1 |  |
| 1788.63 | – |  | – |  | – | 1 | secondary bounce |
| 1789.80 | IN |  | 0.01 | sideline_right | -34.4 cm | 1 |  |
| 1790.37 | – |  | – |  | – | 1 | secondary bounce |
| 1791.99 | UNCERTAIN |  | 0.08 | kitchen_A | -16.5 cm | 1 |  |
| 1792.54 | – |  | – |  | – | 1 | secondary bounce |
| 1792.93 | – |  | – |  | – | 1 | secondary bounce |
| 1794.89 | IN |  | 0.00 | kitchen_B | -132.7 cm | 1 |  |
| 1797.64 | UNCERTAIN |  | 1.00 | sideline_left | 71.3 cm | 1 | unconfirmed by iphone17 |
| 1798.31 | IN |  | 0.00 | kitchen_B | -132.8 cm | 1 |  |
| 1798.84 | UNCERTAIN |  | 1.00 | baseline_A | 310.1 cm | 1 |  |
| 1800.22 | IN |  | 0.00 | kitchen_A | -52.7 cm | 1 |  |
| 1804.33 | IN |  | 0.02 | kitchen_B | -17.2 cm | 1 |  |
| 1804.84 | – |  | – |  | – | 1 | secondary bounce |
| 1805.20 | – |  | – |  | – | 1 | secondary bounce |
| 1805.48 | – |  | – |  | – | 1 | secondary bounce |
| 1806.86 | IN |  | 0.00 | centreline_A | -245.8 cm | 1 |  |
| 1807.20 | IN |  | 0.00 | sideline_right | -82.9 cm | 1 |  |
| 1809.65 | IN |  | 0.00 | sideline_left | -84.9 cm | 1 |  |
| 1810.44 | IN |  | 0.00 | kitchen_A | -125.2 cm | 1 |  |
| 1811.79 | IN |  | 0.00 | kitchen_B | -128.6 cm | 1 |  |
| 1813.09 | IN |  | 0.00 | kitchen_A | -124.6 cm | 1 |  |
| 1814.20 | IN |  | 0.00 | kitchen_B | -111.3 cm | 1 |  |
| 1815.55 | IN |  | 0.00 | kitchen_A | -138.2 cm | 1 |  |
| 1817.01 | IN |  | 0.00 | kitchen_B | -83.8 cm | 2 |  |
| 1818.57 | OUT | **OUT** | 1.00 | sideline_right | 12.6 cm | 2 |  |
| 1820.22 | IN |  | 0.00 | sideline_left | -51.2 cm | 1 |  |
| 1821.44 | IN |  | 0.00 | kitchen_B | -136.3 cm | 1 |  |
| 1821.78 | UNCERTAIN |  | 0.25 | sideline_left | -7.0 cm | 1 |  |
| 1825.74 | IN |  | 0.00 | kitchen_A | -106.9 cm | 1 |  |
| 1827.25 | IN |  | 0.00 | sideline_right | -56.0 cm | 1 |  |
| 1830.03 | IN |  | 0.00 | kitchen_A | -47.7 cm | 1 |  |
| 1833.72 | IN |  | 0.00 | kitchen_A | -44.6 cm | 2 |  |
| 1834.96 | IN |  | 0.00 | kitchen_B | -63.3 cm | 1 |  |
| 1835.47 | IN |  | 0.00 | kitchen_A | -31.9 cm | 1 |  |
| 1838.05 | IN |  | 0.00 | sideline_left | -48.2 cm | 1 |  |
| 1838.58 | UNCERTAIN |  | 0.08 | sideline_left | -17.0 cm | 1 |  |
| 1890.04 | UNCERTAIN |  | 1.00 | sideline_left | 85.4 cm | 2 |  |
| 1922.43 | IN |  | 0.00 | centreline_A | -71.1 cm | 1 |  |
| 1923.58 | IN |  | 0.00 | centreline_B | -165.9 cm | 1 |  |
| 1924.80 | IN |  | 0.00 | centreline_A | -246.4 cm | 1 |  |
| 1929.44 | IN |  | 0.00 | sideline_right | -77.6 cm | 1 |  |
| 1930.21 | IN |  | 0.00 | sideline_right | -24.3 cm | 2 |  |
| 1934.02 | IN |  | 0.00 | kitchen_A | -61.3 cm | 2 |  |
| 1935.25 | IN |  | 0.00 | centreline_B | -51.1 cm | 1 |  |
| 1937.78 | UNCERTAIN |  | 0.07 | kitchen_A | -11.9 cm | 1 |  |
| 1938.93 | – |  | – |  | – | 1 | secondary bounce |
| 1939.14 | – |  | – |  | – | 1 | secondary bounce |
| 1942.76 | IN |  | 0.00 | centreline_A | -249.3 cm | 1 |  |
| 1943.50 | – |  | – |  | – | 1 | secondary bounce |
| 1946.28 | UNCERTAIN |  | 1.00 | baseline_A | 149.1 cm | 1 |  |
| 1953.09 | UNCERTAIN |  | 1.00 | baseline_B | 12.4 cm | 1 |  |
| 1953.79 | – |  | – |  | – | 1 | secondary bounce |
| 1954.28 | – |  | – |  | – | 1 | secondary bounce |
| 1972.38 | UNCERTAIN |  | 0.98 | sideline_left | 277.0 cm | 1 |  |
| 1998.84 | IN |  | 0.00 | kitchen_A | -172.2 cm | 1 |  |
| 2001.39 | IN |  | 0.00 | kitchen_A | -146.5 cm | 1 |  |
| 2004.24 | IN |  | 0.00 | centreline_A | -159.8 cm | 1 |  |
| 2008.84 | UNCERTAIN |  | 1.00 | sideline_left | 41.6 cm | 1 |  |
| 2009.09 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2011.25 | IN |  | 0.00 | kitchen_B | -53.2 cm | 1 |  |
| 2013.28 | IN |  | 0.00 | sideline_left | -130.0 cm | 2 |  |
| 2014.75 | UNCERTAIN |  | 1.00 | sideline_right | 58.6 cm | 1 | silent: one camera, 9 m away, looking across the sideline_right |
| 2020.87 | IN |  | 0.00 | centreline_B | -100.4 cm | 1 |  |
| 2022.38 | IN |  | 0.04 | kitchen_A | -118.8 cm | 2 |  |
| 2023.02 | – |  | – |  | – | 1 | secondary bounce |
| 2023.95 | IN |  | 0.00 | kitchen_B | -219.9 cm | 1 |  |
| 2024.35 | – |  | – |  | – | 1 | secondary bounce |
| 2026.16 | UNCERTAIN |  | 0.20 | sideline_right | -18.4 cm | 2 |  |
| 2026.32 | – |  | – |  | – | 1 | secondary bounce |
| 2040.48 | IN |  | 0.00 | centreline_A | -219.5 cm | 1 |  |
| 2041.87 | UNCERTAIN |  | 1.00 | sideline_left | 198.9 cm | 1 | unconfirmed by redmi |
| 2042.80 | – |  | – |  | – | 2 | secondary bounce |
| 2044.31 | IN |  | 0.00 | kitchen_A | -150.9 cm | 3 |  |
| 2045.03 | – |  | – |  | – | 2 | secondary bounce |
| 2045.55 | – |  | – |  | – | 2 | secondary bounce |
| 2045.77 | IN |  | 0.00 | centreline_A | -265.1 cm | 1 |  |
| 2046.85 | IN |  | 0.00 | centreline_B | -287.5 cm | 2 |  |
| 2047.15 | – |  | – |  | – | 1 | secondary bounce |
| 2048.13 | IN |  | 0.00 | centreline_A | -238.6 cm | 2 |  |
| 2049.44 | UNCERTAIN |  | 1.00 | baseline_B | 370.3 cm | 1 |  |
| 2049.91 | UNCERTAIN |  | 0.25 | sideline_right | -21.0 cm | 2 |  |
| 2056.37 | IN |  | 0.00 | kitchen_A | -28.3 cm | 1 |  |
| 2059.34 | IN |  | 0.00 | sideline_right | -84.3 cm | 1 |  |
| 2063.06 | UNCERTAIN |  | 0.43 | sideline_right | -15.3 cm | 2 |  |
| 2066.12 | IN |  | 0.00 | centreline_A | -277.0 cm | 1 |  |
| 2066.88 | – |  | – |  | – | 1 | secondary bounce |
| 2069.10 | IN |  | 0.00 | sideline_right | -66.4 cm | 1 |  |
| 2072.93 | IN |  | 0.00 | kitchen_A | -257.5 cm | 1 |  |
| 2073.99 | OUT | **OUT** | 0.98 | baseline_B | 64.9 cm | 2 |  |
| 2084.39 | IN |  | 0.00 | centreline_B | -264.3 cm | 1 |  |
| 2087.41 | IN |  | 0.00 | sideline_left | -88.5 cm | 1 |  |
| 2087.57 | – |  | – |  | – | 1 | secondary bounce |
| 2089.99 | IN |  | 0.00 | centreline_A | -222.4 cm | 2 |  |
| 2091.27 | UNCERTAIN |  | 0.19 | sideline_left | -43.2 cm | 2 |  |
| 2094.32 | UNCERTAIN |  | 1.00 | sideline_left | 275.6 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 2097.77 | IN |  | 0.00 | sideline_right | -55.5 cm | 1 |  |
| 2098.79 | UNCERTAIN |  | 0.07 | centreline_B | -75.6 cm | 2 |  |
| 2100.52 | UNCERTAIN |  | 1.00 | sideline_right | 198.0 cm | 1 | silent: one camera, 11 m away, looking across the sideline_right |
| 2101.17 | – |  | – |  | – | 1 | secondary bounce |
| 2101.91 | UNCERTAIN |  | 1.00 | sideline_right | 13.2 cm | 1 |  |
| 2102.30 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2102.58 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2102.81 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2103.22 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2110.26 | IN |  | 0.00 | kitchen_A | -80.8 cm | 1 |  |
| 2111.75 | UNCERTAIN |  | 1.00 | sideline_left | 40.6 cm | 1 | unconfirmed by samsung, redmi |
| 2112.63 | – |  | – |  | – | 1 | secondary bounce |
| 2113.15 | – |  | – |  | – | 1 | secondary bounce |
| 2113.54 | – |  | – |  | – | 1 | secondary bounce |
| 2113.82 | – |  | – |  | – | 1 | secondary bounce |
| 2116.06 | UNCERTAIN |  | 1.00 | baseline_B | 92.3 cm | 1 |  |
| 2117.62 | IN |  | 0.00 | centreline_A | -177.5 cm | 2 |  |
| 2118.19 | – |  | – |  | – | 2 | secondary bounce |
| 2118.63 | – |  | – |  | – | 2 | secondary bounce |
| 2126.34 | IN |  | 0.00 | baseline_A | -34.4 cm | 1 |  |
| 2135.03 | UNCERTAIN |  | 1.00 | sideline_right | 261.9 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 2136.25 | IN |  | 0.00 | centreline_B | -253.4 cm | 2 |  |
| 2137.72 | IN |  | 0.00 | sideline_right | -117.0 cm | 1 |  |
| 2139.09 | IN |  | 0.00 | kitchen_B | -162.4 cm | 2 |  |
| 2141.97 | IN |  | 0.00 | kitchen_A | -74.9 cm | 2 |  |
| 2142.33 | – |  | – |  | – | 2 | secondary bounce |
| 2143.52 | – |  | – |  | – | 1 | secondary bounce |
| 2145.50 | IN |  | 0.00 | baseline_A | -35.6 cm | 1 |  |
| 2150.04 | IN |  | 0.00 | centreline_B | -152.0 cm | 1 | serve from A (half unknown) |
| 2151.84 | OUT | **OUT** | 0.99 | baseline_A | 2.8 cm | 2 |  |
| 2153.36 | IN |  | 0.00 | centreline_A | -136.1 cm | 2 |  |
| 2164.74 | IN |  | 0.00 | baseline_A | -52.6 cm | 1 |  |
| 2167.20 | UNCERTAIN |  | 1.00 | baseline_A | 113.0 cm | 1 |  |
| 2172.26 | UNCERTAIN |  | 0.94 | baseline_B | 26.8 cm | 1 |  |
| 2173.79 | UNCERTAIN |  | 0.45 | sideline_right | -5.8 cm | 2 |  |
| 2174.24 | – |  | – |  | – | 1 | secondary bounce |
| 2174.60 | – |  | – |  | – | 1 | secondary bounce |
| 2175.02 | – |  | – |  | – | 1 | secondary bounce |
| 2184.92 | UNCERTAIN |  | 1.00 | baseline_B | 56.1 cm | 2 |  |
| 2193.17 | IN |  | 0.00 | sideline_right | -45.3 cm | 2 | serve from B right |
| 2195.07 | IN |  | 0.00 | baseline_B | -19.6 cm | 2 |  |
| 2205.76 | IN |  | 0.00 | centreline_B | -287.0 cm | 1 |  |
| 2206.74 | – |  | – |  | – | 1 | secondary bounce |
| 2213.29 | UNCERTAIN |  | 1.00 | baseline_B | 110.5 cm | 1 |  |
| 2214.53 | IN |  | 0.00 | centreline_A | -304.2 cm | 2 |  |
| 2214.88 | – |  | – |  | – | 1 | secondary bounce |
| 2215.84 | IN |  | 0.00 | kitchen_A | -52.8 cm | 1 |  |
| 2216.41 | – |  | – |  | – | 2 | secondary bounce |
| 2216.88 | – |  | – |  | – | 1 | secondary bounce |
| 2218.50 | IN |  | 0.00 | centreline_B | -178.3 cm | 2 |  |
| 2220.84 | UNCERTAIN |  | 1.00 | baseline_B | 52.9 cm | 1 | unconfirmed by iphone17 |
| 2224.37 | UNCERTAIN |  | 1.00 | baseline_B | 62.4 cm | 1 |  |
| 2225.80 | IN |  | 0.00 | baseline_A | -140.0 cm | 2 | serve from B right |
| 2228.56 | IN |  | 0.00 | kitchen_B | -31.3 cm | 1 |  |
| 2228.99 | – |  | – |  | – | 1 | secondary bounce |
| 2233.14 | UNCERTAIN |  | 1.00 | sideline_right | 207.6 cm | 1 |  |
| 2234.55 | UNCERTAIN |  | 1.00 | baseline_A | 93.5 cm | 2 |  |
| 2235.31 | – |  | – |  | – | 2 | secondary bounce |
| 2235.97 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2236.78 | IN |  | 0.00 | centreline_A | -86.3 cm | 1 |  |
| 2237.21 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2239.09 | IN |  | 0.00 | sideline_left | -120.9 cm | 2 |  |
| 2244.63 | UNCERTAIN |  | 1.00 | baseline_A | 134.3 cm | 1 |  |
| 2245.40 | – |  | – |  | – | 1 | secondary bounce |
| 2248.84 | IN |  | 0.00 | centreline_B | -87.4 cm | 2 | serve from A left |
| 2250.31 | IN |  | 0.00 | centreline_A | -158.2 cm | 2 |  |
| 2250.12 | UNCERTAIN |  | 1.00 | baseline_A | 268.3 cm | 1 |  |
| 2252.77 | IN |  | 0.00 | kitchen_B | -108.4 cm | 2 |  |
| 2253.82 | IN |  | 0.00 | kitchen_B | -91.6 cm | 1 |  |
| 2253.98 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2254.27 | – |  | – |  | – | 1 | secondary bounce |
| 2256.75 | IN |  | 0.00 | kitchen_A | -101.2 cm | 2 |  |
| 2257.54 | – |  | – |  | – | 2 | secondary bounce |
| 2257.72 | – |  | – |  | – | 1 | secondary bounce |
| 2259.27 | UNCERTAIN |  | 1.00 | sideline_right | 74.2 cm | 1 |  |
| 2263.18 | UNCERTAIN |  | 1.00 | baseline_A | 112.7 cm | 2 |  |
| 2263.94 | – |  | – |  | – | 2 | secondary bounce |
| 2267.05 | IN |  | 0.00 | sideline_left | -109.0 cm | 1 |  |
| 2268.33 | IN |  | 0.00 | baseline_A | -67.3 cm | 1 |  |
| 2268.70 | IN |  | 0.00 | centreline_A | -137.7 cm | 2 |  |
| 2270.27 | IN |  | 0.00 | kitchen_A | -140.8 cm | 2 |  |
| 2272.63 | IN |  | 0.00 | centreline_A | -64.0 cm | 1 |  |
| 2272.78 | – |  | – |  | – | 3 | secondary bounce |
| 2273.80 | – |  | – |  | – | 1 | secondary bounce |
| 2280.94 | IN |  | 0.00 | sideline_right | -29.4 cm | 2 | serve from A left |
| 2282.63 | IN |  | 0.00 | centreline_A | -158.2 cm | 2 |  |
| 2284.59 | IN |  | 0.00 | kitchen_B | -133.9 cm | 1 |  |
| 2285.78 | – |  | – |  | – | 1 | secondary bounce |
| 2287.56 | UNCERTAIN |  | 1.00 | sideline_right | 65.1 cm | 1 | silent: one camera, 10 m away, looking across the sideline_right |
| 2289.32 | OUT | **OUT** | 1.00 | baseline_A | 76.3 cm | 2 |  |
| 2294.18 | IN |  | 0.00 | kitchen_A | -234.0 cm | 1 |  |
| 2294.57 | UNCERTAIN |  | 0.11 | kitchen_A | -9.0 cm | 1 |  |
| 2294.68 | – |  | – |  | – | 1 | secondary bounce |
| 2295.13 | – |  | – |  | – | 2 | secondary bounce |
| 2295.64 | – |  | – |  | – | 1 | secondary bounce |
| 2298.74 | IN |  | 0.00 | sideline_left | -151.8 cm | 1 |  |
| 2299.40 | – |  | – |  | – | 1 | secondary bounce |
| 2300.90 | UNCERTAIN |  | 1.00 | baseline_B | 72.0 cm | 1 | unconfirmed by iphone17 |
| 2303.28 | UNCERTAIN |  | 1.00 | baseline_B | 79.6 cm | 1 |  |
| 2304.49 | IN |  | 0.00 | sideline_right | -80.9 cm | 2 | serve from B right |
| 2305.98 | IN |  | 0.00 | centreline_B | -284.5 cm | 2 |  |
| 2307.17 | IN |  | 0.00 | kitchen_B | -185.9 cm | 1 |  |
| 2309.43 | IN |  | 0.00 | centreline_B | -73.1 cm | 2 | serve from A (half unknown) |
| 2309.84 | IN |  | 0.00 | centreline_A | -252.8 cm | 1 |  |
| 2316.93 | IN |  | 0.00 | centreline_A | -165.8 cm | 1 | serve from B (half unknown) |
| 2318.65 | IN |  | 0.00 | centreline_B | -116.3 cm | 2 |  |
| 2320.74 | UNCERTAIN |  | 1.00 | baseline_B | 92.8 cm | 1 | unconfirmed by iphone17 |
| 2328.61 | UNCERTAIN |  | 1.00 | baseline_A | 102.2 cm | 2 | silent: start of play far outside the court (ball handling?) |
| 2332.83 | IN |  | 0.00 | centreline_A | -64.9 cm | 1 |  |
| 2333.55 | UNCERTAIN |  | 1.00 | sideline_right | 335.0 cm | 1 |  |
| 2335.05 | IN |  | 0.00 | centreline_B | -121.0 cm | 2 |  |
| 2335.97 | IN |  | 0.00 | baseline_A | -48.9 cm | 1 |  |
| 2336.83 | IN |  | 0.00 | centreline_A | -96.9 cm | 2 |  |
| 2338.77 | IN |  | 0.00 | sideline_left | -82.9 cm | 1 |  |
| 2341.68 | UNCERTAIN |  | 1.00 | sideline_right | 287.9 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 2348.66 | UNCERTAIN |  | 1.00 | baseline_A | 112.8 cm | 1 |  |
| 2349.42 | – |  | – |  | – | 1 | secondary bounce |
| 2353.03 | IN |  | 0.00 | baseline_B | -72.6 cm | 2 |  |
| 2354.46 | IN |  | 0.00 | kitchen_A | -64.5 cm | 2 |  |
| 2355.31 | – |  | – |  | – | 1 | secondary bounce |
| 2356.66 | IN |  | 0.00 | centreline_A | -185.6 cm | 1 |  |
| 2357.43 | UNCERTAIN |  | 1.00 | sideline_right | 241.6 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 2358.05 | OUT | **OUT** | 1.00 | sideline_right | 235.6 cm | 1 |  |
| 2361.20 | UNCERTAIN |  | 1.00 | sideline_right | 127.4 cm | 1 | silent: one camera, 10 m away, looking across the sideline_right |
| 2371.62 | IN |  | 0.00 | baseline_A | -47.0 cm | 2 | serve from B right |
| 2373.29 | IN |  | 0.00 | sideline_left | -148.4 cm | 2 |  |
| 2376.37 | IN |  | 0.00 | centreline_B | -293.9 cm | 1 |  |
| 2377.53 | IN |  | 0.00 | centreline_A | -235.6 cm | 1 |  |
| 2380.56 | IN |  | 0.00 | sideline_right | -116.9 cm | 1 |  |
| 2393.74 | IN |  | 0.00 | centreline_A | -108.8 cm | 2 | serve from B left |
| 2395.47 | IN |  | 0.00 | baseline_B | -33.0 cm | 2 |  |
| 2397.40 | UNCERTAIN |  | 1.00 | baseline_A | 125.0 cm | 1 | unconfirmed by samsung |
| 2400.44 | IN |  | 0.00 | centreline_A | -82.4 cm | 1 |  |
| 2402.89 | IN |  | 0.00 | kitchen_A | -143.8 cm | 2 |  |
| 2403.62 | IN |  | 0.00 | sideline_right | -16.0 cm | 2 |  |
| 2404.00 | – |  | – |  | – | 1 | secondary bounce |
| 2404.37 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2411.57 | UNCERTAIN |  | 1.00 | baseline_B | 131.4 cm | 1 | unconfirmed by iphone17 |
| 2414.45 | UNCERTAIN |  | 1.00 | baseline_B | 85.2 cm | 1 |  |
| 2415.86 | IN |  | 0.00 | sideline_right | -113.5 cm | 1 |  |
| 2417.26 | IN |  | 0.00 | centreline_B | -279.4 cm | 2 |  |
| 2420.81 | IN |  | 0.00 | centreline_B | -280.7 cm | 2 |  |
| 2421.46 | – |  | – |  | – | 1 | secondary bounce |
| 2421.98 | – |  | – |  | – | 1 | secondary bounce |
| 2422.35 | – |  | – |  | – | 1 | secondary bounce |
| 2423.39 | UNCERTAIN |  | 1.00 | sideline_right | 154.7 cm | 1 | silent: one camera, flight not measured (speed 19 +- 37 m/s) |
| 2433.27 | OUT | **OUT** | 1.00 | sideline_left | 45.1 cm | 2 |  |
| 2437.99 | IN |  | 0.00 | centreline_A | -175.0 cm | 2 |  |
| 2440.62 | UNCERTAIN |  | 1.00 | baseline_A | 131.8 cm | 1 | unconfirmed by samsung |
| 2441.27 | – |  | – |  | – | 1 | secondary bounce |
| 2444.19 | IN |  | 0.00 | centreline_B | -181.0 cm | 1 |  |
| 2445.34 | IN |  | 0.00 | kitchen_B | -73.3 cm | 1 |  |
| 2445.67 | – |  | – |  | – | 1 | secondary bounce |
| 2445.93 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2446.60 | – |  | – |  | – | 1 | secondary bounce |
| 2448.63 | IN |  | 0.00 | centreline_A | -289.0 cm | 1 |  |
| 2450.60 | UNCERTAIN |  | 1.00 | baseline_A | 122.7 cm | 2 |  |
| 2451.37 | – |  | – |  | – | 3 | second bounce (ball not returned) |
| 2455.53 | IN |  | 0.00 | centreline_B | -176.2 cm | 2 |  |
| 2457.08 | IN |  | 0.00 | centreline_A | -171.9 cm | 2 |  |
| 2457.24 | – |  | – |  | – | 1 | secondary bounce |
| 2459.09 | OUT | **OUT** | 1.00 | sideline_right | 140.9 cm | 1 |  |
| 2462.42 | UNCERTAIN |  | 1.00 | sideline_left | 357.6 cm | 1 |  |
| 2467.99 | IN |  | 0.00 | sideline_right | -97.6 cm | 2 |  |
| 2469.68 | IN |  | 0.00 | centreline_B | -112.7 cm | 1 |  |
| 2472.74 | UNCERTAIN |  | 1.00 | baseline_A | 250.0 cm | 1 |  |
| 2476.83 | UNCERTAIN |  | 1.00 | sideline_right | 12.3 cm | 1 | unconfirmed by iphone17 |
| 2477.47 | – |  | – |  | – | 1 | secondary bounce |
| 2479.63 | IN |  | 0.00 | baseline_A | -52.2 cm | 1 |  |
| 2482.33 | IN |  | 0.00 | baseline_A | -115.2 cm | 1 |  |
| 2483.69 | IN |  | 0.00 | centreline_A | -151.3 cm | 1 |  |
| 2484.04 | IN |  | 0.00 | centreline_B | -79.8 cm | 1 |  |
| 2486.12 | IN |  | 0.00 | kitchen_B | -153.5 cm | 1 |  |
| 2487.56 | UNCERTAIN |  | 0.99 | baseline_B | 46.0 cm | 1 |  |
| 2489.93 | IN |  | 0.00 | kitchen_A | -95.2 cm | 1 |  |
| 2490.35 | – |  | – |  | – | 1 | secondary bounce |
| 2491.96 | IN |  | 0.00 | kitchen_A | -218.2 cm | 1 |  |
| 2492.48 | – |  | – |  | – | 1 | secondary bounce |
| 2494.35 | IN |  | 0.00 | sideline_left | -54.9 cm | 1 |  |
| 2508.46 | IN |  | 0.00 | baseline_B | -63.3 cm | 1 |  |
| 2511.46 | UNCERTAIN |  | 1.00 | sideline_left | 183.2 cm | 1 |  |
| 2512.03 | IN |  | 0.00 | kitchen_B | -42.1 cm | 1 |  |
| 2512.64 | – |  | – |  | – | 1 | secondary bounce |
| 2513.09 | – |  | – |  | – | 1 | secondary bounce |
| 2513.42 | – |  | – |  | – | 1 | secondary bounce |
| 2513.68 | – |  | – |  | – | 1 | secondary bounce |
| 2518.14 | IN |  | 0.00 | baseline_A | -64.3 cm | 2 |  |
| 2519.74 | UNCERTAIN |  | 1.00 | baseline_A | 83.3 cm | 1 |  |
| 2523.06 | IN |  | 0.00 | baseline_A | -45.1 cm | 1 |  |
| 2523.30 | IN |  | 0.00 | sideline_left | -119.1 cm | 2 | serve from A right |
| 2524.92 | IN |  | 0.00 | centreline_A | -128.4 cm | 2 |  |
| 2525.74 | IN |  | 0.00 | centreline_A | -287.4 cm | 1 |  |
| 2526.03 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2526.40 | – |  | – |  | – | 2 | secondary bounce |
| 2526.73 | – |  | – |  | – | 2 | secondary bounce |
| 2526.98 | – |  | – |  | – | 2 | secondary bounce |
| 2527.19 | – |  | – |  | – | 1 | secondary bounce |
| 2534.62 | IN |  | 0.00 | centreline_B | -193.8 cm | 1 |  |
| 2536.11 | IN |  | 0.00 | centreline_A | -156.6 cm | 1 |  |
| 2536.33 | – |  | – |  | – | 1 | secondary bounce |
| 2540.24 | IN |  | 0.00 | baseline_B | -44.4 cm | 2 |  |
| 2543.39 | IN |  | 0.00 | sideline_right | -104.9 cm | 2 |  |
| 2546.40 | IN |  | 0.01 | kitchen_A | -127.3 cm | 3 |  |
| 2547.31 | IN |  | 0.00 | kitchen_B | -166.3 cm | 2 |  |
| 2548.87 | IN |  | 0.00 | sideline_left | -81.2 cm | 1 |  |
| 2549.25 | – |  | – |  | – | 1 | secondary bounce |
| 2554.15 | UNCERTAIN |  | 1.00 | baseline_A | 70.6 cm | 1 | unconfirmed by samsung |
| 2555.12 | IN |  | 0.00 | baseline_A | -47.4 cm | 1 |  |
| 2556.81 | IN |  | 0.00 | baseline_A | -18.1 cm | 1 |  |
| 2557.29 | UNCERTAIN |  | 1.00 | baseline_B | 152.9 cm | 1 |  |
| 2558.86 | IN |  | 0.00 | baseline_A | -47.9 cm | 1 |  |
| 2560.39 | IN |  | 0.00 | centreline_B | -202.7 cm | 2 |  |
| 2561.57 | IN |  | 0.00 | kitchen_B | -161.5 cm | 2 |  |
| 2563.50 | UNCERTAIN |  | 0.27 | kitchen_B | -4.6 cm | 1 |  |
| 2563.91 | IN |  | 0.00 | kitchen_A | -32.3 cm | 1 |  |
| 2564.22 | – |  | – |  | – | 2 | secondary bounce |
| 2564.47 | – |  | – |  | – | 1 | secondary bounce |
| 2564.64 | – |  | – |  | – | 2 | secondary bounce |
| 2566.09 | UNCERTAIN |  | 0.64 | baseline_A | 8.0 cm | 1 |  |
| 2567.27 | IN |  | 0.00 | kitchen_B | -159.3 cm | 2 |  |
| 2569.34 | UNCERTAIN |  | 1.00 | sideline_right | 52.1 cm | 1 | silent: one camera, 9 m away, looking across the sideline_right |
| 2569.72 | IN |  | 0.00 | baseline_B | -12.1 cm | 1 |  |
| 2573.18 | UNCERTAIN |  | 1.00 | baseline_B | 64.2 cm | 2 |  |
| 2574.57 | IN |  | 0.00 | sideline_right | -101.8 cm | 2 | serve from B right |
| 2576.08 | IN |  | 0.00 | centreline_B | -181.6 cm | 2 |  |
| 2577.60 | IN |  | 0.00 | kitchen_B | -63.9 cm | 1 |  |
| 2577.93 | – |  | – |  | – | 1 | secondary bounce |
| 2578.18 | – |  | – |  | – | 2 | secondary bounce |
| 2587.81 | IN |  | 0.00 | sideline_left | -110.6 cm | 1 | serve from A (half unknown) |
| 2589.32 | IN |  | 0.00 | centreline_A | -67.6 cm | 2 |  |
| 2591.15 | UNCERTAIN |  | 1.00 | sideline_right | 230.3 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 2591.54 | IN |  | 0.00 | sideline_left | -10.4 cm | 1 |  |
| 2591.72 | – |  | – |  | – | 1 | secondary bounce |
| 2593.81 | UNCERTAIN |  | 1.00 | baseline_B | 264.0 cm | 1 |  |
| 2598.49 | UNCERTAIN |  | 1.00 | baseline_B | 135.6 cm | 1 |  |
| 2600.02 | IN |  | 0.00 | centreline_A | -30.6 cm | 2 | serve from B left |
| 2600.78 | – |  | – |  | – | 2 | secondary bounce |
| 2605.15 | IN |  | 0.00 | sideline_right | -83.8 cm | 2 | serve from A left |
| 2606.73 | IN |  | 0.00 | baseline_A | -95.4 cm | 1 |  |
| 2607.89 | UNCERTAIN |  | 0.33 | kitchen_B | -8.2 cm | 3 |  |
| 2608.31 | IN |  | 0.00 | kitchen_A | -33.1 cm | 1 |  |
| 2608.99 | – |  | – |  | – | 1 | secondary bounce |
| 2614.97 | UNCERTAIN |  | 1.00 | baseline_B | 137.5 cm | 1 | unconfirmed by iphone17 |
| 2616.32 | UNCERTAIN |  | 1.00 | baseline_B | 77.2 cm | 2 |  |
| 2617.92 | IN |  | 0.00 | baseline_A | -36.7 cm | 2 |  |
| 2619.34 | IN |  | 0.00 | centreline_B | -295.9 cm | 2 |  |
| 2620.70 | IN |  | 0.00 | kitchen_A | -155.4 cm | 1 |  |
| 2622.26 | IN |  | 0.00 | kitchen_A | -125.7 cm | 3 |  |
| 2622.80 | – |  | – |  | – | 2 | secondary bounce |
| 2623.16 | – |  | – |  | – | 1 | secondary bounce |
| 2624.76 | UNCERTAIN |  | 1.00 | sideline_right | 18.1 cm | 1 | unconfirmed by iphone17 |
| 2625.54 | – |  | – |  | – | 1 | secondary bounce |
| 2629.47 | UNCERTAIN |  | 1.00 | baseline_A | 51.6 cm | 1 |  |
| 2630.55 | OUT | **OUT** | 1.00 | sideline_right | 75.2 cm | 2 |  |
| 2631.64 | – |  | – |  | – | 1 | secondary bounce |
| 2632.61 | – |  | – |  | – | 1 | secondary bounce |
| 2634.96 | UNCERTAIN |  | 1.00 | baseline_B | 143.7 cm | 1 |  |
| 2636.23 | IN |  | 0.00 | centreline_A | -133.1 cm | 2 | serve from B left |
| 2639.09 | IN |  | 0.00 | centreline_B | -188.3 cm | 1 |  |
| 2640.89 | OUT | **OUT** | 1.00 | sideline_right | 79.3 cm | 2 |  |
| 2641.83 | UNCERTAIN |  | 1.00 | sideline_right | 92.8 cm | 1 |  |
| 2642.67 | UNCERTAIN |  | 1.00 | sideline_right | 40.0 cm | 1 |  |
| 2646.61 | IN |  | 0.00 | sideline_right | -82.9 cm | 1 |  |
| 2647.15 | IN |  | 0.00 | kitchen_A | -61.9 cm | 2 |  |
| 2650.19 | UNCERTAIN |  | 1.00 | baseline_B | 193.6 cm | 1 |  |
| 2654.48 | IN |  | 0.00 | baseline_A | -13.5 cm | 1 |  |
| 2656.56 | IN |  | 0.00 | sideline_left | -138.6 cm | 2 |  |
| 2657.89 | IN |  | 0.00 | baseline_A | -29.0 cm | 1 |  |
| 2665.17 | IN |  | 0.00 | sideline_right | -22.2 cm | 2 |  |
| 2669.29 | IN |  | 0.00 | centreline_A | -272.8 cm | 1 |  |
| 2673.84 | IN |  | 0.00 | kitchen_A | -171.7 cm | 2 |  |
| 2675.15 | IN |  | 0.00 | sideline_right | -40.2 cm | 2 |  |
| 2677.24 | IN |  | 0.01 | sideline_left | -7.7 cm | 2 |  |
| 2682.97 | IN |  | 0.00 | sideline_left | -113.3 cm | 1 |  |
| 2688.16 | IN |  | 0.00 | baseline_A | -105.2 cm | 2 | serve from B right |
| 2688.31 | – |  | – |  | – | 1 | secondary bounce |
| 2692.28 | IN |  | 0.00 | sideline_right | -99.6 cm | 2 |  |
| 2694.00 | IN |  | 0.00 | centreline_A | -67.9 cm | 1 |  |
| 2700.31 | IN |  | 0.00 | centreline_B | -152.1 cm | 2 |  |
| 2704.47 | OUT | **OUT** | 1.00 | sideline_left | 23.6 cm | 2 |  |
| 2705.07 | – |  | – |  | – | 1 | secondary bounce |
| 2720.14 | UNCERTAIN |  | 1.00 | baseline_A | 91.4 cm | 2 |  |
| 2721.55 | UNCERTAIN |  | 1.00 | baseline_A | 120.2 cm | 2 |  |
| 2722.31 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2726.05 | IN |  | 0.00 | centreline_B | -61.8 cm | 2 | serve from A right |
| 2727.50 | IN |  | 0.00 | centreline_A | -232.0 cm | 2 |  |
| 2729.79 | UNCERTAIN |  | 1.00 | baseline_B | 255.0 cm | 1 |  |
| 2737.12 | IN |  | 0.00 | sideline_left | -139.9 cm | 2 |  |
| 2738.94 | UNCERTAIN |  | 1.00 | baseline_A | 83.7 cm | 1 |  |
| 2742.44 | UNCERTAIN |  | 0.54 | baseline_B | 2.2 cm | 1 |  |
| 2743.79 | IN |  | 0.00 | kitchen_A | -208.5 cm | 2 |  |
| 2745.33 | IN |  | 0.00 | centreline_B | -167.6 cm | 1 |  |
| 2747.16 | UNCERTAIN |  | 1.00 | sideline_right | 164.3 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 2747.83 | – |  | – |  | – | 2 | secondary bounce |
| 2748.50 | – |  | – |  | – | 1 | secondary bounce |
| 2749.39 | UNCERTAIN |  | 1.00 | baseline_A | 317.4 cm | 1 |  |
| 2749.58 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2750.19 | – |  | – |  | – | 1 | secondary bounce |
| 2760.75 | IN |  | 0.00 | centreline_B | -75.8 cm | 2 | serve from A right |
| 2762.23 | IN |  | 0.00 | centreline_A | -245.4 cm | 2 |  |
| 2763.75 | IN |  | 0.00 | kitchen_A | -214.8 cm | 2 |  |
| 2765.09 | IN |  | 0.00 | kitchen_B | -116.2 cm | 2 |  |
| 2766.05 | IN |  | 0.00 | sideline_left | -49.1 cm | 1 |  |
| 2766.62 | – |  | – |  | – | 2 | secondary bounce |
| 2770.45 | IN |  | 0.00 | sideline_left | -118.8 cm | 2 |  |
| 2771.17 | – |  | – |  | – | 2 | secondary bounce |
| 2773.06 | UNCERTAIN |  | 1.00 | baseline_A | 9.0 cm | 1 |  |
| 2776.80 | IN |  | 0.00 | sideline_right | -131.9 cm | 1 |  |
| 2778.38 | IN |  | 0.00 | sideline_right | -98.9 cm | 2 |  |
| 2779.81 | IN |  | 0.00 | sideline_left | -13.4 cm | 2 |  |
| 2780.29 | – |  | – |  | – | 1 | secondary bounce |
| 2780.66 | – |  | – |  | – | 1 | secondary bounce |
| 2783.88 | IN |  | 0.00 | sideline_left | -119.5 cm | 1 |  |
| 2786.46 | UNCERTAIN |  | 1.00 | baseline_B | 131.0 cm | 1 | unconfirmed by iphone17 |
| 2787.68 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2789.06 | IN |  | 0.00 | centreline_A | -228.0 cm | 2 |  |
| 2790.69 | IN |  | 0.00 | centreline_B | -70.5 cm | 1 |  |
| 2793.83 | IN |  | 0.00 | baseline_B | -75.7 cm | 2 |  |
| 2795.41 | OUT | **OUT** | 1.00 | baseline_A | 9.0 cm | 2 |  |
| 2802.95 | IN |  | 0.00 | centreline_A | -107.6 cm | 1 |  |
| 2804.23 | IN |  | 0.00 | sideline_right | -23.2 cm | 2 |  |
| 2805.26 | – |  | – |  | – | 1 | secondary bounce |
| 2806.52 | UNCERTAIN |  | 1.00 | baseline_B | 352.8 cm | 1 |  |
| 2811.72 | IN |  | 0.00 | sideline_left | -43.8 cm | 2 | serve from B left |
| 2813.54 | IN |  | 0.00 | baseline_B | -16.9 cm | 2 |  |
| 2816.47 | UNCERTAIN |  | 0.06 | kitchen_A | -10.3 cm | 1 |  |
| 2817.34 | – |  | – |  | – | 1 | secondary bounce |
| 2819.99 | IN |  | 0.00 | centreline_B | -190.7 cm | 1 |  |
| 2825.79 | UNCERTAIN |  | 0.17 | baseline_A | -18.5 cm | 1 |  |
| 2827.48 | IN |  | 0.00 | centreline_B | -199.9 cm | 1 |  |
| 2828.83 | IN |  | 0.00 | centreline_A | -183.4 cm | 1 |  |
| 2829.21 | – |  | – |  | – | 1 | secondary bounce |
| 2829.82 | – |  | – |  | – | 1 | secondary bounce |
| 2830.31 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2830.70 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2831.32 | IN |  | 0.00 | baseline_A | -76.8 cm | 1 |  |
| 2831.58 | – |  | – |  | – | 1 | secondary bounce |
| 2833.99 | IN |  | 0.00 | baseline_A | -15.8 cm | 1 |  |
| 2835.03 | – |  | – |  | – | 2 | secondary bounce |
| 2839.39 | IN |  | 0.00 | baseline_B | -88.0 cm | 2 | serve from A right |
| 2840.78 | IN |  | 0.00 | sideline_left | -140.4 cm | 1 |  |
| 2841.67 | UNCERTAIN |  | 1.00 | baseline_B | 91.3 cm | 1 |  |
| 2843.47 | IN |  | 0.00 | kitchen_B | -165.7 cm | 2 |  |
| 2844.60 | IN |  | 0.00 | kitchen_A | -140.9 cm | 2 |  |
| 2845.27 | UNCERTAIN |  | 0.10 | kitchen_B | -94.9 cm | 2 |  |
| 2845.51 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2846.01 | IN |  | 0.00 | sideline_right | -53.7 cm | 2 |  |
| 2846.39 | – |  | – |  | – | 2 | secondary bounce |
| 2846.69 | – |  | – |  | – | 1 | secondary bounce |
| 2846.92 | – |  | – |  | – | 1 | secondary bounce |
| 2847.09 | – |  | – |  | – | 2 | secondary bounce |
| 2847.52 | – |  | – |  | – | 1 | secondary bounce |
| 2847.71 | – |  | – |  | – | 1 | secondary bounce |
| 2848.91 | – |  | – |  | – | 1 | secondary bounce |
| 2852.98 | IN |  | 0.00 | sideline_right | -102.9 cm | 1 |  |
| 2855.25 | OUT | **OUT** | 1.00 | sideline_right | 12.8 cm | 2 |  |
| 2856.03 | – |  | – |  | – | 1 | secondary bounce |
| 2860.06 | UNCERTAIN |  | 1.00 | baseline_B | 53.7 cm | 2 |  |
| 2860.47 | UNCERTAIN |  | 1.00 | baseline_B | 51.0 cm | 1 | unconfirmed by iphone17 |
| 2863.27 | IN |  | 0.00 | sideline_right | -84.6 cm | 1 |  |
| 2864.76 | IN |  | 0.00 | centreline_B | -277.4 cm | 2 |  |
| 2866.02 | UNCERTAIN |  | 1.00 | baseline_A | 194.8 cm | 1 |  |
| 2867.06 | IN |  | 0.00 | sideline_right | -16.7 cm | 2 |  |
| 2869.85 | UNCERTAIN |  | 1.00 | baseline_B | 192.3 cm | 1 |  |
| 2870.77 | – |  | – |  | – | 1 | secondary bounce |
| 2876.48 | UNCERTAIN |  | 1.00 | baseline_B | 118.5 cm | 2 |  |
| 2877.02 | – |  | – |  | – | 1 | secondary bounce |
| 2877.40 | – |  | – |  | – | 1 | secondary bounce |
| 2885.10 | UNCERTAIN |  | 1.00 | baseline_B | 72.3 cm | 1 |  |
| 2885.48 | UNCERTAIN |  | 1.00 | baseline_B | 70.1 cm | 1 |  |
| 2887.10 | IN |  | 0.03 | baseline_B | -30.0 cm | 1 |  |
| 2888.51 | IN |  | 0.00 | centreline_B | -163.8 cm | 1 |  |
| 2895.27 | IN |  | 0.00 | centreline_B | -217.7 cm | 1 |  |
| 2896.43 | – |  | – |  | – | 1 | secondary bounce |
| 2897.06 | – |  | – |  | – | 1 | secondary bounce |
| 2897.84 | – |  | – |  | – | 2 | secondary bounce |
| 2897.50 | UNCERTAIN |  | 1.00 | baseline_B | 47.1 cm | 1 |  |
| 2898.11 | – |  | – |  | – | 1 | secondary bounce |
| 2898.31 | – |  | – |  | – | 2 | secondary bounce |
| 2902.33 | UNCERTAIN |  | 1.00 | baseline_B | 142.4 cm | 2 |  |
| 2909.51 | IN |  | 0.01 | kitchen_A | -9.9 cm | 2 | serve from B (half unknown) |
| 2911.04 | IN |  | 0.00 | baseline_B | -48.7 cm | 2 |  |
| 2913.08 | IN |  | 0.00 | kitchen_B | -135.3 cm | 3 |  |
| 2912.67 | IN |  | 0.00 | kitchen_B | -29.7 cm | 1 |  |
| 2913.78 | – |  | – |  | – | 2 | secondary bounce |
| 2913.58 | IN |  | 0.00 | kitchen_B | -208.1 cm | 1 |  |
| 2916.86 | IN |  | 0.00 | centreline_A | -279.6 cm | 1 |  |
| 2920.03 | IN |  | 0.00 | baseline_A | -80.5 cm | 1 |  |
| 2919.55 | IN |  | 0.00 | baseline_A | -124.6 cm | 1 |  |
| 2921.12 | IN |  | 0.00 | centreline_B | -182.8 cm | 2 |  |
| 2924.53 | UNCERTAIN |  | 0.67 | sideline_left | 0.8 cm | 2 |  |
| 2925.46 | – |  | – |  | – | 1 | secondary bounce |
| 2926.80 | IN |  | 0.00 | centreline_A | -193.4 cm | 2 |  |
| 2928.24 | IN |  | 0.00 | baseline_B | -91.6 cm | 2 |  |
| 2929.32 | IN |  | 0.02 | kitchen_B | -17.6 cm | 1 |  |
| 2929.85 | – |  | – |  | – | 1 | secondary bounce |
| 2930.53 | – |  | – |  | – | 1 | secondary bounce |
| 2934.39 | IN |  | 0.00 | sideline_right | -44.2 cm | 1 |  |
| 2950.09 | IN |  | 0.00 | centreline_A | -118.0 cm | 1 |  |
| 3000.09 | IN |  | 0.00 | centreline_A | -187.7 cm | 1 |  |
| 3001.09 | IN |  | 0.00 | kitchen_B | -21.0 cm | 2 | serve from A right |
| 3002.74 | IN |  | 0.00 | centreline_A | -237.7 cm | 1 |  |
| 3004.22 | IN |  | 0.00 | sideline_left | -125.3 cm | 2 |  |
| 3005.84 | IN |  | 0.00 | sideline_left | -65.3 cm | 2 |  |
| 3007.09 | IN |  | 0.00 | centreline_B | -215.4 cm | 2 |  |
| 3007.70 | – |  | – |  | – | 2 | secondary bounce |
| 3008.77 | – |  | – |  | – | 1 | secondary bounce |
| 3009.24 | UNCERTAIN |  | 1.00 | baseline_B | 247.6 cm | 1 |  |
| 3009.38 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3015.41 | IN |  | 0.00 | sideline_right | -45.7 cm | 1 |  |
| 3015.61 | – |  | – |  | – | 1 | secondary bounce |
| 3016.70 | IN |  | 0.00 | baseline_A | -35.2 cm | 1 |  |
| 3016.90 | – |  | – |  | – | 1 | secondary bounce |
| 3018.52 | UNCERTAIN |  | 1.00 | baseline_A | 71.5 cm | 1 |  |
| 3019.23 | – |  | – |  | – | 1 | secondary bounce |
| 3022.74 | IN |  | 0.00 | centreline_B | -101.5 cm | 2 | serve from A right |
| 3024.33 | IN |  | 0.00 | centreline_A | -174.8 cm | 2 |  |
| 3025.21 | – |  | – |  | – | 1 | secondary bounce |
| 3025.44 | UNCERTAIN |  | 0.13 | kitchen_A | -8.4 cm | 1 |  |
| 3025.78 | – |  | – |  | – | 1 | secondary bounce |
| 3026.04 | – |  | – |  | – | 1 | secondary bounce |
| 3027.76 | IN |  | 0.00 | centreline_A | -182.5 cm | 1 |  |
| 3029.96 | IN |  | 0.00 | centreline_B | -191.1 cm | 2 |  |
| 3031.57 | IN |  | 0.00 | baseline_B | -9.9 cm | 2 |  |
| 3035.18 | UNCERTAIN |  | 1.00 | sideline_right | 52.1 cm | 1 | silent: one camera, 10 m away, looking across the sideline_right |
| 3036.64 | IN |  | 0.00 | centreline_B | -272.5 cm | 2 |  |
| 3038.27 | UNCERTAIN |  | 1.00 | baseline_B | 58.1 cm | 2 |  |
| 3038.62 | – |  | – |  | – | 1 | secondary bounce |
| 3038.89 | – |  | – |  | – | 1 | secondary bounce |
| 3044.73 | IN |  | 0.00 | centreline_A | -171.3 cm | 2 | serve from B (half unknown) |
| 3045.88 | IN |  | 0.00 | kitchen_B | -82.5 cm | 1 |  |
| 3046.58 | IN |  | 0.00 | kitchen_A | -180.6 cm | 1 |  |
| 3048.42 | IN |  | 0.00 | kitchen_B | -249.5 cm | 1 |  |
| 3049.16 | – |  | – |  | – | 2 | secondary bounce |
| 3050.73 | IN |  | 0.00 | sideline_right | -94.7 cm | 1 |  |
| 3057.01 | IN |  | 0.00 | centreline_A | -146.8 cm | 2 | serve from B right |
| 3057.23 | – |  | – |  | – | 1 | secondary bounce |
| 3058.40 | IN |  | 0.00 | kitchen_B | -192.4 cm | 1 |  |
| 3059.24 | – |  | – |  | – | 1 | secondary bounce |
| 3059.86 | IN |  | 0.00 | kitchen_B | -203.2 cm | 1 |  |
| 3061.19 | UNCERTAIN |  | 0.40 | kitchen_B | -123.2 cm | 2 |  |
| 3062.05 | – |  | – |  | – | 1 | secondary bounce |
| 3064.28 | IN |  | 0.00 | baseline_A | -66.3 cm | 2 |  |
| 3065.21 | – |  | – |  | – | 1 | secondary bounce |
| 3065.82 | – |  | – |  | – | 1 | secondary bounce |
| 3066.27 | – |  | – |  | – | 1 | secondary bounce |
| 3071.20 | UNCERTAIN |  | 1.00 | baseline_A | 399.0 cm | 1 |  |
| 3072.16 | IN |  | 0.00 | sideline_right | -76.2 cm | 1 |  |
| 3074.26 | UNCERTAIN |  | 0.58 | sideline_right | 0.9 cm | 1 |  |
| 3076.59 | UNCERTAIN |  | 1.00 | sideline_right | 64.7 cm | 1 | silent: one camera, flight not measured (speed 6 +- 82 m/s) |
| 3077.59 | IN |  | 0.00 | centreline_A | -292.7 cm | 2 |  |
| 3078.41 | – |  | – |  | – | 1 | secondary bounce |
| 3079.12 | IN |  | 0.00 | sideline_left | -132.8 cm | 2 |  |
| 3083.30 | UNCERTAIN |  | 1.00 | sideline_right | 94.1 cm | 1 | silent: one camera, 9 m away, looking across the sideline_right |
| 3087.20 | UNCERTAIN |  | 1.00 | baseline_A | 134.4 cm | 1 |  |
| 3087.97 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 3088.62 | UNCERTAIN |  | 1.00 | baseline_A | 98.9 cm | 1 | unconfirmed by samsung |
| 3091.48 | OUT | **OUT** | 1.00 | baseline_B | 11.1 cm | 2 |  |
| 3093.39 | IN |  | 0.00 | centreline_A | -215.4 cm | 1 |  |
| 3098.79 | UNCERTAIN |  | 1.00 | baseline_A | 78.9 cm | 1 |  |
| 3100.38 | IN |  | 0.00 | sideline_right | -62.9 cm | 1 |  |
| 3105.43 | IN |  | 0.00 | kitchen_A | -51.1 cm | 1 |  |
| 3113.62 | UNCERTAIN |  | 1.00 | baseline_B | 141.7 cm | 1 |  |
| 3117.24 | UNCERTAIN |  | 1.00 | sideline_left | 126.6 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 3121.82 | UNCERTAIN |  | 1.00 | baseline_B | 233.9 cm | 1 |  |
| 3129.01 | IN |  | 0.01 | sideline_right | -10.4 cm | 1 |  |
| 3130.88 | IN |  | 0.00 | kitchen_A | -34.5 cm | 1 |  |
| 3131.48 | – |  | – |  | – | 1 | secondary bounce |
| 3134.23 | IN |  | 0.00 | centreline_B | -250.7 cm | 2 |  |
| 3136.80 | IN |  | 0.00 | sideline_left | -128.8 cm | 1 |  |
| 3141.05 | OUT | **OUT** | 1.00 | sideline_left | 34.2 cm | 2 |  |
| 3142.22 | – |  | – |  | – | 1 | secondary bounce |
| 3143.95 | UNCERTAIN |  | 1.00 | baseline_A | 63.8 cm | 2 |  |
| 3145.64 | IN |  | 0.00 | sideline_right | -74.3 cm | 1 |  |
| 3149.89 | IN |  | 0.00 | baseline_A | -74.0 cm | 2 |  |
| 3151.61 | IN |  | 0.00 | centreline_B | -156.9 cm | 1 |  |
| 3153.70 | UNCERTAIN |  | 1.00 | baseline_B | 120.9 cm | 1 | unconfirmed by iphone17 |
| 3163.05 | IN |  | 0.00 | centreline_A | -120.4 cm | 2 | serve from B left |
| 3164.37 | IN |  | 0.00 | centreline_B | -248.2 cm | 2 |  |
| 3166.24 | IN |  | 0.00 | sideline_right | -14.4 cm | 2 |  |
| 3168.89 | IN |  | 0.00 | sideline_right | -92.4 cm | 1 |  |
| 3170.45 | OUT | **OUT** | 1.00 | sideline_left | 28.9 cm | 2 |  |
| 3173.57 | UNCERTAIN |  | 1.00 | baseline_A | 37.3 cm | 1 |  |
| 3175.00 | UNCERTAIN |  | 1.00 | baseline_A | 92.7 cm | 2 |  |
| 3178.32 | IN |  | 0.00 | centreline_B | -139.5 cm | 2 | serve from A right |
| 3179.92 | IN |  | 0.00 | centreline_A | -208.4 cm | 1 |  |
| 3181.75 | IN |  | 0.00 | centreline_A | -203.4 cm | 1 |  |
| 3182.19 | IN |  | 0.00 | kitchen_A | -147.2 cm | 1 |  |
| 3183.21 | – |  | – |  | – | 2 | secondary bounce |
| 3184.00 | – |  | – |  | – | 2 | secondary bounce |
| 3184.25 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 3184.45 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3188.17 | IN |  | 0.00 | sideline_left | -150.2 cm | 1 |  |
| 3194.10 | IN |  | 0.00 | baseline_B | -121.9 cm | 1 |  |
| 3195.75 | IN |  | 0.00 | centreline_A | -163.1 cm | 1 |  |
| 3198.82 | IN |  | 0.00 | kitchen_A | -54.5 cm | 1 |  |
| 3199.97 | IN |  | 0.00 | kitchen_B | -121.0 cm | 1 |  |
| 3204.10 | IN |  | 0.00 | centreline_A | -145.8 cm | 1 |  |
| 3207.76 | UNCERTAIN |  | 1.00 | sideline_left | 348.2 cm | 1 |  |
| 3208.09 | – |  | – |  | – | 2 | secondary bounce |
| 3209.56 | IN |  | 0.00 | centreline_B | -191.9 cm | 1 |  |
| 3211.30 | IN |  | 0.00 | baseline_A | -112.4 cm | 2 |  |
| 3212.51 | IN |  | 0.00 | sideline_right | -41.7 cm | 1 |  |
| 3217.25 | IN |  | 0.00 | baseline_B | -26.6 cm | 2 |  |
| 3217.80 | – |  | – |  | – | 2 | secondary bounce |
| 3221.74 | IN |  | 0.00 | kitchen_A | -74.4 cm | 2 | serve from B (half unknown) |
| 3223.44 | IN |  | 0.00 | centreline_B | -92.0 cm | 2 |  |
| 3226.20 | IN |  | 0.00 | kitchen_B | -163.0 cm | 2 |  |
| 3227.97 | UNCERTAIN |  | 0.63 | sideline_right | 0.7 cm | 2 |  |
| 3228.81 | – |  | – |  | – | 1 | secondary bounce |
| 3229.29 | – |  | – |  | – | 1 | secondary bounce |
| 3229.54 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3229.80 | – |  | – |  | – | 1 | secondary bounce |
| 3240.36 | IN |  | 0.00 | sideline_left | -138.3 cm | 2 | serve from B left |
| 3242.03 | IN |  | 0.00 | baseline_B | -85.7 cm | 1 |  |
| 3244.45 | UNCERTAIN |  | 1.00 | baseline_A | 63.0 cm | 1 | unconfirmed by samsung |
| 3246.28 | UNCERTAIN |  | 1.00 | sideline_right | 321.9 cm | 1 |  |
| 3246.67 | – |  | – |  | – | 2 | secondary bounce |
| 3247.38 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 3251.29 | UNCERTAIN |  | 1.00 | baseline_A | 77.2 cm | 1 |  |
| 3252.75 | IN |  | 0.00 | sideline_left | -139.9 cm | 2 | serve from A right |
| 3254.56 | UNCERTAIN |  | 1.00 | baseline_A | 19.0 cm | 1 | unconfirmed by samsung |
| 3255.41 | – |  | – |  | – | 1 | secondary bounce |
| 3255.97 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 3256.69 | – |  | – |  | – | 2 | secondary bounce |
| 3263.63 | IN |  | 0.00 | centreline_B | -145.2 cm | 2 | serve from A left |
| 3265.10 | IN |  | 0.00 | centreline_A | -192.0 cm | 1 |  |
| 3266.20 | IN |  | 0.00 | kitchen_A | -74.5 cm | 1 |  |
| 3267.13 | – |  | – |  | – | 2 | secondary bounce |
| 3269.62 | UNCERTAIN |  | 1.00 | sideline_right | 32.9 cm | 1 | unconfirmed by iphone17 |
| 3275.80 | IN |  | 0.00 | baseline_A | -124.4 cm | 1 |  |
| 3277.69 | UNCERTAIN |  | 1.00 | baseline_A | 97.0 cm | 2 |  |
| 3281.53 | IN |  | 0.00 | centreline_B | -137.9 cm | 2 | serve from A right |
| 3283.22 | IN |  | 0.00 | centreline_A | -76.9 cm | 1 |  |
| 3285.16 | IN |  | 0.00 | centreline_A | -179.0 cm | 3 |  |
| 3288.37 | IN |  | 0.00 | kitchen_A | -128.7 cm | 2 |  |
| 3289.71 | IN |  | 0.05 | sideline_left | -13.3 cm | 1 |  |
| 3290.33 | – |  | – |  | – | 2 | secondary bounce |
| 3290.77 | – |  | – |  | – | 2 | secondary bounce |
| 3291.08 | – |  | – |  | – | 1 | secondary bounce |
| 3291.32 | – |  | – |  | – | 1 | secondary bounce |
| 3293.17 | IN |  | 0.00 | centreline_A | -70.7 cm | 1 |  |
| 3295.82 | IN |  | 0.00 | centreline_A | -218.1 cm | 2 |  |
| 3296.52 | – |  | – |  | – | 3 | secondary bounce |
| 3299.17 | UNCERTAIN |  | 1.00 | baseline_A | 78.5 cm | 2 |  |
| 3302.99 | UNCERTAIN |  | 0.96 | baseline_B | 37.9 cm | 1 |  |
| 3304.92 | IN |  | 0.00 | centreline_A | -159.5 cm | 2 |  |
| 3306.49 | IN |  | 0.00 | baseline_B | -83.8 cm | 2 |  |
| 3311.67 | IN |  | 0.00 | sideline_right | -15.2 cm | 1 |  |
| 3313.09 | IN |  | 0.00 | centreline_B | -221.7 cm | 1 |  |
| 3314.84 | IN |  | 0.00 | kitchen_B | -195.3 cm | 1 |  |
| 3315.88 | IN |  | 0.00 | kitchen_A | -30.9 cm | 1 |  |
| 3317.97 | UNCERTAIN |  | 1.00 | sideline_right | 156.0 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 3320.16 | IN |  | 0.00 | baseline_A | -38.6 cm | 1 |  |
| 3322.75 | UNCERTAIN |  | 1.00 | baseline_A | 44.4 cm | 1 |  |
| 3327.87 | IN |  | 0.00 | centreline_B | -21.6 cm | 2 | serve from A right |
| 3328.63 | – |  | – |  | – | 1 | secondary bounce |
| 3329.52 | – |  | – |  | – | 1 | secondary bounce |
| 3330.05 | – |  | – |  | – | 1 | secondary bounce |
| 3333.74 | IN |  | 0.00 | centreline_A | -203.4 cm | 1 |  |
| 3335.79 | UNCERTAIN |  | 1.00 | baseline_B | 67.7 cm | 1 | unconfirmed by iphone17 |
| 3344.44 | IN |  | 0.00 | sideline_right | -152.3 cm | 1 | serve from B (half unknown) |
| 3345.95 | IN |  | 0.00 | centreline_B | -151.7 cm | 2 |  |
| 3346.11 | – |  | – |  | – | 1 | secondary bounce |
| 3352.13 | IN |  | 0.00 | kitchen_A | -227.2 cm | 2 |  |
| 3354.37 | IN |  | 0.00 | centreline_A | -170.8 cm | 1 |  |
| 3354.82 | – |  | – |  | – | 1 | secondary bounce |
| 3357.30 | UNCERTAIN |  | 1.00 | baseline_A | 110.4 cm | 1 |  |
| 3358.70 | IN |  | 0.00 | sideline_left | -45.8 cm | 2 | serve from A right |
| 3359.49 | UNCERTAIN |  | 1.00 | sideline_right | 49.5 cm | 1 |  |
| 3360.19 | IN |  | 0.00 | centreline_A | -148.9 cm | 1 |  |
| 3362.38 | IN |  | 0.00 | centreline_A | -281.6 cm | 3 |  |
| 3361.58 | IN |  | 0.00 | baseline_B | -107.2 cm | 1 |  |
| 3363.25 | UNCERTAIN |  | 1.00 | sideline_left | 14.9 cm | 1 | unconfirmed by samsung |
| 3370.88 | OUT | **OUT** | 1.00 | baseline_A | 58.0 cm | 2 |  |
| 3371.51 | – |  | – |  | – | 1 | secondary bounce |
| 3371.88 | IN |  | 0.00 | baseline_A | -117.8 cm | 1 |  |
| 3373.37 | UNCERTAIN |  | 1.00 | baseline_A | 114.0 cm | 1 |  |
| 3376.72 | IN |  | 0.00 | sideline_right | -21.7 cm | 2 | serve from A left |
| 3378.44 | IN |  | 0.00 | sideline_right | -75.9 cm | 2 |  |
| 3379.38 | UNCERTAIN |  | 1.00 | baseline_B | 106.0 cm | 1 |  |
| 3380.26 | IN |  | 0.00 | centreline_A | -305.4 cm | 1 |  |
| 3383.97 | IN |  | 0.00 | kitchen_B | -74.4 cm | 2 |  |
| 3384.93 | UNCERTAIN |  | 1.00 | baseline_A | 95.7 cm | 1 |  |
| 3385.67 | IN |  | 0.00 | kitchen_B | -223.1 cm | 1 |  |
| 3387.31 | IN |  | 0.00 | kitchen_B | -84.9 cm | 2 |  |
| 3389.24 | OUT | **OUT** | 1.00 | sideline_left | 10.4 cm | 2 |  |
| 3389.93 | – |  | – |  | – | 1 | secondary bounce |
| 3390.43 | – |  | – |  | – | 1 | secondary bounce |
| 3394.29 | UNCERTAIN |  | 1.00 | baseline_B | 78.0 cm | 2 |  |
| 3397.03 | UNCERTAIN |  | 1.00 | baseline_B | 247.1 cm | 1 |  |
| 3402.01 | IN |  | 0.00 | centreline_A | -183.7 cm | 2 |  |
| 3403.27 | IN |  | 0.00 | centreline_B | -226.4 cm | 2 |  |
| 3404.81 | UNCERTAIN |  | 1.00 | baseline_A | 61.2 cm | 1 | unconfirmed by samsung |
| 3407.17 | UNCERTAIN |  | 1.00 | baseline_A | 166.3 cm | 1 |  |
| 3411.14 | IN |  | 0.00 | centreline_B | -177.8 cm | 2 |  |
| 3417.93 | IN |  | 0.00 | kitchen_A | -94.7 cm | 2 | serve from B left |
| 3420.02 | IN |  | 0.00 | centreline_B | -197.7 cm | 2 |  |
| 3422.07 | IN |  | 0.00 | kitchen_B | -117.9 cm | 3 |  |
| 3424.40 | IN |  | 0.00 | kitchen_A | -36.6 cm | 2 |  |
| 3424.98 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3429.63 | IN |  | 0.00 | baseline_B | -75.2 cm | 2 |  |
| 3434.73 | UNCERTAIN |  | 1.00 | sideline_right | 29.4 cm | 1 |  |
| 3447.15 | IN |  | 0.00 | centreline_A | -151.8 cm | 1 |  |
| 3463.70 | UNCERTAIN |  | 1.00 | sideline_left | 43.2 cm | 1 |  |
| 3471.00 | UNCERTAIN |  | 1.00 | baseline_A | 121.3 cm | 1 |  |
| 3472.40 | IN |  | 0.00 | sideline_left | -107.2 cm | 2 | serve from A right |
| 3474.15 | IN |  | 0.00 | centreline_A | -165.8 cm | 2 |  |
| 3477.16 | IN |  | 0.00 | centreline_A | -207.7 cm | 1 |  |
| 3478.10 | UNCERTAIN |  | 1.00 | baseline_B | 390.4 cm | 1 |  |
| 3478.89 | IN |  | 0.00 | kitchen_A | -176.2 cm | 3 |  |
| 3479.69 | IN |  | 0.00 | sideline_right | -69.6 cm | 1 |  |
| 3480.15 | IN |  | 0.00 | sideline_right | -66.1 cm | 2 |  |
| 3480.54 | – |  | – |  | – | 2 | secondary bounce |
| 3482.49 | IN |  | 0.00 | centreline_A | -283.2 cm | 2 |  |
| 3483.48 | – |  | – |  | – | 2 | secondary bounce |
| 3483.91 | – |  | – |  | – | 1 | secondary bounce |
| 3490.46 | UNCERTAIN |  | 0.98 | sideline_right | 21.1 cm | 1 | unconfirmed by samsung |
| 3491.84 | UNCERTAIN |  | 1.00 | baseline_A | 74.0 cm | 1 |  |
| 3492.26 | – |  | – |  | – | 1 | secondary bounce |
| 3492.46 | – |  | – |  | – | 1 | secondary bounce |
| 3495.15 | IN |  | 0.00 | kitchen_B | -29.2 cm | 2 | serve from A (half unknown) |
| 3495.95 | – |  | – |  | – | 2 | secondary bounce |
| 3501.10 | IN |  | 0.00 | kitchen_A | -81.3 cm | 2 | serve from B right |
| 3502.61 | IN |  | 0.00 | centreline_B | -200.6 cm | 1 |  |
| 3504.21 | IN |  | 0.00 | kitchen_A | -199.9 cm | 2 |  |
| 3505.48 | IN |  | 0.00 | sideline_left | -90.2 cm | 1 |  |
| 3506.12 | UNCERTAIN |  | 0.12 | baseline_B | -23.8 cm | 1 |  |
| 3508.08 | IN |  | 0.00 | kitchen_B | -75.7 cm | 1 |  |
| 3512.09 | IN |  | 0.00 | centreline_B | -206.3 cm | 1 |  |
| 3516.30 | UNCERTAIN |  | 0.27 | baseline_A | -1.0 cm | 1 | serve from B (half unknown) |
| 3517.84 | IN |  | 0.00 | sideline_left | -152.9 cm | 2 |  |
| 3519.29 | IN |  | 0.00 | baseline_A | -13.2 cm | 1 |  |
| 3521.43 | OUT | **OUT** | 1.00 | sideline_left | 67.3 cm | 2 |  |
| 3522.76 | IN |  | 0.00 | sideline_left | -109.8 cm | 2 |  |
| 3523.84 | UNCERTAIN |  | 1.00 | sideline_left | 310.5 cm | 1 |  |
| 3524.14 | – |  | – |  | – | 1 | secondary bounce |
| 3524.41 | – |  | – |  | – | 1 | secondary bounce |
| 3529.14 | IN |  | 0.00 | sideline_right | -54.9 cm | 2 | serve from B right |
| 3530.91 | UNCERTAIN |  | 1.00 | sideline_right | 184.4 cm | 1 |  |
| 3531.36 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3534.51 | IN |  | 0.00 | sideline_right | -76.6 cm | 2 |  |
| 3535.22 | – |  | – |  | – | 2 | secondary bounce |
| 3535.90 | IN |  | 0.00 | centreline_B | -36.5 cm | 1 |  |
| 3538.17 | IN |  | 0.00 | centreline_B | -200.1 cm | 1 |  |
| 3538.48 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3543.01 | IN |  | 0.00 | centreline_A | -165.3 cm | 3 |  |
| 3543.60 | – |  | – |  | – | 1 | secondary bounce |
| 3547.90 | UNCERTAIN |  | 1.00 | baseline_A | 71.4 cm | 2 |  |
| 3549.27 | IN |  | 0.00 | centreline_B | -141.1 cm | 2 | serve from A right |
| 3550.85 | IN |  | 0.00 | centreline_A | -167.7 cm | 3 |  |
| 3553.06 | IN |  | 0.00 | sideline_right | -139.9 cm | 1 |  |
| 3560.98 | UNCERTAIN |  | 1.00 | baseline_A | 154.2 cm | 1 |  |
| 3561.98 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 3562.66 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3563.25 | – |  | – |  | – | 1 | secondary bounce |
| 3566.89 | IN |  | 0.00 | centreline_B | -91.1 cm | 2 | serve from A left |
| 3568.57 | IN |  | 0.00 | baseline_A | -52.9 cm | 1 |  |
| 3569.99 | UNCERTAIN |  | 0.20 | kitchen_A | -5.4 cm | 1 |  |
| 3571.19 | – |  | – |  | – | 1 | secondary bounce |
| 3582.40 | IN |  | 0.00 | baseline_B | -95.3 cm | 1 |  |
| 3583.34 | IN |  | 0.00 | centreline_A | -51.5 cm | 3 | serve from B right |
| 3583.82 | – |  | – |  | – | 1 | secondary bounce |
| 3585.08 | IN |  | 0.03 | centreline_B | -29.3 cm | 1 |  |
| 3587.32 | UNCERTAIN |  | 1.00 | baseline_A | 137.1 cm | 1 | unconfirmed by samsung |
| 3589.99 | UNCERTAIN |  | 1.00 | baseline_A | 125.0 cm | 1 | unconfirmed by samsung |
| 3591.79 | IN |  | 0.00 | centreline_B | -234.1 cm | 2 |  |
| 3596.01 | IN |  | 0.00 | baseline_A | -91.9 cm | 1 |  |
| 3597.63 | IN |  | 0.00 | centreline_B | -262.3 cm | 2 |  |
| 3599.59 | UNCERTAIN |  | 1.00 | sideline_right | 163.4 cm | 1 | silent: start of play far outside the court (ball handling?) |
| 3600.85 | UNCERTAIN |  | 1.00 | sideline_right | 221.9 cm | 1 |  |
| 3601.00 | – |  | – |  | – | 1 | secondary bounce |
| 3612.20 | IN |  | 0.00 | sideline_right | -87.3 cm | 2 | serve from B right |
| 3613.75 | IN |  | 0.00 | baseline_B | -105.8 cm | 1 |  |
| 3615.89 | IN |  | 0.00 | sideline_right | -27.1 cm | 1 |  |
| 3617.75 | UNCERTAIN |  | 1.00 | baseline_B | 49.8 cm | 1 |  |
| 3618.48 | – |  | – |  | – | 1 | secondary bounce |
| 3618.99 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3619.37 | UNCERTAIN |  | 1.00 | baseline_B | 277.8 cm | 1 |  |
| 3627.85 | UNCERTAIN |  | 1.00 | baseline_A | 27.4 cm | 1 |  |
| 3631.92 | IN |  | 0.00 | centreline_A | -219.1 cm | 2 |  |
| 3633.46 | IN |  | 0.00 | centreline_B | -230.5 cm | 2 |  |
| 3635.04 | IN |  | 0.00 | kitchen_B | -130.0 cm | 1 |  |
| 3644.42 | UNCERTAIN |  | 0.63 | baseline_A | 8.8 cm | 1 |  |
| 3648.19 | UNCERTAIN |  | 1.00 | baseline_A | 82.4 cm | 1 |  |

## The Mac's load

* Whole machine (8 logical cores): median 19%, 90% of the time below 31%, peak 51%
* BallTracker's camera workers: median 0.41 cores, peak 1.15
* Server process: median 31% of a core
* Busiest other app: WindowServer (median 21% of a core when it was the busiest)

## Warnings

* 60.8 s iphone17: iphone17: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 547.1 s samsung: samsung: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 803.4 s iphone17: iphone17: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 813.7 s iphone17: iphone17: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 1154.2 s nothing: nothing: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 1658.4 s iphone17: iphone17: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 1970.4 s samsung: samsung moved 104.8 px since it was calibrated: recalibrate it
* 2044.1 s samsung: samsung moved 113.1 px since it was calibrated: recalibrate it
* 2044.3 s redmi: redmi moved 80.3 px since it was calibrated: recalibrate it
* 2097.6 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2108.1 s redmi: redmi moved 119.4 px since it was calibrated: recalibrate it
* 2118.3 s samsung: samsung: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2118.6 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2161.8 s redmi: redmi moved 128.7 px since it was calibrated: recalibrate it
* 2172.3 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2214.3 s redmi: redmi moved 130.3 px since it was calibrated: recalibrate it
* 2224.9 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2235.4 s redmi: redmi moved 134.1 px since it was calibrated: recalibrate it
* 2268.0 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2278.5 s redmi: redmi moved 123.1 px since it was calibrated: recalibrate it
* 2299.8 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2310.3 s redmi: redmi moved 132.1 px since it was calibrated: recalibrate it
* 2332.6 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2354.6 s redmi: redmi moved 29.7 px since it was calibrated: recalibrate it
* 2429.3 s redmi: redmi moved 26.2 px since it was calibrated: recalibrate it
* 2492.8 s iphone17: iphone17: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2715.5 s iphone17: iphone17: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 2737.8 s redmi: redmi moved 33.0 px since it was calibrated: recalibrate it
* 2791.2 s redmi: redmi moved 36.4 px since it was calibrated: recalibrate it
* 2957.0 s redmi: redmi moved 23.9 px since it was calibrated: recalibrate it
* 2998.8 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 3083.8 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 3117.2 s redmi: redmi moved 34.8 px since it was calibrated: recalibrate it
* 3225.1 s redmi: redmi moved 24.7 px since it was calibrated: recalibrate it
* 3278.7 s redmi: redmi moved 81.2 px since it was calibrated: recalibrate it
* 3384.8 s redmi: redmi moved 23.8 px since it was calibrated: recalibrate it
* 3472.0 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)
* 3503.4 s redmi: redmi moved 217.9 px since it was calibrated: recalibrate it
* 3588.5 s redmi: redmi: can't match the image to its calibration frame (covered, dark, or moved a lot?)

## Calibrations

* iphone17 at 802 s (snap): RMS 0.05 px from 12 points; worst point A_right_corner 0.1 px
* iphone17 at 805 s (snap): RMS 0.05 px from 12 points; worst point A_right_corner 0.1 px
* iphone17 at 876 s (drift): RMS 0.13 px from 12 points; moved 9.1 px
* samsung at 1061 s (snap + lines (auto)): RMS 1.39 px from 12 points; worst point B_left_corner 2.0 px
* iphone17 at 1062 s (lines (auto, after samsung)): RMS 0.54 px from 12 points; moved 8.5 px
* iphone17 at 1082 s (drift): RMS 1.15 px from 12 points; moved 9.3 px
* samsung at 1083 s (drift): RMS 1.96 px from 12 points; moved 6.7 px
* samsung at 1308 s (drift): RMS 1.75 px from 12 points; moved 4.7 px
* iphone17 at 1399 s (proposal-bounces + lines (auto)): RMS 0.33 px from 12 points; worst point A_right_corner 0.6 px
* samsung at 1400 s (lines (auto, after iphone17)): RMS 1.41 px from 12 points; moved 10.5 px
* samsung at 1421 s (drift): RMS 1.66 px from 12 points; moved 14.2 px
* nothing at 1495 s (snap + lines (auto)): RMS 1.71 px from 11 points; worst point B_kitchen_right 2.8 px
* samsung at 1498 s (lines (auto, after nothing)): RMS 1.41 px from 12 points; moved 13.3 px
* samsung at 1514 s (drift): RMS 1.56 px from 12 points; moved 14.4 px
* samsung at 1628 s (drift): RMS 0.60 px from 12 points; moved 3.9 px
* samsung at 1690 s (drift): RMS 0.69 px from 12 points; moved 3.2 px
* samsung at 1784 s (drift): RMS 1.97 px from 12 points; moved 4.3 px
* samsung at 1909 s (drift): RMS 1.35 px from 12 points; moved 3.4 px
* iphone17 at 2023 s (drift): RMS 0.21 px from 12 points; moved 12.9 px
* redmi at 2039 s (snap + lines (auto)): RMS 0.97 px from 8 points; worst point B_left_corner 1.1 px
* iphone17 at 2040 s (lines (auto, after redmi)): RMS 0.95 px from 12 points; moved 11.3 px
* samsung at 2042 s (lines (auto, after redmi)): RMS 1.41 px from 12 points; moved 22.2 px
* iphone17 at 2055 s (drift): RMS 0.82 px from 12 points; moved 12.5 px
* samsung at 2151 s (drift): RMS 1.75 px from 12 points; moved 21.8 px
* samsung at 2247 s (drift): RMS 1.90 px from 12 points; moved 3.3 px
* samsung at 2332 s (drift): RMS 1.85 px from 12 points; moved 9.9 px
* redmi at 2335 s (snap): RMS 3.62 px from 5 points; worst point B_centre_kitchen 5.8 px
* iphone17 at 2336 s (lines (auto, after redmi)): RMS 1.15 px from 12 points; moved 13.5 px
* iphone17 at 2397 s (drift): RMS 1.31 px from 12 points; moved 13.4 px
* nothing at 2462 s (drift): RMS 1.66 px from 11 points; moved 3.1 px
* samsung at 2515 s (drift): RMS 1.34 px from 12 points; moved 10.1 px
* iphone17 at 2578 s (drift): RMS 0.14 px from 12 points; moved 3.2 px
* nothing at 2643 s (drift): RMS 1.27 px from 11 points; moved 3.8 px
* iphone17 at 2865 s (drift): RMS 0.37 px from 12 points; moved 3.1 px
* samsung at 2877 s (drift): RMS 2.07 px from 12 points; moved 4.6 px
* nothing at 2889 s (drift): RMS 1.62 px from 11 points; moved 4.6 px
* iphone17 at 2900 s (drift): RMS 0.48 px from 12 points; moved 3.0 px
* nothing at 2912 s (drift): RMS 1.91 px from 11 points; moved 5.1 px
* iphone17 at 2934 s (drift): RMS 1.37 px from 12 points; moved 3.5 px
* iphone17 at 2956 s (drift): RMS 0.72 px from 12 points; moved 3.3 px
* samsung at 3063 s (drift): RMS 2.07 px from 12 points; moved 3.7 px
* iphone17 at 3095 s (drift): RMS 0.93 px from 12 points; moved 3.8 px
* iphone17 at 3191 s (drift): RMS 0.09 px from 12 points; moved 3.8 px
* samsung at 3224 s (drift): RMS 2.27 px from 12 points; moved 3.9 px
* iphone17 at 3278 s (drift): RMS 1.28 px from 12 points; moved 3.9 px
* iphone17 at 3396 s (drift): RMS 0.64 px from 12 points; moved 3.3 px
* samsung at 3408 s (drift): RMS 2.13 px from 12 points; moved 5.6 px
* iphone17 at 3472 s (drift): RMS 1.27 px from 12 points; moved 4.4 px
* iphone17 at 3546 s (drift): RMS 0.15 px from 12 points; moved 4.0 px
* iphone17 at 3600 s (drift): RMS 0.07 px from 12 points; moved 3.0 px
