"""Tests for the bundle's leak guard on the thickness score (environment/make_bundle_job.py thickness_secrets()).
    python3 tests/test_thin_leak.py
Run from the repository root; seconds. Cases:
  patterns  the patterns match the house design's height as printed and as a longer decimal that rounds to it, the
            score formula and the wording of a stated target, and no unrelated number
  planted   a folder with a file that carries the height or the formula is reported by leak_hits(); a clean one is not"""
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


def case_patterns():
    if W.THIN_TARGET_STATED:
        assert M.thickness_secrets() == []
        return "target stated: no secret patterns"
    pats = [re.compile(p, re.I) for p in M.thickness_secrets()]

    def hit(text):
        return any(p.search(text) for p in pats)
    r = repr(W.THIN_REFERENCE_MM)
    lower = "%.*f" % (len(r.split(".")[1]), W.THIN_REFERENCE_MM - 10 ** -len(r.split(".")[1]))
    yes = [r, "H = %s mm" % r, r + "0", r + "00 mm", r + "4", lower + "5", lower + "91", "(%s)" % r, "height:%s," % r,
           "s = (1 - x) ^ 4", "x = (H - a) / (C - a)", "The thickness target", "the target is", "Exponent 4",
           "to the %dth power" % W.THIN_SCORE_EXPONENT]
    no = ["1" + r, "2." + r, r + "5", r + "9", lower + "4", lower, r[:-1] + str((int(r[-1]) + 1) % 10) if r[-1] != "9" else "0",
          "0." + r.replace(".", ""), "33.5", "as thin as possible", "targets", "a tenth of a millimetre"]
    for t in yes:
        assert hit(t), "not caught: %r" % t
    for t in no:
        assert not hit(t), "false positive: %r" % t
    return "%d texts caught, %d left alone" % (len(yes), len(no))


def case_planted():
    if W.THIN_TARGET_STATED:
        return "skipped (target stated)"
    tmp = tempfile.mkdtemp(prefix="thin_leak_")
    try:
        note = os.path.join(tmp, "note.txt")
        with open(note, "w") as f:
            f.write("a slim dress watch: the thinner the movement, the better\n")
        assert M.leak_hits(tmp) == [], M.leak_hits(tmp)
        texts = ("measured %.4f mm" % (W.THIN_REFERENCE_MM - 0.0009), "H %s" % W.THIN_REFERENCE_MM,
                 "s = (1 - x) ^ %d" % W.THIN_SCORE_EXPONENT)
        for text in texts:
            with open(note, "w") as f:
                f.write(text + "\n")
            hits = M.leak_hits(tmp)
            assert hits and hits[0][0] == "note.txt", (text, hits)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return "%d planted leaks reported" % len(texts)


CASES = [("patterns", case_patterns), ("planted", case_planted)]


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
