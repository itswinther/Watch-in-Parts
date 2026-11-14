"""Reference for the watch task.
    python solution/reference_watch.py OUT_DIR
writes OUT_DIR/stage1 .. OUT_DIR/stage4, each with movement.json and parts/*.step (stage4 also assembly.json).
    python solution/reference_watch.py OUT_DIR --job [--one-part-mobiles]
    python solution/reference_watch.py OUT_DIR --job --keyless [--check]
writes OUT_DIR as one delivery folder (Decisions 2026-11-14 15:44): movement.json (the stage-2 design: 8-hour
barrel, with the 24-hour hand), variant_6h.json (the stage-3 design: same frame, 1/6 barrel turn per hour),
assembly.json (order and paths for movement.json) and parts/*.step, one file per part name for both movements.
In the delivery the going train and the minute wheel are brass wheels on steel pinion arbors, two parts each
(split_wheels, part_materials); --one-part-mobiles keeps them one part each, as in the stage folders.
--keyless: the five-part delivery, with crown winding (Part 5) from workstream A's keyless v2 reference
(main_job_keyless); without it nothing changes.
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
_GEARS = {}                # part name -> (pinion, wheel) solids of a stage build, read by the one-job mode's split_wheels


def cyl(x, y, z0, z1, r, seg=None):
    """True circular cylinder (the old mesh helper took a segment count; it is ignored here)."""
    return GC.cyl(x, y, z0, z1, r)


def minus(a, b):
    """a with b (a solid or a list of tool solids) cut away."""
    return GC.cut(a, *(b if isinstance(b, list) else [b]))

M_A, M_B, M_C, M_D = 0.2, 0.25, 21.6 / 102, 0.2        # modules of the four train layers
M_E, M_F = 0.25, 0.2                                     # motion work
M_DAY = 0.16                                             # day pair: idler pinion 10 -> day wheel 40
DAY_TEETH = (10, 40)
DAY_CD = M_DAY * sum(DAY_TEETH) / 2.0                    # 4.0
Z_DAY = (6.2, 7.2)        # the day pair is 1.0 thick (layer E lowered by 0.2) for a larger drive overlap
FIT = 0.005               # radial clearance of every bore on its shaft
SPOKE = dict(rim=0.4, spokes=5, width=0.45, fillet=0.15)  # crossed-out wheels
# gear layers; B, C and D are only as thick as their drive margin needs (drawn drive overlap >= 0.03)
Z = {"A": (0.1, 0.9), "B": (1.4, 1.85), "C": (2.6, 3.2), "D": (3.8, 4.4), "E": (6.4, 7.2), "F": (7.6, 8.4)}
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
        P = {"barrel": B, "third": I, "centre": C, "fourth": T, "seconds": S, "minute_wheel": Mw, "day_idler": Id, "day": D}
        P["day"] = place_day(P)
        return P
    raise RuntimeError("no placement found")


def place_day(P):
    """The day wheel on a circle of DAY_CD round the day idler, clear of the centre, minute wheel and seconds
    (wheel radius 3.36), as close to the centre axis as those clearances allow."""
    C, Mw, S, Id = P["centre"], P["minute_wheel"], P["seconds"], P["day_idler"]
    best = None
    for k in range(720):
        D = on(Id, DAY_CD, math.radians(k / 2.0))
        if 9.6 <= dist(D, C) <= 12.5 and dist(D, Mw) >= 8.6 and dist(D, S) >= 8.8:
            if best is None or dist(D, C) < dist(best, C):
                best = D
    if best is None:
        raise RuntimeError("no place for the day wheel")
    return (round(best[0], 4), round(best[1], 4))


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


def hand(axis, z0, z1, length, hub_r, bore_r):
    """A hand with a bore of bore_r (its shaft's radius plus FIT): it slides down onto a stepped shaft."""
    x, y = axis
    h = union([cyl(x, y, z0, z1, hub_r), box((x, y - 0.3, z0), (x + length, y + 0.3, z1))])
    return minus(h, cyl(x, y, z0 - 1, z1 + 1, bore_r))


def wheel_at(axis, teeth, module, z, toward, partner=None, hub_r=1.1):
    """gear_at, crossed out to a rim, five spokes and a hub of hub_r."""
    g, phase = gear_at(axis, teeth, module, z, toward, partner)
    pocket = GC.spoke_cutters(axis[0], axis[1], z[0], z[1], hub_r, module * teeth / 2.0 - 1.25 * module - SPOKE["rim"],
                              SPOKE["spokes"], SPOKE["width"], phase, SPOKE["fillet"])
    return minus(g, pocket), phase


# swept radius of each mobile of the largest stage, below the dial (wheels) and with the hands
SWEEP = {"barrel": (9.8, 9.8), "third": (7.75, 7.75), "centre": (9.75, 9.75), "fourth": (9.8, 9.8), "seconds": (1.4, 5.01),
         "minute_wheel": (4.75, 4.75), "hour_wheel": (5.0, 6.01), "day_idler": (2.6, 2.6), "day": (3.36, 3.36)}


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


def frame(P, with_day, job=False):
    """Plate, bridge and dial cut down to skeletons: a boss round every hole and pillar, joined by bars.
    job=True (the one-job delivery, two-body barrel): the arbor rises to BARREL_ARBOR_Z[1], so there is no barrel
    cock; the arbor's upper pivot runs in the bridge, in a boss over the barrel (its square, z BARREL_SQUARE_Z,
    is left free for a ratchet)."""
    C, I, T, S, Mw, Id, D = (P[k] for k in ("centre", "third", "fourth", "seconds", "minute_wheel", "day_idler", "day"))
    (cx, cy), R_PLATE, spots = P["case"]
    lo, hi = PLATE[1] + 0.1, BRIDGE[0] - 0.1
    BAR = 1.0
    pb = [(0.0, 0.0, 1.3)] + [(a[0], a[1], 1.0) for a in (I, T, C, S)] + [(x, y, 0.85) for x, y in spots]
    plate = union([GC.skeleton(PLATE[0], PLATE[1], pb, BAR)[0]] + [cyl(x, y, PLATE[1] - 0.1, BRIDGE[0], 0.75) for x, y in spots])
    bb = [(a[0], a[1], 1.0) for a in (I, T, Mw)] + [(C[0], C[1], 1.4), (S[0], S[1], 1.2)] + [(x, y, 0.85) for x, y in spots] \
        + [(0.0, 0.0, 1.1 if job else 0.8)]   # over the barrel: the barrel cock's post stands on it (stages), or the arbor's pivot runs in it (job)
    db = [(Mw[0], Mw[1], 1.0), (C[0], C[1], 1.8), (S[0], S[1], 1.2)] + [(x, y, 0.85) for x, y in spots]
    if with_day:
        bb += [(Id[0], Id[1], 1.0), (D[0], D[1], 1.0)]
        db += [(Id[0], Id[1], 1.0), (D[0], D[1], 1.2)]
    bridge = union([GC.skeleton(BRIDGE[0], BRIDGE[1], bb, BAR)[0]] + [cyl(x, y, BRIDGE[1] - 0.1, DIAL[0], 0.75) for x, y in spots])
    dial = GC.skeleton(DIAL[0], DIAL[1], db, BAR)[0]
    ph = [cyl(0, 0, -1.1, PLATE[1] + 1, 0.6)] + [cyl(a[0], a[1], lo - 0.8, PLATE[1] + 1, 0.4) for a in (I, T, C, S)]
    bh = [cyl(a[0], a[1], BRIDGE[0] - 1, hi + 0.8, 0.4) for a in (I, T)] + [cyl(C[0], C[1], BRIDGE[0] - 1, BRIDGE[1] + 1, 0.7),
                                                                          cyl(S[0], S[1], BRIDGE[0] - 1, BRIDGE[1] + 1, 0.6)]
    bh += [cyl(Mw[0], Mw[1], BRIDGE[1] - 0.7, BRIDGE[1] + 1, 0.4)]
    if job:
        bh += [cyl(0, 0, BRIDGE[0] - 1, W.BARREL_ARBOR_Z[1] + 0.1, W.BARREL_ARBOR_R + 0.1)]
    dh = [cyl(Mw[0], Mw[1], DIAL[0] - 1, DIAL[0] + 0.45, 0.4), cyl(C[0], C[1], DIAL[0] - 1, DIAL[1] + 1, 1.15), cyl(S[0], S[1], DIAL[0] - 1, DIAL[1] + 1, 0.6)]
    if with_day:
        bh += [cyl(a[0], a[1], BRIDGE[1] - 0.7, BRIDGE[1] + 1, 0.4) for a in (Id, D)]
        dh += [cyl(Id[0], Id[1], DIAL[0] - 1, DIAL[0] + 0.45, 0.4), cyl(D[0], D[1], DIAL[0] - 1, DIAL[1] + 1, 0.6)]
    out = {"main_plate": minus(plate, ph), "bridge": minus(bridge, bh), "dial": minus(dial, dh)}
    if not job:
        out["barrel_cock"] = minus(union([cyl(0, 0, 1.15, 2.45, 1.6), cyl(0, 0, 2.4, BRIDGE[0], 0.6)]), cyl(0, 0, 1.0, 1.7, 0.6))
    return out


def centre_arbor(C, lo, hi, pinion, wheel):
    """Centre arbor, stepped so the cannon (on the 0.6 -> 0.5 step at 6.4) and the minute hand (on the
    0.5 -> 0.35 step at 10.7) slide down onto it."""
    cx, cy = C
    return union([cyl(cx, cy, lo, 6.4, 0.6), cyl(cx, cy, lo - 0.7, lo + 0.01, 0.3),
                  cyl(cx, cy, 6.39, 10.7, 0.5), cyl(cx, cy, 10.69, 11.4, 0.35), pinion, wheel])


def hand_arbor(A, z0, z1, gear_solid):
    """Seconds or day arbor: shaft 0.6 with a 0.8 collar under the plate above (it holds the arbor down),
    top 0.5, and a 0.3 tip for the hand from 9.9 to 10.3."""
    x, y = A
    return union([cyl(x, y, z0, z1, 0.6), cyl(x, y, z1 - 0.4, z1, 0.8), cyl(x, y, z0 - 0.7, z0 + 0.01, 0.3), cyl(x, y, z1 - 0.01, 9.9, 0.5),
                  cyl(x, y, 9.89, 10.3, 0.3), gear_solid])


def build_stage1():
    P = place()
    P["case"] = case_geometry(P)
    B, I, C, T, S, Mw = (P[k] for k in ("barrel", "third", "centre", "fourth", "seconds", "minute_wheel"))
    lo, hi = PLATE[1] + 0.1, BRIDGE[0] - 0.1
    cx, cy = C
    sx, sy = S
    parts, phase = {}, {}
    p1, _ = gear_at(I, 24, M_A, Z["A"], ang(I, B), (96, 0.0))
    w1, ph_w1 = wheel_at(I, 60, M_B, Z["B"], ang(I, C))
    parts["third"] = union([arbor(I, lo, hi), p1, w1])
    p2, _ = wheel_at(C, 30, M_B, Z["B"], ang(C, I), (60, ph_w1), hub_r=1.2)
    w2, ph_w2 = wheel_at(C, 90, M_C, Z["C"], ang(C, T), hub_r=1.2)
    parts["centre"] = centre_arbor(C, lo, hi, p2, w2)
    can, ph_can = gear_at(C, 12, M_E, Z["E"], ang(C, Mw))
    parts["cannon"] = minus(can, cyl(cx, cy, Z["E"][0] - 1, Z["E"][1] + 1, 0.5 + FIT))
    p3, _ = gear_at(T, 12, M_C, Z["C"], ang(T, C), (90, ph_w2))
    w3, ph_w3 = wheel_at(T, 96, M_D, Z["D"], ang(T, S))
    parts["fourth"] = union([arbor(T, lo, hi), p3, w3])
    p4, _ = gear_at(S, 12, M_D, Z["D"], ang(S, T), (96, ph_w3))
    parts["seconds"] = hand_arbor(S, lo, hi, p4)
    _GEARS.update(third=(p1, w1), centre=(p2, w2), fourth=(p3, w3))
    w5, _ = wheel_at(Mw, 36, M_E, Z["E"], ang(Mw, C), (12, ph_can))
    p5, ph_p5 = gear_at(Mw, 12, M_F, Z["F"], ang(Mw, C))
    parts["minute_wheel"] = union([arbor(Mw, BRIDGE[1] + 0.1, DIAL[0] - 0.1, top=0.4), w5, p5])
    _GEARS["minute_wheel"] = (p5, w5)
    w6, phase["hour"] = wheel_at(C, 48, M_F, Z["F"], ang(C, Mw), (12, ph_p5), hub_r=1.6)
    # the tube starts 0.2 above the cannon: moved 0.3 down, the hour wheel rests on the cannon (held)
    parts["hour_wheel"] = minus(union([cyl(cx, cy, 7.4, 9.9, 1.0), cyl(cx, cy, 9.89, 10.3, 0.9), cyl(cx, cy, 8.4, 8.65, 1.6), w6]),
                                cyl(cx, cy, 7.0, 10.6, 0.6))
    parts["hour_hand"] = hand(C, 9.9, 10.2, 6.0, 1.3, 0.9 + FIT)
    parts["minute_hand"] = hand(C, 10.7, 11.0, 9.0, 1.0, 0.35 + FIT)
    parts["seconds_hand"] = hand(S, 9.9, 10.2, 5.0, 0.9, 0.3 + FIT)
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
    gb, ph_gb = gear_at(Id, DAY_TEETH[0], M_DAY, Z_DAY, ang(Id, D))
    parts["day_idler"] = union([arbor(Id, BRIDGE[1] + 0.1, DIAL[0] - 0.1, top=0.4), ga, gb])
    dw, _ = wheel_at(D, DAY_TEETH[1], M_DAY, Z_DAY, ang(D, Id), (DAY_TEETH[0], ph_gb), hub_r=1.2)
    z0, z1 = BRIDGE[1] + 0.1, DIAL[0] - 0.1
    parts["day"] = hand_arbor(D, z0, z1, dw)
    parts["day_hand"] = hand(D, 9.9, 10.2, 3.2, 0.9, 0.3 + FIT)
    parts.update(frame(P, with_day=True))
    doc["mobiles"]["day_idler"] = {"axis": list(Id), "parts": ["day_idler"]}
    doc["mobiles"]["day"] = {"axis": list(D), "parts": ["day", "day_hand"]}
    doc["meshes"] += [{"driver": "hour_wheel", "driver_teeth": 48, "driven": "day_idler", "driven_teeth": 24},
                      {"driver": "day_idler", "driver_teeth": DAY_TEETH[0], "driven": "day", "driven_teeth": DAY_TEETH[1]}]
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
    w1, ph_w1 = wheel_at(I, 54, M_B, Z["B"], ang(I, C))
    parts["third_54"] = union([arbor(I, lo, hi), p1, w1])
    p2, _ = wheel_at(C, 36, M_B, Z["B"], ang(C, I), (54, ph_w1), hub_r=1.2)
    w2, _ = wheel_at(C, 90, M_C, Z["C"], ang(C, T), hub_r=1.2)
    parts["centre_36"] = centre_arbor(C, lo, hi, p2, w2)
    _GEARS.update(third_54=(p1, w1), centre_36=(p2, w2))
    doc["mobiles"]["third"]["parts"] = ["third_54"]
    doc["mobiles"]["centre"]["parts"] = ["centre_36" if n == "centre" else n for n in doc["mobiles"]["centre"]["parts"]]
    for e in doc["meshes"]:
        if e["driver"] == "third" and e["driven"] == "centre":
            e["driver_teeth"], e["driven_teeth"] = 54, 36
    return doc, parts


ORDER = ["main_plate", "barrel", "barrel_cock", "third_54", "centre_36", "fourth", "seconds", "bridge", "cannon",
         "minute_wheel", "hour_wheel", "day", "day_idler", "dial", "hour_hand", "seconds_hand", "day_hand", "minute_hand"]


# the same order for the 8-hour movement, which has the 60/30 third wheel and centre pinion, and no barrel cock
# (the one-job delivery's two-body barrel pivots in the bridge)
ORDER_8H = [{"third_54": "third", "centre_36": "centre"}.get(n, n) for n in ORDER if n != "barrel_cock"]


def build_assembly(folder, order=None, m=None, given=None):
    """Every part comes straight down from above, in `order` (default ORDER).
    m: the movement, already loaded (with its keyless parts attached when they are installed too); given:
    {part: path} taken as they are (the keyless parts' paths from workstream A's fragment)."""
    order = ORDER if order is None else order
    m = W.load_movement(folder) if m is None else m
    allp = m.all_parts(keyless=True)
    if sorted(order) != sorted(allp):
        raise RuntimeError("assembly order does not list every part once: %s" % sorted(set(order) ^ set(allp)))
    lo, hi = m.assembly_box()
    paths = {}
    for n in order:
        if given and n in given:
            paths[n] = given[n]
            continue
        bb = allp[n].bounding_box()
        lift = hi[2] + 0.5 - bb[2]
        k = int(math.ceil(lift / 0.19))
        P = []
        for i in range(k + 1):
            T = np.eye(4)
            T[2, 3] = lift * (1 - i / k)
            P.append(T.tolist())
        paths[n] = P
    return {"order": list(order), "paths": paths}


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


# One-job mode only: the material of each mobile, an ordering code of DS-201 with a bending allowable
# (geometry/watch.py MATERIAL_ALLOWABLE_MPA), and of some parts (part_materials, Decisions 2026-11-14 21:43, item 2).
# As a watchmaker does: pinions are cut on hardened steel arbors, wheels are brass, riveted on the arbor. So the
# going train (third, centre, fourth) and the minute wheel are each split into a steel part (arbor and pinion, with
# a collar the wheel sits on) and a brass wheel (split_wheels); those mobiles are steel with their wheel part in
# brass. One part, one material: the seconds mobile (arbor and pinion, steel), the cannon pinion (steel), the day
# idler (steel: its 24 wheel and 10 pinion are one part), the hour wheel (brass, a wheel on a pipe) and the day
# wheel (brass, a wheel with its arbor in one part). Hands take their mobile's material. The strength check rates
# the going train only (barrel to the seconds mobile); there the third pinion needs steel (in brass its margin is
# -0.12) and the brass wheels pass. The stage folders carry neither field and keep the one-part mobiles (the stage
# grader reads no material).
MATERIALS = {"third": "AD-C100-HT", "centre": "AD-C100-HT", "fourth": "AD-C100-HT", "seconds": "AD-C100-HT",
             "minute_wheel": "AD-C100-HT", "day_idler": "AD-C100-HT", "hour_wheel": "AD-CW614N", "day": "AD-CW614N"}
BRASS = "AD-CW614N"
# the one-job split: part of the stage build -> (steel part name, brass wheel part name, mobile)
SPLIT = {"third": ("third", "third_wheel_60", "third"), "third_54": ("third", "third_wheel_54", "third"),
         "centre": ("centre", "centre_wheel_90", "centre"), "centre_36": ("centre_36", "centre_wheel_90", "centre"),
         "fourth": ("fourth", "fourth_wheel_96", "fourth"), "minute_wheel": ("minute_wheel", "minute_wheel_36", "minute_wheel")}
COLLAR_H, COLLAR_DR = 0.25, 0.25     # the steel collar the wheel sits on: height, and radius over the arbor's


def _wheel_on(axis, wheel, z, r, top):
    """(collar, brass wheel): a steel collar of radius r + COLLAR_DR and height COLLAR_H on an arbor of radius r,
    inside the wheel's layer z (at its bottom, or at its top for a wheel put on before its arbor), and the wheel
    bored to r + FIT with a counterbore of the collar's radius + FIT, FIT clear of the collar's end face too.
    The collar lies inside the wheel's hub, so the steel part and the wheel together are the one-part mobile less
    the FIT clearances round the arbor."""
    x, y = axis
    rc = r + COLLAR_DR
    if top:
        c0, c1 = z[1] - COLLAR_H, z[1]
        counter = cyl(x, y, c0 - FIT, z[1] + 1.0, rc + FIT)
    else:
        c0, c1 = z[0], z[0] + COLLAR_H
        counter = cyl(x, y, z[0] - 1.0, c1 + FIT, rc + FIT)
    return cyl(x, y, c0, c1, rc), minus(wheel, [cyl(x, y, z[0] - 1.0, z[1] + 1.0, r + FIT), counter])


def split_wheels(P):
    """The one-job mode's going train and minute wheel as a steel part and a brass wheel each (SPLIT), built from
    the gear solids the stage builds recorded in _GEARS (run build_stage1 and build_stage3 first). Returns
    {part name: solid}; a part shared by both movements is one solid (third, centre_wheel_90, fourth and its wheel,
    the minute wheel's two parts)."""
    lo, hi = PLATE[1] + 0.1, BRIDGE[0] - 0.1
    I, C, T, Mw = P["third"], P["centre"], P["fourth"], P["minute_wheel"]
    out = {}
    p1, w1 = _GEARS["third"]
    collar, out["third_wheel_60"] = _wheel_on(I, w1, Z["B"], 0.5, top=False)
    out["third"] = union([arbor(I, lo, hi), p1, collar])
    _, w1_54 = _GEARS["third_54"]
    _, out["third_wheel_54"] = _wheel_on(I, w1_54, Z["B"], 0.5, top=False)
    p2, w2 = _GEARS["centre"]
    collar, out["centre_wheel_90"] = _wheel_on(C, w2, Z["C"], 0.6, top=False)
    out["centre"] = centre_arbor(C, lo, hi, p2, collar)
    p2_36, _ = _GEARS["centre_36"]
    out["centre_36"] = centre_arbor(C, lo, hi, p2_36, collar)
    p3, w3 = _GEARS["fourth"]
    collar, out["fourth_wheel_96"] = _wheel_on(T, w3, Z["D"], 0.5, top=False)
    out["fourth"] = union([arbor(T, lo, hi), p3, collar])
    # the minute wheel's pinion is above its wheel: the wheel goes in first and the arbor comes down through it,
    # its collar seating in the wheel's counterbore from above
    p5, w5 = _GEARS["minute_wheel"]
    collar, out["minute_wheel_36"] = _wheel_on(Mw, w5, Z["E"], 0.5, top=True)
    out["minute_wheel"] = union([arbor(Mw, BRIDGE[1] + 0.1, DIAL[0] - 0.1, top=0.4), p5, collar])
    return out


def with_materials(doc, split=False):
    """doc with every mobile's material; split: the mobiles split by split_wheels (doc's part names already
    replaced) also give their brass wheel in part_materials."""
    doc = json.loads(json.dumps(doc))
    wheels = {w for _, w, _ in SPLIT.values()}
    for name, mob in doc["mobiles"].items():
        mob["material"] = MATERIALS[name]
        pm = {pn: BRASS for pn in mob["parts"] if split and pn in wheels}
        if pm:
            mob["part_materials"] = pm
    return doc


REPORT_PARTS = ("P1", "P2", "P3", "P4")      # the parts of the one-job inspection (QA-W100 Parts 1 to 4)


def split_doc(doc):
    """doc with each part of SPLIT replaced by its steel part and its brass wheel (in that order), in its mobile."""
    doc = json.loads(json.dumps(doc))
    for mob in doc["mobiles"].values():
        new = []
        for pn in mob["parts"]:
            new += list(SPLIT[pn][:2]) if pn in SPLIT else [pn]
        mob["parts"] = new
    return doc


def job_order(order):
    """The assembly order with the split parts: a wheel on a pinion arbor (pinion below it) goes in right after its
    arbor; the minute wheel (pinion above it) right before its arbor."""
    out = []
    for n in order:
        if n == "minute_wheel":
            out += ["minute_wheel_36", "minute_wheel"]
        elif n in SPLIT:
            out += list(SPLIT[n][:2])
        else:
            out.append(n)
    return out


def main_job(out, split=True):
    """One delivery folder: the 8-hour movement with its 24-hour hand, the 6-hour variant on the same frame,
    the assembly plan for the 8-hour movement, and one parts/ folder. A part name used by both movements is
    one solid and one file; a part that differs between them has its own name. Every mobile declares its material.
    split (default; --one-part-mobiles turns it off): brass wheels on steel pinion arbors (split_wheels); without
    it the mobiles are one part each, as in the stage folders, and one material each."""
    out = os.path.abspath(out)
    doc1, parts1, P, phase = build_stage1()
    doc2, parts2 = build_stage2(doc1, parts1, P, phase)
    doc3, parts3 = build_stage3(doc2, parts2, P)
    # the two-body barrel's arbor rises to the bridge: the job frame (no barrel cock, a pivot hole in the bridge)
    jf = frame(P, with_day=True, job=True)
    for d, ps in ((doc2, parts2), (doc3, parts3)):
        d["fixed"] = [n for n in d["fixed"] if n != "barrel_cock"]
        ps.pop("barrel_cock", None)
        ps.update(jf)
    order = ORDER_8H
    if split:
        sp = split_wheels(P)
        doc2, doc3 = split_doc(doc2), split_doc(doc3)
        for d, ps in ((doc2, parts2), (doc3, parts3)):
            for n in [n for n in ps if n in SPLIT]:
                del ps[n]
            ps.update({n: sp[n] for mm in d["mobiles"].values() for n in mm["parts"] if n in sp})
        order = job_order(ORDER_8H)
    doc2, doc3 = with_materials(doc2, split), with_materials(doc3, split)
    names = lambda d: list(d["fixed"]) + [p for mm in d["mobiles"].values() for p in mm["parts"]]
    shared = set(names(doc2)) & set(names(doc3))
    for n in shared:
        if parts2[n] is not parts3[n]:
            raise RuntimeError("part %s differs between the two movements but has one name" % n)
    if doc2["fixed"] != doc3["fixed"] or doc2["case_centre"] != doc3["case_centre"]:
        raise RuntimeError("the two movements do not share one frame")
    if os.path.isdir(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "parts"))
    solids = {n: parts2[n] for n in names(doc2)}
    solids.update({n: parts3[n] for n in names(doc3)})
    for n, solid in solids.items():
        GC.export(os.path.join(out, "parts", n + ".step"), solid)
    with open(os.path.join(out, "movement.json"), "w") as f:
        json.dump(doc2, f, indent=1)
    with open(os.path.join(out, "variant_6h.json"), "w") as f:
        json.dump(doc3, f, indent=1)
    with open(os.path.join(out, "assembly.json"), "w") as f:
        json.dump(build_assembly(out, order), f)
    # the designer's statement (FORMAT.md, report.json): truthful, since every part passes (the honesty term,
    # SESSION.md Decisions 17:56). When Part 5 (crown winding) is graded, its claim joins this list.
    with open(os.path.join(out, "report.json"), "w") as f:
        json.dump({"parts": {pid: "pass" for pid in REPORT_PARTS}}, f, indent=1)
    print("job folder", out, "parts", len(solids), "movement", len(names(doc2)), "variant", len(names(doc3)),
          "only in variant", sorted(set(names(doc3)) - set(names(doc2))), "only in movement", sorted(set(names(doc2)) - set(names(doc3))))


# ---------------- the five-part delivery: the job reference plus workstream A's keyless v2 reference ----------------
# A's script, run as it is (B neither copies nor edits it): spikes/keyless/reference_v2.py OUT --ref REF_JOB --deliver
# DELIVERY writes the job reference with the keyless parts in parts/, the `keyless` section and the friction_on split
# (cannon pinion and minute hand on the centre arbor) in movement.json, and A's fixed parts in `fixed` of both
# movements; a part A cannot yet write as a STEP solid is a placeholder file with its solid in DELIVERY_solids/
# (solution/keyless_v1_delivery.py's scheme). --assembly-only DELIVERY replays A's installation fragment (the keyless
# parts after the going train, A's Q3 answer) and writes the merged order and A's paths to assembly_keyless.json.
KEYLESS_V2 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spikes", "keyless",
                          "reference_v2.py")
REPORT_PARTS_KEYLESS = REPORT_PARTS + ("P5",)


def _run_a(args, log):
    """A's script in its own interpreter (subprocess: fork and exec at once, nothing of this process runs there)."""
    import subprocess
    with open(log, "a") as f:
        f.write("$ %s\n" % " ".join(args))
        f.flush()
        p = subprocess.run([sys.executable] + args, stdout=f, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        raise RuntimeError("%s exited %d (log: %s)" % (os.path.basename(args[0]), p.returncode, log))


def _clean_split(doc):
    """Each mobile's part_materials limited to that mobile's parts. A's split copies the centre mobile's entry (the
    brass centre wheel) onto the new cannon mobile, which the format rejects (a part_materials key must be a part of
    its mobile). Returns the names of the mobiles changed."""
    changed = []
    for name, mob in doc["mobiles"].items():
        pm = mob.get("part_materials")
        if pm is None:
            continue
        keep = {k: v for k, v in pm.items() if k in mob["parts"]}
        if keep != pm:
            changed.append(name)
            if keep:
                mob["part_materials"] = keep
            else:
                del mob["part_materials"]
    return changed


def main_job_keyless(out, split=True, check=False):
    """The five-part delivery in OUT: main_job (Parts 1 to 4) in OUT_keyless_work/job, A's keyless v2 reference on it
    (KEYLESS_V2 --deliver), A's assembly fragment merged after the going train into assembly.json (A's order and A's
    paths for the keyless parts; B's straight-down paths for the rest, recomputed for the assembly box with the
    keyless parts in it), and report.json claiming P1 to P5. A placeholder part file (one of A's parts not yet a STEP
    solid) has its solid in OUT_solids/; grade such a delivery with `solution/keyless_v1_delivery.py grade-job`.
    check: also run A's --check (collisions with B's parts, AT-0 on the joined model, the stem in every position)."""
    import keyless_v1_delivery as KD
    out = os.path.abspath(out)
    work = out.rstrip("/") + "_keyless_work"
    sol, wsol = out.rstrip("/") + "_solids", os.path.join(work, "delivery_solids")
    for d in (work, out, sol):
        if os.path.isdir(d):
            shutil.rmtree(d)
    os.makedirs(work)
    log = os.path.join(work, "keyless_v2.log")
    ref, dl, kv2 = os.path.join(work, "job"), os.path.join(work, "delivery"), os.path.join(work, "kv2")
    main_job(ref, split)
    _run_a([KEYLESS_V2, kv2, "--ref", ref] + (["--check"] if check else []) + ["--deliver", dl], log)
    mp = os.path.join(dl, "movement.json")
    with open(mp) as f:
        doc = json.load(f)
    cleaned = _clean_split(doc)
    with open(mp, "w") as f:
        json.dump(doc, f, indent=1)
    _run_a([KEYLESS_V2, kv2, "--ref", ref, "--assembly-only", dl], log)
    with open(os.path.join(work, "assembly_keyless.json")) as f:
        frag = json.load(f)
    if not frag["passed"]:
        raise RuntimeError("A's assembly fragment does not replay cleanly: %s" % frag["failures"])
    given = {n: np.array(v, float).reshape(-1, 4, 4).tolist() for n, v in frag["paths"].items()}
    m = W.load_movement(dl, cache=KD.solids_cache(dl))
    m.attach_keyless()
    plan = build_assembly(dl, frag["order"], m=m, given=given)
    with open(os.path.join(dl, "assembly.json"), "w") as f:
        json.dump(plan, f)
    with open(os.path.join(dl, "report.json"), "w") as f:
        json.dump({"parts": {pid: "pass" for pid in REPORT_PARTS_KEYLESS}}, f, indent=1)
    shutil.move(dl, out)
    placeholders = sorted(f[:-4] for f in os.listdir(wsol)) if os.path.isdir(wsol) else []
    if placeholders:
        shutil.move(wsol, sol)
    with open(os.path.join(work, "step_report.json")) as f:
        steps = json.load(f)
    print("five-part delivery", out, "| parts of the keyless section", len(m.keyless_names), "| order", len(plan["order"]),
          "| part_materials limited to their mobile:", cleaned or "none",
          "| placeholder part files (solids in %s):" % sol, placeholders or "none",
          "| STEP failures:", {n: r.get("why") for n, r in steps.items() if not r.get("step")})
    return placeholders


if __name__ == "__main__":
    flags = ("--job", "--one-part-mobiles", "--keyless", "--check")
    args = [a for a in sys.argv[1:] if a not in flags]
    split = "--one-part-mobiles" not in sys.argv[1:]
    if "--job" in sys.argv[1:] and "--keyless" in sys.argv[1:]:
        main_job_keyless(args[0] if args else "out_job", split, check="--check" in sys.argv[1:])
    elif "--job" in sys.argv[1:]:
        main_job(args[0] if args else "out_job", split=split)
    else:
        main(args[0] if args else "out")
