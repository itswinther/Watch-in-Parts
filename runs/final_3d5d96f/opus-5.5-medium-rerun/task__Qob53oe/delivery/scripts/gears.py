"""Rack-generated involute spur gear profiles (2D) for the demonstration calibre.
Pressure angle 25 deg, addendum 1.0 m, dedendum 1.25 m, full-round rack tip (DS-W04 basic rack).
Each tooth is thinned by `thin` (mm, on the pitch circle) for backlash."""
import math
import numpy as np
import manifold3d as m3

ALPHA = math.radians(25.0)


def rack_tooth(m, thin, nseg=24):
    """Cutter tooth polygon in rack coordinates (u along pitch line, v outward from the gear)."""
    ta = math.tan(ALPHA)
    w0 = math.pi * m / 4 + thin / 2               # half width of the cutter tooth on the pitch line
    hf = 1.25 * m                                  # depth of the cutter tip below the pitch line
    # full round tip tangent to both flanks, lowest point at v = -hf
    # (w0 + vc*ta)*cos(a) = rho, vc = -hf + rho
    ca = math.cos(ALPHA)
    rho = (w0 - hf * ta) * ca / (1 - ta * ca)
    vc = -hf + rho
    # tangent point on right flank
    nx, ny = ca, -math.sin(ALPHA)                  # outward normal of right flank (pointing +u, -v)
    tx, ty = rho * nx, vc + rho * ny
    a0 = math.atan2(ty - vc, tx)                  # angle of right tangent point from centre
    pts = []
    top = 2.0 * m
    pts.append((w0 + top * ta, top))
    # down the right flank to tangent point, round the tip, up the left flank
    angs = np.linspace(a0, -math.pi - a0, nseg)
    for a in angs:
        pts.append((rho * math.cos(a), vc + rho * math.sin(a)))
    pts.append((-(w0 + top * ta), top))
    return pts[::-1]   # counter-clockwise


def gear_section(m, z, thin, phase=0.0, steps_per_module=24):
    """CrossSection of a gear with z teeth, module m, centred at the origin.
    A tooth is centred on the direction `phase` (radians)."""
    r = m * z / 2
    ra = r + m
    tooth = rack_tooth(m, thin)
    span = 2.6 * m                                 # rack travel on each side
    n = max(40, int(2 * span / m * steps_per_module))
    cut_polys = []
    for s in np.linspace(-span, span, n):
        phi = s / r
        c, si = math.cos(-phi), math.sin(-phi)
        poly = []
        for (u, v) in tooth:
            x, y = u - s, r + v
            poly.append((c * x - si * y, si * x + c * y))
        cut_polys.append(m3.CrossSection([poly]))
    gap = m3.CrossSection.batch_boolean(cut_polys, m3.OpType.Add)
    # gap is centred at +90 deg; rotate so that a tooth is at `phase`
    gaps = [gap.rotate(math.degrees(phase - math.pi / 2 + math.pi / z + 2 * math.pi * k / z)) for k in range(z)]
    allgaps = m3.CrossSection.batch_boolean(gaps, m3.OpType.Add)
    nseg = max(720, int(2 * math.pi * ra / 0.004))
    disc = m3.CrossSection.circle(ra, nseg)
    g = disc - allgaps
    return g.simplify(0.001)


def section_loops(cs):
    return [np.asarray(p, float) for p in cs.to_polygons()]
