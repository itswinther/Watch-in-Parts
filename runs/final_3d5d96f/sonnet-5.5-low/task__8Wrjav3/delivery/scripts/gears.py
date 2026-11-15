import math, numpy as np
ALPHA=math.radians(25)
BL=0.03
def inv(a): return math.tan(a)-a
def gear_polygon(z, m=0.2, phase=0.0, nflank=10, bl=BL):
    """Points (x,y) CCW of spur gear, tooth 0 centred at angle `phase`."""
    r=m*z/2; rb=r*math.cos(ALPHA); rt=r+m; rr=r-1.25*m
    t=math.pi*m/2-bl
    half0=t/(2*r)   # half angle at pitch circle
    def theta(rho):
        a=math.acos(min(1.0,rb/rho))
        return half0+inv(ALPHA)-inv(a)
    rs=max(rb,rr)  # flank start radius
    if rs<rr: rs=rr
    rhos=[rs+(rt-rs)*(i/nflank)**1.0 for i in range(nflank+1)]
    pts=[]
    pitch=2*math.pi/z
    th_tip=theta(rt)
    assert th_tip>0.005, (z,th_tip)
    for k in range(z):
        c=phase+k*pitch
        # right flank (negative side) going up
        for rho in rhos:
            a=c-theta(rho); pts.append((rho*math.cos(a),rho*math.sin(a)))
        # tip arc
        for q in (0.25,0.5,0.75):
            a=c-th_tip+2*th_tip*q; pts.append((rt*math.cos(a),rt*math.sin(a)))
        for rho in reversed(rhos):
            a=c+theta(rho); pts.append((rho*math.cos(a),rho*math.sin(a)))
        # radial to root (if base>root) and root arc to next tooth
        a0=c+theta(rs); a1=c+pitch-theta(rs)
        if rb>rr:
            pts.append((rr*math.cos(a0),rr*math.sin(a0)))
            pts.append((rr*math.cos((a0+a1)/2),rr*math.sin((a0+a1)/2)))
            pts.append((rr*math.cos(a1),rr*math.sin(a1)))
        else:
            pts.append((rr*math.cos((a0+a1)/2),rr*math.sin((a0+a1)/2)))
    return pts
if __name__=='__main__':
    for z in (12,15,24,48,96):
        p=gear_polygon(z); print(z,len(p))
