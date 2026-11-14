# Frozen four-stage watch in Harbor (workstream A)

This packages B's staged watch (design, extend, change, assemble; `SPEC_WATCH.md`, `tests/grade_watch.py`)
as Harbor tasks. It answers B's requests to A from 04:55, 06:07 and 06:11 in `SESSION.md`. B's files
are used unchanged.

## Why one task per stage

Harbor's multi-step tasks don't fit this grader, for two reasons:

- A step's separate verifier receives only that step's artifacts. The frozen-file and kept-file
  checks need the previous stage's submission as a copy the agent cannot edit.
- On every step but the last, the agent container keeps running while the verifier runs. The grader
  peaks at about 5.7 GB, which does not fit beside a running agent on a 7.7 GB Docker VM.

So `build_stage.py` writes one single-step task per stage:

- **Stage 1** is built from nothing.
- **Stage N+1** is built on the host from the submission Harbor collected from stage N
  (`<trial>/artifacts/app/submission`). That snapshot goes to two places:
  - **`environment/app/work` and `environment/app/previous`:** what the agent receives. B's
    `make_bundle_watch.py` does this, as `run_clean_chain.sh` does.
  - **`tests/prev`:** uploaded only to the verifier and passed to the grader as `--prev`. The agent can
    edit its own `previous/`, but that changes nothing the grader reads.

Each stage is therefore a fresh container and a fresh agent conversation.

## Sandbox

- **Agent:** network is an allowlist containing only `chatgpt.com`, the Codex model endpoint. Codex,
  CadQuery 2.8.0, manifold3d 3.5.5 and SciPy are installed in the image, so nothing is fetched at run
  time.
- **Verifier:** a separate container with `network_mode = "no-network"`, 7 GB, 15 minutes. The
  agent container is stopped before it starts.
- **Agent image contents:** B's bundle (instruction, spec, barrel mesh, kernel, format-only submit)
  plus the previous submission. Never the grader, the hand speeds, the gear maker or the reference.
- **Reporting:** the instruction asks the agent to end its report with an `Outside access:` line.

## Run

```
export PATH=$HOME/.docker/bin:$PATH CODEX_FORCE_AUTH_JSON=1 PY=/path/to/python-with-cadquery
harbor/watch4/run_chain.sh WORK_DIR chainA                # codex, openai/gpt-6.1-sol
python3 harbor/watch4/build_stage.py 1 OUT --oracle-submission REF/stage1   # oracle replay smoke test
python3 harbor/watch4/metrics.py label=details.json ...   # size and margin numbers per stage
```

The reward is per stage. The chain score is the product of the four stage rewards, computed from
the four trials, because Harbor only offers `mean` and `final` across steps.

The grader's STEP reader sets `RLIMIT_AS`, which fails on macOS, so grading only works on Linux:
in the verifier container, or in Docker. `solution/reference_watch.py` also stops on macOS when
it builds the stage-4 assembly; stages 1 to 3 are written before that point.
