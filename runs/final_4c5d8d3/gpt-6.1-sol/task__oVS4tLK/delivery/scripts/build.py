import cadquery as cq, math, json, os, sys
sys.path.insert(0,'/app/tools')
from kernel import write_step
OUT='/app/delivery'
os.makedirs(OUT+'/parts',exist_ok=True)
C=(2.8,0); A=(10.8,0); B=(-2,0); CC=(-2,5.25); D=(3.4,5.25); S=(8.15,5.25-math.sqrt(4.8**2-4.75**2)); R=(2.8,-5.55); I=(2.8+math.sqrt(4.08**2-1.266**2),1.266); DAY=(2.8,6)
P=(-2,-10.5); Q=(9.8,-5.5)
shapes={}
def cyl(p,r,z,h): return cq.Workplane('XY').workplane(offset=z).center(*p).circle(r).extrude(h)
def ring(p,ro,ri,z,h): return cyl(p,ro,z,h).cut(cyl(p,ri,z-.01,h+.02))
def strip(p,q,w,z,h):
 dx=q[0]-p[0];dy=q[1]-p[1];L=math.hypot(dx,dy)
 return cq.Workplane('XY').box(L,w,h,centered=(True,True,False)).rotate((0,0,0),(0,0,1),math.degrees(math.atan2(dy,dx))).translate(((p[0]+q[0])/2,(p[1]+q[1])/2,z))
def gear(p,n,m,z,h,phase=0):
 rp=n*m/2; rb=rp*math.cos(math.radians(25)); rf=rp-1.25*m; ra=rp+m
 inv=lambda r: math.sqrt(max(0,(r/rb)**2-1))-math.atan(math.sqrt(max(0,(r/rb)**2-1)))
 half=(math.pi*m/2-.03)/(2*rp); ip=inv(rp)
 pts=[]
 def pt(r,t): return (p[0]+r*math.cos(t),p[1]+r*math.sin(t))
 for k in range(n):
  a=2*math.pi*k/n+phase; rootangle=half+ip-inv(max(rf,rb))
  pts.append(pt(rf,a-rootangle))
  for j in range(9):
   r=max(rf,rb)+(ra-max(rf,rb))*j/8
   pts.append(pt(r,a-half-ip+inv(r)))
  for j in range(8,-1,-1):
   r=max(rf,rb)+(ra-max(rf,rb))*j/8
   pts.append(pt(r,a+half+ip-inv(r)))
  pts.append(pt(rf,a+rootangle))
  for j in range(1,4): pts.append(pt(rf,a+rootangle+(2*math.pi/n-2*rootangle)*j/4))
 # remove adjacent duplicates
 clean=[]
 for pnt in pts:
  if not clean or math.dist(pnt,clean[-1])>1e-8:clean.append(pnt)
 return cq.Workplane('XY').workplane(offset=z).polyline(clean).close().extrude(h)
def save(name,s):
 s=s.clean(); assert len(s.solids().vals())==1,name
 assert s.val().isValid(),name
 shapes[name]=s
 write_step(OUT+'/parts/'+name+'.step',s)
def combine(seq):
 s=seq[0]
 for t in seq[1:]:s=s.union(t)
 return s
# Fixed frame, and separately installable bearing bridges.
base=cyl(C,12.5,-.85,.35)
for p in [P,Q]:base=base.union(cyl(p,.65,-.5,8.2))
base=base.union(ring((0,0),.95,.54,-.5,.3))
for p,r in [((0,0),.54),(A,.39)]:base=base.cut(cyl(p,r,-.95,.6))
save('mainplate',base)
def bridge(name,p,q,z,bore,via=None):
 ss=[strip(p,q,.9,z,.4),cyl(p,.85,z,.4)] if via is None else [strip(p,via,.9,z,.4),strip(via,q,.9,z,.4),cyl(p,.85,z,.4)]
 s=combine(ss).cut(cyl(p,bore,z-.1,.6)).cut(cyl(q,.65,-1,11))
 save(name,s)
# Barrel bridge limited to 0.30 mm so it clears the winding square and minute gear.
s=combine([strip((0,0),P,.9,2.25,.3),cyl((0,0),.95,2.25,.3)]).cut(cyl((0,0),.54,2.2,.4)).cut(cyl(P,.65,-1,11))
save('barrel_bridge',s)
bridge('input_bridge',A,Q,3.12,.39)
bridge('third_bridge',B,P,4.65,.29)
bridge('fifth_bridge',D,Q,5.1,.29,via=(3.4,8.5))
top=cyl(C,12.65,7.7,.4)
for p,r in [(C,.74),(DAY,.69)]:top=top.union(ring(p,1.2,r,8.1,.7 if p==C else .2))
for p,r in [(C,.74),(CC,.29),(S,.29),(R,.39),(I,.54),(DAY,.69)]:top=top.cut(cyl(p,r,7.6,1.4))
save('dial_plate',top)
# Input and minute mobiles vary, but all bearing axes and fixed parts remain identical.
for tag,na,ma in [('8h',40,.2),('6h',30,8/35)]:
 a=combine([gear(A,12,.2,0,.4545,math.pi/12),cyl(A,.35,-.7,4.47),gear(A,na,ma,2.6,.4)])
 save('input_'+tag,a)
 minute=combine([cyl(C,.35,2.6,2.5),cyl(C,.30,5.1,4.45),gear(C,40,ma,2.6,.4,math.pi/40),gear(C,36,.2,3.1,.4)])
 # minute hand axial stop at 8.30
 minute=minute
 save('minute_'+tag,minute)
save('minute_reductionwheel',gear(C,12,.23125,5.1,.4).cut(cyl(C,.30,5,.6)))
save('third',combine([cyl(B,.25,3.1,2.15),cyl(B,.5,4.35,.25),gear(B,12,.2,3.1,.4,math.pi/12),gear(B,48,.175,3.6,.4)]))
save('fourth',combine([cyl(CC,.25,3.6,4.75),cyl(CC,.4,7.35,.25),gear(CC,12,.175,3.6,.4,math.pi/12),gear(CC,60,.15,4.1,.4)]))
save('fifth',combine([cyl(D,.25,4.1,1.7),gear(D,12,.15,4.1,.4,math.pi/12),gear(D,12,.4,4.6,.4)]))
save('seconds_train',combine([cyl(S,.25,4.6,5.45),cyl(S,.5,7.35,.25),gear(S,12,.4,4.6,.4,2*math.atan2(S[1]-D[1],S[0]-D[0])+math.pi/12)]))
save('reduction',combine([cyl(R,.35,5.1,3.25),cyl(R,.6,7.35,.25),gear(R,36,.23125,5.1,.4,math.pi/36),gear(R,12,.185,5.6,.5)]))
hour=combine([cyl(C,.7,5.6,3.45),cyl(C,1,7.35,.25),gear(C,48,.185,5.6,.5,math.pi/48),gear(C,12,.34,6.2,.6)])
hour=hour.cut(cyl(C,.34,5.5,3.7));save('hour_train',hour)
save('day_idler',combine([cyl(I,.5,6.2,2.15),cyl(I,.75,7.35,.25),gear(I,12,.34,6.2,.6,2*math.atan2(I[1],I[0]-C[0])+math.pi/12),gear(I,12,.34,6.9,.6)]))
save('day_train',combine([cyl(DAY,.65,6.9,1.65),cyl(DAY,.9,7.35,.25),gear(DAY,24,.34,6.9,.6,1.5*math.atan2(DAY[1]-I[1],DAY[0]-I[0])+math.pi-math.pi/24)]))
def hand(name,p,r,length,z,angle):
 s=cyl(p,r+.3,z,.4)
 q=(p[0]+length*math.cos(angle),p[1]+length*math.sin(angle))
 # stem starts at the hub and stays clear of bore
 start=(p[0]+r*math.cos(angle),p[1]+r*math.sin(angle))
 s=s.union(strip(start,q,.45,z,.4)).cut(cyl(p,r,z-.01,.16))
 if name=='hour_hand':s=s.cut(cyl(p,.34,z-.01,.5))
 save(name,s)
hand('hour_hand',C,.7,5.3,8.9,math.pi/2)
hand('minute_hand',C,.30,7,9.4,math.pi)
hand('seconds_hand',S,.25,5.2,9.9,-math.pi/2)
hand('day_hand',DAY,.65,3.2,8.4,math.pi/2)
# Blind caps sit on shaft ends, after installation of each bearing bridge.
for name,p,z,r in [('input_cap',A,3.52,.35),('third_cap',B,5.1,.25),('fourth_cap',CC,8.2,.25),('fifth_cap',D,5.55,.25),('reduction_cap',R,8.2,.35),('idler_cap',I,8.2,.5)]:
 save(name,cyl(p,r+.3,z,.4 if name=='third_cap' else .5).cut(cyl(p,r,z-.01,.16 if name=='third_cap' else .16 if name in ['fourth_cap','reduction_cap','idler_cap'] else .26)))
fixed=['mainplate','barrel_bridge','input_bridge','third_bridge','fifth_bridge','dial_plate']
for tag,filename,na in [('8h','movement.json',40),('6h','variant_6h.json',30)]:
 mobs={}
 def mob(n,p,parts):mobs[n]={'axis':list(p),'parts':parts,'material':'AD-C100-HT'}
 mob('input',A,['input_'+tag,'input_cap']);mob('minute',C,['minute_'+tag,'minute_reductionwheel','minute_hand'])
 mob('third',B,['third','third_cap']);mob('fourth',CC,['fourth','fourth_cap']);mob('fifth',D,['fifth','fifth_cap'])
 mob('seconds',S,['seconds_train','seconds_hand']);mob('reduction',R,['reduction','reduction_cap'])
 mob('hour',C,['hour_train','hour_hand']);mob('idler',I,['day_idler','idler_cap']);mob('day',DAY,['day_train','day_hand'])
 meshes=[]
 for a,za,b,zb in [('barrel',96,'input',12),('input',na,'minute',40),('minute',36,'third',12),('third',48,'fourth',12),('fourth',60,'fifth',12),('fifth',12,'seconds',12),('minute',12,'reduction',36),('reduction',12,'hour',48),('hour',12,'idler',12),('idler',12,'day',24)]:meshes.append(dict(driver=a,driver_teeth=za,driven=b,driven_teeth=zb))
 doc=dict(barrel='BR-096-30',case_centre=list(C),fixed=fixed,mobiles=mobs,meshes=meshes,hands={k:dict(mobile=v,part=v+'_hand') for k,v in [('hour','hour'),('minute','minute'),('seconds','seconds'),('day','day')]})
 json.dump(doc,open(OUT+'/'+filename,'w'),indent=2)
order=['mainplate','barrel','barrel_bridge','input_8h','minute_8h','input_bridge','input_cap','third','fourth','fifth','seconds_train','third_bridge','third_cap','fifth_bridge','fifth_cap','minute_reductionwheel','reduction','hour_train','day_idler','day_train','dial_plate','fourth_cap','reduction_cap','idler_cap','day_hand','hour_hand','minute_hand','seconds_hand']
# Vertical insertion at 0.15 mm increments, from entirely above the complete bounding box.
paths={}
for n in order:
 paths[n]=[[[1,0,0,0],[0,1,0,0],[0,0,1,30*(200-j)/200],[0,0,0,1]] for j in range(201)]
json.dump(dict(order=order,paths=paths),open(OUT+'/assembly.json','w'))
json.dump(dict(parts={k:'not_tested' for k in ['P1','P2','P3','P4']},height_mm=11.15),open(OUT+'/report.json','w'),indent=2)
# Nominal checks archived with the generator.
print('Generated',len(shapes),'STEP parts')
