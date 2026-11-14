import sys,json,os,time
sys.path.insert(0,'/app/tools')
import kernel as k
import numpy as np
D=json.load(open('work/movement.json'))
names=D['fixed']+[p for m in D['mobiles'].values() for p in m['parts']]+['barrel']
groups={p:m for m,d in D['mobiles'].items() for p in d['parts']};groups['barrel']='barrel'
os.makedirs('work/cache',exist_ok=True)
sol={}
for n in names:
 f='work/cache/'+n+'.stl'
 if os.path.exists(f): s=k.tris_to_manifold(k.read_stl(f,200000,33554432))
 elif n=='barrel': s=k.tris_to_manifold(k.read_stl('meshes/barrel.stl',200000,33554432));k.write_stl(f,s)
 else:
  s=k.load_step_part('work/parts/'+n+'.step',16777216,200000,.001,.1,500,120,4096,.005);k.write_stl(f,s)
 sol[n]=s
 print('loaded',n,tuple(round(x,3) for x in s.bounding_box()),flush=True)
B=np.array([s.bounding_box() for s in sol.values()]);lo=B[:,:3].min(axis=0)-5;hi=B[:,3:].max(axis=0)+5
json.dump({'lo':lo.tolist(),'hi':hi.tolist()},open('work/bounds.json','w'))
remaining=list(names);removed=[];paths={}
def ray(n,d):
 b=np.array(sol[n].bounding_box()); d=np.array(d,float)
 # earliest strict separation from enlarged box on any moving coordinate
 dist=min([(hi[i]-b[i]+.1)/d[i] if d[i]>0 else (lo[i]-b[i+3]-.1)/d[i] for i in range(3) if abs(d[i])>1e-9])
 count=int(np.ceil(dist/.19)); ts=np.linspace(0,dist,count+1)
 obs=[q for q in remaining if q!=n and not (n in groups and groups.get(q)==groups[n])]
 for t in ts:
  s=sol[n].translate((d*t).tolist())
  for q in obs:
   if k.ivol(s,sol[q])>.01000001:return None
 return [k.translation(d*t).tolist() for t in ts[::-1]]
while remaining:
 found=False
 # prefer small high parts; axial removal is cheapest
 for n in sorted(remaining,key=lambda n: -sol[n].bounding_box()[5]):
  for d in [(0,0,1),(0,0,-1),(1,0,0),(-1,0,0),(0,1,0),(0,-1,0)]:
   p=ray(n,d)
   if p is not None:
    paths[n]=p;removed.append(n);remaining.remove(n);found=True
    print('REMOVED',n,d,'left',len(remaining),flush=True)
    break
  if found:break
 if not found:
  print('STUCK',remaining,flush=True);break
 # provisional valid JSON includes all names
 fallback={n:[k.translation([0,0,40]).tolist(),np.eye(4).tolist()] for n in remaining}
 json.dump({'order':remaining+removed[::-1],'paths':dict(fallback,**paths)},open('work/assembly.json','w'))
json.dump({'removed':removed,'remaining':remaining},open('work/progress.json','w'))
