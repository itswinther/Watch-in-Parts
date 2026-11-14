"""Reference set for Moving Day, instance flat-1.   python tests/test_anchors_md.py
One script that builds each plan, grades it and asserts the score:
gold 1.00, do-nothing 0.00, the likely shortcuts and plausible partial plans lower.
Exit code 1 if any score is off."""
import json
import os
import sys
import tempfile

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "solution"))
import numpy as np
from geometry import md
import reference_md as ref

INST = md.flat_one()
GOLD = ref.build(INST)
TOTAL = sum(INST.weight(n) for n in INST.pieces)


def s(*delivered):
    return md.score(INST, list(delivered))[0]


def plan(order=None, **override):
    paths = {k: [np.asarray(T) for T in v] for k, v in GOLD["paths"].items()}
    paths.update(override)
    return {"order": list(GOLD["order"] if order is None else order), "paths": paths}


def dump(d, doc):
    with open(os.path.join(d, "plan.json"), "w") as f:
        json.dump({"order": doc["order"], "paths": {k: [np.asarray(T).tolist() for T in v] for k, v in doc["paths"].items()}}, f)


def shifted(name, d):
    """The gold path moved sideways by d, eased back to the true path over its last 60 poses."""
    P = [np.array(T) for T in GOLD["paths"][name]]
    n = len(P)
    for i, T in enumerate(P):
        T[:3, 3] += d * min(1.0, (n - 1 - i) / 60.0)
    return P


def teleport(name):
    start = md.trans((-300, 600, 10)) @ np.eye(4)
    return [start, INST.final(name)]


def straight(name, n=400):
    F = INST.final(name)
    start = F.copy()
    start[:3, 3] = (-250, 640, 5)
    return [start + (F - start) * i / n for i in range(n + 1)]


def a_gold(d):
    dump(d, plan())


def a_nothing(d):
    pass


def a_not_json(d):
    with open(os.path.join(d, "plan.json"), "w") as f:
        f.write('{"order": ["sofa"], "paths": {"sofa": [[[1, 0, 0')


def a_oversized(d):
    with open(os.path.join(d, "plan.json"), "w") as f:
        f.write('{"order": [], "paths": {}, "pad": "' + "x" * (33 * 1024 * 1024) + '"}')


def a_final_only(d):
    dump(d, plan(**{n: teleport(n) for n in INST.pieces}))


def a_straight_lines(d):
    dump(d, plan(**{n: straight(n) for n in INST.pieces}))


def a_listed_order(d):
    dump(d, plan(order=INST.listed))


def a_easy_only(d):
    dump(d, plan(order=["bookcase", "chest"]))


def a_no_sofa(d):
    dump(d, plan(order=["wardrobe", "chest", "bookcase"]))


def a_sofa_lying(d):
    """Everything right except the sofa, which is dragged round the corner without being stood up."""
    dump(d, plan(sofa=straight("sofa")))


def a_wardrobe_wrong_tip(d):
    """The wardrobe is carried in correctly but stood up about its 60 edge, which needs 239.6 under a 238 ceiling."""
    F = INST.final("wardrobe")
    body = INST.piece("wardrobe")
    down = ref.swing(body, F, "x", (0, 210.0, 0), -90.0)      # lies down along +y instead
    P = [F] + down
    T = P[-1]
    out = ref.lerp_move(T, (0, 0, 0))
    dump(d, plan(wardrobe=(P + out)[::-1]))


def a_start_outside(d):
    P = [np.array(T) for T in GOLD["paths"]["chest"]]
    dump(d, plan(chest=P[20:]))


def a_nan(d):
    P = [np.array(T) for T in GOLD["paths"]["chest"]]
    P[5] = np.full((4, 4), np.nan)
    dump(d, plan(chest=P))


def a_nonrigid(d):
    P = [np.array(T) for T in GOLD["paths"]["bookcase"]]
    P[7] = P[7] @ np.diag([1.02, 1, 1, 1])
    dump(d, plan(bookcase=P))


def a_twice_unknown(d):
    dump(d, plan(order=["sofa", "piano", "bookcase", "sofa", "wardrobe", "chest"]))


def a_ride_tolerance(d):
    """Bookcase path pushed 0.0002 into the door frame: 0.8 cm3 of overlap, inside the 1.0 allowed."""
    dump(d, plan(bookcase=shifted("bookcase", np.array([0, -3.0002, 0.0]))))


def a_through_frame(d):
    """Bookcase path pushed 0.5 into the door frame."""
    dump(d, plan(bookcase=shifted("bookcase", np.array([0, -3.5, 0.0]))))


ANCHORS = [
    ("gold: reference plan", a_gold, 1.0),
    ("do nothing", a_nothing, 0.0),
    ("not valid JSON", a_not_json, 0.0),
    ("oversized file", a_oversized, 0.0),
    ("shortcut: staging then final pose", a_final_only, 0.0),
    ("shortcut: straight lines through walls", a_straight_lines, 0.0),
    ("gold paths in the listed order", a_listed_order, s("bookcase", "chest")),
    ("easy pieces only", a_easy_only, s("bookcase", "chest")),
    ("partial: everything but the sofa", a_no_sofa, s("wardrobe", "chest", "bookcase")),
    ("partial: sofa not stood on end", a_sofa_lying, s("wardrobe", "chest", "bookcase")),
    ("partial: wardrobe tipped the wrong way", a_wardrobe_wrong_tip, s("sofa", "bookcase", "chest")),
    ("chest starts outside staging", a_start_outside, s("sofa", "bookcase", "wardrobe")),
    ("NaN in the chest path", a_nan, s("sofa", "bookcase", "wardrobe")),
    ("non-rigid pose in the bookcase path", a_nonrigid, s("sofa", "wardrobe", "chest")),
    ("a name twice and an unknown name", a_twice_unknown, 1.0),
    ("rides the volume tolerance", a_ride_tolerance, 1.0),
    ("0.5 into the door frame", a_through_frame, s("sofa", "wardrobe", "chest")),
]


def main():
    bad = 0
    for name, fn, want in ANCHORS:
        with tempfile.TemporaryDirectory() as d:
            fn(d)
            r = md.grade(os.path.join(d, "plan.json"))
        ok = abs(r["reward"] - want) < 1e-6
        bad += not ok
        print("%-4s %-40s S=%.4f expected %.4f  delivered: %s"
              % ("ok" if ok else "OFF", name, r["reward"], want, ",".join(r["delivered"]) or "-"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
