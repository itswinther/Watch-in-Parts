import cadquery as cq, math, json, pathlib
D=pathlib.Path('/app/delivery'); C=(2.87,0)
shapes={}
def cyl(p,r,z,h):return cq.Workplane('XY').workplane(offset=z).center(*p).circle(r).extrude(h)
def ring(p,r,ri,z,h):return cyl(p,r,z,h).cut(cyl(p,ri,z-.01,h+.02))
def save(n,s):
 if n not in ['frame','barrel_bridge','input8','input6']:s=s.translate((0,0,2))
 s=s.clean(); assert len(s.solids().vals())==1,n
 cq.exporters.export(s,str(D/'parts'/f'{n}.step'));shapes[n]=s
# Piecewise linear involutes, with round tip and root-circle arcs approximated at fine spacing.
def gear(p,n,m,z,b,phase=0):
 rp=n*m/2; rb=rp*math.cos(math.radians(25)); rr=rp-1.25*m; ra=rp+m
 def inv(r):
  a=math.acos(min(1,rb/r));return math.tan(a)-a
 half=(math.pi*m/2-.03)/(2*rp); ip=inv(rp); pts=[]
 for k in range(n):
  th=phase+2*math.pi*k/n
  # clockwise edge to counterclockwise edge of each tooth
  amin=th-half-ip
  for r in [rr,max(rr,rb)]+[max(rr,rb)+(ra-max(rr,rb))*j/7 for j in range(1,8)]:
   a=th-half-ip+(inv(r) if r>=rb else 0);pts.append((p[0]+r*math.cos(a),p[1]+r*math.sin(a)))
  htip=half+ip-inv(ra)
  for j in range(1,5):
   a=th-htip+2*htip*j/4;pts.append((p[0]+ra*math.cos(a),p[1]+ra*math.sin(a)))
  for r in [ra-(ra-max(rr,rb))*j/7 for j in range(1,8)]+[rr]:
   a=th+half+ip-(inv(r) if r>=rb else 0);pts.append((p[0]+r*math.cos(a),p[1]+r*math.sin(a)))
  hr=half+ip-(inv(rr) if rr>=rb else 0)
  a0=th+hr;a1=th+2*math.pi/n-hr
  for j in range(1,4):
   a=a0+(a1-a0)*j/4;pts.append((p[0]+rr*math.cos(a),p[1]+rr*math.sin(a)))
 clean=[]
 for pt in pts:
  if not clean or math.dist(pt,clean[-1])>1e-7:clean.append(pt)
 return cq.Workplane('XY').workplane(offset=z).polyline(clean).close().extrude(b)
axes={'minute':C,'hour':C,'input8':(10.8,0),'input6':(11.2,0),'sec_inter':(C[0],-6.528),'seconds':(C[0]+5.6,-6.528+math.sqrt(6.12**2-5.6**2)),'hour_inter':(C[0]-6.4,0),'day_inter':(C[0]+math.sqrt(4.48**2-((4.48**2+6.2**2-6.72**2)/12.4)**2),(4.48**2+6.2**2-6.72**2)/12.4),'day':(C[0],6.2)}
# all gears integral to their own arbor; hands are separately seated rings.
mobs={};meshes=[]
def mobile(n,s,mat='AD-C100-HT'):
 save(n,s);mobs[n]={'axis':axes[n],'parts':[n],'material':mat}
def mesh(a,na,b,nb):meshes.append({'driver':a,'driver_teeth':na,'driven':b,'driven_teeth':nb})
for suffix,nt in [('8',12),('6',16)]:
 n='input'+suffix;p=axes[n];dist=p[0]-C[0];m=dist/48
 s=gear(p,nt,.2,0,.4545,math.pi/nt).union(gear(p,48,m,2.6,.45)).union(cyl(p,.55,.3,6.25).union(cyl(p,.15,6.55,.25)).union(cyl(p,.15,-.45,.75)))
 mobile(n,s)
 # separate minute wheel for each build
 n2='minute'+suffix
 s=gear(C,48,m,.6,.45,math.pi/48).union(gear(C,60,.192,1.25,.45)).union(cyl(C,.78,2.5,.45).union(cyl(C,.85,2.4,.1))).union(cyl(C,.65,.6,5.85).union(cyl(C,.3,.35,.3)).union(cyl(C,.73,5.35,.2)).union(cyl(C,.40,6.45,.25)))
 save(n2,s)
mobile('sec_inter',gear(axes['sec_inter'],8,.192,1.25,.45,math.pi/8).union(gear(axes['sec_inter'],64,.17,1.95,.45)).union(cyl(axes['sec_inter'],.3,.35,4.45).union(cyl(axes['sec_inter'],.5,.6,.2)).union(cyl(axes['sec_inter'],.5,4.4,.2))))
mobile('seconds',gear(axes['seconds'],8,.17,1.95,.45,9*math.atan2(math.sqrt(6.12**2-5.6**2),5.6)+math.pi-math.pi/8).union(cyl(axes['seconds'],.3,.35,5.75).union(cyl(axes['seconds'],.5,.6,.2)).union(cyl(axes['seconds'],.5,5.15,.2))).union(cyl(axes['seconds'],.15,6.1,.25)))
mobile('hour_inter',gear(axes['hour_inter'],48,.2,2.5,.45,math.pi/48).union(gear(axes['hour_inter'],16,.16,3.2,.45)).union(cyl(axes['hour_inter'],.3,.35,4.45).union(cyl(axes['hour_inter'],.4,.6,4.0)).union(cyl(axes['hour_inter'],.5,.6,.2)).union(cyl(axes['hour_inter'],.5,4.4,.2))))
s=gear(C,64,.16,3.2,.45,math.pi/64).union(gear(C,16,.28,4.0,.55)).union(cyl(C,1.04,3.2,2.5));s=s.union(cyl(C,.95,5.7,.25)).union(cyl(C,1.3,5.15,.2)).cut(cyl(C,.78,3.1,2.55)).cut(cyl(C,.70,5.65,.5));mobile('hour',s)
mobile('day_inter',gear(axes['day_inter'],16,.28,4.0,.55,2*math.atan2(axes['day_inter'][1],axes['day_inter'][0]-C[0])+math.pi-math.pi/16).union(gear(axes['day_inter'],16,.28,4.65,.55)).union(cyl(axes['day_inter'],.5,4.0,1.2).union(cyl(axes['day_inter'],.3,3.75,1.6))))
mobile('day',gear(axes['day'],32,.28,4.65,.55,1.5*math.atan2(6.2-axes['day_inter'][1],C[0]-axes['day_inter'][0])+math.pi-math.pi/32).union(cyl(axes['day'],.3,3.75,2.35).union(cyl(axes['day'],.5,4.0,1.35))).union(cyl(axes['day'],.15,6.1,.25)))
mesh('minute',60,'sec_inter',8);mesh('sec_inter',64,'seconds',8);mesh('minute',16,'hour_inter',48);mesh('hour_inter',16,'hour',64);mesh('hour',16,'day_inter',16);mesh('day_inter',16,'day',32)
save('minute_pinion',gear(C,16,.2,2.5,.45).cut(cyl(C,.78,2.4,.7)))
# Hands, positive x points; annular fitting seats locate separately printed pointers.
hands={}
for n,r,ri,z,L in [('hour',1.25,.95,5.5,5.4),('minute',.71,.40,6.25,7.0),('seconds',.40,.15,5.9,5.1),('day',.40,.15,5.9,3.2)]:
 z+=.2
 p=axes[n];s=ring(p,r,ri,z,.25).union(cq.Workplane('XY').workplane(offset=z).center(p[0]+(r*.75+L-.175)/2,p[1]).rect(L-.175-r*.75,.35).extrude(.25)).union(cyl((p[0]+L-.175,p[1]),.175,z,.25))
 save(n+'_hand',s);
 if n!='minute':mobs[n]['parts'].append(n+'_hand')
 hands[n]={'mobile':n,'part':n+'_hand'}
# Lower plate and top closed dial are tied by three peripheral posts.
base=cyl(C,12.65,-.9,.35)
for p in [(-4,9.5),(-4,-9.5),(C[0]+9,7)]:base=base.union(cyl(p,.45,-.55,7.95))
for nn in ['input8','input6']:
 base=base.union(cyl(axes[nn],.7,-.55,.5))
for nn in ['input8','input6']:
 base=base.cut(cyl(axes[nn],.19,-.5,.5))
save('frame',base)
dial=cyl(C,12.69,5.4,.2)
for n in ['minute','seconds','day']:
 r=1.10 if n=='minute' else .35;dial=dial.cut(cyl(axes[n],r,5.3,.5))
# blind bearing pockets on underside of dial; slender supports extend down to arbor ends
for n in ['input8','input6','sec_inter','hour_inter']:
 p=axes[n];boss=ring(p,.6,.20 if n.startswith('input') else .35,4.65,.75);dial=dial.union(boss)
# barrel top journal: cap under the dial, joined by its bearing tube
# Barrel bearing carried on a separately fitted bridge, below the train.
bridge=ring((0,0),.9,.55,2.30,.25).union(cq.Workplane('XY').workplane(offset=2.30).polyline([(-.7,-.4),(-4,9.0),(-4,10.0),(-.7,.4)]).close().extrude(.25))
bridge=bridge.union(cyl((-4,9.5),.75,2.30,.25))
bridge=bridge.cut(cyl((-4,9.5),.45,2.25,.4))
# Lower train bearings carried by a removable branched plate.
def beam(a,b,z,h,w):
 dx=b[0]-a[0];dy=b[1]-a[1];ll=math.hypot(dx,dy);nx=-dy/ll*w/2;ny=dx/ll*w/2
 return cq.Workplane('XY').workplane(offset=z).polyline([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]).close().extrude(h)
for nn in ['minute','sec_inter','seconds','hour_inter']:
 pp=axes[nn];bridge=bridge.union(beam((0,0),pp,2.3,.25,1.2)).union(cyl(pp,.8,2.3,.25))
for nn in ['minute','sec_inter','seconds','hour_inter']:
 bridge=bridge.cut(cyl(axes[nn],.35,2.25,.4))
bridge=bridge.cut(cyl((0,0),.55,2.25,.4))
save('barrel_bridge',bridge)
# Upper side-train shelf, installed after the centre hour wheel.
sh=beam(axes['day_inter'],(C[0]+9,7),5.7,.2,1.3).union(beam(axes['day_inter'],axes['day'],5.7,.2,1.3))
for nn in ['day_inter','day']:
 sh=sh.union(cyl(axes[nn],.8,5.7,.2)).cut(cyl(axes[nn],.35,5.65,.3))
sh=sh.cut(cyl((C[0]+9,7),.45,5.65,.3))
save('day_shelf',sh.translate((0,0,-2)))
for n in ['input8','input6','sec_inter','hour_inter']:
 dial=dial.cut(cyl(axes[n],.19 if n.startswith('input') else .35,4.6,.8))
dial=dial.union(ring(axes['day_inter'],.6,.35,5.25,.15))
save('dial',dial)
for suffix in ['8','6']:
 mm={k:v for k,v in mobs.items() if k not in ['input8','input6']};mm['input']={**mobs['input'+suffix]};mm['minute']={'axis':C,'parts':['minute'+suffix,'minute_pinion','minute_hand'],'material':'AD-C100-HT'}
 me=[{'driver':'barrel','driver_teeth':96,'driven':'input','driven_teeth':12 if suffix=='8' else 16},{'driver':'input','driver_teeth':48,'driven':'minute','driven_teeth':48}]+meshes
 out={'barrel':'BR-096-30','case_centre':C,'fixed':['frame','barrel_bridge','day_shelf','dial'],'mobiles':mm,'meshes':me,'hands':hands}
 (D/('movement.json' if suffix=='8' else 'variant_6h.json')).write_text(json.dumps(out,indent=2))
order=['frame','barrel','barrel_bridge','input8','minute8','sec_inter','seconds','minute_pinion','hour_inter','hour','day_shelf','day_inter','day','dial','hour_hand','seconds_hand','day_hand','minute_hand']
paths={}
for n in order:
 # 20 mm dial-side lift, sampled in 0.1 mm increments
 paths[n]=[[[1,0,0,0],[0,1,0,0],[0,0,1,20-i*.1],[0,0,0,1]] for i in range(201)]
# All parts now enter from the dial side, before their retaining bridge or pinion.
(D/'assembly.json').write_text(json.dumps({'order':order,'paths':paths}))
(D/'report.json').write_text(json.dumps({'parts':{'P1':'not_tested','P2':'not_tested','P3':'not_tested','P4':'not_tested'},'height_mm':9.6},indent=2))
print('Generated',len(shapes),'STEP parts',flush=True)
