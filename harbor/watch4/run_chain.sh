#!/bin/bash
# Run one frozen four-stage watch chain in Harbor, one single-step task per stage (see build_stage.py).
#   harbor/watch4/run_chain.sh WORK_DIR CHAIN_NAME [AGENT] [MODEL]
# AGENT codex (default): MODEL defaults to openai/gpt-6.1-sol; needs CODEX_FORCE_AUTH_JSON=1 and a Codex
#   login on this machine. Codex's built-in web search is turned off (--ak web_search=disabled), since the
#   chatgpt.com allowlist alone would let it through.
# AGENT opencode: MODEL e.g. anthropic/claude-haiku-5-5. Runs Harbor 0.26 from source (HARBOR_SRC), because
#   0.25 always reinstalls OpenCode at run time and the allowlist blocks that. The key comes from
#   ~/.harbor-secrets/anthropic.env, loaded into one subshell only, never printed or written. The chain stops
#   after a stage once its cost (OpenCode step_finish events) passes MAX_COST dollars (default 3).
#   OPENCODE_AK adds agent options, e.g. "--ak reasoning_effort=low" (OpenCode --variant).
# Stage N+1 is built from the submission Harbor collected from stage N's trial
# (<trial>/artifacts/app/submission); the verifier gets that same snapshot as /tests/prev.
# Leaves WORK_DIR/CHAIN/sN (task), WORK_DIR/CHAIN/jobs (Harbor jobs), WORK_DIR/CHAIN/chain.log.
set -u
WORK=$1; CHAIN=$2; AGENT=${3:-codex}; MODEL=${4:-openai/gpt-6.1-sol}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-python3}
D=$WORK/$CHAIN; mkdir -p $D/jobs
prev=""
for st in 1 2 3 4; do
  if [ $st -gt 1 ]; then
    [ -f "$prev/movement.json" ] || { echo "stage $st skipped: no submission from stage $((st-1))" | tee -a $D/chain.log; break; }
    $PY $HERE/build_stage.py $st $D/s$st --prev $prev --name watch4-$CHAIN-s$st --agent $AGENT > /dev/null || exit 1
  else
    $PY $HERE/build_stage.py 1 $D/s1 --name watch4-$CHAIN-s1 --agent $AGENT > /dev/null || exit 1
  fi
  echo "stage $st start $(date +%H:%M:%S)" >> $D/chain.log
  if [ "$AGENT" = "opencode" ]; then
    ( set -a; . $HOME/.harbor-secrets/anthropic.env; set +a
      cd ${HARBOR_SRC:-/Users/mikbs/Desktop/dev/harbor} && uv run --quiet harbor run -p $D/s$st -a opencode -m $MODEL ${OPENCODE_AK:-} -y -o $D/jobs ) > $D/s$st.harbor.log 2>&1
  elif [ "$AGENT" = "codex" ]; then
    harbor run -p $D/s$st -a codex -m $MODEL --ak web_search=disabled -y -o $D/jobs > $D/s$st.harbor.log 2>&1
  else
    harbor run -p $D/s$st -a $AGENT -y -o $D/jobs > $D/s$st.harbor.log 2>&1
  fi
  job=$(ls -td $D/jobs/*/ | head -1)
  trial=$(ls -d ${job}*/ | grep -v -E '/(config|result)' | head -1)
  echo "$trial" > $D/s$st.trial
  r=$(cat ${trial}verifier/reward.txt 2>/dev/null || echo none)
  echo "stage $st end $(date +%H:%M:%S) reward $r trial $trial" >> $D/chain.log
  if [ "$AGENT" = "opencode" ]; then
    cost=$($PY $HERE/cost.py $D/jobs)
    echo "stage $st cost so far \$$cost" >> $D/chain.log
    if $PY -c "import sys; sys.exit(0 if float('$cost') > float('${MAX_COST:-3}') else 1)"; then
      echo "stopped: cost \$$cost passed \$${MAX_COST:-3}" >> $D/chain.log
      break
    fi
  fi
  prev=${trial}artifacts/app/submission
  [ -d "$prev" ] || prev=$(find ${trial}artifacts -type d -name submission | head -1)
done
echo done >> $D/chain.log
