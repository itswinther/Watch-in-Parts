import json, math, sys, itertools
import numpy as np
sys.path.insert(0,'tools')
import kernel
from kernel import ivol, apply
mv=json.load(open('work/movement.json'))
def load(n): return kernel.load_step_part(f'work/parts/{n}.step',16777216,200000,0.001,0.1,500,120,4096,0.005)
barrel=kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl',200000,33554432))
def union(ms):
    r=ms[0]
    for m in ms[1:]: r=r+m
    return r
fixed={n:load(n) for n in mv['fixed']}
mob={'barrel':barrel}; axis={'barrel':(0,0)}
for k,v in mv['mobiles'].items():
    mob[k]=union([load(p) for p in v['parts']]); axis[k]=tuple(v['axis'])
fixedU=union(list(fixed.values()))
def rot(m,ax,deg,dz=(0,0,0)):
    a=math.radians(deg); c,s=math.cos(a),math.sin(a); x,y=ax
    T=np.array([[c,-s,0,x-c*x+s*y],[s,c,0,y-s*x-c*y],[0,0,1,0],[0,0,0,1]])
    return apply(m,T)
def tr(m,d): return apply(m,kernel.translation(d))
bad=[]
# hard
for a,b in itertools.combinations(fixed,2):
    v=ivol(fixed[a],fixed[b]); 
    if v>0.01: bad.append(('fixed-fixed',a,b,v))
for k,m in mob.items():
    v=ivol(m,fixedU)
    if v>0.01: bad.append(('mob-fixed',k,v))
for a,b in itertools.combinations(mob,2):
    v=ivol(mob[a],mob[b])
    if v>0.01: bad.append(('mob-mob',a,b,v))
print('hard',bad)
# free to turn
for k,m in mob.items():
    for i in range(72):
        v=ivol(rot(m,axis[k],5*i),fixedU)
        if v>0.01: bad.append(('free',k,i,v)); break
print('after free',bad)
# held
for k,m in mob.items():
    for d in [(.3,0,0),(-.3,0,0),(0,.3,0),(0,-.3,0),(0,0,.3),(0,0,-.3)]:
        mm=tr(m,d); v=ivol(mm,fixedU)
        for k2,m2 in mob.items():
            if k2==k: continue
            if d[2]!=0 and math.hypot(axis[k][0]-axis[k2][0],axis[k][1]-axis[k2][1])>0.01: continue
            v+=ivol(mm,m2)
        if v<=0.01: bad.append(('held',k,d,v))
print('after held',bad)
# train
teeth={'barrel':96}
for me in mv['meshes']:
    a,b=me['driver'],me['driven']; za,zb=me['driver_teeth'],me['driven_teeth']
    worst=0; mind=0; drive=1e9; N=8*max(za,zb)
    for i in range(N):
        ang=i*360/(8*za)
        A=rot(mob[a],axis[a],ang); B=rot(mob[b],axis[b],-ang*za/zb)
        v=ivol(A,B); worst=max(worst,v)
        if i%4==0:
            d=kernel.min_distance(A,B,0.5); mind=max(mind,d)
        if i%8==0:
            A2=rot(mob[a],axis[a],ang+90/za); v2=ivol(A2,B); drive=min(drive,v2)
    ok= worst<=0.01 and mind<=0.1 and drive>0.01
    print('mesh',a,b,ok,worst,mind,drive)
    if not ok: bad.append(('mesh',a,b))
print('after mesh',bad)
# size
mx=0
for k,m in mob.items():
    V=kernel.verts(m); c=np.array(axis[k]); r=np.hypot(*(V[:,:2]-c).T).max()
    print(k,'r',round(r,2))
cs=[(np.array(axis[k]),np.hypot(*(kernel.verts(m)[:,:2]-np.array(axis[k])).T).max()) for k,m in mob.items()]
from scipy.optimize import minimize
f=lambda c:max(np.hypot(*(a-c))+r for a,r in cs)
res=minimize(f,[8,8],method='Nelder-Mead'); print('centre',res.x,res.fun)
for n,m in list(fixed.items()):
    V=kernel.verts(m); print(n,'fixed rad',np.hypot(*(V[:,:2]-res.x).T).max())
zs=[kernel.verts(m)[:,2] for m in list(mob.values())+list(fixed.values())]
print('z',min(z.min() for z in zs),max(z.max() for z in zs))
# nonmeshing
meshed={frozenset((m['driver'],m['driven'])) for m in mv['meshes']}
for a,b in itertools.combinations(mob,2):
    if frozenset((a,b)) in meshed: continue
    # speeds not computed: assume all moving relative; test using sweep over relative rotations crude
    pass
json.dump(res.x.tolist(),open('scripts/centre.json','w'))
