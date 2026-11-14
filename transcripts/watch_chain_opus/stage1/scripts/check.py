import sys, json, numpy as np
sys.path.insert(0,'tools'); import kernel as K
from fractions import Fraction as F
FULL='full' in sys.argv
d=json.load(open('work/movement.json'))
L=lambda n:K.load_part('work/parts/%s.stl'%n,200000,1<<25,1e-6)
fixed=K.union([L(n) for n in d['fixed']])
mob={k:K.union([L(n) for n in v['parts']]) for k,v in d['mobiles'].items()}
ax={k:v['axis'] for k,v in d['mobiles'].items()}
mob['barrel']=L('../../meshes/barrel') if False else K.tris_to_manifold(K.read_stl('meshes/barrel.stl',10**6,1<<26)); ax['barrel']=[0,0]
def rot(m,a,deg):
    T=np.eye(4); c,s=np.cos(np.radians(deg)),np.sin(np.radians(deg))
    T[:2,:2]=[[c,-s],[s,c]]; T[:2,3]=np.array(a)-T[:2,:2]@np.array(a); return K.apply(m,T)
bad=[]
for k,m in mob.items():
    v=K.ivol(m,fixed)
    if v>0.01: bad.append(('assembled-fixed',k,v))
ks=list(mob)
for i in range(len(ks)):
    for j in range(i+1,len(ks)):
        v=K.ivol(mob[ks[i]],mob[ks[j]])
        if v>0.01: bad.append(('assembled',ks[i],ks[j],v))
print('hard',bad)
# free
for k,m in mob.items():
    for s in range(0,72,1 if FULL else 6):
        v=K.ivol(rot(m,ax[k],5*s),fixed)
        if v>0.01: print('free FAIL',k,s,v); break
# held
for k,m in mob.items():
    for dvec in [(0.3,0,0),(-0.3,0,0),(0,0.3,0),(0,-0.3,0),(0,0,0.3),(0,0,-0.3)]:
        mm=K.apply(m,K.translation(dvec))
        others=[o for o in mob if o!=k and (dvec[2]==0 or np.hypot(*(np.array(ax[o])-ax[k]))<0.01)]
        v=K.ivol(mm,fixed)+sum(K.ivol(mm,mob[o]) for o in others)
        if v<=0.01: print('held FAIL',k,dvec,v)
# speeds
sp={'barrel':F(-1,8)}
for e in d['meshes']: sp[e['driven']]=-sp[e['driver']]*F(e['driver_teeth'],e['driven_teeth'])
print('speeds rev/h (+ccw)',sp)
for e in d['meshes']:
    a,b=e['driver'],e['driven'];Na,Nb=e['driver_teeth'],e['driven_teeth']
    n=8*max(Na,Nb); fails=[]
    for i in range(0,n,1 if FULL else 7):
        da=i*360/(8*Na); db=-da*Na/Nb
        A=rot(mob[a],ax[a],da); B=rot(mob[b],ax[b],db)
        v=K.ivol(A,B)
        if v>0.01: fails.append(('jam',i,v))
        if i%4==0 and K.min_distance(A,B,1.0)>0.1: fails.append(('disengage',i))
        if i%8==0:
            v2=K.ivol(rot(mob[a],ax[a],da+90/Na),B)
            if v2<=0.01: fails.append(('nodrive',i,v2))
    print('mesh',a,b,'fails',fails[:5],len(fails))
# non-meshing pairs
pairs={frozenset((e['driver'],e['driven'])) for e in d['meshes']}
for i in range(len(ks)):
    for j in range(i+1,len(ks)):
        a,b=ks[i],ks[j]
        if frozenset((a,b)) in pairs: continue
        wa,wb=float(sp.get(a,0)),float(sp.get(b,0)); f=max(abs(wa),abs(wb)); rel=wa-wb
        sched=[(s*360/144*wa/f,s*360/144*wb/f) for s in range(144)] if f>0 else []
        if abs(rel)>0: sched+=[(s*360/144*wa/abs(rel),s*360/144*wb/abs(rel)) for s in range(144)]
        for (x,y) in sched[::1 if FULL else 9]:
            v=K.ivol(rot(mob[a],ax[a],x),rot(mob[b],ax[b],y))
            if v>0.01: print('collide',a,b,x,y,v); break
# size
C=np.array(d['case_centre']); zs=[]
allm=list(mob.items())+[('fixed',fixed)]
rmax=0
for k,m in allm:
    V=K.verts(m); a=np.array(ax.get(k,C)); 
    r=np.linalg.norm(V[:,:2]-a,axis=1).max()+np.linalg.norm(a-C) if k!='fixed' else np.linalg.norm(V[:,:2]-C,axis=1).max()
    rmax=max(rmax,r); zs+= [V[:,2].min(),V[:,2].max()]
print('rmax',rmax,'height',max(zs)-min(zs))
for h,v in d['hands'].items():
    V=K.verts(L(v['part'])); print(h,'reach',np.linalg.norm(V[:,:2]-ax[v['mobile']],axis=1).max())
