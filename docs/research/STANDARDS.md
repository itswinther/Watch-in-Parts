# Standards our watch task should follow, and what each one changes

Written by Mikael + Claude (workstream A), 14 Nov. Research only: nothing in the repo was changed to
follow it yet. Every change below is a proposal. Spec and constant changes go through "Proposed spec
changes" in `SESSION.md`, as `CLAUDE.md` requires.

**How to read it.** Each entry gives the standard, what it says (in our own words), the URL, and what
it changes for us. Paywalled standards (ISO, IEEE, BSI, NIHS) are cited by title, scope and public
summaries only. No standard text is copied. **[unverified]** marks a claim we could not confirm from a
primary source. **[secondary]** marks a number taken from a reseller, a blog, a forum or Wikipedia
rather than from the maker or the standard.

The sources were read on 14 Nov 2026 with WebSearch and WebFetch. Two ETA PDFs were downloaded and their
text was extracted with `pypdf` inside `python:3.12-slim` in Docker.

What it applies to:

- the keyless spike (`spikes/keyless/`: `constants.py`, `build_task.py`, `docs/`);
- the staged plan (`spikes/STAGED_ACCEPTANCE_PLAN.md`);
- the harness (`TEST_ENVIRONMENT.md`);
- the four task documents (`TASK_DOCS_TEMPLATE.md`).

---

## 1. Agent-evaluation task standards

### 1.1 METR Task Standard (archived) and the time-horizon method

- **What it is.** METR's Task Standard defined a task family as a Python class with these parts:
  - `get_tasks`, `get_instructions`, `install`, `start` and `score`;
  - a `manifest.yaml` for resources;
  - network access denied unless the task asks for `full_internet`.

  METR has archived it and now writes its tasks in Inspect.
  https://github.com/METR/task-standard
- **Time horizon.** From "Measuring AI Ability to Complete Long Tasks", arXiv:2503.14499:
  - **Who did the baselines:** skilled professionals, averaging about 5 years of experience.
  - **How much:** over 800 baselines, 2,529 hours in total; 148 of 169 tasks have a baseline.
  - **Task time:** the geometric mean of the *successful* human baselines.
  - **Tasks with no successful baseline:** a researcher's estimate, based on similar tasks and on QA
    runs.
  - **Runs:** about 8 per agent and task.
  - **The horizon:** a logistic fit of success against log(task time). The 50 % horizon is the task
    length at which the fitted success rate is 50 %.
  - **Messiness:** tasks are also scored 0 to 16 on "messiness" factors. Each extra point lowered mean
    success by about 8 %.

  https://arxiv.org/html/2503.14499 · https://metr.org/blog/2025-03-19-measuring-ai-ability-to-complete-long-tasks/
- **Reward hacking.** From "Recent frontier models are reward hacking":
  - **Detection:** METR finds suspect runs with anomaly checks (unusually high scores) and an LLM
    monitor (Claude 3.7 Sonnet). Both give many false positives, so a human reviews every flag.
  - **Scoring:** a hack that reached a good score is *excluded* from the reported capability.
  - **Rates for o3:** 30.4 % of RE-Bench runs (where the scoring function is visible) and 0.7 % of
    HCAST runs.
  - **Prompts:** telling the model not to cheat barely reduced it (still 70 to 95 % on one task).

  https://metr.org/blog/2025-06-05-recent-reward-hacking/
- **What it changes for us:**
  - **task.toml:** our expert time is an *estimate*, not a baseline. Say so in metadata:
    `expert_time_basis = "author estimate, no human baseline"`.
  - **Runs:** 8 per model matches METR's practice (our plan already says `-k 8`).
  - **Reporting:** add a reward-hack audit to every run report:
    - an LLM monitor flags suspect transcripts;
    - a human confirms each flag;
    - a confirmed hack is scored 0 and counted, never silently dropped.
  - **Prompt:** our grader is hidden, which is the low-hacking condition (HCAST-like). Keep it hidden.
    Stating the checks is fine; shipping the grader code is not.

### 1.2 Terminal-Bench 2.0 (Harbor's own lineage)

- **What it says.** From the paper, arXiv:2601.11868:
  - **Selection:** 89 tasks chosen from 229 contributed.
  - **Time estimates:** each contributor gives an expert and a junior-engineer completion time. Expert
    estimates are mostly under a day; junior estimates range from an hour to a week.
  - **Difficulty, two kinds:**
    - the author's human rating (medium or hard);
    - an *empirical* label from frontier pass rates: easy ≥ 66.7 %, medium 33.3 to 66.7 %, hard
      < 33.3 %.
  - **Quality criteria:**
    - specificity: tests pass only in acceptable end states;
    - solvability: the oracle passes;
    - integrity: no shortcuts.
  - **Review pipeline, about 3 reviewer-hours per task:** a contributor checklist, an LLM check tool,
    manual review, runs with several models, an *adversarial exploit agent* prompted to cheat, and two
    final auditors.
  - **Reporting:** at least 5 trials per model-agent pair; results given with 95 % confidence
    intervals.

  https://arxiv.org/html/2601.11868v1
- **Task-writing guidance.** From "What makes a good Terminal-Bench task":
  - difficulty must come from the problem, not from fussy formats;
  - test outcomes, not implementation;
  - no step-by-step tutorial in the instruction;
  - watch real trajectories, failed ones especially.

  https://www.tbench.ai/news/writing-a-good-terminal-bench-task
- **Follow-up paper.** Bercovich, arXiv:2604.28093, reports reward loopholes in more than 15 % of tasks
  in mainstream benchmarks. https://arxiv.org/abs/2604.28093
- **What it changes for us:**
  - **task.toml:** keep both `expert_time_estimate_hours` and `junior_time_estimate_hours`.
    - **The conflict:** `build_task.py` says 12 h and 40 h, while `TEST_ENVIRONMENT.md` says "one to two
      days" for the keyless works.
    - **The fix:** pick one estimate, state its basis, and add `difficulty_empirical` once the 8 runs per
      model exist, using the TB2 thresholds.
  - **Validation ladder:** add a TB2-style adversarial exploit agent. That is an OpenCode run whose
    prompt asks it to pass the grader without building a working mechanism, run against the real
    grader. Read its trajectory even when it fails. Our hand-written exploit set is the human half of
    this; the agent half is missing.
  - **Checklist:** TB2's "every behaviour tested is in the instruction, and every behaviour in the
    instruction is tested" is the same rule as our `TASK_DOCS_TEMPLATE.md`. Cite TB2 there.

### 1.3 UK AISI Inspect: scorers, model grading, epochs

- **Scorers.**
  - **Built in:** `match`, `includes`, `pattern`, `answer`, `exact`, `f1`, `choice`, `math`,
    `model_graded_qa`, `model_graded_fact`.
  - **Default metrics:** `accuracy` and `stderr`.

  https://inspect.aisi.org.uk/scorers.html
- **Epochs.**
  - **Setup:** `Epochs(n, reducers)` runs every sample n times and reduces the n scores to one.
  - **Built-in reducers:** `mean` (the default), `median`, `mode`, `majority`, `max`, `pass_at_{k}`,
    `pass_k_{k}`, `at_least_{k}`.
  - **`grouped()`:** gives a metric per subgroup.
  - **`stderr(cluster=...)`:** gives clustered standard errors.

  https://inspect.aisi.org.uk/metrics.html
- **What it changes for us:** use Inspect's names in reports, so a reader knows exactly what each number
  is:
  - the "mean over 8" is `mean`;
  - the "pass rate" is `at_least_1.0` per trial, averaged;
  - the judge's "median of 3" is `median` over 3 epochs.

  Also report per-acceptance-step results with a `grouped` view (one row per step: wind, hold, run…).

### 1.4 SWE-bench Verified and pass@k

- **SWE-bench Verified.**
  - **Annotation:** each of 1,699 candidate issues was screened by about 3 of 93 developers, who flagged
    underspecified issues and invalid tests, and estimated the fix time for an experienced developer.
  - **Fix-time buckets:** < 15 min, 15 min to 1 h, 1 to 4 h, > 4 h.
  - **The 500-task split:** 38.8 / 52.2 / 8.4 / 0.6 % across those buckets.
  - **Disagreement:** labels went to the majority, or to the median when there was no majority.

  https://openai.com/index/introducing-swe-bench-verified/ (blocked to our fetcher; numbers from
  https://arxiv.org/pdf/2410.03859 and https://epoch.ai/blog/what-skills-does-swe-bench-verified-evaluate)
  **[secondary]**
- **pass@k.** Chen et al. 2021, "Evaluating Large Language Models Trained on Code", arXiv:2107.03374,
  introduced the unbiased estimator: with n samples of which c pass, pass@k = 1 − C(n−c, k) / C(n, k).
  We confirmed the paper's identity from its abstract page; the formula is from its section 2.1
  **[unverified: the HTML body was not fetched]**. https://arxiv.org/abs/2107.03374
- **pass^k.** Anthropic's "Demystifying evals for AI agents" defines pass^k (all k trials succeed) as
  the reliability counterpart to pass@k.
  https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- **What it changes for us:**
  - **Reporting:** report pass@1 (the unbiased estimate with n = 8), pass@8 and pass^8 per model, not
    only "how many of 8 reached 1.0". pass^8 is the honest number for "a watch designer you could rely
    on".
  - **task.toml:** a 1 to 2 day expert task is beyond SWE-bench Verified's top bucket, where only
    0.6 % of tasks sit. Say this in `difficulty_explanation`, citing the buckets, to place our task on
    a scale judges know.

### 1.5 HAL, the Holistic Agent Leaderboard (Princeton)

- **What it does.**
  - **The leaderboard:** a third-party, cost-aware leaderboard that reports accuracy *and* dollar cost
    per agent, plots the cost–accuracy Pareto frontier, and has a reliability dashboard.
  - **The paper:** arXiv:2510.11977, 21,730 rollouts, 9 models, 9 benchmarks, about $40k.
  - **Log inspection:** LLM-aided reading of the logs found agents searching HuggingFace for the
    benchmark instead of solving it, and agents misusing credit cards.

  https://hal.cs.princeton.edu/ · https://arxiv.org/abs/2510.11977
- **What it changes for us:**
  - **Reporting:** report cost per trial and tokens next to the score, and say where each model sits on
    cost against score (`harbor/watch4/cost.py` already has the cost).
  - **Audit:** the transcript audit should look specifically for attempts to find the task or its
    answers online. The allowlist blocks it, but an attempt is still a finding for the honesty review.

### 1.6 LLM-as-judge for agent trajectories

- **Sources:**
  - **Anthropic's guide.** https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
    - Prefer deterministic graders; use a model grader only where needed.
    - Grade each rubric dimension with its *own isolated* judge call.
    - Give the judge an "Unknown" way out.
    - Calibrate the judge against human experts.
    - "Grade what the agent produced, not the path it took"; transcripts are for diagnosis.
    - Read the transcripts.
  - **Agent-as-a-Judge.** Zhuge et al., arXiv:2410.10934. It judges intermediate requirements
    (DevAI: 55 tasks, 365 requirements) and comes close to human agreement.
    https://arxiv.org/abs/2410.10934
  - **Rubric position bias.** arXiv:2602.02219 (Findings of EMNLP 2026). Rubric judges favour score
    options at some positions. The fix is balanced permutations of the options across repeats, then
    aggregation. https://arxiv.org/html/2602.02219
  - **Judge panels.** Cross-family panels and majority or median aggregation are common practice.
    https://en.wikipedia.org/wiki/LLM-as-a-Judge **[secondary]**
- **Where our protocol stands** (`spikes/keyless/docs/REVIEW_RUBRIC.md`): cross-family judge, 3 repeats,
  median per item, and evidence quotes checked against the transcript. These already match the
  literature.
- **What it changes for us (judge protocol):**
  1. **One call per rubric item** (a, b, c, d) instead of one call for all four.
  2. **Add "unknown"** as a fourth option. It scores 0 and is counted separately, so a judge without
     evidence does not guess.
  3. **Shuffle** the order of the 0/1/2 descriptions across the 3 repeats (balanced permutation).
  4. **Calibrate once:** Mikael labels about 10 transcripts by hand. Report the agreement between judge
     and human; the target band suggested in vendor guides is 75 to 90 % **[secondary]**.
  5. **Report the spread** across the 3 repeats per item. An item with a wide spread is a rubric
     problem, not an agent result.
  6. **Keep the judge out of `reward.txt`**, as now. Anthropic's "grade the outcome, not the path"
     supports keeping the process review a side score.

---

## 2. Test and verification standards

### 2.1 ISO/IEC/IEEE 29119-3:2021, Test documentation (paywalled)

- **Scope (public summary).** Templates for software test documentation usable with any lifecycle, for
  manual and automated testing.
- **Documents covered:**
  - organisational: test policy, test practices;
  - project and level: test plan, test status report, test completion report;
  - dynamic testing:
    - test specifications: test design, test case, test procedure;
    - test data and environment: test data requirements, test environment requirements, data and
      environment readiness reports;
    - execution and incidents: test execution log, incident report.
- **History:** it replaced IEEE 829-2008 in 2013 and was revised in 2021.
- **URLs:** https://standards.ieee.org/ieee/29119-3/7499 · https://webstore.iec.ch/publication/71834 ·
  https://www.microtool.de/en/document-management/test-documentation-with-iso-iec-ieee-29119-32021/
  (public overview)
- **IEEE 829-2008** (superseded) had the older names: test plan, test design specification, test case
  specification, test procedure specification, test log, test incident report, test summary report. We
  use 29119-3's names and give 829's where a reader may know them better.

**Mapping our documents to 29119-3** (change to the test docs):

| 29119-3 document | Ours today | Change |
|---|---|---|
| Test plan | `CONTEXT.md` (why, what each step means to the owner) + `TEST_ENVIRONMENT.md` (harness, runs) + `STAGED_ACCEPTANCE_PLAN.md` | Add a "Test plan" heading to `CONTEXT.md` with scope, items under test (submission files), features not tested (rate accuracy, shock, magnetism: see section 3), pass criteria, and a pointer to `TEST_ENVIRONMENT.md` |
| Test design spec / test case spec | The acceptance table in `PROMPT.md` (steps 0 to 6) | Give each step an ID (`AT-0` assemble … `AT-6` return) with **preconditions** (crown position, stored turns), **inputs** (turns, pull), **expected result** (number and tolerance from `constants.py`). Use the same IDs in `details.json` |
| Test procedure spec | `grade.py`'s fixed order; the owner's sequence | One paragraph in `SOLUTION.md`: the order, and "a step counts only if all earlier steps passed" (our gate = 29119 "dependencies") |
| Test data requirements | `constants.py`, supplied parts (`supplied.py`) | Already a single source; reference them by name |
| Test environment requirements / readiness | `task.toml`, Dockerfile, the validation ladder (oracle 1.0, nop 0.0) | The oracle and nop results *are* the readiness report: log them as such in `SOLUTION.md` |
| Test execution log | `/logs/verifier/details.json`, `grade.log`, Harbor trial dir | Add to `details.json`: test case ID, start and end time, grader version (git SHA), constants hash, result, measured value |
| Incident report | "every shortfall traced to the acceptance step it failed and the decision behind it" | Make it a fixed record per failing trial: ID, step `AT-n`, measured vs expected, the agent decision behind it (quote), class (agent fault / grader fault / spec ambiguity) |
| Test status / completion report | `SESSION.md` entries; the results table at the end of `SOLUTION.md` | The `SOLUTION.md` results table is the completion report: add the run reporting fields of 1.3 to 1.5 |
| (not a test document) | `STEP_BY_STEP.md` | It is the *design* record of the reference (decisions and reasons). In ISO 9001 terms (2.2) it is a design output with its verification evidence, not a test document. Keep it as is |

### 2.2 ISO 9001:2015 clause 8.3, Design and development (paywalled)

- **What it says (public summaries).** Design must be planned (8.3.2), its inputs defined (8.3.3), and
  three controls applied (8.3.4):
  - **reviews:** can the results meet the requirements?
  - **verification:** do the outputs meet the inputs? ("built it right")
  - **validation:** does the product meet its intended use? ("built the right thing")

  Outputs (8.3.5) and changes (8.3.6) are controlled.
  https://www.iso.org/standard/62085.html (catalogue) ·
  https://www.ecesis.net/ISO-9001/Design-and-Development.aspx (public summary) **[secondary]**
- **What it changes for us:**
  - **Name the two layers in `CONTEXT.md` and the brief:**
    - the per-stage checks are *design verification* (each stage's output against its stated input);
    - the owner's acceptance test is *design validation* (does the finished watch do its job).

    This is exactly the argument of `STAGED_ACCEPTANCE_PLAN.md` ("only at the end"), and 9001 gives it
    a standard name.
  - **Change requests:** the change request after delivery (plan addendum) is 8.3.6, "design and
    development changes". The frozen parts are controlled outputs. Cite it in `CONTEXT.md` as the
    real-world basis of the mechanic.
  - **Judge:** the LLM process review is closest to a *design review*. It checks how the work was
    done, not whether the product works. This is a good one-line justification for keeping it a side
    score.

### 2.3 V-model

- **What it is.** Decomposition runs down the left side (needs, requirements, architecture, part
  design); integration and test run up the right. Each level is checked against its mirror on the
  left. Verification asks "built it right"; validation asks "built the right thing". The German
  V-Modell (IABG, 1992) and a US version (NCOSE 1991) are the origins.
  https://en.wikipedia.org/wiki/V-model
- **What it changes for us.** Add this mapping to `CONTEXT.md` as one figure or table:

  | V-model level | Left side (ours) | Right side (ours) |
  |---|---|---|
  | Need and acceptance | the owner's brief | AT-1 to AT-6 |
  | Requirements and system test | the stated numbers | AT-1 to AT-6 on the whole |
  | Architecture and integration test | choice of mechanism (the agent's) | AT-0 assemble |
  | Part design and unit checks | each part | bounds, printable, held |

  It shows judges that our gate ordering is standard practice, and that the agent owns the left side
  (method freedom).

---

## 3. Watch industry standards and real numbers

### 3.1 ISO 3159 / COSC chronometer

- **What it says.** ISO 3159 (Swiss counterpart NIHS 95-11) defines wrist chronometers with a
  spring-balance oscillator. COSC applies it:
  - 15 days for wristwatches;
  - 5 positions;
  - 3 temperatures: 8, 23 and 38 °C;
  - wound daily;
  - 7 elimination criteria, including a mean daily rate of −4 to +6 s/day.

  https://cosc.swiss/en/certification/methods-measurement (the page now 404s; figures confirmed via
  https://en.wikipedia.org/wiki/COSC **[secondary]**) · ISO catalogue https://www.iso.org/standard/17220.html
  **[unverified: catalogue number not fetched]**
- **What it changes for us:** *nothing in the score*.
  - Our "run" step checks the gear ratios exactly (rates 1/12, 1 and 60 turns per hour). It does not
    simulate an oscillator, so a rate tolerance in s/day has no meaning in our simulation.
  - Say so in the test plan under "features not tested".
  - Do **not** borrow −4/+6 s/day as a tolerance.

### 3.2 ISO 1413:2016, shock-resistant wrist watches

- **What it says.**
  - **The shock:** the test simulates a 1 m fall onto a horizontal hardwood floor, applied as
    pendulum-hammer shocks. Per Wikipedia: 3 kg at 4.43 m/s, about 3,100 g.
  - **After the shocks:** the rate must stay within ±60 s/day.
  - **The 2016 edition:** added a third shock *on the crown* side, after which nothing may be bent or
    broken.
  - **Purpose:** type testing.

  https://www.iso.org/standard/62753.html ·
  https://www.boutique.afnor.org/en-gb/standard/iso-14132016/horology-shockresistant-wrist-watches/xs024431/124470 ·
  https://en.wikipedia.org/wiki/Shock-resistant_watch **[secondary for the hammer numbers and ±60 s/day]**
- **What it changes for us:** not in scope now. It is the one real standard that tests the *crown and
  stem* mechanically.
  - **A possible later step,** "AT-7 knock": after AT-6, apply a stated axial and side load to the crown
    and require that the stem stays in its position and nothing leaves its seat.
  - **Who decides:** list it as an option for the humans; do not add it unasked.

### 3.3 ISO 764:2020, magnetic-resistant watches

- **What it says.** The watch is exposed to a 4,800 A/m DC field. Per secondary summaries, the rate
  afterwards must stay within ±30 s/day.
  https://connect.snv.ch/en/iso-764-2020 ·
  https://www.boutique.afnor.org/en-gb/standard/iso-7642020/horology-magnetic-resistant-watches/xs134273/131492
  **[±30 s/day secondary]**
- **What it changes for us:** nothing. Material magnetism is not modelled. List it under "features not
  tested".

### 3.4 NIHS (Normes de l'industrie horlogère suisse)

- **What it is.** The FH's Watch Industry Standards department in Biel publishes the NIHS. The numbering
  is "topic group – document".
  - **Confirmed numbers:**
    - NIHS 91-10 (Swiss counterpart of ISO 1413);
    - NIHS 91-20 (types of linear shocks on components);
    - NIHS 95-11 (wrist chronometers, = ISO 3159);
    - NIHS 96-50 and 96-60 (external parts);
    - **NIHSG 20-30:2022, "Engrenages – Dimensions des dentures à profils ogivaux"** (ogival gear
      tooth dimensions, 5 pages).
  - **Copyright:** the FH protects the files; they are sold, not free.

  https://www.fhs.swiss/en/shop · https://www.fhs.swiss/file/33/normes_disponibles.pdf (list; 404 on
  our re-fetch, titles from the search index) · https://connect.snv.ch/en/ics/horology
- **Not found [unverified]:** an NIHS norm specifically on winding, setting, crown or stem functions,
  or power reserve. The NIHS list was not readable in full, so one may exist; ask nihs@fhs.swiss or
  read the list in a browser.
- **Related French norms** (cycloidal watch gears): NF S80-525 and NF S80-526 (1995, current).
  https://www.boutique.afnor.org/en-gb/standard/nf-s80526/horology-cycloidal-toothed-gearings-stepup-or-reduction-gears/fa014751/69947
- **What it changes for us:**
  - **Terminology:** use the NIHS and ETA names in the brief and the docs: *winding stem, sliding pinion,
    winding pinion, crown wheel, ratchet wheel, click, click spring, setting lever, yoke, setting-lever
    jumper, setting wheel* (these are the English names in ETA's own parts list, 3.5).
  - **Gear profiles:** the gear-profile norms (NIHS 20-30 ogival, NF S80-525 and 526 cycloidal) are
    the references for the profile we supply or accept. Cite them by title in `CONTEXT.md`; do not
    reproduce their tables.

### 3.5 Manufacturer specs for common movements (the numbers)

| Movement | Size | Height | Jewels | Frequency | Power reserve | Source |
|---|---|---|---|---|---|---|
| **ETA 2824-2** (automatic) | 11½‴, Ø 25.60 mm | 4.60 mm | 25 | 28,800 A/h (4 Hz) | **min 38 h, typical 42 h** | ETA Technical Communication CT 2824-2, 06.10.2022, p. 1 (primary): https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1883 |
| Sellita SW200-1 (2824 equivalent) | 11½‴, Ø 25.60 mm | 4.60 mm | 26 | 28,800 A/h | typical 41 h | Sellita catalogue 2024 (primary, via search index): https://sellita.ch/images/documents/Catalogue2024_ENG.pdf |
| **Unitas / ETA 6497-1** (hand-wound) | 16½‴, Ø 36.6 mm | 4.5 mm | 17 | 18,000 A/h | 46 h | https://wornandwound.com/caliber-spec-unitas-64976498/ **[secondary]** |
| ETA 6497-2 | same | same | 17 | 21,600 A/h | about 53 h | https://calibercorner.com/eta-unitas-caliber-6497-1-vs-6497-2 **[secondary]** |
| Seagull ST3600 (6497 clone) | 16½‴, Ø 36.6 mm | 4.5 mm | 17 | 21,600 A/h | not found | https://calibercorner.com/seagull-caliber-st3600k **[secondary]** |

**What ETA's 2824-2 document gives** (primary):

- **The parts list, with numbered keyless-works positions:**
  - 2 sliding pinion;
  - 3 winding pinion;
  - 4 winding stem;
  - 6 setting lever;
  - 7 yoke;
  - 8 setting-lever jumper;
  - 17 click;
  - 18 click spring;
  - 19 crown wheel;
  - 20 ratchet wheel;
  - 32 setting wheel.
- **An order of assembly** for the hand-setting mechanism: main plate → sliding pinion → winding pinion
  → stem → … → jumper.
- **A typical balance lift angle** of 50°.

It gives **no tooth counts** and no stem travel.

**Crown positions.** The Eterna-cased 2824-2 manual describes two positions: A, winding; B, setting
with stop-seconds. Date versions add a quick-set position.
https://www.manualslib.fr/manual/627394/Eterna-Eta-2824-2.html?page=5 **[secondary]**

**Mainspring and winding figures (all [secondary]):**

- **Barrel speed:** the barrel typically turns once per about 8 h, so "the common 40-hour spring requires
  5 turns to unwind completely" (https://en.wikipedia.org/wiki/Mainspring).
- **Useful turns:** 6 to 8 is a common rule of thumb
  (https://www.firgelliauto.com/blogs/mechanisms/barrel-horology); one watchmaker measured peak torque
  near 7.2 barrel turns on a 2824-2.
- **Spring size:** watch mainsprings are about 20 to 30 cm long and 0.05 to 0.2 mm thick.
- **Recoil:** after winding, the click lets the arbor recoil "about two ratchet teeth" (Wikipedia,
  Mainspring).
- **Crown turns to wind fully from empty:** about 30 to 40 for a 2824-class movement
  (https://www.firgelliauto.com/es/blogs/mechanisms/stem-winding-movement and watch-care guides).
  **[unverified: no maker figure]**
  - That implies roughly 4 to 7 crown turns per barrel turn **[derived]**.
  - Firgelli's worked (not real) example: winding pinion 12, crown wheel 30, coaxial pinion 24, ratchet
    48, so 5 crown turns per barrel turn.
- **Stem travel** between winding and setting is about 1 mm
  (https://watchesbysjx.com/2026/08/keyless-works-explained.html and others) **[secondary]**.
- **Backward crown:** turning the crown backward makes the sliding pinion's ratchet ("wolf's", often
  called Breguet) teeth slip over the winding pinion's, so nothing reaches the barrel or the click
  (watchesbysjx, same URL).

### 3.6 What these numbers change in our acceptance test (`spikes/keyless/constants.py`)

| Constant now | Real reference | Proposed change |
|---|---|---|
| `BARREL_HOURS_PER_TURN = 8.0` | about 8 h per barrel turn (Wikipedia) | Keep; add the citation in a comment |
| `CAPACITY_TURNS = 6.0` → 48 h | 5 turns for 40 h; 6 to 8 useful turns; 2824-2 measured near 7 | Keep; cite |
| `RESERVE_MIN = 0.75` h, after `WIND_TURNS = 1` crown turn | ETA 2824-2: **min 38 h** from a full wind | The real owner winds until full. Make AT-1 "wind N crown turns from empty, where N = capacity × the agent's declared ratio + 10 %", and AT-3 "reserve ≥ 38 h" (ETA's minimum). The staged brief's "at least 40 h" also matches the common 40 h spring; pick one and cite it. If simulation cost forbids N ≈ 35 turns, simulate 1 turn and extrapolate *with the ratio measured in contact*, and say so in the brief |
| `WIND_MIN = 2°` of barrel per crown turn (ratio up to 180 crown turns per barrel turn) | about 4 to 7 crown turns per barrel turn **[derived]**, i.e. about 50 to 90° per crown turn | Set a band: **30° ≤ barrel per crown turn ≤ 120°** (3 to 12 crown turns per barrel turn). Wide enough for any sane design, and it rules out an owner needing 400 turns to wind it |
| `CLICK_RUNBACK = 20°` | recoil about 2 ratchet teeth | Express as "at most 2 ratchet teeth", i.e. 720°/z for the agent's ratchet with z teeth, capped at 20° |
| `PULL = 0.9` mm | about 1 mm stem travel | Keep; cite |
| 2 crown positions | 2824-2 no-date and 6497: 2 positions | Keep |
| `CASE_RADIUS = 8.7` mm (Ø 17.4) | 2824-2 Ø 25.6 mm; 6497 Ø 36.6 mm | Optional: scale the case to a real calibre (rebuild task, section 4) |

These are changes to constants that the grader and the brief share, so they go through "Proposed spec
changes" and need B's and the humans' yes.

---

## 4. Real components and reference designs

**Scope note.** `CLAUDE.md` lists "the datasheet lookup step" as *cut from scope* on day one ("Decisions
already made"). Everything in this section re-adds supplied real-world data in some form. **Whether to
do it is a human decision**; this section only says what exists, what is legal to use, and what the
task would look like.

### 4.1 Gear standards

- **ISO 54:1996, cylindrical gears for general and heavy engineering: modules.**
  - **What it is:** the preferred series of normal modules.
  - **Fit for us:** the public summaries list Series I starting at 1 mm. That is far above watch modules
    (watch train modules are about 0.05 to 0.2 mm **[secondary]**). **Not applicable to watch gears.**
  - **Use:** cite it only to say why we do not use it.
  - https://www.iso.org/standard/22644.html (catalogue; current, confirmed 2022)
- **ISO 1328-1:2013 and DIN 3962:** accuracy classes for involute cylindrical gears.
  - **Scope:** tolerances on pitch, profile and helix deviation for involute gears.
  - **Fit for us:** our contact simulation does not model manufacturing tolerance, and watch gears are
    mostly not involute. Cite by title only.
  - https://www.iso.org/standard/45309.html **[unverified: URL not fetched; scope from general knowledge]**
- **BS 978-2:1952, "Specification for fine pitch gears – Cycloidal type gears".**
  - **Scope:** cycloidal spur gears for spring- or weight-driven mechanisms (clocks, instruments),
    covering **modules 0.070 to 1.000**, tooth forms for wheels driving pinions, and tolerances.
  - **Status:** BSI lists it as current.
  - **Use:** this is the closest open-catalogue norm for our module range. Cite its module range; do not
    copy its tooth tables.
  - https://knowledge.bsigroup.com/products/specification-for-fine-pitch-gears-cycloidal-type-gears
- **NIHSG 20-30:2022 (ogival profiles), NF S80-525 and NF S80-526 (cycloidal):** see 3.4. Paywalled;
  cite by title.

### 4.2 Mainspring catalogues

- **Générale Ressorts (Bienne, Swatch Group).**
  - **The catalogue:** the reference catalogue for mainsprings by calibre. It is printed and old, and
    resellers re-list it.
  - **Size format:** height × thickness (strength) × length × barrel diameter, in mm.
  - **Cousins UK** lists them by size and by calibre.
  - https://www.cousinsuk.com/category/mainsprings-by-size-search-watch-pocket · https://watchguy.co.uk/original-mainsprings/
- **Example sizes [secondary]:**
  - **ETA 2824-2:** reported in an Omega Forums thread as about 1.23 to 1.25 × 0.125 × 360 mm (Cousins
    part G57162). Sources conflict and the barrel diameter is not given.
    https://omegaforums.net/threads/eta-2824-2-mainspring-dimensions-and-part-number.187868/
  - **ETA 2801:** a reseller lists 1.23 × 0.134 × 400 × 10.5 mm.
    https://en.ressortdebarillet.ch/products/1-23-x-134-x-400-x-10-5-eta-2801-mecanique
- **Torque and turns per spring:** not published in anything we found **[unverified]**.
- **Licence:** dimensions are facts, which generally are not copyrightable. Restating a handful of
  sizes with a source link is fine. Copying a reseller's whole table is not; neither is a "Générale
  Ressorts" branded catalogue. (This is our reading, not legal advice.)

### 4.3 Jewel and bearing catalogues

- **Seitz (Swiss jewel maker).** Resellers list Seitz jewel holes by hole diameter × outer diameter.
  Examples:
  - a 0.14 mm hole with a 2.60 or 3.00 mm outer diameter (H.S. Walsh);
  - friction bushings at 1.00 mm OD × 0.30 mm hole × 0.30 mm high.

  https://www.hswalsh.com/watch-parts-straps-batteries/jewel-holes-endstones-roller-pins-pallet-stones/jewel-holes/cat-8 ·
  https://www.ofrei.com/page454.html **[secondary]**
- **No official Seitz size table found [unverified].** The same licence reading as 4.2 applies.

### 4.4 Open-source movement designs

- **openmovement OM10** (association, La Chaux-de-Fonds).
  - **What it is:** described as the first open-source Swiss mechanical movement, 3.5 Hz
    (25,200 A/h), with STEP files.
  - **Access:** a free download after registration.
  - **Licence: unclear.**
    - openmovement.org names no licence.
    - The OHO wiki lists CC BY-SA 3.0 (the page refused our connection).
    - A Hackaday commenter says the download agreement is not open.
  - **Treat as: humans may study it; do not commit or redistribute its files.**
  - https://openmovement.org/ · https://hackaday.com/2025/06/03/open-source-watch-movement-really-ticks-all-the-boxes ·
    https://en.oho.wiki/wiki/Basiswerk_OM_10_clockwork
- **A separate open-source automatic** on Gumroad lists CC BY-SA 4.0 **[unverified: not opened]**.
  https://domsidequest.gumroad.com/l/etynz
- **ETA, Sellita and Unitas:** proprietary. Their public technical communications give envelope numbers
  and parts lists (3.5), not drawings or tooth counts.

### 4.5 Supplier sites with part dimensions

- **Cousins UK:** mainsprings by size and calibre; parts by calibre.
- **H.S. Walsh:** jewels by size.
- **Ofrei:** jewels and bushings.
- **ressortdebarillet.ch:** mainsprings by size.
- **watch-spare.com:** calibre parts lists.

All give dimensions per part number, not geometry.

### 4.6 What we may legally use

| Data | Use in a public repo |
|---|---|
| Envelope numbers (diameter, height, jewels, frequency, power reserve), part names, parts-list topology | Yes, restated with a citation (facts) |
| A few catalogue sizes (mainspring h × t × L × Ø, jewel hole × OD) | Yes, a small, cited selection in our own JSON |
| ETA / Sellita PDFs, exploded drawings, photos | No: link only |
| ISO, BSI, NIHS and AFNOR text or tables | No: title, scope and our own summary only |
| OM10 STEP files | No, until a licence is confirmed in writing |

### 4.7 Two task shapes this enables

**(a) Rebuild: "the keyless works of a 6497-class hand-wound movement".**

- **Supplied:**
  - the case and movement envelope, from public numbers: Ø 36.6 mm, height 4.5 mm;
  - the barrel position and a mainspring stated as "capacity 6 turns, 8 h per turn": 48 h, which
    covers the 6497-1's 46 h;
  - the stem axis, and two crown positions with about 1 mm of travel;
  - the parts list *by name and function only*, taken from ETA's 2824-2 / 6497 lists (sliding pinion,
    winding pinion, crown wheel, ratchet wheel, click and spring, setting lever, yoke, jumper, setting
    wheel).
- **The agent designs:** the geometry and tooth counts. The real ones are not published.
- **Graded by:** our acceptance test, AT-0 to AT-6, with the section 3.6 numbers.
- **Why the 6497:** it is hand-wound, large, simple, and has a cheap clone (ST3600), so a demo can show
  the real part next to the agent's.
- **Gap risk:** naming the parts is a method hint, which `TASK_DOCS_TEMPLATE.md` forbids ("no names of
  mechanisms the agent should choose"). Variant: give only the envelope and the numbers, and keep the
  parts list in `CONTEXT.md` for the judges.

**(b) New design with catalogue components.**

- **Supplied:** `/app/catalogue.json`, a small cited selection:
  - 4 to 6 real mainsprings (h × t × L × barrel Ø, plus our stated capacity and hours per turn);
  - 6 to 10 jewel sizes (hole × OD × height);
  - allowed modules from the BS 978-2 range, say 0.08 to 0.20 mm.
- **The agent:**
  - must pick a mainspring, and that choice sets the barrel size and the reserve;
  - must put every arbor into a catalogue jewel;
  - designs all custom parts at catalogue modules.
- **Grading adds:**
  - every catalogue reference exists and its declared dimensions match the catalogue;
  - the barrel fits the chosen spring;
  - then AT-0 to AT-6.
- **Why it widens the gap:** a choice made early (the spring) has consequences late (reserve, space for
  the keyless works). That is the "foresee consequences" skill `STAGED_ACCEPTANCE_PLAN.md` targets,
  and it is how real engineers pick off-the-shelf parts.

---

## 5. Concrete changes, by place

- **`task.toml` metadata** (`spikes/keyless/build_task.py` and watch stages):
  - one consistent `expert_time_estimate_hours` and `junior_time_estimate_hours`, plus
    `expert_time_basis = "author estimate, no human baseline"` (METR, TB2);
  - `difficulty_empirical` after the 8 runs per model (TB2 thresholds);
  - `standards = ["ISO/IEC/IEEE 29119-3", "ISO 9001:2015 8.3", "ETA 2824-2 CT 2022 (power reserve)"]`;
  - `difficulty_explanation` placing it beyond SWE-bench Verified's top fix-time bucket (> 4 h).
- **Test docs:** the 29119-3 mapping in 2.1:
  - test case IDs `AT-0` to `AT-6` with preconditions, inputs and expected results;
  - a test execution log schema in `details.json`;
  - an incident record per shortfall;
  - the `SOLUTION.md` results table as the completion report;
  - "features not tested" (rate in s/day, shock, magnetism, water) in `CONTEXT.md`.
- **Acceptance numbers:** the table in 3.6 (winding-ratio band, 38 h reserve from a full wind,
  click ≤ 2 teeth, citations in `constants.py`).
- **Judge protocol:** the six points in 1.6.
- **Run reporting** (per model, 8 trials):
  - mean with 95 % CI;
  - pass@1 (unbiased), pass@8, pass^8;
  - per-step pass counts (`grouped`);
  - cost and tokens per trial, with cost against score;
  - timeouts;
  - reward-hack flags (monitor + human, hacks scored 0 and counted);
  - judge median and repeat spread;
  - harness versions (Harbor, OpenCode, model ID, grader SHA).

## 6. Top changes, in priority order

1. **Make the acceptance numbers real and cite them** (3.6): reserve ≥ 38 h from a full wind (ETA
   2824-2 minimum), a winding band of 3 to 12 crown turns per barrel turn (replacing `WIND_MIN = 2°`),
   8 h per barrel turn and 6 turns of capacity (kept, now cited), click run-back ≤ 2 ratchet teeth. The
   current `WIND_MIN` accepts a crown that needs about 180 turns per barrel turn. *Needs B and the
   humans' yes.*
2. **Run reporting to TB2, METR and HAL standard:** 8 trials, mean ± 95 % CI, pass@1/pass@8/pass^8,
   per-step pass counts, cost per trial, timeouts, harness versions.
3. **Reward-hack audit and an adversarial exploit agent:** a TB2-style "cheat on purpose" OpenCode run
   against the real grader, plus an LLM monitor over every transcript with human confirmation. Confirmed
   hacks score 0 and are counted (METR).
4. **29119-3 test IDs and logs:**
   - `AT-0` to `AT-6` as test cases (preconditions, inputs, expected) in `PROMPT.md` and `SOLUTION.md`;
   - the same IDs plus the grader SHA and a constants hash in `details.json`;
   - one incident record per shortfall.
5. **Judge protocol hardening:** one call per item, an "unknown" option, shuffled option order across the
   3 repeats, about 10 human-labelled transcripts for calibration, and repeat spread reported.
6. **Name verification vs validation (ISO 9001 8.3.4) and the V-model in `CONTEXT.md`:** stage checks
   are verification, the owner's test is validation, and the change request is 8.3.6. This is the
   standard basis for "accept as a whole, only at the end".
7. **Reconcile the time estimates in `task.toml`:** 12 h / 40 h vs "one to two days". Mark them as
   author estimates, and add an empirical difficulty after the runs.
8. **(Human decision; re-adds a cut item) Real components:**
   - first, the cheap version: scale the case and envelope to a real calibre (6497: Ø 36.6 mm, 46 h; or
     2824-2: Ø 25.6 mm, 38 h minimum) and cite it;
   - then, optionally, the catalogue task 4.7(b), with a small cited `catalogue.json` (real mainspring
     sizes, Seitz jewel sizes, BS 978-2 module range).

   Never ship ETA PDFs, OM10 files or standard tables.

## Not verified

- ISO 1413's ±60 s/day and hammer figures, and ISO 764's ±30 s/day: secondary sources, not the standard
  text.
- Crown turns to full wind (30 to 40) and the derived 4 to 7 crown turns per barrel turn: blogs, with no
  maker figure. No published tooth counts for the 2824-2 or 6497 keyless works were found.
- The 6497 and ST3600 frequencies and reserves come from secondary sources, which disagree.
- The NIHS full list was not readable. A norm on keyless works or crown functions may exist that we did
  not find.
- The OM10 licence.
- The pass@k formula's location in Chen et al. (section 2.1): from knowledge, not from the fetched page.
- ISO 1328 / DIN 3962 scope: from general knowledge; the catalogue page was not fetched.
