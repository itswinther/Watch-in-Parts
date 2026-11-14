# The one-brief watch task in Harbor (workstream A)

This folder packages the decided task as one Harbor task. The decisions behind it are in `SESSION.md`:
Decisions 13:36, 14:08, 14:20 and 14:45, and B's interface at 15:44.

- **The task:** one professional brief, from start to finish, with nothing frozen and no method hints.
- **Parts:**
  - P1, going train and hands;
  - P2, 24-hour hand;
  - P3, 6-hour-barrel variant;
  - P4, assembly;
  - P5, crown winding, which joins once the keyless geometry is agreed.
- **Datasheets:** in the environment.
- **Scale:** demonstration scale, about 1.6x.
- **Reward:** 0.5 × weighted per-part share + 0.5 × whole build, computed over the graded parts. The
  agent never sees a verdict or a score.

The grader, the reference, `PROMPT.md`, `SOLUTION.md` and `STEP_BY_STEP.md` are workstream B's. This
folder only builds the Harbor task around them, and it calls or copies B's files without changing
them.

## The one command

```
harbor/watch_one/run_all.sh MODEL K [OUT_DIR]
# e.g. KEY_FILE=~/anthropic.key harbor/watch_one/run_all.sh anthropic/claude-opus-5-5 8
# oracle and nop only, no key:   SKIP_MODEL=1 harbor/watch_one/run_all.sh none 0
# once B's one-delivery grader is on main:   GRADER=one-job harbor/watch_one/run_all.sh MODEL 8
```

`run_all.sh` runs these steps in order:

1. Builds the task in Docker.
2. Checks that the agent network is the model-endpoint allowlist and that the verifier is offline.
3. Runs `harbor lint`.
4. Runs the oracle ×3 and nop ×1, then the model with `-k K -n 2 --ak disable_web_search=true`.
   All runs use Harbor 0.26 from source (`HARBOR_SRC`, default `../../harbor` beside the repo's
   parent folder).
5. Summarises with `spikes/keyless/report/` (Python in Docker).
6. Logs each trial's verifier time and peak memory.
7. Scans everything saved for API keys.

With `AGENT=codex`, the task is built with the `chatgpt.com` allowlist and Codex runs instead of OpenCode.

To build by hand (Python only in Docker):

```
docker run --rm -m 2g -v "$PWD:/repo:ro" -v "$PWD/harbor/watch_one/out:/out" keyless-grade \
    python3 -B -I /repo/harbor/watch_one/build_task.py /out/task --agent opencode|codex|oracle [--grader one-job]
```

`--agent` changes only `allowed_hosts`:

- `api.anthropic.com` for opencode and oracle;
- `chatgpt.com` for codex.

Both OpenCode 1.19.5 and Codex 0.169.0 are installed in the image, so nothing is fetched at run
time. The oracle runs on the same task as the OpenCode runs.

## The interface (B, Decisions 15:44) and how the task meets it

| | |
|---|---|
| Delivery | `/app/delivery`: `movement.json` (8 h barrel), `variant_6h.json` (6 h barrel), `assembly.json`, `parts/<name>.step`, `scripts/` (optional). It starts empty, and the build refuses a pre-filled one. |
| Agent's `/app` | `FORMAT.md`, `datasheets/`, `supplied/barrel.stl`, `tools/kernel.py`, `tools/check_format.py` and an empty `delivery/`. The files are taken by allowlist from whatever B's bundle builder writes (`make_bundle_job.py` for one-job). |
| Brief | `instruction.md`, with the canary first and HTML comments stripped. It comes from B's bundle builder if it writes `instruction.md` or `PROMPT.md`, or else from the grader entry's `prompt` path. `--prompt FILE` overrides both. |
| Grader | `tests/test.sh` writes reward 0, then runs `python3 -I /tests/grade_watch.py /app/delivery [--stage 1] --reward … --details …` under `/usr/bin/time -v`. It copies `details.json` to `/logs/verifier/` and overwrites `reward.txt` only if the grader exits 0. The grader and `geometry/` are baked into the verifier image (`tests/Dockerfile`), never into the agent image. |
| Artifacts | `["/app"]`. This covers `/app/delivery` and anything else the agent left (scripts, renders). |
| Oracle | `solution/solve.sh` runs B's `reference_watch.py` in the container and copies its delivery folder to `/app/delivery`. No answer is stored in the task. |

`task.toml` settings:

- **Agent:** 3 h (`timeout_sec = 10800`), 4 CPUs, 4 GB, `allowlist` to the model endpoint only.
- **Verifier:** `separate`, `no-network`, 4 GB; the timeout depends on the grader (below).
- **Metadata:** expert and junior hours, both marked as author estimates.
- **Image pins:** python:3.12-slim, cadquery 2.8.0, manifold3d 3.5.5, scipy 1.18.1, numpy 2.5.4 and
  trimesh 5.2.1, plus `OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX=64000`.

`build_task.py` refuses to write the task if any of these would enter the agent's build context:

- a path outside the allowlist;
- folders named `tests`, `solution`, `anchors`, `realcad`, `report`, `runs`, `review`, `geometry` or `.git`;
- files named `SOLUTION.md`, `STEP_BY_STEP.md`, `CONTEXT.md`, `TRACEABILITY.md`, `SESSION.md` or `CLAUDE.md`;
- a renamed copy of a secret file. It checks sha256 against everything under `tests/`, `solution/`,
  `geometry/` and `spikes/keyless/{docs,realcad,report,runs}`, the keyless grader, engine and reference,
  `TRACEABILITY.md`, `SESSION.md`, `CLAUDE.md` and `SPEC.md`;
- the `NOT-FOR-AGENT` mark.

Two copies are allowed on purpose: `tools/kernel.py` (a copy of `geometry/core.py`) and the barrel
mesh.

## The grader switch

`build_task.py` has one line, `GRADER = "spec06-stage1"`, which you can also set with
`--grader` or `GRADER=` for `run_all.sh`. Each entry in `GRADERS` carries:

- the grader arguments;
- how to take B's bundle;
- the brief;
- the repo files for the verifier image and for `solution/`;
- the reference command and its output folder;
- the verifier timeout and memory.

**`spec06-stage1` (today's placeholder)**

- **Grader:** B's SPEC 0.6 grader with `--stage 1` on `/app/delivery`. It grades only `movement.json`
  (going train and hands).
- **Bundle:** today's builder, mapped onto the new layout (`meshes/barrel.stl` becomes
  `supplied/barrel.stl`), plus `SPEC_WATCH.md` as the interim contract.
- **Brief:** `PROMPT_PLACEHOLDER.md`.
- **Oracle:** delivers the reference's `stage1`.
- **Verifier timeout:** 800 s, which is 2× the slowest grading seen (374 s, measured by B on a loaded
  host).

**`one-job` (B's 15:44 interface, exactly)**

- **Grader call:** `python3 -I /tests/grade_watch.py /app/delivery --reward F --details F`.
- **Bundle:** `environment/make_bundle_job.py OUT`, taken by allowlist; its `FORMAT.md` goes to `/app/FORMAT.md`.
- **Brief:** B's.
- **Oracle:** `reference_watch.py /app/delivery --job` writes the delivery in place.
- **Verifier timeout:** 2400 s for now.

Built today, `one-job` stops with "environment/make_bundle_job.py is not in this checkout yet", because
B's bundle builder is not on main yet. A dry build against a mock of it gives the 15:44 `/app` plus `FORMAT.md`.

`A_DATASHEETS` adds A's sheets from `spikes/keyless/datasheets` next to B's generated sheets:

- `()` today;
- named sheets, such as DS-101 and DS-201, if B's sheets cite them;
- `"ALL"` when P5 joins.

The build fails if the same sheet would come from both B and A.

## What B must provide

These make `GRADER=one-job` run with no other change. B gave the paths at 16:35, and the entry
uses them:

- **Bundle:** `environment/make_bundle_job.py OUT`, with no flags. It writes:
  - `instruction.md`, which becomes the task's `instruction.md` (not copied into `/app`);
  - `FORMAT.md`, which goes to `/app/FORMAT.md`;
  - `datasheets/DS-W01..W03`, `supplied/barrel.stl`, `tools/kernel.py` and `tools/check_format.py`;
  - an empty `delivery/`.
- **Reference:** `reference_watch.py /app/delivery --job` writes the delivery in place.

Still open with B:

1. **G and R on main:** the one-delivery `tests/grade_watch.py` and `make_bundle_job.py`.
2. **The grader's measured time and peak memory.** The verifier timeout becomes 2× the time (until
   then 2400 s), and memory stays 4 GB unless the peak is above about 3 GB.
3. **Any file the grader needs** beyond `tests/grade_watch.py` and `geometry/`, for example A's
   keyless engine for P5. It goes into the entry's `tests` list.


## Validation

The commands and results are in the latest workstream A entry in `SESSION.md`. The agent image's
`/app` tree is in `IMAGE_CONTENTS.txt`.
