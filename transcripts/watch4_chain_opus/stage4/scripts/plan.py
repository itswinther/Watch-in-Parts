import sys, json, pickle, time
import numpy as np, manifold3d as m3
sys.path.insert(0, 'tools')
import kernel
mv = json.load(open('work/movement.json'))
mesh = pickle.load(open('scripts/cache.pkl', 'rb'))
P = {k: m3.Manifold(m3.Mesh(vert_properties=np.asarray(v, np.float32), tri_verts=np.asarray(t, np.uint32))) for k, (v, t) in mesh.items()}
mob = {'barrel': 'barrel'}
for n in mv['fixed']: mob[n] = 'FIXED_' + n
for m, d in mv['mobiles'].items():
    for p in d['parts']: mob[p] = m
names = list(P)
bb = {k: np.array(P[k].bounding_box()) for k in names}
lo = np.min([b[:3] for b in bb.values()], 0) - 5.0
hi = np.max([b[3:] for b in bb.values()], 0) + 5.0
STEP = 0.19
TOL = 0.004
DIRS = [(2, 1), (2, -1), (0, 1), (0, -1), (1, 1), (1, -1)]

def travel(n, ax, sg):
    b = bb[n]
    if sg > 0: return hi[ax] - b[ax] + 0.5
    return b[ax + 3] - lo[ax] + 0.5

def poses(n, ax, sg):
    D = travel(n, ax, sg)
    k = int(np.ceil(D / STEP))
    return [D * (k - i) / k for i in range(k + 1)]  # far -> 0

def free(n, ax, sg, others):
    b = bb[n]
    obs = [o for o in others if mob[o] != mob[n]]
    for s in poses(n, ax, sg):
        if s == 0.0: continue
        d = np.zeros(3); d[ax] = sg * s
        lo1, hi1 = b[:3] + d, b[3:] + d
        moved = None
        for o in obs:
            ob = bb[o]
            if np.all(lo1 < ob[3:]) and np.all(ob[:3] < hi1):
                if moved is None: moved = P[n].translate(d.tolist())
                if kernel.ivol(moved, P[o]) > TOL: return False
    return True

remaining = set(names)
removal = []
t0 = time.time()
while remaining:
    found = False
    # prefer removing in z first, small parts
    for n in sorted(remaining, key=lambda n: -bb[n][5]):
        others = remaining - {n}
        for ax, sg in DIRS:
            if free(n, ax, sg, others):
                removal.append((n, ax, sg)); remaining.remove(n); found = True
                print('remove', n, ax, sg, round(time.time() - t0, 1), flush=True)
                break
        if found: break
    if not found:
        print('STUCK', remaining); break
order = list(reversed(removal))
asm = {'order': [], 'paths': {}}
for n, ax, sg in order:
    path = []
    for s in poses(n, ax, sg):
        T = np.eye(4); T[ax, 3] = sg * s
        path.append(T.tolist())
    asm['order'].append(n); asm['paths'][n] = path
json.dump(asm, open('work/assembly.json', 'w'))
print('order', asm['order'])
