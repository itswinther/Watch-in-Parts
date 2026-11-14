#!/bin/bash
# The one-brief watch task, end to end, with one command:
#
#   harbor/watch_one/run_all.sh MODEL K [OUT_DIR]
#   e.g. harbor/watch_one/run_all.sh anthropic/claude-opus-5-5 8
#
# 1. Builds the Harbor task (build_task.py, run inside Docker because B's bundle builder imports the
#    geometry module) and checks the agent network is the model-endpoint allowlist and the verifier is
#    offline.
# 2. Runs Harbor 0.26: the oracle (B's reference script, run in the container) ORACLE_K times, the nop
#    agent once, then MODEL K times, 2 at a time, with web tools denied (--ak disable_web_search=true).
# 3. Summarises with spikes/keyless/report/ (Python in Docker) and scans everything saved for a key.
#
# Needs: Docker, uv, a Harbor 0.26 checkout in HARBOR_SRC (default ../harbor next to the repo's parent,
# i.e. /Users/mikbs/Desktop/dev/harbor on Mikael's machine), and for the model run the key in
# ANTHROPIC_API_KEY, or KEY_FILE=path (bare key or ANTHROPIC_API_KEY=...). AGENT=codex runs Codex instead
# (task built with the chatgpt.com allowlist; Codex auth as harbor/watch4 does it, CODEX_FORCE_AUTH_JSON=1).
# The key is read into the Harbor subshell only; it is never printed or written.
#
# Environment (all optional): HARBOR_SRC, KEY_FILE, AGENT (opencode), ORACLE_K (3), NOP_K (1),
#   N_CONCURRENT (2), EXTRA_AK, GRADER (build_task.py's default), SKIP_BUILD=1, SKIP_REF=1,
#   SKIP_MODEL=1 (oracle and nop only, no key needed), DOCKER.
set -euo pipefail

MODEL=${1:?usage: run_all.sh MODEL K [OUT_DIR]   e.g. anthropic/claude-opus-5-5 8}
K=${2:?usage: run_all.sh MODEL K [OUT_DIR]}
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
OUT=${3:-$HERE/out/run-$(date +%Y%m%d-%H%M%S)}
mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
DOCKER=${DOCKER:-$(command -v docker || echo "$HOME/.docker/bin/docker")}
HARBOR_SRC=${HARBOR_SRC:-$(cd "$REPO/../.." 2>/dev/null && pwd)/harbor}
AGENT=${AGENT:-opencode}
ORACLE_K=${ORACLE_K:-3}; NOP_K=${NOP_K:-1}; N_CONCURRENT=${N_CONCURRENT:-2}
TASK=$OUT/task; JOBS=$OUT/jobs; LOG=$OUT/run_all.log
SLUG=$(echo "$MODEL" | tr '/:' '__'); TS=$(date +%Y%m%d-%H%M%S)
# the allowlist build_task.py writes for this agent (its HOSTS table); the check below accepts exactly that
case "$AGENT" in
  opencode) HOSTS_EXPECTED='"api.anthropic.com", "api.openai.com", "generativelanguage.googleapis.com", "openrouter.ai"' ;;
  codex) HOSTS_EXPECTED='"chatgpt.com", "api.openai.com"' ;;
  *) echo "AGENT must be opencode or codex" >&2; exit 2 ;; esac

say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$LOG"; }

# ---- Harbor 0.26 from source ----
[ -f "$HARBOR_SRC/pyproject.toml" ] || { echo "HARBOR_SRC=$HARBOR_SRC is not a Harbor checkout" >&2; exit 2; }
harbor() { uv run --quiet --directory "$HARBOR_SRC" harbor "$@"; }
HV=$(harbor --version 2>/dev/null | tail -1)
say "Harbor $HV, agent $AGENT, model $MODEL, k=$K, out $OUT"
case "$HV" in
  0.26*|0.27*|0.28*|0.29*|0.3*) ;;
  *) echo "Harbor $HV: 0.26 or later is needed (0.25 reinstalls OpenCode from npm at run time, which the" \
          "allowlist blocks)" >&2; exit 2 ;;
esac

if [ "${SKIP_MODEL:-0}" != 1 ] && [ "$AGENT" = opencode ] && [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -z "${KEY_FILE:-}" ]; then
  echo "Set ANTHROPIC_API_KEY, or KEY_FILE=path to a file with the key (or SKIP_MODEL=1)" >&2; exit 2
fi
if [ -n "${KEY_FILE:-}" ] && [ ! -r "$KEY_FILE" ]; then echo "KEY_FILE $KEY_FILE not readable" >&2; exit 2; fi

# ---- 1. build the task (in Docker) ----
if [ "${SKIP_BUILD:-0}" != 1 ]; then
  say "building the builder image from spikes/keyless/docker/Dockerfile"
  "$DOCKER" build -q -t keyless-build "$REPO/spikes/keyless/docker" >> "$LOG"
  say "writing the task to $TASK"
  "$DOCKER" run --rm --memory 2g -v "$REPO":/repo:ro -v "$OUT":/out keyless-build \
    python -B -I /repo/harbor/watch_one/build_task.py /out/task --agent "$AGENT" ${GRADER:+--grader "$GRADER"} | tee -a "$LOG"
fi
[ -f "$TASK/task.toml" ] || { echo "no task at $TASK" >&2; exit 1; }
grep -q 'network_mode = "allowlist"' "$TASK/task.toml" && grep -qF "allowed_hosts = [$HOSTS_EXPECTED]" "$TASK/task.toml" \
  || { echo "task.toml: the agent network is not the allowlist [$HOSTS_EXPECTED]; refusing to run" | tee -a "$LOG" >&2; exit 1; }
grep -q 'network_mode = "no-network"' "$TASK/task.toml" || { echo "task.toml: verifier is not no-network" >&2; exit 1; }
say "lint: $(harbor lint "$TASK" >> "$LOG" 2>&1 && echo clean || echo 'findings, see log')"
mkdir -p "$JOBS"

# ---- 2. reference runs (no key needed) ----
if [ "${SKIP_REF:-0}" != 1 ]; then
  say "oracle x$ORACLE_K (expected reward 1.0 each)"
  harbor run -p "$TASK" -a oracle -k "$ORACLE_K" -n 1 -y -o "$JOBS" --job-name "oracle-$TS" >> "$LOG" 2>&1 || say "oracle job exited non-zero"
  say "nop x$NOP_K (expected reward 0.0)"
  harbor run -p "$TASK" -a nop -k "$NOP_K" -n 1 -y -o "$JOBS" --job-name "nop-$TS" >> "$LOG" 2>&1 || say "nop job exited non-zero"
fi

# ---- 3. the model ----
if [ "${SKIP_MODEL:-0}" != 1 ]; then
  say "$MODEL x$K under $AGENT, web tools denied"
  (
    if [ -n "${KEY_FILE:-}" ]; then
      if grep -q '=' "$KEY_FILE"; then set -a; . "$KEY_FILE"; set +a
      else ANTHROPIC_API_KEY=$(tr -d ' \n\r' < "$KEY_FILE"); export ANTHROPIC_API_KEY; fi
    fi
    # shellcheck disable=SC2086
    harbor run -p "$TASK" -a "$AGENT" -m "$MODEL" -k "$K" -n "$N_CONCURRENT" \
      --ak disable_web_search=true ${EXTRA_AK:-} -y -o "$JOBS" --job-name "model-$SLUG-$TS"
  ) >> "$LOG" 2>&1 || say "model job exited non-zero (see $LOG)"
fi

# ---- 4. report (Python in Docker only) ----
say "summarising"
mkdir -p "$OUT/report"
"$DOCKER" run --rm --memory 1g -v "$REPO/spikes/keyless/report":/k:ro -v "$OUT":/o -v "$TASK":/task:ro python:3.12-slim sh -c '
  python -I /k/summarize.py /o/jobs --out /o/report --task /task --k 1,3 &&
  python -I /k/incidents.py /o/jobs --out /o/report/INCIDENTS.md &&
  python -I /k/index.py /o/jobs --out /o/report/INDEX.md --incidents /o/report/INCIDENTS.md' >> "$LOG" 2>&1 \
  || say "summary scripts exited non-zero (they were written for the keyless details format; see $LOG)"
# verifier time and peak memory per trial, from test.sh's /usr/bin/time lines
for f in "$JOBS"/*/*/verifier/test-stdout.txt; do
  [ -f "$f" ] && say "$(echo "$f" | sed "s|$JOBS/||; s|/verifier/test-stdout.txt||"): $(grep -E 'Elapsed|Maximum resident|^reward' "$f" | tr -s ' \t' ' ' | paste -sd ';' -)"
done

# agent timeout: did it bind? (per trial, from Harbor's result.json; needs jq)
AGENT_TIMEOUT=$(awk '/^\[agent\]/{a=1} a&&/^timeout_sec/{print int($3); exit}' "$TASK/task.toml")
if command -v jq >/dev/null; then
  for r in "$JOBS"/*/*/result.json; do
    [ -f "$r" ] || continue
    say "$(echo "$r" | sed "s|$JOBS/||; s|/result.json||"): $(jq -r --argjson t "$AGENT_TIMEOUT" '
      def secs(p): if p and p.started_at and p.finished_at then
        ((p.finished_at|sub("\\.[0-9]+Z$";"Z")|fromdate) - (p.started_at|sub("\\.[0-9]+Z$";"Z")|fromdate)) else null end;
      (secs(.agent_execution)) as $a | (.exception_info.exception_type // "none") as $e |
      "agent \($a // "?") s of \($t) s; verifier phase \(secs(.verifier) // "?") s; exception \($e); timeout bound: \(if ($e|test("Timeout")) or (($a // 0) >= $t) then "YES" else "no" end); reward_valid \(.reward_valid)"' "$r")"
  done
else
  say "jq not found: agent-timeout check skipped"
fi

# ---- 5. key scan ----
if grep -rIlE "sk-ant-[A-Za-z0-9_-]{10}|sk-proj-[A-Za-z0-9_-]{10}" "$OUT" 2>/dev/null | grep -v '/task/' ; then
  say "WARNING: a string like an API key appears in the files above; do not publish them"
else
  say "key scan: no API key string in $OUT"
fi
say "done: $OUT"
