# Watch movement: going train and hands, a 6-hour variant and an assembly plan

You are a movement designer at a watch manufacturer. The calibre is a demonstration-scale model, about 1.617
times the size of an 11 1/2-ligne movement, to be made by 3D printing or a similar process; that process is why
its smallest feature is 0.2 mm.

## The goal

The wearer reads the time from four hands: hours and minutes on a common centre, seconds, and a 24-hour hand that
shows the hour of the day. The movement takes its power from the barrel below, fits the case below, and its parts
can be printed by the process below. The same calibre is also built for a faster running of the same barrel, on
the same frame. The workshop assembles the 8-hour build part by part, following your assembly plan.

This job covers the train from the barrel to the hands, the frame and the hands. The movement has no escapement
and no winding or setting works: the barrel is the driver and turns at the steady speed given in the order.

## Order

| Item | Specification |
|---|---|
| Barrel | part no. BR-096-20, catalogue sheet DS-W01; supplied as `/app/supplied/barrel.stl` |
| Case | part no. CS-414-134, catalogue sheet DS-W02 |
| Parts | printed by the process of sheet DS-W03 |
| 8-hour build (`movement.json`) | barrel BR-096-20 turning clockwise, seen from the dial side, once every 8 h |
| 6-hour variant (`variant_6h.json`) | the same barrel BR-096-20, in the same place, turning clockwise, seen from the dial side, once every 6 h |

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
- `/app/supplied/barrel.stl`: barrel BR-096-20 as a mesh, in its assembled position (DS-W01, section 3). It is not
  part of the delivery.

## Acceptance test

The delivery is inspected after you hand it in. What is in `/app/delivery/` when you finish is what is inspected.

The inspection has four parts. Each part is judged on its own, even when another part fails. The delivery as a
whole is accepted only when every condition and every check of all four parts passes: the movement must all work.

Terms used below:

- **Frame and units.** Millimetres (mm), cubic millimetres (mm3) and degrees. A right-handed frame. Every arbor
  (rotation axis) is parallel to z. The dial side is +z: the hands are read looking from +z towards -z, and
  "clockwise" always means clockwise in that view.
- **Solids.** Every test measures the solids built from the part files as `/app/FORMAT.md` describes; the barrel
  is the solid of `/app/supplied/barrel.stl`. "Intersect by at most 0.01 mm3" means that the volume of the
  intersection of the two solids is at most 0.01 mm3.
- **The frame** is the fixed parts of a movement, taken together.
- **A mobile** is a set of parts that turn together as one rigid body about the vertical line through its axis.
  The barrel is the mobile `barrel`, with its axis on x = 0 mm, y = 0 mm.
- **Speeds** are worked out from the tooth counts declared under `meshes`, as exact fractions, starting from the
  barrel at the speed the order gives for the build being judged. Every declared mesh is external: its two
  mobiles turn in opposite directions.

### Part 1: going train and hands (`movement.json`)

The 8-hour build: the barrel turns clockwise once every 8 h.

Conditions. If one fails, Part 1 fails and none of its checks passes.

- **C1 Files.** `movement.json` and every part file it names are valid as `/app/FORMAT.md` describes.
- **C2 Assembled.** In the drawn positions: taking the frame as one solid and each mobile (the barrel included)
  as one solid, no two of these solids intersect by more than 0.01 mm3; no two fixed parts intersect each
  other by more than 0.01 mm3; no two parts of one mobile intersect each other by more than 0.01 mm3. The fixed
  parts form one frame: two fixed parts are joined when their smallest distance is at most 0.01 mm, and every
  fixed part is joined to every other through a chain of joined fixed parts.

Checks. Each passes or fails.

1. **Free to turn.** Each mobile, the barrel included, turned through one full turn about its axis in 72 steps of
   5 degrees, never intersects the frame by more than 0.01 mm3.
2. **Held.** Each mobile, the barrel included, is moved 0.3 mm along +x, -x, +y, -y, +z and -z in turn, and is
   held in every one of the six directions. Moved in a direction, a mobile is held when it intersects the frame by
   more than 0.01 mm3, or intersects by more than 0.01 mm3 a mobile whose axis is within 0.01 mm of its own
   and which is itself held in that direction; this is worked out until nothing changes. A mobile whose axis is
   further than 0.01 mm from its own never holds it.
3. **Seated.** Every part of a mobile that has more than one part, moved 0.3 mm along +x, -x, +y and -y in turn,
   intersects the other parts of its mobile by more than 0.01 mm3 every time, and moved 0.3 mm along +z or along -z
   (at least one of the two) intersects them by more than 0.01 mm3. The parts of each such mobile form one piece:
   every part is linked to every other by a chain of parts of that mobile, each within 0.02 mm of the next.
   The barrel and mobiles of one part are not tested.
4. **The train runs.** At least one mesh is declared; no mobile is given two different speeds by the declared
   meshes; every declared mesh passes the mesh test below; and every mobile is driven from the barrel through
   declared meshes that pass the mesh test.

   *Mesh test.* For a declared mesh with driver D (z_D teeth) and driven mobile N (z_N teeth), starting from the
   drawn positions, at step i (i = 0, 1, ..., 8 x max(z_D, z_N) - 1) D is turned counter-clockwise by
   i x 360 / (8 x z_D) degrees about its axis, and N clockwise by that angle x z_D / z_N about its own axis.
   Three conditions must hold:
   - no jam: at every step, and at two more positions after every 8th step (i + 1/3 and i + 1/5 in the formula
     above, for i = 0, 8, 16, ...), D and N intersect by at most 0.01 mm3;
   - engaged: at every 4th step (i = 0, 4, 8, ...) at which their intersection is empty, their smallest
     distance is at most 0.1 mm;
   - the teeth drive: at every 8th step (i = 0, 8, 16, ...), D is turned a further 0.25 of its tooth pitch
     (90 / z_D degrees, counter-clockwise) while N stays where it is. V is the volume of the region that the
     turned D shares with N and that D did not occupy before this extra turn; H is the height in z of that region;
     m = 2 x (distance between the two drawn axes) / (z_D + z_N) is the mesh's module. V is at least 0.001 mm3 and
     V / H is more than 0.5 x m x m, at every one of these steps. (V / H is the area that the extra turn cuts into
     N's teeth.)
5. **The train runs with its arbors slightly out of place.** Every declared mesh also passes the mesh test with
   the driven mobile N moved 0.03 mm straight away from D's axis, and with N moved 0.03 mm straight towards
   D's axis (N then turns about its moved axis; if the two axes coincide, "away" is +x and "towards" is -x). The
   steps, the turning angles and m are those of the drawn position. This check does not change which meshes
   drive the hands; that is decided in the drawn position only.
6. **Nothing else collides.** Every pair of mobiles (the barrel included) that is not declared as a mesh is turned
   together, each at its speed from the declared tooth counts (a mobile that no declared mesh reaches from the
   barrel stands still): 144 equal steps covering one full turn of the faster of the two, then, if their speeds
   differ, 144 equal steps covering one full turn of one relative to the other. At every step they intersect by
   at most 0.01 mm3.
7. **Hour hand.** 8. **Minute hand.** 9. **Seconds hand.** The hands show the time: each of the three moves as
   that hand of a watch does. A hand is driven only through declared meshes that pass the mesh test (a declared
   mesh that fails it drives nothing), and no mobile may be given two different speeds by the declared meshes.
10. **Hours and minutes on a common centre.** The axes of the hour hand's mobile and the minute hand's mobile are
    at most 0.01 mm apart.
11. **Hands.** Each of the hour, minute and seconds hand parts reaches at least 5 mm from its mobile's axis;
    lies wholly above the frame (its lowest point is no lower than the highest point of any fixed part); and
    points: its centre of volume is at least 0.5 mm from its mobile's axis.
12. **Fits the case.** Everything stays within 20.7 mm (the inner radius of case CS-414-134, DS-W02) of the
    vertical line through `case_centre` as it turns: every point of every fixed part, and, for each mobile, its
    largest distance from its own axis plus the distance from its axis to `case_centre`. The whole movement, the
    barrel included, is at most 13.4 mm tall in z (the inner height of case CS-414-134).
13. **Printable.** Each part you make (not the barrel) is printable by the test of the manufacturing process
    (sheet DS-W03, section 3), which is:

    The part is divided into cubic voxels of side 0.05 mm whose centres lie at 0.05 x k + 0.0113 mm along x, y and z
    (k any integer); a voxel is solid when its centre is inside the part. A solid voxel survives when its centre
    is at least 0.075 mm (1.5 voxels) from the centre of the nearest voxel that is not solid. The printable body
    is every solid voxel whose centre is within 0.05 mm (1 voxel) of the centre of a surviving voxel. The part is
    printable when at least one voxel survives and no solid voxel's centre is further than 0.2 mm from the centre
    of the nearest voxel of the printable body.

### Part 2: 24-hour hand (`movement.json`)

The 8-hour build: the barrel turns clockwise once every 8 h.

Conditions: C1 and C2 of Part 1, and **C3 24-hour hand declared**: `hands.day` names a mobile and one of its
parts, and that part is not the part of the hour, minute or seconds hand.

Checks:

1. **24-hour hand.** It shows the hour of the day as a 24-hour hand does. It is driven only through declared
   meshes that pass the mesh test of Part 1, and no mobile may be given two different speeds by the declared
   meshes.
2. **24-hour hand placement.** Its mobile's axis is at least 6 mm from the axis of the hour hand's mobile;
   the hand part reaches at least 3 mm from its mobile's axis; it lies wholly above the frame; and its
   centre of volume is at least 0.5 mm from its mobile's axis.

### Part 3: the 6-hour variant (`variant_6h.json`)

The 6-hour variant: the same barrel, in the same place, turns clockwise once every 6 h.

Conditions: C1, C2 and C3 for `variant_6h.json`, and **C4 Same frame**: its `fixed` list is the same as that of
`movement.json` (the same names in the same order, so the same part files), and its `case_centre` is the same
two numbers.

Checks: every check of Part 1 and of Part 2, applied to `variant_6h.json` with the barrel turning once every 6 h.

### Part 4: assembly (`assembly.json`, for `movement.json`)

Conditions: C1 of Part 1 for `movement.json`, and `assembly.json` is valid JSON with a list `order` and an object
`paths` (`/app/FORMAT.md`).

The parts of `movement.json` and the barrel are put in one at a time, in the order of `order`. A name in `order`
that is not one of these parts is ignored; a name that appears more than once counts at its first place only. A
part that is not in `order` is not installed and stands in its assembled position from the start, so every part
in `order` is tested against it. Each part moves along its path. A part is installed when its path obeys all of
these rules:

1. The path is a list of 4x4 matrices. Every matrix is finite and is a proper rotation plus a translation
   (R^T R = I and det R = +1, within 1e-6); its last row is 0 0 0 1 within 1e-6; the last pose is the identity
   within 1e-6.
2. In the first pose, the part's bounding box lies wholly outside the bounding box of the complete movement (all
   its parts and the barrel, assembled) grown by 5 mm on every side.
3. Between consecutive poses, no vertex of the part moves more than 0.2 mm.
4. The path has at least 2 and at most 1,500 poses.
5. In every pose, the part intersects each part placed before it by at most 0.01 mm3, parts of its own mobile
   included.

A part that breaks a rule is not installed, but it still stands in its assembled position for the parts that
follow. Part 4 is judged by the share of the parts (the barrel included) that are installed; it passes in full
when every part is installed.

## How you work

You work alone and unattended; nobody answers questions during the job. The job ends when you stop.

Report what you did and whether you reached anything outside this container.
