#!/bin/bash
# One clean headless agent conversation on the one-job watch brief, then grade the delivery.
#   environment/run_clean_job.sh RUN_DIR MODEL [TIMEOUT_S]
# RUN_DIR must be outside the repo (no CLAUDE.md in any parent folder). The agent's folder is RUN_DIR/app,
# built by environment/make_bundle_job.py; the brief's absolute /app paths are rewritten to RUN_DIR/app
# (in Harbor the folder is /app itself). Leaves RUN_DIR/agent.jsonl, agent.err, start, end, exit,
# reward.txt, details.json, grade.log.
# TIMEOUT_S (default 10800) is a safety stop, sized to never bind: check in the transcript that it did not.
set -u
RUN=$1; MODEL=$2; LIMIT=${3:-10800}
REPO=$(cd "$(dirname "$0")/.." && pwd)
case "$RUN" in "$REPO"*) echo "RUN_DIR must be outside the repo"; exit 2;; esac
APP=$RUN/app
mkdir -p "$RUN"
python3 "$REPO/environment/make_bundle_job.py" "$APP" > "$RUN/bundle.log" || { echo "bundle failed"; exit 2; }
find "$APP" -name __pycache__ | xargs -r rm -rf
grep -rlI "/app" "$APP" | xargs -r sed -i "s#/app#$APP#g"
PROMPT="Your whole working world is the folder $APP. Read $APP/instruction.md and do the job it describes.
Do not read, list or search anything outside $APP, and do not use the network."
date +%s > "$RUN/start"
(cd "$APP" && timeout "$LIMIT" claude -p "$PROMPT" --model "$MODEL" --permission-mode acceptEdits \
   --allowedTools "Bash" "Read" "Write" "Edit" "Glob" "Grep" --output-format stream-json --verbose \
   < /dev/null > "$RUN/agent.jsonl" 2> "$RUN/agent.err")
echo $? > "$RUN/exit"
date +%s > "$RUN/end"
(cd "$REPO/tests" && python3 -I grade_watch.py "$APP/delivery" --reward "$RUN/reward.txt" --details "$RUN/details.json" > "$RUN/grade.log" 2>&1)
echo "graded: $(cat "$RUN/reward.txt")" >> "$RUN/grade.log"
