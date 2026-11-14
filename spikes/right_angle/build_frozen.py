"""Build the frozen movement and the supplied arbor square as STL files.

    python build_frozen.py REF_STAGE1_DIR OUT_DIR

REF_STAGE1_DIR is B's reference stage 1 (`python3 solution/reference_watch.py OUT`, then OUT/stage1),
holding parts/*.step and movement.json. The barrel mesh comes from geometry/data/barrel.stl.
The main plate gets a bore of radius 0.6 round the barrel axis from z -1.8 to -0.95, so the
supplied arbor square can pass through it to the underside.
"""
import json
import os
import shutil
import sys

import numpy as np
import manifold3d as m3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from geometry import core  # noqa: E402
import constants as C  # noqa: E402


def step_to_manifold(path, tol=0.004):
    import cadquery as cq
    shape = cq.importers.importStep(path).val()
    vs, ts = shape.tessellate(tol, 0.2)
    v = np.array([(p.x, p.y, p.z) for p in vs], dtype=np.float64)
    t = np.array(ts, dtype=np.int64)
    return core.tris_to_manifold(v[t])


def arbor_square():
    s = C.SQUARE_SIDE
    z0, z1 = C.SQUARE_Z
    round_part = core.cyl_z(0, 0, z1, -1.0, 0.5)
    square = core.box([-s / 2, -s / 2, z0], [s / 2, s / 2, z1])
    flange = core.cyl_z(0, 0, z0 - 0.3, z0, 1.0)
    return core.union([round_part, square, flange])


def main(ref, out):
    os.makedirs(os.path.join(out, "frozen"), exist_ok=True)
    mv = json.load(open(os.path.join(ref, "movement.json")))
    names = sorted(n[:-5] for n in os.listdir(os.path.join(ref, "parts")) if n.endswith(".step"))
    for n in names:
        man = step_to_manifold(os.path.join(ref, "parts", n + ".step"))
        if n == "main_plate":
            man = man - core.cyl_z(0, 0, -1.8, -0.95, 0.6)
        core.write_stl(os.path.join(out, "frozen", n + ".stl"), man)
        print(n, man.num_tri(), round(man.volume(), 3))
    shutil.copyfile(os.path.join(ROOT, "geometry", "data", "barrel.stl"), os.path.join(out, "frozen", "barrel.stl"))
    core.write_stl(os.path.join(out, "arbor_square.stl"), arbor_square())
    json.dump({"frozen_parts": names + ["barrel"], "source": "B reference_watch.py stage 1, main plate bored at the barrel axis",
               "case_centre": mv.get("case_centre")}, open(os.path.join(out, "frozen.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
