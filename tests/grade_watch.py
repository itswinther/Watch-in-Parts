"""Grader for the mechanical watch task. Run from this directory as:
    python -I grade_watch.py /abs/submission_folder [--reward FILE] [--details FILE]
The folder holds movement.json and parts/<name>.stl; only files named in movement.json are opened.
Never runs submitted code. Writes reward 0 first."""
import json
import os
import signal
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (HERE, os.path.dirname(HERE)):
    if os.path.isdir(os.path.join(cand, "geometry")):
        sys.path.insert(0, cand)
        break

# What a watch does. Clockwise turns per hour. Not stated to the agent.
HAND_SPEED = {"hour": Fraction(1, 12), "minute": Fraction(1), "seconds": Fraction(60)}
WEIGHTS = {"spin": 1, "held": 2, "train": 3, "clear": 1, "minute": 2, "hour": 2, "seconds": 2,
           "coaxial": 1, "hands": 1, "size": 1}
GATES = ("files", "assembled")
TIMEOUT_S = 600


class _Timeout(Exception):
    pass


def _run(fn):
    def handler(signum, frame):
        raise _Timeout()
    old = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, TIMEOUT_S)
    try:
        ok, info = fn()
        return bool(ok), info
    except _Timeout:
        return False, {"error": "timeout"}
    except Exception as e:      # noqa: a failed check, never a crash
        return False, {"error": "%s: %s" % (type(e).__name__, e)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def grade(folder):
    import math
    from geometry import watch as W
    from geometry.core import ivol
    gates = {g: False for g in GATES}
    checks = {k: False for k in WEIGHTS}
    details = {}
    st = {}

    def result():
        G = all(gates.values())
        p = sum(w for k, w in WEIGHTS.items() if checks[k]) / sum(WEIGHTS.values())
        S = (0.5 * p * p + 0.5 * (1.0 if all(checks.values()) else 0.0)) if G else 0.0
        return {"reward": S, "p": p, "gates": gates, "checks": checks, "details": details}

    def load():
        st["m"] = W.load_movement(folder)
        return True, {}
    gates["files"], details["files"] = _run(load)
    if not gates["files"]:
        return result()
    m = st["m"]
    names = list(m.mobiles)

    def assembled():
        worst, pair = 0.0, None
        solids = [("fixed", m.fixed)] + [(n, m.mobiles[n]["solid"]) for n in names]
        for i in range(len(solids)):
            for j in range(i + 1, len(solids)):
                v = ivol(solids[i][1], solids[j][1])
                if v > worst:
                    worst, pair = v, solids[i][0] + "/" + solids[j][0]
        return worst <= W.VOL_TOL, {"worst_volume": worst, "pair": pair}
    gates["assembled"], details["assembled"] = _run(assembled)

    speeds, conflicts = m.speeds()

    def spin():
        r = {n: m.spin(n) for n in names}
        return all(v["worst_volume"] <= W.VOL_TOL for v in r.values()), r

    def held():
        r = {n: m.held(n) for n in names}
        return all(v > W.VOL_TOL for d in r.values() for v in d.values()), r

    def train():
        r = {"conflicts": conflicts, "meshes": []}
        ok = not conflicts and bool(m.meshes) and all(m.hands[h][0] in speeds for h in HAND_SPEED)
        for a, ta, b, tb in m.meshes:
            x = m.mesh_run(a, ta, b, tb)
            x["pair"] = "%s/%s" % (a, b)
            r["meshes"].append(x)
            ok = ok and x["worst_volume"] <= W.VOL_TOL and x["largest_gap"] <= W.ENGAGE_GAP and x["smallest_drive_overlap"] > W.VOL_TOL
        return ok, r

    def clear():
        meshing = {frozenset((a, b)) for a, _, b, _ in m.meshes}
        worst, pair = 0.0, None
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                if frozenset((names[i], names[j])) in meshing:
                    continue
                x = m.clear_run(names[i], names[j], speeds.get(names[i], 0), speeds.get(names[j], 0))
                if x["worst_volume"] > worst:
                    worst, pair = x["worst_volume"], names[i] + "/" + names[j]
        return worst <= W.VOL_TOL, {"worst_volume": worst, "pair": pair}

    def hand(h):
        def fn():
            w = speeds.get(m.hands[h][0])
            return (not conflicts) and w == HAND_SPEED[h], {"clockwise_turns_per_hour": str(w)}
        return fn

    def coaxial():
        a, b = m.mobiles[m.hands["hour"][0]]["axis"], m.mobiles[m.hands["minute"][0]]["axis"]
        d = math.hypot(a[0] - b[0], a[1] - b[1])
        return d <= W.COAX_TOL, {"distance": d}

    def hands():
        r = {h: m.hand_reach(h) for h in HAND_SPEED}
        return all(v >= W.HAND_REACH for v in r.values()), r

    def size():
        e = m.extent()
        return e["radius"] <= W.CASE_RADIUS and e["z_max"] - e["z_min"] <= W.CASE_HEIGHT, e

    table = {"spin": spin, "held": held, "train": train, "clear": clear, "minute": hand("minute"), "hour": hand("hour"),
             "seconds": hand("seconds"), "coaxial": coaxial, "hands": hands, "size": size}
    for k in WEIGHTS:
        checks[k], details[k] = _run(table[k])
    return result()


def main(argv):
    opts = dict(zip(argv, argv[1:]))
    reward_file = opts.get("--reward", "/logs/verifier/reward.txt")
    os.makedirs(os.path.dirname(os.path.abspath(reward_file)), exist_ok=True)
    with open(reward_file, "w") as f:
        f.write("0\n")
    args = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or not argv[i - 1].startswith("--"))]
    if len(args) != 1 or not os.path.isabs(args[0]):
        print("usage: grade_watch.py /abs/submission_folder")
        return 2
    res = grade(args[0])
    if opts.get("--details"):
        with open(opts["--details"], "w") as f:
            json.dump(res, f, indent=1, default=str)
    with open(reward_file, "w") as f:
        f.write("%.6f\n" % res["reward"])
    print(json.dumps({k: res[k] for k in ("reward", "p", "gates", "checks")}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
