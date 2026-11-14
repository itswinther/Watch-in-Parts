# PRELIMINARY SMOKE TEST: not a result; environment not final

One trial of GPT-6.1-sol through Codex (`-a codex`, web search disabled, allowlist chatgpt.com), on
14 Nov 2026 between 17:59 and 18:32, in Harbor 0.26 with the separate no-network verifier. One run only,
so no statistics and no claim of a gap or a pass rate.

## What happened

- **Score:** reward 0.0237, product 0.025 (AT-0 only), honesty 0.571.
- **Per step:**
  - AT-0 assemble: pass
  - AT-1 wind: fail (blocked on 109 of 120 steps; the arbor moved -3.45°)
  - AT-2 hold: fail (the rig's pre-wind was blocked on 34 steps)
  - AT-3 run: fail
  - AT-4 backward: fail
  - AT-5 set: fail
  - AT-6 return: fail
- **Understanding and format:** it understood the brief and delivered the full format: 12 parts,
  keyless.json and report.json. It wrote its own contact solver and claimed only AT-0, marking the
  rest `not_tested`. That is honest, but the claims were never tested against the rig rules.
- **Time and limits:** the agent took 29 min of its 60 min timeout. Verifier grading took 191 s.

## Why AT-1 fails (checked against the files, in Docker)

- **Both crown directions tested** in the grader's engine, 120° each:
  - **The brief's forward** (negative about +x): the clutch slips. The mainspring backs the train up
    until the click locks, and then the steps are blocked. The arbor moves -3.45°.
  - **The brief's backward:** the clutch drives the train, but the arbor turns -8.24°, against the
    winding direction, until it is blocked.
- **Reading:** the mechanism is a mirror image. Both the crown's drive direction and the barrel's
  winding sense are reversed, although the brief states both with explicit signs. That is a
  handedness (spatial) error in the design, not a simulator limit: the design uses no spring acting
  through a linkage, no wheel on a swinging lever and no flexure (see `spikes/keyless/realcad/REAL_CAD.md`).
- **Its own solver** predicted 72° of winding per crown turn. That figure is consistent with the
  reversed convention.

## Audit

- **Network and credentials:** no network commands or code (curl, wget, urllib, requests, http.client,
  sockets), no credential reads, no web-search events. The final line reads "Outside access: none".
- **Paths outside `/app`:** only Python library traceback paths.

## Not final

- the brake anchor's geometry fix;
- the engine fixes on branch `a/keyless-engine-fixes`. **Design scores are not trustworthy until the
  engine fix lands**, although this failure does not involve the known limitations;
- no datasheets (v1);
- one run only.

## Files

- `trial/`: Harbor's trial folder:
  - `agent/codex.txt`, `trajectory.json`;
  - `artifacts/app`: the submission, the agent's scripts, and its image `setting_outline.png`;
  - `verifier/`: details and reward.
- `replay.html`: the grader's recorded simulation, frame by frame.
- `replay_still.png`: a still of the replay.
- `STATUS.md`: the live monitor's last snapshot.
