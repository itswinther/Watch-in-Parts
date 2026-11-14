"""Build the folder an agent under test may see for the watch task.
    python environment/make_bundle_watch.py OUT_DIR [--stage 1|2|3|4] [--prev FOLDER] [--tools no|yes]
--prev is the previous stage's submission folder (stages 2 to 4). Its movement.json and parts/ (STEP files)
are copied into work/ and previous/; its scripts/ is not (a later stage gets files, not the earlier code).
--tools no (default): the written contract, the raw geometry kernel and a format-only submit.
--tools yes: the measuring tools and the public engine (stage 1 only; the stage tools are not built).
Never included: the grader, the hand speeds, the gear maker, any reference, project documents."""
import os
import re
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)


def main(argv):
    out = argv[0]
    opts = dict(zip(argv[1:], argv[2:]))
    stage, prev, tools = int(opts.get("--stage", "1")), opts.get("--prev"), opts.get("--tools", "no")
    for d in ("work/parts", "submission", "meshes", "tools", "scripts"):
        os.makedirs(os.path.join(out, d), exist_ok=True)
    pub = os.path.join(ROOT, "environment", "public")
    shutil.copyfile(os.path.join(pub, "INSTRUCTION_WATCH_S%d.md" % stage), os.path.join(out, "INSTRUCTION.md"))
    with open(os.path.join(pub, "SPEC_WATCH.md")) as f:
        spec = f.read()
    shutil.copyfile(os.path.join(ROOT, "geometry", "data", "barrel.stl"), os.path.join(out, "meshes", "barrel.stl"))
    if tools == "no":
        with open(os.path.join(pub, "SPEC_WATCH_GIVEN_NOTOOLS.md")) as f:
            spec = spec[:spec.index("## Tools")] + f.read()
        shutil.copyfile(os.path.join(ROOT, "geometry", "core.py"), os.path.join(out, "tools", "kernel.py"))
        from geometry import watch as W
        with open(os.path.join(ROOT, "environment", "submit_template.py")) as f:
            sub = f.read()
        sub = (sub.replace("__MAX_PARTS__", str(W.MAX_PARTS)).replace("__MAX_TRIANGLES__", str(W.MAX_TRIANGLES))
               .replace("__MAX_STL_BYTES__", str(W.MAX_STL_BYTES)).replace("__NAME_RE__", W.NAME_RE.pattern))
        for k in ("MAX_STEP_BYTES", "STEP_LINEAR_DEFLECTION", "STEP_ANGULAR_DEFLECTION", "STEP_MAX_TRIANGLE_FACES",
                  "STEP_TIMEOUT_S", "STEP_MEMORY_MB", "SELF_UNION_TOL", "MAX_SCRIPTS_BYTES", "MAX_SCRIPT_FILES"):
            sub = sub.replace("__%s__" % k, repr(getattr(W, k)))
        if re.search(r"__[A-Z_]+__", sub):
            raise SystemExit("submit template has an unfilled placeholder")
        with open(os.path.join(out, "tools", "submit.py"), "w") as f:
            f.write(sub)
    else:
        for d in ("tools/geometry/data", "tools/public"):
            os.makedirs(os.path.join(out, d), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, "environment", "tools_watch.py"), os.path.join(out, "tools", "tools_watch.py"))
        for f in ("__init__.py", "core.py", "watch.py"):
            shutil.copyfile(os.path.join(ROOT, "geometry", f), os.path.join(out, "tools", "geometry", f))
        shutil.copyfile(os.path.join(ROOT, "geometry", "data", "barrel.stl"), os.path.join(out, "tools", "geometry", "data", "barrel.stl"))
        with open(os.path.join(out, "tools", "public", "SPEC_WATCH.md"), "w") as f:
            f.write(spec)
    with open(os.path.join(out, "SPEC_WATCH.md"), "w") as f:
        f.write(spec)
    if stage > 1:
        if not prev or not os.path.isfile(os.path.join(prev, "movement.json")):
            raise SystemExit("stage %d needs --prev with a submitted movement" % stage)
        for dst in ("work", "previous"):
            d = os.path.join(out, dst)
            if os.path.isdir(d):
                shutil.rmtree(d)
            os.makedirs(os.path.join(d, "parts"))
            shutil.copyfile(os.path.join(prev, "movement.json"), os.path.join(d, "movement.json"))
            for f in os.listdir(os.path.join(prev, "parts")):
                shutil.copyfile(os.path.join(prev, "parts", f), os.path.join(d, "parts", f))
    print("bundle written to", out)


if __name__ == "__main__":
    main(sys.argv[1:])
