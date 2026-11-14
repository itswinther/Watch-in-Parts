# DS-W01 Supplied mainspring barrel

| Document | Revision | Date | Status |
|---|---|---|---|
| DS-W01 | A | 2026-11-14 | Released |

**Source:** the supplied part, `/app/supplied/barrel.stl`. It is not a catalogue or a cited document.

## 1. Supply

| Item | Value |
|---|---|
| File | `/app/supplied/barrel.stl` (binary STL, millimetres) |
| Mobile name in the movement files | `barrel` (reserved) |
| Bodies | one rigid body: the toothed wheel and its arbor turn together |
| Axis | the vertical line x = 0 mm, y = 0 mm; the mesh is supplied in its assembled position |

## 2. Geometry

| Quantity | Value |
|---|---|
| Teeth | 96 |
| Module | 0.2 mm |
| Pitch diameter | 19.2 mm |
| Tooth form | involute, pressure angle 25 degrees |
| Tip radius (measured on the supplied mesh) | 9.8 mm |
| Root radius (measured on the supplied mesh) | 9.35 mm |
| Tooth thickness on the pitch circle (arc, measured on the supplied mesh) | 0.284 mm |
| Tooth phase | one tooth centred on the +x direction (0 degrees from +x, measured) |
| Wheel | z 0 mm to z 1 mm |
| Arbor | radius 0.5 mm, z -1 mm to z 1.6 mm |
| Volume (measured on the supplied mesh) | 288.9 mm3 |

## 3. Motion

Seen from the dial side (+z). The barrel turns at a steady speed; there is no escapement.

| Version | Sense | Speed |
|---|---|---|
| 8-hour barrel (for `movement.json`) | clockwise | 1 turn every 8 h |
| 6-hour barrel (for `variant_6h.json`) | clockwise | 1 turn every 6 h |

The two versions are the same part, in the same place, with the same teeth; only the speed differs.
