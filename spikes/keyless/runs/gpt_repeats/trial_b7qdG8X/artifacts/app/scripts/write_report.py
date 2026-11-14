from pathlib import Path
import json
P=Path('/app');out=P/'submission'
f=json.loads((P/'scripts/functional_check.json').read_text())
summary='''Submitted eleven binary STL parts and keyless.json: a 32-tooth axial one-way crown clutch, a 20:20 generated bevel winding pair, a 6:36 spur reduction, a 60-tooth barrel retaining ratchet with a spring slide click, an independently selected setting pair and four fixed bearing/guide bodies. All parts are supplied in position 1 with spring coordinates zero. The setting bevel has relieved inner tooth faces to keep the intermediate selector stops neutral.

AT-0 was checked on the exported STL files: eleven single connected watertight solids, positive volumes, no submitted-body interference above 0.0002 mm^3, all specified retention shifts obstructed, case bounds respected except the permitted stem extension. Maximum file size is 9516 triangles. The crown reaches x=13.25 mm, 1.05 mm beyond the case side at y=0. The supplied fixed minute_post overlaps its supplied dial_plate seat; that fixed seating was excluded from moving-body interference checks.

Local checks used manifold boolean intersection volumes at the stated 0.0002 mm^3 contact tolerance. A series follower search moved each driven gear the least amount in its expected direction needed to clear contact; it did not impose ideal gear ratios. One forward crown turn produced 59.7306 degrees positive arbor motion (6.0271 crown turns per arbor turn). A 90-degree forward and back setting sequence produced 14.6109 degrees and 14.2345 degrees minute-wheel travel. Those paths had no other-body interference. The independent 20-degree arbor advance was swept at 0.5-degree increments; a backward crown turn was swept at 3-degree increments with the arbor held. Both had clear paths with clutch slide under 0.05265 mm, inside its 0.1 mm available travel. Geometric pull and push paths were checked in 0.03 mm increments. At the 0.225, 0.450 and 0.675 mm selector test stops the winding clutch is separated and the setting train is neutral; a two-phase scan at 0.675 mm found maximum setting contact volume 0.00012388 mm^3. At 0.9 mm it engages in both directions.

The click geometry encounters its locking face after approximately 3.12 degrees of run-back from 45 degrees. That predicts about 47.93 hours reserve using the supplied six-turn capacity. Analytical face-normal checks with static friction 0.51 show that the click and clutch ramps can lift their spring slides, whereas their locking faces cannot cam those slides away. These checks do NOT implement the complete multi-contact friction solver, forty-step release/tap protocol, or every acceptance restart and recoupling sequence. Consequently AT-1 through AT-6 are honestly marked not_tested as complete acceptance steps, rather than converting partial geometric checks into full passes.

Difficulties and dead ends, in order: (1) A self-locking worm concept was rejected because it could obstruct the independent arbor advance in AT-3. (2) Initial full 3D swept boolean envelopes generated disconnected slivers and an 871506-triangle bevel; an export job terminated with exit 137. Generating the conical conjugate section in 2D and extruding it avoided that failure. (3) A clockwise click outline initially produced an empty extrusion, corrected by orienting the polygon. Coincident clutch tessellation boundaries also produced STL degeneracies; overlapping backing rings, matching angular segmentation and removal of zero-area triangles yielded closed exported solids. (4) Initial setting-wheel inner faces touched the pinion during partial selection; a star-shaped relief made the tested intermediate stops neutral while retaining the end-position mesh.

Ambiguities: on_stem explicitly inherits crown rotation but does not explicitly state whether crown translation is inherited. Physical stem collars make the clutch follow the pull in either interpretation. The brief gives force ordering and friction coefficients but no preload or tap-force magnitudes or numerical contact tie-breaking algorithm; the local checker therefore does not claim to reproduce the complete rig.

Outside access: none'''
(out/'report.json').write_text(json.dumps({'steps':{'assemble':'pass','wind':'not_tested','hold':'not_tested','run':'not_tested','backward':'not_tested','set':'not_tested','return':'not_tested'},'summary':summary},indent=2))
(out/'REPORT.md').write_text('''Eleven keyless-work parts are submitted in `parts/`, with their mobiles and supports in `keyless.json`.

The winding path uses a one-way axial clutch, a 1:1 bevel pair and a 6:36 spur reduction. A separate spring click holds the barrel arbor. Pulling the stem disengages winding and selects the setting bevel pair. The 32-tooth clutch permits backward crown rotation and independent positive arbor rotation.

Exported solids pass the local assembly, bounds and retention checks. Series geometric contact following gives 59.73° arbor winding per crown turn, and 14.61° forward / 14.23° reverse minute-wheel movement for 90° crown setting turns. Pull/push, backward-crown and independent-arbor paths were swept without other-body interference. The click geometry predicts 3.12° run-back and about 47.93 hours reserve.

The complete friction-and-tap acceptance rig was unavailable. The local checker follows geometric contacts in expected directions and checks ideal ramp friction analytically; it is not a general friction solver. Thus the JSON claims AT-0 pass and marks the six complete dynamic acceptance steps not_tested. Detailed measurements and limitations are in `report.json`; reproducible build and checking scripts are in `/app/scripts/`.

Difficulties, in order: a self-locking worm concept conflicted with free arbor advance; full 3D envelope booleans produced excessive triangles and fragments and one export terminated; a reversed polygon and coincident clutch mesh boundaries needed correction; partial setting engagement needed additional inner-tooth relief. The final profiles use 2D generated sections and closed mesh exports.

The meaning of inherited axial motion for `on_stem`, and the precise numerical treatment of friction/tap ties, were not fully explicit. Stem collars address the former; complete dynamic acceptance remains unverified.

Outside access: none
''')
print('report bytes',(out/'report.json').stat().st_size)
