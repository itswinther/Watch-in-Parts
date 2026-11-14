import math, sys, cadquery as cq
sys.path.insert(0,'tools')
def gear(N,m,z0,z1,phase,pa=25,back=0.03):
    rp=N*m/2; rb=rp*math.cos(math.radians(pa)); ra=rp+m; rr=rp-1.25*m
    def inv(r):  # involute angle at radius r
        t=math.sqrt(max((r/rb)**2-1,0)); return t-math.atan(t)
    rs=max(rb,rr)
    half=(math.pi*m/2-back)/2/rp*1.0  # half tooth angle at pitch circle
    # tooth centred at angle 0: flank angle at r = half + inv(rp) - inv(r)
    rad=[rs+(ra-rs)*i/12 for i in range(13)]
    pts=[]
    pitch=2*math.pi/N
    for k in range(N):
        c=phase+k*pitch
        right=[(r,c-(half+inv(rp)-inv(r))) for r in rad]
        left=[(r,c+(half+inv(rp)-inv(r))) for r in reversed(rad)]
        if rr<rs: pts.append((rr,right[0][1]))
        pts+=right+left
        if rr<rs: pts.append((rr,left[-1][1]))
    xy=[(r*math.cos(a),r*math.sin(a)) for r,a in pts]
    return cq.Workplane('XY').workplane(offset=z0).polyline(xy).close().extrude(z1-z0)
