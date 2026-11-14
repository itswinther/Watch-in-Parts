import json
from pathlib import Path
root=Path('/app');out=root/'submission'
r=json.loads((root/'scripts/model_results.json').read_text());a=json.loads((root/'scripts/audit_results.json').read_text())
assert a['assemble_pass']
assert 3<=r['wind']['ratio']<=12 and abs(r['wind']['minute'])<=1
assert r['run']['coupled_wind_degrees']>1 and r['hold']['reserve_hours']>=38
assert -4<=r['backward']['arbor_change']<=1 and abs(r['backward']['minute_change'])<=1 and r['backward']['coupled_wind_degrees']>1
for stage in ['set','return']:
 for stop in r[stage]['stops']:
  for t in stop['tests']:assert not(t['wind']>1 and abs(t['set'])>1)
  f=stop['tests'][0]
  if abs(stop['x'])<1e-8:assert f['wind']>1 and abs(f['set'])<=1
  if abs(stop['x']-.9)<1e-8:assert f['wind']<=1 and abs(f['set'])>1
assert abs(r['set']['forward_minute'])>=5 and abs(r['set']['backward_minute'])>=5
assert r['return']['final_winding_degrees']>1
report={'steps':{'assemble':'pass','wind':'pass','hold':'not_tested','run':'pass','backward':'pass','set':'pass','return':'pass'},'summary':
'Judgments use my specialized local quasi-static mesh model and a separate geometry audit, not the undisclosed official simulator. Ten binary STL solids implement a 5:1 crossed-helical winding train, a 36-tooth spring-loaded crown face clutch, an independent 36-tooth radial barrel click, and a crown-selected crossed-helical/21-tooth spur setting train. All submitted solids are single connected watertight positive-volume manifolds. No rest overlaps exceed 0.0002 mm3; bounds, binary sizes, counts, and retention shifts pass (32 radial directions plus the required axial shifts). Gear motion is found by first-clear intersection searches; ratchet drive/release direction uses the manufactured flank geometry and the specified friction cones. Winding gives 71.6928 degrees per crown turn (5.0214:1), with zero minute motion. A direct 45-degree arbor winding followed by local settling loses 4.8796 degrees, predicting 47.8916 hours reserve. HOLD IS NOT FULLY TESTED: the official 40-step tapping procedure is not reproduced, so AT-2 is not_tested despite the positive locking-flank analysis. Independent 20-degree arbor winding is unobstructed, followed by 5.2821 degrees winding from a 30-degree crown turn. Backward 360-degree crown rotation produces zero arbor/minute motion, followed by 5.2707 degrees winding. Both-direction 24-degree tests at all five pull and return positions never drive both trains; endpoints select the correct train. Setting 90 degrees each way moves the minute wheel -34.0223 and +32.1194 degrees without arbor loss. Final returned 90-degree winding gives 16.8834 degrees. The local model checks all cross-body overlaps at each simulated pose, using 3-degree crown turns and axial increments no greater than 0.03 mm. These are local-model results rather than a guarantee of identical force-resolution behavior in the official rig. Detailed measurements and reproducible scripts are in /app/scripts; REPORT.md records development issues and ambiguities. Outside access: none.'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
text='''Submitted ten binary STL parts in `parts/`, their mobile and fixed-body declarations in `keyless.json`, and the step claims in `report.json`. The works use crossed helical gears for winding, a spring-loaded face ratchet for backward crown release, a separate radial holding click, and a second, axially selected train for setting. The collar on the stem withdraws the winding clutch before the setting pinion engages.

Checks used the actual STL solids with Manifold intersection volumes. All ten parts are connected, watertight, positive-volume solids; the largest has 29,374 triangles. The assembly passes the local file, rest-clearance, case-bound and retention audit, including 32 transverse shift directions. Sampled conjugate gear trajectories remain below the permitted overlap. A specialized contact model predicts 71.69 degrees of winding per crown turn, zero winding during backward rotation, unobstructed independent arbor advance, correct train selection at all five pull/return positions, and minute-wheel setting of 34.02 and 32.12 degrees on the two 90-degree strokes. Returned 90-degree winding gives 16.88 arbor degrees. Numerical results and source scripts are retained in `/app/scripts`.

After direct 45-degree arbor winding, the local holding calculation settles after 4.88 degrees of run-back, corresponding to 47.89 hours reserve. I did not reproduce the full 40-step tapped holding test; AT-2 is therefore `not_tested`. The other pass claims are local-model judgments. The model uses geometric first-contact searches and analytical Coulomb-cone screening for the ratchet flanks; it is not the official general contact solver.

Difficulties, in order: a self-locking worm concept would obstruct independent forward arbor motion and was abandoned. Early solids needed a connected stem/pinion joint, corrected gear phases, and clearance between the clutch, its bearing and the barrel wheel. The face ratchet was increased from 12 through 24 to 36 teeth to reduce re-engagement lost motion. The click guide was enlarged for reliable transverse retention. The first numerical gear search incorrectly assumed its far endpoint lay in the next tooth gap; it was replaced with a first-clear scan. Excessive bore and straight-extrusion tessellation slowed the first model run; compact hole caps and fewer helical layers reduced the final meshes, and the operating sequences were rerun.

Ambiguities: the brief does not specify the numerical contact-force solver, tap ordering, or the surface-travel radius for compound mobiles. The local model treats motions as quasi-static and uses the stated friction coefficients. Either interpretation of whether `on_stem` includes the stem's axial translation is accommodated by the stem collar driving the clutch's physical axial position. No stem detent is included: the rig prescribes its two axial positions.

Outside access: none
'''
(out/'REPORT.md').write_text(text)
print('Reports written. All assertions for tested steps passed.')
print('Total submitted triangles:',sum(f['triangles'] for f in a['files']))
print('Local model seconds:',r['elapsed_seconds'])
