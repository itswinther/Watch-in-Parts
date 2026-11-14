"""Involute gear maker. Used to build the supplied barrel and the reference movement.
NOT shipped to the agent: making teeth that mesh is part of the task.

    python3 -m geometry.watch_gears        (re)write geometry/data/barrel_drum.stl, barrel_arbor.stl, barrel.stl

The barrel's numbers are the constants of geometry/watch.py (one place)."""
import math
import os
import numpy as np
import manifold3d as m3
from .core import union, write_stl
from .watch import (PRESSURE_ANGLE, BARREL_TEETH, BARREL_MODULE, BARREL_WHEEL_Z, BARREL_ARBOR_Z, BARREL_ARBOR_R,
                    BARREL_CORE_R, BARREL_BORE_R, BARREL_SQUARE_SIDE, BARREL_SQUARE_Z, STAGE_BARREL_ARBOR_Z)

BARREL_SEG = 48             # facets of the arbor's round sections (as the one-body barrel)
CORE_SEG = 192              # facets of the core and of the drum's bore (inscribed polygons; the clearance stays
                            # above 0.01 at any relative turn)


def gear_profile(teeth, module, pressure_deg=PRESSURE_ANGLE, backlash=0.03, addendum=1.0, dedendum=1.25, pts=8):
    """Outline (N x 2) of an involute spur gear centred on the origin. Tooth 0 is centred on +x."""
    a = math.radians(pressure_deg)
    r = module * teeth / 2.0
    rb, ra, rf = r * math.cos(a), r + addendum * module, r - dedendum * module
    s = math.pi * module / 2.0 - backlash
    inv = lambda x: math.tan(x) - x
    half = lambda R: s / (2 * r) + inv(a) - (inv(math.acos(min(1.0, rb / R))) if R > rb else 0.0)
    r0 = max(rb, rf)
    radii = np.linspace(r0, ra, pts)
    flank = [(R, half(R)) for R in radii]
    pitch = 2 * math.pi / teeth
    out = []
    for k in range(teeth):
        c = k * pitch
        if rf < r0:
            out.append((rf, c - half(r0)))
        out += [(R, c - h) for R, h in flank]
        out += [(R, c + h) for R, h in reversed(flank)]
        if rf < r0:
            out.append((rf, c + half(r0)))
        out.append((rf, c + pitch / 2))
    return np.array([(R * math.cos(t), R * math.sin(t)) for R, t in out])


def gear(teeth, module, z0, z1, phase_deg=0.0, **kw):
    cs = m3.CrossSection([gear_profile(teeth, module, **kw)]).rotate(phase_deg)
    return cs.extrude(z1 - z0).translate([0, 0, z0])


def cyl(x, y, z0, z1, r, seg=48):
    return m3.Manifold.cylinder(z1 - z0, r, r, seg).translate([x, y, z0])


def make_barrel_stage():
    """The one-body barrel of the stage mode (data/barrel_stage.stl): a 96-tooth wheel and its arbor."""
    return union([gear(BARREL_TEETH, BARREL_MODULE, *BARREL_WHEEL_Z),
                  cyl(0, 0, STAGE_BARREL_ARBOR_Z[0], STAGE_BARREL_ARBOR_Z[1], BARREL_ARBOR_R)])


def make_barrel_drum():
    """The toothed drum: the 96-tooth wheel of the one-body barrel (same teeth, same phase, same z), with a bore
    of BARREL_BORE_R round the arbor's core."""
    return gear(BARREL_TEETH, BARREL_MODULE, *BARREL_WHEEL_Z) - cyl(0, 0, BARREL_WHEEL_Z[0] - 1, BARREL_WHEEL_Z[1] + 1,
                                                                   BARREL_BORE_R, CORE_SEG)


def make_barrel_arbor():
    """The arbor: pivot and plain sections of BARREL_ARBOR_R from BARREL_ARBOR_Z[0] to [1], the core of
    BARREL_CORE_R over the drum's z, and the winding square over BARREL_SQUARE_Z."""
    a = BARREL_SQUARE_SIDE / 2.0
    return union([cyl(0, 0, BARREL_ARBOR_Z[0], BARREL_ARBOR_Z[1], BARREL_ARBOR_R, BARREL_SEG),
                  cyl(0, 0, BARREL_WHEEL_Z[0], BARREL_WHEEL_Z[1], BARREL_CORE_R, CORE_SEG),
                  m3.Manifold.cube([2 * a, 2 * a, BARREL_SQUARE_Z[1] - BARREL_SQUARE_Z[0]]).translate(
                      [-a, -a, BARREL_SQUARE_Z[0]])])


def make_barrel():
    """The supplied barrel as one solid: the union of the drum and the arbor (they do not touch)."""
    return union([make_barrel_drum(), make_barrel_arbor()])


def write_barrel(data_dir=None):
    data_dir = data_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    out = {"barrel_drum": make_barrel_drum(), "barrel_arbor": make_barrel_arbor()}
    out["barrel"] = union([out["barrel_drum"], out["barrel_arbor"]])
    for n, man in out.items():
        write_stl(os.path.join(data_dir, n + ".stl"), man)
    return out


if __name__ == "__main__":
    for n, man in write_barrel().items():
        print(n, "volume %.4f" % man.volume(), "triangles", man.num_tri())


