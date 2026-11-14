# Watch gear train: specification

## The job

Design the gear train of a mechanical wristwatch, as 3D-printable parts. The work
is done in four stages, each by a different engineer who starts from the result
of the stage before:

1. **Design** the movement (this document up to "Stage 2").
2. **Extend** it with a 24-hour hand, without touching the existing wheels.
3. **Change** it: the barrel now turns faster; rework the movement for that while
   keeping as much of the received parts as you can.
4. **Assemble** it: an order and a collision-free path for every part.

Your instruction file says which stage you are doing. Read the later stages too:
what you design in stage 1 has to survive them, and the size limits and the two
volume limits are the same at every stage.

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
  at most 120 s and, where the operating system supports such a limit,
  4,096 MB of memory (it runs in its own process).
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
  about the vertical line through `axis`. Parts of one mobile touch but must not
  overlap each other (see "Assembled"). Do not list `barrel`; it already exists.
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
  mobile (the barrel included) intersect one another by at most 0.01 mm3, no
  two fixed parts intersect each other by more than 0.01 mm3, and no two parts
  of the same mobile intersect each other by more than 0.01 mm3 (they may touch,
  like a wheel on its arbor). Because curved surfaces are meshed to within 0.001
  of the true surface, a bore and a shaft drawn with the same radius can overlap
  by slivers; a fit needs a small radial clearance. And the fixed parts form one
  frame: two fixed parts are joined when their smallest distance is at most 0.01,
  and every fixed part must be joined to every other through a chain of joined
  fixed parts. (This asks only that the frame's parts touch; it does not test how
  they are fastened.)

## Scored requirements

Each passes or fails. Weights in brackets; the total is 23.

- **Free to turn [1].** Each mobile, turned through a full turn in 72 steps of 5
  degrees, never intersects the fixed parts by more than 0.01 mm3.
- **Held [2].** Only the frame holds. Each mobile, the barrel included, is moved
  0.3 along +x, -x, +y, -y, +z and -z in turn, and must be held in every one of
  the six directions. Moved in a direction, a mobile is held when it intersects
  the fixed parts by more than 0.01 mm3, or intersects by more than 0.01 mm3 a
  mobile on the same axis (within 0.01) that is itself held in that direction;
  this is worked out until nothing changes. So an hour wheel may rest on a cannon
  pinion that rests on the frame, but two mobiles cannot hold each other up, and a
  mobile on another axis never holds. So each mobile can turn but cannot wander.
- **Seated [2].** Every part of a mobile that has more than one part is seated
  on the rest of its mobile: moved 0.3 along +x, -x, +y and -y in turn it must
  intersect the other parts of the same mobile by more than 0.01 mm3 every time,
  and moved 0.3 along +z or along -z (at least one of the two) it must intersect
  them by more than 0.01 mm3. So a wheel needs a bore that fits its arbor and a
  shoulder to rest against; a part that floats free of its mobile fails. The
  parts of each mobile must also form one piece: every part must be linked to
  every other by a chain of parts of that mobile, each within 0.02 of the next,
  so a group of parts that hold only each other fails. The
  supplied barrel and mobiles of one part are not tested.
- **The train runs [3].** No mobile is given two different speeds by the
  declared meshes, each of the three hand mobiles is driven from the barrel, every
  declared mesh passes this test, and every mobile is driven from the barrel
  through declared meshes that pass it (a mobile nothing drives fails this). Starting from the assembled position,
  at step i (i = 0, 1, ..., 8 x max(driver teeth, driven teeth) - 1) the driver
  is turned counter-clockwise (seen from +z) by i x 360 / (8 x driver teeth)
  degrees about its axis and the driven mobile clockwise by that angle x driver
  teeth / driven teeth about its own. Then
  - at every step the two mobiles intersect by at most 0.01 mm3 (no jam), and
    so they do at two more positions after every eighth step: one third and one
    fifth of a step further on (i + 1/3 and i + 1/5 in the formula above, for
    i = 0, 8, 16, ...), so tooth counts that differ from the real ones are found;
  - at every fourth step the smallest distance between them is at most 0.1
    (they stay engaged);
  - at every eighth step, turning the driver a further quarter of its tooth
    pitch (90 / driver teeth degrees, counter-clockwise) while the driven mobile
    is held makes the teeth really drive. Call the extra intersection that this
    push creates V (the intersection after the push less the intersection before
    it), H the height in z of the region where the two intersect after the push,
    and m = 2 x (distance between the two axes) / (driver teeth + driven teeth),
    the mesh's module. Then V must be at least 0.001 mm3, and V / H must be more
    than 0.5 x m x m. V / H is the area the push cuts into the other gear's teeth,
    so this does not depend on how wide the gears are, and m x m scales it to the
    size of the teeth: an honest involute pair at module 0.12 with a total
    backlash of 0.06 gives about 1.2 x m x m, at module 0.25 about 1.6 x m x m.
- **The train runs with its arbors slightly out of place [2].** Arbors are never
  exactly where they were drawn. Every declared mesh must also pass the test of
  "The train runs" twice more: with the driven mobile (the one declared as
  `driven` in the mesh) moved 0.03 straight away from the driver's axis, and
  with it moved 0.03 straight towards the driver's axis (in both cases it turns
  about its moved axis; if the two axes coincide, "away" is +x and "towards" is
  -x). In both positions the same
  three conditions must hold, with the same steps and the same turning angles as
  in the drawn position. This requirement does not change which meshes drive the
  hands: that is decided in the drawn position only.
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
- **Hands reach [1].** Each hand part reaches at least 5.0 from its axis, lies
  wholly above the frame (its lowest point is no lower than the highest point of
  any fixed part), and points: its centre of volume is at least 0.5 from its
  axis.
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
- **Light [2].** The fixed parts together have a volume of at most 355 mm3,
  and all parts of your mobiles together (the supplied barrel not counted) at
  most 278 mm3. The limits are the same at every stage. Volumes are those
  of the solids the grader builds from your part files: for the fixed parts, the
  volume of their union; for the mobiles, the sum of the volumes of every part
  of every mobile, each part counted on its own. Stages 2 and 3 add or remake
  parts under these same two limits, and the parts you receive cannot be made
  lighter without being changed, so a design that spends a limit at stage 1
  leaves no room for what the later stages need.

## Score

```
p     = (weight of scored requirements passed) / 23
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

Scored requirements (total weight 27): all fourteen of stage 1, still passing with
their weights, plus

- **24-hour hand [3].** It moves as a 24-hour hand does.
- **24-hour hand placement [1].** Its axis is at least 6.0 from the hour hand's
  axis, the hand part reaches at least 3.0 from its own axis, and like the other
  hands it lies wholly above the frame and its centre of volume is at least 0.5
  from its axis.

Score: the stage-1 formula with p out of 27.

## Stage 3: change request, a faster barrel

You receive a finished stage-2 movement in `work/` (the same files are in
`previous/` for reference). The barrel is replaced by one that is identical in
every way (same `meshes/barrel.stl`, same place, same teeth) except that it turns
**clockwise once every 6 hours** instead of once every 8. Rework the movement so
that it meets every requirement of stage 2 with this barrel, and keep as much of
the received parts as you can.

Nothing is frozen: you may change, add, remove and rename anything. The hard
requirements are the two of stage 1, plus: **the change request is met**, that
is, the hour hand, minute hand, seconds hand and 24-hour hand requirements all
pass with the barrel turning once every 6 hours. The scored requirements are all sixteen of
stage 2 with their weights (total 27), tested with the barrel turning once every
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
fixed share  = (volume of the received fixed parts that are kept) / (volume of the received fixed parts)
mobile share = (volume of the received parts of mobiles that are kept) / (volume of the received parts of mobiles)
kept share   = the smaller of the two
factor       = min(1, kept share / 0.626)
p          = (weight of scored requirements passed) / 27
score      = 0 if a hard requirement fails, otherwise
score      = (0.5 * p^2 + 0.5 * (1 if every scored requirement passes, else 0)) * factor
```

The shares count material, not files: a received part counts with its volume
(the volume of the solid the grader builds from the received file, each part on
its own), so splitting a design into many files, or adding small parts, does not
change them. The fixed parts and the parts of mobiles are counted separately and
the smaller share is used, so the plates cannot outweigh the wheels. A reference
solution keeps all of the fixed volume and 0.6267 of the mobile volume it
receives; the factor is exactly 1 at a kept share of 0.626 or more.

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
   0.01 mm3, parts of its own mobile included: every part has to slide into
   place past the parts already there.

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
