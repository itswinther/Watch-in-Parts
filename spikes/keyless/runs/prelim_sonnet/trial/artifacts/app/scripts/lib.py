import numpy as np, math, trimesh
from manifold3d import Manifold, CrossSection

SEG = 72

def poly_extrude(pts, z0, z1):
    cs = CrossSection([np.array(pts, dtype=float)])
    m = Manifold.extrude(cs, z1 - z0)
    return m.translate((0, 0, z0))

def circ(r, z0, z1, c=(0, 0), seg=SEG):
    return Manifold.cylinder(z1 - z0, r, r, seg).translate((c[0], c[1], z0))

def tube(ro, ri, z0, z1, c=(0, 0), seg=SEG):
    return circ(ro, z0, z1, c, seg) - circ(ri, z0 - 1, z1 + 1, c, seg)

def inv(a):
    return math.tan(a) - a

def gear2d(z, phi0_deg, m=0.2, pa=20.0, thin=0.03, add=1.0, ded=1.25, n=6):
    pa = math.radians(pa)
    rp = m * z / 2; rb = rp * math.cos(pa); ra = rp + add * m; rr = rp - ded * m
    dp = math.pi / (2 * z) - thin / (2 * rp)
    def delta(r):
        r = max(r, rb)
        return dp + inv(pa) - inv(math.acos(rb / r))
    pts = []
    for k in range(z):
        ck = math.radians(phi0_deg) + 2 * math.pi * k / z
        rs = [rr] + list(np.linspace(max(rr, rb), ra, n))
        for r in rs:
            a = ck - delta(r)
            pts.append((r * math.cos(a), r * math.sin(a)))
        a = ck
        pts.append((ra * math.cos(a), ra * math.sin(a)))  # tip center
        for r in reversed(rs):
            a = ck + delta(r)
            pts.append((r * math.cos(a), r * math.sin(a)))
        a = ck + math.pi / z
        pts.append((rr * math.cos(a), rr * math.sin(a)))
    # remove consecutive duplicates
    out = [pts[0]]
    for p in pts[1:]:
        if np.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > 1e-6:
            out.append(p)
    return out

def gear(z, phi0_deg, z0, z1, c=(0, 0), **kw):
    g = poly_extrude(gear2d(z, phi0_deg, **kw), z0, z1)
    return g.translate((c[0], c[1], 0))

def to_x_axis(m):
    # local (u,v,w) -> world (x=w, y=u, z=v)
    M = np.array([[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]], dtype=float)
    return m.transform(M)

def save(m, path):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(vertices=np.array(mesh.vert_properties)[:, :3], faces=np.array(mesh.tri_verts), process=False)
    t.export(path)
    return t

def load(path):
    t = trimesh.load(path)
    return Manifold(__import__('manifold3d').Mesh(vert_properties=np.array(t.vertices, dtype=np.float32), tri_verts=np.array(t.faces, dtype=np.uint32)))
