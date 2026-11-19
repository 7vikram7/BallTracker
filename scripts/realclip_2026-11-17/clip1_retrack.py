import json, sys, numpy as np
from balltracker.detection import Candidate
from balltracker.tracking import BallTracker
d=json.load(open(sys.argv[1]))
tr=BallTracker()
for i,t,cs in d["dets"]:
    tr.update(i,t,[Candidate(u,v,r,1.0,np.pi*r*r,1.0) for u,v,r in cs])
T=tr.finish()
out=[[[q.frame_index,q.t,q.u,q.v,q.radius_px] for q in x.points] for x in T]
json.dump(out,open(sys.argv[2],"w"))
for k,x in enumerate(T):
    if x.path_length_px()>150: print(f"track {k}: frames {x.points[0].frame_index}-{x.points[-1].frame_index} n={len(x.points)} path {x.path_length_px():.0f} r~{np.median([q.radius_px for q in x.points]):.0f}")
print("tracks", len(T))
