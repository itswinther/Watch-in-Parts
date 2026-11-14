from build import *
import cadquery as cq
npin=load('n_pinion')
# coarse: for each phase, build only wheel ring as manifold from polygon directly (fast)
import manifold3d as m3
def wheelman(phase):
    pts=gear_pts(ND,M,phase)
    cs=m3.CrossSection([[ (x+DX,y+DY) for x,y in pts ]])
    return m3.Manifold.extrude(cs,0.8).translate([0,0,6.6])
pitch=2*math.pi/ND
best=[]
for i in range(48):
    ph=-math.pi/2+pitch*i/48
    w=wheelman(ph)
    best.append((kernel.ivol(w,npin),kernel.min_distance(w,npin,0.5),ph))
for b in best: print(b)
