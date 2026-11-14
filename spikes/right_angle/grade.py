"""Grader for the right-angle winding spike.

    python -I grade.py SUBMISSION_DIR DATA_DIR --reward REWARD_FILE [--details DETAILS_JSON]

SUBMISSION_DIR holds winding.json and parts/<name>.stl for every named part. DATA_DIR holds
frozen/*.stl (the movement, read-only obstacles), frozen.json and arbor_square.stl.
Opens only named files by absolute path. Never runs submitted code. Writes reward 0 first.
"""
import argparse
import json
import math
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np  # noqa: E402
import manifold3d as m3  # noqa: E402
import constants as C  # noqa: E402


# ---------- small geometry helpers (no spec numbers) ----------
class FormatError(Exception):
    pass


def read_stl(path):
    import struct
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
    if len(man.decompose()) != 1:
        raise FormatError("more than one shell")
    norm = m3.Manifold.batch_boolean([man, man], m3.OpType.Add)
    if abs(norm.volume() - vol) > C.SELF_UNION_TOL * vol:
        raise FormatError("volume changes under self-union")
    return norm


def load(path):
    return to_manifold(read_stl(path))


def union(ms):
    ms = [m for m in ms if m is not None]
    if not ms:
        return m3.Manifold()
    return ms[0] if len(ms) == 1 else m3.Manifold.batch_boolean(ms, m3.OpType.Add)


def bbox_overlap(a, b):
    A, B = a.bounding_box(), b.bounding_box()
    return all(A[i] < B[i + 3] and B[i] < A[i + 3] for i in range(3))


def ivol(a, b):
    if a.is_empty() or b.is_empty() or not bbox_overlap(a, b):
        return 0.0
    v = (a ^ b).volume()
    if not np.isfinite(v):
        raise ArithmeticError("non-finite volume")
    return float(v)


def rot(point, direction, angle):
    u = np.asarray(direction, float)
    u = u / np.linalg.norm(u)
    c, s = math.cos(angle), math.sin(angle)
    K = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    Rm = np.eye(3) + s * K + (1 - c) * K @ K
    p = np.asarray(point, float)
    T = np.eye(4)
    T[:3, :3] = Rm
    T[:3, 3] = p - Rm @ p
    return T


def apply(man, T):
    return man.transform(np.asarray(T)[:3, :4].tolist())


def shift(man, d):
    return man.translate([float(d[0]), float(d[1]), float(d[2])])


def verts(man):
    return np.asarray(man.to_mesh().vert_properties, dtype=np.float64)[:, :3]


def perp_pair(u):
    u = np.asarray(u, float) / np.linalg.norm(u)
    a = np.array([1.0, 0, 0]) if abs(u[0]) < 0.9 else np.array([0, 1.0, 0])
    v = np.cross(u, a)
    v /= np.linalg.norm(v)
    return v, np.cross(u, v)


# ---------- grading ----------
def grade(sub, data):
    det = {}
    gates = {"files": False, "rest_frozen": False}
    checks = {k: False for k in C.WEIGHTS}

    # ----- G1 files and format -----
    try:
        spec = json.load(open(os.path.join(sub, "winding.json")))
        mobiles, fixed, meshes = spec["mobiles"], spec.get("fixed", []), spec["meshes"]
        if not isinstance(mobiles, dict) or not isinstance(fixed, list) or not isinstance(meshes, list):
            raise FormatError("mobiles must be an object, fixed and meshes lists")
        if "stem" not in mobiles or "arbor" not in mobiles:
            raise FormatError("mobiles 'stem' and 'arbor' are required")
        names, owner = [], {}
        for mn, mob in mobiles.items():
            if not re.match(C.NAME_RE, mn):
                raise FormatError("bad mobile name")
            if not mob.get("parts"):
                raise FormatError("mobile %s has no parts" % mn)
            for p in mob["parts"]:
                names.append(p)
                owner[p] = mn
        for p in fixed:
            names.append(p)
            owner[p] = None
        if len(set(names)) != len(names):
            raise FormatError("a part is listed twice")
        for p in names:
            if not isinstance(p, str) or not re.match(C.NAME_RE, p) or p in C.RESERVED:
                raise FormatError("bad part name")
        axes = {}
        for mn, mob in mobiles.items():
            if mn == "arbor":
                axes[mn] = (np.array(C.ARBOR_AXIS[0], float), np.array(C.ARBOR_AXIS[1], float))
                continue
            pt = np.array(mob["point"], float)
            d = np.array(mob["direction"], float)
            if pt.shape != (3,) or d.shape != (3,) or not np.isfinite(pt).all() or not np.isfinite(d).all() \
                    or np.linalg.norm(d) < 1e-9:
                raise FormatError("mobile %s: point and direction must be 3 finite numbers" % mn)
            axes[mn] = (pt, d / np.linalg.norm(d))
        # the stem's axis must be the stated line
        pt, d = axes["stem"]
        if abs(abs(d[0]) - 1) > 1e-6 or abs(pt[1] - C.STEM_Y) > 1e-6 or abs(pt[2] - C.STEM_Z) > 1e-6:
            raise FormatError("stem axis is not the stated line")
        for me in meshes:
            for k in ("driver", "driven"):
                if me.get(k) not in mobiles:
                    raise FormatError("mesh names an unknown mobile")
            for k in ("driver_teeth", "driven_teeth"):
                if not isinstance(me.get(k), int) or not 3 <= me[k] <= 400:
                    raise FormatError("tooth counts must be integers 3..400")
            if me.get("sense") not in ("same", "opposite"):
                raise FormatError("sense must be 'same' or 'opposite'")
            if me["driver"] == me["driven"]:
                raise FormatError("a mesh joins a mobile to itself")
        P = {}
        for p in names:
            P[p] = load(os.path.join(sub, "parts", p + ".stl"))
        gates["files"] = True
    except (FormatError, KeyError, TypeError, ValueError, OSError) as e:
        det["files"] = str(e)
        return gates, checks, det

    frozen_names = json.load(open(os.path.join(data, "frozen.json")))["frozen_parts"]
    F = {n: load(os.path.join(data, "frozen", n + ".stl")) for n in frozen_names}
    square = load(os.path.join(data, "arbor_square.stl"))
    frozen_all = union(list(F.values()))
    body = {mn: union([P[p] for p in mob["parts"]] + ([square] if mn == "arbor" else []))
            for mn, mob in mobiles.items()}
    fixed_all = union([P[p] for p in fixed])
    obstacles = union([fixed_all, frozen_all]) if fixed else frozen_all

    # ----- G2 nothing overlaps the frozen movement at rest -----
    try:
        worst = max([(ivol(P[p], frozen_all), p) for p in names])
        det["rest_frozen"] = {"worst_volume": worst[0], "part": worst[1]}
        gates["rest_frozen"] = worst[0] <= C.MAX_OVERLAP
    except Exception as e:  # noqa: BLE001
        det["rest_frozen"] = "error: %s" % e

    # ----- motion: rates through working meshes -----
    working = []
    det["meshes"] = []
    for me in meshes:
        r = {"pair": "%s/%s" % (me["driver"], me["driven"]), "passes": False}
        try:
            a, b = me["driver"], me["driven"]
            pa, da = axes[a]
            pb, db = axes[b]
            ratio = me["driver_teeth"] / me["driven_teeth"]
            sgn = 1.0 if me["sense"] == "same" else -1.0
            za, zb = me["driver_teeth"], me["driven_teeth"]
            # driver turns +theta (right hand about its declared direction); the driven follows
            n = max(int(C.SAMPLES_PER_TOOTH * za * max(1.0, zb / za)), 24)
            span = 2 * math.pi * max(1.0, zb / za)          # one full turn of the slower of the two
            nudge = C.NUDGE_FRACTION * 2 * math.pi / zb
            worst_over, least_contact, at_over, at_contact = 0.0, float("inf"), None, None
            A0, B0 = body[a], body[b]
            for i in range(n):
                th = span * i / n
                Ta = rot(pa, da, th)
                phi = sgn * ratio * th
                A = apply(A0, Ta)
                B = apply(B0, rot(pb, db, phi))
                ov = ivol(A, B)
                if ov > worst_over:
                    worst_over, at_over = ov, i
                Bn = apply(B0, rot(pb, db, phi - math.copysign(nudge, sgn)))
                ct = ivol(A, Bn)
                if ct < least_contact:
                    least_contact, at_contact = ct, i
                if ov > C.MAX_OVERLAP * 10 and least_contact < C.MIN_CONTACT / 10:
                    break
            r.update({"samples": n, "worst_overlap": worst_over, "at": at_over,
                      "least_contact": least_contact, "contact_at": at_contact})
            r["passes"] = bool(worst_over <= C.MAX_OVERLAP and least_contact >= C.MIN_CONTACT)
        except Exception as e:  # noqa: BLE001
            r["error"] = str(e)
        det["meshes"].append(r)
        if r["passes"]:
            working.append(me)

    rate = {"stem": 1.0}
    for _ in range(len(working) + 1):
        for me in working:
            if me["driver"] in rate and me["driven"] not in rate:
                s = 1.0 if me["sense"] == "same" else -1.0
                rate[me["driven"]] = rate[me["driver"]] * s * me["driver_teeth"] / me["driven_teeth"]
    det["rates"] = rate

    # ----- drive, direction, ratio -----
    try:
        checks["drive"] = "arbor" in rate and all(r["passes"] for r in det["meshes"])
        det["drive"] = {"arbor_reached": "arbor" in rate, "all_declared_meshes_work": all(r["passes"] for r in det["meshes"])}
    except Exception as e:  # noqa: BLE001
        det["drive"] = "error: %s" % e
    try:
        if "arbor" in rate:
            checks["direction"] = rate["arbor"] < 0           # clockwise seen from +z when the stem turns clockwise from outside
            ratio = 1.0 / abs(rate["arbor"])
            det["ratio"] = ratio
            checks["ratio"] = C.RATIO_BAND[0] <= ratio <= C.RATIO_BAND[1]
    except Exception as e:  # noqa: BLE001
        det["ratio"] = "error: %s" % e

    # ----- clear: every mobile spins free of fixed parts and the movement; non-meshing mobiles stay apart -----
    try:
        worst = (0.0, None)
        for mn, (pt, d) in axes.items():
            for i in range(C.SPIN_SAMPLES):
                v = ivol(apply(body[mn], rot(pt, d, 2 * math.pi * i / C.SPIN_SAMPLES)), obstacles)
                if v > worst[0]:
                    worst = (v, "%s spin %d" % (mn, i))
        mesh_pairs = {frozenset((me["driver"], me["driven"])) for me in meshes}
        mobs = list(mobiles)
        r_all = {m: rate.get(m) for m in mobs}
        # coupled motion over one turn of the slowest driven mobile (or 3 stem turns), coarse
        turns = 3.0
        for i in range(48):
            th = 2 * math.pi * turns * i / 48
            pose = {m: apply(body[m], rot(axes[m][0], axes[m][1], th * (r_all[m] if r_all[m] is not None else 0.0)))
                    for m in mobs}
            for x in range(len(mobs)):
                for y in range(x + 1, len(mobs)):
                    if frozenset((mobs[x], mobs[y])) in mesh_pairs:
                        continue
                    v = ivol(pose[mobs[x]], pose[mobs[y]])
                    if v > worst[0]:
                        worst = (v, "%s/%s at %d" % (mobs[x], mobs[y], i))
        # fixed parts against each other
        for x in range(len(fixed)):
            for y in range(x + 1, len(fixed)):
                v = ivol(P[fixed[x]], P[fixed[y]])
                if v > worst[0]:
                    worst = (v, "%s/%s" % (fixed[x], fixed[y]))
        det["clear"] = {"worst_volume": worst[0], "where": worst[1]}
        checks["clear"] = worst[0] <= C.MAX_OVERLAP
    except Exception as e:  # noqa: BLE001
        det["clear"] = "error: %s" % e

    # ----- held: every mobile but the arbor hits a fixed part when moved 0.3 along or across its axis -----
    try:
        held = {}
        for mn, (pt, d) in axes.items():
            if mn == "arbor":
                continue
            v1, v2 = perp_pair(d)
            res = {}
            for nm, vec in (("+axis", d), ("-axis", -d), ("+u", v1), ("-u", -v1), ("+v", v2), ("-v", -v2)):
                res[nm] = ivol(shift(body[mn], vec * C.HOLD_SHIFT), obstacles) > C.MAX_OVERLAP
            held[mn] = res
        det["held"] = held
        checks["held"] = all(all(r.values()) for r in held.values())
    except Exception as e:  # noqa: BLE001
        det["held"] = "error: %s" % e

    # ----- seated: the arbor's parts fill the shell round the square without entering it -----
    try:
        s = C.SQUARE_SIDE / 2
        z0, z1 = C.SQUARE_Z
        sq = m3.Manifold.cube([2 * s, 2 * s, z1 - z0]).translate([-s, -s, z0])
        t = s + C.SEAT_SHELL
        shell = m3.Manifold.cube([2 * t, 2 * t, z1 - z0]).translate([-t, -t, z0]) - sq
        arb = union([P[p] for p in mobiles["arbor"]["parts"]])
        fill = ivol(arb, shell) / shell.volume()
        inside = ivol(arb, sq)
        det["seated"] = {"shell_fill": fill, "inside_square": inside}
        checks["seated"] = fill >= C.SEAT_FILL and inside <= C.MAX_OVERLAP
    except Exception as e:  # noqa: BLE001
        det["seated"] = "error: %s" % e

    # ----- anchored: every fixed part touches the movement, directly or through other fixed parts -----
    try:
        anchored, pending = set(), list(fixed)
        dirs = [np.array(v, float) * C.ANCHOR_SHIFT for v in
                ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]
        changed = True
        while changed and pending:
            changed = False
            base = union([frozen_all] + [P[a] for a in anchored])
            for p in list(pending):
                if any(ivol(shift(P[p], dv), base) > 1e-6 for dv in dirs):
                    anchored.add(p)
                    pending.remove(p)
                    changed = True
        det["anchored"] = {"floating": pending}
        checks["anchored"] = not pending
    except Exception as e:  # noqa: BLE001
        det["anchored"] = "error: %s" % e

    # ----- bounds: inside the case; the stem protrudes -----
    try:
        cc = np.array(C.CASE_CENTRE)
        worst_r, worst_z, stem_out = 0.0, 0.0, -1e9
        for p in names:
            v = verts(P[p])
            r = np.hypot(v[:, 0] - cc[0], v[:, 1] - cc[1])
            dz = max(C.CASE_Z[0] - v[:, 2].min(), v[:, 2].max() - C.CASE_Z[1], 0.0)
            worst_z = max(worst_z, dz)
            if owner[p] == "stem":
                stem_out = max(stem_out, float(r.max()) - C.CASE_RADIUS)
            else:
                worst_r = max(worst_r, float(r.max()) - C.CASE_RADIUS)
        det["bounds"] = {"outside_radius": worst_r, "outside_height": worst_z, "stem_beyond_case": stem_out}
        checks["bounds"] = worst_r <= 0 and worst_z <= 0 and stem_out >= C.STEM_PROTRUDE
    except Exception as e:  # noqa: BLE001
        det["bounds"] = "error: %s" % e
    return gates, checks, det


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("submission")
    ap.add_argument("data")
    ap.add_argument("--reward", required=True)
    ap.add_argument("--details")
    a = ap.parse_args()
    with open(a.reward, "w") as f:
        f.write("0\n")
    t = time.time()
    gates, checks, det = grade(os.path.abspath(a.submission), os.path.abspath(a.data))
    total = sum(C.WEIGHTS.values())
    p = sum(C.WEIGHTS[k] for k, v in checks.items() if v) / total
    reward = p if all(gates.values()) else 0.0
    if not np.isfinite(reward):
        reward = 0.0
    out = {"reward": reward, "p": p, "gates": gates, "checks": checks, "details": det, "seconds": round(time.time() - t, 1)}
    if a.details:
        json.dump(out, open(a.details, "w"), indent=1, default=float)
    with open(a.reward, "w") as f:
        f.write("%.6f\n" % reward)
    print(json.dumps({"reward": reward, "gates": gates, "checks": checks, "seconds": out["seconds"]}))


if __name__ == "__main__":
    main()
