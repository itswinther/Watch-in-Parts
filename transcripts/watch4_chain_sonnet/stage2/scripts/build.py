import sys, json, math
sys.path.insert(0,'tools')
import numpy as np, cadquery as cq
from scipy.spatial import ConvexHull
import kernel
M=0.2; PA=math.radians(25); BL=0.03
def inv(a): return math.tan(a)-a
def gear_pts(N, phase):
    rp=M*N/2; rb=rp*math.cos(PA); ra=rp+M; rr=rp-1.25*M
    hp=(math.pi*M/2-BL)/(2*rp)
    def off(r):  # angle of flank at radius r from tooth centre
        return hp-(inv(math.acos(rb/r))-inv(PA))
    r0=max(rb,rr)
    rs=np.linspace(r0,ra,9)
    pts=[]
    for k in range(N):
        c=phase+2*math.pi*k/N
        # right flank rising (angle c-off), tip, left flank descending
        right=[(r,c-off(r)) for r in rs]
        left=[(r,c+off(r)) for r in rs[::-1]]
        seq=[]
        if rr<rb: seq.append((rr,c-off(rb)))
        seq+=right+left
        if rr<rb: seq.append((rr,c+off(rb)))
        # root arc to next tooth
        a1=c+off(r0); a2=phase+2*math.pi*(k+1)/N-off(r0)
        if rr<rb: a1=c+off(rb); a2=phase+2*math.pi*(k+1)/N-off(rb)
        for t in (0.33,0.66): seq.append((rr,a1+(a2-a1)*t))
        pts+=seq
    return [(r*math.cos(a),r*math.sin(a)) for r,a in pts]
def gear(N,cx,cy,z0,z1,phase):
    p=gear_pts(N,phase)
    return cq.Workplane('XY').workplane(offset=z0).polyline(p).close().extrude(z1-z0).translate((cx,cy,0))
def cyl(cx,cy,z0,z1,r):
    return cq.Workplane('XY').workplane(offset=z0).center(cx,cy).circle(r).extrude(z1-z0)

hub=(11.2,8.4)
u=np.array([-0.798,-0.603]); u/=np.linalg.norm(u)
A=np.array(hub)+7.2*u; D=A+2.0*u
al=math.atan2(u[1],u[0])
Z0,Z1=8.6,9.3; P0,P1=9.4,9.9
parts={}
parts['gh']=gear(24,hub[0],hub[1],Z0,Z1,al)
parts['wa']=gear(48,A[0],A[1],Z0,Z1,al+math.pi+math.pi/48)
parts['pa']=gear(10,A[0],A[1],P0,P1,al)
parts['wd']=gear(10,D[0],D[1],P0,P1,al+math.pi+math.pi/10)
parts['arb_a']=(cyl(A[0],A[1],Z0,10.7,0.5).union(cyl(A[0],A[1],10.0,10.35,1.0)).union(cyl(A[0],A[1],10.7,11.0,0.9)))
parts['arb_day']=(cyl(D[0],D[1],P0,11.3,0.5).union(cyl(D[0],D[1],10.0,10.35,1.0)))
arm=cq.Workplane('XY').workplane(offset=11.05).polyline([(0,-0.4),(4.0,-0.3),(4.6,0),(4.0,0.3),(0,0.4)]).close().extrude(0.45)
parts['hand_day']=cyl(0,0,11.05,11.5,1.0).union(arm).translate((D[0],D[1],0))
# cock
pts=[]
for c in [(0,0),tuple(A),tuple(D)]:
    for t in np.linspace(0,2*math.pi,48,endpoint=False): pts.append((c[0]+1.6*math.cos(t),c[1]+1.6*math.sin(t)))
h=ConvexHull(np.array(pts)); poly=[pts[i] for i in h.vertices]
plate=cq.Workplane('XY').workplane(offset=10.4).polyline(poly).close().extrude(0.6)
plate=plate.cut(cyl(A[0],A[1],10.3,11.1,0.58)).cut(cyl(A[0],A[1],10.7,11.1,0.95)).cut(cyl(D[0],D[1],10.3,11.1,0.58))
parts['day_cock']=plate.union(cyl(0,0,7.3,10.4,1.0))
for n,s in parts.items():
    kernel.write_step(f'work/parts/{n}.step',s)
mv=json.load(open('previous/movement.json'))
mv['fixed'].append('day_cock')
mv['mobiles']['hour']['parts'].append('gh')
mv['mobiles']['daymid']={'axis':[float(A[0]),float(A[1])],'parts':['wa','pa','arb_a']}
mv['mobiles']['day']={'axis':[float(D[0]),float(D[1])],'parts':['wd','arb_day','hand_day']}
mv['meshes']+= [{"driver":"hour","driver_teeth":24,"driven":"daymid","driven_teeth":48},
                {"driver":"daymid","driver_teeth":10,"driven":"day","driven_teeth":10}]
mv['hands']['day']={'mobile':'day','part':'hand_day'}
json.dump(mv,open('work/movement.json','w'),indent=1)
print(A,D)
