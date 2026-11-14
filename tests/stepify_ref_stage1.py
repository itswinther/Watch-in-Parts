"""Rebuild some reference stage-1 parts on the CAD kernel as STEP, in a copy of a reference stage-1 folder.
    python3 tests/stepify_ref_stage1.py /abs/OUT/stage1 /abs/OUT/stage1_step
The rebuilt parts replace their .stl files (which are deleted from the copy). A phase-B sketch: same
placement and phases as solution/reference_watch.py, gears from geometry/watch_gears_cad.py."""
import math
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from geometry import watch_gears_cad as GC
from solution import reference_watch as R

PHASES = {}


def gear_at(axis, teeth, module, z, toward, partner=None):
    """Same phasing rule as reference_watch.gear_at, CAD solid."""
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
    return [GC.cyl(x, y, z0, z1, r), GC.cyl(x, y, z0 - plen, z0 + 0.01, pivot), GC.cyl(x, y, z1 - 0.01, z1 + top, pivot)]


def hand(axis, z0, z1, length, hub_r, hole_r):
    x, y = axis
    h = GC.union([GC.cyl(x, y, z0, z1, hub_r), GC.box((x, y - 0.3, z0), (x + length, y + 0.3, z1))])
    return GC.cut(h, GC.cyl(x, y, z0 - 1, z1 + 1, hole_r)) if hole_r else h


def build():
    P = R.place()
    B, I, C, T, S = (P[k] for k in ("barrel", "third", "centre", "fourth", "seconds"))
    lo, hi = R.PLATE[1] + 0.1, R.BRIDGE[0] - 0.1
    sx, sy = S
    parts = {}
    p1, _ = gear_at(I, 24, R.M_A, R.Z["A"], R.ang(I, B), (96, 0.0))
    w1, ph_w1 = gear_at(I, 60, R.M_B, R.Z["B"], R.ang(I, C))
    parts["third"] = GC.union(arbor(I, lo, hi) + [p1, w1])
    # centre wheel phase is needed for the fourth pinion
    _, ph_p2 = gear_at(C, 30, R.M_B, R.Z["B"], R.ang(C, I), (60, ph_w1))
    _, ph_w2 = gear_at(C, 90, R.M_C, R.Z["C"], R.ang(C, T))
    p3, _ = gear_at(T, 12, R.M_C, R.Z["C"], R.ang(T, C), (90, ph_w2))
    w3, ph_w3 = gear_at(T, 96, R.M_D, R.Z["D"], R.ang(T, S))
    parts["fourth"] = GC.union(arbor(T, lo, hi) + [p3, w3])
    p4, _ = gear_at(S, 12, R.M_D, R.Z["D"], R.ang(S, T), (96, ph_w3))
    parts["seconds"] = GC.union([GC.cyl(sx, sy, lo, hi, 0.8), GC.cyl(sx, sy, lo - 0.7, lo + 0.01, 0.3),
                                 GC.cyl(sx, sy, hi - 0.01, 10.3, 0.5), p4])
    parts["hour_hand"] = hand(C, 9.9, 10.2, 6.0, 1.3, 0.85)
    parts["minute_hand"] = hand(C, 10.7, 11.0, 9.0, 1.0, 0.0)
    parts["seconds_hand"] = hand(S, 9.9, 10.2, 5.0, 0.9, 0.0)
    parts["barrel_cock"] = GC.cut(GC.cyl(0, 0, 1.15, 2.45, 3.0), GC.cyl(0, 0, 1.0, 1.7, 0.6))
    return parts


def main(src, dst):
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    t = time.time()
    parts = build()
    for n, s in parts.items():
        os.remove(os.path.join(dst, "parts", n + ".stl"))
        GC.export(os.path.join(dst, "parts", n + ".step"), s)
    print("rebuilt %d parts as STEP in %.1f s: %s" % (len(parts), time.time() - t, ", ".join(sorted(parts))))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
