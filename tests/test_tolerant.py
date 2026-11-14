"""The "arbors slightly out of place" requirement on a minimal two-mobile movement.
    python3 tests/test_tolerant.py
The supplied barrel drives a 12-tooth CAD pinion (geometry/watch_gears_cad.py, through STEP and the
grader's loader) at the standard centre distance. Two pinions:
  honest: backlash allowance 0.03 of its own              -> passes drawn, away and towards
  tight:  teeth 0.06 fatter than standard (backlash -0.06) -> passes drawn (overlap 0.006), jams moved towards (0.017)
Also checks that mesh_run on the cut-down solids gives the same numbers as on the whole solids
(cut=False) on the honest pair in all three positions."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geometry import core
from geometry import watch as W
from geometry import watch_gears_cad as GC
from test_cad_gears import phase_for

TEETH = 12


def movement(tmp, label, **kw):
    """A real Movement: one fixed plate, the barrel, and mobile 'p' with one pinion part."""
    cd = W.BARREL_MODULE * (W.BARREL_TEETH + TEETH) / 2.0
    pin = GC.gear(TEETH, W.BARREL_MODULE, W.BARREL_WHEEL_Z[0], W.BARREL_WHEEL_Z[1],
                  phase_deg=phase_for(TEETH, W.BARREL_TEETH, 0.0, 180.0), x=cd, y=0.0, **kw)
    path = os.path.join(tmp, label + ".step")
    GC.export(path, pin)
    solids = {"pinion": W.load_part_file(path), "plate": core.box((-12, -12, -3.0), (16, 12, -2.5))}
    doc = {"case_centre": [0, 0], "fixed": ["plate"], "mobiles": {"p": {"axis": [cd, 0.0], "parts": ["pinion"]}},
           "meshes": [{"driver": "barrel", "driver_teeth": W.BARREL_TEETH, "driven": "p", "driven_teeth": TEETH}],
           "hands": {h: {"mobile": "p", "part": "pinion"} for h in ("hour", "minute", "seconds")}}
    return W.Movement(doc, lambda n: solids[n])


def passes(x):
    return x["worst_volume"] <= W.VOL_TOL and x["largest_gap"] <= W.ENGAGE_GAP and x["smallest_drive_overlap"] > W.VOL_TOL


def positions(m, cut=True):
    a, ta, b, tb = m.meshes[0]
    return {lab: m.mesh_run(a, ta, b, tb, shift=s, cut=cut)
            for lab, s in (("drawn", 0.0), ("away", W.MESH_SHIFT), ("towards", -W.MESH_SHIFT))}


def show(label, r):
    for lab, x in r.items():
        print("%-7s %-8s worst overlap %.5f  largest gap %.4f  smallest drive %.4f  %s"
              % (label, lab, x["worst_volume"], x["largest_gap"], x["smallest_drive_overlap"],
                 "pass" if passes(x) else "FAIL"), flush=True)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        honest = movement(tmp, "honest", backlash=0.03)
        r = positions(honest)
        show("honest", r)
        assert all(passes(x) for x in r.values()), "honest pinion must pass all three positions"
        plain = positions(honest, cut=False)
        for lab in r:
            for k in ("worst_volume", "largest_gap", "smallest_drive_overlap"):
                assert abs(r[lab][k] - plain[lab][k]) <= 1e-9, (lab, k, r[lab][k], plain[lab][k])
        print("fast and plain mesh_run agree on all three positions")
        tight = movement(tmp, "tight", backlash=-0.06)
        r = positions(tight)
        show("tight", r)
        assert passes(r["drawn"]), "tight pinion must still pass the drawn position (train)"
        assert not passes(r["towards"]), "tight pinion must fail when moved towards the barrel"
    print("ok")


if __name__ == "__main__":
    main()
