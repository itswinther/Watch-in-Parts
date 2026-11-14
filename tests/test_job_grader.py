"""Fixture tests for the one-job grader (tests/grade_watch.py without --stage).
    python3 tests/test_job_grader.py [--slow] [--only a,b,...] [--base /abs/REF_OUT | --job /abs/JOB]
Run from the repository root. Without --slow only the quick cases run (seconds to a minute): the empty
folder through the real grader, and the gates and helpers on their own. --slow adds the full gradings (each
runs the grader once, `python3 -I grade_watch.py` from tests/ in a fresh process, one at a time; a full
delivery takes about 12 minutes on 4 CPUs, all six about an hour).
--base reuses the stage folders solution/reference_watch.py wrote; --job uses a job folder as it is (for when
the reference writes one directly); with neither, the reference is built into a temporary folder (about 40 s).
Cases (the letters of the builder brief):
  a  empty folder: reward 0, every part 0, the reward file says 0
  b  the reference job folder: 1.0
  c  variant_6h.json missing: P3's gates fail, the others pass, reward = 0.5 x (1 - 0.15/0.75)
  d  the variant names a different fixed list (bridge_alt, a byte copy of bridge): P3's same_frame gate (C4) fails
  e  assembly.json missing: P4 scores 0, the others pass, reward = 0.5 x (1 - 0.25/0.75)
  f  movement.json missing, variant present: P1, P2 and P4 fail their gates; P3 is still graded, all its checks
     run, and its same_frame gate fails because there is no movement.json to compare with, so P3 scores 0 too
     and the reward is 0 (decided: the variant is defined against movement.json; without it there is no job)"""
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
         ("reward_formula", case_reward_formula)]
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
        else:
            base = opts.get("--base")
            if not base:
                base = os.path.join(tmp, "ref")
                subprocess.run([sys.executable, os.path.join(ROOT, "solution", "reference_watch.py"), base], check=True,
                               stdout=subprocess.DEVNULL)
            job = os.path.join(tmp, "job")
            print("job folder:", json.dumps(make_job_folder.make(os.path.abspath(base), job)))
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
