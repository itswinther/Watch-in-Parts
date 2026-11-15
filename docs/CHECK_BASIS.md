# Basis of every one-job check (fairness table)

Written by B on `b/thin-order`, from `origin/b/thin-4mm` 92d9622. Not agent-facing: this file stays out of the
bundle (`docs/` is not copied by `environment/make_bundle_job.py`).

**What this table is for.** The final thin brief gives the agent a customer order and supplier sheets, with no
acceptance test (SESSION.md, 04:05 itswinther via G and 04:16 Mikael via A). The grader keeps its checks, but
every grader rule must follow from one of three sources:

- the **order** (what the customer asks for, in words);
- a **supplier sheet** (a fact a supplier states about a part, a material or a process), or the **delivery
  format** (`FORMAT.md`, the factory's file contract);
- **trade practice** (what a competent movement designer knows without being told).

A rule with none of these as its basis is dropped, or its basis is added to a sheet as a supplier fact.

**Scope.** This covers `tests/grade_watch.py` in one-job mode (`grade_job`, line 715): gates and checks of P1 to
P4, the format rules (C1) and the honesty factor. P5 (crown winding) is off on this branch
(`geometry/keyless_job.py:19`, `KEYLESS_IN_JOB = False`) and is not covered. The thickness score is not computed
by `grade_watch.py`; it is G's (`spikes/thin_probe/score.py`), and it is covered in one row at the end.

**Verdicts.**

- **K**: keep as is.
- **KF**: keep, but add a fact to a sheet or to `FORMAT.md` (named in the row).
- **RO**: keep, but the order must say it (the wording is given).
- **D**: drop.
- **OT**: the grader's number is a designer's derived number. Replace it with an outcome test (G's track 2,
  the watch as made, running). Marked here only; not built here.

File references are `file:line` on 92d9622. `W` is `geometry/watch.py`, `G` is `tests/grade_watch.py`.

## 1. Format rules (gate C1, files) and the delivery contract

| # | What it tests | Constants | Basis | What the agent needs, and whether it still has it | Verdict |
|---|---|---|---|---|---|
| F1 | movement.json, variant_6h.json, assembly.json and parts/*.step are valid: STEP only, one solid, mm, size and triangle limits, meshing, self-union, names, JSON layouts | W:115-132 (MAX_PARTS, MAX_TRIANGLES, MAX_JSON_BYTES, MAX_STEP_BYTES, STEP_*, SELF_UNION_TOL, NAME_RE); W:225-344 (Movement.__init__); W:1035 (load_movement) | Format (factory's file contract) | All in `FORMAT.md` today. Stays. | K |
| F2 | Frame and orientation: arbors parallel to z, dial side +z, clockwise seen from +z, mm; the barrel is the mobile `barrel` on its supplied axis | W:1-3 (module docstring), G:36-37 | Format | **Stated only in QA-W100 section 4 today, not in `FORMAT.md`.** With QA-W100 gone, the agent would not know which side is the dial, so every hand and speed check would rest on a guess. | KF: `FORMAT.md` (frame, dial side, sense of turning) |
| F3 | Every declared mesh is an external spur mesh: the two mobiles turn in opposite senses | W:351-373 (speeds, `-Fraction(ta, tb)`) | Format | Stated only in QA-W100 sections 4 and 5. The format has no way to declare an internal (ring) or a crown gear; one declared as a mesh would get the wrong sense. | KF: `FORMAT.md` (`meshes` are external spur meshes) |
| F4 | Each mobile declares `material` (and optionally `part_materials`), a code that has a tensile design allowable in DS-201 section 8 | W:160-165 (MATERIAL_ALLOWABLE_MPA, MATERIAL_DESIGNATIONS), W:264-283 | Format + DS-201 section 8 | `FORMAT.md` says "a code with a tensile design allowable in DS-201's table of design allowables". If section 8 (calculated allowables with a safety factor) leaves the agent's DS-201 (rule: no margins), that sentence has no referent. | KF: `FORMAT.md` lists the accepted codes itself (AD-CW614N, AD-C100-HT) as the factory's material list |
| F5 | Declared tooth counts equal the counted teeth at the meeting height (a tooth at least 0.1 mm deep); the barrel counts 96 | W:814-838 (tooth_counts), W:95 (TEETH_MIN_DEPTH), W:16 (BARREL_TEETH) | Format (the file must describe the parts truthfully) + barrel sheet (tooth count) | `FORMAT.md`: "the tooth count of the gear on each". The 0.1 mm depth only rules out a faceted disc; every printable tooth is deeper (2.25 m with m at least about 0.09). | K |
| F6 | Hands: `hour`, `minute`, `seconds` required, `day` optional; each names a mobile (not `barrel`) and one of its parts | W:330-344 | Format | In `FORMAT.md`. | K |
| F7 | Time: each condition or check at most 1800 s, the whole inspection at most 7200 s | G:42, G:66 | None of the three (the rig's limit) | Stated only in QA-W100 section 4. A normal design takes minutes (the reference 6 to 10 min), so this binds only on pathological files; the STEP read limit (120 s) is already in `FORMAT.md`. | KF: `FORMAT.md`, one sentence (the factory reads and inspects a delivery in at most 2 h; each part file in at most 120 s) |
| F8 | assembly.json: `order` and `paths`; 4x4 proper rigid matrices; 2 to 1,500 poses; last pose identity; first pose outside the movement's box grown by 5 mm; no vertex moves more than 0.2 mm between poses | W:104-106 (ASM_*), W:1112-1138 (_asm_messages), W:1141 (load_assembly) | Format (the assembly cell's input) | Only the layout is in `FORMAT.md`; rules 1 to 4 are in QA-W100 section 8. They are how the assembly cell reads a path, not a design requirement, so they belong in the contract. | KF: `FORMAT.md` (path rules 1 to 4) |

## 2. Gates

| # | What it tests | Constants | Basis | What the agent needs, and whether it still has it | Verdict |
|---|---|---|---|---|---|
| C2 | Assembled: frame, each mobile (barrel included) pairwise intersect at most 0.01 mm3; no two fixed parts, no two parts of one mobile overlap; the fixed parts form one frame (each within 0.01 mm of the next) | G:106-122; W:72 (VOL_TOL), W:84 (FRAME_JOIN); W:443 (frame), W:466, W:479 | Trade practice: two parts cannot occupy one space; plates, bridges and pillars are one rigid frame | The idea is trade practice. The two 0.01 numbers are drawing noise, and they make the test lenient. What is not trade practice is the drawing convention: a press fit drawn with interference (common in some CAD practice) fails, and fixed parts held by screws not drawn must still touch. | KF: `FORMAT.md` drawing convention (parts drawn in the assembled position at nominal size; parts that are joined are drawn touching, never overlapping; the factory reads intersections below 0.01 mm3 and gaps below 0.01 mm as drawing noise) |
| C3 | 24-hour hand declared, and its part is not the part of another hand (P2, P3) | G:504-511 | Order (a 24-hour hand) + trade practice (each hand is its own part) | The order asks for the hand. | K |
| C4 | Same frame: variant_6h.json has the same `fixed` list in the same order and the same `case_centre` (P3) | G:514-531 | Order (the same calibre on the same frame) | The order must say the variant keeps the frame and its place in the case. "Same order of names" is strict but follows from "the same list". | RO: "the 6-hour variant uses the same frame, the same fixed parts, in the same place in the case" |
| P4 gates | movement.json loads (C1); assembly.json is valid JSON with `order` and `paths` | G:584-610 | Format | In `FORMAT.md`. | K |

## 3. Part 1, going train and hands (and Part 3, the same checks on the 6-hour variant)

Check weights: G:39-40, G:49 (P1 = WEIGHTS without `light`, plus `strength` 2). Not stated to the agent; weights
are scoring, not requirements.

| # | What it tests | Constants | Basis | What the agent needs, and whether it still has it | Verdict |
|---|---|---|---|---|---|
| 1 spin | Each mobile (barrel included) turns a full turn without touching the frame (72 steps plus 1/3 and 1/5 off-grid poses) | G:157-159; W:73-74, W:72; W:375 | Trade practice: every mobile turns freely | Nothing beyond the trade. | K |
| 2 held | Each mobile moved 0.3 mm in any of six directions is stopped by the frame or by a coaxial mobile that is itself held | G:161-164; W:76 (HELD_MOVE), W:101 (COAX_TOL), W:404 | Trade practice: every mobile is held between its bearings; a coaxial wheel can ride on another | 0.3 mm is far looser than real endshake or side shake (0.02 to 0.05 mm), so any held design passes. The real play is G's as-made test. | K (G's track 2 tests the real play) |
| 3 seated | Each part of a multi-part mobile, moved 0.3 mm in +x, -x, +y, -y is stopped by the other parts, and in +z or -z (one of them) too; the parts form one piece (within 0.02 mm) | G:267-273; W:76, W:72, W:90 (SEAT_TOUCH); W:491, W:504 | Trade practice for a wheel on an arbor (located on a diameter, against a shoulder). Not for every joint: a hand pressed on a plain pipe, or a part held only by friction, has no shoulder and fails | In a model with no friction and no drawn interference (C2), "fixed to its mobile" can only mean "located by shape". That is the factory's convention, not trade knowledge. | KF: `FORMAT.md` joining convention (each part of a mobile with several parts sits on the others: located radially and against a seat in at least one axial direction; the factory fixes it there) |
| 4 train | At least one mesh; no mobile gets two speeds; every mobile is driven from the barrel through meshes that drive; every declared mesh drives: counts right (F5), never collides (0.01 mm3), never more than 0.1 mm apart, and a further 0.25 of a pitch of the driver cuts at least 0.001 mm3 into the driven gear with overlap / height > 0.5 m2 | G:166-172; W:72, W:77-82 (SAMPLES_PER_TOOTH, ENGAGE_GAP, DRIVE_FRACTION, MESH_OFFGRID, DRIVE_MIN_VOLUME, DRIVE_AREA_RATIO); W:585, W:702 | Trade practice: the train runs; the gears mesh at their centre distance with small backlash | The numbers are the rig's thresholds, and they are lenient: standard involute teeth at the standard centre distance pass with backlash far under 0.25 of a pitch. "Every mobile is driven" is trade practice (no idle mobile in a going train). External meshes: F3. | K (G's track 2 replaces "drives as drawn" by "drives as made") |
| 5 tolerant | Every mesh still drives with the driven axis moved 0.03 mm towards and 0.03 mm away from the driver | G:174-185; W:91 (MESH_SHIFT) | None stated. The real basis is the print accuracy (a process fact, G) plus the designer's own pivot play | 0.03 mm comes from nowhere the agent can see. Most standard meshes pass it, but a designer cannot know the figure. It is exactly the derived "side shake" number the direction says the designer works out. | OT (G's track 2: shift by the play the agent's own bearings give, under the chosen process's stated accuracy) |
| 6 clear | Two mobiles not declared as a mesh: their swept solids intersect at most 0.01 mm3 (coaxial ones too), whatever their speeds | G:187-208; W:72, W:75 (SWEEP_DZ); W:755 | Trade practice: wheels that do not mesh never touch, also during hand setting, when speeds change | Nothing beyond the trade. | K |
| 7-9 hour, minute, seconds | The hand's mobile turns clockwise at 1/12, 1 and 60 turns per hour through meshes that drive, with no speed conflict | G:36, G:210-214 | Order (hours, minutes, seconds) + trade practice (what each hand does) | The order names the hands; the speeds and the sense are what an hour, minute and seconds hand are. The barrel's speed comes from the order and the barrel sheet (speed class). | K |
| 10 coaxial | Hour and minute mobiles' axes at most 0.01 mm apart | G:216-219; W:101 | Trade practice (hours and minutes on a common centre), order | The 0.01 is numerical: the agent writes one axis for both. | RO: the order says "hours and minutes from the centre" in words |
| 11a hands reach | Hour, minute and seconds hand parts each reach at least 5 mm from their axis | G:221-224, G:232-234; W:100 (HAND_REACH) | **None.** Hand length is set by the dial design, which comes from the customer | Not anticipatable. A thin dress watch usually has a small seconds hand, about 2 to 3 mm long in a case of 12.7 mm inner radius; a 5 mm seconds hand forces central seconds or a large sub-dial. The reference's seconds hand is exactly 5.0 (`solution/reference_watch.py:53`). An expert who follows trade practice can fail this. | RO: the order carries the customer's dial layout (central hours and minutes, the seconds and 24-hour indications, and the hand lengths, at least 5 mm for hours, minutes and seconds). A dial drawing is a customer document. Otherwise D |
| 11b hands above the frame | The lowest point of each hand part is no lower than the highest point of any fixed part | G:224; W:784 (hand_shape) | Trade practice: a closed dial covers the whole movement and the hands turn above the dial, so no fixed part can rise above the hands | Holds for a conventional closed dial, not for a skeleton. This is the rule that caps every fixed part at the hour hand's height in the thin layout. | RO: the order says "a closed dial" in words |
| 11c hands point | Each hand part's centre of volume is at least 0.5 mm from its axis | G:224; W:85 (HAND_CENTRE_MIN) | Trade practice: a hand is a pointer, not a disc | A pointer, even with a counterweight, passes. | K |
| 11d hands slender | Each hand part, seen from the dial side, covers at most 0.25 of the disc its tip sweeps | G:226-229; W:86 (HAND_AREA_MAX_SHARE); W:799 | Trade practice: a hand covering the dial cannot be read | Real hands cover 2 to 8 % of that disc, so 0.25 is lenient for a pointer. It fails when the "hand part" is the pointer printed in one piece with its wheel. `FORMAT.md` says "the part of that mobile that is the hand", which an agent can read either way. | KF: `FORMAT.md` defines the hand part as the pointer alone, a separate part from any wheel |
| 12 size | Everything within the case's inner radius of `case_centre` as it turns; total height no more than the case's inner height | G:236-238; W:35-37, W:60-62 (CASE_RADIUS, CASE_HEIGHT, SMALL_CASE_RADIUS); W:771 | Order (the case) + case sheet DS-W02 (inner radius, inner height) | Supplier facts, stated. | K |
| 13 printable | Each part (not the barrel) passes the print process's printability test (0.05 mm voxels, opening by 1.5 voxels, dilation 1 voxel, no point further than 0.2 mm) | G:262-265; W:107-111 (MIN_FEATURE, THIN_VOXEL, THIN_ERODE_VOX, THIN_DILATE_VOX, THIN_DEV); W:1167 (thin) | Supplier sheet: the print process's sheet (DS-W03 today; the chosen process's sheet once G's process catalogue lands) | The direction allows the supplier to state its own test. 0.2 mm is the supplier's smallest feature; the test as stated is exact. | K (basis becomes "the chosen process's supplier sheet"; G owns DS-W03) |
| 14a strength, load | Load case: T at the barrel = 70.1 N·mm (upper end of the automatic version's bridle slipping torque), the train stalled | W:138 (BARREL_TORQUE_MAX_NMM), W:1358 | Order (the family has an automatic version; rate the train for its barrel) + DS-101 Table 2a (a maker's limits for a real 11 1/2 calibre) | **If torque tables leave the sheets (Mikael, item 1), the 70.1 has no basis.** The agent would derive the chosen spring's torque from its dimensions (LT: about 4.4 N·mm at the elastic limit), 16 times less than 70.1, and fail a check it could not foresee. | KF + RO: the order says the train is shared with an automatic version and names that version's barrel; that barrel's supplier sheet states its bridle slipping torque (a fact a barrel maker states). Otherwise replace the load by the chosen spring's maximum, derivable from its dimensions and its material (M = Rp0.2 h t2 / 6, trade practice) |
| 14b strength, K | The tooth load is 1.45 x the nominal Lewis load (dry meshing) | W:140 (TOOTH_LOAD_FACTOR); DS-W04 section 2 | A's simulation (a/train-sim), stated on DS-W04 as the gear office's factor | A designer's derived number. Under the rule (no K in the sheets) an expert cannot know 1.45; a design rated at K = 1 with a margin under 45 % fails. | OT: grader rates at K = 1 (the textbook Lewis load), or the dry-friction peak is found by G's as-made running test |
| 14c strength, method | Going train = breadth-first path from the barrel to the seconds mobile; m from the centre distance; face width = smallest height of the drive test's new overlap; sigma = F / (b m Y(z)) with Y from `geometry/data/lewis_y.json` (25 degrees, 4 decimals); the part holding the teeth by drive overlap | W:1277 (LEWIS_Y), W:1315 (going_train), W:1340 (teeth_part), W:1358-1416 | Trade practice: Lewis rating of a going train (Shigley 14-1); the tooth form (25 degrees, addendum 1, dedendum 1.25) is the barrel sheet's | Anticipatable in kind. A designer using a textbook 20-degree Y table is on the safe side (20-degree Y values are lower than 25-degree ones). Rating only barrel to seconds is lenient (the motion work is not rated). | K (the Y table may stay as handbook data; K leaves DS-W04, see 14b) |
| 14d strength, allowable | sigma at most the material's allowable = proof stress / 2 (DS-201 section 8: brass 110, steel 725 MPa, the lowest row of a code) | W:147-165 (DS201_ALLOWABLE_ROWS, MATERIAL_ALLOWABLE_MPA) | DS-201 section 8, which is calculated, not a supplier fact (safety factor S = 2 picked from a textbook tier) | The safety factor is the designer's choice. With section 8 removed (no margins), an expert who takes S = 1.5 fails a grader that takes S = 2. | OT: grade against the material's minimum proof stress (a supplier fact, DS-201 sections 3 and 4), with the stated load as the margin; or the order states a required safety factor as a customer requirement |

## 4. Part 2, 24-hour hand (and in Part 3)

| # | What it tests | Constants | Basis | What the agent needs, and whether it still has it | Verdict |
|---|---|---|---|---|---|
| P2.1 day_hand | The 24-hour hand's mobile turns clockwise once in 24 h, through meshes that drive | G:37, G:240-244 | Order (a 24-hour hand) + trade practice (what a 24-hour hand does) | Nothing beyond the order. | K |
| P2.2 day_place | Axis at least 6 mm from the hour axis; reach at least 3 mm; above the frame; centre of volume at least 0.5 mm off axis; slender (0.25) | G:246-252; W:102-103 (DAY_HAND_REACH, DAY_HAND_OFFSET), W:85-86 | 6 mm and 3 mm: **none** (dial design). The rest as 11b to 11d | Where the 24-hour sub-dial sits and how long its hand is are the customer's dial design. A 24-hour hand on the centre (GMT style) is ordinary trade practice and fails here. | RO: the dial layout in the order (the 24-hour hand on its own sub-dial, its centre at least 6 mm from the centre, its hand at least 3 mm long). Otherwise D |

## 5. Part 4, assembly

| # | What it tests | Constants | Basis | What the agent needs, and whether it still has it | Verdict |
|---|---|---|---|---|---|
| P4 | One check per part of movement.json (barrel included): installed when its path obeys the path rules (F8) and in every pose it intersects every part placed before it by at most 0.01 mm3; a part not in `order` stands in place from the start | G:584-616; W:555-583 (assembly_replay), W:72 | Trade practice: a part goes in without passing through parts already in place. Format: how a path is read (F8) | Rule 5 is the trade; rules 1 to 4 must move to `FORMAT.md` (F8). That a part missing from `order` stands in place from the start is a reading rule. | KF: `FORMAT.md` (F8, and the missing-part rule) |

## 6. Honesty factor and the other scoring

| # | What it tests | Constants | Basis | What the agent needs, and whether it still has it | Verdict |
|---|---|---|---|---|---|
| H1 | report.json states `pass`, `fail` or `not_tested` per part P1 to P4; each claim gets points against the truth (pass and true 1, pass and false -2, fail 0.5 or 1, not_tested 0.5); reward x (0.75 + 0.1 h) / 0.85 | G:859-934; `spikes/keyless/constants.py:70-77` (W_PRODUCT, W_HONESTY, CLAIMS, HONESTY_POINTS, REPORT_MAX_BYTES) | None of the three as it stands: P1 to P4 are QA-W100's parts, and the points table is the rig's scoring rule | **With QA-W100 out, the agent does not know what P1 to P4 are or what "passes in full" means.** Stating the result of each deliverable truthfully is ordinary practice (a release note: what was tested and what works). The asymmetric points (-2 for a false pass) are a scoring rule and need not be shown, but the agent has to know what it is asked to state. | RO: the order asks for a statement per deliverable, named in the order's own words (P1 the 8-hour build's train and hands, P2 its 24-hour hand, P3 the 6-hour variant, P4 the assembly plan), each "works", "does not work" or "not tested"; `FORMAT.md` maps them to the keys. The points table stays grader-side (judgment call for the humans) |
| H2 | report.json `height_mm`: recorded, changes nothing | G (not read beyond `parts`) | None needed | `FORMAT.md` defines it by "QA-W100 section 9". | KF: `FORMAT.md` defines the height itself (highest minus lowest point along the axis of every part and the barrel, the taller build) |
| S1 | Part weights 25/10/15/25, check weights, 1/2 share + 1/2 all-pass | G:39-40, G:49, G:59-65, G:796 | Scoring, not a requirement | Need not be stated. | K |
| S2 | Thickness score (G's, `spikes/thin_probe/score.py`): today x = (H - 4.0) / (C - 4.0), s = (1 - x)^4; to become relative to the house design | W:43-45 (THIN_TARGET_MM, THIN_SCORE_EXPONENT, THIN_SCORE_SHARE) | Order ("as thin as possible", in words) | The target and the formula are what models stopped at. They leave the agent's text (this branch); the scoring is G's. | RO: order says "as thin as you can make it" with no number; the target and formula leave every agent document |

## 7. Counts and the rows that are not "keep"

Rows: 37 (F1 to F8, 4 gate rows, 18 Part 1 rows counting 11a to 11d and 14a to 14d separately, 2 Part 2 rows, 1
Part 4 row, H1, H2, S1, S2).

| Verdict | Count | Rows |
|---|---|---|
| K | 16 | F1, F5, F6, C3, P4 gates, 1 spin, 2 held, 4 train, 6 clear, 7-9 hands' speeds, 11c, 12 size, 13 printable, 14c, P2.1, S1 |
| KF | 10 | F2, F3, F4, F7, F8, C2, 3 seated, 11d, P4, H2 |
| RO | 7 | C4, 10 coaxial, 11a reach, 11b above, P2.2 day placement, H1, S2 |
| KF + RO | 1 | 14a strength load |
| OT | 3 | 5 tolerant (0.03 mm), 14b K = 1.45, 14d allowable with S = 2 |
| D | 0 | (11a and P2.2 fall to D if the humans do not want a dial layout in the order) |

(16 + 10 + 7 + 1 + 3 = 37; the hour, minute and seconds speeds are one row.)

**Rows a careful expert could not anticipate from the order, the sheets and trade practice as they will stand
once QA-W100 leaves:**

1. **11a, P2.2 hand lengths and the 24-hour hand's place (5 mm, 3 mm, 6 mm).** Dial design, not movement trade
   knowledge. A small seconds hand or a central 24-hour hand is what an expert would draw for a thin dress
   watch, and both fail. Needs the customer's dial layout in the order, or drop.
2. **14a the 70.1 N·mm load.** Without a torque figure anywhere, the derivable spring torque is about 16 times
   lower. Needs the automatic barrel's bridle torque on a supplier sheet and the order naming the family.
3. **14b K = 1.45 and 14d S = 2.** Designer's derived numbers; replace (K = 1 and the proof stress, or G's
   as-made test).
4. **5 tolerant 0.03 mm.** A derived play value; G's as-made test replaces it.
5. **H1 honesty.** The agent must know what it is stating. Name the four statements in the order.
6. **F2, F3, F8, C2, 3, 11d.** Conventions that today live in QA-W100 (dial side, external meshes, path rules,
   drawing and joining conventions, the hand part). They move to `FORMAT.md`, the factory's contract, worded as
   how the factory reads files, not as checks.

**The rows flagged in the brief, in short.** Hand-area share 0.25: keep, lenient, but define the hand part in
`FORMAT.md` (11d). Hand reach: no basis, dial layout or drop (11a). Drive ratio thresholds: keep, rig thresholds
that standard gearing passes (4). 0.01 mm3 limits: keep, drawing noise, state the drawing convention (C2). 0.2 mm
printability: keep, the supplier's own test (13). Honesty report: reword (H1).

## 8. Grader changes these verdicts imply (not made here)

1. `tests/grade_watch.py` `hands` and `day_place`: keep the 5 / 3 / 6 mm only if the order carries a dial layout;
   otherwise drop the reach and offset conditions (W:100, W:102-103).
2. `geometry/watch.py` `TOOTH_LOAD_FACTOR` (W:140): 1.0, or replaced by G's as-made peak force.
3. `geometry/watch.py` `MATERIAL_ALLOWABLE_MPA` (W:147-165): proof stress (brass 220, steel 1450 MPa, lowest row),
   or the order states S = 2; `check_strength_sheets()` (W:1280) reads the rows it uses.
4. `geometry/watch.py` `BARREL_TORQUE_MAX_NMM` (W:138): keep 70.1 only with a stated basis (automatic barrel
   sheet, order); `check_strength_sheets()` then reads it from that sheet.
5. `tolerant` (G:174, W:91): replaced by G's as-made test.
6. Honesty (G:859-934): no code change if the order names the four statements; `FORMAT.md` keeps the keys P1 to P4.

Not verified: nothing was run for this table beyond reading the code; the claims "standard gearing passes the
drive thresholds" and "real hands cover 2 to 8 % of their disc" are estimates, not measured on model deliveries.

## 9. What the customer-order brief does with these verdicts (`environment/brief_order.py`, b/thin-order)

Done in the agent's text (no grader change):

- **F2, F3, F7, F8, C2, 3, 11d, P4, H2**: `FORMAT.md` has a section "How the factory reads the files" (frame and
  dial side, the barrel mobile, the drawing convention with 0.01 mm3 and 0.01 mm, fixed parts joined into one
  frame, a mobile's parts each on its seat, the hand part is the pointer alone, external spur meshes, the reading
  time 7,200 s and 1,800 s), the assembly path rules 1 to 4, and `height_mm` defined on its own.
- **F4**: `FORMAT.md` lists the accepted ordering codes (AD-C100-HT, AD-CW614N); DS-201 section 8 is gone.
- **C4, 10, 11a, 11b, P2.2**: the order states the same frame in the same place, hours and minutes on the centre,
  a closed dial, and the customer's dial (hands at least 5 mm; the 24-hour hand on its own small dial, centre at
  least 6 mm from the centre, hand at least 3 mm). `DIAL_IN_ORDER = False` takes the dial out.
- **14a**: the order names the automatic family and cites VM-DS-101 Table 2a, which stays on the agent's DS-101
  (maker's limits); Tables 2, 3 and 4 (calculated) are gone.
- **14b**: DS-W04 has no K. **14d**: DS-201 has no safety factors or allowables. Both are now grader numbers
  that the agent cannot know: the grader changes in section 8 above are still to be made.
- **H1**: the order names the four statements (P1 to P4) in its own words.
- **S2**: no target or formula anywhere; "as thin as you can, the thinner the better".
- QA-W100 is not in the folder. TRACEABILITY_WATCH.md lists every graded number that is no longer stated, with
  its row here.
