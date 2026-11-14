"""Quasi-static contact engine (manifold3d), one degree of freedom per body.

Bodies
------
Every body is a closed mesh with one coordinate q:
  rot   : rotation (rad, right-hand) about a line (point, unit direction)
  slide : translation (mm) along a unit direction
A body may ride on a carrier: its pose is then the carrier's rotation (only the rotation, not the
carrier's slide) composed with its own coordinate. That is how a sliding pinion rides a turning stem.

Kinds
-----
  fixed   : never moves.
  driven  : its coordinates are set by the scenario (the stem: rotation and pull).
  contact : moves only when pushed, and only as far as needed to clear the contact.
  spring  : like contact when pushed; between steps it returns towards `rest` (a coordinate, or
            +inf / -inf for a direction) until it touches something. A spring never pushes.
  main    : the mainspring arbor. Pushed like contact; between steps it tries to turn towards
            `rest` and does push whatever is in its way (it is strong).

Contact rule
------------
Penetration of a body = its largest intersection volume with any other body (fixed-fixed pairs
and pairs inside one carrier family are not counted). A step is resolved when every penetration is at
most TOL. A pushed body may move at most K times the surface travel (arc length at the body's
outer radius) of the bodies touching it in this step; it moves the least distance that clears it.
This is the friction-cone rule: a contact face inclined steeper than atan(K) to the direction of
the push cannot be cleared by sliding the pushed body along its degree of freedom, so it locks
(a click against a ratchet tooth, a vertical Breguet face); a gentler ramp lets it slip.

If a step cannot be resolved the input is blocked: every body returns to its pose before the step,
and the step is recorded as jammed.
"""
import math

import numpy as np
import manifold3d as m3

TOL = 2e-4          # mm^3 of overlap allowed between two bodies
try:
    from constants import MU    # dry friction of the test rig
except ImportError:             # the engine on its own (toy tests)
    MU = 0.51
K = 1.0 / MU        # friction-cone factor: a face inclined more steeply than atan(1/MU) to the push locks
SWEEPS = 14
RELAX_MAX = 0.25    # mm of surface travel a spring may return per step
SCAN_ARC = 0.002    # mm of surface travel between samples when searching for the clearing position
MAX_STEP_TRAVEL = 0.06  # mm: a step in which any body's surface travels further is split in halves (up to 4 times),
                        # so the friction-cone rule always sees small steps compared with the features


def rot_matrix(point, direction, angle):
    u = np.asarray(direction, float)
    u = u / np.linalg.norm(u)
    c, s = math.cos(angle), math.sin(angle)
    Kx = np.array([[0, -u[2], u[1]], [u[2], 0, -u[0]], [-u[1], u[0], 0]])
    R = np.eye(3) + s * Kx + (1 - c) * Kx @ Kx
    p = np.asarray(point, float)
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p - R @ p
    return T


def slide_matrix(direction, d):
    u = np.asarray(direction, float)
    u = u / np.linalg.norm(u)
    T = np.eye(4)
    T[:3, 3] = u * d
    return T


class Body:
    def __init__(self, name, man, kind, dof=None, point=None, direction=None, rest=None,
                 carrier=None, q0=0.0, lo=-math.inf, hi=math.inf):
        self.name, self.man, self.kind = name, man, kind
        self.dof = dof                      # 'rot' | 'slide' | None (fixed) | 'stem'
        self.point = np.asarray(point if point is not None else (0, 0, 0), float)
        d = np.asarray(direction if direction is not None else (0, 0, 1), float)
        self.dir = d / np.linalg.norm(d)
        self.rest = rest
        self.carrier = carrier              # name of a driven 'stem' body whose rotation it shares
        self.q = q0                         # own coordinate; for the stem: rotation
        self.p = 0.0                        # stem only: pull along dir
        self.lo, self.hi = lo, hi
        v = np.asarray(man.to_mesh().vert_properties, float)[:, :3] if not man.is_empty() else np.zeros((1, 3))
        self.verts = v
        if self.dof in ("rot", "stem"):
            rel = v - self.point
            along = rel @ self.dir
            self.radius = float(np.max(np.linalg.norm(rel - np.outer(along, self.dir), axis=1)))
        else:
            self.radius = 1.0
        self.radius = max(self.radius, 0.05)
        self._cache = {}

    def arc(self, dq):
        return abs(dq) * (self.radius if self.dof in ("rot", "stem") else 1.0)

    def coord_from_arc(self, a):
        return a / (self.radius if self.dof in ("rot", "stem") else 1.0)


class World:
    def __init__(self, bodies):
        self.bodies = {b.name: b for b in bodies}
        self.order_spring = [b for b in bodies if b.kind == "spring"]
        self.order_contact = [b for b in bodies if b.kind == "contact"]
        self.order_main = [b for b in bodies if b.kind == "main"]
        self.movers = self.order_spring + self.order_contact + self.order_main
        self.family = {}
        for b in bodies:
            self.family[b.name] = b.carrier or b.name
        self.evals = 0
        self.pair_cache = {}
        self.dqs = {}

    # ----- poses -----
    def matrix(self, b, q=None):
        q = b.q if q is None else q
        if b.dof is None:
            return np.eye(4)
        if b.dof == "stem":
            return slide_matrix(b.dir, b.p) @ rot_matrix(b.point, b.dir, q)
        if b.dof == "rot":
            T = rot_matrix(b.point, b.dir, q)
        else:
            T = slide_matrix(b.dir, q)
        if b.carrier:
            c = self.bodies[b.carrier]
            T = rot_matrix(c.point, c.dir, c.q) @ T
        return T

    def posed(self, b, q=None, with_key=False):
        T = self.matrix(b, q)
        key = tuple(np.round(T[:3, :4].ravel(), 10))
        m = b._cache.get(key)
        if m is None:
            m = (b.man.transform(T[:3, :4].tolist()), None)
            bb = m[0].bounding_box()
            m = (m[0], bb)
            if len(b._cache) > 12:          # transformed meshes are large: keep only a few poses
                b._cache.clear()
            b._cache[key] = m
        return (m[0], m[1], key) if with_key else m[0]

    def pairs_ok(self, a, b):
        if a is b:
            return False
        if a.kind == "fixed" and b.kind == "fixed":
            return False
        return True

    def children(self, b):
        return [o for o in self.bodies.values() if o.carrier == b.name]

    def pen(self, b, q=None, only=None):
        """Largest overlap of body b (at coordinate q) with any other body (each pair has its own TOL).
        A carrier that is free to turn (a released crown) also answers for the bodies riding on it."""
        if b.kind not in ("driven", "fixed") and b.dof == "stem":
            kids = self.children(b)
            if kids:
                old = b.q
                if q is not None:
                    b.q = q
                try:
                    v = self._pen1(b, None, only)
                    for k in kids:
                        v = max(v, self._pen1(k, None, None if only is None else (set(only) - {b.name})))
                    return v
                finally:
                    b.q = old
        return self._pen1(b, q, only)

    def _pen1(self, b, q=None, only=None):
        mb, A, kb = self.posed(b, q, with_key=True)
        if mb.is_empty():
            return 0.0
        tot = 0.0
        for o in self.bodies.values():
            if not self.pairs_ok(b, o) or (only is not None and o.name not in only):
                continue
            mo, B, ko = self.posed(o, with_key=True)
            if mo.is_empty():
                continue
            if not all(A[i] < B[i + 3] and B[i] < A[i + 3] for i in range(3)):
                continue
            ck = (b.name, kb, o.name, ko) if b.name < o.name else (o.name, ko, b.name, kb)
            v = self.pair_cache.get(ck)
            if v is None:
                self.evals += 1
                v = (mb ^ mo).volume()
                if not math.isfinite(v):
                    raise ArithmeticError("non-finite volume")
                if len(self.pair_cache) > 50000:
                    self.pair_cache.clear()
                self.pair_cache[ck] = v
            tot = max(tot, v)
        return tot

    def neighbours(self, b):
        _, A, _ = self.posed(b, with_key=True)
        out = []
        for o in self.bodies.values():
            if o is b or o.kind == "fixed":
                continue
            _, B, _ = self.posed(o, with_key=True)
            if all(A[i] < B[i + 3] + 0.05 and B[i] < A[i + 3] + 0.05 for i in range(3)):
                out.append(o)
        return out

    # ----- elementary moves -----
    def push(self, b, dmax, only=None):
        """Move b the least distance (at most dmax in its own coordinate) that clears its overlap
        with `only` (all bodies when None). True if cleared."""
        pen = lambda q=None: self.pen(b, q, only)  # noqa: E731
        p0 = pen()
        if p0 <= TOL:
            return True
        tgt = 0.5 * TOL
        if dmax <= 0:
            return False
        best = None
        # scan fine enough not to jump over a narrow clearing window (gear backlash is a few microns)
        h = min(dmax / 8.0, b.coord_from_arc(SCAN_ARC))
        for sgn in (1.0, -1.0):
            prev, lowest, rising = 0.0, p0, 0
            i = 0
            while True:
                i += 1
                d = sgn * min(dmax, h * i)
                q = b.q + d
                if q < b.lo or q > b.hi:
                    break
                v = pen(q)
                if v <= tgt:
                    lo_, hi_ = prev, d          # bisect the first clearing distance
                    for _ in range(8):
                        mid = 0.5 * (lo_ + hi_)
                        if pen(b.q + mid) <= tgt:
                            hi_ = mid
                        else:
                            lo_ = mid
                    if best is None or abs(hi_) < abs(best):
                        best = hi_
                    break
                if v < lowest:
                    lowest, rising = v, 0
                else:
                    rising += 1
                    if rising >= 4 and lowest < p0:     # passed the bottom of the valley: give up this side
                        break
                    if rising >= 6 and lowest >= p0:    # only getting worse this way
                        break
                prev = d
                if abs(d) >= dmax:
                    break
        if best is None:
            return False
        b.q += best
        self._add_dq(b, best)
        return True

    # ----- per-step motion bookkeeping (for the friction cone at the contact point) -----
    def _add_dq(self, b, d):
        r, s_ = self.dqs.get(b.name, (0.0, 0.0))
        if b.dof in ("rot", "stem"):
            r += abs(d)
        else:
            s_ += abs(d)
        self.dqs[b.name] = (r, s_)

    def _axis_dist(self, point, direction, c):
        rel = np.asarray(c) - point
        return float(np.linalg.norm(rel - (rel @ direction) * direction))

    def travel(self, o, c):
        """Distance point c (on body o) travelled in this step because o moved."""
        r, s_ = self.dqs.get(o.name, (0.0, 0.0))
        t = s_
        if o.dof == "rot":
            t += r * self._axis_dist(o.point, o.dir, c)
        elif o.dof == "stem":
            t += r * self._axis_dist(o.point, o.dir, c)
        if o.carrier:
            cr = self.bodies[o.carrier]
            t += self.dqs.get(cr.name, (0.0, 0.0))[0] * self._axis_dist(cr.point, cr.dir, c)
        return t

    def budget(self, b, among):
        """Largest move of b (own coordinate) the friction cone allows, given the bodies in `among`
        that overlap it now."""
        best = 0.0
        fam = [b] + (self.children(b) if b.dof == "stem" else [])
        pairs = [(m, o) for m in fam for o in among if o is not b and o not in fam]
        for m, o in pairs:
            v = self.posed(m) ^ self.posed(o)
            if v.volume() <= 0.5 * TOL:
                continue
            comps = v.decompose()
            for comp in comps:               # each separate contact patch
                if comp.volume() <= 0.05 * TOL:
                    continue
                pts = np.asarray(comp.to_mesh().vert_properties, float)[:, :3]
                if not len(pts):
                    continue
                c = pts.mean(axis=0)
                t = self.travel(o, c) + self.travel(b, c)     # relative sliding at the contact
                if t <= 0:
                    continue
                if b.dof == "rot":
                    rb = max(self._axis_dist(b.point, b.dir, c), 0.05)
                    best = max(best, K * t / rb)
                else:
                    best = max(best, K * t)
        return best

    def relax(self, b):
        """Spring: return towards rest until contact (no pushing)."""
        if b.rest is None:
            return
        target = b.rest
        if math.isinf(target):
            dist_arc = RELAX_MAX
            sgn = 1.0 if target > 0 else -1.0
        else:
            dq = target - b.q
            if abs(dq) < 1e-12:
                return
            sgn = 1.0 if dq > 0 else -1.0
            dist_arc = min(RELAX_MAX, b.arc(dq))
        dmax = b.coord_from_arc(dist_arc)
        n = 10
        last_ok = 0.0
        for i in range(1, n + 1):
            d = sgn * dmax * i / n
            q = b.q + d
            if q < b.lo or q > b.hi:
                break
            if self.pen(b, q) <= 0.5 * TOL:
                last_ok = d
            else:
                lo_, hi_ = last_ok, d
                for _ in range(6):
                    mid = 0.5 * (lo_ + hi_)
                    if self.pen(b, b.q + mid) <= 0.5 * TOL:
                        lo_ = mid
                    else:
                        hi_ = mid
                last_ok = lo_
                break
        b.q += last_ok

    def resolve(self):
        """Sweeps of pushes. Light springs yield first, then free bodies, then the mainspring arbor."""
        fixed_names = {n for n, o in self.bodies.items() if o.kind == "fixed"}
        for _ in range(SWEEPS):
            bad = False
            before = {b.name: b.q for b in self.movers}
            for b in self.movers:
                if self.pen(b) <= TOL:
                    continue
                movers_now = [o for o in self.bodies.values() if o is not b and (
                    any(self.dqs.get(o.name, (0.0, 0.0))) or (o.carrier and any(self.dqs.get(o.carrier, (0.0, 0.0)))))]
                if b.kind == "spring":
                    # light: first it yields to anything it touches, if it can within the friction cone
                    touching = [o for o in self.bodies.values() if o is not b and self.pairs_ok(b, o)]
                    if self.push(b, self.budget(b, touching)):
                        continue
                    # if it cannot simply give way, a pushed spring part passes the push on like a rigid
                    # link (it never drives anything by its own spring, only when something pushes it)
                    pushers = {o.name for o in movers_now} | fixed_names
                    if self.pen(b, only=pushers) > TOL and self.push(b, self.budget(b, movers_now), only=pushers):
                        continue
                    bad = True
                    continue
                # pushed: clear the bodies that moved in this step (and the fixed ones); what it
                # runs into downstream is resolved by those bodies in turn
                pushers = {o.name for o in movers_now} | fixed_names
                if self.pen(b, only=pushers) <= TOL:
                    bad = True
                    continue
                if not self.push(b, self.budget(b, movers_now), only=pushers):
                    bad = True
            if not bad:
                if all(self.pen(b) <= TOL for b in self.movers):
                    return True
            elif all(abs(b.q - before[b.name]) < 1e-12 for b in self.movers):
                return False            # no progress: blocked
        return all(self.pen(b) <= TOL for b in self.movers)

    def snapshot(self):
        return {n: (b.q, b.p) for n, b in self.bodies.items()}

    def restore(self, s):
        for n, (q, p) in s.items():
            self.bodies[n].q, self.bodies[n].p = q, p

    # ----- one input step -----
    def _max_travel(self):
        m = 0.0
        for n, (r, s_) in self.dqs.items():
            b = self.bodies[n]
            m = max(m, r * b.radius + s_)
            if b.carrier:
                m = max(m, self.dqs.get(b.carrier, (0.0, 0.0))[0] * b.radius + s_)
        for b in self.bodies.values():          # carried bodies move with their carrier
            if b.carrier and b.carrier in self.dqs:
                m = max(m, self.dqs[b.carrier][0] * b.radius)
        return m

    def step(self, driver, dq=0.0, dp=0.0, main_try_arc=0.02, _depth=0):
        """Move the driven body by dq (rotation) and dp (pull). Returns True, or False if blocked."""
        snap = self.snapshot()
        d = self.bodies[driver]
        d.q += dq
        d.p += dp
        self.dqs = {driver: (abs(dq), abs(dp))}
        ok = self.resolve()
        if ok and _depth < 4 and self._max_travel() > MAX_STEP_TRAVEL:
            self.restore(snap)
            return (self.step(driver, dq / 2, dp / 2, main_try_arc / 2, _depth + 1)
                    and self.step(driver, dq / 2, dp / 2, main_try_arc / 2, _depth + 1))
        if not ok:
            self.restore(snap)
            return False
        # springs return
        for b in self.order_spring:
            self.relax(b)
        # mainspring: try to turn back, pushing (in small enough pieces)
        for b in self.order_main:
            if b.rest is None:
                continue
            sgn = 1.0 if b.rest > b.q else -1.0
            for frac in (1.0, 0.5, 0.25, 0.125):
                s2 = self.snapshot()
                dqm = sgn * b.coord_from_arc(main_try_arc * frac)
                b.q += dqm
                self.dqs = {b.name: (abs(dqm), 0.0)}
                if self.resolve() and self._max_travel() <= MAX_STEP_TRAVEL:
                    for sb in self.order_spring:
                        self.relax(sb)
                    break
                self.restore(s2)
        return True

    def settle(self, budget=0.3):
        """Start: let every mover clear any overlap at its rest pose (up to `budget` mm of travel)."""
        self.dqs = {}
        for _ in range(3):
            for b in self.movers:
                self.push(b, b.coord_from_arc(budget))
        for _ in range(3):
            for b in self.order_spring:
                self.relax(b)

    def max_pen(self):
        return max([self.pen(b) for b in self.bodies.values() if b.kind != "fixed"] + [0.0])
