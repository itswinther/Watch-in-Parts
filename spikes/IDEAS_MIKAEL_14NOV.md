# Mikael's ideas, 14 Nov (workstream A), with what we found

Written by Mikael + Claude. Each idea says where it stands and what backs it.

## 1. Position-dependent mechanisms: the main lead

**Idea:** mechanisms where the motion depends on position or direction, with no in-between. Examples: a
ratcheting winch that, when pushed aside, ratchets the other way; parts that change behaviour at
certain angles; many parts whose function depends on where the others are.

**Why it should hold up against strong agents:**
- Every gap we have seen came from **consequences of geometry that no rule names**:
  - Sonnet's closed bore, which made a part impossible to install two stages later;
  - GPT's turning-tool flank on a face that points at the bushing (Swiss probe).
- Published evidence: in CADEngBench pin-slot joints passed 0 of 6 for every model and planar contacts 10%,
  against about 60% for revolute joints. CAD-bench's functional mechanisms were the weakest tier (right-angle
  gearbox 4% while 97% built).
- An agent cannot check such a design with ten lines of arithmetic. It needs a contact simulation (springs
  pushing parts into contact, teeth riding over each other). Agents approximate that, and the approximation
  is where they should go wrong.

**Watch version (being built, `spikes/keyless/`):** the keyless works.

| Crown | Turned | Must happen |
|---|---|---|
| Pushed in | Forward | Barrel winds through the right-angle crown wheel |
| Pushed in | Backward | Breguet ratchet teeth slip; nothing winds; the click holds the barrel |
| Pulled out | Either way | Hands turn; barrel does not |
| Anywhere between | — | Cleanly one mode or disengaged: never both trains, never jammed |

Graded by a quasi-static contact simulator: parts move only as far as contact pushes them, and
spring-loaded parts return toward rest.

Other watch-native candidates:
- the instantaneous date jump (still for 24 h, then one snap into a detent);
- the Geneva stop-work (N turns of winding, then blocked);
- bidirectional automatic winding with reverser wheels.

## 2. Rare domain tools and knowledge, not complex shapes

**Idea:** the gap is knowledge that is not common in training data and that companies pay for, not "make a
complex shovel".

**Tried:** the Swiss-type CNC lathe probe (`spikes/swiss_probe/`), programming a watch arbor on a
sliding-headstock machine.
- Opus, Fable and GPT all found the expert solution once the machine's limits were stated: sub-spindle
  pickup, synchronisation, and the rear pivot made while supported.
- The one difference came from something unstated that follows from tool geometry. GPT made a face pointing
  at the bushing with a turning tool; Opus and Fable used the grooving tool.

**Lesson:** stated rules become arithmetic. Domain knowledge bites when it lives in the *consequences* of
stated geometry (tool shapes, part shapes), checked by a simulator. That is the same thesis as idea 1.

## 3. Bias: Claude designing tasks and grading other models

**Concern:** Claude designing the task and judging Claude and other models is like a mark scheme marking
its own homework. A model cannot list its own blind spots.

**What we do about it:**
- Scores come from deterministic code (geometry, kinematics), never an LLM judge. LLM judges favour their
  own outputs: Wataoka et al. 2024 (arXiv 2410.21819), and a 2026 rubric study.
- Difficulty comes from outside the designer: physics, published failures, real shop practice.
- We test several model families: GPT through Codex and OpenCode, Claude, and Gemini if a key arrives.
- Rubrics are written and committed **before** model answers.
- A human expert (watchmaker or machinist) should read the spec and failures. That is on the to-do list.

## 4. Expert designs the models have not seen

Sources, cheapest first:
- generated instances (planted designs, constraints only), which we already use;
- our own traced failures, turned into test cases;
- published practice cited as the source of each rule (Daniels' *Watchmaking*, BHI and AWCI course
  material, machining articles);
- one concrete question on a watch-repair forum;
- a cheap movement measured by hand (Seagull ST36, about €40).

An unseen design only matters when the task built on it still resists writing a solver.

## 5. Realism of size

The watch task is about 1.5 times a real movement's width and 2 to 3 times as thick, because of the 0.2 mm
printability minimum (an anti-sliver check and a grading-cost limit). Proposal: present it as a clock or
large-scale demonstration movement, keeping the numbers. A thinness score was dropped: it ranked the model
that failed (Sonnet) as most compact.

## 6. Harness: use OpenCode as the organisers ask

- OpenCode runs in our sandbox: Haiku 5.5 smoke test, allowlist api.anthropic.com only, key in no log.
- **Harbor 0.25 always reinstalls OpenCode from the internet** (blocked by the allowlist); 0.26 skips the
  reinstall when OpenCode is in the image. Pin 0.26, or bake OpenCode in and check the organisers' version.
- One Haiku stage ended with no output: a single turn used the whole 32k output budget on reasoning. That
  is a harness limit, not task difficulty, and it must be ruled out for the judged model.
