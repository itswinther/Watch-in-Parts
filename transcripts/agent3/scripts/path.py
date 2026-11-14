import sys, os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from geometry import bodies as B
from geometry.core import apply, verts, ivol, load_part

P0 = np.array([70.0, 0.0, 1.6])

def pose(x, z, phi):
    c, s = np.cos(phi), np.sin(phi)
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    T = np.eye(4); T[:3, :3] = R
    T[:3, 3] = P0 + np.array([x, 0, z]) - R @ P0
    return T

def densify(keys, V, maxstep=0.45):
    """keys: list of (x,z,phi). Linear interp in params, subdivided so vertices move <= maxstep."""
    out = [pose(*keys[0])]
    for a, b in zip(keys[:-1], keys[1:]):
        a, b = np.array(a, float), np.array(b, float)
        n = 1
        while True:
            Ps = [pose(*(a + (b - a) * k / n)) for k in range(n + 1)]
            W = [V @ P[:3, :3].T + P[:3, 3] for P in Ps]
            st = max(np.linalg.norm(W[i + 1] - W[i], axis=1).max() for i in range(n))
            if st <= maxstep: break
            n = int(np.ceil(n * st / maxstep)) + 1
        out += Ps[1:]
    return out

def line(T0, d, n):
    out = []
    for k in range(1, n + 1):
        T = T0.copy(); T[:3, 3] += np.asarray(d) * k / n; out.append(T)
    return out

def board_keys(h, s, phi, dx, up):
    # forward order
    return [(s - dx, up, phi), (s - dx, h, phi), (s, h, phi), (s, h, 0.0), (0, h, 0.0), (0, 0, 0.0)]

def main():
    h, s, phi_deg, dx = 0.9, 1.5, 20.0, 2.5
    args = sys.argv[1:]
    if args: h, s, phi_deg, dx = map(float, args[:4])
    base = load_part(os.path.join(ROOT, "work", "base.stl"), 200000, 64 << 20, 0.005)
    board = B.board()
    V = verts(board)
    bp = densify(board_keys(h, s, np.radians(phi_deg), dx, 40.0), V)
    worst = max(((ivol(apply(board, P), base), i) for i, P in enumerate(bp)))
    print("board poses", len(bp), "worst", worst)
    bad = [(i, round(ivol(apply(board, P), base), 3)) for i, P in enumerate(bp) if ivol(apply(board, P), base) > 0.05]
    print("bad", bad[:40])
    # lid: straight down from +31
    lid = [np.eye(4) for _ in range(1)]
    lid = line(np.eye(4) + np.diag([0, 0, 0, 0]), [0, 0, 0], 0)
    T = np.eye(4); T[2, 3] = 31.0
    lid = [T] + line(T, [0, 0, -31.0], 70)
    # battery: from +X
    Tb = np.eye(4); Tb[:3, 3] = [20.0 + 54.0, 15.35, 3.3]
    bat = [Tb] + line(Tb, [-54.0, 0, 0], 120)
    Td = np.eye(4); Td[0, 3] = 54.0
    door = [Td] + line(Td, [-54.0, 0, 0], 120)
    door[-1] = np.eye(4); lid[-1] = np.eye(4); bp[-1] = np.eye(4)
    doc = {k: [np.round(P, 12).tolist() for P in v] for k, v in
           (("board", bp), ("lid", lid), ("battery", bat), ("door", door))}
    with open(os.path.join(ROOT, "work", "assembly.json"), "w") as f:
        json.dump(doc, f)

main()
