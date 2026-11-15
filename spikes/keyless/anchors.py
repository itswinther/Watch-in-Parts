"""Anchors and the exploit hunt: the reference, deliberate faults, and attempts to beat the grader
without real work. Each has the reward it must get.

    python anchors.py WORK_DIR [PARALLEL] [ONLY_PREFIX] [--quick] [--early-stop]

--quick: the reference once plus the faster anchors (skips the reference repeats and the honesty anchors
that re-grade the reference). For iterating only; validate a merge with the full run.
--early-stop: a "<=" anchor stops grading once its bound can no longer be exceeded (reported as ok with
early-stop). Never applied to "=" anchors. For iterating only; never for validating a merge.
Lines are printed as anchors finish, then a summary line.

Builds each variant (reference.build() options, then optional edits to the written submission),
grades it with `python -I grade.py`, and prints one line per anchor with ok or FAIL. Exit 0 when all ok.
Run it inside the grading container (see README): it is heavy.
"""
import json
import math
import os
import shutil
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reference as R  # noqa: E402
import constants as C  # noqa: E402

def sc(*ks):
    """Product when exactly these steps pass (each scored on its own, plus the whole-build term)."""
    v = (1 - C.W_WHOLE) * sum(C.STEP_WEIGHTS[k] for k in ks) + (C.W_WHOLE if set(ks) == set(C.STEPS) else 0.0)
    return round(v, 6)


# ---------- edits applied to a written submission ----------
def edit_json(fn):
    def f(d):
        p = os.path.join(d, "keyless.json")
        j = json.load(open(p))
        fn(j)
        with open(p, "w") as fh:
            json.dump(j, fh, indent=1, allow_nan=True)
    return f


def fuse(j):
    m = j["mobiles"]
    m["stem"]["parts"] += m.pop("sliding_pinion")["parts"] + m.pop("winding_pinion")["parts"]


def axis_off(j):
    p = j["mobiles"]["crown_wheel"]["point"]
    j["mobiles"]["crown_wheel"]["point"] = [p[0] + 0.2, p[1], p[2]]


def nan_point(j):
    j["mobiles"]["crown_wheel"]["point"] = [float("nan"), 0, 0]


def huge_point(j):
    j["mobiles"]["crown_wheel"]["point"] = [1e30, 0, 0]


def click_fixed(j):
    j["fixed"] += j["mobiles"].pop("click")["parts"]


def click_free(j):
    j["mobiles"]["click"]["kind"] = "free"
    j["mobiles"]["click"].pop("rest", None)


def named_fixed(j):
    j["mobiles"]["fixed"] = j["mobiles"].pop("click")


def supplied_spring(j):
    j["mobiles"]["click"]["parts"] = ["minute_post"]


def report(fn):
    def f(d):
        p = os.path.join(d, "report.json")
        fn(d, p)
    return f


def rep_all_pass(d, p):
    json.dump({"steps": {k: "pass" for k in C.STEPS}, "summary": "all good"}, open(p, "w"))


def rep_not_tested(d, p):
    json.dump({"steps": {k: "not_tested" for k in C.STEPS}, "summary": "not tested"}, open(p, "w"))


def rep_malformed(d, p):
    open(p, "w").write("{steps: pass all")


def rep_symlink(d, p):
    os.remove(p)
    os.symlink(os.path.join(d, "keyless.json"), p)


def rep_missing(d, p):
    os.remove(p)


def rep_bad_claim(d, p):
    json.dump({"steps": {k: "probably" for k in C.STEPS}, "summary": "x"}, open(p, "w"))


def only_stem(j):
    j["mobiles"] = {"stem": j["mobiles"]["stem"], "barrel": j["mobiles"]["barrel"]}
    j["fixed"] = []


def drop_click_and_setting(j):
    for m in ("click", "setting_wheel"):
        j["mobiles"].pop(m, None)
    j["fixed"] = [f for f in j["fixed"] if f not in ("click_post", "setting_post")]


def drop_setting(j):
    j["mobiles"].pop("setting_wheel", None)
    j["fixed"] = [f for f in j["fixed"] if f != "setting_post"]


def free_slider_with_pusher(d):
    """The sliding pinion declared a free part, returned towards the winding pinion by a separate sprung
    pusher ring on its outer face (a yoke-spring stand-in): exercises 'carried parts yield first' and
    'springs push free parts'."""
    import shapes as S
    p = os.path.join(d, "keyless.json")
    j = json.load(open(p))
    sp = j["mobiles"]["sliding_pinion"]
    sp["kind"] = "free"
    sp.pop("rest", None)
    S.write_stl(os.path.join(d, "parts", "pusher.stl"),
                S.cyl_x(0, 0, 3.92, 4.2, 0.8, 64) - S.cyl_x(0, 0, 3.8, 4.3, 0.5, 64))
    j["mobiles"]["pusher"] = {"kind": "spring", "dof": "slide", "direction": [1, 0, 0], "rest": -1,
                              "parts": ["pusher"]}
    with open(p, "w") as fh:
        json.dump(j, fh, indent=1)


def symlink_part(d):
    p = os.path.join(d, "parts", "click.stl")
    os.remove(p)
    os.symlink(os.path.join(d, "parts", "stem.stl"), p)


def open_mesh(d):
    p = os.path.join(d, "parts", "click.stl")
    data = open(p, "rb").read()
    n = struct.unpack_from("<I", data, 80)[0]
    with open(p, "wb") as fh:
        fh.write(data[:80] + struct.pack("<I", n - 1) + data[84:84 + 50 * (n - 1)])


ANCHORS = [
    # (name, build options or None for an empty folder, post-edit, want, how[, field]); "le" bounds name the
    # steps expected to pass at most
    ("reference", {}, None, 1.0, "eq"),
    ("reference, repeat 2", {}, None, 1.0, "eq"),
    ("reference, repeat 3", {}, None, 1.0, "eq"),
    ("stop early: only the stem and the barrel wheel", {}, edit_json(only_stem), sc("assemble"), "le"),
    ("stop early: reference without the click and the setting train", {}, edit_json(drop_click_and_setting),
     sc("assemble", "wind", "return"), "le"),
    ("do nothing (empty folder)", None, None, 0.0, "eq"),
    ("skip the hardest step: everything except the setting train (AT-5)", {}, edit_json(drop_setting),
     sc(*[k for k in C.STEPS if k != "set"]), "le"),
    ("Breguet teeth symmetric (ramps both ways): cannot wind", {"breguet_steep": 0.5}, None,
     sc("assemble", "hold"), "le"),
    ("no click", {"click": False}, None, sc("assemble", "wind", "return"), "le"),
    ("click present, ratchet rim without teeth", {"no_ratchet_teeth": True}, None, sc("assemble", "wind", "return"),
     "le"),
    ("winding too slow: 13 crown turns per barrel turn (crown 9 / barrel 39 teeth)", {"zs_crown": 9, "zb": 39}, None,
     sc(*[k for k in C.STEPS if k != "wind"]), "le"),
    ("winding works brake the barrel (square dog teeth instead of Breguet)", {"breguet_square": True}, None,
     sc("assemble", "wind", "set", "return"), "le"),
    ("free sliding pinion + sprung pusher, Breguet teeth symmetric: still cannot wind",
     {"breguet_steep": 0.5}, free_slider_with_pusher, sc("assemble", "hold"), "le"),
    ("free sliding pinion + sprung pusher, square dog teeth: still brakes the barrel",
     {"breguet_square": True}, free_slider_with_pusher, sc("assemble", "wind", "set", "return"), "le"),
    ("free sliding pinion + sprung pusher, proper Breguet teeth (control: reported, not a bound)", {},
     free_slider_with_pusher, 1.0, "le"),
    ("sliding pinion's spur teeth 0.15 further out: meet the setting wheel before the Breguet teeth let go",
     {"teeth_shift": 0.15}, None, sc(*[k for k in C.STEPS if k != "backward"]), "le"),
    ("yoke stroke too small (counterbore 0.6 deeper: the pinion is dragged only 0.15)", {"cbore_end": 3.6}, None,
     sc(*[k for k in C.STEPS if k != "set"]), "le"),
    ("sliding pinion spring pointing the wrong way", {"rest_sign_slider": 1}, None, sc("assemble", "hold"), "le"),
    ("crown wheel 0.1 off its declared axis (caught at rest)", {"shift": {"crown_wheel": (0.1, 0.0, 0.0)}}, None, 0.0, "eq"),
    ("X barrel wheel drawn 0.05 into its neighbours (overlap at rest, not phasable)",
     {"shift": {"barrel_wheel": (0.0, -0.05, 0.0)}}, None, 0.0, "eq"),
    # ----- exploit hunt -----
    ("X nothing engages (no Breguet or setting teeth)", {"no_teeth": True}, None, sc("assemble", "hold"), "le"),
    ("X stem, sliding pinion and winding pinion fused into one mobile", {}, edit_json(fuse), sc("assemble", "wind"), "le"),
    ("X crown wheel axis declared 0.2 off its geometry", {}, edit_json(axis_off), sc("assemble", "hold", "set"), "le"),
    ("X NaN in a declared axis point", {}, edit_json(nan_point), 0.0, "eq"),
    ("X declared axis point at 1e30", {}, edit_json(huge_point), sc("assemble", "hold"), "le"),
    ("X a part file is a symbolic link", {}, symlink_part, 0.0, "eq"),
    ("X a part mesh with one triangle missing (open)", {}, open_mesh, 0.0, "eq"),
    ("X click a 0.002-thick sliver (passes through)", {"sliver_click": True}, None, sc("assemble", "wind", "return"), "le"),
    ("X click declared fixed (a permanent brake): holds, but cannot wind", {}, edit_json(click_fixed),
     sc("assemble", "hold"), "le"),
    ("X click declared free, no spring: the rig's taps in AT-2 move it out", {}, edit_json(click_free),
     sc(*[k for k in C.STEPS if k not in ("hold", "run")]), "le"),
    ("X click spring pointing away from the ratchet", {"rest_sign_click": -1}, None, sc("assemble", "wind", "return"), "le"),
    ("X a mobile named 'fixed' (shadowing the grader's body)", {}, edit_json(named_fixed), 0.0, "eq"),
    ("X a supplied part declared as a spring", {}, edit_json(supplied_spring), 0.0, "eq"),
    ("X fine Breguet teeth (32 teeth, 0.04 high): skip between steps", {"breguet_n": 32, "breguet_h": 0.04}, None,
     sc("assemble", "hold", "set", "return"), "le"),
    # ----- report.json (honesty) -----
    ("H no click, report claims every step passed (overclaim)", {"click": False}, report(rep_all_pass), 0.0, "eq",
     "honesty"),
    ("H reference, report says not_tested everywhere", {}, report(rep_not_tested), 0.5, "eq", "honesty"),
    ("H reference, malformed report", {}, report(rep_malformed), 0.0, "eq", "honesty"),
    ("H reference, report is a symbolic link", {}, report(rep_symlink), 0.0, "eq", "honesty"),
    ("H reference, no report", {}, report(rep_missing), 0.0, "eq", "honesty"),
    ("H reference, report with an invalid claim word", {}, report(rep_bad_claim), 0.0, "eq", "honesty"),
    ("H reference, no report: reward", {}, report(rep_missing), C.W_PRODUCT / (C.W_PRODUCT + C.W_HONESTY), "eq",
     "reward"),
]


EARLY_STOP = False


def quick_skip(name):
    return name.startswith("reference, repeat") or name.startswith("H reference")


def run(i):
    name, opts, post, want, how = ANCHORS[i][:5]
    field = ANCHORS[i][5] if len(ANCHORS[i]) > 5 else "product"
    early = EARLY_STOP and how == "le" and field == "product"
    d = os.path.join(WORK, "a%02d" % i)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    if opts is not None:
        parts, spec = R.build(opts)
        R.write(d, parts, spec)
        if post:
            post(d)
    rw = os.path.join(d, "reward.txt")
    dt = os.path.join(d, "details.json")
    p = subprocess.run([sys.executable, "-I", os.path.join(HERE, "grade.py"), d, os.path.join(HERE, "data"),
                        "--reward", rw, "--details", dt, "--jobs", os.environ.get("ANCHOR_JOBS", "3")]
                       + (["--stop-at-or-below", repr(want)] if early else []), capture_output=True, text=True)
    failed, secs, got = [], "-", float(open(rw).read())
    if os.path.exists(dt):
        j = json.load(open(dt))
        got = float(j.get(field, got))
    elif field == "honesty":
        got = 0.0
    ok = abs(got - want) < 1e-6 if how == "eq" else got <= want + 1e-6
    if os.path.exists(dt):
        failed = [k for k, v in {**j["gates"], **j.get("conditions", {}), **j.get("steps", j.get("counted", {}))}.items()
                  if not v]
        secs = j.get("seconds")
        es = j.get("details", {}).get("early_stop")
        if es:
            secs = "%s, early-stop: not run %s" % (secs, ",".join(es["not_run"]))
    return ok, "%-4s %-100s %s=%.4f want %s %.4f failed: %s (%ss)" % (
        "ok" if ok else "FAIL", name, field, got, "=" if how == "eq" else "<=", want, ",".join(failed) or "-", secs)


if __name__ == "__main__":
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    unknown = flags - {"--quick", "--early-stop"}
    if unknown:
        sys.exit("unknown option(s): %s" % ", ".join(sorted(unknown)))
    EARLY_STOP = "--early-stop" in flags
    WORK = os.path.abspath(args[0])
    par = int(args[1]) if len(args) > 1 else 2
    only = args[2] if len(args) > 2 else None
    idx = [i for i, a in enumerate(ANCHORS) if only is None or a[0].startswith(only)]
    if "--quick" in flags:
        idx = [i for i in idx if not quick_skip(ANCHORS[i][0])]
    shard = os.environ.get("SHARD")              # "i/n": run every n-th anchor starting at i
    if shard:
        si, sn = (int(x) for x in shard.split("/"))
        idx = [i for k, i in enumerate(idx) if k % sn == si]
    print("# anchors: %d of %d%s%s, %d at a time" % (len(idx), len(ANCHORS), " (quick)" if "--quick" in flags else "",
          " (early-stop)" if EARLY_STOP else "", par), flush=True)
    res = []
    with ThreadPoolExecutor(par) as ex:
        futs = {ex.submit(run, i): i for i in idx}
        for f in as_completed(futs):
            try:
                ok, line = f.result()
            except Exception as e:  # noqa: BLE001
                ok, line = False, "ERROR %s: %r" % (ANCHORS[futs[f]][0], e)
            res.append(ok)
            print(line, flush=True)
    print("# %d of %d ok" % (sum(res), len(res)), flush=True)
    sys.exit(0 if all(res) else 1)
