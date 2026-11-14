"""Anchors and the exploit hunt: the reference, deliberate faults, and attempts to beat the grader
without real work. Each has the reward it must get.

    python anchors.py WORK_DIR [PARALLEL] [ONLY_PREFIX]

Builds each variant (reference.build() options, then optional edits to the written submission),
grades it with `python -I grade.py`, and prints one line per anchor with ok or FAIL. Exit 0 when all ok.
Run it inside the grading container (see README): it is heavy.
"""
import json
import math
import os
import shutil
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reference as R  # noqa: E402
import constants as C  # noqa: E402

W = C.WEIGHTS
TOT = sum(W.values())
frac = lambda *ks: sum(W[k] for k in ks) / TOT  # noqa: E731


# ---------- edits applied to a written submission ----------
def edit_json(fn):
    def f(d):
        p = os.path.join(d, "keyless.json")
        j = json.load(open(p))
        fn(j)
        with open(p, "w") as fh:
            json.dump(j, fh, indent=1, allow_nan=True)
    return f


def fuse(j):
    m = j["mobiles"]
    m["stem"]["parts"] += m.pop("sliding_pinion")["parts"] + m.pop("winding_pinion")["parts"]


def axis_off(j):
    p = j["mobiles"]["crown_wheel"]["point"]
    j["mobiles"]["crown_wheel"]["point"] = [p[0] + 0.2, p[1], p[2]]


def nan_point(j):
    j["mobiles"]["crown_wheel"]["point"] = [float("nan"), 0, 0]


def huge_point(j):
    j["mobiles"]["crown_wheel"]["point"] = [1e30, 0, 0]


def click_fixed(j):
    j["fixed"] += j["mobiles"].pop("click")["parts"]


def click_free(j):
    j["mobiles"]["click"]["kind"] = "free"
    j["mobiles"]["click"].pop("rest", None)


def named_fixed(j):
    j["mobiles"]["fixed"] = j["mobiles"].pop("click")


def supplied_spring(j):
    j["mobiles"]["click"]["parts"] = ["minute_post"]


def symlink_part(d):
    p = os.path.join(d, "parts", "click.stl")
    os.remove(p)
    os.symlink(os.path.join(d, "parts", "stem.stl"), p)


def open_mesh(d):
    p = os.path.join(d, "parts", "click.stl")
    data = open(p, "rb").read()
    n = struct.unpack_from("<I", data, 80)[0]
    with open(p, "wb") as fh:
        fh.write(data[:80] + struct.pack("<I", n - 1) + data[84:84 + 50 * (n - 1)])


ANCHORS = [
    # (name, build options or None for an empty folder, post-edit, want, how)
    ("reference", {}, None, 1.0, "eq"),
    ("do nothing (empty folder)", None, None, 0.0, "eq"),
    ("Breguet teeth symmetric (ramps both ways)", {"breguet_steep": 0.5}, None, frac("set"), "le"),
    ("no click", {"click": False}, None, 1 - frac("click"), "le"),
    ("sliding pinion's spur teeth 0.15 further out: meet the setting wheel before the Breguet teeth let go",
     {"teeth_shift": 0.15}, None, 1 - frac("sweep"), "le"),
    ("yoke stroke too small (counterbore 0.45 deeper: the pinion is dragged only 0.3)", {"cbore_end": 3.45}, None,
     frac("wind", "slip"), "le"),
    ("sliding pinion spring pointing the wrong way", {"rest_sign_slider": 1}, None, frac("set"), "le"),
    ("crown wheel 0.1 off its declared axis (caught at rest)", {"shift": {"crown_wheel": (0.1, 0.0, 0.0)}}, None, 0.0, "eq"),
    # ----- exploit hunt -----
    ("X nothing engages (no Breguet or setting teeth): slip and sweep trivially", {"no_teeth": True}, None, 0.0, "eq"),
    ("X stem, sliding pinion and winding pinion fused into one mobile", {}, edit_json(fuse), frac("wind"), "le"),
    ("X crown wheel axis declared 0.2 off its geometry", {}, edit_json(axis_off), frac("set"), "le"),
    ("X NaN in a declared axis point", {}, edit_json(nan_point), 0.0, "eq"),
    ("X declared axis point at 1e30", {}, edit_json(huge_point), frac("set"), "le"),
    ("X a part file is a symbolic link", {}, symlink_part, 0.0, "eq"),
    ("X a part mesh with one triangle missing (open)", {}, open_mesh, 0.0, "eq"),
    ("X click a 0.002-thick sliver (passes through)", {"sliver_click": True}, None, 1 - frac("click"), "le"),
    ("X click declared fixed (a permanent brake)", {}, edit_json(click_fixed), frac("set"), "le"),
    ("X click declared free, no spring (lifted once, never returns)", {}, edit_json(click_free), 1 - frac("click"), "le"),
    ("X click spring pointing away from the ratchet", {"rest_sign_click": -1}, None, 1 - frac("click"), "le"),
    ("X a mobile named 'fixed' (shadowing the grader's body)", {}, edit_json(named_fixed), 0.0, "eq"),
    ("X a supplied part declared as a spring", {}, edit_json(supplied_spring), 0.0, "eq"),
    ("X fine Breguet teeth (32 teeth, 0.04 high): skip between steps", {"breguet_n": 32, "breguet_h": 0.04}, None,
     frac("set"), "le"),
]


def run(i):
    name, opts, post, want, how = ANCHORS[i]
    d = os.path.join(WORK, "a%02d" % i)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    if opts is not None:
        parts, spec = R.build(opts)
        R.write(d, parts, spec)
        if post:
            post(d)
    rw = os.path.join(d, "reward.txt")
    dt = os.path.join(d, "details.json")
    p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "grade.py"), d, os.path.join(HERE, "data"),
                        "--reward", rw, "--details", dt, "--jobs", "4"], capture_output=True, text=True)
    got = float(open(rw).read())
    ok = abs(got - want) < 1e-6 if how == "eq" else got <= want + 1e-6
    failed, secs = [], "-"
    if os.path.exists(dt):
        j = json.load(open(dt))
        failed = [k for k, v in {**j["gates"], **j.get("counted", j["checks"])}.items() if not v]
        secs = j.get("seconds")
    return ok, "%-4s %-100s S=%.4f want %s %.4f failed: %s (%ss)" % (
        "ok" if ok else "FAIL", name, got, "=" if how == "eq" else "<=", want, ",".join(failed) or "-", secs)


if __name__ == "__main__":
    WORK = os.path.abspath(sys.argv[1])
    par = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    only = sys.argv[3] if len(sys.argv) > 3 else None
    idx = [i for i, a in enumerate(ANCHORS) if only is None or a[0].startswith(only)]
    with ThreadPoolExecutor(par) as ex:
        res = list(ex.map(run, idx))
    for ok, line in res:
        print(line, flush=True)
    sys.exit(0 if all(ok for ok, _ in res) else 1)
