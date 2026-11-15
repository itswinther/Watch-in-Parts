import cadquery as cq, math, json, os, sys
from pathlib import Path
OUT=Path('/app/delivery'); shapes={}; fixed=[]; mobs={}; meshes=[]
C=(2.8,0)
axes={'first':(10.8,0),'minute':C,'a':(-2.2,0),'b':(-2.2,-4),'c':(3.6,-5.5378784028),'seconds':(-.4,-5.5378784028),'reducer':(2.8,6),'hour':C,'idler':(8.8,0),'day':(4.8,math.sqrt(40.25))}
# Correct c position on the six-millimetre circle about b.
axes['c']=(3.6,-4-math.sqrt(36-5.8**2)); axes['seconds']=(axes['c'][0]-4,axes['c'][1])
rad={'first':.3,'minute':.25,'a':.22,'b':.22,'c':.22,'seconds':.22,'reducer':.22,'hour':.65,'idler':.22,'day':.25}
span={'first':(-.35,3.55),'minute':(2.7,9.75),'a':(3.4,4.85),'b':(4.05,5.5),'c':(4.7,6.15),'seconds':(5.35,10.2),'reducer':(6.,7.45),'hour':(6.7,9.3),'idler':(7.3,8.75),'day':(7.95,10.65)}
def cyl(p,r,z,h):return cq.Workplane('XY').workplane(offset=z).center(*p).circle(r).extrude(h)
def save(n,s):
 s=s.clean(); assert len(s.solids().vals())==1,(n,len(s.solids().vals())); assert s.val().isValid(),n
 cq.exporters.export(s,str(OUT/'parts'/f'{n}.step')); shapes[n]=s
 print(n,flush=True)
def gear(p,n,m,z,b,phase=0):
 rp=n*m/2; rb=rp*math.cos(math.radians(25)); rr=rp-1.25*m; ra=rp+m
 inv=lambda r: math.sqrt(max(0,(r/rb)**2-1))-math.acos(min(1,rb/r))
 half=math.pi/(2*n)-.018/rp; ip=inv(rp); pts=[]
 for k in range(n):
  a=phase+2*math.pi*k/n; r0=max(rb,rr)
  # Polygonal involute flanks, with radial root extensions below the base circle.
  beta0=half+ip-inv(r0)
  pts.append((rr*math.cos(a-beta0),rr*math.sin(a-beta0)))
  for j in range(9):
   r=r0+(ra-r0)*j/8; beta=half+ip-inv(r)
   pts.append((r*math.cos(a-beta),r*math.sin(a-beta)))
  for j in range(8,-1,-1):
   r=r0+(ra-r0)*j/8; beta=half+ip-inv(r)
   pts.append((r*math.cos(a+beta),r*math.sin(a+beta)))
  pts.append((rr*math.cos(a+beta0),rr*math.sin(a+beta0)))
  end=2*math.pi/n-beta0
  for j in range(1,4):
   t=beta0+(end-beta0)*j/4; pts.append((rr*math.cos(a+t),rr*math.sin(a+t)))
 clean=[]
 for pt in pts:
  if not clean or math.dist(pt,clean[-1])>1e-8:clean.append(pt)
 return cq.Workplane('XY').workplane(offset=z).polyline([(x+p[0],y+p[1]) for x,y in clean]).close().extrude(b)
# Each compound has integral arbor and separately generated, integral toothed lands.
lands={k:[] for k in axes}
def pair(d,nd,r,nr,m,z,b=.3):
 pd=(0,0) if d=='barrel' else axes[d]; pr=axes[r]; alpha=math.atan2(pr[1]-pd[1],pr[0]-pd[0]); dist=math.dist(pd,pr)
 assert abs(dist-m*(nd+nr)/2)<1e-6,(d,r,dist,m*(nd+nr)/2)
 phid=alpha # driver tooth faces the line of centres
 phir=alpha+math.pi-math.pi/nr
 if d!='barrel':lands[d].append((nd,m,z,b,phid))
 lands[r].append((nr,m,z,b,phir))
 meshes.append(dict(driver=d,driver_teeth=nd,driven=r,driven_teeth=nr))
pair('barrel',96,'first',12,.2,0,.4545)
pair('first',24,'minute',24,1/3,3.)
pair('minute',40,'a',10,.2,3.65)
pair('a',30,'b',10,.2,4.3)
pair('b',50,'c',10,.2,4.95)
pair('c',20,'seconds',20,.2,5.6)
pair('minute',12,'reducer',36,.25,6.25)
pair('reducer',10,'hour',40,.24,6.9)
pair('hour',20,'idler',20,.3,7.55)
pair('idler',10,'day',20,.5,8.2)
# Split upper wheels from their arbors so the separator plates can be installed.
# Arbor shoulders locate the loose wheels radially and axially.
def shaft_radius(k,z):
 if k=='first' and .4545<z<3:return .5
 if k=='minute':
  if 3.3<z<3.65:return .75
  if 3.65<=z<6.25:return .5
 if len(lands[k])>1:
  low=sorted(lands[k],key=lambda v:v[2])
  if low[0][2]+low[0][3]<z<low[-1][2]:return .9 if k=='hour' else (.5 if k=='idler' else .4)
 return rad[k]
def make_mobile(k,ls,prefix):
 ls=sorted(ls,key=lambda v:v[2]);lo,hi=span[k]
 shaft=cyl(axes[k],rad[k],lo,hi-lo)
 for n,m,z,b,ph in ls[1:]:
  prev=max(q[2]+q[3] for q in ls if q[2]<z)
  r=shaft_radius(k,(prev+z)/2)
  shaft=shaft.union(cyl(axes[k],r,prev,z-prev))
 n,m,z,b,ph=ls[0];shaft=shaft.union(gear(axes[k],n,m,z,b,ph))
 if k=='hour':shaft=shaft.cut(cyl(C,.30,6.65,3))
 if k in ['hour','minute','seconds','day']:
  tip=.45 if k=='hour' else .16
  t=cyl(axes[k],tip,hi,.15)
  if k=='hour':t=t.cut(cyl(C,.3,hi,.15))
  shaft=shaft.union(t)
 names=[prefix+'_body'];save(names[0],shaft)
 for j,(n,m,z,b,ph) in enumerate(ls[1:]):
  r=rad[k] if j==len(ls)-2 else shaft_radius(k,z+.001)
  w=gear(axes[k],n,m,z,b,ph).cut(cyl(axes[k],r,z-.01,b+.02))
  name=prefix+'_wheel'+str(j+1);save(name,w);names.append(name)
 return names
for k in axes:
 names=make_mobile(k,lands[k],k);mobs[k]={'axis':list(axes[k]),'parts':names,'material':'AD-C100-HT'}
variant_parts={}
for k in ['first','minute']:
 ls=[(18 if k=='first' else 24,16/42,z,b,math.pi if k=='first' else 2*math.pi-math.pi/24) if abs(z-3)<1e-6 else (n,m,z,b,ph) for n,m,z,b,ph in lands[k]]
 variant_parts[k]=make_mobile(k,ls,k+'_6h')
# Plate segments make each successive bearing accessible during top-down assembly.
levels=[(-.85,-.10),(2.59,2.89),(3.375,3.625),(4.025,4.275),(4.675,4.925),(5.325,5.575),(5.975,6.225),(6.625,6.875),(7.275,7.525),(7.925,8.175),(8.575,8.875),(8.95,9.2)]
posts=[]
for ang in [55,125,235,305]:
 p=(C[0]+12.15*math.cos(math.radians(ang)),12.15*math.sin(math.radians(ang))); posts.append(p)
for i,(lo,hi) in enumerate(levels):
 s=cyl(C,12.65,lo,hi-lo)
 for k,p in axes.items():
  l,h=span[k]
  if h>lo and l<hi:
   r=shaft_radius(k,(lo+hi)/2)+.04
   if k=='minute' and hi>6.65:r=.70
   s=s.cut(cyl(p,r,lo-.01,hi-lo+.02))
 if i==0:
  # Bottom of the arbor pocket is 40 microns below the barrel pivot.
  s=s.cut(cyl((0,0),.54,-.4945,.5))
 elif lo<2.59+1e-6:
  # Upper arbor is retained under this plate, without a thin blind-pocket roof.
  pass
 if i==11:
  # Closed dial with only hand-arbor apertures.
  pass
 save('plate_%02d'%i,s); fixed.append('plate_%02d'%i)
# Pillars are segmented at plate surfaces, so all joins are touching, not overlapping.
for i in range(len(levels)-1):
 lo=levels[i][1]; hi=levels[i+1][0]
 for j,p in enumerate(posts):
  n=f'post_{i}_{j}'; save(n,cyl(p,.32,lo,hi-lo));fixed.append(n)
# Four independent pointer parts, sitting on the end faces of their arbors.
for k,length,z in [('hour',5.5,9.3),('minute',6.3,9.75),('seconds',5.1,10.2),('day',3.2,10.65)]:
 p=axes[k]; r=rad[k]; hand=cyl(p,max(.55,r),z,.3)
 # Arms extend toward +x in the delivered display pose.
 arm=cq.Workplane('XY').workplane(offset=z).polyline([(p[0],p[1]-.25),(p[0]+length-.4,p[1]-.19),(p[0]+length,p[1]),(p[0]+length-.4,p[1]+.19),(p[0],p[1]+.25)]).close().extrude(.3)
 hand=hand.union(arm)
 if k=='hour':hand=hand.cut(cyl(p,.30,z-.01,.32))
 hand=hand.cut(cyl(p,.45 if k=='hour' else .16,z-.01,.16))
 save(k+'_hand',hand);mobs[k]['parts'].append(k+'_hand')
# 60-part limit: combine the four pillars for each level with the following plate.
# A single print is connected through that plate and remains open from below.
for i in range(len(levels)-1):
 name='plate_%02d'%(i+1);s=shapes[name]
 for j in range(4):
  n=f'post_{i}_{j}';s=s.union(shapes[n]);fixed.remove(n);del shapes[n];os.remove(OUT/'parts'/f'{n}.step')
 save(name,s)
base={'barrel':'BR-096-30','case_centre':list(C),'fixed':fixed,'mobiles':mobs,'meshes':meshes,'hands':{k:{'mobile':k,'part':k+'_hand'} for k in ['hour','minute','seconds','day']}}
(OUT/'movement.json').write_text(json.dumps(base,indent=2))
import copy
v=copy.deepcopy(base)
for k in ['first','minute']:
 v['mobiles'][k]['parts']=variant_parts[k]+([k+'_hand'] if k=='minute' else [])
v['meshes'][1]['driver_teeth']=18
(OUT/'variant_6h.json').write_text(json.dumps(v,indent=2))
# Assembly with axial insertion, in increasing order of their lowest obstructing feature.
# Tall arbors can be threaded through bearing apertures as successive plates are lowered.
order=['plate_00','barrel','first_body','plate_01','first_wheel1','minute_body','plate_02','minute_wheel1','a_body','plate_03','a_wheel1','b_body','plate_04','b_wheel1','c_body','plate_05','c_wheel1','seconds_body','plate_06','minute_wheel2','reducer_body','plate_07','reducer_wheel1','hour_body','plate_08','hour_wheel1','idler_body','plate_09','idler_wheel1','day_body','plate_10','plate_11','hour_hand','minute_hand','seconds_hand','day_hand']
paths={}
for n in order:
 paths[n]=[[[1,0,0,0],[0,1,0,0],[0,0,1,30*(1-j/200)],[0,0,0,1]] for j in range(201)]
(OUT/'assembly.json').write_text(json.dumps({'order':order,'paths':paths}))
(OUT/'report.json').write_text(json.dumps({'parts':{'P1':'not_tested','P2':'not_tested','P3':'not_tested','P4':'not_tested'},'height_mm':11.8},indent=2))
