"""Thin dress watch calibre, demonstration scale: geometry of every part of both builds.

World frame: barrel axis at (0, 0) (as supplied), dial side +z.  Case centre C = (2.85, 0).
Run:  python3 design.py  -> writes /app/delivery/parts/*.step, movement.json, variant_6h.json
"""
import json
import math
import os
import sys

import numpy as np
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/app/tools")
from gears import gear_section, section_loops   # noqa: E402

OUT = os.environ.get("WATCH_OUT", "/app/delivery")
BARREL = "BR-096-30"
CX, CY = 2.85, 0.0                       # case centre
A0 = (0.0, 0.0)                          # barrel axis
THIN = 0.04                              # tooth thinning on the pitch circle (backlash)
STEEL = "AD-C100-HT"

# ---------------- z levels ----------------
ZBP0, ZBP1 = -0.4545, -0.0345            # bottom plate
ZMP0, ZMP1 = 0.4845, 0.7345              # mid plate
ZIP0, ZIP1 = 1.4745, 1.7245              # motion bridge (IP)
ZTB0, ZTB1 = 2.257, 2.5455               # top bridge
ZH0, ZH1 = 2.5755, 2.7755                # hour wheel / minute-wheel pinion above the top bridge
B0, B1 = 0.7645, 2.227                   # mobile shoulders under/over the plates
HT = 0.20                                # hand thickness
ZL1 = ZH1 + 0.30                         # hand level 1 (seconds, 24 h)   (0.30 left for the dial)
ZL2 = ZL1 + HT + 0.05                    # hour hand
ZL3 = ZL2 + HT + 0.05                    # minute hand
PIV = 0.25                               # pivot radius
HOLE = 0.28                              # pivot hole radius
PLATE_R = 12.5

# ---------------- positions (relative to the case centre) ----------------
REL = {
    "M2": (8.1616, 2.9505), "X": (3.5613, 0.5261), "Y": (7.5145, -1.6239),
    "M3": (5.3264, 6.5730), "M4": (1.2672, 8.6506), "S": (-2.5309, 6.4291),
    "MW": (-1.1058, -3.8441), "I": (2.0800, -1.8745), "D": (4.6558, -5.1919),
    "MIN": (0.0, 0.0), "HOUR": (0.0, 0.0),
}
PIL = [(9.0761, -6.5381), (-4.4202, 7.2434), (-1.8274, -8.0570)]   # mid plate -> top bridge
IPP = (-0.1822, 2.9195)                                               # mid plate -> motion bridge


def W(rel):
    return (rel[0] + CX, rel[1] + CY)


def P(name):
    return W(REL[name])


# exact centre distances from the gear data (positions are refined below so that they are exact)
def cd(m, z1, z2):
    return m * (z1 + z2) / 2.0


def _exact_positions():
    """Move each mobile onto the exact centre distance of its meshes (the planner's numbers are close)."""
    def toward(a, b, d):
        ax, ay = a
        bx, by = b
        L = math.hypot(bx - ax, by - ay)
        return (ax + (bx - ax) * d / L, ay + (by - ay) * d / L)

    def two_circle(c1, r1, c2, r2, near):
        d = math.dist(c1, c2)
        a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
        h = math.sqrt(max(0.0, r1 * r1 - a * a))
        ex = ((c2[0] - c1[0]) / d, (c2[1] - c1[1]) / d)
        s1 = (c1[0] + a * ex[0] - h * ex[1], c1[1] + a * ex[1] + h * ex[0])
        s2 = (c1[0] + a * ex[0] + h * ex[1], c1[1] + a * ex[1] - h * ex[0])
        return s1 if math.dist(s1, near) < math.dist(s2, near) else s2
    pos = {k: W(v) for k, v in REL.items()}
    pos["M2"] = toward(A0, pos["M2"], cd(0.2, 96, 18))
    pos["X"] = toward(pos["MIN"], pos["X"], cd(0.3, 12, 12))
    pos["Y"] = two_circle(pos["M2"], cd(0.33, 14, 14), pos["X"], cd(0.3, 18, 12), pos["Y"])
    pos["M3"] = toward(pos["M2"], pos["M3"], cd(0.23, 32, 8))
    pos["M4"] = toward(pos["M3"], pos["M4"], cd(0.19, 40, 8))
    pos["S"] = toward(pos["M4"], pos["S"], cd(0.2, 36, 8))
    pos["MW"] = toward(pos["MIN"], pos["MW"], cd(0.2, 10, 30))
    pos["I"] = toward(pos["MIN"], pos["I"], cd(0.2, 14, 14))
    pos["D"] = toward(pos["I"], pos["D"], cd(0.2, 14, 28))
    return pos


POS = _exact_positions()


# ---------------- gear tables ----------------
# mesh: (driver mobile, driver gear key, driven mobile, driven gear key)
def gear_table(build):
    v6 = build == "6h"
    G = {
        # key: (mobile, m, z, z0, z1)
        "p2": ("M2", 0.2, 18, -0.0045, 0.5045),
        "G2": ("M2", 0.33, 12 if v6 else 14, 1.3945, 1.7945),
        "W2": ("M2", 0.23, 30 if v6 else 32, 1.827, B1),
        "p3": ("M3", 0.23, 10 if v6 else 8, 1.777, B1),
        "W3": ("M3", 0.19, 40, 1.0945, 1.3445),
        "p4": ("M4", 0.19, 8, 1.0445, 1.3945),
        "W4": ("M4", 0.2, 36, B0, 1.0145),
        "pS": ("S", 0.2, 8, B0, 1.0645),
        "Yd": ("Y", 0.33, 16 if v6 else 14, 1.3945, 1.7945),
        "Ydr": ("Y", 0.3, 18, B0, 1.1645),
        "zX": ("X", 0.3, 12, B0, 1.1645),
        "GM": ("MIN", 0.3, 12, B0, 1.1645),
        "c": ("MIN", 0.2, 10, 1.1645, 1.4445),
        "Wmw": ("MW", 0.2, 30, 1.1945, 1.4445),
        "pmw": ("MW", 0.2, 8, 2.50, ZH1),
        "H": ("HOUR", 0.2, 32, ZH0, ZH1),
        "col": ("HOUR", 0.2, 14, 1.927, B1),
        "I": ("I", 0.2, 14, 1.927, B1),
        "WD": ("D", 0.2, 28, 1.927, B1),
    }
    M = [("barrel", "p2"), ("W2", "p3"), ("W3", "p4"), ("W4", "pS"), ("G2", "Yd"), ("Ydr", "zX"),
         ("zX", "GM"), ("c", "Wmw"), ("pmw", "H"), ("col", "I"), ("I", "WD")]
    return G, M


def phases(build):
    """Angle (rad, world) of one tooth centre of every gear, so that every mesh is centred in its backlash."""
    G, M = gear_table(build)
    ph = {"barrel": 0.0}
    zb = {"barrel": 96}
    # free choices (gears that start a branch); variant keeps the phases of the parts it shares
    free = {"G2": 0.0, "W2": 0.0, "W3": 0.0, "W4": 0.0, "Ydr": 0.0, "c": 0.0, "pmw": 0.0, "col": 0.0}
    if build == "6h":
        # parts shared with the 8 h build must keep their phases: Ydr (on Y) meshes the shared X,
        # W3 (on M3) meshes the shared M4.  Their values are the 8 h ones (0.0 above).
        pass
    ph.update(free)
    pos_of = lambda k: A0 if k == "barrel" else POS[G[k][0]]
    z_of = lambda k: 96 if k == "barrel" else G[k][2]
    changed = True
    while changed:
        changed = False
        for a, b in M:
            if a in ph and b not in ph:
                drv, dvn = a, b
            elif b in ph and a not in ph:
                drv, dvn = b, a
            else:
                continue
            pa, pb = pos_of(drv), pos_of(dvn)
            beta = math.atan2(pb[1] - pa[1], pb[0] - pa[0])
            za, zbn = z_of(drv), z_of(dvn)
            fa = za * (ph[drv] - beta) / (2 * math.pi)
            ph[dvn] = beta + math.pi + (2 * math.pi / zbn) * (0.5 - fa)
            changed = True
    if build == "6h":
        # Yd' and p3' are new parts: their phases were set from G2'/W2' (free on the new M2').
        pass
    return ph


# ---------------- CAD helpers ----------------
def cyl(c, r, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(c[0], c[1]).circle(r).extrude(z1 - z0)


def tube(c, ri, ro, z0, z1):
    return cq.Workplane("XY").workplane(offset=z0).center(c[0], c[1]).circle(ro).circle(ri).extrude(z1 - z0)


_gcache = {}


def gear_prism(c, m, z, phase, z0, z1):
    key = (m, z, round(phase, 12))
    if key not in _gcache:
        _gcache[key] = section_loops(gear_section(m, z, THIN, phase=phase))[0]
    pts = _gcache[key]
    pts = [(float(x + c[0]), float(y + c[1])) for x, y in pts]
    return cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)


def union(objs):
    s = objs[0]
    for o in objs[1:]:
        s = s.union(o)
    return s


def one_solid(wp):
    sol = wp.solids().vals()
    if len(sol) != 1:
        raise RuntimeError("not one solid: %d" % len(sol))
    return wp


# ---------------- mobiles ----------------
def gear(G, ph, key):
    mob, m, z, z0, z1 = G[key]
    return gear_prism(POS[mob], m, z, ph[key], z0, z1)


def plain_mobile(name, G, ph, gears, extra=(), arbor_r=0.33, top="pivot"):
    """A mobile between the mid plate and the top bridge: lower pivot in the mid plate, shoulder on it,
    gears, upper shoulder under the top bridge and upper pivot in it."""
    c = POS[name]
    objs = [cyl(c, PIV, ZMP0 + 0.05, B0 + 0.001), cyl(c, arbor_r, B0, B1)]
    if top == "pivot":
        objs.append(cyl(c, PIV, B1 - 0.001, ZTB1 - 0.0455))
    objs += [gear(G, ph, k) for k in gears]
    objs += list(extra)
    return one_solid(union(objs))


def hand_seat_shaft(c, r_sh, z_from):
    """shaft from under the top bridge up to the level-1 hand: shoulder r 0.5 under the bridge, r 0.4 through it,
    seat r 0.3 for the hand."""
    return [cyl(c, 0.5, B1 - 0.2, B1), cyl(c, 0.4, B1 - 0.001, ZL1 + 0.001), cyl(c, 0.3, ZL1, ZL1 + HT)]


def build_mobiles(build):
    G, M = gear_table(build)
    ph = phases(build)
    parts = {}
    sfx = "_6h" if build == "6h" else ""
    # M2 in two parts: m2a (barrel pinion, arbor, spigot; pivots in the bottom plate and the top bridge), put in
    # before the mobiles that overlap it, and m2b (its two wheels) pressed on the spigot afterwards.
    c = POS["M2"]
    m2a = union([cyl(c, PIV, -0.38, -0.004), gear(G, ph, "p2"), cyl(c, 0.55, 0.5, 1.3945),
                 cyl(c, 0.4, 1.394, B1 + 0.001), cyl(c, PIV, B1, ZTB1 - 0.0455)])
    m2b = union([gear(G, ph, "G2"), cyl(c, 0.55, 1.79, 1.832), gear(G, ph, "W2")]).cut(cyl(c, 0.4, 1.3, 2.4))
    parts["m2a"] = one_solid(m2a)
    parts["m2b" + sfx] = one_solid(m2b)
    parts["m3" + sfx] = plain_mobile("M3", G, ph, ["W3", "p3"])
    parts["y" + sfx] = plain_mobile("Y", G, ph, ["Ydr", "Yd"], extra=[cyl(POS["Y"], 0.6, 1.16, 1.40)])
    # parts shared by both builds (identical geometry and phases)
    parts["m4"] = plain_mobile("M4", G, ph, ["W4", "p4"])
    parts["x"] = plain_mobile("X", G, ph, ["zX"])
    c = POS["S"]
    parts["s"] = one_solid(union([cyl(c, PIV, ZMP0 + 0.05, B0 + 0.001), cyl(c, 0.33, B0, B1), gear(G, ph, "pS")]
                                 + hand_seat_shaft(c, 0.4, B1)))
    c = POS["D"]
    parts["d"] = one_solid(union([cyl(c, PIV, ZMP0 + 0.05, B0 + 0.001), cyl(c, 0.33, B0, B1), gear(G, ph, "WD")]
                                 + hand_seat_shaft(c, 0.4, B1)))
    parts["i"] = plain_mobile("I", G, ph, ["I"])
    c = POS["MW"]
    parts["mw"] = one_solid(union([cyl(c, PIV, ZMP0 + 0.05, B0 + 0.001), cyl(c, 0.33, B0, 1.95), gear(G, ph, "Wmw"),
                                   cyl(c, 1.3, 1.9, B1), cyl(c, 0.97, B1 - 0.001, 2.52), gear(G, ph, "pmw")]))
    # MIN: rides on the fixed central post (r 0.30), bore 0.33
    c = POS["MIN"]
    mn = union([gear(G, ph, "GM"), gear(G, ph, "c"), cyl(c, 0.62, 1.44, ZL3 + 0.001), cyl(c, 0.55, ZL3, ZL3 + HT)])
    mn = mn.cut(cyl(c, 0.33, B0 - 0.1, ZL3 + HT + 0.1))
    parts["min"] = one_solid(mn)
    # HOUR: main part (pipe + hour wheel above the top bridge) and the collar gear under the bridge
    hr = union([cyl(c, 0.85, 1.927, B1 + 0.001), cyl(c, 1.0, B1, ZL2 + 0.001), gear(G, ph, "H"),
                cyl(c, 0.88, ZL2, ZL2 + HT)])
    hr = hr.cut(cyl(c, 0.65, 1.8, ZL2 + HT + 0.1))
    parts["hour"] = one_solid(hr)
    col = gear(G, ph, "col").cut(cyl(c, 0.85, 1.8, 2.4))
    parts["hour_collar"] = one_solid(col)
    return parts, ph


# ---------------- hands ----------------
def hand(c, r_hole, r_hub, length, tip_w, root_w, z0, tail=0.0, angle=math.pi / 2):
    """Pointer pointing along `angle`: a hub ring and a tapered blade."""
    ca, sa = math.cos(angle), math.sin(angle)
    # blade polygon in local coords (x along the hand)
    pts = [(-tail, -root_w / 2), (length - tip_w / 2, -tip_w / 2), (length, 0.0), (length - tip_w / 2, tip_w / 2),
           (-tail, root_w / 2)]
    pts = [(c[0] + x * ca - y * sa, c[1] + x * sa + y * ca) for x, y in pts]
    blade = cq.Workplane("XY").workplane(offset=z0).polyline(pts).close().extrude(HT)
    hub = cyl(c, r_hub, z0, z0 + HT)
    h = blade.union(hub).cut(cyl(c, r_hole, z0 - 0.1, z0 + HT + 0.1))
    return one_solid(h)


def build_hands():
    C = (CX, CY)
    return {
        "hand_seconds": hand(POS["S"], 0.3, 0.6, 5.25, 0.25, 0.45, ZL1),
        "hand_24h": hand(POS["D"], 0.3, 0.6, 3.4, 0.3, 0.5, ZL1),
        "hand_hour": hand(C, 0.88, 1.2, 5.6, 0.35, 0.8, ZL2),
        "hand_minute": hand(C, 0.55, 0.85, 8.5, 0.3, 0.6, ZL3),
    }


# ---------------- frame ----------------
def crescent_pillars():
    """bottom plate -> mid plate pillars, outside the barrel drum (r 9.8)"""
    out = []
    for ang, rr, r in ((55.0, 11.4, 0.75), (-55.0, 11.4, 0.75), (100.0, 10.75, 0.6), (-100.0, 10.75, 0.6)):
        a = math.radians(ang)
        out.append(((A0[0] + rr * math.cos(a), A0[1] + rr * math.sin(a)), r))
    return out


def build_frame():
    C = (CX, CY)
    parts = {}
    bp = cyl(C, PLATE_R, ZBP0, ZBP1)
    for (p, r) in crescent_pillars():
        bp = bp.union(cyl(p, r, ZBP1 - 0.001, ZMP0))
    bp = bp.cut(cyl(A0, 0.53, ZBP0 - 0.1, ZBP1 + 0.1)).cut(cyl(POS["M2"], HOLE, ZBP0 - 0.1, ZBP1 + 0.1))
    parts["bottom_plate"] = one_solid(bp)

    mp = cyl(C, PLATE_R, ZMP0, ZMP1)
    mp = mp.union(cyl(C, 0.30, ZMP1 - 0.001, ZH1 - 0.03))                # central post (ends under the dial)
    for p in PIL:
        mp = mp.union(cyl(W(p), 0.6, ZMP1 - 0.001, ZTB0))
    mp = mp.union(cyl(W(IPP), 0.5, ZMP1 - 0.001, ZIP0))
    mp = mp.cut(cyl(A0, 1.04, ZMP0 - 0.1, ZMP1 + 0.1)).cut(cyl(POS["M2"], 2.1, ZMP0 - 0.1, ZMP1 + 0.1))
    for k in ("M3", "M4", "S", "Y", "X", "MW", "I", "D"):
        mp = mp.cut(cyl(POS[k], HOLE, ZMP0 - 0.1, ZMP1 + 0.1))
    parts["mid_plate"] = one_solid(mp)

    # motion bridge: ring round the minute pipe, arm to its pillar
    ip = cyl(C, 1.6, ZIP0, ZIP1).union(cyl(W(IPP), 0.5, ZIP0, ZIP1))
    dx, dy = W(IPP)[0] - C[0], W(IPP)[1] - C[1]
    L = math.hypot(dx, dy)
    ang = math.degrees(math.atan2(dy, dx))
    arm = (cq.Workplane("XY").workplane(offset=ZIP0).center(C[0], C[1])
           .transformed(rotate=(0, 0, ang)).center(L / 2, 0).rect(L, 0.8).extrude(ZIP1 - ZIP0))
    ip = ip.union(arm).cut(cyl(C, 0.65, ZIP0 - 0.1, ZIP1 + 0.1))
    parts["motion_bridge"] = one_solid(ip)

    tb = cyl(C, PLATE_R, ZTB0, ZTB1)
    tb = tb.cut(cyl(A0, 0.53, ZTB0 - 0.1, ZTB1 + 0.1))
    for k, r in (("M2", HOLE), ("M3", HOLE), ("M4", HOLE), ("Y", HOLE), ("X", HOLE), ("I", HOLE),
                 ("S", 0.43), ("D", 0.43), ("MW", 1.03), ("MIN", 1.03)):
        tb = tb.cut(cyl(POS[k], r, ZTB0 - 0.1, ZTB1 + 0.1))
    parts["top_bridge"] = one_solid(tb)
    return parts


# ---------------- JSON ----------------
FIXED = ["bottom_plate", "mid_plate", "motion_bridge", "top_bridge"]


def movement_json(build):
    G, M = gear_table(build)
    s = "_6h" if build == "6h" else ""
    mobiles = {
        "m2": ["m2a", "m2b" + s], "m3": ["m3" + s], "m4": ["m4"], "seconds": ["s", "hand_seconds"],
        "y": ["y" + s], "x": ["x"], "minute": ["min", "hand_minute"], "minute_wheel": ["mw"],
        "hour": ["hour", "hour_collar", "hand_hour"], "idler": ["i"], "day": ["d", "hand_24h"],
    }
    mob_of = {"M2": "m2", "M3": "m3", "M4": "m4", "S": "seconds", "Y": "y", "X": "x", "MIN": "minute",
              "MW": "minute_wheel", "HOUR": "hour", "I": "idler", "D": "day"}
    axis = {mob_of[k]: [float(POS[k][0]), float(POS[k][1])] for k in mob_of}
    doc = {
        "barrel": BARREL,
        "case_centre": [CX, CY],
        "fixed": FIXED,
        "mobiles": {k: {"axis": axis[k], "parts": v, "material": STEEL} for k, v in mobiles.items()},
        "meshes": [],
        "hands": {
            "hour": {"mobile": "hour", "part": "hand_hour"},
            "minute": {"mobile": "minute", "part": "hand_minute"},
            "seconds": {"mobile": "seconds", "part": "hand_seconds"},
            "day": {"mobile": "day", "part": "hand_24h"},
        },
    }
    for a, b in M:
        ma = "barrel" if a == "barrel" else mob_of[G[a][0]]
        za = 96 if a == "barrel" else G[a][2]
        doc["meshes"].append({"driver": ma, "driver_teeth": za, "driven": mob_of[G[b][0]], "driven_teeth": G[b][2]})
    return doc


def write_all(only=None):
    sys.path.insert(0, "/app/tools")
    import kernel
    os.makedirs(os.path.join(OUT, "parts"), exist_ok=True)
    parts = {}
    parts.update(build_frame())
    p8, ph8 = build_mobiles("8h")
    parts.update(p8)
    p6, ph6 = build_mobiles("6h")
    parts.update(p6)
    parts.update(build_hands())
    for name, wp in parts.items():
        if only and name not in only:
            continue
        kernel.write_step(os.path.join(OUT, "parts", name + ".step"), wp)
        print("wrote", name, flush=True)
    for build, fn in (("8h", "movement.json"), ("6h", "variant_6h.json")):
        with open(os.path.join(OUT, fn), "w") as f:
            json.dump(movement_json(build), f, indent=1)
    return parts


if __name__ == "__main__":
    write_all(sys.argv[1:] or None)
