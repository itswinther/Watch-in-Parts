# Watch in Parts: the Harbor task (workstream A)

This folder packages the decided task as one Harbor task. The decisions behind it are in `SESSION.md`:
Decisions 13:36, 14:08, 14:20 and 14:45, and B's interface at 15:44.

- **The task:** one customer order for a thin dress watch (`environment/public/job/PROMPT.md`), from start to
  finish, with nothing frozen, no method hints, no acceptance test and no target height.
- **Parts graded:**
  - P1, going train and hands (weight 25);
  - P2, 24-hour hand (10);
  - P3, 6-hour-barrel variant (15);
  - P4, assembly (25).
  - P5, crown winding, is off (`geometry/keyless_job.py`, `KEYLESS_IN_JOB = False`) and not part of the task.
- **Datasheets:** in the environment.
- **Scale:** demonstration scale, about 1.6x.
- **Reward:** (0.5 × weighted per-part share + 0.5 × [every part passes] × thickness score) × statement
  factor, as in `SPEC.md` 0.8. The agent never sees a verdict or a score.

The grader, the reference, `PROMPT.md`, `SOLUTION.md` and `STEP_BY_STEP.md` are workstream B's. This
folder only builds the Harbor task around them, and it calls or copies B's files without changing
them.

## The one command

```
harbor/watch_one/run_all.sh MODEL K [OUT_DIR]
# e.g. KEY_FILE=~/anthropic.key harbor/watch_one/run_all.sh anthropic/claude-opus-5-5 8
# oracle and nop only, no key:   SKIP_MODEL=1 harbor/watch_one/run_all.sh none 0   (ORACLE_K=1 when memory is short)
```

`run_all.sh` runs these steps in order:

1. Builds the task in Docker.
2. Checks that the agent network is the model-endpoint allowlist and that the verifier is offline.
3. Runs `harbor lint`.
4. Runs the oracle ×3 (`ORACLE_K`) and nop ×1, then the model with
   `-k K -n 2 --ak disable_web_search=true`. All runs use Harbor 0.26 from source (`HARBOR_SRC`,
   default `../../harbor` beside the repo's parent folder).
5. Summarises with `spikes/keyless/report/` (Python in Docker).
6. Logs, for each trial:
   - the verifier's time and peak memory;
   - the agent's time against its 3 h timeout, and whether the timeout bound.
7. Scans everything saved for API keys.


With `AGENT=codex`, the task is built with the `chatgpt.com` allowlist and Codex runs instead of OpenCode.

To build by hand (Python only in Docker):

```
docker run --rm -m 2g -v "$PWD:/repo:ro" -v "$PWD/harbor/watch_one/out:/out" keyless-grade \
    python3 -B -I /repo/harbor/watch_one/build_task.py /out/task --agent opencode|codex|oracle [--grader one-job]
```

`--agent` changes only `allowed_hosts`:

- for opencode and oracle, the major model endpoints and nothing else: `api.anthropic.com`, `api.openai.com`,
  `generativelanguage.googleapis.com` and `openrouter.ai`, so `-m provider/model` works for any of those providers;
- `chatgpt.com` and `api.openai.com` for codex.

Both OpenCode 1.19.5 and Codex 0.169.0 are installed in the image, so nothing is fetched at run
time. The oracle runs on the same task as the OpenCode runs.

## The interface (B: Decisions 15:44, run-readiness 17:40) and how the task meets it

| | |
|---|---|
| Delivery | `/app/delivery`: `movement.json` (8 h barrel), `variant_6h.json` (6 h barrel), `assembly.json`, `parts/<name>.step`, `scripts/` (optional). It starts empty, and the build refuses a pre-filled one. |
| Agent's `/app` | `instruction.md`, `FORMAT.md`, `datasheets/` (DS-W01..W04, DS-101, DS-201, DS-301 and `INDEX.md`; no QA-W100), `supplied/BR-096-30.stl`, `BR-096-45.stl`, `BR-096-66.stl` (one mesh per catalogue barrel), `tools/kernel.py`, `tools/check_format.py` and an empty `delivery/`. The files are taken by allowlist from `environment/make_bundle_job.py OUT`. |
| Brief | The task's `instruction.md` is the canary followed by the bundle's `instruction.md` (a copy of `environment/public/job/PROMPT.md`). |
| Grader | `tests/test.sh` writes reward 0, then runs `python3 -I /tests/grade_watch.py /app/delivery --reward /logs/verifier/reward.txt --details /logs/verifier/details.json` from `/tests`, with `geometry/` and A's `spikes/keyless/` modules (`constants.py`, `engine.py`, `grade.py`; `build_task.py` list `A_KEYLESS`) beside it, under `/usr/bin/time -v`. The grader writes 0 first and then one reward. The grader, `geometry/` and those modules are baked into the verifier image (`tests/Dockerfile`), never into the agent image. |
| Artifacts | `["/app/delivery"]`, all of it, `scripts/` included. Harbor saves the agent log (OpenCode's output and `trajectory.json`) with every trial in `agent/`. |
| Oracle | `solution/solve.sh` runs `reference_watch.py /app/delivery --job` in the container (about 40 s). No answer is stored in the task. |

`task.toml` settings:

- **Agent:** 3 h (`timeout_sec = 10800`; B's smoke runs took 33 to 61 min), 4 CPUs, 4 GB, `allowlist` to the model endpoints only (no web, no package registries).
- **Verifier:** `separate`, `no-network`, 4 GB, 7800 s for the one-job grader (it stops itself at 7200 s, 1800 s per check), so Harbor never cuts it off before it writes a reward.
- **Metadata:** expert and junior hours, both marked as author estimates.
- **Image pins:** python:3.12-slim, cadquery 2.8.0, manifold3d 3.5.5, scipy 1.18.1, numpy 2.5.4 and
  trimesh 5.2.1, plus `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=128000`.

`build_task.py` refuses to write the task if any of these would enter the agent's build context:

- a path outside the allowlist;
- folders named `tests`, `solution`, `anchors`, `realcad`, `report`, `runs`, `review`, `geometry` or `.git`;
- files named `SOLUTION.md`, `STEP_BY_STEP.md`, `CONTEXT.md`, `TRACEABILITY.md`, `TRACEABILITY_WATCH.md`, `PROMPT.md`, `SESSION.md` or `CLAUDE.md`;
- a renamed copy of a secret file. It checks sha256 against everything under `tests/`, `solution/`,
  `geometry/` and `spikes/keyless/{docs,realcad,report,runs}`, the keyless grader, engine and reference,
  `TRACEABILITY.md`, `TRACEABILITY_WATCH.md`, `SESSION.md`, `CLAUDE.md` and `SPEC.md`;
- the `NOT-FOR-AGENT` mark.

One copy is allowed on purpose: `tools/kernel.py`, made from `geometry/core.py`.

## The grader switch

`build_task.py` has one line, `GRADER = "one-job"`, which you can also set with `--grader` or
`GRADER=` for `run_all.sh`. Each entry in `GRADERS` carries:

- the grader arguments;
- how to take B's bundle;
- the brief;
- the repo files for the verifier image and for `solution/`;
- the reference command;
- the verifier timeout and memory.

**`one-job`** (the default) is the one-delivery grader of `SPEC.md` 0.8, P1 to P4, set up as in the
table above. The `description` and `difficulty_explanation` in `task.toml` describe this grader.

**`spec06-stage1`** is the earlier placeholder, kept only for comparison. It runs the SPEC 0.6
`--stage 1` grader on `movement.json`, with the old bundle mapped onto this layout and
`PROMPT_PLACEHOLDER.md` as the brief.

`A_DATASHEETS` adds A's keyless sheets (`spikes/keyless/datasheets`) to `datasheets/` when P5, crown
winding, joins. Its values are `()` today and `"ALL"` then. B's `make_bundle_job.py` has its own hook
for this (`EXTERNAL_SHEETS`), so only one of the two should be used. The build fails if the same
sheet would come from both.

## Validation

The commands and results are in the latest workstream A entry in `SESSION.md`. `IMAGE_CONTENTS.txt` is a
listing of the agent image's `/app` made on 14 Nov 23:27 from an earlier commit (single `barrel.stl`,
QA-W100, DS-401 and DS-501); the current `/app` is the one in the table above.
