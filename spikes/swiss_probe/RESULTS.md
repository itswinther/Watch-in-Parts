# Swiss-lathe probe: results (14 Nov, about 11:20)

Runs:
- **Opus 5.5 and Fable 5.2:** `claude -p --tools ""` in an empty folder, with no settings and no tools.
- **GPT-6.1-sol:** Codex in the Harbor sandbox (allowlist chatgpt.com, web search disabled). It reported "Outside access: None".

Each model got the same brief (`BRIEF.md`) and answered in text only. Answers are in `answers/`. Each is scored against `RUBRIC.md`, which was committed before any model answered. The scorer is Claude (this session), so a human should check the table.

| Rubric item | Opus 5.5 | Fable 5.2 | GPT-6.1-sol |
|---|---|---|---|
| 1 Z convention | pass | pass | pass |
| 2 Stickout ≤ 3.0 without the sub | pass (max 3.00) | pass (max 3.00) | pass (max 3.00) |
| 3 Sub pickup in sync, on 0.6–2.0 | pass (Ø0.80, M77 then M10) | pass (Ø0.80, M77 then M10) | **letter: fail, substance: pass**. It stops the spindle, grips while stationary, then starts both in sync. A valid way to pick up a part, but the rubric said M77 before clamping |
| 4 Sync discipline | pass (G97 before M77) | pass (G97 S10000 both) | pass (6000 rpm both) |
| 5 Parting with support, rear pivot handled | pass (T03 forms the rear pivot while gripped; it argues why T21 would deflect too much) | pass (same, with its own compliance figure) | pass (turned while gripped, then parted) |
| 6 Order of operations | pass | pass | pass |
| 7 Speed ≤ 10,000 | pass (G50 S10000, G96 S60) | pass | pass |
| 8 Dimensions and tools | pass | pass | pass (but see below) |
| **Total** | **8/8** | **8/8** | **8/8 on substance, 7/8 on the letter** |

## What separated them (not in the rubric, so not scored)

- **The face at z = 5.60 that faces the bushing** (the step from the Ø1.60 pinion blank down to the Ø0.30 rear
  pivot):
  - Opus and Fable both make it with the two-edged parting/grooving tool. Opus states why: a turning tool fed
    in the usual direction cannot generate a face that points at the bushing.
  - GPT plunges the turning tools T01 and T02 there, which leaves the tool's trailing flank to make that
    face.
  - This is real machinist knowledge and the clearest difference between the answers.
  - It needs an expert to confirm, together with the tool shapes our brief did not specify.
- **Pulling turned diameters back into the bushing:**
  - Fable keeps Z increasing once cutting starts, "so no reduced diameter is ever pulled back into the
    bushing".
  - Opus and GPT rough and then return in Z while gripped.
  - Whether this matters with the part held by the sub is a question for an expert.
- **Depth of cut:** Fable takes the front pivot from Ø2.0 to Ø0.30 in one pass. The brief no longer limited
  depth per pass (that rule went with the deflection paragraph).

## Reading

- With the rules stated, all three frontier models found the expert solution: the sub-spindle pickup on
  the shoulder, synchronisation, and the rear pivot made while supported. Stated limits become arithmetic.
  This is the same pattern as every earlier spike.
- The one real difference came from something the brief did not state as a rule but follows from tool
  geometry. If tool shapes were given and a simulator checked flank collisions, the agent would have to
  infer the consequence. That is where a domain gap could live without hiding information. One data
  point, from one model.
- Not tried: a harder part (pinion leaves cut with a hob, a longer arbor, several sub-spindle
  transfers) or a run with a simulator that executes the program.
