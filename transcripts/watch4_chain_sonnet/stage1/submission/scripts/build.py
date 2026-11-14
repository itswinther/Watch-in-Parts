import math, json, os, sys
import cadquery as cq
sys.path.insert(0,'tools')
import kernel
D=math.radians
PA=D(25); BL=0.03
def inv(a): return math.tan(a)-a
def gear_pts(z,m,phi,cx,cy,add=1.0):
    r=z*m/2; rb=r*math.cos(PA); ra=r+add*m; rr=r-1.25*m
    s=math.pi*m/2-BL; thp=s/2/r
    def th(rad):
        return thp-(inv(math.acos(rb/rad))-inv(PA))
    pts=[]; pitch=2*math.pi/z
    n=14
    rs=[max(rb,rr)+(ra-max(rb,rr))*i/n for i in range(n+1)]
    for k in range(z):
        c=phi+k*pitch
        rootr=max(rb,rr)
        L=[]; R=[]
        for rad in rs:
            L.append((rad,c-th(rad))); R.append((rad,c+th(rad)))
        seq=[]
        if rr<rb: seq.append((rr,c-th(rb)))
        seq+=L+R[::-1]
        if rr<rb: seq.append((rr,c+th(rb)))
        a0=c+th(rootr); a1=c+pitch-th(rootr)
        for j in (1,2,3):
            seq.append((rr,a0+(a1-a0)*j/4))
        pts+= [(cx+p*math.cos(a),cy+p*math.sin(a)) for p,a in seq]
    return pts
def gear(z,m,phi,cx,cy,z0,z1,bore=None,add=1.0):
    w=cq.Workplane("XY").workplane(offset=z0).polyline(gear_pts(z,m,phi,cx,cy,add)).close().extrude(z1-z0)
    if bore: w=w.cut(cq.Workplane("XY").workplane(offset=z0-1).center(cx,cy).circle(bore).extrude(z1-z0+2))
    return w
def cyl(cx,cy,z0,z1,r,rin=None):
    w=cq.Workplane("XY").workplane(offset=z0).center(cx,cy).circle(r).extrude(z1-z0)
    if rin: w=w.cut(cq.Workplane("XY").workplane(offset=z0-1).center(cx,cy).circle(rin).extrude(z1-z0+2))
    return w
def hand(cx,cy,z0,z1,L,w0,w1,hubr,rin=None,hubz0=None,hubz1=None):
    # points along +y
    b=cq.Workplane("XY").workplane(offset=z0).polyline([(cx-w0/2,cy),(cx+w0/2,cy),(cx+w1/2,cy+L),(cx-w1/2,cy+L)]).close().extrude(z1-z0)
    h=cyl(cx,cy,hubz0 if hubz0 is not None else z0,hubz1 if hubz1 is not None else z1,hubr)
    s=b.union(h)
    if rin: s=s.cut(cq.Workplane("XY").workplane(offset=z0-1).center(cx,cy).circle(rin).extrude(z1-z0+30))
    return s

# axes
P={}
P['barrel']=(0.0,0.0)
P['train1']=(11.2,0.0)
P['minute']=(11.2,8.4)
def pol(c,d,a): return (c[0]+d*math.cos(D(a)),c[1]+d*math.sin(D(a)))
P['hour']=P['minute']
P['motion']=pol(P['minute'],6.6,330)
P['idler']=pol(P['minute'],6.375,150)
P['seconds']=pol(P['idler'],5.85,120)
# gears: name -> mobile, teeth, module, z0,z1
G={
 'p1':('train1',16,0.2,0.1,0.9),
 'w1':('train1',24,0.4,1.2,2.0),
 'g_in':('minute',18,0.4,1.2,2.0),
 's0':('minute',75,0.15,2.2,3.0),
 's1p':('idler',10,0.15,2.2,3.0),
 's1w':('idler',80,0.13,3.2,4.0),
 's2p':('seconds',10,0.13,3.2,4.0),
 'mw':('minute',15,0.22,4.2,5.0),
 'cw':('motion',45,0.22,4.2,5.0),
 'cp':('motion',12,0.22,5.2,6.0),
 'hw':('hour',48,0.22,5.2,6.0),
}
# meshes (driver gear, driven gear); barrel as ('barrel',96)
MESH=[('barrel','p1'),('w1','g_in'),('s0','s1p'),('s1w','s2p'),('mw','cw'),('cp','hw')]
def tz(g): return 96 if g=='barrel' else G[g][1]
def ax(g): return P['barrel'] if g=='barrel' else P[G[g][0]]
phase={'barrel':0.0}
for a,b in MESH:
    if a not in phase and a not in [y for _,y in MESH]: phase[a]=0.3
# propagate
changed=True
while changed:
    changed=False
    for a,b in MESH:
        for x,y in ((a,b),(b,a)):
            if x in phase and y not in phase:
                ax_,ay_=ax(x); bx,by=ax(y)
                al=math.atan2(by-ay_,bx-ax_)
                z1,z2=tz(x),tz(y)
                p1=2*math.pi/z1
                d1=(phase[x]-al)%p1
                if d1>p1/2: d1-=p1
                gap=al+math.pi-d1*z1/z2
                phase[y]=gap+math.pi/z2
                changed=True
def lc(a,b):
    (ax_,ay_),(bx,by)=ax(a),ax(b)
    return math.hypot(ax_-bx,ay_-by)
def mod(g): return 0.2 if g=='barrel' else G[g][2]
for a,b in MESH:
    exp=(tz(a)*mod(a)+tz(b)*mod(b))/2
    assert abs(exp-lc(a,b))<1e-6,(a,b,exp,lc(a,b))
    assert abs(mod(a)-mod(b))<1e-9
parts={}
for n,(mob,z,m,z0,z1) in G.items():
    cx,cy=P[mob]
    parts[n]=gear(z,m,phase[n],cx,cy,z0,z1,bore=0.8 if n=='hw' else None,add=1.0)
# arbors
def arbor(n,mob,zt,flange=None):
    cx,cy=P[mob]; s=cyl(cx,cy,-1.0,zt,0.5)
    if flange: s=s.union(cyl(cx,cy,flange[0],flange[1],flange[2]))
    parts[n]=s
arbor('arb_train1','train1',6.6)
arbor('arb_minute','minute',8.4)
arbor('arb_motion','motion',6.6)
arbor('arb_idler','idler',6.6)
arbor('arb_seconds','seconds',9.0,flange=(5.5,6.0,1.2))
parts['hour_tube']=cyl(*P['minute'],5.2,7.9,1.1,0.6)
mx,my=P['minute']; sx,sy=P['seconds']
parts['hand_hour']=hand(mx,my,7.4,7.9,5.5,1.0,0.5,1.3,rin=0.6)
parts['hand_minute']=hand(mx,my,8.0,8.5,7.5,1.0,0.5,1.0)
parts['hand_seconds']=hand(sx,sy,8.6,9.1,5.6,0.5,0.4,0.9,hubz0=7.4,hubz1=9.1)
# plate & bridge
axes=[P['barrel'],P['train1'],P['minute'],P['motion'],P['idler'],P['seconds']]
def strip(a,b,w,z0,z1):
    dx,dy=b[0]-a[0],b[1]-a[1]; L=math.hypot(dx,dy); ux,uy=dx/L,dy/L; nx,ny=-uy*w/2,ux*w/2
    return cq.Workplane("XY").workplane(offset=z0).polyline([(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),(b[0]-nx,b[1]-ny),(a[0]-nx,a[1]-ny)]).close().extrude(z1-z0)
links=[(0,1),(1,2),(2,3),(2,4),(4,5)]
def slab(z0,z1,r,w):
    s=None
    for a in axes:
        c=cyl(a[0],a[1],z0,z1,r); s=c if s is None else s.union(c)
    for i,j in links: s=s.union(strip(axes[i],axes[j],w,z0,z1))
    return s
plate=slab(-1.8,-0.1,3.0,3.0)
for a in axes: plate=plate.cut(cyl(a[0],a[1],-1.1,0.0,0.6))
bridge=slab(6.1,7.3,2.8,2.6)
bridge=bridge.union(cyl(0,0,1.1,6.2,1.3))
for n in ('train1','idler','motion'):
    bridge=bridge.cut(cyl(*P[n],6.0,6.7,0.6))
bridge=bridge.cut(cyl(0,0,1.0,1.7,0.6))
bridge=bridge.cut(cyl(*P['minute'],6.0,7.4,1.25))
bridge=bridge.cut(cyl(*P['seconds'],6.0,7.4,0.6))
parts['main_plate']=plate; parts['bridge']=bridge
for n,s in parts.items():
    kernel.write_step(f'work/parts/{n}.step',s)
mobs={
 'train1':['p1','w1','arb_train1'],
 'minute':['g_in','s0','mw','arb_minute','hand_minute'],
 'idler':['s1p','s1w','arb_idler'],
 'seconds':['s2p','arb_seconds','hand_seconds'],
 'motion':['cw','cp','arb_motion'],
 'hour':['hw','hour_tube','hand_hour'],
}
mv={"case_centre":[4.98,5.36],"fixed":["main_plate","bridge"],
 "mobiles":{k:{"axis":list(P[k]),"parts":v} for k,v in mobs.items()},
 "meshes":[
  {"driver":"barrel","driver_teeth":96,"driven":"train1","driven_teeth":16},
  {"driver":"train1","driver_teeth":24,"driven":"minute","driven_teeth":18},
  {"driver":"minute","driver_teeth":75,"driven":"idler","driven_teeth":10},
  {"driver":"idler","driver_teeth":80,"driven":"seconds","driven_teeth":10},
  {"driver":"minute","driver_teeth":15,"driven":"motion","driven_teeth":45},
  {"driver":"motion","driver_teeth":12,"driven":"hour","driven_teeth":48}],
 "hands":{"hour":{"mobile":"hour","part":"hand_hour"},"minute":{"mobile":"minute","part":"hand_minute"},"seconds":{"mobile":"seconds","part":"hand_seconds"}}}
json.dump(mv,open('work/movement.json','w'),indent=1)
print('built',len(parts))
