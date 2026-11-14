import sys, math,json
sys.path.insert(0,'/app/tools')
import kernel
import cadquery as cq
from pathlib import Path
P=Path('/app/work/parts')
A=(12,0); C=(12,11.2); B=(1.92,11.2)
parts={}; mobiles={}; fixed=[]
def cyl(r,z0,z1,xy,hole=0):
 w=cq.Workplane('XY').workplane(offset=z0).center(*xy).circle(r)
 if hole:w=w.circle(hole)
 return w.extrude(z1-z0)
def gear(n,m,z0,z1,xy,phase=0,bore=0,backlash=.03):
 r=n*m/2; rb=r*math.cos(math.radians(25)); ra=r+m; rf=r-1.25*m
 inv=lambda a: math.tan(a)-a
 half=math.pi/(2*n)-backlash/(2*r)
 ip=inv(math.radians(25))
 # flank angle decreases as radius increases
 pts=[]
 for k in range(n):
  mid=phase+2*math.pi*k/n
  def pt(rad,ang):return (xy[0]+rad*math.cos(mid+ang),xy[1]+rad*math.sin(mid+ang))
  start=max(rf,rb)
  def ang(rad):return half+ip-inv(math.acos(min(1,rb/rad)))
  ar=ang(start)
  pts.append(pt(rf,-ar))
  if start>rf:pts.append(pt(start,-ar))
  for j in range(1,9):
   rad=start+(ra-start)*j/8;pts.append(pt(rad,-ang(rad)))
  at=ang(ra)
  for j in range(1,5):pts.append(pt(ra,-at+2*at*j/4))
  for j in range(1,9):
   rad=ra-(ra-start)*j/8;pts.append(pt(rad,ang(rad)))
  if start>rf:pts.append(pt(rf,ar))
  # root arc connecting next tooth
  end=2*math.pi/n-ar
  for j in range(1,4):pts.append(pt(rf,ar+(end-ar)*j/4))
 w=cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1-z0)
 if bore:w=w.cut(cyl(bore,z0-.1,z1+.1,xy))
 return w

def save(name,w,mobile=None,axis=None):
 print('write',name,flush=True);kernel.write_step(P/(name+'.step'),w)
 parts[name]=w
 if mobile:mobiles.setdefault(mobile,{'axis':list(axis),'parts':[]})['parts'].append(name)
 else:fixed.append(name)

def phase_driven(n,theta,driver_n,driver_phase):
 # n*phase2 = (n+driver_n)*theta+n*pi-pi-driver_n*phase1
 return ((n+driver_n)*theta+n*math.pi-math.pi-driver_n*driver_phase)/n
pA=phase_driven(24,0,96,0)
pM=phase_driven(24,math.pi/2,48,0)
pH=phase_driven(96,math.pi/2,16,0)
pB=phase_driven(12,math.pi,72,0)
pS=phase_driven(12,0,120,0)
# Separate wheel files make later changes possible without replacing all the mobile.
save('transfer_pinion',gear(24,.2,0,1,A,pA).union(cyl(.4,-1.0,6.0,A)).union(cyl(.85,-1,-.7,A)), 'transfer',A)
save('transfer_minute',gear(48,22.4/72,3.7,4.3,A,0), 'transfer',A)
save('transfer_hour',gear(16,.2,5,5.6,A,0),'transfer',A)
save('minute_input',gear(24,22.4/72,3.7,4.3,C,pM,bore=.6).union(cyl(.95,2.6,8.4,C,.6)), 'minute',C)
save('minute_output',gear(72,.24,2.6,3.2,C,0,bore=.6),'minute',C)
save('seconds_transfer_input',gear(12,.24,2.6,3.2,B,pB).union(cyl(.4,1.2,4.65,B)).union(cyl(.85,1.5,1.8,B)).union(cyl(.85,4.05,4.3,B)), 'fast_transfer',B)
save('seconds_transfer_output',gear(120,20.16/132,1.5,2.1,B,0),'fast_transfer',B)
save('seconds_pinion',gear(12,20.16/132,1.5,2.1,C,pS).union(cyl(.5,1.5,9.65,C)).union(cyl(.85,9.1,9.3,C)), 'seconds',C)
save('hour_wheel',gear(96,.2,5,5.6,C,pH,bore=1.05).union(cyl(1.6,5,7.7,C,1.05)), 'hour',C)
for name,mob,r,z,bore in [('hour_hand','hour',6,7.4,1.05),('minute_hand','minute',8,8.1,.6),('seconds_hand','seconds',9.5,8.8,0)]:
 hub=1.6 if mob=='hour' else (.95 if mob=='minute' else .85)
 w=cyl(hub,z,z+.35,C,bore)
 bar=cq.Workplane('XY').workplane(offset=z).center(C[0],C[1]+(r+hub-.2)/2).rect(.65,r-hub+.2).extrude(.35)
 # start rectangle at hub-.2
 w=w.union(bar)
 save(name,w,mob,C)
# plate holes and support structure
centre=(6,5.5)
def plate(z0,z1,holes):
 w=cyl(19.8,z0,z1,centre)
 for xy,r in holes:w=w.cut(cyl(r,z0-.1,z1+.1,xy))
 return w
save('bottom_plate',plate(-1.7,-1.1,[]))
w=plate(1.1,1.4,[((0,0),.56),(A,.46),(B,.46),(C,.56)])
for xy in [(-11,5),(6,-11),(23,0)]:w=w.union(cyl(.7,-1.1,1.1,xy))
save('lower_bridge',w)
w=plate(5.7,6.1,[(A,.46),(C,1.7)])
for xy in [(-11,5),(6,-11),(23,0)]:w=w.union(cyl(.7,4.8,5.7,xy))
save('upper_bridge',w)
w=plate(4.4,4.8,[(A,.46),(B,.46),(C,1.05)])
for xy in [(-11,5),(6,-11),(23,0)]:w=w.union(cyl(.7,1.4,4.4,xy))
save('middle_bridge',w)
# radial arms from C to a post outside gears, rings at intermediate heights.
# support stops with arms going right, away from B and A
post=(23,11.2)
def stop(name,z0,z1,rin,rout):
 w=cyl(rout,z0,z1,C,rin)
 arm=cq.Workplane('XY').workplane(offset=z0).center((C[0]+rout-.2+post[0])/2,C[1]).rect(post[0]-(C[0]+rout-.2),.7).extrude(z1-z0)
 w=w.union(arm).union(cyl(.7,1.4,z1,post))
 save(name,w)
stop('minute_lower_stop',2.2,2.5,1.05,2)
# avoid overlapping support posts: split column segments or use unique post for second
# top seconds bearing supported from top bridge
w=cyl(1.25,9.4,9.8,C,.56)
w=w.union(cq.Workplane('XY').workplane(offset=9.4).center((C[0]+1.1+post[0])/2,C[1]).rect(post[0]-C[0]-1.1,.7).extrude(.4)).union(cyl(.7,6.1,9.8,post))
save('seconds_cock',w)
mov={'case_centre':list(centre),'fixed':fixed,'mobiles':mobiles,'meshes':[{'driver':'barrel','driver_teeth':96,'driven':'transfer','driven_teeth':24},{'driver':'transfer','driver_teeth':48,'driven':'minute','driven_teeth':24},{'driver':'transfer','driver_teeth':16,'driven':'hour','driven_teeth':96},{'driver':'minute','driver_teeth':72,'driven':'fast_transfer','driven_teeth':12},{'driver':'fast_transfer','driver_teeth':120,'driven':'seconds','driven_teeth':12}], 'hands':{n:{'mobile':n,'part':n+'_hand'} for n in ['hour','minute','seconds']}}
Path('/app/work/movement.json').write_text(json.dumps(mov,indent=2))
