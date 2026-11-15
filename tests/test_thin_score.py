"""Tests for the thickness score (geometry/watch.py thin_score, spikes/thin_probe/score.py). The leak guard is tested
by tests/test_thin_leak.py and the agent's documents by tests/test_thin_brief.py.
    python3 tests/test_thin_score.py [--table] [--delivery /abs/DELIVERY --details /abs/DETAILS.json]
Run from the repository root; seconds. Cases:
  score        s = 1 at the house design's height and below it, 0 at the case height and above, 0 for a movement
               that does not load, never rising with H, and equal to the formula from the constants in between
  switch       the stated-target mode scores against THIN_TARGET_MM, the default against THIN_REFERENCE_MM
  reward       the reward is 1/2 share + 1/2 [all pass] x s, times the statement factor; no thickness term unless
               everything passes
  reference    (only with --delivery and --details) the reference delivery scores s = 1 and reward 1.0
--table prints s and the reward of an all-pass delivery over a range of heights, for the exponent in use and for
two alternatives (it changes nothing)."""
import importlib.util
import math
import os
import sys
from fractions import Fraction

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.abspath(ROOT))
from geometry import watch as W        # noqa: E402

TABLE_HEIGHTS = (3.0, 3.35, 3.5, 4.0, 4.5, 5.0, 6.6, 9.0)
TABLE_EXPONENTS = (2, 4, 8)


def score_module():
    spec = importlib.util.spec_from_file_location("thin_probe_score", os.path.join(ROOT, "spikes", "thin_probe", "score.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def case_score():
    R, C, E = W.THIN_REFERENCE_MM, W.CASE_HEIGHT, W.THIN_SCORE_EXPONENT
    assert 0 < R < C
    for h in (R, R - 1e-9, R - 0.5, 0.0):
        assert W.thin_score(h, stated=False) == (0.0, 1.0), h
    for h in (C, C + 1.0, 1e9):
        assert W.thin_score(h, stated=False) == (1.0, 0.0), h
    for h in (None, float("nan"), float("inf")):
        assert W.thin_score(h, stated=False) == (1.0, 0.0), h
    last = 1.0
    for i in range(0, 2001):
        h = R - 1.0 + i * (C - R + 2.0) / 2000
        x, s = W.thin_score(h, stated=False)
        assert 0.0 <= s <= 1.0 and s <= last + 1e-15, (h, s, last)
        last = s
    h = R + 0.1
    x, s = W.thin_score(h, stated=False)
    assert abs(x - 0.1 / (C - R)) < 1e-12 and abs(s - (1 - 0.1 / (C - R)) ** E) < 1e-12
    assert s < 1.0                           # a tenth thicker than the house design already costs score
    assert score_module().score(h) == W.thin_score(h)      # score.py has no formula of its own
    return "s 1 at and below %s, 0 from %s, %.4f a tenth above" % (R, C, s)


def case_switch():
    T, R = W.THIN_TARGET_MM, W.THIN_REFERENCE_MM
    assert W.thin_full_score_height(stated=True) == T and W.thin_full_score_height(stated=False) == R
    assert W.thin_full_score_height() == (T if W.THIN_TARGET_STATED else R)
    assert W.thin_score(T, stated=True) == (0.0, 1.0)
    if T > R:
        assert W.thin_score(T, stated=False)[1] < 1.0      # stopping on the old stated target no longer scores 1
    x, s = W.thin_score(T + 1.0, stated=True)
    assert abs(s - (1 - 1.0 / (W.CASE_HEIGHT - T)) ** W.THIN_SCORE_EXPONENT) < 1e-12
    return "stated: full score at %s; default: full score at %s, s(%s) = %.4f" % (T, R, T, W.thin_score(T, stated=False)[1])


def case_reward():
    S = score_module()
    half = W.THIN_SCORE_SHARE
    assert half == Fraction(1, 2)
    assert S.reward(Fraction(1), True, 1.0, Fraction(1)) == 1
    assert S.reward(Fraction(1), True, 0.0, Fraction(1)) == half
    assert S.reward(Fraction(1), True, 0.5, Fraction(1)) == Fraction(3, 4)
    assert S.reward(Fraction(1), True, 1.0, Fraction(31, 34)) == Fraction(31, 34)
    # not everything passes: the parts reward is 1/2 x share, and thickness adds nothing whatever s is
    assert S.reward(Fraction(2, 5), False, 1.0, Fraction(1)) == Fraction(2, 5)
    assert S.reward(Fraction(2, 5), False, 0.0, Fraction(1)) == Fraction(2, 5)
    return "1/2 share + 1/2 [all pass] x s, times the statement factor"


def case_reference(delivery, details):
    import json
    S = score_module()
    hs = [S.height(delivery, n)[0] for n in S.BUILDS]
    assert all(h is not None for h in hs), hs
    H = max(hs)
    assert H <= W.thin_full_score_height(), "the reference (%.4f) is taller than the full-score height" % H
    d = json.load(open(details, encoding="utf-8"))
    r = S.reward(Fraction(d["parts_reward_exact"]), bool(d["all_pass"]), W.thin_score(H)[1],
                 Fraction(d["honesty"]["factor_exact"]))
    assert d["all_pass"] and r == 1, (d["all_pass"], r)
    return "H %.4f, s 1, reward %s" % (H, r)


def table():
    R, C = W.thin_full_score_height(), W.CASE_HEIGHT
    print("s and reward of a delivery that passes everything (statement factor 1); full score at H <= %s, case %s, "
          "exponent in use %s" % (R, C, W.THIN_SCORE_EXPONENT))
    print("| H (mm) | " + " | ".join("s, exp %d | reward, exp %d" % (e, e) for e in TABLE_EXPONENTS) + " |")
    print("|---|" + "---|---|" * len(TABLE_EXPONENTS))
    S = score_module()
    for h in TABLE_HEIGHTS:
        cells = []
        for e in TABLE_EXPONENTS:
            s = W.thin_score(h, exponent=e)[1]
            cells.append("%.4f | %.4f" % (s, float(S.reward(Fraction(1), True, s, Fraction(1)))))
        print("| %s | %s |" % (h, " | ".join(cells)))


def main(argv):
    if "--table" in argv:
        table()
        return 0
    cases = [("score", case_score), ("switch", case_switch), ("reward", case_reward)]
    if "--delivery" in argv:
        dl, dt = argv[argv.index("--delivery") + 1], argv[argv.index("--details") + 1]
        cases.append(("reference", lambda: case_reference(os.path.abspath(dl), os.path.abspath(dt))))
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
