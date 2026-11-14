# Pack in a Box: public specification (instance H2)

Everything that is graded is stated here with its number. Nothing else is graded.

## Goal

Design the smallest enclosure that holds four supplied bodies, can actually be
assembled, and leaves three connectors usable. You choose where every body
goes, in which order the bodies are put in, and how each one moves into place.

## Frame and units

Millimetres, right-handed world frame, +Z is up. You place everything; the world
origin is wherever you want it, within 500 of every vertex you use.

## Supplied bodies

Each body is rigid and is given in its own frame. STL files are in `meshes/`.

**A, main board.** One rigid body made of:

| Piece | Box or cylinder in A's frame |
| --- | --- |
| PCB | x 0..70, y 0..45, z 0..1.6, with four through holes of diameter 3.2 at (3.5, 3.5), (66.5, 3.5), (3.5, 41.5), (66.5, 41.5) |
| J1, USB-C socket | x -1.5..6, y 18..27, z 1.6..4.9 |
| J2, audio jack | x 58..72.5, y 9..15, z -5..0 |
| C1, capacitor | cylinder, diameter 8, axis along z at (15, 33), z 1.6..12.1 |
| J4, battery connector | x 9..15, y 38..43, z -4.5..0 |

**B, daughter board.** One rigid body made of:

| Piece | Box in B's frame |
| --- | --- |
| PCB | x 0..38, y 0..27.5, z 0..1.6 |
| Shield can | x 2..24, y 5..22, z 1.6..4.6 |
| J3, card slot | x 26..37, y -1..9, z 1.6..3.8 |
| L1, inductor | x 28..34, y 16..22, z -2.2..0 |

**battery.** Box x 0..48, y 0..30, z 0..7.5 in its own frame. The face x = 0 is
the lead face.

**speaker.** Cylinder of diameter 18, axis along z through x = y = 0, z 0..6.5.

Plug keep-outs, each in its owner's frame. A keep-out is the space a plug needs;
it starts at the connector's outer face and is 20 long.

| Connector | Owner | Keep-out |
| --- | --- | --- |
| J1 | A | box x -21.5..-1.5, y 16.25..28.75, z -0.25..6.75 |
| J2 | A | cylinder of diameter 8, axis along x through (y 12, z -2.5), x 72.5..92.5 |
| J3 | B | box x 25..38, y -21..-1, z 1.2..4.2 |

## What you make

- `base.stl`: one printed part, in the world frame.
- `lid.stl`: a flat rectangular plate, exactly 2.0 thick in z, with its edges
  along x and y, in the world frame in its final position.
- `assembly.json`:

```
{"order": ["B", "A", "battery", "speaker"],
 "paths": {"A": [P, ...], "B": [...], "battery": [...], "speaker": [...], "lid": [...]}}
```

`order` lists the four bodies in the order they are put in; any order is allowed.
The lid always goes on last. Each P is a 4x4 matrix as four rows of four numbers,
mapping the body from its own frame to the world (`world = R * local + t`, last
row `0 0 0 1`). The last pose of a body is its final pose, which is yours to
choose. The lid is given in its final position, so its last pose is the identity.

## Path rules

1. In its first pose a body has zero intersection volume with the bounding box of
   the printed parts (base and lid together), and its vertex centroid is at least
   30 from where it is in its last pose.
2. Between consecutive poses no vertex of the body moves more than 0.5.
3. At least 2 and at most 2,000 poses per body.
4. Every number is finite and every matrix is a proper rotation plus a translation
   (R^T R = I and det R = +1, within 1e-6).
5. A pose is good if the moving body intersects each thing already in place (the
   base, and every body earlier in the order, each in its final pose) by at most
   0.2 mm3.

Only the listed poses are tested. Nothing is interpolated.

## Hard requirements

If any one of these fails the score is 0.

- Files: `base.stl` is one closed manifold shell with positive volume, at most
  200,000 triangles, no self-intersection. `lid.stl` is the plate described above.
  `assembly.json` has the format above.
- Final pose: with everything in its final pose, no two of base, lid, A, B,
  battery, speaker intersect by more than 0.2 mm3.
- Path rules 1 to 4 hold for all five paths.
- Enclosed: with everything in its final pose, a ball of diameter 1.0 coming from
  outside must not get its centre deeper than 2.5 below any face of the bounding
  box of the printed parts. So the outside of the enclosure is box-shaped, with no
  recess deeper than 2.5, and it has no open hole. For this test each connector
  opening is plugged by its keep-out section grown by 1.0 on every side, running
  from 3.0 inside the connector's outer face to the far end of the keep-out.
  Tested on a 0.25 voxel grid, so a gap narrower than about 0.75 is closed.

## Scored requirements

Each passes or fails. Weights in brackets; the total is 20.

- Path of A [3], of B [2], of the battery [1], of the speaker [1], of the lid [1]:
  path rule 5 holds for every listed pose.
- Supported, one each for A, B, battery, speaker [1 each]: moving the body 0.3
  straight down (-Z) makes it intersect everything else by more than 0.2 mm3.
- A located [1]: moving A's bare PCB (no components) by 0.6 along +X, -X, +Y, -Y
  and -Z of the world each makes it intersect everything else by more than 0.2 mm3.
- Keep-out clear, one each for J1, J2, J3 [1 each]: the keep-out intersects the
  printed parts and the four bodies by at most 0.2 mm3 in total, and the centre of
  its far end face lies outside the bounding box of the printed parts.
- Battery swell [1]: the battery's 48 x 30 faces are horizontal, and the slab 1.0
  thick directly above its upper 48 x 30 face intersects everything else by at
  most 0.2 mm3.
- Battery lead [1]: the centre of the battery's lead face is within 40 of the
  centre of J4, which is (12, 40.5, -2.25) in A's frame.
- Wall thickness [1]: the base is opened with a ball of radius 0.8 (eroded, then
  grown back) on a 0.2 voxel grid. What is left must be one connected piece and no
  point of the base may be further than 0.7 from it. A wall 1.6 thick always
  survives; anything thinner than 1.2 never does.
- Lid seated [1]: moving the lid 0.2 straight down makes it intersect the base by
  more than 0.2 mm3.

Nothing tests whether bodies are held sideways or against being lifted; assume
they are fixed with adhesive pads once they rest on something.

## Score

```
V     = volume of the bounding box of base and lid together, in mm3
p     = (weight of scored requirements passed) / 20
size  = clamp((95000 - V) / (95000 - 81343.3), 0, 1)

score = 0                              if any hard requirement fails
score = 0.3 * p^2                      if any scored requirement fails
score = 0.3 + 0.7 * size               if every scored requirement passes
```

A valid design of any size scores at least 0.3. A valid design with a bounding box
of 81,343.3 mm3 or less scores 1.0; that volume has been achieved.

## Tools

The tools return measurements. They do not say whether a requirement is met; the
numbers above let you decide that yourself.

| Tool | Returns |
| --- | --- |
| `get_spec` | this document |
| `measure PART` | volume, bounding box, triangle count |
| `section PART --axis x|y|z --at V [--polygons]` | area, contour count and bounds of the cross-section on that plane |
| `distance A B [--search D]` | smallest surface distance between two parts, up to D (default 5); 0 if they overlap |
| `interference A B` | intersection volume |
| `thickness` | the wall-thickness opening of the base: pieces left, and largest distance from the base to what is left |
| `bbox` | bounding box of base and lid together, and its volume |
| `sweep` | for `work/assembly.json`: format messages, and per body in order the worst intersection volume over its listed poses, the pose index and what it was with |
| `probe` | the enclosure test: how deep below the bounding box faces a 1.0 ball from outside gets its centre |
| `submit` | copies `work/base.stl`, `work/lid.stl`, `work/assembly.json` to the submission folder; answers "accepted" or a format error |

Part names: `base`, `lid` (your files in `work/`); `A`, `B`, `battery`,
`speaker`; pieces `A_pcb`, `J1`, `J2`, `C1`, `J4`, `B_pcb`, `B_shield`, `J3`,
`L1`; keep-outs `keepout_J1`, `keepout_J2`, `keepout_J3`.

Supplied bodies, pieces and keep-outs are returned in the final pose that
`work/assembly.json` gives their body; add `--local` to get the body's own frame.
`measure`, `section`, `distance` and `interference` accept `--move` for the first
part: 3 numbers (a translation) or 16 numbers (a 4x4 matrix, row by row), applied
after the final pose.

Only what is in the submission folder when you stop is graded. You may submit as
often as you like; the last accepted submission counts.
