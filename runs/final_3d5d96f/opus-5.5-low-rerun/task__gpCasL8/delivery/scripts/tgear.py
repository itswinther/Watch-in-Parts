import manifold3d as m3, numpy as np
from gear import *
def cs(pts): return m3.CrossSection([pts.tolist()])
def test(z1,z2,m,delta=0.02,dd=0.0):
    a=(z1+z2)*m/2+dd
    ph1=0.3
    ph2=mesh_phase(z1,m,ph1,(0,0),z2,(a,0))
    worst=9
    for t in np.linspace(0,2*np.pi/z1,40):
        g1=cs(gear_pts(z1,m,ph1+t,delta))
        g2=cs(gear_pts(z2,m,ph2-t*z1/z2,delta)).translate([a,0])
        inter=(g1^g2).area()
        # clearance: offset g1 by c and check
        lo,hi=0,0.1
        for _ in range(12):
            c=(lo+hi)/2
            if (g1.offset(c,m3.JoinType.Round)^g2).area()>1e-12: hi=c
            else: lo=c
        worst=min(worst,lo if inter<1e-12 else -inter)
    return worst
for z1,z2,m in [(12,96,0.2),(12,24,0.15),(13,13,0.3),(13,26,0.3),(12,48,1/6),(12,45,0.15)]:
    print(z1,z2,m,round(test(z1,z2,m),4))
