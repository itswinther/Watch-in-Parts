import json,sys,math,pickle,os
from pathlib import Path
import numpy as np
sys.path.insert(0,'/app/tools');import kernel as K
from concurrent.futures import ThreadPoolExecutor
P=Path('/app/delivery'); doc=json.loads((P/'movement.json').read_text());variant=json.loads((P/'variant_6h.json').read_text())
names=set(doc['fixed'])
for d in [doc,variant]:
 for v in d['mobiles'].values():names.update(v['parts'])
def load(n):
 m=K.load_part('/app/cache/'+n+'.stl',200000,16777216,.005) if os.path.exists('/app/cache/'+n+'.stl') else K.load_step_part(str(P/'parts'/f'{n}.step'),16777216,200000,.001,.1,500,120,4096,.005)
 return n,m
with ThreadPoolExecutor(max_workers=3) as pool:parts=dict(pool.map(load,sorted(names)))
parts['barrel']=K.tris_to_manifold(K.read_stl('/app/supplied/BR-096-30.stl',200000,16777216))
import manifold3d as m3
os.makedirs('/app/cache',exist_ok=True)
for n,m in parts.items():K.write_stl('/app/cache/'+n+'.stl',m)
print('Loaded',len(parts),'solids',flush=True)
issues=[]
for label,d,hours in [('8h',doc,8),('6h',variant,6)]:
 owner={n:'fixed' for n in d['fixed']};owner['barrel']='barrel'
 for k,v in d['mobiles'].items():
  for n in v['parts']:owner[n]=k
 ns=list(owner)
 for i,n in enumerate(ns):
  for q in ns[i+1:]:
   if owner[n]==owner[q]:continue
   if K.bbox_overlap(parts[n],parts[q]):
    v=K.ivol(parts[n],parts[q])
    if v>.01:issues.append((label,'static_collision',n,q,v))
 speed={'barrel':1/hours}
 for it in range(20):
  for e in d['meshes']:
   if e['driver'] in speed:speed[e['driven']]=-speed[e['driver']]*e['driver_teeth']/e['driven_teeth']
 print(label,'revolutions/hour', {k:speed[k] for k in d['hands']},flush=True)
 # Containment of the full swept envelopes of all mobiles and hands.
 for n,k in owner.items():
  vs=K.verts(parts[n]);xy=vs[:,:2]-np.array(d['case_centre'])
  if k not in ['fixed','barrel']:
   a=np.array(d['mobiles'][k]['axis']);rr=np.linalg.norm(vs[:,:2]-a,axis=1).max()+np.linalg.norm(a-d['case_centre'])
  else:rr=np.linalg.norm(xy,axis=1).max()
  if rr>12.7001:issues.append((label,'case_radius',n,float(rr)))
print('STATIC',issues,flush=True)
# Translational insertion. Paths are piecewise linear, checked at 0.05 mm intervals.
a=json.loads((P/'assembly.json').read_text());placed=[];assembly_issues=[]
for n in a['order']:
 moving=parts[n];b=np.array(moving.bounding_box());
 for q in placed:
  other=parts[q];ob=np.array(other.bounding_box())
  if min(b[3],ob[3])<=max(b[0],ob[0]) or min(b[4],ob[4])<=max(b[1],ob[1]):continue
  low=max(0,ob[2]-b[5]);high=min(30,ob[5]-b[2])
  if high<low:continue
  for z in np.arange(low,high+.025,.05):
   v=K.ivol(moving.translate((0,0,float(z))),other)
   if v>.01:
    assembly_issues.append((n,q,float(z),v));break
 placed.append(n)
print('ASSEMBLY',assembly_issues,flush=True)
Path('/app/verification.json').write_text(json.dumps({'static':issues,'assembly':assembly_issues},indent=2))
