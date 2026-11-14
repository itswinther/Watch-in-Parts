"""Reference set for the four-stage watch task.
    python tests/test_anchors_watch.py [WORKERS] [--only NAME[,NAME...]] [--base REF_DIR]
--only runs the anchors whose name contains one of the given texts (exact name match wins if one is exact).
--base reuses a reference already written by solution/reference_watch.py instead of building one.
Builds the reference for all four stages, changes one thing per anchor, grades it and asserts the score.
Gold is 1.00 at every stage, do-nothing 0.00, likely shortcuts and partial work lower.
Anchors are graded in parallel (default 3 worker processes)."""
import json
import math
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


def kept(lost):
    """Stage-3 kept factor when the received parts named in `lost` do not count (every part when lost is
    None): kept volume over received volume, fixed and mobile parts separately, the smaller share against
    the reference's. An expected value computed from the reference's stage-2 files: call it with (d, base)."""
    def factor(d, base):
        prev = os.path.join(base, "stage2")
        doc = json.load(open(os.path.join(prev, "movement.json")))
        groups = {"fixed": doc["fixed"], "mobile": [p for mo in doc["mobiles"].values() for p in mo["parts"]]}
        shares = []
        for names in groups.values():
            v = {n: float(W.load_part_file(W.part_path(prev, n)).volume()) for n in names}
            shares.append(sum(x for n, x in v.items() if lost is not None and n not in lost) / sum(v.values()))
        return min(1.0, min(shares) / W.REF_KEPT_VOLUME_SHARE)
    return factor


REF_REMADE = ("third", "centre")     # the received parts the reference remakes at stage 3


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


def part_file(d, part):
    return W.part_path(d, part)


def touch_part(d, part):
    """Same geometry, different bytes (the STEP header's file name; for an STL, its 80-byte header)."""
    p = part_file(d, part)
    with open(p, "rb") as f:
        data = f.read()
    if p.endswith(".step"):
        new = data.replace(b"FILE_NAME('", b"FILE_NAME('changed_", 1)
        assert new != data, "no FILE_NAME in " + p
    else:
        new = b"changed".ljust(80, b" ") + data[80:]
    with open(p, "wb") as f:
        f.write(new)


def nothing(d):
    shutil.rmtree(os.path.join(d, "parts"))
    os.remove(os.path.join(d, "movement.json"))


def swap_hands(doc):
    doc["hands"]["hour"], doc["hands"]["minute"] = doc["hands"]["minute"], doc["hands"]["hour"]


def dup_fixed(d):
    src = part_file(d, "bridge")
    shutil.copyfile(src, os.path.join(d, "parts", "bridge_copy" + os.path.splitext(src)[1]))
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
        touch_part(d, os.path.splitext(n)[0])


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


def day_on_received(d, base):
    """The stage-1 movement with only hands.day pointed at the received seconds hand."""
    use_stage(1)(d, base)
    edit(d, lambda doc: doc["hands"].update(day={"mobile": "seconds", "part": "seconds_hand"}))


def paper_edit(d, base):
    """The received stage-2 movement with only the third/centre tooth counts changed to 54/36 in movement.json."""
    use_stage(2)(d, base)

    def fn(doc):
        for e in doc["meshes"]:
            if (e["driver"], e["driven"]) == ("third", "centre"):
                e["driver_teeth"], e["driven_teeth"] = 54, 36
    edit(d, fn)


def old_wheel_as_fixed(d, base):
    """Keep the received third-wheel file and declare it a fixed ornament, moved out of the way by
    renaming nothing: it stands where it always stood, so it collides with the new third wheel."""
    src = part_file(os.path.join(base, "stage2"), "third")
    shutil.copyfile(src, os.path.join(d, "parts", os.path.basename(src)))
    edit(d, lambda doc: doc["fixed"].append("third"))


def _excess(limit, used):
    """A volume that takes `used` 10 percent of `limit` over `limit`."""
    return limit - used + 0.1 * limit


def heavy_fixed_block(d, base):
    """One extra fixed part: a slab under the main plate, centred under the minute hand's axis (where the plate
    carries the centre arbor's bearing), its top face on the plate's bottom face so it is joined to the frame. It is
    as thick as the height limit leaves (less 0.01), inside the case, below every mobile, and big enough to take the
    fixed parts 10 percent of FIXED_VOLUME_MAX over that limit."""
    import cadquery as cq
    from geometry.core import write_step
    m = W.load_movement(d)
    e = m.extent()
    t = W.CASE_HEIGHT - (e["z_max"] - e["z_min"]) - 0.01
    side = math.sqrt(_excess(W.FIXED_VOLUME_MAX, m.volumes()[0]) / t)
    x, y = m.mobiles[m.hands["minute"][0]]["axis"]
    slab = cq.Workplane("XY").box(side, side, t, centered=(True, True, False)).translate((x, y, e["z_min"] - t))
    write_step(os.path.join(d, "parts", "ballast.step"), slab)
    edit(d, lambda doc: doc["fixed"].append("ballast"))


def heavy_mobile(d, base):
    """One extra part on the minute hand's mobile (driven): a disc on the top of the centre arbor, resting on the
    minute hand, bored to the arbor's top step (radius 0.35 in the reference's centre_arbor, plus its FIT), up to
    the arbor's top, so the movement gets no taller. Its radius takes the mobile parts 10 percent of
    MOBILE_VOLUME_MAX over that limit. Seated (bore on the arbor, resting on the hand), one piece with the mobile,
    clear of everything else (nothing else reaches above the minute hand)."""
    import cadquery as cq
    from geometry.core import write_step
    m = W.load_movement(d)
    mob, hand_part = m.hands["minute"]
    x, y = m.mobiles[mob]["axis"]
    z0 = m.mobiles[mob]["parts"][hand_part].bounding_box()[5]
    z1 = m.mobiles[mob]["solid"].bounding_box()[5]
    bore = 0.35 + ref.FIT
    r = math.sqrt(_excess(W.MOBILE_VOLUME_MAX, m.volumes()[1]) / (math.pi * (z1 - z0)) + bore * bore)
    disc = cq.Workplane("XY").workplane(offset=z0).center(x, y).circle(r).circle(bore).extrude(z1 - z0)
    write_step(os.path.join(d, "parts", "ballast_disc.step"), disc)
    edit(d, lambda doc: doc["mobiles"][mob]["parts"].append("ballast_disc"))


# (name, stage, change(folder, base), expected score)
# ---- parts of one mobile (seated, no overlap, stage-4 every pair). Chosen from movement.json, no names assumed.
def _doc_of(d):
    with open(os.path.join(d, "movement.json")) as f:
        return json.load(f)


def _wheel_of(d):
    """(mobile, part): in the first mobile with at least two parts that are not hands, its least tall
    non-hand part (a wheel on its arbor), judged from the loaded solids."""
    doc = _doc_of(d)
    hands = {h["part"] for h in doc["hands"].values()}
    m = W.load_movement(d)
    for k, mo in doc["mobiles"].items():
        cand = [p for p in mo["parts"] if p not in hands]
        if len(cand) >= 2:
            z = {p: m.mobiles[k]["parts"][p].bounding_box() for p in cand}
            return k, min(cand, key=lambda p: z[p][5] - z[p][2])
    raise RuntimeError("no mobile with two parts that are not hands")


def move_part_up(dz):
    def fn(d, base):
        import cadquery as cq
        from geometry import core
        _, part = _wheel_of(d)
        p = part_file(d, part)
        shape = cq.importers.importStep(p).translate((0, 0, dz))
        core.write_step(p, shape)
    return fn


def dup_mobile_part(d, base):
    """A copy of a part of a multi-part mobile added to the same mobile: the two overlap completely."""
    k, part = _wheel_of(d)
    src = part_file(d, part)
    shutil.copyfile(src, os.path.join(d, "parts", part + "_copy" + os.path.splitext(src)[1]))
    edit(d, lambda doc: doc["mobiles"][k]["parts"].append(part + "_copy"))


def swap_within_mobile(d, base):
    """Stage 4: of two parts of one mobile that are closest in the order, the earlier one (e.g. an arbor) is put
    in right after the later one (a wheel that sits on it) instead of before it. It then has to pass through
    that part, and only it fails: the parts in between keep their places in the order."""
    doc = _doc_of(d)
    with open(os.path.join(d, "assembly.json")) as f:
        order = json.load(f)["order"]
    best = None
    for mo in doc["mobiles"].values():
        idx = sorted(order.index(p) for p in mo["parts"] if p in order)
        for i, j in zip(idx, idx[1:]):
            if best is None or j - i < best[1] - best[0]:
                best = (i, j)
    a, b = order[best[0]], order[best[1]]

    def fn(asm):
        asm["order"].remove(a)
        asm["order"].insert(asm["order"].index(b) + 1, a)
    edit(d, fn, "assembly.json")


def fat_seconds_pinion(d, base):
    """Stage 1: the seconds pinion remade with fat teeth (backlash allowance -0.075 on the pitch circle instead
    of +0.03). Measured on the reference: drawn, the pair still runs (worst overlap 0.0067 of 0.01 allowed);
    moved 0.03 towards the fourth wheel it jams (0.0144)."""
    from geometry import watch_gears_cad as GC
    from geometry import core
    P = ref.place()
    T, S = P["fourth"], P["seconds"]
    lo, hi = ref.PLATE[1] + 0.1, ref.BRIDGE[0] - 0.1
    ph_w3 = math.degrees(ref.ang(T, S))                       # the fourth wheel is drawn with a tooth on the line
    _, ph = ref.gear_at(S, 12, ref.M_D, ref.Z["D"], ref.ang(S, T), (96, ph_w3))
    p4 = GC.gear(12, ref.M_D, ref.Z["D"][0], ref.Z["D"][1], phase_deg=ph, x=S[0], y=S[1], backlash=-0.075)
    core.write_step(part_file(d, "seconds"), ref.hand_arbor(S, lo, hi, p4))


def thin_seconds_pinion(d, base):
    """Stage 1: the seconds pinion (12 teeth, module 0.2) remade with teeth thinned by a backlash allowance of
    0.15 on the pitch circle instead of 0.03. Measured on the reference: drawn, the fourth wheel pushed a quarter
    pitch overlaps it by only 0.0066 (more than 0.01 needed), so the pair does not drive; moved 0.03 away, 0.0034.
    (A 24-tooth pinion does not give a valid solid at this allowance; the 12-tooth one does.)"""
    from geometry import watch_gears_cad as GC
    from geometry import core
    P = ref.place()
    T, S = P["fourth"], P["seconds"]
    lo, hi = ref.PLATE[1] + 0.1, ref.BRIDGE[0] - 0.1
    _, ph = ref.gear_at(S, 12, ref.M_D, ref.Z["D"], ref.ang(S, T), (96, math.degrees(ref.ang(T, S))))
    p4 = GC.gear(12, ref.M_D, ref.Z["D"][0], ref.Z["D"][1], phase_deg=ph, x=S[0], y=S[1], backlash=0.15)
    core.write_step(part_file(d, "seconds"), ref.hand_arbor(S, lo, hi, p4))


def coarse_third_pinion(d, base):
    """Stage 1: the third pinion (24 teeth, driven by the supplied 96-tooth barrel, module 0.2) cut at module
    0.206 (3 percent too coarse), same tooth count, same axis and phase, same third wheel and arbor."""
    from geometry import watch_gears_cad as GC
    from geometry import core
    P = ref.place()
    B, I, C = P["barrel"], P["third"], P["centre"]
    lo, hi = ref.PLATE[1] + 0.1, ref.BRIDGE[0] - 0.1
    _, ph = ref.gear_at(I, 24, ref.M_A, ref.Z["A"], ref.ang(I, B), (96, 0.0))
    p1 = GC.gear(24, ref.M_A * 1.03, ref.Z["A"][0], ref.Z["A"][1], phase_deg=ph, x=I[0], y=I[1])
    w1, _ = ref.wheel_at(I, 60, ref.M_B, ref.Z["B"], ref.ang(I, C))
    core.write_step(part_file(d, "third"), ref.union([ref.arbor(I, lo, hi), p1, w1]))


ANCHORS = [
    ("s1 gold", 1, lambda d, b: None, 1.0),
    ("s1 do nothing", 1, lambda d, b: nothing(d), 0.0),
    ("s1 a part file missing", 1, lambda d, b: os.remove(part_file(d, "fourth")), 0.0),
    ("s1 two fixed parts overlap", 1, lambda d, b: dup_fixed(d), 0.0),
    ("s1 hour and minute hands swapped", 1, lambda d, b: edit(d, swap_hands), fails(1, "hour", "minute")),
    ("s1 one tooth count declared wrong", 1, lambda d, b: edit(d, lambda doc: doc["meshes"][1].update(driven_teeth=31)),
     fails(1, "train", "tolerant", "minute", "hour", "seconds")),     # the jam shows in the shifted positions too
    ("s1 barrel not held from above", 1, lambda d, b: edit(d, lambda doc: doc["fixed"].remove("barrel_cock")), fails(1, "held")),
    # mass budget: one extra part takes the fixed parts, or the mobile parts, 10 percent over the limit
    ("s1 one extra solid block added as a fixed part", 1, heavy_fixed_block, fails(1, "light")),
    ("s1 a heavy disc added to a driven mobile", 1, heavy_mobile, fails(1, "light")),
    # tooth exactness: the thinned pinion does not drive, so the seconds hand downstream stands still
    ("s1 a pinion with teeth thinned until they no longer drive", 1, thin_seconds_pinion, fails(1, "train", "tolerant", "seconds")),
    ("s1 a pinion cut 3 percent too coarse", 1, coarse_third_pinion, fails(1, "tolerant")),
    ("s2 gold", 2, lambda d, b: None, 1.0),
    ("s2 stage-1 design handed back unchanged", 2, use_stage(1), 0.0),          # no day hand declared: hard requirement
    ("s2 seconds hand declared as the 24-hour hand", 2,
     lambda d, b: edit(d, lambda doc: doc["hands"].update(day={"mobile": "seconds", "part": "seconds_hand"})), 0.0),   # received part: gate
    ("s2 day hand declared on a received hand part", 2, day_on_received, 0.0),   # stage-1 movement plus one line of JSON
    ("s2 a frozen wheel file changed", 2, lambda d, b: touch_part(d, "third"), 0.0),
    ("s3 gold", 3, lambda d, b: None, kept(REF_REMADE)),
    ("s3 do nothing", 3, lambda d, b: nothing(d), 0.0),
    ("s3 stage-2 movement handed back unchanged", 3, use_stage(2), 0.0),        # change request not met: hard requirement
    ("s3 tooth counts edited on paper only", 3, paper_edit, 0.0),
    ("s3 every part file regenerated", 3, lambda d, b: touch_all(d), kept(None)),
    ("s3 a kept fixed part regenerated", 3, lambda d, b: touch_part(d, "dial"), kept(REF_REMADE + ("dial",))),
    ("s3 a kept mobile renamed", 3, lambda d, b: edit(d, rename_mobile("fourth", "fourth_b")), kept(REF_REMADE + ("fourth",))),
    ("s3 old third wheel kept as a fixed ornament", 3, old_wheel_as_fixed, 0.0),
    ("s3 day train left undriven", 3, lambda d, b: edit(d, drop_mesh("hour_wheel", "day_idler")), 0.0),   # day hand fails: change not met
    ("s4 gold", 4, lambda d, b: None, 1.0),
    ("s4 no assembly.json", 4, lambda d, b: os.remove(os.path.join(d, "assembly.json")), 0.0),
    ("s4 a part file changed", 4, lambda d, b: touch_part(d, "dial"), 0.0),
    ("s4 centre before third", 4, lambda d, b: edit(d, reorder("centre_36", "third_54"), "assembly.json"), parts_score(1)),
    ("s4 dial jumps into place in one step", 4, lambda d, b: edit(d, teleport, "assembly.json"), parts_score(1)),
    # the dial stands in place from the start. The reference's dial is a skeleton of bosses and bars, so of the
    # 13 parts ORDER puts in before it only those lying under a boss or bar are blocked: 11 of them, plus the
    # dial itself (measured on the reference, builder REF)
    ("s4 dial left out of the order", 4, lambda d, b: edit(d, lambda doc: doc["order"].remove("dial"), "assembly.json"),
     parts_score(12)),
    # In the reference the part picked is the cannon on the centre arbor. The hour wheel rests on it (held needs
    # the hour wheel's tube within 0.3 above the cannon; it is 0.2), so the cannon cannot rise 0.4 without
    # running into the hour wheel: the hard requirement "assembled" fails and the score is 0 (builder REF).
    ("s1 a wheel moved 0.4 up its arbor, off its shoulder", 1, move_part_up(0.4), 0.0),
    ("s1 two parts of one mobile overlap", 1, dup_mobile_part, 0.0),
    ("s4 a part put in after the part of its mobile that blocks it", 4, swap_within_mobile,
     lambda d, b: parts_score(1, len(W.load_movement(d).all_parts()))),     # all parts, the barrel included
    ("s1 seconds pinion with fat teeth (no backlash)", 1, fat_seconds_pinion, fails(1, "tolerant")),
    # the reference's bridge is a skeleton: it blocks the barrel, third, centre, fourth and seconds (measured)
    ("s4 bridge on before the wheels", 4, lambda d, b: edit(d, reorder("bridge", "barrel"), "assembly.json"), parts_score(5)),
]


# ---------------- exploits (HANDOFF_EXPLOITS.md), grader-exploits session ----------------
# Each was a submission that scored 1.0 before the rules that close it. Mesh-level cases (false tooth counts,
# the drive test, mutual holding) are in tests/test_exploit_rules.py.
def x_islands(d, base):
    """Every plate cut down to discs of radius 2 round the arbors it carries: fourteen floating fixed parts."""
    import cadquery as cq
    from geometry import watch_gears_cad as GC
    doc = _doc_of(d)
    axes = [(0.0, 0.0)] + [tuple(mo["axis"]) for mo in doc["mobiles"].values()]
    fixed = []
    for name in doc["fixed"]:
        shape = cq.importers.importStep(part_file(d, name)).val()
        os.remove(part_file(d, name))
        if name == "barrel_cock":
            shape = shape.intersect(cq.Solid.makeBox(4, 4, 2.4, cq.Vector(-2, -2, 0.5))).clean()   # its post goes too
        k = 0
        for x, y in axes:
            piece = shape.intersect(cq.Solid.makeCylinder(2.0, 40, cq.Vector(x, y, -20))).clean()
            for sol in piece.Solids():
                if sol.Volume() > 0.05:
                    n = "%s_%d" % (name, k)
                    k += 1
                    GC.export(os.path.join(d, "parts", n + ".step"), sol)
                    fixed.append(n)
    doc["fixed"] = fixed
    json.dump(doc, open(os.path.join(d, "movement.json"), "w"), indent=1)


def x_cock_without_post(d, base):
    """The barrel cock as it was before the frame rule: it holds the barrel but touches no other fixed part."""
    from geometry import watch_gears_cad as GC
    GC.export(part_file(d, "barrel_cock"), GC.cut(GC.cyl(0, 0, 1.15, 2.45, 1.6), GC.cyl(0, 0, 1.0, 1.7, 0.6)))


def x_dummy_ring(d, base):
    """An extra mobile nothing drives: a ring loose round the barrel cock's post."""
    from geometry import watch_gears_cad as GC
    GC.export(os.path.join(d, "parts", "dummy_ring.step"), GC.tube(0, 0, 3.4, 3.6, 1.0, 0.65))
    edit(d, lambda doc: doc["mobiles"].update(dummy={"axis": [0.0, 0.0], "parts": ["dummy_ring"]}))


def x_wheel_as_minute_hand(d, base):
    """The minute hand part deleted; hands.minute names the centre wheel, which sits under the dial."""
    def fn(doc):
        doc["mobiles"]["centre"]["parts"].remove("minute_hand")
        doc["hands"]["minute"]["part"] = "centre"
    edit(d, fn)
    os.remove(part_file(d, "minute_hand"))


ANCHORS += [
    ("x s1 plates cut into islands round the arbors", 1, x_islands, 0.0),                 # Assembled: one frame
    ("x s1 barrel cock touching no other fixed part", 1, x_cock_without_post, 0.0),        # Assembled: one frame
    ("x s1 an undriven ring on the barrel cock's post", 1, x_dummy_ring, fails(1, "train", "held")),
    ("x s1 the centre wheel declared as the minute hand", 1, x_wheel_as_minute_hand, fails(1, "hands")),
    ("x s3 five more received wheels remade", 3, lambda d, b: [touch_part(d, n) for n in ("fourth", "seconds", "minute_wheel", "hour_wheel", "day_idler")],
     kept(REF_REMADE + ("fourth", "seconds", "minute_wheel", "hour_wheel", "day_idler"))),
]


def run_one(args):
    i, base = args
    name, stage, change, want = ANCHORS[i]
    d = tempfile.mkdtemp()
    shutil.rmtree(d)
    shutil.copytree(os.path.join(base, "stage%d" % stage), d)
    if callable(want):                  # an expected value that depends on the reference (e.g. its part count)
        want = want(d, base)
    change(d, base)
    r = grade(d, stage, os.path.join(base, "stage%d" % (stage - 1)) if stage > 1 else None)
    failed = [k for dd in (r["gates"], r["checks"]) for k, v in dd.items() if not v]
    ok = abs(r["reward"] - want) < 1e-6
    shutil.rmtree(d, ignore_errors=True)
    extra = "  kept %s" % r["details"]["kept"].get("share") if stage == 3 and "kept" in r["details"] else ""
    return ok, "%-4s %-46s S=%.4f expected %.4f  failed: %s%s" % ("ok" if ok else "OFF", name, r["reward"], want, ",".join(failed[:8]) or "-", extra)


def main():
    TIMEOUT_S = 1500        # per anchor; each anchor runs in a fresh interpreter (no threads inherited through fork)
    import subprocess
    from concurrent.futures import ThreadPoolExecutor
    args = sys.argv[1:]
    opt = lambda k: args[args.index(k) + 1] if k in args and args.index(k) + 1 < len(args) else None
    only, base = opt("--only"), opt("--base")
    timeout = float(opt("--timeout") or TIMEOUT_S)
    if opt("--one") is not None:        # child: one anchor, its output line, exit 1 when it is off
        ok, line = run_one((int(opt("--one")), base))
        print(line, flush=True)
        return 0 if ok else 1
    pos = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] not in ("--only", "--base", "--timeout"))]
    workers = int(pos[0]) if pos else 3
    pick = list(range(len(ANCHORS)))
    if only:
        want = [w.strip() for w in only.split(",") if w.strip()]
        names = [a[0] for a in ANCHORS]
        pick = [i for i, n in enumerate(names) if any(w == n for w in want) or
                any(w in n and w not in names for w in want)]
        if not pick:
            raise SystemExit("no anchor matches %r" % only)
    if base is None:
        base = tempfile.mkdtemp()
        ref.main(base)
    base = os.path.abspath(base)

    def one(i):
        name = ANCHORS[i][0]
        try:
            r = subprocess.run([sys.executable, os.path.abspath(__file__), "--one", str(i), "--base", base],
                               stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "%-4s %-46s timed out after %g s" % ("OFF", name, timeout)
        lines = [l for l in r.stdout.splitlines() if l.startswith(("ok ", "OFF "))]
        if lines:
            return r.returncode == 0 and lines[-1].startswith("ok "), lines[-1]
        err = (r.stderr.strip().splitlines() or ["no output"])[-1]
        return False, "%-4s %-46s crashed (exit %d): %s" % ("OFF", name, r.returncode, err)
    bad = 0
    with ThreadPoolExecutor(workers) as pool:
        for ok, line in pool.map(one, pick):
            bad += not ok
            print(line, flush=True)
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())
