#!/bin/bash
# Live status of one Harbor job folder: writes STATUS.md next to it every INTERVAL seconds until the job
# finishes. Plain shell (reads files and `docker stats` only).
#   runs/monitor.sh JOB_DIR OUT_STATUS_MD [INTERVAL]
JOB=$1; OUT=$2; INT=${3:-120}
export PATH=$HOME/.docker/bin:$PATH
STATE=$(mktemp -d)
while true; do
  now=$(date +%s)
  {
    echo "# Status $(date '+%H:%M:%S')"
    echo
    echo "| trial | elapsed min | log KB | last tool call | cost so far | reward | flags |"
    echo "|---|---|---|---|---|---|---|"
    for t in "$JOB"/*/; do
      [ -f "$t/config.json" ] || continue
      name=$(basename "$t")
      log=$(ls "$t"agent/opencode.txt "$t"agent/codex.txt 2>/dev/null | head -1)
      start=$(stat -f %B "$t" 2>/dev/null || echo $now)
      el=$(( (now - start) / 60 ))
      size=0; last="-"; cost="-"; flags=""
      if [ -n "$log" ]; then
        size=$(( $(stat -f %z "$log") / 1024 ))
        last=$(grep -o '"tool":"[a-z_]*"\|"type":"command_execution"' "$log" | tail -1 | tr -d '"' )
        cost=$(grep -o '"cost":[0-9.e-]*' "$log" | awk -F: '{s+=$2} END{if (NR) printf "$%.3f", s}')
        if grep -qiE 'sk-ant-|auth\.json|\.codex/|api\.openai\.com|backend-api|web_search_call|curl |wget ' "$log"; then
          flags="$flags NETWORK/AUTH-MENTION"
        fi
        if grep -qiE '"type":"error"|ECONNRESET|reconnect' "$log"; then flags="$flags ERROR/RECONNECT"; fi
        prev=$(cat "$STATE/$name.size" 2>/dev/null)
        if [ "$prev" != "$size" ]; then echo "$size" > "$STATE/$name.size"; echo "$now" > "$STATE/$name.time"; fi
        changed=$(cat "$STATE/$name.time" 2>/dev/null || echo $now)
        idle=$(( (now - changed) / 60 ))
        [ $idle -ge 10 ] && [ ! -f "$t/result.json" ] && flags="$flags STALL-${idle}min"
      fi
      rw=$(cat "$t/verifier/reward.txt" 2>/dev/null || echo "-")
      echo "| $name | $el | $size | $last | $cost | $rw | ${flags:--} |"
    done
    echo
    echo '```'
    docker stats --no-stream --format '{{.Name}} {{.MemUsage}} {{.CPUPerc}}' 2>/dev/null
    echo '```'
  } > "$OUT"
  [ -f "$JOB/result.json" ] && break
  sleep "$INT"
done
