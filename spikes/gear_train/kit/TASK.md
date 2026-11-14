# Design the gear train of a mechanical watch

`instance.json` describes a watch movement: the main plate, three arbors whose positions
are already fixed, the escape wheel and the balance. Design the rest of the gearing and
write it to `design.json`. Work only inside this folder; Python 3 is available.

Units are millimetres. Angles do not matter; only positions in the plane and layer numbers.

## The movement

Going train (power flows barrel -> escapement), between the plates:

| Arbor | Position | Gears on it |
|---|---|---|
| barrel | you choose | barrel_wheel |
| centre | fixed at (0, 0) | centre_pinion, centre_wheel |
| third | you choose | third_pinion, third_wheel |
| fourth (seconds) | fixed | fourth_pinion, fourth_wheel |
| escape | fixed | escape_pinion, plus the escape wheel (given, not designed) |

Meshes: barrel_wheel–centre_pinion, centre_wheel–third_pinion, third_wheel–fourth_pinion,
fourth_wheel–escape_pinion.

Motion work, under the dial: cannon_pinion and hour_wheel on the centre arbor,
minute_wheel and minute_pinion on a minute arbor you place. Meshes: cannon_pinion–minute_wheel,
minute_pinion–hour_wheel.

## Required rates (exact, as fractions)

- The centre arbor carries the minute hand: one turn per hour.
- The fourth arbor carries the seconds hand: exactly 60 turns per centre turn.
- The escape wheel has 15 teeth and two beats per tooth, so it must turn exactly
  beats_per_hour / 30 times per hour.
- The hour wheel turns exactly 1/12 per centre turn.
- The barrel makes 6.5 turns while unwinding, so power reserve in hours is
  6.5 × barrel_wheel teeth / centre_pinion teeth. It must be at least `power_reserve_target_h`.

## Gear rules

- Every gear has a whole number of teeth and a module from:
  0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15.
- Pinions (names ending in `pinion`) have 7 to 16 teeth. The barrel wheel has 40 to 140.
  Every other wheel has 30 to 140.
- Two meshing gears have the same module, sit on the same layer, and their arbors are
  exactly module × (teeth1 + teeth2) / 2 apart (tolerance 0.005).
- A gear's outer radius is module × (teeth + 2) / 2.

## Layers

- Going-train gears sit on layers 0 to 7. The barrel wheel is thick: it occupies its layer
  and the one above. Motion-work gears sit on dial layers 0 to 2.
- Gears on the same arbor must be on different layers. The escape pinion and escape wheel
  must be on different layers.
- Two gears on the same layer that do not mesh with each other must be at least 0.10 apart
  (distance between centres ≥ sum of outer radii + 0.10). This includes the escape wheel.

## Space

- Every gear stays inside the plate: distance of its centre from (0, 0) plus its outer radius
  ≤ plate_radius − 0.30.
- Arbor centres stay at least 1.0 inside the plate edge, and no two arbors are closer than 0.5.
- Arbors run through every layer on their side. A going-train gear must stay 0.25 clear
  (centre distance ≥ outer radius + 0.25) of the barrel, centre, third, fourth and escape
  arbors; a motion-work gear must stay 0.25 clear of the centre, minute and fourth arbors.
  A gear does not need to clear its own arbor or the arbor of the gear it meshes with.
- Every going-train gear stays clear of the balance: centre distance ≥ outer radius +
  balance radius + 0.10.

## Output: design.json

```json
{
  "arbors": {"barrel": [x, y], "third": [x, y], "minute": [x, y]},
  "gears": {
    "barrel_wheel":  {"teeth": 70, "module": 0.10, "level": 0},
    "centre_pinion": {"teeth": 10, "module": 0.10, "level": 0},
    "...": "one entry for each of the 8 going-train gears, with level",
    "cannon_pinion": {"teeth": 10, "module": 0.08, "dial_level": 0},
    "...": "one entry for each of the 4 motion-work gears, with dial_level"
  },
  "escape_wheel_level": 3
}
```

The twelve gear names are: barrel_wheel, centre_pinion, centre_wheel, third_pinion,
third_wheel, fourth_pinion, fourth_wheel, escape_pinion, cannon_pinion, minute_wheel,
minute_pinion, hour_wheel.

## Score

A design that breaks any rule above scores 0. A valid design scores
0.5 × (its power reserve ÷ a reference movement's) + 0.5 × (the reference's layer count ÷ yours),
each part capped at 1. Layer count is the number of distinct going-train layers used
(the barrel counts both of its layers, plus the escape wheel's layer) plus the number of
distinct dial layers used. More reserve and fewer layers are better.

End by stating the power reserve and the layer count of your design.
