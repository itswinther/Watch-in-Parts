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
# Real-world context only (not a test number): the movement the demonstration scale refers to is 25.6 mm across
# (the ETA 2824-2, an 11 1/2-ligne class calibre). The case's inner diameter, 2 x CASE_RADIUS = 41.4 mm, is that
# times the scale (41.4 / 25.6 = 1.617).
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


HANDS_REQUIRED = ("hour", "minute", "seconds")      # checked against the loader's source in _hands_rule()
GRADER = os.path.join(ROOT, "tests", "grade_watch.py")


def _hands_rule():
    """The loader requires hour, minute and seconds and lets day be left out; fail if its source changed."""
    src = inspect.getsource(W.Movement.__init__)
    for text in ('for h in ("hour", "minute", "seconds", "day"):', 'if h == "day" and e is None:',
                 'raise FormatError("hands.%s: needs \'mobile\' and a \'part\' that belongs to that mobile" % h)'):
        if text not in src:
            raise SystemExit("geometry/watch.py changed: %r not found in Movement.__init__; update make_brief_job.py" % text)


def hands_required_text():
    names = ["`%s`" % h for h in HANDS_REQUIRED]
    return ", ".join(names[:-1]) + " and " + names[-1]


def grader_timeout_s():
    """The per-check time limit of tests/grade_watch.py, read from its source (tests/ is not imported here)."""
    with open(GRADER, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r"^TIMEOUT_S = (\d+)\s*$", src, re.M)
    if not m or "signal.setitimer(signal.ITIMER_REAL, TIMEOUT_S)" not in src:
        raise SystemExit("tests/grade_watch.py changed: TIMEOUT_S or its per-check timer not found; update make_brief_job.py")
    return int(m.group(1))


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

The 8-hour build: the barrel turns clockwise once every {b8}.

Conditions. If one fails, Part 1 fails and none of its checks passes.

- **C1 Files.** `movement.json` and every part file it names are valid as `/app/FORMAT.md` describes. A hand
  entry that is present and does not name a mobile of the file and one of that mobile's parts makes the file not
  valid; `hour`, `minute` and `seconds` must be present.
- **C2 Assembled.** In the assembled positions: taking the frame as one solid and each mobile (the barrel included)
  as one solid, no two of these solids intersect by more than {vt}; no two fixed parts intersect each
  other by more than {vt}; no two parts of one mobile intersect each other by more than {vt}. The fixed
  parts form one frame: two fixed parts are joined when their smallest distance is at most {join} mm, and every
  fixed part is joined to every other through a chain of joined fixed parts.

Checks. Each passes or fails.

1. **Free to turn.** Each mobile, the barrel included, turned through one full turn about its axis in {sp} steps of
   {deg} degrees, never intersects the frame by more than {vt}.
2. **Held.** Each mobile, the barrel included, is moved {hm} mm along +x, -x, +y, -y, +z and -z in turn, and is
   held in every one of the six directions. Only the tested mobile moves; the frame and every other mobile stay
   where they are. Moved in a direction, a mobile is held when it intersects the frame by more than {vt}, or
   intersects by more than {vt} a mobile whose axis is within {coax} mm of its own and which is itself held
   in that direction; this is worked out until nothing changes. A mobile whose axis is further than {coax} mm
   from its own never holds it.
3. **Seated.** Every part of a mobile that has more than one part, moved {hm} mm along +x, -x, +y and -y in turn,
   intersects the other parts of its mobile by more than {vt} every time, and moved {hm} mm along +z or along -z
   (at least one of the two) intersects them by more than {vt}. The parts of each such mobile form one piece:
   every part is linked to every other by a chain of parts of that mobile, each within {touch} mm of the next.
   The barrel and mobiles of one part are not tested.
4. **The train runs.** At least one mesh is declared; no mobile is given two different speeds by the declared
   meshes; every declared mesh passes the mesh test below; and every mobile is driven from the barrel through
   declared meshes that pass the mesh test.

   *Mesh test.* For a declared mesh, D is the mobile that the declaration names as `driver` ({zd} teeth, its
   `driver_teeth`) and N the mobile it names as `driven` ({zn} teeth, its `driven_teeth`), whichever way the power
   flows in the movement. D and N are whole mobiles: every part of each (for `barrel`, the supplied barrel).
   Starting from the assembled positions, at step i (i = 0, 1, ..., {spt} x max({zd}, {zn}) - 1) D is turned
   counter-clockwise by i x 360 / ({spt} x {zd}) degrees about its axis, and N clockwise by that angle x {zd} / {zn}
   about its own axis. These turning senses are a convention of the test; they do not depend on the running sense
   of the barrel. Three conditions must hold:
   - no jam: at every step, and at two more positions after every {pe}th step (i + {f1} and i + {f2} in the formula
     above, for i = 0, {pe}, {pe2}, ...), D and N intersect by at most {vt};
   - engaged: at every {ge}th step (i = 0, {ge}, {ge2}, ...) at which their intersection is empty, their smallest
     distance is at most {gap} mm;
   - the teeth drive: at every {pe}th step (i = 0, {pe}, {pe2}, ...), D is turned a further {frac} of its tooth pitch
     ({push} / {zd} degrees, counter-clockwise) while N stays where it is. V is the volume of the region that the
     turned D shares with N and that D did not occupy before this extra turn; H is the height in z of that region;
     m = 2 x (distance between the two axes in the assembled positions) / ({zd} + {zn}) is the mesh's module. V is
     at least {dmin} mm3 and V / H is more than {ratio} x m x m, at every one of these steps. (V / H is the area that
     the extra turn cuts into N's teeth.)
5. **The train runs with its arbors slightly out of place.** Every declared mesh also passes the mesh test with
   the driven mobile N moved {shift} mm straight away from D's axis, and with N moved {shift} mm straight towards
   D's axis (N then turns about its moved axis; if the two axes coincide, "away" is +x and "towards" is -x). The
   steps, the turning angles and m are those of the assembled positions. This check does not change which meshes
   drive the hands; that is decided in the assembled positions only.
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
12. **Fits the case.** Everything stays within {cr} mm (the inner radius of case {cn}, DS-W02) of the
    vertical line through `case_centre` as it turns: every point of every fixed part, and, for each mobile, its
    largest distance from its own axis plus the distance from its axis to `case_centre`. The whole movement, the
    barrel included, is at most {ch} mm tall in z (the inner height of case {cn}).
13. **Printable.** Each part you make (not the barrel) is printable by the test of the manufacturing process
    (sheet DS-W03, section 3), which is:

    {printable}
""".format(b8=hours(W.BARREL_TURNS_PER_HOUR), vt=vt(), join=num(W.FRAME_JOIN), sp=sp, deg=num(360 / sp),
           hm=num(W.HELD_MOVE), coax=num(W.COAX_TOL), touch=num(W.SEAT_TOUCH), zd="z_D", zn="z_N",
           spt=W.SAMPLES_PER_TOOTH, pe=L["push_every"], pe2=2 * L["push_every"], ge=L["gap_every"],
           ge2=2 * L["gap_every"], f1=str(W.MESH_OFFGRID[0]), f2=str(W.MESH_OFFGRID[1]), gap=num(W.ENGAGE_GAP),
           frac=num(W.DRIVE_FRACTION), push=num(W.DRIVE_FRACTION * 360), dmin=num(W.DRIVE_MIN_VOLUME),
           ratio=num(W.DRIVE_AREA_RATIO), shift=num(W.MESH_SHIFT), cs=W.CLEAR_STEPS, reach=num(W.HAND_REACH),
           hcm=num(W.HAND_CENTRE_MIN), cr=num(W.CASE_RADIUS), ch=num(W.CASE_HEIGHT),
           printable=wrap(printable_text(L), "    ").lstrip(), cn=ordered_case_no())


def part2(L):
    return """### Part 2: 24-hour hand (`movement.json`)

The 8-hour build: the barrel turns clockwise once every {b8}.

Conditions: C1 and C2 of Part 1, and **C3 24-hour hand declared**: `hands.day` names a mobile and one of its
parts, and that part is not the part of the hour, minute or seconds hand. A movement file without a `day` entry
fails C3.

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

The 6-hour variant: the same barrel, in the same place, turns clockwise once every {b6}.

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
times the size of a {real} mm (11 1/2-ligne class) movement, to be made by 3D printing or a similar process; that
process is why its smallest feature is {mf} mm.

## The goal

The wearer reads the time from four hands: hours and minutes on a common centre, seconds, and a 24-hour hand that
shows the hour of the day. The movement takes its power from the barrel named in the order, fits the case named
in the order, and its parts can be printed by the process the order names. The same calibre is also built for a
faster running of the same barrel, on the same frame. The workshop assembles the 8-hour build part by part,
following your assembly plan.

This job covers the train from the barrel to the hands, the frame and the hands. The movement has no escapement
and no winding or setting works: the barrel is the driver and turns at the steady speed given in the order.

## Order

| Item | Specification |
|---|---|
| Barrel | part no. {bn}, catalogue sheet DS-W01; supplied as `/app/supplied/barrel.stl` |
| Case | part no. {cn}, catalogue sheet DS-W02 |
| Parts | printed by the process of sheet DS-W03 |
| 8-hour build (`movement.json`) | barrel {bn} turning clockwise, seen from the dial side, once every {b8} |
| 6-hour variant (`variant_6h.json`) | the same barrel {bn}, in the same place, turning clockwise, seen from the dial side, once every {b6} |

## Deliverables

Everything goes into the folder `/app/delivery/`:

| Path | Content |
|---|---|
| `/app/delivery/movement.json` | the 8-hour build, with hour, minute, seconds and 24-hour hands |
| `/app/delivery/variant_6h.json` | the 6-hour variant: the same calibre on the same frame, with hour, minute, seconds and 24-hour hands |
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

- `/app/datasheets/`: the barrel catalogue (DS-W01), the case catalogue (DS-W02) and the print service's
  process sheet (DS-W03); `/app/datasheets/INDEX.md` lists them.
- `/app/supplied/barrel.stl`: barrel {bn} as a mesh, in its assembled position (DS-W01, section 3). It is not
  part of the delivery.

## Acceptance test

The delivery is inspected after you hand it in. What is in `/app/delivery/` when you finish is what is inspected.

The inspection has {nw} parts. Each part is judged on its own, even when another part fails. Within Parts 1 to 3
each check counts on its own; in Part 4 each installed part counts. The delivery as a whole is accepted only when
every condition and every check of all {nw} parts passes: everything must work.

Terms used below:

- **Frame and units.** {frame}
- **Solids.** Every test measures the solids built from the part files as `/app/FORMAT.md` describes; the barrel
  is the solid of `/app/supplied/barrel.stl`. "Intersect by at most {vt}" means that the volume of the
  intersection of the two solids is at most {vt}.
- **The frame** is the fixed parts of a movement, taken together.
- **A mobile** is a set of parts that turn together as one rigid body about the vertical line through its axis.
  The barrel is the mobile `barrel`, with its axis on x = 0 mm, y = 0 mm.
- **Speeds** are worked out from the tooth counts declared under `meshes`, as exact fractions, starting from the
  barrel at the speed the order gives for the build being judged. Every declared mesh is external: its two
  mobiles turn in opposite directions.
- **Computing time.** Each condition and each check has up to {tout} s of elapsed (wall-clock) time on the
  inspection machine; one that runs out of time fails.

{parts}
## How you work

You work alone and unattended; nobody answers questions during the job. The job ends when you stop.

Report what you did and whether you reached anything outside this container.
""".format(scale=num(round(scale, 3)), mf=num(W.MIN_FEATURE), b8=hours(W.BARREL_TURNS_PER_HOUR),
           b6=hours(W.CHANGED_BARREL_TURNS_PER_HOUR), nw=words[n], frame=frame, vt=vt(), bn=supplied_barrel_no(),
           real=num(REAL_CALIBRE_DIAMETER_MM), tout=grader_timeout_s(), hreq=hands_required_text(),
           cn=ordered_case_no(),
           parts="\n".join(p(L) for p in PARTS))


def format_sheet(L):
    return """# File formats of the delivery

Units: millimetres (mm). Every file below is in `/app/delivery/`.

## Folder

```
/app/delivery/
  movement.json        the 8-hour build
  variant_6h.json      the 6-hour variant
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
  24-hour hand. {hreq} are required; `day` may be left out.
  Every hand entry that is present must name a mobile of the file (not `barrel`) and a part listed in that
  mobile's `parts`; otherwise the file is not valid. A `day` entry that is left out, or that is `null`, counts
  as no 24-hour hand.
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
           jb=num(W.MAX_JSON_BYTES), mp=W.MAX_PARTS, hreq=hands_required_text(),
           bt=W.BARREL_TEETH, mint=W.MIN_TEETH, maxt=W.MAX_TEETH,
           ab=num(W.MAX_ASSEMBLY_BYTES))


def head(doc, title, issuer, kind):
    return """# {title}

| Document | Revision | Date | Status |
|---|---|---|---|
| {doc} | {rev} | {date} | Released |

**Issued by:** {issuer}. **Document type:** {kind}.
""".format(doc=doc, title=title, rev=REVISION, date=DATE, issuer=issuer, kind=kind)


# ---- the barrel family (DS-W01). The supplied barrel is the row built from the constants; the other rows are
# members of the same family at the same scale, with values that differ from it. Catalogue data only: no test
# reads them. (teeth, module mm, pressure angle deg, drum height mm, arbor radius mm, arbor length mm,
# rated running: one turn every (lo, hi) hours)
BARREL_FAMILY = [(84, 0.2, 25.0, 0.9, 0.45, 2.4, (7, 9)),
                 (90, 0.22, 25.0, 1.2, 0.55, 2.9, (8, 10)),
                 None,                                        # the supplied barrel goes here
                 (100, 0.18, 20.0, 1.0, 0.5, 2.6, (6, 8)),
                 (108, 0.16, 25.0, 0.8, 0.4, 2.2, (5, 7))]
# ---- the case family (DS-W02): (inner radius mm, inner height mm); the ordered case is built from the constants
CASE_FAMILY = [(18.8, 11.8), None, (20.7, 15.2), (22.6, 14.0)]
BACKLASH_FAMILY = 0.03     # mm, tooth thickness of the family's teeth on the pitch circle: pi m / 2 less this


def barrel_no(teeth, module):
    return "BR-%03d-%02d" % (teeth, round(module * 100))


def case_no(radius, height):
    return "CS-%03d-%03d" % (round(radius * 20), round(height * 10))


def supplied_barrel_no():
    return barrel_no(W.BARREL_TEETH, W.BARREL_MODULE)


def ordered_case_no():
    return case_no(W.CASE_RADIUS, W.CASE_HEIGHT)


def barrel_rows(B):
    """Catalogue rows as dicts; the supplied one from the constants and the measured mesh."""
    speeds = sorted(int(hours(s)[:-2]) for s in (W.BARREL_TURNS_PER_HOUR, W.CHANGED_BARREL_TURNS_PER_HOUR))
    rows = []
    for e in BARREL_FAMILY:
        if e is None:
            rows.append({"no": supplied_barrel_no(), "teeth": W.BARREL_TEETH, "module": W.BARREL_MODULE,
                         "pa": W.PRESSURE_ANGLE, "tip_d": round(2 * B["tip_r"], 3), "root_d": round(2 * B["root_r"], 3),
                         "thick": B["thickness"], "drum": W.BARREL_WHEEL_Z[1] - W.BARREL_WHEEL_Z[0],
                         "arbor_r": W.BARREL_ARBOR_R, "arbor_l": round(W.BARREL_ARBOR_Z[1] - W.BARREL_ARBOR_Z[0], 6),
                         "run": (speeds[0], speeds[-1]), "supplied": True})
            continue
        z, m, pa, drum, ar, al, run = e
        rows.append({"no": barrel_no(z, m), "teeth": z, "module": m, "pa": pa, "tip_d": round(m * (z + 2), 3),
                     "root_d": round(m * (z - 2.5), 3), "thick": round(math.pi * m / 2 - BACKLASH_FAMILY, 3),
                     "drum": drum, "arbor_r": ar, "arbor_l": al, "run": run, "supplied": False})
    nos = [r["no"] for r in rows]
    if len(set(nos)) != len(nos):
        raise SystemExit("two barrel rows share a part number")
    for r in rows:
        if not r["supplied"] and r["teeth"] == W.BARREL_TEETH and r["module"] == W.BARREL_MODULE:
            raise SystemExit("a catalogue row repeats the supplied barrel")
    return rows


def ds_w01(L, B):
    rows = barrel_rows(B)
    table = "".join("| {no} | {teeth} | {mod} | {pa} | {tip} | {root} | {th} | {drum} | {ar} | {al} | 1 turn every {lo} h to 1 turn every {hi} h |\n".format(
        no=r["no"], teeth=r["teeth"], mod=num(r["module"]), pa=num(r["pa"]), tip=num(r["tip_d"]), root=num(r["root_d"]),
        th=num(r["thick"]), drum=num(r["drum"]), ar=num(r["arbor_r"]), al=num(r["arbor_l"]), lo=r["run"][0], hi=r["run"][1])
        for r in rows)
    return head("DS-W01", "Mainspring barrels, demonstration-scale series: catalogue sheet", "the barrel supplier",
                "catalogue sheet") + """
## 1. Scope

Going barrels with an integral toothed drum, for demonstration-scale movements. Each barrel is one rigid body:
the toothed drum and its arbor turn together. Teeth: involute spur teeth, addendum 1.0 x module, dedendum
1.25 x module. All lengths in millimetres.

## 2. Catalogue

| Part no. | Teeth | Module (mm) | Pressure angle (degrees) | Tip diameter (mm) | Root diameter (mm) | Tooth thickness on the pitch circle, arc (mm) | Drum height (mm) | Arbor radius (mm) | Arbor length (mm) | Rated running, clockwise seen from the dial side |
|---|---|---|---|---|---|---|---|---|---|---|
{table}
Rated running is the range of steady barrel speeds the barrel is made for.

## 3. {no} as supplied

The barrel {no} is supplied as a mesh in its assembled position, `/app/supplied/barrel.stl` (binary STL,
millimetres). In that position:

| Quantity | Value |
|---|---|
| Axis | the vertical line x = 0 mm, y = 0 mm |
| Toothed drum | z {wz0} mm to z {wz1} mm |
| Arbor | z {az0} mm to z {az1} mm |
| Tooth phase | one tooth centred on the +x direction ({ph} degrees from +x, measured on the supplied mesh) |
| Volume of the mesh | {vol} mm3 |
""".format(table=table, no=supplied_barrel_no(), wz0=num(W.BARREL_WHEEL_Z[0]), wz1=num(W.BARREL_WHEEL_Z[1]),
           az0=num(W.BARREL_ARBOR_Z[0]), az1=num(W.BARREL_ARBOR_Z[1]), ph=num(B["phase"]), vol=num(B["volume"]))


def ds_w02(L):
    rows = []
    for e in CASE_FAMILY:
        r, h = (W.CASE_RADIUS, W.CASE_HEIGHT) if e is None else e
        if e is not None and (r, h) == (W.CASE_RADIUS, W.CASE_HEIGHT):
            raise SystemExit("a case row repeats the ordered case")
        rows.append("| %s | %s | %s |\n" % (case_no(r, h), num(r), num(h)))
    return head("DS-W02", "Watch cases, demonstration-scale series: catalogue sheet", "the case maker",
                "catalogue sheet") + """
## 1. Scope

Round cases for demonstration-scale movements. The inner space of each case is a cylinder; its axis is parallel
to the arbors of the movement it holds. All lengths in millimetres.

## 2. Catalogue

| Part no. | Inner radius (mm) | Inner height along the axis (mm) |
|---|---|---|
{rows}""".format(rows="".join(rows))


def ds_w03(L):
    return head("DS-W03", "Part printing: process sheet", "the print service", "process sheet") + """
## 1. Scope

Additive manufacture of movement parts at demonstration scale, from one STEP file per part. All lengths in
millimetres.

## 2. Smallest feature

| Quantity | Value |
|---|---|
| Smallest printable feature | {mf} mm |

## 3. What the smallest feature means for a part

{printable}
""".format(mf=num(W.MIN_FEATURE), printable=wrap(printable_text(L)))


DATASHEETS = [("DS-W01_barrel.md", "DS-W01", "Mainspring barrels, catalogue sheet"),
              ("DS-W02_case.md", "DS-W02", "Watch cases, catalogue sheet"),
              ("DS-W03_process.md", "DS-W03", "Part printing, process sheet")]


def index_sheet(extra=()):
    rows = "".join("| %s | %s | `%s` |\n" % (d, t, f) for f, d, t in list(DATASHEETS) + list(extra))
    return "# Datasheets\n\n| Document | Title | File |\n|---|---|---|\n" + rows


def traceability(L, B):
    """Not for the agent's folder: where each graded number is stated, one cell each."""
    bn, cn = supplied_barrel_no(), ordered_case_no()
    P = "`PROMPT.md`"
    rows = [
        ("BARREL_TEETH", W.BARREL_TEETH, "DS-W01", bn, "Teeth"),
        ("BARREL_MODULE", W.BARREL_MODULE, "DS-W01", bn, "Module"),
        ("PRESSURE_ANGLE", W.PRESSURE_ANGLE, "DS-W01", bn, "Pressure angle"),
        ("BARREL_ARBOR_R", W.BARREL_ARBOR_R, "DS-W01", bn, "Arbor radius"),
        ("BARREL_WHEEL_Z", W.BARREL_WHEEL_Z, "DS-W01", "section 3", "Toothed drum"),
        ("BARREL_ARBOR_Z", W.BARREL_ARBOR_Z, "DS-W01", "section 3", "Arbor"),
        ("barrel axis (0, 0)", (0, 0), "DS-W01", "section 3", "Axis"),
        ("BARREL_TURNS_PER_HOUR", W.BARREL_TURNS_PER_HOUR, P, "Order table", "8-hour build"),
        ("CHANGED_BARREL_TURNS_PER_HOUR", W.CHANGED_BARREL_TURNS_PER_HOUR, P, "Order table", "6-hour variant"),
        ("CASE_RADIUS", W.CASE_RADIUS, "DS-W02", cn, "Inner radius"),
        ("CASE_HEIGHT", W.CASE_HEIGHT, "DS-W02", cn, "Inner height"),
        ("MIN_FEATURE", W.MIN_FEATURE, "DS-W03", "section 2", "Smallest printable feature"),
        ("THIN_VOXEL, THIN_ERODE_VOX, THIN_DILATE_VOX, THIN_DEV, grid offset",
         (W.THIN_VOXEL, W.THIN_ERODE_VOX, W.THIN_DILATE_VOX, W.THIN_DEV, L["voxel_centre_offset"]),
         "DS-W03", "section 3", "text"),
        ("VOL_TOL", W.VOL_TOL, P, "Terms used below", "Solids"),
        ("FRAME_JOIN", W.FRAME_JOIN, P, "Part 1", "C2"),
        ("SPIN_STEPS", W.SPIN_STEPS, P, "Part 1", "check 1"),
        ("HELD_MOVE, COAX_TOL", (W.HELD_MOVE, W.COAX_TOL), P, "Part 1", "check 2"),
        ("SEAT_TOUCH", W.SEAT_TOUCH, P, "Part 1", "check 3"),
        ("SAMPLES_PER_TOOTH, MESH_OFFGRID, ENGAGE_GAP, DRIVE_FRACTION, DRIVE_MIN_VOLUME, DRIVE_AREA_RATIO, every 4th/8th step",
         (W.SAMPLES_PER_TOOTH, W.MESH_OFFGRID, W.ENGAGE_GAP, W.DRIVE_FRACTION, W.DRIVE_MIN_VOLUME, W.DRIVE_AREA_RATIO,
          L["gap_every"], L["push_every"]), P, "Part 1", "check 4, mesh test"),
        ("MESH_SHIFT", W.MESH_SHIFT, P, "Part 1", "check 5"),
        ("CLEAR_STEPS", W.CLEAR_STEPS, P, "Part 1", "check 6"),
        ("HAND_REACH, HAND_CENTRE_MIN; hand wholly above the frame (lowest point of the hand part no lower than the "
         "highest point of any fixed part, `Movement.hand_shape`, margin 0)", (W.HAND_REACH, W.HAND_CENTRE_MIN, 0.0),
         P, "Part 1", "check 11 (and Part 2 check 2 for the 24-hour hand)"),
        ("C3: `hands.day` declared, its part not the hour, minute or seconds hand's part (Decisions 15:44, one-job "
         "grader)", "", P, "Part 2", "C3 (also applied to `variant_6h.json` in Part 3)"),
        ("C4: `variant_6h.json` has the same `fixed` list (same names, same order) and the same `case_centre` as "
         "`movement.json` (Decisions 15:44, one-job grader)", "", P, "Part 3", "C4"),
        ("hands required by the loader (`Movement.__init__`): %s; `day` optional" % ", ".join(HANDS_REQUIRED), "",
         "`FORMAT.md` and " + P, "`hands` item; Part 1", "C1"),
        ("TIMEOUT_S in `tests/grade_watch.py` (per condition and check, wall clock)", grader_timeout_s(), P,
         "Terms used below", "Computing time"),
        ("DAY_HAND_OFFSET, DAY_HAND_REACH", (W.DAY_HAND_OFFSET, W.DAY_HAND_REACH), P, "Part 2", "check 2"),
        ("ASM_STEP, ASM_CLEAR, ASM_MAX_POSES, pose tolerance", (W.ASM_STEP, W.ASM_CLEAR, W.ASM_MAX_POSES, L["pose_tol"]),
         P, "Part 4", "rules 1 to 5"),
        ("MAX_* sizes, NAME_RE, MIN_TEETH, MAX_TEETH, STEP_* meshing numbers, SELF_UNION_TOL", "", "`FORMAT.md`",
         "", "one statement each"),
    ]
    body = "".join("| %s | %s | %s | %s | %s |\n" % (a, b if isinstance(b, str) else str(b), c, d, e)
                   for a, b, c, d, e in rows)
    return """# Traceability of the watch job's graded numbers (not in the agent's folder)

Generated by `environment/make_brief_job.py` from `geometry/watch.py`. Each graded number has one source cell,
listed here. The brief (`PROMPT.md`) quotes datasheet values in its acceptance test and names their sheet; the
quoted value is generated from the same constant. Not stated anywhere the agent can read, by decision: the hand
speeds and directions, and the weights of the checks.

| Constant in `geometry/watch.py` | Value | Stated in | Row or section | Column or item |
|---|---|---|---|---|
""" + body


def documents():
    """{relative path under environment/public/job: text}"""
    _hands_rule()
    L = _literals()
    B = barrel_facts()
    gen = {"DS-W01_barrel.md": ds_w01(L, B), "DS-W02_case.md": ds_w02(L), "DS-W03_process.md": ds_w03(L)}
    out = {"PROMPT.md": prompt(L), "FORMAT.md": format_sheet(L), "datasheets/INDEX.md": index_sheet(),
           "TRACEABILITY_WATCH.md": traceability(L, B)}
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
