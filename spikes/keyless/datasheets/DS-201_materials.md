# Aciers Duval SA: Materials for watch movement parts

| Document | Revision | Date | Status |
|---|---|---|---|
| AD-DS-201 | C | 2026-11-14 | Released |

**Demonstration-scale series, scale 1.617:1 to an 11½‴ calibre (s = 1.617).** Every value on this
sheet is a material property and does not depend on size. It applies unchanged at any scale.

> **About this document.** Aciers Duval SA, demonstration series. Every
> property below comes from the cited producer or reference datasheet. The design allowables in
> section 8 are calculated from those properties, as their footnotes state.

## 1. Scope

This sheet covers four groups of material:

- free-cutting brass, for wheels, bridges and plates;
- hardened and tempered 1 % carbon steel, for springs, levers and pinions;
- a cobalt-base spring alloy, for mainsprings;
- synthetic corundum (ruby or sapphire), for jewel bearings.

It also gives friction coefficients and accepted safety factors.

## 2. Ordering codes

| Code | Material | Form |
|---|---|---|
| AD-CW614N | Brass CuZn39Pb3 (EN CW614N) | Rod or bar |
| AD-C100-HT | Carbon steel, 1.00 % C, hardened and tempered | Strip |
| AD-C100S | Carbon steel C100S (1.1274) | Strip, quenched and tempered |
| AD-CoNiCr-45 | Co-Ni-Cr age-hardening spring alloy (Nivaflex 45/5 type) | Wire or strip |
| AD-AL2O3 | Synthetic corundum (ruby or sapphire) | Jewel blanks |

## 3. Brass CuZn39Pb3 (CW614N), rod to EN 12164

| Property | Value | Source |
|---|---|---|
| Tensile strength Rm | 360 to 500 MPa | [^aalco] |
| Proof stress Rp0.2 | 230 to 350 MPa | [^aalco] |
| Rp0.2 by temper, R430 / R500 (rod) | 220 / 350 MPa (R360: not stated) | [^wie] |
| Rm by temper, R360 / R430 / R500 | 360 / 430 / 500 MPa | [^wie] |
| Modulus of elasticity E | 96 GPa | [^wie] |
| Density | 8.46 g/cm³ | [^wie] |
| Elongation A | 5 to 20 % | [^aalco] |
| Hardness | 90 to 160 HB | [^aalco] |
| Density | 8.47 g/cm³ | [^aalco] |
| Modulus of elasticity E | 97 GPa | [^aalco] |

The supplier's values are for rod 6 to 80 mm in diameter (5 to 60 mm across flats). They vary with
temper, product and size, and are indicative only.[^aalco] Use the **lowest published proof stress,
220 MPa** (Wieland R430[^wie]), for design unless a mill certificate states otherwise.

## 4. Carbon steel, 1.00 % C, hardened and tempered strip (AD-C100-HT)

**Nominal composition:** C 1.00 %, Si 0.25 %, Mn 0.45 %.[^alleima] **Density:** 7.85 g/cm³.[^alleima]

| Thickness (mm) | Tensile strength Rm (MPa) | Proof strength (MPa) |
|---|---|---|
| < 0.125 | 2100 | 1900 |
| 0.175 to < 0.225 | 2000 | 1800 |
| 0.275 to < 0.375 | 1900 | 1700 |
| 0.475 to < 0.625 | 1750 | 1600 |
| 0.825 to < 1.000 | 1650 | 1500 |
| 1.000 to < 1.575 | 1600 | 1450 |

Selected rows; all are nominal values at 20 °C.[^alleima] The source's modulus of elasticity is not stated. Use
the C100S value below.

## 5. Carbon steel C100S (1.1274), quenched and tempered, to EN 10132-4 [secondary source]

| Property | Value | Source |
|---|---|---|
| C | 0.95 to 1.05 % | [^c100s] |
| Si | 0.15 to 0.35 % | [^c100s] |
| Mn | 0.30 to 0.60 % | [^c100s] |
| Tensile strength Rm | 1200 to 2100 MPa | [^c100s] |
| Hardness | 370 to 630 HV (38.5 to 57 HRC) | [^c100s] |
| Modulus of elasticity E | 212 GPa | [^c100s] |
| Density | 7.8 g/cm³ | [^c100s] |

The source states no proof stress for this condition.

## 6. Other materials

**Co-Ni-Cr spring alloy, Nivaflex 45/5 type (AD-CoNiCr-45).** Composition, in mass %: Co 45, Ni 21,
Cr 18, Fe 5, W 4, Mo 4, Ti 1, Be 0.2.[^vac]

| Cold work | Rm before / after aging (MPa) | Rp0.2 before / after aging (MPa) | HV after aging |
|---|---|---|---|
| 50 % | 1835 / 2300 | 1470 / 1840 | 675 |
| 70 % | 2115 / 2695 | 1690 / 2155 | 750 |
| 90 % | 2395 / 3095 | 1915 / 2475 | 830 |

Aging is 2 h at 550 °C. Other properties: E 220 GPa, G 90 GPa, density 8.5 g/cm³, non-magnetic.[^vac]
These are wire data.

**Synthetic corundum (ruby or sapphire), AD-AL2O3 [secondary sources]:**

| Property | Value | Source |
|---|---|---|
| Compressive strength | 2700 MPa | [^mif] |
| Compressive strength | about 2400 MPa (350,000 psi) | [^holo] |
| Flexural strength | 1090 MPa | [^mif] |
| Modulus of rupture | 460 to 655 MPa (67,000 to 95,000 psi) | [^holo] |
| Hardness | 1860 HK | [^mif] |
| Hardness | Mohs 9 | [^bird] |
| Density | 4.0 g/cm³ | [^mif] |

The sources disagree by about a factor of two on flexural strength. Use the lower value.

## 7. Friction coefficients (Table 7)

| Pair | Condition | Static μs | Sliding μk | Source |
|---|---|---|---|---|
| Brass on steel | Clean and dry | 0.51 | 0.44 | [^etb] |
| Brass on steel | Greased | 0.19 (type not stated) | – | [^etb] |
| Steel on steel | Clean and dry | 0.5 to 0.8 | 0.42 | [^etb] |
| Steel on steel | Greased | 0.16 (type not stated) | – | [^etb] |
| Steel on ruby or sapphire | Dry | – | about 0.14 | [^bird] |
| Sapphire on sapphire | Clean and dry | 0.2 (type not stated) | – | [^etb] |
| Metal on metal (watch work) | – | 0.15 to 0.17 | – | [^gro] |
| Metal on precious stones (watch work) | – | 0.15 | – | [^gro] |

## 8. Safety factors and design allowables

**Basis of the allowable stress:** yield strength for ductile materials, ultimate strength for brittle
materials.[^ee]

**Recommended safety factors, based on yield (Juvinall and Marshek):**[^uwa]

| Situation | Safety factor S |
|---|---|
| Exceptionally reliable materials, controllable conditions, loads and stresses known with certainty | 1.25 to 1.5 |
| Well-known materials, reasonably constant environment, loads and stresses readily determined | 1.5 to 2 |
| Average materials, ordinary environments | 2 to 2.5 |
| Less-tried materials, or brittle materials under average conditions | 2.5 to 3 |
| Untried materials, or uncertain environment or stresses | 3 to 4 |

**Design allowables at the upper end of the matching tier (calculated):**

| Material | Basis | S | Allowable (MPa) |
|---|---|---|---|
| Brass CW614N | Rp0.2 min 220 MPa[^wie] | 2 | 110[^d1] |
| Steel AD-C100-HT, < 1.000 mm | Proof min 1500 MPa[^alleima] | 2 | 750[^d1] |
| Steel AD-C100-HT, 1.000 to < 1.575 mm | Proof 1450 MPa[^alleima] | 2 | 725[^d1] |
| Corundum, compressive | 2700 MPa[^mif] | 3 | 900[^d1] |

## Notes

1. **Watch parts are smaller than the stock tested.** Thin turned and stamped parts can differ from the
   test-bar values. Where the strength matters, ask for a certificate.
2. **Magnetism and corrosion.** Carbon steels are magnetic and corrosion-sensitive. The Co-Ni-Cr alloy is
   non-magnetic.[^vac]

## Sources

[^aalco]: Aalco, CW614N brass rod datasheet (EN 12164:2011): Rm 360 to 500 MPa, proof 230 to 350 MPa, A 5 to 20 %, 90 to 160 HB, 8.47 g/cm³, E 97 GPa. https://www.aalco.co.uk/datasheets/Copper-and-Copper-Alloys-CW614N-Brass-Rod_31.ashx
[^alleima]: Alleima 20C, hardened and tempered carbon steel strip datasheet, https://alleima.com/en/technical-center/material-datasheets/strip-steel/alleima-20c
[^wie]: Wieland, Z32/Z33 CuZn39Pb3 (CW614N) datasheet: E 96 GPa; density 8.46 g/cm³; rod R360/R430/R500, Rm 360/430/500 MPa, Rp0.2 –/220/350 MPa. https://www.wieland.com/da/content/download/9842/file/Z32-Z33_EX_EN.pdf
[^gro]: J. Grossmann, *Lessons in Horology* (1905), art. 335, friction table (public domain), https://archive.org/download/lessonsinhorolog00gros/lessonsinhorolog00gros_djvu.txt
[^c100s]: EN 10132-4 C100S quenched and tempered (secondary compilation), https://www.mfgrobots.com/Article/material/metal/37153.html
[^vac]: VACUUMSCHMELZE, NIVAFLEX 45/5 alloy information (2008), https://www.cousinsuk.com/pdf/skus/9601_9596_nivaflex_45_5.pdf
[^mif]: Synthetic sapphire properties (secondary), https://makeitfrom.com/material-properties/Synthetic-Sapphire
[^holo]: Ruby properties (secondary), https://holowiki.org/wiki/Ruby
[^bird]: Bird Precision, Ring Jewel Bearings: Mohs 9; sliding friction against steel about 0.14 (from Seitz's guide for users of synthetic jewels). https://catalog.birdprecision.com/Asset/Ring_jewel.pdf
[^etb]: Engineering ToolBox, friction coefficients, https://engineeringtoolbox.com/friction-coefficients-d_778.html
[^ee]: Engineers Edge, factor of safety review ("ductile materials use yield strength", "brittle materials use ultimate strength"), https://engineersedge.com/analysis/factor-of-safety-review.htm
[^uwa]: Recommended safety factors after Juvinall and Marshek, based on yield, https://danotes.mech.uwa.edu.au/SSS/safety/safety.html
[^d1]: Calculated: allowable = basis strength / S. The basis is from the cited row and S from [^uwa]: tier "1.5 to 2" for brass and steel, tier "2.5 to 3" for brittle corundum.
