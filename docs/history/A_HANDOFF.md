# Workstream A handoff (Mikael), 14 Nov 2026, about 19:40 Helsinki

Read this first if you are a new session for Mikael (workstream A). Repo:
/Users/mikbs/Desktop/dev/Junction/board-in-a-box (GitHub itswinther/board-in-a-box). Shared log: SESSION.md on main.
Workstream B = itswinther's sessions. Submission deadline: Sunday 15 Nov, 10:00 Helsinki.

## Rules Mikael set (binding)
- **Everything compute runs in Docker** with memory caps, never on the host (the laptop ran out of memory
  once). The total of all containers' caps stays at or below about 9 to 10 GB; Docker Desktop is set to 16 GB.
- **Sandbox fully:** agents run only through Harbor (0.26 from source: `cd /Users/mikbs/Desktop/dev/harbor && uv run harbor ...`),
  the allowlist is the model endpoint only, the verifier is separate with no network, web search is disabled,
  and every transcript is audited.
- **Push everything to GitHub** via a temporary worktree (`git worktree add --detach TMP origin/main`, cherry-pick or
  copy, push, remove). Never stash or revert others' files in the main checkout. Grep for secrets before each push.
- **Keys:** the Anthropic API key is in ~/.harbor-secrets/anthropic.env (about $17 left; never print or commit
  it). GPT runs use Codex with Mikael's ChatGPT login (`CODEX_FORCE_AUTH_JSON=1`; subscription credits, not the
  API).
- **Run budget:** no Opus runs; at most 4 Sonnet runs via OpenCode, only with Mikael's go; GPT via Codex is fine.
  No model run without Mikael's go.
- **Honesty:** prelims are labelled "not a result"; never claim a gap from one run; check every failure against the files
  and the replay ("unclear" if unsure).
- The judges run `harbor run -a opencode -m provider/model`, so results that count come from Harbor, OpenCode and an API
  key. Codex and Claude Code runs are cross-checks only.

## Decisions in force (all in SESSION.md Decisions)
- One professional brief from start to finish, nothing frozen, no method hints; graded only on the delivered
  output; limits generous (agent 90 min keyless, 3 h one-job).
- Scoring (itswinther): no in-order gating; per-part credit plus a whole-build term,
  0.5 × weighted parts + 0.5 × whole build; A's deterministic honesty term kept, as
  R × (0.75 + 0.10 × honesty) / 0.85.
- One demonstration scale for the whole job: s = 1.617 × an 11½‴ movement.
- Five-part job: going train and hands 0.25, 24-hour hand 0.10, 6-hour variant 0.15, assembly 0.25, crown
  winding (A's keyless) 0.25.
- B's option 1: the work order cites documents (QA-W100 inspection procedure). Option 2: gear strength
  (Lewis bending on the going train only, using DS-101's 70.1 N·mm slipping torque and DS-201's allowables; steel pinions pass,
  brass fails).
- Keyless geometry agreed with B (Decisions 15:29 and 17:46): two-body barrel, stem line chosen by the agent,
  keyless works on the dial side, `friction_on` for hand setting, `carrier` field.
- Parked (only if crown winding turns out too easy): hacking seconds (stop lever) and drawn springs.

## State of things
- **B's four-part job (SPEC 0.7):** on main. Smoke runs under Claude Code, outside Harbor: six of six at 1.0 (Fable, Opus,
  Sonnet × 2). So there is no gap on the four-part job alone. B's builder P (the P5 adapter, behind `KEYLESS_IN_JOB`, off) is
  waiting for A's keyless v2 reference in B's frame.
- **A's Harbor packaging of the one-job:** `harbor/watch_one/` gives oracle 1.0 and nop 0.0 on the two-body barrel; the verifier
  timeout is 7800 s. The one command is `KEY_FILE=… harbor/watch_one/run_all.sh MODEL K`.
- **Keyless v1** (`spikes/keyless/`): the reference scores 1.0 × 3; the anchors and exploits all score low (the free-click exploit 0.325,
  skip-the-hardest 0.41). Prelims (one each):
  - GPT via Codex: 0.024. A mirror-image mechanism; an independent review says the wording is unambiguous.
  - Sonnet via OpenCode: 0.950. Every step passes; it lost only on honesty.
- **Running at handoff:**
  1. The keyless builder: oracle rerun on the brief clarified by the nine wording fixes (59a129b), then 3 GPT repeats via Codex
     (`-k 3 -n 2`) to see whether the handedness error repeats.
  2. The engine-fix session on branch `a/keyless-engine-fixes` (b804aa5, NOT merged). ml01 (Marco Lang's real
     keyless works) now winds and the pull no longer jams, but hold, backward, set and return still fail; it is diagnosing. It must not let the
     symmetric-teeth, dog-teeth, nothing-engages, off-axis or overlap anchors pass. One local grade.py change (stem protrusion
     only at the +x end) waits for this merge.
- **Open for Mikael / to post to B:** the barrel spring chamber. DS-101 Rev F (907fcce) adds real thin springs L, M and N
  that fit the 1.0-tall drum, but they are listed for 7.5 to 8.5 mm barrels while B's chamber is about 10.5 mm. The
  recommendation is that B shrinks the chamber to match L (inner radius 6.06, core 2.02 at s, about 40 h), which leaves the gear train
  unchanged. Not yet posted.
- **Next big steps:**
  1. Merge the engine fixes once ml01 and the anchors pass.
  2. Build the keyless v2 reference in B's frame from the datasheets (Decisions 17:46 numbers) and compare it with Grossmann.
  3. B switches P5 on.
  4. The joined five-part job with documents cited and gear strength.
  5. Then up to 4 Sonnet runs via OpenCode and GPT via Codex.
- **Ask the organisers or the mentor:** the judged model, the timeout and rerun budget, the Harbor version, and API credits.

## Key files
- Research and planning: RESEARCH_BRIEF.md, STANDARDS.md, HARBOR_RESEARCH.md, REAL_DATASHEETS.md, DATASHEET_GAPS_2*.md,
  TEST_ENVIRONMENT.md, TASK_DOCS_TEMPLATE.md, spikes/STAGED_ACCEPTANCE_PLAN.md.
- Keyless: spikes/keyless/ (engine.py, grade.py, constants.py, docs/PROMPT|SOLUTION|STEP_BY_STEP|CONTEXT|
  REVIEW_RUBRIC|REVIEW_DIRECTIONS.md, datasheets/DS-101..501 + TRACEABILITY.md + public_domain/, realcad/REAL_CAD.md,
  runs/INDEX.md, report/run_all.sh, INTERFACE_FOR_B.md).
- Viewers: tools/viewer/ (export_scene.py, export_axes.py, export_keyless_replay.py, export_watch_demo.py X-ray
  demo).
- Scratch (local only): this folder; the demo page is in demo/watch_demo.html; the transcript of Mikael's mentor recording
  is ~/Downloads/New Recording 2 - transcript.txt.
