# Task

Design the gear train of a mechanical wristwatch. The mainspring barrel is
supplied in `meshes/barrel.stl`; it turns clockwise once every 8 hours. Drive the
hour, minute and seconds hands from it. There is no escapement.

`SPEC_WATCH.md` gives the file format, the supplied barrel, the size limit and
every mechanical test with its numbers.

Write your parts and `movement.json` into `work/`, then run the `submit` tool.
Only the last accepted submission is graded, by a separate program.

Write the parts in code: Python 3 with `manifold3d`, `trimesh`, `numpy` and
`scipy` is installed. The tools are a command line:

    python3 tools/tools_watch.py --help

They return measurements only. You have about 60 minutes. Submit early and
resubmit whenever your movement improves.
