"""Write the Harbor task for the keyless-works spike.

    python build_task.py OUT_DIR [--agent codex|opencode] [--host HOST] [--oracle-submission DIR]

The agent image holds /app/BRIEF.md and /app/supplied/*.stl. The grader, engine, constants and data
go to tests/ only (uploaded to the separate, no-network verifier).
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import constants as C  # noqa: E402
import engine as E  # noqa: E402

PROMPT = """Your whole world is the folder /app. Read /app/BRIEF.md and do the task it describes. Work in /app (it is your current folder).

Rules:
- Do not read, list or search anything outside /app. Do not use the network, and do not try to install packages: everything you need is installed (Python 3.12 with cadquery 2.8.0, manifold3d 3.5.5, numpy, scipy, trimesh).
- Do not modify anything under supplied/. You may read it.
- Put your own scripts in a scripts/ subfolder.
- Run everything in the foreground. Do not end your turn while a job of yours is still running: nothing will wake you up, and whatever is in /app/submission when you stop is what gets graded.

Budget: about 50 minutes of work; you are stopped at 55.

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
name = "junction/keyless-works"
description = "Keyless works of a watch: winding, slipping, hand setting, graded by simulated contact."

[metadata]
category = "engineering-design"

[agent]
timeout_sec = 3300.0

[verifier]
timeout_sec = 1500.0
environment_mode = "separate"
network_mode = "no-network"

[verifier.environment]
build_timeout_sec = 1800.0
cpus = 4
memory_mb = 3072
storage_mb = 10240

[environment]
network_mode = "allowlist"
allowed_hosts = ["{host}"]
build_timeout_sec = 1800.0
cpus = 4
memory_mb = 2560
storage_mb = 10240
"""

TEST_SH = """#!/bin/bash
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt
cd /tests
python3 -I grade.py /app/submission /tests/data --reward /logs/verifier/reward.txt --details /logs/verifier/details.json --jobs 4 > /logs/verifier/grade.log 2>&1
echo "grader exit $?" >> /logs/verifier/grade.log
tail -20 /logs/verifier/grade.log
"""


def brief():
    W = C.WEIGHTS
    tot = sum(W.values())
    lo, hi = C.WIND_BAND
    return f"""# Keyless works

Design the **keyless works** of a watch: the mechanism behind the crown. Pushed in, turning the
crown winds the mainspring one way and slips harmlessly the other way; pulled out, it sets the hands
and does not wind. Your mechanism is judged by simulating it, contact by contact.

## Frame and units

Right-handed, millimetres. z points towards the main plate. Angles follow the right-hand rule about
a stated direction.

- The **stem axis** is the x axis (y = 0, z = 0), and the crown end is at +x (outside the case).
- **Position 1** (pushed in) is the stem as you submit it. **Position 2** (pulled out) is the stem
  moved {C.PULL} towards +x.
- **Forward** is turning the crown clockwise as seen from outside the case looking in (from +x
  towards -x), that is a negative rotation about +x. **Backward** is the opposite.
- The **case** is a cylinder of radius {C.CASE_RADIUS} about the vertical line through
  x = {C.CASE_CENTRE[0]}, y = {C.CASE_CENTRE[1]}, from z = {C.CASE_Z[0]} to z = {C.CASE_Z[1]}.

## Supplied parts (`/app/supplied/*.stl`, binary STL; do not modify)

- `main_plate`, `dial_plate`: fixed plates at z 2.6 to 3.2 and z -3.2 to -2.6.
- `barrel_arbor`: the barrel arbor, turning about the vertical line through
  x = {C.BARREL_AXIS[0]}, y = {C.BARREL_AXIS[1]}. **Winding turns it anticlockwise as seen from +z** (positive
  about +z). The **mainspring** always urges it the other way (see the simulation rules): something
  must stop it running back.
- `minute_wheel` (36 teeth, module 0.2, z -2.4 to -1.9) on the fixed `minute_post`: a stand-in for
  the motion work, turning freely about the vertical line through x = {C.MINUTE_AXIS[0]}, y = {C.MINUTE_AXIS[1]}.
  Hand setting means turning it.

## What you submit

`/app/submission/keyless.json` and one binary STL per part in `/app/submission/parts/<name>.stl`,
each part one closed manifold solid with positive volume, **in position 1, at rest**. Names use
letters, digits, `_` and `-`, 1 to 40 characters; the supplied names are reserved. At most 40 parts
and {C.MAX_TRIANGLES} triangles per file.

```json
{{
  "mobiles": {{
    "stem":   {{"kind": "stem", "parts": ["..."]}},
    "barrel": {{"kind": "barrel", "parts": ["..."]}},
    "a_wheel": {{"kind": "free", "dof": "rot", "point": [x, y, z], "direction": [dx, dy, dz], "parts": ["..."]}},
    "a_slider": {{"kind": "spring", "dof": "slide", "direction": [1, 0, 0], "rest": -1, "on_stem": true, "parts": ["..."]}},
    "a_lever": {{"kind": "spring", "dof": "rot", "point": [x, y, z], "direction": [0, 0, 1], "rest": 1, "parts": ["..."]}}
  }},
  "fixed": ["..."]
}}
```

- A **mobile** is a set of parts that move together with one degree of freedom.
  - `stem` (required, kind `stem`): your stem's parts. The simulation turns it about the stem axis and
    pulls it along it.
  - `barrel` (required, kind `barrel`): your parts fixed to the barrel arbor (for example a wheel and
    a ratchet). The supplied arbor is added to it.
  - Any other mobile has kind `free` or `spring`, and `dof` `rot` (turning about the line through
    `point` along `direction`) or `slide` (moving along `direction`).
  - `on_stem: true` (only for a `slide` along the x axis): the mobile also turns with the stem, as a
    part on a square stem section does; its own coordinate is its slide.
  - A `spring` mobile has `rest`: `1` or `-1`, the sign of its own coordinate the spring urges it
    towards (about or along its stated direction).
- **Fixed** parts never move (bridges, posts, cocks). They may touch each other and the plates.

## Simulation rules (quasi-static, contact only)

Every pair of bodies may overlap by at most {E.TOL} mm3 (fixed parts with fixed parts are not checked).
The stem moves in steps of {C.STEP_DEG} degrees (turning) or {C.PULL_STEP} (pulling). After each step:

1. **Pushed bodies.** A body is moved along its own degree of freedom by the least amount that clears
   its overlap with the bodies that moved in this step. It may move at most **{E.K:g} times** the
   surface travel of the bodies pushing it in this step (surface travel = distance moved, or angle
   times the body's largest distance from its axis). So a contact face inclined more steeply than
   about {63} degrees to the pushed body's direction of motion **locks** (the body cannot slip away
   along its degree of freedom); a gentler ramp lets it slip.
2. **Springs are light.** A `spring` body yields first: when anything overlaps it, it moves away
   along its degree of freedom if it can within the limit above. After every step it returns
   towards `rest` until it touches something, by at most {E.RELAX_MAX} of surface travel per step. A
   spring never pushes another body.
3. **The mainspring is strong.** After every step the barrel tries to turn back (against winding),
   up to 0.02 of surface travel per step, and it does push whatever is in its way (wheels it meshes
   with, and so on down the train), as long as those can move under rule 1.
4. If a step cannot be resolved, the stem is **blocked** for that step: nothing moves.
5. Before anything else, every moving body may clear an overlap it has at rest by up to 0.3 of
   surface travel.

## Required behaviour and score

Two hard requirements; if either fails the score is 0: **files** (everything loads as above), and
**rest** (at rest, as submitted, no two bodies overlap by more than {E.TOL} mm3).

Then weighted checks (score = sum of the weights passed / {tot}):

- **Wind ({W['wind']})**: position 1, turn forward 360 degrees: never blocked; the barrel arbor
  winds by between {360 / hi:g} and {360 / lo:g} degrees (that is {lo:g} to {hi:g} stem turns per arbor
  turn); the minute wheel moves at most {C.STILL_TOL} degree.
- **Slip ({W['slip']})**: position 1, turn backward 360 degrees: never blocked; the minute wheel
  moves at most {C.STILL_TOL} degree and the barrel arbor winds by at most {C.HOLD_TOL} degrees.
- **Click ({W['click']})**: the barrel arbor never runs back by more than {C.HOLD_TOL} degrees, in the
  slip test or in the set test.
- **Set ({W['set']})**: pull to position 2, then turn forward 180 and backward 180 degrees: the pull
  and the turns are never blocked; the minute wheel turns at least {C.SET_MIN / 2:g} degrees each way;
  the barrel arbor's net movement is at most {C.HOLD_TOL} degrees.
- **Sweep ({W['sweep']})**: pull from position 1 to 2 and stop at {C.SWEEP_SAMPLES} evenly spaced
  positions (both ends included). At each, from the same state, turn {C.SWEEP_TURN:g} degrees forward,
  and separately {C.SWEEP_TURN:g} degrees backward. No test turn may be blocked, and none may drive
  both trains (the barrel arbor winding by more than {C.STILL_TOL} degree **and** the minute wheel
  moving by more than {C.STILL_TOL} degree). At position 1 the forward turn must wind and not set; at
  position 2 it must set and not wind. Then push back to position 1: never blocked, and a forward
  turn winds again.
  - While pulling or pushing, if a step is blocked, the crown is rocked by up to +-{C.WIGGLE_DEG:g}
    degrees (steps of 1.5) to let teeth find their gaps, as fingers do.
- **Held ({W['held']})**: every `free` and `spring` mobile, moved {C.HOLD_SHIFT} across its axis in
  either of two perpendicular directions (and, for `rot` mobiles, along its axis either way),
  overlaps some other body by more than {E.TOL} mm3.
- **Bounds ({W['bounds']})**: every part inside the case; the stem may leave the case cylinder
  sideways, and some stem material reaches at least {C.STEM_PROTRUDE} outside the case radius.

Not checked: assembly order, minimum feature size, material, friction other than rule 1, inertia.
"""


def main(argv):
    out = os.path.abspath(argv[0])
    opts = dict(zip(argv[1:], argv[2:]))
    agent = opts.get("--agent", "codex")
    host = opts.get("--host", AGENTS[agent][1])
    if os.path.exists(out):
        shutil.rmtree(out)
    app = os.path.join(out, "environment", "app")
    os.makedirs(os.path.join(app, "submission", "parts"))
    shutil.copytree(os.path.join(HERE, "data"), os.path.join(app, "supplied"))
    open(os.path.join(app, "BRIEF.md"), "w").write(brief())
    open(os.path.join(out, "environment", "Dockerfile"), "w").write(DOCKERFILE.replace("{agent_install}", AGENTS[agent][0]))
    open(os.path.join(out, "environment", ".dockerignore"), "w").write("**/__pycache__\n")
    open(os.path.join(out, "instruction.md"), "w").write(PROMPT)
    open(os.path.join(out, "task.toml"), "w").write(TASK_TOML.replace("{host}", host))
    tests = os.path.join(out, "tests")
    os.makedirs(tests)
    for f in ("grade.py", "constants.py", "engine.py"):
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
