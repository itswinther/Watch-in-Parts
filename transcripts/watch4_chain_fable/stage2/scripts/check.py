"""Own implementation of the spec tests. usage: check.py [quick]"""
from common import *
from fractions import Fraction
import time,hashlib
quick='quick' in sys.argv
fast='fast' in sys.argv
t0=time.time()
mv,P=load_all('work')
print('loaded %.0fs'%(time.time()-t0),flush=True)
old=json.load(open('previous/movement.json'))
B=barrel()
ok=True
def rep(name,passed,info=''):
    global ok; ok&=bool(passed); print('PASS' if passed else 'FAIL',name,info,flush=True)
# frozen
fr=True
for n,m in old['mobiles'].items():
    fr&= mv['mobiles'][n]['axis']==m['axis']
    for p in m['parts']:
        fr&= p in mv['mobiles'][n]['parts']
        fr&= open('work/parts/%s.step'%p,'rb').read()==open('previous/parts/%s.step'%p,'rb').read()
fr&= all(m in mv['meshes'] for m in old['meshes']) and all(mv['hands'][h]==old['hands'][h] for h in old['hands'])
oldparts=set(old['fixed'])|{p for m in old['mobiles'].values() for p in m['parts']}
fr&= mv['hands']['day']['part'] in mv['mobiles'][mv['hands']['day']['mobile']]['parts'] and mv['hands']['day']['part'] not in oldparts
rep('frozen+day declared',fr)
F=kernel.union([P[n] for n in mv['fixed']])
MOB={n:kernel.union([P[p] for p in m['parts']]) for n,m in mv['mobiles'].items()}
AX={n:m['axis'] for n,m in mv['mobiles'].items()}
MOB['barrel']=B; AX['barrel']=[0.0,0.0]
# assembled
worst=max(kernel.ivol(F,M) for M in MOB.values()); 
names=list(MOB)
NEW=[n for n in names if n not in old['mobiles'] and n!='barrel']
for i,a in enumerate(names):
    for b in names[i+1:]:
        if fast and a not in NEW and b not in NEW: continue
        v=kernel.ivol(MOB[a],MOB[b]); worst=max(worst,v)
        if v>0: print('  overlap',a,b,v)
fx=mv['fixed']
for i,a in enumerate(fx):
    for b in fx[i+1:]: worst=max(worst,kernel.ivol(P[a],P[b]))
rep('assembled',worst<=0.01,worst)
# free to turn
w=0
for n in (NEW if fast else names):
    for k in range(72): w=max(w,kernel.ivol(F,kernel.apply(MOB[n],rotz(5*k,AX[n]))))
rep('free to turn',w<=0.01,w)
# held
h=True
for n in (NEW if fast else names):
    side=kernel.union([F]+[MOB[o] for o in names if o!=n])
    zz=kernel.union([F]+[MOB[o] for o in names if o!=n and np.hypot(AX[o][0]-AX[n][0],AX[o][1]-AX[n][1])<=0.01])
    for d in ([.3,0,0],[-.3,0,0],[0,.3,0],[0,-.3,0],[0,0,.3],[0,0,-.3]):
        v=kernel.ivol(kernel.apply(MOB[n],kernel.translation(d)),zz if d[2] else side)
        if v<=0.01: h=False; print('  not held',n,d,v)
rep('held',h)
# speeds (turns per hour, cw positive)
sp={'barrel':Fraction(1,8)}; cons=True
for _ in range(20):
    for m in mv['meshes']:
        if m['driver'] in sp:
            s=-sp[m['driver']]*m['driver_teeth']/m['driven_teeth']
            if m['driven'] in sp and sp[m['driven']]!=s: cons=False
            sp[m['driven']]=s
print({k:str(v) for k,v in sp.items()})
H=mv['hands']
rep('speeds',cons and sp[H['hour']['mobile']]==Fraction(1,12) and sp[H['minute']['mobile']]==1 and sp[H['seconds']['mobile']]==60 and sp[H['day']['mobile']]==Fraction(1,24))
# meshes
for m in mv['meshes']:
    if quick and m in old['meshes']: continue
    t=time.time()
    a,b=m['driver'],m['driven'];za,zb=m['driver_teeth'],m['driven_teeth']
    jam=0;gap=0;drv=1e9
    for i in range(8*max(za,zb)):
        ang=i*360/(8*za)
        A=kernel.apply(MOB[a],rotz(ang,AX[a])); Bm=kernel.apply(MOB[b],rotz(-ang*za/zb,AX[b]))
        jam=max(jam,kernel.ivol(A,Bm))
        if i%4==0: gap=max(gap,kernel.min_distance(A,Bm,1.0))
        if i%8==0:
            A2=kernel.apply(MOB[a],rotz(ang+90/za,AX[a])); drv=min(drv,kernel.ivol(A2,Bm))
    rep('mesh %s->%s'%(a,b),jam<=0.01 and gap<=0.1 and drv>0.01,'jam %.5f gap %.4f drive %.4f  %.0fs'%(jam,gap,drv,time.time()-t))
# nothing else collides
meshed={frozenset((m['driver'],m['driven'])) for m in mv['meshes']}
w=0
t=time.time()
for i,a in enumerate(names):
    for b in names[i+1:]:
        if frozenset((a,b)) in meshed: continue
        if (quick or fast) and a not in NEW and b not in NEW: continue
        if not kernel.bbox_overlap(MOB[a],MOB[b],25): continue
        # skip pairs that can never touch: swept radii
        sa,sb=float(sp.get(a,0)),float(sp.get(b,0))
        f=max(abs(sa),abs(sb)); seqs=[]
        if f>0: seqs+=[(360*k/144*sa/f,360*k/144*sb/f) for k in range(144)]
        rel=abs(sa-sb)
        if rel>0: seqs+=[(360*k/144*sa/rel,360*k/144*sb/rel) for k in range(144)]
        for qa,qb in seqs:  # cw positive -> negative angle
            v=kernel.ivol(kernel.apply(MOB[a],rotz(-qa,AX[a])),kernel.apply(MOB[b],rotz(-qb,AX[b])))
            if v>w: w=v; print('  collide',a,b,v)
rep('nothing else collides',w<=0.01,'%g %.0fs'%(w,time.time()-t))
# reach, size, placement
def reach(part,ax):
    v=kernel.verts(P[part]); return np.hypot(v[:,0]-ax[0],v[:,1]-ax[1]).max()
for hn,lim in (('hour',5),('minute',5),('seconds',5),('day',3)):
    r=reach(H[hn]['part'],AX[H[hn]['mobile']]); rep('reach '+hn,r>=lim,r)
d=np.hypot(*(np.array(AX[H['day']['mobile']])-np.array(AX[H['hour']['mobile']]))); rep('day placement',d>=6,d)
cc=mv['case_centre']; rmax=0; zlo=1e9;zhi=-1e9
for n in names:
    v=kernel.verts(MOB[n]); rr=np.hypot(v[:,0]-AX[n][0],v[:,1]-AX[n][1]).max()
    rmax=max(rmax,rr+np.hypot(AX[n][0]-cc[0],AX[n][1]-cc[1])); zlo=min(zlo,v[:,2].min());zhi=max(zhi,v[:,2].max())
v=kernel.verts(F); rmax=max(rmax,np.hypot(v[:,0]-cc[0],v[:,1]-cc[1]).max()); zlo=min(zlo,v[:,2].min());zhi=max(zhi,v[:,2].max())
rep('size',rmax<=20.7 and zhi-zlo<=13.4,'r %.3f h %.3f'%(rmax,zhi-zlo))
# printable
for n,p in P.items():
    if fast and (n in oldparts): continue
    if quick and n in oldparts and n not in mv['fixed']: continue
    worst=0
    for j in (0.0,0.017,0.033):
        bb=p.bounding_box(); lo,shape=kernel.grid_for(np.array(bb[:3])-0.2,np.array(bb[3:])+0.2,0.05,j)
        vox=kernel.voxelize(p,lo,shape,0.05)
        pad=np.pad(vox,1); core=kernel.edt(pad)>=1.5
        if not core.any(): worst=9e9; break
        body=(kernel.edt(~core)<=1.0+1e-9)&pad
        worst=max(worst,kernel.edt(~body)[pad].max()*0.05)
    rep('printable '+n,worst<=0.2,'%.3f'%worst)
print('ALL OK' if ok else 'SOME FAILED')
