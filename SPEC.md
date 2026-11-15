# SPEC.md: Watch in Parts

Version: 0.8 (2026-11-15): the customer-order watch. Same grader checks as 0.7; what changed is the agent's text
(the customer order, no acceptance test, no target; decided 15 Nov 04:05 and 04:16, `environment/brief_order.py`),
the barrel catalogue and the small case (`b/thin-cat`, merged into `g/final` 4c5d8d3), and the reward, which
gains the thickness score (decided by itswinther, 15 Nov 05:10, SESSION.md entry "orchestrator H ... 05:02").
0.7's history: Decisions 15:44 and 17:40 set it up; 17:56 (documents cited, gear strength, honesty term), 18:39
(time limits), 20:14, 20:34 (the 70.1 N·mm load), 21:43 (material per part); 15 Nov 00:50 and 01:19 tightened
checks 1, 6, 7 and 11.

This file is for the team and the judges. The agent never sees it. What the agent reads is listed in
section 2. Every number below is read from the code or the constants, and the file is named next to it.
If this file and the code disagree, the code is what grades; please log the difference in `SESSION.md`.

History is at the end (section 9).

## 1. The task in one paragraph

The agent is a movement designer. It gets a customer order for a thin dress watch and a folder of supplier
documents. It must design, as STEP parts (CadQuery is installed), the frame, going train and hands of a
demonstration-scale movement for a barrel it chooses from a catalogue: hours and minutes on the centre, seconds,
and a 24-hour hand on its own small dial. It also designs a 6-hour variant of the same calibre on the same frame
and an assembly plan, and it may state which parts work. It is asked to make the movement as thin as it can,
with no number given. It delivers one folder. The order states no acceptance test; nothing is frozen and nothing
is graded while it works. After it stops, one grader call inspects the folder part by part and writes one
reward.

## 2. What the agent has

In the task image the agent's folder is `/app`. `environment/make_bundle_job.py OUT` builds it:

| Path in `/app` | What it is | Made from |
|---|---|---|
| `instruction.md` | the customer order | `environment/public/job/PROMPT.md` |
| `FORMAT.md` | file formats, size limits, JSON layouts, how the factory reads the files, accepted materials | `environment/public/job/FORMAT.md` |
| `datasheets/DS-W01_barrel.md` | barrel catalogue: BR-096-30, BR-096-45, BR-096-66; speed classes | `environment/public/job/datasheets/` |
| `datasheets/DS-W02_case.md` | case catalogue; the ordered case is CS-254-134 | same |
| `datasheets/DS-W03_process.md` | print process: smallest feature, printability test, size accuracy | same |
| `datasheets/DS-W04_gear_rating.md` | tooth form, Lewis form factors, 25 degrees (no load factor) | same; values in `geometry/data/lewis_y.json` |
| `datasheets/DS-101`, `DS-201`, `DS-301` | workstream A's supplier sheets (mainsprings and Table 2a, materials, jewels), copied with calculated ratings, margins and safety factors removed | written by `environment/make_brief_job.py` from `spikes/keyless/datasheets/` |
| `datasheets/INDEX.md` | list of the documents | generated |
| `supplied/<part no.>.stl` | each catalogue barrel, drum and arbor as one mesh | `geometry/data/<part no.>/barrel.stl`, neutral header |
| `tools/kernel.py` | geometry helpers, including the STEP loader the grader uses | `geometry/core.py` |
| `tools/check_format.py` | file-format check only | `environment/check_format_job.py` |
| `delivery/` | empty; the agent writes here | |

Not in `/app`: QA-W100 (the inspection procedure of 0.7), DS-401 and DS-501 (crown sheets, left out while Part 5
is off), this file, `docs/CHECK_BASIS.md`, the grader, the reference.

Rules for these documents:

- The order states no acceptance test, no check name, no target height and no scoring formula
  (`ORDER_WORDS` in `make_bundle_job.py`). It names the catalogue items, the dial layout (hands at least 5 mm; the
  24-hour hand on its own dial, centre at least 6 mm from the centre, hand at least 3 mm), the two speed classes,
  the same frame for both builds, the automatic family (VM-DS-101 Table 2a), and the four statements of
  `report.json`.
- Every graded number that is stated lives in exactly one cell of one document in `/app`. Numbers that are
  graded but no longer stated are listed in `environment/public/job/TRACEABILITY_WATCH.md` (never in the image).
- `environment/make_brief_job.py --check` fails if a document is out of date with the constants.
  `make_bundle_job.py` fails if a graded number has no home cell, two home cells, or appears where it has no home,
  and if a forbidden file name, the `NOT-FOR-AGENT` mark, a solution-leaking phrase, the house design's height or
  the thickness formula would enter `/app`.
- The basis of every check (order, supplier sheet, format, or trade practice) is `docs/CHECK_BASIS.md`.

Installed for the agent: Python 3, CadQuery 2.8.0, `manifold3d`, `trimesh`, `numpy`, `scipy` (`PROMPT.md`).

## 3. The delivery

One folder, `/app/delivery/`. Layouts are in `FORMAT.md`.

| File | Content |
|---|---|
| `movement.json` | the 8-hour build (barrel speed class D) with hour, minute, seconds and 24-hour hands; names its barrel under `barrel` |
| `variant_6h.json` | the 6-hour variant (speed class B), the same barrel, the same frame |
| `assembly.json` | order and rigid-pose paths for every part of `movement.json` and the barrel |
| `parts/<name>.step` | one STEP file per part; a part used in both movements is one file |
| `scripts/` | optional; archived, never opened |
| `report.json` | optional; the designer's claim per part P1 to P4: `pass`, `fail` or `not_tested` |

Format limits (`geometry/watch.py`, stated in `FORMAT.md`):

| Limit | Value | Constant |
|---|---|---|
| Parts named in one movement file | 60 | `MAX_PARTS` |
| Triangles per part after tessellation | 200,000 | `MAX_TRIANGLES` |
| STEP file size | 16,777,216 bytes | `MAX_STEP_BYTES` |
| STEP tessellation | 0.001 mm chordal, 0.1 rad | `STEP_LINEAR_DEFLECTION`, `STEP_ANGULAR_DEFLECTION` |
| A STEP with more flat three-edged faces than this is a faceted mesh and is refused | 500 | `STEP_MAX_TRIANGLE_FACES` |
| Volume change allowed when a part is united with itself | 0.5 % | `SELF_UNION_TOL` 0.005 |
| One STEP read, in a child process | 120 s, 4096 MB | `STEP_TIMEOUT_S`, `STEP_MEMORY_MB` |
| Movement file size | 1,048,576 bytes | `MAX_JSON_BYTES` |
| `assembly.json` size | 67,108,864 bytes | `MAX_ASSEMBLY_BYTES` |
| `scripts/` | 200 files, 4,194,304 bytes | `MAX_SCRIPT_FILES`, `MAX_SCRIPTS_BYTES` |
| `report.json` size | 100,000 bytes | `REPORT_MAX_BYTES` in `spikes/keyless/constants.py` |
| Tooth counts in `meshes` | 3 to 1000 | `MIN_TEETH`, `MAX_TEETH` |
| Mobile materials | `AD-CW614N` (brass), `AD-C100-HT` (steel) | `MATERIAL_DESIGNATIONS` |
| Barrel | one of `BR-096-30`, `BR-096-45`, `BR-096-66`; both files name the same one | `BARREL_IDS` |

## 4. The barrels, the case and the order

From `geometry/watch.py` (cells in DS-W01 sections 2 to 4, DS-W02 section 2):

| Item | Value | Constant |
|---|---|---|
| Barrel teeth, module, pressure angle (every barrel) | 96, 0.2 mm, 25 degrees | `BARREL_TEETH`, `BARREL_MODULE`, `PRESSURE_ANGLE` |
| Axis | x = 0, y = 0 | fixed by `Movement` |
| Catalogue | BR-096-66 (z scale 1), BR-096-45 (4.5/6.6), BR-096-30 (3.0/6.6): BR-096-66 scaled in z about z = 0 | `BARREL_CATALOGUE` |
| BR-096-66 | drum z 0 to 1.0, arbor z -1.0 to 5.6, square z 3.3 to 4.9 | `_BR096_Z`, `barrel_z()` |
| BR-096-45 | drum z 0 to 0.6818, arbor z -0.6818 to 3.8182, square z 2.25 to 3.3409 | same |
| BR-096-30 | drum z 0 to 0.4545, arbor z -0.4545 to 2.5455, square z 1.5 to 2.2273 | same |
| Every barrel | pivot radius 0.5, square side 1.4, chamber inner diameter 12.12, core radius 2.02, bore radius 2.0367 | `BARREL_ARBOR_R`, `BARREL_SQUARE_SIDE`, `BARREL_INNER_D`, `BARREL_CORE_R`, `BARREL_BORE_R` |
| 8-hour build | 1/8 turn per hour, clockwise from the dial (speed class D) | `BARREL_TURNS_PER_HOUR` |
| 6-hour variant | 1/6 turn per hour, clockwise (speed class B) | `CHANGED_BARREL_TURNS_PER_HOUR` |
| Case CS-254-134 | inner radius 12.7, inner height 13.4 | `CASE_RADIUS` (= `SMALL_CASE_RADIUS`), `CASE_HEIGHT` |
| Smallest printable feature | 0.2 mm | `MIN_FEATURE` |
| Full thickness score at or below (not stated to the agent) | 3.85 mm | `THIN_REFERENCE_MM` |

The frame is right-handed and millimetres; +z is the dial side; every arbor is parallel to z (stated in
`FORMAT.md`). A file without the `barrel` key gets `DEFAULT_BARREL` (BR-096-30) only in stage mode and in the
tools; in one-job mode the key is required.

## 5. Parts, checks and weights

The table of parts is `JOB_PARTS` in `tests/grade_watch.py`. The agent reads no acceptance test: the order
names the four items, `FORMAT.md` states the conventions, and `docs/CHECK_BASIS.md` gives the basis of each rule. Each part has gates (conditions) and weighted checks. A part whose gates fail scores 0. Every other part
is still graded. No part gates another.

| Part | What | Weight | Gates | Check weights (sum) |
|---|---|---|---|---|
| P1 | going train and hands, `movement.json` | 0.25 | files (C1), assembled (C2) | 23 |
| P2 | 24-hour hand, `movement.json` | 0.10 | C1, C2, day hand declared (C3) | 4 |
| P3 | 6-hour variant, `variant_6h.json` | 0.15 | C1, C2, C3, same frame (C4) | 27 (every P1 and P2 check) |
| P4 | assembly, `assembly.json` for `movement.json` | 0.25 | C1 of `movement.json`, plan is valid JSON | 1 per part, barrel included |
| P5 | crown winding (off) | 0.25 | files | A's step weights, sum 1.0 |

P5 is graded only when `KEYLESS_IN_JOB` is True in `geometry/keyless_job.py`. It is False, so the task
is P1 to P4. See section 6.

**Gates** (`tests/grade_watch.py`, `geometry/watch.py`):

- **C1 files.** The movement file and every part file it names load as `FORMAT.md` says. Every mobile declares
  a valid `material`. `hour`, `minute` and `seconds` hands are present. The file names a catalogue barrel under
  `barrel`, and `variant_6h.json` names the same one as `movement.json`.
- **C2 assembled.** In the assembled pose, the frame (all fixed parts as one solid) and each mobile (barrel
  included) intersect each other by at most 0.01 mm3 (`VOL_TOL`). The same holds between any two fixed parts
  and between parts of one mobile. Fixed parts form one frame: joined when within 0.01 mm (`FRAME_JOIN`).
- **C3 day hand declared.** `hands.day` names a mobile and a part that is not the hour, minute or seconds hand's
  part (`job_day_declared`).
- **C4 same frame.** `variant_6h.json` has the same `fixed` list, in order, and the same `case_centre` as
  `movement.json` (`job_same_frame`).

**P1 checks** (numbers as in `docs/CHECK_BASIS.md`; weights from `WEIGHTS` and `JOB_CHECKS_1` in `tests/grade_watch.py`):

| No. | Key | Weight | Rule, with its numbers |
|---|---|---|---|
| 1 | `spin` | 1 | each mobile turned one turn in 72 steps of 5 degrees (`SPIN_STEPS`), and after every step i also to i + 1/3 and i + 1/5 of a step (`SPIN_OFFGRID`), 216 positions, never meets the frame by more than 0.01 mm3 |
| 2 | `held` | 2 | each mobile moved 0.3 mm (`HELD_MOVE`) along ±x, ±y, ±z is stopped by the frame, or by a coaxial mobile (axes within 0.01 mm) that is itself held |
| 3 | `seated` | 2 | each part of a multi-part mobile, moved 0.3 mm along ±x, ±y and one of ±z, meets its mobile's other parts by more than 0.01 mm3; the parts form one piece, each within 0.02 mm of the next (`SEAT_TOUCH`) |
| 4 | `train` | 3 | every declared mesh passes the mesh test; no mobile gets two speeds; every mobile is driven from the barrel |
| 5 | `tolerant` | 2 | the mesh test again with the driven mobile moved 0.03 mm (`MESH_SHIFT`) away from and towards the driver's axis |
| 6 | `clear` | 1 | every undeclared pair of mobiles (coaxial ones too): their swept solids (each mobile turned through a full turn, a solid of revolution worked out from horizontal sections, bands of at most 0.02 mm where faces slope, `SWEEP_DZ`; `Movement.clear_swept`) share at most 0.01 mm3, so no pair of angles collides |
| 7 | `hour` | 2 | hour hand turns clockwise, 1/12 turn per hour (`HAND_SPEED`) |
| 8 | `minute` | 2 | minute hand, 1 turn per hour |
| 9 | `seconds` | 2 | seconds hand, 60 turns per hour |
| 10 | `coaxial` | 1 | hour and minute axes within 0.01 mm (`COAX_TOL`) |
| 11 | `hands` | 1 | each hand reaches at least 5 mm (`HAND_REACH`; measured on the meshed solid, so a reach within the meshing accuracy of 0.001 mm, `STEP_LINEAR_DEFLECTION`, below the length counts), lies wholly above every fixed part, and its centre of volume is at least 0.5 mm from its axis (`HAND_CENTRE_MIN`), and seen from the dial side it covers at most 0.25 of the disc its tip sweeps (`HAND_AREA_MAX_SHARE`, one-job mode) |
| 12 | `size` | 1 | everything within the case radius 12.7 (`CASE_RADIUS`) of `case_centre` as it turns; total height at most 13.4 (`CASE_HEIGHT`) |
| 13 | `printable` | 1 | every delivered part passes DS-W03's test: voxel 0.05 (`THIN_VOXEL`), erode 1.5 voxels, dilate 1, no point further than 0.2 mm from the printable body (`THIN_DEV`) |
| 14 | `strength` | 2 | Lewis bending of the going train under 70.1 N·mm at the barrel (below) |

**Mesh test** (check 4; `Movement.mesh_run` in `geometry/watch.py`). For declared driver D (z_D teeth)
and driven N (z_N), step i runs from 0 to 8 x max(z_D, z_N) - 1 (`SAMPLES_PER_TOOTH` 8). D turns
counter-clockwise by i x 360 / (8 z_D) degrees and N clockwise by that angle x z_D / z_N.

- No jam: at every step, and at i + 1/3 and i + 1/5 after every 8th step (`MESH_OFFGRID`), D and N meet by at
  most 0.01 mm3.
- Engaged: at every 4th step where they do not meet, their smallest distance is at most 0.1 mm (`ENGAGE_GAP`).
- Drive: at every 8th step D turns a further 0.25 of its pitch (`DRIVE_FRACTION`). The new overlap V must be at
  least 0.001 mm3 (`DRIVE_MIN_VOLUME`), and V / H must exceed 0.5 x m² (`DRIVE_AREA_RATIO`), H being the z extent
  of that overlap and m = 2 x axis distance / (z_D + z_N).

A mesh that fails drives nothing, so the hands it feeds do not turn.

**Gear strength** (check 14; `strength_run` in `geometry/watch.py`; Decisions 17:56, 18:24, 20:34, 21:43):

- Rated: the going train only, from the barrel to the seconds hand's mobile, through passing meshes,
  breadth-first in declared order. The motion work and the 24-hour train are not rated. The barrel's own teeth
  are not rated.
- Load: T_barrel = 70.1 N·mm (`BARREL_TORQUE_MAX_NMM`), the upper end of the bridle slipping torque in DS-101
  Table 2a. The order says the going train is shared with an automatic version and must carry its barrel.
- At driver D: T_D = 70.1 x |n_barrel / n_D|; F = K x T_D / (m z_D / 2), K = 1.45 (`TOOTH_LOAD_FACTOR`, dry
  meshing; not stated to the agent); b = the smallest drive-overlap height H.
- Each gear: sigma = F / (b m Y(z)), Y from DS-W04 (`LEWIS_Y`). Pass when sigma is at most the allowable of the
  material of the part that holds that gear's teeth (the part with the most drive overlap; `part_materials`
  overrides the mobile's `material`).
- Allowables (`DS201_ALLOWABLE_ROWS`, lowest tensile row per code): `AD-CW614N` 110 MPa, `AD-C100-HT` 725 MPa.
  The corundum row (450 MPa, compressive) does not qualify. These allowables were DS-201 section 8, which the
  agent's copy of DS-201 no longer has; the agent gets the proof stresses (sections 3 and 4).

**P2 checks** (`WEIGHTS_2`): `day_hand` 3, the 24-hour hand turns clockwise at 1/24 turn per hour (`DAY_SPEED`);
`day_place` 1, its axis is at least 6.0 mm from the hour axis (`DAY_HAND_OFFSET`), it reaches at least 3.0 mm
(`DAY_HAND_REACH`, with the same 0.001 mm meshing allowance), lies above the frame, its centre of volume is at least 0.5 mm off its axis, and it covers at
most 0.25 of the disc its tip sweeps.

**P3** runs every P1 and P2 check on `variant_6h.json` with the barrel at 1/6 turn per hour.

**P4** (`Movement.assembly_replay`; path rules stated in `FORMAT.md`). Parts go in one at a time in `order`. A part is
installed when its path is a list of proper rigid 4x4 poses (within 1e-6) ending at the identity, its first
pose puts its bounding box wholly outside the movement's box grown by 5 mm (`ASM_CLEAR`), no vertex moves more
than 0.2 mm between poses (`ASM_STEP`), it has 2 to 1,500 poses (`ASM_MAX_POSES`), and in every pose it meets
each part already placed by at most 0.01 mm3. A part not in `order` stands in place from the start. A part that
breaks a rule is not installed but still stands in place. s_4 = parts installed / parts (barrel included).

## 6. Part 5, crown winding (off; not part of the submitted task)

Built by builder P (SESSION.md 21:31) and kept behind `KEYLESS_IN_JOB = False` in `geometry/keyless_job.py`.
With the switch off, `JOB_PARTS` has no P5 row, the order and `FORMAT.md` say nothing about winding works, and
DS-401 and DS-501 are left out of `/app`. Workstream A's thin-layout study (SESSION.md, A 04:03) found that the
winding works do not fit the thin layout. When the switch is on (not tested on this version):

- `movement.json` carries a `keyless` section and may mark mobiles `friction_on`; the grader runs A's acceptance
  steps AT-0 to AT-6 (`tests/grade_keyless.py`, fresh interpreter, at most 5400 s, `KEYLESS_TIMEOUT_S`), with A's
  step weights (`STEP_WEIGHTS` in `spikes/keyless/constants.py`) and part weight `KJ.P5_WEIGHT`.
- A's lengths are moved to our scale in `SCALE_TABLE` (`geometry/keyless_job.py`); keyless parts join Part 4.
- The part weights are renormalised over five parts, and the statement factor's mean runs over five parts.

## 7. Reward

The parts reward R and the statement factor are `grade_job` and `job_honesty` in `tests/grade_watch.py`, exact
fractions throughout. The thickness score is `thin_score()` in `geometry/watch.py`.

```
s_p    = (weight of part p's checks that pass) / (sum of part p's check weights), or 0 if a gate of p fails
share  = sum(w_p x s_p) / sum(w_p)
all    = 1 if every gate and check of every graded part passes, else 0
H      = total height along z of the taller of the two builds, barrel included (mm)
x      = (H - H0) / (CASE_HEIGHT - H0), clamped to 0..1;   H0 = THIN_REFERENCE_MM = 3.85, CASE_HEIGHT = 13.4
s      = (1 - x) ^ THIN_SCORE_EXPONENT,   THIN_SCORE_EXPONENT = 4;   s = 0 when H cannot be measured
R      = THIN_SCORE_SHARE x share + THIN_SCORE_SHARE x all x s,   THIN_SCORE_SHARE = 1/2
h      = max(0, mean over graded parts of points(claim_p, part p passes in full))
reward = R x (W_PRODUCT + W_HONESTY x h) / (W_PRODUCT + W_HONESTY)  =  R x (0.75 + 0.10 h) / 0.85
```

- Part weights w_p: P1 0.25, P2 0.10, P3 0.15, P4 0.25 (`JOB_PARTS`); sum 0.75.
- H0 is the height of the thinnest house design that runs as made at the stated size accuracy of +/- 0.01 mm
  (3.85 mm, `a/thin-asmade` 88904a8). The reference delivery (`solution/reference_watch.py OUT --job`) measures
  3.3491, below H0, and does not run as made. A build at or below H0 gets s = 1. Examples: H 4.71, s 0.686;
  H 6.0, s 0.361; H 13.4, s 0. The
  agent is told only that thinner is better; H0, the exponent and the formula are kept out of `/app`.
- Thickness pays only for a watch that fully works: a delivery with any failing gate or check gets at most
  1/2 x share, whatever its height.
- Points (`HONESTY_POINTS` in `spikes/keyless/constants.py`, imported, never copied):

  | Claim | part passes | part does not pass |
  |---|---|---|
  | `pass` | 1 | -2 |
  | `fail` | 0.5 | 1 |
  | `not_tested` | 0.5 | 0.5 |

- No report, an invalid one, or a part left out counts as `not_tested`. `height_mm` in `report.json` is recorded
  and changes nothing.
- So a full pass at or below H0 with a truthful report scores 1. With no report it scores 16/17 = 0.941.
  Do nothing scores 0.
- The grader writes reward 0 first and overwrites it at the end. If A's constants cannot be imported the reward
  is 0 and the details say why (fail closed).
- Decided by itswinther on 15 Nov 05:10 (SESSION.md). Before it, the one-job reward was R = 1/2 x share + 1/2 x
  all (no s), and the thickness score was computed only afterwards, by `spikes/thin_probe/score.py`.

## 8. Grader and run

- Call: `cd tests && python3 -I grade_watch.py /abs/delivery --reward FILE --details FILE`. It needs
  `tests/grade_watch.py`, `geometry/` and `spikes/keyless/constants.py` (statement factor) beside it.
- It never runs submitted code. It opens only the files the movement files and `assembly.json` name, plus
  `report.json`. Symbolic links and paths outside the delivery are refused.
- Each gate and check runs in its own try block with its own time limit. An exception or a timeout fails that
  check only.
- Time limits (`tests/grade_watch.py`, stated in `FORMAT.md`): 1800 s per condition or check (`TIMEOUT_S`),
  7200 s for the whole inspection (`JOB_TIME_LIMIT_S`). A check that would start after 7200 s fails. Harbor's
  verifier timeout in `harbor/watch_one` is 7800 s, so the grader always writes its own reward.
- The as-made checks (`geometry/asmade.py`: `made_free`, `made_mesh`, `made_clear`) join P1 and P3 only with
  `WATCH_AS_MADE=1` (`geometry/asmade_job.py`); the Harbor task does not set it, so they are not in the score.
- Harbor task: `harbor/watch_one/` (workstream A). Oracle = `python3 solution/reference_watch.py /app/delivery --job`.
  The agent image holds only `/app` above. `build_task.py` refuses `solution/`, `tests/`, `geometry/`,
  `SESSION.md`, `CLAUDE.md`, this file and the solution documents, by name and by sha256.
- Measured in Harbor on `g/final` 4c5d8d3, before the thickness term (SESSION.md, A 04:48): oracle 1.000
  (verifier 153 s), nop 0.000. To be re-run with the thickness term.

## 9. History

- **0.6 and earlier, the staged watch.** Four stages, each a fresh conversation inheriting frozen work: design,
  extend (24-hour hand), change (barrel once per 6 hours, with a kept-parts factor), assemble. Chain score = the
  product of the stage scores, each 0.5 p² + 0.5 [all pass]. The agent-facing text is
  `environment/public/SPEC_WATCH.md` and `INSTRUCTION_WATCH_S1..S4.md`. The grader keeps that mode
  (`grade_watch.py FOLDER --stage N [--prev FOLDER]`, the one-body `geometry/data/barrel_stage.stl`) only to
  regrade old runs (`transcripts/watch4_chain_*`, `harbor/watch4/`); with the thin defaults, old runs regrade
  with `WATCH_THIN_BARREL=0 THIN_CASE_RADIUS=0` (not re-run on this version). It still has the volume budget
  `light` (`FIXED_VOLUME_MAX` 355, `MOBILE_VOLUME_MAX` 278), which 0.7 dropped because no datasheet gives such a
  limit.
- **0.7, the one-job watch with a stated acceptance test** (Decisions 17:40): one brief and one grader call
  instead of four; linear part share instead of p²; no frozen files; C3 and C4 replace the stage-2 lock and the
  stage-3 kept share; `light` dropped; `strength` and the honesty factor added later the same day. The agent
  read QA-W100, an inspection procedure that stated every check. One barrel (6.6 mm arbor) and case CS-414-134
  (radius 20.7). Frontier models scored 1.0 on it.
- **0.7 to 0.8** (15 Nov): thin barrel and small case (`b/thin-4mm`), barrel catalogue (`b/thin-cat`), the
  customer-order brief with QA-W100 removed (`environment/brief_order.py`, `docs/CHECK_BASIS.md`), and the
  thickness term in the reward (section 7).
- **Retired tasks.** Board in a Box (H1 and H2), Moving Day and Hold the Line were dropped because clean agents
  scored 1.0 or close. Their specs are `environment/public/SPEC_H2.md`, `SPEC_MD.md`, and the H1 text of this
  file at commit 071ab86 and earlier (`git show 071ab86:SPEC.md`).
