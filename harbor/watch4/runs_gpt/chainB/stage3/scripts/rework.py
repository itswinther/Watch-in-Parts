import sys,math,json
sys.path.insert(0,'tools')
import kernel as k
import cadquery as cq
import numpy as np
from pathlib import Path
D=Path('work/parts')
def cyl(x,y,z0,z1,r):return cq.Workplane('XY').workplane(offset=z0).center(x,y).circle(r).extrude(z1-z0)
def gear(n,m,phase,x,y,z,t):
 rp=n*m/2; rb=rp*math.cos(math.radians(25)); rr=rp-1.25*m; ra=rp+m
 inv=lambda r: math.sqrt(max(0,(r/rb)**2-1))-math.acos(min(1,rb/r))
 half=math.pi/(2*n)-.03/(2*rp); ip=inv(rp)
 pts=[]
 for j in range(n):
  a=math.radians(phase)+j*2*math.pi/n
  flank=lambda r:half+ip-inv(max(r,rb))
  for r,ang in [(rr,-flank(rb))]+[(r,-flank(r)) for r in np.linspace(max(rr,rb),ra,12)]+[(ra,flank(ra))]+[(r,flank(r)) for r in np.linspace(ra,max(rr,rb),12)]+[(rr,flank(rb))]:
   pts.append((x+r*math.cos(a+ang),y+r*math.sin(a+ang)))
 pts=[p for i,p in enumerate(pts) if i==0 or math.dist(p,pts[i-1])>1e-8]
 return cq.Workplane('XY').workplane(offset=z).polyline(pts).close().extrude(t)
A=np.array([10.,-math.sqrt(12.8**2-100)])
T=np.array([12.,0.]); mid=(A+T)/2; delta=T-A; norm=np.linalg.norm(delta); off=math.sqrt(4.8**2-norm**2/4)*np.array([-delta[1],delta[0]])/norm
B=mid-off
angle=lambda d:math.degrees(math.atan2(d[1],d[0]))
pa=180+4*angle(A)-180/32
pb=2*angle(B-A)+180+180/24
pt=2*angle(T-B)+180+180/24-pb
print('axes',A,B,'phases',pa,pb,pt,flush=True)
# Replace just the old input gear; preserve its exact arbor and stops.
s=cq.importers.importStep('previous/parts/transfer_pinion.step')
# remove all gear material outside the central arbor between z 0 and 1
cut=cyl(12,0,-.001,1.001,3).cut(cyl(12,0,-.01,1.01,.4))
s=s.cut(cut).union(gear(24,.2,pt,*T,1.65,.9))
k.write_step(D/'transfer_pinion.step',s)
a=gear(32,.2,pa,*A,0,1).union(gear(24,.2,0,*A,1.65,.9)).union(cyl(*A,-.85,2.95,.55))
b=gear(24,.2,pb,*B,1.65,.9).union(cyl(*B,-.85,2.95,.55))
k.write_step(D/'reduction_input.step',a); k.write_step(D/'reduction_idler.step',b)
# Bore the bridge for the added shafts. The existing sheet at 1.1..1.4
# lies between the two gear levels. Bearing feet and caps capture both shafts.
bridge=cq.importers.importStep('previous/parts/lower_bridge.step')
for C in [A,B]:
 bridge=bridge.cut(cyl(*C,-1.11,1.41,.65))
 # bottom radial bearing; the wheel face and bottom plate limit axial travel
 bearing=cyl(*C,-1.0,-.10,1.05).cut(cyl(*C,-1.01,-.09,.65))
 # top bearing cap and side post, outside the rotating envelopes
 # use a post on the positive x side for both
 post=C+np.array([3.9,0.])
 cap=cyl(*C,2.65,3.35,1.05).cut(cyl(*C,2.64,3.05,.65))
 arm=cq.Workplane('XY').workplane(offset=3.0).center(C[0]+1.95,C[1]).box(4.9,1.,.3,centered=(True,True,False))
 pillar=cyl(*post,-.95,3.3,.5)
 armlo=cq.Workplane('XY').workplane(offset=-.95).center(C[0]+2.4,C[1]).box(3.7,1.,.3,centered=(True,True,False))
 bridge=bridge.union(bearing).union(cap).union(arm).union(pillar).union(armlo)
k.write_step(D/'lower_bridge.step',bridge)
m=json.loads(Path('previous/movement.json').read_text())
m['mobiles']['reduction_input']={'axis':A.tolist(),'parts':['reduction_input']}
m['mobiles']['reduction_idler']={'axis':B.tolist(),'parts':['reduction_idler']}
m['meshes']= [ {'driver':'barrel','driver_teeth':96,'driven':'reduction_input','driven_teeth':32}, {'driver':'reduction_input','driver_teeth':24,'driven':'reduction_idler','driven_teeth':24}, {'driver':'reduction_idler','driver_teeth':24,'driven':'transfer','driven_teeth':24} ]+m['meshes'][1:]
Path('work/movement.json').write_text(json.dumps(m,indent=2)+'\n')
