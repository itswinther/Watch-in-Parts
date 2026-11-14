import sys,json,math,time
from pathlib import Path
sys.path.insert(0,'tools')
import kernel as k
import numpy as np
import manifold3d as m3
cache=Path('cache'); cache.mkdir(exist_ok=True)
def load(n):
 p=Path('work/parts')/(n+'.step'); c=cache/(n+'.npz')
 if c.exists() and c.stat().st_mtime>p.stat().st_mtime:
  d=np.load(c); return k.tris_to_manifold(d['tris'])
 print('load',n,flush=True)
 m=k.load_step_part(str(p),16777216,200000,.001,.1,500,120,4096,.005)
 me=m.to_mesh(); tris=np.asarray(me.vert_properties)[:,:3][np.asarray(me.tri_verts)]
 np.savez(c,tris=tris); return m
m=json.loads(Path('work/movement.json').read_text())
names=m['fixed']+sum([v['parts'] for v in m['mobiles'].values()],[])
parts={n:load(n) for n in names}
parts['barrel']=k.tris_to_manifold(k.read_stl('meshes/barrel.stl',200000,33554432))
axes={n:v['axis'] for n,v in m['mobiles'].items()};axes['barrel']=[0,0]
bodies={n:k.union([parts[p] for p in v['parts']]) for n,v in m['mobiles'].items()};bodies['barrel']=parts['barrel']
fixed=k.union([parts[n] for n in m['fixed']])
def rot(b,n,a):
 x,y=axes[n]; r=math.radians(a); c=math.cos(r);s=math.sin(r)
 return b.transform([[c,-s,0,x-c*x+s*y],[s,c,0,y-s*x-c*y],[0,0,1,0]])
if 'assembled' in sys.argv or 'all' in sys.argv or len(sys.argv)==1:
 print('ASSEMBLED',flush=True)
 for i,n in enumerate(m['fixed']):
  for j in m['fixed'][i+1:]:
   v=k.ivol(parts[n],parts[j]);
   if v>.01:print('FIXED COLLISION',n,j,v,flush=True)
 for n,b in bodies.items():
  v=k.ivol(b,fixed)
  if v>.01:print('FIXED BODY COLLISION',n,v,flush=True)
 for i,n in enumerate(bodies):
  for j in list(bodies)[i+1:]:
   v=k.ivol(bodies[n],bodies[j])
   if v>.01:print('BODY COLLISION',n,j,v,flush=True)
 print('HELD',flush=True)
 for n,b in bodies.items():
  for dim in range(3):
   other=k.union([fixed]+[v for j,v in bodies.items() if j!=n and (dim!=2 or np.linalg.norm(np.array(axes[n])-axes[j])<=.01)])
   for sign in [-1,1]:
    off=[0,0,0];off[dim]=sign*.3;v=k.ivol(b.translate(off),other)
    if v<=.01:print('NOT HELD',n,off,v,flush=True)
 print('FREE',flush=True)
 for n in bodies if 'all' in sys.argv else ['transfer','reduction_input','reduction_idler']:
  bad=[]
  for a in range(0,360,5):
   v=k.ivol(rot(bodies[n],n,a),fixed)
   if v>.01:bad.append((a,v))
  print('FREE',n,bad[:8],flush=True)
if 'mesh' in sys.argv or 'all' in sys.argv:
 for e in m['meshes'] if 'all' in sys.argv else m['meshes'][:3]:
  a=e['driver']; b=e['driven']; na=e['driver_teeth']; nb=e['driven_teeth'];bad=[];jams=0;gaps=0;nodrive=0;mx=0;ming=10;mind=100
  print('MESH',a,b,flush=True)
  for i in range(8*max(na,nb)):
   angle=i*360/(8*na);A=rot(bodies[a],a,angle); B=rot(bodies[b],b,-angle*na/nb)
   v=k.ivol(A,B);mx=max(mx,v)
   if v>.01:jams+=1;bad.append(('jam',i,v))
   if i%4==0:
    g=k.min_distance(A,B,.101);ming=min(ming,g)
    if g>.1:gaps+=1;bad.append(('gap',i,g))
   if i%8==0:
    v=k.ivol(rot(bodies[a],a,angle+90/na),B);mind=min(mind,v)
    if v<=.01:nodrive+=1;bad.append(('drive',i,v))
  print('RESULT',a,b,'jams/gaps/nodrive',jams,gaps,nodrive,'maxjam',mx,'mindrive',mind,bad[:10],flush=True)

if 'all' in sys.argv:
 from fractions import Fraction
 speeds={'barrel':Fraction(-1,6)}
 for z in range(20):
  for e in m['meshes']:
   a,b=e['driver'],e['driven'];r=Fraction(-e['driver_teeth'],e['driven_teeth'])
   if a in speeds:
    v=speeds[a]*r
    if b in speeds:assert speeds[b]==v
    speeds[b]=v
 print('SPEEDS turns/hour',speeds,flush=True)
 assert all(speeds[m['hands'][h]['mobile']]==v for h,v in {'hour':Fraction(-1,12),'minute':Fraction(-1),'seconds':Fraction(-60),'day':Fraction(-1,24)}.items())
 pairs={frozenset([e['driver'],e['driven']]) for e in m['meshes']}
 for i,a in enumerate(bodies):
  for b in list(bodies)[i+1:]:
   if frozenset([a,b]) in pairs:continue
   sa,sb=float(speeds[a]),float(speeds[b]);bad=[]
   for rate in [max(abs(sa),abs(sb)),abs(sa-sb)]:
    if rate==0:continue
    for j in range(144):
     t=j/(144*rate)
     v=k.ivol(rot(bodies[a],a,360*sa*t),rot(bodies[b],b,360*sb*t))
     if v>.01:bad.append((j,v))
   print('NONMESH',a,b,bad[:5],flush=True)
 ctr=np.array(m['case_centre']);lo=100;hi=-100
 for n,b in bodies.items():
  v=k.verts(b); r=np.linalg.norm(np.array(axes[n])-ctr)+np.linalg.norm(v[:,:2]-axes[n],axis=1).max()
  lo=min(lo,v[:,2].min());hi=max(hi,v[:,2].max())
  print('SWEPT SIZE',n,r,flush=True)
 for n in m['fixed']:
  v=k.verts(parts[n]); r=np.linalg.norm(v[:,:2]-ctr,axis=1).max();lo=min(lo,v[:,2].min());hi=max(hi,v[:,2].max());print('FIXED SIZE',n,r,flush=True)
 print('HEIGHT',hi-lo,flush=True)
 old=json.loads(Path('previous/movement.json').read_text());oldnames=old['fixed']+sum([v['parts'] for v in old['mobiles'].values()],[])
 kept=[n for n in oldnames if (Path('previous/parts')/(n+'.step')).read_bytes()==(Path('work/parts')/(n+'.step')).read_bytes()]
 print('BYTE IDENTICAL',len(kept),'of',len(oldnames),kept,flush=True)
