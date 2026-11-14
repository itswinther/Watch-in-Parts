"""Build the folder the agent under test sees for the one-job watch task (Decisions 2026-11-14 15:44).
    python3 environment/make_bundle_job.py OUT
writes OUT (in the task image it is /app):
    instruction.md          the brief, from environment/public/job/PROMPT.md
    FORMAT.md               the file formats, from environment/public/job/FORMAT.md
    datasheets/             the watch-side sheets (DS-W01 to DS-W03, DS-W04 with the strength check), the inspection
                            procedure QA-W100, workstream A's supplier sheets (DS-101 to DS-501, from
                            spikes/keyless/datasheets/INDEX.md) and one INDEX.md for all of them
    supplied/barrel.stl     the supplied barrel (geometry/data/barrel.stl with a neutral header)
    tools/kernel.py         geometry/core.py
    tools/check_format.py   environment/check_format_job.py with the format numbers filled in
    delivery/               empty
Fails (exit 1, OUT removed) if the committed documents are not what geometry/watch.py gives
(environment/make_brief_job.py --check), if a graded number's home cell in OUT is missing or disagrees with the
constants, or if OUT prints a graded number where it has no home (make_brief_job.verify(), run on the files as
written to OUT, A's sheets included), or if anything forbidden would be in OUT: a forbidden file or folder name,
a file carrying the NOT-FOR-AGENT mark, or a forbidden word or phrase anywhere in any file (FORBIDDEN_WORDS and
the reference's own numbers, case-insensitive)."""
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
# Workstream A's supplier sheets (spikes/keyless/datasheets/DS-*.md, as listed in their INDEX.md) join the bundle
# (Decisions 17:56); make_brief_job.external_sheets() lists them and refuses TRACEABILITY.md and NOT-FOR-AGENT files.

FORBIDDEN_NAMES = {"solution", "tests", "anchors", "solution.md", "step_by_step.md", "context.md", "claude.md",
                   "session.md", ".git", "spec.md", "grade_watch.py", "traceability.md", "public_domain",
                   "traceability_watch.md"}     # environment/public/job/TRACEABILITY_WATCH.md stays in the repository
# case-insensitive regular expressions; none may occur in any file of the bundle. The bare word "reference" is
# allowed since A's sheets use it in its ordinary sense ("reference measurement", "reference datasheet"); the
# phrases that would point at our own solution are banned instead, with the reference's own numbers
# (reference_numbers()). "weight" is banned except in "weight %" (an alloy's composition on DS-201).
FORBIDDEN_WORDS = [r"reference_watch", r"reference[ _-]solution", r"reference[ _-]movement", r"reference[ _-]delivery",
                   r"reference[ _-]design", r"reference[ _-]run", r"reference[ _-]script",
                   r"the reference (?:scores|passes|grades|reaches|keeps|uses|declares)", r"reference's",
                   r"solution", r"\bstages?\b", r"hand_speed", r"1/12", r"1/24", r"60 turns",
                   r"weight", r"anchor", r"board-in-a-box", r"session", r"\bkept\b", r"grade_watch", r"oracle",
                   r"traceab", r"NOT-FOR-AGENT"]
NEUTRAL_STL_HEADER = b"supplied barrel, binary STL, millimetres".ljust(80, b" ")


def fill_check_format():
    with open(os.path.join(ROOT, "environment", "check_format_job.py")) as f:
        s = f.read()
    s = s.replace("__NAME_RE__", W.NAME_RE.pattern)
    for k in ("MAX_PARTS", "MAX_TRIANGLES", "MAX_STEP_BYTES", "STEP_LINEAR_DEFLECTION", "STEP_ANGULAR_DEFLECTION",
              "STEP_MAX_TRIANGLE_FACES", "STEP_TIMEOUT_S", "STEP_MEMORY_MB", "SELF_UNION_TOL", "MAX_SCRIPTS_BYTES",
              "MAX_SCRIPT_FILES", "MAX_JSON_BYTES", "MAX_ASSEMBLY_BYTES", "MIN_TEETH", "MAX_TEETH", "MAX_NAME_LEN",
              "MATERIAL_DESIGNATIONS"):
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


def reference_numbers():
    """Patterns for the numbers that would identify our own delivery: its case centre, its case reach and every
    mobile axis (solution/reference_watch.py's layout, computed, not copied), each to 3 decimals as written."""
    sys.path.insert(0, os.path.join(ROOT, "solution"))
    import reference_watch as R
    P = R.place()
    centre, reach, _ = R.case_geometry(P)
    vals = list(centre) + [reach] + [c for k, a in P.items() if k != "case" for c in a]
    pats = set()
    for v in vals:
        if abs(v - round(v)) > 1e-6:                      # whole numbers (0, 12) say nothing about the layout
            i, f = ("%.6f" % abs(v)).split(".")
            pats.add(re.escape(i + "." + f[:3]))
    return sorted(pats)


def leak_hits(out, words=None):
    """[(relative path, line number or 0 for a name, matched text)] for every forbidden name or word in out."""
    hits = []
    words = FORBIDDEN_WORDS + reference_numbers() if words is None else words
    pats = [re.compile(w.encode(), re.I) for w in words]
    for root, dirs, files in os.walk(out):
        for n in dirs + files:
            if n.lower() in FORBIDDEN_NAMES:
                hits.append((os.path.relpath(os.path.join(root, n), out), 0, n))
        for n in files:
            p = os.path.join(root, n)
            with open(p, "rb") as f:
                data = f.read()
            if b"NOT-FOR-AGENT" in data:
                hits.append((os.path.relpath(p, out), 0, "NOT-FOR-AGENT mark"))
            for i, line in enumerate(data.split(b"\n"), 1):
                for pat in pats:
                    for m in pat.finditer(line):
                        hits.append((os.path.relpath(p, out), i, m.group(0).decode("latin-1")))
    return hits


def cell_errors_in(out, S):
    """make_brief_job.verify() on the files as they are in OUT: every home cell (A's DS-101 and DS-201 cells
    included, through builder S's trace rows) exists and matches the constants, and no graded number is printed
    where it has no home."""
    L, Bf = B._literals(), B.barrel_facts()
    rows = B.traceability_rows(L, Bf, S)
    texts = {}
    for root, _, files in os.walk(out):
        for n in files:
            if n.endswith(".md"):
                p = os.path.join(root, n)
                texts[os.path.relpath(p, out).replace(os.sep, "/")] = open(p, encoding="utf-8").read()
    return B.verify(texts, rows)


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
    S = B.strength_module()
    for f, _, _ in B.our_sheets(S) + [("INDEX.md", None, None)]:
        shutil.copyfile(os.path.join(JOB, "datasheets", f), os.path.join(out, "datasheets", f))
    for f, _, _ in B.external_sheets():
        shutil.copyfile(os.path.join(B.A_SHEETS, f), os.path.join(out, "datasheets", f))
    with open(os.path.join(out, "supplied", "barrel.stl"), "wb") as f:
        f.write(barrel_bytes())
    with open(os.path.join(out, "tools", "kernel.py"), "w", encoding="utf-8") as f:
        f.write(kernel_text())
    with open(os.path.join(out, "tools", "check_format.py"), "w", encoding="utf-8") as f:
        f.write(fill_check_format())
    errs = cell_errors_in(out, S)
    if errs:
        shutil.rmtree(out)
        raise SystemExit("graded numbers in the bundle disagree with the constants, bundle removed:\n" + "\n".join(errs))
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
