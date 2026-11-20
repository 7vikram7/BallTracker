"""Real 240 fps footage with chalk-mark ground truth, without the video (PHASE0_RESULTS.md §6).

data/real/2026-11-17/clip_240fps/frames.jsonl.gz holds every frame's timestamp and ball candidates
from the Mac detector and the phone (C++) detector, extracted from the original iPhone Slo-mo
file by scripts/extract_clip_metadata.py. From them this re-runs tracking and bounce detection
and compares the bounces with the chalk marks photographed after each throw.

The camera is uncalibrated (close, low, portrait; a taped line on tiles), so positions are compared
in pixels and converted with the ball as a ruler (6.7 cm diameter), as in PHASE0_RESULTS.md.
"""

import gzip
import json
from pathlib import Path

import numpy as np
import pytest

D = Path(__file__).resolve().parents[1] / "data" / "real" / "2026-11-17"
FRAMES = D / "clip_240fps" / "frames.jsonl.gz"
# The 12 throws' floor bounces (s), from PHASE0_RESULTS.md §6.
TRUE_BOUNCES = [0.79, 5.61, 9.37, 16.35, 20.60, 24.74, 28.44, 37.51, 41.32, 45.94, 49.57, 52.91]
# When each chalk-mark photo was taken (s into the clip); a mark belongs to a bounce before it.
PHOTO_T = {"5008": 7, "5009": 11, "5010": 18, "5011": 28, "5012": 35, "5013": 39, "5014": 43, "5015": 52, "5016": 55}
BALL_RADIUS_CM = 3.35

pytestmark = [pytest.mark.slow, pytest.mark.skipif(not FRAMES.exists(), reason="clip data missing")]


def _bounces(detector: str) -> list[dict]:
    import dataclasses

    from balltracker.bounce import BounceConfig, BounceDetector
    from balltracker.detection import Candidate
    from balltracker.geometry.camera import Camera
    from balltracker.geometry.court import CourtSpec
    from balltracker.tracking import BallTracker

    tr = BallTracker()
    with gzip.open(FRAMES, "rt") as f:
        for line in f:
            r = json.loads(line)
            tr.update(r["i"], r["t"], [Candidate(*c) for c in r[detector]])
    flights = [x for x in tr.finish() if np.median([p.radius_px for p in x.points]) > 15 and len(x.points) >= 20]
    # No calibration exists for this clip: a stand-in camera looking along the floor, with the
    # court-margin check off, as in the original analysis (scripts/realclip_2026-11-17/orig_eval.py).
    # The 3D physics check (added later, bounce.py 0.3+) needs a real calibration: with the
    # stand-in camera it rejects the 16.35 s bounce ("behind camera", "turned 70 deg"), so it is off
    # here; it is exercised on calibrated field data (test_samples.py, golden tests).
    cam = Camera.look_at(np.array([0.0, -3.0, 0.6]), np.array([0.0, 1.0, 0.0]), (1080, 1920), hfov_deg=40)
    cfg = BounceConfig(max_court_margin_m=1e6, physics_check=False)
    bd = BounceDetector(cam, dataclasses.replace(CourtSpec(), ball_radius=0.033), cfg)
    out = []
    for x in flights:
        for e in bd.detect(x):
            near = [p.radius_px for p in x.points if abs(p.t - e.t) < 0.03]
            out.append({"t": e.t, "u": e.pixel[0], "v": e.pixel[1], "r": float(np.median(near)), "conf": e.confidence})
    return out


def _found(bounces: list[dict]) -> int:
    return sum(any(abs(b["t"] - t) < 0.02 and b["conf"] >= 0.3 for b in bounces) for t in TRUE_BOUNCES)


def test_clip_metadata_describes_the_original_file():
    v = json.loads((D / "clip_240fps" / "video.json").read_text())
    assert v["codec"] == "hevc" and v["frames"] == 11449
    assert 190 < v["measured_avg_fps"] < 240  # variable frame rate, ~205 fps on average


def test_mac_detector_finds_every_throw_and_matches_the_chalk_marks():
    B = _bounces("mac")
    assert _found(B) == 12
    marks = json.loads((D / "chalk_marks_from_photos.json").read_text())
    errs, prev = [], -1.0
    for mk in marks:
        pt = PHOTO_T[mk["photo"]]
        cand = [b for b in B if prev < b["t"] < pt + 1.0 and b["conf"] >= 0.3]
        prev = pt
        assert cand, mk["photo"]
        b = min(cand, key=lambda b: np.hypot(b["u"] - mk["centroid"][0], b["v"] - mk["centroid"][1]))
        # The tape runs vertically in the image: the horizontal offset is the across-line error.
        errs.append(abs(mk["centroid"][0] - b["u"]) * BALL_RADIUS_CM / b["r"])
    # 9 marks (the photo with two new marks is stored once). Photo 5014's mark is a smear at the
    # powder edge, hence the looser maximum.
    assert np.median(errs) <= 1.0, errs
    assert max(errs) <= 3.0, errs


def test_phone_detector_finds_the_throws_too():
    assert _found(_bounces("phone")) >= 11  # PHASE0_RESULTS.md §7: the same bounces as the Mac detector
