"""NOT-FOR-AGENT (realcad test material; never copy into a task image).

Build a keyless submission and supplied-parts folder from Marco Lang's ml01 STEP (Zweigesicht-1).

    python -I convert_ml01.py EXTRACT_DIR OUT_DIR

EXTRACT_DIR is the output of extract_step.py (solids.json + brep/). OUT_DIR gets
    data/        main_plate, dial_plate, barrel_arbor, minute_wheel, minute_post (STL)
    sub/         keyless.json, parts/<name>.stl, report.json (all claims not_tested)
    parts.json   which CAD solid went where, with triangle counts

Frame: the CAD already has the stem along +x at y = 0 with the crown end at +x; the stem axis is at
z = -1.9, so everything is moved by +1.9 in z to put the stem axis on the grader's x axis.
Run it in Docker only (keyless-grade image). Nothing here is ever copied into a task image.
"""
import json
import math
import os
import sys

import numpy as np
import cadquery as cq
import manifold3d as m3
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import grade as G  # noqa: E402

DZ = 1.9
LIN_TOL, ANG_TOL = 0.003, 0.15
BORE_CLEAR = 0.004   # radial clearance cut into a mobile's own pivot bore (CAD fits are line-to-line;
                     # tessellated, a line-to-line fit overlaps by the chord sag)

# CAD solid ids (from extract_step.py on sha256 34f001d6...) -> expected product name prefix
MOBILES = {
    # name: (kind, ids, extra)
    "stem": ("stem", [67], {}),
    # The real sliding pinion is pushed into the winding pinion by the yoke spring, through the yoke.
    # The rig's springs never push other parts, so a spring acting through a link cannot be declared;
    # the closest the format allows is to declare both the yoke and the sliding pinion as sprung
    # towards winding (they then follow each other back, step by step). Limitation, see REAL_CAD.md.
    "sliding_pinion": ("spring", [68], {"dof": "slide", "direction": [1, 0, 0], "on_stem": True}),
    "winding_pinion": ("free", [12], {"dof": "rot", "point": [0, 0, 0], "direction": [1, 0, 0]}),
    "crown_wheel": ("free", [212], {"dof": "rot", "point": [10.92, 0.0, 0], "direction": [0, 0, 1]}),
    "click": ("spring", [220], {"dof": "rot", "point": [13.737, -3.70, 0], "direction": [0, 0, 1]}),
    # the setting-lever screw (116) is threaded into the lever (hole 0.665 < thread 0.70) and turns with it
    "setting_lever": ("free", [207, 208, 116], {"dof": "rot", "point": [15.75, 1.95, 0], "direction": [0, 0, 1]}),
    # screw 203 (threaded into the yoke) and pin 115 (riveted in the balance-stop plate, seated in the
    # yoke) move with the yoke; the balance-stop spring itself is not modelled
    "yoke": ("spring", [110, 203, 115], {"dof": "rot", "point": None, "direction": [0, 0, 1]}),
    "setting_wheel_lever": ("spring", [132], {"dof": "rot", "point": [9.401, -7.194, 0], "direction": [0, 0, 1]}),
    "setting_wheel": ("free", [108, 109], {"dof": "rot", "point": [9.58, 0.004, 0], "direction": [0, 0, 1],
                                           "carrier": "setting_wheel_lever"}),
    "barrel": ("barrel", [4], {}),
}
# endshake: the CAD has the winding pinion's face flat against the stem shoulder (coplanar faces give
# a tessellated overlap of about 1.3e-4 mm^3, inside the rig's touching tolerance of 2e-4 but above the
# 1e-4 target a pushed body must reach, so the pinion could never be pushed). Real endshake is about
# 0.01 to 0.02 mm; 0.005 mm is applied.
ENDSHAKE = {"winding_pinion": [-0.005, 0.0, 0.0]}
# spring sides (sign of the mobile's own coordinate its spring urges it to), from the geometry:
#   yoke: pivot (10, -11), fork at the sliding pinion: + turns the fork towards -x (setting); its spring
#         (an arm of the Winkelhebelfeder) holds it towards winding, so -1;
#   setting_wheel_lever: pivot (9.40, -7.19), wheel at (9.58, 0): + swings the wheel towards -x, into the
#         minute wheel; the Zeigerstellungsfeder holds it out, so -1;
#   click: pivot (13.74, -3.70); the click spring (Sperrfeder) presses it at about (14.2, -2.7), i.e. a
#         negative torque about +z, which swings the click tip into the crown-wheel teeth, so -1.
REST = {"sliding_pinion": 1, "yoke": -1, "setting_wheel_lever": -1, "click": -1}
SUPPLIED = {"main_plate": [139], "dial_plate": [196, 197, 198, 213, 214, 215, 180, 181, 184],
            "barrel_arbor": [5], "minute_wheel": [157, 158], "minute_post": [42]}
FIXED_SCREWS = [221, 133, 136, 137, 43, 202, 204, 205, 211, 219, 217, 222, 218, 56, 61, 62,
                128, 20, 175, 119]
EXPECT = {67: "Aufzugwelle", 68: "Kupplungstrieb", 12: "Kupplungsrad", 212: "Kronrad z45", 220: "Sperrklinke",
          207: "Winkelhebel", 110: "Kupplungshebel", 132: "Zeigerstellhebel", 108: "Zeigerstellrad",
          4: "Federhaustrommel I ", 5: "Federhausdeckel", 139: "Grundplatine", 196: "Aufzugsbr",
          213: "Kronradplatte", 180: "Federhausbr", 157: "Wechselrad1", 158: "Wechseltrieb1"}


def tess(brep):
    s = cq.Shape.importBrep(brep)
    vs, fs = s.tessellate(LIN_TOL, ANG_TOL)
    v = np.array([(p.x, p.y, p.z + DZ) for p in vs], float)
    f = np.array(fs, np.int64)
    m = trimesh.Trimesh(v, f, process=True)
    m.merge_vertices(digits_vertex=6)
    return m


def close_holes(m):
    """Close small boundary loops (a STEP solid that came in as an open shell) by fanning each loop
    from its centroid. Directed boundary edges are reversed so the patch faces outwards."""
    f = np.asarray(m.faces)
    de = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    s = set(map(tuple, de))
    bd = [e for e in map(tuple, de) if (e[1], e[0]) not in s]
    if not bd:
        return m
    nxt = {}
    for a, b in bd:
        nxt.setdefault(b, []).append(a)      # walk reversed edges
    V = [np.asarray(m.vertices)]
    F = [f]
    seen = set()
    nv = len(m.vertices)
    for a0 in list(nxt):
        if a0 in seen:
            continue
        loop, a = [], a0
        while a not in seen and a in nxt and nxt[a]:
            seen.add(a)
            loop.append(a)
            a = nxt[a].pop()
        if len(loop) < 3:
            continue
        c = m.vertices[loop].mean(axis=0)
        V.append(c[None])
        F.append(np.array([[loop[i], loop[(i + 1) % len(loop)], nv] for i in range(len(loop))]))
        nv += 1
    out = trimesh.Trimesh(np.concatenate(V), np.concatenate(F), process=True)
    out.merge_vertices(digits_vertex=6)
    print("closed holes:", len(bd), "boundary edges; watertight now", out.is_watertight, file=sys.stderr)
    return out


def to_man(m):
    tris = m.vertices[m.faces]
    try:
        return G.to_manifold(tris)
    except G.FormatError:
        m = close_holes(m)
        try:
            return G.to_manifold(m.vertices[m.faces])
        except G.FormatError:
            pass
        mesh = m3.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32))
        mesh.merge()
        man = m3.Manifold(mesh)
        if man.status() == m3.Error.NoError and man.volume() > 0:
            return man
        # last resort: voxel-free rebuild by trimesh's convex-safe split (report it)
        print("NOT MANIFOLD:", man.status().name, "watertight", m.is_watertight, file=sys.stderr)
        raise


def man_tris(man):
    me = man.to_mesh()
    v = np.asarray(me.vert_properties, float)[:, :3]
    return v[np.asarray(me.tri_verts)]


def write_stl(path, tris):
    tris = np.asarray(tris, np.float32)
    with open(path, "wb") as fo:
        fo.write(b"ml01 realcad test only, not for any task image".ljust(80, b" "))
        fo.write(np.uint32(len(tris)).tobytes())
        rec = np.zeros(len(tris), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]))
        rec["v"] = tris
        fo.write(rec.tobytes())


TO_X = [[0, 1, 0, 0], [0, 0, 1, 0], [1, 0, 0, 0]]     # (x, y, z) -> (y, z, x): the x axis becomes z
FROM_X = [[0, 0, 1, 0], [1, 0, 0, 0], [0, 1, 0, 0]]


def clear_bore(man, pt, axis="z"):
    """If the part has an empty bore through pt along axis ('z' or 'x'), widen it by BORE_CLEAR."""
    if axis == "x":
        out, info = clear_bore(man.transform(TO_X), [pt[1], pt[2], pt[0]], "z")
        return out.transform(FROM_X), info
    lo, hi = man.bounding_box()[2], man.bounding_box()[5]
    best = None
    for z in np.linspace(lo + 0.02, hi - 0.02, 9):
        for hx, hy, r in hole_centres(man, z):
            if math.hypot(hx - pt[0], hy - pt[1]) < 0.03 and (best is None or r < best):
                best = r
    if best is None:
        return man, None
    cyl = m3.Manifold.cylinder(hi - lo + 0.2, best, circular_segments=256).translate([pt[0], pt[1], lo - 0.1])
    inner = (man ^ m3.Manifold.cylinder(hi - lo + 0.2, best - 0.01, circular_segments=256)
             .translate([pt[0], pt[1], lo - 0.1])).volume()
    if inner > 1e-6:
        return man, {"bore_r": best, "skipped": "material inside the bore"}
    cut = m3.Manifold.cylinder(hi - lo + 0.2, best + BORE_CLEAR, circular_segments=256).translate([pt[0], pt[1], lo - 0.1])
    del cyl
    return man - cut, {"bore_r": round(best, 4), "widened_to": round(best + BORE_CLEAR, 4)}


def hole_centres(man, z):
    """Inner loops of the section of man at height z: (centre x, centre y, mean radius)."""
    cs = man.slice(z)
    out = []
    for poly in cs.to_polygons():
        p = np.asarray(poly)
        a = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
        if a < 0:   # clockwise: a hole
            c = p.mean(axis=0)
            out.append((round(float(c[0]), 4), round(float(c[1]), 4), round(float(np.linalg.norm(p - c, axis=1).mean()), 4)))
    return out


def main():
    ext, out = sys.argv[1], sys.argv[2]
    rows = {r["i"]: r for r in json.load(open(os.path.join(ext, "solids.json")))}
    for i, nm in EXPECT.items():
        assert nm in rows[i]["name"], (i, rows[i]["name"], nm)
    cache = {}

    def man_of(ids):
        ms = []
        for i in ids:
            if i not in cache:
                cache[i] = to_man(tess(os.path.join(ext, "brep", rows[i]["file"] + ".brep")))
            ms.append(cache[i])
        return G.union(ms)

    os.makedirs(os.path.join(out, "data"), exist_ok=True)
    os.makedirs(os.path.join(out, "sub", "parts"), exist_ok=True)
    log = {"supplied": {}, "mobiles": {}, "fixed": {}}
    for n, ids in SUPPLIED.items():
        man = man_of(ids)
        write_stl(os.path.join(out, "data", n + ".stl"), man_tris(man))
        log["supplied"][n] = {"ids": ids, "names": [rows[i]["name"] for i in ids], "tris": man.num_tri()}
    mobiles = {}
    for mn, (kind, ids, extra) in MOBILES.items():
        man = man_of(ids)
        if mn in ENDSHAKE:
            man = man.translate(ENDSHAKE[mn])
        pn = mn + "_p"
        write_stl(os.path.join(out, "sub", "parts", pn + ".stl"), man_tris(man))
        d = {"kind": kind, "parts": [pn]}
        d.update({k: v for k, v in extra.items()})
        if mn == "yoke":
            zmid = 0.5 * (rows[110]["bbox"][2] + rows[110]["bbox"][5]) + DZ
            holes = hole_centres(man, zmid)
            log["yoke_holes"] = holes
            # pivot: the hole farthest from the stem (the fork end is near the stem)
            hx, hy, _ = min(holes, key=lambda h: h[1])
            d["point"] = [hx, hy, 0.0]
        if kind == "spring":
            d["rest"] = REST[mn]
        if d.get("dof") == "rot":
            man, info = clear_bore(man, d["point"], "z" if d["direction"] == [0, 0, 1] else "x")
            log.setdefault("bores", {})[mn] = info
            write_stl(os.path.join(out, "sub", "parts", pn + ".stl"), man_tris(man))
        if mn == "setting_wheel_lever":     # the bore the setting wheel's arbor turns in
            sw = MOBILES["setting_wheel"][2]["point"]
            man, info = clear_bore(man, sw)
            log.setdefault("bores", {})["setting_wheel_lever@wheel"] = info
            write_stl(os.path.join(out, "sub", "parts", pn + ".stl"), man_tris(man))
        log["mobiles"][mn] = {"ids": ids, "names": [rows[i]["name"] for i in ids], "tris": man.num_tri(),
                              "holes_mid": hole_centres(man, 0.5 * (rows[ids[0]]["bbox"][2] + rows[ids[0]]["bbox"][5]) + DZ)}
        mobiles[mn] = d
    fixed = []
    for i in FIXED_SCREWS:
        pn = "fx_%03d" % i
        write_stl(os.path.join(out, "sub", "parts", pn + ".stl"), man_tris(man_of([i])))
        fixed.append(pn)
        log["fixed"][pn] = rows[i]["name"]
    spec = {"mobiles": mobiles, "fixed": fixed}
    json.dump(spec, open(os.path.join(out, "sub", "keyless.json"), "w"), indent=1)
    json.dump({"steps": {k: "not_tested" for k in ("assemble", "wind", "hold", "run", "backward", "set", "return")},
               "summary": "Marco Lang ml01 keyless works, converted from the published STEP; claims not made."},
              open(os.path.join(out, "sub", "report.json"), "w"))
    json.dump(log, open(os.path.join(out, "parts.json"), "w"), indent=1)
    print(json.dumps(log.get("bores")))


if __name__ == "__main__":
    main()
