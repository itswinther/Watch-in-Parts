import json,numpy as np,trimesh,manifold3d as M
from pathlib import Path
j=json.load(open('/app/submission/keyless.json'))
def read(p):
 t=trimesh.load(p);return M.Manifold(M.Mesh(np.array(t.vertices,dtype=np.float32),np.array(t.faces,dtype=np.uint32)))
s={p.stem:read(p) for p in Path('/app/submission/parts').glob('*.stl')}
s.update({p.stem:read(p) for p in Path('/app/supplied').glob('*.stl')})
body={n:n for n in s}
for n,m in j['mobiles'].items():
 for p in m['parts']:body[p]=n
body['barrel_arbor']='barrel';body.update({p:'fixed' for p in j['fixed']+['main_plate','dial_plate','minute_post']})
print('REST')
names=list(s)
for i,n in enumerate(names):
 for p in names[i+1:]:
  if body[n]==body[p]:continue
  v=(s[n]^s[p]).volume()
  if v>.0002:print(n,p,round(v,7))
print('BOUNDS')
for p in Path('/app/submission/parts').glob('*.stl'):
 t=trimesh.load(p);v=t.vertices;r=np.linalg.norm(v[:,:2]-[3.5,0],axis=1)
 print(p.stem,'water',t.is_watertight,'components',len(t.split()),'maxr',round(r.max(),4),'z',v[:,2].min(),v[:,2].max())
print('HELD')
for n,m in j['mobiles'].items():
 if m['kind'] not in ['free','spring']:continue
 d=np.array(m['direction'],float);d/=np.linalg.norm(d);u=np.cross(d,[0,0,1] if abs(d[2])<.9 else [1,0,0]);u/=np.linalg.norm(u);v=np.cross(d,u)
 vectors=[u,-u,v,-v]+([d,-d] if m['dof']=='rot' else [])
 for vec in vectors:
  obj=s[n].translate(vec*.3); hits=[(p,round((obj^sh).volume(),5)) for p,sh in s.items() if body[p]!=n and (obj^sh).volume()>.0002]
  print(n,vec,hits)
json.dump({'body':body},open('/app/scripts/check_meta.json','w'))
