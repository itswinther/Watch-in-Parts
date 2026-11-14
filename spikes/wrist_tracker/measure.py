"""Quick 'does it make sense' measurements for the child's wrist tracker spike.
Bands are rough and generous; this is a spike, not a grader."""
import glob
import json
import os
import sys

import numpy as np
import trimesh
from scipy import ndimage

PARTS = {p["id"]: p for p in json.load(open(os.path.join(os.path.dirname(__file__), "kit", "parts.json")))["parts"]}
PART_MASS = sum(p["mass"] for p in PARTS.values())


def band(x, full, zero):
    """1.0 up to `full`, falling linearly to 0 at `zero`."""
    return float(np.clip((zero - x) / (zero - full), 0, 1))


def main(folder):
    out = {}
    files = sorted(glob.glob(os.path.join(folder, "out", "*.stl")))
    if not files:
        return {"error": "no STL files"}
    meshes = [trimesh.load(f, force="mesh") for f in files]
    out["files"] = [os.path.basename(f) for f in files]
    out["watertight"] = [bool(m.is_watertight) for m in meshes]
    allv = np.vstack([m.vertices for m in meshes])
    lo, hi = allv.min(0), allv.max(0)
    dims = hi - lo
    out["bbox_xyz"] = [round(float(d), 1) for d in dims]
    t, w, l = sorted(dims)
    out["thickness"], out["width"], out["length"] = round(float(t), 1), round(float(w), 1), round(float(l), 1)
    vol = sum(abs(m.volume) for m in meshes)
    out["printed_mass_g"] = round(vol * 1.2 / 1000, 1)
    out["total_mass_g"] = round(out["printed_mass_g"] + PART_MASS, 1)

    # layout: every part present, right size, no overlaps, not inside printed material
    lay_path = os.path.join(folder, "out", "layout.json")
    lay_ok, notes, boxes = True, [], {}
    try:
        lay = json.load(open(lay_path))
        lay = lay.get("parts", lay)
        if isinstance(lay, list):
            lay = {e["id"]: e for e in lay}
        for pid, p in PARTS.items():
            e = lay.get(pid)
            if e is None:
                lay_ok = False
                notes.append("missing " + pid)
                continue
            if isinstance(e, dict):
                mn = np.array(e.get("min") or e.get("min_corner") or e.get("position"), float)
                sz = np.array(e.get("size"), float)
            else:
                mn, sz = np.array(e[0], float), np.array(e[1], float)
            if not np.allclose(sorted(sz), sorted(p["size"]), atol=0.05):
                lay_ok = False
                notes.append("%s size %s is not %s" % (pid, sz.tolist(), p["size"]))
            boxes[pid] = (mn, mn + sz)
        ids = list(boxes)
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                a, b = boxes[ids[i]], boxes[ids[j]]
                ov = np.minimum(a[1], b[1]) - np.maximum(a[0], b[0])
                if np.all(ov > 0.05):
                    lay_ok = False
                    notes.append("%s overlaps %s" % (ids[i], ids[j]))
    except Exception as ex:
        lay_ok = False
        notes.append("layout.json unreadable: %s" % type(ex).__name__)

    # voxel model: printed solid + parts, then flood from outside
    pitch = 0.4
    pad = 3
    shape = np.ceil(dims / pitch).astype(int) + 2 * pad
    origin = lo - pad * pitch
    idx = np.indices(shape).reshape(3, -1).T
    centres = origin + (idx + 0.5) * pitch
    solid = np.zeros(len(centres), bool)
    for m in meshes:
        if m.is_watertight:
            solid |= m.contains(centres)
    solid = solid.reshape(shape)
    partv = np.zeros(shape, bool)
    clash = {}
    for pid, (a, b) in boxes.items():
        inside = np.all((centres > a + 0.2) & (centres < b - 0.2), axis=1).reshape(shape)
        clash[pid] = int((inside & solid).sum())
        partv |= np.all((centres > a) & (centres < b), axis=1).reshape(shape)
        if np.any(a < lo - 0.05) or np.any(b > hi + 0.05):
            notes.append("%s sticks out of the case" % pid)
    bad = {k: v for k, v in clash.items() if v * pitch ** 3 > 2.0}
    if bad:
        lay_ok = False
        notes.append("parts inside printed material (voxels): %s" % bad)
    out["parts_fit"] = lay_ok
    out["fit_notes"] = notes

    empty = ~(solid | partv)
    # openings wider than ~1.2 mm let the outside in: erode the empty space by 1 voxel first
    lab, n = ndimage.label(ndimage.binary_erosion(empty, iterations=1))
    outside = lab == lab[0, 0, 0]
    inner_air = empty & ~ndimage.binary_dilation(outside, iterations=2)
    reach = ndimage.binary_dilation(outside, iterations=2)
    exposed = {}
    for pid, (a, b) in boxes.items():
        pv = np.all((centres > a) & (centres < b), axis=1).reshape(shape)
        shell = ndimage.binary_dilation(pv, iterations=1) & ~pv
        exposed[pid] = round(float((shell & reach & ~solid).sum()) * pitch ** 2, 1)
    out["exposed_area_mm2_by_part"] = exposed
    out["sealed_air_cm3"] = round(float(inner_air.sum()) * pitch ** 3 / 1000, 2)

    # how much of the outside is rounded or sloped rather than flat-and-square
    normals = np.vstack([m.face_normals for m in meshes])
    areas = np.concatenate([m.area_faces for m in meshes])
    axis = np.max(np.abs(normals), axis=1) > 0.996
    out["non_axis_surface_share"] = round(float(areas[~axis].sum() / areas.sum()), 2)

    # generous bands for a 6-10 year old's wrist (wrist breadth roughly 38-45 mm)
    s = {
        "thickness (full <=13, zero at 20)": band(t, 13, 20),
        "width across wrist (full <=40, zero at 55)": band(w, 40, 55),
        "total mass (full <=30 g, zero at 60 g)": band(out["total_mass_g"], 30, 60),
    }
    out["size_scores"] = {k: round(v, 2) for k, v in s.items()}
    return out


if __name__ == "__main__":
    print(json.dumps(main(sys.argv[1]), indent=1))
