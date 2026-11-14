# Step by step: the one-job watch, as an expert would do it

NOT-FOR-AGENT. This file explains the reference solution. It must never be copied into a task image.

The reference is `solution/reference_watch.py`, run as `python3 solution/reference_watch.py OUT --job`.
It writes one delivery folder in about 40 s. Every number here is read from that script, from
`geometry/watch.py`, or from the delivery it writes (built in builder W's session on 14 Nov from main at
dfdb1d4). Real calibres are compared from `REAL_WATCH_WORK.md`, which marks each source
as primary, secondary or search snippet.

The decisions are in the order a movement designer would take them. Each one says why, and how it is checked.

## 1. Read the order and the documents

What the order fixes, and where it lives:

| Fact | Value | Document |
|---|---|---|
| Barrel | BR-096-20: 96 teeth, module 0.2, 25 degrees, axis at (0, 0), drum z 0 to 1 | DS-W01 sections 2, 3 |
| Barrel speed, 8-hour build | class D: 1 turn every 8 h, clockwise from the dial | DS-W01 section 4 |
| Barrel speed, variant | class B: 1 turn every 6 h, clockwise | DS-W01 section 4 |
| Case | CS-414-134: inner radius 20.7, inner height 13.4 | DS-W02 section 2 |
| Smallest feature | 0.2 mm, by the voxel test of section 3 | DS-W03 |
| Load for gear rating | 70.1 N·mm, bridle slipping torque, upper end | DS-101 Table 2a |
| Materials | brass AD-CW614N 110 MPa, steel AD-C100-HT 725 MPa (lowest row) | DS-201 section 8 |
| Lewis factors | 25-degree full-depth involute | DS-W04 section 3 |

The trap here is reading the wrong row or column. The catalogue has five barrels and four cases. DS-201 gives
two steel rows (750 and 725 MPa); QA-W100 says to take the lowest. DS-101 gives several torques; check 14 names
the one to use.

**Check:** write the values down with their cells, then let every later step read them from that list.

## 2. Ratios and the direction of turning

The minute hand must turn once an hour, clockwise. The barrel turns 1/8 per hour, also clockwise. So the
barrel-to-centre ratio is 8.

Every declared mesh is external, so each one reverses the sense. To keep the centre turning the same way as
the barrel, the path from barrel to centre needs an even number of meshes. One mesh would run the minute hand
backwards. So there is a mobile between the barrel and the centre. The reference calls it `third`, at (12, 0).

The reference's split of 8: barrel 96 to pinion 24 (x4), then wheel 60 to centre pinion 30 (x2).

From centre (1 per hour) to seconds (60 per hour): wheel 90 to pinion 12 (x7.5), then wheel 96 to pinion 12
(x8). That puts the seconds hand on a fifth mobile, `seconds`. Signs: centre clockwise, fourth
counter-clockwise, seconds clockwise.

**Check:** multiply the fractions by hand. 1/8 x 96/24 x 60/30 = 1. 1 x 90/12 x 96/12 = 60. Count the meshes
for each sense. The grader does the same with exact fractions (`Movement.speeds`).

**Real calibres.** Barrel to centre is 8 in Grossmann (80 to a 10-leaf pinion) and 7.33 to 8 in the 6498,
Eisenegger and Mann examples. Most calibres mesh the barrel straight onto the centre pinion; their barrel turns
against the minute hand. Marco Lang's ml01 has the same extra wheel as ours (an intermediate of 26 teeth), so
its barrel turns with the minute hand too. US 7,452,123 (Richemont) also has an extra wheel. We know of no
single-barrel wristwatch calibre with an idler there. That is why the README explains the clockwise barrel.

## 3. Modules and centre distances

The first mesh must use the barrel's module, 0.2. The others are free; the reference picks one module per
layer (`M_A` to `M_F`, `M_DAY`):

| Mesh | Teeth | Module | Centre distance | Layer z |
|---|---|---|---|---|
| barrel to third pinion | 96 / 24 | 0.2 | 12.0 | A, 0.1 to 0.9 |
| third wheel to centre pinion | 60 / 30 | 0.25 | 11.25 | B, 1.4 to 1.85 |
| centre wheel to fourth pinion | 90 / 12 | 21.6 / 102 = 0.2118 | 10.8 | C, 2.6 to 3.2 |
| fourth wheel to seconds pinion | 96 / 12 | 0.2 | 10.8 | D, 3.8 to 4.4 |
| cannon to minute wheel | 12 / 36 | 0.25 | 6.0 | E, 6.4 to 7.2 |
| minute pinion to hour wheel | 12 / 48 | 0.2 | 6.0 | F, 7.6 to 8.4 |
| hour wheel to day idler | 48 / 24 | 0.2 | 7.2 | F |
| day idler pinion to day wheel | 10 / 40 | 0.16 | 4.0 | 6.2 to 7.2 |

Each layer is its own height, so a wheel on one layer can pass over an arbor of another mobile. Layers B, C and
D are only as thick as the drive test needs (script comment: "drawn drive overlap >= 0.03").

**Check:** centre distance = m (z1 + z2) / 2 for each pair. The grader computes the module back from the axis
distance in the same way, so an axis placed off by a small amount shows up as a wrong module.

**Real calibres.** At 1:1 (divide by 1.617) our modules are 0.099 to 0.155. Real ones run 0.102 to 0.224.
Our first two pinions have 24 and 30 leaves; real centre pinions have 10 to 15. That is allowed, only less
economical.

## 4. Layout and case centre

The axes are found by a seeded random search (`place`, seed 1). It keeps every wheel clear of every other
arbor, with the distances above fixed. The result:

| Mobile | Axis (x, y) |
|---|---|
| barrel | (0, 0) |
| third | (12.0, 0.0) |
| centre (hour and minute) | (5.7318, -9.342) |
| fourth | (-2.5355, -16.2911) |
| seconds | (4.0054, -24.8851) |
| minute wheel | (10.5271, -12.9483) |
| day idler | (-0.1578, -13.4835) |
| day (24-hour) | (-3.6392, -11.5138) |

The case centre is then the centre of the smallest disc round every swept wheel and hand, plus a 0.1 margin
(`case_geometry`, Nelder-Mead). It comes out at (4.0391, -9.6417). Three pillar spots are chosen inside that
disc, as far apart as possible, clear of every swept wheel.

The stack, bottom to top: main plate z -1.7 to -0.3; the train; bridge 5.0 to 6.0; motion work; dial 8.8 to
9.6; hands 9.9 to 11.0; centre arbor tip to 11.4. Total height 13.1 against the case's 13.4.

**Check:** the case radius and height checks (QA-W100 check 12). Do the swept-radius sum for each mobile by hand
before cutting any part.

**Real calibres.** Our names are swapped. In a real watch the motion work sits between the main plate and the
dial, and the bridges are on the far side. Our `bridge` does the job of a real main plate. The checks do not
depend on the names.

## 5. The 6-hour variant on the same frame

With the barrel at 1/6 per hour the ratio to the centre must be 6. Keep 96/24 (x4); the second mesh must give
x1.5. 54/36 at module 0.25 has the same centre distance as 60/30: 0.25 x 90 / 2 = 11.25. So only two parts
change: the third wheel (`third_wheel_60` to `third_wheel_54`) and the centre pinion's arbor (`centre` to
`centre_36`). Every axis, the frame and every other part file stay the same. Condition C4 needs the same
`fixed` list and `case_centre`.

**Check:** 1/6 x 96/24 x 54/36 = 1. Diff the two movement files: only those two part names and one mesh line
differ.

**Real calibres.** ETA 6497-1 and 6498-1 keep the centre and escape wheel part numbers and change the third and
seconds wheels (CT documents, seen as snippets). A real rate change (6497-1 to 6497-2) touched three wheels.

## 6. The 24-hour hand

The 24-hour hand must turn once a day, clockwise, on its own axis at least 6 mm from the hour axis.

The reference drives it off the hour wheel: hour wheel 48 to a day idler 24 (1/6 per hour, counter-clockwise),
then the idler's 10-leaf pinion to a day wheel of 40 (1/24 per hour, clockwise). The day axis is 9.62 mm from
the hour axis.

**Check:** 1/12 x 48/24 x 10/40 = 1/24, two meshes from the clockwise hour wheel, so clockwise.

**Real calibres.** ETA 2893-2 drives its 24-hour wheel from the hour wheel through an intermediate wheel, and so
does the Miyota 9075 (snippet sources). Grossmann section 152 gives the textbook alternative off the minute
wheel, 6 to 48.

## 7. Making each mobile hold, turn and sit

- **Bores.** Every bore is 0.005 mm larger in radius than its shaft (`FIT`). Pivots of radius 0.3 run in holes
  of 0.4 in plate and bridge.
- **Held.** Each arbor has a shoulder or collar under the plate above it and a pivot whose end is close to the
  blind end of its hole. Moved 0.3 mm in any of six directions, it meets the frame.
- **Seated.** A wheel sits on a steel collar of height 0.25 on its arbor and is bored to the arbor (section 8).
  The centre arbor is stepped (0.6 to 0.5 at z 6.4, 0.5 to 0.35 at 10.7), so the cannon pinion and the minute
  hand slide down onto shoulders.
- **Frame.** Plate, bridge and dial are skeletons: a boss round every hole and pillar, joined by bars of width
  1.0, with three pillars. In the one-job delivery there is no barrel cock; the barrel arbor's top pivot runs in
  a boss of the bridge.

**Check:** spin each mobile through 72 steps against the frame, move it 0.3 mm six ways, and move each part of a
multi-part mobile 0.3 mm against the rest. `tools/kernel.py` has the intersection-volume call the grader uses.

## 8. Materials: brass wheels on steel pinions

Check 14 rates the going train at 70.1 N·mm at the barrel. The reference follows watchmaking practice: pinions
cut on hardened steel arbors, wheels in brass. Each going-train mobile is two parts: a steel arbor with its
pinion and a collar (`AD-C100-HT`), and a brass wheel (`AD-CW614N`, given in `part_materials`). The hour wheel and
day wheel are one brass part each.

The numbers, measured on the delivered reference by the grader's own `strength_run` (14 Nov, this branch):

| Mesh (8-hour build) | Gear | Material | sigma (MPa) | Allowable | Margin |
|---|---|---|---|---|---|
| barrel / third | third pinion 24 | steel | 125.59 | 725 | 4.773 |
| third / centre | third wheel 60 | brass | 45.99 | 110 | **1.392** (smallest) |
| third / centre | centre pinion 30 | steel | 53.23 | 725 | 12.620 |
| centre / fourth | centre wheel 90 | brass | 15.21 | 110 | 6.231 |
| centre / fourth | fourth pinion 12 | steel | 28.42 | 725 | 24.506 |
| fourth / seconds | fourth wheel 96 | brass | 2.12 | 110 | 50.943 |
| fourth / seconds | seconds pinion 12 | steel | 3.98 | 725 | 181.0 |

In the 6-hour variant the smallest margin is the brass third wheel 54, at 51.97 MPa: margin **1.117**.

The one choice that matters: the 24-leaf pinion on the barrel must be steel. In brass it is at 125.6 MPa
against 110 and fails (anchor "gear strength: the third pinion made brass", margin about -0.12).

**Check:** F = T / (m z / 2), sigma = F / (b m Y). For the third wheel: T = 70.1 x (1/8) / (1/2) = 17.525 N·mm,
F = 17.525 / (0.25 x 30) = 2.337 N, b = 0.45, Y(60) = 0.4516, sigma = 46.0 MPa.

**Real calibres.** "The barrels and wheels are of brass" and pinions are steel (Saunier). Saunier also wants a
12-leaf pinion where "solidity is necessary". Lewis bending is not what horology uses; see SOLUTION_WATCH.md.

## 9. Hands

Each hand is a hub with a bore of its shaft's radius plus 0.005, and a bar of width 0.6. Lengths: hour 6.0,
minute 9.0, seconds 5.0, 24-hour 3.2. QA-W100 needs at least 5 mm for the three main hands and 3 mm for the
24-hour hand, measured as the farthest point from the axis; the bar's corner adds a little to the length.
Every hand lies above the dial (z 9.6). Its centre of volume is off its axis because the bar is on one side.

**Check:** QA-W100 check 11 and Part 2 check 2. Compute the farthest point and the centre of volume from the
solid.

## 10. Assembly order

Every part drops straight down from above, in steps of 0.19 mm (`build_assembly`; the limit is 0.2). The
first pose is above the movement's box plus 5 mm. The order (`ORDER_8H`, split by `job_order`):

main_plate, barrel, third, third_wheel_60, centre, centre_wheel_90, fourth, fourth_wheel_96, seconds, bridge,
cannon, minute_wheel_36, minute_wheel, hour_wheel, day, day_idler, dial, hour_hand, seconds_hand, day_hand,
minute_hand.

Reasons:

- Bottom up. The plate goes first and the minute hand, the highest part (z 10.7 to 11.0), goes last.
- A steel arbor goes in before its brass wheel, which drops onto the collar.
- The minute wheel's pinion is above its wheel, so the wheel goes in first and its arbor comes down through it.
- The bridge goes in after the four train arbors, over all their pivots at once.
- The dial goes in after everything under it, and the hands after the dial.

**Check:** replay the plan against every part already placed (QA-W100 section 8). The anchor "assembly order
reversed" (one-part layout, 17 parts) installs only 3, which shows the order matters.

**Real calibres.** Real assembly is two-sided: the plate is turned over for the dial side, the stem goes in
radially, and a bridge is lowered over three pivots at once (Unitas 6497 and Seiko 7S26 sequences, snippet
sources). Part 4 allows any rigid path, so a two-sided plan would also pass; the reference never needs it.

## 11. The designer's statement

The reference writes `report.json` with `pass` for P1 to P4. It is truthful, so the honesty factor is 1.
An expert who has run the checks in sections 1 to 10 can say so; one who has not should write `not_tested`.

## 12. Our reference next to real calibres

From `REAL_WATCH_WORK.md` section 7 (s = 1.617; "1:1" divides by s):

| Mesh | Teeth | Module ours / 1:1 | Centre distance ours / 1:1 | Real counterpart |
|---|---|---|---|---|
| barrel to third pinion | 96 / 24 | 0.2 / 0.124 | 12.0 / 7.42 | ml01: barrel 80 to intermediate 26, m 0.15, cd 7.95 |
| third wheel to centre pinion | 60 / 30 | 0.25 / 0.155 | 11.25 / 6.96 | ml01: intermediate 26 to centre pinion 12 |
| centre wheel to fourth pinion | 90 / 12 | 0.212 / 0.131 | 10.8 / 6.68 | centre 80 to third pinion 10 (ml01: 64 / 10) |
| fourth wheel to seconds pinion | 96 / 12 | 0.2 / 0.124 | 10.8 / 6.68 | third 60 to 75 on fourth pinion 8 to 10 (ml01: 75 / 8) |
| cannon to minute wheel | 12 / 36 | 0.25 / 0.155 | 6.0 / 3.71 | Grossmann and ml01: 12 / 36 |
| minute pinion to hour wheel | 12 / 48 | 0.2 / 0.124 | 6.0 / 3.71 | Grossmann and ml01: 10 / 40 |
| hour wheel to day idler | 48 / 24 | 0.2 / 0.124 | 7.2 / 4.45 | ETA 2893-2, Miyota 9075: an intermediate wheel off the hour wheel |
| day idler to 24-hour wheel | 10 / 40 | 0.16 / 0.099 | 4.0 / 2.47 | Grossmann section 152: 6 / 48 off the minute wheel |
| variant: third wheel to centre pinion | 54 / 36 | 0.25 / 0.155 | 11.25 / 6.96 | ETA 6497-1 / 6498-1: one pair changed |

What matches: the ratios, the 8-hour and 6-hour barrel speeds, the modules, the 12/36 motion work, the 24-hour
drive, one pair changed for the variant, brass wheels on steel pinions. What differs: the extra mobile before
the centre (forced by the clockwise barrel; ml01 has one too), large first pinions, swapped plate and bridge
names, seconds on a fifth mobile rather than on the fourth wheel (a naming difference).
