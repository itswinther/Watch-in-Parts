# Stage 1 watch design

`build.py` creates the assembled CadQuery STEP solids and movement.json.
Run from /app with `OPENBLAS_NUM_THREADS=1 python3 scripts/build.py`.

The barrel drives a 48-tooth transfer pinion. On that arbor a 96/24 pair
drives the minute mobile and a 16/48 pair drives the hour mobile. The minute
mobile drives an 80/10 pair, followed by a 75/10 pair to the seconds mobile.
Relative to the barrel the exact speed ratios are -2, +8, +2/3, -64 and +480.
At one clockwise barrel revolution per eight hours, the hands therefore turn
clockwise once per 12 hours, one hour and one minute.

All gears use 25-degree involute flanks. The modules are 0.2 at the barrel,
0.12 for the minute input, 0.225 for the hour reduction, 0.14 for the first
seconds pair and 12.6/85 for the last pair. Tooth pitch thickness is reduced
by 0.025 mm; root clearance is 1.35 modules. Gear flank profiles are planar
CAD wire edges extruded into solids, not triangular surface meshes.

The common hand axis is (7.2, 0). The transfer is at (14.4, 0), and the
seconds transfer at (7.2, 6.3). The case centre is (5, 0). Concentric sleeves
carry the hour and minute hands around the seconds arbor. The seconds pair
is lowest, the minute pairs intermediate, and the hour pair highest, so all
three hands can be above every gear. Fixed caps and their separate pillars
allow a sequence of vertical insertions without permanent closed cages.

Validation scripts, run from /app:

- `python3 scripts/check.py`: STEP conversion with specification tolerances,
  assembled intersections, 72-step free rotation and all six retention moves.
- `python3 scripts/check.py --mesh`: the complete specified 8*max(N1,N2)
  sample sequence for every mesh, including engagement and quarter-pitch drive.
- `python3 scripts/check_extra.py`: exact rational speeds, hand reach and
  concentric/vertical arrangement, non-meshing mobile tests, conservative swept
  size bounds, and voxel printability at offsets 0, 0.017 and 0.033 mm. Large
  parts use overlapping voxel tiles with a 0.35 mm halo; only each tile's core
  contributes to the distance result, avoiding artificial tile boundary effects.

The supplied submit tool is format-only; it does not establish a mechanical
score. Local checks use its same STEP tessellation parameters and manifold
geometry through tools/kernel.py. No official mechanical grader was available.

## Later stage options (design sketches, not submitted mechanisms)

For a 24-hour extension, the hour wheel can drive a 24-tooth idler at
(7.2,-8.1), module 0.225. A 12-tooth wheel on that idler can drive a 48-tooth
day wheel at (0,-8.1), module 0.24, on a separate z level. The two reductions
produce half the hour speed with the same direction. Fixed supports may be
replaced at stage 2; the existing mobile solids need not be changed.

For a faster barrel, the original barrel pinion can be removed and the
remaining transfer mobile driven at -1.5 barrel speed instead of -2. One
possible three-mesh replacement is 96/24, 24/48 and 18/24. An input axis at
(0,-12), intermediate at approximately (9.206133384,-7.894697561), and the
existing transfer axis give centre distances 12, 10.08 and 9.45 for modules
0.2, 0.28 and 0.45 respectively. Extra upper levels and shaft extensions can
leave existing hand and wheel files in their original positions. Support
clearance and gear phase would need validation in that stage.
