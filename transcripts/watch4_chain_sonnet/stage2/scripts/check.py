import sys, json, math, itertools
sys.path.insert(0,'tools')
import numpy as np, kernel, manifold3d as m3
mv=json.load(open('work/movement.json'))
L=lambda n: kernel.load_step_part(f'work/parts/{n}.step',16777216,200000,0.001,0.1,500,120,4096,0.005)
cache={}
def part(n):
    if n not in cache: cache[n]=L(n)
    return cache[n]
bar=kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl',200000,33554432))
def uni(ms):
    r=ms[0]
    for m in ms[1:]: r=r+m
    return r
fixed=uni([part(n) for n in mv['fixed']])
mob={'barrel':(bar,(0,0))}
for k,v in mv['mobiles'].items(): mob[k]=(uni([part(n) for n in v['parts']]),tuple(v['axis']))
def rot(m,ax,deg):
    a=math.radians(deg); c,s=math.cos(a),math.sin(a); x,y=ax
    T=np.array([[c,-s,0,x-c*x+s*y],[s,c,0,y-s*x-c*y],[0,0,1,0]])
    return m.transform(T)
def iv(a,b): return kernel.ivol(a,b)
# fixed overlap
fl=[part(n) for n in mv['fixed']]
for a,b in itertools.combinations(range(len(fl)),2):
    v=iv(fl[a],fl[b]); 
    if v>0.001: print('FIXED OVERLAP',mv['fixed'][a],mv['fixed'][b],v)
for k,(m,ax) in mob.items():
    print(k,'assembled vs fixed',round(iv(m,fixed),5))
for (a,(ma,_)),(b,(mb,_)) in itertools.combinations(mob.items(),2):
    v=iv(ma,mb)
    if v>0.001: print('MOB OVERLAP',a,b,v)
which=sys.argv[1:] or list(mob)
for k in which:
    m,ax=mob[k]; worst=max(iv(rot(m,ax,5*i),fixed) for i in range(72)); print('free',k,worst)
# held
for k in which:
    m,ax=mob[k]
    res=[]
    for d in [(.3,0,0),(-.3,0,0),(0,.3,0),(0,-.3,0),(0,0,.3),(0,0,-.3)]:
        mm=m.translate(d)
        if d[2]==0: others=[fixed]+[o for n,(o,_) in mob.items() if n!=k]
        else: others=[fixed]+[o for n,(o,a2) in mob.items() if n!=k and math.hypot(a2[0]-ax[0],a2[1]-ax[1])<0.01]
        res.append(round(max(iv(mm,o) for o in others),3))
    print('held',k,res)
# meshes
for ms in mv['meshes']:
    d,dt,v,vt=ms['driver'],ms['driver_teeth'],ms['driven'],ms['driven_teeth']
    if not(set([d,v])&set(sys.argv[1:])) and sys.argv[1:] and not (d in which or v in which): continue
    (md,ad),(mv_,av)=mob[d],mob[v]
    bad=0;mind=0
    for i in range(8*max(dt,vt)):
        a=i*360/(8*dt)
        A=rot(md,ad,a); B=rot(mv_,av,-a*dt/vt)
        o=iv(A,B)
        if o>0.01: bad+=1
        if i%4==0:
            pass
        if i%8==0:
            A2=rot(md,ad,a+90/dt)
            if iv(A2,B)<=0.01: bad+=1000
    print('mesh',d,v,'bad',bad)
