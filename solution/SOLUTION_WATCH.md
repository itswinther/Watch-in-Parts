# Solution: the watch job

NOT-FOR-AGENT. This file gives the answers and the grading margins. It must never be copied into a task image.
`harbor/watch_one/build_task.py` refuses everything under `solution/` by name and by sha256, and the bundle
builder refuses any file with the mark above.

The rules are in `SPEC.md` (version 0.8). The agent's text is the customer order
(`environment/public/job/PROMPT.md`), `FORMAT.md` and the sheets in `environment/public/job/datasheets/`; no
acceptance test is shown. How a designer reaches these answers, step by step, is in `STEP_BY_STEP_WATCH.md`.

Sources: `solution/reference_watch.py` (run as `cd solution && PYTHONPATH=.. python3 reference_watch.py OUT --job`,
no other flags: barrel BR-096-30, one-part mobiles; about 45 s, SESSION.md H 05:21), its constants read by
importing it, the delivery it wrote, and that delivery's grader details (`tests/grade_watch.py OUT --details`,
reward 1.000000, 469.6 s, graded 15 Nov 05:13 Helsinki). Since that grading only `THIN_REFERENCE_MM` changed in
`geometry/watch.py` and `tests/grade_watch.py` (3.35 to 3.95 to 3.85), so the gates, checks and margins are those
of main. Part 5 (crown winding) is switched off (`geometry/keyless_job.py`, `KEYLESS_IN_JOB = False`).

## 1. The answers

There is no single correct design. These are the reference's answers.

| Quantity | Reference |
|---|---|
| Barrel | BR-096-30 (drum z 0 to 0.4545, arbor -0.4545 to 2.5455), both builds |
| Case | CS-254-134; `case_centre` (2.367, 0.6574); radius reached 12.357 of 12.7 |
| Height H | 3.3491 mm, both builds (z -0.4545 to 2.8945) |
| Going train, 8 h | barrel 96 -> third 12; third 42 -> centre 42; centre 90 -> fourth 12; fourth 96 -> seconds 12 |
| Going train, 6 h | the same, but third 36 -> centre 48 |
| Speeds, 8 h (turns per hour, + clockwise) | barrel +1/8, third -1, centre +1, fourth -7.5, seconds +60 |
| Speeds, 6 h | barrel +1/6, third -4/3, centre +1, fourth -7.5, seconds +60 |
| Motion work | cannon 16 -> minute wheel 48; minute pinion 12 -> hour wheel 48: hour +1/12 |
| 24-hour train | hour wheel 48 -> day idler 24; idler pinion 10 -> day wheel 40: day +1/24 |
| Modules | 0.2 (barrel mesh), 0.16 (third/centre), 0.13 (centre/fourth), 0.12 (fourth/seconds), 0.12 (cannon/minute wheel), 0.128 (minute pinion/hour wheel, hour wheel/day idler), 0.16 (day pair) |
| Tooth form | 25-degree full-depth involute, addendum 1 m, dedendum 1.25 m, standard centre distance |
| Materials | AD-C100-HT: third, centre, fourth, seconds, minute_wheel, day_idler. AD-CW614N: hour_wheel, day. No `part_materials` |
| Hands | hour, minute, seconds 5.1 long (reach 5.109); 24-hour 3.1 (reach 3.114); 0.2 thick, 0.6 wide |
| 24-hour dial | day axis 7.370 from the hour axis |
| Report | `pass` for P1 to P4 (true) |

Why each count: the barrel turns clockwise and so must the centre, so two meshes lie between them (the third is
an intermediate). |barrel to centre| is 96/12 x 42/42 = 8 and 96/12 x 36/48 = 6. Centre to seconds:
90/12 x 96/12 = 60. Centre to hour: 16/48 x 12/48 = 1/12. Hour to day: 48/24 x 10/40 = 1/2. Every ratio is
exact. The variant keeps the frame, so it keeps every centre distance: the changed mesh keeps its tooth sum
(42 + 42 = 36 + 48 = 84 at module 0.16). The two motion-work meshes share a centre distance because the hour
wheel is coaxial with the centre: 0.12 x (16 + 48) / 2 = 0.128 x (12 + 48) / 2 = 3.84.

### Axes and centre distances

| Mobile | Axis | Mesh partner, centre distance |
|---|---|---|
| barrel | (0, 0) | third, 10.8 |
| third | (7.681663, 7.591578) | centre, 6.72 |
| centre (and hour wheel) | (8.589106, 0.933129) | fourth 6.63; minute wheel 3.84; day idler 4.608 |
| fourth | (5.425817, -4.893577) | seconds, 6.48 |
| seconds | (-1.011536, -5.635799) | |
| minute_wheel | (7.564436, -2.767635) | |
| day_idler | (7.279518, 5.351119) | day, 4.0 |
| day | (3.354181, 6.120356) | |

### z levels (mm)

| Level | z | Contents |
|---|---|---|
| main plate | -0.4545 to -0.0200 | barrel and third pivots |
| A | 0 to 0.4545 | barrel drum; third pinion (from 0.0200) |
| mid plate | 0.4745 to 0.6745 | lower pivots of centre, fourth, seconds |
| B | 0.6945 to 0.8945 | third wheel, centre pinion |
| C | 0.9145 to 1.1145 | centre wheel, fourth pinion |
| D | 1.1345 to 1.3345 | fourth wheel, seconds pinion |
| bridge | 1.3745 to 1.5745 | |
| E | 1.5945 to 1.7945 | cannon, minute wheel; day idler pinion, day wheel |
| F | 1.8145 to 2.0145 | minute pinion, hour wheel, day idler wheel |
| dial | 2.0345 to 2.2345 | |
| hour hand | 2.2545 to 2.4545 | |
| minute hand | 2.4745 to 2.6745 | |
| seconds, 24-hour hands | 2.6945 to 2.8945 | |

Layers 0.2 (`LAYER_T`), gaps 0.02 (`GAP`), bore clearance 0.005 (`FIT`).

### Part list

`movement.json` names 17 parts; `variant_6h.json` swaps two; `parts/` holds 19 STEP files.

| Kind | Parts |
|---|---|
| fixed (both builds) | main_plate, mid_plate, bridge, dial |
| third | third (8 h); third_54 (6 h: a 36-tooth wheel; the name is a legacy one) |
| centre | centre (8 h) or centre_36 (6 h: a 48-tooth pinion), cannon, minute_hand |
| fourth | fourth |
| seconds | seconds, seconds_hand |
| minute_wheel | minute_wheel |
| hour_wheel | hour_wheel, hour_hand |
| day_idler | day_idler |
| day | day, day_hand |

Assembly order: main_plate, barrel, mid_plate, third, centre, fourth, seconds, bridge, cannon, minute_wheel,
hour_wheel, day, day_idler, dial, hour_hand, seconds_hand, day_hand, minute_hand. Each part is dropped straight
down in steps of at most 0.19 mm, 32 to 48 poses.

## 2. The grader's margins on the reference, smallest first

From the grader details; limits from `geometry/watch.py`. The 8-hour and 6-hour builds give the same values except
where stated.

| Check | Reference value | Limit | Where it binds |
|---|---|---|---|
| hands: lowest point above the highest fixed part | 0.020 | >= 0 | hour hand, one `GAP` over the dial |
| hands: reach | 5.109 | >= 5.0 (`HAND_REACH`) | all three hands |
| size: radius | 12.357 | <= 12.7 (`CASE_RADIUS`) | |
| day_place: reach | 3.114 | >= 3.0 (`DAY_HAND_REACH`) | |
| printable: largest deviation | 0.150 | <= 0.2 (`THIN_DEV`) | centre, fourth, minute_wheel, hour_wheel |
| day_place: axis from the hour axis | 7.370 | >= 6.0 (`DAY_HAND_OFFSET`) | |
| strength: allowable / sigma - 1 | 0.515 | >= 0 | third pinion 12, m 0.2, b 0.4345, sigma 478.5 of 725 MPa, both builds |
| strength, next | 8 h: 1.210 (fourth pinion); 6 h: 0.657 (fourth pinion, sigma 437.5) | >= 0 | the variant's higher centre torque |
| tolerant: smallest drive ratio | 0.792 | > 0.5 (`DRIVE_AREA_RATIO`) | fourth/seconds, shifted away 0.03 |
| tolerant: smallest new overlap | 0.00228 mm3 | >= 0.001 (`DRIVE_MIN_VOLUME`) | fourth/seconds, away |
| tolerant: largest gap | 0.0404 | <= 0.1 (`ENGAGE_GAP`) | fourth/seconds, away |
| train: smallest drive ratio | 1.202 | > 0.5 | minute pinion/hour wheel |
| train: smallest new overlap | 0.00353 mm3 | >= 0.001 | fourth/seconds |
| train: largest gap | 0.0273 | <= 0.1 | barrel/third |
| seated: smallest overlap when moved 0.3 | 0.0338 mm3 | > 0.01 | seconds and day hands on their arbors, sideways |
| held: smallest overlap when moved 0.3 | 0.0383 mm3 | > 0.01 | minute_wheel, day_idler, sideways |
| hands: centre of volume from the axis | 1.44 to 1.58 (24-hour 0.74) | >= 0.5 (`HAND_CENTRE_MIN`) | |
| hands: area share of the swept disc | 0.058 to 0.064 (24-hour 0.118) | <= 0.25 (`HAND_AREA_MAX_SHARE`) | |
| spin, clear, train jams, assembled, P4 | 0.0 mm3 (largest 8.4e-18) | <= 0.01 (`VOL_TOL`) | |
| coaxial | 0.0 | <= 0.01 (`COAX_TOL`) | |
| hour, minute, seconds, day_hand | exactly 1/12, 1, 60, 1/24 | exact | |

## 3. The reward of the reference

- Every gate and every check of P1 to P4 passes: s_p = 1 for all four, share = (25 + 10 + 15 + 25) / 75 = 1,
  all = 1. P4: 18 of 18 parts installed (17 parts and the barrel).
- H = 3.3491 <= 3.85, so x = 0 and s = 1.
- `report.json` claims pass for P1 to P4, all true: points 1 each, h = 1, factor (0.75 + 0.10) / 0.85 = 1.
- reward = (1/2 x 1 + 1/2 x 1 x 1) x 1 = **1.0** (`reward_exact` "1").

Harbor's oracle on the submitted grader gave 1.000 and nop 0.000 (SESSION.md, A 05:49).

## 4. Baselines

| Delivery | Reward | Source |
|---|---|---|
| nothing delivered | 0.000 | `tests/test_anchors_job.py` "job do nothing"; Harbor nop 0.000 (A 05:49) |
| stop early, Part 1 only | 0.157 (8/51) | "job stop-early: Part 1 only" |
| stop early, Parts 1 and 2 | 0.220 (56/255) | "job stop-early: Parts 1 and 2" |
| stop early, Parts 1 to 3, no assembly, truthful report | 0.333 (1/3) | "job stop-early: Parts 1 to 3, no assembly, truthful partial report" |
| the reference without report.json | 0.941 (16/17) | "job gold without a report" |

The three stop-early anchors were re-run on the submitted grader on 15 Nov, 3 of 3 ok
(`python tests/test_anchors_job.py 3 --only "job stop-early"`, SESSION.md H 06:20). They were not re-run for this
file.

## 5. Honest limits

1. **The reference does not run as made.** With every part grown or shrunk by DS-W03's +/- 0.01 mm, the centre
   wheel 90 / fourth pinion 12 jams in the largest state, and in the drawn state with arbors at the far side of
   their holes only one mesh drives (`spikes/asmade/asmade.py --tol 0.01`, both builds; SESSION.md H 05:26). The
   grader does not test this (`WATCH_AS_MADE` unset).
2. **The full-score height is set by another design.** `THIN_REFERENCE_MM` = 3.85 is the height of workstream A's
   design that does run as made at +/- 0.01 (branch `a/thin-asmade` 88904a8: wheel layers 0.16, plates 0.3,
   axial stop gaps 0.022, layer gaps 0.08, SESSION.md A 05:35 and A 05:44; the branch's first version, A 05:02,
   lists modules 0.16 to 0.2, hole clearance 0.021 and backlash 0.027 per gear). It needs case radius 12.766, more than the 12.7 the agent is given, and
   was graded with `THIN_CASE_RADIUS=13.0`. The reference here (3.349) is below the bar, so it gets s = 1 too.
3. **Three grader numbers are in no agent document.** Checked in the code and in the 15 files of the bundle
   (`environment/make_bundle_job.py OUT`, 15 Nov):
   - load factor **1.45** (`geometry/watch.py` `TOOTH_LOAD_FACTOR`; `strength_run` multiplies the nominal Lewis
     load by it). The agent's DS-W04 gives sigma = W_t / (b m Y) with the nominal load and no factor; no sheet
     prints 1.45 as a factor. The order says "runs without oil". The comment beside the constant, which says DS-W04
     states it, is stale;
   - allowables **110 MPa** (AD-CW614N) and **725 MPa** (AD-C100-HT) (`DS201_ALLOWABLE_ROWS`,
     `MATERIAL_ALLOWABLE_MPA`: the lowest tensile row per code). They are half the lowest proof stress, and live in
     section 8 of `spikes/keyless/datasheets/DS-201_materials.md`. The agent's AD-DS-201 has no section 8: it gives
     brass Rp0.2 220 / 350 MPa (230 to 350) and steel proof strength 1450 to 1900 MPa, and no safety factor;
   - the **0.03 mm** shift of `tolerant` (`MESH_SHIFT`). The nearest stated number is DS-W03 section 4's
     +/- 0.01 mm.
   At the stated nominal load (factor 1) the reference's third pinion would be at 330 MPa; a designer who rates at
   factor 1 against the proof stress can deliver teeth the grader fails.
4. **The dial centre is not checked.** The reference's hour and minute axis is 6.23 mm from `case_centre`. No
   document ties "the centre of the dial" to the case centre, and the grader measures the 24-hour offset from the
   hour axis.
5. **One instance.** One order, one case, one barrel catalogue.
