import sys, itertools, time
sys.path.insert(0, 'tools')
from geometry import watch as W, core
m = W.load_movement('work')
w, conf = m.speeds(); print({k: str(v) for k, v in w.items()}, conf)
names = list(m.mobiles)
print('assembled fixed-vs-mobile', {n: core.ivol(m.fixed, m.posed(n)) for n in names})
print('assembled pairs', {(a, b): v for a, b in itertools.combinations(names, 2) if (v := core.ivol(m.posed(a), m.posed(b))) > 0})
for n in names: print('spin', n, m.spin(n))
for n in names: print('held', n, {k: round(v, 4) for k, v in m.held(n).items()})
print('extent', m.extent(), {h: m.hand_reach(h) for h in m.hands})
if 'fast' in sys.argv: sys.exit()
meshed = set()
for a, ta, b, tb in m.meshes:
    t = time.time(); meshed.add(frozenset((a, b)))
    print('mesh', a, b, m.mesh_run(a, ta, b, tb), round(time.time()-t, 1), flush=True)
for a, b in itertools.combinations(names, 2):
    if frozenset((a, b)) not in meshed:
        print('clear', a, b, m.clear_run(a, b, w.get(a, 0), w.get(b, 0)), flush=True)
