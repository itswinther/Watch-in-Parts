# Test environment: Harbor + OpenCode, done the way Harbor documents it

Written by Mikael + Claude (workstream A), 14 Nov 13:05. Sources: docs.harborframework.com (tasks overview,
configuration, instruction, verifier) and Harbor 0.26's built-in task rubric
(`src/harbor/cli/quality_checker/default-rubric.toml`). The organisers ask for
`harbor run -p ./my-task -a opencode -m provider/model`, with the verifier writing one score in [0, 1] to
`/logs/verifier/reward.txt`.

## The harness today

| Setting | Value now | Where it comes from |
|---|---|---|
| Harness | OpenCode (`-a opencode`), pre-installed in the task image | organisers |
| Harbor version | 0.26 from source (`uv run harbor`) | 0.25 always reinstalls OpenCode from the internet, which the allowlist blocks |
| Step or turn limit | **none**: the agent runs until the model stops or the timeout hits | neither Harbor nor OpenCode sets one |
| Time limit | `[agent] timeout_sec`: 2340 s per watch stage, 2400 s for the spikes | our task.toml; Harbor enforces none if unset |
| Token cap | none on total tokens. Per response, the model's output limit as OpenCode sets it (Haiku hit 32,000 thinking tokens in one turn and produced nothing) | OpenCode and the model |
| Reasoning effort | provider default; settable with `--ak reasoning_effort=...` (OpenCode `--variant`) | Harbor OpenCode options |
| Context window | the model's own; OpenCode compacts long sessions | OpenCode |
| Network (agent) | `allowlist`, only the model endpoint (api.anthropic.com) | task.toml |
| Web tools | OpenCode's websearch and webfetch are blocked by the allowlist anyway; also set `--ak disable_web_search=true` so they are denied | Harbor OpenCode options |
| Verifier | `environment_mode = "separate"`, `network_mode = "no-network"`, 600 to 2400 s, 4 to 7 GB | task.toml |
| Cost cap | our runner stops a chain above `MAX_COST`; Harbor has none | `harbor/watch4/run_chain.sh` |

Observed agent times so far: GPT watch stages 3 to 18 min each; right-angle spike 10 to 19 min (GPT) and 9 min
(Sonnet).

**Engineer time (estimate, ours, unverified):** an experienced movement designer working in CAD with the
supplied parts would need about one to two days for the keyless works alone, and one to two weeks for the
whole staged movement. The reference solutions took our own agent sessions several hours each, with the
grader to hand.

**Contest window: unknown.** The judged model, its effort setting, the per-trial timeout and the rerun
budget have not been announced (CLAUDE.md, "Unknown, do not assume"). Ask the organisers.

## How to build each task, following Harbor's documentation

1. **Layout:** `instruction.md`, `task.toml`, `environment/Dockerfile`, `solution/solve.sh`, `tests/test.sh`.
   For the staged task, either one task per stage (as `harbor/watch4/` does, because a step's verifier
   cannot see the previous step's submission as an untouchable copy) or `[[steps]]` with
   `multi_step_reward_strategy`.
2. **`instruction.md`** is generated from `PROMPT.md` (`TASK_DOCS_TEMPLATE.md`):
   - absolute paths (`/app/submission/...`);
   - the exact output schema;
   - every file the tests read named explicitly;
   - a leading canary comment, which Harbor strips before the agent sees it;
   - no method hints.
3. **`task.toml`:**
   - `[task]`: `name`, `authors`, `description`, `keywords`.
   - `[metadata]` (free-form keys): `category`, `difficulty_explanation`, `expert_time_estimate_hours`,
     `junior_time_estimate_hours`.
   - `[agent] timeout_sec` set from the engineer estimate and the observed times (see below).
   - `[environment]`: pinned image, `cpus`, `memory_mb`, `network_mode = "allowlist"`, `allowed_hosts` =
     the model endpoint only.
   - `[verifier]`: `environment_mode = "separate"`, `network_mode = "no-network"`, and a `timeout_sec` that
     covers the slowest grading with margin.
   - `artifacts`: the submission folder.
4. **Image:** Python packages pinned (`cadquery==2.8.0`, `manifold3d==3.5.5`, numpy, scipy, trimesh);
   `opencode-ai` pinned to the tested version (1.19.5), not `@latest`; no grader dependencies in the agent
   image. `.dockerignore` and `.harborignore` keep `solution/`, `tests/`, anchors and the secret docs out
   of the image, and the build script asserts it.
5. **`tests/test.sh`:**
   - writes 0 to `/logs/verifier/reward.txt` first;
   - runs the grader with `python -I` on named files only;
   - overwrites the reward at the end;
   - saves the per-step acceptance results to `/logs/verifier/details.json`.

   One number in `reward.txt`, as the organisers ask; the labelled breakdown is kept for analysis
   (`reward.json` is also supported, but Harbor prefers it over `reward.txt` when both exist).
6. **`solution/solve.sh`** builds the reference by running its generator, not by echoing a stored answer
   (Harbor's rubric item `hardcoded_solution`).

## Validation ladder, in this order, before any model run

1. `harbor check TASK`: Harbor's rubric. It covers:
   - behaviour in instruction matches behaviour in tests, both ways;
   - informative tests;
   - anti-cheating measures;
   - exact data schema;
   - pinned dependencies;
   - typos;
   - tests or solution in the image;
   - test dependencies in the image;
   - hard-coded solution;
   - output files named in the instruction.

   It uses an LLM evaluator, so it costs a little.
2. Oracle (`-a oracle`): reward 1.0. Nop (`-a nop`): reward 0.0.
3. The anchor set and the exploit set (every attempt scores low) run in Docker against the same grader.
4. One cheap OpenCode smoke run (Haiku) to confirm the harness itself works: install, allowlist, no
   output-limit failure, artifacts collected, key in no log.

## Runs

- `harbor run -p TASK -a opencode -m anthropic/claude-sonnet-5-5 -k 8 -n 2 --ak disable_web_search=true`
  (8 trials, 2 at a time within Docker's 16 GB).
- GPT-6.1-sol under Codex as a cross-family check, until an OpenAI key or organiser credits allow OpenCode.
- Report per model:
  - mean, spread and pass rate over the 8 trials, next to the reference's 1.0;
  - every shortfall traced to the acceptance step it failed and the decision behind it;
  - cost per trial.
- After every run: the transcript audit (network, credential reads, paths outside /app, web-tool
  events) and `grep sk-ant-` over everything saved.
- With the separate verifier, Harbor can regrade old trials after a grader fix, without rerunning the
  agents.

## Setting the agent timeout

It must not be the reason a model scores low ("meaningful difficulty": no failure from a time limit).
Set it at about three times the slowest successful agent run observed, and at least 60 min per stage.
Then check in the trial logs that no run was cut off by it.

## Questions for the organisers

1. Which model and effort setting will be judged?
2. Per-trial timeout and the total rerun budget?
3. Harbor version (0.25 reinstalls OpenCode from the internet)?
4. Credits or keys for OpenCode runs, so every model runs under the same harness?
