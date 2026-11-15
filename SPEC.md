# SPEC.md

Version: 0.7 (2026-11-14): the one-job watch. Decisions 15:44 and 17:40 in `SESSION.md` set it up;
17:56 (documents cited, gear strength, honesty term), 18:39 (time limits), 20:14 (hand speeds stated),
20:34 (the 70.1 N·mm platform load) and 21:43 (material per part) filled it in. This body was rewritten on
14 Nov at about 23:30 to describe 0.7 as it is built. No rule changed in that rewrite.

This file is for the team and the judges. The agent never sees it. What the agent reads is listed in
section 2. Every number below is read from the code or the constants, and the file is named next to it.
If this file and the code disagree, the code is what grades; please log the difference in `SESSION.md`.

History is at the end (section 9).

## 1. The task in one paragraph

The agent is a movement designer. It gets one work order and a folder of supplier documents. It must design,
in CadQuery, the going train, frame and hands of a demonstration-scale watch for a supplied barrel. It also
designs a 24-hour hand, a 6-hour variant of the same calibre on the same frame, and an assembly plan. It
delivers one folder. Nothing is frozen and nothing is graded while it works. After it stops, one grader call
inspects the folder part by part and writes one reward.

## 2. What the agent has

In the task image the agent's folder is `/app`. `environment/make_bundle_job.py OUT` builds it:

| Path in `/app` | What it is | Made from |
|---|---|---|
| `instruction.md` | the work order | `environment/public/job/PROMPT.md` |
| `FORMAT.md` | file formats, size limits, JSON layouts | `environment/public/job/FORMAT.md` |
| `datasheets/QA-W100_inspection.md` | the acceptance test, as the maker's inspection procedure | `environment/public/job/datasheets/` |
| `datasheets/DS-W01_barrel.md` | barrel catalogue; the supplied barrel is BR-096-20 | same |
| `datasheets/DS-W02_case.md` | case catalogue; the ordered case is CS-414-134 | same |
| `datasheets/DS-W03_process.md` | print process and the printability test | same |
| `datasheets/DS-W04_gear_rating.md` | Lewis form factors, 25 degrees | same; values in `geometry/data/lewis_y.json` |
| `datasheets/DS-101` to `DS-501` | workstream A's supplier sheets: mainspring and barrel, materials, jewels, crown and stem, finger torque | `spikes/keyless/datasheets/` |
| `datasheets/INDEX.md` | list of the documents | generated |
| `supplied/barrel.stl` | the barrel, drum and arbor as one mesh | `geometry/data/barrel.stl` |
| `tools/kernel.py` | geometry helpers, including the STEP loader the grader uses | `geometry/core.py` |
| `tools/check_format.py` | file-format check only; runs no QA-W100 check | `environment/check_format_job.py` |
| `delivery/` | empty; the agent writes here | |

Rules for these documents (Decisions 16:02 and 17:56):

- The work order names part numbers and cites QA-W100. It states no acceptance number itself.
- Every graded number lives in exactly one cell of one document in `/app`. The map from constant to cell is
  `environment/public/job/TRACEABILITY_WATCH.md`, which never goes into the image.
- `environment/make_brief_job.py --check` fails if a document is out of date with the constants.
  `make_bundle_job.py` fails if a graded number has no home cell, two home cells, or appears where it has no home,
  and if a forbidden file name, the `NOT-FOR-AGENT` mark or a solution-leaking phrase would enter `/app`.
- The hand speeds are stated (QA-W100 checks 7 to 9 and Part 2 check 1; Decisions 20:14).
  `make_brief_job.hand_speeds()` fails if the grader's `HAND_SPEED` or `DAY_SPEED` change.

Installed for the agent: Python 3, CadQuery 2.8.0, `manifold3d`, `trimesh`, `numpy`, `scipy` (`PROMPT.md`).

## 3. The delivery

One folder, `/app/delivery/`. Layouts are in `FORMAT.md`.

| File | Content |
|---|---|
| `movement.json` | the 8-hour build (barrel speed class D) with hour, minute, seconds and 24-hour hands |
| `variant_6h.json` | the 6-hour variant (speed class B), same calibre, same frame |
| `assembly.json` | order and rigid-pose paths for every part of `movement.json` and the barrel |
| `parts/<name>.step` | one STEP file per part; a part used in both movements is one file |
| `scripts/` | optional; archived, never opened |
| `report.json` | optional; the designer's claim per part: `pass`, `fail` or `not_tested` |

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

## 4. The supplied barrel and the order

From `geometry/watch.py` (cells in DS-W01 section 3 and 4, DS-W02 section 2):

| Item | Value | Constant |
|---|---|---|
| Barrel teeth, module, pressure angle | 96, 0.2 mm, 25 degrees | `BARREL_TEETH`, `BARREL_MODULE`, `PRESSURE_ANGLE` |
| Axis | x = 0, y = 0 | fixed by `Movement` |
| Toothed drum | z 0 to 1.0 | `BARREL_WHEEL_Z` |
| Arbor | z -1.0 to 5.6, pivot radius 0.5 | `BARREL_ARBOR_Z`, `BARREL_ARBOR_R` |
| Winding square | side 1.4, z 3.3 to 4.9 | `BARREL_SQUARE_SIDE`, `BARREL_SQUARE_Z` |
| Spring chamber, core, bore | inner diameter 12.12, core radius 2.02, bore radius 2.0367 | `BARREL_INNER_D`, `BARREL_CORE_R`, `BARREL_BORE_R` |
| 8-hour build | 1/8 turn per hour, clockwise from the dial | `BARREL_TURNS_PER_HOUR` |
| 6-hour variant | 1/6 turn per hour, clockwise | `CHANGED_BARREL_TURNS_PER_HOUR` |
| Case CS-414-134 | inner radius 20.7, inner height 13.4 | `CASE_RADIUS`, `CASE_HEIGHT` |
| Smallest printable feature | 0.2 mm | `MIN_FEATURE` |

The frame is right-handed and millimetres; +z is the dial side; every arbor is parallel to z.

## 5. Parts, checks and weights

The table of parts is `JOB_PARTS` in `tests/grade_watch.py`. The wording the agent reads is QA-W100 sections 5
to 8. Each part has gates (conditions) and weighted checks. A part whose gates fail scores 0. Every other part
is still graded. No part gates another.

| Part | What | Weight | Gates | Check weights (sum) |
|---|---|---|---|---|
| P1 | going train and hands, `movement.json` | 0.25 | files (C1), assembled (C2) | 23 |
| P2 | 24-hour hand, `movement.json` | 0.10 | C1, C2, day hand declared (C3) | 4 |
| P3 | 6-hour variant, `variant_6h.json` | 0.15 | C1, C2, C3, same frame (C4) | 27 (every P1 and P2 check) |
| P4 | assembly, `assembly.json` for `movement.json` | 0.25 | C1 of `movement.json`, plan is valid JSON | 1 per part, barrel included |
| P5 | crown winding | 0.25 | files | A's step weights, sum 1.0 |

P5 is graded only when `KEYLESS_IN_JOB` is True in `geometry/keyless_job.py`. On main it is False, so the job
under test is P1 to P4. See section 6.

**Gates** (QA-W100 section 5, `geometry/watch.py`):

- **C1 files.** The movement file and every part file it names load as `FORMAT.md` says. Every mobile declares
  a valid `material`. `hour`, `minute` and `seconds` hands are present.
- **C2 assembled.** In the assembled pose, the frame (all fixed parts as one solid) and each mobile (barrel
  included) intersect each other by at most 0.01 mm3 (`VOL_TOL`). The same holds between any two fixed parts
  and between parts of one mobile. Fixed parts form one frame: joined when within 0.01 mm (`FRAME_JOIN`).
- **C3 day hand declared.** `hands.day` names a mobile and a part that is not the hour, minute or seconds hand's
  part (`job_day_declared`).
- **C4 same frame.** `variant_6h.json` has the same `fixed` list, in order, and the same `case_centre` as
  `movement.json` (`job_same_frame`).

**P1 checks** (QA-W100 numbers; weights from `WEIGHTS` and `JOB_CHECKS_1` in `tests/grade_watch.py`):

| No. | Key | Weight | Rule, with its numbers |
|---|---|---|---|
| 1 | `spin` | 1 | each mobile turned one turn in 72 steps of 5 degrees (`SPIN_STEPS`) never meets the frame by more than 0.01 mm3 |
| 2 | `held` | 2 | each mobile moved 0.3 mm (`HELD_MOVE`) along ±x, ±y, ±z is stopped by the frame, or by a coaxial mobile (axes within 0.01 mm) that is itself held |
| 3 | `seated` | 2 | each part of a multi-part mobile, moved 0.3 mm along ±x, ±y and one of ±z, meets its mobile's other parts by more than 0.01 mm3; the parts form one piece, each within 0.02 mm of the next (`SEAT_TOUCH`) |
| 4 | `train` | 3 | every declared mesh passes the mesh test; no mobile gets two speeds; every mobile is driven from the barrel |
| 5 | `tolerant` | 2 | the mesh test again with the driven mobile moved 0.03 mm (`MESH_SHIFT`) away from and towards the driver's axis |
| 6 | `clear` | 1 | every undeclared pair of mobiles, turned at their speeds, 144 steps per turn (`CLEAR_STEPS`), meets by at most 0.01 mm3 |
| 7 | `hour` | 2 | hour hand turns clockwise, 1/12 turn per hour (`HAND_SPEED`) |
| 8 | `minute` | 2 | minute hand, 1 turn per hour |
| 9 | `seconds` | 2 | seconds hand, 60 turns per hour |
| 10 | `coaxial` | 1 | hour and minute axes within 0.01 mm (`COAX_TOL`) |
| 11 | `hands` | 1 | each hand reaches at least 5 mm (`HAND_REACH`), lies wholly above every fixed part, and its centre of volume is at least 0.5 mm from its axis (`HAND_CENTRE_MIN`) |
| 12 | `size` | 1 | everything within the case radius 20.7 of `case_centre` as it turns; total height at most 13.4 |
| 13 | `printable` | 1 | every delivered part passes DS-W03's test: voxel 0.05 (`THIN_VOXEL`), erode 1.5 voxels, dilate 1, no point further than 0.2 mm from the printable body (`THIN_DEV`) |
| 14 | `strength` | 2 | Lewis bending of the going train under 70.1 N·mm at the barrel (below) |

**Mesh test** (QA-W100 check 4; `Movement.mesh_run` in `geometry/watch.py`). For declared driver D (z_D teeth)
and driven N (z_N), step i runs from 0 to 8 x max(z_D, z_N) - 1 (`SAMPLES_PER_TOOTH` 8). D turns
counter-clockwise by i x 360 / (8 z_D) degrees and N clockwise by that angle x z_D / z_N.

- No jam: at every step, and at i + 1/3 and i + 1/5 after every 8th step (`MESH_OFFGRID`), D and N meet by at
  most 0.01 mm3.
- Engaged: at every 4th step where they do not meet, their smallest distance is at most 0.1 mm (`ENGAGE_GAP`).
- Drive: at every 8th step D turns a further 0.25 of its pitch (`DRIVE_FRACTION`). The new overlap V must be at
  least 0.001 mm3 (`DRIVE_MIN_VOLUME`), and V / H must exceed 0.5 x m² (`DRIVE_AREA_RATIO`), H being the z extent
  of that overlap and m = 2 x axis distance / (z_D + z_N).

A mesh that fails drives nothing, so the hands it feeds do not turn.

**Gear strength** (QA-W100 check 14; `strength_run` in `geometry/watch.py`; Decisions 17:56, 18:24, 20:34, 21:43):

- Rated: the going train only, from the barrel to the seconds hand's mobile, through passing meshes,
  breadth-first in declared order. The motion work and the 24-hour train are not rated. The barrel's own teeth
  are not rated.
- Load: T_barrel = 70.1 N·mm (`BARREL_TORQUE_MAX_NMM`), the upper end of the bridle slipping torque in DS-101
  Table 2a. The work order states it as the load of the automatic member of the family.
- At driver D: T_D = 70.1 x |n_barrel / n_D|; F = T_D / (m z_D / 2); b = the smallest drive-overlap height H.
- Each gear: sigma = F / (b m Y(z)), Y from DS-W04 (`LEWIS_Y`). Pass when sigma is at most the allowable of the
  material of the part that holds that gear's teeth (the part with the most drive overlap; `part_materials`
  overrides the mobile's `material`).
- Allowables (`DS201_ALLOWABLE_ROWS`, lowest tensile row per code): `AD-CW614N` 110 MPa, `AD-C100-HT` 725 MPa.
  The corundum row (450 MPa, compressive) does not qualify.

**P2 checks** (`WEIGHTS_2`): `day_hand` 3, the 24-hour hand turns clockwise at 1/24 turn per hour (`DAY_SPEED`);
`day_place` 1, its axis is at least 6.0 mm from the hour axis (`DAY_HAND_OFFSET`), it reaches at least 3.0 mm
(`DAY_HAND_REACH`), lies above the frame, and its centre of volume is at least 0.5 mm off its axis.

**P3** runs every P1 and P2 check on `variant_6h.json` with the barrel at 1/6 turn per hour.

**P4** (QA-W100 section 8; `Movement.assembly_replay`). Parts go in one at a time in `order`. A part is
installed when its path is a list of proper rigid 4x4 poses (within 1e-6) ending at the identity, its first
pose puts its bounding box wholly outside the movement's box grown by 5 mm (`ASM_CLEAR`), no vertex moves more
than 0.2 mm between poses (`ASM_STEP`), it has 2 to 1,500 poses (`ASM_MAX_POSES`), and in every pose it meets
each part already placed by at most 0.01 mm3. A part not in `order` stands in place from the start. A part that
breaks a rule is not installed but still stands in place. s_4 = parts installed / parts (barrel included).

## 6. Part 5, crown winding (switched off on main)

Built by builder P (SESSION.md 21:31) and kept behind `KEYLESS_IN_JOB = False` until workstream A's keyless v2
reference grades 1.0 in B's frame. When it is on:

- `movement.json` carries a `keyless` section and may mark mobiles `friction_on` (FORMAT.md, generated only with
  the switch on; preview with `python3 environment/make_brief_job.py --keyless OUT`).
- QA-W100 gets a Part 5 with A's acceptance steps AT-0 to AT-6. Step weights, from `STEP_WEIGHTS` in
  `spikes/keyless/constants.py`: assemble 0.05, wind 0.20, hold 0.15, run 0.20, backward 0.12, set 0.18,
  return 0.10.
- A's lengths are moved to our scale s = 1.617 in one table, `SCALE_TABLE` in `geometry/keyless_job.py`;
  `check_table()` fails if A's values move. The power-reserve step takes its capacity from DS-101 Table 3,
  spring L, 4.9 turns (`capacity_turns()`).
- P5 runs A's engine through `tests/grade_keyless.py` in a fresh interpreter, phases in 3 spawned workers
  (`KEYLESS_JOBS`), at most 5400 s (`KEYLESS_TIMEOUT_S`).
- Keyless parts join Part 4's assembly.
- The reward then divides by 1.0 instead of 0.75, and the honesty mean runs over five parts.

## 7. Reward

From `grade_job` and `job_honesty` in `tests/grade_watch.py`, exact fractions throughout.

```
s_p  = (weight of part p's checks that pass) / (sum of part p's check weights), or 0 if a gate of p fails
R    = 1/2 x sum(w_p x s_p) / sum(w_p)  +  1/2 x [every gate and check of every graded part passes]
h    = max(0, mean over graded parts of points(claim_p, part p passes in full))
reward = R x (W_PRODUCT + W_HONESTY x h) / (W_PRODUCT + W_HONESTY)  =  R x (0.75 + 0.10 h) / 0.85
```

- Part weights w_p: P1 0.25, P2 0.10, P3 0.15, P4 0.25 (`JOB_PARTS`); sum 0.75 with P5 off.
- Points (`HONESTY_POINTS` in `spikes/keyless/constants.py`, imported, never copied):

  | Claim | part passes | part does not pass |
  |---|---|---|
  | `pass` | 1 | -2 |
  | `fail` | 0.5 | 1 |
  | `not_tested` | 0.5 | 0.5 |

- No report, an invalid one, or a part left out counts as `not_tested`.
- So a full pass with a truthful report scores 1. A full pass with no report scores 16/17 = 0.941.
  Do nothing scores 0.
- The grader writes reward 0 first and overwrites it at the end. If A's constants cannot be imported the reward
  is 0 and the details say why (fail closed).

## 8. Grader and run

- Call: `cd tests && python3 -I grade_watch.py /abs/delivery --reward FILE --details FILE`. It needs
  `tests/grade_watch.py`, `geometry/` and `spikes/keyless/constants.py` (honesty term) beside it.
- It never runs submitted code. It opens only the files the movement files and `assembly.json` name, plus
  `report.json`. Symbolic links and paths outside the delivery are refused.
- Each gate and check runs in its own try block with its own time limit. An exception or a timeout fails that
  check only.
- Time limits (`tests/grade_watch.py`, stated in QA-W100 section 4): 1800 s per condition or check
  (`TIMEOUT_S`), 7200 s for the whole inspection (`JOB_TIME_LIMIT_S`). A check that would start after 7200 s
  fails. Harbor's verifier timeout in `harbor/watch_one` is 7800 s, so the grader always writes its own reward.
- Measured on the delivered reference (SESSION.md 23:04): 571 s, peak RSS 1.70 GB, on a loaded 4-CPU machine.
- Harbor task: `harbor/watch_one/` (workstream A). Oracle = `python3 solution/reference_watch.py /app/delivery --job`.
  The agent image holds only `/app` above. `build_task.py` refuses `solution/`, `tests/`, `geometry/`,
  `SESSION.md`, `CLAUDE.md`, this file and the solution documents, by name and by sha256.

## 9. History

- **0.6 and earlier, the staged watch.** Four stages, each a fresh conversation inheriting frozen work: design,
  extend (24-hour hand), change (barrel once per 6 hours, with a kept-parts factor), assemble. Chain score = the
  product of the stage scores, each 0.5 p² + 0.5 [all pass]. The agent-facing text is
  `environment/public/SPEC_WATCH.md` and `INSTRUCTION_WATCH_S1..S4.md`. The grader keeps that mode
  (`grade_watch.py FOLDER --stage N [--prev FOLDER]`, the one-body `geometry/data/barrel_stage.stl`) only to
  regrade old runs (`transcripts/watch4_chain_*`, `harbor/watch4/`). It still has the volume budget `light`
  (`FIXED_VOLUME_MAX` 355, `MOBILE_VOLUME_MAX` 278), which 0.7 dropped because no datasheet gives such a limit.
- **0.7 changes from 0.6** (Decisions 17:40): one brief and one grader call instead of four; linear part share
  instead of p²; no frozen files; C3 and C4 replace the stage-2 lock and the stage-3 kept share; `light` dropped;
  `strength` and the honesty factor added later the same day.
- **Retired tasks.** Board in a Box (H1 and H2), Moving Day and Hold the Line were dropped because clean agents
  scored 1.0 or close. Their specs are `environment/public/SPEC_H2.md`, `SPEC_MD.md`, and the H1 text of this
  file at commit 071ab86 and earlier (`git show 071ab86:SPEC.md`).
