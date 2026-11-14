# What published benchmarks say about where frontier models fail (read 14 Nov)

Four papers were read in full (workstream A, Mikael + Claude). The question was: where do they
show frontier models failing at physical design, and would that failure survive an agent with
Python in our sandbox?

| Paper | Task | Headline result | Could the agent run code or the simulator? |
|---|---|---|---|
| LMBuild (arXiv 2610.04292) | Build objects with working joints from a label and an image; MuJoCo scores operability | Operability out of 100: GPT-6 Astra 19.2, GPT-5.6 Sol 19.1, Opus 5 22.1, Fable 5.1 20.8. Joints and kinematics about 40. Structure 83-97 | No. No files or code, 6 rule checks and 4 renders per episode. The movable parts are never stated (hidden affordances) |
| Physics-in-the-Loop (IJCAI 2026) | CadQuery part for a load case; safety factor in [2, 5] while minimising volume | Opus 4.5 72.7%, Sonnet 4.5 56.3% in range. Without FEA feedback 22% in range, with it 59% | No. Only a reviewer agent ran FEA. Thinking was off |
| BuildArena (ICML 2026) | Long build sequences in Besiege: Transport, Support, Lift, levels 1 to 3 | GPT-5 Lv.1 78-95%, Lv.3 11-27%; others 0-16% at Lv.3 | No. Single shot with geometry feedback only. With physics feedback, failed Support Lv.1 runs reached 100% in 5 rounds |
| Compositional Machine Design (arXiv 2510.14980) | Besiege machines from construction trees; includes a gearing task | Gearing passes out of 50: Gemini 2.5 Pro 45, o3 38, Opus 4 4, random placement 5 | No. The pipeline runs the simulator and returns summaries |

## Conclusion

Every published gap rests on at least one of three supports:

- **No code execution or simulator for the agent.**
- **One-shot submission.**
- **Requirements that are never stated.**

Each paper's own ablation shows simulation feedback closes most of its gap: in BuildArena
failed runs reached 100% within 5 rounds, and in the IJCAI paper feedback raised the
in-range rate from 22% to 59%. Our setup gives the agent Python, and the brief states every
rule. That combination produced all of last night's 1.0 scores.

## What still survives a Python sandbox

1. **Optimisation against a strong reference, not pass/fail.** The IJCAI agents all
   over-built, with a mean safety factor of 4-5 where 2 was allowed. Minimum volume (or
   minimum layers or size) at a fixed requirement is open-ended. It needs a reference that is
   actually optimised; our planted references were random valid designs and got beaten.
2. **A grader the agent cannot rebuild exactly**, such as MuJoCo or contact dynamics, used
   for scoring only. This is risky: the agent can write a close approximation, and any
   mismatch between its check and ours looks like noise unless the rule is stated.
3. **Frozen stages and long sequences.** BuildArena scores fall as parts go from 15 to 83.
   Together with B's result, this is the lever that leaves the information untouched.
4. **Hidden requirements (LMBuild's affordances).** These work, but they restrict
   information, which the brief for this work ruled out.
