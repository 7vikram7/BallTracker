import json, numpy as np, cv2, sys
from balltracker.video import VideoFileSource
S=sys.argv[1]
B=json.load(open(f"{S}/clip1/bounces.json"))
src=VideoFileSource("TestData/iPhone17SlowMo/SlowMo.MOV", fps_override=120)
want={int(round(b["frame"])) for b in B} | {int(np.floor(b["frame"])) for b in B} | {1650} | set(range(2200,2212))
imgs={}
for f in src.frames():
    if f.index in want: imgs[f.index]=f.image.copy()
    if f.index>max(want): break
# tape: red pixels on the floor, per row left/right extents
ref=imgs[1650]; hsv=cv2.cvtColor(ref,cv2.COLOR_BGR2HSV)
red=(((hsv[...,0]<10)|(hsv[...,0]>168))&(hsv[...,1]>90)&(hsv[...,2]>70)).astype(np.uint8)
red[:880]=0
ys,xs=np.nonzero(red)
# robust line x = a*y + b: iterate fit + inlier selection
a,b=np.polyfit(ys,xs,1)
for tol in (120,60,30,20):
    m=np.abs(xs-(a*ys+b))<tol; a,b=np.polyfit(ys[m],xs[m],1)
m=np.abs(xs-(a*ys+b))<20
rows=[];L=[];R=[]
for y in np.unique(ys[m]):
    xx=xs[m][ys[m]==y]
    if len(xx)>=4: rows.append(y); L.append(np.percentile(xx,3)); R.append(np.percentile(xx,97)+1)
rows=np.array(rows); L=np.array(L); R=np.array(R)
pl=np.polyfit(rows,L,1); pr=np.polyfit(rows,R,1)
for _ in range(2):
    k=(np.abs(L-np.polyval(pl,rows))<4)&(np.abs(R-np.polyval(pr,rows))<4)
    pl=np.polyfit(rows[k],L[k],1); pr=np.polyfit(rows[k],R[k],1)
print(f"tape rows {rows.min()}-{rows.max()}, width px at top {np.polyval(pr,rows.min())-np.polyval(pl,rows.min()):.1f} at bottom {np.polyval(pr,rows.max())-np.polyval(pl,rows.max()):.1f}")
json.dump(dict(left=pl.tolist(),right=pr.tolist(),rows=[int(rows.min()),int(rows.max())]),open(f"{S}/clip1/tape.json","w"))
crops=[]
for b in B:
    fi=int(round(b["frame"])); img=imgs[fi].copy()
    u,v,r=b["u"],b["v"],b["r"]
    cu,cv_=u,v+0.95*r  # contact point approx below centre
    xl=np.polyval(pl,cv_); xr=np.polyval(pr,cv_)
    # signed gap from tape's right edge to ball's nearest edge (ball as ruler: 6.7 cm diameter)
    cm_per_px=3.35/r
    if cu>xr: gap=(cu-r)-xr; side="right"
    elif cu<xl: gap=xl-(cu+r); side="left"
    else: gap=-1; side="on"
    b.update(side=side, gap_px=float(gap), gap_cm=float(gap*cm_per_px), contact=[cu,cv_])
    for y0,y1 in ((850,1500),):
        for p,c in ((pl,(255,0,255)),(pr,(255,0,255))):
            cv2.line(img,(int(np.polyval(p,y0)),y0),(int(np.polyval(p,y1)),y1),c,1)
    cv2.circle(img,(int(u),int(v)),int(r),(0,255,255),1); cv2.drawMarker(img,(int(cu),int(cv_)),(0,0,255),cv2.MARKER_CROSS,14,2)
    x0=int(max(0,min(cu,xl)-120)); x1=int(min(img.shape[1],max(cu,xr)+120)); y0=int(max(0,cv_-170)); y1=int(min(img.shape[0],cv_+90))
    c=img[y0:y1,x0:x1]; c=cv2.resize(c,(int(c.shape[1]*260/c.shape[0]),260))
    cv2.putText(c,f"f{b['frame']:.1f} {side} {gap*cm_per_px:.1f}cm",(5,20),cv2.FONT_HERSHEY_SIMPLEX,0.6,(255,255,255),2)
    crops.append(c)
    print(f"bounce frame {b['frame']:7.2f} conf {b['conf']:.2f}: contact ({cu:.0f},{cv_:.0f}) -> {side} of tape, gap {gap:.0f}px ~ {gap*cm_per_px:.1f} cm")
json.dump(B,open(f"{S}/clip1/bounces.json","w"),indent=1)
H=max(c.shape[0] for c in crops); row=np.hstack([cv2.copyMakeBorder(c,0,H-c.shape[0],0,4,cv2.BORDER_CONSTANT) for c in crops])
cv2.imwrite(f"{S}/clip1/bounce_crops.jpg",row)
seq=np.hstack([cv2.resize(imgs[i][500:1300,:],(270,200)) for i in range(2200,2212,1)])
cv2.imwrite(f"{S}/clip1/seq2206.jpg",seq)
