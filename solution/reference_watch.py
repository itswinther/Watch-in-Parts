"""Reference for the three-stage watch task.
    python solution/reference_watch.py OUT_DIR
writes OUT_DIR/stage1, OUT_DIR/stage2 and OUT_DIR/stage3, each with movement.json and parts/*.stl
(stage3 also assembly.json).

Stage 1 train: barrel 96 -> 24 ("third"), 60 -> 30 (centre, minute hand), 90 -> 12 ("fourth"),
96 -> 12 (seconds). Motion work on the dial side: cannon 12 -> 36 (minute wheel), 12 -> 48 (hour wheel,
a tube round the centre arbor). Stage 2 adds the 24-hour hand: hour wheel 48 -> 24 (day idler),
its 12 -> 48 (day wheel). Stage 3 drops every part in from above in an order the layers allow."""
import json
import math
import os
import random
import shutil
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
from geometry import watch as W
from geometry import watch_gears as G
from geometry.core import union, write_stl, box

M_A, M_B, M_C, M_D = 0.2, 0.25, 21.6 / 102, 0.2        # modules of the four train layers
M_E, M_F = 0.25, 0.2                                     # motion work
M_DAY = 0.12
Z = {"A": (0.1, 0.9), "B": (1.4, 2.2), "C": (2.6, 3.4), "D": (3.8, 4.6), "E": (6.4, 7.2), "F": (7.6, 8.4)}
PLATE, BRIDGE, DIAL = (-1.7, -0.3), (5.0, 6.0), (8.8, 9.6)
R_PLATE, R_PILLAR = 22.9, 22.1
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
    return G.gear(teeth, module, z[0], z[1], phase_deg=phase).translate([axis[0], axis[1], 0]), phase


def arbor(axis, z0, z1, r=0.5, pivot=0.3, plen=0.7):
    x, y = axis
    return union([W.cyl(x, y, z0, z1, r), W.cyl(x, y, z0 - plen, z0 + 0.01, pivot), W.cyl(x, y, z1 - 0.01, z1 + plen, pivot)])


def hand(axis, z0, z1, length, hub_r, hole_r):
    x, y = axis
    h = union([W.cyl(x, y, z0, z1, hub_r), box((x, y - 0.3, z0), (x + length, y + 0.3, z1))])
    return h - W.cyl(x, y, z0 - 1, z1 + 1, hole_r) if hole_r else h


def frame(P, with_day):
    C, I, T, S, Mw, Id, D = (P[k] for k in ("centre", "third", "fourth", "seconds", "minute_wheel", "day_idler", "day"))
    cx, cy = C
    lo, hi = PLATE[1] + 0.1, BRIDGE[0] - 0.1
    base = ang(C, P["barrel"])
    spots = [on(C, R_PILLAR, base + math.pi / 3 + k * 2 * math.pi / 3) for k in range(3)]
    plate = union([W.cyl(cx, cy, PLATE[0], PLATE[1], R_PLATE, 96)] + [W.cyl(x, y, PLATE[1] - 0.1, BRIDGE[0], 0.75) for x, y in spots])
    bridge = union([W.cyl(cx, cy, BRIDGE[0], BRIDGE[1], R_PLATE, 96)] + [W.cyl(x, y, BRIDGE[1] - 0.1, DIAL[0], 0.75) for x, y in spots])
    dial = W.cyl(cx, cy, DIAL[0], DIAL[1], R_PLATE, 96)
    ph = [W.cyl(0, 0, -1.1, PLATE[1] + 1, 0.6)] + [W.cyl(a[0], a[1], lo - 0.8, PLATE[1] + 1, 0.4) for a in (I, T, C, S)]
    bh = [W.cyl(a[0], a[1], BRIDGE[0] - 1, hi + 0.8, 0.4) for a in (I, T)] + [W.cyl(a[0], a[1], BRIDGE[0] - 1, BRIDGE[1] + 1, 0.6) for a in (C, S)]
    bh += [W.cyl(Mw[0], Mw[1], BRIDGE[1] - 0.7, BRIDGE[1] + 1, 0.4)]
    dh = [W.cyl(Mw[0], Mw[1], DIAL[0] - 1, DIAL[0] + 0.7, 0.4), W.cyl(cx, cy, DIAL[0] - 1, DIAL[1] + 1, 1.15), W.cyl(S[0], S[1], DIAL[0] - 1, DIAL[1] + 1, 0.6)]
    if with_day:
        bh += [W.cyl(a[0], a[1], BRIDGE[1] - 0.7, BRIDGE[1] + 1, 0.4) for a in (Id, D)]
        dh += [W.cyl(Id[0], Id[1], DIAL[0] - 1, DIAL[0] + 0.7, 0.4), W.cyl(D[0], D[1], DIAL[0] - 1, DIAL[1] + 1, 0.6)]
    return {"main_plate": plate - union(ph), "bridge": bridge - union(bh), "dial": dial - union(dh),
            "barrel_cock": W.cyl(0, 0, 1.15, 2.45, 3.0) - W.cyl(0, 0, 1.0, 1.7, 0.6)}


def build_stage1():
    P = place()
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
    parts["centre"] = union([W.cyl(cx, cy, lo, hi, 0.8), W.cyl(cx, cy, lo - 0.7, lo + 0.01, 0.3), W.cyl(cx, cy, hi - 0.01, 11.4, 0.5), p2, w2])
    parts["cannon"], ph_can = gear_at(C, 12, M_E, Z["E"], ang(C, Mw))
    p3, _ = gear_at(T, 12, M_C, Z["C"], ang(T, C), (90, ph_w2))
    w3, ph_w3 = gear_at(T, 96, M_D, Z["D"], ang(T, S))
    parts["fourth"] = union([arbor(T, lo, hi), p3, w3])
    p4, _ = gear_at(S, 12, M_D, Z["D"], ang(S, T), (96, ph_w3))
    parts["seconds"] = union([W.cyl(sx, sy, lo, hi, 0.8), W.cyl(sx, sy, lo - 0.7, lo + 0.01, 0.3), W.cyl(sx, sy, hi - 0.01, 10.3, 0.5), p4])
    w5, _ = gear_at(Mw, 36, M_E, Z["E"], ang(Mw, C), (12, ph_can))
    p5, ph_p5 = gear_at(Mw, 12, M_F, Z["F"], ang(Mw, C))
    parts["minute_wheel"] = union([arbor(Mw, BRIDGE[1] + 0.1, DIAL[0] - 0.1), w5, p5])
    w6, phase["hour"] = gear_at(C, 48, M_F, Z["F"], ang(C, Mw), (12, ph_p5))
    parts["hour_wheel"] = union([W.cyl(cx, cy, 7.4, 10.3, 1.0), W.cyl(cx, cy, 8.4, 8.65, 1.6), w6]) - W.cyl(cx, cy, 7.0, 10.6, 0.7)
    parts["hour_hand"] = hand(C, 9.9, 10.2, 6.0, 1.3, 0.85)
    parts["minute_hand"] = hand(C, 10.7, 11.0, 9.0, 1.0, 0.0)
    parts["seconds_hand"] = hand(S, 9.9, 10.2, 5.0, 0.9, 0.0)
    parts.update(frame(P, with_day=False))
    doc = {
        "case_centre": [cx, cy],
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
    parts["day_idler"] = union([arbor(Id, BRIDGE[1] + 0.1, DIAL[0] - 0.1), ga, gb])
    dw, _ = gear_at(D, 48, M_DAY, Z["E"], ang(D, Id), (12, ph_gb))
    dx, dy = D
    z0, z1 = BRIDGE[1] + 0.1, DIAL[0] - 0.1
    parts["day"] = union([W.cyl(dx, dy, z0, z1, 0.8), W.cyl(dx, dy, z0 - 0.7, z0 + 0.01, 0.3), W.cyl(dx, dy, z1 - 0.01, 10.3, 0.5), dw])
    parts["day_hand"] = hand(D, 9.9, 10.2, 3.2, 0.9, 0.0)
    parts.update(frame(P, with_day=True))
    doc["mobiles"]["day_idler"] = {"axis": list(Id), "parts": ["day_idler"]}
    doc["mobiles"]["day"] = {"axis": list(D), "parts": ["day", "day_hand"]}
    doc["meshes"] += [{"driver": "hour_wheel", "driver_teeth": 48, "driven": "day_idler", "driven_teeth": 24},
                      {"driver": "day_idler", "driver_teeth": 12, "driven": "day", "driven_teeth": 48}]
    doc["hands"]["day"] = {"mobile": "day", "part": "day_hand"}
    return doc, parts


ORDER = ["main_plate", "barrel", "barrel_cock", "third", "centre", "fourth", "seconds", "bridge", "cannon",
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
        write_stl(os.path.join(folder, "parts", n + ".stl"), parts[n])
    with open(os.path.join(folder, "movement.json"), "w") as f:
        json.dump(doc, f, indent=1)


def main(out):
    doc1, parts1, P, phase = build_stage1()
    write(os.path.join(out, "stage1"), doc1, parts1)
    doc2, parts2 = build_stage2(doc1, parts1, P, phase)
    write(os.path.join(out, "stage2"), doc2, parts2)
    s3 = os.path.join(out, "stage3")
    if os.path.isdir(s3):
        shutil.rmtree(s3)
    shutil.copytree(os.path.join(out, "stage2"), s3)
    with open(os.path.join(s3, "assembly.json"), "w") as f:
        json.dump(build_assembly(s3), f)
    print("stage1 parts", len(parts1), "stage2 parts", len(parts2), "axes", {k: [round(v, 2) for v in a] for k, a in P.items()})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
