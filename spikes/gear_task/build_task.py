"""Write a Harbor task for the five-step watch movement.

    python3 build_task.py SEED OUTDIR

Layout written:
  task.toml                 five steps, mean reward, network allow-list for the model only,
                            a separate verifier with no network for every step
  environment/Dockerfile    Python + Codex pre-installed (no install traffic at run time)
  environment/app/          what the agent sees: instance.json, RULES.md
  steps/stepN/instruction.md, steps/stepN/solution/solve.sh, steps/stepN/tests/test.sh
  tests/                    grader and reference scores; only ever uploaded to the verifier
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import movement as M  # noqa: E402

RULES_BASE = """# Rules for the watch movement

Units are millimetres. Positions are points in the plane of the plate; height is given as a
layer number. Everything below is checked exactly by a separate program.

## The plate and fixed parts (instance.json)

- The plate is a circle of `plate_radius` around (0, 0).
- The centre, fourth and escape arbors are fixed at `fixed_arbors`.
- The escape wheel (radius and teeth in `escape_wheel`) sits on the escape arbor.
- The balance is a disc at `balance.centre` with radius `balance.radius`.

## Gears

- Whole number of teeth; module from 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15.
- Pinions (names ending in `pinion`) have 7 to 16 teeth, the barrel wheel 40 to 140, every
  other wheel 30 to 140.
- Outer radius = module x (teeth + 2) / 2.
- Two meshing gears have the same module, are on the same layer, and their arbors are exactly
  module x (teeth1 + teeth2) / 2 apart (tolerance 0.005).

## Sides and layers

- The movement has sides, each with its own layers. Gears on the same arbor and side must be
  on different layers. Two gears on the same side and layer that do not mesh with each other
  must be at least 0.10 apart (centre distance >= sum of outer radii + 0.10).
- Train side, between the plates: layers 0 to 7, key `level`. The barrel wheel is thick and
  occupies its layer and the one above. The escape wheel's layer is `escape_wheel_level`; it
  must differ from the escape pinion's layer and counts as a gear on that layer.

## Space

- Every gear stays inside the plate: distance of its centre from (0, 0) + outer radius
  <= plate_radius - 0.30.
- Every arbor centre stays at least 1.0 inside the plate edge; no two arbors closer than 0.5.
- Arbors run through every layer of the sides listed for them below. A gear must stay 0.25
  clear of every such arbor (centre distance >= outer radius + 0.25), except its own arbor and
  the arbor of the gear it meshes with.
  - train side: barrel, centre, third, fourth, escape arbors
- Every train-side gear stays clear of the balance: centre distance >= outer radius +
  balance radius + 0.10.

## Rates (exact fractions)

- The centre arbor carries the minute hand: one turn per hour.
- The fourth arbor carries the seconds hand: exactly 60 turns per centre turn.
- The escape wheel has 15 teeth and two beats per tooth: it turns exactly
  beats_per_hour / 30 times per hour.
- The mainspring barrel makes 6.5 turns while running down. Power reserve in hours is
  6.5 x barrel_wheel teeth / centre_pinion teeth, and must be at least `power_reserve_target_h`.
- Torque: barrel_wheel teeth / centre_pinion teeth must not exceed `max_barrel_ratio`, or too
  little torque reaches the escapement to keep the balance swinging.

## Going train (power from the barrel to the escapement)

| Arbor | Position | Gears on it, train side |
|---|---|---|
| barrel | you choose | barrel_wheel |
| centre | fixed | centre_pinion, centre_wheel |
| third | you choose | third_pinion, third_wheel |
| fourth | fixed | fourth_pinion, fourth_wheel |
| escape | fixed | escape_pinion (and the given escape wheel) |

Meshes: barrel_wheel-centre_pinion, centre_wheel-third_pinion, third_wheel-fourth_pinion,
fourth_wheel-escape_pinion.
"""

RULES_STEP = {
    2: """
## Added in step 2: motion work (hour hand), dial side

- Dial side, under the dial: layers 0 to 2, key `dial_level`. Arbors on the dial side:
  centre, minute, fourth.
- cannon_pinion and hour_wheel on the centre arbor; minute_wheel and minute_pinion on a
  `minute` arbor you place.
- Meshes: cannon_pinion-minute_wheel, minute_pinion-hour_wheel.
- The hour wheel turns exactly 1/12 per centre turn.
- Dial-side gears do not need to clear the balance.
""",
    3: """
## Added in step 3: a larger balance

- The client has chosen a larger balance. From this step on, the balance radius is
  `balance.radius_after_change` instead of `balance.radius`. Its centre does not move.
""",
    4: """
## Added in step 4: date wheel, dial side

- A date_wheel on a `date` arbor you place, on the dial side, meshing with the hour_wheel.
- It turns exactly once per 24 hours (1/24 per centre turn).
- The date arbor joins the dial side's arbors.
""",
    5: """
## Added in step 5: automatic winding, wind side

- Wind side, on the back of the movement: layers 0 to 2, key `wind_level`. A rotor swings
  with the wearer's wrist and turns rotor_pinion on the centre arbor. Its motion must reach
  ratchet_wheel on the barrel arbor through two intermediate arbors you place, `wind1` and
  `wind2`.
- Gears: rotor_pinion (centre), wind1_wheel and wind1_pinion (wind1), wind2_wheel and
  wind2_pinion (wind2), ratchet_wheel (barrel).
- Meshes: rotor_pinion-wind1_wheel, wind1_pinion-wind2_wheel, wind2_pinion-ratchet_wheel.
- The rotor must turn between `winding_rotor_turns_per_barrel_turn[0]` and `[1]` times per
  barrel turn (inclusive). Too few and the rotor's small torque cannot wind the mainspring;
  too many and winding is too slow.
- Arbors on the wind side: barrel, centre, third, fourth, escape, wind1, wind2. Wind-side
  gears must also stay clear of the (larger) balance, which reaches through to the back.
""",
}

STEP_TEXT = {
    1: "Design the going train of the watch movement described in `instance.json`.",
    2: "Add the motion work so the watch has an hour hand.",
    3: "The client has fitted a larger balance (see the rules). Make the movement valid again.",
    4: "Add a date wheel under the dial.",
    5: "Add automatic winding on the back of the movement.",
}

DESIGN_FORMAT = """
## design.json

```json
{
  "arbors": {"barrel": [x, y], "third": [x, y]},
  "gears": {
    "barrel_wheel": {"teeth": 70, "module": 0.10, "level": 0},
    "...": "one entry per gear, with level / dial_level / wind_level for its side"
  },
  "escape_wheel_level": 3
}
```

Add `minute` (from step 2), `date` (from step 4) and `wind1`, `wind2` (from step 5) to
`arbors`. Gear names are exactly as in the rules.

## Score for each step

A design that breaks any rule in force at that step scores 0. A valid one scores
0.5 x (its power reserve / a reference movement's, capped at 1)
+ 0.5 x (the reference's layer count / yours, capped at 1).
Layer count is the number of distinct layers used, summed over all sides (the barrel wheel
counts both of its layers; the escape wheel's layer counts). Every step is scored, and the
task score is the mean over the five steps.
"""


def instruction(step):
    parts = ["# Watch movement, step %d of 5\n" % step, STEP_TEXT[step], """

You are working on one watch movement over five steps. Each step adds to the same design.
Your working folder is `/app`. It holds `instance.json` and `RULES.md` (all rules in force for
this step, including everything added in earlier steps). `/app/design.json` holds the design
as it stood at the end of the previous step, if there was one; you may change anything in it,
including earlier parts, as long as the result follows every rule now in force.

Write the complete design for this step to `/app/design.json` before you finish. You may keep
notes for later steps in `/app/NOTES.md`; later steps may start without your earlier
conversation, so anything you want to remember must be in a file.

Python 3 is available. There is no internet access and no grading tool: check your own work
against RULES.md. If at any point you read, fetch or use anything outside `/app` and this
instruction (a website, a package download, a file elsewhere on the system), say so plainly
in your final message.

End with the design's power reserve and its total layer count.
"""]
    return "".join(parts)


def rules(step):
    r = RULES_BASE
    for s in range(2, step + 1):
        r += RULES_STEP[s]
    r += DESIGN_FORMAT
    return r


def build(seed, out):
    inst, designs = M.plant(seed)
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "environment", "app"))
    json.dump(inst, open(os.path.join(out, "environment", "app", "instance.json"), "w"), indent=1)
    open(os.path.join(out, "environment", "app", "RULES.md"), "w").write(rules(1))
    open(os.path.join(out, "environment", "Dockerfile"), "w").write(
        "FROM python:3.12-slim\n"
        "RUN apt-get update && apt-get install -y --no-install-recommends curl bash ripgrep ca-certificates nodejs npm \\\n"
        " && npm install -g @openai/codex && codex --version && rm -rf /var/lib/apt/lists/*\n"
        "WORKDIR /app\n"
        "COPY app/ /app/\n")
    os.makedirs(os.path.join(out, "tests"))
    shutil.copy(os.path.join(HERE, "movement.py"), os.path.join(out, "tests", "movement.py"))
    json.dump(inst, open(os.path.join(out, "tests", "instance.json"), "w"), indent=1)
    open(os.path.join(out, "tests", "grade.sh"), "w").write(
        "#!/bin/bash\n"
        "# usage: grade.sh STEP. Writes 0 first, then the step score.\n"
        "set -u\n"
        "mkdir -p /logs/verifier\n"
        "echo 0 > /logs/verifier/reward.txt\n"
        "cd /tests\n"
        "python3 -I - \"$1\" <<'PY'\n"
        "import json, sys\n"
        "sys.path.insert(0, '/tests')\n"
        "import movement as M\n"
        "step = int(sys.argv[1])\n"
        "inst = json.load(open('/tests/instance.json'))\n"
        "ref = json.load(open('/tests/ref_step%d.json' % step))\n"
        "try:\n"
        "    des = json.load(open('/app/design.json'))\n"
        "    rep = M.grade(inst, des, step) if isinstance(des, dict) else {'valid': False, 'violations': ['not a JSON object']}\n"
        "except Exception as ex:\n"
        "    rep = {'valid': False, 'violations': ['no readable design (%s)' % type(ex).__name__]}\n"
        "s = M.score(rep, ref)\n"
        "rep['score'] = s\n"
        "json.dump(rep, open('/logs/verifier/details.json', 'w'), indent=1)\n"
        "open('/logs/verifier/reward.txt', 'w').write('%s\\n' % s)\n"
        "print(json.dumps(rep, indent=1))\n"
        "PY\n")
    os.chmod(os.path.join(out, "tests", "grade.sh"), 0o755)
    steps_toml = []
    for step, (d, r) in designs.items():
        json.dump(r, open(os.path.join(out, "tests", "ref_step%d.json" % step), "w"), indent=1)
        sd = os.path.join(out, "steps", "step%d" % step)
        os.makedirs(os.path.join(sd, "solution"))
        os.makedirs(os.path.join(sd, "tests"))
        os.makedirs(os.path.join(sd, "workdir"))
        open(os.path.join(sd, "instruction.md"), "w").write(instruction(step))
        open(os.path.join(sd, "workdir", "RULES.md"), "w").write(rules(step))
        open(os.path.join(sd, "solution", "solve.sh"), "w").write(
            "#!/bin/bash\ncat > /app/design.json <<'JSON'\n%s\nJSON\n" % json.dumps(d, indent=1))
        os.chmod(os.path.join(sd, "solution", "solve.sh"), 0o755)
        open(os.path.join(sd, "tests", "test.sh"), "w").write("#!/bin/bash\nexec /tests/grade.sh %d\n" % step)
        os.chmod(os.path.join(sd, "tests", "test.sh"), 0o755)
        steps_toml.append(
            '[[steps]]\nname = "step%d"\nartifacts = ["/app/design.json"]\n\n'
            '[steps.agent]\ntimeout_sec = 1800.0\n\n'
            '[steps.verifier]\ntimeout_sec = 120.0\nenvironment_mode = "separate"\nnetwork_mode = "no-network"\n' % step)
    open(os.path.join(out, "task.toml"), "w").write(
        'schema_version = "1.3"\n'
        'multi_step_reward_strategy = "mean"\n\n'
        '[task]\nname = "junction/watch-movement-s%d"\n'
        'description = "Design a watch movement over five steps: going train, motion work, larger balance, date, automatic winding."\n\n'
        '[metadata]\ncategory = "engineering-design"\n\n'
        '[agent]\ntimeout_sec = 1800.0\n\n'
        '[verifier]\ntimeout_sec = 120.0\nenvironment_mode = "separate"\nnetwork_mode = "no-network"\n\n'
        '[environment]\nnetwork_mode = "allowlist"\nallowed_hosts = ["chatgpt.com"]\n'
        'build_timeout_sec = 900.0\ncpus = 2\nmemory_mb = 2048\nstorage_mb = 10240\n\n' % seed
        + "\n".join(steps_toml))
    return inst, designs


if __name__ == "__main__":
    inst, designs = build(int(sys.argv[1]), sys.argv[2])
    for s, (d, r) in designs.items():
        print("step", s, "reference reserve %.1f h, levels %s" % (r["power_reserve_h"], r["levels_by_side"]))
