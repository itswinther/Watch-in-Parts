"""Reference for the four-stage watch task.
    python solution/reference_watch.py OUT_DIR
writes OUT_DIR/stage1 .. OUT_DIR/stage4, each with movement.json and parts/*.step (stage4 also assembly.json).
Parts are built on the CAD kernel (geometry/watch_gears_cad.py, CadQuery/OpenCASCADE) and written as STEP.
Like an agent, each stage copies the part files it keeps from the stage before and writes only new ones.

Stage 1 train: barrel 96 -> 24 ("third"), 60 -> 30 (centre, minute hand), 90 -> 12 ("fourth"),
96 -> 12 (seconds). Motion work on the dial side: cannon 12 -> 36 (minute wheel), 12 -> 48 (hour wheel,
a tube round the centre arbor). Stage 2 adds the 24-hour hand: hour wheel 48 -> 24 (day idler),
its 12 -> 48 (day wheel). Stage 3 (barrel at 1/6 turn per hour) swaps the third wheel and the centre pinion
from 60/30 to 54/36. Stage 4 drops every part in from above in an order the layers allow.
The case centre and plate radius are the smallest disc round everything that turns (case_geometry)."""
import json
import math
import os
import random
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
from geometry import watch as W
from geometry import watch_gears_cad as GC

union, box = GC.union, GC.box
_FILES = {}                # id(solid) -> the STEP file it was first written to


def cyl(x, y, z0, z1, r, seg=None):
    """True circular cylinder (the old mesh helper took a segment count; it is ignored here)."""
    return GC.cyl(x, y, z0, z1, r)


def minus(a, b):
    """a with b (a solid or a list of tool solids) cut away."""
    return GC.cut(a, *(b if isinstance(b, list) else [b]))

M_A, M_B, M_C, M_D = 0.2, 0.25, 21.6 / 102, 0.2        # modules of the four train layers
M_E, M_F = 0.25, 0.2                                     # motion work
M_DAY = 0.12
Z = {"A": (0.1, 0.9), "B": (1.4, 2.2), "C": (2.6, 3.4), "D": (3.8, 4.6), "E": (6.4, 7.2), "F": (7.6, 8.4)}
PLATE, BRIDGE, DIAL = (-1.7, -0.3), (5.0, 6.0), (8.8, 9.6)
PLATE_MARGIN = 0.1        # plate rim beyond the farthest swept wheel or hand
PILLAR_R, PILLAR_GAP = 0.75, 0.15
dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
on = lambda c, r, a: (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
ang = lambda p, q: math.atan2(q[1] - p[1], q[0] - p[0])


def place(seed=1):
    """Axis positions that keep every wheel clear of every other arbor."""
    rnd = random.Random(seed)
    B, I = (0.0, 0.0), (12.0, 0.0)
    for _ in range(400000):
        C = on(I, 11.25, rnd.uniform(0, 2 * math.pi))
        if not 10.8 <= dist(B, C) <= 11.3:
            continue
        T = on(C, 10.8, rnd.uniform(0, 2 * math.pi))
        if dist(I, T) < 10.6 or dist(B, T) < 10.6:
            continue
        S = on(T, 10.8, rnd.uniform(0, 2 * math.pi))
        if not 11.8 <= dist(C, S) <= 16 or dist(B, S) < 10.9 or dist(I, S) < 8.9:
            continue
        Mw = on(C, 6.0, rnd.uniform(0, 2 * math.pi))
        if dist(Mw, S) < 6.0:
            continue
        Id = on(C, 7.2, rnd.uniform(0, 2 * math.pi))                      # stage 2: day idler
        if dist(Id, Mw) < 6.0 or dist(Id, S) < 3.6:
            continue
        D = on(Id, 3.6, rnd.uniform(0, 2 * math.pi))                      # stage 2: day wheel
        if dist(D, C) < 9.6 or dist(D, Mw) < 8.2 or dist(D, S) < 8.8 or dist(D, C) > 12.5:
            continue
        return {"barrel": B, "third": I, "centre": C, "fourth": T, "seconds": S, "minute_wheel": Mw, "day_idler": Id, "day": D}
    raise RuntimeError("no placement found")


def gear_at(axis, teeth, module, z, toward, partner=None):
    """A gear on `axis` phased to mesh with a partner lying in direction `toward` (radians).
    partner = (teeth, phase in degrees) of that partner, or None to put one of our teeth on the line.
    Returns (solid, phase)."""
    line = math.degrees(toward)
    if partner is None:
        phase = line
    else:
        pt, pang = partner
        delta = ((line + 180.0) - pang) % (360.0 / pt)
        phase = line + delta * pt / teeth + 180.0 / teeth
    return GC.gear(teeth, module, z[0], z[1], phase_deg=phase, x=axis[0], y=axis[1]), phase


def arbor(axis, z0, z1, r=0.5, pivot=0.3, plen=0.7, top=None):
    x, y = axis
    top = plen if top is None else top
    return union([cyl(x, y, z0, z1, r), cyl(x, y, z0 - plen, z0 + 0.01, pivot), cyl(x, y, z1 - 0.01, z1 + top, pivot)])


def hand(axis, z0, z1, length, hub_r, hole_r):
    x, y = axis
    h = union([cyl(x, y, z0, z1, hub_r), box((x, y - 0.3, z0), (x + length, y + 0.3, z1))])
    return minus(h, cyl(x, y, z0 - 1, z1 + 1, hole_r)) if hole_r else h


# swept radius of each mobile of the largest stage, below the dial (wheels) and with the hands
SWEEP = {"barrel": (9.8, 9.8), "third": (7.75, 7.75), "centre": (9.75, 9.75), "fourth": (9.8, 9.8), "seconds": (1.4, 5.01),
         "minute_wheel": (4.75, 4.75), "hour_wheel": (5.0, 6.01), "day_idler": (2.6, 2.6), "day": (3.0, 3.22)}


def case_geometry(P):
    """Case centre and plate radius: the smallest disc round every swept wheel and hand of the largest stage
    (plus PLATE_MARGIN), and three pillar spots inside it that clear every swept wheel."""
    from scipy.optimize import minimize
    P = dict(P, hour_wheel=P["centre"])
    reach = lambda c: max(dist(c, P[k]) + r[1] for k, r in SWEEP.items())
    best = min((minimize(lambda v: reach(v), x0, method="Nelder-Mead", options={"xatol": 1e-6, "fatol": 1e-7}) for x0 in
                [P["centre"], (0.0, -8.0), (3.0, -10.0)]), key=lambda r: r.fun)
    cc = (round(float(best.x[0]), 4), round(float(best.x[1]), 4))
    rp = round(reach(cc) + PLATE_MARGIN, 3)
    ok = lambda p: all(dist(p, P[k]) >= r[0] + PILLAR_R + PILLAR_GAP for k, r in SWEEP.items()) \
        and dist(p, cc) <= rp - PILLAR_R - 0.1
    cands = []
    for a in range(0, 360, 3):
        for rr in np.arange(rp - PILLAR_R - 0.1, rp - 8, -0.1):
            if ok(on(cc, rr, math.radians(a))):
                cands.append(on(cc, rr, math.radians(a)))
                break
    best3, score = None, -1
    for i in range(len(cands)):
        for j in range(i + 1, len(cands)):
            for k in range(j + 1, len(cands)):
                s = min(dist(cands[i], cands[j]), dist(cands[j], cands[k]), dist(cands[i], cands[k]))
                if s > score:
                    best3, score = (cands[i], cands[j], cands[k]), s
    return cc, rp, tuple((float(x), float(y)) for x, y in best3)


def frame(P, with_day):
    C, I, T, S, Mw, Id, D = (P[k] for k in ("centre", "third", "fourth", "seconds", "minute_wheel", "day_idler", "day"))
    (cx, cy), R_PLATE, spots = P["case"]
    lo, hi = PLATE[1] + 0.1, BRIDGE[0] - 0.1
    plate = union([cyl(cx, cy, PLATE[0], PLATE[1], R_PLATE, 96)] + [cyl(x, y, PLATE[1] - 0.1, BRIDGE[0], 0.75) for x, y in spots])
    bridge = union([cyl(cx, cy, BRIDGE[0], BRIDGE[1], R_PLATE, 96)] + [cyl(x, y, BRIDGE[1] - 0.1, DIAL[0], 0.75) for x, y in spots])
    dial = cyl(cx, cy, DIAL[0], DIAL[1], R_PLATE, 96)
    ph = [cyl(0, 0, -1.1, PLATE[1] + 1, 0.6)] + [cyl(a[0], a[1], lo - 0.8, PLATE[1] + 1, 0.4) for a in (I, T, C, S)]
    bh = [cyl(a[0], a[1], BRIDGE[0] - 1, hi + 0.8, 0.4) for a in (I, T)] + [cyl(a[0], a[1], BRIDGE[0] - 1, BRIDGE[1] + 1, 0.6) for a in (C, S)]
    bh += [cyl(Mw[0], Mw[1], BRIDGE[1] - 0.7, BRIDGE[1] + 1, 0.4)]
    dh = [cyl(Mw[0], Mw[1], DIAL[0] - 1, DIAL[0] + 0.45, 0.4), cyl(C[0], C[1], DIAL[0] - 1, DIAL[1] + 1, 1.15), cyl(S[0], S[1], DIAL[0] - 1, DIAL[1] + 1, 0.6)]
    if with_day:
        bh += [cyl(a[0], a[1], BRIDGE[1] - 0.7, BRIDGE[1] + 1, 0.4) for a in (Id, D)]
        dh += [cyl(Id[0], Id[1], DIAL[0] - 1, DIAL[0] + 0.45, 0.4), cyl(D[0], D[1], DIAL[0] - 1, DIAL[1] + 1, 0.6)]
    return {"main_plate": minus(plate, ph), "bridge": minus(bridge, bh), "dial": minus(dial, dh),
            "barrel_cock": minus(cyl(0, 0, 1.15, 2.45, 3.0), cyl(0, 0, 1.0, 1.7, 0.6))}


def build_stage1():
    P = place()
    P["case"] = case_geometry(P)
    B, I, C, T, S, Mw = (P[k] for k in ("barrel", "third", "centre", "fourth", "seconds", "minute_wheel"))
    lo, hi = PLATE[1] + 0.1, BRIDGE[0] - 0.1
    cx, cy = C
    sx, sy = S
    parts, phase = {}, {}
    p1, _ = gear_at(I, 24, M_A, Z["A"], ang(I, B), (96, 0.0))
    w1, ph_w1 = gear_at(I, 60, M_B, Z["B"], ang(I, C))
    parts["third"] = union([arbor(I, lo, hi), p1, w1])
    p2, _ = gear_at(C, 30, M_B, Z["B"], ang(C, I), (60, ph_w1))
    w2, ph_w2 = gear_at(C, 90, M_C, Z["C"], ang(C, T))
    parts["centre"] = union([cyl(cx, cy, lo, hi, 0.8), cyl(cx, cy, lo - 0.7, lo + 0.01, 0.3), cyl(cx, cy, hi - 0.01, 11.4, 0.5), p2, w2])
    parts["cannon"], ph_can = gear_at(C, 12, M_E, Z["E"], ang(C, Mw))
    p3, _ = gear_at(T, 12, M_C, Z["C"], ang(T, C), (90, ph_w2))
    w3, ph_w3 = gear_at(T, 96, M_D, Z["D"], ang(T, S))
    parts["fourth"] = union([arbor(T, lo, hi), p3, w3])
    p4, _ = gear_at(S, 12, M_D, Z["D"], ang(S, T), (96, ph_w3))
    parts["seconds"] = union([cyl(sx, sy, lo, hi, 0.8), cyl(sx, sy, lo - 0.7, lo + 0.01, 0.3), cyl(sx, sy, hi - 0.01, 10.3, 0.5), p4])
    w5, _ = gear_at(Mw, 36, M_E, Z["E"], ang(Mw, C), (12, ph_can))
    p5, ph_p5 = gear_at(Mw, 12, M_F, Z["F"], ang(Mw, C))
    parts["minute_wheel"] = union([arbor(Mw, BRIDGE[1] + 0.1, DIAL[0] - 0.1, top=0.4), w5, p5])
    w6, phase["hour"] = gear_at(C, 48, M_F, Z["F"], ang(C, Mw), (12, ph_p5))
    parts["hour_wheel"] = minus(union([cyl(cx, cy, 7.4, 10.3, 1.0), cyl(cx, cy, 8.4, 8.65, 1.6), w6]), cyl(cx, cy, 7.0, 10.6, 0.7))
    parts["hour_hand"] = hand(C, 9.9, 10.2, 6.0, 1.3, 0.85)
    parts["minute_hand"] = hand(C, 10.7, 11.0, 9.0, 1.0, 0.0)
    parts["seconds_hand"] = hand(S, 9.9, 10.2, 5.0, 0.9, 0.0)
    parts.update(frame(P, with_day=False))
    doc = {
        "case_centre": list(P["case"][0]),
        "fixed": ["main_plate", "bridge", "dial", "barrel_cock"],
        "mobiles": {
            "third": {"axis": list(I), "parts": ["third"]},
            "centre": {"axis": list(C), "parts": ["centre", "cannon", "minute_hand"]},
            "fourth": {"axis": list(T), "parts": ["fourth"]},
            "seconds": {"axis": list(S), "parts": ["seconds", "seconds_hand"]},
            "minute_wheel": {"axis": list(Mw), "parts": ["minute_wheel"]},
            "hour_wheel": {"axis": list(C), "parts": ["hour_wheel", "hour_hand"]},
        },
        "meshes": [
            {"driver": "barrel", "driver_teeth": 96, "driven": "third", "driven_teeth": 24},
            {"driver": "third", "driver_teeth": 60, "driven": "centre", "driven_teeth": 30},
            {"driver": "centre", "driver_teeth": 90, "driven": "fourth", "driven_teeth": 12},
            {"driver": "fourth", "driver_teeth": 96, "driven": "seconds", "driven_teeth": 12},
            {"driver": "centre", "driver_teeth": 12, "driven": "minute_wheel", "driven_teeth": 36},
            {"driver": "minute_wheel", "driver_teeth": 12, "driven": "hour_wheel", "driven_teeth": 48},
        ],
        "hands": {"hour": {"mobile": "hour_wheel", "part": "hour_hand"},
                  "minute": {"mobile": "centre", "part": "minute_hand"},
                  "seconds": {"mobile": "seconds", "part": "seconds_hand"}},
    }
    return doc, parts, P, phase


def build_stage2(doc, parts, P, phase):
    """Add the 24-hour hand. Every stage-1 mobile part is untouched; bridge and dial get new holes."""
    doc = json.loads(json.dumps(doc))
    parts = dict(parts)
    C, Id, D = P["centre"], P["day_idler"], P["day"]
    ga, _ = gear_at(Id, 24, M_F, Z["F"], ang(Id, C), (48, phase["hour"]))
    gb, ph_gb = gear_at(Id, 12, M_DAY, Z["E"], ang(Id, D))
    parts["day_idler"] = union([arbor(Id, BRIDGE[1] + 0.1, DIAL[0] - 0.1, top=0.4), ga, gb])
    dw, _ = gear_at(D, 48, M_DAY, Z["E"], ang(D, Id), (12, ph_gb))
    dx, dy = D
    z0, z1 = BRIDGE[1] + 0.1, DIAL[0] - 0.1
    parts["day"] = union([cyl(dx, dy, z0, z1, 0.8), cyl(dx, dy, z0 - 0.7, z0 + 0.01, 0.3), cyl(dx, dy, z1 - 0.01, 10.3, 0.5), dw])
    parts["day_hand"] = hand(D, 9.9, 10.2, 3.2, 0.9, 0.0)
    parts.update(frame(P, with_day=True))
    doc["mobiles"]["day_idler"] = {"axis": list(Id), "parts": ["day_idler"]}
    doc["mobiles"]["day"] = {"axis": list(D), "parts": ["day", "day_hand"]}
    doc["meshes"] += [{"driver": "hour_wheel", "driver_teeth": 48, "driven": "day_idler", "driven_teeth": 24},
                      {"driver": "day_idler", "driver_teeth": 12, "driven": "day", "driven_teeth": 48}]
    doc["hands"]["day"] = {"mobile": "day", "part": "day_hand"}
    return doc, parts


def build_stage3(doc, parts, P):
    """Change request: the barrel turns once every 6 hours instead of 8. The third wheel and the centre pinion
    go from 60/30 to 54/36 (same module, same centre distance 11.25); every other part file is kept."""
    doc = json.loads(json.dumps(doc))
    parts = dict(parts)
    B, I, C, T = P["barrel"], P["third"], P["centre"], P["fourth"]
    lo, hi = PLATE[1] + 0.1, BRIDGE[0] - 0.1
    cx, cy = C
    p1, _ = gear_at(I, 24, M_A, Z["A"], ang(I, B), (96, 0.0))
    w1, ph_w1 = gear_at(I, 54, M_B, Z["B"], ang(I, C))
    parts["third_54"] = union([arbor(I, lo, hi), p1, w1])
    p2, _ = gear_at(C, 36, M_B, Z["B"], ang(C, I), (54, ph_w1))
    w2, _ = gear_at(C, 90, M_C, Z["C"], ang(C, T))
    parts["centre_36"] = union([cyl(cx, cy, lo, hi, 0.8), cyl(cx, cy, lo - 0.7, lo + 0.01, 0.3), cyl(cx, cy, hi - 0.01, 11.4, 0.5), p2, w2])
    doc["mobiles"]["third"]["parts"] = ["third_54"]
    doc["mobiles"]["centre"]["parts"] = ["centre_36" if n == "centre" else n for n in doc["mobiles"]["centre"]["parts"]]
    for e in doc["meshes"]:
        if e["driver"] == "third" and e["driven"] == "centre":
            e["driver_teeth"], e["driven_teeth"] = 54, 36
    return doc, parts


ORDER = ["main_plate", "barrel", "barrel_cock", "third_54", "centre_36", "fourth", "seconds", "bridge", "cannon",
         "minute_wheel", "hour_wheel", "day", "day_idler", "dial", "hour_hand", "seconds_hand", "day_hand", "minute_hand"]


def build_assembly(folder):
    """Every part comes straight down from above, in ORDER."""
    m = W.load_movement(folder)
    allp = m.all_parts()
    lo, hi = m.assembly_box()
    paths = {}
    for n in ORDER:
        bb = allp[n][0].bounding_box()
        lift = hi[2] + 0.5 - bb[2]
        k = int(math.ceil(lift / 0.19))
        P = []
        for i in range(k + 1):
            T = np.eye(4)
            T[2, 3] = lift * (1 - i / k)
            P.append(T.tolist())
        paths[n] = P
    return {"order": ORDER, "paths": paths}


def write(folder, doc, parts):
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    os.makedirs(os.path.join(folder, "parts"))
    names = list(doc["fixed"]) + [p for mm in doc["mobiles"].values() for p in mm["parts"]]
    for n in names:
        dst = os.path.join(folder, "parts", n + ".step")
        src = _FILES.get(id(parts[n]))
        if src and os.path.basename(src) == n + ".step" and os.path.isfile(src):
            shutil.copyfile(src, dst)          # kept part: the same file, byte for byte
        else:
            GC.export(dst, parts[n])
            _FILES[id(parts[n])] = dst
    with open(os.path.join(folder, "movement.json"), "w") as f:
        json.dump(doc, f, indent=1)


def main(out):
    doc1, parts1, P, phase = build_stage1()
    write(os.path.join(out, "stage1"), doc1, parts1)
    doc2, parts2 = build_stage2(doc1, parts1, P, phase)
    write(os.path.join(out, "stage2"), doc2, parts2)
    doc3, parts3 = build_stage3(doc2, parts2, P)
    write(os.path.join(out, "stage3"), doc3, parts3)
    s4 = os.path.join(out, "stage4")
    if os.path.isdir(s4):
        shutil.rmtree(s4)
    shutil.copytree(os.path.join(out, "stage3"), s4)
    with open(os.path.join(s4, "assembly.json"), "w") as f:
        json.dump(build_assembly(s4), f)
    print("stage1 parts", len(parts1), "stage2 parts", len(parts2), "axes", {k: [round(v, 2) for v in a] for k, a in P.items() if k != "case"}, "case", P["case"])


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
