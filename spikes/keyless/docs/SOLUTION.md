<!-- NOT-FOR-AGENT: correct answers, acceptable ranges, the rig's numerical model and every anchor's score. Never copied into the agent image. -->
# Keyless works: answers, ranges and anchor scores

Numbers come from `../constants.py` and `../engine.py` (grader version `keyless-acceptance-1.0`). Every
run was in Docker (image from `../docker/Dockerfile`).

## The rig's numerical model (for judges)

The brief describes the test rig physically: rigid parts, dry friction with a cited coefficient, light
springs, a strong mainspring, and crown steps. The grader implements that as follows:

- **Overlap.** Each pair of bodies may overlap by at most 2e-4 mm³. Fixed-fixed pairs are not checked.
- **Pushing.** A pushed body moves the least distance along its own degree of freedom that clears its
  overlap with the bodies that moved in the step. It may give way by at most K = 1/μ times the relative
  surface travel at each contact patch's centre, measured at that centre. μ = 0.51 is the static
  coefficient, brass on steel, clean and dry
  ([Engineering ToolBox](https://engineeringtoolbox.com/friction-coefficients-d_778.html), and the same
  figures in the [NASA fastener reference](https://ntrs.nasa.gov/api/citations/19930087851/downloads/19930087851.pdf)).
  The sliding value 0.44 is stated in the brief, but the static value decides lock or slip, because a
  pawl or tooth starts each push at rest. So K = 1.96, and a face inclined more steeply than about 63°
  to the pushed body's motion locks.
- **One threshold.** Touching is overlap ≤ 2e-4 mm³ everywhere. A push aims for half of that (a margin)
  but accepts the nearest position ≤ 2e-4 when that is all it can reach, so a part resting on a face
  (coplanar faces give about 1e-4 after tessellation) can still be pushed along it.
- **Fits.** At load, every empty bore coaxial with a turning mobile's declared axis (rot mobiles, the
  stem, the barrel arbor), in that mobile's parts and in every part it turns in, is widened by
  `FIT_CLEARANCE` = 0.005 mm radially, in 12 slabs along the axis. CAD fits are drawn line to line and
  overlap by the chord sag once tessellated; real pivots run 5 to 15 µm.
- **Springs.** Spring bodies yield first, if they can clear everything they touch within the friction
  rule, and only in the direction the contact pushes them (the sign that lowers the overlap, i.e. the
  sign of the contact's moment about a rot body's axis). A click whose reaction pulls it in goes deeper
  and seats; it cannot hop out the other way. If they cannot, a pushed spring body passes the push on like a rigid link: it clears the bodies
  that pushed it, and what it runs into is resolved next. Between steps, springs return towards rest, at
  most 0.25 mm of surface travel per step. After contact they push on, 0.01 mm at a time, any free or
  spring body in their way, with the others resolving as in a step. They never push a fixed body, the
  driven stem or the mainspring arbor, nor another spring away from its own rest side. This is what lets
  a yoke spring return the sliding pinion through the yoke.
- **Carriers.** A mobile may ride on the stem (`on_stem`, slide) or on another rot mobile (`carrier`: a
  wheel on a swinging lever). Its pose is the carrier's rotation composed with its own coordinate. A
  pushed carrier answers for its riders' contacts. A carrier's slide (the stem's pull) does not move its
  riders, so on a pure pull step they are not counted as moved. A free rider of a carrier that turned in
  this step yields first, like a spring (a sliding pinion riding up symmetric or Breguet ramps). If the
  step then cannot be resolved, the step is re-resolved with riders treated as ordinary pushed parts: a
  rider whose chain behind it is held (ml01's sliding pinion, backed by the yoke, the yoke by the
  setting lever in position 2) drives instead of giving way.
- **Rest and start.** Before AT-0's rest check and at the start of every phase, the rig clears each
  mobile's overlaps within 0.3 mm of surface travel. It turns still-overlapping wheels as drivers with
  the train resolving, so wheels drawn tooth through tooth are phased. Then it lets the springs return
  until nothing moves (up to 40 rounds).
- **Position 2.** The design may declare `pull` from 0.4 to 1.0 mm (Sellita SW200 0.80, Marco Lang
  ml01 about 0.49); default 0.9.
- **Taps (AT-2).** Every 5 steps while the crown is let go, every free (contact) body moves up to 0.05 mm
  of surface travel in the direction it can move furthest without overlap. Sprung parts return; free
  parts stay where the tap left them.
- **Mainspring.** After every step the mainspring tries to turn the arbor back by up to 0.02 mm of
  surface travel at its largest radius, and pushes the train.
- **Step splitting.** Any step in which some body's surface travels more than 0.06 mm is split in halves
  (up to 4 times), so the friction rule always sees steps small compared with the features.
- **Clearing search.** The search for the clearing position samples every 0.002 mm of surface travel,
  so it cannot jump over a few microns of gear backlash.
- **Crown let go (AT-2).** The stem becomes a pushed body, and answers for the parts riding on it.

## Realism comparison: real keyless tooth counts (never in the brief)

Grossmann, *Lessons in Horology* (1905), art. 168–169, gives a real keyless works with these counts:
sliding pinion 16, setting wheels 27 and 18, minute wheel 30, cannon pinion 12, ratchet 44, crown wheel
42, winding pinion 18. Our reference uses:

| Part | Grossmann (1905) | Reference |
| --- | --- | --- |
| winding pinion | 18 | 12 (involute, module 0.15) |
| crown wheel | 42 | 36 face teeth, plus a 12-tooth spur pinion |
| ratchet | 44 | barrel wheel 36 and a ratchet ring of 24 |
| sliding pinion | 16 | 8 Breguet teeth and 12 spur teeth |
| setting wheels | 27 and 18 | one setting wheel: 36 face teeth, 12-tooth pinion |
| minute wheel | 30 | supplied stand-in, 36 |

The reference is coarser (fewer, larger teeth), as suits the demonstration scale and the simulation's
tolerances. Its ratios, 9 crown turns per arbor turn, are within the 3 to 12 band.

The datasheets' cannon-pinion slip torque (Rolex, US11256216B2) is a realism fact only; the grader does not
use it. In the joined job a `friction_on` mobile is a free contact body and the going train is one fixed
body (SESSION.md, Decisions 16:00).

## Harness fairness

- **Output cap.** The agent image sets `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=64000`. OpenCode's default
  cap is 32,000 output tokens per response, and Anthropic's "max" thinking variant can spend 31,999 of
  them on thinking. Haiku 5.5 once ended a turn empty that way. With the higher cap, no turn can end
  empty because of the output cap.
- **Agent timeout.** 90 min (5,400 s), from the 3× rule: about three times the slowest run seen (the GPT
  prelim, 29 min) and at least 60 min. Every trial log is checked so that no run was cut off by it.

## Scoring and why the steps carry these weights

There is no in-order gating (decision of 14 Nov 14:45). Each step is judged on its own:

- **Product** = 0.5 × (sum of the weights of the steps that pass) + 0.5 × (1 if every step passes).
- **Headline reward** = product × (0.75 + 0.10 × honesty) / 0.85.

So that a mechanism that does nothing cannot collect the passive steps, each step's own test includes
the capability it protects:

- AT-2 starts from an arbor the rig has wound itself.
- AT-3 and AT-4 each end with a forward crown turn that must still wind.
- AT-5 and AT-6 require winding at position 1.

| Step | Weight | Why it matters to the owner |
| --- | --- | --- |
| AT-0 Assemble | 0.05 | It must hold together, but fitting parts are not yet a mechanism. |
| AT-1 Wind | 0.20 | The basic function. |
| AT-2 Hold | 0.15 | A watch that unwinds when let go is useless. |
| AT-3 Run | 0.20 | The watch must run its reserve; winding works that brake the barrel stop it. |
| AT-4 Backward | 0.12 | Protects against misuse. |
| AT-5 Set | 0.18 | The second function of the crown. |
| AT-6 Return | 0.10 | Back to winding after setting. |

### Does "do everything" stay clearly best?

The product is 0.5 × (sum of the weights passed) + 0.5 × (1 if every step passes): B's formula for the
joined watch job, agreed on 14 Nov at 14:45. The reference scores 1.0. Skipping one step loses half that
step's weight plus the whole-build 0.5:

| Step skipped | Score |
| --- | --- |
| AT-5 Set (likely the hardest for a model) | 0.41 |
| AT-2 Hold | 0.425 |
| AT-1 Wind or AT-3 Run | 0.40 |
| AT-4 Backward | 0.44 |
| AT-6 Return | 0.45 |
| AT-0 Assemble | 0.475 |

This answers the mentor's concern that skipping the hardest part could still earn about 0.75. With a
whole-build share of 0.5, any single skipped step costs more than half the score, so "do everything" is
clearly best. The anchor "skip the hardest step" (the reference without its setting train) measures
this on a real design.

## Acceptable range for every check (acceptance scoring)

| Step or condition | Requirement | Reference achieves |
| --- | --- | --- |
| files (gate) | JSON and STL load; names valid; no symlinks; closed manifolds | yes |
| rest (gate) | every pair overlaps ≤ 2e-4 mm³ at rest | worst 5.8e-5 |
| held (×0.5 if failed) | every free or spring mobile shifted 0.3 hits something | all 5 |
| bounds (×0.5 if failed) | inside case r 8.7 and z ±3.4; stem ≥ 0.5 outside | stem 1.25 outside |
| 1 Wind | 1 forward turn: never blocked; arbor ≥ 2°; minute ≤ 1° | 39.7° per turn (old run) |
| 2 Hold | 40 steps let go: run-back ≤ 20° | TBD (new run) |
| 3 Run | stored turns × 8 h ≥ 0.75 h (capacity 6 turns); arbor turned forward 20° alone never blocked | about 0.88 h |
| 4 Backward | 360° backward: never blocked; arbor between -4° and +1°; minute ≤ 1°; then 90° forward winds > 1° | -0.3° (old slip test) |
| 5 Set | 5 stops during the pull, ±15° test turns: never blocked, never both trains; ends in the right mode; then ±90°: minute ≥ 2° each way, arbor loses ≤ 4° | minute ±19.2° per 180° (old) |
| 6 Return | the same stops, pushing back; then 90° forward winds > 1° | TBD |

Implied design range:

- **Winding ratio.** The reserve of 0.75 h from one turn needs at most 10.7 stem turns per arbor
  turn. Step 1 needs at least 2° per turn, that is at most 180 turns. The reference uses 9.06.
- **Breguet faces.** The driving faces must be steeper than about 63° (atan 2), and the slipping
  faces gentler.

## Anchors and exploit attempts: old vs new scoring

Old scoring: weighted checks (wind 3, slip 3, set 3, sweep 3, click 2, held 1, bounds 1, out of 16).
Slip counts only with wind; click, held and bounds count only with 3 of the 4 behaviours.
New scoring: steps passed in order out of 6, times the condition factors.

TABLE_PLACEHOLDER
