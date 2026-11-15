import cadquery as cq, math, json, os, sys
sys.path.insert(0,'/app/tools')
from kernel import write_step
D='/app/delivery'; C=(2.8,0)
shapes={}; fixed=[]; mobs={}; meshes=[]
def cyl(x,y,r,z,h,ri=0):
 w=cq.Workplane('XY',origin=(x,y,z)).circle(r)
 if ri:w=w.circle(ri)
 return w.extrude(h)
def union(*ss):
 s=ss[0]
 for t in ss[1:]:s=s.union(t)
 return s

def boxlink(p,q,width,z,h):
 dx=q[0]-p[0];dy=q[1]-p[1];L=math.hypot(dx,dy)
 return cq.Workplane('XY').box(L,width,h,centered=(True,True,False)).rotate((0,0,0),(0,0,1),math.degrees(math.atan2(dy,dx))).translate(((p[0]+q[0])/2,(p[1]+q[1])/2,z))
def put(n,s,f=False):
 assert len(s.solids().vals())==1,(n,len(s.solids().vals()))
 shapes[n]=s
 write_step(D+'/parts/'+n+'.step',s)
 if f:fixed.append(n)
 print(n,flush=True)
def abspt(p):return(p[0]+C[0],p[1])
def gear(N,m,p,z,h,phase=0,hole=0):
 rp=N*m/2; rb=rp*math.cos(math.radians(25));rf=rp-1.25*m;ra=rp+m
 inv=lambda a:math.tan(a)-a
 ip=inv(math.radians(25)); half=(math.pi*m/2-.03)/(2*rp)
 pts=[]
 for k in range(N):
  a=phase+2*math.pi*k/N
  radii=[rf,max(rf,rb)]+[max(rf,rb)+(ra-max(rf,rb))*j/7 for j in range(1,8)]
  flank=[]
  for r in radii:
   ang=half+ip-(inv(math.acos(rb/r)) if r>=rb else 0)
   flank.append((r,ang))
  for r,ang in flank:pts.append((p[0]+r*math.cos(a-ang),p[1]+r*math.sin(a-ang)))
  for r,ang in reversed(flank):pts.append((p[0]+r*math.cos(a+ang),p[1]+r*math.sin(a+ang)))
 pts=[v for i,v in enumerate(pts) if i==0 or math.dist(v,pts[i-1])>1e-8]
 s=cq.Workplane('XY',origin=(0,0,z)).polyline(pts).close().extrude(h)
 if hole:s=s.cut(cyl(*p,hole,z-.01,h+.02))
 return s
axes={'barrel':(0,0),'transfer':(10.8,0),'minute':C,'hour':C,'hour_idle':abspt((0,5.1)), 'A':abspt((-5.4,0)), 'B':abspt((-5.8,math.sqrt(4.5**2-.4**2))), 'day':abspt((0,-7))}
axes['seconds']=abspt((0,7))
bp=axes['B'];sp=axes['seconds']; dx=sp[0]-bp[0];dy=sp[1]-bp[1];dd=math.hypot(dx,dy);aa=(5.4**2-2.4**2+dd**2)/(2*dd);hh=math.sqrt(5.4**2-aa**2)
axes['C']=(bp[0]+aa*dx/dd-hh*dy/dd,bp[1]+aa*dy/dd+hh*dx/dd)
y=-20.2/14;axes['day_idle']=abspt((math.sqrt(4.8**2-y*y),y))
ph={('barrel',96):0}
def mesh(a,na,b,nb):
 theta=math.atan2(axes[b][1]-axes[a][1],axes[b][0]-axes[a][0]);pa=ph.get((a,na),0)
 ph[(b,nb)]=((na+nb)*theta+nb*math.pi-na*pa-math.pi)/nb
 meshes.append(dict(driver=a,driver_teeth=na,driven=b,driven_teeth=nb))
def g(mob,n,m,z,h=.4,hole=.4):return gear(n,m,axes[mob],z,h,ph.get((mob,n),0),hole)
def mobile(n,parts):mobs[n]=dict(axis=list(axes[n]),parts=parts,material='AD-C100-HT')
mesh('barrel',96,'transfer',12);mesh('transfer',24,'minute',24)
mesh('minute',12,'hour_idle',36);mesh('hour_idle',12,'hour',48)
mesh('minute',36,'A',12);mesh('A',48,'B',12);mesh('B',60,'C',12);mesh('C',12,'seconds',12)
mesh('hour',24,'day_idle',24);mesh('day_idle',24,'day',48)
# Lower plate, raised minute seat and a centre post; two peripheral pillars.
base=cyl(*C,12.65,-.9,.4)
base=union(base,cyl(0,0,1,-.5,.45),cyl(10.8,0,.8,-.5,.45))
base=base.cut(cyl(0,0,.54,-.5,.6)).cut(cyl(10.8,0,.39,-.5,.6))
for yy in [-11,11]:base=base.union(cyl(C[0],yy,.65,-.5,3.15))

put('lower_frame',base,True)
put('centre_bridge',union(boxlink(C,(C[0],11),1,.5,.25),cyl(*C,.3,.75,8.0)).cut(cyl(C[0],11,.65,.49,.27)),True)
# Frame ring above low-level wheels and the main bearing plate.
upper=union(cyl(*C,12.65,1.35,6.45,12.4),cyl(*C,12.5,2.65,.2))
upper=upper.cut(cyl(*C,.72,2.6,.45))
for p,r in [((0,0),.54),((10.8,0),.39)]:
 upper=upper.union(cyl(*p,.85,2.3,.35)).cut(cyl(*p,r,2.29,(.62 if p[0]>10 else .32)))
# main-plate posts for the hour idler, A, and day
specs={'A':(4.0,6.2,.35,.4),'day':(5.9,8.1,.35,.4)}
for n,(seat,top,r,bore) in specs.items():
 p=axes[n];upper=union(upper,cyl(*p,r,2.85,top-2.85),cyl(*p,.65,seat-.15,.15))
put('upper_frame',upper,True)
put('hour_idle_post',union(cyl(*axes['hour_idle'],.65,3.45,.1),cyl(*axes['hour_idle'],.5,3.55,1.75)),True)
put('hour_idle_bridge',union(boxlink(axes['hour_idle'],abspt((0,12.43)),.6,5.3,.2),cyl(*axes['hour_idle'],.85,5.3,.2)),True)
put('transfer_bridge',boxlink(axes['transfer'],abspt((12.43,0)),.7,3.45,.2),True)
# Separate brackets fitted after the wheels below them.
brackets={'B':(5.5,5.65,5.7,6.9,(-11.3,axes['B'][1])), 'C':(6.1,6.3,6.4,7.6,(12.5,axes['C'][1])), 'seconds':(6.8,7.0,7.1,8.1,(12.5,axes['seconds'][1])), 'day_idle':(4.85,5.05,5.2,6.4,(11.9,-3.75))}
for n,(z,zt,seat,top,q) in brackets.items():
 p=axes[n];q=abspt(q)
 # terminate at the inside surface of the rim, accounting for width
 v=(q[0]-C[0],q[1]); fac=12.43/math.hypot(*v);q=(C[0]+v[0]*fac,v[1]*fac)
 s=union(boxlink(p,q,.55,z,zt-z),cyl(*p,.35,zt,top-zt),cyl(*p,.5,seat-.1,.1))
 put(n+'_bracket',s,True)
# Train parts. All sleeves have .05 radial running clearance on fixed steel posts.
transfer=union(g('transfer',12,.2,0,.4545,0),cyl(*axes['transfer'],.35,-.45,3.3),cyl(*axes['transfer'],.25,2.85,.25))
put('transfer_lower',transfer)
put('transfer_8',union(g('transfer',24,1/3,3.0,.4,.25),cyl(*axes['transfer'],.35,2.85,.55,.25)))
mobile('transfer',['transfer_lower','transfer_8'])
# Variant: retain the first 12 tooth wheel, replace equal pair with 18:24 at same centres.
oldmesh=meshes[1].copy(); meshes[1]['driver_teeth']=18
ph[('transfer',18)]=0;mesh_dummy=len(meshes)
# phase of variant minute gear
th=math.pi; variantphase=((18+24)*th+24*math.pi-math.pi)/24
put('transfer_6',union(gear(18,16/42,axes['transfer'],3.0,.4,0,.25),cyl(*axes['transfer'],.35,2.85,.55,.25)))
meshes[1]=oldmesh
low=cyl(*C,.65,2.9,.55,.35).union(cyl(*C,.55,3.45,.3,.35))
put('minute_lower_8',union(g('minute',24,1/3,3.0,.4,.35),low))
put('minute_lower_6',union(gear(24,16/42,C,3.0,.4,variantphase,.35),low))
tube=cyl(*C,.65,3.45,5.4,.35).cut(cyl(*C,.55,3.44,.31))
tube=union(tube,cyl(*C,.55,8.85,.3,.35),g('minute',12,.2125,3.6,.4,.35),g('minute',36,.225,4.05,.4,.35),cyl(*C,1.2,4.4,.2,.35))
tube=tube.cut(cyl(*C,.55,3.44,.31))
put('minute_upper',tube);mobile('minute',['minute_lower_8','minute_upper','minute_hand'])
hour=union(g('hour',48,.17,4.65,.6,.7),g('hour',24,.2,5.3,.4,.7),cyl(*C,1.2,4.75,3.75,.7),cyl(*C,1.0,8.5,.3,.7))
put('hour_wheel',hour);mobile('hour',['hour_wheel','hour_hand'])
levels={'hour_idle':[(36,.2125,3.6),(12,.17,4.65)], 'A':[(12,.225,4.05),(48,.15,5.75)], 'B':[(12,.15,5.75),(60,.15,6.45)], 'C':[(12,.15,6.45),(12,.2,7.15)], 'day_idle':[(24,.2,5.3),(24,.2,5.95)], 'seconds':[(12,.2,7.15)], 'day':[(48,.2,5.95)]}
for n,gg in levels.items():
 p=axes[n];bottom=gg[0][2];top=gg[-1][2]+.4
 if n in ['seconds','day']:top=8.15
 s=cyl(*p,(.8 if n in ['seconds','day'] else .65),bottom,top-bottom,.4)
 if n=='A':
  put('A_lower',union(g(n,12,.225,4.05,.4,.4),cyl(*p,.6,4.05,1.5,.4),cyl(*p,.5,5.55,.15,.4)))
  put('A_upper',union(g(n,48,.15,5.75,.4,.4),cyl(*p,.6,5.55,.6,.4)).cut(cyl(*p,.5,5.54,.16)))
  mobile(n,['A_lower','A_upper']);continue
 if n=='hour_idle':
  put('hour_idle_lower',union(cyl(*p,.75,3.6,.85,.55),cyl(*p,.65,4.45,.15,.55),g(n,36,.2125,3.6,.4,.55)))
  put('hour_idle_upper',union(cyl(*p,.75,4.45,.8,.55),g(n,12,.17,4.65,.6,.55)).cut(cyl(*p,.65,4.44,.16)))
  mobile(n,['hour_idle_lower','hour_idle_upper']);continue
 else:
  for N,m,z in gg:s=s.union(g(n,N,m,z,.4,.4))
 if n in ['seconds','day']:s=union(s,cyl(*p,.65,top,.3,.4),cyl(*p,.95,7.5,.2,.4))
 put(n+'_wheel',s);mobile(n,[n+'_wheel']+([n+'_hand'] if n in ['seconds','day'] else []))
# Fixed keepers fit over the post ends and seat on the end faces.
for n,top in [('A',6.2),('B',6.9),('C',7.6),('day_idle',6.4)]:
 put(n+'_keeper',cyl(*axes[n],.75,top,.2),True)

# Closed dial with close-fitting staff apertures and a long hour bearing.
dial=union(cyl(*C,12.65,7.8,.3),cyl(*C,1.5,5.75,2.05))
dial=dial.cut(cyl(*C,1.25,5.74,2.5))
for n in ['seconds','day']:dial=dial.cut(cyl(*axes[n],.85,7.79,.32))
put('dial',dial,True)
def hand(n,p,z,rhole,length,angle):
 s=union(cyl(*p,(1.4 if n=='hour_hand' else 1.1),z,.3),boxlink(p,(p[0]+length*math.cos(angle),p[1]+length*math.sin(angle)),.45,z,.3))
 s=s.cut(cyl(*p,rhole,z-.01,.32));put(n,s)
hand('minute_hand',C,8.85,.55,6,0)
hand('hour_hand',C,8.5,1.0,5.5,math.pi/2)
hand('seconds_hand',axes['seconds'],8.15,.65,5,0)
hand('day_hand',axes['day'],8.15,.65,3.2,-math.pi/2)
mov=dict(barrel='BR-096-30',case_centre=list(C),fixed=fixed,mobiles=mobs,meshes=meshes,hands={n:dict(mobile=('day' if n=='day' else n),part=n+'_hand') for n in ['hour','minute','seconds','day']})
json.dump(mov,open(D+'/movement.json','w'),indent=2)
v=json.loads(json.dumps(mov));v['mobiles']['transfer']['parts']=['transfer_lower','transfer_6'];v['mobiles']['minute']['parts'][0]='minute_lower_6';v['meshes'][1]['driver_teeth']=18
json.dump(v,open(D+'/variant_6h.json','w'),indent=2)
# All paths use vertical translations in 0.15 mm increments.
order=['lower_frame','barrel','centre_bridge','transfer_lower','upper_frame','transfer_8','transfer_bridge','minute_lower_8','hour_idle_post','hour_idle_lower','minute_upper','hour_idle_upper','hour_idle_bridge','A_lower','hour_wheel','A_upper','A_keeper','B_bracket','B_wheel','B_keeper','day_idle_bracket','day_idle_wheel','day_idle_keeper','day_wheel','C_bracket','C_wheel','C_keeper','seconds_bracket','seconds_wheel','dial','hour_hand','minute_hand','seconds_hand','day_hand']
assert set(order)==set(fixed+[p for m in mobs.values() for p in m['parts']]+['barrel'])
paths={}
for n in order:
 # At +30 the entire part is above the expanded movement bounding box.
 paths[n]=[[[1,0,0,0],[0,1,0,0],[0,0,1,30*(200-i)/200],[0,0,0,1]] for i in range(201)]
json.dump(dict(order=order,paths=paths),open(D+'/assembly.json','w'))
json.dump(dict(parts={n:'not_tested' for n in ['P1','P2','P3','P4']},height_mm=10.05),open(D+'/report.json','w'),indent=2)
# Save nominal bounds and solids for optional diagnostics outside the archived script.
print('FINISHED',len(shapes))
