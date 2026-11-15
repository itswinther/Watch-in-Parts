# Part 5 (crown winding): is the spread a real gap?

Analysis session, 15 Nov 2026, 03:30 to 05:00 Helsinki. Nothing in the grader, engine, reference or briefs was
changed, and no model was run. Regrades and probes used main's `spikes/keyless/` code (engine files identical to
`c44b69b`). They ran in this cloud session on Python 3.13 with manifold3d 3.5.5, not in A's Docker image, and stopped
at 04:50 at itswinther's request. Each claim below names its source. "Mine" means run here; "A hh:mm" means
SESSION.md on main.

## Answer

1. **No.** The evidence does not support "frontier models consistently score below the reference on Part 5". On
   main's engine, GPT passes every step in two of four deliveries, and Sonnet in its only run. Fable and Opus have
   never run Part 5.
2. **The spread is not on the task we would submit.** All five deliveries come from A's standalone keyless task
   (v1: `/app/BRIEF.md`, stem on x, case radius 8.7, 60 or 90 min, no datasheets). No model has run Part 5 inside the
   five-part job. The agents never saw QA-W100 or DS-501. The job's own Part 5 reference scores 0.72 on main,
   because AT-5/AT-6 do not finish inside the 5400 s limit (A 04:32).
3. **The two GPT shortfalls the README calls "real design faults" are not clean.**
   - QZeuFhk now passes every step (A 04:06).
   - b7qdG8X loses AT-5 and AT-6 to the rig's 0.03 mm pull step, not to its geometry. The same parts pull through
     cleanly in 0.01 mm steps.
4. **Only one shortfall still looks like a real design fault:** the GPT prelim's mirror image (AT-1). It was made
   against the oldest brief, and I did not re-trace it on main's engine.
5. **A judge could zero what remains, for four reasons:**
   - the regrades use rules the agents never saw;
   - grading time is close to or over the verifier limit;
   - neither reference has a recorded 1.0 on the current engine (the job's one hits the 5400 s limit, A 04:32);
   - three engine artifacts have already been found in this one task.

## 1. The deliveries

| Delivery | Model, harness | Brief it saw | Agent time / limit | Harbor cost estimate | First engine (trial) | Main's engine (c44b69b) |
| --- | --- | --- | --- | --- | --- | --- |
| prelim_gpt | GPT-6.1-sol, Codex | `BRIEF.md` md5 cd2e7d… | 28.9 / 60 min | $1.07 | 0.024 | **0.095**: AT-0, AT-2 pass; AT-1 fails, AT-3 to AT-6 fail (A 04:06) |
| prelim_sonnet | Sonnet 5.5, OpenCode | cd2e7d… | 19.1 / 60 min | $1.55 | 0.950 | **0.950**: all 7 pass, honesty 0.571 (A 04:06) |
| b7qdG8X | GPT-6.1-sol, Codex | md5 27e4da… | 31.9 / 90 min | $1.07 | 0.024 | **0.2849**: AT-0 to AT-3 pass; AT-4 to AT-6 fail (A 02:15; mine, 3431 s) |
| imWnpTP | GPT-6.1-sol, Codex | 27e4da… | 38.0 / 90 min | $1.06 | 0.022 | **0.9916**: all 7 pass, honesty 0.929 (A 01:50; mine, 3651 s) |
| QZeuFhk | GPT-6.1-sol, Codex | 27e4da… | 31.1 / 90 min | $0.75 | 0.066 | **0.992**: all 7 pass, honesty 0.93 (A 04:06) |

- **Sources.** Agent time and cost are from each trial's `result.json`; the cost is Harbor's token-price estimate.
  The trial folders are in `spikes/keyless/runs/`.
- **Reproduction.** My two regrades match A's to four decimals, so the Python 3.13 environment here reproduces A's
  Docker.
- **Time.** No agent was stopped by its limit: all used between 19 and 38 minutes.

**Rule changes since the runs.** The repeats' brief differs from main's `spikes/keyless/docs/PROMPT.md` (the brief
main's engine grades against) in these rules:
- COUPLED_TURN 30° → 90° (AT-3, AT-4 and AT-5 position 1);
- SET_MIN 5° → 2°;
- AT-3 now also requires AT-2's hold limits;
- AT-2's hold now runs past 40 steps, up to 240, while the arbor is still running back;
- AT-5's end-position rule;
- new: the fit rule (0.005 mm radial play at bores), returning springs that push free parts, `carrier` mobiles,
  the bounded rest phase, the "What the rig does not model" paragraph, and an optional declared `pull`.

The two prelims saw an older brief again: a 55-minute budget, and "anticlockwise as seen from +z (positive about +z)",
which was later reworded. **Main's engine therefore grades these deliveries against rules their authors never read.**

## 2. Step by step

### imWnpTP (GPT): every step passes

- **Design:** an 8-leaf winding pinion driven through a spring-loaded 24-tooth axial clutch on the stem, a 42-tooth
  face wheel driving a 28-tooth arbor wheel, a radial spring click, and a 20-tooth setting face wheel.
- **Mine, on main:**

  | Step | Result |
  | --- | --- |
  | AT-1 wind | 3.532 crown turns per arbor turn, never blocked |
  | AT-2 hold | run-back 0.23°, drift 0 |
  | AT-3 run | reserve 47.995 h; then winds 22.86° |
  | AT-4 backward | arbor 0°, minute 0°; then winds 22.87° |
  | AT-5/AT-6 set and return | pull never blocked; minute +5.2° / −4.3° per 24° test turn at position 2 |

- **Honesty 0.929 = 6.5 / 7.** It marked AT-2 `not_tested` (0.5 points) and every other step correctly. "Its report
  misstated one result" (A 01:50, README) is wrong: nothing was misstated.
- **On earlier engines** it scored 0.022 and then 0.421. Both were engine faults (A 00:40, 01:50).

### QZeuFhk (GPT): every step passes (A 04:06)

- **Design:** a 5:1 crossed-helical winding pair, a 36-tooth spring face clutch on the stem with a 0.1 mm collar,
  a radial click, and a crossed-helical setting train.
- **The "clutch that won't slip backward" is gone on main's engine.** Mine:
  - 40 backward crown steps from rest: 0 blocked; the clutch rides to q = +0.0056; the arbor does not move
    (`back_probe.py`).
  - The rig's AT-2 pre-wind (arbor driven 90 × 0.5°, crown held): 0 of 90 blocked; the arbor reaches 45.00°, the
    rotor is back-driven −223.75°, and the clutch slips to q = 0.0116 (`prewind_probe.py`).
  - On fde5cf9 the same pre-wind blocked from 1.5° (A 00:05).
- **That "fault" was an engine fault,** like the AT-1 jams before it. The README still lists it as a design fault.

### Sonnet prelim: every step passes (A 04:06)

- **Design:** a loose winding pinion, a spring sawtooth clutch on the stem, a 20-pin contrate crown wheel, a 30-tooth
  gear and a 20-tooth ratchet on the arbor, a spring click, and a contrate setting wheel.
- **First engine:** product 1.0 (5.07 crown turns per arbor turn, run-back 10.4°, reserve 47.8 h).
- **Honesty 0.571:** it claimed AT-0 and marked the other six `not_tested`.
- **Not re-traced here.**

### b7qdG8X (GPT): AT-4, AT-5 and AT-6 fail

- **Design:** a bevel winding pair, a 32-tooth sawtooth clutch on the stem (teeth 0.060 high), a 6:36 spur to the
  arbor, and a radially sliding click.
- **AT-0 to AT-3 pass.** Mine, on main:

  | Step | Result |
  | --- | --- |
  | AT-1 wind | 6.023 crown turns per arbor turn |
  | AT-2 hold | run-back 3.17°, drift 0.23° over 46 steps |
  | AT-3 run | reserve 47.93 h; the 90° coupled turn winds 14.99° |

- **AT-5 and AT-6: the pull blocks on its first step.** This is the rig's step size, not a design fault.
  - **Geometry.** After the rest phase the clutch sits at q = −0.00273. The stem's collar (radius 0.35, x 4.245 to
    4.260, 0.015 thick) is 0.0023 from the clutch's face (x 4.2623).
  - **What the rig does.** One 0.03 pull step puts the whole collar inside the clutch (0.00422 mm³). The overlap is
    then the same at ±0.002 of clutch slide, so `force_signs` returns both signs, and `push` gives up after six flat
    samples (0.012 searched, 0.0248 needed). The step is blocked, and rocking the crown cannot help.
  - **The clutch is free to move.** With the stem pulled 0.03, a scan of the clutch's own slide clears every body
    from +0.0248 to +0.13 (`pull_probe.py`, `pull_trace.py`).
  - **Finer steps pull through.** Pulled to 0.9 in 0.01 or 0.005 steps, nothing blocks and the clutch follows to
    q = 0.8947. The rig's 0.03 blocks at step 0 (`pull_fine.py`; from rest, not from AT-2's end state).
  - **The brief permits this collar.** It says "Not checked: minimum feature size". It says a pushed part "moves the
    least distance … that the contact forces allow; if friction prevents it from giving way, it does not", and here
    friction does not prevent it.
  - **Verdict:** the clutch geometry allows the pull, and the rig refuses it because of its step size and search.
    That is an engine artifact, triggered by an unrealistic 15 µm collar.
- **AT-4 backward: cause unclear.**
  - The 360° backward turn passes: never blocked, arbor 0.0°, minute 0.0°.
  - The forward 90° that follows is blocked on 30 of 30 steps; the arbor gains only 0.21°.
  - From AT-2's end state the same forward turn winds 14.99°, never blocked (AT-3 and AT-5 position 1). So the jam
    depends on where the backward ratcheting leaves the clutch.
  - The probe that would say why was stopped before it printed. On fde5cf9, A saw "the forward crown presses the
    clutch axially instead of turning the pinion" at rest (`gpt_repeats/README.md`).
  - Not classified.
- **A's 01:50 wording "a stem that hits its own clutch on pull" (a design fault) should read:** pull blocked by the
  rig's 0.03 mm step against a 0.015 mm collar; the same parts pull through in finer steps.

### GPT prelim: AT-1 fails (the mirror image)

- **Main's engine:** AT-0 and AT-2 pass, AT-1 fails, and AT-3 to AT-6 fail with it (A 04:06).
- **First-engine trace** (`prelim_gpt/README.md`): forward slips; backward drives the arbor −8.24°, against the winding
  sense. Both the clutch's drive direction and the barrel's sense are reversed, which is a consistent reflection.
- **Verdict:** a genuine design fault on the evidence so far. The brief states both directions with explicit signs
  under the right-hand rule ("negative rotation about +x"; "positive about +z").
- **Not verified here.** My direction probe on main's engine was stopped before it printed. A notes the AT-1 failure
  on main has not been traced (04:06).

## 3. What the reference does differently

The standalone reference (`spikes/keyless/reference.py`) is the usual keyless layout:
- a winding pinion with Breguet face teeth;
- a sliding pinion with Breguet teeth facing it (8 teeth, 0.15 high, drive face 0.03 of the pitch, so close to
  vertical), on a square;
- a crown wheel driving the barrel wheel and its ratchet;
- a pivoted spring click;
- a setting wheel that the sliding pinion's spur teeth meet when pulled.

At the steps where models fall short:

- **AT-5/AT-6 pull:** a collar 0.2 mm thick in a counterbore, with a 0.15 mm gap (`collar_gap`), drags the sliding
  pinion. Thicker than a pull step, so it can never sit wholly inside the pinion after one step.
- **AT-4 then forward:** near-vertical Breguet drive faces on 8 large teeth. b7qdG8X uses 32 small sawtooth teeth.
  Whether that difference explains its AT-4 jam is not established.
- **AT-1 sense:** the drive faces and the crown-wheel / barrel-wheel sense follow the brief's signs; the prelim
  reversed both.

**The reference has no recorded 1.0 on main's engine.** Its last full grades (Harbor oracle 14 Nov 17:40 to 18:00;
anchors 3 × 1.0 in `docs/anchors_independent.log`, 22:36; "1.0 three times on f005958", A 00:50) all predate the
engine changes af355d9, 397b5ad and c44b69b. My regrade on main was stopped unfinished.

## 4. Could a careful engineer have avoided each fault from the brief alone?

- **Mirror image (prelim AT-1): yes.** Both senses are signed in the brief.
- **b7qdG8X pull (AT-5/AT-6): not fairly.**
  - A careful engineer would make a collar thicker than 15 µm, and the brief does give the 0.03 pull step.
  - But nothing in the brief says a contact embedded in one step blocks, and its stated push rule says it should
    give way.
  - The failure depends on how the unshipped engine's search behaves, which a judge would call withheld information.
- **b7qdG8X AT-4: unknown.**
- **The repeats' self-checks.** All three wrote their own contact solvers because the brief does not ship the rig.
  All three flagged the same unclear point: whether an `on_stem` part moves with the stem's pull. They handled it
  with collars, correctly.
  - The job's QA-W100 Part 5 now answers it: "its slide along the stem's line is its own".
  - The job's printability check (0.2 mm, QA-W100 check 13, applied to keyless parts too) is thicker than the job's
    0.04851 mm pull step. So the b7qdG8X kind of block should not arise there. That is inferred from the text, not
    tested.

## 5. Per model (main's engine)

| Model | Runs | Pass every step | Mean reward | Rewards |
| --- | --- | --- | --- | --- |
| GPT-6.1-sol (Codex) | 4 (1 prelim brief, 3 repeat brief) | 2 of 4 | 0.591 | 0.992, 0.9916, 0.2849, 0.095 |
| GPT-6.1-sol, repeat brief only | 3 | 2 of 3 | 0.756 | 0.992, 0.9916, 0.2849 |
| Sonnet 5.5 (OpenCode) | 1 | 1 of 1 | 0.950 | 0.950 |
| Fable 5.2 | 0 | n/a | n/a | n/a |
| Opus 5.5 | 0 | n/a | n/a | n/a |
| Standalone reference | n/a | 1.0 on the first engine only | n/a | not recorded on c44b69b |

- **Small samples.** Two of four is a Wilson 95% interval of about 0.15 to 0.85.
- **The mean is held down by two deliveries:**
  - b7qdG8X (see its breakdown below);
  - the prelim's mirror image, under the oldest brief.
- **b7qdG8X's 0.70 product shortfall** (product = 0.5 × step weights + 0.5 × whole build):
  - AT-5/AT-6: 0.14 (step weight 0.28 × 0.5), lost to the pull artifact;
  - AT-4: 0.06 (0.12 × 0.5), cause unclear;
  - the whole-build term: 0.5, which needs every step.
- **Without the artifact.** If AT-5/AT-6 were judged on geometry, b7qdG8X would still miss AT-4 and the whole-build
  term. So the artifact alone does not explain its score.

## 6. What would settle it

1. **Choose the task the claim is about.**
   - **Part 5 in the five-part job.** Its reference must grade 1.0 first, within the limit.
     - On main (c44b69b) the 797d432 delivery scores **0.72**: AT-0 to AT-4 pass (AT-1 3873 s, AT-4 1886 s), and
       AT-5/AT-6 were still running when the 5400 s Part 5 limit stopped them. That was a timeout, not a block
       (A 04:32).
     - The same geometry (af355d9, mesh placeholders) passed every step with the limit off, in 9658 s, AT-5 alone
       8262 s.
     - An unlimited run on main is due about 06:30.
   - **The standalone task on its current brief.** Its reference needs one recorded 1.0 on c44b69b.
2. **Fix or state the pull-step behaviour before any run** (proposal below), so that no new shortfall carries the
   same doubt.
3. **Runs: clean, k = 5 each for Fable 5.2, Opus 5.5 and GPT-6.1-sol, plus oracle × 1 and nop × 1.**
   - Use the organisers' harness where it applies: OpenCode for Claude, Codex for GPT.
   - Sonnet 5.5 only if a mechanism needs explaining.
   - **What "consistently below" would need:** for each frontier model, at least 4 of 5 runs below the reference,
     and every shortfall traced to a design decision in the delivery.
   - GPT already passed every step in two of three repeats, so on today's evidence I expect the claim to fail for
     GPT.
4. **Budget (estimates, not measured):**
   - **Agents.** On v1, Harbor's estimates were $0.75 to $1.07 per GPT run and $1.55 for Sonnet (1.5 to 4.0 M input
     and 15 to 65 K output tokens).
     - At list prices Opus 5.5 costs 2 × Sonnet 5.5 ($4 / $20 per MTok) and Fable 5.2 costs 4 × ($8 / $40). That
       makes about $3 to $6 per Opus run and $6 to $12 per Fable run on the standalone task; the job with Part 5
       on would cost more.
     - k = 5 costs about $30 to $60 (Fable), $15 to $30 (Opus) and $4 to $5 of Codex credits (GPT).
     - Mikael's rules apply: Fable only through a Claude Code subscription, and A's API key had about $17 left
       at 02:14.
   - **Verifier.** 985 to 2250 s per delivery on A's Mac (fde5cf9), and 3431 to 3651 s here, loaded. Fifteen trials
     are about 5 to 15 CPU-hours: roughly 5 to 8 h of wall time at two trials at a time on A's box.

## 7. What a judge could use to zero the gap

1. **Wrong task.** The Part 5 runs are of the standalone v1 task, not the job's Part 5.
2. **Unseen rules.** Every main-engine score grades a delivery against rules its author never read (section 1).
3. **Engine artifacts in this one task.**
   - Already fixed: the first engine's AT-1 jams, the per-patch budget floor in the pre-wind, and QZeuFhk's "clutch".
   - New, not fixed: b7qdG8X's pull at the 0.03 mm step.
   - Engine fixes alone took two GPT designs from about 0.02 to 0.99. A judge will ask what else remains.
4. **Grader time.**
   - The standalone verifier limit is 3600 s. imWnpTP took 2250 s on A's Mac (fde5cf9) and 3651 s here (loaded:
     3 grades and probes on 4 CPUs, load 8 to 18).
   - Most of it is AT-1: 2548 s and 3036 s here, with 120 K to 189 K overlap evaluations.
   - In the job, Part 5 has 5400 s, and the job's own reference does not finish inside it: 0.72 on main, AT-5/AT-6
     unfinished at 5400 s (A 04:32). Without the limit it needed 9658 s.
   - A timeout scores 0. That would be a time-limit failure on our side, and a judge rerunning on a slower or busier
     box could zero a working design.
5. **The references.** Neither has a recorded 1.0 on the current engine: the standalone one was never regraded
   on it (section 3), and the job's one times out (item 4).
6. **Unshipped rig.** The rig's search and discretization (six flat samples, the patch floor, a pusher embedded in
   one step) are not in the brief. Any failure that turns on them is withheld information.
7. **Mixed harnesses.** Codex for GPT and OpenCode for Sonnet.
8. **Stale documents a judge will read:**
   - `README.md` line 75 and `solution/SOLUTION_WATCH.md` line 286 say b7qdG8X and QZeuFhk have real design faults.
   - `spikes/keyless/runs/INDEX.md` and `gpt_repeats/README.md` show only first-engine and fde5cf9 numbers.
   - README calls imWnpTP's report a misstatement.

## 8. Proposals (need a human yes; nothing changed)

- **Engine (A).** When a pushed body's overlap is flat in both directions, as with a pusher wholly inside it, `push`
  could keep scanning to its budget instead of stopping after six flat samples. Alternatively, `step` could split a
  pull step when that happens.
  - Test with b7qdG8X's pull at 0.03, and rerun the anchors.
  - This changes the engine, so it needs a "yes" under Proposed spec changes.
- **Brief (A, B), if the engine stays.** State that a face which pushes another part along the stem must be thicker
  than one pull step. For the job this follows from the 0.2 mm printability rule; for the standalone brief it does
  not, because minimum feature size is unchecked there.
- **Docs (B, E).** Correct the lines in section 7, item 8. Suggested wording: "On the fixed engine GPT passes every
  step in two of four crown-winding designs and Sonnet in one of one; of the two that fall short, one is a mirror
  image (design fault) and one loses AT-5/AT-6 to the rig's pull step."

## Commands and files (scratchpad, not committed)

- Regrades: `python -I grade.py SUB data --reward R --details D --jobs 2`, from a copy of main's `grade.py`,
  `constants.py`, `engine.py` and `data/`.
  - b7qdG8X: reward 0.284874, 3431 s.
  - imWnpTP: reward 0.991597, 3651 s.
  - reference: stopped.
- Probes, each run as `python -I probes/NAME.py GRADER SUB …`:
  - `pull_probe.py`, `pull_trace.py`, `pull_fine.py` (b7qdG8X);
  - `back_probe.py`, `prewind_probe.py` (QZeuFhk);
  - stopped before output: `b7_at4.py` (b7qdG8X AT-4, with AT-5/AT-6 at a 0.01 mm pull step) and
    `direction_probe.py` (GPT prelim).
- Brief with Part 5 on: `make_brief_job.py --keyless OUT` (main 87c526c), read for section 9 of QA-W100 and DS-501.
  DS-501 is not cited by QA-W100's Part 5, and nothing grades its torque limit.
