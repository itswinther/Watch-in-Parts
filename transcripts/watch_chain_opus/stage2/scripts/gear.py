import numpy as np, manifold3d as m3
def inv(a): return np.tan(a)-a
def gear_cs(N, m=0.2, pa=25.0, back=0.03, phase=0.0, npts=8):
    r=N*m/2; rb=r*np.cos(np.radians(pa)); ra=r+m; rf=r-1.25*m
    s=np.pi*m/2-back
    ap=np.radians(pa)
    half=lambda rho: s/(2*r)+inv(ap)-inv(np.arccos(min(1,rb/rho)))
    r0=max(rb,rf)
    rhos=np.linspace(r0,ra,npts)
    pts=[]
    for k in range(N):
        c=phase+2*np.pi*k/N
        # rising flank (angle c - half), from root to tip
        left=[(rho, c-half(rho)) for rho in rhos]
        right=[(rho, c+half(rho)) for rho in rhos[::-1]]
        seq=[]
        if rf<rb: seq.append((rf,c-half(rb)))
        seq+=left
        # tip arc
        seq+= [(ra, a) for a in np.linspace(c-half(ra),c+half(ra),4)[1:-1]]
        seq+=right
        if rf<rb: seq.append((rf,c+half(rb)))
        # root arc to next tooth
        cn=c+2*np.pi/N
        a0=c+half(r0); a1=cn-half(r0)
        seq+=[(rf,a) for a in np.linspace(a0,a1,5)[1:-1]]
        pts+=seq
    P=np.array([(rho*np.cos(a),rho*np.sin(a)) for rho,a in pts])
    return m3.CrossSection([P.tolist()])
def gear(N, cx, cy, z0, z1, phase=0.0, bore=0.0, **kw):
    g=m3.Manifold.extrude(gear_cs(N,phase=phase,**kw), z1-z0).translate([cx,cy,z0])
    if bore>0:
        g=g-m3.Manifold.cylinder(z1-z0+2,bore,bore,64).translate([cx,cy,z0-1])
    return g
