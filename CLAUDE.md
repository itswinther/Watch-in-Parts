# CLAUDE.md

You are helping one of four teammates build an RL environment ("Board in a Box")
for the AfterQuery challenge at Junction 2026. Final submission is Sunday 15 Nov,
10:00 Helsinki time. Three other Claude sessions are working in this repo for the
other teammates at the same time. The files below are how you stay in step with
them.

- `README.md`  what the project is
- `SPEC.md`    the task, the checks and the score. Single source of truth.
- `SESSION.md` who owns what, what is done, what is decided, what is open

## At the start of every session

1. `git pull --rebase`
2. Read `SESSION.md`: the Current state table, Open questions, Decisions, and the
   last five entries.
3. Read the parts of `SPEC.md` your workstream touches.
4. Tell your human, in two or three lines, which workstream you think you are on
   and what you will do next. If the workstream is unassigned or unclear, ask.

## At every milestone, and before the session ends

1. Append one entry at the bottom of `SESSION.md` using the template there.
2. Update only your own row in the Current state table.
3. `git pull --rebase`, then commit and push. `SESSION.md` uses a union merge, so
   appended entries from several sessions do not conflict.

Write entries for a reader with no context: say what you ran and what came back.

## Rules that keep four sessions consistent

**Spec changes.** Do not change anything in `SPEC.md` on your own: not a
dimension, tolerance, check definition, weight or contract rule. Add a line under
"Proposed spec changes" in `SESSION.md` and tell your human. Once a human says
yes, edit `SPEC.md`, bump its version line, and log it under Decisions. The tools,
the grader and the reference must always agree with the same spec version.

**One geometry module.** The MCP tools and the grader import the same module in
`geometry/` and the same constants file. Never copy a tolerance into a second
place.

**What the agent under test may see.** Only the instruction, the supplied meshes,
the public spec and the tool outputs. Tool and submit messages state geometry
facts and format errors only: no check IDs, no requirement names, no pass/fail on
a requirement. Never copy `solution/`, `anchors/`, `tests/`, `CLAUDE.md`,
`SESSION.md` or `.git` into any image the agent can reach.

**Grader.** It runs in Harbor's separate verifier. It opens exactly three files
by absolute path (`base.stl`, `door.stl`, `assembly.json`), never a folder, and
never runs submitted code. Run it from its own directory with `python -I`. It
writes reward 0 first and overwrites it at the end. Each check runs in its own
try block; an exception, a timeout or a non-finite number fails that check.

**Done means run.** Do not report something as working unless you ran it. Log the
exact command and what it printed. If you could not verify something, say so in
your entry under "Not verified".

**Starter kit wins.** The organisers' harness docs and scoring skeleton override
public Harbor docs. When you find a difference, log it under Decisions.

**Git.** Small commits on `main`, `git pull --rebase` before every push, no
force-push. Stay inside your workstream's folders; if you must touch another
workstream's file, say so in your entry. Never commit API keys.

## Workstreams

| ID | Workstream | Folders |
| --- | --- | --- |
| A | Harness wiring: starter kit, MCP server registration, separate verifier, one command | `environment/`, task config |
| B | Reference script and grader for instance H1 | `solution/`, `geometry/`, `tests/` |
| C | Hold the Line fallback spike | `holdtheline/` |
| D | Mentor questions, anchor suite, transcripts | `anchors/`, `SESSION.md` |

## Decisions already made

Raise these with your human before reopening them.

- Submissions are STL plus a JSON path file. No STEP.
- Agent-declared assembly paths, replayed pose by pose. No fixed insertion
  directions, no interpolation.
- Closure is a gate. Assembly paths are weighted checks, not gates.
- Material is a pass/fail check, not a multiplier.
- The reference run is one parametric script replayed by Harbor's oracle agent.
- Cut from scope: the design-revision step, the support-free printing rule, the
  datasheet lookup step, the small-model training tiebreaker.
- Two ideas are spiked in parallel; the choice is made Saturday 09:00 from
  transcripts. Latest switch is Saturday 16:00.

## Unknown, do not assume

The judged model and effort setting, per-trial timeout, rerun time budget, credit
grant, how the stop-early baseline is defined, which environment provider the
judges use, and whether the organisers' OpenCode registers MCP servers declared
in `task.toml`. Answers go under Open questions in `SESSION.md`.

## Internal note for workstream B

The reference design is expected to tilt the board in at 20 to 25 degrees with J2
entering its window first, slide toward +X, flatten, slide back toward -X, and
drop onto two locating pegs; the door laps on the outside of the floor. This was
worked out by hand and is not confirmed. If the reference cannot pass, report it
before relaxing anything.
