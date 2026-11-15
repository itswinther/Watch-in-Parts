import sys, json, math, numpy as np
sys.path.insert(0,'/app/tools'); sys.path.insert(0,'/app/work')
import kernel, manifold3d as m3
from check import part, barrel
from spec import *
def rot(man,axis,ph):
    c,s=math.cos(ph),math.sin(ph)
    T=np.array([[c,-s,0,0],[s,c,0,0],[0,0,1,0]],float)
    T[0,3]=axis[0]-(c*axis[0]-s*axis[1]); T[1,3]=axis[1]-(s*axis[0]+c*axis[1])
    return man.transform(T.tolist())
def slab(man,z0,z1):
    b=m3.Manifold.cube([100,100,z1-z0],center=False).translate([-50,-50,z0])
    return man^b
mv=json.load(open(sys.argv[1]))
L=LAYERS
# (driver part, driver z-range, driver axis name, driven part, range, teeth1, teeth2)
def axis(m): return mv['mobiles'][m]['axis']
owner={}
for mn,m in mv['mobiles'].items():
    for p in m['parts']: owner[p]=mn
dmap={'M_din':'M_din','M_din6':'M_din6'}
din='M_din6' if 'M_din6' in owner else 'M_din'; ic='I_c6' if 'I_c6' in owner else 'I_c'
pairs=[('barrel',(0,0.4545),'I_shaft',(0,0.4545)),(ic,L['C'],din,L['C']),('M_dd',L['A'],'X1',L['A']),('X1',L['B'],'X2',L['B']),
 ('X2',L['C'],'X3',L['C']),('X3',L['D'],'S_shaft',L['D']),('M_p',L['B'],'J',L['B']),('J',L['D'],'H_tube',L['D']),('H_tube',L['D'],'K',L['D']),('K',L['B'],'D_shaft',L['B'])]
for me,(a,ra,b,rb) in zip(mv['meshes'],pairs):
    z1,z2=me['driver_teeth'],me['driven_teeth']
    A=barrel(mv['barrel']) if a=='barrel' else part(a); B=part(b)
    ax1=[0,0] if a=='barrel' else axis(owner[a]); ax2=axis(owner[b])
    A=slab(A,*ra); B=slab(B,*rb)
    worst=9; ov=0
    for i in range(16):
        ph=i/16*2*math.pi/z1
        A2=rot(A,ax1,ph); B2=rot(B,ax2,-ph*z1/z2)
        v=kernel.ivol(A2,B2); ov=max(ov,v)
        worst=min(worst,0 if v>1e-6 else A2.min_gap(B2,0.3))
    print(a,b,z1,z2,'overlap max',round(ov,5),'min gap',round(worst,4))
