import sys,json,itertools,numpy as np,os,pickle
sys.path.insert(0,'/app/tools')
from kernel import *
D='/app/delivery'; a=json.load(open(D+'/movement.json')); b=json.load(open(D+'/variant_6h.json'))
names=set(a['fixed']+b['fixed'])
for x in [a,b]:
 for m in x['mobiles'].values():names.update(m['parts'])
sol={}
for n in sorted(names):
 print('loading',n,flush=True)
 sol[n]=load_step_part(D+'/parts/'+n+'.step',16777216,200000,.001,.1,500,120,4096,.005)
sol['barrel']=tris_to_manifold(read_stl('/app/supplied/BR-096-30.stl',200000,16777216))
# save geometric meshes for reuse
for n,m in sol.items():
 mesh=m.to_mesh();np.savez('/app/'+n+'.npz',v=mesh.vert_properties,t=mesh.tri_verts)
for label,model in [('8h',a),('6h',b)]:
 use=model['fixed']+['barrel']+[p for m in model['mobiles'].values() for p in m['parts']]
 print('BUILD',label,flush=True)
 for n in use:
  v=verts(sol[n]);r=np.linalg.norm(v[:,:2]-np.array(model['case_centre']),axis=1).max()
  if r>12.7:print('OUTSIDE',n,r,flush=True)
 for n,k in itertools.combinations(use,2):
  vol=ivol(sol[n],sol[k])
  if vol>.010001:print('OVERLAP',n,k,vol,flush=True)
print('DONE',flush=True)
