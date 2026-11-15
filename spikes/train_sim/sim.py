"""Quasi-static contact simulation of a watch going train (verification / demo; not part of any grader).

Kinematics: the keyless contact engine (spikes/keyless/engine.py). The driver mobile is a `driven` body turned in
small steps; the driven mobile is a `contact` body the engine pushes the least distance that clears the overlap,
within its friction-cone budget (so a self-locking flank shows up as a blocked step = jam). Fixed parts (plate,
bridge, dial, cropped to the mesh zone) are obstacles.

Forces (added here; the engine itself has no forces): after every step the driven mobile is turned back by a few
microns into the driver, the overlap is split into contact patches, and for each patch
  point  = volume centroid of the patch,
  normal = -grad_x V(B translated by x)  (the area-weighted contact normal on the driven flank; central differences),
  weight = patch volume (a compliance proxy that shares load between teeth when two pairs touch at once).
Coulomb friction mu on each patch opposes the sliding of B relative to A (the sliding direction from the measured
step angles). Torque balance on the driver (given input torque) gives the force scale; the torque balance on the
driven mobile gives the transmitted torque. Jam = the engine cannot advance the step, or the solved normal force
(or the transmitted torque) is not positive.

Usage (in Docker): python spikes/train_sim/sim.py <design folder> <barrel.stl> <out.json> [--label NAME]
  [--steps-per-pitch N] [--pitches P] [--torque T] [--coupled-deg D]
"""
import argparse
import json
import math
import os
import sys
import time

import numpy as np
import manifold3d as m3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "spikes", "keyless"))

from geometry import watch, core  # noqa: E402
import engine as E  # noqa: E402

MU_SLIDING, MU_STATIC = 0.44, 0.51          # brass on steel, dry (spikes/keyless/constants.py)
MU_OILED = 0.15                             # a lubricated reference point (watch oil on steel/brass, order of magnitude)
PROBE_ARC = 0.004                           # mm: the driven mobile is turned back this far (at its pitch radius) to probe
GRAD_H = 0.0015                             # mm: translation step of the normal's central differences
ENGINE_TOL = 5e-5                           # mm^3: the engine's overlap tolerance (default 2e-4; finer for small pinions)


def vol_centroid(man):
    mesh = man.to_mesh()
    v = np.asarray(mesh.vert_properties, float)[:, :3]
    t = np.asarray(mesh.tri_verts, int)
    a, b, c = v[t[:, 0]], v[t[:, 1]], v[t[:, 2]]
    vol6 = np.einsum("ij,ij->i", a, np.cross(b, c))
    V = vol6.sum()
    if abs(V) < 1e-18:
        return v.mean(axis=0)
    return (vol6[:, None] * (a + b + c)).sum(axis=0) / (4.0 * V)


def rotz(man, ax, deg):
    return watch.rot_about(man, ax, deg) if deg else man


def going_path(m):
    """Meshes from the barrel to the seconds hand's mobile (BFS over declared meshes)."""
    sec = m.hands["seconds"][0]
    prev, q = {"barrel": None}, ["barrel"]
    while q:
        cur = q.pop(0)
        for i, (a, ta, b, tb) in enumerate(m.meshes):
            if a == cur and b not in prev:
                prev[b] = i
                q.append(b)
    path, cur = [], sec
    while prev[cur] is not None:
        i = prev[cur]
        path.append(i)
        cur = m.meshes[i][0]
    return [m.meshes[i] for i in path[::-1]]


def train_solid(m, name):
    """The mobile without its hands (hands do not touch the train; they would only shrink the engine's steps)."""
    mob = m.mobiles[name]
    if not mob["parts"]:
        return mob["solid"]
    hands = {p for (mm, p) in m.hands.values() if mm == name}
    ps = [s for n, s in mob["parts"].items() if n not in hands]
    return core.union(ps)


def patches(Ap, Bp):
    """Contact patches of posed solids Ap, Bp: [(volume, centroid, unit normal on B (force direction from A))]."""
    I = Ap ^ Bp
    if I.is_empty():
        return []
    out = []
    for comp in I.decompose():
        v = comp.volume()
        if v < 1e-9:
            continue
        bb = comp.bounding_box()
        g = 0.03
        box = core.box((bb[0] - g, bb[1] - g, bb[2] - g), (bb[3] + g, bb[4] + g, bb[5] + g))
        Ac, Bc = Ap ^ box, Bp ^ box
        grad = np.zeros(3)
        for k in range(3):
            d = [0.0, 0.0, 0.0]
            d[k] = GRAD_H
            vp = (Ac ^ Bc.translate(d)).volume()
            d[k] = -GRAD_H
            vm = (Ac ^ Bc.translate(d)).volume()
            grad[k] = (vp - vm) / (2 * GRAD_H)
        n = -grad
        nn = np.linalg.norm(n)
        if nn < 1e-12:
            continue
        out.append((v, vol_centroid(comp), n / nn))
    return out


def solve_mesh(pts, OA, OB, sA, sB, rate, T_in, mu):
    """Quasi-static forces of one mesh. pts: patches; rate = dthetaB/dthetaA (magnitude); T_in: torque on A
    (N mm, in A's forward sense). Returns dict or None (no contact)."""
    if not pts:
        return None
    wA, wB = sA * 1.0, sB * rate
    rows, denA, numB = [], 0.0, 0.0
    W = sum(p[0] for p in pts)
    for v, c, n in pts:
        w = v / W
        rA, rB = c[:2] - OA, c[:2] - OB
        vA = wA * np.array([-rA[1], rA[0], 0.0])
        vB = wB * np.array([-rB[1], rB[0], 0.0])
        vr = vB - vA
        vt = vr - (vr @ n) * n
        st = np.linalg.norm(vt)
        t = vt / st if st > 1e-9 else np.zeros(3)
        f = w * (n - mu * t)                        # force on B per unit lambda
        tA = -(rA[0] * f[1] - rA[1] * f[0])          # torque on A from -f
        tB = rB[0] * f[1] - rB[1] * f[0]
        denA += tA
        numB += tB
        rows.append((w, c, n, t, f))
    # equilibrium of A: T_in*sA + lam*denA = 0
    if abs(denA) < 1e-12:
        return {"jam": True, "why": "contact normal passes through the driver's axis"}
    lam = -T_in * sA / denA
    T_out = lam * numB * sB
    contacts = []
    for w, c, n, t, f in rows:
        N = lam * w
        contacts.append({"point": [round(float(x), 5) for x in c], "normal": [round(float(x), 4) for x in n],
                         "normal_force_n": round(float(N), 5), "friction_n": round(float(mu * abs(N)), 5),
                         "slide_dir": [round(float(x), 4) for x in t]})
    jam = lam <= 0 or T_out <= 0
    return {"jam": bool(jam), "T_out": float(T_out), "contacts": contacts,
            "max_normal_n": max(cc["normal_force_n"] for cc in contacts),
            "total_normal_n": float(lam),
            "axial_patches": sum(1 for cc in contacts if abs(cc["normal"][2]) > 0.5)}


def fixed_near(m, A, B, pad=0.3):
    bbA, bbB = A.bounding_box(), B.bounding_box()
    lo = [max(bbA[i], bbB[i]) - pad for i in range(3)]
    hi = [min(bbA[i + 3], bbB[i + 3]) + pad for i in range(3)]
    if any(lo[i] >= hi[i] for i in range(3)):
        return m3.Manifold()
    return m.fixed ^ core.box(tuple(lo), tuple(hi))


def run_pair(m, a, ta, b, tb, sA, solids, steps_per_pitch, pitches, T_in_nominal, log):
    """Drive mesh a->b over `pitches` driver tooth pitches in the engine; forces at every step."""
    axA, axB = m.mobiles[a]["axis"], m.mobiles[b]["axis"]
    A0, B0 = solids[a], solids[b]
    A2, B2 = watch._near_cut(A0, axA, B0, axB), watch._near_cut(B0, axB, A0, axA)
    if not (A2.is_empty() or B2.is_empty()):
        A0, B0 = A2, B2
    F = fixed_near(m, A0, B0)
    sB = -sA
    mod = 2.0 * math.hypot(axB[0] - axA[0], axB[1] - axA[1]) / (ta + tb)
    rpB = mod * tb / 2.0
    bodies = [E.Body("A", A0, "driven", dof="rot", point=(axA[0], axA[1], 0), direction=(0, 0, 1)),
              E.Body("B", B0, "contact", dof="rot", point=(axB[0], axB[1], 0), direction=(0, 0, 1))]
    if not F.is_empty():
        bodies.append(E.Body("fixed", F, "fixed"))
    W = E.World(bodies)
    t0 = time.time()
    init_pen = W.max_pen()
    W.settle(0.05)
    bA, bB = W.bodies["A"], W.bodies["B"]
    n = int(round(steps_per_pitch * pitches))
    dq = sA * (2 * math.pi / ta) / steps_per_pitch
    OA, OB = np.array(axA), np.array(axB)
    trace, jams, prevB = [], 0, bB.q
    probe = PROBE_ARC / rpB
    for i in range(n + 1):
        ok = True if i == 0 else W.step("A", dq)
        if not ok:
            jams += 1
        dB = bB.q - prevB
        prevB = bB.q
        rate = abs(dB / dq) if (i > 0 and ok and abs(dB) > 0) else ta / tb
        rate_valid = bool(i > 1 and ok and trace[-1]["touching"] and trace[-1]["engine_ok"])
        Ap = A0.transform(W.matrix(bA)[:3, :4].tolist())
        Bp = B0.transform(W.matrix(bB, bB.q - sB * probe)[:3, :4].tolist())
        pts = patches(Ap, Bp)
        res = {}
        for mu in (0.0, MU_OILED, MU_SLIDING, MU_STATIC):
            res[mu] = solve_mesh(pts, OA, OB, sA, sB, ta / tb if i == 0 else rate, T_in_nominal, mu)
        fpen = 0.0
        if "fixed" in W.bodies:
            fpen = max(W._pen1(bA, None, {"fixed"}), W._pen1(bB, None, {"fixed"}))
        rec = {"step": i, "angle_deg": {a: math.degrees(bA.q), b: math.degrees(bB.q)},
               "engine_ok": bool(ok), "rate": rate, "rate_valid": rate_valid, "ideal_rate": ta / tb, "fixed_overlap_mm3": fpen,
               "touching": bool(pts)}
        r = res[MU_SLIDING]
        if r is not None and "contacts" in r:
            rec["contacts"] = [dict(cc, pair="%s/%s" % (a, b)) for cc in r["contacts"]]
        for mu, rr in res.items():
            key = "mu%.2f" % mu
            if rr is None:
                rec[key] = None
            elif "contacts" not in rr:
                rec[key] = {"jam": True}
            else:
                eff = rr["T_out"] / (T_in_nominal * tb / ta)
                rec[key] = {"T_out_nmm": rr["T_out"], "eff": eff, "max_normal_n": rr["max_normal_n"],
                            "jam": rr["jam"], "n_contacts": len(rr["contacts"]),
                            "total_normal_n": rr["total_normal_n"], "axial_patches": rr["axial_patches"]}
        trace.append(rec)
        if i % max(1, steps_per_pitch // 4) == 0:
            r44 = rec.get("mu0.44") or {}
            log("  %s/%s step %d/%d ok=%s rate=%.4f (ideal %.4f) eff=%s N=%s pts=%d evals=%d t=%.0fs" % (
                a, b, i, n, ok, rate, ta / tb, ("%.3f" % r44["eff"]) if "eff" in r44 else "-",
                ("%.3f" % r44["max_normal_n"]) if "max_normal_n" in r44 else "-", len(pts), W.evals,
                time.time() - t0))
    return {"pair": "%s/%s" % (a, b), "driver_teeth": ta, "driven_teeth": tb, "module": mod,
            "T_in_nominal_nmm": T_in_nominal, "grader_force_n": T_in_nominal / (mod * ta / 2.0),
            "initial_overlap_mm3": init_pen, "engine_jams": jams, "engine_evals": W.evals,
            "runtime_s": time.time() - t0, "steps": trace}


def summarize_pair(p):
    s = {"pair": p["pair"], "teeth": [p["driver_teeth"], p["driven_teeth"]], "module": round(p["module"], 4),
         "T_in_nominal_nmm": round(p["T_in_nominal_nmm"], 4), "grader_force_n": round(p["grader_force_n"], 4),
         "engine_jams": p["engine_jams"], "runtime_s": round(p["runtime_s"], 1), "engine_evals": p["engine_evals"]}
    st = [x for x in p["steps"] if x["touching"] and x["step"] > 0]
    rates = [x["rate"] for x in st if x.get("rate_valid")]
    if rates:
        s["rate_min_max_vs_ideal"] = [round(min(rates), 4), round(max(rates), 4), round(p["steps"][0]["ideal_rate"], 4)]
    s["steps_touching"] = "%d/%d" % (len(st), len(p["steps"]) - 1)
    for key in ("mu0.00", "mu0.15", "mu0.44", "mu0.51"):
        rr = [x[key] for x in st if x.get(key) and "eff" in x[key]]
        if not rr:
            continue
        effs = [r["eff"] for r in rr]
        s[key] = {"eff_mean": round(float(np.mean(effs)), 4), "eff_min": round(min(effs), 4),
                  "eff_max": round(max(effs), 4), "max_normal_n": round(max(r["max_normal_n"] for r in rr), 4),
                  "mean_normal_n": round(float(np.mean([r["max_normal_n"] for r in rr])), 4),
                  "force_jam_steps": sum(1 for r in rr if r["jam"]),
                  "max_contacts": max(r["n_contacts"] for r in rr),
                  "max_total_normal_n": round(max(r["total_normal_n"] for r in rr), 4),
                  "axial_patch_steps": sum(1 for r in rr if r["axial_patches"])}
    fo = max(x["fixed_overlap_mm3"] for x in p["steps"])
    s["max_fixed_overlap_mm3"] = fo
    return s


def layer_check(m, names, solids, path, log):
    """Bodies that do not mesh but sit close in z: every train mobile (without hands) against every other train
    mobile it does not mesh with and against each fixed part, at the drawn pose and at 4 train positions
    (barrel 0.9, 1.7, 2.6, 3.4 deg, the others at the ideal ratios). Overlap volume and smallest gap (search 0.1 mm)."""
    meshing = {frozenset((a, b)) for (a, _, b, _) in path}
    ratio, r = {"barrel": 1.0}, 1.0
    sgn = {"barrel": -1.0}
    for (a, ta, b, tb) in path:
        ratio[b] = ratio[a] * ta / tb
        sgn[b] = -sgn[a]
    out = []
    bodies = [(n, solids[n], True) for n in names] + [(f, s, False) for f, s in m.fixed_parts.items()]
    for k, deg in enumerate((0.0, 0.9, 1.7, 2.6, 3.4)):
        posed = {n: (rotz(s, m.mobiles[n]["axis"], sgn[n] * ratio[n] * deg) if mob else s)
                 for n, s, mob in bodies}
        for i in range(len(bodies)):
            for j in range(i + 1, len(bodies)):
                ni, nj = bodies[i][0], bodies[j][0]
                if not (bodies[i][2] or bodies[j][2]) or frozenset((ni, nj)) in meshing:
                    continue
                Pi, Pj = posed[ni], posed[nj]
                if not core.bbox_overlap(Pi, Pj, 0.1):
                    continue
                v = core.ivol(Pi, Pj)
                g = float(Pi.min_gap(Pj, 0.1)) if v <= 0 else 0.0
                out.append({"a": ni, "b": nj, "barrel_deg": deg, "overlap_mm3": v, "gap_mm": round(min(g, 0.1), 5)})
    worst = {}
    for e in out:
        key = e["a"] + "/" + e["b"]
        w = worst.get(key)
        if w is None or (e["overlap_mm3"], -e["gap_mm"]) > (w["overlap_mm3"], -w["gap_mm"]):
            worst[key] = e
    res = sorted(worst.values(), key=lambda e: (-e["overlap_mm3"], e["gap_mm"]))
    log("layer check: %s" % json.dumps(res[:12]))
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("design")
    ap.add_argument("barrel_stl")
    ap.add_argument("out")
    ap.add_argument("--label", default="design")
    ap.add_argument("--steps-per-pitch", type=int, default=24)
    ap.add_argument("--pitches", type=float, default=1.25)
    ap.add_argument("--torque", type=float, default=watch.BARREL_TORQUE_MAX_NMM)
    ap.add_argument("--only", default="", help="comma list of pair indices to run (debug)")
    args = ap.parse_args()
    E.TOL = ENGINE_TOL
    t0 = time.time()

    def log(s):
        print("[%6.0fs] %s" % (time.time() - t0, s), flush=True)
    barrel = core.tris_to_manifold(core.read_stl(args.barrel_stl, watch.MAX_TRIANGLES, watch.MAX_STL_BYTES))
    m = watch.load_movement(args.design, barrel_solid=barrel)
    log("loaded %s" % args.design)
    path = going_path(m)
    names = ["barrel"] + [b for (_, _, b, _) in path]
    solids = {n: train_solid(m, n) for n in names}
    layers = layer_check(m, names, solids, path, log)
    sA, T = -1.0, args.torque                 # the barrel turns clockwise seen from the dial (+z)
    pairs, out_pairs = [], []
    T_ideal = T
    only = {int(x) for x in args.only.split(",") if x}
    for k, (a, ta, b, tb) in enumerate(path):
        if not only or k in only:
            log("mesh %s(%d) -> %s(%d), T_in %.3f N mm" % (a, ta, b, tb, T_ideal))
            p = run_pair(m, a, ta, b, tb, sA, solids, args.steps_per_pitch, args.pitches, T_ideal, log)
            pairs.append(p)
            out_pairs.append(summarize_pair(p))
            log("  summary %s" % json.dumps(out_pairs[-1]))
            json.dump({"label": args.label, "partial": True, "meshes": out_pairs}, open(args.out + ".partial", "w"))
        T_ideal *= tb / ta
        sA = -sA
    # overall: chain the mean efficiencies (the meshes are simulated one by one at the grader's ideal input torque;
    # forces scale linearly with torque under Coulomb friction, so efficiencies do not depend on it)
    overall = {}
    for key in ("mu0.00", "mu0.15", "mu0.44", "mu0.51"):
        e_mean = e_min = 1.0
        for s in out_pairs:
            if key in s:
                e_mean *= s[key]["eff_mean"]
                e_min *= s[key]["eff_min"]
        overall[key] = {"eff_mean_product": round(e_mean, 4), "eff_worst_product": round(e_min, 4)}
    summary = {"label": args.label, "design": args.design, "barrel_stl": args.barrel_stl, "barrel_torque_nmm": T,
               "engine_tol_mm3": ENGINE_TOL, "probe_arc_mm": PROBE_ARC, "mu_sliding": MU_SLIDING,
               "mu_static": MU_STATIC, "meshes": out_pairs, "overall": overall,
               "layer_check_closest_pairs": layers,
               "runtime_s": round(time.time() - t0, 1)}
    viewer = {"label": args.label, "frame": "mm; angles in degrees, counter-clockwise seen from +z, relative to the "
              "drawn pose; contacts at mu %.2f" % MU_SLIDING,
              "axes": {n: list(m.mobiles[n]["axis"]) for n in names},
              "segments": [{"pair": p["pair"], "steps": [{"step": x["step"], "angles": x["angle_deg"],
                                                           "contacts": x.get("contacts", [])} for x in p["steps"]]}
                           for p in pairs]}
    json.dump({"summary": summary, "pairs": pairs}, open(args.out, "w"))
    json.dump(viewer, open(args.out.replace(".json", "_viewer.json"), "w"))
    json.dump(summary, open(args.out.replace(".json", "_summary.json"), "w"), indent=1)
    log("done %s" % json.dumps(overall))


if __name__ == "__main__":
    main()
