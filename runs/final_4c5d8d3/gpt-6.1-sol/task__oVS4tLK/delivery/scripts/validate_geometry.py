import sys,os,json,math,itertools,concurrent.futures
import numpy as np
sys.path.insert(0,'/app/tools')
from kernel import *
ROOT='/app/delivery/'
files=sorted(os.listdir(ROOT+'parts'))
def read(n):
 m=load_step_part(ROOT+'parts/'+n,16777216,200000,.001,.1,500,120,4096,.005)
 return n[:-5],m
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: ms=dict(ex.map(read,files))
ms['barrel']=tris_to_manifold(read_stl('/app/supplied/BR-096-30.stl',2000000,100000000))
print('READ',len(ms),flush=True)
for fn in ['movement.json','variant_6h.json']:
 doc=json.load(open(ROOT+fn)); owners={'barrel':'barrel'}
 for n in doc['fixed']: owners[n]='fixed'
 for mob,v in doc['mobiles'].items():
  for n in v['parts']:owners[n]=mob
 bad=[]
 for a,b in itertools.combinations(owners,2):
  v=ivol(ms[a],ms[b])
  if v>.01:bad.append((a,b,round(v,6)))
 print(fn,'static overlaps',bad,flush=True)
 speeds={'barrel':-1/(8 if fn=='movement.json' else 6)}
 for edge in doc['meshes']:
  speeds[edge['driven']]=-speeds[edge['driver']]*edge['driver_teeth']/edge['driven_teeth']
 print('revolutions/hour',speeds,flush=True)
 # nominal barrel sweep, one tooth period; other train gears have much lower transmitted torque.
 inp=doc['mobiles']['input']['parts'][0]
 worst=0
 for j in range(97):
  ang=j/96*360/96
  a=ms['barrel'].rotate([0,0,ang])
  x,y=doc['mobiles']['input']['axis']
  b=ms[inp].translate([-x,-y,0]).rotate([0,0,-ang*8]).translate([x,y,0])
  worst=max(worst,ivol(a,b))
 print('barrel/input max sweep intersection',worst,flush=True)
# Sweep the actual assembly samples against the previously installed parts.
plan=json.load(open(ROOT+'assembly.json')); installed=[];bad=[]
for name in plan['order']:
 worst=0;hit=None
 for pose in plan['paths'][name]:
  m=apply(ms[name],np.array(pose))
  for prev in installed:
   if bbox_overlap(m,ms[prev]):
    v=ivol(m,ms[prev])
    if v>worst:worst=v;hit=prev
 if worst>.01:bad.append((name,hit,round(worst,6)))
 installed.append(name)
 print('INSERT',name,round(worst,6),hit,flush=True)
print('ASSEMBLY sample collisions',bad,flush=True)
# Literal supplier voxel test, with the specified globally fixed grid.
for name,m in ms.items():
 if name=='barrel':continue
 bb=m.bounding_box(); h=.05; shift=.0113
 lower=np.floor((np.array(bb[:3])-shift)/h)*h+shift-h/2-2*h
 size=tuple((np.ceil((np.array(bb[3:])-lower)/h)+3).astype(int))
 pieces,dev=opening_test_slabs(m,lower,size,h,1.5,1,5,slab=24)
 print('PRINT',name,pieces,dev*h,'OK' if pieces and dev*h<=.2+1e-9 else 'FAIL',flush=True)
