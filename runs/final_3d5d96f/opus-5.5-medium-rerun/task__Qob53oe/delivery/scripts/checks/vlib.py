"""Verification helpers: load parts exactly as the factory does, cache them, build bodies."""
import json, math, os, sys, hashlib
import numpy as np
sys.path.insert(0, "/app/tools")
import kernel
import manifold3d as m3

DEL = "/app/delivery"
CACHE = "/app/work/cache"
os.makedirs(CACHE, exist_ok=True)
ARGS = dict(max_bytes=16777216, max_triangles=200000, linear_deflection=0.001, angular_deflection=0.1,
            max_triangle_faces=500, timeout_s=120, memory_mb=4096, self_union_tol=0.005)


def _key(path):
    st = os.stat(path)
    return hashlib.md5(("%s-%d-%d" % (path, st.st_size, st.st_mtime_ns)).encode()).hexdigest()


def load_one(name):
    path = os.path.join(DEL, "parts", name + ".step")
    cp = os.path.join(CACHE, name + "-" + _key(path) + ".npz")
    if os.path.exists(cp):
        d = np.load(cp)
        return name, d["v"], d["f"]
    man = kernel.load_step_part(path, **ARGS)
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties, dtype=np.float64)[:, :3]
    f = np.asarray(mesh.tri_verts, dtype=np.int64)
    np.savez(cp, v=v, f=f)
    return name, v, f


def to_man(v, f):
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(v, np.float32), tri_verts=np.asarray(f, np.uint32)))


def load_parts(names, procs=12):
    from multiprocessing import Pool
    with Pool(procs) as pool:
        res = pool.map(load_one, names)
    return {n: to_man(v, f) for n, v, f in res}


def barrel(part_no):
    tris = kernel.read_stl("/app/supplied/%s.stl" % part_no, 10**7, 10**9)
    return kernel.tris_to_manifold(tris)


def rotz(man, ang, c):
    ca, sa = math.cos(ang), math.sin(ang)
    T = [[ca, -sa, 0, c[0] - ca * c[0] + sa * c[1]], [sa, ca, 0, c[1] - sa * c[0] - ca * c[1]], [0, 0, 1, 0]]
    return man.transform(T)


def rates(doc, period_h):
    """turns per hour (signed, + = clockwise seen from the dial) of every mobile."""
    r = {"barrel": 1.0 / period_h}
    changed = True
    while changed:
        changed = False
        for e in doc["meshes"]:
            a, b = e["driver"], e["driven"]
            if a in r and b not in r:
                r[b] = -r[a] * e["driver_teeth"] / e["driven_teeth"]; changed = True
            elif b in r and a not in r:
                r[a] = -r[b] * e["driven_teeth"] / e["driver_teeth"]; changed = True
    return r
