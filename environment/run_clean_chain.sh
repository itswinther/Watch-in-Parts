#!/bin/bash
# Run the four watch stages (design, extend, change, assemble) with clean headless agents, one fresh conversation per stage.
#   environment/run_clean_chain.sh RUN_DIR MODEL
# RUN_DIR must be outside the repo (no CLAUDE.md above it). Leaves RUN_DIR/stageN/ and RUN_DIR/stageN.jsonl.
set -u
RUN=$1; MODEL=$2
REPO=$(cd "$(dirname "$0")/.." && pwd)
PROMPT='Your whole world is the current folder. Read INSTRUCTION.md and SPEC_WATCH.md, then do the task they describe.

Rules:
- Do not read, list or search anything outside the current folder. Do not use the network.
- Do not modify anything under tools/ or previous/. You may read them.
- Put your own scripts in a scripts/ subfolder.
- Run everything in the foreground. Do not end your turn while a job of yours is still running: nothing will wake you up, and whatever is in the submission folder when you stop is what gets graded.

Budget: about 35 minutes of work; you are stopped at 39. Submit early and resubmit whenever your work improves; only the last accepted submission counts.

When you finish, write a short factual report: what you submitted, how you checked it and against which requirements, the difficulties and dead ends in the order you hit them, and anything in the spec or tools that was ambiguous or broken.'
prev=""
for st in 1 2 3 4; do
  d=$RUN/stage$st
  if [ $st -gt 1 ]; then
    [ -f "$prev/movement.json" ] || { echo "stage $st skipped: no submission from stage $((st-1))" > $RUN/stage$st.skipped; break; }
    python3 $REPO/environment/make_bundle_watch.py $d --stage $st --prev $prev > /dev/null
  else
    python3 $REPO/environment/make_bundle_watch.py $d --stage 1 > /dev/null
  fi
  find $d -name __pycache__ | xargs -r rm -rf
  date +%s > $RUN/stage$st.start
  (cd $d && timeout 2340 claude -p "$PROMPT" --model $MODEL --permission-mode acceptEdits \
     --allowedTools "Bash" "Read" "Write" "Edit" "Glob" "Grep" --output-format stream-json --verbose \
     < /dev/null > $RUN/stage$st.jsonl 2> $RUN/stage$st.err)
  echo "stage $st exit $?" >> $RUN/chain.log
  date +%s > $RUN/stage$st.end
  prev=$d/submission
done
echo done >> $RUN/chain.log
