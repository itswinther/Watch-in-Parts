# Plan: the failure and training-data report

Status: plan only. Nothing in this file has been built or run yet.
Written 14 Nov, 13:45 Helsinki, by Abhishek + Claude.

## What it is, in one paragraph

After all testing is done, we turn the grader's results and the agents'
transcripts into one report that AfterQuery can act on the same day. The grader
already says *whether* a model failed. The report says *where* models fail, *why*
(traced to a decision in the transcript), and *what training data to collect* so
the next model does better. It is an extra on top of the reward, never part of it:
the reward stays deterministic and is unchanged by anything in this plan.

## Who reads it and what they get

| Reader | What they take away |
| --- | --- |
| AfterQuery judges | Proof that we can explain every failure (the "meaningful difficulty" criterion) |
| An AfterQuery data team | A ranked list of skills to collect training data for, with a ready data format |
| Our own team | Which checks actually bite, and which models they bite on |

## Honest limits (these go at the top of the report itself)

1. **Small samples.** Today it is one to two chains per model. Every rate is shown
   with its run count (for example "2 of 8 runs"), never as a bare percentage.
2. **Few models.** Claude and GPT only, unless more are run.
3. **Recommendations are hypotheses.** "Training on X should help with Y" is our
   reading of the failures, not a measured result. We label them that way.
4. **A failure is only reported after it is confirmed.** If a failure could be a
   grader fault, it goes in a separate "grader issues" list, not in the model's
   results.
5. **The task is still changing** (staged watch now, one-brief watch next). The
   report reads whatever the grader writes in its details file, so it should
   survive that change, but it must be rerun on the final task version.

## What it reads (all of this already exists in the repo)

| Input | Where | What we use from it |
| --- | --- | --- |
| Grader details | `grade_watch.py --details FILE` | reward, `p`, every gate and check (pass/fail), and per-check numbers |
| Margins | `harbor/watch4/metrics.py` | how close a pass came to failing (drive overlap, mesh gap, thickness) |
| Harbor trials | `<trial>/agent/*.txt`, `<trial>/artifacts/` | the transcript and the submitted files per run |
| Packed local runs | `transcripts/watch4_chain_*`, `manifest.json` | the same, for runs made outside Harbor |
| Outside-access audit | `harbor/watch4/audit.py` | runs to exclude as contaminated |
| Cost | `harbor/watch4/cost.py` | tokens and dollars per run |
| Reference | `solution/reference_watch.py` | what a correct answer looks like |
| Anchor suite | `tests/test_anchors_watch.py` | proof the grader was healthy when the run was graded |
| 3D viewer | `tools/viewer/` | pictures of failed parts for the report |

## How it works, step by step

1. **Collect.** Gather every graded run into one table, one row per run, stage
   and check: run id, model, harness, effort, task version, grader commit, stage
   or part, check name, weight, passed (yes/no), the check's numbers, cost.

2. **Clean.** Drop runs flagged by the outside-access audit, and runs graded with
   an older grader than the final one (regrade those instead). Record what was
   dropped and why.

3. **Confirm each failure.**
   - Rerun the anchor suite on the same grader commit; it must pass.
   - For each failed check, look at the grader's numbers and the part in the
     viewer, and confirm the failure is real.
   - Anything doubtful goes to the "grader issues" list and to B under Requests.

4. **Find the decision behind it.** For each confirmed failure, read the
   transcript and mark the moment the agent made the choice that caused it, plus
   whether the agent checked its own work before submitting. Use
   `harbor analyze` with our own rubric (see `HARBOR_RESEARCH.md`, section 1.2)
   for a first pass, then a human confirms each label.

5. **Label it with a skill.** Give each failure one label from the skill list
   below. One failure, one main label; a second label is allowed.

6. **Add it up.** Per model and per skill: how many runs failed, how many points
   it cost, and how close the passing runs came (margins).

7. **Write the recommendations.** For each skill that caused failures: what data
   to collect, how to generate it with our environment, and how to know it worked.

8. **Publish.** `report/out/REPORT.md` for people, plus machine-readable files
   for a data team (see "Outputs").

## The skill list (first version, to be adjusted once we read real failures)

Each skill is tied to the watch checks that reveal it, so the labels stay
objective.

| Skill | What going wrong looks like | Checks that reveal it |
| --- | --- | --- |
| **Thinking ahead across steps** | A choice passes now but blocks a later step (Sonnet's arbor that passed stage 2 and could not be installed at stage 4) | earlier stage passes, stage 4 `assembled` or parts install fails |
| **Assembly and spatial reasoning** | Parts collide, cannot be inserted, or sit in the wrong place | `assembled`, `clear`, `coaxial`, `seated` |
| **Mechanical reasoning** | Gears jam, disengage or don't drive; wheels not held | `train`, `spin`, `held`, `tolerant` |
| **Domain knowledge left unstated** | Hands at the wrong speed or turning the wrong way | `minute`, `hour`, `seconds`, `hands` |
| **Making it buildable** | Walls too thin, part too heavy, won't print | `printable`, `light`, `size` |
| **Checking its own work** | Submits without testing a requirement it could have tested | any failed check where the transcript shows no test for it |
| **Working within existing work** | Changes or breaks frozen parts, rebuilds what should be kept | `locked`, kept-parts factor |
| **Process** | Stops early, runs out of time, format errors | no submission, `files` gate |

"Process" failures are reported, but we flag them as possibly the harness's fault
until shown otherwise (for example Haiku stopping at stage 1).

## What the report contains

1. **Summary on one page:** headline score per model against the reference, the
   three biggest failure skills, and the honest limits.
2. **Benchmark table:** per model, per stage, every run, with reference,
   do-nothing and stop-early rows.
3. **Check-by-model heatmap:** which checks fail on which models.
4. **Top failure modes, one page each:**
   - what happened, in plain words;
   - the transcript moment (a short excerpt) and the decision made;
   - the grader's numbers and a viewer picture next to the reference;
   - whether the agent tested this before submitting.
5. **Near misses:** passing runs that came close to failing a check (from the
   margins). These show weaknesses the pass/fail score hides.
6. **Training recommendations,** one block per skill:
   - the skill and the evidence for it;
   - the kind of data to collect (see below);
   - how to generate it with our environment;
   - how to measure improvement (which checks, on fresh unseen instances).
7. **Grader issues found** and what was done about them.
8. **Method and reproduction:** the exact commands, commits and run list.

## The kind of training data we will recommend

These are the data types the recommendations draw from. Which ones appear in the
final report depends on what actually fails.

| Data type | What one example is | How our environment produces it |
| --- | --- | --- |
| **Worked solutions** | A full transcript that reaches 1.0 | The reference script, and the best agent runs |
| **Corrected mistakes** | A transcript up to the bad decision, then the right decision and why | Failed runs cut at the marked moment, with the fix taken from the reference |
| **Self-check examples** | The agent writes a test for a requirement, finds a failure, fixes it, then submits | Runs that did this well; failed runs rewritten to include the missing test |
| **Look-ahead examples** | A step-1 choice, shown together with what it does at step 4 | Chains where an early pass caused a later failure, paired with the reference's choice |
| **Contrast pairs** | Two near-identical designs, one passes and one fails a check, with the reason | Anchor submissions and near misses, labelled by the grader's numbers |
| **Dense rewards** | Per-check scores for reinforcement learning, not just one number | The grader's details file already gives every check separately |

## Outputs

| File | For whom | Contents |
| --- | --- | --- |
| `report/out/REPORT.md` | People | The report described above |
| `report/out/results.csv` | Analysts | One row per run, stage and check (the table from step 1) |
| `report/out/failures.jsonl` | A data team | One line per confirmed failure (format below) |
| `report/out/recommendations.json` | A data team | One entry per skill: evidence, data types, how to generate, how to measure |

One line of `failures.jsonl`:

```json
{
  "run_id": "watch4_chain_sonnet",
  "model": "claude-sonnet-5-5",
  "harness": "claude-code",
  "task_version": "spec 0.5",
  "grader_commit": "abc1234",
  "stage": 2,
  "check": "assembled (seen at stage 4)",
  "skill": "thinking_ahead",
  "decision": "Added an arbor with a wide collar below a closed hole and a wide head above it",
  "transcript_ref": "stage2/transcript.jsonl#L412",
  "self_tested": false,
  "grader_numbers": {"installable": false},
  "confirmed_by": "human"
}
```

(Values above are illustrative, written from the README's description of the
Sonnet run; the real line is generated from the data.)

## Rules this report must keep

- **The reward never changes.** The report reads grader output; it never feeds back
  into the score.
- **Nothing reaches the agent.** The report, its scripts and its outputs stay out
  of every image and bundle the agent can see (they name checks and show the
  reference).
- **No training on the test.** Recommended data must come from **new instances**
  (new seeds, new tooth counts, new cases), never from the exact tasks we evaluate
  on, and the report says so. Otherwise a trained model looks better on our
  benchmark without being better.
- **Done means run.** Every number in the report comes from a command that is
  listed in the method section.

## What we will build, in order

1. `report/collect.py`: reads details files, Harbor trial folders and packed
   runs, writes `results.csv`.
2. `report/analyze_rubric.toml`: the skill list as a `harbor analyze` rubric.
3. `report/label_failures.md`: a short checklist for the human who confirms each
   failure and its label.
4. `report/build_report.py`: reads the CSV and the confirmed labels, writes
   `REPORT.md`, `failures.jsonl` and `recommendations.json`.
5. A first draft on the runs we already have (four watch chains and GPT chains
   A and B), to test the pipeline before the final runs.
6. The final report on the final runs.

## Depends on

- **B:** the details file's format (`gates`, `checks`, `details`) staying stable,
  or a note in SESSION.md when it changes. A grader commit hash in every details
  file would help.
- **A:** where final Harbor runs land, and the run list (model, effort, harness).
- **E (Yoseph):** this report feeds the demo and the README's failure analysis;
  agree on one set of pictures and wording.

## Open questions

- Does AfterQuery want this as part of the submission, or as a separate document?
- Should the report cover the comparison experiment (frozen stages) as well as
  the final one-brief task?
- Is a human check of every failure label feasible for the final run count, or
  do we confirm a sample and say so?
