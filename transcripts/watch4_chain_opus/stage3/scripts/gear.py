"""Involute spur gear like the barrel: PA 25, addendum 1.0m, dedendum 1.25m, thickness -0.03 backlash."""
import math, numpy as np, cadquery as cq
def profile(z, m, phase_deg, cx, cy, pa=25.0, backlash=0.03, n_inv=12):
    r = m * z / 2; rb = r * math.cos(math.radians(pa)); ra = r + m; rf = r - 1.25 * m
    inv = lambda a: math.tan(a) - a
    # half tooth angle at pitch circle
    half_t = (math.pi * m / 2 - backlash) / (2 * r)
    a_p = math.radians(pa)
    r0 = max(rb, rf)
    pts_flank = []
    for i in range(n_inv + 1):
        rr = r0 + (ra - r0) * i / n_inv
        alpha = math.acos(min(1.0, rb / rr))
        th = half_t + inv(a_p) - inv(alpha)  # angle from tooth centre line
        pts_flank.append((rr, th))
    pitch = 2 * math.pi / z
    pts = []
    for k in range(z):
        c = math.radians(phase_deg) + k * pitch
        # root before the tooth
        th_root = pts_flank[0][1]
        if r0 > rf + 1e-9: pts.append((rf, c - th_root))
        for rr, th in pts_flank:
            pts.append((rr, c - th))
        for rr, th in reversed(pts_flank):
            pts.append((rr, c + th))
        if r0 > rf + 1e-9: pts.append((rf, c + th_root))
    xy = [(cx + rr * math.cos(a), cy + rr * math.sin(a)) for rr, a in pts]
    return xy
def gear_solid(z, m, phase_deg, cx, cy, z0, z1):
    xy = profile(z, m, phase_deg, cx, cy)
    return cq.Workplane('XY').workplane(offset=z0).polyline(xy).close().extrude(z1 - z0)
