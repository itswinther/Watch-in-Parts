"""Mesh loading, rigid transforms, intersection volume, voxels. No spec numbers here."""
import struct
import numpy as np
import manifold3d as m3
from scipy import ndimage

SEG = 64


class FormatError(Exception):
    """A problem with a submitted file. The message states format facts only."""


# ---------- STL ----------
def read_stl(path, max_triangles, max_bytes):
    with open(path, "rb") as f:
        data = f.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise FormatError("file larger than %d bytes" % max_bytes)
    if len(data) < 84:
        raise FormatError("file too short to be an STL")
    n = struct.unpack_from("<I", data, 80)[0]
    if len(data) == 84 + 50 * n:                      # binary
        if n > max_triangles:
            raise FormatError("more than %d triangles" % max_triangles)
        rec = np.frombuffer(data, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]),
                            count=n, offset=84)
        tris = rec["v"].astype(np.float64)
    else:                                             # ASCII
        try:
            text = data.decode("ascii")
        except UnicodeDecodeError:
            raise FormatError("neither a binary STL of the declared length nor ASCII")
        vals = []
        for line in text.splitlines():
            p = line.split()
            if len(p) == 4 and p[0] == "vertex":
                vals.append((float(p[1]), float(p[2]), float(p[3])))
                if len(vals) > 3 * max_triangles:
                    raise FormatError("more than %d triangles" % max_triangles)
        if not vals or len(vals) % 3:
            raise FormatError("no complete triangles found")
        tris = np.array(vals, dtype=np.float64).reshape(-1, 3, 3)
    if len(tris) == 0:
        raise FormatError("no triangles")
    if not np.isfinite(tris).all():
        raise FormatError("non-finite vertex coordinate")
    return tris


def write_stl(path, man):
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties, dtype=np.float32)[:, :3]
    t = np.asarray(mesh.tri_verts)
    tris = v[t]
    nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    ln = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = np.where(ln > 0, nrm / np.where(ln > 0, ln, 1), 0)
    rec = np.zeros(len(tris), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
    rec["n"], rec["v"] = nrm, tris
    with open(path, "wb") as f:
        f.write(b"board-in-a-box".ljust(80, b" "))
        f.write(struct.pack("<I", len(tris)))
        f.write(rec.tobytes())


def raw_volume(tris):
    return float(np.einsum("ij,ij->i", tris[:, 0], np.cross(tris[:, 1], tris[:, 2])).sum() / 6.0)


def tris_to_manifold(tris):
    """Weld identical vertices and build a Manifold. Raises FormatError if not a closed manifold."""
    flat = tris.reshape(-1, 3).astype(np.float32)
    verts, inv = np.unique(flat, axis=0, return_inverse=True)
    faces = inv.reshape(-1, 3).astype(np.uint32)
    keep = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    faces = faces[keep]
    man = m3.Manifold(m3.Mesh(vert_properties=verts, tri_verts=faces))
    if man.status() != m3.Error.NoError:
        raise FormatError("mesh is not a closed manifold (%s)" % man.status().name)
    return man


def load_part(path, max_triangles, max_bytes, self_union_tol):
    """Returns a normalised Manifold or raises FormatError (gate G1)."""
    tris = read_stl(path, max_triangles, max_bytes)
    man = tris_to_manifold(tris)
    vol = man.volume()
    if not np.isfinite(vol) or vol <= 0:
        raise FormatError("volume is not positive")
    if len(man.decompose()) != 1:
        raise FormatError("more than one shell")
    norm = m3.Manifold.batch_boolean([man, man], m3.OpType.Add)
    rv = raw_volume(tris)
    for a in (norm.volume(), rv):
        if abs(a - vol) > self_union_tol * vol:
            raise FormatError("volume changes under self-union")
    return norm


# ---------- primitives ----------
def box(lo, hi):
    lo, hi = np.asarray(lo, float), np.asarray(hi, float)
    return m3.Manifold.cube(list(hi - lo)).translate(list(lo))


def cyl_z(cx, cy, z0, z1, r, seg=SEG):
    return m3.Manifold.cylinder(z1 - z0, r, r, seg).translate([cx, cy, z0])


def cyl_x(cy, cz, x0, x1, r, seg=SEG):
    c = m3.Manifold.cylinder(x1 - x0, r, r, seg)          # along +z
    return c.transform([[0, 0, 1, x0], [1, 0, 0, cy], [0, 1, 0, cz]])   # z->x, x->y, y->z


def union(parts):
    parts = [p for p in parts if p is not None]
    return m3.Manifold.batch_boolean(parts, m3.OpType.Add) if len(parts) > 1 else parts[0]


# ---------- rigid motion ----------
def apply(man, T):
    T = np.asarray(T, float)
    return man.transform(T[:3, :4].tolist())


def translation(d):
    T = np.eye(4)
    T[:3, 3] = d
    return T


def verts(man):
    return np.asarray(man.to_mesh().vert_properties, dtype=np.float64)[:, :3]


def bbox_overlap(a, b, pad=0.0):
    A, B = a.bounding_box(), b.bounding_box()
    return all(A[i] - pad < B[i + 3] and B[i] - pad < A[i + 3] for i in range(3))


def ivol(a, b):
    """Intersection volume, mm3."""
    if a.is_empty() or b.is_empty() or not bbox_overlap(a, b):
        return 0.0
    v = (a ^ b).volume()
    if not np.isfinite(v):
        raise ArithmeticError("non-finite volume")
    return float(v)


def min_distance(a, b, search):
    """Smallest surface-to-surface distance up to `search`; 0 if the solids overlap."""
    if ivol(a, b) > 1e-9:
        return 0.0
    return float(a.min_gap(b, search))


def section_x(man, x):
    """Cross-section on the plane X = x, returned in (y, z) coordinates."""
    return man.transform([[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]).slice(x)


# ---------- voxels ----------
def voxelize(man, origin, shape, h):
    """Boolean grid [nx, ny, nz]; a voxel is filled only when its centre is inside the solid."""
    nx, ny, nz = shape
    out = np.zeros(shape, dtype=bool)
    if man.is_empty():
        return out
    ox, oy, oz = origin
    yc = oy + (np.arange(ny) + 0.5) * h
    bb = man.bounding_box()
    for k in range(nz):
        z = oz + (k + 0.5) * h
        if z <= bb[2] or z >= bb[5]:
            continue
        polys = man.slice(z).to_polygons()
        if not polys:
            continue
        p1 = np.concatenate([np.asarray(p, float) for p in polys])
        p2 = np.concatenate([np.roll(np.asarray(p, float), -1, axis=0) for p in polys])
        y1, y2 = p1[:, 1][:, None], p2[:, 1][:, None]
        cross = ((y1 <= yc) & (yc < y2)) | ((y2 <= yc) & (yc < y1))
        e, j = np.nonzero(cross)
        if len(e) == 0:
            continue
        x = p1[e, 0] + (yc[j] - p1[e, 1]) * (p2[e, 0] - p1[e, 0]) / (p2[e, 1] - p1[e, 1])
        col = np.ceil((x - ox) / h - 0.5).astype(np.int64)
        col = np.clip(col, 0, nx)
        d = np.zeros((nx + 1, ny), dtype=np.int32)
        np.add.at(d, (col, j), 1)
        out[:, :, k] = (np.cumsum(d, axis=0)[:nx] % 2).astype(bool)
    return out


def grid_for(lo, hi, h, jitter):
    lo = np.asarray(lo, float) - jitter
    shape = tuple(int(v) for v in np.ceil((np.asarray(hi, float) - lo) / h).astype(int) + 1)
    return lo, shape


def edt(mask):
    """Distance, in voxels, from each True voxel to the nearest False voxel centre."""
    return ndimage.distance_transform_edt(mask)


def opening_test(solid, erode_vox, dilate_vox):
    """Returns (number of connected pieces of the opened solid, largest distance in
    voxels from a solid voxel to the opened solid). (0, inf) if nothing survives."""
    pad = np.pad(solid, 1)
    core = edt(pad) >= erode_vox
    if not core.any():
        return 0, float("inf")
    dist_to_core = edt(~core)
    opened = (dist_to_core <= dilate_vox) & pad
    _, n = ndimage.label(opened, structure=np.ones((3, 3, 3)))
    dev = edt(~opened)[pad].max()
    return int(n), float(dev)
