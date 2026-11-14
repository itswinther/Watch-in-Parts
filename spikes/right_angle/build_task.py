"""Write the Harbor task for the right-angle winding spike.

    python build_task.py OUT_DIR [--agent codex|opencode] [--host HOST] [--oracle-submission DIR]

The agent image holds /app/BRIEF.md, /app/frozen/*.stl, /app/frozen.json and /app/arbor_square.stl.
The grader, its constants and its copy of the data go to tests/ only (uploaded to the separate,
no-network verifier). The reference's gear maker never enters the agent image.
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import constants as C  # noqa: E402

PROMPT = """Your whole world is the folder /app. Read /app/BRIEF.md and do the task it describes. Work in /app (it is your current folder).

Rules:
- Do not read, list or search anything outside /app. Do not use the network, and do not try to install packages: everything you need is installed (Python 3.12 with cadquery 2.8.0, manifold3d 3.5.5, numpy, scipy, trimesh).
- Do not modify anything under frozen/ or arbor_square.stl. You may read them.
- Put your own scripts in a scripts/ subfolder.
- Run everything in the foreground. Do not end your turn while a job of yours is still running: nothing will wake you up, and whatever is in /app/submission when you stop is what gets graded.

Budget: about 35 minutes of work; you are stopped at 40.

When you finish, write a short factual report: what you submitted, how you checked it and against which requirements, the difficulties and dead ends in the order you hit them, and anything in the brief that was ambiguous. End the report with one line that starts with "Outside access:" and says whether you used or tried to use the network or anything outside /app (say "none" if you did not).
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

AGENTS = {
    "codex": ("npm install -g @openai/codex && codex --version", "chatgpt.com"),
    "opencode": ("npm install -g opencode-ai@1.19.5 && opencode --version", "api.anthropic.com"),
}

TASK_TOML = """schema_version = "1.3"
artifacts = ["/app/submission"]

[task]
name = "junction/right-angle-winding"
description = "Keyless winding works at right angles under a frozen watch movement."

[metadata]
category = "engineering-design"

[agent]
timeout_sec = 2400.0

[verifier]
timeout_sec = 600.0
environment_mode = "separate"
network_mode = "no-network"

[verifier.environment]
build_timeout_sec = 1800.0
cpus = 4
memory_mb = 2048
storage_mb = 10240

[environment]
network_mode = "allowlist"
allowed_hosts = ["{host}"]
build_timeout_sec = 1800.0
cpus = 4
memory_mb = 2048
storage_mb = 10240
"""

TEST_SH = """#!/bin/bash
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt
cd /tests
python3 -I grade.py /app/submission /tests/data --reward /logs/verifier/reward.txt --details /logs/verifier/details.json > /logs/verifier/grade.log 2>&1
echo "grader exit $?" >> /logs/verifier/grade.log
tail -20 /logs/verifier/grade.log
"""


def brief():
    W = C.WEIGHTS
    tot = sum(W.values())
    s = C.SQUARE_SIDE
    return f"""# Keyless winding at right angles

A watch movement is already built and frozen: its plates, train and hands are in `frozen/`
(binary STL, millimetres, one closed solid per file, names in `frozen.json`). Its mainspring is
wound by turning the **barrel arbor**. Your job is the winding works on the underside of the
movement: a **winding stem** coming in through the case wall, turning about an axis at right angles
to the barrel arbor, and the wheels that make one turn of the stem wind the arbor.

## Frame

Right-handed, millimetres. The dial side is +z; the underside, where you work, is below the main
plate (the main plate's lowest face is z = -1.7). Angles follow the right-hand rule about an axis's
stated direction.

## What is supplied (do not modify)

- `frozen/*.stl`: the movement. Every part you add must stay clear of all of it, at rest and while
  winding. It is not changed by winding: the barrel arbor turns inside it.
- The **barrel arbor axis**: the z axis (x = 0, y = 0), direction +z.
- `arbor_square.stl`: the end of the barrel arbor, which turns with it. A round section of radius 0.5
  from z = -1.0 down to z = {C.SQUARE_Z[1]}, a **square** of side {s} (sides parallel to x and y,
  centred on the axis) from z = {C.SQUARE_Z[1]} down to z = {C.SQUARE_Z[0]}, and a flange of radius
  1.0 from z = {C.SQUARE_Z[0]} down to z = {C.SQUARE_Z[0] - 0.3:.1f}. Your **ratchet wheel** sits on this square.
- The **stem axis**: the line y = {C.STEM_Y}, z = {C.STEM_Z}, along x. Its direction is +x: from outside the
  case (at -x) into the movement.
- The **case**: a cylinder of radius {C.CASE_RADIUS} about the vertical line through
  x = {C.CASE_CENTRE[0]}, y = {C.CASE_CENTRE[1]}, from z = {C.CASE_Z[0]} to z = {C.CASE_Z[1]}.

## What you submit

`/app/submission/winding.json` and one binary STL per part in `/app/submission/parts/<name>.stl`.
Every part is one closed, manifold solid with positive volume (one shell). Names use letters, digits,
`_` and `-`, 1 to 40 characters; `arbor_square` is reserved. At most {C.MAX_TRIANGLES} triangles per file.
Parts are submitted **in their rest position**.

```json
{{
  "mobiles": {{
    "stem":  {{"point": [0, {C.STEM_Y}, {C.STEM_Z}], "direction": [1, 0, 0], "parts": ["..."]}},
    "some_wheel": {{"point": [x, y, z], "direction": [dx, dy, dz], "parts": ["..."]}},
    "arbor": {{"parts": ["..."]}}
  }},
  "fixed": ["..."],
  "meshes": [
    {{"driver": "stem", "driver_teeth": 12, "driven": "some_wheel", "driven_teeth": 36, "sense": "same"}}
  ]
}}
```

- A **mobile** is a set of parts that turn together about one axis (a point on it and a direction).
  `stem` and `arbor` are required. The stem's axis must be the stated stem axis (direction +x or -x).
  The arbor's axis is fixed (the z axis); list only your parts on it (your ratchet wheel); the
  supplied `arbor_square.stl` is added to it for you.
- **Fixed** parts do not move (bridges, posts, bearings).
- **Meshes**: each gear contact, driver first. Tooth counts are integers 3 to 400. `sense` says how the
  driven mobile turns about **its own stated direction** when the driver turns positively about
  **its** stated direction: `"same"` (also positively) or `"opposite"`. The driven mobile turns
  `driver_teeth / driven_teeth` as fast. Mobiles may be anywhere and point any way, as long as
  everything below holds.

## Requirements

Turning the stem **clockwise as seen from outside the case looking in** (positively about +x) must
wind the **barrel arbor clockwise as seen from +z** (negatively about +z).

How the grader checks your submission, in full. Two hard requirements; if either fails the score is 0:

- **Files**: the JSON and every named part load as described above.
- **Clear of the movement at rest**: no part of yours overlaps the frozen movement by more than
  {C.MAX_OVERLAP} mm3.

Then weighted checks (score = sum of the weights passed / {tot}):

- **Drive ({W['drive']})**: every declared mesh works, and a chain of working meshes leads from `stem` to
  `arbor`. A mesh works when, turning the driver through one full turn of whichever of the two wheels
  turns slower ({C.SAMPLES_PER_TOOTH} samples per driver tooth, the driven wheel following at the
  declared ratio and sense):
  - the two mobiles never overlap by more than {C.MAX_OVERLAP} mm3, and
  - at every sample, turning the driven mobile back (against its motion) by {C.NUDGE_FRACTION:.0%} of its
    tooth pitch, that is by {C.NUDGE_FRACTION} x 360 / driven_teeth degrees, makes it overlap the
    driver by at least {C.MIN_CONTACT} mm3, so the driver is always pushing it.
- **Direction ({W['direction']})** and **ratio ({W['ratio']})**: through the working meshes, the arbor turns
  the required way, and the stem turns between {C.RATIO_BAND[0]:g} and {C.RATIO_BAND[1]:g} times
  (inclusive) per turn of the arbor.
- **Clear ({W['clear']})**: each mobile turned alone through a full turn ({C.SPIN_SAMPLES} samples) overlaps your
  fixed parts and the frozen movement by at most {C.MAX_OVERLAP} mm3; mobiles that do not mesh with each
  other overlap each other by at most {C.MAX_OVERLAP} mm3 while the stem turns three times (48 samples,
  all mobiles at their declared rates); fixed parts do not overlap each other.
- **Held ({W['held']})**: every mobile except the arbor, moved {C.HOLD_SHIFT} mm along its axis either way
  and {C.HOLD_SHIFT} mm in either direction of two perpendicular directions across it, overlaps your
  fixed parts or the frozen movement by more than {C.MAX_OVERLAP} mm3 (so it cannot fall out).
- **Seated ({W['seated']})**: your arbor parts fill at least {C.SEAT_FILL:.0%} of the {C.SEAT_SHELL} mm thick shell
  around the square (z {C.SQUARE_Z[0]} to {C.SQUARE_Z[1]}) and do not enter the square (at most
  {C.MAX_OVERLAP} mm3).
- **Anchored ({W['anchored']})**: every fixed part, moved {C.ANCHOR_SHIFT} mm in some axis direction, touches the
  frozen movement or a fixed part that is itself anchored.
- **Bounds ({W['bounds']})**: every part lies inside the case; parts of the stem mobile may leave the
  case cylinder sideways, and some stem material reaches at least {C.STEM_PROTRUDE} mm outside the
  case radius (so it can be gripped).

Not checked in this task: minimum feature size, material, assembly order, the click that stops the
arbor running back.
"""


def main(argv):
    out = os.path.abspath(argv[0])
    opts = dict(zip(argv[1:], argv[2:]))
    agent = opts.get("--agent", "opencode")
    host = opts.get("--host", AGENTS[agent][1])
    if os.path.exists(out):
        shutil.rmtree(out)
    app = os.path.join(out, "environment", "app")
    os.makedirs(os.path.join(app, "submission", "parts"))
    shutil.copytree(os.path.join(HERE, "data", "frozen"), os.path.join(app, "frozen"))
    shutil.copyfile(os.path.join(HERE, "data", "frozen.json"), os.path.join(app, "frozen.json"))
    shutil.copyfile(os.path.join(HERE, "data", "arbor_square.stl"), os.path.join(app, "arbor_square.stl"))
    open(os.path.join(app, "BRIEF.md"), "w").write(brief())
    open(os.path.join(out, "environment", "Dockerfile"), "w").write(DOCKERFILE.replace("{agent_install}", AGENTS[agent][0]))
    open(os.path.join(out, "environment", ".dockerignore"), "w").write("**/__pycache__\n")
    open(os.path.join(out, "instruction.md"), "w").write(PROMPT)
    open(os.path.join(out, "task.toml"), "w").write(TASK_TOML.replace("{host}", host))
    tests = os.path.join(out, "tests")
    os.makedirs(tests)
    for f in ("grade.py", "constants.py"):
        shutil.copyfile(os.path.join(HERE, f), os.path.join(tests, f))
    shutil.copytree(os.path.join(HERE, "data"), os.path.join(tests, "data"))
    open(os.path.join(tests, "test.sh"), "w").write(TEST_SH)
    os.chmod(os.path.join(tests, "test.sh"), 0o755)
    sol = os.path.join(out, "solution")
    os.makedirs(sol)
    ref = opts.get("--oracle-submission")
    with open(os.path.join(sol, "solve.sh"), "w") as f:
        if ref:
            shutil.copytree(ref, os.path.join(sol, "ref"))
            f.write("#!/bin/bash\nset -e\nrm -rf /app/submission\ncp -r /solution/ref /app/submission\nls /app/submission/parts\n")
        else:
            f.write("#!/bin/bash\nexit 0\n")
    os.chmod(os.path.join(sol, "solve.sh"), 0o755)
    print("task written to", out)


if __name__ == "__main__":
    main(sys.argv[1:])
