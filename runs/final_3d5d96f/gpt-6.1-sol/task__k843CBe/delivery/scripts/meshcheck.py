import sys,json,numpy as np,math
sys.path.insert(0,'/app/tools');import kernel as k
root='/app/delivery/'
doc=json.load(open(root+'movement.json'))
names=doc['fixed']+sum([v['parts'] for v in doc['mobiles'].values()],[])+['barrel']
parts={n:k.tris_to_manifold(k.read_stl('/app/'+n+'.stl',200000,16777216)) for n in names}
def combine(n):
 if n=='barrel':return parts[n]
 return k.union([parts[p] for p in doc['mobiles'][n]['parts']])
def rotate(m,a,p):return m.translate([-p[0],-p[1],0]).rotate([0,0,a]).translate([p[0],p[1],0])
for mesh in doc['meshes']:
 a,b=mesh['driver'],mesh['driven'];n1,n2=mesh['driver_teeth'],mesh['driven_teeth']
 p=(0,0) if a=='barrel' else doc['mobiles'][a]['axis'];q=doc['mobiles'][b]['axis']
 ma,mb=combine(a),combine(b); worst=0
 for angle in np.linspace(0,360/n1,49):
  vol=k.ivol(rotate(ma,angle,p),rotate(mb,-angle*n1/n2,q));worst=max(worst,vol)
 print(a,b,'max tooth cycle intersection',worst,flush=True)
