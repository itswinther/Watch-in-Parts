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
  per turn (`REAL_WATCH_WORK.md`, section 1), so our 8-hour and 6-hour builds are both in range.
- The 24-hour hand is driven off the hour wheel through an intermediate wheel, as in the ETA 2893-2 and the
  Miyota 9075.
- The 6-hour variant changes one gear pair on an unchanged frame. ETA's 6497-1 and 6498-1 do the same: one
  frame family, the centre and escape wheels kept.
- Wheels are brass on steel pinions, as Saunier describes.
- The gear load, 70.1 N·mm, is the Sellita SW200-1's bridle slipping torque (16.57 N·mm) scaled to our size
  (`REAL_WATCH_WORK.md`, section 6).

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

**The going-train job is solved by frontier models.** Ten local runs, ten scores of 1.0: Fable 5.2 and Opus 5.5
three each, Sonnet 5.5 four. Six ran on the early brief, which restated every number. Three ran on the brief
that cites the documents instead and adds the gear strength check. The last (Sonnet) ran on the current brief,
with a material per part and the report statement, and wrote a truthful report. In the first round each model
rebuilt the acceptance test from the brief and checked its own design against it. These ran in Claude Code,
headless, outside Harbor. Nobody has run GPT on this job yet.

**A judge rehearsal found three ways to score 1.0 with a watch that does not work** (`JUDGE_REHEARSAL.md`,
section 4): false tooth counts that get a weak pinion past the strength check, a minute hand that hits the
seconds hand once an hour, and a wheel locked by a pawl that still passes "free to turn". With the known
off-centre disc hand, that makes four. None scores above 1.0. The rules that close them are decided and being
built (see "Open work").

**Crown winding is not in the judged job.** Workstream A built a winding and hand-setting mechanism (crown,
stem, clutch, ratchet, click) as its own task, with its own acceptance steps (`spikes/keyless/`). Its grader is
in this job's code but switched off (`KEYLESS_IN_JOB = False`, `geometry/keyless_job.py`), so the judges' job is
Parts 1 to 4. Runs of A's task, in Harbor:

| Model, harness | Engine | Rewards |
| --- | --- | --- |
| GPT-6.1-sol, Codex | first | 0.024, 0.022, 0.066 (plus a first smoke run at 0.024) |
| GPT-6.1-sol, Codex | fixed engine (c44b69b, the same designs regraded) | **0.992** for imWnpTP (every step passes; it was failed twice by engine bugs); b7qdG8X and QZeuFhk have real design faults (a stem that hits its own clutch on pull; a clutch that will not slip backward), regrades stopped. GPT can solve crown winding. |
| Sonnet 5.5, OpenCode | first | 0.95, every step passing |

The rows used different engines, and Sonnet was graded on the first one only. On the fixed engine GPT's
designs wind, then jam when the rig pre-winds the barrel for the hold test. One of those jams is a design fault
(a clutch that cannot slip). A traced the other two to the simulator (the engine skips contact patches below
a size floor, and these contacts were split into many tiny ones), so they are not the model's mistake. A's
engine fix is on a branch, not merged. Until it is in and the designs are regraded, these numbers are not a
gap.

Two published results point the same way: the static shape is easy and the moving contact is hard. CAD-bench
reports that agents build a right-angle gearbox's shape in 96.9 percent of attempts but average 4.0 percent on
its functional score (link and notes: `HARBOR_RESEARCH.md`, section 3.4, and `spikes/RESEARCH_GAPS.md`; we could
not confirm where it was published). BenchCAD (Zhang et al., arXiv 2605.10865) reports that models replace
sweeps and lofts with simpler extrudes. On our job, so far, frontier models get the moving contact right too.

All numbers and run logs are in [SESSION.md](SESSION.md) and in the results table of
[solution/SOLUTION_WATCH.md](solution/SOLUTION_WATCH.md) (section 9).

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

All commands run from the repo root. The reference, as one delivery folder (about 40 s):

```bash
python3 solution/reference_watch.py /tmp/ref --job
```

Grade a delivery folder (absolute path; 4 min 35 s on an idle 4-CPU machine, allow 10):

```bash
(cd tests && python3 -I grade_watch.py /tmp/ref --reward /tmp/ref_reward.txt --details /tmp/ref_details.json)
```

The do-nothing baseline: the same command on an empty folder gives reward 0 (under a second):

```bash
mkdir -p /tmp/empty && (cd tests && python3 -I grade_watch.py /tmp/empty --reward /tmp/empty_reward.txt)
```

Build the folder the agent gets (brief, datasheets, supplied barrel, kernel, format checker, empty
`delivery/`; a few seconds). It refuses any file that leaks the solution:

```bash
python3 environment/make_bundle_job.py /tmp/bundle
```

The anchor suite: each anchor is the reference with one change, and its expected reward. The full suite (36
anchors) takes about 1 h 40 min with 2 workers. The stop-early baseline alone (a delivery stopped after Part 1,
after Parts 1 and 2, and after Parts 1 to 3; expected 0.157, 0.220, 0.333) took 10 min 24 s in our judge
rehearsal:

```bash
python3 tests/test_anchors_job.py 2
python3 tests/test_anchors_job.py 2 --only "job stop-early"
```

The Harbor task, with one command (needs Docker and a Harbor 0.26 checkout; see
[harbor/watch_one/README.md](harbor/watch_one/README.md)):

```bash
SKIP_MODEL=1 harbor/watch_one/run_all.sh none 0                         # oracle and do-nothing only (oracle verifier 3 min 26 s)
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
| `JUDGE_REHEARSAL.md`, `BRIEF_REVIEW.md` | a mock judging of the repo, and a review of everything the agent reads |
| `docs/history/` | handoffs between sessions and the first watch idea write-up, kept for the record |

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

- Grader rules decided and being built, each with an anchor that must score low: a hand may cover at most a
  quarter of the disc its tip sweeps (closes the disc hand); the drive test starts from flank contact (the ml01
  backlash finding, `REAL_ML01_FAIRNESS.md`); "nothing else collides" tested over every pair of angles;
  "free to turn" tested off the 5-degree grid too; declared tooth counts must match the teeth on the part. Then
  a full anchor rerun.
- Regrade our ten saved 1.0 deliveries with those rules.
- Part 5 (crown winding) in this job: A's engine fix merged, A's reference at 1.0 in our frame, then the switch
  on.
- Harbor runs on the submitted job: several per model, including GPT, with reward, part scores, time and cost.
- Known strict or loose spots are logged in `solution/SOLUTION_WATCH.md`, section 8.

## Team

Four people, each working with a Claude session: itswinther, Mikael, Yoseph and Abhishek. How the sessions stay
in step is in [CLAUDE.md](CLAUDE.md).
