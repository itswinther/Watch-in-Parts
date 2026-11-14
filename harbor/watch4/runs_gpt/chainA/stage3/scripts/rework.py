import sys,math,json
sys.path.insert(0,'/app/tools')
import cadquery as cq
from kernel import write_step
from math import sin,cos,atan,tan,sqrt,pi
m=json.load(open('previous/movement.json'))
A=(5.4,sqrt(14.4**2-5.4**2)); B=(14.4,8.4); T=(14.4,0)
D=math.dist(A,B); mod=2*D/75
print('axes',A,B,'module',mod,flush=True)
def cyl(p,r,z,h):return cq.Workplane('XY').workplane(offset=z).center(*p).circle(r).extrude(h)
def gear(n,mod,p,z,h,phase=0):
 r=n*mod/2; rb=r*cos(math.radians(25)); ra=r+mod; rf=r-1.25*mod
 half=(pi*mod/2-.03)/(2*r); invp=tan(math.radians(25))-math.radians(25)
 def off(rad):
  a=math.acos(min(1,rb/rad)); return half+invp-(tan(a)-a)
 points=[]
 for i in range(n):
  c=phase+2*pi*i/n
  seq=[(rf,-pi/n),(rf,-off(max(rf,rb)))]
  for j in range(9):
   rad=max(rf,rb)+(ra-max(rf,rb))*j/8; seq.append((rad,-off(rad)))
  for j in range(1,5):seq.append((ra,-off(ra)+2*off(ra)*j/4))
  for j in range(1,9):
   rad=ra-(ra-max(rf,rb))*j/8;seq.append((rad,off(rad)))
  seq.extend([(rf,off(max(rf,rb))),(rf,pi/n)])
  for rad,a in seq:
   q=(p[0]+rad*cos(c+a),p[1]+rad*sin(c+a))
   if not points or math.dist(q,points[-1])>1e-8:points.append(q)
 if math.dist(points[0],points[-1])<1e-8:points.pop()
 return cq.Workplane('XY').workplane(offset=z).polyline(points).close().extrude(h)
def phase_driven(n1,p1,ph1,n2,p2):
 a=math.atan2(p2[1]-p1[1],p2[0]-p1[0]);return a+pi+(pi-n1*(ph1-a))/n2
pa=phase_driven(96,(0,0),0,48,A)
# arbitrary compound phase, then phase conjugates for next meshes
p27=0;pb=phase_driven(27,A,p27,48,B)
p48=0;pt=phase_driven(48,B,p48,36,T)
parts={}
parts['input_relay']=gear(48,.2,A,0,1,pa).union(gear(27,mod,A,-.35,.3,p27)).union(cyl(A,.5,-1,2.45))
parts['output_relay']=gear(48,mod,B,-.35,.3,pb).union(gear(48,.2,B,0,1,p48)).union(cyl(B,.5,-1,2.45))
parts['transfer_pinion36']=gear(36,.2,T,0,1,pt)
import shutil
shutil.copyfile('previous/parts/main_plate.step','work/parts/main_plate.step')
parts['input_bearing']=cyl(A,1.3,-1.1,.65).cut(cyl(A,.6,-1.2,.9))
parts['output_bearing']=cyl(B,1.3,-1.1,.65).cut(cyl(B,.6,-1.2,.9))
# independent cocks with a pillar extending outward from each axis
for name,p,ang in [('input_cock',A,pi),('output_cock',B,0)]:
 q=(p[0]+7.6*cos(ang),p[1]+7.6*sin(ang));mid=((p[0]+q[0])/2,(p[1]+q[1])/2)
 arm=cq.Workplane('XY').box(7.6,1.0,.4).translate((*mid,1.3)).rotate((*mid,0),(*mid,1),math.degrees(ang))
 s=cyl(p,1.1,1.1,.4).union(arm).union(cyl(q,.6,-.45,1.95)).cut(cyl(p,.6,1,1))
 parts[name]=s
# Reroute two existing supports around the new lower wheel.
def beam(p,q,z,h,w):
 mid=((p[0]+q[0])/2,(p[1]+q[1])/2)
 return cq.Workplane('XY').box(math.dist(p,q),w,h).translate((*mid,z+h/2)).rotate((*mid,0),(*mid,1),math.degrees(math.atan2(q[1]-p[1],q[0]-p[0])))
p=(15,14);q=(15,16.3)
parts['seconds_transfer_lower_pillar']=cyl(q,.6,-.45,1.55).union(beam(p,q,.75,.35,1.0)).union(cyl(p,.5,.75,.35))
p=(17,12);q=(20.4,12.8)
parts['seconds_transfer_cock_pillar']=cyl(q,.4,-.45,3.05).union(beam(p,q,2.3,.3,.8)).union(cyl(p,.65,2.3,3.9))
for n,s in parts.items():
 print('write',n,len(s.solids().vals()),flush=True);write_step('work/parts/'+n+'.step',s)
m['mobiles']['transfer']['parts'].remove('barrel_pinion48');m['mobiles']['transfer']['parts'].append('transfer_pinion36')
m['mobiles']['input_relay']={'axis':A,'parts':['input_relay']}
m['mobiles']['output_relay']={'axis':B,'parts':['output_relay']}
m['fixed']+=['input_cock','output_cock','input_bearing','output_bearing']
m['meshes']= [{'driver':'barrel','driver_teeth':96,'driven':'input_relay','driven_teeth':48},{'driver':'input_relay','driver_teeth':27,'driven':'output_relay','driven_teeth':48},{'driver':'output_relay','driver_teeth':48,'driven':'transfer','driven_teeth':36}]+m['meshes'][1:]
json.dump(m,open('work/movement.json','w'),indent=2)
