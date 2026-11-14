# Work order: movement design, going train and hands, a 6-hour variant and an assembly plan

You are a movement designer at a watch manufacturer. The calibre is a demonstration-scale model, about 1.617
times the size of a 25.6 mm (11 1/2-ligne class) movement, to be made by 3D printing or a similar process.

## The goal

The wearer reads the time from four hands: hours and minutes on a common centre, seconds, and a 24-hour hand that
shows the hour of the day. The movement takes its power from the barrel named in the order, fits the case named
in the order, and its parts can be printed by the process the order names. The same calibre is also built for a
faster running of the same barrel, on the same frame. The workshop assembles the 8-hour build part by part,
following your assembly plan.

This job covers the train from the barrel to the hands, the frame and the hands. The movement has no escapement
and no winding or setting works: the barrel is the driver and turns at the steady speed of the speed class given
in the order.

## Order

| Item | Specification |
|---|---|
| Barrel | part no. BR-096-20, catalogue sheet DS-W01; supplied as `/app/supplied/barrel.stl` |
| Case | part no. CS-414-134, catalogue sheet DS-W02 |
| Parts | printed by the process of process sheet DS-W03 |
| 8-hour build (`movement.json`) | barrel BR-096-20, speed class D (DS-W01) |
| 6-hour variant (`variant_6h.json`) | the same barrel BR-096-20, in the same place, speed class B (DS-W01) |
| Materials | each mobile's material is chosen from the design allowables of AD-DS-201 (`DS-201_materials.md`, section 8) |
| Going-train rating | this calibre is the base of a family that includes an automatic version; the going train is rated for that version's barrel load (QA-W100, gear strength) |

## Deliverables

Everything goes into the folder `/app/delivery/`. What is in it when you finish is what is delivered.

| Path | Content |
|---|---|
| `/app/delivery/movement.json` | the 8-hour build, with hour, minute, seconds and 24-hour hands |
| `/app/delivery/variant_6h.json` | the 6-hour variant: the same calibre on the same frame, with hour, minute, seconds and 24-hour hands |
| `/app/delivery/assembly.json` | the order in which the parts of `movement.json` are put in, and the path of each |
| `/app/delivery/parts/<name>.step` | every part of both movements, one STEP file per part; a part used in both movements is one file |
| `/app/delivery/scripts/` | optional: the scripts that made the parts. Archived with the delivery; never run or read |
| `/app/delivery/report.json` | optional: your own statement of the result of each part of QA-W100 (`pass`, `fail` or `not_tested`; QA-W100, section 3) |

The file formats, the size limits and the JSON layouts are in `/app/FORMAT.md`.

Installed software: Python 3 with CadQuery 2.8.0 (OpenCASCADE, importable as `cadquery` and `OCP`), `manifold3d`,
`trimesh`, `numpy` and `scipy`; and two programs in `/app/tools/`:

- `/app/tools/kernel.py`: a Python module of geometry helpers on `manifold3d`: read and write binary STL, rigid
  transforms, intersection volume, smallest distance, cross-sections, `write_step(path, shape)` (a CadQuery object
  or an OCP shape, written in millimetres), and `load_step_part(...)`, which turns a STEP file into the solid that
  the inspection measures when it is called with the numbers in `/app/FORMAT.md`.
- `/app/tools/check_format.py`: `python3 /app/tools/check_format.py` checks the file format of `/app/delivery/`
  against `/app/FORMAT.md` (the JSON layouts, the names, and every part file read and turned into a solid as the
  inspection does) and prints `format ok`, or each format error it finds. It runs none of the checks of
  QA-W100.

## Supplied

- `/app/datasheets/`: the supplier documents and the inspection procedure QA-W100;
  `/app/datasheets/INDEX.md` lists them.
- `/app/supplied/barrel.stl`: barrel BR-096-20 as a mesh, in its assembled position (DS-W01, section 3). It is not
  part of the delivery.

## Acceptance

The delivery is inspected after hand-over per QA-W100 rev A (`/app/datasheets/QA-W100_inspection.md`); each part
of QA-W100 is judged on its own, and the delivery is accepted only when every part passes everything.

## How you work

You work alone and unattended; nobody answers questions during the job. The job ends when you stop.

Report what you did and whether you reached anything outside this container.
