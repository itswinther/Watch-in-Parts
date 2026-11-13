"""Anchor suite: submissions with the score SPEC.md says they should get.
    python tests/test_anchors.py
Builds each anchor from the reference script with one thing changed, grades it,
and prints one line per anchor. Exit code 1 if any anchor is off."""
import json
import math
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "solution"))
import numpy as np
import reference as ref
from geometry import constants as C
from geometry.core import box, cyl_x, write_stl
from geometry.checks import grade

W = C.WEIGHTS
TOTAL = sum(W.values())


def only_fails(*ids):
    p = (TOTAL - sum(W[i] for i in ids)) / TOTAL
    return 0.5 * p * p


def write(d, base=None, door=None, asm=None):
    base = ref.build_base() if base is None else base
    door = ref.build_door() if door is None else door
    asm = ref.build_assembly() if asm is None else asm
    write_stl(os.path.join(d, "base.stl"), base)
    write_stl(os.path.join(d, "door.stl"), door)
    with open(os.path.join(d, "assembly.json"), "w") as f:
        json.dump({k: [np.asarray(T).tolist() for T in v] for k, v in asm.items()}, f)


def a_reference(d):
    write(d)


def a_nothing(d):
    pass


def a_garbage(d):
    write(d)
    with open(os.path.join(d, "base.stl"), "wb") as f:
        f.write(b"solid half\nfacet normal 0 0 1\n outer loop\n  vertex 0 0 0\n  vertex 1 0")


def a_wall_removed(d):
    write(d, base=ref.build_base() - box((ref.X0 - 1, ref.Y0 + 3, ref.FLOOR_TOP), (ref.X0 + ref.WALL + 0.1, ref.Y1 - 3, 13)))


def a_u_slot(d):
    (y0, _), (y1, _) = C.J1_KEEPOUT_YZ
    write(d, base=ref.build_base() - box((ref.X0 - 1, y0, 0), (ref.X0 + ref.WALL + 0.1, y1, 13)))


def a_nan(d):
    asm = ref.build_assembly()
    asm["lid"][3] = np.full((4, 4), float("nan"))
    write(d, asm=asm)


def a_teleport(d):
    asm = ref.build_assembly()
    asm["board"] = [asm["board"][0], asm["board"][-1]]
    write(d, asm=asm)


def a_nonrigid(d):
    asm = ref.build_assembly()
    asm["door"][5] = asm["door"][5] @ np.diag([1.01, 1, 1, 1])
    write(d, asm=asm)


def a_final_clash(d):
    write(d, base=ref.build_base() + box((60, 20, ref.FLOOR_TOP), (66, 26, 0.8)))


def a_straight_down(d):
    asm = ref.build_assembly()
    asm["board"] = ref.straight(np.eye(4), (0, 0, 1), 45.0)
    write(d, asm=asm)


def a_no_pegs(d):
    old = ref.PEG_HOLES
    ref.PEG_HOLES = ()
    try:
        write(d)
    finally:
        ref.PEG_HOLES = old


def a_narrow_j2_window(d):
    """J2 window is the body-clearance rectangle only, so the round plug does not fit.
    (A true blind pocket also blocks the board path, so it cannot fail K2 alone.)"""
    old = ref.J2_WIN_R
    ref.J2_WIN_R = 2.0
    try:
        write(d)
    finally:
        ref.J2_WIN_R = old


def a_blind_pocket(d):
    write(d, base=ref.build_base() + box((ref.X1 - 0.35, 5, -8), (ref.X1, 19, 3)))


def a_lazy_tub(d):
    """Thick box, oversize windows, no pegs, straight-down path."""
    lo, hi = np.array(C.ENVELOPE[0]), np.array(C.ENVELOPE[1])
    tub = box(lo + [0, 0, 1.75], hi) - box((-0.3, -0.3, -6.9), (71.8, 45.3, 13))
    tub -= box((-3, 13.5, -3), (0, 31.5, 9.5))
    tub -= cyl_x(12.0, -2.5, 71, 74, 6.9)
    tub -= box((8.7, 3.7, -9), (57.3, 34.3, -6))
    asm = ref.build_assembly()
    asm["board"] = ref.straight(np.eye(4), (0, 0, 1), 45.0)
    write(d, base=tub, asm=asm)


ANCHORS = [
    ("reference", a_reference, 1.0, 1.0),
    ("do nothing", a_nothing, 0, 0),
    ("half-written file", a_garbage, 0, 0),
    ("wall removed", a_wall_removed, 0, 0),
    ("U-slot open to rim", a_u_slot, 0, 0),
    ("NaN in path", a_nan, 0, 0),
    ("teleporting path", a_teleport, 0, 0),
    ("non-rigid pose", a_nonrigid, 0, 0),
    ("clash in final pose", a_final_clash, 0, 0),
    ("lazy tub", a_lazy_tub, 0, 0.25),
    ("no valid board path (A1 only)", a_straight_down, only_fails("A1"), only_fails("A1")),
    ("no pegs (F2 only)", a_no_pegs, only_fails("F2"), only_fails("F2")),
    ("J2 window too narrow (K2 only)", a_narrow_j2_window, only_fails("K2"), only_fails("K2")),
    ("blind J2 pocket", a_blind_pocket, 0, only_fails("A1")),
]


def main():
    bad = 0
    for name, fn, lo, hi in ANCHORS:
        with tempfile.TemporaryDirectory() as d:
            fn(d)
            r = grade(*(os.path.join(d, f) for f in ("base.stl", "door.stl", "assembly.json")))
        ok = lo - 1e-6 <= r["reward"] <= hi + 1e-6
        bad += not ok
        failed = [k for k, v in list(r["gates"].items()) + list(r["checks"].items()) if not v]
        print("%-4s %-32s S=%.4f expected %.4f..%.4f  failed: %s"
              % ("ok" if ok else "OFF", name, r["reward"], lo, hi, ",".join(failed) or "-"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
