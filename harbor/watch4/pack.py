"""Copy one Harbor chain's graded results into the repo, storing each distinct part file once.

    python3 harbor/watch4/pack.py CHAIN_WORK_DIR OUT_DIR

CHAIN_WORK_DIR is what run_chain.sh left (sN.trial files point at the trials). Per stage, OUT_DIR/stageN/
gets reward.txt, details.json, grade.log, the agent transcript (codex.txt or opencode.txt), the trial's
result.json, movement.json, assembly.json if any, scripts/, and parts.json (part file -> SHA-256).
Part files go once each to OUT_DIR/parts_store/<sha>.step.gz (deterministic gzip). Unpack by
reversing parts.json. The Codex/OpenCode login and API keys are not in any of these files; the
caller still scans the output for secrets before committing.
"""
import gzip
import hashlib
import json
import os
import shutil
import sys


def main(work, out):
    os.makedirs(os.path.join(out, "parts_store"), exist_ok=True)
    summary = []
    for st in (1, 2, 3, 4):
        tf = os.path.join(work, "s%d.trial" % st)
        if not os.path.isfile(tf):
            continue
        trial = open(tf).read().strip()
        d = os.path.join(out, "stage%d" % st)
        os.makedirs(d, exist_ok=True)
        for src, dst in (("verifier/reward.txt", "reward.txt"), ("verifier/details.json", "details.json"),
                         ("verifier/grade.log", "grade.log"), ("agent/codex.txt", "codex.txt"),
                         ("agent/opencode.txt", "opencode.txt"), ("result.json", "result.json")):
            p = os.path.join(trial, src)
            if os.path.isfile(p):
                shutil.copyfile(p, os.path.join(d, dst))
        sub = os.path.join(trial, "artifacts", "app", "submission")
        parts = {}
        if os.path.isdir(sub):
            for fn in ("movement.json", "assembly.json"):
                if os.path.isfile(os.path.join(sub, fn)):
                    shutil.copyfile(os.path.join(sub, fn), os.path.join(d, fn))
            if os.path.isdir(os.path.join(sub, "scripts")):
                shutil.copytree(os.path.join(sub, "scripts"), os.path.join(d, "scripts"), dirs_exist_ok=True)
            pdir = os.path.join(sub, "parts")
            for fn in sorted(os.listdir(pdir)) if os.path.isdir(pdir) else []:
                data = open(os.path.join(pdir, fn), "rb").read()
                h = hashlib.sha256(data).hexdigest()
                parts[fn] = h
                dst = os.path.join(out, "parts_store", h + ".step.gz")
                if not os.path.exists(dst):
                    with open(dst, "wb") as f:
                        f.write(gzip.compress(data, mtime=0))
        with open(os.path.join(d, "parts.json"), "w") as f:
            json.dump(parts, f, indent=1, sort_keys=True)
        r = open(os.path.join(d, "reward.txt")).read().strip() if os.path.isfile(os.path.join(d, "reward.txt")) else None
        summary.append({"stage": st, "reward": r, "trial": os.path.basename(trial.rstrip("/")), "parts": len(parts)})
    with open(os.path.join(out, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
