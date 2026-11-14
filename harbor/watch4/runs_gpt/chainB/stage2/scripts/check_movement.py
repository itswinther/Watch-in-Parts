import sys,json,math,itertools,hashlib,time
from pathlib import Path
import numpy as np
sys.path.insert(0,'tools')
import kernel as k
import manifold3d as m3
D=json.loads(Path('work/movement.json').read_text()); cache=Path('check_cache');cache.mkdir(exist_ok=True)
P={}
for name in D['fixed']+sum([m['parts'] for m in D['mobiles'].values()],[]):
 path=Path('work/parts')/(name+'.step');key=hashlib.sha256(path.read_bytes()).hexdigest();cp=cache/(key+'.stl')
 if cp.exists(): man=k.tris_to_manifold(k.read_stl(cp,200000,33554432))
 else:
  print('load',name,flush=True)
  man=k.load_step_part(str(path),16777216,200000,.001,.1,500,120,4096,.005)
  k.write_stl(cp,man)
 P[name]=man
P['barrel']=k.tris_to_manifold(k.read_stl('meshes/barrel.stl',200000,33554432))
A={n:m['axis'] for n,m in D['mobiles'].items()};A['barrel']=[0,0]
M={n:k.union([P[p] for p in m['parts']]) for n,m in D['mobiles'].items()};M['barrel']=P['barrel']
F=k.union([P[p] for p in D['fixed']])
def rotate(s,axis,deg):
 a=math.radians(deg);c=math.cos(a);t=math.sin(a);x,y=axis
 return s.transform([[c,-t,0,x-c*x+t*y],[t,c,0,y-t*x-c*y],[0,0,1,0]])
def check_basic():
 print('ASSEMBLED',flush=True)
 for a,b in itertools.combinations(list(M)+D['fixed'],2):
  v=k.ivol((M|P)[a],(M|P)[b])
  if v>.0100001:print('FAIL overlap',a,b,v,flush=True)
 print('FREE',flush=True)
 for n,m in M.items():
  worst=max(k.ivol(rotate(m,A[n],a),F) for a in range(0,360,5))
  print(n,worst,flush=True)
 print('HELD',flush=True)
 for n,m in M.items():
  other=k.union([F]+[v for q,v in M.items() if q!=n]);coax=k.union([F]+[v for q,v in M.items() if q!=n and np.linalg.norm(np.array(A[n])-A[q])<.01])
  v=[]
  for a in range(3):
   for sign in [-1,1]:
    t=[0,0,0];t[a]=sign*.3;v.append(k.ivol(m.translate(t),coax if a==2 else other))
  print(n,v,flush=True)
 print('SIZE',flush=True)
 for n,m in M.items():
  r=np.linalg.norm(k.verts(m)[:,:2]-A[n],axis=1).max()+np.linalg.norm(np.array(A[n])-D['case_centre'])
  print(n,r,flush=True)
 print('height',max(p.bounding_box()[5] for p in P.values())-min(p.bounding_box()[2] for p in P.values()),flush=True)
def check_mesh(e,full=True):
 a,b=e['driver'],e['driven'];na,nb=e['driver_teeth'],e['driven_teeth'];N=8*max(na,nb) if full else 8
 jam=(0,None);dist=(0,None);drive=(float('inf'),None)
 for i in range(N):
  theta=i*360/(8*na);ma=rotate(M[a],A[a],theta);mb=rotate(M[b],A[b],-theta*na/nb)
  v=k.ivol(ma,mb)
  if v>jam[0]:jam=(v,i)
  if i%4==0:
   d=k.min_distance(ma,mb,.101)
   if d>dist[0]:dist=(d,i)
  if i%8==0:
   v=k.ivol(rotate(M[a],A[a],theta+90/na),mb)
   if v<drive[0]:drive=(v,i)
  if i%200==0:print('mesh progress',a,b,i,flush=True)
 print('MESH',a,b,'jam',jam,'gap',dist,'drive',drive,flush=True)
def frozen():
 old=json.loads(Path('previous/movement.json').read_text())
 for n,m in old['mobiles'].items():
  assert D['mobiles'][n]['axis']==m['axis']
  for p in m['parts']:
   assert p in D['mobiles'][n]['parts']
   assert Path('work/parts',p+'.step').read_bytes()==Path('previous/parts',p+'.step').read_bytes()
 for e in old['meshes']:assert e in D['meshes']
 for n,h in old['hands'].items():assert D['hands'][n]==h
 print('FROZEN all pass',flush=True)
if __name__=='__main__':
 frozen()
 if len(sys.argv)==1 or sys.argv[1]=='basic':check_basic()
 elif sys.argv[1]=='mesh':
  for e in D['meshes']:
   if len(sys.argv)<3 or e['driven']==sys.argv[2]:check_mesh(e)
