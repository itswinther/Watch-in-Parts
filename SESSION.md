# SESSION.md

The shared log for four people and their Claude sessions. Read it when you start.
Append to it when you reach a milestone or stop. Edit only your own row in the
table. Everything below "Session entries" is append-only, newest at the bottom.

## Current state

| ID | Workstream | Owner | Status | Last update |
| --- | --- | --- | --- | --- |
| A | Harness wiring | unassigned | not started | |
| B | Reference script and grader (H1) | unassigned | not started | |
| C | Hold the Line spike | unassigned | not started | |
| D | Mentor questions, anchors, transcripts | unassigned | not started | |

Spec version in use: 0.1

## Deadlines (Helsinki time)

- Sat 03:00 harness wired end to end
- Sat 07:00 both spikes done
- Sat 09:00 decision between the two ideas
- Sat 16:00 latest switch
- Sat 22:00 build-out done, anchor suite passing
- Sun 03:00 full runs and failure analysis
- Sun 09:00 README and demo ready
- Sun 10:00 final submission

## Open questions

Write the answer and who gave it next to the question, then tick it.

- [ ] Which model and effort setting do the judges run?
- [ ] Per-trial timeout?
- [ ] Wall-clock budget for the judges' rerun?
- [ ] Can the agent see images?
- [ ] How is the stop-early baseline defined?
- [ ] How large is the model-credit grant?
- [ ] Which environment provider does the rerun use? (decides compose sidecar or in-container MCP server)
- [ ] Does the organisers' OpenCode register MCP servers declared in task.toml?
- [ ] When do the AfterQuery demo and rerun happen?
- [ ] What does the scoring skeleton record when the verifier is killed or times out?
- [ ] Can agent network access be limited to the model API?

## Decisions

Append one line per decision: time, decision, who agreed.

- 2026-11-14 00:50 Working plan is the second review, updated version. SPEC.md 0.1 is taken from it.

## Proposed spec changes

Append here. A human has to say yes before SPEC.md changes.

(none yet)

## Session entries

Template:

```
### YYYY-MM-DD HH:MM | workstream | human name + Claude
- Did:
- Verified by (command and result):
- Not verified, or assumed:
- Files changed:
- Need from others:
- Next:
```

### 2026-11-14 00:50 | setup | Claude
- Did: created the repo with README.md, CLAUDE.md, SESSION.md, SPEC.md.
- Verified by (command and result): nothing to run yet.
- Not verified, or assumed: every number in SPEC.md was checked by hand only. No code exists. The spike has not run.
- Files changed: all four, new.
- Need from others: assign owners in the table above. Fill in mentor answers.
- Next: workstream A starts from the organisers' starter kit.
