import trimesh as tm,numpy as np,json,math,itertools
import manifold3d as mf
from pathlib import Path
ROOT=Path('/app');C=json.loads((ROOT/'submission/keyless.json').read_text());meshes={};group={}
for n in C['fixed']:group[n]='fixed'
for n,v in C['mobiles'].items():
 for p in v['parts']:group[p]=n
for p in (ROOT/'submission/parts').glob('*.stl'):meshes[p.stem]=tm.load(p)
for p in (ROOT/'supplied').glob('*.stl'):meshes[p.stem]=tm.load(p);group[p.stem]= 'barrel' if p.stem=='barrel_arbor' else ('minute' if p.stem=='minute_wheel' else 'fixed')
def manifold(m):return mf.Manifold(mf.Mesh(np.asarray(m.vertices,np.float32),np.asarray(m.faces,np.uint32)))
mans={n:manifold(m) for n,m in meshes.items()}
def vol(a,b):
 ba=a.bounding_box();bb=b.bounding_box()
 if any(ba[i+3]<=bb[i] or bb[i+3]<=ba[i] for i in range(3)):return 0
 return (a^b).volume()
if __name__=='__main__':
 print('PARTS')
 for n,m in meshes.items():
  if n not in group:continue
  if n in [p.stem for p in (ROOT/'supplied').glob('*.stl')]:continue
  rho=np.linalg.norm(m.vertices[:,:2]-[3.5,0],axis=1)
  print(n,'faces',len(m.faces),'watertight',m.is_watertight,'components',len(m.split()),'bounds',round(rho.max(),5),m.bounds[:,2].round(3).tolist())
 print('OVERLAPS')
 for a,b in itertools.combinations(meshes,2):
  if group[a]==group[b]:continue
  v=vol(mans[a],mans[b])
  if v> .0002:print(a,b,round(v,7),flush=True)
 print('HELD')
 for name,mob in C['mobiles'].items():
  if mob['kind'] not in ['free','spring']:continue
  d=np.array(mob['direction'],float);d/=np.linalg.norm(d);u=np.cross(d,[0,0,1] if abs(d[2])<.9 else [1,0,0]);u/=np.linalg.norm(u);v=np.cross(d,u)
  dirs=[u,-u,v,-v]+([d,-d] if mob['dof']=='rot' else [])
  for dd in dirs:
   hits=[]
   for p in mob['parts']:
    mm=mans[p].translate(.3*dd)
    for other in meshes:
     if group[other]==name:continue
     vv=vol(mm,mans[other])
     if vv>.0002:hits.append((other,round(vv,6)))
   print(name,dd.tolist(),hits,flush=True)
