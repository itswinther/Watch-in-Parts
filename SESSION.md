# SESSION.md

The shared log for four people and their Claude sessions. Read it when you start.
Append to it when you reach a milestone or stop. Edit only your own row in the
table. Everything below "Session entries" is append-only, newest at the bottom.

## Current state

| ID | Workstream | Owner | Status | Last update |
| --- | --- | --- | --- | --- |
| A | Harness wiring | Mikael | starting: adding the organisers' starter kit to the repo | 2026-11-14 02:00 |
| B | Reference script and grader (H1) | itswinther | starting | 2026-11-14 02:00 |
| C | Hold the Line spike | unassigned | not started | |
| D | Mentor questions, anchors, transcripts | unassigned | not started | |
| E | Analysis, demo and story | Yoseph | paused: Yoseph is not working overnight | 2026-11-14 02:00 |

Spec version in use: 0.1

## Deadlines (Helsinki time)

- Sat 03:00 harness wired end to end
- Sat 07:00 both spikes done
- Sat 09:00 decision between the two ideas
- Sat 16:00 latest switch
- Sat 22:00 build-out done, anchor suite passing
- Sun 03:00 full runs and failure analysis
- Sun 09:00 README and demo ready
- Sun 10:00 final submission

## Requests

One line per request to another workstream. The addressee answers on the same
line and ticks it. Format: `- [ ] to B, from A, HH:MM: what you need`.

- [ ] to A, from B, 02:00: say here when the starter kit is in the repo, and where the verifier expects the grader entry point and the reward file. Until then B assumes `tests/grade.py <base.stl> <door.stl> <assembly.json>` taking three absolute paths.

## Open questions

Write the answer and who gave it next to the question, then tick it.

- [ ] Which model and effort setting do the judges run?
- [ ] Per-trial timeout?
- [ ] Wall-clock budget for the judges' rerun?
- [ ] Can the agent see images?
- [ ] How is the stop-early baseline defined?
- [ ] How large is the model-credit grant?
- [ ] Which environment provider does the rerun use? (decides compose sidecar or in-container MCP server)
- [ ] Does the organisers' OpenCode register MCP servers declared in task.toml?
- [ ] When do the AfterQuery demo and rerun happen?
- [ ] What does the scoring skeleton record when the verifier is killed or times out?
- [ ] Can agent network access be limited to the model API?

## Decisions

Append one line per decision: time, decision, who agreed.

- 2026-11-14 00:50 Working plan is the second review, updated version. SPEC.md 0.1 is taken from it.

## Proposed spec changes

Append here. A human has to say yes before SPEC.md changes.

- 2026-11-14 01:25 **"No screws allowed": every body clicks into place.** Proposed by Yoseph + Claude. Status: awaiting team yes/no. Would become SPEC 0.2.
  - **Why:** SPEC 0.1 says "screws are out of scope, parts are assumed screwed down", so nothing holds the board, lid or door. Tool-free snap-fit assembly is a real design-for-assembly rule, gives a better story for judges, and adds a constraint that interacts with the ones we already have (see "Interactions").
  - **Replaces** the Limits line "Screws are out of scope ... no check tests retention against a pull" with: "No fasteners, glue or press-fit pins. Board A, lid and door must each be held by printed geometry. The battery is held by the door (F3, unchanged)."
  - **How a snap is modelled while staying rigid-body (the hard part).** A snap arm has to bend while it is inserted, but the replay only moves rigid bodies. So the agent declares its snap arms in `assembly.json`, and gives a bend angle per pose:
    `"arms": [{"name": "lid_px", "part": "base", "box": [[x0,y0,z0],[x1,y1,z1]], "root": "-z", "bend": "+x"}]`, and each pose may carry `"arms": {"lid_px": 0.04}` (radians).
    The grader takes the printed material inside `box` as a separate rigid piece. At each pose it rotates that piece about the box's root edge by the declared angle, then applies the normal 0.2 mm3 intersection rule against everything else, the rest of its own part included. This is the pseudo-rigid-body model, simplified to a pivot at the root, which is conservative.
  - **What the grader checks on each arm (the agent's declaration is never trusted):**
    1. Material inside the box touches the rest of the part only across the root face. Voxel test, 0.2 voxels, so a gap needs to be at least 0.4 wide to count.
    2. Strain: the grader measures t at the root and L along the box itself. With tip deflection y = L·sin(angle), max strain is 3·t·y / (2·L²), and it must stay at or below 2.0 % (PLA, assumed). For example, t 1.6 with L 10 allows y of 0.83 mm; L 8 allows only 0.53.
  - **Contract additions (format errors fail G4):** at most 8 arms; arm boxes may not overlap; arms only on printed parts; every angle is 0 in the final pose of every body; a change in angle moves the arm tip at most 0.5 per step (same as rule 3).
  - **Where a broken arm counts:** over-strain or a non-free arm fails the path check (A1 to A4) of the body that was moving at that pose, not a gate. This keeps the decision "paths are weighted checks, not gates".
  - **New checks** (each weight 1; the spec goes from 19 checks / weight 23 to 22 checks / weight 26):
    - R1 Board retained: moving board A 0.6 along +Z makes its bare PCB intersect printed parts by more than 0.2 mm3.
    - R2 Lid retained: moving the lid 0.5 along +Z intersects the base by more than 0.2 mm3.
    - R3 Door retained: moving the door 0.5 along -Z intersects the base by more than 0.2 mm3.
  - **Envelope:** the lid is a supplied flat plate whose top is at z 15.5, so a hook over it needs z max to go from 12.5 to 17.25 (15.5 + 1.6 lip + 0.15).
  - **Interactions that make it harder:** the gap around an arm has to be at least 0.4 to count as free (check 1) but below 1.0 or shielded, or G5's 1.0 sphere gets through; arms must be at least 1.6 thick (W1) yet long enough to flex; board hooks must stay 0.4 from J1, J2 and C1 (F4) and must not catch during the tilt-and-slide path; the door latch must clear the battery (A3, F5).
  - **Anchors to add:** pegs but no hooks (fails R1 to R3); an arm declared over a solid wall (fails A-path by check 1); a stubby arm bent too far (fails A-path by strain); hooks that never deflect (fails A-path by intersection).
  - **Tools:** `sweep` also returns the peak strain per arm and its pose index (a geometry fact, no pass/fail). `get_spec` publishes the strain limit and the arm format.
  - **Cost:** B adds arm extraction, rotation and strain to the shared geometry module, plus three latch sets in the reference, roughly half a day. A adds an `arms` passthrough in `sweep`. D adds four anchors.
  - **Timing:** nothing is built yet, and arms change the core of the path replay. So the cheapest moment to decide is before B writes the replay code, which is tonight. If the team would rather not risk the Sat 07:00 spike, the fallback is to keep it as the difficulty lever for Sat 09:00, used if H1 turns out too easy for the judged agent.
  - **Not verified:** that a reference with latches can pass every gate and check; the 2.0 % strain limit for PLA; that 0.2 voxels resolve the arm gap reliably.

## Session entries

Template:

```
### YYYY-MM-DD HH:MM | workstream | human name + Claude
- Did:
- Verified by (command and result):
- Not verified, or assumed:
- Files changed:
- Need from others:
- Next:
```

### 2026-11-14 00:50 | setup | Claude
- Did: created the repo with README.md, CLAUDE.md, SESSION.md, SPEC.md.
- Verified by (command and result): nothing to run yet.
- Not verified, or assumed: every number in SPEC.md was checked by hand only. No code exists. The spike has not run.
- Files changed: all four, new.
- Need from others: assign owners in the table above. Fill in mentor answers.
- Next: workstream A starts from the organisers' starter kit.

### 2026-11-14 01:25 | none assigned (spec proposal) | Yoseph + Claude
- Did: read README.md, SPEC.md 0.1, SESSION.md and CLAUDE.md. The repo holds only these docs; there is no code and no workstream owner yet. Wrote the "No screws allowed" proposal under Proposed spec changes. Snap arms are declared in assembly.json and bent rigidly about their root at each pose, under a strain limit of 2.0 %. Added retention checks R1 to R3 (board, lid, door), and raised envelope z max to 17.25.
- Verified by (command and result): `python3 -c` gave cantilever allowed tip deflection y = 2·eps·L²/(3·t) for t 1.6 and eps 0.02: L 8 -> 0.533, L 10 -> 0.833, L 12 -> 1.2. Nothing else can be run yet.
- Not verified, or assumed: the reference can pass with latches; the PLA strain limit of 2.0 %; that 0.2 voxels resolve a 0.4 arm gap. SPEC.md is unchanged.
- Files changed: SESSION.md only (Proposed spec changes, this entry).
- Need from others: a yes or no from the team on the proposal before B starts the path-replay code.
- Next: if yes, edit SPEC.md to 0.2 and log it under Decisions. If no, leave SPEC 0.1 as it is.

### 2026-11-14 01:35 | E analysis, demo, story | Yoseph + Claude
- Did: Yoseph owns analysis, demo and story. CLAUDE.md lists no workstream for that, so I added row E to the Current state table. The folders and the CLAUDE.md table are not changed. Pushed the "no screws allowed" proposal to main at Yoseph's request, so the other sessions see it.
- Verified by (command and result): `git fetch origin main` showed main still at ddf8bfa before the push.
- Not verified, or assumed: that the team accepts an E row. If not, fold it into D.
- Files changed: SESSION.md (row E, this entry).
- Need from others: a yes or no on the no-screws proposal (Proposed spec changes) before B writes the path-replay code.
- Next: draft the demo story and the analysis plan (which numbers and transcripts we show).

### 2026-11-14 02:00 | B + shared docs | itswinther + Claude
- Did: rewrote the communication part of CLAUDE.md. Reason: sessions were pushing to separate `claude/...` branches and could not see each other's SESSION.md. New rules: `origin/main` is the only shared channel, each session asks its human once for permission to push to `main`, re-reads SESSION.md before each new piece of work, and uses the new "Requests" section here for cross-workstream asks. Added workstream E to the CLAUDE.md table. Set owners: A Mikael (he adds the starter kit), B itswinther, E paused (Yoseph is not working overnight). C and D are unowned tonight.
- Verified by (command and result): `git branch -r --no-merged origin/main` listed `origin/claude/busy-davinci-idw73v` (commit b303740, "Park 'no screws allowed' under Ideas for later"), which is not on main.
- Not verified, or assumed: that every session's human allows pushes to `main`. The grader entry point in the Requests line is B's assumption until A confirms it.
- Files changed: CLAUDE.md, SESSION.md (owner rows A, B and E, Requests section, this entry). Touching rows A and E is outside my own row; done on itswinther's instruction.
- Need from others: A answers the request above. Someone merges b303740 or drops it.
- Next: B builds `geometry/`, the supplied bodies, the reference script and the grader against SPEC 0.1 unchanged.
