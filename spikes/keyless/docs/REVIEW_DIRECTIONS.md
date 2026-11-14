# Review: direction, sense and sign wording in PROMPT.md

Independent reviewer. I read only `PROMPT.md` (same content on origin/main and in the main checkout at review time).
I did not read SOLUTION.md, STEP_BY_STEP.md, the grader, the reference or any notes on intent. I ran no code.

## Frame as I reconstruct it

- Right-handed, mm. x = stem axis, crown end at +x. z points towards the main plate, so +z is the
  main-plate side (main_plate z 2.6..3.2) and -z is the dial side (dial_plate z -3.2..-2.6, minute
  wheel z -2.4..-1.9). y follows from x and z by right-handedness (y = z × x).
- "Vertical" = parallel to z (inferred, never defined).
- Crown forward = rotation of −θ about +x (clockwise to an eye at +x looking towards −x). Backward = +θ about +x.
- Winding = +φ about +z (anticlockwise to an eye at +z looking towards −z). The mainspring urges −φ.
- Position 2 = stem translated +$PULL along x from its submitted pose. Pushing in = towards −x.

## Statement table

| # | Sentence (abridged) | Line | My reading | Ambiguous | Why |
|---|---|---|---|---|---|
| 1 | "Pushed in, turning the crown forward winds the mainspring, and turning it backward does no harm." | 10 | Goal only; senses defined at line 42. | no | Forward/backward are defined later and used consistently. |
| 2 | "Right-handed, millimetres. z points towards the main plate." | 36 | +z = main-plate side; dial at −z. Matches plate z ranges at line 49. | no | Explicit and confirmed by numbers. Horological note: the main plate is traditionally the dial-side plate; here the dial plate is a separate part at −z. The numbers settle it, but a reader thinking "main plate = dial side" could invert z in their head. |
| 3 | "Angles follow the right-hand rule about a stated direction." | 36–37 | Positive angle = right-hand rotation about whichever vector is named (+x, +z, or a mobile's `direction`). | no | Clear. It is the only place that defines the sign of a `rot` mobile's coordinate (see #11). |
| 4 | "Stem axis: the x axis (y = 0, z = 0). The crown end is at +x, outside the case." | 39 | Stem lies on the x axis; crown at the +x end. | no | |
| 5 | "position 1 (pushed in) is the stem as you submit it. Position 2 (pulled out) is the stem moved $PULL towards +x." | 40–41 | Pull = +x translation by $PULL from the submitted pose. | no | Consistent with #4. |
| 6 | "forward is turning the crown clockwise as seen from outside the case looking in (from +x towards −x), that is a negative rotation about +x. Backward is the opposite." | 42–43 | Forward = −θ about +x. | no | Viewpoint, sense and right-hand sign are all given and agree (an eye on +x sees positive rotation as anticlockwise). |
| 7 | "It turns about the vertical line through x = $BARREL_X, y = $BARREL_Y." | 50–51 | Arbor axis parallel to z. | minor | "Vertical" is never defined. Context (the case cylinder "about the vertical line ... from z0 to z1") implies z, but nothing says so outright. |
| 8 | "Winding turns it anticlockwise as seen from +z (positive about +z)." | 51 | Winding = +φ about +z. | minor | "Seen from +z" has no "looking towards −z", unlike line 43, so on its own it could be read as "looking towards +z", which would flip the sense. The parenthetical "positive about +z" together with #3 fixes it, so only a careless reader goes wrong. |
| 9 | "The mainspring always urges it the other way (see the test rig)." | 51–52; also 136 | Mainspring torque on the arbor is −φ about +z. | no | Matches line 136 ("against winding"). |
| 10 | "minute_wheel ... turns freely about the vertical line through x = $MINUTE_X, y = $MINUTE_Y." | 57–59 | Axis parallel to z. No required sense for setting. | minor | Same "vertical" point as #7. No sign is required anywhere for the minute wheel (AT-5 says "each way"), so no sign issue. |
| 11 | "`rest` (`spring` only): `1` or `-1`, the sign of the mobile's own coordinate that its spring urges it towards." | 79–80 | `slide`: coordinate = displacement along the declared `direction` vector, zero at the submitted pose; `rest: -1` urges motion along −direction. `rot`: coordinate = right-hand angle about `direction`. | **yes** | "The mobile's own coordinate" is never defined: not its zero (submitted pose?), and not, for `slide`, that the positive sense is along the declared `direction` vector (it could be read as along the world axis it is parallel to). For `rot`, the sign follows only by combining with #3. Flipping `direction` silently flips what `rest` means. |
| 12 | "`on_stem` (optional, `slide` along the x axis only): ... its own coordinate is then its slide." | 81–82 | Slide coordinate along the declared direction (±x); also rotates with the stem about x. | **yes** | Same undefined coordinate. With `direction: [-1,0,0]` a positive slide points towards −x (inwards). Not stated. |
| 13 | "Parts: each part is one closed manifold solid ... in position 1 and at rest." | 66 | Spring mobiles are submitted at their rest pose (coordinate 0). | minor | Combined with "urged towards their stated rest side ... until they touch something" (line 132–134), "at rest" could mean "at coordinate 0" or "already against its stop on the rest side". Also, does "rest side" refer to the sign in #11 (it seems to) or a pose? |
| 14 | Example JSON: `"direction": [0, 0, 1]` for `wheel_1`. | 92 | A free rot mobile about +z. | no | Has no `rest` or `on_stem`, so it illustrates no sign convention. That is not a contradiction, just a gap: a `spring` example would pin down #11. |
| 15 | "The test rig turns it about the stem axis and pulls it along that axis." | 99–100 | Turns about x, translates along x. | no | |
| 16 | "Held: every free and spring mobile, moved $HOLD_SHIFT across its axis in either of two perpendicular directions ... For rot mobiles this also applies along the axis, either way." | 163–165 | Shift ± along two perpendicular directions normal to the axis, and ± along the axis for rot. | **yes** | "Either of two perpendicular directions" could mean two shifts (+u, +v) or four (±u, ±v). "Either way" is said only for the axial case, which suggests the radial shifts are one-sided. Which two perpendiculars are used is not said. "Either" could also be read as "at least one of" rather than "each of". |
| 17 | "The stem may leave the case cylinder sideways, and some stem material must reach at least $STEM_PROTRUDE outside the case radius." | 166–167 | Stem must poke radially out of the case wall by $STEM_PROTRUDE, at the crown (+x) end. | minor | Does not say at which end. #4 implies +x, but an agent could satisfy "some stem material" at −x if the case geometry allowed it. "Sideways" means radially, not along z; this is inferable but unstated. |
| 18 | "AT-2 ... The crown is let go ... The mainspring pulls back." | 180–181 | Mainspring drives the arbor −φ about +z, and the stem is free to rotate either way. | no | |
| 19 | "Barrel free to run. ... the arbor is turned forward (the winding direction) by itself through $FREE_RUN_DEG degrees" | 190–193 | Arbor turned +φ about +z. | minor | "Forward" was defined only for the crown about +x; here it is reused for the arbor about +z. The parenthetical fixes the sense. A reader may still find the heading "free to run" (running = the barrel giving out power, i.e. unwinding) at odds with turning in the winding direction. That is a wording tension, not a sign ambiguity. |
| 20 | "Nothing winds: the arbor moves at most $STILL_TOL degree forwards and loses at most $HOLD_TOL degrees." | 198–199 | Arbor: ≤ STILL_TOL in +φ, ≤ HOLD_TOL in −φ. | minor | Uses arbor-"forwards" from #19. Consistent, but it depends on that reuse. |
| 21 | "the arbor winds by more than $STILL_TOL degree" (AT-3, AT-4, AT-5, AT-6) | 195, 202, 207, 217 | Net +φ about +z exceeds STILL_TOL. | no | |
| 22 | "the crown is turned $SET_TURN degrees forward and $SET_TURN back" | 211–212 | −θ then +θ about +x. | no | "back" = backward; clear in context. |
| 23 | "pushed back in, stopping at the same positions in reverse order" | 214–215 | Translate towards −x to position 1. | no | |
| 24 | "the crown is rocked by up to ±$WIGGLE_DEG degrees" | 221–222 | Symmetric about x. | no | |

## End-to-end chain

Crown forward = −θ about +x (line 42–43) → the keyless works must drive the barrel arbor +φ about +z
(line 51), i.e. anticlockwise to an eye on the main-plate side (+z) looking towards the dial (−z).
The mainspring pushes −φ about +z, and the click (or whatever holds the arbor) must resist −φ.
Each end of the chain is stated twice (a viewpoint and a right-hand-rule sign), and the two
statements agree. The only weak link is "seen from +z" lacking "looking towards −z", which the
parenthetical "(positive about +z)" makes redundant. **The chain is stated unambiguously.**

The agent must work out the intermediate gear senses itself (stem → winding pinion → crown wheel →
ratchet wheel, each mesh reversing sense). The brief doesn't need to give them, but this is where
a mirror error would actually come from.

## Proposed replacement sentences

1. Line 51: "Winding turns it positive about +z: anticlockwise to an eye on the +z side looking towards −z."
2. Lines 50, 58, 44: replace "the vertical line through" with "the line parallel to z through".
3. Lines 79–80: "`rest` (`spring` only): `1` or `-1`. A mobile's own coordinate is zero as submitted. For `slide` it is the displacement along the declared `direction` vector; for `rot` it is the angle about `direction` by the right-hand rule. The spring urges the coordinate towards the sign given by `rest`."
4. Line 82: "its own coordinate is then its slide, measured along its declared `direction` (which is `[1,0,0]` or `[-1,0,0]`)."
5. Line 66: "Each part is submitted in position 1, with every spring mobile at coordinate zero."
6. Lines 163–165: "every `free` and `spring` mobile is shifted $HOLD_SHIFT in each of the four directions ±u, ±v, where u and v are two perpendicular directions normal to its axis; for `rot` mobiles also by ±$HOLD_SHIFT along the axis. Each shift must overlap some other body by more than $TOL mm³."
7. Line 167: "some stem material at the +x end must reach at least $STEM_PROTRUDE outside the case radius."
8. Lines 192–193: "the arbor is turned in the winding direction (positive about +z) by itself …". Don't call the arbor's sense "forward".
9. Line 198: "the arbor turns at most $STILL_TOL degree positive about +z and at most $HOLD_TOL degrees negative about +z."

None of these says anything about how to design the mechanism.

## Verdict

**No.** A competent agent reading carefully would not reasonably build a mirror-image mechanism
from this text. The two sense statements that decide handedness (crown forward = negative about +x;
winding = positive about +z) are each given with an explicit right-hand-rule sign, which is defined
in the frame section. The crown statement also has a fully specified viewpoint, and the barrel
statement's viewpoint, though loosely worded, agrees with its sign. The plate z ranges confirm
which side +z is. The real direction risks lie elsewhere:

- the undefined "own coordinate" behind `rest` and `on_stem`, where a reversed `direction` vector
  silently flips the spring's sense;
- the one-sided vs two-sided reading of the AT-0 "Held" shift.

Neither of these can mirror the winding chain.
