import numpy as np, trimesh, manifold3d as m3
def box(x0,x1,y0,y1,z0,z1):
    return m3.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def cyl(x,y,z0,z1,r,seg=48):
    return m3.Manifold.cylinder(z1-z0,r,r,seg).translate((x,y,z0))
def hcyl(y,z,x0,x1,r,seg=48):
    c=m3.Manifold.cylinder(x1-x0,r,r,seg).rotate((0,90,0)).translate((x0,y,z))
    return c
T=1.6
X0,X1,Y0,Y1,ZB,ZT=-2.0,73.5,-2.0,47.0,-10.25,12.5
FT=ZB+T  # -8.65
base=box(X0,X1,Y0,Y1,ZB,ZT)-box(X0+T,X1-T,Y0+T,Y1-T,FT,ZT+1)
# J1 window (keepout size) through left wall
base-=box(X0-1,X0+T+0.01,16.25,28.75,-0.25,6.75)
# J2 hole
base-=hcyl(12,-2.5,X1-T-0.01,X1+1,4.9)
# battery door opening front wall
DX0,DX1,DZ0,DZ1=8.8,57.4,FT,-0.9
base-=box(DX0,DX1,Y0-1,Y0+T+0.01,DZ0,DZ1)
# posts + pegs
for (px,py) in [(3.5,3.5),(66.5,3.5),(3.5,41.5),(66.5,41.5)]:
    base+=cyl(px,py,FT-0.01,0.0,3.5)
    base+=cyl(px,py,-0.01,1.0,1.45)
# stops
SZ=-1.5
base+=box(7.3,9.0,8,28,FT-0.01,SZ)
base+=box(57.2,58.9,16,28,FT-0.01,SZ)
base+=box(15,45,30.2,31.9,FT-0.01,SZ)
door=box(DX0+0.05,DX1-0.05,Y0,Y0+T,FT+0.05,DZ1-0.05)
def save(m,name):
    mm=m.to_mesh()
    t=trimesh.Trimesh(mm.vert_properties[:,:3],mm.tri_verts)
    t.export(name); print(name,t.volume,t.is_watertight)
    return t
tb=save(base,'work/base.stl'); td=save(door,'work/door.stl')
print('total vol',tb.volume+td.volume)
