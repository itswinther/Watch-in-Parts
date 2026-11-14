exec(open('/app/scripts/assemble.py').read().split('for n,s in solids.items():')[0])
import hashlib
A=json.load(open(ROOT/'work/assembly.json'))
assert len(A['order'])==len(names) and set(A['order'])==set(names)
lo=np.min([s.bounding_box()[:3] for s in solids.values()],axis=0)-5
hi=np.max([s.bounding_box()[3:] for s in solids.values()],axis=0)+5
placed=[];installed=[];results={}
for n in A['order']:
 Ts=np.asarray(A['paths'][n]);v=k.verts(solids[n]);errors=[]
 assert 2<=len(Ts)<=1500
 assert np.isfinite(Ts).all()
 assert np.max(abs(Ts[-1]-np.eye(4)))<=1e-6
 assert np.max(abs(Ts[:,3,:]-np.array([0,0,0,1])))<=1e-6
 assert np.max(abs(Ts[:,:3,:3].transpose(0,2,1)@Ts[:,:3,:3]-np.eye(3)))<=1e-6
 assert np.max(abs(np.linalg.det(Ts[:,:3,:3])-1))<=1e-6
 first=v@Ts[0,:3,:3].T+Ts[0,:3,3]
 assert any(first[:,i].max()<lo[i] or first[:,i].min()>hi[i] for i in range(3))
 max_step=0;previous=None;peak=0;hits=[]
 for j,T in enumerate(Ts):
  moved_v=v@T[:3,:3].T+T[:3,3]
  if previous is not None:max_step=max(max_step,float(np.linalg.norm(moved_v-previous,axis=1).max()))
  previous=moved_v
  moved=k.apply(solids[n],T)
  for p in placed:
   if group[p]==group[n]:continue
   vol=k.ivol(moved,solids[p]);peak=max(peak,vol)
   if vol>.01 and p not in hits:hits.append(p)
 assert max_step<=.2+1e-9
 if not hits:installed.append(n)
 results[n]={'installed':not hits,'poses':len(Ts),'max_vertex_step':max_step,'peak_collision':peak,'blockers':hits}
 print(n,results[n],flush=True)
 placed.append(n)
for p in ['movement.json']+[f'parts/{n}.step' for n in names if n!='barrel']:
 assert (ROOT/'work'/p).read_bytes()==(ROOT/'previous'/p).read_bytes(),p
print('INSTALLED',len(installed),'OF',len(names),'SCORE',.5*(len(installed)/len(names))**2,flush=True)
json.dump(results,open(ROOT/'verification.json','w'),indent=2)
