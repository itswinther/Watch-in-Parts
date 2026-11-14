from design import *
import itertools
P='/app/submission/'
k=json.load(open(P+'keyless.json'))
shapes={}; groups={}; meshes={}
for f in os.listdir(P+'parts'):
 if f.endswith('.stl'):
  n=f[:-4];shapes[n]=fromfile(P+'parts/'+f);meshes[n]=trimesh.load(P+'parts/'+f)
for f in os.listdir('/app/supplied'):
 n=f[:-4];shapes[n]=fromfile('/app/supplied/'+f);meshes[n]=trimesh.load('/app/supplied/'+f)
for n,m in k['mobiles'].items():
 for p in m['parts']:groups[p]=n
for p in k['fixed']+['main_plate','dial_plate','minute_post']:groups[p]='fixed'
groups['barrel_arbor']='barrel';groups['minute_wheel']='minute_wheel'
def overlap(a,b):
 ba=np.array(a.bounding_box()).reshape(2,3);bb=np.array(b.bounding_box()).reshape(2,3)
 if np.any(np.minimum(ba[1],bb[1])-np.maximum(ba[0],bb[0])<=0):return 0
 return (a^b).volume()
def rot(s,angle,point=(0,0,0),axis='z'):
 t=[0,0,0];t['xyz'.index(axis)]=angle
 return s.translate(tuple(-x for x in point)).rotate(t).translate(point)
if __name__=='__main__':
 results={'collisions':[],'bounds':[],'held':{}}
 for a,b in itertools.combinations(shapes,2):
  if groups[a]==groups[b]:continue
  v=overlap(shapes[a],shapes[b])
  if v>.0002:print('COLLISION',a,b,v,flush=True);results['collisions'].append([a,b,v])
 for n,t in meshes.items():
  if n in ['stem']:continue
  r=np.linalg.norm(t.vertices[:,:2]-[3.5,0],axis=1)
  if r.max()>8.70001 or t.bounds[0,2]<-3.40001 or t.bounds[1,2]>3.40001:print('BOUNDS',n,r.max(),t.bounds,flush=True);results['bounds'].append(n)
 for n,m in k['mobiles'].items():
  if m['kind'] not in ['free','spring']:continue
  # all free axes aligned to x or z
  axis=np.array(m['direction'],dtype=float);axis/=np.linalg.norm(axis)
  ds=[np.array([0,1,0]),np.cross(axis,[0,1,0])]
  if m['dof']=='rot':ds.append(axis)
  target=union([shapes[p] for p in m['parts']]);vv=[]
  for d in ds:
   for sg in [-1,1]:
    moved=target.translate(tuple(.3*sg*d));v=max(overlap(moved,s) for p,s in shapes.items() if groups[p]!=n)
    vv.append(v)
  results['held'][n]=vv;print('HELD',n,vv,flush=True)
 json.dump(results,open('/app/scripts/static_checks.json','w'),indent=2)
