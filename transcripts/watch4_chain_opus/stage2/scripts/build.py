"""Stage 2: build the 24-hour (day) mobile and its fixed post."""
import sys, math
from common import *
import cadquery as cq
PA=math.radians(25)
MX,MY=10.5,4.5          # motion axis (n_pinion, 12 t, m 0.15)
M=0.15; NP=12; ND=96
DIST=M*(NP+ND)/2         # 8.1
DX,DY=MX,MY+DIST         # day axis (10.5, 12.6)
def inv(a): return math.tan(a)-a
def gear_pts(N,m,phase,bl=0.03,nf=10,na=4):
    rp=N*m/2; rb=rp*math.cos(PA); ra=rp+m; rf=rp-1.25*m
    s=math.pi*m/2-bl; hp=s/(2*rp)
    def fl(r):
        if r<=rb: return hp+inv(PA)
        return hp+inv(PA)-inv(math.acos(rb/r))
    r0=max(rf,rb)
    rs=[r0+(ra-r0)*i/nf for i in range(nf+1)]
    pts=[]
    pitch=2*math.pi/N
    for k in range(N):
        c=phase+k*pitch
        prof=[]
        # rising flank (negative side) from root to tip
        if rf<rb: prof.append((rf,c-fl(rb)))
        for r in rs: prof.append((r,c-fl(r)))
        ta=fl(ra)
        for i in range(1,na): prof.append((ra,c-ta+2*ta*i/na))
        for r in reversed(rs): prof.append((r,c+fl(r)))
        if rf<rb: prof.append((rf,c+fl(rb)))
        # root arc to next tooth
        a0=c+fl(r0); a1=c+pitch-fl(r0)
        for i in range(1,na): prof.append((rf,a0+(a1-a0)*i/na))
        pts+=prof
    return [(r*math.cos(a),r*math.sin(a)) for r,a in pts]
def gear(N,m,phase,z0,z1,cx,cy,bore):
    pts=gear_pts(N,m,phase)
    w=cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1-z0)
    if bore: w=w.cut(cq.Workplane('XY').workplane(offset=z0-1).circle(bore).extrude(z1-z0+2))
    return w.translate((cx,cy,0))
def tube(cx,cy,ri,ro,z0,z1):
    w=cq.Workplane('XY').workplane(offset=z0).circle(ro)
    if ri: w=w.circle(ri)
    return w.extrude(z1-z0).translate((cx,cy,0))
POST_R=0.5; BORE=0.6; HUB=1.1
def build(phase, out=None):
    wheel=gear(ND,M,phase,6.6,7.4,DX,DY,None).union(tube(DX,DY,0,HUB,5.6,8.9)).cut(tube(DX,DY,0,BORE,5.0,9.5))
    # hand: collar + arm pointing at its own angle (pointer toward +y (12 o clock, like the other hands at assembly))
    collar=tube(DX,DY,HUB-0.1,1.5,8.0,8.4)
    L=4.2
    arm=(cq.Workplane('XY').workplane(offset=8.0).polyline([(-0.3,1.2),(0.3,1.2),(0.16,L),(-0.16,L)]).close().extrude(0.4)).translate((DX,DY,0))
    hand=collar.union(arm)
    post=tube(DX,DY,0,POST_R,5.5,9.0).union(tube(DX,DY,0,1.0,9.0,9.4))
    return wheel,hand,post
if __name__=='__main__':
    phase=float(sys.argv[1])
    import os
    wheel,hand,post=build(phase)
    P=os.path.join(ROOT,'work','parts')
    for n,s in [('day_wheel',wheel),('day_hand',hand),('day_post',post)]:
        kernel.write_step(os.path.join(P,n+'.step'),s)
    print('ok')
