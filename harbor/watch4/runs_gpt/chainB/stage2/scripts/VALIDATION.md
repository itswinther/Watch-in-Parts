Stage 2 submission
==================
22 STEP parts. Added day_pinion to transfer; added the day mobile with day_wheel
and day_hand; added day_cock; bored the existing upper_bridge for the day arbor.
All received mobile names, axes, mobile part membership and bytes, existing
meshes, and original hand entries are preserved.

The new 12:144 module 0.16 external spur pair takes transfer (-1/2 revolution
per hour) to day (+1/24 revolution per hour). Positive means clockwise here.
New mobile axis (-0.48, 0), 16.7687 mm from the hour axis; hand reach 4.20385 mm.

Local checks use the supplied STEP loader at the specified tolerances and
manifold3d solids, cached under /app/check_cache for subsequent runs.
- All assembled mobile/fixed and fixed/fixed intersection volumes <= 0.01 mm3.
- All mobiles clear fixed parts at all 72 five-degree rotation samples.
- Every mobile is held in all six 0.3 mm displacement tests; the smallest
  measured retention intersection is 0.0658 mm3 (barrel).
- All six meshes pass their full specified sample counts. No jams. All maximum
  sampled gaps < 0.0281 mm. All minimum drive intersections > 0.0201 mm3.
  New mesh: gap <= 0.027304 mm; drive intersection >= 0.040683 mm3.
- All nonmeshing pairs clear at both sets of 144 speed-related samples.
- Exact fraction speeds: hour 1/12, minute 1, seconds 60, day 1/24 rev/hour CW.
- Largest moving radial bound is day at 20.17944 mm; fixed radius <= 19.80001 mm.
  Complete height is 11.50001 mm. Limits: 20.7 mm and 13.4 mm.
- New and modified parts pass the specified voxel opening test at grid offsets
  0 and 0.023 mm. Largest defect distance 0.12248 mm, under 0.2 mm.
- Original hand parts and their coaxial arrangement are unchanged.

Reproduce with:
  python3 scripts/build_day.py
  python3 scripts/check_movement.py basic
  python3 scripts/check_movement.py mesh
  python3 scripts/check_additional.py pairs
  python3 scripts/check_additional.py print
  python3 tools/submit.py

Difficulties encountered, in order: initial geometry inspection was relatively
slow; a validation assertion compared a Fraction with a floating-point reciprocal,
which was corrected to use exact rational arithmetic. No geometric redesign was
needed. No specification or supplied-tool fault was encountered. The grader is
unavailable, so these are local reproductions of its published tests. Printable
checks sample two grid alignments; they do not establish every possible alignment.

Outside access: none
