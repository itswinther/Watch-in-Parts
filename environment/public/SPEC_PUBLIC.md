# Board in a Box: public specification (instance H1)

Everything that is graded is stated here with its number. Nothing else is graded.

## Frame and units

Millimetres. Right-handed frame. Origin at a corner of the circuit board (PCB).
The PCB bottom face is at z = 0, its top face at z = 1.6.

## Supplied bodies

| Body | Final pose | Geometry |
| --- | --- | --- |
| PCB | fixed | Box x 0..70, y 0..45, z 0..1.6, with four through holes of diameter 3.2 at (3.5, 3.5), (66.5, 3.5), (3.5, 41.5), (66.5, 41.5). |
| J1, USB-C socket, top side | with PCB | Box x -1.5..6, y 18..27, z 1.6..4.9. |
| J2, audio jack, bottom side | with PCB | Box x 58..72.5, y 9..15, z -5..0. |
| C1, capacitor, top side | with PCB | Cylinder, diameter 8, axis along z at (15, 33), z 1.6..12.1. |
| J4, battery connector, bottom side | with PCB | Box x 9..15, y 38..43, z -4.5..0. |
| Battery | you choose | Box 48 x 30 x 7.5. Its own frame is x 0..48, y 0..30, z 0..7.5. The face x = 0 is the lead face; the face z = 7.5 is the top face. |
| Lid | fixed | Flat plate, box x -2..73.5, y -2..47, z 12.5..15.5. |

"Board" below means the PCB together with J1, J2, C1 and J4 as one rigid body.
The components are J1, J2, C1 and J4.

Plug keep-outs (space a plug needs, must stay empty of printed material):

- J1: box x -21.5..-1.5, y 16.25..28.75, z -0.25..6.75 (a 12.5 x 7 section, 20 long, pointing -X).
- J2: cylinder of diameter 8 with axis along x through (y 12, z -2.5), x 72.5..92.5.

## What you make

Two printed parts, both in the world frame in their final pose:

- `base.stl`: a one-piece tub that holds the board and the battery and carries the lid.
- `door.stl`: closes the opening through which the battery is inserted.

And `assembly.json`, which states how each body is moved into place.

## Limits

- Envelope for printed parts: x -2.0..73.5, y -2.0..47.0, z -10.25..12.5. Every
  vertex of both parts must be inside it (tolerance 0.01).
- Minimum wall thickness 1.6 (tested as described under "Wall thickness").
- Material: volume(base) + volume(door) at most 17333.44 mm3.
- Each STL: at most 200,000 triangles, one closed manifold shell, positive volume,
  no self-intersection. ASCII or binary.
- Screws are out of scope. Nothing tests whether parts are retained against a pull.

## Assembly contract

`assembly.json` is one JSON object:

```
{"board": [P, P, ...], "lid": [...], "battery": [...], "door": [...]}
```

Each P is a 4x4 matrix as four rows of four numbers. It maps the body from its
supplied frame to the world: `world = R * local + t`, last row `0 0 0 1`.
The board, the lid and the door are supplied in their final pose, so their final
pose is the identity matrix. The battery is supplied in its own frame.

Bodies are placed in this order: board, lid, battery, door. The base is in place
from the start. The battery goes in after the lid, because it must be replaceable
without opening the case.

Rules:

1. In its first pose a body has zero intersection volume with the envelope box and
   its vertex centroid is at least 30 from where it is in its last pose.
2. The last pose is the final pose: the identity (within 1e-6) for board, lid and
   door; your choice for the battery.
3. Between consecutive poses no vertex of the body moves more than 0.5.
4. At least 2 and at most 2,000 poses per body.
5. Every number is finite and every matrix is a proper rotation plus a translation
   (R^T R = I and det R = +1, within 1e-6).
6. A pose is good if the moving body intersects each body already in place
   (the base, and every body placed earlier) by at most 0.2 mm3.

Only the listed poses are tested. Nothing is interpolated.

## Hard requirements

If any one of these fails the score is 0.

- Both STL files load and meet the STL limits above.
- Every printed vertex is inside the envelope.
- With everything in its final pose, no two bodies (base, door, board, lid,
  battery) intersect by more than 0.2 mm3.
- `assembly.json` obeys rules 1 to 5.
- Enclosed: with everything in its final pose, a ball of diameter 1.0 coming from
  outside cannot get within 1.5 of the board or the battery. For this test the two
  connector openings are plugged: the J1 keep-out section grown by 3.0 on every
  side (a rectangle y 13.25..31.75, z -3.25..9.75) for all x <= 0, and the J2
  keep-out section grown by 3.0 (a circle of diameter 14) for all x >= 70.
  Tested on a 0.25 voxel grid, so a gap narrower than about 0.75 is closed.

## Scored requirements

Each passes or fails. Weights in brackets; the total is 23.

Assembly paths, rule 6 over every listed pose:

- Board path [3]. Lid path [1]. Battery path [3]. Door path [1].

Fit:

- Board supported [1]: on the plane z = -0.05, printed material covers at least
  4 mm2 inside the ring between diameter 3.2 and diameter 7 around at least three
  of the four PCB holes.
- Board located [1]: moving the bare PCB (no components) by 0.6 along +X, along
  -X, along +Y, along -Y and along -Z each makes it intersect the printed parts by
  more than 0.2 mm3.
- Battery held [1]: moving the battery by 2.0 along each of +X, -X, +Y, -Y, +Z,
  -Z makes it intersect the other bodies (base, door, board, lid) by more than
  0.2 mm3.
- Component clearance [1]: the smallest distance from each of J1, J2, C1, J4 to
  the printed parts is at least 0.4.
- Battery swell [1]: the battery's 48 x 30 faces are horizontal, and the slab 1.0
  thick directly above its upper 48 x 30 face intersects the other bodies by at
  most 0.2 mm3.
- Battery lead [1]: the centre of the battery's lead face is within 40 of the
  centre of J4, which is (12, 40.5, -2.25).

Connectors:

- J1 keep-out clear [1], J2 keep-out clear [1]: printed parts intersect the
  keep-out by at most 0.2 mm3.
- J1 opening size [1]: on the plane x = -1.05, the area not covered by printed
  material inside the rectangle y 13.25..31.75, z -3.25..9.75 is at most 130.5 mm2.
- J2 opening size [1]: on the plane x = 72.55, the area not covered by printed
  material inside the circle of diameter 14 centred on (y 12, z -2.5) is at most
  78.53 mm2.

Wall thickness:

- Base [1], door [1]: the part is opened with a ball of radius 0.8 (eroded, then
  grown back) on a 0.2 voxel grid. What is left must be one connected piece and no
  point of the part may be further than 0.7 from it. A wall 1.6 thick always
  survives; anything thinner than 1.2 never does.

Seating and material:

- Door stop [1]: moving the door 1.0 along +Z makes it intersect the base by more
  than 0.2 mm3.
- Lid seated [1]: moving the lid 0.2 along -Z makes it intersect the base by more
  than 0.2 mm3.
- Material [1]: the material limit above.

## Score

```
score = 0 if any hard requirement fails, otherwise
score = 0.5 * p^2 + 0.5 * (1 if every scored requirement passes, else 0)
p     = (weight of scored requirements passed) / 23
```

## Tools

The tools return measurements. They do not say whether a requirement is met; the
numbers above let you decide that yourself.

| Tool | Returns |
| --- | --- |
| `get_spec` | this document |
| `measure PART` | volume, surface area, bounding box, triangle count |
| `section PART --axis x|y|z --at V [--polygons]` | area, contour count and bounds of the cross-section on that plane |
| `distance A B` | smallest surface distance between two parts (0 if they overlap) |
| `interference A B` | intersection volume |
| `thickness base|door` | the wall-thickness opening: pieces left and largest distance from the part to what is left |
| `sweep` | for `work/assembly.json`: contract format messages, and per body the worst intersection volume over its listed poses, the pose index and the body it was with |
| `probe` | the enclosure test: how close a 1.0 ball from outside gets to the board or battery |
| `submit` | copies `work/base.stl`, `work/door.stl`, `work/assembly.json` to the submission folder; answers "accepted" or a format error |

`measure`, `section`, `distance` and `interference` accept `--move` for the first
part: 3 numbers (a translation) or 16 numbers (a 4x4 matrix, row by row).

Part names: `base`, `door` (your files in `work/`), `board`, `pcb`, `J1`, `J2`,
`C1`, `J4`, `lid`, `battery` (own frame), `keepout_J1`, `keepout_J2`, `envelope`.

Only what is in the submission folder when you stop is graded. You may submit as
often as you like; the last accepted submission counts.
