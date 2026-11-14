# Mechanical watch: idea write-up

Written 2026-11-14 03:30 Helsinki by Abhishek + Claude. Status: an idea, not a
proposal. Nothing here is built or run, and nothing changes `SPEC.md`. When this
was written the team's active challenge was Moving Day (SPEC 0.3); this file is
for the team to compare against it, or to keep as a fallback.

## Why this idea

H1 and H2 showed no gap: every clean agent scored 1.0 or close to it, in under
8 minutes. The likely reason is that the spec did the modelling for the agent.
Every body was a box with coordinates, the keep-outs were given as boxes, and
the tools measured every requirement. What was left was a fully stated numeric
puzzle, which models are good at.

The idea here is to describe a real product, not a design, and let the agent
infer what the product needs. A mechanical watch fits because its core rules are
strict and universal: the hour hand turns once in 12 hours, the minute hand once
an hour, the seconds hand once a minute, all clockwise, all on one centre.
Anyone who knows what a watch is knows this, so it can be graded exactly without
being stated.

How we got here: smartwatch case (realistic component meshes, wide real-world
ranges like case size and lug width) -> mechanical watch (exact ratios instead
of fuzzy ranges). The smartwatch case is the fallback if this proves too much
to build.

## The rule we must not break: no withheld information

The team's reading of the rubric (B, 02:05 entry in `SESSION.md`): a failure
caused by withheld information scores zero for meaningful difficulty. So every
graded requirement falls into one of three kinds:

| Kind | Example | Stated to the agent? |
| --- | --- | --- |
| Universal fact about the product | Hand ratios, clockwise, coaxial hands, fits on a wrist | No. The agent must infer it. |
| A number we chose | Barrel speed, smallest printable feature, collision tolerance | Yes, always. |
| File format | Part files, `movement.json` layout | Yes, always. |

Test for each hidden check: a skilled human watchmaker given the same inputs
would pass it reliably. A real watch must never fail a hidden check.

## Scope

A full movement cannot be graded in the time we have: whether an escapement
ticks, mainspring torque and friction need a physics simulation. So the task is
the gear train and hand works only. The barrel is the driver; there is no
escapement. The brief says so.

## What the agent gets (draft)

Brief:

> Design the gear train of a mechanical watch. The mainspring barrel is in
> `meshes/barrel.stl`; it turns clockwise (seen from the dial) once every 8
> hours. Drive the hour, minute and seconds hands from it. There is no
> escapement. The movement must fit in a wristwatch and be 3D-printable; the
> smallest printable feature is 0.2 mm.

Plus:

- `meshes/barrel.stl` (the barrel with its teeth, in a fixed pose).
- The file format: one STL per part (wheels, pinions, arbors, plates, bridges,
  three hands) and `movement.json` (below). Size caps per STL. Collision
  tolerance.
- Measuring tools (the existing kind: section, distance, interference, plus a
  rotation sweep, see "Tools"). Geometry facts only, never pass/fail.
- Python with `manifold3d`, `trimesh`, `numpy`, `scipy`.

`movement.json` (draft): which parts are fixed (plates, bridges); which parts
form each rotating unit ("mobile", e.g. wheel + pinion + arbor); each mobile's
axis (point and direction); the tooth count of each gear and which gears mesh;
which mobiles carry the hour, minute and seconds hands. Every claim in it is
checked against the geometry and never trusted.

## Harbor task layout

| File | Agent sees it? | Content |
| --- | --- | --- |
| `instruction.md` | yes | The brief and the file format |
| `environment/Dockerfile` | yes (its result) | Python, libraries, `meshes/`, tools |
| `tests/` | no | `test.sh` calls the grader, writes `/logs/verifier/reward.txt` |
| `solution/` | no | Reference movement and `solve.sh` for the `oracle` agent |
| `task.toml` | no | Time limits, network allowlist, artifacts, MCP tools |

## How the grader tests it

Not a physics simulator. No forces, no time integration. It is arithmetic
(tooth counts give exact speeds) plus geometry (place each part at its angle,
test for overlap), which is the same rigid-pose replay and overlap test the H1
grader already does with `manifold3d`, with rotations instead of slides.

1. Valid parts. Each STL is one closed manifold shell (H1 G1). Nothing overlaps
   in the assembled pose (H1 G3). `movement.json` parses and is consistent.
2. Free to spin. Each mobile rotated through a full turn about its declared axis
   in small steps never hits the fixed parts.
3. Held in bearings. Each mobile moved 0.3 sideways in four directions and
   along its axis both ways intersects a plate or bridge (same pattern as H1 F2,
   "board located"). Rotates freely, cannot move otherwise.
4. Speeds. From the barrel (1 turn per 8 h, clockwise), walk the declared mesh
   network: each external mesh reverses direction and multiplies speed by the
   tooth ratio. Exact fractions (`fractions.Fraction`), no rounding. External
   or internal mesh is read from the centre distance, not from the claim.
5. Timekeeping. Minute hand exactly 1 turn per hour, hour hand exactly 1 per
   12 h, seconds hand exactly 1 per minute, all clockwise, hand axes coincide
   within 0.01. No mobile driven at two conflicting speeds (a locked train).
6. Running simulation. Turn the whole train in small steps at the speeds from
   step 4 until every wheel has done at least one full turn. At every step:
   - no jam: meshing gears overlap by at most the tolerance;
   - engaged: the gap between meshing gears stays below a small limit;
   - teeth drive: turning the driver a fraction of a degree further while the
     driven gear is held makes them collide (rules out smooth friction discs and
     teeth that only nearly touch);
   - hands clear: hour, minute and seconds hands and the dial never touch.
7. Watch-sized and printable. Inside a wide wristwatch outline (hidden, from
   real products), and no feature thinner than the stated 0.2 (H1 W1 pattern).

Why declared tooth counts are safe: if a claimed count is wrong, the gears drift
out of phase as they turn, and within one revolution they are a whole tooth off
and collide in step 6. Counting teeth from the mesh (slice the gear, read the
radius around the circle, count the bumps) becomes an optional cross-check, not
something the grader depends on.

Score: same shape as H1. Gates (valid files, no overlap, readable
`movement.json`) give 0 if failed. Weighted checks for the rest (support,
meshing, each hand's ratio, hand clearance, size, printability). Headline is the
strict pass rate.

## Why it should be hard

- Choosing tooth counts that give exact ratios from 1 turn per 8 h to 1 turn per
  minute (a factor of 480, so several stages).
- The motion works: hour and minute hands share an axis, so the two gear pairs
  between them need equal centre distances and still give 12:1. A classic
  puzzle.
- Modelling gear teeth that actually mesh, not just discs of the right size.
- Packing all of it into about 40 mm across and a few mm thick, with bearings at
  both ends of every arbor.
- Nothing about the ratios, the hand order or the coaxial hands is stated.

Not verified: that any of this produces a gap. Lesson from H1 and H2: run a
clean agent within the first hour.

## Tools for the agent

The existing measuring tools plus a rotation sweep: "turn these mobiles at these
speeds for N steps, report the worst overlap and its step per pair". A geometry
fact, no pass/fail, same as H1 `sweep`.

## Not tested

Escapement function, mainspring torque, power reserve, friction, wear. The brief
must say the barrel is the driver and there is no escapement.

## Effort (estimates, one person with Claude)

| Piece | Estimate | Reuses |
| --- | --- | --- |
| Parse and validate `movement.json` | 1-2 h | contract checks pattern |
| Rotation replay | 2-3 h | pose replay, overlap |
| Speeds through the mesh network | 1-2 h | new, simple |
| Bearing and teeth-drive checks | 1-2 h | F2 pattern |
| Hand clearance | ~1 h | overlap |
| Size and printability | 1-2 h | W1 pattern |
| Reference movement | 4-8 h | `manifold3d`, new design |
| Anchors (wrong ratio, smooth disc, floating arbor, hands colliding, ...) | 2-3 h | anchor runner |
| Rotation sweep tool | 1-2 h | `sweep` |

About 1.5 to 2 days for one person, or one long day for two (grader on one side,
reference movement on the other). These are guesses.

## Risks

- The reference movement is the critical path. We must build a gear train that
  passes every check, which is the agent's own task. Involute teeth are about 50
  lines of `numpy`; open-source CadQuery gear generators exist but are unchecked.
- The "engaged" limit must pass real gears with normal backlash and fail gears
  that have drifted apart. Tuned on the reference.
- Grading time: about 10 mobiles x hundreds of steps x overlap tests. Probably
  seconds to a minute; unmeasured.
- The hidden size limits must come from real watches, checked against sources.
  The numbers we have are from general knowledge.

## Demo

A 3D viewer (three.js) that plays the train: the barrel turns, gears turn,
hands sweep, and a check list beside it goes green or red. A wrong tooth count
shows as teeth drifting apart and flashing red where they collide. Clear on
video, which a reward file is not.

Optional finding for the README: run the same task with a full requirements
sheet and with the minimal brief. If models pass with the sheet and fail with
the brief, that is a result: models can follow a spec but cannot yet turn a
product into one.

## Next steps, if the team wants it

1. Two-gear spike (1-2 h): two gears, rotation replay, jam, engaged and drive
   checks, plus a deliberately wrong tooth count to confirm step 6 catches it.
2. Write the brief and give it to two clean agents (as in B's attempts 5 and 6)
   before building the full grader.
3. Only then: reference movement, full grader, anchors, Harbor task.

## Open questions

- Can the agent see images? If yes, a rendered view of the barrel and an empty
  case could be part of the input.
- Barrel speed (8 h per turn) and the 0.2 printable feature are our choices; is
  a resin printer assumption acceptable?
- Is gear train only (no escapement) a credible "mechanical watch" to judges?
