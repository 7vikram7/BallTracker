import json, sys, time, numpy as np
from balltracker.video import VideoFileSource
from balltracker.detection import MotionColorBallDetector, DetectorConfig
from balltracker.tracking import BallTracker
src = VideoFileSource(sys.argv[1], fps_override=float(sys.argv[3]) if len(sys.argv)>3 else None)
f0 = next(iter(src.frames()))
print("frame shape", f0.image.shape, "fps", src.info.fps)
det = MotionColorBallDetector(DetectorConfig(hsv_low=(28,110,90), hsv_high=(55,255,255), max_radius_px=80))
tr = BallTracker()
dets = []; t0 = time.time(); n = 0
for f in src.frames():
    c = det.detect(f.image)
    tr.update(f.index, f.t, c)
    dets.append([f.index, f.t, [[float(x.u), float(x.v), float(x.radius_px)] for x in c]])
    n += 1
tracks = tr.finish()
print(f"{n} frames in {time.time()-t0:.0f}s; frames with >=1 cand: {sum(1 for d in dets if d[2])}; tracks: {len(tracks)}")
out = []
for k, T in enumerate(tracks):
    p = T.points
    print(f"track {k}: frames {p[0].frame_index}-{p[-1].frame_index} n={len(p)} path {T.path_length_px():.0f}px speed {T.speed_px_s():.0f}px/s")
    out.append([[q.frame_index, q.t, q.u, q.v] for q in p])
json.dump({"dets": dets, "tracks": out}, open(sys.argv[2], "w"))
