# Valtorre Microtechnique SA: Mainsprings for small-calibre barrels

| Document | Revision | Date | Status |
|---|---|---|---|
| VM-DS-101 | C | 2026-11-14 | Released |

> **About this document.** Valtorre Microtechnique SA is a fictional supplier, used for this exercise only.
> Each strip size in Table 1 is a real catalogue item, cited row by row. No maker publishes torque or
> turns for these springs, so every performance figure in Tables 2 to 4 is **calculated, not measured**.
> Note 4 gives the method and its sources.

## 1. Scope

This sheet covers mainsprings for barrels of 7.0 to 10.5 mm inner diameter.[^rdb] Such barrels fit
hand-wound and automatic movements of about 7¾‴ (Ø 17.2 mm, for example ETA 2671[^eta2671]) up to
11½‴ (Ø 25.6 mm[^eta2824]). One ligne (‴) is 2.2558 mm.[^ligne] All data are full scale (1:1).

Two end types are supplied:

- **M (manual):** a fixed outer end. Winding stops when the spring is fully wound, and the click must
  then hold the full torque.
- **A (automatic):** a slipping bridle. The bridle slips in the barrel once the spring is fully wound.

## 2. Ordering code

`VM-MS-<end>-<h>-<t>-<L>-<D>`, where:

- `end` is M or A;
- `h` is the height in 1/100 mm;
- `t` is the thickness in 1/1000 mm;
- `L` is the length in mm;
- `D` is the barrel inner diameter in 1/10 mm.

Example: `VM-MS-A-145-085-240-75` is a 1.45 × 0.085 × 240 mm spring with a bridle, for a barrel of
Ø 7.5 mm.

## 3. Dimensions (Table 1)

| Var. | Ordering code | End | Height h (mm) | Thickness t (mm) | Length L (mm) | Barrel inner Ø D (mm) | Source |
|---|---|---|---|---|---|---|---|
| A | VM-MS-M-090-080-240-70 | M | 0.90 | 0.080 | 240 | 7.0 | [^rA] |
| B | VM-MS-M-070-080-355-75 | M | 0.70 | 0.080 | 355 | 7.5 | [^rB] |
| C | VM-MS-M-070-090-200-70 | M | 0.70 | 0.090 | 200 | 7.0 | [^rC] |
| D | VM-MS-M-087-070-310-79 | M (DB end) | 0.87 | 0.070 | 310 | 7.9 | [^rD] |
| E | VM-MS-A-125-085-300-80 | A | 1.25 | 0.085 | 300 | 8.0 | [^rE] |
| F | VM-MS-A-145-085-240-75 | A | 1.45 | 0.085 | 240 | 7.5 | [^rF] |
| G | VM-MS-A-130-080-220-70 | A | 1.30 | 0.080 | 220 | 7.0 | [^rG] |
| H | VM-MS-A-120-100-300-90 | A | 1.20 | 0.100 | 300 | 9.0 | [^rH] |
| I | VM-MS-A-090-130-300-105 | A | 0.90 | 0.130 | 300 | 10.5 | [^rI] |

**Tolerances:** the cited sellers do not publish tolerances on h, t, L or D, and this sheet states
none. The sellers list sizes in the order height × thickness × length × barrel diameter.[^rdb]

**Material:** an age-hardened Co-Ni-Cr spring alloy of the Nivaflex 45/5 type, with:[^vac]

- E = 220 GPa;
- Rp0.2 = 1840 to 2475 MPa after age-hardening (wire data; strip is assumed equivalent, see Note 4);
- density 8.5 g/cm³;
- non-magnetic.

## 4. Absolute maximum ratings (Table 2)

Stresses above these values may set the spring permanently, which lowers its torque and run time.

| Var. | Max. torque, elastic limit M_el (N·mm)[^d3] | Max. arbor turns from let-down, N (theoretical)[^d1] |
|---|---|---|
| A | 2.38 | 5.7 |
| B | 1.85 | 5.5 |
| C | 2.34 | 4.3 |
| D | 1.76 | 10.1 |
| E | 3.73 | 6.8 |
| F | 4.32 | 6.0 |
| G | 3.43 | 5.9 |
| H | 4.95 | 6.3 |
| I | 6.27 | 4.9 |

**Bridle slipping torque (end type A):** not published by any source we found. For strength checks,
take the slipping torque as no greater than M_el (Note 4).

## 5. Recommended operating conditions and characteristics (Table 3, calculated)

| Var. | Arbor core radius r (mm)[^d0] | Turns N[^d1] | Run time at 8 h per barrel turn (h)[^d4] | Stiffness k (N·mm/rad)[^d2] | Torque at N turns, M_N (N·mm)[^d2] | Bending stress at N (MPa)[^d3] |
|---|---|---|---|---|---|---|
| A | 1.28 | 5.7 | 46 | 0.0352 | 1.27 | 1320 |
| B | 1.28 | 5.5 | 44 | 0.0185 | 0.64 | 851 |
| C | 1.44 | 4.3 | 35 | 0.0468 | 1.27 | 1349 |
| D | 1.12 | 10.1 | 81 | 0.0176 | 1.12 | 1574 |
| E | 1.36 | 6.8 | 54 | 0.0469 | 2.00 | 1331 |
| F | 1.36 | 6.0 | 48 | 0.0680 | 2.56 | 1466 |
| G | 1.28 | 5.9 | 47 | 0.0555 | 2.04 | 1474 |
| H | 1.60 | 6.3 | 50 | 0.0733 | 2.90 | 1449 |
| I | 2.08 | 4.9 | 39 | 0.1208 | 3.72 | 1467 |

The run time assumes a going train that turns the barrel once per 8 h, which is typical.[^wiki] It is
not a property of the spring alone. For reference, ETA states a minimum running time of 38 h for its
11½‴ calibre 2824-2.[^eta2824]

## 6. Torque against arbor turns (Table 4, calculated, frictionless)

Torque at the arbor, in N·mm, after n turns wound from the let-down state.[^d2] A dash means the
variant is fully wound before that turn.

| Var. | n = 1 | 2 | 3 | 4 | 5 | 6 | at N |
|---|---|---|---|---|---|---|---|
| A | 0.22 | 0.44 | 0.66 | 0.88 | 1.11 | – | 1.27 |
| B | 0.12 | 0.23 | 0.35 | 0.47 | 0.58 | – | 0.64 |
| C | 0.29 | 0.59 | 0.88 | 1.18 | – | – | 1.27 |
| D | 0.11 | 0.22 | 0.33 | 0.44 | 0.55 | 0.67 | 1.12 (n = 7: 0.78; 8: 0.89; 9: 1.00; 10: 1.11) |
| E | 0.29 | 0.59 | 0.88 | 1.18 | 1.47 | 1.77 | 2.00 |
| F | 0.43 | 0.85 | 1.28 | 1.71 | 2.14 | – | 2.56 |
| G | 0.35 | 0.70 | 1.05 | 1.39 | 1.74 | – | 2.04 |
| H | 0.46 | 0.92 | 1.38 | 1.84 | 2.30 | 2.76 | 2.90 |
| I | 0.76 | 1.52 | 2.28 | 3.04 | – | – | 3.72 |

## Notes

1. **Barrel space.** Fit a spring only in a barrel of its listed inner diameter D. The drum wall
   thickness and the barrel's outside diameter are not given here; the movement designer must check
   that the drum fits the movement.
2. **Real springs do not follow Table 4 exactly.** A real spring still gives some torque when let down,
   because of its free shape, and friction between its coils lowers the torque it delivers. Neither
   effect is published for these sizes. M_el (Table 2) is a strict upper bound on the torque the spring
   can reach without setting, whatever its shape, so use M_el for strength and holding checks.
3. **Handling.** Wind springs into the barrel with a mainspring winder. Do not hand-wind them in: the
   strip takes a permanent set when bent beyond the elastic limit used for M_el.
4. **Method of calculation.** These notes refer to footnotes [^d0] to [^d4]. The thickness correction,
   the core-radius rule and the half-area rule come from the cited barrel-design article. The torque
   formula is the flat-strip spiral-spring relation. The stress is beam bending of the rectangular strip.

## Sources

[^rdb]: Size notation and listings: ressortdebarillet.ch catalogue, https://en.ressortdebarillet.ch/collections/ressort-de-barillet-epaisseur-0-102
[^eta2671]: ETA 2671: 7¾‴, Ø 17.20 mm, typical reserve about 44 h, https://portal.eta.ch/en/mecaline/2671-2671-5.html
[^eta2824]: ETA 2824-2: Ø 25.60 mm, running time at least 38 h. ETA Technical Communication CT 2824-2, https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1883
[^ligne]: 1 ligne = 2.2558 mm, https://en.wikipedia.org/wiki/Ligne
[^wiki]: The barrel typically turns once per about 8 h, https://en.wikipedia.org/wiki/Mainspring
[^vac]: VACUUMSCHMELZE, NIVAFLEX 45/5 alloy information, January 2008. E 220 GPa; Rp0.2 1840/2155/2475 MPa after age-hardening at 50/70/90 % cold work; density 8.5 g/cm³; non-magnetic. https://www.cousinsuk.com/pdf/skus/9601_9596_nivaflex_45_5.pdf
[^rA]: 0.90 × 0.08 × 240 × 7, mechanical, https://en.ressortdebarillet.ch/products/0-90-x-08-x-240-x-7-mecanique
[^rB]: 0.70 × 0.08 × 355 × 7.5, non-automatic, https://en.ressortdebarillet.ch/products/0-70-x-08-x-355-x-7-5-non-automatique
[^rC]: 0.70 × 0.09 × 200 × 7, non-automatic, https://en.ressortdebarillet.ch/products/0-70-x-09-x-200-x-7-non-automatique
[^rD]: 0.87 × 0.07 × 310 × 7.9, DB end, https://en.ressortdebarillet.ch/products/ressort-de-barillet-0-87-x-0-07-x-310-x-7-9-db-end-jaeger-le-coultre-818
[^rE]: 1.25 × 0.085 × 300 × 8, automatic, https://en.ressortdebarillet.ch/products/1-25-x-085-x-300-x-8-automatique
[^rF]: 1.45 × 0.085 × 240 × 7.5, automatic, https://en.ressortdebarillet.ch/products/1-45-x-085-x-240-x-7-5-automatique
[^rG]: 1.30 × 0.08 × 220 × 7, automatic, https://en.ressortdebarillet.ch/products/1-30-x-08-x-220-x-7-automatique
[^rH]: 1.20 × 0.10 × 300 × 9, automatic, https://en.ressortdebarillet.ch/products/1-20-x-10-x-300-x-9-automatique
[^rI]: 0.90 × 0.13 × 300 × 10.5, automatic, https://en.ressortdebarillet.ch/products/0-90-x-13-x-300-x-10-5-automatique
[^d0]: Not published; derived as r = 16·t, Defossez's ratio r/e = 16 as given in https://watchesbysjx.com/2025/11/in-depth-balancing-mainspring-dimensions-inside-the-barrel.html (the same article gives a modern minimum of about 10).
[^d1]: Not published; derived from conservation of strip area. The strip occupies L·t′, with t′ = t + 0.003 mm, inside the 0.002 to 0.004 mm correction range given in https://watchesbysjx.com/2025/11/in-depth-balancing-mainspring-dimensions-inside-the-barrel.html. Coils wound on the core: n_w = (√(r² + L·t′/π) − r)/t′. Coils let down against the wall: n_d = (R − √(R² − L·t′/π))/t′, with R = D/2. N = n_w − n_d. Inputs: Table 1 (sources [^rA] to [^rI]) and [^d0].
[^d2]: Not published; derived from the spiral-spring relation M = E·b·t³·θ/(12·L), with θ in radians, b = h and θ = 2π·n, from https://calculator.academy/spiral-torsion-spring-calculator/. k = E·b·t³/(12·L), with E = 220 GPa from [^vac].
[^d3]: Not published; derived from the bending stress of a rectangular strip, σ = 6·M/(b·t²), that is M/Z with section modulus Z = b·t²/6, from https://www.codecogs.com/page/1150/v/3359. M_el = Rp0.2·b·t²/6, with Rp0.2 = 2475 MPa (aged, 90 % cold work) from [^vac].
[^d4]: Derived: run time = N × 8 h, with 8 h per barrel turn from [^wiki].
