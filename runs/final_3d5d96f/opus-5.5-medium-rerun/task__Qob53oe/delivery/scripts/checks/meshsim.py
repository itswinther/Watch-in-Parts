import sys; sys.path.insert(0,'/app/delivery/scripts')
from gears import *
def rot(P,a,c=(0,0)):
    ca,sa=math.cos(a),math.sin(a)
    return np.c_[c[0]+ca*P[:,0]-sa*P[:,1], c[1]+sa*P[:,0]+ca*P[:,1]]
def segdist(P,Q,c=None,R=None):
    A=Q; B=np.roll(Q,-1,axis=0)
    if c is not None:
        k=np.hypot(A[:,0]-c[0],A[:,1]-c[1])<R; A=A[k]; B=B[k]
        k=np.hypot(P[:,0]-c[0],P[:,1]-c[1])<R; P=P[k]
    AB=B-A; L2=(AB**2).sum(1)+1e-30
    best=np.inf
    for i in range(0,len(P),256):
        p=P[i:i+256,None,:]
        t=np.clip(((p-A)*AB).sum(2)/L2,0,1)
        d=np.sqrt((((A+t[...,None]*AB)-p)**2).sum(2)).min()
        best=min(best,d)
    return best
def inside(P,Q):
    from matplotlib.path import Path
    return Path(Q).contains_points(P).any()
def gap(PA,PB,c,R):
    if inside(PA,PB) or inside(PB,PA): return -1
    return min(segdist(PA,PB,c,R),segdist(PB,PA,c,R))
def local(P,c,R):
    d=np.hypot(P[:,0]-c[0],P[:,1]-c[1]); return P[d<R]
def sim(m,z1,z2,t1,t2,n=24):
    a=m*(z1+z2)/2
    A=section_loops(gear_section(m,z1,t1,phase=0.0))[0]
    B=section_loops(gear_section(m,z2,t2,phase=math.pi+math.pi/z2))[0]
    pitch=2*math.pi/z1
    res=[]
    for th in np.linspace(0,pitch,n,endpoint=False):
        PA=rot(A,th); PB=rot(B,-th*z1/z2,(a,0))
        cc=(m*z1/2,0); RR=3*m
        g=gap(PA,PB,cc,RR)
        # driving contact: rotate B further CCW (opposite to its motion) until touch
        lo,hi=0.0,0.2/(m*z2/2)
        def touch(d):
            PB2=rot(B,-th*z1/z2+d,(a,0))
            return gap(PA,PB2,cc,RR)<1e-4
        for _ in range(30):
            mid=(lo+hi)/2
            if touch(mid): hi=mid
            else: lo=mid
        res.append((g,hi*m*z2/2))
    res=np.array(res)
    return res
if __name__=='__main__':
    for (m,z1,z2,t1,t2) in [(0.2,96,20,0.03,0.04),(0.2,40,8,0.04,0.04),(0.22,32,8,0.04,0.04),(0.3,12,12,0.04,0.04),(0.2,8,16,0.04,0.04),(0.2,8,32,0.04,0.04),(0.2,8,8,0.04,0.04)]:
        r=sim(m,z1,z2,t1,t2)
        print(m,z1,z2,'min gap %.4f max gap %.4f  arc-backlash min %.4f max %.4f'%(r[:,0].min(),r[:,0].max(),r[:,1].min(),r[:,1].max()))
