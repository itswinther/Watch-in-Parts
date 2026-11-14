# Valtorre Microtechnique SA: Crowns and winding stems, demonstration-scale series

**Demonstration-scale series, scale 1.617:1 to an 11½‴ calibre (s = 1.617).**

| Document | Revision | Date | Status |
|---|---|---|---|
| VM-DS-401 | D | 2026-11-14 | Released |

> **About this document.** Valtorre Microtechnique SA, demonstration series.
>
> - **What is real:** the 1:1 dimensions are those of real parts and documents, cited per row. The 1:1
>   crown withstand ratings (section 5a) are the test values of real watch specifications.
> - **What this series changes:** it enlarges every length by s = 1.617.[^s] **Use the scaled columns.**
> - **What is calculated:** the stem torque ratings (section 5), and the scaled crown withstand ratings
>   (section 5a).

## 1. Scope

This sheet covers crowns and winding stems for two-position keyless works (winding, then hand
setting).

## 2. Ordering codes

- **Crowns:** `VM-CR-<1:1 Ø in 1/100 mm>-<form>-DS`.
- **Stems:** `VM-ST-090-<1:1 square A/F in 1/100 mm>-DS`.

## 3. Crowns (Table 1)

| Ordering code | 1:1 crown Ø (mm) | Source | **Crown Ø (mm)**[^s] | Form |
|---|---|---|---|---|
| VM-CR-300-S-DS | 3.00 | [^p300] | 4.85 | Square |
| VM-CR-400-R-DS | 4.0 | [^ess] | 6.47 | Round |
| VM-CR-500-R-DS | 5.00 | [^p500] | 8.09 | Round |
| VM-CR-510-R-DS | 5.10 | [^p510] | 8.25 | Round |
| VM-CR-520-T10-DS | 5.20 | [^p520] | 8.41 | 10-sided |
| VM-CR-600-R-DS | 6.00 | [^p600] | 9.70 | Round |
| VM-CR-700-R-DS | 7.0 | [^ess] | 11.32 | Round |

- **Thread:** every crown is threaded to fit the stem in section 4: S 0.90 at 1:1, **Ø 1.455 mm** in this
  series.[^ess][^sel][^s]
- **Case tube:** Ø 2.0 or 2.5 mm at 1:1, which is **3.23 or 4.04 mm** in this series.[^ess][^s]
- **Tolerances:** not published by the cited sellers.

For the finger torque available on each crown diameter, see VM-AN-501. Finger torque does not scale.

## 4. Winding stem (Table 2)

| Quantity | 1:1 value | Source | **This series**[^s] |
|---|---|---|---|
| Thread | S 0.90 (Ø 0.90 mm) | [^sel] | Ø 1.455 mm |
| Length, normal | 15.50 mm | [^sel] | 25.07 mm |
| Stem travel between adjacent positions | 0.80 mm | [^sel] | **1.29 mm** |
| Gap from crown to case middle | at most 0.1 mm | [^sel] | at most 0.16 mm |

- **Positions:** a no-date calibre has two positions, winding and setting. Date calibres add a quick-set
  position.[^eterna]
- **Backward turning:** the sliding pinion's Breguet teeth slip, so nothing reaches the barrel or the
  click.[^sjx]
- **Travel tolerance:** not published.

## 5. Ratings: absolute maximum torque on the stem square (Table 3, calculated)

The stem fails in torsion at the square that drives the sliding pinion. The maximum shear stress in a
solid square of side a under a torque T is τ = T/(0.208·a³).[^uok] The steel yields in shear at
τ_y = Rp/√3 (von Mises).[^vm] With Rp = 1450 MPa, the lowest proof strength of the steel strip in AD-DS-201,[^alleima]
τ_y = 837 MPa.

| Ordering code | 1:1 square A/F (mm) | **Square A/F a (mm)**[^s] | **T at shear yield (N·mm)**[^d1] | **Recommended max., S = 2 (N·mm)**[^d1] |
|---|---|---|---|---|
| VM-ST-090-050-DS | 0.50 | 0.809 | 92.1 | 46.0 |
| VM-ST-090-060-DS | 0.60 | 0.970 | 159.1 | 79.5 |
| VM-ST-090-070-DS | 0.70 | 1.132 | 252.6 | 126.3 |

For another size, T_yield = 0.208·a³·837 N·mm, with a in mm. The rating scales with s³, the same as the
torques it carries.

**Torque at the crown thread:** not published.

## 5a. Ratings: crown withstand (Table 4)

A crown and keyless works of this series withstand the following without damage. The 1:1 values are the
test values of real wrist-watch specifications. They are mechanical ratings, so this series scales
forces with s² = 2.615 and torques with s³ = 4.229.[^d2]

| Rating | 1:1 value | Source | **This series**[^d2] |
|---|---|---|---|
| Axial pull on the crown while it moves from the running (winding) position to the setting position | 22.2 ± 1.1 N (5 ± 0.25 lb) | [^mil46374] | **58.1 ± 2.9 N** |
| Side force on the crown, perpendicular to the stem, held for 10 min | 5 N | [^iso6425] | **13.1 N** |
| Torque at the crown, turned forward against a fully wound mainspring | 42.4 ± 3.5 mN·m (6 ± 0.5 in-oz) | [^mil46374][^gg113] | **179.3 ± 14.8 N·mm** |

- These are withstand (survival) ratings, not operating forces or torques.
- **Operating force to move the stem between positions:** not published.
- For the torque a person applies to the crown, which does not scale, see VM-AN-501.

## 6. Handling

Screw the crown fully home on the thread before cutting the stem to length.

## Sources

[^s]: Scale s = 41.4 mm / 25.60 mm = 1.617. 41.4 mm is the case diameter of the demonstration movement this series is made for; 25.60 mm is the ETA 2824-2 (11½‴), https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1883. Scaled length = 1:1 length × 1.617.
[^sel]: Sellita, SW200-1 Documentation technique, rev 07 (2024): stem thread S 0.90; stem travel ("course de la tige") 0.80 mm; stem length 15.50 mm; crown-to-case gap ≤ 0.1 mm. https://www.sellita.ch/scripts/calibres/images/DocTec_SW200-1_7.pdf
[^ess]: Esslinger, crown assortment 83-015-9: Ø 4.0 to 7.0 mm, 0.90 mm thread, 2.0 and 2.5 mm tubes, https://www.esslinger.com/double-o-ring-waterproof-watch-crown-assortment-83-015-9-stainless-steel-12-pieces/
[^p300]: Perrin, crown, tap 0.90 mm, square, Ø 3.00 mm, https://perrinwatchparts.com/collections/watch-case-parts-for-omega/products/omega-crown-waterproof-tap-090-mm-square-diameter-300-mm-see-all-case-numbers-in-description
[^p500]: Perrin, crown TI-TIS21, fits stem tap 0.90 mm, Ø 5.00 mm, https://perrinwatchparts.com/en-us/products/tissot-crown-mido-style-ti-tis21-steel-medium-pipe-fits-a-stem-tap-090-mm
[^p510]: Perrin, crown, tap 0.90 mm, Ø 5.10 mm, https://perrinwatchparts.com/products/omega-crown-waterproof-tap-090-mm-steel-diameter-510-mm-case-numbers-1660064-1660066-1660108-1660144-1660146-1660175-5660016
[^p520]: Perrin, crown, tap 0.90 mm, 10 sides, Ø 5.20 mm, https://perrinwatchparts.com/en-us/products/omega-crown-waterproof-tap-090-mm-steel-10-sides-diameter-520-mm-see-all-case-numbers-in-description
[^p600]: Perrin, crown, tap 0.90 mm, Ø 6.00 mm, https://perrinwatchparts.com/products/omega-crown-waterproof-tap-090-mm-steel-diameter-600-mm-see-all-case-numbers-in-description
[^sjx]: Keyless works explained (Breguet teeth slip backward), https://watchesbysjx.com/2026/08/keyless-works-explained.html
[^eterna]: ETA 2824-2 (Eterna-cased) manual, positions, https://www.manualslib.fr/manual/627394/Eterna-Eta-2824-2.html?page=5
[^uok]: Torsion of a square section, τ_max = T/(0.208·a³), https://prof.uok.ac.ir/Ka.Karami/Courses/Mechanic-of-Material-II/06-Torsion-of-Noncircular-Members.pdf
[^vm]: von Mises shear yield σ_y/√3, https://en.wikipedia.org/wiki/Von_Mises_yield_criterion
[^alleima]: Alleima 20C, proof strength 1450 MPa (1.000 to < 1.575 mm), https://alleima.com/en/technical-center/material-datasheets/strip-steel/alleima-20c
[^mil46374]: MIL-W-46374F, *Watch, Wrist, General Purpose* (US Army), §3.3.6 (p. 8, test §4.7.13): the crown withstands a pull of 5 ± 0.25 lb from the running to the setting position; §3.3.7 (p. 8, test §4.7.12): a fully wound watch is not damaged by 6 ± 0.5 in-oz at the crown. US government work, public domain. https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-W/download.php?spec=MIL-W-46374F.021322.PDF ; units: 1 lbf = 4.448 N (https://en.wikipedia.org/wiki/Pound_(force)), 1 in-oz = 7.06 N·mm (https://en.wikipedia.org/wiki/Ounce-force)
[^gg113]: GG-W-113A (1967), §3.9.3: the same 6 ± ½ oz-in at the crown without damage. US government work, public domain. https://everyspec.com/FED_SPECS/G/download.php?spec=GG-W-113A.022400.PDF
[^iso6425]: ISO 6425:2018, *Divers' watches*, §4.7.2: a force of 5 N applied perpendicular to the crown for 10 min (under overpressure). https://www.iso.org/standard/66517.html
[^d2]: Not published at this scale; derived as the 1:1 value × s² = 2.615 for forces and × s³ = 4.229 for torques (geometric similarity, same materials: the stresses are unchanged). Tolerances scale with the value.
[^d1]: Not published; calculated as T = 0.208·a³·1450/√3 with the scaled a ([^uok], [^vm], [^alleima]). The recommended value divides by S = 2 (https://danotes.mech.uwa.edu.au/SSS/safety/safety.html).
