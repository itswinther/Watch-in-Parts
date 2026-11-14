<!-- NOT-FOR-AGENT: background for judges and teammates. Never copied into the agent image. -->
# Keyless works: context

## What keyless works are

Every mechanical watch has a crown, and behind it a small mechanism with one job: let the owner wind
the mainspring and set the hands through the same stem. Watchmakers call it the keyless works,
because before about 1850 watches were wound and set with separate keys.

It changes what it does with the crown's position and turning direction:

- **Pushed in, turned forward:** the mainspring winds.
- **Pushed in, turned backward:** nothing happens. Teeth ratchet over each other, and the spring
  stays wound.
- **Let go:** the mainspring must stay wound. A click (a small spring-loaded pawl) holds the ratchet
  wheel.
- **Pulled out:** a lever system shifts a sliding pinion away from the winding train and onto the
  setting train. Turning the crown now moves the hands and must not wind.
- **In between:** there must never be a position where both trains are driven, or where the
  mechanism jams.

## Why it is hard for a model, even with code

- **Behaviour comes from contact, not from numbers.**
  - Whether a ratchet slips or drives depends on the angle of a face. Whether a click holds depends
    on where its pivot sits relative to the tooth that pushes it. Whether the pull is clean depends on
    the order in which teeth leave one train and meet the other.
  - None of this reduces to a tooth count or a ratio that a solver can search over.
- **Modes and history.**
  - The same part does different things at different crown positions and directions.
  - A defect often shows up only in a later operation. A click that is lifted out during winding
    shows up only when the crown is let go. A pinion that touches the setting train while it slips
    backward shows up only on the backward turn.
- **Checking it yourself means writing a contact simulator.** A designer agent with Python can do
  that, but the simulator is the hard part, and an approximate one misses exactly the locking and
  slipping that decide the outcome.

## Evidence that this is where models fail

- **CADEngBench** (arXiv 2608.09296): pin-slot joints scored 0 out of 6 for every model, and planar
  contacts about 10%. Revolute joints scored about 60%. Contact-driven, multi-mode joints are the
  weakest category.
- **CAD-bench** (github.com/CAD-bench/cad-bench): agents running code scored 90.6 on easy, 84.9 on
  medium and 76.1 on hard parts, but 14.1 on the functional tier. The right-angle gearbox averaged 4%
  with 97% of attempts building.
- **Our own right-angle spike** (`../right_angle/`, with declared meshes and ratio checks): GPT-6.1-sol
  scored 1.0 on 3 of 3 trials and Sonnet 5.5 scored 1.0. Checks that can be copied into the agent's
  own script (declared tooth counts, ratios, sampled overlaps) were reproduced and passed. That is why
  this task grades behaviour by simulated contact instead.
- Full notes: `../../RESEARCH_GAPS.md`.

## What each acceptance step means to an owner

| Step | The owner's view |
| --- | --- |
| 1 Wind | "I turn the crown and feel it winding." |
| 2 Hold | "I let go and it does not spin back down." |
| 3 Run | "A few turns give me the stated power reserve, and winding does not stop the watch running." |
| 4 Backward | "Turning the crown the wrong way does nothing and breaks nothing." |
| 5 Set | "I pull the crown, the hands move, and I am not winding at the same time." |
| 6 Return | "I push it back in, and it winds again." |
