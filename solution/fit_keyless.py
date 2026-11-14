"""Fitting pass (SESSION.md Decisions 2026-11-14 17:46, B's item 2): workstream A's keyless v1 reference
(spikes/keyless/reference.py, imported, not edited) scaled by s and placed on B's one-job reference delivery.

    python3 solution/fit_keyless.py /abs/REF_JOB [--at0]

REF_JOB is a delivery written by `python3 solution/reference_watch.py REF_JOB --job` (two-body barrel, no barrel
cock). Prints:
  1. the rigid placements of A's v1 (scaled by S about its barrel axis, turned, flipped or not, raised), each with
     its collision table: intersection volume (mm3) of every keyless part with every part of B's reference
     (the barrel as its two bodies), the stem line, the crown's position and the setting wheel's reach;
     --at0 also runs A's own AT-0 rest-overlap and held checks (spikes/keyless/grade.py make_world, held_check)
     on the placed bodies, with B's whole movement as the fixed body;
  2. the proposed layout: the keyless works as envelopes (tip discs, rings and cylinders sized from A's v1 x S,
     z stack compacted), placed so that the four conditions of the brief hold; its collision table against B's
     reference, the centre distances of its meshes, and the frame cuts it needs;
  3. the proposed numbers.
Frames. B: +z is the dial side; barrel axis x = y = 0; main plate z -1.7..-0.3, bridge 5.0..6.0, dial 8.8..9.6.
A: z towards A's main plate, the stem along +x through y = z = 0, the barrel arbor at constants.BARREL_AXIS."""
import importlib.util
import json
import math
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
KEYLESS = os.path.join(ROOT, "spikes", "keyless")
sys.path.insert(0, ROOT)
import numpy as np                    # noqa: E402
import manifold3d as m3               # noqa: E402
from geometry import watch as W       # noqa: E402
from geometry import core             # noqa: E402

S = 1.617                             # demonstration scale (Decisions 14:45; A's datasheets 74c05ae)
PULL_B = 0.80 * S                     # stem travel to position 2 at S (Sellita 0.80 mm x S, A's INTERFACE_FOR_B)
STEM_PROTRUDE_B = 0.5 * S             # A's STEM_PROTRUDE x S: stem material at least this far outside the case
CROWN_GAP_B = 0.4 * S                 # A's v1: crown's inner face 0.4 outside A's case radius; x S
VOL = 1e-6                            # mm3: smaller intersections are not listed
FRAME = ("main_plate", "bridge", "dial")
E_LAYER, F_LAYER = (6.4, 7.2), (7.6, 8.4)    # B's reference: minute-wheel / cannon layer, hour-wheel layer


def _import_keyless(name):
    if KEYLESS not in sys.path:
        sys.path.insert(0, KEYLESS)
    spec = importlib.util.spec_from_file_location("keyless_" + name, os.path.join(KEYLESS, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ B's reference
def load_b(ref):
    m = W.load_movement(ref)
    parts = dict(m.fixed_parts)
    owner = {n: "frame" for n in parts}
    for k, mo in m.mobiles.items():
        if k == "barrel":
            continue
        for n, s in mo["parts"].items():
            parts[n], owner[n] = s, k
    for n, s in W.barrel_bodies().items():
        parts[n], owner[n] = s, "barrel"
    return m, parts, owner


# ------------------------------------------------------------------ A's v1, scaled and placed
class Place:
    """p_B = Rz(phi) . F . S (p_A - (bx, by, 0)) + (0, 0, z0); F = 180 degrees about x when flip."""

    def __init__(self, phi, flip, z0, bx, by):
        self.phi, self.flip, self.z0, self.bx, self.by = phi, flip, z0, bx, by
        c, s_ = math.cos(math.radians(phi)), math.sin(math.radians(phi))
        Rz = np.array([[c, -s_, 0], [s_, c, 0], [0, 0, 1.0]])
        F = np.diag([1.0, -1.0, -1.0]) if flip else np.eye(3)
        self.L = Rz @ F * S
        self.t = np.array([0, 0, z0]) - self.L @ np.array([bx, by, 0.0])

    def point(self, p):
        return self.L @ np.asarray(p, float) + self.t

    def vec(self, d):
        v = self.L @ np.asarray(d, float)
        return v / np.linalg.norm(v)

    def man(self, m):
        M = np.hstack([self.L, self.t[:, None]])
        return m.transform(M.tolist())


def stem_layout(phi, flip, cc):
    """z0-independent facts of a rigid placement: stem direction u (outwards, towards the crown) and the signed
    distance of the case centre from the stem line (0 when the stem is radial)."""
    pl = Place(phi, flip, 0.0, *A_BARREL)
    u = pl.vec((1, 0, 0))[:2]
    p0 = pl.point((0, 0, 0))[:2]
    d = np.asarray(cc) - p0
    return u, float(d[0] * u[1] - d[1] * u[0])


def radial_angle(cc, flip):
    """The turn phi that makes A's stem line pass through the case centre cc, with the crown outwards and the
    rigid stem's crown nearest the case radius (of the two roots, the one that needs the least stem change)."""
    f = lambda a: stem_layout(a, flip, cc)[1]
    roots = []
    for k in range(3600):
        a, b = k / 10.0, (k + 1) / 10.0
        if (f(a) > 0) != (f(b) > 0):
            for _ in range(60):
                mid = (a + b) / 2
                if (f(a) > 0) == (f(mid) > 0):
                    a = mid
                else:
                    b = mid
            roots.append(round((a + b) / 2, 4))
    best = None
    for a in roots:
        u, _ = stem_layout(a, flip, cc)
        pl = Place(a, flip, 0.0, *A_BARREL)
        t = float((pl.point((12.6, 0, 0))[:2] - np.asarray(cc)) @ u)
        if t > 0 and (best is None or abs(t - W.CASE_RADIUS) < best[1]):
            best = (a, abs(t - W.CASE_RADIUS))
    return best[0]


def shorten_stem(parts, pl, cc):
    """Move the crown, the outer stem and the stem guide inwards along the stem so the crown's inner face is
    CROWN_GAP_B outside the case radius (A's v1 is longer than B's case radius allows)."""
    u = pl.vec((1, 0, 0))
    face = pl.point((12.6, 0, 0))
    t_face = float((face[:2] - np.asarray(cc)) @ u[:2])
    shift = t_face - (W.CASE_RADIUS + CROWN_GAP_B)
    cut = pl.point((5.0, 0, 0))
    off = float(u @ cut)
    inner = parts["stem"].trim_by_plane(list(-u), -off)
    outer = parts["stem"].trim_by_plane(list(u), off).translate(list(-u * shift))
    out = dict(parts)
    out["stem"] = core.union([inner, outer])
    out["stem_guide"] = parts["stem_guide"].translate(list(-u * shift))
    return out, shift


def collisions(kparts, bparts, owner, skip=()):
    rows = []
    for kn, km in kparts.items():
        kb = km.bounding_box()
        for bn, bm in bparts.items():
            if (kn, bn) in skip:
                continue
            bb = bm.bounding_box()
            if any(kb[i] > bb[i + 3] or bb[i] > kb[i + 3] for i in range(3)):
                continue
            v = (km ^ bm).volume()
            if v > VOL:
                rows.append((kn, bn, owner[bn], v))
    return rows


def print_table(rows, title):
    print("  %s" % title)
    if not rows:
        print("    (no intersection above %g mm3)" % VOL)
        return
    print("    %-16s %-14s %-12s %10s" % ("keyless part", "B part", "B mobile", "mm3"))
    for kn, bn, ow, v in sorted(rows, key=lambda r: (-r[3])):
        print("    %-16s %-14s %-12s %10.4f" % (kn, bn, ow, v))
    tot = {}
    for _, _, ow, v in rows:
        k = "frame" if ow == "frame" else ("barrel" if ow == "barrel" else "going train / motion work")
        tot[k] = tot.get(k, 0.0) + v
    print("    totals: " + ", ".join("%s %.3f" % kv for kv in sorted(tot.items())))


def z_range(m):
    b = m.bounding_box()
    return b[2], b[5]


def at0(kparts, spec, pl, bparts):
    """A's AT-0 rest-overlap and held checks (spikes/keyless/grade.py) on the placed bodies. B's whole reference
    (frame, every mobile, the barrel drum) is A's fixed body; the arbor joins A's barrel body."""
    G = _import_keyless("grade")
    E = _import_keyless("engine")
    sup = {"b_fixed": core.union([m for n, m in bparts.items() if n != "barrel_arbor"]),
           "barrel_arbor": bparts["barrel_arbor"]}
    defs = []
    for mn, mob in spec["mobiles"].items():
        if mn == "stem":
            defs.append(dict(name=mn, parts=mob["parts"], kind="driven", dof="stem", point=tuple(pl.point((0, 0, 0))),
                             direction=tuple(pl.vec((1, 0, 0)))))
        elif mn == "barrel":
            defs.append(dict(name=mn, parts=mob["parts"] + ["@barrel_arbor"], kind="main", dof="rot",
                             point=(0.0, 0.0, 0.0), direction=tuple(pl.vec((0, 0, 1))), rest=-math.inf))
        else:
            d = dict(name=mn, parts=mob["parts"], kind="spring" if mob["kind"] == "spring" else "contact",
                     dof=mob["dof"], point=tuple(pl.point(mob.get("point", (0, 0, 0)))),
                     direction=tuple(pl.vec(mob["direction"])),
                     rest=(mob["rest"] * math.inf) if mob["kind"] == "spring" else None,
                     carrier="stem" if mob.get("on_stem") else None)
            defs.append(d)
    defs.append(dict(name="fixed", parts=spec["fixed"] + ["@b_fixed"], kind="fixed"))
    w = G.make_world(kparts, sup, defs)
    pens = {n: round(w.pen(b), 4) for n, b in w.bodies.items() if b.kind != "fixed"}
    held = G.held_check(kparts, sup, defs)
    return pens, {k: v["ok"] for k, v in held.items()}, E.TOL


# ------------------------------------------------------------------ section 1: rigid placements
A_BARREL = None


def rigid(ref_parts, owner, cc, do_at0):
    global A_BARREL
    R = _import_keyless("reference")
    C = _import_keyless("constants")
    A_BARREL = C.BARREL_AXIS
    parts_a, spec = R.build()
    bx, by = C.BARREL_AXIS
    za = {n: z_range(m) for n, m in parts_a.items()}
    stack = (za["barrel_wheel"][0], za["barrel_wheel"][1])          # sleeve: the ratchet stack on the arbor
    print("A's v1 at S = %.3f: total height %.2f (z_A %.2f..%.2f); ratchet stack on the arbor %.2f tall, tip radius %.2f;"
          % (S, S * (max(v[1] for v in za.values()) - min(v[0] for v in za.values())),
             min(v[0] for v in za.values()), max(v[1] for v in za.values()), S * (stack[1] - stack[0]),
             S * 3.8))
    print("  stem offset from the barrel axis %.2f; setting wheel spur %.2f above/below the stem axis to %.2f"
          % (S * by, S * 1.9, S * 2.4))
    layouts = []
    for flip in (True, False):
        phi = radial_angle(cc, flip)
        layouts.append((flip, phi, stem_layout(phi, flip, cc)[0]))
    # the z of each layout: put the ratchet stack where B's frame leaves room over the barrel
    #   under the bridge: 3.25..4.95 (above the centre wheel's layer, below the bridge)
    #   below the main plate: top at -1.75
    #   above the bridge: bottom at 6.05
    def z0_for(flip, lo=None, hi=None):
        a, b = (-S * stack[1], -S * stack[0]) if flip else (S * stack[0], S * stack[1])   # stack z relative to z0
        if lo is not None:
            return lo - a
        return hi - b
    results = []
    for flip, phi, u in layouts:
        tag = "W" if flip else "N"
        for where, kw in (("ratchet under the bridge", dict(lo=3.25 + (4.95 - 3.25 - S * (stack[1] - stack[0])) / 2)),
                          ("ratchet below the main plate", dict(hi=-1.75)),
                          ("ratchet above the bridge", dict(lo=6.05))):
            z0 = round(z0_for(flip, **kw), 3)
            pl = Place(phi, flip, z0, bx, by)
            kp = {n: pl.man(m) for n, m in parts_a.items()}
            kp, shift = shorten_stem(kp, pl, cc)
            rows = collisions(kp, ref_parts, owner)
            results.append((tag, where, flip, phi, z0, pl, kp, rows, shift, spec))
    for tag, where, flip, phi, z0, pl, kp, rows, shift, spec in results:
        u = pl.vec((1, 0, 0))
        sp = pl.point((0, 0, 0))
        zs = {n: z_range(m) for n, m in kp.items()}
        sw = pl.point((7.1, 0, 0))
        spur_z = sorted((pl.point((0, 0, -2.4))[2], pl.point((0, 0, -1.9))[2]))
        print("\n[%s, %s] flip %s, phi %.2f deg, z0 %.3f" % (tag, where, flip, phi, z0))
        print("  stem line: point (%.3f, %.3f, %.3f), direction (%.4f, %.4f, %.4f); radial to the case centre; "
              "outer stem shortened by %.2f" % (sp[0], sp[1], sp[2], u[0], u[1], u[2], shift))
        print("  winding sense: the barrel's axis maps to (0, 0, %+d); A winds anticlockwise seen from A's +z, i.e. %s seen "
              "from B's dial side (B's drum runs clockwise; the arbor must be wound the same way)"
              % (round(pl.vec((0, 0, 1))[2]), "clockwise" if flip else "anticlockwise (WRONG)"))
        print("  z extent of the keyless parts: %.2f .. %.2f; ratchet stack %.2f .. %.2f; crown wheel %.2f .. %.2f; "
              "setting wheel %.2f .. %.2f" % (min(v[0] for v in zs.values()), max(v[1] for v in zs.values()),
                                              *zs["barrel_wheel"], *zs["crown_wheel"], *zs["setting_wheel"]))
        mw = np.asarray(M.mobiles["minute_wheel"]["axis"])
        c = np.asarray(M.mobiles["centre"]["axis"])
        print("  setting wheel axis (%.2f, %.2f), its spur z %.2f..%.2f: %.2f from the minute wheel's axis (a mesh needs "
              "4.5 + the spur's pitch radius), %.2f from the hour wheel's" % (sw[0], sw[1], spur_z[0], spur_z[1],
                                                                             np.linalg.norm(sw[:2] - mw), np.linalg.norm(sw[:2] - c)))
        print_table(rows, "collisions with B's reference:")
        if do_at0:
            pens, held, tol = at0(kp, spec, pl, ref_parts)
            print("  A's AT-0 on the placed bodies (B's movement fixed): rest overlap > %g mm3: %s; held fails: %s"
                  % (tol, {k: v for k, v in pens.items() if v > tol} or "none",
                     [k for k, v in held.items() if not v] or "none"))
    return results


# ------------------------------------------------------------------ section 2: the proposed layout (envelopes)
def cyl(x, y, z0, z1, r, seg=96):
    return m3.Manifold.cylinder(z1 - z0, r, r, seg).translate([x, y, z0])


def ring(x, y, z0, z1, r0, r1):
    return cyl(x, y, z0, z1, r1) - cyl(x, y, z0 - 1, z1 + 1, r0)


def along(p0, u, t0, t1, r, z, seg=48):
    c = m3.Manifold.cylinder(t1 - t0, r, r, seg).rotate([0, 90, 0]).translate([t0, 0, 0])
    return c.rotate([0, 0, math.degrees(math.atan2(u[1], u[0]))]).translate([p0[0], p0[1], z])


def box_along(p0, u, t0, t1, half_w, z0, z1):
    b = m3.Manifold.cube([t1 - t0, 2 * half_w, z1 - z0]).translate([t0, -half_w, z0])
    return b.rotate([0, 0, math.degrees(math.atan2(u[1], u[0]))]).translate([p0[0], p0[1], 0])


def circles(p, rp, q, rq, side_of=None):
    """The two intersection points of circles (p, rp) and (q, rq) in the plane."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    d = np.linalg.norm(q - p)
    if not abs(rp - rq) <= d <= rp + rq:
        return []
    a = (rp * rp - rq * rq + d * d) / (2 * d)
    h = math.sqrt(max(rp * rp - a * a, 0.0))
    e = (q - p) / d
    n = np.array([-e[1], e[0]])
    return [p + a * e + h * n, p + a * e - h * n]


P = dict(
    theta=36.0,           # stem direction from the case centre, degrees from +x (radial)
    z_stem=5.5,           # stem axis: in the bridge's thickness (B's bridge plays the real main plate here)
    r_stem=0.35 * S,      # A's v1 stem radius x S
    r_crown=1.0 * S, l_crown=0.8 * S,
    t_wind=6.0,           # winding pinion's inner end, from the case centre along the stem
    r_pin=1.05,           # winding and sliding pinions' tip radius (A's v1 x S is 1.70; see the report)
    l_wind=0.99 * S, l_slide=1.44 * S,
    R_face=2.7 * S,       # crown wheel's face-ring radius: A's v1 x S
    R_set=2.7 * S,        # setting wheel's face-ring radius: A's v1 x S
    w_face=0.35 * S,      # half width of the face ring
    m_wind=0.2 * S,       # ratchet and crown-wheel spur module: A's v1 spur module x S
    z_crown_spur=12,      # crown wheel's spur teeth (A's v1)
    ratchet=(3.35, 4.15), # ratchet's z: on the arbor's square (3.3..4.9)
    m_set=0.25,           # setting wheel's spur: B's minute wheel's module (36 teeth, layer E)
    z_set=12,
)


def proposed(ref_parts, owner, cc, m):
    th = math.radians(P["theta"])
    u = np.array([math.cos(th), math.sin(th)])
    n_left = np.array([-u[1], u[0]])
    cc = np.asarray(cc)
    zs, rp = P["z_stem"], P["r_pin"]
    tw0 = P["t_wind"]
    tw1 = tw0 + P["l_wind"]
    ts0, ts1 = tw1 + 0.02, tw1 + 0.02 + P["l_slide"]
    t_face = W.CASE_RADIUS + CROWN_GAP_B
    O = np.zeros(2)
    Pw = cc + u * (tw0 + tw1) / 2                   # winding pinion's centre in plan
    mw_ax = np.asarray(m.mobiles["minute_wheel"]["axis"])
    # ratchet + crown wheel: |K - O| = ratchet pitch + crown spur pitch, |K - Pw| = R_face, K on the barrel's side
    rk = P["m_wind"] * P["z_crown_spur"] / 2
    d = np.linalg.norm(Pw - O)
    best = None
    for zr in range(20, 80):
        rr = P["m_wind"] * zr / 2
        if rr + P["m_wind"] > 6.5:                  # the fourth wheel reaches 6.7 from the barrel axis at layer D
            break
        for K in circles(O, rr + rk, Pw, P["R_face"]):
            if (K - Pw) @ n_left * ((O - Pw) @ n_left) < 0:
                continue
            score = abs(rr + P["m_wind"] - 5.0)     # prefer a ratchet of about tip radius 5
            if best is None or score < best[0]:
                best = (score, zr, rr, K)
    _, zr, rr, K = best
    # setting wheel: its face ring over the sliding pinion pulled to position 2; its spur meshes B's minute wheel
    Ps = cc + u * (ts1 - 0.4 + PULL_B - 0.15 * S)   # sliding pinion's outer teeth at position 2 (A's v1 geometry)
    rq = P["m_set"] * P["z_set"] / 2
    cand = circles(mw_ax, 4.5 + rq, Ps, P["R_set"])
    if not cand:
        raise SystemExit("setting wheel: no axis meshes the minute wheel and reaches the sliding pinion (%.3f apart, "
                         "reach %.3f)" % (np.linalg.norm(Ps - mw_ax), 4.5 + rq + P["R_set"]))
    c_ax = np.asarray(m.mobiles["centre"]["axis"])
    Q = max(cand, key=lambda q: np.linalg.norm(q - c_ax))      # the one further from the centre arbor and cannon
    z_ring_w = (zs - rp - 0.15, zs - rp + 0.35)     # crown wheel's face ring under the winding pinion
    z_ring_s = (zs + rp - 0.35, zs + rp + 0.15)     # setting wheel's face ring over the sliding pinion
    zr0, zr1 = P["ratchet"]
    ratchet_tip = rr + P["m_wind"]
    sq = W.BARREL_SQUARE_SIDE / 2
    env = {
        "stem": core.union([along(cc, u, tw0 - 1.0 * S, t_face, P["r_stem"], zs),
                            along(cc, u, t_face, t_face + P["l_crown"], P["r_crown"], zs)]),
        "winding_pinion": along(cc, u, tw0, tw1, rp, zs),
        "sliding_pinion": along(cc, u, ts0, ts1, rp, zs),
        "stem_bearing": box_along(cc, u, tw0 - 0.8, tw0 - 0.2, 0.8 * S, zs - 1.0, W.BARREL_SQUARE_Z[1] + 1.1),
        "stem_guide": box_along(cc, u, W.CASE_RADIUS - 1.2, W.CASE_RADIUS - 0.3, 0.6 * S, zs - 0.8 * S, zs + 0.8 * S),
        "ratchet": cyl(0, 0, zr0, zr1, ratchet_tip) - m3.Manifold.cube([2 * sq, 2 * sq, 10]).translate([-sq, -sq, 0]),
        "crown_wheel": core.union([cyl(K[0], K[1], zr0, zr1, rk + P["m_wind"]),
                                   cyl(K[0], K[1], zr1, z_ring_w[0], P["R_face"] + P["w_face"]),
                                   ring(K[0], K[1], z_ring_w[0], z_ring_w[1], P["R_face"] - P["w_face"],
                                        P["R_face"] + P["w_face"])]) - cyl(K[0], K[1], 0, 10, 0.36 * S),
        "crown_post": cyl(K[0], K[1], zr0 - 0.05, 6.0, 0.33 * S),
        "setting_wheel": core.union([cyl(Q[0], Q[1], E_LAYER[0], E_LAYER[1], rq + P["m_set"]),
                                     ring(Q[0], Q[1], z_ring_s[0], z_ring_s[1], P["R_set"] - P["w_face"],
                                          P["R_set"] + P["w_face"]),
                                     cyl(Q[0], Q[1], max(z_ring_s[1], E_LAYER[1]) - 0.01, max(z_ring_s[1], E_LAYER[1]) + 0.15,
                                         P["R_set"] + P["w_face"])]) - cyl(Q[0], Q[1], 0, 10, 0.36 * S),
        "setting_post": cyl(Q[0], Q[1], 5.95, max(z_ring_s[1], E_LAYER[1]) + 0.3, 0.33 * S),
    }
    # the setting wheel's spur meshes B's minute wheel: listed by centre distance, not as a collision
    skip = {("setting_wheel", "minute_wheel")}
    rows = collisions(env, ref_parts, owner, skip)
    print("\nProposed layout (envelopes; the keyless works' own meshes are not modelled, only their space):")
    print("  stem line: point (%.4f, %.4f, %.2f) (the case centre), direction (%.4f, %.4f, 0), theta %.1f deg"
          % (cc[0], cc[1], zs, u[0], u[1], P["theta"]))
    print("  crown: z %.2f, radius %.3f, from %.3f to %.3f from the case centre (case radius %.2f; stem material %.3f outside "
          "needs >= %.3f)" % (zs, P["r_crown"], t_face, t_face + P["l_crown"], W.CASE_RADIUS,
                              t_face + P["l_crown"] - W.CASE_RADIUS, STEM_PROTRUDE_B))
    print("  winding pinion t %.2f..%.2f (centre (%.2f, %.2f)), sliding pinion t %.2f..%.2f; pinion tip radius %.2f; "
          "position 2 = pulled %.3f" % (tw0, tw1, Pw[0], Pw[1], ts0, ts1, rp, PULL_B))
    print("  ratchet on the square, z %.2f..%.2f: %d teeth, module %.4f, pitch radius %.3f, tip %.3f"
          % (zr0, zr1, zr, P["m_wind"], rr, ratchet_tip))
    print("  crown wheel axis (%.3f, %.3f): spur %d teeth (pitch %.3f) at the ratchet's z, centre distance to the barrel "
          "axis %.4f (= %.4f + %.4f); face ring radius %.3f at z %.2f..%.2f under the winding pinion, %.4f from its centre"
          % (K[0], K[1], P["z_crown_spur"], rk, np.linalg.norm(K), rr, rk, P["R_face"], *z_ring_w, np.linalg.norm(K - Pw)))
    print("  setting wheel axis (%.3f, %.3f): spur %d teeth module %.2f at z %.1f..%.1f meshing B's minute wheel "
          "(36 teeth, axis (%.3f, %.3f)): centre distance %.4f (= 4.5 + %.4f); face ring radius %.3f at z %.2f..%.2f over the "
          "sliding pinion at position 2, %.4f from it" % (Q[0], Q[1], P["z_set"], P["m_set"], *E_LAYER, mw_ax[0], mw_ax[1],
                                                        np.linalg.norm(Q - mw_ax), rq, P["R_set"], *z_ring_s,
                                                        np.linalg.norm(Q - Ps)))
    print_table(rows, "collisions with B's reference (frame cuts are frame changes; anything else must be zero):")
    gaps = {}
    for kn, km in env.items():
        for bn, bm in ref_parts.items():
            if owner[bn] in ("frame",) or (kn, bn) in skip or (kn == "ratchet" and bn == "barrel_arbor"):
                continue
            g = km.min_gap(bm, 1.0)
            if g < 1.0 and (kn not in gaps or g < gaps[kn][1]):
                gaps[kn] = (bn, g)
    print("  smallest gap of each keyless envelope to B's mobiles and barrel (within 1.0): "
          + ", ".join("%s-%s %.3f" % (k, v[0], v[1]) for k, v in sorted(gaps.items())))
    zall = [z_range(mm) for mm in env.values()]
    print("  z extent of the keyless works: %.2f .. %.2f (B's reference: %.2f .. %.2f)" % (
        min(z[0] for z in zall), max(z[1] for z in zall), *REF_Z))
    rmax = max(float(np.hypot(*(core.verts(mm)[:, :2] - cc).T).max()) for k, mm in env.items() if k != "stem")
    print("  farthest keyless point from the case centre, the stem left out: %.3f (case radius %.2f)" % (rmax, W.CASE_RADIUS))
    return dict(u=u, K=K, Q=Q, zr=zr, rr=rr, rows=rows, t_face=t_face, env=env)


REF_Z = (0.0, 0.0)
M = None


def main(argv):
    global REF_Z, M
    ref = os.path.abspath(argv[0])
    do_at0 = "--at0" in argv
    M, bparts, owner = load_b(ref)
    cc = M.case_centre
    allz = [z_range(mm) for mm in bparts.values()]
    REF_Z = (min(z[0] for z in allz), max(z[1] for z in allz))
    print("B's reference %s: case centre (%.4f, %.4f), case radius %.2f, height %.2f; parts z %.2f .. %.2f (%.2f tall)"
          % (ref, cc[0], cc[1], W.CASE_RADIUS, W.CASE_HEIGHT, REF_Z[0], REF_Z[1], REF_Z[1] - REF_Z[0]))
    print("Supplied barrel: arbor z %s, pivots radius %s, core radius %.4f (inner diameter %s / 6), square side %s at z %s"
          % (W.BARREL_ARBOR_Z, W.BARREL_ARBOR_R, W.BARREL_CORE_R, W.BARREL_INNER_D, W.BARREL_SQUARE_SIDE, W.BARREL_SQUARE_Z))
    print("\n== 1. A's keyless v1, rigid, scaled by S = %.3f about its barrel axis ==" % S)
    rigid(bparts, owner, cc, do_at0)
    print("\n== 2. Proposed layout ==")
    prop = proposed(bparts, owner, cc, M)
    print("\n== 3. Proposed numbers ==")
    u = prop["u"]
    print(json.dumps({
        "barrel_square": {"side": W.BARREL_SQUARE_SIDE, "z": list(W.BARREL_SQUARE_Z)},
        "barrel_arbor": {"z": list(W.BARREL_ARBOR_Z), "pivot_radius": W.BARREL_ARBOR_R,
                         "core_radius": round(W.BARREL_CORE_R, 4), "inner_diameter": W.BARREL_INNER_D},
        "winding_sense": "the arbor is wound clockwise seen from the dial side (+z), the sense the drum runs",
        "stem_line_reference": {"point": [cc[0], cc[1], P["z_stem"]], "direction": [round(u[0], 4), round(u[1], 4), 0.0]},
        "crown_reference": {"z": P["z_stem"], "radius": round(P["r_crown"], 3),
                            "from_case_centre": [round(prop["t_face"], 3), round(prop["t_face"] + P["l_crown"], 3)]},
        "pull_to_position_2": round(PULL_B, 3),
        "case": {"radius": W.CASE_RADIUS, "height": W.CASE_HEIGHT, "reference_z": [round(REF_Z[0], 2), round(REF_Z[1], 2)]},
    }, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
