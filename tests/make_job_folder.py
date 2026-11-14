"""Build a one-job delivery folder from the four stage folders that solution/reference_watch.py writes.
    python3 tests/make_job_folder.py /abs/REF_OUT /abs/DEST [--assembly as-is|mapped]
REF_OUT holds stage1..stage4. DEST gets:
  movement.json      stage2/movement.json (the 8-hour movement with the day hand)
  variant_6h.json    stage3/movement.json (the 6-hour movement)
  parts/             stage2/parts plus stage3/parts in one folder. A name in both with different bytes is an
                     error (reported, never renamed away).
  assembly.json      stage4/assembly.json. Stage 4's plan was made for the 6-hour movement. With 'as-is' it is
                     copied unchanged. With 'mapped' (the default) every part name of the 6-hour movement that
                     movement.json does not have is replaced by the part at the same place (same mobile, same
                     index in its part list) of movement.json, with the same path.
Only a test fixture: the reference itself will write a job folder (builder R)."""
import json
import os
import shutil
import sys


class Collision(Exception):
    pass


def _same(a, b):
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def part_map(movement, variant):
    """{variant part name: movement part name} for the parts at the same place (same mobile name, same
    index in its part list) whose names differ and whose variant name movement.json does not use."""
    used = set(movement["fixed"]) | {p for mo in movement["mobiles"].values() for p in mo["parts"]}
    out = {}
    for name, mo in variant["mobiles"].items():
        old = movement["mobiles"].get(name)
        if not old:
            continue
        for a, b in zip(mo["parts"], old["parts"]):
            if a != b and a not in used:
                out[a] = b
    for a, b in zip(variant["fixed"], movement["fixed"]):
        if a != b and a not in used:
            out[a] = b
    return out


def make(ref, dest, assembly="mapped"):
    """Write the job folder; returns {"collisions": [...], "mapped": {...}}. Raises Collision if a part name
    appears in stage2 and stage3 with different bytes."""
    s2, s3, s4 = (os.path.join(ref, "stage%d" % i) for i in (2, 3, 4))
    if os.path.exists(dest):
        shutil.rmtree(dest)
    os.makedirs(os.path.join(dest, "parts"))
    shutil.copyfile(os.path.join(s2, "movement.json"), os.path.join(dest, "movement.json"))
    shutil.copyfile(os.path.join(s3, "movement.json"), os.path.join(dest, "variant_6h.json"))
    collisions = []
    for src in (s2, s3):
        for n in sorted(os.listdir(os.path.join(src, "parts"))):
            a, b = os.path.join(src, "parts", n), os.path.join(dest, "parts", n)
            if os.path.exists(b):
                if not _same(a, b):
                    collisions.append(n)
                continue
            shutil.copyfile(a, b)
    if collisions:
        raise Collision("same part name, different bytes in stage2 and stage3: %s" % ", ".join(collisions))
    with open(os.path.join(s4, "assembly.json")) as f:
        asm = json.load(f)
    mapping = {}
    if assembly == "mapped":
        with open(os.path.join(s2, "movement.json")) as f:
            mv = json.load(f)
        with open(os.path.join(s3, "movement.json")) as f:
            var = json.load(f)
        mapping = part_map(mv, var)
        asm["order"] = [mapping.get(n, n) for n in asm["order"]]
        asm["paths"] = {mapping.get(n, n): p for n, p in asm["paths"].items()}
    with open(os.path.join(dest, "assembly.json"), "w") as f:
        json.dump(asm, f)
    return {"collisions": collisions, "mapped": mapping}


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mode = sys.argv[sys.argv.index("--assembly") + 1] if "--assembly" in sys.argv else "mapped"
    args = [a for a in args if a != mode]
    print(json.dumps(make(os.path.abspath(args[0]), os.path.abspath(args[1]), mode)))
