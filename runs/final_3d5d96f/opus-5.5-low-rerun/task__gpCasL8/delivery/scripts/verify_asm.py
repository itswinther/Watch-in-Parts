import sys,json,numpy as np
sys.path.insert(0,'/app/work')
from load import *
mv=json.load(open('/app/delivery/movement.json'));asm=json.load(open('/app/delivery/assembly.json'))
parts={p:part(p) for p in mv['fixed']}
own={}
for mn,m in mv['mobiles'].items():
    for p in m['parts']: parts[p]=part(p); own[p]=mn
parts['barrel']=barrel()
allb=kernel.union(list(parts.values())).bounding_box()
G=np.array(allb); G[:3]-=5; G[3:]+=5
assert set(asm['order'])==set(parts), set(parts)^set(asm['order'])
placed=[]
for nm in asm['order']:
    P=asm['paths'][nm]; M=[np.array(T) for T in P]
    assert 2<=len(M)<=1500
    for T in M:
        R=T[:3,:3]; assert np.allclose(R.T@R,np.eye(3),atol=1e-6) and abs(np.linalg.det(R)-1)<1e-6 and np.allclose(T[3],[0,0,0,1])
    assert np.allclose(M[-1],np.eye(4),atol=1e-6)
    v=kernel.verts(parts[nm])
    f=(M[0][:3,:3]@v.T).T+M[0][:3,3]; lo,hi=f.min(0),f.max(0)
    outside=any(hi[i]<G[i] or lo[i]>G[i+3] for i in range(3))
    mx=max(np.abs(((M[i+1][:3,:3]-M[i][:3,:3])@v.T).T+(M[i+1][:3,3]-M[i][:3,3])).max() for i in range(len(M)-1))
    worst=0;who=None
    for i in range(len(M)-1):
        for s in np.linspace(0,1,5)[:-1]:
            T=M[i]*(1-s)+M[i+1]*s
            Q=parts[nm].transform(T[:3,:4].tolist())
            for o in placed:
                if kernel.bbox_overlap(Q,parts[o]):
                    iv=kernel.ivol(Q,parts[o])
                    if iv>worst: worst,who=iv,o
    print('%-14s poses=%d outside=%s maxstep=%.3f worst_overlap=%.2e %s'%(nm,len(M),outside,mx,worst,who))
    placed.append(nm)
