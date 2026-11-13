# SPEC.md

Version: 0.1 (2026-11-14). Checked by hand only. Feasibility is unconfirmed
until the reference script passes every gate and check.

This file is the single source of truth for instance H1, the assembly contract,
the checks and the score. Changes go through "Proposed spec changes" in
SESSION.md.

## Frame and units

Millimetres. Origin at a corner of board A. The PCB bottom face is at z = 0 and
the top face at z = 1.6.

## Supplied bodies

Each is delivered as one clean manifold mesh, plus the numbers below.

| Body | Final pose | Geometry |
| --- | --- | --- |
| Board A | Fixed | 70 x 45 x 1.6. Holes dia 3.2 at (3.5, 3.5), (66.5, 3.5), (3.5, 41.5), (66.5, 41.5). |
| J1, USB-C (on board A, top side, -X edge) | With board | Body x -1.5..6, y 18..27, z 1.6..4.9. Plug keep-out: 12.5 x 7 section, 20 long, pointing -X. |
| J2, audio jack (on board A, bottom side, +X edge) | With board | Body x 58..72.5, y 9..15, z -5..0. Plug keep-out: dia 8 cylinder, 20 long, pointing +X. |
| C1, capacitor (on board A, top side) | With board | dia 8 x 10.5 tall at (15, 33). |
| J4, battery connector (on board A, bottom side) | With board | x 9..15, y 38..43, z -4.5..0. |
| Battery | Chosen by the agent | 48 x 30 x 7.5, below the board. |
| Lid | Fixed | Flat plate 3.0 thick over the whole footprint, bottom face at z = 12.5. |

## Printed parts

- `base.stl`: one-piece tub with two closed connector windows.
- `door.stl`: covers the battery opening in the floor.

## Limits

- Envelope for printed parts: the reference design's bounding box plus 0.15 per
  side. Nominal: x -2.0..73.5, y -2.0..47.0, z -10.25..12.5.
- Minimum wall: 1.6.
- Material budget: 1.15 x the reference design's printed volume.
- Screws are out of scope. The board, lid and door are assumed screwed down, and
  no check tests retention against a pull.

## Assembly contract

The submission is `base.stl`, `door.stl` and `assembly.json`. The JSON gives a
list of rigid poses for each body, in the fixed order board A, lid, battery,
door. The battery comes after the lid because the battery must be serviceable
without opening the case.

1. The first pose puts the body wholly outside the envelope and at least 30 from
   its final pose.
2. The last pose is the final pose. It is fixed for board A, lid and door.
3. No vertex moves more than 0.5 between consecutive poses.
4. At most 2,000 poses per body.
5. Every matrix is finite and is a proper rotation plus a translation
   (R^T R = I and det = +1 within 1e-6).
6. A pose passes if the moving body intersects each body already placed by at
   most 0.2 mm3.

Only the listed poses are checked. Nothing is interpolated, in the tool or in
the grader.

## Gates (each 0 or 1)

| ID | Gate | Definition |
| --- | --- | --- |
| G1 | Valid files | Each STL has at most 200,000 triangles and is one closed manifold shell with positive volume. ASCII and binary STL are both accepted. |
| G2 | Envelope | Every printed vertex is inside the envelope, tolerance 0.01. |
| G3 | Final pose | No two bodies intersect by more than 0.2 mm3. |
| G4 | Contract | `assembly.json` obeys every rule of the assembly contract. |
| G5 | Enclosed | With all bodies placed, a 1.0 sphere cannot pass from outside to the cavity except through the two keep-out sections grown by 3.0. 0.25 voxels. |

## Checks

19 checks, total weight 23. The denominator is always all 19; a missing feature
is a failed check.

| ID | Check | Definition | Weight |
| --- | --- | --- | --- |
| A1 | Board A path | Every pose passes. | 3 |
| A2 | Lid path | Every pose passes. | 1 |
| A3 | Battery path | Every pose passes, with board A and lid placed. | 3 |
| A4 | Door path | Every pose passes. | 1 |
| F1 | Board supported | Printed material within 0.1 of the PCB bottom over at least 4 mm2, inside the dia 7 ring of at least three holes. | 1 |
| F2 | Board located | Moving board A 0.6 along +X, -X, +Y, -Y and -Z each makes its bare PCB intersect printed parts by more than 0.2 mm3. | 1 |
| F3 | Battery held | Moving the battery 2.0 along each of the six axis directions intersects another body by more than 0.2 mm3. | 1 |
| F4 | Component clearance | Every component on board A is at least 0.4 from printed parts. | 1 |
| F5 | Battery swell | At least 1.0 free above the battery's top face. | 1 |
| F6 | Battery lead | Centre of the battery's lead face within 40 of the centre of J4. | 1 |
| K1 | J1 keep-out clear | Printed parts intersect the J1 plug keep-out by at most 0.2 mm3. | 1 |
| K2 | J2 keep-out clear | Printed parts intersect the J2 plug keep-out by at most 0.2 mm3. | 1 |
| K3 | J1 window size | At the wall mid-plane, open area inside the keep-out section grown by 3.0 is at most the area of that section grown by 1.0. | 1 |
| K4 | J2 window size | Same as K3, for J2. | 1 |
| W1 | Base wall thickness | Open the part with a 0.8 ball. The result is one connected piece, and no point of the part lies more than 0.5 from it. 0.2 voxels. | 1 |
| W2 | Door wall thickness | Same as W1, for the door. | 1 |
| S1 | Door stop | Moving the door 1.0 along +Z intersects the base by more than 0.2 mm3. | 1 |
| S2 | Lid seated | Moving the lid 0.2 along -Z intersects the base by more than 0.2 mm3. | 1 |
| M1 | Material | Total printed volume is at most the budget. | 1 |

Notes:

- F3 and F5 together put the battery's top face between 1.0 and 2.0 below the
  board.
- Voxel checks (G5, W1, W2) fill a voxel only when its centre is inside the
  solid, never on a surface hit.
- State the graded thresholds in the public spec, including any margin added for
  voxel error.

## Score

```
S = G * (0.5 * p^2 + 0.5 * [all 19 checks pass])
G = G1 * G2 * G3 * G4 * G5
p = (weight of checks passed) / 23
```

Report strict pass rate (share of runs with S = 1) as the headline, with S and p
beside it.

## Tools the agent gets (MCP)

`get_spec`, `load_part`, `measure`, `section`, `distance`, `interference`,
`sweep`, `thickness`, `probe`, `submit`.

- Tools take mesh files and numbers only. They never execute submitted code.
- Tools return geometry facts. No check IDs, no requirement names, no pass/fail
  on a requirement.
- `sweep` takes the same `assembly.json` as the grader and returns the worst
  intersection volume and its pose index per body.
- `submit` returns "accepted" or a format error.
- Tools apply the same size caps as the grader (triangles, poses).
- Part names are whitelisted. No path arguments.

## Grader

- Runs in Harbor's separate verifier, from its own directory, with `python -I`.
- Opens exactly three declared artifact files by absolute path. Ignores every
  other file.
- Loads the spec and the supplied bodies from its own image.
- Never runs submitted code.
- Writes reward 0 first, overwrites it at the end.
- Each check runs in its own try block. An exception, a timeout or a non-finite
  number fails that check.
- Normalises each part with a self-union at load; rejects it if the volume
  changes by more than 0.5%.
- Tools and grader are built from one pinned image and share one geometry module.

## Anchor suite

Submissions with expected scores, run as regression tests inside the one-command
evaluation. Expected scores are hand estimates until measured.

| Anchor | Expected S |
| --- | --- |
| Reference design | 1.0 |
| Do nothing (no files) | 0 |
| Half-written or unreadable file | 0 |
| Any example file shipped in the instruction or README | 0 |
| Whole wall removed and called a slot | 0 (G5) |
| U-slot open to the rim | 0 (G5) |
| Non-rigid, NaN or teleporting path | 0 (G4) |
| Parts intersecting in the final pose | 0 (G3) |
| Lazy tub: thick box, windows at the coarse limit, no pegs, straight-down path | under 0.25 |
| Complete design, no valid board path (fails A1 only) | about 0.38 |
| Complete design, no pegs (fails F2 only) | about 0.46 |
| Complete design, blind pocket with no plug access (fails K2 only) | about 0.46 |

Rules the suite asserts:

1. Every cheat anchor scores below the complete design that fails only A1.
2. Sweeping one reference parameter across a threshold flips the score where
   this spec says it should.
3. The worst legal submission (maximum triangles, maximum poses) is graded in
   under half the verifier time limit.
