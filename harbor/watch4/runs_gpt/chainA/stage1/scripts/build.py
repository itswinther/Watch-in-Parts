import sys,math,json,os
sys.path.insert(0,'/app/tools')
import kernel
import cadquery as cq
from math import sin,cos,pi,sqrt,acos,tan
os.makedirs('work/parts',exist_ok=True)
C=(7.2,0); A=(14.4,0); B=(7.2,6.3)
def cyl(x,y,z,h,r,ri=0):
 w=cq.Workplane('XY').workplane(offset=z).center(x,y).circle(r)
 if ri:w=w.circle(ri)
 return w.extrude(h)
def box(x,y,z,dx,dy,dz):return cq.Workplane('XY').box(dx,dy,dz,centered=(False,False,False)).translate((x,y,z))
def gear(n,m,z,h,xy,phase=0,hole=0):
 rp=n*m/2; rb=rp*cos(25*pi/180); ra=rp+m; rr=rp-1.35*m
 half=(pi*m/2-.025)/(2*rp); inv=tan(25*pi/180)-25*pi/180
 pts=[]
 for i in range(n):
  t=2*pi*i/n+phase
  # tooth counterclockwise, left flank root to tip then right flank tip to root
  rr0=max(rr,rb)
  radii=([rr] if rr<rb else [])+[rr0+(ra-rr0)*j/9 for j in range(10)]
  for r in radii:
   a=half+inv-(tan(acos(rb/r))-acos(rb/r) if r>=rb else 0)
   pts.append((xy[0]+r*cos(t-a),xy[1]+r*sin(t-a)))
  for r in reversed(radii):
   a=half+inv-(tan(acos(rb/r))-acos(rb/r) if r>=rb else 0)
   pts.append((xy[0]+r*cos(t+a),xy[1]+r*sin(t+a)))
 w=cq.Workplane('XY').workplane(offset=z).polyline(pts).close().extrude(h)
 if hole:w=w.cut(cyl(*xy,z-.1,h+.2,hole))
 return w
parts={}; mobs={}; fixed=[]
def save(n,w):
 kernel.write_step('work/parts/'+n+'.step',w); parts[n]=w
 print('wrote',n,flush=True)
def mob(n,xy,items):
 mobs[n]={'axis':list(xy),'parts':list(items)}
 for k,v in items.items():save(k,v)
mob('transfer',A,{'transfer_shaft':cyl(*A,-1,7.1,.5), 'barrel_pinion48':gear(48,.2,0,1,A,pi/48), 'minute_driver96':gear(96,.12,2.7,.6,A), 'hour_driver16':gear(16,.225,5,.7,A)})
mob('hour',C,{'hour_wheel48':gear(48,.225,5,.7,C,pi/48,1.4),'hour_sleeve':cyl(*C,4.95,2.25,1.9,1.4),'hour_hand':cyl(*C,6.9,.3,2.1,1.4).union(box(C[0]+1.5,-.4,6.9,3.8,.8,.3))})
mob('minute',C,{'minute_wheel24':gear(24,.12,2.7,.6,C,pi/24,.8),'minute_sleeve':cyl(*C,2.7,5.7,1.25,.8),'seconds_driver80':gear(80,.14,3.8,.7,C,0,.8),'minute_hand':cyl(*C,8,.4,1.45,.8).union(box(C[0]+1,-.3,8,4.6,.6,.4))})
mob('seconds_transfer',B,{'seconds_transfer_shaft':cyl(*B,1.5,4.6,.5),'seconds_pinion10':gear(10,.14,3.8,.7,B),'seconds_driver75':gear(75,12.6/85,1.5,.7,B,-pi/2)})
mob('seconds',C,{'seconds_shaft':cyl(*C,1.5,8.4,.55),'seconds_wheel10':gear(10,12.6/85,1.5,.7,C),'seconds_hand':cyl(*C,9.3,.4,.9).union(box(C[0]+.5,-.2,9.3,5.8,.4,.4))})
# Separate removable caps, supported by individual columns on the main plate.
base=cyl(5,0,-1.7,.6,19)
for xy,r in [((0,0),.6),(A,.6)]:
 base=base.union(cyl(*xy,-1.1,.65,r+.5).cut(cyl(*xy,-1.1,.8,r)))
def arm(xy,end,z,h=.35):
 x,y=xy; ex,ey=end; length=math.hypot(ex-x,ey-y); angle=math.degrees(math.atan2(ey-y,ex-x))
 return box(0,-.45,z,length,.9,h).rotate((0,0,0),(0,0,1),angle).translate((x,y,0))
def cap(name,xy,end,z,ro,ri=0,h=.35,low=None,bore_floor=None):
 global base
 # column touches the underside of its removable bridge.
 save(name+'_pillar',cyl(*end,-1.1,z+1.1,.65));fixed.append(name+'_pillar')
 w=arm(xy,end,z,h).union(cyl(*xy,z if low is None else low,h if low is None else z+h-low,ro))
 if ri:w=w.cut(cyl(*xy,(z if bore_floor is None else bore_floor)-.00001,h+2,ri))
 save(name,w);fixed.append(name)
cap('barrel_cock',(0,0),(-8,-10),1.7,1.1,.6,low=1.15,bore_floor=1.14)
# Restore blind barrel roof after the bearing bore cut.
w=parts['barrel_cock'].union(cyl(0,0,1.7,.35,1.1));save('barrel_cock',w)
cap('seconds_lower_stop',C,(1,-17),1.1,1.05,.65,h=.3)
cap('minute_lower_stop',C,(3,-17),2.3,1.4,.7,h=.3)
cap('hour_lower_stop',C,(5,-17),4.6,2.1,1.3,h=.25)
cap('hour_upper_stop',C,(8,-17),7.3,2.1,1.3)
cap('transfer_cock',A,(20,-8),6.2,1,.6,low=5.85,bore_floor=5.84)
save('transfer_cock',parts['transfer_cock'].union(cyl(*A,6.2,.35,1)))
cap('seconds_transfer_lower',B,(15,14),1.1,1,.6,h=.3)
cap('seconds_transfer_cock',B,(17,12),6.2,1,.6,low=5.85,bore_floor=5.84)
save('seconds_transfer_cock',parts['seconds_transfer_cock'].union(cyl(*B,6.2,.35,1)))
cap('minute_upper_stop',C,(11,-16),8.5,1.45,.7)
cap('seconds_cock',C,(14,-14),10.0,1.05,.65,low=9.8,bore_floor=9.79)
save('seconds_cock',parts['seconds_cock'].union(cyl(*C,10,.35,1.05)))
save('main_plate',base);fixed.insert(0,'main_plate')
doc={'case_centre':[5,0],'fixed':fixed,'mobiles':mobs,'meshes':[{'driver':a,'driver_teeth':n,'driven':b,'driven_teeth':k} for a,n,b,k in [('barrel',96,'transfer',48),('transfer',96,'minute',24),('transfer',16,'hour',48),('minute',80,'seconds_transfer',10),('seconds_transfer',75,'seconds',10)]],'hands':{n:{'mobile':n,'part':n+'_hand'} for n in ['hour','minute','seconds']}}
with open('work/movement.json','w') as f:json.dump(doc,f,indent=2)
