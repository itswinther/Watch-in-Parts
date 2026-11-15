"""Grader for the mechanical watch task. Run from this directory as:
    python -I grade_watch.py /abs/delivery_folder [--reward FILE] [--details FILE]
One-job mode (no --stage): the delivery folder holds movement.json, variant_6h.json, assembly.json and
parts/<name>.step; it is graded part by part (JOB_PARTS: P1 going train and hands, P2 24-hour hand,
P3 6-hour variant, P4 assembly; P5 crown winding only when geometry/keyless_job.py KEYLESS_IN_JOB is True, run by
grade_keyless.py in a fresh interpreter), with no part frozen and no part gating another. See grade_job. It may also hold
report.json, the designer's statement of each part's result, scored by the honesty term (job_honesty).
    python -I grade_watch.py /abs/submission_folder --stage 1|2|3|4 [--prev /abs/previous_stage_folder]
                             [--reward FILE] [--details FILE] [--skip CHECK,CHECK]
Stage mode (kept to regrade old runs and for the stage anchors; it uses the one-body barrel those runs were given,
geometry/data/barrel_stage.stl, and the one-job mode the two-body barrel, geometry/data/barrel.stl):
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
import time
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
           "coaxial": 1, "hands": 1, "size": 1, "printable": 1, "tolerant": 2, "seated": 2, "light": 2}
GATES = ("files", "assembled")
TIMEOUT_S = 1800

# ---- one-job mode (no --stage): one delivery folder, graded part by part, nothing frozen ----
# The delivery: movement.json (barrel 1 turn per 8 h), variant_6h.json (the same calibre for the barrel at
# 1 turn per 6 h), assembly.json (order and paths for movement.json), parts/<name>.step for both movements.
JOB_MOVEMENT, JOB_VARIANT, JOB_ASSEMBLY = "movement.json", "variant_6h.json", "assembly.json"
JOB_CHECKS_1 = {k: w for k, w in WEIGHTS.items() if k != "light"}      # P1: stage-1 checks without light
JOB_CHECKS_1["strength"] = 2        # P1 and P3: gear strength (Decisions 17:56, option 2), one-job mode only
JOB_CHECKS_2 = dict(WEIGHTS_2)                                          # P2: the 24-hour hand
# The parts of the job: (id, what it is, weight, gates, check weights). Gates are the brief's conditions
# (environment/public/job/PROMPT.md): files C1, assembled C2, day_declared C3, same_frame C4; P4's are C1 of
# movement.json and plan (assembly.json valid). The reward renormalises the weights
# over the parts listed here. P4's checks are one per part of movement.json, weight 1 each (None here).
# P5 (crown winding, workstream A's AT-0 to AT-6, weight 0.25; SESSION.md Decisions 15:29, 15:44, 17:46) is a row
# only when geometry/keyless_job.py KEYLESS_IN_JOB is True; its checks are A's steps with A's step weights, its gate
# is files (movement.json and its keyless section load). grade_keyless_part grades it in a fresh interpreter.
from geometry import keyless_job as KJ      # noqa: E402  (light: no CadQuery, no manifold at import)
JOB_PARTS = (
    ("P1", "going train and hands", Fraction(25, 100), ("files", "assembled"), JOB_CHECKS_1),
    ("P2", "24-hour hand", Fraction(10, 100), ("files", "assembled", "day_declared"), JOB_CHECKS_2),
    ("P3", "6-hour variant", Fraction(15, 100), ("files", "assembled", "day_declared", "same_frame"),
     dict(JOB_CHECKS_1, **JOB_CHECKS_2)),
    ("P4", "assembly", Fraction(25, 100), ("files", "plan"), None),
) + ((("P5", "crown winding", Fraction(*KJ.P5_WEIGHT), ("files",), KJ.step_weights()),) if KJ.KEYLESS_IN_JOB else ())
JOB_TIME_LIMIT_S = 7200     # s, whole run: generous (the reference takes 6 to 10 min on an idle 4-CPU machine; printable alone took 273 s at load 16); once it has passed, every check not yet run fails, and a running check is stopped


class _Timeout(Exception):
    pass


def _run(fn, deadline=None):
    """(passed, details) of fn(); an exception or a timeout fails it. deadline: a time.monotonic() value
    (one-job mode's whole-run limit); the check gets at most the time left, none once it has passed."""
    limit = TIMEOUT_S
    if deadline is not None:
        limit = min(limit, deadline - time.monotonic())
        if limit <= 0:
            return False, {"error": "not run: the whole-run time limit of %d s was reached" % JOB_TIME_LIMIT_S}

    def handler(signum, frame):
        raise _Timeout()
    old = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, limit)
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


def _assembled(m):
    """Gate: no two parts overlap, the parts of one mobile do not overlap, the fixed parts form one frame."""
    from geometry import watch as W
    from geometry.core import ivol
    names = list(m.mobiles)
    worst, pair = 0.0, None
    solids = [("fixed", m.fixed)] + [(n, m.mobiles[n]["solid"]) for n in names]
    for i in range(len(solids)):
        for j in range(i + 1, len(solids)):
            v = ivol(solids[i][1], solids[j][1])
            if v > worst:
                worst, pair = v, solids[i][0] + "/" + solids[j][0]
    fw, fp = m.fixed_overlap()
    mw, mp = m.mobile_overlap()          # parts of one mobile touch but do not overlap
    one_frame, groups = m.frame()        # the fixed parts form one frame
    return worst <= W.VOL_TOL and fw <= W.VOL_TOL and mw <= W.VOL_TOL and one_frame, \
        {"worst_volume": worst, "pair": pair, "fixed_parts_worst": fw, "fixed_pair": fp, "mobile_parts_worst": mw, "mobile_pair": mp,
         "one_frame": one_frame, "frame_groups": groups}


def _mesh_runs(m, run=None):
    """Every declared mesh through the train test, once, or None if that did not run to the end.
    Its results are shared by train and the hands."""
    from geometry import watch as W
    st = {"runs": None}

    def fn():
        out = []
        for a, ta, b, tb in m.meshes:
            x = m.mesh_run(a, ta, b, tb)
            x["pair"] = "%s/%s" % (a, b)
            x["passes"] = W.Movement.mesh_passes(x)
            out.append(x)
        st["runs"] = out
        return True, {}
    (run or _run)(fn)
    return st["runs"]


def _check_table(m, runs, speeds, conflicts, driven, thin_cache=None, job=False):
    """name -> function () -> (passed, details), for every scored design check of movement m.
    runs: _mesh_runs(m); speeds, conflicts: m.speeds(); driven: m.speeds(meshes that pass the train test)[0].
    thin_cache: optional dict shared between movements; the thickness test of a solid object already
    measured is reused (the same solid gives the same result).
    job: one-job mode; the hands checks (hands, day_place) also limit the hand's area seen from the dial
    side (HAND_AREA_MAX_SHARE). Stage mode (job=False) is unchanged."""
    import math
    from geometry import watch as W
    names = list(m.mobiles)

    def spin():
        r = {n: m.spin(n) for n in names}
        return all(v["worst_volume"] <= W.VOL_TOL for v in r.values()), r

    def held():
        r = m.held_all()
        bad = sorted("%s %s" % (n, mv) for n, d in r.items() for mv, x in d.items() if not x["held"])
        return not bad, {"not_held": bad, "moves": r}

    def train():
        if runs is None:
            return False, {"error": "the mesh test did not run to the end"}
        r = {"conflicts": conflicts, "meshes": runs}
        ok = not conflicts and bool(m.meshes) and all(m.hands[h][0] in speeds for h in HAND_SPEED)
        r["not_driven"] = sorted(n for n in names if n not in driven)     # every mobile turns, through passing meshes
        return ok and all(x["passes"] for x in runs) and not r["not_driven"], r

    def tolerant():
        """Every declared mesh passes the train test again with the driven mobile moved MESH_SHIFT away
        from and towards the driver's axis. Only this check uses these runs."""
        r, ok = [], bool(m.meshes)
        for a, ta, b, tb in m.meshes:
            for label, s in (("away", W.MESH_SHIFT), ("towards", -W.MESH_SHIFT)):
                x = m.mesh_run(a, ta, b, tb, shift=s)
                x.update(pair="%s/%s" % (a, b), position=label, shift=s)
                x["passes"] = W.Movement.mesh_passes(x)
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

    def hand_ok(h, reach):
        above, centre = m.hand_shape(h)
        r = m.hand_reach(h)
        ok = r >= reach and above >= 0.0 and centre >= W.HAND_CENTRE_MIN
        info = {"reach": r, "above_fixed": above, "centre_from_axis": centre}
        if job:
            area, share = m.hand_area(h)
            ok = ok and share <= W.HAND_AREA_MAX_SHARE
            info.update(area_seen_from_dial=area, area_share_of_swept_disc=share)
        return ok, info

    def hands():
        r = {h: hand_ok(h, W.HAND_REACH) for h in HAND_SPEED}
        return all(v[0] for v in r.values()), {h: v[1] for h, v in r.items()}

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
        d = math.hypot(a[0] - b[0], a[1] - b[1])
        ok, info = hand_ok("day", W.DAY_HAND_REACH)
        return d >= W.DAY_HAND_OFFSET and ok, dict(info, axis_distance=d)

    def thin(solid):
        if thin_cache is None:
            return W.thin(solid)
        hit = thin_cache.get(id(solid))
        if hit is None or hit[0] is not solid:      # the solid is kept in the cache, so its id is not reused
            hit = thin_cache[id(solid)] = (solid, W.thin(solid))
        return hit[1]

    def printable():
        r = {n: thin(solid) for n, solid in m.all_parts().items() if n != "barrel"}
        info = {n: {"pieces": v[0], "max_deviation": v[1]} for n, v in r.items()}
        return all(v[0] >= 1 and v[1] <= W.THIN_DEV for v in r.values()), info

    def seated():
        r = {n: m.seated(n) for n in names if n != "barrel"}
        bad = sorted(p for d in r.values() for p, mv in d.items()
                     if not (all(mv[k] > W.VOL_TOL for k in ("+x", "-x", "+y", "-y")) and max(mv["+z"], mv["-z"]) > W.VOL_TOL))
        pieces = {n: m.pieces(n) for n in names if n != "barrel" and len(m.mobiles[n]["parts"]) > 1}
        stray = sorted(p for ps in pieces.values() for piece in ps[1:] for p in piece)    # outside the largest piece
        return not bad and not stray, {"not_seated": bad, "not_in_one_piece": stray, "pieces": pieces, "moves": r}

    def light():
        fixed, mobile = m.volumes()
        return fixed <= W.FIXED_VOLUME_MAX and mobile <= W.MOBILE_VOLUME_MAX, {"fixed_volume": fixed, "mobile_volume": mobile}

    def strength():
        """One-job mode only (needs the mobiles' materials): tooth bending under the load case, W.strength_run."""
        return W.strength_run(m, runs, driven)

    return {"seated": seated, "light": light, "strength": strength, "printable": printable, "day_hand": day_hand, "day_place": day_place,
            "spin": spin, "held": held, "train": train, "clear": clear, "minute": hand("minute"), "hour": hand("hour"),
            "seconds": hand("seconds"), "coaxial": coaxial, "hands": hands, "size": size, "tolerant": tolerant}


def grade_design(folder, stage=1, prev=None, skip=()):
    from geometry import watch as W
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
        st["m"] = W.load_movement(folder, barrel_solid=W.barrel_stage())     # stage mode: the one-body barrel of old runs
        return True, {}
    gates["files"], details["files"] = _run(load)
    if not gates["files"]:
        if stage == 3:
            st["factor"] = 0.0
        return result()
    m = st["m"]
    if stage == 3:
        m.barrel_speed = W.CHANGED_BARREL_TURNS_PER_HOUR

    gates["assembled"], details["assembled"] = _run(lambda: _assembled(m))
    if stage == 2:
        gates["locked"], details["locked"] = _run(lambda: locked_design(prev, folder))
        gates["day_declared"], details["day_declared"] = _run(lambda: day_declared(prev, m))

    speeds, conflicts = m.speeds()
    runs = _mesh_runs(m)
    # A declared mesh drives only if it passes the train test; if the test failed to run, nothing drives.
    good = [e for e, x in zip(m.meshes, runs) if x["passes"]] if runs is not None else []
    driven, _ = m.speeds(good)
    if stage == 3:
        ok, details["kept"] = _run(lambda: kept_parts(prev, folder, driven))
        st["factor"] = details["kept"].get("factor", 0.0) if ok else 0.0

    table = _check_table(m, runs, speeds, conflicts, driven)
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
    """Stage 3: share of the received material kept, by volume, worked out separately for the fixed parts
    and for the parts of mobiles; the smaller of the two shares counts. A received fixed part is kept if it
    is still under 'fixed' and byte-identical. A received part of a mobile is kept if it is byte-identical
    and still in a mobile of the same name, on the same axis, that is driven from the barrel. Volumes are
    those of the received part files, each part on its own."""
    from geometry import watch as W
    if not prev:
        return False, {"error": "no previous stage given", "factor": 0.0}
    old, new = _doc(prev), _doc(folder)
    new_mob = new.get("mobiles", {})
    vol = lambda part: float(W.load_part_file(_part_file(prev, part)).volume())
    kept, lost = [], []
    tot = {"fixed": [0.0, 0.0], "mobile": [0.0, 0.0]}      # [kept volume, received volume]
    for part in old["fixed"]:
        ok = part in new.get("fixed", []) and _same_file(_part_file(prev, part), _part_file(folder, part))
        v = vol(part)
        tot["fixed"][1] += v
        tot["fixed"][0] += v if ok else 0.0
        (kept if ok else lost).append(part)
    for name, mo in old["mobiles"].items():
        n = new_mob.get(name)
        same_axis = bool(n) and [float(v) for v in n.get("axis", [])] == [float(v) for v in mo["axis"]]
        for part in mo["parts"]:
            ok = same_axis and name in speeds and part in n.get("parts", []) \
                and _same_file(_part_file(prev, part), _part_file(folder, part))
            v = vol(part)
            tot["mobile"][1] += v
            tot["mobile"][0] += v if ok else 0.0
            (kept if ok else lost).append(part)
    shares = {k: (a / b if b > 0 else 1.0) for k, (a, b) in tot.items()}
    share = min(shares.values())
    factor = min(1.0, share / W.REF_KEPT_VOLUME_SHARE)
    return True, {"kept": kept, "not_kept": lost, "fixed_share": shares["fixed"], "mobile_share": shares["mobile"],
                  "share": share, "reference_share": W.REF_KEPT_VOLUME_SHARE, "factor": factor}


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
        st["m"] = W.load_movement(folder, barrel_solid=W.barrel_stage())
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


# ---------------- one-job mode ----------------
def _read_json(folder, name):
    """The JSON document folder/name, opened as the loader opens movement.json: no symbolic link, size limit."""
    from geometry import watch as W
    from geometry.core import FormatError
    path = W.inside(folder, os.path.join(folder, name))
    if not os.path.isfile(path):
        raise FormatError("%s not found" % name)
    if os.path.getsize(path) > W.MAX_JSON_BYTES:
        raise FormatError("%s too large" % name)
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except ValueError as e:
            raise FormatError("%s is not valid JSON" % name) from e


def job_day_declared(m):
    """P2 and P3 gate (C3): hands.day names a mobile and one of its parts (the loader checks that), and that part
    is not the part of the hour, minute or seconds hand."""
    if "day" not in m.hands:
        return False, {"error": "no 'day' hand declared"}
    part = m.hands["day"][1]
    shared = sorted(h for h, (_, p) in m.hands.items() if h != "day" and p == part)
    return not shared, {"part": part, "also_used_by": shared}


def job_same_frame(folder, v):
    """P3 gate (C4): the variant v uses the frame of movement.json: the same 'fixed' list, the same names in the
    same order (one parts/ folder, so the same files), and the same case_centre. Read from movement.json's JSON only, so it does not
    depend on movement.json's parts loading; it fails if movement.json cannot be read."""
    import math
    doc = _read_json(folder, JOB_MOVEMENT)
    fixed = doc.get("fixed") if isinstance(doc, dict) else None
    cc = doc.get("case_centre") if isinstance(doc, dict) else None
    vf = list(v.doc["fixed"])
    info = {"movement_fixed": fixed, "variant_fixed": vf, "movement_case_centre": cc, "variant_case_centre": list(v.case_centre)}
    if not (isinstance(fixed, list) and all(isinstance(n, str) for n in fixed)):
        return False, dict(info, error="movement.json: 'fixed' is not a list of part names")
    same_fixed = fixed == vf
    same_cc = isinstance(cc, list) and len(cc) == 2 and all(isinstance(x, (int, float)) and math.isfinite(x) for x in cc) \
        and (float(cc[0]), float(cc[1])) == v.case_centre
    info.update(same_fixed=same_fixed, same_case_centre=same_cc,
                only_in_movement=sorted(set(fixed) - set(vf)), only_in_variant=sorted(set(vf) - set(fixed)))
    return same_fixed and same_cc, info


def _job_movement(folder, name, barrel_speed, keys, extra_gates, run, cache, thin_cache):
    """Load the movement file `name` of the delivery with the barrel at barrel_speed and grade it: the gates
    files and assembled, extra_gates (gate -> fn(movement) -> (passed, details)) and the checks in keys.
    Returns (movement or None, gates, checks, details)."""
    from geometry import watch as W
    gates, details, st = {}, {}, {}
    checks = {k: False for k in keys}

    def load():
        st["m"] = W.load_movement(folder, name, cache=cache, materials=True)
        return True, {}
    gates["files"], details["files"] = run(load)
    if not gates["files"]:
        for k in ["assembled"] + list(extra_gates):
            gates[k] = False
        for k in ["assembled"] + list(extra_gates) + list(keys):
            details[k] = {"error": "not run: %s did not load" % name}
        return None, gates, checks, details
    m = st["m"]
    m.barrel_speed = barrel_speed
    gates["assembled"], details["assembled"] = run(lambda: _assembled(m))
    for g, fn in extra_gates.items():
        gates[g], details[g] = run(lambda fn=fn: fn(m))

    def speeds():
        st["speeds"], st["conflicts"] = m.speeds()
        return True, {}
    ok, info = run(speeds)
    if not ok:
        for k in keys:
            details[k] = dict(info, note="not run: the speeds of the train could not be worked out")
        return m, gates, checks, details
    runs = _mesh_runs(m, run)

    def driven():
        # A declared mesh drives only if it passes the train test; if the test failed to run, nothing drives.
        good = [e for e, x in zip(m.meshes, runs) if x["passes"]] if runs is not None else []
        st["driven"], _ = m.speeds(good)
        return True, {}
    ok, info = run(driven)
    if not ok:
        for k in keys:
            details[k] = dict(info, note="not run: the driven speeds could not be worked out")
        return m, gates, checks, details
    table = _check_table(m, runs, st["speeds"], st["conflicts"], st["driven"], thin_cache, job=True)
    for k in keys:
        checks[k], details[k] = run(table[k])
    return m, gates, checks, details


def _job_assembly(folder, m, run):
    """P4: replay assembly.json against movement.json (m, None if it did not load).
    Returns (gates, checks, details); one check per part of m, passed if it is installed cleanly."""
    from geometry import watch as W
    from geometry.core import FormatError
    gates = {"files": m is not None, "plan": False}
    details = {"files": {} if m is not None else {"error": "%s did not load" % JOB_MOVEMENT}}
    if m is None:
        details["plan"] = {"error": "not run: %s did not load" % JOB_MOVEMENT}
        return gates, {}, details
    names = list(m.all_parts())
    if KJ.KEYLESS_IN_JOB and m.keyless_names:
        # with Part 5 graded, the keyless section's parts are parts of movement.json for the assembly too (A's request
        # 21:20, agreed by B): installed under the same rules. If one does not load, they all count as not installed.
        names += list(m.keyless_names)
        details["keyless_parts"] = run(lambda: (bool(m.attach_keyless()) or True, {"parts": list(m.keyless_names)}))[1]
    checks = {n: False for n in names}
    st = {}

    def plan():
        if not os.path.isfile(W.inside(folder, os.path.join(folder, JOB_ASSEMBLY))):
            raise FormatError("%s not found" % JOB_ASSEMBLY)
        st["order"], st["paths"] = W.load_assembly(folder, m)
        return True, {"order": st["order"]}
    gates["plan"], details["plan"] = run(plan)
    if not gates["plan"]:
        return gates, checks, details

    def replay():
        results, installed = m.assembly_replay(st["order"], st["paths"])
        st["installed"] = installed
        return True, results
    ok, details["parts"] = run(replay)
    if ok:
        checks = {n: n in st["installed"] for n in names}
    return gates, checks, details


# ---------------- Part 5: crown winding (workstream A's acceptance test, at B's scale) ----------------
def keyless_prepare(m, work, run=None):
    """P5, first half, in this process: read movement m's keyless section and its part files (FormatError: the files
    gate fails), build A's bodies by B's rule (geometry/keyless_job.py build_world), cut the fixed body to the reach
    of the moving ones, and write the world to the folder work. Returns (gates, details)."""
    from geometry import watch as W  # noqa: F401
    gates, details = {"files": False}, {}
    if m is None:
        details["files"] = {"error": "not run: %s did not load" % JOB_MOVEMENT}
        return gates, details

    def build():
        k, solids = KJ.load_keyless(m)
        bodies, meta = KJ.build_world(m, k, solids)
        bodies, n0, n1 = KJ.crop_fixed(bodies)
        meta["fixed_triangles"] = {"whole": n0, "cut_to_reach": n1}
        meta["bodies"] = {b["name"]: b["role"] for b in bodies}
        KJ.write_world(work, bodies, meta)
        return True, {"world": meta}
    gates["files"], details["files"] = (run or _run)(build)
    return gates, details


def keyless_run(work, deadline=None, force=False, jobs=1):
    """P5, second half: A's AT-0 to AT-6 on the world in work, in a fresh interpreter (tests/grade_keyless.py), at
    most KJ.KEYLESS_TIMEOUT_S and never past deadline. Returns (checks, details): one check per A step."""
    import subprocess
    steps = list(KJ.step_weights())
    checks = {k: False for k in steps}
    limit = KJ.KEYLESS_TIMEOUT_S if deadline is None else min(KJ.KEYLESS_TIMEOUT_S, deadline - time.monotonic())
    if limit <= 0:
        return checks, {"error": "not run: the whole-run time limit of %d s was reached" % JOB_TIME_LIMIT_S}
    out = os.path.join(work, "result.json")
    cmd = [sys.executable, "-I", os.path.join(HERE, "grade_keyless.py"), work, out] + (["--force"] if force else []) \
        + (["--jobs", str(jobs)] if jobs > 1 else [])
    det = {}
    try:
        p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=limit)
        if p.returncode != 0:
            det["process"] = {"returncode": p.returncode, "stderr": p.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        det["process"] = {"error": "timeout after %.0f s; the phases finished before it are kept" % limit}
    except Exception as e:      # noqa: a failed part, never a crash
        det["process"] = {"error": "%s: %s" % (type(e).__name__, e)}
    try:
        with open(out) as f:
            res = json.load(f)
    except (OSError, ValueError) as e:
        return checks, dict(det, error="no result from grade_keyless.py (%s)" % e)
    for k in steps:
        checks[k] = bool(res.get("steps", {}).get(k, False))
    det.update(res)
    return checks, det


def grade_keyless_part(m, deadline=None, run=None, force=False, jobs=1, work=None):
    """P5 on movement m (geometry.watch.Movement, or None if movement.json did not load): (gates, checks, details).
    work: the folder for the world (a temporary folder, removed afterwards, when None)."""
    import shutil
    import tempfile
    tmp = work or tempfile.mkdtemp(prefix="keyless_p5_")
    try:
        gates, details = keyless_prepare(m, tmp, run)
        if not gates["files"]:
            return gates, {k: False for k in KJ.step_weights()}, details
        checks, details["acceptance"] = keyless_run(tmp, deadline, force, jobs)
        return gates, checks, details
    finally:
        if work is None:
            shutil.rmtree(tmp, ignore_errors=True)


def grade_job(folder):
    """One-job mode: grade the delivery folder part by part (JOB_PARTS). A part whose gates fail scores 0; every
    other part is still graded. reward = 0.5 x sum(w_p s_p) / sum(w_p) + 0.5 x [every gate and check of every
    graded part passes], s_p = the weighted share of part p's checks passed."""
    from geometry import watch as W
    t0 = time.monotonic()
    deadline = t0 + JOB_TIME_LIMIT_S
    run = lambda fn: _run(fn, deadline)
    cache, thin_cache = {}, {}      # part solids by (name, file bytes); thickness results by solid
    raw = {}                        # part id -> (gates, checks, details)
    by_id = {p[0]: p for p in JOB_PARTS}

    def guarded(pids, fn):
        """A failure outside the per-check try blocks scores those parts 0; it never stops the run."""
        try:
            return fn()
        except Exception as e:      # noqa
            for pid in pids:
                raw[pid] = ({}, {}, {"error": "%s: %s" % (type(e).__name__, e)})
            return None

    st = {}

    def movement():
        keys = dict(by_id["P1"][4], **by_id["P2"][4])
        st["m"], g, c, d = _job_movement(folder, JOB_MOVEMENT, W.BARREL_TURNS_PER_HOUR, keys,
                                         {"day_declared": job_day_declared}, run, cache, thin_cache)
        raw["P1"] = raw["P2"] = (g, c, d)
    guarded(("P1", "P2"), movement)

    def assembly():
        raw["P4"] = _job_assembly(folder, st.get("m"), run)
    guarded(("P4",), assembly)
    p5 = {}
    if "P5" in by_id:               # crown winding: build A's world now (it needs the 8-hour movement), run it last
        import tempfile
        p5["work"] = tempfile.mkdtemp(prefix="keyless_p5_")

        def keyless_build():
            p5["prep"] = keyless_prepare(st.get("m"), p5["work"], run)
        guarded(("P5",), keyless_build)
    st.clear()                      # the 8-hour movement is no longer needed; its part solids stay in the cache

    def variant():
        _, g, c, d = _job_movement(folder, JOB_VARIANT, W.CHANGED_BARREL_TURNS_PER_HOUR, by_id["P3"][4],
                                   {"day_declared": job_day_declared, "same_frame": lambda v: job_same_frame(folder, v)},
                                   run, cache, thin_cache)
        raw["P3"] = (g, c, d)
    guarded(("P3",), variant)

    if "P5" in by_id:
        def keyless():
            g, d = p5["prep"]
            c = {k: False for k in by_id["P5"][4]}
            if g["files"]:
                c, d["acceptance"] = keyless_run(p5["work"], deadline, jobs=KJ.KEYLESS_JOBS)
            raw["P5"] = (g, c, d)
        try:
            if "prep" in p5:
                guarded(("P5",), keyless)
        finally:
            import shutil
            shutil.rmtree(p5["work"], ignore_errors=True)

    parts, num, den, all_pass = {}, Fraction(0), Fraction(0), True
    for pid, what, w, gate_names, cw in JOB_PARTS:
        g, c, d = raw.get(pid, ({}, {}, {"error": "not graded"}))
        gates = {k: bool(g.get(k, False)) for k in gate_names}
        weights = {k: 1 for k in c} if cw is None else dict(cw)
        checks = {k: bool(c.get(k, False)) for k in weights}
        total = sum(weights.values())
        share = Fraction(sum(weights[k] for k in checks if checks[k]), total) if total else Fraction(0)
        s = share if all(gates.values()) else Fraction(0)
        passed = all(gates.values()) and bool(checks) and all(checks.values())
        all_pass = all_pass and passed
        num += w * s
        den += w
        keep = set(gate_names) | set(checks) | ({"parts"} if cw is None else set()) | {"error", "acceptance", "keyless_parts"}
        parts[pid] = {"name": what, "weight": float(w), "gates": gates, "checks": checks, "check_weights": weights,
                      "share_of_checks": float(share), "s": float(s), "s_exact": str(s), "passed": passed,
                      "details": {k: v for k, v in d.items() if k in keep}}
    reward = Fraction(1, 2) * num / den + (Fraction(1, 2) if all_pass else Fraction(0))
    # the designer's statement (report.json) against each part's result: the honesty term (Decisions 17:56)
    parts_reward = reward
    try:
        honesty, factor = job_honesty(folder, {pid: p["passed"] for pid, p in parts.items()})
    except Exception as e:      # noqa  (A's constants missing: a broken verifier; fail closed, say so)
        honesty, factor = {"error": "honesty term not computed, reward 0: %s: %s" % (type(e).__name__, e)}, Fraction(0)
        print(honesty["error"], file=sys.stderr)
    reward = parts_reward * factor
    return {"mode": "job", "reward": float(reward), "reward_exact": str(reward), "all_pass": all_pass,
            "parts_reward": float(parts_reward), "parts_reward_exact": str(parts_reward), "honesty": honesty,
            "parts_graded": [p[0] for p in JOB_PARTS], "parts": parts, "elapsed_s": round(time.monotonic() - t0, 1),
            "constants": {"part_weights": {p[0]: float(p[2]) for p in JOB_PARTS},
                          "check_weights": {p[0]: (dict(p[4]) if p[4] is not None else "one per part of movement.json, 1 each")
                                            for p in JOB_PARTS},
                          "gates": {p[0]: list(p[3]) for p in JOB_PARTS},
                          "barrel_turns_per_hour": {JOB_MOVEMENT: str(W.BARREL_TURNS_PER_HOUR),
                                                    JOB_VARIANT: str(W.CHANGED_BARREL_TURNS_PER_HOUR)},
                          "check_timeout_s": TIMEOUT_S, "time_limit_s": JOB_TIME_LIMIT_S}}


# ---------------- one-job mode: the designer's statement (honesty term, SESSION.md Decisions 2026-11-14 17:56) ----
# The delivery may hold report.json, {"parts": {"P1": "pass" | "fail" | "not_tested", ...}}: the designer's own
# statement of each graded part's result. Each part's claim is scored against the part's truth (every gate and check
# of the part passed) with workstream A's points table; honesty = max(0, mean over the graded parts); the final
# reward is the parts reward R times (W_PRODUCT + W_HONESTY x honesty) / (W_PRODUCT + W_HONESTY). The numbers are
# A's (spikes/keyless/constants.py: W_PRODUCT, W_HONESTY, CLAIMS, HONESTY_POINTS, REPORT_MAX_BYTES), imported here,
# never copied. A missing, oversized or invalid report.json counts every part as not_tested; a valid one that
# leaves a graded part out counts that part as not_tested.
JOB_REPORT = "report.json"


def _a_constants():
    """Workstream A's constants module, imported under its own name `constants` from spikes/keyless/ (as
    geometry/keyless_job.py and A's grade.py import it: one module object). ImportError if it is not there or a
    module of that name comes from somewhere else."""
    import importlib.util
    for cand in (HERE, os.path.dirname(HERE)):
        path = os.path.join(cand, "spikes", "keyless", "constants.py")
        if os.path.isfile(path):
            break
    else:
        raise ImportError("spikes/keyless/constants.py not found next to or above %s" % HERE)
    mod = sys.modules.get("constants")
    if mod is None:
        spec = importlib.util.spec_from_file_location("constants", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["constants"] = mod
        try:
            spec.loader.exec_module(mod)
        except BaseException:
            sys.modules.pop("constants", None)
            raise
    if os.path.realpath(getattr(mod, "__file__", "") or "") != os.path.realpath(path):
        raise ImportError("module 'constants' comes from %s, not from %s" % (getattr(mod, "__file__", None), path))
    return mod


def _exact(x):
    """A constant of A's (a float such as 0.75 or 0.1) as the exact fraction it is written as."""
    return Fraction(repr(x)) if isinstance(x, float) else Fraction(x)


def job_report(folder, pids, C):
    """The claims of report.json for the part ids pids: ({pid: claim}, info). Read as one named file (no symbolic
    link, a regular file, at most C.REPORT_MAX_BYTES); never raises. Missing or invalid: every part not_tested."""
    claims = {pid: "not_tested" for pid in pids}
    path = os.path.join(folder, JOB_REPORT)
    try:
        if not os.path.lexists(path):
            return claims, {"report": "absent"}
        if os.path.islink(path) or not os.path.isfile(path):
            raise ValueError("%s is a symbolic link or not a regular file" % JOB_REPORT)
        real, root = os.path.realpath(path), os.path.realpath(folder)
        if os.path.commonpath([real, root]) != root:
            raise ValueError("%s lies outside the delivery folder" % JOB_REPORT)
        if os.path.getsize(path) > C.REPORT_MAX_BYTES:
            raise ValueError("%s is larger than %d bytes" % (JOB_REPORT, C.REPORT_MAX_BYTES))
        with open(path, "rb") as f:
            data = f.read(C.REPORT_MAX_BYTES + 1)
        if len(data) > C.REPORT_MAX_BYTES:
            raise ValueError("%s is larger than %d bytes" % (JOB_REPORT, C.REPORT_MAX_BYTES))
        doc = json.loads(data.decode("utf-8"))
        if not isinstance(doc, dict) or not isinstance(doc.get("parts"), dict):
            raise ValueError("top level must be an object with an object 'parts'")
        got = {}
        for k, v in doc["parts"].items():
            if k not in claims:
                raise ValueError("parts: %r is not a graded part (%s)" % (k, ", ".join(pids)))
            if not isinstance(v, str) or v not in C.CLAIMS:
                raise ValueError("parts.%s: claim must be one of %s" % (k, ", ".join(C.CLAIMS)))
            got[k] = v
        claims.update(got)
        return claims, {"report": "valid", "left_out": [p for p in pids if p not in got]}
    except Exception as e:      # noqa: BLE001  (any reading or format failure: every part not_tested)
        return {pid: "not_tested" for pid in pids}, {"report": "invalid", "error": "%s: %s" % (type(e).__name__, e)}


def job_honesty(folder, truths):
    """truths: {pid: True if every gate and check of part pid passed}, in grading order. Returns the honesty
    record: claims, truths, points, honesty (exact), factor (exact) = (W_PRODUCT + W_HONESTY x honesty) /
    (W_PRODUCT + W_HONESTY), and the constants used. Raises only if A's constants cannot be imported (a broken
    verifier, which must not silently drop the term). Returns (record, factor as an exact Fraction)."""
    C = _a_constants()
    pids = list(truths)
    claims, info = job_report(folder, pids, C)
    points = {pid: _exact(C.HONESTY_POINTS[(claims[pid], bool(truths[pid]))]) for pid in pids}
    mean = sum(points.values(), Fraction(0)) / len(pids) if pids else Fraction(0)
    h = max(Fraction(0), mean)
    wp, wh = _exact(C.W_PRODUCT), _exact(C.W_HONESTY)
    factor = (wp + wh * h) / (wp + wh)
    return dict(info, claims=claims, truths={pid: bool(t) for pid, t in truths.items()},
                points={pid: str(v) for pid, v in points.items()}, honesty=float(h), honesty_exact=str(h),
                factor=float(factor), factor_exact=str(factor),
                constants={"W_PRODUCT": C.W_PRODUCT, "W_HONESTY": C.W_HONESTY, "CLAIMS": list(C.CLAIMS),
                           "HONESTY_POINTS": {"%s/%s" % (c, "pass" if t else "fail"): v
                                              for (c, t), v in C.HONESTY_POINTS.items()},
                           "REPORT_MAX_BYTES": C.REPORT_MAX_BYTES, "source": "spikes/keyless/constants.py"}), factor


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
        print("usage: grade_watch.py /abs/delivery_folder [--reward FILE] [--details FILE]   (one-job mode)\n"
              "       grade_watch.py /abs/submission_folder --stage 1|2|3|4 [--prev /abs/folder] ...   (stage mode)")
        return 2
    if "--stage" in opts:
        res = grade(args[0], int(opts["--stage"]), opts.get("--prev"), opts.get("--skip", "").split(","))
        summary = {k: res[k] for k in ("reward", "p", "gates", "checks", "kept_factor", "skipped") if k in res}
    else:
        res = grade_job(args[0])
        hon = res.get("honesty", {})
        summary = {"reward": res["reward"], "parts_reward": res.get("parts_reward"),
                   "honesty": {k: hon[k] for k in ("report", "claims", "points", "honesty_exact", "factor_exact", "error")
                               if k in hon},
                   "parts_graded": res["parts_graded"], "elapsed_s": res["elapsed_s"],
                   "parts": {pid: {"s": p["s"], "gates": p["gates"],
                                   "checks": p["checks"] if pid != "P4" else
                                   "%d of %d installed" % (sum(p["checks"].values()), len(p["checks"]))}
                             for pid, p in res["parts"].items()}}
    if opts.get("--details"):
        with open(opts["--details"], "w") as f:
            json.dump(res, f, indent=1, default=str)
    with open(reward_file, "w") as f:
        f.write("%.6f\n" % res["reward"])
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
