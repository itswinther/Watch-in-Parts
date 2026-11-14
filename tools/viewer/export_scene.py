"""Turn one graded watch stage into a self-contained interactive viewer page.

    python tools/viewer/export_scene.py STAGE_DIR OUT.html [--tol 0.01]

STAGE_DIR holds `submission/` (movement.json, parts/*.step, optional assembly.json)
and optionally the grader's `details.json`. For a packed chain in `transcripts/`,
unpack it first: `python3 tests/pack_run.py --unpack transcripts/watch4_chain_opus OUT`.

Needs cadquery and trimesh (the Junction uv env has both). The page loads three.js
from jsdelivr, so open it on the host, not inside a sandbox.
"""
import argparse
import base64
import json
import math
import os
import sys
from fractions import Fraction

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BARREL_STL = os.path.join(ROOT, "geometry", "data", "barrel.stl")
BARREL_TURNS_PER_HOUR = {1: Fraction(1, 8), 2: Fraction(1, 8), 3: Fraction(1, 6), 4: Fraction(1, 6)}


def tessellate_step(path, tol):
    import cadquery as cq
    shape = cq.importers.importStep(path).val()
    verts, tris = shape.tessellate(tol, 0.25)
    v = np.array([(p.x, p.y, p.z) for p in verts], dtype=np.float32)
    f = np.array(tris, dtype=np.uint32).reshape(-1, 3)
    return v, f


def load_stl(path):
    import trimesh
    m = trimesh.load(path, force="mesh")
    return np.asarray(m.vertices, dtype=np.float32), np.asarray(m.faces, dtype=np.uint32)


def b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode("ascii")


def role_of(name, fixed):
    n = name.lower()
    if name in fixed:
        return "fixed"
    for key, role in (("hand", "hand"), ("pinion", "pinion"), ("arbor", "arbor"), ("tube", "arbor"),
                      ("post", "arbor"), ("cap", "fixed"), ("wheel", "wheel")):
        if key in n:
            return role
    return "other"


def speeds(movement, barrel_speed):
    """Turns per hour, clockwise positive, through the declared meshes (external meshes reverse)."""
    sp = {"barrel": Fraction(barrel_speed)}
    meshes = movement.get("meshes", [])
    for _ in range(len(meshes) + 2):
        for m in meshes:
            a, b = m["driver"], m["driven"]
            if a in sp and b not in sp:
                sp[b] = -sp[a] * Fraction(m["driver_teeth"], m["driven_teeth"])
    return sp


def downsample(path, n=24):
    if len(path) <= n:
        return path
    idx = np.linspace(0, len(path) - 1, n).round().astype(int)
    return [path[i] for i in idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage_dir")
    ap.add_argument("out_html")
    ap.add_argument("--tol", type=float, default=0.01, help="tessellation tolerance, mm")
    ap.add_argument("--stage", type=int, default=None, help="stage number (sets barrel speed); read from folder name if omitted")
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    sub = os.path.join(args.stage_dir, "submission")
    if not os.path.isdir(sub):
        sub = args.stage_dir
    movement = json.load(open(os.path.join(sub, "movement.json")))
    details_path = os.path.join(args.stage_dir, "details.json")
    details = json.load(open(details_path)) if os.path.exists(details_path) else None
    # Stage 4 grades assembly only; take the train margins from the previous stage's details.
    train_details = details
    if not (details and details.get("details", {}).get("train")):
        base = os.path.normpath(args.stage_dir)
        if base[-1:].isdigit():
            prev = os.path.join(os.path.dirname(base), os.path.basename(base)[:-1] + str(int(base[-1]) - 1), "details.json")
            if os.path.exists(prev):
                train_details = json.load(open(prev))
    asm_path = os.path.join(sub, "assembly.json")
    assembly = json.load(open(asm_path)) if os.path.exists(asm_path) else None

    stage = args.stage
    if stage is None:
        base = os.path.basename(os.path.normpath(args.stage_dir))
        stage = int(base[-1]) if base[-1:].isdigit() else 1
    sp = speeds(movement, BARREL_TURNS_PER_HOUR.get(stage, Fraction(1, 8)))

    fixed = list(movement.get("fixed", []))
    part_mobile = {}
    axes = {"barrel": [0.0, 0.0]}
    for mname, mob in movement.get("mobiles", {}).items():
        axes[mname] = mob["axis"]
        for p in mob["parts"]:
            part_mobile[p] = mname

    parts = []
    names = [n[:-5] for n in sorted(os.listdir(os.path.join(sub, "parts"))) if n.endswith(".step")]
    for i, name in enumerate(names):
        v, f = tessellate_step(os.path.join(sub, "parts", name + ".step"), args.tol)
        print(f"[{i + 1}/{len(names)}] {name}: {len(f)} triangles", file=sys.stderr)
        r = float(np.max(np.hypot(v[:, 0] - axes.get(part_mobile.get(name), [0, 0])[0],
                                  v[:, 1] - axes.get(part_mobile.get(name), [0, 0])[1]))) if len(v) else 0.0
        parts.append({"name": name, "mobile": part_mobile.get(name), "role": role_of(name, fixed),
                      "zmin": float(v[:, 2].min()), "zmax": float(v[:, 2].max()), "rmax": r,
                      "tris": int(len(f)), "pos": b64(v), "idx": b64(f)})
    if os.path.exists(BARREL_STL):
        v, f = load_stl(BARREL_STL)
        parts.append({"name": "barrel", "mobile": "barrel", "role": "supplied",
                      "zmin": float(v[:, 2].min()), "zmax": float(v[:, 2].max()),
                      "rmax": float(np.max(np.hypot(v[:, 0], v[:, 1]))),
                      "tris": int(len(f)), "pos": b64(v), "idx": b64(f)})

    # Gear pairs: module from the centre distance, face width from the part on each mobile
    # whose outer radius best matches the pitch radius.
    by_mobile = {}
    for p in parts:
        by_mobile.setdefault(p["mobile"], []).append(p)
    mesh_info = []
    train_checks = {}
    if train_details and isinstance(train_details.get("details", {}).get("train"), dict):
        for t in train_details["details"]["train"].get("meshes", []):
            train_checks[t.get("pair")] = t
    for m in movement.get("meshes", []):
        a, b = m["driver"], m["driven"]
        za, zb = m["driver_teeth"], m["driven_teeth"]
        d = math.dist(axes.get(a, [0, 0]), axes.get(b, [0, 0]))
        mod = 2 * d / (za + zb) if za + zb else 0.0
        ra, rb = mod * za / 2, mod * zb / 2

        def gear_part(mob, r):
            cands = [p for p in by_mobile.get(mob, []) if p["role"] in ("wheel", "pinion", "supplied", "other")]
            if not cands:
                return None
            return min(cands, key=lambda p: abs(p["rmax"] - (r + mod)))

        pa, pb = gear_part(a, ra), gear_part(b, rb)
        face = min([x["zmax"] - x["zmin"] for x in (pa, pb) if x] or [0.0])
        if a == "barrel":
            face = 1.0
        mesh_info.append({"driver": a, "driven": b, "driver_teeth": za, "driven_teeth": zb,
                          "centre_distance": d, "module": mod, "driver_pitch_r": ra, "driven_pitch_r": rb,
                          "driver_part": pa and pa["name"], "driven_part": pb and pb["name"], "face_width": face,
                          "grader": train_checks.get(f"{a}/{b}")})

    sec = (movement.get("hands", {}).get("seconds") or {}).get("mobile")
    parent = {}
    for m in movement.get("meshes", []):
        parent.setdefault(m["driven"], m["driver"])
    going = set()
    node = sec
    while node and node != "barrel" and node in parent:
        going.add((parent[node], node))
        node = parent[node]
    for mi in mesh_info:
        mi["going_train"] = (mi["driver"], mi["driven"]) in going

    data = {
        "title": args.title or os.path.normpath(args.stage_dir),
        "stage": stage,
        "movement": movement,
        "speeds": {k: [v.numerator, v.denominator] for k, v in sp.items()},
        "axes": axes,
        "parts": parts,
        "meshes": mesh_info,
        "details": details,
        "assembly": None if not assembly else {
            "order": assembly.get("order", []),
            "paths": {k: downsample(v) for k, v in assembly.get("paths", {}).items()},
        },
        "limits": {"case_radius": 20.7, "case_height": 13.4, "engage_gap": 0.1, "drive_overlap": 0.01},
    }
    tpl = open(os.path.join(HERE, "viewer_template.html")).read()
    html = tpl.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    with open(args.out_html, "w") as fh:
        fh.write(html)
    tris = sum(p["tris"] for p in parts)
    print(f"wrote {args.out_html}: {len(parts)} parts, {tris} triangles, {os.path.getsize(args.out_html) / 1e6:.1f} MB",
          file=sys.stderr)


if __name__ == "__main__":
    main()
