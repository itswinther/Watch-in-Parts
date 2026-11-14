from check import *
from fractions import Fraction
f=k.union([parts[p] for p in mov['fixed']])
print('ASSEMBLED',flush=True)
allb={**{p:parts[p] for p in mov['fixed']},**mobile};names=list(allb)
for i,a in enumerate(names):
 for b in names[i+1:]:
  v=k.ivol(allb[a],allb[b])
  if v>.01:print('FAIL assembled',a,b,v,flush=True)
print('HELD',flush=True)
for a,s in mobile.items():
 for j in range(3):
  for sign in [-1,1]:
   d=[0,0,0];d[j]=sign*.3
   other=k.union([f]+[b for n,b in mobile.items() if n!=a and (j!=2 or np.linalg.norm(np.array(axes[n])-axes[a])<.01)])
   v=k.ivol(s.translate(d),other)
   print('held',a,d,round(v,5),flush=True)
   if v<=.01:print('FAIL held',a,d,v,flush=True)
print('FREE TO TURN',flush=True)
for a,s in mobile.items():
 vmax=max(k.ivol(turn(s,axes[a],i*5),f) for i in range(72))
 print('free',a,vmax,flush=True)
 if vmax>.01:print('FAIL free',a,vmax,flush=True)
speed={'barrel':Fraction(1)}
for _ in range(10):
 for mesh in mov['meshes']:
  a,b,na,nb=[mesh[x] for x in ['driver','driven','driver_teeth','driven_teeth']]
  if a in speed:speed[b]=-speed[a]*Fraction(na,nb)
print('SPEED',speed,flush=True)
pairs={frozenset((e['driver'],e['driven'])) for e in mov['meshes']}
print('OTHER COLLISIONS',flush=True)
names=list(mobile)
for i,a in enumerate(names):
 for b in names[i+1:]:
  if frozenset((a,b)) in pairs:continue
  sa,sb=speed.get(a,0),speed.get(b,0);vmax=0
  for base in [max(abs(sa),abs(sb)),abs(sa-sb)]:
   if not base:continue
   for j in range(144):
    t=Fraction(j,144)/base
    v=k.ivol(turn(mobile[a],axes[a],float(sa*t)*360),turn(mobile[b],axes[b],float(sb*t)*360))
    vmax=max(vmax,v)
  print('pair',a,b,vmax,flush=True)
  if vmax>.01:print('FAIL other',a,b,vmax,flush=True)
print('SIZE',flush=True)
for a,s in mobile.items():
 vv=k.verts(s);ax=np.array(axes[a]);rad=np.linalg.norm(vv[:,:2]-ax,axis=1).max()+np.linalg.norm(ax-mov['case_centre'])
 print(a,'radial bound',rad,flush=True)
for a in mov['fixed']:
 vv=k.verts(parts[a]);rad=np.linalg.norm(vv[:,:2]-mov['case_centre'],axis=1).max()
 if rad>20.7:print('FAIL fixed size',a,rad,flush=True)
zlo=min(s.bounding_box()[2] for s in allb.values());zhi=max(s.bounding_box()[5] for s in allb.values());print('height',zhi-zlo,flush=True)
print('PRINTABLE',flush=True)
for a in mov['fixed']+sum([v['parts'] for v in mov['mobiles'].values()],[]):
 s=parts[a];bb=s.bounding_box();origin,shape=k.grid_for(bb[:3],bb[3:],.05,.017)
 grid=k.voxelize(s,origin,shape,.05);n,dev=k.opening_test(grid,1.5,1)
 print('printable',a,n,dev*.05,flush=True)
 if not n or dev*.05>.200001:print('FAIL printable',a,n,dev*.05,flush=True)
print('DONE',flush=True)
