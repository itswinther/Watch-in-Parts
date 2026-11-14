"""Involute gear maker and solid helpers on the CAD kernel (CadQuery 2.8 / OpenCASCADE).
Same tooth form and phasing as geometry/watch_gears.py: pressure angle 25 degrees, addendum 1.0 m,
dedendum 1.25 m, backlash 0.03 mm on the pitch circle, tooth 0 centred on +x before `phase_deg`.
Flanks are B-spline curves through exact involute points, tips and roots are circular arcs.
Private: used for the reference. NOT shipped to the agent."""
import math
import cadquery as cq
from .watch_gears import PRESSURE_ANGLE

FLANK_POINTS = 12


def _polar(R, t):
    return (R * math.cos(t), R * math.sin(t))


def gear_outline(teeth, module, pressure_deg=PRESSURE_ANGLE, backlash=0.03, addendum=1.0, dedendum=1.25,
                 pts=FLANK_POINTS):
    """Closed planar wire of the gear outline at z = 0 (cq.Wire)."""
    a = math.radians(pressure_deg)
    r = module * teeth / 2.0
    rb, ra, rf = r * math.cos(a), r + addendum * module, r - dedendum * module
    s = math.pi * module / 2.0 - backlash
    inv = lambda x: math.tan(x) - x
    half = lambda R: s / (2 * r) + inv(a) - (inv(math.acos(min(1.0, rb / R))) if R > rb else 0.0)
    r0 = max(rb, rf)
    radii = [r0 + (ra - r0) * k / (pts - 1) for k in range(pts)]
    pitch = 2 * math.pi / teeth
    V = cq.Vector
    edges = []
    for k in range(teeth):
        c = k * pitch
        # root arc from the previous tooth's trailing foot to this tooth's leading foot
        t_prev = ((k - 1) % teeth) * pitch + half(r0)     # same expression as that tooth's foot: ends match exactly
        t_this = c - half(r0)
        t_mid = t_this - (pitch - 2 * half(r0)) / 2
        if rf < r0:
            p_a, p_b = _polar(rf, t_prev), _polar(rf, t_this)
            edges.append(cq.Edge.makeThreePointArc(V(*p_a, 0), V(*_polar(rf, t_mid), 0), V(*p_b, 0)))
            edges.append(cq.Edge.makeLine(V(*p_b, 0), V(*_polar(r0, t_this), 0)))
        else:
            edges.append(cq.Edge.makeThreePointArc(V(*_polar(rf, t_prev), 0), V(*_polar(rf, t_mid), 0),
                                                   V(*_polar(rf, t_this), 0)))
        lead = [V(*_polar(R, c - half(R)), 0) for R in radii]
        trail = [V(*_polar(R, c + half(R)), 0) for R in reversed(radii)]
        edges.append(cq.Edge.makeSpline(lead))
        edges.append(cq.Edge.makeThreePointArc(lead[-1], V(*_polar(ra, c), 0), trail[0]))
        edges.append(cq.Edge.makeSpline(trail))
        if rf < r0:
            edges.append(cq.Edge.makeLine(trail[-1], V(*_polar(rf, c + half(r0)), 0)))
    return cq.Wire.assembleEdges(edges)


def gear(teeth, module, z0, z1, phase_deg=0.0, x=0.0, y=0.0, **kw):
    """Spur gear solid (cq.Solid), axis on (x, y), from z0 to z1."""
    face = cq.Face.makeFromWires(gear_outline(teeth, module, **kw))
    sol = cq.Solid.extrudeLinear(face, cq.Vector(0, 0, z1 - z0))
    return sol.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), phase_deg).translate(cq.Vector(x, y, z0))


def cyl(x, y, z0, z1, r):
    return cq.Solid.makeCylinder(r, z1 - z0, cq.Vector(x, y, z0))


def tube(x, y, z0, z1, r_out, r_in):
    return cut(cyl(x, y, z0, z1, r_out), cyl(x, y, z0 - 1, z1 + 1, r_in))


def box(lo, hi):
    return cq.Solid.makeBox(hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2], cq.Vector(*lo))


def union(solids):
    solids = [s for s in solids if s is not None]
    out = solids[0]
    if len(solids) > 1:
        out = out.fuse(*solids[1:], glue=False).clean()
    return _one_solid(out)


def cut(a, *tools):
    tools = [t for t in tools if t is not None]
    return _one_solid(a.cut(*tools).clean()) if tools else a


def _one_solid(shape):
    sols = shape.Solids()
    if len(sols) != 1:
        raise ValueError("boolean result has %d solids, expected 1" % len(sols))
    return sols[0]


def export(path, solid):
    from .core import write_step
    write_step(path, solid)
