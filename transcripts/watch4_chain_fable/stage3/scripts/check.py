from common import *
import math, itertools, time
from fractions import Fraction as F
mv = json.load(open(os.path.join(ROOT, 'work/movement.json')))
U = kernel.union; iv = kernel.ivol
fixed = U([load(n) for n in mv['fixed']])
mob = {k: U([load(p) for p in v['parts']]) for k, v in mv['mobiles'].items()}
axis = {k: np.array(v['axis']) for k, v in mv['mobiles'].items()}
mob['barrel'] = barrel(); axis['barrel'] = np.zeros(2)
def rot(m, ax, deg):   # CCW positive
    return m.translate([-ax[0], -ax[1], 0]).rotate([0, 0, deg]).translate([ax[0], ax[1], 0])
ok = True
def rep(name, good, extra=''):
    global ok; ok &= bool(good); print('PASS' if good else 'FAIL', name, extra, flush=True)
# speeds (turns per hour, CW positive)
sp = {'barrel': F(1, 6)}
ch = True
while ch:
    ch = False
    for g in mv['meshes']:
        if g['driver'] in sp and g['driven'] not in sp:
            sp[g['driven']] = -sp[g['driver']] * g['driver_teeth'] / g['driven_teeth']; ch = True
print({k: str(v) for k, v in sp.items()})
h = mv['hands']
rep('speeds', sp[h['hour']['mobile']] == F(1, 12) and sp[h['minute']['mobile']] == 1 and sp[h['seconds']['mobile']] == 60 and sp[h['day']['mobile']] == F(1, 24))
da = axis[h['day']['mobile']] - axis[h['hour']['mobile']]
rep('day placement', np.hypot(*da) >= 6.0, np.hypot(*da))
# assembled
worst = max(iv(fixed, m) for m in mob.values())
names = list(mob)
for a, b in itertools.combinations(names, 2):
    worst = max(worst, iv(mob[a], mob[b]))
rep('assembled', worst <= 0.01, worst)
# free to turn
w = max(iv(fixed, rot(m, axis[k], 5 * i)) for k, m in mob.items() for i in range(72))
rep('free to turn', w <= 0.01, w)
# held
bad = []
for k, m in mob.items():
    others = U([fixed] + [mob[o] for o in mob if o != k])
    same = U([fixed] + [mob[o] for o in mob if o != k and np.hypot(*(axis[o] - axis[k])) <= 0.01])
    for d in [(.3,0,0),(-.3,0,0),(0,.3,0),(0,-.3,0)]:
        if iv(m.translate(d), others) <= 0.01: bad.append((k, d))
    for d in [(0,0,.3),(0,0,-.3)]:
        if iv(m.translate(d), same) <= 0.01: bad.append((k, d))
rep('held', not bad, bad)
# size
cc = np.array(mv['case_centre']); rmax = 0; zlo = 1e9; zhi = -1e9
for k, m in list(mob.items()) + [('fixed', fixed)]:
    v = kernel.verts(m); zlo = min(zlo, v[:, 2].min()); zhi = max(zhi, v[:, 2].max())
    if k == 'fixed': rmax = max(rmax, np.hypot(*(v[:, :2] - cc).T).max())
    else: rmax = max(rmax, np.hypot(*(axis[k] - cc)) + np.hypot(*(v[:, :2] - axis[k]).T).max())
rep('size', rmax <= 20.7 and zhi - zlo <= 13.4, (rmax, zhi - zlo))
for k in h:
    v = kernel.verts(load(h[k]['part'])); print(' hand', k, 'reach', np.hypot(*(v[:, :2] - axis[h[k]['mobile']]).T).max())
# printable for new parts
for n in sys.argv[1:]:
    m = load(n); bb = m.bounding_box()
    for jit in (0.0, 0.017, 0.031):
        lo, shape = kernel.grid_for(np.array(bb[:3]) - 0.2, np.array(bb[3:]) + 0.2, 0.05, jit)
        s = np.pad(kernel.voxelize(m, lo, shape, 0.05), 1)
        core = kernel.edt(s) >= 1.5
        body = (kernel.edt(~core) <= 1.0) & s
        dev = kernel.edt(~body)[s].max() * 0.05 if core.any() else float('inf')
        rep('printable %s jit %g' % (n, jit), dev <= 0.2, dev)
# train runs
only = os.environ.get('MESHES')
for g in mv['meshes']:
    a, b, Na, Nb = g['driver'], g['driven'], g['driver_teeth'], g['driven_teeth']
    if only and b not in only.split(','): continue
    t = time.time(); mx = 0; gap = 0; drive = 1e9
    zb = mob[b].bounding_box(); za = mob[a].bounding_box()
    # trim both to the shared z slab neighbourhood for speed (exact for intersections)
    n = 8 * max(Na, Nb)
    for i in range(n):
        ang = i * 360 / (8 * Na)
        A = rot(mob[a], axis[a], ang); B = rot(mob[b], axis[b], -ang * Na / Nb)
        mx = max(mx, iv(A, B))
        if i % 4 == 0: gap = max(gap, kernel.min_distance(A, B, 0.5))
        if i % 8 == 0: drive = min(drive, iv(rot(mob[a], axis[a], ang + 90 / Na), B))
    rep('mesh %s->%s' % (a, b), mx <= 0.01 and gap <= 0.1 and drive > 0.01, 'jam %.5f gap %.4f drive %.4f (%.0fs)' % (mx, gap, drive, time.time() - t))
# nothing else collides
if not os.environ.get('SKIPPAIRS'):
    meshed = {frozenset((g['driver'], g['driven'])) for g in mv['meshes']}
    w = 0
    for a, b in itertools.combinations(names, 2):
        if frozenset((a, b)) in meshed: continue
        if not kernel.bbox_overlap(mob[a], mob[b], 25): continue
        ra = np.hypot(*(kernel.verts(mob[a])[:, :2] - axis[a]).T).max(); rb = np.hypot(*(kernel.verts(mob[b])[:, :2] - axis[b]).T).max()
        if np.hypot(*(axis[a] - axis[b])) > ra + rb: continue
        sa, sb = sp.get(a, F(0)), sp.get(b, F(0))
        fast = max(abs(sa), abs(sb)); rel = abs(sa - sb)
        scheds = []
        if fast: scheds.append(1 / fast)
        if rel: scheds.append(1 / rel)
        for T in scheds:
            for i in range(144):
                t = float(T) * i / 144
                w = max(w, iv(rot(mob[a], axis[a], -360 * float(sa) * t), rot(mob[b], axis[b], -360 * float(sb) * t)))
    rep('nothing else collides', w <= 0.01, w)
print('ALL OK' if ok else 'SOMETHING FAILED')
