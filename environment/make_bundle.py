"""Build the folder an agent under test is allowed to see, for instance H2.
    python environment/make_bundle.py OUT_DIR
OUT_DIR gets INSTRUCTION.md, SPEC_H2.md, meshes/, tools/ (tools_h2.py plus the
public part of geometry/), and empty work/ and submission/. No grader, no
weights, no reference design, no project documents."""
import os
import re
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from geometry import h2_public as P
from geometry import core

PUBLIC_GEOMETRY = ("__init__.py", "constants.py", "core.py", "bodies.py", "contract.py", "h2_public.py")


def main(out):
    for d in ("work", "submission", "meshes", "tools/geometry", "tools/public"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    pub = os.path.join(ROOT, "environment", "public")
    shutil.copyfile(os.path.join(pub, "INSTRUCTION_H2.md"), os.path.join(out, "INSTRUCTION.md"))
    shutil.copyfile(os.path.join(pub, "SPEC_H2.md"), os.path.join(out, "SPEC_H2.md"))
    shutil.copyfile(os.path.join(pub, "SPEC_H2.md"), os.path.join(out, "tools", "public", "SPEC_H2.md"))
    shutil.copyfile(os.path.join(ROOT, "environment", "tools_h2.py"), os.path.join(out, "tools", "tools_h2.py"))
    for f in PUBLIC_GEOMETRY:
        with open(os.path.join(ROOT, "geometry", f)) as fh:
            text = fh.read()
        if f == "constants.py":      # drop grader-only values and project references
            text = re.sub(r"\nWEIGHTS = \{.*?\n\}\n", "\n", text, flags=re.S)
            text = re.sub(r"\n(GATES|REFERENCE_VOLUME|MATERIAL_FACTOR|CHECK_TIMEOUT_S) = [^\n]*", "", text)
            text = re.sub(r'""".*?"""', '"""Shared numbers for the supplied bodies and the voxel measurements."""', text, count=1, flags=re.S)
            text = re.sub(r"\s+# INTERPRETATION[^\n]*", "", text)
            text = re.sub(r"\n# INTERPRETATION[^\n]*", "", text)
            text = text.replace("INTERPRETATION: ", "")
        with open(os.path.join(out, "tools", "geometry", f), "w") as fh:
            fh.write(text)
    for n in P.BODY_NAMES:
        core.write_stl(os.path.join(out, "meshes", n + ".stl"), P.body(n))
    print("bundle written to", out)


if __name__ == "__main__":
    main(sys.argv[1])
