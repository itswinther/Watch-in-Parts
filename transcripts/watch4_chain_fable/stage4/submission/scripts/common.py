import sys, os, json, pickle
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import kernel
import manifold3d as m3
def movement():
    return json.load(open(os.path.join(ROOT, "work", "movement.json")))
def _load_one(n):
    c = os.path.join(ROOT, "cache", n + ".npy")
    if os.path.exists(c):
        return n
    tris = kernel.read_step(os.path.join(ROOT, "work", "parts", n + ".step"), 16777216, 200000, 0.001, 0.1, 500, 120, 4096)
    np.save(c, tris)
    return n
def load_all():
    doc = movement()
    names = list(doc["fixed"]) + [p for m in doc["mobiles"].values() for p in m["parts"]]
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(_load_one, names))
    parts = {n: kernel.tris_to_part(np.load(os.path.join(ROOT, "cache", n + ".npy")), 0.005) for n in names}
    parts["barrel"] = kernel.tris_to_manifold(kernel.read_stl(os.path.join(ROOT, "meshes", "barrel.stl"), 200000, 33554432))
    mob = {"barrel": "barrel"}
    for k, m in doc["mobiles"].items():
        for p in m["parts"]:
            mob[p] = k
    return doc, parts, mob
