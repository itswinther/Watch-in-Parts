"""Tests for the thickness term of the one-job reward (tests/grade_watch.py job_reward, job_thickness). The score
itself is tested by tests/test_thin_score.py.
    python3 tests/test_thin_reward.py [--delivery /abs/DELIVERY [--details /abs/DETAILS.json]]
Run from the repository root; seconds (no grading run). Cases:
  combine      job_reward = (1/2 num/den + 1/2 [all pass] s) x factor: unchanged (the old rule) when s = 1, so a
               delivery at or below the house design's height keeps its reward; a taller all-pass delivery gets
               1/2 share + 1/2 s; without everything passing there is no thickness term whatever s is
  measure      job_thickness takes the taller of movement.json and variant_6h.json (stubbed loader), s = 1 at
               H <= H0 and thin_score(H) above it
  fail closed  a delivery that does not load, a loader that raises and a non-finite height give s = 0 and an error
  reference    (only with --delivery) the delivery measures H <= H0, s = 1; with --details too, the grader's details
               file says s 1, reward 1 and parts_reward_without_thickness 1"""
import importlib.util
import os
import shutil
import sys
import tempfile
from fractions import Fraction

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ROOT)
from geometry import watch as W        # noqa: E402


def grader():
    spec = importlib.util.spec_from_file_location("grade_watch_t", os.path.join(ROOT, "tests", "grade_watch.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


G = grader()


def case_combine():
    R = G.job_reward
    half = W.THIN_SCORE_SHARE
    assert half == Fraction(1, 2)
    num, den = Fraction(3, 4), Fraction(3, 4)               # every part scores 1
    _, s_ref = W.thin_score(W.thin_full_score_height())
    assert s_ref == 1.0
    assert R(num, den, True, s_ref, 1) == 1                 # the reference: exactly 1
    assert R(num, den, True, 1.0, Fraction(16, 17)) == Fraction(16, 17)
    for H in (W.THIN_REFERENCE_MM - 0.3, W.THIN_REFERENCE_MM):
        assert R(num, den, True, W.thin_score(H)[1], 1) == 1, H
    # the old rule is s = 1
    for n, d, a in ((Fraction(1, 5), Fraction(3, 4), False), (Fraction(3, 4), Fraction(3, 4), True)):
        old = Fraction(1, 2) * n / d + (Fraction(1, 2) if a else 0)
        assert R(n, d, a, 1, 1) == old
    # taller and all pass: 1/2 share + 1/2 s
    H = W.THIN_REFERENCE_MM + 1.0
    x, s = W.thin_score(H)
    assert 0 < s < 1
    assert R(num, den, True, s, 1) == half + half * Fraction(s)
    assert R(num, den, True, s, Fraction(31, 34)) == (half + half * Fraction(s)) * Fraction(31, 34)
    assert R(num, den, True, 0.0, 1) == half
    # not everything passes: no thickness term
    for s2 in (0.0, 0.3, 1.0):
        assert R(Fraction(3, 10), den, False, s2, 1) == Fraction(1, 5), s2
    return "s 1 keeps the old reward (reference 1); H0 + 1 mm all pass: %.6f; not all pass: no term" % float(
        R(num, den, True, s, 1))


class _Stub:
    def __init__(self, zlo, zhi):
        self.e = {"radius": 1.0, "z_min": zlo, "z_max": zhi}

    def extent(self):
        return self.e


def _with_loader(heights, folder="/nonexistent"):
    """job_thickness with W.load_movement replaced: heights maps the file name to (z_min, z_max) or an exception."""
    real = W.load_movement

    def fake(folder, name, cache=None, materials=False):
        v = heights[name]
        if isinstance(v, Exception):
            raise v
        return _Stub(*v)
    W.load_movement = fake
    try:
        return G.job_thickness(folder)
    finally:
        W.load_movement = real


def case_measure():
    H0 = W.thin_full_score_height()
    t = _with_loader({"movement.json": (-1.0, H0 - 1.2), "variant_6h.json": (-1.0, H0 - 1.0)})
    assert t["H_mm_taller"] == H0 and t["s"] == 1.0 and t["s_exact"] == 1 and t["error"] is None, t
    assert t["h0_mm"] == H0 and t["exponent"] == W.THIN_SCORE_EXPONENT
    t = _with_loader({"movement.json": (-0.5, H0 + 0.5), "variant_6h.json": (-0.5, H0 - 1.0)})
    assert abs(t["H_mm_taller"] - (H0 + 1.0)) < 1e-12, t       # the taller build counts (here movement.json)
    x, s = W.thin_score(t["H_mm_taller"])
    assert t["s"] == s and t["x"] == x and t["s_exact"] == Fraction(s) and 0 < s < 1, t
    return "taller build counts; H0 + 1 mm: x %.4f, s %.4f" % (x, s)


def case_fail_closed():
    tmp = tempfile.mkdtemp(prefix="thin_reward_")
    try:
        t = G.job_thickness(tmp)                            # empty folder: neither build loads
        assert t["s"] == 0.0 and t["s_exact"] == 0 and t["H_mm_taller"] is None and t["error"], t
        assert t["H_mm"] == {"movement.json": None, "variant_6h.json": None}, t
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    t = _with_loader({"movement.json": (0.0, 3.0), "variant_6h.json": ValueError("broken")})
    assert t["s"] == 0.0 and t["H_mm_taller"] is None and "broken" in t["error"], t
    t = _with_loader({"movement.json": (0.0, float("nan")), "variant_6h.json": (0.0, 3.0)})
    assert t["s"] == 0.0 and t["H_mm_taller"] is None and "non-finite" in t["error"], t
    assert G.job_reward(Fraction(3, 4), Fraction(3, 4), True, t["s_exact"], 1) == Fraction(1, 2)
    return "unloadable, raising and non-finite builds: s 0, error recorded, all-pass reward 1/2"


def case_reference(delivery, details):
    t = G.job_thickness(delivery)
    assert t["error"] is None and t["H_mm_taller"] is not None, t
    assert t["H_mm_taller"] <= W.thin_full_score_height() and t["s"] == 1.0, t
    out = "H %.4f (%s), s 1" % (t["H_mm_taller"], ", ".join("%s %.4f" % kv for kv in t["H_mm"].items()))
    if details:
        import json
        d = json.load(open(details, encoding="utf-8"))
        assert d["thickness"]["s"] == 1.0 and d["thickness"]["error"] is None, d["thickness"]
        assert d["reward_exact"] == "1" and d["parts_reward_exact"] == "1", (d["reward_exact"], d["parts_reward_exact"])
        assert d["parts_reward_without_thickness_exact"] == "1"
        assert abs(d["thickness"]["H_mm_taller"] - t["H_mm_taller"]) < 1e-9
        out += "; details: reward 1, parts reward 1, without thickness 1"
    return out


def main(argv):
    cases = [("combine", case_combine), ("measure", case_measure), ("fail closed", case_fail_closed)]
    if "--delivery" in argv:
        dl = os.path.abspath(argv[argv.index("--delivery") + 1])
        dt = os.path.abspath(argv[argv.index("--details") + 1]) if "--details" in argv else None
        cases.append(("reference", lambda: case_reference(dl, dt)))
    failed = 0
    for name, fn in cases:
        try:
            print("PASS %s: %s" % (name, fn()), flush=True)
        except AssertionError as e:
            failed += 1
            print("FAIL %s: %s" % (name, e), flush=True)
    print("%d of %d passed" % (len(cases) - failed, len(cases)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
