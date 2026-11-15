# Replay

Pick an AI run and watch it build a mechanical watch, with what the AI was doing shown
beside it. The demo for our Junction 2026 AfterQuery entry: "It looked done. It wasn't."

Status: milestone 7. Ten runs on the final task, every score from the final grader 3d5d96f:
all six of GPT-6.1-sol's (Harbor + Codex: 0.427, 0.427, 0.447, 0.448, 0.457, 0.467) and the
four Claude runs that delivered a watch (Harbor + OpenCode: Opus 5.5 medium 0.943, Opus 5.5
low 0.422 (score disputed, see the run's note), Sonnet 5.5 low 0.422 and 0.412). Four more
Claude runs scored 0 with nothing delivered, stopped by the API usage limit or the output
limit; they are not shown. Each run has Parts 1 to 4 (what the grader checked) and a Part 5
review: where it failed, what the AI reported, and how the score is made, every number read
from the grader's output. The parts behind each failed check are shown in red. The X-ray
button shows the run's watch in Mikael's X-ray viewer; Reference switches to his X-ray of
the final task's reference watch.

## The runs

Harbor kept each delivery and the grader's output, not the agent's transcript, so the log of a
run is the agent's own `report.json`, line by line, set against the grader's verdict per part.
Three runs were made on task commit 4c5d8d3; for those, Replay uses Mikael's regrade on the
final grader (`details_grader_3d5d96f.json`). Get the files from the team repo's branch
`a/final-runs` once:

```bash
for p in $(git -C ../board-in-a-box ls-tree -d --name-only -r origin/a/final-runs runs/ \
           | grep -E "gpt-6.1-sol/task__[^/]+$"); do
  id=$(basename $p | sed 's/task__//'); mkdir -p work/gpt_$id
  git -C ../board-in-a-box archive origin/a/final-runs $p | tar -x -C work/gpt_$id --strip-components=4
done
for p in opus-5.5-medium-rerun/task__Qob53oe opus-5.5-low-rerun/task__gpCasL8 \
         sonnet-5.5-low-run3/task__TxhN8Ly sonnet-5.5-low/task__8Wrjav3; do
  id=$(basename $p | sed 's/task__//'); mkdir -p work/claude_$id
  git -C ../board-in-a-box archive origin/a/final-runs runs/final_3d5d96f/$p \
    | tar -x -C work/claude_$id --strip-components=4
done
```

Failures are worded from the grader's own numbers (`explain` in `build.py`, rules as in
`tests/grade_watch.py` at 3d5d96f): hands too short, below the frame, off-centre or too
wide; wheels whose pieces are not seated; wheels that run into each other (`clear`); wheels
nothing holds (`held`).

## One-time setup for the 3D

The 3D pages are made by the team's `tools/viewer/export_scene.py`, which needs cadquery.
Install it once into a private environment in this folder (about 1.4 GB; your normal
Python is not touched):

```bash
python3 -m venv .venv && .venv/bin/pip install cadquery==2.8.0 trimesh numpy==2.5.3
```

Without it, `build.py` still writes the data and the page shows no 3D.

## Build

Needs Python 3 (tested on 3.13) and the team repo next to this folder
(`../board-in-a-box`, or pass `--repo PATH`). The repo is only read, never changed.

```bash
python3 build.py         # unpack the runs, write data/ and scenes/ (3D: ~6 min the first time)
python3 check_data.py    # check every log line and score against its source
```

## Open the page

```bash
open index.html
```

No server needed. Click a stage at the bottom (or use the arrow keys) to see its log;
Play replays the run with each stage's score hidden until that stage ends. Hover a log
line to see the transcript line it came from.

## X-ray view

The **X-ray** button swaps the 3D frame for Mikael's X-ray viewer of the same stage
(`tools/viewer/export_watch_demo.py` in the team repo, run unchanged): see-through frame,
labelled wheels, the gear connections with tooth counts, the hand speeds checked against what
a watch needs, a running clock and a watch-face view. It does not replay the assembly path;
the normal 3D view does. Stages 3 and 4 use the 6-hour barrel, so `build.py` gives the
exporter those stages as `variant_6h.json` (the file name it reads at that speed).

## Cost

Building the 3D and X-ray pages runs on your machine and uses no AI tokens. Each stage takes
about 85 s per view, almost all of it reading the STEP files, and existing pages are reused,
so only a new run costs time. A coarser tessellation does not help: `--tol 0.05` gave the
same file and time as 0.01. Tokens are spent only when a Claude session reads the output,
which is why `CLAUDE.md` tells sessions never to open the pages in `scenes/`.

## What it writes

- `work/<run>/`: the unpacked run (made by the repo's `tests/pack_run.py --unpack`)
- `data/runs/<run>.json`: everything the page shows for one run
- `data/runs/<run>.js`: the same data, loadable from a folder with a `<script>` tag
- `data/index.js`: the list of runs
- `scenes/<run>_stage<n>.html`: the 3D watch for one section. Made by the team's
  `export_scene.py`, unchanged, then put into `app/scene_template.html`, a copy of
  `tools/viewer/viewer_template.html` with an embed mode added. Rebuild them with
  `python3 build.py --rebuild-scenes`.
- `scenes/<run>_stage<n>_xray.html`: the same section in Mikael's X-ray viewer.

A run file has `run` (model, harness, task and grader version, chain score) and
`sections` (a stage today, a part in the one-brief task). Each section has its score
and failures copied from the grader output, and `log`: short lines, each with `src`,
the transcript line it came from. Scores are never computed here.

Log line kinds: `read`, `write`, `run`, `check` (the AI's own checks), `result`,
`error`, `harness` (a Claude Code message, not the AI), `wait`, `submit`, `say` and
`think` (quotes), `done` (the AI's final message).

## Add a run

1. Add an entry to `RUNS` in `build.py`: an id, a label, the adapter and the path.
2. If the log format is new, write an adapter in `adapters/` that returns the same
   section and log-line fields, then register it in `ADAPTERS`.
3. Run `python3 build.py` and `python3 check_data.py`.
