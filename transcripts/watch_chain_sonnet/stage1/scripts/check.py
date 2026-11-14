import sys, json, math
sys.path.insert(0,'tools')
import numpy as np, manifold3d as m3
import kernel as K
from fractions import Fraction
mv=json.load(open('work/movement.json'))
def load(n): return K.load_part('work/parts/%s.stl'%n,200000,2**25,1e-3)
bar=K.tris_to_manifold(K.read_stl('meshes/barrel.stl',10**6,2**26))
fixed={n:load(n) for n in mv['fixed']}
mob={}
axes={'barrel':(0,0)}
mob['barrel']=bar
for k,m in mv['mobiles'].items():
    mob[k]=K.union([load(p) for p in m['parts']]); axes[k]=tuple(m['axis'])
F=K.union(list(fixed.values()))
def rotz(m,ax,deg):
    t=np.eye(4); a=math.radians(deg); c,s=math.cos(a),math.sin(a)
    t[:2,:2]=[[c,-s],[s,c]]; t[0,3]=ax[0]-c*ax[0]+s*ax[1]; t[1,3]=ax[1]-s*ax[0]-c*ax[1]
    return K.apply(m,t)
bad=0
# hard
fl=list(fixed.items())
for i in range(len(fl)):
  for j in range(i):
    v=K.ivol(fl[i][1],fl[j][1])
    if v>0.01: print('FIXED OVERLAP',fl[i][0],fl[j][0],v); bad+=1
for k,m in mob.items():
    v=K.ivol(m,F)
    if v>0.01: print('HARD mobile/fixed',k,v); bad+=1
names=list(mob)
# free
for k,m in mob.items():
    for s in range(72):
        v=K.ivol(rotz(m,axes[k],5*s),F)
        if v>0.01: print('FREE fail',k,s,v); bad+=1; break
# held
for k,m in mob.items():
    for d in [(.3,0,0),(-.3,0,0),(0,.3,0),(0,-.3,0),(0,0,.3),(0,0,-.3)]:
        mm=K.apply(m,K.translation(d))
        others=[F]+[mob[o] for o in names if o!=k and (d[2]==0 or math.dist(axes[o],axes[k])<0.01)]
        v=max(K.ivol(mm,o) for o in others)
        if v<=0.01: print('HELD fail',k,d,v); bad+=1
# train
spd={'barrel':Fraction(-1)}  # cw negative
for e in mv['meshes']:
    pass
meshpairs=set()
for e in mv['meshes']:
    d,n=e['driver'],e['driven']; meshpairs.add(frozenset((d,n)))
    spd.setdefault(n, spd[d]*Fraction(-e['driver_teeth'],e['driven_teeth']))
print({k:str(v) for k,v in spd.items()})
for e in mv['meshes']:
    d,n,zd,zn=e['driver'],e['driven'],e['driver_teeth'],e['driven_teeth']
    fails=0; mx=0; mind=0
    for i in range(8*max(zd,zn)):
        a=i*360/(8*zd)
        A=rotz(mob[d],axes[d],a); B=rotz(mob[n],axes[n],-a*zd/zn)
        v=K.ivol(A,B); mx=max(mx,v)
        if v>0.01: fails+=1
        if i%4==0:
            dd=K.min_distance(A,B,0.5)
            if dd>0.1: print('  engage fail',d,n,i,dd); fails+=1
        if i%8==0:
            A2=rotz(mob[d],axes[d],a+90/zd)
            if K.ivol(A2,B)<=0.01: print('  drive fail',d,n,i,K.ivol(A2,B)); fails+=1; 
    print('mesh',d,n,'maxvol',mx,'fails',fails); bad+=fails>0
# others
for i in range(len(names)):
  for j in range(i):
    a,b=names[i],names[j]
    if frozenset((a,b)) in meshpairs: continue
    sa=spd.get(a,Fraction(0)) if a!='barrel' else spd['barrel']; sb=spd.get(b,Fraction(0))
    fa,fb=float(sa),float(sb)
    fast=max(abs(fa),abs(fb))
    mx=0
    # phase 1: both turn together, faster does one full turn
    for s in range(144):
        t=s/144*360/fast
        v=K.ivol(rotz(mob[a],axes[a],t*fa),rotz(mob[b],axes[b],t*fb)); mx=max(mx,v)
    # phase 2: relative turn
    rel=fa-fb
    for s in range(144):
        t=s/144*360/ (abs(rel) if rel else 1)
        v=K.ivol(rotz(mob[a],axes[a],t*fa),rotz(mob[b],axes[b],t*fb)); mx=max(mx,v)
    if mx>0.01: print('COLLIDE',a,b,mx); bad+=1
# size
allv=np.concatenate([K.verts(m) for m in list(mob.values())+list(fixed.values())])
print('zrange',allv[:,2].min(),allv[:,2].max())
cc=np.array(mv['case_centre'])
# max radius incl rotation: per-mobile max distance from axis + axis dist
mr=0
for k,m in mob.items():
    v=K.verts(m); r=np.hypot(*(v[:,:2]-axes[k]).T).max(); mr=max(mr,np.hypot(*(np.array(axes[k])-cc))+r)
for k,m in fixed.items():
    v=K.verts(m); mr=max(mr,np.hypot(*(v[:,:2]-cc).T).max())
print('max radius',mr)
print('BAD',bad)
