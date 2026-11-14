# Valtorre Microtechnique SA: Application note, finger torque at the crown

**Demonstration-scale series, scale 1.617:1 to an 11½‴ calibre (s = 1.617).** Human strength does not
scale with the movement: every value in this note applies unchanged to the demonstration-scale series,
at the actual crown diameter.

| Document | Revision | Date | Status |
|---|---|---|---|
| VM-AN-501 | C | 2026-11-14 | Released |

> **About this document.** Valtorre Microtechnique SA, demonstration series. The measured torques, the pinch strengths, the friction values and the design limit for knobs
> come from the cited studies and standards. The recommended winding torque (section 5) is
> **calculated**, as its footnote states.

## 1. Scope

This note covers the torque that adults apply to a small round crown with thumb and index finger. It
also sets the recommended maximum winding torque at the crown, against which a keyless works is
designed.

## 2. Measured maximum finger torque on small cylinders (Table 1)

Mean maximum voluntary torque, finger pinch, from industrial workers (10 men, 13 women).[^imr] The
torques were measured in in-oz and are converted at 1 in-oz = 7.06 N·mm.[^ozf]

| Cylinder Ø | Group | Smooth, loosening | Smooth, tightening | Knurled, loosening | Knurled, tightening |
|---|---|---|---|---|---|
| 3.3 mm | Men | 100 N·mm | 114 N·mm | 150 N·mm | 203 N·mm |
| 3.3 mm | Women | 74 N·mm | **69 N·mm** | 129 N·mm | 154 N·mm |
| 5.0 mm | Men | 155 N·mm | 157 N·mm | 184 N·mm | 294 N·mm |
| 5.0 mm | Women | 90 N·mm | 96 N·mm | 156 N·mm | 232 N·mm |

These are **maximal** efforts, not comfortable ones. The lowest value, 69 N·mm, is for women on a
smooth 3.3 mm cylinder.[^imr]

## 3. Design limit for knobs (Table 2)

| Quantity | Value | Source |
|---|---|---|
| Fingertip-grasp knob, diameter | 10 to 100 mm | [^mil] |
| Maximum torque resistance, knob Ø ≤ 25 mm | **32 mN·m (32 N·mm)** | [^mil] |
| Maximum torque resistance, knob Ø > 25 mm | 42 mN·m | [^mil] |

A crown is smaller than the standard's minimum knob, so 32 N·mm is the maximum torque resistance for
comfortable operation, not a crown rating.

## 3a. Crown torque the watch withstands, for comparison (Table 2a)

| Quantity | Value at 1:1 | Source |
|---|---|---|
| Torque at the crown that a fully wound watch withstands without damage | **42 mN·m** (42.4 ± 3.5 mN·m, 6 ± 0.5 in-oz) | [^mil46374][^gg113] |
| Torque limits of motorised crown winders, at full wind (supporting context) | typically 10 to 50 mN·m | [^omega] |

- **The human-side values in this note are NOT scaled.** Fingers do not scale with the movement: the
  32 N·mm knob maximum, the measured finger torques of Table 1, the pinch forces of Table 3 and T_rec
  of Table 4 apply unchanged to the demonstration-scale series.
- The 42 mN·m is a withstand limit of a real 1:1 watch, not a comfort level, and it lies above the
  32 mN·m comfortable knob maximum. The corresponding rating of the demonstration-scale crown and works
  is a mechanical rating and does scale (VM-DS-401 Table 4: 179.3 N·mm).
- **A measured comfortable crown winding torque:** not published.

## 4. Pinch strength and fingertip friction (Table 3)

| Quantity | Value | Source |
|---|---|---|
| Tip pinch, women 20–24, left hand (lowest mean for ages 20 to 34) | 10.5 lb = 46.7 N | [^tes][^lbf] |
| Tip pinch, men 20–24, right hand | 18.0 lb = 80.1 N | [^tes][^lbf] |
| Finger pad on aluminium, μ (mean, at 1 to 20 N) | 0.6 | [^seo] |
| Change in μ from 1 to 20 N normal force | −46 % | [^seo] |
| Continuous effort, maximum share of maximum strength | 15 % | [^ergo] |

The pinch norms are from Mathiowetz et al. 1985.[^math]

## 5. Recommended maximum winding torque at the crown (Table 4, calculated)

Two opposed pads each press on a crown of diameter D with force F. Each carries μ·F before it slips,
at radius D/2, so the torque before slipping is **T = μ·F·D**.[^etb] With F = 15 % × 46.7 N = 7.0 N
and μ = 0.6, T = 4.20·D N·mm. The result is capped at the MIL-STD knob limit of 32 N·mm:

  **T_rec = min(4.20·D, 32) N·mm**, with D in mm.[^d1]

| Crown Ø D (mm) | 2 | 3 | 4 | 5 | 6 | 7 | ≥ 7.62 |
|---|---|---|---|---|---|---|---|
| **T_rec (N·mm)** | 8.4 | 12.6 | 16.8 | 21.0 | 25.2 | 29.4 | **32.0** |

The winding torque needed at the crown must not exceed T_rec. That is the largest mainspring torque,
divided by the gear ratio from crown to barrel arbor.

**Cross-check.** At D = 3.3 mm, T_rec = 13.9 N·mm, which is 20 % of the lowest measured maximum in
Table 1 (69 N·mm).[^imr]

## 6. Notes

1. **This note covers adults of working age only.** The pinch value used is for ages 20 to 34; older adults pinch less (the same norms give 7.9 lb for women 75 and over).
2. **Condition of the fingers.** Wet or gloved fingers change μ. Table 1 shows that knurling raises the
   maximum torque, but T_rec gives it no credit.

## Sources

[^imr]: Imrhan S. and Munoz-Vasa M., "Finger pinch loosening and tightening torques on small cylindrical handles among industrial workers", ISER 1(2), 2013, tables 2 and 3, https://westpointpressjournals.westpoint.edu/index.php/iser/article/download/20/Imrhan/112
[^ozf]: 1 ozf = 0.278 N, so 1 in-oz = 0.278 N × 25.4 mm = 7.06 N·mm, https://en.wikipedia.org/wiki/Ounce-force
[^mil]: MIL-STD-1472H, Human Engineering (15 Sep 2020), figure 10 "Knobs" (public domain, distribution A), https://everyspec.com/MIL-STD/MIL-STD-1400-1499/download.php?spec=MIL-STD-1472H.057041.pdf
[^mil46374]: MIL-W-46374F, *Watch, Wrist, General Purpose* (US Army), §3.3.7 (p. 8, test §4.7.12): a fully wound watch is not damaged by 6 ± 0.5 in-oz at the crown (1 in-oz = 7.06 mN·m, [^ozf]). US government work, public domain. https://everyspec.com/MIL-SPECS/MIL-SPECS-MIL-W/download.php?spec=MIL-W-46374F.021322.PDF
[^gg113]: GG-W-113A (1967), §3.9.3: the same 6 ± ½ oz-in. US government work, public domain. https://everyspec.com/FED_SPECS/G/download.php?spec=GG-W-113A.022400.PDF
[^omega]: Omega SA, US 9,244,437 B2 (crown-winding device), description: torque limits typically 10 to 50 mN·m at full wind. US patent text, public domain. https://patents.google.com/patent/US9244437B2/en
[^math]: Mathiowetz V. et al., Arch Phys Med Rehabil 1985; 66(2): 69–74, https://pubmed.ncbi.nlm.nih.gov/3970660/
[^tes]: Reproduction of the Mathiowetz 1985 pinch tables (lb), https://www.topendsports.com/testing/tests/pinch-grip-strength.htm
[^lbf]: 1 lbf = 4.448 N, https://en.wikipedia.org/wiki/Pound_(force)
[^seo]: Seo N.J. and Armstrong T.J., Ergonomics 2009; 52(5): 609–616, https://stacks.cdc.gov/view/cdc/215047
[^ergo]: Ergoweb, static load: at most 15 % of maximum strength for continuous effort (Rohmert), https://ergoweb.com/static-load/
[^etb]: Coulomb friction F_f = μ·N, Engineering ToolBox, https://engineeringtoolbox.com/friction-coefficients-d_778.html
[^d1]: Not published; calculated as T = μ·F·D, with μ = 0.6 [^seo] and F = 0.15 × 46.7 N [^ergo][^tes][^lbf], capped at 32 N·mm [^mil]. The cap applies from D = 32/4.20 = 7.62 mm.
