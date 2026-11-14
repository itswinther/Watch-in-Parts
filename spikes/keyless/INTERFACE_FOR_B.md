# Keyless works as the fifth part of the one watch job: interface for B

This answers B's request of 14 Nov 14:08 ("to A (Mikael), from B (orchestrator)"). It is a draft by A
(Mikael + Claude). Nothing in B's files or in the keyless v1 runs changes because of it.

## 1. Engine entry point

**From the command line (keyless v1, as it is):**

```
python -I spikes/keyless/grade.py SUBMISSION_DIR DATA_DIR --reward REWARD.txt --details DETAILS.json --jobs 3
```

- `SUBMISSION_DIR` holds `keyless.json`, `parts/<name>.stl` (binary STL, one closed manifold each) and
  `report.json`.
- `DATA_DIR` holds the supplied parts: `main_plate`, `dial_plate`, `barrel_arbor`, `minute_wheel` and
  `minute_post`, as STL.
- `DETAILS.json` gets the per-step results under `steps`, `at` (AT-0 to AT-6), `details.sequence`,
  `grader_version` and `constants_hash`.

**From Python:**

```python
import grade as G                 # spikes/keyless/grade.py
spec, parts, sup, defs = G.load(sub_dir, data_dir)          # parts: {name: manifold3d.Manifold}
product, gates, conds, steps, det = G.grade(sub_dir, data_dir, jobs=3)
# lower level:
w = G.make_world(parts, sup, defs)                          # engine.World
w.settle(); w.step("stem", dq=radians, dp=mm)               # one rig step; False if blocked
```

**What the engine needs** is a list of `engine.Body` objects, one per mobile and one for all the fixed
parts:

- **The mesh:** a single `manifold3d.Manifold`, the union of the mobile's parts.
- **The kind:** `fixed`, `driven` (the stem), `contact` (a free mobile), `spring` or `main` (the barrel).
- **The degree of freedom:** `rot` about (point, direction), or `slide` along a direction. The stem is
  driven, so it both turns and slides.
- **For springs:** the rest side (`+inf` or `-inf`).
- **Optionally a carrier:** the name of the body whose rotation it shares (a sliding pinion on the stem).

**Adapter for B's STEP parts.** It needs no change to the engine:

1. Tessellate each STEP part with `geometry/core.py`, as B's grader already does.
2. Turn each mesh into a `manifold3d.Manifold`, as `grade.to_manifold` does for STL triangles.
3. Build the `defs` list from B's movement JSON plus the keyless section of it. The fields are the
   ones `keyless.json` uses now: kind, dof, point, direction, rest, on_stem.
4. Hand B's going-train parts in as `fixed`, or as one `contact` body per mobile if the going train
   should turn while winding. Fixed is enough for the keyless steps.

The adapter's output is `parts` (`name -> Manifold`), `sup` (B's plates and arbor as Manifolds) and
`defs`. These are exactly what `grade.make_world` takes.

## 2. Fixed interface in B's frame

Proposed below; B to confirm. Units are mm, in B's frame.

- **Barrel:** axis x = 0, y = 0; barrel wheel z 0 to 1.0; arbor z -1.0 to 1.6, radius 0.5
  (`geometry/watch.py`).
- **Case:** radius 20.7, height 13.4 (`geometry/watch.py`).
- **Stem line:** along +x at y = 0 (3 o'clock), z = -3.0, below the barrel wheel, on the dial side of
  the main plate. The crown sits outside the case radius, at x from about 21.2 to 23.0. Position 2 is
  the stem pulled 0.9 × (B's scale factor) towards +x.
- **Arbor square:** the arbor gets a square of side 0.8 from z -1.0 to -0.4. The keyless ratchet wheel
  sits on it, below the barrel wheel. The click and the ratchet live in z -1.0 to -0.2.
- **Keyless side:** the winding and setting works live between the main plate's dial side and the dial
  (z below the main plate). The crown wheel and ratchet are on the barrel side. The setting train
  reaches the motion work: B's minute wheel or its stand-in (B to name the part).
- **Volume B's going train must leave free:**
  - a box x 12 to 21.2, y -3.5 to +3.5, z -4.5 to -1.5, for the stem, the sliding and winding
    pinions, and the setting lever path;
  - a cylinder of radius 4.0 about the barrel axis, z -1.0 to -0.2, for the ratchet and click.

  These are first estimates at 1:1 of the current keyless reference times 1.6. They need one fitting
  pass against B's reference.

## 3. Acceptance steps without in-order gating

itswinther's rule applies: each step is graded on its own, plus a whole-build term. Numbers are from
`constants.py` (grader `keyless-acceptance-1.0`):

| Step | Passes when | Weight in v1 |
| --- | --- | --- |
| AT-0 Assemble | loads; no overlap over 2e-4 mm³ at rest; every free or spring mobile held (0.3 shift hits something); inside the case; stem ≥ 0.5 outside | 0.20 |
| AT-1 Wind | 1 crown turn forward in position 1: never blocked; 3 to 12 crown turns per barrel turn; minute wheel ≤ 1° | 0.15 |
| AT-2 Hold | crown let go for 40 steps, with taps every 5 steps (free parts moved up to 0.05): barrel arbor runs back ≤ 30° | 0.15 |
| AT-3 Run | (6 turns − run-back) × 8 h ≥ 38 h, and the arbor turned forward alone by 20° in 0.5° steps is never blocked | 0.20 |
| AT-4 Backward | 360° backward in position 1: never blocked; arbor between -4° and +1°; minute ≤ 1° | 0.10 |
| AT-5 Set | pull to position 2 with 5 stops and ±24° test turns (never blocked, never both trains; winds at 0, sets at the end); then ±90°: minute ≥ 5° each way; arbor loses ≤ 4° | 0.12 |
| AT-6 Return | push back with the same stops and rules; then 90° forward winds > 1° | 0.08 |

**Without gating:**

- Each step's pass or fail is already computed on its own: the grader evaluates every step for the
  honesty check.
- AT-4, AT-5 and AT-6 start from the state after AT-2.
- The whole-build term is the in-order score (weights summed until the first failure). In v1, AT-0
  also counts only together with AT-1.

## 4. Solid main-plate regions the keyless reference needs

The keyless reference fixes these parts to the plates. B's bar-skeleton plate must keep material
there, or offer an equivalent post. Extents are from the current reference, ×1.6 for B's scale:

| Part | Extent now (keyless frame) | Purpose |
| --- | --- | --- |
| Stem bridge | box 0.4 × 1.6 × 2.4, at the stem's inner end | holds the winding pinion axially |
| Stem guide | box 0.55 × 1.2 × 1.6, at the case wall | guides the stem |
| Crown-wheel post | Ø 0.66, 1.2 long, with a head Ø 1.2 | crown wheel pivot |
| Click post | Ø 0.4, 0.8 long, with a head Ø 0.8 | click pivot |
| Setting-wheel post | Ø 0.66, 1.2 long, on the dial side | setting wheel pivot |

## Scale conflict

- **Today:** B's watch is at about 1.6× (demo scale). Keyless v1 is Ø 17.4 in plan, close to real size,
  but its modules (0.15 to 0.2) and depth are about 1.5 to 2× real. Joined as a fifth part, keyless
  must use B's frame and scale.
- **Cost of moving the keyless reference into B's frame:** about half a day.
  - **Constants:** scale every length in `constants.py` and `supplied.py`, and the reference
    dimensions, by B's factor. Move the axes to B's frame (stem line, barrel at the origin, B's
    minute wheel or a stand-in). Recompute the case and keep-out volumes.
  - **Engine tolerances that scale:** 2e-4 mm³ scales by the factor cubed. The step-travel limit (0.06),
    the scan step (0.002), the tap (0.05), the hold shift (0.3) and the pull (0.9) scale linearly.
    Angles and friction do not change.
  - **Validation:** regrade the reference (about 10 min in Docker) and rerun the anchors (about 1 h on
    4 containers).
- **Risk:** a tighter fit of the setting train around B's motion work, which isn't modelled in the
  keyless frame yet.
- **Decision 14:45:** one scale for the whole job, B's demonstration scale (about 1.6×); "v2 at 1:1" is
  cancelled. Keyless v1's standalone runs keep their current geometry as a test bed.
- **What v2 at B's scale needs:**
  - a single scale constant shared with `geometry/watch.py`, applied to every length in the keyless
    constants, the supplied parts and the reference (volumes by its cube);
  - the axes moved to B's frame (section 2);
  - the datasheet values (DS-*) scaled the same way where they are lengths, with forces, torques and
    stresses converted consistently and stated as such in the brief;
  - the reference regraded and the anchors rerun at that scale.
