"""Build the folder an agent under test may see for Moving Day.
    python environment/make_bundle_md.py OUT_DIR [instance]
Writes INSTRUCTION.md, SPEC_MD.md, instance.json, meshes/, tools/ (tools_md.py and
the public geometry files) and empty work/ and submission/. No reference paths,
no grader script, no project documents."""
import json
import os
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from geometry import core, md


def spec_tables(inst):
    """The instance-specific part of the spec, generated from the same data the grader uses."""
    L = ["## This apartment (instance %s)" % inst.name, "",
         "The apartment is a solid block, x %g..%g, y %g..%g, z %g..%g, with these boxes of air cut out of it."
         % (inst.block[0][0], inst.block[1][0], inst.block[0][1], inst.block[1][1], inst.block[0][2], inst.block[1][2]),
         "Everything else inside the block is solid: walls, floor, ceilings, door frames.", "",
         "| Air box | x | y | z |", "| --- | --- | --- | --- |"]
    for k, (lo, hi) in inst.air.items():
        L.append("| %s | %g..%g | %g..%g | %g..%g |" % (k, lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]))
    lo, hi = inst.staging
    L += ["", "Staging box (outside the front door): x %g..%g, y %g..%g, z %g..%g." % (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2]),
          "Space outside the block is empty.", "",
          "## The furniture", "",
          "Each piece is a union of boxes in its own frame. The final pose is the 4x4 matrix, row by row.", "",
          "| Piece | Weight | Boxes in its own frame | Final pose |", "| --- | --- | --- | --- |"]
    for n in inst.listed:
        p = inst.pieces[n]
        boxes = "; ".join("x %g..%g, y %g..%g, z %g..%g" % (b[0][0], b[1][0], b[0][1], b[1][1], b[0][2], b[1][2]) for b in p["boxes"])
        F = inst.final(n)
        L.append("| %s | %g | %s | `%s` |" % (n, p["weight"], boxes, json.dumps([[round(float(v), 9) for v in r] for r in F])))
    L += ["", "Total weight: %g." % sum(p["weight"] for p in inst.pieces.values()), ""]
    return "\n".join(L)


def main(out, instance="flat-1"):
    inst = md.INSTANCES[instance]()
    for d in ("work", "submission", "meshes", "tools/geometry", "tools/public"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    pub = os.path.join(ROOT, "environment", "public")
    with open(os.path.join(pub, "SPEC_MD.md")) as f:
        spec = f.read().replace("<<INSTANCE>>", spec_tables(inst))
    for dst in (os.path.join(out, "SPEC_MD.md"), os.path.join(out, "tools", "public", "SPEC_MD.md")):
        with open(dst, "w") as f:
            f.write(spec)
    shutil.copyfile(os.path.join(pub, "INSTRUCTION_MD.md"), os.path.join(out, "INSTRUCTION.md"))
    shutil.copyfile(os.path.join(ROOT, "environment", "tools_md.py"), os.path.join(out, "tools", "tools_md.py"))
    for f in ("__init__.py", "core.py", "md.py"):
        shutil.copyfile(os.path.join(ROOT, "geometry", f), os.path.join(out, "tools", "geometry", f))
    core.write_stl(os.path.join(out, "meshes", "apartment.stl"), inst.apartment())
    for n in inst.pieces:
        core.write_stl(os.path.join(out, "meshes", n + ".stl"), inst.piece(n))
    doc = {"name": inst.name, "units": "cm", "block": inst.block, "air": inst.air, "staging": inst.staging,
           "pieces": {n: {"boxes": p["boxes"], "final": inst.final(n).tolist(), "weight": p["weight"]} for n, p in inst.pieces.items()},
           "listed": inst.listed, "max_step": md.MAX_STEP, "max_poses": md.MAX_POSES, "volume_tolerance": md.VOL_TOL}
    with open(os.path.join(out, "instance.json"), "w") as f:
        json.dump(doc, f, indent=1)
    print("bundle written to", out)


if __name__ == "__main__":
    main(*sys.argv[1:3])
