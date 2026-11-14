"""Format check of a delivery folder. Checks the file format only; it runs none of the acceptance checks.
    python3 tools/check_format.py [FOLDER]
FOLDER defaults to the folder `delivery` next to this tools folder. Checks movement.json, variant_6h.json
and assembly.json (each when present: a missing file is reported, and the rest is still checked), the part
names, every part file they name, read and turned into a solid exactly as the inspection does, and report.json
when it is there (optional; its layout only, not whether its statements are right).
Prints "format ok" or every format error found, one per line, and exits 0 or 1. Copies and changes nothing."""
import json
import math
import os
import re
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
MATERIALS = __MATERIAL_DESIGNATIONS__
REPORT_MAX_BYTES = __REPORT_MAX_BYTES__
REPORT_PARTS = __REPORT_PARTS__
REPORT_CLAIMS = __REPORT_CLAIMS__
NAME = re.compile(r"__NAME_RE__")
MOVEMENT_FILES = ("movement.json", "variant_6h.json")


class Bad(Exception):
    pass


def real_file(folder, rel):
    """The path of rel inside folder; Bad if it, or a folder on the way, is a symbolic link or leads outside."""
    cur = folder
    for comp in rel.split("/"):
        cur = os.path.join(cur, comp)
        if os.path.islink(cur):
            raise Bad("%s is a symbolic link; delivered files must be real files in the folder" % rel)
    if os.path.exists(cur):
        real, root = os.path.realpath(cur), os.path.realpath(folder)
        if os.path.commonpath([real, root]) != root:
            raise Bad("%s lies outside the delivery folder" % rel)
    return cur


def read_json(folder, rel, limit):
    p = real_file(folder, rel)
    if not os.path.isfile(p):
        raise Bad("%s is missing" % rel)
    if os.path.getsize(p) > limit:
        raise Bad("%s is larger than %d bytes" % (rel, limit))
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except ValueError:
        raise Bad("%s is not valid JSON" % rel)


def xy(v, where):
    if not (isinstance(v, list) and len(v) == 2 and all(isinstance(c, (int, float)) and not isinstance(c, bool)
                                                        and math.isfinite(c) for c in v)):
        raise Bad("%s must be [x, y]" % where)


def movement_names(doc, rel):
    """The part names of one movement file, after checking its layout."""
    if not isinstance(doc, dict):
        raise Bad("%s: top level must be an object" % rel)
    xy(doc.get("case_centre"), "%s: case_centre" % rel)
    names = []

    def take(lst, where):
        if not isinstance(lst, list) or not lst:
            raise Bad("%s: %s needs a non-empty list of part names" % (rel, where))
        for n in lst:
            if not isinstance(n, str) or not NAME.match(n):
                raise Bad("%s: %s: bad part name %r (letters, digits, _ and -, 1 to %d characters)" % (rel, where, n, MAX_NAME_LEN))
            if n == "barrel":
                raise Bad("%s: %s: 'barrel' is the supplied barrel and cannot be a part name" % (rel, where))
            if n in names:
                raise Bad("%s: part '%s' is named more than once" % (rel, n))
            names.append(n)
    take(doc.get("fixed"), "fixed")
    mob = doc.get("mobiles")
    if not isinstance(mob, dict) or not mob:
        raise Bad("%s: 'mobiles' must be a non-empty object" % rel)
    for k, m in mob.items():
        if not NAME.match(str(k)) or k == "barrel" or not isinstance(m, dict):
            raise Bad("%s: bad mobile %r (letters, digits, _ and -, 1 to %d characters, not 'barrel')" % (rel, k, MAX_NAME_LEN))
        xy(m.get("axis"), "%s: mobile '%s' axis" % (rel, k))
        take(m.get("parts"), "mobile '%s'" % k)
        if not isinstance(m.get("material"), str) or m["material"] not in MATERIALS:
            raise Bad("%s: mobile '%s': 'material' must be the designation of a material with a bending (tensile) "
                      "design allowable in DS-201 section 8" % (rel, k))
        pm = m.get("part_materials", {})
        if not isinstance(pm, dict):
            raise Bad("%s: mobile '%s': 'part_materials' must be an object {part name: designation}" % (rel, k))
        for pn, pmat in pm.items():
            if pn not in m["parts"]:
                raise Bad("%s: mobile '%s': 'part_materials' names %r, which is not a part of this mobile" % (rel, k, pn))
            if not isinstance(pmat, str) or pmat not in MATERIALS:
                raise Bad("%s: mobile '%s': 'part_materials' of part '%s' must be the designation of a material with a "
                          "bending (tensile) design allowable in DS-201 section 8" % (rel, k, pn))
    if len(names) > MAX_PARTS:
        raise Bad("%s: more than %d parts" % (rel, MAX_PARTS))
    known = set(mob) | {"barrel"}
    meshes = doc.get("meshes")
    if meshes is not None and not isinstance(meshes, list):
        raise Bad("%s: 'meshes' must be a list" % rel)
    for i, e in enumerate(meshes or []):
        if not isinstance(e, dict) or e.get("driver") not in known or e.get("driven") not in known or e.get("driver") == e.get("driven"):
            raise Bad("%s: meshes[%d]: unknown or repeated mobile" % (rel, i))
        if not all(isinstance(e.get(t), int) and not isinstance(e.get(t), bool) and MIN_TEETH <= e[t] <= MAX_TEETH
                   for t in ("driver_teeth", "driven_teeth")):
            raise Bad("%s: meshes[%d]: tooth counts must be integers from %d to %d" % (rel, i, MIN_TEETH, MAX_TEETH))
    hands = doc.get("hands")
    if not isinstance(hands, dict):
        raise Bad("%s: 'hands' must be an object" % rel)
    for h in ("hour", "minute", "seconds", "day"):
        e = hands.get(h)
        if e is None and h == "day":
            continue
        if not isinstance(e, dict) or e.get("mobile") not in mob or e.get("part") not in mob[e["mobile"]]["parts"]:
            raise Bad("%s: hands.%s needs 'mobile' and a 'part' that belongs to that mobile" % (rel, h))
    return names


def load_part(folder, n):
    p = real_file(folder, "parts/" + n + ".step")
    if not os.path.isfile(p):
        if os.path.isfile(os.path.join(folder, "parts", n + ".stl")):
            raise Bad("parts/%s.stl: parts must be STEP files (parts/%s.step); STL is not accepted" % (n, n))
        raise Bad("parts/%s.step not found" % n)
    try:
        kernel.load_step_part(p, MAX_STEP_BYTES, MAX_TRIANGLES, STEP_LINEAR_DEFLECTION, STEP_ANGULAR_DEFLECTION,
                              STEP_MAX_TRIANGLE_FACES, STEP_TIMEOUT_S, STEP_MEMORY_MB, SELF_UNION_TOL)
    except kernel.FormatError as e:
        raise Bad("parts/%s.step: %s" % (n, e))


def check_assembly(folder):
    a = read_json(folder, "assembly.json", MAX_ASSEMBLY_BYTES)
    if not isinstance(a, dict) or not isinstance(a.get("order"), list) or not isinstance(a.get("paths"), dict):
        raise Bad("assembly.json: needs a list 'order' and an object 'paths'")
    for n, P in a["paths"].items():
        ok = isinstance(P, list) and all(isinstance(T, list) and len(T) == 4 and all(
            isinstance(row, list) and len(row) == 4 and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                                            for v in row) for row in T) for T in P)
        if not ok:
            raise Bad("assembly.json: paths.%s must be a list of 4x4 matrices (four rows of four numbers)" % n)


def check_report(folder):
    """report.json, if present: its layout only (FORMAT.md). An invalid one counts every part as not_tested."""
    p = os.path.join(folder, "report.json")
    if not os.path.lexists(p):
        return
    doc = read_json(folder, "report.json", REPORT_MAX_BYTES)
    if not isinstance(doc, dict) or not isinstance(doc.get("parts"), dict):
        raise Bad("report.json: top level must be an object with an object 'parts'")
    for k, v in doc["parts"].items():
        if k not in REPORT_PARTS:
            raise Bad("report.json: parts: %r is not a part of the inspection (%s)" % (k, ", ".join(REPORT_PARTS)))
        if v not in REPORT_CLAIMS:
            raise Bad("report.json: parts.%s must be one of %s" % (k, ", ".join(REPORT_CLAIMS)))


def check_scripts(folder):
    d = os.path.join(folder, "scripts")
    if not os.path.isdir(d):
        return
    files, total = 0, 0
    for root, dirs, fs in os.walk(d):
        for f in fs:
            p = os.path.join(root, f)
            if os.path.isfile(p) and not os.path.islink(p):
                files += 1
                total += os.path.getsize(p)
    if files > MAX_SCRIPT_FILES:
        raise Bad("scripts/ holds more than %d files" % MAX_SCRIPT_FILES)
    if total > MAX_SCRIPTS_BYTES:
        raise Bad("scripts/ holds more than %d bytes" % MAX_SCRIPTS_BYTES)


def main(argv):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    folder = os.path.abspath(argv[0]) if argv else os.path.join(here, "delivery")
    errors, parts = [], []

    def run(fn, *args):
        try:
            return fn(*args)
        except Bad as e:
            errors.append(str(e))
    for rel in MOVEMENT_FILES:
        doc = run(read_json, folder, rel, MAX_JSON_BYTES)
        if doc is not None:
            names = run(movement_names, doc, rel)
            parts += [n for n in names or [] if n not in parts]
    run(lambda: real_file(folder, "parts"))
    for n in parts:
        run(load_part, folder, n)
    run(check_assembly, folder)
    run(check_report, folder)
    run(check_scripts, folder)
    if errors:
        for e in errors:
            print(e)
        return 1
    print("format ok")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
