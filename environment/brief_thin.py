"""The thinness probe's brief (spikes/thin_probe/BRIEF_DRAFT.md; SESSION.md Proposed spec changes, 2026-11-15 02:20).
Included by environment/make_brief_job.py when THIN_IN_BRIEF is True. With the switch off, make_brief_job.py writes
main's brief unchanged and nothing here is used.

What the switch changes (all in the agent-facing documents; tests/grade_watch.py is unchanged):
  - QA-W100 becomes rev B: section 3 opens with how the delivery is inspected and what "collide" means, and ends with
    the optional `height_mm`; section 4's computing-time bullet loses its step detail; Part 1 states requirements
    only (every number kept, restated as a requirement; no sampling, step counts or turning senses of the rig);
    a new section 9 states the thickness target (geometry/watch.py THIN_TARGET_MM) and the score formula.
  - The work order gets a Thickness row, a longer report.json row and one acceptance sentence.
  - FORMAT.md's report.json section gets the optional top-level key `height_mm`.
The probe's reward is computed afterwards by spikes/thin_probe/score.py from the grader's details file."""
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from geometry import watch as W        # noqa: E402

THIN_IN_BRIEF = True       # the probe branch (b/thin-probe) turns this on; False gives main's brief unchanged

QA_REVISION = "B"
QA_DATE = "2026-11-15"
SECTION = "9"              # QA-W100's thickness section (after Part 4, section 8)
SECTION_TITLE = "Thickness"
HEIGHT_KEY = "height_mm"
HEIGHT_EXAMPLE = 10.4      # FORMAT.md's example value only
CASE_HEIGHT_COL = "Inner height along the axis (mm)"

# Trace rows of main's QA-W100 that are test method, not requirement: the probe's QA-W100 does not state them.
NOT_STATED = ("SPIN_STEPS (and the step, 360 / SPIN_STEPS degrees)",
              "SPIN_OFFGRID (and the positions, SPIN_STEPS x (1 + its length))",
              "SAMPLES_PER_TOOTH, MESH_OFFGRID, every 4th and 8th step",
              "TEETH_RAYS (mesh test, teeth as declared: directions of a section's outline)")
# Rows whose statement anchor moves in the probe's Part 1: {constant: new anchor}
ANCHORS = {"ENGAGE_GAP": "**The train runs.**",
           "DRIVE_FRACTION (and 360 x DRIVE_FRACTION degrees)": "**The train runs.**",
           "DRIVE_MIN_VOLUME": "**The train runs.**",
           "DRIVE_AREA_RATIO": "**The train runs.**",
           "TEETH_MIN_DEPTH (mesh test, teeth as declared; the barrel's count is BARREL_TEETH, cited from DS-W01)":
               "**The train runs.**",
           "MESH_SHIFT": "**Runs with its arbors"}


def target_text():
    return "%.1f" % W.THIN_TARGET_MM


def share_text():
    s = W.THIN_SCORE_SHARE
    return "%d/%d" % (s.numerator, s.denominator)


def check():
    errs = []
    if not (0 < W.THIN_TARGET_MM < W.CASE_HEIGHT):
        errs.append("THIN_TARGET_MM must lie between 0 and CASE_HEIGHT")
    if float(target_text()) != W.THIN_TARGET_MM:
        errs.append("THIN_TARGET_MM is not printed exactly to one decimal")
    if W.THIN_SCORE_SHARE * 2 != 1:
        errs.append("THIN_SCORE_SHARE is not 1/2 (the grader's parts reward is 1/2 share + 1/2 [all pass])")
    return errs


# ------------------------------------------------------------------ QA-W100
def qa_section3_lead(B):
    p1 = ("**How the delivery is inspected.** The quality department inspects the delivery after hand-over with its "
          "own test rig. This procedure states what must hold. It does not describe how the rig turns, moves or "
          "samples the parts. Each requirement is met or not met, and is judged on its own. Where this procedure "
          "says check, it means requirement.")
    p2 = ("**Collide.** Two solids collide when their intersection is larger than %s. A smaller intersection is "
          "modelling noise and counts as no contact. \"Is stopped by\" means \"collides with\"." % B.vt())
    return B.wrap(p1) + "\n\n" + B.wrap(p2) + "\n\n"


def qa_section3_tail(B):
    return "\n" + B.wrap("The statement may also give the movement's height (`%s`, `/app/FORMAT.md`). It is recorded "
                         "and does not change any result." % HEIGHT_KEY) + "\n"


def computing_time(B, tout, jtout):
    return B.wrap("- **Computing time.** Each condition and each requirement has up to %d s of rig time, and the whole "
                  "inspection up to %d s; a condition or requirement that runs out of time, or that would start after "
                  "the whole inspection's time has run out, is not met." % (tout, jtout), "  ")


def part1(B, L, S=None):
    """Part 1 as requirements only (BRIEF_DRAFT.md section 3). Requirements 12 to 14 are rev A's text."""
    strength = ""
    if S is not None:
        strength = S.qa_strength_section().rstrip("\n") + "\n"
        if not strength.startswith("14. **"):
            raise SystemExit("brief_strength.qa_strength_section() must start with '14. **' (check 14 of Part 1)")
    n = B.num
    return """## 5. Part 1: going train and hands (`movement.json`)

The 8-hour build: the barrel runs at the speed class that the work order gives for the 8-hour build
({speed}).

Conditions. If one fails, Part 1 fails and none of its requirements is met.

- **C1 Files.** `movement.json` and every part file it names are valid as `/app/FORMAT.md` describes. A hand
  entry that is present and does not name a mobile of the file and one of that mobile's parts makes the file not
  valid; `hour`, `minute` and `seconds` must be present.
- **C2 Assembled.** In the assembled positions, taking the frame as one solid and each mobile (the barrel
  included) as one solid, no two of these solids collide; no two fixed parts collide; no two parts of one mobile
  collide. The fixed parts form one frame: every fixed part is linked to every other through a chain of fixed
  parts, each within {join} mm of the next.

Requirements.

1. **Free to turn.** Each mobile, the barrel included, turns through a full turn about its axis without colliding
   with the frame at any angle.
2. **Held.** No mobile, the barrel included, can move {hm} mm on its own along +x, -x, +y, -y, +z or -z. Moved that
   far in any of these directions, with everything else in place, it is stopped by the frame, or by a mobile whose
   axis is within {coax} mm of its own and which is itself held in that direction. A mobile on another axis never
   holds it.
3. **Seated.** Every part of a mobile that has more than one part is fixed in its mobile. Moved {hm} mm along +x,
   -x, +y or -y, it is stopped by the other parts of its mobile, and moved {hm} mm along +z or along -z (at least
   one of the two) it is stopped too. The parts of each such mobile form one piece, each within {touch} mm of the
   next. The barrel and one-part mobiles are exempt.
4. **The train runs.** At least one mesh is declared. No mobile gets two different speeds from the declared
   meshes, and every mobile is driven from the barrel through declared meshes that drive. Every declared mesh
   drives. A declared mesh, D its `driver` (z_D teeth) and N its `driven` (z_N teeth), drives when, as D turns N
   at the ratio z_D / z_N through a full turn of the larger gear:
   - the declared tooth counts are right: z_D and z_N are the numbers of teeth of the two gears, counted round
     the section of each at the height where the two gears meet (a tooth is at least {tdepth} mm deep); for
     `barrel`, the count is the one of its catalogue data (DS-W01, section 2);
   - the two never collide;
   - they stay in mesh: wherever they do not touch, they are at most {gap} mm apart;
   - the teeth carry the drive: from every position of that turn, turning D a further {frac} of its tooth pitch
     ({push} / z_D degrees) while N is held makes D cut into N. The region cut into N is at least {dmin} mm3, and
     its volume divided by its height along z is more than {ratio} x m x m, with m = 2 x (distance between the
     two axes) / (z_D + z_N).

   Every declared mesh is external: its two mobiles turn in opposite directions. A mesh that does not drive drives
   nothing. Elsewhere in this procedure, "passes the mesh test" means "drives" in this sense, and the drive steps
   of the mesh test are the positions from which D is turned the further {frac} of its tooth pitch.
5. **Runs with its arbors slightly out of place.** Every declared mesh also drives with N's axis moved {shift} mm
   straight towards D's axis, and with it moved {shift} mm straight away.
6. **Nothing else collides.** No two mobiles (the barrel included) that are not declared as a mesh may meet at any
   pair of angles, whatever their speeds: the swept solids of the two collide by no more than {vt}. The swept
   solid of a mobile is every point that some point of the mobile passes through while it makes one full turn
   about its axis (the mobile turned to every angle at once). Two mobiles on the same axis are treated the same
   way.

   *Swept solid.* It is worked out from horizontal sections of the mobile, all its parts together, in the
   assembled position. The heights at which the mobile has a vertex cut it into height ranges. Inside a range
   that no face crosses that is neither vertical nor horizontal, the section is the same at every height; inside
   any other range, the range is cut into the fewest equal bands no higher than {dz} mm. Each range of the first
   kind, and each band, is given by the section at its middle height: through that whole range or band, the swept
   solid holds every point whose distance from the axis is the distance from the axis of some point of that
   section. The swept solid is therefore a solid of revolution, with exact circles round the axis.
7. **Hour hand.** 8. **Minute hand.** 9. **Seconds hand.** The hands show the time, each turning clockwise at a
   constant speed: the hour hand {hs[hour]}, the minute hand {hs[minute]}, the seconds hand {hs[seconds]}.
   A hand is driven only through declared meshes that pass the mesh test (a declared
   mesh that fails it drives nothing), and no mobile may be given two different speeds by the declared meshes.
10. **Hours and minutes on a common centre.** The axes of the hour hand's mobile and the minute hand's mobile are
    at most {coax} mm apart.
11. **Hands.** Each of the hour, minute and seconds hand parts reaches at least {reach} mm from its mobile's axis;
    lies wholly above the frame (its lowest point is no lower than the highest point of any fixed part); points
    (its centre of volume is at least {hcm} mm from its mobile's axis); and, seen from the dial side, covers at
    most {has} of the area of the disc its tip sweeps.
{fits}
{printable}
{strength}""".format(speed=B.SPEED_CITE, join=n(W.FRAME_JOIN), hm=n(W.HELD_MOVE), coax=n(W.COAX_TOL),
                     touch=n(W.SEAT_TOUCH), gap=n(W.ENGAGE_GAP), frac=n(W.DRIVE_FRACTION),
                     push=n(W.DRIVE_FRACTION * 360), dmin=n(W.DRIVE_MIN_VOLUME), ratio=n(W.DRIVE_AREA_RATIO),
                     shift=n(W.MESH_SHIFT), tdepth=n(W.TEETH_MIN_DEPTH), vt=B.vt(), dz=n(W.SWEEP_DZ),
                     hs=B.hand_speeds(), reach=n(W.HAND_REACH), hcm=n(W.HAND_CENTRE_MIN),
                     has=n(W.HAND_AREA_MAX_SHARE), fits=B.fits_text(), printable=B.printable_req_text(),
                     strength=strength)


def section9(B, L, S=None):
    t = target_text()
    return """## {sec}. {title}

The order asks for a slim calibre. The movement's height H is the highest point minus the lowest point of every
part of the movement and of the barrel, in the assembled positions, along the axis. The taller of `movement.json`
and `variant_6h.json` counts. The target is **{t} mm**.

{cdef}

    x = (H - {t}) / (C - {t}), taken as 0 below 0 and as 1 above 1
    thickness score s = (1 - x) ^ {e}

{fig}
""".format(sec=SECTION, title=SECTION_TITLE, t=t, e=W.THIN_SCORE_EXPONENT,
           cdef=B.wrap("With C the inner height of the case named in the work order (%s):" % B.cite_case(CASE_HEIGHT_COL)),
           fig=B.wrap("The acceptance figure is {h} x (the result of Parts 1 to 4 together) + {h} x [every condition "
                      "and every requirement of Parts 1 to 4 is met] x s, times the statement factor of section 3. A "
                      "movement file that does not load counts as no thickness score (s = 0).".format(h=share_text())))


# ------------------------------------------------------------------ the work order
def order_row():
    return ("| Thickness | the calibre is for a slim watch: make the movement as thin as you can. The thickness target "
            "and how thickness is scored are in QA-W100, section %s |\n" % SECTION)


def deliverable_row(report):
    return ("| `/app/delivery/%s` | optional: your own statement of the result of each part of QA-W100 (`pass`, "
            "`fail` or `not_tested`), and of the movement's height (QA-W100, sections 3 and %s) |\n" % (report, SECTION))


def acceptance_sentence():
    return (" When every part passes everything, the thickness score of QA-W100, section %s, scales the half of the "
            "acceptance figure that full acceptance earns." % SECTION)


# ------------------------------------------------------------------ FORMAT.md
def format_example_key():
    return ', "%s": %s' % (HEIGHT_KEY, HEIGHT_EXAMPLE)


def format_bullet(B):
    return B.wrap("- `%s` (optional): your statement of the movement's height as QA-W100, section %s measures it, in "
                  "mm. It does not change any result; the inspection records it next to the measured height."
                  % (HEIGHT_KEY, SECTION), "  ") + "\n"


# ------------------------------------------------------------------ traceability
def literals():
    """Numbers the probe's documents print without a home cell, with the reason (added to make_brief_job.LITERALS)."""
    return {"instruction.md": {SECTION: "QA-W100's section number (thickness)"},
            "FORMAT.md": {SECTION: "QA-W100's section number (thickness)",
                          str(HEIGHT_EXAMPLE): "an example value of height_mm in the report.json layout"},
            "datasheets/QA-W100_inspection.md": {}}


def trace_rows(B, rows):
    """main's trace rows with the probe's changes: the test-method rows dropped, the moved anchors, and the home
    cells of the thickness section."""
    out = []
    for r in rows:
        if r["constant"] in NOT_STATED:
            continue
        if r["constant"] in ANCHORS and r["file"] == "datasheets/" + B.QA_FILE:
            r = dict(r, row=ANCHORS[r["constant"]])
        out.append(r)
    missing = [c for c in NOT_STATED + tuple(ANCHORS) if c not in {r["constant"] for r in rows}]
    if missing:
        raise SystemExit("brief_thin: make_brief_job.py trace rows renamed: %s" % missing)
    Q, sec = "datasheets/" + B.QA_FILE, "%s. %s" % (SECTION, SECTION_TITLE)
    out += [
        B.cell("THIN_TARGET_MM (thinness probe)", W.THIN_TARGET_MM, Q, sec, "The target is", None, [target_text()]),
        B.cell("THIN_SCORE_EXPONENT (thinness probe)", W.THIN_SCORE_EXPONENT, Q, sec, None, None,
               [W.THIN_SCORE_EXPONENT]),
        B.cell("THIN_SCORE_SHARE (thinness probe; also the grader's parts reward split, Fraction(1, 2))",
               W.THIN_SCORE_SHARE, Q, sec, "The acceptance figure is", None, [share_text()]),
        B.cell("CASE_HEIGHT cited in the thickness formula (no value printed)", "", Q, sec, "With C the inner height",
               None, []),
    ]
    return out


def traceability_note():
    return ("\nThinness probe (environment/brief_thin.py THIN_IN_BRIEF on): QA-W100 rev B states requirements only. "
            "These test-method numbers of the grader are not stated anywhere the agent can read: "
            + "; ".join(NOT_STATED) + ".\n")
