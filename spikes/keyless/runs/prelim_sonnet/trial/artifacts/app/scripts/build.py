import sys, os, json, math, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from lib import *
from manifold3d import Manifold

OUT = '/app/submission/parts'
os.makedirs(OUT, exist_ok=True)
P = {}   # name -> Manifold

# ---------------- parameters ----------------
ARB = (2.15, 4.157)
WC = (1.55, 0.0)     # W axis
SC = (7.05, 0.0)     # S axis
CLK = (4.10, 2.40)   # click pivot
RING_R = 2.0; NPIN = 20; PIN_R = 0.125
H_TOOTH = 0.25; CLR = 0.03; NFACE = 8; PSI_A = 0.0; OFS = 0.5
R_IN, R_OUT = 0.45, 0.70
STEM_R = 0.35

# ---------------- face teeth ----------------
def hull_pts(pts):
    return Manifold.hull_points([tuple(p) for p in pts])

def face_P():
    p = 360.0 / NFACE; ns = 15
    parts = []
    for t in range(NFACE):
        for i in range(ns):
            a0 = math.radians(PSI_A + t * p + i * p / ns)
            a1 = math.radians(PSI_A + t * p + (i + 1) * p / ns)
            h0 = H_TOOTH * i / ns; h1 = H_TOOTH * (i + 1) / ns
            pts = []
            for r in (R_IN, R_OUT):
                for a, h in ((a0, h0), (a1, h1)):
                    pts.append((r * math.cos(a), r * math.sin(a), h))
                    pts.append((r * math.cos(a), r * math.sin(a), -0.01))
            parts.append(hull_pts(pts))
    return Manifold.batch_boolean(parts, 0) if False else union(parts)

def union(ms):
    r = ms[0]
    for m in ms[1:]:
        r = r + m
    return r

def face_K():
    p = 360.0 / NFACE; ns = 15
    top = H_TOOTH + CLR
    parts = []
    for t in range(NFACE):
        for i in range(ns):
            a0 = math.radians(PSI_A + OFS + t * p + i * p / ns)
            a1 = math.radians(PSI_A + OFS + t * p + (i + 1) * p / ns)
            h0 = CLR + H_TOOTH * i / ns; h1 = CLR + H_TOOTH * (i + 1) / ns
            pts = []
            for r in (R_IN, R_OUT):
                for a, h in ((a0, h0), (a1, h1)):
                    pts.append((r * math.cos(a), r * math.sin(a), h))
                    pts.append((r * math.cos(a), r * math.sin(a), top + 0.01))
            parts.append(hull_pts(pts))
    return union(parts)

# ---------------- stem ----------------
shaft = circ(STEM_R, -1.2, 13.6)
collar = circ(0.55, 0.95, 1.3)
G = gear(10, 0.0, 3.95, 4.35)
crown = circ(1.0, 12.9, 13.6)
stem = to_x_axis_helper = None
def xax(m):  # local z-axis built solid -> x axis
    return to_x_axis(m)
stem = xax(shaft + collar + G + crown)
P['stem'] = stem

# ---------------- stem washer (fixed) ----------------
P['stem_washer'] = xax(tube(0.8, 0.4, -1.0, -0.7))

# ---------------- P: loose winding pinion ----------------
spur = gear(10, 0.0, -0.7, -0.2) - circ(0.4, -1, 1)
hubP = tube(0.7, 0.4, -0.2, 0.0)
teethP = face_P() - circ(0.4, -1, 1)
P['pinion'] = xax(spur + hubP + teethP)

# ---------------- K: clutch sleeve ----------------
top = H_TOOTH + CLR
body = tube(0.75, 0.4, top, 0.6)
cav = tube(0.75, 0.6, 0.6, 1.3)
wall = tube(0.75, 0.4, 1.3, 1.6)
tK = face_K() - circ(0.4, -1, 3)
tK = tK - circ(R_OUT + 0.0, 0, 0)  if False else tK
K = body + cav + wall + tK
P['clutch'] = xax(K)

# ---------------- W ----------------
def pins(c, ring, n, ang0, z0, z1, r=PIN_R):
    ms = []
    for k in range(n):
        a = math.radians(ang0 + 360.0 * k / n)
        ms.append(circ(r, z0, z1, (c[0] + ring * math.cos(a), c[1] + ring * math.sin(a)), 16))
    return union(ms)


def rackpins(c, ring, n, ang0, sign, sb=1.66, rad=0.2):
    wp = 0.314 - 0.06; t = math.tan(math.radians(20))
    ms = []
    def wid(s): return wp + 2 * (s - 1.0) * t
    for k in range(n):
        a = math.radians(ang0 + 360.0 * k / n)
        cx = c[0] + ring * math.cos(a); cy = c[1] + ring * math.sin(a)
        rd = np.array([math.cos(a), math.sin(a)]); tg = np.array([-math.sin(a), math.cos(a)])
        pts = []
        for s_ in (0.8, 1.2, sb):
            hw = wid(min(s_, 1.2)) / 2
            for dr in (-rad, rad):
                for dt in (-hw, hw):
                    p2 = np.array([cx, cy]) + dr * rd + dt * tg
                    pts.append((p2[0], p2[1], sign * s_))
        ms.append(hull_pts(pts))
    return union(ms)

ang_WA = math.degrees(math.atan2(ARB[1] - WC[1], ARB[0] - WC[0]))
W = circ(2.2, 1.65, 1.95, WC) + rackpins(WC, RING_R, NPIN, 180.0, +1, 1.66) \
    + circ(0.6, 1.94, 2.01, WC) + gear(12, ang_WA, 2.0, 2.5, WC)
W = W - circ(0.28, 0, 4, WC)
P['crown_wheel'] = W

# ---------------- S ----------------
ang_S = math.degrees(math.atan2(-4.157 - SC[1], 4.65 - SC[0]))
S = circ(2.2, -1.85, -1.55, SC) + rackpins(SC, RING_R, NPIN, 180.0, -1, 1.56) \
    + circ(0.6, -1.91, -1.84, SC) + gear(12, ang_S, -2.4, -1.9, SC)
S = S - circ(0.28, -3, 0, SC)
P['setting_wheel'] = S

# ---------------- barrel parts: gear + ratchet ----------------
ang_R = ang_WA + 180.0 + 6.0
Rg = gear(30, ang_R, 2.0, 2.5, ARB)
hub = tube(0.8, 0.62, 1.5, 2.01, ARB)
def ratchet2d(nt, r_root, r_tip, a0=0.0, flat=2.0):
    pts = []
    p = 360.0 / nt
    for k in range(nt):
        ak = a0 + k * p
        # wall at ak: root->tip, then ramp down to next root
        pts.append((r_root, ak)); pts.append((r_tip, ak))
        pts.append((r_root, ak + p - flat))
    out = []
    for r, a in pts:
        a = math.radians(a); out.append((r * math.cos(a), r * math.sin(a)))
    return out
rat = poly_extrude(ratchet2d(20, 1.3, 1.6, 0.0), 1.0, 1.5).translate((ARB[0], ARB[1], 0))
rat = rat - circ(0.62, 0, 4, ARB)
P['ratchet_gear'] = Rg + hub + rat

# ---------------- click ----------------
def click2d_parts():
    B1 = (3.46, 4.127)
    # ramp line from R(-2deg) to T(-18deg)
    def pol(r, a):
        a = math.radians(a); return np.array([ARB[0] + r * math.cos(a), ARB[1] + r * math.sin(a)])
    R2 = pol(1.3, -2.0); T = pol(1.6, -18.0)
    d = (T - R2); d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    if n[0] < 0: n = -n
    off = 0.03
    B2 = R2 + off * n
    E = B2 + d * 1.0
    return B1, B2, E
B1, B2, E = click2d_parts()
def prism_hull(pts2, z0, z1):
    pts = [(x, y, z) for (x, y) in pts2 for z in (z0, z1)]
    return hull_pts(pts)
ZC0, ZC1 = 1.0, 1.5
beak = prism_hull([B1, B2, (E[0], E[1]), (E[0], B1[1])], ZC0, ZC1)
# rod from beak to pivot boss
bosspts = [(CLK[0] + 0.45 * math.cos(math.radians(a)), CLK[1] + 0.45 * math.sin(math.radians(a))) for a in range(0, 360, 20)]
rod = prism_hull([(E[0], B1[1]), (E[0] + 0.35, B1[1]), (E[0], E[1])] + bosspts, ZC0, ZC1)
click = beak + rod - circ(0.18, 0, 4, CLK)
P['click'] = click

# ---------------- studs ----------------
P['stud_w'] = circ(0.25, 1.35, 2.6, WC) + circ(0.7, 1.35, 1.65, WC)
P['stud_s'] = circ(0.25, -2.6, -1.25, SC) + circ(0.7, -1.55, -1.25, SC)
P['stud_click'] = circ(0.15, 0.7, 1.8, CLK) + circ(0.55, 0.7, 1.0, CLK) + circ(0.55, 1.5, 1.8, CLK)

for k, m in P.items():
    t = save(m, f'{OUT}/{k}.stl')
    print(k, len(t.faces), round(t.volume, 3), t.is_watertight, t.bounds.round(2).tolist())

cfg = {
 'mobiles': {
  'stem': {'kind': 'stem', 'parts': ['stem']},
  'barrel': {'kind': 'barrel', 'parts': ['ratchet_gear']},
  'pinion': {'kind': 'free', 'dof': 'rot', 'point': [0, 0, 0], 'direction': [1, 0, 0], 'parts': ['pinion']},
  'clutch': {'kind': 'spring', 'dof': 'slide', 'direction': [1, 0, 0], 'rest': -1, 'on_stem': True, 'parts': ['clutch']},
  'crown_wheel': {'kind': 'free', 'dof': 'rot', 'point': [WC[0], WC[1], 0], 'direction': [0, 0, 1], 'parts': ['crown_wheel']},
  'setting_wheel': {'kind': 'free', 'dof': 'rot', 'point': [SC[0], SC[1], 0], 'direction': [0, 0, 1], 'parts': ['setting_wheel']},
  'click': {'kind': 'spring', 'dof': 'rot', 'point': [CLK[0], CLK[1], 0], 'direction': [0, 0, 1], 'rest': 1, 'parts': ['click']},
 },
 'fixed': ['stem_washer', 'stud_w', 'stud_s', 'stud_click'],
}
json.dump(cfg, open('/app/submission/keyless.json', 'w'), indent=1)
