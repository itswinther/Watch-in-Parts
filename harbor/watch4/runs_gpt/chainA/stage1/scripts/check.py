import sys,json,os,pickle,math,time
sys.path.insert(0,'/app/tools');import kernel as k
import numpy as np
D=json.load(open('work/movement.json'))
P={}
for n in D['fixed']+sum([v['parts'] for v in D['mobiles'].values()],[]):
 path='work/parts/'+n+'.step'; cache='work/'+n+'.pickle'
 if os.path.exists(cache) and os.path.getmtime(cache)>os.path.getmtime(path):
  tris=pickle.load(open(cache,'rb'));P[n]=k.tris_to_manifold(tris)
 else:
  tris=k.read_step(path,16777216,200000,.001,.1,500,120,4096);pickle.dump(tris,open(cache,'wb'));P[n]=k.tris_to_part(tris,.005)
 print('load',n,flush=True)
P['barrel']=k.tris_to_manifold(k.read_stl('meshes/barrel.stl',200000,33554432))
M={n:k.union([P[p] for p in v['parts']]) for n,v in D['mobiles'].items()};M['barrel']=P['barrel']
AX={n:v['axis'] for n,v in D['mobiles'].items()};AX['barrel']=[0,0]
def rot(n,a):
 x,y=AX[n];return M[n].translate([-x,-y,0]).rotate([0,0,a]).translate([x,y,0])
F=k.union([P[n] for n in D['fixed']])
if '--mesh' not in sys.argv:
 for i,n in enumerate(D['fixed']):
  for m in D['fixed'][i+1:]:
   v=k.ivol(P[n],P[m])
   if v>.01:print('FIXED_COLLISION',n,m,v,flush=True)
 names=list(M)
 for i,n in enumerate(names):
  v=k.ivol(M[n],F)
  if v>.01:print('ASSEMBLED_FIXED',n,v,flush=True)
  for m in names[i+1:]:
   v=k.ivol(M[n],M[m])
   if v>.01: print('ASSEMBLED_MOBILE',n,m,v,flush=True)
 for n in names:
  worst=max(k.ivol(rot(n,a),F) for a in range(0,360,5))
  print('FREE',n,worst,flush=True)
  vals=[]
  for d in [[.3,0,0],[-.3,0,0],[0,.3,0],[0,-.3,0],[0,0,.3],[0,0,-.3]]:
   hold=k.union([F]+[M[m] for m in names if m!=n and (not d[2] or np.linalg.norm(np.array(AX[m])-AX[n])<.01)])
   vals.append(k.ivol(M[n].translate(d),hold))
  print('HELD',n,vals,flush=True)
else:
 for e in D['meshes']:
  a,b,n,m=e['driver'],e['driven'],e['driver_teeth'],e['driven_teeth']; jams=[];dis=[];drive=[]
  for i in range(8*max(n,m)):
   aa=i*360/(8*n);u=rot(a,aa);v=rot(b,-aa*n/m)
   vol=k.ivol(u,v)
   if vol>.01:jams.append((i,vol))
   if i%4==0:
    gap=k.min_distance(u,v,.101)
    if gap>.1:dis.append((i,gap))
   if i%8==0:
    vol=k.ivol(rot(a,aa+90/n),v)
    if vol<=.01:drive.append((i,vol))
  print('MESH',a,b,'jam',len(jams),jams[:4],'gap',len(dis),dis[:4],'drivefail',len(drive),drive[:4],flush=True)
