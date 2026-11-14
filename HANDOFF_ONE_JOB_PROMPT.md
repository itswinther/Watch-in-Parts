# Start prompt for the session that takes over workstream B

Start a new cloud session on this repository. Paste everything in the block
below as the first message.

```
You are taking over workstream B (the watch task's spec, grader, reference and anchors) in this repo for itswinther. You may push to main; that is the answer to the question CLAUDE.md tells you to ask.

1. Sync: git fetch origin && git merge origin/main. Read CLAUDE.md, then HANDOFF_ONE_JOB.md in full. It is your brief: where things stand, what is decided, what is not built, and how to work with Mikael. Then read SESSION.md: the Current state table, "To do, in priority order", every open line under Requests, the Decisions dated 14 Nov from 13:00 on, and the last ten entries.

2. Talk to Mikael's session before you build anything. You cannot message it; the only channel is SESSION.md on origin/main. In your first push:
   - append an entry saying a new session has taken over row B, and update row B of the Current state table;
   - read spikes/keyless/INTERFACE_FOR_B.md and write under Decisions whether you confirm the interface he proposed (stem line, crown position, the square on the barrel arbor, plate regions, the engine's entry point), or what you change, with the reason;
   - add one Requests line to A asking for the current state of the keyless reference and engine (it scored 0.72 on its own task at 14:05, with one exploit open), and anything in the datasheet quantities that has changed since his entry stamped 14:20;
   - answer and tick any open request addressed to B.
   After that, fetch, merge and re-read SESSION.md before each new piece of work and before every push, and put anything both workstreams depend on under Decisions before either side builds on it.

3. Then tell me, in a few lines: what is on main, what you would build first, and the open choices from section 2 of the handoff that need my yes (the barrel change as a variant, the weights of the five parts, whether the delivery step may still report file-format errors, what replaces the volume limits). Do not start building until I say go.

4. When I say go, work as the handoff describes: brief builder agents in their own git worktrees (two at a time, because four at once hit my usage limit), merge their branches, run the acceptance commands yourself, and have a fresh reviewer read the result. Every brief you write must stand alone. Do not report anything as working that you did not run, and log each milestone in SESSION.md with the commands and what they printed.

5. Principles that are decided and not up for redesign: nothing is frozen and the agent gets one brief from start to finish; five parts (going train and hands, 24-hour hand, barrel change, crown winding, assembly); no hints and no feedback to the agent; every part counts even if an earlier one failed, and the whole build is scored too; datasheets in the environment; tokens, time and cost are recorded but not scored; 8 runs per model in Docker and Modal through Harbor. We do not design for failure: report results as they are, and never tune a rule to make a model fail.
```

If the session stops early, start a new one and paste the same block; the
handoff and `SESSION.md` carry the state.
