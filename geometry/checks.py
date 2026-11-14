"""Gates G1-G5, the 19 checks and the score, exactly as SPEC.md 0.1 states them.
Used by the grader only. The tools use core, contract and measure, never this file."""
import math
import signal
import numpy as np
from scipy import ndimage
import manifold3d as m3
from . import constants as C
from . import bodies as B
from . import core
from . import measure
from .core import FormatError, apply, translation, ivol, union, box
from .contract import load_assembly, check_contract, replay


class _Timeout(Exception):
    pass


def _run(fn, timeout):
    """Each check in its own try block: exception, timeout or non-finite number fails it."""
    def handler(signum, frame):
        raise _Timeout()
    old = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, timeout)
    try:
        ok, info = fn()
        for v in info.values():
            if isinstance(v, float) and not math.isfinite(v):
                return False, dict(info, error="non-finite number")
        return bool(ok), info
    except _Timeout:
        return False, {"error": "timeout"}
    except BaseException as e:                      # noqa: a failed check, never a crash
        if isinstance(e, KeyboardInterrupt):
            raise
        return False, {"error": "%s: %s" % (type(e).__name__, e)}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


class World:
    """Everything placed in its final pose."""
    def __init__(self, base, door, paths):
        sup = B.supplied()
        self.base, self.door = base, door
        self.printed = union([base, door])
        self.board, self.lid = sup["board"], sup["lid"]
        self.battery_local = sup["battery"]
        self.paths = paths
        self.T_batt = paths["battery"][-1]
        self.battery = apply(self.battery_local, self.T_batt)
        self.local = {"board": self.board, "lid": self.lid, "battery": self.battery_local, "door": door}
        self.final = {"base": base, "board": self.board, "lid": self.lid, "battery": self.battery, "door": door}
        self.pcb = B.pcb()
        self.comps = B.components()


# ---------------- gates ----------------
def g2(w):
    lo, hi = np.array(C.ENVELOPE[0]), np.array(C.ENVELOPE[1])
    worst = 0.0
    for part in (w.base, w.door):
        V = core.verts(part)
        worst = max(worst, float(np.max(np.maximum(lo - V, V - hi))))
    return worst <= C.ENVELOPE_TOL, {"max_outside": worst}


def g3(w):
    names = list(w.final)
    worst, pair = 0.0, None
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = ivol(w.final[names[i]], w.final[names[j]])
            if v > worst:
                worst, pair = v, names[i] + "/" + names[j]
    return worst <= C.VOL_TOL, {"worst_volume": worst, "pair": pair}


def g4(w):
    msgs = check_contract(w.paths, w.local, B.envelope_box())
    return not msgs, {"messages": msgs}


def g5(w):
    nearest = measure.enclosure_reach(w.final.values(), union([w.board, w.battery]))
    return nearest >= C.G5_NEAR, {"outside_reaches_within": nearest}


# ---------------- checks ----------------
def _path(w, name, placed):
    def fn():
        r = replay(w.local[name], w.paths[name], {k: w.final[k] for k in placed})
        return r["worst_volume"] <= C.VOL_TOL, r
    return fn


def f1(w):
    sec = w.printed.slice(-F1Z)
    areas = []
    for x, y in C.HOLES:
        ring = (m3.CrossSection.circle(C.F1_RING_DIA / 2, 128) - m3.CrossSection.circle(C.HOLE_DIA / 2, 128)).translate([x, y])
        areas.append(float((sec ^ ring).area()))
    return sum(a >= C.F1_AREA for a in areas) >= C.F1_MIN_HOLES, {"areas": areas}


F1Z = C.F1_GAP / 2


def f2(w):
    vols = {}
    for label, d in (("+X", (1, 0, 0)), ("-X", (-1, 0, 0)), ("+Y", (0, 1, 0)), ("-Y", (0, -1, 0)), ("-Z", (0, 0, -1))):
        vols[label] = ivol(apply(w.pcb, translation(np.array(d) * C.F2_MOVE)), w.printed)
    return all(v > C.VOL_TOL for v in vols.values()), {"volumes": vols}


def f3(w):
    others = union([w.base, w.door, w.board, w.lid])
    vols = {}
    for label, d in (("+X", (1, 0, 0)), ("-X", (-1, 0, 0)), ("+Y", (0, 1, 0)), ("-Y", (0, -1, 0)),
                     ("+Z", (0, 0, 1)), ("-Z", (0, 0, -1))):
        vols[label] = ivol(apply(w.battery, translation(np.array(d) * C.F3_MOVE)), others)
    return all(v > C.VOL_TOL for v in vols.values()), {"volumes": vols}


def f4(w):
    gaps = {k: core.min_distance(c, w.printed, C.F4_CLEAR + 1.0) for k, c in w.comps.items()}
    return all(g >= C.F4_CLEAR - 1e-6 for g in gaps.values()), {"gaps": gaps}


def f5(w):
    up = float(w.T_batt[2, 2])
    sx, sy, sz = C.BATTERY_SIZE
    if up > 1 - 1e-6:
        slab = box((0, 0, sz), (sx, sy, sz + C.F5_SWELL))
    elif up < -1 + 1e-6:
        slab = box((0, 0, -C.F5_SWELL), (sx, sy, 0))
    else:
        return False, {"error": "battery large face is not horizontal"}
    v = ivol(apply(slab, w.T_batt), union([w.base, w.door, w.board, w.lid]))
    return v <= C.VOL_TOL, {"volume_in_swell_space": v}


def f6(w):
    p = w.T_batt[:3, :3] @ np.array(C.BATTERY_LEAD_CENTRE) + w.T_batt[:3, 3]
    d = float(np.linalg.norm(p - np.array(C.J4_CENTRE)))
    return d <= C.F6_LEAD, {"distance": d}


def _keepout(w, name):
    def fn():
        v = ivol(B.keepouts()[name], w.printed)
        return v <= C.VOL_TOL, {"volume": v}
    return fn


def _window(w, plane_x, sec2d):
    def fn():
        solid = core.section_x(w.printed, plane_x)
        open_area = float((sec2d(C.K_GROW_OUTER) - solid).area())
        limit = float(sec2d(C.K_GROW_INNER).area())
        return open_area <= limit, {"open_area": open_area, "limit": limit}
    return fn


def _wall(part):
    def fn():
        n, dev_mm = measure.wall_opening(part)
        return n == 1 and dev_mm <= C.W_DEV, {"pieces": n, "max_deviation": dev_mm}
    return fn


def s1(w):
    v = ivol(apply(w.door, translation((0, 0, C.S1_MOVE))), w.base)
    return v > C.VOL_TOL, {"volume": v}


def s2(w):
    v = ivol(apply(w.lid, translation((0, 0, -C.S2_MOVE))), w.base)
    return v > C.VOL_TOL, {"volume": v}


def m1(w):
    v = float(w.base.volume() + w.door.volume())
    if C.REFERENCE_VOLUME is None:
        return False, {"volume": v, "error": "reference volume not set"}
    budget = C.MATERIAL_FACTOR * C.REFERENCE_VOLUME
    return v <= budget, {"volume": v, "budget": budget}


def score(gates, checks):
    G = 1
    for g in C.GATES:
        G *= 1 if gates.get(g) else 0
    total = sum(C.WEIGHTS.values())
    p = sum(wt for k, wt in C.WEIGHTS.items() if checks.get(k)) / total
    strict = all(checks.get(k) for k in C.WEIGHTS)
    return G * (0.5 * p * p + 0.5 * (1 if strict else 0)), p, bool(G and strict)


def grade(base_path, door_path, assembly_path, timeout=C.CHECK_TIMEOUT_S):
    """Returns {"reward", "p", "strict", "gates", "checks", "details"}. Never raises."""
    gates = {g: False for g in C.GATES}
    checks = {k: False for k in C.WEIGHTS}
    details = {}

    def result():
        S, p, strict = score(gates, checks)
        return {"reward": S, "p": p, "strict": strict, "gates": gates, "checks": checks, "details": details}

    state = {}

    def load():
        state["base"] = core.load_part(base_path, C.MAX_TRIANGLES, C.MAX_STL_BYTES, C.SELF_UNION_TOL)
        state["door"] = core.load_part(door_path, C.MAX_TRIANGLES, C.MAX_STL_BYTES, C.SELF_UNION_TOL)
        return True, {}
    gates["G1"], details["G1"] = _run(load, timeout)
    if not gates["G1"]:
        return result()

    def loadj():
        state["paths"] = load_assembly(assembly_path)
        state["world"] = World(state["base"], state["door"], state["paths"])
        return True, {}
    ok, info = _run(loadj, timeout)
    if not ok:
        details["G4"] = info
        return result()
    w = state["world"]

    for g, fn in (("G2", g2), ("G3", g3), ("G4", g4), ("G5", g5)):
        gates[g], details[g] = _run(lambda fn=fn: fn(w), timeout)

    table = {
        "A1": _path(w, "board", ("base",)),
        "A2": _path(w, "lid", ("base", "board")),
        "A3": _path(w, "battery", ("base", "board", "lid")),
        "A4": _path(w, "door", ("base", "board", "lid", "battery")),
        "F1": lambda: f1(w), "F2": lambda: f2(w), "F3": lambda: f3(w), "F4": lambda: f4(w),
        "F5": lambda: f5(w), "F6": lambda: f6(w),
        "K1": _keepout(w, "J1"), "K2": _keepout(w, "J2"),
        "K3": _window(w, C.J1_WALL_PLANE_X, B.j1_section_2d),
        "K4": _window(w, C.J2_WALL_PLANE_X, B.j2_section_2d),
        "W1": _wall(w.base), "W2": _wall(w.door),
        "S1": lambda: s1(w), "S2": lambda: s2(w), "M1": lambda: m1(w),
    }
    for k, fn in table.items():
        checks[k], details[k] = _run(fn, timeout)
    return result()
