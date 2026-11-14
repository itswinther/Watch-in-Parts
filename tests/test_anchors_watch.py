"""Reference set for the three-stage watch task.   python tests/test_anchors_watch.py
Builds the reference for all three stages, changes one thing per anchor, grades it and asserts the score.
Gold is 1.00 at every stage, do-nothing 0.00, likely shortcuts and partial work lower."""
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
from grade_watch import grade, WEIGHTS, WEIGHTS_2


def fails(stage, *ids):
    w = dict(WEIGHTS, **(WEIGHTS_2 if stage == 2 else {}))
    p = (sum(w.values()) - sum(w[i] for i in ids)) / sum(w.values())
    return 0.5 * p * p


def parts_score(missing, total=18):
    p = (total - missing) / total
    return 0.5 * p * p


def edit(d, fn, name="movement.json"):
    p = os.path.join(d, name)
    with open(p) as f:
        doc = json.load(f)
    fn(doc)
    with open(p, "w") as f:
        json.dump(doc, f)


def touch_part(d, part):
    """Same geometry, different bytes (the STL header)."""
    p = os.path.join(d, "parts", part + ".stl")
    with open(p, "rb") as f:
        data = f.read()
    with open(p, "wb") as f:
        f.write(b"changed".ljust(80, b" ") + data[80:])


def nothing(d):
    shutil.rmtree(os.path.join(d, "parts"))
    os.remove(os.path.join(d, "movement.json"))


def swap_hands(doc):
    doc["hands"]["hour"], doc["hands"]["minute"] = doc["hands"]["minute"], doc["hands"]["hour"]


def dup_fixed(d):
    shutil.copyfile(os.path.join(d, "parts", "bridge.stl"), os.path.join(d, "parts", "bridge_copy.stl"))
    edit(d, lambda doc: doc["fixed"].append("bridge_copy"))


def reorder(first, after):
    def fn(doc):
        doc["order"].remove(first)
        doc["order"].insert(doc["order"].index(after), first)
    return fn


def teleport(doc):
    doc["paths"]["dial"] = [doc["paths"]["dial"][0], doc["paths"]["dial"][-1]]


def use_stage1(d, base):
    shutil.rmtree(d)
    shutil.copytree(os.path.join(base, "stage1"), d)


# (name, stage, change(folder, base), expected score)
ANCHORS = [
    ("s1 gold", 1, lambda d, b: None, 1.0),
    ("s1 do nothing", 1, lambda d, b: nothing(d), 0.0),
    ("s1 a part file missing", 1, lambda d, b: os.remove(os.path.join(d, "parts", "fourth.stl")), 0.0),
    ("s1 two fixed parts overlap", 1, lambda d, b: dup_fixed(d), 0.0),
    ("s1 hour and minute hands swapped", 1, lambda d, b: edit(d, swap_hands), fails(1, "hour", "minute")),
    ("s1 one tooth count declared wrong", 1, lambda d, b: edit(d, lambda doc: doc["meshes"][1].update(driven_teeth=31)),
     fails(1, "train", "minute", "hour", "seconds")),
    ("s1 barrel not held from above", 1, lambda d, b: edit(d, lambda doc: doc["fixed"].remove("barrel_cock")), fails(1, "held")),
    ("s2 gold", 2, lambda d, b: None, 1.0),
    ("s2 stage-1 design handed back unchanged", 2, use_stage1, fails(2, "day_hand", "day_place")),
    ("s2 seconds hand declared as the 24-hour hand", 2,
     lambda d, b: edit(d, lambda doc: doc["hands"].update(day={"mobile": "seconds", "part": "seconds_hand"})), fails(2, "day_hand")),
    ("s2 a frozen wheel file changed", 2, lambda d, b: touch_part(d, "third"), 0.0),
    ("s3 gold", 3, lambda d, b: None, 1.0),
    ("s3 no assembly.json", 3, lambda d, b: os.remove(os.path.join(d, "assembly.json")), 0.0),
    ("s3 a part file changed", 3, lambda d, b: touch_part(d, "dial"), 0.0),
    ("s3 centre before third", 3, lambda d, b: edit(d, reorder("centre", "third"), "assembly.json"), parts_score(1)),
    ("s3 dial jumps into place in one step", 3, lambda d, b: edit(d, teleport, "assembly.json"), parts_score(1)),
    ("s3 bridge on before the wheels", 3, lambda d, b: edit(d, reorder("bridge", "barrel"), "assembly.json"), parts_score(6)),
]


def main():
    base = tempfile.mkdtemp()
    ref.main(base)
    bad = 0
    for name, stage, change, want in ANCHORS:
        d = tempfile.mkdtemp()
        shutil.rmtree(d)
        shutil.copytree(os.path.join(base, "stage%d" % stage), d)
        change(d, base)
        r = grade(d, stage, os.path.join(base, "stage%d" % (stage - 1)) if stage > 1 else None)
        failed = [k for dd in (r["gates"], r["checks"]) for k, v in dd.items() if not v]
        ok = abs(r["reward"] - want) < 1e-6
        bad += not ok
        print("%-4s %-46s S=%.4f expected %.4f  failed: %s" % ("ok" if ok else "OFF", name, r["reward"], want, ",".join(failed[:8]) or "-"), flush=True)
        shutil.rmtree(d, ignore_errors=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
