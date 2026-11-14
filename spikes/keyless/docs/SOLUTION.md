<!-- NOT-FOR-AGENT: correct answers, acceptable ranges and what every anchor scores. Never copied into the agent image. -->
# Keyless works: answers, ranges and anchor scores

Numbers come from `../constants.py` and `../engine.py`. All runs were in Docker (image built from
`../docker/Dockerfile`).

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
