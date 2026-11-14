"""Interactive page for a keyless-works submission (general axes, sliding parts, supplied parts see-through).

    python tools/viewer/export_keyless.py SUBMISSION_DIR OUT.html --supplied spikes/keyless/data \
        [--details details.json] [--title "Sonnet trial 3"]

Uses tools/viewer/axes_template.html. Turning speeds per stem turn come from the grader's details when
given (barrel from AT-1); other mobiles are drawn at rest. Sliding mobiles are drawn in position 1.
"""
import argparse, base64, json, os
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
STEM = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0))
BARREL = ((2.15, 4.157, 0.0), (0.0, 0.0, 1.0))
MINUTE = ((4.65, -4.157, 0.0), (0.0, 0.0, 1.0))


def mesh(path):
    m = trimesh.load(path, force="mesh")
    return (base64.b64encode(np.asarray(m.vertices, np.float32).tobytes()).decode(),
            base64.b64encode(np.asarray(m.faces, np.uint32).tobytes()).decode(), int(len(m.faces)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sub"); ap.add_argument("out")
    ap.add_argument("--supplied"); ap.add_argument("--title", default="")
    ap.add_argument("--details")
    a = ap.parse_args()
    k = json.load(open(os.path.join(a.sub, "keyless.json")))
    mobiles = {}
    for name, m in k.get("mobiles", {}).items():
        if name == "stem":
            p, d = STEM
        elif name == "barrel":
            p, d = BARREL
        else:
            p = m.get("point", (0, 0, 0)) if m.get("dof") == "rot" else (0, 0, 0)
            d = m.get("direction", (0, 0, 1))
        mobiles[name] = {"point": list(p), "direction": list(d), "parts": m.get("parts", [])}
    mobiles["minute_wheel"] = {"point": list(MINUTE[0]), "direction": list(MINUTE[1]), "parts": ["minute_wheel"]}
    details = json.load(open(a.details)) if a.details and os.path.exists(a.details) else None
    speed = {"stem": -1.0}                                  # forward winding: negative about +x
    try:
        r = details["details"]["sequence"]["wind"]["crown_turns_per_barrel_turn"]
        speed["barrel"] = 1.0 / r if r else 0.0
    except Exception:  # noqa: BLE001
        pass
    owner = {p: n for n, m in mobiles.items() for p in m["parts"]}
    parts = []
    pdir = os.path.join(a.sub, "parts")
    for f in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
        if f.endswith(".stl") and not os.path.islink(os.path.join(pdir, f)):
            n = f[:-4]
            try:
                pos, idx, t = mesh(os.path.join(pdir, f))
            except Exception:  # noqa: BLE001
                continue
            parts.append({"name": n, "mobile": owner.get(n), "frozen": False, "pos": pos, "idx": idx, "tris": t})
    if a.supplied:
        for f in sorted(os.listdir(a.supplied)):
            if f.endswith(".stl"):
                n = f[:-4]
                pos, idx, t = mesh(os.path.join(a.supplied, f))
                parts.append({"name": n, "mobile": owner.get(n) if n == "minute_wheel" else None,
                              "frozen": n != "minute_wheel", "pos": pos, "idx": idx, "tris": t})
    data = {"title": a.title, "mobiles": mobiles, "speed": speed, "meshes": [], "fixed": k.get("fixed", []),
            "parts": parts, "reward": details.get("reward") if details else None,
            "checks": details.get("at") if details else None}
    html = open(os.path.join(HERE, "axes_template.html")).read().replace("/*__DATA__*/null", json.dumps(data))
    open(a.out, "w").write(html)
    print(a.out, len(parts), "parts", sum(p["tris"] for p in parts), "tris", round(os.path.getsize(a.out) / 1e6, 1), "MB")


if __name__ == "__main__":
    main()
