import sys,os,json,math,itertools,concurrent.futures
import numpy as np
sys.path.insert(0,'/app/tools')
from kernel import *
ROOT='/app/delivery/'
def read(n):return n[:-5],load_step_part(ROOT+'parts/'+n,16777216,200000,.001,.1,500,120,4096,.005)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: ms=dict(ex.map(read,sorted(os.listdir(ROOT+'parts'))))
ms['barrel']=tris_to_manifold(read_stl('/app/supplied/BR-096-30.stl',2000000,100000000))
print('READ',flush=True)
for fn in ['movement.json','variant_6h.json']:
 doc=json.load(open(ROOT+fn)); axes={'barrel':[0,0]}; mobiles={'barrel':ms['barrel']}
 for k,v in doc['mobiles'].items():axes[k]=v['axis'];mobiles[k]=union([ms[n] for n in v['parts']])
 for edge in doc['meshes']:
  a,b=edge['driver'],edge['driven'];n1,n2=edge['driver_teeth'],edge['driven_teeth'];worst=0
  x1,y1=axes[a];x2,y2=axes[b]
  for j in range(129):
   angle=360/n1*j/128
   ma=mobiles[a].translate([-x1,-y1,0]).rotate([0,0,angle]).translate([x1,y1,0])
   mb=mobiles[b].translate([-x2,-y2,0]).rotate([0,0,-angle*n1/n2]).translate([x2,y2,0])
   worst=max(worst,ivol(ma,mb))
  print('MESH',fn,a,b,worst,flush=True)
 # Every mobile against the stationary frame over a complete turn.
 fixed=union([ms[n] for n in doc['fixed']])
 for mob,m in mobiles.items():
  x,y=axes[mob];worst=0
  for j in range(72):
   ma=m.translate([-x,-y,0]).rotate([0,0,5*j]).translate([x,y,0]);worst=max(worst,ivol(ma,fixed))
  print('FRAME ROTATION',fn,mob,worst,flush=True)
# Every model is made solely of vertical extrusions. Its union of upward-extruded constant
# cross-section intervals is its entire continuous vertical insertion sweep, without pose sampling.
plan=json.load(open(ROOT+'assembly.json')); installed=[]
for name in plan['order']:
 m=ms[name];levels=np.unique(np.round(verts(m)[:,2],6));slabs=[]
 for z0,z1 in zip(levels[:-1],levels[1:]):
  if z1-z0<1e-6:continue
  cross=m.slice((z0+z1)/2)
  if cross.area()>1e-10:slabs.append(cross.extrude(float(z1-z0+30)).translate([0,0,float(z0)]))
 swept=union(slabs);worst=0;hit=None
 for prev in installed:
  v=ivol(swept,ms[prev])
  if v>worst:worst=v;hit=prev
 print('CONTINUOUS INSERT',name,worst,hit,flush=True)
 installed.append(name)
# Geometry dimensions in the case, including whole hand sweeps.
for fn in ['movement.json','variant_6h.json']:
 doc=json.load(open(ROOT+fn));x,y=doc['case_centre'];names=doc['fixed']+[n for v in doc['mobiles'].values() for n in v['parts']]+['barrel']
 lo=min(ms[n].bounding_box()[2] for n in names);hi=max(ms[n].bounding_box()[5] for n in names)
 radius=max(np.hypot(verts(ms[n])[:,0]-x,verts(ms[n])[:,1]-y).max() for n in names)
 for k,v in doc['hands'].items():
  p=doc['mobiles'][v['mobile']]['axis'];vs=verts(ms[v['part']]);r=np.hypot(vs[:,0]-p[0],vs[:,1]-p[1]).max()
  radius=max(radius,math.dist([x,y],p)+r)
  print('HAND',fn,k,'max reach',r,'axis',p,flush=True)
 print('CASE',fn,'height',hi-lo,'max radius incl swept hands',radius,flush=True)
