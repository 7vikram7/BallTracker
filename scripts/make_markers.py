#!/usr/bin/env python3
"""Print the side markers used by automatic calibration (balltracker/geometry/autocal.py).

    python scripts/make_markers.py docs/markers

Writes marker_A.png (ArUco DICT_4X4_50 id 0) and marker_B.png (id 1), sized for A4 at 300 dpi
(the black square is ~18 cm). Place marker A upright behind baseline A and marker B behind
baseline B, facing the court, where cameras at the other end can see them. They tell the
automatic calibration which half is which (the court looks the same rotated 180 degrees).
"""

import sys
from pathlib import Path

import cv2
import numpy as np


def main() -> None:
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "docs/markers")
    out.mkdir(parents=True, exist_ok=True)
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    for mid, side in ((0, "A"), (1, "B")):
        m = cv2.aruco.generateImageMarker(d, mid, 2100)  # 2100 px = 17.8 cm at 300 dpi
        page = np.full((3508, 2480), 255, np.uint8)  # A4 portrait at 300 dpi
        y0, x0 = 500, (2480 - 2100) // 2
        page[y0:y0 + 2100, x0:x0 + 2100] = m
        cv2.putText(page, f"SIDE {side}", (x0, 3000), cv2.FONT_HERSHEY_SIMPLEX, 8, 0, 20)
        cv2.putText(page, f"BallTracker marker id {mid} (place behind baseline {side})", (x0, 3250),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.6, 0, 3)
        cv2.imwrite(str(out / f"marker_{side}.png"), page)
        print(out / f"marker_{side}.png")


if __name__ == "__main__":
    main()
