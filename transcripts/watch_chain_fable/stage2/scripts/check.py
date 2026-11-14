import sys,json,itertools,time
sys.path.insert(0,'tools')
import kernel as K, numpy as np
from fractions import Fraction as F
W=sys.argv[1] if len(sys.argv)>1 else 'work'
only_new=len(sys.argv)>2
doc=json.load(open(W+'/movement.json'))
L=lambda n:K.load_part(W+'/parts/%s.stl'%n,200000,1<<25,0.005)
fixed=K.union([L(n) for n in doc['fixed']])
fx=[L(n) for n in doc['fixed']]
mob={k:K.union([L(n) for n in m['parts']]) for k,m in doc['mobiles'].items()}
axis={k:np.array(m['axis'],float) for k,m in doc['mobiles'].items()}
mob['barrel']=K.load_part('meshes/barrel.stl',200000,1<<25,0.005); axis['barrel']=np.zeros(2)
def rot(k,deg):  # ccw positive
    a=np.radians(deg); c,s=np.cos(a),np.sin(a); x,y=axis[k]
    T=np.eye(4); T[:2,:2]=[[c,-s],[s,c]]; T[0,3]=x-c*x+s*y; T[1,3]=y-s*x-c*y
    return K.apply(mob[k],T)
ok=True
def rep(name,passed,info=''):
    global ok; ok&=bool(passed); print('PASS' if passed else 'FAIL',name,info,flush=True)
# hard
worst=0
for a,b in itertools.combinations(range(len(fx)),2): worst=max(worst,K.ivol(fx[a],fx[b]))
names=list(mob)
for k in names: worst=max(worst,K.ivol(fixed,mob[k]))
for a,b in itertools.combinations(names,2):
    v=K.ivol(mob[a],mob[b]); worst=max(worst,v)
    if v>0.001: print('  overlap',a,b,v)
rep('assembled',worst<=0.01,worst)
# speeds (ccw positive turns per hour)
sp={'barrel':F(-1,8)}
ch=True; cons=True
while ch:
    ch=False
    for e in doc['meshes']:
        for a,b,ta,tb in ((e['driver'],e['driven'],e['driver_teeth'],e['driven_teeth']),(e['driven'],e['driver'],e['driven_teeth'],e['driver_teeth'])):
            if a in sp:
                s=-sp[a]*ta/tb
                if b not in sp: sp[b]=s; ch=True
                elif sp[b]!=s: cons=False
print({k:str(1/v) if v else 0 for k,v in sp.items()})
rep('speeds consistent',cons)
for h,per in (('hour',12),('minute',1),('seconds',F(1,60)),('day',24)):
    if h in doc['hands']: rep('hand '+h, sp.get(doc['hands'][h]['mobile'])==-1/F(per))
# size
cc=np.array(doc['case_centre']); zs=[];rmax=0
for k in names:
    v=K.verts(mob[k]); zs+=[v[:,2].min(),v[:,2].max()]
    rmax=max(rmax,np.linalg.norm(axis[k]-cc)+np.linalg.norm(v[:,:2]-axis[k],axis=1).max())
v=K.verts(fixed); zs+=[v[:,2].min(),v[:,2].max()]; rmax=max(rmax,np.linalg.norm(v[:,:2]-cc,axis=1).max())
rep('size',rmax<=23 and max(zs)-min(zs)<=16,(rmax,max(zs)-min(zs)))
for h,need in (('hour',5),('minute',5),('seconds',5),('day',3)):
    if h in doc['hands']:
        e=doc['hands'][h]; v=K.verts(L(e['part'])); rep('reach '+h,np.linalg.norm(v[:,:2]-axis[e['mobile']],axis=1).max()>=need)
if 'day' in doc['hands']:
    rep('day placement',np.linalg.norm(axis[doc['hands']['day']['mobile']]-axis[doc['hands']['hour']['mobile']])>=6)
# free
w=0
for k in names:
    for i in range(72): w=max(w,K.ivol(fixed,rot(k,5*i)))
rep('free to turn',w<=0.01,w)
# held
allh=True
for k in names:
    for d in ([.3,0,0],[-.3,0,0],[0,.3,0],[0,-.3,0],[0,0,.3],[0,0,-.3]):
        m=K.apply(mob[k],K.translation(d))
        if d[2]==0: others=[fixed]+[mob[j] for j in names if j!=k]
        else: others=[fixed]+[mob[j] for j in names if j!=k and np.linalg.norm(axis[j]-axis[k])<=0.01]
        v=K.ivol(m,K.union(others))
        if v<=0.01: allh=False; print('  not held',k,d,v)
        elif v<0.03: print('  marginal',k,d,v)
rep('held',allh)
# meshes
t0=time.time()
for e in doc['meshes']:
    a,b,ta,tb=e['driver'],e['driven'],e['driver_teeth'],e['driven_teeth']
    if only_new and not (a.startswith('day') or b.startswith('day')): continue
    jam=0; gap=0; drive=1e9
    for i in range(8*max(ta,tb)):
        ang=i*360/(8*ta)
        A=rot(a,ang); B=rot(b,-ang*ta/tb)
        jam=max(jam,K.ivol(A,B))
        if i%4==0: gap=max(gap,K.min_distance(A,B,1.0))
        if i%8==0: drive=min(drive,K.ivol(rot(a,ang+90/ta),B))
    rep('mesh %s>%s'%(a,b),jam<=0.01 and gap<=0.1 and drive>0.01,'jam %.4f gap %.4f drive %.4f'%(jam,gap,drive))
# non-mesh pairs
meshed={frozenset((e['driver'],e['driven'])) for e in doc['meshes']}
w=0
for a,b in itertools.combinations(names,2):
    if frozenset((a,b)) in meshed: continue
    if only_new and not (a.startswith('day') or b.startswith('day')): continue
    if not K.bbox_overlap(rot(a,0),rot(b,0),30): continue
    ra=np.linalg.norm(K.verts(mob[a])[:,:2]-axis[a],axis=1).max(); rb=np.linalg.norm(K.verts(mob[b])[:,:2]-axis[b],axis=1).max()
    za=mob[a].bounding_box(); zb=mob[b].bounding_box()
    if np.linalg.norm(axis[a]-axis[b])>ra+rb or za[5]<zb[2] or zb[5]<za[2]: continue
    sa,sb=sp.get(a,F(0)),sp.get(b,F(0))
    sched=[]
    fast=max(abs(sa),abs(sb))
    if fast:
        for i in range(144): sched.append((float(sa/fast)*i*2.5,float(sb/fast)*i*2.5))
    rel=abs(sa-sb)
    if rel:
        for i in range(144): sched.append((float(sa/rel)*i*2.5,float(sb/rel)*i*2.5))
    for x,y in sched:
        v=K.ivol(rot(a,x),rot(b,y))
        if v>w: w=v; 
        if v>0.01: print('  collide',a,b,v); break
rep('nothing else collides',w<=0.01,w)
print('ALL OK' if ok else 'SOME FAIL', time.time()-t0)
