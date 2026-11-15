# Watch in Parts

Watch in Parts is an RL environment for the AfterQuery challenge at Junction 2026, in Harbor format. The agent gets a customer
order for a thin dress watch and a folder of supplier sheets. It designs the movement as CAD parts (STEP, made
with CadQuery) and delivers one folder. A separate offline verifier grades that folder by geometry. The agent
never sees a check, a score or a verdict.

**In one minute**

- **The task:** design a thin dress-watch movement from a customer order: gear train, four hands, a 6-hour
  variant on the same frame, and an assembly plan. One job, start to finish, about 20 CAD parts.
- **The reference:** our own design, built by one script: reward **1.000** (Harbor oracle, in Docker and on
  Modal).
- **The frontier agent:** GPT-6.1-sol, six runs: **0.427 to 0.467**, mean 0.447. Every run delivers a complete
  movement that does not fully work, 2.5 to 3.1 times the height of our 3.85 mm design, and says itself that it
  did not test it.
- **Baselines:** do nothing **0.000**; stop early **0.157, 0.220, 0.333**.
- **Run it:** `harbor run -p task -a oracle`, then `-a nop`, then `-a opencode -m <provider/model>`.
- **The strongest runs we have:** Opus 5.5 delivered a fully working movement twice, every check passed and the
  report honest: **0.925** (medium thinking, 4.23 mm) and **0.811** (low thinking, on Modal, 4.92 mm). Both lose
  score on thickness alone, against our 3.85 mm. So the task can be done from what the agent is given, and the
  best agent is still below the reference.
- **Other Claude runs:** Sonnet 5.5 and Opus 5.5 at low thinking, one valid run each, both 0.422.
- **What we do not show:** repeated Claude runs, and some grader thresholds the agent is not told. Both are
  spelled out below, with the ten things we would change next.

The project is called Watch in Parts. Its working name was `board-in-a-box`, after our first idea, which we
dropped; a few file headers and old notes still carry that name.

**Where to look first**

| You want | Go to |
| --- | --- |
| The task, ready for `harbor run` | [`task/`](task/) |
| What the agent is told | [`task/instruction.md`](task/instruction.md) |
| The rules and every number | [`SPEC.md`](SPEC.md) |
| The grader | [`tests/grade_watch.py`](tests/grade_watch.py) |
| The reference solution, and the job step by step | [`solution/reference_watch.py`](solution/reference_watch.py), [`solution/STEP_BY_STEP_WATCH.md`](solution/STEP_BY_STEP_WATCH.md) |
| Results and the rubric, point by point | below, "Results" and "The judging rubric" |
| Everything else | "Where things are", at the end |

Folders that are not part of the submitted task: `spikes/` (experiments), `holdtheline/` (a dropped idea),
`transcripts/` and `docs/history/` (earlier versions), `docs/research/` (our notes on real watches, standards
and the harness).

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

The task is grounded in real watches (`docs/research/REAL_WATCH_WORK.md`):

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
(`docs/research/REAL_ML01_FAIRNESS.md`).

## Reward integrity

- The verifier runs in Harbor's separate environment with no network. It holds the grader and `geometry/`;
  the agent image holds neither.
- It reads only the delivered files that `movement.json`, `variant_6h.json` and `assembly.json` name, plus
  `report.json`. Symbolic links and paths outside the delivery are refused. It never runs submitted code;
  `scripts/` is archived, never opened.
- `tests/test.sh` writes reward 0 first; the grader writes 0 again and overwrites it once at the end. Each gate
  and check runs in its own try block with its own time limit (1,800 s each, 7,200 s in all); an exception or a
  timeout fails that check only.
- Baselines in Harbor, twice. On Modal sandboxes, from the checked-in `task/` with the grader on `main`
  (Harbor 0.26, 15 Nov, about 08:25): oracle 1.000 in 4 min 15 s, nop 0.000 in 3 min 11 s, no exceptions. The job folders are on
  branch `modal-runs` (`jobs-modal/`); the oracle's details file there shows H 3.349 mm against the 3.85 mm bar,
  thickness score 1, verifier time 169 s. In local
  Docker on grader `3d5d96f`: oracle 1.000, nop 0.000 (SESSION.md, A 05:49). Outside Harbor an empty delivery
  folder grades 0.000000.
- Leak guard: `make_bundle_job.py` refuses any file name, mark, phrase or number that would point at the
  solution, including the house design's height and the thickness formula. `harbor/watch_one/build_task.py`
  admits only an allowlist of paths into the agent image and refuses copies of secret files by sha256.
- The agent's network is an allowlist of model endpoints only; web tools are denied.

## How to run it

The task is a plain Harbor task, checked in at [`task/`](task/): `instruction.md`, `task.toml`,
`environment/` (Dockerfile and the agent's `/app`), `tests/` (the verifier) and `solution/` (the reference,
replayed by the oracle agent). With Harbor 0.26 or later installed:

```bash
harbor run -p task -a oracle                                           # the reference: 1.0
harbor run -p task -a nop                                              # do nothing: 0.0
harbor run -p task -a opencode -m <provider/model> -k 3 --ak disable_web_search=true
```

On Modal sandboxes, the same three steps with one command (it checks the Harbor version, the Modal login and
the model key first, and prints each trial's reward):

```bash
uv tool install 'harbor[modal]' && modal token new                     # once
harbor/watch_one/run_modal.sh                                          # oracle and nop
OPENAI_API_KEY=... harbor/watch_one/run_modal.sh openai/gpt-6.1-sol 3  # then a model, 3 runs
```

**Any model provider works.** `task.toml` limits the agent's network to an allowlist, because this repo is
public and an open network would let the agent download the reference. The list names Anthropic, OpenAI,
Google and OpenRouter. For any other provider, Harbor 0.26 adds the model's own endpoint to the allowlist by
itself when it starts the agent (it logs "Allowlisting inference host ..."). If it cannot work the endpoint out,
it says so, and one flag adds it: `--allow-agent-host <hostname>`. The verifier stays offline either way.

On Windows, run the three `harbor run` lines above with `-e modal` from PowerShell (the `.sh` runners need
bash); use a clone that has `.gitattributes` (commit `fca7fe9` or later), which keeps the shell scripts in LF.

`task/` is generated, not hand-written: `harbor/watch_one/build_task.py` writes it from the sources in this repo
(`environment/`, `geometry/`, `tests/`, `solution/`) and refuses anything that would leak the solution into the
agent's image. To rebuild it and run everything with one command (needs Docker, `uv` and a Harbor checkout in
`HARBOR_SRC`; details in [harbor/watch_one/README.md](harbor/watch_one/README.md)):

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

Every number here is from the submitted task. The agent's files are those of commit `4c5d8d3` in every run;
the rewards are from the grader on `main`. Runs are in Harbor, sandboxed, web tools denied. Deliveries and
grader details are on branch `a/final-runs`, under `runs/final_4c5d8d3/` and `runs/final_3d5d96f/`.

| Agent | Runs | Reward | Notes |
| --- | --- | --- | --- |
| Oracle (our reference) | 2 | 1.000, 1.000 | H 3.35 mm; once in local Docker, once on Modal |
| nop (does nothing) | 2 | 0.000, 0.000 | once in local Docker, once on Modal |
| Stop-early (three cut-off deliveries) | 3 | 0.157, 0.220, 0.333 | Part 1 only; Parts 1 and 2; Parts 1 to 3 |
| GPT-6.1-sol (Codex) | 6 | 0.457, 0.447, 0.427, 0.467, 0.458, 0.427 (mean 0.447) | no run delivers a watch that fully works |
| Sonnet 5.5, low thinking (OpenCode) | 1 valid | 0.422 | 5.75 mm; three mobiles not held; see below |
| Opus 5.5, low thinking (OpenCode) | 1 valid | 0.422 (0.082 when regraded on another machine) | 4.08 mm; see below |
| Opus 5.5, medium thinking (OpenCode) | 1 valid | **0.925** | 4.23 mm; every check passes; see below |
| Opus 5.5, low thinking (OpenCode, on Modal) | 1 valid so far | **0.811** | 4.92 mm; every check passes; two more trials were still running at 09:25 |
| Fable 5.2 | not run | | |

The six GPT-6.1-sol runs, check by check:

| Run | Reward | Share of checks | Height H | What fails |
| --- | --- | --- | --- | --- |
| `dQKXa6k` | 0.457 | 0.956 | 9.60 mm | `held` in P1 and P3: one mobile is stopped sideways by 0.006 mm3 of contact, under the 0.01 limit (0.037 in the other directions) |
| `fhhWYjp` | 0.447 | 0.934 | 11.80 mm | `seated` and `clear` in P1 and P3: a wheel is not seated on its arbor; the minute and seconds mobiles overlap as they turn (0.0106 mm3 against a limit of 0.01) |
| `oVS4tLK` | 0.427 | 0.894 | 11.15 mm | `held` and `clear` in P1 and P3: nothing stops the seconds mobile dropping out downwards; minute and seconds overlap (0.034 mm3). `day_place` in P2 and P3: the 24-hour hand lies 0.4 mm below the top of the frame |
| `UVsdmwL` | 0.467 | 0.978 | 12.10 mm | `clear` in P1 and P3: the minute and seconds mobiles overlap as they turn (0.088 mm3) |
| `k843CBe` | 0.458 | 0.959 | 11.95 mm | `day_place` in P2 and P3: the 24-hour hand's centre of volume is 0.41 mm from its axis; the grader asks 0.5 (a threshold of ours, see known limits) |
| `owFDECg` | 0.427 | 0.894 | 10.05 mm | `hands` and `seated` in P1 and P3: the hour and seconds hands lie 0.25 and 0.6 mm below the top of the frame; four wheels are not seated. `day_place`: the 24-hour hand lies 0.6 mm below the top of the frame |

**A grader fault we found in these runs and fixed.** `k843CBe` first also failed `hands`: its seconds hand, drawn
at exactly the ordered 5.000 mm, measured 4.99994 mm on our mesh. The check had no allowance for our own
meshing accuracy (0.001 mm, `FORMAT.md`). It has one now. That run went from 0.448 to 0.458; no other run and
no other check changed.

How to read these:

- **The reward is below one half because the watch does not work, not because half of it is missing.** Each
  run passes 89 to 98 % of the weighted checks, and the assembly plan (P4) passes in all six. Half of the
  reward is paid only when every check of every part passes, and none of the six reaches that.
- **Thickness did not change these six scores**, because it only applies to a watch that fully works. Had
  the faults been fixed at the delivered heights, the thickness scores would all be 0.025 or less: the
  watches are 9.6 to 12.1 mm against 3.85 mm. The order says "as thin as you can".
- **The model said so itself.** All six reports state P1 to P3 `not_tested` and P4 `pass`. That is truthful,
  and costs 3/68 of the reward.
- **It stopped early.** The first three agents ran for 810 to 2,036 s (14 to 34 minutes) of a 10,800 s limit
  (times for the other three are not logged yet).
- **Not every fault is equally clear.** Four runs have a fault nobody would argue with (a mobile that can fall
  out, hands below the frame, overlaps of 0.03 to 0.09 mm3). Two rest on a number close to a threshold of ours:
  `dQKXa6k` (held by 0.006 mm3 against 0.01) and `k843CBe` (hand shape 0.41 against 0.5). Even if those two
  were passed, their thickness scores would be 0.025 and 0.0005, and their rewards 0.49 and 0.48.

All six rewards were regraded on a second machine, outside Harbor, from the files on `a/final-runs`: the first
three with grader `3d5d96f`, the other three with the grader on `main`. Rewards and failed checks were
identical to workstream A's details files, except `k843CBe` after the fix above.

**Claude models (workstream A, Harbor + OpenCode, 15 Nov 08:39 to 08:56).**

- **Opus 5.5 at medium thinking: 0.925, the one run that delivers a watch that fully works.** 24 parts, 80
  steps, about 15.50 USD. Every gate and check of all four parts passes, on workstream A's verifier and again on
  a second machine. The report claims all four parts pass, and that is true. The movement is 4.23 mm tall; full
  thickness score is at 3.85 mm, so s = 0.850 and the reward is 1/2 + 1/2 x 0.850 = 0.925. (A's details file
  shows 0.943: it was graded when the bar was 3.95 mm.) This run shows two things. The task can be solved from
  the order and the sheets alone, including every threshold the agent is not told. And the thickness term does
  what it is for: the remaining gap to the reference, 0.075, is 0.38 mm of height.
- **Opus 5.5 at low thinking, on Modal: 0.811, also a watch that fully works.** Run by a second team member
  from the checked-in `task/` with the grader on `main` (branch `modal-runs`, `jobs-modal/opus-low/`, trial
  `3hJXaYm`; Harbor marks it valid, agent time 50 minutes). Every gate and check passes, the report is honest,
  the movement is 4.92 mm tall: s = 0.622, reward 1/2 + 1/2 x 0.622 = 0.811. This number is from Harbor's own
  verifier on Modal; we have not regraded it separately.

- **Sonnet 5.5: 0.422.** A complete movement, 5.75 mm tall. One check fails, `held`, in both builds: three
  mobiles can be lifted straight out upwards, with nothing above them (zero contact). The report claims all four
  parts pass, which costs 2/17 of the reward. Regraded on a second machine with the grader on `main`: the same
  reward and the same failed check.
- **Opus 5.5: 0.422 in workstream A's verifier, and we could not reproduce that number.** There it is a complete
  movement, 4.08 mm tall, the closest to our 3.85 mm of any run, and one check fails: `tolerant`. One gear pair
  still drives at 0.488 of the required overlap when its axis is moved 0.03 mm, against a limit of 0.5. Both
  numbers are thresholds of ours that the agent is not told (known limits), so this failure is a close call on a
  rule the agent could not read. Had it passed, the run would score 0.95: everything works, and it is 0.23 mm
  thicker than our bar. The report claims all four parts pass.
  Regraded on a second machine (x86, cadquery-ocp 7.9.3.1), the same delivery scores **0.082**: OpenCASCADE reads
  one of its part files, `a_wheel_8h.step`, as two open shells instead of one solid, so the 8-hour build fails
  the format gate. The file is the same; the two machines' CAD kernels read it differently. We have not found
  which reading the judges' machine will give. This is a reproducibility fault of our environment (the image
  does not pin the CAD kernel build), found at 08:50 on the last morning and not fixed.
- **Before these:** Sonnet 5.5 delivered nothing in six runs (four at default and medium thinking, A 06:20; one
  at medium, A 07:01; one at low, A 07:44), each ending in a single reply of about 128,000 thinking tokens (see
  "How to run it"). Other Claude runs were cut off by our API credit limit, which Harbor marks invalid; one of
  them, Sonnet at low thinking, had built a 5.02 mm watch scoring 0.412 with 18 unheld directions.

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
- **Frontier agent:** GPT-6.1-sol, six Harbor runs: 0.427 to 0.467, mean 0.447. All six are below one half;
  the spread is 0.04.
- **The strongest results:** Opus 5.5, two working watches: 0.925 (medium thinking, 4.23 mm) and 0.811 (low
  thinking, on Modal, 4.92 mm). Both are below the reference by thickness alone. A third Opus run, at low
  thinking in local Docker, scored 0.422.
- **Checkable:** the six deliveries and the grader's details files are on branch `a/final-runs`. Anyone can
  regrade them with the four shell lines under "How to run it".
- **Other Claude runs under OpenCode:** one valid run each of Sonnet 5.5 and Opus 5.5 at low thinking, both
  0.422; the Opus one did not reproduce on a second machine (Results).
- **Not shown:** repeated Claude runs: each Claude number is one run, which is not "consistently". With Opus at
  medium thinking the gap is 0.075, not one half; we do not know how often it reaches a working watch. The six
  GPT runs used the Codex agent, not OpenCode.

### Meaningful difficulty (30 p)

> Full points: you can explain the agent's main mistakes and connect them to decisions in the task; the
> information and tools needed to do better are available to it. Zero points: the gap comes from unfairly
> withheld information, trick wording, impossible timing, or broken tools.

- **The mistakes, by name** (table under Results): mobiles that overlap as they turn (three runs of six), a mobile
  that is not held in place (two), wheels not seated on their arbors (two), a 24-hour hand below the top of the
  frame (two), hour and seconds hands below it (one), a 24-hour hand of the wrong shape (one). Each is a measured fault in the delivered parts, in the details file.
- **The decisions behind them:**
  - The agent decided when it was done. It stopped after 14 to 34 minutes of 3 hours.
  - It decided not to test its own watch. All six reports say P1 to P3 `not_tested`.
  - It decided how thin to go. All six are 9.6 to 12.1 mm in a case that allows 13.4 mm; our designs are
    3.35 and 3.85 mm.
- **Information and tools available:** the order, seven supplier sheets, the file format, CadQuery, and
  `tools/kernel.py` with the factory's own STEP loader, intersection volume and smallest distance. These are
  enough to test "held", "overlap while turning" and "hand above the frame" before delivering. The reference
  is built with the same CadQuery; its involute gear maker (`geometry/watch_gears_cad.py`) is our own code and is
  not given to the agent, which has to write its own.
- **It can be done:** Opus 5.5 at medium thinking passed every check from the same order, sheets and tools,
  without being told a single threshold.
- **Withheld information:** the agent is not shown the acceptance test. Every check traces to the order, a
  sheet, the format or trade practice ([docs/CHECK_BASIS.md](docs/CHECK_BASIS.md)). The requirement is always
  traceable; some of the exact thresholds are ours and are stated nowhere (known limits). `held` and `seated`
  ask whether a mobile can be moved 0.3 mm out of place.
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

- **Doing nothing:** 0.000 in Harbor (nop agent), in local Docker and on Modal; an empty delivery folder grades
  0.000000 outside Harbor.
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
- **Anchor suite on the submitted grader** (`python3 tests/test_anchors_job.py 3`, 38 deliveries, each the
  reference with one change, about 80 minutes): the reference scores 1.000; without a report 0.941; with one
  honest part marked `fail` 0.985. The other 32 that could be built score between 0.000 (do nothing) and 0.462. So in
  this suite nothing but the complete, working reference comes near full score.
  - 14 anchors give exactly the reward written in the file, including do-nothing, the three stop-early
    deliveries and the report (honesty) cases.
  - 24 do not match the file, and the file is what is out of date: it was written for our earlier, roomier
    reference. Five give the expected reward with a different part list (18 parts now, not 17). Fifteen score
    lower than written, because on the thin layout the same single fault breaks more checks. One scores 0.0005
    higher (17 of 18 parts installed instead of 16 of 17). Three could not be built on the thin geometry.
  - We have not rewritten those 24 expectations for the thin layout.
- **Not done:** an exploit hunt against this version. Earlier hunts are in `docs/history/`.

### Craft (15 p)

> Full points: the environment's rules and behavior make sense for the setting; judges can run the evaluation
> from your README with one command and reproduce your reported results. Zero points: the environment only
> works in your demo, or judges cannot reproduce the evaluation.

- **Makes sense for the setting:** the task is a movement designer's job from a customer order and supplier
  sheets, and its numbers come from real calibres ("Why it is hard, and why that is fair").
- **One command:** `harbor/watch_one/run_all.sh MODEL K` builds the task and runs oracle, nop and the model.
- **Reproduce:** oracle 1.000 and nop 0.000 were reproduced by a second team member on a second machine and a
  second sandbox (Windows, Modal), from a fresh clone and the three commands under "How to run it"; the GPT
  deliveries can be regraded from `a/final-runs`.
- **Rules in one place:** `SPEC.md` names the constant and file behind every number.
- **Found by that clean-clone run and fixed:** a Windows checkout turned the verifier's shell script into CRLF
  and no reward was written. `.gitattributes` now keeps LF on every checkout.

### Tiebreaker: a smaller model that improves after training

Not done.

## Known limits

- **One task instance.** One order, one case, one catalogue.
- **Grader numbers that no agent document states.** The strength check uses a tooth load factor of 1.45 and
  allowables of 110 MPa (brass) and 725 MPa (steel); the agent's DS-201 gives proof stresses and no safety
  factor. The `tolerant` check shifts the driven axis by 0.03 mm. `held` and `seated` test whether a mobile can
  be moved 0.3 mm. The mesh test and the hand-shape test have thresholds of their own. We treat the last three
  as trade practice (a wheel must be held, a hand is a pointer), but the exact numbers are ours. The full list,
  step by step, is at the end of [solution/STEP_BY_STEP_WATCH.md](solution/STEP_BY_STEP_WATCH.md).
  `docs/CHECK_BASIS.md` marks the strength and `tolerant` numbers for replacement by a test of the movement as
  made; that replacement is not built. Of the faults in the GPT runs, `held` and `seated` rest on the 0.3 mm
  threshold; none rests on the strength numbers or the 0.03 mm shift.
- **The CAD kernel build is not pinned.** The images install `cadquery==2.8.0`, which pulls whichever
  `cadquery-ocp` build fits the machine. One delivered STEP file (Opus, `a_wheel_8h.step`) reads as one solid in
  one verifier and as two open shells in another, which changes that run's reward from 0.422 to 0.082. Within
  one machine the agent's own format checker and the verifier use the same kernel, so the agent can see what the
  verifier will see; across machines a reward may not reproduce.
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

## What we would change next

Reading our own results as someone who builds environments would, these are the faults that matter most, and
the fix for each.

1. **The reward hardly separates good from bad work below a working watch.** Eight of the ten valid agent runs that
   delivered a watch score between 0.42 and 0.47: a 4 mm watch with one near-miss and a 12 mm watch with hands below the dial get about
   the same. Half of the reward sits behind "every check passes"; two runs reached it (0.925 and 0.811), and only there did
   thickness count.
   *Fix:* pay the working-watch half in steps (per build, per function: runs, shows the time, can be
   assembled), and let thickness scale each step, so that a better watch always scores more.
2. **A complete but faulty watch scores little more than stopping early** (0.42 to 0.47 against 0.33 for three
   flawless parts of four). *Fix:* the same graded term; and weight the checks by what a fault costs the
   wearer, not evenly.
3. **Some pass marks are numbers the agent cannot read**, and three of the eight runs that fell short rest on a
   close call against one of them. *Fix:* state every threshold in a supplier sheet or the format sheet, or replace
   the check with the outcome it stands for (the movement as made, running), and score a band around each
   threshold instead of a hard edge.
4. **One delivered file gets two rewards on two machines.** *Fix:* pin the CAD kernel build in both images,
   and have the verifier refuse to grade if its kernel is not the pinned one.
5. **Nobody has shown a delivery that scores 1.0 and meets every stated condition.** The reference fits the
   case but would not run as printed; the design that runs as printed needs a slightly larger case. *Fix:* one
   reference that does both, with the as-made test in the score, and the full-score height taken from it.
6. **Too few runs on the judged harness.** *Fix:* eight runs per model under OpenCode, on Modal, with the
   thinking level fixed and stated.
7. **We know which checks failed, not yet which decision caused each.** *Fix:* read each transcript back from
   the failed check to the step that introduced the fault, and publish that trace per run.
8. **The fault anchors are written for an older layout.** *Fix:* regenerate every expected value from the
   current reference, and run the suite in CI on every change to the grader.
9. **One task instance.** *Fix:* vary the order: case size, barrel catalogue, hand layout, the variant's
   speed. The grader already reads these from constants; the reference script would have to become a solver.
10. **A run is slow and costly** (up to three hours, about 9 USD for one Opus run). *Fix:* a smaller order
    (two hands, one build) as an easier rung of the same task.

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
| `task/` | the Harbor task, ready to run |
| `harbor/watch_one/` | the script that builds `task/`, and the one-command runner |
| `docs/research/REAL_WATCH_WORK.md`, `docs/research/REAL_ML01_FAIRNESS.md` | the task against real watches and a real CAD design |
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
