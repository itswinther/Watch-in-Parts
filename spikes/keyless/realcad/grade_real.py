"""NOT-FOR-AGENT (realcad test material; never copy into a task image).

Run the keyless acceptance test (AT-0 to AT-6) on a real movement's own keyless works.

    python -I grade_real.py SUB_DIR DATA_DIR --details OUT.json [--jobs N] [--case R] [--wind-sense S]
    python -I grade_real.py SUB_DIR DATA_DIR --probe

It imports spikes/keyless/grade.py and engine.py unchanged and only overrides, in this process (and in
the forked workers):

- the movement constants (case, barrel axis, minute-wheel axis, winding sense) with the real
  movement's own (see REAL below; the stem axis is the grader's, the converter moves the CAD onto it);
- the supplied parts, by pointing DATA_DIR at the real movement's plate, bridges, wound barrel member
  and minute wheel (written by convert_ml01.py);
- one format extension the public keyless.json cannot express: a mobile may ride on a carrier other
  than the stem ("carrier": "<mobile>", e.g. a setting wheel on a swinging lever). engine.World already
  composes a carrier's rotation; RealWorld only extends the stem-only "a carrier answers for the bodies
  riding on it" rule (pen, budget) to any carrier.

realcad/ is test-only material: never copy it into a task image (build_task.py excludes it).
"""
import argparse
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
KEY = os.path.dirname(HERE)
sys.path.insert(0, KEY)
import numpy as np  # noqa: E402
import constants as C  # noqa: E402
import engine as E  # noqa: E402
import grade as G  # noqa: E402

# Marco Lang ml01 (Zweigesicht-1), in the grader frame (CAD z + 1.9; the CAD's stem axis is y = 0, z = -1.9)
REAL = {
    "CASE_CENTRE": (0.0, 0.0),        # movement centre
    "CASE_RADIUS": 17.0,              # main plate radius 16.98 mm
    "CASE_Z": (-4.0, 4.0),            # the movement's own thickness, both dial sides of the Zweigesicht
    "BARREL_AXIS": (6.2, 8.1),        # barrel I: its drum is the wound member (the crown wheel meshes the drum)
    "MINUTE_AXIS": (4.2429, 0.246),   # minute wheel (Wechselrad 1) on its post
}


def apply(over):
    for k, v in over.items():
        setattr(C, k, v)


class RealWorld(E.World):
    """engine.World with the carrier rule generalised from the stem to any carrier."""

    def pen(self, b, q=None, only=None):
        kids = self.children(b) if b.dof != "stem" else []
        if not kids:
            return super().pen(b, q, only)
        old = b.q
        if q is not None:
            b.q = q
        try:
            v = self._pen1(b, None, only)
            for k in kids:
                v = max(v, self._pen1(k, None, only))
            return v
        finally:
            b.q = old

    def budget(self, b, among):
        best = super().budget(b, among)
        if b.dof == "stem":
            return best
        for k in self.children(b):
            # a pushed carrier also clears what its riders touch; travel at the rider's contact point
            # converted to the carrier's coordinate (the rider turns about its own axis, carried)
            for o in among:
                if o is b or o is k:
                    continue
                v = self.posed(k) ^ self.posed(o)
                if v.volume() <= 0.5 * E.TOL:
                    continue
                for comp in v.decompose():
                    if comp.volume() <= 0.05 * E.TOL:
                        continue
                    pts = np.asarray(comp.to_mesh().vert_properties, float)[:, :3]
                    if not len(pts):
                        continue
                    c = pts.mean(axis=0)
                    t = self.travel(o, c) + self.travel(b, c)
                    if t <= 0:
                        continue
                    if b.dof == "rot":
                        best = max(best, E.K * t / max(self._axis_dist(b.point, b.dir, c), 0.05))
                    else:
                        best = max(best, E.K * t)
        return best


_orig_load = G.load


def load(sub, data):
    spec, parts, sup, defs = _orig_load(sub, data)
    for d in defs:
        mob = spec["mobiles"].get(d["name"])
        if mob and mob.get("carrier"):
            c = mob["carrier"]
            if c not in spec["mobiles"] or c in ("stem", "barrel") or spec["mobiles"][c].get("dof") != "rot":
                raise G.FormatError("mobile %s: carrier must be another rot mobile" % d["name"])
            d["carrier"] = c
    return spec, parts, sup, defs


def make_world(parts, sup, defs, shift=None):
    bodies = []
    for d in defs:
        ms = [sup[p[1:]] if p.startswith("@") else parts[p] for p in d["parts"]]
        man = G.union(ms)
        if shift and d["name"] == shift[0]:
            man = man.translate(list(shift[1]))
        bodies.append(E.Body(d["name"], man, d["kind"], dof=d.get("dof"), point=d.get("point"),
                             direction=d.get("direction"), rest=d.get("rest"), carrier=d.get("carrier")))
    return RealWorld(bodies)


G.load = load
G.make_world = make_world


def probe(sub, data):
    """Facts the keyless.json needs from the geometry: the overlaps at rest, which way each spring part
    must be urged to touch its partner, and which way forward crown turns drive the barrel."""
    spec, parts, sup, defs = load(sub, data)
    w = make_world(parts, sup, defs)
    out = {"rest_pen": {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}}
    for n, b in w.bodies.items():
        if b.kind != "spring":
            continue
        res = {}
        for sgn in (1, -1):
            q0 = b.q
            free = 0.0
            for i in range(1, 41):
                d = sgn * b.coord_from_arc(0.01 * i)
                if w.pen(b, q0 + d) > E.TOL:
                    break
                free = 0.01 * i
            res[sgn] = free
        out.setdefault("spring_free_travel_mm", {})[n] = res
    w.settle()
    out["after_settle_pen"] = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
    G._set_kind(w, "barrel", "contact")          # no mainspring: just see where forward turns go
    s0 = G._state(w)
    bl = G._turn(w, C.FORWARD * 30)
    s1 = G._state(w)
    out["forward_30"] = {"blocked": bl, "moves_deg": {k: round(math.degrees(s1[k] - s0[k]), 3) for k in s0}}
    w.restore({k: (v, 0.0) for k, v in s0.items()})
    s0 = G._state(w)
    bl = G._turn(w, -C.FORWARD * 30)
    s1 = G._state(w)
    out["backward_30"] = {"blocked": bl, "moves_deg": {k: round(math.degrees(s1[k] - s0[k]), 3) for k in s0}}
    return out


def staged(sub, data, details):
    """The same static checks and worker phases as grade.grade(), run one after another in this process
    (low memory), writing the details file after every phase so partial results survive."""
    out = {"overrides": {k: getattr(C, k) for k in list(REAL) + ["WIND_SENSE", "PULL"]}, "steps": {}}

    def dump(tag, val):
        out[tag] = val
        print(tag, json.dumps(val, default=str)[:3000], flush=True)
        if details:
            json.dump(out, open(details, "w"), indent=1, default=str)

    t0 = time.time()
    spec, parts, sup, defs = load(sub, data)
    w = make_world(parts, sup, defs)
    pens = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
    rest = all(v <= E.TOL for v in pens.values())
    bok, bdet = G.bounds_check(spec, parts)
    held = G.held_check(parts, sup, defs)
    hok = all(v["ok"] for v in held.values())
    dump("assemble", {"rest_ok": rest, "rest_overlap": pens, "bounds_ok": bok, "bounds": bdet, "held_ok": hok,
                      "held_failures": {k: v for k, v in held.items() if not v["ok"]},
                      "ok": rest and bok and hok, "seconds": round(time.time() - t0, 1)})
    out["steps"]["assemble"] = rest and bok and hok
    ph, r, err = G.worker(("wind", (sub, data), defs, None))
    dump("wind", r if err is None else {"error": err, "ok": False})
    ph, first, err = G.worker(("first", (sub, data), defs, None))
    if err:
        dump("first_error", err)
        return
    state = first.pop("state")
    dump("hold", first["hold"])
    dump("run", first["run"])
    for phase in ("backward", "set", "return"):
        ph, r, err = G.worker((phase, (sub, data), defs, state))
        dump(phase, r if err is None else {"error": err, "ok": False})
    for k in C.STEPS[1:]:
        out["steps"][k] = bool(out.get(k, {}).get("ok", False))
    per = sum(C.STEP_WEIGHTS[k] for k in C.STEPS if out["steps"][k])
    whole = 1.0 if all(out["steps"].values()) else 0.0
    dump("summary", {"steps": out["steps"], "at": {C.AT_IDS[k]: v for k, v in out["steps"].items()},
                     "product": round((1 - C.W_WHOLE) * per + C.W_WHOLE * whole, 6),
                     "seconds": round(time.time() - t0, 1)})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sub")
    ap.add_argument("data")
    ap.add_argument("--details")
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--wind-sense", type=float, default=1.0)
    ap.add_argument("--pull", type=float, default=None,
                    help="position-2 pull (mm); default the brief's PULL. ml01's own is about 0.5 (jumper notches)")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--staged", action="store_true",
                    help="one process, the same checks as grade.grade(), each result printed as it lands")
    a = ap.parse_args()
    apply(dict(REAL, WIND_SENSE=a.wind_sense))
    if a.pull is not None:
        apply({"PULL": a.pull})
    sub, data = os.path.abspath(a.sub), os.path.abspath(a.data)
    t = time.time()
    if a.probe:
        print(json.dumps(probe(sub, data), indent=1))
        return
    if a.staged:
        staged(sub, data, a.details)
        return
    product, gates, conds, steps, det = G.grade(sub, data, a.jobs)
    out = {"product": product, "gates": gates, "conditions": conds, "steps": steps,
           "at": {C.AT_IDS[k]: v for k, v in steps.items()}, "overrides": {k: getattr(C, k) for k in list(REAL) + ["WIND_SENSE", "PULL"]},
           "details": det, "seconds": round(time.time() - t, 1)}
    if a.details:
        json.dump(out, open(a.details, "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("product", "gates", "conditions", "at", "seconds")}))


if __name__ == "__main__":
    main()
