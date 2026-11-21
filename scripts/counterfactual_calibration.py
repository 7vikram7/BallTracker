#!/usr/bin/env python3
"""What calibrations would the current server have used in a recorded session?

Runs the calibration upkeep (auto line snap at each calibration, re-snap of the other cameras,
drift tracking every 10 s) on the session's recorded preview snapshots, starting from the
clicks that were actually made, and writes the resulting calibration history as ``calibrated``
events (camera models and points, no images):

    .venv/bin/python scripts/counterfactual_calibration.py data/live/sessions/<id> out.jsonl
    bt replay data/field/<id> --calibrations out.jsonl --workers 3

Needs the local session folder with snapshots (``<camera>/index.csv`` + ``frames.bin``); the
snapshots show people, so they are not committed, and the output is (after the privacy scrub).

Field test 3: ``data/field/20261121-071625/counterfactual/calibrations.jsonl`` was produced by
this procedure with the code of commit 22aef8d (drift tracking by a similarity transform; since
ee648f1 it is a homography, so a fresh run gives a different history). See the README there.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent / "hooks"))

from balltracker.geometry.camera import Camera  # noqa: E402
from balltracker.geometry.court import CourtSpec  # noqa: E402
from balltracker.geometry.drift import DriftTracker  # noqa: E402
from balltracker.live.upkeep import auto_snap  # noqa: E402

EVERY_S = 10.0  # the server's drift check interval


def main() -> None:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    court = CourtSpec.from_dict(json.loads((src / "court.json").read_text()))
    ev = [json.loads(line) for line in (src / "events.jsonl").read_text().splitlines() if line.strip()]
    end_t = max(e["t"] for e in ev if isinstance(e.get("t"), (int, float)))
    snaps = {d.name: (list(csv.DictReader(open(d / "index.csv"))), open(d / "frames.bin", "rb"))
             for d in src.iterdir() if (d / "index.csv").exists()}

    def snapshot(cam: str, t: float):
        if cam not in snaps:
            return None
        rows, fb = snaps[cam]
        r = min(rows, key=lambda r: abs(float(r["t_session"]) - t))
        if abs(float(r["t_session"]) - t) > 5:
            return None
        fb.seek(int(r["offset"]))
        return cv2.imdecode(np.frombuffer(fb.read(int(r["nbytes"])), np.uint8), cv2.IMREAD_COLOR)

    state: dict[str, dict] = {}
    out: list[dict] = []

    def apply(cam, camera, points, t, source, extra, img):
        ref = DriftTracker(img, points) if (img is not None and source != "drift") else (state.get(cam) or {}).get("ref")
        state[cam] = {"camera": camera, "ref": ref}
        out.append({"type": "calibrated", "camera": cam, "t": t, "rms_px": camera.reprojection_rms_px, "source": source,
                    "camera_model": camera.to_dict(), "clicked": points, **extra})
        print(f"{t:7.0f} {cam:12} {source:30} rms {camera.reprojection_rms_px:.2f}")

    clicks = [e for e in ev if e.get("type") == "calibrated"]
    timeline = sorted([(e["t"], "click", e) for e in clicks] + [(t, "drift", None) for t in np.arange(0, end_t, EVERY_S)],
                      key=lambda a: a[0])
    for t, kind, e in timeline:
        if kind == "click":
            cam, camera = e["camera"], Camera.from_dict(e["camera_model"])
            img = snapshot(cam, t)
            sn = auto_snap(img, court, camera) if img is not None else None
            if sn:
                apply(cam, sn["camera"], sn["points"], t, "clicks + lines (auto)",
                      {"moved_px": sn["moved_px"], "fit_px": sn["fit_px"], "clicked_rms_px": camera.reprojection_rms_px}, img)
            else:
                apply(cam, camera, e["clicked"], t, "clicks", {}, img)
            for other, st in list(state.items()):  # re-snap the other cameras (server._refine_others)
                if other == cam:
                    continue
                im = snapshot(other, t)
                sn = auto_snap(im, court, st["camera"]) if im is not None else None
                if sn:
                    apply(other, sn["camera"], sn["points"], t + 0.5, f"lines (auto, after {cam})",
                          {"moved_px": sn["moved_px"], "fit_px": sn["fit_px"]}, im)
        else:
            for cam, st in list(state.items()):
                im = snapshot(cam, t) if st["ref"] is not None else None
                if im is None:
                    continue
                res = st["ref"].check(im, court, st["camera"])
                if res["status"] == "moved":
                    apply(cam, res["camera"], res["points"], t, "drift", {"moved_px": res["moved_px"], "how": res["how"]}, im)
    from privacy import scrub  # names in the gitignored .private_words, home paths

    dst.write_text(scrub("".join(json.dumps(e) + "\n" for e in out)))
    print(f"{len(out)} calibration events -> {dst}")


if __name__ == "__main__":
    main()
