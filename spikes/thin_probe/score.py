"""Score one thinness-probe run afterwards (spikes/thin_probe/BRIEF_DRAFT.md section 5). The one-job grader now
applies the same score itself (tests/grade_watch.py job_thickness); this script rescores runs graded before that.
    python3 spikes/thin_probe/score.py DETAILS.json DELIVERY_DIR
DETAILS.json: the details file the grader wrote for this delivery (tests/grade_watch.py DELIVERY --details D).
DELIVERY_DIR: the delivery folder (movement.json, variant_6h.json, parts/*.step, report.json).

H is measured here from the delivered STEP parts and the supplied barrel (geometry/watch.py load_movement, as the
grader loads them: barrel included, the same meshing): for movement.json and for variant_6h.json, the highest
point minus the lowest point along z of every part of the movement and of the barrel in the assembled positions;
the taller of the two counts. A movement file that does not load gives no thickness score (s = 0).
    x = (H - H0) / (CASE_HEIGHT - H0), clamped to 0..1;  s = (1 - x) ** THIN_SCORE_EXPONENT
with H0 = geometry/watch.py thin_full_score_height(): the height the house design reaches (THIN_REFERENCE_MM), or the
stated target THIN_TARGET_MM while THIN_TARGET_STATED is on (WATCH_THIN_TARGET_STATED=1, to rescore runs of the
stated-target brief). A movement at H0 or thinner has s = 1. The score itself is geometry/watch.py thin_score().
    probe reward = (THIN_SCORE_SHARE x share + THIN_SCORE_SHARE x [all pass] x s) x statement factor
with share and [all pass] taken from the details file: the grader's parts reward is THIN_SCORE_SHARE x share +
THIN_SCORE_SHARE x [all pass], so share term = parts_reward - THIN_SCORE_SHARE x [all pass]. The constants are
geometry/watch.py's. Also printed: the size check's z extent from the
details file (P1, P3) as a cross-check, and the agent's own claim, report.json height_mm, if present."""
import json
import math
import os
import sys
from fractions import Fraction

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.abspath(ROOT))
from geometry import watch as W        # noqa: E402

BUILDS = ("movement.json", "variant_6h.json")


def height(folder, name):
    """(H in mm, None) for one movement file, or (None, error text) if it does not load."""
    try:
        m = W.load_movement(folder, name, materials=True)
        e = m.extent()
        h = e["z_max"] - e["z_min"]
        if not math.isfinite(h):
            return None, "non-finite height"
        return h, None
    except Exception as ex:          # a format error, a missing file, or anything else: no thickness score
        return None, "%s: %s" % (type(ex).__name__, ex)


def score(H):
    return W.thin_score(H)


def reward(parts_reward, all_pass, s, factor):
    """The probe reward as an exact Fraction: (share term + THIN_SCORE_SHARE x [all pass] x s) x statement factor,
    with share term = parts_reward - THIN_SCORE_SHARE x [all pass] (the grader's parts reward without its
    all-pass half)."""
    half = W.THIN_SCORE_SHARE
    share_term = Fraction(parts_reward) - (half if all_pass else 0)
    return (share_term + (half * Fraction(s) if all_pass else 0)) * Fraction(factor)


def claimed_height(folder):
    p = os.path.join(folder, "report.json")
    if os.path.islink(p) or not os.path.isfile(p):
        return None
    try:
        if os.path.getsize(p) > 1_000_000:
            return "report.json too large to read"
        doc = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError) as ex:
        return "report.json not readable: %s" % ex
    if not isinstance(doc, dict) or "height_mm" not in doc:
        return None
    return doc["height_mm"]


def details_size(d, pid):
    try:
        s = d["parts"][pid]["details"]["size"]
        return s["z_max"] - s["z_min"]
    except (KeyError, TypeError):
        return None


def main(argv):
    if len(argv) != 2:
        print(__doc__.split("\n")[1].strip())
        return 2
    with open(argv[0], encoding="utf-8") as f:
        d = json.load(f)
    folder = os.path.abspath(argv[1])
    hs = {}
    for name in BUILDS:
        h, err = height(folder, name)
        hs[name] = h
        print("%-16s H %s" % (name, "%.4f mm" % h if h is not None else "none (%s)" % err))
    H = max(hs.values()) if all(v is not None for v in hs.values()) else None
    x, s = score(H)
    A = bool(d.get("all_pass"))
    # A details file from a grader that applies the thickness score itself (tests/grade_watch.py job_thickness) has
    # parts_reward_without_thickness: the parts reward with the whole all-pass half, as older graders wrote it.
    if "parts_reward_without_thickness_exact" in d:
        pr = Fraction(d["parts_reward_without_thickness_exact"])
    elif "parts_reward_exact" in d:
        pr = Fraction(d["parts_reward_exact"])
    else:
        pr = Fraction(d.get("parts_reward", 0.0))
    hon = d.get("honesty") or {}
    factor = Fraction(hon["factor_exact"]) if "factor_exact" in hon else Fraction(hon.get("factor", 0.0))
    share_term = pr - (W.THIN_SCORE_SHARE if A else 0)
    probe = reward(pr, A, s, factor)
    print("details size z extent  P1 %s  P3 %s" % tuple(
        "%.4f" % v if v is not None else "none" for v in (details_size(d, "P1"), details_size(d, "P3"))))
    print("H %s  %s %s  case height %s  x %.4f  s %.6f" % (
        "%.4f" % H if H is not None else "none", "target" if W.THIN_TARGET_STATED else "house design",
        W.thin_full_score_height(), W.CASE_HEIGHT, x, s))
    print("all_pass %s  parts_reward %.6f  share term %.6f  statement factor %.6f" % (
        A, float(pr), float(share_term), float(factor)))
    print("grader reward %s  probe reward %.6f" % (d.get("reward"), float(probe)))
    c = claimed_height(folder)
    print("claimed height_mm %s" % ("not given" if c is None else c))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
