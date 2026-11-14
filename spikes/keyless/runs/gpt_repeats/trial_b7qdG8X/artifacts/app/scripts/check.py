import json,math,time
from pathlib import Path
import manifold3d as md
import numpy as np
import trimesh
P=Path('/app');D=json.loads((P/'submission/keyless.json').read_text())

def load(path):
 m=trimesh.load(path);return md.Manifold(md.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
S={p.stem:load(p) for p in (P/'submission/parts').glob('*.stl')}
S.update({p.stem:load(p) for p in (P/'supplied').glob('*.stl')})

def vol(a,b):
 aa=np.array(a.bounding_box());bb=np.array(b.bounding_box())
 if np.any(aa[:3]>=bb[3:]) or np.any(bb[:3]>=aa[3:]): return 0
 return (a^b).volume()

def rotate(m,axis,angle,point=(0,0,0)):
 ang=[0.,0.,0.];ang[axis]=angle
 return m.translate([-x for x in point]).rotate(ang).translate(point)

def restcheck():
 fail=[]
 names=list(S)
 print('SOLIDS',flush=True)
 for n in names:
  m=S[n];mesh=trimesh.load(P/('submission/parts' if n not in ['main_plate','dial_plate','minute_post','minute_wheel','barrel_arbor'] else 'supplied')/(n+'.stl'))
  if n in ['main_plate','dial_plate','minute_post','minute_wheel','barrel_arbor']:continue
  r=np.linalg.norm(mesh.vertices[:,:2]-[3.5,0],axis=1)
  print(n,'tri',len(mesh.faces),'closed',mesh.is_watertight,'components',len(mesh.split()),'vol',m.volume(),'radius',r.max(),'z',mesh.bounds[:,2],flush=True)
 print('OVERLAPS',flush=True)
 # parts belonging to same mobile are rigidly united, and supplied fixed parts may touch.
 for i,a in enumerate(names):
  for b in names[i+1:]:
   v=vol(S[a],S[b])
   if v>.0002:print(a,b,v,flush=True);fail.append((a,b,v))
 print('HELD',flush=True)
 for name,mob in D['mobiles'].items():
  if mob['kind'] not in ['free','spring']:continue
  axis=np.argmax(np.abs(mob['direction']));shifts=[]
  for i in range(3):
   if i==axis and mob['dof']!='rot':continue
   for sign in [-1,1]:
    off=[0,0,0];off[i]=.3*sign
    hits=[]
    for part in mob['parts']:
     a=S[part].translate(off)
     for n,b in S.items():
      if n in mob['parts']:continue
      v=vol(a,b)
      if v>.0002:hits.append((n,round(v,6)))
    print(name,off,hits,flush=True)
 return fail
if __name__=='__main__':restcheck()
