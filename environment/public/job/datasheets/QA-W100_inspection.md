# Inspection procedure: movement design deliveries, demonstration-scale calibre

| Document | Revision | Date | Status |
|---|---|---|---|
| QA-W100 | B | 2026-11-15 | Released |

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

## 3. Acceptance

**How the delivery is inspected.** The quality department inspects the delivery after hand-over with its own test
rig. This procedure states what must hold. It does not describe how the rig turns, moves or samples the parts.
Each requirement is met or not met, and is judged on its own. Where this procedure says check, it means
requirement.

**Collide.** Two solids collide when their intersection is larger than 0.01 mm3. A smaller intersection is
modelling noise and counts as no contact. "Is stopped by" means "collides with".

The inspection has four parts. Each part is judged on its own, even when another part fails. Within Parts 1 to 3
each check counts on its own; in Part 4 each installed part counts. The delivery as a whole is accepted only when
every condition and every check of all four parts passes: everything must work.

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
or not valid. The statement's agreement score h is the mean of these points over the four parts, or 0 if that mean
is below 0. The delivery's acceptance figure is its parts figure (the result of the four parts together) times
(0.75 + 0.1 x h) / 0.85. The statement changes no other result of the inspection.

The statement may also give the movement's height (`height_mm`, `/app/FORMAT.md`). It is recorded and does not
change any result.


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
  barrel at the speed, and in the running sense, of the speed class that the work order gives for the build
  being judged (DS-W01, section 4). Every declared mesh is external: its two mobiles turn in opposite directions.
- **Computing time.** Each condition and each requirement has up to 1800 s of rig time, and the whole inspection
  up to 7200 s; a condition or requirement that runs out of time, or that would start after the whole inspection's
  time has run out, is not met.

## 5. Part 1: going train and hands (`movement.json`)

The 8-hour build: the barrel runs at the speed class that the work order gives for the 8-hour build
(DS-W01, section 4).

Conditions. If one fails, Part 1 fails and none of its requirements is met.

- **C1 Files.** `movement.json` and every part file it names are valid as `/app/FORMAT.md` describes. A hand
  entry that is present and does not name a mobile of the file and one of that mobile's parts makes the file not
  valid; `hour`, `minute` and `seconds` must be present.
- **C2 Assembled.** In the assembled positions, taking the frame as one solid and each mobile (the barrel
  included) as one solid, no two of these solids collide; no two fixed parts collide; no two parts of one mobile
  collide. The fixed parts form one frame: every fixed part is linked to every other through a chain of fixed
  parts, each within 0.01 mm of the next.

Requirements.

1. **Free to turn.** Each mobile, the barrel included, turns through a full turn about its axis without colliding
   with the frame at any angle.
2. **Held.** No mobile, the barrel included, can move 0.3 mm on its own along +x, -x, +y, -y, +z or -z. Moved that
   far in any of these directions, with everything else in place, it is stopped by the frame, or by a mobile whose
   axis is within 0.01 mm of its own and which is itself held in that direction. A mobile on another axis never
   holds it.
3. **Seated.** Every part of a mobile that has more than one part is fixed in its mobile. Moved 0.3 mm along +x,
   -x, +y or -y, it is stopped by the other parts of its mobile, and moved 0.3 mm along +z or along -z (at least
   one of the two) it is stopped too. The parts of each such mobile form one piece, each within 0.02 mm of the
   next. The barrel and one-part mobiles are exempt.
4. **The train runs.** At least one mesh is declared. No mobile gets two different speeds from the declared
   meshes, and every mobile is driven from the barrel through declared meshes that drive. Every declared mesh
   drives. A declared mesh, D its `driver` (z_D teeth) and N its `driven` (z_N teeth), drives when, as D turns N
   at the ratio z_D / z_N through a full turn of the larger gear:
   - the two never collide;
   - they stay in mesh: wherever they do not touch, they are at most 0.1 mm apart;
   - the teeth carry the drive: from every position of that turn, turning D a further 0.25 of its tooth pitch
     (90 / z_D degrees) while N is held makes D cut into N. The region cut into N is at least 0.001 mm3, and
     its volume divided by its height along z is more than 0.5 x m x m, with m = 2 x (distance between the
     two axes) / (z_D + z_N).

   Every declared mesh is external: its two mobiles turn in opposite directions. A mesh that does not drive drives
   nothing. Elsewhere in this procedure, "passes the mesh test" means "drives" in this sense, and the drive steps
   of the mesh test are the positions from which D is turned the further 0.25 of its tooth pitch.
5. **Runs with its arbors slightly out of place.** Every declared mesh also drives with N's axis moved 0.03 mm
   straight towards D's axis, and with it moved 0.03 mm straight away.
6. **Nothing else collides.** As the movement runs, at any time of day, no two mobiles that are not declared as a
   mesh ever collide with each other.
7. **Hour hand.** 8. **Minute hand.** 9. **Seconds hand.** The hands show the time, each turning clockwise at a
   constant speed: the hour hand one turn every 12 h, the minute hand one turn every hour, the seconds hand one turn every minute.
   A hand is driven only through declared meshes that pass the mesh test (a declared
   mesh that fails it drives nothing), and no mobile may be given two different speeds by the declared meshes.
10. **Hours and minutes on a common centre.** The axes of the hour hand's mobile and the minute hand's mobile are
    at most 0.01 mm apart.
11. **Hands.** Each of the hour, minute and seconds hand parts reaches at least 5 mm from its mobile's axis;
    lies wholly above the frame (its lowest point is no lower than the highest point of any fixed part); points
    (its centre of volume is at least 0.5 mm from its mobile's axis); and, seen from the dial side, covers at
    most 0.25 of the area of the disc its tip sweeps.
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
    slipping torque of the automatic version's bridle (DS-101, Table 2a), whatever mainspring the barrel of this
    build holds. The going train is stalled at its end, so each of its meshes carries the full torque that reaches
    it.

    *Meshes rated.* The going train: the declared meshes on the path from the barrel to the mobile that carries
    the seconds hand, through declared meshes that pass the mesh test (check 4); where there is more than one such
    path, the one a breadth-first search from the barrel finds first when it takes the meshes in their declared
    order (so the one with the fewest meshes). If the seconds hand's mobile is not reached from the barrel that
    way, this check fails. For each rated mesh, with D the mobile that the declaration names as `driver`, N the
    one it names as `driven`, and z_D and z_N their declared tooth counts:

    - torque at D: T_D = T_barrel x |n_barrel / n_D| (N·mm), with n the turns per hour that the declared tooth
      counts give through meshes that pass the mesh test (the same speeds as the hand checks);
    - module: m = 2 x (distance between the two axes in the assembled positions) / (z_D + z_N) (mm), as in the
      mesh test;
    - tooth load: F = K x T_D / (m x z_D / 2) (N), on the pitch circle of D, with K the load factor for
      unlubricated (dry) meshing of DS-W04, section 2: the gears of this movement run without lubricant;
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
   the hand part reaches at least 3 mm from its mobile's axis; it lies wholly above the frame; its
   centre of volume is at least 0.5 mm from its mobile's axis; and seen from the dial side it covers at most
   0.25 of the area of the disc its tip sweeps, measured as in Part 1 check 11.

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

## 9. Thickness

The order asks for a slim calibre. The movement's height H is the highest point minus the lowest point of every
part of the movement and of the barrel, in the assembled positions, along the axis. The taller of `movement.json`
and `variant_6h.json` counts. The target is **4.0 mm**.

With C the inner height of the case named in the work order (DS-W02, section 2, column "Inner height along the
axis (mm)"):

    x = (H - 4.0) / (C - 4.0), taken as 0 below 0 and as 1 above 1
    thickness score s = (1 - x) ^ 4

The acceptance figure is 1/2 x (the result of Parts 1 to 4 together) + 1/2 x [every condition and every
requirement of Parts 1 to 4 is met] x s, times the statement factor of section 3. A movement file that does not
load counts as no thickness score (s = 0).
