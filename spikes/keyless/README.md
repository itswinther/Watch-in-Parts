# Spike: keyless works graded by simulated contact (workstream A)

This spike asks whether a mechanism that changes behaviour with direction and position opens a gap,
when it is graded by simulating contact rather than by declared tooth counts. In CADEngBench,
pin-slot joints scored 0 out of 6 for every model and planar contacts 10%, while revolute joints
scored about 60%; see `../RESEARCH_GAPS.md`. Here the agent must design the watch's **keyless
works**:

- **Position 1, forward:** turning the crown forward winds the barrel.
- **Position 1, backward:** turning it backward slips (Breguet ratchet teeth), and a click stops the
  mainspring running back.
- **Position 2:** pulling the stem out shifts a sliding pinion over to the setting train. Turning
  the crown then sets the hands and does not wind.
- **The pull in between:** at every point the mechanism is in one clean mode or disengaged. It is
  never jammed and never drives both trains.

Nothing here changes B's task.

## Engine (`engine.py`)

The engine is quasi-static and runs on manifold3d. Each body has one degree of freedom (rotation
about a line, or a slide), and each body has a kind:

- **fixed:** never moves.
- **driven:** the stem; its rotation and pull are set by the scenario.
- **contact:** moved only by pushes.
- **spring:** light. It yields first when touched, and returns towards rest until contact. It never
  pushes.
- **main:** the mainspring arbor. It tries to turn back each step and pushes the train.

Contact is resolved step by step:

- **Contact rule:** each pair may overlap by at most 2e-4 mm³. A pushed body moves the least distance
  along its degree of freedom that clears the bodies that moved in this step.
- **Friction cone:** a pushed body may move at most K = 2 times the pushing surface travel. So a face
  steeper than atan 2 ≈ 63° locks (a click face, or the vertical face of a Breguet tooth), and a
  gentler ramp slips.
- **Blocked steps:** a step that cannot be resolved blocks the input, and nothing moves.

Toy tests (`python test_engine.py`, under 1 s) all pass:

| Test | Result |
| --- | --- |
| Spur pair 12:24 | ratio -0.491 (expected -0.5) |
| Ratchet and pawl | free forwards, locks backwards within one tooth |
| Mainspring with click | arbor holds (-0.24°); without a click it unwinds (-9.6° in 20 steps) |
| Detent | lifts 0.10 rad and snaps back within 0.007 rad |

## Task

- **Brief:** `build_task.py` writes it from `constants.py` and `engine.py`, so the numbers cannot
  drift. It states every rule of the simulation; only the verdicts are hidden.
- **Supplied parts (`supplied.py` → `data/`):** the main and dial plates, the barrel arbor, and a
  minute-wheel stand-in on its post.
- **Grader (`grade.py`):** runs with `python -I`, opens only named files, never runs submitted code,
  writes reward 0 first, and puts each check in its own try block.
  - **Hard requirements:** files, and no overlap at rest.
  - **Scenarios:** four, run in parallel: wind (360° forward), slip (360° backward), set (pull, then
    180° each way), and the pull sweep (10 samples with test turns both ways, then push back and wind
    again).
  - **Checks:** wind 3, slip 2, click 2, set 3, sweep 3, held 2, bounds 1.

## Reference (`reference.py`)

| Part | Design |
| --- | --- |
| Winding pinion | 12-tooth involute, module 0.15, with 8 Breguet face teeth |
| Sliding pinion | on the stem square, with matching Breguet teeth and 12 spur teeth at its outer end |
| Crown wheel | face gear cut by envelope with the pinion (36 teeth), with a 12-tooth spur pinion on top |
| Barrel wheel | 36 teeth, with a 24-tooth ratchet ring |
| Click | its pivot lies on the tangent through its tip, so it locks |
| Setting wheel | face gear below the stem, with a 12-tooth pinion driving the minute wheel |
| Stem | a collar in the sliding pinion's counterbore drags it out of the Breguet teeth and into the setting wheel when pulled; the sliding pinion's spring pushes it back |

Results on the reference:

- **Wind:** 39.7° per stem turn (9.06 turns per arbor turn).
- **Slip:** free; the barrel holds within 0.3°.
- **Set:** the minute wheel turns ±19.2° per 180°.
- **Sweep:** winding at pull 0 and 0.1, disengaged from 0.2 to 0.4, setting from 0.5 to 0.9.
- **Grading time:** about 160 s on 4 cores.

## Reproduce

```
python supplied.py data
python reference.py SUB && python -I grade.py SUB data --reward r.txt --details d.json
python anchors.py WORK 3            # every anchor, exit 0 when all ok
python build_task.py TASK --agent codex --oracle-submission SUB
```
