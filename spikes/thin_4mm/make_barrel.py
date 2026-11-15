"""Spike only: write the thin barrel of spikes/thin_4mm/data/ (barrel.stl, barrel_drum.stl, barrel_arbor.stl): the
supplied meshes of geometry/data/ scaled in z by geometry.watch.THIN_BARREL_SCALE about z = 0 (arbor -0.4545..2.5455,
drum 0..0.4545, square 1.5..2.2273). The teeth (96, module 0.2) and every x/y size are unchanged.
    python3 spikes/thin_4mm/make_barrel.py"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from geometry import core, watch as W     # noqa: E402

for name in ("barrel", "barrel_drum", "barrel_arbor"):
    src = os.path.join(ROOT, "geometry", "data", name + ".stl")
    man = core.tris_to_manifold(core.read_stl(src, W.MAX_TRIANGLES, W.MAX_STL_BYTES)).scale([1.0, 1.0, W.THIN_BARREL_SCALE])
    dst = os.path.join(ROOT, "spikes", "thin_4mm", "data", name + ".stl")
    core.write_stl(dst, man)
    b = man.bounding_box()
    print(name, "z %.4f .. %.4f" % (b[2], b[5]), "volume %.3f" % man.volume())
