"""Anchors for the one-job watch grader (tests/grade_watch.py without --stage).
    python3 tests/test_anchors_job.py WORKERS [--job /abs/REF_JOB] [--only NAME[,NAME...]] [--timeout S]
Run from the repository root (any directory works; paths are taken from this file).
Each anchor is a delivery folder built from the reference job folder (solution/reference_watch.py --job) by one
small change, then graded as the verifier grades it: `python3 -I grade_watch.py DELIVERY --reward R --details D`
from tests/. The expected reward is derived below from the rule (environment/public/job/PROMPT.md, Acceptance
test, and the weights of SESSION.md Decisions 2026-11-14 15:44 (B)) and asserted to 1e-4, together with each
part's score s and the names of the gates and checks that fail (from the details file).
--job reuses a reference job folder; without it one is built into a temporary folder (about 60 s).
--only runs the anchors whose name contains one of the given texts (an exact name match wins).
--timeout is per anchor (build plus grading), default 4000 s.
Every anchor runs in fresh interpreters: one that builds its folder (`--build INDEX --job REF --out DIR`,
may load CadQuery), then the grader. This process loads neither CadQuery nor manifold, and starts the children
from a thread pool of WORKERS threads. Prints one `ok` / `OFF` line per anchor, then a table; exits 1 if any is off.

Reward rule. Parts and weights: P1 going train and hands 0.25, P2 24-hour hand 0.10, P3 6-hour variant 0.15,
P4 assembly 0.25 (sum 0.75). reward = 1/2 x sum(w_p s_p) / 0.75 + 1/2 x [every gate and check passes].
When not everything passes this is   reward = 1/2 - (2/3) x sum(w_p x (1 - s_p))   (the "deficit form").
Check weights: P1 spin 1, held 2, train 3, clear 1, hour 2, minute 2, seconds 2, coaxial 1, hands 1, size 1,
printable 1, tolerant 2, seated 2 (sum 21); P2 day_hand 3, day_place 1 (sum 4); P3 every P1 and P2 check
(sum 25); P4 one per part of movement.json, the barrel included: 17 part files + barrel = 18 in the reference.
A part whose gates fail scores 0.

The reference job folder: movement.json (8 h) has fixed main_plate, bridge, dial, barrel_cock and mobiles third
[third], centre [centre, cannon, minute_hand], fourth [fourth], seconds [seconds, seconds_hand], minute_wheel,
hour_wheel [hour_wheel, hour_hand], day_idler, day [day, day_hand]. variant_6h.json is the same with third_54
and centre_36 in place of third and centre (third/centre 54/36 instead of 60/30). So a change to `third` or
`centre` touches P1 (and P4) only; a change to any other part touches P1 and P3 alike.
assembly.json drops every part straight down from above, in the order main_plate, barrel, barrel_cock, third,
centre, fourth, seconds, bridge, cannon, minute_wheel, hour_wheel, day, day_idler, dial, hour_hand, seconds_hand,
day_hand, minute_hand."""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import time
from fractions import Fraction as F

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TESTS = os.path.join(ROOT, "tests")
HERE = os.path.abspath(__file__)

# ---------------- the rule, as stated (not read from the grader; checked against it at start) ----------------
PART_W = {"P1": F(25, 100), "P2": F(10, 100), "P3": F(15, 100), "P4": F(25, 100)}
CW1 = {"spin": 1, "held": 2, "train": 3, "clear": 1, "hour": 2, "minute": 2, "seconds": 2, "coaxial": 1,
       "hands": 1, "size": 1, "printable": 1, "tolerant": 2, "seated": 2}
CW2 = {"day_hand": 3, "day_place": 1}
CW = {"P1": CW1, "P2": CW2, "P3": dict(CW1, **CW2)}
GATES = {"P1": ("files", "assembled"), "P2": ("files", "assembled", "day_declared"),
         "P3": ("files", "assembled", "day_declared", "same_frame"), "P4": ("files", "plan")}
REF_P4_PARTS = 18          # 17 part files of the reference movement.json and the barrel
ORDER_8H = ["main_plate", "barrel", "barrel_cock", "third", "centre", "fourth", "seconds", "bridge", "cannon",
            "minute_wheel", "hour_wheel", "day", "day_idler", "dial", "hour_hand", "seconds_hand", "day_hand",
            "minute_hand"]


class X:
    """What an anchor should score. For P1 to P3: the gates and the checks expected to fail (checks=None:
    not asserted, used when a gate fails and the checks do not matter). For P4: the gates expected to fail and
    the parts expected NOT to be installed (a set of names; or an int n = number not installed)."""

    def __init__(self, **parts):
        self.parts = {}
        for pid in PART_W:
            spec = parts.get(pid, {})
            self.parts[pid] = {"gates": set(spec.get("gates", ())),
                               "checks": None if spec.get("checks", ()) is None else set(spec.get("checks", ())),
                               "not_installed": spec.get("not_installed", set())}

    def s(self, pid):
        p = self.parts[pid]
        if p["gates"]:
            return F(0)
        if pid == "P4":
            n = p["not_installed"] if isinstance(p["not_installed"], int) else len(p["not_installed"])
            return F(REF_P4_PARTS - n, REF_P4_PARTS)
        w = CW[pid]
        return F(sum(w.values()) - sum(w[k] for k in p["checks"]), sum(w.values()))

    def all_pass(self):
        return all(self.s(pid) == 1 and not self.parts[pid]["gates"] for pid in PART_W)

    def reward(self):
        num = sum(PART_W[p] * self.s(p) for p in PART_W)
        return F(1, 2) * num / sum(PART_W.values()) + (F(1, 2) if self.all_pass() else F(0))


ALL_FAIL = None     # checks not asserted


# ---------------- helpers used by the builders (run in the --build child) ----------------
def _edit(d, name, fn):
    p = os.path.join(d, name)
    with open(p) as f:
        doc = json.load(f)
    fn(doc)
    with open(p, "w") as f:
        json.dump(doc, f, indent=1)


def _both(d, fn):
    """The same edit to movement.json and variant_6h.json (a shared part changed in both declarations)."""
    _edit(d, "movement.json", fn)
    _edit(d, "variant_6h.json", fn)


def _set_teeth(a, b, ta, tb):
    def fn(doc):
        for e in doc["meshes"]:
            if (e["driver"], e["driven"]) == (a, b):
                e["driver_teeth"], e["driven_teeth"] = ta, tb
    return fn


_REF = {}


def _ref():
    """The reference script as a module and its layout: (ref, P, lo, hi). P is the reference's own placement
    (place() with its default seed), so a part rebuilt here sits exactly where the reference put it."""
    if not _REF:
        sys.path.insert(0, ROOT)
        sys.path.insert(0, os.path.join(ROOT, "solution"))
        import reference_watch as ref
        P = ref.place()
        _REF.update(ref=ref, P=P, lo=ref.PLATE[1] + 0.1, hi=ref.BRIDGE[0] - 0.1)
    return _REF["ref"], _REF["P"], _REF["lo"], _REF["hi"]


def _write(d, name, solid):
    from geometry import watch_gears_cad as GC
    GC.export(os.path.join(d, "parts", name + ".step"), solid)


def _third(wheel_z=None, top_shoulder=True):
    """The 8-hour third mobile as the reference draws it (arbor, 24-pinion driven by the barrel, 60-wheel driving
    the centre pinion), with the wheel's z range or the arbor's top shoulder changed."""
    ref, P, lo, hi = _ref()
    B, I, C = P["barrel"], P["third"], P["centre"]
    p1, _ = ref.gear_at(I, 24, ref.M_A, ref.Z["A"], ref.ang(I, B), (96, 0.0))
    w1, _ = ref.wheel_at(I, 60, ref.M_B, wheel_z or ref.Z["B"], ref.ang(I, C))
    if top_shoulder:
        arb = ref.arbor(I, lo, hi)
    else:
        # the shaft is 0.5 only up to the wheel; above it, the arbor is the 0.3 pivot all the way through the bridge
        x, y = I
        zt = ref.Z["B"][1]
        arb = ref.union([ref.cyl(x, y, lo, zt, 0.5), ref.cyl(x, y, lo - 0.7, lo + 0.01, 0.3), ref.cyl(x, y, zt - 0.01, hi + 0.7, 0.3)])
    return ref.union([arb, p1, w1])


def _centre(neck=False, tip_top=11.4):
    """The 8-hour centre arbor (pinion 30 driven by the third wheel, wheel 90 driving the fourth), with the shaft
    under the cannon turned down to 0.2 (neck) or the top tip ending at tip_top."""
    ref, P, lo, hi = _ref()
    I, C, T = P["third"], P["centre"], P["fourth"]
    _, ph_w1 = ref.wheel_at(I, 60, ref.M_B, ref.Z["B"], ref.ang(I, C))
    p2, _ = ref.wheel_at(C, 30, ref.M_B, ref.Z["B"], ref.ang(C, I), (60, ph_w1), hub_r=1.2)
    w2, _ = ref.wheel_at(C, 90, ref.M_C, ref.Z["C"], ref.ang(C, T), hub_r=1.2)
    cx, cy = C
    cyl = ref.cyl
    shaft = [cyl(cx, cy, 6.39, 10.7, 0.5)] if not neck else \
        [cyl(cx, cy, 6.39, 6.41, 0.5), cyl(cx, cy, 6.4, 7.3, 0.2), cyl(cx, cy, 7.29, 10.7, 0.5)]
    return ref.union([cyl(cx, cy, lo, 6.4, 0.6), cyl(cx, cy, lo - 0.7, lo + 0.01, 0.3)] + shaft +
                     [cyl(cx, cy, 10.69, tip_top, 0.35), p2, w2])


def _seconds(pinion=None, lug=None, burr=False):
    """The seconds arbor as the reference draws it (hand_arbor with the 12-pinion driven by the fourth wheel).
    pinion: (teeth, z range, backlash) to cut a different pinion; lug: (z0, z1, reach, width) adds a radial arm
    pointing straight away from the nearest pillar; burr: a lump (radius 0.15, centred 0.05 outside the tip
    circle, so it stands 0.2 proud of the tip) on the tooth that points furthest from the fourth wheel."""
    ref, P, lo, hi = _ref()
    from geometry import watch_gears_cad as GC
    T, S = P["fourth"], P["seconds"]
    teeth, z, backlash = pinion or (12, ref.Z["D"], 0.03)
    wt = 96 if teeth == 12 else 108 - teeth                 # the fourth wheel it meshes with (same centre distance)
    _, ph_w3 = ref.wheel_at(T, wt, ref.M_D, ref.Z["D"], ref.ang(T, S))
    _, ph = ref.gear_at(S, teeth, ref.M_D, z, ref.ang(S, T), (wt, ph_w3))
    p4 = GC.gear(teeth, ref.M_D, z[0], z[1], phase_deg=ph, x=S[0], y=S[1], backlash=backlash)
    if burr:
        away = math.degrees(ref.ang(S, T)) + 180.0
        k = min(range(teeth), key=lambda k: abs((ph + 360.0 * k / teeth - away + 180.0) % 360.0 - 180.0))
        a = math.radians(ph + 360.0 * k / teeth)            # tooth k is centred here (tooth 0 on +x before phase)
        r = ref.M_D * teeth / 2.0 + ref.M_D + 0.05
        p4 = ref.union([p4, GC.cyl(S[0] + r * math.cos(a), S[1] + r * math.sin(a), z[0], z[1], 0.15)])
    solid = ref.hand_arbor(S, lo, hi, p4)
    if lug:
        z0, z1, reach, width = lug
        P["case"] = P.get("case") or ref.case_geometry(P)
        spots = P["case"][2]
        q = min(spots, key=lambda s: ref.dist(s, S))
        a = math.degrees(ref.ang(S, q)) + 180.0            # away from the nearest pillar
        arm = GC.box((S[0], S[1] - width / 2, z0), (S[0] + reach, S[1] + width / 2, z1))
        import cadquery as cq
        arm = arm.rotate(cq.Vector(S[0], S[1], 0), cq.Vector(S[0], S[1], 1), a)
        solid = ref.union([solid, arm])
    return solid


# ---------------- builders: change(d) edits the copied reference job folder d ----------------
def b_nothing(d):
    for n in os.listdir(d):
        p = os.path.join(d, n)
        shutil.rmtree(p) if os.path.isdir(p) and not os.path.islink(p) else os.remove(p)


def b_plan_without_paths(d):
    _edit(d, "assembly.json", lambda a: a.update(paths={}))


def b_variant_without_day(d):
    _edit(d, "variant_6h.json", lambda doc: doc["hands"].pop("day"))


def b_no_day_train(d):
    def fn(doc):
        for k in ("day", "day_idler"):
            doc["mobiles"].pop(k)
        doc["meshes"] = [e for e in doc["meshes"] if not {e["driver"], e["driven"]} & {"day", "day_idler"}]
        doc["hands"].pop("day")
    _edit(d, "movement.json", fn)      # assembly.json still names day, day_idler, day_hand: ignored (rule)


def b_jam(d):
    _write(d, "seconds", _seconds(burr=True))


def b_no_engage(d):
    _write(d, "seconds", _seconds(pinion=(12, (4.6, 4.9), 0.03)))


def b_wrong_speed(d):
    ref, P, lo, hi = _ref()
    C, T, S = P["centre"], P["fourth"], P["seconds"]
    _, ph_w2 = ref.wheel_at(C, 90, ref.M_C, ref.Z["C"], ref.ang(C, T), hub_r=1.2)
    p3, _ = ref.gear_at(T, 12, ref.M_C, ref.Z["C"], ref.ang(T, C), (90, ph_w2))
    w3, _ = ref.wheel_at(T, 95, ref.M_D, ref.Z["D"], ref.ang(T, S))
    _write(d, "fourth", ref.union([ref.arbor(T, lo, hi), p3, w3]))
    _write(d, "seconds", _seconds(pinion=(13, ref.Z["D"], 0.03)))
    _both(d, _set_teeth("fourth", "seconds", 95, 13))


def b_not_held(d):
    _write(d, "third", _third(top_shoulder=False))


def b_not_seated(d):
    _write(d, "centre", _centre(neck=True))


def b_too_thin(d):
    _write(d, "third", _third(wheel_z=(1.4, 1.5)))


def b_too_tall(d):
    _write(d, "centre", _centre(tip_top=11.8))


def b_hands_collide(d):
    ref, P, lo, hi = _ref()
    _write(d, "hour_hand", ref.hand(P["centre"], 9.9, 10.2, 9.0, 1.3, 0.9 + ref.FIT))


def b_rubs_frame(d):
    _write(d, "seconds", _seconds(lug=(1.05, 1.35, 5.2, 0.6)))


def b_day_on_hour_part(d):
    _edit(d, "movement.json", lambda doc: doc["hands"].update(day=dict(doc["hands"]["hour"])))


def b_day_wrong_rate(d):
    ref, P, lo, hi = _ref()
    C, Mw, Id, D = P["centre"], P["minute_wheel"], P["day_idler"], P["day"]
    _, ph_p5 = ref.gear_at(Mw, 12, ref.M_F, ref.Z["F"], ref.ang(Mw, C))
    _, ph_hour = ref.wheel_at(C, 48, ref.M_F, ref.Z["F"], ref.ang(C, Mw), (12, ph_p5), hub_r=1.6)
    ga, _ = ref.gear_at(Id, 24, ref.M_F, ref.Z["F"], ref.ang(Id, C), (48, ph_hour))
    gb, ph_gb = ref.gear_at(Id, 15, ref.M_DAY, ref.Z_DAY, ref.ang(Id, D))
    _write(d, "day_idler", ref.union([ref.arbor(Id, ref.BRIDGE[1] + 0.1, ref.DIAL[0] - 0.1, top=0.4), ga, gb]))
    dw, _ = ref.wheel_at(D, 35, ref.M_DAY, ref.Z_DAY, ref.ang(D, Id), (15, ph_gb), hub_r=1.2)
    _write(d, "day", ref.hand_arbor(D, ref.BRIDGE[1] + 0.1, ref.DIAL[0] - 0.1, dw))
    _both(d, _set_teeth("day_idler", "day", 15, 35))


DAY_CLOSE_ANGLE = 91.0      # degrees round the day idler: the day axis 5.961 from the hour axis


def b_day_too_close(d):
    """The reference rebuilt with the 24-hour wheel on the day-idler circle at 91 degrees, 5.961 mm from the hour
    hand's axis (the reference puts it 9.62 away). To keep everything else working, as a designer would: the
    hour hand is 5.0 long (reach 5.009, was 6.0) so it passes the day arbor, and the day hand sits at z 10.3-10.6
    on a longer day arbor tip, above the hour hand (9.9-10.2) and below the minute hand (10.7)."""
    ref, P, lo, hi = _ref()
    Id = P["day_idler"]
    Dn = ref.on(Id, ref.DAY_CD, math.radians(DAY_CLOSE_ANGLE))
    Dn = (round(Dn[0], 4), round(Dn[1], 4))
    hand0, arbor0 = ref.hand, ref.hand_arbor

    def hand(axis, z0, z1, length, hub_r, bore_r):
        if length == 6.0:                    # the hour hand
            length = 5.0
        if length == 3.2:                    # the 24-hour hand
            z0, z1 = 10.3, 10.6
        return hand0(axis, z0, z1, length, hub_r, bore_r)

    def hand_arbor(A, z0, z1, gear_solid):
        if tuple(A) != Dn:
            return arbor0(A, z0, z1, gear_solid)
        x, y = A
        c = ref.cyl
        return ref.union([c(x, y, z0, z1, 0.6), c(x, y, z1 - 0.4, z1, 0.8), c(x, y, z0 - 0.7, z0 + 0.01, 0.3),
                          c(x, y, z1 - 0.01, 10.3, 0.5), c(x, y, 10.29, 10.7, 0.3), gear_solid])
    ref.place_day, ref.hand, ref.hand_arbor = (lambda P: Dn), hand, hand_arbor
    ref.main_job(d)


def b_variant_is_movement(d):
    shutil.copyfile(os.path.join(d, "movement.json"), os.path.join(d, "variant_6h.json"))


def b_variant_paper_counts(d):
    def fn(doc):
        doc["mobiles"]["third"]["parts"] = ["third"]
        doc["mobiles"]["centre"]["parts"] = ["centre" if n == "centre_36" else n for n in doc["mobiles"]["centre"]["parts"]]
    _edit(d, "variant_6h.json", fn)        # meshes still declare third/centre 54/36


def b_variant_plate_renamed(d):
    shutil.copyfile(os.path.join(d, "parts", "main_plate.step"), os.path.join(d, "parts", "plate_6h.step"))
    _edit(d, "variant_6h.json", lambda doc: doc.update(fixed=["plate_6h" if n == "main_plate" else n for n in doc["fixed"]]))


def b_order_reversed(d):
    _edit(d, "assembly.json", lambda a: a.update(order=list(reversed(a["order"]))))


def b_coarse_path(d):
    def fn(a):
        p = a["paths"]["dial"]
        a["paths"]["dial"] = p[::2] + ([p[-1]] if (len(p) - 1) % 2 else [])
    _edit(d, "assembly.json", fn)


def b_minute_hand_left_out(d):
    _edit(d, "assembly.json", lambda a: a["order"].remove("minute_hand"))


def _disc_hand(d, off):
    ref, P, lo, hi = _ref()
    from geometry import watch_gears_cad as GC
    cx, cy = P["centre"]
    disc = GC.cut(GC.cyl(cx + off, cy, 10.7, 11.0, 18.0), GC.cyl(cx, cy, 10.0, 11.5, 0.35 + ref.FIT))
    _write(d, "minute_hand", disc)


def b_disc_centred(d):
    _disc_hand(d, 0.0)


def b_disc_off_centre(d):
    _disc_hand(d, 0.6)


def b_barrel_as_part(d):
    _edit(d, "movement.json", lambda doc: doc["mobiles"]["third"]["parts"].append("barrel"))


def b_symlinked_part(d):
    os.makedirs(os.path.join(d, "scripts"), exist_ok=True)
    real = os.path.join(d, "scripts", "third.step")
    shutil.move(os.path.join(d, "parts", "third.step"), real)
    os.symlink(os.path.join("..", "scripts", "third.step"), os.path.join(d, "parts", "third.step"))


# ---------------- extra assertions on the details file ----------------
def _mesh(d, pid, pair, key):
    for x in d["parts"][pid]["details"]["train"]["meshes"]:
        if x["pair"] == pair:
            return x[key]
    return None


def mesh_fact(pid, pair, key, test, text):
    def fn(d):
        v = _mesh(d, pid, pair, key)
        return None if v is not None and test(v) else "%s train %s %s = %r, expected %s" % (pid, pair, key, v, text)
    return fn


def detail(path, test, text):
    """path: keys into the details file from d['parts']."""
    def fn(d):
        v = d["parts"]
        try:
            for k in path:
                v = v[k]
        except (KeyError, TypeError, IndexError):
            return "details %s missing" % "/".join(map(str, path))
        return None if test(v) else "details %s = %r, expected %s" % ("/".join(map(str, path)), v, text)
    return fn


# ---------------- the anchors ----------------
# (name, builder, expected X, [extra assertions]). The reward of each is X(...).reward(); the arithmetic in the
# comments uses the deficit form reward = 1/2 - (2/3) sum w_p (1 - s_p).
ANCHORS = [
    # 1 = 1/2 x 0.75/0.75 + 1/2
    ("job gold", None, X(), []),
    # nothing loads: every part's files gate fails, 1/2 - (2/3)(0.75) = 0
    ("job do nothing", b_nothing,
     X(P1={"gates": GATES["P1"], "checks": ALL_FAIL}, P2={"gates": GATES["P2"], "checks": ALL_FAIL},
       P3={"gates": GATES["P3"], "checks": ALL_FAIL}, P4={"gates": GATES["P4"]}), []),

    # ---- 3. everything except one part ----
    # The hardest part is P4, the assembly: it is the only part whose result depends on every other design
    # choice at once (each part's shape must leave a path past every part placed before it, parts of its own
    # mobile included, and a part left out still blocks those after it), the delivery's tools do not run it,
    # and on the staged task it is where frontier runs fell short (SESSION.md: GPT chain B 0.42 at stage 4,
    # Sonnet's trapped day_cock). The 6-hour variant is smaller once the frame is planned for it: the reference
    # swaps two parts at the same centre distance (60/30 -> 54/36).
    # An assembly.json with the order but no paths: the plan is valid JSON (gate passes), no part has a path, so
    # none is installed: s4 = 0/18. 1/2 - (2/3)(0.25) = 1/3
    ("job everything except the hardest part (assembly: order, no paths)", b_plan_without_paths,
     X(P4={"not_installed": REF_P4_PARTS}), []),
    # The variant handed in without its 24-hour hand: C3 fails, s3 = 0. 1/2 - (2/3)(0.15) = 0.4
    ("job everything except the variant (no day hand in variant_6h.json)", b_variant_without_day,
     X(P3={"gates": ["day_declared"]}), [detail(["P3", "checks"], lambda c: all(c.values()), "every P3 check to pass")]),
    # The 8-hour build without the 24-hour train (mobiles day and day_idler, their meshes and the day hand gone;
    # their part files stay for the variant; assembly.json still names them, which the rule ignores): C3 fails,
    # s2 = 0; P1 loses nothing; P4 has 15 parts and installs all. 1/2 - (2/3)(0.10) = 13/30 = 0.43333
    # (P1 cannot be left out alone: P2's gates contain P1's (C1, C2) and P4 needs C1, so a delivery without a
    # working P1 also loses P2, and P4 if movement.json does not load.)
    ("job everything except the 24-hour hand (no day train in movement.json)", b_no_day_train,
     X(P2={"gates": ["day_declared"]}), [detail(["P4", "checks"], lambda c: len(c) == 15 and all(c.values()), "15 parts, all installed")]),

    # ---- 4. Part 1 checks a real design can fail ----
    # One tooth of the seconds pinion left with a lump 0.2 proud of its tip (radius 0.15): drawn, that tooth
    # points away from the fourth wheel (C2 holds); each time it comes into mesh it runs into the wheel's root
    # (tip-to-root clearance 0.25 x 0.2 = 0.05), a jam. (Uniformly fat teeth do not make this anchor: measured
    # with backlash -0.12 the drawn overlap is already 0.015, a C2 failure.) A failing mesh drives nothing, so
    # the seconds hand stands; the shifted runs jam too. fourth and seconds are in both movements: P1 and P3
    # fail train 3, tolerant 2, seconds 2 = 7. Deficit 0.25 x 7/21 + 0.15 x 7/25 = 1/12 + 0.042; reward
    # 1/2 - (2/3)(0.125333) = 937/2250 = 0.416444
    ("job a mesh that jams (a lump on one seconds-pinion tooth)", b_jam,
     X(P1={"checks": ["train", "tolerant", "seconds"]}, P3={"checks": ["train", "tolerant", "seconds"]}),
     [mesh_fact("P1", "fourth/seconds", "worst_volume", lambda v: v > 0.01, "> 0.01 (a jam)")]),
    # The seconds pinion cut 0.8 too high on its arbor (z 4.6-4.9; the fourth wheel is at 3.8-4.4): the teeth
    # miss each other, smallest distance 0.2 > 0.1 (not engaged) and the drive test finds nothing. No jam. Same
    # failing checks as above: 937/2250 = 0.416444
    ("job a mesh whose teeth do not engage (seconds pinion 0.8 too high)", b_no_engage,
     X(P1={"checks": ["train", "tolerant", "seconds"]}, P3={"checks": ["train", "tolerant", "seconds"]}),
     [mesh_fact("P1", "fourth/seconds", "largest_gap", lambda v: v > 0.1, "> 0.1 (not engaged)"),
      mesh_fact("P1", "fourth/seconds", "worst_volume", lambda v: v <= 0.01, "<= 0.01 (no jam)")]),
    # The fourth wheel and seconds pinion cut and declared 95/13 instead of 96/12 (same centre distance, module
    # 0.2, sum 108): the train runs, the seconds hand turns 7.5 x 95/13 = 54.8 per hour, not 60. Both movements:
    # P1 and P3 fail seconds (2). Deficit 0.25 x 2/21 + 0.15 x 2/25 = 1/42 + 3/250 = 94/2625; reward
    # 1/2 - (2/3)(94/2625) = 7499/15750 = 0.476127
    ("job a hand at the wrong speed (seconds pair 95/13)", b_wrong_speed,
     X(P1={"checks": ["seconds"]}, P3={"checks": ["seconds"]}),
     [detail(["P1", "details", "seconds", "clockwise_turns_per_hour_through_working_meshes"], lambda v: v == "1425/26", "1425/26 (7.5 x 95/13)")]),
    # The 8-hour third arbor without its top shoulder (0.3 pivot from the wheel up through the bridge, which has a
    # 0.4 hole): moved +z it touches nothing. third is in movement.json only: P1 fails held (2). Deficit
    # 0.25 x 2/21 = 1/42; reward 1/2 - 1/63 = 61/126 = 0.484127
    ("job a mobile not held (third arbor without its top shoulder)", b_not_held,
     X(P1={"checks": ["held"]}),
     [detail(["P1", "details", "held", "not_held"], lambda v: v == ["third +z"], "['third +z']")]),
    # The 8-hour centre arbor turned down to 0.2 under the cannon (z 6.4-7.3; the cannon's bore is 0.505): the
    # cannon still rests on the 0.6 shoulder (one piece, -z seated) but moved 0.3 sideways it touches nothing.
    # P1 fails seated (2): 61/126 = 0.484127
    ("job a part not seated (cannon loose on a turned-down arbor)", b_not_seated,
     X(P1={"checks": ["seated"]}),
     [detail(["P1", "details", "seated", "not_seated"], lambda v: v == ["cannon"], "['cannon']")]),
    # The 8-hour third wheel cut 0.1 thick (z 1.4-1.5): at most two voxel centres across it, none survives, so
    # the wheel is not in the printable body (deviation far over 0.2). P1 fails printable (1). Deficit
    # 0.25 x 1/21 = 1/84; reward 1/2 - 1/126 = 31/63 = 0.492063
    ("job a part too thin to print (third wheel 0.1 thick)", b_too_thin,
     X(P1={"checks": ["printable"]}),
     [detail(["P1", "details", "printable", "third", "max_deviation"], lambda v: v > 0.2, "> 0.2")]),
    # The 8-hour centre arbor's top tip 0.4 longer (to 11.8): the movement is 11.8 - (-1.7) = 13.5 tall > 13.4.
    # The assembly paths start 0.5 above the old box top + 5, so still 0.1 above the new one. P1 fails size (1):
    # 31/63 = 0.492063
    ("job the movement taller than the case (centre tip +0.4)", b_too_tall,
     X(P1={"checks": ["size"]}),
     [detail(["P1", "details", "size"], lambda e: abs(e["z_max"] - e["z_min"] - 13.5) < 1e-3, "13.5 tall")]),
    # The hour hand 9.0 long (was 6.0): the 24-hour hand's hub (r 0.9, same z 9.9-10.2) is 9.62 from the hour
    # axis, so in each turn the hour hand runs into it; drawn, both hands point +x and do not touch. hour_hand is
    # in both movements: P1 and P3 fail clear (1). Deficit 0.25/21 + 0.15/25 = 47/2625; reward
    # 1/2 - (2/3)(47/2625) = 7687/15750 = 0.488063
    ("job two non-meshing mobiles collide (hour hand into the 24-hour hub)", b_hands_collide,
     X(P1={"checks": ["clear"]}, P3={"checks": ["clear"]}),
     [detail(["P1", "details", "clear", "pair"], lambda v: v in ("hour_wheel/day", "day/hour_wheel"), "hour_wheel/day")]),
    # A counterweight arm on the seconds arbor (z 1.05-1.35, reach 5.2, 0.6 wide) drawn pointing away from the
    # nearest pillar (5.556 from the seconds axis, radius 0.75): in its turn it sweeps through that pillar.
    # Nothing else is at that height within reach. Both movements: P1 and P3 fail spin (1): 7687/15750 = 0.488063
    ("job a mobile rubs the frame when turned (seconds arm into a pillar)", b_rubs_frame,
     X(P1={"checks": ["spin"]}, P3={"checks": ["spin"]}),
     [detail(["P1", "details", "spin", "seconds", "worst_volume"], lambda v: v > 0.01, "> 0.01")]),

    # ---- 5. Part 2 ----
    # hands.day names the hour hand's mobile and part: C3 fails, s2 = 0. 1/2 - (2/3)(0.10) = 13/30 = 0.433333
    ("job 24-hour hand on the hour hand's part", b_day_on_hour_part,
     X(P2={"gates": ["day_declared"]}), []),
    # The day pair cut and declared 15/35 instead of 10/40 (same module 0.16 and centre distance 4.0): the
    # 24-hour hand turns 1/12 x 48/24 x 15/35 = 1/14 per hour, not 1/24. Shared parts: P2 and P3 fail day_hand
    # (3). Deficit 0.10 x 3/4 + 0.15 x 3/25 = 0.075 + 0.018 = 0.093; reward 1/2 - 0.062 = 0.438
    ("job 24-hour hand at the wrong rate (day pair 15/35)", b_day_wrong_rate,
     X(P2={"checks": ["day_hand"]}, P3={"checks": ["day_hand"]}),
     [detail(["P2", "details", "day_hand", "clockwise_turns_per_hour_through_working_meshes"], lambda v: v == "1/14", "1/14")]),
    # The reference rebuilt with the day axis 5.961 from the hour axis (< 6.0), the hour hand shortened to 5.0
    # and the day hand lifted to clear it (see b_day_too_close). The frame changes for both movements alike:
    # P2 and P3 fail day_place (1). Deficit 0.10/4 + 0.15/25 = 0.031; reward 1/2 - 0.0206667 = 0.479333
    ("job 24-hour hand axis too close to the hour axis (5.96 mm)", b_day_too_close,
     X(P2={"checks": ["day_place"]}, P3={"checks": ["day_place"]}),
     [detail(["P2", "details", "day_place", "axis_distance"], lambda v: 5.9 < v < 6.0, "5.96")]),

    # ---- 6. Part 3 ----
    # movement.json copied as the variant: gates pass (same frame), the barrel at 1/6 turns every hand 4/3 too
    # fast: hour 2, minute 2, seconds 2, day_hand 3 = 9 of 25. Deficit 0.15 x 9/25 = 0.054; reward
    # 1/2 - 0.036 = 0.464
    ("job variant = the 8-hour movement unchanged", b_variant_is_movement,
     X(P3={"checks": ["hour", "minute", "seconds", "day_hand"]}),
     [detail(["P3", "details", "minute", "clockwise_turns_per_hour_through_working_meshes"], lambda v: v == "4/3", "4/3")]),
    # The variant declares third/centre 54/36 but names the 8-hour parts third and centre (cut 60/30): turned
    # at 54/36 the teeth jam, the mesh drives nothing, so every hand stands: train 3, tolerant 2, hour 2,
    # minute 2, seconds 2, day_hand 3 = 14 of 25. Deficit 0.15 x 14/25 = 0.084; reward 1/2 - 0.056 = 0.444
    ("job variant with 6-hour tooth counts on the 8-hour parts", b_variant_paper_counts,
     X(P3={"checks": ["train", "tolerant", "hour", "minute", "seconds", "day_hand"]}),
     [mesh_fact("P3", "third/centre", "passes", lambda v: v is False, "False")]),
    # The variant's main_plate renamed plate_6h (a byte copy): C4 fails, s3 = 0; every P3 check still passes.
    # 1/2 - (2/3)(0.15) = 0.4
    ("job variant with one fixed part renamed", b_variant_plate_renamed,
     X(P3={"gates": ["same_frame"]}),
     [detail(["P3", "checks"], lambda c: all(c.values()), "every P3 check to pass")]),

    # ---- 7. Part 4 ----
    # Order reversed, same straight-down paths. A part is installed when nothing placed before it lies in its
    # way down. Reversed, the top parts come first: minute_hand (nothing placed), day_hand and seconds_hand (not
    # under the minute hand) are installed; every other part has something already placed above it: hour_hand
    # under the minute hand's bar, dial under the seconds and day hand hubs, day_idler, day, hour_wheel and
    # minute_wheel under dial bosses, cannon under the hour wheel's tube, bridge under the minute wheel, seconds
    # under its hand's bore, fourth, centre, third and barrel_cock under bridge bosses, barrel under the barrel
    # cock, main_plate under everything. 3 of 18: deficit 0.25 x 15/18; reward 1/2 - (2/3)(0.208333) = 13/36
    ("job assembly order reversed", b_order_reversed,
     X(P4={"not_installed": set(ORDER_8H) - {"minute_hand", "day_hand", "seconds_hand"}}), []),
    # The dial's path with every other pose dropped: vertices move about 0.38 > 0.2 between poses, the dial is not
    # installed but stands in place; the parts after it (hands) are above it. 17 of 18: deficit 0.25/18;
    # reward 1/2 - 1/108 = 53/108 = 0.490741
    ("job one path teleports (dial path every other pose)", b_coarse_path,
     X(P4={"not_installed": {"dial"}}), []),
    # The minute hand left out of the order: it stands at z 10.7-11.0 from the start (hub r 1.0 bore 0.355 on the
    # centre axis, a 9.0 x 0.6 bar along +x). Blocked on the way down: centre (arbor 0.5 through the 0.355 bore),
    # cannon, hour_wheel, hour_hand (all under the hub or bar), minute_wheel (its rim 3.3-3.9 under the bar),
    # dial, bridge, main_plate (bosses round the centre axis under the hub). Clear: barrel (9.96 > 9.8 from the
    # hub), barrel_cock, third (9.04 from the bar > 7.75), fourth (hub 9.8 from its axis, its tips 9.8: no
    # volume), seconds, day, day_idler, seconds_hand, day_hand. minute_hand itself is not installed. 9 of 18:
    # deficit 0.125; reward 1/2 - 1/12 = 5/12 = 0.416667
    ("job one part left out of the order (minute hand)", b_minute_hand_left_out,
     X(P4={"not_installed": {"minute_hand", "centre", "cannon", "hour_wheel", "hour_hand", "minute_wheel",
                             "dial", "bridge", "main_plate"}}), []),

    # ---- 8. exploit-style ----
    # The minute hand replaced by a disc r 18 (0.3 thick) on the centre axis, over the whole dial: it reaches
    # and lies above the frame but its centre of volume is on the axis (< 0.5): Hands fails in P1 and P3 (1).
    # 7687/15750 = 0.488063
    ("x minute hand is a disc over the whole dial (centred)", b_disc_centred,
     X(P1={"checks": ["hands"]}, P3={"checks": ["hands"]}),
     [detail(["P1", "details", "hands", "minute", "centre_from_axis"], lambda v: v < 0.5, "< 0.5")]),
    # The same disc 0.6 off-centre: reach 18.6 (+1.72 to the case centre = 20.32 <= 20.7), above the frame,
    # centre of volume 0.6 from the axis: every stated rule holds, so the rule gives 1.0. FINDING if it scores
    # 1.0: a hand may be a disc that hides the seconds and 24-hour hands; no stated rule stops it.
    ("x minute hand is a disc over the whole dial, 0.6 off-centre (FINDING)", b_disc_off_centre, X(), []),
    # movement.json lists 'barrel' as a part of the third mobile: a format error (C1), so P1, P2 and P4 score 0;
    # the variant still passes (C4 reads movement.json's fixed list and case centre only).
    # 1/2 - (2/3)(0.6) = 0.1
    ("x movement.json names the barrel as a part", b_barrel_as_part,
     X(P1={"gates": GATES["P1"], "checks": ALL_FAIL}, P2={"gates": GATES["P2"], "checks": ALL_FAIL}, P4={"gates": GATES["P4"]}),
     [detail(["P1", "details", "files", "error"], lambda v: "reserved" in v, "the 'barrel' reserved-name error")]),
    # parts/third.step is a symbolic link to a real copy inside the delivery (scripts/third.step): refused (C1)
    # for movement.json; the variant does not use third. 0.1
    ("x symlinked part file", b_symlinked_part,
     X(P1={"gates": GATES["P1"], "checks": ALL_FAIL}, P2={"gates": GATES["P2"], "checks": ALL_FAIL}, P4={"gates": GATES["P4"]}),
     [detail(["P1", "details", "files", "error"], lambda v: "symbolic link" in v, "a symbolic-link error")]),
]


# ---------------- comparing a details file with the expectation ----------------
def compare(x, d, extra):
    """List of differences between the grader's details d and the expectation x."""
    out = []
    want = x.reward()
    if abs(d["reward"] - float(want)) > 1e-4:
        out.append("reward %.6f expected %.6f (%s)" % (d["reward"], float(want), want))
    for pid, spec in x.parts.items():
        p = d["parts"].get(pid)
        if p is None:
            out.append("%s missing" % pid)
            continue
        if abs(p["s"] - float(x.s(pid))) > 1e-9:
            out.append("%s s %s expected %s" % (pid, p["s_exact"], x.s(pid)))
        gates = {k for k, v in p["gates"].items() if not v}
        if gates != spec["gates"]:
            out.append("%s failing gates %s expected %s" % (pid, sorted(gates), sorted(spec["gates"])))
        if pid == "P4":
            if not spec["gates"]:
                bad = {k for k, v in p["checks"].items() if not v}
                ni = spec["not_installed"]
                if (len(bad) != ni) if isinstance(ni, int) else (bad != ni):
                    out.append("P4 not installed %s expected %s" % (sorted(bad), ni if isinstance(ni, int) else sorted(ni)))
        elif spec["checks"] is not None:
            bad = {k for k, v in p["checks"].items() if not v}
            if bad != spec["checks"]:
                out.append("%s failing checks %s expected %s" % (pid, sorted(bad), sorted(spec["checks"])))
    for fn in extra:
        try:
            e = fn(d)
        except Exception as ex:          # noqa
            e = "extra assertion raised %s: %s" % (type(ex).__name__, ex)
        if e:
            out.append(e)
    return out


def check_rule_matches_grader():
    """The weights and gates written above, against the grader's constants (grade_watch imports no geometry at
    module level). A difference is reported as an OFF line, never fixed here."""
    sys.path.insert(0, TESTS)
    import grade_watch as G
    out = []
    for pid, what, w, gates, cw in G.JOB_PARTS:
        if pid not in PART_W:
            out.append("grader grades %s, not in this rule" % pid)
            continue
        if F(w) != PART_W[pid]:
            out.append("%s weight %s in the grader, %s here" % (pid, w, PART_W[pid]))
        if tuple(gates) != GATES[pid]:
            out.append("%s gates %s in the grader, %s here" % (pid, gates, GATES[pid]))
        if pid != "P4" and dict(cw) != CW[pid]:
            out.append("%s check weights %s in the grader, %s here" % (pid, cw, CW[pid]))
    if {p[0] for p in G.JOB_PARTS} != set(PART_W):
        out.append("grader parts %s" % [p[0] for p in G.JOB_PARTS])
    return out


# ---------------- runner ----------------
def build(index, ref_job, out):
    """--build child: copy the reference job folder to out and apply the anchor's change."""
    name, change, _, _ = ANCHORS[index]
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(ref_job, out, symlinks=True)
    if change is not None:
        sys.path.insert(0, ROOT)
        change(out)


def run_anchor(i, ref_job, timeout):
    name, _, x, extra = ANCHORS[i]
    t0 = time.time()
    tmp = tempfile.mkdtemp(prefix="job_anchor_")
    d = os.path.join(tmp, "delivery")
    reward, details = os.path.join(tmp, "reward.txt"), os.path.join(tmp, "details.json")
    row = {"name": name, "expected": float(x.reward()), "exact": str(x.reward()), "got": None, "s": {}, "ok": False, "msg": ""}
    try:
        try:
            b = subprocess.run([sys.executable, HERE, "--build", str(i), "--job", ref_job, "--out", d], cwd=ROOT,
                               stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            row["msg"] = "build timed out"
            return row
        if b.returncode != 0:
            row["msg"] = "build failed: " + ((b.stderr.strip().splitlines() or ["no output"])[-1])
            return row
        left = timeout - (time.time() - t0)
        try:
            g = subprocess.run([sys.executable, "-I", "grade_watch.py", d, "--reward", reward, "--details", details],
                               cwd=TESTS, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=max(1.0, left))
        except subprocess.TimeoutExpired:
            row["msg"] = "grading timed out"
            return row
        if g.returncode != 0 or not os.path.isfile(details):
            row["msg"] = "grader exit %d: %s" % (g.returncode, (g.stderr.strip().splitlines() or ["no output"])[-1])
            return row
        with open(details) as f:
            dd = json.load(f)
        with open(reward) as f:
            text = f.read().strip()
        row["got"] = dd["reward"]
        row["s"] = {pid: p["s_exact"] for pid, p in dd["parts"].items()}
        row["grade_s"] = dd.get("elapsed_s")
        diffs = compare(x, dd, extra)
        if abs(float(text) - dd["reward"]) > 1e-6:
            diffs.append("reward file %r, details %r" % (text, dd["reward"]))
        row["ok"] = not diffs
        row["msg"] = "; ".join(diffs)
        return row
    finally:
        row["time"] = time.time() - t0
        shutil.rmtree(tmp, ignore_errors=True)


def line(row):
    s = " ".join("%s=%s" % (k, v) for k, v in sorted(row["s"].items()))
    got = "%.4f" % row["got"] if row["got"] is not None else "-"
    return "%-4s %-72s reward %s expected %.4f  %s  %4.0f s%s" % (
        "ok" if row["ok"] else "OFF", row["name"], got, row["expected"], s, row["time"],
        ("  | " + row["msg"]) if row["msg"] else "")


def main(argv):
    opt = lambda k: argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else None
    if opt("--build") is not None:
        build(int(opt("--build")), os.path.abspath(opt("--job")), os.path.abspath(opt("--out")))
        return 0
    from concurrent.futures import ThreadPoolExecutor
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in ("--only", "--job", "--timeout"))]
    workers = int(pos[0]) if pos else 2
    timeout = float(opt("--timeout") or 4000)
    pick = list(range(len(ANCHORS)))
    if opt("--only"):
        want = [w.strip() for w in opt("--only").split(",") if w.strip()]
        names = [a[0] for a in ANCHORS]
        pick = [i for i, n in enumerate(names) if any(w == n for w in want) or any(w in n and w not in names for w in want)]
        if not pick:
            raise SystemExit("no anchor matches %r" % opt("--only"))
    bad = 0
    for e in check_rule_matches_grader():
        print("OFF  rule: " + e, flush=True)
        bad += 1
    tmp = None
    job = opt("--job")
    if job is None:
        tmp = tempfile.mkdtemp(prefix="job_anchors_ref_")
        job = os.path.join(tmp, "ref")
        subprocess.run([sys.executable, os.path.join(ROOT, "solution", "reference_watch.py"), job, "--job"],
                       check=True, stdout=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    job = os.path.abspath(job)
    print("reference job folder %s, %d anchors, %d workers, timeout %g s" % (job, len(pick), workers, timeout), flush=True)
    rows = []
    try:
        with ThreadPoolExecutor(workers) as pool:
            for row in pool.map(lambda i: run_anchor(i, job, timeout), pick):
                rows.append(row)
                bad += not row["ok"]
                print(line(row), flush=True)
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    print("\n| anchor | expected | got | P1 | P2 | P3 | P4 | time s | |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        got = "%.4f" % r["got"] if r["got"] is not None else "-"
        print("| %s | %.4f (%s) | %s | %s | %s | %s | %s | %.0f | %s |" % (
            r["name"], r["expected"], r["exact"], got, *(r["s"].get(p, "-") for p in ("P1", "P2", "P3", "P4")),
            r["time"], "ok" if r["ok"] else "OFF: " + r["msg"]))
    print("%d of %d anchors ok" % (len(rows) - sum(not r["ok"] for r in rows), len(rows)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
