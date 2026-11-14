import sys,json,time,math
sys.path.insert(0,'/app/tools'); import kernel as k
import numpy as np, manifold3d as m
from pathlib import Path
mov=json.loads(Path('work/movement.json').read_text());parts={}
cache=Path('work/cache');cache.mkdir(exist_ok=True)
for name in mov['fixed']+sum([v['parts'] for v in mov['mobiles'].values()],[]):
 p=Path('work/parts')/(name+'.step'); cp=cache/(name+'.npz')
 if cp.exists() and cp.stat().st_mtime>p.stat().st_mtime:
  d=np.load(cp);s=m.Manifold(m.Mesh(d['v'],d['t']))
 else:
  s=k.load_step_part(str(p),16777216,200000,.001,.1,500,120,4096,.005)
  me=s.to_mesh();np.savez(cp,v=me.vert_properties,t=me.tri_verts)
 parts[name]=s
 print('loaded',name,flush=True)
parts['barrel']=k.tris_to_manifold(k.read_stl('meshes/barrel.stl',200000,33554432))
mobile={'barrel':parts['barrel']};axes={'barrel':[0,0]}
for name,v in mov['mobiles'].items(): mobile[name]=k.union([parts[p] for p in v['parts']]);axes[name]=v['axis']
def turn(s,axis,deg):return s.translate([-axis[0],-axis[1],0]).rotate([0,0,deg]).translate([axis[0],axis[1],0])
if __name__=='__main__':
 allb={**{p:parts[p] for p in mov['fixed']},**mobile}
 names=list(allb)
 print('ASSEMBLED',flush=True)
 for i,a in enumerate(names):
  for b in names[i+1:]:
   v=k.ivol(allb[a],allb[b])
   if v>.01:print('COLLISION',a,b,v,flush=True)
 f=k.union([parts[p] for p in mov['fixed']])
 print('HELD',flush=True)
 for a,s in mobile.items():
  for j in range(3):
   for sign in [-1,1]:
    d=[0,0,0];d[j]=sign*.3
    other=k.union([f]+[b for n,b in mobile.items() if n!=a and (j!=2 or np.linalg.norm(np.array(axes[n])-axes[a])<.01)])
    v=k.ivol(s.translate(d),other)
    if v<=.01:print('NOTHELD',a,d,v,flush=True)
 print('GEARS',flush=True)
 for mesh in mov['meshes']:
  a,b=mesh['driver'],mesh['driven'];na,nb=mesh['driver_teeth'],mesh['driven_teeth'];n=8*max(na,nb)
  jam=0;drive=1e9;gap=0
  for i in range(n):
   deg=i*360/(8*na);x=turn(mobile[a],axes[a],deg);y=turn(mobile[b],axes[b],-deg*na/nb)
   v=k.ivol(x,y);jam=max(jam,v)
   if i%4==0:gap=max(gap,k.min_distance(x,y,.11))
   if i%8==0:drive=min(drive,k.ivol(turn(mobile[a],axes[a],deg+90/na),y))
   if i%128==0:print(a,b,i,'jam',jam,'drive',drive,'gap',gap,flush=True)
  print('RESULT',a,b,jam,drive,gap,flush=True)
