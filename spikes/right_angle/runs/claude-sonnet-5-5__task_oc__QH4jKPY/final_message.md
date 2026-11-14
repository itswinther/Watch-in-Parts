I submitted a working winding train: the stem drives the ratchet wheel through an 8-tooth pinion and an 80-tooth crown wheel, a ratio of 10 stem turns per arbor turn. I checked it with my own overlap tests built from the brief's rules, not the real grader. It passes every check I could build.

**Parts, in `/app/submission`**
- `stem.stl`:
  - an 8-tooth involute pinion, module 0.2, 1.2 mm wide, at x = +8.0 on the stem axis (y = 0, z = -3.9);
  - a 0.5 mm radius rod from x = -15.5 to 10.6;
  - two collars radius 0.9 and a grip head radius 1.0 at the outer end.
- `ratchet.stl` (the arbor part): a crown (face) gear with 80 downward-pointing teeth, a web at z -2.5 to -1.9, and a 0.61 mm square hole that sits on the arbor square. Its teeth are cut by sweeping the pinion through the mesh motion, so they match the pinion exactly. It has about 254k triangles.
- `post_a.stl` and `post_b.stl` (fixed): two blocks hanging from the main plate with a 0.01 mm gap. A has a through bore between the stem collars, and B has a blind bore for the stem tip.
- `winding.json`: mobile `stem` (+x axis), mobile `arbor` (`ratchet`), and one mesh with `driver_teeth` 8, `driven_teeth` 80 and `sense` "opposite". The pinion is on the +x side so that a positive stem turn about +x turns the arbor negatively about +z.

**How I checked it, against the brief**

| Requirement | Result |
|---|---|
| Files | Every part is watertight, a single shell, with positive volume. |
| Clear of the movement at rest | Overlap with the frozen parts is 0 for every part. |
| Drive | I tested 180 phases plus random ones. The largest stem-to-ratchet overlap is 3e-5 mm³ (limit 0.002). The smallest overlap with the ratchet turned back 3% of a pitch is 0.003 mm³ (needs at least 0.0002). With the wrong sense the overlap is 0.03 mm³, so the test does detect it. |
| Direction and ratio | 10 stem turns per arbor turn, within 8 to 12; direction follows from the declared "opposite". |
| Clear | Each mobile turned alone through 36 samples overlaps the fixed parts and the movement by 0. The two posts don't touch each other. |
| Held | The stem shifted 0.3 mm in all six directions overlaps the posts by at least 0.37 mm³. |
| Seated | The ratchet fills 88% of the shell around the square and overlaps the square by essentially 0. |
| Anchored | Each post shifted 0.05 mm up overlaps the plate by about 0.1 mm³. |
| Bounds | The stem reaches 22.7 mm from the case centre (needs at least 21.2). Every part is inside the case height of -5.0 to 11.4. |

**Difficulties, in order**
1. The first pinion (module 0.22) had its tip at z = -5.0, exactly on the case floor. I changed to module 0.2, which puts the tip at -4.9.
2. The stem came out as two shells because the rod started at x = -13.05, short of the head at -16. I extended the rod to -15.5.
3. The ratchet first saved with duplicate float32 vertices and degenerate triangles, so trimesh called it non-watertight. Reloading and calling `simplify(5e-4)` before saving fixed that.
4. At 24 sweep steps the ratchet had 582k triangles, over the 400k limit. I settled on 16 steps, which gives 254k triangles after simplifying.
5. I tried ray casting with trimesh to look at the plate underside, but `rtree` isn't installed. I used manifold overlap tests instead.

**Ambiguities in the brief**
- I treated "touches" in the Anchored check as the 0.05 mm shifted part overlapping the frozen part. If it means a gap or contact within some tolerance, the 0.01 mm gap should still pass.
- The brief doesn't say how the "arbor" mobile's point and direction are defined, so I left them out as in its example.
- The sample counts in the brief imply a long drive test (480 samples), which I only spot-checked by symmetry.

Outside access: none