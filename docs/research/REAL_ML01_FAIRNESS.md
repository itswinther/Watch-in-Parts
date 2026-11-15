# Fairness test: a real watchmaker's going train through Part 1

NOT-FOR-AGENT. This file describes how a real movement fares against our Part 1 checks. It belongs with
`tests/realcad/` and must never be copied into a task image.

Builder F, 14 Nov 2026. This is a report only. No grader, engine, spec or task file was changed.

**Source.** Marco Lang's ml01 ("001 ml01 Werk montiert einbaufertig", STEP, sha256 `34f001d6…1f75991`, checked).
- **No licence.** The STEP, the extracted solids, the converted parts and every derived mesh exist only in a scratch
  folder. Nothing from ml01 is committed.
- **Committed:** the scripts that download and convert at run time, plus numbers.
  - `tests/realcad/ml01_train.py`
  - `tests/realcad/fairness_ml01.py`
  - `tests/realcad/results_ml01_train.json` (numbers only, no geometry)
  - `tests/realcad/.harborignore` (`*`)
- **Safe from images:** `tests/realcad` is a folder name in `build_task.py`'s `NEVER_DIRS`.

The plan is REAL_WATCH_WORK.md section 9.

## Verdict

ml01's real going train passes most of Part 1 as is.

**Passes as drawn:**
- free to turn;
- held (once a dial holds the hour wheel's washer, as the real watch's dial does);
- nothing else collides;
- the three hands' speeds (60, 1 and 1/12 turns per hour, clockwise);
- coaxial;
- fits the case;
- the train at arbors 0.03 mm out of place;
- gear strength in steel (smallest margin +105 %).

**The checks it fails, and why:**

| Check | Result on the real design | Whose fault |
|---|---|---|
| 4 train (and with it 7 to 9 and 14) | Fails with the driven wheels delivered in the middle of their backlash. Passes when the centre is delivered on the flank the test pushes. | Grader rule: the drive test judges the delivered pose, not the design. Strict for real backlash (below). |
| 13 printable | Fails on fine features at ×1.2. | The real design at this scale. Fair, given the print process. The test also depends on the part's angle. |
| 3 seated | Fails on a pressed bush with no shoulder. | A real design feature. Strict, and defensible for printed parts. |
| C2 assembled (before our adjustments) | Fails as drawn: interference press fits and threads overlap by 0.014 to 0.32 mm³. | Grader and format: they have no notion of a press fit or a thread. Too strict for real CAD. |
| C1 files (before our adjustments) | Fails as drawn: the plate with its jewels has 391,259 triangles, over the 200,000 limit. | The format's limit against real CAD. Too strict, combined with MAX_PARTS 60. |
| 14 strength with brass wheels | Fails: the brass intermediate wheel z26 is at 318 MPa against 110. | The convention (Lewis, involute, 70.1 N·mm at a train scaled ×1.2). Strict for a real brass wheel. |

Final graded result (run 2, every adjustment below, Part 1 checks only):
- gates files and assembled pass;
- 12 of 14 checks pass;
- share 0.870 (20 of 23 weight points);
- seated and printable fail.

## 1. What was converted, and how

Pipeline (scratch folder `WORK`, every step logged in `WORK/build_log.json`):

1. `ml01_train.py fetch WORK`: curl from marcolangwatches.com, sha256 check, then
   `spikes/keyless/realcad/extract_step.py` (unchanged). Result: 223 solids.
2. `ml01_train.py build WORK [--phases F]`:
   - fuses each part's CAD solids with OpenCASCADE;
   - turns mobiles by their phase;
   - scales ×1.2 about the CAD movement centre;
   - shifts by (+7.44, −9.72) so that barrel II's axis lands at (0, 0), where the engine puts the barrel mobile;
   - writes one STEP per part with `geometry.core.write_step`, then `movement.json` and `WORK/barrel_ml01.step`.
3. `ml01_train.py phase WORK OUT.json`: finds each driven mobile's phase (section 3, adjustment 8).
4. `fairness_ml01.py WORK --details OUT.json` imports `tests/grade_watch.py` and `geometry/watch.py` unchanged and
   overrides two things only:
   - `W.barrel` returns barrel II (drum z80 + cover), read by the grader's own STEP loader;
   - `W.BARREL_TURNS_PER_HOUR = Fraction(3, 20)`.

   It then runs `grade_watch._job_movement` with P1's gates and checks, exactly as `grade_job` does for Part 1.

**Tooth counts.** I counted every train and motion-work gear on CAD sections (`teeth.py`, scratch). The counts agree
with the CAD names: barrel II 80, intermediate 26, centre pinion 12, centre wheel 64, third pinion 10, third wheel 75,
seconds pinion 8, cannon 12, minute wheel 36, minute pinion 10, hour wheel 40, ratchets 62.

**Speeds.** With the minute wheel at 1 turn per hour, barrel II turns 12/80 = 3/20 turn per hour. It turns in the
same sense as the centre, through two external meshes (barrel to intermediate, intermediate to centre pinion), so it
turns clockwise.
- The grader reported: centre 1, seconds 1 × 64/10 × 75/8 = 60, hour wheel 1 × 12/36 × 10/40 = 1/12.
- All three are clockwise, through working meshes (run 2).

| Mobile (axis, grader frame) | Parts (CAD solids) |
|---|---|
| barrel (0, 0), supplied by override | Federhaustrommel II z80 + Federhausdeckel II |
| intermediate (4.2251, −8.5534) | ÜFHMinRad z26 + the shoulder screw threaded into its arbor (one part) |
| centre (7.44, −9.72) | Minutentrieb z12, Minutenrad z64, Sekundenwellenlager (bush), Viertelrohr1 z12 (cannon), minute hand |
| third (11.2446, −14.0606) | Kleinbodentrieb z10, Kleinbodenrad z75 |
| seconds (7.44, −9.72) | Sekundentrieb z8 (central seconds through the hollow centre pinion), Sekundenrad z81, seconds hand |
| minute_wheel (12.5315, −9.4248) | Wechselrad1 z36, Wechseltrieb1 z10 |
| hour_wheel (7.44, −9.72) | Stundenrad1 z40, Butzen (pipe), hour hand |

Meshes, driver first: barrel 80 → intermediate 26 → centre 12; centre 64 → third 10; third 75 → seconds 8;
centre (cannon) 12 → minute wheel 36; minute wheel 10 → hour wheel 40.

**Fixed: 33 parts.** Each pressed sub-assembly is one part:
- the main plate with its jewels, pins and screws (in 6 pieces, plus one jewel that only touches);
- train bridge, barrel bridge, minute bridge and pallet bridge, each with its jewels, chatons and pins;
- the escape cap plate;
- barrel I (drum and cover, plus its arbor as a separate part);
- arbor II;
- the two series ratchets;
- 14 screws;
- the dial washer, and a dial that is not in the CAD.

**Left out:** escape wheel, balance, pallets, keyless works, springs, mainsprings, the second dial's motion work and
bridge, the shock indicator, the case clamps.

Every mobile is declared `AD-C100-HT` (steel). 49 parts in all: 33 fixed and 16 in mobiles; the limit is 60.

## 2. Part 1 results

Two graded runs. The machine was shared (load about 8 on 4 CPUs); the runs took 663 s and 553 s.

- **Run 1:** every driven mobile phased to the middle of its clear (backlash) range.
- **Run 2:** as run 1, but the centre turned +4.0° to the push-side end of its clear range against the
  intermediate, with the mobiles it drives turned with it kinematically, so that their own meshes are unchanged.

| Check | Run 1 | Run 2 | Measured (run 2 unless stated) |
|---|---|---|---|
| C1 files | pass | pass | after the adjustments of section 3 |
| C2 assembled | pass | pass | worst mobile pair centre/seconds 0.0006 mm³; fixed parts 0.0055 (plate / third jewel, line-to-line); parts of one mobile 0.0088 (hour wheel / its riveted pipe); one frame |
| 1 free to turn | pass | pass | worst 0.0 mm³ for every mobile: CAD line-to-line fits need no bore widening at VOL_TOL 0.01 |
| 2 held | pass | pass | smallest overlap moved 0.3 mm: seconds 0.027, third 0.047 mm³ (against 0.01) |
| 4 train | **fail** | pass | see section 4.1; drive ratio V/H/m², smallest per mesh: 1.55, 0.99, 1.06, 0.86, 1.76, 1.44 (need > 0.5); largest gap ≤ 0.042 (need ≤ 0.1); no jam (0.0 mm³) |
| 5 tolerant | **fail** | pass | ±0.03 mm: smallest ratio 0.61 (third/seconds, away) |
| 6 clear | pass | pass | worst 0.0006 mm³ (centre/seconds, the line-to-line bush) |
| 7 hour | fail (train) | pass | 1/12 |
| 8 minute | fail (train) | pass | 1 |
| 9 seconds | fail (train) | pass | 60 |
| 10 coaxial | pass | pass | 0.0 mm |
| 11 hands | pass | pass | reach 6.60 / 9.00 / 9.60 mm; above the frame by 0.60 / 1.32 / 2.02 mm; centre of volume 1.47 / 3.00 / 3.22 mm from the axis |
| 12 size | pass | pass | radius 20.374 (limit 20.7); height 8.56 (limit 13.4) |
| 13 printable | **fail** | **fail** | section 4.2 |
| 14 strength | fail (train) | pass | section 5 |
| 3 seated | **fail** | **fail** | seconds bush: ±x, ±y 0.028 mm³ (ok); +z 0.0, −z 0.0029 (need > 0.01) |
| share of P1 weights | 0.304 | **0.870** | |

## 3. Every adjustment, and why

Each adjustment is a finding about the grader or the format, except where it says otherwise.

1. **Scale ×1.2 and shift.** As planned: the plate radius becomes 20.37 (case 20.7). The shift puts barrel II's
   axis at (0, 0), because `Movement.__init__` fixes the barrel mobile at (0, 0). `case_centre` is the moved
   movement centre (7.44, −9.72).
2. **Barrel and speed overridden** in `fairness_ml01.py` (barrel II drum and cover; 3/20 turn per hour). Arbor II
   is fixed, since it is held while the train runs.
3. **Pressed and riveted sub-assemblies fused into one part** (per CAD sub-assembly). The reasons are all measured:
   - **Press fits overlap.** The CAD draws jewels, chatons and pins as interference fits. At ×1.2, 14 of them overlap
     their bridge or plate by more than C2's 0.01 mm³ between fixed parts:
     - plate jewels: 0.0175, 0.0137, 0.0137, 0.0184;
     - train-bridge chatons: 0.0276, 0.0276;
     - pins: 0.0148 (×4), 0.0107 (×2);
     - barrel-bridge jewels: 0.0175 (×2).
   - **The part limit.** Kept separate, the fittings make about 79 parts, over MAX_PARTS 60.
   - **Finding:** a real frame can be delivered only fused.
4. **The plate assembly is cut into pieces.**
   - Fused, the plate with its 12 fittings has **391,259 triangles** at the grader's tessellation (0.001 mm,
     0.1 rad). The limit is 200,000; the bare plate alone has 163,505, and a single jewel has about 35,000.
   - It is cut by planes clear of every fitting into 6 pieces of 28,512 to 110,723 triangles. They touch along the
     cuts, and their union is unchanged.
   - A plane at x = −4.5 (CAD frame) gave an invalid solid; −4.6 was used.
   - **Finding:** a real main plate cannot be one part file. Fused it is over MAX_TRIANGLES; separate, its fittings
     are over MAX_PARTS and fail C2.
5. **Screw threads trimmed.** Screws are drawn at the thread's major diameter inside tapped holes drawn at the minor
   diameter. As drawn at ×1.2, the screws overlap the plate, the pallet bridge and the barrel arbors by 0.014 to
   0.323 mm³, which would fail C2.
   - Each of the 13 screws that screw into a frame part is trimmed by the part it is screwed into (CUTS in the script).
   - The intermediate's shoulder screw (0.294 mm³ in the wheel's arbor) is fused into the wheel.
   - **Finding:** the format has no thread, so real CAD always needs this step.
6. **Internal cavity filled.** Fusing the train bridge enclosed two cavities (0.0011 mm³ in all) under screw tips in
   blind tapped holes. The loader rejects a part with "more than one shell", so the outer shell is kept. **Finding**
   (minor).
7. **Series ratchets phased.** Both ratchets are fixed parts and are drawn tooth through tooth: 0.105 mm³. Arbor II,
   its ratchet and its screw were turned together 1.81° about barrel II's axis, to the middle of the clear range. This
   is a modelling step of ours; it has nothing to do with the grader.
8. **Driven wheels phased** (`phase`). Each driven mobile was turned to the middle of the widest range of angles at
   which it clears its driver at 8 poses over one driver pitch. As drawn, the rest overlaps were over 0.01 mm³ on
   six pairs.
   - Overlaps as drawn: barrel/intermediate 0.062, intermediate/centre 0.018, centre/third 0.017,
     third/seconds 0.0102, cannon/minute wheel 0.015, minute wheel/hour wheel 0.027.
   - Phases (run 1): intermediate 6.49°, centre 26.25°, third 28.13°, seconds 29.06°, minute wheel 3.13°,
     hour wheel 5.44°.
   - Backlash, as the clear range over the driven pitch: barrel/intermediate 17 %, **intermediate/centre pinion 31 %**,
     centre/third 17 %, third/seconds 19 %, cannon/minute wheel 6 %, minute wheel/hour wheel 10 %.
   - This is a modelling step of ours, since a CAD assembly is rarely phased. **Run 2:** centre +4.0° (section 4.1).
9. **A dial added.** The CAD has no dial. In the watch, the dial presses the washer ("Flitter") onto the hour wheel.
   - Without anything above the washer, the washer is not joined to the frame (it is 0.30 mm from the plate), so C2
     fails.
   - Without the washer, the hour wheel is not held in +z: moved +0.3 mm, it overlaps nothing.
   - The dial added: a flat disc, z 0.204 to 0.45 (CAD units), outer radius 14.0, hole 0.95, on three feet standing on
     the plate's dial face.
   - With it, held passes for every mobile. This is a missing part, not a grader problem.
10. **Hands added**, since the CAD has none.
    - Each is a collet tube on its pipe or arbor (hour pipe r 0.75, cannon top r 0.40, seconds arbor r 0.116, CAD
      units) plus a blade with a hub disc, 0.25 thick.
    - Reach 5.5 / 7.5 / 8.0 CAD units (6.6 / 9.0 / 9.6 mm).
    - They are in the material of their mobile.
11. **Not needed: bore widening.** Free to turn and clear pass on the CAD's line-to-line fits. The worst spin
    overlap is 0.0, and the line-to-line bush gives 0.0006 mm³. VOL_TOL 0.01 is loose enough for real fits (the
    keyless rig's 2e-4 was not).

## 4. Tracing the failures

### 4.1 Train (run 1): the drive test judges the delivered pose

Run 1 fails on one mesh only: intermediate z26 → centre pinion z12, module 0.18.
- No jam (0.0 mm³), largest gap 0.082 (≤ 0.1).
- Drive test: V = 0.0052 mm³ (≥ 0.001), H = 0.60, V/H = 0.0087 against the required 0.5 m² = 0.0162. The ratio
  is 0.267 against the required 0.5.
- **Cause.** This pair has a backlash of 31 % of a pitch. Delivered mid-backlash, the test's push of 0.25 of the
  driver's pitch reaches only about 9.5 % of a pitch into the pinion leaf.

The same parts, with only the centre turned (`drive_try.py`, scratch; every pose clear at rest):

| Centre turned | Drive overlap V | Ratio | Mesh test | ±0.03 mm |
|---|---|---|---|---|
| −4.0° (on the far flank) | 0.0 | 0.0 | fails | fails |
| 0 (mid-backlash, run 1) | 0.0052 | 0.267 | fails | fails (0.16 / 0.38) |
| +4.0° (on the pushed flank, run 2) | 0.0192 | 0.986 | passes | passes (0.76 / 1.21) |

- **The result depends on where in its backlash the delivery happens to put the wheel.** The design is the same
  in all three rows.
- The test pushes counter-clockwise by convention, whatever the running sense. Here the pushed flank happens to be
  the loaded one: the barrel turns clockwise, so the intermediate turns counter-clockwise.
- The meshes with 6 to 19 % backlash pass even mid-backlash.
- **Classification:** a grader rule. It is not wrong (it catches teeth that do not engage), but a real cycloidal
  pinion mesh with generous backlash fails unless it is delivered on the pushed flank. A neutral pose or the other
  flank fails.
- **Option for the humans** (not done): run the drive test from the pose where the driven touches the pushed flank,
  for example after turning the driven until the first contact.

### 4.2 Printable: the real design at ×1.2, with an angle effect

The per-part result in run 2 is:

| Part | Pieces | Largest deviation (limit 0.2 mm) |
|---|---|---|
| plate_c, plate_d, plate_e, plate_f | 1 | 0.555, 1.701, 0.778, 0.752 |
| dial_washer | 12 | 0.517 |
| centre_pinion | 1 | 0.218 |
| seconds_bush | 0 | — |
| cannon | 2 | 0.555 |
| third_pinion | 4 | 0.324 |
| seconds_pinion | 4 | 0.316 |

Every other part passes: every wheel, the minute pinion, the bridges, the screws, the jewels and the hands.

Per CAD solid (`thin_diag.py`, scratch):
- **The bare plate fails** (0.753); every jewel and pin passes (0.07 to 0.16). The failing plate feature was not
  located.
- **The thin walls below 0.2 mm at ×1.2 are real:**
  - cannon pipe wall 0.125 × 1.2 = 0.15 mm;
  - seconds bush wall 0.10 × 1.2 = 0.12 mm, which vanishes entirely;
  - the spring washer.
- **The pinion leaves and pivots are real:** seconds arbor tip r 0.075 × 1.2; pinion leaves at module 0.139 to 0.18.

So these are real watch features below our 0.2 mm process limit at this scale, which is the task's premise: fair.
Watch out for one property of the test, though:
- **The test depends on the angle.** The third pinion passed in run 1 (phase 28.1°) and failed in run 2 (phase 2.5°:
  4 pieces, 0.324); unturned it fails (0.287).
- The centre pinion's deviation moved from 0.269 (run 1) to 0.218 (run 2).
- So the 0.05 mm voxel opening is not invariant to turning a part about its own axis, and a marginal part can pass
  or fail by its phase alone.

### 4.3 Seated: a pressed bush

The Sekundenwellenlager is pressed into the top of the hollow centre pinion with no shoulder (interference
0.0028 mm³). Moved 0.3 mm in ±z it overlaps the pinion by 0.0 and 0.0029 mm³, under 0.01.
- Moved in ±x and ±y, it overlaps by 0.028.
- **Classification:** a real design that the rule rejects. A press fit holds by friction, and the rule demands a
  positive seat.
- This is strict for real watchwork, and defensible for printed parts.
- Fused into the pinion (one pressed part), the pinion's own seat passes (+z 0.138, −z 0.135).

## 5. Strength (check 14) at T_barrel = 70.1 N·mm

Run 2. The going train is barrel → intermediate → centre → third → seconds. Face width b is the measured smallest
drive-overlap height. A pinion row passes in both material choices, a wheel row only in steel unless marked.

| Mesh | Gear | z | Wheel / pinion | m (mm) | b (mm) | T at driver (N·mm) | F (N) | Y | σ (MPa) | Steel (725) | Brass (110) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| barrel → intermediate | intermediate | 26 | wheel | 0.180 | 0.456 | 70.10 | 9.736 | 0.3734 | **317.7** | pass | **fail** |
| intermediate → centre | intermediate | 26 | wheel | 0.180 | 0.600 | 22.78 | 9.736 | 0.3734 | 241.4 | pass | **fail** |
| intermediate → centre | centre pinion | 12 | pinion | 0.180 | 0.600 | 22.78 | 9.736 | 0.2546 | 354.1 | pass | (steel) |
| centre → third | centre wheel | 64 | wheel | 0.156 | 0.276 | 10.52 | 2.106 | 0.4560 | 107.3 | pass | pass (margin 2.5 %) |
| centre → third | third pinion | 10 | pinion | 0.156 | 0.276 | 10.52 | 2.106 | 0.2198 | 222.6 | pass | (steel) |
| third → seconds | third wheel | 75 | wheel | 0.139 | 0.240 | 1.643 | 0.315 | 0.4658 | 20.3 | pass | pass |
| third → seconds | seconds pinion | 8 | pinion | 0.139 | 0.240 | 1.643 | 0.315 | 0.1748 | 54.0 | pass | (steel) |

| Material choice | Check 14 |
|---|---|
| All steel (AD-C100-HT, 725 MPa; graded) | **pass**, smallest margin +1.048 (centre pinion) |
| Brass wheels (AD-CW614N, 110) on steel pinions, per part (what builder M's `part_materials` will express) | **fail**: the intermediate z26 (317.7 and 241.4) |
| Per mobile, as today: the wheel-only intermediate in brass, the rest steel | **fail**: the same |
| Every mobile brass | **fail**: the intermediate, the centre pinion 12 (354), the third pinion 10 (223) |

These match the research estimates in REAL_WATCH_WORK.md section 9: 354, 335/241, 223 and 107.
- **The load is the wrong size for this train.** 70.1 N·mm is SW200-1's slipping maximum scaled for our ×1.617
  task. For a train at ×1.2, the same scaling gives 16.57 × 1.2³ = 28.6 N·mm. At that load every σ is ×0.408, and
  the brass intermediate still fails (129.6 > 110).
- **We do not know ml01's materials.** The STEP has none; brass wheels are what Saunier describes.
- **Classification:** a strict convention, not the design's fault. Lewis bending on our 25° involute form factors,
  rated at an automatic's slipping torque, rejects a brass intermediate wheel that the real watchmaker built.
  REAL_WATCH_WORK.md section 8 item 3 already proposes stating check 14 as a convention.

## 6. Not verified

- **Run 2's centre turn is a choice.** It was chosen because the test pushes that flank. I did not grade a run with
  every driven wheel on its pushed flank, nor one on its real loaded flank. That would put barrel/intermediate,
  centre/third and cannon/minute wheel on the far flank, which `drive_try.py` suggests would fail them.
- **Phases come from 8 sampled poses per driver pitch** on a 1/48-pitch grid. They are not exact backlash
  midpoints.
- **The failing plate feature** (0.753 mm deviation) was not located.
- **Parts 2 to 5 were not run** (they do not apply). The hands and dial are my own simple parts, not ml01's.
- **Builder M's `part_materials` is not on main**, so the brass rows are computed from the graded stresses, not
  graded.
- **The scratch tools** (`teeth.py`, `drive_try.py`, `thin_diag.py`, `held_nodial.py`, `tricount.py`,
  `loadcheck.py`) are not committed.

## 7. Reproduce

```
W=<scratch folder>
python3 -I tests/realcad/ml01_train.py fetch $W            # sha256 34f001d6...1f75991, then extract
python3 -I tests/realcad/ml01_train.py build $W
python3 -I tests/realcad/ml01_train.py phase $W $W/phases1.json
python3 -I tests/realcad/ml01_train.py build $W --phases $W/phases1.json
python3 -I tests/realcad/fairness_ml01.py $W --details $W/grade1.json         # run 1
# phases2.json = phases1 with centre +4.0, third -25.6, seconds +240.0, minute_wheel -1.333, hour_wheel +0.333 (deg)
python3 -I tests/realcad/ml01_train.py build $W --phases $W/phases2.json
python3 -I tests/realcad/fairness_ml01.py $W --details $W/grade2.json         # run 2
```

Both runs' numbers are in `tests/realcad/results_ml01_train.json`.
