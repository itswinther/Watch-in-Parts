"""Fixture tests for the one-job grader (tests/grade_watch.py without --stage).
    python3 tests/test_job_grader.py [--slow] [--only a,b,...] [--base /abs/REF_OUT | --job /abs/JOB]
Run from the repository root. Without --slow only the quick cases run (seconds to a minute): the empty
folder through the real grader, and the gates and helpers on their own. --slow adds the full gradings (each
runs the grader once, `python3 -I grade_watch.py` from tests/ in a fresh process, one at a time; a full
delivery takes about 12 minutes on 4 CPUs, all six about an hour).
--job uses a job folder as it is (`python3 solution/reference_watch.py JOB --job`); with neither, that job
folder is built into a temporary folder (about 1 min). --base builds the job folder from stage folders with
tests/make_job_folder.py; since the two-body barrel (its arbor rises to z 5.6) those stage folders' barrel cock
collides with the arbor, so --base no longer gives a reference that passes (use --job).
Cases (the letters of the builder brief):
  a  empty folder: reward 0, every part 0, the reward file says 0
  b  the reference job folder (with its truthful report.json, every part `pass`): 1.0
  c  variant_6h.json missing: P3's gates fail, the others pass, reward = 0.5 x (1 - 0.15/0.75) x 31/34 (the
     reference's report claims P3 `pass`: honesty points 1, 1, -2, 1, h = 1/4, factor (0.75 + 0.10/4) / 0.85)
  d  the variant names a different fixed list (bridge_alt, a byte copy of bridge): P3's same_frame gate (C4) fails
  e  assembly.json missing: P4 scores 0, the others pass, reward = 0.5 x (1 - 0.25/0.75) x 31/34
  f  movement.json missing, variant present: P1, P2 and P4 fail their gates; P3 is still graded, all its checks
     run, and its same_frame gate fails because there is no movement.json to compare with, so P3 scores 0 too
     and the reward is 0 (decided: the variant is defined against movement.json; without it there is no job)
Quick cases for crown winding (Part 5's format, geometry/keyless_job.py; graded only when KEYLESS_IN_JOB):
  keyless_format  a `keyless` section loads and its parts are read; a part used twice (keyless and a mobile, keyless
                  and fixed, twice in keyless) is a format error; the section's own rules; no section: as before
  friction_on     a friction_on mobile turns at its carrier's speed; bad carriers are format errors; P5's split
  keyless_assembly with P5 on, the keyless parts are parts of Part 4 (checks, replay, standing in place)
  keyless_switch  the P5 row follows KEYLESS_IN_JOB; the scaled table agrees with A's files
  keyless_engine  the runner's loader stub (spec and sup empty dicts, pull_of works) and every SCALE_TABLE row at its
                  job value in the runner; check_table() is [] (A's 01:00 items 1, 2)
  keyless_phases  a crashed worker fails only its phase; a dead runner keeps the phases before it; on a timeout the
                  finished phases are kept and the runner's process group is killed (items 3, 7)
  keyless_minute  the minute mobile not friction_on: AT-5/AT-6 fail with the reason; free: held covers it; the stem
                  protrudes at its crown end only (items 6, 7)"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from fractions import Fraction

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TESTS = os.path.join(ROOT, "tests")
sys.path.insert(0, ROOT)
sys.path.insert(0, TESTS)
import grade_watch as G           # noqa: E402
import make_job_folder            # noqa: E402

W_ = {p[0]: Fraction(p[2]) for p in G.JOB_PARTS}
TOTAL = sum(W_.values())


def honesty_factor(claims, truths):
    """(W_PRODUCT + W_HONESTY x h) / (W_PRODUCT + W_HONESTY), h = max(0, mean of A's points), exact."""
    C = G._a_constants()
    pts = [Fraction(repr(float(C.HONESTY_POINTS[(claims[p], truths[p])]))) for p in truths]
    h = max(Fraction(0), sum(pts, Fraction(0)) / len(pts))
    wp, wh = Fraction(repr(C.W_PRODUCT)), Fraction(repr(C.W_HONESTY))
    return (wp + wh * h) / (wp + wh)


def without(*pids):
    """The reward when every check of every part passes except that the parts pids score 0, with the reference's
    report.json (every part claimed `pass`) scored against that result."""
    truths = {p: p not in pids for p in W_}
    r = Fraction(1, 2) * (1 - sum(W_[p] for p in pids) / TOTAL)
    return float(r * honesty_factor({p: "pass" for p in W_}, truths))


def run_grader(folder, out):
    """The grader as the verifier runs it. Returns (details, reward file text, seconds)."""
    reward, details = os.path.join(out, "reward.txt"), os.path.join(out, "details.json")
    t = time.time()
    p = subprocess.run([sys.executable, "-I", "grade_watch.py", folder, "--reward", reward, "--details", details],
                       cwd=TESTS, capture_output=True, text=True)
    assert p.returncode == 0, p.stdout + p.stderr
    with open(details) as f:
        d = json.load(f)
    with open(reward) as f:
        return d, f.read(), time.time() - t


def part_ok(d, pid):
    p = d["parts"][pid]
    return all(p["gates"].values()) and all(p["checks"].values()) and p["s"] == 1.0


# ---------------- quick cases ----------------
def case_a(job, tmp):
    folder = os.path.join(tmp, "empty")
    os.makedirs(folder)
    d, text, sec = run_grader(folder, tmp)
    assert d["reward"] == 0.0 and text.strip() == "0.000000", (d["reward"], text)
    assert all(p["s"] == 0.0 for p in d["parts"].values()), {k: p["s"] for k, p in d["parts"].items()}
    assert all(not p["gates"]["files"] for p in d["parts"].values())
    assert d["parts_graded"] == [p[0] for p in G.JOB_PARTS]
    return "reward %s, file %r, parts %s, %.0f s" % (d["reward"], text.strip(), {k: p["s"] for k, p in d["parts"].items()}, sec)


def case_frame_gate(job, tmp):
    """d (gate only, quick): job_same_frame on the reference variant, and on the variant with bridge renamed."""
    from geometry import watch as W
    folder = os.path.join(tmp, "frame")
    shutil.copytree(job, folder)
    cache = {}
    v = W.load_movement(folder, G.JOB_VARIANT, cache=cache)
    ok, info = G.job_same_frame(folder, v)
    assert ok, info
    _different_fixed(folder)
    v2 = W.load_movement(folder, G.JOB_VARIANT, cache=cache)
    ok2, info2 = G.job_same_frame(folder, v2)
    assert not ok2 and info2["only_in_movement"] == ["bridge"] and info2["only_in_variant"] == ["bridge_alt"], info2
    # the same names in another order fail it (C4: the same names in the same order)
    _edit(folder, G.JOB_VARIANT, lambda doc: doc.update(fixed=list(reversed(v.doc["fixed"]))))
    ok5, info5 = G.job_same_frame(folder, W.load_movement(folder, G.JOB_VARIANT, cache=cache))
    assert not ok5 and not info5["same_fixed"] and not info5["only_in_variant"], info5
    # a different case_centre alone also fails it
    _edit(folder, G.JOB_VARIANT, lambda doc: doc.update(fixed=v.doc["fixed"], case_centre=[doc["case_centre"][0] + 0.5, doc["case_centre"][1]]))
    ok3, info3 = G.job_same_frame(folder, W.load_movement(folder, G.JOB_VARIANT, cache=cache))
    assert not ok3 and info3["same_fixed"] and not info3["same_case_centre"], info3
    # movement.json missing: the gate fails, it does not crash
    os.remove(os.path.join(folder, G.JOB_MOVEMENT))
    ok4, info4 = G._run(lambda: G.job_same_frame(folder, v))
    assert not ok4 and "movement.json not found" in info4["error"], info4
    return "reference variant passes; bridge->bridge_alt fails (%s); same names reversed fail; case centre +0.5 fails; no movement.json fails (%s)" % (
        info2["only_in_variant"], info4["error"])


def case_day_gate(job, tmp):
    """C3 (P2 and P3): hands.day declared on a part no other hand uses. A missing day hand fails C3, not C1."""
    from geometry import watch as W
    for name in (G.JOB_MOVEMENT, G.JOB_VARIANT):
        m = W.load_movement(job, name)
        ok, info = G.job_day_declared(m)
        assert ok, (name, info)
        for h in ("hour", "minute", "seconds"):
            m.hands["day"] = m.hands[h]
            ok, info = G.job_day_declared(m)
            assert not ok and info["also_used_by"] == [h], (name, h, info)
    folder = os.path.join(tmp, "noday")
    shutil.copytree(job, folder)
    _edit(folder, G.JOB_VARIANT, lambda doc: doc["hands"].pop("day"))
    v = W.load_movement(folder, G.JOB_VARIANT)          # C1 still holds
    ok, info = G.job_day_declared(v)
    assert not ok and "no 'day' hand" in info["error"], info
    return "both reference movements pass; day on the hour, minute or seconds hand part fails; no day hand: C1 holds, C3 fails"


def case_cache(job, tmp):
    """The part cache: a part shared by both movements is the same solid; a changed file is loaded again."""
    from geometry import watch as W
    cache = {}
    m = W.load_movement(job, cache=cache)
    v = W.load_movement(job, G.JOB_VARIANT, cache=cache)
    shared = sorted(set(m.all_parts()) & set(v.all_parts()) - {"barrel"})
    assert shared and all(m.all_parts()[n] is v.all_parts()[n] for n in shared)
    fresh = W.load_part_file(W.part_path(job, shared[0]))
    assert abs(float(fresh.volume()) - float(m.all_parts()[shared[0]].volume())) == 0.0
    # the default call is unchanged: no cache, movement.json
    m0 = W.load_movement(job)
    assert sorted(m0.all_parts()) == sorted(m.all_parts())
    return "%d parts shared and loaded once: %s" % (len(shared), ", ".join(shared))


def case_deadline(job, tmp):
    """The whole-run limit: a check started after the deadline fails with a message, never runs."""
    ran = []
    ok, info = G._run(lambda: (ran.append(1) or True, {}), deadline=time.monotonic() - 1)
    assert not ok and not ran and "whole-run time limit" in info["error"], info
    ok2, _ = G._run(lambda: (True, {}), deadline=time.monotonic() + 60)
    assert ok2
    return "past the deadline: not run, %r; before it: runs" % info["error"]


CACHE = {}          # part solids shared by the quick cases below (geometry.watch's cache: by name and file bytes)


def _keyless_folder(job, tmp, name, keyless=True, friction=True):
    """A copy of the job folder whose movement.json has the cannon pinion and minute hand as their own mobile
    `cannon`, "friction_on": "centre" (friction), and a small `keyless` section (keyless) whose parts are byte copies
    of hand parts (their shapes do not matter to the format)."""
    folder = os.path.join(tmp, name)
    shutil.copytree(job, folder)
    for src, dst in (("hour_hand", "k_stem"), ("minute_hand", "k_ratchet"), ("seconds_hand", "k_wheel"),
                     ("day_hand", "k_slide")):
        shutil.copyfile(os.path.join(folder, "parts", src + ".step"), os.path.join(folder, "parts", dst + ".step"))

    def edit(doc):
        if friction:
            cen = doc["mobiles"]["centre"]
            doc["mobiles"]["centre"] = dict(cen, parts=[p for p in cen["parts"] if p not in ("cannon", "minute_hand")])
            doc["mobiles"]["cannon"] = dict(cen, parts=["cannon", "minute_hand"], friction_on="centre")   # material kept
            for e in doc["meshes"]:
                if e["driver"] == "centre" and e["driven"] == "minute_wheel":
                    e["driver"] = "cannon"
            doc["hands"]["minute"]["mobile"] = "cannon"
        if keyless:
            cx, cy = doc["case_centre"]
            doc["keyless"] = {"stem": {"parts": ["k_stem"], "point": [cx, cy, 5.5], "direction": [0.8090, 0.5878, 0]},
                              "arbor": {"parts": ["k_ratchet"]},
                              "mobiles": {"k_wheel": {"kind": "free", "dof": "rot", "point": [6.1, -2.9, 0],
                                                      "direction": [0, 0, 1], "parts": ["k_wheel"]},
                                          "k_slide": {"kind": "spring", "dof": "slide", "direction": [0.8090, 0.5878, 0],
                                                      "rest": -1, "on_stem": True, "parts": ["k_slide"]}}}
    _edit(folder, G.JOB_MOVEMENT, edit)
    return folder


def _format_error(folder, fn=None):
    """The FormatError message of loading movement.json (and fn(movement) after it), or None."""
    from geometry import watch as W
    from geometry.core import FormatError
    try:
        m = W.load_movement(folder, cache=CACHE)
        if fn is not None:
            fn(m)
    except FormatError as e:
        return str(e)
    return None


def case_keyless_format(job, tmp):
    """The `keyless` section (Part 5's format): it loads, its parts are read through the movement's loader, a part
    used twice across fixed, mobiles and keyless is a format error, and the section's own rules hold."""
    from geometry import watch as W
    from geometry import keyless_job as KJ
    folder = _keyless_folder(job, tmp, "keyless")
    m = W.load_movement(folder, cache=CACHE)
    assert m.keyless_names == ["k_stem", "k_ratchet", "k_wheel", "k_slide"], m.keyless_names
    k, solids = KJ.load_keyless(m)
    assert sorted(solids) == ["k_ratchet", "k_slide", "k_stem", "k_wheel"] and all(s.volume() > 0 for s in solids.values())
    assert k["mobiles"]["k_slide"]["on_stem"] and k["mobiles"]["k_slide"]["rest"] == -1 and k["arbor"] == ["k_ratchet"]
    assert abs(k["stem"]["direction"][0] ** 2 + k["stem"]["direction"][1] ** 2 - 1) < 1e-12
    msgs = {}
    # a part used twice: in the keyless section and in a mobile; in the keyless section and in fixed; twice in keyless
    for label, change in (("mobile", lambda d: d["keyless"]["stem"].update(parts=["minute_hand"])),
                          ("fixed", lambda d: d["keyless"]["arbor"].update(parts=["bridge"])),
                          ("keyless", lambda d: d["keyless"]["mobiles"]["k_wheel"].update(parts=["k_stem"]))):
        f2 = _keyless_folder(job, tmp, "twice_" + label)
        _edit(f2, G.JOB_MOVEMENT, change)
        msgs[label] = _format_error(f2)
        assert msgs[label] is not None and "used more than once" in msgs[label], (label, msgs[label])
    # the section's rules (FormatError from Part 5's reader; movement.json itself still loads)
    for label, change, want in (
            ("not radial", lambda d: d["keyless"]["stem"].update(point=[0, 0, 5.5]), "radial"),
            ("not horizontal", lambda d: d["keyless"]["stem"].update(direction=[0.8, 0.58, 0.1]), "horizontal"),
            ("on_stem rot", lambda d: d["keyless"]["mobiles"]["k_wheel"].update(on_stem=True), "ride on the stem"),
            ("spring rest", lambda d: d["keyless"]["mobiles"]["k_slide"].update(rest=0), "rest 1 or -1"),
            ("name clash", lambda d: d["keyless"]["mobiles"].update(third=d["keyless"]["mobiles"].pop("k_wheel")),
             "bad mobile name")):
        f2 = _keyless_folder(job, tmp, "rule_" + label.replace(" ", "_"))
        _edit(f2, G.JOB_MOVEMENT, change)
        assert _format_error(f2) is None, label
        msgs[label] = _format_error(f2, KJ.parse_keyless)
        assert msgs[label] is not None and want in msgs[label], (label, msgs[label])
    # no keyless section: movement.json loads as before (P1 to P4 unchanged); Part 5's reader reports it
    f3 = _keyless_folder(job, tmp, "no_keyless", keyless=False, friction=False)
    m3 = W.load_movement(f3, cache=CACHE)
    assert m3.keyless_names == [] and m3.friction == {}
    assert "no 'keyless' section" in _format_error(f3, KJ.parse_keyless)
    return "loads (%d keyless parts); twice: %s" % (len(solids), "; ".join("%s: %s" % kv for kv in msgs.items()))


def case_friction_on(job, tmp):
    """friction_on: the mobile turns at its carrier's speed (and drives what it meshes with); a carrier that is not
    coaxial, or is itself carried, is a format error; P5's rule puts it, and what it alone drives, among the free
    bodies."""
    from geometry import watch as W
    from geometry import keyless_job as KJ
    folder = _keyless_folder(job, tmp, "friction", keyless=False)
    m = W.load_movement(folder, cache=CACHE)
    assert m.friction == {"cannon": "centre"}
    sp, conflicts = m.speeds()
    assert not conflicts and sp["cannon"] == sp["centre"] == G.HAND_SPEED["minute"], (sp, conflicts)
    assert sp["hour_wheel"] == G.HAND_SPEED["hour"] and sp["day"] == G.DAY_SPEED, sp
    ref = W.load_movement(job, cache=CACHE).speeds()[0]
    assert all(sp[k] == v for k, v in ref.items()), "speeds differ from the reference's"
    fixed, free = KJ.train_split(m)
    assert sorted(fixed) == ["centre", "fourth", "seconds", "third"], fixed
    assert free == ["cannon", "day", "day_idler", "hour_wheel", "minute_wheel"], free
    msgs = {}
    for label, change, want in (
            ("not coaxial", lambda d: d["mobiles"]["cannon"].update(friction_on="third"), "coaxial"),
            ("chain", lambda d: d["mobiles"]["centre"].update(friction_on="cannon"), "itself carried"),
            ("barrel", lambda d: d["mobiles"]["cannon"].update(friction_on="barrel"), "not 'barrel'")):
        f2 = _keyless_folder(job, tmp, "friction_" + label.replace(" ", "_"), keyless=False)
        _edit(f2, G.JOB_MOVEMENT, change)
        msgs[label] = _format_error(f2)
        assert msgs[label] is not None and want in msgs[label], (label, msgs[label])
    return "cannon turns at %s like centre; free bodies %s; errors: %s" % (sp["cannon"], free, msgs)


def case_keyless_assembly(job, tmp):
    """With Part 5 graded, the keyless section's parts are parts of movement.json for Part 4: they are in P4's
    checks, in the replay (a part in `order` is replayed, one left out stands in place) and in the bounding box.
    KEYLESS_IN_JOB is set True for this case only. Without it, P4's parts are those of the reference."""
    from geometry import watch as W
    from geometry import keyless_job as KJ
    folder = _keyless_folder(job, tmp, "keyless_asm")
    far = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 500.0], [0, 0, 0, 1]]
    eye = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    with open(os.path.join(folder, G.JOB_ASSEMBLY), "w") as f:
        json.dump({"order": ["k_stem"], "paths": {"k_stem": [far, eye]}}, f)
    m = W.load_movement(folder, cache=CACHE)
    old = KJ.KEYLESS_IN_JOB
    try:
        KJ.KEYLESS_IN_JOB = True
        gates, checks, det = G._job_assembly(folder, m, G._run)
    finally:
        KJ.KEYLESS_IN_JOB = old
    assert gates == {"files": True, "plan": True}, (gates, det.get("plan"))
    assert set(m.keyless_names) <= set(checks) and len(checks) == len(m.all_parts()) + len(m.keyless_names), checks
    res = det["parts"]
    assert res["k_stem"]["format_messages"] and "moves" in res["k_stem"]["format_messages"][0], res["k_stem"]
    assert all(res[n].get("not_in_order") for n in ("k_ratchet", "k_wheel", "k_slide")), {n: res[n] for n in m.keyless_names}
    assert not any(checks[n] for n in m.keyless_names)
    m2 = W.load_movement(folder, cache=CACHE)          # P5 off: no keyless part in Part 4
    _, checks2, _ = G._job_assembly(folder, m2, G._run) if not old else (None, {}, None)
    assert old or not set(m2.keyless_names) & set(checks2), checks2
    return "P4 with P5 on: %d checks (%d keyless); k_stem replayed: %s; the other keyless parts stand in place" % (
        len(checks), len(m.keyless_names), res["k_stem"]["format_messages"][0])


def case_keyless_switch(job, tmp):
    """KEYLESS_IN_JOB is False on this branch: no P5 row; the scaled table agrees with A's files."""
    from geometry import keyless_job as KJ
    errs = KJ.check_table()
    assert not errs, errs
    rows = [p[0] for p in G.JOB_PARTS]
    assert rows == (["P1", "P2", "P3", "P4", "P5"] if KJ.KEYLESS_IN_JOB else ["P1", "P2", "P3", "P4"]), rows
    return "KEYLESS_IN_JOB %s, parts %s, scaled %s" % (KJ.KEYLESS_IN_JOB, rows, KJ.scaled())


def _tiny_world(folder, minute_free=True):
    """A small world in geometry/keyless_job.py write_world's format (a plate, the arbor, a stem, the minute mobile;
    nothing meshes, so every step fails, quickly): Part 5's runner on it takes about a second a phase."""
    import math
    import manifold3d as m3
    from geometry import keyless_job as KJ

    def cyl(r, h, x, y, z):
        return m3.Manifold.cylinder(h, r, circular_segments=32).translate([x, y, z])
    bodies = []

    def add(name, kind, solid, dof=None, point=None, direction=None, rest=None):
        bodies.append(dict(name=name, kind=kind, dof=dof, point=point, direction=direction, rest=rest, carrier=None,
                           solid=solid, role="test"))
    add("fixed", "fixed", m3.Manifold.cube([30, 30, 1]).translate([-15, -15, -2]))
    add("barrel", "main", cyl(2, 1, 0, 0, 0), dof="rot", point=(0, 0, 0), direction=(0, 0, 1),
        rest=-KJ.WIND_SENSE * math.inf)
    add("stem", "driven", m3.Manifold.cylinder(4, 0.5, circular_segments=16).rotate([0, 90, 0]).translate([8, 0, 3]),
        dof="stem", point=(0, 0, 3), direction=(1, 0, 0))
    if minute_free:
        add(KJ.MINUTE, "contact", cyl(1.5, 1, -6, 6, 0), dof="rot", point=(-6, 6, 0), direction=(0, 0, 1))
    else:
        add(KJ.MINUTE, "fixed", cyl(1.5, 1, -6, 6, 0))
    meta = {"minute_free": minute_free, "minute_mobile": "centre", "bounds": [True, {}]}
    if not minute_free:
        meta["setting_not_run"] = KJ.minute_not_free_reason("centre")
    KJ.write_world(folder, bodies, meta)
    return folder


STUB_PROBE = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
import grade_keyless as GK
from geometry import keyless_job as KJ
GK.setup(sys.argv[2])
E, G = GK.E, GK.G
spec, parts, sup, defs = G.load(None, None)
live = {}
for row in KJ.SCALE_TABLE:
    where, name = row[0], row[1]
    if where == "constants":
        v = getattr(G.C, name)
    elif ":" in name:
        cls, rest = name.split(".", 1)
        fn, arg = rest.split(":")
        v = getattr(getattr(E, cls), fn).__defaults__[0]
    else:
        v = getattr(E, name)
    live[where + "." + name] = [list(v) if isinstance(v, tuple) else v, KJ.job_value(row)]
ph, out, err = G.worker(("wind", (None, None), defs, None))
print(json.dumps({"spec": spec, "sup": sup, "pull": G.pull_of(spec), "want_pull": KJ.scaled()["PULL"], "live": live,
                  "worker_error": err}))
"""


def case_keyless_engine(job, tmp):
    """A's 01:00 items 1 and 2: the runner's loader stub gives an empty dict for spec and sup, so A's worker reads the
    pull with pull_of (the scaled PULL); every SCALE_TABLE row (MAIN_TRY in the engine, the floors, FORCE_EPS,
    World.phase's budget, the fit rule's lengths, PULL_RANGE) is set to its job value in the runner's interpreter;
    check_table() is [] against the merged engine (in a fresh interpreter, so this one's A modules stay unscaled)."""
    from geometry import keyless_job as KJ
    assert KJ.check_table() == [], KJ.check_table()
    assert KJ.UNSCALED == ()
    names = {r[0] + "." + r[1] for r in KJ.SCALE_TABLE}
    for n in ("engine.MAIN_TRY", "engine.RADIUS_FLOOR", "engine.LEVER_FLOOR", "engine.NEIGHBOUR_MARGIN",
              "engine.SPRING_PUSH_ARC", "engine.FORCE_EPS", "engine.World.phase:budget", "constants.FIT_CLEARANCE",
              "constants.FIT_CENTRE_TOL", "constants.FIT_EMPTY_INSET", "constants.PULL_RANGE"):
        assert n in names, n
    assert "engine.World.step:main_try_arc" not in names
    assert {r[1]: r[4] for r in KJ.SCALE_TABLE}["FORCE_EPS"] == 3
    world = _tiny_world(os.path.join(tmp, "world"))
    p = subprocess.run([sys.executable, "-I", "-c", STUB_PROBE, TESTS, world], capture_output=True, text=True, cwd=TESTS)
    assert p.returncode == 0, p.stderr[-3000:]
    r = json.loads(p.stdout.strip().splitlines()[-1])
    assert r["spec"] == {} and r["sup"] == {}, r
    assert r["pull"] == r["want_pull"] == 1.294, r
    assert r["worker_error"] is None, r["worker_error"]
    bad = {k: v for k, v in r["live"].items() if v[0] != v[1]}
    assert not bad, bad
    return "stub spec %s sup %s, pull %s; %d rows at their job values (MAIN_TRY %s, phase budget %s, FORCE_EPS %.3g)" % (
        r["spec"], r["sup"], r["pull"], len(r["live"]), r["live"]["engine.MAIN_TRY"][0],
        r["live"]["engine.World.phase:budget"][0], r["live"]["engine.FORCE_EPS"][0])


def _group_gone(pgid, wait_s=10.0):
    """True when no running (non-zombie) process is in process group pgid, within wait_s."""
    t = time.time()
    while True:
        alive = []
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                with open("/proc/%s/stat" % pid) as f:
                    st = f.read().rsplit(")", 1)[1].split()
            except OSError:
                continue
            if int(st[2]) == pgid and st[0] != "Z":
                alive.append(pid)
        if not alive:
            return True
        if time.time() - t > wait_s:
            return False
        time.sleep(0.2)


def case_keyless_phases(job, tmp):
    """A's 01:00 items 3 and 7: finished phases survive. (1) --jobs 3, the `set` worker crashes: every other phase is
    recorded, set fails with the reason. (2) serial, the runner itself dies in `backward`: wind, hold and run are in
    the result file already. (3) --jobs 3, `wind` never returns and the time limit is reached: the other phases are
    kept, and the runner's whole process group (its spawned workers included) is killed."""
    from geometry import keyless_job as KJ
    world = _tiny_world(os.path.join(tmp, "world"))
    steps = list(KJ.step_weights())
    c1, d1 = G.keyless_run(world, jobs=3, extra=["--test-fault", "set:crash"])
    seq = d1["sequence"]
    assert d1.get("done") and set(seq) == set(steps[1:]), (d1.get("error"), sorted(seq))
    assert "worker failed" in seq["set"]["error"] and not c1["set"], seq["set"]
    assert all("error" not in seq[k] for k in steps[1:] if k != "set"), {k: seq[k].get("error") for k in seq}
    assert set(d1["steps"]) == set(steps), d1["steps"]
    c2, d2 = G.keyless_run(world, jobs=1, extra=["--test-fault", "backward:crash"])
    assert d2["process"]["returncode"] == 70, d2["process"]
    assert d2["phases_done"] == ["assemble", "wind", "first"] and set(d2["sequence"]) == {"wind", "hold", "run"}, d2
    assert set(d2["steps"]) == {"assemble", "wind", "hold", "run"} and not d2.get("done"), d2["steps"]
    t = time.monotonic()
    c3, d3 = G.keyless_run(world, deadline=time.monotonic() + 20, jobs=3, extra=["--test-fault", "wind:hang"])
    took = time.monotonic() - t
    assert "timeout" in d3["process"].get("error", ""), d3["process"]
    assert set(d3["phases_done"]) == {"assemble", "first", "backward", "set", "return"}, d3["phases_done"]
    assert set(d3["steps"]) == set(steps) - {"wind"} and not c3["wind"], d3["steps"]
    assert _group_gone(d3["process"]["pgid"]), "process group %d still has running processes" % d3["process"]["pgid"]
    return ("crash in set (--jobs 3): %s; runner dies in backward (serial): kept %s; hang in wind: timeout after "
            "%.0f s, kept %s, process group %d gone" % (seq["set"]["error"][:40], d2["phases_done"], took,
                                                        d3["phases_done"], d3["process"]["pgid"]))


def case_keyless_minute(job, tmp):
    """A's 01:00 item 6, B's rule (Decisions 15:47 and the 17:46 line): the minute hand's mobile is a free contact
    body in P5 only if it is friction_on (or driven only through one); otherwise build_world marks the setting steps
    not run, and the runner fails AT-5 and AT-6 with that reason instead of letting "never both trains" pass
    trivially. With the minute mobile free, AT-0's held check covers it (A's held_check skips the name minute_wheel).
    Item 7: the stem protrudes at its crown end only."""
    import types
    import manifold3d as m3
    from geometry import watch as W
    from geometry import keyless_job as KJ
    # build_world on the job: the reference's minute hand is on the centre mobile (no friction_on): fixed
    f0 = _keyless_folder(job, tmp, "minute_fixed", friction=False)
    m0 = W.load_movement(f0, cache=CACHE)
    k0, s0 = KJ.load_keyless(m0)
    b0, meta0 = KJ.build_world(m0, k0, s0)
    kinds0 = {b["name"]: b["kind"] for b in b0}
    assert kinds0[KJ.MINUTE] == "fixed" and not meta0["minute_free"] and "AT-5 and AT-6 fail" in meta0["setting_not_run"]
    f1 = _keyless_folder(job, tmp, "minute_free", friction=True)
    m1 = W.load_movement(f1, cache=CACHE)
    k1, s1 = KJ.load_keyless(m1)
    b1, meta1 = KJ.build_world(m1, k1, s1)
    kinds1 = {b["name"]: b["kind"] for b in b1}
    assert kinds1[KJ.MINUTE] == "contact" and meta1["minute_free"] and "setting_not_run" not in meta1, meta1
    # the runner on a small world: minute fixed -> set and return not run, the others run
    w0 = _tiny_world(os.path.join(tmp, "w_fixed"), minute_free=False)
    c, d = G.keyless_run(w0)
    seq = d["sequence"]
    for k in KJ.SETTING_STEPS:
        assert not c[k] and "hands cannot be set" in seq[k]["error"], seq[k]
    assert all("error" not in seq[k] for k in ("wind", "hold", "run", "backward")), seq
    assert KJ.MINUTE not in d["assemble"]["held"], d["assemble"]["held"]
    w1 = _tiny_world(os.path.join(tmp, "w_free"), minute_free=True)
    c, d = G.keyless_run(w1)
    assert all("error" not in d["sequence"][k] for k in d["sequence"]), d["sequence"]
    assert KJ.MINUTE in d["assemble"]["held"], d["assemble"]["held"]
    # stem protrusion: only the crown end (the side the stem's direction points to) counts
    fake = types.SimpleNamespace(case_centre=(0.0, 0.0), extent=lambda: {"z_min": 0.0, "z_max": 1.0})
    k = {"stem": {"parts": ["st"], "direction": (1.0, 0.0, 0.0)}}

    def stem(x0, x1):
        return m3.Manifold.cylinder(x1 - x0, 0.3, circular_segments=16).rotate([0, 90, 0]).translate([x0, 0, 0.5])
    far = KJ.bounds(fake, k, {"st": stem(-W.CASE_RADIUS - 1.3, 10.0)})
    crown = KJ.bounds(fake, k, {"st": stem(-10.0, W.CASE_RADIUS + 1.3)})
    assert not far[0] and far[1]["stem_protrude"] < 0, far
    assert crown[0] and abs(crown[1]["stem_protrude"] - 1.3) < 0.01, crown
    return ("minute on centre: %s, setting steps: %s; friction_on: %s, held covers it; stem past the far end only: "
            "protrude %s (fails), at the crown: %s (passes)" % (kinds0[KJ.MINUTE], seq["set"]["error"][:60],
                                                                 kinds1[KJ.MINUTE], far[1]["stem_protrude"],
                                                                 crown[1]["stem_protrude"]))


def case_reward_formula(job, tmp):
    # parts reward 0.5 x (1 - 0.15/0.75) = 2/5; the report claims P3 `pass` while it fails: points 1, 1, -2, 1,
    # mean 1/4, factor (0.75 + 0.10/4) / 0.85 = 31/34; reward 2/5 x 31/34 = 31/85
    assert without("P3") == float(Fraction(31, 85)), without("P3")
    # 0.5 x (1 - 0.25/0.75) = 1/3, the same factor: 31/102
    assert without("P4") == float(Fraction(31, 102)), without("P4")
    return "without P3 %r, without P4 %r" % (without("P3"), without("P4"))


def case_honesty(job, tmp):
    """The honesty term on its own (no geometry): report.json read as one named file, A's points, the factor."""
    T = {"P1": True, "P2": True, "P3": False, "P4": True}
    folder = os.path.join(tmp, "hon")
    os.makedirs(folder)
    rep = os.path.join(folder, G.JOB_REPORT)

    def put(obj, raw=None):
        with open(rep, "w") as f:
            f.write(raw if raw is not None else json.dumps(obj))

    def fac(**kw):
        rec, f = G.job_honesty(folder, dict(T, **kw))
        return rec, f
    # absent: every part not_tested, 0.5 each, h = 1/2, factor (0.75 + 0.05) / 0.85 = 16/17
    rec, f = fac()
    assert rec["report"] == "absent" and f == Fraction(16, 17) and set(rec["claims"].values()) == {"not_tested"}, rec
    # truthful: pass, pass, fail, pass on truths T: 1, 1, 1, 1: h = 1, factor 1
    put({"parts": {"P1": "pass", "P2": "pass", "P3": "fail", "P4": "pass"}})
    rec, f = fac()
    assert f == 1 and rec["honesty_exact"] == "1", rec
    # P3 claimed pass while it fails: 1, 1, -2, 1: h = 1/4, factor 0.775 / 0.85 = 31/34
    put({"parts": {"P1": "pass", "P2": "pass", "P3": "pass", "P4": "pass"}})
    assert fac()[1] == Fraction(31, 34)
    # P1 claimed fail while it passes: 0.5, 1, 1, 1 (P3 fail is true): h = 7/8, factor (0.75 + 0.0875) / 0.85 = 67/68
    put({"parts": {"P1": "fail", "P2": "pass", "P3": "fail", "P4": "pass"}})
    assert fac()[1] == Fraction(67, 68)
    # every part claimed pass, two fail: 1, -2, -2, 1: mean -1/2, h = max(0, -1/2) = 0, factor 0.75/0.85 = 15/17
    put({"parts": {"P1": "pass", "P2": "pass", "P3": "pass", "P4": "pass"}})
    assert fac(P2=False)[1] == Fraction(15, 17)
    # a part left out counts as not_tested: P1 pass, the rest absent: 1, 0.5, 0.5, 0.5: h = 5/8
    put({"parts": {"P1": "pass"}})
    rec, f = fac()
    assert f == (Fraction(3, 4) + Fraction(1, 10) * Fraction(5, 8)) / Fraction(17, 20) and rec["left_out"] == ["P2", "P3", "P4"], rec
    # invalid in each way: every part not_tested, factor 16/17
    C = G._a_constants()
    for obj, raw in (({"parts": {"P1": "passed"}}, None), ({"parts": {"P9": "pass"}}, None), ([1], None),
                     ({"claims": {}}, None), (None, "{not json"), (None, " " * (C.REPORT_MAX_BYTES + 1))):
        put(obj, raw)
        rec, f = fac()
        assert rec["report"] == "invalid" and f == Fraction(16, 17), (obj, raw and raw[:20], rec)
    # a symbolic link is not read
    os.remove(rep)
    real = os.path.join(tmp, "elsewhere.json")
    with open(real, "w") as f_:
        json.dump({"parts": {"P1": "pass", "P2": "pass", "P3": "fail", "P4": "pass"}}, f_)
    os.symlink(real, rep)
    rec, f = fac()
    assert rec["report"] == "invalid" and f == Fraction(16, 17), rec
    return "absent 16/17, truthful 1, false pass 31/34, false fail 67/68, floor at 0 15/17, partial, invalid x6, link"


# ---------------- full gradings ----------------
def _edit(folder, name, fn):
    p = os.path.join(folder, name)
    with open(p) as f:
        doc = json.load(f)
    fn(doc)
    with open(p, "w") as f:
        json.dump(doc, f)


def _different_fixed(folder):
    shutil.copyfile(os.path.join(folder, "parts", "bridge.step"), os.path.join(folder, "parts", "bridge_alt.step"))
    _edit(folder, G.JOB_VARIANT, lambda doc: doc.update(fixed=["bridge_alt" if n == "bridge" else n for n in doc["fixed"]]))


def _full(job, tmp, name, change):
    folder = os.path.join(tmp, name)
    shutil.copytree(job, folder)
    change(folder)
    return run_grader(folder, tmp)


def _summary(d, sec):
    return "reward %r (%s), s %s, %.0f s" % (d["reward"], d["reward_exact"], {k: p["s"] for k, p in d["parts"].items()}, sec)


def case_b(job, tmp):
    d, text, sec = _full(job, tmp, "gold", lambda f: None)
    assert d["reward"] == 1.0 and text.strip() == "1.000000", _summary(d, sec)
    assert all(part_ok(d, pid) for pid in d["parts"])
    return _summary(d, sec)


def case_c(job, tmp):
    d, text, sec = _full(job, tmp, "no_variant", lambda f: os.remove(os.path.join(f, G.JOB_VARIANT)))
    p3 = d["parts"]["P3"]
    assert not p3["gates"]["files"] and p3["s"] == 0.0, p3["gates"]
    assert all(part_ok(d, pid) for pid in ("P1", "P2", "P4")), _summary(d, sec)
    assert d["reward"] == without("P3") and d["reward_exact"] == "31/85", _summary(d, sec)
    return _summary(d, sec)


def case_d(job, tmp):
    d, text, sec = _full(job, tmp, "other_frame", _different_fixed)
    p3 = d["parts"]["P3"]
    assert p3["gates"] == {"files": True, "assembled": True, "day_declared": True, "same_frame": False}, p3["gates"]
    assert all(p3["checks"].values()) and p3["s"] == 0.0
    assert all(part_ok(d, pid) for pid in ("P1", "P2", "P4")), _summary(d, sec)
    assert d["reward"] == without("P3"), _summary(d, sec)
    return _summary(d, sec) + "; P3 frame details: only_in_variant %s" % p3["details"]["same_frame"]["only_in_variant"]


def case_e(job, tmp):
    d, text, sec = _full(job, tmp, "no_assembly", lambda f: os.remove(os.path.join(f, G.JOB_ASSEMBLY)))
    p4 = d["parts"]["P4"]
    assert p4["gates"] == {"files": True, "plan": False} and p4["s"] == 0.0, p4["gates"]
    assert all(part_ok(d, pid) for pid in ("P1", "P2", "P3")), _summary(d, sec)
    assert d["reward"] == without("P4") and d["reward_exact"] == "31/102", _summary(d, sec)
    return _summary(d, sec) + "; P4 plan: %s" % p4["details"]["plan"]


def case_f(job, tmp):
    d, text, sec = _full(job, tmp, "no_movement", lambda f: os.remove(os.path.join(f, G.JOB_MOVEMENT)))
    for pid in ("P1", "P2", "P4"):
        assert not d["parts"][pid]["gates"]["files"] and d["parts"][pid]["s"] == 0.0, pid
    p3 = d["parts"]["P3"]
    assert p3["gates"] == {"files": True, "assembled": True, "day_declared": True, "same_frame": False}, p3["gates"]
    assert all(p3["checks"].values()), p3["checks"]      # still graded: every check ran and passed
    assert "movement.json not found" in p3["details"]["same_frame"]["error"]
    assert d["reward"] == 0.0 and text.strip() == "0.000000"
    return _summary(d, sec) + "; P3 checks all ran and passed, same_frame: %s" % p3["details"]["same_frame"]["error"]


def case_barrel_field(job, tmp):
    """The catalogue barrel (b/thin-cat): each movement file names its barrel under "barrel" (required in one-job
    mode); the movement turns that barrel's own solid; a missing or unknown part no. is a format error (C1); the variant
    naming another barrel than movement.json fails its files gate with a plain message."""
    from geometry import watch as W
    from geometry.core import FormatError
    m = W.load_movement(job, cache=CACHE, materials=True)
    assert m.barrel_id in W.BARREL_IDS and m.mobiles["barrel"]["solid"] is W.barrel(m.barrel_id), m.barrel_id
    folder = os.path.join(tmp, "barrel_field")
    shutil.copytree(job, folder)
    msgs = {}
    for label, edit in (("missing", lambda d: d.pop("barrel")), ("unknown", lambda d: d.update(barrel="BR-096-20")),
                        ("not a string", lambda d: d.update(barrel=96))):
        _edit(folder, G.JOB_MOVEMENT, edit)
        try:
            W.load_movement(folder, cache=CACHE, materials=True)
            raise AssertionError("%s barrel key loaded" % label)
        except FormatError as e:
            msgs[label] = str(e)
            assert "'barrel' must be the part no." in str(e) and "DS-W01" in str(e), e
        _edit(folder, G.JOB_MOVEMENT, lambda d: d.update(barrel=m.barrel_id))
    W.load_movement(folder, cache=CACHE)            # stage mode and tools: the key may be left out (default barrel)
    other = [b for b in W.BARREL_IDS if b != m.barrel_id][0]
    _edit(folder, G.JOB_VARIANT, lambda d: d.update(barrel=other))
    v = W.load_movement(folder, G.JOB_VARIANT, cache=CACHE, materials=True)
    assert v.barrel_id == other and v.mobiles["barrel"]["solid"] is W.barrel(other)
    zb = W.barrel_z(other)["arbor"]
    bb = v.mobiles["barrel"]["solid"].bounding_box()
    assert abs(bb[2] - zb[0]) < 1e-3 and abs(bb[5] - zb[1]) < 1e-3, (bb, zb)
    ok, info = G._run(lambda: (G.job_same_barrel(folder, G.JOB_VARIANT, v) or True, {}))
    assert not ok and "both builds use the same barrel" in info["error"], info
    ok2, _ = G._run(lambda: (G.job_same_barrel(folder, G.JOB_VARIANT, m) or True, {}))
    assert ok2
    return "%s; missing: %r; variant on %s: %r" % (m.barrel_id, msgs["missing"], other, info["error"])


QUICK = [("a", case_a), ("barrel_field", case_barrel_field), ("frame_gate", case_frame_gate), ("day_gate", case_day_gate), ("cache", case_cache), ("deadline", case_deadline),
         ("reward_formula", case_reward_formula), ("keyless_format", case_keyless_format), ("friction_on", case_friction_on),
         ("keyless_assembly", case_keyless_assembly), ("keyless_switch", case_keyless_switch),
         ("keyless_engine", case_keyless_engine), ("keyless_phases", case_keyless_phases),
         ("keyless_minute", case_keyless_minute), ("honesty", case_honesty)]
SLOW = [("b", case_b), ("c", case_c), ("d", case_d), ("e", case_e), ("f", case_f)]


def main(argv):
    opts = dict(zip(argv, argv[1:]))
    only = set(opts["--only"].split(",")) if "--only" in opts else None
    cases = QUICK + (SLOW if "--slow" in argv else [])
    cases = [c for c in cases if only is None or c[0] in only]
    tmp = tempfile.mkdtemp(prefix="job_grader_")
    try:
        if "--job" in opts:
            job = os.path.abspath(opts["--job"])
        elif "--base" in opts:
            job = os.path.join(tmp, "job")
            print("job folder:", json.dumps(make_job_folder.make(os.path.abspath(opts["--base"]), job)))
        else:
            job = os.path.join(tmp, "job")
            subprocess.run([sys.executable, os.path.join(ROOT, "solution", "reference_watch.py"), job, "--job"], check=True,
                           stdout=subprocess.DEVNULL)
            print("job folder:", job)
        failed = 0
        for name, fn in cases:
            sub = os.path.join(tmp, "case_" + name)
            os.makedirs(sub)
            try:
                print("PASS %s: %s" % (name, fn(job, sub)), flush=True)
            except AssertionError as e:
                failed += 1
                print("FAIL %s: %s" % (name, e), flush=True)
            shutil.rmtree(sub, ignore_errors=True)
        print("%d of %d passed" % (len(cases) - failed, len(cases)))
        return 1 if failed else 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
