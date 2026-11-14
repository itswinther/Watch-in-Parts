import numpy as np, trimesh as tm, math, json
from pathlib import Path
O=Path('/app/submission'); P=O/'parts'; P.mkdir(exist_ok=True)
pi=np.pi

def union(*ms):
 return tm.boolean.union(list(ms),engine='manifold') if len(ms)>1 else ms[0]
def diff(a,b):return tm.boolean.difference([a,b],engine='manifold')
def box(lo,hi):
 lo=np.array(lo);hi=np.array(hi);m=tm.creation.box(hi-lo);m.apply_translation((lo+hi)/2);return m
def cyl(r,z0,z1,c=(0,0),bore=0,n=96):
 m=tm.creation.annulus(r_min=bore,r_max=r,height=z1-z0,sections=n) if bore else tm.creation.cylinder(r,height=z1-z0,sections=n)
 m.apply_translation([*c,(z0+z1)/2]);return m
def xform_x(m,x0=0):
 # local z -> x, local x -> y, local y -> z
 T=np.eye(4);T[:3,:3]=[[0,0,1],[1,0,0],[0,1,0]];T[0,3]=x0;m.apply_transform(T);return m
def xcyl(r,a,b,bore=0):return xform_x(cyl(r,a,b,bore=bore))
def ring_mesh(angles,radii,z0,z1,bore,twist=0,layers=2,center=(0,0),phase=0):
 angles=np.asarray(angles);radii=np.asarray(radii);n=len(angles);verts=[]
 for z in np.linspace(z0,z1,layers):
  a=angles+phase+twist*(z-(z0+z1)/2)
  for rad in (radii,np.full(n,bore)):
   verts.extend(np.column_stack([center[0]+rad*np.cos(a),center[1]+rad*np.sin(a),np.full(n,z)]))
 faces=[]
 for k in range(layers-1):
  for i in range(n):
   j=(i+1)%n; a=k*2*n+i;b=k*2*n+j;c=(k+1)*2*n+j;d=(k+1)*2*n+i
   faces.extend([[a,b,c],[a,c,d]])
   a+=n;b+=n;c+=n;d+=n;faces.extend([[a,c,b],[a,d,c]])
 for i in range(n):
  j=(i+1)%n;faces.extend([[i,j+n,j],[i,i+n,j+n]])
  a=(layers-1)*2*n;faces.extend([[a+i,a+j,a+j+n],[a+i,a+j+n,a+i+n]])
 m=tm.Trimesh(vertices=verts,faces=faces,process=True);m.fix_normals();return m

def gear(n,rp,z0,z1,bore,helix=0,phase=0,center=(0,0),backlash=.015,pa=20):
 mn=2*rp/n*np.cos(helix);ra=rp+mn;rf=rp-1.25*mn
 alpha=np.arctan(np.tan(np.deg2rad(pa))/np.cos(helix));rb=rp*np.cos(alpha)
 inv=lambda a:np.tan(a)-a
 invp=inv(alpha);half=pi/(2*n)-backlash/(2*rp)
 rstart=max(rb,rf);abase=half+invp-inv(np.arccos(min(1,rb/rstart)))
 ang=[];rad=[]
 for t in range(n):
  mid=t*2*pi/n
  ang.append(mid-abase-.012);rad.append(rf)
  for r in np.linspace(rstart,ra,7):
   a=half+invp-inv(np.arccos(min(1,rb/r)));ang.append(mid-a);rad.append(r)
  atop=half+invp-inv(np.arccos(rb/ra))
  for a in np.linspace(-atop,atop,4)[1:]:ang.append(mid+a);rad.append(ra)
  for r in np.linspace(ra,rstart,7)[1:]:
   a=half+invp-inv(np.arccos(min(1,rb/r)));ang.append(mid+a);rad.append(r)
  ang.append(mid+abase+.012);rad.append(rf)
  end=(t+1)*2*pi/n-abase-.012
  for a in np.linspace(ang[-1],end,4)[1:-1]:ang.append(a);rad.append(rf)
 return ring_mesh(ang,rad,z0,z1,bore,np.tan(helix)/rp, max(2,int((z1-z0)/.04)+1),center,phase)

def face_ring(r0,r1,xbase,height,teeth=12,side='left'):
 # common interface x=base + height * tooth phase; left below, right above
 ns=teeth*12;angles=np.arange(ns)*2*pi/ns
 f=xbase+height*((np.arange(ns)%12)/12)
 # each tooth needs explicit near vertical drop, no zero angular width
 verts=[]
 for i,a in enumerate(angles):
  for r in (r0,r1):
   verts.extend([[f[i],r*np.cos(a),r*np.sin(a)],[(xbase-.15 if side=='left' else xbase+height+.22),r*np.cos(a),r*np.sin(a)]])
 faces=[]
 for i in range(ns):
  j=(i+1)%ns
  # quad at interface, back, inner, outer
  for a,b,c,d in [(4*i,4*j,4*j+2,4*i+2),(4*i+1,4*i+3,4*j+3,4*j+1),(4*i,4*i+1,4*j+1,4*j),(4*i+2,4*j+2,4*j+3,4*i+3)]:faces.extend([[a,b,c],[a,c,d]])
 m=tm.Trimesh(verts,faces,process=True);m.fix_normals();return m

def save(name,m):
 m.remove_unreferenced_vertices();m.fix_normals();m.export(P/(name+'.stl'));print(name,len(m.faces),'volume',round(m.volume,5),'solid',m.is_watertight,flush=True)
 return m

# winding crossed helicals, ratio 5, both right handed, axes x and z.
rp=.6928333333333334;R=5*rp;beta=pi/4
wg=xform_x(gear(8,rp,1.65,2.45,.25,beta,phase=0,backlash=.009))
wg=union(wg,xcyl(.385,1.4,2.49,.25),face_ring(.32,.50,2.56,.04,36,'left'),xcyl(.50,2.40,2.425,.25))
save('winding_pinion',wg)
# barrel top ratchet teeth; negative angular slope permits forward lift.
ang=[];rad=[]
for i in range(36):
 for f in [0,.02,.25,.5,.75,.98]:ang.append((i+f)*2*pi/36);rad.append(3.1-.25*f)
rat=ring_mesh(ang,rad,1.15,1.43,.605,center=(2.15,4.157))
bg=gear(40,R,-.5,.5,.605,beta,phase=-pi/2+pi/40+math.radians(7.35),center=(2.15,4.157),backlash=.009)
bg=union(bg,cyl(.76,.45,1.43,(2.15,4.157),.605),rat)
save('barrel_gear',bg)
# Sliding crown-carried ratchet ring, spring loaded toward the winding wheel.
cl=union(face_ring(.32,.50,2.563,.04,36,'right'),xcyl(.50,2.81,2.94,.19))
save('sliding_clutch',cl)
# crown, shaft and selection collar; setting pinion arrives at x=7 after pulling .9.
yset=math.sqrt(5.7**2-2.35**2)-4.157
rs=yset* .4; Ri=yset*.6
sg=xform_x(gear(12,rs,5.90,6.30,.17,beta,phase=0,backlash=.008))
# gear center axial x6.1 in pos1, x7 in pos2
stem=union(xcyl(.18,.45,12.9),xcyl(.235,2.70,2.80),sg,xcyl(.75,12.72,13.15))
save('crown_stem',stem)
# Setting intermediate: crossed helical above, 21 tooth spur at minute level.
setting=union(gear(18,Ri,-.32,.32,.20,beta,phase=-pi/2+pi/18,center=(7,yset),backlash=.008),cyl(.30,-2.40,.44,(7,yset),.20),gear(21,2.1,-2.4,-1.9,.20,center=(7,yset),phase=math.radians(15.4),backlash=.025))
save('setting_intermediate',setting)
# setting axle fixed, with thrust shoulders, all one solid
ax=union(cyl(.18,-2.59,.62,(7,yset)),cyl(.37,-2.58,-2.44,(7,yset)),cyl(.37,.48,.64,(7,yset)))
save('setting_axle',ax)
# Stem/winding bearings, fixed individual washers; held on both sides.
save('winding_left_bearing',xcyl(.50,1.20,1.38,.225))
save('winding_right_bearing',xcyl(.30,2.70,2.77,.255))
# radial sliding click, nose just outside the root before the radial locking flank
click=box([5.065,4.057,1.14],[5.72,4.157,1.44])
save('barrel_click',click)
# open radial channel, lateral and axial retention; connected end bridge
rail=diff(box([5.40,3.707,.79],[6.20,4.507,1.79]),box([5.39,4.047,1.13],[6.15,4.167,1.45]))
save('click_guide',rail)
config={'mobiles':{'stem':{'kind':'stem','parts':['crown_stem']},'barrel':{'kind':'barrel','parts':['barrel_gear']},'winding_rotor':{'kind':'free','dof':'rot','point':[0,0,0],'direction':[1,0,0],'parts':['winding_pinion']},'crown_clutch':{'kind':'spring','dof':'slide','direction':[1,0,0],'rest':-1,'on_stem':True,'parts':['sliding_clutch']},'setting_rotor':{'kind':'free','dof':'rot','point':[7,yset,0],'direction':[0,0,1],'parts':['setting_intermediate']},'holding_click':{'kind':'spring','dof':'slide','direction':[1,0,0],'rest':-1,'parts':['barrel_click']}},'fixed':['setting_axle','winding_left_bearing','winding_right_bearing','click_guide']}
(O/'keyless.json').write_text(json.dumps(config,indent=2))
