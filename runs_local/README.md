# B's local (unsandboxed) agent runs, 14-15 Nov 2026

Each folder is one `claude -p` conversation started by `environment/run_clean_job.sh` in B's cloud container. These runs were NOT sandboxed: the agent was told to stay inside its folder, and nothing enforced it. An audit of every tool call in every transcript found no access outside the run's own folder and its Claude Code scratch folder. Files: `agent.jsonl` (transcript), `details.json` / `reward.txt` / `grade.log` (one-job grader), `delivery.tar.xz` (the delivery as submitted), `start`/`end` (unix time).

| Run | Brief | Model | Result |
|---|---|---|---|
| smoke1_*, smoke2_* | four-part one-job brief | Fable, Opus, Sonnet | 1.0 each (see SESSION.md) |
| qa1_*, qa2_sonnet | brief with QA-W100, strength, honesty | Fable, Opus, Sonnet | see SESSION.md |
| thin1_opus | thinness probe, target 9.0 (b/thin-probe 05f254b) | Opus | 1.000, H 8.35, radius 19.00 |
| thin1_sonnet | same | Sonnet | 1.000, H 8.10, radius 19.05 |
| thin2_* | 4.0 mm brief (b/thin-4mm 92d9622) | Opus, Sonnet | stopped by itswinther at about 8 min, no delivery |
