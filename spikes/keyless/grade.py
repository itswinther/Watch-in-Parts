"""Grader for the keyless-works spike: behaviour by simulated contact.

    python -I grade.py SUBMISSION_DIR DATA_DIR --reward REWARD_FILE [--details DETAILS_JSON] [--jobs N]

SUBMISSION_DIR holds keyless.json and parts/<name>.stl for every named part. DATA_DIR holds the
supplied parts (main_plate, dial_plate, barrel_arbor, minute_wheel, minute_post). Opens only named
files by absolute path. Never runs submitted code. Writes reward 0 first.
"""
import argparse
import json
import math
import os
import re
import struct
import sys
import time
from concurrent.futures import ProcessPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import manifold3d as m3  # noqa: E402
import constants as C  # noqa: E402
import engine as E  # noqa: E402

SUPPLIED = ("main_plate", "dial_plate", "barrel_arbor", "minute_wheel", "minute_post")


class FormatError(Exception):
    pass


def read_stl(path):
    with open(path, "rb") as f:
        data = f.read(C.MAX_BYTES + 1)
    if len(data) > C.MAX_BYTES:
        raise FormatError("file larger than %d bytes" % C.MAX_BYTES)
    if len(data) < 84:
        raise FormatError("file too short to be an STL")
    n = struct.unpack_from("<I", data, 80)[0]
    if len(data) == 84 + 50 * n:
        if n > C.MAX_TRIANGLES:
            raise FormatError("more than %d triangles" % C.MAX_TRIANGLES)
        rec = np.frombuffer(data, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]),
                            count=n, offset=84)
        tris = rec["v"].astype(np.float64)
    else:
        try:
            text = data.decode("ascii")
        except UnicodeDecodeError:
            raise FormatError("neither a binary STL of the declared length nor ASCII")
        vals = []
        for line in text.splitlines():
            p = line.split()
            if len(p) == 4 and p[0] == "vertex":
                try:
                    vals.append((float(p[1]), float(p[2]), float(p[3])))
                except ValueError:
                    raise FormatError("non-numeric vertex coordinate")
                if len(vals) > 3 * C.MAX_TRIANGLES:
                    raise FormatError("more than %d triangles" % C.MAX_TRIANGLES)
        if not vals or len(vals) % 3:
            raise FormatError("no complete triangles found")
        tris = np.array(vals, dtype=np.float64).reshape(-1, 3, 3)
    if len(tris) == 0 or not np.isfinite(tris).all():
        raise FormatError("no triangles or a non-finite coordinate")
    return tris


def to_manifold(tris):
    flat = tris.reshape(-1, 3).astype(np.float32)
    verts, inv = np.unique(flat, axis=0, return_inverse=True)
    faces = inv.reshape(-1, 3).astype(np.uint32)
    keep = (faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])
    man = m3.Manifold(m3.Mesh(vert_properties=verts, tri_verts=faces[keep]))
    if man.status() != m3.Error.NoError:
        raise FormatError("mesh is not a closed manifold (%s)" % man.status().name)
    vol = man.volume()
    if not np.isfinite(vol) or vol <= 0:
        raise FormatError("volume is not positive")
    return man


def union(ms):
    ms = [m for m in ms if m is not None and not m.is_empty()]
    if not ms:
        return m3.Manifold()
    return ms[0] if len(ms) == 1 else m3.Manifold.batch_boolean(ms, m3.OpType.Add)


# ---------- reading the submission ----------
def load(sub, data):
    spec = json.load(open(os.path.join(sub, "keyless.json")))
    mobiles, fixed = spec.get("mobiles"), spec.get("fixed", [])
    if not isinstance(mobiles, dict) or not isinstance(fixed, list):
        raise FormatError("mobiles must be an object and fixed a list")
    if "stem" not in mobiles or "barrel" not in mobiles:
        raise FormatError("mobiles 'stem' and 'barrel' are required")
    names = []
    for mn, mob in mobiles.items():
        if not isinstance(mn, str) or not re.match(C.NAME_RE, mn) or mn in ("minute_wheel", "fixed"):
            raise FormatError("bad mobile name")
        if not isinstance(mob, dict) or not isinstance(mob.get("parts"), list) or not mob["parts"]:
            raise FormatError("mobile %s needs a non-empty parts list" % mn)
        names += mob["parts"]
    names += fixed
    if len(set(names)) != len(names):
        raise FormatError("a part is listed twice")
    for p in names:
        if not isinstance(p, str) or not re.match(C.NAME_RE, p) or p in C.RESERVED:
            raise FormatError("bad or reserved part name")
    if len(names) > 40:
        raise FormatError("more than 40 parts")
    parts = {}
    for p in names:
        path = os.path.join(sub, "parts", p + ".stl")
        if os.path.islink(path) or os.path.islink(os.path.join(sub, "parts")):
            raise FormatError("symbolic links are not accepted")
        parts[p] = to_manifold(read_stl(path))
    sup = {p: to_manifold(read_stl(os.path.join(data, p + ".stl"))) for p in SUPPLIED}
    # body definitions (plain data, rebuilt in each worker)
    defs = []
    for mn, mob in mobiles.items():
        kind = mob.get("kind")
        if mn == "stem":
            if kind != "stem":
                raise FormatError("mobile 'stem' must have kind 'stem'")
            defs.append(dict(name=mn, parts=mob["parts"], kind="driven", dof="stem",
                             point=C.STEM_POINT, direction=C.STEM_DIR))
            continue
        if mn == "barrel":
            if kind != "barrel":
                raise FormatError("mobile 'barrel' must have kind 'barrel'")
            defs.append(dict(name=mn, parts=mob["parts"] + ["@barrel_arbor"], kind="main", dof="rot",
                             point=(C.BARREL_AXIS[0], C.BARREL_AXIS[1], 0.0), direction=(0, 0, 1),
                             rest=-C.WIND_SENSE * math.inf))
            continue
        if kind not in ("free", "spring"):
            raise FormatError("mobile %s: kind must be 'free' or 'spring'" % mn)
        dof = mob.get("dof")
        if dof not in ("rot", "slide"):
            raise FormatError("mobile %s: dof must be 'rot' or 'slide'" % mn)
        d = np.asarray(mob.get("direction"), float)
        if d.shape != (3,) or not np.isfinite(d).all() or np.linalg.norm(d) < 1e-9:
            raise FormatError("mobile %s: direction must be 3 finite numbers" % mn)
        pt = (0.0, 0.0, 0.0)
        if dof == "rot":
            pt = np.asarray(mob.get("point"), float)
            if pt.shape != (3,) or not np.isfinite(pt).all():
                raise FormatError("mobile %s: point must be 3 finite numbers" % mn)
            pt = tuple(float(v) for v in pt)
        on_stem = bool(mob.get("on_stem", False))
        if on_stem:
            dn = d / np.linalg.norm(d)
            if dof != "slide" or abs(abs(dn[0]) - 1) > 1e-6:
                raise FormatError("mobile %s: only a slide along the stem axis can ride on the stem" % mn)
        carrier = "stem" if on_stem else None
        if mob.get("carrier") is not None:
            cn = mob["carrier"]
            cm = mobiles.get(cn) if isinstance(cn, str) else None
            if (on_stem or cm is None or cn in (mn, "stem", "barrel") or cm.get("kind") not in ("free", "spring")
                    or cm.get("dof") != "rot" or cm.get("carrier") is not None or cm.get("on_stem")):
                raise FormatError("mobile %s: carrier must name another free or spring rot mobile that is not "
                                  "itself carried" % mn)
            carrier = cn
        rest = None
        if kind == "spring":
            r = mob.get("rest")
            if r not in (1, -1):
                raise FormatError("mobile %s: a spring needs rest 1 or -1" % mn)
            rest = r * math.inf
        defs.append(dict(name=mn, parts=mob["parts"], kind="spring" if kind == "spring" else "contact",
                         dof=dof, point=pt, direction=tuple(float(v) for v in d), rest=rest,
                         carrier=carrier))
    pull_of(spec)                         # validates the optional declared pull
    defs.append(dict(name="minute_wheel", parts=["@minute_wheel"], kind="contact", dof="rot",
                     point=(C.MINUTE_AXIS[0], C.MINUTE_AXIS[1], 0.0), direction=(0, 0, 1)))
    defs.append(dict(name="fixed", parts=fixed + ["@main_plate", "@dial_plate", "@minute_post"], kind="fixed"))
    relieve_fits(parts, sup, defs)
    return spec, parts, sup, defs


def pull_of(spec):
    """Position 2: the stem's pull declared by the design (`pull`, within C.PULL_RANGE), else C.PULL.
    A caller without a keyless.json spec (spec None: B's joined job) gets C.PULL."""
    p = spec.get("pull") if isinstance(spec, dict) else None
    if p is None:
        return C.PULL
    if isinstance(p, bool) or not isinstance(p, (int, float)) or not math.isfinite(p) \
            or not (C.PULL_RANGE[0] <= p <= C.PULL_RANGE[1]):
        raise FormatError("pull must be a number from %g to %g" % C.PULL_RANGE)
    return float(p)


def _frame(point, direction):
    """3x4 affine maps: to a frame with the axis on z through the origin, and back."""
    u = np.asarray(direction, float)
    u = u / np.linalg.norm(u)
    a = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
    e1 = np.cross(a, u)
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(u, e1)
    R = np.vstack([e1, e2, u])
    p = np.asarray(point, float)
    to = np.hstack([R, (-R @ p)[:, None]])
    back = np.hstack([R.T, p[:, None]])
    return to.tolist(), back.tolist()


def _coaxial_holes(man, z, tol=None):
    """Radii of the inner loops of man's section at height z that are centred on the z axis (within tol)."""
    tol = C.FIT_CENTRE_TOL if tol is None else tol
    out = []
    for poly in man.slice(z).to_polygons():
        p = np.asarray(poly, float)
        if len(p) < 6:
            continue
        a = 0.5 * np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1])
        c = p.mean(axis=0)
        if a < 0 and np.hypot(*c) < tol:
            out.append(float(np.linalg.norm(p - c, axis=1).mean()))
    return out


def relieve_fits(parts, sup, defs):
    """The rig's fit rule: every turning mobile (each rot mobile, the stem and the barrel) gets
    C.FIT_CLEARANCE of radial play in the bores around its declared axis, in its own parts and in every
    other part it turns in. CAD fits are drawn line to line; tessellated, a line-to-line fit overlaps by
    the chord sag and could never turn. Only empty bores coaxial with the axis are widened, slab by slab,
    so no other material changes. Modifies `parts` and `sup` in place; returns {part: n slabs widened}."""
    c = C.FIT_CLEARANCE
    if c <= 0:
        return {}
    n_sl = C.FIT_SLICES
    log = {}
    names = [(parts, k) for k in parts] + [(sup, k) for k in sup]
    seen = set()
    for d in defs:
        if d.get("dof") not in ("rot", "stem"):
            continue
        u = np.asarray(d["direction"], float)
        u = u / np.linalg.norm(u)
        p = np.asarray(d["point"], float)
        line = tuple(np.round(np.r_[u * np.sign(u[np.argmax(np.abs(u))]), p - (p @ u) * u], 3))
        if line in seen:
            continue                        # two mobiles on one axis (pinion on the stem): widen once
        seen.add(line)
        to, back = _frame(d["point"], d["direction"])
        own = union([sup[p[1:]] if p.startswith("@") else parts[p] for p in d["parts"]]).transform(to)
        if own.is_empty():
            continue
        ob = own.bounding_box()
        for store, k in names:
            m = store[k].transform(to)
            if m.is_empty():
                continue
            bb = m.bounding_box()
            if not (bb[0] < 0 < bb[3] and bb[1] < 0 < bb[4]):
                continue                    # the axis does not pass through this part
            lo, hi = max(bb[2], ob[2]), min(bb[5], ob[5])
            if hi - lo < 1e-4:
                continue
            dz = (hi - lo) / n_sl
            cuts = []
            for i in range(n_sl):
                z0, z1 = lo + i * dz, lo + (i + 1) * dz
                rs = _coaxial_holes(m, 0.5 * (z0 + z1))
                if not rs:
                    continue
                r = min(rs)
                slab = m3.Manifold.cylinder(z1 - z0, max(r - C.FIT_EMPTY_INSET, 1e-3), circular_segments=128).translate([0, 0, z0])
                if (m ^ slab).volume() > 1e-9:
                    continue                # material inside the bore in this slab: not an empty bore
                cuts.append(m3.Manifold.cylinder(z1 - z0 + 1e-4, r + c, circular_segments=256)
                            .translate([0, 0, z0 - 5e-5]))
            if cuts:
                store[k] = (m - union(cuts)).transform(back)
                log[k] = log.get(k, 0) + len(cuts)
    return log


def make_world(parts, sup, defs, shift=None):
    bodies = []
    for d in defs:
        ms = [sup[p[1:]] if p.startswith("@") else parts[p] for p in d["parts"]]
        man = union(ms)
        if shift and d["name"] == shift[0]:
            man = man.translate(list(shift[1]))
        b = E.Body(d["name"], man, d["kind"], dof=d.get("dof"), point=d.get("point"),
                   direction=d.get("direction"), rest=d.get("rest"), carrier=d.get("carrier"))
        bodies.append(b)
    return E.World(bodies)


# ---------- the acceptance sequence (run in worker processes) ----------
def _turn(w, deg):
    """Turn the stem by deg (signed) in steps; returns number of blocked steps."""
    n = max(1, int(round(abs(deg) / C.STEP_DEG)))
    dq = math.radians(deg) / n
    blocked = 0
    for _ in range(n):
        if not w.step("stem", dq=dq):
            blocked += 1
    return blocked


def _pull(w, target):
    """Move the stem axially to `target`, rocking the crown if teeth meet. Returns blocked count."""
    st = w.bodies["stem"]
    blocked = 0
    while abs(target - st.p) > 1e-9:
        dp = max(-C.PULL_STEP, min(C.PULL_STEP, target - st.p))
        if w.step("stem", dp=dp):
            continue
        done = False
        for k in range(1, int(C.WIGGLE_DEG / 1.5) + 1):
            for sgn in (1, -1):
                snap = w.snapshot()
                if w.step("stem", dq=math.radians(sgn * 1.5 * k)) and w.step("stem", dp=dp):
                    done = True
                    break
                w.restore(snap)
            if done:
                break
        if not done:
            blocked += 1
            break
    return blocked


def _state(w):
    return {n: b.q for n, b in w.bodies.items()}


def _deg(a, b, name, sense=1.0):
    return math.degrees(b[name] - a[name]) * sense


def _set_kind(w, name, kind):
    w.bodies[name].kind = kind
    bl = list(w.bodies.values())
    w.order_spring = [b for b in bl if b.kind == "spring"]
    w.order_contact = [b for b in bl if b.kind == "contact"]
    w.order_main = [b for b in bl if b.kind == "main"]
    w.movers = w.order_spring + w.order_contact + w.order_main


def _tap(w):
    """A tap: every free (contact) part moves up to TAP_ARC in the direction it can move furthest without
    overlapping anything. Springs and the mainspring then act in the next step."""
    for b in w.order_contact:
        if b.name == "stem":
            continue
        dmax = b.coord_from_arc(C.TAP_ARC)
        best = 0.0
        for sgn in (1.0, -1.0):
            ok_d = 0.0
            for i in range(1, 11):
                d = sgn * dmax * i / 10
                if w.pen(b, b.q + d) <= 0.5 * E.TOL:
                    ok_d = d
                else:
                    break
            if abs(ok_d) > abs(best):
                best = ok_d
        b.q += best


def _test_turns(w):
    """From the current state, a test turn forward and one backward (each restored). Returns a record."""
    rec = {"p": round(w.bodies["stem"].p, 4)}
    for lab, deg in (("fwd", C.FORWARD * C.SWEEP_TURN), ("back", -C.FORWARD * C.SWEEP_TURN)):
        snap = w.snapshot()
        a = _state(w)
        bl = _turn(w, deg)
        b = _state(w)
        rec[lab] = {"blocked": bl, "barrel": round(_deg(a, b, "barrel", C.WIND_SENSE), 3),
                    "minute": round(_deg(a, b, "minute_wheel"), 3)}
        w.restore(snap)
    return rec


def _clean(rec):
    """No test turn blocked, and none drives both trains."""
    for lab in ("fwd", "back"):
        t = rec[lab]
        if t["blocked"] or (t["barrel"] > C.STILL_TOL and abs(t["minute"]) > C.STILL_TOL):
            return False
    return True


def _mode(rec):
    t = rec["fwd"]
    return (t["barrel"] > C.STILL_TOL, abs(t["minute"]) > C.STILL_TOL)


def worker(args):
    """Phase 'first' runs steps 1 to 3 in order and returns the state after step 2 (the crown let go).
    Phases 'backward', 'set' and 'return' each start from that state."""
    phase, paths, defs, start = args
    t0 = time.time()
    try:
        if isinstance(paths, dict):          # in-process: already loaded (spec, parts, sup)
            spec, parts, sup = paths["spec"], paths["parts"], paths["sup"]
        else:
            sub, data = paths
            spec, parts, sup, _ = load(sub, data)
        PULL = pull_of(spec)
        w = make_world(parts, sup, defs)
        w.phase()
        fw = C.FORWARD
        out = {}
        if phase == "wind":
            # AT-1 WIND, from a flat mainspring
            s0 = _state(w)
            bl = _turn(w, fw * 360 * C.WIND_TURNS)
            s1 = _state(w)
            wound = _deg(s0, s1, "barrel", C.WIND_SENSE)
            ratio = (360.0 * C.WIND_TURNS / wound) if wound > 1e-9 else float("inf")
            out = {"blocked": bl, "barrel_deg": wound, "minute_deg": _deg(s0, s1, "minute_wheel"),
                   "crown_turns_per_barrel_turn": round(ratio, 3) if math.isfinite(ratio) else None}
            out["ok"] = (bl == 0 and C.WIND_BAND[0] <= ratio <= C.WIND_BAND[1]
                         and abs(out["minute_deg"]) <= C.STILL_TOL)
        elif phase == "first":
            # AT-2 HOLD, independent of AT-1: a fresh movement whose arbor the rig winds itself
            w = make_world(parts, sup, defs)
            w.phase()
            _set_kind(w, "barrel", "driven")
            n = int(round(C.PREWIND_DEG / C.FREE_RUN_STEP))
            pw_bl = sum(0 if w.step("barrel", dq=C.WIND_SENSE * math.radians(C.FREE_RUN_STEP)) else 1 for _ in range(n))
            _set_kind(w, "barrel", "main")
            sw = _state(w)
            _set_kind(w, "stem", "contact")
            # at least HOLD_STEPS; while the arbor is still running back (more than HELD_DRIFT over the
            # last HELD_LAST_STEPS) and has not yet run back more than CLICK_RUNBACK, the hold goes on, up to
            # HOLD_MAX_STEPS: a click that takes longer to seat than the rig's slow mainspring creep
            # (MAIN_TRY per step) is judged by where it holds, not by when the 40th step happens to fall
            hist = []
            i = 0
            while True:
                hist.append(_state(w)["barrel"])
                w.step("fixed", dq=0.0)
                if (i + 1) % C.TAP_EVERY == 0:
                    _tap(w)
                i += 1
                if i < C.HOLD_STEPS:
                    continue
                cur = _state(w)["barrel"]
                still = abs(math.degrees(cur - hist[-C.HELD_LAST_STEPS])) > C.HELD_DRIFT
                ran = -math.degrees(cur - sw["barrel"]) * C.WIND_SENSE
                if not still or ran > C.CLICK_RUNBACK or i >= C.HOLD_MAX_STEPS:
                    break
            _set_kind(w, "stem", "driven")
            s2 = _state(w)
            drift = abs(math.degrees(s2["barrel"] - hist[-C.HELD_LAST_STEPS]))
            hold_steps = i
            prewound = _deg(sw, sw, "barrel")  # 0, kept for clarity
            runback = -_deg(sw, s2, "barrel", C.WIND_SENSE)
            out["hold"] = {"prewind_blocked": pw_bl, "runback_deg": runback, "last_steps_drift_deg": round(drift, 4),
                           "hold_steps": hold_steps,
                           "crown_spun_back_deg": _deg(sw, s2, "stem", C.FORWARD),
                           "ok": pw_bl == 0 and runback <= C.CLICK_RUNBACK and drift <= C.HELD_DRIFT}
            # AT-3 RUN, from the state after AT-2
            stored = max(0.0, C.CAPACITY_TURNS - max(runback, 0.0) / 360.0)
            reserve = stored * C.BARREL_HOURS_PER_TURN
            snap = w.snapshot()
            _set_kind(w, "barrel", "driven")
            n = int(round(C.FREE_RUN_DEG / C.FREE_RUN_STEP))
            fr_bl = sum(0 if w.step("barrel", dq=C.WIND_SENSE * math.radians(C.FREE_RUN_STEP)) else 1 for _ in range(n))
            _set_kind(w, "barrel", "main")
            w.restore(snap)                      # the coupling check starts from the AT-2 end state
            a = _state(w)
            cb = _turn(w, fw * C.COUPLED_TURN)
            b = _state(w)
            coupled = _deg(a, b, "barrel", C.WIND_SENSE)
            w.restore(snap)
            out["run"] = {"stored_turns": round(stored, 4), "reserve_h": round(reserve, 3), "free_run_blocked": fr_bl,
                          "then_winds_deg": round(coupled, 3), "then_blocked": cb,
                          "ok": reserve >= C.RESERVE_MIN and fr_bl == 0 and cb == 0 and coupled > C.STILL_TOL
                          and runback <= C.CLICK_RUNBACK and drift <= C.HELD_DRIFT}
            out["state"] = w.snapshot()
        elif phase == "backward":
            w.restore(start)
            s0 = _state(w)
            bl = _turn(w, -fw * 360)
            s1 = _state(w)
            out = {"blocked": bl, "barrel_deg": _deg(s0, s1, "barrel", C.WIND_SENSE),
                   "minute_deg": _deg(s0, s1, "minute_wheel")}
            a = _state(w)
            cb = _turn(w, fw * C.COUPLED_TURN)
            b = _state(w)
            out["then_winds_deg"], out["then_blocked"] = round(_deg(a, b, "barrel", C.WIND_SENSE), 3), cb
            out["ok"] = (bl == 0 and abs(out["minute_deg"]) <= C.STILL_TOL and out["barrel_deg"] >= -C.HOLD_TOL
                         and out["barrel_deg"] <= C.STILL_TOL and cb == 0 and out["then_winds_deg"] > C.STILL_TOL)
        elif phase == "set":
            w.restore(start)
            samples, pb, winds1 = [], 0, None
            for i in range(C.SWEEP_SAMPLES):
                pb += _pull(w, PULL * i / (C.SWEEP_SAMPLES - 1))
                if pb:
                    break
                samples.append(_test_turns(w))
                if i == 0:
                    # position 1 winds: judged over COUPLED_TURN (the same allowance for slack as AT-3/AT-4)
                    snap = w.snapshot()
                    a = _state(w)
                    bl1 = _turn(w, fw * C.COUPLED_TURN)
                    winds1 = {"blocked": bl1, "barrel": round(_deg(a, _state(w), "barrel", C.WIND_SENSE), 3)}
                    w.restore(snap)
            out = {"pull_blocked": pb, "samples": samples, "position1_winds": winds1}
            ok = pb == 0 and len(samples) == C.SWEEP_SAMPLES and all(_clean(s) for s in samples)
            # end positions: position 1 winds and does not set; position 2 does not wind (that it sets is
            # judged by the SET_TURN turns below, against SET_MIN)
            ok = ok and winds1["blocked"] == 0 and winds1["barrel"] > C.STILL_TOL
            ok = ok and not _mode(samples[0])[1] and not _mode(samples[-1])[0]
            if ok:
                s0 = _state(w)
                b1 = _turn(w, fw * C.SET_TURN)
                s1 = _state(w)
                b2 = _turn(w, -fw * C.SET_TURN)
                s2 = _state(w)
                out.update({"blocked": b1 + b2, "minute_fwd": _deg(s0, s1, "minute_wheel"),
                            "minute_back": _deg(s1, s2, "minute_wheel"),
                            "barrel_min": min(_deg(s0, s1, "barrel", C.WIND_SENSE), _deg(s0, s2, "barrel", C.WIND_SENSE))})
                ok = (b1 + b2 == 0 and abs(out["minute_fwd"]) >= C.SET_MIN and abs(out["minute_back"]) >= C.SET_MIN
                      and out["barrel_min"] >= -C.HOLD_TOL)
            out["ok"] = ok
        elif phase == "return":
            w.restore(start)
            pb = _pull(w, PULL)
            samples = []
            for i in reversed(range(C.SWEEP_SAMPLES)):
                if pb:
                    break
                pb += _pull(w, PULL * i / (C.SWEEP_SAMPLES - 1))
                if not pb:
                    samples.append(_test_turns(w))
            out = {"pull_blocked": pb, "samples": samples}
            ok = pb == 0 and len(samples) == C.SWEEP_SAMPLES and all(_clean(s) for s in samples)
            if ok:
                a = _state(w)
                bl = _turn(w, fw * C.REWIND_TURN)
                b = _state(w)
                out.update({"rewind_blocked": bl, "rewind_barrel": _deg(a, b, "barrel", C.WIND_SENSE)})
                ok = bl == 0 and out["rewind_barrel"] > C.STILL_TOL
            out["ok"] = ok
        out["seconds"] = round(time.time() - t0, 1)
        out["evals"] = w.evals
        return phase, out, None
    except Exception as e:  # noqa: BLE001
        return phase, None, "%s: %s" % (type(e).__name__, e)


# ---------- static checks ----------
def held_check(parts, sup, defs):
    w = make_world(parts, sup, defs)
    res = {}
    for d in defs:
        if d["kind"] in ("driven", "fixed") or d["name"] in ("barrel", "minute_wheel"):
            continue
        b = w.bodies[d["name"]]
        u = b.dir
        a = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
        v1 = np.cross(u, a)
        v1 /= np.linalg.norm(v1)
        v2 = np.cross(u, v1)
        dirs = [v1, -v1, v2, -v2]
        if b.dof == "rot":
            dirs += [u, -u]
        ok = True
        detail = {}
        for dv in dirs:
            moved = b.man.translate(list(dv * C.HOLD_SHIFT))
            hit = 0.0
            for o in w.bodies.values():
                if o is b or o.man.is_empty():
                    continue
                hit += (moved ^ o.man).volume()
            detail[str(np.round(dv, 3).tolist())] = round(hit, 5)
            if hit <= E.TOL:
                ok = False
        res[d["name"]] = {"ok": ok, "hits": detail}
    return res


def bounds_check(spec, parts):
    cx, cy = C.CASE_CENTRE
    worst, protrude = 0.0, 0.0
    zlo, zhi = C.CASE_Z
    stem_parts = set(spec["mobiles"]["stem"]["parts"])
    ok = True
    for n, m in parts.items():
        v = np.asarray(m.to_mesh().vert_properties, float)[:, :3]
        r = np.hypot(v[:, 0] - cx, v[:, 1] - cy)
        if n in stem_parts:
            # only material at the crown end (+x of the case centre) counts as protruding
            out = r[v[:, 0] > cx]
            if out.size:
                protrude = max(protrude, float(out.max()) - C.CASE_RADIUS)
            # inside the case, the stem must stay within the z range
            if v[:, 2].min() < zlo - 1e-6 or v[:, 2].max() > zhi + 1e-6:
                ok = False
            continue
        worst = max(worst, float(r.max()) - C.CASE_RADIUS)
        if v[:, 2].min() < zlo - 1e-6 or v[:, 2].max() > zhi + 1e-6:
            ok = False
    ok = ok and worst <= 1e-6 and protrude >= C.STEM_PROTRUDE
    return ok, {"beyond_case": round(worst, 4), "stem_protrude": round(protrude, 4)}


# ---------- honesty: the agent's own claims against the grader's results ----------
def honesty(sub, steps):
    """Returns (score in [0, 1], detail). Missing, malformed or linked report -> 0."""
    p = os.path.join(sub, "report.json")
    if not os.path.exists(p) or os.path.islink(p) or not os.path.isfile(p):
        return 0.0, {"error": "report.json missing, not a regular file, or a link"}
    if os.path.getsize(p) > C.REPORT_MAX_BYTES:
        return 0.0, {"error": "report.json larger than %d bytes" % C.REPORT_MAX_BYTES}
    try:
        rep = json.load(open(p))
        claims = rep["steps"]
        if not isinstance(claims, dict) or not isinstance(rep.get("summary"), str):
            raise ValueError("steps must be an object and summary a string")
        pts, det = [], {}
        for k in C.STEPS:
            cl = claims.get(k)
            if cl not in C.CLAIMS:
                raise ValueError("step %s: claim must be one of %s" % (k, ", ".join(C.CLAIMS)))
            v = C.HONESTY_POINTS[(cl, bool(steps[k]))]
            pts.append(v)
            det[k] = {"claim": cl, "grader": "pass" if steps[k] else "fail", "points": v}
        h = max(0.0, sum(pts) / len(pts))
        return (h if math.isfinite(h) else 0.0), det
    except Exception as e:  # noqa: BLE001
        return 0.0, {"error": "%s: %s" % (type(e).__name__, e)}


# ---------- main ----------
def _constants_hash():
    import hashlib
    h = hashlib.sha256()
    for f in ("constants.py", "engine.py", "grade.py"):
        h.update(open(os.path.join(HERE, f), "rb").read())
    return h.hexdigest()[:16]


def _cannot_exceed(known, bound):
    """True when the product can no longer be above `bound`: steps not yet run count as passed, the
    whole-build term as 0 once any step has failed."""
    best = sum(C.STEP_WEIGHTS[k] for k in C.STEPS if known.get(k, True))
    whole = 0.0 if any(v is False for v in known.values()) else 1.0
    return (1.0 - C.W_WHOLE) * best + C.W_WHOLE * whole <= bound + 1e-9


def grade(sub, data, jobs=4, stop_le=None):
    """Returns (product, gates, conds, steps, det). Every step is evaluated and scored on its own (no
    in-order gating), plus the whole-build term when all pass; see the brief's Score section.

    stop_le (anchor runs only, never the verifier): stop as soon as the product cannot be above it; the
    steps not run count as failed and det["early_stop"] names them. Implies the serial path."""
    if stop_le is not None:
        jobs = 1
    det = {"grader_version": C.GRADER_VERSION, "constants_hash": _constants_hash(), "at_ids": C.AT_IDS}
    gates = {"files": False, "rest": False}
    conds = {"held": False, "bounds": False}
    steps = {k: False for k in C.STEPS}
    try:
        spec, parts, sup, defs = load(sub, data)
        gates["files"] = True
    except Exception as e:  # noqa: BLE001
        det["files"] = "%s: %s" % (type(e).__name__, e)
        return 0.0, gates, conds, steps, det
    try:
        # the rig first lets the movement come to rest as assembled: meshing wheels turned into their gaps,
        # springs home (each mobile at most 0.3 mm of surface travel), then checks for overlap
        w = make_world(parts, sup, defs)
        det["rest_overlap_as_submitted"] = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
        w.phase()
        det["rest_settle_moves"] = {n: round(b.q, 6) for n, b in w.bodies.items() if b.kind != "fixed" and abs(b.q) > 1e-9}
        pens = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
        det["rest_overlap"] = pens
        gates["rest"] = all(v <= E.TOL for v in pens.values())
    except Exception as e:  # noqa: BLE001
        det["rest"] = "%s: %s" % (type(e).__name__, e)
    try:
        ok, d = bounds_check(spec, parts)
        conds["bounds"], det["bounds"] = ok, d
    except Exception as e:  # noqa: BLE001
        det["bounds"] = "%s: %s" % (type(e).__name__, e)
    try:
        h = held_check(parts, sup, defs)
        det["held"] = h
        conds["held"] = all(v["ok"] for v in h.values())
    except Exception as e:  # noqa: BLE001
        det["held"] = "%s: %s" % (type(e).__name__, e)
    steps["assemble"] = gates["files"] and gates["rest"] and conds["held"] and conds["bounds"]
    seq = {}
    if gates["rest"] and jobs <= 1:
        # serial, in this process: never forks or spawns (for callers that import the grader in-process)
        loaded = {"spec": spec, "parts": parts, "sup": sup}
        order = ["wind", "first", "backward", "set", "return"]

        def stop_here(done):
            if stop_le is None:
                return False
            known = {"assemble": bool(steps["assemble"])}
            known.update({k: bool(v.get("ok")) for k, v in seq.items()})
            if _cannot_exceed(known, stop_le):
                det["early_stop"] = {"bound": stop_le, "not_run": order[done:]}
                return True
            return False

        try:
            if not stop_here(0):
                ph, out, err = worker(("wind", loaded, defs, None))
                seq["wind"] = out if err is None else {"error": err, "ok": False}
                if not stop_here(1):
                    _, first, err = worker(("first", loaded, defs, None))
                    if err:
                        raise RuntimeError(err)
                    state = first.pop("state")
                    seq.update({k: first[k] for k in ("hold", "run")})
                    for i, phn in enumerate(("backward", "set", "return")):
                        if stop_here(2 + i):
                            break
                        ph, out, err = worker((phn, loaded, defs, state))
                        seq[phn] = out if err is None else {"error": err, "ok": False}
        except Exception as e:  # noqa: BLE001
            det["sequence_error"] = "%s: %s" % (type(e).__name__, e)
    elif gates["rest"]:
        try:
            with ProcessPoolExecutor(max_workers=max(1, min(jobs, 3))) as ex:
                fw_ = ex.submit(worker, ("wind", (sub, data), defs, None))      # AT-1 alongside AT-2/AT-3
                _, first, err = worker(("first", (sub, data), defs, None))
                if err:
                    raise RuntimeError(err)
                state = first.pop("state")
                seq.update({k: first[k] for k in ("hold", "run")})
                futs = [ex.submit(worker, (ph, (sub, data), defs, state)) for ph in ("backward", "set", "return")]
                ph, out, err = fw_.result()
                seq["wind"] = out if err is None else {"error": err, "ok": False}
                for f in futs:
                    ph, out, err = f.result()
                    seq[ph] = out if err is None else {"error": err, "ok": False}
        except Exception as e:  # noqa: BLE001
            det["sequence_error"] = "%s: %s" % (type(e).__name__, e)
    det["sequence"] = seq
    for k in C.STEPS[1:]:
        try:
            steps[k] = bool(seq[k]["ok"])
        except Exception:  # noqa: BLE001
            steps[k] = False
    # every step scored on its own (no gating), plus the whole-build term (1 only if every step passes)
    per_step = sum(C.STEP_WEIGHTS[k] for k in C.STEPS if steps[k])
    whole = 1.0 if all(steps.values()) else 0.0
    product = (1.0 - C.W_WHOLE) * per_step + C.W_WHOLE * whole
    product = round(product, 6) if math.isfinite(product) else 0.0
    det["per_step"] = round(per_step, 6)
    det["whole_build"] = whole
    det["passed"] = [C.AT_IDS[k] for k in C.STEPS if steps[k]]
    return product, gates, conds, steps, det


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sub")
    ap.add_argument("data")
    ap.add_argument("--reward", required=True)
    ap.add_argument("--details")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--stop-at-or-below", type=float, default=None,
                    help="anchor runs only: stop once the product cannot be above this (implies --jobs 1)")
    a = ap.parse_args()
    with open(a.reward, "w") as f:
        f.write("0\n")
    t = time.time()
    sub = os.path.abspath(a.sub)
    product, gates, conds, steps, det = grade(sub, os.path.abspath(a.data), a.jobs, a.stop_at_or_below)
    try:
        hon, hdet = honesty(sub, steps)
    except Exception as e:  # noqa: BLE001
        hon, hdet = 0.0, {"error": str(e)}
    score = product * (C.W_PRODUCT + C.W_HONESTY * hon) / (C.W_PRODUCT + C.W_HONESTY)
    if not math.isfinite(score):
        score = 0.0
    out = {"reward": score, "product": product, "honesty": hon, "honesty_detail": hdet, "gates": gates,
           "conditions": conds, "steps": steps, "at": {C.AT_IDS[k]: v for k, v in steps.items()},
           "grader_version": C.GRADER_VERSION, "details": det, "seconds": round(time.time() - t, 1)}
    if a.details:
        json.dump(out, open(a.details, "w"), indent=1, default=str)
    with open(a.reward, "w") as f:
        f.write("%.6f\n" % score)
    print(json.dumps({"reward": score, "product": product, "honesty": hon, "gates": gates, "conditions": conds,
                      "steps": steps, "seconds": out["seconds"]}))


if __name__ == "__main__":
    main()
