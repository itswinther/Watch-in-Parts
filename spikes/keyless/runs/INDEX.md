# Keyless runs: index

| Run | Label | Reward | Product | Honesty | AT-0 to AT-6 | Agent time | Files |
|---|---|---|---|---|---|---|---|
| reference (grader, in Docker) | reference | 1.000 | 1.000 | 1.000 | all pass | - | [details](reference/details.json), [replay](reference/replay.html) |
| GPT-6.1-sol, Codex, 1 trial | **PRELIMINARY SMOKE TEST: not a result; environment not final** | 0.024 | 0.025 | 0.571 | AT-0 pass, AT-1 to AT-6 fail (mirror-image mechanism) | 29 min / 60 | [README](prelim_gpt/README.md), [log](prelim_gpt/trial/), [replay](prelim_gpt/replay.html), [still](prelim_gpt/replay_still.png), [agent image](prelim_gpt/trial/) |
| Sonnet 5.5, OpenCode, 1 trial | **PRELIMINARY SMOKE TEST: not a result; environment not final** | 0.950 | 1.000 | 0.571 | all pass | 19 min / 60 | [README](prelim_sonnet/README.md), [log](prelim_sonnet/trial/), [replay](prelim_sonnet/replay.html), [still](prelim_sonnet/replay_still.png) |
| GPT-6.1-sol, Codex, repeat b7qdG8X | keyless v1 GPT repeats (Codex harness; engine fixes not yet merged; GPT's prelim design used no unsupported mechanism) | 0.024 | 0.025 | 0.571 | AT-0 pass, AT-1 to AT-6 fail (forward jam at clutch face teeth) | 32 min / 90 | [README](gpt_repeats/README.md), [log](gpt_repeats/trial_b7qdG8X/), [replay](gpt_repeats/replay_b7qdG8X.html) |
| GPT-6.1-sol, Codex, repeat imWnpTP | keyless v1 GPT repeats (Codex harness; engine fixes not yet merged; GPT's prelim design used no unsupported mechanism) | 0.022 | 0.025 | 0.000 | AT-0 pass, AT-1 to AT-6 fail (pinion-to-face-wheel tooth interference) | 38 min / 90 | [README](gpt_repeats/README.md), [log](gpt_repeats/trial_imWnpTP/), [replay](gpt_repeats/replay_imWnpTP.html) |
| GPT-6.1-sol, Codex, repeat QZeuFhk | keyless v1 GPT repeats (Codex harness; engine fixes not yet merged; GPT's prelim design used no unsupported mechanism) | 0.066 | 0.075 | 0.000 | AT-0 and AT-6 pass, AT-1 to AT-5 fail (forward jam at clutch face teeth, phase-dependent) | 31 min / 90 | [README](gpt_repeats/README.md), [log](gpt_repeats/trial_QZeuFhk/), [replay](gpt_repeats/replay_QZeuFhk.html) |

- **Validation:** [validation/VALIDATION.md](validation/VALIDATION.md) (lint, /app listing, oracle 1.0,
  nop 0.0).
- **Anchors:** [../docs/anchors_independent.log](../docs/anchors_independent.log).
