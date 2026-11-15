import os,sys,math,json
import numpy as np
import cadquery as cq
import manifold3d as md
sys.path.insert(0,'/app/tools')
from kernel import write_step
OUT='/app/delivery'
C=np.array([2.8,0.]); axes={'input':np.array([10.8,0]),'minute':C,'s1':C+[-5.4,0],'s2':C+[-5.4,-5.3],'s3':C+[-.6,-5.3],'seconds':C+[3.4,-5.3],'motion':C+[0,5.6],'hour':C,'dayidler':C+3.6*np.array([-2**-.5,2**-.5]),'day':C+3.6*np.array([-2**-.5,2**-.5])+5.25*np.array([math.cos(math.radians(160)),math.sin(math.radians(160))])}
parts={}; bounds={}
def cyl(r,z,h,xy):return cq.Workplane('XY').workplane(offset=z).center(*xy).circle(r).extrude(h)
def ann(ro,ri,z,h,xy):return cq.Workplane('XY').workplane(offset=z).center(*xy).circle(ro).circle(ri).extrude(h)
def save(name,s):
 s=s.clean(); assert len(s.solids().vals())==1,(name,len(s.solids().vals())); assert s.val().isValid(),name
 write_step(f'{OUT}/parts/{name}.step',s)
 parts[name]=s; b=s.val().BoundingBox();bounds[name]=[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]
 print(name,round(s.val().Volume(),3),flush=True)
cache={}
def gearpoints(n,m):
 key=(n,m)
 if key in cache:return cache[key]
 rp=n*m/2;ra=rp+m;rf=rp-1.25*m;a=math.radians(25);rb=rp*math.cos(a)
 if n<13:
  w=math.pi*m/2+.03; tip=w/2-1.25*m*math.tan(a);rr=min(.318*m,tip/(1/math.cos(a)-math.tan(a))*.99)
  cx=tip-rr*(1/math.cos(a)-math.tan(a));cy=rp-1.25*m+rr
  right=[(cx+rr*math.cos(t),cy+rr*math.sin(t)) for t in np.linspace(-math.pi/2,-a,9)]
  top=rp+2*m;xt=w/2+2*m*math.tan(a)
  poly=[(-xt,top)]+[(-x,y) for x,y in right[::-1]]+right+[(xt,top)]
  cutter=md.CrossSection([poly]); cuts=[]
  for th in np.arange(-1.4,1.401,.006):cuts.append(cutter.translate([-rp*th,0]).rotate(-math.degrees(th)))
  notch=md.CrossSection.batch_boolean(cuts,md.OpType.Add)
  cutters=[notch.rotate(360*k/n+180/n-90) for k in range(n)]
  body=md.CrossSection.circle(ra,360)-md.CrossSection.batch_boolean(cutters,md.OpType.Add)
  pts=np.array(body.simplify(.0006).to_polygons()[0]);
 else:
  half=(math.pi*m/2-.03)/(2*rp);inv=lambda r: math.tan(math.acos(rb/r))-math.acos(rb/r)
  ip=inv(rp);pts=[]
  rstart=max(rf,rb)
  for k in range(n):
   mid=2*math.pi*k/n
   # from lower root to lower flank, around tip, down upper flank
   h0=half+ip-(inv(rstart) if rstart>=rb else 0)
   pts.append((rf*math.cos(mid-h0),rf*math.sin(mid-h0)))
   for r in np.linspace(rstart,ra,9):
    h=half+ip-inv(r);pts.append((r*math.cos(mid-h),r*math.sin(mid-h)))
   ht=half+ip-inv(ra)
   for t in np.linspace(mid-ht,mid+ht,4)[1:]:pts.append((ra*math.cos(t),ra*math.sin(t)))
   for r in np.linspace(ra,rstart,9)[1:]:
    h=half+ip-inv(r);pts.append((r*math.cos(mid+h),r*math.sin(mid+h)))
   pts.append((rf*math.cos(mid+h0),rf*math.sin(mid+h0)))
   nxt=mid+2*math.pi/n-h0
   for t in np.linspace(mid+h0,nxt,4)[1:]:pts.append((rf*math.cos(t),rf*math.sin(t)))
  pts=np.array(pts)
 pts=np.array([p for i,p in enumerate(pts) if np.linalg.norm(p-pts[i-1])>1e-7])
 cache[key]=pts;return pts

def gear(n,m,z,xy,phase=0,h=.4,bore=0):
 pts=gearpoints(n,m);rot=np.array([[math.cos(phase),-math.sin(phase)],[math.sin(phase),math.cos(phase)]])
 pp=pts@rot.T+xy
 s=cq.Workplane('XY').workplane(offset=z).polyline(pp.tolist()).close().extrude(h)
 if bore:s=s.cut(cyl(bore,z-.01,h+.02,xy))
 return s

def stem(axis,lo=.75,hi=8.65,r=.3):
 xy=axes[axis];s=cyl(r,lo,hi-lo,xy)
 if lo<1:s=s.union(cyl(.6,1.,.25,xy))
 
 if axis!='minute':s=s.union(cyl(.6,8.2,.2,xy))
 return s

# Lower tray, four frame columns, and barrel's blind lower bearing.
base=cyl(12.5,-.95,.7,C)
base=base.cut(cyl(.54,-.5,.3,[0,0]))
base=base.cut(cyl(.34,-.75,.6,axes['input']))
posts=[C+12*np.array([math.cos(t),math.sin(t)]) for t in np.radians([45,135,235,315])]
for p in posts:base=base.union(cyl(.35,-.25,.75,p))
save('base',base)
# Intermediate plate includes the upper barrel end bearing, relieved for its square.
bridge=cyl(12.5,.5,.45,C).cut(cyl(1.05,.49,2.0,[0,0]))
bridge=bridge.union(ann(1.3,1.05,.95,1.35,[0,0]))
cap=cyl(1.3,2.3,.55,[0,0]).cut(cyl(.54,2.29,.31,[0,0]))
bridge=bridge.union(cap).cut(cyl(.65,.49,.48,axes['input']))
for k in ['minute','s1','s2','s3','seconds','motion']:
 bridge=bridge.cut(cyl(.49 if k=='minute' else (.54 if k=='motion' else .34),.7,.27,axes[k]))
save('lower_bridge',bridge)
# Covering dial and its four pillars: journal holes are the only dial apertures.
dial=cyl(12.65,8.45,.5,C)
for p in posts:dial=dial.union(cyl(.35,.95,7.5,p))
for k in ['input','s1','s2','s3','motion']:
 dial=dial.cut(cyl(.54 if k=='motion' else .34,8.44,.26,axes[k]))
for k,r in [('hour',.76),('seconds',.34),('day',.69),('dayidler',.79)]:dial=dial.cut(cyl(r,8.44,.53,axes[k]))
save('dial',dial)

# Independent wheels slide onto stepped shafts, allowing assembly by gear level.
def sleeve(name,z0,z1,r=.55,bore=.3):
 save(name,ann(r,bore,z0,z1-z0,axes[name.split('_')[0]]))
inputstem=stem('input',-.7,8.65).union(gear(12,.2,0,axes['input'],math.pi/12,h=.4545)).union(cyl(.6,2.7,.2,axes['input']))
# Remove the integral upper collar; its separate sleeve is installed after the wheels.
inputstem=inputstem.cut(ann(.61,.3,8.19,.22,axes['input']))
save('input_pinion',inputstem)
save('input_sleeve',ann(.55,.3,3.2,8.4-3.2,axes['input']))
minute_shaft=cyl(.45,.75,2.9-.75,C).union(cyl(.4,2.9,.35,C)).union(cyl(.35,3.25,1.8,C)).union(cyl(.3,5.05,9.95-5.05,C)).union(cyl(.6,1,.25,C))
save('minute_shaft',minute_shaft)
for tag,dn,cn in [('8h',28,28),('6h',24,32)]:
 save('transfer_'+tag,gear(dn,2/7,2.9,axes['input'],0,h=.3,bore=.3))
 save('minute_'+tag,gear(cn,2/7,2.9,C,math.pi/cn,h=.3,bore=.4))
save('minute_seconds_wheel',gear(24,.3375,3.25,C,0,bore=.35))
save('minute_motion_pinion',gear(12,5.6/24,5.05,C,0,bore=.3))
save('minute_hour_seat',ann(.6,.3,5.45,.25,C))
for name,lower,upper in [
 ('s1',(8,.3375,3.25,math.pi/8),(32,.265,3.7,-math.pi/2)),
 ('s2',(8,.265,3.7,math.pi/2-math.pi/8),(40,.2,4.15,0)),
 ('s3',(8,.2,4.15,math.pi-math.pi/8),(16,.25,4.6,0)),
 ('motion',(36,5.6/24,5.05,-math.pi/2-math.pi/36),(12,5.6/30,5.75,-math.pi/2))]:
 n,m,z,ph=lower; un,um,uz,uph=upper
 sr=.5 if name=='motion' else .3
 sh=stem(name,.75,8.65,sr).cut(ann(.61,sr,8.19,.22,axes[name]))
 sh=sh.union(gear(n,m,z,axes[name],ph)).union(cyl(sr+.2,uz-.2,.2,axes[name]))
 save(name,sh)
 width=.6 if name=='motion' else .4
 save(name+'_upper',gear(un,um,uz,axes[name],uph,h=width,bore=sr))
 save(name+'_sleeve',ann(sr+.25,sr,uz+width,8.4-uz-width,axes[name]))
save('seconds',stem('seconds',.75,10.45).union(gear(16,.25,4.6,axes['seconds'],math.pi-math.pi/16)))
hour=ann(.7,.36,5.75,9.45-5.75,C).union(gear(48,5.6/30,5.75,C,math.pi/2-math.pi/48,h=.6,bore=.36)).union(gear(12,.3,6.4,C,3*math.pi/4,h=.8,bore=.36)).union(ann(1.,.36,8.2,.2,C))
save('hour',hour)
for k,z,n,m,phase,width in [('dayidler',6.4,12,.3,3*math.pi/4+math.pi-math.pi/12,.8),('day',7.25,20,.35,math.radians(160)+math.pi-math.pi/20,.9)]:
 hi=9.15 if k=='dayidler' else 10.95
 sr=.7 if k=='dayidler' else .6
 sh=cyl(sr,z,hi-z,axes[k]).union(cyl(sr+.05,z,9.0-z,axes[k])).union(cyl(sr+.35,8.2,.2,axes[k])).union(gear(n,m,z,axes[k],phase,h=width))
 if k=='dayidler':sh=sh.union(gear(10,.35,7.25,axes[k],math.radians(160),h=.9))
 save(k,sh)
 save(k+'_collar',ann(sr+.35,sr,9.0,.25,axes[k]))

# Pointers are standalone blind-bored parts, seated against the ends of their arbors.
for k,z,r,L,ang in [('hour',9.3,.7,5.5,math.pi/2),('minute',9.8,.3,6.5,math.pi/2),('seconds',10.3,.3,5.2,math.pi/2),('day',10.8,.6,3.2,math.pi/2)]:
 xy=axes[k];hub=max(r+.3,.7)
 s=cyl(hub,z,.35,xy)
 pointer=cq.Workplane('XY').workplane(offset=z).polyline([(0,-.3),(L-.35,-.23),(L,0),(L-.35,.23),(0,.3)]).close().extrude(.35)
 pointer=pointer.rotate((0,0,0),(0,0,1),math.degrees(ang)).translate((float(xy[0]),float(xy[1]),0))
 s=s.union(pointer).cut(cyl(r,z-.01,.16,xy))
 if k=='hour':s=s.cut(cyl(.36,z-.01,.38,xy))
 save(k+'_hand',s)

fixed=['base','lower_bridge','dial']
def build(tag):
 mob={}
 def add(k,ps):mob[k]={'axis':axes[k].tolist(),'parts':ps,'material':'AD-C100-HT'}
 add('input',['input_pinion','transfer_'+tag,'input_sleeve']);add('minute',['minute_shaft','minute_'+tag,'minute_seconds_wheel','minute_motion_pinion','minute_hour_seat','minute_hand'])
 for k in ['s1','s2','s3','motion']:add(k,[k,k+'_upper',k+'_sleeve'])
 for k in ['seconds','hour']:add(k,[k,k+'_hand'])
 add('dayidler',['dayidler','dayidler_collar']);add('day',['day','day_collar','day_hand'])
 mesh=[]
 for a,na,b,nb in [('barrel',96,'input',12),('input',28 if tag=='8h' else 24,'minute',28 if tag=='8h' else 32),('minute',24,'s1',8),('s1',32,'s2',8),('s2',40,'s3',8),('s3',16,'seconds',16),('minute',12,'motion',36),('motion',12,'hour',48),('hour',12,'dayidler',12),('dayidler',10,'day',20)]:mesh.append(dict(driver=a,driver_teeth=na,driven=b,driven_teeth=nb))
 return dict(barrel='BR-096-30',case_centre=C.tolist(),fixed=fixed,mobiles=mob,meshes=mesh,hands={k:dict(mobile=k,part=k+'_hand') for k in ['hour','minute','seconds','day']})
for tag,file in [('8h','movement.json'),('6h','variant_6h.json')]:json.dump(build(tag),open(OUT+'/'+file,'w'),indent=2)
order=['base','barrel','input_pinion','lower_bridge','minute_shaft','transfer_8h','minute_8h','minute_seconds_wheel','s1','s1_upper','s2','s2_upper','s3','s3_upper','seconds','minute_motion_pinion','motion','minute_hour_seat','motion_upper','hour','dayidler','day','input_sleeve','s1_sleeve','s2_sleeve','s3_sleeve','motion_sleeve','dial','dayidler_collar','day_collar','hour_hand','minute_hand','seconds_hand','day_hand']
paths={}
for name in order:
 # Approach from above, except the first tray (empty workspace).
 poses=[]
 for dz in np.linspace(25,0,251):poses.append([[1,0,0,0],[0,1,0,0],[0,0,1,float(dz)],[0,0,0,1]])
 paths[name]=poses
json.dump(dict(order=order,paths=paths),open(OUT+'/assembly.json','w'))
json.dump(bounds,open('/app/bounds.json','w'))
json.dump({'parts':{k:'not_tested' for k in ['P1','P2','P3','P4']},'height_mm':12.1},open(OUT+'/report.json','w'),indent=2)
