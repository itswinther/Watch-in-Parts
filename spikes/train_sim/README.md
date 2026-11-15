# Going-train contact simulation (verification / demo; not a grader change)

`sim.py` runs a quasi-static contact simulation of a delivery's going train (barrel -> ... -> the seconds hand's
mobile, found from movement.json's meshes) with real contact geometry, contact normal forces and Coulomb
friction, and compares it with the one-job grader's strength-check formula (DS-W04, `geometry/watch.py
strength_run`: F = T_driver / (m z_driver / 2)).

## Method

* **Loading**: `geometry.watch.load_movement` (STEP parts as manifolds, the same tessellation as the grader), the
  barrel passed in as an STL (`geometry/data/barrel.stl`, or the thin barrel). Hands are left out of the train
  bodies (they touch nothing in the train and would only shrink the engine's steps).
* **Kinematics**: `spikes/keyless/engine.py`. For each mesh of the going train, the driver mobile is a `driven`
  body turned in steps (default 40 per driver tooth pitch, 2 pitches; the barrel clockwise seen from the dial),
  the driven mobile a `contact` body the engine pushes the least distance that clears the overlap, within the
  friction-cone budget (mu 0.51; a step the engine cannot resolve is a kinematic jam). The two solids are cut to
  the material that can reach each other (`watch._near_cut`, as the mesh test does); the fixed parts (plate,
  bridge, dial) cropped to the mesh zone are obstacles. Engine overlap tolerance lowered to 5e-5 mm^3.
* **Forces** (added on top of the engine, which has none): after each step the driven mobile is turned back
  0.004 mm (at its pitch radius) into the driver; the overlap splits into contact patches. Per patch:
  point = volume centroid; normal = minus the gradient of the overlap volume under a translation of the driven
  mobile (central differences, 1.5 um) = the area-weighted contact normal; load share = patch volume. Coulomb
  friction mu on each patch opposes the sliding velocity of the driven flank relative to the driver (from the
  measured angle increments). Torque balance on the driver (input torque given) sets the force scale; the torque
  balance on the driven mobile gives the transmitted torque. Run at mu 0 (sanity: efficiency must be ~1, virtual
  work), mu 0.15 (a lubricated reference point), mu 0.44 (dry sliding, running) and mu 0.51 (static, start from rest / stall).
* **Load case**: input torque of each mesh = the grader's (barrel 70.1 N mm x speed ratio, friction-free). Under
  Coulomb friction all forces scale linearly with torque, so efficiencies do not depend on it and forces for
  another torque (e.g. the thin spring, x 0.83) are a straight scale. Holding the seconds mobile (stall) gives the
  same static force set as the mu 0.51 column. Overall efficiency = product of the per-mesh means (and of the
  per-mesh minima, a lower bound when worst phases coincide).
* **Layer check**: every train mobile against every non-meshing train mobile and fixed part, at 5 train
  positions: overlap volume and smallest gap (search 0.1 mm). Rubbing between adjacent layers would show as
  overlap here, or as a contact patch with an axial normal (`axial_patch_steps`) in a mesh.

## Run (Docker only)

    docker run --rm --memory 4g --cpus 3 -v <worktree>:/w:ro -v <deliveries>:/d:ro -v <out>:/out -w /w \
      keyless-grade python spikes/train_sim/sim.py /d/<design> <barrel.stl> /out/<name>.json --label <name>

Outputs: `<name>.json` (summary + full per-step records), `<name>_summary.json`, `<name>_viewer.json`
(per mesh segment, per step: mobile angles in degrees CCW from +z relative to the drawn pose, and contacts
`{pair, point xyz, normal, normal_force_n, friction_n, slide_dir}` at mu 0.44).

## Limitations

Quasi-static (no inertia, no impacts, no escapement: the load is whatever the barrel torque can hold); rigid
bodies on exact fixed axes (no pivot play, tilt, axial shake, deflection); load sharing between simultaneous tooth
pairs by overlap volume, a crude compliance proxy (the total mesh force is reliable, the split is not); no pivot
or arbor friction (only tooth friction); one constant Coulomb mu; contact found from tessellated STEP meshes
(facet error ~ microns), probe depth 4 um, step 1/40 of a tooth pitch; meshes are simulated one at a time (each
with the ideal input torque), not as one coupled chain.

Spring torques: `torque_cases.py` turns a result into the DS-101 load cases (row L Table 4: full wind 4.5 N mm,
low end n = 1 0.9 N mm; thin barrel x 0.83: 3.735 / 0.747; 70.1 N mm = Table 2a bridle max, the strength / stall
case). Exact by linearity (see its docstring), not a separate run.

## Results (2026-11-15, 40 steps per driver pitch, 2 pitches per mesh; `results/`)

Designs: `c2` 6.6 mm (supplied barrel), `t1` 3.66 mm and `t5` 3.00 mm (thin barrel, 0.02 mm z gaps). Runtime
94 to 113 s per design (4 meshes x 81 steps, ~10k engine evals per mesh), 3 CPUs.

| mesh (input torque at 70.1) | grader F (N) | peak normal mu 0 / 0.15 / 0.44 / 0.51 (N) | efficiency mean (worst phase) mu 0.15 / 0.44 / 0.51 |
|---|---|---|---|
| barrel 96 / third 24 (70.1 N mm) | 7.30 | 8.14 / 8.67 / 10.1 / 10.6 | 0.983 (0.970) / 0.950 (0.924) / 0.942 (0.913) |
| third 60 / centre 30 (17.5) | 2.34 | 2.60 / 2.77 / 3.23 / 3.37 | 0.984 (0.973) / 0.954 (0.932) / 0.947 (0.921) |
| centre 90 / fourth 12 (8.76) | 0.920 | 1.03 / 1.09 / 1.27 / 1.33 | 0.973 (0.946) / 0.919 (0.859) / 0.906 (0.837) |
| fourth 96 / seconds 12 (1.17) | 0.122 | 0.137 / 0.144 / 0.169 / 0.176 | 0.973 (0.945) / 0.919 (0.861) / 0.906 (0.840) |
| overall (product) | | | 0.917 (0.843) / 0.765 (0.636) / 0.731 (0.590) |

The three designs agree to the third digit (same tooth profiles in x/y; they differ in z only). mu 0 check: mean
efficiency 1.000 to 1.002 on every mesh (the force solve is consistent with the kinematics by virtual work).
No jam: every engine step resolved, and the solved normal force and transmitted torque are positive at every step,
at every mu. No contact with the plate, bridge or dial in any mesh zone, no axial (face) contact patch.
Layer check: no overlap; t5's smallest gaps are exactly 0.02 mm (each train mobile to plate and bridge, barrel
to centre), c2 and t1 0.05 mm.

Versus the grader (DS-W04): frictionless, the peak normal force is 8.14 N = 7.30 / cos 25 deg (the formula's
tangential force at the pitch circle, resolved along the 25 deg line of action): the formula is right for a
frictionless mesh. With dry friction the peak tooth force is 10.1 N (mu 0.44) to 10.6 N (0.51), 1.39 to 1.45 x
the formula's F, at the pitch point on the approach side (N = T / (r_p (cos a - mu sin a))); oiled (0.15) 1.19 x.
The strength margins the grader prints are therefore optimistic by up to that factor on the friction side.
Spring cases (row L): at the low end 0.9 N mm (thin 0.747) the seconds mobile still receives 1.20e-3
(thin 0.99e-3) N mm in the worst phase at mu 0.44, 64 % of the frictionless 1.875e-3; in this model the train
advances against any seconds load below that. There is no threshold torque here (Coulomb tooth friction is
proportional to load); pivot friction, which is not modelled, is what would stop a train at the low end.
