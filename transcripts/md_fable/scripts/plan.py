import sys, os, json, heapq
from collections import deque
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools"))
from geometry import core, md
from scipy.spatial.transform import Rotation as Rot

inst = md.flat_one()
def R(axis, deg): return md.rot(axis, deg)[:3, :3]
I3 = np.eye(3)

def pose_anchor(Rm, minc, V):
    """pose with rotation Rm whose AABB min corner is minc"""
    W = V @ Rm.T
    T = np.eye(4); T[:3, :3] = Rm; T[:3, 3] = np.asarray(minc, float) - W.min(axis=0)
    return T

def seg(V, R0, m0, R1, m1, out, lim=4.5):
    """interpolate rotation (geodesic) and AABB min corner; adaptive subdivision"""
    rel = Rot.from_matrix(R0.T @ R1).as_rotvec()
    def P(s):
        Rm = R0 @ Rot.from_rotvec(rel * s).as_matrix()
        return pose_anchor(Rm, (1 - s) * np.asarray(m0, float) + s * np.asarray(m1, float), V)
    def mv(A, B):
        return np.linalg.norm((V @ A[:3, :3].T + A[:3, 3]) - (V @ B[:3, :3].T + B[:3, 3]), axis=1).max()
    n = 1
    while True:
        ps = [P(s) for s in np.linspace(0, 1, n + 1)]
        if max(mv(ps[i], ps[i + 1]) for i in range(n)) <= lim: break
        n = int(n * 1.3) + 1
    if not out: out.append(ps[0])
    out.extend(ps[1:])

def build(name, keys):
    V = core.verts(inst.piece(name))
    out = []
    for (R0, m0), (R1, m1) in zip(keys[:-1], keys[1:]):
        seg(V, R0, m0, R1, m1, out)
    return out, V

paths = {}

# ---------- sofa ----------
S1 = R("x", 90)                 # on its side: 240 along x, 80 along y, 160 up
S2 = R("y", -90) @ S1           # upright: 240 up, footprint 160(x) x 80(y)
V = core.verts(inst.piece("sofa"))
out = []
seg(V, S1, (-300, 633, 0), S1, (330, 633, 0), out)
seg(V, S1, (330, 633, 0), S2, (330, 633, 0), out)
# 2D search for the corner turn: rectangle 160x80, centre (cx,cy), angle th
free = [(320, 700, 595, 720), (575, 700, 300, 720)]
u = np.linspace(-1, 1, 41)
bd = np.concatenate([np.c_[80 * u, 40 + 0 * u], np.c_[80 * u, -40 + 0 * u], np.c_[80 + 0 * u, 40 * u], np.c_[-80 + 0 * u, 40 * u]])
MARG = 1.0
def ok2(cx, cy, th):
    c, s = np.cos(np.radians(th)), np.sin(np.radians(th))
    p = bd @ np.array([[c, s], [-s, c]]) + (cx, cy)
    ins = np.zeros(len(p), bool)
    for x0, x1, y0, y1 in free:
        ins |= (p[:, 0] >= x0 + MARG) & (p[:, 0] <= x1 - MARG) & (p[:, 1] >= y0 + MARG) & (p[:, 1] <= y1 - MARG)
    return ins.all()
DX, DT = 2.5, 2.5
start = (0, 0, 0)   # i -> x=410+DX*i ; j -> y=673-DX*j ; k -> th=DT*k
def st(i, j, k): return (410 + DX * i, 673 - DX * j, -DT * k)
assert ok2(*st(*start))
prev = {start: None}; dq = deque([start]); goal = None
while dq:
    s = dq.popleft()
    x, y, th = st(*s)
    if s[2] == 36 and y <= 520: goal = s; break
    for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
        n = (s[0] + d[0], s[1] + d[1], s[2] + d[2])
        if n in prev or not (0 <= n[2] <= 36): continue
        nx, ny, nt = st(*n)
        if not (400 <= nx <= 700 and 400 <= ny <= 720): continue
        if ok2(nx, ny, nt): prev[n] = s; dq.append(n)
assert goal, "no 2D path"
chain = []
s = goal
while s is not None: chain.append(s); s = prev[s]
chain.reverse()
print("2D path", len(chain), "end", st(*goal))
def pose2d(cx, cy, th):
    Rm = R("z", th) @ S2
    T = np.eye(4); T[:3, :3] = Rm
    W = V @ Rm.T
    c = Rm @ np.array([0, 80, 40.0])
    T[:3, 3] = (cx - c[0], cy - c[1], -W[:, 2].min())
    return T
for s in chain[1:]:
    out.append(pose2d(*st(*s)))
S3 = R("z", -90) @ S2
gx, gy, _ = st(*goal)
m = (gx - 40, gy - 80, 0)
seg(V, S3, m, S3, (600, 100, 0), out)
seg(V, S3, (600, 100, 0), S2, (600, 100, 0), out)
seg(V, S2, (600, 100, 0), S2, (500, 100, 0), out)
seg(V, S2, (500, 100, 0), S1, (500, 100, 0), out)
seg(V, S1, (500, 100, 0), I3, (500, 100, 0), out)
seg(V, I3, (500, 100, 0), I3, (520, 40, 0), out)
paths["sofa"] = out

# ---------- wardrobe ----------
Lx, Ly, Fin = R("y", 90), R("x", 90), R("z", 90)
paths["wardrobe"], _ = build("wardrobe", [
    (Lx, (-300, 650, 0)), (Lx, (30, 650, 0)), (I3, (30, 650, 0)), (I3, (73, 650, 0)),
    (I3, (73, 482, 0)), (Ly, (73, 482, 0)), (Ly, (73, 215, 0)), (I3, (73, 215, 0)),
    (Fin, (73, 215, 0)), (Fin, (25, 210, 0))])

# ---------- bookcase, chest: pure translations ----------
paths["bookcase"], _ = build("bookcase", [(I3, (-200, 640, 0)), (I3, (400, 640, 0)), (I3, (400, 595, 0))])
paths["chest"], _ = build("chest", [(I3, (-200, 650, 0)), (I3, (63, 650, 0)), (I3, (63, 400, 0))])

order = ["sofa", "wardrobe", "bookcase", "chest"]
for n in order:
    P = np.array(paths[n]); P[-1] = inst.final(n)
    paths[n] = P.tolist(); print(n, len(P))
os.makedirs("work", exist_ok=True)
json.dump({"order": order, "paths": paths}, open("work/plan.json", "w"))
