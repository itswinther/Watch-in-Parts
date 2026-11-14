# Brief and datasheet review (A and B, 15 Nov 2026)

Shared file for both workstreams' reviews of everything the agent sees: the work order and PROMPT, FORMAT.md, QA-W100, the DS-W datasheets (B), and the crown-winding brief and DS-101..DS-501 (A). Each side appends findings under its own heading; decisions go at the bottom and in SESSION.md Decisions. Not shown to the agent (keep it out of every bundle; it is not under environment/public/).

**The two failure modes (from the judging rubric):**
- **Over-giving** kills the gap: the documents hand over the solution to the hard part (values that pin the design, how a mechanism must be built rather than what it must do, every test threshold so self-checking is trivial, the reference's choices leaking through examples). Ask: would a real job's documents contain it?
- **Under-giving** makes the gap unfair (difficulty scores zero): something the grader checks is not stated or derivable (threshold, convention, sign, unit, frame, tolerance, limits, format), trick wording, or numbers that disagree between documents.

**Format for each finding:** document:line or a short quote; over- or under-giving; effect (gap, difficulty); in real job documents? yes/no; the proposed edit (exact wording); owner (A or B).

**Deadline:** edits must land before the final model runs (target: decided by 02:30, merged by 03:00), because changing the brief after the runs makes them stale.

## A's findings
A's reviewer, 00:55 (read-only; origin/main and a/keyless-engine-fixes at af355d9). Owners: `environment/brief_keyless.py`, `make_brief_job.py`, `public/job/*` = B; `spikes/keyless/*` (grade.py, PROMPT.md, datasheets) = A.

### Brief review: over-giving and under-giving (read-only, origin/main 69b5d0e, origin/a/keyless-engine-fixes af355d9)

Scope read: `environment/public/job/` (PROMPT, FORMAT, QA-W100, DS-W01..W04, INDEX), `environment/brief_keyless.py`
(the Part 5 text the joined job will print when `geometry/keyless_job.py KEYLESS_IN_JOB = True`), `geometry/keyless_job.py`,
`spikes/keyless/docs/PROMPT.md` (main and branch), `spikes/keyless/datasheets/DS-101..501` (main and branch),
`spikes/keyless/grade.py` + `constants.py` (branch), `tests/grade_watch.py`, `spikes/keyless/docs/SOLUTION.md`,
`spikes/keyless/reference.py`, SESSION Decisions 13:36 / 13:50.

Key structural fact: the joined job's Part 5 text is **not** `spikes/keyless/docs/PROMPT.md`; it is
`environment/brief_keyless.py qa_part5()` + `format_keyless_block()/format_text()` on main. That text was written
from the *older* spike brief. The numbers in it are pulled from `constants.py` (so they update on merge), but the
prose about how the rig behaves does not. Several findings come from that.

Legend: OVER = gives away the solution; UNDER = something graded is not stated, or is stated wrongly.
"Real docs?" = would a real watchmaker's job documents contain it.

---

#### A. Ranked findings

##### 1. UNDER (contradiction): joined Part 5 rig text describes the old engine — HIGH (difficulty, and possibly a fake gap)
`environment/brief_keyless.py:152-154` (QA-W100 Part 5, **Springs**):
> "They give way first when pushed; if they cannot give way, they are pushed along like any body. They return
> towards rest until they touch something; their springs never drive other bodies."

The engine on `a/keyless-engine-fixes` (5086722, F1/F2) does the opposite: a returning spring pushes free/spring
bodies in its path ("This is what lets a yoke spring return the sliding pinion through the yoke", SOLUTION.md),
gives way only in the pushed direction, and a free rider of a turning carrier (an `on_stem` free sliding pinion)
yields first like a spring. The branch's `spikes/keyless/docs/PROMPT.md:146-168` already says this; the joined
text does not. Also missing from the joined text: the **Fits** rule (0.005 mm radial play on every bore of a
turning axis, PROMPT.md:143-145), the **"What the rig does not model"** paragraph (rigid parts; every axis fixed in
the frame except riders), the settle-before-rest rule for AT-0 (`brief_keyless.py:167` still says "At rest, as
delivered"), and AT-2's extension to `HOLD_MAX_STEPS`.
- Effect: an agent that reads the joined brief is told the realistic design (yoke spring returning the sliding
  pinion via the yoke) cannot work, and is steered to a sprung sliding pinion (see finding 2). Any failure an
  agent makes because it believed this text is a document fault, not an agent fault: it fails the
  "information available" test of the difficulty criterion and is visible to a judge who compares brief and engine.
- Real docs? A real rig/QA description would describe the rig as it actually behaves: yes.
- Edit (in `qa_part5`, replace the **Springs** bullet, and add three bullets after **Mainspring**):
  > - **Springs.** Spring-loaded mobiles (`spring`) are urged towards their rest side by springs much lighter than
  >   the mainspring. They give way first when pushed, and only in the direction the contact pushes them; if they
  >   cannot give way, they are pushed along like any body. Between steps they return towards rest. On the way
  >   they push along any `free` or `spring` mobile in their path, but never the frame, the stem, the barrel
  >   arbor, or another spring away from its own rest side; where they cannot push, they stop.
  > - **Riding on the stem.** A mobile declared `on_stem` turns with the stem. While the stem turns, a `free`
  >   `on_stem` mobile is light along its slide: where a contact pushes it that way within the friction rule, it
  >   gives way first, like a spring. If it cannot give way, or giving way would push a body behind it into
  >   something that cannot move, it drives what it touches.
  > - **Fits.** The rig gives every bore around a turning body's declared axis (a `rot` mobile, the stem, the
  >   barrel arbor) {FIT_CLEARANCE x S} mm of radial play, in that body's own parts and in any part it turns in.
  >   Parts may be drawn line to line at a pivot. Nothing else is changed.
  > - **What the rig does not model.** Parts do not bend: a flexing arm or blade is rigid on the rig. Every axis
  >   and slide line is fixed in the frame, except that an `on_stem` mobile turns with the stem. A spring has no
  >   body of its own: it acts on other bodies only through its own mobile pushing them by contact. A design that
  >   depends on anything else of this kind will not behave on the rig as it would in metal.
  And `brief_keyless.py:160` / `:167`: "At the start of each step below, the rig first lets the movement come to
  rest: each mobile clears its overlaps within {settle} mm of surface travel, meshing wheels are turned into their
  gaps, and the springs return their parts." / "0. **AT-0 Assemble.** Once the rig has let the movement come to
  rest, no two bodies intersect by more than {tol} mm3. ..."
  (Check first that the joined adapter `keyless_job.build_world` really passes `carrier` only for `on_stem`; if B
  later exposes rot carriers, add the `carrier` sentence from the branch PROMPT.)

##### 2. OVER: the joined FORMAT example is the reference's own keyless declaration — HIGH (gap)
`environment/brief_keyless.py:83-94` (`format_keyless_block`, printed into FORMAT.md):
```
"mobile_name": {"kind": "free", "dof": "rot", "point": [x, y, z], "direction": [dx, dy, dz], ...},
"mobile_name": {"kind": "spring", "dof": "slide", "direction": [dx, dy, dz], "rest": 1, "on_stem": true, ...},
```
The second line is exactly the reference's sliding pinion (`spikes/keyless/reference.py:219-220`:
`"sliding_pinion": {"kind": "spring", "dof": "slide", "direction": [1,0,0], "on_stem": True, "rest": ...}`). It
tells the agent "the clutch is a spring-loaded slide riding on the stem", i.e. the architecture of the hard part.
Combined with finding 1's stale "springs never drive other bodies", it is the path of least resistance. The
spike brief deliberately avoided this ("Example of the format only (one wheel turning on a bracket; not a keyless
design)", PROMPT.md:96-107); Decision 16:10 (1) asked FORMAT.md to stay neutral for the same reason.
- Real docs? A file-format sheet would show a neutral example: no.
- Edit: replace the `mobiles` example with one neutral entry and keep the field definitions as they are:
  ```
    "keyless": {
      "stem":  {"parts": ["part_name", ...], "point": [x, y, z], "direction": [dx, dy, 0]},
      "arbor": {"parts": ["part_name", ...]},
      "mobiles": {
        "mobile_name": {"kind": "free", "dof": "rot", "point": [x, y, z], "direction": [0, 0, 1],
                        "parts": ["part_name", ...]},
        ...
      }
    },
  ```
  The prose bullet (`format_text`, lines 112-119) already defines `spring`, `slide`, `rest` and `on_stem`, so
  nothing the agent needs is lost.

##### 3. UNDER (hidden rule): AT-3 also fails whenever AT-2's hold fails — HIGH (difficulty, reward integrity)
`spikes/keyless/grade.py` (branch) line 478-479: AT-3 `ok = reserve >= RESERVE_MIN and fr_bl == 0 and cb == 0 and
coupled > STILL_TOL and runback <= CLICK_RUNBACK and drift <= HELD_DRIFT`. The last two terms are AT-2's
criteria. Neither text says so: `brief_keyless.py:181-187` (joined) and `PROMPT.md:217-226` (spike) list only
reserve, free run, still coupled. Both texts also say "Each step is judged on its own". So a click that runs back
40 degrees (AT-2 fail) also fails AT-3 even when its reserve, (4.9 - 40/360) x 8 = 38.3 h, passes the stated
AT-3 test. Same for `pw_bl` (the rig's own 45-degree prewind being blocked): it fails AT-2 but is stated only as a
starting state.
- Effect: one design fault is charged twice (0.15 + 0.20 of Part 5's step share), without the agent being able to
  know; a judge tracing a failed AT-3 to the brief finds nothing. Also contradicts "judged on its own".
- Real docs? Yes, a real test procedure states its pass criteria.
- Edit, one of (prefer a: no grader change on the night):
  a. Add to AT-3 (joined `brief_keyless.py:181`, spike `PROMPT.md:217`): "AT-3 counts only from a movement that is
     held: if the arbor ran back more than {rb} degrees in AT-2, or moved more than {hd} degree over its last {hl}
     steps, AT-3 fails." And to AT-2: "If the rig's own winding of the arbor by {prewind} degrees is blocked, AT-2
     fails."
  b. Or drop `and runback <= C.CLICK_RUNBACK and drift <= C.HELD_DRIFT` from AT-3 in grade.py (the reserve term
     already charges the run-back). Needs an anchor rerun.

##### 4. UNDER (two-hop inference): the arbor's winding sense in the joined job — MEDIUM (difficulty)
`brief_keyless.py:146`: "The arbor winds when it turns in the barrel's running sense (DS-W01, section 4)." Correct
(arbor and drum turn the same way), and DS-W01 §4 says "clockwise, seen from the dial side", QA §4 says dial side
is +z. But it is a two-document hop through a fact many people get backwards, and "mechanism wound the wrong way"
is one of the observed GPT failures. The spike brief states it directly (PROMPT.md:52-53).
- Real docs? Yes, a drawing would carry the winding arrow.
- Edit: "The arbor winds when it turns in the barrel's running sense (DS-W01, section 4): clockwise, seen from
  the dial side (+z) looking towards -z. The mainspring urges it the other way."
  This is a statement of a supplied part's fact, not a method hint.

##### 5. UNDER (stale prose, numbers drift): AT-5 position 1 rule — MEDIUM
`brief_keyless.py:195-196`: "At position 1 the forward test turn winds and does not set". The branch engine judges
"winds" over a separate `COUPLED_TURN` (90 deg) turn, not over the 24-degree test turn (grade.py:503-513, spike
PROMPT.md:240-242). With the stale text a design with normal Breguet slack (up to one pitch, ~30 deg) reads as
failing; an agent may distort its clutch to remove backlash.
- Edit (joined): "At position 1 the forward test turn does not set, and a forward turn of {ct} degrees from there
  (never blocked) winds the arbor by more than {still} degree. At position 2 the forward test turn does not wind;
  that it sets is judged by the turns below." Same for AT-2's wording: "let go for {hs} steps, or longer while the
  arbor is still running back (up to {hmax} steps, or until it has run back more than {rb} degrees)".

##### 6. UNDER (number disagreement between branches): stem travel row — MEDIUM-LOW (merge hazard)
`spikes/keyless/datasheets/DS-401_crown_stem.md:52` on main: "Travel from position 1 (winding) to the setting
position (0.30 to the date position, then 0.50) | 0.80 mm | **1.294 mm**". On the branch: "Stem travel between
adjacent positions | 0.80 mm | **1.29 mm**". The grader uses 1.294 (`keyless_job.SCALE_TABLE`), and
`brief_keyless.TRAVEL_ROW` cites main's row text verbatim, so merging the branch sheet either breaks
`make_brief_job --check` or ships "1.29" against a graded 1.294. The branch wording is also wrong for SW200-1 (0.30
+ 0.50 are adjacent steps; 0.80 is the total). Main's parenthetical is also confusing for a two-position calibre
(an agent may read the no-date travel as 0.50 x s).
- Edit (keep main's number, clarify): "| Travel from position 1 (winding) to position 2 (setting), two-position
  stem | 0.80 mm | [^sel] | **1.294 mm** |" and move "(SW200-1: 0.30 to the date position, then 0.50)" into the
  [^sel] footnote. Do not merge the branch's row.

##### 7. OVER (mild): DS-401 names the clutch's working method — MEDIUM-LOW (gap); optional
`DS-401_crown_stem.md:57-58`: "**Backward turning:** the sliding pinion's Breguet teeth slip, so nothing reaches
the barrel or the click." A stem supplier's sheet would not describe the calibre's clutch. It names the part
(sliding pinion), the tooth form (Breguet) and the behaviour that makes AT-4 pass. Counter-evidence: GPT still built
a clutch that cannot slip backward with this line present, so it is not single-handedly closing the gap. Fairness:
the requirement is already in AT-4; the method is standard horology (but the public-domain texts are excluded from
the joined bundle, `make_bundle_job.FORBIDDEN_NAMES`, and the sandbox has no web).
- Real docs? No.
- Edit: delete the bullet (AT-4 states the requirement). If the team prefers to keep a supplier-ish note:
  "**Backward turning:** the stem itself takes no load when the crown is turned backward; what the keyless works
  do then is the calibre's design." Recommend leaving this until after tonight's runs: removing it changes the
  documents that the 0.95 / 0.1-0.4 numbers were measured on.

##### 8. UNDER: agent time limit not stated in the joined brief — LOW-MEDIUM
`environment/public/job/PROMPT.md:69-71` ("The job ends when you stop.") states no limit; the task enforces
`AGENT_TIMEOUT_SEC = 10800` (`harbor/watch_one/build_task.py:99`). The spike brief states its budget. With Part 5
added the job is much larger; an agent cut off by an unstated limit is an "impossible timing" failure.
- Real docs? Yes (a deadline).
- Edit: "You have up to 3 hours; what is in `/app/delivery/` when you stop, or when the time is up, is delivered."
  Also confirm per run that no trial hit the timeout.

##### 9. UNDER: Part 5 rig cost vs the 5400 s / 7200 s budget — LOW-MEDIUM (verifier side)
`brief_keyless.py:203-204` and QA §4: Part 5 gets at most 5400 s and never past the whole run's 7200 s, after
Parts 1-4 (6-10 min idle, more under load). Rig time depends on the agent's triangle counts and number of contact
bodies, which the agent cannot measure. A heavy but correct design could fail steps by timeout. Not a document
fix: check the slowest GPT/Claude delivery's Part 5 wall time under the real verifier and keep the limits >= 3x it.

##### 10. UNDER (format example incomplete, Parts 1-4): `material` missing from the JSON layout — LOW
`FORMAT.md:47-65` shows a mobile as `{"axis": [x, y], "parts": [...]}`; line 72-75 then says a mobile without
`material` makes the file not valid. Claude read it (10/10), but it is the kind of inconsistency a judge notices.
- Edit (in `make_brief_job.format_sheet`): `"mobile_name": {"axis": [x, y], "parts": ["part_name", ...],
  "material": "ordering code"},`.

##### 11. UNDER (small): joined `rest` definition lacks the zero point — LOW
`brief_keyless.py:115-117` defines `rest` as "the sign of the mobile's own coordinate ... that its spring urges
it towards" but never says the coordinate is zero as delivered (spike PROMPT.md:82-84: "A mobile's own coordinate
is zero as submitted"). Edit: add "A mobile's own coordinate is zero in its delivered position."

##### 12. Number disagreements that are not graded (cosmetic) — LOW
DS-201 corundum compressive allowable 450 (main) vs 900 (branch), DS-301 jewel p_max 450 vs 900 and Table 4. Not
used by any check (check 14 excludes compressive rows). Pick one before the bundle is frozen so a judge does not
see two versions; TRACEABILITY.md:306 already flags it as open.

---

#### B. Looked at and recommend leaving alone

| Item | Why leave it |
|---|---|
| QA-W100 Parts 1-4 states the mesh test, held test, etc. algorithmically (QA-W100.md:93-195) | Over-specified for a real QA sheet, but Parts 1-4 have no gap to protect (10/10 at 1.0), and removing graded detail now creates under-giving. Team decision 13:36 was "every graded number stays". |
| Part 5 thresholds stated (WIND_BAND 3-12, run-back 30 deg, SET_MIN, STILL_TOL, friction 0.51/0.44) | Real requirements a watchmaker would get (winding ratio, click recoil, setting must move the hands). Self-checking them needs a contact simulator the agent does not have, so stating them does not make Part 5 trivially checkable. Friction is needed to size ramp and click angles. |
| `on_stem` field itself (FORMAT) | It is tool vocabulary the rig needs; without it no sliding clutch can be expressed. Only the example (finding 2) leaks. |
| DS-501 §5 "winding torque ... is the largest mainspring torque divided by the gear ratio" | Standard engineering statement; consistent with WIND_BAND; not graded (engine has no torques). |
| DS-W02 case sized from the reference (watch.py:34 "reference reaches 20.354 ... plus 0.3") | A constraint, not a giveaway; the case is a given item in a real job. Check only that the keyless reference still fits 20.7 / 13.4. |
| Tooth counts, module, ratios | Not given anywhere agent-facing for the keyless works (only the barrel's 96 x m0.2 and, in the spike, the 36-tooth minute wheel stand-in, which are supplied parts). SOLUTION.md's tooth-count table is NOT-FOR-AGENT and FORBIDDEN_NAMES keeps it out. |
| Part 5 step weights not stated in the joined QA | Real QA sheets do not publish weights; "each step counts on its own" is stated. |

---

#### C. Top 3 to change before the final runs

1. **Finding 1 (+5): bring `environment/brief_keyless.py` Part 5 prose in line with the engine that will grade
   tonight** (springs push on return; give way only in the pushed direction; free `on_stem` rider yields first;
   Fits; does-not-model paragraph; settle before AT-0 rest; AT-2 extension; AT-5 position 1 over COUPLED_TURN).
   Biggest effect on the difficulty score: without it, failures can be traced to the documents.
2. **Finding 2: neutral `keyless.mobiles` example in FORMAT** (drop the spring/slide/on_stem line that mirrors the
   reference's sliding pinion). Biggest pure over-giving item; cheap; protects the gap.
3. **Finding 3: state (or remove) the AT-2 -> AT-3 coupling.** A hidden pass rule that double-charges a click fault;
   a judge checking "is every failure explainable from the stated rules" will find it.

If there is time for one more line: finding 4 (state "clockwise seen from +z" next to the winding-sense rule),
and confirm finding 6 (do not merge the branch's DS-401 row). Leave finding 7 (Breguet line) until after the
runs, so the measured numbers stay comparable.

## B's findings
(B: independent pass on your four-part documents first, then ours if time allows.)

### B's reviewer: independent pass on the four-part documents (15 Nov, run on `make_bundle_job.py` output)

Read in full: instruction.md, FORMAT.md, QA-W100, DS-W01 to DS-W04, DS-101 Table 2a and Note 2, DS-201 section 8, tools/kernel.py, tools/check_format.py. Compared line by line with `tests/grade_watch.py` (`grade_job`, `JOB_PARTS`, `_check_table`) and `geometry/watch.py` (`mesh_run`, `drive_parts`, `strength_run`, `going_train`, `assembly_replay`, `_asm_messages`, `extent`, `hand_shape`). Not run: a delivery through the grader (no solution run for this review).

**Summary.** No BLOCKING item: every grader check I traced (all 14 checks of Part 1, the 2 of Part 2, C1 to C4, the Part 4 rules, the honesty table and its formula) is stated in QA-W100 or FORMAT with the same number and the same convention. I found no design value, tooth count, layout, ratio, module choice or method in any file the agent sees (DS-W01 gives only the supplied barrel's own data). The cause of 10 of 10 is not a leaked value. It is that QA-W100 is a complete executable specification: every threshold, step count, off-grid pose, tolerance and the rating formula is given, so the agent can write its own copy of the grader from the folder (with `kernel.ivol`, `min_distance`, `opening_test_slabs`, `load_step_part`) and iterate until it passes. Most of that is not removable (removing a threshold makes the gap unfair). The items below are the few places where less would still be fair.

#### WORTH CHANGING

1. **Load case stated three times, down to the cell.** instruction.md:28 ("the going train is rated for that version's barrel load"), QA-W100:156-158 ("upper end of the bridle's slipping torque, DS-101, Table 2a, row ..., column for this series ... whatever mainspring the barrel of this build holds"), DS-101:194-197 (Note 2, bold: "The highest torque this sheet states ... is the reference slipping torque, 70.1 N·mm"). Over-giving. Effect: the one judgement in check 14 (which torque is the design load: M½ 50.2, the lower bridle value 51.6, or the upper bridle value 70.1) becomes a lookup. In real job documents: a work order and a rating procedure would state the design load or name its source; naming source row and column as well is more than usual. Would removal be unfair: not if QA keeps "the upper end of the slipping torque band of the automatic version's bridle (DS-101, Table 2a)", because the work order sentence and DS-101 Note 2 still make it findable with one reading. Proposed edit to QA-W100:156-158: delete "row \"Slipping torque of the bridle (min. to max.)\", column for this series (N·mm)," and leave "T_barrel is the upper end of the slipping torque of the automatic version's bridle (DS-101, Table 2a), whatever mainspring the barrel of this build holds." Keep instruction.md:28. Owner: B for QA; A for DS-101 Note 2 (delete the bold value and keep "the highest torque this sheet states is the slipping torque of Table 2a"). Gain is small; decide with the humans.

2. **QA-W100:163-165 tells the agent which meshes need no strength.** "The motion work, and any other mesh off that path, is not rated." Over-giving (shortcut): it states the exploit (keep strong gears on the seconds path, anything off it can be weak and thin). The path rule in the sentences before it already says which meshes are rated, so this sentence adds no information a checker needs. In real job documents: a rating procedure defines the rated path; it rarely adds "everything else is exempt". Removal is fair (the path definition stays). Proposed edit: delete that sentence (keep the "If the seconds hand's mobile is not reached ... this check fails" sentence). Owner: B.

#### MINOR

3. **FORMAT.md:52 layout block lacks `material`.** The example `"mobile_name": {"axis": [x, y], "parts": [...]}` has no `material` or `part_materials`, while FORMAT.md:72-80 bullets (below the block, in a list about `meshes`/`hands`) make `material` mandatory and a missing one makes the file not valid (QA C1 then fails the whole part). Under-giving by layout, stated once in prose; `check_format.py` catches it, so not BLOCKING. Proposed edit: `"mobile_name": {"axis": [x, y], "parts": ["part_name", ...], "material": "AD-...", "part_materials": {"part_name": "AD-..."}},` and mark `part_materials` optional in the sentence below. Owner: B.

4. **`tools/check_format.py:32` `MATERIALS = ('AD-C100-HT', 'AD-CW614N')`.** Over-giving, tiny: the agent reads which codes qualify instead of working it out from DS-201 section 8 (corundum is compressive only; C100S and CoNiCr have no row). The next error message gives the same answer on the first try anyway. In real documents: a format checker would know its codes. No change needed; noted because the material choice is one of the small judgement steps. Owner: B.

5. **DS-W03:22 voxel offset `0.0113` and the full voxel recipe.** A print service sheet would give the 0.2 mm feature rule, not a voxel grid with a sub-millimetre offset; the offset has no meaning for a designer. Over-giving only in the sense that the agent can run the exact printability test with `kernel.opening_test_slabs`. Removal would be unfair unless the sheet kept the recipe (the tooth tips of module 0.2 are narrower than 0.2 mm, so the outcome depends on the recipe, not on "0.2 mm"). Keep. Owner: B (no change).

6. **QA-W100:117 off-grid poses (`i + 1/3`, `i + 1/5`).** Grader hardening that no real procedure states. Harmless to fairness; removal changes nothing for a design that meshes. Keep or drop, no effect on the gap. Owner: B.

7. **DS-W01:47 "Tooth phase ... measured on the supplied mesh".** Derivable from `barrel.stl`; a catalogue sheet would not state it. Removal is fair. Over-giving of a trivial step. Owner: B (optional).

8. **QA-W100:30-31 "the delivery's acceptance figure is its parts figure ... times (0.75 + 0.1 x h) / 0.85".** "Parts figure (the result of the four parts together)" is not defined in the agent's folder (the grader's is 0.5 x weighted share + 0.5 x all-pass, not shown, correctly). No effect on design; only the report.json decision (claim `pass` risks -2) is affected and that uses only the table given. Leave. Owner: none.

#### Checked and consistent (no finding)

- Case numbers: DS-W02 CS-414-134 (20.7, 13.4) equal `CASE_RADIUS`, `CASE_HEIGHT`; QA check 12 states the conservative mobile bound the grader uses (max distance from own axis plus axis offset), and that the barrel is included in height and radius.
- Barrel numbers: DS-W01 section 3 (bore 2.0367, core 2.02, drum z 0 to 1, arbor z -1 to 5.6, speed classes D = 8 h, B = 6 h, clockwise) equal the `geometry/watch.py` constants.
- Mesh test: QA steps, off-grid poses, engaged every 4th step, drive push 0.25 pitch, V at least 0.001, V/H > 0.5 m^2, shift 0.03 away and towards: all equal `mesh_run`.
- Check 14: Y table lookup, T_D, F, b = smallest H, "lowest allowable" (725 for AD-C100-HT, 110 for AD-CW614N, corundum row excluded), tooth-holding part by summed drive volume, BFS rule: equal `strength_run`, `going_train`, `teeth_part`, `MATERIAL_ALLOWABLE_MPA`.
- Part 4 rules 1 to 5 equal `_asm_messages` and `assembly_replay` (a part that fails still stands in place; parts not in `order` stand from the start).
- Honesty table (1, -2; 0.5, 1; 0.5, 0.5) and factor (0.75 + 0.1 h) / 0.85 equal `HONESTY_POINTS`, `W_PRODUCT`, `W_HONESTY`.
- C3 (day part not the hour, minute or seconds part), C4 (same `fixed` list in order, same `case_centre`): equal `job_day_declared`, `job_same_frame`.
- DS-301, DS-401, DS-501 (crown set) are in the bundle with Part 5 off and are not referenced by the work order or QA-W100; they are noise, not a leak, and carry no tooth counts or train data.
- `tools/kernel.py` has primitives, boolean volume, minimum distance, slices, voxelise and opening only. It has no mesh test, no gear generator, no train logic, so it contains no check of Parts 1 to 4 except the printability engine of DS-W03 (item 5).

## Decisions
| # | Finding | Decision | Who | Commit |
|---|---|---|---|---|
