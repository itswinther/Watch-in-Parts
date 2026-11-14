# SESSION.md

The shared log for four people and their Claude sessions. Read it when you start.
Append to it when you reach a milestone or stop. Edit only your own row in the
table. Everything below "Session entries" is append-only, newest at the bottom.

## Current state

| ID | Workstream | Owner | Status | Last update |
| --- | --- | --- | --- | --- |
| A | Harness wiring | Mikael | Harbor + Codex (GPT-6.1-sol) running sandboxed on Mikael's Mac; network locked to the model only, separate verifier. Five-step watch task: no gap (3x 1.0). Regulation task with hidden physics in a sealed sidecar: runs in progress. See 05:10 entry | 2026-11-14 05:10 |
| B | Reference script and grader | itswinther | Single-stage watch: Fable, Opus and Sonnet all 1.0. Built a three-stage watch task (design, add a 24-hour hand to a frozen design, assemble) with the test code withheld; three clean chains running since 04:12 | 2026-11-14 04:13 |
| C | Hold the Line spike | unassigned | not started | |
| D | Mentor questions, anchors, transcripts | unassigned | not started | |
| E | Analysis, demo and story | Yoseph | paused: Yoseph is not working overnight | 2026-11-14 01:40 |

Spec version in use: 0.3 (Moving Day, instance flat-1)

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

- [x] to A, from B, 01:40: say here when the starter kit is in the repo, and where the verifier expects the grader entry point and the reward file. Until then B assumes `tests/grade.py <base.stl> <door.stl> <assembly.json>` taking three absolute paths. **A, 02:20: there is no starter kit and no scoring skeleton. The organisers' only contract is a plain Harbor task whose verifier writes one number in 0..1 to `/logs/verifier/reward.txt` (your guess was right). Harbor runs `tests/test.sh`; A will write that to call `grade.py` with your three-path signature, so keep it.**
- [x] to A, from B, 02:05: is a session for A running? Nothing from A is on `origin/main` yet. Please push the starter kit as its own first commit, even untouched, so B can read the verifier contract. **A, 02:20: yes, running since about 02:00 with push rights to main. Nothing to push as a starter kit; the organiser message is quoted in the 02:20 entry.**
- [ ] to all, from B, 02:05: sessions started before 01:40 still follow the old CLAUDE.md. Tell your session to `git fetch origin && git rebase origin/main` and re-read CLAUDE.md.
- [ ] to whoever owns branch `claude/fervent-brown-cb0201` (`cala-tests/`, Cala API responses): is that meant for this repo? It is not on main.
- [ ] to Abhishek (watch idea), from B, 2026-11-14 03:42: itswinther has made the mechanical watch the main idea. B is building the first runnable version now in `geometry/watch.py`, `tests/grade_watch.py`, `solution/reference_watch.py`, `environment/tools_watch.py`. Please do not build the same pieces; if you have a barrel mesh, tooth numbers or a brief already, push them and say so here.
- [x] to B (and Abhishek), from A, 2026-11-14 04:00: before building the watch further, read `spikes/README.md` and `spikes/gear_train/`. A fully specified watch gear train (exact rates, centre distances from tooth counts, layered packing in a round plate, balance keep-out) was solved by all three models: Fable 1.0, Opus 1.0, Sonnet 0.92, each by writing an exhaustive search. Your version differs in two ways that may matter: a minimal brief where the hand rates are unstated, and a rotating replay (jam, engagement, drive). Those are the untested parts; a first clean run on a stripped brief would show quickly whether they create a gap. Also: with no torque limit the power reserve objective is trivially maxed (6.5 x 140/7 = 130 h). **B, 03:52: read. My version is exactly those two untested parts: the brief leaves the hand speeds, direction and shared hour-minute axis unstated, and the agent must submit real meshing gears as STL that the grader turns (jam, engagement, drive). There is no power-reserve term. Three clean runs (Fable, Opus, Sonnet) started at 03:47; results will be in my next entry. I am not building further until they are in.**

## Open questions

Write the answer and who gave it next to the question, then tick it.

- [ ] Which model and effort setting do the judges run? (Partly answered 02:20: the organisers "urge" OpenCode and give the example `harbor run -p ./my-task -a opencode -m [provider/model]`; the model is not named, and credits are Google/OpenAI/Modal, so we choose what we benchmark on.)
- [ ] Per-trial timeout?
- [ ] Wall-clock budget for the judges' rerun?
- [ ] Can the agent see images?
- [ ] How is the stop-early baseline defined?
- [x] How large is the model-credit grant? **None. Organiser message (Mikael, 02:20): AfterQuery gives no inference credits; use the Google, OpenAI and Modal sponsor credits.**
- [ ] Which environment provider does the rerun use? (decides compose sidecar or in-container MCP server)
- [x] Does the organisers' OpenCode register MCP servers declared in task.toml? **Yes, per Harbor source v0.26.0 (`src/harbor/agents/installed/opencode.py`, `_build_register_config_command`): it writes `[[environment.mcp_servers]]` into OpenCode's config, stdio as a local command or HTTP as a remote URL. Read in source by A, not yet seen in a transcript. There is no organiser-specific OpenCode build.**
- [ ] When do the AfterQuery demo and rerun happen?
- [x] What does the scoring skeleton record when the verifier is killed or times out? **There is no scoring skeleton. What plain Harbor records on a verifier timeout is still untested (A will test).**
- [x] Can agent network access be limited to the model API? **Yes in Harbor's task config: `[environment] network_mode = "allowlist"` with `allowed_hosts`. From the Harbor docs, not yet run by A.**
- [ ] H1 scored 1.0 on the first agent attempt (02:15). Do we harden Board in a Box, or move weight to Hold the Line? Needs a human answer before more is built.

## Decisions

Append one line per decision: time, decision, who agreed.

- 2026-11-14 00:50 Working plan is the second review, updated version. SPEC.md 0.1 is taken from it.
- 2026-11-14 02:20 Organiser contract replaces the "starter kit wins" rule: the environment is a plain Harbor task (`instruction.md`, `task.toml`, `environment/Dockerfile`, `tests/`, `solution/`), run as `harbor run -p ./my-task -a opencode -m provider/model`, reward is one number 0..1 in `/logs/verifier/reward.txt`. Submission also needs at least one Harbor run log with its score and a short README. Source: organiser message relayed by Mikael.
- 2026-11-14 02:49 H1 is retired as the judged instance: six agent attempts, three models, all scored 1.0. itswinther asked B to build instance H2 with four changes: continuous score against an optimised reference, agent-chosen placement of several bodies, agent-chosen assembly order, and the H1 loopholes closed. Agreed: itswinther.
- 2026-11-14 02:58 SPEC.md is version 0.2: the judged instance is H2, specified in `environment/public/SPEC_H2.md`. Agreed: itswinther (asked for the four changes).
- 2026-11-14 02:58 Interface for A (H2): the grader call is `python -I tests/grade_h2.py /abs/base.stl /abs/lid.stl /abs/assembly.json --reward FILE [--details FILE]`; the three artifacts are `base.stl`, `lid.stl`, `assembly.json` (the door is gone). `python environment/make_bundle.py DIR` writes everything the agent may see. B says yes to running the tools inside the agent container: the bundle holds no weights, gate list, check code or reference.
- 2026-11-14 03:05 Board in a Box is scrapped as the challenge, both H1 and H2. Reason: clean agents score 1.0 on H1 and 0.97 on H2 within five minutes. The team will pick a new idea with a real gap. Decided: itswinther. The code stays in the repo for now; nothing depends on it.
- 2026-11-14 03:14 New challenge to test: "Moving Day". Fixed apartment mesh and N furniture meshes with given final poses; the agent submits one JSON with the carry-in order and a rigid pose-by-pose path per piece; score 0.5 p^2 + 0.5 [all delivered]. Nothing is designed, so there are no design loopholes. Decided: itswinther (other teammates are testing other ideas in parallel). B builds the hardest instance it can and measures it with clean agents before anything else is built.
- 2026-11-14 03:22 Interface for A (Moving Day): one artifact, `plan.json`. Grader call: `python -I tests/grade_md.py /abs/plan.json [--instance flat-1] --reward FILE [--details FILE]`. `python environment/make_bundle_md.py DIR` writes everything the agent may see; the tools are `tools/tools_md.py` and the agent may import `tools/geometry`. Units are centimetres.
- 2026-11-14 03:33 Moving Day stays in the back pocket: built and measured, but it shows no real gap (Fable 1.0, Opus 1.0). It is not the chosen challenge. Decided: itswinther.
- 2026-11-14 03:42 The mechanical watch gear train (write-up in `MECHANICAL_WATCH_IDEA.md`) is now the main idea. Moving Day, H2 and H1 are backups. Decided: itswinther.
- 2026-11-14 03:51 Interface for A (watch task): the artifact is a folder holding `movement.json` and `parts/<name>.stl`. Grader call: `python -I tests/grade_watch.py /abs/folder --reward FILE [--details FILE]`; it opens only the files `movement.json` names. `python environment/make_bundle_watch.py DIR` writes everything the agent may see. Grading the reference takes about 35 s.
- 2026-11-14 03:51 Choices B made while building the watch task, different from or beyond the write-up, open to a human no: (1) all arbors are parallel to z and this is stated; (2) the size limit is stated (radius 23, height 16), not hidden, because a hidden number we chose would be withheld information; (3) only the hour and minute hands must share an axis, since real watches often have a small seconds hand elsewhere; (4) the hand speeds, clockwise direction and that shared axis are the only unstated requirements; (5) the barrel is 96 teeth, module 0.2, 25 degree pressure angle, all stated; (6) the agent is not given a gear maker; (7) "held" accepts another mobile as the thing that holds a mobile, because an hour wheel rides on the centre arbor in real watches; (8) there is no minimum-feature (printability) check yet.
- 2026-11-14 04:13 Watch task, two changes agreed by itswinther: (1) three stages with frozen hand-over, each stage a fresh agent conversation: design; add a 24-hour hand to a frozen design; give an assembly order and paths for the frozen result. (2) For these runs the agent gets the full written contract, the raw geometry kernel and a format-only submit, but no test code and no measuring tools. This reverses the earlier "tools measure everything" principle on purpose; every graded number is still stated in the spec, except what a watch hand does.
- 2026-11-14 04:13 Interface for A (staged watch): `python -I tests/grade_watch.py /abs/folder --stage N [--prev /abs/previous_stage_folder] --reward FILE`. Stage 3 adds `assembly.json` to the folder. `python environment/make_bundle_watch.py DIR --stage N [--prev FOLDER] --tools no` writes what the agent may see. `environment/run_clean_chain.sh RUN_DIR MODEL` runs the three stages headless; `python tests/grade_chain.py RUN_DIR` grades them.

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
- 2026-11-14 03:30 **Mechanical watch gear train: a new challenge, as an alternative to Moving Day.** Proposed by Abhishek + Claude. Status: parked as an idea, nothing built or run. Full write-up in `MECHANICAL_WATCH_IDEA.md`. In short: the agent gets a minimal brief ("design the gear train of a mechanical watch, driven by this barrel turning once per 8 h") and must infer the unstated but universal rules (hour 1 per 12 h, minute 1 per h, seconds 1 per min, clockwise, coaxial hands). The grader checks exact ratios from declared tooth counts, then rotates the train with the existing rigid-pose replay and overlap test (no jam, still engaged, teeth drive, hands clear). Estimated 1.5 to 2 person-days; the reference movement is the critical path.

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

### 2026-11-14 02:15 | B first agent attempt (result) | itswinther + Claude
- Did: gave a fresh agent (a subagent of this session, same model) a clean folder holding only `INSTRUCTION.md`, `SPEC_PUBLIC.md`, the supplied meshes and the tools (`tools_cli.py` plus `geometry/` without `checks.py`). Then graded what it submitted. Also measured grading time on a large submission.
- Verified by (command and result):
  - `cd tests && python3 -I grade.py .../agent1/submission/base.stl .../door.stl .../assembly.json` printed `"reward": 1.0, "p": 1.0, "strict": true`, all 5 gates and 19 checks true.
  - The agent took 4 min 54 s, 7 tool calls, about 110,000 tokens, one 66-line build script, one submission. It did not iterate: the first build passed every measurement it ran.
  - Its design matches the reference in every main decision: raised floor with the door lapped outside, tilt 16 degrees, slide +X, flatten, slide -X, drop 2.0. It located the board in +X with a block on the wall instead of pegs.
  - Grading time: a 123,392-triangle base and 19,200-triangle door with 2,000 poses per body graded in 16.3 s and scored 1.0.
- Finding: H1 as specified shows no gap against this model. The task is a fully stated numeric constraint problem with tools that measure every constraint, and the agent solved it in one pass.
- Not verified, or assumed:
  - The run was contaminated: the harness injects the repo's CLAUDE.md into subagents, and CLAUDE.md contains the "Internal note for workstream B" that describes the board path. The agent reported this itself. An uninformed agent might do worse, but one sentence of hint does not explain a 5-minute perfect score.
  - The judged model and harness are unknown; this was not run in Harbor or OpenCode. One run only.
- Issues the agent reported in the tools and spec: `constants.py` in the tools bundle shows check IDs, weights and the reference volume, and comments name `SESSION.md` and `solution/reference.py`; the tools help mentions a `--battery-pose` option that does not exist; `distance` stops at 5.0 and the spec does not say so; no tool gives the ring area or the lead distance directly; nothing requires the base to be a tub or the door to be retained.
- Files changed: `transcripts/agent1/` (the agent's script, its three submitted files, grader details), SESSION.md.
- Need from others: a human decision. Options: (a) rerun clean after removing the internal note from CLAUDE.md, to confirm; (b) make H1 harder; (c) give Hold the Line an owner now. See Open questions.
- Next: nothing built until the decision.

### 2026-11-14 02:20 | A harness wiring | Mikael + Claude
- Did: started workstream A. Relaying the organisers' "Required Stack" message, which the team has not seen. Read Harbor's public docs and source for the points A depends on. Installed tooling on Mikael's Mac.
- Organiser message, in short:
  - Framework is Harbor (github.com/laude-institute/harbor). The environment is a Harbor task: `instruction.md`, `task.toml`, `environment/Dockerfile`, `tests/`, `solution/`.
  - Harness: they "urge" OpenCode: `harbor run -p ./my-task -a opencode -m [provider/model]`.
  - Reward: the verifier writes one score between 0 and 1 to `/logs/verifier/reward.txt`. Partial credit is welcome.
  - Before submitting: at least one Harbor run log with its score; a short README (what the agent does, why it is hard, how it is scored; they warn AI-written READMEs may communicate poorly); playthroughs encouraged in the demo video.
  - AfterQuery provides NO inference credits. Use the Google, OpenAI and Modal sponsor credits.
  - "What we're looking for: super cool simulations, environments, and some post-training experiments." Post-training is the tiebreaker and is now named outright; we cut it from scope.
  - No starter kit or scoring skeleton is mentioned anywhere. CLAUDE.md's "Starter kit wins" rule and several open questions assumed one.
- Verified by (command and result):
  - `uv tool install harbor` then `harbor --version` printed `0.25.0`. `harbor agent list` includes `oracle`, `nop`, `opencode`.
  - Harbor source cloned at v0.26.0. `grep -n -i mcp src/harbor/agents/installed/opencode.py` shows the agent writing task-declared MCP servers into OpenCode's config (lines 839 to 858, 927 to 929).
  - `examples/tasks/sidecar-artifacts/task.toml` shows `environment_mode = "separate"` and artifacts declared one file at a time, optionally from a named sidecar service.
  - `brew install --cask docker` reports Docker Desktop installed. Not yet started, no container run.
- Not verified, or assumed: nothing has run in Harbor yet. Harbor docs say multi-step tasks start a fresh agent conversation per step, compose sidecars run on Modal only through Docker-in-Docker, and the default verifier is shared (separate is opt-in); all read, none run.
- Proposal from A, needs a human yes (interface between A and B): run the MCP tool server INSIDE the agent's container over stdio, not as a compose sidecar. Reason: SPEC 0.1 never says how a sidecar reads a mesh the agent just wrote (separate filesystem, and a model cannot pass an STL as a tool argument); in-container needs no compose file, so it also runs on Modal. Cost: the agent can read the tool source, so the tools bundle must hold only geometry primitives. B's 02:15 entry says `constants.py` in the bundle currently exposes check IDs, weights and the reference volume; that file needs a public/private split before this is safe.
- On B's 02:15 result (H1 scored 1.0 in 5 minutes): A's work is the same for either idea, so A continues. Note for the decision: the organisers no longer supply the model, so "the judged agent" is whatever we can run on Google/OpenAI credits through OpenCode, which may be weaker or stronger than the subagent B tested. A clean rerun in the real harness is the measurement that counts.
- Files changed: SESSION.md (row A, two requests answered, five open questions answered, one decision line, this entry).
- Need from others: B, a yes or no on in-container tools, and the `constants.py` split. Anyone with sponsor credits: an OpenAI or Google API key for the first OpenCode run (do not commit it).
- Next: build the Harbor task (`task.toml` with separate verifier and three single-file artifacts, `environment/Dockerfile`, `tests/test.sh`, `solution/solve.sh`), then run `oracle` (expect 1.0) and `nop` (expect 0).

### 2026-11-14 02:27 | B agent attempts 2 to 6 (result) | itswinther + Claude
- Did: removed the board-path note from CLAUDE.md, then ran five more attempts at H1 with the same instruction, public spec, meshes and tools. Attempts 2 to 4 were subagents of this session. Attempts 5 and 6 were started with the headless command line (`claude -p ... --model M --permission-mode acceptEdits --output-format stream-json`) from a folder outside the repo.
- Verified by (command and result): each submission graded with `cd tests && python3 -I grade.py <three absolute paths>`.

  | Attempt | Model | Context | Score | Time | Submissions | Notable |
  | --- | --- | --- | --- | --- | --- | --- |
  | 1 | Fable 5.2 | saw the hint | 1.0 | 4 min 54 s | 1 | floor door, tilt 16 degrees |
  | 2 | Fable 5.2 | saw the hint | 1.0 | 4 min 36 s | 1 | battery through a side door |
  | 3 | Opus | saw the hint | 1.0 | 7 min 56 s | 1 | battery above the board, floating 1.7 above the PCB |
  | 4 | Sonnet | saw the hint | 1.0 | 5 min 35 s | 1 | two colliding tilts fixed with `sweep` before submitting |
  | 5 | Fable 5.2 | clean | 1.0 | 4 min 59 s, 6 turns, $1.68 | 1 | tilt 15 degrees, floor door |
  | 6 | Sonnet 5.5 | clean | 1.0 | 4 min 40 s, 7 turns, $0.51 | 1 | no tilt at all: base is a floorless ring, the door is the whole bottom, the board goes straight up from below |

  For attempt 6 I checked first that a command-line agent started outside the repo has no project instructions: `claude -p "what project instructions are in your context, or NONE"` printed `NONE`.
- Findings:
  - No gap. The two clean runs scored 1.0, so the hint was not what made it easy.
  - Attempts 2 to 4 were still contaminated: the harness cached CLAUDE.md at session start, so removing the note from the file did not remove it from subagents. Each of them quoted the note back.
  - Attempt 6 avoids the intended difficulty completely. Nothing requires the base to have a floor or the board to enter from above, so the wall below each connector opening can belong to the door and the board needs no tilt.
  - Attempt 3 shows the public spec never says the battery sits below the board, and nothing checks that the battery is supported from below.
  - No attempt needed a second submission. The measuring tools let the agent confirm every requirement before submitting.
- Not verified, or assumed: the judged model, harness and time limit are unknown; none of this ran in Harbor or OpenCode.
- Files changed: CLAUDE.md (internal note removed), `environment/tools_cli.py` (help text), `transcripts/agent1` to `agent6` (submitted files, agent scripts, grader details; full transcripts for 5 and 6), SESSION.md.
- Need from others: a human decision on the open question "harden Board in a Box or move to Hold the Line".
- Next: nothing built until that decision.

### 2026-11-14 02:49 | B instance H2 (starting) | itswinther + Claude
- Did: starting H2 on itswinther's instruction. Design: supplied bodies are board A (unchanged), a second board B with a card slot, the battery and a speaker. The agent chooses every body's final pose and the insertion order, and makes `base.stl` plus a flat `lid.stl`. Score = gates x (0.3 p^2 + 0.7 q if every check passes), where q falls linearly with the bounding-box volume of the printed parts, 1 at the reference volume. Code goes in `geometry/h2.py`, `solution/reference_h2.py`, `tests/grade_h2.py`; H1 files stay as they are.
- Verified by (command and result): nothing yet.
- Not verified, or assumed: whether H2 produces a gap. No agent runs until itswinther says so.
- Files changed: SESSION.md.
- Need from others: nothing.
- Next: report when the reference and anchors pass.

### 2026-11-14 02:58 | B instance H2 (built) | itswinther + Claude
- Did: built instance H2. Supplied bodies: board A (unchanged), board B (38 x 27.5 PCB with shield, card slot J3 and inductor), battery, speaker. The agent chooses every final pose and the insertion order, and makes `base.stl` and a flat 2.0 `lid.stl`. Four gates (files, final pose, path format, enclosed) and 17 checks (weight 20). Score: 0 if a gate fails; 0.3 p^2 if a check fails; otherwise 0.3 + 0.7 x size, where size falls linearly from 1 at the reference bounding-box volume (81,343.3 mm3) to 0 at 95,000 mm3. H1 loopholes closed: the second part must be a flat plate, so the base needs a floor and closed windows; every body must rest on something; the door is gone.
- New files: `geometry/h2_public.py` (bodies, public numbers, measurements), `geometry/h2_checks.py` (grader only), `tests/grade_h2.py`, `tests/test_anchors_h2.py`, `solution/reference_h2.py`, `environment/tools_h2.py`, `environment/make_bundle.py`, `environment/public/SPEC_H2.md`, `environment/public/INSTRUCTION_H2.md`. SPEC.md header now points to H2.
- Verified by (command and result):
  - `python3 solution/reference_h2.py OUT` printed `bounding box [74.85, 48.3, 22.5], volume 81343.2 mm3; poses {'B': 130, 'speaker': 126, 'A': 280, 'battery': 114, 'lid': 89}`.
  - `cd tests && python3 -I grade_h2.py OUT/base.stl OUT/lid.stl OUT/assembly.json --reward R` printed reward 1.0, p 1.0, size_term 1.0, all gates and checks true.
  - `python3 tests/test_anchors_h2.py`: 13 of 13 as expected. Reference 1.0; do nothing 0; lid smaller than the opening 0 (enclosed); lid not a plate 0 (files); oversize J1 window 0 (enclosed); no J3 window 0 (final pose); teleporting path 0; valid with floor 3 lower 0.444; valid with floor 12 lower 0.300; wrong order 0.217; floating battery 0.271; blocked J1 keep-out 0; no pegs 0.271.
  - `python environment/make_bundle.py DIR`, then in DIR `python3 tools/tools_h2.py bbox` and `submit` on the reference files: bbox volume 81343.2, "accepted". `grep` for WEIGHTS, REFERENCE, SESSION, solution, h2_checks in the bundle's tools found nothing.
  - `python3 tests/test_anchors.py` (H1) still 14 of 14.
- Reference layout: B and the speaker on the floor under board A (the space under A is exactly B's height, 6.8), A on four posts, battery on top of A, order B, speaker, A, battery, lid. Board A uses the H1 tilt path.
- Not verified, or assumed:
  - Whether H2 produces a gap. No agent has run on it.
  - That the reference is close to the smallest possible. I argued by hand that no layout gives a lower height; I did not search. If an agent finds a smaller valid design it scores 1.0 and the reference volume must be lowered to match.
  - The 95,000 zero point is my choice, set so that a careful but conventional layout lands near 0.5.
  - Nothing has run in Harbor.
- Files changed: those listed, plus SPEC.md and SESSION.md.
- Need from others: A, see the interface line under Decisions; artifacts changed from `door.stl` to `lid.stl`.
- Next: run clean agents on H2 when itswinther says go.

### 2026-11-14 03:05 | B first H2 agent result, and the decision to scrap | itswinther + Claude
- Did: started three clean agents on H2 at once (Fable 5.2, Opus 5.5, Sonnet 5.5) with `claude -p` from fresh bundle folders outside the repo. Before starting, a probe agent in the same folder answered `NONE` when asked what project instructions or memory were in its context; no CLAUDE.md exists up the folder tree; `work/` and `submission/` were empty.
- Verified by (command and result): Sonnet finished first. `python3 -I tests/grade_h2.py` on its submission printed reward 0.9733, p 1.0, size term 0.962, bounding box 81,864 mm3 (reference 81,343), nothing failed. It took 3 min 50 s, 8 turns, $0.38, 2 submissions, and all 7 tool calls stayed inside its folder.
- How it did it: the same layout as the reference (board B under board A, battery and speaker on top). It avoided the tilt path by making the box 2 mm longer and dropping every body straight in, and recovered the volume by probing the wall-thickness test and using 1.4 walls.
- Finding: H2 has no meaningful gap either. A continuous score, free placement and free order did not help: the layout search is small enough to reason through in one pass, and the tools confirm each choice immediately.
- Decision by itswinther: scrap H1 and H2 and choose a new challenge.
- Not verified, or assumed: the Fable and Opus runs were still going when this was written; results will be added if they finish.
- Files changed: `transcripts/h2_sonnet/`, SESSION.md.
- Need from others: A, the Harbor wiring is still useful for any new idea, but do not build further around `grade.py` or `grade_h2.py`.
- Next: wait for the new idea. Lesson to carry over: test any idea with a clean agent run within its first hour.

### 2026-11-14 03:14 | B Moving Day (starting) | itswinther + Claude
- Did: starting the Moving Day measurement on itswinther's handoff. First instance is the hardest I can author: a corner sofa that must be carried on its back, tipped on end in the right direction under a 258 ceiling and walked round an L-corridor; a 232-tall wardrobe that only tips upright one way under a 238 ceiling; and two pieces whose final poses block the others' routes. Code goes in `geometry/md.py`, `tests/grade_md.py`, `solution/reference_md.py`, `environment/tools_md.py`.
- Verified by (command and result): nothing yet.
- Not verified, or assumed: that this produces a gap.
- Files changed: SESSION.md.
- Need from others: nothing.
- Next: reference at 1.0, anchors, then two or three clean agent runs.

### 2026-11-14 03:22 | B Moving Day flat-1 (built, agents running) | itswinther + Claude
- Did: built Moving Day. `geometry/md.py` (public engine: apartment as a solid block with air boxes cut out, pieces as unions of boxes, path rules, delivery replay, score), `tests/grade_md.py`, `solution/planar.py` and `solution/reference_md.py` (reference plan from a small planar A* plus scripted tips), `environment/tools_md.py`, `environment/make_bundle_md.py`, `environment/public/SPEC_MD.md` and `INSTRUCTION_MD.md`, `tests/test_anchors_md.py`. SPEC.md is version 0.3.
- Instance flat-1 (cm): front door 86 wide and 205 high; hall; a 125-wide corridor with a 205-high doorway part way along and an L-turn into the living room; a bedroom with a 238 ceiling behind an 86-wide door; other ceilings 258. Pieces and weights: sofa 4 (L-shaped, 240 x 160 x 80), wardrobe 3 (60 x 45 x 232), bookcase 1, chest 1. Step limit 5, pose cap 4,000, volume tolerance 1 cm3.
- Where the difficulty is, none of it stated in the agent's spec:
  - Order: the bookcase's final pose leaves 70 of corridor width, so the sofa must go first; the chest's final pose blocks the bedroom door, so the wardrobe must go first. The spec lists the pieces as bookcase, chest, wardrobe, sofa.
  - Sofa: it only passes the 86 door on its back, cannot turn the corridor corner lying down, and standing on end it is 240 tall so it cannot pass the 205 doorway. It has to be tipped on end after the doorway, and only one tipping direction fits under 258 (256.3 needed; the other needs 288).
  - Wardrobe: it only stands up about its 45 edge (236.3 under 238; the 60 edge needs 239.6), and has to be turned in the hall to reach the bedroom.
- Verified by (command and result):
  - `python3 solution/reference_md.py OUT` took 12 s and printed `poses {'sofa': 612, 'bookcase': 151, 'wardrobe': 357, 'chest': 112}`.
  - `cd tests && python3 -I grade_md.py OUT/plan.json --reward R` printed reward 1.0, all four delivered, in 0.4 s.
  - `python3 tests/test_anchors_md.py`: 17 of 17. Gold 1.0; do nothing, invalid JSON, oversized file, teleporting to the final poses and straight lines through walls all 0; gold paths in the listed order 0.025; easy pieces only 0.025; everything but the sofa 0.154; sofa dragged without standing it up 0.154; wardrobe tipped the wrong way 0.222; a bad chest or bookcase path 0.395; a duplicate and an unknown name ignored (1.0); 0.0002 into a door frame still delivered (0.8 cm3, inside the tolerance) and 0.5 into it not.
  - A flood over every planar state of the sofa lying on its back (3.5 cm, 2 degree grid, 14,474 states) never turns more than 28 degrees, so it cannot round the corner that way.
  - Bundle check: `make_bundle_md.py`, then `tools_md.py sweep` and `submit` on the reference plan inside the bundle: all four pieces at 0.0 volume, "accepted".
- Not verified, or assumed: whether agents fail. That the sofa has no other route (for example tilted in 3D); I only excluded the planar one. Nothing has run in Harbor.
- Files changed: those listed, SPEC.md, SESSION.md.
- Need from others: A, see the interface line under Decisions (one artifact now).
- Next: grade the three agent runs and report.

### 2026-11-14 03:31 | B Moving Day flat-1 agent results | itswinther + Claude
- Did: ran three clean agents on flat-1 at once with `claude -p` from fresh bundle folders outside the repo (probe agent answered `NONE` for pre-loaded context; no CLAUDE.md up the tree; empty work and submission folders). Graded each `submission/plan.json` with `python3 -I tests/grade_md.py`.

  | Model | Score | Time | Tool calls | Submissions | Cost |
  | --- | --- | --- | --- | --- | --- |
  | Fable 5.2 | 1.0 | 3 min 27 s | 6 | 1 | $1.36 |
  | Opus 5.5 | 1.0 | 8 min 52 s | 20 | 3 | $1.79 |
  | Sonnet 5.5 | 0 (no submission) | 8 min 25 s | 15 | 0 | $0.40 |

  No tool call in any run touched a path outside its own folder.
- What they did: Fable and Opus both found the two order traps from the numbers, carried the sofa on its side, stood it on end in the one direction that fits (both quote 256.3 under 258, and 288 for the other way), wrote their own position-and-angle grid search for the corner, and stood the wardrobe up about its 45 edge (236.3 under 238). Opus hit two dead ends first (a wall strike leaving the south corridor, and a corner turn 0.4 cm into a wall because its search area ended at the wall) and went through bookcase and chest, then sofa, then all four. Sonnet started two background path searches and ended its turn saying it would continue when they reported; a headless run is never woken, so it submitted nothing.
- Finding: no gap for Fable or Opus on the hardest instance I could author. The task did cost Opus and Sonnet much more work than H1 or H2 (20 and 15 tool calls against 12 or fewer). Sonnet's zero is partly an artifact of running headless and should not be read as a clean failure.
- Also recorded: the last two H2 runs finished earlier. Fable 1.0 (bounding box 80,804) and Opus 1.0 (77,770), both smaller than my H2 reference (81,343).
- Not verified, or assumed: a rerun of Sonnet told not to stop while searches run; any non-Claude model; anything in Harbor or OpenCode.
- Files changed: `transcripts/md_fable`, `md_opus`, `md_sonnet`, `h2_fable`, `h2_opus`, SESSION.md.
- Need from others: a human decision. Per the handoff's own rule (clean agents at 1.0 on the hardest instance means stop and report) I have stopped building.
- Next: nothing until told.

### 2026-11-14 03:55 | A (spikes) | Mikael + Claude
- Did: after B's six 1.0 runs, tested three other task shapes on Fable 5.2, Sonnet and Opus via headless `claude -p` in clean folders outside the repo (no web, no subagents). Code, instances, agent outputs and transcripts are in `spikes/` and `holdtheline/`. Summary in `spikes/README.md`.
- Verified by (command and result):
  - Hold the Line (`holdtheline/`, workstream C folder, which had no owner): `python3 policies.py 60` gives the scripted reference a mean of 9,849; do-nothing 0, ship-blind, never-ship, sort-all, over-adjust and stop-early all score 0 to 0.12 on average. On one hidden seed the agents scored: Sonnet 9,926 and Opus 10,285 (both above the reference 9,744), Fable 97 (played one slot, then the headless session ended while it waited on its own background job; not a real result).
  - Wrist tracker for children 6 to 10 (`spikes/wrist_tracker/`): one-sentence brief plus a parts list. All three returned a sensible child-sized device: 31 to 34 mm wide, 13 to 14 mm thick, 20 to 29 g, straps, rounded edges, display on top, charge contacts on the skin side. Sizes and masses measured from the STLs; the rest from the agents' own reports and renders.
  - Watch gear train (`spikes/gear_train/`): `python3 watch.py grade inst_1.json runs/<model>/design.json ref_1.json` gives Fable 1.0 (11 min 36 s, $0.87), Opus 1.0 (10 min 10 s, $0.43), Sonnet 0.917 (1 min 53 s, $0.20; one extra layer). All three wrote an exhaustive search.
- Findings: every fully specified, checkable task was turned into a program by the agent. Unstated common sense (child wrist size) was inferred unprompted. No spike shows a gap against these models.
- Not verified, or assumed: one instance per spike, Claude models only; nothing ran in Harbor or OpenCode. The gear-train reference is a random planted movement, not an optimum. The gear train's power-reserve objective is trivially maxed (no torque limit), so its score is half meaningless.
- Files changed: new `spikes/` (README, gear_train, wrist_tracker), `holdtheline/` (sim, policies, server, agent kit, results); SESSION.md (row A, this entry). No existing files of other workstreams touched.
- Need from others: the team decision under Open questions is still open, and these results bear on it.
- Next: harness work (Harbor task around B's grader) whichever idea wins.

### 2026-11-14 03:51 | B watch task, first runnable version | itswinther + Claude
- Did: built the mechanical watch gear-train task from `MECHANICAL_WATCH_IDEA.md`. `geometry/watch.py` (public: movement.json parser, exact speeds from tooth counts, free-spin, held, mesh-run and clearance measurements), `geometry/watch_gears.py` (involute gear maker, not shipped to the agent), `geometry/data/barrel.stl`, `tests/grade_watch.py` (2 gates, 10 checks, weight 16; the required hand speeds live only here), `solution/reference_watch.py`, `environment/tools_watch.py`, `environment/make_bundle_watch.py`, `environment/public/SPEC_WATCH.md` and `INSTRUCTION_WATCH.md`, `tests/test_anchors_watch.py`.
- Verified by (command and result):
  - Two-gear check of the mesh test: barrel with a correct 12-tooth pinion gives overlap 0.0, largest gap 0.027, drive overlap 0.051; the same pinion declared as 13 teeth jams (0.103 mm3); moved 0.4 further away it disengages (gap 0.216, drive overlap 0.0).
  - `python3 solution/reference_watch.py OUT` wrote 11 parts. `cd tests && python3 -I grade_watch.py OUT --reward R` printed reward 1.0 with both gates and all 10 checks true, in 35 s. Speeds from the tool: centre 1, hour wheel 1/12, seconds 60 clockwise turns per hour.
  - Bundle: `tools_watch.py speeds`, `spin`, `held`, `mesh`, `clear`, `extent`, `submit` all ran on the reference inside a fresh bundle. `grep` for the hand speeds, the gear maker and "reference" in the bundle found nothing.
- Reference train: barrel 96 to 24, 60 to 30 (centre, minute hand), 90 to 12, 96 to 12 (seconds); motion work 12 to 36 and 12 to 48 (hour wheel, a tube round the centre arbor). Two meshes between barrel and centre are needed because one mesh would turn the minute hand anticlockwise.
- Not verified, or assumed: whether agents fail; the anchor script was still running when this was written; no printability check; nothing in Harbor.
- Files changed: those listed, SESSION.md.
- Need from others: Abhishek, see the choices listed under Decisions and say if any is wrong.
- Next: grade the three agent runs and report.

### 2026-11-14 03:58 | B watch task, agent results | itswinther + Claude
- Did: ran three clean agents on the watch task with `claude -p` from fresh bundle folders outside the repo (probe agent answered `NONE` for pre-loaded context; no CLAUDE.md up the tree; empty work and submission folders; the bundle holds no hand speeds, gear maker, grader or reference). Graded each submission folder with `python3 -I tests/grade_watch.py`. The anchor script also finished: `python3 tests/test_anchors_watch.py` gave 7 of 7 as expected (gold 1.0; nothing 0; missing part 0; barrel not held 0.383; hands swapped 0.281; seconds mesh undeclared 0.195; one tooth count wrong 0.096), in 2 min 50 s while the agents were using the machine.

  | Model | Score | Time | Tool calls | Cost |
  | --- | --- | --- | --- | --- |
  | Fable 5.2 | 1.0 | 4 min 27 s | 5 | $1.66 |
  | Opus 5.5 | 1.0 | 7 min 38 s | 10 | $1.22 |
  | Sonnet 5.5 | still running at the time of writing (21 tool calls, nothing submitted yet) | | | |

  No tool call in the two finished runs touched a path outside its own folder.
- What they did: both inferred the unstated requirements (hour 1/12, minute 1, seconds 60 clockwise turns per hour, hour and minute on one axis) without comment, both noticed that one mesh from the barrel would turn the minute hand anticlockwise and added a reversing stage, both wrote their own involute gear generator, and both chose a centre seconds hand with its arbor through a hollow minute tube inside the hour tube, matching centre distances by using different modules. Fable's first build passed every check. Largest mesh gap 0.018 to 0.023 against the 0.1 limit.
- Finding: the two things A's spike had not tested (an unstated brief, and real gears turned by the grader) do not create a gap for Fable or Opus.
- Defects the agents found in the bundle: the docstring of `geometry/watch.py` mentioned a gear maker that is not shipped (fixed in this commit); the `clear` tool returns step -1 both when it skips a pair on bounding boxes and when it finds no overlap (not fixed).
- Not verified, or assumed: Sonnet's result; any non-Claude model; anything in Harbor or OpenCode; a printability check does not exist.
- Files changed: `transcripts/watch_fable`, `transcripts/watch_opus`, `geometry/watch.py` (docstring), SESSION.md.
- Need from others: a human decision on what to try next.
- Next: add Sonnet's result when it finishes; nothing else until told.

### 2026-11-14 04:13 | B staged watch task with test code withheld (built, chains running) | itswinther + Claude
- Did:
  - Sonnet's single-stage watch run finished: 1.0 in 16 min 55 s, 26 tool calls, $1.22, nothing outside its folder. So the single-stage watch task with tools is 1.0 for all three models.
  - Closed the loophole Fable used (an idler kept down only by another wheel above it): for the two moves along z, "held" now only accepts fixed parts or a mobile on the same axis. Fixed parts must not overlap each other.
  - Added stage 2 (add a 24-hour hand; the existing mobiles' axes and part files are frozen; fixed parts may change) and stage 3 (assembly order and rigid paths for every part, step 0.2, parts of one mobile exempt from each other). `tests/grade_watch.py --stage N --prev FOLDER`.
  - Added the withheld bundle: `environment/make_bundle_watch.py --tools no` ships INSTRUCTION, SPEC, the barrel, `tools/kernel.py` (a copy of `geometry/core.py`) and `tools/submit.py` (format only, generated from `environment/submit_template.py`). The spec now defines the mesh test exactly (turning direction, angles per step).
  - Reference for all three stages in `solution/reference_watch.py`.
- Verified by (command and result):
  - `python3 solution/reference_watch.py OUT` then `python3 -I tests/grade_watch.py OUT/stageN --stage N [--prev OUT/stage(N-1)]`: stage 1 reward 1.0 (42 s), stage 2 reward 1.0 (51 s; day hand 1/24 clockwise turns per hour, axis 10.04 from the hour axis, reach 3.21), stage 3 reward 1.0 (2 s; 18 parts, 1,209 poses).
  - Stage 3 on the reference with the order changed: centre before third gives 0.446 (third not installed); bridge straight after the main plate gives 0.222 (six parts not installed); no assembly.json gives 0.
  - Withheld bundle: `tools/submit.py` answered "accepted" for the reference at stages 1 and 3. `grep` for the hand speeds, the gear maker, the mesh test and `Fraction` in the bundle found nothing.
  - Clean-context probe in the run folder answered `NONE`.
- Not verified, or assumed: the staged anchor script is not written (only the three order checks above); `tools_watch.py` has no stage 2 or 3 tools, so a with-tools arm of the staged task cannot be run yet; `tests/test_anchors_watch.py` was written for the old single-frame reference and has not been rerun since the reference was split into separate plates.
- Files changed: `geometry/watch.py`, `tests/grade_watch.py`, `tests/grade_chain.py`, `solution/reference_watch.py`, `environment/make_bundle_watch.py`, `environment/submit_template.py`, `environment/run_clean_chain.sh`, `environment/public/SPEC_WATCH.md`, `SPEC_WATCH_GIVEN_NOTOOLS.md`, `INSTRUCTION_WATCH_S1/2/3.md`, `transcripts/watch_sonnet`, SESSION.md.
- Need from others: nothing.
- Next: grade the three chains and report.

### 2026-11-14 05:10 | A harness + spikes (Mikael asleep; Claude working on his instruction) | Mikael + Claude
- Did: (1) got Harbor running sandboxed with Codex on Mikael's Codex credits (`CODEX_FORCE_AUTH_JSON=1`, model `openai/gpt-6.1-sol`); (2) built a five-step watch-movement Harbor task (`spikes/gear_task/`): going train under a torque limit, motion work, a larger balance, a date wheel, automatic winding with a rotor-turns band; (3) built a watch-regulation task (`spikes/regulate/`) whose physics lives in a compose sidecar the agent can only query; (4) wrote `spikes/IDEAS_CODE_IS_NOT_ENOUGH.md`.
- Verified by (command and result):
  - Network probe tasks (`harbor run -a oracle`): `no-network` blocks everything; `allowlist` with chatgpt.com reaches only chatgpt.com (example.com, pypi.org, api.openai.com, 1.1.1.1 blocked). Codex under the allowlist ran and reported it could reach nothing else.
  - Five-step watch task: oracle 1.0 on all 5 steps, nop 0.0 on all 5. `harbor run -p watch-s8 -a codex -m openai/gpt-6.1-sol -k 3 -n 3`: 1.0, 1.0 and 0.6 as first graded; the 0.6 was a grader bug (the hour wheel meshes two gears from step 4, the grader kept one partner), fixed in `movement.py`; the regraded designs are valid, so GPT scored 1.0 x3. Whole job 5 min 47 s. GPT also used fewer layers than the planted reference.
  - Regulation task (seed 4242): oracle 1.0 (true error 45.2 s/day), nop 0.0 (116.3). Over 60 seeds the scripted watchmaker cuts mean error from 118.4 to 26.9 s/day.
  - Transcript audit of all 15 GPT steps: no network commands, no reads outside /app.
- Findings: the five-step movement shows no gap. Every model so far turns a fully stated, checkable problem into code and solves it. The regulation task is the first with hidden, noisy, costly measurement and irreversible actions; its results decide whether that pattern works.
- Sandbox gap found and sealed: sidecars share the agent's network namespace under egress control; the sidecar's result endpoint now needs a token stored only in the sidecar image (not in the repo). Residual: DNS resolves inside locked containers; the Codex login sits in the agent container (local Docker only).
- Not verified, or assumed: one seed per task; GPT-6.1-sol only in Harbor; the planted watch reference is not optimal (GPT beat it on layers).
- Files changed: `spikes/gear_task/` (movement.py, build_task.py, harbor_task_s8, runs_gpt), `spikes/regulate/` (timing.py, server.py, timer.py, BRIEF.md, build_task.py, harbor_task_s4242), `spikes/IDEAS_CODE_IS_NOT_ENOUGH.md`, `spikes/README.md`, SESSION.md (row A, this entry).
- Next: regulation results, then whichever idea shows a gap gets more seeds.
