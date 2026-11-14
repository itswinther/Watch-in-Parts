import sys, json, pickle
import numpy as np, manifold3d as m3
sys.path.insert(0, 'tools')
import kernel
mv = json.load(open('work/movement.json'))
asm = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'work/assembly.json'))
mesh = pickle.load(open('scripts/cache.pkl', 'rb'))
P = {k: m3.Manifold(m3.Mesh(vert_properties=np.asarray(v, np.float64), tri_verts=np.asarray(t, np.uint32))) for k, (v, t) in mesh.items()}
mob = {'barrel': 'barrel'}
for n in mv['fixed']: mob[n] = 'F_' + n
for m, d in mv['mobiles'].items():
    for p in d['parts']: mob[p] = m
allp = set(P)
bbs = np.array([P[k].bounding_box() for k in P])
glo, ghi = bbs[:, :3].min(0) - 5, bbs[:, 3:].max(0) + 5
seen = []; ok_all = True
order = []
for n in asm['order']:
    if n in allp and n not in order: order.append(n)
missing = allp - set(order)
print('missing from order:', missing)
for n in order:
    path = [np.array(T, float) for T in asm['paths'].get(n, [])]
    errs = []
    if not (2 <= len(path) <= 1500): errs.append('npose %d' % len(path))
    for T in path:
        R = T[:3, :3]
        if not np.all(np.isfinite(T)) or np.abs(R.T @ R - np.eye(3)).max() > 1e-6 or abs(np.linalg.det(R) - 1) > 1e-6 or np.abs(T[3] - [0, 0, 0, 1]).max() > 1e-6:
            errs.append('bad matrix'); break
    if path and np.abs(path[-1] - np.eye(4)).max() > 1e-6: errs.append('last not identity')
    V = kernel.verts(P[n])
    if path:
        W = V @ path[0][:3, :3].T + path[0][:3, 3]
        lo, hi = W.min(0), W.max(0)
        if not np.any((lo > ghi) | (hi < glo)): errs.append('first pose not outside')
    for a, b in zip(path, path[1:]):
        d = (V @ (b[:3, :3] - a[:3, :3]).T + (b[:3, 3] - a[:3, 3]))
        if np.linalg.norm(d, axis=1).max() > 0.2: errs.append('step too big'); break
    worst = 0
    obs = [o for o in seen if mob[o] != mob[n]]
    for T in path:
        M = kernel.apply(P[n], T)
        for o in obs:
            v = kernel.ivol(M, P[o]); worst = max(worst, v)
    if worst > 0.01: errs.append('collision %.4f' % worst)
    print(n, len(path), 'worst %.5f' % worst, errs or 'OK', flush=True)
    ok_all &= not errs
    seen.append(n)
print('ALL OK' if ok_all and not missing else 'PROBLEMS')
