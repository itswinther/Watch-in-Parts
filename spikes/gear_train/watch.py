"""Watch gear train: instance generator, exact grader and SVG view. One file, the single source of rules.

    python3 watch.py gen SEED instance.json
    python3 watch.py grade instance.json design.json [report.json] [view.svg]
"""
import json
import math
import random
import sys
from fractions import Fraction as F

MODULES = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15]
PINION = (7, 16)
WHEEL = (30, 140)
BARREL = (40, 140)
ARBOR_R = 0.25      # pivot clearance radius
GAP = 0.10          # clearance between non-meshing gears on one level
EDGE = 0.30         # clearance to the plate edge
MESH_TOL = 0.005    # centre-distance tolerance for a mesh
ARBOR_EDGE = 1.0    # arbor centres stay this far inside the plate
LEVELS = 8          # train levels 0..7; dial levels 0..2
DIAL_LEVELS = 3
BARREL_TURNS = F(13, 2)

TRAIN = ["barrel_wheel", "centre_pinion", "centre_wheel", "third_pinion", "third_wheel",
         "fourth_pinion", "fourth_wheel", "escape_pinion"]
DIAL = ["cannon_pinion", "minute_wheel", "minute_pinion", "hour_wheel"]
ARBOR_OF = {"barrel_wheel": "barrel", "centre_pinion": "centre", "centre_wheel": "centre",
            "third_pinion": "third", "third_wheel": "third", "fourth_pinion": "fourth",
            "fourth_wheel": "fourth", "escape_pinion": "escape", "cannon_pinion": "centre",
            "minute_wheel": "minute", "minute_pinion": "minute", "hour_wheel": "centre"}
MESHES = [("barrel_wheel", "centre_pinion"), ("centre_wheel", "third_pinion"),
          ("third_wheel", "fourth_pinion"), ("fourth_wheel", "escape_pinion"),
          ("cannon_pinion", "minute_wheel"), ("minute_pinion", "hour_wheel")]
TRAIN_ARBORS = ("barrel", "centre", "third", "fourth", "escape")
DIAL_ARBORS = ("centre", "minute", "fourth")
PARTNER = {}
for a, b in MESHES:
    PARTNER[a] = ARBOR_OF[b]
    PARTNER[b] = ARBOR_OF[a]


def tip(m, z):
    return m * (z + 2) / 2.0


def pitch_dist(m, z1, z2):
    return m * (z1 + z2) / 2.0


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def polar(r, deg):
    return [round(r * math.cos(math.radians(deg)), 4), round(r * math.sin(math.radians(deg)), 4)]


# ---------------------------------------------------------------- instance
def gen(seed):
    rng = random.Random(seed)
    for _ in range(10000):
        R = round(rng.uniform(12.0, 13.5), 2)
        beat = rng.choice([18000, 21600, 25200, 28800])
        k = beat // 1800                       # fourth -> escape ratio
        S = polar(round(rng.uniform(5.0, 7.0), 2), rng.choice([270, 180, 0]))
        opts = [(m, k * ze, ze) for m in MODULES for ze in range(7, 11) if WHEEL[0] <= k * ze <= WHEEL[1]]
        m, zsw, zep = rng.choice(opts)
        d = pitch_dist(m, zsw, zep)
        ang = rng.uniform(0, 360)
        E = [S[0] + d * math.cos(math.radians(ang)), S[1] + d * math.sin(math.radians(ang))]
        RE = 1.9
        RB = round(rng.uniform(3.6, 4.4), 2)
        # balance sits beyond the escape wheel, roughly away from the fourth arbor
        u = math.radians(ang + rng.uniform(-50, 50))
        Bal = [E[0] + (RE + RB + 1.2) * math.cos(u), E[1] + (RE + RB + 1.2) * math.sin(u)]
        E = [round(x, 4) for x in E]
        Bal = [round(x, 4) for x in Bal]
        if math.hypot(*E) + RE > R - EDGE or math.hypot(*E) > R - ARBOR_EDGE:
            continue
        if math.hypot(*Bal) + RB > R - EDGE:
            continue
        if dist(S, Bal) < tip(m, zsw) + RB + GAP or dist((0, 0), Bal) < RB + 3.0:
            continue
        # the fourth wheel and escape pinion must clear the centre arbor, and both fit the plate
        if dist(S, (0, 0)) < tip(m, zsw) + ARBOR_R or dist(E, (0, 0)) < tip(m, zep) + ARBOR_R + 2.0:
            continue
        if math.hypot(*S) + tip(m, zsw) > R - EDGE or dist(E, Bal) < tip(m, zep) + RB + GAP:
            continue
        target = rng.choice([36, 40, 42, 45, 48])
        return {"seed": seed, "plate_radius": R, "beats_per_hour": beat, "power_reserve_target_h": target,
                "fixed_arbors": {"centre": [0.0, 0.0], "fourth": S, "escape": E},
                "escape_wheel": {"radius": RE, "teeth": 15},
                "balance": {"centre": Bal, "radius": RB}}
    raise RuntimeError("no instance")


def plant(seed, tries=200000):
    """Build a valid movement at random, then publish only its fixed points. Returns (instance, design)."""
    rng = random.Random(seed)
    P = lambda c, r, a: [c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a))]
    for _ in range(tries):
        R = round(rng.uniform(12.0, 13.5), 2)
        beat = rng.choice([18000, 21600, 25200, 28800])
        k = beat // 1800
        zTp, zSp = rng.randint(7, 12), rng.randint(7, 12)
        prod = 60 * zTp * zSp
        divs = [z for z in range(WHEEL[0], WHEEL[1] + 1) if prod % z == 0 and WHEEL[0] <= prod // z <= WHEEL[1]]
        if not divs:
            continue
        zCw = rng.choice(divs)
        zTw = prod // zCw
        zEp = rng.randint(7, 10)
        zSw = k * zEp
        if zSw > WHEEL[1]:
            continue
        zCp = rng.randint(8, 14)
        zB = rng.randint(max(BARREL[0], 5 * zCp), min(BARREL[1], 9 * zCp))
        small = MODULES[:5]
        m0 = rng.choice(MODULES[2:8])
        m1, m2, m3 = (rng.choice(small) for _ in range(3))
        if tip(m0, zB) > 5.5 or tip(m1, zCw) > 5.0 or tip(m2, zTw) > 4.5 or tip(m3, zSw) > 4.0:
            continue
        C = [0.0, 0.0]
        T = P(C, pitch_dist(m1, zCw, zTp), rng.uniform(0, 360))
        S = P(T, pitch_dist(m2, zTw, zSp), rng.uniform(0, 360))
        E = P(S, pitch_dist(m3, zSw, zEp), rng.uniform(0, 360))
        B = P(C, pitch_dist(m0, zB, zCp), rng.uniform(0, 360))
        RE, RB = 1.9, round(rng.uniform(3.4, 4.2), 2)
        Bal = P(E, RE + RB + 1.2, rng.uniform(0, 360))
        if math.hypot(*Bal) + RB > R - EDGE or math.hypot(*E) + RE > R - EDGE:
            continue
        mo = None
        for _ in range(40):
            zcp, zmp = rng.randint(8, 14), rng.randint(8, 14)
            num = 12 * zcp * zmp
            dv = [z for z in range(30, 81) if num % z == 0 and WHEEL[0] <= num // z <= WHEEL[1]]
            if not dv:
                continue
            zmw = rng.choice(dv)
            zhw = num // zmw
            pairs = [(a, b) for a in MODULES for b in MODULES
                     if abs(pitch_dist(a, zcp, zmw) - pitch_dist(b, zmp, zhw)) <= MESH_TOL / 2]
            if pairs:
                m4, m5 = rng.choice(pairs)
                mo = (m4, zcp, zmw, m5, zmp, zhw)
                break
        if mo is None:
            continue
        m4, zcp, zmw, m5, zmp, zhw = mo
        M = P(C, pitch_dist(m4, zcp, zmw), rng.uniform(0, 360))
        rnd = lambda p: [round(p[0], 6), round(p[1], 6)]
        inst = {"seed": seed, "plate_radius": R, "beats_per_hour": beat, "power_reserve_target_h": 0,
                "fixed_arbors": {"centre": C, "fourth": rnd(S), "escape": rnd(E)},
                "escape_wheel": {"radius": RE, "teeth": 15}, "balance": {"centre": rnd(Bal), "radius": RB}}
        g = lambda z, m, l: {"teeth": z, "module": m, "level": l}
        gd = lambda z, m, l: {"teeth": z, "module": m, "dial_level": l}
        des = {"arbors": {"barrel": rnd(B), "third": rnd(T), "minute": rnd(M)},
               "gears": {"barrel_wheel": g(zB, m0, 0), "centre_pinion": g(zCp, m0, 0),
                         "centre_wheel": g(zCw, m1, 2), "third_pinion": g(zTp, m1, 2),
                         "third_wheel": g(zTw, m2, 3), "fourth_pinion": g(zSp, m2, 3),
                         "fourth_wheel": g(zSw, m3, 4), "escape_pinion": g(zEp, m3, 4),
                         "cannon_pinion": gd(zcp, m4, 0), "minute_wheel": gd(zmw, m4, 0),
                         "minute_pinion": gd(zmp, m5, 1), "hour_wheel": gd(zhw, m5, 1)},
               "escape_wheel_level": 5}
        rep = grade(inst, des)
        hard = [x for x in rep["violations"] if "overlap" not in x and "share" not in x and "power reserve" not in x]
        if hard:
            continue
        # squeeze levels: try layouts with the fewest distinct levels first
        best = None
        for lv in sorted(((a, b, c, d, e) for a in range(4) for b in range(5) for c in range(5) for d in range(5) for e in range(6)
                          if a != b and b != c and c != d and d != e),
                         key=lambda t: len({t[0], t[0] + 1, t[1], t[2], t[3], t[4]})):
            for n, l in zip(["barrel_wheel", "centre_wheel", "third_wheel", "fourth_wheel"], lv[:4]):
                des["gears"][n]["level"] = l
            des["gears"]["centre_pinion"]["level"] = lv[0]
            des["gears"]["third_pinion"]["level"] = lv[1]
            des["gears"]["fourth_pinion"]["level"] = lv[2]
            des["gears"]["escape_pinion"]["level"] = lv[3]
            des["escape_wheel_level"] = lv[4]
            r2 = grade(inst, des)
            if not [x for x in r2["violations"] if "power reserve" not in x]:
                best = lv
                break
        if best is None:
            continue
        res = float(BARREL_TURNS * F(zB, zCp))
        inst["power_reserve_target_h"] = int(res * 0.85)
        rep = grade(inst, des)
        if rep["valid"]:
            return inst, des, rep
    raise RuntimeError("no planted movement")


# ---------------------------------------------------------------- grader
def grade(inst, des):
    v = []      # violations
    R = inst["plate_radius"]
    try:
        arb = {k: [float(x) for x in p] for k, p in inst["fixed_arbors"].items()}
        for k in ("barrel", "third", "minute"):
            p = des["arbors"][k]
            arb[k] = [float(p[0]), float(p[1])]
        g = {}
        for name in TRAIN + DIAL:
            e = des["gears"][name]
            z, m = e["teeth"], e["module"]
            if not isinstance(z, int) or isinstance(z, bool):
                v.append("%s: teeth must be a whole number" % name)
                return {"valid": False, "violations": v, "score": 0.0}
            lvl = e["dial_level"] if name in DIAL else e["level"]
            if not isinstance(lvl, int) or isinstance(lvl, bool):
                v.append("%s: level must be a whole number" % name)
                return {"valid": False, "violations": v, "score": 0.0}
            g[name] = {"z": z, "m": float(m), "lvl": lvl, "c": arb[ARBOR_OF[name]]}
        lE = des["escape_wheel_level"]
        if not isinstance(lE, int) or isinstance(lE, bool):
            raise ValueError
    except Exception as ex:
        return {"valid": False, "violations": ["design file is malformed (%s)" % type(ex).__name__], "score": 0.0}

    bc = inst["balance"]["centre"]
    if math.hypot(*bc) + inst["balance"]["radius"] > R - EDGE + 1e-9:
        v.append("instance error: balance outside the plate")
    for k, p in arb.items():
        if not all(math.isfinite(x) for x in p):
            return {"valid": False, "violations": ["arbor %s is not finite" % k], "score": 0.0}
        if math.hypot(*p) > R - ARBOR_EDGE + 1e-9:
            v.append("arbor %s is closer than %.1f to the plate edge" % (k, ARBOR_EDGE))
    for i, a in enumerate(arb):
        for b in list(arb)[i + 1:]:
            if dist(arb[a], arb[b]) < 2 * ARBOR_R:
                v.append("arbors %s and %s coincide" % (a, b))

    for n, e in g.items():
        lo, hi = BARREL if n == "barrel_wheel" else (PINION if n.endswith("pinion") else WHEEL)
        if not lo <= e["z"] <= hi:
            v.append("%s: %d teeth is outside %d..%d" % (n, e["z"], lo, hi))
        if not any(abs(e["m"] - mm) < 1e-9 for mm in MODULES):
            v.append("%s: module %g is not an allowed module" % (n, e["m"]))
        top = DIAL_LEVELS if n in DIAL else LEVELS - (1 if n == "barrel_wheel" else 0)
        if not 0 <= e["lvl"] < top:
            v.append("%s: level %d is out of range" % (n, e["lvl"]))
        e["rt"] = tip(e["m"], e["z"])
        e["levels"] = {e["lvl"], e["lvl"] + 1} if n == "barrel_wheel" else {e["lvl"]}
        if math.hypot(*e["c"]) + e["rt"] > R - EDGE + 1e-9:
            v.append("%s: reaches past the plate edge" % n)
    if not 0 <= lE < LEVELS:
        v.append("escape wheel level out of range")
    if v:
        return {"valid": False, "violations": v, "score": 0.0}

    # meshes
    for a, b in MESHES:
        A, B = g[a], g[b]
        if abs(A["m"] - B["m"]) > 1e-9:
            v.append("%s and %s: modules differ" % (a, b))
        if A["lvl"] != B["lvl"]:
            v.append("%s and %s: not on the same level" % (a, b))
        want = pitch_dist(A["m"], A["z"], B["z"])
        got = dist(A["c"], B["c"])
        if abs(got - want) > MESH_TOL:
            v.append("%s and %s: centre distance %.4f, the teeth need %.4f" % (a, b, got, want))

    # kinematics, exact
    z = {n: e["z"] for n, e in g.items()}
    fourth = F(z["centre_wheel"], z["third_pinion"]) * F(z["third_wheel"], z["fourth_pinion"])
    if fourth != 60:
        v.append("fourth arbor turns %s times per centre turn, not 60" % fourth)
    esc = fourth * F(z["fourth_wheel"], z["escape_pinion"])
    need = F(inst["beats_per_hour"], 2 * inst["escape_wheel"]["teeth"])
    if esc != need:
        v.append("escape wheel turns %s per hour, the beat rate needs %s" % (esc, need))
    hour = F(z["cannon_pinion"], z["minute_wheel"]) * F(z["minute_pinion"], z["hour_wheel"])
    if hour != F(1, 12):
        v.append("hour wheel turns %s per centre turn, not 1/12" % hour)
    reserve = BARREL_TURNS * F(z["barrel_wheel"], z["centre_pinion"])
    if reserve < inst["power_reserve_target_h"]:
        v.append("power reserve %.2f h is below the %d h target" % (float(reserve), inst["power_reserve_target_h"]))

    # same-arbor gears on different levels
    for a in ARBOR_OF.values():
        on = [n for n in g if ARBOR_OF[n] == a]
        for i, n1 in enumerate(on):
            for n2 in on[i + 1:]:
                if (n1 in DIAL) == (n2 in DIAL) and g[n1]["levels"] & g[n2]["levels"]:
                    v.append("%s and %s share an arbor and a level" % (n1, n2))
    if g["escape_pinion"]["lvl"] == lE:
        v.append("escape pinion and escape wheel share a level")

    # gear vs arbors, and vs balance. Train gears sit between the plates, where the barrel,
    # centre, third, fourth and escape arbors run; dial gears sit under the dial, where the
    # centre, minute and fourth (seconds) arbors run.
    for n, e in g.items():
        for k, p in arb.items():
            if k == ARBOR_OF[n] or k == PARTNER[n]:
                continue
            if k not in (DIAL_ARBORS if n in DIAL else TRAIN_ARBORS):
                continue
            if dist(e["c"], p) < e["rt"] + ARBOR_R - 1e-9:
                v.append("%s: hits the %s arbor" % (n, k))
        if n in TRAIN and dist(e["c"], inst["balance"]["centre"]) < e["rt"] + inst["balance"]["radius"] + GAP - 1e-9:
            v.append("%s: hits the balance" % n)

    # gear vs gear on a shared level
    meshset = {frozenset(p) for p in MESHES}
    disks = [(n, e["c"], e["rt"], e["levels"], n in DIAL) for n, e in g.items()]
    disks.append(("escape_wheel", arb["escape"], inst["escape_wheel"]["radius"], {lE}, False))
    for i in range(len(disks)):
        for j in range(i + 1, len(disks)):
            n1, c1, r1, l1, d1 = disks[i]
            n2, c2, r2, l2, d2 = disks[j]
            if d1 != d2 or not (l1 & l2) or frozenset((n1, n2)) in meshset:
                continue
            if n1 != "escape_wheel" and n2 != "escape_wheel" and ARBOR_OF[n1] == ARBOR_OF[n2]:
                continue
            if dist(c1, c2) < r1 + r2 + GAP - 1e-9:
                v.append("%s and %s overlap on a level" % (n1, n2))

    levels = set()
    for n in TRAIN:
        levels |= g[n]["levels"]
    levels.add(lE)
    dial = {g[n]["lvl"] for n in DIAL}
    out = {"valid": not v, "violations": v, "power_reserve_h": round(float(reserve), 3),
           "train_levels": len(levels), "dial_levels": len(dial), "total_levels": len(levels) + len(dial)}
    out["score"] = 0.0
    return out


def score(rep, ref):
    if not rep["valid"]:
        return 0.0
    a = min(1.0, rep["power_reserve_h"] / ref["power_reserve_h"])
    b = min(1.0, ref["total_levels"] / rep["total_levels"])
    return round(0.5 * a + 0.5 * b, 4)


# ---------------------------------------------------------------- view
def svg(inst, des, path):
    R = inst["plate_radius"]
    arb = dict(inst["fixed_arbors"])
    arb.update({k: des["arbors"][k] for k in ("barrel", "third", "minute")})
    colours = ["#d1495b", "#edae49", "#00798c", "#30638e", "#6a4c93", "#2a9d8f", "#e76f51", "#8ab17d"]
    W = 260
    panels = []
    allv = {}
    for n in TRAIN + DIAL:
        e = des["gears"][n]
        side = "dial" if n in DIAL else "train"
        lv = e["dial_level"] if n in DIAL else e["level"]
        ls = [lv, lv + 1] if n == "barrel_wheel" else [lv]
        for l in ls:
            allv.setdefault((side, l), []).append((n, arb[ARBOR_OF[n]], tip(e["module"], e["teeth"]), e["module"] * e["teeth"] / 2))
    allv.setdefault(("train", des["escape_wheel_level"]), []).append(("escape_wheel", arb["escape"], inst["escape_wheel"]["radius"], inst["escape_wheel"]["radius"] - 0.2))
    keys = sorted(allv, key=lambda k: (k[0] != "train", k[1]))
    s = W / (2 * R + 2)
    body = []
    for i, key in enumerate(keys):
        ox, oy = (i % 4) * (W + 20) + W / 2 + 10, (i // 4) * (W + 40) + W / 2 + 30
        body.append('<text x="%.1f" y="%.1f" font-size="13" font-family="sans-serif">%s level %d</text>' % (ox - W / 2, oy - W / 2 - 8, key[0], key[1]))
        body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#f4f1ea" stroke="#999"/>' % (ox, oy, R * s))
        if key[0] == "train":
            b = inst["balance"]
            body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#ddd" stroke="#666" stroke-dasharray="3,2"/>' % (ox + b["centre"][0] * s, oy - b["centre"][1] * s, b["radius"] * s))
        for j, (n, c, rt, rp) in enumerate(allv[key]):
            col = colours[(TRAIN + DIAL + ["escape_wheel"]).index(n) % len(colours)]
            body.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s" fill-opacity="0.35" stroke="%s"/>' % (ox + c[0] * s, oy - c[1] * s, rt * s, col, col))
            body.append('<text x="%.1f" y="%.1f" font-size="8" font-family="sans-serif" text-anchor="middle">%s</text>' % (ox + c[0] * s, oy - c[1] * s - rt * s - 2, n.replace("_", " ")))
        for k, p in arb.items():
            body.append('<circle cx="%.1f" cy="%.1f" r="2" fill="black"/>' % (ox + p[0] * s, oy - p[1] * s))
    rows = (len(keys) + 3) // 4
    open(path, "w").write('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" style="background:white">%s</svg>' % (4 * (W + 20) + 20, rows * (W + 40) + 30, "".join(body)))


if __name__ == "__main__":
    if sys.argv[1] == "gen":
        json.dump(gen(int(sys.argv[2])), open(sys.argv[3], "w"), indent=1)
    elif sys.argv[1] == "grade":
        inst = json.load(open(sys.argv[2]))
        try:
            des = json.load(open(sys.argv[3]))
        except Exception:
            des = None
        rep = grade(inst, des) if isinstance(des, dict) else {"valid": False, "violations": ["no readable design"], "score": 0.0}
        if len(sys.argv) > 4 and sys.argv[4] != "-":
            ref = json.load(open(sys.argv[4]))
            rep["score"] = score(rep, ref)
        if len(sys.argv) > 5 and rep.get("valid"):
            svg(inst, des, sys.argv[5])
        print(json.dumps(rep, indent=1))
