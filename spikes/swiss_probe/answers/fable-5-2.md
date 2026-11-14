# Swiss-lathe program for the watch arbor

The approach: turn the whole front profile in one pass with T02, pick the part up on the Ø0.80 shoulder before stickout exceeds 3.0, then form the rear pivot and cut off with T03 while the sub-spindle supports the part. Nothing here has been run or simulated; it is reasoned from the machine description.

## Conventions and assumptions

- **Z to part coordinate:** the tool point cuts at part z = Z − 0.5, so to cut at part position z, program Z = z + 0.5.
- **T03 reference edge (assumption):** the blade's bushing-side edge is the tool point, so the blade covers part z from Z − 1.0 to Z − 0.5. If your T03 is set on the part-side edge instead, subtract 0.5 from the three T03 Z values.
- **Z2 (assumption):** distance from the bushing face to the sub-collet face. `Z2=` in the same block as Z means both axes move together; on a two-path control these go in path 2 with wait codes.
- **Start condition:** the bar end was left by the previous cut-off at the tool plane, so Z = 0.5.
- **Nose radius:** all moves are axis-parallel and T02 is touched off in X and Z, so no radius compensation is needed. Internal corners get an R0.02 fillet.

## 1. Operations and why in this order

1. **T02 turns the front pivot Ø0.30 (z 0–0.8) in one pass from Ø2.0.** The cut is 0.5 mm from the bushing with full Ø2.0 stock behind it. It goes first because it is at the front, and on a sliding-head machine material is cut in the order it leaves the bushing.
2. **T02 faces out to Ø0.80 and turns the shoulder only to z = 2.5 (Z3.0).** That is the 3.0 stickout limit, so unsupported cutting stops here.
3. **Sub-spindle pick-up on the Ø0.80 shoulder.** The tool retracts in X only, M77 synchronises, the open collet slides over the part to z = 2.0 and M10 clamps.
   - The Ø0.30 pivot cannot be gripped (minimum 0.6); it sits inside the collet relief.
   - The grip is 1.2 mm long on Ø0.80 (z 0.8–2.0).
4. **T02 returns to exactly X0.80 at the same Z and finishes the profile, Z and Z2 moving together.** This covers the shoulder to z 3.8, the Ø1.00 seat to 4.4 and the Ø1.60 blank to 5.65 (0.05 overrun so T03 cleans the rear face).
5. **T03 forms the rear pivot with two overlapping plunges to Ø0.30** (blade at z 5.6–6.1, then 5.9–6.4). Plunging avoids side-loading a 0.5 mm blade. I stop T02 at 5.65 and do not pre-turn this zone, so the bushing still holds full Ø2.0 right behind the blade.
6. **T03 cuts off at z = 6.4** (blade at 6.4–6.9), with the part held by the synchronised sub-spindle so it does not drop or twist off.
7. **Sub-spindle retracts, sync off, part ejected, Z reset** (6.9 mm of bar used per part).

Z never decreases once cutting starts, so no reduced diameter is ever pulled back into the bushing. This is why every diameter is finished in a single pass and T01 is not used: a rough-then-finish sequence would need a retract and would finish on an unsupported neck.

T21 is deliberately not used for size. With the part held at z 0.8–2.0, I calculate the compliance at the rear pivot tip as about 0.0077 mm/N (the 1.8 mm of free Ø0.80 contributes 0.0053, the pivot itself 0.0020). A radial finishing force of 0.3 N (my estimate) would then give about 4.6 µm error on diameter, outside ±0.003. Cutting the rear pivot at the bushing avoids this.

## 2. Program

```
O0001 (WATCH ARBOR - BAR D2.0)
N10  G50 S10000              (SPEED LIMIT)
N20  G97 S10000 M03          (FIXED RPM; G96 WOULD ONLY SIT ON THE LIMIT)
N30  M11                     (SUB COLLET OPEN)
N40  T0202                   (FINISH TOOL R0.02)
N50  G00 X2.4 Z0.3           (FULL BAR BACK 0.2: END BEHIND TOOL PLANE)
N60  G00 X0.30
N70  G01 Z1.3 F0.005         (FRONT PIVOT D0.30, z 0-0.8)
N80  G01 X0.80 F0.004        (FACE AT z 0.8)
N90  G01 Z3.0 F0.008         (SHOULDER D0.80 TO z 2.5 - STICKOUT 3.0)
N100 G00 X20.0               (X ONLY, CLEAR OF SUB NOSE - Z STAYS)
N110 M77                     (SUB SYNCHRONISED WITH MAIN)
N120 G00 X2=0 Z2=3.5         (SUB ON CENTRE, 0.5 OFF BAR END)
N130 G01 Z2=1.0 F0.05        (COLLET FACE AT PART z 2.0)
N140 M10                     (CLAMP ON D0.80, z 0.8-2.0)
N150 G00 X1.0
N160 G01 X0.80 F0.004        (BACK TO SIZE, SAME Z)
N170 G01 Z4.3 Z2=2.3 F0.008  (SHOULDER TO z 3.8)
N180 G01 X1.00 F0.004        (FACE AT z 3.8)
N190 G01 Z4.9 Z2=2.9 F0.008  (WHEEL SEAT D1.00 TO z 4.4)
N200 G01 X1.60 F0.004        (FACE AT z 4.4)
N210 G01 Z6.15 Z2=4.15 F0.008 (PINION BLANK D1.60 TO z 5.65)
N220 G00 X2.4
N230 T0303                   (PARTING TOOL W0.5)
N240 G01 Z6.6 Z2=4.6 F0.2    (BLADE AT z 5.6-6.1)
N250 G01 X0.30 F0.003        (REAR FACE z 5.6 + PIVOT D0.30)
N260 G00 X2.4
N270 G01 Z6.9 Z2=4.9 F0.2    (BLADE AT z 5.9-6.4)
N280 G01 X0.30 F0.003        (PIVOT D0.30 TO z 6.4)
N290 G00 X2.4
N300 G01 Z7.4 Z2=5.4 F0.2    (BLADE AT z 6.4-6.9)
N310 G01 X0.30 F0.004
N320 G01 X-0.04 F0.002       (CUT OFF, PART LENGTH 6.40)
N330 G00 Z2=30.0             (SUB AWAY WITH PART)
N340 G00 X20.0
N350 M78                     (SYNC OFF)
N360 M11                     (RELEASE / EJECT PART)
N370 M05
N380 G50 Z0.5                (NEW BAR END IS AT TOOL PLANE: FREE LENGTH 0.5)
N390 M30
```

## 3. Limit checks, step by step

| Blocks | Z (= stickout) | Sub gripping + sync? | Limit | Material between bushing and tool |
|---|---|---|---|---|
| N50–N80 | 0.3 → 1.3 | no | 3.0 ✓ | Ø2.0 |
| N90 | 3.0 | no | 3.0 ✓ (at the limit) | Ø2.0 |
| N100–N140 | 3.0, no cutting | clamps at N140 | ✓ | — |
| N160–N210 | 3.0 → 6.15 | yes | 12.0 ✓ | Ø2.0 |
| N240–N280 | 6.6, 6.9 | yes | 12.0 ✓ | Ø2.0 |
| N300–N320 | 7.4 (maximum) | yes | 12.0 ✓ | Ø2.0 |

- **Order of support:** M77 (N110) and M10 (N140) both come before the first block with Z > 3.0 (N170). M78 and M11 come only after the part is severed (N320).
- **Grip diameter:** Ø0.80, inside the 0.6–2.0 range. The grip zone z 0.8–2.0 was fully turned in N90 (to z 2.5).
- **Collet clearance:** the collet face stays at part z 2.0 throughout (Z2 = Z − 2.0 in every block), 0.5 mm from the tool plane at pick-up with the tool retracted.
- **Speed:** 10,000 rpm on both spindles, which is the limit. That gives 62.8 m/min at Ø2.0 and 9.4 m/min at Ø0.30.
- **Deflection at the cut:** Ø2.0 stock 0.5 mm from the bushing gives δ/F = 0.5³ / (3 · 210,000 · 0.785) ≈ 2.5 × 10⁻⁷ mm/N. Even at my estimated 20 N for the full-depth pivot cut that is about 0.005 µm, negligible against ±3 µm.
- **Geometry (Z − 0.5):**
  - T02 faces: Z1.3 → z 0.8, Z4.3 → z 3.8, Z4.9 → z 4.4.
  - T03 part-side edge (Z − 1.0): Z6.6 → z 5.6, Z7.4 → z 6.4.
  - Diameters: 0.30 / 0.80 / 1.00 / 1.60 / 0.30.

Things to verify on the first part:

- **Pick-up mark:** look for a witness line at z 2.5 where the cut was interrupted for the pick-up.
- **Rear pivot:** check for a step at z 5.9–6.1 between the two plunges. This needs a T03 edge ground flat and parallel to the axis. If your blade has a lead angle, leave 0.04 on the rear pivot and finish it with T21 after re-gripping close to the Ø1.00 seat.
- **Offsets:** adjust the T02 and T03 wear offsets against the ±0.003 measurements.
