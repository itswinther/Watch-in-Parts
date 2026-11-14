# Four documents every task ships with

Proposed by Mikael (workstream A), 14 Nov. Each task we submit or test carries the same four files, so
judges, teammates and graders read every task the same way.

| File | Contents | Audience | Harbor location |
|---|---|---|---|
| `CONTEXT.md` | The real-world background: what the mechanism or job is, who does it, why it is hard, the evidence (papers, our runs), and what each acceptance step means to the end user | Judges, teammates, demo | Repo only |
| `PROMPT.md` | The exact brief the agent receives (see "Prompt rules") | **The agent** | Becomes `instruction.md` |
| `SOLUTION.md` | The correct answers and the acceptable range for every check, taken from the constants file; what the reference scores on each; what common wrong answers, anchors and exploit attempts score, and why | Graders, judges | `solution/`, **never in the agent image** |
| `STEP_BY_STEP.md` | The reference solution as an expert would do it: the decisions in order, the reason for each, the traps, and how each step is verified | Judges, demo, reviewers | `solution/`, **never in the agent image** |

## Prompt rules

- **Role and context in one or two sentences:** "You are a movement designer at a watch manufacturer."
- **Goal:** what the delivered thing must do, in the end user's terms.
- **Deliverables:** files, formats, the software to use (for example CadQuery 2.8, installed), and anything
  supplied.
- **Acceptance test:** every check, with every number and tolerance, and the order it runs in. A
  requirement the grader checks must be in the prompt. A hidden requirement is withheld information, and
  the judges score that down.
- **No method:** no steps, no hints about how to build it, no names of mechanisms the agent should
  choose, unless the part is supplied. Working out the method is the expert skill being tested.
- **Closing line:** "Report what you did and whether you reached anything outside this container."

## Rules for all four

- **One source of truth:** numbers in `PROMPT.md` and `SOLUTION.md` are generated from, or checked
  against, the same constants file the grader imports.
- **Keep the solution out of the agent's reach:** the build script must fail if `SOLUTION.md`,
  `STEP_BY_STEP.md`, `CONTEXT.md`, `solution/`, `tests/` or anchors would end up in the agent image (see
  CLAUDE.md, "What the agent under test may see").
- **Runs and results:** `SOLUTION.md` ends with a results table per model (8 runs: mean, spread, pass
  rate), and every shortfall is traced to the acceptance step it failed and the decision behind it.
