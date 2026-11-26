#!/usr/bin/env python3
"""What calibrations would the current server have used in a recorded session?

Runs the calibration upkeep (auto line snap at each calibration, re-snap of the other cameras,
drift tracking every 10 s, a camera that moved more than it can follow taken out of the calls)
on the session's recorded preview snapshots, starting from the clicks that were actually made,
and writes the resulting calibration history as ``calibrated`` events (camera models and
points, no images) and ``camera_suspended`` / ``camera_resumed`` events:

    .venv/bin/python scripts/counterfactual_calibration.py data/live/sessions/<id> out.jsonl [--no-suspend] [--live-clicks] [--no-scrub]
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
LOST_CHECKS_TO_SUSPEND = 3  # server.LiveServer.LOST_CHECKS_TO_SUSPEND


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    suspend_moved = "--no-suspend" not in sys.argv  # --no-suspend: keep moved cameras in the calls (old server)
    # --live-clicks: take every calibration live made by hand or by line snap as it was (only the
    # drift checks are re-run). Isolates a drift-tracking change from the line snap: re-snapping on a
    # different snapshot than live used can land on another court's lines (field test 5, Samsung).
    live_clicks = "--live-clicks" in sys.argv
    src, dst = Path(args[0]), Path(args[1])
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

    def suspend(cam, t, reason):
        st = state[cam]
        if st.get("suspended") is None:
            st["suspended"] = reason
            out.append({"type": "camera_suspended", "camera": cam, "t": t, "reason": reason})
            print(f"{t:7.0f} {cam:12} suspended: {reason}")

    def resume(cam, t, why):
        st = state.get(cam) or {}
        st["lost"] = 0
        if st.get("suspended") is not None:
            st["suspended"] = None
            out.append({"type": "camera_resumed", "camera": cam, "t": t, "why": why})
            print(f"{t:7.0f} {cam:12} resumed: {why}")

    def apply(cam, camera, points, t, source, extra, img):
        ref = DriftTracker(img, points) if (img is not None and source != "drift") else (state.get(cam) or {}).get("ref")
        if cam in state:
            resume(cam, t, "recalibrated")
        state[cam] = {"camera": camera, "ref": ref, "suspended": None, "lost": 0}
        out.append({"type": "calibrated", "camera": cam, "t": t, "rms_px": camera.reprojection_rms_px, "source": source,
                    "camera_model": camera.to_dict(), "clicked": points, **extra})
        print(f"{t:7.0f} {cam:12} {source:30} rms {camera.reprojection_rms_px:.2f}")

    clicks = [e for e in ev if e.get("type") == "calibrated" and (not live_clicks or e.get("source") != "drift")]
    # cameras that connected with a calibration saved in an earlier session: not used for calls until
    # the court lines confirm it (server._drift_loop), tried at every check until a calibration exists
    saved = {e["camera"]: Camera.from_dict(e["camera_model"]) for e in ev
             if e.get("type") == "camera_connected" and e.get("camera_model") and suspend_moved}
    saved_off: dict[str, bool] = {}
    timeline = sorted([(e["t"], "click", e) for e in clicks] + [(t, "drift", None) for t in np.arange(0, end_t, EVERY_S)],
                      key=lambda a: a[0])
    for t, kind, e in timeline:
        if kind == "click" and live_clicks:
            cam = e["camera"]
            apply(cam, Camera.from_dict(e["camera_model"]), e["clicked"], t, e["source"],
                  {k: e[k] for k in ("moved_px", "fit_px") if k in e}, snapshot(cam, t))
        elif kind == "click":
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
            for cam, model in list(saved.items()):
                if cam in state:
                    saved.pop(cam)
                    continue
                im = snapshot(cam, t)
                if im is None:
                    continue
                sn = auto_snap(im, court, model, 0.0)
                if sn:
                    saved.pop(cam)
                    if saved_off.pop(cam, False):
                        out.append({"type": "camera_resumed", "camera": cam, "t": t, "why": "confirmed by the lines"})
                    apply(cam, sn["camera"], sn["points"], t, "lines (auto, at start)",
                          {"moved_px": sn["moved_px"], "fit_px": sn["fit_px"]}, im)
                elif not saved_off.get(cam):
                    saved_off[cam] = True
                    out.append({"type": "camera_suspended", "camera": cam, "t": t,
                                "reason": "calibration from an earlier session, not confirmed by the court lines"})
                    print(f"{t:7.0f} {cam:12} suspended: saved calibration not confirmed")
            for cam, st in list(state.items()):
                im = snapshot(cam, t) if st["ref"] is not None else None
                if im is None:
                    continue
                res = st["ref"].check(im, court, st["camera"])
                status = res["status"]
                if status != "lost":
                    st["lost"] = 0
                if status == "moved":
                    apply(cam, res["camera"], res["points"], t, "drift", {"moved_px": res["moved_px"], "how": res["how"]}, im)
                elif status == "big" and suspend_moved:
                    suspend(cam, t, f"moved {res.get('moved_px')} px since calibration")
                elif status == "lost" and suspend_moved:
                    st["lost"] += 1
                    if st["lost"] >= LOST_CHECKS_TO_SUSPEND:
                        suspend(cam, t, "view doesn't match its calibration frame")
                elif status == "steady":
                    resume(cam, t, "back where it was")
    from privacy import scrub  # names in the gitignored .private_words, home paths

    text = "".join(json.dumps(e) + "\n" for e in out)
    # scrubbed (device names) to match the exported copy in data/field/<id>; --no-scrub keeps the
    # local session's own camera names, to replay against data/live/sessions/<id>
    dst.write_text(text if "--no-scrub" in sys.argv else scrub(text))
    print(f"{len(out)} calibration events -> {dst}")


if __name__ == "__main__":
    main()
