# Inspection procedure: movement design deliveries, demonstration-scale calibre

| Document | Revision | Date | Status |
|---|---|---|---|
| QA-W100 | A | 2026-11-14 | Released |

**Issued by:** the manufacturer's quality department. **Document type:** inspection procedure.

## 1. Scope

This procedure is the acceptance inspection of a movement design delivery for the demonstration-scale calibre:
the 8-hour build (`movement.json`), the 6-hour variant (`variant_6h.json`), the assembly plan (`assembly.json`),
the part files and, when delivered, the designer's statement (`report.json`), in the folder `/app/delivery/`, in
the file formats of `/app/FORMAT.md`. The inspection is run after hand-over, on what is in `/app/delivery/` at
that time.

## 2. Documents

Values that belong to a supplied item are taken from that item's supplier document, as cited in each check.

| Document | Used for |
|---|---|
| The work order | the barrel part no. and its speed class for each build, the case part no., the print process |
| DS-W01 | the barrel: its catalogue data (section 2), the barrel as supplied (section 3) and the speed classes (section 4) |
| DS-W02 | the case: inner radius and inner height (section 2) |
| DS-W03 | the printability test (section 3) |
| `/app/FORMAT.md` | the file formats, and how a part file becomes the solid that is measured |
| DS-W04 | Parts 1 and 3, check 14 |
| VM-DS-101 | Parts 1 and 3, check 14 |
| AD-DS-201 | Parts 1 and 3, check 14 |
| VM-DS-401 | Part 5: the winding stem's travel from position 1 to position 2 (section 4, Table 2) |

## 3. Acceptance

The inspection has five parts. Each part is judged on its own, even when another part fails. Within Parts 1 to 3
each check counts on its own; in Part 4 each installed part counts; in Part 5 each step counts on its own. The
delivery as a whole is accepted only when every condition and every check and step of all five parts passes:
everything must work.

**Designer's statement.** The delivery may include the designer's own statement of the result of each part of this
inspection, in the file `report.json` (layout in `/app/FORMAT.md`): `pass` (the part passes in full: every
condition and every check of it passes; in Part 4, every part is installed), `fail` (it does not pass in full) or
`not_tested` (no statement). The inspection compares each part's statement with that part's result and scores it
by this table:

| Statement for a part | The part passes | The part does not pass |
|---|---|---|
| `pass` | 1 | -2 |
| `fail` | 0.5 | 1 |
| `not_tested` | 0.5 | 0.5 |

A part that `report.json` leaves out counts as `not_tested`, and so does every part when `report.json` is absent
or not valid. The statement's agreement score h is the mean of these points over the five parts, or 0 if that mean
is below 0. The delivery's acceptance figure is its parts figure (the result of the five parts together) times
(0.75 + 0.1 x h) / 0.85. The statement changes no other result of the inspection.


## 4. Terms

- **Frame and units.** Millimetres (mm), cubic millimetres (mm3) and degrees. A right-handed frame. Every arbor
  (rotation axis) is parallel to z. The dial side is +z: the hands are read looking from +z towards -z, and
  "clockwise" always means clockwise in that view.
- **Solids.** Every test measures the solids built from the part files as `/app/FORMAT.md` describes; the barrel
  is the solid of `/app/supplied/barrel.stl`. "Intersect by at most 0.01 mm3" means that the volume of the
  intersection of the two solids is at most 0.01 mm3.
- **The frame** is the fixed parts of a movement, taken together.
- **A mobile** is a set of parts that turn together as one rigid body about the vertical line through its axis.
  The barrel is the mobile `barrel` (its drum and its arbor together, as one solid); its axis is the axis of the
  barrel as supplied (DS-W01, section 3).
- **Speeds** are worked out from the tooth counts declared under `meshes`, as exact fractions, starting from the
  barrel at the speed, and in the running sense, of the speed class that the work order gives for the build being
  judged (DS-W01, section 4). Every declared mesh is external: its two mobiles turn in opposite directions. A
  mobile declared `friction_on` turns with the mobile it names, at the same speed (`/app/FORMAT.md`).
- **Computing time.** Each condition and each check has up to 1800 s of elapsed (wall-clock) time on the
  inspection machine, and the whole inspection has up to 7200 s; a condition or check that runs out of time, or
  that would start after the whole inspection's time has run out, fails.

## 5. Part 1: going train and hands (`movement.json`)

The 8-hour build: the barrel runs at the speed class that the work order gives for the 8-hour build
(DS-W01, section 4).

Conditions. If one fails, Part 1 fails and none of its checks passes.

- **C1 Files.** `movement.json` and every part file it names are valid as `/app/FORMAT.md` describes. A hand
  entry that is present and does not name a mobile of the file and one of that mobile's parts makes the file not
  valid; `hour`, `minute` and `seconds` must be present.
- **C2 Assembled.** In the assembled positions: taking the frame as one solid and each mobile (the barrel included)
  as one solid, no two of these solids intersect by more than 0.01 mm3; no two fixed parts intersect each
  other by more than 0.01 mm3; no two parts of one mobile intersect each other by more than 0.01 mm3. The fixed
  parts form one frame: two fixed parts are joined when their smallest distance is at most 0.01 mm, and every
  fixed part is joined to every other through a chain of joined fixed parts.

Checks. Each passes or fails.

1. **Free to turn.** Each mobile, the barrel included, turned through one full turn about its axis in 72 steps of
   5 degrees, never intersects the frame by more than 0.01 mm3.
2. **Held.** Each mobile, the barrel included, is moved 0.3 mm along +x, -x, +y, -y, +z and -z in turn, and is
   held in every one of the six directions. Only the tested mobile moves; the frame and every other mobile stay
   where they are. Moved in a direction, a mobile is held when it intersects the frame by more than 0.01 mm3, or
   intersects by more than 0.01 mm3 a mobile whose axis is within 0.01 mm of its own and which is itself held
   in that direction; this is worked out until nothing changes. A mobile whose axis is further than 0.01 mm
   from its own never holds it.
3. **Seated.** Every part of a mobile that has more than one part, moved 0.3 mm along +x, -x, +y and -y in turn,
   intersects the other parts of its mobile by more than 0.01 mm3 every time, and moved 0.3 mm along +z or along -z
   (at least one of the two) intersects them by more than 0.01 mm3. The parts of each such mobile form one piece:
   every part is linked to every other by a chain of parts of that mobile, each within 0.02 mm of the next.
   The barrel and mobiles of one part are not tested.
4. **The train runs.** At least one mesh is declared; no mobile is given two different speeds by the declared
   meshes; every declared mesh passes the mesh test below; and every mobile is driven from the barrel through
   declared meshes that pass the mesh test.

   *Mesh test.* For a declared mesh, D is the mobile that the declaration names as `driver` (z_D teeth, its
   `driver_teeth`) and N the mobile it names as `driven` (z_N teeth, its `driven_teeth`), whichever way the power
   flows in the movement. D and N are whole mobiles: every part of each (for `barrel`, the supplied barrel).
   Starting from the assembled positions, at step i (i = 0, 1, ..., 8 x max(z_D, z_N) - 1) D is turned
   counter-clockwise by i x 360 / (8 x z_D) degrees about its axis, and N clockwise by that angle x z_D / z_N
   about its own axis. These turning senses are a convention of the test; they do not depend on the running sense
   of the barrel. Three conditions must hold:
   - no jam: at every step, and at two more positions after every 8th step (i + 1/3 and i + 1/5 in the formula
     above, for i = 0, 8, 16, ...), D and N intersect by at most 0.01 mm3;
   - engaged: at every 4th step (i = 0, 4, 8, ...) at which their intersection is empty, their smallest
     distance is at most 0.1 mm;
   - the teeth drive: at every 8th step (i = 0, 8, 16, ...), D is turned a further 0.25 of its tooth pitch
     (90 / z_D degrees, counter-clockwise) while N stays where it is. V is the volume of the region that the
     turned D shares with N and that D did not occupy before this extra turn; H is the z extent of that region (its highest point minus its lowest);
     m = 2 x (distance between the two axes in the assembled positions) / (z_D + z_N) is the mesh's module. V is
     at least 0.001 mm3 and V / H is more than 0.5 x m x m, at every one of these steps. (V / H is the area that
     the extra turn cuts into N's teeth.)
5. **The train runs with its arbors slightly out of place.** Every declared mesh also passes the mesh test with
   the driven mobile N moved 0.03 mm straight away from D's axis, and with N moved 0.03 mm straight towards
   D's axis (N then turns about its moved axis; if the two axes coincide, "away" is +x and "towards" is -x). The
   steps, the turning angles and m are those of the assembled positions. This check does not change which meshes
   drive the hands; that is decided in the assembled positions only.
6. **Nothing else collides.** Every pair of mobiles (the barrel included) that is not declared as a mesh is turned
   together, each at its speed from the declared tooth counts (a mobile that no declared mesh reaches from the
   barrel stands still): 144 equal steps covering one full turn of the faster of the two, then, if their speeds
   differ, 144 equal steps covering one full turn of one relative to the other. At every step they intersect by
   at most 0.01 mm3.
7. **Hour hand.** 8. **Minute hand.** 9. **Seconds hand.** The hands show the time, each turning clockwise at a
   constant speed: the hour hand one turn every 12 h, the minute hand one turn every hour, the seconds hand one turn every minute.
   A hand is driven only through declared meshes that pass the mesh test (a declared
   mesh that fails it drives nothing), and no mobile may be given two different speeds by the declared meshes.
10. **Hours and minutes on a common centre.** The axes of the hour hand's mobile and the minute hand's mobile are
    at most 0.01 mm apart.
11. **Hands.** Each of the hour, minute and seconds hand parts reaches at least 5 mm from its mobile's axis;
    lies wholly above the frame (its lowest point is no lower than the highest point of any fixed part); and
    points: its centre of volume is at least 0.5 mm from its mobile's axis.
12. **Fits the case.** Everything stays within the inner radius of the case named in the work order (DS-W02,
    section 2, column "Inner radius (mm)") of the vertical line through `case_centre` as it turns: every point of
    every fixed part, and, for each mobile, its largest distance from its own axis plus the distance from its axis
    to `case_centre`. The whole movement, the barrel included, is no taller in z than the inner height of that
    case (DS-W02, section 2, column "Inner height along the axis (mm)").
13. **Printable.** Each part of the delivery (not the barrel) is printable by the printability test of the process
    named in the work order (DS-W03, section 3).
14. **Gear strength.** The gears of the going train are strong enough in tooth bending.

    *Load case.* This calibre is the base of a family that includes an automatic version, whose barrel has a
    slipping bridle; the going train is rated for that version's barrel load. T_barrel is the upper end of the
    bridle's slipping torque, DS-101, Table 2a, row "Slipping torque of the bridle (min. to max.)", column for
    this series (N·mm), whatever mainspring the barrel of this build holds. The going train is stalled at its end,
    so each of its meshes carries the full torque that reaches it.

    *Meshes rated.* The going train: the declared meshes on the path from the barrel to the mobile that carries
    the seconds hand, through declared meshes that pass the mesh test (check 4); where there is more than one such
    path, the one a breadth-first search from the barrel finds first when it takes the meshes in their declared
    order (so the one with the fewest meshes). The motion work, and any other mesh off that path, is not rated. If
    the seconds hand's mobile is not reached from the barrel that way, this check fails. For each rated mesh, with
    D the mobile that the declaration names as `driver`, N the one it names as `driven`, and z_D and z_N their
    declared tooth counts:

    - torque at D: T_D = T_barrel x |n_barrel / n_D| (N·mm), with n the turns per hour that the declared tooth
      counts give through meshes that pass the mesh test (the same speeds as the hand checks);
    - module: m = 2 x (distance between the two axes in the assembled positions) / (z_D + z_N) (mm), as in the
      mesh test;
    - tooth load: F = T_D / (m x z_D / 2) (N), on the pitch circle of D;
    - face width: b = the smallest H over the drive steps of the mesh test for this mesh (mm), H being the height
      in z of the region that the further-turned D shares with N and did not occupy before;
    - bending stress of each of the two gears, each with its own tooth count z (z_D or z_N): sigma = F / (b x m x
      Y(z)) (MPa, that is N/mm2), Y(z) the Lewis form factor of DS-W04, section 3, for z teeth.

    *Which part holds a gear's teeth.* A mobile may be made of several parts, for example a wheel on a pinion
    arbor. In a rated mesh, the part that holds a gear's teeth is the part of that gear's mobile that holds the
    largest volume of the region the drive steps of the mesh test find for this mesh (the region that the
    further-turned D shares with N and did not occupy before; a part of D taken in its further-turned position, a
    part of N in its position at that step), that volume added over the drive steps. Where two parts hold the same
    volume, it is the one listed first in the mobile's `parts`. A one-part mobile holds its teeth in that part.

    *Allowable.* A gear's allowable stress is that of the material of the part that holds its teeth: the part's
    entry in its mobile's `part_materials`, or else the mobile's `material`. It is the lowest design allowable
    that DS-201 section 8 gives for that ordering code (a code with several rows, for example by stock thickness,
    is rated at the lowest of them, since the delivery does not state stock thickness). Tooth bending puts the
    root of the tooth in tension, so only a bending (tensile, yield-based) allowable applies: a row that gives a
    compressive allowable does not, and a code without a bending allowable in section 8 cannot be declared (C1).

    *Pass.* sigma <= the allowable for both gears of every rated mesh. The supplied barrel's own teeth are not
    rated here (the barrel is a supplied part, rated by its maker): in a mesh with the barrel only the other gear
    is rated.

## 6. Part 2: 24-hour hand (`movement.json`)

The 8-hour build, as in Part 1.

Conditions: C1 and C2 of Part 1, and **C3 24-hour hand declared**: `hands.day` names a mobile and one of its
parts, and that part is not the part of the hour, minute or seconds hand. A movement file without a `day` entry
fails C3.

Checks:

1. **24-hour hand.** It shows the hour of the day, turning clockwise at a constant speed of one turn every 24 h. It is driven only through declared
   meshes that pass the mesh test of Part 1, and no mobile may be given two different speeds by the declared
   meshes.
2. **24-hour hand placement.** Its mobile's axis is at least 6 mm from the axis of the hour hand's mobile;
   the hand part reaches at least 3 mm from its mobile's axis; it lies wholly above the frame; and its
   centre of volume is at least 0.5 mm from its mobile's axis.

## 7. Part 3: the 6-hour variant (`variant_6h.json`)

The 6-hour variant: the same barrel, in the same place, runs at the speed class that the work order gives for
the 6-hour variant (DS-W01, section 4).

Conditions: C1, C2 and C3 for `variant_6h.json`, and **C4 Same frame**: its `fixed` list is the same as that of
`movement.json` (the same names in the same order, so the same part files), and its `case_centre` is the same
two numbers.

Checks: every check of Part 1 and of Part 2, applied to `variant_6h.json` with the barrel at the speed class of
the 6-hour variant.

## 8. Part 4: assembly (`assembly.json`, for `movement.json`)

Conditions: C1 of Part 1 for `movement.json`, and `assembly.json` is valid JSON with a list `order` and an object
`paths` (`/app/FORMAT.md`).

The parts of `movement.json` include every part of its `keyless` section (Part 5), the stem's parts among them:
each is put in, tested and counted below exactly as any other part, and one left out of `order` stands in its
assembled position from the start.

The parts of `movement.json` and the barrel are put in one at a time, in the order of `order`. A name in `order`
that is not one of these parts is ignored; a name that appears more than once counts at its first place only. A
part that is not in `order` is not installed and stands in its assembled position from the start, so every part
in `order` is tested against it. Each part moves along its path. A part is installed when its path obeys all of
these rules:

1. The path is a list of 4x4 matrices. Every matrix is finite and is a proper rotation plus a translation
   (R^T R = I and det R = +1, within 1e-6); its last row is 0 0 0 1 within 1e-6; the last pose is the identity
   within 1e-6.
2. In the first pose, the part's bounding box lies wholly outside the bounding box of the complete movement (all
   its parts and the barrel, assembled) grown by 5 mm on every side.
3. Between consecutive poses, no vertex of the part moves more than 0.2 mm.
4. The path has at least 2 and at most 1,500 poses.
5. In every pose, the part intersects each part placed before it by at most 0.01 mm3, parts of its own mobile
   included.

A part that breaks a rule is not installed, but it still stands in its assembled position for the parts that
follow. Part 4 is judged by the share of the parts (the barrel included) that are installed; it passes in full
when every part is installed.

## 9. Part 5: crown winding (`movement.json`, its `keyless` section)

The 8-hour build, with its crown-winding works, is used on a simulated test rig the way an owner uses a watch.

Conditions. If one fails, Part 5 fails and none of its steps passes.

- **C1 Files** of Part 1 for `movement.json`, and its `keyless` section and every part file the section names are
  valid as `/app/FORMAT.md` describes.

The test rig.

- **Bodies.** The rig moves rigid bodies, each with one degree of freedom: the stem (the parts of `keyless.stem`),
  which the rig turns about the stem's line and moves along it; the barrel arbor (the arbor of the supplied
  barrel, DS-W01 section 3, with the parts of `keyless.arbor`), which turns about the barrel's axis; each mobile
  of `keyless.mobiles`, as declared; and, turning freely about their axes, every mobile declared `friction_on` and
  every mobile that the declared meshes drive from the barrel only through such a mobile. Everything else, the
  frame, the barrel's drum and every other mobile of `mobiles`, is one fixed body: the going train stands while
  the crown is used. The minute hand's mobile is called the minute mobile below.
- **Positions and directions.** Position 1 (pushed in) is the stem as delivered. Position 2 (pulled out) is the
  stem moved outwards along its line by the winding stem's travel from position 1 to position 2 (VM-DS-401,
  section 4, Table 2, this series). Forward is turning the crown clockwise as seen from outside the case, looking
  in along the stem; backward is the opposite. The arbor winds when it turns in the barrel's running sense
  (DS-W01, section 4).
- **Touching.** Two bodies touch, and do not interpenetrate, while they intersect by at most 0.0008456 mm3.
- **Friction.** Clean, dry contacts, brass on steel: coefficient of friction static 0.51, sliding 0.44
  (Engineering ToolBox, "Friction and Friction Coefficients"). A body pushed by another moves the least distance
  along its degree of freedom that the contact, with static friction, allows; if friction prevents it from giving
  way, it does not.
- **Springs.** Spring-loaded mobiles (`spring`) are urged towards their rest side by springs much lighter than the
  mainspring. They give way first when pushed; if they cannot give way, they are pushed along like any body. They
  return towards rest until they touch something; their springs never drive other bodies.
- **Mainspring.** The mainspring always urges the barrel arbor against winding. It is much stronger than any
  spring and pushes whatever is in its way.
- **The crown** is turned in steps of 3 degrees and pulled or pushed in steps of 0.04851 mm. A step that cannot
  proceed is blocked, and nothing moves. While pulling or pushing, a blocked step is retried with the crown rocked
  by up to 15 degrees either way, in steps of 1.5 degrees, to let teeth find their gaps.
- **At the start** of each step below, bodies may overlap and settle by up to 0.4851 mm of surface travel.
- **Starting states.** AT-1 starts from a let-down mainspring. AT-2 starts from a fresh movement whose barrel
  arbor the rig has turned in the winding sense by 45 degrees itself (the arbor, not the crown). AT-3 starts where
  AT-2 ends; AT-4, AT-5 and AT-6 each start from the state at the end of AT-2 (crown let go, in position 1).

Steps. Each passes or fails on its own.

0. **AT-0 Assemble.** At rest, as delivered, no two bodies intersect by more than 0.0008456 mm3. Every mobile of
   `keyless.mobiles` and every freely turning mobile of the going train, moved 0.4851 mm across its axis in each
   of two perpendicular directions (and, for one that turns, along its axis each way), intersects some other body
   by more than 0.0008456 mm3. Every part of the `keyless` section except the stem's lies within the inner radius
   of the case named in the work order (DS-W02, section 2, column "Inner radius (mm)") of the vertical line
   through `case_centre`; the whole movement with these parts is no taller than the inner height of that case
   (DS-W02, section 2, column "Inner height along the axis (mm)"); and stem material reaches at least 0.8085 mm
   beyond that radius.
1. **AT-1 Wind.** The crown, in position 1, is turned forward 1 turn. It is never blocked; it takes between 3 and
   12 crown turns per turn of the barrel arbor (measured over this turn); the minute mobile moves at most 1
   degree.
2. **AT-2 Hold.** The crown is let go for 40 steps: it is free to turn, pushed like any free body, and the
   mainspring pulls back. Every 5 steps the rig taps the movement: each free body moves up to 0.08085 mm (surface
   travel) in the direction it can move furthest, and spring-loaded bodies return towards rest. The arbor runs
   back at most 30 degrees in all, and over the last 10 steps it moves at most 0.3 degree: it is held.
3. **AT-3 Run.** Fully wound, the mainspring stores the turns of the arbor that VM-DS-101 gives for the spring the
   supplied barrel holds (Table 3, var. L, column "N at r = D/6"); the run-back measured in AT-2 is lost from
   that, and while the watch runs the barrel turns at the speed class of the 8-hour build (DS-W01, section 4), so
   the power reserve is (capacity - run-back) x the hours per barrel turn. It is at least 38 hours. The barrel is
   free to run: with the crown in position 1, the arbor is turned in the winding sense by itself through 20
   degrees in steps of 0.5 degree, and no step is blocked. It is still coupled: then the crown is turned forward
   30 degrees; it is never blocked and the arbor winds by more than 1 degree.
4. **AT-4 Backward.** The crown, in position 1, is turned backward 360 degrees. It is never blocked; the arbor
   moves at most 1 degree in the winding sense and loses at most 4 degrees; the minute mobile moves at most 1
   degree. Then the crown is turned forward 30 degrees: never blocked, and the arbor winds by more than 1 degree.
5. **AT-5 Set.** The crown is pulled out to position 2, stopping at 5 evenly spaced positions (both ends
   included). At each stop, from the same state, the crown is turned 24 degrees forward and, separately, 24
   degrees backward. No test turn is blocked, and none drives both trains (the arbor winding by more than 1 degree
   and the minute mobile moving by more than 1 degree). At position 1 the forward test turn winds and does not
   set; at position 2 it sets and does not wind. Then, in position 2, the crown is turned 90 degrees forward and
   90 degrees back: it is never blocked, the minute mobile turns at least 5 degrees each way, and the arbor never
   loses more than 4 degrees.
6. **AT-6 Return.** From position 2 the crown is pushed back in, stopping at the same positions in reverse order,
   with the same test turns and the same rules (never blocked, never both trains). Then, in position 1, it is
   turned forward 90 degrees: it is never blocked, and the arbor winds by more than 1 degree.

Part 5 is judged by the steps that pass. The rig runs Part 5 as one, within at most 5400 s of the whole
inspection's time; a step not finished by then fails.
