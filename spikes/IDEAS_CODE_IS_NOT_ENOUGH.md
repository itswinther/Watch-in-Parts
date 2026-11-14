# Task ideas where writing a program is not enough

Written overnight 14 Nov (workstream A, Mikael + Claude) after every spike was solved by an
agent that wrote a search or a simulator. Code wins when four things hold: the rules are
complete enough to encode, testing is free, the search fits the time, and the physics is
known from the brief. Each idea below breaks at least one of them without hiding rules:
everything the agent needs is either stated or measurable.

| # | Idea | What breaks for "just write code" | Expert intuition it needs | Grader |
|---|---|---|---|---|
| 1 | **Regulating a watch** (timing machine in a sidecar) | Physics is hidden per seed and can only be measured, noisily, at a cost in time; mass removal from the balance is irreversible | Poise errors show only in vertical positions and flip sign with amplitude; fix poise before regulating; do not chase noise | Exact: final true rate spread over positions and wind states, against a scripted watchmaker |
| 2 | **Five-step movement** (built tonight, `gear_task/`) | Steps reveal new requirements (larger balance, date, auto-winding); early choices constrain later ones; rules interact across three sides | Leave room near the balance and around the barrel arbor; keep the hour wheel small enough to drive a date wheel | Exact geometry and rate checks per step, mean over steps |
| 3 | **Print compensation** | Printer distortion is hidden and measured only through a few test prints | Which calibration pieces separate shrinkage, sag and hole closure | Dimensional error of the final part on fresh noise |
| 4 | **Selective assembly** | Parts come with random manufacturing errors; measuring each costs budget; pairing decisions are irreversible | Measure the parts whose errors matter most; pair long with short | Fraction of assemblies within tolerance |
| 5 | **Tolerance stack under wear** | A movement must keep time after simulated years: wear grows clearances, the agent chooses jewels and materials under a cost budget | Where wear actually matters (escapement, high-speed pivots) | Simulated rate drift after N years |
| 6 | **Diagnosing a stopped watch** | A faulty movement (hidden fault among many) and a budget of inspections; each disassembly risks damage | Symptom-to-cause reasoning; cheapest discriminating test first | Fault identified and repaired with fewest risky steps |

## Which to try first

1. **Idea 2** runs tonight (Harbor, Codex, sandboxed); it is the cheapest because it extends
   tested code.
2. **Idea 1** is the strongest on paper: it needs a simulator the agent cannot read, so it
   runs as a Harbor compose sidecar holding the hidden physics, and the agent reaches it only
   through a narrow HTTP interface. Nothing it needs is withheld; it must measure it.
3. Ideas 3 to 6 share idea 1's pattern (hidden state behind a measurement budget) and can
   reuse its sidecar.

## Rules every one of these keeps

- Fully sandboxed in Harbor: no internet beyond the model's own address, grader in a separate
  container, hidden state in a sidecar or the verifier, never in the agent's image.
- The brief states every rule and every formula's structure that a professional would know;
  only per-instance numbers are hidden, and they are measurable.
- A scripted reference that a human can explain, plus do-nothing and stop-early anchors.

## Results so far (14 Nov, GPT-6.1-sol via Codex in Harbor, sandboxed)

- Idea 2, five-step movement: 1.0, 1.0, 1.0. No gap.
- Idea 1, regulation with hidden physics in a sidecar: 1.0, 1.0, 1.0, beating the scripted
  watchmaker. Stating the formula's structure turned it into a least-squares fit, which the
  agent wrote in one go. Measurement noise and the time budget were not binding.

What this suggests: the hidden-measurement pattern only bites if the agent must also find the
model's structure, or if measurements are scarce enough that the order of experiments
matters. Both move toward "less information", which the brief for these ideas ruled out, so
that trade-off needs a team decision.
- Idea 1 with a 100-minute budget (6 hidden watches, 2 runs each): mean 0.974, GPT beat the
  scripted watchmaker on 7 of 12 runs. Scarce measurement was not enough either.
- The five-step movement allowed changing earlier parts at every step. B's staged watch
  freezes earlier stages, and that produced the only shortfall seen tonight, so freezing is the
  lever worth pursuing; a frozen version of the five-step movement would be a quick test.
