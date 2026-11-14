"""A test delivery for Part 5 (crown winding): the one-job reference plus workstream A's keyless v1 reference, scaled
by S and placed rigidly by solution/fit_keyless.py, as a `keyless` section; and a runner that grades its Part 5.
Not a reference: A's v1 does not fit B's frame rigidly (builder K's fitting pass); this exercises the P5 adapter.

    python3 solution/keyless_v1_delivery.py build /abs/REF_JOB /abs/OUT [--layout under|above|below] [--diag]
    python3 solution/keyless_v1_delivery.py grade /abs/OUT [--force] [--jobs N] [--work /abs/DIR]

build: REF_JOB is `python3 solution/reference_watch.py REF_JOB --job`. OUT gets a copy of it with, in movement.json,
  - the centre mobile split: `centre` (the centre wheel) and `cannon` (cannon pinion and minute hand,
    "friction_on": "centre"); the cannon pinion's mesh with the minute wheel and hands.minute name `cannon`;
  - A's v1 fixed parts (stem bridge, stem guide, posts) added to `fixed` (also in variant_6h.json: the same frame);
  - a `keyless` section: A's stem, its `barrel` parts on the supplied arbor (`arbor`), and A's other mobiles with
    their kind, dof, point, direction, rest and on_stem mapped into B's frame.
  Layout (fit_keyless.py section 1, the flipped placements, which wind the arbor clockwise seen from +z as B's
  barrel requires): `under` (default) puts A's ratchet stack under the bridge, on the arbor's square; `above` and
  `below` are the other two. A's parts are meshes; a STEP file of a mesh has one face per triangle and the loader
  rejects it, so each keyless part file is a placeholder and its solid is written to OUT_solids/<name>.stl.
  --diag (for tracing failures past AT-0): without A's setting wheel and its post (in the `under` layout they cut
  into B's dial and mesh nothing of B's motion work) and with the ratchet stack cut at DIAG_CUT_Z, below B's bridge.
grade: loads OUT's movement.json with the part cache primed with those solids (key: name and the placeholder's
  bytes, as geometry/watch.py's cache keys them) and runs tests/grade_watch.py grade_keyless_part (Part 5 only,
  whatever KEYLESS_IN_JOB says). --force runs AT-1 to AT-6 even if the rest gate fails (diagnosis). Prints and
  writes OUT_p5.json."""
import hashlib
import json
import os
import shutil
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "solution"))
sys.path.insert(0, os.path.join(ROOT, "tests"))


def _placeholder(name):
    return ("placeholder for the keyless test part %s; its solid is in the _solids folder\n" % name).encode()


DIAG_CUT_Z = 4.99      # --diag: the ratchet stack is cut here (B's bridge starts at z 5.0)


def build(ref, out, layout="under", diag=False):
    import fit_keyless as F
    from geometry import core
    if os.path.exists(out):
        raise SystemExit("%s exists" % out)
    shutil.copytree(ref, out)
    with open(os.path.join(out, "movement.json")) as f:
        doc = json.load(f)
    cc = tuple(doc["case_centre"])
    R = F._import_keyless("reference")
    C = F._import_keyless("constants")
    F.A_BARREL = C.BARREL_AXIS
    parts_a, spec = R.build()
    bx, by = C.BARREL_AXIS
    za = parts_a["barrel_wheel"].bounding_box()
    stack = (za[2], za[5])
    flip = True
    phi = F.radial_angle(cc, flip)
    a, b = -F.S * stack[1], -F.S * stack[0]           # the ratchet stack's z relative to z0 (flipped)
    z0 = {"under": 3.25 + (4.95 - 3.25 - F.S * (stack[1] - stack[0])) / 2 - a, "below": -1.75 - b,
          "above": 6.05 - a}[layout]
    z0 = round(z0, 3)
    pl = F.Place(phi, flip, z0, bx, by)
    kp = {n: pl.man(m) for n, m in parts_a.items()}
    kp, shift = F.shorten_stem(kp, pl, cc)
    if diag:        # tracing variant: no setting train (it meshes nothing of B's), ratchet stack cut below the bridge
        import manifold3d as m3
        for n in ("setting_wheel", "setting_post"):
            kp.pop(n)
        spec = json.loads(json.dumps(spec))
        spec["mobiles"].pop("setting_wheel")
        spec["fixed"].remove("setting_post")
        bb = kp["barrel_wheel"].bounding_box()
        keep = m3.Manifold.cube([bb[3] - bb[0] + 2, bb[4] - bb[1] + 2, DIAG_CUT_Z - bb[2] + 1]).translate(
            [bb[0] - 1, bb[1] - 1, bb[2] - 1])
        kp["barrel_wheel"] = kp["barrel_wheel"] ^ keep
    # the keyless section, A's keyless.json mapped into B's frame (Place is a rotation and a scale: rest signs keep)
    mobs = {}
    for mn, mob in spec["mobiles"].items():
        if mn in ("stem", "barrel"):
            continue
        e = {"kind": mob["kind"], "dof": mob["dof"], "parts": mob["parts"],
             "direction": [round(float(v), 9) for v in pl.vec(mob["direction"])]}
        if mob["dof"] == "rot":
            e["point"] = [round(float(v), 9) for v in pl.point(mob["point"])]
        if mob["kind"] == "spring":
            e["rest"] = mob["rest"]
        if mob.get("on_stem"):
            e["on_stem"] = True
        mobs[mn] = e
    doc["keyless"] = {"stem": {"parts": spec["mobiles"]["stem"]["parts"],
                               "point": [round(float(v), 9) for v in pl.point((0, 0, 0))],
                               "direction": [round(float(v), 9) for v in pl.vec((1, 0, 0))]},
                      "arbor": {"parts": spec["mobiles"]["barrel"]["parts"]}, "mobiles": mobs}
    doc["keyless"]["stem"]["direction"][2] = 0.0
    # friction_on: the cannon pinion and the minute hand become their own mobile on the centre wheel
    cen = doc["mobiles"]["centre"]
    can = ["cannon", "minute_hand"]

    def keep(parts):       # material kept; part_materials only for the parts the new mobile has
        d = dict(cen, parts=parts)
        pm = {k: v for k, v in cen.get("part_materials", {}).items() if k in parts}
        d.pop("part_materials", None)
        if pm:
            d["part_materials"] = pm
        return d
    doc["mobiles"]["centre"] = keep([p for p in cen["parts"] if p not in can])     # centre arbor (and its wheel part)
    doc["mobiles"]["cannon"] = dict(keep(can), friction_on="centre")
    for e in doc["meshes"]:
        if e["driver"] == "centre" and e["driven"] == "minute_wheel":
            e["driver"] = "cannon"
    doc["hands"]["minute"]["mobile"] = "cannon"
    doc["fixed"] = doc["fixed"] + spec["fixed"]
    with open(os.path.join(out, "movement.json"), "w") as f:
        json.dump(doc, f, indent=1)
    with open(os.path.join(out, "variant_6h.json")) as f:
        var = json.load(f)
    var["fixed"] = doc["fixed"]
    with open(os.path.join(out, "variant_6h.json"), "w") as f:
        json.dump(var, f, indent=1)
    sol = out.rstrip("/") + "_solids"
    os.makedirs(sol)
    for n, m in kp.items():
        with open(os.path.join(out, "parts", n + ".step"), "wb") as f:
            f.write(_placeholder(n))
        core.write_stl(os.path.join(sol, n + ".stl"), m)
    info = {"diag": diag, "layout": layout, "flip": flip, "phi_deg": phi, "z0": z0, "outer_stem_shortened_by": round(shift, 4),
            "keyless_parts": sorted(kp), "fixed_added": spec["fixed"], "solids": sol}
    print(json.dumps(info, indent=1))
    return info


def grade(out, force=False, jobs=1, work=None):
    from geometry import watch as W
    from geometry import core
    import grade_watch as G
    sol = out.rstrip("/") + "_solids"
    cache = {}
    for f in sorted(os.listdir(sol)):
        n = f[:-4]
        cache[(n, hashlib.sha256(_placeholder(n)).hexdigest())] = core.tris_to_manifold(
            core.read_stl(os.path.join(sol, f), W.MAX_TRIANGLES, W.MAX_STL_BYTES))
    t = time.time()
    m = W.load_movement(out, cache=cache)
    print("movement.json loaded in %.0f s; keyless parts %s; friction %s" % (time.time() - t, m.keyless_names, m.friction))
    t = time.time()
    if work:
        os.makedirs(work, exist_ok=True)
    g, c, d = G.grade_keyless_part(m, force=force, jobs=jobs, work=work)
    res = {"gates": g, "checks": c, "seconds": round(time.time() - t, 1), "details": d}
    w = G.KJ.step_weights()
    res["s"] = float(sum(w[k] for k in w if c.get(k)) / sum(w.values())) if all(g.values()) else 0.0
    p = out.rstrip("/") + "_p5.json"
    with open(p, "w") as f:
        json.dump(res, f, indent=1, default=str)
    print(json.dumps({"gates": g, "checks": c, "s": res["s"], "seconds": res["seconds"], "details_file": p}))
    return res


def main(argv):
    if argv[:1] == ["build"]:
        layout = argv[argv.index("--layout") + 1] if "--layout" in argv else "under"
        build(os.path.abspath(argv[1]), os.path.abspath(argv[2]), layout, "--diag" in argv)
        return 0
    if argv[:1] == ["grade"]:
        jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 1
        work = os.path.abspath(argv[argv.index("--work") + 1]) if "--work" in argv else None
        grade(os.path.abspath(argv[1]), "--force" in argv, jobs, work)
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
