"""Write STEP files that the part loader must reject, and one it must accept.
    python3 tests/make_bad_steps.py OUT_DIR
Prints, for each file, what geometry.watch.load_part_file says."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cadquery as cq
from OCP.STEPControl import STEPControl_Writer, STEPControl_AsIs
from OCP.Interface import Interface_Static
from geometry import watch as W
from geometry import watch_gears_cad as GC
from geometry.core import FormatError


def write(path, shape, unit="MM"):
    Interface_Static.SetCVal_s("write.step.unit", unit)
    w = STEPControl_Writer()
    w.Transfer(getattr(shape, "wrapped", shape), STEPControl_AsIs)
    w.Write(path)
    Interface_Static.SetCVal_s("write.step.unit", "MM")


def faceted(path):
    """A gear dumped from a mesh: every triangle a planar face, sewn into a solid."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
    from OCP.gp import gp_Pnt
    from OCP.TopoDS import TopoDS
    from geometry import watch_gears as G
    import numpy as np
    m = G.gear(24, 0.2, 0.0, 1.0).to_mesh()
    v = np.asarray(m.vert_properties)[:, :3]
    sew = BRepBuilderAPI_Sewing(1e-6)
    for t in np.asarray(m.tri_verts):
        p = BRepBuilderAPI_MakePolygon(*[gp_Pnt(*map(float, v[i])) for i in t], True)
        sew.Add(BRepBuilderAPI_MakeFace(p.Wire(), True).Face())
    sew.Perform()
    solid = BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(sew.SewedShape())).Solid()
    write(path, solid)
    return len(np.asarray(m.tri_verts))


def main(out):
    os.makedirs(out, exist_ok=True)
    g = GC.gear(12, 0.2, 0.0, 1.0)
    files = {}
    files["good_mm"] = os.path.join(out, "good_mm.step")
    write(files["good_mm"], g)
    files["inch"] = os.path.join(out, "inch.step")
    write(files["inch"], g, "INCH")
    files["metre"] = os.path.join(out, "metre.step")
    write(files["metre"], g, "M")
    files["two_solids"] = os.path.join(out, "two_solids.step")
    write(files["two_solids"], cq.Compound.makeCompound([g, GC.cyl(5, 5, 0, 1, 0.5)]))
    files["broken"] = os.path.join(out, "broken.step")
    with open(files["good_mm"], "rb") as f:
        data = f.read()
    with open(files["broken"], "wb") as f:
        f.write(data[: len(data) // 2])
    files["garbage"] = os.path.join(out, "garbage.step")
    with open(files["garbage"], "wb") as f:
        f.write(b"ISO-10303-21;\nthis is not a step file\n" * 100)
    files["oversized"] = os.path.join(out, "oversized.step")
    with open(files["oversized"], "wb") as f:
        f.write(data)
        f.write(b"/* padding */\n" * ((W.MAX_STEP_BYTES - len(data)) // 14 + 10))
    files["shell_only"] = os.path.join(out, "shell_only.step")
    write(files["shell_only"], g.Shells()[0])
    files["faceted"] = os.path.join(out, "faceted.step")
    nf = faceted(files["faceted"])
    print("faceted gear: %d triangles" % nf)
    for k, p in files.items():
        t = time.time()
        try:
            s = W.load_part_file(p)
            msg = "ACCEPTED volume %.4f" % s.volume()
        except FormatError as e:
            msg = "format error: %s" % e
        print("%-11s %5.2f s  %s" % (k, time.time() - t, msg))


if __name__ == "__main__":
    main(sys.argv[1])
