# Part printing: process sheet

| Document | Revision | Date | Status |
|---|---|---|---|
| DS-W03 | A | 2026-11-14 | Released |

**Issued by:** the print service. **Document type:** process sheet.

## 1. Scope

Additive manufacture of movement parts at demonstration scale, from one STEP file per part. All lengths in
millimetres.

## 2. Smallest feature

| Quantity | Value |
|---|---|
| Smallest printable feature | 0.2 mm |

## 3. What the smallest feature means for a part

The part is divided into cubic voxels of side 0.05 mm whose centres lie at 0.05 x k + 0.0113 mm along x, y and z
(k any integer); a voxel is solid when its centre is inside the part. A solid voxel survives when its centre is at
least 0.075 mm (1.5 voxels) from the centre of the nearest voxel that is not solid. The printable body is every
solid voxel whose centre is within 0.05 mm (1 voxel) of the centre of a surviving voxel. The part is printable
when at least one voxel survives and no solid voxel's centre is further than 0.2 mm from the centre of the nearest
voxel of the printable body.

## 4. Size accuracy

Every surface of a printed part lies within the size accuracy of its drawn position, in any direction: a part may
come out that much larger or that much smaller than drawn, all over.

| Quantity | Value |
|---|---|
| Size accuracy | +/- 0.01 mm |
