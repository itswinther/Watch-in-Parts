import math, json, os, sys
import cadquery as cq
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
import kernel

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
PARTS = os.path.join(ROOT, 'work', 'parts')
os.makedirs(PARTS, exist_ok=True)
PA = math.radians(25)
BACK = 0.02


def inv(a):
    return math.tan(a) - a


def gear_pts(N, m, phase_deg, cx, cy, add=1.0, ded=1.25, back=BACK):
    rp = N * m / 2
    rb = rp * math.cos(PA)
    ra = rp + add * m
    rf = rp - ded * m
    s = math.pi * m / 2 - back
    half_p = s / (2 * rp) + inv(PA)  # half angle at base circle (involute start)
    def half(r):
        if r <= rb:
            return half_p
        a = math.acos(rb / r)
        return half_p - inv(a)
    rs = [max(rb, rf)]
    nf = 8
    r0 = max(rb, rf)
    flank = [r0 + (ra - r0) * (i / nf) for i in range(nf + 1)]
    pitch = 2 * math.pi / N
    pts = []
    for k in range(N):
        c = math.radians(phase_deg) + k * pitch
        # root point(s) before tooth
        hr = half(flank[0])
        root_gap_start = c - hr
        pts.append((rf, c - hr - 0.0))
        if rf < rb:
            pts.append((rb, c - hr))
        for r in flank[1:]:
            pts.append((r, c - half(r)))
        ht = half(ra)
        pts.append((ra, c))
        for r in reversed(flank[1:]):
            pts.append((r, c + half(r)))
        if rf < rb:
            pts.append((rb, c + hr))
        pts.append((rf, c + hr))
        # root arc midpoint
        pts.append((rf, c + pitch / 2))
    return [(cx + r * math.cos(a), cy + r * math.sin(a)) for r, a in pts]


def gear(N, m, phase, cx, cy, z0, z1, **kw):
    pts = gear_pts(N, m, phase, cx, cy, **kw)
    return cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def cyl(cx, cy, z0, z1, r):
    return cq.Workplane('XY').workplane(offset=z0).center(cx, cy).circle(r).extrude(z1 - z0)


def tube(cx, cy, z0, z1, ri, ro):
    return cq.Workplane('XY').workplane(offset=z0).center(cx, cy).circle(ro).circle(ri).extrude(z1 - z0)


def hand(cx, cy, z0, z1, ri, rhub, length, width):
    hub = tube(cx, cy, z0, z1, ri, rhub)
    blade = cq.Workplane('XY').workplane(offset=z0).center(cx, cy + (rhub * 0.5 + length) / 2).rect(width, length - rhub * 0.5).extrude(z1 - z0)
    return hub.union(blade).cut(cyl(cx, cy, z0 - 1, z1 + 1, ri))


# ---------------- layout
M = (10.5, 0.0)
CENTRE = M
def place(c, d, ang):
    return (c[0] + d * math.cos(math.radians(ang)), c[1] + d * math.sin(math.radians(ang)))
A = (8.747, 0.0)
# exact A: |A|=11.2, |A-M|=7.0
ax = (11.2**2 - 7.0**2 + M[0]**2) / (2 * M[0]); A = (ax, math.sqrt(11.2**2 - ax**2))
X = place(M, 6.75, -50)
S = place(X, 6.375, -50)
N = place(M, 4.5, 90)

def angle(p, q):
    return math.degrees(math.atan2(q[1] - p[1], q[0] - p[0]))

def driven_phase(drv_c, drv_N, drv_phase, dvn_c, dvn_N):
    th = angle(drv_c, dvn_c)
    pitch = 360.0 / drv_N
    eps = (th - drv_phase) % pitch  # driver tooth at th - eps
    return th + 180 + 180.0 / dvn_N + eps * drv_N / dvn_N

# z layout
L0 = (0.0, 1.0); L1 = (1.2, 2.0); L2 = (2.2, 3.0); L3 = (3.2, 4.0)
COL = (4.1, 4.4); TP = (4.5, 5.5); BP = (-1.5, -0.2)
U0 = (5.6, 6.4); U1 = (6.6, 7.4)
HH = (8.4, 8.8); MH = (8.9, 9.3); SH = (9.4, 9.8)
CAP = (7.6, 8.2)
CL = 0.06

parts = {}; mobiles = {}; meshes = []
# A
pa = driven_phase((0, 0), 96, 0.0, A, 16)
parts['a_pinion'] = gear(16, 0.2, pa, *A, *L0)
parts['a_wheel'] = gear(40, 0.2, 0.0, *A, *L1)
RA = 0.35
parts['a_arbor'] = cyl(*A, -0.6, 4.9, RA)
mobiles['third'] = {'axis': list(A), 'parts': ['a_arbor', 'a_pinion', 'a_wheel']}
meshes.append({'driver': 'barrel', 'driver_teeth': 96, 'driven': 'third', 'driven_teeth': 16})
# M (centre / minute)
pm = driven_phase(A, 40, 0.0, M, 30)
RM = 0.4
parts['m_pinion'] = gear(30, 0.2, pm, *M, *L1)
parts['m_wheel'] = gear(80, 0.15, 0.0, *M, *L2)
parts['m_arbor'] = cyl(*M, -0.6, MH[1], RM).union(cyl(*M, *COL, 0.8))
parts['cannon_pinion'] = gear(15, 0.15, 0.0, *M, *U0)
parts['minute_hand'] = hand(*M, *MH, RM - 0.01, 0.9, 5.6, 0.5)
mobiles['centre'] = {'axis': list(M), 'parts': ['m_arbor', 'm_pinion', 'm_wheel', 'cannon_pinion', 'minute_hand']}
meshes.append({'driver': 'third', 'driver_teeth': 40, 'driven': 'centre', 'driven_teeth': 30})
# X
px = driven_phase(M, 80, 0.0, X, 10)
RX = 0.35
parts['x_pinion'] = gear(10, 0.15, px, *X, *L2)
parts['x_wheel'] = gear(75, 0.15, 0.0, *X, *L3)
parts['x_arbor'] = cyl(*X, -0.6, 4.9, RX)
mobiles['fourth'] = {'axis': list(X), 'parts': ['x_arbor', 'x_pinion', 'x_wheel']}
meshes.append({'driver': 'centre', 'driver_teeth': 80, 'driven': 'fourth', 'driven_teeth': 10})
# S
ps = driven_phase(X, 75, 0.0, S, 10)
RS = 0.35
parts['s_pinion'] = gear(10, 0.15, ps, *S, *L3)
parts['s_arbor'] = cyl(*S, -0.6, SH[1], RS).union(cyl(*S, *COL, 0.7))
parts['seconds_hand'] = hand(*S, *SH, RS - 0.01, 0.8, 5.3, 0.45)
mobiles['seconds'] = {'axis': list(S), 'parts': ['s_arbor', 's_pinion', 'seconds_hand']}
meshes.append({'driver': 'fourth', 'driver_teeth': 75, 'driven': 'seconds', 'driven_teeth': 10})
# N (minute wheel of motion work)
pn = driven_phase(M, 15, 0.0, N, 45)
RN = 0.35
parts['n_wheel'] = gear(45, 0.15, pn, *N, *U0)
parts['n_pinion'] = gear(12, 0.15, 0.0, *N, *U1)
parts['n_arbor'] = cyl(*N, 5.1, CAP[0] - 0.1, RN)
mobiles['motion'] = {'axis': list(N), 'parts': ['n_arbor', 'n_wheel', 'n_pinion']}
meshes.append({'driver': 'centre', 'driver_teeth': 15, 'driven': 'motion', 'driven_teeth': 45})
# H (hour wheel)
ph = driven_phase(N, 12, 0.0, M, 48)
HRI = RM + CL
parts['h_wheel'] = gear(48, 0.15, ph, *M, *U1).cut(cyl(*M, U1[0] - 1, U1[1] + 1, HRI))
parts['h_tube'] = tube(*M, U0[1] + 0.1, HH[1], HRI, HRI + 0.3)
parts['hour_hand'] = hand(*M, *HH, HRI, 1.0, 5.1, 0.6)
mobiles['hour'] = {'axis': list(M), 'parts': ['h_tube', 'h_wheel', 'hour_hand']}
meshes.append({'driver': 'motion', 'driver_teeth': 12, 'driven': 'hour', 'driven_teeth': 48})

# fixed
PR = 19.5
bp = cyl(*CENTRE, *BP, PR)
for c, r, zb in [((0, 0), 0.5, -1.0), (A, RA, -0.6), (M, RM, -0.6), (X, RX, -0.6), (S, RS, -0.6)]:
    bp = bp.cut(cyl(*c, zb - 0.1, BP[1] + 1, r + CL))
parts['bottom_plate'] = bp
tp = cyl(*CENTRE, *TP, PR).union(cyl(0, 0, 1.4, TP[0] + 0.01, 1.0))
tp = tp.cut(cyl(0, 0, 1.0, 1.7, 0.5 + CL))
for c, r in [(A, RA), (X, RX)]:
    tp = tp.cut(cyl(*c, TP[0] - 1, 5.0, r + CL))
for c, r in [(M, RM), (S, RS)]:
    tp = tp.cut(cyl(*c, TP[0] - 1, TP[1] + 1, r + CL))
tp = tp.cut(cyl(*N, 5.0, TP[1] + 1, RN + CL))
parts['top_plate'] = tp
cap = cyl(*N, *CAP, 1.0)
parts['n_cap'] = cap
fixed = ['bottom_plate', 'top_plate', 'n_cap']

for name, wp in parts.items():
    kernel.write_step(os.path.join(PARTS, name + '.step'), wp)

mv = {'case_centre': list(CENTRE), 'fixed': fixed, 'mobiles': mobiles, 'meshes': meshes,
      'hands': {'hour': {'mobile': 'hour', 'part': 'hour_hand'},
                'minute': {'mobile': 'centre', 'part': 'minute_hand'},
                'seconds': {'mobile': 'seconds', 'part': 'seconds_hand'}}}
json.dump(mv, open(os.path.join(ROOT, 'work', 'movement.json'), 'w'), indent=1)
print('ok', len(parts))
