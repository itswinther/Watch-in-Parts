"""Reference set for the watch task.   python tests/test_anchors_watch.py
Builds the reference movement, changes one thing per anchor, grades it and asserts the score."""
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "solution"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reference_watch as ref
from grade_watch import grade, WEIGHTS

TOTAL = sum(WEIGHTS.values())


def fails(*ids):
    p = (TOTAL - sum(WEIGHTS[i] for i in ids)) / TOTAL
    return 0.5 * p * p


def edit(d, fn):
    p = os.path.join(d, "movement.json")
    with open(p) as f:
        doc = json.load(f)
    fn(doc)
    with open(p, "w") as f:
        json.dump(doc, f)


def a_gold(d):
    pass


def a_nothing(d):
    shutil.rmtree(os.path.join(d, "parts"))
    os.remove(os.path.join(d, "movement.json"))


def a_hands_swapped(d):
    def fn(doc):
        doc["hands"]["hour"], doc["hands"]["minute"] = doc["hands"]["minute"], doc["hands"]["hour"]
    edit(d, fn)


def a_wrong_count(d):
    edit(d, lambda doc: doc["meshes"][1].update(driven_teeth=31))


def a_no_cock(d):
    edit(d, lambda doc: doc["fixed"].remove("barrel_cock"))


def a_no_seconds_drive(d):
    edit(d, lambda doc: doc["meshes"].pop(3))


def a_missing_part(d):
    os.remove(os.path.join(d, "parts", "fourth.stl"))


ANCHORS = [
    ("gold: reference movement", a_gold, 1.0),
    ("do nothing", a_nothing, 0.0),
    ("a part file missing", a_missing_part, 0.0),
    ("hour and minute hands swapped", a_hands_swapped, fails("hour", "minute")),
    ("one tooth count declared wrong", a_wrong_count, fails("train", "minute", "hour", "seconds")),
    ("barrel not held from above", a_no_cock, fails("held")),
    ("seconds mesh not declared", a_no_seconds_drive, None),
]


def main():
    base = tempfile.mkdtemp()
    ref.main(base)
    bad = 0
    for name, fn, want in ANCHORS:
        d = tempfile.mkdtemp()
        shutil.rmtree(d)
        shutil.copytree(base, d)
        fn(d)
        r = grade(d)
        failed = [k for dd in (r["gates"], r["checks"]) for k, v in dd.items() if not v]
        ok = want is None or abs(r["reward"] - want) < 1e-6
        bad += not ok
        print("%-4s %-34s S=%.4f expected %s  failed: %s" % ("ok" if ok else "OFF", name, r["reward"],
              "(recorded)" if want is None else "%.4f" % want, ",".join(failed) or "-"))
        shutil.rmtree(d, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
