# Watch movement design job

An RL environment for the AfterQuery challenge at Junction 2026, in Harbor format. The agent gets a work
order and a folder of supplier documents, and designs the gear train of a mechanical watch in real CAD.

The repo is still named `board-in-a-box` after our first idea, which we dropped.

## What the agent does

It plays a movement designer at a watch maker. The order names a barrel from a catalogue, a case and a print
process. The agent must deliver, in one folder:

- the going train, frame and hands for that barrel: hours and minutes on one centre, and seconds;
- a 24-hour hand on its own axis;
- a 6-hour variant: the same barrel run faster, on the same frame;
- an assembly plan: an order and a collision-free path for every part;
- optionally, its own statement of which parts pass.

Parts are STEP files written with CadQuery. The agent has a geometry kernel and a format checker. It has no
grader and gets no score while it works. The acceptance test is a written inspection procedure in its folder
(`QA-W100`), and every number it needs sits in one cell of one supplier sheet: barrel and case catalogues,
a print process sheet, a gear rating sheet, mainspring, materials, jewels and crown sheets.

The full rules are in [SPEC.md](SPEC.md) (version 0.7). The brief is
[environment/public/job/PROMPT.md](environment/public/job/PROMPT.md).

## Why it is realistic

We checked the task against real watches (`REAL_WATCH_WORK.md`):

- The ratios are real. Barrel to centre is 8, as in Grossmann's textbook train. Real barrels run 6.3 to 8 hours
  per turn, so our 8-hour and 6-hour builds are both in range.
- The 24-hour hand is driven off the hour wheel through an intermediate wheel, as in the ETA 2893-2 and the
  Miyota 9075.
- The 6-hour variant changes one gear pair on an unchanged frame. ETA's 6497-1 and 6498-1 do the same: one
  frame family, the centre and escape wheels kept.
- Wheels are brass on steel pinions, as Saunier describes.
- The gear load, 70.1 N·mm, is the Sellita SW200-1's bridle slipping torque (16.57 N·mm) scaled to our size.

We also ran a real professional design through our checks: Marco Lang's ml01 going train, from his public
CAD file (`REAL_ML01_FAIRNESS.md`). It passes most checks. Where it fails, the file says whether the fault is
the design, the scale or our rule.

**Why our barrel turns clockwise.** Most real calibres mesh the barrel straight onto the centre pinion. Their
barrel then turns against the minute hand, counter-clockwise seen from the dial. Our catalogue barrel turns
clockwise. So the train needs one extra wheel before the centre, or the minute hand runs backwards. Lang's ml01
has exactly that extra wheel (26 teeth), and so does US patent 7,452,123. It is real but uncommon. A
counter-clockwise barrel would let a textbook train drop straight in; this one makes the designer work out the
turning sense.

## What we found so far

**The going-train job is solved by frontier models.** Nine local runs, nine scores of 1.0: Fable 5.2, Opus 5.5
and Sonnet 5.5, three each. Six ran on the early brief, which restated every number. Three ran on the brief
that cites the documents instead and adds the gear strength check. In the first round each model rebuilt the
acceptance test from the brief and checked its own design against it. These ran in Claude Code, headless,
outside Harbor.

**The gap signal is in crown winding.** Workstream A built a winding and hand-setting mechanism (crown, stem,
clutch, ratchet, click) with its own acceptance steps. On that task, run in Harbor:

| Model, harness | Rewards |
| --- | --- |
| GPT-6.1-sol, Codex, first engine | 0.024, 0.022, 0.066 (plus a first smoke run at 0.024) |
| GPT-6.1-sol, Codex, fixed engine (3 repeats regraded) | 0.421, 0.119, 0.110 (mean 0.217): the designs wind, then jam when the rig pre-winds the barrel for the hold test (one clutch that cannot slip; two jams still being traced) |
| Sonnet 5.5, OpenCode | 0.95, every step passing |

These are few runs on a task that is still changing, so they are a signal, not a result. Crown winding joins
this job as Part 5 when A's reference passes in our frame; the grader code for it is in, switched off.

This matches two published findings. CAD-bench (Saini, ICML 2026) reports that agents build a right-angle
gearbox's shape in 96.9 percent of attempts but average 4.0 percent on its functional score. BenchCAD (Zhang et
al., arXiv 2605.10865) reports that models replace sweeps and lofts with simpler extrudes. In our runs too, the
static shape is easy and the moving contact is where models fall short.

All numbers and run logs are in [SESSION.md](SESSION.md) and in the results table of
[solution/SOLUTION_WATCH.md](solution/SOLUTION_WATCH.md).

## How it is scored

The inspection has four parts: going train and hands (weight 0.25), 24-hour hand (0.10), 6-hour variant (0.15)
and assembly (0.25). Each part is a weighted share of pass/fail checks. Nothing gates anything else.

```
R      = 0.5 x (weighted share of the parts) + 0.5 x [everything passes]
reward = R x (0.75 + 0.10 h) / 0.85      h = how well the agent's own report matches the result
```

So a delivery that skips any part scores at most 0.5, and a finished one scores 1.0. A truthful report helps;
a false "pass" costs more than no report. The grader never runs submitted code.

## Running it

Tested on Python 3.13 (the task image uses 3.12).

```bash
pip install -r requirements.txt
```

The reference, as one delivery folder (about 40 s):

```bash
python3 solution/reference_watch.py /tmp/ref --job
```

Grade a delivery folder (absolute path; about 10 minutes):

```bash
cd tests
python3 -I grade_watch.py /tmp/ref --reward /tmp/ref_reward.txt --details /tmp/ref_details.json
```

The anchor suite (each anchor is the reference with one change, and its expected reward), from the repo root:

```bash
python3 tests/test_anchors_job.py 2
```

The Harbor task, with one command (needs Docker and a Harbor 0.26 checkout; see
[harbor/watch_one/README.md](harbor/watch_one/README.md)):

```bash
SKIP_MODEL=1 harbor/watch_one/run_all.sh none 0                         # oracle and do-nothing only
KEY_FILE=~/anthropic.key harbor/watch_one/run_all.sh anthropic/claude-sonnet-5-5 3
AGENT=codex CODEX_FORCE_AUTH_JSON=1 harbor/watch_one/run_all.sh openai/gpt-6.1-sol 3
```

A local headless run in Claude Code, from a folder outside the repo:

```bash
environment/run_clean_job.sh /path/outside/repo/run1 claude-sonnet-5-5
```

## Where things are

| Path | What it is |
| --- | --- |
| `SPEC.md` | the rules, with every number and the file it comes from |
| `environment/public/job/` | what the agent reads: brief, format sheet, datasheets, inspection procedure |
| `environment/make_bundle_job.py` | builds the agent's folder and refuses anything that leaks the solution |
| `tests/grade_watch.py` | the grader |
| `geometry/watch.py` | the constants and the mechanical tests |
| `solution/reference_watch.py` | the reference |
| `solution/SOLUTION_WATCH.md` | answers, margins, anchors, results (never in the agent's image) |
| `solution/STEP_BY_STEP_WATCH.md` | the reference as an expert would build it (never in the agent's image) |
| `tests/test_anchors_job.py` | anchor suite |
| `harbor/watch_one/` | the Harbor task (workstream A) |
| `spikes/keyless/` | crown winding: engine, acceptance steps, datasheets, runs (workstream A) |
| `REAL_WATCH_WORK.md`, `REAL_ML01_FAIRNESS.md` | the task against real watches and a real CAD design |
| `visualizer/` | demo pages: open `index.html` (Replay of Sonnet's staged run) or `xray.html` (X-ray of the watch) in a browser; no server needed. See `visualizer/README.md` |
| `tools/viewer/` | scripts that make the 3D pages |
| `transcripts/` | earlier agent runs with grader output |
| `SESSION.md` | shared log: decisions, requests, every result |

## What we tried before this

Nine task ideas were built and tested over one night: an enclosure design, a packing problem, furniture path
planning, a single-stage watch, an abstract gear train, a five-step watch, a regulation task with hidden
physics, a wrist tracker and a decision game. Every fully specified task with exact feedback was solved at or
near 1.0 by the strongest models, usually in under ten minutes. Details are in `SESSION.md` and
`spikes/README.md`.

Then we built the watch as four frozen stages: design, extend, change, assemble, each a fresh conversation
that inherited the last one's files (SPEC.md 0.6). Fable and Opus scored 1.0 on every stage. Sonnet and one
GPT-6.1-sol chain fell short at assembly, because a part added earlier could not be put in. We moved to one
job with nothing frozen, because a real designer sees the whole order at once. The staged grader is kept to
regrade old runs (`grade_watch.py FOLDER --stage N`).

## Open work

- Part 5 (crown winding) in this job: A's reference in our frame, then the switch on.
- Harbor runs on the submitted job: several per model, including GPT, with reward, part scores, time and cost.
- Stop-early anchors and the full anchor run on the current grader.
- Known strict or loose spots, all logged in `SOLUTION_WATCH.md`: the drive test depends on where in its
  backlash a wheel is delivered; a minute hand drawn as a big disc meets every stated hand rule.

## Team

Four people, each working with a Claude session: itswinther, Mikael, Yoseph and Abhishek. How the sessions stay
in step is in [CLAUDE.md](CLAUDE.md).
