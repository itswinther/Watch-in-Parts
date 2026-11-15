<!-- NOT-FOR-AGENT: the v2 reference as an expert would build it. Never copied into the agent image. -->
# Keyless v2 reference in B's frame: step by step

The script is `../reference_v2.py` (`python3 spikes/keyless/reference_v2.py OUT --ref REF_JOB [--check] [--grade]`).
REF_JOB is B's job delivery (`python3 solution/reference_watch.py REF_JOB --job`). All lengths are in mm at
s = 1.617, in B's frame (+z is the dial side, the barrel axis is x = y = 0). Each choice below names the
datasheet cell it comes from, as the sheets stand on main at a79bfb5. The script records the same cells and
margins in `OUT/sizing_v2.json`.

## 0. What the reference has to fit

These are B's numbers (geometry/watch.py at 51568b7). They are parameters in `P`, and the defaults are B's new
values:

| Item | Value | Source |
| --- | --- | --- |
| Spring chamber | inner diameter 12.12, core radius 2.02, drum 1.0 tall | B 51568b7 (A's 19:50 request) |
| Winding square | side 1.4, z 3.3 to 4.9, sides parallel to x and y | B 18:45 |
| Winding sense | arbor wound clockwise seen from +z | B 18:45 |
| Frame | main plate -1.7 to -0.3, bridge 5.0 to 6.0 (bars), dial 8.8 to 9.6 | B 15:29 |
| Case | radius 20.7, centre (4.0391, -9.6417) | B's movement.json |

## 1. Mainspring: variant L

- **Choice.** VM-MS-M-L-DS: h 0.78, t 0.162, L 437, D 12.1.
  - **Cell.** DS-101 Table 1, row L.
- **Height.** 0.78 is at most the drum's 1.0, which leaves 0.22.
  - **Cell.** DS-101 Table 1, row L, "Height h".
- **Barrel.** L's listed D is 12.1 (7.5 × 1.617 = 12.13). B's chamber is 12.12, so DS-101 Note 1 ("fit a spring
  only in a barrel of its listed inner diameter") holds.
- **Core.** r = D/6 = 2.02.
  - **Cell.** DS-101 section 1 and Table 3, row L, "r = D/6".
- **Turns and reserve.** N = 4.9 turns gives 40 h.
  - **Cell.** DS-101 Table 3, row L.
  - The grader check (AT-3) uses capacity 4.9, so (4.9 − 30°/360°) × 8 h = 38.5 h, which is at least 38 h.
- **Design torque.** L is a manual spring (M end), so it has no bridle. Its first-yield torque is M_el =
  8.4 N·mm (DS-101 Table 2, row L).
  - DS-101 Note 2 says M_el is not an upper bound. It also says the highest torque the sheet states for the
    11½‴ class is the bridle's slipping torque of **70.1 N·mm** (DS-101 Table 2a, "Slipping torque of the
    bridle (min. to max.)", this series, upper end; a maker's limit). B states the same 70.1 N·mm as the
    train's design load (Decisions 20:36).
  - Every tooth is sized at **70.1**. `sizing_v2.json` also gives each stress at 8.4.
- **Kept as parameters.** `chamber_inner_d`, `core_r`, `square_side` and `square_z`. The script prints a note
  when B's geometry/watch.py differs from them.

## 2. Stem line: θ = 66°, not B's 36°

- **Why B's 36° fails.** At z 5.5 the stem lies in the bridge's thickness, and at 36° it crosses B's bridge bar
  from the third wheel to the pillar at (22.6, -3.5). That gives a 1.9 mm³ overlap (fit_keyless.py).
  - The bar cannot be re-routed without changing B's files.
- **The choice.** θ = 66° is radial from B's case centre, direction (0.4067, 0.9135, 0). The line runs through
  the open sector between the bars centre→third and centre→barrel.
  - Its closest approach to the third wheel's boss is 3.35 from the axis, which leaves 0.65 outside the pinions.
  - It passes 7.61 from the barrel axis and clears B's boss over the arbor.
- **Pull.** 1.294 (DS-401 Table 2, "Stem travel between adjacent positions", this series 1.29; B's 0.80 × s).

## 3. Crown and stem

| Choice | Value | Cell |
| --- | --- | --- |
| Crown | VM-CR-400-R-DS, Ø 6.47, 1.29 long | DS-401 Table 1 |
| Gap from crown to case middle | 0.16 (crown face at 20.86) | DS-401 Table 2, "at most 0.16" |
| Stem square | VM-ST-090-050-DS, A/F 0.809 (recommended max 46.0 N·mm, yield 92.1) | DS-401 Table 3 |
| Stem round | radius 0.467 (v1's 0.35 × 4/3) | carried over from v1 |
| Stem inner pivot | radius 0.38: passes the sliding pinion's square bore, so the stem goes in from outside | assembly (section 8a) |
| Stem groove (yoke) | core radius 0.35, width 0.23 | DS-401 Table 3: π r³ τ / 2 = 28.1 N·mm ≥ T_rec 27.2, with τ = 46 / (0.208 × 0.809³) = 418 MPa, the square's rated shear |
| Stem material outside the case | 1.69 (the rig asks for at least 0.81) | constants.STEM_PROTRUDE × s |

- **Why a Ø 6.47 crown and not Ø 4.85.** The crown torque is 20.0 N·mm (section 4).
  - Ø 4.85 gives T_rec = 4.20 × 4.85 = 20.4 N·mm (DS-501 Table 4), a margin of 2 %.
  - Ø 6.47 gives T_rec = 27.2 N·mm, a margin of 36 %.
- **The square.** It carries at most T_rec = 27.2 N·mm, which is within the recommended 46.0.
- **Stem length.** It is cut to length (DS-401 section 6). The inner end is at 9.08 from the case centre.

## 4. Winding train, sized by Lewis at 70.1 N·mm

**Train:** stem → winding pinion → crown wheel → intermediate wheel → ratchet.

- **Winding pinion.** 12 teeth, module 0.2 (v1's 0.15 × 4/3, so the bore around the 0.467 stem leaves a 0.26
  wall).
- **Crown wheel.** A 28-tooth face ring (R 2.8) facing the pinion, plus a 24-tooth spur, module 0.3234.
  - Its axis is on the stem line, inward of the pinion, at (7.273, -2.379), which makes it a true intersecting-axis
    face gear.
  - B's envelope put the crown wheel axis 4.2 off the stem line. That is a crossed-axis contact, which a spur
    pinion cannot mesh conjugately.
- **Intermediate wheel.** 12 teeth, at (6.961, 3.434), an idler.
  - The barrel axis lies 7.61 from the stem line, too far for a direct mesh.
  - The idler also restores the winding sense: an inward crown wheel turns the opposite way to v1's.
- **Ratchet.** 36 teeth, module 0.3234 (0.2 × s), on the square at z 3.31 to 3.70, steel.
- **Ratio.** (36/24) × (28/12) = **3.5 crown turns per arbor turn**. That is inside the rig's band of 3 to 12,
  and the crown torque is 70.1 / 3.5 = **20.0 N·mm**.

**Lewis, σ = F/(b·m·Y).** This is B's method (geometry/watch.py `strength_run`), with Y from
geometry/data/lewis_y.json.

| Gear | z | m | b | σ at 70.1 (MPa) | Steel allowable 725 | Brass 110 |
| --- | --- | --- | --- | --- | --- | --- |
| Ratchet | 36 | 0.3234 | 0.39 | 233 | pass (margin 2.1) | fail |
| Intermediate, ratchet side | 12 | 0.3234 | 0.39 | 375 | pass (0.93) | fail |
| Intermediate, crown side | 12 | 0.3234 | 0.28 | 522 | pass (0.39) | fail |
| Crown wheel spur | 24 | 0.3234 | 0.28 | 366 | pass (0.98) | fail |
| Winding pinion (face mesh, F = 46.7/2.8) | 12 | 0.2 | 0.70 | 468 | pass (0.55) | fail |
| Crown face ring (treated as a 28-tooth rack) | 28 | 0.2 | 0.70 | 312 | pass (1.32) | fail |

- **Allowables.** DS-201 section 8: steel AD-C100-HT 725 MPa (the lowest steel row), brass CW614N 110 MPa.
- **Material.** Every keyless wheel and pinion is declared **AD-C100-HT**. Brass fails every row at 70.1 N·mm.
- **At M_el = 8.4 N·mm** every stress is about 0.12 × the values above (28 to 63 MPa).
- **The band of z.** The ratchet sits at 3.31 to 3.70, the crown spur at 3.75 to 4.03, and the face ring's
  root at 4.05. The crown spur cannot rise into the face ring's root zone, because the pinion's tips reach
  4.10. This band sets b = 0.28 for the crown side, which is the smallest margin (0.39).

## 5. Breguet teeth and click

- **Breguet teeth.** 8 sawtooth teeth, 0.2 high, at radii 0.60 to 1.13 (v1 × 4/3).
  - The crown torque of 20.0 N·mm at a mean radius of 0.867 gives F = 23.1 N.
  - Treated as a cantilever with one tooth carrying all of it, root equal to one pitch: σ = 6Fh/(w·p²) =
    **112 MPa**, against 725 for steel.
  - The steep faces lock under μ 0.51 (DS-201 Table 7, brass on steel, static), as in v1.
- **Click ring.** 24 sawtooth teeth, radius 3.19 to 3.70, at z 4.25 to 4.55, on the ratchet.
  - The click is v1's geometry (pivot on the tangent through the tip), scaled by 1.276 in plan and turned
    150° about the barrel axis, so it sits clear of the crown wheel, under the keyless bridge.
  - Tooth force 70.1 / 3.70 = 18.9 N. Bending gives 206 MPa, against 725 for steel.

## 6. Pivots (DS-301)

| Pivot | Radial load | Bushing | F_max | Hole | Post Ø |
| --- | --- | --- | --- | --- | --- |
| Crown wheel | 20.6 N | RL-B-40-150-55-DS | 63.3 N | 0.647 | 0.601 |
| Intermediate wheel | 24.1 N | RL-B-40-150-55-DS | 63.3 N | 0.647 | 0.601 |
| Click | 18.9 N | RL-B-30-100-30-DS | 25.9 N | 0.485 | 0.451 |
| Setting wheel and setting idler | the hands' friction only | RL-B-30-100-30-DS | 25.9 N | 0.485 | 0.451 |

- **Sources.** Loads come from the mesh forces above; F_max is from DS-301 Table 4 (section 5.3); holes are
  from Table 3.
- **Clearance.** DS-301 section 5.1 gives hole = pivot + 0.016 at Ø 0.226. It is applied proportionally:
  0.016 × hole/0.226, i.e. 0.046 at 0.647 and 0.034 at 0.485. The sheet states only "proportionally smaller"
  for smaller pivots, so this is an extrapolation and is labelled as such.

## 7. Setting train (position 2)

**Train:** sliding pinion → setting wheel → setting idler → B's hour wheel.

- **Sliding pinion.** 12 teeth, module 0.2, sprung towards the winding pinion (`spring`, `rest -1`, on the stem).
  - A **yoke** draws it out by 1.294 − 0.2 = 1.094 (0.015 groove clearance, 0.185 finger gap).
    - The yoke is a slide (`free`, `slide` along the stem) on two shouldered studs on the keyless bridge.
    - One finger sits in the stem's groove; the other sits in a neck turned in the sliding pinion (core 0.85).
    - Pulling the stem, the groove's inner wall drives the yoke out, and its finger draws the pinion off the Breguet
      teeth onto the setting wheel. Pushing in, the outer wall brings the yoke back and the pinion's spring follows.
    - The neck leaves 0.32 behind the finger, more than the Breguet teeth's 0.2 lift, so the yoke never holds the
      pinion off the winding pinion while the crown is turned backwards.
    - It replaces v1's collar in a counterbore. A collar inboard of the pinion cannot be put in from outside after
      the pinions, which the installation order (section 8a) needs.
    - Main's engine moves a contact body by contact only, so the yoke is a slide, not a pivoted lever with a spring
      (that is the engine-fix branch, section 10).
- **Setting wheel.** A 28-tooth face ring over the pulled pinion, plus a 16-tooth spur, module 0.2, on B's
  hour-wheel layer z 7.6 to 8.4. Its axis is on the stem line, at (8.694, 0.813).
- **Setting idler.** 24 teeth, module 0.2, at (6.003, -2.147).
- **Hour wheel.** B's hour wheel, 48 teeth, module 0.2. It drives B's minute wheel (12 → 48) and the cannon.
  - This is Grossmann's pair of setting wheels.
  - The minute wheel itself is out of reach of any wheel on the stem line: the cannon pinion blocks layer E.
- **Ratio.** Crown 90° turns the hour wheel 12.9°. The minute wheel then turns 51°, at least the rig's 5°.
- **Posts.** B's job dial is a skeleton of bars with nothing over S1 or S2.
  - The setting idler sits on a seat that stands on the keyless bridge. A headed post (0.5 head) goes in through
    it from the dial side, after it.
  - The setting wheel's post comes in from the dial side after the wheel. It has a shoulder above the wheel and
    no head below: the winding pinion holds the wheel from below.
  - A setting cover joins the two posts into B's frame (B 02:41: the setting post stood apart, so the `assembled`
    gate failed). It is a plate under the dial, between the motion work and the dial (z 8.42 to 8.8), round the
    setting post's shoulder and the idler post's head, each in a bore 0.005 over its radius. It goes in last.
  - The idler post's head is 0.5 thick, more than B's HOLD_SHIFT 0.485, so the held test's jump lands in it. The
    click post's head goes down to 0.05 over the ratchet for the same reason.
  - The heads of the crown-wheel and intermediate posts and of the yoke's studs are 0.25 thick (`head_t`): at 0.07
    to 0.1 they failed B's printable check (MIN_FEATURE 0.2, deviations 0.22 to 0.36 against THIN_DEV 0.2). Now
    every keyless fixed part opens within 0.16.
- **Cannon.** Split from the centre mobile as `friction_on: centre` (Decisions 15:47), with the minute hand.

## 8. Fixed parts and how they meet B's frame

- **Keyless bridge.** One plate at z 4.6 to 5.0, under B's bridge. It touches the barrel→centre bar at z 5.0
  (zero overlap), and its path is cut clear of the pinions.
  - It carries the crown-wheel post, the intermediate post, the click post, the stem bridge, the yoke's two
    studs and the setting idler's seat.
  - Every post and stud only touches it: no overlap, so each can be installed on its own.
- **No stem guide.** v2 had one at 19.0 to 19.6 along the stem, for the case tube. The case is not modelled, so
  it touched nothing in B's frame and failed the `assembled` gate (B 02:41). It is gone: the stem is held by the
  stem bridge, the winding pinion's bore and the sliding pinion's square (AT-0 held: no failure).
- **Setting posts and cover.** Hung from the dial side, joined by the setting cover (section 7). B's frame check
  (`Movement.frame()`) finds one frame of all fixed parts.

## 8a. Installation order (QA-W100 section 8)

This follows REAL_WATCH_WORK.md section 4 (Unitas/ETA 6497) where B's frame allows.

- **The pinions go first, then the stem.** The winding pinion and the sliding pinion go in along the stem line
  from outside the case. Then the stem slides in radially through them to position 1, as in the 6497.
- **The yoke goes in after the stem, then its studs.** Its fingers drop into the stem's groove and the pinion's
  neck from the dial side. This is the 6497's setting lever peg in the stem's slot.
- **The setting wheels go in on the dial side,** after B's bridge.
- **One difference from the 6497.** There the crown wheel, the click and the ratchet sit on top of the barrel bridge. Here
  they sit under the keyless bridge, which goes on after them. B's frame has no barrel bridge over the barrel.
- **The merged order.** B's job order (`ORDER_8H`), with:
  - after `seconds`: ratchet, click_post, click, intermediate_post, intermediate_wheel, crown_post, crown_wheel,
    keyless_bridge, stem_bridge, winding_pinion, sliding_pinion, stem, yoke, yoke_stud_a, yoke_stud_b;
  - after `bridge`: setting_wheel, setting_post, setting_idler_seat, setting_idler, setting_idler_post,
    setting_cover.
- **Paths.** The pinions and the stem translate along the stem direction, from wholly outside the box grown by
  5 mm. Every other part comes straight down from above, as in B's plan. The steps are 0.19 mm.
- **Check.** `reference_v2.py OUT --ref REF --assembly-only DELIVERY` merges the parts and replays the plan
  with B's `Movement.assembly_replay` (keyless parts attached). All 38 parts install, B's included, with no
  pose over 0.01 mm³. The fragment is written to `assembly_keyless.json`.

## 9. Results

- **Fit, checked with `--check` in Docker.** No collision with any part of B's delivery (mm³ > 1e-6), with
  the barrel taken as its two bodies.
  - Smallest gaps: setting idler to hour wheel 0.014 (a mesh), crown post to centre arbor 0.43, crown wheel
    to bridge 0.5.
  - The keyless bridge touches B's bridge.
- **AT-0 on the joined model.** B's frame and going train fixed; B's motion work free, with the cannon
  `friction_on`. Rest overlap is none over 2e-4 mm³, every mobile is held, and the bounds pass (the stem is
  1.69 outside).
- **Every stem position against B's dial, bridge and plate.** The stem is moved by p, the yoke by p − 0.015 and
  the sliding pinion by p − 0.2, for p = 0, 0.3, 0.65, 0.9, 1.1 and 1.294. Nothing touches (mm³ > 1e-7).
- **B's runner (Part 5, `geometry/keyless_job.py` SCALE_TABLE, `tests/grade_keyless.py` through
  `solution/keyless_v1_delivery.py grade`), first run (v4 delivery, serial, loaded box).** s = 0.72.
  - AT-0 to AT-4 pass: 3.525 crown turns per arbor turn, a run-back of 0.45°, 47.99 h at the old capacity of 6
    turns (39.2 h at L's 4.9).
  - AT-5 and AT-6 fail: the pull blocks at 0.37 mm, where the yoke starts to draw the sliding pinion. This is
    being fixed.
  - Wall time 3347 s, of which AT-1 took 2399 s.
- **Installation order.** It passes B's section 8 replay merged into the job plan: section 8a.
- **STEP.** `--deliver` writes all 21 parts as B-reps that load through B's STEP reader as real solids (no part
  over one flat triangular face; the largest file, the crown wheel, is 15.3 MB of the 16 MB limit).
  - 17 parts are planar-faced: coplanar triangles merge into one polygon face, built in frame V (axis-aligned
    planes) and moved into B's frame as a B-rep. Round trip within 4e-5 mm³.
  - The other four have curved faces, built by `spikes/keyless/exact_v2.py`:
    - Breguet teeth (winding and sliding pinions): each edge of the unrolled tooth profile is a helix on the
      inner and outer cylinders, and the flank between them is the ruled helicoid. The winding pinion's cutters
      are clipped to one turn, as the mesh builder does. Round trip 4e-4 and 8e-4 mm³ against the 0.03-facet
      mesh.
    - Face rings (crown and setting wheels): the pinion envelope is recut with 200 poses a pitch (the mesh uses 16),
      sliced across the gap by planes 0.02 to 0.05 mm apart, each slice fitted with a 60-pole cubic B-spline,
      and the slices lofted into one gap. The gap is grown 0.0005 mm first, so the spline's fit error (at most
      0.0012 mm, at the gap bottom of the outer end) never adds material. One pitch of the ring is cut, and 28
      turned copies of its faces are sewn into the ring: cutting 28 gaps from one ring dropped some gaps, where
      the pointed outer tooth ends bring neighbouring gaps within a hair. Web, hub and bore are true cylinders.
      Against the 200-pose mesh the slices are within 0.0015 mm almost everywhere; the round trip differs from
      the design mesh by 0.020 and 0.024 mm³, mostly the 0.0005 mm growth.

## 10. What the engine-fix branch (a/keyless-engine-fixes, not merged) would allow

- **A pivoted setting lever and a sprung yoke instead of the slide.** With "springs push through links" the yoke
  spring could push the sliding pinion through the yoke, as in every modern calibre. Main's engine only lets
  a spring part move itself, so v2's yoke is a slide driven both ways by the stem's groove.
- **A click spring as its own part.** Same reason.
- **Line-to-line fits.** `relieve_fits` / FIT_CLEARANCE would let the ratchet sit line to line on the square
  and the wheels on posts at the drawn size. Main needs the explicit DS-301 clearances.
- **No phase search.** "Phase before Rest" would set the gear phases at rest. v2 searches the phases itself:
  `clear_phase` and the geared pinion phase.
- **A declared pull and `carrier`.** These would let the setting wheel ride a pivoted lever (`carrier`) and
  let a design declare its own travel.
  - On the branch, PULL_RANGE is 0.4 to 1.0 in A's unscaled frame. B's 1.294 needs that range × s.
- **The rig in B's frame.** grade.py `load()` still hard-codes the frame (stem along +x, BARREL_AXIS,
  MINUTE_AXIS). v2 grades by mapping B's parts into the v1 frame and patching `constants` in memory. The P5
  adapter should take the stem point and direction and the axes from the keyless section instead.

## 11. Comparison with Grossmann (*Lessons in Horology*, art. 168–169)

| Part | Grossmann | v2 | Why it differs |
| --- | --- | --- | --- |
| Winding pinion | 18 | 12 (spur, meshing a 28-tooth face ring) | A conjugate face gear needs the spur pinion. 18 × 0.2 would be Ø 3.6, beyond the 1.4 tip B's envelope and the bridge gap allow |
| Crown wheel | 42 | 28 face + 24 spur, two sets of teeth | Grossmann's crown wheel idles between pinion and ratchet with one set of teeth. Here the barrel is 7.61 from the stem line |
| Ratchet | 44 | 36 spur + 24-tooth click ring | Tip radius ≤ 6.15 keeps clear of the fourth wheel (6.7 from the barrel axis); the separate click ring is v1's proven click geometry |
| Intermediate wheel | – | 12 | The barrel's distance, and the winding sense of an inward crown wheel |
| Sliding pinion | 16 | 12 spur + 8 Breguet teeth | Module 0.2 at a 1.4 tip |
| Setting wheels | 27 and 18 | 28/16 setting wheel and 24 idler | The same two-wheel arrangement; v2 meshes the hour wheel, because the cannon blocks the minute wheel's layer |
| Minute wheel / cannon | 30 / 12 | B's 36 / 12 | B's |
| Crown turns per arbor turn | 44/18 = 2.44 | 3.5 | At 70.1 N·mm, 2.44 needs 28.7 N·mm at the crown, above T_rec for every catalogue crown up to Ø 6.47 (27.2). It is also below the rig's band of 3 to 12 |

**Known limit.** DS-401 Table 4 rates a crown and its keyless works to withstand 179.3 N·mm at the crown
against a fully wound spring.

- v2 does not meet it. The VM-ST-090-050-DS square yields at 92.1 N·mm.
- At 3.5 turns per turn, 179.3 N·mm at the crown puts 628 N·mm on the arbor, about 9 × the design load on
  the teeth.
- No square that fits the 1.4-tip pinions reaches 179.3. This is recorded, not hidden: the brief asks for the
  70.1 N·mm design case.
