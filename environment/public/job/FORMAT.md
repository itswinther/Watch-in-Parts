# File formats of the delivery

Units: millimetres (mm). Every file below is in `/app/delivery/`.

## Folder

```
/app/delivery/
  movement.json        the 8-hour build
  variant_6h.json      the 6-hour variant
  assembly.json        the assembly plan of movement.json
  parts/<name>.step    one STEP file per part, for both movements
  scripts/             optional, at most 200 files and 4,194,304 bytes in all; never run or read
  report.json          optional: the designer's statement of each inspection part's result
```

Of `parts/`, only the files that `movement.json` and `variant_6h.json` name are opened. Every file that is
opened, and the `parts/` folder, must be a real file or folder inside `/app/delivery/`: a symbolic link, or a
file outside the folder, is a format error.

## Names

Part and mobile names use letters, digits, `_` and `-`, 1 to 40 characters. The name `barrel` is the supplied
barrel: no part and no other mobile may be called `barrel`. Part `<name>` is the file `parts/<name>.step`; a part
named in both movement files is that one file. STL part files are not accepted.

## Part files (STEP)

Each part file holds one part in its assembled position. It becomes the solid that every test uses like this:

- The file is at most 16,777,216 bytes. Its length unit is millimetre; a file in any other unit (inch, metre, ...) is
  rejected, not converted. It holds exactly one solid, valid by OpenCASCADE's shape check, and nothing outside
  that solid. A file whose solid has more than 500 flat faces with exactly three edges is rejected (only such
  triangular faces are counted). Reading and meshing one file may take at most 120 s and, where the operating
  system supports such a limit, 4,096 MB of memory (it runs in its own process).
- The solid is meshed with OpenCASCADE (`BRepMesh_IncrementalMesh`) with a linear deflection of 0.001 mm
  (absolute) and an angular deflection of 0.1 radians. A meshed curved surface lies within 0.001 mm of the true
  one (inside a convex surface, outside a concave one, such as a hole).
- The mesh has at most 200,000 triangles; its triangles, with identical vertices joined, form a single closed
  manifold shell with positive volume, and its volume changes by at most 0.5% when the solid is united with
  itself.

## `movement.json` and `variant_6h.json`

Each is at most 1,048,576 bytes and names at most 60 parts.

```
{
  "case_centre": [x, y],
  "fixed": ["part_name", ...],
  "mobiles": {
    "mobile_name": {"axis": [x, y], "parts": ["part_name", ...], "material": "ordering code",
                     "part_materials": {"part_name": "ordering code"}},
    ...
  },
  "meshes": [
    {"driver": "barrel", "driver_teeth": n, "driven": "mobile_name", "driven_teeth": n},
    ...
  ],
  "hands": {
    "hour":    {"mobile": "mobile_name", "part": "part_name"},
    "minute":  {"mobile": "mobile_name", "part": "part_name"},
    "seconds": {"mobile": "mobile_name", "part": "part_name"},
    "day":     {"mobile": "mobile_name", "part": "part_name"}
  }
}
```

- `case_centre`: x and y of the case's axis, in mm.
- `fixed`: the parts that do not move. A non-empty list.
- `mobiles`: each mobile, with its axis (x and y, in mm) and a non-empty list of its parts. `barrel` is not listed;
  it exists already.
- `material`: in each mobile, its material, as an ordering code of DS-201 (its table of ordering codes). Every
  part of a mobile is of its material, except a part named in `part_materials`. The code must be one that has a
  design allowable for bending (a tensile, yield-based allowable) in DS-201's table of design allowables; any
  other value, or a mobile without `material`, makes the file not valid.
- `part_materials` (optional): in a mobile, an object `{"part name": "ordering code"}` that gives some of its
  parts another material than the mobile's `material`, for example a brass wheel on a steel pinion. Each key must
  be a part listed in that mobile's `parts`, and each code must qualify as for `material`; anything else makes the
  file not valid. A part not named here is of the mobile's `material`.
- `meshes`: every pair of gears that drive one another: the two mobiles (`barrel` or a mobile name), and the tooth
  count of the gear on each (each `n` above stands for one). Tooth counts are integers from 3 to 1000.
- `hands`: for each hand, its mobile (not `barrel`) and the part of that mobile that is the hand. `day` is the
  24-hour hand. `hour`, `minute` and `seconds` are required; `day` may be left out.
  Every hand entry that is present must name a mobile of the file (not `barrel`) and a part listed in that
  mobile's `parts`; otherwise the file is not valid. A `day` entry that is left out, or that is `null`, counts
  as no 24-hour hand.
- In one file a part is named only once (under `fixed` or in one mobile).

## `assembly.json`

At most 67,108,864 bytes.

```
{"order": ["part_name", ...], "paths": {"part_name": [P, P, ...], ...}}
```

`order` lists the part names of `movement.json`, and `barrel`, in the order they are put in. Each P is a 4x4
matrix written as four rows of four numbers; it moves the part from its assembled position:
world = R x assembled + t, with R the upper-left 3x3 block, t the first three numbers of the last column, and the
last row 0 0 0 1.

## `report.json` (optional)

At most 100,000 bytes.

```
{"parts": {"P1": "pass", "P2": "fail", "P3": "not_tested", "P4": "pass"}, "height_mm": 10.4}
```

- `parts`: one key per part of QA-W100 (`P1` for Part 1, and so on for each part), each with the statement of that
  part's result: one of `pass`, `fail`, `not_tested`. A part left out counts as `not_tested`. Other keys at the
  top level are ignored.
- `report.json` must be a real file in `/app/delivery/` (not a symbolic link). One that is larger than the limit,
  is not valid JSON, has no object `parts`, names a key that is not a part of QA-W100 or gives any other value is
  not valid: every part then counts as `not_tested`. How the statement is scored: QA-W100, section 3.
- `height_mm` (optional): your statement of the movement's height as QA-W100, section 9 measures it, in mm. It
  does not change any result; the inspection records it next to the measured height.
