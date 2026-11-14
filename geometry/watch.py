"""Mechanical watch gear train: public engine. The supplied barrel, movement.json,
the mechanical measurements. Units: millimetres. All arbors are parallel to z; the dial side is +z.
Angles are counter-clockwise seen from +z; "clockwise" always means seen from the dial (+z)."""
import json
import math
import os
import re
from fractions import Fraction
import numpy as np
import manifold3d as m3
from . import core
from .core import FormatError, ivol, union

# ---- numbers we chose (all stated to the agent) ----
PRESSURE_ANGLE = 25.0
BARREL_TEETH = 96
BARREL_MODULE = 0.2
BARREL_WHEEL_Z = (0.0, 1.0)
BARREL_ARBOR_Z = (-1.0, 1.6)
BARREL_ARBOR_R = 0.5
BARREL_TURNS_PER_HOUR = Fraction(1, 8)          # clockwise
CASE_RADIUS = 20.7         # reference reaches 20.354 at its largest stage, plus 0.3, rounded up to 0.05
CASE_HEIGHT = 13.4         # reference is 13.1 tall, plus 0.3
# stage 3, change request: the supplied barrel (same mesh) turns clockwise once every 6 hours instead of 8
CHANGED_BARREL_TURNS_PER_HOUR = Fraction(1, 6)
REF_KEPT_SHARE = Fraction(15, 17)   # the reference keeps 15 of the 17 part files it receives at stage 3
VOL_TOL = 0.01              # mm3
SPIN_STEPS = 72             # free-spin test: steps of 5 degrees
HELD_MOVE = 0.3
SAMPLES_PER_TOOTH = 8
ENGAGE_GAP = 0.1            # mm: meshing gears are never further apart than this
DRIVE_FRACTION = 0.25       # of the driver's tooth pitch: backlash must be smaller
CLEAR_STEPS = 144
HAND_REACH = 5.0
COAX_TOL = 0.01
DAY_HAND_REACH = 3.0
DAY_HAND_OFFSET = 6.0       # its axis is at least this far from the hour hand's axis
ASM_STEP = 0.2              # mm any vertex may move between consecutive assembly poses
ASM_MAX_POSES = 1500
ASM_CLEAR = 5.0             # a part starts wholly outside the movement's bounding box grown by this
MIN_FEATURE = 0.2           # smallest printable feature
THIN_VOXEL = 0.05
THIN_ERODE_VOX = 1.5        # ball radius 0.1 on the 0.05 grid, less half a voxel of margin
THIN_DILATE_VOX = 1.0
THIN_DEV = 0.2              # no point of a part may be further than this from what survives the opening
MAX_PARTS = 60
MAX_TRIANGLES = 200_000
MAX_STL_BYTES = 32 * 1024 * 1024
MAX_JSON_BYTES = 1024 * 1024
NAME_RE = re.compile(r"^[A-Za-z0-9_\-]{1,40}$")


# ---------------- supplied barrel and a cylinder helper ----------------
def cyl(x, y, z0, z1, r, seg=48):
    return m3.Manifold.cylinder(z1 - z0, r, r, seg).translate([x, y, z0])


_BARREL = None


def barrel():
    """The supplied mainspring barrel (meshes/barrel.stl): a 96-tooth wheel and its arbor, axis on x = y = 0."""
    global _BARREL
    if _BARREL is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "barrel.stl")
        _BARREL = core.tris_to_manifold(core.read_stl(path, MAX_TRIANGLES, MAX_STL_BYTES))
    return _BARREL


# ---------------- movement ----------------
def rot_about(man, axis_xy, deg):
    return man.translate([-axis_xy[0], -axis_xy[1], 0]).rotate([0, 0, deg]).translate([axis_xy[0], axis_xy[1], 0])


class Movement:
    """A parsed movement: fixed solid, mobiles (name -> solid, axis), meshes, hands."""

    def __init__(self, doc, load_stl):
        if not isinstance(doc, dict):
            raise FormatError("movement.json: top level must be an object")
        cc = doc.get("case_centre")
        if not (isinstance(cc, list) and len(cc) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in cc)):
            raise FormatError("movement.json: 'case_centre' must be [x, y]")
        self.case_centre = (float(cc[0]), float(cc[1]))
        used = set()

        def parts(names, where):
            if not isinstance(names, list) or not names:
                raise FormatError("%s: needs a non-empty list of part files" % where)
            out = []
            for n in names:
                if not isinstance(n, str) or not NAME_RE.match(n):
                    raise FormatError("%s: bad part name %r (letters, digits, _ and - only, no extension)" % (where, n))
                if n in used:
                    raise FormatError("part '%s' is used more than once" % n)
                used.add(n)
                if len(used) > MAX_PARTS:
                    raise FormatError("more than %d parts" % MAX_PARTS)
                out.append(load_stl(n))
            return out
        self.doc = doc
        self.barrel_speed = BARREL_TURNS_PER_HOUR      # the grader sets CHANGED_BARREL_TURNS_PER_HOUR at stage 3
        fixed_names = doc.get("fixed")
        self.fixed_parts = dict(zip(fixed_names if isinstance(fixed_names, list) else [], parts(fixed_names, "fixed")))
        self.fixed = union(list(self.fixed_parts.values()))
        mob = doc.get("mobiles")
        if not isinstance(mob, dict) or not mob:
            raise FormatError("movement.json: 'mobiles' must be a non-empty object")
        self.mobiles = {"barrel": {"axis": (0.0, 0.0), "solid": barrel(), "parts": {}}}
        for name, m in mob.items():
            if not NAME_RE.match(str(name)) or name == "barrel":
                raise FormatError("bad mobile name %r" % (name,))
            ax = m.get("axis") if isinstance(m, dict) else None
            if not (isinstance(ax, list) and len(ax) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in ax)):
                raise FormatError("mobile '%s': 'axis' must be [x, y]" % name)
            names = m.get("parts")
            ps = parts(names, "mobile '%s'" % name)
            self.mobiles[name] = {"axis": (float(ax[0]), float(ax[1])), "solid": union(ps), "parts": dict(zip(names, ps))}
        self.meshes = []
        for i, e in enumerate(doc.get("meshes") or []):
            try:
                a, b, ta, tb = e["driver"], e["driven"], e["driver_teeth"], e["driven_teeth"]
            except (TypeError, KeyError):
                raise FormatError("meshes[%d]: needs driver, driver_teeth, driven, driven_teeth" % i)
            if a not in self.mobiles or b not in self.mobiles or a == b:
                raise FormatError("meshes[%d]: unknown or repeated mobile" % i)
            if not all(isinstance(t, int) and 3 <= t <= 1000 for t in (ta, tb)):
                raise FormatError("meshes[%d]: tooth counts must be integers from 3 to 1000" % i)
            self.meshes.append((a, ta, b, tb))
        self.hands = {}
        hd = doc.get("hands")
        if not isinstance(hd, dict):
            raise FormatError("movement.json: 'hands' must be an object")
        for h in ("hour", "minute", "seconds", "day"):
            e = hd.get(h)
            if h == "day" and e is None:
                continue
            if not isinstance(e, dict) or e.get("mobile") not in self.mobiles or e.get("mobile") == "barrel" \
                    or e.get("part") not in self.mobiles[e["mobile"]]["parts"]:
                raise FormatError("hands.%s: needs 'mobile' and a 'part' that belongs to that mobile" % h)
            self.hands[h] = (e["mobile"], e["part"])

    def posed(self, name, deg=0.0):
        m = self.mobiles[name]
        return m["solid"] if deg == 0.0 else rot_about(m["solid"], m["axis"], deg)

    # ---- arithmetic ----
    def speeds(self):
        """Clockwise turns per hour of every mobile reached from the barrel, as exact fractions.
        Returns (speeds, conflicts). Every declared mesh is external: it reverses direction."""
        w = {"barrel": self.barrel_speed}
        conflicts = []
        changed = True
        while changed:
            changed = False
            for a, ta, b, tb in self.meshes:
                for src, ts, dst, td in ((a, ta, b, tb), (b, tb, a, ta)):
                    if src in w:
                        v = -w[src] * Fraction(ts, td)
                        if dst not in w:
                            w[dst] = v
                            changed = True
                        elif w[dst] != v and (src, dst) not in conflicts and (dst, src) not in conflicts:
                            conflicts.append((src, dst))
        return w, conflicts

    # ---- measurements ----
    def spin(self, name):
        """Largest overlap with the fixed parts while the mobile makes one full turn."""
        worst = (0.0, 0)
        for i in range(SPIN_STEPS):
            v = ivol(self.posed(name, 360.0 * i / SPIN_STEPS), self.fixed)
            if v > worst[0]:
                worst = (v, i)
        return {"worst_volume": worst[0], "step": worst[1], "steps": SPIN_STEPS}

    def held(self, name):
        """Overlap after moving the mobile HELD_MOVE along each axis direction. Sideways moves are
        tested against everything else; up and down only against the fixed parts and mobiles that
        share this mobile's axis (two wheels on different axes must not rest on each other)."""
        ax = self.mobiles[name]["axis"]
        side = union([self.fixed] + [m["solid"] for k, m in self.mobiles.items() if k != name])
        coax = [m["solid"] for k, m in self.mobiles.items()
                if k != name and math.hypot(m["axis"][0] - ax[0], m["axis"][1] - ax[1]) <= COAX_TOL]
        updown = union([self.fixed] + coax)
        out = {}
        for label, d in (("+x", (1, 0, 0)), ("-x", (-1, 0, 0)), ("+y", (0, 1, 0)), ("-y", (0, -1, 0)), ("+z", (0, 0, 1)), ("-z", (0, 0, -1))):
            out[label] = ivol(self.posed(name).translate([c * HELD_MOVE for c in d]), updown if d[2] else side)
        return out

    def fixed_overlap(self):
        """Largest overlap between two fixed parts."""
        names = list(self.fixed_parts)
        worst, pair = 0.0, None
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                v = ivol(self.fixed_parts[names[i]], self.fixed_parts[names[j]])
                if v > worst:
                    worst, pair = v, names[i] + "/" + names[j]
        return worst, pair

    # ---- assembly ----
    def all_parts(self):
        """name -> (solid, group). Parts of one mobile share a group and may pass through each other."""
        out = {"barrel": (self.mobiles["barrel"]["solid"], "mobile:barrel")}
        for n, p in self.fixed_parts.items():
            out[n] = (p, "fixed:" + n)
        for k, m in self.mobiles.items():
            for n, p in m["parts"].items():
                out[n] = (p, "mobile:" + k)
        return out

    def assembly_box(self):
        lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
        for solid, _ in self.all_parts().values():
            bb = np.array(solid.bounding_box())
            lo, hi = np.minimum(lo, bb[:3]), np.maximum(hi, bb[3:])
        return lo - ASM_CLEAR, hi + ASM_CLEAR

    def assembly_replay(self, order, paths):
        """Put the parts in one at a time. Returns per-part results and the list installed cleanly.
        A part is tested against every part placed before it, except parts of its own mobile."""
        parts = self.all_parts()
        lo, hi = self.assembly_box()
        placed, results, installed = [], {}, []
        for name in order:
            solid, group = parts[name]
            P = paths.get(name)
            msgs = _asm_messages(name, solid, P, lo, hi)
            res = {"format_messages": msgs, "worst_volume": None, "pose_index": None, "hit": None,
                   "poses": int(len(P)) if isinstance(P, np.ndarray) and P.ndim == 3 else 0}
            if not msgs:
                worst = (0.0, -1, None)
                for i, T in enumerate(P):
                    mv = core.apply(solid, T)
                    for pn, ps, pg in placed:
                        if pg == group:
                            continue
                        v = ivol(mv, ps)
                        if v > worst[0]:
                            worst = (v, i, pn)
                res.update(worst_volume=worst[0], pose_index=worst[1], hit=worst[2])
                if worst[0] <= VOL_TOL:
                    installed.append(name)
            placed.append((name, solid, group))
            results[name] = res
        return results, installed

    def mesh_run(self, a, ta, b, tb, speeds=None):
        """Turn a declared mesh through max(ta, tb) tooth pitches of the driver. Reports the largest
        overlap, the largest gap, and the smallest overlap produced by pushing the driver
        DRIVE_FRACTION of a tooth pitch further with the driven gear held."""
        n = SAMPLES_PER_TOOTH * max(ta, tb)
        da = 360.0 / (SAMPLES_PER_TOOTH * ta)                 # driver turns counter-clockwise here; the sign is irrelevant
        db = -da * ta / tb
        worst, gap, drive = (0.0, 0), 0.0, float("inf")
        push = DRIVE_FRACTION * 360.0 / ta
        for i in range(n):
            A, B = self.posed(a, da * i), self.posed(b, db * i)
            v = ivol(A, B)
            if v > worst[0]:
                worst = (v, i)
            if i % 4 == 0:
                gap = max(gap, float(A.min_gap(B, 1.0)) if v <= 1e-12 else 0.0)
            if i % 8 == 0:
                drive = min(drive, ivol(self.posed(a, da * i + push), B))
        return {"worst_volume": worst[0], "step": worst[1], "steps": n, "largest_gap": gap, "smallest_drive_overlap": drive}

    def clear_run(self, a, b, wa, wb):
        """Two mobiles that do not mesh, turned together at their own speeds: largest overlap."""
        if not core.bbox_overlap(self._swept_box(a), self._swept_box(b)):
            return {"worst_volume": 0.0, "step": -1}
        wa, wb = float(wa), float(wb)
        ref = max(abs(wa), abs(wb)) or 1.0
        worst = (0.0, -1)
        for i in range(CLEAR_STEPS):
            t = 360.0 * i / CLEAR_STEPS / ref
            v = ivol(self.posed(a, -wa * t), self.posed(b, -wb * t))
            if v > worst[0]:
                worst = (v, i)
        if abs(wa - wb) > 1e-12:                               # also one full relative turn
            for i in range(CLEAR_STEPS):
                t = 360.0 * i / CLEAR_STEPS / abs(wa - wb)
                v = ivol(self.posed(a, -wa * t), self.posed(b, -wb * t))
                if v > worst[0]:
                    worst = (v, CLEAR_STEPS + i)
        return {"worst_volume": worst[0], "step": worst[1]}

    def _swept_box(self, name):
        m = self.mobiles[name]
        V = core.verts(m["solid"])
        r = float(np.hypot(V[:, 0] - m["axis"][0], V[:, 1] - m["axis"][1]).max())
        return core.box((m["axis"][0] - r, m["axis"][1] - r, V[:, 2].min()), (m["axis"][0] + r, m["axis"][1] + r, V[:, 2].max()))

    def extent(self):
        """Largest distance from the case centre reached by anything as it turns, and the z range."""
        rmax, zlo, zhi = 0.0, float("inf"), float("-inf")
        V = core.verts(self.fixed)
        rmax = float(np.hypot(V[:, 0] - self.case_centre[0], V[:, 1] - self.case_centre[1]).max())
        zlo, zhi = float(V[:, 2].min()), float(V[:, 2].max())
        for m in self.mobiles.values():
            V = core.verts(m["solid"])
            r = float(np.hypot(V[:, 0] - m["axis"][0], V[:, 1] - m["axis"][1]).max())
            rmax = max(rmax, r + math.hypot(m["axis"][0] - self.case_centre[0], m["axis"][1] - self.case_centre[1]))
            zlo, zhi = min(zlo, float(V[:, 2].min())), max(zhi, float(V[:, 2].max()))
        return {"radius": rmax, "z_min": zlo, "z_max": zhi}

    def hand_reach(self, hand):
        mob, part = self.hands[hand]
        V = core.verts(self.mobiles[mob]["parts"][part])
        ax = self.mobiles[mob]["axis"]
        return float(np.hypot(V[:, 0] - ax[0], V[:, 1] - ax[1]).max())


def load_movement(folder):
    """folder holds movement.json and parts/<name>.stl. Opens only the files movement.json names."""
    path = os.path.join(folder, "movement.json")
    if os.path.getsize(path) > MAX_JSON_BYTES:
        raise FormatError("movement.json too large")
    with open(path, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except ValueError as e:
            raise FormatError("movement.json is not valid JSON") from e

    def load_stl(name):
        p = os.path.join(folder, "parts", name + ".stl")
        if not os.path.isfile(p):
            raise FormatError("part file parts/%s.stl not found" % name)
        try:
            return core.load_part(p, MAX_TRIANGLES, MAX_STL_BYTES, 0.005)
        except FormatError as e:
            raise FormatError("parts/%s.stl: %s" % (name, e))
    return Movement(doc, load_stl)


def _asm_messages(name, solid, P, lo, hi):
    if not isinstance(P, np.ndarray) or P.ndim != 3 or P.shape[1:] != (4, 4):
        return ["%s: path must be a list of 4x4 matrices" % name]
    if len(P) < 2 or len(P) > ASM_MAX_POSES:
        return ["%s: %d poses (allowed 2 to %d)" % (name, len(P), ASM_MAX_POSES)]
    if not np.isfinite(P).all():
        return ["%s: non-finite number" % name]
    if np.abs(P[:, 3, :] - np.array([0, 0, 0, 1.0])).max() > 1e-6:
        return ["%s: last row of a matrix is not 0 0 0 1" % name]
    R, t = P[:, :3, :3], P[:, :3, 3]
    rtr = np.einsum("nji,njk->nik", R, R) - np.eye(3)
    bad = np.nonzero((np.abs(rtr).max(axis=(1, 2)) > 1e-6) | (np.abs(np.linalg.det(R) - 1) > 1e-6))[0]
    if len(bad):
        return ["%s: pose %d is not a proper rotation plus translation" % (name, bad[0])]
    msgs = []
    V = core.verts(solid)
    Wd = np.einsum("nij,vj->nvi", R, V) + t[:, None, :]
    step = np.linalg.norm(Wd[1:] - Wd[:-1], axis=2).max(axis=1)
    bad = np.nonzero(step > ASM_STEP + 1e-9)[0]
    if len(bad):
        msgs.append("%s: a vertex moves %.4f between poses %d and %d (limit %.2f)" % (name, step[bad[0]], bad[0], bad[0] + 1, ASM_STEP))
    a, b = Wd[0].min(axis=0), Wd[0].max(axis=0)
    if not ((b < lo) | (a > hi)).any():
        msgs.append("%s: first pose is not wholly outside the movement's bounding box grown by %.1f" % (name, ASM_CLEAR))
    if np.abs(P[-1] - np.eye(4)).max() > 1e-6:
        msgs.append("%s: last pose is not the identity (parts are given in their assembled position)" % name)
    return msgs


def load_assembly(folder, movement):
    """assembly.json: {"order": [every part name and "barrel"], "paths": {name: [4x4, ...]}}"""
    path = os.path.join(folder, "assembly.json")
    if os.path.getsize(path) > 64 * 1024 * 1024:
        raise FormatError("assembly.json too large")
    with open(path, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except ValueError as e:
            raise FormatError("assembly.json is not valid JSON") from e
    if not isinstance(doc, dict) or not isinstance(doc.get("order"), list) or not isinstance(doc.get("paths"), dict):
        raise FormatError("assembly.json: needs a list 'order' and an object 'paths'")
    names = set(movement.all_parts())
    order = []
    for n in doc["order"]:
        if n in names and n not in order:
            order.append(n)
    paths = {}
    for n in order:
        try:
            paths[n] = np.array(doc["paths"].get(n), dtype=np.float64)
        except (ValueError, TypeError):
            paths[n] = None
    return order, paths


def thin(part):
    """Open the part with a ball of radius MIN_FEATURE / 2 on a THIN_VOXEL grid. Returns
    (pieces left, largest distance in mm from the part to what is left). Paper-thin walls vanish."""
    h = THIN_VOXEL
    bb = np.array(part.bounding_box())
    lo = np.floor(bb[:3] / h).astype(int) - 2
    hi = np.ceil(bb[3:] / h).astype(int) + 2
    solid = core.voxelize(part, lo * h - 0.0137, tuple(int(v) for v in hi - lo), h)
    n, dev = core.opening_test(solid, THIN_ERODE_VOX, THIN_DILATE_VOX)
    return n, (dev * h if np.isfinite(dev) else 1e9)
