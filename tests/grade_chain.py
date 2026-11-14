"""Grade a four-stage clean chain made by environment/run_clean_chain.sh.
    python tests/grade_chain.py RUN_DIR [--skip CHECK,CHECK]     (--skip is passed to grade_watch.py)
Prints one line per stage: score, time, tool calls, failed items, and whether any tool call left the folder.
The chain score is the product of the four stage scores; a stage not run or with nothing submitted counts 0."""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(run, skip=""):
    STAGES = (1, 2, 3, 4)
    scores = {st: 0.0 for st in STAGES}
    log = open(os.path.join(run, "chain.log")).read() if os.path.isfile(os.path.join(run, "chain.log")) else ""
    exits = dict(re.findall(r"stage (\d) exit (\d+)", log))
    prev_failed = set()
    for st in STAGES:
        d = os.path.join(run, "stage%d" % st)
        tr = os.path.join(run, "stage%d.jsonl" % st)
        if not os.path.isfile(tr):
            print("stage %d: not run" % st)
            continue
        L = [json.loads(l) for l in open(tr) if l.strip()]
        res = [x for x in L if x.get("type") == "result"]
        calls = [json.dumps(c.get("input")) for x in L if x.get("type") == "assistant"
                 for c in x["message"].get("content", []) if c.get("type") == "tool_use"]
        outside = [c for c in calls if re.search(r"/home/user|\.\./\.\.|/root|scratchpad/(?!chains/%s/stage%d)" % (os.path.basename(run), st), c)]
        sub = os.path.join(d, "submission")
        line = "stage %d: " % st
        code = exits.get(str(st))
        if code == "124":
            line += "KILLED BY THE TIME LIMIT; "
        elif not res:
            line += ("ended without a result (exit %s); " % code) if code else "still running; "
        else:
            line += "%.1f min, $%.2f; " % (res[-1].get("duration_ms", 0) / 60000, res[-1].get("total_cost_usd") or 0)
        line += "%d tool calls, %d outside; " % (len(calls), len(outside))
        if os.path.isfile(os.path.join(sub, "movement.json")) and (st < 4 or os.path.isfile(os.path.join(sub, "assembly.json"))):
            prev = os.path.join(run, "stage%d" % (st - 1), "submission")
            cmd = [sys.executable, "-I", "grade_watch.py", sub, "--stage", str(st), "--reward", os.path.join(run, "stage%d.reward" % st),
                   "--details", os.path.join(run, "stage%d.details.json" % st)] + (["--skip", skip] if skip else []) + (["--prev", prev] if st > 1 else [])
            p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True)
            g = json.loads(p.stdout.strip().splitlines()[-1])
            failed = [k for dd in (g["gates"], g["checks"]) for k, v in dd.items() if not v]
            scores[st] = g["reward"]
            line += "SCORE %.4f (p %.3f%s)" % (g["reward"], g["p"], ", kept factor %.3f" % g["kept_factor"] if "kept_factor" in g else "")
            if st in (2, 3):
                inherited = sorted(set(failed) & prev_failed)
                new = sorted(set(failed) - prev_failed)
                line += " inherited from stage %d: %s; new in stage %d: %s" % (st - 1, ",".join(inherited) or "-", st, ",".join(new) or "-")
            else:
                line += " failed: %s" % (",".join(failed) or "-")
            if st < 3:
                prev_failed = set(failed)
        else:
            line += "SCORE 0 (nothing complete submitted)"
        print(line)
        for o in outside[:3]:
            print("    outside:", o[:160])
    prod = 1.0
    for st in STAGES:
        prod *= scores[st]
    print("chain score (product of %d stages): %.4f   stages: %s" % (len(STAGES), prod, " ".join("%.4f" % scores[st] for st in STAGES)))


if __name__ == "__main__":
    a = sys.argv[1:]
    sk = a[a.index("--skip") + 1] if "--skip" in a else ""
    main(os.path.abspath([x for i, x in enumerate(a) if x != "--skip" and (i == 0 or a[i - 1] != "--skip")][0]), sk)
