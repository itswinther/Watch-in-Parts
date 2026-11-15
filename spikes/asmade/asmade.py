"""The movement as made, as a command (the test itself is geometry/asmade.py): each part at the print process's size limits, each mobile at
the ends of the play its own bearings give it, and the same running checks as the drawn movement.

    python3 spikes/asmade/asmade.py DELIVERY_DIR OUT.json [--tol 0.03] [--file movement.json] [--states drawn,max,min] [--quick] [--stage] [--full]

Why: the one-job grader measures the drawn solids only. A design whose layers are 0.02 mm apart passes it, and no
printed part holds 0.02 mm. A designer gets the process's size tolerance from the print service (DS-W03 would
state it) and works out the clearances, the shake and the backlash that follow. This test asks for the outcome:
the movement still runs when every part is at either size limit.

States (tol = the size tolerance, every surface of a printed part lies within tol of its drawn position):
  drawn   the parts as delivered
  max     every delivered part grown by tol (most material: the tightest fits, the smallest gaps)
  min     every delivered part shrunk by tol (least material: the loosest fits, the most play)
The supplied barrel is a supplied part and stays as supplied.

Growing and shrinking (resize): the Minkowski sum with, or erosion by, an upright cylinder of radius tol and
half-height tol: every wall moves tol in plan and every flat face moves tol in height. It is worked out from
horizontal sections, as the swept solids of check 6 are (geometry/watch.py _swept_bands): the heights at which the
part has a vertex cut it into slabs, a slab that a sloping face crosses is cut into bands at most SWEEP_DZ high,
and each slab is its middle section. The grown part at a height is the union of the sections within tol of that
height, each offset outwards by tol with round corners; the shrunk part is the intersection of them, each offset
inwards by tol (and nothing where the part does not reach tol above and below).

In each state:
  assembled    no mobile overlaps the frame or another mobile by more than VOL_TOL at rest
  free         Movement.spin: each mobile turns a full turn clear of the frame
  play         how far each mobile moves along +x, -x, +y, -y, +z, -z before the frame (or a mobile on its own
               axis) stops it; "not held" if nothing stops it within PLAY_CAP
  mesh         each declared mesh, with the driven mobile first turned to the middle of its backlash (settle):
               no jam with the arbors where they are drawn (backlash is left); and the teeth still drive (a push
               of DRIVE_PUSH of a pitch reaches the driven teeth) there and with both arbors at the far side of
               their holes along the line of centres, where the tooth load pushes them
  clear        Movement.clear_swept for every pair of mobiles that is not a declared mesh, drawn position, and with
               each of the two at the end of its axial play towards the other

--quick: skips the radial-play mesh runs and the axial-play clear runs.
--stage: an old stage-mode delivery (stage barrel, no materials). --full: every mesh through its whole turn.
"""
import json
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from geometry import watch as W          # noqa: E402
from geometry import asmade as A         # noqa: E402
from geometry.asmade import *            # noqa: E402,F401,F403  (resize, play, settle, ... for scripts that import this file)

STAGE = False           # --stage: an old stage-mode delivery (the one-body stage barrel, no materials declared)


def load_state(folder, name, tol, cache):
    """The movement of `name` with every delivered part resized by tol (0: as drawn). cache: {(part, tol): solid}."""
    bs = W.barrel_stage() if STAGE else None
    base = W.load_movement(folder, name, cache=cache.setdefault("files", {}), barrel_solid=bs, materials=not STAGE)
    if tol == 0.0:
        return base
    load0 = base.load_part

    def load(n):
        key = (n, tol)
        if key not in cache:
            cache[key] = A.resize(load0(n), tol)
            if cache[key].is_empty():
                raise A.core.FormatError("part '%s' vanishes at the size limit (shrunk by %g mm)" % (n, -tol))
        return cache[key]
    return W.Movement(base.doc, load, bs, materials=not STAGE)



def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    folder, out = os.path.abspath(argv[0]), argv[1]
    flags = [a for a in argv[2:] if a in ("--quick", "--stage", "--full", "--towards")]
    rest = [a for a in argv[2:] if a not in flags]
    opts = dict(zip(rest[0::2], rest[1::2]))
    tol = float(opts.get("--tol", "0.03"))
    name = opts.get("--file", "movement.json")
    quick = "--quick" in argv
    global STAGE
    STAGE = "--stage" in argv
    A.FULL_TURN, A.TOWARDS = "--full" in argv, "--towards" in argv
    cache, result = {}, {"delivery": folder, "file": name, "tol": tol, "states": {}}
    only = opts.get("--states", "drawn,max,min").split(",")
    for label, t in (("drawn", 0.0), ("max", tol), ("min", -tol)):
        if label not in only:
            continue
        print("state %s (%+.3f mm)" % (label, t), flush=True)
        t0 = time.time()
        try:
            m = load_state(folder, name, t, cache)
        except Exception as ex:
            print("  does not load: %s: %s" % (type(ex).__name__, ex), flush=True)
            result["states"][label] = {"error": "%s: %s" % (type(ex).__name__, ex), "ok": {"loads": False}}
            continue
        print("  loaded and resized in %.1f s" % (time.time() - t0), flush=True)
        result["states"][label] = A.run_state(m, quick, lambda s: print(s, flush=True))
        st = result["states"][label]
        print("  %s  (%.0f s)" % (st["ok"], st["seconds"]), flush=True)
        for k, v in st["free"].items():
            if v > W.VOL_TOL:
                print("  FAIL free: %s overlaps the frame by %.4f mm3 while turning" % (k, v), flush=True)
        for k, v in st["clear"].items():
            if v["worst"] > W.VOL_TOL:
                print("  FAIL clear: %s swept overlap %.4f mm3 (drawn %.4f)" % (k, v["worst"], v["drawn"]), flush=True)
    result["runs_as_made"] = all(all(s["ok"].values()) for s in result["states"].values())
    with open(out, "w") as f:
        json.dump(result, f, indent=1, default=float)
    print("runs as made at +/- %g mm: %s" % (tol, result["runs_as_made"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
