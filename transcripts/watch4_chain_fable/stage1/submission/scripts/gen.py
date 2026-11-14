"""Generates every part (STEP) and movement.json into work/.  Run from the task folder."""
import sys, os, math, json
sys.path.insert(0, 'tools')
import kernel
import cadquery as cq

PA = math.radians(25.0)
BL = 0.02            # tooth thinning on the pitch circle (backlash) for my gears
O = (0.0, 0.0)
H = (10.85, 0.0)     # hands axis = case centre


def on_circle(c, r, deg):
    return (c[0] + r * math.cos(math.radians(deg)), c[1] + r * math.sin(math.radians(deg)))


# intermediate: 12.0 from barrel (96+24, m0.2), 9.375 from H (50+25, m0.25)
_x = (144.0 - 9.375 ** 2 + H[0] ** 2) / (2 * H[0])
I = (_x, math.sqrt(144.0 - _x * _x))
T = on_circle(H, 9.18, 20.0)    # third: 96+12 at m0.17 = 90+12 at m0.18 = 9.18
M = on_circle(H, 9.6, -70.0)    # motion: 12+36 at m0.4 = 12+48 at m0.32 = 9.6

# z levels
L0, L1, L2, L3, L4, L5 = (0.0, 1.0), (1.2, 2.2), (2.4, 3.4), (3.6, 4.6), (4.8, 5.8), (6.0, 7.0)
BP = (-1.1, -0.1)
TP = (8.8, 9.6)
JR, HR = 0.5, 0.56   # journal and hole radius


def gear_pts(c, z, m, phase, n=8):
    r = z * m / 2; rb = r * math.cos(PA); ra = r + m; rf = r - 1.25 * m
    half = (math.pi * m / 2 - BL) / (2 * r)
    inv0 = math.tan(PA) - PA
    def th(rr):
        a = math.acos(min(1.0, rb / rr))
        return half + inv0 - (math.tan(a) - a)
    r0 = max(rb, rf)
    rs = [r0 + (ra - r0) * (i / (n - 1)) ** 1.0 for i in range(n)]
    pts = []
    for k in range(z):
        cc = phase + 2 * math.pi * k / z
        fl = [(rr, th(rr)) for rr in rs]
        if rf < rb - 1e-9:
            fl = [(rf, th(rb))] + fl
        for rr, t in fl:
            pts.append((c[0] + rr * math.cos(cc - t), c[1] + rr * math.sin(cc - t)))
        for rr, t in reversed(fl):
            pts.append((c[0] + rr * math.cos(cc + t), c[1] + rr * math.sin(cc + t)))
    return pts


def cyl(c, r, z0, z1):
    return cq.Workplane('XY').workplane(offset=z0).center(c[0], c[1]).circle(r).extrude(z1 - z0)


def gear(c, z, m, phase, lev, bore):
    g = cq.Workplane('XY').workplane(offset=lev[0]).polyline(gear_pts(c, z, m, phase)).close().extrude(lev[1] - lev[0])
    return g.cut(cyl(c, bore, lev[0] - 1, lev[1] + 1))


def mate_phase(c1, z1, ph1, c2, z2):
    """phase (angle of a tooth centre) of gear 2 so that it meshes with gear 1"""
    al = math.atan2(c2[1] - c1[1], c2[0] - c1[0])
    return al + math.pi - (ph1 - al) * z1 / z2 + math.pi / z2


def hand(c, bore, hub, reach, w, z0, z1):
    ring = cyl(c, hub, z0, z1)
    y0 = bore + 0.2
    bar = cq.Workplane('XY').workplane(offset=z0).center(c[0], c[1] + (y0 + reach) / 2).rect(w, reach - y0).extrude(z1 - z0)
    return ring.union(bar).cut(cyl(c, bore, z0 - 1, z1 + 1))


parts = {}
# ---- fixed
bp = cyl(H, 20.5, *BP)
for a in (0, 120, 240):
    bp = bp.union(cyl(on_circle(H, 19.2, a), 1.0, BP[0], TP[0]))
for c in (O, I, T, M, H):
    bp = bp.cut(cyl(c, HR, BP[0] - 1, BP[1] + 1))
parts['bottom_plate'] = bp
tp = cyl(H, 20.5, *TP).union(cyl(O, 1.2, 1.1, TP[0] + 0.1))
for c in (I, T, M):
    tp = tp.cut(cyl(c, HR, TP[0] - 1, TP[1] + 1))
tp = tp.cut(cyl(H, 1.56, TP[0] - 1, TP[1] + 1)).cut(cyl(O, HR, 0.5, 1.8))
parts['top_plate'] = tp

# ---- intermediate mobile (barrel -> minute).  Stage 3 only needs new wheel + drive pinion.
parts['intermediate_arbor'] = cyl(I, JR, -1.0, 9.5).union(cyl(I, 0.9, 8.2, 8.7))
parts['intermediate_pinion_24t_m020'] = gear(I, 24, 0.2, mate_phase(O, 96, 0.0, I, 24), L0, JR)
parts['intermediate_wheel_50t_m025'] = gear(I, 50, 0.25, 0.0, L2, JR)
# ---- minute mobile (tube on the seconds arbor)
parts['minute_tube'] = cyl(H, 1.0, 2.3, 10.8).cut(cyl(H, HR, 0, 12))
parts['minute_drive_pinion_25t_m025'] = gear(H, 25, 0.25, mate_phase(I, 50, 0.0, H, 25), L2, 1.0)
parts['centre_wheel_96t_m017'] = gear(H, 96, 0.17, 0.0, L3, 1.0)
parts['cannon_pinion_12t_m040'] = gear(H, 12, 0.4, 0.0, L4, 1.0)
parts['minute_hand'] = hand(H, 1.0, 1.8, 9.5, 0.6, 10.4, 10.8)
# ---- third mobile
parts['third_arbor'] = cyl(T, JR, -1.0, 9.5).union(cyl(T, 0.9, 8.2, 8.7)).union(cyl(T, 0.9, 0.0, 0.6))
parts['third_pinion_12t_m017'] = gear(T, 12, 0.17, mate_phase(H, 96, 0.0, T, 12), L3, JR)
parts['third_wheel_90t_m018'] = gear(T, 90, 0.18, 0.0, L1, JR)
# ---- seconds mobile
parts['seconds_arbor'] = cyl(H, JR, -1.0, 11.4).union(cyl(H, 0.8, 0.0, 1.2))
parts['seconds_pinion_12t_m018'] = gear(H, 12, 0.18, mate_phase(T, 90, 0.0, H, 12), L1, JR)
parts['seconds_hand'] = hand(H, JR, 1.2, 10.0, 0.4, 11.0, 11.4)
# ---- motion mobile (minute wheel)
parts['motion_arbor'] = cyl(M, JR, -1.0, 9.5).union(cyl(M, 0.9, 8.2, 8.7)).union(cyl(M, 0.9, 0.0, 0.6))
parts['motion_wheel_36t_m040'] = gear(M, 36, 0.4, mate_phase(H, 12, 0.0, M, 36), L4, JR)
parts['motion_pinion_12t_m032'] = gear(M, 12, 0.32, 0.0, L5, JR)
# ---- hour mobile (tube on the minute tube)
parts['hour_tube'] = cyl(H, 1.5, 5.9, 10.2).union(cyl(H, 2.2, 8.2, 8.7)).cut(cyl(H, 1.06, 5, 11))
parts['hour_wheel_48t_m032'] = gear(H, 48, 0.32, mate_phase(M, 12, 0.0, H, 48), L5, 1.5)
parts['hour_hand'] = hand(H, 1.5, 2.3, 7.0, 0.6, 9.8, 10.2)

os.makedirs('work/parts', exist_ok=True)
for n, s in parts.items():
    kernel.write_step('work/parts/%s.step' % n, s)

mob = lambda ax, pre: {"axis": [ax[0], ax[1]], "parts": [n for n in parts if n.startswith(pre)]}
doc = {
    "case_centre": [H[0], H[1]],
    "fixed": ["bottom_plate", "top_plate"],
    "mobiles": {
        "intermediate": mob(I, "intermediate_"),
        "minute": {"axis": list(H), "parts": ["minute_tube", "minute_drive_pinion_25t_m025", "centre_wheel_96t_m017",
                                              "cannon_pinion_12t_m040", "minute_hand"]},
        "third": mob(T, "third_"),
        "seconds": mob(H, "seconds_"),
        "motion": mob(M, "motion_"),
        "hour": mob(H, "hour_"),
    },
    "meshes": [
        {"driver": "barrel", "driver_teeth": 96, "driven": "intermediate", "driven_teeth": 24},
        {"driver": "intermediate", "driver_teeth": 50, "driven": "minute", "driven_teeth": 25},
        {"driver": "minute", "driver_teeth": 96, "driven": "third", "driven_teeth": 12},
        {"driver": "third", "driver_teeth": 90, "driven": "seconds", "driven_teeth": 12},
        {"driver": "minute", "driver_teeth": 12, "driven": "motion", "driven_teeth": 36},
        {"driver": "motion", "driver_teeth": 12, "driven": "hour", "driven_teeth": 48},
    ],
    "hands": {
        "hour": {"mobile": "hour", "part": "hour_hand"},
        "minute": {"mobile": "minute", "part": "minute_hand"},
        "seconds": {"mobile": "seconds", "part": "seconds_hand"},
    },
}
json.dump(doc, open('work/movement.json', 'w'), indent=1)
print(len(parts), 'parts')
