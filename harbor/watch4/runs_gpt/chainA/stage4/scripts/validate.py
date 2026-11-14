import os,sys,json,hashlib
import numpy as np
sys.path.insert(0,'/app/tools')
import kernel as k
D=json.load(open('work/movement.json'));A=json.load(open('work/assembly.json'))
names=D['fixed']+[p for m in D['mobiles'].values() for p in m['parts']]+['barrel']
assert len(A['order'])==len(names)==len(set(A['order'])) and set(A['order'])==set(names)
for f in ['movement.json']+['parts/'+n+'.step' for n in names if n!='barrel']:
 assert open('work/'+f,'rb').read()==open('previous/'+f,'rb').read(),f
print('Frozen files byte-identical; exact part list:',len(names),flush=True)
groups={p:m for m,d in D['mobiles'].items() for p in d['parts']};groups['barrel']='barrel'
sol={}
for n in names:
 if n=='barrel':sol[n]=k.tris_to_manifold(k.read_stl('meshes/barrel.stl',200000,33554432))
 else:sol[n]=k.load_step_part('work/parts/'+n+'.step',16777216,200000,.001,.1,500,120,4096,.005)
B=np.array([s.bounding_box() for s in sol.values()]);lo=B[:,:3].min(axis=0)-5;hi=B[:,3:].max(axis=0)+5
placed=[];worst=0.;maxstep=0.;total=0
for n in A['order']:
 poses=np.array(A['paths'][n]);assert 2<=len(poses)<=1500
 assert np.isfinite(poses).all()
 assert np.max(abs(poses[-1]-np.eye(4)))<=1e-6
 for T in poses:
  assert np.max(abs(T[3]-[0,0,0,1]))<=1e-6
  assert np.max(abs(T[:3,:3].T@T[:3,:3]-np.eye(3)))<=1e-6
  assert abs(np.linalg.det(T[:3,:3])-1)<=1e-6
 first=np.array(k.apply(sol[n],poses[0]).bounding_box())
 assert np.any((first[3:]<lo)|(first[:3]>hi)),(n,first,lo,hi)
 v=k.verts(sol[n]);old=None
 for T in poses:
  vv=v@T[:3,:3].T+T[:3,3]
  if old is not None:
   step=np.linalg.norm(vv-old,axis=1).max();maxstep=max(maxstep,step);assert step<=.2+1e-9,(n,step)
  old=vv
  s=k.apply(sol[n],T)
  for q in placed:
   if n in groups and groups.get(q)==groups[n]:continue
   vol=k.ivol(s,sol[q]);worst=max(worst,vol)
   assert vol<=.01,(n,q,vol,T)
 placed.append(n);total+=len(poses)
 print('PASS',n,len(poses),'poses',flush=True)
report={'parts':len(names),'poses':total,'max_vertex_step_mm':maxstep,'max_intersection_mm3':worst,'frozen_identical':True,'rules_1_to_5':'pass'}
json.dump(report,open('work/validation.json','w'),indent=2);print(json.dumps(report),flush=True)
