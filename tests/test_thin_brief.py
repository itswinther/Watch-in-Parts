"""Tests for what the agent's documents say about thickness (environment/brief_thin.py, W.THIN_TARGET_STATED off).
    python3 tests/test_thin_brief.py
Run from the repository root; seconds. Case:
  documents  no document of the agent's folder matches a pattern of make_bundle_job.thickness_secrets(); the work
             order has its one Thickness sentence and no scoring text; its Acceptance paragraph does not mention
             thickness; QA-W100 section 9 says how the height is measured and prints no length; the bundle builds"""
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.abspath(ROOT))
sys.path.insert(0, os.path.join(os.path.abspath(ROOT), "environment"))
from geometry import watch as W        # noqa: E402
import make_bundle_job as M            # noqa: E402


def case_documents():
    import brief_thin as T
    import make_brief_job as B
    if W.THIN_TARGET_STATED or not T.THIN_IN_BRIEF:
        return "skipped (target stated, or the thinness probe is off)"
    texts = B.agent_texts(B.documents())
    pats = [re.compile(p, re.I) for p in M.thickness_secrets()]
    for path, text in texts.items():
        for p in pats:
            m = p.search(text)
            assert m is None, "%s prints %r" % (path, m.group(0))
    qa = texts["datasheets/" + B.QA_FILE]
    sec = qa[qa.index("## %s. %s" % (T.SECTION, T.SECTION_TITLE)):]
    flat = " ".join(sec.split())
    for phrase in ("highest point minus the lowest point", "the taller of the two counts",
                   "manufacturer's own design", "Thinner is better"):
        assert phrase in flat, "section %s lacks %r" % (T.SECTION, phrase)
    assert not re.search(r"[0-9]\s*mm\b", sec), "section %s prints a length" % T.SECTION
    order = [ln for ln in texts["instruction.md"].split("\n") if ln.startswith("| Thickness |")]
    assert len(order) == 1 and "the thinner the movement, the better" in order[0]
    assert "score" not in sec and "score" not in order[0]
    acc = texts["instruction.md"].split("## Acceptance")[1].split("## ")[0]
    assert "thick" not in acc and not re.search(r"\bthin", acc), "the Acceptance paragraph speaks of thickness"
    tmp = tempfile.mkdtemp(prefix="thin_brief_")
    try:
        out = M.build(os.path.join(tmp, "bundle"))
        assert M.leak_hits(out) == []
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return "%d documents clean; the bundle builds with no leak" % len(texts)


CASES = [("documents", case_documents)]


def main(argv):
    failed = 0
    for name, fn in CASES:
        try:
            print("PASS %s: %s" % (name, fn()), flush=True)
        except AssertionError as e:
            failed += 1
            print("FAIL %s: %s" % (name, e), flush=True)
    print("%d of %d passed" % (len(CASES) - failed, len(CASES)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
