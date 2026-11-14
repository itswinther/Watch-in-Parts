from common import *
from fractions import Fraction as F
import math
m=mv()
cache={}
def L(n):
    if n not in cache: cache[n]=barrel() if n=='barrel' else load(n)
    return cache[n]
fixed=kernel.union([L(n) for n in m['fixed']])
mobs={k:v for k,v in m['mobiles'].items()}; mobs['barrel']={'axis':[0,0],'parts':['barrel']}
mm={k:kernel.union([L(p) for p in v['parts']]) for k,v in mobs.items()}
def rot(man,ax,deg):
    a=math.radians(deg); c,s=math.cos(a),math.sin(a); x,y=ax
    T=np.array([[c,-s,0,x-c*x+s*y],[s,c,0,y-s*x-c*y],[0,0,1,0],[0,0,0,1]])
    return kernel.apply(man,T)
# speeds (turns per hour, + = cw)
sp={'barrel':F(1,8)}
ch=True
while ch:
    ch=False
    for e in m['meshes']:
        if e['driver'] in sp and e['driven'] not in sp:
            sp[e['driven']]=-sp[e['driver']]*F(e['driver_teeth'],e['driven_teeth']); ch=True
print('speeds',sp)
new=['day']
# fixed overlaps
fx=m['fixed']
for i in range(len(fx)):
    for j in range(i+1,len(fx)):
        v=kernel.ivol(L(fx[i]),L(fx[j]))
        if v>0.001: print('fixed overlap',fx[i],fx[j],v)
for k in mm:
    v=kernel.ivol(mm[k],fixed); 
    if v>0.001: print('mob-fixed',k,v)
ks=list(mm)
for i in range(len(ks)):
    for j in range(i+1,len(ks)):
        v=kernel.ivol(mm[ks[i]],mm[ks[j]])
        if v>0.001: print('mob-mob',ks[i],ks[j],v)
for k in new:
    ax=mobs[k]['axis']
    worst=max(kernel.ivol(rot(mm[k],ax,5*i),fixed) for i in range(72)); print('free',k,worst)
    others=kernel.union([mm[o] for o in mm if o!=k]+[fixed])
    same=kernel.union([fixed]+[mm[o] for o in mm if o!=k and abs(mobs[o]['axis'][0]-ax[0])<0.01 and abs(mobs[o]['axis'][1]-ax[1])<0.01])
    for d in [(0.3,0,0),(-0.3,0,0),(0,0.3,0),(0,-0.3,0),(0,0,0.3),(0,0,-0.3)]:
        tgt=others if d[2]==0 else same
        print('held',k,d,round(kernel.ivol(kernel.apply(mm[k],kernel.translation(d)),tgt),4))
    # size
    v=kernel.verts(mm[k]); r=np.hypot(v[:,0]-m['case_centre'][0],v[:,1]-m['case_centre'][1])
    # max radius as it turns: dist axis-centre + max r from axis
    ra=np.hypot(v[:,0]-ax[0],v[:,1]-ax[1]).max(); print('size',np.hypot(ax[0]-m['case_centre'][0],ax[1]-m['case_centre'][1])+ra, v[:,2].min(), v[:,2].max())
    print('reach', np.hypot(*(kernel.verts(L(m['hands'][k]['part']))[:,:2]-ax).T).max() if k in [h['mobile'] for h in m['hands'].values()] else '')
# run test on new meshes
for e in m['meshes']:
    if e['driven'] not in new: continue
    a,b=e['driver'],e['driven']; ta,tb=e['driver_teeth'],e['driven_teeth']
    A,B=mm[a],mm[b]; axa,axb=mobs[a]['axis'],mobs[b]['axis']
    n=8*max(ta,tb); bad=0; maxi=0; maxd=0; mindrive=1e9
    for i in range(n):
        da=i*360/(8*ta); db=da*ta/tb
        Ai=rot(A,axa,da); Bi=rot(B,axb,-db)
        v=kernel.ivol(Ai,Bi); maxi=max(maxi,v)
        if i%4==0: maxd=max(maxd,kernel.min_distance(Ai,Bi,1.0))
        if i%8==0: mindrive=min(mindrive,kernel.ivol(rot(A,axa,da+90/ta),Bi))
    print('mesh',a,b,'maxint',maxi,'maxdist',maxd,'mindrive',mindrive)
# nothing else collides: day vs all non-meshing
meshp={(e['driver'],e['driven']) for e in m['meshes']}|{(e['driven'],e['driver']) for e in m['meshes']}
for k in new:
    for o in mm:
        if o==k or (k,o) in meshp: continue
        if not kernel.bbox_overlap(mm[k],mm[o],0) and True:
            # check swept bbox overlap
            pass
        sk,so=float(sp.get(k,0)),float(sp.get(o,0))
        fast=max(abs(sk),abs(so)); worst=0
        rel=abs(sk-so)
        for base in [fast, rel]:
            if base==0: continue
            for i in range(144):
                t=i/144/base
                worst=max(worst,kernel.ivol(rot(mm[k],mobs[k]['axis'],-360*sk*t),rot(mm[o],mobs[o]['axis'],-360*so*t)))
        if worst>0.0: print('collide',k,o,worst)
print('done')
