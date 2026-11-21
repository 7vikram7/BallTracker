# Session 20261121-071625

* **When:** 2026-11-21T07:16:25+0530 → not closed cleanly (–)
* **Code:** commit `747b106e84e0feebd45a21177e505129a966bcaf` + 1 uncommitted files; bounce 0.4.0, fusion 0.1.0, phone detector edge_color_motion 1.0.0, protocol 2
* **Command:** `~/Vikram/BallTracker/.venv/bin/bt serve --record`
* **Court:** pickleball, 6.10 × 13.41 m
* **Settings:** {"record": true, "phone_reduction": true, "detector_overrides": {}, "hold_s": 0.6, "window_s": 0.08, "corroborate": true}

## Cameras

| camera | kind | device | frames | dropped | clock rtt / ± | calibration | lowest fps | worst latency | disconnects |
|---|---|---|---|---|---|---|---|---|---|
| samsung | edge | samsung SM-S948B | 181562 | 0 (0.0%) | 164 / ±81.9 ms | 6.90 px | 51 | 412 ms | 1 |
| iphone17 | edge | Apple iPhone 17 | 349834 | 287 (0.1%) | 7 / ±3.3 ms | 2.36 px | 120 | 3407 ms | 1 |
| nothing | edge | Nothing A009P | 72401 | 0 (0.0%) | 228 / ±114.1 ms | 2.15 px | 26 | 21 ms | 1 |

## Calls

1740 single-camera reports → 1286 decisions (425 seen by 2+ cameras): IN 608, OUT 22, UNCERTAIN 344, suppressed (2nd bounce) 312
Spoken: 22. Delay bounce → call: median 1.38 s, max 4.40 s.

| t (s) | call | spoken | p(out) | line | distance | cameras | note |
|---|---|---|---|---|---|---|---|
| 238.77 | IN |  | 0.00 | centreline_A | -94.9 cm | 1 |  |
| 242.35 | IN |  | 0.04 | sideline_right | -107.9 cm | 1 |  |
| 257.74 | UNCERTAIN |  | 1.00 | sideline_right | 152.6 cm | 1 |  |
| 284.68 | UNCERTAIN |  | 0.77 | sideline_left | -37.9 cm | 1 |  |
| 297.80 | UNCERTAIN |  | 1.00 | baseline_A | 213.2 cm | 1 |  |
| 381.63 | IN |  | 0.00 | centreline_A | -247.2 cm | 1 |  |
| 425.17 | UNCERTAIN |  | 0.86 | sideline_left | 121.4 cm | 1 |  |
| 435.91 | UNCERTAIN |  | 1.00 | baseline_A | 34.0 cm | 1 |  |
| 444.45 | UNCERTAIN |  | 1.00 | baseline_A | 114.7 cm | 1 |  |
| 449.12 | UNCERTAIN |  | 0.99 | baseline_A | 108.9 cm | 1 |  |
| 919.31 | UNCERTAIN |  | 1.00 | sideline_right | 357.6 cm | 1 |  |
| 985.08 | UNCERTAIN |  | 1.00 | sideline_right | 52.6 cm | 1 | unconfirmed by samsung |
| 987.11 | UNCERTAIN |  | 1.00 | sideline_right | 272.0 cm | 1 |  |
| 1045.02 | UNCERTAIN |  | 1.00 | sideline_right | 349.2 cm | 1 |  |
| 1049.98 | UNCERTAIN |  | 1.00 | sideline_right | 134.1 cm | 1 |  |
| 1069.22 | IN |  | 0.00 | kitchen_A | -32.8 cm | 1 |  |
| 1182.24 | IN |  | 0.00 | kitchen_A | -39.7 cm | 1 |  |
| 1208.95 | IN |  | 0.00 | kitchen_B | -206.3 cm | 1 |  |
| 1215.94 | IN |  | 0.00 | kitchen_B | -226.4 cm | 1 |  |
| 1217.39 | IN |  | 0.00 | centreline_B | -245.5 cm | 1 |  |
| 1217.80 | – |  | – |  | – | 1 | secondary bounce |
| 1218.91 | IN |  | 0.00 | centreline_B | -252.0 cm | 1 |  |
| 1220.22 | IN |  | 0.00 | kitchen_B | -182.7 cm | 1 |  |
| 1220.92 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1221.41 | IN |  | 0.00 | kitchen_B | -88.9 cm | 1 |  |
| 1256.76 | UNCERTAIN |  | 1.00 | sideline_left | 100.7 cm | 1 |  |
| 1262.99 | UNCERTAIN |  | 1.00 | sideline_left | 146.1 cm | 1 |  |
| 1265.71 | UNCERTAIN |  | 1.00 | sideline_left | 50.1 cm | 1 |  |
| 1274.43 | UNCERTAIN |  | 1.00 | baseline_B | 110.2 cm | 1 |  |
| 1279.65 | UNCERTAIN |  | 0.85 | baseline_B | 15.9 cm | 1 |  |
| 1281.33 | UNCERTAIN |  | 0.47 | baseline_B | -1.5 cm | 1 |  |
| 1284.30 | UNCERTAIN |  | 0.24 | baseline_B | -10.6 cm | 1 |  |
| 1284.89 | IN |  | 0.02 | sideline_left | -18.1 cm | 1 |  |
| 1286.29 | IN |  | 0.00 | sideline_left | -56.5 cm | 1 |  |
| 1288.25 | UNCERTAIN |  | 0.27 | baseline_B | -10.7 cm | 1 |  |
| 1316.69 | UNCERTAIN |  | 1.00 | baseline_B | 42.7 cm | 2 |  |
| 1317.19 | – |  | – |  | – | 2 | secondary bounce |
| 1317.91 | – |  | – |  | – | 1 | secondary bounce |
| 1322.68 | UNCERTAIN |  | 1.00 | baseline_B | 46.9 cm | 2 |  |
| 1323.55 | IN |  | 0.00 | baseline_B | -85.0 cm | 1 |  |
| 1323.98 | IN |  | 0.00 | kitchen_B | -60.2 cm | 1 |  |
| 1324.29 | – |  | – |  | – | 1 | secondary bounce |
| 1324.55 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1324.97 | – |  | – |  | – | 1 | secondary bounce |
| 1325.29 | – |  | – |  | – | 1 | secondary bounce |
| 1339.78 | UNCERTAIN |  | 1.00 | baseline_B | 38.4 cm | 1 |  |
| 1341.31 | IN |  | 0.00 | centreline_A | -211.3 cm | 1 |  |
| 1342.98 | IN |  | 0.00 | sideline_left | -62.8 cm | 2 |  |
| 1343.68 | – |  | – |  | – | 2 | secondary bounce |
| 1344.32 | – |  | – |  | – | 2 | secondary bounce |
| 1344.59 | – |  | – |  | – | 1 | secondary bounce |
| 1347.33 | UNCERTAIN |  | 1.00 | baseline_B | 101.8 cm | 2 |  |
| 1348.64 | IN |  | 0.00 | centreline_A | -225.2 cm | 2 |  |
| 1350.14 | IN |  | 0.01 | sideline_left | -14.2 cm | 2 |  |
| 1351.39 | IN |  | 0.00 | centreline_A | -186.7 cm | 1 |  |
| 1351.40 | – |  | – |  | – | 1 | secondary bounce |
| 1352.67 | IN |  | 0.00 | kitchen_B | -232.6 cm | 1 |  |
| 1353.31 | – |  | – |  | – | 1 | secondary bounce |
| 1352.68 | IN |  | 0.00 | kitchen_B | -222.7 cm | 1 |  |
| 1360.98 | UNCERTAIN |  | 0.25 | kitchen_A | -4.5 cm | 1 |  |
| 1361.53 | – |  | – |  | – | 1 | secondary bounce |
| 1362.20 | – |  | – |  | – | 2 | secondary bounce |
| 1361.92 | IN |  | 0.00 | kitchen_A | -115.2 cm | 1 |  |
| 1365.69 | UNCERTAIN |  | 0.57 | sideline_right | 1.2 cm | 1 |  |
| 1369.92 | IN |  | 0.00 | centreline_B | -123.0 cm | 2 |  |
| 1371.34 | IN |  | 0.00 | kitchen_B | -73.6 cm | 2 |  |
| 1371.69 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1372.03 | – |  | – |  | – | 1 | secondary bounce |
| 1372.48 | – |  | – |  | – | 1 | secondary bounce |
| 1380.10 | UNCERTAIN |  | 0.91 | sideline_right | 5.2 cm | 2 |  |
| 1381.78 | IN |  | 0.00 | centreline_A | -89.9 cm | 1 |  |
| 1383.44 | IN |  | 0.00 | centreline_B | -165.3 cm | 1 |  |
| 1383.45 | – |  | – |  | – | 1 | secondary bounce |
| 1384.79 | IN |  | 0.00 | baseline_A | -70.8 cm | 1 |  |
| 1389.22 | IN |  | 0.00 | sideline_right | -87.2 cm | 1 |  |
| 1389.24 | – |  | – |  | – | 1 | secondary bounce |
| 1392.64 | IN |  | 0.03 | kitchen_A | -47.4 cm | 1 |  |
| 1391.00 | IN |  | 0.00 | centreline_A | -25.3 cm | 1 |  |
| 1396.95 | IN |  | 0.00 | centreline_B | -74.1 cm | 2 |  |
| 1398.54 | OUT | **OUT** | 1.00 | baseline_A | 17.8 cm | 2 |  |
| 1399.83 | IN |  | 0.00 | centreline_B | -190.1 cm | 2 |  |
| 1401.36 | IN |  | 0.00 | baseline_A | -50.4 cm | 1 |  |
| 1402.90 | IN |  | 0.00 | sideline_right | -41.0 cm | 1 |  |
| 1403.19 | – |  | – |  | – | 1 | secondary bounce |
| 1406.49 | IN |  | 0.00 | sideline_right | -17.6 cm | 1 |  |
| 1416.38 | IN |  | 0.00 | centreline_B | -102.5 cm | 2 |  |
| 1417.45 | IN |  | 0.00 | kitchen_A | -218.7 cm | 2 |  |
| 1418.05 | – |  | – |  | – | 2 | secondary bounce |
| 1419.68 | IN |  | 0.00 | sideline_left | -109.8 cm | 2 |  |
| 1421.12 | IN |  | 0.00 | sideline_left | -59.4 cm | 1 |  |
| 1421.63 | – |  | – |  | – | 1 | secondary bounce |
| 1422.01 | – |  | – |  | – | 1 | secondary bounce |
| 1422.26 | – |  | – |  | – | 1 | secondary bounce |
| 1426.14 | IN |  | 0.00 | sideline_left | -83.2 cm | 1 |  |
| 1427.38 | IN |  | 0.02 | centreline_A | -108.6 cm | 1 |  |
| 1428.46 | IN |  | 0.00 | centreline_B | -206.4 cm | 2 |  |
| 1429.92 | IN |  | 0.00 | kitchen_A | -222.3 cm | 1 |  |
| 1430.40 | – |  | – |  | – | 1 | secondary bounce |
| 1436.62 | IN |  | 0.00 | baseline_B | -11.4 cm | 1 |  |
| 1437.80 | IN |  | 0.00 | centreline_A | -222.5 cm | 2 |  |
| 1439.27 | IN |  | 0.00 | centreline_B | -174.1 cm | 1 |  |
| 1440.85 | UNCERTAIN |  | 0.95 | sideline_right | 7.8 cm | 1 | unconfirmed by nothing |
| 1441.25 | UNCERTAIN |  | 1.00 | sideline_right | 164.8 cm | 1 |  |
| 1450.26 | UNCERTAIN |  | 1.00 | sideline_right | 37.0 cm | 1 | unconfirmed by nothing |
| 1451.20 | UNCERTAIN |  | 1.00 | sideline_left | 72.8 cm | 1 | unconfirmed by samsung, iphone17 |
| 1454.85 | UNCERTAIN |  | 1.00 | baseline_A | 322.6 cm | 1 |  |
| 1455.89 | IN |  | 0.00 | centreline_B | -143.1 cm | 1 |  |
| 1459.38 | IN |  | 0.00 | kitchen_A | -81.0 cm | 1 |  |
| 1457.37 | IN |  | 0.00 | centreline_A | -140.1 cm | 1 |  |
| 1458.72 | IN |  | 0.00 | kitchen_A | -23.8 cm | 1 |  |
| 1462.90 | IN |  | 0.00 | centreline_B | -265.0 cm | 2 |  |
| 1464.69 | IN |  | 0.00 | sideline_right | -116.8 cm | 2 |  |
| 1467.29 | IN |  | 0.00 | centreline_A | -156.5 cm | 2 |  |
| 1468.93 | IN |  | 0.00 | centreline_B | -76.4 cm | 2 |  |
| 1470.22 | IN |  | 0.00 | baseline_A | -80.3 cm | 2 |  |
| 1476.82 | IN |  | 0.00 | sideline_right | -15.4 cm | 2 |  |
| 1477.78 | UNCERTAIN |  | 1.00 | sideline_right | 16.9 cm | 1 | unconfirmed by iphone17 |
| 1484.51 | IN |  | 0.00 | centreline_A | -233.4 cm | 1 |  |
| 1526.90 | UNCERTAIN |  | 1.00 | baseline_B | 95.4 cm | 1 |  |
| 1527.33 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1545.06 | UNCERTAIN |  | 1.00 | baseline_B | 80.3 cm | 2 |  |
| 1547.39 | UNCERTAIN |  | 1.00 | baseline_B | 221.5 cm | 1 |  |
| 1548.90 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1580.57 | UNCERTAIN |  | 0.09 | sideline_left | -10.2 cm | 2 |  |
| 1581.03 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1582.48 | UNCERTAIN |  | 0.97 | sideline_left | 12.7 cm | 2 | cameras disagree (chi2 21) |
| 1582.92 | – |  | – |  | – | 1 | secondary bounce |
| 1584.51 | UNCERTAIN |  | 0.37 | sideline_left | -5.0 cm | 1 |  |
| 1584.93 | UNCERTAIN |  | 0.31 | sideline_left | -10.4 cm | 1 |  |
| 1588.16 | IN |  | 0.00 | kitchen_A | -210.5 cm | 1 |  |
| 1593.21 | UNCERTAIN |  | 0.73 | baseline_A | 28.5 cm | 3 |  |
| 1593.61 | UNCERTAIN |  | 0.98 | sideline_left | 67.8 cm | 1 |  |
| 1594.96 | IN |  | 0.00 | kitchen_B | -121.3 cm | 2 |  |
| 1595.64 | IN |  | 0.00 | sideline_right | -57.5 cm | 1 |  |
| 1596.27 | IN |  | 0.00 | centreline_A | -210.4 cm | 1 |  |
| 1604.34 | IN |  | 0.00 | baseline_A | -15.5 cm | 1 |  |
| 1605.91 | IN |  | 0.00 | centreline_B | -164.2 cm | 2 |  |
| 1607.56 | IN |  | 0.00 | centreline_A | -133.5 cm | 2 |  |
| 1608.99 | IN |  | 0.00 | centreline_B | -44.5 cm | 2 |  |
| 1609.46 | IN |  | 0.00 | baseline_B | -92.0 cm | 2 |  |
| 1613.95 | IN |  | 0.00 | centreline_B | -85.1 cm | 2 |  |
| 1615.48 | IN |  | 0.00 | centreline_A | -228.3 cm | 2 |  |
| 1615.72 | – |  | – |  | – | 1 | secondary bounce |
| 1616.73 | IN |  | 0.00 | kitchen_A | -192.0 cm | 2 |  |
| 1617.00 | – |  | – |  | – | 2 | secondary bounce |
| 1617.22 | – |  | – |  | – | 1 | secondary bounce |
| 1618.78 | IN |  | 0.00 | baseline_A | -70.4 cm | 3 |  |
| 1619.16 | – |  | – |  | – | 1 | secondary bounce |
| 1620.02 | IN |  | 0.00 | sideline_right | -94.0 cm | 2 |  |
| 1620.57 | – |  | – |  | – | 1 | secondary bounce |
| 1621.05 | – |  | – |  | – | 1 | secondary bounce |
| 1626.65 | IN |  | 0.00 | centreline_B | -287.8 cm | 2 |  |
| 1627.34 | – |  | – |  | – | 1 | secondary bounce |
| 1628.92 | IN |  | 0.00 | centreline_A | -138.4 cm | 2 |  |
| 1630.91 | IN |  | 0.00 | kitchen_A | -109.9 cm | 1 |  |
| 1630.06 | UNCERTAIN |  | 0.39 | kitchen_B | -2.2 cm | 1 |  |
| 1631.16 | IN |  | 0.00 | kitchen_A | -146.7 cm | 1 |  |
| 1630.70 | IN |  | 0.00 | kitchen_A | -124.3 cm | 1 |  |
| 1630.91 | – |  | – |  | – | 1 | secondary bounce |
| 1634.62 | IN |  | 0.00 | centreline_B | -160.2 cm | 1 |  |
| 1636.53 | IN |  | 0.00 | sideline_left | -47.1 cm | 2 |  |
| 1637.91 | IN |  | 0.00 | sideline_left | -23.8 cm | 2 |  |
| 1638.88 | – |  | – |  | – | 1 | secondary bounce |
| 1643.77 | IN |  | 0.00 | kitchen_A | -102.2 cm | 1 |  |
| 1643.77 | – |  | – |  | – | 1 | secondary bounce |
| 1645.13 | IN |  | 0.00 | centreline_B | -215.3 cm | 1 |  |
| 1645.13 | – |  | – |  | – | 1 | secondary bounce |
| 1646.72 | IN |  | 0.00 | sideline_left | -41.3 cm | 2 |  |
| 1647.15 | UNCERTAIN |  | 1.00 | sideline_left | 383.3 cm | 1 |  |
| 1647.46 | – |  | – |  | – | 3 | secondary bounce |
| 1648.35 | UNCERTAIN |  | 1.00 | sideline_left | 72.2 cm | 2 | cameras disagree (chi2 19) |
| 1649.24 | – |  | – |  | – | 1 | secondary bounce |
| 1649.46 | – |  | – |  | – | 1 | secondary bounce |
| 1653.26 | UNCERTAIN |  | 1.00 | baseline_B | 264.4 cm | 1 |  |
| 1656.22 | IN |  | 0.00 | sideline_right | -44.0 cm | 2 |  |
| 1657.98 | IN |  | 0.00 | sideline_left | -90.8 cm | 2 |  |
| 1658.50 | – |  | – |  | – | 2 | secondary bounce |
| 1658.88 | – |  | – |  | – | 1 | secondary bounce |
| 1662.56 | UNCERTAIN |  | 1.00 | sideline_left | 38.1 cm | 1 |  |
| 1663.82 | UNCERTAIN |  | 0.78 | sideline_left | 6.4 cm | 2 |  |
| 1665.78 | OUT | **OUT** | 1.00 | sideline_right | 89.8 cm | 1 |  |
| 1666.80 | – |  | – |  | – | 1 | secondary bounce |
| 1667.88 | UNCERTAIN |  | 1.00 | sideline_right | 101.5 cm | 1 |  |
| 1678.10 | IN |  | 0.00 | sideline_right | -67.9 cm | 1 |  |
| 1680.45 | IN |  | 0.00 | centreline_A | -137.7 cm | 1 |  |
| 1680.97 | – |  | – |  | – | 1 | secondary bounce |
| 1685.69 | IN |  | 0.00 | centreline_B | -159.0 cm | 1 |  |
| 1686.02 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 1686.28 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 1686.46 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1687.98 | OUT | **OUT** | 1.00 | sideline_right | 171.7 cm | 1 |  |
| 1688.75 | – |  | – |  | – | 1 | secondary bounce |
| 1688.98 | – |  | – |  | – | 1 | secondary bounce |
| 1695.17 | UNCERTAIN |  | 1.00 | baseline_B | 99.0 cm | 1 |  |
| 1696.72 | IN |  | 0.00 | centreline_A | -247.5 cm | 1 |  |
| 1700.68 | UNCERTAIN |  | 0.06 | baseline_B | -26.9 cm | 1 |  |
| 1702.72 | UNCERTAIN |  | 1.00 | sideline_left | 167.6 cm | 1 | unconfirmed by samsung, nothing |
| 1703.65 | – |  | – |  | – | 3 | secondary bounce |
| 1704.75 | – |  | – |  | – | 1 | secondary bounce |
| 1705.08 | – |  | – |  | – | 1 | secondary bounce |
| 1707.55 | UNCERTAIN |  | 1.00 | sideline_left | 48.6 cm | 2 |  |
| 1708.95 | IN |  | 0.00 | sideline_right | -138.3 cm | 1 |  |
| 1710.20 | IN |  | 0.00 | centreline_A | -250.2 cm | 2 |  |
| 1710.83 | – |  | – |  | – | 1 | secondary bounce |
| 1712.47 | UNCERTAIN |  | 1.00 | baseline_A | 127.9 cm | 2 |  |
| 1712.13 | UNCERTAIN |  | 1.00 | baseline_A | 40.4 cm | 1 |  |
| 1713.94 | UNCERTAIN |  | 1.00 | baseline_A | 234.7 cm | 1 |  |
| 1718.38 | IN |  | 0.00 | centreline_A | -163.1 cm | 2 |  |
| 1719.94 | IN |  | 0.00 | sideline_left | -28.2 cm | 2 |  |
| 1721.66 | IN |  | 0.00 | centreline_A | -173.0 cm | 2 |  |
| 1722.93 | IN |  | 0.00 | centreline_B | -200.4 cm | 2 |  |
| 1724.11 | – |  | – |  | – | 1 | secondary bounce |
| 1725.62 | UNCERTAIN |  | 1.00 | baseline_B | 301.3 cm | 1 |  |
| 1727.96 | IN |  | 0.00 | sideline_left | -143.0 cm | 2 |  |
| 1729.63 | UNCERTAIN |  | 1.00 | baseline_B | 249.5 cm | 1 |  |
| 1730.69 | IN |  | 0.00 | kitchen_A | -184.2 cm | 2 |  |
| 1731.79 | – |  | – |  | – | 3 | secondary bounce |
| 1731.32 | IN |  | 0.00 | centreline_A | -218.2 cm | 1 |  |
| 1732.32 | – |  | – |  | – | 1 | secondary bounce |
| 1733.33 | – |  | – |  | – | 2 | secondary bounce |
| 1733.66 | – |  | – |  | – | 1 | secondary bounce |
| 1740.34 | UNCERTAIN |  | 1.00 | baseline_B | 128.3 cm | 1 |  |
| 1741.23 | – |  | – |  | – | 1 | secondary bounce |
| 1744.82 | IN |  | 0.00 | centreline_A | -249.5 cm | 1 |  |
| 1746.24 | IN |  | 0.00 | baseline_B | -133.4 cm | 1 |  |
| 1747.62 | IN |  | 0.00 | baseline_A | -53.6 cm | 1 |  |
| 1748.27 | IN |  | 0.00 | sideline_left | -79.7 cm | 1 |  |
| 1748.42 | – |  | – |  | – | 1 | secondary bounce |
| 1749.33 | IN |  | 0.00 | centreline_B | -203.7 cm | 2 |  |
| 1750.44 | UNCERTAIN |  | 1.00 | sideline_left | 68.1 cm | 1 | unconfirmed by samsung, nothing |
| 1751.11 | IN |  | 0.00 | kitchen_A | -150.6 cm | 2 |  |
| 1751.79 | – |  | – |  | – | 3 | secondary bounce |
| 1754.89 | IN |  | 0.00 | baseline_A | -45.1 cm | 1 |  |
| 1756.32 | IN |  | 0.00 | centreline_B | -147.1 cm | 1 |  |
| 1757.87 | OUT | **OUT** | 1.00 | sideline_right | 120.0 cm | 1 |  |
| 1762.59 | UNCERTAIN |  | 1.00 | baseline_A | 115.9 cm | 1 | unconfirmed by samsung |
| 1769.85 | IN |  | 0.00 | baseline_B | -145.2 cm | 2 |  |
| 1770.16 | IN |  | 0.00 | centreline_A | -212.5 cm | 2 |  |
| 1771.64 | IN |  | 0.00 | baseline_A | -85.3 cm | 2 |  |
| 1772.07 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 1773.35 | IN |  | 0.00 | centreline_B | -67.6 cm | 1 |  |
| 1775.83 | IN |  | 0.00 | centreline_A | -72.6 cm | 2 |  |
| 1780.28 | IN |  | 0.00 | sideline_right | -74.2 cm | 2 |  |
| 1783.45 | IN |  | 0.00 | sideline_left | -16.6 cm | 2 |  |
| 1784.53 | UNCERTAIN |  | 0.13 | sideline_left | -31.0 cm | 1 |  |
| 1785.04 | IN |  | 0.00 | centreline_B | -151.4 cm | 1 |  |
| 1786.40 | IN |  | 0.00 | kitchen_B | -93.1 cm | 1 |  |
| 1786.83 | – |  | – |  | – | 1 | secondary bounce |
| 1791.59 | IN |  | 0.00 | centreline_A | -247.7 cm | 2 |  |
| 1793.16 | IN |  | 0.00 | centreline_B | -160.4 cm | 2 |  |
| 1794.91 | UNCERTAIN |  | 0.08 | sideline_left | -43.1 cm | 1 |  |
| 1796.08 | IN |  | 0.00 | sideline_left | -69.1 cm | 1 |  |
| 1798.01 | IN |  | 0.00 | baseline_A | -55.3 cm | 2 |  |
| 1799.44 | IN |  | 0.00 | baseline_B | -94.6 cm | 1 |  |
| 1801.83 | IN |  | 0.00 | kitchen_B | -92.0 cm | 1 |  |
| 1802.33 | UNCERTAIN |  | 0.18 | kitchen_B | -7.3 cm | 1 |  |
| 1802.62 | UNCERTAIN |  | 0.23 | kitchen_A | -4.9 cm | 1 |  |
| 1804.19 | UNCERTAIN |  | 0.17 | baseline_A | -5.2 cm | 1 |  |
| 1805.02 | UNCERTAIN |  | 0.99 | sideline_left | 61.5 cm | 1 |  |
| 1804.20 | IN |  | 0.00 | sideline_left | -5.8 cm | 1 |  |
| 1805.52 | UNCERTAIN |  | 1.00 | sideline_left | 129.6 cm | 1 |  |
| 1805.01 | UNCERTAIN |  | 1.00 | sideline_left | 136.8 cm | 1 | unconfirmed by samsung, nothing |
| 1809.76 | UNCERTAIN |  | 0.96 | sideline_left | 15.3 cm | 1 | unconfirmed by samsung, iphone17 |
| 1809.06 | UNCERTAIN |  | 0.71 | sideline_right | 3.8 cm | 1 |  |
| 1809.27 | – |  | – |  | – | 1 | secondary bounce |
| 1811.25 | IN |  | 0.00 | sideline_left | -75.1 cm | 1 |  |
| 1813.67 | UNCERTAIN |  | 1.00 | baseline_A | 68.8 cm | 1 | unconfirmed by samsung, iphone17 |
| 1824.88 | IN |  | 0.00 | sideline_left | -149.9 cm | 2 |  |
| 1826.68 | IN |  | 0.00 | centreline_A | -127.8 cm | 1 |  |
| 1828.01 | IN |  | 0.00 | kitchen_B | -222.7 cm | 2 |  |
| 1829.07 | UNCERTAIN |  | 0.06 | kitchen_B | -19.1 cm | 1 |  |
| 1829.61 | – |  | – |  | – | 1 | secondary bounce |
| 1832.27 | IN |  | 0.00 | sideline_left | -95.0 cm | 3 |  |
| 1840.52 | UNCERTAIN |  | 1.00 | baseline_B | 72.0 cm | 1 |  |
| 1847.07 | IN |  | 0.00 | centreline_A | -197.2 cm | 2 |  |
| 1848.79 | IN |  | 0.00 | centreline_B | -155.7 cm | 1 |  |
| 1852.05 | IN |  | 0.00 | centreline_A | -200.9 cm | 1 |  |
| 1853.07 | IN |  | 0.00 | kitchen_B | -67.7 cm | 1 |  |
| 1856.47 | IN |  | 0.00 | kitchen_B | -149.1 cm | 1 |  |
| 1857.31 | IN |  | 0.00 | sideline_right | -73.0 cm | 1 |  |
| 1858.12 | IN |  | 0.00 | baseline_B | -43.9 cm | 1 |  |
| 1858.56 | – |  | – |  | – | 2 | secondary bounce |
| 1859.41 | – |  | – |  | – | 1 | secondary bounce |
| 1860.24 | – |  | – |  | – | 1 | secondary bounce |
| 1863.92 | IN |  | 0.00 | kitchen_A | -125.4 cm | 1 |  |
| 1864.30 | – |  | – |  | – | 1 | secondary bounce |
| 1865.36 | IN |  | 0.00 | centreline_B | -215.8 cm | 2 |  |
| 1866.42 | IN |  | 0.00 | sideline_left | -24.8 cm | 2 |  |
| 1878.61 | UNCERTAIN |  | 1.00 | baseline_A | 214.3 cm | 1 |  |
| 1879.60 | IN |  | 0.00 | sideline_left | -122.8 cm | 2 |  |
| 1881.66 | UNCERTAIN |  | 1.00 | baseline_B | 87.7 cm | 2 |  |
| 1882.05 | – |  | – |  | – | 1 | secondary bounce |
| 1885.83 | IN |  | 0.00 | centreline_A | -200.8 cm | 1 |  |
| 1887.54 | IN |  | 0.00 | centreline_B | -165.7 cm | 2 |  |
| 1889.77 | UNCERTAIN |  | 1.00 | sideline_left | 105.1 cm | 2 |  |
| 1893.21 | UNCERTAIN |  | 1.00 | baseline_B | 323.3 cm | 1 |  |
| 1895.12 | UNCERTAIN |  | 1.00 | baseline_B | 218.7 cm | 1 |  |
| 1896.79 | UNCERTAIN |  | 1.00 | baseline_B | 144.2 cm | 1 |  |
| 1897.62 | UNCERTAIN |  | 1.00 | baseline_B | 137.6 cm | 1 |  |
| 1900.76 | IN |  | 0.00 | centreline_A | -193.6 cm | 1 |  |
| 1902.34 | IN |  | 0.00 | centreline_B | -129.3 cm | 2 |  |
| 1903.26 | IN |  | 0.00 | kitchen_B | -198.1 cm | 1 |  |
| 1904.59 | IN |  | 0.00 | kitchen_B | -77.1 cm | 2 |  |
| 1905.33 | – |  | – |  | – | 2 | secondary bounce |
| 1909.99 | UNCERTAIN |  | 0.36 | sideline_right | -11.3 cm | 1 |  |
| 1912.71 | UNCERTAIN |  | 0.52 | baseline_A | 2.6 cm | 1 |  |
| 1915.55 | IN |  | 0.00 | centreline_B | -274.0 cm | 2 |  |
| 1917.24 | IN |  | 0.00 | centreline_A | -116.2 cm | 1 |  |
| 1938.05 | UNCERTAIN |  | 1.00 | baseline_A | 91.4 cm | 1 |  |
| 1938.97 | – |  | – |  | – | 2 | secondary bounce |
| 1942.38 | IN |  | 0.00 | centreline_B | -166.8 cm | 2 |  |
| 1944.11 | IN |  | 0.00 | centreline_A | -257.0 cm | 2 |  |
| 1945.76 | IN |  | 0.00 | centreline_A | -245.9 cm | 1 |  |
| 1946.22 | – |  | – |  | – | 1 | secondary bounce |
| 1946.54 | – |  | – |  | – | 1 | secondary bounce |
| 1946.78 | – |  | – |  | – | 1 | secondary bounce |
| 1946.97 | – |  | – |  | – | 1 | secondary bounce |
| 1947.10 | – |  | – |  | – | 1 | secondary bounce |
| 1947.25 | – |  | – |  | – | 1 | secondary bounce |
| 1949.55 | IN |  | 0.00 | sideline_right | -50.5 cm | 1 |  |
| 1953.41 | IN |  | 0.00 | baseline_B | -81.3 cm | 2 |  |
| 1955.19 | IN |  | 0.00 | sideline_right | -65.7 cm | 2 |  |
| 1957.05 | IN |  | 0.00 | kitchen_A | -117.9 cm | 1 |  |
| 1958.34 | IN |  | 0.00 | kitchen_A | -142.6 cm | 1 |  |
| 1959.37 | – |  | – |  | – | 1 | secondary bounce |
| 1981.62 | IN |  | 0.00 | centreline_B | -232.8 cm | 2 |  |
| 1983.23 | IN |  | 0.00 | sideline_left | -79.8 cm | 2 |  |
| 1986.08 | IN |  | 0.00 | sideline_right | -62.2 cm | 2 |  |
| 1986.52 | – |  | – |  | – | 1 | secondary bounce |
| 1995.92 | IN |  | 0.00 | sideline_left | -103.5 cm | 2 |  |
| 1997.66 | IN |  | 0.00 | centreline_A | -208.3 cm | 2 |  |
| 2000.00 | IN |  | 0.00 | centreline_A | -227.9 cm | 2 |  |
| 2001.43 | IN |  | 0.00 | kitchen_B | -104.2 cm | 1 |  |
| 2001.72 | IN |  | 0.00 | kitchen_A | -66.5 cm | 1 |  |
| 2002.23 | – |  | – |  | – | 1 | secondary bounce |
| 2002.02 | IN |  | 0.00 | kitchen_A | -136.4 cm | 1 |  |
| 2002.42 | – |  | – |  | – | 1 | secondary bounce |
| 2005.69 | IN |  | 0.00 | sideline_left | -99.7 cm | 2 |  |
| 2006.50 | – |  | – |  | – | 2 | secondary bounce |
| 2010.00 | IN |  | 0.00 | centreline_A | -232.5 cm | 2 |  |
| 2010.20 | – |  | – |  | – | 1 | secondary bounce |
| 2011.51 | UNCERTAIN |  | 0.86 | sideline_left | 11.0 cm | 2 |  |
| 2013.38 | IN |  | 0.00 | centreline_B | -285.4 cm | 2 |  |
| 2013.96 | – |  | – |  | – | 1 | secondary bounce |
| 2016.33 | IN |  | 0.00 | kitchen_B | -140.0 cm | 2 |  |
| 2016.81 | – |  | – |  | – | 2 | secondary bounce |
| 2018.99 | IN |  | 0.00 | kitchen_B | -188.9 cm | 2 |  |
| 2020.35 | IN |  | 0.00 | kitchen_A | -235.7 cm | 2 |  |
| 2021.52 | IN |  | 0.00 | kitchen_B | -200.2 cm | 1 |  |
| 2021.87 | – |  | – |  | – | 1 | secondary bounce |
| 2023.82 | UNCERTAIN |  | 0.29 | kitchen_B | -188.2 cm | 2 |  |
| 2024.37 | UNCERTAIN |  | 0.16 | kitchen_A | -48.1 cm | 2 |  |
| 2025.01 | IN |  | 0.02 | sideline_right | -16.0 cm | 1 |  |
| 2025.65 | UNCERTAIN |  | 0.30 | sideline_right | -4.0 cm | 1 |  |
| 2026.39 | IN |  | 0.00 | sideline_right | -21.3 cm | 1 |  |
| 2030.97 | OUT | **OUT** | 0.96 | baseline_B | 23.9 cm | 2 |  |
| 2042.86 | IN |  | 0.00 | centreline_B | -206.2 cm | 1 |  |
| 2043.96 | – |  | – |  | – | 1 | secondary bounce |
| 2053.08 | IN |  | 0.00 | sideline_left | -117.3 cm | 1 |  |
| 2053.97 | – |  | – |  | – | 1 | secondary bounce |
| 2053.46 | IN |  | 0.00 | baseline_A | -19.0 cm | 1 |  |
| 2056.23 | UNCERTAIN |  | 1.00 | baseline_B | 292.1 cm | 1 |  |
| 2056.65 | – |  | – |  | – | 1 | secondary bounce |
| 2060.87 | IN |  | 0.00 | centreline_A | -225.9 cm | 1 |  |
| 2062.26 | IN |  | 0.00 | centreline_B | -220.2 cm | 2 |  |
| 2063.76 | OUT | **OUT** | 1.00 | sideline_right | 62.4 cm | 1 |  |
| 2065.59 | UNCERTAIN |  | 1.00 | sideline_right | 166.0 cm | 1 |  |
| 2065.79 | – |  | – |  | – | 1 | secondary bounce |
| 2065.97 | – |  | – |  | – | 1 | secondary bounce |
| 2075.47 | IN |  | 0.00 | centreline_B | -155.0 cm | 2 |  |
| 2076.84 | IN |  | 0.00 | centreline_A | -206.7 cm | 2 |  |
| 2079.17 | IN |  | 0.00 | kitchen_A | -183.7 cm | 2 |  |
| 2081.17 | UNCERTAIN |  | 0.96 | baseline_A | 71.6 cm | 1 |  |
| 2082.01 | IN |  | 0.01 | kitchen_A | -49.4 cm | 1 |  |
| 2082.85 | – |  | – |  | – | 2 | secondary bounce |
| 2084.36 | IN |  | 0.05 | sideline_left | -12.1 cm | 1 |  |
| 2085.16 | – |  | – |  | – | 1 | secondary bounce |
| 2085.71 | – |  | – |  | – | 1 | secondary bounce |
| 2086.11 | IN |  | 0.01 | sideline_left | -20.7 cm | 1 |  |
| 2098.76 | IN |  | 0.04 | baseline_A | -87.7 cm | 1 |  |
| 2099.56 | – |  | – |  | – | 2 | secondary bounce |
| 2102.93 | IN |  | 0.00 | centreline_B | -156.3 cm | 2 |  |
| 2104.67 | IN |  | 0.00 | sideline_right | -47.4 cm | 2 |  |
| 2106.02 | UNCERTAIN |  | 0.78 | baseline_B | 14.4 cm | 2 |  |
| 2106.89 | – |  | – |  | – | 1 | secondary bounce |
| 2121.52 | UNCERTAIN |  | 1.00 | baseline_B | 109.2 cm | 2 |  |
| 2123.17 | UNCERTAIN |  | 1.00 | baseline_B | 48.6 cm | 2 |  |
| 2123.59 | – |  | – |  | – | 2 | secondary bounce |
| 2124.01 | UNCERTAIN |  | 1.00 | baseline_B | 48.6 cm | 2 |  |
| 2124.40 | – |  | – |  | – | 1 | secondary bounce |
| 2124.80 | – |  | – |  | – | 2 | secondary bounce |
| 2127.35 | UNCERTAIN |  | 1.00 | baseline_B | 81.5 cm | 1 |  |
| 2127.76 | UNCERTAIN |  | 1.00 | baseline_B | 64.6 cm | 2 |  |
| 2128.18 | – |  | – |  | – | 1 | secondary bounce |
| 2131.51 | IN |  | 0.00 | centreline_A | -179.2 cm | 2 |  |
| 2132.93 | IN |  | 0.00 | centreline_B | -262.2 cm | 2 |  |
| 2134.41 | UNCERTAIN |  | 0.98 | baseline_A | 129.2 cm | 1 |  |
| 2134.67 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2135.69 | UNCERTAIN |  | 0.07 | kitchen_B | -26.1 cm | 2 |  |
| 2136.53 | IN |  | 0.00 | kitchen_A | -67.9 cm | 2 |  |
| 2137.05 | – |  | – |  | – | 1 | secondary bounce |
| 2139.95 | IN |  | 0.00 | kitchen_B | -221.3 cm | 1 |  |
| 2157.16 | UNCERTAIN |  | 1.00 | baseline_B | 133.9 cm | 2 |  |
| 2162.39 | IN |  | 0.00 | sideline_left | -26.0 cm | 2 |  |
| 2164.14 | IN |  | 0.00 | centreline_B | -174.0 cm | 1 |  |
| 2166.61 | IN |  | 0.00 | kitchen_B | -199.6 cm | 1 |  |
| 2168.02 | IN |  | 0.00 | kitchen_A | -152.0 cm | 3 |  |
| 2169.72 | IN |  | 0.00 | kitchen_A | -164.7 cm | 2 |  |
| 2170.97 | IN |  | 0.00 | kitchen_B | -47.9 cm | 1 |  |
| 2172.13 | UNCERTAIN |  | 1.00 | sideline_left | 56.9 cm | 1 | unconfirmed by samsung, nothing |
| 2172.74 | – |  | – |  | – | 2 | secondary bounce |
| 2173.18 | – |  | – |  | – | 1 | secondary bounce |
| 2181.93 | IN |  | 0.00 | kitchen_B | -135.5 cm | 2 |  |
| 2185.96 | IN |  | 0.00 | centreline_A | -222.3 cm | 2 |  |
| 2187.67 | IN |  | 0.00 | baseline_B | -79.8 cm | 1 |  |
| 2188.84 | OUT | **OUT** | 1.00 | sideline_left | 101.1 cm | 2 |  |
| 2199.90 | UNCERTAIN |  | 1.00 | baseline_A | 66.6 cm | 1 |  |
| 2202.99 | IN |  | 0.00 | sideline_left | -119.3 cm | 2 |  |
| 2204.68 | IN |  | 0.00 | centreline_A | -89.6 cm | 1 |  |
| 2206.29 | IN |  | 0.00 | kitchen_A | -153.8 cm | 1 |  |
| 2207.99 | IN |  | 0.00 | centreline_A | -236.5 cm | 1 |  |
| 2213.82 | UNCERTAIN |  | 1.00 | baseline_A | 104.3 cm | 1 |  |
| 2214.27 | UNCERTAIN |  | 1.00 | baseline_A | 75.5 cm | 1 | unconfirmed by samsung |
| 2213.82 | UNCERTAIN |  | 1.00 | baseline_A | 101.3 cm | 1 |  |
| 2217.01 | UNCERTAIN |  | 0.20 | baseline_A | -46.7 cm | 1 |  |
| 2217.00 | UNCERTAIN |  | 1.00 | baseline_A | 115.2 cm | 1 |  |
| 2220.52 | IN |  | 0.03 | sideline_right | -16.2 cm | 2 |  |
| 2222.05 | IN |  | 0.00 | kitchen_A | -228.0 cm | 1 |  |
| 2222.04 | IN |  | 0.00 | centreline_A | -280.9 cm | 1 |  |
| 2223.61 | IN |  | 0.00 | centreline_A | -243.7 cm | 1 |  |
| 2224.99 | UNCERTAIN |  | 1.00 | baseline_A | 169.7 cm | 1 |  |
| 2228.65 | IN |  | 0.00 | centreline_A | -133.3 cm | 3 |  |
| 2230.00 | UNCERTAIN |  | 0.12 | centreline_B | -22.1 cm | 2 |  |
| 2239.83 | IN |  | 0.00 | kitchen_A | -169.5 cm | 2 |  |
| 2241.59 | IN |  | 0.00 | sideline_left | -55.8 cm | 2 |  |
| 2243.09 | IN |  | 0.00 | centreline_B | -256.6 cm | 2 |  |
| 2244.60 | IN |  | 0.00 | kitchen_B | -255.4 cm | 2 |  |
| 2246.59 | IN |  | 0.00 | kitchen_B | -144.1 cm | 2 |  |
| 2249.46 | UNCERTAIN |  | 1.00 | sideline_right | 34.8 cm | 1 |  |
| 2249.76 | – |  | – |  | – | 1 | secondary bounce |
| 2250.46 | UNCERTAIN |  | 1.00 | sideline_right | 119.1 cm | 1 |  |
| 2250.29 | IN |  | 0.00 | baseline_A | -29.5 cm | 1 |  |
| 2253.46 | IN |  | 0.00 | sideline_right | -52.4 cm | 1 |  |
| 2253.46 | – |  | – |  | – | 1 | secondary bounce |
| 2255.06 | UNCERTAIN |  | 1.00 | baseline_B | 191.8 cm | 1 |  |
| 2255.49 | – |  | – |  | – | 1 | secondary bounce |
| 2255.90 | – |  | – |  | – | 1 | secondary bounce |
| 2259.43 | IN |  | 0.00 | sideline_left | -26.6 cm | 2 |  |
| 2260.95 | UNCERTAIN |  | 1.00 | sideline_left | 31.8 cm | 1 |  |
| 2261.33 | IN |  | 0.00 | baseline_B | -121.7 cm | 1 |  |
| 2263.12 | UNCERTAIN |  | 0.84 | sideline_left | 11.5 cm | 2 |  |
| 2265.20 | IN |  | 0.00 | baseline_B | -58.6 cm | 2 |  |
| 2272.41 | IN |  | 0.00 | sideline_right | -70.0 cm | 2 |  |
| 2274.01 | UNCERTAIN |  | 1.00 | baseline_B | 74.2 cm | 1 |  |
| 2276.58 | IN |  | 0.00 | sideline_right | -122.2 cm | 1 |  |
| 2277.49 | IN |  | 0.00 | kitchen_B | -194.2 cm | 1 |  |
| 2285.07 | IN |  | 0.00 | baseline_A | -53.7 cm | 1 |  |
| 2290.72 | IN |  | 0.00 | centreline_B | -119.8 cm | 1 |  |
| 2292.27 | IN |  | 0.00 | baseline_A | -14.9 cm | 1 |  |
| 2294.02 | IN |  | 0.00 | kitchen_A | -153.4 cm | 1 |  |
| 2296.14 | UNCERTAIN |  | 0.07 | sideline_left | -10.3 cm | 1 |  |
| 2296.38 | – |  | – |  | – | 1 | secondary bounce |
| 2296.77 | – |  | – |  | – | 1 | secondary bounce |
| 2305.67 | UNCERTAIN |  | 1.00 | baseline_A | 108.8 cm | 1 |  |
| 2306.48 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2310.83 | IN |  | 0.00 | centreline_B | -160.0 cm | 1 |  |
| 2312.56 | IN |  | 0.00 | centreline_A | -154.1 cm | 2 |  |
| 2315.25 | IN |  | 0.04 | sideline_right | -19.4 cm | 1 |  |
| 2315.48 | – |  | – |  | – | 1 | secondary bounce |
| 2315.77 | – |  | – |  | – | 1 | secondary bounce |
| 2320.24 | IN |  | 0.00 | baseline_B | -57.4 cm | 2 |  |
| 2321.97 | UNCERTAIN |  | 1.00 | baseline_B | 173.4 cm | 1 |  |
| 2323.10 | UNCERTAIN |  | 1.00 | baseline_B | 150.5 cm | 1 |  |
| 2324.72 | UNCERTAIN |  | 1.00 | baseline_B | 74.1 cm | 1 |  |
| 2328.24 | IN |  | 0.00 | sideline_right | -40.2 cm | 2 |  |
| 2329.81 | IN |  | 0.00 | sideline_right | -28.8 cm | 1 |  |
| 2330.96 | IN |  | 0.00 | centreline_A | -263.7 cm | 1 |  |
| 2340.52 | UNCERTAIN |  | 0.40 | baseline_A | -12.8 cm | 1 |  |
| 2342.10 | IN |  | 0.00 | centreline_B | -194.3 cm | 2 |  |
| 2343.59 | UNCERTAIN |  | 1.00 | baseline_B | 66.5 cm | 2 |  |
| 2345.78 | UNCERTAIN |  | 1.00 | baseline_B | 127.7 cm | 1 |  |
| 2346.91 | UNCERTAIN |  | 1.00 | baseline_B | 36.8 cm | 1 | unconfirmed by iphone17 |
| 2348.48 | IN |  | 0.00 | kitchen_A | -138.2 cm | 2 |  |
| 2348.85 | IN |  | 0.00 | kitchen_A | -117.9 cm | 1 |  |
| 2350.14 | IN |  | 0.00 | centreline_B | -181.4 cm | 2 |  |
| 2351.80 | IN |  | 0.00 | kitchen_A | -75.9 cm | 2 |  |
| 2353.99 | IN |  | 0.00 | centreline_B | -231.9 cm | 2 |  |
| 2354.55 | – |  | – |  | – | 1 | secondary bounce |
| 2356.96 | UNCERTAIN |  | 1.00 | baseline_B | 163.1 cm | 2 |  |
| 2357.36 | – |  | – |  | – | 1 | secondary bounce |
| 2357.80 | UNCERTAIN |  | 1.00 | baseline_B | 283.8 cm | 1 |  |
| 2361.30 | IN |  | 0.00 | centreline_A | -253.1 cm | 1 |  |
| 2363.05 | IN |  | 0.00 | centreline_B | -83.6 cm | 2 |  |
| 2365.16 | IN |  | 0.00 | sideline_right | -34.3 cm | 2 |  |
| 2367.02 | IN |  | 0.00 | centreline_B | -257.7 cm | 2 |  |
| 2367.30 | – |  | – |  | – | 1 | secondary bounce |
| 2368.26 | IN |  | 0.05 | sideline_left | -43.9 cm | 1 |  |
| 2368.93 | UNCERTAIN |  | 0.43 | sideline_left | -1.1 cm | 1 |  |
| 2369.25 | UNCERTAIN |  | 0.09 | kitchen_A | -32.3 cm | 1 |  |
| 2369.44 | – |  | – |  | – | 2 | secondary bounce |
| 2372.40 | UNCERTAIN |  | 1.00 | baseline_B | 167.3 cm | 1 |  |
| 2375.83 | UNCERTAIN |  | 1.00 | baseline_B | 311.2 cm | 1 |  |
| 2381.10 | UNCERTAIN |  | 1.00 | baseline_B | 139.2 cm | 1 |  |
| 2389.94 | UNCERTAIN |  | 1.00 | baseline_B | 105.4 cm | 1 |  |
| 2392.58 | UNCERTAIN |  | 1.00 | baseline_B | 136.7 cm | 1 |  |
| 2395.70 | IN |  | 0.00 | kitchen_A | -215.5 cm | 2 |  |
| 2397.77 | UNCERTAIN |  | 0.98 | baseline_B | 43.4 cm | 1 |  |
| 2400.91 | IN |  | 0.00 | kitchen_B | -133.2 cm | 2 |  |
| 2403.33 | IN |  | 0.00 | centreline_B | -205.6 cm | 1 |  |
| 2405.46 | OUT | **OUT** | 1.00 | baseline_B | 57.5 cm | 2 |  |
| 2406.54 | IN |  | 0.00 | kitchen_A | -219.5 cm | 1 |  |
| 2410.23 | UNCERTAIN |  | 1.00 | baseline_B | 249.0 cm | 1 |  |
| 2411.40 | UNCERTAIN |  | 1.00 | baseline_B | 119.0 cm | 2 |  |
| 2411.79 | – |  | – |  | – | 1 | secondary bounce |
| 2412.55 | UNCERTAIN |  | 1.00 | baseline_B | 114.9 cm | 1 | unconfirmed by iphone17, nothing |
| 2415.51 | UNCERTAIN |  | 1.00 | baseline_B | 243.1 cm | 1 |  |
| 2416.26 | UNCERTAIN |  | 1.00 | baseline_B | 118.3 cm | 2 |  |
| 2416.96 | – |  | – |  | – | 1 | secondary bounce |
| 2421.39 | IN |  | 0.00 | sideline_right | -20.2 cm | 2 |  |
| 2423.12 | UNCERTAIN |  | 1.00 | baseline_B | 69.6 cm | 1 |  |
| 2426.29 | UNCERTAIN |  | 0.90 | sideline_right | 3.5 cm | 1 |  |
| 2437.81 | IN |  | 0.00 | centreline_A | -171.7 cm | 2 |  |
| 2439.62 | UNCERTAIN |  | 0.10 | centreline_B | -26.0 cm | 1 |  |
| 2441.36 | IN |  | 0.00 | kitchen_A | -92.6 cm | 1 |  |
| 2442.52 | IN |  | 0.00 | kitchen_B | -210.8 cm | 2 |  |
| 2443.88 | IN |  | 0.00 | kitchen_A | -82.0 cm | 1 |  |
| 2445.82 | UNCERTAIN |  | 1.00 | baseline_B | 316.7 cm | 1 |  |
| 2447.44 | IN |  | 0.00 | sideline_right | -29.3 cm | 2 |  |
| 2447.91 | UNCERTAIN |  | 0.28 | sideline_right | -3.9 cm | 1 |  |
| 2448.15 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2453.90 | UNCERTAIN |  | 1.00 | baseline_B | 241.1 cm | 1 |  |
| 2454.12 | UNCERTAIN |  | 1.00 | baseline_B | 125.5 cm | 1 |  |
| 2457.26 | UNCERTAIN |  | 1.00 | baseline_B | 293.3 cm | 1 |  |
| 2462.60 | IN |  | 0.00 | centreline_A | -131.1 cm | 2 |  |
| 2464.23 | IN |  | 0.00 | centreline_B | -147.0 cm | 1 |  |
| 2465.33 | IN |  | 0.00 | centreline_A | -172.6 cm | 2 |  |
| 2475.57 | UNCERTAIN |  | 1.00 | baseline_A | 62.6 cm | 1 | unconfirmed by samsung, nothing |
| 2486.93 | UNCERTAIN |  | 0.44 | sideline_left | -4.5 cm | 1 |  |
| 2487.36 | UNCERTAIN |  | 0.45 | sideline_left | -2.9 cm | 1 |  |
| 2487.71 | – |  | – |  | – | 1 | secondary bounce |
| 2502.72 | OUT | **OUT** | 1.00 | sideline_right | 43.5 cm | 1 |  |
| 2502.93 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2503.76 | IN |  | 0.00 | sideline_right | -50.9 cm | 1 |  |
| 2504.47 | UNCERTAIN |  | 0.16 | sideline_right | -19.6 cm | 1 |  |
| 2504.87 | – |  | – |  | – | 1 | secondary bounce |
| 2505.26 | – |  | – |  | – | 1 | secondary bounce |
| 2506.88 | IN |  | 0.00 | kitchen_B | -197.8 cm | 1 |  |
| 2507.37 | – |  | – |  | – | 1 | secondary bounce |
| 2507.98 | – |  | – |  | – | 1 | secondary bounce |
| 2510.49 | UNCERTAIN |  | 1.00 | baseline_B | 122.4 cm | 1 |  |
| 2512.15 | UNCERTAIN |  | 0.21 | sideline_left | -20.0 cm | 1 |  |
| 2515.79 | IN |  | 0.00 | baseline_A | -26.2 cm | 1 |  |
| 2520.61 | IN |  | 0.00 | sideline_right | -106.7 cm | 1 |  |
| 2531.17 | IN |  | 0.01 | sideline_right | -68.1 cm | 1 |  |
| 2531.34 | IN |  | 0.00 | baseline_A | -85.9 cm | 1 |  |
| 2531.59 | – |  | – |  | – | 2 | secondary bounce |
| 2532.41 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2532.82 | – |  | – |  | – | 1 | secondary bounce |
| 2533.24 | – |  | – |  | – | 1 | secondary bounce |
| 2534.31 | – |  | – |  | – | 1 | secondary bounce |
| 2534.68 | – |  | – |  | – | 1 | secondary bounce |
| 2539.17 | UNCERTAIN |  | 0.46 | baseline_B | -2.5 cm | 2 |  |
| 2540.81 | IN |  | 0.00 | sideline_right | -87.6 cm | 2 |  |
| 2542.39 | IN |  | 0.00 | centreline_A | -238.6 cm | 1 |  |
| 2544.23 | IN |  | 0.00 | sideline_left | -42.7 cm | 1 |  |
| 2544.58 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2548.12 | IN |  | 0.00 | centreline_B | -119.8 cm | 1 |  |
| 2552.78 | IN |  | 0.00 | centreline_A | -211.6 cm | 2 |  |
| 2554.55 | IN |  | 0.00 | centreline_B | -199.3 cm | 2 |  |
| 2558.91 | IN |  | 0.00 | centreline_B | -298.5 cm | 1 |  |
| 2559.15 | – |  | – |  | – | 1 | secondary bounce |
| 2560.71 | IN |  | 0.00 | centreline_B | -137.7 cm | 1 |  |
| 2565.25 | IN |  | 0.00 | centreline_A | -151.4 cm | 2 |  |
| 2567.26 | IN |  | 0.00 | baseline_B | -115.0 cm | 1 |  |
| 2569.10 | IN |  | 0.00 | baseline_B | -56.5 cm | 1 |  |
| 2571.71 | IN |  | 0.00 | centreline_A | -196.4 cm | 2 |  |
| 2572.66 | – |  | – |  | – | 1 | secondary bounce |
| 2573.35 | IN |  | 0.03 | sideline_right | -14.5 cm | 1 |  |
| 2573.86 | IN |  | 0.00 | kitchen_A | -34.6 cm | 1 |  |
| 2574.52 | – |  | – |  | – | 2 | secondary bounce |
| 2577.94 | UNCERTAIN |  | 0.97 | baseline_B | 29.5 cm | 2 |  |
| 2578.55 | – |  | – |  | – | 1 | secondary bounce |
| 2579.30 | – |  | – |  | – | 1 | secondary bounce |
| 2581.54 | UNCERTAIN |  | 1.00 | baseline_B | 233.6 cm | 1 |  |
| 2587.53 | IN |  | 0.00 | centreline_A | -223.3 cm | 1 |  |
| 2589.09 | IN |  | 0.00 | centreline_B | -239.2 cm | 2 |  |
| 2590.50 | IN |  | 0.00 | centreline_B | -252.3 cm | 1 |  |
| 2592.16 | UNCERTAIN |  | 1.00 | sideline_right | 92.1 cm | 1 | unconfirmed by iphone17 |
| 2593.03 | – |  | – |  | – | 1 | secondary bounce |
| 2593.64 | UNCERTAIN |  | 0.22 | sideline_right | -3.7 cm | 1 |  |
| 2594.39 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2599.33 | IN |  | 0.00 | baseline_A | -77.3 cm | 1 |  |
| 2601.02 | UNCERTAIN |  | 0.06 | sideline_right | -12.9 cm | 1 |  |
| 2604.47 | UNCERTAIN |  | 0.59 | baseline_B | 4.1 cm | 2 |  |
| 2605.70 | IN |  | 0.00 | kitchen_A | -240.3 cm | 2 |  |
| 2607.21 | IN |  | 0.00 | kitchen_B | -190.4 cm | 2 |  |
| 2607.63 | – |  | – |  | – | 1 | secondary bounce |
| 2608.48 | IN |  | 0.00 | kitchen_A | -167.3 cm | 3 |  |
| 2609.85 | IN |  | 0.00 | kitchen_B | -210.8 cm | 2 |  |
| 2610.93 | UNCERTAIN |  | 0.94 | sideline_left | 40.0 cm | 1 |  |
| 2611.77 | UNCERTAIN |  | 0.20 | sideline_left | -10.4 cm | 2 |  |
| 2613.31 | UNCERTAIN |  | 0.93 | sideline_left | 31.6 cm | 1 |  |
| 2614.14 | UNCERTAIN |  | 0.74 | sideline_left | 13.3 cm | 1 |  |
| 2618.30 | IN |  | 0.00 | centreline_A | -207.3 cm | 1 |  |
| 2618.74 | – |  | – |  | – | 1 | secondary bounce |
| 2619.16 | – |  | – |  | – | 1 | secondary bounce |
| 2619.52 | – |  | – |  | – | 1 | secondary bounce |
| 2619.90 | – |  | – |  | – | 2 | secondary bounce |
| 2620.29 | IN |  | 0.00 | centreline_A | -178.7 cm | 1 |  |
| 2620.67 | – |  | – |  | – | 1 | secondary bounce |
| 2624.28 | UNCERTAIN |  | 1.00 | sideline_left | 358.3 cm | 1 |  |
| 2625.90 | IN |  | 0.00 | sideline_right | -66.9 cm | 2 |  |
| 2627.62 | IN |  | 0.00 | centreline_A | -242.9 cm | 1 |  |
| 2628.75 | UNCERTAIN |  | 0.19 | kitchen_B | -7.1 cm | 1 |  |
| 2629.22 | IN |  | 0.00 | kitchen_A | -41.5 cm | 1 |  |
| 2630.17 | IN |  | 0.04 | kitchen_A | -40.3 cm | 1 |  |
| 2630.31 | – |  | – |  | – | 1 | secondary bounce |
| 2633.46 | IN |  | 0.00 | sideline_right | -48.8 cm | 1 |  |
| 2639.04 | IN |  | 0.00 | centreline_B | -242.7 cm | 2 |  |
| 2639.46 | IN |  | 0.00 | baseline_A | -41.6 cm | 1 |  |
| 2639.99 | IN |  | 0.00 | centreline_B | -192.1 cm | 2 |  |
| 2640.39 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2640.52 | – |  | – |  | – | 1 | secondary bounce |
| 2641.07 | – |  | – |  | – | 1 | secondary bounce |
| 2641.25 | – |  | – |  | – | 1 | secondary bounce |
| 2673.22 | IN |  | 0.00 | baseline_A | -64.5 cm | 2 |  |
| 2674.79 | IN |  | 0.00 | centreline_B | -262.2 cm | 2 |  |
| 2676.01 | OUT | **OUT** | 1.00 | sideline_right | 59.2 cm | 1 |  |
| 2683.38 | IN |  | 0.00 | centreline_B | -175.6 cm | 2 |  |
| 2689.06 | IN |  | 0.00 | centreline_A | -199.6 cm | 2 |  |
| 2690.61 | IN |  | 0.00 | centreline_B | -191.0 cm | 2 |  |
| 2692.36 | IN |  | 0.00 | kitchen_B | -69.7 cm | 2 |  |
| 2694.00 | IN |  | 0.00 | centreline_B | -286.4 cm | 2 |  |
| 2701.35 | IN |  | 0.04 | sideline_right | -19.9 cm | 1 |  |
| 2702.03 | – |  | – |  | – | 1 | secondary bounce |
| 2705.11 | IN |  | 0.00 | centreline_B | -175.0 cm | 2 |  |
| 2706.64 | IN |  | 0.00 | centreline_A | -49.0 cm | 2 |  |
| 2706.80 | – |  | – |  | – | 1 | secondary bounce |
| 2708.74 | IN |  | 0.00 | kitchen_A | -170.7 cm | 2 |  |
| 2710.46 | IN |  | 0.00 | kitchen_B | -229.6 cm | 2 |  |
| 2711.81 | IN |  | 0.00 | sideline_right | -37.4 cm | 1 |  |
| 2718.57 | UNCERTAIN |  | 1.00 | baseline_A | 157.5 cm | 1 |  |
| 2719.28 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 2722.25 | IN |  | 0.00 | sideline_right | -42.0 cm | 2 |  |
| 2723.82 | IN |  | 0.00 | sideline_right | -120.3 cm | 2 |  |
| 2730.70 | IN |  | 0.00 | centreline_A | -228.7 cm | 2 |  |
| 2731.70 | – |  | – |  | – | 2 | secondary bounce |
| 2731.93 | IN |  | 0.00 | baseline_A | -133.8 cm | 1 |  |
| 2736.15 | IN |  | 0.00 | sideline_right | -55.9 cm | 1 |  |
| 2736.59 | – |  | – |  | – | 1 | secondary bounce |
| 2739.59 | UNCERTAIN |  | 0.09 | baseline_B | -30.0 cm | 2 |  |
| 2741.63 | UNCERTAIN |  | 1.00 | sideline_right | 51.1 cm | 1 | unconfirmed by nothing |
| 2746.17 | IN |  | 0.00 | baseline_A | -58.6 cm | 1 |  |
| 2750.27 | IN |  | 0.00 | baseline_B | -123.9 cm | 2 |  |
| 2751.85 | IN |  | 0.00 | centreline_A | -172.3 cm | 2 |  |
| 2753.40 | OUT | **OUT** | 1.00 | baseline_B | 65.0 cm | 2 |  |
| 2757.21 | UNCERTAIN |  | 1.00 | baseline_B | 328.1 cm | 1 |  |
| 2761.67 | UNCERTAIN |  | 1.00 | sideline_left | 214.5 cm | 1 |  |
| 2762.76 | IN |  | 0.00 | centreline_A | -290.7 cm | 2 |  |
| 2764.91 | IN |  | 0.00 | sideline_right | -70.7 cm | 2 |  |
| 2771.12 | IN |  | 0.00 | centreline_A | -262.8 cm | 1 |  |
| 2772.94 | UNCERTAIN |  | 1.00 | baseline_B | 68.5 cm | 1 |  |
| 2779.39 | UNCERTAIN |  | 0.62 | sideline_right | 1.1 cm | 3 |  |
| 2780.73 | UNCERTAIN |  | 1.00 | baseline_A | 20.2 cm | 1 | unconfirmed by samsung, nothing |
| 2782.19 | UNCERTAIN |  | 1.00 | baseline_A | 99.4 cm | 2 | cameras disagree (chi2 31) |
| 2786.06 | IN |  | 0.00 | baseline_B | -94.4 cm | 2 |  |
| 2787.80 | IN |  | 0.00 | sideline_right | -55.7 cm | 1 |  |
| 2788.67 | – |  | – |  | – | 2 | secondary bounce |
| 2794.65 | UNCERTAIN |  | 1.00 | baseline_A | 14.3 cm | 1 | unconfirmed by samsung, nothing |
| 2794.98 | IN |  | 0.00 | centreline_B | -141.4 cm | 2 |  |
| 2796.64 | IN |  | 0.00 | baseline_A | -61.9 cm | 1 |  |
| 2800.20 | IN |  | 0.00 | centreline_A | -132.4 cm | 2 |  |
| 2802.87 | IN |  | 0.00 | kitchen_B | -137.1 cm | 1 |  |
| 2802.25 | UNCERTAIN |  | 1.00 | baseline_A | 65.8 cm | 1 | unconfirmed by samsung, nothing |
| 2802.44 | IN |  | 0.00 | kitchen_B | -109.1 cm | 1 |  |
| 2807.37 | IN |  | 0.00 | kitchen_B | -130.2 cm | 1 |  |
| 2807.98 | – |  | – |  | – | 1 | secondary bounce |
| 2808.42 | – |  | – |  | – | 1 | secondary bounce |
| 2809.19 | – |  | – |  | – | 1 | secondary bounce |
| 2812.17 | IN |  | 0.00 | baseline_A | -59.7 cm | 2 |  |
| 2813.46 | UNCERTAIN |  | 1.00 | baseline_A | 85.1 cm | 2 | cameras disagree (chi2 41) |
| 2817.96 | IN |  | 0.00 | sideline_left | -86.5 cm | 2 |  |
| 2819.43 | OUT | **OUT** | 0.97 | sideline_right | 22.9 cm | 2 |  |
| 2821.16 | UNCERTAIN |  | 1.00 | sideline_right | 135.6 cm | 1 |  |
| 2822.20 | – |  | – |  | – | 1 | secondary bounce |
| 2827.16 | UNCERTAIN |  | 1.00 | baseline_A | 84.3 cm | 1 |  |
| 2829.42 | UNCERTAIN |  | 0.96 | baseline_A | 104.6 cm | 1 |  |
| 2830.67 | IN |  | 0.00 | centreline_B | -171.8 cm | 2 |  |
| 2832.00 | IN |  | 0.00 | kitchen_A | -170.2 cm | 3 |  |
| 2833.57 | IN |  | 0.00 | kitchen_B | -135.1 cm | 1 |  |
| 2833.58 | – |  | – |  | – | 1 | secondary bounce |
| 2833.99 | – |  | – |  | – | 1 | secondary bounce |
| 2836.25 | IN |  | 0.00 | centreline_A | -267.1 cm | 1 |  |
| 2836.94 | OUT | **OUT** | 1.00 | sideline_right | 69.0 cm | 2 |  |
| 2842.07 | IN |  | 0.00 | sideline_right | -77.8 cm | 3 |  |
| 2847.59 | IN |  | 0.00 | centreline_B | -200.8 cm | 2 |  |
| 2849.23 | IN |  | 0.00 | kitchen_B | -173.9 cm | 1 |  |
| 2849.57 | – |  | – |  | – | 1 | secondary bounce |
| 2851.54 | IN |  | 0.00 | kitchen_A | -72.5 cm | 1 |  |
| 2852.26 | – |  | – |  | – | 1 | secondary bounce |
| 2855.37 | UNCERTAIN |  | 1.00 | baseline_A | 259.9 cm | 1 |  |
| 2855.70 | IN |  | 0.00 | centreline_A | -170.2 cm | 1 |  |
| 2856.07 | – |  | – |  | – | 1 | secondary bounce |
| 2855.69 | UNCERTAIN |  | 1.00 | baseline_A | 97.5 cm | 1 |  |
| 2859.90 | IN |  | 0.00 | baseline_B | -91.4 cm | 2 |  |
| 2860.24 | UNCERTAIN |  | 1.00 | baseline_A | 73.8 cm | 1 |  |
| 2861.65 | IN |  | 0.00 | centreline_A | -229.7 cm | 1 |  |
| 2867.18 | UNCERTAIN |  | 1.00 | sideline_left | 33.4 cm | 1 | unconfirmed by samsung, nothing |
| 2871.81 | UNCERTAIN |  | 0.08 | baseline_A | -77.6 cm | 1 |  |
| 2877.14 | UNCERTAIN |  | 0.79 | baseline_B | 17.1 cm | 2 |  |
| 2878.71 | IN |  | 0.00 | centreline_A | -241.0 cm | 1 |  |
| 2879.04 | – |  | – |  | – | 1 | secondary bounce |
| 2880.37 | IN |  | 0.00 | kitchen_A | -36.6 cm | 1 |  |
| 2880.25 | IN |  | 0.00 | sideline_left | -126.0 cm | 1 |  |
| 2887.24 | UNCERTAIN |  | 1.00 | baseline_A | 100.5 cm | 1 |  |
| 2889.94 | IN |  | 0.00 | baseline_B | -56.1 cm | 1 |  |
| 2890.71 | – |  | – |  | – | 1 | secondary bounce |
| 2891.55 | UNCERTAIN |  | 0.09 | baseline_A | -4.7 cm | 1 |  |
| 2894.77 | IN |  | 0.00 | sideline_right | -104.1 cm | 2 |  |
| 2895.99 | IN |  | 0.00 | centreline_B | -227.1 cm | 2 |  |
| 2897.43 | IN |  | 0.00 | baseline_A | -49.1 cm | 1 |  |
| 2900.27 | UNCERTAIN |  | 0.06 | centreline_B | -34.0 cm | 2 |  |
| 2902.45 | IN |  | 0.00 | centreline_B | -204.1 cm | 2 |  |
| 2903.86 | IN |  | 0.00 | centreline_B | -274.5 cm | 2 |  |
| 2906.33 | IN |  | 0.00 | kitchen_B | -136.6 cm | 1 |  |
| 2906.99 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2913.15 | IN |  | 0.00 | centreline_B | -115.8 cm | 1 |  |
| 2919.41 | IN |  | 0.00 | centreline_A | -247.0 cm | 1 |  |
| 2921.29 | UNCERTAIN |  | 0.06 | centreline_B | -35.0 cm | 2 |  |
| 2922.91 | IN |  | 0.00 | baseline_A | -83.4 cm | 2 |  |
| 2924.30 | UNCERTAIN |  | 1.00 | baseline_A | 138.8 cm | 1 |  |
| 2924.74 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2929.42 | UNCERTAIN |  | 0.85 | baseline_A | 41.2 cm | 1 |  |
| 2931.16 | IN |  | 0.00 | sideline_left | -68.2 cm | 2 |  |
| 2931.92 | – |  | – |  | – | 1 | secondary bounce |
| 2935.97 | IN |  | 0.00 | kitchen_A | -185.5 cm | 2 |  |
| 2937.81 | IN |  | 0.00 | baseline_B | -55.1 cm | 1 |  |
| 2938.54 | IN |  | 0.00 | centreline_B | -276.5 cm | 1 |  |
| 2938.85 | IN |  | 0.00 | kitchen_B | -57.1 cm | 1 |  |
| 2942.16 | IN |  | 0.00 | sideline_right | -150.8 cm | 3 |  |
| 2942.69 | – |  | – |  | – | 2 | secondary bounce |
| 2943.12 | – |  | – |  | – | 2 | secondary bounce |
| 2943.54 | IN |  | 0.00 | sideline_right | -43.5 cm | 1 |  |
| 2943.96 | – |  | – |  | – | 1 | secondary bounce |
| 2943.96 | – |  | – |  | – | 1 | secondary bounce |
| 2948.25 | UNCERTAIN |  | 0.34 | sideline_left | -5.5 cm | 2 |  |
| 2951.94 | IN |  | 0.00 | kitchen_A | -194.3 cm | 1 |  |
| 2952.89 | – |  | – |  | – | 2 | secondary bounce |
| 2952.89 | IN |  | 0.00 | centreline_A | -241.1 cm | 1 |  |
| 2954.64 | UNCERTAIN |  | 1.00 | baseline_A | 45.3 cm | 2 | cameras disagree (chi2 43) |
| 2959.49 | IN |  | 0.00 | sideline_right | -38.0 cm | 1 |  |
| 2959.50 | – |  | – |  | – | 1 | secondary bounce |
| 2963.57 | IN |  | 0.00 | kitchen_A | -115.9 cm | 1 |  |
| 2963.58 | – |  | – |  | – | 1 | secondary bounce |
| 2964.83 | IN |  | 0.00 | kitchen_A | -69.2 cm | 1 |  |
| 2965.34 | IN |  | 0.00 | sideline_left | -52.0 cm | 1 |  |
| 2964.83 | IN |  | 0.00 | kitchen_A | -185.6 cm | 1 |  |
| 2965.13 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2965.34 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2965.66 | UNCERTAIN |  | 1.00 | sideline_left | 15.9 cm | 1 | unconfirmed by samsung, nothing |
| 2965.94 | – |  | – |  | – | 1 | secondary bounce |
| 2966.66 | – |  | – |  | – | 1 | secondary bounce |
| 2971.07 | IN |  | 0.00 | baseline_A | -81.1 cm | 1 |  |
| 2973.77 | UNCERTAIN |  | 1.00 | baseline_A | 86.7 cm | 1 |  |
| 2977.45 | IN |  | 0.02 | baseline_B | -56.8 cm | 2 |  |
| 2979.03 | IN |  | 0.00 | centreline_A | -272.2 cm | 2 |  |
| 2980.44 | IN |  | 0.00 | centreline_B | -284.6 cm | 1 |  |
| 2981.32 | IN |  | 0.00 | kitchen_B | -141.1 cm | 1 |  |
| 2981.88 | – |  | – |  | – | 1 | secondary bounce |
| 2982.64 | – |  | – |  | – | 1 | secondary bounce |
| 2988.68 | UNCERTAIN |  | 1.00 | baseline_A | 116.7 cm | 1 | unconfirmed by samsung |
| 2989.40 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 2993.12 | UNCERTAIN |  | 0.98 | baseline_B | 40.5 cm | 1 |  |
| 2993.62 | IN |  | 0.00 | baseline_A | -52.8 cm | 1 |  |
| 2994.81 | IN |  | 0.00 | centreline_A | -99.9 cm | 1 |  |
| 2997.21 | IN |  | 0.00 | centreline_A | -264.7 cm | 1 |  |
| 3000.68 | IN |  | 0.00 | kitchen_B | -221.3 cm | 2 |  |
| 3001.87 | IN |  | 0.00 | centreline_A | -215.5 cm | 3 |  |
| 3003.65 | IN |  | 0.00 | kitchen_B | -181.0 cm | 1 |  |
| 3004.84 | IN |  | 0.00 | centreline_A | -242.4 cm | 2 |  |
| 3006.41 | IN |  | 0.00 | sideline_right | -47.1 cm | 2 |  |
| 3019.47 | UNCERTAIN |  | 1.00 | sideline_left | 254.6 cm | 1 |  |
| 3024.38 | UNCERTAIN |  | 1.00 | baseline_A | 301.8 cm | 1 |  |
| 3028.84 | IN |  | 0.00 | kitchen_A | -122.4 cm | 1 |  |
| 3033.00 | UNCERTAIN |  | 1.00 | sideline_left | 137.7 cm | 1 | unconfirmed by samsung, iphone17 |
| 3034.94 | UNCERTAIN |  | 1.00 | baseline_A | 232.0 cm | 1 |  |
| 3038.13 | UNCERTAIN |  | 1.00 | sideline_left | 355.0 cm | 1 |  |
| 3038.59 | UNCERTAIN |  | 1.00 | sideline_left | 386.8 cm | 1 |  |
| 3041.54 | UNCERTAIN |  | 1.00 | baseline_A | 24.1 cm | 1 |  |
| 3042.74 | UNCERTAIN |  | 0.99 | sideline_left | 37.9 cm | 2 | cameras disagree (chi2 103) |
| 3045.52 | IN |  | 0.00 | centreline_A | -170.4 cm | 1 |  |
| 3045.53 | IN |  | 0.00 | centreline_A | -159.2 cm | 1 |  |
| 3060.09 | UNCERTAIN |  | 1.00 | baseline_A | 18.8 cm | 1 | unconfirmed by samsung, nothing |
| 3061.22 | UNCERTAIN |  | 1.00 | sideline_left | 108.5 cm | 2 | cameras disagree (chi2 104) |
| 3062.10 | – |  | – |  | – | 1 | secondary bounce |
| 3065.04 | UNCERTAIN |  | 1.00 | baseline_B | 110.6 cm | 2 |  |
| 3065.77 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3069.16 | UNCERTAIN |  | 1.00 | sideline_right | 48.5 cm | 1 | unconfirmed by nothing |
| 3071.33 | UNCERTAIN |  | 1.00 | sideline_right | 31.1 cm | 2 |  |
| 3072.66 | IN |  | 0.00 | kitchen_B | -111.3 cm | 2 |  |
| 3073.35 | – |  | – |  | – | 1 | secondary bounce |
| 3073.84 | – |  | – |  | – | 1 | secondary bounce |
| 3074.18 | – |  | – |  | – | 1 | secondary bounce |
| 3078.56 | IN |  | 0.00 | centreline_A | -241.3 cm | 1 |  |
| 3080.23 | IN |  | 0.00 | sideline_right | -127.3 cm | 1 |  |
| 3081.87 | IN |  | 0.00 | kitchen_B | -126.7 cm | 2 |  |
| 3082.32 | – |  | – |  | – | 1 | secondary bounce |
| 3083.49 | IN |  | 0.00 | kitchen_B | -175.5 cm | 1 |  |
| 3092.23 | IN |  | 0.00 | sideline_left | -112.1 cm | 2 |  |
| 3093.70 | IN |  | 0.00 | centreline_A | -256.0 cm | 3 |  |
| 3096.69 | OUT | **OUT** | 1.00 | sideline_right | 156.5 cm | 1 |  |
| 3102.56 | IN |  | 0.00 | baseline_A | -60.1 cm | 2 |  |
| 3102.98 | UNCERTAIN |  | 1.00 | sideline_left | 172.1 cm | 1 |  |
| 3104.47 | UNCERTAIN |  | 1.00 | baseline_A | 82.1 cm | 3 | cameras disagree (chi2 51) |
| 3105.19 | – |  | – |  | – | 3 | secondary bounce |
| 3107.15 | UNCERTAIN |  | 1.00 | baseline_A | 57.5 cm | 1 | unconfirmed by samsung, nothing |
| 3108.39 | UNCERTAIN |  | 0.93 | baseline_B | 26.5 cm | 1 |  |
| 3110.07 | IN |  | 0.00 | centreline_A | -159.0 cm | 2 |  |
| 3111.16 | UNCERTAIN |  | 1.00 | baseline_B | 262.8 cm | 1 |  |
| 3111.86 | IN |  | 0.02 | kitchen_A | -47.4 cm | 1 |  |
| 3112.23 | – |  | – |  | – | 1 | secondary bounce |
| 3111.86 | IN |  | 0.00 | kitchen_A | -156.2 cm | 1 |  |
| 3113.20 | IN |  | 0.00 | centreline_B | -111.0 cm | 1 |  |
| 3120.25 | IN |  | 0.00 | sideline_right | -40.0 cm | 1 |  |
| 3120.95 | – |  | – |  | – | 2 | secondary bounce |
| 3124.39 | UNCERTAIN |  | 0.07 | centreline_B | -39.5 cm | 2 |  |
| 3127.10 | IN |  | 0.00 | centreline_A | -183.9 cm | 1 |  |
| 3128.84 | IN |  | 0.00 | centreline_B | -119.6 cm | 1 |  |
| 3133.85 | IN |  | 0.00 | kitchen_A | -138.4 cm | 2 |  |
| 3134.37 | – |  | – |  | – | 1 | secondary bounce |
| 3135.15 | IN |  | 0.00 | sideline_right | -83.0 cm | 2 |  |
| 3136.51 | IN |  | 0.00 | centreline_B | -270.0 cm | 2 |  |
| 3137.87 | IN |  | 0.00 | kitchen_A | -118.8 cm | 1 |  |
| 3141.28 | OUT | **OUT** | 1.00 | sideline_right | 36.3 cm | 2 |  |
| 3148.93 | UNCERTAIN |  | 1.00 | baseline_B | 123.9 cm | 2 |  |
| 3149.74 | – |  | – |  | – | 2 | second bounce (ball not returned) |
| 3150.10 | – |  | – |  | – | 1 | secondary bounce |
| 3155.85 | IN |  | 0.00 | sideline_left | -31.0 cm | 1 |  |
| 3156.72 | – |  | – |  | – | 2 | secondary bounce |
| 3160.77 | OUT | **OUT** | 1.00 | sideline_right | 127.3 cm | 1 |  |
| 3171.65 | UNCERTAIN |  | 1.00 | baseline_B | 293.0 cm | 1 |  |
| 3172.05 | UNCERTAIN |  | 1.00 | baseline_B | 274.7 cm | 1 |  |
| 3174.72 | IN |  | 0.00 | baseline_A | -39.8 cm | 1 |  |
| 3176.31 | IN |  | 0.00 | centreline_A | -235.5 cm | 1 |  |
| 3177.68 | IN |  | 0.00 | centreline_B | -217.1 cm | 2 |  |
| 3178.57 | UNCERTAIN |  | 0.34 | baseline_A | -27.9 cm | 1 |  |
| 3179.56 | IN |  | 0.00 | kitchen_B | -200.5 cm | 1 |  |
| 3180.91 | IN |  | 0.00 | kitchen_B | -172.1 cm | 2 |  |
| 3182.06 | IN |  | 0.00 | sideline_left | -37.5 cm | 1 |  |
| 3184.19 | IN |  | 0.00 | kitchen_A | -175.3 cm | 1 |  |
| 3185.53 | IN |  | 0.00 | kitchen_B | -183.7 cm | 1 |  |
| 3186.64 | IN |  | 0.00 | kitchen_A | -145.4 cm | 2 |  |
| 3187.87 | IN |  | 0.00 | kitchen_B | -105.1 cm | 2 |  |
| 3189.01 | IN |  | 0.00 | kitchen_A | -222.9 cm | 2 |  |
| 3190.12 | IN |  | 0.00 | kitchen_B | -121.4 cm | 2 |  |
| 3191.34 | IN |  | 0.00 | kitchen_A | -72.0 cm | 1 |  |
| 3192.64 | IN |  | 0.00 | sideline_left | -97.5 cm | 1 |  |
| 3193.86 | IN |  | 0.00 | kitchen_A | -188.1 cm | 2 |  |
| 3194.13 | IN |  | 0.00 | kitchen_A | -147.1 cm | 1 |  |
| 3195.01 | IN |  | 0.00 | sideline_right | -27.4 cm | 2 |  |
| 3196.93 | IN |  | 0.00 | centreline_A | -221.3 cm | 2 |  |
| 3203.80 | UNCERTAIN |  | 0.70 | baseline_A | 47.6 cm | 1 |  |
| 3205.71 | IN |  | 0.00 | baseline_A | -12.9 cm | 1 |  |
| 3209.65 | OUT | **OUT** | 1.00 | sideline_right | 187.6 cm | 1 |  |
| 3209.97 | – |  | – |  | – | 1 | secondary bounce |
| 3210.24 | – |  | – |  | – | 1 | secondary bounce |
| 3210.43 | – |  | – |  | – | 1 | secondary bounce |
| 3212.94 | IN |  | 0.00 | baseline_A | -14.5 cm | 1 |  |
| 3213.25 | UNCERTAIN |  | 1.00 | baseline_B | 221.6 cm | 1 |  |
| 3216.38 | IN |  | 0.00 | kitchen_A | -207.8 cm | 1 |  |
| 3216.34 | IN |  | 0.00 | centreline_A | -227.5 cm | 1 |  |
| 3218.00 | IN |  | 0.00 | centreline_B | -204.1 cm | 2 |  |
| 3220.05 | IN |  | 0.00 | centreline_B | -165.6 cm | 2 |  |
| 3222.15 | IN |  | 0.00 | kitchen_B | -137.2 cm | 1 |  |
| 3231.63 | IN |  | 0.00 | centreline_A | -191.8 cm | 2 |  |
| 3233.09 | IN |  | 0.00 | kitchen_B | -179.8 cm | 2 |  |
| 3234.19 | IN |  | 0.00 | sideline_right | -30.8 cm | 2 |  |
| 3234.24 | UNCERTAIN |  | 0.92 | sideline_right | 8.5 cm | 1 |  |
| 3241.53 | UNCERTAIN |  | 0.39 | sideline_right | -2.6 cm | 2 |  |
| 3242.02 | – |  | – |  | – | 1 | secondary bounce |
| 3245.12 | IN |  | 0.00 | baseline_A | -87.6 cm | 1 |  |
| 3246.95 | IN |  | 0.00 | centreline_B | -96.2 cm | 2 |  |
| 3248.86 | IN |  | 0.00 | centreline_B | -245.8 cm | 2 |  |
| 3249.53 | UNCERTAIN |  | 0.99 | sideline_left | 64.3 cm | 1 |  |
| 3251.60 | UNCERTAIN |  | 1.00 | baseline_B | 12.9 cm | 1 | unconfirmed by iphone17, nothing |
| 3255.13 | UNCERTAIN |  | 1.00 | baseline_B | 162.3 cm | 1 |  |
| 3256.05 | – |  | – |  | – | 1 | secondary bounce |
| 3256.63 | – |  | – |  | – | 1 | secondary bounce |
| 3275.57 | IN |  | 0.00 | sideline_left | -73.7 cm | 1 |  |
| 3277.28 | IN |  | 0.00 | centreline_B | -102.9 cm | 2 |  |
| 3278.67 | IN |  | 0.00 | centreline_A | -73.9 cm | 2 |  |
| 3280.23 | UNCERTAIN |  | 0.80 | baseline_A | 39.3 cm | 1 |  |
| 3287.40 | IN |  | 0.01 | baseline_B | -65.8 cm | 2 |  |
| 3287.92 | – |  | – |  | – | 1 | secondary bounce |
| 3288.24 | UNCERTAIN |  | 0.78 | baseline_A | 44.5 cm | 1 |  |
| 3291.47 | IN |  | 0.00 | centreline_A | -15.1 cm | 2 |  |
| 3293.07 | IN |  | 0.00 | kitchen_B | -171.2 cm | 1 |  |
| 3294.52 | IN |  | 0.00 | kitchen_A | -65.8 cm | 3 |  |
| 3296.28 | IN |  | 0.00 | kitchen_A | -182.5 cm | 3 |  |
| 3296.86 | – |  | – |  | – | 1 | secondary bounce |
| 3304.39 | IN |  | 0.02 | sideline_left | -35.7 cm | 2 |  |
| 3305.22 | – |  | – |  | – | 2 | secondary bounce |
| 3308.19 | UNCERTAIN |  | 1.00 | baseline_B | 263.1 cm | 1 |  |
| 3308.85 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3315.24 | UNCERTAIN |  | 0.88 | sideline_left | 5.4 cm | 2 |  |
| 3315.60 | – |  | – |  | – | 1 | secondary bounce |
| 3316.74 | UNCERTAIN |  | 1.00 | sideline_left | 60.4 cm | 1 | unconfirmed by samsung, nothing |
| 3316.98 | IN |  | 0.00 | sideline_left | -79.7 cm | 2 |  |
| 3318.22 | IN |  | 0.00 | baseline_A | -7.1 cm | 1 |  |
| 3337.08 | IN |  | 0.00 | sideline_right | -31.9 cm | 1 |  |
| 3346.20 | IN |  | 0.00 | centreline_A | -272.2 cm | 1 |  |
| 3347.74 | IN |  | 0.00 | sideline_left | -140.1 cm | 2 |  |
| 3349.36 | IN |  | 0.00 | centreline_B | -189.7 cm | 1 |  |
| 3351.18 | IN |  | 0.00 | kitchen_B | -143.1 cm | 2 |  |
| 3351.85 | – |  | – |  | – | 1 | secondary bounce |
| 3353.78 | UNCERTAIN |  | 0.97 | baseline_A | 92.3 cm | 1 |  |
| 3354.69 | UNCERTAIN |  | 1.00 | sideline_right | 114.6 cm | 1 |  |
| 3354.99 | – |  | – |  | – | 1 | secondary bounce |
| 3357.65 | UNCERTAIN |  | 1.00 | baseline_A | 118.2 cm | 2 | cameras disagree (chi2 37) |
| 3358.42 | – |  | – |  | – | 2 | secondary bounce |
| 3362.75 | IN |  | 0.00 | sideline_right | -40.4 cm | 1 |  |
| 3368.86 | IN |  | 0.00 | centreline_B | -113.6 cm | 2 |  |
| 3370.82 | IN |  | 0.00 | centreline_A | -249.7 cm | 1 |  |
| 3372.24 | IN |  | 0.00 | centreline_B | -215.8 cm | 2 |  |
| 3373.73 | IN |  | 0.00 | kitchen_A | -119.2 cm | 1 |  |
| 3374.91 | IN |  | 0.00 | kitchen_B | -230.9 cm | 2 |  |
| 3380.09 | IN |  | 0.00 | baseline_A | -89.4 cm | 1 |  |
| 3380.81 | – |  | – |  | – | 1 | secondary bounce |
| 3383.58 | IN |  | 0.00 | baseline_A | -57.0 cm | 1 |  |
| 3386.49 | IN |  | 0.00 | sideline_right | -52.9 cm | 2 |  |
| 3387.82 | IN |  | 0.00 | kitchen_A | -149.4 cm | 1 |  |
| 3387.82 | – |  | – |  | – | 1 | secondary bounce |
| 3389.63 | UNCERTAIN |  | 0.22 | centreline_A | -57.8 cm | 1 |  |
| 3389.45 | IN |  | 0.00 | kitchen_B | -195.0 cm | 1 |  |
| 3390.78 | IN |  | 0.00 | centreline_A | -225.2 cm | 2 |  |
| 3391.45 | – |  | – |  | – | 3 | second bounce (ball not returned) |
| 3390.79 | IN |  | 0.00 | kitchen_A | -226.6 cm | 1 |  |
| 3391.93 | IN |  | 0.00 | sideline_right | -26.1 cm | 2 |  |
| 3392.27 | – |  | – |  | – | 1 | secondary bounce |
| 3392.56 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3392.94 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3396.62 | IN |  | 0.00 | centreline_B | -182.9 cm | 2 |  |
| 3397.35 | – |  | – |  | – | 2 | secondary bounce |
| 3399.30 | UNCERTAIN |  | 1.00 | baseline_B | 77.7 cm | 1 | unconfirmed by iphone17, nothing |
| 3399.77 | – |  | – |  | – | 2 | secondary bounce |
| 3403.02 | IN |  | 0.00 | centreline_A | -127.4 cm | 3 |  |
| 3404.83 | IN |  | 0.00 | centreline_B | -67.1 cm | 2 |  |
| 3407.05 | IN |  | 0.00 | centreline_B | -146.2 cm | 1 |  |
| 3409.39 | UNCERTAIN |  | 1.00 | baseline_A | 98.1 cm | 1 | unconfirmed by samsung, nothing |
| 3410.06 | IN |  | 0.04 | baseline_A | -111.4 cm | 1 |  |
| 3412.58 | IN |  | 0.00 | sideline_left | -154.4 cm | 1 |  |
| 3418.71 | IN |  | 0.00 | centreline_A | -142.7 cm | 2 |  |
| 3419.81 | – |  | – |  | – | 1 | secondary bounce |
| 3420.45 | UNCERTAIN |  | 1.00 | baseline_B | 148.0 cm | 1 |  |
| 3426.53 | IN |  | 0.00 | baseline_A | -104.0 cm | 2 |  |
| 3427.92 | IN |  | 0.00 | centreline_B | -167.4 cm | 1 |  |
| 3430.09 | IN |  | 0.00 | centreline_B | -99.5 cm | 2 |  |
| 3432.38 | IN |  | 0.00 | kitchen_B | -112.8 cm | 2 |  |
| 3434.12 | IN |  | 0.00 | kitchen_B | -136.2 cm | 1 |  |
| 3434.37 | – |  | – |  | – | 1 | secondary bounce |
| 3436.38 | IN |  | 0.00 | centreline_A | -253.7 cm | 3 |  |
| 3437.07 | – |  | – |  | – | 2 | secondary bounce |
| 3437.57 | – |  | – |  | – | 2 | secondary bounce |
| 3438.23 | – |  | – |  | – | 3 | secondary bounce |
| 3437.94 | IN |  | 0.00 | sideline_right | -96.0 cm | 2 |  |
| 3438.43 | – |  | – |  | – | 1 | secondary bounce |
| 3443.27 | UNCERTAIN |  | 1.00 | baseline_A | 106.7 cm | 2 | cameras disagree (chi2 34) |
| 3447.12 | IN |  | 0.03 | sideline_left | -31.0 cm | 2 |  |
| 3454.33 | IN |  | 0.00 | centreline_A | -180.4 cm | 3 |  |
| 3456.05 | UNCERTAIN |  | 1.00 | baseline_A | 77.9 cm | 2 |  |
| 3458.45 | UNCERTAIN |  | 1.00 | baseline_A | 83.4 cm | 1 |  |
| 3461.75 | UNCERTAIN |  | 0.97 | baseline_A | 113.9 cm | 1 |  |
| 3462.55 | IN |  | 0.00 | sideline_right | -145.3 cm | 1 |  |
| 3463.92 | IN |  | 0.00 | kitchen_B | -132.6 cm | 1 |  |
| 3464.44 | – |  | – |  | – | 1 | secondary bounce |
| 3468.71 | IN |  | 0.00 | sideline_right | -28.2 cm | 1 |  |
| 3471.87 | UNCERTAIN |  | 0.98 | baseline_A | 111.4 cm | 1 |  |
| 3473.23 | IN |  | 0.05 | baseline_B | -39.8 cm | 2 |  |
| 3474.93 | IN |  | 0.00 | centreline_A | -147.3 cm | 2 |  |
| 3476.87 | IN |  | 0.00 | sideline_left | -119.0 cm | 1 |  |
| 3478.81 | IN |  | 0.00 | kitchen_A | -165.3 cm | 3 |  |
| 3480.11 | IN |  | 0.00 | kitchen_B | -191.0 cm | 1 |  |
| 3481.84 | UNCERTAIN |  | 0.68 | sideline_left | 9.7 cm | 1 |  |
| 3482.24 | IN |  | 0.00 | kitchen_B | -86.9 cm | 1 |  |
| 3482.74 | – |  | – |  | – | 1 | secondary bounce |
| 3483.28 | IN |  | 0.00 | kitchen_A | -119.8 cm | 2 |  |
| 3491.66 | UNCERTAIN |  | 1.00 | baseline_A | 198.4 cm | 1 |  |
| 3492.48 | IN |  | 0.00 | sideline_right | -133.8 cm | 2 |  |
| 3492.98 | – |  | – |  | – | 1 | secondary bounce |
| 3494.16 | IN |  | 0.00 | centreline_A | -217.8 cm | 1 |  |
| 3495.55 | UNCERTAIN |  | 0.43 | sideline_right | -1.6 cm | 1 |  |
| 3496.27 | UNCERTAIN |  | 0.26 | sideline_right | -6.0 cm | 1 |  |
| 3496.26 | UNCERTAIN |  | 0.09 | sideline_right | -10.9 cm | 1 |  |
| 3501.89 | IN |  | 0.00 | baseline_B | -61.2 cm | 2 |  |
| 3502.40 | – |  | – |  | – | 1 | secondary bounce |
| 3502.78 | IN |  | 0.00 | centreline_B | -194.2 cm | 1 |  |
| 3506.87 | IN |  | 0.01 | sideline_right | -64.1 cm | 2 |  |
| 3508.39 | IN |  | 0.00 | centreline_B | -262.9 cm | 2 |  |
| 3509.44 | UNCERTAIN |  | 0.15 | kitchen_B | -27.3 cm | 2 |  |
| 3509.90 | – |  | – |  | – | 1 | secondary bounce |
| 3510.98 | – |  | – |  | – | 1 | secondary bounce |
| 3513.62 | UNCERTAIN |  | 1.00 | sideline_right | 40.3 cm | 1 |  |
| 3514.08 | – |  | – |  | – | 1 | secondary bounce |
| 3514.54 | – |  | – |  | – | 2 | secondary bounce |
| 3515.06 | – |  | – |  | – | 2 | secondary bounce |
| 3515.49 | – |  | – |  | – | 1 | secondary bounce |
| 3515.97 | – |  | – |  | – | 2 | secondary bounce |
| 3516.40 | IN |  | 0.00 | baseline_A | -11.5 cm | 1 |  |
| 3516.68 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3520.47 | IN |  | 0.00 | baseline_A | -87.0 cm | 2 |  |
| 3522.05 | IN |  | 0.00 | centreline_B | -175.7 cm | 2 |  |
| 3524.97 | IN |  | 0.00 | kitchen_B | -139.8 cm | 1 |  |
| 3528.58 | UNCERTAIN |  | 1.00 | baseline_A | 124.3 cm | 1 |  |
| 3533.12 | UNCERTAIN |  | 1.00 | baseline_A | 65.5 cm | 2 | cameras disagree (chi2 38) |
| 3534.04 | – |  | – |  | – | 2 | secondary bounce |
| 3537.10 | IN |  | 0.00 | baseline_B | -101.7 cm | 1 |  |
| 3538.60 | IN |  | 0.00 | centreline_A | -156.8 cm | 1 |  |
| 3539.85 | IN |  | 0.00 | kitchen_B | -81.1 cm | 1 |  |
| 3540.15 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3540.48 | UNCERTAIN |  | 0.32 | sideline_left | -4.5 cm | 1 |  |
| 3540.87 | – |  | – |  | – | 1 | secondary bounce |
| 3543.04 | IN |  | 0.00 | centreline_B | -172.3 cm | 1 |  |
| 3551.44 | UNCERTAIN |  | 1.00 | baseline_A | 220.2 cm | 1 |  |
| 3552.43 | IN |  | 0.03 | baseline_B | -37.0 cm | 2 |  |
| 3553.78 | IN |  | 0.00 | centreline_A | -155.5 cm | 1 |  |
| 3555.38 | IN |  | 0.00 | kitchen_B | -137.3 cm | 1 |  |
| 3555.39 | IN |  | 0.00 | kitchen_B | -158.3 cm | 1 |  |
| 3557.06 | IN |  | 0.00 | kitchen_A | -208.2 cm | 2 |  |
| 3555.99 | UNCERTAIN |  | 1.00 | baseline_B | 49.6 cm | 1 |  |
| 3558.30 | UNCERTAIN |  | 0.69 | sideline_left | 13.8 cm | 1 |  |
| 3559.84 | IN |  | 0.00 | kitchen_A | -135.0 cm | 2 |  |
| 3561.51 | IN |  | 0.00 | kitchen_A | -137.2 cm | 1 |  |
| 3561.82 | – |  | – |  | – | 1 | secondary bounce |
| 3563.41 | UNCERTAIN |  | 1.00 | baseline_B | 377.2 cm | 1 |  |
| 3564.09 | UNCERTAIN |  | 1.00 | baseline_B | 371.1 cm | 1 |  |
| 3564.58 | – |  | – |  | – | 1 | secondary bounce |
| 3583.85 | IN |  | 0.00 | baseline_A | -70.8 cm | 2 |  |
| 3585.27 | IN |  | 0.00 | centreline_B | -210.0 cm | 1 |  |
| 3586.49 | UNCERTAIN |  | 0.91 | baseline_A | 81.7 cm | 1 |  |
| 3586.67 | IN |  | 0.00 | kitchen_B | -31.2 cm | 1 |  |
| 3587.29 | – |  | – |  | – | 2 | secondary bounce |
| 3587.58 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3587.89 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3591.20 | IN |  | 0.00 | centreline_B | -160.9 cm | 1 |  |
| 3596.21 | OUT | **OUT** | 1.00 | baseline_A | 166.3 cm | 1 |  |
| 3597.36 | IN |  | 0.00 | centreline_A | -266.1 cm | 2 |  |
| 3598.97 | IN |  | 0.00 | centreline_B | -171.3 cm | 1 |  |
| 3600.25 | IN |  | 0.00 | kitchen_A | -89.6 cm | 1 |  |
| 3601.21 | IN |  | 0.00 | kitchen_B | -171.8 cm | 1 |  |
| 3606.29 | UNCERTAIN |  | 1.00 | baseline_B | 91.5 cm | 2 |  |
| 3606.70 | – |  | – |  | – | 1 | secondary bounce |
| 3607.48 | – |  | – |  | – | 1 | secondary bounce |
| 3607.90 | – |  | – |  | – | 1 | secondary bounce |
| 3609.04 | UNCERTAIN |  | 1.00 | baseline_B | 139.9 cm | 2 |  |
| 3613.05 | IN |  | 0.00 | baseline_A | -81.0 cm | 1 |  |
| 3614.69 | IN |  | 0.00 | centreline_B | -205.9 cm | 2 |  |
| 3616.18 | IN |  | 0.00 | centreline_B | -197.6 cm | 1 |  |
| 3617.51 | IN |  | 0.02 | sideline_left | -21.4 cm | 2 |  |
| 3618.85 | IN |  | 0.00 | kitchen_B | -197.6 cm | 1 |  |
| 3619.27 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3620.16 | IN |  | 0.00 | kitchen_A | -43.7 cm | 2 |  |
| 3621.66 | IN |  | 0.00 | kitchen_A | -227.2 cm | 2 |  |
| 3626.41 | UNCERTAIN |  | 1.00 | baseline_B | 100.9 cm | 1 |  |
| 3628.47 | IN |  | 0.00 | sideline_right | -60.3 cm | 2 |  |
| 3629.19 | – |  | – |  | – | 2 | secondary bounce |
| 3629.59 | IN |  | 0.00 | baseline_A | -35.1 cm | 1 |  |
| 3630.15 | UNCERTAIN |  | 1.00 | baseline_B | 58.3 cm | 1 | unconfirmed by iphone17 |
| 3631.63 | UNCERTAIN |  | 1.00 | baseline_B | 245.5 cm | 1 |  |
| 3632.04 | – |  | – |  | – | 1 | secondary bounce |
| 3635.63 | IN |  | 0.00 | centreline_A | -296.6 cm | 2 |  |
| 3637.57 | IN |  | 0.00 | centreline_B | -256.6 cm | 2 |  |
| 3638.39 | – |  | – |  | – | 1 | secondary bounce |
| 3638.98 | – |  | – |  | – | 1 | secondary bounce |
| 3647.66 | UNCERTAIN |  | 0.14 | baseline_A | -60.1 cm | 1 |  |
| 3663.38 | UNCERTAIN |  | 1.00 | baseline_A | 96.4 cm | 1 |  |
| 3666.74 | UNCERTAIN |  | 1.00 | baseline_A | 86.2 cm | 2 | cameras disagree (chi2 37) |
| 3667.51 | IN |  | 0.00 | sideline_right | -62.7 cm | 1 |  |
| 3673.11 | UNCERTAIN |  | 0.46 | baseline_B | -2.8 cm | 2 |  |
| 3674.82 | IN |  | 0.00 | baseline_A | -75.5 cm | 2 |  |
| 3676.90 | IN |  | 0.00 | centreline_A | -155.2 cm | 3 |  |
| 3677.92 | – |  | – |  | – | 1 | secondary bounce |
| 3678.69 | IN |  | 0.00 | kitchen_B | -28.9 cm | 1 |  |
| 3687.12 | UNCERTAIN |  | 1.00 | baseline_A | 121.7 cm | 1 |  |
| 3690.28 | UNCERTAIN |  | 0.99 | baseline_A | 170.3 cm | 1 |  |
| 3691.14 | IN |  | 0.00 | sideline_right | -108.5 cm | 1 |  |
| 3691.14 | IN |  | 0.00 | sideline_right | -118.3 cm | 1 |  |
| 3692.89 | IN |  | 0.00 | centreline_A | -135.6 cm | 1 |  |
| 3692.89 | IN |  | 0.00 | centreline_A | -144.0 cm | 1 |  |
| 3694.56 | UNCERTAIN |  | 0.25 | kitchen_B | -104.2 cm | 2 |  |
| 3695.17 | UNCERTAIN |  | 1.00 | sideline_right | 39.1 cm | 1 | unconfirmed by iphone17 |
| 3694.55 | OUT | **OUT** | 1.00 | sideline_right | 153.7 cm | 1 |  |
| 3695.17 | UNCERTAIN |  | 0.99 | sideline_right | 16.2 cm | 1 | unconfirmed by samsung |
| 3695.78 | – |  | – |  | – | 1 | secondary bounce |
| 3696.01 | – |  | – |  | – | 1 | secondary bounce |
| 3696.20 | – |  | – |  | – | 1 | secondary bounce |
| 3700.09 | UNCERTAIN |  | 1.00 | sideline_left | 122.6 cm | 1 |  |
| 3700.79 | UNCERTAIN |  | 1.00 | baseline_A | 204.3 cm | 1 |  |
| 3707.59 | IN |  | 0.00 | sideline_left | -73.5 cm | 2 |  |
| 3709.07 | IN |  | 0.00 | centreline_A | -168.0 cm | 3 |  |
| 3709.27 | – |  | – |  | – | 1 | secondary bounce |
| 3710.72 | IN |  | 0.00 | sideline_left | -101.5 cm | 1 |  |
| 3712.30 | IN |  | 0.00 | kitchen_A | -203.9 cm | 2 |  |
| 3712.52 | – |  | – |  | – | 1 | secondary bounce |
| 3716.91 | UNCERTAIN |  | 1.00 | baseline_A | 4.1 cm | 1 | unconfirmed by samsung, nothing |
| 3718.06 | – |  | – |  | – | 1 | secondary bounce |
| 3719.72 | IN |  | 0.00 | sideline_right | -78.1 cm | 1 |  |
| 3719.72 | – |  | – |  | – | 1 | secondary bounce |
| 3720.58 | – |  | – |  | – | 1 | secondary bounce |
| 3722.03 | UNCERTAIN |  | 0.89 | baseline_B | 26.3 cm | 2 |  |
| 3722.85 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3723.19 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3723.95 | – |  | – |  | – | 1 | secondary bounce |
| 3726.95 | OUT | **OUT** | 1.00 | sideline_right | 18.4 cm | 2 |  |
| 3728.77 | UNCERTAIN |  | 1.00 | sideline_right | 45.3 cm | 1 | unconfirmed by iphone17 |
| 3730.93 | UNCERTAIN |  | 1.00 | baseline_B | 220.6 cm | 1 |  |
| 3735.77 | UNCERTAIN |  | 1.00 | baseline_A | 15.4 cm | 2 | cameras disagree (chi2 41) |
| 3737.66 | IN |  | 0.00 | centreline_B | -223.6 cm | 1 |  |
| 3738.80 | IN |  | 0.00 | sideline_right | -36.1 cm | 2 |  |
| 3764.47 | OUT | **OUT** | 1.00 | sideline_right | 145.0 cm | 1 |  |
| 3781.06 | IN |  | 0.00 | sideline_left | -81.1 cm | 2 |  |
| 3782.60 | IN |  | 0.00 | baseline_A | -12.8 cm | 2 |  |
| 3784.51 | IN |  | 0.00 | centreline_A | -151.6 cm | 1 |  |
| 3785.22 | UNCERTAIN |  | 0.37 | sideline_left | -9.1 cm | 2 |  |
| 3785.95 | – |  | – |  | – | 1 | secondary bounce |
| 3794.27 | IN |  | 0.00 | sideline_left | -128.9 cm | 1 |  |
| 3807.18 | IN |  | 0.00 | baseline_A | -9.7 cm | 1 |  |
| 3807.49 | IN |  | 0.00 | kitchen_B | -102.2 cm | 1 |  |
| 3808.33 | IN |  | 0.00 | kitchen_A | -66.7 cm | 1 |  |
| 3808.51 | – |  | – |  | – | 1 | secondary bounce |
| 3808.65 | – |  | – |  | – | 1 | secondary bounce |
| 3809.21 | – |  | – |  | – | 1 | secondary bounce |
| 3808.34 | IN |  | 0.00 | kitchen_A | -68.6 cm | 1 |  |
| 3807.51 | IN |  | 0.01 | sideline_right | -40.4 cm | 1 |  |
| 3807.81 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3808.11 | IN |  | 0.04 | sideline_right | -37.5 cm | 1 |  |
| 3813.75 | UNCERTAIN |  | 1.00 | baseline_A | 118.3 cm | 1 |  |
| 3814.46 | – |  | – |  | – | 1 | secondary bounce |
| 3816.41 | IN |  | 0.00 | baseline_A | -27.0 cm | 1 |  |
| 3818.19 | IN |  | 0.00 | sideline_left | -54.5 cm | 2 |  |
| 3819.51 | IN |  | 0.00 | sideline_right | -149.0 cm | 2 |  |
| 3820.79 | IN |  | 0.00 | centreline_B | -203.5 cm | 1 |  |
| 3821.68 | IN |  | 0.00 | kitchen_A | -214.0 cm | 2 |  |
| 3822.28 | – |  | – |  | – | 1 | secondary bounce |
| 3825.04 | IN |  | 0.00 | centreline_A | -208.2 cm | 1 |  |
| 3826.04 | IN |  | 0.00 | kitchen_B | -167.2 cm | 2 |  |
| 3826.76 | – |  | – |  | – | 1 | secondary bounce |
| 3827.26 | – |  | – |  | – | 2 | secondary bounce |
| 3827.62 | – |  | – |  | – | 2 | secondary bounce |
| 3828.11 | – |  | – |  | – | 1 | secondary bounce |
| 3837.40 | IN |  | 0.00 | centreline_A | -189.0 cm | 2 |  |
| 3838.94 | IN |  | 0.00 | centreline_B | -245.8 cm | 2 |  |
| 3841.11 | IN |  | 0.00 | centreline_B | -229.9 cm | 1 |  |
| 3843.49 | UNCERTAIN |  | 1.00 | sideline_left | 10.0 cm | 1 | unconfirmed by samsung, nothing |
| 3849.49 | IN |  | 0.00 | baseline_A | -35.9 cm | 1 |  |
| 3855.81 | IN |  | 0.00 | sideline_left | -78.9 cm | 2 |  |
| 3857.51 | IN |  | 0.00 | centreline_B | -111.7 cm | 2 |  |
| 3858.81 | IN |  | 0.00 | kitchen_B | -138.1 cm | 1 |  |
| 3859.33 | – |  | – |  | – | 1 | secondary bounce |
| 3861.79 | UNCERTAIN |  | 1.00 | sideline_left | 59.0 cm | 1 |  |
| 3863.30 | UNCERTAIN |  | 1.00 | baseline_B | 251.1 cm | 1 |  |
| 3863.81 | – |  | – |  | – | 1 | secondary bounce |
| 3864.72 | – |  | – |  | – | 1 | secondary bounce |
| 3867.74 | UNCERTAIN |  | 1.00 | baseline_A | 15.9 cm | 1 | unconfirmed by samsung, nothing |
| 3869.70 | IN |  | 0.00 | centreline_B | -159.2 cm | 1 |  |
| 3871.38 | IN |  | 0.00 | sideline_right | -114.1 cm | 2 |  |
| 3875.30 | IN |  | 0.00 | sideline_right | -38.6 cm | 1 |  |
| 3875.89 | UNCERTAIN |  | 1.00 | sideline_left | 391.7 cm | 1 |  |
| 3877.20 | IN |  | 0.00 | sideline_right | -27.5 cm | 1 |  |
| 3877.95 | – |  | – |  | – | 1 | secondary bounce |
| 3879.89 | IN |  | 0.03 | baseline_A | -3.0 cm | 1 |  |
| 3885.29 | UNCERTAIN |  | 1.00 | sideline_left | 359.1 cm | 1 |  |
| 3886.68 | UNCERTAIN |  | 1.00 | sideline_left | 156.7 cm | 1 |  |
| 3891.46 | IN |  | 0.00 | baseline_A | -107.1 cm | 1 |  |
| 3892.17 | – |  | – |  | – | 2 | secondary bounce |
| 3896.86 | UNCERTAIN |  | 0.49 | baseline_B | -0.4 cm | 2 |  |
| 3898.58 | IN |  | 0.00 | centreline_A | -300.1 cm | 1 |  |
| 3900.33 | IN |  | 0.00 | centreline_A | -189.2 cm | 2 |  |
| 3902.47 | UNCERTAIN |  | 1.00 | baseline_A | 163.1 cm | 1 |  |
| 3902.61 | UNCERTAIN |  | 1.00 | sideline_left | 335.8 cm | 1 |  |
| 3902.81 | UNCERTAIN |  | 1.00 | baseline_A | 145.2 cm | 1 |  |
| 3903.07 | – |  | – |  | – | 1 | second bounce (ball not returned) |
| 3907.11 | UNCERTAIN |  | 1.00 | sideline_left | 395.0 cm | 1 |  |
| 3908.60 | UNCERTAIN |  | 1.00 | baseline_A | 98.5 cm | 1 |  |
| 3909.54 | IN |  | 0.00 | centreline_A | -138.4 cm | 1 |  |
| 3911.72 | UNCERTAIN |  | 0.99 | baseline_B | 51.3 cm | 1 |  |
| 3912.29 | UNCERTAIN |  | 1.00 | baseline_A | 48.7 cm | 1 | unconfirmed by samsung, nothing |
| 3915.77 | IN |  | 0.00 | centreline_A | -164.2 cm | 2 |  |
| 3915.78 | IN |  | 0.00 | centreline_A | -175.3 cm | 1 |  |
| 3918.38 | UNCERTAIN |  | 1.00 | baseline_A | 25.3 cm | 1 | unconfirmed by samsung, nothing |
| 3918.56 | – |  | – |  | – | 1 | secondary bounce |
| 3920.00 | UNCERTAIN |  | 1.00 | sideline_left | 369.3 cm | 1 |  |
| 3927.59 | UNCERTAIN |  | 1.00 | sideline_left | 304.5 cm | 1 |  |
| 3928.81 | UNCERTAIN |  | 1.00 | sideline_left | 175.9 cm | 1 |  |
| 3929.38 | – |  | – |  | – | 1 | secondary bounce |
| 3930.66 | IN |  | 0.00 | centreline_A | -162.3 cm | 1 |  |
| 3933.31 | UNCERTAIN |  | 1.00 | sideline_left | 198.0 cm | 1 |  |
| 3934.35 | IN |  | 0.00 | kitchen_B | -125.6 cm | 1 |  |
| 3935.38 | – |  | – |  | – | 1 | secondary bounce |
| 3937.47 | IN |  | 0.00 | centreline_A | -174.5 cm | 2 |  |
| 3936.33 | UNCERTAIN |  | 1.00 | baseline_A | 10.9 cm | 1 |  |
| 3937.45 | IN |  | 0.00 | centreline_A | -187.3 cm | 1 |  |
| 3943.54 | UNCERTAIN |  | 1.00 | baseline_A | 58.2 cm | 1 |  |
| 3943.85 | – |  | – |  | – | 1 | secondary bounce |
| 3944.63 | IN |  | 0.00 | sideline_right | -121.0 cm | 1 |  |
| 3945.27 | UNCERTAIN |  | 1.00 | baseline_A | 127.8 cm | 1 |  |
| 3946.18 | IN |  | 0.00 | centreline_A | -137.4 cm | 2 |  |
| 3947.75 | UNCERTAIN |  | 1.00 | baseline_B | 63.3 cm | 1 | unconfirmed by iphone17 |
| 3948.87 | UNCERTAIN |  | 1.00 | sideline_left | 323.0 cm | 1 |  |
| 3954.62 | UNCERTAIN |  | 1.00 | baseline_B | 290.6 cm | 1 |  |
| 3955.04 | – |  | – |  | – | 1 | secondary bounce |
| 3955.45 | UNCERTAIN |  | 1.00 | baseline_B | 272.1 cm | 1 |  |
| 3957.86 | IN |  | 0.00 | sideline_right | -110.5 cm | 3 |  |
| 3959.46 | IN |  | 0.00 | centreline_B | -232.6 cm | 2 |  |
| 3960.94 | IN |  | 0.00 | sideline_left | -81.8 cm | 1 |  |
| 3961.54 | IN |  | 0.00 | kitchen_B | -116.2 cm | 1 |  |
| 3963.20 | IN |  | 0.00 | centreline_B | -254.5 cm | 2 |  |
| 3965.29 | UNCERTAIN |  | 1.00 | sideline_left | 287.5 cm | 1 |  |
| 3965.70 | IN |  | 0.00 | sideline_right | -104.8 cm | 1 |  |
| 3967.71 | UNCERTAIN |  | 1.00 | sideline_left | 288.1 cm | 1 |  |
| 3970.00 | UNCERTAIN |  | 1.00 | sideline_left | 337.3 cm | 1 |  |
| 3971.52 | UNCERTAIN |  | 1.00 | sideline_left | 232.3 cm | 1 |  |
| 3972.15 | – |  | – |  | – | 2 | secondary bounce |
| 3972.49 | UNCERTAIN |  | 1.00 | sideline_left | 362.4 cm | 1 |  |
| 3974.26 | UNCERTAIN |  | 1.00 | baseline_B | 220.8 cm | 1 |  |
| 3974.68 | UNCERTAIN |  | 1.00 | baseline_B | 215.0 cm | 1 |  |
| 3977.51 | UNCERTAIN |  | 0.93 | sideline_right | 15.2 cm | 1 |  |
| 3977.96 | IN |  | 0.00 | centreline_A | -205.5 cm | 1 |  |
| 3978.34 | – |  | – |  | – | 1 | secondary bounce |
| 3979.52 | IN |  | 0.00 | sideline_left | -121.9 cm | 2 |  |
| 3980.57 | UNCERTAIN |  | 1.00 | sideline_left | 398.3 cm | 1 |  |
| 3985.82 | IN |  | 0.00 | kitchen_B | -155.5 cm | 2 |  |
| 3986.66 | – |  | – |  | – | 2 | secondary bounce |
| 3990.76 | IN |  | 0.00 | sideline_right | -73.1 cm | 1 |  |
| 3991.22 | – |  | – |  | – | 1 | secondary bounce |
| 3991.56 | – |  | – |  | – | 2 | secondary bounce |
| 3992.00 | – |  | – |  | – | 1 | secondary bounce |
| 3995.14 | UNCERTAIN |  | 1.00 | sideline_left | 247.9 cm | 1 |  |
| 3995.78 | OUT | **OUT** | 1.00 | sideline_right | 72.5 cm | 2 |  |
| 3998.30 | UNCERTAIN |  | 1.00 | baseline_A | 140.5 cm | 1 |  |
| 4001.80 | UNCERTAIN |  | 1.00 | sideline_left | 305.8 cm | 1 |  |
| 4002.48 | – |  | – |  | – | 2 | secondary bounce |
| 4003.06 | UNCERTAIN |  | 1.00 | sideline_left | 224.9 cm | 1 |  |
| 4003.93 | IN |  | 0.00 | centreline_A | -286.3 cm | 2 |  |
| 4004.24 | UNCERTAIN |  | 1.00 | sideline_left | 355.6 cm | 1 |  |
| 4005.39 | – |  | – |  | – | 1 | secondary bounce |
| 4006.92 | IN |  | 0.00 | kitchen_B | -181.2 cm | 2 |  |
| 4006.79 | UNCERTAIN |  | 1.00 | sideline_left | 352.8 cm | 1 |  |
| 4007.43 | IN |  | 0.00 | kitchen_B | -166.9 cm | 1 |  |
| 4009.46 | UNCERTAIN |  | 1.00 | sideline_left | 391.0 cm | 1 |  |
| 4012.38 | UNCERTAIN |  | 1.00 | sideline_left | 237.1 cm | 1 |  |
| 4014.80 | IN |  | 0.00 | sideline_left | -93.7 cm | 2 |  |
| 4016.55 | UNCERTAIN |  | 1.00 | baseline_A | 88.8 cm | 1 |  |
| 4017.24 | – |  | – |  | – | 1 | secondary bounce |
| 4018.20 | UNCERTAIN |  | 1.00 | sideline_left | 193.4 cm | 1 |  |
| 4020.50 | IN |  | 0.00 | centreline_B | -188.1 cm | 2 |  |
| 4021.24 | UNCERTAIN |  | 1.00 | baseline_A | 54.5 cm | 1 | unconfirmed by samsung, nothing |
| 4022.05 | UNCERTAIN |  | 0.25 | sideline_left | -16.2 cm | 1 |  |
| 4022.05 | – |  | – |  | – | 1 | secondary bounce |
| 4022.51 | – |  | – |  | – | 1 | secondary bounce |
| 4023.57 | IN |  | 0.00 | kitchen_A | -157.4 cm | 1 |  |
| 4024.20 | UNCERTAIN |  | 1.00 | sideline_left | 313.9 cm | 1 |  |
| 4024.99 | IN |  | 0.00 | kitchen_A | -211.4 cm | 1 |  |
| 4024.96 | UNCERTAIN |  | 0.71 | kitchen_B | -106.7 cm | 1 |  |
| 4025.98 | – |  | – |  | – | 1 | secondary bounce |
| 4027.48 | UNCERTAIN |  | 1.00 | sideline_left | 171.3 cm | 2 |  |
| 4027.29 | UNCERTAIN |  | 1.00 | sideline_left | 235.4 cm | 1 |  |
| 4029.77 | UNCERTAIN |  | 1.00 | baseline_A | 283.2 cm | 1 |  |
| 4031.13 | UNCERTAIN |  | 1.00 | sideline_left | 295.4 cm | 1 |  |
| 4034.81 | UNCERTAIN |  | 1.00 | sideline_left | 365.0 cm | 1 |  |
| 4035.13 | – |  | – |  | – | 1 | secondary bounce |
| 4035.86 | UNCERTAIN |  | 1.00 | baseline_A | 236.0 cm | 1 |  |
| 4036.75 | IN |  | 0.00 | centreline_B | -229.5 cm | 2 |  |
| 4038.27 | IN |  | 0.00 | centreline_A | -208.4 cm | 2 |  |
| 4038.92 | UNCERTAIN |  | 1.00 | sideline_left | 289.8 cm | 1 |  |
| 4040.06 | IN |  | 0.00 | kitchen_A | -111.0 cm | 1 |  |
| 4040.29 | – |  | – |  | – | 1 | secondary bounce |
| 4039.75 | IN |  | 0.02 | sideline_left | -14.8 cm | 1 |  |
| 4040.01 | – |  | – |  | – | 1 | secondary bounce |
| 4043.45 | UNCERTAIN |  | 1.00 | sideline_left | 344.5 cm | 1 |  |
| 4043.93 | – |  | – |  | – | 1 | secondary bounce |
| 4047.98 | IN |  | 0.00 | baseline_A | -81.0 cm | 2 |  |
| 4048.93 | – |  | – |  | – | 1 | secondary bounce |
| 4049.60 | IN |  | 0.00 | sideline_right | -30.8 cm | 1 |  |
| 4049.90 | – |  | – |  | – | 2 | secondary bounce |
| 4050.11 | – |  | – |  | – | 1 | secondary bounce |
| 4066.49 | UNCERTAIN |  | 1.00 | sideline_left | 278.2 cm | 1 |  |

## Warnings

* – s samsung: frame size 1920x1080 differs from calibration 1920x1440; recalibrate

## Calibrations

* iphone17 at 654 s: RMS 2.36 px from 12 points; worst point B_centre_kitchen 4.0 px
* samsung at 1309 s: RMS 6.90 px from 12 points; worst point A_centre_kitchen 18.3 px
* nothing at 1400 s: RMS 2.15 px from 10 points; worst point B_centre_kitchen 4.8 px
