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

---

# Second round: the six CAD papers from B's 09:44 entry, read in full (14 Nov, 11:00)

B's session could see only search summaries. All six were read in full here, appendices included,
and the summaries were checked against the papers.

| Paper | What the summary said | What the paper says | Could the agent run code? |
|---|---|---|---|
| **CAD-bench** (github.com/CAD-bench/cad-bench, anonymous, "submitted to NeurIPS 2026"; the ICML-workshop claim is unconfirmed) | Agents fail often on interfaces and mechanisms | 17 tasks. Agents (Codex and Pi harnesses, GPT-5.4 and 5.4-mini) score 90.6 easy, 84.9 medium, 76.1 hard, **14.1 functional**. **Right-angle gearbox 0.040 mean with 96.9% built**; threaded pair 0.071 with 93.8% built; compound gearbox 0.138; two-gear transmission 0.316. Kinematics are checked by rigid-body simulation in Blender | **Yes**, agent harnesses with tool feedback. Whether they could run the simulation themselves is not stated |
| **Parametric CAD Bench v3** (2611.02659) | Opus 5.5 low 40s on edit, over 80 on drawings | Correct: Claude Code + Opus 5.5 scores 50.9 creation, **39.7 create-and-edit**, 84.7 drawing-to-CAD. All 5 tasks that every system scored 0 on are edit tasks. But the "edit" regenerates both versions from scratch, and part of the difficulty is a hidden parameter check on the feature tree | Yes (Harbor 0.23, Claude Code, Codex and others) |
| **Done Is Not Correct** (2611.10063) | 98% claim done, 14.1% silently wrong; measure-then-claim brings it to 3.2% | Correct, but for Haiku 4.5, Sonnet 4.6, DeepSeek and Qwen, with no shell and 4 turns. Sonnet 4.6 with tool feedback: 100% success, 0% silent failure. Silent errors concentrate in **internal features** (bore depth, counterbores, holes off the main axis), and 13 of 31 came from one task whose spec had two readings | No (the harness ran the code and returned measurements) |
| **CADEngBench** (2608.09296) | 1,030 of 2,400 run, 432 of those pass the next level; coupled edits and face grounding hard | Correct. **Edits that join or cut existing bodies pass 40-46%; edits that add a separate body pass 247/248.** Assembly end-to-end 11.5%; pin-slot 0/6 for all models | No (one response, GPT-5.2 and Sonnet 4.5 era) |
| **RealCADBench** (2609.03773) | All 25 assembly tasks executed; surface overlap 0.10-0.12 | Partly wrong. Only Codex + GPT-5.5 executed all 25; Claude Code + Opus 4.8 executed 88%. Surface overlap 0.116 and 0.086. The agent loop fixes execution, but fine detail and placement stay wrong | Yes (Codex, Claude Code) |
| **Text2CAD-Bench** (2605.18430) | Big drop on sweep, loft and shell | Correct (68-92% invalid at L3), but with 3 retries and no agent. The failures are mostly kernel errors that an agent loop would likely repair | Partly (error and 3 retries) |

## What this adds

1. **The strongest evidence with agents that run code is CAD-bench's functional tier**, especially
   the **right-angle gearbox**: 97% of attempts build, and they average 4% once kinematics are
   simulated. That is B's proposal 3 (a winding stem at right angles, with crown or bevel teeth). It is the one
   proposal with published evidence of a gap for code-running agents. Caveat: GPT-5.4 is older than
   GPT-6.1-sol, and CAD-bench's grader had blind spots (a narrowed tooth still scored 0.943, a 5% lead
   error 0.971). Our tooth and mesh checks must be exact.
2. **Edits coupled to existing geometry** (cut into or join a frozen part) are the second lead: 40-46% in
   CADEngBench and about 40 for Opus 5.5 in Parametric v3. Neither paper is a clean test with a strong
   agent, because one has no execution and the other hides its checks. In our task this would be a stage
   that hands the agent a frozen STEP part to *modify* (a new bore, counterbore or jewel seat), graded
   on the new feature plus untouched faces identical to the original. This is B's proposal 6 in a
   stricter form.
3. **Internal features are where silent errors live** (Done Is Not Correct, RealCADBench). Check bore
   depths, counterbores and off-axis holes per feature, never by volume or IoU alone.
4. **Ambiguity produces fake gaps.** One spec with two readings gave 13 of 31 silent failures. Every new
   rule needs a reference solution and a read by someone else before release.
5. **Do not use** IoU, Chamfer distance or an LLM judge as the main score (they reward near misses, and
   judges don't repeat). Do not count execution or "builds" as difficulty: agent loops saturate them.
