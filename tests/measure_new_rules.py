"""Measure the three new rules (light, seated, tolerant) on a reference folder through the existing engine,
exactly as written in the orchestrator's brief, before the check code exists.
    python3 tests/measure_new_rules.py /abs/OUT [STAGES]     e.g. 123 or 4
Stages 1 to 3: volumes, worst same-mobile overlap, unseated parts, each mesh at -0.03, 0, +0.03.
Stage 4: assembly replay with parts of the same mobile tested against each other too."""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from geometry import watch as W
from geometry.core import ivol, union

MOVE, SHIFT = W.HELD_MOVE, W.MESH_SHIFT


def volumes(m):
    fv = sum(p.volume() for p in m.fixed_parts.values())
    mv = sum(p.volume() for k, mm in m.mobiles.items() if k != "barrel" for p in mm["parts"].values())
    return fv, mv


def same_mobile(m):
    worst, unseated = (0.0, None), []
    for k, mm in m.mobiles.items():
        ps = mm["parts"]
        names = list(ps)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                v = ivol(ps[names[i]], ps[names[j]])
                if v > worst[0]:
                    worst = (v, "%s/%s" % (names[i], names[j]))
        if len(names) < 2:
            continue
        for n in names:
            rest = union([ps[o] for o in names if o != n])
            side = {lab: ivol(ps[n].translate(d), rest) for lab, d in
                    (("+x", [MOVE, 0, 0]), ("-x", [-MOVE, 0, 0]), ("+y", [0, MOVE, 0]), ("-y", [0, -MOVE, 0]))}
            up, down = ivol(ps[n].translate([0, 0, MOVE]), rest), ivol(ps[n].translate([0, 0, -MOVE]), rest)
            ok = all(v > W.VOL_TOL for v in side.values()) and max(up, down) > W.VOL_TOL
            if not ok:
                unseated.append((n, {k2: round(v, 4) for k2, v in side.items()}, round(up, 4), round(down, 4)))
            else:
                unseated_min = min(list(side.values()) + [max(up, down)])
                worst_seat[0] = min(worst_seat[0], (unseated_min, n))
    return worst, unseated


worst_seat = [(float("inf"), None)]


def shifted(m, name, dxy):
    """A shallow copy of m with mobile `name` moved by dxy (solid and axis)."""
    c = object.__new__(W.Movement)
    c.__dict__.update(m.__dict__)
    c.mobiles = dict(m.mobiles)
    mm = dict(m.mobiles[name])
    mm["solid"] = mm["solid"].translate([dxy[0], dxy[1], 0])
    mm["axis"] = (mm["axis"][0] + dxy[0], mm["axis"][1] + dxy[1])
    c.mobiles[name] = mm
    return c


def tolerant(m):
    rows = []
    for a, ta, b, tb in m.meshes:
        A, B = m.mobiles[a]["axis"], m.mobiles[b]["axis"]
        d = math.hypot(B[0] - A[0], B[1] - A[1])
        u = ((B[0] - A[0]) / d, (B[1] - A[1]) / d)
        row = {"pair": "%s/%s" % (a, b)}
        for lab, s in (("-0.03", -SHIFT), ("0", 0.0), ("+0.03", SHIFT)):
            r = shifted(m, b, (u[0] * s, u[1] * s)).mesh_run(a, ta, b, tb)
            ok = W.Movement.mesh_passes(r)
            row[lab] = (round(r["worst_volume"], 5), round(r["largest_gap"], 4), round(r["smallest_drive_overlap"], 4), ok)
        rows.append(row)
        print("   mesh", row, flush=True)
    return rows


def stage4(folder):
    m = W.load_movement(folder)
    order, paths = W.load_assembly(folder, m)
    res, installed = m.assembly_replay(order, paths)
    bad = {n: (r["worst_volume"], r["hit"], r["format_messages"]) for n, r in res.items() if n not in installed}
    print("stage 4 all-pairs replay: installed %d of %d; not installed: %s" % (len(installed), len(m.all_parts()), bad))


def main(out, stages):
    for st in stages:
        folder = os.path.join(out, "stage%d" % st)
        if st == 4:
            stage4(folder)
            continue
        m = W.load_movement(folder)
        fv, mv = volumes(m)
        worst_seat[0] = (float("inf"), None)
        worst, uns = same_mobile(m)
        print("stage %d: fixed volume %.1f, mobile volume %.1f; worst same-mobile overlap %.5f (%s); unseated %s; "
              "smallest seated overlap %s" % (st, fv, mv, worst[0], worst[1], uns or "none", worst_seat[0]), flush=True)
        rows = tolerant(m)
        print("stage %d tolerant: %s" % (st, "all pass" if all(r[k][3] for r in rows for k in ("-0.03", "0", "+0.03"))
                                         else "FAIL " + str([r["pair"] for r in rows if not all(r[k][3] for k in ("-0.03", "0", "+0.03"))])),
              flush=True)


if __name__ == "__main__":
    main(sys.argv[1], [int(c) for c in (sys.argv[2] if len(sys.argv) > 2 else "1234")])
