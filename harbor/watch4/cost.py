"""Sum the dollar cost of every OpenCode step_finish event under a jobs folder.
    python3 harbor/watch4/cost.py JOBS_DIR   ->  prints the total, e.g. 0.8123"""
import json
import os
import sys

total = 0.0
for root, _, files in os.walk(sys.argv[1]):
    for fn in files:
        if fn == "opencode.txt":
            with open(os.path.join(root, fn), errors="replace") as f:
                for line in f:
                    if '"step_finish"' not in line:
                        continue
                    try:
                        total += float(json.loads(line).get("part", {}).get("cost") or 0)
                    except ValueError:
                        pass
print("%.4f" % total)
