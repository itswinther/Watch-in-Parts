import cadquery as cq, math,json,os,sys
from pathlib import Path
ROOT=Path('/app/delivery'); parts={}; axes={}
C=(2.8,0); A=(10.8,0); M=C; T=(2.8,6.6); S=(8.25,6.6-math.sqrt(5.6**2-5.45**2)); H=(-3.2,0); I=(2.8,-3.6); D=(2.8,-7.2)
def cyl(p,r,z,h): return cq.Workplane('XY').workplane(offset=z).center(*p).circle(r).extrude(h)
def ring(p,ro,ri,z,h): return cq.Workplane('XY').workplane(offset=z).center(*p).circle(ro).circle(ri).extrude(h)
def bar(p,q,w,z,h):
 dx=q[0]-p[0];dy=q[1]-p[1]; n=math.hypot(dx,dy); nx=-dy/n*w/2;ny=dx/n*w/2
 return cq.Workplane('XY').workplane(offset=z).polyline([(p[0]+nx,p[1]+ny),(q[0]+nx,q[1]+ny),(q[0]-nx,q[1]-ny),(p[0]-nx,p[1]-ny)]).close().extrude(h).union(cyl(p,w/2,z,h)).union(cyl(q,w/2,z,h))
def save(name,sh):
 sh=sh.clean();assert len(sh.solids().vals())==1,name; assert sh.val().isValid(),name
 cq.exporters.export(sh,str(ROOT/'parts'/f'{name}.step')); parts[name]=sh
 print(name,round(sh.val().Volume(),3),flush=True)
def gear(p,n,m,z,b,phase=0,bore=0):
 # Sample the analytical 25 degree involute; root joins below base circle.
 rp=n*m/2; rb=rp*math.cos(math.radians(25)); ra=rp+m; rf=max(rp-1.25*m,.25)
 inv=lambda r: math.sqrt(max(0,(r/rb)**2-1))-math.acos(min(1,rb/r)) if r>rb else 0
 half=math.pi/(2*n)-.01/rp # 0.02 mm total circular backlash
 def ang(r):return half+inv(rp)-inv(r)
 pts=[]
 for k in range(n):
  mid=phase+2*math.pi*k/n; lo=max(rf,rb)
  seq=[(rf,-ang(lo))]+[(r,-ang(r)) for r in [lo+(ra-lo)*j/8 for j in range(9)]]
  seq += [(ra,ang(ra))]+[(r,ang(r)) for r in [ra-(ra-lo)*j/8 for j in range(1,9)]]+[(rf,ang(lo))]
  seq += [(rf,ang(lo)+(2*math.pi/n-2*ang(lo))*j/4) for j in range(1,4)]
  pts.extend([(p[0]+r*math.cos(mid+a),p[1]+r*math.sin(mid+a)) for r,a in seq])
 pts=[v for j,v in enumerate(pts) if j==0 or math.dist(v,pts[j-1])>1e-8]
 sh=cq.Workplane('XY').workplane(offset=z).polyline(pts).close().extrude(b)
 if bore:sh=sh.cut(cyl(p,bore,z-.01,b+.02))
 return sh
def toward(p,q):return math.atan2(q[1]-p[1],q[0]-p[0])
def pair(p,q,n1,n2,m,z,b,bore1=0,bore2=0):
 a=toward(p,q); return gear(p,n1,m,z,b,a,bore1),gear(q,n2,m,z,b,a+math.pi+math.pi/n2,bore2)
def spindle(p,z0=-.65,z1=10.2,r=.3,lower=True,upper=True):
 sh=cyl(p,r,z0,z1-z0)
 if lower:sh=sh.union(cyl(p,.65,-.3,.2))
 if upper:sh=sh.union(cyl(p,max(.65,r+.25),9.8,.2))
 return sh
# Main plate with pillars. All bearing running clearances exceed print tolerances.
base=cyl(C,12.65,-.4545,.4)
for p,r in [((0,0),.54),(A,.54),(M,.46),(T,.39),(S,.34)]:base=base.cut(cyl(p,r,-.5,.5))
pillars=[(-5.2,-9),(-5.2,9),(10.8,-9),(10.8,9)]
for p in pillars:base=base.union(cyl(p,.4,-.0545,10.1045))
save('mainplate',base)
dial=cyl(C,12.65,10.05,.4)
for p,r in [(M,1.14),(S,.34),(D,1.04)]:dial=dial.cut(cyl(p,r,10.0,.5))
for p,r in [(A,.54),(T,.39),(H,.74),(I,.74)]:dial=dial.cut(cyl(p,r,10.0,.25))
save('closed_dial',dial)
trainplate=cyl(C,12.65,.5,1.6)
for p,r in [((0,0),1.04),(A,1.5),(M,.46),(T,.39),(S,.34)]:trainplate=trainplate.cut(cyl(p,r,.49,1.62))
for p in pillars:trainplate=trainplate.cut(cyl(p,.4,.49,1.62))
save('train_plate',trainplate)
def support(name,p,target,z,ri):
 sh=bar(p,target,.7,z,.25).union(cyl(p,max(.9,ri+.35),z,.25)).cut(cyl(p,ri,z-.01,.27)).cut(cyl(target,.4,z-.01,.27))
 if name=='motion_bridge':sh=sh.cut(parts['barrel_bridge'])
 save(name,sh)
support('barrel_bridge',(0,0),pillars[0],2.35,.54)
support('motion_bridge',H,pillars[0],3.95,.74)
support('day_idler_bridge',I,pillars[2],5.55,.74)
support('day_bridge',D,pillars[0],6.9,1.04)
# Compound wheels, separate hand pointers.
for variant in [False,True]:
 suf='_6h' if variant else ''
 f=spindle(A,z0=-.35,r=.5,lower=False).union(gear(A,12,.2,0,.4545,math.pi+math.pi/12))
 n=30 if variant else 40; mod=8/(.5*(n+40))
 w1,w2=pair(A,M,n,40,mod,2.65,.4)
 save('first'+suf,f.union(w1))
 minute=spindle(M,z0=.55,z1=11.25,r=.42,lower=False,upper=False).union(w2)
 mw,tw=pair(M,T,80,8,.15,3.2,.4)
 minute=minute.union(mw).union(cyl(M,.65,2.2,.2)).union(cyl(M,.65,4.6,.15))
 drive,hi=pair(M,H,12,36,.25,4.3,.4)
 minute=minute.union(drive).union(cyl(M,.25,11.25,.25))
 save('minute'+suf,minute)
 if not variant:
  tt,ss=pair(T,S,48,8,.2,3.75,.4)
  save('seconds_intermediate',spindle(T,z0=.55,r=.35,lower=False).union(cyl(T,.65,2.2,.2)).union(tw).union(tt))
  sec=spindle(S,z0=.55,z1=10.9,lower=False).union(cyl(S,.65,2.2,.2)).union(ss).union(cyl(S,.22,10.9,.25));save('seconds_arbor',sec)
  hi2,hw=pair(H,M,12,48,.2,4.85,.6,bore2=.48)
  hs=spindle(H,4.0,10.2,r=.7,lower=False).union(cyl(H,.95,4.25,.2)).union(hi).union(hi2)
  save('motion_intermediate',hs)
  hd,ii=pair(M,I,12,12,.3,5.95,1.1,bore1=.48)
  hour=ring(M,1.1,.48,4.85,5.7).union(hw).union(hd).union(ring(M,1.4,.48,9.8,.2))
  save('hour_sleeve',hour.union(ring(M,.95,.48,10.55,.25)))
  ii2,dd=pair(I,D,12,24,.2,7.2,2.4)
  ids=spindle(I,5.6,10.2,r=.7,lower=False).union(cyl(I,.95,5.85,.2)).union(ii).union(ii2)
  save('day_intermediate',ids)
  ds=spindle(D,6.95,10.9,r=1.0,lower=False).union(dd).union(cyl(D,.8,10.9,.25));save('day_arbor',ds)
def hand(name,p,length,ri,ro,z,h,angle):
 # Parallel sided pointer and annular hub, with a print-friendly rounded end.
 end=(p[0]+(length-.2)*math.cos(angle),p[1]+(length-.2)*math.sin(angle))
 sh=bar(p,end,.4,z,h).union(cyl(p,ro,z,h)).cut(cyl(p,ri,z-.01,h+.02));save(name,sh)
hand('hour_hand',M,5.5,.95,1.35,10.55,.25,0)
hand('minute_hand',M,6.3,.25,.85,11.25,.25,math.pi/2)
hand('seconds_hand',S,5,.22,.65,10.9,.25,-math.pi/2)
hand('day_hand',D,3.2,.8,1.3,10.9,.25,0)
fixed=['mainplate','train_plate','barrel_bridge','motion_bridge','day_idler_bridge','day_bridge','closed_dial']
mobiledef={'first':(A,['first']),'minute':(M,['minute','minute_hand']),'seconds_intermediate':(T,['seconds_intermediate']),'seconds':(S,['seconds_arbor','seconds_hand']),'motion_intermediate':(H,['motion_intermediate']),'hour':(M,['hour_sleeve','hour_hand']),'day_intermediate':(I,['day_intermediate']),'day':(D,['day_arbor','day_hand'])}
for variant in [False,True]:
 mobiles={}
 for name,(pos,ps) in mobiledef.items():
  ps=[s+'_6h' if variant and s in ['first','minute'] else s for s in ps]
  mobiles[name]={'axis':list(pos),'parts':ps,'material':'AD-C100-HT'}
 ms=[('barrel',96,'first',12),('first',30 if variant else 40,'minute',40),('minute',80,'seconds_intermediate',8),('seconds_intermediate',48,'seconds',8),('minute',12,'motion_intermediate',36),('motion_intermediate',12,'hour',48),('hour',12,'day_intermediate',12),('day_intermediate',12,'day',24)]
 doc={'barrel':'BR-096-30','case_centre':C,'fixed':fixed,'mobiles':mobiles,'meshes':[dict(driver=a,driver_teeth=b,driven=c,driven_teeth=d) for a,b,c,d in ms],'hands':{h:{'mobile':mob,'part':part} for h,mob,part in [('hour','hour','hour_hand'),('minute','minute','minute_hand'),('seconds','seconds','seconds_hand'),('day','day','day_hand')]}}
 (ROOT/('variant_6h.json' if variant else 'movement.json')).write_text(json.dumps(doc,indent=2))
order=['mainplate','barrel','train_plate','barrel_bridge','first','minute','seconds_intermediate','seconds_arbor','motion_bridge','motion_intermediate','hour_sleeve','day_idler_bridge','day_intermediate','day_bridge','day_arbor','closed_dial','hour_hand','seconds_hand','day_hand','minute_hand']
paths={}
for name in order:
 # A uniform 25 mm approach in <=0.2 mm increments.
 paths[name]=[[[1,0,0,0],[0,1,0,0],[0,0,1,float(t)],[0,0,0,1]] for t in [25*(1-i/130) for i in range(131)]]
(ROOT/'assembly.json').write_text(json.dumps({'order':order,'paths':paths}))
(ROOT/'report.json').write_text(json.dumps({'parts':{x:'not_tested' for x in ['P1','P2','P3','P4']},'height_mm':11.9545},indent=2))
