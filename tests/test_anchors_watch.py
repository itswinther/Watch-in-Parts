"""Reference set for the four-stage watch task.   python tests/test_anchors_watch.py [WORKERS]
Builds the reference for all four stages, changes one thing per anchor, grades it and asserts the score.
Gold is 1.00 at every stage, do-nothing 0.00, likely shortcuts and partial work lower.
Anchors are graded in parallel (default 3 worker processes)."""
import json
import os
import shutil
import sys
import tempfile
from fractions import Fraction
from multiprocessing import Pool

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "solution"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reference_watch as ref
from grade_watch import grade, stage_weights
from geometry import watch as W


def fails(stage, *ids):
    w = stage_weights(stage)
    p = (sum(w.values()) - sum(w[i] for i in ids)) / sum(w.values())
    return 0.5 * p * p if ids else 1.0


def kept(n_lost, received=17):
    """Stage-3 kept-parts factor when n_lost of the received part files do not count."""
    return float(min(Fraction(1), Fraction(received - n_lost, received) / W.REF_KEPT_SHARE))


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


def use_stage(n):
    def fn(d, base):
        shutil.rmtree(d)
        shutil.copytree(os.path.join(base, "stage%d" % n), d)
    return fn


def touch_all(d):
    for n in os.listdir(os.path.join(d, "parts")):
        touch_part(d, n[:-4])


def rename_mobile(old, new):
    def fn(doc):
        doc["mobiles"][new] = doc["mobiles"].pop(old)
        for e in doc["meshes"]:
            for k in ("driver", "driven"):
                if e[k] == old:
                    e[k] = new
        for h in doc["hands"].values():
            if h["mobile"] == old:
                h["mobile"] = new
    return fn


def drop_mesh(a, b):
    def fn(doc):
        doc["meshes"] = [e for e in doc["meshes"] if (e["driver"], e["driven"]) != (a, b)]
    return fn


def old_wheel_as_fixed(d, base):
    """Keep the received third-wheel file and declare it a fixed ornament, moved out of the way by
    renaming nothing: it stands where it always stood, so it collides with the new third wheel."""
    shutil.copyfile(os.path.join(base, "stage2", "parts", "third.stl"), os.path.join(d, "parts", "third.stl"))
    edit(d, lambda doc: doc["fixed"].append("third"))


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
    ("s2 stage-1 design handed back unchanged", 2, use_stage(1), fails(2, "day_hand", "day_place")),
    ("s2 seconds hand declared as the 24-hour hand", 2,
     lambda d, b: edit(d, lambda doc: doc["hands"].update(day={"mobile": "seconds", "part": "seconds_hand"})), fails(2, "day_hand")),
    ("s2 a frozen wheel file changed", 2, lambda d, b: touch_part(d, "third"), 0.0),
    ("s3 gold", 3, lambda d, b: None, 1.0 * kept(2)),
    ("s3 do nothing", 3, lambda d, b: nothing(d), 0.0),
    ("s3 stage-2 movement handed back unchanged", 3, use_stage(2), fails(3, "hour", "minute", "seconds", "day_hand") * kept(0)),
    ("s3 every part file regenerated", 3, lambda d, b: touch_all(d), 1.0 * kept(17)),
    ("s3 a kept fixed part regenerated", 3, lambda d, b: touch_part(d, "dial"), 1.0 * kept(3)),
    ("s3 a kept mobile renamed", 3, lambda d, b: edit(d, rename_mobile("fourth", "fourth_b")), 1.0 * kept(3)),
    ("s3 old third wheel kept as a fixed ornament", 3, old_wheel_as_fixed, 0.0),
    ("s3 day train left undriven", 3, lambda d, b: edit(d, drop_mesh("hour_wheel", "day_idler")), fails(3, "day_hand", "clear") * kept(5)),
    ("s4 gold", 4, lambda d, b: None, 1.0),
    ("s4 no assembly.json", 4, lambda d, b: os.remove(os.path.join(d, "assembly.json")), 0.0),
    ("s4 a part file changed", 4, lambda d, b: touch_part(d, "dial"), 0.0),
    ("s4 centre before third", 4, lambda d, b: edit(d, reorder("centre_36", "third_54"), "assembly.json"), parts_score(1)),
    ("s4 dial jumps into place in one step", 4, lambda d, b: edit(d, teleport, "assembly.json"), parts_score(1)),
    ("s4 bridge on before the wheels", 4, lambda d, b: edit(d, reorder("bridge", "barrel"), "assembly.json"), parts_score(6)),
]


def run_one(args):
    i, base = args
    name, stage, change, want = ANCHORS[i]
    d = tempfile.mkdtemp()
    shutil.rmtree(d)
    shutil.copytree(os.path.join(base, "stage%d" % stage), d)
    change(d, base)
    r = grade(d, stage, os.path.join(base, "stage%d" % (stage - 1)) if stage > 1 else None)
    failed = [k for dd in (r["gates"], r["checks"]) for k, v in dd.items() if not v]
    ok = abs(r["reward"] - want) < 1e-6
    shutil.rmtree(d, ignore_errors=True)
    extra = "  kept %s" % r["details"]["kept"].get("share") if stage == 3 and "kept" in r["details"] else ""
    return ok, "%-4s %-46s S=%.4f expected %.4f  failed: %s%s" % ("ok" if ok else "OFF", name, r["reward"], want, ",".join(failed[:8]) or "-", extra)


def main():
    base = tempfile.mkdtemp()
    ref.main(base)
    bad = 0
    with Pool(int(sys.argv[1]) if len(sys.argv) > 1 else 3) as pool:
        for ok, line in pool.imap(run_one, [(i, base) for i in range(len(ANCHORS))]):
            bad += not ok
            print(line, flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
