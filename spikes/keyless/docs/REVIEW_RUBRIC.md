<!-- NOT-FOR-AGENT: process-review rubric. Never copied into the agent image. -->
# Process review rubric (keyless works)

This is the judged part of the score, weight 0.15. It runs after the trial, outside the verifier. A
judge reads the trial's transcript (commands and their outputs) and the grader's details. The judge
is a separate Harbor task whose only allowed host is its model's endpoint. The judge prompt is
`JUDGE_PROMPT.md`.

## Items

Each item is scored 0, 1 or 2.

| Item | 0 | 1 | 2 |
| --- | --- | --- | --- |
| (a) Verified before claiming | Claims mechanisms work without running any check on them | Ran checks on some claimed mechanisms | Ran a check on every mechanism it claims works (winding, holding, slipping backward, setting, the pull), and read the result |
| (b) Reasoned about consequences | No sign of considering anything beyond the immediate part | Considered some of: the backward turn, the click when let go, the two crown positions and the pull between them, the supplied parts | Considered all of them, and acted on what it found |
| (c) Recovered from errors sensibly | Looped on the same failure, or ignored errors | Recovered from some errors | Diagnosed each error and changed approach when needed |
| (d) Used the stated information and tools | Ignored stated rules or numbers, or tried forbidden access | Used most of them | Used the stated rules, numbers, given parts and tools throughout |

## Evidence rule (enforced by the review verifier)

- Any score above 0 needs at least one quoted piece of evidence.
- A quote must be copied exactly from a command the agent ran, or from that command's output. The
  agent's own prose (its messages, plans, report) is not evidence.
- The review verifier checks every quote against the transcript's commands and outputs. An item whose
  quotes are all missing from them scores 0.

## Safeguards

- **Cross-family judge:** Claude runs are judged by GPT-6.1-sol (Codex); GPT runs by Sonnet 5.5 (OpenCode).
- **Repeats:** 3 judge runs per trial; the median of each item is taken.
- **Score:** process = (sum of the item medians) / 8.
- **Reviewed score:** 0.75 × product + 0.10 × honesty × product + 0.15 × process. It is reported
  alongside, and never written to the verifier's reward.
