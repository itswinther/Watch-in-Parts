"""Anchors: the reference and deliberate faults, each with the reward it must get.

    python anchors.py WORK_DIR

Builds each variant with reference.build(), grades it with `python -I grade.py`, and prints one
line per anchor with ok or FAIL. Exit code 0 when every anchor is ok.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reference as R  # noqa: E402
import constants as C  # noqa: E402

W = C.WEIGHTS
TOT = sum(W.values())
lose = lambda *ks: 1 - sum(W[k] for k in ks) / TOT  # noqa: E731
P_SPUR = 3.141592653589793 * 0.2
P_FACE = 3.141592653589793 * 0.15

ANCHORS = [
    ("reference", {}, 1.0, "eq"),
    ("do nothing (empty folder)", None, 0.0, "eq"),
    ("wrong winding direction (pinion on the far side of the crown wheel)", {"side": +1}, lose("direction"), "eq"),
    ("ratio outside the band (crown pinion 18 teeth: 6 stem turns per arbor turn)", {"zcs": 18}, lose("ratio"), "eq"),
    ("plain disc instead of face teeth", {"face_plain": True}, lose("drive", "direction", "ratio"), "le"),
    ("ratchet teeth thinned 10 %", {"thin_spur": 0.025 * P_SPUR}, lose("drive", "direction", "ratio"), "le"),
    ("face teeth thinned 10 %", {"thin_face": 0.025 * P_FACE}, lose("drive", "direction", "ratio"), "le"),
    ("crown wheel 0.1 off its declared axis", {"crown_shift": (0.1, 0.0)}, lose("drive", "direction", "ratio"), "le"),
    ("ratchet tooth count declared 35 instead of 36", {"declare": {(1, "driven_teeth"): 35}}, lose("drive", "direction", "ratio"), "le"),
    ("winding wheels raised into the main plate", {"spur_z": (-2.0, -1.5)}, 0.0, "eq"),
    ("stem ends inside the case", {"stem_x_out": -14.0}, lose("bounds"), "eq"),
]


def main(work):
    py = sys.executable
    bad = 0
    for i, (name, opts, want, how) in enumerate(ANCHORS):
        d = os.path.join(work, "a%02d" % i)
        os.makedirs(d, exist_ok=True)
        if opts is not None:
            parts, spec = R.build(opts)
            R.write(d, parts, spec)
        rw = os.path.join(d, "reward.txt")
        dt = os.path.join(d, "details.json")
        subprocess.run([py, "-I", os.path.join(HERE, "grade.py"), d, os.path.join(HERE, "data"),
                        "--reward", rw, "--details", dt], capture_output=True, text=True)
        got = float(open(rw).read())
        ok = abs(got - want) < 1e-6 if how == "eq" else got <= want + 1e-6
        failed = []
        if os.path.exists(dt):
            j = json.load(open(dt))
            failed = [k for k, v in {**j["gates"], **j["checks"]}.items() if not v]
        bad += not ok
        print("%-4s %-72s S=%.4f want %s %.4f failed: %s" % ("ok" if ok else "FAIL", name, got,
              "=" if how == "eq" else "<=", want, ",".join(failed) or "-"))
    return bad


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1]) else 0)
