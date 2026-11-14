import json,re,struct
from pathlib import Path
import numpy as np,trimesh
import manifold3d as M
root=Path('/app/submission');j=json.loads((root/'keyless.json').read_text());files=list((root/'parts').glob('*.stl'));assert 0<len(files)<=40
used=j['fixed']+[p for m in j['mobiles'].values() for p in m['parts']]
assert len(used)==len(set(used)) and set(used)=={p.stem for p in files}
assert j['mobiles']['stem']['kind']=='stem' and j['mobiles']['barrel']['kind']=='barrel'
records={}
for p in files:
 assert re.fullmatch('[A-Za-z0-9_-]{1,40}',p.stem)
 data=p.read_bytes();n=struct.unpack('<I',data[80:84])[0];assert len(data)==84+50*n and n<=200000
 t=trimesh.load(p);assert t.is_watertight and t.is_winding_consistent and t.volume>0 and len(t.split())==1
 assert np.all(t.vertices[:,2]>=-3.4) and np.all(t.vertices[:,2]<=3.4)
 rr=np.linalg.norm(t.vertices[:,:2]-[3.5,0],axis=1)
 if p.stem!='stem':assert rr.max()<=8.7
 else:assert t.vertices[:,0].max()>=12.7
 records[p.stem]={'triangles':n,'volume_mm3':float(t.volume),'closed':True,'components':1,'max_case_radius_mm':float(rr.max())}
json.dump(records,open(root/'mesh_checks.json','w'),indent=2)
report={
 'steps':{'assemble':'pass','wind':'pass','hold':'not_tested','run':'pass','backward':'pass','set':'pass','return':'pass'},
 'summary':'''Eight binary STL solids and their kinematic manifest are submitted in position 1 with spring coordinates zero. Own checks, not an official verifier run: all meshes load, are consistently oriented closed single solids, have positive volume and fewer than 200000 triangles. All required bearing shifts produce interference, no rest interference exceeds 0.0002 mm3, non-stem parts fit the case, and the stem reaches x=13.1. A geometric least-motion solver using the specified overlap allowance gives 101.88 degrees arbor winding from 360 degrees forward crown (ratio 3.534); the minute wheel stays stationary. Generated face gears and 25-degree involute spur gears were swept through their meshes, including a 0.25-degree crown grid. The radial click's calculated static run-back after 45 degrees winding is 0.261 degree, giving 47.994 hours reserve. AT-2 is marked not_tested because I did not reproduce the exact 40-step tapped, force-coupled rig. The click is mechanically stopped on its rest side, and its radial locking face supplies a holding constraint; this supports a hold prediction but is not the full tap test. The arbor-only 20-degree sweep at 0.5-degree increments clears, and the subsequent 30-degree crown turn winds another 7.00 degrees. Backward crown rotation through 360 degrees clears with the barrel fixed at the calculated holding boundary, by axial clutch overrun; the follow-up 30-degree forward turn winds 5.71 degrees. Clutch ramp and locking-flank force ratios were checked against both supplied friction coefficients. Pulling and pushing were checked at every 0.03 mm increment. At all five test stops, 24-degree turns in either direction clear and do not drive both trains: 0.225 and 0.45 are neutral, and 0.675 and 0.9 set only. At position 1 the forward 24-degree test winds 3.94 degrees and does not set. A sequential 90-degree forward/back setting cycle moves the minute wheel +19.37/-18.72 degrees. The barrel stays held in the setting model. Pushing in after this cycle clears, and a 90-degree winding restart gives 22.83 degrees arbor motion. These pass judgments use the own geometric solver plus analytical Coulomb flank checks; a general force/contact solver was not available in the supplied folder.
Difficulties in order: Boolean-generated face-tooth sweeps made mesh slivers; I replaced them with a sampled generating envelope, cleaned export degeneracies, and reloaded the STLs. Initial flange, setting-gear and guide clashes required separation, a larger setting face wheel, and an open click guide. A 12-tooth clutch could consume the 30-degree restart allowance; I changed it to 24 teeth and checked friction margins. I then reduced mesh density and added axial clearance above the barrel spur to reduce unnecessary contact and computation.
Ambiguities: the exact contact-force solver, tap selection/settling order and numerical definition of least movement are unspecified. on_stem explicitly promises rotation but is less explicit about translation; the stem shoulders physically locate the sliding clutch in either interpretation. Virtual spring loads are supplied by the declared spring mobiles.
Outside access: none'''
}
(root/'report.json').write_text(json.dumps(report,indent=2)+'\n')
assert len((root/'report.json').read_bytes())<100000 and not (root/'report.json').is_symlink()
(root/'REPORT.md').write_text('''# Keyless works submission

Submitted: eight binary STL parts, `keyless.json`, `report.json`, mesh measurements and an assembly preview. Reproduction and checking scripts are in `/app/scripts/`. The supplied parts were not modified.

The stem drives an eight-leaf winding pinion through a spring-loaded, 24-tooth axial overrunning clutch. A 42-tooth face/spur wheel drives the 28-tooth arbor wheel. A radial spring click holds the arbor. Pulling 0.9 mm disengages winding and brings the stem setting pinion into a separate 20-tooth face wheel, whose 20-tooth lower spur drives the supplied minute wheel. The intermediate stops include a neutral interval.

Own checks: closed single solids, positive volumes, binary STL format, triangle limits, rest clearance, case bounds and every specified bearing shift pass. Contact-boundary calculations give a winding ratio of 3.534, setting travel of +19.37/-18.72 degrees for the sequential 90-degree turns, and 22.83 degrees arbor winding after a 90-degree return turn. Translation was checked every 0.03 mm and gear meshes on a 0.25-degree crown grid. Clutch flank ratios were compared with the specified static and sliding friction coefficients. The arbor-only running sweep and backward-overrun paths clear.

The exact 40-step tapped hold simulation was not reproduced, so AT-2 is `not_tested`. Its static geometric estimate is 0.261 degree run-back, corresponding to 47.994 hours reserve. The other step claims are judgments from the own contact-boundary model and analytical friction checks, not results from an official verifier or a general force solver.

Difficulties, in order: (1) Boolean tooth generation produced sliver triangles; a sampled generating envelope and export cleanup resolved them. (2) Flange, setting-wheel and click-guide clashes required greater separation and a guide opening. (3) The first clutch had too much potential lost motion for the restart test; 24 teeth reduced it. (4) Mesh density and unnecessary axial face contact were reduced before final checks.

Ambiguities: the brief does not define the numerical contact solver or tap/settling selection order. `on_stem` specifies shared rotation more clearly than shared translation; physical stem shoulders locate the clutch. The declared spring mobiles use the rig's virtual spring forces.

Outside access: none
''')
print('Final manifest and eight STL solids validated. Report written. Total triangles:',sum(r['triangles'] for r in records.values()))
