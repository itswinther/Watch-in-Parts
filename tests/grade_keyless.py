"""Part 5 (crown winding) of the one-job watch: workstream A's acceptance test AT-0 to AT-6, run on a world that
geometry/keyless_job.py wrote from a delivery. Run by tests/grade_watch.py in a fresh interpreter, in its own process
group (grade_watch.keyless_run kills the whole group on a timeout, so no spawned worker outlives it):
    python3 -I grade_keyless.py /abs/WORLD_DIR /abs/OUT.json [--force] [--jobs N]
A's engine and acceptance phases (spikes/keyless/engine.py, grade.py) are imported, not copied; their length
constants are set to B's scale from geometry/keyless_job.py SCALE_TABLE in this interpreter only. The rig's fit rule
(A's grade.relieve_fits, which A's own loader applies) is applied to the world's bodies here, as A's load() does.
Each step's result is recorded as soon as its phase ends and OUT.json is rewritten after every phase, so a run
stopped by the time limit, or a phase whose worker crashed, keeps every phase that finished.
--force runs AT-1 to AT-6 even when the rest gate fails (diagnosis only; A's rule, used by the grader, skips them).
--jobs N > 1 runs the phases in spawned interpreters, at most N at a time, each phase in its own (no fork after
manifold's threads exist; one worker's crash fails only its own phase). Each holds the whole world in memory; the
one-job grader uses KEYLESS_JOBS (geometry/keyless_job.py).
--test-fault PHASE:crash|hang (tests/test_job_grader.py only): that phase's worker exits at once, or never returns.
Never runs submitted code; reads only WORLD_DIR."""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from geometry import keyless_job as KJ          # noqa: E402

E = G = None
STATE = {}
FAULT = {}                  # tests only: {phase: "crash" | "hang"}
LATER = ("backward", "set", "return")           # phases that start from the state at the end of AT-2


def setup(world_dir):
    """Import A's engine and grade modules, scale them (KJ.apply_to_engine), load the world, apply the rig's fit rule
    (A's relieve_fits) and point A's `load` at it. Returns (defs, parts, meta)."""
    global E, G
    E = KJ._import_a("engine")
    G = KJ._import_a("grade")
    KJ.apply_to_engine(E, G)
    defs, parts, meta = KJ.read_world(world_dir)
    fits = G.relieve_fits(parts, {}, defs)      # in place, as A's load() does for files
    # A's worker reads (spec, parts, sup, defs) from load() for a path, or (spec, parts, sup) from a dict; spec and
    # sup are empty dicts (no keyless.json: pull_of gives the scaled PULL; B's plates are in the fixed body)
    G.load = lambda sub, data: ({}, parts, {}, defs)
    STATE.update(defs=defs, parts=parts, meta=meta, fits=fits, loaded={"spec": {}, "parts": parts, "sup": {}})
    return defs, parts, meta


def _fault(phase):
    mode = FAULT.get(phase)
    if mode == "crash":
        os._exit(70)
    if mode == "hang":
        while True:
            time.sleep(60)


def run_phase(phase, start):
    """One of A's phases on this interpreter's world: (phase, out, error)."""
    _fault(phase)
    return G.worker((phase, STATE["loaded"], STATE["defs"], start))


def _init(world_dir, fault):           # spawned workers (--jobs)
    FAULT.update(fault)
    setup(world_dir)


def _phase(args):
    return run_phase(*args)


def assemble(defs, parts, meta):
    """AT-0 as A's grade() computes it: files (loaded by the parent), rest overlap once the rig has let the movement
    come to rest (World.phase), held, bounds (B's frame). Held covers every free and spring body, the free going-train
    bodies and, when it is free, the minute mobile (A's held_check skips the body named minute_wheel, which in A's own
    job is a supplied part on a supplied post; here it is the delivery's)."""
    det, gates, conds = {}, {"files": True, "rest": False}, {"held": False, "bounds": False}
    try:
        w = G.make_world(parts, {}, defs)
        det["rest_overlap_as_submitted"] = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
        w.phase()
        det["rest_settle_moves"] = {n: round(b.q, 6) for n, b in w.bodies.items()
                                    if b.kind != "fixed" and abs(b.q) > 1e-9}
        pens = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
        det["rest_overlap"] = pens
        det["rest_tol"] = E.TOL
        gates["rest"] = all(v <= E.TOL for v in pens.values())
    except Exception as e:  # noqa: BLE001
        det["rest"] = "%s: %s" % (type(e).__name__, e)
    try:
        held_name = "minute_mobile"
        hdefs = [dict(d, name=held_name) if d["name"] == KJ.MINUTE and meta.get("minute_free") else d for d in defs]
        h = G.held_check(parts, {}, hdefs)
        if held_name in h:
            h[KJ.MINUTE] = h.pop(held_name)
        det["held"] = h
        conds["held"] = all(v["ok"] for v in h.values())
    except Exception as e:  # noqa: BLE001
        det["held"] = "%s: %s" % (type(e).__name__, e)
    ok, d = meta["bounds"]
    conds["bounds"], det["bounds"] = bool(ok), d
    return gates, conds, det


def run_parallel(world, jobs, record):
    """A's phases in spawned interpreters, at most `jobs` at a time, each phase in its own executor, so a worker that
    crashes (killed for memory, a segfault) fails its own phase only. wind and first start at once; backward, set and
    return start from first's end state."""
    import multiprocessing as mp
    from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
    ctx = mp.get_context("spawn")
    queue = [("wind", None), ("first", None)]
    running = {}
    try:
        while queue or running:
            while queue and len(running) < jobs:
                ph, st = queue.pop(0)
                ex = ProcessPoolExecutor(max_workers=1, mp_context=ctx, initializer=_init, initargs=(world, dict(FAULT)))
                running[ex.submit(_phase, (ph, st))] = (ph, ex)
            done, _ = wait(list(running), return_when=FIRST_COMPLETED)
            for f in done:
                ph, ex = running.pop(f)
                try:
                    r = f.result()
                except Exception as e:  # noqa: BLE001  (BrokenProcessPool: the worker died)
                    r = (ph, None, "worker failed: %s: %s" % (type(e).__name__, e))
                ex.shutdown(wait=True)
                queue += record(*r)
    finally:
        for f, (ph, ex) in running.items():
            ex.shutdown(wait=False, cancel_futures=True)


def main(argv):
    opts = [a for a in argv if a.startswith("--")]
    vals = {argv[i + 1] for i, a in enumerate(argv[:-1]) if a in ("--jobs", "--test-fault")}
    args = [a for a in argv if not a.startswith("--") and a not in vals]
    world, out = args[0], args[1]
    jobs = int(argv[argv.index("--jobs") + 1]) if "--jobs" in argv else 1
    if "--test-fault" in argv:
        ph, mode = argv[argv.index("--test-fault") + 1].split(":")
        FAULT[ph] = mode
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
                            "engine": {"TOL": E.TOL, "FORCE_EPS": E.FORCE_EPS, "RELAX_MAX": E.RELAX_MAX,
                                       "SCAN_ARC": E.SCAN_ARC, "MAX_STEP_TRAVEL": E.MAX_STEP_TRAVEL, "MU": E.MU,
                                       "MAIN_TRY": E.MAIN_TRY, "SPRING_PUSH_ARC": E.SPRING_PUSH_ARC,
                                       "spring_push": E.World.spring_push,
                                       "phase_budget": E.World.phase.__defaults__[0]},
                            "unscaled": list(KJ.UNSCALED)}
        res["fits_relieved"] = STATE["fits"]
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
            skip = meta.get("setting_not_run")      # B's minute rule (geometry/keyless_job.py SETTING_STEPS)

            def record(ph, o, err):
                """Store phase ph's result and its steps' pass or fail now, write OUT.json, and return the phases
                that may start now [(phase, start state)]."""
                more = []
                if ph == "first":
                    if err is None:
                        STATE["start"] = o.pop("state")
                        seq.update({k: o[k] for k in ("hold", "run")})
                    else:
                        seq["hold"] = {"error": err, "ok": False}
                        seq["run"] = {"error": err, "ok": False}
                    for k in ("hold", "run"):
                        res["steps"][k] = bool(seq[k].get("ok"))
                else:
                    seq[ph] = o if err is None else {"error": err, "ok": False}
                    res["steps"][ph] = bool(seq[ph].get("ok"))
                res["phases_done"].append(ph)
                save()
                if ph == "first":
                    for p in LATER:
                        if p in KJ.SETTING_STEPS and skip:
                            more += record(p, None, skip)
                        elif "start" not in STATE:
                            more += record(p, None, "not run: AT-2 did not finish")
                        else:
                            more.append((p, STATE["start"]))
                return more
            if jobs <= 1:
                todo = [("wind", None), ("first", None)]
                while todo:
                    ph, st = todo.pop(0)
                    todo += record(*run_phase(ph, st))
            else:
                run_parallel(world, jobs, record)
        for k in C.STEPS[1:]:
            res["steps"].setdefault(k, False)
        res["at"] = {C.AT_IDS[k]: v for k, v in res["steps"].items()}
        res["done"] = True
    except Exception as e:  # noqa: BLE001
        res["error"] = "%s: %s" % (type(e).__name__, e)
    save()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
