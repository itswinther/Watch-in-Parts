<!-- NOT-FOR-AGENT: secret. Traces every implied check to a datasheet value. Never copied into the agent image. -->
# Datasheets v2: traceability (secret)

Written by Mikael + Claude (workstream A), 14 Nov 2026. This revision regenerates the sheets at the
demonstration scale. This file is for the graders and the judges; the agent receives only `DS-*.md` and
`INDEX.md`.

## 0. Build rule (for the keyless and watch builders)

- **Copy:** only `datasheets/DS-*.md` and `datasheets/INDEX.md`, into the agent image.
- **Keep out:**
  - `TRACEABILITY.md`, and anything containing `NOT-FOR-AGENT` (this file's first line);
  - `public_domain/`, unless that is decided separately.
- **Fail the build** if any of those would be included. `assert_clean()` in `spikes/keyless/build_task.py`
  already rejects the marker. Also add `TRACEABILITY.md` to `SECRET_DOCS`.
- **`.harborignore`** in this folder lists `TRACEABILITY.md`.
- This session did not edit any builder.

## 1. Scale: s = 1.617 to an 11½‴ calibre

**The decision.** One scale for the whole job: B's demonstration scale (SESSION.md, Decisions 14:23 B
and 14:45 A).

**The factor.**

- Inputs:
  - `geometry/watch.py` on main: `CASE_RADIUS = 20.7`, so the case is Ø 41.4 mm;
  - ETA 2824-2 Ø 25.60 mm (ETA CT 2824-2, https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1883).
- **s = 41.4/25.6 = 1.6172**, given as 1.617; s² = 2.615; s³ = 4.229 (Docker).
- Other checks in `geometry/watch.py`:
  - `BARREL_MODULE = 0.2`, `BARREL_TEETH = 96`: pitch Ø 19.2 mm, which is 11.9 mm at 1:1, plausible
    for an 11½‴ barrel;
  - `MIN_FEATURE = 0.2` mm, which is 0.12 mm at 1:1, about a real pivot;
  - `CASE_HEIGHT = 13.4` mm, which is 2.9 times the 2824-2's 4.60 mm. Height is **not** geometrically
    scaled. The sheets scale lengths by s only.

**The assumptions.**

- **Geometric similarity:** every length × s, with the same materials.
- **What scales with s:**
  - dimensions (strip h, t, L, D; jewel hole, OD and tolerances; bushings; crown Ø; tube; stem thread,
    length and travel; stem squares; clearance).
- **What scales with s³:**
  - torques. M = E·h·t³·θ/(12L) and M_el = Rp·h·t²/6 both scale with s³ for the same θ, so the stress
    6M/(h·t²) stays the same.
  - stem torsion ratings (0.208·a³·τ).
- **What scales with s²:** forces and radial load ratings (F = M/r scales with s², and F_max = p·d·ℓ
  scales with s², so the pressure stays the same).
- **What does not scale:**
  - turns N, which depend only on length ratios;
  - hours;
  - ratios;
  - friction coefficients;
  - material strengths, moduli and safety factors;
  - **human finger torque and force**, since humans do not scale. That makes the crown-torque check
    4.229 times tighter than at 1:1 (section 3).
- **The mainspring still gives 38 h or more:** the 11½‴-class variants pass at the stated core ratio
  (section 3, row 1).

## 2. Every scaled value and its derivation

Scaled value = 1:1 cited value × s, computed in Docker (`python:3.12-slim`, 2 GB).

| Sheet | Quantity | 1:1 value (source) | Scaled |
|---|---|---|---|
| DS-101 | Strip h, t, L, D, variants A to K | ressortdebarillet.ch product pages (cited per row) | ×1.617 (Table 1) |
| DS-101 | Thickness correction | 0.003 mm (watchesbysjx 2025: 0.002 to 0.004) | 0.0049 mm |
| DS-101 | Core radius r | 12·t or 16·t (watchesbysjx 2025) | uses the scaled t |
| DS-101 | N | geometric, scale-free | unchanged (checked: the same N at both scales) |
| DS-101 | M_el, k, Table 4 | from the scaled sizes | equal to the 1:1 values × 4.229 |
| DS-201 | All values | — | not scaled (material properties) |
| DS-301 | Jewel holes 0.14 to 0.32; OD 2.60 / 3.00 | H.S. Walsh | 0.226 to 0.517; 4.20 / 4.85 |
| DS-301 | Hole tolerance 5.1 / 2.5 µm; concentricity 5.1 / 12.7 µm | Bird Precision | 8.2 / 4.1; 8.2 / 20.5 µm |
| DS-301 | Bushings (9 sizes) | Otto Frei | ×1.617 |
| DS-301 | Clearance 0.01 mm | Watch Repair Talk (secondary) | 0.016 mm |
| DS-301 | F_max | p·d·ℓ, with p not scaled | the 1:1 values × 2.615 |
| DS-401 | Crowns 3.00 to 7.0 | Perrin, Esslinger | 4.85 to 11.32 |
| DS-401 | Tube 2.0 / 2.5 | Esslinger | 3.23 / 4.04 |
| DS-401 | Thread S 0.90; stem length 15.50; travel 0.80; crown gap ≤ 0.1 | Sellita SW200-1 DocTec (link-only, confidential drawings, not reproduced) | 1.455; 25.07; **1.29**; 0.16 |
| DS-401 | Stem squares 0.50 / 0.60 / 0.70 (Valtorre's offer, not cited) | — | 0.809 / 0.970 / 1.132; T_y 92.1 / 159.1 / 252.6 N·mm |
| DS-501 | All values | — | not scaled (human) |

**For the builder:** the stem travel at demonstration scale is 1.29 mm (0.80 × s). The keyless
constant `PULL` should become 1.29 at this scale. The 0.9 × 1.6 = 1.44 in `INTERFACE_FOR_B.md` was based
on the v1 pull and on 1.6 rather than 1.617.

## 3. Implied checks → datasheet value → formula → source

| # | Check | Datasheet values | Formula | Sources |
|---|---|---|---|---|
| 1 | Reserve ≥ 38 h | DS-101 Table 3: N(V) at the core ratio of the supplied barrel | N × 8 h ≥ 38 h | N: area conservation (watchesbysjx 2025). 8 h: Wikipedia Mainspring. 38 h: ETA CT 2824-2 |
| 2 | Tooth bending | DS-101: M_el(V). DS-201 §8: brass 110, steel 750 or 725 MPa | F_t = M_s/r_p. σ = F_t/(b·m·Y), or σ = 6·F_t·h/(b·t²) on the agent's actual tooth (NPTEL lecture 7, eq. 7.12 / 7.6). M_s = M_el at the barrel side, divided by the stage ratios upstream | NPTEL https://archive.nptel.ac.in/content/storage2/courses/112106137/pdf/2_7.pdf ; Wieland; Alleima; UWA (Juvinall) |
| 3 | The click holds | DS-101: M_el. DS-201 Table 7 | F = M_el/r_tip. The draw holds at μ = 0 (conservative). Click and tooth stress ≤ allowable. The click-spring stress at working deflection ≤ steel allowable | Engineering ToolBox; Grossmann art. 335; codecogs |
| 4 | Crown torque ≤ human | DS-501: T_rec = min(4.20·D, 32) N·mm. DS-101: M_el | M_el(V)/i ≤ T_rec(D), with i the crown turns per barrel turn | Seo & Armstrong; Mathiowetz; Rohmert / Ergoweb; MIL-STD-1472H |
| 5a | Pivot fit | DS-301 Tables 1 and 3; clearance 0.016 mm at about 0.226 mm | Catalogue hole; 0 < hole − pivot; recommended ≈ 0.016 mm (band at the builder's choice) | Watch Repair Talk (secondary); H.S. Walsh; Otto Frei |
| 5b | Pivot load | DS-301 §5.3: p_max 900 / 110 N/mm² | F_radial ≤ p_max·d·ℓ | Engineers Edge; makeitfrom; Wieland; UWA |
| 6 | Stem torque | DS-401 Table 3 | M_el/i ≤ the recommended value for the square size a | UoK notes; von Mises; Alleima |
| 7 | Stem positions | DS-401: travel 1.29 mm | `PULL` = 1.29 | Sellita (fact only) |

**Row 1, which variants pass:**

- **At r = 12·t:** every variant passes. The lowest is K, at 5.8 turns = 47 h.
- **At r = 16·t:** C (35 h) and K (28 h) fail.
- **The real check:** K is the ETA 2801 size, and ETA states 42 h for the 2801-2. r = 12·t gives 47 h;
  r = 16·t gives 28 h. So r = 12·t is the realistic column, and r = 16·t is the conservative one.
- **The builder must state the barrel's core ratio** (or its core radius) in the brief or the supplied
  barrel. The supplied arbor's `BARREL_ARBOR_R = 0.5` is the pivot, not the spring core.
- **For the 11½‴-class barrels:** H, I, J and K have scaled inner Ø 14.6 to 17.0 mm, which suits B's
  19.2 mm pitch-Ø barrel wheel.

**Row 4: is the crown-torque limit binding at this scale?**

- M_el at demonstration scale is 7.4 to 38.5 N·mm (variants D to K).
- The worst case inside `WIND_BAND` (i ≥ 3) is K: 38.5/3 = 12.8 N·mm.
- Every catalogue crown in DS-401 is at least Ø 4.85 mm, so T_rec ≥ 20.4 N·mm.
- **So the check is not binding for any catalogue crown.** It binds only if the agent makes its own
  crown smaller than M_el/(3 × 4.20) mm:
  - K: 3.06 mm;
  - I: 2.10 mm;
  - F: 1.45 mm.
- At the old 1:1 scale, the same thresholds were 4.229 times smaller (about 0.7 mm for K), so the check
  is now 4.2 times tighter. It is still not a discriminator for sane designs.
- **Real cross-check:** a 2824-class spring under Grossmann's law gives about 6 to 9 N·mm at 1:1, which
  is 25 to 38 N·mm at demonstration scale. At the NH35's i ≈ 6.9, that is about 3.7 to 5.5 N·mm at the
  crown, well below T_rec.

**The other rows, for sane designs:**

- **Row 2:** a reference-like ratchet at this scale (pitch r about 4.4 mm, module about 0.35, face
  0.8 mm, Y ≈ 0.3) with M_el = 18.3 (F) carries F_t ≈ 4.2 N. Then σ ≈ 4.2/(0.8 × 0.35 × 0.3) ≈ 50 MPa,
  against 110 MPa for brass. The stresses are the same as at 1:1, as geometric similarity requires.
- **Row 5b:** reactions of about 2 to 10 N against ratings of 7 to 230 N.

The discriminating rows remain 1 (choosing the spring at the right core ratio), 2, 3 and 5a.

## 4. Real-document values from REAL_DATASHEETS.md (on main), and what they corrected

| Value | Source (from REAL_DATASHEETS.md) | Where used / corrected |
|---|---|---|
| NH35: 55 crown turns for a full wind, 8 ratchet-wheel turns, so **about 6.9 crown turns per barrel turn** [derived] | TMI NH3 technical guide, https://timemodule.com/upload/category/24/technical_guide/NH35_TG.pdf (link-only) | Row 4 cross-check. Inside `WIND_BAND` 3 to 12. Kept out of the DS sheets, so that no design ratio is hinted |
| **Grossmann's torque law** M = E·h·e³·2πn/(12L), n from the free state; worked example 5,640 g·mm, −389 g·mm per turn | Grossmann 1905, art. 97 and 99 (PD; text in `public_domain/`, verified by grep) | DS-101 now cites it as the primary source of the formula. Note 2 corrected: n counts from the free spring, so a real spring has torque at let-down. Table 4 is relabelled "torque gained above let-down", and M_el remains the bound |
| **MIL-STD-1472H:** knob max **32 mN·m** for Ø ≤ 25 mm (42 above); fingertip knob Ø 10 to 100 mm | everyspec copy of MIL-STD-1472H fig. 10 (PD) | DS-501: T_rec is now capped at 32 N·mm |
| **Imrhan 2013:** MVC finger torque **69 to 155 mN·m** (smooth Ø 3.3 to 5.0 mm, women's tightening to men's loosening) | westpointpressjournals ISER 1(2) (link-only) | **Corrected DS-501:** the earlier friction-model "maximum finger torque" columns (e.g. 140 N·mm for women at Ø 5) overstated the measured 90 to 96. They are removed and replaced by Imrhan's measured table. The recommended limit (20 % of the lowest measured maximum at 3.3 mm) is consistent |
| **Sellita SW200-1 / SW215-1: stem travel 0.80 mm**, S 0.90, stem 15.50 mm, crown gap ≤ 0.1 mm | Sellita DocTec SW200-1 rev 07 (**link-only; drawing pages marked confidential; values cited as facts, document not reproduced or shipped**) | **Corrected DS-401:** the travel was "about 1 mm" (watchesbysjx, secondary); it is now 0.80 mm (primary) × s = 1.29 mm |
| **ETA 6497-2: 53 h; ETA 6498-1: 46 h** | ETA CT 6497-2 and 6498-1 (heritage-site mirrors, link-only) | DS-101 comparison table. Corrects STANDARDS.md 3.5's "6497-1, 46 h" (that figure is the 6498-1's) |
| ETA 2801-2: 42 h | ETA CT 2801-2, https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1626 | Calibrates DS-101's core ratio (variant K) |
| Wieland CuZn39Pb3: R430 Rp0.2 220 MPa; E 96 GPa; density 8.46 g/cm³ | Wieland Z32/Z33 | **Corrected DS-201:** the brass design minimum was 230 MPa (Aalco); it is now 220 MPa, so the allowable is 110 MPa (was 115), and the DS-301 bushing p_max is 110 |
| Grossmann friction: metal on metal 0.15 to 0.17; metal on stones 0.15 | Grossmann art. 335 (PD) | Added to DS-201 Table 7 and DS-301 §5.2. Consistent with Bird's 0.14 |

## 5. Sources and licensing

- **Every URL** used is in the footnotes of the DS sheets. The full list of the previous revision is
  unchanged, plus:
  - Wieland, Grossmann, MIL-STD-1472H, Imrhan, Sellita DocTec SW200-1;
  - ETA CT 2801-2, 6497-2, 6498-1;
  - the ressortdebarillet pages for 1.45 × 0.10 × 380 × 10 and for the 2801 size;
  - Wikipedia "Ounce-force".
- **What is restated:** facts only, in our own words and layout, as small selections.
- **Suppliers:** fictional (Valtorre Microtechnique SA, Aciers Duval SA, Rubis Lumen SA).
- **Sellita:** its numbers are cited as facts with a link. The document is not reproduced, quoted or
  shipped.
- **Public domain:** Grossmann and MIL-STD-1472H.
- **Link-only:** Imrhan, ETA, TMI and Sellita.

This is our reading, not legal advice.

## 6. Not verified

- **Not re-fetched:** some ressortdebarillet sizes come from product titles (the HTTP 429 rate limit).
  The 1.45 × 0.10 × 380 × 10 and 2801 pages were not re-fetched.
- **Secondary or reported values:**
  - the Perrin Ø 5.00 mm crown comes from a search summary;
  - the Imrhan, MIL-STD and Sellita values are as reported in REAL_DATASHEETS.md (read there from
    pypdf text) and were not re-read in this session;
  - Imrhan's column order (smooth then knurled, loosening then tightening) is REAL_DATASHEETS.md's
    reading.
- **The core-ratio calibration rests on one real spring** (the 2801).
- **The Nivaflex data** are wire data, applied to strip.
