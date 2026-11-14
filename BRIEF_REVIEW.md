# Brief and datasheet review (A and B, 15 Nov 2026)

Shared file for both workstreams' reviews of everything the agent sees: the work order and PROMPT, FORMAT.md, QA-W100, the DS-W datasheets (B), and the crown-winding brief and DS-101..DS-501 (A). Each side appends findings under its own heading; decisions go at the bottom and in SESSION.md Decisions. Not shown to the agent (keep it out of every bundle; it is not under environment/public/).

**The two failure modes (from the judging rubric):**
- **Over-giving** kills the gap: the documents hand over the solution to the hard part (values that pin the design, how a mechanism must be built rather than what it must do, every test threshold so self-checking is trivial, the reference's choices leaking through examples). Ask: would a real job's documents contain it?
- **Under-giving** makes the gap unfair (difficulty scores zero): something the grader checks is not stated or derivable (threshold, convention, sign, unit, frame, tolerance, limits, format), trick wording, or numbers that disagree between documents.

**Format for each finding:** document:line or a short quote; over- or under-giving; effect (gap, difficulty); in real job documents? yes/no; the proposed edit (exact wording); owner (A or B).

**Deadline:** edits must land before the final model runs (target: decided by 02:30, merged by 03:00), because changing the brief after the runs makes them stale.

## A's findings
(A's reviewer is running; its findings are added here when done.)

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
