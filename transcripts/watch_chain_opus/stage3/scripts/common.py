import json, os, sys, pickle
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import kernel

def load():
    doc = json.load(open(os.path.join(ROOT, "work", "movement.json")))
    parts, owner = {}, {}
    for n in doc["fixed"]:
        owner[n] = "__fixed__" + n
    for k, m in doc["mobiles"].items():
        for n in m["parts"]:
            owner[n] = k
    for n in owner:
        parts[n] = kernel.load_part(os.path.join(ROOT, "work", "parts", n + ".stl"), 200000, 33554432, 0.005)
    parts["barrel"] = kernel.load_part(os.path.join(ROOT, "meshes", "barrel.stl"), 200000, 33554432, 0.005)
    owner["barrel"] = "barrel"
    return doc, parts, owner

def total_bbox(parts):
    bbs = np.array([p.bounding_box() for p in parts.values()])
    return np.concatenate([bbs[:, :3].min(0), bbs[:, 3:].max(0)])
