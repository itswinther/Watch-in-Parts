import numpy as np, manifold3d as m3, math
ALPHA=math.radians(25)
def cutter_poly(m, s, nfl=12, narc=24):
    """rack cutter tooth in (x, depth) ; gear space at pitch = pi*m - s."""
    w0=(math.pi*m - s)/2; ta=math.tan(ALPHA)
    rho=(w0*math.cos(ALPHA)-1.25*m*math.sin(ALPHA))/(1-math.sin(ALPHA))
    dc=1.25*m-rho
    # tangent point on right flank: direction normal of flank (cos a, sin a) in (x,d)
    tx=rho*math.cos(ALPHA); td=dc+rho*math.sin(ALPHA)
    top=-2.0*m
    pts=[(w0-top*ta, top)]
    pts.append((tx,td))
    # arc from angle ALPHA (measured from +x toward +d) to pi-ALPHA through +d (bottom)
    for t in np.linspace(ALPHA, math.pi-ALPHA, narc)[1:-1]:
        pts.append((rho*math.cos(t), dc+rho*math.sin(t)))
    pts.append((-tx,td)); pts.append((-(w0-top*ta), top))
    return pts
def gear_cs(z, m, s=None, nstep=None, thin=0.0):
    """CrossSection of a rack-generated spur gear, one tooth gap centred on +y.
    s: tooth thickness on pitch circle (default pi m/2 - thin)."""
    if s is None: s=math.pi*m/2-thin
    r=m*z/2; ra=r+m
    cut=cutter_poly(m,s)
    xmax=2*math.sqrt(max(ra**2-(r-1.25*m)**2,0))+3*m
    phmax=xmax/r
    if nstep is None: nstep=int(max(300, 2*phmax/(0.004*m/ r)))  # fine
    nstep=min(nstep,1500)
    polys=[]
    for ph in np.linspace(-phmax,phmax,nstep):
        c,sn=math.cos(-ph),math.sin(-ph)
        P=[]
        for x,d in cut:
            X=x-r*ph; Y=r-d
            P.append((c*X-sn*Y, sn*X+c*Y))
        A=0.5*sum(P[i][0]*P[(i+1)%len(P)][1]-P[(i+1)%len(P)][0]*P[i][1] for i in range(len(P)))
        if A<0: P=P[::-1]
        polys.append(m3.CrossSection([P]))
    gap=m3.CrossSection.batch_boolean(polys, m3.OpType.Add)
    gaps=[gap.rotate(360.0*k/z) for k in range(z)]
    nseg=int(min(2000,max(256, math.pi/math.acos(1-0.0005/ra))))
    disc=m3.CrossSection.circle(ra, nseg)
    g=disc - m3.CrossSection.batch_boolean(gaps, m3.OpType.Add)
    return g
def dp(pts, tol):
    pts=np.asarray(pts)
    if len(pts)<3: return pts
    keep=np.zeros(len(pts),bool); keep[0]=keep[-1]=True
    stack=[(0,len(pts)-1)]
    while stack:
        i,j=stack.pop()
        if j<=i+1: continue
        a,b=pts[i],pts[j]; ab=b-a; L=np.hypot(*ab)
        seg=pts[i+1:j]
        if L<1e-12: d=np.hypot(*(seg-a).T)
        else: d=np.abs(ab[0]*(seg[:,1]-a[1])-ab[1]*(seg[:,0]-a[0]))/L
        k=np.argmax(d)
        if d[k]>tol:
            keep[i+1+k]=True; stack.append((i,i+1+k)); stack.append((i+1+k,j))
    return pts[keep]
def outline(cs, tol=0.0008):
    polys=cs.to_polygons()
    assert len(polys)==1, len(polys)
    p=np.asarray(polys[0])
    # closed ring simplify: split in two halves
    n=len(p); h=n//2
    a=dp(np.vstack([p[:h+1]]),tol); b=dp(np.vstack([p[h:],p[:1]]),tol)
    return np.vstack([a[:-1],b[:-1]])
def frac(x): return x-math.floor(x)
def mate_phase(th1,z1,p1,p2,z2):
    """tooth-centre angle (deg) for gear2 meshing gear1 (tooth angle th1)."""
    psi=math.degrees(math.atan2(p2[1]-p1[1],p2[0]-p1[0]))
    u1=frac((psi-th1)*z1/360.0)
    return psi+180.0-(0.5-u1)*360.0/z2
def phased(cs,z,th):
    return cs.rotate(th-(90.0+180.0/z))
