"""Watch movement built up over five steps: rules, exact grader, planted reference, SVG view.

The movement has three sides, each with its own layers:
  train   between the plates: barrel -> centre -> third -> fourth -> escape (and the balance)
  dial    under the dial: motion work, later the date wheel
  wind    on the back: automatic winding, from the rotor at the centre down to the barrel

Steps (one movement, files persist; each step adds to it or changes a condition):
  1  going train, with a torque limit on the barrel ratio
  2  motion work (hour hand)
  3  the client fits a larger balance; fixed arbors stay put
  4  date wheel, driven by the hour wheel, once per 24 hours
  5  automatic winding: the rotor's swing must reach the barrel arbor within a ratio band

    python3 movement.py plant SEED OUTDIR
    python3 movement.py grade STEP instance.json design.json [ref_stepN.json] [view.svg]
"""
import json
import math
import os
import random
import sys
from fractions import Fraction as F

MODULES = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15]
PINION, WHEEL, BARREL = (7, 16), (30, 140), (40, 140)
ARBOR_R, GAP, EDGE, MESH_TOL, ARBOR_EDGE = 0.25, 0.10, 0.30, 0.005, 1.0
TOP = {"train": 8, "dial": 3, "wind": 3}
LEVEL_KEY = {"train": "level", "dial": "dial_level", "wind": "wind_level"}
BARREL_TURNS = F(13, 2)

TRAIN = ["barrel_wheel", "centre_pinion", "centre_wheel", "third_pinion", "third_wheel",
         "fourth_pinion", "fourth_wheel", "escape_pinion"]
DIAL = ["cannon_pinion", "minute_wheel", "minute_pinion", "hour_wheel"]
DATE = ["date_wheel"]
WIND = ["rotor_pinion", "wind1_wheel", "wind1_pinion", "wind2_wheel", "wind2_pinion", "ratchet_wheel"]
SIDE = {**{n: "train" for n in TRAIN}, **{n: "dial" for n in DIAL + DATE}, **{n: "wind" for n in WIND}}
ARBOR_OF = {"barrel_wheel": "barrel", "centre_pinion": "centre", "centre_wheel": "centre",
            "third_pinion": "third", "third_wheel": "third", "fourth_pinion": "fourth",
            "fourth_wheel": "fourth", "escape_pinion": "escape", "cannon_pinion": "centre",
            "minute_wheel": "minute", "minute_pinion": "minute", "hour_wheel": "centre",
            "date_wheel": "date", "rotor_pinion": "centre", "wind1_wheel": "wind1",
            "wind1_pinion": "wind1", "wind2_wheel": "wind2", "wind2_pinion": "wind2",
            "ratchet_wheel": "barrel"}
ALL_MESHES = [("barrel_wheel", "centre_pinion"), ("centre_wheel", "third_pinion"),
              ("third_wheel", "fourth_pinion"), ("fourth_wheel", "escape_pinion"),
              ("cannon_pinion", "minute_wheel"), ("minute_pinion", "hour_wheel"),
              ("hour_wheel", "date_wheel"), ("rotor_pinion", "wind1_wheel"),
              ("wind1_pinion", "wind2_wheel"), ("wind2_pinion", "ratchet_wheel")]
SIDE_ARBORS = {"train": ("barrel", "centre", "third", "fourth", "escape"),
               "dial": ("centre", "minute", "fourth", "date"),
               "wind": ("barrel", "centre", "third", "fourth", "escape", "wind1", "wind2")}
STEP_ARBORS = {1: ["barrel", "third"], 2: ["minute"], 4: ["date"], 5: ["wind1", "wind2"]}


def tip(m, z):
    return m * (z + 2) / 2.0


def pd(m, z1, z2):
    return m * (z1 + z2) / 2.0


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def names_for(step):
    return TRAIN + (DIAL if step >= 2 else []) + (DATE if step >= 4 else []) + (WIND if step >= 5 else [])


def arbors_for(step):
    return [a for s, lst in STEP_ARBORS.items() if s <= step for a in lst]


def balance_r(inst, step):
    return inst["balance"]["radius_after_change"] if step >= 3 else inst["balance"]["radius"]


# ------------------------------------------------------------------ grader
def grade(inst, des, step):
    v = []
    R = inst["plate_radius"]
    names = names_for(step)
    meshes = [m for m in ALL_MESHES if m[0] in names and m[1] in names]
    partner = {}                     # a gear can mesh with more than one gear (the hour wheel does)
    for a, b in meshes:
        partner.setdefault(a, set()).add(ARBOR_OF[b])
        partner.setdefault(b, set()).add(ARBOR_OF[a])
    try:
        arb = {k: [float(x) for x in p] for k, p in inst["fixed_arbors"].items()}
        for k in arbors_for(step):
            p = des["arbors"][k]
            if not isinstance(p, list) or len(p) != 2:
                raise ValueError
            arb[k] = [float(p[0]), float(p[1])]
        g = {}
        for n in names:
            e = des["gears"][n]
            z, lvl, m = e["teeth"], e[LEVEL_KEY[SIDE[n]]], e["module"]
            if type(z) is not int or type(lvl) is not int or type(m) not in (int, float):
                return {"valid": False, "violations": ["%s: teeth and level must be whole numbers, module a number" % n]}
            g[n] = {"z": z, "m": float(m), "lvl": lvl, "c": arb[ARBOR_OF[n]], "side": SIDE[n]}
        lE = des["escape_wheel_level"]
        if type(lE) is not int:
            raise ValueError
    except Exception as ex:
        return {"valid": False, "violations": ["design file is malformed or incomplete for step %d (%s)" % (step, type(ex).__name__)]}

    for k, p in arb.items():
        if not all(math.isfinite(x) for x in p):
            return {"valid": False, "violations": ["arbor %s is not finite" % k]}
        if math.hypot(*p) > R - ARBOR_EDGE + 1e-9:
            v.append("arbor %s is closer than %.1f to the plate edge" % (k, ARBOR_EDGE))
    ks = list(arb)
    for i, a in enumerate(ks):
        for b in ks[i + 1:]:
            if dist(arb[a], arb[b]) < 2 * ARBOR_R:
                v.append("arbors %s and %s coincide" % (a, b))
    for n, e in g.items():
        lo, hi = BARREL if n == "barrel_wheel" else (PINION if n.endswith("pinion") else WHEEL)
        if not lo <= e["z"] <= hi:
            v.append("%s: %d teeth is outside %d..%d" % (n, e["z"], lo, hi))
        if not any(abs(e["m"] - mm) < 1e-9 for mm in MODULES):
            v.append("%s: module %g is not allowed" % (n, e["m"]))
        top = TOP[e["side"]] - (1 if n == "barrel_wheel" else 0)
        if not 0 <= e["lvl"] < top:
            v.append("%s: level %d is out of range" % (n, e["lvl"]))
        e["rt"] = tip(e["m"], e["z"])
        e["levels"] = {e["lvl"], e["lvl"] + 1} if n == "barrel_wheel" else {e["lvl"]}
        if math.hypot(*e["c"]) + e["rt"] > R - EDGE + 1e-9:
            v.append("%s: reaches past the plate edge" % n)
    if not 0 <= lE < TOP["train"]:
        v.append("escape wheel level out of range")
    if v:
        return {"valid": False, "violations": v}

    for a, b in meshes:
        A, B = g[a], g[b]
        if abs(A["m"] - B["m"]) > 1e-9:
            v.append("%s and %s: modules differ" % (a, b))
        if A["lvl"] != B["lvl"]:
            v.append("%s and %s: not on the same level" % (a, b))
        want, got = pd(A["m"], A["z"], B["z"]), dist(A["c"], B["c"])
        if abs(got - want) > MESH_TOL:
            v.append("%s and %s: centre distance %.4f, the teeth need %.4f" % (a, b, got, want))

    z = {n: e["z"] for n, e in g.items()}
    ratio = F(z["barrel_wheel"], z["centre_pinion"])
    if ratio > F(str(inst["max_barrel_ratio"])):
        v.append("barrel ratio %.3f exceeds %s: too little torque would reach the escapement" % (float(ratio), inst["max_barrel_ratio"]))
    reserve = BARREL_TURNS * ratio
    if reserve < inst["power_reserve_target_h"]:
        v.append("power reserve %.2f h is below the %d h target" % (float(reserve), inst["power_reserve_target_h"]))
    fourth = F(z["centre_wheel"], z["third_pinion"]) * F(z["third_wheel"], z["fourth_pinion"])
    if fourth != 60:
        v.append("fourth arbor turns %s times per centre turn, not 60" % fourth)
    esc = fourth * F(z["fourth_wheel"], z["escape_pinion"])
    need = F(inst["beats_per_hour"], 2 * inst["escape_wheel"]["teeth"])
    if esc != need:
        v.append("escape wheel turns %s per hour; %d beats per hour needs %s" % (esc, inst["beats_per_hour"], need))
    if step >= 2:
        hour = F(z["cannon_pinion"], z["minute_wheel"]) * F(z["minute_pinion"], z["hour_wheel"])
        if hour != F(1, 12):
            v.append("hour wheel turns %s per centre turn, not 1/12" % hour)
    if step >= 4:
        if F(1, 12) * F(z["hour_wheel"], z["date_wheel"]) != F(1, 24):
            v.append("date wheel does not turn once per 24 hours")
    wind = None
    if step >= 5:
        wind = F(z["rotor_pinion"], z["wind1_wheel"]) * F(z["wind1_pinion"], z["wind2_wheel"]) * F(z["wind2_pinion"], z["ratchet_wheel"])
        lo, hi = inst["winding_rotor_turns_per_barrel_turn"]
        if not lo <= 1 / wind <= hi:
            v.append("rotor turns %.1f times per barrel turn; it must be %d to %d (too few: the rotor cannot wind the spring; too many: it winds too slowly)" % (float(1 / wind), lo, hi))

    for a in set(ARBOR_OF[n] for n in g):
        on = [n for n in g if ARBOR_OF[n] == a]
        for i, n1 in enumerate(on):
            for n2 in on[i + 1:]:
                if g[n1]["side"] == g[n2]["side"] and g[n1]["levels"] & g[n2]["levels"]:
                    v.append("%s and %s share an arbor and a level" % (n1, n2))
    if g["escape_pinion"]["lvl"] == lE:
        v.append("escape pinion and escape wheel share a level")

    RB = balance_r(inst, step)
    for n, e in g.items():
        for k, p in arb.items():
            if k == ARBOR_OF[n] or k in partner.get(n, ()) or k not in SIDE_ARBORS[e["side"]]:
                continue
            if dist(e["c"], p) < e["rt"] + ARBOR_R - 1e-9:
                v.append("%s: hits the %s arbor" % (n, k))
        if e["side"] in ("train", "wind") and dist(e["c"], inst["balance"]["centre"]) < e["rt"] + RB + GAP - 1e-9:
            v.append("%s: hits the balance" % n)

    meshset = {frozenset(p) for p in meshes}
    disks = [(n, e["c"], e["rt"], e["levels"], e["side"]) for n, e in g.items()]
    disks.append(("escape_wheel", arb["escape"], inst["escape_wheel"]["radius"], {lE}, "train"))
    for i in range(len(disks)):
        for j in range(i + 1, len(disks)):
            n1, c1, r1, l1, s1 = disks[i]
            n2, c2, r2, l2, s2 = disks[j]
            if s1 != s2 or not (l1 & l2) or frozenset((n1, n2)) in meshset:
                continue
            if "escape_wheel" not in (n1, n2) and ARBOR_OF[n1] == ARBOR_OF[n2]:
                continue
            if dist(c1, c2) < r1 + r2 + GAP - 1e-9:
                v.append("%s and %s overlap on a level" % (n1, n2))

    used = {"train": set(), "dial": set(), "wind": set()}
    for n, e in g.items():
        used[e["side"]] |= e["levels"]
    used["train"].add(lE)
    total = sum(len(s) for s in used.values())
    out = {"valid": not v, "violations": v, "power_reserve_h": round(float(reserve), 3),
           "levels_by_side": {k: len(s) for k, s in used.items()}, "total_levels": total}
    if wind is not None:
        out["rotor_turns_per_barrel_turn"] = round(float(1 / wind), 3)
    return out


def score(rep, ref):
    """0 if invalid; else 0.5 x reserve vs reference + 0.5 x reference levels vs yours, each capped at 1."""
    if not rep.get("valid"):
        return 0.0
    a = min(1.0, rep["power_reserve_h"] / ref["power_reserve_h"])
    b = min(1.0, ref["total_levels"] / rep["total_levels"])
    return round(0.5 * a + 0.5 * b, 4)


# ------------------------------------------------------------------ planted reference
def _rnd(p):
    return [round(p[0], 6), round(p[1], 6)]


def _circ(p, r1, q, r2):
    d = dist(p, q)
    if d == 0 or d > r1 + r2 or d < abs(r1 - r2):
        return []
    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, r1 * r1 - a * a))
    mx, my = p[0] + a * (q[0] - p[0]) / d, p[1] + a * (q[1] - p[1]) / d
    return [[mx + h * (q[1] - p[1]) / d, my - h * (q[0] - p[0]) / d], [mx - h * (q[1] - p[1]) / d, my + h * (q[0] - p[0]) / d]]


def _set_levels(d, lv):
    names = [("barrel_wheel", 0), ("centre_pinion", 0), ("centre_wheel", 1), ("third_pinion", 1),
             ("third_wheel", 2), ("fourth_pinion", 2), ("fourth_wheel", 3), ("escape_pinion", 3)]
    for n, i in names:
        d["gears"][n]["level"] = lv[i]
    d["escape_wheel_level"] = lv[4]


def _for_step(base, step):
    d = json.loads(json.dumps(base))
    d["arbors"] = {k: p for k, p in d["arbors"].items() if k in arbors_for(step)}
    d["gears"] = {n: e for n, e in d["gears"].items() if n in names_for(step)}
    return d


def plant(seed, tries=300000):
    rng = random.Random(seed)
    P = lambda c, r, a: [c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))]
    TRAIN_LV = sorted(((a, b, c, d, e) for a in range(4) for b in range(5) for c in range(5) for d in range(5) for e in range(6)
                       if a != b and b != c and c != d and d != e),
                      key=lambda t: len({t[0], t[0] + 1, t[1], t[2], t[3], t[4]}))
    for _ in range(tries):
        R = round(rng.uniform(12.5, 13.5), 2)
        beat = rng.choice([18000, 21600, 25200, 28800])
        k = beat // 1800
        zEp = rng.randint(7, 10)
        if k * zEp > WHEEL[1]:
            continue
        m3 = rng.choice(MODULES[:5])
        zTp, zSp = rng.randint(7, 12), rng.randint(7, 12)
        prod = 60 * zTp * zSp
        divs = [x for x in range(30, 141) if prod % x == 0 and 30 <= prod // x <= 140]
        if not divs:
            continue
        zCw = rng.choice(divs)
        zTw = prod // zCw
        zCp = rng.randint(8, 14)
        maxr = round(rng.uniform(6.0, 8.0), 2)
        zB = rng.randint(max(40, 5 * zCp), min(140, int(maxr * zCp)))
        m0 = rng.choice(MODULES[2:8])
        m1, m2 = rng.choice(MODULES[:5]), rng.choice(MODULES[:5])
        if tip(m0, zB) > 5.5 or tip(m1, zCw) > 5.0 or tip(m2, zTw) > 4.5 or tip(m3, k * zEp) > 4.2:
            continue
        C = [0.0, 0.0]
        a0 = rng.uniform(0, 360)               # the train curls round the centre; the barrel sits opposite
        turn = rng.choice([-1, 1])
        T = P(C, pd(m1, zCw, zTp), a0)
        S = P(T, pd(m2, zTw, zSp), a0 + turn * rng.uniform(60, 130))
        E = P(S, pd(m3, k * zEp, zEp), a0 + turn * rng.uniform(120, 220))
        B = P(C, pd(m0, zB, zCp), a0 - turn * rng.uniform(90, 180))
        RE, RB = 1.9, round(rng.uniform(3.2, 3.8), 2)
        RB2 = round(RB + rng.uniform(0.8, 1.3), 2)
        if math.hypot(*E) + RE > R - EDGE:
            continue
        Bal = None
        for ang in rng.sample(range(0, 360, 15), 24):
            cand = P(E, RE + RB2 + 1.2, ang)
            if math.hypot(*cand) + RB2 <= R - EDGE and all(dist(cand, q) > RB2 + 1.0 for q in (C, T, S, B)):
                Bal = cand
                break
        if Bal is None:
            continue
        gt = lambda z_, m, l: {"teeth": z_, "module": m, "level": l}
        gd = lambda z_, m, l: {"teeth": z_, "module": m, "dial_level": l}
        gw = lambda z_, m, l: {"teeth": z_, "module": m, "wind_level": l}
        inst = {"plate_radius": R, "beats_per_hour": beat, "power_reserve_target_h": 0, "max_barrel_ratio": maxr,
                "fixed_arbors": {"centre": C, "fourth": _rnd(S), "escape": _rnd(E)},
                "escape_wheel": {"radius": RE, "teeth": 15},
                "balance": {"centre": _rnd(Bal), "radius": RB, "radius_after_change": RB2},
                "winding_rotor_turns_per_barrel_turn": [0, 0]}
        inst["power_reserve_target_h"] = int(float(BARREL_TURNS * F(zB, zCp)) * 0.85)
        base = {"arbors": {"barrel": _rnd(B), "third": _rnd(T)},
                "gears": {"barrel_wheel": gt(zB, m0, 0), "centre_pinion": gt(zCp, m0, 0),
                          "centre_wheel": gt(zCw, m1, 2), "third_pinion": gt(zTp, m1, 2),
                          "third_wheel": gt(zTw, m2, 3), "fourth_pinion": gt(zSp, m2, 3),
                          "fourth_wheel": gt(k * zEp, m3, 4), "escape_pinion": gt(zEp, m3, 4)},
                "escape_wheel_level": 5}
        # cheap pre-check on step 3 (larger balance) with every gear on its own level
        big = json.loads(json.dumps(inst))
        big["balance"]["radius"] = RB2          # step-1 rules with the step-3 balance
        r = grade(big, _for_step(base, 1), 1)
        if any("overlap" not in x and "share" not in x for x in r["violations"]):
            continue
        lv_ok = None
        for lv in TRAIN_LV:
            _set_levels(base, lv)
            if grade(big, _for_step(base, 1), 1)["valid"]:
                lv_ok = lv
                break
        if lv_ok is None:
            continue
        # motion work + date
        done = False
        for _ in range(80):
            zcp, zmp = rng.randint(8, 14), rng.randint(8, 14)
            num = 12 * zcp * zmp
            dv = [x for x in range(30, 81) if num % x == 0 and 30 <= num // x <= 70]
            if not dv:
                continue
            zmw = rng.choice(dv)
            zhw = num // zmw
            prs = [(a, b) for a in MODULES for b in MODULES if abs(pd(a, zcp, zmw) - pd(b, zmp, zhw)) <= MESH_TOL / 2]
            if not prs:
                continue
            m4, m5 = rng.choice(prs)
            base["arbors"]["minute"] = _rnd(P(C, pd(m4, zcp, zmw), rng.uniform(0, 360)))
            base["arbors"]["date"] = _rnd(P(C, pd(m5, zhw, 2 * zhw), rng.uniform(0, 360)))
            base["gears"].update({"cannon_pinion": gd(zcp, m4, 0), "minute_wheel": gd(zmw, m4, 0),
                                  "minute_pinion": gd(zmp, m5, 1), "hour_wheel": gd(zhw, m5, 1),
                                  "date_wheel": gd(2 * zhw, m5, 1)})
            if grade(inst, _for_step(base, 4), 4)["valid"]:
                done = True
                break
        if not done:
            continue
        # automatic winding: rotor pinion at the centre -> wind1 -> wind2 -> ratchet on the barrel arbor
        done = False
        for _ in range(400):
            zrp, zw1p, zw2p = rng.randint(7, 12), rng.randint(7, 12), rng.randint(7, 12)
            zw1w, zw2w, zrw = rng.randint(40, 90), rng.randint(40, 90), rng.randint(40, 90)
            ma, mb, mc = rng.choice(MODULES[:5]), rng.choice(MODULES[:5]), rng.choice(MODULES[:6])
            W1 = P(C, pd(ma, zrp, zw1w), rng.uniform(0, 360))
            for W2 in _circ(W1, pd(mb, zw1p, zw2w), B, pd(mc, zw2p, zrw)):
                base["arbors"]["wind1"], base["arbors"]["wind2"] = _rnd(W1), _rnd(W2)
                base["gears"].update({"rotor_pinion": gw(zrp, ma, 0), "wind1_wheel": gw(zw1w, ma, 0),
                                      "wind1_pinion": gw(zw1p, mb, 1), "wind2_wheel": gw(zw2w, mb, 1),
                                      "wind2_pinion": gw(zw2p, mc, 2), "ratchet_wheel": gw(zrw, mc, 2)})
                turns = float(F(zw1w, zrp) * F(zw2w, zw1p) * F(zrw, zw2p))
                lo, hi = int(turns * rng.uniform(0.75, 0.9)), int(math.ceil(turns * rng.uniform(1.1, 1.3)))
                inst["winding_rotor_turns_per_barrel_turn"] = [lo, hi]
                if grade(inst, _for_step(base, 5), 5)["valid"]:
                    done = True
                    break
                # try squeezing winding levels
                for wl in ((0, 1, 0), (0, 1, 2), (1, 0, 1), (0, 2, 1)):
                    for (wh, pn), l in zip((("wind1_wheel", "rotor_pinion"), ("wind2_wheel", "wind1_pinion"), ("ratchet_wheel", "wind2_pinion")), wl):
                        base["gears"][wh]["wind_level"] = l
                        base["gears"][pn]["wind_level"] = l
                    if grade(inst, _for_step(base, 5), 5)["valid"]:
                        done = True
                        break
                if done:
                    break
            if done:
                break
        if not done:
            continue
        designs = {}
        for step in (1, 2, 3, 4, 5):
            d = _for_step(base, step)
            r = grade(inst, d, step)
            if not r["valid"]:
                break
            designs[step] = (d, r)
        if len(designs) == 5:
            return inst, designs
    raise RuntimeError("no planted movement")


# ------------------------------------------------------------------ view
def svg(inst, des, step, path):
    R = inst["plate_radius"]
    arb = dict(inst["fixed_arbors"])
    arb.update(des.get("arbors", {}))
    colours = ["#d1495b", "#edae49", "#00798c", "#30638e", "#6a4c93", "#2a9d8f", "#e76f51", "#8ab17d"]
    W = 260
    allv = {}
    for n in names_for(step):
        e = des["gears"][n]
        side = SIDE[n]
        lv = e[LEVEL_KEY[side]]
        for l in ([lv, lv + 1] if n == "barrel_wheel" else [lv]):
            allv.setdefault((side, l), []).append((n, arb[ARBOR_OF[n]], tip(e["module"], e["teeth"])))
    allv.setdefault(("train", des["escape_wheel_level"]), []).append(("escape_wheel", arb["escape"], inst["escape_wheel"]["radius"]))
    order = {"train": 0, "dial": 1, "wind": 2}
    keys = sorted(allv, key=lambda k: (order[k[0]], k[1]))
    s = W / (2 * R + 2)
    body = []
    allnames = TRAIN + DIAL + DATE + WIND + ["escape_wheel"]
    for i, key in enumerate(keys):
        ox, oy = (i % 4) * (W + 20) + W / 2 + 10, (i // 4) * (W + 40) + W / 2 + 30
        body.append('<text x="%.1f" y="%.1f" font-size="13" font-family="sans-serif">%s level %d</text>' % (ox - W / 2, oy - W / 2 - 8, key[0], key[1]))
        body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#f4f1ea" stroke="#999"/>' % (ox, oy, R * s))
        if key[0] in ("train", "wind"):
            b = inst["balance"]
            body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ddd" stroke="#666" stroke-dasharray="3,2"/>' % (ox + b["centre"][0] * s, oy - b["centre"][1] * s, balance_r(inst, step) * s))
        for n, c, rt in allv[key]:
            col = colours[allnames.index(n) % len(colours)]
            body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.35" stroke="%s"/>' % (ox + c[0] * s, oy - c[1] * s, rt * s, col, col))
            body.append('<text x="%.1f" y="%.1f" font-size="8" font-family="sans-serif" text-anchor="middle">%s</text>' % (ox + c[0] * s, oy - c[1] * s - rt * s - 2, n.replace("_", " ")))
        for kk, p in arb.items():
            body.append('<circle cx="%.1f" cy="%.1f" r="2" fill="black"/><text x="%.1f" y="%.1f" font-size="7" font-family="sans-serif" fill="#555">%s</text>' % (ox + p[0] * s, oy - p[1] * s, ox + p[0] * s + 3, oy - p[1] * s + 9, kk))
    rows = (len(keys) + 3) // 4
    open(path, "w").write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" style="background:white">%s</svg>' % (4 * (W + 20) + 20, rows * (W + 40) + 30, "".join(body)))


if __name__ == "__main__":
    if sys.argv[1] == "plant":
        inst, designs = plant(int(sys.argv[2]))
        out = sys.argv[3]
        os.makedirs(out, exist_ok=True)
        json.dump(inst, open(os.path.join(out, "instance.json"), "w"), indent=1)
        for step, (d, r) in designs.items():
            json.dump(d, open(os.path.join(out, "ref_design_step%d.json" % step), "w"), indent=1)
            json.dump(r, open(os.path.join(out, "ref_step%d.json" % step), "w"), indent=1)
            svg(inst, d, step, os.path.join(out, "ref_step%d.svg" % step))
            print("step", step, "reserve %.1f h, levels %s" % (r["power_reserve_h"], r["levels_by_side"]))
    elif sys.argv[1] == "grade":
        step = int(sys.argv[2])
        inst = json.load(open(sys.argv[3]))
        try:
            des = json.load(open(sys.argv[4]))
            rep = grade(inst, des, step) if isinstance(des, dict) else {"valid": False, "violations": ["design is not a JSON object"]}
        except Exception as ex:
            rep = {"valid": False, "violations": ["no readable design (%s)" % type(ex).__name__]}
        if len(sys.argv) > 5 and sys.argv[5] != "-":
            rep["score"] = score(rep, json.load(open(sys.argv[5])))
        if len(sys.argv) > 6 and rep.get("valid"):
            svg(inst, des, step, sys.argv[6])
        print(json.dumps(rep, indent=1))
