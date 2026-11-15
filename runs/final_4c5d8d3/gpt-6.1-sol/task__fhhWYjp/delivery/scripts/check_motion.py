import sys,json,math
import numpy as np
sys.path.insert(0,'/app/tools');import kernel as K
D='/app/delivery/'
base=json.load(open(D+'movement.json'));variant=json.load(open(D+'variant_6h.json'))
cache={}
def part(n):
 if n not in cache:cache[n]=K.tris_to_manifold(K.read_stl('/app/cache/'+n+'.stl',200000,16777216))
 return cache[n]
def rot(m,a,theta):return m.translate((-a[0],-a[1],0)).rotate((0,0,theta)).translate((a[0],a[1],0))
for label,d in [('8h',base),('6h',variant)]:
 ms={k:K.union([part(n) for n in v['parts']]) for k,v in d['mobiles'].items()};ms['barrel']=part('barrel');axis={k:v['axis'] for k,v in d['mobiles'].items()};axis['barrel']=[0,0]
 for e in d['meshes']:
  dr=e['driver'];dn=e['driven'];nd=e['driver_teeth'];nr=e['driven_teeth'];mx=0
  for t in np.linspace(0,360/nd,65):
   v=K.ivol(rot(ms[dr],axis[dr],t),rot(ms[dn],axis[dn],-t*nd/nr));mx=max(mx,v)
  print(label,dr,dn,'max intersection',mx,flush=True)
# Exact maxima for axial insertions: all profiles are piecewise constant in z.
a=json.load(open(D+'assembly.json'));prior=[];faults=[]
for n in a['order']:
 p=part(n);pv=K.verts(p);pz=np.unique(np.round(pv[:,2],5))
 for q in prior:
  other=part(q);pb=p.bounding_box();qb=other.bounding_box()
  if min(pb[3],qb[3])<=max(pb[0],qb[0]) or min(pb[4],qb[4])<=max(pb[1],qb[1]):continue
  qz=np.unique(np.round(K.verts(other)[:,2],5))
  points=np.unique((qz[:,None]-pz[None,:]).flatten());points=points[(points>=0)&(points<=30)]
  for z in points:
   vol=K.ivol(p.translate((0,0,float(z))),other)
   if vol>.01:faults.append([n,q,float(z),vol]);break
 prior.append(n)
print('EXACT AXIAL INSERTION',faults,flush=True)
json.dump({'assembly_faults':faults},open('/app/assembly_check.json','w'),indent=2)
