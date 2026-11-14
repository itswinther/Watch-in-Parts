"""Interactive page for a mechanism whose mobiles turn about any axis (right-angle spike).

    python tools/viewer/export_axes.py SUBMISSION_DIR OUT.html --frozen spikes/right_angle/data/frozen \
        --title "GPT trial 1" [--details details.json]

SUBMISSION_DIR holds winding.json and parts/*.stl. The barrel arbor defaults to (0,0,0) along +z.
"""
import argparse, base64, json, os
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_AXES = {"arbor": ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0)), "stem": ((0.0, 0.0, -3.9), (1.0, 0.0, 0.0))}


def mesh(path):
    m = trimesh.load(path, force="mesh")
    return (base64.b64encode(np.asarray(m.vertices, np.float32).tobytes()).decode(),
            base64.b64encode(np.asarray(m.faces, np.uint32).tobytes()).decode(), int(len(m.faces)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sub"); ap.add_argument("out")
    ap.add_argument("--frozen"); ap.add_argument("--title", default="")
    ap.add_argument("--details")
    a = ap.parse_args()
    w = json.load(open(os.path.join(a.sub, "winding.json")))
    mobiles = {}
    for name, m in w.get("mobiles", {}).items():
        p, d = DEFAULT_AXES.get(name, ((0, 0, 0), (0, 0, 1)))
        mobiles[name] = {"point": m.get("point", p), "direction": m.get("direction", d), "parts": m["parts"]}
    # speeds: stem = 1 turn; driven = driver * zd/zn, sign by declared sense (as in grade.py)
    speed = {"stem": 1.0}
    for _ in range(len(w.get("meshes", [])) + 1):
        for me in w.get("meshes", []):
            if me["driver"] in speed and me["driven"] not in speed:
                s = 1.0 if me["sense"] == "same" else -1.0
                speed[me["driven"]] = speed[me["driver"]] * s * me["driver_teeth"] / me["driven_teeth"]
    owner = {p: n for n, m in mobiles.items() for p in m["parts"]}
    parts = []
    for f in sorted(os.listdir(os.path.join(a.sub, "parts"))):
        if f.endswith(".stl"):
            n = f[:-4]; pos, idx, t = mesh(os.path.join(a.sub, "parts", f))
            parts.append({"name": n, "mobile": owner.get(n), "frozen": False, "pos": pos, "idx": idx, "tris": t})
    if a.frozen:
        for f in sorted(os.listdir(a.frozen)):
            if f.endswith(".stl"):
                pos, idx, t = mesh(os.path.join(a.frozen, f))
                parts.append({"name": f[:-4], "mobile": None, "frozen": True, "pos": pos, "idx": idx, "tris": t})
    details = json.load(open(a.details)) if a.details and os.path.exists(a.details) else None
    data = {"title": a.title, "mobiles": mobiles, "speed": speed, "meshes": w.get("meshes", []),
            "fixed": w.get("fixed", []), "parts": parts,
            "reward": details.get("reward") if details else None,
            "checks": details.get("checks") if details else None}
    html = open(os.path.join(HERE, "axes_template.html")).read().replace("/*__DATA__*/null", json.dumps(data))
    open(a.out, "w").write(html)
    print(a.out, len(parts), "parts", sum(p["tris"] for p in parts), "tris", round(os.path.getsize(a.out) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
