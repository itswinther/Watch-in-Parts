import sys,json,numpy as np
sys.path.insert(0,'scripts'); sys.path.insert(0,'tools')
import kernel
from block import P,mob,names
a=json.load(open('work/assembly.json'))
order=a['order']; assert sorted(order)==sorted(names) and len(set(order))==len(order), 'order set'
lo=np.min([P[n].bounding_box()[:3] for n in names],0)-5; hi=np.max([P[n].bounding_box()[3:] for n in names],0)+5
ok=0
for i,n in enumerate(order):
    ps=[np.array(p,float) for p in a['paths'][n]]; err=[]
    if not 2<=len(ps)<=1500: err.append('count')
    V=kernel.verts(P[n]); prev=None; worst=0
    for k,T in enumerate(ps):
        R=T[:3,:3]
        if T.shape!=(4,4) or not np.isfinite(T).all() or abs(R.T@R-np.eye(3)).max()>1e-6 or abs(np.linalg.det(R)-1)>1e-6 or abs(T[3]-[0,0,0,1]).max()>1e-6: err.append('rule1 %d'%k)
        W=V@R.T+T[:3,3]
        if k==0:
            b0,b1=W.min(0),W.max(0)
            if not ((b0>hi).any() or (b1<lo).any()): err.append('rule2')
        if prev is not None and np.linalg.norm(W-prev,axis=1).max()>0.2: err.append('rule3 %d'%k)
        prev=W
        M=kernel.apply(P[n],T)
        for b in order[:i]:
            if mob[b]==mob[n]: continue
            v=kernel.ivol(M,P[b]); worst=max(worst,v)
            if v>0.01: err.append('rule5 %d %s %.4f'%(k,b,v))
    if abs(ps[-1]-np.eye(4)).max()>1e-6: err.append('last')
    print(n,len(ps),'worst %.5f'%worst,'OK' if not err else err[:5]); ok+=not err
print('installed',ok,'of',len(order))
