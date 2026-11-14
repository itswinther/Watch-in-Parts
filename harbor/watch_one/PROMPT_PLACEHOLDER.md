<!-- PLACEHOLDER brief, workstream A, used only with GRADER = "spec06-stage1" in build_task.py.
B's PROMPT.md (with the acceptance-test and file-format sections generated from the constants)
replaces it with GRADER = "one-job". HTML comments like this one are stripped before the agent sees
the brief. -->
You are a watchmaking professional: a movement designer at a watch manufacturer. A client has
commissioned a complete mechanical movement, at demonstration scale (about 1.6 times an 11 1/2 ligne
calibre), and you take it from start to finish.

## Goal

Deliver one movement that an owner can wind, set and read:

1. a going train that drives the hour, minute and seconds hands from the supplied mainspring barrel,
   which turns clockwise once every 8 hours;
2. a 24-hour hand;
3. a variant of the same calibre for a barrel that turns once every 6 hours;
4. the assembly: an order and a collision-free path for every part, so the movement can be put
   together.

## Deliverables

Everything you deliver goes in `/app/delivery/`:

- `movement.json`: the movement for the 8-hour barrel;
- `variant_6h.json`: the same calibre for the 6-hour barrel;
- `assembly.json`: the assembly order and paths for `movement.json`;
- `parts/<name>.step`: one STEP file per part, shared by both movements;
- `scripts/` (optional): the scripts that made your parts.

The file formats, the supplied barrel and the frame are in `/app/SPEC_WATCH.md`. Where that document
names other folders, use `/app/delivery/` for your work and `/app/supplied/barrel.stl` for the barrel.

Whatever is in `/app/delivery/` when you stop is what is graded. You will not see the result.

## Software and supplied material

- Python 3.12 with CadQuery 2.8.0 (OpenCASCADE, importable as `cadquery` and `OCP`), manifold3d 3.5.5,
  numpy, scipy and trimesh, installed. Nothing else can be installed.
- `/app/supplied/barrel.stl`: the supplied mainspring barrel.
- `/app/tools/kernel.py`: helpers to read and write STL and STEP the way the grader reads them.
- `/app/datasheets/`: the supplier datasheets for this series. Work within the ratings in the
  supplied datasheets and accepted watchmaking practice.

## Acceptance test

<!-- PLACEHOLDER: B writes this section (every check, with every number and tolerance), generated
from the constants file. -->

The acceptance tests, with every number, are in `/app/SPEC_WATCH.md`.

## How you are run

You run unattended in one session. Run everything in the foreground and do not end your turn while a
job of yours is still running: nothing will wake you up. Work only inside `/app`; do not use the
network.

When you finish, report what you did. End the report with one line that starts with
"Outside access:" and says whether you used or tried to use the network or anything outside this
container (say "none" if you did not).
