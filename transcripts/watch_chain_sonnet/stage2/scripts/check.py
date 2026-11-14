import sys,json,math,numpy as np
sys.path.insert(0,'tools')
import kernel as k
from fractions import Fraction
mv=json.load(open('work/movement.json'))
P={}
def part(n):
    if n not in P: P[n]=k.load_part(f'work/parts/{n}.stl',200000,1<<25,1e-3)
    return P[n]
bar=k.load_part('meshes/barrel.stl',200000,1<<25,1e-3)
fixed=k.union([part(n) for n in mv['fixed']])
mob={'barrel':(k.union([bar]),np.zeros(2))}
for n,m in mv['mobiles'].items(): mob[n]=(k.union([part(p) for p in m['parts']]),np.array(m['axis']))
def rot(man,ax,deg):
    a=math.radians(deg);c,s=math.cos(a),math.sin(a)
    T=np.eye(4);T[:2,:2]=[[c,-s],[s,c]]
    T[:2,3]=ax-T[:2,:2]@ax
    return k.apply(man,T)
# fixed overlaps
fl=[part(n) for n in mv['fixed']]
for i in range(len(fl)):
    for j in range(i):print('fixed',i,j,k.ivol(fl[i],fl[j]))
for n,(m,ax) in mob.items():
    print(n,'asm vs fixed',round(k.ivol(m,fixed),4),end=' ')
    # free turn
    mx=max(k.ivol(rot(m,ax,5*i),fixed) for i in range(72)); print('turn max',round(mx,4),end=' ')
    h=[]
    for d in [(.3,0,0),(-.3,0,0),(0,.3,0),(0,-.3,0),(0,0,.3),(0,0,-.3)]:
        mm=k.apply(m,k.translation(d)); v=k.ivol(mm,fixed)
        for n2,(o,ax2) in mob.items():
            if n2==n: continue
            if d[2]!=0 and np.linalg.norm(ax2-ax)>0.01: continue
            v+=k.ivol(mm,o)
        h.append(round(v,3))
    print('held',h)
def speeds():
    sp={'barrel':Fraction(-1)}
    ch=True
    while ch:
        ch=False
        for e in mv['meshes']:
            a,b=e['driver'],e['driven']
            if a in sp and b not in sp: sp[b]=-sp[a]*Fraction(e['driver_teeth'],e['driven_teeth']);ch=True
    return sp
sp=speeds();print({k_:str(v) for k_,v in sp.items()})
only=sys.argv[1:] 
for e in mv['meshes']:
    a,b=e['driver'],e['driven']
    if only and not(a in only or b in only): continue
    (A,ax),(B,bx)=mob[a],mob[b]; Nd,Nn=e['driver_teeth'],e['driven_teeth']
    bad=0;far=0;noh=0
    for i in range(8*max(Nd,Nn)):
        ang=i*360/(8*Nd)
        A2=rot(A,ax,ang);B2=rot(B,bx,-ang*Nd/Nn)
        v=k.ivol(A2,B2)
        if v>0.01:bad+=1
        if i%4==0 and k.min_distance(A2,B2,0.2)>0.1:far+=1
        if i%8==0:
            if k.ivol(rot(A,ax,ang+90/Nd),B2)<=0.01:noh+=1
    print('mesh',a,b,'jam',bad,'disengaged',far,'nodrive',noh)
meshed={frozenset((e['driver'],e['driven'])) for e in mv['meshes']}
names=list(mob)
for a in ['D','T']:
  for b in names:
    if a==b or frozenset((a,b)) in meshed: continue
    (A,ax),(B,bx)=mob[a],mob[b]; sa,sb=sp[a],sp[b]
    mxv=0
    big=max(abs(sa),abs(sb))
    for i in range(288):
        if i<144: t=i/144; ta=-sa*t*360/ big*1 ; tb=-sb*t*360/big
        else: t=(i-144)/144; ta=0; tb=(sb-sa)*t*360/ (abs(sb-sa) or 1)*(1 if sb!=sa else 0)
        # sign convention: speeds negative=cw; rotate ccw positive degrees
        v=k.ivol(rot(A,ax,float(ta)),rot(B,bx,float(tb)));mxv=max(mxv,v)
    print('nomesh',a,b,round(mxv,4))
bb=[m.bounding_box() for m,_ in mob.values()]+[fixed.bounding_box()]
print('zrange',min(b[2] for b in bb),max(b[5] for b in bb))
cc=np.array(mv['case_centre']);R=0
for n,(m,ax) in mob.items():
    v=k.verts(m);R=max(R,np.hypot(*(v[:,:2]-cc).T).max())
print('max radius mobiles',R)
