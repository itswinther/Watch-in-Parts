# Real watch CAD against the keyless acceptance test

NOT-FOR-AGENT. Everything in `spikes/keyless/realcad/` is test-only material: it describes, and
its scripts rebuild, a real watchmaker's keyless works. A real design would hand the agent the
answer, so this folder must never be copied into a task image. `build_task.py` already refuses it
(`NEVER_IN_IMAGE` lists `realcad`), and `.harborignore` here excludes everything. No CAD file, STL
or converted part is in the repository. The downloads and conversions live only in the scratch
folder of the session that ran them.

Purpose: check that the grader is fair. A real watchmaker's keyless works should pass AT-0 to AT-6,
or fail only for reasons we can name.

## 1. Sources and licences (checked 14 Nov 2026)

| Source | Licence (quoted) | Download without account | Modify / test / redistribute | Keyless works included |
| --- | --- | --- | --- | --- |
| openmovement OM10 | CC BY-SA 3.0 | No, members only | Yes, under CC BY-SA 3.0 (share-alike, attribution) | Very likely (complete manual-wind movement, STEP), not verified |
| Marco Lang, ml01 (Zweigesicht-1) | No licence stated | Yes | Testing locally: yes (shared openly for use). Redistribution: not granted | Yes, complete |
| Dom's Sidequest open-source automatic watch (Gumroad) | CC BY-SA 4.0 | No: a $0 Gumroad checkout asks for an email | Yes, under CC BY-SA 4.0 (except the third-party shapes in `05-MISC`) | Probably not (off-the-shelf movement, see below) |
| Printables, Thingiverse, MakerWorld, GitHub searches | n/a | n/a | n/a | None found: printable cases for commercial movements and printable clocks only |

### openmovement OM10

- Site: https://openmovement.org/ says "This is the first open source mechanical Swiss watch movement
  in the world that you can download for free."
- Licence, from https://openmovement.org/general-conditions/: "All published plans are licensed
  under Creative Commons Attribution-ShareAlike 3.0 Unported (CC BY-SA 3.0)." The same page adds:
  - "2D and 3D data may be commercially traded by OM and are subject to purchase terms."
  - "Whoever uses OM's plans for the manufacture of a movement undertakes to mark the movement with
    the OM calibre number and to engrave his movement visibly with his own name or company
    (signature/stamp)."
  - "OM can adapt the general conditions, privacy terms, the disclaimer and the license conditions
    at any time."
- The Open Hardware Observatory lists it under "License: CC BY-SA 3.0":
  https://en.oho.wiki/wiki/Basiswerk_OM_10_clockwork.
- Download: https://openmovement.org/member-download/ says "The downloads are only accessible for
  members." Files listed there:
  - `om10-00001_20220701_va_01_3.stp` (OM10 manual winding, version A 01.3);
  - `om10-00001_20220701_vb_01_3.stp` (version B);
  - `01-3-aut-beta-3d-step-file-va-22-05-2023.stp` (automatic, beta);
  - `om10_movement_holder_v5.zip`.
- Hackaday (https://hackaday.com/2025/06/03/open-source-watch-movement-really-ticks-all-the-boxes)
  confirms "Openmovement has already released STEP files of OM10 ... (You do need to sign up to
  download, however.)" It does not mention GrabCAD. No GrabCAD copy of OM10 was found.
- **Not downloaded: it needs an account.** This is the best-licensed candidate: CC BY-SA allows
  redistribution with attribution. **User action:** register at openmovement.org, download
  `om10-00001_20220701_va_01_3.stp`, and drop it in the scratch folder. The pipeline here
  (`extract_step.py`, then a converter like `convert_ml01.py`) applies to it unchanged, apart from the
  part list.

### Marco Lang (Dresden): ml01 movement of the Zweigesicht-1

- Article: https://watchesbysjx.com/2023/09/marco-lang-open-source-movement.html ("unrestricted
  access to all the construction data related to every component").
- CAD page: https://www.marcolangwatches.com/de/cad/ (English: /en/cad/). The only terms on it are:
  - "…Open Source Konstruktionen… als Hilfestellung für zukünftige Generationen zur Pflege und
    Revision meiner Uhren und als Inspiration für junge kreative Uhrmacher";
  - "Diese (Kopf) Arbeit möchte ich gern offen und kostenfrei mit allen Uhrenliebhabern und Fans
    feiner Mechanik teilen." (He wants to share this work openly and free of charge with watch
    lovers and fans of fine mechanics.)
  - "Es besteht also keine Garantie oder Gewähr auf hundertprozentige Richtigkeit aller Daten."
    (No guarantee that all the data is correct.)
- **There is no licence text** (no CC, no redistribution grant). Under German copyright law that
  means all rights are reserved, apart from the use he invites: download, study and inspiration.
  Testing the files privately is within that. **Redistribution in a public repository is not
  allowed.** So we commit only our scripts and results, never the STEP, the STL or the derived parts.
- Download, no account needed: https://www.marcolangwatches.com/cad/001-ml01-werk-montiert-einbaufertig/
  ("001 ml01 Werk montiert einbaufertig", 57.13 MB package: jpg, stp, stl). The STEP file is
  `001 ml01 Werk montiert einbaufertig.stp`, 19,007,949 bytes, sha256
  `34f001d6f98eeab4b9aacea1f0a47e145666c00a3549364959dbdf33d1f75991`. It was fetched with the
  curlimages/curl container from `...?wpdmdl=1998&ind=1690622339023` (Content-Disposition confirms
  the `.stp` name). The STEP header gives author 'Marco Lang', Solid Edge, 2023-06-12.
- It holds the complete movement (222 solids). Keyless works:

  | CAD name | Part |
  | --- | --- |
  | Aufzugwelle | stem |
  | Kupplungstrieb | sliding pinion |
  | Kupplungsrad z17 | winding pinion |
  | Kronrad z45 | crown wheel |
  | Sperrklinke | click |
  | Sperrfeder | click spring |
  | Winkelhebel | setting lever |
  | Winkelhebelfeder | setting-lever jumper and yoke spring, one flexure |
  | Kupplungshebel | yoke |
  | Zeigerstellrad z19 | setting wheel |
  | Zeigerstellhebel | setting-wheel lever |
  | Zeigerstellungsfeder | its spring |
  | Wechselrad 1 | minute wheel |
  | Aufzugsbrücke | keyless bridge |
  | Kronradplatte | crown-wheel bearing plate |

  There is no crown in the file.

### Dom's Sidequest "Open source automatic watch: CAD, drawings and sourcing"

- https://domsidequest.gumroad.com/l/etynz: the offer is listed at price 0.0 USD. Its terms: "License
  CC BY-SA 4.0. ... Use it, modify it, sell what you make from it, including commercially. Two
  conditions: credit me, and release modified design files under the same license. My design files
  only. Not the third party reference shapes in 05-MISC, which I did not design and cannot license to
  you."
- Contents: "STEP files, ... technical drawings, 3MF ..., BOM for off-the-shelf parts". Its "third
  party reference shapes" folder, and "a mechanical watch I built from scratch" with a BOM of
  off-the-shelf parts, point to a bought automatic movement. The author's own files would then be the
  case, dial and hands, and the keyless works would not be his. Not verified.
- **Not downloaded:** a Gumroad $0 checkout asks for an email address, and we never give one.
  **User action, if wanted:** get it from Gumroad and check whether `05-MISC` holds the movement.
  Even if it does, those shapes are excluded from the licence.

### Others

Searches of Printables, Thingiverse, MakerWorld, GitHub and Onshape turned up printable cases for
ETA 6497/6498 or Miyota/Seiko movements, and printable desk clocks. None had openly licensed watch
keyless works with a crown, sliding pinion and setting. Not found: an Onshape public document with
real keyless works.

## 2. What was tested: ml01 keyless works through the unchanged grader

### Pipeline (all in Docker, `keyless-grade` image, at most 3 GB; scratch folder only)

1. `extract_step.py STEP OUT`: reads the STEP with XCAF and writes every leaf solid as BREP, plus
   `solids.json` (name, instance path, bounding box, volume). 223 solids. The sliding pinion
   (Kupplungstrieb) arrives as an open shell after STEP healing fails ("FixShape ... zero norm"). It is
   sewn and made a solid; the resulting mesh has 8 open edges, which `convert_ml01.py` closes by fanning
   the boundary loops.
2. `convert_ml01.py EXTRACT OUT`: tessellates each solid (linear tolerance 0.003 mm, angular 0.15 rad)
   and moves everything +1.9 mm in z, so that the CAD stem axis (y = 0, z = -1.9, crown at +x) lies on
   the grader's x axis. It then writes the submission and the supplied parts:

   | Mobile | Kind | CAD parts | Axis (grader frame) |
   | --- | --- | --- | --- |
   | stem | stem | Aufzugwelle | x axis |
   | sliding_pinion | spring, slide on stem, rest +1 | Kupplungstrieb | x |
   | winding_pinion | free rot | Kupplungsrad z17 | x axis |
   | crown_wheel | free rot | Kronrad z45 | z through (10.916, 0) |
   | click | spring rot, rest -1 | Sperrklinke | z through (13.737, -3.70) |
   | setting_lever | free rot | Winkelhebel + its pin + setting-lever screw | z through (15.75, 1.95) |
   | yoke | spring rot, rest -1 | Kupplungshebel + its screw + the stop-plate pin | z through (10.0, -11.0) |
   | setting_wheel_lever | spring rot, rest -1 | Zeigerstellhebel | z through (9.40, -7.19) |
   | setting_wheel | free rot, **carried by setting_wheel_lever** | Zeigerstellrad z19 + arbor | z through (9.58, 0) |
   | barrel | barrel | Federhaustrommel I (drum, z80) | z through (6.2, 8.1) |

   - **Supplied parts:**
     - `main_plate` = Grundplatine;
     - `dial_plate` = keyless bridge + crown-wheel plate + barrel bridge, with their pins;
     - `barrel_arbor` = barrel cover (Federhausdeckel), which turns with the drum;
     - `minute_wheel` = Wechselrad 1 with its pinion;
     - `minute_post` = its screw.
   - **Fixed:** 20 screws and pins in the keyless area.
   - **Left out:**
     - the three flexure springs (click spring, the Winkelhebelfeder jumper and yoke spring, the
       setting-wheel-lever spring), declared instead as `spring` mobiles;
     - the going train, barrel II, the balance-stop spring and the second dial's motion work.
3. `phase_ml01.py SUB DATA SUB_PH DATA_PH crown_wheel=3`: the STEP shows the wheels unphased, tooth
   through tooth. Without phasing, the as-submitted overlaps are crown wheel/barrel 0.040 mm³ and
   winding pinion/crown wheel 0.0094 mm³, so AT-0 Rest fails. The script turns the crown wheel 3°,
   lets the rig settle and the springs relax, and writes the parts at those poses. Applied:

   | Mobile | Applied |
   | --- | --- |
   | crown_wheel | 3.0° |
   | barrel | -0.07° |
   | click | 7.5° |
   | yoke | -4.06° |
   | setting_wheel_lever | -0.63° |
   | sliding_pinion | +0.770 mm |

   The CAD has the stem pushed in but the sliding pinion 0.6 mm away from the winding pinion: the
   assembly is not kinematically consistent. With the springs relaxed, the sliding pinion seats in the
   winding pinion's Breguet teeth, which is position 1 as a watchmaker would deliver it.
4. `grade_real.py SUB_PH DATA_PH --details OUT.json`: imports `grade.py` and `engine.py` unchanged
   and runs `grade.grade()` with the overrides below.
   - **Constants:**
     - case: centre (0, 0), radius 17.0 (the plate is 16.98), z ±4;
     - BARREL_AXIS (6.2, 8.1);
     - MINUTE_AXIS (4.2429, 0.246);
     - WIND_SENSE +1;
     - optionally PULL.
   - **The `carrier` extension:** `RealWorld` generalises the engine's "a carrier answers for its
     riders" rule (`pen`, `budget`) from the stem to any carrier.

### Adjustments made to the CAD, and why (each one is a finding about the simulator)

1. **Bore clearance (4 µm radial).** CAD fits are line-to-line. Tessellated, a shaft in a bore of the
   same nominal radius overlaps by the chord sag (crown wheel on its plate: 0.0012 mm³, above the
   2e-4 mm³ touching tolerance), so the wheel can never turn. `convert_ml01.py` widens each mobile's
   own pivot bore by 4 µm (real watch bearings run 5 to 15 µm). Affected: winding pinion, crown wheel,
   click, yoke, setting-wheel lever, and the setting-wheel bore in its lever.
2. **Endshake (5 µm).** The winding pinion's face is coplanar with the stem shoulder. That gives
   1.3e-4 mm³ of overlap: inside the touching tolerance TOL = 2e-4, but above the 0.5·TOL that
   `engine.push` must reach. A body resting at that overlap can never be pushed, so the first winding
   step jammed. Moving the pinion 5 µm along x fixed it, and the crown then winds. **Engine
   inconsistency:** "touching" is ≤ TOL, but a pushed body must clear to ≤ TOL/2, and it cannot do that
   while it still touches something else that is not moving.
3. **Phasing** (step 3 above). Real CAD assemblies are rarely phased. The brief's AT-0 Rest check
   counts as-submitted tooth overlap as a failure.
4. **Pose: position 1.** The CAD stem is pushed in, but the yoke, sliding pinion and setting-wheel
   lever are drawn in their setting positions. The springs were relaxed to put them in position 1.
5. **Springs.** The real springs are flexures (click spring, the Winkelhebelfeder jumper/yoke spring,
   Zeigerstellungsfeder). They were removed and their parts declared `spring` mobiles.
   - **The yoke spring acts on the sliding pinion through the yoke.** The rig's springs never push
     other parts, so this cannot be declared. The sliding pinion was declared sprung as well; the two
     then follow each other back, one contact at a time. That adds a spring the real watch does not
     have.
   - **The jumper sets the two stem positions,** and the format has no detent. Position 2 is the
     brief's 0.9 mm. ml01's own is about 0.49 mm: its second jumper notch is a lever turn of about 14°
     (`--pull` overrides it).
6. **A wheel on a swinging lever** (setting wheel on the Zeigerstellhebel) needs a carrier other
   than the stem. The public `keyless.json` cannot express it. `grade_real.py` adds `"carrier"` and
   generalises the engine's stem-only carrier rule.
7. **Winding sense.** The click locks the drum's negative rotation about +z (grader frame) and lets
   crown wheel and drum wind positive, so WIND_SENSE = +1. That was checked by tracing:
   - with +1, the mainspring's back-turn pulls the click into the teeth;
   - with -1, it lifts the click.

## 3. Results (staged run, 14 Nov, one process, 3,530 s; `results_ml01.json`)

Command (Docker, keyless-grade, `--memory 3g`):
`python -I realcad/grade_real.py SUB_PH DATA_PH --staged --details staged_ml01.json --wind-sense 1`
(PULL = the brief's 0.9). `--staged` runs the same `grade.load`, `bounds_check`, `held_check` and
`grade.worker` phases as `grade.grade()`, one after another. The `grade.py` used is the copy on disk
at run time, which includes the new AT-2 drift rule (HELD_DRIFT).

| Step | Result | Numbers | Reason |
| --- | --- | --- | --- |
| AT-0 Assemble | **fail** | Rest ok (max overlap 1e-4); bounds ok (stem protrudes 5.75); Held fails for yoke and setting_wheel_lever: shifted 0.3 mm in +z they hit nothing | Simulator/format: in ml01 these two levers are held down by the flexure springs' plates (Winkelhebelfeder, Zeigerstellungsfeder) and the dial, which had to be removed to declare the springs |
| AT-1 Wind | **pass** | not blocked; 4.87 crown turns per barrel turn (band 3 to 12); minute wheel 0.0° | Real design works. The CAD ratio is 80/17 × (45/45) = 4.71; the extra comes from backlash and run-back while winding |
| AT-2 Hold | **fail** | run-back 7.4° (≤ 30 ok), crown spun back 21°, but still drifting 1.85° over the last 10 steps (> HELD_DRIFT 0.3) | Probably the simulator: the click works on the crown wheel's ordinary gear teeth, and the engine judges lock only by the friction cone, not by the moment about the click pivot, so the mainspring keeps easing the click deeper. Not proven: a longer hold was not run |
| AT-3 Run | **fail** | reserve 47.8 h (≥ 38 ok), barrel free to run (0 blocked), still coupled (+6.3°) | Fails only because AT-3 repeats AT-2's drift condition |
| AT-4 Backward | **fail** | 111 of 120 steps blocked; arbor -4.8° | Simulator: the Breguet teeth must push the sliding pinion back against the yoke spring, through the yoke. With both declared as springs, the sprung sliding pinion cannot yield while the sprung yoke holds its groove, so the backward turn drags the winding train back until the click stops it. A traced single step shows exactly this (winding pinion, crown wheel and barrel pushed back) |
| AT-5 Set | **fail** | position-1 test turns clean (wind 5.1°, no setting); pull blocked at p = 0.12 mm | Simulator: setting lever → yoke (spring) → sliding pinion (spring) cannot be resolved; residual overlap setting_lever/yoke 0.0053 mm³. The same block at μ = 0.15, so it is not friction. Engine detail: on a pure pull step (dp only), `resolve` counts a body carried by the stem as "moved" (`any(dqs[carrier])`), although a carried body does not follow the stem's slide; the sliding pinion then becomes a "pusher" the yoke must clear, which it cannot |
| AT-6 Return | **fail** | could not reach position 2 | Same as AT-5 |

Product score on the brief's weights: 0.10 (AT-1 only).

## 4. Fairness verdict

**The grader cannot pass a real watchmaker's keyless works today, and the failures are the
simulator's, not the design's.**

- **What works:** where the real mechanism is in the engine's vocabulary, it passes, and its numbers
  match the drawing. AT-1 Wind passes without a block (4.87 turns per barrel turn against the drawn
  4.71), the reserve is 47.8 h, the barrel runs free, and winding re-couples after the hold.
- **What fails:** every other step fails at a point where ml01 uses something the rig cannot
  represent. None of these failures points to a fault in Lang's design: the movement was built and
  sold, and these are its standard mechanisms.
  - **Flexure springs:** each spring has to become a declared `spring` mobile, so the flexure is lost
    as a hold-down plate (AT-0 Held).
  - **A spring acting through a linkage:** the yoke spring returns the sliding pinion through the
    yoke (AT-4, AT-5, AT-6).
  - **A wheel on a swinging lever:** this needed a format extension.
  - **A click on gear teeth:** the click's hold depends on its moment, not on friction (AT-2,
    probable).
- **What it means for the agent:** our reference passes because it avoids every one of these real
  features. It has no yoke, no setting lever, a sprung sliding pinion pulled by the stem shoulder,
  and a setting wheel permanently in mesh. So the brief rewards a simplified mechanism the rig can
  simulate, and penalises textbook keyless works. That is worth saying in the brief, or fixing (next
  section).

### Simulator limitations found, and what would fix them (no file outside realcad/ was changed)

1. **Springs cannot push through a link.** In `engine.resolve`, a spring "never pushes" and yields only
   if it clears every contact. Fix options:
   - let a spring mobile push free and spring bodies on its rest side (a force, not just a stop);
   - or allow `rest` on a free mobile that is linked to a spring.
2. **Pure-slide steps treat carried bodies as moved** (`movers_now` uses `any(dqs[carrier])`). It
   should use only the carrier's rotation, `dqs[carrier][0]`.
3. **Touching vs pushable.** Touching is ≤ TOL, but `push` targets ≤ 0.5·TOL, so a body resting
   between the two can never be pushed. Either measure the residual only against the pushers, or use
   one threshold.
4. **Line-to-line CAD fits** overlap after tessellation. The rig needs a stated clearance rule (or
   tolerance), or real CAD will always need 4 to 5 µm of hand clearance.
5. **AT-0 Rest on unphased gears.** Real assemblies are unphased; the rig's own settle could phase
   them before the Rest check, as it already does before the sequence.
6. **No carrier other than the stem** in `keyless.json` (`grade_real.py` shows a two-method extension
   that works).
7. **No detent:** position 2 is fixed at 0.9 mm; ml01's own pull is about 0.49 mm. Not the cause of
   any failure here (the pull blocked at 0.12).
8. **Click lock by moment (probable):** the friction-cone rule judges a click by the slope of the
   contact face, not by whether the reaction pulls the click in. Not proven; a longer hold or a
   moment-based test would settle it.
9. **Speed:** with real meshes (crown wheel 193k triangles, sliding pinion 101k), the full run takes
   59 minutes in one process (AT-1 alone 30 minutes). The two-worker run hit the 3 GB cap.

## 5. Reproduce (Docker only; scratch paths; nothing is written in the repo)

```
curl (curlimages/curl) -> ml01_werk.stp   (sha256 34f001d6f98eeab4b9aacea1f0a47e145666c00a3549364959dbdf33d1f75991)
python -I realcad/extract_step.py ml01_werk.stp EXT
python -I realcad/convert_ml01.py EXT CONV
python -I realcad/phase_ml01.py CONV/sub CONV/data CONV/sub_ph CONV/data_ph crown_wheel=3
python -I realcad/grade_real.py CONV/sub_ph CONV/data_ph --probe
python -I realcad/grade_real.py CONV/sub_ph CONV/data_ph --staged --details OUT.json --wind-sense 1 [--pull 0.49]
```

Not done: OM10 (needs an account); a run with `--pull 0.49` (it would not change the AT-5 block at
0.12 mm); a longer AT-2 hold to tell a slow lock from no lock.
