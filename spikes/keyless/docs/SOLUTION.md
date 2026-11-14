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
- **Springs.** Spring bodies yield first. They return towards rest until contact, at most 0.25 mm of
  surface travel per step, and never push.
- **Mainspring.** After every step the mainspring tries to turn the arbor back by up to 0.02 mm of
  surface travel at its largest radius, and pushes the train.
- **Step splitting.** Any step in which some body's surface travels more than 0.06 mm is split in halves
  (up to 4 times), so the friction rule always sees steps small compared with the features.
- **Clearing search.** The search for the clearing position samples every 0.002 mm of surface travel,
  so it cannot jump over a few microns of gear backlash.
- **Crown let go (AT-2).** The stem becomes a pushed body, and answers for the parts riding on it.

## Why the steps carry these weights

| Step | Weight | Why it matters to the owner |
| --- | --- | --- |
| AT-0 Assemble | 0.20 | Earned only with AT-1. Without a movement that holds together nothing else matters, but parts that only fit together are not a mechanism. |
| AT-1 Wind | 0.15 | The basic function. |
| AT-2 Hold | 0.15 | A watch that unwinds when let go is useless. |
| AT-3 Run | 0.20 | The watch must actually run its reserve; winding works that brake the barrel stop the watch. |
| AT-4 Backward | 0.10 | Protects against misuse. |
| AT-5 Set | 0.12 | The second function of the crown. |
| AT-6 Return | 0.08 | Usually follows when AT-5 works. |

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
| 4 Backward | 360° backward: never blocked; arbor between -4° and +1°; minute ≤ 1° | -0.3° (old slip test) |
| 5 Set | 5 stops during the pull, ±15° test turns: never blocked, never both trains; ends in the right mode; then ±90°: minute ≥ 5° each way, arbor loses ≤ 4° | minute ±19.2° per 180° (old) |
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
