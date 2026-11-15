"""Exact B-rep (OpenCASCADE) builders for the v2 keyless parts whose meshes are not planar-faced: the Breguet teeth
(a profile in the unrolled (u, x) band wrapped round the stem axis) and the face rings of the crown and setting
wheels (contrate teeth cut by the mating pinion's envelope). Used by reference_v2.deliver only; the meshes in
reference_v2.build stay the design and check geometry, these are the same surfaces as CAD faces:

- Breguet teeth: each profile edge (u0, x0)-(u1, x1) wrapped at r is a helix on the cylinder r (angle u / r_mean);
  the flank between the inner and outer cylinders is the ruled (helicoidal) face between the two helices, exactly
  the surface reference.warp_cyl_x approximates with 0.03 facets.
- Face ring: the envelope gap (recut with 200 pinion poses a pitch) is sliced by planes across the gap from the
  ring's inner to its outer edge, each slice fitted with a cubic B-spline (shared knots), the slices lofted into one
  gap solid; one pitch of an exact ring minus the gap is turned 28 times and the faces sewn into the ring.
"""
import math

import numpy as np
import manifold3d as m3

from OCP.gp import gp_Pnt, gp_Pnt2d, gp_Dir, gp_Dir2d, gp_Ax2, gp_Ax3, gp_Trsf, gp_Vec
from OCP.Geom import Geom_CylindricalSurface
from OCP.Geom2d import Geom2d_Line
from OCP.BRepBuilderAPI import (BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeVertex, BRepBuilderAPI_MakeWire,
                                BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid,
                                BRepBuilderAPI_Transform, BRepBuilderAPI_MakePolygon)
from OCP.BRepLib import BRepLib
from OCP.BRepFill import BRepFill
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder, BRepPrimAPI_MakeBox
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.TopTools import TopTools_ListOfShape
from OCP.TopoDS import TopoDS
from OCP.TopAbs import TopAbs_SHELL, TopAbs_SOLID, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.ShapeFix import ShapeFix_Solid
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp


# ------------------------------------------------------------------ small helpers
def volume(sh):
    p = GProp_GProps()
    BRepGProp.VolumeProperties_s(sh, p)
    return p.Mass()


def nfaces(sh):
    ex, n = TopExp_Explorer(sh, TopAbs_FACE), 0
    while ex.More():
        n += 1
        ex.Next()
    return n


def _bool(op, a, b):
    if isinstance(b, (list, tuple)):
        if not b:
            return a
        args, tools = TopTools_ListOfShape(), TopTools_ListOfShape()
        args.Append(a)
        for t in b:
            tools.Append(t)
        o = op()
        o.SetArguments(args)
        o.SetTools(tools)
        o.SetFuzzyValue(1e-7)
        o.Build()
    else:
        o = op(a, b)
    if not o.IsDone():
        raise RuntimeError("boolean failed")
    return o.Shape()


def fuse(a, b):
    return _bool(BRepAlgoAPI_Fuse, a, b)


def cut(a, b):
    return _bool(BRepAlgoAPI_Cut, a, b)


def common(a, b):
    return _bool(BRepAlgoAPI_Common, a, b)


def one_solid(sh):
    ex = TopExp_Explorer(sh, TopAbs_SOLID)
    sols = []
    while ex.More():
        sols.append(TopoDS.Solid_s(ex.Current()))
        ex.Next()
    if len(sols) != 1:
        raise RuntimeError("%d solids" % len(sols))
    return sols[0]


def moved(sh, M):
    """Apply a 3x4 (or 4x4) affine matrix (rotation + translation, or a mirror)."""
    M = np.asarray(M, float)
    t = gp_Trsf()
    t.SetValues(*[float(M[i, j]) for i in range(3) for j in range(4)])
    return BRepBuilderAPI_Transform(sh, t, True).Shape()


def rot_z(deg, cx=0.0, cy=0.0):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0, cx - c * cx + s * cy], [s, c, 0, cy - s * cx - c * cy], [0, 0, 1, 0]]


def translate(dx, dy, dz):
    return [[1, 0, 0, dx], [0, 1, 0, dy], [0, 0, 1, dz]]


MIRROR_Z = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0]]


def cyl_z(cx, cy, z0, z1, r):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(cx, cy, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape()


def cyl_x(y, z, x0, x1, r):
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x0, y, z), gp_Dir(1, 0, 0)), r, x1 - x0).Shape()


def box(lo, hi):
    return BRepPrimAPI_MakeBox(gp_Pnt(*lo), gp_Pnt(*hi)).Shape()


def tube_x(x0, x1, r_in, r_out):
    return cut(cyl_x(0, 0, x0, x1, r_out), cyl_x(0, 0, x0 - 1, x1 + 1, r_in))


def tube_z(z0, z1, r_in, r_out):
    return cut(cyl_z(0, 0, z0, z1, r_out), cyl_z(0, 0, z0 - 1, z1 + 1, r_in))


def sew_solid(faces, tol=1e-6):
    sw = BRepBuilderAPI_Sewing(tol)
    for f in faces:
        sw.Add(f)
    sw.Perform()
    ex = TopExp_Explorer(sw.SewedShape(), TopAbs_SHELL)
    shell = TopoDS.Shell_s(ex.Current())
    sol = BRepBuilderAPI_MakeSolid(shell).Solid()
    fx = ShapeFix_Solid(sol)
    fx.Perform()
    sol = fx.Solid()
    if volume(sol) < 0:
        sol = TopoDS.Solid_s(sol.Reversed())
    return sol


# ------------------------------------------------------------------ Breguet teeth
def _cyl_surface(r):
    # U = angle from +y towards +z about +x, V = x: point (V, r cos U, r sin U), as reference.warp_cyl_x
    return Geom_CylindricalSurface(gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0), gp_Dir(0, 1, 0)), r)


def wrapped_prism(poly, r_in, r_out, r_mean):
    """The polygon [(u, x)] (u along the band, mm at r_mean) wrapped round +x between r_in and r_out."""
    pts = [(u / r_mean, x) for u, x in poly]
    n = len(pts)
    loops = {}
    edges = {}
    for r in (r_in, r_out):
        srf = _cyl_surface(r)
        vs = [BRepBuilderAPI_MakeVertex(gp_Pnt(x, r * math.cos(t), r * math.sin(t))).Vertex() for t, x in pts]
        es = []
        for i in range(n):
            (t0, x0), (t1, x1) = pts[i], pts[(i + 1) % n]
            L = math.hypot(t1 - t0, x1 - x0)
            ln = Geom2d_Line(gp_Pnt2d(t0, x0), gp_Dir2d(t1 - t0, x1 - x0))
            e = BRepBuilderAPI_MakeEdge(ln, srf, vs[i], vs[(i + 1) % n], 0.0, L).Edge()
            BRepLib.BuildCurves3d_s(e, 1e-7)
            es.append(e)
        w = BRepBuilderAPI_MakeWire()
        for e in es:
            w.Add(e)
        loops[r] = BRepBuilderAPI_MakeFace(srf, w.Wire(), True).Face()
        edges[r] = es
    faces = [loops[r_in], loops[r_out]]
    for i in range(n):
        faces.append(BRepFill.Face_s(edges[r_in][i], edges[r_out][i]))
    return sew_solid(faces)


def breguet(o, x0, x1, r_in, r_out, sliding):
    """reference.breguet as a B-rep (same profile, same wrap)."""
    n, steep = o["breguet_n"], o["breguet_steep"]
    rm = 0.5 * (r_in + r_out)
    pu = 2 * math.pi * rm / n
    tris = []
    for k in range(n):
        u0 = k * pu
        if steep >= 0.49:
            tri = [(u0, x1), (u0 + 0.5 * pu, x0), (u0 + pu, x1)]
        else:
            tri = [(u0, x1), (u0 + steep * pu, x0), (u0 + pu, x1)]
        tris.append(tri)
    if sliding:
        sol = tube_x(x1 - 0.001, x1 + 0.049, r_in, r_out)
        prisms = []
        for t in tris:
            prisms.append(wrapped_prism(t, r_in, r_out, rm))
        return one_solid(_bool(BRepAlgoAPI_Fuse, sol, prisms))
    cs = m3.CrossSection(tris, m3.FillRule.Positive)
    if cs.area() <= 0:
        cs = m3.CrossSection([t[::-1] for t in tris], m3.FillRule.Positive)
    off = cs.offset(o["clear"], m3.JoinType.Miter)
    # the offset teeth join into one loop longer than the turn; reference.breguet keeps the turn u = 0..2 pi rm:
    # clip to it, in two halves so no cutter wraps onto itself
    L = 2 * math.pi * rm
    halves = [off ^ m3.CrossSection.square([L / 2, 10]).translate([h * L / 2, x0 - 5]) for h in (0, 1)]
    cutters = []
    for P in [q for hf in halves for q in hf.to_polygons()]:
        P = [tuple(p) for p in np.asarray(P, float)]
        a = 0.5 * sum(P[i][0] * P[(i + 1) % len(P)][1] - P[(i + 1) % len(P)][0] * P[i][1] for i in range(len(P)))
        if a < 0:
            P = P[::-1]
        cutters.append(wrapped_prism(P, r_in - 0.01, r_out + 0.01, rm))
    band = tube_x(x0 - 0.05, x1, r_in, r_out)
    return one_solid(_bool(BRepAlgoAPI_Cut, band, cutters))


# ------------------------------------------------------------------ face ring (envelope gaps lofted from slices)
def _basis(t, n_ctrl, deg=3):
    """Clamped uniform cubic B-spline basis at parameters t in [0, 1]: (len(t) x n_ctrl), and the knots."""
    nseg = n_ctrl - deg
    kv = np.concatenate([np.zeros(deg), np.linspace(0, 1, nseg + 1), np.ones(deg)])
    t = np.clip(np.asarray(t, float), 0, 1 - 1e-12)
    N = np.zeros((len(t), len(kv) - 1))
    for i in range(len(kv) - 1):
        N[:, i] = (kv[i] <= t) & (t < kv[i + 1])
    for p in range(1, deg + 1):
        M = np.zeros((len(t), len(kv) - 1 - p))
        for i in range(len(kv) - 1 - p):
            d0, d1 = kv[i + p] - kv[i], kv[i + p + 1] - kv[i + 1]
            if d0 > 0:
                M[:, i] += (t - kv[i]) / d0 * N[:, i]
            if d1 > 0:
                M[:, i] += (kv[i + p + 1] - t) / d1 * N[:, i + 1]
        N = M
    return N, np.linspace(0, 1, nseg + 1)


def _fit(P, n_ctrl):
    """Least-squares cubic B-spline (clamped, uniform knots, n_ctrl poles) through the open polyline P (uniform
    parameters, ends pinned): every slice gets the same knots, so the loft needs no knot insertion."""
    from OCP.Geom import Geom_BSplineCurve
    from OCP.TColgp import TColgp_Array1OfPnt
    from OCP.TColStd import TColStd_Array1OfReal, TColStd_Array1OfInteger
    t = np.linspace(0, 1, len(P))
    N, knots = _basis(t, n_ctrl)
    N[-1, :] = 0
    N[-1, -1] = 1
    A = N[:, 1:-1]
    rhs = P - np.outer(N[:, 0], P[0]) - np.outer(N[:, -1], P[-1])
    C = np.linalg.lstsq(A, rhs, rcond=None)[0]
    C = np.vstack([P[0], C, P[-1]])
    poles = TColgp_Array1OfPnt(1, n_ctrl)
    for i, c in enumerate(C):
        poles.SetValue(i + 1, gp_Pnt(*map(float, c)))
    kn = TColStd_Array1OfReal(1, len(knots))
    mu = TColStd_Array1OfInteger(1, len(knots))
    for i, k in enumerate(knots):
        kn.SetValue(i + 1, float(k))
        mu.SetValue(i + 1, 4 if i in (0, len(knots) - 1) else 1)
    return Geom_BSplineCurve(poles, kn, mu, 3), float(np.max(np.linalg.norm(N @ C - P, axis=1)))


def _resample_open(P, m):
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    t = np.linspace(0, s[-1], m)
    return np.column_stack([np.interp(t, s, P[:, k]) for k in range(P.shape[1])])


def gap_sections(gap_mesh, radii, m=600, grow=0.0, close=0.0):
    """Slices of one gap (centre on -x) by the planes x = -d: each a straight bottom (the cut below the tip
    plane) and the U of flank, root, flank from its right end round to its left end, resampled at m points.
    grow: the slice is offset outwards first (a little more gap, so the spline's fit error never adds material)."""
    out = []
    for d in radii:
        g = gap_mesh.transform([[0, 1, 0, 0], [0, 0, 1, 0], [-1, 0, 0, -d]])   # plane x = -d -> z' = 0
        cs = g.slice(0.0)
        if grow > 0 or close > 0:   # grow, and round the inner corners (closing) so a spline can follow them
            cs = cs.offset(grow + close, m3.JoinType.Round, 2.0, 64)
            if close > 0:
                cs = cs.offset(-close, m3.JoinType.Round, 2.0, 64)
        polys = cs.to_polygons()
        if len(polys) != 1:
            raise RuntimeError("slice at %.3f: %d loops" % (d, len(polys)))
        Q = np.asarray(polys[0], float)
        a = 0.5 * np.sum(Q[:, 0] * np.roll(Q[:, 1], -1) - np.roll(Q[:, 0], -1) * Q[:, 1])
        if a < 0:
            Q = Q[::-1]
        zb = Q[:, 1].min()
        onb = Q[:, 1] < zb + 1e-7
        right = int(np.flatnonzero(onb)[np.argmax(Q[onb, 0])])
        left = int(np.flatnonzero(onb)[np.argmin(Q[onb, 0])])
        Q = np.roll(Q, -right, axis=0)                 # CCW from the right corner: up, over the root, down
        L = (left - right) % len(Q)
        U = Q[:L + 1]
        if np.any(U[1:-1, 1] < zb + 1e-7):
            raise RuntimeError("slice at %.3f: bottom not one straight run" % d)
        out.append((d, _resample_open(U, m)))
    return out


def lofted_gap(sections, n_ctrl):
    """Loft the slices (x = -d planes) into one closed solid; returns it and the largest slice-fit error."""
    ts = BRepOffsetAPI_ThruSections(True, False, 1e-6)
    ts.SetSmoothing(False)
    ts.CheckCompatibility(False)
    worst = 0.0
    for d, U in sections:
        P3 = np.column_stack([np.full(len(U), -d), U])
        crv, err = _fit(P3, n_ctrl)
        worst = max(worst, err)
        a, b = gp_Pnt(*map(float, P3[-1])), gp_Pnt(*map(float, P3[0]))
        va, vb = BRepBuilderAPI_MakeVertex(a).Vertex(), BRepBuilderAPI_MakeVertex(b).Vertex()
        eu = BRepBuilderAPI_MakeEdge(crv, vb, va).Edge()
        el = BRepBuilderAPI_MakeEdge(va, vb).Edge()
        w = BRepBuilderAPI_MakeWire(eu, el).Wire()
        ts.AddWire(w)
    ts.Build()
    if not ts.IsDone():
        raise RuntimeError("loft failed")
    return one_solid(ts.Shape()), worst


def face_ring(gap_mesh, zc, r_in, r_out, z0, z1, n_sec=0, m=600, n_ctrl=60, grow=0.0005):
    """Exact ring r_in..r_out, z0..z1 about z, minus zc lofted copies of the gap (centre on -x). The slices run
    from just inside r_in cos(half pitch) (the ring's inner edge across a gap) to just outside r_out."""
    a, b = r_in * math.cos(math.pi / zc) - 0.015, r_out + 0.01
    if n_sec:
        radii = np.linspace(a, b, n_sec)
    else:   # 0.02 apart near the ends (the inner undercut and the pointed outer end change fastest), 0.05 between
        radii = np.unique(np.concatenate([np.arange(a, a + 0.26, 0.02), np.linspace(a + 0.26, b - 0.14, 7),
                                          np.arange(b, b - 0.141, -0.02)]).round(6))
    gap, err = lofted_gap(gap_sections(gap_mesh, radii, m, grow), n_ctrl)
    print("face ring: slice fit error %.6f mm" % err)
    # one pitch of the ring (a sector between two tooth centres) minus the gap, then 28 turned copies of its faces
    # sewn together without the sector planes (cutting 28 gaps from one ring fails where the pointed outer tooth
    # ends bring neighbouring gaps within a hair of each other)
    h = math.pi / zc
    big = 2 * (r_out + 1)
    wedge = BRepBuilderAPI_MakePolygon(gp_Pnt(0, 0, z0 - 1), gp_Pnt(-big * math.cos(h), -big * math.sin(h), z0 - 1),
                                       gp_Pnt(-big * math.cos(h), big * math.sin(h), z0 - 1), True).Wire()
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    wedge = BRepPrimAPI_MakePrism(BRepBuilderAPI_MakeFace(wedge, True).Face(), gp_Vec(0, 0, z1 - z0 + 2)).Shape()
    sector = cut(common(tube_z(z0, z1, r_in, r_out), wedge), gap)
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_Plane
    keep = []
    ex = TopExp_Explorer(sector, TopAbs_FACE)
    while ex.More():
        f = TopoDS.Face_s(ex.Current())
        ad = BRepAdaptor_Surface(f)
        side = False
        if ad.GetType() == GeomAbs_Plane:
            n = ad.Plane().Axis().Direction()
            side = abs(n.Z()) < 1e-9          # a sector plane (through the axis)
        if not side:
            keep.append(f)
        ex.Next()
    faces = [moved(f, rot_z(k * 360.0 / zc)) for k in range(zc) for f in keep]
    ring = sew_solid(faces, 1e-6)
    return one_solid(ring), gap


def face_gear_gap(zc, zp, m, r_in, r_out, z_root, z_tip_plane, cutter_thin, steps_per_pitch, window_pitches=1.6,
                  ext=0.15, dz=0.010):
    """gears.face_gear's cutter for one gap (centre on -x), kept to x in -(r_out + ext)..-(r_in - ext) and to
    z_tip_plane - dz .. z_root + dz: the solid the slices are taken from."""
    import gears as G
    pin = G.pinion_along_x(zp, m, -r_out - 0.3, -r_in + 0.3, 0.0, 0.0, thin=cutter_thin)
    pc = 2 * math.pi / zc
    poses = []
    n = int(window_pitches * steps_per_pitch * 2) + 1
    for phi in np.linspace(-window_pitches * pc, window_pitches * pc, n):
        psi = phi * zc / zp
        P = G.tf(pin, G.rot_axis([0, 0, 0], [1, 0, 0], psi))
        poses.append(P.rotate([0, 0, -math.degrees(phi)]))
    cutter = m3.Manifold.batch_boolean(poses, m3.OpType.Add)
    R = r_out + 1
    half = pc / 2
    wedge_pts = [(0, 0)] + [(-R * math.cos(t), -R * math.sin(t)) for t in np.linspace(-half, half, 16)]
    wedge = m3.Manifold.extrude(m3.CrossSection([wedge_pts], m3.FillRule.EvenOdd), 40).translate([0, 0, -20])
    keep = m3.Manifold.cube([r_out - r_in + 2 * ext, 2 * R, z_root - z_tip_plane + 2 * dz]).translate(
        [-(r_out + ext), -R, z_tip_plane - dz])
    return cutter ^ wedge ^ keep
