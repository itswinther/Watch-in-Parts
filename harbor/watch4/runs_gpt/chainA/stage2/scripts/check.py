import sys,os,json,math,itertools,time
import numpy as np
sys.path.insert(0,'tools');import kernel as k
m=json.load(open('work/movement.json')); old=json.load(open('previous/movement.json'))
os.makedirs('work/cache',exist_ok=True)
def load(n):
 path='work/parts/'+n+'.step'; cache='work/cache/'+n+'.npz'
 if os.path.exists(cache) and os.path.getmtime(cache)>os.path.getmtime(path):
  a=np.load(cache);return k.tris_to_manifold(a['t'])
 t=k.read_step(path,16777216,200000,.001,.1,500,120,4096)
 np.savez_compressed(cache,t=t); return k.tris_to_part(t,.005)
ps={n:load(n) for n in m['fixed']+sum((v['parts'] for v in m['mobiles'].values()),[])}
bs=k.tris_to_manifold(k.read_stl('meshes/barrel.stl',200000,33554432))
ms={n:k.union([ps[p] for p in v['parts']]) for n,v in m['mobiles'].items()};ms['barrel']=bs
ax={n:v['axis'] for n,v in m['mobiles'].items()};ax['barrel']=[0,0]
def rot(s,n,a):
 x,y=ax[n]; return s.translate([-x,-y,0]).rotate([0,0,a]).translate([x,y,0])
f=k.union([ps[n] for n in m['fixed']])
if '--basic' in sys.argv:
 for n,v in old['mobiles'].items():
  assert m['mobiles'][n]['axis']==v['axis']
  for p in v['parts']:assert open('work/parts/'+p+'.step','rb').read()==open('previous/parts/'+p+'.step','rb').read()
 assert m['meshes'][:len(old['meshes'])]==old['meshes']
 assert all(m['hands'][n]==v for n,v in old['hands'].items())
 print('frozen verified',flush=True)
 for (n,a),(q,b) in itertools.combinations(list(ms.items())+[('fixed',f)],2):
  v=k.ivol(a,b)
  if v>.01:print('ASSEMBLED FAIL',n,q,v,flush=True)
 for n,q in itertools.combinations(m['fixed'],2):
  v=k.ivol(ps[n],ps[q])
  if v>.01:print('FIXED FAIL',n,q,v,flush=True)
 print('assembled checked',flush=True)
 for n,a in ms.items():
  bad=[]
  for i in range(72):
   v=k.ivol(rot(a,n,i*5),f)
   if v>.01:bad.append((i,v))
  print('free',n,'PASS' if not bad else bad,flush=True)
  for dim in range(3):
   holder=k.union([f]+[b for q,b in ms.items() if q!=n and (dim<2 or math.dist(ax[q],ax[n])<=.01)])
   for sign in [-1,1]:
    delta=[0,0,0];delta[dim]=sign*.3;v=k.ivol(a.translate(delta),holder)
    if v<=.01:print('HELD FAIL',n,dim,sign,v,flush=True)
 print('held checked',flush=True)
 for n,a in ms.items():
  vv=k.verts(a);r=np.linalg.norm(vv[:,:2]-ax[n],axis=1).max()+math.dist(ax[n],m['case_centre'])
  print('size mobile',n,r,flush=True)
 print('total z',min(s.bounding_box()[2] for s in ps.values()),max(s.bounding_box()[5] for s in ps.values()),flush=True)
if '--mesh' in sys.argv:
 edges=m['meshes'] if '--all' in sys.argv else m['meshes'][-1:]
 for e in edges:
  n=e['driver'];q=e['driven'];nt=e['driver_teeth'];qt=e['driven_teeth']; a=ms[n];b=ms[q];jams=[];gaps=[];drives=[]
  start=time.time()
  for i in range(8*max(nt,qt)):
   angle=i*360/(8*nt); aa=rot(a,n,angle);bb=rot(b,q,-angle*nt/qt)
   v=k.ivol(aa,bb)
   if v>.01:jams.append((i,v))
   if i%4==0:
    dist=k.min_distance(aa,bb,.101)
    if dist>.1:gaps.append((i,dist))
   if i%8==0:
    v=k.ivol(rot(a,n,angle+90/nt),bb)
    if v<=.01:drives.append((i,v))
   if i%128==0:print('mesh progress',n,q,i,round(time.time()-start,1),flush=True)
  print('MESH',n,q,'jams',jams[:10],len(jams),'gaps',gaps[:10],len(gaps),'no drive',drives[:10],len(drives),flush=True)
if '--collisions' in sys.argv:
 from fractions import Fraction
 speed={'barrel':Fraction(-1,8)}
 while True:
  changed=False
  for e in m['meshes']:
   n,q=e['driver'],e['driven'];r=Fraction(-e['driver_teeth'],e['driven_teeth'])
   if n in speed and q not in speed:speed[q]=speed[n]*r;changed=True
   elif q in speed and n not in speed:speed[n]=speed[q]/r;changed=True
   elif n in speed and q in speed:assert speed[q]==speed[n]*r
  if not changed:break
 print('speeds revolutions/hour',speed,flush=True)
 edges={frozenset([e['driver'],e['driven']]) for e in m['meshes']}
 for n,q in itertools.combinations(ms,2):
  if frozenset([n,q]) in edges:continue
  # Only pairs affected by the added parts need new dynamic checks.
  if '--all' not in sys.argv and n not in ['day','transfer'] and q not in ['day','transfer']:continue
  # Skip pairs separated in z at every rotation.
  aa=ms[n].bounding_box();bb=ms[q].bounding_box()
  if aa[5]<=bb[2] or bb[5]<=aa[2]:continue
  bad=[]
  for kind,denom in [('absolute',max(abs(speed.get(n,0)),abs(speed.get(q,0)))),('relative',abs(speed.get(n,0)-speed.get(q,0)))]:
   if not denom:continue
   for i in range(144):
    a=rot(ms[n],n,float(speed.get(n,0)/denom)*360*i/144)
    b=rot(ms[q],q,float(speed.get(q,0)/denom)*360*i/144)
    v=k.ivol(a,b)
    if v>.01:bad.append((kind,i,v))
  print('nonmesh',n,q,'PASS' if not bad else bad[:10],flush=True)
if '--print' in sys.argv:
 names=list(ps) if '--all' in sys.argv else ['day_driver16','day_driver_extension','day_wheel96','day_shaft','day_hand','day_bridge','transfer_cock']
 for n in names:
  s=ps[n];bb=s.bounding_box()
  for jitter in [.013,.027,.041]:
   origin,shape=k.grid_for(bb[:3],bb[3:],.05,jitter)
   vox=k.voxelize(s,origin,shape,.05)
   pieces,dev=k.opening_test(vox,1.5,1.)
   print('print',n,jitter,pieces,dev*.05,'PASS' if pieces and dev*.05<=.2 else 'FAIL',flush=True)

if '--dimensions' in sys.argv:
 for n in m['fixed']:
  r=np.linalg.norm(k.verts(ps[n])[:,:2]-m['case_centre'],axis=1).max()
  assert r<=20.7,(n,r)
 print('fixed radial envelope PASS',flush=True)
 for n,v in m['hands'].items():
  r=np.linalg.norm(k.verts(ps[v['part']])[:,:2]-ax[v['mobile']],axis=1).max()
  assert r>=(3 if n=='day' else 5),(n,r)
  print('hand reach',n,r,flush=True)
 dist=math.dist(ax[m['hands']['hour']['mobile']],ax[m['hands']['day']['mobile']])
 assert dist>=6
 print('day axis separation',dist,flush=True)
