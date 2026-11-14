# Task

Design a 3D-printable enclosure for the circuit board assembly described in
`SPEC_PUBLIC.md`, and state how it is assembled.

Produce three files in `work/`: `base.stl`, `door.stl` and `assembly.json`. Then
run the `submit` tool. Only the last accepted submission is graded, by a separate
program that applies exactly the requirements in `SPEC_PUBLIC.md`.

Write the parts in code (Python with `manifold3d`, `trimesh`, `numpy`, `scipy` is
installed). The supplied bodies are in `meshes/` as STL files and are described
numerically in the spec.

The tools are a command line:

    python3 tools/tools_cli.py --help

They return measurements only. Use them to check your own work against the
numbers in the spec before you submit. Submit early and resubmit when you improve.
