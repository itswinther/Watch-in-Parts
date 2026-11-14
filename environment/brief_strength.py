"""Gear strength (check `strength`, one-job mode; SESSION.md Decisions 2026-11-14 17:56, option 2): the texts the
brief generator (environment/make_brief_job.py, builder D) includes, all generated from geometry/watch.py.
    ds_w04()               the text of datasheets/DS-W04_gear_rating.md (Lewis form factors, 25 deg full depth)
    qa_strength_section()  the strength check as an inspection step of QA-W100; cites every supplier value to its cell
    format_material_text() the "material" field of a mobile, for the file-format sheet
    trace_rows()           traceability rows (constant, value, sheet, row, column), never for the agent's folder
    check(folder)          the DS-101 and DS-201 cells against the constants, and DS-W04 against LEWIS_Y
    python3 environment/brief_strength.py [DATASHEETS_FOLDER]   runs check() and prints the rows
The QA text states the load case, the formulas and the units but no value that lives in a supplier sheet."""
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
from geometry import watch as W   # noqa: E402

DS_W04 = ("DS-W04_gear_rating.md", "DS-W04", "Gear tooth rating, rating sheet")   # (file, document, title) for INDEX.md
REVISION, DATE = "A", "2026-11-14"
COLS = 10


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


def format_material_text():
    """The `material` field of a mobile, for the file-format sheet (FORMAT.md, mobiles)."""
    return ("`material`: the material of the mobile, as the ordering code of DS-201 (section 2), for example the "
            "code of a brass or of a steel. Every part of a mobile is of its material. The code must be one that "
            "has a design allowable in DS-201 section 8 for bending (that is, a tensile or yield-based allowable); "
            "any other value, or a mobile without `material`, makes the file not valid.")


def qa_strength_section(title="Gear strength", mesh_test="the mesh test"):
    """The strength check as an inspection step (markdown, no number: the generator places and numbers it).
    mesh_test: how the procedure names the mesh test whose steps, H and m this step reuses."""
    return """**{title}.** The gears of the going train are strong enough in tooth bending.

*Load case.* The barrel delivers the highest torque the mainspring sheet states for this calibre class:
T_barrel = the upper end of the bridle slipping torque, DS-101, Table 2a, row "Slipping torque of the bridle",
column for this series (N·mm). The going train is stalled at its end, so each of its meshes carries the full
torque that reaches it.

*Meshes rated.* The going train: the declared meshes on the path from the barrel to the mobile that carries the
seconds hand, through declared meshes that pass {mt}. The motion work and any other mesh off that path are not
rated. If the seconds hand's mobile is not reached from the barrel that way, this check fails. For each rated
mesh, with D the mobile the declaration names as `driver`, N the one it names as `driven`, and z_D and z_N their
declared tooth counts:

- torque at D: T_D = T_barrel x |n_barrel / n_D| (N·mm), with n the turns per hour that the declared tooth counts
  give through meshes that pass {mt} (the same speeds as the hand checks);
- module: m = 2 x (distance between the two axes in the assembled positions) / (z_D + z_N) (mm), as in {mt};
- tooth load: F = T_D / (m x z_D / 2) (N), on the pitch circle of D;
- face width: b = the smallest H over the drive steps of {mt} for this mesh (mm): H is the height in z of the
  region that the further-turned D shares with N at that step;
- bending stress of each of the two gears, each with its own tooth count z (z_D or z_N):
  sigma = F / (b x m x Y(z)) (MPa = N/mm2), Y(z) the Lewis form factor of DS-W04, section 3, for z teeth.

*Allowable.* A gear's allowable stress is that of its mobile's `material`: the lowest design allowable that
DS-201 section 8 gives for that ordering code (a code with several rows, for example by stock thickness, is
rated at the lowest of them, since the delivery does not state stock thickness). Tooth bending puts the root in
tension, so only a bending (tensile, yield-based) allowable applies; a row that gives a compressive allowable
does not, and a code without a bending allowable in section 8 cannot be declared (C1).

*Pass.* sigma <= the allowable for both gears of every mesh rated. The supplied barrel's own teeth are not rated
here (the barrel is a supplied part, rated by its maker); in a mesh with the barrel only the other gear is rated.
""".format(title=title, mt=mesh_test)


def trace_rows():
    """(constant, value, document, row, column) for every graded number of the strength check."""
    rows = [("BARREL_TORQUE_MAX_NMM", W.BARREL_TORQUE_MAX_NMM, "DS-101", "Table 2a, Slipping torque of the bridle",
             "This series (N·mm), upper end")]
    for cell, code, mpa, kind in W.DS201_ALLOWABLE_ROWS:
        used = kind == "tensile" and W.MATERIAL_ALLOWABLE_MPA.get(code) == mpa
        rows.append(("MATERIAL_ALLOWABLE_MPA[%s]" % code if used else "DS201_ALLOWABLE_ROWS (%s, not used: %s)" % (
            code, "compressive" if kind != "tensile" else "not the lowest row of its code"), mpa, "DS-201",
            "section 8, %s" % cell, "Allowable (MPa)"))
    rows.append(("MATERIAL_ALLOWABLE_MPA keys", sorted(W.MATERIAL_ALLOWABLE_MPA), "DS-201", "section 2", "Code"))
    rows.append(("LEWIS_Y[z], z = %d..%d" % (W.MIN_TEETH, W.MAX_TEETH), "geometry/data/lewis_y.json", "DS-W04",
                 "section 3, row of the tens", "column of the units"))
    rows.append(("PRESSURE_ANGLE (tooth form of Y)", W.PRESSURE_ANGLE, "DS-W04", "section 2", "Pressure angle"))
    rows.append(("LEWIS_ADDENDUM, LEWIS_DEDENDUM", (W.LEWIS_ADDENDUM, W.LEWIS_DEDENDUM), "DS-W04", "section 2",
                 "Addendum, Dedendum of the basic rack"))
    rows.append(("rack_tip_radius()", round(W.rack_tip_radius(), 3), "DS-W04", "section 2", "Tip radius of the basic rack"))
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
    """Every strength value against its one cell: DS-101 and DS-201 (A's sheets, or the copies in folder) against
    the constants, and DS-W04 as generated against LEWIS_Y. Raises SystemExit listing every difference."""
    bad = list(W.check_strength_sheets(folder))
    printed = parse_w04(ds_w04())
    if printed != W.LEWIS_Y:
        diff = sorted(z for z in set(printed) | set(W.LEWIS_Y) if printed.get(z) != W.LEWIS_Y.get(z))
        bad.append("DS-W04 table differs from LEWIS_Y at %d tooth counts, first %s" % (len(diff), diff[:5]))
    qa = qa_strength_section()
    for name, val in (("BARREL_TORQUE_MAX_NMM", W.BARREL_TORQUE_MAX_NMM),) + tuple(
            ("allowable %s" % c, v) for c, v in W.MATERIAL_ALLOWABLE_MPA.items()):
        if re.search(r"(?<![\d.])%s(?![\d])" % re.escape(_num(val)), qa):
            bad.append("the QA text states %s (%s), a supplier value; cite its cell instead" % (name, _num(val)))
    if bad:
        raise SystemExit("strength sheets: " + "; ".join(bad))
    return len(trace_rows())


if __name__ == "__main__":
    n = check(sys.argv[1] if len(sys.argv) > 1 else None)
    for r in trace_rows():
        print(r)
    print("strength sheets ok:", n, "traceability rows")
