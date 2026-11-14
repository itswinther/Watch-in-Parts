"""Anchors: the reference and deliberate faults, each with the reward it must get.

    python anchors.py WORK_DIR [PARALLEL]

Builds each variant with reference.build(), grades it with `python -I grade.py`, and prints one
line per anchor with ok or FAIL. Exit code 0 when every anchor is ok.
"""
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reference as R  # noqa: E402
import constants as C  # noqa: E402

W = C.WEIGHTS
TOT = sum(W.values())
lose = lambda *ks: 1 - sum(W[k] for k in ks) / TOT  # noqa: E731

ANCHORS = [
    ("reference", {}, 1.0, "eq"),
    ("do nothing (empty folder)", None, 0.0, "eq"),
    ("Breguet teeth symmetric (ramps both ways)", {"breguet_steep": 0.5}, lose("wind"), "le"),
    ("no click", {"click": False}, lose("click"), "le"),
    ("sliding pinion's spur teeth 0.15 further out: meet the setting wheel before the Breguet teeth let go", {"teeth_shift": 0.15}, lose("sweep"), "le"),
    ("yoke stroke too small (counterbore 0.45 deeper: the collar drags the pinion only 0.3)", {"cbore_end": 3.45}, lose("set", "sweep"), "le"),
    ("sliding pinion spring pointing the wrong way", {"rest_sign_slider": 1}, lose("wind"), "le"),
    ("crown wheel 0.1 off its declared axis (caught at rest)", {"shift": {"crown_wheel": (0.1, 0.0, 0.0)}}, 0.0, "eq"),
]


def run(i):
    name, opts, want, how = ANCHORS[i]
    d = os.path.join(WORK, "a%02d" % i)
    os.makedirs(d, exist_ok=True)
    if opts is not None:
        parts, spec = R.build(opts)
        R.write(d, parts, spec)
    rw = os.path.join(d, "reward.txt")
    dt = os.path.join(d, "details.json")
    subprocess.run([sys.executable, "-I", os.path.join(HERE, "grade.py"), d, os.path.join(HERE, "data"),
                    "--reward", rw, "--details", dt], capture_output=True, text=True)
    got = float(open(rw).read())
    ok = abs(got - want) < 1e-6 if how == "eq" else got <= want + 1e-6
    failed = []
    if os.path.exists(dt):
        j = json.load(open(dt))
        failed = [k for k, v in {**j["gates"], **j["checks"]}.items() if not v]
    return ok, "%-4s %-66s S=%.4f want %s %.4f failed: %s" % (
        "ok" if ok else "FAIL", name, got, "=" if how == "eq" else "<=", want, ",".join(failed) or "-")


if __name__ == "__main__":
    WORK = os.path.abspath(sys.argv[1])
    par = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    with ThreadPoolExecutor(par) as ex:
        res = list(ex.map(run, range(len(ANCHORS))))
    for ok, line in res:
        print(line)
    sys.exit(0 if all(ok for ok, _ in res) else 1)
