# Spikes: looking for a task frontier models fail

Run overnight 14 Nov by workstream A (Mikael + Claude), after H1 scored 1.0 in six of six
attempts. Each spike is a rough version tested on three Claude models (Fable 5.2, Sonnet,
Opus) running headless (`claude -p`) in a clean folder outside the repo, with web search and
subagents disabled. One instance each, so treat every number as a first look.

| Spike | What makes it hard on paper | Result | Folder |
| --- | --- | --- | --- |
| Hold the Line | 120 irreversible decisions, drift, jumps, delayed returns, inspection budget | Sonnet and Opus beat the scripted reference (9,926 and 10,285 vs 9,744). Fable played one slot (it waited on a background job and the headless session ended). | `../holdtheline/` |
| Wrist tracker for a child | One-sentence brief; size, mass, strap, edges never stated | All three made a sensible child-sized watch (31-34 mm wide, 20-29 g), with straps and rounded edges | `wrist_tracker/` |
| Watch gear train | Exact rates, centre distances fixed by tooth counts, layered packing in a round plate | All three valid. Fable and Opus scored 1.0, Sonnet 0.917 (one extra layer) | `gear_train/` |

## What the spikes show

- **Anything fully specified and checkable gets turned into a program.** In Hold the Line and
  the gear train every agent wrote its own simulator or exhaustive search, then submitted the
  result. A gap that depends on out-searching a model's own script is thin.
- **Unstated common sense is not a gap either.** The wrist-tracker agents inferred child wrist
  size, straps, sealed cases and skin-side charging without being asked.
- **What none of the briefs had:** components with connections (cable lengths, which face
  touches the skin), and physical limits the agent cannot compute from the brief alone.

## Known flaws found in the spikes themselves

- **Gear train, power reserve is free.** Nothing limits the barrel ratio, so every agent took
  6.5 × 140 / 7 = 130 h, and the reserve half of the score is trivial. A real movement is
  limited by torque at the escapement; a torque or amplitude rule would fix it.
- **Gear train, reference is weak.** The reference is a randomly planted valid movement (5 to
  7 layers), not an optimum, so agents match or beat it.
- **Wrist tracker** has no grader beyond size and mass; the deeper checks were not finished.

## Reproduce

- Gear train: `cd gear_train && python3 watch.py grade inst_1.json runs/opus/design.json ref_1.json view.svg`.
  New instances: `python3 -c "import watch; print(watch.plant(4))"`. The agent's brief is `kit/TASK.md`.
- Hold the Line: `cd ../holdtheline && python3 policies.py 60` scores the reference and anchors on 60 seeds.
