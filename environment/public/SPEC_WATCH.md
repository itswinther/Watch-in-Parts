# Watch gear train: specification

## The job

Design the gear train of a mechanical wristwatch, as 3D-printable parts. The work
is done in four stages, each by a different engineer who starts from the result
of the stage before:

1. **Design** the movement (this document up to "Stage 2").
2. **Extend** it with a 24-hour hand, without touching the existing wheels.
3. **Change** it: the barrel now turns faster; rework the movement for that while
   keeping as many of the received part files as you can.
4. **Assemble** it: an order and a collision-free path for every part.

Your instruction file says which stage you are doing. Read the later stages too:
what you design in stage 1 has to survive them, and the size limit is the same
at every stage.

The mainspring barrel is supplied (`meshes/barrel.stl`). It turns **clockwise,
once every 8 hours** (at stage 3 it turns once every 6 hours; see "Stage 3").
Drive the watch's **hour, minute and seconds hands** from it. There is no
escapement and no winding or setting mechanism in this task: the barrel is simply
the driver, and the grader turns it at that steady speed.

You make every other part: wheels, pinions, arbors, plates, bridges and the three
hands.

## Frame and units

Millimetres. Right-handed frame. **Every arbor (rotation axis) is parallel to z.**
The dial side is +z: the hands are read looking from +z towards -z, and
"clockwise" always means clockwise in that view.

## The supplied barrel

`meshes/barrel.stl`, fixed where it is: axis on x = 0, y = 0.

- A spur gear of 96 teeth, module 0.2 (pitch diameter 19.2), z 0 to 1.0.
  Involute teeth, pressure angle 25 degrees, addendum 1.0 x module, dedendum
  1.25 x module, tooth thickness on the pitch circle reduced by 0.03 for
  backlash. One tooth is centred on the +x direction.
- An arbor of radius 0.5 from z -1.0 to z 1.6.

The barrel is a mobile named `barrel`. You must hold it like any other mobile.
The name `barrel` is reserved: none of your parts or mobiles may be called
`barrel` (a file that does so fails the Files requirement).

## What you submit

A folder `work/` containing `movement.json` and one STEP file per part,
`parts/<name>.step`, made with a CAD kernel (CadQuery 2.8.0 / OpenCASCADE is
installed). STL part files are not accepted. Keep the scripts that made your
parts in `scripts/`; they are copied with your submission and archived with it,
but nothing in them is run or graded. **A later stage does not receive your
scripts**: the next engineer gets only `movement.json` and the `parts/` STEP
files (in `work/` and again in `previous/`), and reworks the movement from
those files alone.

The supplied barrel is the one exception: it is given as a mesh,
`meshes/barrel.stl` (binary STL, millimetres, in its place). You do not submit
it. To use it in your own checks, load it as a `manifold3d` solid, for example
with `tools/kernel.py`: `kernel.tris_to_manifold(kernel.read_stl(path, 200000,
33554432))`.

Each part is in its assembled position. At most 60 parts. Part and mobile
names use letters, digits, `_` and `-`, 1 to 40 characters; `barrel` is taken
by the supplied barrel and may not name a part or another mobile. Tooth counts
in `meshes` are integers from 3 to 1000. `movement.json` may be at most
1,048,576 bytes and `assembly.json` at most 67,108,864 bytes. Every file the
grader opens (`movement.json`, `assembly.json`, each part file, and the `parts/`
folder) must be a real file or folder inside the submission folder: a symbolic
link, or a file outside the folder, is a format error. How a part file becomes the solid that every test
below uses:

- At most 16,777,216 bytes. The file's length unit must be millimetre; a file
  in any other unit (inch, metre, ...) is rejected, not converted. It must hold
  exactly one solid, valid by OpenCASCADE's shape check, and nothing outside
  that solid. A file whose solid has more than 500 flat faces with exactly three
  edges is rejected (the rule counts only such triangular faces). Reading and meshing one file may take
  at most 120 s and 4,096 MB of memory (it runs in its own process).
- The solid is meshed with OpenCASCADE (`BRepMesh_IncrementalMesh`) with a
  linear deflection of 0.001 mm (absolute) and an angular deflection of 0.1
  radians. A meshed curved surface lies within 0.001 mm of the true one (inside
  a convex surface, outside a concave one, such as a hole).
- The mesh may have at most 200,000 triangles; the triangles, with identical
  vertices joined, must form a single closed manifold shell with positive
  volume, and its volume may change by at most 0.5% when the solid is united
  with itself.

`movement.json`:

```
{
  "case_centre": [x, y],
  "fixed": ["main_plate", "bridge", ...],
  "mobiles": {
    "some_name": {"axis": [x, y], "parts": ["wheel_a", "arbor_a", ...]},
    ...
  },
  "meshes": [
    {"driver": "barrel", "driver_teeth": 96, "driven": "some_name", "driven_teeth": 12},
    ...
  ],
  "hands": {
    "hour":    {"mobile": "...", "part": "..."},
    "minute":  {"mobile": "...", "part": "..."},
    "seconds": {"mobile": "...", "part": "..."}
  }
}
```

- `fixed`: parts that do not move (plates, bridges, pillars, cocks). Fixed parts
  must not overlap one another.
- `mobiles`: each mobile is a set of parts that turn together as one rigid body
  about the vertical line through `axis`. Parts of one mobile may overlap each
  other. Do not list `barrel`; it already exists.
- `meshes`: every pair of gears that drive one another, with the tooth count of
  the gear on each mobile. All meshes are external (the two mobiles turn in
  opposite directions). Speeds are worked out from these tooth counts as exact
  fractions, starting from the barrel.
- `hands`: which mobile carries each hand, and which of that mobile's parts is
  the hand.
- A part may be used only once.

## Hard requirements

If either fails the score is 0.

- Files: `movement.json` and every part it names are valid as described above.
- Assembled: in the positions given, the fixed parts taken together and each
  mobile (the barrel included) intersect one another by at most 0.01 mm3, and no
  two fixed parts intersect each other by more than 0.01 mm3.

## Scored requirements

Each passes or fails. Weights in brackets; the total is 17.

- **Free to turn [1].** Each mobile, turned through a full turn in 72 steps of 5
  degrees, never intersects the fixed parts by more than 0.01 mm3.
- **Held [2].** Each mobile, the barrel included, is moved 0.3 along +x, -x, +y,
  -y, +z and -z in turn and must intersect what holds it by more than 0.01 mm3
  every time. For the four sideways moves, anything else counts (fixed parts and
  other mobiles). For the two moves along z, only the fixed parts and mobiles on
  the same axis (within 0.01) count: a wheel may not be kept in place by a wheel
  on a different arbor. So each mobile can turn but cannot wander.
- **The train runs [3].** No mobile is given two different speeds by the
  declared meshes, each of the three hand mobiles is driven from the barrel, and
  every declared mesh passes this test. Starting from the assembled position,
  at step i (i = 0, 1, ..., 8 x max(driver teeth, driven teeth) - 1) the driver
  is turned counter-clockwise (seen from +z) by i x 360 / (8 x driver teeth)
  degrees about its axis and the driven mobile clockwise by that angle x driver
  teeth / driven teeth about its own. Then
  - at every step the two mobiles intersect by at most 0.01 mm3 (no jam);
  - at every fourth step the smallest distance between them is at most 0.1
    (they stay engaged);
  - at every eighth step, turning the driver a further quarter of its tooth
    pitch (90 / driver teeth degrees, counter-clockwise) while the driven mobile
    is held makes them intersect by more than 0.01 mm3 (the teeth really drive).
- **Nothing else collides [1].** Every pair of mobiles that does not mesh is
  turned together at the speeds the tooth counts give (a mobile that is not
  driven stands still): 144 equal steps covering one full turn of the faster of
  the two, then 144 equal steps covering one full turn of one relative to the
  other. At every step they intersect by at most 0.01 mm3.
- **Hour hand [2], minute hand [2], seconds hand [2], hand arrangement [1].** The
  watch must tell the time: the hands must move as the hands of a watch do. A
  hand is driven only through meshes that pass the test of "The train runs": a
  declared mesh that fails that test drives nothing, so the hand speeds are
  worked out from the barrel through the passing meshes only. (The same holds
  for the 24-hour hand of stages 2 and 3.)
- **Hands reach [1].** Each hand part reaches at least 5.0 from its axis.
- **Size [1].** Everything, as it turns, stays within 20.7 of the vertical line
  through `case_centre`, and the whole movement including the barrel is at most
  13.4 tall in z. These limits are the same at every stage.
- **Printable [1].** The smallest printable feature is 0.2. Each of your parts
  (not the barrel) is tested like this: it is turned into voxels on a 0.05 grid,
  a voxel being solid when its centre is inside the part. A solid voxel survives
  if its centre is at least 0.075 (1.5 voxels) from the centre of the nearest
  voxel that is not solid. The printable body is every solid voxel whose centre
  is within 0.05 of a surviving voxel's centre. The part passes if something
  survives and no solid voxel's centre is further than 0.2 from the printable
  body. Ordinary gear teeth of module 0.12 or more pass; a wall, web or roof 0.2
  thick or less does not. How the grid lines up with your part is not fixed, so
  leave a little margin.
- **Light [2].** The fixed parts together have a volume of at most 2117 mm3,
  and all parts of your mobiles together (the supplied barrel not counted) at
  most 512 mm3. The limits are the same at every stage. Volumes are those
  of the solids the grader builds from your part files: for the fixed parts, the
  volume of their union; for the mobiles, the sum of the volumes of every part
  of every mobile, each part counted on its own.

## Score

```
p     = (weight of scored requirements passed) / 17
score = 0 if a hard requirement fails, otherwise
score = 0.5 * p^2 + 0.5 * (1 if every scored requirement passes, else 0)
```

## Stage 2: add a 24-hour hand

You receive a finished stage-1 movement in `work/` (the same files are in
`previous/` for reference). Add a **24-hour hand**: a fourth hand that shows day
and night. Declare it as `"day"` under `hands`.

What is frozen:

- every mobile of the received movement keeps its name and its axis (the same
  two numbers, unchanged);
- every part file of those mobiles stays byte-for-byte the same and stays in its
  mobile (you may add new parts to a mobile);
- every declared mesh stays, and the hour, minute and seconds entries under
  `hands` stay.

You may add mobiles, add parts, add meshes, and replace or add fixed parts.

Hard requirements: the two of stage 1, the frozen items above, and a 24-hour
hand is declared (`hands.day` names a mobile and one of that mobile's parts,
and that part is a new part, not one of the received parts).

Scored requirements (total weight 21): all eleven of stage 1, still passing with
their weights, plus

- **24-hour hand [3].** It moves as a 24-hour hand does.
- **24-hour hand placement [1].** Its axis is at least 6.0 from the hour hand's
  axis, and the hand part reaches at least 3.0 from its own axis.

Score: the stage-1 formula with p out of 21.

## Stage 3: change request, a faster barrel

You receive a finished stage-2 movement in `work/` (the same files are in
`previous/` for reference). The barrel is replaced by one that is identical in
every way (same `meshes/barrel.stl`, same place, same teeth) except that it turns
**clockwise once every 6 hours** instead of once every 8. Rework the movement so
that it meets every requirement of stage 2 with this barrel, and keep as many of
the received part files as you can.

Nothing is frozen: you may change, add, remove and rename anything. The hard
requirements are the two of stage 1, plus: **the change request is met**, that
is, the hour hand, minute hand, seconds hand and 24-hour hand requirements all
pass with the barrel turning once every 6 hours. The scored requirements are all thirteen of
stage 2 with their weights (total 21), tested with the barrel turning once every
6 hours. The hands must still move as the hands of a watch do, and the 24-hour
hand as a 24-hour hand does.

Kept parts. A received part (a part named in the received `movement.json`) is
**kept** if its file in your submission is byte-for-byte the same as the received
file and

- for a received fixed part: it is still listed under `fixed`;
- for a received part of a mobile: it is still in a mobile of the same name, whose
  axis is the same as the received mobile's axis (the same two numbers,
  unchanged), and that mobile is driven from the barrel through declared meshes
  that pass the test of "The train runs".

A received file that is not named in your `movement.json`, that moves to another
mobile, to a renamed mobile or to `fixed`, or that sits on a mobile nothing drives,
is not kept.

```
kept share = (received part files that are kept) / (received part files)
factor     = min(1, kept share / (15/17))
p          = (weight of scored requirements passed) / 21
score      = 0 if a hard requirement fails, otherwise
score      = (0.5 * p^2 + 0.5 * (1 if every scored requirement passes, else 0)) * factor
```

The share counts part files: each file counts once, whatever its size or what it
holds. 15/17 (about 0.882) is the kept share of a reference solution, which keeps 15 of
the 17 part files it receives. The factor is exactly 1 at a kept share of 15/17
or more.

## Stage 4: assemble it

You receive a finished stage-3 movement in `work/` (also in `previous/`).
`movement.json` and every part file are frozen: byte-for-byte unchanged.

Write `work/assembly.json`:

```
{"order": ["part_name", ...], "paths": {"part_name": [P, P, ...], ...}}
```

`order` lists every part named in `movement.json`, and `barrel`, in the order
they are put in. A name that is not a part is ignored; a name that appears more
than once counts at its first place only. A part that is not in `order` is not
installed, and it stands in its assembled position from the start, so every part
in `order` is tested against it. Each P is a 4x4 matrix as four rows of four numbers that moves
the part from its assembled position (`world = R * assembled + t`, last row
`0 0 0 1`); the parts are given in their assembled position, so the last pose of
every path is the identity.

Rules for a path:

1. Every matrix is finite and a proper rotation plus translation (R^T R = I and
   det R = +1, within 1e-6); the last pose is the identity within 1e-6.
2. In the first pose the part's bounding box lies wholly outside the bounding box
   of the complete movement (all parts and the barrel, assembled) grown by 5.0 on
   every side.
3. Between consecutive poses no vertex of the part moves more than 0.2.
4. At least 2 and at most 1,500 poses.
5. In every pose the part intersects each part placed before it by at most
   0.01 mm3. Parts of the same mobile are pressed onto each other and are not
   tested against one another. The barrel counts as a part of the mobile `barrel`.

A part whose path obeys rules 1 to 5 is installed. A part that breaks a rule is
not installed, but it still stands in its assembled position for the parts that
follow.

```
p     = (parts installed) / (all parts, the barrel included)
score = 0 if the Files requirement of stage 1 fails, if movement.json or a part file was changed,
        or if assembly.json cannot be read
score = 0.5 * p^2 + 0.5 * (1 if every part is installed, else 0)
```

## Tools

The tools return measurements. They do not say whether a requirement is met; the
numbers above let you decide that yourself.

| Tool | Returns |
| --- | --- |
| `get_spec` | this document |
| `measure PART` | volume, bounding box, triangle count |
| `section PART --axis x|y|z --at V [--polygons]` | cross-section area, contours, bounds |
| `distance A B [--search D]` | smallest distance between two parts, up to D (default 5); 0 if they overlap |
| `interference A B` | intersection volume of two parts |
| `speeds` | from your declared meshes: clockwise turns per hour of every mobile, as exact fractions; mobiles not driven; conflicting meshes |
| `spin MOBILE` | the free-to-turn test for one mobile: largest overlap and its step |
| `held MOBILE` | the held test for one mobile: overlap after each of the six moves |
| `mesh DRIVER DRIVEN` | the train test for one declared mesh: largest overlap and its step, largest gap, smallest overlap from the quarter-pitch push |
| `clear A B` | the collision test for two mobiles that do not mesh |
| `extent` | largest distance from the case centre reached by anything, the z range, and how far each hand reaches |
| `submit` | copies `movement.json` and the parts it names to the submission folder; answers "accepted" or a format error |

PART is one of your part names (no extension) or `barrel`. MOBILE is one of your
mobile names or `barrel`.

You may import the code the tools use (`tools/geometry/`) in your own scripts.

Only the submission folder as it is when you stop is graded. You may submit as
often as you like; the last accepted submission counts.
