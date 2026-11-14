import numpy as np, trimesh, json, manifold3d as m3
import sys
W=float(sys.argv[1]) if len(sys.argv)>1 else 1.6   # wall
FL=float(sys.argv[2]) if len(sys.argv)>2 else 1.6  # floor
def box(x0,x1,y0,y1,z0,z1):
    return m3.Manifold.cube((x1-x0,y1-y0,z1-z0)).translate((x0,y0,z0))
def cyl(r,h,x,y,z,seg=64):
    return m3.Manifold.cylinder(h,r,r,seg).translate((x,y,z))
X0,X1,Y0,Y1=-1.5,72.5,0,45
ZF=-6.8; ZT=12.1
outer=box(X0-W,X1+W,Y0-W,Y1+W,ZF-FL,ZT)
cav=box(X0,X1,Y0,Y1,ZF,ZT+1)
base=outer-cav
mg=0.15
# J1 hole
base=base-box(X0-W-1,X0+0.01,16.25-mg,28.75+mg,-0.25-mg,6.75+mg)
# J2 hole (cylinder along x)
c=m3.Manifold.cylinder(W+1,4+mg,4+mg,64).rotate((0,90,0)).translate((X1-0.01,12,-2.5))
base=base-c
# J3 hole: B at x offset 19, B y offset 1, z offset -4.6
BX,BY,BZ=19,1,-4.6
base=base-box(BX+25-mg,BX+38+mg,Y0-W-1,Y0+0.01,BZ+1.2-mg,BZ+4.2+mg)
# pins
for (px,py) in [(3.5,3.5),(66.5,3.5),(3.5,41.5),(66.5,41.5)]:
    base=base+cyl(1.5,1.2-ZF+0.2,px,py,ZF-0.2)
mesh=base.to_mesh()
tm=trimesh.Trimesh(mesh.vert_properties[:,:3],mesh.tri_verts)
tm.export('work/base.stl')
lx0,lx1,ly0,ly1=X0-W,X1+W,Y0-W,Y1+W
lid=trimesh.creation.box(extents=(lx1-lx0,ly1-ly0,2.0))
lid.apply_translation(((lx0+lx1)/2,(ly0+ly1)/2,ZT+1.0))
lid.export('work/lid.stl')
def T(x,y,z):
    M=np.eye(4);M[:3,3]=(x,y,z);return M
def path(final,up=31,step=0.49):
    n=int(np.ceil(up/step)); P=[]
    for i in range(n,-1,-1):
        M=final.copy();M[2,3]+=min(i*step,up) if i<n else up;P.append(M.tolist())
    return P
# fix: descend evenly
def path(final,up=31,step=0.49):
    n=int(np.ceil(up/step)); P=[]
    for i in range(n,-1,-1):
        M=final.copy();M[2,3]+=up*i/n;P.append(M.tolist())
    return P
fin={'B':T(BX,BY,BZ),'A':T(0,0,0),'battery':T(20.5,7,1.6),'speaker':T(11,9.5,1.6),'lid':np.eye(4)}
asm={'order':['B','A','battery','speaker'],'paths':{k:path(v) for k,v in fin.items()}}
json.dump(asm,open('work/assembly.json','w'))
