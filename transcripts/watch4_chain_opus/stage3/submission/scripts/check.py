import sys, json, math, numpy as np
from fractions import Fraction as F
sys.path.insert(0, 'tools'); import kernel, manifold3d as m3
mv = json.load(open('work/movement.json'))
def ld(n):
    d = np.load('scripts/cache/%s.npz' % n)
    return m3.Manifold(m3.Mesh(vert_properties=d['v'].astype(np.float32), tri_verts=d['f'].astype(np.uint32)))
barrel = kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl', 200000, 33554432))
mob = {k: kernel.union([ld(p) for p in v['parts']]) for k, v in mv['mobiles'].items()}
mob['barrel'] = barrel
axis = {k: v['axis'] for k, v in mv['mobiles'].items()}; axis['barrel'] = [0, 0]
fixed = kernel.union([ld(p) for p in mv['fixed']])
def rot(man, ax, deg):  # positive = CCW seen from +z
    a = math.radians(deg); c, s = math.cos(a), math.sin(a); x, y = ax
    T = [[c, -s, 0, x - c*x + s*y], [s, c, 0, y - s*x - c*y], [0, 0, 1, 0]]
    return man.transform(T)
# speeds (rev/h, CCW positive)
sp = {'barrel': F(-1, 6)}
changed = True
while changed:
    changed = False
    for e in mv['meshes']:
        if e['driver'] in sp and e['driven'] not in sp:
            sp[e['driven']] = -sp[e['driver']] * e['driver_teeth'] / e['driven_teeth']; changed = True
for e in mv['meshes']:
    assert sp[e['driven']] == -sp[e['driver']] * e['driver_teeth'] / e['driven_teeth'], e
print('speeds rev/h (CCW+):', {k: str(v) for k, v in sp.items()})
names = sorted(mob)
bad = 0
# assembled
for k in names:
    v = kernel.ivol(fixed, mob[k])
    if v > 0.01: print('ASSEMBLED fixed vs', k, v); bad += 1
for i, a in enumerate(names):
    for b in names[i+1:]:
        v = kernel.ivol(mob[a], mob[b])
        if v > 0.01: print('ASSEMBLED', a, b, v); bad += 1
focus = sys.argv[1:] or names
# free to turn
for k in focus:
    if k == 'barrel': continue
    for s in range(72):
        v = kernel.ivol(fixed, rot(mob[k], axis[k], 5 * s))
        if v > 0.01: print('FREE', k, s, v); bad += 1; break
# meshes
for e in mv['meshes']:
    a, b = e['driver'], e['driven']
    if a not in focus and b not in focus: continue
    ta, tb = e['driver_teeth'], e['driven_teeth']
    for i in range(8 * max(ta, tb)):
        da = i * 360 / (8 * ta); db = -da * ta / tb
        A = rot(mob[a], axis[a], da); B = rot(mob[b], axis[b], db)
        v = kernel.ivol(A, B)
        if v > 0.01: print('JAM', a, b, i, v); bad += 1; break
        if i % 4 == 0:
            d = kernel.min_distance(A, B, 0.5)
            if d > 0.1: print('DISENGAGED', a, b, i, d); bad += 1; break
        if i % 8 == 0:
            v2 = kernel.ivol(rot(mob[a], axis[a], da + 90 / ta), B)
            if v2 <= 0.01: print('NODRIVE', a, b, i, v2); bad += 1; break
    print('mesh', a, b, 'done')
# non-meshing pairs
meshed = {frozenset((e['driver'], e['driven'])) for e in mv['meshes']}
for i, a in enumerate(names):
    for b in names[i+1:]:
        if frozenset((a, b)) in meshed or (a not in focus and b not in focus): continue
        if not kernel.bbox_overlap(mob[a], mob[b], 0.05): continue
        wa, wb = sp.get(a, 0), sp.get(b, 0)
        fast = max(abs(wa), abs(wb)); rel = abs(wa - wb)
        hit = False
        for scale in ([1 / fast] if fast else []) + ([1 / rel] if rel else []):
            for s in range(144):
                t = scale * s / 144
                v = kernel.ivol(rot(mob[a], axis[a], float(360 * wa * t)), rot(mob[b], axis[b], float(360 * wb * t)))
                if v > 0.01: print('COLLIDE', a, b, s, v); bad += 1; hit = True; break
            if hit: break
print('BAD', bad)
