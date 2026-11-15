#!/bin/bash
# The checked-in task (task/) on Modal sandboxes, with one command:
#
#   harbor/watch_one/run_modal.sh                          # reference (oracle) and do-nothing (nop) only: no model key
#   harbor/watch_one/run_modal.sh openai/gpt-6.1-sol 3     # then MODEL, K runs, under OpenCode, web search off
#   harbor/watch_one/run_modal.sh anthropic/claude-opus-5-5 3
#
# Before the first run, once:
#   uv tool install 'harbor[modal]'      # Harbor 0.26 or later, with its Modal extra
#   modal token new                      # or: export MODAL_TOKEN_ID=... MODAL_TOKEN_SECRET=...
# For a model run, the key of the model's provider must be in this shell (never in a file in the repo):
#   export OPENAI_API_KEY=...            # openai/...
#   export ANTHROPIC_API_KEY=...         # anthropic/...
#   export GEMINI_API_KEY=...            # gemini/... or google/...
# Harbor passes the key to the agent; it is not written to the job folder by this script.
#
# Environment (optional): OUT (jobs folder, default jobs-modal), N (concurrent trials, default 3),
#   SKIP_REF=1 (skip oracle and nop), ENVIRONMENT (default modal; "docker" runs the same thing locally),
#   EFFORT (passed as --effort, e.g. low), EXTRA (extra harbor run arguments).
set -uo pipefail

MODEL=${1:-}
K=${2:-3}
HERE=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$HERE/../.." && pwd)
TASK=$REPO/task
OUT=${OUT:-$REPO/jobs-modal}
N=${N:-3}
ENVIRONMENT=${ENVIRONMENT:-modal}
TS=$(date +%Y%m%d-%H%M%S)

say() { echo "[$(date +%H:%M:%S)] $*"; }
die() { echo "ERROR: $*" >&2; exit 2; }

# ---- checks that cost nothing ----
command -v harbor >/dev/null || die "harbor not found. Install it:  uv tool install 'harbor[modal]'"
HV=$(harbor --version 2>/dev/null | tail -1)
case "$HV" in
  0.2[6-9]*|0.[3-9]*|[1-9]*) ;;
  *) die "Harbor $HV found; 0.26 or later is needed (earlier versions reinstall OpenCode at run time, which the task's network allowlist blocks)" ;;
esac
[ -f "$TASK/task.toml" ] || die "no task at $TASK"
if [ "$ENVIRONMENT" = modal ]; then
  if [ -z "${MODAL_TOKEN_ID:-}" ] && [ ! -f "$HOME/.modal.toml" ]; then
    die "no Modal login found. Run:  modal token new   (or export MODAL_TOKEN_ID and MODAL_TOKEN_SECRET)"
  fi
fi
if [ -n "$MODEL" ]; then
  case "$MODEL" in
    openai/*)            KEY=OPENAI_API_KEY ;;
    anthropic/*)         KEY=ANTHROPIC_API_KEY ;;
    gemini/*|google/*)   KEY=GEMINI_API_KEY ;;
    openrouter/*)        KEY=OPENROUTER_API_KEY ;;
    *)                   KEY= ;;
  esac
  if [ -n "$KEY" ] && [ -z "${!KEY:-}" ]; then
    die "$MODEL needs $KEY in this shell:  export $KEY=...   (do not put it in a file in the repo)"
  fi
fi
say "Harbor $HV, environment $ENVIRONMENT, task $TASK, results in $OUT"
harbor lint "$TASK" >/dev/null 2>&1 && say "lint: clean" || say "lint: findings (run: harbor lint task)"
mkdir -p "$OUT"

rewards() {   # print the reward of every trial of one job
  local job=$1 found=0
  for r in "$OUT/$job"/*/verifier/reward.txt; do
    [ -f "$r" ] || continue
    found=1
    say "  $(basename "$(dirname "$(dirname "$r")")"): reward $(tr -d '\n' < "$r")"
  done
  [ $found = 1 ] || say "  no reward file under $OUT/$job (the trial did not reach the verifier; see the job's log)"
}

# ---- reference and do-nothing (no key) ----
if [ "${SKIP_REF:-0}" != 1 ]; then
  say "oracle (the reference, expected reward 1.0)"
  harbor run -p "$TASK" -a oracle -e "$ENVIRONMENT" -k 1 -n 1 -y -o "$OUT" --job-name "oracle-$TS" ${EXTRA:-} \
    || say "oracle job exited non-zero"
  rewards "oracle-$TS"
  say "nop (does nothing, expected reward 0.0)"
  harbor run -p "$TASK" -a nop -e "$ENVIRONMENT" -k 1 -n 1 -y -o "$OUT" --job-name "nop-$TS" ${EXTRA:-} \
    || say "nop job exited non-zero"
  rewards "nop-$TS"
fi

# ---- the model ----
if [ -n "$MODEL" ]; then
  SLUG=$(echo "$MODEL" | tr '/:' '__')
  say "$MODEL x$K under OpenCode, web search off"
  # shellcheck disable=SC2086
  harbor run -p "$TASK" -a opencode -m "$MODEL" -e "$ENVIRONMENT" -k "$K" -n "$N" \
    --ak disable_web_search=true ${EFFORT:+--effort "$EFFORT"} ${EXTRA:-} \
    -y -o "$OUT" --job-name "model-$SLUG-$TS" || say "model job exited non-zero"
  rewards "model-$SLUG-$TS"
fi

say "done. Per trial: $OUT/<job>/<trial>/verifier/{reward.txt,details.json}; the delivery is under the trial's artifacts."
# last line of defence: a key must never be in what we share
if grep -rIlE "sk-ant-[A-Za-z0-9_-]{20,}|sk-(proj-)?[A-Za-z0-9_-]{32,}|AIza[0-9A-Za-z_-]{30,}" "$OUT" >/dev/null 2>&1; then
  say "WARNING: something that looks like an API key is in $OUT. Do not push that folder before removing it."
else
  say "key scan of $OUT: nothing that looks like an API key"
fi
