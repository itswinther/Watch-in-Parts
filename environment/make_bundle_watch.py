"""Build the folder an agent under test may see for the watch task.
    python environment/make_bundle_watch.py OUT_DIR
No grader, no hand speeds, no gear maker, no reference movement, no project documents."""
import os
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def main(out):
    for d in ("work/parts", "submission", "meshes", "tools/geometry/data", "tools/public"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    pub = os.path.join(ROOT, "environment", "public")
    shutil.copyfile(os.path.join(pub, "INSTRUCTION_WATCH.md"), os.path.join(out, "INSTRUCTION.md"))
    shutil.copyfile(os.path.join(pub, "SPEC_WATCH.md"), os.path.join(out, "SPEC_WATCH.md"))
    shutil.copyfile(os.path.join(pub, "SPEC_WATCH.md"), os.path.join(out, "tools", "public", "SPEC_WATCH.md"))
    shutil.copyfile(os.path.join(ROOT, "environment", "tools_watch.py"), os.path.join(out, "tools", "tools_watch.py"))
    for f in ("__init__.py", "core.py", "watch.py"):
        shutil.copyfile(os.path.join(ROOT, "geometry", f), os.path.join(out, "tools", "geometry", f))
    shutil.copyfile(os.path.join(ROOT, "geometry", "data", "barrel.stl"), os.path.join(out, "tools", "geometry", "data", "barrel.stl"))
    shutil.copyfile(os.path.join(ROOT, "geometry", "data", "barrel.stl"), os.path.join(out, "meshes", "barrel.stl"))
    print("bundle written to", out)


if __name__ == "__main__":
    main(sys.argv[1])
