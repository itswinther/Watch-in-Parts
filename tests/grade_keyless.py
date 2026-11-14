"""Part 5 (crown winding) of the one-job watch: workstream A's acceptance test AT-0 to AT-6, run on a world that
geometry/keyless_job.py wrote from a delivery. Run by tests/grade_watch.py in a fresh interpreter:
    python3 -I grade_keyless.py /abs/WORLD_DIR /abs/OUT.json [--force] [--jobs N]
A's engine and acceptance phases (spikes/keyless/engine.py, grade.py) are imported, not copied; their length
constants are set to B's scale from geometry/keyless_job.py SCALE_TABLE in this interpreter only. The phases run one
after another here (no fork after manifold's threads exist; Decisions 17:46, A 18:20). OUT.json is rewritten after
each phase, so a run stopped by the time limit keeps the phases it finished.
--force runs AT-1 to AT-6 even when the rest gate fails (diagnosis only; A's rule, used by the grader, skips them).
--jobs N > 1 runs the phases in N spawned interpreters (each holds the whole world in memory); the one-job grader
uses KEYLESS_JOBS (geometry/keyless_job.py).
Never runs submitted code; reads only WORLD_DIR."""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from geometry import keyless_job as KJ          # noqa: E402

E = G = None
STATE = {}


def setup(world_dir):
    """Import A's engine and grade modules, scale them (KJ.apply_to_engine), load the world and point A's `load` at
    it. Returns (defs, parts, meta)."""
    global E, G
    E = KJ._import_a("engine")
    G = KJ._import_a("grade")
    KJ.apply_to_engine(E, G)
    defs, parts, meta = KJ.read_world(world_dir)
    G.load = lambda sub, data: (None, parts, {}, defs)      # A's worker phases rebuild the world from these
    STATE.update(defs=defs, parts=parts, meta=meta)
    return defs, parts, meta


def _init(world_dir):           # spawned workers (--jobs)
    setup(world_dir)


def _phase(args):
    phase, start = args
    return G.worker((phase, (None, None), STATE["defs"], start))


def assemble(defs, parts, meta):
    """AT-0 as A's grade() computes it: files (loaded by the parent), rest overlap, held, bounds (B's frame)."""
    det, gates, conds = {}, {"files": True, "rest": False}, {"held": False, "bounds": False}
    try:
        w = G.make_world(parts, {}, defs)
        pens = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
        det["rest_overlap"] = pens
        det["rest_tol"] = E.TOL
        gates["rest"] = all(v <= E.TOL for v in pens.values())
    except Exception as e:  # noqa: BLE001
        det["rest"] = "%s: %s" % (type(e).__name__, e)
    try:
        h = G.held_check(parts, {}, defs)
        det["held"] = h
        conds["held"] = all(v["ok"] for v in h.values())
    except Exception as e:  # noqa: BLE001
        det["held"] = "%s: %s" % (type(e).__name__, e)
    ok, d = meta["bounds"]
    conds["bounds"], det["bounds"] = bool(ok), d
    return gates, conds, det


def main(argv):
    opts = [a for a in argv if a.startswith("--")]
    args = [a for a in argv if not a.startswith("--") and not a.isdigit()]
    world, out = args[0], args[1]
    jobs = 1
    if "--jobs" in argv:
        jobs = int(argv[argv.index("--jobs") + 1])
    t0 = time.time()
    res = {"steps": {}, "sequence": {}, "phases_done": [], "started": t0}

    def save():
        res["seconds"] = round(time.time() - t0, 1)
        tmp = out + ".tmp"
        with open(tmp, "w") as f:
            json.dump(res, f, indent=1, default=str)
        os.replace(tmp, out)
    try:
        defs, parts, meta = setup(world)
        C = G.C
        res["constants"] = {"scale": KJ.S, "scaled": KJ.scaled(), "wind_sense": C.WIND_SENSE,
                            "grader_version": C.GRADER_VERSION, "step_weights": C.STEP_WEIGHTS,
                            "engine": {"TOL": E.TOL, "RELAX_MAX": E.RELAX_MAX, "SCAN_ARC": E.SCAN_ARC,
                                       "MAX_STEP_TRAVEL": E.MAX_STEP_TRAVEL, "MU": E.MU,
                                       "settle_budget": E.World.settle.__defaults__[0],
                                       "main_try_arc": E.World.step.__defaults__[2]},
                            "unscaled": KJ.UNSCALED}
        res["bodies"] = {d["name"]: {"kind": d["kind"], "dof": d.get("dof"), "triangles": int(parts[d["name"]].num_tri())}
                         for d in defs}
        gates, conds, det = assemble(defs, parts, meta)
        res.update(gates=gates, conditions=conds, assemble=det)
        res["steps"]["assemble"] = gates["files"] and gates["rest"] and conds["held"] and conds["bounds"]
        res["phases_done"].append("assemble")
        save()
        force = "--force" in opts
        if not gates["rest"] and not force:
            res["sequence_skipped"] = "rest overlap above TOL: AT-1 to AT-6 not run (A's rule)"
        else:
            res["forced"] = force and not gates["rest"]
            seq = res["sequence"]

            def record(ph, o, err):
                if ph == "first":
                    if err is None:
                        STATE["start"] = o.pop("state")
                        seq.update({k: o[k] for k in ("hold", "run")})
                    else:
                        seq["hold"] = seq["run"] = {"error": err, "ok": False}
                else:
                    seq[ph] = o if err is None else {"error": err, "ok": False}
                res["phases_done"].append(ph)
                save()
            if jobs <= 1:
                for ph in ("wind", "first"):
                    record(*G.worker((ph, (None, None), defs, None)))
                for ph in ("backward", "set", "return"):
                    if "start" not in STATE:
                        record(ph, None, "not run: AT-2 did not finish")
                        continue
                    record(*G.worker((ph, (None, None), defs, STATE["start"])))
            else:
                import multiprocessing as mp
                from concurrent.futures import ProcessPoolExecutor
                with ProcessPoolExecutor(max_workers=jobs, mp_context=mp.get_context("spawn"), initializer=_init,
                                         initargs=(world,)) as ex:
                    fw = ex.submit(_phase, ("wind", None))
                    record(*ex.submit(_phase, ("first", None)).result())
                    futs = [ex.submit(_phase, (ph, STATE["start"])) for ph in ("backward", "set", "return")] \
                        if "start" in STATE else []
                    record(*fw.result())
                    for f in futs:
                        record(*f.result())
        for k in C.STEPS[1:]:
            try:
                res["steps"][k] = bool(res["sequence"][k]["ok"])
            except Exception:  # noqa: BLE001
                res["steps"][k] = False
        res["at"] = {C.AT_IDS[k]: v for k, v in res["steps"].items()}
        res["done"] = True
    except Exception as e:  # noqa: BLE001
        res["error"] = "%s: %s" % (type(e).__name__, e)
    save()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
