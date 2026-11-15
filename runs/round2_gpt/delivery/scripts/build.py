import cadquery as cq, math, json, os
from pathlib import Path
P=Path('/app/delivery'); shapes={}
def cyl(r,z,h,x=0,y=0):return cq.Workplane('XY').workplane(offset=z).center(x,y).circle(r).extrude(h).val()
def box(s,z,h,x=0,y=0):return cq.Workplane('XY').workplane(offset=z).center(x,y).rect(s,s).extrude(h).val()
def union(ss):
 s=ss[0]
 for t in ss[1:]:s=s.fuse(t)
 return s.clean()
def save(n,s):
 s=s.clean();assert len(s.Solids())==1 and s.isValid(),n
 cq.exporters.export(s,str(P/'parts'/f'{n}.step'));shapes[n]=s
 print(n,round(s.Volume(),3),flush=True)
def gear(n,m,z,h,ax,phase=0):
 rp=n*m/2; rb=rp*math.cos(math.radians(25)); rt=rp+m; rr=rp-1.25*m
 inv=lambda r: math.sqrt(max(0,(r/rb)**2-1))-math.atan(math.sqrt(max(0,(r/rb)**2-1)))
 half=(math.pi*m/2-.025)/(2*rp); ip=inv(rp)
 if half+ip-inv(rt)<.001:
  lo,hi=rp,rt
  for _ in range(40):
   mid=(lo+hi)/2
   if half+ip-inv(mid)>.001:lo=mid
   else:hi=mid
  rt=lo
 pts=[]
 for k in range(n):
  c=phase+2*math.pi*k/n
  # symmetric involute, radial root relief
  low=max(rb,rr); a0=half+ip-inv(low)
  pts.append((rr*math.cos(c-a0),rr*math.sin(c-a0)))
  for j in range(9):
   r=low+(rt-low)*j/8;a=half+ip-inv(r);pts.append((r*math.cos(c-a),r*math.sin(c-a)))
  at=half+ip-inv(rt)
  for j in range(1,4):
   a=-at+2*at*j/3;pts.append((rt*math.cos(c+a),rt*math.sin(c+a)))
  for j in range(7,-1,-1):
   r=low+(rt-low)*j/8;a=half+ip-inv(r);pts.append((r*math.cos(c+a),r*math.sin(c+a)))
  pts.append((rr*math.cos(c+a0),rr*math.sin(c+a0)))
 # remove duplicate points
 out=[]
 for p in pts:
  if not out or math.dist(p,out[-1])>1e-8:out.append(p)
 return cq.Workplane('XY').workplane(offset=z).polyline(out).close().extrude(h).val().translate((*ax,0))
def phase(a,b,zd,zn,p=0):
 beta=math.atan2(b[1]-a[1],b[0]-a[0]);return beta+math.pi+(zd/zn)*(beta-p)-math.pi/zn
A={'input':(11.2,0),'minute':(5,0),'third':(2,4),'seconds':(-1.63,4),'counter':(5,-3.6),'hour':(5,0),'dayidler':(6.8,3.1176914536),'day':(8.6,6.2353829072)}
# common frame
base=cyl(12.6,-.75,.2,2.3,0)
for deg in (100,-100,140):
 x=2.3+12*math.cos(math.radians(deg));y=12*math.sin(math.radians(deg));base=base.fuse(cyl(.32,-.55,3.2,x,y))
base=base.fuse(cyl(.9,-.55,.4).cut(cyl(.57,-.56,.42)))
save('mainplate',base)
bridge=cyl(12.6,2.65,.25,2.3,0)
for key,ax in A.items():
 if key=='minute':continue
 r=.8 if key=='hour' else .46
 bridge=bridge.cut(cyl(r,2.6,.4,*ax))
bridge=bridge.fuse(cyl(.9,2.3,.35).cut(cyl(.57,2.29,.33)))
save('bridge',bridge)
# shafts with lower thrust collar, square top and seating shoulder
G={}
def shaft(key,bottom,top=3.2):
 x,y=A[key];return union([cyl(.3,bottom,2.95-bottom,x,y),cyl(.55,2.45,.15,x,y),cyl(.45,2.75,.20,x,y),box(.6,2.95,top-2.95,x,y)])
def cap(key,handz=None,length=None):
 x,y=A[key];z=2.95;top=3.15 if handz is None else handz+.22
 s=cyl(.65,z,top-z,x,y).cut(box(.6,z-.01,top-z+.02,x,y))
 if handz is not None:
  # pointer lies along +x, attached to its hub
  p=cq.Workplane('XY').workplane(offset=handz).polyline([(x+.4,y-.3),(x+length,y-.15),(x+length,y+.15),(x+.4,y+.3)]).close().extrude(.22).val();s=s.fuse(p)
 return s
# input variant gears both have 16-tooth barrel pinion
for variant,nd,nn in [('8h',40,30),('6h',30,30)]:
 m=12.4/(nd+nn)
 inp=union([shaft('input',0),gear(16,.2,0,.4545,A['input'],phase((0,0),A['input'],96,16)),gear(nd,m,.6,.3,A['input'])]);save('input_'+variant,inp)
 # minute spindle, upper collar retains it on hour tube
 x,y=A['minute'];s=union([cyl(.3,.6,3.14,x,y),cyl(.6,1.98,.02,x,y),cyl(.35,3.64,.10,x,y),box(.45,3.74,.22,x,y),gear(nn,m,.6,.3,A['minute'],phase(A['input'],A['minute'],nd,nn)),gear(60,2*math.dist(A['minute'],A['third'])/70,1,.25,A['minute'])]);save('minute_'+variant,s)
# other compound wheels
third=union([shaft('third',1),gear(10,2*math.dist(A['minute'],A['third'])/70,1,.25,A['third'],phase(A['minute'],A['third'],60,10)),gear(60,.11,1.3,.3,A['third'])]);save('third',third)
seconds=union([shaft('seconds',1.3,3.42),gear(6,.11,1.3,.3,A['seconds'],phase(A['third'],A['seconds'],60,6))]);save('seconds',seconds)
# minute motion work 12 teeth on minute shaft at 1.98-2.2
for v in ['8h','6h']:
 s=shapes['minute_'+v].fuse(gear(12,.15,1.75,.22,A['minute']));save('minute_'+v,s)
counter=union([shaft('counter',1.75),gear(36,.15,1.75,.22,A['counter'],phase(A['minute'],A['counter'],12,36)),gear(12,.12,2.35,.25,A['counter'])]);save('counter',counter)
x,y=A['hour'];hour=union([cyl(.7,2.05,.9,x,y),box(1.1,2.95,.74,x,y),cyl(.77,2.93,.02,x,y),gear(48,.12,2.35,.25,A['hour'],phase(A['counter'],A['hour'],12,48)),gear(12,.3,2.05,.22,A['hour'])]).cut(cyl(.38,2.0,2.0,x,y));save('hour',hour)
idler=union([shaft('dayidler',1.75),gear(12,.3,2.05,.22,A['dayidler'],phase(A['hour'],A['dayidler'],12,12)),gear(12,.2,1.75,.22,A['dayidler'])]);save('dayidler',idler)
day=union([shaft('day',1.75,3.42),gear(24,.2,1.75,.22,A['day'],phase(A['dayidler'],A['day'],12,24))]);save('day',day)
for key in ['input','third','counter','dayidler']:save(key+'_cap',cap(key))
save('seconds_hand',cap('seconds',3.2,5.2));save('day_hand',cap('day',3.2,3.3))
# hour retaining cap and hand separately, square seats and concentric bore
x,y=A['hour']
def pointer(name,ax,z,length,hub,hole):
 x,y=ax;s=union([cyl(hub,z,.22,x,y),cq.Workplane('XY').workplane(offset=z).polyline([(x+.4,y-.25),(x+length,y-.1),(x+length,y+.1),(x+.4,y+.25)]).close().extrude(.22).val()]).cut(box(hole,z-.01,.24,x,y));save(name,s)
for name,key,z,hz,tip,rad,hole in [('hour_hand','hour',2.95,3.47,5.6,1.05,1.1),('minute_hand','minute',3.74,3.74,6.2,.55,.45)]:
 x,y=A[key];s=cyl(rad,z,hz+.22-z,x,y).cut(box(hole,z-.01,hz+.24-z,x,y))
 w=.4 if key=='hour' else .25;wt=.15 if key=='hour' else .1
 t=cq.Workplane('XY').workplane(offset=hz).polyline([(x+.4,y-w),(x+tip,y-wt),(x+tip,y+wt),(x+.4,y+w)]).close().extrude(.22).val()
 save(name,s.fuse(t).cut(box(hole,z-.01,hz+.24-z,x,y)))
for v in ['8h','6h']:
 mob={}
 for k in A:
  parts=[k+'_'+v if k in ['input','minute'] else k]
  if k in ['input','third','counter','dayidler']:parts+=[k+'_cap']
  if k in ['hour','minute','seconds','day']:parts+=[k+'_hand']
  mob[k]={'axis':list(A[k]),'parts':parts,'material':'AD-C100-HT'}
 meshes=[('barrel',96,'input',16),('input',40 if v=='8h' else 30,'minute',30),('minute',60,'third',10),('third',60,'seconds',6),('minute',12,'counter',36),('counter',12,'hour',48),('hour',12,'dayidler',12),('dayidler',12,'day',24)]
 obj={'case_centre':[2.3,0],'fixed':['mainplate','bridge'],'mobiles':mob,'meshes':[dict(driver=a,driver_teeth=b,driven=c,driven_teeth=d) for a,b,c,d in meshes],'hands':{k:{'mobile':k,'part':k+'_hand'} for k in ['hour','minute','seconds','day']}}
 (P/('movement.json' if v=='8h' else 'variant_6h.json')).write_text(json.dumps(obj,indent=2))
# all insertion translations sampled under .2 mm, lower to upper
order=['mainplate','barrel','input_8h','minute_8h','third','seconds','hour','dayidler','day','counter','bridge','input_cap','third_cap','counter_cap','dayidler_cap','seconds_hand','day_hand','hour_hand','minute_hand']
paths={}
for n in order:
 dz=-20 if n=='mainplate' else 20
 vec=(0,0,dz)
 if n=='counter':vec=(0,-30,0)
 if n in ['dayidler','day']:vec=(15,25.980762114,0)
 steps=170 if n in ['counter','dayidler','day'] else 110
 paths[n]=[[[1,0,0,vec[0]*(1-i/steps)],[0,1,0,vec[1]*(1-i/steps)],[0,0,1,vec[2]*(1-i/steps)],[0,0,0,1]] for i in range(steps+1)]
(P/'assembly.json').write_text(json.dumps({'order':order,'paths':paths}))
(P/'report.json').write_text(json.dumps({'parts':{k:'not_tested' for k in ['P1','P2','P3','P4']},'height_mm':4.71},indent=2))
