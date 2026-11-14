## What you are given to work with

There are no measuring tools and no copy of the grader's test code. Every test
above is defined completely by its numbers, so you can build your own checks.

- Python 3 with `cadquery` 2.8.0 (OpenCASCADE, importable as `cadquery` and
  `OCP`), `manifold3d`, `trimesh`, `numpy` and `scipy`.
- `tools/kernel.py`: small helpers on top of `manifold3d` (read and write STL,
  used for the supplied barrel and for your own checks; rigid transform, intersection volume, smallest distance, cross-section), plus
  `write_step(path, shape)` (a CadQuery object or OCP shape, written in
  millimetres) and `load_step_part(...)`, which turns a STEP file into the same
  `manifold3d` solid the grader uses. `python3 tools/submit.py` calls it with the
  numbers stated under "What you submit", so a part that submit accepts is the
  solid the tests see.
- `meshes/barrel.stl` (the supplied barrel, the only mesh; your parts are STEP).
- `python3 tools/submit.py`: checks the file format only (JSON structure, part
  names, each part file read and turned into a solid exactly as described under
  "What you submit") and copies your work to the submission folder: the
  `movement.json`, the part files it names, `assembly.json` if present, and
  `scripts/` (at most 200 files and 4,194,304 bytes; larger is a format error).
  It answers "accepted" or a format error. It runs none of the tests.

Only the submission folder as it is when you stop is graded. You may submit as
often as you like; the last accepted submission counts.
