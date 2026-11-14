# Watch in Four Stages

An RL environment for the AfterQuery challenge at Junction 2026. An agent designs
the gear train of a mechanical watch in real CAD, and three more agents then
extend it, rework it and assemble it, each inheriting the frozen work of the one
before.

**Status (Saturday 14 Nov, 10:15 Helsinki):** the task, grader, reference and
anchor suite are built and run. It is not yet packaged as a Harbor task, and it
has only been tested on Claude models. Three more checks are being built on a
branch and are not described here until they land: a mass budget, every part of
a wheel assembly seated and assembled on its own, and gears that still run with
their arbors 0.03 mm out of place. Live state is in [SESSION.md](SESSION.md).

The repo is still named `board-in-a-box` after the first idea, which was dropped.

## What the agent does

It gets a mainspring barrel (a 96-tooth gear that turns once every 8 hours) and a
written specification. The work runs as four stages. Each stage is a fresh agent
conversation that starts from the previous stage's submitted files.

| Stage | Job | What is frozen |
| --- | --- | --- |
| 1. Design | Design the gear train and the hour, minute and seconds hands, as STEP parts plus a `movement.json` | nothing yet |
| 2. Extend | Add a 24-hour hand to the received movement | every existing wheel: its axis and its part file |
| 3. Change | The barrel now turns once every 6 hours; make the watch keep time again, keeping as many part files as possible | nothing, but changed files cost score |
| 4. Assemble | Give an order and a collision-free path for every part | everything |

Parts are written with CadQuery and submitted as STEP files. The agent has a CAD
kernel, a mesh kernel and a submit command that checks file format only. It has
no measuring tools and no copy of the grader's tests, so it has to build its own
checks from the specification.

The full agent-facing text is
[environment/public/SPEC_WATCH.md](environment/public/SPEC_WATCH.md).

## Why it should be hard

Every graded number is stated in the specification, with one deliberate
exception: what the hands of a watch do (hour once per 12 hours, minute once per
hour, seconds once per minute, all clockwise) is left for the agent to know.

The difficulty we are testing is not the puzzle inside one stage. It is that a
choice made early can pass its own stage and break a later one that the agent
making the choice cannot test. A wheel held in place by a clever retaining
feature passes stage 1; if that feature makes the part impossible to put in, the
watch fails at stage 4.

## How it is scored

Each stage has hard requirements (score 0 if one fails) and weighted pass/fail
checks, for example: every wheel turns freely, every wheel is held in its
bearings, every pair of gears runs through a full turn without jamming or
disengaging, the hands show the time, the movement fits the case, every part is
thick enough to print.

```
stage score = 0.5 * p^2 + 0.5 * [every check passes]      p = weighted share of checks passed
stage 3     = that, times a kept-parts factor
stage 4     = the same formula with p = share of parts installed
chain score = stage 1 * stage 2 * stage 3 * stage 4
```

The grader never runs submitted code. It reads the STEP files, turns them into
solids and tests them.

## Results so far

One clean chain per model, run headless from a folder outside the repo, on the
final version of the task (14 Nov, 07:27 to 08:33):

| Model | Design | Extend | Change | Assemble | Chain score |
| --- | --- | --- | --- | --- | --- |
| Reference | 1.0 | 1.0 | 1.0 | 1.0 | 1.00 |
| Claude Fable 5.2 | 1.0 | 1.0 | 1.0 | 1.0 | 1.00 |
| Claude Opus 5.5 | 1.0 | 1.0 | 1.0 | 1.0 | 1.00 |
| Claude Sonnet 5.5 | 1.0 | 1.0 | 1.0 | 0.47 | 0.47 |
| Do nothing | 0 | | | | 0 |

What this shows, and what it does not:

- **Sonnet's failure is the kind the task is built to find.** At stage 2 it added
  a part whose arbor has a wide collar below a closed hole and a wide head above
  it. That passed stage 2. At stage 4 the part cannot be installed by any path.
  The same thing happened on an earlier three-stage version, with a different
  design.
- **The two strongest models show no gap.** They scored 1.0 on every stage.
- **It is one run per model**, on Claude models only, not in Harbor.
- **The change stage did not bite.** Every model read the coming change at stage
  1, split its design into many files and swapped one gear pair at stage 3.

Each run's transcript, scripts, submitted files and grader output are packed in
`transcripts/watch4_chain_*`.

## Running it

Tested on Python 3.13.

```bash
pip install -r requirements.txt
```

Build the reference and grade each stage:

```bash
python3 solution/reference_watch.py /tmp/ref
```

```bash
cd tests
python3 -I grade_watch.py /tmp/ref/stage1 --stage 1 --reward /tmp/ref/r1.txt
python3 -I grade_watch.py /tmp/ref/stage2 --stage 2 --prev /tmp/ref/stage1 --reward /tmp/ref/r2.txt
python3 -I grade_watch.py /tmp/ref/stage3 --stage 3 --prev /tmp/ref/stage2 --reward /tmp/ref/r3.txt
python3 -I grade_watch.py /tmp/ref/stage4 --stage 4 --prev /tmp/ref/stage3 --reward /tmp/ref/r4.txt
```

Run the anchor suite (27 submissions with their expected scores: the reference,
do-nothing, shortcuts and partial work), from the repo root:

```bash
python3 tests/test_anchors_watch.py
```

Run a clean agent chain and grade it. This needs the `claude` command line and a
run folder outside the repo:

```bash
environment/run_clean_chain.sh /path/outside/repo/run1 claude-sonnet-5-5
```

```bash
python3 tests/grade_chain.py /path/outside/repo/run1
```

**Not available yet:** the one-command Harbor evaluation the judges will use
(`harbor run -p ... -a ...`). See "Open work".

## Repository layout

```
environment/public/   what the agent reads: SPEC_WATCH.md, INSTRUCTION_WATCH_S1..S4.md
environment/          bundle builder, format-only submit, clean-chain runner
geometry/watch.py     public engine: movement.json, speeds, the mechanical tests, assembly replay
geometry/core.py      kernel helpers (shipped to the agent as tools/kernel.py)
geometry/watch_gears*.py   gear makers, private to the reference
tests/grade_watch.py  the grader (the hand speeds live only here)
tests/test_anchors_watch.py   anchor suite
tests/grade_chain.py, tests/pack_run.py   grade and package a four-stage run
solution/reference_watch.py   reference for all four stages
tools/viewer/         interactive 3D page per stage (run the train, explode, replay the assembly)
transcripts/          every agent run from the weekend, with grader output
spikes/, holdtheline/ other ideas that were tested and showed no gap
SESSION.md            shared log: status, decisions, requests between teammates
```

Older files for the dropped ideas (`*_h2*`, `*_md*`, `tools_cli.py`, `grade.py`,
`reference.py`) are still in the tree as history.

## What we tried before this

Nine task ideas were built and tested over one night. Every fully specified
task with exact feedback was solved at or near 1.0 by the strongest models,
usually in under ten minutes: an enclosure design, a packing problem, furniture
path planning, a single-stage watch, an abstract gear train, a five-step watch
where earlier steps could be revised, a watch-regulation task with hidden
physics, a wrist tracker and a decision game. Hiding the test
code, leaving common-sense requirements unstated and adding a continuous score
did not change that. Freezing earlier work between stages is the only thing that
produced a shortfall. The details are in [SESSION.md](SESSION.md) and
[spikes/README.md](spikes/README.md).

## Open work

- Package the four stages as one Harbor task and run reference, do-nothing and
  agent runs in the sandbox.
- Run the task on a non-Claude model (workstream A has GPT running in Harbor).
- More than one run per model, to show the result repeats.
- Decide how to present a gap that appears for a mid-tier model and not for the
  strongest ones.
- The kept-parts score at stage 3 counts files, so a design split into many
  files makes that stage free.
- Demo video and the final version of this README.

## Team

Four people, each working with a Claude session: itswinther, Mikael, Yoseph and
Abhishek. How the sessions stay in step is in [CLAUDE.md](CLAUDE.md).
