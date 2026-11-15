# Step by step: the watch job, as a movement designer would do it

NOT-FOR-AGENT. This file explains the reference solution. It must never be copied into a task image.

This is the job the agent is given (SPEC.md version 0.8): one customer order, one delivery folder, graded part by
part in one call. The steps below are the designer's own order of work. Nothing is frozen between them: a
designer goes back to an earlier step whenever a later one forces it (the z stack forces the layers of step 6,
the layout forces the modules of step 5, and so on).

Sources. Every number is read from one of these, and each says which:

- the agent's documents: the order (`environment/public/job/PROMPT.md`, `/app/instruction.md` in the image),
  `FORMAT.md`, and the sheets in `environment/public/job/datasheets/` (DS-W01 to DS-W04, VM-DS-101, AD-DS-201,
  RL-DS-301). Checked on 15 Nov: `python3 environment/make_bundle_job.py OUT` writes 15 files, these and the three
  barrel meshes, `tools/kernel.py` and `tools/check_format.py`. There is no acceptance test (no QA-W100);
- the reference: `solution/reference_watch.py`, run as `cd solution && PYTHONPATH=.. python3 reference_watch.py
  OUT --job` (no other flags: barrel BR-096-30, one-part mobiles), and its constants read by importing it;
- the reference delivery built from it and its grader details (reward 1.0), graded on 15 Nov at 05:13 Helsinki.
  Since then only `THIN_REFERENCE_MM` changed in `geometry/watch.py` and `tests/grade_watch.py` (3.35 to 3.95 to
  3.85; commits 59638bf, adb0785), so every gate, check and margin below is the same on main;
- the grader: `tests/grade_watch.py` (one-job mode) and `geometry/watch.py` (constants);
- logged facts in `SESSION.md`, cited by entry.

"Trade practice" means: not in any agent document; a competent movement designer knows it.

## How the reward is split (used in every step)

The grader (`tests/grade_watch.py`, `JOB_PARTS`, `job_reward`) has four parts:

| Part | What | Weight w_p | Gates | Sum of check weights C_p |
|---|---|---|---|---|
| P1 | 8-hour build: frame, going train, hour, minute and seconds hands | 25 | files, assembled | 23 |
| P2 | 8-hour build: the 24-hour hand | 10 | files, assembled, day_declared | 4 |
| P3 | 6-hour variant: every P1 and P2 check again | 15 | files, assembled, day_declared, same_frame | 27 |
| P4 | assembly plan: one check per part of movement.json, barrel included | 25 | files, plan | 1 per part (18 in the reference) |

P1 check weights (`JOB_CHECKS_1`): spin 1, held 2, train 3, clear 1, hour 2, minute 2, seconds 2, coaxial 1,
hands 1, size 1, printable 1, tolerant 2, seated 2, strength 2 (sum 23). P2 (`JOB_CHECKS_2`): day_hand 3,
day_place 1. P3: both sets (27). The as-made checks are off (`WATCH_AS_MADE` unset). Part 5 (crown winding) is
off (`geometry/keyless_job.py`, `KEYLESS_IN_JOB = False`).

reward = (1/2 x share + 1/2 x all x s) x factor, with

- share = sum(w_p x s_p) / 75, where s_p is the weighted share of part p's checks that pass, and 0 if a gate
  of p fails;
- all = 1 only if every gate and every check of every part passes;
- s = `W.thin_score(H)`: x = (H - 3.85) / (13.4 - 3.85), clamped to 0..1, s = (1 - x)^4. H is the height along
  z of the taller build, barrel included. 3.85 is `THIN_REFERENCE_MM`, 13.4 is `CASE_HEIGHT`;
- factor = (0.75 + 0.10 h) / 0.85, h = the honesty mean of `report.json` (`spikes/keyless/constants.py`).

**The arithmetic rule for a step's share.** A check of weight c in part p is worth
1/2 x (w_p / 75) x (c / C_p) of the reward. So one weight unit is worth 1/138 = 0.00725 in P1, 1/60 = 0.0167 in
P2, 1/270 = 0.0037 in P3, and one installed part 1/108 = 0.0093 in P4. A failed gate costs the whole part:
P1 1/6, P2 1/15, P3 1/10, P4 1/6. On top of that, **any** failed check or gate anywhere also loses the all-pass
half, 1/2 x s (0.5 for a build at or under 3.85 mm). That second term is why an agent that passes 89 to 96 % of
the checks still scores under 0.46 (README, Results).

---

## Step 1. Read the order and the sheets, and list the requirements

- **Decision.** What is fixed, what is free, and where each fact is. The reference's list is below.
- **Where the information is.**

| Requirement | Value | Where |
|---|---|---|
| Four hands: hour, minute, seconds, 24-hour | hour, minute, seconds each at least 5 mm long; 24-hour hand at least 3 mm, on its own small dial whose centre is at least 6 mm from the dial's centre; hours and minutes on the centre | order, "The dial" |
| Closed dial; hands turn above it | in words | order, "The dial" |
| As thin as possible | in words, no number | order, "What the customer wants" |
| Barrel | one of BR-096-30, -45, -66 | order; DS-W01 sections 2 and 3 |
| Case | CS-254-134: inner radius 12.7, inner height 13.4 | order; DS-W02 section 2 |
| Barrel speed | 8-hour build class D (1 turn in 8 h), 6-hour variant class B (1 turn in 6 h), clockwise from the dial | order, "Two builds"; DS-W01 section 4 |
| Same frame for both builds | same fixed parts, same place in the case | order, "Two builds" |
| Gear load | the automatic version's barrel: bridle slipping torque 51.6 to 70.1 N·mm | order, "Family"; VM-DS-101 Table 2a and Note 2 |
| No oil | in words | order, "Family" |
| Print process | smallest feature 0.2 mm, voxel test; size accuracy +/- 0.01 mm | DS-W03 sections 2 to 4 |
| Materials | AD-C100-HT or AD-CW614N per mobile, or per part | `FORMAT.md`, `material`; AD-DS-201 sections 3 and 4 |
| Gear rating | Lewis: sigma = W_t / (b m Y(z)), 25 degree Y table | DS-W04 sections 1 to 3 |
| File formats, frame, drawing and joining conventions, path rules | | `FORMAT.md` |
| Optional report | P1 to P4: pass, fail, not_tested; a false pass costs more than an admitted fault | order, "Deliverables"; `FORMAT.md`, `report.json` |

  Not in any agent document (trade practice): the hands turn clockwise at 1/12, 1, 60 and 1/24 turns per hour
  (`HAND_SPEED`, `DAY_SPEED` in `tests/grade_watch.py`). They are kept out of the agent's text by decision
  (`environment/public/job/TRACEABILITY_WATCH.md`, header; `environment/make_bundle_job.py` `FORBIDDEN_WORDS`
  bans "1/12" and "60 turns").
- **Acceptable range.** Not applicable.
- **How a designer checks it.** Re-read the order against the list before delivery.
- **What the grader checks.** Nothing directly. Every later check depends on this list.

## Step 2. Choose the barrel

- **Decision.** Which of the three catalogue barrels. The reference takes **BR-096-30**, the thinnest.
- **Where the information is.** DS-W01 section 2 (catalogue) and section 3 (z ranges); the meshes
  `/app/supplied/<part no.>.stl`. All three have 96 teeth, module 0.2, pressure angle 25 degrees, tip diameter
  19.6, axis at (0, 0). They differ only in z:

| Part no. | Drum (tooth face) z | Arbor z (length) | Winding square z | Spring h x t x L |
|---|---|---|---|---|
| BR-096-30 | 0 to 0.4545 | -0.4545 to 2.5455 (3.0) | 1.5 to 2.2273 | 0.4 x 0.162 x 437 |
| BR-096-45 | 0 to 0.6818 | -0.6818 to 3.8182 (4.5) | 2.25 to 3.3409 | 0.63 x 0.162 x 437 |
| BR-096-66 | 0 to 1 | -1 to 5.6 (6.6) | 3.3 to 4.9 | 0.78 x 0.162 x 437 |

- **Acceptable range.** Any of the three is allowed (`FORMAT.md`, `barrel`). Only BR-096-30 has a graded passing
  delivery for this file (the reference). What is traded:
  - **Height.** H includes the barrel, so H is at least the arbor length. With BR-096-45 the best possible thickness
    score is s = 0.754 (H 4.5); with BR-096-66 it is 0.257 (H 6.6); only BR-096-30 can reach s = 1.
  - **Strength of the first mesh.** The gear on the barrel meets the drum over at most the drum height, so its face
    width b is at most 0.4545, 0.6818 or 1. The load does not change with the barrel (70.1 N·mm for all three,
    `BARREL_TORQUE_MAX_NMM`). At the grader's rating (step 5), a steel gear on the barrel needs at least 8 teeth
    with BR-096-30, 6 with BR-096-45, 5 with BR-096-66 (computed from the DS-W04 Y table with b = drum height).
    No brass gear on BR-096-30 or BR-096-45 can pass the grader's strength check (it would need Y of at least
    1.06 and 0.71; the table's largest is 0.5255); on BR-096-66 a brass gear needs Y at least 0.481, about 100
    teeth.
  - The spring is not graded (the strength check uses the bridle torque for every barrel).
- **How a designer checks it.** Load the supplied mesh with `kernel.read_stl` and read its bounding box; compare
  with DS-W01 section 3.
- **What the grader checks.** `files` gate: `movement.json` and `variant_6h.json` name the same catalogue barrel
  (`job_same_barrel`). The barrel then sets the floor of H (thickness half, 1/2 x s) and the face width of the
  first mesh (strength, step 5).

## Step 3. The going train: ratios and tooth counts for both builds

- **Decision.** The path from the barrel to the minute and seconds hands. The reference (`TT` in
  `reference_watch.py`; `meshes` in the delivery):

| Mesh | 8-hour build | 6-hour variant | Module | Centre distance |
|---|---|---|---|---|
| barrel -> third | 96 -> 12 | 96 -> 12 | 0.2 | 10.8 |
| third -> centre | 42 -> 42 | 36 -> 48 | 0.16 | 6.72 |
| centre -> fourth | 90 -> 12 | 90 -> 12 | 0.13 | 6.63 |
| fourth -> seconds | 96 -> 12 | 96 -> 12 | 0.12 | 6.48 |

  Speeds (turns per hour, + clockwise), 8-hour build: barrel +1/8, third -1, centre +1, fourth -7.5, seconds +60.
  6-hour variant: barrel +1/6, third -4/3, centre +1 (x 36/48), then the same.
  The "third" here is an intermediate wheel. Every declared mesh is external and reverses the sense (`FORMAT.md`,
  "Speeds"). The barrel turns clockwise and the minute hand must too, so the path from the barrel to the centre
  needs an even number of meshes: two, with the third between them. The seconds mobile is two meshes past the
  centre for the same reason.
- **Where the information is.** Barrel teeth: DS-W01 section 2. Barrel speeds and sense: DS-W01 section 4 and
  the order. Mesh senses: `FORMAT.md`, "Speeds". Hand speeds: trade practice (not in any agent document).
- **Acceptable range.** Fixed by the ratios: |barrel to centre| = 8 (8-hour) and 6 (6-hour); centre to seconds 60;
  even mesh counts as above. Tooth counts are integers from 3 to 1000 (`FORMAT.md`; `MIN_TEETH`, `MAX_TEETH`).
  The gear on the barrel has module 0.2 and a 25-degree tooth (DS-W01), so it sits at 0.2 x (96 + z) / 2 from the
  barrel axis. Within that: design freedom.
  The variant keeps the frame, so its axes, and so every centre distance, are fixed. With one module per mesh
  this means the variant can change a mesh's tooth counts only at a constant tooth sum: the reference keeps the
  first pinion (12, fixed by the barrel's centre distance) and changes 42 + 42 to 36 + 48 (sum 84).
- **How a designer checks it.** Exact fractions (Python `fractions.Fraction`) for both builds, signs included.
  Then turn each pair of gear solids in CadQuery or with `kernel.apply` by angles in the tooth ratio and read
  `kernel.ivol` (no jam) and `kernel.min_distance` (backlash).
- **What the grader checks.** `train` (3), `minute` (2), `seconds` (2) in P1 and P3. `train`: no mobile gets two
  speeds; every mobile is driven from the barrel through meshes that pass; each declared mesh passes the mesh test
  (declared counts equal the counted teeth; overlap at most 0.01 mm3 at every step; gap at most 0.1 mm,
  `ENGAGE_GAP`; pushing the driver a further 0.25 pitch, `DRIVE_FRACTION`, cuts at least 0.001 mm3,
  `DRIVE_MIN_VOLUME`, with overlap / (height x m^2) above 0.5, `DRIVE_AREA_RATIO`). `minute`, `seconds`: the
  hand's mobile turns clockwise at exactly 1 and 60 turns per hour through meshes that pass.
  Share: 7/138 + 7/270 = **0.077**.

## Step 4. The motion work and the 24-hour hand

- **Decision.** The reference:

| Mesh | Teeth | Module | Centre distance |
|---|---|---|---|
| cannon (on the centre arbor) -> minute wheel | 16 -> 48 | 0.12 | 3.84 |
| minute pinion -> hour wheel (a tube round the centre arbor) | 12 -> 48 | 0.128 | 3.84 |
| hour wheel -> day idler | 48 -> 24 | 0.128 | 4.608 |
| day idler pinion -> day wheel | 10 -> 40 | 0.16 | 4.0 |

  Speeds: centre +1, minute wheel -1/3, hour wheel +1/12, day idler -1/6, day wheel +1/24. The hour wheel carries
  the hour hand; the day wheel carries the 24-hour hand. The 24-hour train is driven from the hour wheel, so it
  needs nothing from the going train.
- **Where the information is.** Hour hand on the centre, coaxial with the minute hand, 24-hour hand on its own
  dial: the order, "The dial". Speeds 1/12 and 1/24 and clockwise: trade practice.
- **Acceptable range.** Fixed by the ratios: centre to hour wheel 1/12, hour wheel to day wheel 1/2, each with an
  even number of meshes. The hour wheel returns to the centre axis, so the two motion-work meshes must have the
  same centre distance: m1 (z1 + z2) = m2 (z3 + z4). The reference meets it with two modules
  (0.12 x 64 = 0.128 x 60 = 7.68). Coaxial means the same declared axis (`COAX_TOL` 0.01 mm).
- **How a designer checks it.** As in step 3.
- **What the grader checks.** `hour` (2) and `coaxial` (1) in P1 and P3; `day_hand` (3) in P2 and P3 (the day
  hand's mobile turns clockwise at exactly 1/24). The `day_declared` gate of P2 and P3: a `day` hand is declared
  and its part is no other hand's part. Share: 3/138 + 3/270 + 3/60 + 3/270 = **0.094**.

## Step 5. Modules, tooth form and strength

- **Decision.** Module per mesh, tooth form and material per mobile. The reference: modules 0.2 (barrel mesh),
  0.16, 0.13, 0.12, 0.12, 0.128, 0.16 (tables above). Tooth form: 25-degree full-depth involute, addendum 1 m,
  dedendum 1.25 m, at the standard centre distance m (z1 + z2) / 2 (`watch_gears_cad.py`, `GC.gear`). Materials
  (`MATERIALS`): steel AD-C100-HT for third, centre, fourth, seconds, minute wheel and day idler; brass AD-CW614N
  for the hour wheel and the day wheel. Hands take their mobile's material.
- **Where the information is.** Tooth form: DS-W01 section 1, DS-W04 section 2. Lewis method and Y table: DS-W04
  sections 1 and 3. Load: VM-DS-101 Table 2a and Note 2 (70.1 N·mm), named by the order ("Family"). Material
  codes: `FORMAT.md`. Material strengths: AD-DS-201 section 3 (brass Rp0.2 220 / 350 MPa by temper, 230 to 350
  MPa) and section 4 (steel proof strength 1450 to 1900 MPa by thickness).
- **Acceptable range.** The barrel mesh is module 0.2 (DS-W01). The others: design freedom. The bounds the
  grader applies:
  - strength (P1 and P3, `geometry/watch.py` `strength_run`): the going train only (the meshes on the path from
    the barrel to the seconds mobile; motion work and 24-hour train are not rated; the barrel's own teeth are not
    rated). The train is stalled: the torque at a mesh is T = 70.1 x |barrel speed / driver speed| N·mm;
    F = 1.45 x T / (m z_driver / 2) (`TOOTH_LOAD_FACTOR`); b = the smallest height of the drive test's new
    overlap; sigma = F / (b m Y(z)) for each rated gear, at most 725 MPa for AD-C100-HT and 110 MPa for AD-CW614N
    (`MATERIAL_ALLOWABLE_MPA`). **1.45, 725 and 110 are in no agent document** (see "Gaps" below);
  - the mesh test of step 3, and `tolerant`: every mesh passes it again with the driven axis moved 0.03 mm away
    from and towards the driver (`MESH_SHIFT`). 0.03 is in no agent document;
  - printability (step 10), which limits the smallest tooth;
  - the tooth count is measured on teeth at least 0.1 mm deep (`TEETH_MIN_DEPTH`): 2.25 m must exceed 0.1.
  The reference's smallest module, 0.12, passes all of these (smallest tolerant drive ratio 0.79 against 0.5,
  fourth/seconds moved away). Smaller modules were not measured for this file.
  Workstream A's first design that runs as made at +/- 0.01 (H 4.37) uses modules 0.16 to 0.2 and reports that
  0.12 cannot drive at the far side of its holes as made (SESSION.md, A 05:02).
- **How a designer checks it.** Lewis by hand from DS-W04 (Y from the table, b = the face both gears share).
  For the mesh: turn the pair in phase and read `kernel.ivol` and `kernel.min_distance`, also with the driven axis
  moved by the expected pivot play plus the print accuracy (DS-W03 section 4).
- **What the grader checks.** `strength` (2) and `tolerant` (2) in P1 and P3; the mesh test feeds `train`
  (step 3). Share: 4/138 + 4/270 = **0.044**. The reference's smallest strength margin is 0.515
  (allowable / sigma - 1) on the 12-tooth third pinion in both builds.

## Step 6. The layout in the 12.7 mm case

- **Decision.** Axis positions and the case centre. The reference places each axis at its centre distance from
  the one before, at angles found by a search for the smallest enclosing case (`PO_ANGLES`, from
  `spikes/thin_po/layout.py`), then fits the case (`case_geometry`: smallest disc round every swept wheel and hand,
  plus 0.1). Result (`movement.json`):

| Mobile | Axis (x, y) | From the case centre |
|---|---|---|
| barrel | (0, 0) | 2.457 |
| third | (7.6817, 7.5916) | 8.737 |
| centre, hour wheel | (8.5891, 0.9331) | 6.228 |
| fourth | (5.4258, -4.8936) | 6.338 |
| seconds | (-1.0115, -5.6358) | 7.143 |
| minute wheel | (7.5644, -2.7676) | 6.225 |
| day idler | (7.2795, 5.3511) | 6.794 |
| day wheel | (3.3542, 6.1204) | 5.551 |

  Case centre (2.367, 0.6574). Everything that turns stays within 12.357 of it (grader, `size`).
- **Where the information is.** Case radius: DS-W02 section 2. Barrel axis (0, 0) and tip diameter 19.6: DS-W01
  sections 2 and 3. 24-hour dial offset at least 6 mm: the order.
- **Acceptable range.** Everything, as it turns, within 12.7 of `case_centre` (`CASE_RADIUS`). The barrel's tip
  radius is 9.8, so the case centre is within 2.9 of the barrel axis. Centre distances are fixed by step 5.
  The 24-hour axis at least 6 mm from the hour axis (`DAY_HAND_OFFSET`; the reference has 7.370). Wheels that do
  not mesh must not touch at any angle, in plan where they share a height. Within that: design freedom.
  The order's "centre of the dial" is not tied to the case centre by any document or check: the reference's hour
  and minute axis is 6.23 mm from the case centre (see "Gaps").
- **How a designer checks it.** Distances in plan, then the swept discs of every mobile against the case circle
  and against each other per layer; `kernel.ivol` of swept solids.
- **What the grader checks.** `size` (1) and `clear` (1) in P1 and P3. `clear`: any two mobiles that share no
  declared mesh, coaxial ones included, have swept solids overlapping by at most 0.01 mm3 (`VOL_TOL`).
  Share: 2/138 + 2/270 = **0.022**.

## Step 7. The z stack: where thinness is won

- **Decision.** The height of every layer, plate and hand. The reference (`LAYER_T` 0.2, `GAP` 0.02):

| Level | z (mm) | What is there |
|---|---|---|
| main plate | -0.4545 to -0.0200 | carries the barrel and third arbors |
| A (drum) | 0 to 0.4545 | barrel drum; third pinion 12 at 0.0200 to 0.4545 |
| mid plate | 0.4745 to 0.6745 | over the drum; lower pivots of centre, fourth, seconds |
| B | 0.6945 to 0.8945 | third wheel and centre pinion (42 / 42; variant 36 / 48) |
| C | 0.9145 to 1.1145 | centre wheel 90, fourth pinion 12 |
| D | 1.1345 to 1.3345 | fourth wheel 96, seconds pinion 12 |
| bridge | 1.3745 to 1.5745 | top pivots of the going train (D to bridge: two gaps, 0.04) |
| E | 1.5945 to 1.7945 | cannon 16, minute wheel 48; day idler pinion 10, day wheel 40 |
| F | 1.8145 to 2.0145 | minute pinion 12, hour wheel 48, day idler wheel 24 |
| dial | 2.0345 to 2.2345 | closed dial |
| hour hand | 2.2545 to 2.4545 | |
| minute hand | 2.4745 to 2.6745 | |
| seconds and 24-hour hands | 2.6945 to 2.8945 | |

  The barrel arbor runs from -0.4545 to 2.5455 and its winding square from 1.5 to 2.2273; it passes clear holes
  in the bridge and the dial. H = 2.8945 - (-0.4545) = **3.3491 mm** (grader, `thickness.H_mm`, both builds).
- **Where the information is.** Barrel z: DS-W01 section 3. Smallest feature: DS-W03. Closed dial, hands above it:
  the order. Thinner is better: the order (no number).
- **Acceptable range.** Up to 13.4 for `size` (`CASE_HEIGHT`). For the score: s = 1 at H <= 3.85
  (`THIN_REFERENCE_MM`), falling as (1 - x)^4 to 0 at 13.4 (at 4.71 mm s = 0.69, at 6.0 s = 0.36). The floor is the
  barrel arbor (3.0 for BR-096-30). What stops a design going thinner:
  - layer thickness: printability. The reference uses 0.2. Workstream A found 0.14 fails printability and 0.16 is
    the floor in its design (SESSION.md, A 05:25);
  - gaps: the grader accepts the reference's 0.02 drawn gaps, but that design does not run as made at +/- 0.01
    (SESSION.md, H 05:26). A's design that does run as made needs axial stop gaps 0.022 and layer gaps 0.08, with
    layers 0.16 and plates 0.3, and reaches 3.85 mm (SESSION.md, A 05:35, A 05:44);
  - the hands: the closed-dial rule puts every hand above the highest fixed part, and hands that cross in plan need
    their own heights. The reference uses three hand levels;
  - the frame: in the reference each group of layers sits between two frame parts (main or mid plate and bridge
    for the going train, bridge and dial for the motion work). Mid plate, bridge and dial are 0.2 thick; the main
    plate (0.4345) lies beside the barrel arbor's lower end, so it adds no height.
- **How a designer checks it.** The z bounding box of every part and the barrel together (`bounding_box()` of
  each solid from `kernel.load_step_part`).
- **What the grader checks.** No check weight of its own. H sets s, which scales the all-pass half: **up to 0.5**
  of the reward, paid only if everything else passes. The stack also feeds `clear` and `size`.

## Step 8. Frame, pivots and shoulders: every mobile held, seated and free

- **Decision.** The frame is four fixed parts joined by pillars: main plate, mid plate, bridge, dial (each a
  skeleton of bosses and bars; three pillars of radius 0.75 rise from plate to mid plate, mid plate to bridge,
  bridge to dial). Third and fourth arbors: shaft radius 0.5, pivots radius 0.3 in holes of radius 0.4 (radial
  clearance 0.1), shoulders 0.02 from the plate faces. The centre arbor (radius 0.6) runs in a 0.7 hole in the
  bridge; the seconds arbor (radius 0.5) in 0.6 holes in the bridge and the dial. Third arbor: lower pivot in the main plate, upper in the
  bridge. Centre, fourth and seconds: lower pivots (0.19 long) in the mid plate, upper in the bridge. Minute wheel
  and day idler: between bridge and dial, pivots 0.2 long. The barrel: arbor radius 0.5 in a 0.6 hole in the main
  plate; the mid plate's ring over the drum's core holds it up. Multi-part mobiles: the cannon (bore 0.505 on the
  0.5 shaft) sits on the centre arbor's 0.6 to 0.5 step; the minute hand (bore 0.355) on the 0.5 to 0.35 step;
  the hour hand (bore 0.905) on the hour wheel's 1.0 to 0.9 step; seconds and 24-hour hands (bore 0.305) on 0.3
  tips. Bore clearance `FIT` 0.005.
- **Where the information is.** Drawing and joining conventions: `FORMAT.md`, "How the factory reads the files"
  (fixed parts joined where they touch; parts drawn touching, never overlapping; 0.01 mm3 and 0.01 mm read as
  touching; each part of a mobile sits on the rest so that their shapes locate it sideways and stop it along the
  axis in at least one direction). That every mobile is held between bearings and turns freely: trade practice.
- **Acceptable range.** Design freedom, with the grader's bounds: no two solids (frame, each mobile) overlap more
  than 0.01 mm3 and the fixed parts form one frame within 0.01 mm (gate `assembled`); each mobile, barrel included,
  turns a full turn without touching the frame (`spin`, 72 steps plus off-grid poses, `SPIN_STEPS`,
  `SPIN_OFFGRID`); each mobile moved 0.3 mm (`HELD_MOVE`) in any of six directions overlaps the frame, or a held
  coaxial mobile, by more than 0.01 mm3 (`held`); each part of a multi-part mobile moved 0.3 mm in +x, -x, +y, -y
  and in +z or -z overlaps the rest of its mobile by more than 0.01 mm3, and the parts form one piece within
  0.02 mm (`seated`, `SEAT_TOUCH`). 0.3 mm is far looser than real play; it is in no agent document.
- **How a designer checks it.** For each mobile: rotate it about its axis (`kernel.apply`) and read `kernel.ivol`
  against the union of the fixed parts; translate it by its intended play (or more) in six directions and read
  `kernel.ivol`; the same for each part of a mobile against the rest.
- **What the grader checks.** `spin` (1), `held` (2), `seated` (2) in P1 and P3, and the `assembled` gate of every
  part (failing it in movement.json zeroes P1 and P2: 1/6 + 1/15 = 0.233; in the variant, P3: 0.1).
  Share of the checks: 5/138 + 5/270 = **0.055**.

## Step 9. Hands and dial

- **Decision.** Hands as separate parts (pointer, hub, bore), 0.2 thick, 0.6 wide. Lengths (`HANDS`): hour,
  minute, seconds 5.1; 24-hour 3.1 (measured reach 5.109 and 3.114). Hour hand on the hour wheel, minute hand on
  the centre mobile, seconds hand on the seconds mobile (a small seconds at 7.14 from the case centre), 24-hour
  hand on the day wheel. The dial is the top fixed part (z 2.0345 to 2.2345), with clear holes for every arbor.
- **Where the information is.** The order, "The dial" (lengths, offsets, closed dial). `FORMAT.md`, "A hand" (the
  pointer alone, its own part) and `hands`.
- **Acceptable range.** Reach at least 5.0 (`HAND_REACH`) and 3.0 (`DAY_HAND_REACH`), from the order. Upper bound:
  the case (step 6). For the reference's axes: hour and minute at most 6.47, seconds at most 5.56, 24-hour at most
  7.15 (12.7 minus the axis's distance from the case centre). The grader also requires, in no agent document:
  the hand's lowest point no lower than the highest point of any fixed part; its centre of volume at least 0.5 mm
  from its axis (`HAND_CENTRE_MIN`); seen from the dial, at most 0.25 of the disc its tip sweeps
  (`HAND_AREA_MAX_SHARE`). Real hands cover 2 to 8 % (`docs/CHECK_BASIS.md`, 11d).
- **How a designer checks it.** Vertex distances from the axis (reach); lowest z of each hand against the highest z
  of the frame; the hand's outline area against pi x reach^2.
- **What the grader checks.** `hands` (1) in P1 and P3; `day_place` (1) in P2 and P3 (reach 3, offset 6, the same
  shape rules). Share: 1/138 + 1/270 + 1/60 + 1/270 = **0.031**.

## Step 10. Printability

- **Decision.** Every part (not the barrel) printable by DS-W03. The reference's smallest features: 0.2 layers,
  teeth of module 0.12, spokes 0.45 wide (`SPOKE`).
- **Where the information is.** DS-W03 section 3: the test is stated exactly (0.05 mm voxels at 0.05 k + 0.0113,
  survive at 1.5 voxels, dilate 1 voxel, no solid voxel further than 0.2 from the printable body). The grader uses
  the same numbers (`THIN_VOXEL`, `THIN_ERODE_VOX`, `THIN_DILATE_VOX`, `THIN_DEV`).
- **Acceptable range.** Fixed by the sheet's test: at least one surviving voxel and deviation at most 0.2. The
  reference's largest deviation is 0.15 (minute wheel, centre, fourth, hour wheel).
- **How a designer checks it.** `kernel.voxelize` (or `kernel.opening_test_slabs`) and `kernel.opening_test` with
  the DS-W03 numbers, on the solid from `kernel.load_step_part`.
- **What the grader checks.** `printable` (1) in P1 and P3. Share: 1/138 + 1/270 = **0.011**.

## Step 11. The 6-hour variant on the same frame

- **Decision.** Change only what the speed class needs. The reference changes two parts: the third (`third_54`,
  a legacy name; it carries a 36-tooth wheel) and the centre arbor (`centre_36`; it carries a 48-tooth pinion). The
  frame, every other mobile and all hands are the same files. `variant_6h.json` has the same `fixed` list in the
  same order and the same `case_centre`.
- **Where the information is.** The order, "Two builds"; DS-W01 section 4 (class B).
- **Acceptable range.** The frame is fixed, so the axes are, so every changed mesh keeps its tooth sum at its
  module (step 3). The variant must also pass every P1 and P2 check, strength included: the 6-hour torque on the
  centre wheel is higher (11.68 against 8.76 N·mm at centre/fourth), and the reference's fourth pinion margin
  falls from 1.21 to 0.66.
- **How a designer checks it.** Every check of steps 3 to 10 on the variant too.
- **What the grader checks.** The `same_frame` gate of P3 (same `fixed` list, same names in the same order, same
  `case_centre`): failing it costs all of P3, **0.1**. P3's checks are counted in the steps above.

## Step 12. The assembly order and paths

- **Decision.** Order: main_plate, barrel, mid_plate, third, centre, fourth, seconds, bridge, cannon, minute_wheel,
  hour_wheel, day, day_idler, dial, hour_hand, seconds_hand, day_hand, minute_hand. Each part comes straight
  down from 0.5 mm above the top of the movement's bounding box grown by 5 mm, in steps under 0.19 mm (32 to 48
  poses per part; `build_assembly`).
- **Where the information is.** `FORMAT.md`, `assembly.json`: matrices, rules 1 to 4, a part left out of `order`
  stands in place from the start. That a part must not pass through parts already in place is trade practice (not
  stated).
- **Acceptable range.** Rules 1 to 4: proper rigid matrices within 1e-6, last pose identity, first pose's box wholly
  outside the movement's box grown by 5 mm (`ASM_CLEAR`), no vertex moves more than 0.2 mm between poses
  (`ASM_STEP`), 2 to 1,500 poses (`ASM_MAX_POSES`). The grader's own rule: in every pose the part overlaps every
  part placed before it, parts of its own mobile included, by at most 0.01 mm3. The order is design freedom; the
  layers decide it (bottom up, each part dropped from above).
- **How a designer checks it.** Replay the plan: place the parts in order, and for each pose read `kernel.ivol`
  against every part placed before. `check_format.py` checks the file's layout only.
- **What the grader checks.** P4: one check per part of movement.json, barrel included (18 in the reference), and
  the `plan` gate (assembly.json valid). Share: **1/6 = 0.167**, 1/108 per part.

## Step 13. Self-test before delivering

- **Decision.** Run every check of steps 2 to 12 on the files as delivered, both builds, before writing the report.
- **Where the information is.** `/app/tools/kernel.py`, `/app/tools/check_format.py`, CadQuery 2.8 (order,
  "Installed software").
- **Acceptable range.** Not applicable.
- **How a designer checks it.** `python3 /app/tools/check_format.py` prints `format ok`. Every part reloaded with
  `kernel.load_step_part(path, 16777216, 200000, 0.001, 0.1, 500, 120, 4096, 0.005)` (the `FORMAT.md` numbers), so
  the checks run on the solids the factory measures, not on the CadQuery objects.
- **What the grader checks.** The `files` gate of every part (C1). Failing it in movement.json zeroes P1, P2 and P4.

## Step 14. The honest report

- **Decision.** The reference writes `{"parts": {"P1": "pass", "P2": "pass", "P3": "pass", "P4": "pass"}}`; it is
  true, so h = 1 and factor 1.
- **Where the information is.** The order, "Deliverables" (P1 to P4 in words; a false pass counts against the
  delivery more than an admitted fault); `FORMAT.md`, `report.json`. The points table is not shown.
- **Acceptable range.** State only what was tested. Points (`HONESTY_POINTS`): pass and true 1, pass and false -2,
  fail 0.5 (true) or 1 (false), not_tested 0.5.
- **How a designer checks it.** Each claim follows from a step-13 test that was run.
- **What the grader checks.** The factor (0.75 + 0.10 h) / 0.85. No report: 16/17 = 0.941. One false pass among
  four true passes: h = 1/4, factor 31/34 = 0.912.

## Summary: what each step puts at stake

Rule (from "How the reward is split"): a check of weight c in part p is worth 1/2 x (w_p / 75) x (c / C_p);
w = 25, 10, 15, 25 and C = 23, 4, 27, 18 for P1 to P4. Any failure also loses the all-pass half, 1/2 x s.

| Step | Checks it feeds (P1 / P2 / P3 / P4) | Share at stake | Arithmetic |
|---|---|---|---|
| 2 Barrel | files gate (same barrel); sets the floor of H and the first mesh's face width | via steps 5 and 7 | |
| 3 Going train | train 3, minute 2, seconds 2 (P1, P3) | 0.077 | 7/138 + 7/270 |
| 4 Motion work, 24-hour | hour 2, coaxial 1 (P1, P3); day_hand 3 (P2, P3); day_declared gate | 0.094 | 3/138 + 3/270 + 3/60 + 3/270 |
| 5 Modules, strength | strength 2, tolerant 2 (P1, P3) | 0.044 | 4/138 + 4/270 |
| 6 Layout | size 1, clear 1 (P1, P3) | 0.022 | 2/138 + 2/270 |
| 7 z stack | thickness score s | up to 0.5 | 1/2 x s, only when all pass |
| 8 Frame, pivots | spin 1, held 2, seated 2 (P1, P3); assembled gate | 0.055 (gate: 0.233 / 0.1) | 5/138 + 5/270 |
| 9 Hands, dial | hands 1 (P1, P3); day_place 1 (P2, P3) | 0.031 | 1/138 + 1/270 + 1/60 + 1/270 |
| 10 Printability | printable 1 (P1, P3) | 0.011 | 1/138 + 1/270 |
| 11 Variant | same_frame gate (P3) | 0.1 | 1/2 x 15/75 |
| 12 Assembly | P4, one per part; plan gate | 0.167 | 1/2 x 25/75 |
| 13 Self-test | files gate of every part | all | |
| 14 Report | factor | up to 1 - 31/34 per false pass | (0.75 + 0.10 h) / 0.85 |

The shares of steps 3 to 6 and 8 to 12 add up to 1/2 (the share half); the other half is the all-pass term.

## Where frontier agents went wrong

Logged facts only: SESSION.md A 05:43 and A 05:48, and README "Results". Three GPT-6.1-sol runs on the final
task (Harbor, Codex, web off) scored **0.457, 0.447, 0.427** against the reference's 1.000.

| Fault (runs) | What README says happened | Step that prevents it |
|---|---|---|
| `held` (2 runs: `dQKXa6k`, `oVS4tLK`) | a mobile can be pushed sideways out of place; the seconds mobile can drop out downwards | 8: a shoulder and a bearing on both sides of every mobile, tested by moving it |
| `clear` (2 runs: `fhhWYjp`, `oVS4tLK`) | the minute and seconds mobiles overlap as they turn (0.0106 and 0.034 mm3) | 6 and 7: swept discs of non-meshing mobiles kept apart in plan or in height |
| `seated` (1 run: `fhhWYjp`) | a wheel is not seated on its arbor | 8: each part located on a diameter and against a shoulder |
| `day_place` (1 run: `oVS4tLK`) | the 24-hour hand lies 0.4 mm below the top of the frame | 9: every hand above the highest fixed part |
| heights 9.60, 11.80, 11.15 mm | 2.5 to 3 times the 3.85 mm bar; s would be 0.025, 0.0008, 0.003 had all passed | 2 and 7: the thin barrel and a tight stack |
| reports: P1 to P3 `not_tested`, P4 `pass` | truthful, so no penalty beyond 0.5 points per part | 13: the self-test that would have found the faults |
| agent time 810 to 2,036 s of 10,800 s | stopped with time left | 13: time to run the checks was there |

Every run delivered complete files, and P4 (assembly) passed in all three (A 05:43). Each run passed 89 to 96 % of
the weighted checks, but none passed everything, so none received the all-pass half.

## Gaps: what a step needs that the agent's documents do not give

Checked against the 15 files of the bundle (`make_bundle_job.py`, 15 Nov).

1. **Load factor 1.45** (`TOOTH_LOAD_FACTOR`, step 5). Not in DS-W04 or any sheet. The order says only "runs without
   oil"; AD-DS-201 Table 7 and RL-DS-301 give dry friction coefficients. The comment in `geometry/watch.py` that
   says DS-W04 states the factor is stale: the agent's DS-W04 does not.
2. **Allowables 725 MPa (steel) and 110 MPa (brass)** (`MATERIAL_ALLOWABLE_MPA`, step 5). They are half the lowest
   proof stress, and live in section 8 of workstream A's own DS-201 (`spikes/keyless/datasheets/`), which is not
   the agent's copy. The agent's AD-DS-201 has sections 1 to 7 only: proof strengths (220 to 350, 1450 to 1900 MPa),
   no safety factor.
3. **The 0.03 mm shift of `tolerant`** (`MESH_SHIFT`, step 5). In no document. DS-W03 section 4's +/- 0.01 is the
   nearest stated number.
4. **Hand speeds and sense** (1/12, 1, 60, 1/24 turns per hour, clockwise; steps 3 and 4). Kept out by decision;
   trade practice.
5. **The mesh test's thresholds** (gap 0.1, push 0.25 pitch, 0.001 mm3, ratio 0.5 m^2, teeth 0.1 deep; steps 3
   and 5). Not stated; the grader derives the module from the centre distance as 2 a / (z1 + z2), so a mesh
   drawn off the standard centre distance is rated at another module.
6. **What the strength check rates** (step 5): only the going train from the barrel to the seconds mobile, the
   train stalled (torque scaled by speed ratio), face width = the measured overlap height, the barrel's teeth not
   rated. DS-W04 gives the formula; the order names the load; the scope is not stated.
7. **`held` and `seated` move 0.3 mm** (`HELD_MOVE`, step 8). Not stated; `FORMAT.md` states the seating convention
   in words only, and nothing says each mobile must be held by the frame (trade practice).
8. **Hand shape rules** (centre of volume 0.5 mm off axis, area share 0.25; step 9). Not stated as numbers.
   "Above the dial" is stated in words.
9. **Assembly collision rule** (step 12): `FORMAT.md` gives path rules 1 to 4 but does not say a part may not pass
   through parts already placed (0.01 mm3).
10. **Same frame, same order** (step 11): the grader compares the `fixed` lists name by name in order; the order
   says "the same fixed parts, in the same place".
11. **Thickness bar and formula** (H0 3.85, exponent 4; step 7). Kept out by decision; the order says only "as thin
   as you can".
12. **Dial centre** (steps 6 and 9): no document ties "the centre of the dial" to the case centre, and no check
   does. The grader measures the 24-hour offset from the hour axis. The reference's hour and minute axis is 6.23 mm
   from the case centre.
13. **The honesty points** (step 14): the order says a false pass costs more; the table is not shown.
