#!/bin/bash
# Runs 2 and 3 per model from the frozen worktree at 071ab86; three in parallel per round; each graded by the runner.
F=/tmp/claude-0/frozen_071ab86
for r in 2 3; do
  for m in fable:claude-fable-5-2 opus:claude-opus-5-5 sonnet:claude-sonnet-5-5; do
    n=${m%%:*}; id=${m#*:}; R=/tmp/claude-0/runs/smoke${r}_$n; rm -rf $R
    $F/environment/run_clean_job.sh $R $id > $R.log 2>&1 &
    sleep 30
  done
  wait
  echo "round $r done $(TZ=Europe/Helsinki date +%H:%M)" >> /tmp/claude-0/runs/repeat.log
done
