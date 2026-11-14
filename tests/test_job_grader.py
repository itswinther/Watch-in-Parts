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
  b  the reference job folder: 1.0
  c  variant_6h.json missing: P3's gates fail, the others pass, reward = 0.5 x (1 - 0.15/0.75)
  d  the variant names a different fixed list (bridge_alt, a byte copy of bridge): P3's same_frame gate (C4) fails
  e  assembly.json missing: P4 scores 0, the others pass, reward = 0.5 x (1 - 0.25/0.75)
  f  movement.json missing, variant present: P1, P2 and P4 fail their gates; P3 is still graded, all its checks
     run, and its same_frame gate fails because there is no movement.json to compare with, so P3 scores 0 too
     and the reward is 0 (decided: the variant is defined against movement.json; without it there is no job)
Quick cases for crown winding (Part 5's format, geometry/keyless_job.py; graded only when KEYLESS_IN_JOB):
  keyless_format  a `keyless` section loads and its parts are read; a part used twice (keyless and a mobile, keyless
                  and fixed, twice in keyless) is a format error; the section's own rules; no section: as before
  friction_on     a friction_on mobile turns at its carrier's speed; bad carriers are format errors; P5's split
  keyless_switch  the P5 row follows KEYLESS_IN_JOB; the scaled table agrees with A's files"""
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


def without(*pids):
    """The reward when every check of every part passes except that the parts pids score 0."""
    return float(Fraction(1, 2) * (1 - sum(W_[p] for p in pids) / TOTAL))


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


def case_keyless_switch(job, tmp):
    """KEYLESS_IN_JOB is False on this branch: no P5 row; the scaled table agrees with A's files."""
    from geometry import keyless_job as KJ
    errs = KJ.check_table()
    assert not errs, errs
    rows = [p[0] for p in G.JOB_PARTS]
    assert rows == (["P1", "P2", "P3", "P4", "P5"] if KJ.KEYLESS_IN_JOB else ["P1", "P2", "P3", "P4"]), rows
    return "KEYLESS_IN_JOB %s, parts %s, scaled %s" % (KJ.KEYLESS_IN_JOB, rows, KJ.scaled())


def case_reward_formula(job, tmp):
    assert without("P3") == 0.5 * (1 - 0.15 / 0.75) == 0.4
    assert abs(without("P4") - 0.5 * (1 - 0.25 / 0.75)) < 1e-15
    return "without P3 %r, without P4 %r" % (without("P3"), without("P4"))


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
    assert d["reward"] == without("P3") == 0.4 and d["reward_exact"] == "2/5", _summary(d, sec)
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
    assert d["reward"] == without("P4") and d["reward_exact"] == "1/3", _summary(d, sec)
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


QUICK = [("a", case_a), ("frame_gate", case_frame_gate), ("day_gate", case_day_gate), ("cache", case_cache), ("deadline", case_deadline),
         ("reward_formula", case_reward_formula), ("keyless_format", case_keyless_format), ("friction_on", case_friction_on),
         ("keyless_switch", case_keyless_switch)]
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
