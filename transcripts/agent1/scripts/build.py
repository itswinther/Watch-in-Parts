import json, math, numpy as np, manifold3d as m3, trimesh
M = m3.Manifold
def box(lo, hi):
    return M.cube([hi[i]-lo[i] for i in range(3)]).translate(lo)
def save(man, path):
    me = man.to_mesh()
    trimesh.Trimesh(np.array(me.vert_properties)[:, :3], np.array(me.tri_verts)).export(path)

ZF0, ZF1 = -8.6, -7.0        # floor
ZTOP = 12.5
BX, BY, BZ = 9.5, 7.5, -8.6  # battery origin
outer = box((-2, -2, ZF0), (73.5, 47, ZTOP))
cav = box((-0.4, -0.4, ZF1), (71.9, 45.4, ZTOP + 1))
base = outer - cav
# battery opening in floor
base -= box((BX-0.2, BY-0.2, ZF0-1), (BX+48.2, BY+30.2, ZF1+1))
# corner bosses under the PCB holes
for sx, sy in ((0, 0), (1, 0), (0, 1), (1, 1)):
    x0, x1 = (-0.5, 5.5) if sx == 0 else (64.5, 72.0)
    y0, y1 = (-0.5, 5.5) if sy == 0 else (39.5, 45.5)
    base += box((x0, y0, ZF1-0.1), (x1, y1, 0.0))
# +X locating block
base += box((70.4, 20, -1.0), (72.0, 30, 1.4))
# J1 slot (-X wall)
base -= box((-3, 16.25, -0.25), (0.0, 28.75, 7.5))
# J2 slot (+X wall) + keep-out circle
base -= box((71, 8.5, -5.5), (74.5, 15.5, 2.8))
cyl = M.cylinder(4.0, 4.05, 4.05, 96).rotate([0, 90, 0]).translate([71, 12, -2.5])
base -= cyl
save(base, 'work/base.stl')

door = box((BX-2.6, BY-2.6, -10.25), (BX+48+2.6, BY+30+2.6, -8.65))
save(door, 'work/door.stl')
print('vol', base.volume(), door.volume(), base.volume()+door.volume())

def T(dx=0, dy=0, dz=0):
    A = np.eye(4); A[:3, 3] = (dx, dy, dz); return A
def Ry(th, px, pz):
    c, s = math.cos(th), math.sin(th)
    A = np.eye(4); A[0, 0] = c; A[0, 2] = s; A[2, 0] = -s; A[2, 2] = c
    A[0, 3] = px - (c*px + s*pz); A[2, 3] = pz - (-s*px + c*pz)
    return A
def lin(a, b, step=0.45):
    n = max(1, int(math.ceil(np.linalg.norm(np.array(b)-np.array(a))/step)))
    return [tuple(np.array(a) + (np.array(b)-np.array(a))*i/n) for i in range(1, n+1)]

# board: reverse path from final
LIFT, SH, TH = 2.0, 1.2, math.radians(16)
rev = [np.eye(4)]
for p in lin((0, 0, 0), (0, 0, LIFT)): rev.append(T(*p))
for p in lin((0, 0, LIFT), (SH, 0, LIFT)): rev.append(T(*p))
base_T = T(SH, 0, LIFT)
px, pz = 70 + SH, LIFT
nrot = int(math.ceil(TH / 0.0055))
for i in range(1, nrot+1):
    rev.append(Ry(TH*i/nrot, px, pz) @ base_T)
R = Ry(TH, px, pz) @ base_T
for p in lin((0, 0, 0), (-3.5, 0, 0)): rev.append(T(*p) @ R)
for p in lin((-3.5, 0, 0), (-3.5, 0, 45)): rev.append(T(*p) @ R)
board = rev[::-1]
lid = [T(0, 0, z) for z in np.linspace(35, 0, 80)]
bat = [T(BX, BY, BZ + z) for z in np.linspace(-40, 0, 90)]
dr = [T(0, 0, z) for z in np.linspace(-35, 0, 80)]
json.dump({k: [a.tolist() for a in v] for k, v in
           (('board', board), ('lid', lid), ('battery', bat), ('door', dr))}, open('work/assembly.json', 'w'))
print(len(board), 'board poses; battery pose', BX, BY, BZ)
