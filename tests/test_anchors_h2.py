"""Anchor suite for instance H2.   python tests/test_anchors_h2.py
Each anchor is the reference with one thing changed. Exit code 1 if any is off."""
import json
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "solution"))
import numpy as np
import reference_h2 as ref
from geometry import h2_public as P
from geometry.core import box, write_stl
from geometry.h2_checks import grade, WEIGHTS, W_STRUCT, W_SIZE, size_term

TOTAL = sum(WEIGHTS.values())


def only_fails(*ids):
    p = (TOTAL - sum(WEIGHTS[i] for i in ids)) / TOTAL
    return W_STRUCT * p * p


def write(d, base=None, lid=None, asm=None):
    base = ref.build_base() if base is None else base
    lid = ref.build_lid() if lid is None else lid
    asm = ref.build_assembly() if asm is None else asm
    write_stl(os.path.join(d, "base.stl"), base)
    write_stl(os.path.join(d, "lid.stl"), lid)
    with open(os.path.join(d, "assembly.json"), "w") as f:
        json.dump({"order": asm["order"], "paths": {k: [np.asarray(T).tolist() for T in v] for k, v in asm["paths"].items()}}, f)


class patched:
    def __init__(self, **kw):
        self.kw = kw

    def __enter__(self):
        self.old = {k: getattr(ref, k) for k in self.kw}
        for k, v in self.kw.items():
            setattr(ref, k, v)

    def __exit__(self, *a):
        for k, v in self.old.items():
            setattr(ref, k, v)


def a_reference(d):
    write(d)


def a_nothing(d):
    pass


def deeper(extra):
    """Same design with the floor `extra` lower: valid but larger."""
    def fn(d):
        with patched(FLOOR_TOP=ref.FLOOR_TOP - extra, FLOOR_BOT=ref.FLOOR_BOT - extra,
                     T_B=(ref.T_B[0], ref.T_B[1], ref.T_B[2] - extra),
                     T_SPK=(ref.T_SPK[0], ref.T_SPK[1], ref.T_SPK[2] - extra)):
            write(d)
    return fn


def deeper_score(extra):
    size = np.array([ref.X1 - ref.X0, ref.Y1 - ref.Y0, ref.ZTOP + P.LID_THICKNESS - ref.FLOOR_BOT + extra])
    return W_STRUCT + W_SIZE * size_term(float(np.prod(size)))


def a_small_lid(d):
    write(d, lid=box((10, 10, ref.ZTOP), (60, 36, ref.ZTOP + P.LID_THICKNESS)))


def a_lid_not_plate(d):
    write(d, lid=ref.build_lid() - box((20, 10, 0), (50, 30, 30)))


def a_big_window(d):
    write(d, base=ref.build_base() - box((ref.X0 - 1, 12, -3), (ref.X0 + ref.WALL + 0.2, 33, 10)))


def a_no_j3_window(d):
    with patched(T_B=(ref.T_B[0] - 20, ref.T_B[1], ref.T_B[2])):
        base = ref.build_base()
    write(d, base=base)


def a_teleport(d):
    asm = ref.build_assembly()
    asm["paths"]["A"] = [asm["paths"]["A"][0], asm["paths"]["A"][-1]]
    write(d, asm=asm)


def a_wrong_order(d):
    asm = ref.build_assembly()
    asm["order"] = ["A", "B", "speaker", "battery"]
    write(d, asm=asm)


def a_floating_battery(d):
    with patched(T_BATT=(ref.T_BATT[0], ref.T_BATT[1], ref.T_BATT[2] + 1.0)):
        write(d)


def a_blocked_keepout(d):
    write(d, base=ref.build_base() + box((ref.X0 - 6, 14, -1), (ref.X0 + 0.5, 16.2, 8)) + box((ref.X0 - 6, 14, -1), (ref.X0 - 4.4, 31, 8)))


def a_no_pegs(d):
    with patched(PEG_HOLES=()):
        write(d)


ANCHORS = [
    ("reference", a_reference, 1.0, 1.0),
    ("do nothing", a_nothing, 0, 0),
    ("lid smaller than the opening", a_small_lid, 0, 0),
    ("lid is not a plate", a_lid_not_plate, 0, 0),
    ("oversize J1 window", a_big_window, 0, 0),
    ("no window for J3", a_no_j3_window, 0, 0),
    ("teleporting path", a_teleport, 0, 0),
    ("valid, floor 3 lower", deeper(3.0), deeper_score(3.0), deeper_score(3.0)),
    ("valid, floor 12 lower", deeper(12.0), W_STRUCT, W_STRUCT),
    ("wrong order (B after A)", a_wrong_order, 0, only_fails("path_B")),
    ("battery floating 1.0", a_floating_battery, only_fails("supported_battery"), only_fails("supported_battery")),
    ("J1 keep-out blocked outside", a_blocked_keepout, 0, only_fails("keepout_J1")),
    ("no pegs", a_no_pegs, only_fails("located_A"), only_fails("located_A")),
]


def main():
    bad = 0
    for name, fn, lo, hi in ANCHORS:
        with tempfile.TemporaryDirectory() as d:
            fn(d)
            r = grade(*(os.path.join(d, f) for f in ("base.stl", "lid.stl", "assembly.json")))
        ok = lo - 1e-4 <= r["reward"] <= hi + 1e-4
        bad += not ok
        failed = [k for k, v in list(r["gates"].items()) + list(r["checks"].items()) if not v]
        if len(failed) > 6:
            failed = failed[:6] + ["..."]
        print("%-4s %-30s S=%.4f expected %.4f..%.4f  bbox %s  failed: %s"
              % ("ok" if ok else "OFF", name, r["reward"], lo, hi,
                 "%.0f" % r["bbox_volume"] if r["bbox_volume"] else "-", ",".join(failed) or "-"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
