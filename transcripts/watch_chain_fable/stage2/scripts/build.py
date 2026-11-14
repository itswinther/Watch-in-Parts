import sys,os,json,shutil
sys.path.insert(0,'tools')
import kernel as K, numpy as np, manifold3d as m3
L=lambda n:K.load_part('previous/parts/%s.stl'%n,200000,1<<25,0.005)
C=np.array([9.093266739736606,6.750000000000001])
M=0.2; PA=np.radians(25)
BL=float(os.environ.get('BL','0.015'))

def gear_cs(N,phase,bl=BL,m=M):
    """2D involute gear, a tooth centred at angle phase (rad)."""
    rp=N*m/2; rb=rp*np.cos(PA); ra=rp+m; rr=rp-1.25*m
    inv=lambda a:np.tan(a)-a
    half_p=(np.pi*m/2-bl)/(2*rp)          # half tooth angle at pitch
    pts=[]
    r0=max(rb,rr)
    rs=np.linspace(r0,ra,10)
    def half(r):
        al=np.arccos(min(1,rb/r)); return half_p+inv(PA)-inv(al)
    for k in range(N):
        c=phase+2*np.pi*k/N
        fl=[(r,half(r)) for r in rs]
        seq=[]
        if rr<r0: seq.append((rr,-half(r0)))
        seq+=[(r,-h) for r,h in fl]
        seq+=[(r,h) for r,h in fl[::-1]]
        if rr<r0: seq.append((rr,half(r0)))
        # root arc midpoint to next tooth
        seq.append((rr,np.pi/N))
        for r,a in seq: pts.append((r*np.cos(c+a),r*np.sin(c+a)))
    return m3.CrossSection([pts])

def gear(N,phase,ax,z0,z1,bore=0):
    g=gear_cs(N,phase).extrude(z1-z0).translate([ax[0],ax[1],z0])
    return g
def cyl(ax,z0,z1,r): return K.cyl_z(ax[0],ax[1],z0,z1,r)

# measure hour wheel tooth phase
hw=L('hour_wheel')
p=np.concatenate(hw.slice(7.7).to_polygons())-C
r=np.linalg.norm(p,axis=1); a=np.arctan2(p[:,1],p[:,0])
sel=r>4.8
ph_h=np.angle(np.mean(np.exp(1j*48*a[sel])))/48     # tooth centre angle mod pitch
print('hour phase deg',np.degrees(ph_h))

ang=np.radians(float(os.environ.get('ANG','-90')))
u=np.array([np.cos(ang),np.sin(ang)])
I=C+7.2*u
D=I+6.0*u
print('idler',I,'day',D)
# idler A (24T) meshes hour: gap of A facing C
thA=ang+np.pi  # direction idler->C
# hour tooth position along line from C to I, as offset from a tooth centre in units of pitch
f=((ang-ph_h)/(2*np.pi/48))%1.0      # hour has tooth at ph_h+k*pitch; at 'ang' we are f pitches past a tooth
# A must have at thA: a point (0.5 - f)... mirrored: hour tooth offset +f (ccw) at contact maps to A gap offset -f (in A's ccw sense it is... )
# hour rotating ccw moves tooth +; A rotates cw. Arc position s=f*pitch ccw from line around C  == point displaced perpendicular; around I same point is cw by s.
# so A has a gap centre at thA - f*pitchA  => tooth centre at thA - f*pA + pA/2
pA=2*np.pi/24
phA=thA-f*pA+pA/2
_hm=hw
_best=[]
for _i in range(300):
    _ph=_i*pA/300
    _v=K.ivol(_hm,gear(24,_ph,I,7.1,8.3))
    _best.append(_v)
_b=np.array(_best); _free=_b<1e-9
# centre of the circular free interval
_idx=np.nonzero(_free)[0]
_c=np.angle(np.mean(np.exp(2j*np.pi*_idx/300)))/(2*np.pi)*300
print('analytic phA mod pitch',(phA%pA)/pA*300,'scan centre',_c%300,'free count',len(_idx))
phA=(_c%300)*pA/300
# B (12T) tooth toward D; D (48T) gap toward I
phB=ang
phD=ang+np.pi+np.pi/48
zb=5.75
idler_wheel=gear(24,phA,I,7.1,8.3)
idler_pinion=gear(12,phB,I,5.8,7.0)
idler_arbor=K.union([cyl(I,zb,8.4,0.8),cyl(I,8.3,9.3,0.5)])
day_wheel=gear(48,phD,D,5.8,7.0)
day_arbor=K.union([cyl(D,zb,8.4,0.9),cyl(D,8.3,9.95,0.5)])
# hand pointing +y from D, z 9.45..9.95
hz0,hz1=9.45,9.95
hand=K.union([cyl(D,hz0,hz1,1.0),
   m3.CrossSection([[(-0.45,0),(0.45,0),(0.12,3.6),(-0.12,3.6)]]).extrude(hz1-hz0).translate([D[0],D[1],hz0])])
# bridge
n=np.array([-u[1],u[0]])
mid=(I+D)/2
P1=mid+6.6*n; P2=mid-6.6*n
def bar(a,b,w,z0,z1):
    d=b-a; l=np.linalg.norm(d); t=d/l; nn=np.array([-t[1],t[0]])
    pts=[a+nn*w,a-nn*w,b-nn*w,b+nn*w]
    cs=m3.CrossSection([[tuple(q) for q in pts]])
    if cs.area()<0: cs=m3.CrossSection([[tuple(q) for q in pts[::-1]]])
    return cs.extrude(z1-z0).translate([0,0,z0])
bz0,bz1=8.5,9.3
br=K.union([bar(I,D,1.0,bz0,bz1),bar(P1,P2,1.0,bz0,bz1),cyl(I,bz0,bz1,1.15),cyl(D,bz0,bz1,1.3),
            cyl(P1,5.7,bz1,1.1),cyl(P2,5.7,bz1,1.1)])
br=br-cyl(I,bz0-1,bz1+1,0.58)-cyl(D,bz0-1,bz1+1,0.58)
new={'idler_wheel':idler_wheel,'idler_pinion':idler_pinion,'idler_arbor':idler_arbor,
     'day_wheel':day_wheel,'day_arbor':day_arbor,'day_hand':hand,'day_bridge':br}
doc=json.load(open('previous/movement.json'))
for k,v in new.items():
    K.write_stl('work/parts/%s.stl'%k,v)
doc['fixed'].append('day_bridge')
doc['mobiles']['day_idler']={'axis':[float(I[0]),float(I[1])],'parts':['idler_arbor','idler_wheel','idler_pinion']}
doc['mobiles']['day']={'axis':[float(D[0]),float(D[1])],'parts':['day_arbor','day_wheel','day_hand']}
doc['meshes']+=[{'driver':'hour','driver_teeth':48,'driven':'day_idler','driven_teeth':24},
                {'driver':'day_idler','driver_teeth':12,'driven':'day','driven_teeth':48}]
doc['hands']['day']={'mobile':'day','part':'day_hand'}
json.dump(doc,open('work/movement.json','w'),indent=1)
