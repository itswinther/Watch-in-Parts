# Swiss-type program for the watch arbor (Ø2.00 steel bar)

## 0. Conventions and assumptions

- **Z** is the headstock position, which equals the bar's stickout from the bushing face. T01 and T02 cut at part coordinate **z = Z − 0.5**, measured from the part's front end.
- **T03 (width 0.5).** Its reference edge is the bushing-side edge, which sits 0.5 from the bushing face. The blade extends 0.5 further out, so the kerf spans **z = Z − 1.0 to Z − 0.5**.
  - Parting at Z7.40 therefore cuts the kerf 6.40–6.90.
  - The new bar face is left at stickout 0.50, exactly where the next cycle starts. The previous part-off has already faced it.
  - A new bar needs a separate face/slug-off routine, not shown here.
- **Sub-spindle Z2 is written as B.** B is the distance from the bushing face to the sub-collet face. On a real control this is a separate axis letter or path 2 with superimposition.
  - X2 is parked on centreline.
  - While the sub grips, every Z move carries **B = Z − 1.8**, so the sub travels with the part.
- **Main-collet open/close for the re-chuck** is not among the codes given, so those lines are comments only.

## 1. Operations, in order, and why

The key constraint: without the sub, Z ≤ 3.0, so tools can only reach **z ≤ 2.5**. The rest of the part (z 2.5 to 6.9, including the kerf) needs Z up to 7.4. That is only allowed while the sub grips the part in sync.

The sub can grip only Ø0.6–2.0. That rules out both pivots (Ø0.30), so it must grip the **Ø0.80 shoulder**. That shoulder must therefore be finished *before* the grip, using only the reach available in phase A.

**Phase A: bushing support only (Z ≤ 3.0)**

1. **T01 rough** the front pivot to Ø0.36 (z 0–0.78) and the shoulder to Ø0.86 (z 0–2.50).
2. **T02 finish** the front pivot to Ø0.30 (z 0–0.80), face the shoulder at z = 0.80, then finish Ø0.80 to z = 2.49.
   - This is done now because the sub collet will cover z 0.8–1.8 afterwards.

**Phase B: hand-over**

3. Switch to constant rpm, **M77** sync, move the sub onto the part with the collet covering z 0.8–1.8 on Ø0.80, then **M10** clamp.
   - The pivot (z 0–0.8) sits free in the collet bore.
   - From here the stickout limit is 12.0.

**Phase C: gripped by the sub and synchronised (Z up to 7.4)**

4. **T01 rough**, three passes, each starting at z 2.48 so it overlaps the phase-A surface:
   - Ø1.66 to z 6.00
   - Ø1.06 to z 4.38
   - Ø0.86 to z 3.78
5. **T02 finish** in one forward pass: Ø0.80 to z 3.80, face, Ø1.00 to z 4.40, face, Ø1.60 to z 5.62.
   - The pass runs 0.02 past 5.60 into material that the groove removes next. This guarantees full Ø1.60 right up to the pinion's rear face.
6. **T03 forms the rear pivot.** It plunges kerfs 5.62–6.12 and 5.90–6.40 to Ø0.34, then does a finish plunge at kerf 5.60–6.10 to Ø0.30 (this makes the pinion rear face exactly at 5.60). Last, a side pass to kerf 5.90–6.40 at Ø0.30.
   - A turning tool cannot make this feature. The face at z 5.60 faces the bushing, which a turning tool feeding towards the bushing cannot generate.
7. **T03 parts off** at kerf 6.40–6.90, through centre to X−0.05.
8. **Unload and re-chuck:**
   - M78 sync off, then the sub withdraws with the part.
   - The blade stays at centre as a bar stop.
   - Open the main collet, move the headstock back to Z0.50 (bar-feeder pressure holds the bar against the blade), close the collet.
   - Retract T03 and eject the part from the sub.

**Why T21 (back-working) is not used for the rear pivot**

In the sub, the part would be held only on the Ø0.80 shoulder, with the collet face at z 1.8. The tool would act at about z 6.0. A cantilever estimate (E = 210,000 N/mm²) gives the compliance at the tool:

| Section | z range | I (mm⁴) | ∫(L−x)²dx / I |
|---|---|---|---|
| Ø0.80 | 1.8–3.8 | 0.0201 | 21.15 / 0.0201 ≈ 1052 |
| Ø1.00 | 3.8–4.4 | 0.0491 | 2.18 / 0.0491 ≈ 44 |
| Ø1.60 | 4.4–5.6 | 0.322 | 1.34 / 0.322 ≈ 4 |
| Ø0.30 | 5.6–6.0 | 3.98e-4 | 0.021 / 3.98e-4 ≈ 54 |

- The sum is about 1154, so δ ≈ 1154 / E ≈ **5.5 µm per N**.
- A light finishing radial force of about 0.5 N gives about 2.7 µm radial, or 5.5 µm on diameter.
- That is more than the ±0.003 tolerance.

On the main side, the pivot is cut 0.5 from the bushing, with the bar behind it and the sub in front. The worst case is a Ø0.30 core no more than 0.3 long to the Ø2 bar:

- EI = 83.5 N·mm², giving δ ≈ F·0.027 / (3·83.5) ≈ 0.1 µm per N, which is negligible.

## 2. Program

```
O1000 (WATCH ARBOR - Z = STICKOUT, PART z = Z-0.5 FOR T01/T02)
(CYCLE START: BAR FACE AT STICKOUT 0.50, MAIN COLLET CLOSED, SUB OPEN AND CLEAR)
(=========== PHASE A : BUSHING ONLY, Z <= 3.00 ===========)
G50 S10000                    (SPINDLE CAP)
T0101                         (T01 TURNING - ROUGH)
G96 S60 M03                   (60 M/MIN: 9549 RPM AT D2, CAPPED 10000 BELOW D1.91)
G00 X2.20 Z0.40               (TOOL 0.10 AHEAD OF BAR FACE)
G00 X1.40
G01 Z3.00 F0.02               (z 2.50, STICKOUT 3.00 = LIMIT)
G00 X2.20
G00 Z0.40
G00 X0.86
G01 Z3.00                     (SHOULDER ROUGH D0.86 TO z 2.50)
G00 X2.20
G00 Z0.40
G00 X0.36
G01 Z1.28                     (FRONT PIVOT ROUGH TO z 0.78)
G01 X0.90                     (ROUGH SHOULDER FACE)
G00 X2.20
T0202                         (T02 FINISH, R0.02, IMAGINARY-TIP OFFSETS)
G00 Z0.45
G00 X0.30
G01 Z1.30 F0.008              (FRONT PIVOT D0.30, z 0 - 0.80)
G01 X0.80                     (SHOULDER FACE AT z 0.80)
G01 Z2.99                     (D0.80 TO z 2.49, STICKOUT 2.99)
G00 X2.20
(=========== PHASE B : SUB GRIP ===========)
G97 S9500 M03                 (CONSTANT RPM FOR SYNC)
M77                           (SYNC ON)
M11                           (SUB COLLET OPEN)
G00 B6.00                     (SUB FACE BEYOND PART FRONT AT 2.99)
G01 B1.19 F0.5                (COLLET COVERS z 0.8-1.8 ON D0.80; B = Z-1.8)
M10                           (SUB CLAMP)
G04 X0.3
(=========== PHASE C : GRIPPED + SYNCED, STICKOUT <= 12 ===========)
T0101
G00 Z2.98 B1.18
G00 X1.66
G01 Z6.50 B4.70 F0.02         (D1.66 TO z 6.00)
G00 X2.20
G00 Z2.98 B1.18
G00 X1.06
G01 Z4.88 B3.08               (D1.06 TO z 4.38)
G01 X1.70
G00 X2.20
G00 Z2.98 B1.18
G00 X0.86
G01 Z4.28 B2.48               (D0.86 TO z 3.78)
G01 X1.10
G00 X2.20
T0202
G00 Z2.95 B1.15               (z 2.45, OVERLAP PHASE-A SURFACE)
G00 X0.90
G01 X0.80 F0.008
G01 Z4.30 B2.50               (D0.80 TO z 3.80)
G01 X1.00                     (FACE z 3.80)
G01 Z4.90 B3.10               (D1.00 TO z 4.40)
G01 X1.60                     (FACE z 4.40)
G01 Z6.12 B4.32               (D1.60 TO z 5.62)
G00 X2.20
T0303                         (PARTING BLADE 0.5; KERF = Z-1.0 .. Z-0.5)
G00 Z6.62 B4.82               (KERF 5.62-6.12)
G00 X2.10
G01 X0.34 F0.008
G00 X2.20
G00 Z6.90 B5.10               (KERF 5.90-6.40)
G01 X0.34
G00 X2.20
G00 Z6.60 B4.80               (KERF 5.60-6.10)
G00 X1.70
G01 X0.30                     (PINION REAR FACE z 5.60, PIVOT D0.30)
G01 Z6.90 B5.10               (SIDE PASS D0.30 TO z 6.40)
G00 X2.20
G00 Z7.40 B5.60               (KERF 6.40-6.90, STICKOUT 7.40)
G01 X-0.05 F0.006             (PART OFF THROUGH CENTRE)
G04 X0.2
M78                           (SYNC OFF)
G00 B20.00                    (SUB WITHDRAWS WITH PART)
M05
(MAIN COLLET OPEN - MACHINE-SPECIFIC M-CODE)
G00 Z0.50                     (HEADSTOCK BACK; BAR HELD ON T03 BY BAR FEEDER)
(MAIN COLLET CLOSE - MACHINE-SPECIFIC M-CODE)
G00 X2.20                     (T03 CLEAR; NEW BAR FACE AT STICKOUT 0.50)
(SUB: STOP, MOVE TO EJECT POSITION - MACHINE-SPECIFIC)
M11                           (RELEASE PART)
M30
```

## 3. Limit checks

**Free stickout ≤ 3.0 while cutting without the sub**

- The largest Z in phase A is 3.00, on the rough passes.
- Every phase-A cut lies at z ≤ 2.50. ✓

**Stickout ≤ 12.0 only while gripped and synced**

- Phase C runs from Z 2.95 to 7.40.
- M77 and M10 are active from before the first phase-C cut until after part-off (M78 comes after X−0.05). ✓
- During the M77/M10 approach the stickout is 2.99, but no cutting takes place. ✓
- The re-chuck is done with no cutting. ✓

**Sub grip diameter 0.6–2.0**

- The sub grips Ø0.80 over z 0.8–1.8, which is entirely within the Ø0.80 shoulder. ✓
- The Ø0.30 pivot is never gripped. ✓
- The grip surface was finished before clamping. Use a smooth collet to avoid marking it.

**Sub and tool clearance**

- The smallest B is 1.15, so the collet face is at least 0.65 beyond the cutting point at 0.50.
- **This must be verified against the real collet nose and tool geometry.** If it is too tight, shorten the grip to about z 0.8–1.5.

**Spindle speed ≤ 10,000 rpm**

- G50 S10000 is set before G96. G96 S60 gives 9549 rpm at Ø2 and is capped at 10,000 below Ø1.91.
- Phase C runs at G97 S9500 on both spindles, held by sync. ✓
- Low surface speed on Ø0.30 (about 9 m/min) is the tradeoff of the rpm cap. Expect to tune feed and finish there.

**Part dimensions**

| Feature | z range | Made by |
|---|---|---|
| Ø0.30 front pivot | 0–0.80 | phase-A T02 |
| Ø0.80 shoulder | 0.80–3.80 | phase-A T02 to 2.49, phase-C T02 from 2.45 (same clamping, no re-reference) |
| Ø1.00 wheel seat | 3.80–4.40 | phase-C T02 |
| Ø1.60 pinion blank | 4.40–5.60 | phase-C T02 |
| Ø0.30 rear pivot | 5.60–6.40 | T03 |
| Overall length | 6.40 | — |

- Lengths come straight from the Z positions. ✓
- Internal corners carry T02's R0.02, since the drawing gives no corner spec.
- Phase-A and phase-C tool contact sits 0.5 from the bushing on Ø2 or Ø0.86 stock: δ ≲ 0.03 µm at about 4 N radial roughing force. That is negligible.

**Deflection against the ±0.003 tolerance**

- The main-side cuts are stiff, as shown in section 1.
- Back-working with T21 would give about 5.5 µm/N, which is why it is not used.

**Holding ±0.003 in production**

The ±0.003 tolerance still depends on wear offsets and in-process measurement, especially for the two Ø0.30 pivots. With no simulator, prove out the first part:

- single-block run
- measure each diameter
- trim the T02 and T03 X offsets
