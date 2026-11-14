import sys, json, math, os
sys.path.insert(0, 'tools')
import numpy as np, manifold3d as m3
import kernel as K
from manifold3d import CrossSection

M_ = 0.2; PA = math.radians(25); BL = 0.03
def inv(a): return math.tan(a) - a

def gear2d(z, phase):
    rp = M_*z/2; rb = rp*math.cos(PA); ra = rp+M_; rr = rp-1.25*M_
    psi_p = (math.pi*M_/2 - BL)/(2*rp)
    pts = []
    pitch = 2*math.pi/z
    r0 = max(rb, rr)
    rs = np.linspace(r0, ra, 12)
    def half(r):
        a = math.acos(min(1, rb/r)); return psi_p + inv(PA) - inv(a)
    for k in range(z):
        c = phase + k*pitch
        # right flank (cw side) from root to tip, then left flank back
        if rr < rb:
            pts.append((rr, c - half(rb)))
        right = [(r, c - half(r)) for r in rs]
        left = [(r, c + half(r)) for r in rs[::-1]]
        pts += right + left
        if rr < rb:
            pts.append((rr, c + half(rb)))
        # root arc
        nxt = c + pitch - half(rb) if rr < rb else None
        a0 = c + half(rb); a1 = c + pitch - half(rb)
        for f in (0.33, 0.66):
            pts.append((rr, a0 + f*(a1-a0)))
    poly = [(r*math.cos(a), r*math.sin(a)) for r, a in pts]
    return CrossSection([poly])

def gear(z, phase, z0, z1):
    return gear2d(z, phase).extrude(z1-z0).translate([0, 0, z0])

def cyl(r, z0, z1, seg=48, at=(0, 0)):
    return K.cyl_z(at[0], at[1], z0, z1, r, seg)

# ---- layout ----
barrel = (0.0, 0.0)
P = {}
P['A'] = (11.2, 0.0)
P['M'] = (8.9, 8.05)
P['B'] = (P['A'][0]+6*math.cos(math.radians(-50)), P['A'][1]+6*math.sin(math.radians(-50)))
P['C'] = (P['B'][0]+6*math.cos(math.radians(60)), P['B'][1]+6*math.sin(math.radians(60)))
P['S'] = (P['C'][0], P['C'][1]+7.2)
P['T'] = (P['M'][0]+6*math.cos(math.radians(135)), P['M'][1]+6*math.sin(math.radians(135)))
# fix exact distances by construction above (M-A solved numerically)
def fix_M():
    # solve M on circle |M|=12 and |M-A|=8.4
    x = (144 + 11.2**2 - 8.4**2)/(2*11.2); y = math.sqrt(144-x*x); P['M'] = (x, y)
    P['T'] = (x+6*math.cos(math.radians(135)), y+6*math.sin(math.radians(135)))
fix_M()
def dist(a, b): return math.dist(a, b)

# gears: id -> (mobile, teeth, layer)
G = {
 'A_a': ('A',16,0), 'A_b': ('A',48,1), 'B_a': ('B',12,1), 'B_b': ('B',48,2),
 'C_a': ('C',12,2), 'C_b': ('C',60,3), 'S_a': ('S',12,3), 'M_a': ('M',36,1),
 'M_b': ('M',15,4), 'T_a': ('T',45,4), 'T_b': ('T',12,5), 'H_a': ('H',48,5)}
pos = {k: P[v[0]] for k, v in G.items() if v[0] != 'H'}
P['H'] = P['M']; pos['H_a'] = P['M']
TH = 0.85
def zr(l): return (0.0, TH) if l == 0 else (l+0.1, l+0.1+TH)
# edges (driver gear -> driven gear)
edges = [('barrel','A_a'),('A_b','B_a'),('B_b','C_a'),('C_b','S_a'),('A_b','M_a'),('M_b','T_a'),('T_b','H_a')]
teeth = {k: v[1] for k, v in G.items()}; teeth['barrel'] = 96
pos['barrel'] = barrel
phase = {'barrel': 0.0, 'A_b': 0.0, 'B_b': 0.0, 'C_b': 0.0, 'M_b': 0.0, 'T_b': 0.0}
# gears on same mobile are free to take own phase, except via edges; propagate
def mesh_phase(d, n):
    p1, p2 = pos[d], pos[n]
    phi = math.atan2(p2[1]-p1[1], p2[0]-p1[0])
    z1, z2 = teeth[d], teeth[n]
    assert abs(dist(p1, p2) - M_*(z1+z2)/2) < 1e-9, (d, n, dist(p1, p2), M_*(z1+z2)/2)
    f1 = ((phi - phase[d])/(2*math.pi/z1)) % 1
    f2 = (0.5 - f1) % 1
    phase[n] = phi + math.pi - f2*2*math.pi/z2
for d, n in edges: mesh_phase(d, n)

mob_gears = {}
for k, v in G.items(): mob_gears.setdefault(v[0], []).append(k)

ARB, HOLE = 0.5, 0.6
ZBOT = -1.3
tops = {'A': 1.95, 'B': 2.95, 'C': 3.95, 'S': 7.9, 'T': 5.95, 'M': 9.5}
def body(name):
    at = P[name]
    parts = [cyl(1.0, ZBOT, -0.7, at=at), cyl(ARB, ZBOT, tops[name], at=at)]
    lows = []
    for g in mob_gears[name]:
        l = G[g][2]; z0, z1 = zr(l)
        gg = gear(teeth[g], phase[g], z0, z1).translate([at[0], at[1], 0])
        parts.append(gg); lows.append(z0)
    zl = min(lows)
    if zl > 0.01: parts.append(cyl(1.0, 0.0, zl+0.2, at=at))
    return K.union(parts)

def hbody():
    at = P['H']
    g = gear(48, phase['H_a'], *zr(5)).translate([at[0], at[1], 0])
    tube = cyl(1.3, zr(5)[0], 8.7, at=at)
    return K.union([g, tube]) - cyl(0.65, 5.0, 8.8, at=at)

def bar(at, length, tail, w, z0, z1, hub_r, hole=0.0):
    b = K.box([at[0]-tail, at[1]-w/2, z0], [at[0]+length, at[1]+w/2, z1])
    h = cyl(hub_r, z0, z1, at=at)
    s = K.union([b, h])
    if hole: s = s - cyl(hole, z0-1, z1+1, at=at)
    return s

parts = {}
for n in 'ABCSTM': parts[n+'_body'] = body(n)
parts['H_body'] = hbody()
parts['hand_sec'] = bar(P['S'], 5.8, 1.5, 0.5, 7.4, 7.9, 1.0)
parts['hand_hour'] = bar(P['H'], 6.0, 1.5, 0.9, 8.2, 8.7, 1.3, hole=0.65)
parts['hand_min'] = bar(P['M'], 9.5, 1.5, 0.7, 8.75, 9.5, 1.5)
# rotate hands initial angles for variety
def rot(m, at, deg):
    return m.translate([-at[0], -at[1], 0]).rotate([0, 0, deg]).translate([at[0], at[1], 0])
parts['hand_sec'] = rot(parts['hand_sec'], P['S'], 40)
parts['hand_hour'] = rot(parts['hand_hour'], P['H'], 100)
parts['hand_min'] = rot(parts['hand_min'], P['M'], 200)

cc = P['M']
plate = cyl(22.5, -0.65, -0.05, 128, at=cc)
for at in [barrel]+[P[k] for k in 'ABCSTM']:
    plate = plate - cyl(HOLE, -1, 0, at=at)
parts['main_plate'] = plate
parts['barrel_cock'] = cyl(1.5, 1.65, 2.65)

os.makedirs('work/parts', exist_ok=True)
for n, m in parts.items(): K.write_stl('work/parts/%s.stl' % n, m)
mov = {
 'case_centre': list(cc),
 'fixed': ['main_plate', 'barrel_cock'],
 'mobiles': {
  'A': {'axis': list(P['A']), 'parts': ['A_body']},
  'B': {'axis': list(P['B']), 'parts': ['B_body']},
  'C': {'axis': list(P['C']), 'parts': ['C_body']},
  'T': {'axis': list(P['T']), 'parts': ['T_body']},
  'S': {'axis': list(P['S']), 'parts': ['S_body', 'hand_sec']},
  'M': {'axis': list(P['M']), 'parts': ['M_body', 'hand_min']},
  'H': {'axis': list(P['H']), 'parts': ['H_body', 'hand_hour']}},
 'meshes': [
  {'driver':'barrel','driver_teeth':96,'driven':'A','driven_teeth':16},
  {'driver':'A','driver_teeth':48,'driven':'B','driven_teeth':12},
  {'driver':'B','driver_teeth':48,'driven':'C','driven_teeth':12},
  {'driver':'C','driver_teeth':60,'driven':'S','driven_teeth':12},
  {'driver':'A','driver_teeth':48,'driven':'M','driven_teeth':36},
  {'driver':'M','driver_teeth':15,'driven':'T','driven_teeth':45},
  {'driver':'T','driver_teeth':12,'driven':'H','driven_teeth':48}],
 'hands': {'hour': {'mobile':'H','part':'hand_hour'}, 'minute': {'mobile':'M','part':'hand_min'}, 'seconds': {'mobile':'S','part':'hand_sec'}}}
json.dump(mov, open('work/movement.json', 'w'), indent=1)
print({k: [round(c, 3) for c in v] for k, v in P.items()})
