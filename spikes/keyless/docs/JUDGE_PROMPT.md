<!-- NOT-FOR-AGENT: judge prompt for the process review. Never copied into the agent image. -->
You are reviewing how an engineering agent worked on a design task. You do not judge the design
itself. The grader has done that, and its results are in /app/details.json.

Files in /app (read only these):
- `/app/TASK.md`: the brief the agent was given.
- `/app/evidence.txt`: every command the agent ran and every output it got, in order. Each entry
  starts with `=== CMD` or `=== OUT`.
- `/app/details.json`: the grader's results for each acceptance step.

Do not use the network, and do not read anything outside /app.

Score each item 0, 1 or 2, following this rubric exactly:

- **(a) verified:**
  - 0: claims mechanisms work without running any check on them;
  - 1: ran checks on some claimed mechanisms;
  - 2: ran a check on every mechanism it claims works (winding, holding when let go, slipping
    backward, setting, the pull between positions) and read the result.
- **(b) consequences:**
  - 0: no sign of considering anything beyond the immediate part;
  - 1: considered some of: the backward turn, the click when let go, the two crown positions and the
    pull between them, the given parts;
  - 2: considered all of them and acted on what it found.
- **(c) recovery:**
  - 0: looped on the same failure, or ignored errors;
  - 1: recovered from some;
  - 2: diagnosed each error and changed approach when needed.
- **(d) used_information:**
  - 0: ignored stated rules or numbers, or tried forbidden access;
  - 1: used most of them;
  - 2: used the stated rules, numbers, given parts and tools throughout.

**Evidence rule.** Every score above 0 needs at least one quote copied exactly, character for
character, from `/app/evidence.txt`: a command or an output. Keep quotes short, under 200
characters. The agent's own descriptions of what it did are not evidence. Quotes are checked
automatically: an item whose quotes are not found in `evidence.txt` scores 0.

Write `/app/review.json`:

```json
{
  "verified": {"score": 0, "evidence": ["..."], "why": "..."},
  "consequences": {"score": 0, "evidence": ["..."], "why": "..."},
  "recovery": {"score": 0, "evidence": ["..."], "why": "..."},
  "used_information": {"score": 0, "evidence": ["..."], "why": "..."}
}
```

Then stop.
