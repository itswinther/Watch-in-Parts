# Reproducing the keyless-works results

This is the judge-facing guide for running the keyless-works task (`spikes/keyless/`) end to end. The task
asks an agent to design the keyless works of a mechanical watch. A contact simulation grades the design
by running a watch owner's acceptance sequence, AT-0 to AT-6 (assemble, wind, hold, run, backward, set,
return). One command builds the task and runs:

- the reference solution;
- the do-nothing agent;
- a model of your choice under OpenCode, k times.

It then writes the results table.

## Prerequisites

| Need | Version, and how we run it |
|---|---|
| Docker | Docker Desktop or Engine. Give it at least 12 GB of memory for 2 concurrent trials; see *Time and memory*. |
| uv | any recent version (runs Harbor from source) |
| Harbor | **0.26** (see *Harbor 0.25 vs 0.26*): a checkout in `HARBOR_SRC` (`git clone https://github.com/harbor-framework/harbor && git -C harbor checkout v0.26.0`), or a `harbor` 0.26 on `PATH` |
| Model key | `export ANTHROPIC_API_KEY=...`, or `KEY_FILE=/path/to/file` holding the bare key or `ANTHROPIC_API_KEY=...` |
| bash, grep | standard |

No Python is needed on the host apart from Harbor itself. The task builder and the report scripts run
inside Docker.

## One command

From the repository root:

```bash
HARBOR_SRC=/path/to/harbor spikes/keyless/report/run_all.sh anthropic/claude-opus-5-5 5
```

`run_all.sh MODEL K [OUT_DIR]` does the following:

1. **Builds the task.** It builds the builder image from `spikes/keyless/docker/Dockerfile` (CadQuery and
   manifold3d), then runs `build_task.py OUT/task --agent opencode` inside it. It refuses to go on unless
   `task.toml` has these settings:
   - the agent network is an allowlist of `api.anthropic.com` only;
   - the verifier network is `no-network`.
2. **Runs the reference agents.** It runs `harbor run -a oracle -k 3` (the reference solution, built by its
   generator script) and `harbor run -a nop -k 1` (an agent that does nothing).
3. **Runs the model.** It runs
   `harbor run -a opencode -m MODEL -k K -n 2 --ak disable_web_search=true`. The key reaches this subshell
   only.
4. **Writes the report.** In `python:3.12-slim`, it writes these files to `OUT/report/`:
   - `RESULTS.md` and `results.json`, from `summarize.py`;
   - `INDEX.md`, from `index.py`;
   - `INCIDENTS.md` and `INCIDENTS.json`, from `incidents.py`.
5. **Scans for the key.** It checks everything saved for an `sk-ant-` string.

`OUT_DIR` defaults to `./keyless-run-<timestamp>`. These optional settings change a run:

| Setting | Default | Effect |
|---|---|---|
| `ORACLE_K` | 3 | Number of oracle runs |
| `NOP_K` | 1 | Number of nop runs |
| `N_CONCURRENT` | 2 | Trials run at the same time |
| `EXTRA_AK` | none | Extra agent options, e.g. `"--ak reasoning_effort=high"` |
| `SKIP_BUILD=1` | off | Reuse `OUT/task` |
| `SKIP_REF=1` | off | Run the model only |

You can run the report alone on any Harbor job folder, including older ones:

```bash
docker run --rm --memory 1g -v "$PWD/spikes/keyless":/k:ro -v /path/to/jobs:/j:ro -v "$PWD/out":/o \
  python:3.12-slim sh -c 'python -I /k/report/summarize.py /j --out /o &&
    python -I /k/report/incidents.py /j --out /o/INCIDENTS.md &&
    python -I /k/report/index.py /j --out /o/INDEX.md --incidents /o/INCIDENTS.md'
```

## Reading the results

### The reward

Each trial gets one reward in [0, 1], written by the separate, no-network verifier to
`verifier/reward.txt`:

reward = product × (0.75 + 0.10 × honesty) / 0.85

- **product:** the sum of the weights of the acceptance steps passed in order from AT-0. The weights are
  0.20, 0.15, 0.15, 0.20, 0.10, 0.12 and 0.08. AT-0 counts only together with AT-1.
- **honesty:** compares the agent's `report.json` claims for each step with the grader's results. A
  claimed pass that fails costs 2 points.

`verifier/details.json` holds the full breakdown:

- gates and conditions;
- every step's measured values;
- `first_failed`;
- the grader version and a hash of the constants.

### `RESULTS.md`, one row per agent and model

- **Statistics:** n valid out of n trials, mean, 95 % CI (Student t), sd and min–max of the reward,
  product and honesty.
- **Validity:** only trials whose reward Harbor marks `reward_valid` count. API and rate-limit errors
  are excluded, as Harbor's own mean does. Agent timeouts are graded and do count.
- **Pass:** a trial passes at reward ≥ 1.0, which means full acceptance and a fully honest report.
  `--threshold` changes this.
- **pass@1, pass@k and pass^k:**
  - pass@k uses the unbiased estimator of Chen et al. 2021, *Evaluating Large Language Models Trained on
    Code*, arXiv:2107.03374 §2.1: 1 − C(n−c, k)/C(n, k).
  - pass^k = C(c, k)/C(n, k), the chance that k trials all pass (Yao et al. 2024, τ-bench,
    arXiv:2406.12045).
  - pass@1 also gets a Wilson 95 % interval.
- **Acceptance steps:** how many trials passed each step AT-0 to AT-6, and how many trials first failed
  at each step.
- **Cost and time:**
  - mean and total cost, and tokens;
  - mean and maximum agent time;
  - the maximum agent time as a share of the agent timeout, which shows whether the time limit ever
    caused a low score;
  - timeouts, invalid trials and exception types.
- **Versions:** the harness, model, agent options, Harbor version and commit, grader version, and task
  checksum.

### `INDEX.md`, one row per trial

Each row links to:

- the agent log (`agent/opencode.txt`) and the ATIF trajectory;
- the agent's `report.json` and the score breakdown;
- the grader log and the images the agent saved under `/app`;
- the incident record;
- the trial in Harbor's viewer. Start the viewer with `uv run harbor view OUT/jobs`.

The index also has a ✓/✗ grid per step with the agent's own claim beside each result.

### `INCIDENTS.md`, one record per failing trial

The records follow the ISO/IEC/IEEE 29119-3 *incident report*. Each record has:

- an ID and the first failed AT step;
- expected against actual, taken from `constants.py` and `details.json`;
- the agent's claim for that step;
- the last tool calls before the end, as `opencode.txt:LINE`;
- three blank fields that a person fills in after reading the trajectory: **root cause (the agent's
  decision)**, **classification** (agent fault, grader fault or spec ambiguity) and **confirmed by**.

### Expected numbers (placeholders until the runs are in)

| Agent | Expected | Ours (fill in from `RESULTS.md`) |
|---|---|---|
| oracle (reference) | 1.0 ×3 | _TBD_ ×3 |
| nop | 0.0 | _TBD_ |
| anthropic/claude-opus-5-5, k = _TBD_ | below the reference | mean _TBD_ [CI _TBD_], pass@1 _TBD_, pass^k _TBD_; first failures _TBD_ |
| anthropic/claude-sonnet-5-5, k = _TBD_ | below the reference | _TBD_ |
| openai/gpt-6.1-sol (Codex, cross-family check) | below the reference | _TBD_ |

These numbers count as reproduced when both of the following hold:

- the oracle scores 1.0 on every repeat, and the nop scores 0.0;
- a model's mean on a fresh run falls inside the CI we report.

The grader is deterministic. The same submission always gets the same reward, so all the spread comes
from the agent.

## Notes

### Harbor 0.25 vs 0.26

Use 0.26. Harbor 0.25 always reinstalls OpenCode from npm when the agent starts. The task's agent network
is an allowlist of the model endpoint only, so that install fails and every model trial ends at agent
setup. Harbor 0.26 sees that the pinned OpenCode (1.19.5) is already in the image: its log says
"OpenCode is already available at the requested version". `run_all.sh` checks the version and stops on
0.25. The oracle and nop agents work on both.

### Time and memory

| Phase | Resources | Time |
|---|---|---|
| Agent container | 4 CPUs, 3 GB | Times out at 90 min (`[agent] timeout_sec = 5400`; 3× the slowest run seen, at least 60 min) |
| Verifier container | 4 CPUs, 4 GB, no network | Times out at 40 min; grading the reference takes about 160 s on 4 cores |
| First image build | Installs CadQuery and OpenCode | A few minutes; cached after that |

- **Concurrency:** with `-n 2`, two agent and two verifier containers can run at once, which needs about
  14 GB of Docker memory. Use `N_CONCURRENT=1` on a 8 GB machine.
- **Wall time:** expect about 10 min for the oracle ×3, then about K × 30 to 60 min / N_CONCURRENT for the
  model. Agent times observed on the earlier spikes were 9 to 19 min.
- **The timeout:** the report's "max share of timeout" column shows whether any trial came near the
  timeout.

### Cost

Harbor records the cost of each trial from OpenCode's usage. `RESULTS.md` shows the mean and the total.
Neither Harbor nor `run_all.sh` caps spending. For reference, on the earlier, smaller spikes:

- Sonnet 5.5 cost $0.49 per trial (right-angle winding, 9 min);
- GPT-6.1-sol watch stages cost $0.13 to $0.65.

For the keyless task, expect several dollars per frontier-model trial (_TBD after the first runs_). Start
with `K=1` to check the setup before running the full k.

### Regrading

The verifier is separate and collects `/app` as an artifact. After a grader fix,
`uv run harbor job regrade OUT/jobs/<job> -p OUT/task` rescores old trials without rerunning the agents.
Then rerun the report step.

## Harness settings

- **Output cap:** the task image sets `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=64000` (in the
  Dockerfile that `build_task.py` writes), so OpenCode with default settings cannot end a turn empty
  because of its 32,000-token output cap.
- **Web search:** run OpenCode with `--ak disable_web_search=true`.
- **Harbor version:** use 0.26 from source (`uv run harbor ...`). 0.25 reinstalls OpenCode from the
  internet, which the task's allowlist blocks.
