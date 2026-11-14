import sys, json, numpy as np
sys.path.insert(0, 'tools')
from geometry.core import box, union, write_stl

W = 1.6
X0, X1, Y0, Y1, Z0, Z1 = -2.0, 73.5, -2.0, 47.0, -10.25, 12.5
FL = Z0 + W            # floor top -8.65
outer = box((X0, Y0, Z0), (X1, Y1, Z1))
cav = box((-0.4, -0.4, FL), (X1 - W, 45.4, Z1 + 1))
base = outer - cav
# J1 window (-X wall), J2 window (+X wall)
base -= box((X0 - 1, 16.2, -0.3), (0.0, 28.8, 6.8))
base -= box((X1 - W - 0.5, 7.95, -6.55), (X1 + 1, 16.05, 1.55))
# door opening in -Y wall
DX0, DX1, DZ0, DZ1 = 8.0, 57.0, FL, -0.95
base -= box((DX0, Y0 - 1, DZ0), (DX1, 0.0, DZ1))
adds = []
LT, LB = -0.02, -2.02
for (ya, yb) in ((-0.5, 6.5), (38.5, 45.5)):
    adds.append(box((-0.5, ya, LB), (6.5, yb, LT)))
    adds.append(box((60.5, ya, LB), (72.0, yb, LT)))
    adds.append(box((70.4, ya, LB), (72.0, yb, 0.6)))     # +X stop
# battery ribs (battery x 8.5..56.5, y 0..30)
RH = FL + 2.0
adds.append(box((6.1, 8, FL - 0.1), (8.1, 22, RH)))
adds.append(box((56.9, 8, FL - 0.1), (58.9, 22, RH)))
adds.append(box((22, 30.4, FL - 0.1), (42, 32.4, RH)))
base = union([base] + adds)
door = box((DX0 + 0.1, Y0, DZ0 + 0.1), (DX1 - 0.1, -0.4, DZ1 - 0.1))
write_stl('work/base.stl', base); write_stl('work/door.stl', door)
print('vol', base.volume(), door.volume(), base.volume() + door.volume(), base.num_tri())

def T(dx=0, dy=0, dz=0, th=0.0, piv=(0, 0)):
    # rotate about Y-parallel axis through (piv x, piv z) : left end up for th>0, then translate
    c, s = np.cos(th), np.sin(th)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    p = np.array([piv[0], 0, piv[1]])
    M = np.eye(4); M[:3, :3] = R; M[:3, 3] = p - R @ p + np.array([dx, dy, dz])
    return M

def lin(a, b, step):
    n = max(1, int(np.ceil(np.linalg.norm(np.array(b) - np.array(a)) / step)))
    return [tuple(np.array(a) + (np.array(b) - np.array(a)) * i / n) for i in range(1, n + 1)]

# board, built backwards from final
h, s, TH = 0.7, 1.3, np.radians(20)
rev = [T()]
for p in lin((0, 0), (0, h), 0.45): rev.append(T(p[0], 0, p[1]))
for p in lin((0, h), (s, h), 0.45): rev.append(T(p[0], 0, p[1]))
K = (70.0, 1.6)   # local pivot: PCB top right edge
nrot = 70
for i in range(1, nrot + 1):
    rev.append(T(s, 0, h) @ T(th=TH * i / nrot, piv=K))
ax = np.array([-np.cos(TH), np.sin(TH)])
base_pose = T(s, 0, h) @ T(th=TH, piv=K)
d = 8.0
for p in lin((0, 0), tuple(ax * d), 0.45): rev.append(T(p[0], 0, p[1]) @ base_pose)
o = ax * d
for p in lin(tuple(o), (o[0], o[1] + 40), 0.45): rev.append(T(p[0], 0, p[1]) @ base_pose)
board = rev[::-1]
lid = [T(0, 0, z) for z in np.linspace(35, 0, 80)]
bf = np.array([8.5, 0.0, FL + 0.05])
batt = [T(bf[0], y, bf[2]) for y in np.linspace(-36, 0, 82)]
doorp = [T(0, y, 0) for y in np.linspace(-32, 0, 72)]
json.dump({"board": [m.tolist() for m in board], "lid": [m.tolist() for m in lid],
           "battery": [m.tolist() for m in batt], "door": [m.tolist() for m in doorp]}, open('work/assembly.json', 'w'))
print(len(board), len(lid), len(batt), len(doorp))
