"""Grader for the mechanical watch task. Run from this directory as:
    python -I grade_watch.py /abs/submission_folder [--stage 1|2|3|4] [--prev /abs/previous_stage_folder]
                             [--reward FILE] [--details FILE] [--skip CHECK,CHECK]
--skip leaves named scored checks out (only for runs made before a check existed); the list is in the output.
The grader reads no environment variables.
Stage 1: design the movement. Stage 2: add a 24-hour hand to a frozen stage-1 movement (--prev).
Stage 3: change request: the barrel turns once every 6 hours; every design check again, times a
kept-parts factor against the stage-2 movement (--prev).
Stage 4: give an assembly order and paths for a frozen stage-3 movement (--prev).
The folder holds movement.json and parts/<name>.step; only files named in movement.json are opened.
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
DAY_SPEED = Fraction(1, 24)
WEIGHTS_2 = {"day_hand": 3, "day_place": 1}
WEIGHTS = {"spin": 1, "held": 2, "train": 3, "clear": 1, "minute": 2, "hour": 2, "seconds": 2,
           "coaxial": 1, "hands": 1, "size": 1, "printable": 1, "tolerant": 2, "seated": 2}
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


def stage_weights(stage):
    return dict(WEIGHTS, **(WEIGHTS_2 if stage in (2, 3) else {}))


STAGE_GATES = {1: GATES, 2: GATES + ("locked", "day_declared"), 3: GATES + ("change_met",)}
CHANGE_CHECKS = ("hour", "minute", "seconds", "day_hand")     # stage 3: the change request is met


def grade_design(folder, stage=1, prev=None, skip=()):
    import math
    from geometry import watch as W
    from geometry.core import ivol
    weights = stage_weights(stage)
    for k in skip:                  # --skip, only for grading runs made before a check existed
        weights.pop(k, None)
    gates = {g: False for g in STAGE_GATES[stage]}
    checks = {k: False for k in weights}
    details = {}
    st = {"factor": 1.0}

    def result():
        G = all(gates.values())
        p = sum(w for k, w in weights.items() if checks[k]) / sum(weights.values())
        S = (0.5 * p * p + 0.5 * (1.0 if all(checks.values()) else 0.0)) if G else 0.0
        out = {"reward": S, "p": p, "gates": gates, "checks": checks, "details": details}
        if stage == 3:
            out["reward"] = S * st["factor"]
            out["kept_factor"] = st["factor"]
        return out

    def load():
        st["m"] = W.load_movement(folder)
        return True, {}
    gates["files"], details["files"] = _run(load)
    if not gates["files"]:
        if stage == 3:
            st["factor"] = 0.0
        return result()
    m = st["m"]
    if stage == 3:
        m.barrel_speed = W.CHANGED_BARREL_TURNS_PER_HOUR
    names = list(m.mobiles)

    def assembled():
        worst, pair = 0.0, None
        solids = [("fixed", m.fixed)] + [(n, m.mobiles[n]["solid"]) for n in names]
        for i in range(len(solids)):
            for j in range(i + 1, len(solids)):
                v = ivol(solids[i][1], solids[j][1])
                if v > worst:
                    worst, pair = v, solids[i][0] + "/" + solids[j][0]
        fw, fp = m.fixed_overlap()
        mw, mp = m.mobile_overlap()          # parts of one mobile touch but do not overlap
        return worst <= W.VOL_TOL and fw <= W.VOL_TOL and mw <= W.VOL_TOL, \
            {"worst_volume": worst, "pair": pair, "fixed_parts_worst": fw, "fixed_pair": fp, "mobile_parts_worst": mw, "mobile_pair": mp}
    gates["assembled"], details["assembled"] = _run(assembled)
    if stage == 2:
        gates["locked"], details["locked"] = _run(lambda: locked_design(prev, folder))
        gates["day_declared"], details["day_declared"] = _run(lambda: day_declared(prev, m))

    speeds, conflicts = m.speeds()

    def mesh_runs():
        """Every declared mesh through the train test, once. Its results are shared by train and the hands."""
        out = []
        for a, ta, b, tb in m.meshes:
            x = m.mesh_run(a, ta, b, tb)
            x["pair"] = "%s/%s" % (a, b)
            x["passes"] = x["worst_volume"] <= W.VOL_TOL and x["largest_gap"] <= W.ENGAGE_GAP and x["smallest_drive_overlap"] > W.VOL_TOL
            out.append(x)
        st["mesh_runs"] = out
        return True, {}
    st["mesh_runs"] = None
    _run(mesh_runs)
    runs = st["mesh_runs"]
    # A declared mesh drives only if it passes the train test; if the test failed to run, nothing drives.
    good = [e for e, x in zip(m.meshes, runs) if x["passes"]] if runs is not None else []
    driven, _ = m.speeds(good)
    if stage == 3:
        ok, details["kept"] = _run(lambda: kept_parts(prev, folder, driven))
        st["factor"] = details["kept"].get("factor", 0.0) if ok else 0.0

    def spin():
        r = {n: m.spin(n) for n in names}
        return all(v["worst_volume"] <= W.VOL_TOL for v in r.values()), r

    def held():
        r = {n: m.held(n) for n in names}
        return all(v > W.VOL_TOL for d in r.values() for v in d.values()), r

    def train():
        if runs is None:
            return False, {"error": "the mesh test did not run to the end"}
        r = {"conflicts": conflicts, "meshes": runs}
        ok = not conflicts and bool(m.meshes) and all(m.hands[h][0] in speeds for h in HAND_SPEED)
        return ok and all(x["passes"] for x in runs), r

    def tolerant():
        """Every declared mesh passes the train test again with the driven mobile moved MESH_SHIFT away
        from and towards the driver's axis. Only this check uses these runs."""
        r, ok = [], bool(m.meshes)
        for a, ta, b, tb in m.meshes:
            for label, s in (("away", W.MESH_SHIFT), ("towards", -W.MESH_SHIFT)):
                x = m.mesh_run(a, ta, b, tb, shift=s)
                x.update(pair="%s/%s" % (a, b), position=label, shift=s)
                x["passes"] = x["worst_volume"] <= W.VOL_TOL and x["largest_gap"] <= W.ENGAGE_GAP and x["smallest_drive_overlap"] > W.VOL_TOL
                ok = ok and x["passes"]
                r.append(x)
        return ok, {"meshes": r}

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
            w = driven.get(m.hands[h][0])
            return (not conflicts) and w == HAND_SPEED[h], {"clockwise_turns_per_hour_through_working_meshes": str(w)}
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

    def day_hand():
        if "day" not in m.hands:
            return False, {"error": "no 'day' hand declared"}
        w = driven.get(m.hands["day"][0])
        return (not conflicts) and w == DAY_SPEED, {"clockwise_turns_per_hour_through_working_meshes": str(w)}

    def day_place():
        if "day" not in m.hands:
            return False, {"error": "no 'day' hand declared"}
        a, b = m.mobiles[m.hands["day"][0]]["axis"], m.mobiles[m.hands["hour"][0]]["axis"]
        d, reach = math.hypot(a[0] - b[0], a[1] - b[1]), m.hand_reach("day")
        return d >= W.DAY_HAND_OFFSET and reach >= W.DAY_HAND_REACH, {"axis_distance": d, "reach": reach}

    def printable():
        r = {n: W.thin(solid) for n, (solid, _) in m.all_parts().items() if n != "barrel"}
        info = {n: {"pieces": v[0], "max_deviation": v[1]} for n, v in r.items()}
        return all(v[0] >= 1 and v[1] <= W.THIN_DEV for v in r.values()), info

    def seated():
        r = {n: m.seated(n) for n in names if n != "barrel"}
        bad = sorted(p for d in r.values() for p, mv in d.items()
                     if not (all(mv[k] > W.VOL_TOL for k in ("+x", "-x", "+y", "-y")) and max(mv["+z"], mv["-z"]) > W.VOL_TOL))
        return not bad, {"not_seated": bad, "moves": r}

    table = {"seated": seated, "printable": printable, "day_hand": day_hand, "day_place": day_place, "spin": spin, "held": held, "train": train, "clear": clear, "minute": hand("minute"), "hour": hand("hour"),
             "seconds": hand("seconds"), "coaxial": coaxial, "hands": hands, "size": size, "tolerant": tolerant}
    for k in weights:
        checks[k], details[k] = _run(table[k])
    if stage == 3:
        # the change request is met: every hand requirement passes with the 6-hour barrel (a skipped one is not checked)
        gates["change_met"] = all(checks.get(k, True) for k in CHANGE_CHECKS)
    return result()


def _part_file(folder, name):
    """The file of part `name`, as the loader picks it (geometry.watch.part_path), or None."""
    from geometry import watch as W
    return W.part_path(folder, name)


def _same_file(a, b):
    """Both files exist, have the same extension and the same bytes."""
    if a is None or b is None or not (os.path.isfile(a) and os.path.isfile(b)):
        return False
    if os.path.splitext(a)[1] != os.path.splitext(b)[1]:
        return False
    with open(a, "rb") as fa, open(b, "rb") as fb:
        return fa.read() == fb.read()


def _doc(folder):
    with open(os.path.join(folder, "movement.json")) as f:
        return json.load(f)


def locked_design(prev, folder):
    """Stage 2: every mobile of the previous stage keeps its axis and its part files, every declared
    mesh and the three hands stay. Fixed parts may change; parts and mobiles may be added."""
    if not prev:
        return False, {"error": "no previous stage given"}
    old, new = _doc(prev), _doc(folder)
    changed = []
    for name, m in old["mobiles"].items():
        n = new.get("mobiles", {}).get(name)
        if not n or [float(v) for v in n.get("axis", [])] != [float(v) for v in m["axis"]]:
            changed.append("mobile %s: missing or axis moved" % name)
            continue
        for part in m["parts"]:
            if part not in n.get("parts", []) or not _same_file(_part_file(prev, part), _part_file(folder, part)):
                changed.append("part %s: missing from its mobile or file changed" % part)
    for e in old["meshes"]:
        if e not in new.get("meshes", []):
            changed.append("mesh %s/%s removed or changed" % (e.get("driver"), e.get("driven")))
    for h in ("hour", "minute", "seconds"):
        if new.get("hands", {}).get(h) != old["hands"][h]:
            changed.append("hand %s changed" % h)
    return not changed, {"changed": changed}


def day_declared(prev, m):
    """Stage 2: a 24-hour hand is declared, and its part is a new part: its name appears nowhere in the
    received movement.json (it may sit on an existing mobile)."""
    if "day" not in m.hands:
        return False, {"error": "no 'day' hand declared"}
    if not prev:
        return False, {"error": "no previous stage given"}
    old = _doc(prev)
    received = set(old["fixed"]) | {p for mo in old["mobiles"].values() for p in mo["parts"]}
    part = m.hands["day"][1]
    return part not in received, {"part": part, "new_part": part not in received}


def kept_parts(prev, folder, speeds):
    """Stage 3: share of the received part files kept. A received fixed part counts if it is still under
    'fixed' and byte-identical. A received part of a mobile counts if it is byte-identical and still in a
    mobile of the same name, on the same axis, that is driven from the barrel."""
    from geometry import watch as W
    if not prev:
        return False, {"error": "no previous stage given", "factor": 0.0}
    old, new = _doc(prev), _doc(folder)
    new_mob = new.get("mobiles", {})
    kept, lost = [], []
    for part in old["fixed"]:
        ok = part in new.get("fixed", []) and _same_file(_part_file(prev, part), _part_file(folder, part))
        (kept if ok else lost).append(part)
    for name, mo in old["mobiles"].items():
        n = new_mob.get(name)
        same_axis = bool(n) and [float(v) for v in n.get("axis", [])] == [float(v) for v in mo["axis"]]
        for part in mo["parts"]:
            ok = same_axis and name in speeds and part in n.get("parts", []) \
                and _same_file(_part_file(prev, part), _part_file(folder, part))
            (kept if ok else lost).append(part)
    share = Fraction(len(kept), len(kept) + len(lost))
    factor = float(min(Fraction(1), share / W.REF_KEPT_SHARE))
    return True, {"kept": kept, "not_kept": lost, "share": str(share), "reference_share": str(W.REF_KEPT_SHARE), "factor": factor}


def locked_all(prev, folder):
    """Stage 4: movement.json and every part it names are byte-identical to the previous stage."""
    if not prev:
        return False, {"error": "no previous stage given"}
    changed = []
    if not _same_file(os.path.join(prev, "movement.json"), os.path.join(folder, "movement.json")):
        changed.append("movement.json")
    old = _doc(prev)
    for part in list(old["fixed"]) + [p for m in old["mobiles"].values() for p in m["parts"]]:
        if not _same_file(_part_file(prev, part), _part_file(folder, part)):
            changed.append(part)
    return not changed, {"changed": changed}


def grade_assembly(folder, prev):
    from geometry import watch as W
    gates = {"files": False, "locked": False, "plan": False}
    details, st = {}, {}
    out = {"reward": 0.0, "p": 0.0, "gates": gates, "checks": {}, "details": details}

    def load():
        st["m"] = W.load_movement(folder)
        return True, {}
    gates["files"], details["files"] = _run(load)
    gates["locked"], details["locked"] = _run(lambda: locked_all(prev, folder))

    def plan():
        st["order"], st["paths"] = W.load_assembly(folder, st["m"])
        return True, {}
    if gates["files"]:
        gates["plan"], details["plan"] = _run(plan)
    if not all(gates.values()):
        return out

    def replay():
        results, installed = st["m"].assembly_replay(st["order"], st["paths"])
        st["installed"] = installed
        return True, results
    ok, details["parts"] = _run(replay)
    if not ok:
        return out
    total = len(st["m"].all_parts())
    p = len(st["installed"]) / total
    out["checks"] = {n: n in st["installed"] for n in st["m"].all_parts()}
    out["p"] = p
    out["reward"] = 0.5 * p * p + 0.5 * (1.0 if len(st["installed"]) == total else 0.0)
    return out


def grade(folder, stage=1, prev=None, skip=()):
    skip = [k for k in skip if k]
    res = grade_assembly(folder, prev) if stage == 4 else grade_design(folder, stage, prev, skip)
    res["skipped"] = skip
    return res


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
    res = grade(args[0], int(opts.get("--stage", "1")), opts.get("--prev"), opts.get("--skip", "").split(","))
    if opts.get("--details"):
        with open(opts["--details"], "w") as f:
            json.dump(res, f, indent=1, default=str)
    with open(reward_file, "w") as f:
        f.write("%.6f\n" % res["reward"])
    print(json.dumps({k: res[k] for k in ("reward", "p", "gates", "checks", "kept_factor", "skipped") if k in res}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
