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
x      = (H - 3.85) / (13.4 - 3.85), clamped to 0..1      H = total height of the taller build, mm
s      = (1 - x)^4
reward = (1/2 x share + 1/2 x all x s) x (0.75 + 0.10 h) / 0.85
```

- **Thickness.** 3.85 mm (`THIN_REFERENCE_MM`) is the height of the thinnest design of ours that still runs when
  every part is made 0.01 mm larger or smaller than drawn, the size accuracy the process sheet states; 13.4 mm is
  the case height. A build at or below 3.85 mm gets s = 1. At 4.71 mm s = 0.69; at 6 mm s = 0.36. Thickness pays only
  for a watch that fully works. The agent is told only that thinner is better.
- **Statement factor.** h scores `report.json` against the truth, part by part: `pass` on a part that passes
  in full 1, `pass` on one that does not -2, `fail` 0.5 or 1, `not_tested` 0.5; h = max(0, mean over the four
  parts). No report, an invalid one, or a part left out counts as `not_tested`. A working watch with no report
  scores 16/17 = 0.941; with a truthful report, 1.0. A false "pass" costs more than an admitted fault.

## Why thinness, and why it is scored this way

**Why thinness at all.** The order is for a dress watch, and a slim case is what defines one: it has to slide
under a shirt cuff. Watch guides put the whole watch at roughly 6 to 10 mm. The movement sets the floor for
that, so "how thin" is a real question a movement designer is asked, and watchmakers treat thin movements as
an achievement in their own right. Three production calibres show the range:

| Calibre | Diameter | Height | Note |
| --- | --- | --- | --- |
| ETA 2824-2 | 25.6 mm | 4.6 mm | the common automatic |
| ETA 2892-A2 | 25.6 mm | 3.6 mm | same diameter, 1 mm thinner; generally regarded as ETA's higher-grade alternative |
| Peseux / ETA 7001 | 23.3 mm | 2.5 mm | hand-wound |
| Piaget 9P (1957) | 20.5 mm | 2.0 mm | hand-wound; the watches built on it were just over 4 mm thick |

To get there Piaget thinned wheels from the usual 0.2 mm to 0.12 mm, and thin parts distort. That is the
trade the agent faces too: a thinner movement leaves less room for wheels on different levels to pass each
other, for end-shake, for teeth strong enough to carry the barrel, and for a part that can still be printed
(smallest feature 0.2 mm, DS-W03). The barrel catalogue makes it a choice: the thinnest barrel has the
shortest arbor (3.0 mm against 6.6) and the narrowest toothed drum (0.45 mm against 1.0, DS-W01).

Our parts are 1.617 times real size (the order says so). Divided by that, our thinnest design that runs as
made is 3.85 / 1.617 = 2.4 mm, between the 7001 and the Piaget 9P; the GPT deliveries, at 9.6 to 11.8 mm, are
5.9 to 7.3 mm. The comparison is rough: our movement has no escapement and no winding works.

**Why we score it at all.** With a fixed list of requirements, every frontier model we ran met the list and
stopped (SESSION.md, 15 Nov 04:05). Sonnet 5.5, on a brief with a 9.0 mm target, delivered 8.10 mm and wrote: "below the 9.0 mm target, so the
thickness score should be 1. I did not try to go thinner." Meeting a specification and designing well are different things, and thickness is the one quantity
in this job where better has no stated end.

**Why this formula.**

- *Only for a watch that fully works.* A thin watch that does not run is worth nothing to the customer, so
  thickness scales only the all-pass half of the reward. Making a broken watch thinner earns nothing.
- *Measured, not declared.* H is taken from the delivered solids, barrel included. `height_mm` in the report
  is recorded and ignored.
- *Against a design we can show.* Full score is at 3.85 mm, the thinnest design of ours that still runs with
  every part 0.01 mm larger or smaller than drawn (the accuracy DS-W03 states). Nothing is asked of the agent
  that we have not built. Thinner than that earns no more.
- *Zero at the case.* The scale ends at 13.4 mm, the inner height of the case in the order: a movement that
  fills the case has made no attempt.
- *The fourth power.* s = (1 - x)^4 falls fastest near the bar: 1 mm over costs about a third of the thickness
  score, 2 mm over about 60 %. In real calibres a millimetre is the whole difference between the 2824-2 and
  the 2892-A2.
- *No number in the order.* When we printed a target, models aimed at it and stopped. The order says what a
  customer would say: as thin as you can.

Sources for the watch figures: Caliber Corner (ETA 2892-A2, ETA 7001), Time+Tide and Monochrome (2824-2
against 2892-A2), Mr Porter, "Chasing Two Millimetres" (Piaget 9P), Deployant and Swisswatches Magazine (dress
watch).

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
- Baselines in Harbor on the submitted grader (`3d5d96f`): oracle (our reference, built in the container)
  1.000, nop 0.000, both marked valid by Harbor (SESSION.md, A 05:49). Outside Harbor an empty delivery folder
  grades 0.000000.
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

**Sonnet 5.5 under OpenCode.** The task image lets one reply use the model's full output limit
(`OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=128000`, set in `harbor/watch_one/build_task.py`; an earlier image
capped it at 64,000). At that limit Sonnet 5.5, at default and at medium thinking, ended in a single reply of
128,000 thinking tokens with nothing delivered, in four runs of four (SESSION.md, A 06:20). It read the order,
the sheets and `kernel.py`, then tried to plan the whole movement in one reply and never wrote a script. No
tool failed. We report these runs separately and do not count them in the gap.

Without Harbor (Python 3.12 or 3.13, `pip install -r requirements.txt`, from the repo root):

```bash
python3 solution/reference_watch.py /tmp/ref --job                     # the reference delivery, about 40 s
(cd tests && python3 -I grade_watch.py /tmp/ref --reward /tmp/r.txt --details /tmp/d.json)
mkdir -p /tmp/empty && (cd tests && python3 -I grade_watch.py /tmp/empty --reward /tmp/e.txt)   # reward 0
python3 environment/make_bundle_job.py /tmp/bundle                     # the agent's /app
python3 environment/make_brief_job.py --check                          # documents agree with the constants
python3 tests/test_anchors_job.py 3 --only "job stop-early"            # stop-early baselines: 0.157, 0.220, 0.333
```

Grading the reference takes a few minutes (188 s in the Harbor oracle run; about 8 min on a busy 4-core machine).

## Results

Every number here is from the submitted task: agent image `4c5d8d3`, grader `3d5d96f` (same agent files; the
grader adds the thickness term). Runs are in Harbor, sandboxed, web tools denied. Deliveries and grader details
are on branch `a/final-runs`, under `runs/final_4c5d8d3/`.

| Agent | Runs | Reward | Notes |
| --- | --- | --- | --- |
| Oracle (our reference) | 1 | 1.000 | H 3.35 mm, built in the container in 37 s |
| nop (does nothing) | 1 | 0.000 | |
| GPT-6.1-sol (Codex) | 3 | 0.457, 0.447, 0.427 (mean 0.444) | no run delivers a watch that fully works |
| Sonnet 5.5 (OpenCode) | 0 valid | | see below |
| Opus 5.5 (OpenCode) | 0 valid | | see below |
| Fable 5.2 | not run yet | | |

The three GPT-6.1-sol runs, check by check:

| Run | Reward | Share of checks | Height H | What fails |
| --- | --- | --- | --- | --- |
| `dQKXa6k` | 0.457 | 0.956 | 9.60 mm | `held` in P1 and P3: one mobile can be pushed sideways out of place |
| `fhhWYjp` | 0.447 | 0.934 | 11.80 mm | `seated` and `clear` in P1 and P3: a wheel is not seated on its arbor; the minute and seconds mobiles overlap as they turn (0.0106 mm3 against a limit of 0.01) |
| `oVS4tLK` | 0.427 | 0.894 | 11.15 mm | `held` and `clear` in P1 and P3: the seconds mobile can drop out downwards, minute and seconds overlap (0.034 mm3). `day_place` in P2 and P3: the 24-hour hand lies 0.4 mm below the top of the frame |

How to read these:

- **The reward is below one half because the watch does not work, not because half of it is missing.** Each
  run passes 89 to 96 % of the weighted checks, and the assembly plan (P4) passes in all three. Half of the
  reward is paid only when every check of every part passes, and none of the three reaches that.
- **Thickness did not change these three scores**, because it only applies to a watch that fully works. Had
  the faults been fixed at the delivered heights, the thickness scores would be 0.025, 0.0008 and 0.003: the
  watches are 9.6 to 11.8 mm against 3.85 mm. The order says "as thin as you can".
- **The model said so itself.** All three reports state P1 to P3 `not_tested` and P4 `pass`. That is truthful,
  and costs 3/68 of the reward.
- **It stopped early.** The three agents ran for 810 to 2,036 s (14 to 34 minutes) of a 10,800 s limit.
- One of the faults is marginal: the 0.0106 mm3 overlap in `fhhWYjp`. That run also fails `seated`, so its
  score does not depend on it.

These three rewards were graded three times with grader `3d5d96f`: in Harbor's verifier, again in Docker by
workstream A (SESSION.md, A 05:48), and a third time on another machine outside Harbor from the files on
`a/final-runs`. All three gave the same rewards to six decimals and the same failed checks.

**Claude models: no scored watch yet.** Sonnet 5.5 at default and medium thinking delivered nothing in four
runs of four (see "How to run it"). Earlier Sonnet runs and one Opus 5.5 run ended when our API credit ran out;
Harbor marks those invalid (SESSION.md, A 05:46). Sonnet at low thinking, Opus and three more GPT runs are in
progress and this table will be updated.

Earlier briefs, for context only:

- On the briefs that stated the acceptance test (four-part job), ten of ten local runs in Claude Code, outside
  Harbor, scored 1.0 (Fable 5.2 and Opus 5.5 three each, Sonnet 5.5 four). With a stated 9.0 mm thickness
  target, GPT, Opus and Sonnet all scored 1.000 (SESSION.md 04:05).
- Round 2 (4.0 mm target stated, thin barrel, 12.7 mm case; `b/thin-4mm` 92d9622): GPT-6.1-sol scored 0.354 in
  one run. H was 4.71 mm; P1 and P3 failed train, seconds, tolerant and strength; it claimed all four parts pass
  (SESSION.md, A 04:31).

All runs and logs are in [SESSION.md](SESSION.md).

## The judging rubric, and our answer to each point

The rubric text is the organisers', quoted in full. Under each we say what we show, with where to check it, and
what we do not show.

### The gap (30 p)

> Full points: the frontier agent consistently scores below a stronger reference run your team demonstrates;
> both results can be reproduced across repeated runs. Zero points: no measurable gap, or the claimed gap
> cannot be reproduced or checked against a demonstrated reference run.

- **Reference run:** `solution/reference_watch.py`, replayed by Harbor's oracle agent inside the container:
  reward 1.000 (SESSION.md, A 05:49). It is a script, so it gives the same delivery every time.
- **Frontier agent:** GPT-6.1-sol, three Harbor runs: 0.457, 0.447, 0.427. All three are below one half; the
  spread is 0.03.
- **Checkable:** the three deliveries and the grader's details files are on branch `a/final-runs`. Anyone can
  regrade them with the four shell lines under "How to run it".
- **Not shown:** a valid run of a Claude model on the submitted task, and more than three runs.

### Meaningful difficulty (30 p)

> Full points: you can explain the agent's main mistakes and connect them to decisions in the task; the
> information and tools needed to do better are available to it. Zero points: the gap comes from unfairly
> withheld information, trick wording, impossible timing, or broken tools.

- **The mistakes, by name** (table under Results): a mobile that is not held in place (two runs), mobiles that
  overlap as they turn (two runs), a wheel not seated on its arbor (one run), a 24-hour hand below the top of
  the frame (one run). Each is a measured fault in the delivered parts, in the details file.
- **The decisions behind them:**
  - The agent decided when it was done. It stopped after 14 to 34 minutes of 3 hours.
  - It decided not to test its own watch. All three reports say P1 to P3 `not_tested`.
  - It decided how thin to go. All three are 9.6 to 11.8 mm in a case that allows 13.4 mm; our designs are
    3.35 and 3.85 mm.
- **Information and tools available:** the order, seven supplier sheets, the file format, CadQuery, and
  `tools/kernel.py` with the factory's own STEP loader, intersection volume and smallest distance. These are
  enough to test "held", "overlap while turning" and "hand above the frame" before delivering. The reference
  is built with the same CadQuery; its involute gear maker (`geometry/watch_gears_cad.py`) is our own code and is
  not given to the agent, which has to write its own.
- **Withheld information:** the agent is not shown the acceptance test. Every check traces to the order, a
  sheet, the format or trade practice ([docs/CHECK_BASIS.md](docs/CHECK_BASIS.md)). Three grader numbers do
  not (known limits); none of the faults above depends on them.
- **Timing:** no run came near the 3-hour limit.
- **Broken tools:** none that we know of. Sonnet 5.5 delivers nothing under OpenCode because it spends a whole
  reply, at its full output limit, on thinking ("How to run it"). No tool fails in those runs, but we do not
  count them in the gap either: the gap we claim is from runs that delivered a complete watch.
- **Not done:** a trace of each fault through the agent's transcript to the step where it was introduced.

### Reward integrity (25 p)

> Full points: the reward measures success at the task and holds up when judges try to exploit it; doing
> nothing or stopping early earns little or no credit; completing the task well remains the best way to score.
> Zero points: an exploit, scoring loophole, or strategy that avoids the task earns a better score than
> successful play.

- **Doing nothing:** 0.000 in Harbor (nop agent); an empty delivery folder grades 0.000000 outside Harbor.
- **Stopping early:** three stop-early deliveries, each the reference cut off after its first parts, graded on
  the submitted grader: Part 1 only 0.157; Parts 1 and 2: 0.220; Parts 1 to 3 without an assembly plan, with a
  truthful report: 0.333. Command: `python3 tests/test_anchors_job.py 3 --only "job stop-early"` (3 of 3 as
  expected, about 6 minutes). A flawless three quarters of the job earns one third.
- **Completing the task well is the best way to score:** half of the reward is paid only when every check of
  every part passes, and that half is scaled by thickness. A partial delivery cannot pass one half.
- **Measures success at the task:** the checks are geometric tests of the delivered solids: nothing overlaps,
  every mobile turns and is held, every mesh drives, the hands turn at the right speeds, every part can be put
  in along its stated path.
- **Against exploits:** the verifier is a separate offline container; it reads only the files the delivery
  names, refuses links and outside paths, and never runs submitted code. Reward 0 is written first. Each check
  has its own try block and time limit. The report can only lower the reward: a truthful one leaves it as it
  is, a false `pass` costs more than an admitted fault.
- **Not done on the submitted version:** the full anchor suite (`tests/test_anchors_job.py`, the reference with
  one fault each and the expected reward) has not been re-run since the layout became thin, and one anchor is
  known to be out of date. No exploit hunt was run against this version. Earlier hunts are in
  `docs/history/`.

### Craft (15 p)

> Full points: the environment's rules and behavior make sense for the setting; judges can run the evaluation
> from your README with one command and reproduce your reported results. Zero points: the environment only
> works in your demo, or judges cannot reproduce the evaluation.

- **Makes sense for the setting:** the task is a movement designer's job from a customer order and supplier
  sheets, and its numbers come from real calibres ("Why it is hard, and why that is fair").
- **One command:** `harbor/watch_one/run_all.sh MODEL K` builds the task and runs oracle, nop and the model.
- **Reproduce:** oracle 1.000 and nop 0.000 were reproduced in Harbor on the submitted grader; the GPT
  deliveries can be regraded from `a/final-runs`.
- **Rules in one place:** `SPEC.md` names the constant and file behind every number.
- **Not done:** a run of the README from a clean clone by someone who did not write it.

### Tiebreaker: a smaller model that improves after training

Not done.

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
  at 3.85 mm and does not reward going further.
- **The reference delivery is thinner than the bar, and would not run as printed.** `solution/` builds a 3.35 mm
  design. It passes every check of the grader, but with parts grown by the stated 0.01 mm one gear pair jams
  (`spikes/asmade/asmade.py --tol 0.01`). So full thickness score is set at 3.85 mm, the height of our design that
  does run as made. That design needs a case radius of 12.766 mm, 0.066 mm more than the 12.7 mm case the agent is
  given; we have not found one that fits. The as-made test itself is not part of the score.

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
