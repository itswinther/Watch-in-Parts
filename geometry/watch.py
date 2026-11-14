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
MESH_SHIFT = 0.03           # mm: tolerant test, the driven mobile moved this far away from and towards the driver's axis
MESH_CUT_MARGIN = 1.05      # mm, private speed-up of mesh_run: material further than this from the other mobile's reach
                            # is cut away before stepping (must exceed the 1.0 search length of min_gap in mesh_run)
MESH_GAP_SEARCH = 0.15      # mm, private speed-up of mesh_run: gaps are searched this far first, then to 1.0 if none found
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
# mass budget, mm3. PLACEHOLDERS: 50 % of the current reference's fixed volume (4233.68, stage 1) and 60 % of its
# mobile volume (853.19, stage 2); builder REF replaces them with the reworked reference's values plus 10 %.
FIXED_VOLUME_MAX = 346.0    # union of the fixed parts (reference at its largest stage 313.8, plus 10 percent)
MOBILE_VOLUME_MAX = 278.0   # reference 252.1 at stages 2 and 3, plus 10 percent; sum of the volumes of every part of every mobile, the supplied barrel not counted
MAX_PARTS = 60
MAX_TRIANGLES = 200_000
MAX_STL_BYTES = 32 * 1024 * 1024
MAX_JSON_BYTES = 1024 * 1024
NAME_RE = re.compile(r"^[A-Za-z0-9_\-]{1,40}$")
# STEP parts (read with OpenCASCADE, tessellated, then treated exactly like an STL)
MAX_STEP_BYTES = 16 * 1024 * 1024
STEP_LINEAR_DEFLECTION = 0.001  # mm, absolute chordal deviation of the tessellation
STEP_ANGULAR_DEFLECTION = 0.1   # radians
STEP_MAX_TRIANGLE_FACES = 500   # more flat three-edged faces than this: a faceted mesh, rejected
STEP_TIMEOUT_S = 120            # per STEP file, read and tessellation, in a child process
STEP_MEMORY_MB = 4096           # address-space limit of that child process
SELF_UNION_TOL = 0.005          # relative volume change allowed under self-union
MAX_SCRIPTS_BYTES = 4 * 1024 * 1024   # scripts/ copied with a submission (never opened by the grader)
MAX_SCRIPT_FILES = 200
MAX_ASSEMBLY_BYTES = 64 * 1024 * 1024
MIN_TEETH, MAX_TEETH = 3, 1000       # tooth counts declared in meshes (Movement.__init__ still types 3 and 1000 inline)
MAX_NAME_LEN = 40                    # the {1,40} of NAME_RE


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
                if n == "barrel":
                    raise FormatError("%s: 'barrel' is reserved for the supplied barrel and cannot be a part name" % where)
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
    def speeds(self, meshes=None):
        """Clockwise turns per hour of every mobile reached from the barrel, as exact fractions.
        Returns (speeds, conflicts). Every declared mesh is external: it reverses direction.
        meshes: the meshes to follow (default: every declared mesh)."""
        w = {"barrel": self.barrel_speed}
        conflicts = []
        changed = True
        while changed:
            changed = False
            for a, ta, b, tb in (self.meshes if meshes is None else meshes):
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
    # ---- parts of one mobile: no overlap, and each seated on the rest ----
    def mobile_overlap(self):
        """Largest overlap between two parts of the same mobile: (volume, 'mobile:a/b')."""
        worst, pair = 0.0, None
        for k, mo in self.mobiles.items():
            names = list(mo["parts"])
            for i in range(len(names)):
                for j in range(i + 1, len(names)):
                    v = ivol(mo["parts"][names[i]], mo["parts"][names[j]])
                    if v > worst:
                        worst, pair = v, "%s:%s/%s" % (k, names[i], names[j])
        return worst, pair

    def seated(self, name):
        """Each part of a mobile with more than one part, moved HELD_MOVE along each axis direction:
        its overlap with the other parts of that mobile. {} for a one-part mobile."""
        parts = self.mobiles[name]["parts"]
        if len(parts) < 2:
            return {}
        out = {}
        for pn, ps in parts.items():
            rest = union([q for qn, q in parts.items() if qn != pn])
            out[pn] = {label: ivol(ps.translate([c * HELD_MOVE for c in d]), rest) for label, d in
                       (("+x", (1, 0, 0)), ("-x", (-1, 0, 0)), ("+y", (0, 1, 0)), ("-y", (0, -1, 0)), ("+z", (0, 0, 1)), ("-z", (0, 0, -1)))}
        return out

    def all_parts(self):
        """name -> (solid, group). Parts of one mobile share a group and may pass through each other."""
        out = {"barrel": (self.mobiles["barrel"]["solid"], "mobile:barrel")}
        for n, p in self.fixed_parts.items():
            out[n] = (p, "fixed:" + n)
        for k, m in self.mobiles.items():
            for n, p in m["parts"].items():
                out[n] = (p, "mobile:" + k)
        return out

    def volumes(self):
        """(volume of the union of the fixed parts, sum of the volumes of every part of every mobile
        except the supplied barrel), in mm3, of the solids built from the part files."""
        mobile = sum(p.volume() for k, mo in self.mobiles.items() if k != "barrel" for p in mo["parts"].values())
        return float(self.fixed.volume()), float(mobile)

    def assembly_box(self):
        lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
        for solid, _ in self.all_parts().values():
            bb = np.array(solid.bounding_box())
            lo, hi = np.minimum(lo, bb[:3]), np.maximum(hi, bb[3:])
        return lo - ASM_CLEAR, hi + ASM_CLEAR

    def assembly_replay(self, order, paths):
        """Put the parts in one at a time. Returns per-part results and the list installed cleanly.
        A part is tested against every part placed before it, parts of its own mobile included.
        A part missing from `order` stands in its assembled position from the start and is not installed."""
        parts = self.all_parts()
        lo, hi = self.assembly_box()
        placed = [(n, solid, group) for n, (solid, group) in parts.items() if n not in order]
        results, installed = {n: {"not_in_order": True} for n, _, _ in placed}, []
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
                        v = ivol(mv, ps)
                        if v > worst[0]:
                            worst = (v, i, pn)
                res.update(worst_volume=worst[0], pose_index=worst[1], hit=worst[2])
                if worst[0] <= VOL_TOL:
                    installed.append(name)
            placed.append((name, solid, group))
            results[name] = res
        return results, installed

    def mesh_run(self, a, ta, b, tb, speeds=None, shift=0.0, cut=True):
        """Turn a declared mesh through max(ta, tb) tooth pitches of the driver. Reports the largest
        overlap, the largest gap, and the smallest overlap produced by pushing the driver
        DRIVE_FRACTION of a tooth pitch further with the driven gear held.
        shift: the driven mobile (and its axis) is first moved this far straight away from the driver's
        axis (negative: towards it); same steps and angles. cut=False skips the speed-up (same results)."""
        A, ax_a = self.mobiles[a]["solid"], self.mobiles[a]["axis"]
        B, ax_b = self.mobiles[b]["solid"], self.mobiles[b]["axis"]
        if shift:
            dx, dy = ax_b[0] - ax_a[0], ax_b[1] - ax_a[1]
            d = math.hypot(dx, dy)
            ux, uy = (dx / d, dy / d) if d > 1e-12 else (1.0, 0.0)
            B = B.translate([shift * ux, shift * uy, 0.0])
            ax_b = (ax_b[0] + shift * ux, ax_b[1] + shift * uy)
        if cut:
            A2, B2 = _near_cut(A, ax_a, B, ax_b), _near_cut(B, ax_b, A, ax_a)
            if not (A2.is_empty() or B2.is_empty()):      # nothing within reach: keep the whole solids
                A, B = A2, B2
        pa = lambda deg: A if deg == 0.0 else rot_about(A, ax_a, deg)
        pb = lambda deg: B if deg == 0.0 else rot_about(B, ax_b, deg)
        n = SAMPLES_PER_TOOTH * max(ta, tb)
        da = 360.0 / (SAMPLES_PER_TOOTH * ta)                 # driver turns counter-clockwise here; the sign is irrelevant
        db = -da * ta / tb
        worst, gap, drive = (0.0, 0), 0.0, float("inf")
        push = DRIVE_FRACTION * 360.0 / ta
        for i in range(n):
            Ai, Bi = pa(da * i), pb(db * i)
            v = ivol(Ai, Bi)
            if v > worst[0]:
                worst = (v, i)
            if i % 4 == 0 and v <= 1e-12:
                g = Ai.min_gap(Bi, MESH_GAP_SEARCH)       # exact below the short search length, and much faster
                gap = max(gap, float(g if g < MESH_GAP_SEARCH else Ai.min_gap(Bi, 1.0)))
            if i % 8 == 0:
                drive = min(drive, ivol(pa(da * i + push), Bi))
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


def _near_cut(S, ax, O, ax_o):
    """S (turning about ax) without the material that can never come within MESH_CUT_MARGIN of O (turning
    about ax_o), whatever the two angles: everything closer to ax than (axis distance - reach of O - margin),
    and everything outside O's z range grown by the margin. Intersection volumes and gaps up to the margin
    are unchanged, because O at any angle stays inside both regions that are kept."""
    if S.is_empty() or O.is_empty():
        return S
    VS, VO = core.verts(S), core.verts(O)
    r_o = float(np.hypot(VO[:, 0] - ax_o[0], VO[:, 1] - ax_o[1]).max())
    d = math.hypot(ax_o[0] - ax[0], ax_o[1] - ax[1])
    lo, hi = VS.min(axis=0) - 1.0, VS.max(axis=0) + 1.0
    z0, z1 = max(lo[2], float(VO[:, 2].min()) - MESH_CUT_MARGIN), min(hi[2], float(VO[:, 2].max()) + MESH_CUT_MARGIN)
    if z1 <= z0:
        return m3.Manifold()          # empty: the caller then keeps the whole solids
    keep = core.box((lo[0], lo[1], z0), (hi[0], hi[1], z1))
    r_in = d - r_o - MESH_CUT_MARGIN          # removed as a polygon inscribed in this circle: only points inside it go
    if r_in > 0.0:
        keep = keep - cyl(ax[0], ax[1], lo[2] - 1.0, hi[2] + 1.0, r_in, 96)
    return S ^ keep


def load_movement(folder):
    """folder holds movement.json and parts/<name>.step. Opens only the files movement.json names."""
    path = inside(folder, os.path.join(folder, "movement.json"))
    if os.path.getsize(path) > MAX_JSON_BYTES:
        raise FormatError("movement.json too large")
    with open(path, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except ValueError as e:
            raise FormatError("movement.json is not valid JSON") from e

    def load(name):
        p = part_path(folder, name)
        if p is None:
            if os.path.isfile(os.path.join(folder, "parts", name + ".stl")):
                raise FormatError("parts/%s.stl: parts must be STEP files (parts/%s.step); STL is not accepted" % (name, name))
            raise FormatError("part file parts/%s.step not found" % name)
        try:
            return load_part_file(p)
        except FormatError as e:
            raise FormatError("parts/%s: %s" % (os.path.basename(p), e))
    return Movement(doc, load)


def inside(folder, path):
    """path, if it is a regular file (or directory) inside folder reached without any symbolic link;
    FormatError otherwise. Missing files are returned unchanged (the caller reports them)."""
    rel = os.path.relpath(path, folder)
    cur = folder
    for comp in rel.split(os.sep):
        cur = os.path.join(cur, comp)
        if os.path.islink(cur):
            raise FormatError("%s is a symbolic link; submitted files must be real files in the folder" % rel)
    if os.path.exists(path):
        real, root = os.path.realpath(path), os.path.realpath(folder)
        if os.path.commonpath([real, root]) != root:
            raise FormatError("%s lies outside the submitted folder" % rel)
    return path


def part_path(folder, name):
    """parts/<name>.step if it exists, else None. (Parts are STEP files; STL parts are not accepted.)
    FormatError if it, or parts/, is a symbolic link or lies outside folder."""
    p = inside(folder, os.path.join(folder, "parts", name + ".step"))
    return p if os.path.isfile(p) else None


def load_part_file(p):
    """One STEP part file as a normalised Manifold, or FormatError."""
    if not p.endswith(".step"):
        raise FormatError("parts must be STEP files (.step)")
    return core.load_step_part(p, MAX_STEP_BYTES, MAX_TRIANGLES, STEP_LINEAR_DEFLECTION, STEP_ANGULAR_DEFLECTION,
                               STEP_MAX_TRIANGLE_FACES, STEP_TIMEOUT_S, STEP_MEMORY_MB, SELF_UNION_TOL)


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
    path = inside(folder, os.path.join(folder, "assembly.json"))
    if os.path.getsize(path) > MAX_ASSEMBLY_BYTES:
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


CORNER_ERODE_VOX = 1.5      # study only, not a requirement: the opening of `thin`, applied to the empty space
CORNER_DILATE_VOX = 1.0
CORNER_MARGIN_VOX = 4       # empty voxels kept around the part's bounding box


def corners(part, offset=(0.0137, 0.0137, 0.0137)):
    """Dual of `thin`, unused by the grader: open the empty space around the part on a THIN_VOXEL grid.
    Returns (largest distance in mm from an empty voxel to the opened empty space, number of empty
    voxels the opening removes). Sharp concave corners and gaps narrower than the ball are removed."""
    h = THIN_VOXEL
    bb = np.array(part.bounding_box())
    lo = np.floor(bb[:3] / h).astype(int) - CORNER_MARGIN_VOX
    hi = np.ceil(bb[3:] / h).astype(int) + CORNER_MARGIN_VOX
    solid = core.voxelize(part, lo * h - np.asarray(offset), tuple(int(v) for v in hi - lo), h)
    empty = ~solid                      # the grid's border counts as empty space that goes on (edt sees no zero there)
    keep = core.edt(empty) >= CORNER_ERODE_VOX
    opened = (core.edt(~keep) <= CORNER_DILATE_VOX) & empty
    removed = empty & ~opened
    dev = core.edt(~opened)[empty].max() if removed.any() else 0.0
    return float(dev * h), int(removed.sum())
