"""CAD gear maker -> STEP -> the grader's loader -> mesh_run.
    python3 tests/test_cad_gears.py            # the stated tessellation tolerance; asserts the mesh passes
    python3 tests/test_cad_gears.py --sweep    # also measures other tolerances (table for the spec)
A 96-tooth wheel and a 12-tooth pinion, module 0.2, built with geometry/watch_gears_cad.py, written to
STEP, read back through geometry.watch.load_part_file, placed at the centre distance with the phasing
the reference uses, and turned through the mesh test."""
import math
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from geometry import core
from geometry import watch as W
from geometry import watch_gears_cad as GC

TEETH_A, TEETH_B, MODULE = 96, 12, 0.2


def phase_for(teeth, partner_teeth, partner_phase, line_deg):
    """Same rule as solution/reference_watch.py gear_at: mesh with a partner lying along line_deg."""
    delta = ((line_deg + 180.0) - partner_phase) % (360.0 / partner_teeth)
    return line_deg + delta * partner_teeth / teeth + 180.0 / teeth


def pair_movement(sa, sb, axis_b):
    m = object.__new__(W.Movement)
    m.mobiles = {"a": {"axis": (0.0, 0.0), "solid": sa, "parts": {}}, "b": {"axis": axis_b, "solid": sb, "parts": {}}}
    return m


def build(tmp):
    cd = MODULE * (TEETH_A + TEETH_B) / 2.0
    t0 = time.time()
    wheel = GC.gear(TEETH_A, MODULE, 0.0, 1.0, phase_deg=0.0)
    t1 = time.time()
    pa = os.path.join(tmp, "wheel96.step")
    GC.export(pa, wheel)
    t2 = time.time()
    pinion = GC.gear(TEETH_B, MODULE, 0.0, 1.0, phase_deg=phase_for(TEETH_B, TEETH_A, 0.0, 180.0), x=cd, y=0.0)
    pb = os.path.join(tmp, "pinion12.step")
    GC.export(pb, pinion)
    print("96-tooth gear: build %.2f s, STEP export %.2f s, file %d bytes; 12-tooth file %d bytes"
          % (t1 - t0, t2 - t1, os.path.getsize(pa), os.path.getsize(pb)))
    return pa, pb, (cd, 0.0)


def measure(pa, pb, axis_b, lin, ang):
    kw = dict(max_bytes=W.MAX_STEP_BYTES, max_triangles=W.MAX_TRIANGLES, linear_deflection=lin, angular_deflection=ang,
              max_triangle_faces=W.STEP_MAX_TRIANGLE_FACES, timeout_s=W.STEP_TIMEOUT_S, memory_mb=W.STEP_MEMORY_MB,
              self_union_tol=W.SELF_UNION_TOL)
    t = time.time()
    sa = core.load_step_part(pa, **kw)
    sb = core.load_step_part(pb, **kw)
    load = time.time() - t
    t = time.time()
    r = pair_movement(sa, sb, axis_b).mesh_run("a", TEETH_A, "b", TEETH_B)
    run = time.time() - t
    return {"lin": lin, "ang": ang, "tris_96": sa.num_tri(), "tris_12": sb.num_tri(), "load_s": load, "run_s": run,
            "worst": r["worst_volume"], "gap": r["largest_gap"], "drive": r["smallest_drive_overlap"]}


def row(d):
    return ("lin %-7g ang %-5g | tris 96: %7d  12: %6d | load %5.2f s | mesh_run %5.1f s | worst overlap %.5f  "
            "largest gap %.4f  smallest drive %.4f" % (d["lin"], d["ang"], d["tris_96"], d["tris_12"], d["load_s"],
                                                       d["run_s"], d["worst"], d["gap"], d["drive"]))


def main():
    with tempfile.TemporaryDirectory() as tmp:
        pa, pb, axis_b = build(tmp)
        if "--sweep" in sys.argv:
            for lin, ang in ((0.01, 0.5), (0.003, 0.2), (0.001, 0.1), (0.0003, 0.05)):
                print(row(measure(pa, pb, axis_b, lin, ang)), flush=True)
        d = measure(pa, pb, axis_b, W.STEP_LINEAR_DEFLECTION, W.STEP_ANGULAR_DEFLECTION)
        print("stated tolerance:", row(d))
        assert d["worst"] <= W.VOL_TOL, "jam: worst overlap %.5f" % d["worst"]
        assert d["gap"] <= W.ENGAGE_GAP, "gap %.4f" % d["gap"]
        assert d["drive"] > W.VOL_TOL, "drive overlap %.5f" % d["drive"]
        mesh = core.tris_to_manifold  # noqa: the same path an STL takes
        # the CAD gear and the mesh gear of geometry/watch_gears.py have the same tooth form
        from geometry import watch_gears as G
        ref = G.gear(TEETH_A, MODULE, 0.0, 1.0)
        sa = W.load_part_file(pa)
        dv = core.ivol(sa, ref)
        print("96-tooth CAD vs mesh gear: volumes %.4f / %.4f, symmetric difference %.4f mm3"
              % (sa.volume(), ref.volume(), sa.volume() + ref.volume() - 2 * dv))
    print("PASS")


if __name__ == "__main__":
    main()
