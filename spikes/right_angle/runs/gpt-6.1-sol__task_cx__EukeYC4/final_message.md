Submitted [winding.json](/app/submission/winding.json) and three binary STLs: stem/pinion/crown, bevel ratchet wheel, and captive bearing bridge. The drive gives the required direction at 10:1.

Local checks passed all stated requirements:

- All parts are watertight single solids within triangle limits.
- Zero movement overlap at rest.
- All 720 mesh samples passed: zero winding overlap; minimum backoff overlap `0.000981 mm³`, above `0.0002`.
- Clearance, retention, anchoring, bounds, and grip checks passed.
- Square-shell seating is 94.23%, with zero arbor interference.

Difficulties, in order: the initial coarse profile lost contact; wheel placement needed correction for direction; root asymmetry needed correction; degenerate STL triangles required cleanup and full rechecking.

No material ambiguities affected the result. Details are in [REPORT.md](/app/REPORT.md); scripts and numerical results are in `/app/scripts/`. All jobs have finished.

Outside access: none