"""NOT-FOR-AGENT (realcad test material; never copy into a task image).

Run the keyless acceptance test (AT-0 to AT-6) on a real movement's own keyless works.

    python -I grade_real.py SUB_DIR DATA_DIR [--details OUT.json] [--staged] [--wind-sense S] [--pull P]
    python -I grade_real.py SUB_DIR DATA_DIR --probe

Imports spikes/keyless/grade.py and engine.py unchanged and overrides, in this process only, the
movement constants with the real movement's own (REAL below: case, barrel axis, minute-wheel axis,
winding sense); DATA_DIR holds the real movement's plate, bridges, wound barrel member and minute
wheel (written by convert_ml01.py). Since the engine fixes (branch a/keyless-engine-fixes) everything
else is native: carriers other than the stem, the declared pull, the fit rule, phasing at rest.

Runs serially in this process (grade.grade(jobs=1)): no fork, no spawn.
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


def probe(sub, data):
    """Rest overlaps before and after the rig's phase, and where a forward and a backward 30 deg turn go
    with the mainspring off (barrel as a free part)."""
    spec, parts, sup, defs = G.load(sub, data)
    w = G.make_world(parts, sup, defs)
    out = {"rest_pen_as_submitted": {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}}
    w.phase()
    out["after_phase_moves"] = {n: round(b.q, 5) for n, b in w.bodies.items() if abs(b.q) > 1e-9}
    out["after_phase_pen"] = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
    G._set_kind(w, "barrel", "contact")
    snap = w.snapshot()
    for tag, deg in (("forward_30", C.FORWARD * 30), ("backward_30", -C.FORWARD * 30)):
        w.restore(snap)
        s0 = G._state(w)
        bl = G._turn(w, deg)
        s1 = G._state(w)
        out[tag] = {"blocked": bl, "moves_deg": {k: round(math.degrees(s1[k] - s0[k]), 3) for k in s0}}
    return out


def staged(sub, data, details):
    """grade.grade(jobs=1), phase by phase, printing and saving each result as it lands."""
    out = {"overrides": {k: getattr(C, k) for k in list(REAL) + ["WIND_SENSE", "PULL"]}, "steps": {}}

    def dump(tag, val):
        out[tag] = val
        print(tag, json.dumps(val, default=str)[:3000], flush=True)
        if details:
            json.dump(out, open(details, "w"), indent=1, default=str)

    t0 = time.time()
    spec, parts, sup, defs = G.load(sub, data)
    out["declared_pull"] = G.pull_of(spec)
    w = G.make_world(parts, sup, defs)
    raw = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
    w.phase()
    pens = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
    rest = all(v <= E.TOL for v in pens.values())
    bok, bdet = G.bounds_check(spec, parts)
    held = G.held_check(parts, sup, defs)
    hok = all(v["ok"] for v in held.values())
    dump("assemble", {"rest_ok": rest, "rest_overlap_as_submitted": raw, "rest_overlap": pens,
                      "settle_moves": {n: round(b.q, 5) for n, b in w.bodies.items() if abs(b.q) > 1e-9},
                      "bounds_ok": bok, "bounds": bdet, "held_ok": hok,
                      "held_failures": {k: v for k, v in held.items() if not v["ok"]},
                      "ok": rest and bok and hok, "seconds": round(time.time() - t0, 1)})
    out["steps"]["assemble"] = rest and bok and hok
    loaded = {"spec": spec, "parts": parts, "sup": sup}
    ph, r, err = G.worker(("wind", loaded, defs, None))
    dump("wind", r if err is None else {"error": err, "ok": False})
    ph, first, err = G.worker(("first", loaded, defs, None))
    if err:
        dump("first_error", err)
        return
    state = first.pop("state")
    dump("hold", first["hold"])
    dump("run", first["run"])
    for phase in ("backward", "set", "return"):
        ph, r, err = G.worker((phase, loaded, defs, state))
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
    ap.add_argument("--wind-sense", type=float, default=1.0)
    ap.add_argument("--hold-steps", type=int, default=None, help="override HOLD_STEPS (a longer AT-2 hold)")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--staged", action="store_true")
    a = ap.parse_args()
    apply(dict(REAL, WIND_SENSE=a.wind_sense))
    if a.hold_steps:
        apply({"HOLD_STEPS": a.hold_steps})
    sub, data = os.path.abspath(a.sub), os.path.abspath(a.data)
    if a.probe:
        print(json.dumps(probe(sub, data), indent=1))
        return
    if a.staged:
        staged(sub, data, a.details)
        return
    t = time.time()
    product, gates, conds, steps, det = G.grade(sub, data, jobs=1)
    out = {"product": product, "gates": gates, "conditions": conds, "steps": steps,
           "at": {C.AT_IDS[k]: v for k, v in steps.items()}, "details": det, "seconds": round(time.time() - t, 1)}
    if a.details:
        json.dump(out, open(a.details, "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("product", "gates", "conditions", "at", "seconds")}))


if __name__ == "__main__":
    main()
