import numpy as np
ALPHA=np.radians(25)
def inv(a): return np.tan(a)-a
def gear_pts(z,m,phase=0.0,delta=0.02,nfl=12,narc=3):
    """2D outline (N,2) ccw, centred at origin, tooth 0 centred at angle=phase."""
    r=z*m/2; rb=r*np.cos(ALPHA); ra=r+m-delta; rf=r-1.25*m
    def psi(rho):
        rho=max(rho,rb)
        phi=np.arccos(rb/rho)
        return np.pi/(2*z)+inv(ALPHA)-inv(phi)-delta/rb
    r0=max(rb,rf)
    rhos=r0+(ra-r0)*(1-np.cos(np.linspace(0,np.pi/2,nfl)))  # denser near base
    rhos=np.linspace(r0,ra,nfl)
    pts=[]
    for k in range(z):
        th=phase+2*np.pi*k/z
        right=[]
        if rf<rb: right.append((rf,th-psi(rb)))
        for rho in rhos: right.append((rho,th-psi(rho)))
        pt=psi(ra)
        assert pt>0.002, ("pointed",z,m,pt)
        tip=[(ra,th-pt+2*pt*i/(narc+1)) for i in range(1,narc+1)]
        left=[(rho,2*th-a) for rho,a in right[::-1]]
        seq=right+tip+left
        # root arc to next tooth
        a0=left[-1][1]; a1=th+2*np.pi/z-psi(rb if rf<rb else rf)
        root=[(rf,a0+(a1-a0)*i/(narc+1)) for i in range(1,narc+1)]
        for rho,a in seq+root: pts.append((rho*np.cos(a),rho*np.sin(a)))
    return np.array(pts)
def mesh_phase(z1,m1,ph1,c1,z2,c2):
    """phase of gear2 (z2, same module) meshing gear1 at c1 with phase ph1."""
    c1=np.asarray(c1,float);c2=np.asarray(c2,float)
    psi=np.arctan2(*(c2-c1)[::-1])
    p1=2*np.pi/z1
    e1=(psi-ph1+p1/2)%p1-p1/2
    r1=z1*m1/2;r2=z2*m1/2;p=np.pi*m1
    s1=e1*r1
    s2=p/2-s1
    return psi+np.pi-s2/r2
