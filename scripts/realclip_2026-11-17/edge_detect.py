"""Run the phone detector (EdgeBallDetector, the C++ app's reference) on the 240 fps original.

Writes the same det.json format as orig_detect.py, so orig_eval.py can score it:
    python scripts/realclip_2026-11-17/edge_detect.py IMG_5017.MOV out_det.json 240 [--native]

--native runs the app's C++ detector (identical results, ~20x faster; see tests/test_edge.py).
"""
import json, sys, time
from balltracker.video import VideoFileSource
from balltracker.edge_detection import EdgeBallDetector, EdgeDetectorConfig
from balltracker.tracking import BallTracker

src = VideoFileSource(sys.argv[1])
cfg = EdgeDetectorConfig(fps=float(sys.argv[3]) if len(sys.argv) > 3 else 240.0)
if "--native" in sys.argv:
    from balltracker.ballcore import NativeDetector
    det = NativeDetector(cfg)
else:
    det = EdgeBallDetector(cfg)
tr = BallTracker()
dets = []; t0 = time.time(); n = 0
for f in src.frames():
    c = det.detect(f.image)
    tr.update(f.index, f.t, c)
    dets.append([f.index, f.t, [[float(x.u), float(x.v), float(x.radius_px)] for x in c]])
    n += 1
tracks = tr.finish()
print(f"{n} frames in {time.time()-t0:.0f}s ({(time.time()-t0)/n*1e3:.1f} ms/frame); frames with >=1 cand: "
      f"{sum(1 for d in dets if d[2])}; tracks: {len(tracks)}")
json.dump({"dets": dets}, open(sys.argv[2], "w"))
