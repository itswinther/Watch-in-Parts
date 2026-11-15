"""Write the barrel catalogue's meshes, geometry/data/<id>/{barrel,barrel_drum,barrel_arbor}.stl, for every id of
geometry.watch.BARREL_CATALOGUE: BR-096-20's meshes (geometry/data/) scaled in z only, about z = 0. BR-096-66 is
copied byte for byte from geometry/data/, BR-096-30 from geometry/data/thin/ (the thin barrel); the others are
scaled here.     python3 spikes/barrel_catalogue/make_barrels.py"""
import os
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from geometry import core, watch as W     # noqa: E402

DATA = os.path.join(ROOT, "geometry", "data")
COPY = {"BR-096-66": DATA, "BR-096-30": os.path.join(DATA, "thin")}
for bid, k in sorted(W.BARREL_CATALOGUE.items()):
    os.makedirs(os.path.join(DATA, bid), exist_ok=True)
    for name in ("barrel", "barrel_drum", "barrel_arbor"):
        dst = os.path.join(DATA, bid, name + ".stl")
        if bid in COPY:
            shutil.copyfile(os.path.join(COPY[bid], name + ".stl"), dst)
        else:
            src = os.path.join(DATA, name + ".stl")
            man = core.tris_to_manifold(core.read_stl(src, W.MAX_TRIANGLES, W.MAX_STL_BYTES)).scale([1.0, 1.0, k])
            core.write_stl(dst, man)
        man = core.tris_to_manifold(core.read_stl(dst, W.MAX_TRIANGLES, W.MAX_STL_BYTES))
        b = man.bounding_box()
        print(bid, name, "z %.4f .. %.4f" % (b[2], b[5]), "expected", W.barrel_z(bid)["arbor" if name != "barrel_drum" else "wheel"])
