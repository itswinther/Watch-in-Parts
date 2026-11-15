# Watch movement design job

An RL environment for the AfterQuery challenge at Junction 2026, in Harbor format. The agent gets a customer
order for a thin dress watch and a folder of supplier sheets. It designs the movement as CAD parts (STEP, made
with CadQuery) and delivers one folder. A separate offline verifier grades that folder by geometry. The agent
never sees a check, a score or a verdict.

The repo is still named `board-in-a-box` after our first idea, which we dropped.

## What the agent gets and what it must deliver

The instruction is [environment/public/job/PROMPT.md](environment/public/job/PROMPT.md), written as a customer
order. It asks for:

- a movement with four hands: hours and minutes on the centre, seconds, and a 24-hour hand on its own small dial;
- a barrel chosen by the agent from the catalogue DS-W01 (three barrels with arbors 3.0, 4.5 and 6.6 mm long);
- case CS-254-134 (inner radius 12.7 mm, inner height 13.4 mm, DS-W02);
- parts printed by the process of DS-W03 (smallest feature 0.2 mm), each mobile in brass or steel;
- two builds on the same frame: `movement.json` with the barrel at one turn per 8 hours, and `variant_6h.json`
  with the same barrel at one turn per 6 hours;
- an assembly plan, `assembly.json`: an order and a path of rigid poses for every part of the 8-hour build;
- optionally `report.json`: the designer's statement, for each of four items, `pass`, `fail` or `not_tested`;
- "as thin as you can": no number is given.

There is no acceptance test, no target height and no stated formula in anything the agent reads.

The agent's `/app`, built by `environment/make_bundle_job.py`:

| Path | What it is |
| --- | --- |
| `instruction.md` | the order (from `PROMPT.md`) |
| `FORMAT.md` | file formats, size limits, JSON layouts, how the factory reads the files |
| `datasheets/` | DS-W01 barrels, DS-W02 cases, DS-W03 printing, DS-W04 gear rating, DS-101 mainsprings, DS-201 materials, DS-301 jewels, `INDEX.md` |
| `supplied/BR-096-30.stl`, `BR-096-45.stl`, `BR-096-66.stl` | each catalogue barrel as a mesh |
| `tools/kernel.py` | geometry helpers, including the STEP loader the grader uses |
| `tools/check_format.py` | checks file format only, prints `format ok` or the format errors |
| `delivery/` | empty; the agent writes here |

Installed: Python 3.12, CadQuery 2.8.0, manifold3d, trimesh, numpy, scipy.

## How it is graded

`tests/grade_watch.py`, one-job mode. The full rules are in [SPEC.md](SPEC.md) (version 0.8).

| Part | What | Weight | Gates |
| --- | --- | --- | --- |
| P1 | 8-hour build: frame, going train, hour, minute and seconds hands | 25 | files load; parts do not overlap |
| P2 | the 24-hour hand of the 8-hour build | 10 | as P1, plus a 24-hour hand declared |
| P3 | the 6-hour variant: every P1 and P2 check again | 15 | as P2, plus the same frame as the 8-hour build |
| P4 | assembly: each part of the 8-hour build goes in along its path | 25 | movement.json loads; assembly.json is valid |

P1 has 14 weighted checks: every mobile turns freely and is held; multi-part mobiles are one piece; every mesh
drives, also with the driven axis moved 0.03 mm; no undeclared pair of mobiles ever touches; the hands turn at
1/12, 1 and 60 turns per hour, clockwise; hour and minute are coaxial; hands are at least 5 mm long and lie
above the frame; everything fits the case; every part passes the print test; the going train passes a Lewis
bending check under 70.1 N·mm at the barrel. P4 scores the share of parts installed. A part whose gates fail
scores 0; no part gates another.

The reward:

```
share  = sum(w_p x s_p) / sum(w_p)          s_p = weighted share of part p's checks that pass (0 if a gate fails)
all    = 1 if every gate and check of every part passes, else 0
x      = (H - 3.35) / (13.4 - 3.35), clamped to 0..1      H = total height of the taller build, mm
s      = (1 - x)^4
reward = (1/2 x share + 1/2 x all x s) x (0.75 + 0.10 h) / 0.85
```

- **Thickness.** 3.35 mm (`THIN_REFERENCE_MM`) is the height our own house design reaches; 13.4 mm is the case
  height. A build at or below 3.35 mm gets s = 1. At 4.71 mm s = 0.56; at 6 mm s = 0.29. Thickness pays only
  for a watch that fully works. The agent is told only that thinner is better.
- **Statement factor.** h scores `report.json` against the truth, part by part: `pass` on a part that passes
  in full 1, `pass` on one that does not -2, `fail` 0.5 or 1, `not_tested` 0.5; h = max(0, mean over the four
  parts). No report, an invalid one, or a part left out counts as `not_tested`. A working watch with no report
  scores 16/17 = 0.941; with a truthful report, 1.0. A false "pass" costs more than an admitted fault.

## Why it is hard, and why that is fair

On an earlier brief that printed the acceptance test and a 4.0 mm thickness target, every frontier model we ran
scored 1.0: they rebuilt the stated checks as a self-test and stopped when it passed (SESSION.md, 15 Nov
04:05). So the submitted brief states no test and no target. The agent has to know what a working movement is,
check its own design, and decide how thin it can go.

Every check must trace to one of four sources: the order, a supplier sheet, the file format, or ordinary trade
practice (a wheel turns freely, two parts do not occupy one space, a hand is a pointer). The table, check by
check, is [docs/CHECK_BASIS.md](docs/CHECK_BASIS.md). Where a check had no basis, we added the fact to the order
or to `FORMAT.md` (for example the dial layout and hand lengths, the dial side, the drawing convention), or we
list it under known limits below.

The task is grounded in real watches (`REAL_WATCH_WORK.md`):

- Barrel to centre is 8, as in Grossmann's textbook train. Real barrels run 6.3 to 8 hours per turn, so the
  8-hour and 6-hour builds are both in range.
- The 24-hour hand is driven off the hour wheel through an intermediate wheel, as in the ETA 2893-2 and the
  Miyota 9075.
- The 6-hour variant changes one gear pair on an unchanged frame, as ETA's 6497-1 and 6498-1 share one frame.
- Wheels are brass on steel pinions, as Saunier describes.
- The gear load, 70.1 N·mm, is the Sellita SW200-1's bridle slipping torque (16.57 N·mm) scaled to our size
  (DS-101 Table 2a). The order says the train is shared with an automatic version and must carry its barrel.
- The catalogue barrels turn clockwise seen from the dial. Most real calibres mesh the barrel straight onto the
  centre pinion, so the minute hand would run backwards here; the train needs one extra wheel. Marco Lang's
  ml01 has that wheel, and so does US patent 7,452,123.

We also ran Marco Lang's ml01 going train, from his public CAD file, through an earlier version of our checks
(`REAL_ML01_FAIRNESS.md`).

## Reward integrity

- The verifier runs in Harbor's separate environment with no network. It holds the grader and `geometry/`;
  the agent image holds neither.
- It reads only the delivered files that `movement.json`, `variant_6h.json` and `assembly.json` name, plus
  `report.json`. Symbolic links and paths outside the delivery are refused. It never runs submitted code;
  `scripts/` is archived, never opened.
- `tests/test.sh` writes reward 0 first; the grader writes 0 again and overwrites it once at the end. Each gate
  and check runs in its own try block with its own time limit (1,800 s each, 7,200 s in all); an exception or a
  timeout fails that check only.
- Baselines in Harbor on `g/final` 4c5d8d3: oracle (our reference, built in the container) 1.000, nop 0.000
  (SESSION.md, A 04:48). That run was before the thickness term was added. The reference is at H0, so it
  should stay 1.0; this is to be re-run.
- Leak guard: `make_bundle_job.py` refuses any file name, mark, phrase or number that would point at the
  solution, including the house design's height and the thickness formula. `harbor/watch_one/build_task.py`
  admits only an allowlist of paths into the agent image and refuses copies of secret files by sha256.
- The agent's network is an allowlist of model endpoints only; web tools are denied.

## How to run it

The Harbor task, with one command. Needs Docker, `uv` and a Harbor 0.26 checkout (`HARBOR_SRC`); details in
[harbor/watch_one/README.md](harbor/watch_one/README.md).

```bash
SKIP_MODEL=1 harbor/watch_one/run_all.sh none 0                        # oracle and nop only, no key
KEY_FILE=~/anthropic.key harbor/watch_one/run_all.sh anthropic/claude-opus-5-5 3
AGENT=codex CODEX_FORCE_AUTH_JSON=1 harbor/watch_one/run_all.sh openai/gpt-6.1-sol 3
```

It builds the task, checks the network settings, runs `harbor lint`, the oracle, nop and the model (OpenCode by
default, agent cap 3 h), and summarises the results.

Without Harbor (Python 3.12 or 3.13, `pip install -r requirements.txt`, from the repo root):

```bash
python3 solution/reference_watch.py /tmp/ref --job                     # the reference delivery, about 40 s
(cd tests && python3 -I grade_watch.py /tmp/ref --reward /tmp/r.txt --details /tmp/d.json)
mkdir -p /tmp/empty && (cd tests && python3 -I grade_watch.py /tmp/empty --reward /tmp/e.txt)   # reward 0
python3 environment/make_bundle_job.py /tmp/bundle                     # the agent's /app
python3 environment/make_brief_job.py --check                          # documents agree with the constants
python3 tests/test_anchors_job.py 2 --only "job stop-early"            # stop-early anchors
```

Grading the reference takes a few minutes (153 s in the Harbor oracle run).

## Results

Final brief (`g/final` 4c5d8d3 agent image), Harbor, OpenCode or Codex, graded with the thickness term.

| Model | Runs | Rewards | Height H (mm) | Notes |
| --- | --- | --- | --- | --- |
| Oracle (reference) | 1 | pending re-run (1.000 before the thickness term) | 3.35 | |
| nop | 1 | pending re-run (0.000 before the thickness term) | | |
| Sonnet 5.5 | 3 | pending | pending | |
| Opus 5.5 | pending | pending | pending | |
| Fable 5.2 | pending | pending | pending | |
| GPT-6.1-sol | pending | pending | pending | |

Earlier briefs, for context only:

- On the briefs that stated the acceptance test (four-part job), ten of ten local runs in Claude Code, outside
  Harbor, scored 1.0 (Fable 5.2 and Opus 5.5 three each, Sonnet 5.5 four). With a stated 9.0 mm thickness target, GPT, Opus and Sonnet all scored 1.000 (SESSION.md 04:05).
- Round 2 (4.0 mm target stated, thin barrel, 12.7 mm case; `b/thin-4mm` 92d9622): GPT-6.1-sol scored 0.354 in
  one run. H was 4.71 mm; P1 and P3 failed train, seconds, tolerant and strength; it claimed all four parts pass
  (SESSION.md, A 04:31).

All runs and logs are in [SESSION.md](SESSION.md).

## Known limits

- **One task instance.** One order, one case, one catalogue.
- **Three grader numbers the agent cannot derive.** The tooth load factor 1.45 (dry meshing), the material
  allowables (brass 110 MPa, steel 725 MPa, proof stress / 2) and the 0.03 mm shift of the `tolerant` check
  are in the grader but in no agent document. `docs/CHECK_BASIS.md` marks them OT: to be replaced by a test of
  the movement as made. That replacement is not built.
- **The as-made test is not in the score.** A test of the watch as printed, within DS-W03's +/- 0.01 mm, exists
  (`geometry/asmade.py`, `spikes/asmade/asmade.py`; in the grader only with `WATCH_AS_MADE=1`, which the
  Harbor task does not set). Its results are reported beside the score, not in it.
- **Crown winding is not in the task.** Workstream A built a winding and hand-setting part (`spikes/keyless/`)
  and the grader can include it as Part 5, but it is switched off (`geometry/keyless_job.py`,
  `KEYLESS_IN_JOB = False`); it does not fit the thin layout.
- **Thickness is scored against our own design.** If a better design than ours is possible, the scale tops out
  at 3.35 mm and does not reward going further.

## Where things are

| Path | What it is |
| --- | --- |
| `SPEC.md` | the rules, with every number and the constant it comes from |
| `docs/CHECK_BASIS.md` | the basis of every check |
| `environment/public/job/` | what the agent reads: order, format sheet, datasheets |
| `environment/make_bundle_job.py` | builds the agent's folder and refuses anything that leaks the solution |
| `tests/grade_watch.py` | the grader |
| `geometry/watch.py` | the constants and the mechanical tests |
| `solution/reference_watch.py` | the reference (house design) |
| `tests/test_anchors_job.py` | anchor suite: the reference with one change each, and its expected reward |
| `harbor/watch_one/` | the Harbor task |
| `REAL_WATCH_WORK.md`, `REAL_ML01_FAIRNESS.md` | the task against real watches and a real CAD design |
| `visualizer/` | demo pages, open `index.html` or `xray.html` in a browser |
| `SESSION.md` | shared log of the four sessions: decisions, requests, every result |

## History

Before this task we built and dropped nine others, including Board in a Box (an enclosure design), because
clean agents scored at or near 1.0 (`spikes/README.md`, `SESSION.md`). The first watch version was four frozen
stages (SPEC 0.6), where Fable and Opus scored 1.0 on every stage; its grader mode is kept to regrade old runs
(`grade_watch.py FOLDER --stage N`). SPEC 0.7 made it one job with a stated acceptance test (QA-W100); every
frontier model scored 1.0. SPEC 0.8 is the customer order described above. Earlier write-ups are in
`docs/history/`.

## Team

Four people, each working with a Claude session: itswinther, Mikael, Yoseph and Abhishek. How the sessions stay
in step is in [CLAUDE.md](CLAUDE.md).
