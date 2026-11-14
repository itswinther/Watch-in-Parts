import os, json, math, time
import numpy as np
import trimesh
import manifold3d as M
from math import sin,cos,pi,sqrt,atan2
OUT='/app/submission/parts'
os.makedirs(OUT,exist_ok=True)
solids={}
def union(xs): return M.Manifold.batch_boolean(xs,M.OpType.Add)
def cyl(r,h,z=0,x=0,y=0,n=96): return M.Manifold.cylinder(h,r,r,n).translate((x,y,z))
def box(a,b,c,pos): return M.Manifold.cube((a,b,c)).translate(pos)
def poly(p,h,z=0): return M.CrossSection([p]).extrude(h).translate((0,0,z))
def ring(ro,ri,h,z=0,x=0,y=0): return cyl(ro,h,z,x,y)-cyl(ri,h+.02,z-.01,x,y)
def tm(s):
 a=s.to_mesh();return trimesh.Trimesh(np.asarray(a.vert_properties)[:,:3],np.asarray(a.tri_verts),process=True)
def orient_mesh(v,f):
 t=trimesh.Trimesh(v,f,process=True);v=np.asarray(t.vertices);f=np.asarray(t.faces).copy()
 edges={}
 for i,face in enumerate(f):
  for j in range(3):
   a,b=int(face[j]),int(face[(j+1)%3]);edges.setdefault(tuple(sorted((a,b))),[]).append((i,a<b))
 adj=[[] for _ in f]
 for es in edges.values():
  if len(es)==2:
   (a,da),(b,db)=es;adj[a].append((b,da==db));adj[b].append((a,da==db))
 seen={}
 for root in range(len(f)):
  if root in seen:continue
  seen[root]=False;stack=[root]
  while stack:
   a=stack.pop()
   for b,flip in adj[a]:
    if b not in seen:seen[b]=seen[a]^flip;stack.append(b)
 for i,flip in seen.items():
  if flip:f[i]=f[i][::-1]
 t=trimesh.Trimesh(v,f,process=False)
 if t.volume<0:t.invert()
 return t
def save(n,s):
 s=s.simplify(1e-6); t=tm(s);t.merge_vertices(digits_vertex=6);t.update_faces(t.nondegenerate_faces());t.update_faces(t.unique_faces());t.remove_unreferenced_vertices();t.export(OUT+'/'+n+'.stl'); solids[n]=s
 print(n,'tri',len(t.faces),'volume',round(t.volume,5),'solid',len(s.decompose()),flush=True)
 assert t.is_watertight and t.volume>0 and len(s.decompose())==1 and len(t.faces)<200000

def gear(n,m,h,z=0,phase=0,shift=0,backlash=0,outline=False):
 r=n*m/2; rb=r*cos(pi/9); rf=r-m*(1.25-shift); ra=r+m*(1+shift)
 inv=lambda a: math.tan(a)-a
 half=pi/(2*n)+2*shift*math.tan(pi/9)/n-backlash/(2*r)
 inv0=inv(pi/9); p=[]
 for k in range(n):
  a=phase+2*pi*k/n
  # CCW polygon: left root, left involute, tip arc, right involute, right root
  hb=half+inv0
  p.append((rf*cos(a-hb),rf*sin(a-hb)))
  radii=np.linspace(max(rf,rb),ra,9)
  for rr in radii:
   al=math.acos(min(1,rb/rr));ang=a-half-inv0+inv(al)
   p.append((rr*cos(ang),rr*sin(ang)))
  ht=half+inv0-inv(math.acos(rb/ra))
  for ang in np.linspace(a-ht,a+ht,5)[1:]:p.append((ra*cos(ang),ra*sin(ang)))
  for rr in radii[::-1][1:]:
   al=math.acos(min(1,rb/rr));ang=a+half+inv0-inv(al)
   p.append((rr*cos(ang),rr*sin(ang)))
  p.append((rf*cos(a+hb),rf*sin(a+hb)))
  for ang in np.linspace(a+hb,a+2*pi/n-hb,5)[1:-1]:p.append((rf*cos(ang),rf*sin(ang)))
 return p if outline else poly(p,h,z)
def sector(r1,r2,a1,a2,h,z):
 aa=np.linspace(a1,a2,40);p=[(r2*cos(a),r2*sin(a)) for a in aa]
 p += [(r1*cos(a),r1*sin(a)) for a in aa[::-1]] if r1 else [(0,0)]
 return poly(p,h,z)

def facegear():
 cache='/app/scripts/face_cache_v2.stl'
 if os.path.exists(cache):return fromfile(cache)
 p=np.array(gear(20,.075,1,backlash=-.006,outline=True))
 nr=5; na=49
 rad=np.linspace(.77,1.03,nr); ang=np.linspace(-pi/24,pi/24,na)
 X=(rad[:,None]*np.cos(ang)[None,:]).ravel();Y=(rad[:,None]*np.sin(ang)[None,:]).ravel()
 H=np.full(X.shape,-.64)
 for theta in np.arange(-22,22.001,.2):
  t=theta*pi/180;ph=t/1.2
  xx=X*cos(ph)-Y*sin(ph);yy=X*sin(ph)+Y*cos(ph)
  valid=np.abs(xx-.9)<=.143
  yc=p[:,1]*cos(t)+p[:,0]*sin(t);zc=p[:,1]*sin(t)-p[:,0]*cos(t)
  y1=yc[:,None];y2=np.roll(yc,-1)[:,None];z1=zc[:,None];z2=np.roll(zc,-1)[:,None]
  with np.errstate(divide='ignore',invalid='ignore'):
   frac=(yy[None,:]-y1)/(y2-y1); zz=z1+frac*(z2-z1)
  zz[(frac<0)|(frac>1)|~np.isfinite(zz)]=np.inf
  low=np.min(zz,axis=0)
  H[valid]=np.minimum(H[valid],low[valid])
 H=H.reshape(nr,na);H[:,0]=H[:,-1]=np.minimum(H[:,0],H[:,-1])
 # rotationally periodic structured mesh, closed bottom and walls
 aa=np.concatenate([ang[:-1]+k*pi/12 for k in range(24)]);nt=len(aa)
 hh=np.tile(H[:,:-1],(1,24));v=[]
 for rr in range(nr):
  for j,theta in enumerate(aa):v.append((rad[rr]*cos(theta),rad[rr]*sin(theta),hh[rr,j]))
 base=len(v)
 for rr in [rad[0],rad[-1]]:
  for theta in aa:v.append((rr*cos(theta),rr*sin(theta),-.85))
 f=[]
 for i in range(nr-1):
  for j in range(nt):
   k=(j+1)%nt;a=i*nt+j;b=(i+1)*nt+j;c=(i+1)*nt+k;d=i*nt+k
   f.extend([(a,b,c),(a,c,d)])
 for j in range(nt):
  k=(j+1)%nt
  # inner, outer, bottom
  f.extend([(j,base+k,base+j),(j,k,base+k)])
  a=(nr-1)*nt+j;b=(nr-1)*nt+k;c=base+nt+k;d=base+nt+j
  f.extend([(a,d,c),(a,c,b)])
  f.extend([(base+j,base+k,base+nt+k),(base+j,base+nt+k,base+nt+j)])
 mesh=trimesh.Trimesh(v,f,process=True);mesh.fix_normals()
 tooth=M.Manifold(M.Mesh(np.asarray(mesh.vertices,dtype=np.float32),np.asarray(mesh.faces,dtype=np.uint32)))
 crown=union([tooth,cyl(1.04,.12,-.96)])
 print('crown mesh',crown.num_tri(),crown.status(),len(crown.decompose()),flush=True)
 tm(crown).export(cache)
 return crown

def fromfile(path):
 t=trimesh.load(path);return M.Manifold(M.Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)))


def saw_axial(sleeve=False):
 n=36; angles=[]; heights=[]
 for k in range(n):
  for u in np.linspace(0,1,17):
   angles.append(k*2*pi/n+u*(2*pi/n-.0002));heights.append(.025*u)
 nn=len(angles);v=[]
 for rr in [.26,.54]:
  for a,h in zip(angles,heights):
   lo,hi=(h+.001,.34) if sleeve else (-.06,h)
   v.extend([(rr*cos(a),rr*sin(a),lo),(rr*cos(a),rr*sin(a),hi)])
 f=[]
 for j in range(nn):
  k=(j+1)%nn;a=2*j;b=2*k;c=2*nn+2*k;d=2*nn+2*j
  f.extend([(a,b,c),(a,c,d),(a+1,c+1,b+1),(a+1,d+1,c+1)])
  f.extend([(a,a+1,b+1),(a,b+1,b),(d,c,c+1),(d,c+1,d+1)])
 t=orient_mesh(v,f)
 shape=M.Manifold(M.Mesh(np.asarray(t.vertices,dtype=np.float32),np.asarray(t.faces,dtype=np.uint32)))
 return shape.rotate((0,90,0)).translate((3.50,0,0))

def ratchet():
 p=[];n=36
 for k in range(n):
  # radius drops with increasing angle; winding (+z) lifts the click
  for j in range(9):
   a=(k+j/8)*2*pi/n;r=3.65-.22*j/8
   p.append((r*cos(a),r*sin(a)))
 return poly(p,.30,1.0).translate((2.15,4.157,0))

def setting_pinion(cx):
 cache='/app/scripts/set_cache_v2.stl'
 if os.path.exists(cache): return fromfile(cache)
 t=trimesh.load('/app/supplied/minute_wheel.stl')
 xy=t.vertices[:,:2]-[4.65,-4.157];rr=np.linalg.norm(xy,axis=1)
 pp=np.unique(np.round(xy[rr>3.3],7),axis=0)
 aa=np.arctan2(pp[:,1],pp[:,0]);pp=pp[np.argsort(aa)]
 # cutter slightly enlarged to provide running backlash
 pp=pp*1.0006
 minute=M.CrossSection([pp])
 alpha=atan2(-4.157,4.65-cx)
 pts=[(1.0*cos(a),1.0*sin(a)) for a in np.linspace(alpha-pi/8-.0001,alpha+pi/8+.0001,80)]+[(0,0)]
 blank=M.CrossSection([pts])
 for phi in np.arange(-37,37.001,.25):
  cutter=minute.rotate(-phi*8/36).translate((4.65-cx,-4.157)).rotate(-phi)
  blank=blank-cutter
 pieces=[blank.rotate(k*45) for k in range(8)]
 cs=M.CrossSection.batch_boolean(pieces,M.OpType.Add)
 cs=cs.simplify(.00002)
 pin=cs.extrude(.5).translate((0,0,-2.4))
 # hub ties any undercut roots together
 pin=union([pin,cyl(.34,.5,-2.4)])
 pin=pin.simplify(.0001)
 print('setting pinion',pin.num_tri(),len(pin.decompose()),flush=True)
 tm(pin).export(cache)
 return pin

def bearing_post(cx,bottom):
 # bottom collar and spindle, with top retaining washer
 return union([cyl(.42,bottom-.02+2.6,-2.6,cx,0),cyl(.205,(-.72)-(-2.6),-2.6,cx,0),cyl(.40,.10,-.82,cx,0)])

def build():
 face=facegear()
 # integer spur ratio 66 / 16; centres 4.157 mm
 module=2*4.157/82
 inter=gear(16,module,.33,-1.50,shift=.10,backlash=.005)
 inter=union([inter,face,cyl(.40,.65,-1.50)])-cyl(.22,1.5,-1.6)
 save('winding_transfer',inter.translate((2.15,0,0)))
 # Phasing puts the inter tooth opposite a barrel gap
 barrelphase=pi/66 + pi/2 # opposite contact at -y
 barrel=gear(66,module,.33,-1.50,phase=barrelphase,shift=-.10,backlash=.005).translate((2.15,4.157,0))
 barrel=union([barrel,ratchet(),cyl(.80,2.75,-1.50,2.15,4.157)])-cyl(.603,3.0,-1.6,2.15,4.157)
 save('barrel_ratchet',barrel)
 # free winding pinion and its face ratchet
 pin=gear(20,.075,.28,-.14).rotate((0,90,0)).translate((3.05,0,0))
 hub=cyl(.30,.68,0).rotate((0,90,0)).translate((2.78,0,0))
 flange=cyl(.44,.08,0).rotate((0,90,0)).translate((3.20,0,0))
 pin=union([pin,hub,flange,saw_axial(False)])-cyl(.18,1.3,0).rotate((0,90,0)).translate((2.6,0,0))
 save('winding_pinion',pin)
 sleeve=union([saw_axial(True),cyl(.54,.20,0).rotate((0,90,0)).translate((3.74,0,0))])
 # inner clearance for stem pulling collar, plus a smaller guiding bore
 sleeve=sleeve-cyl(.25,.26,0).rotate((0,90,0)).translate((3.49,0,0))
 sleeve=sleeve-cyl(.175,.8,0).rotate((0,90,0)).translate((3.3,0,0))
 save('sliding_clutch',sleeve)
 # setting crown/pinion, in position 1 0.9 mm before engagement
 cx=4.65+sqrt(4.4**2-4.157**2);contact=cx-.9
 stemshaft=cyl(.16,11.4,0).rotate((0,90,0)).translate((1.6,0,0))
 pullcollar=cyl(.225,.09,0).rotate((0,90,0)).translate((3.63,0,0))
 setpin=gear(20,.075,.28,-.14).rotate((0,90,0)).translate((contact-.9,0,0))
 # hub for the setting pinion and a modest crown handle outside the case
 sethub=cyl(.29,.36,0).rotate((0,90,0)).translate((contact-1.08,0,0))
 crown=cyl(.65,.25,0).rotate((0,90,0)).translate((12.75,0,0))
 save('stem',union([stemshaft,pullcollar,setpin,sethub,crown]))
 setter=union([face.rotate((0,0,180)),setting_pinion(cx),cyl(.34,1.56,-2.4)])-cyl(.22,2,-2.5)
 save('setting_transfer',setter.translate((cx,0,0)))
 # sliding click and a rectangular guide attached to the main plate
 click=union([box(.34,.095,.24,(5.803,4.172,1.03)),box(.55,.27,.26,(6.05,4.14,1.02))])
 save('click',click)
 guide=union([box(1.1,.06,1.66,(6.02,4.06,.94)),box(1.1,.06,1.66,(6.02,4.43,.94)),box(1.1,.43,.06,(6.02,4.06,.94)),box(1.1,.43,.06,(6.02,4.06,1.30))])
 save('click_guide',guide)
 save('winding_post',bearing_post(2.15,-1.50))
 save('setting_post',bearing_post(cx,-2.40))
 # fixed split-style stem bearings held from the main plate
 for name,x,bore,outer in [('left_bearing',2.72,.18,.36),('right_bearing',3.30,.315,.44)]:
  ann=ring(outer,bore,.05).rotate((0,90,0)).translate((x,0,0))
  arm=box(.05,.22,2.6-(outer-.04),(x,-.11,outer-.04))
  save(name,union([ann,arm]))
 mobiles={
 'stem':{'kind':'stem','parts':['stem']},
 'barrel':{'kind':'barrel','parts':['barrel_ratchet']},
 'winding_pinion':{'kind':'free','dof':'rot','point':[3.05,0,0],'direction':[1,0,0],'parts':['winding_pinion']},
 'winding_transfer':{'kind':'free','dof':'rot','point':[2.15,0,0],'direction':[0,0,1],'parts':['winding_transfer']},
 'setting_transfer':{'kind':'free','dof':'rot','point':[cx,0,0],'direction':[0,0,1],'parts':['setting_transfer']},
 'clutch':{'kind':'spring','dof':'slide','direction':[1,0,0],'rest':-1,'on_stem':True,'parts':['sliding_clutch']},
 'click':{'kind':'spring','dof':'slide','direction':[1,0,0],'rest':-1,'parts':['click']}}
 fixed=['click_guide','winding_post','setting_post','left_bearing','right_bearing']
 with open('/app/submission/keyless.json','w') as f:json.dump({'mobiles':mobiles,'fixed':fixed},f,indent=2)
 print('built',cx,contact,flush=True)

if __name__=='__main__':build()
