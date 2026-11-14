# Judge rehearsal, 15 Nov 2026, about 01:00 Helsinki

A Claude session played an AfterQuery judge who has never seen the project. It worked in a fresh clone of
`origin/main` at `cd81895`, outside every other worktree, on an idle 4-CPU, 15 GB cloud machine with Python
3.13.18. It changed no code, grader, reference or agent-facing file, and started no model runs. Every number
below was printed by a command shown in section 3 or 4.

While this ran, `main` moved to `73db9a3`. Only `SESSION.md` and a new `BRIEF_REVIEW.md` changed, so the audit
below still describes main. Two things in those entries matter here. A ran the Harbor oracle and nop on
`cd81895`: 1.0 and 0.0 (00:47). And itswinther decided two rule changes at 00:50, now being built: a hand-shape
limit, which closes the disc hand, and a drive test that starts from flank contact. By my reading of the
decided rules, neither closes the three new findings in section 4. I have not run them against the new
rules.

## 1. The verdict in five lines

- **The commands work.** Every local command in the README ran from a clean clone. The reference graded 1.0 in
  275 s, an empty delivery 0.0, and the three stop-early anchors matched their expected rewards.
- **No gap on the job as submitted.** The README reports frontier models at 1.0 on all nine of its runs of this
  job (B's log says 10 of 10). The one gap it cites, in crown winding, is switched off in the job, and two of
  GPT's three shortfalls there were traced by A to a simulator artifact. The rubric scores that kind of gap zero.
- **Three new ways to score 1.0 with a watch that does not work** (section 4). False tooth counts get a pinion
  that is too weak past the gear strength check: graded 1.0. A minute hand that hits the seconds hand once an
  hour: graded 1.0. A wheel locked by the frame passes "free to turn" (unit demo with the grader's own function).
  They add to the known off-centre disc hand. None scores above 1.0, but each scores as much as a working watch.
- **Integrity work is otherwise strong.** The grader fails closed and the verifier is offline. There are 36
  anchors, asserted to exact fractions. Do-nothing and stop-early baselines are measured.
- **Rubric estimate: about 39 of 100** (section 5). Most of the missing points are in the gap, so the change
  worth most is a gap on the job the judges will actually run (section 6).

## 2. README audit

What a judge reads first: `README.md`, then `SPEC.md`, `harbor/watch_one/README.md`,
`solution/SOLUTION_WATCH.md`, the brief `environment/public/job/PROMPT.md` and
`environment/public/job/datasheets/QA-W100_inspection.md`.

**Claims that disagree with the files, or are stale**

| # | Where | It says | The files say |
|---|---|---|---|
| 1 | README, "What we found so far" | "Nine local runs, nine scores of 1.0" | SESSION.md 23:58 (B): Sonnet on the latest brief also 1.0, "10 of 10 at 1.0" |
| 2 | README, "Open work" | "Stop-early anchors and the full anchor run on the current grader" are still to do | the three stop-early anchors exist and pass (section 3, step 6); A ran 32 of 33 anchors at 82c5678 and B fixed the 33rd (SESSION.md 23:53) |
| 3 | README, "The gap signal is in crown winding" | presented as the gap | Part 5 is off in the judged job (`KEYLESS_IN_JOB = False`, `geometry/keyless_job.py:19`). Two of GPT's three shortfalls are a simulator artifact (A, 00:40). The table puts Sonnet's 0.95 (first engine) next to GPT's regrade (fixed engine) without saying the engines differ |
| 4 | SOLUTION_WATCH.md section 3 | stop-early anchors "are not in the file yet"; A's anchor table "is not in SESSION.md yet" | both exist: `tests/test_anchors_job.py:539-561`, SESSION.md 23:53 |
| 5 | SOLUTION_WATCH.md section 9 | the latest Sonnet run is "running; not in SESSION.md"; "Nine of nine at 1.0" | 1.0, SESSION.md 23:58 |
| 6 | harbor/watch_one/README.md, interface table | the agent's `datasheets/` holds "DS-W01..W03, INDEX.md" | the bundle I built holds DS-W01..W04, QA-W100, DS-101..501 and INDEX.md (16 files, section 3, step 4) |
| 7 | harbor/watch_one/README.md, interface table | the verifier image has the grader "with `geometry/` beside it" | it also needs `spikes/keyless/constants.py` or every trial scores 0. `build_task.py` does copy it (`A_KEYLESS`); only the README leaves it out |
| 8 | harbor/watch_one/IMAGE_CONTENTS.txt | image built 16:56 from 566415f, with no `DS-W04_gear_rating.md` | the current bundle has DS-W04 and the strength check needs it. The listing is out of date |
| 9 | CLAUDE.md (README links it), "Decisions already made" | "Submissions are STL plus a JSON path file. No STEP." The grader "opens exactly three files ... `base.stl`, `door.stl`, `assembly.json`" | parts are STEP only; STL is refused (`FORMAT.md`, `geometry/watch.py:737`). These are rules of the retired Board in a Box. A judge who follows the README link reads rules for a task that no longer exists |
| 10 | SESSION.md, last entries | timestamps 00:05, then 2026-11-15 **23:58**, then 00:40, then **00:26** ("follow A's 00:40 verdict") | the log reads out of order, and 23:58 is dated a day late. A's 00:52 entry says some of A's stamps were written ahead of the clock |
| 11 | requirements.txt | numpy 2.5.3, no trimesh | the task image pins numpy 2.5.4 and installs trimesh 5.2.1, which the brief lists as installed. The grader does not need trimesh (it ran without it) |

**Numbers without a source next to them** (each has a source somewhere in the repo; the README does not say where)

- CAD-bench 96.9 percent and 4.0 percent, and "Saini, ICML 2026": `HARBOR_RESEARCH.md` lines 416 and 577
  give a jsdelivr link to the PDF. I could not check the venue.
- BenchCAD, arXiv 2605.10865: cited nowhere else in the repo (outside SESSION.md). I could not check it.
- "Real barrels run 6.3 to 8 hours per turn": `REAL_WATCH_WORK.md` line 49 (6.33 to 8).
- SW200-1 bridle slipping torque 16.57 N·mm: `REAL_WATCH_WORK.md` line 227. 16.57 x 1.617³ = 70.06, so the
  70.1 N·mm is consistent.

**Commands the README does not give, though a judge needs them** (they exist; I found them in SPEC.md or in
the scripts)

- Build the agent's folder: `python3 environment/make_bundle_job.py OUT` (SPEC.md section 2). The README's
  table names the script, but gives no command.
- Grade an empty delivery, the do-nothing baseline: the same grader command on an empty folder.
- The stop-early baseline: `python3 tests/test_anchors_job.py 2 --only "job stop-early"`. The README gives only
  the full suite, with no time estimate. Measured here: 3 anchors took 10 min 24 s with 2 workers. A reports
  the full suite at 1 h 40 min with 2 workers (SESSION.md, A's 00:42 offer).

**What held.** Every path the README names exists (24 checked). The reward formula in the README matches
`grade_job`. The reference's margins in SOLUTION_WATCH.md section 2 match the details file I produced: drive
V/H/m² 2.149 on barrel/third, smallest 1.238 on day idler/day; hand reaches 5.009, 6.007 and 9.005; strength
margin 1.392. The reference timing ("about 40 s") matches: 35.5 s. The grading time ("about 10 minutes") is
generous: 4 min 35 s here, idle.

## 3. Command log

All from `/tmp/.../scratchpad/clean`, a fresh `git clone` of `origin/main` at `cd81895`. One grading at a time,
except that the anchor suite runs its own 2 workers, as the README asks.

| Step | Command | What came back | Time |
|---|---|---|---|
| 1 | `pip install -r requirements.txt` | exit 0 (cadquery 2.8.0, manifold3d 3.5.5, scipy, numpy) | 37 s |
| 2 | `python3 solution/reference_watch.py REF --job` | "parts 22 movement 20 variant 20 only in variant ['centre_36', 'third_wheel_54'] only in movement ['centre', 'third_wheel_60']" | 35.5 s |
| 3 | `cd tests && python3 -I grade_watch.py REF --reward R --details D` | **reward 1.000000**; P1 to P4 all gates and checks true; P4 "21 of 21 installed"; honesty claims pass x 4, factor 1; `elapsed_s` 275.2 | 4 min 35 s |
| 4 | `python3 environment/make_bundle_job.py BUNDLE` (not in the README) | "bundle written"; 16 files: FORMAT.md, instruction.md (identical to PROMPT.md), DS-W01..W04, QA-W100, DS-101..501, INDEX.md, supplied/barrel.stl, tools/kernel.py, tools/check_format.py, and an empty delivery/ | 2.9 s |
| 5 | grader on an empty folder, and on the bundle's empty `delivery/` | **reward 0.000000** both; every gate false; honesty "absent", factor 16/17 | 0.1 s |
| 6 | `python3 tests/test_anchors_job.py 2 --only "job stop-early"` (I added `--keep DIR` to keep the details) | **3 of 3 ok**: Part 1 only 0.1569 (8/51); Parts 1 and 2 0.2196 (56/255); Parts 1 to 3 with a truthful report 0.3333 (1/3) | 10 min 24 s |
| 7 | `python3 -I tools/check_format.py FOLDER` (the agent's checker) on both exploit folders | "format ok" on both | not timed |

Where the README was not enough:

- Step 4 and step 5 are not in the README (see section 2).
- After `cd tests` for step 3, the next README command (the anchors) says "from the repo root". It works from
  anywhere, but a reader copying the block in order is in `tests/`.
- My first try at step 3 failed because I wrapped it in `/usr/bin/time`, which this machine lacks. That was my
  wrapper, not the README.
- Not run: the Harbor commands (they need a Harbor 0.26 checkout at `../../harbor` and Docker) and
  `environment/run_clean_job.sh` (a model run). A ran the Harbor oracle and nop on `cd81895` during this
  rehearsal: oracle 1.0, verifier 3 min 26 s, peak RSS 1.69 GB; nop 0.0 (SESSION.md 00:47). SOLUTION_WATCH.md
  section 9 still says "earlier builds".

## 4. Exploit hunt

I read QA-W100, FORMAT.md, `tests/grade_watch.py` and `geometry/watch.py`, then tried to make deliveries that
score as well as honest work while the watch does not work. Each attempt is the delivered reference plus one
small change. I graded each one with the same command as step 3, one at a time. The scripts are short and are
given below, so anyone can rebuild them.

### Results

| # | Attempt | What it shows | Score |
|---|---|---|---|
| 1 | **False tooth counts beat the gear strength check.** The third pinion made brass (an honest brass pinion fails check 14). The barrel/third mesh declared 48:12 instead of 96:24: same ratio, so every speed is unchanged. No geometry change | check 14 trusts declared tooth counts. It takes the module from them: m = 2a / (z_D + z_N) doubles to 0.4. That more than offsets the smaller Lewis factor of 12 teeth (0.2546 against 0.3634 for 24), so the stress falls from 125.6 to 89.6 MPa, under brass's 110. The mesh test still passes (V/H/m² 1.106, needs over 0.5), because only the ratio has to match the geometry | **1.000000** (graded; P1 to P4 all pass, strength true in P1 and P3). Control, same files with the honest 96:24: strength false, sigma 125.6 MPa against 110 |
| 2 | **Hands that crash once an hour pass "Nothing else collides".** The minute hand lengthened from 9.0 to 12.0 mm, with a 0.5 x 1.0 mm fin under its tip reaching down into the layer of the seconds hand (z 9.9 to 10.7). In the delivered pose the hand points away from the seconds dial | check 6 turns each pair 144 steps over one turn of the faster mobile, then 144 over one relative turn. The slow mobile only ever turns a few degrees: here the minute hand turns 6.00 and 6.10 degrees. The grader's own `clear_run(centre, seconds)` gives 0.0 mm³. From 82 degrees past its delivered angle (13.7 minutes later) to at least 180 (I searched no further), the fin hits the seconds hand by up to **0.1439 mm³**, 14 times the limit | **1.000000** (graded; P1 to P4 all pass, `clear` true in P1 and P3, P4 21 of 21 installed) |
| 3 | **A wheel locked by the frame passes "Free to turn"** (unit demo, no delivery). A 72-tooth wheel and a fixed pawl in one tooth gap | check 1 turns a mobile in 72 steps of exactly 5 degrees. A wheel with 72 (or 144, ...) teeth looks the same at every step, so a pawl that stops it passes. `Movement.spin` gives worst 0.0 mm³. Turned 1.25 degrees: 0.0139 mm³; 2.5 degrees: 0.0300 mm³ (limit 0.01). Checks 4 and 6 never test a mobile against the frame, so nothing else catches it | **passes check 1** (the grader's function, no full grading) |
| known | minute hand as an off-centre disc over the dial (builder N) | already in SOLUTION_WATCH.md section 8 | 16/17, or 1.0 with a truthful report |
| known | drive test depends on the backlash phase (`REAL_ML01_FAIRNESS.md`) | already reported | |

Why these matter more than their score: frontier agents already score 1.0, so no exploit can score more. What
a judge will see is a grader that cannot tell a watch that works from one that does not. Attempt 2 is a
natural mistake too: putting the minute and seconds hands in one layer is something a model can do by
accident, and the grader would pass it. Attempt 1 brings back the same class of hit, false tooth counts,
that the earlier red team found and closed for the speeds (`HANDOFF_EXPLOITS.md`, hit 1), this time through
the strength check, which was added after that fix. All three rules are stated in QA-W100 exactly as the code
runs them. So an agent that reads the procedure can find each hole. That is fair to the agent, and not what
the check is for.

### Tried and held

- **Teleporting paths.** The vertex-step rule is exact: for a rigid motion the largest move is at a vertex, and
  every vertex is checked. Tunnelling is possible only through a 0.2 mm wall by a feature of under about
  0.1 mm² cross-section (overlap stays under 0.01 mm³), which is too small to matter.
- **Gaming report.json.** The factor is at most 1, reached only by the true claims; any guess scores less (a
  blanket `pass` beats `not_tested` only when the agent is over 5/6 sure). It cannot lift a failing delivery.
- **Wrong ratio in a variant.** Declaring the 6-hour barrel mesh 72:24 on 96:24 geometry would fix the speeds
  without new parts, but the ratio must match the geometry or the pair jams (the anchor "variant with 6-hour
  counts on 8-hour parts", 0.4148).
- **Files the grader should not read.** Symbolic links and paths outside the delivery are refused
  (`inside()`). The verifier is a separate container, so hard links and processes left running by the agent do
  not reach it. `scripts/` is never opened.
- **A frame that holds nothing.** Fixed parts need not touch (joined within 0.01 mm), and "held" needs a real
  overlap after a 0.3 mm move against the frame or a held coaxial mobile. I found no way past it without a real
  frame. The earlier "mutual hold" and "islands" hits are closed.
- **Undocumented input.** The grader accepts a `friction_on` field (and a `keyless` section) with Part 5 off.
  FORMAT.md does not describe them and the agent's checker ignores them. A coaxial mobile marked `friction_on`
  counts as driven with no mesh. I found no score gain from it, but it is input the agent is not told about.
- **Not tested: the solution through a model API.** The agent's network allows `api.anthropic.com`,
  `api.openai.com`, `generativelanguage.googleapis.com` and `openrouter.ai`. Some of these offer web tools that
  run on the provider's side. The repo is private today (GitHub search: `"private": true`). If it is made
  public for judging, an agent with its harness's API key could fetch `solution/reference_watch.py` that way.
  Workstream A's network check would not see it.

### The attempt scripts

Exploit 1 (`e1_false_teeth.py REF OUT`):

```python
import json, os, shutil, sys
ref, out = sys.argv[1], sys.argv[2]
shutil.rmtree(out, ignore_errors=True); shutil.copytree(ref, out)
for fn in ("movement.json", "variant_6h.json"):
    p = os.path.join(out, fn); d = json.load(open(p))
    d["mobiles"]["third"]["material"] = "AD-CW614N"; d["mobiles"]["third"].pop("part_materials", None)
    for e in d["meshes"]:
        if e["driver"] == "barrel" and e["driven"] == "third":
            e["driver_teeth"], e["driven_teeth"] = 48, 12          # was 96, 24
    json.dump(d, open(p, "w"), indent=1)
```

Exploit 2 (`e2_crashing_hands.py BUNDLE/tools REF OUT`):

```python
import json, os, shutil, sys
import numpy as np
tools, ref, out = sys.argv[1:4]
sys.path.insert(0, tools)
import cadquery as cq, kernel
shutil.rmtree(out, ignore_errors=True); shutil.copytree(ref, out)
cx, cy = json.load(open(os.path.join(out, "movement.json")))["mobiles"]["centre"]["axis"]
hand = cq.importers.importStep(os.path.join(ref, "parts", "minute_hand.step")).val()
blade = cq.Solid.makeBox(4.0, 0.5, 0.3, cq.Vector(cx + 8.0, cy - 0.25, 10.7))   # r 8 to 12, z 10.7 to 11.0
fin = cq.Solid.makeBox(1.0, 0.5, 0.8, cq.Vector(cx + 11.0, cy - 0.25, 9.9))     # r 11 to 12, z 9.9 to 10.7
kernel.write_step(os.path.join(out, "parts", "minute_hand.step"), hand.fuse(blade).fuse(fin).clean())
asm = json.load(open(os.path.join(out, "assembly.json")))
asm["paths"]["minute_hand"] = [                       # straight down from 7.2 mm, 0.2 mm a pose
    [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0.2 * k], [0, 0, 0, 1]] for k in range(36, -1, -1)]
json.dump(asm, open(os.path.join(out, "assembly.json"), "w"))
```

The collision it hides, with the grader's own functions: load the folder with
`geometry.watch.load_movement(OUT, "movement.json", materials=True)`, then compare `m.clear_run("centre",
"seconds", 1, 60)` (0.0) with `ivol(m.posed("centre", -theta), m.posed("seconds", -psi))` for theta from 0 to
180 in steps of 2 and psi from 0 to 354 in steps of 6. The first value over 0.01 is at theta 82 and psi 312
(0.0120 mm³). The largest is at theta 94 and psi 282 (0.1439 mm³).

Exploit 3 (unit demo): a 72-tooth wheel (disc of radius 7.0 with 72 teeth of 0.4 x 0.3 x 0.6 mm at 5-degree
spacing), a 0.3 x 0.2 x 0.6 mm pawl at 2.5 degrees, radius 7.1, joined to a plate. `Movement.spin` run on a
stub with `fixed` = pawl + plate gives `{'worst_volume': 0.0, 'steps': 72}`. `ivol` with the wheel turned 2.5
degrees gives 0.0300.

### What would close them (each is a spec change for the humans)

1. **Check 14:** take the module and z from the geometry, not from the declaration. In a mesh with the barrel,
   the barrel's own 96 teeth and 0.2 module are known, so the minimum is to reject a barrel mesh whose barrel
   count is not 96. More generally, count each gear's teeth from a cross-section at the drive height (lobes
   on the tip circle), and refuse a declaration that differs.
2. **Check 6:** cover the slow mobile's whole turn. For example, test the slow one at 72 angles across its
   turn, each against the fast one's 144 steps. Or first prune with swept solids: if the two swept discs do
   not meet in z and xy, skip the pair.
3. **Check 1:** add off-grid spin poses (for example, 2.5 degrees after each step), or use a step count that no
   tooth count is likely to share, such as 73.
4. **Hands:** already decided at 00:50 (a hand covers at most 0.25 of the disc its tip sweeps) and being built.
   It closes the disc hand, but not attempt 2: that minute hand covers 0.0200 of the disc its 12.0 mm tip
   sweeps. I measured that with manifold's `project().area()`, which gives the reference's hands 0.030 to
   0.112, matching the decision text.

Does the 00:50 drive-test change close attempt 1? By my reading, no. The new test turns the driver to flank
contact and then pushes a quarter of the *declared* pitch. With 48:12 declared, that push is half a real
barrel pitch, so V/H only grows, and check 14 still takes m and z from the declaration. Not run.

Each fix needs its anchor (the three attempts above are ready-made anchors) and a rerun of the suite.

## 5. Rubric estimate, as a judge would score it

| Criterion | Points | Estimate | Why |
|---|---|---|---|
| Gap between frontier agents and the reference | 30 | **3** | On the judged job (P1 to P4), frontier models scored 1.0 in all nine runs the README reports (10 of 10 in SESSION.md), and none of those runs was in Harbor. Nobody has run GPT on this job. The three runs the judges make will most likely land at or near 1.0. The cited gap is in crown winding, which is off in the job. There, two of GPT's three shortfalls come from a simulator artifact, which the rubric scores zero. A few points for stating all this honestly, and for the staged version's real shortfalls (Sonnet 0.47, GPT 0.42 at assembly) |
| Meaningful difficulty | 30 | **12** | The task is well grounded: real calibres, a real CAD design run through the checks, supplier documents with one home per number, and a stated inspection procedure. But "meaningful difficulty" needs explained failures, and on this job there are none. Frontier models finish in 33 to 61 minutes for about $5. The one documented strict spot (ml01 fails "the train runs" depending on its backlash phase) reads as a convention, not difficulty |
| Reward integrity | 25 | **14** | Strong: offline separate verifier, reward 0 written first, every check in its own try block, leak checks by name and sha256, 36 anchors asserted to the fraction, do-nothing 0 and stop-early 0.157, 0.220 and 0.333 measured. Weak: four ways to reach 1.0 with a watch that does not work (the disc hand, documented; false counts on strength, crashing hands and the locked wheel, new). Nothing beats 1.0 because 1.0 is the top, so the "zero" clause may not fire, but a judge who finds one in 15 minutes will mark this down. That attempt 1 brings back an already-fixed class of hit will cost more |
| Craft | 15 | **10** | Strong: SPEC.md names the constant and file behind every number, commands are given with measured times, and the "not verified" notes are honest. Weak: the stale lines in section 2; a repo named after a dropped idea; 19 markdown files at the root, including internal handoffs; a 418 KB SESSION.md logged out of order; no Harbor run of the submitted job on a model; and the ten 1.0 deliveries are not in the repo, so no judge can inspect them |
| **Total** | 100 | **about 39** | |

## 6. The five changes that would raise the score most

| # | Change | Raises | Cost |
|---|---|---|---|
| 1 | **A gap on the job the judges run.** Merge A's engine fixes, which are on `a/keyless-engine-fixes` (contact counted per pair, c6dc192; batch 2, 397b5ad) and wait on B's items from A's 01:00 request. Get A's v2 crown-winding reference to 1.0 in B's frame, switch Part 5 on, and use the GPT crown-winding regrade A is running now. Then run Fable, Opus and GPT three times each in Harbor on the five-part job. Cheap first step: regrade the ten 1.0 deliveries of this job (if the humans still have them) with checks 1, 6 and 14 fixed. Any false pass is a real, explainable shortfall at once | gap, up to +15 to 20 if the shortfalls are design faults; difficulty +5 | engine fix plus an anchor rerun (1 to 2 h machine time); the P5 reference in B's frame (A's estimate); 9 or more Harbor runs at up to 3 h each, 2 in parallel, about $5 each. The regrade: 10 x 5 min |
| 2 | **Close the holes in section 4** (checks 1, 6 and 14; the hand-shape rule is already decided), with the three attempts as anchors, and state each new rule in QA-W100 | integrity +5 to 8 | each fix is under 50 lines of grader code, plus QA-W100 wording, a traceability entry, and an anchor rerun of about 1.5 to 2 h at 2 workers. Needs a human yes for each spec change |
| 3 | **Run the submitted job in Harbor as the judges will:** oracle x 3, nop and stop-early, then three runs of each frontier model with OpenCode, the judges' standard harness. Put the table in the README, even if it shows 1.0 | craft +2; gap evidence, positive or an honest zero; difficulty +2 | about $5 a run and 33 to 61 min each, so about 3 to 5 h wall time for 9 runs at 2 in parallel |
| 4 | **Commit every delivered folder and details file** of the agent runs, starting with the ten at 1.0. For any shortfall, add a failure analysis with a `tools/viewer/` picture, traced to the agent's decision | difficulty +2 to 4; craft +1 | about 1 h, once the folders are found |
| 5 | **A judge-facing cleanup:** README fixed (10 of 10, open work, the bundle, empty-grading and stop-early commands with times, citations pointing to `HARBOR_RESEARCH.md`); SOLUTION sections 3 and 9; the Harbor README's datasheet list and IMAGE_CONTENTS.txt; CLAUDE.md's Board in a Box decisions marked superseded; internal handoffs moved out of the root | craft +2 to 3 | 1 to 2 h |

Already decided and being built (00:50), and worth finishing before any judged run: the drive test from flank
contact (the ml01 finding) and the hand-shape limit. The first protects "meaningful difficulty" against the
reading that the hard part is a strict convention. The second closes the one integrity hit a judge would find
first, because SOLUTION_WATCH.md section 8 lists it.
