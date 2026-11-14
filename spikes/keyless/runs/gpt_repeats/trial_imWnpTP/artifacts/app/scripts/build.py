import math,json,time
from pathlib import Path
import numpy as np
import manifold3d as M
import trimesh
OUT=Path('/app/submission'); PARTS=OUT/'parts'; PARTS.mkdir(exist_ok=True)
D=math.pi/180
B=np.array([2.15,4.157]); cw_x=2.15-math.sqrt(4.2**2-4.157**2)
S=np.array([4.65+math.sqrt(5.6**2-4.157**2),0.])
WX=cw_x+2.52; SX=S[0]+1.2
print('centres',cw_x,S,'pinions',WX,SX,flush=True)

def union(a):return M.Manifold.batch_boolean(a,M.OpType.Add)
def cyl(r,z0,z1,xy=(0,0),n=96):return M.Manifold.cylinder(z1-z0,r,circular_segments=n).translate([*xy,z0])
def xcyl(r,x0,x1,yz=(0,0),n=80):return M.Manifold.cylinder(x1-x0,r,circular_segments=n).rotate([0,90,0]).translate([x0,*yz])
def box(lo,hi):return M.Manifold.cube(np.array(hi)-lo).translate(lo)
def extr(poly,z0,z1):return M.Manifold.extrude(M.CrossSection([poly]),z1-z0).translate([0,0,z0])
def ring(r,ri,z0,z1,xy=(0,0)):return cyl(r,z0,z1,xy)-cyl(ri,z0-.01,z1+.01,xy)
def gear(n,mod,z0,z1,phase=0,clear=.008,pa=25):
 rp=n*mod/2; rb=rp*math.cos(pa*D); root=rp-1.25*mod; tip=rp+mod
 inv=lambda r:math.tan(math.acos(min(1,rb/r)))-math.acos(min(1,rb/r))
 hp=math.pi/(2*n)-clear/(2*rp); ip=inv(rp); pts=[]
 for i in range(n):
  c=2*math.pi*i/n+phase*D
  rr=np.r_[root,np.linspace(max(root,rb),tip,10)]
  flank=[hp+ip-inv(r) for r in rr]
  for r,a in zip(rr,flank):pts.append([r*math.cos(c-a),r*math.sin(c-a)])
  for r,a in zip(rr[::-1],flank[::-1]):pts.append([r*math.cos(c+a),r*math.sin(c+a)])
  end=c+2*math.pi/n-(hp+ip-inv(root))
  start=c+hp+ip-inv(root)
  for a in np.linspace(start,end,4)[1:-1]:pts.append([root*math.cos(a),root*math.sin(a)])
 gear.last_outline=np.asarray(pts)
 return extr(pts,z0,z1)

def face(n,r,pinion,phase=0):
 print('face',n,flush=True)
 # Sample the lower envelope left by a generating pinion. The regular mesh
 # avoids sliver triangles at the periodic boundaries of Boolean-cut teeth.
 ns=40; nr=5; half=math.pi/n
 aa=np.linspace(-half,half,ns+1)[:-1]; rr=np.linspace(r-.19,r+.19,nr)
 ag,rg=np.meshgrid(aa,rr,indexing='ij'); ang=ag.ravel(); rad=rg.ravel()
 top=np.full(len(ang),-.342)
 gear(8,.12,-.2,.2,clear=-.006); pp=gear.last_outline.copy(); yz=np.c_[pp[:,1],-pp[:,0]]
 for ph in np.arange(-56,56.001,.5):
  p=ph*D; beta=ang+p/(n/8)
  xx=rad*np.cos(beta); yy=rad*np.sin(beta)
  rot=yz@np.array([[math.cos(p),math.sin(p)],[-math.sin(p),math.cos(p)]])
  y0=rot[:,0]; y1=np.roll(y0,-1); z0=rot[:,1]; z1=np.roll(z0,-1)
  dy=y1-y0; dy[np.abs(dy)<1e-12]=1e-12
  t=(yy[:,None]-y0[None,:])/dy[None,:]
  zz=z0[None,:]+t*(z1-z0)[None,:]
  zz[(t<0)|(t>1)]=10
  low=zz.min(axis=1)
  low[np.abs(xx-r)>.20]=10
  top=np.minimum(top,low)
 zz=top.reshape(ns,nr)
 # Full annular height field. Every periodic boundary shares its vertices.
 verts=[]
 for i in range(n*ns):
  a=-half+2*math.pi*i/(n*ns)
  for j,rv in enumerate(rr):verts.append([rv*math.cos(a),rv*math.sin(a),zz[i%ns,j]])
 count=len(verts)
 for v in verts[:]:verts.append([v[0],v[1],-.736])
 faces=[]; nt=n*ns
 for i in range(nt):
  ii=(i+1)%nt
  for j in range(nr-1):
   a=i*nr+j;b=ii*nr+j;c=b+1;d=a+1
   faces.extend([[a,d,c],[a,c,b],[a+count,c+count,d+count],[a+count,b+count,c+count]])
  for j in [0,nr-1]:
   a=i*nr+j;b=ii*nr+j
   ff=[[a,b,b+count],[a,b+count,a+count]]
   faces.extend(ff if j==0 else [f[::-1] for f in ff])
 shape=M.Manifold(M.Mesh(np.array(verts,dtype=np.float32),np.array(faces,dtype=np.uint32)))
 print('face mesh',shape.status(),shape.num_tri(),flush=True)
 return shape.rotate([0,0,phase])

parts={}; mobiles={}; fixed=[]
def save(name,shape):
 shape=union([p for p in shape.decompose() if p.volume()>1e-8]).set_tolerance(0.0002).simplify(0.0002)
 mesh=shape.to_mesh(); t=trimesh.Trimesh(np.asarray(mesh.vert_properties)[:,:3],np.asarray(mesh.tri_verts),process=True)
 print(name,shape.status(),len(t.faces),t.volume,'solids',len(shape.decompose()),flush=True)
 if len(shape.decompose())!=1: print([(p.volume(),p.bounding_box()) for p in shape.decompose()],flush=True)
 print('watertight',t.is_watertight,'euler',t.euler_number,'degenerate',sum(~t.nondegenerate_faces()),flush=True)
 if not t.is_watertight:
  t.update_faces(t.nondegenerate_faces(height=1e-9));t.update_faces(t.unique_faces());t.remove_unreferenced_vertices();print('clean watertight',t.is_watertight,'euler',t.euler_number,flush=True)
 if not t.is_watertight or t.volume<=0 or len(shape.decompose())!=1:raise RuntimeError(name+' invalid')
 t.export(PARTS/(name+'.stl'));parts[name]=shape

def mobile(name,shape,kind='free',dof='rot',point=None,direction=(0,0,1),**kw):
 save(name,shape);v={'kind':kind,'parts':[name]}
 if kind in ('free','spring'):
  v.update(dof=dof,direction=list(direction));
  if dof=='rot':v['point']=point
 v.update(kw);mobiles[name]=v

# Eight-leaf steel winding pinion, circular journal and axial ratchet face.
pin=gear(8,.12,-.155,.155,clear=.010).rotate([0,90,0])
cutter=gear(8,.12,-.20,.20,clear=-.006).rotate([0,90,0])
fc=face(42,2.52,cutter)
wind=union([gear(42,.12,-1.5,-1.05),cyl(2.30,-1.10,-.735),cyl(2.71,-1.03,-.735),fc,cyl(.4,-1.80,-1.04)])-cyl(.225,-1.9,-.5)
mobile('winding_face_wheel',wind.translate([cw_x,0,0]),point=[cw_x,0,0])
# Setting crown: separate upper face and lower twenty-leaf spur, on a common boss.
alpha=math.atan2(-4.157,4.65-S[0]); setphase=((alpha+(36*(alpha+math.pi-5*D)-math.pi)/20)/D)%18
fcset=face(20,1.2,cutter)
setting=union([gear(20,.2,-2.4,-1.9,phase=setphase),cyl(.79,-1.9,-.90),cyl(1.39,-.90,-.735),fcset,cyl(.36,-2.5,-1.9)])-cyl(.205,-2.6,-.3)
mobile('setting_face_wheel',setting.translate([*S,0]),point=[*S,0])

# Axial Breguet ratchet.  Positive relative rotation rides its ramps;
# negative stem rotation meets the friction-locking faces and drives the rotor.
def axial_ratchet(xbase,r0,r1,height,n=24,upper=False,gap=.008):
 verts=[]; faces=[]; sub=16
 for k in range(n):
  for j in range(sub):
   t=j/(sub-1)*.78;a=(k+t)*2*math.pi/n;f=xbase+height*t/.78
   for r in [r0,r1]:
    for x in ([f+gap,xbase+height+.18] if upper else [xbase-.10,f]):verts.append([x,r*math.cos(a),r*math.sin(a)])
 nt=n*sub
 for i in range(nt):
  a=4*i;b=4*((i+1)%nt)
  # ordering per angular ring: inner low, inner high, outer low, outer high
  faces.extend([[a+1,a+3,b+3],[a+1,b+3,b+1],[a,b+2,a+2],[a,b,b+2],
                [a,a+1,b+1],[a,b+1,b],[a+2,b+3,a+3],[a+2,b+2,b+3]])
 return M.Manifold(M.Mesh(np.array(verts,dtype=np.float32),np.array(faces,dtype=np.uint32)))

base=WX+.45
rotor=union([pin.translate([WX,0,0]),xcyl(.28,WX-.68,base-.08),xcyl(.39,WX-.68,WX-.60),xcyl(.96,base-.10,base+.001),axial_ratchet(base,.54,.94,.15)])-xcyl(.175,WX-.8,base+.4)
mobile('winding_pinion',rotor,point=[0,0,0],direction=[1,0,0])
clutch=union([axial_ratchet(base,.54,.94,.15,upper=True),xcyl(.76,base+.16,base+.33),xcyl(.50,base+.22,base+.33)])-xcyl(.18,base-.1,base+.7)
# Remove inner material forward of the stem shoulder, preserving the tooth annulus.
clutch=clutch-xcyl(.51,base-.05,base+.22)
mobile('sliding_clutch',clutch,kind='spring',dof='slide',direction=[1,0,0],rest=-1,on_stem=True)
# Main stem, fixed shoulders, and setting pinion (which arrives at SX after pulling).
stem=union([xcyl(.15,.1,13.0),xcyl(.48,12.65,13.1),xcyl(.50,base+.16,base+.22),xcyl(.50,base+.56,base+.62),pin.translate([SX-.9,0,0])])
mobile('stem',stem,kind='stem')

# Barrel arbor wheel and one-direction holding ratchet, all keyed to the given arbor.
def radial_ratchet(n,root,tip,z0,z1,phase=0):
 pts=[]
 for i in range(n):
  for t in np.linspace(0,1,12):
   a=(i+t)*2*math.pi/n+phase*D;r=tip-(tip-root)*t
   pts.append([r*math.cos(a),r*math.sin(a)])
 return extr(pts,z0,z1)
alpha=math.atan2(4.157,2.15-cw_x); bphase=((42*alpha+28*(alpha+math.pi)-math.pi)/28/D)%(360/28)
br=union([gear(28,.12,-1.5,-1.05,phase=bphase),cyl(.33,-1.75,.9),radial_ratchet(24,1.55,1.9,.35,.65),cyl(.59,.65,.9)])
mobile('barrel',br.translate([*B,0]),kind='barrel')
# The click slides radially, its square end sits behind a ratchet locking face.
click=union([box([B[0]+1.67,B[1]-.10,.36],[B[0]+2.45,B[1]-.005,.64]),box([B[0]+2.15,B[1]-.18,.34],[B[0]+2.70,B[1]+.18,.66])])
mobile('barrel_click',click,kind='spring',dof='slide',direction=[1,0,0],rest=-1)

# Fixed bearing furniture, all joined by the upper plate rim / small bridges.
support=[]
# bottom journals and top caps for vertical wheels
for xy,ri,ro,zbot,ztop in [((cw_x,0),.205,.43,-1.83,-.69),(tuple(S),.185,.36,-2.52,-.70)]:
 support.extend([cyl(ri,-2.61,ztop+.10,xy),cyl(ro,-2.61,zbot,xy),cyl(ro,ztop,ztop+.10,xy)])
 # a side bridge rising above the stem and thence to the main plate: cap joins shaft already
# winding pinion journal x-sleeve, with axial clearance .02
jr=xcyl(.43,WX-.58,WX-.18)-xcyl(.295,WX-.7,WX-.1)
support.append(jr)
support.append(box([WX-.56,-.16,.39],[WX-.22,.16,2.61]))
# click guide channel, clearance in slide direction, with end stops
support.extend([box([B[0]+2.10,B[1]-.24,.27],[B[0]+3.16,B[1]-.19,.73]),box([B[0]+2.10,B[1]+.19,.27],[B[0]+3.16,B[1]+.24,.73]),box([B[0]+2.10,B[1]-.24,.27],[B[0]+3.16,B[1]+.24,.32]),box([B[0]+2.10,B[1]-.24,.68],[B[0]+3.16,B[1]+.24,.73]),box([B[0]+2.08,B[1]+.02,.27],[B[0]+2.15,B[1]+.24,.73]),box([B[0]+3.12,B[1]-.24,.27],[B[0]+3.16,B[1]+.24,.73]),box([B[0]+2.75,B[1]-.24,.71],[B[0]+3.16,B[1]+.24,2.61])])
# make one connected fixed part by a bridge above all gears, through plate-adjacent posts
support.extend([box([cw_x-.16,-.16,-.64],[cw_x+.16,.16,2.61]),box([S[0]-.12,-.12,-.65],[S[0]+.12,.12,2.61]),box([cw_x-.16,-.16,2.44],[S[0]+.12,.16,2.61]),box([S[0]-.12,0,2.44],[S[0]+.12,B[1]+.24,2.61]),box([B[0]+2.75,B[1]-.16,2.44],[S[0]+.12,B[1]+.16,2.61])])
# Clear the main stem (including pull), leaving bridges at positive z.
support.extend([box([xx-.09,.24,-.64],[xx+.09,.35,2.61]) for xx in [cw_x,S[0]]])
support.extend([box([xx-.09,.10,2.44],[xx+.09,.35,2.61]) for xx in [cw_x,S[0]]])
sup=union(support)-xcyl(.17,-.1,14)
save('bearing_bridge',sup);fixed.append('bearing_bridge')
json.dump({'mobiles':mobiles,'fixed':fixed},open(OUT/'keyless.json','w'),indent=2)
print('DONE',flush=True)
