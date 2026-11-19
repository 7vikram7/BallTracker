import numpy as np, cv2, sys, json
from balltracker.video import VideoFileSource
S=sys.argv[1]; D="TestData/iPhone17SlowMo"
base=next(iter(VideoFileSource(f"{D}/AllPhotosData/IMG_5017.MOV").frames(start_s=0.3))).image
imgs=[("start",base)]+[(f"50{i:02d}",cv2.imread(f"{D}/IMG_50{i:02d}/IMG_50{i:02d}.JPG")) for i in range(8,17)]
ref=cv2.cvtColor(imgs[-1][1],cv2.COLOR_BGR2GRAY).astype(np.float32)
def align(im):
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(np.float32)
    W=np.eye(2,3,dtype=np.float32)
    try:
        _,W=cv2.findTransformECC(cv2.GaussianBlur(ref,(0,0),2),cv2.GaussianBlur(g,(0,0),2),W,cv2.MOTION_EUCLIDEAN,(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,100,1e-5),None,5)
    except cv2.error: pass
    return cv2.warpAffine(im,W,(im.shape[1],im.shape[0]),flags=cv2.INTER_LINEAR+cv2.WARP_INVERSE_MAP),W
def yellow(im):
    lab=cv2.cvtColor(im,cv2.COLOR_BGR2LAB).astype(np.float32)
    b=lab[...,2]-np.median(lab[900:1400,:,2]); return cv2.GaussianBlur(b,(0,0),3)
Y=[];A=[]
for n,im in imgs:
    a,W=align(im); A.append(a); Y.append(yellow(a)); print(n,"shift px",W[:,2].round(1),"rot",round(float(np.degrees(np.arctan2(W[1,0],W[0,0]))),3))
roi=np.zeros(base.shape[:2],bool); roi[930:1330,330:1000]=True
res=[];tiles=[]
for k in range(1,len(imgs)):
    d=(Y[k-1]-Y[k]); d[~roi]=0  # yellow removed
    d=cv2.GaussianBlur(d,(0,0),4)
    y,x=np.unravel_index(np.argmax(d),d.shape); pk=d[y,x]
    m=(d>0.5*pk).astype(np.uint8); n_,lab,st,cen=cv2.connectedComponentsWithStats(m)
    j=lab[y,x]; x0,y0,w,h,area=st[j]
    snr=pk/np.std(d[roi])
    res.append(dict(photo=imgs[k][0],peak=[int(x),int(y)],centroid=[float(cen[j][0]),float(cen[j][1])],box=[int(x0),int(y0),int(w),int(h)],snr=float(snr)))
    print(f"{imgs[k-1][0]}->{imgs[k][0]}: biggest yellow loss at ({x},{y}) centroid ({cen[j][0]:.0f},{cen[j][1]:.0f}) box {w}x{h} snr {snr:.1f}")
    vis=A[k][880:1380,280:1040].copy(); cv2.rectangle(vis,(x0-280-6,y0-880-6),(x0-280+w+6,y0-880+h+6),(255,0,255),2)
    prev=A[k-1][880:1380,280:1040].copy()
    cv2.putText(prev,imgs[k-1][0],(8,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2); cv2.putText(vis,imgs[k][0],(8,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
    tiles.append(np.hstack([prev,vis]))
json.dump(res,open(f"{S}/photos/marks.json","w"),indent=1)
for i in range(0,9,3): cv2.imwrite(f"{S}/photos/pairs{i//3}.jpg",cv2.resize(np.vstack(tiles[i:i+3]),None,fx=0.75,fy=0.75))
