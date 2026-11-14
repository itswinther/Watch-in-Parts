"""Involute gear maker. Used to build the supplied barrel and the reference movement.
NOT shipped to the agent: making teeth that mesh is part of the task."""
import math
import numpy as np
import manifold3d as m3
from .core import union

PRESSURE_ANGLE = 25.0
BARREL_TEETH = 96
BARREL_MODULE = 0.2
BARREL_WHEEL_Z = (0.0, 1.0)
BARREL_ARBOR_Z = (-1.0, 1.6)
BARREL_ARBOR_R = 0.5


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


def make_barrel():
    """The supplied mainspring barrel: a 96-tooth wheel and its arbor, axis on x = y = 0."""
    return union([gear(BARREL_TEETH, BARREL_MODULE, *BARREL_WHEEL_Z),
                  cyl(0, 0, BARREL_ARBOR_Z[0], BARREL_ARBOR_Z[1], BARREL_ARBOR_R)])


