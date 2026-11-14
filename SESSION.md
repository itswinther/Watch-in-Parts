# SESSION.md

The shared log for four people and their Claude sessions. Read it when you start.
Append to it when you reach a milestone or stop. Edit only your own row in the
table. Everything below "Session entries" is append-only, newest at the bottom.

## Current state

| ID | Workstream | Owner | Status | Last update |
| --- | --- | --- | --- | --- |
| A | Harness wiring | Mikael | Staged watch in Harbor (`harbor/watch4/`). GPT-6.1-sol, sandboxed, web search off: chain A 1.0 x4 stages; chain B 1.0, 1.0, 1.0, 0.4232 (stage-3 rework of `lower_bridge` cannot be installed at stage 4). Haiku 5.5 (OpenCode) stopped at stage 1 with no submission. Chain C and a Haiku retry cancelled. See 11:55 entry | 2026-11-14 11:55 |
| B | Reference script and grader | itswinther | `light`, `seated`, `tolerant` and the reworked skeleton reference are on main (42482a0 plus this entry): reference 1.0 at all four stages, 36 of 36 anchors ok, one review round with no blocking finding. NO clean chain has been run on this version; itswinther decides when, and the "Grader exploits fixes" session is changing agent-visible rules on top of it (branch `claude/gifted-gauss-b7b3jy`), so chains should wait for that. Orchestrator session owns the anchor runner fix (fork hang) | 2026-11-14 13:14 |
| C | Hold the Line spike | unassigned | not started | |
| D | Mentor questions, anchors, transcripts | unassigned | not started | |
| E | Analysis, demo and story | Yoseph | paused: Yoseph is not working overnight | 2026-11-14 01:40 |

Spec version in use: 0.5 (staged watch, four stages, with `light`, `seated`, `tolerant`; `environment/public/SPEC_WATCH.md`)

## To do, in priority order

There is no timeline. The aim is to excel on every judging criterion, whatever
work that takes. Work from the top; when the situation changes, reorder this
list instead of dropping items. The one fixed date is the submission: Sunday
15 Nov, 10:00 Helsinki.

This list assigns nobody. Who does what is decided by the team in person.

**1. The gap (30 points): frontier models must consistently score below the reference.**
- Find a mechanism that makes Fable, Opus and GPT-class models fall short, not only Sonnet. Today no frontier model does.
- Finish and test the three checks being built (`light`, `seated`, `tolerant`).
- Build and test the remaining proposals from the 09:44 entry: a winding stem at right angles (bevel or crown teeth), an intermittent date ring, a change request that edits geometry with "kept" measured by volume.
- Keep looking beyond that list; nothing is ruled out because it is large.
- Test every candidate with clean chains, at least three per model, including GPT in the Harbor sandbox. Keep what bites on the strongest models.

**2. Meaningful difficulty (30 points): every shortfall explained and fair.**
- For each failed check, trace it to a decision the agent made, in the transcript and in the submitted files.
- Confirm each failure against the grader, so a grader fault is never reported as an agent failure.
- Confirm the agent had the information and tools to do better, and that no failure comes from a time limit, trick wording or a broken tool.
- Write the failure analysis, with pictures from `tools/viewer/`.

**3. Reward integrity (25 points): no exploit beats real work.**
- Anchors for every stage and every check, including each new one; all asserted by one script.
- A deliberate exploit hunt against the grader and the STEP loader; every attempt logged with its score, every hit turned into an anchor.
- Do-nothing and stop-early baselines defined, run and in the results table.
- Fix the kept-parts score, which counts files and can be padded.
- Close the open review notes (hard links, project name in file headers, the reference's thin drive margin).

**4. Craft (15 points): it makes sense and anyone can reproduce it.**
- One Harbor task for all stages; reference 1.0 and do-nothing 0.0 in the sandbox; one command in the README. Rebuild the image and rerun both whenever a new check lands.
- A dry run from a clean clone by someone who did not write the README.
- Repeat runs, so every reported number is shown to repeat.
- README in a human voice (the organisers warned that AI-written READMEs read poorly); demo script and video, using `tools/viewer/` to show the reference running and a part that cannot be installed.
- A read of `environment/public/SPEC_WATCH.md` by someone who knows watches, flagging anything a watchmaker would call wrong.

**5. Tiebreaker: a smaller model that improves after training on our environment.**
- This was cut from scope on day one. The organisers name it as the tiebreaker and as something they look for, so it is back on the list; a human should confirm.

## Requests

One line per request to another workstream. The addressee answers on the same
line and ticks it. Format: `- [ ] to B, from A, HH:MM: what you need`.

- [x] to A, from B, 01:40: say here when the starter kit is in the repo, and where the verifier expects the grader entry point and the reward file. Until then B assumes `tests/grade.py <base.stl> <door.stl> <assembly.json>` taking three absolute paths. **A, 02:20: there is no starter kit and no scoring skeleton. The organisers' only contract is a plain Harbor task whose verifier writes one number in 0..1 to `/logs/verifier/reward.txt` (your guess was right). Harbor runs `tests/test.sh`; A will write that to call `grade.py` with your three-path signature, so keep it.**
- [x] to A, from B, 02:05: is a session for A running? Nothing from A is on `origin/main` yet. Please push the starter kit as its own first commit, even untouched, so B can read the verifier contract. **A, 02:20: yes, running since about 02:00 with push rights to main. Nothing to push as a starter kit; the organiser message is quoted in the 02:20 entry.**
- [ ] to all, from B, 02:05: sessions started before 01:40 still follow the old CLAUDE.md. Tell your session to `git fetch origin && git rebase origin/main` and re-read CLAUDE.md.
- [ ] to whoever owns branch `claude/fervent-brown-cb0201` (`cala-tests/`, Cala API responses): is that meant for this repo? It is not on main.
- [ ] to Abhishek (watch idea), from B, 2026-11-14 03:42: itswinther has made the mechanical watch the main idea. B is building the first runnable version now in `geometry/watch.py`, `tests/grade_watch.py`, `solution/reference_watch.py`, `environment/tools_watch.py`. Please do not build the same pieces; if you have a barrel mesh, tooth numbers or a brief already, push them and say so here.
- [x] to B (and Abhishek), from A, 2026-11-14 04:00: before building the watch further, read `spikes/README.md` and `spikes/gear_train/`. A fully specified watch gear train (exact rates, centre distances from tooth counts, layered packing in a round plate, balance keep-out) was solved by all three models: Fable 1.0, Opus 1.0, Sonnet 0.92, each by writing an exhaustive search. Your version differs in two ways that may matter: a minimal brief where the hand rates are unstated, and a rotating replay (jam, engagement, drive). Those are the untested parts; a first clean run on a stripped brief would show quickly whether they create a gap. Also: with no torque limit the power reserve objective is trivially maxed (6.5 x 140/7 = 130 h). **B, 03:52: read. My version is exactly those two untested parts: the brief leaves the hand speeds, direction and shared hour-minute axis unstated, and the agent must submit real meshing gears as STL that the grader turns (jam, engagement, drive). There is no power-reserve term. Three clean runs (Fable, Opus, Sonnet) started at 03:47; results will be in my next entry. I am not building further until they are in.**
- [x] to A, from B, 2026-11-14 04:55: read your 05:10 to 06:00 entries. The most useful run now is the one neither of us has: the **frozen** staged watch on GPT-6.1-sol in your Harbor sandbox. Stages and grader are on main (`tests/grade_watch.py --stage N --prev FOLDER`, bundles from `environment/make_bundle_watch.py OUT --stage N --prev FOLDER --tools no`, reference from `solution/reference_watch.py`). Each step must start a fresh conversation, receive the previous step's submission as read-only `previous/` plus a copy in `work/`, and must not be able to change frozen files (the grader checks bytes). Image needs `manifold3d==3.5.5 scipy trimesh numpy`. Grading a stage takes 2 to 3 minutes. If you can run three chains, post the per-step scores here. An overnight orchestrator session may change the stage list (it adds a change-request stage and STEP files); the three-stage version on main at commit 6bfb150 is stable and is the one to run first. **B, 10:21: out of date, do not act on the details in this line. It describes the three-stage task at commit 6bfb150; main is now four stages with STEP parts only. See the status entry of 10:21 for the current state.**
- [x] to A, from B (orchestrator), 2026-11-14 06:07: what Harbor needs for the staged watch as it is on main now. (1) Four steps, one fresh conversation each: design, extend, change, assemble; step N+1 starts from step N's `submission/` (bundle: `python environment/make_bundle_watch.py OUT --stage N --prev PREV_SUBMISSION`). (2) Grader per step: `python -I tests/grade_watch.py /abs/submission --stage N [--prev /abs/previous_submission] --reward /logs/verifier/reward.txt`; it needs `geometry/` next to `tests/`. (3) Image packages for agent and verifier: `manifold3d==3.5.5 scipy numpy trimesh cadquery==2.8.0` (cadquery-ocp 7.9.3.1.1; build123d cannot be installed beside it). (4) Verifier resources: a stage takes 3 to 4 minutes and peaks at 5.7 GB of memory here (the thickness check on the plates), so give it 8 GB and a 15-minute timeout. (5) Reward: Harbor has only `mean` and `final`; our chain score is the product, so use `final` with the last verifier grading all four folders, or report the mean and say so. (6) Artifacts per step: `movement.json`, `parts/*.step`, `scripts/`, and `assembly.json` at step 4. STL parts stop being accepted once the reference port lands tonight. **A, 10:50: done in `harbor/watch4/` (one single-step task per stage, so the verifier gets the previous submission from the host, not from the agent; 7 GB / 15 min verifier; cadquery 2.8.0, manifold3d 3.5.5, scipy in both images; chain score = product of the four per-stage rewards, computed from the trials). GPT chain A ran through all four stages, see the 10:50 entry.**
- [x] to A, from B (orchestrator), 2026-11-14 06:11: when you package the staged watch in Harbor, the verifier must take `--prev` from the previous step's own graded submission, never from the `previous/` copy inside the agent's workspace (the agent can edit that copy, which would defeat the frozen-file and kept-file checks). Found by the reviewer; `environment/run_clean_chain.sh` already does this. **A, 10:50: yes. `--prev` is `/tests/prev`, a host snapshot of the previous trial's collected submission, uploaded only to the verifier.**
- [ ] to B, from itswinther's review session, 2026-11-14 11:50: before `light`, `seated` and `tolerant` go to main, read `HANDOFF_EXPLOITS.md`. The mesh test accepts false tooth counts (real 44/46 declared 6/3 scores 1.0) because it samples 8 poses per declared tooth; your TOLERANT builder rewrote `mesh_run`, so the fix has to sit on top of that version. Also: the reference's `barrel_cock` floats 1.45 from every other fixed part, and the thickness test needs 0.83 GB per mm of part height (reference 6.1 GB of the verifier's 7.0).
- [ ] to B (orchestrator session), from the grader-exploits session (itswinther), 2026-11-14 11:59: itswinther approved all seven exploit fixes (Proposed spec changes, 11:50) and asked me to build them on top of your `light`/`seated`/`tolerant` branch. Your builders are editing `geometry/watch.py`, `geometry/core.py`, `tests/grade_watch.py`, `SPEC_WATCH.md` and the reference right now (X1 to X5). To avoid two sessions in the same functions: say here (or by send_message) what you are still changing and when it is pushed to `origin/claude/confident-brown-ipeiud`. I will own `mesh_run` sampling, `held`, frame connectivity, driven-from-barrel, hands, stage-3 kept share, the drive threshold and the slabbed thickness test, plus their anchors, and will not edit shared files until you answer.
- [ ] to A, from the grader-exploits session (itswinther), 2026-11-14 11:59: heads-up, no action yet. The seven exploit fixes will change the grader, the reference and `SPEC_WATCH.md`, so the `harbor/watch4/` images and bundles will go stale; I will post here when they are on main. Also from the review: `build_stage.py` copies every file in `submission/parts/` to the next stage (notes pass between stages; a subfolder crashes the build); copying only the part files `movement.json` names would close that. That file is yours; I will not touch `harbor/`.

## Open questions

Write the answer and who gave it next to the question, then tick it.

- [ ] Which model and effort setting do the judges run? (Partly answered 02:20: the organisers "urge" OpenCode and give the example `harbor run -p ./my-task -a opencode -m [provider/model]`; the model is not named, and credits are Google/OpenAI/Modal, so we choose what we benchmark on.)
- [ ] Per-trial timeout?
- [ ] Wall-clock budget for the judges' rerun?
- [ ] Can the agent see images?
- [ ] How is the stop-early baseline defined?
- [x] How large is the model-credit grant? **None. Organiser message (Mikael, 02:20): AfterQuery gives no inference credits; use the Google, OpenAI and Modal sponsor credits.**
- [ ] Which environment provider does the rerun use? (decides compose sidecar or in-container MCP server)
- [x] Does the organisers' OpenCode register MCP servers declared in task.toml? **Yes, per Harbor source v0.26.0 (`src/harbor/agents/installed/opencode.py`, `_build_register_config_command`): it writes `[[environment.mcp_servers]]` into OpenCode's config, stdio as a local command or HTTP as a remote URL. Read in source by A, not yet seen in a transcript. There is no organiser-specific OpenCode build.**
- [ ] When do the AfterQuery demo and rerun happen?
- [x] What does the scoring skeleton record when the verifier is killed or times out? **There is no scoring skeleton. What plain Harbor records on a verifier timeout is still untested (A will test).**
- [x] Can agent network access be limited to the model API? **Yes in Harbor's task config: `[environment] network_mode = "allowlist"` with `allowed_hosts`. From the Harbor docs, not yet run by A.**
- [ ] H1 scored 1.0 on the first agent attempt (02:15). Do we harden Board in a Box, or move weight to Hold the Line? Needs a human answer before more is built.

## Decisions

Append one line per decision: time, decision, who agreed.

- 2026-11-14 00:50 Working plan is the second review, updated version. SPEC.md 0.1 is taken from it.
- 2026-11-14 02:20 Organiser contract replaces the "starter kit wins" rule: the environment is a plain Harbor task (`instruction.md`, `task.toml`, `environment/Dockerfile`, `tests/`, `solution/`), run as `harbor run -p ./my-task -a opencode -m provider/model`, reward is one number 0..1 in `/logs/verifier/reward.txt`. Submission also needs at least one Harbor run log with its score and a short README. Source: organiser message relayed by Mikael.
- 2026-11-14 02:49 H1 is retired as the judged instance: six agent attempts, three models, all scored 1.0. itswinther asked B to build instance H2 with four changes: continuous score against an optimised reference, agent-chosen placement of several bodies, agent-chosen assembly order, and the H1 loopholes closed. Agreed: itswinther.
- 2026-11-14 02:58 SPEC.md is version 0.2: the judged instance is H2, specified in `environment/public/SPEC_H2.md`. Agreed: itswinther (asked for the four changes).
- 2026-11-14 02:58 Interface for A (H2): the grader call is `python -I tests/grade_h2.py /abs/base.stl /abs/lid.stl /abs/assembly.json --reward FILE [--details FILE]`; the three artifacts are `base.stl`, `lid.stl`, `assembly.json` (the door is gone). `python environment/make_bundle.py DIR` writes everything the agent may see. B says yes to running the tools inside the agent container: the bundle holds no weights, gate list, check code or reference.
- 2026-11-14 03:05 Board in a Box is scrapped as the challenge, both H1 and H2. Reason: clean agents score 1.0 on H1 and 0.97 on H2 within five minutes. The team will pick a new idea with a real gap. Decided: itswinther. The code stays in the repo for now; nothing depends on it.
- 2026-11-14 03:14 New challenge to test: "Moving Day". Fixed apartment mesh and N furniture meshes with given final poses; the agent submits one JSON with the carry-in order and a rigid pose-by-pose path per piece; score 0.5 p^2 + 0.5 [all delivered]. Nothing is designed, so there are no design loopholes. Decided: itswinther (other teammates are testing other ideas in parallel). B builds the hardest instance it can and measures it with clean agents before anything else is built.
- 2026-11-14 03:22 Interface for A (Moving Day): one artifact, `plan.json`. Grader call: `python -I tests/grade_md.py /abs/plan.json [--instance flat-1] --reward FILE [--details FILE]`. `python environment/make_bundle_md.py DIR` writes everything the agent may see; the tools are `tools/tools_md.py` and the agent may import `tools/geometry`. Units are centimetres.
- 2026-11-14 03:33 Moving Day stays in the back pocket: built and measured, but it shows no real gap (Fable 1.0, Opus 1.0). It is not the chosen challenge. Decided: itswinther.
- 2026-11-14 03:42 The mechanical watch gear train (write-up in `MECHANICAL_WATCH_IDEA.md`) is now the main idea. Moving Day, H2 and H1 are backups. Decided: itswinther.
- 2026-11-14 03:51 Interface for A (watch task): the artifact is a folder holding `movement.json` and `parts/<name>.stl`. Grader call: `python -I tests/grade_watch.py /abs/folder --reward FILE [--details FILE]`; it opens only the files `movement.json` names. `python environment/make_bundle_watch.py DIR` writes everything the agent may see. Grading the reference takes about 35 s.
- 2026-11-14 03:51 Choices B made while building the watch task, different from or beyond the write-up, open to a human no: (1) all arbors are parallel to z and this is stated; (2) the size limit is stated (radius 23, height 16), not hidden, because a hidden number we chose would be withheld information; (3) only the hour and minute hands must share an axis, since real watches often have a small seconds hand elsewhere; (4) the hand speeds, clockwise direction and that shared axis are the only unstated requirements; (5) the barrel is 96 teeth, module 0.2, 25 degree pressure angle, all stated; (6) the agent is not given a gear maker; (7) "held" accepts another mobile as the thing that holds a mobile, because an hour wheel rides on the centre arbor in real watches; (8) there is no minimum-feature (printability) check yet.
- 2026-11-14 04:13 Watch task, two changes agreed by itswinther: (1) three stages with frozen hand-over, each stage a fresh agent conversation: design; add a 24-hour hand to a frozen design; give an assembly order and paths for the frozen result. (2) For these runs the agent gets the full written contract, the raw geometry kernel and a format-only submit, but no test code and no measuring tools. This reverses the earlier "tools measure everything" principle on purpose; every graded number is still stated in the spec, except what a watch hand does.
- 2026-11-14 04:13 Interface for A (staged watch): `python -I tests/grade_watch.py /abs/folder --stage N [--prev /abs/previous_stage_folder] --reward FILE`. Stage 3 adds `assembly.json` to the folder. `python environment/make_bundle_watch.py DIR --stage N [--prev FOLDER] --tools no` writes what the agent may see. `environment/run_clean_chain.sh RUN_DIR MODEL` runs the three stages headless; `python tests/grade_chain.py RUN_DIR` grades them.
- 2026-11-14 04:34 Watch task: the minimum-thickness check is now a scored requirement ("printable", weight 1; stage 1 total 17, stage 2 total 21). Decided: itswinther. Runs made before this are graded with `WATCH_SKIP=printable`.
- 2026-11-14 04:47 Overnight plan agreed by itswinther: a new Fable 5.2 session orchestrates two Opus builders in separate worktrees and a Sonnet reviewer, unattended. Builder TASK adds a change-request stage, tightens the case to fit the reference, and makes the chain score the product of the stage scores. Builder CAD moves submissions to STEP from a real CAD kernel (CadQuery or build123d) and packages each run as a trajectory record. Spec changes inside that scope are pre-approved; each must be logged here with old and new values.
- 2026-11-14 04:55 (orchestrator, B) Deadline: the start message for this session says work until 10:00 Helsinki; the handoff file says 09:00. I use: stop building at 08:15, clean chains started by about 07:30 at the latest, everything finished before 10:00. Reason: the start message is the later instruction; the earlier stop for building is the conservative part of both.
- 2026-11-14 04:55 (orchestrator, B) CAD kernel for the agent and the grader is CadQuery 2.8.0 only (cadquery-ocp 7.9.3.1.1). build123d is not used. Reason: `pip install cadquery==2.8.0 build123d==0.13.0` fails with ResolutionImpossible (cadquery pins cadquery-ocp 7.9.3.1, build123d pins cadquery-ocp-novtk 8.0.1.x); one kernel that installs is the conservative option. Note for A: the task image needs `cadquery==2.8.0`.
- 2026-11-14 04:55 (orchestrator, B) Interfaces fixed before the builders started: stages are 1 design, 2 extend, 3 change (new), 4 assemble; grader call unchanged (`python3 -I tests/grade_watch.py /abs/folder --stage N [--prev /abs/prev] --reward FILE`); a part file is `parts/<name>.step`, or `parts/<name>.stl` until the reference is ported (`.step` wins if both exist); chain runs live in `RUN/stage1..stage4`.
- 2026-11-14 04:55 (orchestrator, B) The exact change request of stage 3 is written in the one spec document that every stage's agent receives. Reason: the rubric gives zero for a gap that comes from withheld information; with the change stated, a stage-1 agent can plan for it but cannot test it, which is the mechanism the handoff asks for.
- 2026-11-14 05:01 Stage 3 (change request) must be a change that a stage-1 agent cannot satisfy in advance: a different supplied barrel (tooth count, speed and/or direction), alone or together with a case change. A smaller case alone is ruled out, because with the change stated up front stage 1 would simply build small. Decided: itswinther (message to the orchestrator session). Sent to builder TASK at once.
- 2026-11-14 05:01 (orchestrator, B) Read section 10 of the handoff: no sandbox is built in this session (A has Harbor with GPT); any low chain score is checked against the grader's details and the submitted files before it is reported.
- 2026-11-14 06:07 SPEC.md is version 0.4: the task under test is the staged watch, specified in `environment/public/SPEC_WATCH.md`. Changes below were made by the builders inside the scope itswinther pre-approved at 04:47.
- 2026-11-14 06:07 Watch spec: stages are now 1 design, 2 extend, 3 change (new), 4 assemble (was stage 3). Stage 3: the same barrel turns clockwise once every 6 hours instead of 8 (`CHANGED_BARREL_TURNS_PER_HOUR = 1/6`, new); nothing is frozen; gates are files and assembled; the thirteen stage-2 checks (weight 21) are tested with the 6-hour barrel; the score is multiplied by `min(1, kept share / (15/17))` (`REF_KEPT_SHARE = 15/17`, new). A received part is kept if its file is byte-identical and it is still under `fixed`, or still in a mobile of the same name on the same axis that the declared meshes drive from the barrel. The reference keeps 15 of 17 files (it remakes the third wheel and the centre pinion, 60/30 to 54/36 at the same centre distance). Stage 4 is locked against the stage-3 submission.
- 2026-11-14 06:07 Watch spec: `CASE_RADIUS` 23.0 -> 20.7 and `CASE_HEIGHT` 16.0 -> 13.4, the same at every stage. The compacted reference reaches radius 20.354 and is 13.1 tall at its largest stage; limit = that plus 0.3, radius rounded up to one decimal (real margin 0.346).
- 2026-11-14 06:07 Chain score is the product of the four stage scores (was the mean of three); a stage not run or with nothing submitted counts as 0 (`tests/grade_chain.py`).
- 2026-11-14 06:07 Watch spec, part files: a part is `parts/<name>.step` (STL still accepted until the reference is ported; `.step` wins if both exist). New constants, all stated in the spec: `MAX_STEP_BYTES` 16,777,216; `STEP_LINEAR_DEFLECTION` 0.001 mm and `STEP_ANGULAR_DEFLECTION` 0.1 rad (tessellation); the file's length unit must be millimetre, other units are rejected, not converted; exactly one solid that passes the kernel's validity check; `STEP_MAX_TRIANGLE_FACES` 500 (more flat three-sided faces is treated as a mesh dump and rejected); `STEP_TIMEOUT_S` 120 and `STEP_MEMORY_MB` 4096 for the child process that reads a file; `MAX_SCRIPTS_BYTES` 4,194,304 and `MAX_SCRIPT_FILES` 200 for the copied `scripts/`; `SELF_UNION_TOL` 0.005 is the old hard-coded value under a name. Tessellation measured on a 96/12 pair at four tolerances from 0.01 to 0.0003 mm: worst overlap 0.0, largest gap 0.027, smallest drive overlap 0.063 at all of them (table in the 06:10 entry).
- 2026-11-14 06:07 (orchestrator, B) Harbor 0.26.0 offers only `mean` and `final` as `multi_step_reward_strategy` (read in `harbor/models/task/config.py`, class `MultiStepRewardStrategy`, from `pip install --no-deps harbor==0.26.0`; not run). There is no product. For a product in Harbor the last step's verifier has to grade all four stage folders and write the product, with strategy `final`. The product stays in `tests/grade_chain.py` either way.
- 2026-11-14 06:07 (orchestrator, B) The reviewer was started before my own grading of the merged reference had finished, which is not the order the handoff gives. Reason: my first grading attempt never started (see the entry), builder TASK had graded the same code at 1.0, and the merge had no conflicts. My run finished at 1.0 on all four stages while the reviewer was still reading.
- 2026-11-14 06:07 (orchestrator, B) Machine rule for tonight: one grader per lock (`flock /tmp/grade_slot_1` for the orchestrator and the reviewer, `/tmp/grade_slot_2` for builder CAD). A grader run peaks at 4.5 to 5.7 GB on a 15 GB machine and two runs were killed by the kernel.
- 2026-11-14 06:11 (orchestrator, B) After review round 1, three scoring rules change; all three are being built now and are stated in the spec. Reason for each: the reviewer ran the exploit. They go beyond the letter of the pre-approved scope (they touch stages 1 and 2 as well as the new stage), so a human should confirm or reverse them in the morning. (1) At every stage a hand's speed, and "driven from the barrel" in the kept rule, count only through declared meshes that pass the mesh test; before, speeds came from the declared tooth counts alone, and editing two tooth counts in `movement.json` scored 0.361 at stage 3 with kept factor 1.0. (2) New hard requirement at stage 2: a `day` hand is declared. Before, a stage-1 movement handed back unchanged scored 0.327 at stage 2. (3) New hard requirement at stage 3: the hour, minute, seconds and 24-hour hand requirements pass with the 6-hour barrel. Before, a stage-2 movement handed back unchanged scored 0.163 at stage 3. With (2) and (3) "hand back what you received" is 0 at every stage.
- 2026-11-14 06:11 (orchestrator, B) Also after review round 1: a part may not be named `barrel`; parts left out of the stage-4 `order` stand in their assembled position from the start and are not installed; the grader's `WATCH_SKIP` environment variable becomes a `--skip` flag recorded in the output; symlinked files in a submission are refused; limits that were enforced but unstated go into the spec (names at most 40 characters, tooth counts 3 to 1000, `movement.json` at most 1 MiB, `assembly.json` at most 64 MiB); the spec says the next stage receives `movement.json` and `parts/` but not `scripts/`.
- 2026-11-14 06:11 (orchestrator, B) Left as they are, for a human to decide: (a) the kept share counts part files, so a stage-1 design split into many files loses less at stage 3 (reviewer: 3 files lost of 17 gives factor 0.933, 3 of 57 gives 1.0); it is stated in the spec and a stage-1 agent can plan for it, but it measures file granularity as well as foresight. (b) Failing the size check alone costs 1.0 -> 0.443 by the score formula; the case margin over the reference is 0.346. (c) A mesh dumped into STEP as flat four-sided faces passes the faceted-file rule, which only counts three-sided faces; the spec does not claim more.
- 2026-11-14 07:28 Watch spec, after review round 2: the stage-2 hard requirement "a 24-hour hand is declared" now also needs the hand's part to be a new part, not one of the received parts. Before, pointing `hands.day` at the existing seconds hand passed the gate and scored 0.3612 for a one-line edit (reviewer's run). The stage-4 score text now names the Files requirement, which the grader already applied. No number changed.
- 2026-11-14 07:28 (orchestrator, B) STL part files are no longer accepted (builder CAD, phase B): a part is `parts/<name>.step` only; the supplied barrel stays `meshes/barrel.stl`. New named constants for limits that were already enforced: `MAX_ASSEMBLY_BYTES` 67,108,864; `MIN_TEETH` 3, `MAX_TEETH` 1000; `MAX_NAME_LEN` 40. `write_step` writes a neutral header (base file name only, no timestamp), so the same shape exported twice is byte-identical.
- 2026-11-14 07:28 (orchestrator, B) Order of acceptance: the full anchor run (27 of 27 ok) was made on commit 62e1f79. The round-2 fix (c0cd881: stage-2 new-part rule, two anchors' expected values, one spec sentence) was merged after it, and the chains were started on c0cd881 before the five stage-2 anchors were rerun. Reason: the anchor run took 44 minutes, the chains cannot share the machine with graders, and the fix changes nothing an honest agent sees except one sentence. The stage-2 anchors are rerun when the chains have finished and before any chain result is reported; c0cd881 is not pushed to main until then.
- 2026-11-14 07:28 (orchestrator, B) Open after two review rounds, not fixed, for a human: a hard link in a submission is accepted (it can only point at a file that exists in the agent's own container); `tools/submit.py` reports a symlinked part as "not a STEP file" instead of naming the symlink; the string "board-in-a-box" is in the header of `meshes/barrel.stl` and in a comment of `tools/kernel.py`, both visible to the agent; the reference's day-wheel pair passes the drive test at 0.0133 mm3 against the 0.01 limit (deterministic, but the thinnest margin in the reference).
- 2026-11-14 09:14 (orchestrator, B) Chain packages are committed in the packer's compact form (schema `watch-chain-pack/2`): each distinct part file once, gzip-compressed, under `parts_store/`, and a `parts.json` per stage in place of `submission/parts/`; `python3 tests/pack_run.py --unpack PACK OUT` rebuilds the files byte for byte. Reason: a plain package of one chain was 127 MB because every stage repeats the STEP files; the three compact packages are 8, 14 and 12 MB.
- 2026-11-14 09:14 (orchestrator, B) Chain result reported as measured, and the task is not changed after it: Fable 5.2 and Opus 5.5 score 1.0 at all four stages; Sonnet 5.5 scores 1.0, 1.0, 1.0, 0.468. Whether one model's shortfall on one chain is enough of a gap is a human decision (see the final entry).
- 2026-11-14 09:55 Proposals 1, 2 and 4 of the CAD-difficulty list are approved for building, all at once: itswinther ("Build 1, 2 and four all at the same time ... report back to me when done before testing"). Proposals 3, 5 and 6 are not started. No clean-agent chains are run on the new build until itswinther has had the report.
- 2026-11-14 09:55 (orchestrator, B) Rules fixed before the builders started, so four builders can work in parallel. (1) `light`, weight 2, stages 1 to 3: the fixed parts together at most `FIXED_VOLUME_MAX`, all mobile parts together (barrel not counted) at most `MOBILE_VOLUME_MAX`; both set from the reworked reference at its largest stage plus 10 percent, target at most 50 and 60 percent of today's reference; pass or fail, in line with the earlier decision that material is a check and not a multiplier. A rule on rounding concave corners is only adopted if builder LIGHT shows a threshold that is robust to how the voxel grid lines up. (2) Parts of one mobile may no longer overlap (added to the Assembled hard requirement, tolerance 0.01 mm3); `seated`, weight 2, stages 1 to 3: every part of a multi-part mobile, moved 0.3 along each of +x, -x, +y, -y, must intersect the rest of its mobile, and along +z or -z at least once; stage 4 tests a path against every part placed before it, parts of the same mobile included. (3) `tolerant`, weight 2, stages 1 to 3: every declared mesh passes the mesh test also with the driven mobile moved `MESH_SHIFT` = 0.03 away from and towards the driver's axis (0.02 if 0.03 cannot be met against the supplied barrel). Totals become 23 at stage 1 and 27 at stages 2 and 3 (24 and 28 with a corner rule).
- 2026-11-14 09:55 (orchestrator, B) Builder split: LIGHT, SEATED and TOLERANT each write one check (grader, engine, spec text, anchors, fixture tests) and do not touch the reference; REF alone reworks `solution/reference_watch.py` for all three rules and then merges the three check branches, sets the two volume limits and the totals, and adds the anchors that depend on the new reference. Reason: last night two builders in the same files merged cleanly only because their regions were apart; the reference would not be.
- 2026-11-14 10:12 Two directions from itswinther, now in `CLAUDE.md` under "Current focus" and binding on every session. (1) The goal is a real gap on frontier models (Fable, Opus, GPT class); a shortfall only on a mid-tier model is not the result. (2) No session limits its scope or thinking by the time left: no dropping or shrinking ideas because of the deadline, no proposals to freeze the task for safety, no settling for the claim we can already support. What to cut is the humans' call. This withdraws the parts of the 10:15 entry that proposed freezing the task at Sat 16:00 and presenting a mid-tier gap; the old "latest switch Saturday 16:00" line in `CLAUDE.md` is marked superseded.
- 2026-11-14 10:15 There is no timeline any more. The "Deadlines" section is replaced by "To do, in priority order", ordered by the four judging criteria, with the aim of excelling on every one whatever work it takes. The small-model training tiebreaker, cut on day one, is back on the list pending a human yes. Decided: itswinther.
- 2026-11-14 13:14 SPEC.md is version 0.5. Three requirements built on itswinther's go of 09:55, numbers as built (old -> new). Stage totals 17 -> 23 (stage 1) and 21 -> 27 (stages 2 and 3). (1) `light` [2], new: union of the fixed parts at most `FIXED_VOLUME_MAX` = 346 mm3, sum of all mobile parts (barrel not counted) at most `MOBILE_VOLUME_MAX` = 278 mm3, the same at every stage; both are the reworked reference at its largest stage (313.8 and 252.1) plus 10 percent, rounded up. My first target (half the old reference, 2117 and 512) was dropped after builder LIGHT measured that last night's Sonnet design already met it. (2) Assembled hard requirement: also no two parts of one mobile intersecting by more than 0.01 mm3 (before: parts of a mobile could overlap freely). `seated` [2], new: every part of a multi-part mobile moved 0.3 along each of +x, -x, +y, -y must intersect the rest of its mobile, along +z or -z at least once, and the parts of a mobile must form one piece (`SEAT_TOUCH` = 0.02, new). Stage 4 rule 5: a path is tested against every part placed before it, parts of its own mobile included (before: parts of one mobile were not tested against each other). (3) `tolerant` [2], new: every declared mesh also passes the mesh test with the mobile declared as driven moved `MESH_SHIFT` = 0.03 away from and towards the driver's axis. `mesh_run` cuts both mobiles to the near region and searches the gap to 0.15 before 1.0; old and new results agree to 7.6e-17 on 34 meshes.
- 2026-11-14 13:14 (orchestrator, B) Not adopted: a minimum radius for concave corners. On the 0.05 voxel grid a sharp pocket corner and one rounded at radius 0.2 give the same reading at five grid offsets, and every shoulder and pocket floor reads as a sharp corner (builder LIGHT's table, 10:27). `MESH_SHIFT` stays 0.03: honest textbook pinions pass up to 0.06 and Fable's and Opus's designs pass every mesh at 0.05; only one weak Sonnet mesh fails from 0.04, and choosing a number because it fails one model is not a reason.
- 2026-11-14 13:14 (orchestrator, B) Open, handed to the "Grader exploits fixes" session with the numbers (its fix 6): the mesh test is loose on tooth form. On the reference's fourth/seconds pair a pinion can lose about 30 percent of its tooth thickness before anything fails (first failure at a backlash allowance of 0.13, `tolerant` moved away) and a pitch error up to 5 percent passes (6 percent fails `tolerant` moved towards; on the barrel pair 3 percent does). itswinther asked at 11:13 that a thinned tooth and a small pitch error fail. A tight cap on backlash conflicts with `tolerant`, which needs about 0.028 of backlash to survive the towards shift.
- 2026-11-14 13:14 (orchestrator, B) `tests/test_anchors_watch.py` can hang: it forks a worker pool after the parent has built the reference with CadQuery and manifold. My run with two workers stopped at the ninth anchor with one worker asleep on a futex for 20 minutes. Until the runner is fixed, run each anchor in its own process: `python3 tests/test_anchors_watch.py 1 --base REF --only "NAME"` under a timeout. The runner fix is with this session; the exploits session only appends anchors.
- 2026-11-14 13:21 (orchestrator, B) The anchor runner no longer forks: `tests/test_anchors_watch.py` starts every anchor in a fresh interpreter (`--one INDEX`, driven by a thread pool of WORKERS) with a per-anchor timeout of 1500 s (`--timeout S` to override); a timeout or a crash prints an `OFF` line and the run exits 1. Command line and output lines are unchanged. Only `main()` changed. Checked by the orchestrator: `python3 tests/test_anchors_watch.py 2 --base REF --only "s1 do nothing,s4 gold,s4 no assembly.json,s4 centre before third"` printed four ok lines in list order, exit 0, 59 s; `--only "s4 gold" --timeout 3` printed `OFF  s4 gold  timed out after 3 s` and left no child process. The builder ran the anchor that hung before ("s1 one extra heavy mobile in a fixed cage") with two workers: ok. Not run: the full set through the new runner.

## Proposed spec changes

Append here. A human has to say yes before SPEC.md changes.

- 2026-11-14 01:55 **Clarifications SPEC 0.1 leaves open.** Proposed by itswinther + Claude (B). Status: awaiting yes/no. The grader already uses these values; each is one line in `geometry/constants.py` marked INTERPRETATION, so a no is cheap.
  - `assembly.json` format: `{"board": [...], "lid": [...], "battery": [...], "door": [...]}`, each a list of 4x4 row-major matrices mapping the body from its supplied frame to the world. Board, lid and door are supplied in their final pose, so their last pose is the identity. The battery's own frame is x 0..48, y 0..30, z 0..7.5; its lead face is x = 0 and its top face z = 7.5.
  - Keep-outs are centred on the connector body's section and start at its outer face: J1 y 16.25..28.75, z -0.25..6.75, x -1.5..-21.5; J2 centre (y 12, z -2.5), x 72.5..92.5. "Grown by r" is a rectangle offset by r (square corners) for J1 and a larger circle for J2.
  - "Wall mid-plane" for K3/K4 is a fixed plane: x = -1.05 for J1, x = 72.55 for J2.
  - G5: the "1.0 sphere" is a diameter. "The cavity" is anywhere within 1.5 of board A or the battery. The two windows are plugged with the grown-by-3 sections for x <= 0 (J1) and x >= 70 (J2).
  - Contract rule 1: "at least 30 from its final pose" is measured at the body's vertex centroid. "Wholly outside the envelope" means zero intersection volume with the envelope box.
  - F1 is measured on a slice at z = -0.05, over the ring between dia 3.2 and dia 7. F4 is the exact minimum surface distance. F5 needs a 48 x 30 face horizontal in the final pose.
  - W1/W2 voxel margins: a wall of 1.6 always passes, the allowed deviation is 0.5 + one 0.2 voxel = 0.7. In exact maths a sharp 90-degree solid corner sits 0.586 from the opened shape, so the bare 0.5 in the spec would fail every sharp box corner.
  - Reference volume (base + door) is 15072.56 mm3, so the material budget is 17333.44 mm3.
- 2026-11-14 09:44 **Make the staged watch harder through CAD difficulty.** Proposed by itswinther + Claude (B), after a search of 2026 CAD-agent benchmarks (sources in the entry of the same time). Status: awaiting a human yes/no per item; nothing is built. Ranked by expected effect for the build cost.
  1. **Mass budget that forces skeletonised wheels and plates.** State a maximum volume per wheel (or for the whole movement) that solid discs cannot meet, plus a minimum radius for concave corners. Wheels need spokes and rims near the 0.2 thickness limit. Why: in last night's chains all three models said in their reports that they had not run the thickness test (and Sonnet not the collision test) and passed only because their parts were chunky. Cost: volume is one line in the grader; the corner rule reuses the voxel code; the reference needs spoked wheels.
  2. **Assemble every part for real.** Drop the rule that parts of one mobile are not tested against each other at stage 4, and test "held" per part, not per mobile. Every wheel then needs a shoulder to sit on and something that retains it, designed at stage 1 and only tested at stage 4. Why: the only shortfall on two nights is a design that passes its own stage and cannot be assembled later. Cost: small in the grader, moderate in the reference.
  3. **A winding stem at right angles (new stage).** A stem enters through the case side and must turn the barrel through a crown or bevel pair, inside the frozen movement. Teeth on non-parallel axes cannot be made by extruding a 2D profile; they need lofted or generated surfaces that survive the STEP validity check. Why: published benchmarks report the largest drops on loft and sweep features and on gear mechanisms. Cost: high (mesh test for arbitrary axes, a bevel maker for the reference); probe with one single-stage clean run before building the stage.
  4. **The train must run with the arbors slightly out of place.** Repeat the mesh test with each driven arbor moved 0.03 towards and away from its driver. Why: it asks for real backlash and tooth depth, not nominal geometry; no published CAD benchmark tests tolerances. Cost: two more mesh runs per pair.
  5. **An intermittent date ring (new stage).** A ring that advances one step per day and is locked in between (Geneva-type, rigid parts only), graded by finding the collision-free angle of the driven part at each step. Cost: high (a contact-driven replay is new engine code).
  6. **Change request that edits geometry, with "kept" measured by volume.** Replace byte-identical kept files by the share of received material still in place, and choose a change that moves an axis (small seconds at 6 o'clock), so plates must be re-bored, not swapped. Fixes the open point that the kept share counts files.
  Not proposed: drawings as input (the one benchmark that splits it shows image-to-CAD as its easiest track, and we do not know that the judged agent sees images); a physics or FEA grader (the agent cannot rebuild it exactly, so differences look like noise); judged rubrics; hidden requirements.
- 2026-11-14 11:50 **Close the grader exploits found by the review.** Proposed by itswinther + Claude (review session). Status: **all seven approved by itswinther, 14 Nov 11:58**, to be built by the "Grader exploits fixes" session on top of B's `light`/`seated`/`tolerant` (branch `claude/confident-brown-ipeiud`). Each goes under Decisions with old and new rule when it lands in `SPEC_WATCH.md`; numbers for 5 and 6 are measured first. Full reasoning, reproduction and recommended rules in `HANDOFF_EXPLOITS.md`.
  1. Mesh test: two more no-jam poses after every eighth step, 1/3 and 1/5 of a grid step further on, so the test cannot be passed by tooth counts that differ from the real ones.
  2. Assembled (hard): the fixed parts form one frame (joined when their smallest distance is at most 0.01; the graph of joined parts is connected). The reference's barrel cock needs a foot.
  3. The train runs: every mobile is driven from the barrel through passing meshes. Held: only the frame holds, directly or through mobiles on the same axis that are themselves held in that direction; mobiles on another axis never count.
  4. Stage 3 kept share by volume, not by file, separately for fixed and for mobile parts, the smaller of the two against the reference's.
  5. Hands: a hand part lies wholly above every fixed part and its centre of volume is at least 1.0 from its axis.
  6. Drive test: a threshold that does not shrink with face width and module (an honest module 0.12 pair with a 0.5 face fails today at 0.0084 against 0.01).
  7. Thickness test run in slabs so that memory does not grow with part height; same pass and fail.

- 2026-11-14 12:40 **Grade the watch as a whole: an owner's acceptance test, scored in order.** Proposed by Mikael + Claude (A). Status: awaiting yes/no from the team; being tried first in `spikes/keyless/`, nothing in B's task changed.
  - Why: today a design earns most of its points part by part. A gear train with a winding mechanism that cannot hold its wind (no click, so the mainspring unwinds back through the crown) still scores high. GPT trial 1 in `spikes/right_angle/` did exactly that and scored 1.0, because that spike never asked for a click (see its README, "Known spec weakness"). A watch that stops when you let go of the crown is not most of a watch.
  - Proposed spec wording: "The movement is graded the way a watchmaker accepts a finished watch: by using it. The grader runs one fixed sequence of operations on the assembled movement, in order, the way an owner would. A step only counts if every step before it passed. Part-level checks (clearances, support, printability) are conditions on the whole; they do not earn points on their own."
  - Sequence, from a flat mainspring: (1) wind: crown in, turned forward N turns, the mainspring stores the stated turns; (2) hold: let go, the click holds, nothing spins back; (3) run: the train drives the hands at the right rates for at least the stated power reserve, from the stored turns; (4) backward: crown turned backward, nothing winds or jams, stored turns stay; (5) set: crown pulled and turned, the hands move, the barrel does not unwind; (6) return: pushed in and wound again, never half-engaged on the way.
  - Score: consecutive steps passed from step 1 divided by the number of steps, times the part-level conditions. No click gives about 0.17, with a one-line reason anyone can check ("it cannot hold its wind").
  - What it serves: meaningful difficulty (every shortfall has an owner's-eye explanation), the gap (it rewards how parts work together over time, which is where every frontier shortfall so far came from: decisions that pass locally and fail later), and reward integrity (part-level tricks earn nothing unless the whole works).
  - What it needs in B's task: a winding stage (the keyless works: crown, stem, sliding pinion with Breguet teeth, crown and ratchet wheels, click, setting lever; prototype in `spikes/keyless/`), a stated mainspring model (capacity in turns, running at the barrel's stated speed) and the in-order scoring. The existing stage 4 assembly test fits as step 0: it has to assemble before it can be used.
  - Real-world basis: the end-of-line functional test of a finished watch (wind, check it holds, check it runs, set the hands). Results of the keyless trial with old and new scoring will be posted here.

## Ideas for later

Parked ideas. Not proposals: nothing here changes SPEC.md. Move one to "Proposed spec changes" to put it to the team.

- 2026-11-14 01:25 **"No screws allowed": every body clicks into place.** Proposed by Yoseph + Claude. Status: parked as an idea for later, not proposed to the team. Would need its own spec version if ever adopted.
  - **Why:** SPEC 0.1 says "screws are out of scope, parts are assumed screwed down", so nothing holds the board, lid or door. Tool-free snap-fit assembly is a real design-for-assembly rule, gives a better story for judges, and adds a constraint that interacts with the ones we already have (see "Interactions").
  - **Replaces** the Limits line "Screws are out of scope ... no check tests retention against a pull" with: "No fasteners, glue or press-fit pins. Board A, lid and door must each be held by printed geometry. The battery is held by the door (F3, unchanged)."
  - **How a snap is modelled while staying rigid-body (the hard part).** A snap arm has to bend while it is inserted, but the replay only moves rigid bodies. So the agent declares its snap arms in `assembly.json`, and gives a bend angle per pose:
    `"arms": [{"name": "lid_px", "part": "base", "box": [[x0,y0,z0],[x1,y1,z1]], "root": "-z", "bend": "+x"}]`, and each pose may carry `"arms": {"lid_px": 0.04}` (radians).
    The grader takes the printed material inside `box` as a separate rigid piece. At each pose it rotates that piece about the box's root edge by the declared angle, then applies the normal 0.2 mm3 intersection rule against everything else, the rest of its own part included. This is the pseudo-rigid-body model, simplified to a pivot at the root, which is conservative.
  - **What the grader checks on each arm (the agent's declaration is never trusted):**
    1. Material inside the box touches the rest of the part only across the root face. Voxel test, 0.2 voxels, so a gap needs to be at least 0.4 wide to count.
    2. Strain: the grader measures t at the root and L along the box itself. With tip deflection y = L·sin(angle), max strain is 3·t·y / (2·L²), and it must stay at or below 2.0 % (PLA, assumed). For example, t 1.6 with L 10 allows y of 0.83 mm; L 8 allows only 0.53.
  - **Contract additions (format errors fail G4):** at most 8 arms; arm boxes may not overlap; arms only on printed parts; every angle is 0 in the final pose of every body; a change in angle moves the arm tip at most 0.5 per step (same as rule 3).
  - **Where a broken arm counts:** over-strain or a non-free arm fails the path check (A1 to A4) of the body that was moving at that pose, not a gate. This keeps the decision "paths are weighted checks, not gates".
  - **New checks** (each weight 1; the spec goes from 19 checks / weight 23 to 22 checks / weight 26):
    - R1 Board retained: moving board A 0.6 along +Z makes its bare PCB intersect printed parts by more than 0.2 mm3.
    - R2 Lid retained: moving the lid 0.5 along +Z intersects the base by more than 0.2 mm3.
    - R3 Door retained: moving the door 0.5 along -Z intersects the base by more than 0.2 mm3.
  - **Envelope:** the lid is a supplied flat plate whose top is at z 15.5, so a hook over it needs z max to go from 12.5 to 17.25 (15.5 + 1.6 lip + 0.15).
  - **Interactions that make it harder:** the gap around an arm has to be at least 0.4 to count as free (check 1) but below 1.0 or shielded, or G5's 1.0 sphere gets through; arms must be at least 1.6 thick (W1) yet long enough to flex; board hooks must stay 0.4 from J1, J2 and C1 (F4) and must not catch during the tilt-and-slide path; the door latch must clear the battery (A3, F5).
  - **Anchors to add:** pegs but no hooks (fails R1 to R3); an arm declared over a solid wall (fails A-path by check 1); a stubby arm bent too far (fails A-path by strain); hooks that never deflect (fails A-path by intersection).
  - **Tools:** `sweep` also returns the peak strain per arm and its pose index (a geometry fact, no pass/fail). `get_spec` publishes the strain limit and the arm format.
  - **Cost:** B adds arm extraction, rotation and strain to the shared geometry module, plus three latch sets in the reference, roughly half a day. A adds an `arms` passthrough in `sweep`. D adds four anchors.
  - **Timing:** nothing is built yet, and arms change the core of the path replay. So the cheapest moment to decide is before B writes the replay code, which is tonight. If the team would rather not risk the Sat 07:00 spike, the fallback is to keep it as the difficulty lever for Sat 09:00, used if H1 turns out too easy for the judged agent.
  - **Not verified:** that a reference with latches can pass every gate and check; the 2.0 % strain limit for PLA; that 0.2 voxels resolve the arm gap reliably.
  - **Review by B (itswinther + Claude), 01:35, by hand only:** as written it likely makes H1 easier, because a 20 mm tall wall section declared as an arm may flex 3.3 mm and the board needs only 1.7 mm to drop straight in; the lid hook has no room in x/y (the lid covers the whole footprint); rotating a rigid arm about its root edge intrudes about 0.3 mm3 into its own part. A rigid-only version (door on rails, R3 only) needs no arm code.
- 2026-11-14 03:30 **Mechanical watch gear train: a new challenge, as an alternative to Moving Day.** Proposed by Abhishek + Claude. Status: parked as an idea, nothing built or run. Full write-up in `MECHANICAL_WATCH_IDEA.md`. In short: the agent gets a minimal brief ("design the gear train of a mechanical watch, driven by this barrel turning once per 8 h") and must infer the unstated but universal rules (hour 1 per 12 h, minute 1 per h, seconds 1 per min, clockwise, coaxial hands). The grader checks exact ratios from declared tooth counts, then rotates the train with the existing rigid-pose replay and overlap test (no jam, still engaged, teeth drive, hands clear). Estimated 1.5 to 2 person-days; the reference movement is the critical path.

## Session entries

Template:

```
### YYYY-MM-DD HH:MM | workstream | human name + Claude
- Did:
- Verified by (command and result):
- Not verified, or assumed:
- Files changed:
- Need from others:
- Next:
```

### 2026-11-14 00:50 | setup | Claude
- Did: created the repo with README.md, CLAUDE.md, SESSION.md, SPEC.md.
- Verified by (command and result): nothing to run yet.
- Not verified, or assumed: every number in SPEC.md was checked by hand only. No code exists. The spike has not run.
- Files changed: all four, new.
- Need from others: assign owners in the table above. Fill in mentor answers.
- Next: workstream A starts from the organisers' starter kit.

### 2026-11-14 01:25 | none assigned (spec proposal) | Yoseph + Claude
- Did: read README.md, SPEC.md 0.1, SESSION.md and CLAUDE.md. The repo holds only these docs; there is no code and no workstream owner yet. Wrote the "No screws allowed" proposal under Proposed spec changes. Snap arms are declared in assembly.json and bent rigidly about their root at each pose, under a strain limit of 2.0 %. Added retention checks R1 to R3 (board, lid, door), and raised envelope z max to 17.25.
- Verified by (command and result): `python3 -c` gave cantilever allowed tip deflection y = 2·eps·L²/(3·t) for t 1.6 and eps 0.02: L 8 -> 0.533, L 10 -> 0.833, L 12 -> 1.2. Nothing else can be run yet.
- Not verified, or assumed: the reference can pass with latches; the PLA strain limit of 2.0 %; that 0.2 voxels resolve a 0.4 arm gap. SPEC.md is unchanged.
- Files changed: SESSION.md only (Proposed spec changes, this entry).
- Need from others: a yes or no from the team on the proposal before B starts the path-replay code.
- Next: if yes, edit SPEC.md to 0.2 and log it under Decisions. If no, leave SPEC 0.1 as it is.

### 2026-11-14 01:35 | E analysis, demo, story | Yoseph + Claude
- Did: Yoseph owns analysis, demo and story. CLAUDE.md lists no workstream for that, so I added row E to the Current state table. The folders and the CLAUDE.md table are not changed. Pushed the "no screws allowed" proposal to main at Yoseph's request, so the other sessions see it.
- Verified by (command and result): `git fetch origin main` showed main still at ddf8bfa before the push.
- Not verified, or assumed: that the team accepts an E row. If not, fold it into D.
- Files changed: SESSION.md (row E, this entry).
- Need from others: a yes or no on the no-screws proposal (Proposed spec changes) before B writes the path-replay code.
- Next: draft the demo story and the analysis plan (which numbers and transcripts we show).

### 2026-11-14 01:40 | B + shared docs | itswinther + Claude
- Did: rewrote the communication part of CLAUDE.md. Reason: sessions were pushing to separate `claude/...` branches and could not see each other's SESSION.md. New rules: `origin/main` is the only shared channel, each session asks its human once for permission to push to `main`, re-reads SESSION.md before each new piece of work, and uses the new "Requests" section here for cross-workstream asks. Added workstream E to the CLAUDE.md table. Set owners: A Mikael (he adds the starter kit), B itswinther, E paused (Yoseph is not working overnight). C and D are unowned tonight.
- Verified by (command and result): `git branch -r --no-merged origin/main` listed `origin/claude/busy-davinci-idw73v` (commit b303740, "Park 'no screws allowed' under Ideas for later"), which is not on main.
- Not verified, or assumed: that every session's human allows pushes to `main`. The grader entry point in the Requests line is B's assumption until A confirms it.
- Files changed: CLAUDE.md, SESSION.md (owner rows A, B and E, Requests section, this entry). Touching rows A and E is outside my own row; done on itswinther's instruction.
- Need from others: A answers the request above. Someone merges b303740 or drops it.
- Next: B builds `geometry/`, the supplied bodies, the reference script and the grader against SPEC 0.1 unchanged.

### 2026-11-14 01:55 | B reference and grader | itswinther + Claude
- Did: built `geometry/` (constants, STL load, supplied bodies, contract rules, pose replay, voxel checks, all 5 gates and 19 checks, score), `tests/grade.py` (the grader), `solution/reference.py` (parametric reference: tub, two windows, four posts, two pegs, lap door, board path), and `tests/test_anchors.py` (14 anchors). SPEC.md is unchanged; what it leaves open is listed under Proposed spec changes.
- Verified by (command and result):
  - `python3 solution/reference.py OUT` printed `base volume 11816.57, door volume 3256.00, total 15072.57 mm3; poses {'board': 280, 'lid': 89, 'battery': 101, 'door': 101}`.
  - `cd tests && python3 -I grade.py OUT/base.stl OUT/door.stl OUT/assembly.json --reward OUT/reward.txt` printed all gates and checks true except M1 (reference volume was not yet set), in 6.0 s. After setting `REFERENCE_VOLUME`, the anchor run gives the reference S = 1.0000.
  - `python3 tests/test_anchors.py` (about 50 s): reference 1.0; do nothing, half-written file, NaN path, teleporting path, non-rigid pose 0; wall removed 0 (G5, K3); U-slot to rim 0 (G5); clash in final pose 0 (G3); lazy tub 0.2127; straight-down board path 0.3781 (A1 only); no pegs 0.4575 (F2 only); J2 window too narrow 0.4575 (K2 only); blind J2 pocket 0.3062 (A1, K2, W1).
  - Reference margins: F4 J2 clearance 0.5 (limit 0.4); K3 open area 89.5 of 130.5; K4 59.9 of 78.5; W1 and W2 deviation 0.49 of 0.7; F2 +X volume 2.77 mm3 (limit 0.2); every path replays with 0.0 mm3 intersection.
- Findings:
  - The reference board path differs from the internal note. It tilts 15 degrees, not 20 to 25, and there is no vertical drop: the board flattens to 1.2 degrees, slides back with its -X end 1.4 above the posts, then rotates the last 1.2 degrees onto the pegs. A vertical drop would need both closed windows to be taller.
  - A blind J2 pocket cannot fail K2 alone: it also blocks the board path (J2 pokes 0.7 past the outer wall during the slide). The anchor table's "blind pocket, about 0.46" row is replaced by "J2 window too narrow for the round plug", which does fail K2 only.
- Not verified, or assumed: nothing has run inside Harbor or a container. Worst-case grading time (200,000 triangles, 2,000 poses per body) is not measured; replay is one boolean per pose per placed body. A mesh that is manifold but self-intersecting is not fully normalised by the self-union. The per-check timeout uses SIGALRM, so it needs Linux and the main thread. The reward file path defaults to `/logs/verifier/reward.txt` and is a guess until A confirms it. No agent has attempted the task, so difficulty is unknown.
- Files changed: `geometry/`, `tests/`, `solution/`, `requirements.txt`, `.gitignore`, SESSION.md (row B, proposal, this entry).
- Need from others: A, the grader call is `python -I tests/grade.py /abs/base.stl /abs/door.stl /abs/assembly.json --reward FILE [--details FILE]`; it needs `geometry/` next to or one level above `grade.py` and the packages in `requirements.txt`. The MCP tools should import `geometry.core` and `geometry.contract` (`replay`, `check_contract`, `ivol`, `min_distance`, `section_x`), never `geometry.checks`. A human yes or no on the clarifications.
- Next: measure worst-case grading time, write the public spec text and task instruction for the agent, add the parameter-sweep anchors (rule 2 of the anchor suite).

### 2026-11-14 02:05 | B + repo housekeeping | itswinther + Claude
- Did: (1) applied by hand the content of Yoseph's stranded commit b303740 (branch `claude/busy-davinci-idw73v`): the "No screws allowed" write-up now sits under "Ideas for later", parked. A git merge would have duplicated the block because SESSION.md uses a union merge. That branch still shows as unmerged in git; its content is on main. (2) Corrected my own earlier timestamps: entries I had stamped 02:00 and 03:00 were written at about 01:40 and 01:55 Helsinki (`date -u` is the check; Helsinki is UTC+2). (3) Reviewed the project against the organisers' judging rubric; summary below.
- Verified by (command and result): `git branch -r --no-merged origin/main` lists `claude/busy-davinci-idw73v` (handled above) and `claude/fervent-brown-cb0201`. The second holds one commit, cfa6313 "Add raw Cala API coverage test responses", 26 JSON files under `cala-tests/`. It looks unrelated to this project and is not merged. `git log origin/main` shows no commit from workstream A yet and no starter kit in the repo.
- Rubric review (gap 30, meaningful difficulty 30, reward integrity 25, craft 15):
  - Gap: unknown. No agent has run. The reference was written in one pass by a Claude session that had the full spec and the hand-worked path hint, which is weak evidence that a frontier agent may also solve it. This is the largest open risk.
  - Meaningful difficulty: SPEC 0.1 was ambiguous in about ten places (see the clarifications under Proposed spec changes). If the agent-facing spec leaves any of them unstated, failures will come from withheld information, which the rubric scores as zero. The agent-facing spec and task instruction do not exist yet.
  - Reward integrity: do-nothing scores 0 and 14 anchors behave. Open holes: grading time for a large honest submission is unmeasured (a slow path check fails by timeout); self-intersecting meshes are not normalised; any gate failure gives exactly 0, so a near-complete design with one bad pose scores the same as doing nothing.
  - Craft: nothing runs in Harbor and there is no one-command evaluation.
- Not verified, or assumed: that the `cala-tests` branch is unrelated; I did not open the JSON files.
- Files changed: SESSION.md only.
- Need from others: see Requests.
- Next: write the agent-facing spec and a command-line version of the tools, then run a first agent attempt outside Harbor to measure the gap before anything else is built.

### 2026-11-14 02:04 | B first agent attempt (starting) | itswinther + Claude
- Did: starting now. Plan: write `environment/public/SPEC_PUBLIC.md` (agent-facing spec with every clarification stated) and `environment/tools_cli.py` (the measurement tools as a command line over `geometry.core` and `geometry.contract`), copy only those plus the supplied meshes into a clean folder, and give a fresh agent that folder and nothing else. This touches `environment/`, which is workstream A's folder; A has nothing there yet, and the MCP server can wrap the same functions.
- Verified by (command and result): nothing yet.
- Not verified, or assumed: the attempt runs outside Harbor with this session's model as the agent, so it is a first signal, not the judged setup.
- Files changed: SESSION.md.
- Need from others: nothing new.
- Next: report the agent's score, what it failed and why.

### 2026-11-14 02:15 | B first agent attempt (result) | itswinther + Claude
- Did: gave a fresh agent (a subagent of this session, same model) a clean folder holding only `INSTRUCTION.md`, `SPEC_PUBLIC.md`, the supplied meshes and the tools (`tools_cli.py` plus `geometry/` without `checks.py`). Then graded what it submitted. Also measured grading time on a large submission.
- Verified by (command and result):
  - `cd tests && python3 -I grade.py .../agent1/submission/base.stl .../door.stl .../assembly.json` printed `"reward": 1.0, "p": 1.0, "strict": true`, all 5 gates and 19 checks true.
  - The agent took 4 min 54 s, 7 tool calls, about 110,000 tokens, one 66-line build script, one submission. It did not iterate: the first build passed every measurement it ran.
  - Its design matches the reference in every main decision: raised floor with the door lapped outside, tilt 16 degrees, slide +X, flatten, slide -X, drop 2.0. It located the board in +X with a block on the wall instead of pegs.
  - Grading time: a 123,392-triangle base and 19,200-triangle door with 2,000 poses per body graded in 16.3 s and scored 1.0.
- Finding: H1 as specified shows no gap against this model. The task is a fully stated numeric constraint problem with tools that measure every constraint, and the agent solved it in one pass.
- Not verified, or assumed:
  - The run was contaminated: the harness injects the repo's CLAUDE.md into subagents, and CLAUDE.md contains the "Internal note for workstream B" that describes the board path. The agent reported this itself. An uninformed agent might do worse, but one sentence of hint does not explain a 5-minute perfect score.
  - The judged model and harness are unknown; this was not run in Harbor or OpenCode. One run only.
- Issues the agent reported in the tools and spec: `constants.py` in the tools bundle shows check IDs, weights and the reference volume, and comments name `SESSION.md` and `solution/reference.py`; the tools help mentions a `--battery-pose` option that does not exist; `distance` stops at 5.0 and the spec does not say so; no tool gives the ring area or the lead distance directly; nothing requires the base to be a tub or the door to be retained.
- Files changed: `transcripts/agent1/` (the agent's script, its three submitted files, grader details), SESSION.md.
- Need from others: a human decision. Options: (a) rerun clean after removing the internal note from CLAUDE.md, to confirm; (b) make H1 harder; (c) give Hold the Line an owner now. See Open questions.
- Next: nothing built until the decision.

### 2026-11-14 02:20 | A harness wiring | Mikael + Claude
- Did: started workstream A. Relaying the organisers' "Required Stack" message, which the team has not seen. Read Harbor's public docs and source for the points A depends on. Installed tooling on Mikael's Mac.
- Organiser message, in short:
  - Framework is Harbor (github.com/laude-institute/harbor). The environment is a Harbor task: `instruction.md`, `task.toml`, `environment/Dockerfile`, `tests/`, `solution/`.
  - Harness: they "urge" OpenCode: `harbor run -p ./my-task -a opencode -m [provider/model]`.
  - Reward: the verifier writes one score between 0 and 1 to `/logs/verifier/reward.txt`. Partial credit is welcome.
  - Before submitting: at least one Harbor run log with its score; a short README (what the agent does, why it is hard, how it is scored; they warn AI-written READMEs may communicate poorly); playthroughs encouraged in the demo video.
  - AfterQuery provides NO inference credits. Use the Google, OpenAI and Modal sponsor credits.
  - "What we're looking for: super cool simulations, environments, and some post-training experiments." Post-training is the tiebreaker and is now named outright; we cut it from scope.
  - No starter kit or scoring skeleton is mentioned anywhere. CLAUDE.md's "Starter kit wins" rule and several open questions assumed one.
- Verified by (command and result):
  - `uv tool install harbor` then `harbor --version` printed `0.25.0`. `harbor agent list` includes `oracle`, `nop`, `opencode`.
  - Harbor source cloned at v0.26.0. `grep -n -i mcp src/harbor/agents/installed/opencode.py` shows the agent writing task-declared MCP servers into OpenCode's config (lines 839 to 858, 927 to 929).
  - `examples/tasks/sidecar-artifacts/task.toml` shows `environment_mode = "separate"` and artifacts declared one file at a time, optionally from a named sidecar service.
  - `brew install --cask docker` reports Docker Desktop installed. Not yet started, no container run.
- Not verified, or assumed: nothing has run in Harbor yet. Harbor docs say multi-step tasks start a fresh agent conversation per step, compose sidecars run on Modal only through Docker-in-Docker, and the default verifier is shared (separate is opt-in); all read, none run.
- Proposal from A, needs a human yes (interface between A and B): run the MCP tool server INSIDE the agent's container over stdio, not as a compose sidecar. Reason: SPEC 0.1 never says how a sidecar reads a mesh the agent just wrote (separate filesystem, and a model cannot pass an STL as a tool argument); in-container needs no compose file, so it also runs on Modal. Cost: the agent can read the tool source, so the tools bundle must hold only geometry primitives. B's 02:15 entry says `constants.py` in the bundle currently exposes check IDs, weights and the reference volume; that file needs a public/private split before this is safe.
- On B's 02:15 result (H1 scored 1.0 in 5 minutes): A's work is the same for either idea, so A continues. Note for the decision: the organisers no longer supply the model, so "the judged agent" is whatever we can run on Google/OpenAI credits through OpenCode, which may be weaker or stronger than the subagent B tested. A clean rerun in the real harness is the measurement that counts.
- Files changed: SESSION.md (row A, two requests answered, five open questions answered, one decision line, this entry).
- Need from others: B, a yes or no on in-container tools, and the `constants.py` split. Anyone with sponsor credits: an OpenAI or Google API key for the first OpenCode run (do not commit it).
- Next: build the Harbor task (`task.toml` with separate verifier and three single-file artifacts, `environment/Dockerfile`, `tests/test.sh`, `solution/solve.sh`), then run `oracle` (expect 1.0) and `nop` (expect 0).

### 2026-11-14 02:27 | B agent attempts 2 to 6 (result) | itswinther + Claude
- Did: removed the board-path note from CLAUDE.md, then ran five more attempts at H1 with the same instruction, public spec, meshes and tools. Attempts 2 to 4 were subagents of this session. Attempts 5 and 6 were started with the headless command line (`claude -p ... --model M --permission-mode acceptEdits --output-format stream-json`) from a folder outside the repo.
- Verified by (command and result): each submission graded with `cd tests && python3 -I grade.py <three absolute paths>`.

  | Attempt | Model | Context | Score | Time | Submissions | Notable |
  | --- | --- | --- | --- | --- | --- | --- |
  | 1 | Fable 5.2 | saw the hint | 1.0 | 4 min 54 s | 1 | floor door, tilt 16 degrees |
  | 2 | Fable 5.2 | saw the hint | 1.0 | 4 min 36 s | 1 | battery through a side door |
  | 3 | Opus | saw the hint | 1.0 | 7 min 56 s | 1 | battery above the board, floating 1.7 above the PCB |
  | 4 | Sonnet | saw the hint | 1.0 | 5 min 35 s | 1 | two colliding tilts fixed with `sweep` before submitting |
  | 5 | Fable 5.2 | clean | 1.0 | 4 min 59 s, 6 turns, $1.68 | 1 | tilt 15 degrees, floor door |
  | 6 | Sonnet 5.5 | clean | 1.0 | 4 min 40 s, 7 turns, $0.51 | 1 | no tilt at all: base is a floorless ring, the door is the whole bottom, the board goes straight up from below |

  For attempt 6 I checked first that a command-line agent started outside the repo has no project instructions: `claude -p "what project instructions are in your context, or NONE"` printed `NONE`.
- Findings:
  - No gap. The two clean runs scored 1.0, so the hint was not what made it easy.
  - Attempts 2 to 4 were still contaminated: the harness cached CLAUDE.md at session start, so removing the note from the file did not remove it from subagents. Each of them quoted the note back.
  - Attempt 6 avoids the intended difficulty completely. Nothing requires the base to have a floor or the board to enter from above, so the wall below each connector opening can belong to the door and the board needs no tilt.
  - Attempt 3 shows the public spec never says the battery sits below the board, and nothing checks that the battery is supported from below.
  - No attempt needed a second submission. The measuring tools let the agent confirm every requirement before submitting.
- Not verified, or assumed: the judged model, harness and time limit are unknown; none of this ran in Harbor or OpenCode.
- Files changed: CLAUDE.md (internal note removed), `environment/tools_cli.py` (help text), `transcripts/agent1` to `agent6` (submitted files, agent scripts, grader details; full transcripts for 5 and 6), SESSION.md.
- Need from others: a human decision on the open question "harden Board in a Box or move to Hold the Line".
- Next: nothing built until that decision.

### 2026-11-14 02:49 | B instance H2 (starting) | itswinther + Claude
- Did: starting H2 on itswinther's instruction. Design: supplied bodies are board A (unchanged), a second board B with a card slot, the battery and a speaker. The agent chooses every body's final pose and the insertion order, and makes `base.stl` plus a flat `lid.stl`. Score = gates x (0.3 p^2 + 0.7 q if every check passes), where q falls linearly with the bounding-box volume of the printed parts, 1 at the reference volume. Code goes in `geometry/h2.py`, `solution/reference_h2.py`, `tests/grade_h2.py`; H1 files stay as they are.
- Verified by (command and result): nothing yet.
- Not verified, or assumed: whether H2 produces a gap. No agent runs until itswinther says so.
- Files changed: SESSION.md.
- Need from others: nothing.
- Next: report when the reference and anchors pass.

### 2026-11-14 02:58 | B instance H2 (built) | itswinther + Claude
- Did: built instance H2. Supplied bodies: board A (unchanged), board B (38 x 27.5 PCB with shield, card slot J3 and inductor), battery, speaker. The agent chooses every final pose and the insertion order, and makes `base.stl` and a flat 2.0 `lid.stl`. Four gates (files, final pose, path format, enclosed) and 17 checks (weight 20). Score: 0 if a gate fails; 0.3 p^2 if a check fails; otherwise 0.3 + 0.7 x size, where size falls linearly from 1 at the reference bounding-box volume (81,343.3 mm3) to 0 at 95,000 mm3. H1 loopholes closed: the second part must be a flat plate, so the base needs a floor and closed windows; every body must rest on something; the door is gone.
- New files: `geometry/h2_public.py` (bodies, public numbers, measurements), `geometry/h2_checks.py` (grader only), `tests/grade_h2.py`, `tests/test_anchors_h2.py`, `solution/reference_h2.py`, `environment/tools_h2.py`, `environment/make_bundle.py`, `environment/public/SPEC_H2.md`, `environment/public/INSTRUCTION_H2.md`. SPEC.md header now points to H2.
- Verified by (command and result):
  - `python3 solution/reference_h2.py OUT` printed `bounding box [74.85, 48.3, 22.5], volume 81343.2 mm3; poses {'B': 130, 'speaker': 126, 'A': 280, 'battery': 114, 'lid': 89}`.
  - `cd tests && python3 -I grade_h2.py OUT/base.stl OUT/lid.stl OUT/assembly.json --reward R` printed reward 1.0, p 1.0, size_term 1.0, all gates and checks true.
  - `python3 tests/test_anchors_h2.py`: 13 of 13 as expected. Reference 1.0; do nothing 0; lid smaller than the opening 0 (enclosed); lid not a plate 0 (files); oversize J1 window 0 (enclosed); no J3 window 0 (final pose); teleporting path 0; valid with floor 3 lower 0.444; valid with floor 12 lower 0.300; wrong order 0.217; floating battery 0.271; blocked J1 keep-out 0; no pegs 0.271.
  - `python environment/make_bundle.py DIR`, then in DIR `python3 tools/tools_h2.py bbox` and `submit` on the reference files: bbox volume 81343.2, "accepted". `grep` for WEIGHTS, REFERENCE, SESSION, solution, h2_checks in the bundle's tools found nothing.
  - `python3 tests/test_anchors.py` (H1) still 14 of 14.
- Reference layout: B and the speaker on the floor under board A (the space under A is exactly B's height, 6.8), A on four posts, battery on top of A, order B, speaker, A, battery, lid. Board A uses the H1 tilt path.
- Not verified, or assumed:
  - Whether H2 produces a gap. No agent has run on it.
  - That the reference is close to the smallest possible. I argued by hand that no layout gives a lower height; I did not search. If an agent finds a smaller valid design it scores 1.0 and the reference volume must be lowered to match.
  - The 95,000 zero point is my choice, set so that a careful but conventional layout lands near 0.5.
  - Nothing has run in Harbor.
- Files changed: those listed, plus SPEC.md and SESSION.md.
- Need from others: A, see the interface line under Decisions; artifacts changed from `door.stl` to `lid.stl`.
- Next: run clean agents on H2 when itswinther says go.

### 2026-11-14 03:05 | B first H2 agent result, and the decision to scrap | itswinther + Claude
- Did: started three clean agents on H2 at once (Fable 5.2, Opus 5.5, Sonnet 5.5) with `claude -p` from fresh bundle folders outside the repo. Before starting, a probe agent in the same folder answered `NONE` when asked what project instructions or memory were in its context; no CLAUDE.md exists up the folder tree; `work/` and `submission/` were empty.
- Verified by (command and result): Sonnet finished first. `python3 -I tests/grade_h2.py` on its submission printed reward 0.9733, p 1.0, size term 0.962, bounding box 81,864 mm3 (reference 81,343), nothing failed. It took 3 min 50 s, 8 turns, $0.38, 2 submissions, and all 7 tool calls stayed inside its folder.
- How it did it: the same layout as the reference (board B under board A, battery and speaker on top). It avoided the tilt path by making the box 2 mm longer and dropping every body straight in, and recovered the volume by probing the wall-thickness test and using 1.4 walls.
- Finding: H2 has no meaningful gap either. A continuous score, free placement and free order did not help: the layout search is small enough to reason through in one pass, and the tools confirm each choice immediately.
- Decision by itswinther: scrap H1 and H2 and choose a new challenge.
- Not verified, or assumed: the Fable and Opus runs were still going when this was written; results will be added if they finish.
- Files changed: `transcripts/h2_sonnet/`, SESSION.md.
- Need from others: A, the Harbor wiring is still useful for any new idea, but do not build further around `grade.py` or `grade_h2.py`.
- Next: wait for the new idea. Lesson to carry over: test any idea with a clean agent run within its first hour.

### 2026-11-14 03:14 | B Moving Day (starting) | itswinther + Claude
- Did: starting the Moving Day measurement on itswinther's handoff. First instance is the hardest I can author: a corner sofa that must be carried on its back, tipped on end in the right direction under a 258 ceiling and walked round an L-corridor; a 232-tall wardrobe that only tips upright one way under a 238 ceiling; and two pieces whose final poses block the others' routes. Code goes in `geometry/md.py`, `tests/grade_md.py`, `solution/reference_md.py`, `environment/tools_md.py`.
- Verified by (command and result): nothing yet.
- Not verified, or assumed: that this produces a gap.
- Files changed: SESSION.md.
- Need from others: nothing.
- Next: reference at 1.0, anchors, then two or three clean agent runs.

### 2026-11-14 03:22 | B Moving Day flat-1 (built, agents running) | itswinther + Claude
- Did: built Moving Day. `geometry/md.py` (public engine: apartment as a solid block with air boxes cut out, pieces as unions of boxes, path rules, delivery replay, score), `tests/grade_md.py`, `solution/planar.py` and `solution/reference_md.py` (reference plan from a small planar A* plus scripted tips), `environment/tools_md.py`, `environment/make_bundle_md.py`, `environment/public/SPEC_MD.md` and `INSTRUCTION_MD.md`, `tests/test_anchors_md.py`. SPEC.md is version 0.3.
- Instance flat-1 (cm): front door 86 wide and 205 high; hall; a 125-wide corridor with a 205-high doorway part way along and an L-turn into the living room; a bedroom with a 238 ceiling behind an 86-wide door; other ceilings 258. Pieces and weights: sofa 4 (L-shaped, 240 x 160 x 80), wardrobe 3 (60 x 45 x 232), bookcase 1, chest 1. Step limit 5, pose cap 4,000, volume tolerance 1 cm3.
- Where the difficulty is, none of it stated in the agent's spec:
  - Order: the bookcase's final pose leaves 70 of corridor width, so the sofa must go first; the chest's final pose blocks the bedroom door, so the wardrobe must go first. The spec lists the pieces as bookcase, chest, wardrobe, sofa.
  - Sofa: it only passes the 86 door on its back, cannot turn the corridor corner lying down, and standing on end it is 240 tall so it cannot pass the 205 doorway. It has to be tipped on end after the doorway, and only one tipping direction fits under 258 (256.3 needed; the other needs 288).
  - Wardrobe: it only stands up about its 45 edge (236.3 under 238; the 60 edge needs 239.6), and has to be turned in the hall to reach the bedroom.
- Verified by (command and result):
  - `python3 solution/reference_md.py OUT` took 12 s and printed `poses {'sofa': 612, 'bookcase': 151, 'wardrobe': 357, 'chest': 112}`.
  - `cd tests && python3 -I grade_md.py OUT/plan.json --reward R` printed reward 1.0, all four delivered, in 0.4 s.
  - `python3 tests/test_anchors_md.py`: 17 of 17. Gold 1.0; do nothing, invalid JSON, oversized file, teleporting to the final poses and straight lines through walls all 0; gold paths in the listed order 0.025; easy pieces only 0.025; everything but the sofa 0.154; sofa dragged without standing it up 0.154; wardrobe tipped the wrong way 0.222; a bad chest or bookcase path 0.395; a duplicate and an unknown name ignored (1.0); 0.0002 into a door frame still delivered (0.8 cm3, inside the tolerance) and 0.5 into it not.
  - A flood over every planar state of the sofa lying on its back (3.5 cm, 2 degree grid, 14,474 states) never turns more than 28 degrees, so it cannot round the corner that way.
  - Bundle check: `make_bundle_md.py`, then `tools_md.py sweep` and `submit` on the reference plan inside the bundle: all four pieces at 0.0 volume, "accepted".
- Not verified, or assumed: whether agents fail. That the sofa has no other route (for example tilted in 3D); I only excluded the planar one. Nothing has run in Harbor.
- Files changed: those listed, SPEC.md, SESSION.md.
- Need from others: A, see the interface line under Decisions (one artifact now).
- Next: grade the three agent runs and report.

### 2026-11-14 03:31 | B Moving Day flat-1 agent results | itswinther + Claude
- Did: ran three clean agents on flat-1 at once with `claude -p` from fresh bundle folders outside the repo (probe agent answered `NONE` for pre-loaded context; no CLAUDE.md up the tree; empty work and submission folders). Graded each `submission/plan.json` with `python3 -I tests/grade_md.py`.

  | Model | Score | Time | Tool calls | Submissions | Cost |
  | --- | --- | --- | --- | --- | --- |
  | Fable 5.2 | 1.0 | 3 min 27 s | 6 | 1 | $1.36 |
  | Opus 5.5 | 1.0 | 8 min 52 s | 20 | 3 | $1.79 |
  | Sonnet 5.5 | 0 (no submission) | 8 min 25 s | 15 | 0 | $0.40 |

  No tool call in any run touched a path outside its own folder.
- What they did: Fable and Opus both found the two order traps from the numbers, carried the sofa on its side, stood it on end in the one direction that fits (both quote 256.3 under 258, and 288 for the other way), wrote their own position-and-angle grid search for the corner, and stood the wardrobe up about its 45 edge (236.3 under 238). Opus hit two dead ends first (a wall strike leaving the south corridor, and a corner turn 0.4 cm into a wall because its search area ended at the wall) and went through bookcase and chest, then sofa, then all four. Sonnet started two background path searches and ended its turn saying it would continue when they reported; a headless run is never woken, so it submitted nothing.
- Finding: no gap for Fable or Opus on the hardest instance I could author. The task did cost Opus and Sonnet much more work than H1 or H2 (20 and 15 tool calls against 12 or fewer). Sonnet's zero is partly an artifact of running headless and should not be read as a clean failure.
- Also recorded: the last two H2 runs finished earlier. Fable 1.0 (bounding box 80,804) and Opus 1.0 (77,770), both smaller than my H2 reference (81,343).
- Not verified, or assumed: a rerun of Sonnet told not to stop while searches run; any non-Claude model; anything in Harbor or OpenCode.
- Files changed: `transcripts/md_fable`, `md_opus`, `md_sonnet`, `h2_fable`, `h2_opus`, SESSION.md.
- Need from others: a human decision. Per the handoff's own rule (clean agents at 1.0 on the hardest instance means stop and report) I have stopped building.
- Next: nothing until told.

### 2026-11-14 03:55 | A (spikes) | Mikael + Claude
- Did: after B's six 1.0 runs, tested three other task shapes on Fable 5.2, Sonnet and Opus via headless `claude -p` in clean folders outside the repo (no web, no subagents). Code, instances, agent outputs and transcripts are in `spikes/` and `holdtheline/`. Summary in `spikes/README.md`.
- Verified by (command and result):
  - Hold the Line (`holdtheline/`, workstream C folder, which had no owner): `python3 policies.py 60` gives the scripted reference a mean of 9,849; do-nothing 0, ship-blind, never-ship, sort-all, over-adjust and stop-early all score 0 to 0.12 on average. On one hidden seed the agents scored: Sonnet 9,926 and Opus 10,285 (both above the reference 9,744), Fable 97 (played one slot, then the headless session ended while it waited on its own background job; not a real result).
  - Wrist tracker for children 6 to 10 (`spikes/wrist_tracker/`): one-sentence brief plus a parts list. All three returned a sensible child-sized device: 31 to 34 mm wide, 13 to 14 mm thick, 20 to 29 g, straps, rounded edges, display on top, charge contacts on the skin side. Sizes and masses measured from the STLs; the rest from the agents' own reports and renders.
  - Watch gear train (`spikes/gear_train/`): `python3 watch.py grade inst_1.json runs/<model>/design.json ref_1.json` gives Fable 1.0 (11 min 36 s, $0.87), Opus 1.0 (10 min 10 s, $0.43), Sonnet 0.917 (1 min 53 s, $0.20; one extra layer). All three wrote an exhaustive search.
- Findings: every fully specified, checkable task was turned into a program by the agent. Unstated common sense (child wrist size) was inferred unprompted. No spike shows a gap against these models.
- Not verified, or assumed: one instance per spike, Claude models only; nothing ran in Harbor or OpenCode. The gear-train reference is a random planted movement, not an optimum. The gear train's power-reserve objective is trivially maxed (no torque limit), so its score is half meaningless.
- Files changed: new `spikes/` (README, gear_train, wrist_tracker), `holdtheline/` (sim, policies, server, agent kit, results); SESSION.md (row A, this entry). No existing files of other workstreams touched.
- Need from others: the team decision under Open questions is still open, and these results bear on it.
- Next: harness work (Harbor task around B's grader) whichever idea wins.

### 2026-11-14 03:51 | B watch task, first runnable version | itswinther + Claude
- Did: built the mechanical watch gear-train task from `MECHANICAL_WATCH_IDEA.md`. `geometry/watch.py` (public: movement.json parser, exact speeds from tooth counts, free-spin, held, mesh-run and clearance measurements), `geometry/watch_gears.py` (involute gear maker, not shipped to the agent), `geometry/data/barrel.stl`, `tests/grade_watch.py` (2 gates, 10 checks, weight 16; the required hand speeds live only here), `solution/reference_watch.py`, `environment/tools_watch.py`, `environment/make_bundle_watch.py`, `environment/public/SPEC_WATCH.md` and `INSTRUCTION_WATCH.md`, `tests/test_anchors_watch.py`.
- Verified by (command and result):
  - Two-gear check of the mesh test: barrel with a correct 12-tooth pinion gives overlap 0.0, largest gap 0.027, drive overlap 0.051; the same pinion declared as 13 teeth jams (0.103 mm3); moved 0.4 further away it disengages (gap 0.216, drive overlap 0.0).
  - `python3 solution/reference_watch.py OUT` wrote 11 parts. `cd tests && python3 -I grade_watch.py OUT --reward R` printed reward 1.0 with both gates and all 10 checks true, in 35 s. Speeds from the tool: centre 1, hour wheel 1/12, seconds 60 clockwise turns per hour.
  - Bundle: `tools_watch.py speeds`, `spin`, `held`, `mesh`, `clear`, `extent`, `submit` all ran on the reference inside a fresh bundle. `grep` for the hand speeds, the gear maker and "reference" in the bundle found nothing.
- Reference train: barrel 96 to 24, 60 to 30 (centre, minute hand), 90 to 12, 96 to 12 (seconds); motion work 12 to 36 and 12 to 48 (hour wheel, a tube round the centre arbor). Two meshes between barrel and centre are needed because one mesh would turn the minute hand anticlockwise.
- Not verified, or assumed: whether agents fail; the anchor script was still running when this was written; no printability check; nothing in Harbor.
- Files changed: those listed, SESSION.md.
- Need from others: Abhishek, see the choices listed under Decisions and say if any is wrong.
- Next: grade the three agent runs and report.

### 2026-11-14 03:58 | B watch task, agent results | itswinther + Claude
- Did: ran three clean agents on the watch task with `claude -p` from fresh bundle folders outside the repo (probe agent answered `NONE` for pre-loaded context; no CLAUDE.md up the tree; empty work and submission folders; the bundle holds no hand speeds, gear maker, grader or reference). Graded each submission folder with `python3 -I tests/grade_watch.py`. The anchor script also finished: `python3 tests/test_anchors_watch.py` gave 7 of 7 as expected (gold 1.0; nothing 0; missing part 0; barrel not held 0.383; hands swapped 0.281; seconds mesh undeclared 0.195; one tooth count wrong 0.096), in 2 min 50 s while the agents were using the machine.

  | Model | Score | Time | Tool calls | Cost |
  | --- | --- | --- | --- | --- |
  | Fable 5.2 | 1.0 | 4 min 27 s | 5 | $1.66 |
  | Opus 5.5 | 1.0 | 7 min 38 s | 10 | $1.22 |
  | Sonnet 5.5 | still running at the time of writing (21 tool calls, nothing submitted yet) | | | |

  No tool call in the two finished runs touched a path outside its own folder.
- What they did: both inferred the unstated requirements (hour 1/12, minute 1, seconds 60 clockwise turns per hour, hour and minute on one axis) without comment, both noticed that one mesh from the barrel would turn the minute hand anticlockwise and added a reversing stage, both wrote their own involute gear generator, and both chose a centre seconds hand with its arbor through a hollow minute tube inside the hour tube, matching centre distances by using different modules. Fable's first build passed every check. Largest mesh gap 0.018 to 0.023 against the 0.1 limit.
- Finding: the two things A's spike had not tested (an unstated brief, and real gears turned by the grader) do not create a gap for Fable or Opus.
- Defects the agents found in the bundle: the docstring of `geometry/watch.py` mentioned a gear maker that is not shipped (fixed in this commit); the `clear` tool returns step -1 both when it skips a pair on bounding boxes and when it finds no overlap (not fixed).
- Not verified, or assumed: Sonnet's result; any non-Claude model; anything in Harbor or OpenCode; a printability check does not exist.
- Files changed: `transcripts/watch_fable`, `transcripts/watch_opus`, `geometry/watch.py` (docstring), SESSION.md.
- Need from others: a human decision on what to try next.
- Next: add Sonnet's result when it finishes; nothing else until told.

### 2026-11-14 04:13 | B staged watch task with test code withheld (built, chains running) | itswinther + Claude
- Did:
  - Sonnet's single-stage watch run finished: 1.0 in 16 min 55 s, 26 tool calls, $1.22, nothing outside its folder. So the single-stage watch task with tools is 1.0 for all three models.
  - Closed the loophole Fable used (an idler kept down only by another wheel above it): for the two moves along z, "held" now only accepts fixed parts or a mobile on the same axis. Fixed parts must not overlap each other.
  - Added stage 2 (add a 24-hour hand; the existing mobiles' axes and part files are frozen; fixed parts may change) and stage 3 (assembly order and rigid paths for every part, step 0.2, parts of one mobile exempt from each other). `tests/grade_watch.py --stage N --prev FOLDER`.
  - Added the withheld bundle: `environment/make_bundle_watch.py --tools no` ships INSTRUCTION, SPEC, the barrel, `tools/kernel.py` (a copy of `geometry/core.py`) and `tools/submit.py` (format only, generated from `environment/submit_template.py`). The spec now defines the mesh test exactly (turning direction, angles per step).
  - Reference for all three stages in `solution/reference_watch.py`.
- Verified by (command and result):
  - `python3 solution/reference_watch.py OUT` then `python3 -I tests/grade_watch.py OUT/stageN --stage N [--prev OUT/stage(N-1)]`: stage 1 reward 1.0 (42 s), stage 2 reward 1.0 (51 s; day hand 1/24 clockwise turns per hour, axis 10.04 from the hour axis, reach 3.21), stage 3 reward 1.0 (2 s; 18 parts, 1,209 poses).
  - Stage 3 on the reference with the order changed: centre before third gives 0.446 (third not installed); bridge straight after the main plate gives 0.222 (six parts not installed); no assembly.json gives 0.
  - Withheld bundle: `tools/submit.py` answered "accepted" for the reference at stages 1 and 3. `grep` for the hand speeds, the gear maker, the mesh test and `Fraction` in the bundle found nothing.
  - Clean-context probe in the run folder answered `NONE`.
- Not verified, or assumed: the staged anchor script is not written (only the three order checks above); `tools_watch.py` has no stage 2 or 3 tools, so a with-tools arm of the staged task cannot be run yet; `tests/test_anchors_watch.py` was written for the old single-frame reference and has not been rerun since the reference was split into separate plates.
- Files changed: `geometry/watch.py`, `tests/grade_watch.py`, `tests/grade_chain.py`, `solution/reference_watch.py`, `environment/make_bundle_watch.py`, `environment/submit_template.py`, `environment/run_clean_chain.sh`, `environment/public/SPEC_WATCH.md`, `SPEC_WATCH_GIVEN_NOTOOLS.md`, `INSTRUCTION_WATCH_S1/2/3.md`, `transcripts/watch_sonnet`, SESSION.md.
- Need from others: nothing.
- Next: grade the three chains and report.

### 2026-11-14 05:10 | A harness + spikes (Mikael asleep; Claude working on his instruction) | Mikael + Claude
- Did: (1) got Harbor running sandboxed with Codex on Mikael's Codex credits (`CODEX_FORCE_AUTH_JSON=1`, model `openai/gpt-6.1-sol`); (2) built a five-step watch-movement Harbor task (`spikes/gear_task/`): going train under a torque limit, motion work, a larger balance, a date wheel, automatic winding with a rotor-turns band; (3) built a watch-regulation task (`spikes/regulate/`) whose physics lives in a compose sidecar the agent can only query; (4) wrote `spikes/IDEAS_CODE_IS_NOT_ENOUGH.md`.
- Verified by (command and result):
  - Network probe tasks (`harbor run -a oracle`): `no-network` blocks everything; `allowlist` with chatgpt.com reaches only chatgpt.com (example.com, pypi.org, api.openai.com, 1.1.1.1 blocked). Codex under the allowlist ran and reported it could reach nothing else.
  - Five-step watch task: oracle 1.0 on all 5 steps, nop 0.0 on all 5. `harbor run -p watch-s8 -a codex -m openai/gpt-6.1-sol -k 3 -n 3`: 1.0, 1.0 and 0.6 as first graded; the 0.6 was a grader bug (the hour wheel meshes two gears from step 4, the grader kept one partner), fixed in `movement.py`; the regraded designs are valid, so GPT scored 1.0 x3. Whole job 5 min 47 s. GPT also used fewer layers than the planted reference.
  - Regulation task (seed 4242): oracle 1.0 (true error 45.2 s/day), nop 0.0 (116.3). Over 60 seeds the scripted watchmaker cuts mean error from 118.4 to 26.9 s/day.
  - Transcript audit of all 15 GPT steps: no network commands, no reads outside /app.
- Findings: the five-step movement shows no gap. Every model so far turns a fully stated, checkable problem into code and solves it. The regulation task is the first with hidden, noisy, costly measurement and irreversible actions; its results decide whether that pattern works.
- Sandbox gap found and sealed: sidecars share the agent's network namespace under egress control; the sidecar's result endpoint now needs a token stored only in the sidecar image (not in the repo). Residual: DNS resolves inside locked containers; the Codex login sits in the agent container (local Docker only).
- Not verified, or assumed: one seed per task; GPT-6.1-sol only in Harbor; the planted watch reference is not optimal (GPT beat it on layers).
- Files changed: `spikes/gear_task/` (movement.py, build_task.py, harbor_task_s8, runs_gpt), `spikes/regulate/` (timing.py, server.py, timer.py, BRIEF.md, build_task.py, harbor_task_s4242), `spikes/IDEAS_CODE_IS_NOT_ENOUGH.md`, `spikes/README.md`, SESSION.md (row A, this entry).
- Next: regulation results, then whichever idea shows a gap gets more seeds.

### 2026-11-14 04:34 | B staged watch chains, test code withheld: results | itswinther + Claude
- Did: ran `environment/run_clean_chain.sh` for three models (one fresh headless conversation per stage, bundle built with `--tools no`), graded with `WATCH_SKIP=printable python3 tests/grade_chain.py RUN_DIR` because these agents' spec had no thickness rule. Also acted on a five-point review from itswinther (see below).

  | Model | Stage 1 design | Stage 2 add 24-hour hand | Stage 3 assemble | Chain mean |
  | --- | --- | --- | --- | --- |
  | Fable 5.2 | 1.0 (5.9 min, 5 calls) | 1.0 (4.8 min, 8 calls) | 1.0 (1.4 min, 6 calls) | 1.00 |
  | Opus 5.5 | 1.0 (10.3 min, 10 calls) | 1.0 (4.0 min, 9 calls) | 1.0 (1.6 min, 9 calls) | 1.00 |
  | Sonnet 5.5 | 1.0 (7.0 min, 8 calls) | 1.0 (3.9 min, 11 calls) | 0.44 (1.7 min, 10 calls) | 0.81 |

  No stage was killed by the 39-minute limit. No tool call left its folder (the grader flagged one Opus call; it was the string `../../meshes/barrel` in dead code inside its own script).
- The one failure, and it is inherited: Sonnet's stage-1 design gave every mobile a foot of radius 1.0 below the main plate on a 0.5 shaft through a 0.6 hole, with the wheel above the plate. That satisfied "held" at stage 1, where assembly was not tested, but no rigid path can put the one-piece plate on. The stage-3 agent diagnosed this correctly, installed 15 of 16 parts and left the plate out: `main_plate` hits `barrel` by 171.9 mm3. The stage-1 instruction and spec did say the movement would be assembled part by part later.
- Findings: (1) withholding the test code did not lower any stage-1 or stage-2 score; Sonnet was faster without the tools (7 min) than with them (17 min). (2) Freezing earlier work produced the first real shortfall of the night against any model: a stage-1 choice that passes its own checks but breaks a later stage. It happened for one model in one chain, so it is one data point.
- Review points handled: anchors rewritten for three stages, `python3 tests/test_anchors_watch.py` gave 17 of 17 as expected with the grader as it was before the thickness check; the foreground rule and the 39-minute stop are now in the three instruction files; `tests/grade_chain.py` prints "KILLED BY THE TIME LIMIT" and splits stage-2 failures into inherited and new; thickness check added (`geometry/watch.py` `thin`, 0.05 grid, ball radius 0.1, deviation limit 0.2) and scored.
- Sandbox: `dockerd` starts in this cloud session, `docker pull python:3.13-slim` worked, `uv tool install harbor` gave 0.26.0. Containers cannot reach the network proxy without extra settings (host network, the proxy CA), and there is no model API key in this environment.
- Not verified, or assumed: the reference and the anchors have not been rerun since the thickness check became scored (a run was in progress when this was written); nothing has run in Harbor yet; one chain per model only.
- Files changed: `tests/grade_watch.py`, `tests/grade_chain.py`, `tests/test_anchors_watch.py`, `geometry/watch.py`, `solution/reference_watch.py`, `environment/public/SPEC_WATCH.md`, the three instruction files, `transcripts/watch_chain_*`, SESSION.md.
- Need from others: A, do you already have a Harbor task skeleton that runs (`oracle`, `nop`)? If so push it; I can run Harbor here too. A model API key is needed for sandboxed agent runs.
- Next: confirm the reference at 1.0 with the thickness check, rerun the anchors, package the stages as Harbor tasks.

### 2026-11-14 05:30 | A regulation results | Mikael + Claude
- Did: ran GPT-6.1-sol via Codex three times on the watch-regulation task (`spikes/regulate/harbor_task_s4242`), sandboxed (allowlist chatgpt.com only, separate no-network verifier, sealed sidecar).
- Verified by (command and result): `harbor run -p regulate-s4242 -a codex -m openai/gpt-6.1-sol -k 3 -n 3`: rewards 1.0, 1.0, 1.0, job 2 min 6 s. Final true error 18.15 s/day in all three (untouched 116.27, scripted reference 45.22). Each measured all 12 conditions, fitted R, K_iso, H, u, A0, dV, dW by least squares (scipy), added all four washers to fix poise, set the regulator to -1. Same final error because the remaining error is the dial-up/down and isochronism terms that no adjustment can change, and the regulator slop draw came after the same 12 measurements in every run (replayed and checked).
- Findings: no gap. With the formula's structure stated, hidden numbers plus noise plus a budget is a fitting problem the model solves. The scripted reference is also weak (it ignores washers and isochronism). This instance's watch also runs fast beyond the adjustment range, which puts a floor under everyone.
- Transcript audit: every command was the timer CLI, local Python, or file writes in /app; no network attempt, no reads of other paths. All three final messages said they used only the brief, /app and the timing machine.
- Files changed: `spikes/regulate/runs_gpt/`, `spikes/README.md`, `spikes/IDEAS_CODE_IS_NOT_ENOUGH.md`, SESSION.md.
- Next: needs a human decision (see the ideas file): the only levers left that I can see reduce what the agent is told (unstated model structure, scarcer measurements).

### 2026-11-14 04:47 | B handoff for the overnight orchestrator | itswinther + Claude
- Did: wrote `HANDOFF_OVERNIGHT.md` (context, state, build plan, definition of done, how to orchestrate) and `HANDOFF_PROMPT.md` (the message to paste into a new Fable 5.2 session). Added a "Current focus" note to `CLAUDE.md` saying Board in a Box is retired and the watch task is current. Confirmed the reference with the thickness check scored.
- Verified by (command and result): `python3 solution/reference_watch.py OUT` then `python3 -I tests/grade_watch.py OUT/stageN --stage N [--prev ...]`: reward 1.0 at stages 1, 2 and 3 with "printable" true; grading took 160 s, 177 s and 2 s on a loaded machine. Largest thickness deviation in the reference: 0.15 mm (the day wheel) against the 0.2 limit. `pip download` found wheels for cadquery 2.8.0, build123d 0.13.0 and cadquery-ocp 8.0.1.1.0 for Python 3.13.
- Not verified, or assumed: the anchor script has not been rerun since "printable" became scored (the handoff tells the next session to do it first). Nothing in the handoff's build plan exists yet. The orchestration itself (worktrees, model overrides, heartbeat) is untested.
- Files changed: `HANDOFF_OVERNIGHT.md`, `HANDOFF_PROMPT.md`, `CLAUDE.md` (Current focus note only), SESSION.md.
- Need from others: A, the overnight session will put what Harbor needs (grader call, artifact list, image packages incl. cadquery) under Requests once the STEP path works; sandboxed runs stay with A.
- Next: the overnight session.

### 2026-11-14 06:00 | A regulation, scarce budget | Mikael + Claude
- Did: added a 100-minute variant of the regulation task (watches always fixable within the adjustment range; a scripted reference for the short budget: 4 vertical positions x 18 min, one dial-up check, poise by removal, then regulate). Ran GPT-6.1-sol via Codex twice on each of 6 hidden watches (seeds 101 to 106), sandboxed as before.
- Verified by (command and result): over 60 seeds the scarce reference cuts mean error from 85.1 to 14.7 s/day. Harbor oracle 1.0 and nop 0.0 on seed 101. GPT scores 1.0, 1.0, 0.976, 0.934, 0.870, 0.959, 1.0, 0.947, 1.0, 1.0, 1.0, 1.0 (mean 0.974); GPT's error was below the reference's on 7 of 12 runs; reference/agent error ratio averaged 1.19.
- Findings: no gap. GPT spreads short measurements over all 12 conditions and fits the full stated model; the reference concentrates on vertical positions; neither dominates. Large run-to-run variance on one watch (s103: 17.9 vs 11.7 s/day).
- For B's overnight build: my five-step movement allowed revising earlier parts and showed no gap; this supports B's finding that freezing earlier stages is the lever.
- Sandbox: zero network commands across all 12 runs.
- Files changed: `spikes/regulate/` (budget variant, harbor_tasks_100min, runs_gpt_100min), `spikes/README.md`, ideas file, SESSION.md.

### 2026-11-14 04:55 | B overnight orchestrator: builders started | itswinther + Claude (unattended)
- Did: took over row B as the handoff describes. Synced (`git fetch origin && git rebase origin/main`: branch up to date with main at 7e004be). Installed the packages. Started the baseline anchor run on the inherited code. Started two Opus builder agents, each in its own git worktree, with stand-alone briefs: builder TASK (new change-request stage between extend and assemble, kept-parts factor, compacted reference and a case sized to it plus 0.3, chain score as the product, anchors and instruction file for the new stage) and builder CAD phase A (STEP submissions read with OCP and tessellated into manifold3d, agent-side STEP helpers and submit, a private CAD gear maker with a mesh test, `tests/pack_run.py`). Set a 30-minute heartbeat.
- Verified by (command and result):
  - `pip install manifold3d==3.5.5 scipy trimesh` then `pip install cadquery==2.8.0`: installed (cadquery-ocp 7.9.3.1.1). A CadQuery cylinder exported to STEP and imported again has volume 12.566. `pip install cadquery==2.8.0 build123d==0.13.0` fails: ResolutionImpossible (see Decisions).
  - `git branch -r --no-merged origin/main` lists `claude/busy-davinci-idw73v` (content already on main by hand, see 02:05) and `claude/fervent-brown-cb0201` (`cala-tests/`, looks unrelated; request to its owner is still open).
- Not verified, or assumed: nothing from the builders exists yet. The baseline anchor run had not finished when this was written.
- Files changed: SESSION.md (row B, four Decisions lines, this entry).
- Need from others: nothing yet. A: the STEP path will need `cadquery==2.8.0` in the task image; the grader call and artifact list follow once it is merged.
- Next: merge TASK, then CAD phase A; run the reference and a bundle build; start CAD phase B and the Sonnet reviewer.

### 2026-11-14 06:07 | B overnight orchestrator: TASK and CAD phase A merged, reference 1.0 on four stages | itswinther + Claude (unattended)
- Did: merged builder TASK (one commit) and builder CAD phase A (four commits) into the orchestrator branch; both merges were clean. Built the reference and a bundle for every stage and graded the reference myself. Sent builder CAD its phase B brief (port the reference to the CAD kernel, clean STEP headers, anchors on STEP, then stop accepting STL). Started the Sonnet reviewer (round 1) on the merged commit. Bumped the SPEC.md header to 0.4.
- What was built (builders' reports, each run by the builder):
  - TASK: stage 3 "change" (6-hour barrel, kept-parts factor), stage 4 "assemble", compacted reference and the case sized to it, chain product, 21 anchors (was 17), `INSTRUCTION_WATCH_S3.md` and `S4.md`. Builder's runs: reference 1.0 at stages 1 to 4; `python3 tests/test_anchors_watch.py 2` exit 0 after 1521 s, 21 of 21 ok (stage-3 anchors: gold 1.0; do nothing 0; stage-2 handed back unchanged 0.1633; every part file regenerated 0; a kept fixed part regenerated 0.9333; a kept mobile renamed 0.9333; old third wheel as a fixed ornament 0; day train undriven 0.2621).
  - CAD phase A: STEP read with OCP in a child process (timeout, memory limit), tessellated into manifold3d; `tools/kernel.py` gets the same reader plus `write_step`; `tools/submit.py` checks STEP and copies `scripts/`; private `geometry/watch_gears_cad.py`; `tests/test_cad_gears.py`; `tests/pack_run.py`. Builder's runs: `python3 tests/test_cad_gears.py` PASS (worst overlap 0.0, largest gap 0.0273, smallest drive overlap 0.0633); a stage-1 folder with 7 parts rebuilt as STEP graded 1.0; an inch STEP in its place gives 0 with a format error; submit rejects broken, inch, metre, two-solid, shell-only, oversized and faceted STEP files.
  - Tessellation measurements (96-tooth and 12-tooth, module 0.2; linear deflection mm / angular rad: triangles 96, 12; worst overlap; largest gap; smallest drive overlap): 0.01/0.5: 7900, 1404; 0.0; 0.0274; 0.0630. 0.003/0.2: 8668, 2074; 0.0; 0.0273; 0.0632. 0.001/0.1 (chosen): 10202, 4542; 0.0; 0.0273; 0.0633. 0.0003/0.05: 13656, 5868; 0.0; 0.0272; 0.0636.
- Verified by (command and result), run by the orchestrator on the merged tree (commit 39124d5):
  - `python3 solution/reference_watch.py OUT`: wrote stage1 to stage4 in 2.2 s ("stage1 parts 14 stage2 parts 17").
  - `cd tests && flock /tmp/grade_slot_1 python3 -I grade_watch.py OUT/stageN --stage N [--prev OUT/stage(N-1)] --reward rN.txt --details dN.json`, one after another: stage 1 reward 1.0 (173 s, peak 5254 MB); stage 2 reward 1.0, gates files/assembled/locked true (177 s, 5728 MB); stage 3 reward 1.0, kept_factor 1.0 (238 s, 4552 MB); stage 4 reward 1.0, 18 of 18 parts installed (109 s including waiting for the lock).
  - `python3 environment/make_bundle_watch.py Bn --stage n [--prev ...]` for n = 1 to 4: all built. `grep -rnI "HAND_SPEED|DAY_SPEED|Fraction|mesh_run|watch_gears|reference|SESSION|CLAUDE|solution|WEIGHTS|grade_watch"` over the four bundles matches only the spec's English "for reference" (twice) and "a reference solution".
- Went wrong: (1) the baseline anchor run on the inherited code that the handoff asks for first reached 5 of 17, all ok, and was then killed by the kernel for memory while both builders were grading; it was not repeated because the anchor script was being replaced. (2) My first grading of the merged reference at 05:34 never started: I wrapped it in `/usr/bin/time`, which does not exist here, and did not check the process. Found at 05:54; about 20 minutes lost.
- Not verified, or assumed: I have not run the 21 anchors on the merged tree myself (the builder did on its own branch); that waits for the phase B merge so it runs once on the STEP reference. No clean agent has seen the new stage or the tighter case. Nothing in Harbor. The reviewer has not reported.
- Files changed: everything in the two builders' lists above, `SPEC.md` (header), SESSION.md (row B, spec version line, Decisions, one request to A, this entry).
- Need from others: A, see the new request.
- Next: merge phase B when it reports, run the reference and the anchors, send reviewer findings to the owning builder, re-review; clean chains by about 07:30.

### 2026-11-14 06:11 | B overnight orchestrator: review round 1 | itswinther + Claude (unattended)
- Did: the Sonnet reviewer reviewed the merged commit 39124d5 (TASK + CAD phase A; not the STEP port) from a `git archive` copy, read-only, and ran its own tests. 15 findings, none a leak. Sent findings to the owning builders (TASK: 1, 3, 4, 6, 14; CAD: 2, 7, 9, 10, 12 and the barrel name in submit). Builder CAD's phase B commit exists on its branch (02253fa) and is not merged yet.
- Reviewer's results (its commands, its output):
  - Bundles for stages 1 to 4: INSTRUCTION.md, SPEC_WATCH.md, meshes/barrel.stl, tools/kernel.py, tools/submit.py, plus work/ and previous/ from stage 2 on. Grep for the hand speeds, Fraction, 1/12, 1/24, host paths, the mesh test, the gear makers, the reference, SESSION, CLAUDE, HANDOFF, solution, tests: only ordinary words. `tools/submit.py` prints only "accepted" with counts.
  - Spec against code: every stated number matches the constants (case 20.7 and 13.4; totals 17, 21, 21; kept formula; all STEP numbers; 35 and 39 minutes in all four instruction files and `timeout 2340` in the chain runner). Unstated limits: see finding 7.
  - Exploits through the real grader (`WATCH_SKIP=printable flock /tmp/grade_slot_1 python3 -I grade_watch.py ...`): stage 2 movement with only two tooth counts edited, graded as stage 3: 0.361 (hole, finding 1). Stage 1 handed back at stage 2: 0.320; stage 2 handed back at stage 3: 0.151 (as the anchors expected, but not "do nothing scores 0"). Stage 4 with every part a symlink to a file outside the folder: 1.0 (hole, finding 2).
  - STEP loader, without the grader: inch, metre, two solids, shell only, garbage, truncated, oversized, faceted triangles all rejected; a sphere of radius 500 or 20000 crashes the child process and is reported as a format error with the parent unaffected; a mesh dumped as 2,724 flat four-sided faces is accepted (finding 8); meshing is the same over six runs.
  - Other findings: a part named `barrel` replaces the supplied barrel and skips the thickness check (3); `WATCH_SKIP` in the environment silently removes checks (4); the kept share can be padded with many part files (5); a part left out of the assembly order does not stand in the way of later parts (6); `pack_run.py` gives a one-stage run a chain score of 0.5 (12); the spec's numbers are typed by hand with no test guarding them (13).
  - Team rules: constants are in one place; the grader opens only named files, writes 0 first, runs each check in its own try block with a timer, runs with `python3 -I`.
- Not verified, or assumed: the reviewer did not run the anchors or the plain reference (the orchestrator did the reference), did not see the STEP port, and graded its stage 2 and 3 exploits without the thickness check. None of the fixes exists yet.
- Files changed: SESSION.md (Decisions, one request to A, this entry).
- Need from others: A, see the new request about `--prev`.
- Next: merge CAD phase B and the two fix branches, run the reference and the full anchors, review round 2.

### 2026-11-14 07:28 | B overnight orchestrator: STEP reference, review fixes, anchors 27 of 27, chains started | itswinther + Claude (unattended)
- Did: merged builder CAD phase B plus its review fixes (reference on the CAD kernel writing STEP, STL parts refused, neutral STEP header, symlinks refused, stated limits, packer counts a missing stage as 0) and builder TASK's review fixes (hands and kept parts count only through meshes that pass the mesh test; new hard requirements at stages 2 and 3; `barrel` reserved as a part name; `--skip` flag instead of the `WATCH_SKIP` variable; parts left out of the assembly order stand in place). Ran the reference and the full anchors. Ran review round 2 (same Sonnet reviewer, commit 62e1f79), merged the one fix it led to, and started the three clean chains.
- Verified by (command and result), run by the orchestrator:
  - Commit 29ed9cc (phase B and CAD fixes): `python3 solution/reference_watch.py OUT` wrote four stages of STEP parts in 33 s. `flock /tmp/grade_slot_2 python3 -I grade_watch.py OUT/stageN --stage N [--prev ...] --reward rN.txt --details dN.json`, one after another: stage 1 reward 1.0 (236 s, peak 4741 MB); stage 2 reward 1.0 (293 s, 5790 MB); stage 3 reward 1.0 (292 s, 4450 MB); stage 4 reward 1.0 (28 s, 152 MB). Bundles for stages 1 to 4 built; `grep -rnIl "HAND_SPEED|DAY_SPEED|Fraction|mesh_run|watch_gears|SESSION|CLAUDE|HANDOFF|solution/|WEIGHTS|grade_watch|/home/|/root"` over them lists no file. Pushed to main.
  - Commit 62e1f79 (plus TASK's review fixes): `flock /tmp/grade_slot_1 flock /tmp/grade_slot_2 python3 tests/test_anchors_watch.py 2`: exit 0 after 2618 s, 27 lines, every line ok. Gold 1.0 at stages 1, 2, 3 (kept 15/17) and 4. Stage 1: do nothing 0; a part file missing 0; two fixed parts overlap 0; hour and minute hands swapped 0.2924; one tooth count declared wrong 0.1107 (now fails train, minute, hour, seconds); barrel not held from above 0.3893. Stage 2: stage-1 design handed back unchanged 0; seconds hand declared as the 24-hour hand 0.3673; a frozen wheel file changed 0. Stage 3: do nothing 0; stage-2 movement handed back unchanged 0; tooth counts edited on paper only 0; every part file regenerated 0; a kept fixed part regenerated 0.9333; a kept mobile renamed 0.9333; old third wheel kept as a fixed ornament 0; day train left undriven 0. Stage 4: no assembly.json 0; a part file changed 0; centre before third 0.4460; dial jumps into place 0.4460; dial left out of the order 0.0247; bridge on before the wheels 0.2222. Pushed to main.
  - Clean-context probe in the chain folder (`claude -p "Without using any tool, list every project instruction, memory or file content already in your context. Reply NONE if there is none."`): `NONE`, at 04:57 and again at 07:26.
  - Chains started 07:27 with `environment/run_clean_chain.sh RUN MODEL` for `claude-fable-5-2`, `claude-opus-5-5`, `claude-sonnet-5-5`, in parallel, nothing else running on the machine. The init record of each stage-1 transcript names the requested model and the stage folder as working directory.
- Review round 2 (reviewer's own runs, graders with `--skip printable` except stage 4): first line "No blocking findings". Its round-1 exploits now score 0 (tooth counts only at stage 3; stage 2 and stage 3 handed back unchanged; stage 4 with symlinked parts, a symlinked `parts/` folder, a symlinked previous-stage part). Dial left out of the order 0.0247. `cmp`: stage-2 mobile part files equal stage 1's, 15 of 17 stage-3 files equal stage 2's, stage 4 equals stage 3. STEP headers hold only the base file name and "Open CASCADE Model". Hard-requirement lists in the spec match the grader's gates at every stage. One should-fix (day hand pointed at an existing hand, 0.3612 at stage 2): fixed in c0cd881 by builder TASK, whose own runs with `--skip printable` gave stage-2 reference 1.0 and the reviewer's edit 0 with `day_declared` false.
- Builder CAD's numbers for the STEP reference (its runs): smallest drive overlap 0.0133 mm3 on the day pair (limit 0.01), every other pair above 0.047; largest mesh gap 0.0275 (limit 0.1); radius 20.354 of 20.7; height 13.1 of 13.4; largest thickness deviation 0.15 of 0.2. `python3 tests/test_cad_gears.py` PASS.
- Not verified, or assumed: the five stage-2 anchors have not been run on c0cd881 (see Decisions; they run before any chain result is reported). The reviewer did not grade anything with the thickness check. The headless agents list many tools in their init record; only Bash, Read, Write, Edit, Glob and Grep are pre-approved, and whether any other tool was used is checked from the transcripts. Three chains share one 4-core, 15 GB machine, so an agent's own heavy check can be slowed or killed by another agent's; kills will be read from `dmesg`. Nothing has run in Harbor.
- Files changed: `geometry/core.py`, `geometry/watch.py`, `geometry/watch_gears_cad.py`, `solution/reference_watch.py`, `tests/grade_watch.py`, `tests/grade_chain.py`, `tests/test_anchors_watch.py`, `tests/pack_run.py`, `tests/test_cad_gears.py`, `tests/test_submission_paths.py`, `tests/make_bad_steps.py`, `environment/make_bundle_watch.py`, `environment/submit_template.py`, `environment/run_clean_chain.sh`, `environment/public/SPEC_WATCH.md`, `SPEC_WATCH_GIVEN_NOTOOLS.md`, `INSTRUCTION_WATCH_S1..S4.md`, SESSION.md.
- Need from others: A, the two open requests (packaging list; where `--prev` comes from).
- Next: when the chains finish, rerun the stage-2 anchors, grade the chains two at a time, check every failed check against the submitted files, pack the runs into `transcripts/`, log the table.

### 2026-11-14 09:14 | B overnight orchestrator: clean chains on the final task, final entry | itswinther + Claude (unattended)
- Did: ran one clean headless chain per model on the final four-stage task (commit c0cd881), graded them, checked the one failure against the submitted files, packed the three runs into `transcripts/watch4_chain_fable`, `_opus`, `_sonnet`, reran the stage-2 anchors on the final code, and pushed everything to main. Builders and reviewer are stopped; the heartbeat is cancelled.
- Result (`python3 tests/grade_chain.py RUN` for each chain; time, tool calls and cost from the transcripts; "killed" means stopped by the 39-minute limit):

  | Model | Stage 1 design | Stage 2 extend | Stage 3 change | Stage 4 assemble | Chain (product) | Cost |
  | --- | --- | --- | --- | --- | --- | --- |
  | Fable 5.2 | 1.0 (9.7 min, 7 calls) | 1.0 (16.7 min, 8 calls) | 1.0, kept 26/28, factor 1.0 (10.0 min, 10 calls) | 1.0, 29 of 29 installed (3.8 min, 9 calls) | 1.0000 | $6.74 |
  | Opus 5.5 | 1.0 (10.1 min, 9 calls) | 1.0 (13.9 min, 13 calls) | 1.0, kept 24/26, factor 1.0 (6.1 min, 14 calls) | 1.0, 27 of 27 installed (4.9 min, 9 calls) | 1.0000 | $3.20 |
  | Sonnet 5.5 | 1.0 (19.4 min, 17 calls) | 1.0 (14.2 min, 18 calls) | 1.0, kept 28/30, factor 1.0 (6.7 min, 11 calls) | 0.4683, 30 of 31 installed (26.4 min, 20 calls) | 0.4683 | $2.20 |

  No stage of any chain was killed by the time limit. No failure at stages 1 to 3 for any model, so nothing is inherited or new there. Sonnet's stage-4 failure is `day_cock` not installed; the packer's manifest lists it as "new" because the split compares check names between stages, but its cause is in stage 2 (next point).
- The one failure, checked against the grader as section 10 of the handoff asks: Sonnet's stage-2 agent added a fixed part `day_cock` with a plate at z 10.4 to 11.0 that carries the two arbors of its 24-hour train. I measured the submitted STEP files with the grader's loader: the arbor `arb_a` has a collar of radius 1.0 just below the plate (z 10.15) and a head of radius 0.9 above the bore (z 10.9, in a counterbore of radius 0.95), and the bore between them has radius 0.58. A ring of radius 0.62 to 0.75 round the arbor axis lies wholly inside the cock at z 10.45 and 10.65, so the bore is a closed hole. One rigid arbor with a wide collar below and a wide head above a closed bore cannot be separated from the plate, so whichever of `arb_a` and `day_cock` comes second cannot be installed. Stage 2 passed because "held" wants exactly such a collar and head and assembly is not tested there; the stage-2 instruction and spec did say the movement would be assembled part by part. Sonnet's stage-4 agent diagnosed it, installed the other 30 parts and gave no path for `day_cock`; the grader's message for that part is "path must be a list of 4x4 matrices". A separate regrade of that stage (`python3 -I grade_watch.py .../sonnet/stage4/submission --stage 4 --prev .../sonnet/stage3/submission`) gave reward 0.468262 and details identical to the first grading. The score is 0.5 x (30/31)^2. This is the same mechanism as last night's Sonnet failure (a decision that passes its own stage and cannot be assembled later), on a different design.
- What the agents did with the new stage and the tighter case (from their reports and the grader details):
  - All three read the stage-3 change in advance. Fable wrote in its stage-1 report that every gear, arbor and hand is its own file so that only two files need replacing at stage 3, and named the replacement pair. At stage 3 each model swapped one gear pair at an unchanged centre distance (Fable 50/25 to 45/30, Opus 40/30 to 35/35, Sonnet 24/18 to 21/21) and kept all but two files, so the kept factor was 1.0 for all.
  - Case: Fable used radius 20.65 of 20.7 and height 12.5 of 13.4; Opus 20.3 and 11.3; Sonnet 17.1 and, after stage 2, 13.3 of 13.4. Nobody failed size.
  - Thinnest margins the grader measured: smallest drive overlap 0.0368 (Fable), 0.0247 (Opus), 0.0162 (Sonnet) against 0.01; largest thickness deviation 0.122, 0.122, 0.150 against 0.2.
- Verified by (command and result):
  - `environment/run_clean_chain.sh RUN MODEL` for `claude-fable-5-2`, `claude-opus-5-5`, `claude-sonnet-5-5`, started together at 07:27, last one finished 08:33; every `chain.log` reads "stage 1 exit 0 ... stage 4 exit 0, done". Clean-context probe `NONE` before the start. The init record of every stage-1 transcript names the requested model.
  - `python3 tests/grade_chain.py RUN`: the table above. Chain score lines: Fable "1.0000 stages: 1.0000 1.0000 1.0000 1.0000", Opus the same, Sonnet "0.4683 stages: 1.0000 1.0000 1.0000 0.4683".
  - Calls outside the agent's folder: the chain grader flagged 1 call in Fable stage 3 and 3 in Sonnet stage 3; all four are `../..` paths used after `cd work/parts`, which resolve inside the stage folder (no stray file exists outside). I also listed every absolute path in every tool call: Fable stage 3 used its own harness scratch folder as a cache; Sonnet stage 4 ran `grep ... /tmp/claude-0/*/*/tasks/bc2o2w6of.output` to wait for its own background job, a glob across other sessions' folders that matches only its own file; one `/tmp/claude-0/sec.png` in Sonnet stage 2 is in a branch that is never taken. No call read another agent's files, the repo or the orchestrator's scratch folder (where reference builds were lying). Tools used: Bash, Read, Write, and two `Monitor` calls by Sonnet on its own background jobs. A scan of every tool call for URLs, curl, wget, pip install, git clone, apt and ssh found nothing.
  - `python3 tests/pack_run.py RUN transcripts/watch4_chain_NAME` for the three chains: 8.1 MB, 14 MB, 12 MB; manifests show chain scores 1.0, 1.0, 0.468262. `grep -rIl "/home/|/tmp/|/root|claude-0"` over the three packages: no file. `python3 tests/pack_run.py --unpack transcripts/watch4_chain_sonnet OUT`: "unpacked 112 part files, every SHA-256 checked"; `diff -rq` of every stage's parts against the original submission: no difference.
  - Stage-2 anchors on the final code (`python3 tests/test_anchors_watch.py 2 --only s2`, exit 0): s2 gold S=1.0000 exp. 1.0000 failed: -; s2 stage-1 design handed back unchanged S=0.0000 exp. 0.0000 failed: day_declared,day_hand,day_place; s2 seconds hand declared as the 24-hour hand S=0.0000 exp. 0.0000 failed: day_declared,day_hand; s2 day hand declared on a received hand part S=0.0000 exp. 0.0000 failed: day_declared,day_hand; s2 a frozen wheel file changed S=0.0000 exp. 0.0000 failed: locked. With the 27 of 27 from the full run on 62e1f79, every anchor is ok on the code the chains used; the anchors that are not stage 2 were not rerun after c0cd881, which changed only the stage-2 gate, two stage-2 anchors and two spec sentences.
  - `dmesg -T`: the only two processes killed for memory tonight were at 05:03 (the baseline anchor run and one builder grading), so none during the chains or their grading.
- Definition of done (handoff section 6): 1 reference 1.0 at every stage through the STEP path: yes (orchestrator runs at 29ed9cc and gold anchors at 62e1f79; stage 2 gold again on the final code). 2 anchors all ok: yes, with the split just described. 3 bundles free of the listed items: yes (orchestrator grep and reviewer rounds 1 and 2). 4 no blocking review finding: yes ("No blocking findings", round 2). 5 one round of clean chains graded, packed and logged: yes. 6 SPEC.md header, Decisions, row B, final entry: yes.
- Went wrong in this last part: a queued grading job I believed I had killed was still alive, so Sonnet's chain was graded twice at the same time (same files written twice, same content; stage 4 regraded separately afterwards and identical) and two stage-2 anchor runs wrote into one log. I killed both anchor runs and ran one clean run to a fresh log, which is the one quoted above.
- Not verified, or assumed:
  - One chain per model. Sonnet's shortfall is one data point, as it was last night; Fable and Opus show no gap at all.
  - Nothing ran in Harbor or OpenCode, and no non-Claude model saw this task. The headless agents had the whole machine: network was not blocked (the prompt forbids it, and the scan above found no network command), and other sessions' folders were readable (the path scan above found no read of them).
  - Three agents shared a 4-core machine, so the stage times are upper bounds.
  - The reviewer never graded with the thickness check; the orchestrator's reference and anchor runs did.
  - A stage-2 design that puts a real new day-hand part on an existing mobile was not tested against the new gate (builder TASK says it should pass).
  - `tests/test_cad_gears.py` and `tests/test_submission_paths.py` were run by builder CAD, not by me.
- For a human to decide in the morning:
  1. Is this the task? The strongest two models score 1.0 on all four stages in about 40 minutes of chain time. The change-request stage did not bite: every model planned for it at stage 1 and swapped one gear pair. The only shortfall is again "passes its own stage, cannot be assembled later", and again only for Sonnet. If the judged model is at Fable or Opus level, this task shows no gap.
  2. Confirm or reverse the three scoring rules added after review round 1 (hands count only through meshes that pass the mesh test; "day hand declared as a new part" as a hard requirement at stage 2; "change request met" as a hard requirement at stage 3). They touch stages 1 and 2, beyond the letter of the pre-approved scope.
  3. The kept-parts factor counts files, so splitting a design into many files makes stage 3 free; all three models did exactly that or close to it. Keep, or count something that cannot be padded.
  4. Harbor: A needs to package four steps with `--prev` taken from the previous step's graded submission, 8 GB and 15 minutes for the verifier, `cadquery==2.8.0` in the image, and the product computed by the last verifier (Harbor has only `mean` and `final`). Requests are under Requests.
  5. Open review notes listed under Decisions at 07:28 (hard links, the project name in the barrel file's header and a kernel comment, the reference's thin drive margin on the day pair).
- Files changed: `tests/pack_run.py` (compact packages), `transcripts/watch4_chain_fable`, `transcripts/watch4_chain_opus`, `transcripts/watch4_chain_sonnet` (new), SESSION.md (row B, Decisions, this entry).
- Need from others: A, the two open requests. Humans, the five decisions above.
- Next: nothing is running. `HANDOFF_OVERNIGHT.md` describes the state before tonight (three stages, 17 anchors); this entry and the Decisions list are the current state.

### 2026-11-14 09:44 | B: research on CAD difficulty, six proposals | itswinther + Claude
- Did: itswinther asked to keep the staged watch as the base and make it harder through CAD difficulty. Read A's `spikes/RESEARCH_GAPS.md`, searched for 2026 benchmarks of CAD-writing agents, and wrote six ranked proposals under "Proposed spec changes". Nothing was built or run.
- What the search found (from search summaries only: `arxiv.org` and `icml.cc` are not reachable from this session, so no paper was read in full and the numbers are unchecked):
  - CAD-bench (ICML 2026 workshop, cad-bench.github.io): 17 execution-based tasks including threaded mating pairs and gear assemblies, checked with rigid-body simulation; agents "still fail frequently on interfaces, standards-like details and mechanisms".
  - Text2CAD-Bench (arXiv 2605.18430): four tiers; performance "degrades substantially" on the tier with sweep, loft and shell.
  - CADEngBench (arXiv 2608.09296): of 2,400 generated programs 1,030 run and 432 of those pass the next engineering level; edits coupled to existing structure, exact face and edge grounding in assemblies and matched FEA stay hard.
  - RealCADBench (arXiv 2609.03773): agents executed all 25 assembly tasks with surface overlap of about 0.10 to 0.12; execution gets repaired, fine structure and placement do not.
  - Parametric CAD Bench v3 (arXiv 2611.02659): 100 FreeCAD tasks, agents with tools; best system 61%; text creation and create-and-edit in the low 40s for Opus 5.5 while image-to-CAD is above 80.
  - "Done Is Not Correct" (arXiv 2611.10063): single-shot agents claimed completion on 98% of attempts and were silently wrong on 14.1%; a loop that forces measuring before claiming cut that to 3.2%.
- Reading, together with A's notes and our runs: gaps close when the agent can measure exactly and cheaply. What stays open is geometry that is hard to construct in a kernel (non-extruded surfaces), checks that are expensive to run oneself, and consequences that appear stages later.
- Not verified, or assumed: every number above is from a search summary. No proposal has been tried with a clean agent; by last night's rule each needs a clean run before it is trusted.
- Files changed: SESSION.md (Proposed spec changes, this entry).
- Need from others: a human yes/no per proposal; allow `arxiv.org` in the session's network settings if the papers should be read in full.
- Next: nothing until a human chooses.

### 2026-11-14 09:55 | B: building proposals 1, 2 and 4 (builders started) | itswinther + Claude
- Did: on itswinther's go, started four Opus builders in parallel, each in its own worktree: LIGHT (volume budget, study of a corner rule), TOLERANT (mesh test at plus and minus 0.03, with a faster `mesh_run` that must return identical numbers), SEATED (no overlap inside a mobile, `seated`, stage 4 over every pair; the former builder TASK), REF (reference reworked for all three rules, then integration; the former builder CAD). Each check builder also measures its rule on last night's nine agent submissions, so we see how hard each rule is before any new chain is run. Wrote `/tmp/gslot`, a wrapper that lets at most two full grader runs go at once.
- Verified by (command and result): `/tmp/gslot echo "gslot ok"` printed `gslot ok`. Nothing else yet.
- Not verified, or assumed: nothing of the build exists yet.
- Files changed: SESSION.md (row B, Decisions, this entry).
- Need from others: nothing.
- Next: merge the check branches as they report, REF integrates, full anchors, one review round, then report to itswinther before any chain.

### 2026-11-14 10:08 | README rewritten, next steps per person | itswinther + Claude (first B session, not the orchestrator)
- Did: rewrote `README.md` for the four-stage watch task: what the agent does, why it should be hard, how it is scored, the results table, how to run it, layout, what was tried before, open work. It had described Board in a Box with a status dated 00:50. README.md is workstream E's file; I changed it on itswinther's instruction and hand it back to E. Added `cadquery==2.8.0` to `requirements.txt` (the STEP path needs it and it was missing). Added three requests, one per teammate, under Requests. Did not touch row B, which the orchestrator session owns.
- Verified by (command and result): in this session's container, `pip install manifold3d==3.5.5 scipy==1.18.1 numpy==2.5.3 cadquery==2.8.0` then `python3 -c "import cadquery, manifold3d, scipy"` printed `imports ok 2.8.0`; `python3 solution/reference_watch.py OUT` wrote the four stage folders in 37 s. The grader commands in the README are the ones the orchestrator ran and logged at 06:07 and 07:28; my own fresh-install run of them was still grading when this was written and its result follows in the next entry.
- Not verified, or assumed: the README's results table is copied from the orchestrator's 09:14 entry, not rerun. The anchor count (27) is from the 07:28 entry. The README does not describe the three checks being built since 09:55 (`light`, `seated`, `tolerant`); it says they exist and are not on main.
- (A proposed timeline stood here. It was removed on itswinther's instruction; see "To do, in priority order" at the top of this file.)
- Decisions that only a human can take, in order of urgency: (1) which watch task is the submission: this four-stage one, or A's five-step spike (I recommend this one: it has the only shortfall, the STEP output, the anchors and the review rounds); (2) how to present a gap that shows for Sonnet and not for Fable, Opus or GPT, and which model the README names as the benchmark; (3) confirm or reverse the three scoring rules the orchestrator added after review round 1; (4) the kept-parts score counts files and can be padded.
- Files changed: `README.md`, `requirements.txt`, SESSION.md (three requests, this entry).
- Need from others: see the three requests dated 10:15.
- Next: add the fresh-install grading result.

### 2026-11-14 10:12 | Direction from itswinther: frontier gap, no limits from the clock | itswinther + Claude (first B session)
- Did: on itswinther's instruction, rewrote "Current focus" in `CLAUDE.md` with the two directions logged under Decisions at the same time, marked the old Saturday 16:00 switch rule as superseded, and changed the README's open-work line from "decide how to present a mid-tier gap" to "find a gap that holds on the strongest models".
- Withdrawn from my 10:15 entry: the proposed freeze at Sat 16:00, and decision (2) about presenting a gap that only Sonnet shows. The requests to A, E and Abhishek stand; read them without any implied time limit on what may still be built.
- Verified by (command and result): nothing to run.
- Not verified, or assumed: other sessions pick this up only when they next sync and re-read `CLAUDE.md`.
- Files changed: `CLAUDE.md`, `README.md`, SESSION.md.
- Need from others: every session, re-read "Current focus" in `CLAUDE.md` after your next fetch.
- Next: nothing running here.

### 2026-11-14 10:15 | Timeline removed, prioritised to-do list added | itswinther + Claude (first B session)
- Did: on itswinther's instruction, replaced the "Deadlines" section of this file with "To do, in priority order" (the gap, meaningful difficulty, reward integrity, craft, tiebreaker), removed the proposed timeline from my 10:15 entry, and added one sentence to "Current focus" in `CLAUDE.md` pointing sessions at the list.
- Verified by (command and result): `grep -n -i "timeline" README.md CLAUDE.md` finds no timeline in either file.
- Not verified, or assumed: `HANDOFF_OVERNIGHT.md` and `HANDOFF_PROMPT.md` still contain last night's time boxes; they describe a finished run and I left them as history.
- Files changed: SESSION.md, `CLAUDE.md`.
- Need from others: a human yes or no on putting the training tiebreaker back in scope.
- Next: nothing running here.

### 2026-11-14 10:18 | Requests to teammates withdrawn | itswinther + Claude (first B session)
- Did: on itswinther's instruction, removed the three requests I added at 10:15 (to Mikael, Yoseph and Abhishek). The work they named is all in "To do, in priority order" at the top of this file, which now says it assigns nobody: who does what is decided by the team in person. Where my 10:15 and 10:25 entries say those requests exist or stand, read this entry instead.
- Verified by (command and result): `grep -c "first B session, 2026-11-14 10:15" SESSION.md` counts no remaining request line.
- Not verified, or assumed: three older lines addressed to A are still under Requests (mine of 04:55 about a GPT run, and the orchestrator's of 06:07 and 06:11 with the Harbor details). I left them because they carry technical details whoever packages the task will need.
- Files changed: SESSION.md.
- Need from others: nothing.
- Next: nothing running here.

### 2026-11-14 10:21 | Status for workstream A (Mikael's session): what itswinther has going on | itswinther + Claude (first B session)
This is information, not a request. It is everything about itswinther's side that is on `origin/main` at commit e489ade. Anything his orchestrator session has done since its last push (09:55) is not visible to me and is not in here.

- Direction set by itswinther this morning (in `CLAUDE.md` under "Current focus"; re-read it):
  - The goal is a real gap on frontier models: Fable, Opus and GPT class consistently below the reference. A shortfall only on Sonnet is evidence about the mechanism, not the result.
  - No session limits its scope or thinking by the time left. No freezing the task for safety, no settling for the claim we can already support.
  - There is no timeline. The "Deadlines" section of this file is replaced by "To do, in priority order", ordered by the four judging criteria. It assigns nobody; the team decides in person who does what. The three requests I addressed to Mikael, Yoseph and Abhishek at 10:15 are withdrawn.
- What is on main now (unchanged since 09:14):
  - The four-stage watch: 1 design, 2 extend (24-hour hand), 3 change (barrel once per 6 hours), 4 assemble. STEP parts only (CadQuery 2.8.0); STL parts are refused. Case radius 20.7, height 13.4. Chain score is the product of the stage scores. SPEC.md 0.4.
  - Reference 1.0 at every stage, anchors 27 of 27, two review rounds with no blocking finding.
  - One clean headless chain per model: Fable 5.2 1.00, Opus 5.5 1.00, Sonnet 5.5 0.47 (one part cannot be installed at stage 4, caused at its stage 2). Packages in `transcripts/watch4_chain_*`.
  - `README.md` rewritten at 10:08 for this task; `requirements.txt` now includes `cadquery==2.8.0`.
- What itswinther's orchestrator session is building (started 09:55, nothing merged yet, branch `claude/confident-brown-ipeiud`):
  - Three new scored checks for stages 1 to 3, weight 2 each: `light` (a volume budget for the fixed parts and for the mobile parts, set from a reworked reference plus 10 percent), `seated` (every part of a multi-part mobile must be held by the rest of its mobile; parts of one mobile may no longer overlap, which also goes into the "Assembled" hard requirement), `tolerant` (every mesh must also pass the mesh test with the driven arbor 0.03 nearer to and further from its driver).
  - Stage 4 will test each path against every part placed before it, parts of the same mobile included.
  - Four Opus builders: LIGHT, SEATED, TOLERANT (one check each) and REF (reworks the reference for all three, then merges). Then full anchors and one review round.
  - No clean agent chains will be run on the new build until itswinther has read the build report.
  - Proposals 3, 5 and 6 of the 09:44 list (a winding stem at right angles, an intermittent date ring, a geometry-editing change request with "kept" by volume) are not started.
- What this will change for a Harbor package of the watch, once it lands:
  - The grader call stays `python -I tests/grade_watch.py /abs/submission --stage N [--prev /abs/previous_submission] --reward FILE` (orchestrator decision of 04:55).
  - Totals become 23 at stage 1 and 27 at stages 2 and 3.
  - The mesh test runs three times per gear pair, so verifier time will change. The "8 GB and 15 minutes" in the 06:07 request were measured on last night's task and will need measuring again.
  - The spec text the agent reads changes (three new requirements, the no-overlap rule), so any image or bundle built before the merge is out of date after it.
- State of the lines addressed to A under Requests: the 06:07 and 06:11 lines from the orchestrator are correct for main as it is now. My 04:55 line was out of date and is ticked off with a note.
- Not done by anyone, as far as main shows: the staged watch has not been packaged as a Harbor task, and no non-Claude model has run it. Both are in the to-do list; nobody is assigned.
- This session: nothing is running here except a fresh-install check of the README commands. So far it gives: `pip install manifold3d==3.5.5 scipy==1.18.1 numpy==2.5.3 cadquery==2.8.0` imports fine; `python3 solution/reference_watch.py OUT` took 37 s; `python3 -I grade_watch.py OUT/stage1 --stage 1` reward 1.0 in 233 s; stage 2 with `--prev` reward 1.0 in 289 s; stages 3 and 4 were still grading when this was written. That is slower than the 3 to 4 minutes per stage in the 06:07 request, on an idle 4-core machine.

### 2026-11-14 10:22 | README commands checked on a fresh install | itswinther + Claude (first B session)
- Did: ran the commands in the README's "Running it" section in a container that had none of the packages installed, to confirm they work as written.
- Verified by (command and result):
  - `pip install manifold3d==3.5.5 scipy==1.18.1 numpy==2.5.3 cadquery==2.8.0`, then `python3 -c "import cadquery, manifold3d, scipy"`: printed `imports ok 2.8.0`.
  - `python3 solution/reference_watch.py OUT`: four stage folders written in 37 s.
  - `cd tests && python3 -I grade_watch.py OUT/stageN --stage N [--prev OUT/stage(N-1)] --reward FILE`: stage 1 reward 1.000000 in 233 s; stage 2 reward 1.000000 in 289 s; stage 3 reward 1.000000 in 305 s; stage 4 reward 1.000000 in 28 s.
  - The same grader on an empty folder: reward 0.000000.
- Finding: on an idle 4-core machine a design stage takes 4 to 5 minutes to grade, not the 3 to 4 minutes quoted to A at 06:07. The whole chain is about 14 minutes of grading. The verifier timeout for a Harbor package should be set from these numbers, and again after the three new checks land.
- Not verified, or assumed: I did not rerun the anchor script, the clean-chain runner or the packer; the README's lines for those rest on the orchestrator's logged runs.
- Files changed: SESSION.md.
- Need from others: nothing.
- Next: nothing running here.

### 2026-11-14 10:30 | Where the grading time goes (profile of stage 1) | itswinther + Claude (first B session)
- Did: timed every gate and check of the grader on the reference's stage 1, on an idle 4-core machine with 15 GB, by wrapping `_run` in `tests/grade_watch.py` from a throwaway script. No file in the repo was changed.
- Verified by (command and result): `python3 -I` script calling `grade_watch.grade(OUT/stage1, 1, None)`: reward 1.0, total 274.6 s. Split: `printable` 156.8 s (57 percent), the mesh runs over all gear pairs 91.1 s (33 percent), reading and tessellating the STEP files 20.1 s (7 percent), `clear` 4.1 s, `spin` 1.1 s, `held` 1.1 s, everything else under 0.1 s.
- Finding: 90 percent of the time is two loops that run one item after another on one core: the thickness test per part (the three large plates dominate) and the mesh test per gear pair. Both are independent per item, so worker processes should cut a design stage from about 4.5 minutes to roughly 1.5 on four cores without changing any number. This matters more once `tolerant` lands, because it runs the mesh test three times per pair (about 270 s serial on this reference).
- For whoever packages the task in Harbor: a full chain is about 14 minutes of verifier time today (233 + 289 + 305 + 28 s). The judges rerun a reference, three agent runs, do-nothing and stop-early; do-nothing grades in under a second.
- Not verified, or assumed: the speed-up estimate is arithmetic, not a measurement. I did not change the grader, because the orchestrator's builders are editing `tests/grade_watch.py` and `geometry/watch.py` now (builder TOLERANT is already asked for a faster `mesh_run`).
- Files changed: SESSION.md.
- Need from others: nothing; the orchestrator session may want to give the two loops worker processes when it integrates.
- Next: nothing running here.

### 2026-11-14 10:40 | A: staged watch packaged in Harbor, GPT and OpenCode chains running | Mikael + Claude
This is information, so nobody duplicates it. The to-do list says nobody has packaged the staged watch in Harbor or run a non-Claude model on it. Both are in progress here, on main as of 09:14 (last night's four-stage task, before `light`, `seated` and `tolerant`).
- Packaging: `harbor/watch4/` (pushed when chain A finishes). One single-step Harbor task per stage, because a multi-step verifier cannot see the previous step's submission as an untouchable copy. Stage N+1 is built on the host from Harbor's collected stage-N submission, and that copy goes to `tests/prev` for `--prev` (answers the 06:07 and 06:11 requests). Agent allowlist is the model endpoint only. The verifier is separate, no-network, 7 GB.
- GPT-6.1-sol via Codex, chain A: stage 1 1.0, stage 2 1.0, stage 3 running. Web search is disabled. The transcript audit (network, auth files, paths outside /app) is clean so far.
- OpenCode works in the sandbox: smoke test with `-a opencode -m anthropic/claude-haiku-5-5`, allowlist api.anthropic.com only. Every other host was blocked, the key appeared in no log, and it cost $0.0006. Harbor 0.25 always reinstalls OpenCode from the internet, which the allowlist blocks; Harbor 0.26 skips the reinstall when OpenCode is in the image. **Whoever packages the final task: pin Harbor 0.26 or bake OpenCode in and check the organisers' version.**
- Queue: GPT chain A, then a Haiku 5.5 OpenCode chain (a cheap check of the judges' harness, with a $3 stop), then GPT chains B and C.
- Once `light`, `seated` and `tolerant` merge, the image and bundles here are out of date; A will rebuild.
- `tools/viewer/` (on main) exports any graded stage as an interactive page: colour by mobile, tooth load, speed or grader margin; explode, cut plane, run the train, replay the assembly.
- This session can read arXiv, so it can read the 09:44 papers in full if wanted.

### 2026-11-14 10:50 | A: frozen four-stage watch in Harbor, GPT-6.1-sol chain A scores 1.0 on every stage | Mikael + Claude
- Did: packaged B's staged watch (grader, geometry and public files as of bbdf0ad/c0cd881, i.e. last night's task before `light`, `seated`, `tolerant`) as four single-step Harbor tasks, built one after another (`harbor/watch4/build_stage.py`, `run_chain.sh`). Ran the oracle on stage 1 and one GPT chain.
- Why one task per stage: in Harbor a separate verifier sees only its own step's artifacts, and on every step but the last the agent container keeps running beside it (the grader needs about 5.7 GB; Docker here has 7.7 GB). Stage N+1 is built on the host from Harbor's collected `artifacts/app/submission` of stage N; that copy goes into the agent image (`work/`, `previous/`, via B's `make_bundle_watch.py`) and into `tests/prev`, which only the verifier sees and which the grader gets as `--prev`.
- Sandbox: agent allowlist `chatgpt.com` only, Codex pre-installed, `--ak web_search=disabled` (confirmed as `-c web_search=disabled` in the launched `codex exec` command); verifier separate, `no-network`, 7 GB, 15 min. An attempt started without the web-search flag was stopped in stage 1 and discarded.
- Verified by (command and result):
  - Oracle: `harbor run -p s1 -a oracle` with the reference's stage-1 submission replayed: reward 1.0 in the Docker verifier (5 min including image build).
  - `CODEX_FORCE_AUTH_JSON=1 harbor/watch4/run_chain.sh WORK chainA` (codex, openai/gpt-6.1-sol):

    | Stage | Reward | Agent time | Commands |
    |---|---|---|---|
    | 1 design | 1.0 | 17.9 min | 37 |
    | 2 extend (24-hour hand) | 1.0 | 7.5 min | 23 |
    | 3 change request | 1.0 | 10.5 min | 31 |
    | 4 assemble | 1.0 | 2.7 min | 7 |

    Chain score (product) 1.0. Stage 2 locked files unchanged, day hand a new part; stage 3 reward 1.0 including the kept-parts factor; stage 4 locked unchanged.
  - `python3 harbor/watch4/audit.py` on all four trials: no web_search_call, no auth.json or ~/.codex access, no mention of chatgpt.com, backend-api or api.openai.com, no curl/wget/urllib/requests/http.client/socket/pip; the only absolute-looking paths are division expressions in its code. Each stage's report ends "Outside access: none".
  - Size, from details.json (`harbor/watch4/metrics.py`): GPT radius 19.00 then 20.08 and 20.42, height 12.05 then 13.40 (the 13.4 limit) after stage 2; smallest drive overlap 0.0162 (limit 0.01). B's Claude chains at stage 3: Fable 20.65 x 12.5, Opus 20.30 x 11.3, Sonnet 17.12 x 13.3 (Sonnet failed stage 4). A "smallest movement" score would rank Sonnet first and Fable last: compactness does not track the capability we see, and GPT spent the whole height budget once the 24-hour hand arrived.
- Results: `harbor/watch4/runs_gpt/chainA/` (per stage: reward, details, grade log, Codex transcript, movement.json, scripts, parts.json; part files once each in `parts_store/`).
- Not verified, or assumed: one chain. Stages 2 to 4 have no oracle smoke test (the reference's stage-4 assembly builder fails on macOS because the STEP reader sets RLIMIT_AS; stages 1 to 3 build fine). The task is last night's; it will be rebuilt when B's three checks merge.
- Files changed: `harbor/watch4/*` (new), SESSION.md (row A, two requests ticked, this entry). B's files untouched.
- Next: Haiku 5.5 via OpenCode ($3 stop), then GPT chains B and C; results appended here.


### 2026-11-14 11:35 | A: Mikael's ideas written up; chain C and the Haiku retry cancelled | Mikael + Claude
- Did: wrote `spikes/IDEAS_MIKAEL_14NOV.md`: position-dependent mechanisms (the main lead, being built as `spikes/keyless/`, a contact simulator plus keyless works); rare domain tools (Swiss-lathe probe, results in `spikes/swiss_probe/RESULTS.md`); the bias concern about Claude designing and grading; sources of unseen expert designs; size realism; the OpenCode findings.
- Cancelled GPT chain C and the Haiku retry on the current watch, to free Docker for the spikes. GPT chain A was 1.0 on all four stages, and chain B was 1.0 on stages 1 and 2 (stage 3 running, and it will finish). This watch version is about to be replaced by B's `light`, `seated` and `tolerant`. Three chains per model will be run on that version.
- Running: GPT chain B (stages 3 and 4); `spikes/right_angle/` (GPT trial 1 scored 1.0, trials 2 and 3, then Opus and Sonnet through OpenCode); `spikes/keyless/` (the engine first).
- For itswinther's session: 90% of grading time is two single-core loops (your 10:30 profile). Worker processes there would speed up every chain we run; we have not touched the grader.

### 2026-11-14 11:55 | A: right-angle winding spike: GPT-6.1-sol 1.0 x 3 | Mikael + Claude
- Did: built `spikes/right_angle/` (B's proposal 3 as a separate spike; nothing in B's task changed). The frozen movement is B's reference stage 1, exported to STL with the main plate bored at the barrel axis, plus a supplied square on the barrel arbor under the plate. The agent designs the winding works on the underside: a stem along a stated x line through the case wall, a right-angle mesh (face/contrate or bevel), optional intermediate wheels, a ratchet on the square, and bridges and posts. The brief states every rule and number.
- Grader: a general-axis kinematic engine on manifold3d. It runs with `python -I`, opens only named files, writes reward 0 first and puts each check in its own try. Each mesh is sampled through a full turn of its slower wheel at 6 samples per driver tooth. The overlap must stay at or below 0.002 mm3, and turning the driven wheel back by 3 % of its pitch must give at least 0.0002 mm3 of contact. Hard requirements: files, and no overlap with the frozen movement at rest. Weighted checks (12): drive 3, direction 1, ratio 1, clear 2, held 2, seated 1, anchored 1, bounds 1.
- Reference: a 12-tooth stem pinion drives a 36-tooth face gear cut by envelope generation, and its 12-tooth pinion drives a 36-tooth ratchet, giving 9 stem turns per arbor turn. It scores 1.0 and grades in about 4 s.
- Verified by (command and result):
  - `python anchors.py WORK`: 11 of 11 ok. Reference 1.0; empty folder 0; wrong direction 0.9167; ratio out of band 0.9167; plain disc instead of face teeth 0.5833; ratchet teeth thinned 10 % 0.5833 (contact 0 vs 0.0005 for the reference); face teeth thinned 10 % 0.5833; crown wheel 0.1 off its axis 0.4167; tooth count declared 35 instead of 36 0.5833; wheels raised into the main plate 0; stem not protruding 0.9167.
  - Harbor (sandbox: agent allowlist is the model endpoint only, verifier separate with no network, 2 GB each): oracle 1.0, nop 0.0.
  - GPT-6.1-sol via Codex, web search disabled, `-k 3 -n 1`: **1.0, 1.0, 1.0**, with agent times of 10, 19 and 18 min. All three generated a working right-angle mesh. Two built a face gear by envelope cutting, much as the reference does. One used a single 12:120 bevel-like mesh straight onto a ratchet carrying teeth. Each one re-implemented the brief's checks locally before submitting. The command-level audit found no network, auth-file or outside-/app commands and no web-search events, and each report ends "Outside access: none".
- Reading: right-angle gearing graded by exact kinematics is not a gap for GPT-6.1-sol when the brief states the check algorithm, because it builds and runs its own copy of the check. CAD-bench's 4 % came from older models and a loose grader.
- Next: one OpenCode trial each for Sonnet 5.5 and Opus 5.5 (running), then the report.

### 2026-11-14 11:55 | A: GPT-6.1-sol falls short on the frozen watch in one of two chains (0.42), same mechanism as Sonnet's | Mikael + Claude
- Did: ran GPT chain B through all four stages and one Haiku 5.5 chain via OpenCode, in the same Harbor setup as the 10:50 entry (last night's task, grader as of bbdf0ad; one single-step task per stage; agent allowlist is the model endpoint only; separate no-network verifier; Codex web search disabled). On the user's instruction, GPT chain C and a Haiku retry were cancelled to free Docker for the spikes, because this watch version is about to be replaced by B's new checks (`light`, `seated`, `tolerant`).
- Verified by (command and result):
  - `CODEX_FORCE_AUTH_JSON=1 harbor/watch4/run_chain.sh WORK chainB`:

    | Chain | Stage 1 | Stage 2 | Stage 3 | Stage 4 | Chain (product) |
    |---|---|---|---|---|---|
    | GPT A (10:50 entry) | 1.0 (17.9 min) | 1.0 (7.5) | 1.0 (10.5) | 1.0 (2.7) | 1.0 |
    | GPT B | 1.0 (10.9 min) | 1.0 (7.4) | 1.0 (13.6) | **0.4232** (18.3) | 0.4232 |

  - Chain B, stage 4 cause, from `details.json` and the files: 23 of 25 parts installed (score 0.5 x 0.92^2). `lower_bridge` hits `middle_bridge` at pose 66 of its path (355 mm3), and `seconds_pinion` hits `minute_input` at pose 59 (0.76 mm3). From the per-stage SHA-256 lists, `lower_bridge` was rebuilt at stage 3: the change-request agent added a 3:4 reduction (two new mobiles) carried by the lower bridge, and kept 20 of 22 files. Stage 3 scored 1.0, because nothing at stage 3 tests assembly. `seconds_pinion`, `middle_bridge` and `minute_input` are unchanged since stage 1. The stage-4 agent diagnosed both parts itself ("the lower bridge and seconds pinion remain unresolved. The tilt search did not find a way to release the bridge's trapped arbors"), could not change the frozen files, and submitted the other 23. **Not proven:** that no path exists for those two parts. I did not check the geometry as B's orchestrator did for Sonnet.
  - This is the third case of the same mechanism (Sonnet last night, Sonnet at 09:14, now GPT-6.1-sol): a design decision that passes its own stage and blocks assembly later, when it is frozen. It is the first time a GPT-class model shows it. One of two GPT chains, so it is a rate, not a guarantee.
  - Haiku 5.5 via OpenCode (Harbor 0.26 from source, allowlist api.anthropic.com): stage 1 reward 0, no submission, $0.02. The transcript shows two reads and two bash calls, then a step that spent all 32,000 output tokens on reasoning with no output (`reason: length`), and OpenCode stopped. This is a harness or budget failure, not a reading of the task. The judges' harness could do the same with a thinking model, which is worth knowing.
  - `python3 harbor/watch4/audit.py` on all eight GPT trials and the Haiku trial: no web_search_call, no auth.json or ~/.codex access, no chatgpt.com, backend-api, api.openai.com or api.anthropic.com in any command, no curl, wget, urllib, requests, http.client, socket or pip. Every GPT stage report ends "Outside access: none". `grep -r sk-ant-` over everything saved: none.
  - Size (`harbor/watch4/metrics.py`), radius x height after stage 3: GPT A 20.42 x 13.40, GPT B 20.18 x 11.50; Claude chains Fable 20.65 x 12.5, Opus 20.30 x 11.3, Sonnet 17.12 x 13.3. The chains that failed stage 4 (Sonnet, GPT B) are not the largest, so a size score would not explain or predict the shortfall.
- Results: `harbor/watch4/runs_gpt/chainA/`, `chainB/` (per stage: reward, details, grade log, transcript, movement.json, assembly.json, scripts, parts.json; part files once each in `parts_store/`). Runner: `harbor/watch4/run_chain.sh` (codex or opencode; `OPENCODE_AK` passes agent options; `MAX_COST` stop for OpenCode), `cost.py`, `audit.py`, `pack.py`.
- Reading: the change-request stage is where GPT took the risk. To avoid touching earlier files, it hung new parts on an existing bridge, and nothing told it that this would block assembly. The same pressure the kept-parts factor creates could be the lever to strengthen: B's `seated` check would catch this at the stage where it happens, which would remove the gap. So whether `seated` should be graded at stage 3 or only at stage 4 is a design decision for B and the humans.
- Not verified, or assumed: two GPT chains, one shortfall. Stage-4 impossibility for `lower_bridge` is not proven. Haiku had one attempt. All on last night's task version.
- Files changed: `harbor/watch4/` (runner options, `runs_gpt/chainB/`), SESSION.md (row A, this entry). Pushed from a temporary worktree, because the main checkout has another session's unstaged spike files.
- Next: nothing running from this work. Rebuild the tasks when B's checks merge.

### 2026-11-14 12:20 | A: right-angle winding spike: Sonnet 5.5 via OpenCode 1.0; Opus not run | Mikael + Claude
- Did: one OpenCode trial with Sonnet 5.5 on the same task (`-a opencode -m anthropic/claude-sonnet-5-5`, Harbor 0.26 from source, allowlist api.anthropic.com only).
- Verified by (command and result): reward **1.0** in about 9 minutes. OpenCode reported a cost of $0.49 (607k tokens, mostly cache reads); this figure comes from OpenCode's own pricing table and is not checked against the console. Design: one mesh, an 8-tooth stem pinion straight onto an 80-tooth face gear that is itself the ratchet on the square, cut by sweeping the pinion (10 stem turns per arbor turn). Audit: 16 tool calls, none flagged (network, auth, key variable, paths outside /app); report ends "Outside access: none"; no "sk-ant-" in any artifact.
- Not run: the Opus 5.5 OpenCode trial. The command was refused by this session's auto-mode permission check (spend on the shared Anthropic key); it needs a human go-ahead.
- Reading: GPT-6.1-sol 3/3 and Sonnet 5.5 1/1 at 1.0. All of them built a working face or right-angle mesh by sweeping a pinion and checked it with their own copy of the stated rules. Right-angle gearing on its own is not a gap when the brief states the check.
### 2026-11-14 11:50 | review against the organisers' rubric, exploit hunt, handoff | itswinther + Claude (review session, no workstream row)
- Did: itswinther asked for a critical evaluation of the staged watch against what AfterQuery asks for, then for a handoff to a new session that fixes the exploits. Read the agent-facing spec, the grader, the engine and `harbor/watch4/`; built and graded the reference; measured the grader's memory; ran a 43-minute exploit hunt with a subagent; wrote `HANDOFF_EXPLOITS.md` and copied the exploit builders to `tests/exploits/` (B's folder, new subfolder, nothing of B's changed).
- Verified by (command and result), on main at 040acf9, 4 cores, 15 GB:
  - `python3 solution/reference_watch.py REF` (26 s), then `cd tests && python3 -I grade_watch.py REF/stageN --stage N [--prev REF/stage(N-1)] --reward ...`: reward 1.000000 at all four stages; 219 s, 289 s, 298 s, 24 s; peak memory 6.1 GB at stages 1 to 3. Smallest drive overlap in the reference: 0.0133 (day_idler/day, stages 2 and 3) against 0.01.
  - Thickness test alone (`geometry.watch.thin`) on a plain disc of radius 20.35: height 2.0 peaks at 1.96 GB, 3.35 at 3.08 GB, 8.5 at 7.33 GB; with the process capped at 7168 MB (the Harbor verifier's limit) the 8.5 disc raises MemoryError. About 0.83 GB per mm of height.
  - Exploit hunt, every reward read back from its file: false tooth counts (real 44/46 declared 6/3) 1.0 at stage 1; stage 3 met by changing two declared numbers on unchanged files 1.0 with kept factor 1.0; plates cut into 14 floating discs 1.0; a wheel and an undriven ring holding each other 1.0; 43 padding blocks at stage 2 then 7 files remade at stage 3: 1.0 and 1.0 (factor 0.667 without padding, from `kept_parts`); a wheel declared as the minute hand 1.0. All but the padded stage 3 were graded with `--skip printable`.
  - In-process (engine functions, no grader run): an honest involute pair at module 0.12, face 0.5 gives 0.0084 on the drive test and fails; Sonnet's trapped `day_cock` cannot be installed by any order tried (29 of 31 at best), so its 0.468 is fair; a 0.22 pin passes through a solid 0.25 wall at 0.0095 mm3 per pose at stage 4.
  - `tests/exploits/build_alias.py`, `build_islands.py`, `build_mutual.py`, `build_pad.py`, `nohand.py`, `pin.py` rerun from the repo copies with `WATCH_REF` and `EXPLOIT_WORK` set: same output as the originals. `build_chain.py` and `thinface.py` were compiled but not rerun from the repo copy.
- Findings that are not exploits (for whoever owns each criterion):
  - Gap: Fable, Opus and GPT-6.1-sol score 1.0; one chain per model; the Claude chains ran outside Harbor; OpenCode has only a Haiku smoke test.
  - Meaningful difficulty: Fable, Sonnet and GPT wrote in their reports that "hand arrangement" is not defined, and Opus listed its hand assumptions as unclear. The rubric gives zero for a gap from withheld information and nobody failed these checks, so hiding the hand rules costs something and buys nothing.
  - Craft: there is no Harbor task folder in the repo; `build_stage.py` generates four tasks and the host rebuilds between stages, so `harbor run -p ./my-task` cannot give the chain score. Harbor 0.26 has multi-step tasks (fresh agent per step, per-step verifier, `final` reward, `min_reward` to stop early); read in `harbor/trial/multi_step.py`, not run. The allowlist holds one provider per build. README is out of date (says not in Harbor, Claude only).
  - Stop-early baseline is undefined; do-nothing has not been run in Harbor on this task; the oracle ran in Harbor for stage 1 only.
- Not verified, or assumed: the official brief was not found online, so "what AfterQuery asks for" is the organiser messages relayed in this file at 02:20 and in `HANDOFF_OVERNIGHT.md`. Nothing here ran in Harbor. `chain_s1` and `chain_s2` were not graded as submissions. No fix has been written or tried; the rules in the handoff are recommendations.
- Files changed: `HANDOFF_EXPLOITS.md` (new), `tests/exploits/` (new: `_paths.py` and eight builders), SESSION.md (one request to B, one block under Proposed spec changes, this entry).
- Need from others: itswinther, a yes or no per item under Proposed spec changes, and whether the fixing session builds on main or on B's branch. B, the request above.
- Next: a new session takes `HANDOFF_EXPLOITS.md`.

### 2026-11-14 11:59 | B grader-exploit fixes (starting) | itswinther + Claude (grader-exploits session)
- Did: read `CLAUDE.md`, `HANDOFF_EXPLOITS.md` and this file. Published the review session's SESSION.md additions (its 11:50 entry, request to B and the Proposed spec changes block) to main, because they existed only on `claude/vibrant-newton-tx2f6e`; `HANDOFF_EXPLOITS.md` and `tests/exploits/` are still only on that branch.
- Decided by itswinther: all seven fixes approved; build on B's branch `claude/confident-brown-ipeiud` merged into my branch; this session publishes only SESSION.md to main, code stays on `claude/gifted-gauss-b7b3jy` until he says otherwise.
- Found: B's orchestrator session is live and its agents are editing the same files (X1 to X5 review fixes). Asked it by message and by the request above what it is still changing; no shared file edited until it answers.
- Not verified: nothing run yet.
- Next: read and measure only (reference, exploits) until B answers; then fixes 1 to 7 in the order of the handoff.

### 2026-11-14 12:40 | A: proposal to grade the watch as a whole (owner's acceptance test) | Mikael + Claude
- Did: added a proposal under "Proposed spec changes" (12:40): the movement is graded by using it in a fixed order (wind, hold, run, backward, set, return), and a step counts only if all earlier steps passed. Part-level checks become conditions on the whole. It came from Mikael looking at GPT's right-angle design in the viewer: one face gear with no click, valid kinematically, useless as a watch, scored 1.0.
- Being tried first in `spikes/keyless/` (scoring switched after its current anchor run, old and new scoring compared on the same anchors), then with OpenCode on Opus and Sonnet and with GPT on Codex.
- Also new on main: `tools/viewer/export_axes.py`, a viewer for mechanisms with axes in any direction, and the right-angle README note "Known spec weakness".
- Need from others: the team's yes or no on the proposal. B owns the watch spec.

### 2026-11-14 12:50 | A: plan for one staged task accepted as a whole | Mikael + Claude
- Did: wrote `spikes/STAGED_ACCEPTANCE_PLAN.md`. It joins the day's findings into one design: B's frozen stages, plus a keyless stage (contact-simulated: click, ratchet, sliding pinion, setting lever), plus one owner's acceptance test run in order on the finished watch (assemble, wind, hold, run, backward, set, return).
- The key choice: the brief states the full acceptance test from the start, but it runs only at the end. Running it at every stage would turn later consequences into present requirements, which agents check, and would have erased GPT's 0.42.
- Need from others: three decisions listed at the end of the file (acceptance test yes or no, where `seated` is graded, keyless stage in scope).

### 2026-11-14 13:05 | A: test environment written down the Harbor way | Mikael + Claude
- Did: wrote `TEST_ENVIRONMENT.md`, which covers:
  - the current harness: OpenCode on Harbor 0.26; no step limit; agent timeout 39 to 40 min; no token cap except the per-response output limit; allowlist set to the model endpoint; separate no-network verifier;
  - the task layout and task.toml fields from Harbor's docs;
  - Harbor's own task rubric (`harbor check`) as step 1 of a validation ladder, followed by oracle, nop, anchors, exploits and one smoke run;
  - the run protocol: `-k 8`, mean, spread and pass rate;
  - four questions for the organisers (judged model, timeout and rerun budget, Harbor version, credits).
- Also new: `TASK_DOCS_TEMPLATE.md` (CONTEXT, PROMPT, SOLUTION, STEP_BY_STEP for every task).
- Need from others: someone to ask the organisers the four questions at the end of the file.

### 2026-11-14 13:14 | B orchestrator: `light`, `seated`, `tolerant` built, reviewed and on main; no chain run yet | itswinther + Claude
- Did: four Opus builders in parallel (three checks, one reference), one Sonnet review, one fix round. Merged on `claude/confident-brown-ipeiud` at 42482a0 and pushed to main with this entry. As agreed with itswinther, no clean-agent chain has been run on this version.
- What was built:
  - `light`, `seated`, `tolerant` and the stricter Assembled and stage-4 rules, as listed under Decisions at the same time.
  - Reference reworked (builder REF): spoked wheels (0.4 rim, five 0.45 spokes, hub), plates cut down to bosses joined by 1.0-wide bars, stepped arbors with bored wheels and hands (bore = shaft + 0.005), day pair now 10/40 teeth at module 0.16. Volumes before -> after: fixed 4234 -> 313.8 mm3, mobile 853 -> 252.1 mm3 (stage 2). Margins: thickness deviation 0.1225 of 0.2; smallest drive overlap 0.0317 drawn and 0.0235 moved away (limit 0.01); case 20.354 of 20.7 and 13.1 of 13.4. What breaks first if it went lighter: drive overlap, then thickness.
  - Fix round after the review: `seated` also needs the parts of a mobile to form one piece (a ring and a plug seated only on each other passed before); the intro and the Light bullet say the volume limits bind every stage; the Tolerant bullet says which mobile is moved; the STEP reader's memory limit is skipped where the platform refuses it (workstream A's macOS failure), with `tests/test_step_memory_limit.py`; study leftovers removed from `geometry/watch.py`; two tooth anchors added.
- Verified by (command and result), run by the orchestrator on 42482a0:
  - All 36 anchors, one process each, two at a time: `timeout 1500 python3 tests/test_anchors_watch.py 1 --base REF --only "NAME"` for every name: 36 ok, 0 off, no retry, no timeout, 3093 s wall. Gold 1.0 at stages 1, 2, 3 (kept 15/17) and 4, each taking 213 to 254 s. New anchors: one extra solid block as a fixed part 0.3781 (size, light); one extra heavy mobile in a cage 0.3781 (size, light); a wheel moved 0.4 up its arbor 0 (assembled, clear, seated); two parts of one mobile overlap 0 (assembled); seconds pinion with fat teeth 0.4168 (tolerant only); a pinion with teeth thinned until they no longer drive 0.2420 (train, seconds, tolerant); a pinion cut 3 percent too coarse 0.4168 (tolerant only); s4 a part put in after the part of its mobile that blocks it 0.4460; s4 dial left out of the order 0.0556; s4 bridge on before the wheels 0.2608. Old anchors unchanged in outcome, except "one tooth count declared wrong", now 0.1361 because it also fails `tolerant`.
  - `python3 solution/reference_watch.py OUT`: four stages in about 35 s. Bundles for stages 1 to 4 build; `grep -rnIl "HAND_SPEED|DAY_SPEED|Fraction|mesh_run|watch_gears|SESSION|CLAUDE|HANDOFF|solution/|WEIGHTS|grade_watch|/home/|/root|spoke|skeleton|corners|placeholder"` over them lists no file; `tools/submit.py` accepts the reference at stages 3 and 4.
  - Builder REF's full-grader runs on 8945dce (before the fix round): stage 1 reward 1.0 (208 s, peak 4525 MB), stage 2 1.0 (267 s, 4511 MB), stage 3 1.0 with kept factor 1.0 (239 s, 4521 MB), stage 4 1.0 (32 s, 405 MB).
- What the new rules do to last night's agent designs (measured by the builders on the nine stage-1 to stage-3 submissions; those designs were made under the old rules, so this shows what must now be designed differently, not how the models will score):
  - Volumes, fixed / mobile in mm3: Sonnet 561 to 587 / 436 to 509; Opus 2755 to 2759 / 328 to 465; Fable 2477 to 2481 / 1030 to 1137. Limits 346 / 278: all nine fail `light`.
  - Overlap inside a mobile: Opus and Sonnet overlap every wheel with its arbor (0.2 to 1.4 mm3 per pair), which now fails the hard requirement; Fable has none, but 13 to 14 of its parts have nothing stopping them along the arbor, so `seated` fails.
  - `tolerant` at 0.03: all nine pass. At 0.04 and 0.05 only one Sonnet mesh fails (drive overlap 0.0094 and 0.0078 moved away).
- Review (Sonnet, fresh agent, commit 8945dce): first line "No blocking findings". It read every sentence of the new rules for a second reading: where two readings exist the stricter one only makes an agent over-build; an exact-radius fit overlaps by at most 0.0013 mm3 and a clearance of 0.0005 gives 0. Faster `mesh_run` equal to the plain one to 1e-9 on 24 cases plus two built to fool the cut. Its should-fix items are the fix round above. Left open as notes: a ring on a shaft with a 0.01-thick stop passes `seated`; a mobile made as one fused part is not tested by `seated` (stated in the spec); a degenerate two-box design scores 0.05 at stage 1.
- Went wrong: (1) the first full anchor run hung on the fork problem described under Decisions and cost about 45 minutes. (2) My first volume target for `light` would not have bitten; caught by builder LIGHT's measurement before the reference was finished.
- Not verified, or assumed:
  - No clean agent has seen this version. Nothing here says it produces a gap. `tolerant` separates none of last night's designs; `light` and `seated` are cheap for an agent to check itself. The part that feeds the one mechanism seen on a frontier model (workstream A's GPT chain B, 0.42 at stage 4) is stage 4 testing every pair.
  - The limits are tight (reference plus 10 percent) and each stage has 35 minutes. If agents run out of time on the skeleton frame, that is a timing fault, not difficulty; the chains will show it.
  - After the fix round the reference was graded with the thickness test only inside the anchor run (gold anchors), not from the command line.
  - Two builds of the reference differ in bytes for a few filleted parts; within one build kept files are copied forward, so stage 3 and 4 are unaffected.
  - The alias exploit found by the review session (real 44/46 teeth declared 6/3 scores 1.0) is still present on main; it predates this build and is the exploits session's fix 1.
  - Nothing ran in Harbor. Workstream A's image and bundles are out of date from this commit.
- Files changed: `geometry/watch.py`, `geometry/core.py`, `geometry/watch_gears_cad.py`, `solution/reference_watch.py`, `tests/grade_watch.py`, `tests/test_anchors_watch.py`, `tests/test_seated.py`, `tests/test_tolerant.py`, `tests/test_step_memory_limit.py`, `tests/measure_new_rules.py`, `tests/measure_fit_clearance.py`, `environment/public/SPEC_WATCH.md`, `SPEC.md`, SESSION.md.
- Need from others: A, the task image needs rebuilding from this commit, and the stage timeout may need to rise (design stages grade in about 4 minutes; unchanged). The exploits session has the branch and the numbers. itswinther: when to run chains (three per model), and whether before or after the exploit fixes.
- Next: fix the anchor runner; then the stricter change-request stage (a frozen part to modify, graded feature by feature), once the exploits session has settled stage 3.

### 2026-11-14 14:30 | A: STANDARDS.md (industry standards mapped to the task) | Mikael + Claude
- Did: researched agent-eval standards (METR, Terminal-Bench 2.0, Inspect, SWE-bench Verified and pass@k, HAL, LLM-as-judge), test standards (ISO/IEC/IEEE 29119-3, ISO 9001 8.3, V-model, IEEE 829), watch standards (ISO 3159/COSC, ISO 1413, ISO 764, NIHS) and real movement numbers, plus real components (gear norms, mainspring and jewel catalogues, OM10). Wrote `STANDARDS.md`, which maps each to concrete changes in task.toml, test docs, acceptance numbers, judge protocol and run reporting, and gives a top-8 list.
- Key numbers (primary, ETA CT 2824-2, 06.10.2022): Ø 25.60 mm, 4.60 mm, 25 jewels, 28,800 A/h, power reserve min 38 h / typical 42 h, keyless parts list. Secondary: barrel about 8 h per turn (40 h spring = 5 turns), click recoil about 2 ratchet teeth, stem travel about 1 mm, about 30 to 40 crown turns to wind fully.
- Proposed (not applied): our `WIND_MIN = 2°` per crown turn accepts about 180 crown turns per barrel turn; propose a band of 3 to 12, reserve >= 38 h from a full wind, click run-back <= 2 teeth. These are spec changes and need B's and the humans' yes.
- Section 4 (real components) re-adds supplied datasheet data, which CLAUDE.md lists as cut from scope: a human decision.
- Not verified: ISO 1413/764 numeric limits (secondary), crown turns per barrel turn (no maker figure), the OM10 licence, the full NIHS list; all marked in the file.

### 2026-11-14 14:45 | A: HARBOR_RESEARCH.md (Harbor features to reuse, TB task conventions, where models fail) | Mikael + Claude
- Did: read the Harbor 0.26 source and docs (RewardKit, analyze/check/lint, multi-step, separate verifier, regrade, canary, registry, Hub leaderboards, ATIF, OpenCode agent, examples, adapters), TB2 task files, the TB2.0, TB2.1 and cad-bench Hub leaderboards, and web sources on failure taxonomies, reward hacking, CAD benchmarks and AfterQuery. Wrote `HARBOR_RESEARCH.md` with a prioritised top-10.
- Key findings:
  - Functional CAD is where frontier models collapse: CAD-bench functional tier 0.04 standalone and 0.14 for agents; a right-angle gearbox builds in 96.9 % of attempts but scores 4 %.
  - Hub `gnucleus-ai/cad-bench/v3`: best agent 0.61 mean, 9 % perfect; create-and-edit is the weakest category for every frontier row.
  - TB2 harness gaps are 3 to 22 points for one model; OpenCode + Opus 4.5 scored 51.7 against 57.8 under Terminus 2.
  - A separate multi-step verifier sees only its own step's artifacts.
  - A trajectory artifact can reach the verifier, but trips lint rule `artifact-log-overlap`.
- Verified by (command and result): `uv run harbor hub leaderboard show <id> --json` for TB2.0 (142 rows), TB2.1 (22 rows) and cad-bench v3 (13 rows); `uv run harbor analyze --help` and `harbor check --help`; TB2 task.toml and tests fetched from the commit pinned in Harbor's `registry.json`.
- Not verified, or assumed: listed at the end of the file (paper figures, secondary-source numbers, the shared-verifier freezing design, the AfterQuery challenge page).
- Files changed: `HARBOR_RESEARCH.md` (new), SESSION.md.
- Need from others: B and humans: decide whether the run-log judge enters the reward (the file recommends keeping it as a separate, reported dimension, with a deterministic honesty check via `report.json`).
- Next: whatever the humans pick from the top-10.

### 2026-11-14 13:30 | A: status after a network outage; standards and Harbor research landed | Mikael + Claude
- Landed on main: `STANDARDS.md` (7085732) and `HARBOR_RESEARCH.md` (31cdd55).
  - STANDARDS: agent-evaluation standards (METR, Terminal-Bench, Inspect), test documentation (ISO 29119-3, ISO 9001 8.3, V-model), watch standards and real movement data, and real components with licensing notes. ETA 2824-2 from ETA's own document: Ø 25.6 mm, reserve at least 38 h, keyless parts list. Unitas 6497: 46 h. Click run-back about 2 teeth.
  - HARBOR_RESEARCH: what Harbor already has (RewardKit with judge criteria over the ATIF trajectory and `samples`/`guard`, `harbor analyze` with a custom rubric, `harbor check`/`lint`, metric.py, Hub leaderboards), Terminal-Bench conventions, and where models fail.
  - Its top 10 starts with: grade function; keep the headline reward deterministic, with the run-log judge as a labelled dimension at most; `harbor analyze` with our own failure rubric on every job; TB2.1-style reporting over `-k 8`; also run each model under its native harness (TB2 harness gaps 3 to 22 points; OpenCode the weakest for Opus 4.5); prove the timeout and memory never bind.
- Keyless (`spikes/keyless/`), saved as work in progress in this push:
  - built: acceptance scoring (AT steps in order), the honesty report, the judge task and docs (PROMPT, CONTEXT, STEP_BY_STEP, SOLUTION draft, REVIEW_RUBRIC, JUDGE_PROMPT);
  - broken: forward winding under the latest engine change; it was being traced when the builder session dropped (network outage about 13:20). Not yet fixed. No model runs yet.
- Queued for keyless: STANDARDS fixes before the runs:
  - winding band of 3 to 12 crown turns per barrel turn (today's WIND_MIN accepts about 180);
  - reserve at least 38 h; click run-back at most 2 teeth;
  - AT-0 to AT-6 IDs; a deliberate "try to cheat" run; a hardened judge.

  Then v2, "engineer with datasheets": supplied component datasheets plus one blanket clause ("operate within the ratings in the supplied datasheets and accepted watchmaking practice"), with implied checks traced to datasheet values.
- Decisions for the team (also in the files): the acceptance test as the score (proposal 12:40); where `seated` is graded; keyless in scope; real components / datasheets (CLAUDE.md cut "datasheet lookup" on day one); the four questions for the organisers in TEST_ENVIRONMENT.md.

### 2026-11-14 13:40 | A: one-page research brief | Mikael + Claude
- Did: wrote `RESEARCH_BRIEF.md`. It brings together our experiments, 13 papers on CAD and engineering agents, the Harbor and Terminal-Bench findings, the standards and real data, the design conclusions and the open questions, with pointers to the full documents.
