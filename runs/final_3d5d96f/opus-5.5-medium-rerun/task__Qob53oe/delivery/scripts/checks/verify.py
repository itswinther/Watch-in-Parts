import json, math, sys, time, itertools
import numpy as np
from vlib import *

build = sys.argv[1] if len(sys.argv) > 1 else "movement.json"
what = set(sys.argv[2:]) or {"static", "mesh", "global", "retain", "case", "hands"}
doc = json.load(open(os.path.join(DEL, build)))
period = 8.0 if build == "movement.json" else 6.0
names = list(doc["fixed"]) + [p for m in doc["mobiles"].values() for p in m["parts"]]
t0 = time.time()
P = load_parts(names)
print("loaded %d parts in %.1fs" % (len(P), time.time() - t0), flush=True)
BAR = barrel(doc["barrel"])
C = tuple(doc["case_centre"])
bodies = {"frame": kernel.union([P[n] for n in doc["fixed"]]), "barrel": BAR}
axis = {"barrel": (0.0, 0.0)}
for k, m in doc["mobiles"].items():
    bodies[k] = kernel.union([P[n] for n in m["parts"]])
    axis[k] = tuple(m["axis"])
R = rates(doc, period)
print("rates (turns/h, + = cw):", {k: round(v, 6) for k, v in R.items()})
for h, e in doc["hands"].items():
    print("  hand", h, e["mobile"], "rate", R[e["mobile"]], "period h", 1 / R[e["mobile"]] if R[e["mobile"]] else None)


def report_pair(a, b, A, B, lim=0.02):
    v = kernel.ivol(A, B)
    g = kernel.min_distance(A, B, 0.5) if v <= 1e-9 else 0.0
    flag = "" if (v <= 1e-6 and g >= lim) else "  <-- CHECK"
    return v, g, flag


if "static" in what:
    print("== joined parts inside each body")
    groups = {"frame": list(doc["fixed"])}
    for k, m in doc["mobiles"].items():
        groups[k] = m["parts"]
    for g, ps in groups.items():
        for a, b in itertools.combinations(ps, 2):
            if not kernel.bbox_overlap(P[a], P[b], 0.05):
                continue
            v = kernel.ivol(P[a], P[b])
            d = kernel.min_distance(P[a], P[b], 0.1) if v < 1e-9 else 0
            print("  %s: %s/%s ivol %.5f gap %.4f" % (g, a, b, v, d))
    print("== between bodies (nominal)")
    for a, b in itertools.combinations(bodies, 2):
        A, B = bodies[a], bodies[b]
        if not kernel.bbox_overlap(A, B, 0.1):
            continue
        v, g, flag = report_pair(a, b, A, B)
        if g < 0.2 or v > 0:
            print("  %-14s %-14s ivol %.6f gap %.4f%s" % (a, b, v, g, flag), flush=True)

if "case" in what:
    allv = []
    for n, man in list(P.items()) + [("barrel", BAR)]:
        v = kernel.verts(man)
        allv.append(v)
        r = np.hypot(v[:, 0] - C[0], v[:, 1] - C[1]).max()
        if r > 12.6:
            print("  case radius: %s %.4f" % (n, r))
    V = np.concatenate(allv)
    print("== height %.4f (z %.4f .. %.4f), max radius %.4f" % (V[:, 2].max() - V[:, 2].min(), V[:, 2].min(), V[:, 2].max(),
                                                         np.hypot(V[:, 0] - C[0], V[:, 1] - C[1]).max()))

if "mesh" in what:
    print("== rotation of every mesh pair through two tooth pitches")
    for e in doc["meshes"]:
        a, b = e["driver"], e["driven"]
        A, B = bodies[a], bodies[b]
        pitch_a = 2 * math.pi / e["driver_teeth"]
        worst_v, worst_g = 0.0, 9.0
        for t in np.linspace(0, 2 * pitch_a, 41):
            # driver turns by -t (cw positive rate convention irrelevant here), driven opposite at ratio
            ang_a = t
            ang_b = -t * e["driver_teeth"] / e["driven_teeth"]
            AA = rotz(A, ang_a, axis[a]); BB = rotz(B, ang_b, axis[b])
            v = kernel.ivol(AA, BB)
            g = kernel.min_distance(AA, BB, 0.3) if v <= 1e-9 else 0
            worst_v = max(worst_v, v); worst_g = min(worst_g, g)
        print("  %-13s(%3d) -> %-13s(%3d): max ivol %.6f min gap %.4f%s" % (a, e["driver_teeth"], b, e["driven_teeth"],
              worst_v, worst_g, "" if worst_v < 1e-6 and worst_g >= 0.02 else "  <-- CHECK"), flush=True)

if "global" in what:
    print("== whole train at random times: all body pairs")
    rng = np.random.default_rng(1)
    for trial in range(int(os.environ.get("NTRIAL", "6"))):
        th = rng.uniform(0, 2 * math.pi)       # barrel angle (math, ccw)
        cur = {"frame": bodies["frame"]}
        for k in bodies:
            if k == "frame":
                continue
            ang = -th * R[k] / R["barrel"]  # same sense convention for all
            cur[k] = rotz(bodies[k], ang, axis[k])
        bad = []
        for a, b in itertools.combinations(cur, 2):
            if not kernel.bbox_overlap(cur[a], cur[b], 0.05):
                continue
            v = kernel.ivol(cur[a], cur[b])
            g = kernel.min_distance(cur[a], cur[b], 0.05) if v <= 1e-9 else 0
            if v > 1e-6 or g < 0.02:
                bad.append((a, b, round(v, 6), round(g, 4)))
        print("  trial", trial, "problems:", bad, flush=True)

if "retain" in what:
    print("== retention of each mobile by the frame (free travel before touching the frame)")
    F = bodies["frame"]
    for k in list(doc["mobiles"]) + ["barrel"]:
        M = bodies[k]
        out = []
        for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            hit = None
            for s_ in np.arange(0.005, 1.0001, 0.005):
                if kernel.ivol(M.translate([d[0] * s_, d[1] * s_, d[2] * s_]), F) > 1e-7:
                    hit = s_; break
            out.append(">1.0" if hit is None else "%.3f" % hit)
        print("  %-13s +x %s -x %s +y %s -y %s +z %s -z %s" % (k, *out), flush=True)

if "hands" in what:
    print("== hands")
    hand_parts = {e["part"] for e in doc["hands"].values() if e}
    zmin_h = min(kernel.verts(P[p])[:, 2].min() for p in hand_parts)
    # every non-hand part above the lowest hand bottom?
    for n, man in P.items():
        if n in hand_parts:
            continue
        v = kernel.verts(man)
        hi = v[v[:, 2] > zmin_h - 0.3]
        if len(hi):
            print("  part %s reaches z %.4f (lowest hand %.4f); radius of that region about its axis:" % (n, v[:, 2].max(), zmin_h))
    for h, e in doc["hands"].items():
        v = kernel.verts(P[e["part"]]); a = axis[e["mobile"]]
        L = np.hypot(v[:, 0] - a[0], v[:, 1] - a[1]).max()
        print("  %s: length %.3f z %.4f..%.4f axis dist from centre %.3f" % (h, L, v[:, 2].min(), v[:, 2].max(), math.dist(a, C)))
    # sweep each hand through a full turn against every other body (other bodies fixed)
    for h, e in doc["hands"].items():
        H = P[e["part"]]; a = axis[e["mobile"]]
        others = [k for k in bodies if k != e["mobile"]]
        worst = 9
        for ang in np.linspace(0, 2 * math.pi, 73)[:-1]:
            HH = rotz(H, ang, a)
            for k in others:
                if not kernel.bbox_overlap(HH, bodies[k], 0.05):
                    continue
                v = kernel.ivol(HH, bodies[k])
                g = kernel.min_distance(HH, bodies[k], 0.1) if v <= 1e-9 else 0
                worst = min(worst, g)
                if g < 0.02:
                    print("   hand %s at %.0f deg vs %s: ivol %.5f gap %.4f" % (h, math.degrees(ang), k, v, g))
        print("  hand %s sweep min gap to other bodies %.4f" % (h, worst))
print("done in %.1fs" % (time.time() - t0))
