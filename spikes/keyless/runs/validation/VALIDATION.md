# Harbor validation (14 Nov, 17:40-18:00), all in Docker

- harbor lint: clean on task_codex and task_opencode (after fixing authors format and pinning numpy 2.5.4, trimesh 5.2.1, codex 0.169.0)
- agent image /app listing: see agent_image_app_listing.txt (BRIEF.md and the 5 supplied STLs only)
- oracle (solve.sh builds the reference): reward 1.000000 in Harbor's separate no-network verifier
- nop: reward 0.000000
- reference with trace (grader run outside Harbor, Docker): product 1.0, honesty 1.0, reward 1.0, 1213 s; replay page runs/reference/replay.html
