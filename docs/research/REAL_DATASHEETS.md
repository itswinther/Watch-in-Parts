# Real, publicly downloadable datasheets for the keyless-works task

Written by Mikael + Claude (workstream A), 14 Nov 2026. Research only: no task file was changed.
The synthesized, cited datasheets in `spikes/keyless/datasheets/` (DS-101 to DS-501) stay the fallback;
this file lists the real documents that could replace or back them.

**Method.** Every document below was downloaded on 14 Nov 2026 with `curlimages/curl` in Docker into a
scratch folder outside the repo. Text was extracted with `pypdf` in `python:3.12-slim`, and the values
quoted here were read from that text, not from search snippets. The sha256 is of the file as served that
day. No document was committed. Wayback snapshots were found with the `archive.org/wayback/available`
API, and the main ones were re-downloaded (`id_` form) to check that they match byte for byte.

**Labels.**

- **[PD]** public domain or a US-government work: could even be shipped in the image or the repo.
- **[link-only]** copyrighted, no licence: fetch from the official URL at build time and never commit.
- **[secondary]** a reseller or mirror, not the maker.
- **[derived]** our arithmetic on published values.

This is our reading of the terms, not legal advice.

---

## 0. Summary

| Need | Best real document | Fetch | Ship |
|---|---|---|---|
| Movement envelope, reserve, parts names | ETA 2824-2 CT (ETA official) | yes | no |
| Crown turns to full wind, barrel turns | TMI NH3 technical guide; Miyota 8215 and 9015 specs; Sellita SW200-1 / SW215-1 | yes | no |
| Stem thread, stem travel, stem length | Sellita SW200-1 DocTec (has a confidentiality notice, see 1.2); SW215-1 | ask first | no |
| Mainspring torque | Grossmann, *Lessons in Horology* (1905): formula, worked example, torque per barrel turn | yes | **yes [PD]** |
| Mainspring sizes | Resellers only (ressortdebarillet.ch, Cousins). Générale Ressorts catalogue is not public | HTML, unstable | no |
| Jewels | Bird Precision ring-jewel catalogue (tolerances); H.S. Walsh listing (Seitz sizes) | yes / HTML | no |
| Brass, nickel silver, steels, spring alloy | Wieland Z32/Z33, Matthey CuNi18Zn20, Alleima 20C, Jacques Allemann 20AP, Zapp, Nivaflex 45/5 | yes | no |
| Friction | Grossmann 1905 table [PD]; Lewis 1896 [PD]; NACA TR-1062 [PD]; Engineering ToolBox | yes | PD ones yes |
| Finger torque on a small knob | MIL-STD-1472H fig. 10 [PD]; Imrhan & Munoz-Vasa 2013 (3.3 to 6.4 mm cylinders) | yes | 1472H yes |
| Gear and keyless theory | Saunier, *Treatise on Modern Horology* (1887) [PD]; Saunier, *Watchmakers' Hand Book* (Gutenberg) [PD] | yes | yes |

---

## 1. Movement technical documents

All of these are free downloads without a login. None states a licence.

- **ETA:** a liability disclaimer, "All modifications reserved", and copyright by default.
- **Miyota:** the site footer says "Copyright Citizen Watch Co., Ltd. All Rights Reserved."
- **TMI:** "Copyright © Time Module Ltd."

So all are **[link-only]**: fetch at build time for evaluation (the same as any watchmaker downloading
them), and never commit or republish them.

### 1.1 ETA (Swatch Group)

| Doc | URL | sha256 | Pages | Wayback |
|---|---|---|---|---|
| CT 2824-2, FDE 481688 25, 06.10.2022 | https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1883 | `d280c3f1b0cbaf2a84f999f96b53bbb3b28947fb307c225843cd6893cd548d56` (7,393,595 B) | 24 | 2024-04-24 snapshot exists but is **truncated at 1 MiB**: not a usable fallback |
| CT 2801-2, FDE 481538 15, 12.12.2017 | https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1626 | `d93cfce3ca4fca17f751c82df4e4efc9f305fe924e3033caae96d25b018fbb92` | 20 | none |
| CT 2804-2, FDE 481611 13, 28.05.2013 [secondary: Beco Technic mirror] | https://www.beco-technic.com/media/77/ea/90/1619813321/eta_2804-2_de_en_fr.pdf | `88572af42b0d5217ec83624b5cd231ef362fc0d1657c957e57793b18ac5399d5` | 12 | none |
| CT 6497-2, FDE 482448 13, 31.05.2017 [secondary: Bourgogne-Franche-Comté heritage site] | https://patrimoine.bourgognefranchecomte.fr/documents/ETA_6497-2.pdf | `7d0dacebff6c95c5774705ed730b57dfaf3bfab638c8b654eb28f2b6d44fe3f5` | 24 | 2026-04-10 snapshot **truncated at 5 MiB** |
| CT 6498-1, FDE 482382 09, 05.12.2016 [secondary, same site] | https://patrimoine.bourgognefranchecomte.fr/documents/ETA_6498-1.pdf | `0923e2aac216261626001d8f914081324b85f9931b5aa93f01acee04ddce91ca` | 24 | listed, not checked |

**Values (page 1 of each, primary):**

| Calibre | Size | Height | Reserve | Jewels | Lift | Frequency |
|---|---|---|---|---|---|---|
| 2824-2 | 11½‴, Ø 25.60 mm | 4.60 mm | min 38 h, typical 42 h | 25 | 50° typical | 28,800 A/h |
| 2801-2 (hand-wound) | 11½‴, Ø 25.60 | 3.35 | 42 h | 17 | 50° | 28,800 |
| 2804-2 (hand-wound) | 11½‴, Ø 25.60 | 3.35 | 42 h | 17 | 50° | 28,800 |
| 6497-2 (hand-wound) | 16½‴, Ø 36.60 | 4.50 | 53 h | 17 | 44° | 21,600 |
| 6498-1 (hand-wound) | 16½‴, Ø 36.60 | 4.50 | 46 h | 17 | 44° | 18,000 |

**What else is in them:**

- **Keyless parts list with numbered positions and part numbers.** For the 6497-2: setting lever,
  winding pinion, sliding pinion, winding stem, yoke, yoke spring, setting wheel, intermediate setting
  wheel, setting-lever jumper, crown-wheel ring, crown wheel, click spring, click, ratchet wheel.
- The assembly order of the hand-setting mechanism.
- Lubricants per point (Moebius 9010, 9415, 9501 and so on; epilame Fixodrop).
- The **crown-wheel screw is a left-hand thread**.
- Stem removal: in position 2, undo the setting-lever screw at most 2 turns.

This corrects STANDARDS.md 3.5. "Unitas 6497-1, 46 h, 18,000 A/h" is now primary for the **6498-1**.
The 6497-2 is primary at 53 h, 21,600 A/h, 44° lift.

**Not in them:** tooth counts, modules, stem travel, crown turns to full wind, mainspring size or torque.

### 1.2 Sellita

| Doc | URL | sha256 | Pages | Wayback |
|---|---|---|---|---|
| SW200-1 Documentation technique, rev 07, 02.09.2024 | https://www.sellita.ch/scripts/calibres/images/DocTec_SW200-1_7.pdf | `511ad6793e8d6969c19c8fb8e459d6623de0aac505d7976a1a6cd0eae894c593` | 28 | **verified identical**: https://web.archive.org/web/20261103025053id_/https://www.sellita.ch/scripts/calibres/images/DocTec_SW200-1_7.pdf |
| SW210-1 DocTec, rev 01, 2014 [secondary: Boley mirror; sellita.ch now returns 404] | https://boley.de/downloads/b85c043fdb1a40528caf6ca9b4bf3dfb/SELLITA-210-1.pdf | `45c8e28d264a7c1cd8db57d89f2d41f418ed89cabd071efbda7358a12b18e8c2` | 23 | none |
| SW215-1 DocTec, rev 01, 14.11.2014 [secondary: Boley] | https://boley.de/downloads/f3ce59ff595344b58a7b4ba7d729560f/SELLITA-215-1.pdf | `ad00434ffeed5e805ff3cac508ed49726d1768a43cbcfc160e42c8ee14ae41ce` | 25 | none |
| Catalogue 2024 ENG | https://sellita.ch/images/documents/Catalogue2024_ENG.pdf | `e2a5bbc081bd8cc86407c4ebd1d991076bd3eb6a56b1045df9cf333077a5befc` (29 MB) | 126 | 2026-11-13, not checked |
| Catalogue 2026-2027 ENG | https://sellita.ch/images/documents/Catalogue_2026-2027_ENG.pdf | `4695a6aee0126711686a2dd8bc9d23b7d80ca7b767dab23b968f10360c02023d` (83 MB) | 71 | 2026-11-13, not checked |

**Values: the best keyless numbers we found anywhere.**

- **SW200-1** (automatic, 2824 class):
  - 4.60 mm high, Ø 25.60 mm, 28,800 A/h;
  - reserve min 38 h, typical 41 h;
  - 26 jewels, lift 50°.
  - **Winding by the stem:** minimum 27 turns at up to 100 rpm, within 25 s with the automatic device
    fitted (p. 4). We read "27 turns" as the minimum number of crown turns for a full wind (the
    document does not say this in words).
  - **Stem travel ("Course de la tige"): 0.80 mm** (frame drawing p. 12).
  - **Stem thread: S 0.90** (pp. 12 and 25).
  - Stem length, normal / long: 15.50 / 20.00 mm (p. 25).
  - The crown-to-case-middle gap must be no more than 0.1 mm (p. 25).
  - Screw torques are given as minimum loosening torques: 8, 12 and 16 N·mm (pp. 10 to 11).
- **SW215-1** (hand-wound, 2801 class):
  - 3.35 mm high, 42 h;
  - **manual winding minimum 23 turns** at up to 100 rpm;
  - stem travel 0.80 mm;
  - stem "S0.90x16" (parts list);
  - stem length 15.50 mm normal.
- **SW210-1:** 3.35 mm, 42 h, 19 jewels, lift 50°, minimum 23 winding turns.

**Terms: the SW200-1 drawing pages say:**

> This document is confidential and belongs to SELLITA WATCH CO S.A. ... access is strictly reserved
> to persons authorised by SELLITA ... may not be copied, reproduced or distributed without prior
> written authorisation.

(Our translation of the French. The notice is printed 8 times, on the drawing pages.) Yet Sellita
publishes the file openly on its own site, without a login.

**Recommendation:** do not fetch the SW200-1 DocTec into the agent image without written permission from
Sellita. Use its numbers only as cited facts in our own synthesized datasheet; that is what DS-401 already
does. The 2014 Boley copies of SW210-1 and SW215-1 carry no such notice in their text, but they are
third-party mirrors: treat them as [link-only].

### 1.3 Miyota (Citizen)

Official files on miyotamovement.com. The upload ids differ from those in search indexes, so use these.

| Doc | URL | sha256 | Pages | Wayback |
|---|---|---|---|---|
| Movements list | https://miyotamovement.com/assets_en/pdf/movement.pdf | `75ee19bbfd08ca2f4b771e672ba392f42fa4fc0273ea9a87b498900638b51c15` | 2 | 2026-06-16 |
| 8215 spec | https://miyotamovement.com/uploads/product/product_8jT5DEdzRXAsaSN2Bu.pdf | `bcb22d8e921b06165e67ffbbecfbcc444b8a67ccb4319d598c14bda6216418dc` | 2 | **verified identical**: https://web.archive.org/web/20261003045553id_/https://miyotamovement.com/uploads/product/product_8jT5DEdzRXAsaSN2Bu.pdf |
| 8215 drawing (image only) | https://miyotamovement.com/uploads/product/product_LGuS8EY5DX03RiBaJH.pdf | `95db183473b7372aad4f80665c23cdff32d5f64fdfe63b1cc3828811ef132c54` | 4 | 2026-10-03 |
| 8215 parts list | https://miyotamovement.com/uploads/product/product_PveYk926HfOtdLJUux.pdf | `fdafef819f8d0f3d91e4062072ce13a05beb20a4a61b96c6e2415500281657ad` | 1 | none |
| 8215 manual | https://miyotamovement.com/uploads/product/product_mRAnUkS0wHFurpOK3T.pdf | `6286b8431619f825b6bfd2715be78891dd2cd7ba3dfbead3959d570b08e2afb9` | 1 | 2026-10-03 |
| 9015 spec | https://miyotamovement.com/uploads/product/product_7ev6UD3QZ0FwfgH1kJ.pdf | `7192f8fccdc30b428315d234a9ca37479c26e7914466939b0870aeb56db48e28` | 2 | **verified identical**: https://web.archive.org/web/20260828112428id_/https://miyotamovement.com/uploads/product/product_7ev6UD3QZ0FwfgH1kJ.pdf |
| 9015 drawing (image only) | https://miyotamovement.com/uploads/product/product_GRZasplzcESHFnDKI0.pdf | `ad67fa2b8e5a1680ffd4261e79452d5feae512b8f8ba87e96f27f45b53155e3d` | 3 | 2026-08-28 |
| 9015 parts list | https://miyotamovement.com/uploads/product/product_6VYkM4Gnta0BQXiULu.pdf | `7097238a181bb9fc1086937b6e4f82768b0ab22b7a06c8ac6dcb377bdc63e227` | 1 | 2026-08-28 |
| 82S7 spec | https://miyotamovement.com/uploads/product/product_mCGlRLBZIOVron80fp.pdf | `b8ce9d456175033839e6920422e385d80fbc814a3b58e27d313c4dd49229eb3e` | 2 | 2026-10-03 |
| 82S7 drawing (image only) | https://miyotamovement.com/uploads/product/product_fWHSMkEOPZ9opDtgzn.pdf | `559ad79078c5aba88fbe4248658278b74bd80298512963f00a94ba7f03ac6a53` | 4 | 2026-02-15 |
| 82S7 parts list | https://miyotamovement.com/uploads/product/product_9H3Tv1IMaunDXC8l5Q.pdf | `4068ecda007c84e76e2b6abf40dcdc93cb83be6eaafbdc91b10023d6f764a535` | 1 | none |

**Values:**

| Calibre | Size | Height | Reserve | Frequency | Lift | Jewels | Stem |
|---|---|---|---|---|---|---|---|
| 8215 | 11½‴, Ø 26.00 mm | 5.67 mm | more than 42 h | 21,600 | 49° | 21 | stem 065-212 |
| 82S7 | same | 5.67 | about 42 h | 21,600 | 49° | 21 | stem 065-212 |
| 9015 | 11½‴, Ø 26.00 | 3.90 | about 42 h | 28,800 | 51° | 24 | stem 065-A05 |

- **"To make full-winded: 82 / 8N / 90 / 91: turn the crown 40 times; 6T: 20 times."** (spec p. 2)
- The 9015 parts list names the whole keyless train: winding pinion 063-351, clutch wheel 064-991,
  crown wheel 058-502, ratchet wheel 059-805, click 060-551, click spring 903-A15, setting lever 067-995,
  setting-lever spring 077-996, yoke 071-995, setting wheel 076-751, setting stem 065-A05 (longer stem
  24.0 mm: 065-A25).
- No dimensions of the parts. The drawings are image-only PDFs: they would need OCR or a human to read
  the stem dimensions.

### 1.4 Seiko Instruments / Time Module (NH35, NH36)

| Doc | URL | sha256 | Pages | Wayback |
|---|---|---|---|---|
| NH3 series (NH34A to NH39A) technical guide and parts catalogue, 25.06.2025 | https://timemodule.com/upload/category/24/technical_guide/NH35_TG.pdf (byte-identical to `.../25/technical_guide/NH36_TG.pdf`) | `0cd2c8b82e392b6daed4306b4b679b97ff2b3d9cbcc9dcb75ccada806dd4a8b0` | 20 | the snapshot is an **HTML page, not the PDF**: no usable fallback |
| NH35 spec sheet | https://timemodule.com/upload/category/24/spec_sheet/NH35_SS.pdf | `ef1a20e566691b887d1de947de0fe3786bddba2e5084055f7632831a261a748d` | 11 (mostly images) | 2026-02-06, not checked |
| NH36 spec sheet | https://timemodule.com/upload/category/25/spec_sheet/NH36_SS.pdf | `fc2f8218e879f5b6f5b171aa5cc5e2b5ddce13daa36d4c92e8715faeb8185963` | 10 | 2026-02-06, not checked |
| NH36A specification, SII, 09.01.2014 [secondary: Cousins copy] | https://www.cousinsuk.com/PDF/categories/6809_Seiko%20NH36%20Technical%20Sheet.pdf | `491068dc3f949ecaf266f5a5e415dd27dd2e0e6457f7b8e0045018c38d27522f` | 10 | none |

The index of all TMI downloads (no login) is https://www.timemodule.com/en/download_support/.

**Values:**

- **Size:** Ø 27.40 mm (29.36 mm with the dial spacer), 5.32 mm high.
- **Rate and running:** 21,600 A/h, lift 53°, more than 41 h, accuracy -20 to +40 s/day.
- **"Fully wound up by turning the crown minimum 55 times. Fully wound up by turning the ratchet wheel
  screw 8 times."** (TG p. 2)
  - That is **8 barrel turns** for a full wind, and **about 6.9 crown turns per barrel turn** [derived].
  - So **about 5.1 h per barrel turn** [derived: 41 h / 8].
- **Crown:** at the normal position, clockwise winds and anticlockwise is free.
  - NH35: first click, date setting; second click, time setting.
  - NH36: first click, day and date.
- **SII 2014 sheet:** hand fitting force under 50 N (hour and minute) and under 30 N (seconds). Hand
  unbalance under 1.50, 1.25 and 0.20 µN·m.

Seiko **6R15** and Seagull **ST36 / ST3600**: no official technical document found (gap).

---

## 2. Mainsprings

| Doc | URL | sha256 | Pages | Terms |
|---|---|---|---|---|
| **J. Grossmann, *Lessons in Horology*, 1905** (Internet Archive, Library of Congress scan) | https://archive.org/download/lessonsinhorolog00gros/lessonsinhorolog00gros.pdf ; text: `.../lessonsinhorolog00gros_djvu.txt` | pdf `a2d2500626c8903dfec6dd4fa315b99db3ec3f037c8ffc43790b0c90c75d6053`; txt `9463393b8bf93baaded5aae2a420866d3215df70d36d3da5f24fbdb553afec3f` | 294 | **[PD]** 1905. The item says "The Library of Congress is unaware of any copyright restrictions" |
| Barrel spring 1.23 × 0.134 × 400 × 10.5 (ETA 2801), ressortdebarillet.ch [secondary] | https://en.ressortdebarillet.ch/products/1-23-x-134-x-400-x-10-5-eta-2801-mecanique (`.json` adds a stable body) | json `af65832d36a9599396651ab6b41254679f3e3bd212e26e1c7a54e85583ee3162` (HTML changes; do not pin it) | n/a | [link-only] |
| Cousins UK mainsprings by size and by list [secondary] | https://www.cousinsuk.com/category/mainsprings-by-size-search-watch-pocket | **403 to non-browser clients** (bot protection) | n/a | [link-only], not fetchable at build |
| Nivaflex 45/5 sheet (Vacuumschmelze data; Cousins copy) | https://www.cousinsuk.com/pdf/skus/9601_9596_nivaflex_45_5.pdf | `dddc1ee277c758c79aa9355f5f76dd6088ca4cfd1d15482c02dca12fa9060aef` | 2 | [link-only]. Wayback 2025-02-11 exists. VAC's own 45/18 URL is now 404 (Wayback 2024-06-07 exists) |

**Grossmann 1905 gives what no maker publishes: a mainspring torque law with a worked example.**

- **Formula (art. 97):** M = E·h·e³·2πn / (12·L), with E the elastic modulus, h the height, e the
  thickness, L the length and n the turns wound beyond the free state.
- **Worked example (art. 99):** a pocket-watch spring, h = 3.6 mm, e = 0.18 mm, L = 650 mm,
  E = 23,000,000 g/mm².
  - The free spring makes 5 turns, 14 in the barrel, with a 6-turn development; n = 14.5 at full wind.
  - **M = 5,640 g·mm (about 55 N·mm) at full wind, falling by 389 g·mm per barrel turn:** 5,251,
    4,862, 4,473, 4,084 ...
  - It also notes that the moment is larger when wound, so the torque is not flat.
- **Coefficient-of-elasticity table:** art. 92.
- **Friction table:** art. 335, see 4.

**Nivaflex 45/5:**

- Tensile strength Rm 1,835 to 3,095 MPa by condition;
- Rp0.2 about 80 % of Rm;
- E = 220 GPa, G = 90 GPa;
- up to 830 HV.

**Example, applying Grossmann to a 2824-class spring [derived, not a published figure].**

- **Spring:** about 1.25 × 0.125 × 360 mm (Omega Forums size in STANDARDS.md 4.2, [secondary]).
- **Material:** E = 220 GPa (Nivaflex).
- **Torque law:** M ≈ 0.78 N·mm per turn of n.
- **At a full wind:** with n ≈ 8 to 11, about 6 to 9 N·mm.
- **At the crown:** dividing by the NH35 ratio of about 6.9 gives about 1 to 1.3 N·mm, before keyless
  friction. That is far below the finger limits in section 6.

---

## 3. Jewels

| Doc | URL | sha256 | Pages | Terms |
|---|---|---|---|---|
| Bird Precision, *Ring Jewel Bearings* catalogue (1913 to 2013 centenary edition) | https://catalog.birdprecision.com/Asset/Ring_jewel.pdf | `047989c069a0e844f33673fdcaf84547c6d5cc6882f11577d180dd31ac54ff41` | 5 | [link-only]. No Wayback snapshot. (The HTML catalogue returns 403 to bots.) |
| H.S. Walsh, jewel holes (Bergeon 30712 Seitz) [secondary] | https://www.hswalsh.com/watch-parts-straps-batteries/jewel-holes-endstones-roller-pins-pallet-stones/jewel-holes/cat-8 | HTML, changes; do not pin | n/a | [link-only] |
| Cousins 2018 non-branded parts catalogue [secondary] | https://www.cousinsuk.com/PDF/products/8664_Cousins%202018%20WATCH%20PARTS%20NON%20BRANDED%20Catalogue.pdf | `f5a9c349866613f9cd21219f8c7b56d16b8f0189f677faa313141fbf21591783` (11 MB) | 214 | [link-only] |

**Values:**

- **Bird (instrument jewels, US):**
  - ID tolerance 0.0002" (5.1 µm) total band, at no extra cost, below 0.080" ID;
  - 0.0001" (2.5 µm) on request;
  - ID-to-OD concentricity 0.0002" TIR;
  - mounting concentricity 0.0005" TIR, trued to 0.0002 to 0.0003".
- **H.S. Walsh, Seitz flat cylindrical jewel holes:** sizes Ø 0.14 to 0.28 mm hole × Ø 2.60 or 3.00 mm
  OD (MJ18-xx.260 / .300).
- **Cousins 2018, Seitz and Bergeon brass bushes:** listed as OD × hole × height, e.g. 0.70 × 0.10 × 0.25,
  0.90 × 0.50 × 0.90, 1.20 × 0.50 × 1.00 mm.

**Not found:**

- an official Seitz or Swiss jewel-maker size table;
- olive-hole tolerances;
- any load rating for a watch jewel (gap).

---

## 4. Materials and friction

| Doc | URL | sha256 | Pages | Wayback | Values |
|---|---|---|---|---|---|
| Wieland Z32/Z33 (CuZn39Pb3, CW614N, C38500) | https://www.wieland.com/da/content/download/9842/file/Z32-Z33_EX_EN.pdf | `80ea72ebc943c442147728bb8e281bba5e4a276c44e5de0c09651c863850bb6d` | 2 | 2026-01-24 | see below |
| Diehl Brass Solutions datasheet 002 (CuZn39Pb3) | https://www.diehl.com/cms/files/Diehl_Brass_Solutions_Material_Datasheet_002.pdf | `4e26c5246db2f11b8325770621e624e1d45116fb90a26bb93807a7afb383eb3e` | 1 | 2024-03-31 | density 8.5; α 19.97e-6/K; "cold formability less suitable" |
| Matthey CuNi18Zn20 (nickel silver, CW409J, 2.0740) | https://www.matthey.ch/fileadmin/user_upload/downloads/fichetechnique/EN/CuNi18Zn20_v22E.pdf | `66e1f08bd4edd24812e2d43e7b0a1adff733603beb83b81f7184340b11fe7ba1` | 2 | 2026-11-02 | see below |
| Matthey CuZn38Pb2 (CW608N) | https://www.matthey.ch/fileadmin/user_upload/downloads/fichetechnique/EN/CuZn38Pb2_v22E.pdf | `805e2071d0a0b81b5fb007d3a87c0f1e88d4ea0b67da1204c9a31984f07a2740` | 2 | 2026-08-10 | E 102 GPa, density 8.44 |
| Alleima 20C strip (1.1274, ASTM 1095) | https://www.alleima.com/en/technical-center/material-datasheets/strip-steel/alleima-20c/?show=pdf | `7b8b5830d76d40aab5b35193ea3bd3b1e56cc7d868ce50745ca2c5727f2b3117` | 6 | none | see below |
| Jacques Allemann 20AP wire tech sheet | https://www.jacques-allemann.com/media/cms/Legierungen%20/%20Tech-Sheets/JAS%20-%20Tech%20Sheet%20/%20Werkstoffe/jas-020-tech-sheet-20ap.pdf | `68ea389af60893d12ba8e3db310cb1db92b243e1b4600f55982fe78516939234` | 2 | 2025-12-13 | see below |
| Zapp free-cutting wire (20AP, Finemac) | https://www.zapp.com/fileadmin/_documents/Downloads/PW/informationsdatenblaetter/FreeCuttingWire-Data_sheet.pdf | `da1adb4aea1639b9cd951bf2595c5d5bd64801bf8d5ac0cf4e698ffc44e854b5` | 3 | 2025-05-31 | 20AP "hardenable, free-cutting carbon steel"; watch parts |
| Alleima Exera 20AP medical wire | https://www.alleima.com/contentassets/8b6ec81edfc843589ef203e96462b372/datasheet-exera-20ap-free-cutting-medical-wire-en-v2023-11-09-1440-version-1.pdf/download | `aaf204ba3ba0d7f5591cf547288c5523cbf30c7a3debbd016597563f95f3d8b0` | 5 | none | Rm and Rp0.2 by diameter; impact strength vs tempering |
| **Grossmann 1905**, art. 335 friction table | see 2 | | | | see below |
| **W. T. Lewis, *Friction, Lubrication and the Lubricants in Horology*, 1896** | https://archive.org/download/frictionlubricat00lewi/frictionlubricat00lewi.pdf (txt `_djvu.txt`) | pdf `8f27f6f70d121b319fc329321ce5f6dccaab60cb83190614122ff7cd29900d13`; txt `dd9440cded3179eb3d7a49eaa2a5f79f95ea5fc73538c57f618a076752d0d3e1` | 104 | (IA item) | see below |
| **NACA Report 1062 (1952)**: brass, bronze and others sliding on SAE 52100 steel | https://ntrs.nasa.gov/api/citations/19930092108/downloads/19930092108.pdf | `752dbb70e788a455708f8194e8624926881dfee95812530cdaf474e16a24ea2e` | 20 | none | brass tested (65 Cu cold drawn) as a cage material; "results with brass ... were poor" |
| Engineering ToolBox, friction coefficients | https://www.engineeringtoolbox.com/friction-coefficients-d_778.html | HTML changes; do not pin | n/a | 2026-10-31 | see below |

Details for the rows marked "see below":

- **Wieland Z32/Z33 (CuZn39Pb3):**
  - E 96 GPa, density 8.46 g/cm³, thermal conductivity 113 W/(m·K);
  - round rod tempers R360 / R430 / R500: Rm 360 / 430 / 500 MPa and Rp0.2 – / 220 / 350 MPa;
  - HB 90 to 160.
- **Matthey CuNi18Zn20:**
  - E 135 GPa, density 8.7;
  - strip R370 to R680: Rm 370 to 700+ MPa, HV 90 to 200+;
  - "used in the watch making industry".
- **Alleima 20C strip:**
  - nominal composition C 1.00, Si 0.25, Mn 0.45;
  - Rm 2,100 MPa (under 0.125 mm) down to 1,600 MPa (1 to 3.5 mm thick); Rp0.2 1,900 to 1,450 MPa;
  - density 7.85;
  - thickness tolerances (T1).
- **Jacques Allemann 20AP:**
  - "~1095, 1.1268+Pb";
  - C 1.00, Mn 0.40, Si 0.20, S 0.05, Pb 0.20;
  - wire Ø 0.02 to 4.00 mm;
  - "most commonly used material in décolletage ... watch and automobile industry".
- **Grossmann friction table (art. 335):** metal on metal 0.15 to 0.17; **metal on precious stones 0.15**;
  well-greased large machines 0.08.
- **Lewis 1896:** the theory of friction in watches, the laws of friction, the effect of lubricants.
- **Engineering ToolBox:**
  - steel on steel: dry 0.5 to 0.8 static, 0.42 kinetic; greased 0.16;
  - brass on steel: dry 0.51 static, 0.44 kinetic; greased 0.19.

Not found: a CuZn39Pb3 sheet on matthey.ch (the guessed URL is 404); a Wieland N18 nickel-silver sheet
(404 now; Wayback 2022-06-18 exists).

**Terms:**

- The maker sheets are [link-only]. Matthey: "informative only"; Diehl: "general information purposes
  only".
- Grossmann, Lewis and NACA are **[PD]**: pre-1930 US publications, or US-government work (NACA/NASA).

---

## 5. Crowns and stems

- **The real numbers come from Sellita (1.2):**
  - stem thread **S 0.90**;
  - stem travel **0.80 mm**;
  - stem length 15.50 mm (normal) or 20.00 mm (long);
  - crown-to-case gap ≤ 0.1 mm.
- **Miyota:** stem part numbers only. The 9015 long stem is 24.0 mm.
- **ETA:** the stem is position 4 (2801/2824) or 5 (6497). No dimensions.
- **Thread pitch:** S 0.90 is an NIHS "S-series" watch thread; a vendor gives a pitch of 0.225 mm
  [secondary; vb-tools.com blocks scripted fetches]. The NIHS 06-xx thread norms are paywalled.
- **Found nothing usable as a public datasheet from Cousins or Esslinger** for crown taps or stem threads.
  Their listings are HTML behind bot protection (Cousins answers 403 to scripted clients) and give part
  numbers, not ratings.

---

## 6. Human factors: finger torque on a small knob

| Doc | URL | sha256 | Pages | Wayback | Terms |
|---|---|---|---|---|---|
| **MIL-STD-1472H, *Human Engineering*, 15 Sep 2020** | https://everyspec.com/MIL-STD/MIL-STD-1400-1499/download.php?spec=MIL-STD-1472H.057041.pdf (official source: DLA ASSIST, quicksearch.dla.mil) | `74ca9890986bd86d787a964cd2f37f101e1ec9c8c2087259abf1e11abdb96d65` (12.9 MB) | 456 | 2025-12-07 snapshot **truncated at 5 MiB** | **[PD]** "DISTRIBUTION STATEMENT A. Approved for public release. Distribution is unlimited." |
| FAA HF-STD-001B, *Human Factors Design Standard*, Dec 2016 | https://hf.tc.faa.gov/publications/2016-12-human-factors-design-standard/full_text.pdf | `bcbbe0276186f2042e6b9bca9af5eb08e2e7d502b89b944735e49e6ef696fa4d` (12.5 MB) | 753 | **verified identical**: https://web.archive.org/web/20250622134643id_/https://hf.tc.faa.gov/publications/2016-12-human-factors-design-standard/full_text.pdf | [PD] US-government work |
| Imrhan & Munoz-Vasa, "Finger pinch loosening and tightening torques on small cylindrical handles among industrial workers", *ISER* 1(2), 2013 | https://westpointpressjournals.westpoint.edu/index.php/iser/article/download/20/Imrhan/112 | `85d098471c0487e5eb11657fac71ba0ba637096429b2061041713bf0706f7f60` | 9 | none | [link-only] ("ISER © 2013"; no licence found) |
| DoD *Human Engineering Design Data Digest* (2000) and AMRL knob-torque report (1962) | https://apps.dtic.mil/sti/pdfs/ADA467401.pdf ; https://apps.dtic.mil/sti/tr/pdf/AD0283347.pdf | DTIC returns **403 to curl** | | Wayback 2023-12-14 / 2025-02-02 | [PD] |
| NASA-STD-3000 (MSIS) sections 4 and 11 | https://msis.jsc.nasa.gov/sections/section11.htm | **DNS failed** on 14 Nov 2026 | | Wayback 2025-04-06 | [PD] |

**Values:**

- **MIL-STD-1472H, figure 10 (Knobs, PDF p. 89, printed p. 72):**
  - fingertip-grasp knob **diameter minimum 10 mm**, maximum 100 mm; height 13 to 25 mm;
  - **maximum torque 32 mN·m (4.5 in-ozf) for knobs of 25 mm diameter or less**, and 42 mN·m above that;
  - "Knobs shall have resistance as low as possible without permitting the setting to be changed by
    vibration or merely touching" (5.1.4.1.2.1.7.2).
  - A watch crown (about 4 to 7 mm) is **below the standard's minimum knob size**, so the 32 mN·m is an
    upper bound on intended operating torque, not a crown rating.
- **Imrhan 2013, tables 2 and 3:** mean MVC torque in in-oz, ×7.06 for mN·m.

  | Diameter | Group | Smooth, loosen | Smooth, tighten | Knurled, loosen | Knurled, tighten |
  |---|---|---|---|---|---|
  | 5.0 mm | male, n = 10 | 21.9 (155 mN·m) | 22.2 | 26.0 | 41.6 |
  | 5.0 mm | female, n = 13 | 12.7 (90 mN·m) | 13.6 (96 mN·m) | 22.1 | 32.8 |
  | 3.3 mm | male | 14.2 (100 mN·m) | 16.2 | 21.2 | 28.8 |
  | 3.3 mm | female | 10.5 (74 mN·m) | 9.8 (69 mN·m) | 18.2 | 21.8 |
  | 6.4 mm | male | 33.3 | 36.6 | 54.8 | 67.2 |

  The 3.3 and 5.0 mm rows have no flanged values, so the PDF text gives four numbers per row. We read
  them as smooth L/T then knurled L/T, which matches the paper's text: "smallest ... smooth surface,
  14.2 in-oz in males and 9.8 in females". These are **maximal** voluntary torques, not comfortable ones.

**Sanity check [derived]:** crown torque of about 1 to 2 N·mm (section 2) ≪ 32 mN·m (MIL-STD) ≪ 69 to
155 mN·m (MVC at 3.3 to 5 mm). Winding a real watch is far below human limits.

---

## 7. Watch gear standards and open horology texts

| Doc | URL | sha256 | Size | Terms |
|---|---|---|---|---|
| **C. Saunier, *A Treatise on Modern Horology in Theory and Practice*, 1887** (Digital Library of India scan, IA) | https://archive.org/download/in.ernet.dli.2015.220719/2015.220719.A-Treatise_djvu.txt (PDF: `2015.220719.A-Treatise.pdf`, 86 MB) | txt `d00a3d7bef471f6ea4cc9e24d02f029823afba53eaa050fa0d938203ba705f2f` | 858 pp. | **[PD]** 1887 |
| **C. Saunier, ed. H. G. Abbott, *The Watchmakers' Hand Book*, 1892** (Project Gutenberg #76850) | https://www.gutenberg.org/cache/epub/76850/pg76850.txt | `e488d40d61d5239354c78b04714b5d11b0f09a9344c11c8a7fcb59a34638a770` | 885 kB | **[PD]** in the US; Gutenberg licence (keep its header, or strip the trademark) |
| **Grossmann 1905** | see 2 | | 294 pp. | [PD] |
| BS 978-2:1952 (cycloidal fine-pitch gears, module 0.07 to 1.0); NIHS 20-xx; NF S80-525 and NF S80-526 | catalogue pages only (STANDARDS.md 4.1) | — | — | paywalled; cite by title |

**What the open books give:**

- **Saunier 1887:**
  - the section "Keyless watches" (p. 796 ff.), with Patek & Philippe's, Lecoultre's and Audemars'
    mechanisms;
  - a long treatment of gearing: cycloidal and epicycloidal teeth, wheel and pinion proportions,
    depthing.
- **Saunier and Abbott 1892:**
  - workshop practice, including cutting keyless and ratchet teeth (§ 363, § 417);
  - a metals and alloys table (§ 121).
- **Grossmann 1905:**
  - gearing tables (the angle traversed by the pinion);
  - the coefficients of elasticity;
  - the mainspring torque law;
  - friction.

**Not found:** any public summary of BS 978-2's tooth tables. The NIHS norm list is public by title only.

---

## 8. Gaps: values no public document gives

1. **Tooth counts, modules and tooth forms of any real keyless works:** none published. ETA, Sellita,
   Miyota and TMI give names and part numbers only.
2. **Mainspring torque curves from a maker** (Générale Ressorts, Seiko and others): none. Only
   Grossmann's 1905 law and worked example (PD) and our derivation.
3. **The Générale Ressorts catalogue:** not public. Sizes come from resellers only, and Cousins blocks
   scripted access.
4. **Jewel tolerances and load ratings for watch jewels:** none from Seitz or another Swiss maker. Only
   Bird Precision's instrument-jewel tolerances.
5. **Stem thread pitch:** S 0.90 is published (Sellita) but its pitch (0.225 mm) is from one vendor
   [secondary]. The NIHS thread norms are paywalled.
6. **Click-spring and setting-lever-jumper forces, and crown push/pull forces:** none.
7. **Stem travel per calibre:** only Sellita (0.80 mm). ETA, Miyota and TMI give positions, not travel.
8. **Seiko 6R15, Seagull ST36 and an official SW210-1:** no maker technical document reachable.
9. **Comfortable crown winding torque:** none. Only maxima (MVC) and a knob-design maximum (MIL-STD,
   for knobs of 10 mm and up).

---

## 9. Scale: real size or 1.5×?

**What the task uses now** (`spikes/keyless/constants.py` and `PROMPT.md` on main):

- case Ø 17.4 mm and 6.8 mm deep (z -3.4 to 3.4);
- plates 0.6 mm thick, 5.2 mm apart;
- stem pull 0.9 mm;
- minute wheel module 0.2 (36 teeth);
- the step-by-step reference uses modules 0.15 and 0.2.

B's watch (`geometry/watch.py`): barrel 96 teeth at module 0.2 (pitch Ø 19.2 mm), case radius 20.7 mm
(Ø 41.4), `MIN_FEATURE = 0.2` mm.

**Comparison with the real documents:**

| Quantity | Task | Real | Ratio |
|---|---|---|---|
| Keyless case Ø | 17.4 mm | 7¾‴ ladies' calibre about 17.2 mm (as DS files note) | **1.0** |
| Keyless case Ø, against an 11½‴ | 17.4 mm | 25.6 to 26.0 mm | 0.7 |
| Total depth | 6.8 mm | 2824-2 4.60 mm; SW215-1 3.35 mm; 6497 4.50 mm (whole movements) | **about 1.5 to 2** |
| Stem pull | 0.9 mm | 0.80 mm (Sellita) | **1.1** |
| Keyless modules | 0.15 to 0.2 | not published (gap 1); watch modules 0.05 to 0.2, BS 978-2 starts at 0.07 [secondary] | probably **about 1.5 to 2** |
| B's case Ø | 41.4 mm | 2824 25.6; 6497 36.6 | 1.6 / 1.13 |

**Verdict: neither "1:1" nor "1.5×" holds alone.**

- The keyless spike's **plan view is real size** for a small calibre, and the stem pull is real.
- Its **depth and tooth sizes are about 1.5 to 2× real**.
- B's watch is about 1.6× a 2824 in plan.

**Which real data still fit:**

- **Scale-free data fit as they are:** crown turns per full wind (23 to 55), barrel turns (8), reserve
  (38 to 53 h), finger torque limits, material strength and modulus, friction coefficients.
- **Dimensional data fit only at 1:1:** S 0.90 stem, 0.80 mm travel, jewel hole and OD sizes, mainspring
  h × t × L × Ø, movement heights.
- **At 1.5×, a strength check is lenient.** For a given torque, bending stress scales as 1/s³, so a
  1.5× part is about 3.4× stronger than the real one. Real material limits only bite at 1:1.

**To run the keyless task at real scale** (all these constants go through "Proposed spec changes";
they are not changed here):

1. **Case depth:** bring the case depth to the real stack, about 4 to 4.6 mm, and plate thicknesses
   to real values.
2. **Supplied minute wheel:** use a real module, about 0.08 to 0.1 [unverified].
3. **PULL:** 0.80 (Sellita).
4. **Engine tolerances** that are absolute lengths or volumes scale down:
   - the overlap tolerance (2e-4 mm³) by about s³, to about 6e-5 at s = 1.5;
   - `PULL_STEP` 0.03 → 0.02;
   - `HOLD_SHIFT` 0.3 → 0.2;
   - `MAIN_TRY` 0.02 → 0.013;
   - `STILL_TOL` and the angle tolerances do not change.
5. **Meshes:** a module-0.08 tooth needs a finer tessellation, though not more triangles per tooth.
   manifold3d's precision (about 1e-6 of the bounding box) is ample. `MAX_TRIANGLES` may need raising
   for a 60-tooth crown wheel.
6. **B's `MIN_FEATURE = 0.2`** (printable) would have to drop to about 0.05 to 0.08 for real watch parts,
   which breaks the "printable demo part" story. Keep printing at 2:1 or 3:1 for the demo instead, and
   grade at 1:1.

---

## 10. Proposed Dockerfile snippet

**What it does:**

- fetches the chosen documents into `/app/datasheets` at build time;
- pins every file by sha256;
- tries the official URL, then the Wayback copy (only where we verified it is identical);
- **fails the build** if a file cannot be verified. Every run must see the same bytes; on failure, build
  the image with the synthesized `spikes/keyless/datasheets/` instead.

**What it leaves out:**

- Sellita SW200-1, which is marked confidential (1.2);
- HTML pages, whose bytes change between fetches.

```dockerfile
# --- real datasheets, fetched at build time; never committed (REAL_DATASHEETS.md) ---
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates poppler-utils \
 && rm -rf /var/lib/apt/lists/*
COPY datasheets.lock /tmp/datasheets.lock
RUN set -eu; mkdir -p /app/datasheets; cd /app/datasheets; \
    while read -r name sha url wb; do \
      case "$name" in ''|'#'*) continue;; esac; \
      ok=0; \
      for u in "$url" "$wb"; do \
        [ "$u" = "-" ] && continue; \
        if curl -fsSL --retry 3 --max-time 180 -A "Mozilla/5.0 (task-build)" -o "$name" "$u" \
           && echo "$sha  $name" | sha256sum -c - >/dev/null 2>&1; then ok=1; break; fi; \
      done; \
      [ "$ok" = 1 ] || { echo "datasheet $name failed verification" >&2; exit 1; }; \
      case "$name" in *.pdf) pdftotext -layout "$name" "${name%.pdf}.txt" || true;; esac; \
    done < /tmp/datasheets.lock; \
    rm /tmp/datasheets.lock; chmod -R a-w /app/datasheets
```

`datasheets.lock` has one line per file: `name sha256 url wayback-or-dash`. It is a proposal; the URLs
and hashes are as verified on 14 Nov 2026.

```text
# movements
eta_2824-2_CT.pdf d280c3f1b0cbaf2a84f999f96b53bbb3b28947fb307c225843cd6893cd548d56 https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1883 -
eta_2801-2_CT.pdf d93cfce3ca4fca17f751c82df4e4efc9f305fe924e3033caae96d25b018fbb92 https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1626 -
eta_6498-1_CT.pdf 0923e2aac216261626001d8f914081324b85f9931b5aa93f01acee04ddce91ca https://patrimoine.bourgognefranchecomte.fr/documents/ETA_6498-1.pdf -
eta_6497-2_CT.pdf 7d0dacebff6c95c5774705ed730b57dfaf3bfab638c8b654eb28f2b6d44fe3f5 https://patrimoine.bourgognefranchecomte.fr/documents/ETA_6497-2.pdf -
miyota_8215_spec.pdf bcb22d8e921b06165e67ffbbecfbcc444b8a67ccb4319d598c14bda6216418dc https://miyotamovement.com/uploads/product/product_8jT5DEdzRXAsaSN2Bu.pdf https://web.archive.org/web/20261003045553id_/https://miyotamovement.com/uploads/product/product_8jT5DEdzRXAsaSN2Bu.pdf
miyota_9015_spec.pdf 7192f8fccdc30b428315d234a9ca37479c26e7914466939b0870aeb56db48e28 https://miyotamovement.com/uploads/product/product_7ev6UD3QZ0FwfgH1kJ.pdf https://web.archive.org/web/20260828112428id_/https://miyotamovement.com/uploads/product/product_7ev6UD3QZ0FwfgH1kJ.pdf
miyota_9015_parts.pdf 7097238a181bb9fc1086937b6e4f82768b0ab22b7a06c8ac6dcb377bdc63e227 https://miyotamovement.com/uploads/product/product_6VYkM4Gnta0BQXiULu.pdf -
tmi_nh3_technical_guide.pdf 0cd2c8b82e392b6daed4306b4b679b97ff2b3d9cbcc9dcb75ccada806dd4a8b0 https://timemodule.com/upload/category/24/technical_guide/NH35_TG.pdf https://timemodule.com/upload/category/25/technical_guide/NH36_TG.pdf
# mainspring theory, friction, gearing (public domain)
grossmann_lessons_in_horology_1905.pdf a2d2500626c8903dfec6dd4fa315b99db3ec3f037c8ffc43790b0c90c75d6053 https://archive.org/download/lessonsinhorolog00gros/lessonsinhorolog00gros.pdf -
saunier_treatise_1887.txt d00a3d7bef471f6ea4cc9e24d02f029823afba53eaa050fa0d938203ba705f2f https://archive.org/download/in.ernet.dli.2015.220719/2015.220719.A-Treatise_djvu.txt -
lewis_friction_horology_1896.pdf 8f27f6f70d121b319fc329321ce5f6dccaab60cb83190614122ff7cd29900d13 https://archive.org/download/frictionlubricat00lewi/frictionlubricat00lewi.pdf -
# materials
wieland_cuzn39pb3_z32_z33.pdf 80ea72ebc943c442147728bb8e281bba5e4a276c44e5de0c09651c863850bb6d https://www.wieland.com/da/content/download/9842/file/Z32-Z33_EX_EN.pdf -
matthey_cuni18zn20.pdf 66e1f08bd4edd24812e2d43e7b0a1adff733603beb83b81f7184340b11fe7ba1 https://www.matthey.ch/fileadmin/user_upload/downloads/fichetechnique/EN/CuNi18Zn20_v22E.pdf -
alleima_20c_1.1274.pdf 7b8b5830d76d40aab5b35193ea3bd3b1e56cc7d868ce50745ca2c5727f2b3117 https://www.alleima.com/en/technical-center/material-datasheets/strip-steel/alleima-20c/?show=pdf -
jacques_allemann_20ap.pdf 68ea389af60893d12ba8e3db310cb1db92b243e1b4600f55982fe78516939234 https://www.jacques-allemann.com/media/cms/Legierungen%20/%20Tech-Sheets/JAS%20-%20Tech%20Sheet%20/%20Werkstoffe/jas-020-tech-sheet-20ap.pdf -
nivaflex_45_5.pdf dddc1ee277c758c79aa9355f5f76dd6088ca4cfd1d15482c02dca12fa9060aef https://www.cousinsuk.com/pdf/skus/9601_9596_nivaflex_45_5.pdf -
bird_ring_jewels.pdf 047989c069a0e844f33673fdcaf84547c6d5cc6882f11577d180dd31ac54ff41 https://catalog.birdprecision.com/Asset/Ring_jewel.pdf -
# human factors
mil-std-1472h.pdf 74ca9890986bd86d787a964cd2f37f101e1ec9c8c2087259abf1e11abdb96d65 https://everyspec.com/MIL-STD/MIL-STD-1400-1499/download.php?spec=MIL-STD-1472H.057041.pdf -
imrhan_2013_finger_torque.pdf 85d098471c0487e5eb11657fac71ba0ba637096429b2061041713bf0706f7f60 https://westpointpressjournals.westpoint.edu/index.php/iser/article/download/20/Imrhan/112 -
```

**Notes on the snippet:**

- **Sizes:**
  - total about 85 MB;
  - the ETA, MIL and Grossmann PDFs are 7 to 17 MB each;
  - `pdftotext` adds a `.txt` next to each PDF so the agent can read it with its own tools;
  - the Miyota drawings and the NH35 spec sheet are image-only, so they are left out.
- **The PD documents could be vendored instead of fetched:** Grossmann, Saunier, Lewis, MIL-STD-1472H,
  FAA, NACA. They are lawful to redistribute. This brief says not to commit PDFs, so that would be a
  separate team decision (Git LFS or a release asset).
- **Leakage check:** some of these documents name the keyless parts (the ETA, Miyota and TMI parts
  lists). `TASK_DOCS_TEMPLATE.md` forbids naming the mechanisms the agent should choose. Shipping a real
  parts list is how a real engineer works, but it is a method hint by that template's rule. That needs a
  human decision before these go into `/app`.
- **Reproducibility:** the build depends on 12 third-party hosts.
  - ETA's shop, TMI and Boley have no verified fallback.
  - A changed file fails the hash check, which is safe but blocks the build.
  - Build once, and push the image to the registry Harbor pulls from. That is internal storage, not
    redistribution, but it is a team call.
