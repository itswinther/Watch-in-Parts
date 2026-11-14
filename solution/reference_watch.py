"""Reference movement for the mechanical watch task.
    python solution/reference_watch.py OUT_DIR     writes OUT_DIR/movement.json and OUT_DIR/parts/*.stl

Train: barrel 96 -> 24 (mobile "third"), its wheel 60 -> 30 (centre, minute hand), centre wheel 90 -> 12
(mobile "fourth"), its wheel 96 -> 12 (seconds). Motion work on the dial side: cannon 12 -> 36
(minute wheel), its pinion 12 -> 48 (hour wheel, a tube round the centre arbor)."""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
from geometry import watch as W
from geometry import watch_gears as G
from geometry.core import union, write_stl, box

M_A, M_B, M_C, M_D = 0.2, 0.25, 21.6 / 102, 0.2        # modules of the four train layers
M_E, M_F = 0.25, 0.2                                     # motion work
Z = {"A": (0.1, 0.9), "B": (1.4, 2.2), "C": (2.6, 3.4), "D": (3.8, 4.6), "E": (6.4, 7.2), "F": (7.6, 8.4)}
PLATE = (-1.7, -0.3)
BRIDGE = (5.0, 6.0)
DIAL = (8.8, 9.6)
R_PLATE = 22.9


def place(seed=1):
    """Axis positions that keep every wheel clear of every other arbor."""
    rnd = random.Random(seed)
    d = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
    on = lambda c, r, a: (c[0] + r * math.cos(a), c[1] + r * math.sin(a))
    B, I = (0.0, 0.0), (12.0, 0.0)
    for _ in range(200000):
        C = on(I, 11.25, rnd.uniform(0, 2 * math.pi))
        if not 10.8 <= d(B, C) <= 11.3:
            continue
        T = on(C, 10.8, rnd.uniform(0, 2 * math.pi))
        if d(I, T) < 10.6 or d(B, T) < 10.6:
            continue
        S = on(T, 10.8, rnd.uniform(0, 2 * math.pi))
        if not 11.8 <= d(C, S) <= 16 or d(B, S) < 10.9 or d(I, S) < 8.9:
            continue
        Mw = on(C, 6.0, rnd.uniform(0, 2 * math.pi))
        if d(Mw, S) < 6.0:
            continue
        return {"barrel": B, "third": I, "centre": C, "fourth": T, "seconds": S, "minute_wheel": Mw}
    raise RuntimeError("no placement found")


def gear_at(axis, teeth, module, z, toward, partner_phase=None):
    """A gear on `axis` whose teeth are phased to mesh with a partner in direction `toward` (radians).
    partner_phase = (teeth, tooth-centre angle in degrees) of the partner, or None to put a tooth on the line."""
    line = math.degrees(toward)
    if partner_phase is None:
        phase = line
    else:
        pt, pang = partner_phase
        pitch_p = 360.0 / pt
        delta = ((line + 180.0) - pang) % pitch_p               # partner's tooth is this far before the line of centres
        phase = line - delta * pt / teeth + 180.0 / teeth       # so our gap is centred the matching amount after it
    return G.gear(teeth, module, z[0], z[1], phase_deg=phase).translate([axis[0], axis[1], 0]), phase


def ang(p, q):
    return math.atan2(q[1] - p[1], q[0] - p[0])


def arbor(axis, z0, z1, r=0.5, pivot=0.3, plen=0.7):
    x, y = axis
    return union([W.cyl(x, y, z0, z1, r), W.cyl(x, y, z0 - plen, z0 + 0.01, pivot), W.cyl(x, y, z1 - 0.01, z1 + plen, pivot)])


def build():
    P = place()
    B, I, C, T, S, Mw = (P[k] for k in ("barrel", "third", "centre", "fourth", "seconds", "minute_wheel"))
    lo, hi = PLATE[1] + 0.1, BRIDGE[0] - 0.1                      # arbor bodies between the plates
    parts, fixed_cut = {}, []

    # third: pinion 24 on the barrel, wheel 60
    p1, _ = gear_at(I, 24, M_A, Z["A"], ang(I, B), (96, 0.0))
    w1, ph_w1 = gear_at(I, 60, M_B, Z["B"], ang(I, C))
    parts["third"] = union([arbor(I, lo, hi), p1, w1])
    # centre: pinion 30, wheel 90, long arbor to the minute hand, cannon pinion 12
    p2, _ = gear_at(C, 30, M_B, Z["B"], ang(C, I), (60, ph_w1))
    w2, ph_w2 = gear_at(C, 90, M_C, Z["C"], ang(C, T))
    can, ph_can = gear_at(C, 12, M_E, Z["E"], ang(C, Mw))
    cx, cy = C
    centre_arbor = union([W.cyl(cx, cy, lo, hi, 0.8), W.cyl(cx, cy, lo - 0.7, lo + 0.01, 0.3), W.cyl(cx, cy, hi - 0.01, 11.4, 0.5)])
    parts["centre"] = union([centre_arbor, p2, w2, can])
    # fourth: pinion 12, wheel 96
    p3, _ = gear_at(T, 12, M_C, Z["C"], ang(T, C), (90, ph_w2))
    w3, ph_w3 = gear_at(T, 96, M_D, Z["D"], ang(T, S))
    parts["fourth"] = union([arbor(T, lo, hi), p3, w3])
    # seconds: pinion 12, arbor up through bridge and dial
    p4, _ = gear_at(S, 12, M_D, Z["D"], ang(S, T), (96, ph_w3))
    sx, sy = S
    parts["seconds"] = union([W.cyl(sx, sy, lo, hi, 0.8), W.cyl(sx, sy, lo - 0.7, lo + 0.01, 0.3), W.cyl(sx, sy, hi - 0.01, 10.3, 0.5), p4])
    # minute wheel: wheel 36 on the cannon pinion, pinion 12
    w5, _ = gear_at(Mw, 36, M_E, Z["E"], ang(Mw, C), (12, ph_can))
    p5, ph_p5 = gear_at(Mw, 12, M_F, Z["F"], ang(Mw, C))
    parts["minute_wheel"] = union([arbor(Mw, BRIDGE[1] + 0.1, DIAL[0] - 0.1), w5, p5])
    # hour wheel: a tube round the centre arbor
    w6, _ = gear_at(C, 48, M_F, Z["F"], ang(C, Mw), (12, ph_p5))
    tube = union([W.cyl(cx, cy, 7.4, 10.3, 1.0), W.cyl(cx, cy, 8.4, 8.65, 1.6), w6]) - W.cyl(cx, cy, 7.0, 10.6, 0.7)
    parts["hour_wheel"] = tube

    # hands
    def hand(axis, z0, z1, length, hub_r, hole_r):
        x, y = axis
        h = union([W.cyl(x, y, z0, z1, hub_r), box((x, y - 0.3, z0), (x + length, y + 0.3, z1))])
        return h - W.cyl(x, y, z0 - 1, z1 + 1, hole_r) if hole_r else h
    parts["hour_hand"] = hand(C, 9.9, 10.2, 6.0, 1.3, 0.85)
    parts["minute_hand"] = hand(C, 10.7, 11.0, 9.0, 1.0, 0.0)
    parts["seconds_hand"] = hand(S, 9.9, 10.2, 5.0, 0.9, 0.0)

    # frame: main plate, bridge, dial plate, pillars, barrel cock on a post
    plate = W.cyl(cx, cy, PLATE[0], PLATE[1], R_PLATE, 96)
    bridge = W.cyl(cx, cy, BRIDGE[0], BRIDGE[1], R_PLATE, 96)
    dial = W.cyl(cx, cy, DIAL[0], DIAL[1], R_PLATE, 96)
    pillars = []
    base = ang(C, B)
    for k in range(3):
        a = base + math.pi / 3 + k * 2 * math.pi / 3
        pillars.append(W.cyl(cx + 22.1 * math.cos(a), cy + 22.1 * math.sin(a), PLATE[0], DIAL[1], 0.75))
    frame = union([plate, bridge, dial] + pillars)
    holes = [W.cyl(0, 0, -1.1, PLATE[1] + 1, 0.6)]                                    # barrel, bottom
    for ax in (I, T):
        holes += [W.cyl(ax[0], ax[1], lo - 0.8, PLATE[1] + 1, 0.4), W.cyl(ax[0], ax[1], BRIDGE[0] - 1, hi + 0.8, 0.4)]
    for ax in (C, S):
        holes += [W.cyl(ax[0], ax[1], lo - 0.8, PLATE[1] + 1, 0.4), W.cyl(ax[0], ax[1], BRIDGE[0] - 1, BRIDGE[1] + 1, 0.6)]
    holes += [W.cyl(Mw[0], Mw[1], BRIDGE[1] - 0.7, BRIDGE[1] + 1, 0.4), W.cyl(Mw[0], Mw[1], DIAL[0] - 1, DIAL[0] + 0.7, 0.4)]
    holes += [W.cyl(cx, cy, DIAL[0] - 1, DIAL[1] + 1, 1.15), W.cyl(sx, sy, DIAL[0] - 1, DIAL[1] + 1, 0.6)]
    parts["frame"] = frame - union(holes)
    parts["barrel_cock"] = W.cyl(0, 0, 1.15, 2.45, 3.0) - W.cyl(0, 0, 1.0, 1.7, 0.6)

    doc = {
        "case_centre": [cx, cy],
        "fixed": ["frame", "barrel_cock"],
        "mobiles": {
            "third": {"axis": list(I), "parts": ["third"]},
            "centre": {"axis": list(C), "parts": ["centre", "minute_hand"]},
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
    return doc, parts


def main(out):
    doc, parts = build()
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    for n, m in parts.items():
        write_stl(os.path.join(out, "parts", n + ".stl"), m)
    with open(os.path.join(out, "movement.json"), "w") as f:
        json.dump(doc, f, indent=1)
    print("parts", len(parts), "axes", {k: [round(v, 2) for v in m["axis"]] for k, m in doc["mobiles"].items()})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
