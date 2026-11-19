import json, sys, numpy as np
from balltracker.tracking import Track, TrackPoint
from balltracker.bounce import BounceDetector, BounceConfig, _best_joint, _fit
from balltracker.geometry.camera import Camera
from balltracker.geometry.court import CourtSpec
import dataclasses
T=json.load(open(sys.argv[1]))
cam=Camera.look_at(np.array([0.0,-3.0,0.6]), np.array([0.0,1.0,0.0]), (1080,1920), hfov_deg=40)
court=dataclasses.replace(CourtSpec(), ball_radius=0.033)
bd=BounceDetector(cam, court, BounceConfig(max_court_margin_m=1e6))
res=[]
for k,tr in enumerate(T):
    if np.median([p[4] for p in tr])<15 or len(tr)<12: continue
    trk=Track(k,[TrackPoint(int(p[0]),p[1],p[2],p[3],p[4],1.0) for p in tr])
    evs=bd.detect(trk)
    t=np.array([p[1] for p in tr]); uv=np.array([[p[2],p[3]] for p in tr])
    print(f"flight frames {tr[0][0]}-{tr[-1][0]} n={len(tr)} r~{np.median([p[4] for p in tr]):.0f}px: {len(evs)} bounce(s)")
    for e in evs:
        tb=e.t; fb=tb*120
        # local jitter: joint fit in +-12 frames around the bounce
        m=np.abs(t-tb)<=12/120
        tbl,sse,coef=_best_joint(t[m]-tb, uv[m], -2/120, 2/120)
        rms=np.sqrt(sse/(2*m.sum()-10))
        print(f"   bounce at frame {fb:.2f} (t={tb:.4f}s ±{e.t_std*1000:.1f}ms) pixel ({e.pixel[0]:.1f},{e.pixel[1]:.1f}) conf {e.confidence:.2f}; residual jitter {rms:.2f}px per axis over {m.sum()} pts")
        res.append(dict(track=k, frame=fb, t=tb, t_std=e.t_std, u=e.pixel[0], v=e.pixel[1], r=float(np.median([p[4] for p in tr])), conf=e.confidence, rms=rms))
    if not evs:
        # still report jitter assuming one kink anywhere
        tb,sse,coef=_best_joint(t-t[0],uv,0,t[-1]-t[0],n=40)
        print(f"   (no bounce) best kink fit residual {np.sqrt(sse/(2*len(t)-10)):.2f}px")
json.dump(res,open(sys.argv[2],"w"),indent=1)
