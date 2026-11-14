# SESSION.md

The shared log for four people and their Claude sessions. Read it when you start.
Append to it when you reach a milestone or stop. Edit only your own row in the
table. Everything below "Session entries" is append-only, newest at the bottom.

## Current state

| ID | Workstream | Owner | Status | Last update |
| --- | --- | --- | --- | --- |
| A | Harness wiring | Mikael | starting: adding the organisers' starter kit to the repo | 2026-11-14 01:40 |
| B | Reference script and grader (H1) | itswinther | reference scores 1.0, 14 anchors as expected; NOW: writing agent-facing spec + command-line tools, then a first agent attempt outside Harbor | 2026-11-14 02:04 |
| C | Hold the Line spike | unassigned | not started | |
| D | Mentor questions, anchors, transcripts | unassigned | not started | |
| E | Analysis, demo and story | Yoseph | paused: Yoseph is not working overnight | 2026-11-14 01:40 |

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

- [ ] to A, from B, 01:40: say here when the starter kit is in the repo, and where the verifier expects the grader entry point and the reward file. Until then B assumes `tests/grade.py <base.stl> <door.stl> <assembly.json>` taking three absolute paths.
- [ ] to A, from B, 02:05: is a session for A running? Nothing from A is on `origin/main` yet. Please push the starter kit as its own first commit, even untouched, so B can read the verifier contract.
- [ ] to all, from B, 02:05: sessions started before 01:40 still follow the old CLAUDE.md. Tell your session to `git fetch origin && git rebase origin/main` and re-read CLAUDE.md.
- [ ] to whoever owns branch `claude/fervent-brown-cb0201` (`cala-tests/`, Cala API responses): is that meant for this repo? It is not on main.

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

- 2026-11-14 01:55 **Clarifications SPEC 0.1 leaves open.** Proposed by itswinther + Claude (B). Status: awaiting yes/no. The grader already uses these values; each is one line in `geometry/constants.py` marked INTERPRETATION, so a no is cheap.
  - `assembly.json` format: `{"board": [...], "lid": [...], "battery": [...], "door": [...]}`, each a list of 4x4 row-major matrices mapping the body from its supplied frame to the world. Board, lid and door are supplied in their final pose, so their last pose is the identity. The battery's own frame is x 0..48, y 0..30, z 0..7.5; its lead face is x = 0 and its top face z = 7.5.
  - Keep-outs are centred on the connector body's section and start at its outer face: J1 y 16.25..28.75, z -0.25..6.75, x -1.5..-21.5; J2 centre (y 12, z -2.5), x 72.5..92.5. "Grown by r" is a rectangle offset by r (square corners) for J1 and a larger circle for J2.
  - "Wall mid-plane" for K3/K4 is a fixed plane: x = -1.05 for J1, x = 72.55 for J2.
  - G5: the "1.0 sphere" is a diameter. "The cavity" is anywhere within 1.5 of board A or the battery. The two windows are plugged with the grown-by-3 sections for x <= 0 (J1) and x >= 70 (J2).
  - Contract rule 1: "at least 30 from its final pose" is measured at the body's vertex centroid. "Wholly outside the envelope" means zero intersection volume with the envelope box.
  - F1 is measured on a slice at z = -0.05, over the ring between dia 3.2 and dia 7. F4 is the exact minimum surface distance. F5 needs a 48 x 30 face horizontal in the final pose.
  - W1/W2 voxel margins: a wall of 1.6 always passes, the allowed deviation is 0.5 + one 0.2 voxel = 0.7. In exact maths a sharp 90-degree solid corner sits 0.586 from the opened shape, so the bare 0.5 in the spec would fail every sharp box corner.
  - Reference volume (base + door) is 15072.56 mm3, so the material budget is 17333.44 mm3.

## Ideas for later

Parked ideas. Not proposals: nothing here changes SPEC.md. Move one to "Proposed spec changes" to put it to the team.

- 2026-11-14 01:25 **"No screws allowed": every body clicks into place.** Proposed by Yoseph + Claude. Status: parked as an idea for later, not proposed to the team. Would need its own spec version if ever adopted.
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
  - **Review by B (itswinther + Claude), 01:35, by hand only:** as written it likely makes H1 easier, because a 20 mm tall wall section declared as an arm may flex 3.3 mm and the board needs only 1.7 mm to drop straight in; the lid hook has no room in x/y (the lid covers the whole footprint); rotating a rigid arm about its root edge intrudes about 0.3 mm3 into its own part. A rigid-only version (door on rails, R3 only) needs no arm code.

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

### 2026-11-14 01:40 | B + shared docs | itswinther + Claude
- Did: rewrote the communication part of CLAUDE.md. Reason: sessions were pushing to separate `claude/...` branches and could not see each other's SESSION.md. New rules: `origin/main` is the only shared channel, each session asks its human once for permission to push to `main`, re-reads SESSION.md before each new piece of work, and uses the new "Requests" section here for cross-workstream asks. Added workstream E to the CLAUDE.md table. Set owners: A Mikael (he adds the starter kit), B itswinther, E paused (Yoseph is not working overnight). C and D are unowned tonight.
- Verified by (command and result): `git branch -r --no-merged origin/main` listed `origin/claude/busy-davinci-idw73v` (commit b303740, "Park 'no screws allowed' under Ideas for later"), which is not on main.
- Not verified, or assumed: that every session's human allows pushes to `main`. The grader entry point in the Requests line is B's assumption until A confirms it.
- Files changed: CLAUDE.md, SESSION.md (owner rows A, B and E, Requests section, this entry). Touching rows A and E is outside my own row; done on itswinther's instruction.
- Need from others: A answers the request above. Someone merges b303740 or drops it.
- Next: B builds `geometry/`, the supplied bodies, the reference script and the grader against SPEC 0.1 unchanged.

### 2026-11-14 01:55 | B reference and grader | itswinther + Claude
- Did: built `geometry/` (constants, STL load, supplied bodies, contract rules, pose replay, voxel checks, all 5 gates and 19 checks, score), `tests/grade.py` (the grader), `solution/reference.py` (parametric reference: tub, two windows, four posts, two pegs, lap door, board path), and `tests/test_anchors.py` (14 anchors). SPEC.md is unchanged; what it leaves open is listed under Proposed spec changes.
- Verified by (command and result):
  - `python3 solution/reference.py OUT` printed `base volume 11816.57, door volume 3256.00, total 15072.57 mm3; poses {'board': 280, 'lid': 89, 'battery': 101, 'door': 101}`.
  - `cd tests && python3 -I grade.py OUT/base.stl OUT/door.stl OUT/assembly.json --reward OUT/reward.txt` printed all gates and checks true except M1 (reference volume was not yet set), in 6.0 s. After setting `REFERENCE_VOLUME`, the anchor run gives the reference S = 1.0000.
  - `python3 tests/test_anchors.py` (about 50 s): reference 1.0; do nothing, half-written file, NaN path, teleporting path, non-rigid pose 0; wall removed 0 (G5, K3); U-slot to rim 0 (G5); clash in final pose 0 (G3); lazy tub 0.2127; straight-down board path 0.3781 (A1 only); no pegs 0.4575 (F2 only); J2 window too narrow 0.4575 (K2 only); blind J2 pocket 0.3062 (A1, K2, W1).
  - Reference margins: F4 J2 clearance 0.5 (limit 0.4); K3 open area 89.5 of 130.5; K4 59.9 of 78.5; W1 and W2 deviation 0.49 of 0.7; F2 +X volume 2.77 mm3 (limit 0.2); every path replays with 0.0 mm3 intersection.
- Findings:
  - The reference board path differs from the internal note. It tilts 15 degrees, not 20 to 25, and there is no vertical drop: the board flattens to 1.2 degrees, slides back with its -X end 1.4 above the posts, then rotates the last 1.2 degrees onto the pegs. A vertical drop would need both closed windows to be taller.
  - A blind J2 pocket cannot fail K2 alone: it also blocks the board path (J2 pokes 0.7 past the outer wall during the slide). The anchor table's "blind pocket, about 0.46" row is replaced by "J2 window too narrow for the round plug", which does fail K2 only.
- Not verified, or assumed: nothing has run inside Harbor or a container. Worst-case grading time (200,000 triangles, 2,000 poses per body) is not measured; replay is one boolean per pose per placed body. A mesh that is manifold but self-intersecting is not fully normalised by the self-union. The per-check timeout uses SIGALRM, so it needs Linux and the main thread. The reward file path defaults to `/logs/verifier/reward.txt` and is a guess until A confirms it. No agent has attempted the task, so difficulty is unknown.
- Files changed: `geometry/`, `tests/`, `solution/`, `requirements.txt`, `.gitignore`, SESSION.md (row B, proposal, this entry).
- Need from others: A, the grader call is `python -I tests/grade.py /abs/base.stl /abs/door.stl /abs/assembly.json --reward FILE [--details FILE]`; it needs `geometry/` next to or one level above `grade.py` and the packages in `requirements.txt`. The MCP tools should import `geometry.core` and `geometry.contract` (`replay`, `check_contract`, `ivol`, `min_distance`, `section_x`), never `geometry.checks`. A human yes or no on the clarifications.
- Next: measure worst-case grading time, write the public spec text and task instruction for the agent, add the parameter-sweep anchors (rule 2 of the anchor suite).

### 2026-11-14 02:05 | B + repo housekeeping | itswinther + Claude
- Did: (1) applied by hand the content of Yoseph's stranded commit b303740 (branch `claude/busy-davinci-idw73v`): the "No screws allowed" write-up now sits under "Ideas for later", parked. A git merge would have duplicated the block because SESSION.md uses a union merge. That branch still shows as unmerged in git; its content is on main. (2) Corrected my own earlier timestamps: entries I had stamped 02:00 and 03:00 were written at about 01:40 and 01:55 Helsinki (`date -u` is the check; Helsinki is UTC+2). (3) Reviewed the project against the organisers' judging rubric; summary below.
- Verified by (command and result): `git branch -r --no-merged origin/main` lists `claude/busy-davinci-idw73v` (handled above) and `claude/fervent-brown-cb0201`. The second holds one commit, cfa6313 "Add raw Cala API coverage test responses", 26 JSON files under `cala-tests/`. It looks unrelated to this project and is not merged. `git log origin/main` shows no commit from workstream A yet and no starter kit in the repo.
- Rubric review (gap 30, meaningful difficulty 30, reward integrity 25, craft 15):
  - Gap: unknown. No agent has run. The reference was written in one pass by a Claude session that had the full spec and the hand-worked path hint, which is weak evidence that a frontier agent may also solve it. This is the largest open risk.
  - Meaningful difficulty: SPEC 0.1 was ambiguous in about ten places (see the clarifications under Proposed spec changes). If the agent-facing spec leaves any of them unstated, failures will come from withheld information, which the rubric scores as zero. The agent-facing spec and task instruction do not exist yet.
  - Reward integrity: do-nothing scores 0 and 14 anchors behave. Open holes: grading time for a large honest submission is unmeasured (a slow path check fails by timeout); self-intersecting meshes are not normalised; any gate failure gives exactly 0, so a near-complete design with one bad pose scores the same as doing nothing.
  - Craft: nothing runs in Harbor and there is no one-command evaluation.
- Not verified, or assumed: that the `cala-tests` branch is unrelated; I did not open the JSON files.
- Files changed: SESSION.md only.
- Need from others: see Requests.
- Next: write the agent-facing spec and a command-line version of the tools, then run a first agent attempt outside Harbor to measure the gap before anything else is built.

### 2026-11-14 02:04 | B first agent attempt (starting) | itswinther + Claude
- Did: starting now. Plan: write `environment/public/SPEC_PUBLIC.md` (agent-facing spec with every clarification stated) and `environment/tools_cli.py` (the measurement tools as a command line over `geometry.core` and `geometry.contract`), copy only those plus the supplied meshes into a clean folder, and give a fresh agent that folder and nothing else. This touches `environment/`, which is workstream A's folder; A has nothing there yet, and the MCP server can wrap the same functions.
- Verified by (command and result): nothing yet.
- Not verified, or assumed: the attempt runs outside Harbor with this session's model as the agent, so it is a first signal, not the judged setup.
- Files changed: SESSION.md.
- Need from others: nothing new.
- Next: report the agent's score, what it failed and why.
