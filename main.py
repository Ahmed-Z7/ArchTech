"""
================================================================
  HAND GESTURE AR v6.0 — Holographic Edition
  Made by Mohamed Mohamed Lotfy & Mennat Allah Mohamed Lotfy
================================================================
"""
import cv2
import mediapipe as mp
import numpy as np
import time, math
from collections import deque

CAM=0;W,H=1280,720;DWELL=1.0;ER_R=45;DT=5
FONT=cv2.FONT_HERSHEY_SIMPLEX;STABLE_N=5;EXIT_S=1.5;MAX_UNDO=15
MENU,DRAW,PICKER,HOLO3D,PORTAL=0,1,2,3,4
C_BG=(12,12,20);C_CY=(255,200,0);C_MG=(200,100,255);C_GN=(100,255,180)
C_RD=(80,80,255);C_WH=(255,255,255);C_GR=(140,140,160);C_PN=(25,25,45)
C_GO=(0,215,255);C_DR=(0,220,255);C_PR=(255,100,100)
mp_h=mp.solutions.hands;mp_du=mp.solutions.drawing_utils;mp_st=mp.solutions.drawing_styles
TIPS=[4,8,12,16,20]

# ============ GESTURE ============
def fst(hlm,hd):
    lm=hlm.landmark;f=[]
    f.append(1 if(lm[4].x<lm[3].x if hd=="Right" else lm[4].x>lm[3].x)else 0)
    for t in TIPS[1:]:f.append(1 if lm[t].y<lm[t-2].y else 0)
    return f
def tpx(hlm,tid,w,h):
    l=hlm.landmark[tid];return int(l.x*w),int(l.y*h)
def pinch_dist(hlm,w,h):
    t=hlm.landmark[4];i=hlm.landmark[8]
    return math.sqrt((t.x*w-i.x*w)**2+(t.y*h-i.y*h)**2)
def palm_center(hlm,w,h):
    lm=hlm.landmark;x=int(lm[9].x*w);y=int(lm[9].y*h);return(x,y)
def clas(f):
    s=sum(f)
    if s==0:return"FIST"
    if s==5:return"PALM"
    if s==1 and f[1]:return"INDEX"
    if s==2 and f[1] and f[2]:return"TWO"
    if s==3 and f[1] and f[2] and f[3]:return"THREE"
    if s==4 and f[0] and f[1] and f[2] and f[3]:return"FOUR"
    return"OTHER"
class Stab:
    def __init__(s,n=STABLE_N):s.n=n;s.c=s.p="NONE";s.cnt=0
    def u(s,g):
        if g==s.p:s.cnt+=1
        else:s.p=g;s.cnt=1
        if s.cnt>=s.n:s.c=s.p
        return s.c
    def r(s):s.c=s.p="NONE";s.cnt=0
class Smo:
    def __init__(s,a=0.45):s.a=a;s.p=None
    def u(s,r):
        if s.p is None:s.p=r
        else:s.p=(int(s.a*r[0]+(1-s.a)*s.p[0]),int(s.a*r[1]+(1-s.a)*s.p[1]))
        return s.p
    def r(s):s.p=None
class ExD:
    def __init__(s):s.t=None
    def u(s,nh,af):
        if nh>=2 and len(af)>=2 and sum(af[0])+sum(af[1])>=9:
            if s.t is None:s.t=time.time()
        else:s.t=None
    def ok(s):return s.t is not None and(time.time()-s.t)>=EXIT_S
    def pr(s):return min((time.time()-s.t)/EXIT_S,1.0)if s.t else 0.0
    def r(s):s.t=None

# ============ UI ============
def orect(img,x1,y1,x2,y2,c,a=0.6):
    y1c,y2c=max(y1,0),min(y2,H);x1c,x2c=max(x1,0),min(x2,W)
    if y2c<=y1c or x2c<=x1c:return
    sub=img[y1c:y2c,x1c:x2c];r=np.full_like(sub,c,np.uint8);cv2.addWeighted(r,a,sub,1-a,0,sub)
def neon(img,x1,y1,x2,y2,c,t=2):
    for i in range(3,0,-1):
        cc=tuple(min(255,v+25*i)for v in c);cv2.rectangle(img,(x1-i,y1-i),(x2+i,y2+i),cc,1,cv2.LINE_AA)
    cv2.rectangle(img,(x1,y1),(x2,y2),c,t,cv2.LINE_AA)
def ptx(img,t,p,s=0.6,c=C_WH,th=1,sh=True):
    if sh:cv2.putText(img,t,(p[0]+1,p[1]+1),FONT,s,(0,0,0),th+1,cv2.LINE_AA)
    cv2.putText(img,t,p,FONT,s,c,th,cv2.LINE_AA)
def pc(img,t,cx,cy,s=0.8,c=C_WH,th=2):
    (tw,tth),_=cv2.getTextSize(t,FONT,s,th);ptx(img,t,(cx-tw//2,cy+tth//2),s,c,th)
def parc(img,cx,cy,p,r=28,c=C_CY):
    a=int(360*min(p,1.0))
    for i in range(3,0,-1):
        cc=tuple(min(255,v+20*i)for v in c);cv2.ellipse(img,(cx,cy),(r+i*2,r+i*2),-90,0,a,cc,1,cv2.LINE_AA)
    cv2.ellipse(img,(cx,cy),(r,r),-90,0,a,c,3,cv2.LINE_AA)
def cur(img,p,c=C_CY,r=10):
    cx,cy=p;g=4
    cv2.circle(img,(cx,cy),r+6,c,1,cv2.LINE_AA)
    for dx,dy in[(-r-10,0),(-g,0),(g,0),(r+10,0),(0,-r-10),(0,-g),(0,g),(0,r+10)]:
        pass
    cv2.line(img,(cx-r-10,cy),(cx-g,cy),c,1,cv2.LINE_AA)
    cv2.line(img,(cx+g,cy),(cx+r+10,cy),c,1,cv2.LINE_AA)
    cv2.line(img,(cx,cy-r-10),(cx,cy-g),c,1,cv2.LINE_AA)
    cv2.line(img,(cx,cy+g),(cx,cy+r+10),c,1,cv2.LINE_AA)
    cv2.circle(img,(cx,cy),3,c,-1,cv2.LINE_AA)
def scanl(img):
    o=np.zeros_like(img)
    for y in range(0,H,4):cv2.line(o,(0,y),(W,y),(40,40,40),1)
    cv2.addWeighted(o,0.02,img,1.0,0,img)
def corners(img,c):
    for p0,p1,p2 in[((5,5),(30,5),(5,30)),((W-5,5),(W-30,5),(W-5,30)),((5,H-5),(30,H-5),(5,H-30)),((W-5,H-5),(W-30,H-5),(W-5,H-30))]:
        cv2.line(img,p0,p1,c,1,cv2.LINE_AA);cv2.line(img,p0,p2,c,1,cv2.LINE_AA)
def hud(fr,mode,fps,gest,hint=""):
    mc={"MENU":C_CY,"DRAW":C_GN,"PICKER":C_MG,"3D HOLO":C_GO,"PORTAL":C_PR}.get(mode,C_GR)
    orect(fr,W-240,10,W-10,52,C_BG,0.75);neon(fr,W-240,10,W-10,52,mc,1)
    pc(fr,mode,W-125,31,0.6,mc,2)
    fc=C_GN if fps>=25 else C_CY if fps>=15 else C_RD
    ptx(fr,f"FPS {fps}",(W-100,72),0.5,fc,1,False)
    orect(fr,5,H-55,380,H-5,C_BG,0.6)
    ptx(fr,f"Gesture: {gest}",(12,H-35),0.45,mc,1,False)
    if hint:ptx(fr,hint,(12,H-14),0.38,C_GR,1,False)
    corners(fr,mc)
def exit_ov(fr,ep):
    if ep>0:parc(fr,W//2,45,ep,30,C_RD);pc(fr,f"EXIT {int(ep*100)}%",W//2,90,0.5,C_RD,2)

# ============ MENU ============
B1=(W//2-430,200,W//2-20,278);B2=(W//2+20,200,W//2+430,278)
B3=(W//2-430,298,W//2-20,376);B4=(W//2+20,298,W//2+430,376)
def render_menu(fr,hov,dp,bc):
    orect(fr,0,0,W,H,C_BG,0.55)
    pc(fr,"GESTURE AR SYSTEM",W//2,90,1.3,C_CY,3)
    pc(fr,"v6.0 HOLOGRAPHIC | Point & Hold",W//2,125,0.5,C_GR,1)
    pc(fr,"Made by: Mohamed & Mennat Allah",W//2,155,0.45,C_GO,1)
    bx=W//2+260;cv2.rectangle(fr,(bx,95),(bx+35,125),bc,-1);neon(fr,bx,95,bx+35,125,C_WH,1)
    btns=[("draw",B1,"AIR PAINTER","Draw in air with gestures",C_GN),
          ("picker",B2,"COLOR PICKER","Pick & save colors",C_MG),
          ("holo",B3,"3D HOLOGRAM","Interactive 3D wireframes",C_GO),
          ("portal",B4,"MAGIC PORTAL","Dr. Strange AR FX",C_PR)]
    for k,r,lab,sub,c in btns:
        x1,y1,x2,y2=r;ih=(hov==k)
        orect(fr,x1,y1,x2,y2,c if ih else C_PN,0.65 if ih else 0.45)
        neon(fr,x1,y1,x2,y2,c if ih else(40,40,60),2 if ih else 1)
        pc(fr,lab,(x1+x2)//2,(y1+y2)//2-8,0.75,C_WH if ih else C_GR,2)
        pc(fr,sub,(x1+x2)//2,y2-12,0.35,c,1)
        if ih and dp>0:parc(fr,(x1+x2)//2,y1-20,dp,16,c)
def ptin(p,r):return r[0]<=p[0]<=r[2] and r[1]<=p[1]<=r[3]

# ============ CANVAS ============
class Canvas:
    def __init__(s):
        s.c=np.zeros((H,W,3),np.uint8);s.prev=None;s.col=C_DR;s.paused=False
        s.hist=[];s.hmax=MAX_UNDO;s.show_hist=False;s._scd=0
    def draw(s,p):
        if s.paused:return
        if s.prev:
            cv2.line(s.c,s.prev,p,s.col,DT,cv2.LINE_AA)
            gc=tuple(min(255,v+50)for v in s.col)
            cv2.line(s.c,s.prev,p,gc,DT+4,cv2.LINE_AA)
            cv2.addWeighted(s.c,0.88,s.c,0.12,0,s.c)
        s.prev=p
    def lift(s):s.prev=None
    def erase(s,p):
        if not s.paused:cv2.circle(s.c,p,ER_R,(0,0,0),-1)
    def snap(s):
        if s._scd>0:return
        if len(s.hist)>=s.hmax:s.hist.pop(0)
        s.hist.append(s.c.copy());s._scd=20
    def undo(s):
        if s.hist:s.c=s.hist.pop()
        else:s.c[:]=0
    def clear(s):s.snap();s.c[:]=0;s.prev=None
    def tick(s):
        if s._scd>0:s._scd-=1
    def blend(s,fr):
        g=cv2.cvtColor(s.c,cv2.COLOR_BGR2GRAY);_,m=cv2.threshold(g,5,255,cv2.THRESH_BINARY)
        m3=cv2.merge([m]*3);np.copyto(fr,s.c,where=(m3>0))
    def render_hist(s,fr):
        if not s.hist:
            orect(fr,W//2-150,H//2-30,W//2+150,H//2+30,C_BG,0.85)
            pc(fr,"No history yet",W//2,H//2,0.6,C_GR,1);return
        n=min(len(s.hist),5);tw_,th_=140,80;gap=12;total=n*(tw_+gap)-gap
        sx=W//2-total//2;sy=H//2-th_//2-30
        orect(fr,sx-15,sy-40,sx+total+15,sy+th_+50,C_BG,0.9)
        neon(fr,sx-15,sy-40,sx+total+15,sy+th_+50,C_CY,1)
        pc(fr,f"SAVED DRAWINGS ({len(s.hist)})",W//2,sy-18,0.5,C_CY,2)
        for i in range(n):
            idx=len(s.hist)-1-i;thumb=cv2.resize(s.hist[idx],(tw_,th_))
            x=sx+i*(tw_+gap)
            fr[sy:sy+th_,x:x+tw_]=np.where(thumb>0,thumb,fr[sy:sy+th_,x:x+tw_])
            neon(fr,x,sy,x+tw_,sy+th_,(80,80,120),1)

# ============ COLOR PICKER ============
def gen_wheel(sz=280):
    img=np.zeros((sz,sz,3),np.uint8);cx,cy=sz//2,sz//2;r=sz//2-10
    for y in range(sz):
        for x in range(sz):
            dx,dy=x-cx,y-cy;d=math.sqrt(dx*dx+dy*dy)
            if d<=r:img[y,x]=[int((math.atan2(dy,dx)/math.pi*0.5+0.5)*180)%180,int(d/r*255),255]
    return cv2.cvtColor(img,cv2.COLOR_HSV2BGR)
CWHEEL=gen_wheel(280)

class Picker:
    def __init__(s,bc):
        s.pal=[];s.rgb=(128,128,128);s.bgr=bc;s.live=False
        s.show_pal=False;s.show_whl=False;s.mx=12;s._cd=0;s.ph=-1
    def samp(s,cl,p):
        x=np.clip(p[0],0,cl.shape[1]-1);y=np.clip(p[1],0,cl.shape[0]-1)
        b,g,r=cl[y,x];s.rgb=(int(r),int(g),int(b))
    def samp_whl(s,p):
        wx,wy=W//2-140,H//2-140;lx,ly=p[0]-wx,p[1]-wy
        if 0<=lx<280 and 0<=ly<280:
            b,g,r=CWHEEL[ly,lx]
            if not(b==0 and g==0 and r==0):s.rgb=(int(r),int(g),int(b));return True
        return False
    def save(s):
        if s._cd>0:return
        if len(s.pal)<s.mx and s.rgb not in s.pal:s.pal.append(s.rgb);s._cd=15
    def sel(s,i):
        if 0<=i<len(s.pal):s.rgb=s.pal[i];r,g,b=s.rgb;s.bgr=(b,g,r)
    def applyb(s):r,g,b=s.rgb;s.bgr=(b,g,r)
    def tick(s):
        if s._cd>0:s._cd-=1
    def swatches(s):
        cols,sz,gap=6,48,7;sx0=W//2-(cols*(sz+gap))//2;sy0=H-160
        return[(sx0+i%cols*(sz+gap),sy0+i//cols*(sz+gap),sx0+i%cols*(sz+gap)+sz,sy0+i//cols*(sz+gap)+sz,i)for i in range(len(s.pal))]
    def render(s,fr,tip):
        orect(fr,12,12,375,210,C_PN,0.8);neon(fr,12,12,375,210,C_MG,1)
        r,g,b=s.rgb;cv2.rectangle(fr,(22,28),(100,85),(b,g,r),-1);neon(fr,22,28,100,85,C_WH,1)
        ptx(fr,f"R:{r:3d} G:{g:3d} B:{b:3d}",(110,48),0.45,(200,220,255),1)
        ptx(fr,f"#{r:02X}{g:02X}{b:02X}",(110,72),0.6,C_WH,2)
        cv2.rectangle(fr,(280,28),(340,85),s.bgr,-1);neon(fr,280,28,340,85,C_GN,1)
        ptx(fr,"BRUSH",(283,100),0.35,C_GN,1,False)
        ht=[("1f=Palette",C_CY),("2f=Scan",C_MG),("3f=Save",C_GN),("4f=Wheel",C_GO),("5f=Palette view",C_WH)]
        for i,(h,c) in enumerate(ht):ptx(fr,h,(22,115+i*17),0.35,c,1,False)
        if s.live:ptx(fr,"SCANNING",(W-170,35),0.6,(0,int(128+127*math.sin(time.time()*6)),120),2)
        if tip:cur(fr,tip,(b,g,r),12)
        if s.show_pal and s.pal:s._dpal(fr)
        if s.show_whl:s._dwhl(fr)
    def _dpal(s,fr):
        cols,sz,gap=6,48,7;sx0=W//2-(cols*(sz+gap))//2;sy0=H-160
        pw=cols*(sz+gap)+gap;rows=(len(s.pal)-1)//cols+1;ph=rows*(sz+gap)+gap+30
        orect(fr,sx0-gap,sy0-30,sx0+pw,sy0+ph,C_BG,0.88);neon(fr,sx0-gap,sy0-30,sx0+pw,sy0+ph,C_MG,1)
        ptx(fr,"SAVED PALETTE",(sx0,sy0-10),0.42,C_MG,1,False)
        for i,(r,g,b) in enumerate(s.pal):
            c_,ro=i%cols,i//cols;x=sx0+c_*(sz+gap);y=sy0+ro*(sz+gap)
            cv2.rectangle(fr,(x,y),(x+sz,y+sz),(b,g,r),-1)
            cv2.rectangle(fr,(x,y),(x+sz,y+sz),C_CY if i==s.ph else(50,50,70),3 if i==s.ph else 1)
    def _dwhl(s,fr):
        wx,wy=W//2-140,H//2-140
        orect(fr,wx-15,wy-40,wx+295,wy+310,C_BG,0.9);neon(fr,wx-15,wy-40,wx+295,wy+310,C_GO,1)
        pc(fr,"COLOR WHEEL",W//2,wy-18,0.55,C_GO,2)
        ptx(fr,"2 fingers to pick",(wx,wy+295),0.4,C_GR,1,False)
        region=fr[wy:wy+280,wx:wx+280];np.copyto(region,CWHEEL,where=(CWHEEL>0))

# ============ 3D SHAPES ============
def mk_cube():
    v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],float)
    e=[(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)];return v,e
def mk_icosa():
    phi=(1+math.sqrt(5))/2;v=[]
    for s1 in[-1,1]:
        for s2 in[-1,1]:
            v+=[[0,s1,s2*phi],[s1,s2*phi,0],[s2*phi,0,s1]]
    v=np.array(v,float);v/=np.linalg.norm(v[0])
    e=[];n=len(v)
    for i in range(n):
        dists=[(np.linalg.norm(v[i]-v[j]),j)for j in range(n)if j!=i]
        dists.sort();nn=[d[1]for d in dists[:5]]
        for j in nn:
            if(i,j)not in e and(j,i)not in e:e.append((i,j))
    return v,e
def mk_torus(R=1.2,r_=0.5,n1=16,n2=10):
    v=[];e=[]
    for i in range(n1):
        a=2*math.pi*i/n1
        for j in range(n2):
            b=2*math.pi*j/n2
            x=(R+r_*math.cos(b))*math.cos(a);y=(R+r_*math.cos(b))*math.sin(a);z=r_*math.sin(b)
            v.append([x,y,z])
    v=np.array(v,float)
    for i in range(n1):
        for j in range(n2):
            cur_=i*n2+j;nxt_j=i*n2+(j+1)%n2;nxt_i=((i+1)%n1)*n2+j
            e.append((cur_,nxt_j));e.append((cur_,nxt_i))
    return v,e
def mk_star():
    v=[[0,2,0]];n=8
    for i in range(n):
        a=2*math.pi*i/n;r_=1.5 if i%2==0 else 0.7
        v.append([r_*math.cos(a),0,r_*math.sin(a)])
    v.append([0,-2,0])
    v=np.array(v,float)
    e=[(0,i+1)for i in range(n)]+[(len(v)-1,i+1)for i in range(n)]
    e+=[(i+1,(i+1)%n+1)for i in range(n)]
    return v,e
def mk_helix(turns=3,pts=60,r_=1.0):
    v=[];e=[]
    for i in range(pts):
        t=i/pts*turns*2*math.pi;y=-1.5+3*i/pts
        v.append([r_*math.cos(t),y,r_*math.sin(t)])
    v=np.array(v,float)
    for i in range(pts-1):e.append((i,i+1))
    return v,e
def mk_diamond():
    v=np.array([[0,1.8,0],[-1,0.3,-1],[1,0.3,-1],[1,0.3,1],[-1,0.3,1],
                [-0.6,-0.3,-0.6],[0.6,-0.3,-0.6],[0.6,-0.3,0.6],[-0.6,-0.3,0.6],[0,-1.5,0]],float)
    e=[(0,1),(0,2),(0,3),(0,4),(1,2),(2,3),(3,4),(4,1),(1,5),(2,6),(3,7),(4,8),
       (5,6),(6,7),(7,8),(8,5),(9,5),(9,6),(9,7),(9,8)]
    return v,e

SHAPES=[("CUBE",mk_cube),("ICOSAHEDRON",mk_icosa),("TORUS",mk_torus),
        ("STAR",mk_star),("HELIX",mk_helix),("DIAMOND",mk_diamond)]

def rx(a):c,s=math.cos(a),math.sin(a);return np.array([[1,0,0],[0,c,-s],[0,s,c]])
def ry(a):c,s=math.cos(a),math.sin(a);return np.array([[c,0,s],[0,1,0],[-s,0,c]])
def rz(a):c,s=math.cos(a),math.sin(a);return np.array([[c,-s,0],[s,c,0],[0,0,1]])
def proj(v3,cx,cy,fov=500,d=5):
    pts=[]
    for v in v3:
        z_=v[2]+d;z_=max(z_,0.1);pts.append((int(cx+v[0]*fov/z_),int(cy-v[1]*fov/z_)))
    return pts

class Holo3D:
    def __init__(s):
        s.si=0;s.trx=0.3;s.try_=0.5;s.trz=0;s.scale=1.5
        s.auto=True;s.trail=deque(maxlen=80)
        s.trans_off=0.0;s._cd=0
        s.base_pinch=None;s.base_scale=1.5
        s.palm_base=None;s.base_rx=0.3;s.base_ry=0.5
        s.show_list=False;s.list_hover=-1
        s.morph_t=0
    def reset_pose(s):
        s.trx=0.3;s.try_=0.5;s.trz=0;s.scale=1.5;s.auto=True
    def select_shape(s,idx):
        if idx!=s.si:s.morph_t=1.0;s.si=idx
        s.show_list=False
    def tick(s,dt):
        if s._cd>0:s._cd-=1
        if s.auto and not s.show_list:s.try_+=0.6*dt;s.trx+=0.2*dt
        if abs(s.trans_off)>0.01:s.trans_off*=0.85
        else:s.trans_off=0
        if s.morph_t>0:s.morph_t=max(0,s.morph_t-dt*2.5)
    def render(s,fr,tp,sg,hlm0):
        name,fn=SHAPES[s.si];verts,edges=fn()
        anim_scale=1.0-s.morph_t if s.morph_t>0 else 1.0
        v=verts*s.scale*anim_scale;R=rx(s.trx)@ry(s.try_)@rz(s.trz);v=v@R.T
        cx_=int(W//2+s.trans_off);cy_=H//2
        pts=proj(v,cx_,cy_)
        t_=time.time()
        for idx,(i,j) in enumerate(edges):
            hue=(t_*30+idx*20)%180
            hsv=np.uint8([[[int(hue),200,255]]]);bgr=cv2.cvtColor(hsv,cv2.COLOR_HSV2BGR)[0][0]
            c=tuple(int(x)for x in bgr)
            for g in range(3,0,-1):
                gc=tuple(min(255,v_+20*g)for v_ in c)
                cv2.line(fr,pts[i],pts[j],gc,g*2,cv2.LINE_AA)
            cv2.line(fr,pts[i],pts[j],c,2,cv2.LINE_AA)
        for p in pts:
            cv2.circle(fr,p,4,C_WH,-1,cv2.LINE_AA);cv2.circle(fr,p,7,C_CY,1,cv2.LINE_AA)
        if tp and sg=="INDEX" and not s.show_list:s.trail.append((tp,time.time()))
        trpts=[(p,t)for p,t in s.trail if time.time()-t<1.5]
        for i_ in range(1,len(trpts)):
            age=1.0-(time.time()-trpts[i_][1])/1.5
            cv2.line(fr,trpts[i_-1][0],trpts[i_][0],tuple(int(v_*age)for v_ in C_CY),max(1,int(3*age)),cv2.LINE_AA)
        if s.show_list:s._draw_list(fr)
        orect(fr,12,12,340,145,C_PN,0.8);neon(fr,12,12,340,145,C_GO,1)
        ptx(fr,"3D HOLOGRAM VIEWER",(22,35),0.55,C_GO,2)
        ptx(fr,f"Shape: {name} ({s.si+1}/{len(SHAPES)})",(22,58),0.42,C_CY,1,False)
        ptx(fr,f"Scale: {s.scale:.1f}x | Auto: {'ON' if s.auto else 'OFF'}",(22,78),0.38,C_GN,1,False)
        ptx(fr,"PALM=Control | PINCH=Scale",(22,98),0.34,C_GR,1,False)
        ptx(fr,"FIST=Shapes | THREE=Reset",(22,116),0.34,C_GR,1,False)
        ptx(fr,"INDEX=Trail",(22,134),0.34,C_GR,1,False)
        for i_ in range(len(SHAPES)):
            bx=W//2-len(SHAPES)*12+i_*24;by=H-30
            c_=C_GO if i_==s.si else(60,60,80)
            cv2.circle(fr,(bx,by),6,c_,-1 if i_==s.si else 1,cv2.LINE_AA)
    def _draw_list(s,fr):
        cols=3;sz_w=180;sz_h=60;gap=10
        rows=(len(SHAPES)+cols-1)//cols
        tw=cols*(sz_w+gap)-gap;th=rows*(sz_h+gap)-gap
        ox=W//2-tw//2;oy=H//2-th//2-20
        orect(fr,ox-20,oy-45,ox+tw+20,oy+th+35,C_BG,0.92)
        neon(fr,ox-20,oy-45,ox+tw+20,oy+th+35,C_GO,1)
        pc(fr,"SELECT SHAPE",W//2,oy-22,0.55,C_GO,2)
        s._list_rects=[]
        for i,(nm,_) in enumerate(SHAPES):
            c_=i%cols;ro=i//cols;x=ox+c_*(sz_w+gap);y=oy+ro*(sz_h+gap)
            ih=(i==s.list_hover);act=(i==s.si)
            bg=C_GO if ih else(C_PN if not act else(40,60,50))
            orect(fr,x,y,x+sz_w,y+sz_h,bg,0.7)
            brd=C_GO if ih else(C_GN if act else(50,50,70))
            neon(fr,x,y,x+sz_w,y+sz_h,brd,2 if ih else 1)
            tc=C_WH if ih else(C_GN if act else C_GR)
            pc(fr,nm,(x+sz_w//2),(y+sz_h//2),0.5,tc,2 if ih else 1)
            s._list_rects.append((x,y,x+sz_w,y+sz_h,i))
    def list_rects(s):
        return getattr(s,'_list_rects',[])

PORTAL_STYLES = ["DR. STRANGE", "ARC REACTOR", "CYBER HEX"]
class MagicPortal:
    def __init__(s):
        s.t=0;s.particles=[];s.si=0;s.show_list=False;s.lhov=-1;s._cd=0
    def tick(s,dt):
        s.t+=dt*2
        if s._cd>0:s._cd-=1
    def render(s,fr,tp,sg,hlm0):
        if np.random.rand()<0.15:s.particles.append([np.random.randint(0,W),np.random.randint(0,H),(np.random.rand()-0.5)*4,(np.random.rand()-0.5)*4,np.random.randint(50,150)])
        orect(fr,12,12,340,135,C_PN,0.8);neon(fr,12,12,340,135,C_PR,1)
        ptx(fr,"MAGIC PORTAL",(22,35),0.55,C_PR,2)
        ptx(fr,f"Style: {PORTAL_STYLES[s.si]}",(22,58),0.42,C_CY,1,False)
        ptx(fr,"PALM=Effect | FIST=Black Hole",(22,78),0.38,C_GN,1,False)
        ptx(fr,"FOUR=Setup Menu",(22,98),0.38,C_GR,1,False)
        
        c_1=(0,165,255)if s.si==0 else((255,200,50)if s.si==1 else(50,255,50))
        c_2=(50,200,255)if s.si==0 else((255,255,255)if s.si==1 else(255,50,255))
        c_3=(0,100,255)if s.si==0 else((200,100,0)if s.si==1 else(0,150,50))
        
        if sg=="PALM" and hlm0 and not s.show_list:
            cx,cy=palm_center(hlm0,W,H)
            for i in range(4):
                r=80+i*25;a=(s.t*(1 if i%2==0 else -1)*(1.5-i*0.2))%(2*math.pi)
                pts=[]
                for j in range(6):
                    ang=a+j*math.pi/3;pts.append((int(cx+r*math.cos(ang)),int(cy+r*math.sin(ang))))
                pts=np.array(pts,np.int32)
                cv2.polylines(fr,[pts],True,c_1,2,cv2.LINE_AA)
                if i%2==1:
                    for p in pts:cv2.circle(fr,p,3,c_2,-1)
            cv2.circle(fr,(cx,cy),40,c_3,4)
            for _ in range(5):s.particles.append([cx,cy,(np.random.rand()-0.5)*30,(np.random.rand()-0.5)*30,200])
        elif sg=="FIST" and hlm0 and not s.show_list:
            cx,cy=palm_center(hlm0,W,H)
            cv2.circle(fr,(cx,cy),25,(0,0,0),-1);cv2.circle(fr,(cx,cy),32,(150,0,255),3)
            for p in s.particles:
                dx=cx-p[0];dy=cy-p[1];dist=max(1,math.sqrt(dx*dx+dy*dy))
                p[0]+=dx/dist*12;p[1]+=dy/dist*12
        elif sg=="FOUR":
            if s._cd==0:s.show_list=not s.show_list;s._cd=15
            
        alive=[]
        for p in s.particles:
            p[0]+=p[2];p[1]+=p[3];p[4]-=1
            if p[4]>0:
                cv2.circle(fr,(int(p[0]),int(p[1])),int(p[4]*0.05+1),c_2,-1)
                alive.append(p)
        s.particles=alive
        
        if s.show_list:
            tw=500;th=100;ox=W//2-tw//2;oy=H//2-th//2
            orect(fr,ox-20,oy-40,ox+tw+20,oy+th+20,C_BG,0.9);neon(fr,ox-20,oy-40,ox+tw+20,oy+th+20,C_PR,1)
            pc(fr,"SELECT STYLE",W//2,oy-18,0.55,C_PR,2)
            s._rects=[]
            for i,nm in enumerate(PORTAL_STYLES):
                x=ox+i*170;y=oy;ih=(i==s.lhov);act=(i==s.si)
                orect(fr,x,y,x+150,y+70,C_PR if ih else C_PN,0.7)
                neon(fr,x,y,x+150,y+70,C_PR if ih else(C_GN if act else C_GR),2 if ih else 1)
                pc(fr,nm,x+75,y+35,0.45,C_WH if ih else C_GR,2)
                s._rects.append((x,y,x+150,y+70,i))
    def list_rects(s):return getattr(s,'_rects',[])

def main():
    cap=cv2.VideoCapture(CAM)
    if not cap.isOpened():print("[ERROR] No camera");return
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,W);cap.set(cv2.CAP_PROP_FRAME_HEIGHT,H);cap.set(cv2.CAP_PROP_FPS,30)
    det=mp_h.Hands(static_image_mode=False,max_num_hands=2,min_detection_confidence=0.85,min_tracking_confidence=0.8)
    state=MENU;cv_=Canvas();brush=C_DR;pk=Picker(brush);h3=Holo3D();mp_p=MagicPortal()
    stb=Stab(n=6);exd=ExD();tsm=Smo()
    mhov=None;mdwl=None;pdwi=-1;pdws=None;sdwi=-1;sdws=None;hdwi=-1;hdws=None
    cdwi=-1;cdws=None
    fq=deque(maxlen=30);pt_=time.time()
    cv2.namedWindow("Gesture AR",cv2.WINDOW_NORMAL);cv2.resizeWindow("Gesture AR",W,H)
    hlm0_ref=None
    while True:
        ok,fr=cap.read()
        if not ok:break
        fr=cv2.flip(fr,1);rgb=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB);res=det.process(rgb)
        now=time.time();dt_=max(now-pt_,1e-6);fq.append(1.0/dt_);pt_=now;fps=int(np.mean(fq))
        clean=fr.copy()
        nh=0;f0=[0]*5;af=[];gest="NONE";tp=None;hlm0_ref=None
        if res.multi_hand_landmarks:
            nh=len(res.multi_hand_landmarks)
            for i,hlm in enumerate(res.multi_hand_landmarks):
                lab=res.multi_handedness[i].classification[0].label
                fi=fst(hlm,lab);af.append(fi)
                if i==0:f0=fi;hlm0_ref=hlm
                mp_du.draw_landmarks(fr,hlm,mp_h.HAND_CONNECTIONS,mp_st.get_default_hand_landmarks_style(),mp_st.get_default_hand_connections_style())
            raw=tpx(res.multi_hand_landmarks[0],8,W,H);tp=tsm.u(raw);gest=clas(f0)
        else:tsm.r()
        sg=stb.u(gest);exd.u(nh,af if len(af)>=2 else[[0]*5,[0]*5]);pk.tick();cv_.tick();scanl(fr)

        if state==MENU:
            dp=(time.time()-mdwl)/DWELL if mdwl else 0
            render_menu(fr,mhov,dp,brush)
            if tp and sg=="INDEX":
                cur(fr,tp,C_CY)
                hit=None
                if ptin(tp,B1):hit="draw"
                elif ptin(tp,B2):hit="picker"
                elif ptin(tp,B3):hit="holo"
                elif ptin(tp,B4):hit="portal"
                if hit:
                    if mhov!=hit:mhov=hit;mdwl=time.time()
                    elif time.time()-mdwl>=DWELL:
                        if hit=="draw":state=DRAW;cv_.col=brush;cv_.snap()
                        elif hit=="picker":state=PICKER;pk=Picker(brush)
                        elif hit=="holo":state=HOLO3D;h3=Holo3D()
                        else:state=PORTAL;mp_p=MagicPortal()
                        mhov=None;mdwl=None;stb.r();exd.r()
                else:mhov=None;mdwl=None
            else:mhov=None;mdwl=None
            hud(fr,"MENU",fps,sg,"Point & hold 1s")

        elif state==DRAW:
            cv_.col=brush;cv_.blend(fr)
            if exd.ok():state=MENU;cv_.lift();exd.r();stb.r();hdwi=-1;hdws=None;cdwi=-1;cdws=None
            else:
                if sg=="FIST":
                    if cv_.show_hist:cv_.show_hist=False;stb.r()
                    else:cv_.paused=True;cv_.lift()
                elif sg=="PALM":
                    cv_.paused=False;cv_.show_hist=False
                    if tp:cv_.erase(tp);cv2.circle(fr,tp,ER_R,C_RD,2,cv2.LINE_AA)
                    cv_.lift()
                elif sg=="INDEX":
                    cv_.paused=False;cv_.show_hist=False
                    if tp:cur(fr,tp,brush,6);cv_.draw(tp)
                elif sg=="THREE":cv_.snap();stb.r()
                elif sg=="FOUR":cv_.show_hist=True;cv_.lift()
                elif sg=="TWO":
                    if cv_.show_hist and tp:
                        n=min(len(cv_.hist),5)
                        tw_,th_=140,80;gap=12;total=n*(tw_+gap)-gap
                        sx=W//2-total//2;sy=H//2-th_//2-30
                        hi=-1
                        for i in range(n):
                            x=sx+i*(tw_+gap)
                            if x<=tp[0]<=x+tw_ and sy<=tp[1]<=sy+th_:hi=i;break
                        if hi>=0:
                            idx=len(cv_.hist)-1-hi
                            cur(fr,tp,C_GN,15)
                            if hdwi!=hi:hdwi=hi;hdws=time.time()
                            elif time.time()-hdws>=DWELL:
                                cv_.c=cv_.hist[idx].copy();cv_.show_hist=False
                                hdwi=-1;hdws=None;stb.r()
                            else:parc(fr,tp[0],tp[1]-30,(time.time()-hdws)/DWELL,14,C_GN)
                        else:hdwi=-1;hdws=None
                    else:
                        if cdwi!=2:cdwi=2;cdws=time.time()
                        elif time.time()-cdws>=2.0:
                            cv_.clear();stb.r();cdwi=-1;cdws=None
                        else:parc(fr,tp[0],tp[1]-30,(time.time()-cdws)/2.0,20,C_RD)
                else:cv_.lift();hdwi=-1;hdws=None;cdwi=-1;cdws=None
            if cv_.show_hist:cv_.render_hist(fr)
            exit_ov(fr,exd.pr())
            st="PAUSED" if cv_.paused else("ERASER" if sg=="PALM" else "DRAWING")
            orect(fr,W-280,H-70,W-10,H-5,C_BG,0.7)
            cv2.rectangle(fr,(W-270,H-55),(W-240,H-15),brush,-1);neon(fr,W-270,H-55,W-240,H-15,C_WH,1)
            ptx(fr,f"{st} | Saves:{len(cv_.hist)}",(W-230,H-28),0.45,C_GN,1)
            hud(fr,"DRAW",fps,sg,"1f=Draw|PALM=Erase|2f=Clear/Sel|3f=Save|4f=Hist")

        elif state==PICKER:
            if exd.ok():brush=pk.bgr;state=MENU;exd.r();stb.r()
            else:
                if sg=="PALM":pk.show_pal=True;pk.show_whl=False;pk.live=False
                elif sg=="FOUR":pk.show_whl=True;pk.show_pal=False;pk.live=False
                elif sg=="THREE":pk.save();pk.applyb();pk.show_pal=False;pk.show_whl=False
                elif sg=="TWO":
                    pk.live=True;pk.show_pal=False
                    if tp:
                        if pk.show_whl:pk.samp_whl(tp)
                        else:pk.samp(clean,tp)
                elif sg=="INDEX":
                    pk.live=False
                    if pk.show_whl and tp:pk.samp_whl(tp);pk.applyb()
                    elif pk.show_pal and tp and pk.pal:
                        hi=-1
                        for sx,sy,ex,ey,i in pk.swatches():
                            if sx<=tp[0]<=ex and sy<=tp[1]<=ey:hi=i;break
                        pk.ph=hi
                        if hi>=0:
                            if pdwi!=hi:pdwi=hi;pdws=time.time()
                            elif time.time()-pdws>=DWELL:pk.sel(hi);brush=pk.bgr;pk.show_pal=False;pdwi=-1;pdws=None
                        else:pdwi=-1;pdws=None
                    else:pk.show_pal=False;pk.show_whl=False;pdwi=-1;pdws=None
                else:pk.live=False
            exit_ov(fr,exd.pr());pk.render(fr,tp)
            hud(fr,"PICKER",fps,sg,"1f=Select|2f=Scan|3f=Save|4f=Wheel|5f=Palette")

        elif state==HOLO3D:
            h3.tick(dt_)
            if exd.ok():state=MENU;exd.r();stb.r()
            else:
                if sg=="PALM" and hlm0_ref:
                    # FULL HAND CONTROL — everything else stops
                    h3.auto=False;h3.show_list=False
                    pc_=palm_center(hlm0_ref,W,H)
                    if h3.palm_base is None:
                        h3.palm_base=pc_;h3.base_rx=h3.trx;h3.base_ry=h3.try_
                    else:
                        dx=(pc_[0]-h3.palm_base[0])/W*6.0
                        dy=(pc_[1]-h3.palm_base[1])/H*6.0
                        h3.try_=h3.base_ry+dx;h3.trx=h3.base_rx+dy
                    ptx(fr,"HAND CONTROL",(W//2-90,H-80),0.65,C_GO,2)
                elif sg=="FIST":
                    if h3._cd==0:
                        h3.show_list=not h3.show_list;h3._cd=15;stb.r()
                        sdwi=-1;sdws=None
                elif sg=="INDEX" and h3.show_list and tp:
                    hi=-1
                    for(lx,ly,lex,ley,li)in h3.list_rects():
                        if lx<=tp[0]<=lex and ly<=tp[1]<=ley:hi=li;break
                    h3.list_hover=hi
                    if hi>=0:
                        cur(fr,tp,C_GO)
                        if sdwi!=hi:sdwi=hi;sdws=time.time()
                        elif time.time()-sdws>=DWELL:
                            h3.select_shape(hi);sdwi=-1;sdws=None;stb.r()
                        else:parc(fr,tp[0],tp[1]-30,(time.time()-sdws)/DWELL,14,C_GO)
                    else:sdwi=-1;sdws=None
                elif sg=="THREE":h3.reset_pose();h3.show_list=False;stb.r()
                else:h3.palm_base=None
                # PINCH SCALE — strict logic
                if hlm0_ref and sg not in["FIST","THREE","INDEX","TWO","FOUR"] and not h3.show_list:
                    pd=pinch_dist(hlm0_ref,W,H)
                    if h3.base_pinch is None:h3.base_pinch=pd;h3.base_scale=h3.scale
                    else:
                        raw_r=pd/max(h3.base_pinch,1)
                        ratio=1.0+(raw_r-1.0)*0.3
                        h3.scale=max(0.3,min(4.0,h3.base_scale*ratio))
                else:h3.base_pinch=None
                if sg!="PALM":h3.palm_base=None
            h3.render(fr,tp,sg,hlm0_ref)
            exit_ov(fr,exd.pr())
            hud(fr,"3D HOLO",fps,sg,"PALM=Control|FIST=Shapes|THREE=Reset")

        elif state==PORTAL:
            mp_p.tick(dt_)
            if exd.ok():state=MENU;exd.r();stb.r()
            else:
                if sg=="INDEX" and mp_p.show_list and tp:
                    hi=-1
                    for(lx,ly,lex,ley,li)in mp_p.list_rects():
                        if lx<=tp[0]<=lex and ly<=tp[1]<=ley:hi=li;break
                    mp_p.lhov=hi
                    if hi>=0:
                        cur(fr,tp,C_GO)
                        if sdwi!=hi:sdwi=hi;sdws=time.time()
                        elif time.time()-sdws>=DWELL:
                            mp_p.si=hi;mp_p.show_list=False;sdwi=-1;sdws=None;stb.r()
                        else:parc(fr,tp[0],tp[1]-30,(time.time()-sdws)/DWELL,14,C_GO)
                    else:sdwi=-1;sdws=None
                else:sdwi=-1;sdws=None
            mp_p.render(fr,tp,sg,hlm0_ref)
            exit_ov(fr,exd.pr())
            hud(fr,"PORTAL",fps,sg,"PALM=Shield|FIST=Blackhole")

        cv2.imshow("Gesture AR",fr)
        k=cv2.waitKey(1)&0xFF
        if k==ord('q'):break
        elif k==ord('c')and state==DRAW:cv_.clear()
    cap.release();cv2.destroyAllWindows()
if __name__=="__main__":main()