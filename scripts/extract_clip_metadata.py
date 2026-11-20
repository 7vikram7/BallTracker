#!/usr/bin/env python3
"""Turn a video into data that can be shared and tested without the video itself.

    .venv/bin/python scripts/extract_clip_metadata.py TestData/iPhone17SlowMo/AllPhotosData/IMG_5017.MOV \
        data/real/2026-11-17/clip_240fps

Writes into the output folder:
  video.json          container facts: codec, size, display rotation, frame count, duration,
                      frame-interval statistics (from the presentation timestamps)
  frames.jsonl.gz     one line per frame: {"i": index, "t": seconds (from PTS), "mac": [...], "phone": [...]}
                      with every ball candidate of the Mac detector (detection.py) and of the phone
                      detector (C++ core via ballcore.py, the same code the app runs), each
                      [u, v, radius_px, score, area_px, elongation] in upright-image pixels.

Tracking, bounce detection and the chalk-mark comparison all start from these candidates, so
`tests/test_real_clip.py` re-runs the real-footage validation on any clone. Images are not
stored: the video can show people and is hundreds of MB.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from balltracker.detection import DetectorConfig, MotionColorBallDetector  # noqa: E402
from balltracker.video import VideoFileSource  # noqa: E402


def _cands(cs) -> list[list[float]]:
    return [[round(c.u, 2), round(c.v, 2), round(c.radius_px, 2), round(c.score, 3), round(c.area_px, 1),
             round(c.elongation, 3)] for c in cs]


def video_facts(path: Path, src: VideoFileSource, ts: list[float]) -> dict:
    import av

    with av.open(str(path)) as c:
        s = c.streams.video[0]
        codec = s.codec_context.name
        size = [s.codec_context.width, s.codec_context.height]
        avg = float(s.average_rate) if s.average_rate else None
    dt = np.diff(ts)
    return {"file": path.name, "codec": codec, "coded_size": size, "display_rotation_deg": src.rotation_deg,
            "upright_size": [src.info.width, src.info.height],
            "frames": len(ts), "duration_s": round(ts[-1] - ts[0], 4), "container_avg_fps": avg,
            "measured_avg_fps": round((len(ts) - 1) / (ts[-1] - ts[0]), 2),
            "frame_interval_ms": {"median": round(1e3 * float(np.median(dt)), 3),
                                  "p5": round(1e3 * float(np.percentile(dt, 5)), 3),
                                  "p95": round(1e3 * float(np.percentile(dt, 95)), 3),
                                  "max": round(1e3 * float(dt.max()), 3)}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--no-phone", action="store_true", help="skip the phone (C++) detector")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    src = VideoFileSource(a.video)
    mac = MotionColorBallDetector(DetectorConfig())
    phone = None
    if not a.no_phone:
        from balltracker.ballcore import NativeDetector

        phone = NativeDetector()
    ts, t0 = [], time.time()
    with gzip.open(a.out / "frames.jsonl.gz", "wt", compresslevel=9) as f:
        for fr in src.frames():
            row = {"i": fr.index, "t": round(float(fr.t), 6), "mac": _cands(mac.detect(fr.image))}
            if phone is not None:
                row["phone"] = _cands(phone.detect(fr.image))
            f.write(json.dumps(row, separators=(",", ":")) + "\n")
            ts.append(float(fr.t))
            if fr.index % 1000 == 0:
                print(f"frame {fr.index}  {time.time() - t0:.0f} s", flush=True)
    facts = video_facts(a.video, src, ts)
    facts["detectors"] = {"mac": mac.name if hasattr(mac, "name") else "MotionColorBallDetector",
                          "phone": phone.name if phone is not None else None}
    (a.out / "video.json").write_text(json.dumps(facts, indent=1) + "\n")
    print(json.dumps(facts, indent=1))


if __name__ == "__main__":
    main()
