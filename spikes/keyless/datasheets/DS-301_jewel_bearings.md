# Rubis Lumen SA: Jewel holes and pivot bushings

| Document | Revision | Date | Status |
|---|---|---|---|
| RL-DS-301 | B | 2026-11-14 | Released |

> **About this document.** Rubis Lumen SA is a fictional supplier, used for this exercise only. The
> sizes are those of real catalogue items, cited per table, and the tolerances and friction come from
> a real jewel-bearing maker. **Load ratings are not published by any source we found.** Section 5
> calculates them, and its footnotes give the method and inputs.

## 1. Scope

This sheet covers two product lines:

- **RL-J:** synthetic ruby jewel holes, flat with a cylindrical hole (hole sizes in Table 1);
- **RL-B:** brass friction bushings (sizes in Table 2), for parts that do not justify a jewel.

Both lines are full scale (1:1) watch parts.

## 2. Ordering code

- **Jewels:** `RL-J-<hole>-<OD>`, with the hole in 1/100 mm and the outside diameter in 1/100 mm.
  Example: `RL-J-20-300` is a hole of Ø 0.20 mm with an outside diameter of Ø 3.00 mm.
- **Bushings:** `RL-B-<hole>-<OD>-<height>`, all in 1/100 mm.

## 3. RL-J jewel holes: sizes (Table 1)

Every size is offered with an outside diameter of Ø 2.60 or Ø 3.00 mm, except as marked.[^hsw]

| Hole Ø (mm) | OD 2.60 | OD 3.00 |
|---|---|---|
| 0.14 | RL-J-14-260 | RL-J-14-300 |
| 0.15 | RL-J-15-260 | RL-J-15-300 |
| 0.16 | RL-J-16-260 | RL-J-16-300 |
| 0.17 | RL-J-17-260 | – |
| 0.18 | – | RL-J-18-300 |
| 0.19 | RL-J-19-260 | RL-J-19-300 |
| 0.20 | RL-J-20-260 | RL-J-20-300 |
| 0.22 | RL-J-22-260 | RL-J-22-300 |
| 0.24 | RL-J-24-260 | RL-J-24-300 |
| 0.26 | RL-J-26-260 | RL-J-26-300 |
| 0.28 | RL-J-28-260 | RL-J-28-300 |
| 0.32 | RL-J-32-260 | RL-J-32-300 |

**Jewel height:** not stated by the size source. Specify it on order.

**Tolerances, from a ring-jewel maker's published capability:**[^bird]

| Feature | Value |
|---|---|
| Hole Ø, standard (holes under 0.080″, about 2 mm) | 0.0002″ total (5.1 µm) |
| Hole Ø, on request | 0.0001″ total (2.5 µm) |
| Hole-to-OD concentricity, specifiable | down to 0.0002″ TIR (5.1 µm) |
| Concentricity after mounting in a bushing | 0.0005″ TIR (12.7 µm); 0.0002 to 0.0003″ after truing |
| Surface finish of the bore | 2 µin (0.05 µm) and under |

**Outside-diameter tolerance:** not published in any source we found. Fit the jewel so that it seats
without force and with almost no free play,[^wrt3] in a straight plate hole slightly smaller than the
jewel's largest outside diameter.[^wrt2]

## 4. RL-B brass friction bushings: sizes (Table 2)

| Ordering code | Hole Ø (mm) | OD (mm) | Height (mm) |
|---|---|---|---|
| RL-B-10-070-25 | 0.10 | 0.70 | 0.25 |
| RL-B-11-100-35 | 0.11 | 1.00 | 0.35 |
| RL-B-12-150-55 | 0.12 | 1.50 | 0.55 |
| RL-B-16-200-70 | 0.16 | 2.00 | 0.70 |
| RL-B-30-100-30 | 0.30 | 1.00 | 0.30 |
| RL-B-40-150-55 | 0.40 | 1.50 | 0.55 |
| RL-B-60-200-70 | 0.60 | 2.00 | 0.70 |
| RL-B-80-260-80 | 0.80 | 2.60 | 0.80 |
| RL-B-100-260-80 | 1.00 | 2.60 | 0.80 |

All sizes are from the cited listing.[^ofrei] The source does not state the brass grade or the
tolerances.

## 5. Ratings

### 5.1 Recommended pivot clearance (diametral)

| Pivot Ø | Recommended hole | Basis |
|---|---|---|
| about 0.14 mm | pivot + 0.01 mm (0.14 mm pivot in a 0.15 mm hole) | [^wrt1] [secondary] |
| about 0.07 mm and below | proportionally smaller clearance | [^wrt1] [secondary] |

A hole equal to the pivot diameter has zero clearance and binds.[^wrt3] The pivot must never be larger
than the hole.

### 5.2 Friction and alignment

- **Friction:** steel on ruby, dry, μ ≈ 0.14. Lubrication lowers it.[^bird]
- **Friction moment of a pivot of Ø p under load S:** M = (1/3)·μ·S·p for a straight hole, and
  M = (1/6)·μ·S·p for an olive hole.[^bird]
- **Misalignment:** an olive (rounded) hole tolerates about 2 to 5° of shaft misalignment. A straight
  hole needs accurate alignment.[^bird]

### 5.3 Absolute maximum radial load (Table 3, calculated)

The radial load is limited by the bearing pressure on the projected area, p = F/(d·ℓ):[^ee] d is the
hole diameter and ℓ the engaged length of the pivot in the hole. The allowable pressures are:

- **RL-J:** p_max = 900 N/mm², that is corundum's compressive strength of 2700 MPa divided by S = 3
  for a brittle material;[^d1]
- **RL-B:** p_max = 115 N/mm², that is the lowest brass proof stress, 230 MPa, divided by S = 2.[^d2]

These ratings are for slow or intermittent turning, as in keyless works and the barrel. They do not
cover a continuously running train.

| Product | Hole Ø d (mm) | Engaged length ℓ (mm) | F_max radial (N) |
|---|---|---|---|
| RL-J | 0.14 | 0.15 | 18.9 |
| RL-J | 0.14 | 0.30 | 37.8 |
| RL-J | 0.20 | 0.15 | 27.0 |
| RL-J | 0.20 | 0.30 | 54.0 |
| RL-J | 0.32 | 0.15 | 43.2 |
| RL-J | 0.32 | 0.30 | 86.4 |
| RL-B-10-070-25 | 0.10 | 0.25 (full height) | 2.9 |
| RL-B-11-100-35 | 0.11 | 0.35 | 4.4 |
| RL-B-12-150-55 | 0.12 | 0.55 | 7.6 |
| RL-B-16-200-70 | 0.16 | 0.70 | 12.9 |
| RL-B-30-100-30 | 0.30 | 0.30 | 10.4 |
| RL-B-40-150-55 | 0.40 | 0.55 | 25.3 |
| RL-B-60-200-70 | 0.60 | 0.70 | 48.3 |
| RL-B-80-260-80 | 0.80 | 0.80 | 73.6 |
| RL-B-100-260-80 | 1.00 | 0.80 | 92.0 |

For any other engaged length, F_max = p_max·d·ℓ.

### 5.4 Absolute maximum axial load

Not published. Calculate it the same way, as F_ax,max = p_max × the actual contact area of the pivot
shoulder on the jewel or bushing face. Use p_max from 5.3 for the face material.

## 6. Handling and lubrication

- **Lubrication:** jewels can run dry in open systems. In closed systems, a light boundary film, or an
  oil cup recessed into the jewel, lowers friction.[^bird]
- **Pressing in:** press the jewel square into the plate. Do not press on the hole or on the bore
  surface.

## Sources

[^hsw]: H.S. Walsh, jewel holes (Bergeon 30712 series), hole × OD sizes, https://www.hswalsh.com/watch-parts-straps-batteries/jewel-holes-endstones-roller-pins-pallet-stones/jewel-holes/cat-8
[^ofrei]: Otto Frei, friction bushing refills, hole × OD × height, https://www.ofrei.com/page454.html
[^bird]: Bird Precision, Ring Jewel Bearings (tolerances, friction 0.14 and moment formulas citing Seitz, olive-hole misalignment of 2 to 5°, lubrication), https://catalog.birdprecision.com/Asset/Ring_jewel.pdf
[^wrt1]: Watch Repair Talk forum, "0.14 mm pivot for a 0.15 jewel, 0.01 mm side shake" (secondary, practitioner), https://watchrepairtalk.com/topic/27101-balance-staff-pivot-tolerance-to-jewel-hole
[^wrt2]: Watch Repair Talk forum, jewel seating discussion, https://watchrepairtalk.com/topic/30199-sizing-a-jewel-from-the-jewel-setting
[^wrt3]: Watch Repair Talk forum: "if you have a hole with the same diameter as a pivot you have zero clearance", https://watchrepairtalk.com/topic/14596-jewel-replace-size-question
[^ee]: Engineers Edge, journal bearing load on the projected area, https://engineersedge.com/calculators/journal_bearing_lubrication_15314.htm
[^d1]: Not published; calculated as p_max = 2700 MPa / 3. The 2700 MPa is from https://makeitfrom.com/material-properties/Synthetic-Sapphire. The factor S = 3 is the upper end of the "brittle materials" tier (2.5 to 3) at https://danotes.mech.uwa.edu.au/SSS/safety/safety.html, applied to ultimate strength as https://engineersedge.com/analysis/factor-of-safety-review.htm prescribes for brittle materials. See also AD-DS-201.
[^d2]: Not published; calculated as p_max = 230 MPa / 2. The 230 MPa is the lowest CW614N proof stress at https://www.aalco.co.uk/datasheets/Copper-and-Copper-Alloys-CW614N-Brass-Rod_31.ashx. The factor S = 2 is the upper end of the 1.5 to 2 tier at https://danotes.mech.uwa.edu.au/SSS/safety/safety.html. The brass grade of the listed bushings is not stated by the source, so this sheet assumes it.
