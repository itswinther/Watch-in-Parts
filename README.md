# Board in a Box

An RL environment for the AfterQuery challenge at Junction 2026.

An agent receives a circuit board assembly as data and meshes and must design a
3D-printable enclosure for it in code (CadQuery, trimesh, manifold3d). It submits
two STL files and a declared assembly path. A code-only grader checks that the
parts are valid solids, fit the board, can physically be assembled along the
declared path, and leave the connectors usable.

**Status (14 Nov, 00:50):** planning done, nothing built or run yet.
Live state is in [SESSION.md](SESSION.md). The exact task and scoring are in
[SPEC.md](SPEC.md).

## Why it should be hard for an agent

The agent has measurement tools (sections, distances, interference, sweeps) but
no tool that says whether a requirement passes. Every requirement is defined
numerically, so a careful agent can verify its own design before submitting.
The difficulty comes from constraints that interact:

- The board with its two connectors is longer than the cavity, so it has to be
  tilted and slid in.
- The slide needs spare room that the "board located" check then forbids, so the
  board needs locating pegs.
- The battery can only go in through the floor, after the lid is on.
- The height stack has 0.15 mm to spare.

Whether this actually produces a gap against a frontier agent is unknown until
the first spike runs.

## How it is scored (short version)

`S = G x (0.5 * p^2 + 0.5 * [all checks pass])`

`G` is the product of five pass/fail gates. `p` is the weighted share of 19
checks passed. The headline number is strict pass rate. Details: SPEC.md.

## Repository layout

```
SPEC.md         single source of truth: instance, contract, checks, score
CLAUDE.md       rules for Claude sessions working in this repo
SESSION.md      shared log: owners, status, decisions, open questions
environment/    agent image and MCP tool server          (not built yet)
geometry/       geometry module shared by tools and grader (not built yet)
tests/          grader, runs in Harbor's separate verifier (not built yet)
solution/       reference script for Harbor's oracle agent (not built yet)
anchors/        cheating and degenerate submissions with expected scores (not built yet)
holdtheline/    spike of the fallback idea               (not built yet)
```

## Running it

Not runnable yet. The target is one command that runs the reference, the anchor
suite, three agent runs and the two baselines, and prints the result table. This
section gets the real command once it has been run on a clean machine.

## Timeline (Helsinki time)

| When | What |
| --- | --- |
| Sat 03:00 | Harness wired end to end from the starter kit |
| Sat 07:00 | Two spikes done: instance H1, and the Hold the Line fallback |
| Sat 09:00 | Decision between the two ideas, from transcripts |
| Sat 16:00 | Latest moment to switch ideas |
| Sat 22:00 | Environment built out, anchor suite passing |
| Sun 03:00 | Full runs and failure analysis |
| Sun 09:00 | README and demo ready |
| Sun 10:00 | Final submission |

## Working in this repo

1. `git pull --rebase`
2. Read SESSION.md.
3. Do the work. Small commits.
4. Append an entry to SESSION.md, then `git pull --rebase` and `git push`.

If you work with Claude, it follows [CLAUDE.md](CLAUDE.md) and does steps 1, 2
and 4 for you.

## Caveats

The plan came from AI reviews and is untested. Probabilities, expected scores and
the H1 geometry were checked by hand only. Mentor answers and our own run results
win wherever they disagree with anything written here.
