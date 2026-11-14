import sys,math,json
from pathlib import Path
sys.path.insert(0,'tools')
import kernel
import cadquery as cq
M=.16
AX=(-.48,0)
def cylinder(x,y,r,z,h):
 return cq.Workplane('XY').workplane(offset=z).center(x,y).circle(r).extrude(h)
def gear(n,axis,z,h,phase=0):
 rp=M*n/2; rb=rp*math.cos(math.radians(25)); rr=rp-1.25*M; ra=rp+M
 inv=lambda a: math.tan(a)-a
 half=(math.pi*M/2-.03)/(2*rp)
 def flank(r):
  return half+inv(math.radians(25))-(inv(math.acos(rb/r)) if r>rb else 0)
 pts=[]
 def point(r,a): pts.append((axis[0]+r*math.cos(a),axis[1]+r*math.sin(a)))
 for i in range(n):
  a=2*math.pi*i/n+math.radians(phase)
  roots=flank(max(rr,rb))
  point(rr,a-roots)
  if rr<rb: point(rb,a-roots)
  for j in range(1,7):
   r=max(rr,rb)+(ra-max(rr,rb))*j/6
   point(r,a-flank(r))
  t=flank(ra)
  for j in range(1,4): point(ra,a-t+2*t*j/3)
  for j in range(5,-1,-1):
   r=max(rr,rb)+(ra-max(rr,rb))*j/6
   point(r,a+flank(r))
  if rr<rb: point(rr,a+roots)
  for j in range(1,4): point(rr,a+roots+(2*math.pi/n-2*roots)*j/4)
 return cq.Workplane('XY').workplane(offset=z).polyline(pts).close().extrude(h)
# Keep the received mobile shapes and add a pinion above the upper bridge.
pinion=gear(12,(12,0),6.25,1.1).union(cylinder(12,0,.4,5.8,.8))
wheel=gear(144,AX,6.25,1.1,1.25).union(cylinder(*AX,.5,5.8,2.85)).union(cylinder(*AX,.9,7.95,.3))
hand=cylinder(*AX,.9,7.55,.35).union(cq.Workplane('XY').workplane(offset=7.55).center(*AX).moveTo(-.3,0).lineTo(.3,0).lineTo(.18,4.2).lineTo(-.18,4.2).close().extrude(.35))
# Upper bridge gains a bearing bore without changing any mobile part.
upper=cq.importers.importStep('previous/parts/upper_bridge.step').cut(cylinder(*AX,.56,5.6,.6))
# A cantilevered cock, carried by a post outside the swept gear envelope.
post=(-12.6,1.)
dx=AX[0]-post[0];dy=AX[1]-post[1];L=math.hypot(dx,dy);ang=math.degrees(math.atan2(dy,dx))
beam=cq.Workplane('XY').workplane(offset=8.35).box(L, .8, .4, centered=(True,True,False)).rotate((0,0,0),(0,0,1),ang).translate(((AX[0]+post[0])/2,(AX[1]+post[1])/2,0))
cock=beam.union(cylinder(*post,.45,6.1,2.65)).union(cylinder(*AX,1.15,8.35,.4)).cut(cylinder(*AX,.56,8.3,.5))
for name,shape in [('day_pinion',pinion),('day_wheel',wheel),('day_hand',hand),('day_cock',cock),('upper_bridge',upper)]:
 print('writing',name,flush=True);kernel.write_step('work/parts/'+name+'.step',shape)
doc=json.loads(Path('previous/movement.json').read_text())
doc['mobiles']['transfer']['parts'].append('day_pinion')
doc['mobiles']['day']={'axis':list(AX),'parts':['day_wheel','day_hand']}
doc['fixed'].append('day_cock')
doc['meshes'].append({'driver':'transfer','driver_teeth':12,'driven':'day','driven_teeth':144})
doc['hands']['day']={'mobile':'day','part':'day_hand'}
Path('work/movement.json').write_text(json.dumps(doc,indent=2)+'\n')
