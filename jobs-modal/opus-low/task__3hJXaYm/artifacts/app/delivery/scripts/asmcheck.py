import sys, json; sys.path.insert(0,'.'); sys.path.insert(0,'/app/tools')
from verify import *
A=json.load(open(f'{D}/assembly.json')); mv=json.load(open(f'{D}/movement.json'))
allp=['barrel']+mv['fixed']+[p for m in mv['mobiles'].values() for p in m['parts']]
assert set(allp)==set(A['order']), set(allp)^set(A['order'])
full=[get(n).bounding_box() for n in allp]
lo=np.min([b[:3] for b in full],0)-5; hi=np.max([b[3:] for b in full],0)+5
placed=[]
for n in A['order']:
    P=np.array(A['paths'][n]); man=get(n); V=kernel.verts(man)
    b0=kernel.apply(man,P[0]).bounding_box()
    outside=any(b0[i]>hi[i] or b0[i+3]<lo[i] for i in range(3))
    mx=0; bad=0
    for k in range(len(P)):
        X=kernel.apply(man,P[k])
        if k: 
            W0=V@P[k-1][:3,:3].T+P[k-1][:3,3]; W1=V@P[k][:3,:3].T+P[k][:3,3]; mx=max(mx,np.linalg.norm(W1-W0,axis=1).max())
        for q in placed:
            if kernel.bbox_overlap(X,get(q)) and kernel.ivol(X,get(q))>1e-6: bad+=1; print('  collide',n,q,k)
    print(n,'start outside',outside,'max step',round(mx,4),'collisions',bad,'last identity',np.allclose(P[-1],np.eye(4)))
    placed.append(n)
