import sys, json, numpy as np
sys.path.insert(0,'.')
from scipy.spatial.transform import Rotation as Rot, Slerp
from tools.geometry import md
inst = md.flat_one()
AIR = [(np.array(a),np.array(b)) for a,b in inst.air.values()]
BLO,BHI = np.array(inst.block[0],float), np.array(inst.block[1],float)

def surf_points(name, sp=6.0):
    pts=[]
    for lo,hi in inst.pieces[name]["boxes"]:
        lo=np.array(lo,float);hi=np.array(hi,float)
        ax=[np.unique(np.append(np.arange(lo[i],hi[i],sp),hi[i])) for i in range(3)]
        g=np.stack(np.meshgrid(*ax,indexing='ij'),-1).reshape(-1,3)
        on=((g==lo)|(g==hi)).any(1)
        pts.append(g[on])
    return np.unique(np.vstack(pts),axis=0)

def free(P):
    e=1e-7
    outside=((P<BLO-e)|(P>BHI+e)).any(1)
    ok=outside.copy()
    for lo,hi in AIR:
        ok|=((P>=lo-e)&(P<=hi+e)).all(1)
    return ok

class Planner:
    def __init__(s,name,sp=6.0,seed=0):
        s.pts=surf_points(name,sp); s.rng=np.random.default_rng(seed)
        s.rad=np.linalg.norm(s.pts-s.pts.mean(0),axis=1).max()
    def pose(s,q): # q = (t(3), rotvec(3))
        T=np.eye(4);T[:3,:3]=Rot.from_rotvec(q[3:]).as_matrix();T[:3,3]=q[:3];return T
    def valid(s,q):
        T=s.pose(q);W=s.pts@T[:3,:3].T+T[:3,3]
        return bool(free(W).all())
    def edge_ok(s,a,b,step=2.0):
        n=int(max(np.linalg.norm(b[:3]-a[:3])/step, s.ang(a,b)*s.rad/step))+1
        for i in range(1,n+1):
            if not s.valid(s.interp(a,b,i/n)): return False
        return True
    def ang(s,a,b):
        return (Rot.from_rotvec(a[3:]).inv()*Rot.from_rotvec(b[3:])).magnitude()
    def interp(s,a,b,u):
        ra,rb=Rot.from_rotvec(a[3:]),Rot.from_rotvec(b[3:])
        r=Slerp([0,1],Rot.concatenate([ra,rb]))(u)
        return np.concatenate([a[:3]*(1-u)+b[:3]*u,r.as_rotvec()])
    def dist(s,a,b):
        return np.linalg.norm(a[:3]-b[:3])+s.rad*0.6*s.ang(a,b)
    def rrt(s,start,goal,lo,hi,iters=20000,ext=15.0,bias=0.1):
        assert s.valid(start) and s.valid(goal),(s.valid(start),s.valid(goal))
        if s.edge_ok(start,goal): return [start,goal]
        TA=[start];PA=[-1];TB=[goal];PB=[-1]
        for it in range(iters):
            q=np.concatenate([s.rng.uniform(lo,hi),Rot.random(random_state=int(s.rng.integers(1<<30))).as_rotvec()])
            # extend A toward q
            i=min(range(len(TA)),key=lambda k:s.dist(TA[k],q))
            d=s.dist(TA[i],q);u=min(1,ext/max(d,1e-9));nq=s.interp(TA[i],q,u)
            if s.edge_ok(TA[i],nq):
                TA.append(nq);PA.append(i)
                # connect B toward nq
                j=min(range(len(TB)),key=lambda k:s.dist(TB[k],nq))
                cur=j
                while True:
                    d=s.dist(TB[cur],nq);u=min(1,ext/max(d,1e-9));c=s.interp(TB[cur],nq,u)
                    if not s.edge_ok(TB[cur],c): break
                    TB.append(c);PB.append(cur);cur=len(TB)-1
                    if u>=1:
                        pa=[];k=len(TA)-1
                        while k>=0: pa.append(TA[k]);k=PA[k]
                        pa=pa[::-1];pb=[];k=cur
                        while k>=0: pb.append(TB[k]);k=PB[k]
                        res=pa+pb
                        if np.abs(res[0]-start).max()>1e-9: res=res[::-1]
                        return res
            TA,TB,PA,PB=TB,TA,PB,PA
            # keep orientation: swap roles; track
            s._swapped=not getattr(s,'_swapped',False)
        return None

    def smooth(s,path,rounds=200):
        path=list(path)
        for _ in range(rounds):
            if len(path)<3: break
            i,j=sorted(s.rng.choice(len(path),2,replace=False))
            if j-i>1 and s.edge_ok(path[i],path[j]): path=path[:i+1]+path[j:]
        return path
    def dense(s,path,maxmove=4.0):
        out=[path[0]]
        for a,b in zip(path[:-1],path[1:]):
            n=int(np.ceil(max(np.linalg.norm(b[:3]-a[:3]),s.ang(a,b)*s.rad)/maxmove))+1
            for i in range(1,n+1): out.append(s.interp(a,b,i/n))
        return out
