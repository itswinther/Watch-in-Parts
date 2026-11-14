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
        if not isinstance(mn, str) or not re.match(C.NAME_RE, mn) or mn in ("minute_wheel",):
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
        rest = None
        if kind == "spring":
            r = mob.get("rest")
            if r not in (1, -1):
                raise FormatError("mobile %s: a spring needs rest 1 or -1" % mn)
            rest = r * math.inf
        defs.append(dict(name=mn, parts=mob["parts"], kind="spring" if kind == "spring" else "contact",
                         dof=dof, point=pt, direction=tuple(float(v) for v in d), rest=rest,
                         carrier="stem" if on_stem else None))
    defs.append(dict(name="minute_wheel", parts=["@minute_wheel"], kind="contact", dof="rot",
                     point=(C.MINUTE_AXIS[0], C.MINUTE_AXIS[1], 0.0), direction=(0, 0, 1)))
    defs.append(dict(name="fixed", parts=fixed + ["@main_plate", "@dial_plate", "@minute_post"], kind="fixed"))
    return spec, parts, sup, defs


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


# ---------- scenarios (run in worker processes) ----------
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


def scenario(args):
    name, parts_paths, defs = args
    sub, data = parts_paths
    t0 = time.time()
    try:
        spec, parts, sup, _ = load(sub, data)
        w = make_world(parts, sup, defs)
        w.settle()
        fw = C.FORWARD
        out = {}
        if name == "wind":
            s0 = _state(w)
            out["blocked"] = _turn(w, fw * 360)
            s1 = _state(w)
            out["barrel_deg"] = _deg(s0, s1, "barrel", C.WIND_SENSE)
            out["minute_deg"] = _deg(s0, s1, "minute_wheel")
        elif name == "slip":
            s0 = _state(w)
            out["blocked"] = _turn(w, -fw * 360)
            s1 = _state(w)
            out["barrel_deg"] = _deg(s0, s1, "barrel", C.WIND_SENSE)
            out["minute_deg"] = _deg(s0, s1, "minute_wheel")
        elif name == "set":
            out["pull_blocked"] = _pull(w, C.PULL)
            s0 = _state(w)
            out["blocked_fwd"] = _turn(w, fw * 180)
            s1 = _state(w)
            out["blocked_back"] = _turn(w, -fw * 180)
            s2 = _state(w)
            out["minute_fwd_deg"] = _deg(s0, s1, "minute_wheel")
            out["minute_back_deg"] = _deg(s1, s2, "minute_wheel")
            out["barrel_deg"] = _deg(s0, s2, "barrel", C.WIND_SENSE)
            out["barrel_min_deg"] = min(0.0, _deg(s0, s1, "barrel", C.WIND_SENSE), out["barrel_deg"])
        elif name == "sweep":
            samples = []
            ps = [C.PULL * i / (C.SWEEP_SAMPLES - 1) for i in range(C.SWEEP_SAMPLES)]
            pull_blocked = 0
            for p in ps:
                pull_blocked += _pull(w, p)
                if pull_blocked:
                    break
                rec = {"p": round(w.bodies["stem"].p, 4)}
                for lab, deg in (("fwd", C.FORWARD * C.SWEEP_TURN), ("back", -C.FORWARD * C.SWEEP_TURN)):
                    snap = w.snapshot()
                    a = _state(w)
                    bl = _turn(w, deg)
                    b = _state(w)
                    rec[lab] = {"blocked": bl, "barrel": round(_deg(a, b, "barrel", C.WIND_SENSE), 3),
                                "minute": round(_deg(a, b, "minute_wheel"), 3)}
                    w.restore(snap)
                samples.append(rec)
            out["samples"] = samples
            out["pull_blocked"] = pull_blocked
            # back to position 1, then it must wind again
            if not pull_blocked:
                out["return_blocked"] = _pull(w, 0.0)
                a = _state(w)
                out["after_return_blocked"] = _turn(w, C.FORWARD * C.SWEEP_TURN)
                b = _state(w)
                out["after_return_barrel"] = _deg(a, b, "barrel", C.WIND_SENSE)
        out["seconds"] = round(time.time() - t0, 1)
        out["evals"] = w.evals
        return name, out, None
    except Exception as e:  # noqa: BLE001
        return name, None, "%s: %s" % (type(e).__name__, e)


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
            protrude = max(protrude, float(r.max()) - C.CASE_RADIUS)
            # inside the case, the stem must stay within the z range
            if v[:, 2].min() < zlo - 1e-6 or v[:, 2].max() > zhi + 1e-6:
                ok = False
            continue
        worst = max(worst, float(r.max()) - C.CASE_RADIUS)
        if v[:, 2].min() < zlo - 1e-6 or v[:, 2].max() > zhi + 1e-6:
            ok = False
    ok = ok and worst <= 1e-6 and protrude >= C.STEM_PROTRUDE
    return ok, {"beyond_case": round(worst, 4), "stem_protrude": round(protrude, 4)}


# ---------- main ----------
def grade(sub, data, jobs=4):
    det = {}
    gates = {"files": False, "rest": False}
    checks = {k: False for k in C.WEIGHTS}
    try:
        spec, parts, sup, defs = load(sub, data)
        gates["files"] = True
    except Exception as e:  # noqa: BLE001
        det["files"] = "%s: %s" % (type(e).__name__, e)
        return 0.0, gates, checks, det
    try:
        w = make_world(parts, sup, defs)
        pens = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
        det["rest_overlap"] = pens
        gates["rest"] = all(v <= E.TOL for v in pens.values())
    except Exception as e:  # noqa: BLE001
        det["rest"] = "%s: %s" % (type(e).__name__, e)
    if not all(gates.values()):
        return 0.0, gates, checks, det
    try:
        ok, d = bounds_check(spec, parts)
        checks["bounds"], det["bounds"] = ok, d
    except Exception as e:  # noqa: BLE001
        det["bounds"] = "%s: %s" % (type(e).__name__, e)
    try:
        h = held_check(parts, sup, defs)
        det["held"] = h
        checks["held"] = all(v["ok"] for v in h.values())
    except Exception as e:  # noqa: BLE001
        det["held"] = "%s: %s" % (type(e).__name__, e)
    names = ["sweep", "set", "wind", "slip"]
    args = [(n, (sub, data), defs) for n in names]
    res = {}
    with ProcessPoolExecutor(max_workers=max(1, min(jobs, 4))) as ex:
        for n, out, err in ex.map(scenario, args):
            res[n] = out if err is None else {"error": err}
    det["scenarios"] = res
    lo, hi = 360.0 / C.WIND_BAND[1], 360.0 / C.WIND_BAND[0]
    try:
        r = res["wind"]
        checks["wind"] = r["blocked"] == 0 and lo <= r["barrel_deg"] <= hi and abs(r["minute_deg"]) <= C.STILL_TOL
    except Exception:  # noqa: BLE001
        pass
    try:
        r = res["slip"]
        checks["slip"] = r["blocked"] == 0 and abs(r["minute_deg"]) <= C.STILL_TOL and r["barrel_deg"] <= C.HOLD_TOL
    except Exception:  # noqa: BLE001
        pass
    try:
        r1, r2 = res["slip"], res["set"]
        checks["click"] = r1["barrel_deg"] >= -C.HOLD_TOL and r2["barrel_min_deg"] >= -C.HOLD_TOL
    except Exception:  # noqa: BLE001
        pass
    try:
        r = res["set"]
        need = C.SET_MIN / 2
        checks["set"] = (r["pull_blocked"] == 0 and r["blocked_fwd"] == 0 and r["blocked_back"] == 0
                         and abs(r["minute_fwd_deg"]) >= need and abs(r["minute_back_deg"]) >= need
                         and abs(r["barrel_deg"]) <= C.HOLD_TOL)
    except Exception:  # noqa: BLE001
        pass
    try:
        r = res["sweep"]
        ok = r["pull_blocked"] == 0 and r.get("return_blocked", 1) == 0 and r.get("after_return_blocked", 1) == 0
        ok = ok and r.get("after_return_barrel", 0) > C.STILL_TOL
        modes = []
        for s in r["samples"]:
            for lab in ("fwd", "back"):
                t = s[lab]
                wind = t["barrel"] > C.STILL_TOL
                setm = abs(t["minute"]) > C.STILL_TOL
                if t["blocked"] or (wind and setm):
                    ok = False
            modes.append((s["fwd"]["barrel"] > C.STILL_TOL, abs(s["fwd"]["minute"]) > C.STILL_TOL))
        if len(modes) != C.SWEEP_SAMPLES or modes[0] != (True, False) or modes[-1] != (False, True):
            ok = False
        checks["sweep"] = ok
    except Exception:  # noqa: BLE001
        pass
    tot = sum(C.WEIGHTS.values())
    score = sum(C.WEIGHTS[k] for k, v in checks.items() if v) / tot
    for v in [score]:
        if not math.isfinite(v):
            return 0.0, gates, checks, det
    return score, gates, checks, det


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sub")
    ap.add_argument("data")
    ap.add_argument("--reward", required=True)
    ap.add_argument("--details")
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args()
    with open(a.reward, "w") as f:
        f.write("0\n")
    t = time.time()
    score, gates, checks, det = grade(os.path.abspath(a.sub), os.path.abspath(a.data), a.jobs)
    out = {"reward": score, "gates": gates, "checks": checks, "details": det, "seconds": round(time.time() - t, 1)}
    if a.details:
        json.dump(out, open(a.details, "w"), indent=1, default=str)
    with open(a.reward, "w") as f:
        f.write("%.6f\n" % score)
    print(json.dumps({"reward": score, "gates": gates, "checks": checks, "seconds": out["seconds"]}))


if __name__ == "__main__":
    main()
