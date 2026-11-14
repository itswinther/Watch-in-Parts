import sys,json,pickle,time
from pathlib import Path
sys.path.insert(0,'/app/tools')
import kernel as k
import numpy as np
ROOT=Path('/app')
m=json.load(open(ROOT/'work/movement.json'))
group={p:n for n,v in m['mobiles'].items() for p in v['parts']}
group.update({p:p for p in m['fixed']});group['barrel']='barrel'
names=list(group)
cache=ROOT/'solids.pkl'
if cache.exists():
 data=pickle.load(open(cache,'rb')); solids={n:k.tris_to_manifold(t) for n,t in data.items()}
else:
 solids={}
 for n in names:
  print('load',n,flush=True)
  solids[n]=k.tris_to_manifold(k.read_stl(ROOT/'meshes/barrel.stl',200000,33554432)) if n=='barrel' else k.load_step_part(ROOT/f'work/parts/{n}.step',16777216,200000,.001,.1,500,120,4096,.005)
 pickle.dump({n:np.asarray(s.to_mesh().vert_properties)[:,:3][np.asarray(s.to_mesh().tri_verts)] for n,s in solids.items()},open(cache,'wb'))
for n,s in solids.items(): print(n, np.round(s.bounding_box(),3).tolist(),flush=True)
lo=np.min([s.bounding_box()[:3] for s in solids.values()],axis=0)-5
hi=np.max([s.bounding_box()[3:] for s in solids.values()],axis=0)+5
remaining=set(names);removed=[];paths={}
directions=[np.array(d,float) for d in [(0,0,1),(0,0,-1),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]]
def attempt(n,d):
 s=solids[n];bb=np.array(s.bounding_box());axis=np.argmax(abs(d));sign=d[axis]
 dist=(hi[axis]-bb[axis]+.05) if sign>0 else (bb[axis+3]-lo[axis]+.05)
 steps=int(np.ceil(dist/.19)); offsets=[d*(dist*i/steps) for i in range(steps+1)]
 others=[p for p in remaining if p!=n and group[p]!=group[n]]
 for off in offsets:
  moved=s.translate(off.tolist())
  for p in others:
   if k.ivol(moved,solids[p])>.01000001:return None
 return offsets
while remaining:
 progress=False
 for n in names:
  if n not in remaining:continue
  for d in directions:
   offsets=attempt(n,d)
   if offsets is not None:
    print('REMOVE',n,'direction',d.tolist(),'poses',len(offsets),flush=True)
    remaining.remove(n);removed.append(n)
    paths[n]=[k.translation(off).tolist() for off in offsets[::-1]]
    progress=True;break
 if not progress:
  print('STUCK',list(remaining),flush=True);break
# Include all, with fallback straight up for unresolved parts.
for n in remaining:
 bb=solids[n].bounding_box();dist=hi[2]-bb[2]+.05;steps=int(np.ceil(dist/.19))
 paths[n]=[k.translation([0,0,dist*i/steps]).tolist() for i in range(steps,-1,-1)]
order=list(remaining)+removed[::-1]
json.dump({'order':order,'paths':paths},open(ROOT/'work/assembly.json','w'))
print('ASSEMBLY',len(removed),'/',len(names),flush=True)
