#!/usr/bin/env python3
"""Cut a time slice out of a recorded live session (for sample data and quick replays).

    python scripts/slice_session.py data/live/sessions/20261119-070916 out_dir --from 1000 --to 1500 [--previews 2]

Keeps: court.json, session.json, calibration/, connection/calibration events, the events
inside the slice, each camera's dets.jsonl rows inside the slice, and (optionally) a few
preview frames per camera (frames.bin + index.csv) so the court can be looked at.
The result is a normal session folder: `bt replay out_dir` works on it.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
from pathlib import Path

KEEP_ALWAYS = {"camera_connected", "calibrated"}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--from", dest="t0", type=float, required=True, help="session seconds")
    ap.add_argument("--to", dest="t1", type=float, required=True)
    ap.add_argument("--previews", type=int, default=2, help="preview frames to keep per camera")
    a = ap.parse_args()
    src, out = a.session, a.out
    out.mkdir(parents=True, exist_ok=True)
    for name in ("court.json", "session.json"):
        if (src / name).exists():
            shutil.copy2(src / name, out / name)
    if (src / "calibration").is_dir():
        shutil.copytree(src / "calibration", out / "calibration", dirs_exist_ok=True)
    with open(src / "events.jsonl") as f, open(out / "events.jsonl", "w") as o:
        for line in f:
            e = json.loads(line)
            if e.get("type") in KEEP_ALWAYS or a.t0 <= float(e.get("t", -1)) <= a.t1:
                o.write(line)
    for cam in sorted(p for p in src.iterdir() if p.is_dir() and p.name not in ("calibration", "replays")):
        dets = cam / "dets.jsonl"
        if not dets.exists():
            continue
        (out / cam.name).mkdir(exist_ok=True)
        n = 0
        with open(dets) as f, open(out / cam.name / "dets.jsonl", "w") as o:
            for line in f:
                ts = json.loads(line)["ts"]
                if ts > a.t1:
                    break
                if ts >= a.t0:
                    o.write(line)
                    n += 1
        idx = cam / "index.csv"
        if a.previews and idx.exists() and (cam / "frames.bin").exists():
            rows = [r for r in csv.DictReader(open(idx)) if a.t0 <= float(r["t_session"]) <= a.t1]
            step = max(1, len(rows) // a.previews)
            pick = rows[::step][: a.previews]
            with open(cam / "frames.bin", "rb") as fb, open(out / cam.name / "frames.bin", "wb") as ob, \
                    open(out / cam.name / "index.csv", "w", newline="") as oi:
                w = csv.DictWriter(oi, fieldnames=list(rows[0].keys()) if rows else ["seq"])
                w.writeheader()
                off = 0
                for r in pick:
                    fb.seek(int(r["offset"]))
                    data = fb.read(int(r["nbytes"]))
                    ob.write(data)
                    w.writerow({**r, "offset": off})
                    off += len(data)
        print(f"{cam.name}: {n} frames of detections")


if __name__ == "__main__":
    main()
