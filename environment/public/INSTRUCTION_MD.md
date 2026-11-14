# Task

It is moving day. Work out how to carry every piece of furniture into the
apartment described in `SPEC_MD.md`: the order the pieces go in, and a
pose-by-pose path for each one from the staging box to its final pose.

Write your plan to `work/plan.json`, then run the `submit` tool. Only the last
accepted submission is graded, by a separate program that replays your plan
exactly as `SPEC_MD.md` describes.

The tools are a command line:

    python3 tools/tools_md.py --help

Python 3 with `manifold3d`, `numpy` and `scipy` is installed, and you may import
the geometry code in `tools/geometry/` in your own scripts. You have about 60
minutes. Submit early and resubmit whenever your plan delivers more.
