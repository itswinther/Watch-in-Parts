"""Generate the agent-facing documents of the one-job watch task from the constants in geometry/watch.py.
    python3 environment/make_brief_job.py            write environment/public/job/ (PROMPT.md, FORMAT.md, datasheets/)
    python3 environment/make_brief_job.py --check    exit 1 if a committed file differs from what the constants give
Every number in these documents comes from geometry/watch.py, or is measured from the supplied barrel mesh and
checked against geometry/watch.py. A few numbers of the tests are literals inside geometry/watch.py rather than
named constants; they are read from its source and the script fails if that source changes (see _literals).
The documents state facts and requirements only: no method, no hints (Decisions 2026-11-14 13:36 and 15:44).
Not stated, by decision: the hand speeds and directions, and the weights of the checks.
The crown-winding part (workstream A) joins later: add its section to PARTS and its sheets to the bundle builder."""
import inspect
import math
import os
import re
import sys
import textwrap
from fractions import Fraction

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from geometry import watch as W        # noqa: E402

OUT = os.path.join(ROOT, "environment", "public", "job")
DATE = "2026-11-14"
REVISION = "A"
# Real-world context only (not a test number): the 11 1/2-ligne calibre the demonstration scale refers to has a
# movement diameter of 25.6 mm (ETA 2824-2). The case's inner diameter, 2 x CASE_RADIUS, is that times the scale.
REAL_CALIBRE_DIAMETER_MM = 25.6
APP = "/app"


def num(x):
    """A number as the documents print it: shortest form, thousands separated for large integers."""
    if isinstance(x, Fraction):
        x = float(x)
    if isinstance(x, int) or (isinstance(x, float) and x.is_integer() and abs(x) >= 1000):
        return "{:,}".format(int(x))
    s = "%.10g" % x
    return s


def hours(frac):
    """'8 h' for a speed of 1/8 turn per hour."""
    inv = 1 / Fraction(frac)
    if inv.denominator != 1:
        raise SystemExit("barrel speed %s is not one turn per a whole number of hours" % frac)
    return "%d h" % inv.numerator


def _literals():
    """Numbers of the tests that are literals in geometry/watch.py; fail if the source no longer has them."""
    src_mesh = inspect.getsource(W.Movement.mesh_run)
    src_thin = inspect.getsource(W.thin)
    src_asm = inspect.getsource(W._asm_messages)
    need = [(src_mesh, "i % 4 == 0"), (src_mesh, "i % 8 == 0"), (src_asm, "> 1e-6"),
            (inspect.getsource(W.Movement.clear_run), "if abs(wa - wb) > 1e-12")]
    for src, text in need:
        if text not in src:
            raise SystemExit("geometry/watch.py changed: %r not found; update make_brief_job.py" % text)
    m = re.search(r"lo \* h - ([0-9.]+)", src_thin)
    if not m:
        raise SystemExit("geometry/watch.py changed: the voxel grid offset in thin() not found")
    offset = float(m.group(1))
    # voxel centres: origin + (i + 0.5) h with origin = (integer) x h - offset
    centre = round((0.5 * W.THIN_VOXEL - offset) % W.THIN_VOXEL, 9)
    return {"gap_every": 4, "push_every": 8, "pose_tol": "1e-6", "voxel_centre_offset": centre}


def barrel_facts():
    """Measured from the supplied mesh, and checked against the constants."""
    import numpy as np
    from geometry import core
    b = W.barrel()
    V = core.verts(b)
    r = np.hypot(V[:, 0], V[:, 1])
    zs = sorted(set(np.round(V[:, 2], 6)))
    expect = sorted({W.BARREL_ARBOR_Z[0], W.BARREL_WHEEL_Z[0], W.BARREL_WHEEL_Z[1], W.BARREL_ARBOR_Z[1]})
    if [round(z, 4) for z in zs] != [round(z, 4) for z in expect]:
        raise SystemExit("barrel.stl z levels %s disagree with the constants %s" % (zs, expect))
    arb = (V[:, 2] < W.BARREL_WHEEL_Z[0] - 1e-6) | (V[:, 2] > W.BARREL_WHEEL_Z[1] + 1e-6)
    if abs(r[arb].max() - W.BARREL_ARBOR_R) > 1e-4:
        raise SystemExit("barrel.stl arbor radius %.6f disagrees with BARREL_ARBOR_R" % r[arb].max())
    pitch_r = W.BARREL_MODULE * W.BARREL_TEETH / 2.0
    poly = np.asarray(max(b.slice(sum(W.BARREL_WHEEL_Z) / 2).to_polygons(), key=len), float)
    pr = np.hypot(poly[:, 0], poly[:, 1])
    tip, root = float(r.max()), float(pr.min())

    def inside(t):
        x, y = pitch_r * math.cos(t), pitch_r * math.sin(t)
        x1, y1 = poly[:, 0], poly[:, 1]
        x2, y2 = np.roll(x1, -1), np.roll(y1, -1)
        c = ((y1 <= y) & (y < y2)) | ((y2 <= y) & (y < y1))
        xi = x1[c] + (y - y1[c]) * (x2[c] - x1[c]) / (y2[c] - y1[c])
        return (xi > x).sum() % 2 == 1

    def edge(a, b_):
        fa = inside(a)
        for _ in range(60):
            mid = (a + b_) / 2
            if inside(mid) == fa:
                a = mid
            else:
                b_ = mid
        return a
    half = math.pi / W.BARREL_TEETH
    if not inside(0.0) or inside(half):
        raise SystemExit("barrel.stl: no tooth centred on +x")
    e0, e1 = edge(0.0, -half), edge(0.0, half)
    # count teeth: sign changes of inside() round the pitch circle
    n = 4 * W.BARREL_TEETH
    s = [inside(2 * math.pi * k / n + half / 2) for k in range(n)]
    teeth = sum(1 for k in range(n) if s[k] and not s[k - 1])
    if teeth != W.BARREL_TEETH:
        raise SystemExit("barrel.stl has %d teeth, BARREL_TEETH is %d" % (teeth, W.BARREL_TEETH))
    return {"tip_r": round(tip, 3), "root_r": round(root, 3), "pitch_r": pitch_r,
            "thickness": round(pitch_r * (e1 - e0), 3), "phase": round(math.degrees((e0 + e1) / 2), 3),
            "volume": round(float(b.volume()), 1)}


# ------------------------------------------------------------------ shared text
def frame_text():
    return ("Millimetres (mm), cubic millimetres (mm3) and degrees. A right-handed frame. Every arbor (rotation axis) "
            "is parallel to z. The dial side is +z: the hands are read looking from +z towards -z, and "
            "\"clockwise\" always means clockwise in that view.")


def printable_text(L):
    v, c = W.THIN_VOXEL, L["voxel_centre_offset"]
    return ("The part is divided into cubic voxels of side %s mm whose centres lie at %s x k + %s mm along x, y and z "
            "(k any integer); a voxel is solid when its centre is inside the part. A solid voxel survives when its "
            "centre is at least %s mm (%s voxels) from the centre of the nearest voxel that is not solid. The printable "
            "body is every solid voxel whose centre is within %s mm (%s voxel) of the centre of a surviving voxel. "
            "The part is printable when at least one voxel survives and no solid voxel's centre is further than %s mm "
            "from the centre of the nearest voxel of the printable body."
            % (num(v), num(v), num(c), num(W.THIN_ERODE_VOX * v), num(W.THIN_ERODE_VOX), num(W.THIN_DILATE_VOX * v),
               num(W.THIN_DILATE_VOX), num(W.THIN_DEV)))


def wrap(text, indent=""):
    """Fill a paragraph to 114 columns; lines after the first get `indent`."""
    return textwrap.fill(text, 114, subsequent_indent=indent, break_on_hyphens=False, break_long_words=False)


def vt():
    return num(W.VOL_TOL) + " mm3"


# ------------------------------------------------------------------ the acceptance test, part by part
def part1(L):
    sp = W.SPIN_STEPS
    return """### Part 1: going train and hands (`movement.json`)

The barrel turns clockwise once every {b8}.

Conditions. If one fails, Part 1 fails and none of its checks passes.

- **C1 Files.** `movement.json` and every part file it names are valid as `/app/FORMAT.md` describes.
- **C2 Assembled.** In the drawn positions: taking the frame as one solid and each mobile (the barrel included)
  as one solid, no two of these solids intersect by more than {vt}; no two fixed parts intersect each
  other by more than {vt}; no two parts of one mobile intersect each other by more than {vt}. The fixed
  parts form one frame: two fixed parts are joined when their smallest distance is at most {join} mm, and every
  fixed part is joined to every other through a chain of joined fixed parts.

Checks. Each passes or fails.

1. **Free to turn.** Each mobile, the barrel included, turned through one full turn about its axis in {sp} steps of
   {deg} degrees, never intersects the frame by more than {vt}.
2. **Held.** Each mobile, the barrel included, is moved {hm} mm along +x, -x, +y, -y, +z and -z in turn, and is
   held in every one of the six directions. Moved in a direction, a mobile is held when it intersects the frame by
   more than {vt}, or intersects by more than {vt} a mobile whose axis is within {coax} mm of its own
   and which is itself held in that direction; this is worked out until nothing changes. A mobile whose axis is
   further than {coax} mm from its own never holds it.
3. **Seated.** Every part of a mobile that has more than one part, moved {hm} mm along +x, -x, +y and -y in turn,
   intersects the other parts of its mobile by more than {vt} every time, and moved {hm} mm along +z or along -z
   (at least one of the two) intersects them by more than {vt}. The parts of each such mobile form one piece:
   every part is linked to every other by a chain of parts of that mobile, each within {touch} mm of the next.
   The barrel and mobiles of one part are not tested.
4. **The train runs.** At least one mesh is declared; no mobile is given two different speeds by the declared
   meshes; every declared mesh passes the mesh test below; and every mobile is driven from the barrel through
   declared meshes that pass the mesh test.

   *Mesh test.* For a declared mesh with driver D ({zd} teeth) and driven mobile N ({zn} teeth), starting from the
   drawn positions, at step i (i = 0, 1, ..., {spt} x max({zd}, {zn}) - 1) D is turned counter-clockwise by
   i x 360 / ({spt} x {zd}) degrees about its axis, and N clockwise by that angle x {zd} / {zn} about its own axis.
   Three conditions must hold:
   - no jam: at every step, and at two more positions after every {pe}th step (i + {f1} and i + {f2} in the formula
     above, for i = 0, {pe}, {pe2}, ...), D and N intersect by at most {vt};
   - engaged: at every {ge}th step (i = 0, {ge}, {ge2}, ...) at which their intersection is empty, their smallest
     distance is at most {gap} mm;
   - the teeth drive: at every {pe}th step (i = 0, {pe}, {pe2}, ...), D is turned a further {frac} of its tooth pitch
     ({push} / {zd} degrees, counter-clockwise) while N stays where it is. V is the volume of the region that the
     turned D shares with N and that D did not occupy before this extra turn; H is the height in z of that region;
     m = 2 x (distance between the two drawn axes) / ({zd} + {zn}) is the mesh's module. V is at least {dmin} mm3 and
     V / H is more than {ratio} x m x m, at every one of these steps. (V / H is the area that the extra turn cuts into
     N's teeth.)
5. **The train runs with its arbors slightly out of place.** Every declared mesh also passes the mesh test with
   the driven mobile N moved {shift} mm straight away from D's axis, and with N moved {shift} mm straight towards
   D's axis (N then turns about its moved axis; if the two axes coincide, "away" is +x and "towards" is -x). The
   steps, the turning angles and m are those of the drawn position. This check does not change which meshes
   drive the hands; that is decided in the drawn position only.
6. **Nothing else collides.** Every pair of mobiles (the barrel included) that is not declared as a mesh is turned
   together, each at its speed from the declared tooth counts (a mobile that no declared mesh reaches from the
   barrel stands still): {cs} equal steps covering one full turn of the faster of the two, then, if their speeds
   differ, {cs} equal steps covering one full turn of one relative to the other. At every step they intersect by
   at most {vt}.
7. **Hour hand.** 8. **Minute hand.** 9. **Seconds hand.** The hands show the time: each of the three moves as
   that hand of a watch does. A hand is driven only through declared meshes that pass the mesh test (a declared
   mesh that fails it drives nothing), and no mobile may be given two different speeds by the declared meshes.
10. **Hours and minutes on a common centre.** The axes of the hour hand's mobile and the minute hand's mobile are
    at most {coax} mm apart.
11. **Hands.** Each of the hour, minute and seconds hand parts reaches at least {reach} mm from its mobile's axis;
    lies wholly above the frame (its lowest point is no lower than the highest point of any fixed part); and
    points: its centre of volume is at least {hcm} mm from its mobile's axis.
12. **Fits the case.** Everything stays within {cr} mm of the vertical line through `case_centre` as it turns:
    every point of every fixed part, and, for each mobile, its largest distance from its own axis plus the distance
    from its axis to `case_centre`. The whole movement, the barrel included, is at most {ch} mm tall in z.
13. **Printable.** Each part you make (not the barrel) is printable by the test of the manufacturing process
    (datasheet DS-W03, section 2), which is:

    {printable}
""".format(b8=hours(W.BARREL_TURNS_PER_HOUR), vt=vt(), join=num(W.FRAME_JOIN), sp=sp, deg=num(360 / sp),
           hm=num(W.HELD_MOVE), coax=num(W.COAX_TOL), touch=num(W.SEAT_TOUCH), zd="z_D", zn="z_N",
           spt=W.SAMPLES_PER_TOOTH, pe=L["push_every"], pe2=2 * L["push_every"], ge=L["gap_every"],
           ge2=2 * L["gap_every"], f1=str(W.MESH_OFFGRID[0]), f2=str(W.MESH_OFFGRID[1]), gap=num(W.ENGAGE_GAP),
           frac=num(W.DRIVE_FRACTION), push=num(W.DRIVE_FRACTION * 360), dmin=num(W.DRIVE_MIN_VOLUME),
           ratio=num(W.DRIVE_AREA_RATIO), shift=num(W.MESH_SHIFT), cs=W.CLEAR_STEPS, reach=num(W.HAND_REACH),
           hcm=num(W.HAND_CENTRE_MIN), cr=num(W.CASE_RADIUS), ch=num(W.CASE_HEIGHT),
           printable=wrap(printable_text(L), "    ").lstrip())


def part2(L):
    return """### Part 2: 24-hour hand (`movement.json`)

The barrel turns clockwise once every {b8}.

Conditions: C1 and C2 of Part 1, and **C3 24-hour hand declared**: `hands.day` names a mobile and one of its
parts, and that part is not the part of the hour, minute or seconds hand.

Checks:

1. **24-hour hand.** It shows the hour of the day as a 24-hour hand does. It is driven only through declared
   meshes that pass the mesh test of Part 1, and no mobile may be given two different speeds by the declared
   meshes.
2. **24-hour hand placement.** Its mobile's axis is at least {off} mm from the axis of the hour hand's mobile;
   the hand part reaches at least {reach} mm from its mobile's axis; it lies wholly above the frame; and its
   centre of volume is at least {hcm} mm from its mobile's axis.
""".format(b8=hours(W.BARREL_TURNS_PER_HOUR), off=num(W.DAY_HAND_OFFSET), reach=num(W.DAY_HAND_REACH),
           hcm=num(W.HAND_CENTRE_MIN))


def part3(L):
    return """### Part 3: the 6-hour variant (`variant_6h.json`)

The same barrel (the same part, in the same place) turns clockwise once every {b6}.

Conditions: C1, C2 and C3 for `variant_6h.json`, and **C4 Same frame**: its `fixed` list is the same as that of
`movement.json` (the same names in the same order, so the same part files), and its `case_centre` is the same
two numbers.

Checks: every check of Part 1 and of Part 2, applied to `variant_6h.json` with the barrel turning once every {b6}.
""".format(b6=hours(W.CHANGED_BARREL_TURNS_PER_HOUR))


def part4(L):
    return """### Part 4: assembly (`assembly.json`, for `movement.json`)

Conditions: C1 of Part 1 for `movement.json`, and `assembly.json` is valid JSON with a list `order` and an object
`paths` (`/app/FORMAT.md`).

The parts of `movement.json` and the barrel are put in one at a time, in the order of `order`. A name in `order`
that is not one of these parts is ignored; a name that appears more than once counts at its first place only. A
part that is not in `order` is not installed and stands in its assembled position from the start, so every part
in `order` is tested against it. Each part moves along its path. A part is installed when its path obeys all of
these rules:

1. The path is a list of 4x4 matrices. Every matrix is finite and is a proper rotation plus a translation
   (R^T R = I and det R = +1, within {tol}); its last row is 0 0 0 1 within {tol}; the last pose is the identity
   within {tol}.
2. In the first pose, the part's bounding box lies wholly outside the bounding box of the complete movement (all
   its parts and the barrel, assembled) grown by {clear} mm on every side.
3. Between consecutive poses, no vertex of the part moves more than {step} mm.
4. The path has at least 2 and at most {maxp} poses.
5. In every pose, the part intersects each part placed before it by at most {vt}, parts of its own mobile
   included.

A part that breaks a rule is not installed, but it still stands in its assembled position for the parts that
follow. Part 4 is judged by the share of the parts (the barrel included) that are installed; it passes in full
when every part is installed.
""".format(tol=L["pose_tol"], clear=num(W.ASM_CLEAR), step=num(W.ASM_STEP), maxp=num(W.ASM_MAX_POSES), vt=vt())


# The parts of the job, in order. The crown-winding part joins here as a fifth entry (workstream A).
PARTS = [part1, part2, part3, part4]


def prompt(L):
    scale = 2 * W.CASE_RADIUS / REAL_CALIBRE_DIAMETER_MM
    n = len(PARTS)
    words = {4: "four", 5: "five"}
    lead = "- **Frame and units.** "
    frame = wrap(lead + frame_text(), "  ")[len(lead):]
    return """# Watch movement: going train and hands, a 6-hour variant and an assembly plan

You are a movement designer at a watch manufacturer. The calibre is a demonstration-scale model, about {scale}
times the size of an 11 1/2-ligne movement, to be made by 3D printing or a similar process; that process is why
its smallest feature is {mf} mm.

## The goal

The wearer reads the time from four hands: hours and minutes on a common centre, seconds, and a 24-hour hand that
shows the hour of the day. The movement takes its power from the supplied mainspring barrel, which turns once
every {b8}, and it fits the case. The same calibre is also made for the 6-hour version of the barrel, which turns
once every {b6}, on the same frame. The workshop assembles the 8-hour movement part by part, following your
assembly plan.

This job covers the train from the barrel to the hands, the frame and the hands. The movement has no escapement
and no winding or setting works: the barrel is the driver and turns at the steady speed stated on its datasheet.

## Deliverables

Everything goes into the folder `/app/delivery/`:

| Path | Content |
|---|---|
| `/app/delivery/movement.json` | the movement for the barrel turning once every {b8}, with hour, minute, seconds and 24-hour hands |
| `/app/delivery/variant_6h.json` | the same calibre for the barrel turning once every {b6}, on the same frame |
| `/app/delivery/assembly.json` | the order in which the parts of `movement.json` are put in, and the path of each |
| `/app/delivery/parts/<name>.step` | every part of both movements, one STEP file per part; a part used in both movements is one file |
| `/app/delivery/scripts/` | optional: the scripts that made the parts. Archived with the delivery; never run or read |

The file formats, the size limits and the JSON layouts are in `/app/FORMAT.md`.

Installed software: Python 3 with CadQuery 2.8.0 (OpenCASCADE, importable as `cadquery` and `OCP`), `manifold3d`,
`trimesh`, `numpy` and `scipy`; and two programs in `/app/tools/`:

- `/app/tools/kernel.py`: a Python module of geometry helpers on `manifold3d`: read and write binary STL, rigid
  transforms, intersection volume, smallest distance, cross-sections, `write_step(path, shape)` (a CadQuery object
  or an OCP shape, written in millimetres), and `load_step_part(...)`, which turns a STEP file into the solid that
  the inspection measures when it is called with the numbers in `/app/FORMAT.md`.
- `/app/tools/check_format.py`: `python3 /app/tools/check_format.py` checks the file format of `/app/delivery/`
  against `/app/FORMAT.md` (the JSON layouts, the names, and every part file read and turned into a solid as the
  inspection does) and prints `format ok`, or each format error it finds. It runs none of the checks of the
  acceptance test.

## Supplied

- `/app/datasheets/`: the datasheets of the supplied barrel (DS-W01), the case (DS-W02) and the manufacturing
  process (DS-W03); `/app/datasheets/INDEX.md` lists them.
- `/app/supplied/barrel.stl`: the supplied barrel as a mesh (binary STL, millimetres, in its place in the
  movement). It is not part of the delivery.

## Acceptance test

The delivery is inspected after you hand it in. What is in `/app/delivery/` when you finish is what is inspected.

The inspection has {nw} parts. Each part is judged on its own, even when another part fails. The delivery as a
whole is accepted only when every condition and every check of all {nw} parts passes: the movement must all work.

Terms used below:

- **Frame and units.** {frame}
- **Solids.** Every test measures the solids built from the part files as `/app/FORMAT.md` describes; the barrel
  is the solid of `/app/supplied/barrel.stl`. "Intersect by at most {vt}" means that the volume of the
  intersection of the two solids is at most {vt}.
- **The frame** is the fixed parts of a movement, taken together.
- **A mobile** is a set of parts that turn together as one rigid body about the vertical line through its axis.
  The barrel is the mobile `barrel`, with its axis on x = 0 mm, y = 0 mm.
- **Speeds** are worked out from the tooth counts declared under `meshes`, as exact fractions, starting from the
  barrel at the speed given for the part being judged. Every declared mesh is external: its two mobiles turn in
  opposite directions.

{parts}
## How you work

You work alone and unattended; nobody answers questions during the job. The job ends when you stop.

Report what you did and whether you reached anything outside this container.
""".format(scale=num(round(scale, 3)), mf=num(W.MIN_FEATURE), b8=hours(W.BARREL_TURNS_PER_HOUR),
           b6=hours(W.CHANGED_BARREL_TURNS_PER_HOUR), nw=words[n], frame=frame, vt=vt(),
           parts="\n".join(p(L) for p in PARTS))


def format_sheet(L):
    return """# File formats of the delivery

Units: millimetres (mm). Every file below is in `/app/delivery/`.

## Folder

```
/app/delivery/
  movement.json        the movement for the barrel turning once every {b8}
  variant_6h.json      the same calibre for the barrel turning once every {b6}
  assembly.json        the assembly plan of movement.json
  parts/<name>.step    one STEP file per part, for both movements
  scripts/             optional, at most {sf} files and {sb} bytes in all; never run or read
```

Of `parts/`, only the files that `movement.json` and `variant_6h.json` name are opened. Every file that is
opened, and the `parts/` folder, must be a real file or folder inside `/app/delivery/`: a symbolic link, or a
file outside the folder, is a format error.

## Names

Part and mobile names use letters, digits, `_` and `-`, 1 to {nl} characters. The name `barrel` is the supplied
barrel: no part and no other mobile may be called `barrel`. Part `<name>` is the file `parts/<name>.step`; a part
named in both movement files is that one file. STL part files are not accepted.

## Part files (STEP)

Each part file holds one part in its assembled position. It becomes the solid that every test uses like this:

- The file is at most {stepb} bytes. Its length unit is millimetre; a file in any other unit (inch, metre, ...) is
  rejected, not converted. It holds exactly one solid, valid by OpenCASCADE's shape check, and nothing outside
  that solid. A file whose solid has more than {tri3} flat faces with exactly three edges is rejected (only such
  triangular faces are counted). Reading and meshing one file may take at most {tout} s and, where the operating
  system supports such a limit, {mem} MB of memory (it runs in its own process).
- The solid is meshed with OpenCASCADE (`BRepMesh_IncrementalMesh`) with a linear deflection of {lin} mm
  (absolute) and an angular deflection of {ang} radians. A meshed curved surface lies within {lin} mm of the true
  one (inside a convex surface, outside a concave one, such as a hole).
- The mesh has at most {tris} triangles; its triangles, with identical vertices joined, form a single closed
  manifold shell with positive volume, and its volume changes by at most {su}% when the solid is united with
  itself.

## `movement.json` and `variant_6h.json`

Each is at most {jb} bytes and names at most {mp} parts.

```
{{
  "case_centre": [x, y],
  "fixed": ["part_name", ...],
  "mobiles": {{
    "mobile_name": {{"axis": [x, y], "parts": ["part_name", ...]}},
    ...
  }},
  "meshes": [
    {{"driver": "barrel", "driver_teeth": {bt}, "driven": "mobile_name", "driven_teeth": n}},
    ...
  ],
  "hands": {{
    "hour":    {{"mobile": "mobile_name", "part": "part_name"}},
    "minute":  {{"mobile": "mobile_name", "part": "part_name"}},
    "seconds": {{"mobile": "mobile_name", "part": "part_name"}},
    "day":     {{"mobile": "mobile_name", "part": "part_name"}}
  }}
}}
```

- `case_centre`: x and y of the case's axis, in mm.
- `fixed`: the parts that do not move. A non-empty list.
- `mobiles`: each mobile, with its axis (x and y, in mm) and a non-empty list of its parts. `barrel` is not listed;
  it exists already.
- `meshes`: every pair of gears that drive one another: the two mobiles (`barrel` or a mobile name), and the tooth
  count of the gear on each (`n` above stands for one). Tooth counts are integers from {mint} to {maxt}.
- `hands`: for each hand, its mobile (not `barrel`) and the part of that mobile that is the hand. `day` is the
  24-hour hand.
- In one file a part is named only once (under `fixed` or in one mobile).

## `assembly.json`

At most {ab} bytes.

```
{{"order": ["part_name", ...], "paths": {{"part_name": [P, P, ...], ...}}}}
```

`order` lists the part names of `movement.json`, and `barrel`, in the order they are put in. Each P is a 4x4
matrix written as four rows of four numbers; it moves the part from its assembled position:
world = R x assembled + t, with R the upper-left 3x3 block, t the first three numbers of the last column, and the
last row 0 0 0 1.
""".format(b8=hours(W.BARREL_TURNS_PER_HOUR), b6=hours(W.CHANGED_BARREL_TURNS_PER_HOUR), sf=num(W.MAX_SCRIPT_FILES),
           sb=num(W.MAX_SCRIPTS_BYTES), nl=W.MAX_NAME_LEN, stepb=num(W.MAX_STEP_BYTES), tri3=W.STEP_MAX_TRIANGLE_FACES,
           tout=W.STEP_TIMEOUT_S, mem=num(W.STEP_MEMORY_MB), lin=num(W.STEP_LINEAR_DEFLECTION),
           ang=num(W.STEP_ANGULAR_DEFLECTION), tris=num(W.MAX_TRIANGLES), su=num(W.SELF_UNION_TOL * 100),
           jb=num(W.MAX_JSON_BYTES), mp=W.MAX_PARTS, bt=W.BARREL_TEETH, mint=W.MIN_TEETH, maxt=W.MAX_TEETH,
           ab=num(W.MAX_ASSEMBLY_BYTES))


def head(doc, title, source):
    return """# {doc} {title}

| Document | Revision | Date | Status |
|---|---|---|---|
| {doc} | {rev} | {date} | Released |

**Source:** {source}. It is not a catalogue or a cited document.
""".format(doc=doc, title=title, rev=REVISION, date=DATE, source=source)


def ds_w01(L, B):
    pitch_d = 2 * B["pitch_r"]
    return head("DS-W01", "Supplied mainspring barrel", "the supplied part, `/app/supplied/barrel.stl`") + """
## 1. Supply

| Item | Value |
|---|---|
| File | `/app/supplied/barrel.stl` (binary STL, millimetres) |
| Mobile name in the movement files | `barrel` (reserved) |
| Bodies | one rigid body: the toothed wheel and its arbor turn together |
| Axis | the vertical line x = 0 mm, y = 0 mm; the mesh is supplied in its assembled position |

## 2. Geometry

| Quantity | Value |
|---|---|
| Teeth | {teeth} |
| Module | {mod} mm |
| Pitch diameter | {pd} mm |
| Tooth form | involute, pressure angle {pa} degrees |
| Tip radius (measured on the supplied mesh) | {tip} mm |
| Root radius (measured on the supplied mesh) | {root} mm |
| Tooth thickness on the pitch circle (arc, measured on the supplied mesh) | {th} mm |
| Tooth phase | one tooth centred on the +x direction ({ph} degrees from +x, measured) |
| Wheel | z {wz0} mm to z {wz1} mm |
| Arbor | radius {ar} mm, z {az0} mm to z {az1} mm |
| Volume (measured on the supplied mesh) | {vol} mm3 |

## 3. Motion

Seen from the dial side (+z). The barrel turns at a steady speed; there is no escapement.

| Version | Sense | Speed |
|---|---|---|
| 8-hour barrel (for `movement.json`) | clockwise | 1 turn every {b8} |
| 6-hour barrel (for `variant_6h.json`) | clockwise | 1 turn every {b6} |

The two versions are the same part, in the same place, with the same teeth; only the speed differs.
""".format(teeth=W.BARREL_TEETH, mod=num(W.BARREL_MODULE), pd=num(pitch_d), pa=num(W.PRESSURE_ANGLE),
           tip=num(B["tip_r"]), root=num(B["root_r"]), th=num(B["thickness"]), ph=num(B["phase"]),
           wz0=num(W.BARREL_WHEEL_Z[0]), wz1=num(W.BARREL_WHEEL_Z[1]), ar=num(W.BARREL_ARBOR_R),
           az0=num(W.BARREL_ARBOR_Z[0]), az1=num(W.BARREL_ARBOR_Z[1]), vol=num(B["volume"]),
           b8=hours(W.BARREL_TURNS_PER_HOUR), b6=hours(W.CHANGED_BARREL_TURNS_PER_HOUR))


def ds_w02(L):
    return head("DS-W02", "Case", "the case supplied for this calibre") + """
## 1. Inner space

The case's inner space is a cylinder whose axis is parallel to z. The movement files state where that axis lies
(`case_centre`, x and y in mm).

| Quantity | Value |
|---|---|
| Inner radius | {cr} mm (inner diameter {cd} mm) |
| Inner height, along z | {ch} mm |

Units: millimetres.
""".format(cr=num(W.CASE_RADIUS), cd=num(2 * W.CASE_RADIUS), ch=num(W.CASE_HEIGHT))


def ds_w03(L):
    return head("DS-W03", "Manufacturing process", "the process that makes the parts of this calibre") + """
## 1. Smallest feature

| Quantity | Value |
|---|---|
| Smallest printable feature | {mf} mm |

## 2. What the smallest feature means for a part

{printable}

Units: millimetres.
""".format(mf=num(W.MIN_FEATURE), printable=wrap(printable_text(L)))


DATASHEETS = [("DS-W01_barrel.md", "DS-W01", "Supplied mainspring barrel"), ("DS-W02_case.md", "DS-W02", "Case"),
              ("DS-W03_process.md", "DS-W03", "Manufacturing process")]


def index_sheet(extra=()):
    rows = "".join("| %s | %s | `%s` |\n" % (d, t, f) for f, d, t in list(DATASHEETS) + list(extra))
    return "# Datasheets\n\n| Document | Title | File |\n|---|---|---|\n" + rows


def documents():
    """{relative path under environment/public/job: text}"""
    L = _literals()
    B = barrel_facts()
    gen = {"DS-W01_barrel.md": ds_w01(L, B), "DS-W02_case.md": ds_w02(L), "DS-W03_process.md": ds_w03(L)}
    out = {"PROMPT.md": prompt(L), "FORMAT.md": format_sheet(L), "datasheets/INDEX.md": index_sheet()}
    for f, _, _ in DATASHEETS:
        out["datasheets/" + f] = gen[f]
    return out


def check(out_dir=OUT):
    """Names of the committed files that differ from what the constants give (empty: up to date)."""
    bad = []
    for rel, text in documents().items():
        p = os.path.join(out_dir, rel)
        if not os.path.isfile(p) or open(p, encoding="utf-8").read() != text:
            bad.append(rel)
    return bad


def main(argv):
    if "--check" in argv:
        bad = check()
        if bad:
            print("out of date (run python3 environment/make_brief_job.py): " + ", ".join(bad))
            return 1
        print("up to date")
        return 0
    for rel, text in documents().items():
        p = os.path.join(OUT, rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote", os.path.relpath(p, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
