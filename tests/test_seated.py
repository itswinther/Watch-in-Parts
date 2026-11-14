"""Small fixtures for the rules on parts of one mobile, through the real STEP loader and grader.
    python3 tests/test_seated.py
A wheel (a disc, radius 3, z 1.0 to 1.5) on an arbor (shaft radius 0.5, z 0 to 5) on the axis x = 30, y = 0,
far from the barrel; one fixed block far away. Checks: Assembled (no overlap inside a mobile), seated,
and stage-4 replay with every pair tested."""
import json
import math
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import cadquery as cq
from geometry import core
from grade_watch import grade_design, grade_assembly, WEIGHTS

AX = (30.0, 0.0)
CLEAR = 0.01            # radial clearance of the bore (see tests/measure_fit_clearance.py)


def cyl(r, z0, z1, x=AX[0], y=AX[1]):
    return cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).extrude(z1 - z0)


def shaft():
    return cyl(0.5, 0.0, 5.0)


def stepped():
    return shaft().union(cyl(1.0, 0.0, 1.0))                     # shoulder below the wheel


def collared():
    return stepped().union(cyl(1.0, 1.5, 2.0))                   # and a collar above it


def wheel(bore=True, dx=0.0):
    w = cyl(3.0, 1.0, 1.5, AX[0] + dx)
    return w.cut(cyl(0.5 + CLEAR, 0.0, 5.0, AX[0] + dx)) if bore else w


def write(folder, arbor, whl, extra=None):
    os.makedirs(os.path.join(folder, "parts"))
    extra = extra or {}
    for n, solid in extra.items():
        core.write_step(os.path.join(folder, "parts", n + ".step"), solid)
    core.write_step(os.path.join(folder, "parts", "arbor.step"), arbor)
    core.write_step(os.path.join(folder, "parts", "wheel.step"), whl)
    core.write_step(os.path.join(folder, "parts", "block.step"),
                    cq.Workplane("XY").box(2, 2, 2).translate((-30, 0, 0)))
    doc = {"case_centre": [0, 0], "fixed": ["block"],
           "mobiles": {"m": {"axis": list(AX), "parts": ["arbor", "wheel"] + list(extra)}}, "meshes": [],
           "hands": {h: {"mobile": "m", "part": "wheel"} for h in ("hour", "minute", "seconds")}}
    with open(os.path.join(folder, "movement.json"), "w") as f:
        json.dump(doc, f)


def drop_from_above(folder, order):
    """Every part comes straight down from above the movement's grown box, in `order`."""
    from geometry import watch as W
    m = W.load_movement(folder)
    lo, hi = m.assembly_box()
    paths = {}
    for n in order:
        solid = m.all_parts()[n]
        lift = hi[2] + 0.5 - solid.bounding_box()[2]
        k = int(math.ceil(lift / 0.19))
        paths[n] = [[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, lift * (1 - i / k)], [0, 0, 0, 1]] for i in range(k + 1)]
    with open(os.path.join(folder, "assembly.json"), "w") as f:
        json.dump({"order": order, "paths": paths}, f)


ONLY_SEATED = [k for k in WEIGHTS if k != "seated"]
failures = 0


def check(label, got, want, info=""):
    global failures
    ok = got == want
    failures += not ok
    print("%-4s %-62s got %-5s want %-5s %s" % ("ok" if ok else "FAIL", label, got, want, info), flush=True)


def design(arbor, whl, extra=None):
    d = tempfile.mkdtemp()
    shutil.rmtree(d)
    write(d, arbor, whl, extra)
    r = grade_design(d, 1, None, ONLY_SEATED)
    return d, r


def main():
    d, r = design(stepped(), wheel())
    a = r["details"]["assembled"]
    check("wheel with bore on a stepped arbor: Assembled", r["gates"]["assembled"], True, "mobile overlap %.6f" % a["mobile_parts_worst"])
    check("wheel with bore on a stepped arbor: seated", r["checks"]["seated"], True, str(r["details"]["seated"]["not_seated"]))

    for order, want in ((["block", "barrel", "arbor", "wheel"], {"arbor", "wheel"}),):
        shutil.copytree(d, d + "_s4")
        drop_from_above(d + "_s4", order)
        g = grade_assembly(d + "_s4", d + "_s4")
        got = {n for n in ("arbor", "wheel") if g["checks"].get(n)}
        check("stage 4, stepped arbor, wheel put on from the open side", sorted(got), sorted(want), "reward %.4f" % g["reward"])

    _, r = design(stepped(), wheel(bore=False))
    a = r["details"]["assembled"]
    check("wheel without a bore overlapping the arbor: Assembled", r["gates"]["assembled"], False,
          "mobile overlap %.4f %s" % (a["mobile_parts_worst"], a["mobile_pair"]))

    _, r = design(shaft(), wheel())
    ns = r["details"]["seated"]["not_seated"]
    check("wheel on a plain shaft, no shoulder: wheel not seated", "wheel" in ns, True, str(ns))
    check("wheel on a plain shaft, no shoulder: Assembled", r["gates"]["assembled"], True)

    _, r = design(stepped(), wheel(dx=5.0))
    ns = r["details"]["seated"]["not_seated"]
    check("wheel beside the arbor, not on it: wheel not seated", "wheel" in ns, True, str(ns))

    # the reviewer's case: a ring and a plug that seat on each other, floating 4 mm beside the arbor
    x = AX[0] + 4.0
    ring = cyl(2.0, 3.0, 3.5, x).cut(cyl(1.0 + CLEAR, 0.0, 5.0, x))      # above the wheel (z 1.0 to 1.5), clear of it
    plug = cyl(1.0, 2.5, 3.5, x).union(cyl(1.5, 3.5, 4.0, x))
    _, r = design(stepped(), wheel(), {"ring": ring, "plug": plug})
    sd = r["details"]["seated"]
    check("ring and plug seated on each other only: Assembled", r["gates"]["assembled"], True)
    check("ring and plug seated on each other only: each part seated", sd.get("not_seated"), [], str(sd.get("pieces")))
    check("ring and plug seated on each other only: not in one piece", sd.get("not_in_one_piece"), ["plug", "ring"])
    check("ring and plug seated on each other only: seated fails", r["checks"]["seated"], False)

    d, r = design(collared(), wheel())
    check("collars on both sides: Assembled", r["gates"]["assembled"], True, "mobile overlap %.6f" % r["details"]["assembled"]["mobile_parts_worst"])
    for order, second in ((["block", "barrel", "arbor", "wheel"], "wheel"), (["block", "barrel", "wheel", "arbor"], "arbor")):
        s4 = d + "_" + second
        shutil.copytree(d, s4)
        drop_from_above(s4, order)
        g = grade_assembly(s4, s4)
        first = "arbor" if second == "wheel" else "wheel"
        check("stage 4, collars on both sides, %s second: %s not installed" % (second, second), g["checks"].get(second), False,
              "hit %s" % g["details"]["parts"][second].get("hit"))
        check("stage 4, collars on both sides, %s second: %s installed" % (second, first), g["checks"].get(first), True)
    print("%d failed" % failures)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
