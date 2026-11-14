"""Submitted files must be real files inside the submission folder (no symbolic links, nothing outside).
    python3 tests/test_submission_paths.py"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from geometry import watch as W
from geometry.core import FormatError


def refused(fn):
    try:
        fn()
    except FormatError as e:
        return str(e)
    return None


def main():
    with tempfile.TemporaryDirectory() as t:
        out = os.path.join(t, "outside")
        os.makedirs(os.path.join(out, "parts"))
        for n in ("a.step", "movement.json", "assembly.json"):
            open(os.path.join(out, n), "w").write("{}")
        open(os.path.join(out, "parts", "b.step"), "w").write("x")
        sub = os.path.join(t, "sub")                                   # part file a symlink
        os.makedirs(os.path.join(sub, "parts"))
        os.symlink(os.path.join(out, "a.step"), os.path.join(sub, "parts", "a.step"))
        os.symlink(os.path.join(out, "movement.json"), os.path.join(sub, "movement.json"))
        os.symlink(os.path.join(out, "assembly.json"), os.path.join(sub, "assembly.json"))
        sub2 = os.path.join(t, "sub2")                                 # parts/ a symlink
        os.makedirs(sub2)
        os.symlink(os.path.join(out, "parts"), os.path.join(sub2, "parts"))
        open(os.path.join(sub2, "parts_ok"), "w").close()
        cases = [("part file symlink", lambda: W.part_path(sub, "a")),
                 ("parts/ symlink", lambda: W.part_path(sub2, "b")),
                 ("movement.json symlink", lambda: W.load_movement(sub)),
                 ("assembly.json symlink", lambda: W.load_assembly(sub, None))]
        bad = 0
        for name, fn in cases:
            msg = refused(fn)
            print("%-24s %s" % (name, ("refused: " + msg) if msg else "NOT REFUSED"))
            bad += msg is None
        real = os.path.join(t, "real")
        os.makedirs(os.path.join(real, "parts"))
        open(os.path.join(real, "parts", "c.step"), "w").write("x")
        ok = W.part_path(real, "c") is not None and W.part_path(real, "missing") is None
        print("%-24s %s" % ("real file", "found" if ok else "WRONG"))
        bad += not ok
    print("PASS" if not bad else "FAIL")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
