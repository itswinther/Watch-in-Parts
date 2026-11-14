# Rules for the watch movement

Units are millimetres. Positions are points in the plane of the plate; height is given as a
layer number. Everything below is checked exactly by a separate program.

## The plate and fixed parts (instance.json)

- The plate is a circle of `plate_radius` around (0, 0).
- The centre, fourth and escape arbors are fixed at `fixed_arbors`.
- The escape wheel (radius and teeth in `escape_wheel`) sits on the escape arbor.
- The balance is a disc at `balance.centre` with radius `balance.radius`.

## Gears

- Whole number of teeth; module from 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15.
- Pinions (names ending in `pinion`) have 7 to 16 teeth, the barrel wheel 40 to 140, every
  other wheel 30 to 140.
- Outer radius = module x (teeth + 2) / 2.
- Two meshing gears have the same module, are on the same layer, and their arbors are exactly
  module x (teeth1 + teeth2) / 2 apart (tolerance 0.005).

## Sides and layers

- The movement has sides, each with its own layers. Gears on the same arbor and side must be
  on different layers. Two gears on the same side and layer that do not mesh with each other
  must be at least 0.10 apart (centre distance >= sum of outer radii + 0.10).
- Train side, between the plates: layers 0 to 7, key `level`. The barrel wheel is thick and
  occupies its layer and the one above. The escape wheel's layer is `escape_wheel_level`; it
  must differ from the escape pinion's layer and counts as a gear on that layer.

## Space

- Every gear stays inside the plate: distance of its centre from (0, 0) + outer radius
  <= plate_radius - 0.30.
- Every arbor centre stays at least 1.0 inside the plate edge; no two arbors closer than 0.5.
- Arbors run through every layer of the sides listed for them below. A gear must stay 0.25
  clear of every such arbor (centre distance >= outer radius + 0.25), except its own arbor and
  the arbor of the gear it meshes with.
  - train side: barrel, centre, third, fourth, escape arbors
- Every train-side gear stays clear of the balance: centre distance >= outer radius +
  balance radius + 0.10.

## Rates (exact fractions)

- The centre arbor carries the minute hand: one turn per hour.
- The fourth arbor carries the seconds hand: exactly 60 turns per centre turn.
- The escape wheel has 15 teeth and two beats per tooth: it turns exactly
  beats_per_hour / 30 times per hour.
- The mainspring barrel makes 6.5 turns while running down. Power reserve in hours is
  6.5 x barrel_wheel teeth / centre_pinion teeth, and must be at least `power_reserve_target_h`.
- Torque: barrel_wheel teeth / centre_pinion teeth must not exceed `max_barrel_ratio`, or too
  little torque reaches the escapement to keep the balance swinging.

## Going train (power from the barrel to the escapement)

| Arbor | Position | Gears on it, train side |
|---|---|---|
| barrel | you choose | barrel_wheel |
| centre | fixed | centre_pinion, centre_wheel |
| third | you choose | third_pinion, third_wheel |
| fourth | fixed | fourth_pinion, fourth_wheel |
| escape | fixed | escape_pinion (and the given escape wheel) |

Meshes: barrel_wheel-centre_pinion, centre_wheel-third_pinion, third_wheel-fourth_pinion,
fourth_wheel-escape_pinion.

## Added in step 2: motion work (hour hand), dial side

- Dial side, under the dial: layers 0 to 2, key `dial_level`. Arbors on the dial side:
  centre, minute, fourth.
- cannon_pinion and hour_wheel on the centre arbor; minute_wheel and minute_pinion on a
  `minute` arbor you place.
- Meshes: cannon_pinion-minute_wheel, minute_pinion-hour_wheel.
- The hour wheel turns exactly 1/12 per centre turn.
- Dial-side gears do not need to clear the balance.

## Added in step 3: a larger balance

- The client has chosen a larger balance. From this step on, the balance radius is
  `balance.radius_after_change` instead of `balance.radius`. Its centre does not move.

## Added in step 4: date wheel, dial side

- A date_wheel on a `date` arbor you place, on the dial side, meshing with the hour_wheel.
- It turns exactly once per 24 hours (1/24 per centre turn).
- The date arbor joins the dial side's arbors.

## Added in step 5: automatic winding, wind side

- Wind side, on the back of the movement: layers 0 to 2, key `wind_level`. A rotor swings
  with the wearer's wrist and turns rotor_pinion on the centre arbor. Its motion must reach
  ratchet_wheel on the barrel arbor through two intermediate arbors you place, `wind1` and
  `wind2`.
- Gears: rotor_pinion (centre), wind1_wheel and wind1_pinion (wind1), wind2_wheel and
  wind2_pinion (wind2), ratchet_wheel (barrel).
- Meshes: rotor_pinion-wind1_wheel, wind1_pinion-wind2_wheel, wind2_pinion-ratchet_wheel.
- The rotor must turn between `winding_rotor_turns_per_barrel_turn[0]` and `[1]` times per
  barrel turn (inclusive). Too few and the rotor's small torque cannot wind the mainspring;
  too many and winding is too slow.
- Arbors on the wind side: barrel, centre, third, fourth, escape, wind1, wind2. Wind-side
  gears must also stay clear of the (larger) balance, which reaches through to the back.

## design.json

```json
{
  "arbors": {"barrel": [x, y], "third": [x, y]},
  "gears": {
    "barrel_wheel": {"teeth": 70, "module": 0.10, "level": 0},
    "...": "one entry per gear, with level / dial_level / wind_level for its side"
  },
  "escape_wheel_level": 3
}
```

Add `minute` (from step 2), `date` (from step 4) and `wind1`, `wind2` (from step 5) to
`arbors`. Gear names are exactly as in the rules.

## Score for each step

A design that breaks any rule in force at that step scores 0. A valid one scores
0.5 x (its power reserve / a reference movement's, capped at 1)
+ 0.5 x (the reference's layer count / yours, capped at 1).
Layer count is the number of distinct layers used, summed over all sides (the barrel wheel
counts both of its layers; the escape wheel's layer counts). Every step is scored, and the
task score is the mean over the five steps.
