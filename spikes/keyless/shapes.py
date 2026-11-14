"""Solids for the toy tests, the reference and the anchors (the grader never imports this).

All in millimetres. Polygons are extruded with manifold3d.
"""
import math
import struct

import numpy as np
import manifold3d as m3


def extrude_poly(pts, z0, z1):
    if _area(pts) < 0:
        pts = pts[::-1]
    cs = m3.CrossSection([pts], m3.FillRule.Positive)
    return m3.Manifold.extrude(cs, z1 - z0).translate([0, 0, z0])


def cyl_z(x, y, z0, z1, r, n=96):
    return m3.Manifold.cylinder(z1 - z0, r, r, n).translate([x, y, z0])


def cyl_x(y, z, x0, x1, r, n=96):
    c = m3.Manifold.cylinder(x1 - x0, r, r, n)            # along +z from 0
    c = c.transform([[0, 0, 1, 0], [0, 1, 0, 0], [-1, 0, 0, 0]])  # z -> x
    return c.translate([x0, y, z])


def box(lo, hi):
    return m3.Manifold.cube([hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2]]).translate(list(lo))


def union(ms):
    ms = [m for m in ms if m is not None and not m.is_empty()]
    if not ms:
        return m3.Manifold()
    return ms[0] if len(ms) == 1 else m3.Manifold.batch_boolean(ms, m3.OpType.Add)


def z_to_x(man):
    """Map a solid built along +z onto +x (z->x, x->y, y->z)."""
    return man.transform([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]])


def write_stl(path, man):
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties, dtype=np.float32)[:, :3]
    f = np.asarray(mesh.tri_verts, dtype=np.int64)
    with open(path, "wb") as fh:
        fh.write(b"keyless spike".ljust(80, b" "))
        fh.write(struct.pack("<I", len(f)))
        tri = v[f]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        rec = np.zeros(len(f), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
        rec["n"] = n
        rec["v"] = tri
        fh.write(rec.tobytes())


# ---------- toy-test solids ----------
def ratchet_wheel(n, r_root, r_tip, z0, z1, steep_frac=0.03):
    """Sawtooth wheel on z. Turning anticlockwise (+) lifts a click; clockwise meets a steep face."""
    p = 2 * math.pi / n
    pts = []
    for k in range(n):
        a = k * p
        pts.append((r_root * math.cos(a), r_root * math.sin(a)))
        a2 = a + steep_frac * p
        pts.append((r_tip * math.cos(a2), r_tip * math.sin(a2)))
    return extrude_poly(pts, z0, z1)


def click(n, r_root, r_tip, z0, z1, lever=2.5, clearance=0.03):
    """Click lever whose tip sits in the valley at angle 0 of ratchet_wheel(n, ...).

    The pivot lies on the tangent through the tip, on the side the steep face pushes towards, so
    the click locks. Rest direction: +1 (anticlockwise about the pivot moves the tip inwards).
    Returns (solid, pivot point, rest sign).
    """
    p = 2 * math.pi / n
    h = r_tip - r_root
    # wedge in the valley: bounded by the ramp below and the steep face at angle ~0
    a_face = -0.004                                    # just before the steep face
    tip_in = (r_root + 0.06) * math.cos(a_face), (r_root + 0.06) * math.sin(a_face)
    a_back = -0.45 * p
    r_ramp_back = r_root + h * (0.45)                 # ramp height there (ramp falls towards angle 0)
    back = ((r_ramp_back + 0.05) * math.cos(a_back), (r_ramp_back + 0.05) * math.sin(a_back))
    top_face = (r_tip + 0.35) * math.cos(a_face), (r_tip + 0.35) * math.sin(a_face)
    xm = r_tip + 0.35
    piv = (xm - 0.25, -lever)
    wedge = [tip_in, back, (xm, back[1] - 0.3), (xm, top_face[1])]
    wedge = [(x, y) for x, y in wedge]
    tipm = extrude_poly(wedge, z0, z1)
    arm = extrude_poly([(xm - 0.5, piv[1]), (xm, piv[1]), (xm, back[1]), (xm - 0.5, back[1])], z0, z1)
    hub = cyl_z(piv[0], piv[1], z0, z1, 0.35, 48)
    sol = union([tipm, arm, hub])
    # open a small clearance from the wheel at rest by rotating the click outwards slightly
    return sol, (piv[0], piv[1], 0.0)


def star_wheel(n, r_root, r_tip, z0, z1):
    """Symmetric star (pointed teeth) on z, a valley at angle 0."""
    p = 2 * math.pi / n
    pts = []
    for k in range(n):
        a = k * p
        pts.append((r_root * math.cos(a), r_root * math.sin(a)))
        a2 = a + p / 2
        pts.append((r_tip * math.cos(a2), r_tip * math.sin(a2)))
    return extrude_poly(pts, z0, z1)


def detent_lever(n, r_root, r_tip, z0, z1, lever=2.5):
    """Detent with a V tip resting in the star's valley at angle 0; pivot on the -y side."""
    p = 2 * math.pi / n
    r_v = r_root + 0.05
    a = 0.30 * p
    tipv = [(r_v, 0.0)]
    rr = r_root + (r_tip - r_root) * 0.6
    left = (rr * math.cos(-a) + 0.04, rr * math.sin(-a))
    right = (rr * math.cos(a) + 0.04, rr * math.sin(a))
    xm = r_tip + 0.3
    poly = [tipv[0], left, (xm, left[1]), (xm, right[1]), right]
    # order anticlockwise
    poly = [tipv[0], left, (xm, left[1]), (xm, right[1]), right]
    sol = extrude_poly(poly[::-1] if _area(poly) < 0 else poly, z0, z1)
    piv = (xm - 0.25, -lever)
    arm = extrude_poly([(xm - 0.5, piv[1]), (xm, piv[1]), (xm, left[1]), (xm - 0.5, left[1])], z0, z1)
    hub = cyl_z(piv[0], piv[1], z0, z1, 0.35, 48)
    return union([sol, arm, hub]), (piv[0], piv[1], 0.0)


def _area(poly):
    s = 0.0
    for i in range(len(poly)):
        x0, y0 = poly[i]
        x1, y1 = poly[(i + 1) % len(poly)]
        s += x0 * y1 - x1 * y0
    return s / 2
