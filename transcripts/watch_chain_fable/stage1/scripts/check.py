import sys, os, json, math, itertools
from fractions import Fraction as F
import numpy as np
sys.path.insert(0, 'tools')
import kernel as K
D = sys.argv[1] if len(sys.argv) > 1 else 'work'
doc = json.load(open(D+'/movement.json'))
def load(n): return K.load_part('%s/parts/%s.stl' % (D, n), 200000, 1 << 25, 0.005)
fixed = {n: load(n) for n in doc['fixed']}
FX = K.union(list(fixed.values()))
mob = {k: K.union([load(n) for n in v['parts']]) for k, v in doc['mobiles'].items()}
axis = {k: tuple(v['axis']) for k, v in doc['mobiles'].items()}
mob['barrel'] = K.tris_to_manifold(K.read_stl('meshes/barrel.stl', 10**7, 1 << 30)); axis['barrel'] = (0.0, 0.0)
def rot(man, ax, deg):   # CCW positive
    return man.translate([-ax[0], -ax[1], 0]).rotate([0, 0, deg]).translate([ax[0], ax[1], 0])
ok = {}
# hard
bad = []
for a, b in itertools.combinations(fixed, 2):
    v = K.ivol(fixed[a], fixed[b])
    if v > 0.01: bad.append((a, b, v))
names = ['FIXED'] + list(mob); ob = dict(mob, FIXED=FX)
for a, b in itertools.combinations(names, 2):
    v = K.ivol(ob[a], ob[b])
    if v > 0.001: bad.append((a, b, v))
print('HARD assembled', 'OK' if not bad else bad)
# free to turn
bad = []
for k in mob:
    w = max(K.ivol(rot(mob[k], axis[k], 5*i), FX) for i in range(72))
    if w > 0.001: bad.append((k, w))
print('free to turn', 'OK' if not bad else bad)
# held
bad = []
for k in mob:
    others = K.union([FX] + [mob[j] for j in mob if j != k])
    same = K.union([FX] + [mob[j] for j in mob if j != k and math.dist(axis[j], axis[k]) <= 0.01])
    res = []
    for d in [(.3, 0, 0), (-.3, 0, 0), (0, .3, 0), (0, -.3, 0)]:
        res.append(K.ivol(mob[k].translate(list(d)), others))
    for d in [(0, 0, .3), (0, 0, -.3)]:
        res.append(K.ivol(mob[k].translate(list(d)), same))
    print('  held', k, ['%.3f' % r for r in res])
    if min(res) <= 0.02: bad.append(k)
print('held', 'OK' if not bad else bad)
# speeds (CW positive, rev per 8h)
sp = {'barrel': F(1)}
ch = True
while ch:
    ch = False
    for e in doc['meshes']:
        for x, y, nx, ny in [(e['driver'], e['driven'], e['driver_teeth'], e['driven_teeth']), (e['driven'], e['driver'], e['driven_teeth'], e['driver_teeth'])]:
            if x in sp:
                s = -sp[x]*nx/ny
                if y not in sp: sp[y] = s; ch = True
                elif sp[y] != s: print('SPEED CONFLICT', y)
print('speeds per hour (CW+):', {k: str(v/8) for k, v in sp.items()})
# mesh test
for e in doc['meshes']:
    a, b, na, nb = e['driver'], e['driven'], e['driver_teeth'], e['driven_teeth']
    n = 8*max(na, nb); mx = 0; mg = 0; md = 1e9
    for i in range(n):
        ang = i*360/(8*na)
        ra = rot(mob[a], axis[a], ang); rb = rot(mob[b], axis[b], -ang*na/nb)
        mx = max(mx, K.ivol(ra, rb))
        if i % 4 == 0: mg = max(mg, K.min_distance(ra, rb, 1.0))
        if i % 8 == 0: md = min(md, K.ivol(rot(mob[a], axis[a], ang+90/na), rb))
    st = 'OK' if (mx <= 0.005 and mg <= 0.08 and md > 0.02) else 'FAIL'
    print('mesh %s->%s: max ivol %.5f  max gap %.4f  min drive ivol %.4f  %s' % (a, b, mx, mg, md, st))
# non-meshing pairs
meshed = {frozenset((e['driver'], e['driven'])) for e in doc['meshes']}
bad = []
for a, b in itertools.combinations(mob, 2):
    if frozenset((a, b)) in meshed: continue
    sa, sb = float(sp.get(a, 0)), float(sp.get(b, 0))   # CW positive
    w = 0
    fast = max(abs(sa), abs(sb)); rel = abs(sa-sb)
    for tot in ([1/fast] if fast else []) + ([1/rel] if rel else []):
        for i in range(145):
            t = tot*i/144
            w = max(w, K.ivol(rot(mob[a], axis[a], -360*sa*t), rot(mob[b], axis[b], -360*sb*t)))
    if not fast: w = K.ivol(mob[a], mob[b])
    if w > 0.001: bad.append((a, b, w))
print('nothing else collides', 'OK' if not bad else bad)
# reach, size
cc = doc['case_centre']
for h, e in doc['hands'].items():
    v = K.verts(load(e['part'])); ax = axis[e['mobile']]
    print('hand', h, 'reach %.2f' % np.hypot(v[:, 0]-ax[0], v[:, 1]-ax[1]).max(), 'z %.2f..%.2f' % (v[:, 2].min(), v[:, 2].max()), 'speed/h', sp[e['mobile']]/8)
rmax = 0; zs = []
for k, m in ob.items():
    v = K.verts(m); zs += [v[:, 2].min(), v[:, 2].max()]
    if k == 'FIXED': r = np.hypot(v[:, 0]-cc[0], v[:, 1]-cc[1]).max()
    else:
        r = math.dist(axis[k], cc) + np.hypot(v[:, 0]-axis[k][0], v[:, 1]-axis[k][1]).max()
    rmax = max(rmax, r)
print('size: rmax %.3f (<=23)  height %.3f (<=16)' % (rmax, max(zs)-min(zs)))
