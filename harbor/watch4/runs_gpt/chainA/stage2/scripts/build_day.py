import sys,math,json
sys.path.insert(0,'tools')
import cadquery as cq
import kernel
D=(14.4,0); C=(2.,-7.); P=(-11.,-10.)
d=math.dist(D,C); mod=2*d/112
alpha=math.atan2(C[1]-D[1],C[0]-D[0])
def cyl(x,y,z,r,h): return cq.Workplane('XY').workplane(offset=z).center(x,y).circle(r).extrude(h)
def gear(n,phase,xy,z,h):
 rp=mod*n/2; rb=rp*math.cos(math.radians(25)); rr=rp-1.25*mod; ra=rp+mod
 inv=lambda r: math.sqrt(max(0,(r/rb)**2-1))-math.atan(math.sqrt(max(0,(r/rb)**2-1)))
 half=(math.pi*mod/2-.03)/(2*rp); base=half+inv(rp)
 pts=[]
 for k in range(n):
  mid=phase+k*2*math.pi/n
  # root left, radial climb then involute ascending
  if rr<rb: pts.append((rr,mid-base))
  for j in range(11):
   r=max(rb,rr)+(ra-max(rb,rr))*j/10
   pts.append((r,mid-base+inv(r)))
  for j in range(10,-1,-1):
   r=max(rb,rr)+(ra-max(rb,rr))*j/10
   pts.append((r,mid+base-inv(r)))
  if rr<rb: pts.append((rr,mid+base))
 return cq.Workplane('XY').workplane(offset=z).polyline([(xy[0]+r*math.cos(a),xy[1]+r*math.sin(a)) for r,a in pts]).close().extrude(h)
def bar(a,b,z,h,width):
 dx=b[0]-a[0];dy=b[1]-a[1]; L=math.hypot(dx,dy); nx=-dy/L*width/2;ny=dx/L*width/2
 return cq.Workplane('XY').workplane(offset=z).polyline([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]).close().extrude(h)
def save(n,s):
 assert len(s.solids().vals())==1,n
 kernel.write_step('work/parts/'+n+'.step',s)
print('module',mod,'distance',d,flush=True)
save('day_driver16',gear(16,alpha,D,10.4,.6))
save('day_driver_extension',cyl(*D,5.8,.5,5.1))
save('day_wheel96',gear(96,alpha+math.pi-math.pi/96,C,10.4,.6))
save('day_shaft',cyl(*C,9.9,.5,1.75))
hand=cyl(*C,11.,1.,.3).union(bar(C,(C[0]+3.4,C[1]),11.,.3,.55))
save('day_hand',hand)
support=cyl(*P,-.45,.55,12.15)
for z,h in [(9.95,.35),(11.4,.3)]:
 arm=bar(P,C,z,h,.7).union(cyl(*C,z,1.,h)).cut(cyl(*C,z-.01,.62,h+.02))
 support=support.union(arm)
save('day_bridge',support)
cock=cq.importers.importStep('previous/parts/transfer_cock.step')
save('transfer_cock',cock.cut(cyl(*D,5.7,.62,1.1)))
m=json.load(open('previous/movement.json'))
m['mobiles']['transfer']['parts']+=['day_driver16','day_driver_extension']
m['mobiles']['day']={'axis':list(C),'parts':['day_wheel96','day_shaft','day_hand']}
m['fixed'].append('day_bridge')
m['meshes'].append({'driver':'transfer','driver_teeth':16,'driven':'day','driven_teeth':96})
m['hands']['day']={'mobile':'day','part':'day_hand'}
json.dump(m,open('work/movement.json','w'),indent=2)
