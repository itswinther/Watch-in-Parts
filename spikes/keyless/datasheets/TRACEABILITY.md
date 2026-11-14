<!-- NOT-FOR-AGENT: secret. Traces every implied check to a datasheet value. Never copied into the agent image. -->
# Datasheets v2: traceability (secret)

Written by Mikael + Claude (workstream A), 14 Nov 2026. This file is for the graders and the judges.
The agent receives only `DS-*.md` and `INDEX.md`.

## 0. Build rule (for the keyless builder session)

- **What build_task.py copies:** only `datasheets/DS-*.md` and `datasheets/INDEX.md`, into the agent
  image (for example `/app/datasheets/`).
- **What must fail the build:** `TRACEABILITY.md`, or any file containing `NOT-FOR-AGENT`, reaching the
  image. The first line of this file carries that marker, so the existing `assert_clean()` catches it
  once the datasheets directory is inside the walked `env_dir`. Also add `TRACEABILITY.md` to
  `SECRET_DOCS`, or make an explicit check.
- **`.harborignore`** in this folder lists `TRACEABILITY.md`.
- This session did **not** edit `build_task.py`.

## 1. Scale decision: full scale, no scaling

The task's case is Ø 17.4 mm (`CASE_RADIUS = 8.7`). That is a real 7¾‴ calibre:

- 7.75 × 2.2558 mm = 17.48 mm (https://en.wikipedia.org/wiki/Ligne);
- the ETA 2671 is 7¾‴, Ø 17.20 mm (https://portal.eta.ch/en/mecaline/2671-2671-5.html).

The supplied geometry is also of watch size:

- spur module 0.2 and face module 0.15 in the reference;
- a stem square of about 0.62 mm;
- a crown of Ø 2.0 mm in the reference.

The task is therefore not an enlarged printable model. All datasheets are 1:1, with no scaling factor,
and each says "full scale (1:1)". Two points are larger than in a real 7¾‴:

- **Movement height:** the plates span z ±3.2 mm, against the 2671's 4.80 mm.
- **Modules:** they are on the large side for keyless works.

Neither changes a rating; both only add margin.

## 2. Implied checks → datasheet value → formula → source

The checks below are written in terms of the agent's choices:

- the variant V from DS-101;
- the crown Ø D;
- the gear stages i;
- the jewel or bushing sizes.

| # | Implied check (the brief's blanket clause) | Datasheet value used | Formula | Source of formula and inputs |
|---|---|---|---|---|
| 1 | Reserve: power reserve ≥ 38 h from full wind (`RESERVE_MIN`) | DS-101 Table 3: N(V) | reserve = N(V) × 8 h (`BARREL_HOURS_PER_TURN`) | N: DS-101 [^d1] (area conservation; thickness correction and r = 16·t from watchesbysjx 2025). 8 h: Wikipedia Mainspring. 38 h: ETA CT 2824-2 |
| 1a | The spring fits: barrel inner Ø D(V) plus the drum wall fits the free space at `BARREL_AXIS` | DS-101 Table 1: D(V) | D(V)/2 + wall ≤ 8.7 − 4.371 = 4.33 mm (barrel axis to case centre is 4.371 mm) | Geometry from constants.py. The drum wall is not published: the builder states it or lets the agent design it |
| 2 | Tooth bending under mainspring torque ≤ allowable | DS-101 Table 2: M_el(V). DS-201 §8: σ_allow (brass 115, steel 750 or 725 MPa) | At a stage with torque M_s: F_t = M_s/r_p. Lewis σ = F_t/(b·m·Y) (NPTEL eq. 7.12), or, for non-involute teeth, the cantilever σ = 6·F_t·h/(b·t²) (NPTEL eq. 7.6), measured on the agent's tooth. M_s = M_el at the ratchet and barrel gear, and M_el/(product of ratios to that stage) upstream | NPTEL Machine Design II, Lecture 7 (https://archive.nptel.ac.in/content/storage2/courses/112106137/pdf/2_7.pdf). M_el: DS-101 [^d3]. Allowables: Aalco and Alleima ÷ Juvinall S = 2 (UWA) |
| 3 | The click and its spring hold the mainspring torque | DS-101: M_el(V). DS-201 Table 7: μ steel/steel 0.5 to 0.8 (static), brass/steel 0.51. DS-201 §8 allowables | Tooth load F = M_el/r_tip. (a) **Draw:** with μ = 0, the contact normal's moment about the click pivot must pull the click into the ratchet. Since μ only adds margin, μ = 0 is the conservative case. (b) The click tooth and the ratchet tooth under F stay ≤ σ_allow (as in row 2). (c) The click spring is not loaded by M_el if the draw holds; its bending stress at working deflection ≤ steel allowable (σ = 6M/(b·t²)) | Friction: Engineering ToolBox. Stress: codecogs. Material: Alleima / Aalco |
| 4 | Winding torque at the crown ≤ finger torque | DS-501 Table 3: T_rec(D) = 4.20·D N·mm. DS-101: M_el(V) | T_crown = M_el(V)/i, where i is crown turns per barrel turn, frictionless. Check T_crown ≤ T_rec(D) | T = μ·F·D, with μ = 0.6 (Seo & Armstrong 2009), F = 0.15 × 46.7 N (Mathiowetz 1985 via topendsports; Rohmert 15 % via Ergoweb) |
| 5a | Pivots fit their holes | DS-301 Tables 1 and 2 (hole sizes). §5.1: clearance about 0.01 mm at about 0.14 mm | Hole must be a catalogue size, and 0 < hole − pivot. Recommended: hole − pivot ≈ 0.01 mm for pivots of about 0.14 mm; a grader tolerance band is the builder's choice (e.g. 0.005 to 0.03 mm) | Watch Repair Talk (secondary, practitioner). Sizes: H.S. Walsh, Otto Frei |
| 5b | Pivot load ≤ rating | DS-301 §5.3: p_max = 900 N/mm² (jewel), 115 N/mm² (brass bushing) | F_radial ≤ p_max·d·ℓ, with F_radial the bearing reaction from the tooth forces at M_el | p = F/(d·ℓ): Engineers Edge. 2700 MPa: makeitfrom. S: UWA/Juvinall and Engineers Edge |
| 6 | Stem torque ≤ rating | DS-401 Table 2: T_yield = 0.208·a³·837; recommended ÷ 2 | T_crown (row 4) ≤ the recommended value for the agent's square size a | Torsion 0.208: UoK lecture notes. von Mises: Wikipedia. Rp 1450: Alleima |
| 7 | Stem positions | DS-401 §4: 2 positions, travel about 1 mm | `PULL = 0.9` lies within "about 1 mm" | watchesbysjx (2026); Eterna 2824-2 manual |

**Which variants pass row 1** (N × 8 h ≥ 38 h):

| Variant | N × 8 h | Passes? | Note |
|---|---|---|---|
| A | 46 h | Yes | |
| B | 44 h | Yes | |
| C | 35 h | **No** | A real selection trap: a plausible small spring that falls short |
| D | 81 h | Yes | N = 10.1, above `CAPACITY_TURNS = 6`. The builder must decide whether the simulation uses N(V) or caps it at 6 |
| E | 54 h | Yes | |
| F | 48 h | Yes | N = 6.0, which matches `CAPACITY_TURNS` exactly; the natural pick |
| G | 47 h | Yes | |
| H | 50 h | Yes | Barrel D 9.0 does not fit the 8.66 mm envelope (row 1a) |
| I | 39 h | Yes | Barrel D 10.5 does not fit the 8.66 mm envelope (row 1a) |

**How tight the checks are, for a sane design.** For variant F, M_el = 4.32 N·mm.

- **Row 2:** a reference-like ratchet (pitch radius about 2.7 mm, module about 0.22, face 0.5 mm,
  Y ≈ 0.3) carries F_t ≈ 1.6 N. Then σ ≈ 1.6/(0.5 × 0.22 × 0.3) ≈ 48 MPa, against 115 MPa for brass.
  It fails only for thin or short teeth.
- **Row 4:** at the band edge i = 3 (`WIND_BAND`), T_crown = 1.44 N·mm, against T_rec(Ø 2.0) = 8.4 N·mm.
  It cannot fail inside the winding band with any listed spring: the worst case is I, 6.27/3 = 2.1 N·mm.
  This is realistic, since watches are easy to wind. Keep it as a check of reading DS-501 and the
  units, not as a discriminator.
- **Row 5b:** keyless reactions are around 1 N, against ratings of 3 to 90 N. It fails only on gross
  misuse.

The discriminating rows are 1/1a (picking and fitting the spring), 2, 3 and 5a (fits).

## 3. How each derived number was computed

The computations ran in Docker (`python:3.12-slim`, 2 GB memory) with the script below. They can be
rerun the same way.

```python
import math
E=220000.0; RP=2475.0; DE=0.003          # MPa (VAC 45/5), MPa (aged, 90 % CW), mm (watchesbysjx correction)
for n,b,t,L,D in [("A",0.90,0.08,240,7.0),("B",0.70,0.08,355,7.5),("C",0.70,0.09,200,7.0),
                  ("D",0.87,0.07,310,7.9),("E",1.25,0.085,300,8.0),("F",1.45,0.085,240,7.5),
                  ("G",1.30,0.08,220,7.0),("H",1.20,0.10,300,9.0),("I",0.90,0.13,300,10.5)]:
    R=D/2; te=t+DE; r=16*t; A=L*te/math.pi
    N=(math.sqrt(r*r+A)-r)/te-(R-math.sqrt(R*R-A))/te           # turns of development
    k=E*b*t**3/(12*L)                                            # N.mm/rad
    M_N=k*2*math.pi*N; M_el=RP*b*t*t/6; sig_N=6*M_N/(b*t*t)
# finger: T = 0.6*F*D, F = 46.7 N (women's mean max), 80.1 N (men's), 0.15*46.7 N (recommended)
# stem:   T = 0.208*a**3*1450/sqrt(3), recommended /2
# jewel:  F = (2700/3)*d*l ; bushing: F = (230/2)*d*h
```

- **DS-101 N:** the strip's area L·t′ is conserved, with t′ = t + 0.003 mm.
  - Wound up, it is an annulus on the core of radius r: n_w = (√(r² + L·t′/π) − r)/t′.
  - Let down, it is an annulus against the wall of radius R: n_d = (R − √(R² − L·t′/π))/t′.
  - N = n_w − n_d.
  - r = 16·t (Defossez, via watchesbysjx 2025).
  - This is the textbook geometric result the article describes in words; its figures were not readable.
- **DS-101 torque:** M = E·b·t³·θ/(12·L), linear from the let-down state, frictionless. This
  under-represents the real torque at let-down (free-shape preload) and over-represents the delivered
  torque (coil friction). Hence every check uses **M_el = Rp0.2·b·t²/6**: the largest moment that the
  strip's section carries elastically, a strict upper bound on the torque whatever the free shape.
- **DS-101 stress at N:** σ = 6·M_N/(b·t²). Every value (851 to 1574 MPa) is below Rp0.2 = 2475 MPa, so
  Table 4 is internally consistent.
- **DS-201 allowables:** basis ÷ S.
  - S = 2 (upper end of Juvinall's "well-known materials" tier) for brass and steel, on yield.
  - S = 3 (upper end of "brittle materials") for corundum, on compressive ultimate.
- **DS-301 loads:** projected-area pressure.
- **DS-401 stem:** square-section torsion with von Mises shear yield.
- **DS-501:** two-pad Coulomb friction, T = 2·μ·F·D/2. The pound-force norms are converted at
  4.448 N/lbf.

**Assumptions stated in the sheets themselves:**

- The Nivaflex 45/5 data are wire data, applied to strip.
- The brass grade of the Otto Frei bushings is assumed to be CW614N-class.
- The steel stem has strip proof strength (1450 MPa, the lowest Alleima row).
- No jewel outside-diameter tolerance, jewel height, mainspring tolerance, bridle slipping torque,
  arbor square, crown-thread rating or travel tolerance was published. Each is marked "not published"
  rather than invented.

## 4. Source register (every URL used in DS-*.md)

- **Mainsprings:**
  - ressortdebarillet.ch:
    - https://en.ressortdebarillet.ch/collections/ressort-de-barillet-epaisseur-0-102
    - …/products/0-90-x-08-x-240-x-7-mecanique
    - …/0-70-x-08-x-355-x-7-5-non-automatique
    - …/0-70-x-09-x-200-x-7-non-automatique
    - …/ressort-de-barillet-0-87-x-0-07-x-310-x-7-9-db-end-jaeger-le-coultre-818
    - …/1-25-x-085-x-300-x-8-automatique
    - …/1-45-x-085-x-240-x-7-5-automatique
    - …/1-30-x-08-x-220-x-7-automatique
    - …/1-20-x-10-x-300-x-9-automatique
    - …/0-90-x-13-x-300-x-10-5-automatique
  - Barrel design: https://watchesbysjx.com/2025/11/in-depth-balancing-mainspring-dimensions-inside-the-barrel.html
  - Spiral-spring formula: https://calculator.academy/spiral-torsion-spring-calculator/
  - Strip bending: https://www.codecogs.com/page/1150/v/3359
  - Barrel speed: https://en.wikipedia.org/wiki/Mainspring
- **Movements:**
  - ETA 2671: https://portal.eta.ch/en/mecaline/2671-2671-5.html
  - ETA 2824-2: https://shopb2b.eta.ch/technicaldocuments/index/pdf/id/1883
  - Ligne: https://en.wikipedia.org/wiki/Ligne
- **Materials:**
  - Nivaflex 45/5: https://www.cousinsuk.com/pdf/skus/9601_9596_nivaflex_45_5.pdf (text extracted with
    pypdf in Docker)
  - Brass CW614N: https://www.aalco.co.uk/datasheets/Copper-and-Copper-Alloys-CW614N-Brass-Rod_31.ashx
  - Alleima 20C: https://alleima.com/en/technical-center/material-datasheets/strip-steel/alleima-20c
  - C100S: https://www.mfgrobots.com/Article/material/metal/37153.html (secondary)
  - Sapphire: https://makeitfrom.com/material-properties/Synthetic-Sapphire (secondary)
  - Ruby: https://holowiki.org/wiki/Ruby (secondary)
- **Friction and safety factors:**
  - Friction: https://engineeringtoolbox.com/friction-coefficients-d_778.html
  - Basis of the allowable: https://engineersedge.com/analysis/factor-of-safety-review.htm
  - Juvinall tiers: https://danotes.mech.uwa.edu.au/SSS/safety/safety.html
- **Jewels:**
  - Bird Precision: https://catalog.birdprecision.com/Asset/Ring_jewel.pdf (text extracted with pypdf in
    Docker)
  - H.S. Walsh: https://www.hswalsh.com/watch-parts-straps-batteries/jewel-holes-endstones-roller-pins-pallet-stones/jewel-holes/cat-8
  - Otto Frei: https://www.ofrei.com/page454.html
  - Watch Repair Talk:
    - https://watchrepairtalk.com/topic/27101-balance-staff-pivot-tolerance-to-jewel-hole
    - https://watchrepairtalk.com/topic/30199-sizing-a-jewel-from-the-jewel-setting
    - https://watchrepairtalk.com/topic/14596-jewel-replace-size-question
  - Bearing pressure: https://engineersedge.com/calculators/journal_bearing_lubrication_15314.htm
- **Crowns and stems:**
  - Esslinger: https://www.esslinger.com/double-o-ring-waterproof-watch-crown-assortment-83-015-9-stainless-steel-12-pieces/
  - Perrin: five product pages, listed in DS-401
  - Keyless works: https://watchesbysjx.com/2026/08/keyless-works-explained.html
  - Eterna 2824-2 manual: https://www.manualslib.fr/manual/627394/Eterna-Eta-2824-2.html?page=5
  - Torsion of a square: https://prof.uok.ac.ir/Ka.Karami/Courses/Mechanic-of-Material-II/06-Torsion-of-Noncircular-Members.pdf
  - von Mises: https://en.wikipedia.org/wiki/Von_Mises_yield_criterion
- **Human factors:**
  - Mathiowetz 1985: https://pubmed.ncbi.nlm.nih.gov/3970660/
  - Norm tables: https://www.topendsports.com/testing/tests/pinch-grip-strength.htm
  - Fingertip friction: https://stacks.cdc.gov/view/cdc/215047
  - Rohmert 15 %: https://ergoweb.com/static-load/
  - Pound-force: https://en.wikipedia.org/wiki/Pound_(force)
- **Gear stress (graders only):** https://archive.nptel.ac.in/content/storage2/courses/112106137/pdf/2_7.pdf

## 5. Licensing basis

- **What is restated:** facts (dimensions, material properties, norm means), as a small cited selection
  in our own words, layout and tables. STANDARDS.md 4.6 applies: facts are restated with a citation, and
  no maker's document text, layout, table, drawing or logo is copied.
- **Selections:**
  - About 9 mainspring sizes out of a catalogue of hundreds.
  - 6 of the 13 rows of Alleima's strength table.
  - 9 of the 34 Otto Frei bushing sizes.
  - The jewel sizes are a product list, not a document table.
- **Supplier names:** fictional (Valtorre Microtechnique SA, Aciers Duval SA, Rubis Lumen SA). Real
  makers and sellers appear only as cited sources, never as branding.
- **Not used:** no Générale Ressorts, Seitz, NIHS or ISO table was reproduced. "Nivaflex 45/5 type" names
  a material grade for identification; it is not branding.

This is our reading, not legal advice.

## 6. Not verified

- Several ressortdebarillet product pages hit an HTTP 429 rate limit on re-fetch. Their sizes are taken
  from the product titles in search results.
- The watchesbysjx keyless-works URL is taken from STANDARDS.md and was not re-fetched in this session.
- The Perrin 5.00 mm Tissot crown diameter is taken from a search summary.
- The Esslinger assortment's intermediate sizes were not listed, so only the 4.0 and 7.0 mm ends are
  used.
- The mfgrobots C100S, makeitfrom and holowiki data are secondary.
- The 0.01 mm clearance rule comes from a practitioner forum.
- The 38 h minimum is ETA's figure for the 2824-2. For the 2671, ETA's product page gives a typical
  44 h; a 38 h minimum for the 2671 was seen only in a search summary of an ETA sheet.
