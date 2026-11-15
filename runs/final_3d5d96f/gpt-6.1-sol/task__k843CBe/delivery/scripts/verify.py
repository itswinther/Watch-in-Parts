import sys,json,math,itertools,pickle
import numpy as np
sys.path.insert(0,'/app/tools'); import kernel as k
from pathlib import Path
root=Path('/app/delivery')
mov=json.loads((root/'movement.json').read_text()); var=json.loads((root/'variant_6h.json').read_text())
ns=set(mov['fixed']+sum([v['parts'] for v in mov['mobiles'].values()],[])+sum([v['parts'] for v in var['mobiles'].values()],[]))
parts={}
for name in sorted(ns):
 man=k.load_step_part(str(root/'parts'/f'{name}.step'),16777216,200000,.001,.1,500,120,4096,.005)
 parts[name]=man;print('loaded',name,flush=True)
parts['barrel']=k.tris_to_manifold(k.read_stl('/app/supplied/BR-096-30.stl',200000,16777216))
# Cache raw mesh, for repeat testing without rereading STEP.
for n,m in parts.items():k.write_stl('/app/'+n+'.stl',m)
for label,doc in [('8h',mov),('6h',var)]:
 owners={p:'fixed' for p in doc['fixed']};owners['barrel']='barrel'
 for n,v in doc['mobiles'].items():
  for p in v['parts']:owners[p]=n
 print('STATIC',label,flush=True)
 for a,b in itertools.combinations(owners,2):
  if not k.bbox_overlap(parts[a],parts[b]):continue
  vol=k.ivol(parts[a],parts[b])
  if vol>.01:print('OVERLAP',a,b,vol,flush=True)
 maxr=0
 for n in owners:
  vs=k.verts(parts[n]);maxr=max(maxr,np.linalg.norm(vs[:,:2]-np.asarray(doc['case_centre']),axis=1).max())
 print('case max radius',maxr,flush=True)
# Full discrete assembly at specified increments, with midpoint checks.
order=json.loads((root/'assembly.json').read_text())['order']; assembled=[]
for name in order:
 hits={}
 for z in np.linspace(25,0,261):
  cur=parts[name].translate([0,0,float(z)])
  for other in assembled:
   if other in hits or not k.bbox_overlap(cur,parts[other]):continue
   vol=k.ivol(cur,parts[other])
   if vol>.01:hits[other]=(float(z),vol)
 print('ASSEMBLY',name,hits,flush=True);assembled.append(name)
