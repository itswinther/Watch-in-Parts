import json, os, sys, math, pickle
import numpy as np
from concurrent.futures import ProcessPoolExecutor
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import kernel

W = os.path.join(ROOT, 'work')
mv = json.load(open(os.path.join(W, 'movement.json')))

def load(n):
    t = kernel.read_step(os.path.join(W, 'parts', n + '.step'), 16777216, 200000, 0.001, 0.1, 500, 120, 4096)
    return n, t

names = list(mv['fixed']) + [p for m in mv['mobiles'].values() for p in m['parts']]
with ProcessPoolExecutor(8) as ex:
    tris = dict(ex.map(load, names))
P = {n: kernel.tris_to_part(t, 0.005) for n, t in tris.items()}
P['barrel'] = kernel.tris_to_manifold(kernel.read_stl(os.path.join(ROOT, 'meshes/barrel.stl'), 200000, 33554432))
fixed = kernel.union([P[n] for n in mv['fixed']])
mobs = {k: (v['axis'], kernel.union([P[p] for p in v['parts']])) for k, v in mv['mobiles'].items()}
mobs['barrel'] = ([0, 0], P['barrel'])

def rot(man, axis, deg):
    a = math.radians(deg); c, s = math.cos(a), math.sin(a)
    T = np.eye(4); T[:2, :2] = [[c, -s], [s, c]]
    T[0, 3] = axis[0] - c * axis[0] + s * axis[1]
    T[1, 3] = axis[1] - s * axis[0] - c * axis[1]
    return kernel.apply(man, T)

print('fixed pair overlaps:')
for i, a in enumerate(mv['fixed']):
    for b in mv['fixed'][i + 1:]:
        v = kernel.ivol(P[a], P[b])
        if v > 0.001: print(' ', a, b, v)
ks = list(mobs)
print('assembled:')
for i, a in enumerate(ks):
    v = kernel.ivol(mobs[a][1], fixed)
    if v > 0.001: print('  fixed', a, v)
    for b in ks[i + 1:]:
        v = kernel.ivol(mobs[a][1], mobs[b][1])
        if v > 0.001: print(' ', a, b, v)
print('free to turn:')
for k in ks:
    ax, m = mobs[k]
    worst = max(kernel.ivol(rot(m, ax, d), fixed) for d in range(0, 360, 5))
    if worst > 0.001: print(' ', k, worst)
print('held:')
for k in ks:
    ax, m = mobs[k]
    for d in [(0.3, 0, 0), (-0.3, 0, 0), (0, 0.3, 0), (0, -0.3, 0), (0, 0, 0.3), (0, 0, -0.3)]:
        mm = kernel.apply(m, kernel.translation(d))
        others = [fixed] + [mobs[o][1] for o in ks if o != k and (d[2] == 0 or (abs(mobs[o][0][0] - ax[0]) < 0.01 and abs(mobs[o][0][1] - ax[1]) < 0.01))]
        v = sum(kernel.ivol(mm, o) for o in others)
        if v <= 0.01: print('  NOT HELD', k, d, v)
# speeds
from fractions import Fraction as F
sp = {'barrel': F(-1, 8)}  # rev/h, CCW positive
for _ in range(10):
    for e in mv['meshes']:
        if e['driver'] in sp and e['driven'] not in sp:
            sp[e['driven']] = -sp[e['driver']] * e['driver_teeth'] / e['driven_teeth']
print('speeds', {k: str(v) for k, v in sp.items()})
print('mesh test:')
for e in mv['meshes']:
    a, b = e['driver'], e['driven']; na, nb = e['driver_teeth'], e['driven_teeth']
    (axa, ma), (axb, mb) = mobs[a], mobs[b]
    steps = 8 * max(na, nb)
    jam = 0; dis = 0; drv = 0; mind = 9
    for i in range(0, steps, 2 if len(sys.argv) < 2 else 1):
        ang = i * 360 / (8 * na)
        A_ = rot(ma, axa, ang); B_ = rot(mb, axb, -ang * na / nb)
        v = kernel.ivol(A_, B_)
        jam = max(jam, v)
        if i % 4 == 0:
            d = kernel.min_distance(A_, B_, 1.0)
            if d > 0.1: dis += 1
        if i % 8 == 0:
            v2 = kernel.ivol(rot(ma, axa, ang + 90 / na), B_)
            if v2 <= 0.01: drv += 1; mind = min(mind, v2)
            else: mind = min(mind, v2)
    print(' ', a, b, 'maxjam %.4f disengaged %d nodrive %d mindrive %.4f' % (jam, dis, drv, mind))
print('noncolliding pairs:')
meshed = {frozenset((e['driver'], e['driven'])) for e in mv['meshes']}
for i, a in enumerate(ks):
    for b in ks[i + 1:]:
        if frozenset((a, b)) in meshed: continue
        (axa, ma), (axb, mb) = mobs[a], mobs[b]
        wa, wb = float(sp.get(a, 0)), float(sp.get(b, 0))
        f = max(abs(wa), abs(wb))
        worst = 0
        if f > 0:
            for j in range(0, 144, 3):
                t = j / 144 / f
                worst = max(worst, kernel.ivol(rot(ma, axa, 360 * wa * t), rot(mb, axb, 360 * wb * t)))
        r = abs(wa - wb)
        if r > 0:
            for j in range(0, 144, 3):
                t = j / 144 / r
                worst = max(worst, kernel.ivol(rot(ma, axa, 360 * wa * t), rot(mb, axb, 360 * wb * t)))
        if worst > 0.001: print(' ', a, b, worst)
# size
allm = kernel.union([fixed] + [m for _, m in mobs.values()])
v = kernel.verts(allm); c = mv['case_centre']
print('height', v[:, 2].max() - v[:, 2].min())
rmax = 0
for k, (ax, m) in mobs.items():
    vv = kernel.verts(m); r = np.hypot(vv[:, 0] - ax[0], vv[:, 1] - ax[1]).max()
    rmax = max(rmax, math.hypot(ax[0] - c[0], ax[1] - c[1]) + r)
vf = kernel.verts(fixed); rmax = max(rmax, np.hypot(vf[:, 0] - c[0], vf[:, 1] - c[1]).max())
print('radius bound', rmax)
