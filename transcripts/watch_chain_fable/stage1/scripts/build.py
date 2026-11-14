import sys, os, json, math
import numpy as np
sys.path.insert(0, 'tools')
import kernel as K
import manifold3d as m3

PA = math.radians(25)
def inv(a): return math.tan(a) - a

def gear2d(N, m, phase, bl=0.015, npts=10):
    r = N*m/2; rb = r*math.cos(PA); ra = r+m; rf = r-1.25*m
    s = math.pi*m/2 - bl
    half0 = s/(2*r) + inv(PA)
    def half(rho):
        return half0 - inv(math.acos(min(1.0, rb/rho)))
    rs = max(rb, rf)
    rhos = np.linspace(rs, ra, npts)
    pts = []
    for k in range(N):
        c = phase + 2*math.pi*k/N
        fl = [(rho, half(rho)) for rho in rhos]
        seq = []
        if rf < rb:
            seq.append((rf, half(rb)))
        seq += fl
        # right flank (negative angle) from root to tip, then left flank tip to root
        for rho, h in seq:
            pts.append((rho*math.cos(c-h), rho*math.sin(c-h)))
        for rho, h in reversed(seq):
            pts.append((rho*math.cos(c+h), rho*math.sin(c+h)))
    return m3.CrossSection([np.array(pts)])

def gear(N, m, phase, z0, z1, ax, bl=0.015):
    return gear2d(N, m, phase, bl).extrude(z1-z0).translate([ax[0], ax[1], z0])

def cyl(ax, z0, z1, r): return K.cyl_z(ax[0], ax[1], z0, z1, r)

def driven_phase(pd, Nd, Nn, axd, axn):
    """tooth-centre phase for the driven gear given driver tooth phase pd"""
    th = math.atan2(axn[1]-axd[1], axn[0]-axd[0])
    pitch = 2*math.pi/Nd
    delta = (th - pd) % pitch
    return th + math.pi + delta*Nd/Nn + math.pi/Nn

O = (0.0, 0.0)
A = (0.0, 12.0)
a = math.radians(-30)
C = (A[0]+10.5*math.cos(a), A[1]+10.5*math.sin(a))
b = math.radians(-8)
T = (C[0]+9.18*math.cos(b), C[1]+9.18*math.sin(b))
g = math.radians(100)
M = (C[0]+6.0*math.cos(g), C[1]+6.0*math.sin(g))
CC = (8.3, 4.0)   # case centre
PLATE_R = 21.0
ZB0, ZB1 = -1.0, -0.1       # bottom plate
ZT0, ZT1 = 4.8, 5.7         # top plate
print('C', C, 'T', T, 'M', M, '|C|', math.hypot(*C), '|T|', math.hypot(*T),
      '|T-A|', math.hypot(T[0]-A[0], T[1]-A[1]))

parts = {}
# ---- gears
# mesh1 barrel(96, phase 0) -> A pinion 24
phA = driven_phase(0.0, 96, 24, O, A)
A_pin = gear(24, 0.2, phA, 0.0, 1.0, A)
# mesh2 A wheel 40 m.35 -> centre pinion 20
A_wh = gear(40, 0.35, 0.0, 1.6, 2.6, A)
C_pin = gear(20, 0.35, driven_phase(0.0, 40, 20, A, C), 1.5, 2.7, C)
# mesh3 centre wheel 96 m.17 -> third pinion 12
C_wh = gear(96, 0.17, 0.0, 3.2, 4.2, C)
T_pin = gear(12, 0.17, driven_phase(0.0, 96, 12, C, T), 3.1, 4.3, T)
# mesh4 third wheel 90 m.18 -> seconds pinion 12
T_wh = gear(90, 0.18, 0.0, 0.1, 1.1, T)
S_pin = gear(12, 0.18, driven_phase(0.0, 90, 12, T, C), 0.0, 1.2, C)
# mesh5 cannon 12 m.25 -> minute wheel 36
CAN = gear(12, 0.25, 0.0, 5.8, 7.0, C)
M_wh = gear(36, 0.25, driven_phase(0.0, 12, 36, C, M), 5.8, 6.9, M)
# mesh6 minute pinion 12 m.2 -> hour wheel 48
M_pin = gear(12, 0.2, 0.0, 6.9, 8.3, M)
H_wh = gear(48, 0.2, driven_phase(0.0, 12, 48, M, C), 7.1, 8.3, C)

def arbor(ax, z0=0.0, z1=4.7, r=0.7, rp=0.35):
    return K.union([cyl(ax, z0, z1, r), cyl(ax, z0-0.6, z0+0.1, rp), cyl(ax, z1-0.1, z1+0.6, rp)])

# intermediate mobile A
parts['inter_arbor'] = arbor(A)
parts['inter_pinion'] = A_pin
parts['inter_wheel'] = A_wh
# third mobile
parts['third_arbor'] = arbor(T)
parts['third_wheel'] = T_wh
parts['third_pinion'] = T_pin
# seconds mobile
parts['seconds_arbor'] = K.union([cyl(C, -0.6, 11.0, 0.3), S_pin])
def hand(L, w, z0, z1, hub_r, bore):
    blade = K.box([C[0]-w/2, C[1], z0], [C[0]+w/2, C[1]+L, z1])
    h = K.union([cyl(C, z0, z1, hub_r), blade])
    if bore: h = h - cyl(C, z0-1, z1+1, bore)
    return h
parts['seconds_hand'] = hand(9.0, 0.3, 10.5, 10.9, 0.8, 0)
# centre mobile (minute)
tube = cyl(C, 1.3, 10.4, 0.8)
collar = cyl(C, 4.1, 4.7, 1.5)
parts['centre_wheel'] = K.union([tube, collar, C_pin, C_wh]) - cyl(C, 0, 12, 0.36)
parts['cannon_pinion'] = CAN - cyl(C, 5, 8, 0.5)
parts['minute_hand'] = hand(8.0, 0.5, 9.7, 10.2, 1.5, 0.36)
# hour mobile
parts['hour_wheel'] = K.union([H_wh, cyl(C, 7.1, 9.6, 1.3)]) - cyl(C, 6, 11, 0.86)
parts['hour_hand'] = hand(5.8, 0.8, 9.1, 9.6, 1.8, 0.86)
# minute wheel mobile (motion work)
parts['mw_arbor'] = K.union([cyl(M, 4.4, 8.3, 0.4), cyl(M, 4.4, 4.7, 1.0)])
parts['mw_wheel'] = K.union([M_wh, M_pin])

# ---- fixed
wheels_plan = [(O, 9.8), (A, 7.35), (C, 8.33), (T, 8.28), (M, 1.0)]
pillars = []
for ang in np.arange(0, 360, 2.0):
    p = (CC[0]+(PLATE_R-1.6)*math.cos(math.radians(ang)), CC[1]+(PLATE_R-1.6)*math.sin(math.radians(ang)))
    cl = min(math.hypot(p[0]-q[0], p[1]-q[1]) - r for q, r in wheels_plan)
    if cl > 2.0 and all(math.hypot(p[0]-q[0], p[1]-q[1]) > 12 for q in pillars):
        pillars.append(p)
print('pillars', pillars)
assert len(pillars) >= 3
bp = cyl(CC, ZB0, ZB1, PLATE_R)
bp = K.union([bp] + [cyl(p, ZB0, ZT0, 1.2) for p in pillars])
for ax, r in [(O, 0.55), (A, 0.4), (T, 0.4), (C, 0.35)]:
    bp = bp - cyl(ax, ZB0-1, ZB1+1, r)
parts['main_plate'] = bp
tp = K.union([cyl(CC, ZT0, ZT1, PLATE_R), cyl(O, 1.1, ZT0+0.1, 2.0)])
tp = tp - cyl(O, 0.5, 2.2, 0.55)
for ax, r in [(A, 0.4), (T, 0.4), (C, 0.86), (M, 0.45)]:
    tp = tp - cyl(ax, ZT0-1, ZT1+1, r)
parts['top_plate'] = tp

os.makedirs('work/parts', exist_ok=True)
for n, p in parts.items():
    assert p.status() == m3.Error.NoError and len(p.decompose()) == 1, n
    K.write_stl('work/parts/%s.stl' % n, p)
doc = {
 "case_centre": list(CC),
 "fixed": ["main_plate", "top_plate"],
 "mobiles": {
  "intermediate": {"axis": list(A), "parts": ["inter_arbor", "inter_pinion", "inter_wheel"]},
  "centre": {"axis": list(C), "parts": ["centre_wheel", "cannon_pinion", "minute_hand"]},
  "third": {"axis": list(T), "parts": ["third_arbor", "third_wheel", "third_pinion"]},
  "seconds": {"axis": list(C), "parts": ["seconds_arbor", "seconds_hand"]},
  "minute_wheel": {"axis": list(M), "parts": ["mw_arbor", "mw_wheel"]},
  "hour": {"axis": list(C), "parts": ["hour_wheel", "hour_hand"]},
 },
 "meshes": [
  {"driver": "barrel", "driver_teeth": 96, "driven": "intermediate", "driven_teeth": 24},
  {"driver": "intermediate", "driver_teeth": 40, "driven": "centre", "driven_teeth": 20},
  {"driver": "centre", "driver_teeth": 96, "driven": "third", "driven_teeth": 12},
  {"driver": "third", "driver_teeth": 90, "driven": "seconds", "driven_teeth": 12},
  {"driver": "centre", "driver_teeth": 12, "driven": "minute_wheel", "driven_teeth": 36},
  {"driver": "minute_wheel", "driver_teeth": 12, "driven": "hour", "driven_teeth": 48},
 ],
 "hands": {"hour": {"mobile": "hour", "part": "hour_hand"},
           "minute": {"mobile": "centre", "part": "minute_hand"},
           "seconds": {"mobile": "seconds", "part": "seconds_hand"}},
}
json.dump(doc, open('work/movement.json', 'w'), indent=1)
print('built', len(parts))
