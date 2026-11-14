# Task

Design the enclosure for an activity tracker worn on the wrist by children aged 6 to 10.

The parts that go inside are listed in `parts.json` (millimetres, grams). You decide how
they are arranged.

Write the printed parts as STL files in `out/`, in their assembled position, and write
`out/layout.json` giving where each supplied part sits: for each part id, the min corner
`[x, y, z]` and the size `[dx, dy, dz]` of its box in the same coordinates as the STL files.

Python with CadQuery, trimesh, manifold3d and numpy is at:

    /Users/mikbs/Desktop/dev/Junction/.venv/bin/python

Your design will be judged on whether it is a sensible product for that user.
