"""Write one Harbor task for one stage of the frozen four-stage watch (workstream A).

    python3 harbor/watch4/build_stage.py STAGE OUT_TASK_DIR [--prev HOST_SUBMISSION_DIR] [--name NAME]
                                         [--oracle-submission REFERENCE_STAGE_DIR] [--agent codex|opencode]

Why one task per stage, not one multi-step task: in Harbor 0.25/0.26 a step's separate verifier
only receives that step's own artifacts, and the agent container keeps running beside the
verifier on every step but the last. The grader needs the previous stage's submission as a copy
the agent cannot edit, and peaks at about 5.7 GB, which does not fit next to a running agent on
a 7.7 GB Docker VM. So each stage is a single-step task: a fresh container and a fresh Codex
conversation. Stage N+1 is built on the host from the submission Harbor collected from stage N
(`<trial>/artifacts/app/submission`). That snapshot goes twice into the new task:
  - into the agent image as work/ and previous/ (B's bundle builder does this), and
  - into tests/prev/, which only the verifier sees, and which the grader uses as --prev.
The agent can edit its own previous/ copy, but that changes nothing the grader reads.

Sandbox: the agent's network is an allowlist containing only its model endpoint (chatgpt.com for
Codex, api.anthropic.com for OpenCode); the harness is pre-installed so nothing is fetched at run time. The verifier is a separate
container with no network. Grader, geometry code and the previous snapshot are in tests/, which
Harbor uploads only to the verifier.
"""
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))

PROMPT = """Your whole world is the folder /app. Read /app/INSTRUCTION.md and /app/SPEC_WATCH.md, then do the task they describe. Work in /app (it is your current folder).

Rules:
- Do not read, list or search anything outside /app. Do not use the network, and do not try to install packages: everything you need is installed.
- Do not modify anything under tools/ or previous/. You may read them.
- Put your own scripts in a scripts/ subfolder.
- Run everything in the foreground. Do not end your turn while a job of yours is still running: nothing will wake you up, and whatever is in the submission folder when you stop is what gets graded.

Budget: about 35 minutes of work; you are stopped at 39. Submit early and resubmit whenever your work improves; only the last accepted submission counts.

When you finish, write a short factual report: what you submitted, how you checked it and against which requirements, the difficulties and dead ends in the order you hit them, and anything in the spec or tools that was ambiguous or broken. End the report with one line that starts with "Outside access:" and says whether you used or tried to use the network or anything outside /app (say "none" if you did not).
"""

DOCKERFILE = """FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl bash ripgrep ca-certificates nodejs npm \\
    libgl1 libglib2.0-0 libxrender1 libxext6 libsm6 \\
 && {agent_install} && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir cadquery==2.8.0 manifold3d==3.5.5 scipy==1.18.1 numpy trimesh \\
 && python -c "import cadquery, manifold3d, scipy; print('ok')"
WORKDIR /app
COPY app/ /app/
"""

TASK_TOML = """schema_version = "1.3"

[task]
name = "junction/{name}"
description = "Frozen mechanical watch, stage {stage} of 4 ({what})."

[metadata]
category = "engineering-design"

[agent]
timeout_sec = 2340.0

[verifier]
timeout_sec = 900.0
environment_mode = "separate"
network_mode = "no-network"

[verifier.environment]
build_timeout_sec = 1800.0
cpus = 4
memory_mb = 7168
storage_mb = 10240

[environment]
network_mode = "allowlist"
allowed_hosts = ["{host}"]
build_timeout_sec = 1800.0
cpus = 4
memory_mb = 6144
storage_mb = 10240

artifacts = ["/app/submission"]
"""

# Agent harness baked into the image (nothing is installed at run time; the allowlist would block it),
# and the one host it may reach: its model endpoint.
AGENTS = {
    "codex": ("npm install -g @openai/codex && codex --version", "chatgpt.com"),
    "opencode": ("npm install -g opencode-ai@1.19.5 && opencode --version", "api.anthropic.com"),
}

WHAT = {1: "design", 2: "extend with a 24-hour hand", 3: "change request", 4: "assemble"}

TEST_SH = """#!/bin/bash
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt
cd /tests
python3 -I grade_watch.py /app/submission --stage {stage} {prev} --reward /logs/verifier/reward.txt --details /logs/verifier/details.json > /logs/verifier/grade.log 2>&1
echo "grader exit $?" >> /logs/verifier/grade.log
tail -40 /logs/verifier/grade.log
"""


def main(argv):
    stage, out = int(argv[0]), os.path.abspath(argv[1])
    opts = dict(zip(argv[2:], argv[3:]))
    prev = opts.get("--prev")
    name = opts.get("--name", "watch4-s%d" % stage)
    agent = opts.get("--agent", "codex")
    if agent not in AGENTS:
        raise SystemExit("--agent must be one of %s" % ", ".join(AGENTS))
    if stage > 1 and not prev:
        raise SystemExit("stage %d needs --prev" % stage)
    if os.path.exists(out):
        shutil.rmtree(out)
    app = os.path.join(out, "environment", "app")
    cmd = [sys.executable, os.path.join(REPO, "environment", "make_bundle_watch.py"), app, "--stage", str(stage)]
    if prev:
        cmd += ["--prev", os.path.abspath(prev)]
    subprocess.run(cmd, check=True, cwd=REPO, stdout=subprocess.DEVNULL)
    for root, dirs, _ in os.walk(app):
        for d in dirs:
            if d == "__pycache__":
                shutil.rmtree(os.path.join(root, d))
    with open(os.path.join(out, "environment", "Dockerfile"), "w") as f:
        f.write(DOCKERFILE.replace("{agent_install}", AGENTS[agent][0]))
    with open(os.path.join(out, "environment", ".dockerignore"), "w") as f:
        f.write("**/__pycache__\n")
    with open(os.path.join(out, "instruction.md"), "w") as f:
        f.write(PROMPT)
    toml = TASK_TOML.format(name=name, stage=stage, what=WHAT[stage], host=AGENTS[agent][1])
    # artifacts is a top-level key; TOML needs it before the first table.
    toml = toml.replace('\nartifacts = ["/app/submission"]\n', "")
    toml = toml.replace('schema_version = "1.3"\n', 'schema_version = "1.3"\nartifacts = ["/app/submission"]\n')
    with open(os.path.join(out, "task.toml"), "w") as f:
        f.write(toml)
    tests = os.path.join(out, "tests")
    os.makedirs(tests)
    shutil.copyfile(os.path.join(REPO, "tests", "grade_watch.py"), os.path.join(tests, "grade_watch.py"))
    shutil.copytree(os.path.join(REPO, "geometry"), os.path.join(tests, "geometry"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    prev_arg = ""
    if prev:
        p = os.path.join(tests, "prev")
        os.makedirs(os.path.join(p, "parts"))
        shutil.copyfile(os.path.join(prev, "movement.json"), os.path.join(p, "movement.json"))
        for fn in os.listdir(os.path.join(prev, "parts")):
            shutil.copyfile(os.path.join(prev, "parts", fn), os.path.join(p, "parts", fn))
        prev_arg = "--prev /tests/prev"
    with open(os.path.join(tests, "test.sh"), "w") as f:
        f.write(TEST_SH.format(stage=stage, prev=prev_arg))
    os.chmod(os.path.join(tests, "test.sh"), 0o755)
    sol = os.path.join(out, "solution")
    os.makedirs(sol)
    ref = opts.get("--oracle-submission")
    with open(os.path.join(sol, "solve.sh"), "w") as f:
        if ref:
            # Replay a reference submission made on the host by solution/reference_watch.py (the gear
            # maker it needs never enters the agent image). The oracle copies it into place.
            shutil.copytree(ref, os.path.join(sol, "ref"), ignore=shutil.ignore_patterns("__pycache__"))
            f.write("#!/bin/bash\nset -e\nrm -rf /app/submission\ncp -r /solution/ref /app/submission\n"
                    "ls /app/submission\n")
        else:
            f.write("#!/bin/bash\n# Build with --oracle-submission DIR to replay the reference.\nexit 0\n")
    os.chmod(os.path.join(sol, "solve.sh"), 0o755)
    print("task written to", out)


if __name__ == "__main__":
    main(sys.argv[1:])
