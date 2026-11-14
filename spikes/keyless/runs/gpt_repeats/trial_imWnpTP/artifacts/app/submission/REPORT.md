# Keyless works submission

Submitted: eight binary STL parts, `keyless.json`, `report.json`, mesh measurements and an assembly preview. Reproduction and checking scripts are in `/app/scripts/`. The supplied parts were not modified.

The stem drives an eight-leaf winding pinion through a spring-loaded, 24-tooth axial overrunning clutch. A 42-tooth face/spur wheel drives the 28-tooth arbor wheel. A radial spring click holds the arbor. Pulling 0.9 mm disengages winding and brings the stem setting pinion into a separate 20-tooth face wheel, whose 20-tooth lower spur drives the supplied minute wheel. The intermediate stops include a neutral interval.

Own checks: closed single solids, positive volumes, binary STL format, triangle limits, rest clearance, case bounds and every specified bearing shift pass. Contact-boundary calculations give a winding ratio of 3.534, setting travel of +19.37/-18.72 degrees for the sequential 90-degree turns, and 22.83 degrees arbor winding after a 90-degree return turn. Translation was checked every 0.03 mm and gear meshes on a 0.25-degree crown grid. Clutch flank ratios were compared with the specified static and sliding friction coefficients. The arbor-only running sweep and backward-overrun paths clear.

The exact 40-step tapped hold simulation was not reproduced, so AT-2 is `not_tested`. Its static geometric estimate is 0.261 degree run-back, corresponding to 47.994 hours reserve. The other step claims are judgments from the own contact-boundary model and analytical friction checks, not results from an official verifier or a general force solver.

Difficulties, in order: (1) Boolean tooth generation produced sliver triangles; a sampled generating envelope and export cleanup resolved them. (2) Flange, setting-wheel and click-guide clashes required greater separation and a guide opening. (3) The first clutch had too much potential lost motion for the restart test; 24 teeth reduced it. (4) Mesh density and unnecessary axial face contact were reduced before final checks.

Ambiguities: the brief does not define the numerical contact solver or tap/settling selection order. `on_stem` specifies shared rotation more clearly than shared translation; physical stem shoulders locate the clutch. The declared spring mobiles use the rig's virtual spring forces.

Outside access: none
