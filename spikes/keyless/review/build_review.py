"""Build a Harbor judge task for one finished keyless trial (process review, outside the verifier).

    python build_review.py TRIAL_DIR OUT_TASK_DIR --judge codex|opencode

TRIAL_DIR is a Harbor trial folder (agent/opencode.txt or agent/codex.txt, verifier/details.json).
The judge's image holds /app/TASK.md (the brief), /app/evidence.txt (every command and output, in
order) and /app/details.json (the grader's results). The judge writes /app/review.json. The review
verifier (check_review.py) keeps only quotes found verbatim in evidence.txt.
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYLESS = os.path.dirname(HERE)
MAX_EVIDENCE = 400_000      # characters; long outputs are cut in the middle

AGENTS = {
    "codex": ("npm install -g @openai/codex && codex --version", "chatgpt.com"),
    "opencode": ("npm install -g opencode-ai@1.19.5 && opencode --version", "api.anthropic.com"),
}

DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl bash ripgrep ca-certificates nodejs npm \\
 && {agent_install} && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY app/ /app/
"""

TASK_TOML = """schema_version = "1.3"
artifacts = ["/app/review.json"]

[task]
name = "junction/keyless-review"
authors = ["Board in a Box team, Junction 2026 (workstream A)"]
description = "Process review of one keyless-works trial against a fixed rubric, with verbatim evidence."
keywords = ["review", "rubric"]

[agent]
timeout_sec = 1200.0

[verifier]
timeout_sec = 120.0
environment_mode = "separate"
network_mode = "no-network"

[verifier.environment]
cpus = 1
memory_mb = 1024

[environment]
network_mode = "allowlist"
allowed_hosts = ["{host}"]
build_timeout_sec = 900.0
cpus = 2
memory_mb = 2048
"""

TEST_SH = """#!/bin/bash
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt
python3 -I /tests/check_review.py /app/review.json /tests/evidence.txt --reward /logs/verifier/reward.txt \\
  --details /logs/verifier/review_checked.json > /logs/verifier/check.log 2>&1
cp /app/review.json /logs/verifier/review_raw.json 2>/dev/null
cat /logs/verifier/check.log
"""


def clip(s, n=6000):
    s = s if isinstance(s, str) else json.dumps(s)
    return s if len(s) <= n else s[: n // 2] + "\n...[cut]...\n" + s[-n // 2:]


def evidence(trial):
    out = []
    oc = os.path.join(trial, "agent", "opencode.txt")
    cx = os.path.join(trial, "agent", "codex.txt")
    if os.path.exists(oc):
        for line in open(oc, errors="replace"):
            try:
                j = json.loads(line)
            except ValueError:
                continue
            if j.get("type") == "tool_use":
                p = j.get("part", {})
                st = p.get("state", {})
                inp = st.get("input", {})
                cmd = inp.get("command") if isinstance(inp, dict) and "command" in inp else json.dumps(inp)
                out.append("=== CMD (%s)\n%s" % (p.get("tool"), clip(cmd)))
                out.append("=== OUT\n%s" % clip(st.get("output", "")))
    elif os.path.exists(cx):
        for line in open(cx, errors="replace"):
            try:
                j = json.loads(line)
            except ValueError:
                continue
            it = j.get("item", {})
            if j.get("type") == "item.completed" and it.get("type") == "command_execution":
                out.append("=== CMD (shell)\n%s" % clip(it.get("command", "")))
                out.append("=== OUT\n%s" % clip(it.get("aggregated_output", "")))
            elif j.get("type") == "item.completed" and it.get("type") == "file_change":
                out.append("=== CMD (file_change)\n%s" % clip(it.get("changes", "")))
    else:
        raise SystemExit("no transcript in %s" % trial)
    text = "\n".join(out)
    if len(text) > MAX_EVIDENCE:
        text = text[: MAX_EVIDENCE // 2] + "\n...[cut]...\n" + text[-MAX_EVIDENCE // 2:]
    return text


def main(argv):
    trial, out = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    judge = dict(zip(argv[2:], argv[3:])).get("--judge", "opencode")
    if os.path.exists(out):
        shutil.rmtree(out)
    app = os.path.join(out, "environment", "app")
    os.makedirs(app)
    ev = evidence(trial)
    open(os.path.join(app, "evidence.txt"), "w").write(ev)
    shutil.copyfile(os.path.join(trial, "verifier", "details.json"), os.path.join(app, "details.json"))
    shutil.copyfile(os.path.join(KEYLESS, "docs", "PROMPT.md"), os.path.join(app, "TASK.md"))
    prompt = open(os.path.join(KEYLESS, "docs", "JUDGE_PROMPT.md")).read().split("-->", 1)[1].lstrip()
    open(os.path.join(out, "instruction.md"), "w").write(prompt)
    open(os.path.join(out, "environment", "Dockerfile"), "w").write(DOCKERFILE.replace("{agent_install}", AGENTS[judge][0]))
    open(os.path.join(out, "task.toml"), "w").write(TASK_TOML.replace("{host}", AGENTS[judge][1]))
    tests = os.path.join(out, "tests")
    os.makedirs(tests)
    shutil.copyfile(os.path.join(HERE, "check_review.py"), os.path.join(tests, "check_review.py"))
    open(os.path.join(tests, "evidence.txt"), "w").write(ev)
    open(os.path.join(tests, "test.sh"), "w").write(TEST_SH)
    os.chmod(os.path.join(tests, "test.sh"), 0o755)
    os.makedirs(os.path.join(out, "solution"))
    with open(os.path.join(out, "solution", "solve.sh"), "w") as f:
        f.write('#!/bin/bash\necho \'{"verified":{"score":0,"evidence":[]},"consequences":{"score":0,"evidence":[]},'
                '"recovery":{"score":0,"evidence":[]},"used_information":{"score":0,"evidence":[]}}\' > /app/review.json\n')
    os.chmod(os.path.join(out, "solution", "solve.sh"), 0o755)
    print("review task written to", out, "evidence chars", len(ev))


if __name__ == "__main__":
    main(sys.argv[1:])
