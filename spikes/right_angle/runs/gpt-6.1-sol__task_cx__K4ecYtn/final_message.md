Submitted [winding.json](/app/submission/winding.json) and four binary STLs: the stem/pinion, arbor face gear, and two bearings. The drive gives nine stem turns per arbor turn, with the required direction.

Local checks passed file validity, single-shell geometry, movement clearance, drive contact, retention, seating, anchoring, and bounds. Across 649 drive samples, maximum overlap was 0.000000199 mm³; minimum backstep contact was 0.00147 mm³. Square-shell coverage was 88.8%, with zero square intrusion. Results are in [checks.json](/app/scripts/checks.json).

Difficulties, in order: dense tooth replication exhausted memory; simplifying the cached tooth resolved that. Coincident sector seams then produced invalid STL geometry. A component diagnostic required unavailable `networkx`; rounding and further simplification did not repair the seams. Slight sector overlap resolved them. The final build was reproduced and rechecked.

I interpreted the sampling wording as nine stem revolutions per slower arbor revolution, and the seating shell as an outward 0.04 mm offset around the square. Supplied geometry was unchanged. No jobs remain running.

Outside access: none