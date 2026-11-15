"""Crown winding (keyless works) as Part 5 of the one-job watch (SESSION.md Decisions 15:29, 15:47, 17:46).

The acceptance test is workstream A's: spikes/keyless/engine.py (the contact engine), grade.py (AT-0 to AT-6, the
`worker` phases, `held_check`, `make_world`) and constants.py, imported and never copied or edited here. This module
holds, in one place:
  - KEYLESS_IN_JOB, the switch: Part 5 is in the grader's JOB_PARTS and in the brief only when it is True;
  - SCALE_TABLE, the one table that moves A's length constants to B's demonstration scale S (lengths x S, volumes
    x S^3; angles, turns, hours, friction and counts unchanged, so they are taken from A's module as they are);
    check_table() fails when a listed A value is no longer what A's files hold;
  - B's frame values that replace A's frame constants (winding sense, barrel axis, case);
  - the `keyless` section of movement.json (parse_keyless) and the adapter that turns a delivery into A's bodies
    (build_world, write_world, read_world). The run itself is tests/grade_keyless.py, in a fresh interpreter.
Importing this module is light (no CadQuery, no manifold); geometry.watch is imported inside the functions."""
import json
import math
import os
import sys

KEYLESS_IN_JOB = False      # Part 5 is graded and briefed only when True (Decisions 17:46: A's v2 reference first)
S = 1.617                   # demonstration scale (Decisions 14:45; A's datasheets, s = 1.617); one value for the job
P5_WEIGHT = (25, 100)       # Part 5's weight in JOB_PARTS (Decisions 15:44)

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
A_DIR = os.path.join(ROOT, "spikes", "keyless")      # workstream A's engine and acceptance test (A may move it)

# ---------------------------------------------------------------------------------------------------------------
# A's length constants at B's scale. (A's file, name, A's value there, the value scaled here, power of S, digits the
# job value is rounded to or None, note). The job value is (scaled value) x S^power, rounded; a pair (PULL_RANGE) is
# scaled element by element. check_table() compares the third column with A's files, so a change on A's side is
# caught here rather than silently copied. "World.phase:budget" is a default argument of A's engine (mm of surface
# travel; World.phase passes it on to World.settle, so settle's own default is not used by the rig); the others are
# module attributes. MAIN_TRY is in both of A's modules: the engine imports it from constants at import time, so the
# engine's attribute is the one the rig uses, and both rows are set.
SCALE_TABLE = (
    ("constants", "PULL", 0.9, 0.80, 1, 3,
     "position 2: VM-DS-401 Table 2 travel, 0.80 mm at 1:1 (Sellita SW200-1) x S = 1.294 (builder K's fitting pass); "
     "A's standalone v1 keeps 0.9 at its own scale (INTERFACE_FOR_B.md, notes)"),
    ("constants", "PULL_RANGE", (0.4, 1.0), (0.4, 1.0), 1, None,
     "a declared pull's range (A's keyless.json `pull`; the joined job declares none, so position 2 is PULL)"),
    ("constants", "PULL_STEP", 0.03, 0.03, 1, None, "stem pull per rig step"),
    ("constants", "TAP_ARC", 0.05, 0.05, 1, None, "AT-2 tap, surface travel of each free part"),
    ("constants", "HOLD_SHIFT", 0.3, 0.3, 1, None, "AT-0 held: the shift that must hit something"),
    ("constants", "STEM_PROTRUDE", 0.5, 0.5, 1, None, "AT-0 bounds: stem material at least this far outside the case"),
    ("constants", "MAIN_TRY", 0.02, 0.02, 1, None, "mainspring's try per step (A's constants; see engine.MAIN_TRY)"),
    ("constants", "FIT_CLEARANCE", 0.005, 0.005, 1, None, "the fit rule: radial play given to every empty bore of a turning axis"),
    ("constants", "FIT_CENTRE_TOL", 0.02, 0.02, 1, None, "the fit rule: a hole is a bore of the axis within this"),
    ("constants", "FIT_EMPTY_INSET", 0.01, 0.01, 1, None, "the fit rule: a bore is empty when nothing lies inside its radius less this"),
    ("engine", "TOL", 2e-4, 2e-4, 3, 7, "overlap two bodies may have and still only touch (mm3, x S^3)"),
    ("engine", "FORCE_EPS", 1e-7, 1e-7, 3, None, "overlap difference below which a contact pushes neither way (mm3, x S^3)"),
    ("engine", "RELAX_MAX", 0.25, 0.25, 1, None, "a spring's return per step"),
    ("engine", "SCAN_ARC", 0.002, 0.002, 1, None, "search step for the clearing position"),
    ("engine", "MAX_STEP_TRAVEL", 0.06, 0.06, 1, None, "a step moving any surface further is split"),
    ("engine", "SPRING_PUSH_ARC", 0.01, 0.01, 1, None, "a returning spring's push increment on free parts"),
    ("engine", "RADIUS_FLOOR", 0.05, 0.05, 1, None, "a body's radius about its axis is at least this"),
    ("engine", "LEVER_FLOOR", 0.05, 0.05, 1, None, "budget(): a contact's lever arm is at least this"),
    ("engine", "NEIGHBOUR_MARGIN", 0.05, 0.05, 1, None, "neighbours(): boxes closer than this are neighbours"),
    ("engine", "MAIN_TRY", 0.02, 0.02, 1, None, "mainspring's try per step (World.step's default when None)"),
    ("engine", "World.phase:budget", 0.3, 0.3, 1, None, "start: overlap each mover may clear by settling and phasing"),
)
# Every length of A's engine and grade module that the rig uses is in the table (INTERFACE_FOR_B.md, "Lengths on the
# engine-fix branch"); nothing is left at A's scale.
UNSCALED = ()

# B's frame in place of A's frame constants (A: constants.py STEM_POINT, STEM_DIR, BARREL_AXIS, WIND_SENSE,
# MINUTE_AXIS, CASE_*). The stem line is declared in the delivery; the minute body is the minute hand's mobile.
WIND_SENSE = -1.0           # the supplied arbor is wound clockwise seen from +z (the drum's running sense, DS-W01
                            # section 4; builder K, Decisions 17:46): negative about +z. The mainspring urges it back.
BARREL_POINT = (0.0, 0.0, 0.0)
BARREL_DIR = (0.0, 0.0, 1.0)
# Grader-side speed-up only: the fixed body is cut to the reach of the moving bodies grown by this (mm); a slide
# body's reach along its direction is taken as SLIDE_REACH either way. Intersections inside that region are unchanged.
CROP_MARGIN = 2.0
SLIDE_REACH = 6.0
KEYLESS_TIMEOUT_S = 5400    # s, the whole Part 5 run (bounded by the grader's whole-run limit)
KEYLESS_JOBS = 3          # Part 5 phases in this many spawned interpreters (no fork; A 23:12 proposal, B agreed): wall time about the wind phase
BODY_KINDS = ("free", "spring")
DOFS = ("rot", "slide")


def _import_a(name):
    """A's module `name` (constants, engine, grade) from A_DIR, imported under its own name (A's grade.py imports
    `constants` and `engine` by those names)."""
    if A_DIR not in sys.path:
        sys.path.insert(0, A_DIR)
    import importlib
    mod = importlib.import_module(name)
    if os.path.dirname(os.path.abspath(mod.__file__)) != A_DIR:
        raise ImportError("module %s comes from %s, not from %s" % (name, mod.__file__, A_DIR))
    return mod


def _default(func, arg):
    import inspect
    p = inspect.signature(func).parameters
    if arg not in p or p[arg].default is inspect.Parameter.empty:
        raise ValueError("A's %s has no default argument %r any more" % (func.__qualname__, arg))
    return p[arg].default


def _a_value(mods, where, name):
    if "." in name and ":" in name:
        cls, rest = name.split(".", 1)
        fn, arg = rest.split(":")
        return _default(getattr(getattr(mods[where], cls), fn), arg)
    return getattr(mods[where], name)


def _scale1(base, power, digits):
    v = base * S ** power
    return round(v, digits) if digits is not None else v


def job_value(row):
    """(scaled value) x S^power, rounded to the row's digits; element by element for a pair."""
    _, _, _, base, power, digits, _ = row
    if isinstance(base, tuple):
        return tuple(_scale1(b, power, digits) for b in base)
    return _scale1(base, power, digits)


def scaled():
    """{name: job value} of every row of SCALE_TABLE (the engine's default arguments under their table names)."""
    return {r[1]: job_value(r) for r in SCALE_TABLE}


def check_table(mods=None):
    """[error] for every row whose A value is not what A's files hold, or whose job value is not (scaled value) x
    S^power (rounded as stated); [] when consistent. mods: {"constants": module, "engine": module} (imported from
    A_DIR when None; importing the engine needs manifold3d)."""
    if mods is None:
        mods = {"constants": _import_a("constants"), "engine": _import_a("engine")}
    errs = []
    for row in SCALE_TABLE:
        where, name, a_val, base, power, digits, note = row
        try:
            live = _a_value(mods, where, name)
        except (AttributeError, ValueError) as e:
            errs.append("%s.%s: not found in A's files (%s)" % (where, name, e))
            continue
        lv = tuple(live) if isinstance(live, (tuple, list)) else (live,)
        av = a_val if isinstance(a_val, tuple) else (a_val,)
        if not (len(lv) == len(av) and all(isinstance(x, (int, float)) and not isinstance(x, bool)
                                           and math.isclose(x, y, rel_tol=0, abs_tol=1e-15) for x, y in zip(lv, av))):
            errs.append("%s.%s: A's files hold %r, the table %r" % (where, name, live, a_val))
        bv = base if isinstance(base, tuple) else (base,)
        gv = job_value(row)
        gv = gv if isinstance(gv, tuple) else (gv,)
        for b_, got in zip(bv, gv):
            want = b_ * S ** power
            tol = 0.5 * 10 ** -digits if digits is not None else 1e-15 * max(1.0, abs(want))
            if abs(got - want) > tol:
                errs.append("%s.%s: job value %r is not %r x %r^%d" % (where, name, got, b_, S, power))
        if base != a_val and "VM-DS" not in note:
            errs.append("%s.%s: scaled value %r differs from A's %r without a cited source" % (where, name, base, a_val))
    return errs


def step_weights():
    """{A's step name: weight as an exact fraction}, A's STEP_WEIGHTS in A's step order (AT-0 to AT-6)."""
    from fractions import Fraction
    C = _import_a("constants")
    return {k: Fraction(str(C.STEP_WEIGHTS[k])) for k in C.STEPS}



JOB_SPRING = "LT"       # the spring the supplied (thin) barrel holds: DS-101 Rev F row LT, spring L with a 0.25 strip (b/thin-4mm)
DS101 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "spikes", "keyless", "datasheets",
                     "DS-101_mainspring_barrel.md")


def capacity_turns(path=DS101):
    """AT-3's capacity in the joined job: DS-101 Table 3, row JOB_SPRING, column "N at r = D/6" (A's 21:50 answer).
    Also checks that the row's core radius "r = D/6 (mm)" equals the supplied arbor's core (geometry/watch.py)."""
    import re
    from geometry import watch as W
    with open(path, encoding="utf-8") as f:
        txt = f.read()
    sec = txt[txt.index("(Table 3, calculated)"):]
    m = re.search(r"^\|\s*%s\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|\s*([0-9.]+)\s*\|" % JOB_SPRING, sec, re.M)
    if not m:
        raise RuntimeError("DS-101 Table 3: no row %s" % JOB_SPRING)
    core, n = float(m.group(1)), float(m.group(3))
    if abs(core - W.BARREL_CORE_R) > 0.005:
        raise RuntimeError("DS-101 Table 3 row %s: core %s mm, supplied arbor core %s mm" % (JOB_SPRING, core, W.BARREL_CORE_R))
    return n

def job_constants(C):
    """A namespace with every upper-case constant of A's constants module C, the scaled lengths of SCALE_TABLE and
    B's frame values in place of A's (WIND_SENSE; the case, the stem line and the minute body come from the delivery)."""
    import types
    ns = types.SimpleNamespace(**{k: getattr(C, k) for k in dir(C) if k.isupper()})
    for row in SCALE_TABLE:
        if row[0] == "constants":
            setattr(ns, row[1], job_value(row))
    ns.WIND_SENSE = WIND_SENSE
    ns.CAPACITY_TURNS = capacity_turns()        # the supplied spring's turns, from DS-101 (A's 21:50 answer)
    for k in ("STEM_POINT", "STEM_DIR", "BARREL_AXIS", "MINUTE_AXIS", "CASE_CENTRE", "CASE_RADIUS", "CASE_Z"):
        if hasattr(ns, k):
            delattr(ns, k)          # B's frame: these come from the delivery and geometry/watch.py, never A's
    return ns


def apply_to_engine(E, G):
    """Put the scaled constants into A's engine module E and grade module G, in this interpreter only (the P5 run is
    a fresh interpreter, tests/grade_keyless.py). Returns the namespace now used as G.C."""
    errs = check_table({"constants": _import_a("constants"), "engine": E})
    if errs:
        raise RuntimeError("SCALE_TABLE disagrees with A's files: " + "; ".join(errs))
    ns = job_constants(G.C)
    for row in SCALE_TABLE:
        if row[0] != "engine":
            continue
        name, val = row[1], job_value(row)
        if ":" in name:
            cls, rest = name.split(".", 1)
            fn, arg = rest.split(":")
            f = getattr(getattr(E, cls), fn)
            import inspect
            names = [p for p in inspect.signature(f).parameters]
            # positional defaults line up with the last len(__defaults__) parameters (self excluded from neither)
            d = list(f.__defaults__)
            idx = names.index(arg) - (len(names) - len(d))
            d[idx] = val
            f.__defaults__ = tuple(d)
        else:
            setattr(E, name, val)
    G.C = ns
    return ns


# ---------------------------------------------------------------------------------------------------------------
# The keyless section of movement.json
def keyless_part_names(kl):
    """Part names a keyless section names (stem, arbor, then mobiles), as far as its layout can be read. The layout is
    checked by parse_keyless; this only lets the movement loader count every part file once across the file."""
    out = []
    if not isinstance(kl, dict):
        return out
    for key in ("stem", "arbor"):
        e = kl.get(key)
        if isinstance(e, dict) and isinstance(e.get("parts"), list):
            out += [n for n in e["parts"] if isinstance(n, str)]
    mob = kl.get("mobiles")
    if isinstance(mob, dict):
        for e in mob.values():
            if isinstance(e, dict) and isinstance(e.get("parts"), list):
                out += [n for n in e["parts"] if isinstance(n, str)]
    return out


def _vec(x, what, n=3):
    from .core import FormatError
    if not (isinstance(x, list) and len(x) == n and all(isinstance(v, (int, float)) and not isinstance(v, bool)
                                                        and math.isfinite(v) for v in x)):
        raise FormatError("%s must be %d finite numbers" % (what, n))
    return tuple(float(v) for v in x)


def _unit(x, what):
    from .core import FormatError
    v = _vec(x, what)
    n = math.sqrt(sum(c * c for c in v))
    if n < 1e-9:
        raise FormatError("%s must not be zero" % what)
    return tuple(c / n for c in v)


def parse_keyless(m):
    """The `keyless` section of movement m (geometry.watch.Movement), checked: FormatError for a missing or malformed
    section. Returns {"stem": {"parts", "point", "direction"}, "arbor": [parts], "mobiles": {name: {...}}}.
    Rules: the stem is horizontal (direction's z = 0) and its line passes within COAX_TOL of case_centre (radial);
    its direction points from the case centre towards the crown (position 2 is the stem moved PULL that way); a
    mobile's kind is free or spring, its dof rot or slide; rot needs a point; a spring needs rest 1 or -1; on_stem
    only for a slide along the stem line; mobile names are not those of the going train's mobiles, nor barrel."""
    from . import watch as W
    from .core import FormatError
    kl = m.doc.get("keyless")
    if kl is None:
        raise FormatError("movement.json has no 'keyless' section")
    if not isinstance(kl, dict):
        raise FormatError("keyless: must be an object")
    unknown = sorted(set(kl) - {"stem", "arbor", "mobiles"})
    if unknown:
        raise FormatError("keyless: unknown key(s) %s" % ", ".join(unknown))

    def names(e, where, empty_ok=False):
        ps = e.get("parts") if isinstance(e, dict) else None
        if not isinstance(ps, list) or (not ps and not empty_ok) or not all(isinstance(p, str) for p in ps):
            raise FormatError("%s: needs a %slist of part names" % (where, "" if empty_ok else "non-empty "))
        return list(ps)
    st = kl.get("stem")
    if not isinstance(st, dict):
        raise FormatError("keyless.stem: must be an object with parts, point and direction")
    stem = {"parts": names(st, "keyless.stem"), "point": _vec(st.get("point"), "keyless.stem.point"),
            "direction": _unit(st.get("direction"), "keyless.stem.direction")}
    u, p = stem["direction"], stem["point"]
    if abs(u[2]) > 1e-9:
        raise FormatError("keyless.stem.direction: the stem is horizontal (its z component must be 0)")
    cx, cy = m.case_centre
    dist = abs((cx - p[0]) * u[1] - (cy - p[1]) * u[0])
    if dist > W.COAX_TOL:
        raise FormatError("keyless.stem: the stem line passes %.4f mm from case_centre; it must be radial (within %g)"
                          % (dist, W.COAX_TOL))
    arbor = names(kl.get("arbor"), "keyless.arbor", empty_ok=True) if kl.get("arbor") is not None else []
    mobs = kl.get("mobiles", {})
    if not isinstance(mobs, dict):
        raise FormatError("keyless.mobiles: must be an object")
    out = {}
    for name, e in mobs.items():
        where = "keyless.mobiles.%s" % name
        if not W.NAME_RE.match(str(name)) or name in m.mobiles or name in ("barrel", "stem", "arbor"):
            raise FormatError("%s: bad mobile name (letters, digits, _ and -; not a mobile of 'mobiles', not barrel, "
                              "stem or arbor)" % where)
        if not isinstance(e, dict):
            raise FormatError("%s: must be an object" % where)
        kind, dof = e.get("kind"), e.get("dof")
        if kind not in BODY_KINDS:
            raise FormatError("%s: kind must be 'free' or 'spring'" % where)
        if dof not in DOFS:
            raise FormatError("%s: dof must be 'rot' or 'slide'" % where)
        d = _unit(e.get("direction"), where + ".direction")
        pt = _vec(e.get("point"), where + ".point") if dof == "rot" else (0.0, 0.0, 0.0)
        on_stem = e.get("on_stem", False)
        if not isinstance(on_stem, bool):
            raise FormatError("%s: on_stem must be true or false" % where)
        if on_stem and (dof != "slide" or abs(abs(sum(a * b for a, b in zip(d, u))) - 1.0) > 1e-6):
            raise FormatError("%s: only a slide along the stem line can ride on the stem" % where)
        rest = None
        if kind == "spring":
            r = e.get("rest")
            if r not in (1, -1) or isinstance(r, bool):
                raise FormatError("%s: a spring needs rest 1 or -1" % where)
            rest = r
        out[name] = {"parts": names(e, where), "kind": kind, "dof": dof, "point": pt, "direction": d,
                     "rest": rest, "on_stem": on_stem}
    return {"stem": stem, "arbor": arbor, "mobiles": out}


def load_keyless(m):
    """(parsed section, {part name: solid}) for movement m; the part files are read through m's own loader (the
    same checks and cache as every other part)."""
    k = parse_keyless(m)
    solids = {}
    for n in k["stem"]["parts"] + k["arbor"] + [p for e in k["mobiles"].values() for p in e["parts"]]:
        solids[n] = m.load_part(n)
    return k, solids


def train_split(m):
    """B's P5 rule (Decisions 15:47, widened 17:46/18:45): (fixed going-train mobiles, free going-train mobiles).
    Free: every `friction_on` mobile, and every mobile reached from the barrel, through declared meshes, only through
    a friction_on mobile. Fixed: every other mobile (with the frame and the barrel's drum, one fixed body)."""
    adj = {k: set() for k in m.mobiles}
    for a, _, b, _ in m.meshes:
        adj[a].add(b)
        adj[b].add(a)
    fr = set(m.friction)
    links = {k: set(v) for k, v in adj.items()}
    for f, c in m.friction.items():
        links[f].add(c)
        links[c].add(f)

    def reach(nbrs, avoid):
        seen, todo = {"barrel"}, ["barrel"]
        while todo:
            k = todo.pop()
            for j in nbrs[k]:
                if j not in seen and j not in avoid:
                    seen.add(j)
                    todo.append(j)
        return seen
    r_all, r_direct = reach(links, set()), reach(adj, fr)
    free = sorted(fr | (r_all - r_direct))
    fixed = [k for k in m.mobiles if k != "barrel" and k not in free]
    return fixed, free


# ---------------------------------------------------------------------------------------------------------------
# A's bodies from a delivery
MINUTE = "minute_wheel"     # A's name of the body AT-1, AT-4 and AT-5 watch (here: the minute hand's mobile)
# B's P5 rule for the minute mobile (Decisions 15:47, 17:46/18:45): it must be a free body in P5 (declared
# friction_on, or driven from the barrel only through such a mobile), or the hands cannot be set while the going train
# stands. Then the setting steps cannot be meaningful (with a fixed minute body "never both trains" holds trivially),
# so AT-5 and AT-6 fail with this reason and are not run.
SETTING_STEPS = ("set", "return")


def minute_not_free_reason(minute):
    return ("not run: the minute hand's mobile %r is part of the fixed going train in Part 5 (it is not declared "
            "friction_on, nor driven from the barrel only through a friction_on mobile), so the hands cannot be set "
            "while the going train stands; AT-5 and AT-6 fail" % minute)


def build_world(m, k, solids):
    """A's bodies for movement m with keyless section k (parse_keyless) and its part solids. Returns (bodies, meta):
    bodies = [{"name", "kind", "dof", "point", "direction", "rest", "carrier", "solid", "role"}] in A's terms
    (kind fixed / driven / contact / spring / main; rest +-inf or None); meta = the split and the AT-0 bounds facts.
    Body names: "fixed" (frame + fixed going train + drum), "barrel" (supplied arbor + keyless.arbor parts),
    "stem", "minute_wheel" (the minute hand's mobile), "train.<mobile>" (free going-train mobiles),
    "keyless.<mobile>" (the keyless section's mobiles)."""
    from . import watch as W
    from .core import union
    fixed_gt, free_gt = train_split(m)
    minute = m.hands["minute"][0]
    drum, arbor = W.barrel_bodies()["barrel_drum"], W.barrel_bodies()["barrel_arbor"]
    bodies = []

    def add(name, kind, solid, role, dof=None, point=None, direction=None, rest=None, carrier=None):
        bodies.append({"name": name, "kind": kind, "dof": dof, "point": point, "direction": direction, "rest": rest,
                       "carrier": carrier, "solid": solid, "role": role})
    fixed_solids = [m.fixed, drum] + [m.mobiles[n]["solid"] for n in fixed_gt if n != minute]
    add("fixed", "fixed", union(fixed_solids), "frame, fixed going train (%s), barrel drum" % ", ".join(
        n for n in fixed_gt if n != minute))
    add("barrel", "main", union([arbor] + [solids[n] for n in k["arbor"]]), "supplied arbor + keyless.arbor",
        dof="rot", point=BARREL_POINT, direction=BARREL_DIR, rest=-WIND_SENSE * math.inf)
    add("stem", "driven", union([solids[n] for n in k["stem"]["parts"]]), "keyless.stem", dof="stem",
        point=k["stem"]["point"], direction=k["stem"]["direction"])
    for n in [minute] + [x for x in free_gt if x != minute]:
        ax = m.mobiles[n]["axis"]
        name = MINUTE if n == minute else "train." + n
        if n == minute and n not in free_gt:
            add(name, "fixed", m.mobiles[n]["solid"], "minute hand's mobile %s (going train, fixed)" % n)
        else:
            add(name, "contact", m.mobiles[n]["solid"], "going-train mobile %s%s" % (
                n, " (friction_on %s)" % m.friction[n] if n in m.friction else " (driven through friction)"),
                dof="rot", point=(ax[0], ax[1], 0.0), direction=(0.0, 0.0, 1.0))
    for n, e in k["mobiles"].items():
        add("keyless." + n, "spring" if e["kind"] == "spring" else "contact",
            union([solids[p] for p in e["parts"]]), "keyless mobile %s" % n, dof=e["dof"], point=e["point"],
            direction=e["direction"], rest=(e["rest"] * math.inf) if e["rest"] is not None else None,
            carrier="stem" if e["on_stem"] else None)
    meta = {"fixed_going_train": [n for n in fixed_gt if n != minute], "free_going_train": free_gt,
            "minute_mobile": minute, "minute_free": minute in free_gt, "bounds": bounds(m, k, solids)}
    if minute not in free_gt:
        meta["setting_not_run"] = minute_not_free_reason(minute)
    return bodies, meta


def bounds(m, k, solids):
    """AT-0 bounds in B's frame: every keyless part (stem excepted) within the case radius of case_centre; the whole
    movement with its keyless parts no taller than the case; stem material at least STEM_PROTRUDE x S outside the
    case radius at its crown end (the side of case_centre that keyless.stem.direction points to). Returns (passed,
    details)."""
    import numpy as np
    from . import watch as W
    from .core import verts
    cx, cy = m.case_centre
    ux, uy = k["stem"]["direction"][0], k["stem"]["direction"][1]
    stem = set(k["stem"]["parts"])
    worst, protrude, zlo, zhi = -math.inf, -math.inf, math.inf, -math.inf
    for n, s_ in solids.items():
        V = verts(s_)
        R = np.hypot(V[:, 0] - cx, V[:, 1] - cy) - W.CASE_RADIUS
        if n in stem:
            # only stem material at the crown end counts (A's bounds_check: the side of the case centre the stem's
            # direction points to); material across the case centre at the far end does not
            out = R[(V[:, 0] - cx) * ux + (V[:, 1] - cy) * uy > 0]
            if out.size:
                protrude = max(protrude, float(out.max()))
        else:
            worst = max(worst, float(R.max()))
        zlo, zhi = min(zlo, float(V[:, 2].min())), max(zhi, float(V[:, 2].max()))
    e = m.extent()
    zlo, zhi = min(zlo, e["z_min"]), max(zhi, e["z_max"])
    need = scaled()["STEM_PROTRUDE"]
    ok = worst <= 1e-6 and (zhi - zlo) <= W.CASE_HEIGHT + 1e-9 and protrude >= need
    return ok, {"beyond_case_radius": round(worst, 4) if math.isfinite(worst) else None,
                "height_with_keyless": round(zhi - zlo, 4), "case_height": W.CASE_HEIGHT,
                "stem_protrude": round(protrude, 4) if math.isfinite(protrude) else None, "stem_protrude_min": need}


def crop_fixed(bodies):
    """The fixed body cut to the region the other bodies can reach (a speed-up: intersections with the moving bodies
    are unchanged while each stays within its reach; see CROP_MARGIN, SLIDE_REACH). Returns (bodies, triangles before,
    triangles after)."""
    import numpy as np
    import manifold3d as m3
    from .core import verts
    byname = {b["name"]: b for b in bodies}
    boxes = []
    for b in bodies:
        if b["kind"] == "fixed" or b["solid"].is_empty():
            continue
        V = verts(b["solid"])
        ax = b if b["carrier"] is None else byname[b["carrier"]]
        lo, hi = V.min(axis=0), V.max(axis=0)
        if b["dof"] == "slide":
            d = np.asarray(b["direction"], float)
            lo, hi = np.minimum(lo, lo - SLIDE_REACH * np.abs(d)), np.maximum(hi, hi + SLIDE_REACH * np.abs(d))
        if ax["dof"] in ("rot", "stem"):
            p, u = np.asarray(ax["point"], float), np.asarray(ax["direction"], float)
            u = u / np.linalg.norm(u)
            pts = np.vstack([V, [lo, hi]]) if b["dof"] == "slide" else V
            t = (pts - p) @ u
            r = float(np.linalg.norm((pts - p) - np.outer(t, u), axis=1).max())
            t0, t1 = float(t.min()), float(t.max())
            if ax["dof"] == "stem":
                t1 += scaled()["PULL"]
            ends = np.array([p + t0 * u, p + t1 * u])
            ext = r * np.sqrt(np.clip(1.0 - u * u, 0.0, 1.0))
            lo = np.minimum(lo, ends.min(axis=0) - ext)
            hi = np.maximum(hi, ends.max(axis=0) + ext)
        lo, hi = lo - CROP_MARGIN, hi + CROP_MARGIN
        boxes.append(m3.Manifold.cube([float(x) for x in hi - lo]).translate([float(x) for x in lo]))
    out = []
    n0 = n1 = 0
    region = m3.Manifold.batch_boolean(boxes, m3.OpType.Add) if len(boxes) > 1 else boxes[0]
    for b in bodies:
        if b["kind"] == "fixed" and b["name"] == "fixed":
            n0 = int(b["solid"].num_tri())
            b = dict(b, solid=b["solid"] ^ region)
            n1 = int(b["solid"].num_tri())
        out.append(b)
    return out, n0, n1


def write_world(folder, bodies, meta):
    """bodies (build_world) into folder: world.json and one .npz (float32 vertices, uint32 triangles) per body."""
    import numpy as np
    os.makedirs(folder, exist_ok=True)
    rows = []
    for i, b in enumerate(bodies):
        mesh = b["solid"].to_mesh()
        f = "body_%02d.npz" % i
        np.savez(os.path.join(folder, f), verts=np.asarray(mesh.vert_properties, np.float32)[:, :3],
                 tris=np.asarray(mesh.tri_verts, np.uint32))
        r = {k: v for k, v in b.items() if k != "solid"}
        if r["rest"] is not None and math.isinf(r["rest"]):
            r["rest"] = "+inf" if r["rest"] > 0 else "-inf"
        r["file"] = f
        rows.append(r)
    with open(os.path.join(folder, "world.json"), "w") as fh:
        json.dump({"bodies": rows, "meta": meta, "scale": S}, fh, indent=1, default=str)


def read_world(folder):
    """(defs in A's make_world format, {body name: manifold3d.Manifold}, meta) from write_world's folder."""
    import numpy as np
    import manifold3d as m3
    with open(os.path.join(folder, "world.json")) as fh:
        doc = json.load(fh)
    defs, parts = [], {}
    for r in doc["bodies"]:
        z = np.load(os.path.join(folder, r["file"]))
        man = m3.Manifold(m3.Mesh(vert_properties=z["verts"], tri_verts=z["tris"]))
        parts[r["name"]] = man
        rest = r["rest"]
        if isinstance(rest, str):
            rest = math.inf if rest == "+inf" else -math.inf
        d = {"name": r["name"], "parts": [r["name"]], "kind": r["kind"]}
        if r["kind"] != "fixed":
            d.update(dof=r["dof"], point=tuple(r["point"]), direction=tuple(r["direction"]), rest=rest,
                     carrier=r["carrier"])
        defs.append(d)
    return defs, parts, doc["meta"]
