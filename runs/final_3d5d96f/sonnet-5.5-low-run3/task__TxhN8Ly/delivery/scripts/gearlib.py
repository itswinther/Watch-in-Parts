import math, numpy as np
ALPHA=math.radians(25)
def inv(p): return math.tan(p)-p
def profile(z,m,rho=0.0,nfl=9,tfrac=0.4524):
    R=z*m/2; Ra=R+m; Rf=R-1.25*m; Rb=R*math.cos(ALPHA)
    t=tfrac*math.pi*m; delta=t/(2*R)
    def th(r):
        return delta-(inv(math.acos(min(1,Rb/r)))-inv(ALPHA))
    r0=max(Rb,Rf)
    # tip radius where th>=~0.004
    rt=Ra
    if th(Ra)<0.004:
        lo,hi=r0,Ra
        for _ in range(60):
            mid=(lo+hi)/2
            if th(mid)>0.004: lo=mid
            else: hi=mid
        rt=lo
    rs=np.linspace(r0,rt,nfl)
    pitch=2*math.pi/z
    pts=[]
    for k in range(z):
        c=k*pitch+rho
        # right flank (negative side) from root up to tip
        seq=[]
        if Rf<Rb-1e-9: seq.append((Rf,-th(Rb)))
        for r in rs: seq.append((r,-th(r)))
        # tip arc
        thT=th(rt)
        seq.append((rt,-thT*0.0))  # tip centre
        for r in rs[::-1]: seq.append((r,th(r)))
        if Rf<Rb-1e-9: seq.append((Rf,th(Rb)))
        # root arc to next tooth
        a_end=th(Rb) if Rf<Rb-1e-9 else th(r0)
        a0=a_end; a1=pitch-a_end
        for f in (0.33,0.66):
            seq.append((Rf if Rf<Rb else r0, a0+(a1-a0)*f)) if False else None
        for (r,a) in seq: pts.append((r*math.cos(c+a),r*math.sin(c+a)))
        # root arc intermediate points
        rr=Rf if Rf<Rb-1e-9 else r0
        for f in (0.5,):
            a=a0+(a1-a0)*f; pts.append((rr*math.cos(c+a),rr*math.sin(c+a)))
    return pts
def mesh_rho(z1,m,rho1,z2,beta):
    """rotation of driven gear (z2 teeth, same module) so it meshes driver z1 at rotation rho1; beta=angle from G1 to G2"""
    R1=z1*m/2; R2=z2*m/2
    r2=beta+math.pi-(R1/R2)*(rho1-beta)+math.pi/z2
    p=2*math.pi/z2
    return r2%p
