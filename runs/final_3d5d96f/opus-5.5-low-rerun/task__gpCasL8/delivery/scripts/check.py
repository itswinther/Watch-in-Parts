import sys,json,itertools,numpy as np,time
sys.path.insert(0,'/app/work')
from load import *
from design import speeds as SPD, MOBILE_NAMES
build=sys.argv[1] if len(sys.argv)>1 else '8h'
mv=json.load(open('/app/delivery/'+('movement.json' if build=='8h' else 'variant_6h.json')))
inv={v:k for k,v in MOBILE_NAMES.items()}
n=SPD(build)
parts={}
owner={}
for p in mv['fixed']: parts[p]=part(p); owner[p]='frame'
for mn,m in mv['mobiles'].items():
    for p in m['parts']: parts[p]=part(p); owner[p]=mn
parts['barrel']=barrel(); owner['barrel']='barrel'
axis={mn:m['axis'] for mn,m in mv['mobiles'].items()}; axis['barrel']=[0,0]
speed={mn:n[inv[mn]] for mn in mv['mobiles']}; speed['barrel']=n['barrel']
print('loaded',len(parts))
CC=np.array(mv['case_centre'])
# case & height
lo=min(p.bounding_box()[2] for p in parts.values()); hi=max(p.bounding_box()[5] for p in parts.values())
print('height',round(hi-lo,4),lo,hi)
for k,p in parts.items():
    v=kernel.verts(p); r=np.hypot(v[:,0]-CC[0],v[:,1]-CC[1]).max()
    if r>12.65: print('CASE radius',k,r)
def pose(k,t):
    o=owner[k]
    if o=='frame': return parts[k]
    a=2*np.pi*speed[o]*t
    return rotz(parts[k],axis[o][0],axis[o][1],a)
names=list(parts)
def check_pairs(t,tag,pairs=None,report=True):
    P={k:pose(k,t) for k in names}
    worst=[]
    for a,b in (pairs or itertools.combinations(names,2)):
        if owner[a]==owner[b]: continue
        if not kernel.bbox_overlap(P[a],P[b],0.05): continue
        v=kernel.ivol(P[a],P[b])
        d=kernel.min_distance(P[a],P[b],0.1) if v<=1e-9 else 0
        worst.append((d,v,a,b))
    worst.sort()
    if report:
        for d,v,a,b in worst[:6]: print(tag,'%s-%s d=%.4f v=%.5f'%(a,b,d,v))
    return worst
w=check_pairs(0,'t0')
pairs=[(a,b) for d,v,a,b in w if d<0.1]
print('close pairs',len(pairs))
# sweep: slowest relevant motion - sample times so fastest mobile turns 1/12 turn; plus long times
ts=list(np.linspace(0,1/60/12,25))+list(np.linspace(0,1/12,13))+list(np.linspace(0,1.0,13))+list(np.linspace(0,8.0,33))
mind={}
for t in ts:
    for d,v,a,b in check_pairs(t,'',pairs,False):
        key=(a,b); mind[key]=min(mind.get(key,9),d if v<=1e-9 else -v)
for k,v in sorted(mind.items(),key=lambda x:x[1])[:15]: print('sweep',k,round(v,4))
