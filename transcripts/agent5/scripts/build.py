import json, numpy as np, trimesh
from manifold3d import Manifold, CrossSection

def box(x0,x1,y0,y1,z0,z1):
    return Manifold.cube([x1-x0,y1-y0,z1-z0]).translate([x0,y0,z0])

X0,X1,Y0,Y1,Z0,Z1 = -2.0,73.5,-2.0,47.0,-10.25,12.5
FT = -8.55            # floor top / door top / battery bottom
XI0,XI1,YI0,YI1 = -0.4,71.9,-0.4,45.4
BX,BY = 9.5,5.5       # battery origin
DX0,DX1,DY0,DY1 = BX-1.6,BX+48+1.6,BY-1.6,BY+30+1.6   # door
G=0.2

base = box(X0,X1,Y0,Y1,Z0,Z1) - box(XI0,XI1,YI0,YI1,FT,Z1+1)
# posts
for (px,py) in [(3.5,3.5),(3.5,41.5),(66.5,3.5),(66.5,41.5)]:
    x0,x1 = (XI0-0.1,6.0) if px<35 else (63.8,69.6)
    y0,y1 = (YI0-0.1,6.0) if py<22 else (39.0,YI1+0.1)
    base += box(x0,x1,y0,y1,FT-0.1,0.0)
# battery ribs (overhang the door margin)
RT=-3.0; RB=FT+0.05
def rib(x0,x1,y0,y1, fx0,fx1,fy0,fy1):
    # upper part everywhere, lower part only over the floor region
    return box(x0,x1,y0,y1,RB,RT) + box(fx0,fx1,fy0,fy1,FT-0.1,RT)
e=0.3
base += rib(BX-e-3.3,BX-e,16,24,  BX-e-3.3,DX0-G,16,24)
base += rib(BX+48+e,BX+48+e+3.3,20,28,  DX1+G,BX+48+e+3.3,20,28)
base += rib(29,37,BY-e-3.3,BY-e,  29,37,BY-e-3.3,DY0-G)
base += rib(29,37,BY+30+e,BY+30+e+3.3,  29,37,DY1+G,BY+30+e+3.3)
# PCB +X locator
base += box(70.4,XI1+0.1,26,34,FT-0.1,0.9)
# door opening
base -= box(DX0-G,DX1+G,DY0-G,DY1+G,Z0-1,FT+0.01)
# J1 hole
base -= box(X0-1,XI0+0.1,16.2,28.8,-0.3,6.8)
# J2 hole
circ = CrossSection.circle(4.05,96)
rect = CrossSection.square([7.0,7.0]).translate([-3.5,-3.0])  # y' -3.5..3.5, z' -3..4  (z -5.5..1.5)
prof = circ + rect   # coords (y-12, z+2.5)
hole = Manifold.extrude(prof,5.0)  # along local z
# map local (u,v,w) -> world (x=w, y=u, z=v)
hole = hole.transform([[0,0,1,70.0],[1,0,0,12.0],[0,1,0,-2.5]])
base -= hole

door = box(DX0,DX1,DY0,DY1,Z0,FT)

def save(m,fn):
    me=m.to_mesh()
    t=trimesh.Trimesh(np.asarray(me.vert_properties)[:,:3],np.asarray(me.tri_verts),process=False)
    t.export(fn); print(fn,m.volume(),len(t.faces),m.genus())
save(base,'work/base.stl'); save(door,'work/door.stl')
print('total',base.volume()+door.volume())

# ---- assembly
def T(t):
    M=np.eye(4); M[:3,3]=t; return M
def boardpose(th,a,b):
    c,s=np.cos(th),np.sin(th)
    R=np.array([[c,0,s],[0,1,0],[-s,0,c]])
    P=np.array([70.0,0,0])
    M=np.eye(4); M[:3,:3]=R; M[:3,3]=P-R@P+np.array([a,0,b]); return M
bc=np.array([[x,y,z] for x in(-1.5,72.5) for y in(0,45) for z in(-5,12.1)])
def interp(wps,fn,pts,step=0.4):
    out=[fn(*wps[0])]
    for w0,w1 in zip(wps[:-1],wps[1:]):
        w0=np.array(w0,float); w1=np.array(w1,float)
        n=1
        while True:
            ps=[fn(*(w0+(w1-w0)*i/n)) for i in range(n+1)]
            d=max(np.linalg.norm((ps[i+1]-ps[i])[:3,:3]@pts.T+(ps[i+1]-ps[i])[:3,3:4],axis=0).max() for i in range(n))
            if d<=step: break
            n=int(n*max(d/step,1.05))+1
        out+=ps[1:]
    return out
th=np.radians(15); c,s=np.cos(th),np.sin(th); r=2.1
A=1.25
board=interp([(th,A-r*c,1+r*s+50),(th,A-r*c,1+r*s),(th,A,1.0),(0,A,1.0),(0,0,1.0),(0,0,0)],boardpose,bc)
board[-1]=np.eye(4)
def lin(p0,p1,n):
    return [T(np.array(p0)+(np.array(p1)-np.array(p0))*i/n) for i in range(n+1)]
lid=lin([0,0,40],[0,0,0],100); lid[-1]=np.eye(4)
bat=lin([BX,BY,FT-45],[BX,BY,FT],113)
dr=lin([0,0,-40],[0,0,0],100); dr[-1]=np.eye(4)
json.dump({k:[m.tolist() for m in v] for k,v in dict(board=board,lid=lid,battery=bat,door=dr).items()},open('work/assembly.json','w'))
print({k:len(v) for k,v in dict(board=board,lid=lid,battery=bat,door=dr).items()})
