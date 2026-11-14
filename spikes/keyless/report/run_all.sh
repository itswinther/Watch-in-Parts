#!/bin/bash
# Reproduce the keyless-works results with one command:
#
#   spikes/keyless/report/run_all.sh MODEL K [OUT_DIR]
#   e.g. spikes/keyless/report/run_all.sh anthropic/claude-opus-5-5 5
#
# 1. Builds the Harbor task from spikes/keyless (build_task.py, run inside Docker because it imports the
#    engine, which needs manifold3d), for OpenCode, and checks the agent network is an allowlist.
# 2. Runs Harbor: the oracle (reference solution) ORACLE_K times, the nop agent NOP_K times, and MODEL
#    under OpenCode K times, with web tools denied (--ak disable_web_search=true).
# 3. Writes OUT_DIR/report/{RESULTS.md,results.json,INDEX.md,INCIDENTS.md,INCIDENTS.json} (Python in
#    Docker, python:3.12-slim) and scans everything saved for an Anthropic key.
#
# Needs: Docker, uv, Harbor 0.26 (a checkout in HARBOR_SRC, or `harbor` 0.26 on PATH), and the model key
# in ANTHROPIC_API_KEY, or KEY_FILE=path to a file holding either the bare key or ANTHROPIC_API_KEY=....
# The key is read into the Harbor subshell only; it is never printed or written.
#
# Environment (all optional): HARBOR_SRC, KEY_FILE, ORACLE_K (3), NOP_K (1), N_CONCURRENT (2),
#   EXTRA_AK (e.g. "--ak reasoning_effort=high"), SKIP_BUILD=1 (reuse OUT_DIR/task), SKIP_REF=1 (skip
#   oracle and nop), DOCKER (docker binary).
set -euo pipefail

MODEL=${1:?usage: run_all.sh MODEL K [OUT_DIR]   e.g. anthropic/claude-opus-5-5 5}
K=${2:?usage: run_all.sh MODEL K [OUT_DIR]}
HERE=$(cd "$(dirname "$0")" && pwd)
KL=$(cd "$HERE/.." && pwd)
OUT=${3:-$PWD/keyless-run-$(date +%Y%m%d-%H%M%S)}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
DOCKER=${DOCKER:-$(command -v docker || echo "$HOME/.docker/bin/docker")}
ORACLE_K=${ORACLE_K:-3}; NOP_K=${NOP_K:-1}; N_CONCURRENT=${N_CONCURRENT:-2}
TASK=$OUT/task; JOBS=$OUT/jobs; LOG=$OUT/run_all.log
SLUG=$(echo "$MODEL" | tr '/:' '__'); TS=$(date +%Y%m%d-%H%M%S)

say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

# ---- Harbor 0.26 ----
if [ -n "${HARBOR_SRC:-}" ]; then
  harbor() { uv run --quiet --directory "$HARBOR_SRC" harbor "$@"; }
elif command -v harbor >/dev/null; then
  harbor() { command harbor "$@"; }
else
  echo "Harbor not found: set HARBOR_SRC to a Harbor 0.26 checkout, or install harbor 0.26" >&2; exit 2
fi
HV=$(harbor --version 2>/dev/null | tail -1)
say "Harbor $HV, model $MODEL, k=$K, out $OUT"
case "$HV" in
  0.26*|0.27*|0.28*|0.29*|0.3*) ;;
  *) echo "Harbor $HV: 0.26 or later is needed (0.25 reinstalls OpenCode from npm at run time, which the" \
          "task's allowlist blocks, so every model trial fails at agent setup)" >&2; exit 2 ;;
esac

# ---- key: checked here, loaded only into the model run's subshell ----
if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -z "${KEY_FILE:-}" ]; then
  echo "Set ANTHROPIC_API_KEY, or KEY_FILE=path to a file with the key" >&2; exit 2
fi
if [ -n "${KEY_FILE:-}" ] && [ ! -r "$KEY_FILE" ]; then echo "KEY_FILE $KEY_FILE not readable" >&2; exit 2; fi

# ---- 1. build the task (in Docker) ----
if [ "${SKIP_BUILD:-0}" != 1 ]; then
  say "building the builder image from spikes/keyless/docker/Dockerfile"
  "$DOCKER" build -q -t keyless-build "$KL/docker" >> "$LOG"
  say "writing the task to $TASK"
  "$DOCKER" run --rm --memory 2g -v "$KL":/src:ro -v "$OUT":/out keyless-build \
    python -B /src/build_task.py /out/task --agent opencode | tee -a "$LOG"
fi
[ -f "$TASK/task.toml" ] || { echo "no task at $TASK" >&2; exit 1; }
# exactly the model endpoints build_task.py allows for OpenCode (its AGENTS table), nothing else
HOSTS_EXPECTED='"api.anthropic.com", "api.openai.com", "generativelanguage.googleapis.com", "openrouter.ai"'
grep -q 'network_mode = "allowlist"' "$TASK/task.toml" && grep -qF "allowed_hosts = [$HOSTS_EXPECTED]" "$TASK/task.toml" \
  || { echo "task.toml: the agent network is not the allowlist [$HOSTS_EXPECTED]; refusing to run" | tee -a "$LOG" >&2; exit 1; }
grep -q 'network_mode = "no-network"' "$TASK/task.toml" || { echo "task.toml: verifier is not no-network" >&2; exit 1; }
mkdir -p "$JOBS"

# ---- 2. reference runs (no key needed) ----
if [ "${SKIP_REF:-0}" != 1 ]; then
  say "oracle x$ORACLE_K (expected reward 1.0 each)"
  harbor run -p "$TASK" -a oracle -k "$ORACLE_K" -n "$N_CONCURRENT" -y -o "$JOBS" --job-name "oracle-$TS" >> "$LOG" 2>&1 || say "oracle job exited non-zero"
  say "nop x$NOP_K (expected reward 0.0)"
  harbor run -p "$TASK" -a nop -k "$NOP_K" -y -o "$JOBS" --job-name "nop-$TS" >> "$LOG" 2>&1 || say "nop job exited non-zero"
fi

# ---- 3. the model ----
say "$MODEL x$K under OpenCode, web tools denied"
(
  if [ -n "${KEY_FILE:-}" ]; then
    if grep -q '=' "$KEY_FILE"; then set -a; . "$KEY_FILE"; set +a
    else ANTHROPIC_API_KEY=$(tr -d ' \n\r' < "$KEY_FILE"); export ANTHROPIC_API_KEY; fi
  fi
  # shellcheck disable=SC2086
  harbor run -p "$TASK" -a opencode -m "$MODEL" -k "$K" -n "$N_CONCURRENT" \
    --ak disable_web_search=true ${EXTRA_AK:-} -y -o "$JOBS" --job-name "model-$SLUG-$TS"
) >> "$LOG" 2>&1 || say "model job exited non-zero (see $LOG)"

# ---- 4. report (Python in Docker only) ----
say "summarising"
mkdir -p "$OUT/report"
"$DOCKER" run --rm --memory 1g -v "$KL":/k:ro -v "$OUT":/o -v "$TASK":/task:ro python:3.12-slim sh -c '
  python -I /k/report/summarize.py /o/jobs --out /o/report --task /task --k 1,3 &&
  python -I /k/report/incidents.py /o/jobs --out /o/report/INCIDENTS.md &&
  python -I /k/report/index.py /o/jobs --out /o/report/INDEX.md --incidents /o/report/INCIDENTS.md' | tee -a "$LOG"

# ---- 5. key scan ----
if grep -rIl "sk-ant-" "$OUT" 2>/dev/null | grep -v '/task/' ; then
  say "WARNING: a string like an Anthropic key appears in the files above; do not publish them"
else
  say "key scan: no sk-ant- string in $OUT"
fi
say "done: $OUT/report/RESULTS.md"
