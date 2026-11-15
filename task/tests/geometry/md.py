"""Moving Day: public engine. Apartment, furniture, rules, replay and score.
Everything here may be shipped to the agent; the only secret is the reference paths.
Units: centimetres. +Z is up."""
import json
import os
import numpy as np
from . import core
from .core import box, union, apply, ivol, FormatError

MAX_STEP = 5.0            # cm any vertex may move between consecutive poses
MAX_POSES = 4000
VOL_TOL = 1.0             # cm3 a pose may overlap the apartment or a delivered piece
ROT_TOL = 1e-6
FINAL_TOL = 1e-6
MAX_JSON_BYTES = 32 * 1024 * 1024


class Instance:
    """block: outer solid box. air: boxes carved out of it. staging: box outside the
    front door. pieces: name -> {"boxes": [...], "final": 4x4, "weight": w} with the
    boxes in the piece's own frame. listed: the order pieces are listed to the agent."""

    def __init__(self, name, block, air, staging, pieces, listed):
        self.name, self.block, self.air, self.staging, self.pieces, self.listed = name, block, air, staging, pieces, listed

    def apartment(self):
        return box(*self.block) - union([box(*a) for a in self.air.values()])

    def piece(self, name):
        if name not in self.pieces:
            raise FormatError("unknown piece '%s'" % name)
        return union([box(*b) for b in self.pieces[name]["boxes"]])

    def final(self, name):
        return np.array(self.pieces[name]["final"], dtype=float)

    def weight(self, name):
        return self.pieces[name]["weight"]


def rot(axis, deg):
    c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
    R = {"x": [[1, 0, 0], [0, c, -s], [0, s, c]], "y": [[c, 0, s], [0, 1, 0], [-s, 0, c]], "z": [[c, -s, 0], [s, c, 0], [0, 0, 1]]}[axis]
    T = np.eye(4)
    T[:3, :3] = R
    return T


def trans(t):
    T = np.eye(4)
    T[:3, 3] = t
    return T


def flat_one():
    """Instance "flat-1"."""
    air = {
        "front_door": ((0, 630, 0), (20, 716, 205)),
        "hall": ((20, 480, 0), (170, 720, 258)),
        "corridor_west": ((170, 595, 0), (300, 720, 258)),
        "corridor_doorway": ((300, 595, 0), (320, 720, 205)),
        "corridor_east": ((320, 595, 0), (700, 720, 258)),
        "corridor_south": ((575, 300, 0), (700, 720, 258)),
        "living_room": ((420, 30, 0), (880, 300, 258)),
        "bedroom_door": ((60, 460, 0), (146, 480, 205)),
        "bedroom": ((20, 200, 0), (390, 460, 238)),
    }
    pieces = {
        "bookcase": {"boxes": [((0, 0, 0), (100, 55, 200))], "final": trans((400, 595, 0)), "weight": 1},
        "chest": {"boxes": [((0, 0, 0), (80, 50, 90))], "final": trans((63, 400, 0)), "weight": 1},
        "wardrobe": {"boxes": [((0, 0, 0), (60, 45, 232))], "final": trans((70, 210, 0)) @ rot("z", 90), "weight": 3},
        "sofa": {"boxes": [((0, 0, 0), (240, 90, 80)), ((0, 0, 0), (90, 160, 80))], "final": trans((520, 40, 0)), "weight": 4},
    }
    return Instance("flat-1", ((0, 0, -20), (900, 740, 280)), air, ((-420, 480, 0), (-20, 860, 300)),
                    pieces, ["bookcase", "chest", "wardrobe", "sofa"])


INSTANCES = {"flat-1": flat_one}


# ---------------- plan file ----------------
def parse_plan(doc, inst):
    """Returns (order, paths, notes). Raises FormatError only if the file as a whole is unusable."""
    if not isinstance(doc, dict) or not isinstance(doc.get("order"), list) or not isinstance(doc.get("paths"), dict):
        raise FormatError("top level must be an object with a list 'order' and an object 'paths'")
    order, notes, seen = [], [], set()
    for n in doc["order"]:
        if not isinstance(n, str) or n not in inst.pieces:
            notes.append("order: unknown name %r ignored" % (n,))
        elif n in seen:
            notes.append("order: '%s' listed more than once, later entry ignored" % n)
        else:
            seen.add(n)
            order.append(n)
    paths = {}
    for n in order:
        poses = doc["paths"].get(n)
        try:
            arr = np.array(poses, dtype=np.float64)
        except (ValueError, TypeError):
            arr = None
        paths[n] = arr
    return order, paths, notes


def load_plan(path, inst):
    if os.path.getsize(path) > MAX_JSON_BYTES:
        raise FormatError("plan larger than %d bytes" % MAX_JSON_BYTES)
    with open(path, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except ValueError as e:
            raise FormatError("plan is not valid JSON") from e
    return parse_plan(doc, inst)


def path_messages(inst, name, P):
    """Format rules for one path. Empty list means the path is well formed."""
    if P is None or P.ndim != 3 or P.shape[1:] != (4, 4):
        return ["%s: path must be a list of 4x4 matrices" % name]
    if len(P) < 2 or len(P) > MAX_POSES:
        return ["%s: %d poses (allowed 2 to %d)" % (name, len(P), MAX_POSES)]
    if not np.isfinite(P).all():
        return ["%s: non-finite number" % name]
    msgs = []
    R, t = P[:, :3, :3], P[:, :3, 3]
    if np.abs(P[:, 3, :] - np.array([0, 0, 0, 1.0])).max() > ROT_TOL:
        return ["%s: last row of a matrix is not 0 0 0 1" % name]
    rtr = np.einsum("nji,njk->nik", R, R) - np.eye(3)
    bad = np.nonzero((np.abs(rtr).max(axis=(1, 2)) > ROT_TOL) | (np.abs(np.linalg.det(R) - 1) > ROT_TOL))[0]
    if len(bad):
        return ["%s: pose %d is not a proper rotation plus translation" % (name, bad[0])]
    V = core.verts(inst.piece(name))
    W = np.einsum("nij,vj->nvi", R, V) + t[:, None, :]
    step = np.linalg.norm(W[1:] - W[:-1], axis=2).max(axis=1)
    bad = np.nonzero(step > MAX_STEP + 1e-9)[0]
    if len(bad):
        msgs.append("%s: a vertex moves %.3f between poses %d and %d (limit %.1f)" % (name, step[bad[0]], bad[0], bad[0] + 1, MAX_STEP))
    lo, hi = np.array(inst.staging[0]), np.array(inst.staging[1])
    if (W[0] < lo - 1e-9).any() or (W[0] > hi + 1e-9).any():
        msgs.append("%s: first pose is not wholly inside the staging box" % name)
    if np.abs(P[-1] - inst.final(name)).max() > FINAL_TOL:
        msgs.append("%s: last pose is not the given final pose" % name)
    return msgs


def replay(inst, order, paths):
    """Carry the pieces in, in order. Returns per-piece results and the delivered list."""
    apartment = inst.apartment()
    placed = {"apartment": apartment}
    results, delivered = {}, []
    for name in order:
        P = paths[name]
        msgs = path_messages(inst, name, P)
        res = {"format_messages": msgs, "worst_volume": None, "pose_index": None, "hit": None,
               "poses": int(len(P)) if P is not None and P.ndim == 3 else 0}
        if not msgs:
            body = inst.piece(name)
            worst = (0.0, -1, None)
            for i, T in enumerate(P):
                mv = apply(body, T)
                for pname, pm in placed.items():
                    v = ivol(mv, pm)
                    if v > worst[0]:
                        worst = (v, i, pname)
            res.update(worst_volume=worst[0], pose_index=worst[1], hit=worst[2])
            if worst[0] <= VOL_TOL:
                delivered.append(name)
                placed[name] = apply(body, inst.final(name))
        results[name] = res
    return results, delivered


def score(inst, delivered):
    total = sum(inst.weight(n) for n in inst.pieces)
    p = sum(inst.weight(n) for n in delivered) / total
    allin = len(delivered) == len(inst.pieces)
    return 0.5 * p * p + 0.5 * (1.0 if allin else 0.0), p


def grade(plan_path, instance="flat-1"):
    inst = INSTANCES[instance]()
    out = {"reward": 0.0, "p": 0.0, "delivered": [], "pieces": {}, "notes": []}
    try:
        order, paths, notes = load_plan(plan_path, inst)
    except (FormatError, OSError) as e:
        out["notes"] = ["plan rejected: %s" % e]
        return out
    try:
        results, delivered = replay(inst, order, paths)
    except Exception as e:      # noqa: never crash the grader
        out["notes"] = notes + ["replay failed: %s: %s" % (type(e).__name__, e)]
        return out
    S, p = score(inst, delivered)
    if not np.isfinite(S):
        S = 0.0
    out.update(reward=float(S), p=float(p), delivered=delivered, pieces=results, notes=notes)
    return out
