"""The movement as made: each part at the print process's size limits, each mobile at the ends of the play its
own bearings give it, and the running checks again there. Used by the one-job grader when AS_MADE_IN_JOB is on
(tests/grade_watch.py, checks made_free, made_mesh, made_clear) and by spikes/asmade/asmade.py (a command).

A designer gets the process's size accuracy from the print service (DS-W03 states it: every surface of a printed
part lies within PRINT_TOLERANCE of its drawn position) and works out the fits, the shake and the backlash that
follow. The checks ask for the outcome: the movement still runs when every part is at either size limit.

States: drawn (the parts as delivered), max (every delivered part grown by the tolerance: most material, the
tightest fits), min (every delivered part shrunk by it: least material, the most play). The supplied barrel is a
supplied part and stays as supplied.

Growing and shrinking (resize): the Minkowski sum with, or erosion by, an upright cylinder of radius tol and
half-height tol: every wall moves tol in plan and every flat face moves tol in height. It is worked out from
horizontal sections, as the swept solids of check 6 are (watch._swept_bands): the heights at which the part has a
vertex cut it into slabs, a slab that a sloping face crosses is cut into bands at most SWEEP_DZ high, and each slab
is its middle section. The grown part at a height is the union of the sections within tol of that height, each
offset outwards by tol with round corners; the shrunk part is the intersection of them, each offset inwards by tol
(and nothing where the part does not reach tol above and below).

In each state:
  free    nothing overlaps at rest (mobile against frame, mobile against mobile); each mobile turns a full turn
          clear of the frame (Movement.spin); each mobile is stopped by the frame, or by a mobile on its own axis,
          within PLAY_CAP in all six directions. The distance it moves first is its play.
  mesh    each declared mesh, with the driven mobile first turned to the middle of its backlash (settle): no jam
          with the arbors where they are drawn (backlash is left); and the teeth still drive (a push of DRIVE_PUSH
          of a pitch reaches the driven teeth) there and with both arbors at the far side of their holes along the
          line of centres, where the tooth load pushes them.
  clear   Movement.clear_swept for every pair of mobiles that is not a declared mesh, in the drawn position and
          with each of the two at the end of its axial play towards the other.
"""
import math
import time

import numpy as np
import manifold3d as m3

from . import core
from . import watch as W

from .asmade_job import AS_MADE_IN_JOB, PRINT_TOLERANCE      # noqa: E402,F401

PLAY_CAP = 0.5          # mm: a mobile that moves further than this without being stopped is not held
PLAY_STEP = 0.01        # mm: scan step of the play search (then bisected to PLAY_EPS)
PLAY_EPS = 0.0005
DRIVE_PUSH = 0.5        # of the driver's tooth pitch: as made, the teeth must still reach each other within this
SETTLE_SAMPLES = 64     # phases of the driven mobile tried over one of its tooth pitches
ARC_SEGMENTS = 64       # segments per full circle of the round corners of an offset


# ---------------------------------------------------------------------------------------------- resize
def slabs(S):
    """[(z0, z1, CrossSection)] covering S's whole z range without gaps (an empty section where S has nothing)."""
    mesh = S.to_mesh()
    vp = np.asarray(mesh.vert_properties, dtype=np.float64)[:, :3]
    tv = np.asarray(mesh.tri_verts, dtype=np.int64)
    if len(tv) == 0:
        return []
    T = vp[tv]
    n = np.cross(T[:, 1] - T[:, 0], T[:, 2] - T[:, 0])
    nn = np.linalg.norm(n, axis=1)
    nz = np.abs(n[:, 2]) / np.where(nn > 0, nn, 1.0)
    slanted = (nz > 1e-9) & (nz < 1.0 - 1e-9)
    s_lo, s_hi = np.sort(T[slanted, :, 2].min(axis=1)), np.sort(T[slanted, :, 2].max(axis=1))
    zs = np.unique(vp[:, 2])
    zs = zs[np.concatenate(([True], np.diff(zs) > 1e-9))]
    out = []
    for z0, z1 in zip(zs[:-1], zs[1:]):
        zm = 0.5 * (z0 + z1)
        k = int(np.searchsorted(s_lo, zm)) - int(np.searchsorted(s_hi, zm))
        parts = max(1, int(math.ceil((z1 - z0) / W.SWEEP_DZ - 1e-9))) if k > 0 else 1
        for j in range(parts):
            b0, b1 = z0 + (z1 - z0) * j / parts, z0 + (z1 - z0) * (j + 1) / parts
            out.append((float(b0), float(b1), S.slice(0.5 * (b0 + b1))))
    return out


def resize(S, t):
    """S grown (t > 0) or shrunk (t < 0) by |t|: see the module text. t == 0 returns S."""
    if t == 0.0 or S.is_empty():
        return S
    sl = slabs(S)
    if not sl:
        return S
    a = abs(t)
    # consecutive slabs with the same section are one slab (a prism cut by vertex heights of other features)
    merged = []
    for z0, z1, cs in sl:
        if merged and _same_section(merged[-1][2], cs):
            merged[-1] = (merged[-1][0], z1, merged[-1][2])
        else:
            merged.append((z0, z1, cs))
    sl = merged
    off = [(z0, z1, cs.offset(t, m3.JoinType.Round, 2.0, ARC_SEGMENTS) if not cs.is_empty() else cs)
           for z0, z1, cs in sl]
    zmin, zmax = sl[0][0], sl[-1][1]
    cuts = sorted({round(z + s * a, 9) for z0, z1, _ in sl for z in (z0, z1) for s in (-1.0, 1.0)})
    lo_all, hi_all = (zmin - a, zmax + a) if t > 0 else (zmin + a, zmax - a)
    runs, memo = [], {}                       # [(c0, c1, key)]: consecutive intervals with the same slabs join
    for c0, c1 in zip(cuts[:-1], cuts[1:]):
        if c1 - c0 < 1e-9 or c0 < lo_all - 1e-9 or c1 > hi_all + 1e-9:
            continue
        key = tuple(i for i, (z0, z1, _) in enumerate(off) if z1 > c0 - a + 1e-9 and z0 < c1 + a - 1e-9)
        if not key:
            continue
        if runs and runs[-1][2] == key and abs(runs[-1][1] - c0) < 1e-9:
            runs[-1] = (runs[-1][0], c1, key)
        else:
            runs.append((c0, c1, key))
    prisms = []
    for c0, c1, key in runs:
        if key not in memo:
            near = [off[i][2] for i in key]
            if t > 0:
                near = [cs for cs in near if not cs.is_empty()]
                sec = None if not near else (near[0] if len(near) == 1
                                             else m3.CrossSection.batch_boolean(near, m3.OpType.Add))
            elif any(cs.is_empty() for cs in near):
                sec = None
            else:
                sec = near[0]
                for cs in near[1:]:
                    sec = sec ^ cs
                    if sec.is_empty():
                        break
            memo[key] = None if sec is None or sec.is_empty() else sec
        sec = memo[key]
        if sec is not None:
            prisms.append(sec.extrude(c1 - c0).translate([0.0, 0.0, c0]))
    if not prisms:
        return m3.Manifold()
    return prisms[0] if len(prisms) == 1 else m3.Manifold.batch_boolean(prisms, m3.OpType.Add)


SAME_SECTION = 0.002    # mm: two sections whose outlines differ by less than this on average are one shape (the
                        # tessellation of a STEP file moves a vertical wall by up to STEP_LINEAR_DEFLECTION, 0.001)


def _perimeter(cs):
    return float(sum(np.linalg.norm(np.roll(np.asarray(p), -1, axis=0) - np.asarray(p), axis=1).sum()
                     for p in cs.to_polygons()))


def _same_section(a, b):
    """Two sections are the same shape: the area between their outlines is under SAME_SECTION x the outline's
    length. A sloping face moves the outline by its slope x the band height, far more than that."""
    if a.is_empty() or b.is_empty():
        return a.is_empty() and b.is_empty()
    if abs(a.area() - b.area()) > SAME_SECTION * _perimeter(a):
        return False
    return ((a - b) + (b - a)).area() <= SAME_SECTION * _perimeter(a)


# ---------------------------------------------------------------------------------------------- loading
# ---------------------------------------------------------------------------------------------- checks
def assembled(m):
    """Largest overlap at rest: mobile against frame, and mobile against mobile."""
    worst, pair = 0.0, None
    names = list(m.mobiles)
    for k in names:
        v = core.ivol(m.mobiles[k]["solid"], m.fixed)
        if v > worst:
            worst, pair = v, "%s/frame" % k
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            v = core.ivol(m.mobiles[names[i]]["solid"], m.mobiles[names[j]]["solid"])
            if v > worst:
                worst, pair = v, "%s/%s" % (names[i], names[j])
    return {"worst_volume": worst, "pair": pair, "ok": worst <= W.VOL_TOL}


def _stops(m, name):
    """What can stop the mobile: the frame, and every other mobile on its own axis."""
    ax = m.mobiles[name]["axis"]
    co = [mo["solid"] for k, mo in m.mobiles.items() if k != name
          and math.hypot(mo["axis"][0] - ax[0], mo["axis"][1] - ax[1]) <= W.COAX_TOL]
    S = m.mobiles[name]["solid"]
    V = core.verts(S)
    lo, hi = V.min(axis=0) - PLAY_CAP - 0.1, V.max(axis=0) + PLAY_CAP + 0.1
    return W.union([m.fixed] + co) ^ core.box(tuple(lo), tuple(hi))


def play(m, name, stops=None):
    """{direction: distance in mm the mobile moves before it is stopped, or None if not stopped within PLAY_CAP}."""
    S = m.mobiles[name]["solid"]
    O = _stops(m, name) if stops is None else stops
    out = {}
    for label, d in W.Movement.DIRECTIONS:
        hit = lambda s: core.ivol(S.translate([c * s for c in d]), O) > W.VOL_TOL
        s, found = 0.0, None
        while s < PLAY_CAP - 1e-12:
            s = min(PLAY_CAP, s + PLAY_STEP)
            if hit(s):
                found = s
                break
        if found is None:
            out[label] = None
            continue
        lo, hi = found - PLAY_STEP, found
        while hi - lo > PLAY_EPS:
            mid = 0.5 * (lo + hi)
            if hit(mid):
                hi = mid
            else:
                lo = mid
        out[label] = max(0.0, lo)
    return out


def settle(m, a, b, tb, shift=0.0):
    """Turn the driven mobile b to the middle of its backlash against a (both at step 0 of the mesh test).
    Returns (angle in degrees to turn b by, width of the free window in degrees), or (None, 0.0) when b overlaps
    a at every phase tried: jammed at rest."""
    A, ax_a = m.mobiles[a]["solid"], m.mobiles[a]["axis"]
    B, ax_b = m.mobiles[b]["solid"], m.mobiles[b]["axis"]
    if shift:
        dx, dy = ax_b[0] - ax_a[0], ax_b[1] - ax_a[1]
        d = math.hypot(dx, dy)
        ux, uy = (dx / d, dy / d) if d > 1e-12 else (1.0, 0.0)
        B = B.translate([shift * ux, shift * uy, 0.0])
        ax_b = (ax_b[0] + shift * ux, ax_b[1] + shift * uy)
    A2, B2 = W._near_cut(A, ax_a, B, ax_b), W._near_cut(B, ax_b, A, ax_a)
    if not (A2.is_empty() or B2.is_empty()):
        A, B = A2, B2
    pitch = 360.0 / tb
    phis = [pitch * (i / SETTLE_SAMPLES - 0.5) for i in range(SETTLE_SAMPLES)]
    free = [core.ivol(A, B if p == 0.0 else W.rot_about(B, ax_b, p)) <= 1e-9 for p in phis]
    if not any(free):
        return None, 0.0
    if all(free):
        return 0.0, pitch
    # the longest run of free phases, cyclic; the one that holds phase 0 wins a tie
    n, best = SETTLE_SAMPLES, (0, 0)
    start = next(i for i in range(n) if not free[i])
    i = 0
    while i < n:
        j = (start + i) % n
        if free[j]:
            k = 0
            while k < n and free[(j + k) % n]:
                k += 1
            if k > best[1]:
                best = (j, k)
            i += k
        else:
            i += 1
    j, k = best
    centre = phis[j] + 0.5 * (k - 1) * pitch / n
    return centre, k * pitch / n


MESH_PITCHES = 2        # tooth pitches of the driver run at each of MESH_SPOTS places round the turn
MESH_SPOTS = 3          # (the drawn movement's check 4 runs the whole turn; resizing is the same for every tooth)


def mesh_few(m, a, ta, b, tb, shift=0.0, full=False):
    """The mesh test's no-jam and drive conditions (Movement.mesh_run's own steps, angles and measures) on
    MESH_PITCHES tooth pitches of the driver at MESH_SPOTS places round the larger gear's turn, instead of the whole
    turn. full=True runs Movement.mesh_run itself (the whole turn)."""
    if full:
        return m.mesh_run(a, ta, b, tb, shift=shift)
    A, ax_a = m.mobiles[a]["solid"], m.mobiles[a]["axis"]
    B, ax_b = m.mobiles[b]["solid"], m.mobiles[b]["axis"]
    module = 2.0 * math.hypot(ax_b[0] - ax_a[0], ax_b[1] - ax_a[1]) / (ta + tb)
    if shift:
        dx, dy = ax_b[0] - ax_a[0], ax_b[1] - ax_a[1]
        d = math.hypot(dx, dy)
        ux, uy = (dx / d, dy / d) if d > 1e-12 else (1.0, 0.0)
        B = B.translate([shift * ux, shift * uy, 0.0])
        ax_b = (ax_b[0] + shift * ux, ax_b[1] + shift * uy)
    A2, B2 = W._near_cut(A, ax_a, B, ax_b), W._near_cut(B, ax_b, A, ax_a)
    if not (A2.is_empty() or B2.is_empty()):
        A, B = A2, B2
    pa = lambda deg: A if deg == 0.0 else W.rot_about(A, ax_a, deg)
    pb = lambda deg: B if deg == 0.0 else W.rot_about(B, ax_b, deg)
    spt = W.SAMPLES_PER_TOOTH
    n = spt * max(ta, tb)
    da = 360.0 / (spt * ta)
    db = -da * ta / tb
    push = W.DRIVE_FRACTION * 360.0 / ta
    steps = sorted({(s0 + j) % n for k in range(MESH_SPOTS) for s0 in [spt * ((max(ta, tb) * k) // MESH_SPOTS)]
                    for j in range(spt * MESH_PITCHES)})
    worst, gap, drive, ratio, height = (0.0, 0), 0.0, float("inf"), float("inf"), float("inf")
    for i in steps:
        Ai, Bi = pa(da * i), pb(db * i)
        v = core.ivol(Ai, Bi)
        if v > worst[0]:
            worst = (v, i)
        if i % 4 == 0 and v <= 1e-12:
            g = Ai.min_gap(Bi, W.MESH_GAP_SEARCH)
            gap = max(gap, float(g if g < W.MESH_GAP_SEARCH else Ai.min_gap(Bi, 1.0)))
        for f in W.MESH_OFFGRID if i % 4 == 0 else ():
            vf = core.ivol(pa(da * (i + float(f))), pb(db * (i + float(f))))
            if vf > worst[0]:
                worst = (vf, i + float(f))
        if i % 2 == 0:
            P = pa(da * i + push)
            extra, r, hz = 0.0, 0.0, 0.0
            if core.bbox_overlap(P, Bi):
                N = (P ^ Bi) - Ai
                extra = float(N.volume()) if not N.is_empty() else 0.0
                if extra > 0.0:
                    zb = N.bounding_box()
                    hz = zb[5] - zb[2]
                    r = extra / (hz * module * module) if hz > 1e-9 and module > 1e-9 else 0.0
            drive, ratio = min(drive, extra), min(ratio, r)
            height = min(height, hz if extra > 0.0 else 0.0)
    return {"worst_volume": worst[0], "step": worst[1], "steps": len(steps), "largest_gap": gap,
            "smallest_drive_overlap": drive, "smallest_drive_ratio": ratio, "module": module,
            "smallest_drive_height": height}


TOWARDS = False         # --towards: also run each mesh with the two arbors pushed together (reported only)
FULL_TURN = False       # --full: run every mesh through the whole turn (Movement.mesh_run), as check 4 does


def mesh_state(m, a, ta, b, tb, shift=0.0):
    """The mesh with b settled in the middle of its backlash: no jam, and the drive test with a push of DRIVE_PUSH
    of a pitch (module constant swapped for the call)."""
    phi, window = settle(m, a, b, tb, shift)
    if phi is None:
        return {"jam_at_rest": True, "ok_no_jam": False, "ok_drive": False, "backlash_deg": 0.0}
    mo = m.mobiles[b]
    keep = mo["solid"]
    old = W.DRIVE_FRACTION
    try:
        if phi:
            mo["solid"] = W.rot_about(keep, mo["axis"], phi)
        W.DRIVE_FRACTION = DRIVE_PUSH
        r = mesh_few(m, a, ta, b, tb, shift=shift, full=FULL_TURN)
    finally:
        mo["solid"] = keep
        W.DRIVE_FRACTION = old
    r["settle_deg"], r["backlash_deg"] = phi, window
    r["backlash_pitch_share"] = window / (360.0 / tb)
    r["ok_no_jam"] = r["worst_volume"] <= W.VOL_TOL
    r["ok_drive"] = W.Movement.drive_passes(r)
    return r


def clear_pairs(m):
    declared = {frozenset((a, b)) for a, _, b, _ in m.meshes}
    names = list(m.mobiles)
    return [(names[i], names[j]) for i in range(len(names)) for j in range(i + 1, len(names))
            if frozenset((names[i], names[j])) not in declared]


def clear_state(m, plays, with_play=True):
    """Check 6 on every undeclared pair: drawn position, and with the lower of the two moved up and the upper moved
    down, each by its own axial play (the worst the two can do to each other in height). Two mobiles on one axis
    are tested in the drawn position only: one may be what stops the other, so their plays are not independent."""
    out = {}
    for a, b in clear_pairs(m):
        r = m.clear_swept(a, b)
        entry = {"drawn": r["worst_volume"]}
        (xa, ya), (xb, yb) = m.mobiles[a]["axis"], m.mobiles[b]["axis"]
        coaxial = math.hypot(xb - xa, yb - ya) <= W.COAX_TOL     # each may be what stops the other: drawn only
        if with_play and not coaxial \
                and not (r["pruned"] and r["worst_volume"] == 0.0 and not _near_in_z(m, a, b, plays)):
            za, zb = m.swept_cylinder(a), m.swept_cylinder(b)
            lower, upper = (a, b) if (za[1] + za[2]) <= (zb[1] + zb[2]) else (b, a)
            up, down = plays[lower].get("+z"), plays[upper].get("-z")
            if up is not None and down is not None and (up > 0 or down > 0):
                sa, sb = m.mobiles[lower]["solid"], m.mobiles[upper]["solid"]
                try:
                    m.mobiles[lower]["solid"] = sa.translate([0, 0, up])
                    m.mobiles[upper]["solid"] = sb.translate([0, 0, -down])
                    entry["with_play"] = m.clear_swept(lower, upper)["worst_volume"]
                finally:
                    m.mobiles[lower]["solid"], m.mobiles[upper]["solid"] = sa, sb
        entry["worst"] = max(entry.values())
        out["%s/%s" % (a, b)] = entry
    return out


def _near_in_z(m, a, b, plays):
    """The two swept cylinders overlap in plan, and come within their axial plays of each other in height."""
    ra, a0, a1 = m.swept_cylinder(a)
    rb, b0, b1 = m.swept_cylinder(b)
    (xa, ya), (xb, yb) = m.mobiles[a]["axis"], m.mobiles[b]["axis"]
    if math.hypot(xb - xa, yb - ya) >= ra + rb:
        return False
    reach = sum((plays[k].get(d) or PLAY_CAP) for k in (a, b) for d in ("+z", "-z"))
    return min(a1, b1) + reach > max(a0, b0)


def mesh_all(m, plays, quick=False, say=None):
    """{mesh: centre / away (/ towards) runs, ok_no_jam, ok_drive} for every declared mesh of m; plays: play() per
    mobile."""
    say = say or (lambda *_: None)
    res = {"play": plays, "mesh": {}}
    for a, ta, b, tb in m.meshes:
        key = "%s:%d/%s:%d" % (a, ta, b, tb)
        e = {"centre": mesh_state(m, a, ta, b, tb)}
        if not quick:
            # radial play along the line of centres: b away from a, and b towards a (b's own play; a stays)
            ax_a, ax_b = m.mobiles[a]["axis"], m.mobiles[b]["axis"]
            dx, dy = ax_b[0] - ax_a[0], ax_b[1] - ax_a[1]
            d = math.hypot(dx, dy) or 1.0
            pb, pa = res["play"][b], res["play"][a]
            along = lambda p, ux, uy: min((p[l] if p[l] is not None else PLAY_CAP) / max(abs(c), 1e-9)
                                          for l, c in (("+x" if ux > 0 else "-x", ux), ("+y" if uy > 0 else "-y", uy))
                                          if abs(c) > 1e-9)
            away = along(pb, dx / d, dy / d) + along(pa, -dx / d, -dy / d)
            towards = along(pb, -dx / d, -dy / d) + along(pa, dx / d, dy / d)
            e["away_mm"], e["towards_mm"] = away, towards
            e["away"] = mesh_state(m, a, ta, b, tb, shift=away)
            if TOWARDS:
                e["towards"] = mesh_state(m, a, ta, b, tb, shift=-towards)
        # the rule: backlash is left with the arbors where they are drawn (no jam), and the teeth still drive there
        # and with both arbors at the far side of their holes, where the load pushes them (away). Pushed together
        # the teeth may bottom; that is reported (--towards), not judged: the mobiles are free to move apart again.
        e["ok_no_jam"] = e["centre"]["ok_no_jam"]
        e["ok_drive"] = e["centre"]["ok_drive"] and ("away" not in e or (e["away"]["ok_drive"] and e["away"]["ok_no_jam"]))
        res["mesh"][key] = e
        say("  mesh %s: %s; backlash %.3f of a pitch; %s" % (
            key, "ok" if e["ok_no_jam"] and e["ok_drive"] else "FAIL", e["centre"].get("backlash_pitch_share", 0.0), "; ".join(
            "%s%s no jam %s drives %s" % (w, "" if w == "centre" else " %.3f mm" % e[w + "_mm"], e[w]["ok_no_jam"],
                                          e[w]["ok_drive"]) for w in ("centre", "away", "towards") if w in e)))
    return res["mesh"]


def run_state(m, quick=False, log=None):
    say = log or (lambda *_: None)
    t0 = time.time()
    res = {"assembled": assembled(m)}
    say("  assembled worst %.4f (%s)" % (res["assembled"]["worst_volume"], res["assembled"]["pair"]))
    res["free"] = {}
    for k in m.mobiles:
        r = m.spin(k, W.SPIN_OFFGRID)
        res["free"][k] = r["worst_volume"]
    say("  free worst %.4f" % max(res["free"].values()))
    res["play"] = {k: play(m, k) for k in m.mobiles}
    nh = [k for k, p in res["play"].items() if any(v is None for v in p.values())]
    say("  play: not held %s; axial %s" % (nh, {k: (round(p["+z"], 3) if p["+z"] is not None else None,
                                                 round(p["-z"], 3) if p["-z"] is not None else None)
                                             for k, p in res["play"].items()}))
    res["mesh"] = mesh_all(m, res["play"], quick, say)
    res["clear"] = clear_state(m, res["play"], with_play=not quick)
    wc = max((v["worst"] for v in res["clear"].values()), default=0.0)
    say("  clear worst %.4f" % wc)
    res["ok"] = {
        "assembled": res["assembled"]["ok"],
        "free": max(res["free"].values()) <= W.VOL_TOL,
        "held": not nh,
        "no_jam": all(e["ok_no_jam"] for e in res["mesh"].values()),
        "drives": all(e["ok_drive"] for e in res["mesh"].values()),
        "clear": wc <= W.VOL_TOL,
    }
    res["seconds"] = round(time.time() - t0, 1)
    return res


def state_of(m, tol, cache=None):
    """Movement m with every delivered part resized by tol (0: m itself). cache: {(part name, tol): solid}."""
    if tol == 0.0:
        return m
    cache = {} if cache is None else cache

    def load(n):
        key = (n, tol)
        if key not in cache:
            cache[key] = resize(m.load_part(n), tol)
            if cache[key].is_empty():
                raise core.FormatError("part '%s' vanishes at the size limit (shrunk by %g mm)" % (n, -tol))
        return cache[key]
    s = W.Movement(m.doc, load, m.mobiles["barrel"]["solid"], materials="material" in next(
        (mo for k, mo in m.mobiles.items() if k != "barrel"), {}))
    s.barrel_speed = m.barrel_speed
    return s


STATES = (("drawn", 0.0), ("max", 1.0), ("min", -1.0))


class AsMade:
    """The three checks on movement m, sharing the work: free(), mesh(), clear() -> (passed, details)."""

    def __init__(self, m, tol=None):
        self.m, self.tol = m, PRINT_TOLERANCE if tol is None else tol
        self._parts, self._state, self._play = {}, {}, {}

    def state(self, label):
        if label not in self._state:
            self._state[label] = state_of(self.m, dict(STATES)[label] * self.tol, self._parts)
        return self._state[label]

    def play(self, label):
        if label not in self._play:
            s = self.state(label)
            self._play[label] = {k: play(s, k) for k in s.mobiles}
        return self._play[label]

    def free(self):
        out, ok = {}, True
        for label, _ in STATES:
            try:
                s = self.state(label)
            except core.FormatError as e:
                out[label] = {"error": str(e)}
                ok = False
                continue
            a = assembled(s)
            spin = {k: s.spin(k, W.SPIN_OFFGRID)["worst_volume"] for k in s.mobiles}
            pl = self.play(label)
            loose = [k for k, p in pl.items() if any(v is None for v in p.values())]
            out[label] = {"assembled": a, "spin": spin, "play": pl, "not_held": loose}
            ok = ok and a["ok"] and max(spin.values()) <= W.VOL_TOL and not loose
        return ok, out

    def mesh(self):
        out, ok = {}, True
        for label, _ in STATES:
            try:
                s = self.state(label)
            except core.FormatError as e:
                out[label] = {"error": str(e)}
                ok = False
                continue
            out[label] = mesh_all(s, self.play(label))
            ok = ok and all(e["ok_no_jam"] and e["ok_drive"] for e in out[label].values())
        return ok, out

    def clear(self):
        out, ok = {}, True
        for label, _ in STATES:
            try:
                s = self.state(label)
            except core.FormatError as e:
                out[label] = {"error": str(e)}
                ok = False
                continue
            out[label] = clear_state(s, self.play(label))
            ok = ok and all(v["worst"] <= W.VOL_TOL for v in out[label].values())
        return ok, out
