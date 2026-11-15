"""Instance H2: gates, checks and score. Grader only; never shipped to the agent."""
import numpy as np
from . import core
from . import h2_public as P
from .core import apply, translation, ivol, union, box
from .contract import replay
from .checks import _run

WEIGHTS = {
    "path_A": 3, "path_B": 2, "path_battery": 1, "path_speaker": 1, "path_lid": 1,
    "supported_A": 1, "supported_B": 1, "supported_battery": 1, "supported_speaker": 1,
    "located_A": 1,
    "keepout_J1": 1, "keepout_J2": 1, "keepout_J3": 1,
    "battery_swell": 1, "battery_lead": 1,
    "wall": 1, "lid_seated": 1,
}
GATES = ("files", "final_pose", "contract", "enclosed")
W_STRUCT, W_SIZE = 0.3, 0.7
CHECK_TIMEOUT_S = 120


def size_term(volume):
    if P.V_REF is None:
        return 0.0
    return float(np.clip((P.V_ZERO - volume) / (P.V_ZERO - P.V_REF), 0.0, 1.0))


def score(gates, checks, volume):
    G = all(gates.get(g) for g in GATES)
    total = sum(WEIGHTS.values())
    p = sum(w for k, w in WEIGHTS.items() if checks.get(k)) / total
    allp = all(checks.get(k) for k in WEIGHTS)
    q = size_term(volume) if (volume is not None and allp) else 0.0
    return (W_STRUCT * p * p + W_SIZE * q) if G else 0.0, p, q


class World:
    def __init__(self, base, lid, order, paths):
        self.base, self.lid, self.order, self.paths = base, lid, order, paths
        self.printed = union([base, lid])
        self.lo, self.hi = P.printed_bbox(base, lid)
        self.volume = float(np.prod(self.hi - self.lo))
        self.local = {n: P.body(n) for n in P.BODY_NAMES}
        self.local["lid"] = lid
        self.T = {n: paths[n][-1] for n in P.BODY_NAMES}
        self.final = {n: apply(self.local[n], self.T[n]) for n in P.BODY_NAMES}
        self.everything = dict(self.final, base=base, lid=lid)

    def others(self, name):
        return union([m for k, m in self.everything.items() if k != name])

    def posed(self, owner, man):
        return apply(man, self.T[owner])


def g_final(w):
    names = list(w.everything)
    worst, pair = 0.0, None
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = ivol(w.everything[names[i]], w.everything[names[j]])
            if v > worst:
                worst, pair = v, names[i] + "/" + names[j]
    return worst <= P.VOL_TOL, {"worst_volume": worst, "pair": pair}


def g_contract(w):
    msgs = P.contract_messages(w.paths, w.local, w.lo, w.hi)
    return not msgs, {"messages": msgs}


def g_enclosed(w):
    plugs = [w.posed(o, m) for o, m in P.plugs().values()]
    d = P.enclosure_depth(w.everything.values(), plugs, w.lo, w.hi)
    return d <= P.ENCLOSE_DEPTH, {"deepest_outside_ball": d}


def c_path(w, name):
    def fn():
        placed = {"base": w.base}
        seq = w.order + ["lid"]
        for n in seq[:seq.index(name)]:
            placed[n] = w.final[n]
        r = replay(w.local[name], w.paths[name], placed)
        return r["worst_volume"] <= P.VOL_TOL, r
    return fn


def c_supported(w, name):
    def fn():
        v = ivol(apply(w.final[name], translation((0, 0, -P.SUPPORT_MOVE))), w.others(name))
        return v > P.VOL_TOL, {"volume": v}
    return fn


def c_located(w):
    pcb = w.posed("A", P.sub_parts()["A_pcb"][1])
    others = w.others("A")
    vols = {}
    for label, d in (("+X", (1, 0, 0)), ("-X", (-1, 0, 0)), ("+Y", (0, 1, 0)), ("-Y", (0, -1, 0)), ("-Z", (0, 0, -1))):
        vols[label] = ivol(apply(pcb, translation(np.array(d) * P.LOCATE_MOVE)), others)
    return all(v > P.VOL_TOL for v in vols.values()), {"volumes": vols}


def c_keepout(w, name):
    def fn():
        owner, prism = P.keepouts()[name]
        ko = w.posed(owner, prism)
        v = ivol(ko, w.printed) + sum(ivol(ko, m) for k, m in w.final.items())
        far = w.T[owner][:3, :3] @ np.array(P.keepout_far_centres()[name][1]) + w.T[owner][:3, 3]
        outside = bool(np.any(far < w.lo) or np.any(far > w.hi))
        return v <= P.VOL_TOL and outside, {"volume": v, "far_end_outside_box": outside}
    return fn


def c_swell(w):
    T = w.T["battery"]
    sx, sy, sz = P.BATTERY_SIZE
    up = float(T[2, 2])
    if up > 1 - 1e-6:
        slab = box((0, 0, sz), (sx, sy, sz + P.SWELL))
    elif up < -1 + 1e-6:
        slab = box((0, 0, -P.SWELL), (sx, sy, 0))
    else:
        return False, {"error": "battery large face is not horizontal"}
    v = ivol(apply(slab, T), w.others("battery"))
    return v <= P.VOL_TOL, {"volume_in_swell_space": v}


def c_lead(w):
    a = w.T["battery"][:3, :3] @ np.array(P.BATTERY_LEAD_CENTRE) + w.T["battery"][:3, 3]
    b = w.T["A"][:3, :3] @ np.array(P.J4_CENTRE) + w.T["A"][:3, 3]
    d = float(np.linalg.norm(a - b))
    return d <= P.LEAD_MAX, {"distance": d}


def c_wall(w):
    n, dev = P.wall_opening(w.base)
    return n == 1 and dev <= P.W_DEV, {"pieces": n, "max_deviation": dev}


def c_lid(w):
    v = ivol(apply(w.lid, translation((0, 0, -0.2))), w.base)
    return v > P.VOL_TOL, {"volume": v}


def grade(base_path, lid_path, assembly_path, timeout=CHECK_TIMEOUT_S):
    gates = {g: False for g in GATES}
    checks = {k: False for k in WEIGHTS}
    details = {}
    st = {"volume": None}

    def result():
        S, p, q = score(gates, checks, st["volume"])
        return {"reward": S, "p": p, "size_term": q, "bbox_volume": st["volume"],
                "strict": bool(S >= 1.0 - 1e-9), "gates": gates, "checks": checks, "details": details}

    def load():
        base, lid = P.load_base(base_path), P.load_lid(lid_path)
        order, paths = P.load_assembly(assembly_path)
        st["w"] = World(base, lid, order, paths)
        st["volume"] = st["w"].volume
        return True, {"bbox_volume": st["volume"]}
    gates["files"], details["files"] = _run(load, timeout)
    if not gates["files"]:
        return result()
    w = st["w"]
    for g, fn in (("final_pose", g_final), ("contract", g_contract), ("enclosed", g_enclosed)):
        gates[g], details[g] = _run(lambda fn=fn: fn(w), timeout)
    table = {"located_A": lambda: c_located(w), "battery_swell": lambda: c_swell(w), "battery_lead": lambda: c_lead(w),
             "wall": lambda: c_wall(w), "lid_seated": lambda: c_lid(w)}
    for n in list(P.BODY_NAMES) + ["lid"]:
        table["path_" + n] = c_path(w, n)
    for n in P.BODY_NAMES:
        table["supported_" + n] = c_supported(w, n)
    for n in ("J1", "J2", "J3"):
        table["keepout_" + n] = c_keepout(w, n)
    for k in WEIGHTS:
        checks[k], details[k] = _run(table[k], timeout)
    return result()
