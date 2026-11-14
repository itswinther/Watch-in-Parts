"""Reference search for a watch gear train instance. Time-boxed; the result is checked by watch.grade.

    python3 refsolve.py instance.json design_out.json ref_out.json [seconds]

Order: fourth-escape stage (fixed distance) -> centre-third-fourth (third arbor at a circle
intersection) -> barrel placed around the centre, biggest reserve first -> levels from a
precomputed overlap table -> motion work around the centre on two dial levels.
"""
import itertools
import json
import math
import sys
import time
from fractions import Fraction as F

import watch as W

inst = json.load(open(sys.argv[1]))
BUDGET = float(sys.argv[4]) if len(sys.argv) > 4 else 120
t0 = time.time()
R = inst["plate_radius"]
C = (0.0, 0.0)
S = tuple(inst["fixed_arbors"]["fourth"])
E = tuple(inst["fixed_arbors"]["escape"])
BAL = tuple(inst["balance"]["centre"])
RB = inst["balance"]["radius"]
RE = inst["escape_wheel"]["radius"]
k = inst["beats_per_hour"] // 1800
target = inst["power_reserve_target_h"]
d_ = W.dist
tip = W.tip


def ok_disk(c, rt, avoid, train=True):
    """plate, balance, and every arbor in `avoid`."""
    if math.hypot(*c) + rt > R - W.EDGE:
        return False
    if train and d_(c, BAL) < rt + RB + W.GAP:
        return False
    return all(d_(c, p) >= rt + W.ARBOR_R for p in avoid)


def circ_int(p, r1, q, r2):
    d = d_(p, q)
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return []
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    mx, my = p[0] + a * (q[0] - p[0]) / d, p[1] + a * (q[1] - p[1]) / d
    return [(mx + h * (q[1] - p[1]) / d, my - h * (q[0] - p[0]) / d),
            (mx - h * (q[1] - p[1]) / d, my + h * (q[0] - p[0]) / d)]


PIN = range(W.PINION[0], W.PINION[1] + 1)
WHL = range(W.WHEEL[0], W.WHEEL[1] + 1)

dSE = d_(S, E)
se = [(m, ze * k, ze) for m in W.MODULES for ze in PIN
      if ze * k in WHL and abs(W.pitch_dist(m, ze * k, ze) - dSE) <= W.MESH_TOL
      and ok_disk(S, tip(m, ze * k), [C]) and ok_disk(E, tip(m, ze), [C])]

trains = []
for zTp in PIN:
    for zSp in PIN:
        P = 60 * zTp * zSp
        for zCw in WHL:
            if P % zCw or P // zCw not in WHL:
                continue
            zTw = P // zCw
            for m1 in W.MODULES:
                rCw, rTp = tip(m1, zCw), tip(m1, zTp)
                if not ok_disk(C, rCw, [S, E]):
                    continue
                d1 = W.pitch_dist(m1, zCw, zTp)
                for m2 in W.MODULES:
                    rTw, rSp = tip(m2, zTw), tip(m2, zSp)
                    if not ok_disk(S, rSp, [C, E]):
                        continue
                    for T in circ_int(C, d1, S, W.pitch_dist(m2, zTw, zSp)):
                        if math.hypot(*T) > R - W.ARBOR_EDGE or d_(T, E) < 2 * W.ARBOR_R:
                            continue
                        if not (ok_disk(T, rTp, [S, E]) and ok_disk(T, rTw, [C, E])):
                            continue
                        if d_(C, T) < 0 or not ok_disk(C, rCw, [S, E]):
                            continue
                        trains.append((m1, zCw, zTp, m2, zTw, zSp, T))
combos = []
for tr in trains:
    T = tr[6]
    for s4 in se:
        # fourth wheel must clear the third arbor; escape pinion must clear centre/third
        if not ok_disk(S, tip(s4[0], s4[1]), [C, T]) or not ok_disk(E, tip(s4[0], s4[2]), [C, T]):
            continue
        if not ok_disk(C, tip(tr[0], tr[1]), [S, E]):
            continue
        combos.append((tr, s4))
print("fourth-escape options %d, centre-third-fourth options %d, combined %d (%.1fs)" % (len(se), len(trains), len(combos), time.time() - t0))

barrels = sorted(((F(13, 2) * F(zB, zCp), m0, zB, zCp) for m0 in W.MODULES for zCp in PIN
                  for zB in range(W.BARREL[0], W.BARREL[1] + 1) if F(13, 2) * F(zB, zCp) >= target), reverse=True)
ANG = [a * 5.0 for a in range(72)]
placed = []   # (reserve, m0, zB, zCp, Bpos, rB) barrel fits plate, balance, fixed arbors
for res, m0, zB, zCp in barrels:
    d0 = W.pitch_dist(m0, zB, zCp)
    rB = tip(m0, zB)
    for a in ANG:
        Bp = (d0 * math.cos(math.radians(a)), d0 * math.sin(math.radians(a)))
        if math.hypot(*Bp) <= R - W.ARBOR_EDGE and ok_disk(Bp, rB, [S, E]) and ok_disk(C, tip(m0, zCp), [S, E]):
            placed.append((res, m0, zB, zCp, Bp, rB))
print("barrel placements %d (%.1fs)" % (len(placed), time.time() - t0))

LEVELS = sorted(itertools.product(range(5), repeat=5), key=lambda t: len({t[0], t[0] + 1, t[1], t[2], t[3], t[4]}))
LEVELS = [t for t in LEVELS if t[0] + 1 < W.LEVELS and t[0] != t[1] and t[1] != t[2] and t[2] != t[3] and t[3] != t[4]]


def best_levels(disks):
    """disks: name -> (centre, rt, arbor, var); var picks which level variable the disk uses.
    vars: 0 barrel(two levels), 1 centre wheel/third pinion, 2 third wheel/fourth pinion,
    3 fourth wheel/escape pinion, 4 escape wheel.  centre pinion uses var 0."""
    meshes = {frozenset(p) for p in W.MESHES}
    names = list(disks)
    clash = []
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            if frozenset((a, b)) in meshes or disks[a][2] == disks[b][2]:
                continue
            if d_(disks[a][0], disks[b][0]) < disks[a][1] + disks[b][1] + W.GAP:
                clash.append((disks[a][3], disks[b][3], a == "barrel_wheel" or b == "barrel_wheel", a, b))
    for lv in LEVELS:
        bad = False
        for va, vb, isbar, a, b in clash:
            la = {lv[va], lv[va] + 1} if a == "barrel_wheel" else {lv[va]}
            lb = {lv[vb], lv[vb] + 1} if b == "barrel_wheel" else {lv[vb]}
            if la & lb:
                bad = True
                break
        if not bad:
            return lv
    return None


motion = []
for zcp in PIN:
    for zmw in range(W.WHEEL[0], 81):
        for zmp in PIN:
            num = 12 * zcp * zmp
            if num % zmw or num // zmw not in WHL:
                continue
            zhw = num // zmw
            for m4 in W.MODULES:
                for m5 in W.MODULES:
                    if abs(W.pitch_dist(m4, zcp, zmw) - W.pitch_dist(m5, zmp, zhw)) <= W.MESH_TOL:
                        motion.append((max(tip(m4, zmw), tip(m5, zhw)), m4, zcp, zmw, m5, zmp, zhw))
motion.sort()


def place_motion(arbs):
    for _, m4, zcp, zmw, m5, zmp, zhw in motion:
        dm = W.pitch_dist(m4, zcp, zmw)
        for a in ANG:
            M = (dm * math.cos(math.radians(a)), dm * math.sin(math.radians(a)))
            if math.hypot(*M) > R - W.ARBOR_EDGE or any(d_(M, p) < 2 * W.ARBOR_R for p in arbs):
                continue
            others = [p for p in arbs if p != C]
            if (ok_disk(C, tip(m4, zcp), others, False) and ok_disk(C, tip(m5, zhw), others, False)
                    and ok_disk(M, tip(m4, zmw), [p for p in arbs], False) and ok_disk(M, tip(m5, zmp), [p for p in arbs], False)
                    and d_(C, M) >= tip(m4, zmw) + W.ARBOR_R and d_(C, M) >= tip(m5, zmp) + W.ARBOR_R):
                return (m4, zcp, zmw, m5, zmp, zhw), M
    return None


best = None
graded = 0
for res, m0, zB, zCp, Bp, rB in placed:
    if time.time() - t0 > BUDGET:
        break
    if best and res < best[0]["power_reserve_h"] - 1e-9:
        break
    for tr, s4 in combos:
        m1, zCw, zTp, m2, zTw, zSp, T = tr
        m3, zSw, zEp = s4
        if d_(Bp, T) < 2 * W.ARBOR_R or not ok_disk(Bp, rB, [T]):
            continue
        if d_(C, Bp) < tip(m1, zCw) + W.ARBOR_R or d_(T, Bp) < max(tip(m1, zTp), tip(m2, zTw)) + W.ARBOR_R:
            continue
        if d_(S, Bp) < max(tip(m2, zSp), tip(m3, zSw)) + W.ARBOR_R or d_(E, Bp) < tip(m3, zEp) + W.ARBOR_R:
            continue
        disks = {"barrel_wheel": (Bp, rB, "barrel", 0), "centre_pinion": (C, tip(m0, zCp), "centre", 0),
                 "centre_wheel": (C, tip(m1, zCw), "centre", 1), "third_pinion": (T, tip(m1, zTp), "third", 1),
                 "third_wheel": (T, tip(m2, zTw), "third", 2), "fourth_pinion": (S, tip(m2, zSp), "fourth", 2),
                 "fourth_wheel": (S, tip(m3, zSw), "fourth", 3), "escape_pinion": (E, tip(m3, zEp), "escape", 3),
                 "escape_wheel": (E, RE, "escape_w", 4)}
        lv = best_levels(disks)
        if lv is None:
            continue
        mo = place_motion([C, S, E, T, Bp])
        if mo is None:
            continue
        (m4, zcp, zmw, m5, zmp, zhw), M = mo
        g = lambda z, m, l: {"teeth": int(z), "module": m, "level": int(l)}
        gd = lambda z, m, l: {"teeth": int(z), "module": m, "dial_level": int(l)}
        des = {"arbors": {"barrel": list(Bp), "third": list(T), "minute": list(M)},
               "gears": {"barrel_wheel": g(zB, m0, lv[0]), "centre_pinion": g(zCp, m0, lv[0]),
                         "centre_wheel": g(zCw, m1, lv[1]), "third_pinion": g(zTp, m1, lv[1]),
                         "third_wheel": g(zTw, m2, lv[2]), "fourth_pinion": g(zSp, m2, lv[2]),
                         "fourth_wheel": g(zSw, m3, lv[3]), "escape_pinion": g(zEp, m3, lv[3]),
                         "cannon_pinion": gd(zcp, m4, 0), "minute_wheel": gd(zmw, m4, 0),
                         "minute_pinion": gd(zmp, m5, 1), "hour_wheel": gd(zhw, m5, 1)},
               "escape_wheel_level": int(lv[4])}
        rep = W.grade(inst, des)
        graded += 1
        if not rep["valid"]:
            print("solver/grader disagree:", rep["violations"][:3])
            continue
        if best is None or rep["total_levels"] < best[0]["total_levels"]:
            best = (rep, des)
            print("found reserve %.2f h, %d levels at %.1fs" % (rep["power_reserve_h"], rep["total_levels"], time.time() - t0))
        if best[0]["total_levels"] <= 7:
            break

if best is None:
    print("NO SOLUTION within budget (%.1fs)" % (time.time() - t0))
    sys.exit(1)
json.dump(best[1], open(sys.argv[2], "w"), indent=1)
json.dump(best[0], open(sys.argv[3], "w"), indent=1)
print("reference: reserve %.2f h, %d levels, %.1fs" % (best[0]["power_reserve_h"], best[0]["total_levels"], time.time() - t0))
