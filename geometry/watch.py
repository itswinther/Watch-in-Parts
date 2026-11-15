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
BARREL_WHEEL_Z = (0.0, 1.0)         # the toothed drum
# The supplied barrel has two bodies on its axis (Decisions 2026-11-14 17:46, item 1): the toothed drum (the
# mainspring turns it; it drives the train) and the arbor (it carries the mainspring's inner end and, on its
# square, the ratchet the winding works turn). In the going-train checks (one-job parts P1 to P4) the two
# bodies are one mobile `barrel`, the union of the two meshes (data/barrel.stl).
BARREL_ARBOR_Z = (-1.0, 5.6)        # the whole arbor
BARREL_ARBOR_R = 0.5                # the arbor's pivots and plain sections, below and above the drum
BARREL_INNER_D = 12.12              # inside diameter of the drum's spring chamber (not modelled in the mesh):
                                    # DS-101 Rev F: thin spring L's listed barrel at demonstration scale (A, 19:50);
                                    # the thin barrel's spring LT (L with a 0.25 strip) has the same D
BARREL_CORE_R = BARREL_INNER_D / 6  # arbor core (hub) radius, one third of the inner radius (DS-101 section 1,
                                    # Grossmann art. 108 to 111, Saunier art. 517); the core spans the drum's z
BARREL_BORE_R = 2.0367              # the drum's bore round the core: radial clearance 0.0167
BARREL_SQUARE_SIDE = 1.4            # winding square on the arbor (a square prism on the barrel axis, sides
BARREL_SQUARE_Z = (3.3, 4.9)        # parallel to x and y) that carries the ratchet; half-diagonal 0.99
STAGE_BARREL_ARBOR_Z = (-1.0, 1.6)  # stage mode only (old runs): the one-body barrel of data/barrel_stage.stl
BARREL_TURNS_PER_HOUR = Fraction(1, 8)          # clockwise
CASE_RADIUS = 20.7         # reference reaches 20.354 at its largest stage, plus 0.3, rounded up to 0.05 (main; on
                           # b/thin-4mm SMALL_CASE_RADIUS 12.7 below replaces it, by the same rule)
CASE_HEIGHT = 13.4         # reference is 13.1 tall, plus 0.3
# thinness probe (SESSION.md Proposed spec changes, 2026-11-15 02:20; spikes/thin_probe/): not graded by
# tests/grade_watch.py. Stated in QA-W100 section 9 only when environment/brief_thin.py THIN_IN_BRIEF is on, and
# scored afterwards by spikes/thin_probe/score.py: x = (H - THIN_TARGET_MM) / (CASE_HEIGHT - THIN_TARGET_MM), clamped
# to 0..1, s = (1 - x) ** THIN_SCORE_EXPONENT, reward = THIN_SCORE_SHARE x share + THIN_SCORE_SHARE x [all pass] x s.
# (Not the THIN_VOXEL ... constants below, which belong to the printability test.)
THIN_TARGET_MM = 4.0       # mm: the thickness target, total height along z of the taller build, barrel included
THIN_SCORE_EXPONENT = 4
THIN_SCORE_SHARE = Fraction(1, 2)   # the half of the reward that full acceptance earns (as tests/grade_watch.py)
# stage 3, change request: the supplied barrel (same mesh) turns clockwise once every 6 hours instead of 8
CHANGED_BARREL_TURNS_PER_HOUR = Fraction(1, 6)
# The thin barrel (branch b/thin-4mm, from A's spike a/thin-4mm): ON by default on this branch, so the generator, the
# bundle, the grader, the reference and spikes/thin_probe/score.py all read the same barrel without any setting.
# WATCH_THIN_BARREL=0 gives the 6.6 mm barrel of main (to regrade old runs). The thin barrel is the main meshes
# scaled in z by THIN_BARREL_SCALE about z = 0 (arbor 3.0 mm instead of 6.6; teeth, module and every x/y size
# unchanged), written by spikes/thin_4mm/make_barrel.py to data/thin/ (inside geometry/, so every image that
# carries geometry/ carries them). The z constants of the barrel follow. The strength load case
# (BARREL_TORQUE_MAX_NMM, the automatic version's bridle) is kept at full value: conservative (A's choice).
THIN_BARREL = os.environ.get("WATCH_THIN_BARREL", "1") != "0"
# The small case (branch b/thin-4mm, from A's spike a/thin-po cde0408): ON by default on this branch. The size check
# and the documents use THIN_CASE_RADIUS as CASE_RADIUS, and the reference picks its small-case layout when it is
# set. SMALL_CASE_RADIUS = A's small-case reference reaches 12.357 (both builds), plus 0.3, rounded up to 0.05 (the
# rule the old 20.7 came from). THIN_CASE_RADIUS=<r> sets another radius; THIN_CASE_RADIUS=0 gives main's 20.7.
SMALL_CASE_RADIUS = 12.7
_tcr = os.environ.get("THIN_CASE_RADIUS", "")
THIN_CASE_RADIUS = SMALL_CASE_RADIUS if _tcr == "" else (float(_tcr) if float(_tcr) > 0 else None)
del _tcr
if THIN_CASE_RADIUS is not None:
    CASE_RADIUS = THIN_CASE_RADIUS
THIN_BARREL_SCALE = 3.0 / 6.6
if THIN_BARREL:
    BARREL_WHEEL_Z = tuple(v * THIN_BARREL_SCALE for v in BARREL_WHEEL_Z)
    BARREL_ARBOR_Z = tuple(v * THIN_BARREL_SCALE for v in BARREL_ARBOR_Z)
    BARREL_SQUARE_Z = tuple(v * THIN_BARREL_SCALE for v in BARREL_SQUARE_Z)
# Barrel catalogue (branch a/barrel-catalogue): the agent may choose its barrel. Each entry is BR-096-20 (96 teeth,
# module 0.2, every x/y size unchanged) scaled in z only, about z = 0, by the factor below; meshes in data/<id>/
# (barrel.stl, barrel_drum.stl, barrel_arbor.stl; written by spikes/barrel_catalogue/make_barrels.py: BR-096-66 is
# byte for byte data/, BR-096-30 byte for byte data/thin/). movement.json may name one under the top-level key
# "barrel"; without it the loader keeps the barrel above (THIN_BARREL). Unscaled z of BR-096-20: drum (0, 1),
# arbor (-1, 5.6), square (3.3, 4.9).
BARREL_CATALOGUE = {"BR-096-66": 1.0, "BR-096-45": 4.5 / 6.6, "BR-096-30": 3.0 / 6.6}


# Geometry the catalogue sheet may print (drawing data only): spring strip h x t x L (mm, demonstration scale s =
# 1.617, DS-101 [^s]) and the 1:1 row it is cut from. Spring height = the drum height less 0.05 clearance, at 1:1
# rounded down to 0.01 mm; t, L and the chamber are spring L's (DS-101 Table 1). BR-096-66 holds L itself.
BARREL_SPRING_GEOMETRY = {
    "BR-096-66": {"row": "L", "h_1to1": 0.48, "h": 0.78, "t": 0.162, "L": 437},
    "BR-096-45": {"row": "L39", "h_1to1": 0.39, "h": 0.63, "t": 0.162, "L": 437},
    "BR-096-30": {"row": "LT", "h_1to1": 0.25, "h": 0.40, "t": 0.162, "L": 437},
}
# GRADER-INTERNAL, not for the agent's documents: the spring's own torques (DS-101 formulas d1 to d3, M proportional
# to h, so row L's values x h/0.48; turns and run time are L's). The strength check's load stays the bridle torque
# BARREL_TORQUE_MAX_NMM for every barrel.
BARREL_SPRING_TORQUE = {
    "BR-096-66": {"torque_factor": 1.0, "M_el_nmm": 8.4, "n_el": 9.7, "turns_D6": 4.9, "run_h_D6": 40, "M_at_N_nmm": 4.5},
    "BR-096-45": {"torque_factor": 0.39 / 0.48, "M_el_nmm": 6.8, "n_el": 9.7, "turns_D6": 4.9, "run_h_D6": 40, "M_at_N_nmm": 3.7},
    "BR-096-30": {"torque_factor": 0.25 / 0.48, "M_el_nmm": 4.4, "n_el": 9.7, "turns_D6": 4.9, "run_h_D6": 40, "M_at_N_nmm": 2.4},
}


def barrel_z(barrel_id):
    """{"wheel": drum z range, "arbor": arbor z range, "square": winding square z range} of a catalogue barrel."""
    k = BARREL_CATALOGUE[barrel_id]
    return {"wheel": (0.0, 1.0 * k), "arbor": (-1.0 * k, 5.6 * k), "square": (3.3 * k, 4.9 * k)}


REF_KEPT_VOLUME_SHARE = 0.626   # stage 3: the reference keeps 0.6267 of the mobile volume and all of the fixed volume it receives (rounded down)
VOL_TOL = 0.01              # mm3
SPIN_STEPS = 72             # free-spin test: steps of 5 degrees
SPIN_OFFGRID = (Fraction(1, 3), Fraction(1, 5))   # one-job mode: extra free-spin poses after every step, as fractions of a step
SWEEP_DZ = 0.02             # mm, one-job mode, check 6: swept solids, the largest height of a band where the shape changes with z
HELD_MOVE = 0.3
SAMPLES_PER_TOOTH = 8
ENGAGE_GAP = 0.1            # mm: meshing gears are never further apart than this
DRIVE_FRACTION = 0.25       # of the driver's tooth pitch: backlash must be smaller
MESH_OFFGRID = (Fraction(1, 3), Fraction(1, 5))   # extra no-jam poses after every eighth step, as fractions of a step
DRIVE_MIN_VOLUME = 0.001    # mm3: and that extra overlap is at least this (meshing noise is far below it)
DRIVE_AREA_RATIO = 0.5      # drive test: overlap / (its height in z) must exceed this x the mesh's module squared
                            # (module = 2 x axis distance / (driver teeth + driven teeth))
FRAME_JOIN = 0.01           # mm: two fixed parts this close are joined; the fixed parts must form one frame
HAND_CENTRE_MIN = 0.5       # mm: a hand part's centre of volume is at least this far from its axis
HAND_AREA_MAX_SHARE = 0.25  # one-job mode: a hand part seen from the dial side (its projection on the xy plane)
                            # covers at most this share of the disc its tip sweeps (pi x Movement.hand_reach ** 2)
THIN_SLAB = 32              # layers per slab of the thickness test (memory only; the result does not depend on it)
THIN_DEV_CAP_VOX = 8        # the thickness test's deviation is exact up to this many voxels (limit THIN_DEV is 4)
SEAT_TOUCH = 0.02           # mm: parts of one mobile closer than this touch; a mobile's parts must form one piece
MESH_SHIFT = 0.03           # mm: tolerant test, the driven mobile moved this far away from and towards the driver's axis
MESH_CUT_MARGIN = 1.05      # mm, private speed-up of mesh_run: material further than this from the other mobile's reach
                            # is cut away before stepping (must exceed the 1.0 search length of min_gap in mesh_run)
MESH_GAP_SEARCH = 0.15      # mm, private speed-up of mesh_run: gaps are searched this far first, then to 1.0 if none found
TEETH_MIN_DEPTH = 0.1       # mm: mesh test, a section whose outline's largest and smallest distance from the axis differ
                            # by less than this has no teeth (a round, faceted disc is not a gear)
TEETH_RAYS = 7200           # mesh test: the outline of a section is measured along this many equally spaced directions
                            # (0.05 degrees apart; a tooth of the finest printable pitch spans dozens of them)
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
# mass budget, the same at every stage
FIXED_VOLUME_MAX = 355.0    # union of the fixed parts: the reference at its largest stage (322.4) plus 10 percent, rounded up
MOBILE_VOLUME_MAX = 278.0   # mm3, the sum of the volumes of every part of every mobile, the supplied barrel not counted
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

# ---- gear strength (one-job mode, check `strength`; SESSION.md Decisions 2026-11-14 17:56, option 2) ----
# Load case: the barrel at the highest torque DS-101 states, the train stalled downstream. Each value below is
# one cell of a supplier sheet in spikes/keyless/datasheets/ (workstream A's); check_strength_sheets() reads
# the cells from the sheet text and fails if any differs, so the sheet stays the one source.
BARREL_TORQUE_MAX_NMM = 70.1         # N·mm: DS-101 Table 2a, "Slipping torque of the bridle", column "This series
                                     # (N·mm)", the upper end of "51.6 to 70.1" (also DS-101 Note 2)
TOOTH_LOAD_FACTOR = 1.45             # the rated tooth load is this x the nominal W_t = T / (m z / 2): the load factor
                                     # for unlubricated (dry) meshing that DS-W04 states (section 1 and its table of
                                     # section 2). Basis: A's train simulation (a/train-sim 42b3eaf,
                                     # spikes/train_sim/README.md): with dry friction the peak tooth force is 1.39 to
                                     # 1.45 x the Lewis F. Approved by Mikael (B logs it in SESSION.md).
# DS-201 section 8, table "Design allowables at the upper end of the matching tier": every row, as
# (the row's Material cell, its ordering code from DS-201 section 2, Allowable (MPa), kind of strength).
DS201_ALLOWABLE_ROWS = (
    ("Brass CW614N", "AD-CW614N", 110.0, "tensile"),
    ("Steel AD-C100-HT, < 1.000 mm", "AD-C100-HT", 750.0, "tensile"),
    ("Steel AD-C100-HT, 1.000 to < 1.575 mm", "AD-C100-HT", 725.0, "tensile"),
    ("Corundum, compressive", "AD-AL2O3", 450.0, "compressive"),
)
# The material a mobile may declare and the allowable its teeth are rated at (orchestrator's answers to
# builder S, 2026-11-14, logged under Decisions by B): only a designation with a tensile (yield-based) allowable
# in DS-201 section 8, since tooth bending is tensile at the root, so the corundum row (compressive) does not
# qualify; a designation with several rows takes the LOWEST (AD-C100-HT: 725, not 750), because the delivery
# does not declare stock thickness. AD-C100S and AD-CoNiCr-45 have no allowable in section 8: not accepted.
# The supplied barrel's own teeth are not rated (a supplied part, rated by its maker): in a mesh with the barrel
# only the other gear is checked.
MATERIAL_ALLOWABLE_MPA = {}
for _cell, _code, _mpa, _kind in DS201_ALLOWABLE_ROWS:
    if _kind == "tensile":
        MATERIAL_ALLOWABLE_MPA[_code] = min(_mpa, MATERIAL_ALLOWABLE_MPA.get(_code, float("inf")))
del _cell, _code, _mpa, _kind
MATERIAL_DESIGNATIONS = tuple(sorted(MATERIAL_ALLOWABLE_MPA))   # what a mobile may declare (the format check's list)
STRENGTH_SHEETS = {"DS-101": "DS-101_mainspring_barrel.md", "DS-201": "DS-201_materials.md"}
# Lewis form factor: full-depth involute teeth cut by the standard basic rack (addendum 1.0 m, dedendum 1.25 m),
# see lewis_form_factor(). LEWIS_Y is the table the grader uses (4 decimals, the values DS-W04 prints), frozen in
# geometry/data/lewis_y.json and checked against lewis_form_factor() by tests/test_strength.py.
LEWIS_ADDENDUM, LEWIS_DEDENDUM = 1.0, 1.25
LEWIS_DECIMALS = 4


# ---------------- supplied barrel and a cylinder helper ----------------
def cyl(x, y, z0, z1, r, seg=48):
    return m3.Manifold.cylinder(z1 - z0, r, r, seg).translate([x, y, z0])


_MESHES = {}


def mesh_path(name, barrel_id=None):
    """The file of supplied mesh `name` (barrel, barrel_drum, barrel_arbor, barrel_stage): data/<barrel_id>/ for a
    catalogue barrel (BARREL_CATALOGUE), else data/thin/ when THIN_BARREL (the stage task's one-body barrel_stage is
    never thinned), else data/."""
    data = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    if barrel_id is not None and name != "barrel_stage":
        if barrel_id not in BARREL_CATALOGUE:
            raise FormatError("movement.json: 'barrel' must be one of %s" % ", ".join(sorted(BARREL_CATALOGUE)))
        data = os.path.join(data, barrel_id)
    elif THIN_BARREL and name != "barrel_stage":
        data = os.path.join(data, "thin")
    return os.path.join(data, name + ".stl")


def _mesh(name, barrel_id=None):
    key = (name, barrel_id)
    if key not in _MESHES:
        _MESHES[key] = core.tris_to_manifold(core.read_stl(mesh_path(name, barrel_id), MAX_TRIANGLES, MAX_STL_BYTES))
    return _MESHES[key]


def barrel(barrel_id=None):
    """The supplied mainspring barrel as one solid (data/barrel.stl, the agent's supplied/barrel.stl): the union
    of the toothed drum and the arbor in their assembled position, axis on x = y = 0. The going-train checks
    turn it as one mobile. barrel_id: a catalogue barrel instead (BARREL_CATALOGUE)."""
    return _mesh("barrel", barrel_id)


def barrel_bodies(barrel_id=None):
    """The two bodies of the supplied barrel, {"barrel_drum": solid, "barrel_arbor": solid} (data/barrel_drum.stl,
    data/barrel_arbor.stl), for the crown-winding part: there the drum stands with the going train and the
    arbor is wound."""
    return {n: _mesh(n, barrel_id) for n in ("barrel_drum", "barrel_arbor")}


def barrel_stage():
    """Stage mode only (regrading old runs): the one-body barrel those runs were given (data/barrel_stage.stl,
    byte for byte the former data/barrel.stl), arbor z STAGE_BARREL_ARBOR_Z."""
    return _mesh("barrel_stage")


# ---------------- movement ----------------
def rot_about(man, axis_xy, deg):
    return man.translate([-axis_xy[0], -axis_xy[1], 0]).rotate([0, 0, deg]).translate([axis_xy[0], axis_xy[1], 0])


class Movement:
    """A parsed movement: fixed solid, mobiles (name -> solid, axis), meshes, hands."""

    def __init__(self, doc, load_stl, barrel_solid=None, materials=False):
        """materials: one-job mode; every mobile must declare "material", a key of MATERIAL_ALLOWABLE_MPA (a format
        error otherwise, C1), and may declare "part_materials", {part of that mobile: such a key}, overriding
        "material" for those parts (a format error if a key is not a part of the mobile or a value does not
        qualify). mobiles[name]["part_materials"] then gives every part its material. Without it (stage mode)
        neither field is read."""
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
                reserve(n, where)
                out.append(load_stl(n))
            return out

        def reserve(n, where):
            if not isinstance(n, str) or not NAME_RE.match(n):
                raise FormatError("%s: bad part name %r (letters, digits, _ and - only, no extension)" % (where, n))
            if n == "barrel":
                raise FormatError("%s: 'barrel' is reserved for the supplied barrel and cannot be a part name" % where)
            if n in used:
                raise FormatError("part '%s' is used more than once" % n)
            used.add(n)
            if len(used) > MAX_PARTS:
                raise FormatError("more than %d parts" % MAX_PARTS)
        self.doc = doc
        self.load_part = load_stl       # Part 5 reads the keyless section's part files through it (same checks, same cache)
        self.barrel_speed = BARREL_TURNS_PER_HOUR      # the grader sets CHANGED_BARREL_TURNS_PER_HOUR at stage 3
        fixed_names = doc.get("fixed")
        self.fixed_parts = dict(zip(fixed_names if isinstance(fixed_names, list) else [], parts(fixed_names, "fixed")))
        self.fixed = union(list(self.fixed_parts.values()))
        mob = doc.get("mobiles")
        if not isinstance(mob, dict) or not mob:
            raise FormatError("movement.json: 'mobiles' must be a non-empty object")
        bid = doc.get("barrel")         # optional: a catalogue barrel (BARREL_CATALOGUE); default the supplied one
        if bid is not None and (not isinstance(bid, str) or bid not in BARREL_CATALOGUE):
            raise FormatError("movement.json: 'barrel' must be one of %s" % ", ".join(sorted(BARREL_CATALOGUE)))
        self.barrel_id = bid
        if barrel_solid is None:
            barrel_solid = barrel(bid)
        self.mobiles = {"barrel": {"axis": (0.0, 0.0), "solid": barrel_solid,
                                   "parts": {}}}
        for name, m in mob.items():
            if not NAME_RE.match(str(name)) or name == "barrel":
                raise FormatError("bad mobile name %r" % (name,))
            ax = m.get("axis") if isinstance(m, dict) else None
            if not (isinstance(ax, list) and len(ax) == 2 and all(isinstance(v, (int, float)) and math.isfinite(v) for v in ax)):
                raise FormatError("mobile '%s': 'axis' must be [x, y]" % name)
            names = m.get("parts")
            ps = parts(names, "mobile '%s'" % name)
            self.mobiles[name] = {"axis": (float(ax[0]), float(ax[1])), "solid": union(ps), "parts": dict(zip(names, ps))}
            if materials:
                mat = m.get("material")
                if not isinstance(mat, str) or mat not in MATERIAL_ALLOWABLE_MPA:
                    raise FormatError("mobile '%s': 'material' must be the designation of a material with a bending "
                                      "(tensile) design allowable in DS-201 section 8" % name)
                self.mobiles[name]["material"] = mat
                # part_materials (Decisions 2026-11-14 21:43, item 2): {part: designation} for some parts of this
                # mobile, overriding "material" for those parts; the same designations qualify
                pm = m.get("part_materials", {})
                if not isinstance(pm, dict):
                    raise FormatError("mobile '%s': 'part_materials' must be an object {part name: designation}" % name)
                for pn, pmat in pm.items():
                    if pn not in names:
                        raise FormatError("mobile '%s': 'part_materials' names %r, which is not a part of this mobile"
                                          % (name, pn))
                    if not isinstance(pmat, str) or pmat not in MATERIAL_ALLOWABLE_MPA:
                        raise FormatError("mobile '%s': 'part_materials' of part '%s' must be the designation of a "
                                          "material with a bending (tensile) design allowable in DS-201 section 8"
                                          % (name, pn))
                self.mobiles[name]["part_materials"] = {pn: pm.get(pn, mat) for pn in names}
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
        # friction_on (SESSION.md Decisions 2026-11-14 15:47): a mobile carried by friction on another coaxial mobile.
        # In the going-train checks it turns with its carrier (speeds()); in the crown-winding part it is a free body.
        self.friction = {}
        for name, m in mob.items():
            fo = m.get("friction_on")
            if fo is None:
                continue
            if not isinstance(fo, str) or fo not in self.mobiles or fo in ("barrel", name):
                raise FormatError("mobile '%s': 'friction_on' must name another mobile of the file (not 'barrel')" % name)
            self.friction[name] = fo
        for name, fo in self.friction.items():
            if fo in self.friction:
                raise FormatError("mobile '%s': 'friction_on' names '%s', which is itself carried by friction" % (name, fo))
            a, b = self.mobiles[name]["axis"], self.mobiles[fo]["axis"]
            if math.hypot(a[0] - b[0], a[1] - b[1]) > COAX_TOL:
                raise FormatError("mobile '%s': 'friction_on' needs a coaxial mobile; the axes of '%s' and '%s' are %.4f mm "
                                  "apart (at most %g)" % (name, name, fo, math.hypot(a[0] - b[0], a[1] - b[1]), COAX_TOL))
        # the crown-winding (keyless) section: its part names count once with the others here; the section itself, and
        # its part files, are read by geometry/keyless_job.py when Part 5 runs
        from .keyless_job import keyless_part_names
        self.keyless_names = keyless_part_names(doc.get("keyless"))
        self.keyless_solids = {}        # filled by attach_keyless() (Part 4 when Part 5 is graded)
        for n in self.keyless_names:
            reserve(n, "keyless")
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
        Returns (speeds, conflicts). Every declared mesh is external: it reverses direction. A `friction_on` mobile
        and its carrier turn as one, at the same speed, whichever of the two is reached first.
        meshes: the meshes to follow (default: every declared mesh)."""
        w = {"barrel": self.barrel_speed}
        conflicts = []
        links = [(a, b, -Fraction(ta, tb)) for a, ta, b, tb in (self.meshes if meshes is None else meshes)]
        links += [(c, f, Fraction(1)) for f, c in getattr(self, "friction", {}).items()]
        changed = True
        while changed:
            changed = False
            for a, b, r in links:
                for src, dst, k in ((a, b, r), (b, a, 1 / r)):
                    if src in w:
                        v = w[src] * k
                        if dst not in w:
                            w[dst] = v
                            changed = True
                        elif w[dst] != v and (src, dst) not in conflicts and (dst, src) not in conflicts:
                            conflicts.append((src, dst))
        return w, conflicts

    # ---- measurements ----
    def spin(self, name, offgrid=()):
        """Largest overlap with the fixed parts while the mobile makes one full turn: SPIN_STEPS poses of
        360 / SPIN_STEPS degrees. offgrid (one-job mode: SPIN_OFFGRID): also the poses i + f of a step, for every
        step i and every fraction f, so a mobile whose shape repeats every step (a 72-tooth wheel) cannot hide a
        stop between the steps. Without offgrid (stage mode) the test is the old one, unchanged."""
        if not offgrid:
            worst = (0.0, 0)
            for i in range(SPIN_STEPS):
                v = ivol(self.posed(name, 360.0 * i / SPIN_STEPS), self.fixed)
                if v > worst[0]:
                    worst = (v, i)
            return {"worst_volume": worst[0], "step": worst[1], "steps": SPIN_STEPS}
        # the frame cut to the box round the mobile's swept solid: the mobile stays inside it at every angle, so
        # every intersection volume is unchanged
        F = self.fixed ^ self._swept_box(name)
        worst, n = (0.0, 0), 0
        for i in range(SPIN_STEPS):
            for f in (Fraction(0),) + tuple(offgrid):
                s = i + f
                v = ivol(self.posed(name, float(Fraction(360) * s / SPIN_STEPS)), F)
                n += 1
                if v > worst[0]:
                    worst = (v, s)
        return {"worst_volume": worst[0], "step": float(worst[1]), "step_exact": str(worst[1]),
                "angle_deg": float(Fraction(360) * worst[1] / SPIN_STEPS), "steps": SPIN_STEPS, "poses": n}

    DIRECTIONS = (("+x", (1, 0, 0)), ("-x", (-1, 0, 0)), ("+y", (0, 1, 0)), ("-y", (0, -1, 0)),
                  ("+z", (0, 0, 1)), ("-z", (0, 0, -1)))

    def held_all(self):
        """Only the frame holds. For each of the six moves of HELD_MOVE, a mobile is held when, moved, it
        intersects the fixed parts, or a mobile on the same axis (within COAX_TOL) that is itself held in
        that direction, by more than VOL_TOL; worked out to a fixed point. Mobiles on another axis never
        count, so two wheels cannot hold each other in mid-air.
        Returns {mobile: {move: {"held": bool, "fixed_volume": overlap with the fixed parts, "via": mobile or None}}}."""
        out = {k: {} for k in self.mobiles}
        for label, d in self.DIRECTIONS:
            moved = {k: mo["solid"].translate([c * HELD_MOVE for c in d]) for k, mo in self.mobiles.items()}
            fv = {k: ivol(moved[k], self.fixed) for k in self.mobiles}
            held = {k: None for k in self.mobiles if fv[k] > VOL_TOL}
            changed = True
            while changed:
                changed = False
                for k, mo in self.mobiles.items():
                    if k in held:
                        continue
                    for j in list(held):
                        aj = self.mobiles[j]["axis"]
                        if math.hypot(aj[0] - mo["axis"][0], aj[1] - mo["axis"][1]) <= COAX_TOL \
                                and ivol(moved[k], self.mobiles[j]["solid"]) > VOL_TOL:
                            held[k] = j
                            changed = True
                            break
            for k in self.mobiles:
                out[k][label] = {"held": k in held, "fixed_volume": fv[k], "via": held.get(k)}
        return out

    def held(self, name):
        """Per move: overlap of the moved mobile with what can hold it under held_all's rule (the fixed parts,
        and the mobiles on its axis that are held in that direction)."""
        hall, out = self.held_all(), {}
        ax = self.mobiles[name]["axis"]
        for label, d in self.DIRECTIONS:
            co = [mo["solid"] for k, mo in self.mobiles.items() if k != name and hall[k][label]["held"]
                  and math.hypot(mo["axis"][0] - ax[0], mo["axis"][1] - ax[1]) <= COAX_TOL]
            out[label] = ivol(self.posed(name).translate([c * HELD_MOVE for c in d]), union([self.fixed] + co))
        return out

    def frame(self):
        """The fixed parts form one frame: two are joined when their smallest distance is at most FRAME_JOIN.
        Returns (connected, groups of part names, the smallest distance from each group to the rest)."""
        names = list(self.fixed_parts)
        parent = {n: n for n in names}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = self.fixed_parts[names[i]], self.fixed_parts[names[j]]
                if find(names[i]) != find(names[j]) and core.bbox_overlap(a, b, FRAME_JOIN) \
                        and float(a.min_gap(b, FRAME_JOIN * 2)) <= FRAME_JOIN:
                    parent[find(names[i])] = find(names[j])
        groups = {}
        for n in names:
            groups.setdefault(find(n), []).append(n)
        groups = sorted(groups.values(), key=len, reverse=True)
        return len(groups) <= 1, groups

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

    def pieces(self, name):
        """The parts of a mobile grouped into pieces: part A and part B are in one piece when a chain of
        parts leads from A to B, each within SEAT_TOUCH of the next. Largest piece first (ties: listing order)."""
        parts = self.mobiles[name]["parts"]
        names = list(parts)
        group = {n: i for i, n in enumerate(names)}
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                if group[a] != group[b] and parts[a].min_gap(parts[b], 2 * SEAT_TOUCH) <= SEAT_TOUCH:
                    old, new = group[b], group[a]
                    for n in names:
                        if group[n] == old:
                            group[n] = new
        out = {}
        for n in names:
            out.setdefault(group[n], []).append(n)
        return sorted(out.values(), key=lambda g: (-len(g), names.index(g[0])))

    def all_parts(self, keyless=False):
        """name -> solid, for every part: the supplied barrel, the fixed parts and the parts of every mobile.
        keyless: also the parts of the keyless section that attach_keyless() has read (none until then); the
        assembly (Part 4) uses them when the crown-winding part is graded (A's request 21:20, agreed by B)."""
        out = {"barrel": self.mobiles["barrel"]["solid"]}
        out.update(self.fixed_parts)
        for m in self.mobiles.values():
            out.update(m["parts"])
        if keyless:
            out.update(self.keyless_solids)
        return out

    def attach_keyless(self):
        """Read the keyless section's part files (through the movement's own loader) so that the assembly includes
        them. FormatError if one does not load; then none is attached."""
        solids = {n: self.load_part(n) for n in self.keyless_names}
        self.keyless_solids = solids
        return solids

    def volumes(self):
        """(volume of the union of the fixed parts, sum of the volumes of every part of every mobile
        except the supplied barrel), in mm3, of the solids built from the part files."""
        mobile = sum(p.volume() for k, mo in self.mobiles.items() if k != "barrel" for p in mo["parts"].values())
        return float(self.fixed.volume()), float(mobile)

    def assembly_box(self):
        lo, hi = np.full(3, np.inf), np.full(3, -np.inf)
        for solid in self.all_parts(keyless=True).values():
            bb = np.array(solid.bounding_box())
            lo, hi = np.minimum(lo, bb[:3]), np.maximum(hi, bb[3:])
        return lo - ASM_CLEAR, hi + ASM_CLEAR

    def assembly_replay(self, order, paths):
        """Put the parts in one at a time. Returns per-part results and the list installed cleanly.
        A part is tested against every part placed before it, parts of its own mobile included.
        A part missing from `order` stands in its assembled position from the start and is not installed.
        The keyless section's parts take part once attach_keyless() has read them (Part 5 graded)."""
        parts = self.all_parts(keyless=True)
        lo, hi = self.assembly_box()
        placed = [(n, solid) for n, solid in parts.items() if n not in order]
        results, installed = {n: {"not_in_order": True} for n, _ in placed}, []
        for name in order:
            solid = parts[name]
            P = paths.get(name)
            msgs = _asm_messages(name, solid, P, lo, hi)
            res = {"format_messages": msgs, "worst_volume": None, "pose_index": None, "hit": None,
                   "poses": int(len(P)) if isinstance(P, np.ndarray) and P.ndim == 3 else 0}
            if not msgs:
                worst = (0.0, -1, None)
                for i, T in enumerate(P):
                    mv = core.apply(solid, T)
                    for pn, ps in placed:
                        v = ivol(mv, ps)
                        if v > worst[0]:
                            worst = (v, i, pn)
                res.update(worst_volume=worst[0], pose_index=worst[1], hit=worst[2])
                if worst[0] <= VOL_TOL:
                    installed.append(name)
            placed.append((name, solid))
            results[name] = res
        return results, installed

    def mesh_run(self, a, ta, b, tb, speeds=None, shift=0.0, cut=True):
        """Turn a declared mesh through max(ta, tb) tooth pitches of the driver. Reports the largest
        overlap (grid steps, plus MESH_OFFGRID poses after every eighth step), the largest gap, and the
        drive test: pushing the driver DRIVE_FRACTION of a tooth pitch further with the driven gear held,
        the intersection that the push creates (the part of the pushed driver's intersection with the driven
        mobile that the driver did not already occupy before the push), alone and divided by (its height in z
        x module squared), and the smallest of those heights in z over the steps (smallest_drive_height: the face
        width of the strength check; 0 if a step creates no new overlap).
        shift: the driven mobile (and its axis) is first moved this far straight away from the driver's
        axis (negative: towards it); same steps and angles. cut=False skips the speed-up (same results).
        Also the tooth-count condition (tooth_counts: its keys are added to the result)."""
        teeth = self.tooth_counts(a, ta, b, tb)
        A, ax_a = self.mobiles[a]["solid"], self.mobiles[a]["axis"]
        B, ax_b = self.mobiles[b]["solid"], self.mobiles[b]["axis"]
        module = 2.0 * math.hypot(ax_b[0] - ax_a[0], ax_b[1] - ax_a[1]) / (ta + tb)   # drawn position
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
        worst, gap, drive, ratio = (0.0, 0), 0.0, float("inf"), float("inf")
        height = float("inf")         # smallest height in z of the push's new overlap (0 at a step that has none)
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
                for f in MESH_OFFGRID:                    # off the grid: false tooth counts cannot line up here
                    vf = ivol(pa(da * (i + float(f))), pb(db * (i + float(f))))
                    if vf > worst[0]:
                        worst = (vf, i + float(f))
                P = pa(da * i + push)
                extra, r, hz = 0.0, 0.0, 0.0
                if core.bbox_overlap(P, Bi):
                    N = (P ^ Bi) - Ai              # intersection the push creates: not already there before it
                    extra = float(N.volume()) if not N.is_empty() else 0.0
                    if not math.isfinite(extra):
                        raise ArithmeticError("non-finite volume")
                    if extra > 0.0:
                        zb = N.bounding_box()
                        hz = zb[5] - zb[2]
                        r = extra / (hz * module * module) if hz > 1e-9 and module > 1e-9 else 0.0
                drive, ratio = min(drive, extra), min(ratio, r)
                height = min(height, hz if extra > 0.0 else 0.0)
        return {"worst_volume": worst[0], "step": worst[1], "steps": n, "largest_gap": gap,
                "smallest_drive_overlap": drive, "smallest_drive_ratio": ratio, "module": module,
                "smallest_drive_height": height, **teeth}

    def drive_parts(self, a, ta, b, tb):
        """For the strength check: the drive test of mesh_run (drawn position, no shift; the same steps, angles
        and push), with the new overlap the push creates at each step split by part: for each of a and b, the
        volume of that overlap inside each of its parts (the driver's parts pushed, the driven mobile's parts
        held), summed over the drive-test steps. Returns {mobile: {part: mm3}}; the supplied barrel (no parts)
        and a one-part mobile are left out (nothing to split)."""
        A, ax_a = self.mobiles[a]["solid"], self.mobiles[a]["axis"]
        B, ax_b = self.mobiles[b]["solid"], self.mobiles[b]["axis"]
        A2, B2 = _near_cut(A, ax_a, B, ax_b), _near_cut(B, ax_b, A, ax_a)
        A0, B0 = (A, B) if (A2.is_empty() or B2.is_empty()) else (A2, B2)
        # each part without the material that can never reach the other mobile (as _near_cut does for mesh_run):
        # the overlap lies inside the other mobile, so the part's share of it is unchanged
        side = {}
        for name, ax, other, ax_o in ((a, ax_a, B, ax_b), (b, ax_b, A, ax_a)):
            ps = self.mobiles[name]["parts"]
            if len(ps) > 1:
                side[name] = (ax, {pn: _near_cut(q, ax, other, ax_o) for pn, q in ps.items()})
        out = {name: {pn: 0.0 for pn in qs} for name, (_, qs) in side.items()}
        if not side:
            return out
        n = SAMPLES_PER_TOOTH * max(ta, tb)
        da = 360.0 / (SAMPLES_PER_TOOTH * ta)
        db = -da * ta / tb
        push = DRIVE_FRACTION * 360.0 / ta
        rot = lambda S, ax, deg: S if deg == 0.0 else rot_about(S, ax, deg)
        for i in range(0, n, 8):
            Ai, Bi, P = rot(A0, ax_a, da * i), rot(B0, ax_b, db * i), rot(A0, ax_a, da * i + push)
            if not core.bbox_overlap(P, Bi):
                continue
            N = (P ^ Bi) - Ai
            if N.is_empty():
                continue
            for name, deg in ((a, da * i + push), (b, db * i)):
                if name not in side:
                    continue
                ax, qs = side[name]
                for pn, q in qs.items():
                    if q.is_empty():
                        continue
                    qq = rot(q, ax, deg)
                    if core.bbox_overlap(qq, N):
                        v = qq ^ N
                        vol = 0.0 if v.is_empty() else float(v.volume())
                        if not math.isfinite(vol):
                            raise ArithmeticError("non-finite volume")
                        out[name][pn] += vol
        return out

    @staticmethod
    def drive_passes(x):
        """The drive test alone (the third condition of the mesh test) on a mesh_run result."""
        return x["smallest_drive_overlap"] >= DRIVE_MIN_VOLUME and x["smallest_drive_ratio"] > DRIVE_AREA_RATIO

    @staticmethod
    def mesh_passes(x):
        """The conditions of the mesh test on a mesh_run result: teeth as declared, no jam, engaged, the teeth drive."""
        return x["teeth_match"] and x["worst_volume"] <= VOL_TOL and x["largest_gap"] <= ENGAGE_GAP \
            and x["smallest_drive_overlap"] >= DRIVE_MIN_VOLUME and x["smallest_drive_ratio"] > DRIVE_AREA_RATIO

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

    # ---- swept solids (one-job mode, check 6 "Nothing else collides") ----
    def swept_cylinder(self, name):
        """(radius, z_min, z_max) of the upright cylinder round the mobile's axis that holds it at every angle:
        its largest vertex distance from the axis and its z range."""
        m = self.mobiles[name]
        V = core.verts(m["solid"])
        return (float(np.hypot(V[:, 0] - m["axis"][0], V[:, 1] - m["axis"][1]).max()),
                float(V[:, 2].min()), float(V[:, 2].max()))

    def swept_profile(self, name):
        """The mobile's swept solid: every point that some point of the mobile passes through while it makes a
        full turn about its axis (the union of the mobile turned to every angle). It is a solid of revolution, given
        as a list of horizontal bands (z0, z1, [(r0, r1), ...]): inside a band it holds exactly the points whose
        distance from the axis lies in one of the (disjoint, sorted) intervals. See _swept_bands. Cached per solid."""
        m = self.mobiles[name]
        cache = self.__dict__.setdefault("_swept_cache", {})
        hit = cache.get(name)
        if hit is None or hit[0] is not m["solid"]:
            hit = (m["solid"], _swept_bands(m["solid"], m["axis"]))
            cache[name] = hit
        return hit[1]

    def clear_swept(self, a, b):
        """Check 6 in one-job mode: the intersection volume of the swept solids of mobiles a and b (worked out
        exactly from the bands, circles as true circles). A pair whose swept cylinders (swept_cylinder) do not
        meet is not swept: 0. Returns worst_volume (the swept intersection), z_range of the shared region
        (None if empty) and pruned."""
        ra, za0, za1 = self.swept_cylinder(a)
        rb, zb0, zb1 = self.swept_cylinder(b)
        (xa, ya), (xb, yb) = self.mobiles[a]["axis"], self.mobiles[b]["axis"]
        d = math.hypot(xb - xa, yb - ya)
        if d >= ra + rb or min(za1, zb1) <= max(za0, zb0):
            return {"worst_volume": 0.0, "z_range": None, "pruned": True}
        v, zr = _swept_ivol(self.swept_profile(a), self.swept_profile(b), d)
        if not math.isfinite(v):
            raise ArithmeticError("non-finite volume")
        return {"worst_volume": v, "z_range": zr, "pruned": False}

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

    def hand_shape(self, hand):
        """A hand points and sits above the frame: (lowest z of the hand part - highest z of any fixed part,
        distance of the hand part's centre of volume from its mobile's axis)."""
        mob, part = self.hands[hand]
        p = self.mobiles[mob]["parts"][part]
        ax = self.mobiles[mob]["axis"]
        mesh = p.to_mesh()
        vp = np.asarray(mesh.vert_properties, dtype=np.float64)[:, :3]
        tv = np.asarray(mesh.tri_verts, dtype=np.int64)
        a, b, c = vp[tv[:, 0]], vp[tv[:, 1]], vp[tv[:, 2]]
        v6 = np.einsum("ij,ij->i", a, np.cross(b, c))
        cen = ((a + b + c) * v6[:, None]).sum(axis=0) / (4.0 * v6.sum())
        above = float(vp[:, 2].min() - core.verts(self.fixed)[:, 2].max())
        return above, float(math.hypot(cen[0] - ax[0], cen[1] - ax[1]))

    def hand_area(self, hand):
        """A hand is slender: (area of the hand part seen from the dial side, i.e. its projection on the xy
        plane in mm2, that area as a share of the disc its tip sweeps, pi x hand_reach ** 2).
        One-job mode only; the limit is HAND_AREA_MAX_SHARE."""
        mob, part = self.hands[hand]
        area = float(self.mobiles[mob]["parts"][part].project().area())
        r = self.hand_reach(hand)
        return area, (area / (math.pi * r * r) if r > 0.0 else float("inf"))

    def hand_reach(self, hand):
        mob, part = self.hands[hand]
        V = core.verts(self.mobiles[mob]["parts"][part])
        ax = self.mobiles[mob]["axis"]
        return float(np.hypot(V[:, 0] - ax[0], V[:, 1] - ax[1]).max())

    def tooth_counts(self, a, ta, b, tb):
        """The mesh test's tooth-count condition (SESSION.md Decisions 2026-11-15 01:19, A3): each declared count
        is the number of teeth of that gear, counted (count_teeth) on its whole mobile's section at the height
        where the two mobiles meet (meet_height). The supplied barrel's count is BARREL_TEETH, not measured.
        Measured on the mobiles as drawn (the tolerant test's shift does not change it); cached per mesh.
        Returns {"teeth_match": bool, "declared_teeth": {a: ta, b: tb}, "measured_teeth": {a: n, b: n},
        "teeth_height": z or None}; a count is None when the two mobiles never meet in height."""
        cache = self.__dict__.setdefault("_teeth_cache", {})
        key = (a, b)
        if key not in cache:
            A, ax_a = self.mobiles[a]["solid"], self.mobiles[a]["axis"]
            B, ax_b = self.mobiles[b]["solid"], self.mobiles[b]["axis"]
            z = meet_height(A, ax_a, B, ax_b)
            got = {}
            for name, S, ax in ((a, A, ax_a), (b, B, ax_b)):
                if name == "barrel":
                    got[name] = BARREL_TEETH
                else:
                    got[name] = None if z is None else count_teeth(S, ax, z)
            cache[key] = (z, got)
        z, got = cache[key]
        measured = {a: got[a], b: got[b]}
        return {"teeth_match": measured[a] == ta and measured[b] == tb, "declared_teeth": {a: ta, b: tb},
                "measured_teeth": measured, "teeth_height": z}


def section_outline(solid, axis, z, rays=TEETH_RAYS):
    """The outline of solid's section at height z as seen from the vertical line through axis: for each of `rays`
    equally spaced directions (direction k at 360 k / rays degrees), the largest distance from the axis at which
    that half-line meets the section (0 where it meets none). Exact on the section's polygons."""
    out = np.zeros(rays)
    step = 2.0 * math.pi / rays
    for P in solid.slice(z).to_polygons():
        P = np.asarray(P, dtype=np.float64) - np.asarray(axis, dtype=np.float64)
        if len(P) < 3:
            continue
        Q = np.roll(P, -1, axis=0)
        a0 = np.arctan2(P[:, 1], P[:, 0])
        da = (np.arctan2(Q[:, 1], Q[:, 0]) - a0 + math.pi) % (2.0 * math.pi) - math.pi
        lo, hi = np.minimum(a0, a0 + da), np.maximum(a0, a0 + da)
        k0, k1 = np.ceil(lo / step).astype(np.int64), np.floor(hi / step).astype(np.int64)
        cnt = np.maximum(k1 - k0 + 1, 0)
        if cnt.sum() == 0:
            continue
        edge = np.repeat(np.arange(len(P)), cnt)
        k = k0[edge] + (np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt))
        th = k * step
        ux, uy = np.cos(th), np.sin(th)
        ex, ey = (Q - P)[edge, 0], (Q - P)[edge, 1]
        den = ux * ey - uy * ex
        ok = np.abs(den) > 1e-15
        s = np.where(ok, (P[edge, 0] * ey - P[edge, 1] * ex) / np.where(ok, den, 1.0), 0.0)
        np.maximum.at(out, k % rays, np.where(ok & (s > 0.0), s, 0.0))
    return out


def count_teeth(solid, axis, z):
    """Number of teeth of solid's section at height z about the vertical line through axis: going once round, the
    number of times the outline (section_outline) rises from at most to above the radius halfway between its
    smallest and largest value. 0 when those two differ by less than TEETH_MIN_DEPTH."""
    r = section_outline(solid, axis, z)
    lo, hi = float(r.min()), float(r.max())
    if hi - lo < TEETH_MIN_DEPTH:
        return 0
    up = r > (lo + hi) / 2.0
    return int(np.count_nonzero(up & ~np.roll(up, 1)))


def meet_height(A, ax_a, B, ax_b):
    """The height where two mobiles meet: the heights at which either solid has a vertex, within the z range both
    cover, cut that range into layers; the thickest layer whose middle section has largest distances from the
    two axes (of A's section from ax_a, of B's from ax_b) adding up to more than the distance between the axes
    (ties: the lowest). Returns the middle of that layer, or None if no layer qualifies."""
    VA, VB = core.verts(A), core.verts(B)
    z0, z1 = max(VA[:, 2].min(), VB[:, 2].min()), min(VA[:, 2].max(), VB[:, 2].max())
    if not z1 > z0:
        return None
    zs = np.unique(np.round(np.concatenate([VA[:, 2], VB[:, 2]]), 7))
    zs = np.unique(np.concatenate([[z0], zs[(zs > z0) & (zs < z1)], [z1]]))
    d = math.hypot(ax_b[0] - ax_a[0], ax_b[1] - ax_a[1])

    def reach(S, ax, z):
        best = 0.0
        for P in S.slice(z).to_polygons():
            P = np.asarray(P, dtype=np.float64)
            if len(P):
                best = max(best, float(np.hypot(P[:, 0] - ax[0], P[:, 1] - ax[1]).max()))
        return best
    for i in sorted(range(len(zs) - 1), key=lambda i: (-(zs[i + 1] - zs[i]), zs[i])):
        z = float(zs[i] + zs[i + 1]) / 2.0
        if reach(A, ax_a, z) + reach(B, ax_b, z) > d:
            return z
    return None


def _radial_intervals(cs, ax):
    """The distances from the point ax that the points of the planar region cs take, as sorted disjoint intervals.
    Each connected piece (an outline with its holes) gives one interval: from 0 if ax lies in it (else its
    smallest distance from ax, on an edge) to its largest distance from ax (at a vertex)."""
    out = []
    for comp in cs.decompose():
        loops = [np.asarray(p, dtype=np.float64) - np.asarray(ax, dtype=np.float64) for p in comp.to_polygons()]
        loops = [p for p in loops if len(p) >= 3]
        if not loops:
            continue
        dmax, dmin, crossings = 0.0, float("inf"), 0
        for p in loops:
            q = np.roll(p, -1, axis=0)
            dmax = max(dmax, float(np.hypot(p[:, 0], p[:, 1]).max()))
            e = q - p
            L2 = (e * e).sum(axis=1)
            t = np.clip(-(p * e).sum(axis=1) / np.where(L2 > 0, L2, 1.0), 0.0, 1.0)
            c = p + t[:, None] * e
            dmin = min(dmin, float(np.hypot(c[:, 0], c[:, 1]).min()))
            up = (p[:, 1] > 0) != (q[:, 1] > 0)             # edges that cross the ray from ax along +x
            with np.errstate(divide="ignore", invalid="ignore"):
                x = p[:, 0] - p[:, 1] * e[:, 0] / e[:, 1]
            crossings += int(np.count_nonzero(up & (x > 0)))
        out.append((0.0 if crossings % 2 else dmin, dmax))
    out.sort()
    merged = []
    for r0, r1 in out:
        if merged and r0 <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], r1))
        else:
            merged.append((r0, r1))
    return merged


def _swept_bands(S, ax):
    """The swept solid of S turned about the vertical line through ax (see Movement.swept_profile), as bands.
    The band edges are every height at which S has a vertex. Between two such heights the horizontal section of S
    changes only where a face of S that is neither vertical nor horizontal crosses that height range; where none
    does, the section is the same at every height of the band, and one section at its middle height gives the
    band exactly. Where one does, the range is cut into equal bands at most SWEEP_DZ high, each given by its
    section at its middle height."""
    mesh = S.to_mesh()
    vp = np.asarray(mesh.vert_properties, dtype=np.float64)[:, :3]
    tv = np.asarray(mesh.tri_verts, dtype=np.int64)
    if len(tv) == 0:
        return []
    T = vp[tv]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    nn = np.linalg.norm(n, axis=1)
    nz = np.abs(n[:, 2]) / np.where(nn > 0, nn, 1.0)
    slanted = (nz > 1e-9) & (nz < 1.0 - 1e-9)
    s_lo, s_hi = np.sort(T[slanted, :, 2].min(axis=1)), np.sort(T[slanted, :, 2].max(axis=1))
    zs = np.unique(vp[:, 2])
    zs = zs[np.concatenate(([True], np.diff(zs) > 1e-9))]
    bands = []
    for z0, z1 in zip(zs[:-1], zs[1:]):
        zm = 0.5 * (z0 + z1)
        # slanted faces that span the middle of this range (lowest point below it, highest above it)
        k = int(np.searchsorted(s_lo, zm)) - int(np.searchsorted(s_hi, zm))
        parts = max(1, int(math.ceil((z1 - z0) / SWEEP_DZ - 1e-9))) if k > 0 else 1
        for j in range(parts):
            b0, b1 = z0 + (z1 - z0) * j / parts, z0 + (z1 - z0) * (j + 1) / parts
            iv = _radial_intervals(S.slice(0.5 * (b0 + b1)), ax)
            if iv:
                bands.append((float(b0), float(b1), iv))
    return bands


def _lens(a, b, d):
    """Area shared by two discs of radii a and b whose centres are d apart."""
    if a <= 0.0 or b <= 0.0 or d >= a + b:
        return 0.0
    if d <= abs(a - b):
        return math.pi * min(a, b) ** 2
    ca = max(-1.0, min(1.0, (d * d + a * a - b * b) / (2.0 * d * a)))
    cb = max(-1.0, min(1.0, (d * d + b * b - a * a) / (2.0 * d * b)))
    k = (-d + a + b) * (d + a - b) * (d - a + b) * (d + a + b)
    return a * a * math.acos(ca) + b * b * math.acos(cb) - 0.5 * math.sqrt(max(0.0, k))


def _swept_ivol(pa, pb, d):
    """Volume shared by two swept solids given as bands (_swept_bands) about vertical axes d apart, and the z
    range of the shared region (None if it is empty). An annulus r0..r1 and an annulus s0..s1 share
    L(r1, s1) - L(r1, s0) - L(r0, s1) + L(r0, s0), with L the disc-disc area _lens."""
    total, zlo, zhi = 0.0, float("inf"), float("-inf")
    i = j = 0
    while i < len(pa) and j < len(pb):
        a0, a1, ia = pa[i]
        b0, b1, ib = pb[j]
        lo, hi = max(a0, b0), min(a1, b1)
        if hi > lo:
            area = 0.0
            for r0, r1 in ia:
                for s0, s1 in ib:
                    area += _lens(r1, s1, d) - _lens(r1, s0, d) - _lens(r0, s1, d) + _lens(r0, s0, d)
            if area > 1e-12:
                total += area * (hi - lo)
                zlo, zhi = min(zlo, lo), max(zhi, hi)
        if a1 <= b1:
            i += 1
        else:
            j += 1
    return total, ([zlo, zhi] if total > 0.0 else None)


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


def load_movement(folder, name="movement.json", cache=None, barrel_solid=None, materials=False):
    """folder holds movement.json and parts/<name>.step. Opens only the files movement.json names.
    name: the movement file in folder to read instead of movement.json (a plain file name, e.g. variant_6h.json).
    cache: an optional dict shared between calls; a part file whose name and bytes were loaded before is
    taken from it instead of being read again (the same solid; the result does not depend on the cache).
    barrel_solid: the supplied barrel's solid (default barrel(); the stage mode passes barrel_stage()).
    materials: one-job mode, every mobile declares a material (see Movement)."""
    if not isinstance(name, str) or os.path.basename(name) != name or not name.endswith(".json"):
        raise FormatError("bad movement file name %r" % (name,))
    path = inside(folder, os.path.join(folder, name))
    if os.path.getsize(path) > MAX_JSON_BYTES:
        raise FormatError("%s too large" % name)
    with open(path, "r", encoding="utf-8") as f:
        try:
            doc = json.load(f)
        except ValueError as e:
            raise FormatError("%s is not valid JSON" % name) from e

    def load(name):
        p = part_path(folder, name)
        if p is None:
            if os.path.isfile(os.path.join(folder, "parts", name + ".stl")):
                raise FormatError("parts/%s.stl: parts must be STEP files (parts/%s.step); STL is not accepted" % (name, name))
            raise FormatError("part file parts/%s.step not found" % name)
        key = None
        if cache is not None and os.path.getsize(p) <= MAX_STEP_BYTES:
            import hashlib
            with open(p, "rb") as f:
                key = (name, hashlib.sha256(f.read()).hexdigest())
            if key in cache:            # a solid, or the format error that file gave
                if isinstance(cache[key], FormatError):
                    raise cache[key]
                return cache[key]
        try:
            solid = load_part_file(p)
        except FormatError as e:
            err = FormatError("parts/%s: %s" % (os.path.basename(p), e))
            if key is not None:
                cache[key] = err
            raise err
        if key is not None:
            cache[key] = solid
        return solid
    return Movement(doc, load, barrel_solid, materials=materials)


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
    names = set(movement.all_parts(keyless=True))     # keyless parts only once attach_keyless() has read them
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
    # in slabs along z: memory does not grow with the part's height; same result as
    # core.opening_test(core.voxelize(...)) (deviation exact up to THIN_DEV_CAP_VOX voxels)
    n, dev = core.opening_test_slabs(part, lo * h - 0.0137, tuple(int(v) for v in hi - lo), h,
                                     THIN_ERODE_VOX, THIN_DILATE_VOX, THIN_DEV_CAP_VOX, THIN_SLAB)
    return n, (dev * h if np.isfinite(dev) else 1e9)


# ---------------- gear strength: Lewis form factor, materials, the load case ----------------
def rack_tip_radius(alpha_deg=PRESSURE_ANGLE, addendum=LEWIS_ADDENDUM, dedendum=LEWIS_DEDENDUM):
    """Tip radius of the basic rack, in modules. ISO 53 (20 deg) takes the radius at which the rack's straight flank
    ends exactly at the depth of the addendum: c / (1 - sin a), c = dedendum - addendum (0.38 at 20 deg). At 25 deg
    that radius (0.433) is larger than the rack tooth's tip can carry (the two rounds would overlap), so the tip is
    then a full round: half the tip width x tan(45 deg + a/2) (0.317 at 25 deg)."""
    a = math.radians(alpha_deg)
    c = dedendum - addendum
    half_tip = math.pi / 4.0 - dedendum * math.tan(a)
    return min(c / (1.0 - math.sin(a)), half_tip * math.tan(math.pi / 4.0 + a / 2.0))


def _rack_cut_tooth(z, alpha_deg, n=4000, grid=20001):
    """Half of one tooth (module 1) of a z-tooth spur gear cut by the basic rack without profile shift, as
    (R, phi, fillet_phi): for each radius R the angle phi from the tooth's centre line to its flank (the smallest
    angle the cutter reaches at that radius), and the angle the cutter's tip round alone reaches (inf where it does
    not). The flank and the tip round of the rack are carried through every rolling position by their envelope
    (a rack point is cutting when its profile normal passes through the pitch point); every branch, the loops of an
    undercut included, is kept, and the tooth is what no branch reaches."""
    a = math.radians(alpha_deg)
    r = z / 2.0
    rho = rack_tip_radius(alpha_deg)
    v0 = -LEWIS_DEDENDUM + rho                    # centre of the tip round, rack frame (v: height, 0 on the pitch line)
    u0 = (rho + math.cos(a) * math.pi / 4.0 - math.sin(a) * v0) / math.cos(a)
    vt = v0 - rho * math.sin(a)                   # where the round meets the straight flank
    v = np.linspace(vt, LEWIS_ADDENDUM + 0.05, n)
    flank = (math.pi / 4.0 - v * math.tan(a), v, np.full(n, -math.cos(a)), np.full(n, -math.sin(a)))
    th = np.linspace(math.atan2(-math.sin(a), -math.cos(a)), -math.pi / 2.0, n)
    round_ = (u0 + rho * np.cos(th), v0 + rho * np.sin(th), np.cos(th), np.sin(th))
    R = np.linspace(r - LEWIS_DEDENDUM + 1e-6, r + LEWIS_ADDENDUM, grid)
    out = []
    for u, vv, nu, nv in (flank, round_):
        psi = (u - vv * nu / nv) / r              # the gear's turn at which this rack point cuts
        X, Y = u - r * psi, r + vv
        gx = np.cos(psi) * X + np.sin(psi) * Y    # into the gear's frame (turned back by psi)
        gy = -np.sin(psi) * X + np.cos(psi) * Y
        rr, pp = np.hypot(gx, gy), np.arctan2(gx, gy)
        best = np.full(grid, np.inf)
        d = np.sign(np.diff(rr))
        cuts = list(np.nonzero(d[1:] != d[:-1])[0] + 1) + [len(rr) - 1]
        start = 0
        for c in cuts:                            # each piece monotone in radius
            x, y = rr[start:c + 1], pp[start:c + 1]
            if x[0] > x[-1]:
                x, y = x[::-1], y[::-1]
            if len(x) > 1:
                best = np.minimum(best, np.interp(R, x, y, left=np.inf, right=np.inf))
            start = c
        out.append(best)
    return R, np.minimum(out[0], out[1]), out[1]


def lewis_form_factor(z, alpha_deg=PRESSURE_ANGLE):
    """Lewis form factor Y of a z-tooth full-depth involute spur gear, by Lewis's method: the tangential load
    W_t acts at the tip of one tooth, on its centre line at the tip circle (the cantilever of Shigley, Mechanical
    Engineering Design, section 14-1); the weakest section is where the parabola of constant strength with its
    vertex at the load point is tangent to the root fillet; there, with t the tooth thickness and l the distance
    from the load point, sigma = 6 W_t l / (b t^2) = W_t / (b m Y), so Y = t^2 / (6 l m), the smallest over the
    fillet. The tooth is the one the basic rack cuts (addendum 1.0 m, dedendum 1.25 m, tip radius
    rack_tip_radius(), no profile shift; undercut included); the fillet is the part of the flank the rack's tip
    round cuts. The radial (compressive) component of the load is neglected, as in Lewis. Y does not depend on
    the module. A tooth pointed below the tip circle is loaded at its point."""
    R, phi, fil = _rack_cut_tooth(z, alpha_deg)
    ok = np.isfinite(phi) & (phi > 0.0)
    R, phi, fil = R[ok], phi[ok], fil[ok]
    x, y = R * np.sin(phi), R * np.cos(phi)       # half thickness, height on the centre line
    top = float(R[-1])                            # tip circle (or the point of a pointed tooth)
    on_fillet = fil <= phi + 1e-12
    h = top - y
    sel = on_fillet & (h > 1e-9)
    if not sel.any():
        raise ArithmeticError("no root fillet found for %d teeth" % z)
    return float((4.0 * x[sel] ** 2 / (6.0 * h[sel])).min())


def lewis_table_doc(lo=MIN_TEETH, hi=MAX_TEETH):
    """The frozen table as written to geometry/data/lewis_y.json: Y rounded to LEWIS_DECIMALS for every tooth count."""
    return {"pressure_angle": PRESSURE_ANGLE, "addendum": LEWIS_ADDENDUM, "dedendum": LEWIS_DEDENDUM,
            "rack_tip_radius": round(rack_tip_radius(), 6), "decimals": LEWIS_DECIMALS,
            "method": "geometry.watch.lewis_form_factor",
            "Y": {str(z): round(lewis_form_factor(z), LEWIS_DECIMALS) for z in range(lo, hi + 1)}}


def _load_lewis_table():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "lewis_y.json")
    if not os.path.isfile(path):
        return {}                     # only while the table is being built (tests/test_strength.py --write-lewis)
    with open(path) as f:
        doc = json.load(f)
    if doc.get("pressure_angle") != PRESSURE_ANGLE or doc.get("addendum") != LEWIS_ADDENDUM \
            or doc.get("dedendum") != LEWIS_DEDENDUM or doc.get("decimals") != LEWIS_DECIMALS:
        raise RuntimeError("geometry/data/lewis_y.json was made for other constants; rebuild it "
                           "(python3 tests/test_strength.py --write-lewis)")
    return {int(k): float(v) for k, v in doc["Y"].items()}


LEWIS_Y = _load_lewis_table()          # teeth -> Y, every tooth count from MIN_TEETH to MAX_TEETH


def check_strength_sheets(folder=None):
    """The supplier-sheet cells the strength constants come from, read from the sheet text. Returns a list of
    differences (empty when every constant equals its cell). folder: the datasheets folder (default A's)."""
    if folder is None:
        folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spikes", "keyless", "datasheets")
    bad = []
    with open(os.path.join(folder, STRENGTH_SHEETS["DS-101"]), encoding="utf-8") as f:
        ds101 = f.read()
    row = re.search(r"^\|\s*Slipping torque of the bridle[^|\n]*\|[^|\n]*\|\s*\*\*([0-9.]+) to ([0-9.]+)\*\*\s*\|\s*$", ds101, re.M)
    if not row:
        bad.append("DS-101 Table 2a: row 'Slipping torque of the bridle' with a bold 'a to b' cell not found")
    elif float(row.group(2)) != BARREL_TORQUE_MAX_NMM:
        bad.append("DS-101 Table 2a slipping torque upper end is %s, BARREL_TORQUE_MAX_NMM is %s" % (row.group(2), BARREL_TORQUE_MAX_NMM))
    with open(os.path.join(folder, STRENGTH_SHEETS["DS-201"]), encoding="utf-8") as f:
        ds201 = f.read()
    sec = re.search(r"^## 8\..*?\n(?=## )", ds201, re.M | re.S)
    tab = re.search(r"\*\*Design allowables[^\n]*\n\n((?:\|[^\n]*\n)+)", sec.group(0)) if sec else None
    if not tab:
        bad.append("DS-201 section 8: design allowables table not found")
        return bad
    rows = []
    for line in tab.group(1).splitlines()[2:]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        mpa = re.match(r"([0-9.]+)", cells[-1])
        rows.append((cells[0], float(mpa.group(1)) if mpa else None))
    want = [(cell, mpa) for cell, _, mpa, _ in DS201_ALLOWABLE_ROWS]
    if rows != want:
        bad.append("DS-201 section 8 allowables are %r, DS201_ALLOWABLE_ROWS has %r" % (rows, want))
    codes = re.search(r"^## 2\..*?\n(?=## )", ds201, re.M | re.S)
    for _, code, _, _ in DS201_ALLOWABLE_ROWS:
        if not codes or not re.search(r"^\|\s*%s\s*\|" % re.escape(code), codes.group(0), re.M):
            bad.append("DS-201 section 2: ordering code %s not found" % code)
    return bad


def going_train(m, runs):
    """The going train: the declared meshes on the path from the barrel to the mobile that carries the seconds
    hand, through declared meshes that pass the mesh test (the shortest such path; among equals, the one found
    first in declaration order). Returns (list of indices into m.meshes, None) or (None, reason)."""
    sec = m.hands["seconds"][0]
    prev = {"barrel": None}
    queue = ["barrel"]
    while queue:
        cur = queue.pop(0)
        for i, ((a, _, b, _), x) in enumerate(zip(m.meshes, runs)):
            if not Movement.mesh_passes(x):
                continue
            for src, dst in ((a, b), (b, a)):
                if src == cur and dst not in prev:
                    prev[dst] = (cur, i)
                    queue.append(dst)
    if sec not in prev:
        return None, "the seconds hand's mobile '%s' is not driven from the barrel through meshes that pass the mesh test" % sec
    path, cur = [], sec
    while prev[cur] is not None:
        cur, i = prev[cur]
        path.append(i)
    return path[::-1], None


def teeth_part(m, name, by_part):
    """The part of mobile `name` that holds its teeth in a rated mesh (Decisions 2026-11-14 21:43, item 2): the part
    holding the largest volume of the mesh's drive-test overlap with the other mobile (by_part: that mobile's entry
    of Movement.drive_parts, summed over the drive test's steps); ties: the first in the mobile's parts list.
    A one-part mobile: that part. Returns (part, by_part or None); (None, None) for a mobile that lists no parts."""
    names = list(m.mobiles[name].get("parts", {}))
    if not names:
        return None, None
    if len(names) == 1:
        return names[0], None
    by_part = by_part or {}
    best = names[0]
    for pn in names[1:]:
        if by_part.get(pn, 0.0) > by_part.get(best, 0.0):
            best = pn
    return best, {pn: by_part.get(pn, 0.0) for pn in names}


def strength_run(m, runs, driven):
    """The strength check of movement m: tooth bending by Lewis under the load case. runs: m.mesh_run of every
    declared mesh, in m.meshes order (None if the mesh test did not run); driven: m.speeds(passing meshes)[0].
    Rated: the going train (going_train: barrel to the seconds hand's mobile through passing meshes; the motion
    work and other branches are not rated, as a watchmaker rates a train: the cannon pinion slips; Decisions,
    orchestrator's answer (B) to builder S). For each rated mesh: T at the driver = BARREL_TORQUE_MAX_NMM x
    |barrel speed / driver speed| (N·mm), F = TOOTH_LOAD_FACTOR x T / (m z_D / 2) (N) with
    m = 2 x axis distance / (z_D + z_N) (mm),
    b = the smallest height in z of the drive test's new overlap over its steps (mm), sigma = F / (b m Y(z)) (MPa)
    for each gear with its own z, in the material of the part of its mobile that holds its teeth (teeth_part:
    that part's entry of "part_materials", which defaults to the mobile's "material"), the supplied barrel's gear
    not rated. A rated mesh
    whose drive test fails has no b, and fails (cannot happen on the path, which passes the mesh test).
    Returns (passed, details); details "margin" = allowable / sigma - 1 (passes when >= 0)."""
    if runs is None:
        return False, {"error": "the mesh test did not run to the end"}
    path, why = going_train(m, runs)
    if path is None:
        return False, {"error": why, "meshes": []}
    out, ok = [], True
    wb = abs(driven.get("barrel", m.barrel_speed))
    for i in path:
        (a, ta, b, tb), x = m.meshes[i], runs[i]
        T = BARREL_TORQUE_MAX_NMM * float(wb / abs(driven[a]))
        mod = x["module"]
        F0 = T / (mod * ta / 2.0)                   # nominal tooth load on the driver's pitch circle
        F = TOOTH_LOAD_FACTOR * F0                  # the rated load: with the load factor for dry meshing
        e = {"pair": "%s/%s" % (a, b), "torque_nmm": T, "nominal_force_n": F0, "load_factor": TOOTH_LOAD_FACTOR,
             "force_n": F, "module": mod}
        out.append(e)
        if not Movement.drive_passes(x):
            e["error"] = "the drive test fails, so the face width is not measured"
            ok = False
            continue
        bw = x["smallest_drive_height"]
        e["face_width"] = bw
        e["gears"] = {}
        split = None
        for name, z in ((a, ta), (b, tb)):
            if name == "barrel":
                e["gears"][name] = {"teeth": z, "rated": False}
                continue
            Y = LEWIS_Y[z]
            sig = F / (bw * mod * Y)
            if len(m.mobiles[name].get("parts", {})) > 1 and split is None:
                split = m.drive_parts(a, ta, b, tb)
            part, by_part = teeth_part(m, name, (split or {}).get(name))
            pm = m.mobiles[name].get("part_materials")
            mat = pm[part] if pm and part is not None else m.mobiles[name]["material"]
            allow = MATERIAL_ALLOWABLE_MPA[mat]
            e["gears"][name] = {"teeth": z, "Y": Y, "sigma_mpa": sig, "part": part, "material": mat,
                                "allowable_mpa": allow, "margin": allow / sig - 1.0}
            if by_part is not None:
                e["gears"][name]["drive_overlap_by_part"] = by_part
            ok = ok and sig <= allow
    margins = [g["margin"] for e in out for g in e.get("gears", {}).values() if "margin" in g]
    return ok and bool(out), {"meshes": out, "smallest_margin": min(margins) if margins else None,
                              "barrel_torque_nmm": BARREL_TORQUE_MAX_NMM, "going_train": [out_["pair"] for out_ in out]}

