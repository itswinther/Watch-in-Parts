# Research brief: where frontier agents fail at engineering design, and what it means for our task

Workstream A (Mikael + Claude), 14 Nov 2026, 13:40. One page that brings together everything researched and
tested on 13 and 14 Nov. Details and full sources are in `spikes/RESEARCH_GAPS.md`, `STANDARDS.md` and
`HARBOR_RESEARCH.md`, our own results in `spikes/*` and `harbor/watch4/`, and the plan in
`spikes/STAGED_ACCEPTANCE_PLAN.md`.

## The question

Where do frontier agents (GPT-6.1-sol, Claude Opus 5.5 and Fable 5.2) fall short of an expert on physical
engineering design, in a way that holds up when the agent has Python, CAD and a sandbox, and that we can
explain and grade fairly?

## Bottom line

1. **Anything the agent can check with a few lines of code, it checks, and the gap disappears.** Stated
   ratios, limits and mesh checks get rebuilt and passed: our right-angle spike gave GPT 1.0 x3 and Sonnet 1.0.
2. **Every frontier shortfall we have seen came from a consequence that shows up later or through contact,
   not from a check that could be copied.** GPT-6.1-sol scored 0.42 and Sonnet 0.47 on the frozen staged
   watch. In both, a choice that passed its own stage made assembly impossible later.
3. **Published evidence agrees:** functional mechanisms are the weakest category. CAD-bench's right-angle
   gearbox builds 97 % of the time and scores 4 %; CADEngBench pin-slot joints passed 0 of 6 for every model.
   But most papers tested older models, no code execution, or hidden requirements.
4. **So we grade the watch as a whole, by using it** (an owner's acceptance test, in order), we build it in
   frozen stages, we add contact-driven mechanisms (keyless works), and we supply datasheets rather than
   stated limits, as a real engineer would get. The headline score stays deterministic; the run log explains
   failures.

## 1. Our own experiments (sandboxed: Harbor, allowlist set to the model endpoint, separate offline verifier)

| Task | Models | Result | What it showed |
|---|---|---|---|
| Gear train (13 Nov) | Fable, Opus, Sonnet | 1.0, 1.0, 0.92 | Numeric design becomes a solver |
| Five-step movement | GPT-6.1-sol x3 | 1.0 x3 | Revisable stages remove the pressure |
| Watch regulation, hidden physics | GPT x3, then x12 at 100 min | 1.0 x3; mean 0.974 | A stated formula becomes a least-squares fit |
| Frozen four-stage watch (B's task) | Fable, Opus (B); GPT x2 (A) | 1.0, 1.0; **GPT 1.0 and 0.42**; Sonnet 0.47 | **The only frontier shortfall:** a stage-3 bridge that blocks assembly at stage 4 |
| Right-angle winding (kinematic grader) | GPT x3, Sonnet (OpenCode) | 1.0 x4 | Agents rebuilt the mesh check. GPT's no-click face gear passed because the spec never asked for a click: part-by-part scoring rewards a non-working watch |
| Swiss-lathe probe (CAM, text only) | Opus, Fable, GPT | 8/8, 8/8, 8/8 (7/8 to the letter) | Stated machine limits become arithmetic. The only slip (GPT) followed from tool geometry, not a stated rule |
| Keyless works, contact simulator | in progress | engine and acceptance scoring built | The current lead (see the plan) |

Harness note: one Haiku run under OpenCode spent its whole 32k output budget on reasoning and submitted
nothing. That is a harness failure, not difficulty, and it has to be ruled out for the judged model.

## 2. Published evidence on CAD and engineering agents (read in full)

| Source | Finding | Caveat |
|---|---|---|
| **CAD-bench** (github CAD-bench, 2026) | Functional tier 14 %; right-angle gearbox 4 % with 97 % built; threaded pair 7 % | GPT-5.4 era; the grader passed a thinned tooth at 0.94 |
| **CADEngBench** (arXiv 2608.09296) | Edits that cut into or join existing bodies pass 40 to 46 %, against 247/248 for separate bodies; pin-slot 0/6 | One-shot, no execution |
| **Parametric CAD Bench v3** (2611.02659) | Opus 5.5: create-and-edit 39.7, drawing-to-CAD 84.7; all-zero tasks are edits | The edit regenerates from scratch; hidden checks |
| **Done Is Not Correct** (2611.10063) | 98 % claim done, 14.1 % silently wrong; errors sit in internal features (bores, counterbores); measuring before claiming gives 3.2 % | Older models, no shell; one ambiguous spec caused 13 of 31 errors |
| **RealCADBench** (2609.03773) | The agent loop fixes execution; fine detail and placement stay wrong | Surface overlap only 0.09 to 0.12 |
| **LMBuild** (2610.04292) | Operability about 20/100 for GPT-6 Astra and Opus 5 | No code execution, unstated affordances |
| **Physics-in-the-Loop** (IJCAI 2026) | FEA feedback raises the in-range share from 22 % to 59 %; models over-build | Only a reviewer agent ran FEA |
| **BuildArena** (ICML 2026) | Level 3 at 11 to 27 % for GPT-5 | Single shot; physics feedback gave 100 % in 5 rounds |
| **Text2CAD-Bench** (2605.18430) | Sweep, loft and shell 68 to 92 % invalid | Kernel errors an agent loop repairs |
| **Wendland 2025** (Education and New Developments) | "The most frequent errors arise from incorrect spatial arrangement"; describing the arrangement makes AI succeed, as with novice students | 4 qualitative cases, ChatGPT-4o |
| **CAD-Coder** (MIT, IDETC 2025) | A fine-tuned 13B model went from 0 % to beating GPT-4.5 on image-to-CadQuery (IoU 0.675 vs 0.524) | Evidence for the small-model tiebreaker, not for the gap |
| SpacetimeML research page | 85 to 90 % failure on 20 blueprints; five unsourced percentages | Vendor page; do not cite the numbers |

**Pattern:** published gaps rest on no code execution, single-shot submission or unstated requirements.
Each paper's own feedback ablation closes most of its gap. What survives is function under contact, edits
coupled to existing geometry, internal features, and consequences that appear later.

## 3. Harbor and Terminal-Bench: how tasks are built and where agents fail (`HARBOR_RESEARCH.md`)

**Harness matters:**
- On Terminal-Bench 2, the same model scores 3 to 22 points apart across harnesses (GPT-5.4: Codex 77.3 against
  Terminus 54.8). For Opus 4.5, OpenCode was the weakest of three (51.7 against 57.8).
- A gap shown only under OpenCode can be blamed on the harness. Run each model under its native harness too.

**Failure taxonomy** (TB2 paper and MAST, 1,642 traces):
- execution: disobeying the spec, step repetition 17.1 %;
- coherence: reasoning-action mismatch 14.0 %;
- verification: premature termination 7.8 %, no or weak verification 6.8 %.

24.1 % of failed commands called a missing executable. Turn count and token count do not predict success.

**Reward hacking is measured:**
- TB2.1 has a `reward_hacks` column (one harness and model at about 9 %).
- METR found o3 hacking 30.4 % of RE-Bench runs.
- TB2.0 runs deliberate "try to cheat" agents.

**Judges:**
- TB3 allows LLM judges only "in rare and extraordinary circumstances".
- LLM judges favour their own outputs (Wataoka et al. 2024, arXiv 2410.21819; a 2026 rubric study).
- **Keep the headline deterministic.** Use judges to explain, as a labelled side score at most, with repeats
  and the median taken.

**What Harbor already has:**
- RewardKit: programmatic plus judge criteria, judging the ATIF trajectory, `samples` with the median taken,
  and `guard` against planted instructions;
- `harbor analyze`: classifies failures with our own rubric;
- `harbor check` (a quality rubric) and `harbor lint`;
- `metric.py` for computing reported numbers, Hub leaderboards, and regrading old trials.

**Authors underestimate difficulty:** 54.5 % of TB tasks rated "medium" were hard. Experts' time estimates
correlate only r = 0.44 with observed difficulty. Measure difficulty, don't guess it.

## 4. Standards and real data (`STANDARDS.md`)

**Agent evaluation:**
- METR: about 8 runs per task; human baseline time as the difficulty measure.
- Terminal-Bench: each model at least 5 times; easy at 66.7 % pass or more, hard below 33.3 %.
- Report mean ± 95 % CI, pass@1, pass@k and pass^k.

**Test practice:**
- ISO/IEC/IEEE 29119-3 test documentation: test plan, test case specification, test log, incident report.
  Our acceptance steps become AT-0 to AT-6.
- ISO 9001:2015 clause 8.3 and the V-model: part checks are *verification*, the owner's test is *validation*,
  and a change request is a controlled design change. This is the standard basis for "accept as a whole".

**Watches:**
- ETA 2824-2 (from ETA's own document): Ø 25.6 mm, 4.6 mm high, reserve at least 38 h (typically 42),
  28,800 vibrations per hour, a numbered keyless parts list.
- Unitas 6497: Ø 36.6 mm, 46 h.
- Click run-back about 2 ratchet teeth; stem travel about 1 mm; barrel about one turn every 8 h.
- ISO 3159/COSC (rate), ISO 1413 (shock), ISO 764 (magnetism) exist but do not apply to a kinematic grader.
- BS 978-2 covers clock-scale cycloidal gears (module 0.07 to 1.0). ISO 54 starts at module 1.

**Licensing:** we may cite envelope numbers and part names. We may not ship ETA PDFs, standards' tables,
or OpenMovement CAD files (licence unclear).

**Machining** (Swiss-lathe probe):
- On a Swiss-type lathe a longer turn is a Z-plus move (MMS, "How Swiss-Type Machining is Different").
- The guide bushing supports the bar next to the cut, and its land limits travel per pass (Production
  Machining; CTE).
- Watch pinions and pivots are under 1 mm (CTE, "Time: Swiss precision").

## 5. What we concluded for the design

1. **Grade function, the way an owner accepts a watch:** assemble, wind, hold, run, backward, set, return, in
   order. Part checks are conditions on the whole, not points. *(Proposal 12:40, awaiting the team.)*
2. **Build in frozen stages, or with change requests after delivery.** The full acceptance test is stated up
   front and runs once, at the end, so foreseeing consequences is the skill tested.
3. **Contact-driven mechanisms (keyless works):** behaviour the agent cannot verify with arithmetic.
4. **An engineer's brief:** a role, the goal, deliverables, real datasheets, and one blanket clause ("operate
   within the ratings in the supplied datasheets and accepted watchmaking practice"). No method hints. Every
   implied check is traceable to a supplied value plus textbook physics.
5. **A deterministic headline score, plus a deterministic honesty check** (claimed results compared with
   actual ones). The run-log review uses RewardKit and `harbor analyze`, cross-family, with the median of 3
   runs, to explain failures.
6. **Harbor done properly:**
   - OpenCode as the organisers ask, plus a native-harness run per model;
   - `-k 8` with TB-style reporting;
   - `harbor check` and `lint`, oracle 1.0, nop 0.0, anchors and an exploit hunt, a deliberate cheat run;
   - evidence that the timeout and memory never bind;
   - everything in Docker.

## Open questions

- **For the team:**
  - the acceptance test as the score;
  - where `seated` is graded;
  - keyless and datasheets in scope (CLAUDE.md cut "datasheet lookup" on day one);
  - the tiebreaker (CAD-Coder shows small-model fine-tuning on CadQuery works).
- **For the organisers:**
  - the judged model and effort setting;
  - the per-trial timeout and rerun budget;
  - the Harbor version (0.25 reinstalls OpenCode from the internet);
  - credits for OpenCode runs.
