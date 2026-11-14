## What you are given to work with

There are no measuring tools and no copy of the grader's test code. Every test
above is defined completely by its numbers, so you can build your own checks.

- Python 3 with `manifold3d`, `trimesh`, `numpy` and `scipy`.
- `tools/kernel.py`: small helpers on top of `manifold3d` (read and write STL,
  rigid transform, intersection volume, smallest distance, cross-section).
- `meshes/barrel.stl`.
- `python3 tools/submit.py`: checks the file format only (JSON structure, part
  names, each STL a closed manifold shell) and copies your work to the submission
  folder. It answers "accepted" or a format error. It runs none of the tests.

Only the submission folder as it is when you stop is graded. You may submit as
often as you like; the last accepted submission counts.
