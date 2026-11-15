import json, math, sys, time
import numpy as np
sys.path.insert(0,'/app/delivery/scripts')
from vlib import *
import assembly
doc=json.load(open(os.path.join(DEL,'movement.json')))
names=list(doc['fixed'])+[p for m in doc['mobiles'].values() for p in m['parts']]
P=load_parts(names); P['barrel']=barrel(doc['barrel'])
allv=np.concatenate([kernel.verts(m) for m in P.values()])
lo=allv.min(0); hi=allv.max(0)
zmin={n:kernel.verts(m)[:,2].min() for n,m in P.items()}
A=assembly.make(zmin, hi[2])
missing=set(P)-set(A['order']); print('not in order:',missing)
json.dump(A,open(os.path.join(DEL,'assembly.json'),'w'))
# verify
placed=[]
worst=0
for n in A['order']:
    poses=A['paths'][n]
    man=P[n]
    # rule 2
    T0=np.array(poses[0]); v=kernel.verts(man)@T0[:3,:3].T+T0[:3,3]
    out = (v.min(0) > hi+5).any() or (v.max(0) < lo-5).any()
    assert out, n
    assert np.allclose(np.array(poses[-1]),np.eye(4))
    steps=[np.abs(np.array(poses[i+1])[:3,3]-np.array(poses[i])[:3,3]).max() for i in range(len(poses)-1)]
    assert max(steps)<=0.2, n
    bad=[]
    for T in poses:
        mm=man.translate([T[0][3],T[1][3],T[2][3]])
        for q in placed:
            if not kernel.bbox_overlap(mm,P[q],0.0): continue
            iv=kernel.ivol(mm,P[q])
            if iv>1e-6: bad.append((q,round(T[2][3],3),round(iv,5)))
    mx=max([b[2] for b in bad],default=0)
    print('%-14s poses %3d  collisions(max ivol) %.5f %s'%(n,len(poses),mx, bad[:4] if mx>0.0 else ''),flush=True)
    placed.append(n)
