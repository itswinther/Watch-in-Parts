"""NOT-FOR-AGENT (realcad test material; never copy into a task image).

Grade Marco Lang's ml01 going train (converted by ml01_train.py into WORK) with Part 1 of the one-job grader,
tests/grade_watch.py and geometry/watch.py unchanged. Only these are overridden, in this process:

- the supplied barrel: W.barrel() returns ml01's barrel II (drum z80 + cover, WORK/barrel_ml01.step, read by the
  grader's own STEP loader) instead of geometry/data/barrel.stl; ml01_train.py moved the movement so that barrel
  II's axis is at (0, 0), where the engine puts the barrel mobile;
- its speed: W.BARREL_TURNS_PER_HOUR = 3/20 turn per hour, clockwise (barrel II z80 -> intermediate z26 -> centre
  pinion z12 gives the centre 3/20 x 80/12 = 1 turn per hour in the barrel's own sense).

    python3 -I fairness_ml01.py WORK --details OUT.json

Part 1 only: the gates files and assembled, and the checks of JOB_PARTS P1. Parts 2 and 3 do not apply (no 24-hour
hand, no variant). Also reports check 14 for other material choices from the same stresses (FORMAT.md allows one
material per mobile today; a brass wheel on a steel pinion is reported per gear).
"""
import json
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "tests"))
sys.path.insert(0, REPO)

BARREL_TURNS_PER_HOUR = Fraction(3, 20)
_STATE = {}


def install(work):
    from geometry import watch as W
    path = os.path.join(work, "barrel_ml01.step")

    def barrel():
        if "barrel" not in _STATE:
            _STATE["barrel"] = W.load_part_file(path)
        return _STATE["barrel"]
    W.barrel = barrel
    W.BARREL_TURNS_PER_HOUR = BARREL_TURNS_PER_HOUR
    return W


# a watchmaker's materials, per gear: (mobile, teeth) -> what holds those teeth
WHEEL_OR_PINION = {("intermediate", 26): "wheel", ("centre", 12): "pinion", ("centre", 64): "wheel",
                   ("third", 10): "pinion", ("third", 75): "wheel", ("seconds", 8): "pinion"}


def strength_variants(det):
    from geometry import watch as W
    st, br = W.MATERIAL_ALLOWABLE_MPA["AD-C100-HT"], W.MATERIAL_ALLOWABLE_MPA["AD-CW614N"]
    choices = {
        "all steel (AD-C100-HT, 725 MPa)": lambda mob, z: st,
        "brass wheels (AD-CW614N, 110 MPa) on steel pinions, per part": lambda mob, z: br if WHEEL_OR_PINION.get((mob, z)) == "wheel" else st,
        "per mobile today: the wheel-only intermediate in brass, the rest steel": lambda mob, z: br if mob == "intermediate" else st,
        "all brass (every mobile AD-CW614N)": lambda mob, z: br,
    }
    rows = []
    for e in det.get("meshes", []):
        for mob, g in e.get("gears", {}).items():
            if "sigma_mpa" in g:
                rows.append({"mesh": e["pair"], "gear": mob, "teeth": g["teeth"], "kind": WHEEL_OR_PINION.get((mob, g["teeth"])),
                             "module": e["module"], "face_width": e["face_width"], "torque_nmm": e["torque_nmm"],
                             "force_n": e["force_n"], "Y": g["Y"], "sigma_mpa": g["sigma_mpa"]})
    out = {}
    for label, f in choices.items():
        r = [dict(x, allowable=f(x["gear"], x["teeth"]), passes=x["sigma_mpa"] <= f(x["gear"], x["teeth"])) for x in rows]
        out[label] = {"passes": bool(r) and all(x["passes"] for x in r), "failing": [(x["mesh"], x["gear"], x["teeth"]) for x in r if not x["passes"]]}
    return rows, out


def main(argv):
    work = os.path.abspath(argv[0])
    opts = dict(zip(argv[1:], argv[2:]))
    W = install(work)
    import grade_watch as G
    t0 = time.monotonic()
    deadline = t0 + G.JOB_TIME_LIMIT_S
    timings = {}

    def run(fn):
        t = time.monotonic()
        r = G._run(fn, deadline)
        timings[getattr(fn, "__name__", "?") + "@%d" % len(timings)] = round(time.monotonic() - t, 1)
        print("  ran %s in %.0f s: %s" % (getattr(fn, "__name__", "?"), time.monotonic() - t, r[0]), flush=True)
        return r
    p1 = dict(G.JOB_PARTS[0][4])
    folder = os.path.join(work, "delivery")
    m, gates, checks, details = G._job_movement(folder, G.JOB_MOVEMENT, W.BARREL_TURNS_PER_HOUR, p1, {}, run, {}, {})
    share = Fraction(sum(w for k, w in p1.items() if checks[k]), sum(p1.values()))
    res = {"part": "P1 going train and hands", "barrel_turns_per_hour": str(W.BARREL_TURNS_PER_HOUR),
           "gates": gates, "checks": checks, "check_weights": p1, "share_of_checks": float(share),
           "s": float(share) if all(gates.values()) else 0.0, "elapsed_s": round(time.monotonic() - t0, 1),
           "timings_s": timings, "details": details}
    if isinstance(details.get("strength"), dict):
        res["strength_rows"], res["strength_variants"] = strength_variants(details["strength"])
    if opts.get("--details"):
        with open(opts["--details"], "w") as f:
            json.dump(res, f, indent=1, default=str)
    print(json.dumps({k: res[k] for k in ("gates", "checks", "share_of_checks", "s", "elapsed_s")}, default=str))
    if "strength_variants" in res:
        print(json.dumps(res["strength_variants"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
