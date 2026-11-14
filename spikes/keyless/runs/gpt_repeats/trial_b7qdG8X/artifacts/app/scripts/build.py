import math,json,time
from pathlib import Path
import numpy as np
import trimesh
import manifold3d as md
P=Path('/app'); OUT=P/'submission'; PART=OUT/'parts'; CACHE=P/'scripts/cache';CACHE.mkdir(exist_ok=True)
T=time.time()
def log(s): print(f'{time.time()-T:.1f}s {s}',flush=True)
def union(ms): return md.Manifold.batch_boolean(ms,md.OpType.Add)
def diff(a,bs): return md.Manifold.batch_boolean([a]+list(bs),md.OpType.Subtract)
def cyl(r,z0,z1,xy=(0,0),n=96): return md.Manifold.cylinder(z1-z0,r,r,n).translate([*xy,z0])
def tube(ro,ri,z0,z1,xy=(0,0),n=96): return cyl(ro,z0,z1,xy,n)-cyl(ri,z0-.01,z1+.01,xy,n)
def cx(r,x0,x1,n=96): return cyl(r,x0,x1,n=n).rotate([0,90,0])
def tx(ro,ri,x0,x1): return cx(ro,x0,x1)-cx(ri,x0-.01,x1+.01)
def box(x0,x1,y0,y1,z0,z1): return md.Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])
def poly_extrude(v,z0,z1):
 v=np.asarray(v)
 if np.sum(v[:,0]*np.roll(v[:,1],-1)-v[:,1]*np.roll(v[:,0],-1))<0:v=v[::-1]
 return md.Manifold.extrude(md.CrossSection([v]),z1-z0).translate([0,0,z0])
def from_stl(p):
 m=trimesh.load(p);return md.Manifold(md.Mesh(np.asarray(m.vertices,dtype=np.float32),np.asarray(m.faces,dtype=np.uint32)))
def export(m,path):
 mesh=m.to_mesh(); tr=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True)
 tr.update_faces(tr.nondegenerate_faces(height=1e-12));tr.update_faces(tr.unique_faces());tr.remove_unreferenced_vertices();tr.export(path)
 return tr

def profile(n,r=1,alpha=25,backlash=.002,phase=0):
 # Involute external tooth, profile around the whole wheel; groove at angle zero.
 module=2*r/n;rb=r*math.cos(math.radians(alpha));rr=r-1.25*module;ra=r+module
 inv=lambda a: math.tan(a)-a
 ip=inv(math.radians(alpha));half=math.pi/(2*n)-backlash/(2*r)
 verts=[]
 for k in range(n):
  center=(k+.5)*2*math.pi/n+phase
  radii=np.unique(np.r_[rr,max(rr,rb),np.linspace(max(rr,rb),ra,11)])
  angles=[]
  for rad in radii:
   ir=inv(math.acos(min(1,rb/rad))) if rad>=rb else 0
   angles.append(center-half-ip+ir)
  # Root valley arc, from previous tooth's root to this tooth's left root.
  prev=center-2*math.pi/n+half+ip
  for a in np.linspace(prev,angles[0],4,endpoint=False):verts.append([rr*math.cos(a),rr*math.sin(a)])
  for rad,a in zip(radii,angles):verts.append([rad*math.cos(a),rad*math.sin(a)])
  for a in np.linspace(angles[-1],2*center-angles[-1],4)[1:]:verts.append([ra*math.cos(a),ra*math.sin(a)])
  for rad,a in list(zip(radii,angles))[-2::-1]:
   a=2*center-a;verts.append([rad*math.cos(a),rad*math.sin(a)])
 return np.array(verts)

# Pitch radius .7 at the middle of a short, 45 degree straight bevel pinion.
# Both crown meshes use identical geometry and a generated mating wheel.
def cone_pinion():
 a,b=.62,.78
 shape=md.CrossSection([profile(20,r=1,backlash=.003)])
 shape=shape.scale([a,a])
 return md.Manifold.extrude(shape,b-a,scale_top=[b/a,b/a]).translate([0,0,a]).rotate([0,90,0])

def bevel_wheel(pin):
 cached=CACHE/'bevel2.stl'
 if cached.exists(): return from_stl(cached)
 # The tooth flanks are cones sharing the axis intersection. Generate the
 # conjugate section once and scale it towards that intersection.
 a,b=.15,1.5
 cs=md.CrossSection([profile(20,r=1,backlash=.003)])
 cutter=md.Manifold.extrude(cs.scale([a,a]),b-a,scale_top=[b/a,b/a]).translate([0,0,a]).rotate([0,90,0]).scale([1,1.002,1.002])
 blank=md.CrossSection.circle(.80,160)
 cuts=[]
 for t in np.linspace(0,18,73):
  cuts.append(cutter.rotate([t,0,0]).rotate([0,0,-t]).slice(-.7)^blank)
 sector=md.CrossSection.batch_boolean(cuts,md.OpType.Add)
 cut=md.CrossSection.batch_boolean([sector.rotate(i*18) for i in range(20)],md.OpType.Add)
 section=(blank-cut).simplify(.00025)
 section=max(section.decompose(),key=lambda c:c.area())
 log(f'bevel section {section.num_vert()} vertices, area {section.area()}')
 # Lower section at z=-.89, upper section at z=-.60, scaled about apex.
 lo,hi=.89,.60
 lower=section.scale([lo/.7,lo/.7])
 wheel=md.Manifold.extrude(lower,lo-hi,scale_top=[hi/lo,hi/lo]).translate([0,0,-lo])
 wheel=wheel-cyl(.59,-1.1,-.50)
 wheel=union([wheel,cyl(1.02,-1.035,-.885),cyl(.20,-1.035,-.6)])
 wheel=clean(wheel)
 export(wheel,cached)
 return wheel

def small_gear(big,center,tag):
 cached=CACHE/(tag+'2.stl')
 if cached.exists():return from_stl(cached)
 blank=md.CrossSection.circle(.8,120)
 big=big.slice(0).scale([1.0007,1.0007])
 cuts=[]
 for t in np.linspace(-5,5,121):
  c=big.rotate(t).translate(center).rotate(6*t)^blank
  if not c.is_empty():cuts.append(c)
 sector=md.CrossSection.batch_boolean(cuts,md.OpType.Add)
 allcuts=md.CrossSection.batch_boolean([sector.rotate(k*60) for k in range(6)],md.OpType.Add)
 section=(blank-allcuts).simplify(.00025)
 section=max(section.decompose(),key=lambda c:c.area())
 gear=md.Manifold.extrude(section,.5).translate([0,0,-.25])
 log(f'{tag}: {gear.num_tri()} triangles; area {section.area()}')
 export(gear,cached)
 return gear

def clean(m):
 comps=m.decompose()
 if len(comps)>1:
  ordered=sorted(comps,key=lambda c:c.volume(),reverse=True)
  log(f'clean: {len(comps)} components; largest volumes {[round(x.volume(),8) for x in ordered[:5]]}')
  return ordered[0]
 return m

# Sawtooth annular face coupling, local x axis.
def face_clutch(upper=False):
 n=32;rs=[.40,.66];A=4.075;H=.060;clear=.003
 # triangulated surface at each radial band; sawtooth includes a vertical edge.
 seg=3
 angles=[];heights=[]
 for k in range(n):
  for j in range(seg+1):
   angles.append((k+j/seg)*2*math.pi/n);heights.append(H*j/seg)
 V=[]
 # A thin solid per tooth, boolean united through the common backing.
 teeth=[]
 for k in range(n):
  ids=range(k*(seg+1),(k+1)*(seg+1));aa=np.array(angles)[list(ids)];hh=np.array(heights)[list(ids)]
  # Local z is axial, convert it to world x afterwards.
  verts=[]
  for side in [0,1]:
   for r in rs:
    for a,h in zip(aa,hh):
     z=(A+h+clear if upper else A-.065) if side==0 else (A+.21 if upper else A+h)
     verts.append([r*math.cos(a),r*math.sin(a),z])
  l=len(aa); faces=[]
  def quad(a,b,c,d):faces.extend([[a,b,c],[a,c,d]])
  for j in range(l-1):
   quad(j,j+1,l+j+1,l+j)
   quad(2*l+j,3*l+j,3*l+j+1,2*l+j+1)
   quad(j,2*l+j,2*l+j+1,j+1)
   quad(l+j,l+j+1,3*l+j+1,3*l+j)
  quad(0,l,3*l,2*l);quad(l-1,3*l-1,4*l-1,2*l-1)
  tm=trimesh.Trimesh(verts,faces,process=True);tm.fix_normals()
  teeth.append(md.Manifold(md.Mesh(np.asarray(tm.vertices,dtype=np.float32),np.asarray(tm.faces,dtype=np.uint32))))
 backing=tube(.680,.370,A+.180,A+.240) if upper else tube(.662,.17,A-.08,A-.06)
 return union(teeth+[backing]).rotate([0,90,0])

log('building gear cutters')
pin=cone_pinion(); bevel=bevel_wheel(pin)
big=poly_extrude(profile(36,r=3.6,backlash=.008),-.25,.25)
smallwind=small_gear(big,[-.6,4.157],'wind_pinion')
minute=from_stl(P/'supplied/minute_wheel.stl').translate([-4.65,4.157,2.15])
smallset=small_gear(minute,[-.6,-4.157],'set_pinion')

parts={};mobiles={};fixed=[]
def add(name,shape,kind=None,**kw):
 parts[name]=clean(shape)
 if kind:
  mobile=kw.pop('mobile',name)
  mobiles[mobile]={'kind':kind,'parts':[name],**kw}
 else:fixed.append(name)

# Crown and shaft. The inner end stops short of the winding wheel's upright axle.
stem=union([cx(.14,3.0,13.25),cx(.35,4.245,4.260),cx(.36,4.5,4.6),pin.translate([5.25-.9,0,0]),cx(.58,12.75,13.25),box(4.20,4.50,.10,.205,-.04,.04)])
add('crown_stem',stem,'stem',mobile='stem')
rotor=union([pin.translate([2.75,0,0]),cx(.26,3.50,4.02),face_clutch(False)])-cx(.172,2.9,4.4)
add('winding_pinion',rotor,'free',dof='rot',point=[0,0,0],direction=[1,0,0])
sleeve=union([face_clutch(True),tx(.43,.172,4.265,4.400)])-box(4.13,4.51,.12,.215,-.05,.05)
add('sliding_clutch',sleeve,'spring',dof='slide',direction=[1,0,0],rest=-1,on_stem=True)

windwheel=union([bevel,cyl(.20,-.62,1.55),smallwind.translate([0,0,1.325])]).translate([2.75,0,0])
add('winding_transfer',windwheel,'free',dof='rot',point=[2.75,0,0],direction=[0,0,1])
starhole=[]
for k in range(40):
 a=k*math.pi/20;r=.68 if k%2==0 else .82
 starhole.append([r*math.cos(a),r*math.sin(a)])
clearance_star=poly_extrude(starhole,-.885,-.5)
setwheel=union([bevel-clearance_star,cyl(.20,-2.40,-.93),smallset.translate([0,0,-2.15])]).translate([5.25,0,0])
add('setting_transfer',setwheel,'free',dof='rot',point=[5.25,0,0],direction=[0,0,1])

# Barrel wheel and a 60-tooth retaining ratchet on one rigid arbor mobile.
N=60;rat=[]
for k in range(N):
 for j in range(9):
  a=(k+j/8)*2*math.pi/N;r=3.20-.18*j/8
  rat.append([r*math.cos(a),r*math.sin(a)])
ratchet=poly_extrude(rat,1.82,2.25)
barrel=union([big.translate([0,0,1.325]),cyl(.82,1.50,1.90),ratchet])-cyl(.605,.8,2.4)
add('barrel_winding_wheel',barrel.translate([2.15,4.157,0]),'barrel',mobile='barrel')

# Radially sliding click: the upper flat is the locking face, the lower tip rides the ramps.
pawlpoly=np.array([[3.025,-.006],[3.47,-.006],[3.47,-.16],[3.10,-.070]])+[2.15,4.157]
pawl=poly_extrude(pawlpoly,1.91,2.20)
add('retaining_click',pawl,'spring',dof='slide',direction=[1,0,0],rest=-1)

# Bearings, thrust faces and fixed supports. Their running clearances are 15 microns.
windhold=union([
 tube(.38,.215,.30,1.07,(2.75,0)),
 tube(.40,.215,1.58,1.78,(2.75,0)),
 tube(.40,.215,-1.18,-1.065,(2.75,0)),
 cyl(.16,-1.18,2.60,(1.50,0)),
 box(1.50,2.50,-.145,.145,.45,.65),
 box(1.50,2.76,-.145,.145,1.62,1.76),
 box(1.50,2.76,-.145,.145,-1.18,-1.065)
])
add('winding_bridge',windhold)
rotorhold=union([tx(.48,.275,3.55,3.955),box(3.68,3.88,-1.3,-.32,-.12,.12),cyl(.15,-.12,2.6,(3.78,-1.3))])
add('pinion_bridge',rotorhold)
sethold=union([tube(.38,.215,-1.85,-1.10,(5.25,0)),box(5.12,5.38,.27,1.25,-1.6,-1.4),cyl(.15,-2.6,-1.4,(5.25,1.25))])
add('setting_bridge',sethold)
clickguide=box(3.23,3.73,-.50,.50,1.80,2.31)-box(3.22,3.74,-.175,.004,1.895,2.215)
clickguide=union([clickguide,box(3.5,3.7,-.25,.08,2.30,2.60)]).translate([2.15,4.157,0])
add('click_guide',clickguide)

log('writing parts')
for name,shape in parts.items():
 comps=shape.decompose()
 log(f'{name}: {shape.num_tri()} triangles, {len(comps)} components, volume {shape.volume():.5f}')
 export(shape,PART/(name+'.stl'))
(OUT/'keyless.json').write_text(json.dumps({'mobiles':mobiles,'fixed':fixed},indent=2))
log('done')
