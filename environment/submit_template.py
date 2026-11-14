"""Format-only submit for the watch task. Checks structure, never runs a test.
    python3 tools/submit.py
Reads ./work, copies movement.json, the parts it names and assembly.json (if present) to ./submission,
and ./scripts (if present) to ./submission/scripts. Each part is parts/<name>.step (STL parts are not
accepted). Every part is loaded exactly as the grader loads it."""
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
MAX_STEP_BYTES = __MAX_STEP_BYTES__
STEP_LINEAR_DEFLECTION = __STEP_LINEAR_DEFLECTION__
STEP_ANGULAR_DEFLECTION = __STEP_ANGULAR_DEFLECTION__
STEP_MAX_TRIANGLE_FACES = __STEP_MAX_TRIANGLE_FACES__
STEP_TIMEOUT_S = __STEP_TIMEOUT_S__
STEP_MEMORY_MB = __STEP_MEMORY_MB__
SELF_UNION_TOL = __SELF_UNION_TOL__
MAX_SCRIPTS_BYTES = __MAX_SCRIPTS_BYTES__
MAX_SCRIPT_FILES = __MAX_SCRIPT_FILES__
MAX_JSON_BYTES = __MAX_JSON_BYTES__
MAX_ASSEMBLY_BYTES = __MAX_ASSEMBLY_BYTES__
MIN_TEETH, MAX_TEETH = __MIN_TEETH__, __MAX_TEETH__
MAX_NAME_LEN = __MAX_NAME_LEN__
NAME = re.compile(r"__NAME_RE__")
WORK, SUBMIT = os.path.join(os.getcwd(), "work"), os.path.join(os.getcwd(), "submission")
SCRIPTS = os.path.join(os.getcwd(), "scripts")


class Bad(Exception):
    pass


def part_file(n):
    p = os.path.join(WORK, "parts", n + ".step")
    if os.path.isfile(p):
        return p
    if os.path.isfile(os.path.join(WORK, "parts", n + ".stl")):
        raise Bad("parts/%s.stl: parts must be STEP files (parts/%s.step); STL is not accepted" % (n, n))
    return None


def load(p):
    """The part as the grader builds it (a manifold3d solid)."""
    return kernel.load_step_part(p, MAX_STEP_BYTES, MAX_TRIANGLES, STEP_LINEAR_DEFLECTION, STEP_ANGULAR_DEFLECTION,
                                 STEP_MAX_TRIANGLE_FACES, STEP_TIMEOUT_S, STEP_MEMORY_MB, SELF_UNION_TOL)


def script_files():
    """Regular files under ./scripts (relative paths), within the size limits."""
    out, total = [], 0
    if not os.path.isdir(SCRIPTS):
        return out
    for root, dirs, files in os.walk(SCRIPTS):
        dirs[:] = sorted(d for d in dirs if not os.path.islink(os.path.join(root, d)) and d != "__pycache__")
        for f in sorted(files):
            p = os.path.join(root, f)
            if os.path.islink(p) or not os.path.isfile(p):
                continue
            total += os.path.getsize(p)
            out.append(os.path.relpath(p, SCRIPTS))
            if len(out) > MAX_SCRIPT_FILES:
                raise Bad("scripts/ holds more than %d files" % MAX_SCRIPT_FILES)
            if total > MAX_SCRIPTS_BYTES:
                raise Bad("scripts/ holds more than %d bytes" % MAX_SCRIPTS_BYTES)
    return out


def xy(v, where):
    if not (isinstance(v, list) and len(v) == 2 and all(isinstance(c, (int, float)) and math.isfinite(c) for c in v)):
        raise Bad("%s must be [x, y]" % where)


def main():
    mj = os.path.join(WORK, "movement.json")
    if os.path.isfile(mj) and os.path.getsize(mj) > MAX_JSON_BYTES:
        raise Bad("movement.json larger than %d bytes" % MAX_JSON_BYTES)
    try:
        with open(mj) as f:
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
                raise Bad("%s: bad part name %r (letters, digits, _ and -, 1 to %d characters)" % (where, n, MAX_NAME_LEN))
            if n == "barrel":
                raise Bad("%s: 'barrel' is the supplied barrel and cannot be a part name" % where)
            if n in names:
                raise Bad("part '%s' is used more than once" % n)
            names.append(n)
    take(doc.get("fixed"), "fixed")
    mob = doc.get("mobiles")
    if not isinstance(mob, dict) or not mob:
        raise Bad("'mobiles' must be a non-empty object")
    for k, m in mob.items():
        if not NAME.match(str(k)) or k == "barrel" or not isinstance(m, dict):
            raise Bad("bad mobile %r (letters, digits, _ and -, 1 to %d characters, not 'barrel')" % (k, MAX_NAME_LEN))
        xy(m.get("axis"), "mobile '%s' axis" % k)
        take(m.get("parts"), "mobile '%s'" % k)
    if len(names) > MAX_PARTS:
        raise Bad("more than %d parts" % MAX_PARTS)
    known = set(mob) | {"barrel"}
    for i, e in enumerate(doc.get("meshes") or []):
        if not isinstance(e, dict) or e.get("driver") not in known or e.get("driven") not in known or e.get("driver") == e.get("driven"):
            raise Bad("meshes[%d]: unknown or repeated mobile" % i)
        if not all(isinstance(e.get(t), int) and not isinstance(e.get(t), bool) and MIN_TEETH <= e[t] <= MAX_TEETH
                   for t in ("driver_teeth", "driven_teeth")):
            raise Bad("meshes[%d]: tooth counts must be integers from %d to %d" % (i, MIN_TEETH, MAX_TEETH))
    hands = doc.get("hands")
    if not isinstance(hands, dict):
        raise Bad("'hands' must be an object")
    for h in ("hour", "minute", "seconds", "day"):
        e = hands.get(h)
        if e is None and h == "day":
            continue
        if not isinstance(e, dict) or e.get("mobile") not in mob or e.get("part") not in mob[e["mobile"]]["parts"]:
            raise Bad("hands.%s: needs 'mobile' and a 'part' that belongs to that mobile" % h)
    files = {}
    for n in names:
        p = part_file(n)
        if p is None:
            raise Bad("parts/%s.step not found" % n)
        try:
            load(p)
        except kernel.FormatError as e:
            raise Bad("parts/%s: %s" % (os.path.basename(p), e))
        files[n] = p
    scripts = script_files()
    asm = os.path.join(WORK, "assembly.json")
    if os.path.isfile(asm):
        if os.path.getsize(asm) > MAX_ASSEMBLY_BYTES:
            raise Bad("assembly.json larger than %d bytes" % MAX_ASSEMBLY_BYTES)
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
    for n, p in files.items():
        shutil.copyfile(p, os.path.join(SUBMIT, "parts", os.path.basename(p)))
    if os.path.isfile(asm):
        shutil.copyfile(asm, os.path.join(SUBMIT, "assembly.json"))
    for rel in scripts:
        dst = os.path.join(SUBMIT, "scripts", rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(os.path.join(SCRIPTS, rel), dst)
    print(json.dumps({"result": "accepted", "parts": len(names),
                      "assembly": os.path.isfile(asm), "scripts": len(scripts)}))


if __name__ == "__main__":
    try:
        main()
    except Bad as e:
        print(json.dumps({"format_error": str(e)}))
        sys.exit(1)
