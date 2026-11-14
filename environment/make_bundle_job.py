"""Build the folder the agent under test sees for the one-job watch task (Decisions 2026-11-14 15:44).
    python3 environment/make_bundle_job.py OUT
writes OUT (in the task image it is /app):
    instruction.md          the brief, from environment/public/job/PROMPT.md
    FORMAT.md               the file formats, from environment/public/job/FORMAT.md
    datasheets/             the watch-side sheets (DS-W01 to DS-W03, INDEX.md), plus EXTERNAL_SHEETS
    supplied/barrel.stl     the supplied barrel (geometry/data/barrel.stl with a neutral header)
    tools/kernel.py         geometry/core.py
    tools/check_format.py   environment/check_format_job.py with the format numbers filled in
    delivery/               empty
Fails (exit 1, OUT removed) if the committed documents are not what geometry/watch.py gives
(environment/make_brief_job.py --check), or if anything forbidden would be in OUT: a forbidden file or folder
name, or a forbidden word anywhere in any file (FORBIDDEN_WORDS, case-insensitive)."""
import os
import re
import shutil
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from geometry import watch as W        # noqa: E402
import make_brief_job as B             # noqa: E402

JOB = os.path.join(ROOT, "environment", "public", "job")
# Sheets owned by other workstreams that join the bundle with their part of the job, as
# (source path relative to the repository root, document id, title). Empty until the crown-winding part joins:
# workstream A's keyless sheets (spikes/keyless/datasheets/DS-101 ... DS-501) go here then.
EXTERNAL_SHEETS = []

FORBIDDEN_NAMES = {"solution", "tests", "anchors", "solution.md", "step_by_step.md", "context.md", "claude.md",
                   "session.md", ".git", "spec.md", "grade_watch.py",
                   "traceability_watch.md"}     # environment/public/job/TRACEABILITY_WATCH.md stays in the repository
# case-insensitive regular expressions; none may occur in any file of the bundle
FORBIDDEN_WORDS = [r"reference", r"solution", r"\bstages?\b", r"hand_speed", r"1/12", r"1/24", r"60 turns",
                   r"weight", r"anchor", r"board-in-a-box", r"session", r"\bkept\b", r"grade_watch", r"oracle"]
NEUTRAL_STL_HEADER = b"supplied barrel, binary STL, millimetres".ljust(80, b" ")


def fill_check_format():
    with open(os.path.join(ROOT, "environment", "check_format_job.py")) as f:
        s = f.read()
    s = s.replace("__NAME_RE__", W.NAME_RE.pattern)
    for k in ("MAX_PARTS", "MAX_TRIANGLES", "MAX_STEP_BYTES", "STEP_LINEAR_DEFLECTION", "STEP_ANGULAR_DEFLECTION",
              "STEP_MAX_TRIANGLE_FACES", "STEP_TIMEOUT_S", "STEP_MEMORY_MB", "SELF_UNION_TOL", "MAX_SCRIPTS_BYTES",
              "MAX_SCRIPT_FILES", "MAX_JSON_BYTES", "MAX_ASSEMBLY_BYTES", "MIN_TEETH", "MAX_TEETH", "MAX_NAME_LEN"):
        s = s.replace("__%s__" % k, repr(getattr(W, k)))
    if "{1,%d}" % W.MAX_NAME_LEN not in W.NAME_RE.pattern:
        raise SystemExit("NAME_RE and MAX_NAME_LEN disagree")
    if re.search(r"__[A-Z_]+__", s):
        raise SystemExit("check_format template has an unfilled placeholder")
    return s


def kernel_text():
    with open(os.path.join(ROOT, "geometry", "core.py")) as f:
        s = f.read()
    return s.replace('b"board-in-a-box"', 'b"kernel"')


def barrel_bytes():
    with open(os.path.join(ROOT, "geometry", "data", "barrel.stl"), "rb") as f:
        data = f.read()
    return NEUTRAL_STL_HEADER + data[80:]


def leak_hits(out, words=FORBIDDEN_WORDS):
    """[(relative path, line number or 0 for a name, matched text)] for every forbidden name or word in out."""
    hits = []
    pats = [re.compile(w.encode(), re.I) for w in words]
    for root, dirs, files in os.walk(out):
        for n in dirs + files:
            if n.lower() in FORBIDDEN_NAMES:
                hits.append((os.path.relpath(os.path.join(root, n), out), 0, n))
        for n in files:
            p = os.path.join(root, n)
            with open(p, "rb") as f:
                data = f.read()
            for i, line in enumerate(data.split(b"\n"), 1):
                for pat in pats:
                    for m in pat.finditer(line):
                        hits.append((os.path.relpath(p, out), i, m.group(0).decode("latin-1")))
    return hits


def build(out):
    bad = B.check()
    if bad:
        raise SystemExit("documents out of date with geometry/watch.py (run python3 environment/make_brief_job.py): "
                         + ", ".join(bad))
    if os.path.exists(out):
        shutil.rmtree(out)
    for d in ("datasheets", "supplied", "tools", "delivery"):
        os.makedirs(os.path.join(out, d))
    shutil.copyfile(os.path.join(JOB, "PROMPT.md"), os.path.join(out, "instruction.md"))
    shutil.copyfile(os.path.join(JOB, "FORMAT.md"), os.path.join(out, "FORMAT.md"))
    for f, _, _ in B.DATASHEETS:
        shutil.copyfile(os.path.join(JOB, "datasheets", f), os.path.join(out, "datasheets", f))
    extra = []
    for src, doc, title in EXTERNAL_SHEETS:
        name = os.path.basename(src)
        shutil.copyfile(os.path.join(ROOT, src), os.path.join(out, "datasheets", name))
        extra.append((name, doc, title))
    with open(os.path.join(out, "datasheets", "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(B.index_sheet(extra))
    with open(os.path.join(out, "supplied", "barrel.stl"), "wb") as f:
        f.write(barrel_bytes())
    with open(os.path.join(out, "tools", "kernel.py"), "w", encoding="utf-8") as f:
        f.write(kernel_text())
    with open(os.path.join(out, "tools", "check_format.py"), "w", encoding="utf-8") as f:
        f.write(fill_check_format())
    hits = leak_hits(out)
    if hits:
        shutil.rmtree(out)
        raise SystemExit("forbidden content, bundle removed:\n" + "\n".join("%s:%d: %s" % h for h in hits))
    return out


def main(argv):
    if len(argv) != 1:
        print("usage: make_bundle_job.py OUT")
        return 2
    out = os.path.abspath(argv[0])
    build(out)
    print("bundle written to", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
