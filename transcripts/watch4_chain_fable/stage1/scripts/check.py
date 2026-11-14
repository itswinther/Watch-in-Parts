"""My own re-implementation of the spec tests (not the grader). Run from the task folder."""
import sys, json, math, itertools, time
from fractions import Fraction
sys.path.insert(0, 'tools')
import numpy as np, kernel, manifold3d as m3
W = 'work'
doc = json.load(open(W + '/movement.json'))
ld = lambda n: kernel.load_step_part('%s/parts/%s.step' % (W, n), 16777216, 200000, 0.001, 0.1, 500, 120, 4096, 0.005)
P = {n: ld(n) for n in doc['fixed'] + [p for m in doc['mobiles'].values() for p in m['parts']]}
print('tris', {n: p.num_tri() for n, p in P.items() if p.num_tri() > 20000})
barrel = kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl', 200000, 33554432))
fixed = kernel.union([P[n] for n in doc['fixed']])
mob = {k: kernel.union([P[n] for n in m['parts']]) for k, m in doc['mobiles'].items()}
ax = {k: m['axis'] for k, m in doc['mobiles'].items()}
mob['barrel'] = barrel; ax['barrel'] = [0, 0]
def rot(k, deg):   # CCW positive
    c = ax[k]
    return mob[k].translate([-c[0], -c[1], 0]).rotate([0, 0, deg]).translate([c[0], c[1], 0])
ok = {}
# assembled
bad = []
for a, b in itertools.combinations(doc['fixed'], 2):
    if kernel.ivol(P[a], P[b]) > 0.01: bad.append((a, b))
for k in mob:
    v = kernel.ivol(mob[k], fixed)
    if v > 0.01: bad.append((k, 'fixed', v))
for a, b in itertools.combinations(mob, 2):
    v = kernel.ivol(mob[a], mob[b])
    if v > 1e-6: print('  touch', a, b, v)
    if v > 0.01: bad.append((a, b, v))
ok['assembled'] = not bad; print('assembled', bad)
# free to turn
bad = [(k, i) for k in mob for i in range(72) if kernel.ivol(rot(k, 5 * i), fixed) > 0.01]
ok['free'] = not bad; print('free', bad[:5])
# held
bad = []
for k in mob:
    others = kernel.union([fixed] + [mob[j] for j in mob if j != k])
    zs = kernel.union([fixed] + [mob[j] for j in mob if j != k and math.hypot(ax[j][0] - ax[k][0], ax[j][1] - ax[k][1]) <= 0.01])
    for d in ([.3, 0, 0], [-.3, 0, 0], [0, .3, 0], [0, -.3, 0], [0, 0, .3], [0, 0, -.3]):
        v = kernel.ivol(mob[k].translate(d), zs if d[2] else others)
        if v <= 0.01: bad.append((k, d, v))
        elif v < 0.05: print('  held low', k, d, v)
ok['held'] = not bad; print('held', bad)
# train
speed = {'barrel': Fraction(1, 8)}   # rev/h, clockwise positive
bad = []
for e in doc['meshes']:
    a, b, za, zb = e['driver'], e['driven'], e['driver_teeth'], e['driven_teeth']
    speed[b] = -speed[a] * za / zb
    t0 = time.time(); mx = 0; mind = 0; mindrive = 1e9
    for i in range(8 * max(za, zb)):
        th = i * 360.0 / (8 * za)
        A, B = rot(a, th), rot(b, -th * za / zb)
        v = kernel.ivol(A, B); mx = max(mx, v)
        if i % 4 == 0: mind = max(mind, kernel.min_distance(A, B, 1.0))
        if i % 8 == 0: mindrive = min(mindrive, kernel.ivol(rot(a, th + 90.0 / za), B))
    good = mx <= 0.01 and mind <= 0.1 and mindrive > 0.01
    print('mesh %s>%s jam %.5f gap %.4f drive %.4f %s %.0fs' % (a, b, mx, mind, mindrive, good, time.time() - t0), flush=True)
    if not good: bad.append((a, b))
ok['train'] = not bad
print('speeds', {k: str(v) for k, v in speed.items()})
# others
meshed = {frozenset((e['driver'], e['driven'])) for e in doc['meshes']}
bad = []
for a, b in itertools.combinations(mob, 2):
    if frozenset((a, b)) in meshed or not kernel.bbox_overlap(mob[a], mob[b], 0.1): continue
    sa, sb = float(speed.get(a, 0)), float(speed.get(b, 0))
    f = max(abs(sa), abs(sb)); rel = abs(sa - sb)
    for T_ in ([1 / f] if f else []) + ([1 / rel] if rel else []):
        for i in range(144):
            t = T_ * i / 144
            if kernel.ivol(rot(a, -360 * sa * t), rot(b, -360 * sb * t)) > 0.01: bad.append((a, b)); break
ok['others'] = not bad; print('others', bad)
# hands, size
cc = doc['case_centre']
for h, e in doc['hands'].items():
    v = kernel.verts(P[e['part']]); c = ax[e['mobile']]
    print('hand', h, 'reach %.2f' % np.hypot(v[:, 0] - c[0], v[:, 1] - c[1]).max(), 'speed', speed[e['mobile']])
zl, zh, rmax = 1e9, -1e9, 0
for k in mob:
    v = kernel.verts(mob[k]); c = ax[k]
    rmax = max(rmax, math.hypot(c[0] - cc[0], c[1] - cc[1]) + np.hypot(v[:, 0] - c[0], v[:, 1] - c[1]).max())
    zl, zh = min(zl, v[:, 2].min()), max(zh, v[:, 2].max())
v = kernel.verts(fixed); rmax = max(rmax, np.hypot(v[:, 0] - cc[0], v[:, 1] - cc[1]).max())
zl, zh = min(zl, v[:, 2].min()), max(zh, v[:, 2].max())
ok['size'] = rmax <= 20.7 and zh - zl <= 13.4; print('size r %.3f h %.3f' % (rmax, zh - zl))
# printable
from scipy import ndimage
bad = []
for n, p in P.items():
    bb = p.bounding_box()
    if (bb[3] - bb[0]) * (bb[4] - bb[1]) * (bb[5] - bb[2]) / 0.05 ** 3 > 6e7: print('  printable skipped', n); continue
    worst = 0
    for j in (0.0, 0.017, 0.033):
        lo, shape = kernel.grid_for([bb[0] - 0.1, bb[1] - 0.1, bb[2] - 0.1], bb[3:], 0.05, j)
        shape = tuple(s + 3 for s in shape)
        s = np.pad(kernel.voxelize(p, lo, shape, 0.05), 1)
        surv = ndimage.distance_transform_edt(s) >= 1.5
        if not surv.any(): worst = 99; break
        body = s & (ndimage.distance_transform_edt(~surv) <= 1.0 + 1e-9)
        worst = max(worst, ndimage.distance_transform_edt(~body)[s].max() * 0.05)
    if worst > 0.2: bad.append((n, worst))
    print('  printable %-32s %.3f' % (n, worst), flush=True)
ok['printable'] = not bad
print(ok)
