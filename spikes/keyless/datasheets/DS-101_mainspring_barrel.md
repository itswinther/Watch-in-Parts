# Valtorre Microtechnique SA: Mainsprings, demonstration-scale series

**Demonstration-scale series, scale 1.617:1 to an 11½‴ calibre (s = 1.617).**

| Document | Revision | Date | Status |
|---|---|---|---|
| VM-DS-101 | E | 2026-11-14 | Released |

> **About this document.** Valtorre Microtechnique SA is a fictional supplier, used for this exercise
> only.
>
> - **What is real:** each spring in Table 1 is a real catalogue size, cited row by row. This series
>   reproduces it with every length multiplied by s = 1.617.
> - **What is measured:** one reference torque measurement on a real 11½‴ calibre (Table 2a), and a
>   published winding/unwinding ratio. Both are cited as facts.
> - **What is calculated:** no maker publishes torque or turns for these particular springs, so their
>   performance figures are calculated, not measured. Note 5 and the footnotes give the method and the
>   sources.
>
> Both the 1:1 size and the scaled size are given. **Use the scaled columns** for this series.

## 1. Scope and scale

- **Scale:** this series is a geometrically similar enlargement of real watch mainsprings. Every length
  is multiplied by s = 1.617, the ratio of a Ø 41.4 mm demonstration movement to the 11½‴ (Ø 25.60 mm)
  ETA 2824-2.[^eta2824][^s]
- **What the scale changes, and what it does not:** with the same material, stresses are unchanged,
  torques scale with s³ = 4.229, and turns and hours are unchanged.[^d5]
- **End types:**
  - **M (manual):** a fixed outer end. The click must hold the full torque.
  - **A (automatic):** a slipping bridle, which slips in the barrel once the spring is fully wound.[^wiki]
- **Barrels supplied with this series:** the arbor core (hub) radius is one third of the barrel's inner
  radius, r = D/6, the classical proportion "established by long practice".[^gro108][^saun] For the
  strips of Table 1 this gives a hub diameter of 26 to 38 times the strip thickness, about the 32 × t of
  Grossmann's worked case.[^gro108][^d6]

## 2. Ordering code

`VM-MS-<end>-<variant>-DS`, for example `VM-MS-A-F-DS`. "DS" marks the demonstration-scale series.

## 3. Dimensions (Table 1)

| Var. | End | Real size h × t × L × D (mm), 1:1 | Source | **Height h (mm)** | **Thickness t (mm)** | **Length L (mm)** | **Barrel inner Ø D (mm)** |
|---|---|---|---|---|---|---|---|
| A | M | 0.90 × 0.080 × 240 × 7.0 | [^rA] | 1.46 | 0.129 | 388 | 11.3 |
| B | M | 0.70 × 0.080 × 355 × 7.5 | [^rB] | 1.13 | 0.129 | 574 | 12.1 |
| C | M | 0.70 × 0.090 × 200 × 7.0 | [^rC] | 1.13 | 0.146 | 323 | 11.3 |
| D | M (DB end) | 0.87 × 0.070 × 310 × 7.9 | [^rD] | 1.41 | 0.113 | 501 | 12.8 |
| E | A | 1.25 × 0.085 × 300 × 8.0 | [^rE] | 2.02 | 0.137 | 485 | 12.9 |
| F | A | 1.45 × 0.085 × 240 × 7.5 | [^rF] | 2.34 | 0.137 | 388 | 12.1 |
| G | A | 1.30 × 0.080 × 220 × 7.0 | [^rG] | 2.10 | 0.129 | 356 | 11.3 |
| H | A | 1.20 × 0.100 × 300 × 9.0 | [^rH] | 1.94 | 0.162 | 485 | 14.6 |
| I | A | 0.90 × 0.130 × 300 × 10.5 | [^rI] | 1.46 | 0.210 | 485 | 17.0 |
| J | A | 1.45 × 0.100 × 380 × 10.0 | [^rJ] | 2.34 | 0.162 | 615 | 16.2 |
| K | M (ETA 2801 size) | 1.23 × 0.134 × 400 × 10.5 | [^rK] | 1.99 | 0.217 | 647 | 17.0 |

All scaled values are the real value × s.[^s] The sellers list sizes as height × thickness × length ×
barrel diameter.[^rdb] **Tolerances:** not published by the cited sellers, and none are stated here.

**Material:** an age-hardened Co-Ni-Cr spring alloy of the Nivaflex 45/5 type, with:[^vac]

- E = 220 GPa;
- Rp0.2 up to 2475 MPa after age-hardening (wire data, assumed to hold for strip);
- non-magnetic.

## 4. Absolute maximum ratings (Table 2, calculated)

M_el is the torque at which the outer fibre of the strip reaches its proof stress.

| Var. | **Max. torque at the elastic limit, M_el (N·mm)**[^d3] | Turns from let-down to M_el, n_el[^d2] |
|---|---|---|
| A | 10.0 | 10.7 |
| B | 7.8 | 15.9 |
| C | 9.9 | 8.0 |
| D | 7.4 | 15.9 |
| E | 15.8 | 12.6 |
| F | 18.3 | 10.1 |
| G | 14.5 | 9.8 |
| H | 20.9 | 10.7 |
| I | 26.5 | 8.3 |
| J | 25.3 | 13.6 |
| K | 38.5 | 10.7 |

M_el is the calculated torque at first yield of a straight, unstressed strip. It is **not** an upper
bound on the torque a finished spring delivers: see Table 2a and Note 2.

**Bridle slipping torque (type A):** not published for the springs of Table 1. The reference
measurement in Table 2a gives the slipping band of a real 11½‴ automatic spring.

## 4a. Reference measurement on a real 11½‴ calibre (Table 2a, measured)

Measured torque at the barrel arbor of a production automatic movement of the 11½‴ class (Sellita
SW200-1).[^sel] The maker does not publish that spring's dimensions, so the measurement is given for the
class, not for a variant of Table 1. The demonstration-scale value is the 1:1 value × s³ = 4.229.[^d5]

| Quantity | 1:1 value (measured) | **This series (N·mm)**[^d7] |
|---|---|---|
| Torque half a turn from full wind, M½ | 11.86 N·mm | **50.2** |
| Torque after 24 h of running, M24 | 8.83 N·mm (0.745 × M½) | **37.3** |
| Slipping torque of the bridle | 12.21 to 16.57 N·mm (1.03 to 1.40 × M½) | **51.6 to 70.1** |

**Winding against unwinding:** the torque a spring delivers while unwinding is at least 80 % of the
torque needed to wind it at the same state of wind (84 % measured half a turn from full wind, on a
500 mm × 90 µm spring).[^niv] The ratio does not depend on scale.

## 5. Turns and run time (Table 3, calculated)

Turns of development N depend strongly on the barrel's arbor core radius r.[^sjx25] Values are given for
the core of the barrels supplied with this series, and for two other core ratios for comparison:

- **r = D/6 (one third of the inner radius):** the supplied barrels (section 1);[^gro108][^saun]
- **r = 12·t:** within the modern range (minimum about 10);
- **r = 16·t:** Defossez's ratio.

| Var. | **r = D/6 (mm)** | r/t | **N at r = D/6** | **Run time (h)** | r = 12·t (mm) | N at r = 12·t | Run time (h) | r = 16·t (mm) | N at r = 16·t | Run time (h) |
|---|---|---|---|---|---|---|---|---|---|---|
| A | 1.89 | 14.6 | 6.5 | 52 | 1.55 | 8.0 | 64 | 2.07 | 5.7 | 46 |
| B | 2.02 | 15.6 | 5.7 | 45 | 1.55 | 8.0 | 64 | 2.07 | 5.5 | 44 |
| C | 1.89 | 13.0 | 5.9 | 47 | 1.75 | 6.4 | 51 | 2.33 | 4.3 | 35 |
| D | 2.13 | 18.8 | 8.5 | 68 | 1.36 | 12.6 | 101 | 1.81 | 10.1 | 81 |
| E | 2.16 | 15.7 | 7.0 | 56 | 1.65 | 9.2 | 74 | 2.20 | 6.8 | 54 |
| F | 2.02 | 14.7 | 6.7 | 53 | 1.65 | 8.2 | 66 | 2.20 | 6.0 | 48 |
| G | 1.89 | 14.6 | 6.6 | 53 | 1.55 | 8.1 | 65 | 2.07 | 5.9 | 47 |
| H | 2.43 | 15.0 | 6.8 | 55 | 1.94 | 8.6 | 69 | 2.59 | 6.3 | 50 |
| I | 2.83 | 13.5 | 6.2 | 50 | 2.52 | 7.0 | 56 | 3.36 | 4.9 | 39 |
| J | 2.70 | 16.7 | 7.6 | 60 | 1.94 | 10.4 | 83 | 2.59 | 7.9 | 63 |
| K | 2.83 | 13.1 | 5.2 | 41 | 2.60 | 5.8 | 47 | 3.47 | 3.5 | 28 |

How these were calculated:

- N is from [^d1]. It is the same at 1:1 and at demonstration scale, because it depends only on length
  ratios.[^d5]
- Run time = N × 8 h, at the typical barrel speed of one turn per 8 h.[^wiki] That speed is a property
  of the going train, not of the spring.

**Calibration against a real movement.**

- **The check:** variant K is the ETA 2801 size,[^rK] and ETA states 42 h for the 2801-2.[^eta2801]
- **The result:** the r = D/6 column gives 41 h; the r = 12·t column gives 47 h; the r = 16·t column
  gives 28 h.
- **The conclusion:** the r = D/6 column, which is the core of the supplied barrels, agrees with the
  real movement to within 1 h. The r = 16·t column is very conservative.

**For comparison, real minimum and typical reserves:**

| Calibre | Reserve |
|---|---|
| ETA 2824-2 | min 38 h[^eta2824] |
| ETA 6497-2 | 53 h[^rds] |
| ETA 6498-1 | 46 h[^rds] |

## 6. Torque against arbor turns (Table 4, calculated, frictionless)

Torque at the arbor, in N·mm, gained after n turns wound from the let-down state.[^d2] A dash means the
spring is fully wound before that turn (r = 12·t column of Table 3). The last column is the torque at
full wind, which is no more than M_el.

| Var. | n = 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | at N (r = 12·t) |
|---|---|---|---|---|---|---|---|---|---|
| A | 0.9 | 1.9 | 2.8 | 3.7 | 4.7 | 5.6 | 6.5 | 7.5 | 7.5 |
| B | 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.0 | 3.4 | 3.9 | 3.9 |
| C | 1.2 | 2.5 | 3.7 | 5.0 | 6.2 | – | – | – | 8.0 |
| D | 0.5 | 0.9 | 1.4 | 1.9 | 2.3 | 2.8 | 3.3 | 3.8 | 5.9 |
| E | 1.2 | 2.5 | 3.7 | 5.0 | 6.2 | 7.5 | 8.7 | 10.0 | 11.5 |
| F | 1.8 | 3.6 | 5.4 | 7.2 | 9.0 | 10.8 | 12.7 | 14.5 | 14.9 |
| G | 1.5 | 2.9 | 4.4 | 5.9 | 7.4 | 8.8 | 10.3 | 11.8 | 11.9 |
| H | 1.9 | 3.9 | 5.8 | 7.8 | 9.7 | 11.7 | 13.6 | 15.6 | 16.7 |
| I | 3.2 | 6.4 | 9.6 | 12.8 | 16.1 | 19.3 | 22.5 | – | 22.6 |
| J | 1.9 | 3.7 | 5.6 | 7.4 | 9.3 | 11.2 | 13.0 | 14.9 | 19.3 |
| K | 3.6 | 7.2 | 10.8 | 14.4 | 18.0 | – | – | – | 21.0 |

## Notes

1. **Barrel space.** Fit a spring only in a barrel of its listed inner diameter D. The drum wall is not
   given here.
2. **Real springs carry torque at let-down.** Grossmann counts turns from the spring's free, unwound
   state, so a real spring already gives torque when let down. His worked example falls from 5,640 to
   5,251 g·mm over the first barrel turn of running, so the curve is not flat.[^gro] The free shape of
   these springs is not published, so Table 4 shows only the torque gained above let-down. Coil friction
   lowers the torque delivered.
   **Correction (Rev E):** Rev D called M_el a strict upper bound on the torque. It is not. Finished
   springs are set in manufacture and deliver more than the first-yield torque of a straight strip: the
   measured 11½‴ reference (Table 2a) gives 11.86 N·mm at 1:1 half a turn from full wind, and its bridle
   slips at up to 16.57 N·mm, above the calculated M_el of every spring in Table 1 at 1:1 (largest: K,
   9.1 N·mm). The highest torque this sheet states for the 11½‴ class is the reference slipping torque,
   **70.1 N·mm** in this series.[^sel][^d7]
3. **Handling.** Use a mainspring winder. Do not wind springs into the barrel by hand.
4. **Scaled springs.** At this scale the strip is about 0.11 to 0.22 mm thick.
5. **Method.** Footnotes [^d1] to [^d7].

## Sources

[^s]: Scale s = 41.4 mm / 25.60 mm = 1.617. 41.4 mm is the case diameter of the demonstration movement this series is made for; 25.60 mm is the ETA 2824-2 diameter.[^eta2824] Every scaled length = real length × 1.617.
[^eta2824]: ETA CT 2824-2: 11½‴, Ø 25.60 mm, running time min 38 h, https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1883
[^eta2801]: ETA CT 2801-2 (hand-wound, 11½‴): 42 h, https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1626
[^rds]: ETA CT 6497-2, 53 h, https://patrimoine.bourgognefranchecomte.fr/documents/ETA_6497-2.pdf ; ETA CT 6498-1, 46 h, https://patrimoine.bourgognefranchecomte.fr/documents/ETA_6498-1.pdf
[^wiki]: The barrel turns once per about 8 h; the slipping bridle of automatic watches. https://en.wikipedia.org/wiki/Mainspring
[^vac]: VACUUMSCHMELZE, NIVAFLEX 45/5: E 220 GPa; Rp0.2 1840/2155/2475 MPa after aging (50/70/90 % cold work). https://www.cousinsuk.com/pdf/skus/9601_9596_nivaflex_45_5.pdf
[^rdb]: Size notation, ressortdebarillet.ch, https://en.ressortdebarillet.ch/collections/ressort-de-barillet-epaisseur-0-102
[^rA]: https://en.ressortdebarillet.ch/products/0-90-x-08-x-240-x-7-mecanique
[^rB]: https://en.ressortdebarillet.ch/products/0-70-x-08-x-355-x-7-5-non-automatique
[^rC]: https://en.ressortdebarillet.ch/products/0-70-x-09-x-200-x-7-non-automatique
[^rD]: https://en.ressortdebarillet.ch/products/ressort-de-barillet-0-87-x-0-07-x-310-x-7-9-db-end-jaeger-le-coultre-818
[^rE]: https://en.ressortdebarillet.ch/products/1-25-x-085-x-300-x-8-automatique
[^rF]: https://en.ressortdebarillet.ch/products/1-45-x-085-x-240-x-7-5-automatique
[^rG]: https://en.ressortdebarillet.ch/products/1-30-x-08-x-220-x-7-automatique
[^rH]: https://en.ressortdebarillet.ch/products/1-20-x-10-x-300-x-9-automatique
[^rI]: https://en.ressortdebarillet.ch/products/0-90-x-13-x-300-x-10-5-automatique
[^rJ]: https://en.ressortdebarillet.ch/products/1-45-x-10-x-380-x-10-automatique
[^rK]: 1.23 × 0.134 × 400 × 10.5, ETA 2801, https://en.ressortdebarillet.ch/products/1-23-x-134-x-400-x-10-5-eta-2801-mecanique
[^sjx25]: Core ratio r/e: Defossez 16; modern minimum about 10; thickness correction 0.002 to 0.004 mm; maximum turns at half the area. https://watchesbysjx.com/2025/11/in-depth-balancing-mainspring-dimensions-inside-the-barrel.html
[^gro]: J. Grossmann, *Lessons in Horology* (1905), art. 97 (M = E·h·e³·2πn/(12·L), n counted from the free spring) and art. 99 (worked example: 5,640 g·mm at full wind, less 389 g·mm per barrel turn). Public domain. https://archive.org/download/lessonsinhorolog00gros/lessonsinhorolog00gros_djvu.txt
[^d1]: Not published; derived from conservation of strip area, L·t′ with t′ = t + 0.003·s mm (the correction from [^sjx25], scaled). Coils on the core: n_w = (√(r² + L·t′/π) − r)/t′. Coils against the wall: n_d = (R − √(R² − L·t′/π))/t′, with R = D/2. N = n_w − n_d. Inputs from Table 1; r from [^sjx25].
[^d2]: Not published; derived from M = E·h·t³·2πn/(12·L) (Grossmann art. 97 [^gro]; also https://calculator.academy/spiral-torsion-spring-calculator/), with E from [^vac] and the scaled sizes. Here n is counted from let-down (Note 2). n_el = M_el/(2π·k), with k = E·h·t³/(12·L).
[^d3]: Not published; derived as M_el = Rp0.2·h·t²/6 (rectangular section, Z = b·t²/6, https://www.codecogs.com/page/1150/v/3359), with Rp0.2 = 2475 MPa from [^vac] and the scaled h and t.
[^gro108]: J. Grossmann, *Lessons in Horology* (1905), art. 108 (p. 63: "the custom, in practice, to make the radius of the hub equal to one-third of the interior radius of the barrel"), art. 110 (p. 64) and art. 111 (pp. 64 to 66: the proportion is "established by long practice"; worked case barrel ID 17.4 mm, hub Ø 5.8 mm, spring 0.18 mm, so hub Ø ≈ 32 × thickness). Public domain. https://archive.org/download/lessonsinhorolog00gros/lessonsinhorolog00gros_djvu.txt
[^saun]: C. Saunier, *The Watchmaker's Hand-Book*, art. 517 "The Arbor-Nut": the diameter of the nut is usually one third of the inside diameter of the barrel, larger for thick springs and smaller for thin ones. Public domain. https://www.gutenberg.org/ebooks/76850
[^sel]: Sellita, SW200-1 Documentation technique, rev 04 (02.02.2015), p. 3: torque half a turn from full wind 11.86 N·mm; after 24 h 8.83 N·mm; slipping bridle 12.21 to 16.57 N·mm. Cited as facts only; the document is copyrighted and not reproduced. Third-party copy: https://watch.co.uk/download/sw200-ml-pdf
[^niv]: Nivarox-FAR, US 11,320,786 B2 (mainspring), summary, claim 7 and FIG. 2: unwinding torque at least 80 % of winding torque, 84 % measured after half a turn; spring 500 mm × 90 µm, core Ø 1.5 mm. US patent text, public domain. https://patents.google.com/patent/US11320786B2/en
[^d6]: Not published; derived as r = D/6 with the scaled D of Table 1, and N from [^d1] at that r. Hub Ø/t = (D/3)/t.
[^d7]: Not published at this scale; derived as the 1:1 value from [^sel] × s³ = 4.229 [^d5]. Ratios to M½ are computed from [^sel].
[^d5]: Geometric similarity: with every length × s, the stress σ = 6M/(h·t²) stays the same when M scales with s³, and M = E·h·t³·θ/(12·L) does scale with s³ for the same θ. N depends only on length ratios, so turns and hours do not change. https://www.codecogs.com/page/1150/v/3359 ; https://calculator.academy/spiral-torsion-spring-calculator/
