# Handoff: the watch as one start-to-finish job

Written 2026-11-14 15:30 Helsinki by the workstream B orchestrator session
(itswinther + Claude) for a new session that takes over row B. Read this whole
file before doing anything. `CLAUDE.md` holds the team rules and still applies.
`HANDOFF_OVERNIGHT.md` and `HANDOFF_EXPLOITS.md` describe finished work; read
them only for history.

## 0. Your role

You take over workstream B (the watch task's specification, grader, reference
and anchors) for itswinther. The session before you worked as an orchestrator:
it briefed builder agents (Opus) in separate git worktrees, merged their
branches, ran the acceptance commands itself, and had a Sonnet reviewer read the
result. That worked and is the recommended way to continue, with one warning:
four builders at once hit itswinther's 5-hour usage limit at about 14:40. Run
two at a time unless itswinther says otherwise.

Nothing is being built right now. itswinther asked for an update and
recommended next steps, and has not yet said go. **Ask before starting step 1
of section 7.**

## 1. The project in six lines

- Junction 2026, AfterQuery challenge. We build an RL environment in Harbor
  format: a task, a reference solution, and a verifier that writes one number
  from 0 to 1. Submission is Sunday 15 Nov, 10:00 Helsinki.
- Judging: the gap between frontier agents and the reference 30, meaningful
  difficulty 30, reward integrity 25, craft 15. A gap that comes from withheld
  information, trick wording, a time limit or a broken tool scores zero.
- The task: a coding agent designs a mechanical watch movement as STEP parts
  made with CadQuery, plus JSON files that describe it. The grader loads the
  parts and tests them geometrically (gears turned against each other, parts
  moved to see what holds them, an assembly replayed pose by pose).
- Workstream A (Mikael) owns the Harbor harness, the model runs, the datasheets
  and a second mechanism, the crown-winding works ("keyless").
- The team's goal, from `CLAUDE.md`: frontier models (Fable, Opus, GPT class)
  consistently below the reference, for reasons we can explain.
- itswinther's principle since 13:30: **we do not design for failure.** The
  task must be what a professional would really be asked to do.

## 2. Decisions that bind you (all by itswinther on 14 Nov; lines in `SESSION.md` under Decisions)

1. **Nothing is frozen.** One brief from start to finish, as a professional
   would get it. No prompt per stage, no hand-over between agent conversations.
2. **Five parts of one job:** going train and hands; 24-hour hand; the barrel
   change; crown winding (A's mechanism); assembly order and paths.
3. **No hints in what the agent reads.** A role and context ("you are a
   watchmaking professional"), the goal, the deliverables, the supplied data and
   the acceptance test with every number. Never how to do it.
4. **No feedback to the agent.** It is never told whether anything passed or
   failed. It delivers a full build, and the build is graded afterwards.
5. **Scoring:** every part counts even if an earlier part failed (no in-order
   gating), and the build as a whole is scored as well. Mikael agreed at 14:45.
6. **Datasheets are in the environment.** Requirements reach the agent as the
   documents a professional receives, not as prose digested for a model.
7. **Tokens, time and cost of a run are recorded and reported.** They are not
   part of the score, and limits are generous so they never decide a result.
8. **Runs:** 8 per model, through Harbor, in Docker and Modal sandboxes.
9. **Scale:** the watch stays at its present size, about 1.617 times an
   11 1/2 ligne movement, presented as a demonstration-scale model. Mikael's
   datasheets are already regenerated at that scale.
10. **Format:** Harbor's own task layout, and four documents per task:
    `CONTEXT.md`, `PROMPT.md` (becomes `instruction.md`), `SOLUTION.md` (answer
    ranges, what the reference and each anchor score), `STEP_BY_STEP.md`. See
    `TASK_DOCS_TEMPLATE.md` and `TEST_ENVIRONMENT.md`.

Choices the previous session made without an explicit yes; raise them with
itswinther before building on them:

- The barrel change becomes a **variant in the same delivery** (the movement
  for the 8-hour barrel and a variant for the 6-hour barrel, graded on the
  variant working and on the parts the two share), because a change that
  arrives after delivery is a second prompt.
- Proposed weights: going train and hands 0.25, 24-hour hand 0.10, barrel
  variant 0.15, crown winding 0.25, assembly 0.25; score = 0.5 x weighted share
  of checks passed + 0.5 x (1 if the whole build passes everything, else 0).
  Mikael wants the whole-build term kept at 0.5 or more (mentor's point: with
  per-part grading alone a model can skip the hardest part and still score
  0.75).
- The delivery step still reports file-format errors (nothing about
  requirements). itswinther has not said whether that should go too.
- `light` (the volume limits) was sized as our reference plus 10 percent, which
  is a limit made to bite. It should be replaced by limits from the datasheets,
  or dropped.

## 3. What is on `main` (SPEC.md version 0.6, commit d36109b and later)

The task on `main` is still the **old shape**: four stages, one agent
conversation each, each inheriting the frozen result of the one before. That
shape is decided against (section 2) but the engine, the checks, the reference
and the anchors underneath it are what you build the new shape from.

| Path | What it is |
| --- | --- |
| `geometry/watch.py` | Engine and the one constants block. `Movement`, `mesh_run`, `held`, `seated`, `pieces`, `volumes`, `assembly_replay`, `thin`, part loading |
| `geometry/core.py` | Kernel: STEP loading in a child process, tessellation, voxel thickness test in slabs. Shipped to the agent as `tools/kernel.py` |
| `geometry/watch_gears_cad.py` | Private CAD gear maker and helpers for the reference |
| `tests/grade_watch.py` | Grader: `python3 -I grade_watch.py /abs/folder --stage N [--prev /abs/prev] --reward FILE [--details FILE] [--skip a,b]` |
| `tests/test_anchors_watch.py` | 41 anchors. Each runs in its own interpreter: `python3 tests/test_anchors_watch.py WORKERS [--base REF] [--only NAMES] [--timeout S]` |
| `tests/test_exploit_rules.py`, `tests/exploits/` | The exploit hunt's cases (52 assertions) and builders |
| `tests/test_seated.py`, `test_tolerant.py`, `test_cad_gears.py`, `test_step_memory_limit.py` | Fixture tests |
| `tests/grade_chain.py`, `tests/pack_run.py`, `environment/run_clean_chain.sh` | Run, grade and pack a headless chain (old four-stage shape) |
| `solution/reference_watch.py` | Reference for the four stages: spoked wheels, plates cut to bars, stepped arbors |
| `environment/public/SPEC_WATCH.md`, `INSTRUCTION_WATCH_S1..S4.md`, `SPEC_WATCH_GIVEN_NOTOOLS.md` | What the agent reads today. Full of hints that must go |
| `environment/make_bundle_watch.py`, `environment/submit_template.py` | Builds the agent's folder and its format-only delivery check |
| `transcripts/watch4_chain_*` | Last night's three Claude chains, packed |
| `harbor/watch4/` | A's Harbor packaging of the four-stage task and two GPT chains |
| `spikes/keyless/` | A's crown-winding task: contact engine, grader, datasheets, `INTERFACE_FOR_B.md` |

Checks at a design stage (weights; totals 23 at stage 1, 27 at stages 2 and
3): free to turn 1, held 2, seated 2, the train runs 3, tolerant 2, nothing
else collides 1, hour, minute and seconds hand 2 each, hand arrangement 1, hands
reach 1, size 1, printable 1, light 2; plus 24-hour hand 3 and its placement 1.
Hard requirements: files valid; assembled (nothing overlaps, parts of one
mobile do not overlap, the fixed parts form one frame). What the hands of a
watch do is deliberately not stated to the agent and lives only in the grader.

Verified by the previous session on the merged code (commands and output are in
its `SESSION.md` entries of 13:14 and 15:11):

- Reference 1.0 at all four stages on the full grader; about 4 to 6 minutes per
  design stage; peak memory 1.5 GB.
- 41 of 41 anchors ok; exploit-rule test 52 of 52; the four fixture tests pass.

Not verified: no agent has run on any version after last night's. Bundles were
not rebuilt and searched for leaks after the exploit fixes were merged. Nothing
of version 0.6 has run in Harbor.

## 4. What the evidence says (so you do not repeat it)

| What was tried | Result |
| --- | --- |
| Fully stated numeric tasks with exact checks (enclosure, packing, furniture paths, single-stage gear train, regulation, Swiss-lathe probe) | 1.0 or close for every frontier model |
| Right-angle gearing with exact kinematics (A's spike) | GPT-6.1-sol 1.0 three times, Sonnet 1.0 |
| Four frozen stages, last night's version | Fable 1.0, Opus 1.0, GPT 1.0 and 0.42 (two chains), Sonnet 0.47. Every shortfall was a design that passed its own stage and could not be assembled later |
| `light`, `seated`, `tolerant` (built today) | Not run with agents. Measured on last night's designs: all nine fail `light`; Opus and Sonnet overlap wheels and arbors; `tolerant` fails nothing |

Reading: whatever an agent can check with a few lines of code, it checks.
The only shortfalls on frontier models came from freezing, which is now decided
against. So scores of 1.0 are the likely outcome of the new shape unless reading
a full realistic specification is what trips the models (the industry contact's
claim). itswinther knows this and chose realism. **Report results as they are;
do not tune a rule to make a model fail.**

A partial regrade of last night's chains under the new rules (from the
exploits session, full grader; my build before the exploit fixes / with them):
Fable 0.34/0.34, 0.36/0.36, 0.36/0.36, 0.19/0.19 across the four stages; Opus
0/0, 0/0, then unfinished. Identical wherever both finished, so those drops come
from `light` and `seated`, not from the exploit fixes. Sonnet and GPT were not
finished. Those designs were made under the old rules.

## 5. Working with Mikael (workstream A)

You cannot message Mikael's sessions: they run on his machine and account. The
only channel is `SESSION.md` on `origin/main`. His session reads it and answers
on the same line, usually within half an hour. Do this:

- **When you start:** append an entry saying a new session has taken over row B,
  and add a Requests line to A asking for the current state of the keyless
  reference and engine (see below). Publish at once.
- **Before each new piece of work, and before every push:** fetch, merge
  `origin/main`, and read the Current state table, the Requests addressed to B,
  the Decisions added since your last read, and A's newest entries. His clock
  runs ahead of the commit times, so read by commit order, not by the time in
  the heading.
- **Anything both sides depend on** (a file path, a function signature, a file
  format, a number) goes under Decisions before either side builds on it.

The split Mikael agreed to at 14:20:

- **B builds:** the acceptance grader for one delivered movement (one verifier
  call, weighted parts plus the whole-build term, per-part results in the
  details file), its constants, anchors and the reference as one delivered
  folder; the acceptance-test section and the file-format sheet of `PROMPT.md`,
  generated from the constants with no hints; `SOLUTION.md` and
  `STEP_BY_STEP.md` for the watch.
- **A builds:** the datasheets and their real-world numbers; the Harbor task
  (`task.toml`, Dockerfile, `tests/test.sh`, `solution/solve.sh`, canary,
  `harbor check`, oracle 1.0 and nop 0.0); the 8 runs per model in Docker and
  Modal; the tokens, time and cost table; `CONTEXT.md` with workstream E.
- **Interface:** every number an agent needs lives once, in the constants block
  of `geometry/watch.py`. A posts datasheet values in `SESSION.md`; B puts them
  in the constants; the bundle builder checks the datasheet files against the
  constants and fails on a mismatch.

What A has delivered for you to build on:

- `spikes/keyless/INTERFACE_FOR_B.md`: the contact engine's entry point
  (`spikes/keyless/grade.py`), an adapter path for our STEP parts, the fixed
  interface in our coordinates (stem line, crown position, the square on the
  barrel arbor), his acceptance steps without gating, and which regions of the
  main plate he needs. **He marked the interface as proposed, "B to confirm".
  Confirming or correcting it under Decisions is your first act of
  coordination.**
- The datasheet quantities table in his `SESSION.md` entry stamped 14:20, and
  the sheets in `spikes/keyless/datasheets/` at scale 1.617.
- His entry stamped 15:35: the supplied barrel's arbor core radius must be
  stated as a fact of the supplied part, in the barrel datasheet and the brief.
  That is an action for B, in the constants.

Known state on A's side, which changes what you can rely on: at 14:05 his
keyless reference scored 0.72 on his own task (a jam when the crown is pulled),
one exploit was open, and no model had run on it. Ask for the current state
before you plan the fifth part around it.

Other sessions of itswinther's that touched this work: the "Grader exploits
fixes" session (`session_01Fk8az6eMZj3nGFe5yEgcwo`, reachable with the
claude-code-remote `send_message` tool if it is still alive; it stopped at
about 15:10 for the usage limit, with the chain regrade unfinished).

## 6. What is not built

1. The one-delivery grader over five parts.
2. The brief (`PROMPT.md`) and the file-format sheet, with every hint removed.
   Hints in today's text include "Read the later stages too", "So a wheel needs
   a bore that fits its arbor and a shoulder to rest against", "a fit needs a
   small radial clearance", "leave a little margin", "leaves no room for what
   the later stages need", "submit a first version early", and the reference's
   kept share. Every graded number must stay.
3. Datasheets for the watch side wired to the constants; limits taken from them.
4. The reference as one delivered folder covering all five parts, including an
   8-hour and a 6-hour variant and the crown-winding parts.
5. `SOLUTION.md`, `STEP_BY_STEP.md`; the anchor "everything except the hardest
   part"; anchors for the new shape.
6. The Harbor task for the new shape, and any agent run (A's side).

What goes away with freezing: the stage-2 and stage-4 "locked" gates, the
frozen-file rules, the stage-3 kept share between stages
(`REF_KEPT_VOLUME_SHARE`; a shared-parts measure between the two barrel
variants may replace it), `tests/grade_chain.py` and
`environment/run_clean_chain.sh` in their present form.

## 7. Recommended order of work (ask itswinther for a go first)

1. **One-delivery grader.** One call grades one folder: the going train and
   hands, the 24-hour hand, the barrel variant, the crown winding (A's engine
   through the adapter of `INTERFACE_FOR_B.md`), the assembly. Per-part results
   in the details file, one reward. Keep every existing guarantee: reward 0
   written first, only named files opened, each check in its own try block,
   never runs delivered code.
2. **Brief and data.** `PROMPT.md` without hints, the file-format sheet, the
   watch datasheets checked against the constants.
3. **Reference as one folder,** then `SOLUTION.md` and `STEP_BY_STEP.md`
   generated from it and the constants.
4. **Anchors** for the new shape, including "everything except the hardest
   part" and do-nothing; a review by a fresh Sonnet agent with a specific brief
   to look for sentences with two readings and for leaks in the agent's folder.
5. **Hand to A** for the Harbor task and the 8 runs per model. Do not run agent
   chains on the old four-prompt shape; it measures something already dropped.

## 8. Commands that work today

```bash
pip install -r requirements.txt            # manifold3d 3.5.5, scipy, numpy, trimesh, cadquery 2.8.0 (build123d cannot be installed beside it)
python3 solution/reference_watch.py /abs/OUT            # about 40 s, writes OUT/stage1..stage4
cd tests && python3 -I grade_watch.py /abs/OUT/stage1 --stage 1 --reward /abs/r1.txt --details /abs/d1.json
python3 -I grade_watch.py /abs/OUT/stage2 --stage 2 --prev /abs/OUT/stage1 --reward /abs/r2.txt
python3 tests/test_anchors_watch.py 3 --base /abs/OUT    # from the repo root, about an hour
python3 tests/test_exploit_rules.py --base /abs/OUT      # about 15 minutes
python3 environment/make_bundle_watch.py /abs/B1 --stage 1
```

## 9. Things that went wrong, so you can avoid them

- **Check that a background job started.** One grading run was wrapped in
  `/usr/bin/time`, which this machine does not have, and nothing ran for 20
  minutes.
- **Do not fork after CAD libraries have started threads.** The old anchor
  runner hung that way; the new one starts each anchor in a fresh interpreter.
- **Do not change files under a running job.** The anchor runner and the chain
  runner read the working tree while they run. Builders work in their own
  worktrees for that reason. To publish a `SESSION.md` change while your branch
  holds an unvalidated merge, commit it in a temporary worktree of `origin/main`
  (`git worktree add --detach DIR origin/main`) and push from there.
- **Merge, do not rebase,** when your branch has merge commits; a rebase
  flattens them and your pushed branch diverges. `CLAUDE.md` says rebase; with
  builder merges use `git merge origin/main` and never force-push.
- **Size limits from evidence, not from the reference.** My first volume limit
  would not have bitten and my second was sized to bite; itswinther now wants
  neither.
- **A check that changes meaning needs its anchors reread.** Three merges today
  left an anchor expecting the old result. None was a grader fault, but each
  cost a rerun.
- **Usage limits.** Four Opus builders in parallel hit the 5-hour limit. A
  stopped builder keeps its work; send it a message to continue once the limit
  resets.
- **Clock:** use `TZ=Europe/Helsinki date '+%Y-%m-%d %H:%M'` for entries.
- **The stop hook** asks you to push your own `claude/...` branch when it has
  unpushed commits. That is fine. It is not a reason to push to `main`.
- `.claude/worktrees/` is in `.git/info/exclude` on the previous machine only;
  add it again so builder worktrees are never committed.

## 10. Done, for the next milestone

- One command grades one delivered folder over five parts and writes one
  reward; the reference scores 1.0; do-nothing scores 0; "everything except the
  hardest part" scores well below the reference.
- The agent's folder holds the brief, the datasheets, the format sheet, the
  supplied parts and the kernel, and nothing else; a search finds no hint, no
  hand speed, no reference, no project document.
- Every number in the brief and the datasheets comes from the constants block.
- A reviewer's last report has no open blocking finding.
- A has what the Harbor task needs, written under Requests, and has confirmed
  the interface under Decisions.
- `SPEC.md` version bumped, every changed rule under Decisions with old and new
  value, row B updated, an entry that says what was run and what was not.
