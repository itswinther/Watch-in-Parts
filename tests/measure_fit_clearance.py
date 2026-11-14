"""Measure how much a shaft overlaps a bore of (nearly) the same radius once both go through the real
STEP loader (deflection 0.001). Prints the intersection volume per radius, clearance and seam angle.
    python3 tests/measure_fit_clearance.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import cadquery as cq
from geometry import watch as W
from geometry import core


def load(shape, d, name):
    p = os.path.join(d, name + ".step")
    core.write_step(p, shape)
    return W.load_part_file(p)


def main():
    d = tempfile.mkdtemp()
    print("radius clearance seam_deg overlap_mm3")
    for r in (0.5, 1.0):
        for c in (0.0, 0.0005, 0.001, 0.002, 0.005, 0.01):
            for seam in (0.0, 7.3, 90.0):
                bore = cq.Workplane("XY").box(4 * r + 4, 4 * r + 4, 5, centered=(True, True, False)) \
                    .cut(cq.Workplane("XY").circle(r + c).extrude(5))
                shaft = cq.Workplane("XY").circle(r).extrude(5).rotate((0, 0, 0), (0, 0, 1), seam)
                v = core.ivol(load(bore, d, "bore"), load(shaft, d, "shaft"))
                print("%.1f %.4f %5.1f %.6f" % (r, c, seam, v), flush=True)


if __name__ == "__main__":
    main()
