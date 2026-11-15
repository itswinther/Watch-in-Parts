# Mainspring barrels, demonstration-scale series: catalogue sheet

| Document | Revision | Date | Status |
|---|---|---|---|
| DS-W01 | A | 2026-11-14 | Released |

**Issued by:** the barrel supplier. **Document type:** catalogue sheet.

## 1. Scope

Going barrels with an integral toothed drum, for demonstration-scale movements. Each barrel has two bodies on one
axis: the toothed drum, which the mainspring turns and which drives the train, and the arbor, which holds the
mainspring's inner end on its core and carries a winding square for a ratchet. The drum turns on the arbor's
core with a radial clearance; the two bodies do not touch. Teeth: involute spur teeth, addendum 1.0 x module,
dedendum 1.25 x module. All lengths in millimetres.

The arbor core radius of every barrel in this series is one third of the inner radius of its spring chamber
(the hub proportion of Grossmann, *Lessons in Horology*, art. 108 to 111, and Saunier, art. 517).

Each barrel is delivered with its mainspring fitted: a strip of the spring alloy of VM-DS-101 (section 3 of that
sheet), of the height h, thickness t and length L given in section 2, at the scale of this series.

## 2. Catalogue

| Part no. | Teeth | Module (mm) | Pressure angle (degrees) | Tip diameter (mm) | Root diameter (mm) | Tooth thickness on the pitch circle, arc (mm) | Drum height (mm) | Spring chamber inner diameter (mm) | Arbor pivot radius (mm) | Arbor length (mm) | Arbor core radius (mm) | Winding square side (mm) | Mainspring fitted, h x t x L (mm) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BR-096-66 | 96 | 0.2 | 25 | 19.6 | 18.7 | 0.284 | 1 | 12.12 | 0.5 | 6.6 | 2.02 | 1.4 | 0.78 x 0.162 x 437 |
| BR-096-45 | 96 | 0.2 | 25 | 19.6 | 18.7 | 0.284 | 0.6818 | 12.12 | 0.5 | 4.5 | 2.02 | 1.4 | 0.63 x 0.162 x 437 |
| BR-096-30 | 96 | 0.2 | 25 | 19.6 | 18.7 | 0.284 | 0.4545 | 12.12 | 0.5 | 3 | 2.02 | 1.4 | 0.4 x 0.162 x 437 |

Every barrel is made for every speed class of section 4; a barrel is ordered for one speed class.

## 3. The barrels as supplied

Each barrel is supplied as a mesh in its assembled position (binary STL, millimetres): the drum and the arbor
together, as one mesh. In that position, for every barrel of the series:

| Quantity | Value |
|---|---|
| Axis | the vertical line x = 0 mm, y = 0 mm |
| Bore of the drum | radius 2.0367 mm |
| Arbor, pivots and plain sections | round, radius 0.5 mm |
| Arbor core (inside the drum's bore) | over the height of the toothed drum, radius 2.02 mm |
| Spring chamber inside the drum (not modelled in the mesh) | inner diameter 12.12 mm |
| Winding square | side 1.4 mm, sides parallel to x and y |

and for each barrel:

| Part no. | Mesh | Toothed drum | Arbor | Winding square | Volume of the mesh (mm3) |
|---|---|---|---|---|---|
| BR-096-66 | `/app/supplied/BR-096-66.stl` | z 0 mm to z 1 mm | z -1 mm to z 5.6 mm | z 3.3 mm to z 4.9 mm | 293.7 |
| BR-096-45 | `/app/supplied/BR-096-45.stl` | z 0 mm to z 0.6818 mm | z -0.6818 mm to z 3.8182 mm | z 2.25 mm to z 3.3409 mm | 200.2 |
| BR-096-30 | `/app/supplied/BR-096-30.stl` | z 0 mm to z 0.4545 mm | z -0.4545 mm to z 2.5455 mm | z 1.5 mm to z 2.2273 mm | 133.5 |

## 4. Speed classes

The steady running speed of the barrel in the movement, for each speed class.

| Speed class | Barrel speed, steady running | Running sense, seen from the dial side |
|---|---|---|
| A | 1 turn every 5 h | clockwise |
| B | 1 turn every 6 h | clockwise |
| C | 1 turn every 7 h | clockwise |
| D | 1 turn every 8 h | clockwise |
| E | 1 turn every 9 h | clockwise |
| F | 1 turn every 10 h | clockwise |
