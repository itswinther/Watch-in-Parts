"""The movement as made (spike; no grader change): each part at the print process's size limits, each mobile at
the ends of the play its own bearings give it, and the same running checks as the drawn movement.

    python3 spikes/asmade/asmade.py DELIVERY_DIR OUT.json [--tol 0.03] [--file movement.json] [--quick]

Why: the one-job grader measures the drawn solids only. A design whose layers are 0.02 mm apart passes it, and no
printed part holds 0.02 mm. A designer gets the process's size tolerance from the print service (DS-W03 would
state it) and works out the clearances, the shake and the backlash that follow. This test asks for the outcome:
the movement still runs when every part is at either size limit.

States (tol = the size tolerance, every surface of a printed part lies within tol of its drawn position):
  drawn   the parts as delivered
  max     every delivered part grown by tol (most material: the tightest fits, the smallest gaps)
  min     every delivered part shrunk by tol (least material: the loosest fits, the most play)
The supplied barrel is a supplied part and stays as supplied.

Growing and shrinking (resize): the Minkowski sum with, or erosion by, an upright cylinder of radius tol and
half-height tol: every wall moves tol in plan and every flat face moves tol in height. It is worked out from
horizontal sections, as the swept solids of check 6 are (geometry/watch.py _swept_bands): the heights at which the
part has a vertex cut it into slabs, a slab that a sloping face crosses is cut into bands at most SWEEP_DZ high,
and each slab is its middle section. The grown part at a height is the union of the sections within tol of that
height, each offset outwards by tol with round corners; the shrunk part is the intersection of them, each offset
inwards by tol (and nothing where the part does not reach tol above and below).

In each state:
  assembled    no mobile overlaps the frame or another mobile by more than VOL_TOL at rest
  free         Movement.spin: each mobile turns a full turn clear of the frame
  play         how far each mobile moves along +x, -x, +y, -y, +z, -z before the frame (or a mobile on its own
               axis) stops it; "not held" if nothing stops it within PLAY_CAP
  mesh         each declared mesh, with the driven mobile first turned to the middle of its backlash (settle), is
               run through Movement.mesh_run: no jam; and the teeth still drive (a push of DRIVE_PUSH of a pitch
               reaches the driven teeth), also with the driven mobile at the two ends of its radial play along the
               line of centres
  clear        Movement.clear_swept for every pair of mobiles that is not a declared mesh, drawn position, and with
               each of the two at the end of its axial play towards the other

--quick: skips the radial-play mesh runs and the axial-play clear runs.
"""
import json
import math
import os
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
import numpy as np                       # noqa: E402
import manifold3d as m3                  # noqa: E402
from geometry import watch as W          # noqa: E402
from geometry import core                # noqa: E402

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
def load_state(folder, name, tol, cache):
    """The movement of `name` with every delivered part resized by tol (0: as drawn). cache: {(part, tol): solid}."""
    base = W.load_movement(folder, name, cache=cache.setdefault("files", {}), materials=True)
    if tol == 0.0:
        return base
    load0 = base.load_part

    def load(n):
        key = (n, tol)
        if key not in cache:
            cache[key] = resize(load0(n), tol)
            if cache[key].is_empty():
                raise core.FormatError("part '%s' vanishes at the size limit (shrunk by %g mm)" % (n, -tol))
        return cache[key]
    return W.Movement(base.doc, load, None, materials=True)


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


def mesh_state(m, a, ta, b, tb, shift=0.0):
    """mesh_run on the mesh with b settled in the middle of its backlash. The drive test pushes DRIVE_PUSH of a
    pitch (module constant swapped for the call)."""
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
        r = m.mesh_run(a, ta, b, tb, shift=shift)
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
    down, each by its own axial play (the worst the two can do to each other in height)."""
    out = {}
    for a, b in clear_pairs(m):
        r = m.clear_swept(a, b)
        entry = {"drawn": r["worst_volume"]}
        if with_play and not (r["pruned"] and r["worst_volume"] == 0.0 and not _near_in_z(m, a, b, plays)):
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
    res["mesh"] = {}
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
            e["towards"] = mesh_state(m, a, ta, b, tb, shift=-towards)
        e["ok_no_jam"] = all(v["ok_no_jam"] for v in e.values() if isinstance(v, dict))
        e["ok_drive"] = all(v["ok_drive"] for v in e.values() if isinstance(v, dict))
        res["mesh"][key] = e
        say("  mesh %s: no jam %s, drives %s, backlash %.3f of a pitch%s" % (
            key, e["ok_no_jam"], e["ok_drive"], e["centre"].get("backlash_pitch_share", 0.0),
            "" if quick else " (away %.3f, towards %.3f mm)" % (e["away_mm"], e["towards_mm"])))
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


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    folder, out = os.path.abspath(argv[0]), argv[1]
    opts = dict(zip(argv[2:], argv[3:]))
    tol = float(opts.get("--tol", "0.03"))
    name = opts.get("--file", "movement.json")
    quick = "--quick" in argv
    cache, result = {}, {"delivery": folder, "file": name, "tol": tol, "states": {}}
    for label, t in (("drawn", 0.0), ("max", tol), ("min", -tol)):
        print("state %s (%+.3f mm)" % (label, t), flush=True)
        t0 = time.time()
        try:
            m = load_state(folder, name, t, cache)
        except Exception as ex:
            print("  does not load: %s: %s" % (type(ex).__name__, ex), flush=True)
            result["states"][label] = {"error": "%s: %s" % (type(ex).__name__, ex), "ok": {"loads": False}}
            continue
        print("  loaded and resized in %.1f s" % (time.time() - t0), flush=True)
        result["states"][label] = run_state(m, quick, lambda s: print(s, flush=True))
        print("  %s  (%.0f s)" % (result["states"][label]["ok"], result["states"][label]["seconds"]), flush=True)
    result["runs_as_made"] = all(all(s["ok"].values()) for s in result["states"].values())
    with open(out, "w") as f:
        json.dump(result, f, indent=1, default=float)
    print("runs as made at +/- %g mm: %s" % (tol, result["runs_as_made"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
