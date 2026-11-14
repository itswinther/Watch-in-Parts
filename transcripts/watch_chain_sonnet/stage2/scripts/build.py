import sys,json,math,shutil,numpy as np
sys.path.insert(0,'tools')
import kernel as k, manifold3d as m3
M=0.2; PA=math.radians(25)
def inv(a): return math.tan(a)-a
def gear2d(N,phase,backlash=0.03,pts=10):
    r=N*M/2; rb=r*math.cos(PA); ra=r+M; rr=r-1.25*M
    half_p=(math.pi*M/2-backlash)/(2*r)   # half angle at pitch
    def half(rho):
        a=math.acos(min(1,rb/rho)); return half_p-(inv(a)-inv(PA))
    r0=max(rb,rr+1e-6)
    rhos=np.linspace(r0,ra,pts)
    poly=[]
    for t in range(N):
        c=phase+2*math.pi*t/N
        right=[(rho,c-half(rho)) for rho in rhos]
        left=[(rho,c+half(rho)) for rho in rhos[::-1]]
        seq=[(rr,right[0][1])]+right+left+[(rr,left[-1][1])]
        for rho,a in seq: poly.append((rho*math.cos(a),rho*math.sin(a)))
    return np.array(poly)
def gear(N,phase,z0,z1,cx,cy,bore=0):
    cs=m3.CrossSection([gear2d(N,phase)])
    g=cs.extrude(z1-z0) if hasattr(cs,'extrude') else None
    g=m3.Manifold.extrude(cs.to_polygons(),z1-z0) if g is None else g
    g=g.translate([cx,cy,z0])
    return g
def cyl(cx,cy,z0,z1,r): return k.cyl_z(cx,cy,z0,z1,r,96)
if __name__=='__main__':
    th=math.radians(float(sys.argv[1]) if len(sys.argv)>1 else 45)
    mv=json.load(open('previous/movement.json'))
    T=np.array(mv['mobiles']['T']['axis'])
    R=0.1*(12+96)
    D=T+R*np.array([math.cos(th),math.sin(th)])
    # T add-on
    tg=gear(12,th,6.05,6.55,*T)
    tadd=k.union([tg,cyl(*T,5.8,6.1,0.5)])
    # D body
    dw=gear(96,th+math.pi+math.pi/96,6.05,6.55,*D)
    dbody=k.union([cyl(*D,-1.3,-0.7,1.0),cyl(*D,-0.7,0.0,0.5),cyl(*D,0,0.5,1.0),cyl(*D,0,6.7,0.5),dw,cyl(*D,6.0,6.6,1.0)])
    # hand: pointer from hub toward angle 90deg
    L=4.5
    hub=cyl(*D,6.6,7.0,1.0)
    ptr=k.box([D[0]-0.4,D[1],6.6],[D[0]+0.4,D[1]+L,7.0])
    tip=k.union([ptr,hub])
    plate=k.load_part('previous/parts/main_plate.stl',200000,1<<25,1e-3)
    plate=plate-cyl(*D,-1,1,0.6)
    # keep original hole fill? plate hole cutter only
    k.write_stl('work/parts/T_top.stl',tadd)
    k.write_stl('work/parts/D_body.stl',dbody)
    k.write_stl('work/parts/hand_day.stl',tip)
    k.write_stl('work/parts/main_plate.stl',plate)
    doc=json.load(open('previous/movement.json'))
    doc['mobiles']['T']['parts'].append('T_top')
    doc['mobiles']['D']={'axis':[float(D[0]),float(D[1])],'parts':['D_body','hand_day']}
    doc['meshes'].append({'driver':'T','driver_teeth':12,'driven':'D','driven_teeth':96})
    doc['hands']['day']={'mobile':'D','part':'hand_day'}
    json.dump(doc,open('work/movement.json','w'),indent=1)
    print(D)
