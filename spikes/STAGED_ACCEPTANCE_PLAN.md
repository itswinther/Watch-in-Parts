# Build the watch step by step, accept it as a whole: a proposal (14 Nov, 12:45)

Written by Mikael + Claude (workstream A). It joins three findings from 14 Nov into one task design. It is
a proposal for the team: B owns the watch task and spec, and nothing here changes them.

## What the day's evidence says

| Finding | Evidence | Where |
|---|---|---|
| Checks the agent can copy in a few lines get copied, and the gap disappears | Right-angle gearing: GPT-6.1-sol 1.0 x3, Sonnet 1.0; every agent rebuilt the brief's mesh check before submitting. Swiss-lathe probe: stated limits became arithmetic for Opus, Fable and GPT | `spikes/right_angle/`, `spikes/swiss_probe/` |
| Frozen stages give the only frontier shortfalls so far | GPT-6.1-sol 0.42 (1 of 2 chains) and Sonnet 0.47: a decision that passed its own stage made assembly impossible later | `harbor/watch4/`, SESSION 11:55 |
| Part-by-part scoring rewards designs that do not work as a watch | GPT's right-angle design: one face gear, no click, so the mainspring would unwind through the crown. Scored 1.0 because the spec never asked for a click | `spikes/right_angle/README.md` |
| Behaviour that depends on position and contact is the strongest candidate for a gap | CADEngBench pin-slot joints 0/6 for every model; CAD-bench functional mechanisms weakest | `spikes/RESEARCH_GAPS.md`, `spikes/keyless/` |
| Spatial arrangement is where models (and novice students) fail | Wendland 2025, Education and New Developments: "the most frequent errors arise from incorrect spatial arrangement of features" | cited in `spikes/RESEARCH_GAPS.md` (to add) |

## The design

**The brief states the full final acceptance test from the start.** The agent knows the watch will be
assembled, wound, held, run, set and pushed back. Nothing is hidden.

**Stages, each graded on what it adds, then frozen:**

1. **Going train and barrel:** the hands' train runs at the right rates (B's stage 1).
2. **Motion works and the 24-hour hand** (B's stage 2).
3. **Change request:** the barrel's speed changes; rework with the earlier parts kept (B's stage 3; kept share by volume, as already approved).
4. **Keyless works:** stem, sliding pinion with Breguet teeth, crown and ratchet wheels, click, setting lever (prototype: `spikes/keyless/`).
5. **Assemble:** every part, in a declared order, along declared paths (B's stage 4).

**The final acceptance test, run once on the finished watch, in order:**

| Step | The owner… | It passes if… |
|---|---|---|
| 0 | Has it assembled | every part goes in along its path, in order |
| 1 | Winds the crown forward N turns | the mainspring stores the stated turns |
| 2 | Lets go | the click holds, nothing spins back |
| 3 | Lets it run | the hands turn at the right rates for at least the stated reserve |
| 4 | Turns the crown backward | nothing winds or jams; stored turns stay |
| 5 | Pulls the crown and turns it | the hands move; the barrel does not unwind |
| 6 | Pushes it back in and winds | it winds again, never half-engaged on the way |

**Score:** the chain of stage scores (as today) times the share of acceptance steps passed in order. A
step counts only if every step before it passed. Part-level conditions (clearances, support,
printability) are conditions on the whole, not points of their own.

## Why only at the end

If every stage ran the whole acceptance test on what exists so far, later consequences would become
present requirements, and agents check present requirements. GPT's 0.42 would then have been caught
and fixed at stage 3. Stating the final test up front but running it only on the finished watch keeps all
the information available while asking the agent to act on it early. That is the skill a watch designer
needs: foreseeing what a decision does three steps later.

## Fairness and integrity

- **Every shortfall has an owner's-eye reason:** "it cannot hold its wind", "the hands will not set", "the
  bridge cannot be installed".
- **The agent has the information and the tools.** The full test is in the brief, and CadQuery plus Python
  are in the image. Only the grader's verdicts are hidden.
- **Exploits:** in-order scoring makes part-level tricks worthless. The keyless exploit hunt (`spikes/keyless/`)
  is the template for the rest.
- **Repeatability:** the acceptance steps are deterministic simulations; no LLM judge anywhere.

## What it takes

- **B:** stages 1 to 3 and 5 exist. `seated` and the seven exploit fixes are being built now and fit
  unchanged.
- **A:** the keyless stage and the contact engine (`spikes/keyless/`, in progress), a stated mainspring
  model (capacity in turns, running at the barrel's stated speed) and the acceptance runner. Harbor packaging
  per stage already exists (`harbor/watch4/`).
- **Harness:** OpenCode via Harbor 0.26, as the organisers ask, with the allowlist set to the model
  endpoint only.
- **Grading cost:** the contact simulation adds minutes per run. It runs once, at the end.

## Open questions for the team

1. Yes or no on the acceptance test as the final score (proposal 12:40 in SESSION.md).
2. Should `seated` (B) be graded at stage 3, or only through step 0 at the end? This proposal argues for
   the end, to keep the delayed-consequence gap.
3. Is the keyless stage in scope for the submission, given its build and grading cost? This file argues
   yes, but it is the humans' decision.
