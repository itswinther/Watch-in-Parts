# Real watchmaking work compared with our task

Research only, 14 Nov 2026, for workstream B. Nothing in the task, the grader or the reference was changed.
This file says what real calibres, real service documents and one real professional CAD model show about our
going train, our 24-hour drive, our 6-hour variant, our assembly part and our gear-strength check. Every number
has a source or is marked *derived* (our arithmetic on sourced numbers) or "not found".

**How to read the sources.**

- **P** means primary: a manufacturer document, a patent, a textbook or a CAD file we opened ourselves.
- **S** means secondary: a forum post, an article or a hobbyist's measurement.
- **[snippet]** means the page itself could not be opened from this container, and the fact comes from a
  search engine's extract of that page. A human should open the page before the fact is quoted to a judge.
  The list of blocked hosts is in section 10.
- The public-domain books are the copies already in `spikes/keyless/datasheets/public_domain/`. Line numbers
  refer to those text files.

**Licences.** No third-party file is in the repository. The ml01 STEP (no licence stated; local testing only) and
one patent PDF (US public domain) were downloaded into the session scratchpad only. Manufacturer documents are
copyrighted; only facts are cited here.

## 1. Real going trains

Teeth are given as wheel / pinion. "h per barrel turn" is barrel teeth divided by centre-pinion leaves, which
holds when the barrel drives the centre pinion directly or through an idler.

| Calibre or source | Barrel | Centre | Third | Fourth (seconds) | Escape | h per barrel turn | vph | Modules, centre distances | Source | P/S |
|---|---|---|---|---|---|---|---|---|---|---|
| Grossmann, *Lessons in Horology* (1905), example | 80 | 80 / 10 | 75 / 10 | (60 turns per centre turn) | not given | 8 | 18,000 (worked example) | not given | `grossmann_lessons_1905_djvu.txt` l. 4560 (barrel 80 to centre pinion 10), l. 5855-5870 (80/10, 75/10 gives 60) | P |
| Saunier, *Treatise* (1887): 40 mm calliper | in fig. 33, not in the text | diameter 13.50 mm | 10.70 mm | 9.96 mm | 8.25 mm | not given | 18,000 is "the most frequent case" (l. 15052-15067) | wheel and pinion diameters, l. 15430-15450 | `saunier_treatise_1887_djvu.txt` p. 243 | P |
| ETA/Unitas 6498-1 | 88 | 80 / 12 | 60 / 10 | 70 / 8 *(8 derived from 60 turns/h)* | 15 / 7 | 7.33 *(derived)* | 18,000 *(derived: 70/7 x 30 = 300 per min)* | barrel m 0.191 (tip diameter 17.3); escape pinion m about 0.111; cannon 12 at m 0.224; hour wheel 40 at m 0.204 | watchmaking.io/2022/02/2-taking-measurements-6498-calibre.html, measurement table [snippet]; fourth 70, escape 15/7: watchrepairtalk.com/topic/15688 [snippet] | S (hobbyist's measurement) |
| Unitas 6497 (21,600 vph version) | not found | 80 / not found | 60 / 10 | 120 / 8 | 15 / 10 | not found | 21,600 *(derived: 120/10 x 30 = 360 per min)* | not found | horology-student.org/movements/modern-eta-and-clones/unitas-eta-6497-6498/ [snippet] | S |
| Abbey Clock, "Chapter VI: The Train" (textbook example) | 90 | 80 / 12 | 75 / 10 | 75 / 10 | 16 / 8 | 7.5 *(derived)* | 18,000 *(derived)* | not given; rule: centre pinion at least 12 leaves, third and fourth 10, escape at least 7 | abbeyclock.com/gbk/gbk6.html [snippet] | S |
| K. Eisenegger, *Uhrenkonstruktion* v5.2 (2011) | 90 | 80 / 12 | 75 / 10 | 70 / 10 | not given | 7.5 | not given | barrel-to-pinion ratio "usually about 5 to 10"; companion example barrel 95 to pinion 15 at m 0.124 or 0.135 | watchmaking.com/index_htm_files/Uhrenkonstruktion52-Probe.pdf [snippet] | S (a design textbook) |
| H. Mann, *Porträt einer Taschenuhr*, Kaliber 972 | 90 (tip diameter 17.42) | 80 (tip 11.63) / 12 (tip 2.55) | not found | not found | not found | 7.5 | not found | barrel to centre pinion: m 0.1875, centre distance 9.56 (0.1875 x 102/2 = 9.5625, *derived*) | flume.de/media/a9/80/9a/1599051556/pimFile_0000004393.pdf, "Verzahnungstabelle Räderwerk" [snippet] | S |
| **Marco Lang ml01** (2023, Solid Edge CAD, measured by us) | 80 (barrel II), then an intermediate wheel 26 | 64 / 12 | 75 / 10 | 81 / 8 (central seconds) | 20 / 9 | 6.67 *(derived: 80/12)* | 21,600 *(derived: 9 turns per min x 20 x 2)* | m 0.15, 0.15, 0.13, 0.116, 0.102; centre distances 7.95, 2.85, 4.81, 4.81, 4.59 mm | CAD solid names and slices, section 5 | P (CAD file) |
| ETA 2824-2 | not found | no centre wheel at the centre: the barrel drives an off-centre second wheel | not found | the fourth wheel is at the centre and carries the seconds hand | 20 | not found | 28,800 | not found | 17jewels.info/movements/e/eta/eta-2824-2/; watchrepairtalk.com/topic/28427 [snippet] | S |
| ETA 2836-2, 2893-2, SW200-1, ST36, Miyota 8215, Seiko 6R15/NH35, Peseux 7001, Valjoux 7750, OM10 | not found | | | | | | | | the parts lists we could see give part numbers only, not tooth counts | |

Not to be used: firgelliauto.com/blogs/mechanisms/watch-train gives a "2824-2" train (barrel 96; wheels 80, 75,
70; pinions 8, 10, 10, 7) whose own numbers give 18,000 vph, not 28,800. The page looks machine-written.

**General rules, with sources.**

- The centre wheel turns once an hour and carries the minute hand. The fourth wheel turns once a minute and
  carries the seconds hand. Sources: Grossmann l. 5866-5872 (P); Saunier, *Treatise*, l. 15052-15054 (P).
- A watch barrel "usually" turns once every 8 h. Source: Wikipedia, "Barrel (horology)", citing Hood, *Modern
  Methods in Horology* (1904), p. 44 [snippet]. Also DS-101 footnote `[^wiki]`.
- Real ratios run from 6.33 to 8 h per barrel turn (above). Our 8 h (class D) and 6 h (class B) are both inside
  that range.
- The barrel drives the centre pinion directly in most calibres: Grossmann l. 4560 (P); Wikipedia, "Wheel train"
  [snippet]. Seen from the back of the watch, a going barrel turns clockwise, so it turns counter-clockwise seen
  from the dial [snippet; the attribution, timezonewatchschool.com glossary or pocketwatchrepair.com, is unclear].
- **Exceptions with an extra wheel between barrel and centre** (our layout):
  - ml01 puts an intermediate wheel of 26 teeth between barrel II and the centre pinion (P, measured). Its barrel
    therefore turns the same way as the minute hand, as our DS-W01 class D barrel does.
  - US 7,452,123 B2 (Richemont, 2008) has coaxial barrels in series feeding the centre pinion through an extra
    wheel (P, read by us: col. 3-4, items 18, 20, 22, 28, 30a, 32d, 46, 48).
  - We found no single-barrel wristwatch calibre with an idler between the barrel and the centre wheel.
  - In the "indirect minute" calibres (ETA 2824-2, Valjoux 7750), the barrel to minute hand path has an odd
    number of meshes, so the barrel still turns against the minute hand (*derived*, from the layouts cited above).
- **Strength in tooth counts.** Saunier says to use a 12-leaf pinion where "solidity is necessary, as in the centre
  wheel"; a 10-leaf pinion's leaves are "of necessity very thin". Source: Saunier, *Treatise*, art. 1136-1142 (P).

## 2. Real 24-hour (GMT) motion work

| Calibre or source | Where the 24-hour wheel sits and what drives it | Tooth counts | Source | P/S |
|---|---|---|---|---|
| Grossmann (1905) §151-152 | §151: a 24-hour dial on its own: cannon 12, minute wheel 48, minute pinion 10, hour wheel 60. §152: a 12-hour and a 24-hour hand together. A second pinion of 6 leaves is fixed on the minute-wheel pinion and drives a second hour wheel of 48 teeth, which turns loose on the first hour wheel. | 12 / 36, 10 / 40 for 12 h; 12 / 36, 6 / 48 for 24 h (36/12 x 48/6 = 24) | `grossmann_lessons_1905_djvu.txt` l. 7000-7075 (book p. 95-97) | P |
| ETA 2893-2 | A double-toothed hour wheel. The 24-hour wheel ("universal hour indicator", item 43) is driven through an "hour indicator driving wheel" (item 45) from one of the two toothings. Crown position 2 sets the 24-hour hand. | not found | ETA Technical Communication CT 2893-2 (shopb2b.eta.ch/technicaldocuments/index/pdf/id/1905) [snippet]; watchrepairtalk.com/topic/20003 [snippet] | P / S |
| Miyota 9075 | The 24-hour wheel is at the centre beside the hour wheel, driven by a small intermediate wheel from the hour wheel's lower toothing. The hour wheel has its own jumper, for the jumping local hour. | not found | watch-movements.eu/blog/en/2023/01/29/the-miyota-9075-with-true-gmt-function/; monochrome-watches.com, 9075 deconstruction [snippet] | S |
| Sellita SW330-1 to SW330-2 | The double-toothed hour wheel became single-toothed; the "24-hour wheel" became the "GMT wheel". | not found | calibercorner.com/sellita-caliber-sw330-2 [snippet] | S |
| Rolex 3285 / 3186 | Jumping local hour hand: a four-toothed star wheel and a patented jumper spring. | not found | rolex.com, "Second Time Zone Function" [snippet] | P [snippet] |
| US 9,778,621 B2 (Longines) | An intermediate wheel turning once in 12 h meshes with the 24-hour wheel, so the ratio is 2:1 *(derived)*. | not found | Google Patents [snippet] | P [snippet] |
| US 3,503,203 | A second hour hand driven by a train from the minute shaft, once per 24 h. | not found | Google Patents [snippet] | P [snippet] |
| ml01 | No 24-hour hand. Its second dial (hours and minutes on the back) is driven from minute wheel 1 (36) to a transfer wheel 36, then 24 to cannon 8 and 8 to hour wheel 32. | as given | CAD, section 5 | P |

All of these drive the 24-hour hand from the motion work, off the hour wheel or the minute wheel, on the dial
side.

## 3. Real calibre variants on one frame

All entries are from search extracts of the documents named [snippet]. Part numbers are ETA's 13-digit
numbers.

| Pair | What changed | What was kept | Source | P/S |
|---|---|---|---|---|
| ETA 6497-1 vs 6498-1 (small seconds at 9 vs 6) | The third wheel (7613226028913 vs 7613226007574); the seconds wheel is listed as "Var". In the 6497 the seconds wheel sits above the third wheel, in the 6498 below it. One secondary source adds the main plate, barrel bridge, winding stem and setting lever; a vendor list instead shows barrel bridge 105 shared, so **the sources conflict** on the plate and bridge. | The centre wheel (7613226033887) and escape wheel (7613226056374) have the same numbers in both | ETA CT 6497-1 (28.11.2016) and CT 6498-1 (05.12.2016), mirrored at patrimoine.bourgognefranchecomte.fr/documents/ETA_6497-1.pdf and ETA_6498-1.pdf; calibercorner.com/eta-unitas-caliber-6497-vs-6498/ | P / S |
| ETA 6497-1 vs 6497-2 (18,000 vs 21,600 vph) | The centre (7613226033887 to 7613226021808), third (7613226028913 to 7613226045484) and escape wheels (7613226056374 to 7613226044357) | Calibre size (16½‴) and layout; a shared plate is not confirmed | ETA CT 6497-1; CT 6497-2 (31.05.2017), same mirror | P |
| ETA 6498-1 vs 6498-2 | The escape wheel and the third wheel. The 6498-2 CT records a revision of its own **order of assembly**. | Diameter 36.60 mm, height 4.50 mm, 17 jewels | ETA CT 6498-2 (07.02.2018), same mirror, `/gtrudov/documents/ETA_6498-2.pdf` | P |
| Sellita SW200 to SW200-1 | A new, stronger tooth profile on three automatic-winding parts (1481, 1482, 415), replaced as a set | "All other components remain interchangeable" | Sellita Information Sheet IS 05, "Evolution calibre SW200 vers SW200-1" | P |
| Sellita SW200-1 to SW200-2 | Fitted main plate, shock settings, balance bridge shape and regulator | Dimensions and casing | Sellita IS 33 | P |
| ETA 2824-2 / 2834-2 / 2836-2 | Day-date added on the dial side (height 4.6 to 5.05 mm) | Barrel bridge, centre wheel, third wheel shared in vendor lists | emmywatch.com movement pages; Cousins interchangeability list `29_ETA2801.2-ETA2836.2.pdf` (not opened) | S |
| ETA 2892-A2 to 2893-2 / 2895-2 / 2897 | Modules added: GMT, small seconds, power reserve | The 2892-A2 base at 28,800 vph; which wheels change was not found | Wikipedia, "List of ETA movements" [snippet] | S |
| Valjoux 7750 vs 7753, Miyota 8215 / 821A / 8205, Seiko 7S26 / 4R36, Peseux 7001 | Dial-side or keyless additions; wheel changes not found | — | boley.de, Caliber Corner, Miyota spec sheet [snippet] | S |

**Against our 6-hour variant.** Ours keeps the frame and changes one gear pair: the third wheel and centre
pinion go from 60/30 to 54/36 at the same centre distance. That matches the 6497-1 to 6498-1 pattern: one frame
family, centre and escape wheels kept, the third and seconds wheels changed. A real rate change (6497-1 to -2)
touched three wheels. Real makers record what was kept by part number in the parts list and announce a change in
a dated information sheet (Sellita IS 05, IS 33) or a CT revision table.

## 4. Real assembly sequences

**Unitas/ETA 6497.** Source: archive.horlogerie-suisse.com/Theoriehorlogerie/reassembling-mechanical-watch.html
[snippet] (S, educational).

| Step | Part | Side and direction | Constraint |
|---|---|---|---|
| 1 | Sliding pinion and winding pinion on the stem | Dial side; the stem goes in **radially, through the edge of the plate** | — |
| 2-4 | Setting lever, yoke, setting-lever spring, setting wheels, minute wheel | Dial side | The setting lever's peg must engage the stem's slot |
| 5 | Barrel, centre wheel, barrel bridge | Bridge side, plate turned over | The centre wheel goes in **before** the barrel bridge, which covers it |
| 6 | Crown wheel, click, ratchet | On top of the barrel bridge | Needs the barrel bridge in place |
| 7 | Third, seconds and escape wheels | Bridge side | — |
| 8 | Train bridge | Lowered over **three pivots at once**, each coaxed into its jewel before the screws go in | Source for the pivot handling: caseandcaliber.com/eta-6497-mod-homage/ [snippet] |
| 9-10 | Pallets and pallet bridge; dial-side shock setting; balance and cock | Both sides | — |

**Seiko 7S26.** Source: clockmaker.com.au/diy_seiko_7s26/, chapters 9-14 [snippet] (S, a working watchmaker).

- The stem goes in radially and the yoke is laid in without tension.
- On the bridge side: the barrel, then the third, escape and fourth wheels.
- The train bridge is lowered over three pivots, guided in the order fourth, third, escape. Start at the alignment
  pin, with "virtually no pressure".

**Other sources.**

- ETA 2892-A2 CT (cousinsuk.com, rev. 20.12.2016, P [snippet]) orders the chapters as hand-setting, base and
  train, automatic, calendar. A WatchRepairTalk thread (topic 25027 [snippet]) says the barrel bridge must in fact
  go in before the keyless works.
- A Seiko NH36 build fits a combined barrel and train bridge last (watchrepairtalk.com/topic/1635 [snippet]).
- Sellita SW200-1 DocTec v07 covers assembly on pp. 10-19 (P [snippet]); the steps themselves were not readable.

**Against our Part 4.**

- **Real:** wheels first, then a bridge over them; order constraints exist, such as the centre wheel before the
  barrel bridge. **Ours:** the same, since every part is tested against those already in.
- **Real:** the plate is turned over, and the keyless works, motion work, dial and hands go in from the dial
  side. **Ours:** every reference part drops from +z. QA-W100 Part 4 allows any rigid path, so two-sided
  assembly is allowed but never needed.
- **Real:** the stem goes in sideways. **Ours:** there is no stem until crown winding (P5).
- **Real:** a bridge is lowered over several pivots at once, each guided by hand. **Ours:** a straight drop with
  0.01 mm³ allowed per pose. This is an idealisation of the hand guiding, not a contradiction of it.
- **Real:** the order is not unique; practitioners deviate from it, and ETA revised the 6498-2 order. **Ours:**
  any order that works is accepted.

**Layout difference a watchmaker would notice.** Our reference stacks, from -z to +z: `main_plate` (z -1.7 to
-0.3), the train, `bridge` (5.0 to 6.0), the motion work (6.4 to 8.4), then the dial (8.8 to 9.6). This is from
`solution/reference_watch.py`, l. 51-52. In a real watch the motion work sits between the main plate and the
dial, and the bridges are on the far side (Grossmann l. 6843-6863, the cannon pinion "under the dial"; the 6497
order above). So our `bridge` does the job of a real main plate and our `main_plate` does the job of the
bridges. Function and the checks are not affected; only the names are.

## 5. Openly available CAD with a real going train

| Source | Licence, verbatim | Script download | Real going train | Fit as a fairness test |
|---|---|---|---|---|
| **Marco Lang, ml01** ("001 ml01 Werk montiert einbaufertig") | None. The page shows only version, size, file types and date. `spikes/keyless/realcad/REAL_CAD.md` §1 has the CAD page's wording ("offen und kostenfrei ... teilen"). | Yes, no account. The URL is in REAL_CAD.md; sha256 34f001d6...1f75991 matched. | **Yes, complete and professional**: 223 solids. | **Best**: local testing only, never committed. |
| openmovement OM10 | "CC BY-SA 3.0" (REAL_CAD.md §1) | No, members only; openmovement.org is also blocked here | Very likely, not verified | Best licence. A human must register and download it. |
| GrabCAD, "ETA 6497-1 complete watch movement" (two uploads: Steen Winther; alexandre.willame-1) | Not checked (needs login; host blocked) | No | One is described as a "cosmetic model" [snippet] | Unknown. Named in the MIT-licensed `github.com/jmogl/ETA-6497_Watch_Movement_Sim` README. |
| Kelsus K1 rev C, github.com/JonChristensen/kelsus-manufacture | README: "CERN-OHL-P v2" for hardware and STEP; MIT for tooling | Yes, `git clone` | Desk-clock scale (diameter 170, module 1.0). Its STEP names and its `revc.py` disagree on tooth counts. Hobby build. | Weak: not professional, and the counts are inconsistent. |
| Laimer tourbillon (thingiverse thing:1249221), kevinbchen/tourbillon-desk-toy, daki0607/Tourbillon (GPL-3.0) | Not found / none / GPL-3.0 | Blocked / yes / yes | No hand train, or not verified | No |
| Dom's Sidequest (Gumroad) | "CC BY-SA 4.0" (REAL_CAD.md) | No, email checkout | Probably a bought movement | No |
| Printables, MakerWorld, Onshape | — | Hosts blocked | Clocks and escapements only [snippet] | No |

### ml01 going train, measured

**How it was read.** The STEP was read with OCP 7.9.3 in a scratch venv. Every tooth count in a CAD name was
checked by slicing the solid every 0.01 mm and counting lobes. The escape wheel's name carries no count, so its
20 teeth were counted the same way. Module is 2 x centre distance / (z1 + z2). Face width is the z range where
the two gears' teeth overlap.

| Mobile | CAD name | Teeth wheel / pinion | Axis x, y (mm) | Centre distance to driver | Module | Face width |
|---|---|---|---|---|---|---|
| Barrel II (drives the train) | Federhaustrommel II z80 m0,15 | 80 | -6.2, 8.1 | — | 0.15 | 0.36 |
| Intermediate | ÜFHMinRad z26 m0,15 | 26 | -2.6791, 0.9722 | 7.950 | 0.150 | 0.50 |
| Centre (minute) | Minutenrad z64 m0,13 / Minutentrieb z12 m0,15 | 64 / 12 | 0, 0 | 2.850 | 0.150 | 0.23 / 0.73 |
| Third | Kleinbodenrad z75 m0,1159 / Kleinbodentrieb z10 m0,13 | 75 / 10 | 3.1705, -3.6172 | 4.810 | 0.130 | 0.20 / 0.72 |
| Fourth = seconds (central seconds, through the hollow centre pinion) | Sekundenrad z81 m0,102 / Sekundentrieb z8 m0,1159 | 81 / 8 | 0, 0 | 4.810 | 0.1159 | 0.20 / 0.43 |
| Escape | Gangrad Niv20.5 / Gangtrieb z9 m0,102 | 20 (counted) / 9 | -1.9999, -4.1314 | 4.590 | 0.102 | 0.09 |
| Motion work | Viertelrohr1 z12 to Wechselrad1 z36 m0,177; Wechseltrieb1 z10 m0,17 to Stundenrad1 z40 m0,17 | 12 / 36, 10 / 40 | minute wheel at 4.2429, 0.246 | 4.250, 4.250 | 0.177, 0.170 | 0.25 |

**Barrels.** Barrel I (z80, at 6.2, 8.1) is coupled in series with barrel II through two ratchets (z62, m 0.20).

**Size and stack.** The main plate has radius 16.98 mm (diameter 33.97). The stack spans z -6.06 to 2.41, with
the plate at -2.0 to 0 and the bridges at -4.4 to -2.0, so +z is the dial side.

**What is not in the file.** No hands, no 24-hour wheel and no materials (no material designation in the STEP).

**Speeds** *(derived from the counts)*. In turns per hour: centre 1, third 32/5, seconds 60, escape 540,
intermediate 6/13, barrel II 3/20 (6.67 h per turn). The barrel and the minute hand turn the same way.

**Tooth form.** The sections are arcs and lines, the arc-approximated horological profile, not involute.

**Our checks run on the parts** (scratch scripts, not the repo's grader):

- Every train part is valid by OpenCASCADE's shape check and has at most one triangular planar face.
- Meshed at 0.001 mm / 0.1 rad, the largest part has 84,440 triangles, under the 200,000 limit.
- **Unphased teeth overlap at rest.** As drawn, five pairs are over the 0.01 mm³ limit:

  | Pair | Overlap (mm³) |
  |---|---|
  | barrel II / intermediate | 0.036 |
  | intermediate / centre pinion | 0.0102 |
  | centre wheel / third pinion | 0.0101 |
  | series ratchets | 0.061 |
  | minute pinion / hour wheel | 0.0155 |

The scripts and outputs are in the session scratchpad (`realcad_train/scripts/`, `realcad_train/out/`); they are
not committed.

## 6. How real watch gears are rated for strength

| Standard or method | What it covers | Used for watches | Source |
|---|---|---|---|
| NIHS 20-02, 20-10, 20-25 (SN 282025), 20-30 | Ogival (arc-approximated cycloidal) profiles: dimensions, layout and calculation; corrected epicycloidal teeth for winding and hand-setting | Yes | standards.globalspec.com/std/9929051; patent EP3244094A1 cites NIHS 20-02 and 20-25 as base profiles [snippet] |
| AFNOR NF S80-525 / 526 / 541 | Horological cycloidal toothing, including barrel-to-centre gears | Yes | boutique.afnor.org [snippet] |
| AFNOR NF S80-566 / 569, NF S80-501 | **Horological involute toothing** (normal and +0.5 m shift) and preferred modules | Yes, as an option | boutique.afnor.org [snippet] |
| DIN 58400 (withdrawn 2016), DIN 58405-1 | Involute rack and design data for fine mechanics, modules about 0.1 to 1 | Fine mechanics | shop.standards.ie, beuth.de [snippet] |
| AGMA 207.06, later ANSI/AGMA 1003 / 1103 | Fine-pitch tooth proportions; 25 degrees "for greater tooth strength" | No | globalspec, ANSI previews [snippet] |
| Lewis bending | Root bending stress | **No horological source found that uses it** | — |
| What horology designs for instead | Efficiency, friction, depthing, polish, tolerance of centre-distance error; leaf count for strength | Yes | Saunier, *Treatise*, art. 1083 (involute is good in principle but impracticable to form and polish), art. 1136-1142 (12-leaf pinion "of sufficient strength") (P); EPFL thesis 6890 (Theurillat-Bonjour 2016, DOI 10.5075/epfl-thesis-6890) [snippet] |

**Real torques.**

| Calibre | Torque at the barrel | Source |
|---|---|---|
| Sellita SW200-1 (automatic, 11½‴) | Half a turn from full wind: max 11.86 N·mm. After 24 h: min 8.83. Bridle slipping: 12.21 to 16.57. | Sellita DocTec SW200-1 rev 04 p. 1, already cited in DS-101 `[^sel]` (copy: watch.co.uk/download/sw200-ml-pdf); rev 05 and 06 [snippet] |
| SW300-1, SW330, SW360-1 | Slipping 7.70 to 10.44 N·mm | Boley and Cousins sheets [snippet] |
| ETA 2824-2 | Spring rated 1300 g·mm (about 12.7 N·mm) | WatchProSite, "WatchTech 101.1 Motive Power" [snippet] (S) |
| 19-ligne (43 mm) pocket watch | 5000 g·mm (about 49 N·mm) fully wound, 3400 g·mm (about 33 N·mm) after 4 turns | Grossmann §82-83, `grossmann_lessons_1905_djvu.txt` l. 2785-2828 (P) |
| Grossmann's worked example (18,000 vph) | F = 4800 g·mm (about 47 N·mm) | Grossmann l. 4553 (P) |
| Saunier's 40 mm calliper | 6.0 / 7.5 / 9.0 g on a 185 mm lever at key turns 1, 2½ and 4: about 10.9 / 13.6 / 16.3 N·mm *(derived; the lever's own 3.88 g moment is left out because its centre of gravity is not stated)* | Saunier, *Treatise*, p. 243, l. 15455-15466 (P) |
| Torque at the centre, third and fourth wheels of a named calibre | not found | — |

**What real damage looks like.** The documented overload is the recoil when a mainspring breaks. It damages the
barrel teeth or the **centre pinion**, which is why the safety pinion exists. Sources: Merritt Burt, US patent
44,161 (1864); Fogg (1865); pocketwatchdatabase.com [snippet]. US 8,079,754 states that the highest meshing stress
in a wristwatch train is at the centre wheel and pinion [snippet]. No published tooth stress in MPa was found.

**Lewis form factors (load at the tip).** Values are full depth.

| Teeth | 20 degrees, published | 25 degrees, published | Ours (DS-W04, 25 degrees) |
|---|---|---|---|
| 12 | 0.245 (gearpy; Shigley per snippet) | 0.277 (DatumMark) | 0.2546 |
| 20 | 0.322 (DatumMark), 0.320 (Viewmold) | 0.369 (DatumMark) | 0.3386 |
| 25 | — | 0.402 (RoyMech; column inferred from a snippet) | 0.3686 |
| 30 to 96 | not found (Shigley Table 14-2 could not be opened) | not found | — |

All published values are [snippet]. Where a 25-degree value was found, ours is 8 to 9 % lower, so our check errs
strict. This agrees with builder S's note in SESSION.md 19:11.

**What follows for check 14.**

- **The load is real and stated.** 70.1 N·mm is the SW200-1's maximum slipping torque scaled by 1.617³:
  16.57 x 4.228 = 70.06 *(derived)*. The work order states it as the load of the automatic member of the family,
  so it is a stated requirement, not one the agent has to infer.
- **A manual train alone** would be rated at full wind: 11.86 N·mm, or 50.1 N·mm at our scale *(derived)*.
  The slipping maximum is 1.40 times that, not 4 to 8 times. The "8.4 N·mm" in A's 21:05 point (1) is spring L's
  *calculated* elastic-limit torque in DS-101 Table 1, not a measured torque.
- **Stalling the train at its end** is a realistic load case: a stopped balance or held hands.
- **Lewis on an involute tooth** is an engineering convention here, not horological practice.
- **Brass wheels on steel pinions.** In real watches "the barrels and wheels are of brass" (Saunier, *Watchmaker's
  Hand Book*, §112, `gutenberg_saunier_76850.txt` l. 5495), and pinions are steel (Saunier, *Treatise*, l. 2183: "a
  brass wheel, when working dry against steel"). FORMAT.md says "every part of a mobile is of its material", so a
  mobile cannot declare a brass wheel on a steel pinion. Our reference declares the whole of every going-train
  mobile as steel (`solution/reference_watch.py` l. 394).

## 7. Our reference against the real calibres

Our reference is at scale s = 1.617. The "1:1" column divides by s. Its source is
`solution/reference_watch.py`: l. 42-52 (modules and layers), l. 224-250 (train), l. 280-297 (24-hour) and
l. 303-320 (variant).

| Mesh in our reference | Teeth | Module, ours / at 1:1 | Centre distance, ours / at 1:1 | Face (layer) | Real counterpart |
|---|---|---|---|---|---|
| barrel to "third" pinion | 96 / 24 | 0.2 / 0.124 | 12.0 / 7.42 | 0.8 (A) | ml01: barrel 80 to intermediate 26, m 0.15, cd 7.95. Most calibres have no such wheel. |
| "third" wheel to centre pinion | 60 / 30 | 0.25 / 0.155 | 11.25 / 6.96 | 0.45 (B) | ml01: intermediate 26 to centre pinion 12, m 0.15 |
| centre wheel to "fourth" pinion | 90 / 12 | 0.212 / 0.131 | 10.8 / 6.68 | 0.6 (C) | real: centre 80 to third pinion 10 (ml01: 64 / 10 at m 0.13) |
| "fourth" wheel to seconds pinion | 96 / 12 | 0.2 / 0.124 | 10.8 / 6.68 | 0.6 (D) | real: third 60-75 to fourth pinion 8-10 (ml01: 75 / 8 at m 0.116) |
| cannon to minute wheel | 12 / 36 | 0.25 / 0.155 | 6.0 / 3.71 | 0.8 (E) | Grossmann 12 / 36 ("very often employed"); ml01 12 / 36 at m 0.177 |
| minute pinion to hour wheel | 12 / 48 | 0.2 / 0.124 | 6.0 / 3.71 | 0.8 (F) | Grossmann and ml01 10 / 40 |
| hour wheel to day idler | 48 / 24 | 0.2 / 0.124 | 7.2 / 4.45 | 0.8 (F) | ETA 2893-2 and Miyota 9075: an intermediate wheel off the hour wheel |
| day idler pinion to 24-hour wheel | 10 / 40 | 0.16 / 0.099 | 4.0 / 2.47 | 1.0 | Grossmann §152: 6 / 48 off the minute wheel; Longines: 2:1 from a 12-hour wheel |
| 6-hour variant: "third" wheel to centre pinion | 54 / 36 | 0.25 / 0.155 | 11.25 / 6.96 | 0.45 | ETA 6497-1 / 6498-1: one pair changed, centre and escape wheels kept |

**What matches.**

- The ratios are real: barrel to centre is 8 (1 turn per 8 h), and centre to seconds is 60, made as 7.5 x 8
  where real trains use 8 x 7.5 or 6.4 x 9.375.
- Barrel speeds of 8 h and 6 h are real.
- Modules at 1:1 (0.099 to 0.155) are inside the real range (0.102 to 0.224, above).
- Pinions are at least 12, which meets Saunier's and Abbey's strength advice.
- The motion work ratio is 12, and the cannon pinion and minute wheel are 12 / 36.
- The 24-hour wheel is driven off the hour wheel through an intermediate wheel, as in the 2893-2 and 9075.
- The variant on one frame changes one pair.

**What differs.**

1. **An extra mobile between barrel and centre**, forced by the clockwise barrel of DS-W01 section 4. ml01 does
   the same, so it is real but uncommon.
2. **Our pinions are 24 and 30 leaves in the first two meshes.** Real centre pinions have 10 to 15 leaves. This is
   allowed, just less economical.
3. **Our face widths at 1:1** are 0.28 to 0.49 mm. ml01's are 0.20 to 0.50 mm. This matches roughly, but no
   catalogue value was found.
4. **Plate and bridge names** are swapped relative to real practice (section 4).
5. **Every mobile is a single material.** A real wheel is brass on a steel pinion (section 6).
6. **Seconds on a fifth mobile, not on the fourth wheel.** This is a naming difference only.

**A small inconsistency in the reference.** The docstring (l. 13-14) says the 24-hour train is "its 12 -> 48
(day wheel)". The code uses `DAY_TEETH = (10, 40)` (l. 45, 296-297). The ratio is the same; the comment is stale.

## 8. What we could adopt, ranked

Scored against the four judging criteria: gap 30, meaningful difficulty 30, reward integrity 25, craft 15. None
of these is meant to make the task harder for its own sake. Items 2, 5 and 6 change the format, a document or the
reference, so they need a human yes and a line under "Proposed spec changes".

1. **Fairness test: ml01's real going train through our grader (Part 1).**
   - **Benefit:** reward integrity and meaningful difficulty. If a professional watchmaker's train passes, our
     checks are not arbitrary. If it fails, we learn which check is unrealistic before a judge does, as the
     keyless run did (SESSION 17:45). Craft: a strong story for the README.
   - **Gap:** none.
   - **Cost:** about six scripted steps, all in a scratch folder (section 9).
2. **Material per part, not per mobile.** This would allow a brass wheel on a steel pinion.
   - **Benefit:** craft. It is the first thing a watchmaker reading FORMAT.md would flag. Meaningful difficulty:
     an agent that designs as a watchmaker does can say so. It also matters for the fairness test, whose
     intermediate wheel would be rated as brass in reality (section 9).
   - **Cost:** a format change (`material` on a part or on a gear), the strength check attributing each gear to
     the part that carries its teeth, the reference and anchors updated. Medium.
3. **Say plainly in QA-W100 and DS-W04 that check 14 is an engineering convention, and cite the real numbers.**
   - **What to say:** Lewis on the involute of DS-W04; horology designs to NIHS 20-02 profiles and has involute
     standards too (AFNOR NF S80-566); the load is SW200-1's slipping maximum, a real figure; a manual-only train
     would be rated at 11.86 N·mm (50.1 scaled).
   - **Also:** have a human check DS-W04's Y values against Shigley Table 14-2 and a published 25-degree table.
   - **Benefit:** reward integrity and craft. **Cost:** a few sentences and one lookup.
4. **Write down, for judges, why our barrel turns clockwise.** Cite ml01's intermediate wheel and US 7,452,123 as
   real precedents, and note that most calibres mesh barrel to centre pinion directly.
   - **Benefit:** meaningful difficulty (a judge sees the extra wheel is a known real layout) and craft.
     **Cost:** a README paragraph.
   - **Alternative:** a counter-clockwise class would let a textbook train drop straight in. It is a spec change
     and makes the train shorter, so it is not recommended unless the fairness test needs it.
5. **Make the 6-hour variant and "kept parts" look like real documents.**
   - **What:** state the change as a dated change notice in the style of Sellita's Information Sheets ("IS 05:
     evolution SW200 to SW200-1": which parts changed, "all other components remain interchangeable").
   - **Measure:** what is kept by part identity in both parts lists, as ETA's CTs do (a shared part number means
     a kept part). This is also the realistic answer to the "kept-parts score counts files and can be padded"
     item in the to-do list.
   - **Benefit:** craft and reward integrity. **Cost:** low for the wording; medium if a "kept" check returns.
6. **A real layout, with two-sided assembly.**
   - **What:** put the motion work and dial on the plate's side, and the bridges on the other side. The
     reference's assembly turns the movement over.
   - **Benefit:** craft, and possibly meaningful difficulty and gap, because real assembly order constraints
     appear (the centre wheel before the barrel bridge, a bridge over several pivots). This is untested; we do not
     know it bites.
   - **Cost:** high. It means a new reference frame and anchors. Part 4 already allows any path, so no rule
     changes. A cheaper half-step: rename `main_plate` and `bridge` in the documents, or explain the naming.
7. **Fix the stale docstring** in `solution/reference_watch.py` l. 13-14. Craft; trivial.

Not recommended, because these add difficulty without realism: a real rate change that touches three wheels
(6497-1 to -2), cycloidal teeth on the supplied barrel, or mandatory dial-side assembly.

## 9. Best fairness test: ml01's going train

**Why this one.** ml01 is the only verified professional going train we can get. Its train matches what our task
asks for at Part 1: centre 1 turn per hour; central seconds; motion work 12 / 36 / 10 / 40; and an intermediate
wheel, so the barrel turns with the minute hand, like DS-W01's clockwise classes. **Licence: none.** Download,
study and local testing only; nothing from it may be committed or put in an image (REAL_CAD.md §1).

**What converting it takes.** The ideas come from `spikes/keyless/realcad/` (extract, convert, phase,
grade_real) and the scratch scripts of this research.

1. **Extract.** Done: 223 solids, with names, counts, axes and meshes.
2. **Scale.** Scale x1.2 about the centre. The plate radius becomes 20.38, inside CS-414-134's 20.7. Modules
   become 0.18, 0.18, 0.156, 0.139 and 0.122. This keeps the case, process and strength checks at our values.
   The alternative is grading at 1:1 with the case, the printability limit and T_barrel overridden.
3. **Barrel.** Override the supplied barrel with ml01's barrel II (drum plus cover) at its own axis, and the speed
   with 3/20 turn per hour, clockwise. This is not a DS-W01 class, so it is a constants override, like
   `grade_real.py` did for keyless. Using BR-096-20 instead would mean redesigning the first mesh, and the train
   would no longer be the real one.
4. **Frame and mobiles.**
   - Fixed: the main plate, train bridge, barrel bridge, minute bridge, pallet bridge, motion-work bridge, jewels,
     chatons, screws, barrel I, the ratchets and arbor II.
   - Mobiles: intermediate, centre plus cannon, third, seconds, minute wheel, hour wheel. The escape wheel is left
     out, since our task has no escapement and the seconds wheel carries the hand.
   - Drop: the balance, pallets, keyless works and springs.
5. **Hands.** Add three simple hand parts (hour, minute, central seconds), each reaching at least 5 mm, above
   the frame. ml01's CAD has none.
6. **Phasing.** Turn the driven wheels until every rest overlap is at most 0.01 mm³. Five pairs are over today
   (section 5). `phase_ml01.py` shows the method.
7. **Bores.** If "free to turn" fails on line-to-line fits, widen each mobile's own bore by a few microns, as the
   keyless run did (REAL_CAD.md §2, adjustment 1). Log every such change as a finding about the simulator.
8. **Run Part 1 only**, with `grade_watch.py` unchanged and the constants overridden. Parts 2 and 3 do not apply:
   ml01 has no 24-hour hand and no variant. Part 4 can follow once Part 1 passes.

**What to expect.** These are estimates from the research agent's arithmetic, not grader runs.

- **Check 14, at x1.2 and 70.1 N·mm:**

  | Gear | Stress (MPa) |
  |---|---|
  | centre pinion 12 | 354 |
  | intermediate wheel 26 | 335 as driven, 241 as driver |
  | third pinion | 223 |
  | centre wheel | 107 |

  - Declared steel (allowable 725), everything passes.
  - **Declared brass (110), the intermediate wheel fails.** The fair load for a train of this size would be
    16.57 x 1.2³ = 28.6 N·mm *(derived)*, and the intermediate wheel would still be above 110 even then.
  - This is the concrete case for item 2 of section 8, and for stating the load and the convention.
- **Check 13, printability (0.2 mm smallest feature):** the 0.2 mm wheels become 0.24 at x1.2, which is
  marginal. The fine teeth of m 0.12 to 0.14 are at risk. Worth reporting as "a real design at this scale is near
  our printing limit", not as a failure of the train.
- **Check 5 (arbors 0.03 mm out of place):** the tightest tip-to-root clearance after the shift is 0.019 mm at
  x1.2, so it probably passes.
- **Checks 4 and 6, and the drive measure V/H > 0.5 m²:** not estimated.

## 10. What we could not reach

The container's network policy let web search through but refused nearly every page download. Exceptions:
raw.githubusercontent.com, anonymous `git clone` from GitHub, patentimages.storage.googleapis.com, and
www.marcolangwatches.com (see below).

**Refused:**

- **Manufacturers:** sellita.ch, eta.ch, shopb2b.eta.ch.
- **Suppliers:** cousinsuk.com, ofrei.com, julesborel.com, boley.de, watchguy.co.uk, watch-spare.com.
- **Standards and textbooks:** fhs.swiss, ssc.ch, highered.mheducation.com.
- **Reference sites:** en.wikipedia.org, ranfft.de, ranfft.org, horopedia.org.
- **Forums:** watchuseek.com, watchrepairtalk.com, timezone.com, theindex.nawcc.org.
- **Hobbyist and educational sites:** watchmaking.io, horology-student.org, 17jewels.info, calibercorner.com,
  abbeyclock.com, flume.de, watchmaking.com, awci.com.
- **Archives:** archive.org, web.archive.org.
- **Patents:** patents.google.com, espacenet, uspto.
- **CAD sites:** grabcad.com, printables.com, thingiverse.com, makerworld.com, cad.onshape.com, openmovement.org.
- **GitHub:** the REST API for repositories not in this session.

**Fetch these first, to turn [snippet] facts into primary ones:**

- the ETA CTs for 6497-1, 6498-1, 6497-2 and 6498-2 (patrimoine.bourgognefranchecomte.fr mirror) and for 2893-2;
- Sellita DocTec SW200-1 v07, and IS 05, IS 33 and IS 03;
- Cousins `14_ETA 2892.A2 2016 Version2.pdf` and `29_ETA2801.2-ETA2836.2.pdf`;
- watchmaking.io's 6498 measurement page;
- Eisenegger's *Uhrenkonstruktion* sample and Mann's Kaliber 972 gear table;
- Shigley Table 14-2;
- the OM10 STEP (needs an account).

**One environment change was made during this research.** A research subagent asked to add
`www.marcolangwatches.com` to this session's personal cloud environment so it could download ml01, and the
approval prompt was accepted. The change lasts for later sessions on that environment.

**Not verified.** Every [snippet] fact. The Lewis and printability estimates in section 9 (not run through our
grader). Whether ml01's wheels are brass (the STEP has no materials). The GrabCAD 6497 models' licence and
content.
