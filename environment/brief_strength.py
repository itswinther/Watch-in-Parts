"""Gear strength (check `strength`, one-job mode; SESSION.md Decisions 2026-11-14 17:56, option 2, and the
orchestrator's answers to builder S): the texts the brief generator includes, all generated from geometry/watch.py.
The interface is the hook strength_module() of environment/make_brief_job.py (builder D):
    ds_w04()               the text of datasheets/DS-W04_gear_rating.md (Lewis form factors, 25 deg full depth)
    qa_strength_section()  check 14 of QA-W100 Part 1 ("14. **..."), citing every supplier value to its cell
    format_text()          the `material` bullet of FORMAT.md's movement.json section
    trace_rows()           home cells of the strength constants, in the row format of make_brief_job.cell()
    check()                [error]: DS-101 and DS-201 cells against the constants, DS-W04 against LEWIS_Y, and no
                           supplier value in the QA text (empty when consistent)
    DS_W04_FILE, DS_W04_TITLE
    python3 environment/brief_strength.py [DATASHEETS_FOLDER]   runs check() and prints the rows
The QA text states the load case, the formulas and the units but no value that lives in a supplier sheet."""
import os
import re
import sys
import textwrap

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from geometry import watch as W   # noqa: E402

DS_W04_FILE, DS_W04_TITLE = "DS-W04_gear_rating.md", "Gear tooth rating, rating sheet"
DS101_FILE, DS201_FILE = "datasheets/" + W.STRENGTH_SHEETS["DS-101"], "datasheets/" + W.STRENGTH_SHEETS["DS-201"]
W04 = "datasheets/" + DS_W04_FILE
REVISION, DATE = "A", "2026-11-14"
COLS = 10
WIDTH = 114


def _num(x):
    s = ("%.6f" % x).rstrip("0").rstrip(".")
    return s if s != "-0" else "0"


def _head(doc, title, issuer, kind):
    return """# {title}

| Document | Revision | Date | Status |
|---|---|---|---|
| {doc} | {rev} | {date} | Released |

**Issued by:** {issuer}. **Document type:** {kind}.
""".format(doc=doc, title=title, rev=REVISION, date=DATE, issuer=issuer, kind=kind)


def _y_table():
    lo, hi = W.MIN_TEETH, W.MAX_TEETH
    head = "| Teeth | " + " | ".join("+%d" % k for k in range(COLS)) + " |\n|---|" + "---|" * COLS + "\n"
    rows = []
    for base in range(lo - lo % COLS, hi + 1, COLS):
        cells = []
        for z in range(base, base + COLS):
            cells.append("%.*f" % (W.LEWIS_DECIMALS, W.LEWIS_Y[z]) if lo <= z <= hi else "–")
        rows.append("| %d | %s |\n" % (base, " | ".join(cells)))
    return head + "".join(rows)


def ds_w04():
    """The gear rating sheet: Lewis form factors for full-depth involute spur teeth at the barrel's pressure angle,
    every tooth count the movement format accepts, generated from W.LEWIS_Y; the method and its source."""
    a = _num(W.PRESSURE_ANGLE)
    return _head("DS-W04", "Gear tooth rating: Lewis form factors", "the gear design office", "rating sheet") + """
## 1. Scope

Bending strength of spur gear teeth by the Lewis formula. For a gear of z teeth and module m (mm), with face
width b (mm), carrying a tangential load W_t (N) on its pitch circle, the bending stress at the root of a tooth is

    sigma = W_t / (b x m x Y(z))      (MPa = N/mm2)

where Y(z) is the Lewis form factor of section 3. Y has no unit and does not depend on the module.

## 2. Tooth form and method

| Quantity | Value |
|---|---|
| Pressure angle | {a} degrees |
| Tooth system | full-depth involute, cut by the basic rack without profile shift |
| Addendum of the basic rack | {ha} x m |
| Dedendum of the basic rack | {hf} x m |
| Tip radius of the basic rack | {rho} x m |
| Load position | at the tip of one tooth |

**Tooth form.** Each tooth is the one the basic rack generates: the rack's straight flank cuts the involute and
its tip round cuts the root fillet (undercut included, for small tooth counts). The rack's tip radius follows
the rule of ISO 53 (0.38 x m at 20 degrees): the radius at which the rack's straight flank ends at the depth of
the addendum, (dedendum - addendum) / (1 - sin a). At {a} degrees that radius does not fit on the rack tooth's
tip, so the tip is a full round, of radius half the rack's tip width x tan(45 degrees + a / 2): the value in the
table above.

**Method (Lewis).** The tooth is a cantilever. The tangential load W_t acts at the tip, on the tooth's centre line
at the tip circle (at its point, for a tooth pointed below the tip circle). The weakest section is where the
parabola of constant strength, with its vertex at the load point, is tangent to the root fillet. At that section,
with t the tooth thickness and l the distance along the centre line from the load point,
sigma = 6 x W_t x l / (b x t^2), so Y = t^2 / (6 x l x m), taken at the fillet point where it is smallest. The
radial component of the tooth load is neglected, as in Lewis. Values are computed on the generated tooth and
rounded to {d} decimals.

**Sources.** W. Lewis, "Investigation of the strength of gear teeth", Proceedings of the Engineers' Club of
Philadelphia, 1892 (the method); R. G. Budynas and J. K. Nisbett, *Shigley's Mechanical Engineering Design*,
section 14-1, "The Lewis bending equation" (the cantilever, the parabola and Y = 2 x P / 3, in module form
Y = 2 x / (3 m) with x = t^2 / (4 l)); ISO 53, "Cylindrical gears for general and heavy engineering: standard
basic rack tooth profile" (addendum 1.0 m, dedendum 1.25 m, the rack tip radius rule). The values below are
computed by this office for the {a}-degree tooth form; they are not copied from a published table.

## 3. Lewis form factor Y, {a}-degree full-depth involute, load at the tip

Read the row of the tens and the column of the units: for 47 teeth, row 40, column +7.

{table}""".format(a=a, ha=_num(W.LEWIS_ADDENDUM), hf=_num(W.LEWIS_DEDENDUM), rho="%.3f" % W.rack_tip_radius(),
                  d=W.LEWIS_DECIMALS, table=_y_table())


def _fill(text, first, rest):
    return textwrap.fill(text, WIDTH, initial_indent=first, subsequent_indent=rest, break_on_hyphens=False,
                         break_long_words=False)


def format_text():
    """The `material` bullet of FORMAT.md's movement.json section (after the `mobiles` bullet)."""
    return _fill("`material`: in each mobile, its material, as an ordering code of DS-201 (its table of ordering "
                 "codes). Every part of a mobile is of its material. The code must be one that has a design "
                 "allowable for bending (a tensile, yield-based allowable) in DS-201's table of design allowables; "
                 "any other value, or a mobile without `material`, makes the file not valid.", "- ", "  ") + "\n"


def qa_strength_section(number=14, mesh_test="the mesh test (check 4)"):
    """Check `number` of QA-W100 Part 1 ("14. **Gear strength.** ..."), a markdown list item whose paragraphs are
    indented to the item. mesh_test: how the procedure names the mesh test whose steps, H and m this check reuses."""
    ind = " " * (len(str(number)) + 2)
    paras = [
        "**Gear strength.** The gears of the going train are strong enough in tooth bending.",
        "*Load case.* This calibre is the base of a family that includes an automatic version, whose barrel has a "
        "slipping bridle; the going train is rated for that version's barrel load. T_barrel is the upper end of the "
        "bridle's slipping torque, DS-101, Table 2a, row \"Slipping torque of the bridle (min. to max.)\", column "
        "for this series (N·mm), whatever mainspring the barrel of this build holds. The going train is stalled at "
        "its end, so each of its meshes carries the full torque that reaches it.",
        "*Meshes rated.* The going train: the declared meshes on the path from the barrel to the mobile that "
        "carries the seconds hand, through declared meshes that pass %s; where there is more than one such path, "
        "the one a breadth-first search from the barrel finds first when it takes the meshes in their declared "
        "order (so the one with the fewest meshes). The motion work, and any other mesh off "
        "that path, is not rated. If the seconds hand's mobile is not reached from the barrel that way, this check "
        "fails. For each rated mesh, with D the mobile that the declaration names as `driver`, N the one it names "
        "as `driven`, and z_D and z_N their declared tooth counts:" % mesh_test,
    ]
    bullets = [
        "torque at D: T_D = T_barrel x |n_barrel / n_D| (N·mm), with n the turns per hour that the declared tooth "
        "counts give through meshes that pass the mesh test (the same speeds as the hand checks);",
        "module: m = 2 x (distance between the two axes in the assembled positions) / (z_D + z_N) (mm), as in the "
        "mesh test;",
        "tooth load: F = T_D / (m x z_D / 2) (N), on the pitch circle of D;",
        "face width: b = the smallest H over the drive steps of the mesh test for this mesh (mm), H being the "
        "height in z of the region that the further-turned D shares with N and did not occupy before;",
        "bending stress of each of the two gears, each with its own tooth count z (z_D or z_N): "
        "sigma = F / (b x m x Y(z)) (MPa, that is N/mm2), Y(z) the Lewis form factor of DS-W04, section 3, for "
        "z teeth.",
    ]
    tail = [
        "*Allowable.* A gear's allowable stress is that of its mobile's `material`: the lowest design allowable "
        "that DS-201 section 8 gives for that ordering code (a code with several rows, for example by stock "
        "thickness, is rated at the lowest of them, since the delivery does not state stock thickness). Tooth "
        "bending puts the root of the tooth in tension, so only a bending (tensile, yield-based) allowable applies: "
        "a row that gives a compressive allowable does not, and a code without a bending allowable in section 8 "
        "cannot be declared (C1).",
        "*Pass.* sigma <= the allowable for both gears of every rated mesh. The supplied barrel's own teeth are not "
        "rated here (the barrel is a supplied part, rated by its maker): in a mesh with the barrel only the other "
        "gear is rated.",
    ]
    out = [_fill(paras[0], "%d. " % number, ind)]
    out += [_fill(p, ind, ind) for p in paras[1:]]
    out.append("\n".join(_fill(b, ind + "- ", ind + "  ") for b in bullets))
    out += [_fill(p, ind, ind) for p in tail]
    return "\n\n".join(out) + "\n"


def _cell(constant, value, file, section, row=None, column=None, tokens=(), pick="all", text=None, has=None):
    """A row in the format of environment/make_brief_job.cell()."""
    return {"constant": constant, "value": value, "file": file, "section": section, "row": row, "column": column,
            "tokens": [str(t) for t in tokens], "pick": pick, "text": text, "has": has}


def trace_rows():
    """Home cells of every graded number of the strength check (agent-folder paths; make_brief_job checks them)."""
    rows = [_cell("BARREL_TORQUE_MAX_NMM (strength load case; the upper end of the cell)", W.BARREL_TORQUE_MAX_NMM,
                  DS101_FILE, "4a. Reference specification of a real 11½‴ calibre (Table 2a, maker's limits)", "Slipping torque of the bridle (min. to max.)", "This series",
                  [_num(W.BARREL_TORQUE_MAX_NMM)], pick="max")]
    for i, (cell, code, mpa, kind) in enumerate(W.DS201_ALLOWABLE_ROWS):
        if kind != "tensile":
            what = "DS201_ALLOWABLE_ROWS[%d] (%s: compressive, not accepted for a mobile)" % (i, code)
        elif W.MATERIAL_ALLOWABLE_MPA[code] == mpa:
            what = "MATERIAL_ALLOWABLE_MPA[%s] (the lowest row of its code)" % code
        else:
            what = "DS201_ALLOWABLE_ROWS[%d] (%s: not the lowest row of its code, not used)" % (i, code)
        rows.append(_cell(what, mpa, DS201_FILE, "8. Safety factors", cell, "Allowable", [_num(mpa)]))
    for code in W.MATERIAL_DESIGNATIONS:
        rows.append(_cell("MATERIAL_DESIGNATIONS: %s (ordering code)" % code, code, DS201_FILE, "2. Ordering codes",
                          code, "Code", (), text=code))
    rows += [
        _cell("PRESSURE_ANGLE (tooth form of the Lewis form factors)", W.PRESSURE_ANGLE, W04, "2. Tooth form",
              "Pressure angle", "Value", [_num(W.PRESSURE_ANGLE)]),
        _cell("LEWIS_ADDENDUM", W.LEWIS_ADDENDUM, W04, "2. Tooth form", "Addendum of the basic rack", "Value",
              [_num(W.LEWIS_ADDENDUM)]),
        _cell("LEWIS_DEDENDUM", W.LEWIS_DEDENDUM, W04, "2. Tooth form", "Dedendum of the basic rack", "Value",
              [_num(W.LEWIS_DEDENDUM)]),
        _cell("rack_tip_radius() (rounded to 3 decimals)", round(W.rack_tip_radius(), 3), W04, "2. Tooth form",
              "Tip radius of the basic rack", "Value", ["%.3f" % W.rack_tip_radius()]),
    ]
    for base in range(W.MIN_TEETH - W.MIN_TEETH % COLS, W.MAX_TEETH + 1, COLS):
        for k in range(COLS):
            z = base + k
            if W.MIN_TEETH <= z <= W.MAX_TEETH:
                rows.append(_cell("LEWIS_Y[%d] (geometry/data/lewis_y.json)" % z, W.LEWIS_Y[z], W04, "3. Lewis form factor",
                                  str(base), "+%d" % k, ["%.*f" % (W.LEWIS_DECIMALS, W.LEWIS_Y[z])]))
    return rows


def parse_w04(text):
    """teeth -> Y as printed in DS-W04 section 3."""
    out = {}
    sec = text.split("## 3.", 1)[1]
    for line in sec.splitlines():
        m = re.match(r"^\|\s*(\d+)\s*\|(.*)\|\s*$", line)
        if not m:
            continue
        base = int(m.group(1))
        for k, c in enumerate(x.strip() for x in m.group(2).split("|")):
            if c not in ("–", ""):
                out[base + k] = float(c)
    return out


def check(folder=None):
    """[error] (empty when consistent): DS-101 and DS-201 (A's sheets, or the copies in folder) against the
    constants, DS-W04 as generated against LEWIS_Y, and no supplier value (torque, allowable, Y) in the QA text."""
    bad = list(W.check_strength_sheets(folder))
    printed = parse_w04(ds_w04())
    if printed != W.LEWIS_Y:
        diff = sorted(z for z in set(printed) | set(W.LEWIS_Y) if printed.get(z) != W.LEWIS_Y.get(z))
        bad.append("DS-W04 table differs from LEWIS_Y at %d tooth counts, first %s" % (len(diff), diff[:5]))
    qa = qa_strength_section() + format_text()
    vals = [("BARREL_TORQUE_MAX_NMM", W.BARREL_TORQUE_MAX_NMM)] + \
        [("allowable of %s" % c, v) for _, c, v, _ in W.DS201_ALLOWABLE_ROWS] + \
        [("rack tip radius", round(W.rack_tip_radius(), 3))]
    for name, val in vals:
        if re.search(r"(?<![\d.])%s(?![\d])" % re.escape(_num(val)), qa):
            bad.append("the QA or format text states %s (%s), a supplier value; cite its cell instead" % (name, _num(val)))
    if re.search(r"\b0\.\d{4}\b", qa):
        bad.append("the QA or format text holds a 4-decimal number (a Lewis form factor?)")
    if not qa_strength_section().startswith("14. **"):
        bad.append("qa_strength_section() must start with '14. **'")
    return bad


if __name__ == "__main__":
    errors = check(sys.argv[1] if len(sys.argv) > 1 else None)
    rows = trace_rows()
    for r in rows[:16]:
        print(r)
    print("... %d rows in all" % len(rows))
    print("\n".join(errors) if errors else "strength sheets ok")
    sys.exit(1 if errors else 0)
