import numpy as np, trimesh, json
import manifold3d as m3
M=m3.Manifold
def box(x0,x1,y0,y1,z0,z1): return M.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def cyl(x,y,z0,z1,r): return M.cylinder(z1-z0,r,r,64).translate((x,y,z0))
ZB=-8.65; ZT=12.5; G=0.05
base=box(-2,73.5,-2,47,ZB,ZT)-box(-0.3,71.8,-0.3,45.3,ZB-1,ZT+1)
# J1 opening + notch (wall -x)
base=base-box(-3,0,16,29,ZB-1,7.0)
# J2 opening + notch (+x wall)
base=base-box(71,74.5,7.9,16.1,ZB-1,1.6)
door=box(-2,73.5,-2,47,-10.25,ZB)
door=door+box(-2,-0.3,16+G,29-G,ZB-.01,-0.5)
door=door+box(71.8,73.5,7.9+G,16.1-G,ZB-.01,-6.6)
for x,y in [(3.5,3.5),(66.5,3.5),(3.5,41.5),(66.5,41.5)]:
    door=door+cyl(x,y,ZB-.01,0,3.5)+cyl(x,y,-0.01,1.5,1.45)
door=door+box(20,40,30.6,32.4,ZB-.01,-1.1)
for n,p in [('base',base),('door',door)]:
    mm=p.to_mesh(); t=trimesh.Trimesh(mm.vert_properties[:,:3],mm.tri_verts)
    t.export(f'work/{n}.stl'); print(n,t.volume,t.is_watertight,t.bounds.tolist())
def T(x,y,z):
    m=np.eye(4); m[:3,3]=[x,y,z]; return m.tolist()
N=80; 
asm={'board':[T(0,0,-0.5*k) for k in range(N,-1,-1)],
 'lid':[T(0,0,0.5*k) for k in range(N,-1,-1)],
 'battery':[T(8.2,0.2,-8.6-0.5*k) for k in range(N,-1,-1)],
 'door':[T(0,0,-0.5*k) for k in range(N,-1,-1)]}
json.dump(asm,open('work/assembly.json','w'))
