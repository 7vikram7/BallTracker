"""Original 240 fps clip: tracks -> bounces -> compare with chalk marks from photos."""
import json, sys, numpy as np, dataclasses
from balltracker.detection import Candidate
from balltracker.tracking import BallTracker, Track
from balltracker.bounce import BounceDetector, BounceConfig, _best_joint
from balltracker.geometry.camera import Camera
from balltracker.geometry.court import CourtSpec
S=sys.argv[1]
d=json.load(open(f"{S}/orig/det.json")); marks=json.load(open(f"{S}/photos/marks.json"))
photo_t={"5008":7,"5009":11,"5010":18,"5011":28,"5012":35,"5013":39,"5014":43,"5015":52,"5016":55}
tape=json.load(open(f"{S}/clip1/tape.json"))
tr=BallTracker()
for i,t,cs in d["dets"]:
    tr.update(i,t,[Candidate(u,v,r,1.0,np.pi*r*r,1.0) for u,v,r in cs])
T=[x for x in tr.finish() if np.median([p.radius_px for p in x.points])>15 and len(x.points)>=20]
cam=Camera.look_at(np.array([0.0,-3.0,0.6]), np.array([0.0,1.0,0.0]), (1080,1920), hfov_deg=40)
court=dataclasses.replace(CourtSpec(), ball_radius=0.033)
bd=BounceDetector(cam, court, BounceConfig(max_court_margin_m=1e6))
B=[]
for x in T:
    t=np.array([p.t for p in x.points]); uv=np.array([[p.u,p.v] for p in x.points])
    evs=bd.detect(x)
    print(f"flight {x.points[0].frame_index}-{x.points[-1].frame_index} ({t[0]:.2f}-{t[-1]:.2f}s) n={len(t)} r~{np.median([p.radius_px for p in x.points]):.0f}: {len(evs)} bounce(s)")
    for e in evs:
        m=np.abs(t-e.t)<=0.1
        _,sse,_=_best_joint(t[m]-e.t,uv[m],-2/240,2/240)
        rms=float(np.sqrt(sse/(2*m.sum()-10)))
        near=[p.radius_px for p in x.points if abs(p.t-e.t)<0.03]
        r=float(np.median(near))
        B.append(dict(t=e.t,t_std=e.t_std,u=e.pixel[0],v=e.pixel[1],r=r,conf=e.confidence,rms=rms,n=int(m.sum())))
        print(f"   t={e.t:.4f}s ±{e.t_std*1000:.2f}ms pixel ({e.pixel[0]:.1f},{e.pixel[1]:.1f}) r {r:.1f} conf {e.confidence:.2f} jitter {rms:.2f}px over {m.sum()} pts")
json.dump(B,open(f"{S}/orig/bounces.json","w"),indent=1)
# match each photo's mark to the latest floor bounce before the photo (and after the previous photo)
print("\nphoto  mark(px)      bounce t   centre(px)     d_centre(px)  (du,dv)/r")
prev=-1; rows=[]
for mk in marks:
    pt=photo_t[mk["photo"]]
    cand=[b for b in B if prev<b["t"]<pt+1.0 and b["conf"]>=0.3]
    prev=pt
    if not cand: print(mk["photo"],"no bounce"); continue
    # choose the candidate closest to the mark (in px)
    b=min(cand,key=lambda b:np.hypot(b["u"]-mk["centroid"][0],b["v"]-mk["centroid"][1]))
    du=mk["centroid"][0]-b["u"]; dv=mk["centroid"][1]-b["v"]
    rows.append(dict(photo=mk["photo"],mark=mk["centroid"],t=b["t"],u=b["u"],v=b["v"],r=b["r"],du=du,dv=dv,ncand=len(cand)))
    print(f"{mk['photo']}  ({mk['centroid'][0]:.0f},{mk['centroid'][1]:.0f})  {b['t']:8.3f}  ({b['u']:.0f},{b['v']:.0f})  ({du:+.0f},{dv:+.0f})  ({du/b['r']:+.2f},{dv/b['r']:+.2f})  [{len(cand)} cand]")
json.dump(rows,open(f"{S}/orig/matches.json","w"),indent=1)
