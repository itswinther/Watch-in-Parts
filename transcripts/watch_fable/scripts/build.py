import sys, os, json, math
sys.path.insert(0, 'tools')
import numpy as np
import manifold3d as m3
from geometry import core

PA = math.radians(25.0)
def inv(a): return math.tan(a) - a

def gear(n, m, z0, z1, phase, axis, backlash=0.01, nf=10):
    rp = n*m/2; rb = rp*math.cos(PA); ra = rp+m; rr = rp-1.25*m
    s = math.pi*m/2 - backlash
    def psi(r):
        r = max(r, rb)
        return s/(2*rp) + inv(PA) - inv(math.acos(min(1.0, rb/r)))
    radii = []
    if rr < rb: radii.append(rr)
    radii += list(np.linspace(max(rb, rr), ra, nf))
    pts = []
    pitch = 2*math.pi/n
    for k in range(n):
        c = phase + k*pitch
        for r in radii:                 # right flank (lower angle), going outward
            a = c - psi(r); pts.append((r*math.cos(a), r*math.sin(a)))
        for r in reversed(radii):
            a = c + psi(r); pts.append((r*math.cos(a), r*math.sin(a)))
    cs = m3.CrossSection([pts], m3.FillRule.Positive)
    return cs.extrude(z1-z0).translate([axis[0], axis[1], z0])

def cyl(ax, z0, z1, r, seg=64):
    return m3.Manifold.cylinder(z1-z0, r, r, seg).translate([ax[0], ax[1], z0])

def mate(phi_a, na, A, nb, B):
    th = math.atan2(B[1]-A[1], B[0]-A[0])
    pa, pb = 2*math.pi/na, 2*math.pi/nb
    u = (phi_a - th)/pa
    return th + math.pi - u*pb + pb/2

def hand(ax, z0, z1, hub_r, bore, length, width):
    h = cyl(ax, z0, z1, hub_r)
    bar = core.box((ax[0]-width/2, ax[1], z0), (ax[0]+width/2, ax[1]+length-width, z1))
    tip = m3.Manifold.cylinder(z1-z0, width/2, width/2, 16).translate([ax[0], ax[1]+length-width/2-0.001, z0])
    h = core.union([h, bar, tip])
    if bore: h = h - cyl(ax, z0-1, z1+1, bore)
    return h

# ---- layout ----
O = (0.0, 0.0)
I = (11.6, 0.0)
C = (14.8, 0.0)
M1, M2 = 0.15, 16.2/102
T = (C[0], C[1]+8.1)
MW = (C[0], C[1]-4.8)
MM1, MM2 = 0.2, 0.16
CL = 0.08

parts = {}
# idler
ph_i = mate(0.0, 96, O, 20, I)
idler = core.union([gear(20, 0.2, 0, 1, ph_i, I), cyl(I, -1.4, 0.05, 0.6), cyl(I, -2.2, -1.3, 0.3)])
parts['idler'] = idler
# minute (centre) mobile
ph_cp = mate(ph_i, 20, I, 12, C)
bore_m = 0.25 + CL
minute = core.union([gear(12, 0.2, 0, 1.15, ph_cp, C), gear(96, M1, 1.1, 1.9, 0.0, C),
                     cyl(C, 0, 6.8, 0.65), gear(12, MM1, 3.0, 3.8, 0.0, C)]) - cyl(C, -1, 8, bore_m)
parts['centre'] = minute
parts['minute_hand'] = hand(C, 6.4, 6.8, 1.1, bore_m, 8.5, 0.5)
# third
ph_tp = mate(0.0, 96, C, 12, T)
third = core.union([gear(12, M1, 1.1, 1.9, ph_tp, T), gear(90, M2, -1.4, -0.6, 0.0, T), cyl(T, -2.2, 2.7, 0.3)])
parts['third'] = third
# seconds
ph_sp = mate(0.0, 90, T, 12, C)
sec = core.union([gear(12, M2, -1.4, -0.4, ph_sp, C), cyl(C, -0.45, -0.1, 0.8), cyl(C, -2.2, 7.3, 0.25)])
parts['fourth'] = sec
parts['seconds_hand'] = hand(C, 7.0, 7.3, 0.6, 0, 9.2, 0.25)
# motion work
ph_mw = mate(0.0, 12, C, 36, MW)
motion = core.union([gear(36, MM1, 3.0, 3.8, ph_mw, MW), gear(12, MM2, 3.75, 4.7, 0.0, MW), cyl(MW, 2.3, 5.3, 0.3)])
parts['motion'] = motion
ph_hw = mate(0.0, 12, MW, 48, C)
bore_h = 0.65 + CL
hour = core.union([gear(48, MM2, 3.9, 4.7, ph_hw, C), cyl(C, 3.9, 6.2, 1.0)]) - cyl(C, 3, 7, bore_h)
parts['hour_wheel'] = hour
parts['hour_hand'] = hand(C, 5.8, 6.2, 1.5, bore_h, 6.0, 0.7)

# ---- frame ----
circles = [(O, 9.8), (C, 9.3), (T, 90*M2/2+M2), (MW, 3.8), (I, 2.2)]
from scipy.optimize import minimize
f = lambda k: max(math.hypot(k[0]-c[0], k[1]-c[1])+r for c, r in circles)
K = minimize(f, [8, 2], method='Nelder-Mead').x
K = (round(float(K[0]), 3), round(float(K[1]), 3)); Renc = f(K)
R = Renc + 2.2
print('case centre', K, 'enclosing', Renc, 'plate R', R)
def disc(z0, z1): return cyl(K, z0, z1, R, 128)
frame = [disc(-2.4, -1.5), disc(2.0, 2.9), disc(4.8, 5.5),
         cyl(O, -1.5, -0.1, 1.5), cyl(O, 1.1, 2.0, 1.5)]
for k in range(4):
    a = math.radians(45+90*k)
    frame.append(cyl((K[0]+(R-1.0)*math.cos(a), K[1]+(R-1.0)*math.sin(a)), -2.4, 5.5, 0.8))
frame = core.union(frame)
holes = [cyl(O, -3, 3.5, 0.5+CL),            # barrel arbor, both plates
         cyl(I, -3, -1.0, 0.3+CL),
         cyl(C, -3, -1.0, 0.25+CL),          # seconds pivot
         cyl(T, -3, 3.5, 0.3+CL),
         cyl(C, 1.95, 3.0, 0.65+CL),         # minute tube through P1
         cyl(MW, 1.95, 6, 0.3+CL),           # motion pivots P1 and P2
         cyl(C, 4.7, 6, 1.0+CL)]             # hour tube through dial
frame = frame - core.union(holes)
parts['frame'] = frame

for n, p in parts.items():
    assert len(p.decompose()) == 1, n
    core.write_stl('work/parts/%s.stl' % n, p)
doc = {"case_centre": list(K), "fixed": ["frame"],
  "mobiles": {
    "idler": {"axis": list(I), "parts": ["idler"]},
    "minute": {"axis": list(C), "parts": ["centre", "minute_hand"]},
    "third": {"axis": list(T), "parts": ["third"]},
    "seconds": {"axis": list(C), "parts": ["fourth", "seconds_hand"]},
    "motion": {"axis": list(MW), "parts": ["motion"]},
    "hour": {"axis": list(C), "parts": ["hour_wheel", "hour_hand"]}},
  "meshes": [
    {"driver": "barrel", "driver_teeth": 96, "driven": "idler", "driven_teeth": 20},
    {"driver": "idler", "driver_teeth": 20, "driven": "minute", "driven_teeth": 12},
    {"driver": "minute", "driver_teeth": 96, "driven": "third", "driven_teeth": 12},
    {"driver": "third", "driver_teeth": 90, "driven": "seconds", "driven_teeth": 12},
    {"driver": "minute", "driver_teeth": 12, "driven": "motion", "driven_teeth": 36},
    {"driver": "motion", "driver_teeth": 12, "driven": "hour", "driven_teeth": 48}],
  "hands": {"hour": {"mobile": "hour", "part": "hour_hand"},
            "minute": {"mobile": "minute", "part": "minute_hand"},
            "seconds": {"mobile": "seconds", "part": "seconds_hand"}}}
json.dump(doc, open('work/movement.json', 'w'), indent=1)
