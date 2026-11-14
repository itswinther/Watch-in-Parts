Eleven keyless-work parts are submitted in `parts/`, with their mobiles and supports in `keyless.json`.

The winding path uses a one-way axial clutch, a 1:1 bevel pair and a 6:36 spur reduction. A separate spring click holds the barrel arbor. Pulling the stem disengages winding and selects the setting bevel pair. The 32-tooth clutch permits backward crown rotation and independent positive arbor rotation.

Exported solids pass the local assembly, bounds and retention checks. Series geometric contact following gives 59.73° arbor winding per crown turn, and 14.61° forward / 14.23° reverse minute-wheel movement for 90° crown setting turns. Pull/push, backward-crown and independent-arbor paths were swept without other-body interference. The click geometry predicts 3.12° run-back and about 47.93 hours reserve.

The complete friction-and-tap acceptance rig was unavailable. The local checker follows geometric contacts in expected directions and checks ideal ramp friction analytically; it is not a general friction solver. Thus the JSON claims AT-0 pass and marks the six complete dynamic acceptance steps not_tested. Detailed measurements and limitations are in `report.json`; reproducible build and checking scripts are in `/app/scripts/`.

Difficulties, in order: a self-locking worm concept conflicted with free arbor advance; full 3D envelope booleans produced excessive triangles and fragments and one export terminated; a reversed polygon and coincident clutch mesh boundaries needed correction; partial setting engagement needed additional inner-tooth relief. The final profiles use 2D generated sections and closed mesh exports.

The meaning of inherited axial motion for `on_stem`, and the precise numerical treatment of friction/tap ties, were not fully explicit. Stem collars address the former; complete dynamic acceptance remains unverified.

Outside access: none
