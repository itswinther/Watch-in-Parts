"""Interactive "X-ray" demo page of a watch delivery: movement, dial and hands, for pitches and judges.

    python tools/viewer/export_watch_demo.py DELIVERY OUT.html [--keyless-trace TRACE.json]
        [--keyless-sub KEYLESS_SUBMISSION] [--keyless-supplied STL_DIR] [--tol 0.02] [--title ...]

DELIVERY is a job delivery folder (movement.json, variant_6h.json, parts/*.step), e.g. the output of
`python3 solution/reference_watch.py OUT --job`. A single stage folder with only movement.json works too.
Writes ONE self-contained HTML page: every part is tessellated and embedded; the only network request is
three.js r160 from cdn.jsdelivr.net.

Tessellating STEP needs CadQuery: run it in Docker (image `keyless-grade`), never on a crowded host, e.g.
    docker run --rm --memory 2g --cpus 2 -v $PWD:/w -w /w keyless-grade \
        python3 tools/viewer/export_watch_demo.py /w/out_job /w/demo.html

Speeds are exact fractions, computed the way the grader does (geometry/watch.py, Movement.speeds): the barrel
turns clockwise at 1/8 turn per hour in movement.json and 1/6 in variant_6h.json, and every declared mesh is
external, so it reverses the direction and multiplies the speed by driver teeth / driven teeth.

Keyless trace (optional second tab). Two formats are read:
  1. the simple documented format
       {"mobiles": {name: {"dof": "rot" | "slide" | "stem", "point": [x, y, z], "direction": [dx, dy, dz],
                           "carrier": other_mobile_or_null}},
        "frames": [{"t": seconds, "phase": "wind", "label": "...", "coords": {name: value or [values]}}]}
     rot: value is an angle in radians about `direction` through `point`; slide: a distance in mm along
     `direction`; stem: [angle, slide]. A mobile with a carrier is also turned with the carrier's angle.
  2. the keyless grader's trace (spikes/keyless/grade.py --trace): {"trace": {phase: [{"label", "q"}]}},
     with mobiles read from keyless.json in --keyless-sub (or next to the trace file).
With --keyless-sub (keyless.json + parts/*.stl) and --keyless-supplied (supplied STLs), the parts are drawn;
otherwise each mobile is drawn as a schematic disc or slider at its point.
The crown-to-hands link on the main tab is illustrative (kinematic) until the keyless works are joined to
the movement; the page says so.
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
sys.path.insert(0, ROOT)
BARREL_STL = os.path.join(ROOT, "geometry", "data", "barrel.stl")
try:                                     # the grader's numbers when the engine imports (it needs manifold3d)
    from geometry import watch as W
    BARREL_SPEED = {"movement": W.BARREL_TURNS_PER_HOUR, "variant_6h": W.CHANGED_BARREL_TURNS_PER_HOUR}
    FRAME_Z = {"plate": (-1.7, -0.3), "bridge": (5.0, 6.0), "dial": (8.8, 9.6)}
    CASE_RADIUS, CASE_HEIGHT = W.CASE_RADIUS, W.CASE_HEIGHT
    BARREL_WHEEL_Z, BARREL_ARBOR_Z, BARREL_ARBOR_R = W.BARREL_WHEEL_Z, W.BARREL_ARBOR_Z, W.BARREL_ARBOR_R
except Exception:                        # same values, stated in geometry/watch.py
    BARREL_SPEED = {"movement": Fraction(1, 8), "variant_6h": Fraction(1, 6)}
    FRAME_Z = {"plate": (-1.7, -0.3), "bridge": (5.0, 6.0), "dial": (8.8, 9.6)}
    CASE_RADIUS, CASE_HEIGHT = 20.7, 13.4
    BARREL_WHEEL_Z, BARREL_ARBOR_Z, BARREL_ARBOR_R = (0.0, 1.0), (-1.0, 1.6), 0.5
MOVEMENT_FILES = (("movement", "movement.json", "8-hour build"), ("variant_6h", "variant_6h.json", "6-hour variant"))
KEYLESS_STEM = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))        # the keyless task's fixed frame (spikes/keyless)
KEYLESS_BARREL = ((2.15, 4.157, 0.0), (0.0, 0.0, 1.0))
KEYLESS_MINUTE = ((4.65, -4.157, 0.0), (0.0, 0.0, 1.0))


def b64(a):
    return base64.b64encode(np.ascontiguousarray(a).tobytes()).decode("ascii")


def tessellate_step(path, tol):
    import cadquery as cq
    shape = cq.importers.importStep(path).val()
    verts, tris = shape.tessellate(tol, 0.3)
    return (np.array([(p.x, p.y, p.z) for p in verts], dtype=np.float32),
            np.array(tris, dtype=np.uint32).reshape(-1, 3))


def load_stl(path):
    import trimesh
    m = trimesh.load(path, force="mesh")
    return np.asarray(m.vertices, dtype=np.float32), np.asarray(m.faces, dtype=np.uint32)


def speeds(meshes, barrel_speed):
    """Movement.speeds of geometry/watch.py: clockwise turns per hour, every mesh reverses. Also the conflicts."""
    w = {"barrel": Fraction(barrel_speed)}
    conflicts, changed = [], True
    while changed:
        changed = False
        for m in meshes:
            a, ta, b, tb = m["driver"], m["driver_teeth"], m["driven"], m["driven_teeth"]
            for src, ts, dst, td in ((a, ta, b, tb), (b, tb, a, ta)):
                if src in w:
                    v = -w[src] * Fraction(ts, td)
                    if dst not in w:
                        w[dst] = v
                        changed = True
                    elif w[dst] != v and (src, dst) not in conflicts and (dst, src) not in conflicts:
                        conflicts.append((src, dst))
    return w, conflicts


def mesh_height(va, axa, ra, vb, axb, rb, module):
    """z range where both mobiles have material near their pitch circles, facing each other."""
    def zs(v, ax, r, other):
        if v is None or not len(v):
            return np.zeros(0)
        d = np.hypot(v[:, 0] - ax[0], v[:, 1] - ax[1])
        toward = math.atan2(other[1] - ax[1], other[0] - ax[0])
        a = np.arctan2(v[:, 1] - ax[1], v[:, 0] - ax[0])
        da = np.abs((a - toward + np.pi) % (2 * np.pi) - np.pi)
        sel = (d > r - 1.6 * module) & (d < r + 1.4 * module) & (da < 0.6)
        return v[sel, 2]
    za, zb = zs(va, axa, ra, axb), zs(vb, axb, rb, axa)
    if not len(za) or not len(zb):
        return None
    lo, hi = max(za.min(), zb.min()), min(za.max(), zb.max())     # tooth faces are flat: vertices sit on both faces
    return [float(lo), float(hi)] if hi > lo else None


def movement_data(doc, key, label, verts):
    sp, conflicts = speeds(doc.get("meshes", []), BARREL_SPEED[key])
    axes = {"barrel": [0.0, 0.0]}
    part_mobile = {}
    for name, mob in doc.get("mobiles", {}).items():
        axes[name] = [float(mob["axis"][0]), float(mob["axis"][1])]
        for p in mob["parts"]:
            part_mobile[p] = name
    by_mobile = {}
    for p, m in part_mobile.items():
        if p in verts:
            by_mobile.setdefault(m, []).append(verts[p])
    by_mobile = {m: np.concatenate(v) for m, v in by_mobile.items()}
    if "barrel" in verts:
        by_mobile["barrel"] = verts["barrel"]
    meshes = []
    for m in doc.get("meshes", []):
        a, b, za, zb = m["driver"], m["driven"], m["driver_teeth"], m["driven_teeth"]
        A, B = axes.get(a, [0, 0]), axes.get(b, [0, 0])
        d = math.dist(A, B)
        mod = 2 * d / (za + zb)
        z = mesh_height(by_mobile.get(a), A, mod * za / 2, by_mobile.get(b), B, mod * zb / 2, mod)
        if z is None and a == "barrel":
            z = list(BARREL_WHEEL_Z)
        meshes.append({"driver": a, "driven": b, "driver_teeth": za, "driven_teeth": zb, "centre_distance": d,
                       "module": mod, "z": z})
    return {"key": key, "label": label, "doc": doc, "axes": axes, "part_mobile": part_mobile, "meshes": meshes,
            "barrel_speed": [BARREL_SPEED[key].numerator, BARREL_SPEED[key].denominator],
            "speeds": {k: [v.numerator, v.denominator] for k, v in sp.items()},
            "conflicts": conflicts}


def keyless_data(trace_path, sub, supplied):
    raw = json.load(open(trace_path))
    kjson = None
    for cand in ([os.path.join(sub, "keyless.json")] if sub else []) + [os.path.join(os.path.dirname(trace_path), "keyless.json")]:
        if os.path.exists(cand):
            kjson = json.load(open(cand))
            break
    mobiles, frames = {}, []
    if "frames" in raw:                                    # the simple documented format
        for name, m in raw.get("mobiles", {}).items():
            mobiles[name] = {"dof": m.get("dof", "rot"), "point": m.get("point", [0, 0, 0]),
                             "dir": m.get("direction", m.get("dir", [0, 0, 1])), "carrier": m.get("carrier"),
                             "role": m.get("role", ""), "parts": m.get("parts", [])}
        for i, f in enumerate(raw["frames"]):
            c = f.get("coords", f.get("q", {}))
            frames.append({"t": f.get("t", i), "phase": f.get("phase", ""), "label": f.get("label", ""),
                           "q": {k: (v if isinstance(v, list) else [v]) for k, v in c.items()}})
    else:                                                  # the keyless grader's trace
        tr = raw.get("trace", raw)
        for phase, fr in tr.items():
            if not isinstance(fr, list):
                continue
            for f in fr:
                q = f.get("q", f.get("coords", {}))
                frames.append({"t": f.get("t", len(frames)), "phase": phase, "label": f.get("label", ""),
                               "q": {k: (v if isinstance(v, list) else [v]) for k, v in q.items()}})
        for name, m in ((kjson or {}).get("mobiles", {}) or {}).items():
            if name == "stem":
                mobiles[name] = {"dof": "stem", "point": KEYLESS_STEM[0], "dir": KEYLESS_STEM[1]}
            elif name == "barrel":
                mobiles[name] = {"dof": "rot", "point": KEYLESS_BARREL[0], "dir": KEYLESS_BARREL[1]}
            else:
                mobiles[name] = {"dof": m.get("dof", "rot"), "point": m.get("point", [0, 0, 0]),
                                 "dir": m.get("direction", [0, 0, 1]), "carrier": "stem" if m.get("on_stem") else None}
            mobiles[name]["parts"] = list(m.get("parts", []))
        if any("minute_wheel" in f["q"] for f in frames) and "minute_wheel" not in mobiles:
            mobiles["minute_wheel"] = {"dof": "rot", "point": KEYLESS_MINUTE[0], "dir": KEYLESS_MINUTE[1],
                                       "parts": ["minute_wheel"]}
        if "barrel" in mobiles and "barrel_arbor" not in mobiles["barrel"]["parts"]:
            mobiles["barrel"]["parts"].append("barrel_arbor")
    for f in frames:                                       # any mobile without a declaration: schematic, z axis
        for n, v in f["q"].items():
            if n not in mobiles:
                mobiles[n] = {"dof": "stem" if len(v) == 2 else "rot", "point": [0, 0, 0], "dir": [0, 0, 1]}
    for m in mobiles.values():
        m.setdefault("carrier", None)
        m.setdefault("parts", [])
        m.setdefault("role", "")
    owner = {p: n for n, m in mobiles.items() for p in m["parts"]}
    parts = []
    dirs = [(os.path.join(sub, "parts"), False)] if sub and os.path.isdir(os.path.join(sub, "parts")) else []
    if supplied and os.path.isdir(supplied):
        dirs.append((supplied, True))
    for d, is_supplied in dirs:
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if f.endswith(".stl") and not os.path.islink(p):
                v, t = load_stl(p)
                n = f[:-4]
                parts.append({"name": n, "mobile": owner.get(n),
                              "ghost": is_supplied and n in ("main_plate", "dial_plate"), "pos": b64(v), "idx": b64(t)})
    return {"mobiles": mobiles, "frames": frames, "parts": parts, "source": os.path.basename(trace_path)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("delivery")
    ap.add_argument("out_html")
    ap.add_argument("--keyless-trace", default=None, help="recorded keyless simulation (see the formats above)")
    ap.add_argument("--keyless-sub", default=None, help="keyless submission folder: keyless.json and parts/*.stl")
    ap.add_argument("--keyless-supplied", default=None, help="folder of the keyless task's supplied STLs")
    ap.add_argument("--tol", type=float, default=0.02, help="tessellation tolerance, mm (page size vs. smoothness)")
    ap.add_argument("--title", default=None)
    a = ap.parse_args()

    docs = []
    for key, fname, label in MOVEMENT_FILES:
        p = os.path.join(a.delivery, fname)
        if os.path.exists(p):
            docs.append((key, label, json.load(open(p))))
    if not docs:
        sys.exit(f"no movement.json in {a.delivery}")
    names = []
    for _, _, d in docs:
        for n in list(d.get("fixed", [])) + [p for m in d.get("mobiles", {}).values() for p in m["parts"]]:
            if n not in names:
                names.append(n)
    verts, parts = {}, []
    for i, n in enumerate(names):
        path = os.path.join(a.delivery, "parts", n + ".step")
        if not os.path.exists(path):
            print(f"missing part file {path}", file=sys.stderr)
            continue
        v, f = tessellate_step(path, a.tol)
        verts[n] = v
        print(f"[{i + 1}/{len(names)}] {n}: {len(f)} triangles", file=sys.stderr)
        parts.append({"name": n, "zmin": float(v[:, 2].min()), "zmax": float(v[:, 2].max()),
                      "tris": int(len(f)), "pos": b64(v), "idx": b64(f)})
    if os.path.exists(BARREL_STL):
        v, f = load_stl(BARREL_STL)
        verts["barrel"] = v
        parts.append({"name": "barrel", "zmin": float(v[:, 2].min()), "zmax": float(v[:, 2].max()),
                      "tris": int(len(f)), "pos": b64(v), "idx": b64(f), "supplied": True})

    movements = [movement_data(d, key, label, verts) for key, label, d in docs]
    for m in movements:
        m["part_mobile"]["barrel"] = "barrel"
        for mm in m["meshes"]:
            print(f"{m['key']}: {mm['driver']} {mm['driver_teeth']} -> {mm['driven']} {mm['driven_teeth']}"
                  f" at z {mm['z']}, speed {m['speeds'].get(mm['driven'])}", file=sys.stderr)
    keyless = None
    if a.keyless_trace:
        if os.path.exists(a.keyless_trace):
            keyless = keyless_data(a.keyless_trace, a.keyless_sub, a.keyless_supplied)
            print(f"keyless trace: {len(keyless['frames'])} frames, {len(keyless['mobiles'])} mobiles", file=sys.stderr)
        else:
            print(f"keyless trace {a.keyless_trace} not found: no keyless tab", file=sys.stderr)
    data = {
        "title": a.title or "Watch movement: X-ray demo",
        "source": os.path.basename(os.path.normpath(a.delivery)),
        "movements": movements, "parts": parts, "keyless": keyless,
        "frame_z": FRAME_Z, "case": {"radius": CASE_RADIUS, "height": CASE_HEIGHT},
        "barrel": {"wheel_z": list(BARREL_WHEEL_Z), "arbor_z": list(BARREL_ARBOR_Z), "arbor_r": BARREL_ARBOR_R},
    }
    tpl = open(os.path.join(HERE, "watch_demo_template.html")).read()
    html = tpl.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":")))
    with open(a.out_html, "w") as fh:
        fh.write(html)
    print(f"wrote {a.out_html}: {len(parts)} parts, {sum(p['tris'] for p in parts)} triangles, "
          f"{os.path.getsize(a.out_html) / 1e6:.1f} MB", file=sys.stderr)


if __name__ == "__main__":
    main()
