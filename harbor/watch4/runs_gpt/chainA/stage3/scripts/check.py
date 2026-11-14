import sys,os,json,time,math,argparse
sys.path.insert(0,'/app/tools')
import kernel as k
import numpy as np,manifold3d as m3
from fractions import Fraction
os.makedirs('checks/cache',exist_ok=True)
m=json.load(open('work/movement.json'))
def load(n):
 path='meshes/barrel.stl' if n=='barrel' else 'work/parts/'+n+'.step'
 import hashlib
 key=__import__('hashlib').sha256(open(path,'rb').read()).hexdigest();cache='checks/cache/'+key+'.stl'
 if os.path.exists(cache):return k.tris_to_manifold(k.read_stl(cache,200000,33554432))
 s=k.tris_to_manifold(k.read_stl(path,200000,33554432)) if n=='barrel' else k.load_step_part(path,16777216,200000,.001,.1,500,120,4096,.005)
 k.write_stl(cache,s);return s
names=m['fixed']+sum([v['parts'] for v in m['mobiles'].values()],[])+['barrel']
parts={}
for n in names:
 parts[n]=load(n)
 print('loaded',n,flush=True)
axes={'barrel':(0,0),**{n:v['axis'] for n,v in m['mobiles'].items()}}
mob={n:k.union([parts[p] for p in v['parts']]) for n,v in m['mobiles'].items()};mob['barrel']=parts['barrel']
fixed=k.union([parts[n] for n in m['fixed']])
def rot(s,n,a):
 x,y=axes[n];return s.translate([-x,-y,0]).rotate([0,0,a]).translate([x,y,0])
def assembled():
 worst=[]
 for i,a in enumerate(names):
  for b in names[:i]:
   if a not in m['fixed'] and b not in m['fixed']:continue
   v=k.ivol(parts[a],parts[b])
   if v>.01:worst.append((a,b,v))
 for i,(a,sa) in enumerate(mob.items()):
  for b,sb in list(mob.items())[:i]:
   v=k.ivol(sa,sb)
   if v>.01:worst.append((a,b,v))
 print('ASSEMBLED',worst,flush=True)
def meshes():
 for e in m['meshes']:
  a,b=e['driver'],e['driven'];na,nb=e['driver_teeth'],e['driven_teeth'];N=8*max(na,nb)
  bad=[];maxv=0;mingrip=1e9;maxgap=0
  for i in range(N):
   angle=i*360/(8*na);sa=rot(mob[a],a,angle);sb=rot(mob[b],b,-angle*na/nb)
   v=k.ivol(sa,sb);maxv=max(maxv,v)
   if v>.01:bad.append(('jam',i,v))
   if i%4==0:
    gap=k.min_distance(sa,sb,.101);maxgap=max(gap,maxgap)
    if gap>.10001:bad.append(('gap',i,gap))
   if i%8==0:
    v=k.ivol(rot(mob[a],a,angle+90/na),sb);mingrip=min(v,mingrip)
    if v<=.01:bad.append(('drive',i,v))
  print('MESH',a,b,'maxjam',maxv,'mingrip',mingrip,'maxgap',maxgap,'bad',len(bad),bad[:12],flush=True)
def freeheld():
 for n,s in mob.items():
  worst=max(k.ivol(rot(s,n,i*5),fixed) for i in range(72))
  vals=[]
  for d in [(0.3,0,0),(-.3,0,0),(0,.3,0),(0,-.3,0),(0,0,.3),(0,0,-.3)]:
   other=[fixed]+[v for a,v in mob.items() if a!=n and (d[2]==0 or math.dist(axes[n],axes[a])<=.01)]
   vals.append(k.ivol(s.translate(d),k.union(other)))
  print('FREEHELD',n,worst,vals,flush=True)
mode=sys.argv[1] if len(sys.argv)>1 else 'assembly'
if mode=='assembly':assembled()
if mode=='meshes':meshes()
if mode=='freeheld':freeheld()

def speeds():
 v={'barrel':Fraction(-1,6)}
 for _ in range(20):
  for e in m['meshes']:
   a,b=e['driver'],e['driven'];r=Fraction(-e['driver_teeth'],e['driven_teeth'])
   if a in v:
    w=v[a]*r
    if b in v:assert v[b]==w
    v[b]=w
   elif b in v:v[a]=v[b]/r
 return v
if mode=='nonmesh':
 v=speeds();declared={frozenset((e['driver'],e['driven'])) for e in m['meshes']}
 for i,(a,sa) in enumerate(mob.items()):
  for b,sb in list(mob.items())[:i]:
   if frozenset((a,b)) in declared:continue
   va=float(v.get(a,0));vb=float(v.get(b,0));worst=0;bad=0
   for rate in [max(abs(va),abs(vb)),abs(va-vb)]:
    if rate==0:continue
    for j in range(144):
     f=j*360/144/rate
     vol=k.ivol(rot(sa,a,f*va),rot(sb,b,f*vb));worst=max(worst,vol);bad+=vol>.01
   print('NONMESH',a,b,worst,bad,flush=True)
if mode=='metrics':
 print('SPEEDS',speeds(),flush=True)
 centre=np.array(m['case_centre'])
 for n,s in mob.items():
  r=np.linalg.norm(k.verts(s)[:,:2]-axes[n],axis=1).max();env=r+np.linalg.norm(np.array(axes[n])-centre)
  print('ENVELOPE',n,env,flush=True)
 print('FIXED_ENVELOPE',np.linalg.norm(k.verts(fixed)[:,:2]-centre,axis=1).max(),flush=True)
 print('HEIGHT',max(s.bounding_box()[5] for s in parts.values())-min(s.bounding_box()[2] for s in parts.values()),flush=True)
 for n,s in parts.items():
  if n=='barrel':continue
  bb=s.bounding_box();lo,shape=k.grid_for(bb[:3],bb[3:],.05,np.array([.017,.023,.031]));solid=k.voxelize(s,lo,shape,.05)
  ncore,dev=k.opening_test(solid,1.5,1.0)
  print('PRINT',n,ncore,dev*.05,flush=True)
