# Valtorre Microtechnique SA: Application note, finger torque at the crown

| Document | Revision | Date | Status |
|---|---|---|---|
| VM-AN-501 | A | 2026-11-14 | Released |

> **About this document.** Valtorre Microtechnique SA is a fictional supplier, used for this exercise
> only. The strength and friction data are from the cited studies. No study we found measured torque
> on a watch-sized crown directly, so the torques in Table 3 are **calculated** from pinch strength and
> fingertip friction, as their footnotes state.

## 1. Scope

This note covers the torque that an adult can apply to a small round crown, held between the thumb
and index finger. It also sets the recommended maximum winding torque at the crown, against which a
keyless works is designed. It applies to crowns of Ø 2 to 7 mm, turned by hand without tools.

## 2. Pinch strength of adults (Table 1)

Mean values from the Milwaukee norms, 310 men and 328 women aged 20 to 94.[^math] They are converted
from pounds-force at 1 lbf = 4.448 N.[^lbf]

| Pinch | Age | Hand | Men (lb) | Men (N) | Women (lb) | Women (N) |
|---|---|---|---|---|---|---|
| Tip (2-point) | 20–24 | R | 18.0 | 80.1 | 11.0 | 48.9 |
| Tip (2-point) | 20–24 | L | 17.0 | 75.6 | 10.5 | 46.7 |
| Tip (2-point) | 25–29 | R | 18.3 | 81.4 | 11.2 | 49.8 |
| Tip (2-point) | 25–29 | L | 17.5 | 77.8 | 10.8 | 48.0 |
| Tip (2-point) | 30–34 | R | 17.6 | 78.3 | 11.5 | 51.2 |
| Tip (2-point) | 30–34 | L | 17.6 | 78.3 | 11.2 | 49.8 |
| Key (lateral) | 20–24 | R | 26.0 | 115.7 | 17.6 | 78.3 |
| Palmar (3-point) | 20–24 | R | 26.6 | 118.3 | 17.2 | 76.5 |

The pound values are from a reproduction of the norm tables.[^tes] The newtons are converted.

**Design basis:** tip pinch, the lowest mean in Table 1: **46.7 N** (women, 20–24, left hand). This note
does not cover users over 34, whose norms are not reproduced here.

## 3. Fingertip friction (Table 2)

| Pair | μ | Conditions | Source |
|---|---|---|---|
| Finger pad on aluminium | 0.6 (mean) | Longitudinal pull at 1, 10 and 20 N normal force | [^seo] |
| Finger pad on rubber hose | 0.9 (mean) | Same as above | [^seo] |
| Skin on metals | 0.8 to 1.0 | Clean and dry | [^etb] |

The friction coefficient fell by 46 % as the normal force rose from 1 to 20 N.[^seo] The design value
is **μ = 0.6**, the lower of the two metal values.

## 4. Torque on a round crown

Two opposed finger pads each press on the crown with the pinch force F. Each pad can carry a
tangential friction force of μ·F before it slips (Coulomb friction).[^etb] Both forces act at the
crown radius D/2, so the largest torque before the fingers slip is

  **T = 2·μ·F·(D/2) = μ·F·D.**

**Recommended force for repeated use.** For continuous effort, a force should be at most 15 % of
maximum strength (Rohmert's curve).[^ergo] The recommended design force is therefore
0.15 × 46.7 N = **7.0 N**.

## 5. Ratings (Table 3, calculated)

| Crown Ø D (mm) | Max. finger torque, women's mean, 46.7 N (N·mm) | Max. finger torque, men's mean, 80.1 N (N·mm) | **Recommended max. winding torque at the crown (N·mm)** |
|---|---|---|---|
| 2.0 | 56.0 | 96.1 | **8.4** |
| 2.5 | 70.0 | 120.1 | **10.5** |
| 3.0 | 84.1 | 144.1 | **12.6** |
| 4.0 | 112.1 | 192.2 | **16.8** |
| 5.0 | 140.1 | 240.2 | **21.0** |
| 6.0 | 168.1 | 288.2 | **25.2** |
| 7.0 | 196.1 | 336.3 | **29.4** |

All columns are calculated.[^d1] For any other diameter:

- recommended maximum winding torque: **T_rec = 4.20·D** N·mm, with D in mm;
- women's maximum finger torque: 28.0·D N·mm;
- men's maximum finger torque: 48.0·D N·mm.

The winding torque that the movement needs at the crown must not exceed T_rec. That includes the
largest mainspring torque, divided by the gear ratio from crown to barrel arbor.

## 6. Notes

1. **The maximum columns are upper estimates.** μ falls as the normal force rises,[^seo] so near full
   pinch force the real μ may be below 0.6. The recommended column uses 7.0 N, within the 1 to 20 N
   range in which μ = 0.6 was measured.
2. **Grip and condition.** A tip-pinch gauge is not a knurled cylinder, so the force on a crown may
   differ. Wet or oily fingers, and gloves, change μ. A knurled or fluted crown edge is not credited
   here.

## Sources

[^math]: Mathiowetz V. et al., "Grip and pinch strength: normative data for adults", Arch Phys Med Rehabil 1985; 66(2): 69–74, https://pubmed.ncbi.nlm.nih.gov/3970660/
[^tes]: Reproduction of the Mathiowetz 1985 tip, key and palmar pinch tables (means, lb), https://www.topendsports.com/testing/tests/pinch-grip-strength.htm
[^lbf]: 1 lbf = 4.448 222 N, https://en.wikipedia.org/wiki/Pound_(force)
[^seo]: Seo N.J. and Armstrong T.J., "Friction coefficients in a longitudinal direction between the finger pad and selected materials", Ergonomics 2009; 52(5): 609–616. μ 0.6 on aluminium, 0.9 on rubber, a 46 % fall from 1 to 20 N. https://stacks.cdc.gov/view/cdc/215047
[^etb]: Engineering ToolBox, friction coefficients (skin on metals 0.8 to 1.0, clean and dry; F_f = μ·N), https://engineeringtoolbox.com/friction-coefficients-d_778.html
[^ergo]: Ergoweb, static load: continuous effort at most 15 % of maximum strength (Rohmert), https://ergoweb.com/static-load/
[^d1]: Not published; calculated as T = μ·F·D, with μ = 0.6 from [^seo]. F is 46.7 N (women's lowest mean tip pinch) or 80.1 N (men, 20–24, right), both from [^tes] converted with [^lbf]. For the recommended column, F = 0.15 × 46.7 N from [^ergo].
