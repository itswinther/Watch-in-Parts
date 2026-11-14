# Moving Day: public specification

Everything that is graded is stated here with its number. Nothing else is graded.

## Goal

Carry every piece of furniture from the staging box outside the front door to
its given final pose inside the apartment, without anything passing through a
wall, a floor, a ceiling or furniture that is already in place. You decide the
order in which the pieces are carried in and the path each one takes. Nothing is
designed: the apartment, the furniture and every final pose are fixed.

## Frame and units

Centimetres. Right-handed world frame, +Z is up, the floor is z = 0.

<<INSTANCE>>
The same data is in `instance.json`, and as STL files in `meshes/` (the
apartment in the world frame, each piece in its own frame).

## What you submit

One file, `plan.json`:

```
{"order": ["name", "name", ...],
 "paths": {"name": [P, P, ...], ...}}
```

`order` is the order in which pieces are carried in. Each P is a 4x4 matrix as
four rows of four numbers, mapping the piece from its own frame to the world
(`world = R * local + t`, last row `0 0 0 1`).

## Rules for a path

1. Every matrix is finite and is a proper rotation plus a translation
   (R^T R = I and det R = +1, within 1e-6).
2. In the first pose every vertex of the piece is inside the staging box.
3. The last pose equals the piece's given final pose (every entry within 1e-6).
4. Between consecutive poses no vertex of the piece moves more than 5.0.
5. At least 2 and at most 4,000 poses.
6. In every pose the piece intersects the apartment by at most 1.0 cm3, and
   intersects each piece delivered before it (in its final pose) by at most
   1.0 cm3.

Only the listed poses are tested. Nothing is interpolated. Pieces do not need to
rest on anything while they are carried, and nothing models gravity or grip.

## Delivery and score

Pieces are processed in the order you give. A piece whose path obeys rules 1 to
6 is **delivered**: it then stands in its final pose and later pieces must avoid
it. A piece whose path breaks any rule is not delivered and is treated as absent
from then on. A piece missing from `order` is not delivered. An unknown name in
`order` is ignored; if a name appears twice, only the first counts.

```
p     = (weight of delivered pieces) / (total weight)
score = 0.5 * p^2 + 0.5 * (1 if every piece is delivered, else 0)
```

A file that is not valid JSON, has no `order` list or `paths` object, or is
larger than 32 MB scores 0.

## Tools

The tools return measurements and format messages. They do not give a score.

| Tool | Returns |
| --- | --- |
| `get_spec` | this document |
| `measure PART` | volume, bounding box, triangle count |
| `section PART --axis x|y|z --at V [--polygons]` | area, contour count and bounds of the cross-section on that plane |
| `distance A B [--search D]` | smallest surface distance between two parts, up to D (default 50); 0 if they overlap |
| `interference A B` | intersection volume |
| `sweep` | replays `work/plan.json` exactly as the grader does. Per piece, in your order: format messages, the largest intersection volume over its poses, the index of that pose and what it hit |
| `submit` | copies `work/plan.json` to the submission folder; answers "accepted" or a format error |

Part names are `apartment` and the furniture names. A piece is in its own frame
unless you add `--final` (its final pose) or `--pose` with 16 numbers (a 4x4
matrix, row by row). For the second part of `distance` and `interference` use
`--final2` and `--pose2`.

You may also import the geometry code the tools use (`tools/geometry/`,
functions such as `md.flat_one()`, `inst.apartment()`, `inst.piece(name)`,
`core.apply`, `core.ivol`, `md.replay`) in your own Python scripts, for example
to write a path planner.

Only `submission/plan.json` as it is when you stop is graded. You may submit as
often as you like; the last accepted submission counts.
