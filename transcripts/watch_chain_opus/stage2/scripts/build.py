import sys,json,shutil,os; sys.path.insert(0,'tools'); sys.path.insert(0,'scripts')
import kernel as K, numpy as np, gear, manifold3d as m3
def L(n): return K.load_part(f'previous/parts/{n}.stl',200000,1<<25,.005)
H=np.array([9.247085729384876,5.79555495773441])
th=np.radians(-120); I=H+7.2*np.array([np.cos(th),np.sin(th)])
ph2=np.radians(-90); D=I+6.0*np.array([np.cos(ph2),np.sin(ph2)])
P=D+np.array([-6.0,0.0])
print('I',I,'D',D,'P',P,'|D-H|',np.linalg.norm(D-H))
hw=L('h_wheel')
def best_phase(mk, other, n):
    pitch=2*np.pi/n; phs=np.linspace(0,pitch,61)[:-1]
    v=[K.ivol(mk(p),other) for p in phs]
    v=np.array(v); ok=v<1e-6
    # centre of the longest run of ok (circular)
    best=None; idx=np.where(ok)[0]
    if len(idx)==0: return phs[v.argmin()],v.min()
    # circular run finding
    runs=[];cur=[]
    for k in range(2*len(phs)):
        if ok[k%len(phs)]: cur.append(k)
        else:
            if cur: runs.append(cur); cur=[]
    if cur: runs.append(cur)
    r=max(runs,key=len); c=(r[0]+r[-1])/2
    return (c%len(phs))*pitch/len(phs), 0
Z=dict(pl=5.7, g1=(5.8,6.6), g2=(6.7,7.5), br=(7.6,8.4))
# idler wheel A=24 at z g2 meshing hour wheel
mkA=lambda p: gear.gear(24,*I,*Z['g2'],phase=p)
pA,_=best_phase(mkA,hw,24); print('phase A',pA)
idA=gear.gear(24,*I,*Z['g2'],phase=pA)
idB0=lambda p: gear.gear(12,*I,*Z['g1'],phase=p)
pB=0.0
idB=idB0(pB)
mkC=lambda p: gear.gear(48,*D,*Z['g1'],phase=p)
pC,_=best_phase(mkC,idB,48); print('phase C',pC)
dC=mkC(pC)
ARB=0.5
id_arbor=K.cyl_z(*I,5.75,8.7,ARB)
d_arbor=K.cyl_z(*D,5.75,10.1,ARB)
d_collar=K.cyl_z(*D,7.0,7.5,1.0)
# day hand: hub + bar pointing +y, z 9.8-10.1
hz=(9.8,10.1)
hand=K.union([K.cyl_z(*D,*hz,0.8), K.box([D[0]-0.2,D[1]-1.2,hz[0]],[D[0]+0.2,D[1]+5.3,hz[1]]),
              K.cyl_z(D[0],D[1]+5.3,*hz,0.2)])
# bridge: bars I-D and D-P at z br, with holes; pillar at P down to plate
def bar(a,b,w,z0,z1):
    cs=m3.CrossSection.circle(w,48).translate(list(a)) + m3.CrossSection.circle(w,48).translate(list(b))
    return m3.Manifold.extrude(cs.hull(), z1-z0).translate([0,0,z0])
br=K.union([bar(I,D,1.2,*Z['br']), bar(D,P,1.2,*Z['br']), K.cyl_z(*P,5.7,Z['br'][0]+0.01,0.9)])
br=br-K.cyl_z(*I,5,9,0.55)-K.cyl_z(*D,5,11,0.55)
out='work/parts'
parts=dict(idler_wheel=idA,idler_pinion=idB,idler_arbor=id_arbor,day_wheel=dC,day_arbor=d_arbor,day_collar=d_collar,day_hand=hand,day_bridge=br)
for n,m in parts.items():
    assert len(m.decompose())==1,n
    K.write_stl(f'{out}/{n}.stl',m)
d=json.load(open('previous/movement.json'))
d['fixed'].append('day_bridge')
d['mobiles']['idler']={'axis':[float(I[0]),float(I[1])],'parts':['idler_arbor','idler_wheel','idler_pinion']}
d['mobiles']['day']={'axis':[float(D[0]),float(D[1])],'parts':['day_arbor','day_wheel','day_collar','day_hand']}
d['meshes']+= [{'driver':'hour','driver_teeth':48,'driven':'idler','driven_teeth':24},
               {'driver':'idler','driver_teeth':12,'driven':'day','driven_teeth':48}]
d['hands']['day']={'mobile':'day','part':'day_hand'}
json.dump(d,open('work/movement.json','w'),indent=1)
