import sys, os, itertools
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from geometry import watch as W, core
m = W.load_movement(os.path.join(os.path.dirname(__file__), '..', 'work'))
names = list(m.mobiles)
only = sys.argv[1:] or ['asm', 'spin', 'held', 'mesh', 'clear']
if 'asm' in only:
    for a in names:
        v = core.ivol(m.posed(a), m.fixed)
        if v > 0.001: print('ASM fixed', a, v)
    for a, b in itertools.combinations(names, 2):
        v = core.ivol(m.posed(a), m.posed(b))
        if v > 0.001: print('ASM', a, b, v)
    print('asm done')
if 'spin' in only:
    for a in names: print('spin', a, m.spin(a))
if 'held' in only:
    for a in names:
        h = m.held(a); print('held', a, 'min', min(h.values()), h)
w, _ = m.speeds()
meshed = set()
for x, tx, y, ty in m.meshes:
    meshed.add(frozenset((x, y)))
    if 'mesh' in only: print('mesh', x, y, m.mesh_run(x, tx, y, ty), flush=True)
if 'clear' in only:
    for a, b in itertools.combinations(names, 2):
        if frozenset((a, b)) in meshed: continue
        print('clear', a, b, m.clear_run(a, b, w[a], w[b]), flush=True)
