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
| `README.md` | this file |

This is the built output of Abhishek's Replay project (milestone 4: Sonnet's four-stage
run with log, timeline and the 3D watch from `tools/viewer/`), copied here on 14 Nov.
The build scripts stay in Abhishek's Replay project; a rebuild there does not update
this folder, so a new build has to be copied in again.

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
