# Visualizer

A self-contained copy of the Replay demo, for Mikael to add his visualizer to.
It needs no build step, no server and no Python: open `index.html` in a browser.

## What is in this folder

| Path | What it is |
| --- | --- |
| `index.html` | the Replay page |
| `app/` | its script (`replay.js`), style (`replay.css`) and the 3D frame template |
| `data/` | the runs the page shows (`index.js`, `runs/<run>.js`) |
| `scenes/` | the 3D watch for each section of a run, shown in the page's frame |
| `source/` | the scripts that build it: `build.py`, `check_data.py`, `adapters/`, and Replay's own README and CLAUDE.md |
| `README.md` | this file |

This is the built output of Abhishek's Replay project, copied here on 15 Nov. It shows ten
runs on the final task, every score from the final grader 3d5d96f (files on branch
`a/final-runs`, `runs/final_*`):

- GPT-6.1-sol, all six runs (Harbor + Codex): owFDECg 0.427, oVS4tLK 0.427, fhhWYjp 0.447,
  k843CBe 0.448, dQKXa6k 0.457, UVsdmwL 0.467. The three made on task commit 4c5d8d3 use
  Mikael's regrade on 3d5d96f.
- The four Claude runs that delivered a watch (Harbor + OpenCode): Opus 5.5 medium Qob53oe
  0.943 (every check passes; it loses only on thickness, 4.23 mm), Opus 5.5 low gpCasL8 0.422
  (score disputed: H's regrade gives 0.082, see the run's note), Sonnet 5.5 low TxhN8Ly 0.422
  and 8Wrjav3 0.412. Four other Claude runs scored 0 with nothing delivered (API usage limit
  or output limit) and are not shown.

Each run has Parts 1 to 4 (what the grader checked) and Part 5, a review: where it failed,
what the AI reported, and how the score is made (reproduced from the grader's output; the
build stops if it does not match). The agent's own `report.json` is the log, because Harbor
kept no transcript. The 3D view shows in red the parts behind each failed check (hands that
break the hand rule, wheels that collide, that nothing holds, or whose teeth bite too little
when moved 0.03 mm, wheel pieces not seated), and drags like Mikael's X-ray viewer. The
X-ray button shows the run's watch in Mikael's X-ray viewer (made with his
`tools/viewer/export_watch_demo.py`, unchanged); in X-ray mode, Reference switches to his
`xray.html`, the final task's reference watch.

To rebuild: put the files of `source/` next to `index.html` and `app/` in a folder beside the
team repo, fetch the runs as `source/README.md` says, then `python3 build.py` and
`python3 check_data.py` (the 3D needs the `.venv` it describes).

## Where the visualizer goes

Put the visualizer page in this folder as its own file, for example `xray.html`.
It should:

- be one self-contained HTML file, the way the team's `tools/viewer/export_watch_demo.py`
  writes them (parts embedded; external scripts only from a CDN such as jsdelivr);
- open straight from disk, with no server;
- fill its window (`width: 100%; height: 100vh`), because Replay shows 3D in a frame
  (`<iframe id="scene">` in `index.html`, its `src` set in `app/replay.js`).

Then add it to the table below. Linking it into the Replay page (a tab or a button that
loads it in the frame) is a small change in `index.html` and `app/replay.js`.

## Visualizer pages

| File | What it shows | Made by |
| --- | --- | --- |
| `xray.html` (still: `xray.png`) | X-ray view of the whole watch: B's movement (going train, hands, barrel) with A's keyless v1 reference, plus the dial side. Parts embedded; three.js from a CDN; fills its window. Made by `tools/viewer/export_watch_demo.py`, from the team's own reference geometry only, no third-party CAD. Keyless motion is a recorded sample trace of the v1 engine. Three base64 mesh runs had a space inserted after `AI` so the secret scanner does not mistake them for Google keys; `atob` ignores it. **Next:** v2, replaying every step AT-0..AT-6 from the merged engine's traces with pass/fail numbers and contact highlights. | Mikael |
