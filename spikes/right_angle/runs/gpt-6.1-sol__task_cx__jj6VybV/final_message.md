Submitted [winding.json](/app/submission/winding.json) and five binary STLs: stem, transfer wheel, ratchet, and two bearing bridges. The train provides nine stem turns per arbor turn in the required direction.

Local checks passed file validity, full sampled gear contact, frozen-movement clearance, retention, anchoring, square seating, and case bounds. All parts are single watertight solids below the triangle limit.

Difficulties encountered, in order: cutter-envelope memory exhaustion, initial crown/shaft interference, and tiny STL edges affecting watertightness. These were resolved using repeating sectors, underside relief with wider cutter sweeps, and mesh simplification.

No material ambiguity remained; the slower-wheel sweep was interpreted as three driver turns. Details and check results are in [REPORT.md](/app/submission/REPORT.md).

Outside access: none.