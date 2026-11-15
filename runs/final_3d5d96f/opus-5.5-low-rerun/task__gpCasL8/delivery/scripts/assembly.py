import sys,json,numpy as np
sys.path.insert(0,'/app/work')
from load import *
mv=json.load(open('/app/delivery/movement.json'))
parts={p:part(p) for p in mv['fixed']}
for m in mv['mobiles'].values():
    for p in m['parts']: parts[p]=part(p)
parts['barrel']=barrel()
allm=kernel.union(list(parts.values())); bb=allm.bounding_box()
TOP=bb[5]
pref=['plate','barrel','plate2']+[m['parts'][0] for m in mv['mobiles'].values()]+['dial','hand_day','hand_minute','hand_hour','hand_seconds']
def descent_ok(name,placed,step=0.05):
    P=parts[name]; pb=P.bounding_box()
    dz0=TOP+5.2-pb[2]
    for dz in np.arange(dz0,-1e-9,-step)[::-1]:   # check from bottom (final) upward: fail fast near final
        Q=P.translate([0,0,float(dz)])
        for o in placed:
            if kernel.bbox_overlap(Q,parts[o]) and kernel.ivol(Q,parts[o])>1e-6: return False,(o,dz)
    return True,dz0
phase=lambda n: 0 if n in('plate',) else 1 if n=='barrel' else 2 if n=='plate2' else 4 if n=='dial' else 5 if n.startswith('hand') else 3
# pairwise: must a come before b?  (b descending collides with a placed -> b before a)
import itertools
names=pref
before={n:set() for n in names}   # before[n] = set of parts that must precede n
for a,b in itertools.permutations(names,2):
    if phase(a)!=phase(b): 
        if phase(a)<phase(b): before[b].add(a)
        continue
    ok,info=descent_ok(b,[a])
    if not ok: before[a].add(b)   # b must be placed before a
order=[];remaining=list(names)
while remaining:
    for nm in remaining:
        if before[nm]<=set(order):
            order.append(nm);remaining.remove(nm);break
    else:
        print('CYCLE',remaining,{n:before[n]-set(order) for n in remaining});break
# verify full sequence
for i,nm in enumerate(order):
    ok,info=descent_ok(nm,order[:i])
    print('verify',nm,ok,info if not ok else '')
    if not ok: remaining=[nm]
def path(name):
    pb=parts[name].bounding_box(); dz0=TOP+5.3-pb[2]
    n=int(np.ceil(dz0/0.18))
    out=[]
    for i in range(n+1):
        dz=dz0*(1-i/n); T=np.eye(4); T[2,3]=dz; out.append(T.round(9).tolist())
    out[-1]=np.eye(4).tolist()
    return out
if not remaining:
    json.dump({'order':order,'paths':{p:path(p) for p in order}},open('/app/delivery/assembly.json','w'))
    print('written',order)
