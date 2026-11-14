"""Format-only submit for the watch task. Checks structure, never runs a test.
    python3 tools/submit.py
Reads ./work, copies movement.json, the parts it names and assembly.json (if present) to ./submission."""
import json
import math
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import kernel

MAX_PARTS = __MAX_PARTS__
MAX_TRIANGLES = __MAX_TRIANGLES__
MAX_STL_BYTES = __MAX_STL_BYTES__
NAME = re.compile(r"__NAME_RE__")
WORK, SUBMIT = os.path.join(os.getcwd(), "work"), os.path.join(os.getcwd(), "submission")


class Bad(Exception):
    pass


def xy(v, where):
    if not (isinstance(v, list) and len(v) == 2 and all(isinstance(c, (int, float)) and math.isfinite(c) for c in v)):
        raise Bad("%s must be [x, y]" % where)


def main():
    try:
        with open(os.path.join(WORK, "movement.json")) as f:
            doc = json.load(f)
    except (OSError, ValueError):
        raise Bad("work/movement.json is missing or not valid JSON")
    if not isinstance(doc, dict):
        raise Bad("movement.json: top level must be an object")
    xy(doc.get("case_centre"), "case_centre")
    names = []

    def take(lst, where):
        if not isinstance(lst, list) or not lst:
            raise Bad("%s: needs a non-empty list of part names" % where)
        for n in lst:
            if not isinstance(n, str) or not NAME.match(n):
                raise Bad("%s: bad part name %r" % (where, n))
            if n in names:
                raise Bad("part '%s' is used more than once" % n)
            names.append(n)
    take(doc.get("fixed"), "fixed")
    mob = doc.get("mobiles")
    if not isinstance(mob, dict) or not mob:
        raise Bad("'mobiles' must be a non-empty object")
    for k, m in mob.items():
        if not NAME.match(str(k)) or k == "barrel" or not isinstance(m, dict):
            raise Bad("bad mobile %r" % (k,))
        xy(m.get("axis"), "mobile '%s' axis" % k)
        take(m.get("parts"), "mobile '%s'" % k)
    if len(names) > MAX_PARTS:
        raise Bad("more than %d parts" % MAX_PARTS)
    known = set(mob) | {"barrel"}
    for i, e in enumerate(doc.get("meshes") or []):
        if not isinstance(e, dict) or e.get("driver") not in known or e.get("driven") not in known or e.get("driver") == e.get("driven"):
            raise Bad("meshes[%d]: unknown or repeated mobile" % i)
        if not all(isinstance(e.get(t), int) and 3 <= e[t] <= 1000 for t in ("driver_teeth", "driven_teeth")):
            raise Bad("meshes[%d]: tooth counts must be integers from 3 to 1000" % i)
    hands = doc.get("hands")
    if not isinstance(hands, dict):
        raise Bad("'hands' must be an object")
    for h in ("hour", "minute", "seconds", "day"):
        e = hands.get(h)
        if e is None and h == "day":
            continue
        if not isinstance(e, dict) or e.get("mobile") not in mob or e.get("part") not in mob[e["mobile"]]["parts"]:
            raise Bad("hands.%s: needs 'mobile' and a 'part' that belongs to that mobile" % h)
    for n in names:
        p = os.path.join(WORK, "parts", n + ".stl")
        if not os.path.isfile(p):
            raise Bad("parts/%s.stl not found" % n)
        try:
            kernel.load_part(p, MAX_TRIANGLES, MAX_STL_BYTES, 0.005)
        except kernel.FormatError as e:
            raise Bad("parts/%s.stl: %s" % (n, e))
    asm = os.path.join(WORK, "assembly.json")
    if os.path.isfile(asm):
        try:
            with open(asm) as f:
                a = json.load(f)
        except ValueError:
            raise Bad("assembly.json is not valid JSON")
        if not isinstance(a, dict) or not isinstance(a.get("order"), list) or not isinstance(a.get("paths"), dict):
            raise Bad("assembly.json: needs a list 'order' and an object 'paths'")
    if os.path.isdir(SUBMIT):
        shutil.rmtree(SUBMIT)
    os.makedirs(os.path.join(SUBMIT, "parts"))
    shutil.copyfile(os.path.join(WORK, "movement.json"), os.path.join(SUBMIT, "movement.json"))
    for n in names:
        shutil.copyfile(os.path.join(WORK, "parts", n + ".stl"), os.path.join(SUBMIT, "parts", n + ".stl"))
    if os.path.isfile(asm):
        shutil.copyfile(asm, os.path.join(SUBMIT, "assembly.json"))
    print(json.dumps({"result": "accepted", "parts": len(names), "assembly": os.path.isfile(asm)}))


if __name__ == "__main__":
    try:
        main()
    except Bad as e:
        print(json.dumps({"format_error": str(e)}))
        sys.exit(1)
