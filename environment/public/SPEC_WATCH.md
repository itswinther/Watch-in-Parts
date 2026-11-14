# Watch gear train: specification

## The job

Design the gear train of a mechanical wristwatch, as 3D-printable parts.

The mainspring barrel is supplied (`meshes/barrel.stl`). It turns **clockwise,
once every 8 hours**. Drive the watch's **hour, minute and seconds hands** from
it. There is no escapement and no winding or setting mechanism in this task: the
barrel is simply the driver, and the grader turns it at that steady speed.

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

## What you submit

A folder `work/` containing `movement.json` and `parts/<name>.stl`.

Each part is one STL: a single closed manifold shell with positive volume, at
most 200,000 triangles, in its assembled position. At most 60 parts. Part names
use letters, digits, `_` and `-`.

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

- `fixed`: parts that do not move (plates, bridges, pillars, cocks).
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
  mobile (the barrel included) intersect one another by at most 0.01 mm3.

## Scored requirements

Each passes or fails. Weights in brackets; the total is 16.

- **Free to turn [1].** Each mobile, turned through a full turn in 72 steps of 5
  degrees, never intersects the fixed parts by more than 0.01 mm3.
- **Held [2].** Each mobile, the barrel included, moved 0.3 along +x, -x, +y, -y,
  +z and -z in turn, intersects everything else (fixed parts and other mobiles)
  by more than 0.01 mm3 every time. So each mobile can turn but cannot wander.
- **The train runs [3].** No mobile is given two different speeds by the
  declared meshes, each of the three hand mobiles is driven from the barrel, and
  every declared mesh passes this test: the driver is turned in steps of one
  eighth of its tooth pitch, the driven mobile turning with it at the speed the
  tooth counts give, for 8 x max(driver teeth, driven teeth) steps. Then
  - at every step the two mobiles intersect by at most 0.01 mm3 (no jam);
  - at every fourth step the smallest distance between them is at most 0.1
    (they stay engaged);
  - at every eighth step, turning the driver a further quarter of its tooth
    pitch while the driven mobile is held makes them intersect by more than
    0.01 mm3 (the teeth really drive).
- **Nothing else collides [1].** Every pair of mobiles that does not mesh, turned
  together at their own speeds (144 steps over one turn of the faster, and 144
  over one turn of one relative to the other), intersects by at most 0.01 mm3.
- **Hour hand [2], minute hand [2], seconds hand [2], hand arrangement [1].** The
  watch must tell the time: the hands must move as the hands of a watch do.
- **Hands reach [1].** Each hand part reaches at least 5.0 from its axis.
- **Size [1].** Everything, as it turns, stays within 23.0 of the vertical line
  through `case_centre`, and the whole movement including the barrel is at most
  16.0 tall in z.

## Score

```
p     = (weight of scored requirements passed) / 16
score = 0 if a hard requirement fails, otherwise
score = 0.5 * p^2 + 0.5 * (1 if every scored requirement passes, else 0)
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

PART is one of your part names (no `.stl`) or `barrel`. MOBILE is one of your
mobile names or `barrel`.

You may import the code the tools use (`tools/geometry/`) in your own scripts.

Only the submission folder as it is when you stop is graded. You may submit as
often as you like; the last accepted submission counts.
