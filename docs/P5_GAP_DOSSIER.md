# Part 5 (crown winding): is the spread a real gap?

Analysis session, 15 Nov 2026, from about 03:30 Helsinki. No grader, engine, reference or brief was changed. No
model was run. Regrades and probes were run with main's `spikes/keyless/` code (engine files identical to
`c44b69b`; main at `87c526c`), on Python 3.13 with manifold3d 3.5.5 in this cloud session, not in A's Docker image
(Python 3.12). Scripts and logs are in the session's scratchpad. Every claim below gives the command or file it
rests on.

## Answer in five lines

1. **Not yet.** The evidence does not support "frontier models consistently score below the reference on Part 5".
2. **No model has ever run the job's Part 5.** All five Part 5 deliveries are from A's standalone keyless task
   (v1: `/app/BRIEF.md`, stem on x, case radius 8.7, 60 or 90 min). The job's Part 5 is another frame and scale
   with its own reference, which is not at 1.0 (B 02:41: P5 0.72).
3. **GPT can solve it** (imWnpTP: every step passes on the fixed engine). Sonnet's one run also passed every step
   (old engine). Fable and Opus have no Part 5 runs at all.
4. **Two of the three GPT shortfalls given as "real design faults" in the README are not clean.** b7qdG8X's AT-5/AT-6
   block comes from the rig's 0.03 mm pull step (the same parts pull through cleanly in 0.01 mm steps). QZeuFhk's
   "clutch that won't slip backward" does not happen on main's engine: neither from rest nor in the rig's 45°
   pre-wind where AT-2 starts (0 of 90 steps blocked). Its full grade on main is still pending.
5. **The deliveries were made under an older brief.** Main's engine grades them against rules the agents never
   saw (COUPLED_TURN 30 → 90, SET_MIN 5 → 2, AT-3 now needs AT-2's limits, a longer hold, new fit and spring rules).
   A gap claim needs fresh runs on the current brief.

> **Work in progress (03:55).** This file is on the analysis branch only, not on main. The per-delivery step tables,
> the per-model figures and the risk list follow when the regrades now running here finish (imWnpTP, b7qdG8X,
> the standalone reference on main's engine; the QZeuFhk pre-wind probe). Until then, treat only the confirmed
> findings below as established.

## Confirmed so far (each was run here)

- **b7qdG8X pull.** After the rig's rest phase the clutch sits at q = -0.00273; the stem's collar (radius 0.35,
  x 4.245 to 4.260, 0.015 thick) is 0.0023 from the clutch's face (x 4.2623). One 0.03 pull step puts the whole
  collar inside the clutch (overlap 0.00422 mm³). The engine's `push` then sees the same overlap at ±0.002, gets
  both signs from `force_signs`, and stops after six flat samples (0.012 < the 0.0248 needed): blocked. A scan of
  the clutch's own slide with the stem pulled 0.03 clears every body from +0.0248 to +0.13. Pulled to 0.9 in
  0.01 or 0.005 steps (no rocking), nothing blocks and the clutch follows to q = 0.8947. Probes:
  `pull_probe.py`, `pull_trace.py`, `pull_fine.py`.
- **QZeuFhk backward from rest.** 40 backward crown steps of 3°: 0 blocked, the clutch rides to q = +0.0056, the
  arbor does not move (`back_probe.py`).
- **QZeuFhk pre-wind (AT-2's start).** The arbor driven by the rig in the winding sense, 90 steps of 0.5°, crown
  held: 0 blocked, arbor at 45.00°, winding rotor back-driven -223.75°, clutch slipping to q = 0.0116, click at
  0.0871 (`prewind_probe.py`). On fde5cf9 the same pre-wind blocked from 1.5° (A, 00:05).
- **Briefs.** The prelim runs saw `BRIEF.md` md5 cd2e7d… (55/60 min); the three repeats md5 27e4da… (85/90 min).
  Their differences from main's `spikes/keyless/docs/PROMPT.md` are listed in point 5 above.
- **Time.** Agent minutes: imWnpTP 38.0, b7qdG8X 31.9, QZeuFhk 31.1, GPT prelim 28.9 (of 90, 90, 90, 60),
  Sonnet prelim 19.1 (of 60). No run was stopped by a limit.
