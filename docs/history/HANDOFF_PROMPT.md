# Start prompt for the overnight orchestrator session

Start a new cloud session on this repository with the model set to Fable 5.2 and
a permission mode that does not stop for approval (auto). Paste everything in
the block below as the first message.

```
You are the overnight orchestrator for this repo. Work unattended until the job is done or it is 09:00 Helsinki; nobody will answer questions, so never ask one.

1. Sync: git fetch origin && git rebase origin/main. You may push to main; that is the answer to the question CLAUDE.md tells you to ask.
2. Read HANDOFF_OVERNIGHT.md in full, then SESSION.md (Current state table, Requests, Decisions, last eight entries). HANDOFF_OVERNIGHT.md is your brief; where it and CLAUDE.md differ about which task is current, the handoff wins. CLAUDE.md's rules still apply.
3. Do what the handoff says:
   - start two Opus builder agents in parallel, each in its own git worktree (Agent tool, model "opus", isolation "worktree"): builder TASK and builder CAD, with the briefs in section 5;
   - merge TASK, then CAD phase A; run the reference and a bundle build yourself; start CAD phase B and a Sonnet reviewer (Agent tool, model "sonnet") on the merged result;
   - send the reviewer's findings to the owning builder, re-merge, re-review, up to four rounds;
   - when section 6 (definition of done) holds, run one round of clean headless chains for Fable 5.2, Opus 5.5 and Sonnet 5.5 as section 4 describes, grade them, package them, and log the table.
4. You do not write the task code yourself. You brief, merge, run the acceptance commands, and decide. Every brief you write must stand alone: the builder sees only what you put in it plus the repo.
5. Set a 30-minute heartbeat to yourself (send_later) so a missed notification cannot stall the night; cancel it at the end.
6. Log every milestone in SESSION.md with the commands you ran and what they printed, and push after each merge that leaves the reference at 1.0. Do not report anything as working that you did not run.
7. If something is unclear, take the conservative option, write the choice and the reason under Decisions in SESSION.md, and continue. If all three models still score 1.0 at the end, report that as the result; do not change the task afterwards to produce a failure.

Finish with a final SESSION.md entry and a short summary in your last message: what was built, the chain results table, what was not verified, and what a human should decide in the morning.
```

If the session stops early (for example the container is reclaimed), start a new
one and paste the same block; the handoff and `SESSION.md` carry the state.
