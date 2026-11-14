# Task

Design the smallest 3D-printable enclosure for the four bodies described in
`SPEC_H2.md`, and state how it is assembled. You decide where each body sits, the
order they go in and the path each one takes.

Produce three files in `work/`: `base.stl`, `lid.stl` and `assembly.json`. Then
run the `submit` tool. Only the last accepted submission is graded, by a separate
program that applies exactly the requirements and the score formula in
`SPEC_H2.md`.

Your score rises as the bounding box of your enclosure shrinks, down to a volume
that is known to be achievable. A valid large design is a start, not the goal.

Write the parts in code (Python with `manifold3d`, `trimesh`, `numpy`, `scipy` is
installed). The supplied bodies are in `meshes/` as STL files, each in its own
frame, and are described numerically in the spec.

The tools are a command line:

    python3 tools/tools_h2.py --help

They return measurements only. Use them to check your own work against the
numbers in the spec. Submit early and resubmit whenever you improve.
