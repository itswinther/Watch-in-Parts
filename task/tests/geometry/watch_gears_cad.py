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


def _vertical_edges(solid):
    return cq.Workplane().add(solid).edges("|Z").vals()


def spoke_cutters(x, y, z0, z1, hub_r, rim_r, spokes, width, phase_deg=0.0, fillet=0.15):
    """The pockets between `spokes` straight spokes of `width` from a hub of radius hub_r to a rim whose inside
    radius is rim_r, as separate solids reaching 0.5 beyond z0..z1. Their vertical edges are rounded by
    `fillet`, so the wheel's inside corners are rounded."""
    ann = cyl(x, y, z0 - 0.5, z1 + 0.5, rim_r).cut(cyl(x, y, z0 - 1, z1 + 1, hub_r))
    bars = []
    for k in range(spokes):
        b = cq.Solid.makeBox(rim_r + 1.0, width, z1 - z0 + 3.0, cq.Vector(x, y - width / 2.0, z0 - 1.5))
        bars.append(b.rotate(cq.Vector(x, y, 0), cq.Vector(x, y, 1), phase_deg + 360.0 * k / spokes))
    out = []
    for p in ann.cut(*bars).Solids():
        if fillet:
            try:
                p = p.fillet(fillet, _vertical_edges(p))
            except Exception:
                pass
        out.append(p)
    return out


def spoked_gear(teeth, module, z0, z1, phase_deg=0.0, x=0.0, y=0.0, hub_r=1.3, rim=0.5, spokes=5, width=0.6,
                fillet=0.15, **kw):
    """gear() with the web cut away to a rim (`rim` mm inside the root circle), `spokes` spokes and a hub."""
    g = gear(teeth, module, z0, z1, phase_deg=phase_deg, x=x, y=y, **kw)
    rf = module * teeth / 2.0 - kw.get("dedendum", 1.25) * module
    rim_r = rf - rim
    if rim_r - hub_r < 0.8:
        return g
    return cut(g, *spoke_cutters(x, y, z0, z1, hub_r, rim_r, spokes, width, phase_deg, fillet))


def skeleton(z0, z1, bosses, bar_width):
    """A frame plate: a disc for each boss (x, y, r) joined by straight bars of bar_width along a minimum
    spanning tree of the boss centres; one solid from z0 to z1."""
    n = len(bosses)
    d = lambda i, j: math.hypot(bosses[i][0] - bosses[j][0], bosses[i][1] - bosses[j][1])
    inside, edges = {0}, []
    while len(inside) < n:
        i, j = min(((i, j) for i in inside for j in range(n) if j not in inside), key=lambda e: d(*e))
        edges.append((i, j))
        inside.add(j)
    parts = [cyl(x, y, z0, z1, r) for x, y, r in bosses]
    for i, j in edges:
        (xa, ya, _), (xb, yb, _) = bosses[i], bosses[j]
        L = d(i, j)
        b = cq.Solid.makeBox(L, bar_width, z1 - z0, cq.Vector(xa, ya - bar_width / 2.0, z0))
        parts.append(b.rotate(cq.Vector(xa, ya, 0), cq.Vector(xa, ya, 1), math.degrees(math.atan2(yb - ya, xb - xa))))
    return union(parts), edges
