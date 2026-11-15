import sys,json,os,itertools,math
import numpy as np
import manifold3d as md
from scipy import ndimage as ndi
sys.path.insert(0,'/app/tools');from kernel import *
D='/app/delivery';a=json.load(open(D+'/movement.json'));b=json.load(open(D+'/variant_6h.json'))
names=set(a['fixed']+b['fixed'])
for model in [a,b]:
 for m in model['mobiles'].values():names.update(m['parts'])
sol={}
for n in names|{'barrel'}:
 z=np.load('/app/'+n+'.npz');sol[n]=md.Manifold(md.Mesh(vert_properties=z['v'],tri_verts=z['t']))
# Exact process-sheet voxel centres, with a two-voxel empty margin.
for n in sorted(names):
 m=sol[n];bb=np.array(m.bounding_box());h=.05
 ilo=np.floor((bb[:3]-.0113)/h).astype(int)-3;ihi=np.ceil((bb[3:]-.0113)/h).astype(int)+3
 origin=ilo*h+.0113-h/2;shape=tuple(ihi-ilo+1)
 mask=voxelize(m,origin,shape,h)
 dist=ndi.distance_transform_edt(mask)
 survive=mask&(dist>=1.5-1e-9)
 printable=mask & (ndi.distance_transform_edt(~survive)<=1+1e-9)
 reach=ndi.distance_transform_edt(~printable)
 maximum=float(reach[mask].max())*h
 print('PRINT',n,maximum,'PASS' if survive.any() and maximum<=.2+1e-9 else 'FAIL',flush=True)
 del mask,dist,survive,printable,reach
print('PRINTING DONE',flush=True)
# Kinematic tooth engagement test: rotate each meshing pair over two driver tooth pitches.
for tag,model in [('8h',a),('6h',b)]:
 mobiles={k:md.Manifold.batch_boolean([sol[p] for p in v['parts']],md.OpType.Add) for k,v in model['mobiles'].items()}
 mobiles['barrel']=sol['barrel'];axes={k:v['axis'] for k,v in model['mobiles'].items()};axes['barrel']=[0,0]
 def rotated(m,xy,deg):return m.translate([-xy[0],-xy[1],0]).rotate([0,0,deg]).translate([xy[0],xy[1],0])
 for mesh in model['meshes']:
  u,v=mesh['driver'],mesh['driven'];nu,nv=mesh['driver_teeth'],mesh['driven_teeth'];maximum=0
  for deg in np.linspace(0,720/nu,33):
   vol=ivol(rotated(mobiles[u],axes[u],deg),rotated(mobiles[v],axes[v],-deg*nu/nv));maximum=max(maximum,vol)
  print('MESH',tag,u,v,maximum,flush=True)
print('DYNAMICS DONE',flush=True)
# Straight insertion paths, all 0.1mm increments. Test against installed parts.
assy=json.load(open(D+'/assembly.json'));installed=[]
for name in assy['order']:
 worst=0;other=None;at=None
 for pose in assy['paths'][name]:
  moved=apply(sol[name],pose)
  for n in installed:
   vol=ivol(moved,sol[n])
   if vol>worst:worst=vol;other=n;at=pose[2][3]
 print('INSERT',name,'max',worst,'against',other,'at',at,flush=True)
 installed.append(name)
print('ASSEMBLY DONE',flush=True)
