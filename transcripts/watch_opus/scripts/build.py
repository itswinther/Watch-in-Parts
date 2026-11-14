import sys, os, json, math
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import manifold3d as m3
from geometry import core
WORK = os.path.join(os.path.dirname(__file__), '..', 'work')
os.makedirs(os.path.join(WORK, 'parts'), exist_ok=True)
PA = math.radians(25)
SEG = 96
BL = float(os.environ.get('BL', '0.02'))

def inv(a): return math.tan(a) - a

def gear_poly(N, m, phase, bl=BL, bore=None):
    r = m * N / 2; rb = r * math.cos(PA); ra = r + m; rf = r - 1.25 * m
    psi = (math.pi * m / 2 - bl) / (2 * r)
    def half(rho):
        if rho <= rb: return psi + inv(PA)
        return psi + inv(PA) - inv(math.acos(rb / rho))
    r0 = max(rb, rf)
    rhos = [rf] + list(np.linspace(r0, ra, 12))
    pts = []
    pitch = 2 * math.pi / N
    for k in range(N):
        c = phase + k * pitch
        fl = [(rho, c - half(rho)) for rho in rhos]          # leading flank (cw side)
        fr = [(rho, c + half(rho)) for rho in reversed(rhos)]
        tipa, tipb = c - half(ra), c + half(ra)
        tip = [(ra, t) for t in np.linspace(tipa, tipb, 4)[1:-1]]
        # root arc to next tooth
        ra0 = c + half(rf); ra1 = c + pitch - half(rf)
        root = [(rf, t) for t in np.linspace(ra0, ra1, 5)[1:-1]]
        pts += fl + tip + fr + root
    xy = [(p * math.cos(t), p * math.sin(t)) for p, t in pts]
    return xy

def gear(N, m, phase, z0, z1, axis, bore=None):
    cs = m3.CrossSection([gear_poly(N, m, phase)])
    g = cs.extrude(z1 - z0).translate([0, 0, z0])
    if bore:
        g = g - core.cyl_z(0, 0, z0 - 1, z1 + 1, bore, SEG)
    return g.translate([axis[0], axis[1], 0])

def cyl(axis, z0, z1, r, rin=None):
    c = core.cyl_z(axis[0], axis[1], z0, z1, r, SEG)
    if rin:
        c = c - core.cyl_z(axis[0], axis[1], z0 - 1, z1 + 1, rin, SEG)
    return c

def ang(P, Q): return math.atan2(Q[1] - P[1], Q[0] - P[0])

def phase_for(Q, Nd, thd, P, Nn):
    psi = ang(Q, P)
    delta = thd - psi
    return psi + math.pi + math.pi / Nn - delta * Nd / Nn

# ---- layout ----
B = (0.0, 0.0)
S = (10.8, 0.0)
C = (8.17874275, 9.23520495)
def at(P, r, Q):  # exact distance r from P toward Q
    a = ang(P, Q); return (P[0] + r * math.cos(a), P[1] + r * math.sin(a))
C = at(S, 9.6, C)
T = at(C, 9.0, (5.08639873, 17.68727029))
M = at(C, 6.0, (11.56892719, 14.18562407))
CC = (2.6268, 7.9716)

# gears
m_bp = 0.2;  Z_B, Z_p1 = 96, 12
m_wp = 0.2;  Z_W2, Z_p2 = 48, 48
m_c3 = 9.0 * 2 / (90 + 12); Z_c, Z_3p = 90, 12
m_3s = 9.0 * 2 / (96 + 12); Z_3, Z_sp = 96, 12
m_cm = 0.25; Z_cp, Z_mw = 12, 36
m_mh = 0.2;  Z_mp, Z_hw = 12, 48

# z layers
L0 = (0.0, 1.0); L1 = (1.15, 1.95); L2 = (2.1, 2.9); L3 = (3.05, 3.85); L4 = (4.0, 4.8)
TOP = (4.95, 5.75); PLATE = (-1.5, -0.1)
HH = (5.9, 6.2); MH = (6.35, 6.65); SH = (6.8, 7.1)
R_SEC = 0.3; R_MIN_IN = 0.36; R_MIN_OUT = 0.6; R_HR_IN = 0.66; R_HR_OUT = 0.95; R_TOPHOLE = 1.01
R_ARB = 0.4; R_HOLE = 0.45; R_COLLAR = 0.8

parts = {}
ph_p1 = phase_for(B, Z_B, 0.0, S, Z_p1)
ph_p2 = phase_for(S, Z_W2, 0.0, C, Z_p2)
ph_3p = phase_for(C, Z_c, 0.0, T, Z_3p)
ph_sp = phase_for(T, Z_3, 0.0, C, Z_sp)
ph_mw = phase_for(C, Z_cp, 0.0, M, Z_mw)
ph_hw = phase_for(M, Z_mp, 0.0, C, Z_hw)

# S mobile (second wheel): p1, W2, arbor, collar
parts['s_body'] = core.union([
    gear(Z_p1, m_bp, ph_p1, *L0, S), gear(Z_W2, m_wp, 0.0, *L1, S),
    cyl(S, -1.0, 5.5, R_ARB), cyl(S, L4[0] + 0.3, TOP[0] - 0.1, R_COLLAR)])
# T mobile (third wheel)
parts['t_body'] = core.union([
    gear(Z_3, m_3s, 0.0, *L0, T), gear(Z_3p, m_c3, ph_3p, *L2, T),
    cyl(T, -1.0, 5.5, R_ARB), cyl(T, L4[0] + 0.3, TOP[0] - 0.1, R_COLLAR)])
# M mobile (minute wheel of motion work)
parts['m_body'] = core.union([
    gear(Z_mw, m_cm, ph_mw, *L3, M), gear(Z_mp, m_mh, 0.0, *L4, M),
    cyl(M, L3[0], 5.5, R_ARB)])
# seconds mobile (centre)
parts['sec_body'] = core.union([gear(Z_sp, m_3s, ph_sp, *L0, C), cyl(C, -1.0, SH[1], R_SEC)])
def hand(axis, z0, z1, rin, rhub, length, width, tail=1.0):
    hub = cyl(axis, z0, z1, rhub, rin)
    blade = core.box((-width / 2, -tail, z0), (width / 2, length, z1)).translate([axis[0], axis[1], 0])
    h = hub + blade
    if rin:
        h = h - core.cyl_z(axis[0], axis[1], z0 - 1, z1 + 1, rin, SEG)
    return h
parts['sec_hand'] = hand(C, *SH, None, 0.9, 7.5, 0.25, 1.5)
# minute mobile (centre)
parts['min_body'] = core.union([
    gear(Z_p2, m_wp, ph_p2, *L1, C, bore=R_MIN_IN), gear(Z_c, m_c3, 0.0, *L2, C, bore=R_MIN_IN),
    gear(Z_cp, m_cm, 0.0, *L3, C, bore=R_MIN_IN), cyl(C, L1[0], MH[1], R_MIN_OUT, R_MIN_IN)])
parts['min_hand'] = hand(C, *MH, R_MIN_IN, 1.2, 7.0, 0.5)
# hour mobile (centre)
parts['hr_body'] = core.union([gear(Z_hw, m_mh, ph_hw, *L4, C, bore=R_HR_IN), cyl(C, L4[0], HH[1], R_HR_OUT, R_HR_IN)])
parts['hr_hand'] = hand(C, *HH, R_HR_IN, 1.3, 5.5, 0.8)

# fixed
holes_plate = [(B, 0.56), (S, R_HOLE), (T, R_HOLE), (C, R_SEC + 0.05)]
plate = cyl(CC, *PLATE, 19.0)
for P, r in holes_plate:
    plate = plate - core.cyl_z(P[0], P[1], PLATE[0] - 1, PLATE[1] + 1, r, SEG)
top = cyl(CC, *TOP, 19.0)
cock = cyl(B, 1.1, TOP[0] + 0.01, 1.5)
pillars = [cyl(p, PLATE[1] - 0.01, TOP[0] + 0.01, 1.0) for p in json.loads(os.environ.get('PILLARS', '[]'))]
top = core.union([top, cock] + pillars + [plate])
for P, r in [(B, 0.56), (S, R_HOLE), (T, R_HOLE), (M, R_HOLE), (C, R_TOPHOLE)]:
    top = top - core.cyl_z(P[0], P[1], 1.0, 9, r, SEG)
parts['frame'] = top

for n, p in parts.items():
    assert len(p.decompose()) == 1, n
    core.write_stl(os.path.join(WORK, 'parts', n + '.stl'), p)

doc = {
    "case_centre": list(CC),
    "fixed": ["frame"],
    "mobiles": {
        "second": {"axis": list(S), "parts": ["s_body"]},
        "third": {"axis": list(T), "parts": ["t_body"]},
        "minutewheel": {"axis": list(M), "parts": ["m_body"]},
        "seconds": {"axis": list(C), "parts": ["sec_body", "sec_hand"]},
        "minute": {"axis": list(C), "parts": ["min_body", "min_hand"]},
        "hour": {"axis": list(C), "parts": ["hr_body", "hr_hand"]},
    },
    "meshes": [
        {"driver": "barrel", "driver_teeth": Z_B, "driven": "second", "driven_teeth": Z_p1},
        {"driver": "second", "driver_teeth": Z_W2, "driven": "minute", "driven_teeth": Z_p2},
        {"driver": "minute", "driver_teeth": Z_c, "driven": "third", "driven_teeth": Z_3p},
        {"driver": "third", "driver_teeth": Z_3, "driven": "seconds", "driven_teeth": Z_sp},
        {"driver": "minute", "driver_teeth": Z_cp, "driven": "minutewheel", "driven_teeth": Z_mw},
        {"driver": "minutewheel", "driver_teeth": Z_mp, "driven": "hour", "driven_teeth": Z_hw},
    ],
    "hands": {
        "hour": {"mobile": "hour", "part": "hr_hand"},
        "minute": {"mobile": "minute", "part": "min_hand"},
        "seconds": {"mobile": "seconds", "part": "sec_hand"},
    },
}
json.dump(doc, open(os.path.join(WORK, 'movement.json'), 'w'), indent=1)
print('ok', {n: p.num_tri() for n, p in parts.items()})
