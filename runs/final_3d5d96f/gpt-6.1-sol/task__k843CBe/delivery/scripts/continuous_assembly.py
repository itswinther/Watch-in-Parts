import sys,json,numpy as np
sys.path.insert(0,'/app/tools');import kernel as k
root='/app/delivery/';doc=json.load(open(root+'movement.json'));asm=json.load(open(root+'assembly.json'))
ns=doc['fixed']+sum([v['parts'] for v in doc['mobiles'].values()],[])+['barrel']
parts={n:k.tris_to_manifold(k.read_stl('/app/'+n+'.stl',200000,16777216)) for n in ns}
levels={n:np.unique(np.round(k.verts(m)[:,2],6)) for n,m in parts.items()}
allv=np.concatenate([k.verts(m) for m in parts.values()]);lo=allv.min(0)-5;hi=allv.max(0)+5
previous=[];failed=False
for n in asm['order']:
 path=np.asarray(asm['paths'][n]); vs=k.verts(parts[n]);start=vs+path[0,:3,3]
 assert ((start.max(0)<lo)|(start.min(0)>hi)).any(),n
 assert np.linalg.norm(np.diff(path[:,:3,3],axis=0),axis=1).max()<=.2+1e-9
 assert np.allclose(path[-1],np.eye(4))
 hits={}
 for other in previous:
  # Each solid has a polygonal footprint constant between successive z levels.
  # Consequently the intersection volume under z translation is piecewise linear,
  # and all its maxima occur when two of these levels coincide.
  aa,bb=parts[n].bounding_box(),parts[other].bounding_box()
  if any(aa[j]>=bb[j+3] or bb[j]>=aa[j+3] for j in [0,1]):continue
  offsets=np.unique(np.clip((levels[other][:,None]-levels[n]).ravel(),0,25))
  for z in offsets:
   vol=k.ivol(parts[n].translate([0,0,float(z)]),parts[other])
   if vol>.01:
    hits[other]=(float(z),vol);failed=True;break
 print(n,hits,flush=True);previous.append(n)
print('continuous assembly', 'FAIL' if failed else 'PASS',flush=True)
