import sys, json, numpy as np
sys.path.insert(0, 'tools')
import manifold3d as m3
from geometry import core, bodies as B, constants as C
from geometry.core import ivol, apply, translation as tr, union, box
base = core.load_part('work/base.stl', 200000, 1<<26, .005); door = core.load_part('work/door.stl', 200000, 1<<26, .005)
P = json.load(open('submission/assembly.json'))
batt = apply(B.battery(), P['battery'][-1]); board = B.board(); lid = B.lid(); pcb = B.pcb()
printed = union([base, door])
bod = {'base': base, 'door': door, 'board': board, 'lid': lid, 'battery': batt}
ks = list(bod)
print('final pairs', {a+'-'+b: round(ivol(bod[a], bod[b]), 4) for i, a in enumerate(ks) for b in ks[i+1:]})
for m in (base, door):
    v = core.verts(m); print('bbox', v.min(0), v.max(0))
print('material', base.volume() + door.volume(), 'limit 17333.44')
sec = printed.slice(-0.05)
for (x, y) in C.HOLES:
    ring = m3.CrossSection.circle(3.5, 128) - m3.CrossSection.circle(1.6, 128)
    print('support', (x, y), round((sec ^ ring.translate([x, y])).area(), 2))
for d in ((.6,0,0),(-.6,0,0),(0,.6,0),(0,-.6,0),(0,0,-.6)):
    print('located', d, round(ivol(apply(pcb, tr(d)), printed), 3))
others = union([base, door, board, lid])
for d in ((2,0,0),(-2,0,0),(0,2,0),(0,-2,0),(0,0,2),(0,0,-2)):
    print('held', d, round(ivol(apply(batt, tr(d)), others), 2))
for k, c in B.components().items():
    print('clear', k, round(c.min_gap(printed, 5.0), 3), ivol(c, printed))
bb = batt.bounding_box(); print('batt bbox', bb)
slab = box((bb[0], bb[1], bb[5]), (bb[3], bb[4], bb[5] + 1.0)); print('swell', ivol(slab, others))
lead = (np.array(P['battery'][-1]) @ np.array([0, 15, 3.75, 1]))[:3]; print('lead', np.linalg.norm(lead - np.array(C.J4_CENTRE)))
for k, v in B.keepouts().items(): print('keepout', k, ivol(v, printed))
s1 = core.section_x(printed, -1.05); print('J1 open', (B.j1_section_2d(3.0) - s1).area(), '<=130.5')
s2 = core.section_x(printed, 72.55); print('J2 open', (B.j2_section_2d(3.0) - s2).area(), '<=78.53')
print('door stop', ivol(apply(door, tr((0,0,1))), base), 'lid seat', ivol(apply(lid, tr((0,0,-.2))), base))
