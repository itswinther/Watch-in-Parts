# Valtorre Microtechnique SA: Crowns and winding stems

| Document | Revision | Date | Status |
|---|---|---|---|
| VM-DS-401 | B | 2026-11-14 | Released |

> **About this document.** Valtorre Microtechnique SA is a fictional supplier, used for this exercise
> only. The crown sizes and thread are those of real catalogue items, cited per row. The stem torque
> ratings are **calculated**, and their footnotes give the method and inputs.

## 1. Scope

This sheet covers:

- crowns with a Ø 0.90 mm female thread;
- winding stems with a Ø 0.90 mm thread, as used in two-position (winding and setting) keyless works.

All data are full scale (1:1).

## 2. Ordering codes

- **Crowns:** `VM-CR-<Ø in 1/100 mm>-<form>`, where the form is R (round), S (square) or
  T10 (10-sided).
- **Stems:** `VM-ST-090-<square A/F in 1/100 mm>`. The movement maker cuts the stem to length when
  casing.

## 3. Crowns (Table 1)

| Ordering code | Crown Ø (mm) | Form | Thread Ø (mm) | Case tube Ø (mm) | Source |
|---|---|---|---|---|---|
| VM-CR-300-S | 3.00 | Square | 0.90 | not stated | [^p300] |
| VM-CR-400-R | 4.0 | Round | 0.90 | 2.0 or 2.5 | [^ess] |
| VM-CR-500-R | 5.00 | Round | 0.90 | not stated | [^p500] |
| VM-CR-510-R | 5.10 | Round | 0.90 | not stated | [^p510] |
| VM-CR-520-T10 | 5.20 | 10-sided | 0.90 | not stated | [^p520] |
| VM-CR-600-R | 6.00 | Round | 0.90 | not stated | [^p600] |
| VM-CR-700-R | 7.0 | Round | 0.90 | 2.0 or 2.5 | [^ess] |

The 4.0 and 7.0 mm sizes are the ends of a 4.0 to 7.0 mm assortment for 2.0 and 2.5 mm tubes.[^ess]

**Tolerances:** not published by the cited sellers.

For the finger torque available on each crown diameter, see VM-AN-501.

## 4. Stem functions and positions

| Position | Function | Stem travel from position 1 |
|---|---|---|
| 1 (pushed in) | Winding | 0 |
| 2 (pulled out) | Hand setting | about 1 mm[^sjx] |

- **Positions:** a no-date calibre has two crown positions, winding and setting.[^eterna] Date calibres
  add a quick-set position between them.[^eterna]
- **Forward winding:** the sliding pinion's ratchet (Breguet) teeth drive the winding pinion.
- **Backward turning:** the same teeth slip over each other, so nothing reaches the barrel or the
  click.[^sjx]
- **Travel tolerance:** not published.

## 5. Ratings

### 5.1 Absolute maximum torque on the stem square (Table 2, calculated)

The stem fails in torsion at its smallest section, the square that drives the sliding pinion. The
maximum shear stress in a solid square of side a under a torque T is τ = T/(0.208·a³).[^uok] The steel
yields in shear at τ_y = Rp/√3 (von Mises).[^vm]

The ratings use Rp = 1450 MPa, the lowest proof strength listed for hardened and tempered 1 % C steel
in AD-DS-201.[^alleima] That gives τ_y = 837 MPa.

| Ordering code | Square A/F a (mm) | T at shear yield (N·mm) | Recommended max., S = 2 (N·mm) |
|---|---|---|---|
| VM-ST-090-050 | 0.50 | 21.8[^d1] | 10.9[^d1] |
| VM-ST-090-060 | 0.60 | 37.6[^d1] | 18.8[^d1] |
| VM-ST-090-070 | 0.70 | 59.7[^d1] | 29.9[^d1] |

For another square size, T_yield = 0.208·a³·837 N·mm, with a in mm.

### 5.2 Torque at the crown thread

Not published by the cited sellers.

## 6. Handling

- Screw the crown fully home on the thread before the stem is cut to length.

## Sources

[^ess]: Esslinger, stainless steel crown assortment 83-015-9: Ø 4.0 to 7.0 mm, 0.90 mm thread, 2.0 and 2.5 mm tube openings, https://www.esslinger.com/double-o-ring-waterproof-watch-crown-assortment-83-015-9-stainless-steel-12-pieces/
[^p300]: Perrin, crown, tap 0.90 mm, square, Ø 3.00 mm, https://perrinwatchparts.com/collections/watch-case-parts-for-omega/products/omega-crown-waterproof-tap-090-mm-square-diameter-300-mm-see-all-case-numbers-in-description
[^p500]: Perrin, crown TI-TIS21, steel, medium pipe, fits a stem tap 0.90 mm, Ø 5.00 mm, https://perrinwatchparts.com/en-us/products/tissot-crown-mido-style-ti-tis21-steel-medium-pipe-fits-a-stem-tap-090-mm
[^p510]: Perrin, crown, tap 0.90 mm, steel, Ø 5.10 mm, https://perrinwatchparts.com/products/omega-crown-waterproof-tap-090-mm-steel-diameter-510-mm-case-numbers-1660064-1660066-1660108-1660144-1660146-1660175-5660016
[^p520]: Perrin, crown, tap 0.90 mm, steel, 10 sides, Ø 5.20 mm, https://perrinwatchparts.com/en-us/products/omega-crown-waterproof-tap-090-mm-steel-10-sides-diameter-520-mm-see-all-case-numbers-in-description
[^p600]: Perrin, crown, tap 0.90 mm, steel, Ø 6.00 mm, https://perrinwatchparts.com/products/omega-crown-waterproof-tap-090-mm-steel-diameter-600-mm-see-all-case-numbers-in-description
[^sjx]: Keyless works explained: stem travel about 1 mm between positions; the Breguet teeth slip when turned backward. https://watchesbysjx.com/2026/08/keyless-works-explained.html
[^eterna]: ETA 2824-2 (Eterna-cased) manual: position A winding, position B setting; date versions add a quick-set position. https://www.manualslib.fr/manual/627394/Eterna-Eta-2824-2.html?page=5
[^uok]: Torsion of non-circular members: square section, τ_max = T/(0.208·a³) (coefficient 0.208 for b/a = 1), https://prof.uok.ac.ir/Ka.Karami/Courses/Mechanic-of-Material-II/06-Torsion-of-Noncircular-Members.pdf
[^vm]: von Mises criterion: the shear yield stress is σ_y/√3, https://en.wikipedia.org/wiki/Von_Mises_yield_criterion
[^alleima]: Alleima 20C strip, proof strength 1450 MPa (1.000 to < 1.575 mm), the lowest row, https://alleima.com/en/technical-center/material-datasheets/strip-steel/alleima-20c
[^d1]: Not published; calculated as T = 0.208·a³·(1450/√3), with the formula from [^uok] and [^vm] and the input from [^alleima]. The recommended value divides by S = 2, the upper end of the 1.5 to 2 tier at https://danotes.mech.uwa.edu.au/SSS/safety/safety.html.
