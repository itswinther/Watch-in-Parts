"""Part 5 (crown winding) of the one-job watch's documents: QA-W100's Part 5, the work order's lines and FORMAT.md's
`friction_on` and `keyless` text, and their home cells. make_brief_job.py includes it only when
geometry/keyless_job.py KEYLESS_IN_JOB is True (or with `--keyless OUT`, which writes the documents with Part 5 to
another folder), so the documents on main agree with the grader on main.

The procedure is workstream A's acceptance test (spikes/keyless/docs/PROMPT.md, "The test rig" and "The acceptance
test"), stated in B's frame and at B's scale: the lengths are geometry/keyless_job.py's scaled values, every other
number is A's constant as it is. A supplier fact is cited to its cell (the stem's travel: VM-DS-401 Table 2; the case:
DS-W02; the barrel's running sense and speed: DS-W01 section 4), never restated. Not stated, as for Parts 1 to 4: the
weights of the steps. Every function takes H, the make_brief_job module (num, wrap, cite_case, cell, ...)."""
import inspect
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
from geometry import keyless_job as KJ      # noqa: E402
from geometry import watch as W             # noqa: E402

SECTION = "9. Part 5"
DS401 = "datasheets/DS-401_crown_stem.md"
TRAVEL_ROW = "Travel from position 1 (winding) to position 2 (setting)"
WIGGLE_STEP = 1.5           # degrees: the rocking step, a literal in A's grade.py _pull (checked in check())
BACKWARD_TURN = 360         # degrees: AT-4's backward turn, a literal in A's grade.py worker (checked in check())


def _c():
    """A's constants at B's scale (the namespace the grader uses), and the engine values."""
    C = KJ.job_constants(KJ._import_a("constants"))
    sc = KJ.scaled()
    return C, sc


def check():
    """[error]: the scale table against A's files, A's literals this text states, and the barrel speed."""
    errs = list(KJ.check_table())
    C, _ = _c()
    if C.BARREL_HOURS_PER_TURN != float(1 / W.BARREL_TURNS_PER_HOUR):
        errs.append("A's BARREL_HOURS_PER_TURN %r is not the 8-hour build's speed class (1 turn every %s h)"
                    % (C.BARREL_HOURS_PER_TURN, 1 / W.BARREL_TURNS_PER_HOUR))
    G = KJ._import_a("grade")
    src = inspect.getsource(G._pull) + inspect.getsource(G.worker)
    for text in ("C.WIGGLE_DEG / 1.5", "sgn * 1.5 * k", "_turn(w, -fw * 360)"):
        if text not in src:
            errs.append("A's grade.py changed: %r not found; update environment/brief_keyless.py" % text)
    return errs


def docs_rows():
    """Rows of QA-W100's Documents table."""
    return [("VM-DS-401", "Part 5: the winding stem's travel from position 1 to position 2 (section 4, Table 2)")]


def work_order_goal():
    return ("This job covers the train from the barrel to the hands, the frame, the hands, and the crown-winding works: "
            "with the crown pushed in, turning it winds the mainspring through the arbor of the supplied barrel; pulled "
            "out, turning it sets the hands while the going train stands. The movement has no escapement: in the going "
            "train the barrel is the driver and turns at the steady speed of the speed class given in the order.")


def work_order_rows():
    return "| Winding stem | series VM-DS-401 (`DS-401_crown_stem.md`), with its travel to the setting position |\n"


def part4_text():
    """QA-W100 Part 4: the keyless section's parts are assembled like every other part (A's request 21:20, agreed
    by B)."""
    return ("The parts of `movement.json` include every part of its `keyless` section (Part 5), the stem's parts "
            "among them: each is put in, tested and counted below exactly as any other part, and one left out of "
            "`order` stands in its assembled position from the start.")


def format_assembly_text():
    return ("The part names of `movement.json` include those of its `keyless` section; they are put in like every "
            "other part.")


def format_mobile_line():
    return '    "mobile_name": {"axis": [x, y], "parts": ["part_name", ...], "friction_on": "mobile_name"},\n'


def format_keyless_block():
    return """  "keyless": {
    "stem":  {"parts": ["part_name", ...], "point": [x, y, z], "direction": [dx, dy, 0]},
    "arbor": {"parts": ["part_name", ...]},
    "mobiles": {
      "mobile_name": {"kind": "free", "dof": "rot", "point": [x, y, z], "direction": [dx, dy, dz],
                      "parts": ["part_name", ...]},
      "mobile_name": {"kind": "spring", "dof": "slide", "direction": [dx, dy, dz], "rest": 1, "on_stem": true,
                      "parts": ["part_name", ...]},
      ...
    }
  },
"""


def format_text(H):
    """FORMAT.md bullets: friction_on (A's neutral wording, Decisions 15:47) and the keyless section."""
    return H.wrap("- `friction_on` (optional, on a mobile of `mobiles`): a mobile may be declared as carried by friction "
                  "on another coaxial mobile, named here: their axes are the same within QA-W100's coaxial tolerance, "
                  "and the other mobile is not `barrel` and is not itself carried by friction. In the going train "
                  "the two turn as one.", "  ") + "\n" + \
        H.wrap("- `keyless` (in `movement.json`): the crown-winding works (the crown-winding part of QA-W100). Its parts are part files "
               "like any other, and each part is named once in the file, across `fixed`, `mobiles` and `keyless`; "
               "parts of the crown-winding works that never move are listed under `fixed` (they belong to the frame). "
               "A `keyless` section in `variant_6h.json` is read for its part names only.", "  ") + "\n" + \
        H.wrap("  - `stem`: the stem's parts (the crown included), a `point` on the stem's line and its `direction`, "
               "from `case_centre` towards the crown. The line is horizontal (the direction's z is 0) and passes "
               "through `case_centre` (within QA-W100's coaxial tolerance), so the stem is radial.", "    ") + "\n" + \
        H.wrap("  - `arbor`: the parts fixed to the arbor of the supplied barrel, which turn with it. May be empty.",
               "    ") + "\n" + \
        H.wrap("  - `mobiles`: every other moving part of the crown-winding works, one entry per rigid body. `kind`: "
               "`free` (it moves only when pushed) or `spring` (a light spring urges it towards its rest side). `dof`: "
               "`rot` (it turns about the line through `point` along `direction`) or `slide` (it moves along "
               "`direction`; `point` is not needed). `direction`: three numbers, not all zero. `rest` (springs only): "
               "`1` or `-1`, the sign of the mobile's own coordinate (angle about, or travel along, `direction`) that "
               "its spring urges it towards. `on_stem` (optional, `true` or `false`): `true` for a slide along the "
               "stem's line that also turns with the stem. A name here is not a name of `mobiles`, and not `barrel`, "
               "`stem` or `arbor`.", "    ") + "\n"


def qa_part5(H):
    C, sc = _c()
    n = H.num
    text = """## 9. Part 5: crown winding (`movement.json`, its `keyless` section)

The 8-hour build, with its crown-winding works, is used on a simulated test rig the way an owner uses a watch.

Conditions. If one fails, Part 5 fails and none of its steps passes.

- **C1 Files** of Part 1 for `movement.json`, and its `keyless` section and every part file the section names are
  valid as `/app/FORMAT.md` describes.

The test rig.

- **Bodies.** The rig moves rigid bodies, each with one degree of freedom: the stem (the parts of `keyless.stem`),
  which the rig turns about the stem's line and moves along it; the barrel arbor (the arbor of the supplied barrel,
  DS-W01 section 3, with the parts of `keyless.arbor`), which turns about the barrel's axis; each mobile of
  `keyless.mobiles`, as declared; and, turning freely about their axes, every mobile declared `friction_on` and
  every mobile that the declared meshes drive from the barrel only through such a mobile. Everything else, the
  frame, the barrel's drum and every other mobile of `mobiles`, is one fixed body: the going train stands while
  the crown is used. The minute hand's mobile is called the minute mobile below.
- **Positions and directions.** Position 1 (pushed in) is the stem as delivered. Position 2 (pulled out) is the stem
  moved outwards along its line by the winding stem's travel from position 1 to position 2 (VM-DS-401, section 4,
  Table 2, this series). Forward is turning the crown clockwise as seen from outside the case, looking in along the
  stem; backward is the opposite. The arbor winds when it turns in the barrel's running sense (DS-W01, section 4).
- **Touching.** Two bodies touch, and do not interpenetrate, while they intersect by at most {tol} mm3.
- **Friction.** Clean, dry contacts, brass on steel: coefficient of friction static {mus}, sliding {mud}
  (Engineering ToolBox, "Friction and Friction Coefficients"). A body pushed by another moves the least distance along
  its degree of freedom that the contact, with static friction, allows; if friction prevents it from giving way, it
  does not.
- **Springs.** Spring-loaded mobiles (`spring`) are urged towards their rest side by springs much lighter than the
  mainspring. They give way first when pushed; if they cannot give way, they are pushed along like any body. They
  return towards rest until they touch something; their springs never drive other bodies.
- **Mainspring.** The mainspring always urges the barrel arbor against winding. It is much stronger than any spring
  and pushes whatever is in its way.
- **The crown** is turned in steps of {step} degrees and pulled or pushed in steps of {pstep} mm. A step that cannot
  proceed is blocked, and nothing moves. While pulling or pushing, a blocked step is retried with the crown rocked
  by up to {wig} degrees either way, in steps of {wst} degrees, to let teeth find their gaps.
- **At the start** of each step below, bodies may overlap and settle by up to {settle} mm of surface travel.
- **Starting states.** AT-1 starts from a let-down mainspring. AT-2 starts from a fresh movement whose barrel arbor
  the rig has turned in the winding sense by {prewind} degrees itself (the arbor, not the crown). AT-3 starts where
  AT-2 ends; AT-4, AT-5 and AT-6 each start from the state at the end of AT-2 (crown let go, in position 1).

Steps. Each passes or fails on its own.

0. **AT-0 Assemble.** At rest, as delivered, no two bodies intersect by more than {tol} mm3. Every mobile of
   `keyless.mobiles` and every freely turning mobile of the going train, moved {shift} mm across its axis in each of
   two perpendicular directions (and, for one that turns, along its axis each way), intersects some other body by
   more than {tol} mm3. Every part of the `keyless` section except the stem's lies within the inner radius of the
   case named in the work order ({crad}) of the vertical line through `case_centre`; the whole movement with these
   parts is no taller than the inner height of that case ({chgt}); and stem material reaches at least {prot} mm
   beyond that radius.
1. **AT-1 Wind.** The crown, in position 1, is turned forward {wt} turn. It is never blocked; it takes between {wlo}
   and {whi} crown turns per turn of the barrel arbor (measured over this turn); the minute mobile moves at most
   {still} degree.
2. **AT-2 Hold.** The crown is let go for {hs} steps: it is free to turn, pushed like any free body, and the mainspring
   pulls back. Every {te} steps the rig taps the movement: each free body moves up to {tap} mm (surface travel) in
   the direction it can move furthest, and spring-loaded bodies return towards rest. The arbor runs back at most
   {rb} degrees in all, and over the last {hl} steps it moves at most {hd} degree: it is held.
3. **AT-3 Run.** Fully wound, the mainspring stores {cap} turns of the arbor; the run-back measured in AT-2 is lost
   from that, and while the watch runs the barrel turns at the speed class of the 8-hour build (DS-W01, section 4),
   so the power reserve is (capacity - run-back) x the hours per barrel turn. It is at least {res} hours. The barrel
   is free to run: with the crown in position 1, the arbor is turned in the winding sense by itself through {fr}
   degrees in steps of {frs} degree, and no step is blocked. It is still coupled: then the crown is turned forward
   {ct} degrees; it is never blocked and the arbor winds by more than {still} degree.
4. **AT-4 Backward.** The crown, in position 1, is turned backward {bt} degrees. It is never blocked; the arbor
   moves at most {still} degree in the winding sense and loses at most {htol} degrees; the minute mobile moves at
   most {still} degree. Then the crown is turned forward {ct} degrees: never blocked, and the arbor winds by more
   than {still} degree.
5. **AT-5 Set.** The crown is pulled out to position 2, stopping at {ns} evenly spaced positions (both ends
   included). At each stop, from the same state, the crown is turned {sw} degrees forward and, separately, {sw}
   degrees backward. No test turn is blocked, and none drives both trains (the arbor winding by more than {still}
   degree and the minute mobile moving by more than {still} degree). At position 1 the forward test turn winds and
   does not set; at position 2 it sets and does not wind. Then, in position 2, the crown is turned {st} degrees
   forward and {st} degrees back: it is never blocked, the minute mobile turns at least {smin} degrees each way, and
   the arbor never loses more than {htol} degrees.
6. **AT-6 Return.** From position 2 the crown is pushed back in, stopping at the same positions in reverse order,
   with the same test turns and the same rules (never blocked, never both trains). Then, in position 1, it is
   turned forward {rw} degrees: it is never blocked, and the arbor winds by more than {still} degree.

Part 5 is judged by the steps that pass. The rig runs Part 5 as one, within at most {pt} s of the whole inspection's
time; a step not finished by then fails.
""".format(tol=n(sc["TOL"]), mus=n(C.MU_STATIC), mud=n(C.MU_SLIDING), step=n(C.STEP_DEG), pstep=n(sc["PULL_STEP"]),
           wig=n(C.WIGGLE_DEG), wst=n(WIGGLE_STEP), settle=n(sc["World.settle:budget"]), prewind=n(C.PREWIND_DEG),
           shift=n(sc["HOLD_SHIFT"]), crad=H.cite_case("Inner radius (mm)"),
           chgt=H.cite_case("Inner height along the axis (mm)"), prot=n(sc["STEM_PROTRUDE"]), wt=n(C.WIND_TURNS),
           wlo=n(C.WIND_BAND[0]), whi=n(C.WIND_BAND[1]), still=n(C.STILL_TOL), hs=C.HOLD_STEPS, te=C.TAP_EVERY,
           tap=n(sc["TAP_ARC"]), rb=n(C.CLICK_RUNBACK), hl=C.HELD_LAST_STEPS, hd=n(C.HELD_DRIFT),
           cap=n(C.CAPACITY_TURNS), res=n(C.RESERVE_MIN), fr=n(C.FREE_RUN_DEG), frs=n(C.FREE_RUN_STEP),
           ct=n(C.COUPLED_TURN), bt=BACKWARD_TURN, htol=n(C.HOLD_TOL), ns=C.SWEEP_SAMPLES, sw=n(C.SWEEP_TURN),
           st=n(C.SET_TURN), smin=n(C.SET_MIN), rw=n(C.REWIND_TURN), pt=KJ.KEYLESS_TIMEOUT_S)
    return _rewrap(text, H)


def _rewrap(text, H):
    """Fill every paragraph, bullet and numbered item to the documents' width (the values change the line lengths)."""
    import re
    out, block, indent = [], [], ""

    def flush():
        if block:
            out.append(H.wrap(" ".join(s.strip() for s in block), indent))
            block.clear()
    for ln in text.split("\n"):
        m = re.match(r"^(\d+\. |- )", ln)
        if ln.startswith("#") or not ln.strip():
            flush()
            out.append(ln)
        elif m:
            flush()
            indent = " " * len(m.group(1))
            block.append(ln)
        else:
            if not block:
                indent = ""
            block.append(ln)
    flush()
    return "\n".join(out)


def trace_rows(H):
    """Home cells of every number Part 5 states (QA-W100 section 9) and of the stem's travel (VM-DS-401)."""
    C, sc = _c()
    n, cell, Q, P = H.num, H.cell, "datasheets/" + H.QA_FILE, SECTION
    k = "keyless "
    return [
        cell(k + "PULL: 0.80 x S = %s, used as %s (geometry/keyless_job.py); VM-DS-401 prints it to 0.01 mm"
             % (n(0.80 * KJ.S), n(sc["PULL"])), sc["PULL"], DS401, "4. Winding stem", TRAVEL_ROW, "This series",
             [n(round(sc["PULL"], 2))]),
        cell(k + "TOL x S^3 (A's engine.TOL, rounded)", sc["TOL"], Q, P, "**Touching.**", None, [n(sc["TOL"])]),
        cell(k + "MU_STATIC, MU_SLIDING (A's constants)", (C.MU_STATIC, C.MU_SLIDING), Q, P, "**Friction.**", None,
             [n(C.MU_STATIC), n(C.MU_SLIDING)]),
        cell(k + "STEP_DEG, PULL_STEP x S, WIGGLE_DEG, the rocking step (literal 1.5 in A's grade._pull)",
             (C.STEP_DEG, sc["PULL_STEP"], C.WIGGLE_DEG, WIGGLE_STEP), Q, P, "**The crown**", None,
             [n(C.STEP_DEG), n(sc["PULL_STEP"]), n(C.WIGGLE_DEG), n(WIGGLE_STEP)]),
        cell(k + "engine World.settle budget x S", sc["World.settle:budget"], Q, P, "**At the start**", None,
             [n(sc["World.settle:budget"])]),
        cell(k + "PREWIND_DEG", C.PREWIND_DEG, Q, P, "**Starting states.**", None, [n(C.PREWIND_DEG)]),
        cell(k + "HOLD_SHIFT x S, STEM_PROTRUDE x S", (sc["HOLD_SHIFT"], sc["STEM_PROTRUDE"]), Q, P, "0. **AT-0", None,
             [n(sc["HOLD_SHIFT"]), n(sc["STEM_PROTRUDE"])]),
        cell(k + "WIND_TURNS, WIND_BAND, STILL_TOL", (C.WIND_TURNS, C.WIND_BAND, C.STILL_TOL), Q, P, "1. **AT-1", None,
             [n(C.WIND_TURNS), n(C.WIND_BAND[0]), n(C.WIND_BAND[1]), n(C.STILL_TOL)]),
        cell(k + "HOLD_STEPS, TAP_EVERY, TAP_ARC x S, CLICK_RUNBACK, HELD_LAST_STEPS, HELD_DRIFT",
             (C.HOLD_STEPS, C.TAP_EVERY, sc["TAP_ARC"], C.CLICK_RUNBACK, C.HELD_LAST_STEPS, C.HELD_DRIFT), Q, P,
             "2. **AT-2", None, [C.HOLD_STEPS, C.TAP_EVERY, n(sc["TAP_ARC"]), n(C.CLICK_RUNBACK), C.HELD_LAST_STEPS,
                                 n(C.HELD_DRIFT)]),
        cell(k + "CAPACITY_TURNS, RESERVE_MIN, FREE_RUN_DEG, FREE_RUN_STEP, COUPLED_TURN (BARREL_HOURS_PER_TURN is "
             "the 8-hour build's speed class, cited)", (C.CAPACITY_TURNS, C.RESERVE_MIN, C.FREE_RUN_DEG,
                                                       C.FREE_RUN_STEP, C.COUPLED_TURN), Q, P, "3. **AT-3", None,
             [n(C.CAPACITY_TURNS), n(C.RESERVE_MIN), n(C.FREE_RUN_DEG), n(C.FREE_RUN_STEP), n(C.COUPLED_TURN)]),
        cell(k + "AT-4 backward turn (literal 360 in A's grade.worker), HOLD_TOL", (BACKWARD_TURN, C.HOLD_TOL), Q, P,
             "4. **AT-4", None, [BACKWARD_TURN, n(C.HOLD_TOL)]),
        cell(k + "SWEEP_SAMPLES, SWEEP_TURN, SET_TURN, SET_MIN", (C.SWEEP_SAMPLES, C.SWEEP_TURN, C.SET_TURN, C.SET_MIN),
             Q, P, "5. **AT-5", None, [C.SWEEP_SAMPLES, n(C.SWEEP_TURN), n(C.SET_TURN), n(C.SET_MIN)]),
        cell(k + "REWIND_TURN", C.REWIND_TURN, Q, P, "6. **AT-6", None, [n(C.REWIND_TURN)]),
        cell(k + "KEYLESS_TIMEOUT_S (geometry/keyless_job.py)", KJ.KEYLESS_TIMEOUT_S, Q, P, "Part 5 is judged", None,
             [KJ.KEYLESS_TIMEOUT_S]),
    ]
