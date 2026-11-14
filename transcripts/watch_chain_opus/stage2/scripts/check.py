import sys,json; sys.path.insert(0,'tools')
import kernel as K, numpy as np
from fractions import Fraction as F
d=json.load(open('work/movement.json'))
def L(n,dir='work/parts'): return K.load_part(f'{dir}/{n}.stl',200000,1<<25,.005)
fixed=K.union([L(n) for n in d['fixed']])
fixl={n:L(n) for n in d['fixed']}
mob={k:(np.array(v['axis']),K.union([L(n) for n in v['parts']])) for k,v in d['mobiles'].items()}
mob['barrel']=(np.zeros(2),K.load_part('meshes/barrel.stl',200000,1<<25,.005))
NEW=set(sys.argv[1:]) or set(mob)
def rot(m,ax,deg):
    a=np.radians(deg);c,s=np.cos(a),np.sin(a)
    T=np.array([[c,-s,0,ax[0]-c*ax[0]+s*ax[1]],[s,c,0,ax[1]-s*ax[0]-c*ax[1]],[0,0,1,0],[0,0,0,1]])
    return K.apply(m,T)
# speeds (rev per hour, CCW positive)
sp={'barrel':F(-1,8)}
ch=True
while ch:
    ch=False
    for e in d['meshes']:
        a,b=e['driver'],e['driven']
        if a in sp and b not in sp: sp[b]=-sp[a]*e['driver_teeth']/e['driven_teeth']; ch=True
        if b in sp and a not in sp: sp[a]=-sp[b]*e['driven_teeth']/e['driver_teeth']; ch=True
for e in d['meshes']:
    assert sp[e['driven']]==-sp[e['driver']]*e['driver_teeth']/e['driven_teeth'],e
print({k:str(v) for k,v in sp.items()})
bad=0
fn=list(fixl)
for i in range(len(fn)):
    for j in range(i+1,len(fn)):
        v=K.ivol(fixl[fn[i]],fixl[fn[j]])
        if v>0.01: print('FIXED OVERLAP',fn[i],fn[j],v); bad+=1
names=list(mob)
for k in names:
    v=K.ivol(mob[k][1],fixed)
    if v>0.01: print('ASSEMBLED mobile-fixed',k,v); bad+=1
    for k2 in names:
        if k<k2:
            v=K.ivol(mob[k][1],mob[k2][1])
            if v>0.01: print('ASSEMBLED',k,k2,v); bad+=1
# free to turn
for k in names:
    if k not in NEW and 'free' not in NEW: continue
    ax,m=mob[k]
    for s in range(72):
        v=K.ivol(rot(m,ax,5*s),fixed)
        if v>0.01: print('TURN',k,s,v); bad+=1; break
# held
for k in names:
    if k not in NEW: continue
    ax,m=mob[k]
    for dv in [(.3,0,0),(-.3,0,0),(0,.3,0),(0,-.3,0),(0,0,.3),(0,0,-.3)]:
        mm=K.apply(m,K.translation(dv))
        others=[fixed]+[mob[o][1] for o in names if o!=k and (dv[2]==0 or np.linalg.norm(mob[o][0]-ax)<0.01)]
        if not any(K.ivol(mm,o)>0.01 for o in others): print('NOT HELD',k,dv); bad+=1
# meshes
for e in d['meshes']:
    a,b=e['driver'],e['driven']
    if a not in NEW and b not in NEW: continue
    na,nb=e['driver_teeth'],e['driven_teeth']
    (axa,ma),(axb,mb)=mob[a],mob[b]
    for i in range(8*max(na,nb)):
        ang=i*360/(8*na)
        A=rot(ma,axa,ang); B=rot(mb,axb,-ang*na/nb)
        if K.ivol(A,B)>0.01: print('JAM',a,b,i); bad+=1; break
        if i%4==0 and K.min_distance(A,B,1.0)>0.1: print('DISENGAGED',a,b,i); bad+=1; break
        if i%8==0 and K.ivol(rot(ma,axa,ang+90/na),B)<=0.01: print('NO DRIVE',a,b,i); bad+=1; break
    print('mesh done',a,b)
# nothing else collides
meshed={frozenset((e['driver'],e['driven'])) for e in d['meshes']}
for i,a in enumerate(names):
    for b in names[i+1:]:
        if frozenset((a,b)) in meshed or (a not in NEW and b not in NEW): continue
        wa,wb=float(sp.get(a,0)),float(sp.get(b,0))
        (axa,ma),(axb,mb)=mob[a],mob[b]
        fast=max(abs(wa),abs(wb)); rel=abs(wa-wb)
        for T in ([1/fast] if fast else [])+([1/rel] if rel else []):
            for s in range(144):
                t=T*s/144
                if K.ivol(rot(ma,axa,-360*wa*t*-1),rot(mb,axb,360*wb*t))>0.01: print('COLLIDE',a,b,s); bad+=1; break
print('pairs done')
# size
cc=np.array(d['case_centre']); zs=[]
for k,(ax,m) in mob.items():
    V=K.verts(m); r=np.hypot(V[:,0]-ax[0],V[:,1]-ax[1]).max()+np.linalg.norm(ax-cc)
    if r>23: print('SIZE',k,r); bad+=1
    b=m.bounding_box(); zs+= [b[2],b[5]]
V=K.verts(fixed); print('fixed max r',np.hypot(V[:,0]-cc[0],V[:,1]-cc[1]).max())
b=fixed.bounding_box(); zs+=[b[2],b[5]]; print('height',max(zs)-min(zs))
print('BAD',bad)
