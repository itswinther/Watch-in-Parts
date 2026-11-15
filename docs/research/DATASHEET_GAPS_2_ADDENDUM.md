# Addendum to DATASHEET_GAPS_2.md: crown torque and force (gap 6), Seiko 6R15 and Seagull ST36 (gap 8)

From the sub-search that reported after DATASHEET_GAPS_2.md was pushed (14 Nov, workstream A). In the
"Status" column, "read" means the primary text was read (for scans, from the page images; OCR misread
"6±0.5" as "60.5"), and "snippet" means a search summary only. Files were downloaded in Docker to scratch
only; none are in the repo.

## Gap 6: crown torque and force

| Value | Source | Status | Licence |
|---|---|---|---|
| A fully wound watch is not damaged by **6 ± 0.5 in-oz = 42.4 ± 3.5 mN·m** at the crown | MIL-W-46374F §3.3.7 and §4.7.12 (p.8, p.20), https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-W/download.php?spec=MIL-W-46374F.021322.PDF | read | public domain (US government) |
| The same: 6 ± ½ oz-in | GG-W-113A §3.9.3 (1967), https://everyspec.com/FED_SPECS/G/download.php?spec=GG-W-113A.022400.PDF | read | public domain |
| "The winding operation shall be smooth without excessive torque" (no number) | MIL-W-46374F §4.7.11 | read | public domain |
| The crown withstands a **pull of 5 ± 0.25 lb = 22.2 ± 1.1 N** from running to set | MIL-W-46374F §3.3.6, §4.7.13 | read | public domain |
| Crown back to the winding position: the minute hand jumps at most one tip width; pulling to set stops the movement (hack) | MIL-W-46374F §3.3.6.1, §3.2.3.3.1 | read | public domain |
| Movement Ø 23.7 to 26.0 mm; at least 36 h; at least 15 jewels; crown Ø 5.6 mm, straight knurl 1.6 mm | MIL-W-46374F §3.2.3.2.1.1, §3.2.3.2.2, Fig. 3 | read | public domain |
| The current revision (G, 1999) dropped the torque and pull numbers; use F and GG-W-113A for values | MIL-PRF-46374G, https://chrononautix.com/wp-content/uploads/2022/03/Mil-PRF-46374G.pdf | read | public domain |
| Motorised crown-winder torque limits **typically 10 to 50 mN·m** at full wind | Omega US9244437B2, https://patents.google.com/patent/US9244437B2/en | read via a fetch summary | US patent text, public domain |
| Cannon-pinion friction **at least 1.8 mN·m, nominal 2.0 (σ 0.20)**, in a high-friction design | Rolex US11256216B2, https://patents.google.com/patent/US11256216B2/en (claim 19) | read | public domain |
| A hand-setting coupling flange at about 0.8 N·mm | Breguet/Swatch US12554227 | snippet | public domain (unverified) |
| 5 N on the crown, perpendicular, for 10 min, under overpressure | ISO 6425:2018 §4.7.2 (iTeh preview) | read | ISO copyright: cite only |
| 5 N on the crown at 10 cm for 5 min | ISO 2281:1990 §6.2.4 (sample) | read | ISO copyright: cite only. Superseded by ISO 22810:2010, whose text was not seen |
| Ratchet-wheel screw tightening torque 250 g·cm (about 24.5 mN·m) | Seiko 6R15B technical guide p.12 | read | Seiko copyright: cite only |

**Not found anywhere:** a measured comfortable winding torque for real watches; a "comfortable = X % of
maximum" rule. One forum post gives barrel torques (2824 about 12 N·mm, 6497 over 20 N·mm); unverified, don't
cite.

**Recommendation:**
- crown torque limit at full wind = **42 mN·m**, a withstand-without-damage limit, not a comfort level (MIL-W-46374F, GG-W-113A; Omega's 10 to 50 mN·m brackets it). It sits above MIL-STD-1472H's 32 mN·m knob maximum;
- crown pull **22.2 N**;
- crown side force **5 N** (ISO 6425, link only);
- cannon-pinion slip about **2.0 mN·m** (Rolex, labelled high-friction).

## Gap 8: Seiko 6R15 and Seagull ST36

- **Seiko 6R15:** all maker documents, Seiko copyright, link only.
  - [Cousins 6R15C/D technical guide](https://www.cousinsuk.com/pdf/categories/8955_pao024_14267_191030121314_1_6r15cd.pdf): Ø 27.4 mm outside, 27.0 mm casing, height 5.25 mm, 23 jewels, 21,600 vph, lift angle 53°.
    - Reserve "approximately 50 h", but its p.18 duration test says about 41 h.
    - Crown: in = manual winding (clockwise only); 1st click = date (counter-clockwise); 2nd = time with stop seconds.
    - Keyless part codes: stem, winding pinion 0283 020, clutch wheel 0282 183, setting lever 0383 185, yoke 0384 183, jumper 0388 177, click 0381 004, ratchet wheel 0285 051.
  - [Boley 6R15B mirror](https://boley.de/downloads/c6941cc257f2415f8f8c5a0e532f807f/HATTORY-SEIKO-6R15.pdf): the same dimensions.
  - [Owner's instructions](https://api.seikoboutique.hu/Instructions/6R15D_EN.pdf): "turn the crown approximately 20 times to start the watch". The full-wind turn count is not stated anywhere.
- **Seagull ST36/ST3600:** no official document found (seagullwatch.com was down). Secondary only:
  - 36.6 mm, 4.5 mm, 17 jewels, 21,600 vph, an ETA/Unitas 6497 clone;
  - reserve stated as anything from over 40 h to 48 h.

  Use the ETA 6497 documents instead.

## What this changes

- **DS-401 and DS-501:** add 42 mN·m, 22.2 N and 5 N with these sources. Keep MIL-STD-1472H's 32 mN·m as the
  design maximum for a comfortable knob, and 42 mN·m as the no-damage limit.
- **Parts lists such as the 6R15's keyless codes** name the solution's parts. Per the 14:20 decision they stay
  out of /app.
