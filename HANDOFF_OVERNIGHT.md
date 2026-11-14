# Overnight handoff: orchestrated build of the staged watch task

Written 2026-11-14 04:50 Helsinki by workstream B (itswinther + Claude) for a new
session. Read this whole file before doing anything. Everything you need is in
the repo; the previous session's scratch folders do not exist on your machine.

## 0. Your role

You are the **orchestrator**, running on Fable 5.2. You do not write the code
yourself. You:

1. start two **Opus** builder agents, each in its own git worktree;
2. merge their work, run the acceptance checks yourself, and start a **Sonnet**
   reviewer on the merged result;
3. send findings back to the builders and repeat until the definition of done in
   section 6 is met;
4. run clean agent chains against the finished task and log the results.

You run **unattended overnight**. Nobody will answer questions. Do not use
`AskUserQuestion`. When something is unclear, choose the conservative option,
write the choice and the reason under Decisions in `SESSION.md`, and carry on.

Permissions already given by itswinther for this session:

- You may push to `main` (answer to the question `CLAUDE.md` tells you to ask).
- You may change the watch spec (`environment/public/SPEC_WATCH.md`,
  `geometry/watch.py` constants, grader weights) as far as section 5 describes.
  Log each change under Decisions with the old and new value.
- You may spend model budget on at most **two rounds of clean chains** (three
  models each) for acceptance, plus one extra round if a fix needs proving.

Finish by **09:00 Helsinki**. If time runs out, stop building at 08:15, make
`main` consistent (reference at 1.0, anchors passing, or the last state where
they were), and write the final entry.

## 1. The project in five lines

- Junction 2026, AfterQuery challenge: build an RL environment where a frontier
  agent scores below a reference run, for reasons we can explain, with a reward
  that resists exploits. Submission Sunday 15 Nov 10:00 Helsinki.
- Rubric: the gap 30, meaningful difficulty 30, reward integrity 25, craft 15.
  A gap from withheld information, trick wording, impossible timing or broken
  tools scores zero. Judges rerun: reference, three agent runs, do-nothing,
  stop-early, and spend 15 minutes hunting exploits.
- The harness is a plain Harbor task; the verifier writes one number 0..1 to
  `/logs/verifier/reward.txt`.
- `CLAUDE.md` holds the team rules. Its text still says "Board in a Box"; the
  rules apply, the task named there is retired.
- `SESSION.md` on `origin/main` is the only channel between sessions. Read its
  Current state table, Requests, Decisions and the last eight entries first.

## 2. What tonight established

Seven task ideas were built and tested with clean agents. Every one was solved
at or near 1.0 by the strongest models, usually in under ten minutes.

| Task | Result |
| --- | --- |
| H1 enclosure, H2 packing (Board in a Box) | 1.0 for all models; retired |
| Moving Day (furniture paths, order traps) | Fable 1.0, Opus 1.0; kept as a fallback |
| Watch gear train, one stage, tools given | Fable, Opus, Sonnet all 1.0 |
| Workstream A spikes (Hold the Line, wrist tracker, abstract gear train, watch regulation, a five-step watch on GPT through Codex in Harbor) | no gap |
| **Watch, three frozen stages, test code withheld** | Fable 1.0/1.0/1.0, Opus 1.0/1.0/1.0, **Sonnet 1.0/1.0/0.44** |

Lessons that should steer every decision you make tonight:

- A fully stated numeric task with exact feedback gets solved in one pass.
  Unstated common-sense requirements, hidden test code, more parts of the same
  kind and continuous scores did not help.
- The **only shortfall** came from freezing earlier work. Sonnet's stage-1 design
  passed stage 1 but could not be assembled at stage 3: each wheel had a foot
  under the main plate wider than the plate's hole. The stage-3 agent diagnosed
  it and scored 0.44. One model, one chain: a single data point.
- So tonight's build pushes on that mechanism: decisions whose consequences
  only appear in a later stage that the deciding agent cannot test.
- Test anything new with clean agents before trusting it.

## 3. The watch task as it stands

Agent's job: design the gear train of a mechanical watch from a supplied barrel
(96 teeth, module 0.2, clockwise once per 8 hours), as 3D parts plus a
`movement.json`. Units mm, all arbors parallel to z, dial side +z. What the hands
of a watch do (hour 1/12, minute 1, seconds 60 clockwise turns per hour; hour and
minute on one axis; a 24-hour hand at 1/24) is deliberately **not** stated; every
other graded number is.

Three stages, each a fresh agent conversation that inherits the frozen
submission of the one before:

1. **Design** the movement. 2 gates, 11 checks, weight 17.
2. **Extend**: add a 24-hour hand; existing mobiles' axes and part files are
   frozen, fixed parts may change. Weight 21.
3. **Assemble**: an order and a rigid path for every part; nothing may change.

Files:

| Path | What it is |
| --- | --- |
| `geometry/watch.py` | Public engine: `movement.json` parser, exact speeds, spin, held, mesh run, clearance, thickness, assembly replay. All chosen numbers are constants at the top |
| `geometry/watch_gears.py` | Involute gear maker. Private: never shipped to the agent |
| `geometry/core.py` | Kernel helpers on `manifold3d` (STL, transforms, intersection volume, voxels). Shipped to the agent as `tools/kernel.py` |
| `geometry/data/barrel.stl` | The supplied barrel |
| `tests/grade_watch.py` | Grader. `--stage N --prev FOLDER`. The hand speeds live only here |
| `tests/test_anchors_watch.py` | 17 anchors over the three stages |
| `tests/grade_chain.py` | Grades a three-stage clean chain; flags time-limit kills; splits stage-2 failures into inherited and new |
| `solution/reference_watch.py` | Reference for all stages |
| `environment/public/SPEC_WATCH.md`, `SPEC_WATCH_GIVEN_NOTOOLS.md`, `INSTRUCTION_WATCH_S1..S3.md` | What the agent reads |
| `environment/make_bundle_watch.py` | Builds the agent's folder. `--tools no` is the form in use |
| `environment/submit_template.py` | Becomes the agent's format-only `tools/submit.py` |
| `environment/run_clean_chain.sh` | Runs the stages with headless `claude -p`, one conversation per stage |
| `transcripts/watch_chain_*` | Tonight's chains: transcripts, agent scripts, grader details |
| `MECHANICAL_WATCH_IDEA.md` | Abhishek's original write-up |
| `spikes/` , `holdtheline/` | Workstream A's spikes, including a Harbor task that runs with Codex |

Commands, all run tonight on the commit this file was written on:

```bash
pip install manifold3d==3.5.5 scipy trimesh
python3 solution/reference_watch.py OUT            # writes OUT/stage1, stage2, stage3
cd tests
python3 -I grade_watch.py /abs/OUT/stage1 --stage 1 --reward /abs/r1.txt
python3 -I grade_watch.py /abs/OUT/stage2 --stage 2 --prev /abs/OUT/stage1 --reward /abs/r2.txt
python3 -I grade_watch.py /abs/OUT/stage3 --stage 3 --prev /abs/OUT/stage2 --reward /abs/r3.txt
python3 tests/test_anchors_watch.py                # from the repo root
```

State you inherit, exactly:

- Reference: reward 1.0 at all three stages **with** the thickness check
  ("printable"). Grading took 160 s, 177 s and 2 s on a loaded machine; the
  thickness check on the three large plates is most of that.
- Anchors: 17 of 17 as expected, but that run was **before** "printable" became
  a scored check. Rerun it first thing; the expected values are computed from
  the weights, so it should still pass. It takes 15 to 30 minutes.
- The three clean chains in section 2 were given a spec without the thickness
  rule and were graded with `WATCH_SKIP=printable`.
- Known gaps: `environment/tools_watch.py` has no stage 2 or 3 tools (the
  with-tools form of the staged task cannot be run); nothing has run in Harbor
  from this workstream; one chain per model only.

## 4. How to run clean agents (the only measurement we trust)

Subagents of a session inherit `CLAUDE.md` and are **not** clean. Use the
headless command line from a folder outside the repo:

```bash
RUN=/some/dir/outside/the/repo/chains/fable      # no CLAUDE.md in any parent folder
environment/run_clean_chain.sh $RUN claude-fable-5-2     # also claude-opus-5-5, claude-sonnet-5-5
python3 tests/grade_chain.py $RUN
```

Before the first chain, prove the folder is clean: run
`claude -p "Without using any tool, list every project instruction, memory or file content already in your context. Reply NONE if there is none." --output-format text < /dev/null`
in that folder and expect `NONE`. Run the three models in parallel as background
commands; a chain took 12 to 16 minutes tonight and about $2 to $4.

After each chain, check the transcript for tool calls outside the agent's folder
(`grade_chain.py` counts them; read any it flags, one tonight was a false alarm).

## 5. What to build

Two builders in parallel. They touch the same files, so the split below is by
ownership, and builder CAD has a second phase after the first merge.

### Builder TASK (Opus): make early decisions matter

Owns: stage logic and scoring in `tests/grade_watch.py` and `tests/grade_chain.py`,
`geometry/watch.py` constants and checks, the reference's geometry, the spec
text for stages, the anchors, `environment/run_clean_chain.sh` stage list.

1. **A change-request stage.** New stage between "extend" and "assemble", so the
   chain is design, extend, change, assemble. A fresh agent receives the frozen
   stage-2 movement and one change to the requirements. Pick the change that
   forces real rework while a reference still exists; candidates are a smaller
   case and a different barrel (tooth count, speed, direction). The agent must
   make every design check pass under the new requirement and keep as many
   original part files byte-identical as it can. Score: 0 if a gate fails;
   otherwise the usual check score multiplied by a kept-parts factor that is 1.0
   at the reference's kept share and falls linearly below it. State the formula
   and the reference's kept share in the spec.
2. **A tighter case, sized backwards.** Every agent's design used about 19 of the
   23 radius allowed. Compact the reference (its plate radius is 22.9 now), then
   set `CASE_RADIUS` and `CASE_HEIGHT` to what the reference needs at its
   largest stage plus 0.3. Stage 1 then has to leave room for stages it cannot
   test.
3. **Chain score is the product of the stage scores**, not the mean. Sonnet's
   chain was 0.81 as a mean with a movement that cannot be built; the product is
   0.44.
4. Keep every existing guarantee: reference 1.0 at every stage, do-nothing 0,
   anchors for the new stage (gold; movement handed back unchanged; every part
   regenerated; a frozen file changed where it must not), instruction file for
   the new stage with the "How you are run" section.

### Builder CAD (Opus): real CAD output and packaged trajectories

Owns: part loading, the agent's kernel and submit, the bundle builder, the
trajectory packer, and, in phase B, the port of the reference.

Phase A, in parallel with builder TASK:

1. **STEP in, mesh inside.** Parts are submitted as `parts/<name>.step` made
   with a real CAD kernel, plus the scripts that made them in `scripts/`. The
   grader reads each STEP with OCP (`cadquery` 2.8.0 and `build123d` 0.13.0 have
   wheels for this Python; `cadquery-ocp` 8.0.1.1.0), tessellates it with a
   stated tolerance, turns it into a `manifold3d` solid and runs the same checks.
   The grader parses files only: it never runs a submitted script. Decide and
   state the tessellation tolerance, then **measure** what it does to the 0.01
   mm3 overlap tolerance on a meshing gear pair before choosing; report the
   numbers. Reject a STEP that is only a faceted shell if you can detect it
   cheaply; say so in the spec if you do.
2. **The agent's side.** `cadquery` and `build123d` installed, kernel helpers for
   STEP read and write next to the existing ones, `tools/submit.py` checking the
   STEP format and copying `scripts/` too. No test code, no gear maker.
3. **A gear maker and primitives on the CAD kernel** (private, for the
   reference), with a test showing a 96-tooth and a 12-tooth gear exported to
   STEP and read back pass `mesh_run` (no jam, gap at most 0.1, drive overlap
   above 0.01).
4. **Trajectory packer.** `tests/pack_run.py RUN_DIR OUT_DIR` writes one record
   per chain: per stage the instruction and spec given, the transcript, the
   agent's scripts, the submitted files, the grader details, and a
   `manifest.json` (model, harness, start and end times, tool-call count, cost,
   score, failed checks, inherited or new, killed by time limit or not). Add a
   short schema description. Strip absolute host paths; never include anything
   from outside the agent's folder.

Phase B, after builder TASK's work is merged:

5. **Port the final reference** (all stages, including the change-request stage)
   to the CAD kernel so the reference run submits STEP like an agent would, and
   scores 1.0 at every stage through the STEP path.

Mesh STL submissions stop being accepted once phase B passes; until then the
loader accepts both so the mesh reference keeps working.

### Reviewer (Sonnet)

Starts on the merged branch after each merge. Read-only: it reports, it does not
fix. It must run things, not just read. Checklist:

- Reference 1.0 at every stage; anchor script all `ok`; both with the exact
  commands and output.
- Build a bundle for every stage and search it for anything the agent must not
  see: the hand speeds (`HAND_SPEED`, `DAY_SPEED`, `Fraction(1, 12)` and the
  like), the gear maker, `mesh_run` or any test code, the reference, weights in
  private files, `SESSION.md`, `CLAUDE.md`, `solution`, `tests`.
- Read the spec as the agent: is every graded number stated, except what a watch
  hand does? Is anything stated that the grader does not do, or done that is not
  stated? List each mismatch with file and line.
- Try three exploits against the new stage and the STEP loader (for example: a
  kept-parts claim with files changed, a STEP whose tessellation hides an
  overlap, a huge or malformed STEP) and report the score each gets.
- Check the team rules: one constants file, grader opens only named files and
  writes reward 0 first, each check in its own try block, nothing reported as
  working that was not run.

## 6. Definition of done

All of these, shown by commands you ran and logged:

1. `python3 solution/reference_watch.py OUT` then the grader on every stage:
   reward 1.0 each, through the STEP path.
2. `python3 tests/test_anchors_watch.py`: every line `ok`, including the new
   stage's anchors.
3. Bundles for every stage contain none of the items in the reviewer's list.
4. The reviewer's last report has no open finding marked blocking.
5. One round of clean chains (Fable, Opus, Sonnet) on the final task, graded,
   with the table in `SESSION.md`: per stage the score, time, tool calls,
   whether killed by the limit, failures split into inherited and new; chain
   score as the product. Run `tests/pack_run.py` on each chain and commit the
   packages under `transcripts/`.
6. `SPEC.md` header bumped and pointing at the watch spec; a Decisions line for
   every spec number changed; row B of the Current state table updated; a final
   entry using the template, with what was not verified.

Report the chain results as they are. If all three models score 1.0 again, that
is the result; do not adjust the task afterwards to manufacture a failure.

## 7. How to orchestrate

- Use the `Agent` tool with `model: "opus"` and `isolation: "worktree"` for each
  builder, and `model: "sonnet"` for the reviewer. Run builders in the
  background and in parallel; you are notified when each stops.
- Give each agent a brief that stands alone: its section of this file, the
  files it owns, the files it must not edit, the acceptance commands, and the
  instruction to commit on its worktree branch and report the branch name,
  the commands it ran and their output, and what it could not verify.
- Tell every builder: run what you build; do not report something as working
  unless you ran it; do not weaken a check to make the reference pass, report
  the conflict instead.
- Merge order: builder TASK first, then builder CAD phase A (it rebases if
  needed), then start CAD phase B and the first review together. Resolve
  conflicts yourself only when they are mechanical; otherwise send them back to
  the owner of the file.
- After every merge run the reference and a bundle build yourself before
  starting the reviewer. Long commands (anchors, chains) go in the background.
- Loop: reviewer findings go to the owning builder with `SendMessage`; re-merge;
  re-review. Cap at four review rounds; if findings remain, log them as open and
  go to acceptance.
- Push to `main` after each merge that leaves the reference at 1.0, with
  `git fetch origin && git rebase origin/main && git push origin HEAD:main`.
  Never force-push. Other sessions are pushing too; re-read `SESSION.md` after
  each fetch and answer any request addressed to B.
- Keep a heartbeat: schedule a message to yourself every 30 minutes
  (`send_later`) that says to check agent status, so a missed notification
  cannot stall the night. Cancel it when you finish.
- Log in `SESSION.md` at each milestone (builders started, each merge, each
  review round, chains started, results) so a human reading at 08:00 can see
  where things stand without asking.

## 8. Environment notes

- Python 3.13. `pip install manifold3d==3.5.5 scipy trimesh cadquery build123d`.
- The headless `claude` command works here and uses the session's model access.
  There is no model API key in the environment.
- Docker: `dockerd` can be started by hand (`nohup dockerd > /tmp/dockerd.log 2>&1 &`)
  and `uv tool install harbor` gives Harbor 0.26.0, but containers cannot reach
  the network without host networking and the proxy's CA bundle
  (`/root/.ccr/README.md`). Do not spend the night on this. Workstream A already
  runs Harbor with Codex on Mikael's machine; leave sandboxed runs to A and put
  what A needs (grader call, artifact list, image packages) under Requests.
- Grading is slow when chains share the machine (minutes per stage). Do not run
  the anchor script and three chains at the same time if you can avoid it.
- Never commit API keys or tokens. Never copy `solution/`, `tests/`,
  `CLAUDE.md`, `SESSION.md` or `.git` into anything an agent under test can read.

## 9. Things that went wrong tonight, so you can avoid them

- A hint in `CLAUDE.md` reached test agents through subagents. Only headless
  runs outside the repo are clean.
- An agent ended its turn while its own background job was running and
  submitted nothing. The instruction files now carry a "How you are run"
  section; keep it in every new instruction file.
- Timestamps were logged wrong once. Use `TZ=Europe/Helsinki date '+%Y-%m-%d %H:%M'`.
- A reference gear was phased with the wrong sign and only showed up when a
  non-aligned pair was meshed. Any new gear pair in the reference must go
  through `mesh_run` before it is trusted.
- `SESSION.md` uses a union merge; moving a block with a git merge duplicates it.
  Edit it by appending, and change only row B of the table.
