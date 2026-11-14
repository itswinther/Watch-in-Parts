import json, sys, time
import numpy as np
from common import *
doc, parts, owner = load()
A = json.load(open(os.path.join(ROOT, "submission", "assembly.json")))
order, paths = A["order"], A["paths"]
allp = set(parts)
assert sorted(order) == sorted(allp), (set(order) ^ allp)
TB = total_bbox(parts); G = TB + np.array([-5, -5, -5, 5, 5, 5])
placed = []; ok_all = True; t0 = time.time()
for n in order:
    P = parts[n]; V = kernel.verts(P); bad = []
    poses = [np.array(p, float) for p in paths[n]]
    if not (2 <= len(poses) <= 1500): bad.append("count")
    for T in poses:
        R = T[:3, :3]
        if T.shape != (4, 4) or not np.isfinite(T).all() or np.abs(T[3] - [0, 0, 0, 1]).max() > 1e-6 \
           or np.abs(R.T @ R - np.eye(3)).max() > 1e-6 or abs(np.linalg.det(R) - 1) > 1e-6:
            bad.append("rigid"); break
    if np.abs(poses[-1] - np.eye(4)).max() > 1e-6: bad.append("last")
    W0 = V @ poses[0][:3, :3].T + poses[0][:3, 3]
    lo, hi = W0.min(0), W0.max(0)
    if not any(hi[i] < G[i] or lo[i] > G[i + 3] for i in range(3)): bad.append("start")
    prev = W0
    for T in poses[1:]:
        W = V @ T[:3, :3].T + T[:3, 3]
        if np.linalg.norm(W - prev, axis=1).max() > 0.2: bad.append("step"); break
        prev = W
    worst = 0
    for T in poses:
        M = kernel.apply(P, T)
        for o in placed:
            if owner[o] == owner[n]: continue
            v = kernel.ivol(M, parts[o]); worst = max(worst, v)
            if v > 0.01: bad.append("hit %s %.4f" % (o, v)); break
        if any(b.startswith("hit") for b in bad): break
    placed.append(n)
    ok_all &= not bad
    print(n, len(poses), "OK" if not bad else bad, "worst %.5f" % worst, round(time.time() - t0, 1), flush=True)
print("ALL OK" if ok_all else "FAILURES")
