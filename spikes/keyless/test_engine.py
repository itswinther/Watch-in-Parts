"""Toy tests for the contact engine: gear ratio, ratchet and pawl, detent.

    python test_engine.py      (exit 0 when all pass)
"""
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import manifold3d as m3  # noqa: E402
import numpy as np  # noqa: E402
import engine as E  # noqa: E402
import gears as G  # noqa: E402
import shapes as S  # noqa: E402


def gear_pair():
    a = G.spur(12, 0.2, 0, 1.0, thin=0.01)
    b = G.spur(24, 0.2, 0, 1.0, thin=0.01, phase=math.pi / 24).translate([3.6, 0, 0])
    A = E.Body("a", a, "driven", dof="stem", point=(0, 0, 0), direction=(0, 0, 1))
    B = E.Body("b", b, "contact", dof="rot", point=(3.6, 0, 0), direction=(0, 0, 1))
    w = E.World([A, B])
    w.settle()
    b0 = B.q
    for _ in range(30):
        assert w.step("a", dq=math.radians(2.0)), "gear pair jammed"
    ratio = (B.q - b0) / math.radians(60)
    print("gear pair: driven/driver = %.3f (expect -0.5)" % ratio)
    return abs(ratio + 0.5) < 0.06


def ratchet_pawl():
    wheel = S.ratchet_wheel(20, 2.0, 2.4, 0, 1.0)        # steep face leads anticlockwise
    pawl, piv = S.click(20, 2.0, 2.4, 0, 1.0)
    W = E.Body("wheel", wheel, "driven", dof="stem", point=(0, 0, 0), direction=(0, 0, 1))
    P = E.Body("pawl", pawl, "spring", dof="rot", point=piv, direction=(0, 0, 1), rest=math.inf)
    w = E.World([W, P])
    w.settle()
    ok_fwd = all(w.step("wheel", dq=math.radians(1.5)) for _ in range(40))
    blocked = False
    for _ in range(16):                       # within one tooth (18 deg) backwards it must lock
        if not w.step("wheel", dq=math.radians(-1.5)):
            blocked = True
            break
    print("ratchet: forward 60 deg free=%s, backward blocked=%s" % (ok_fwd, blocked))
    return ok_fwd and blocked


def mainspring_click():
    wheel = S.ratchet_wheel(20, 2.0, 2.4, 0, 1.0)
    pawl, piv = S.click(20, 2.0, 2.4, 0, 1.0)
    for with_click in (True, False):
        W = E.Body("arbor", wheel, "main", dof="rot", point=(0, 0, 0), direction=(0, 0, 1), rest=-math.inf)
        bodies = [W]
        if with_click:
            bodies.append(E.Body("click", pawl, "spring", dof="rot", point=piv, direction=(0, 0, 1), rest=math.inf))
        dummy = E.Body("stem", m3.Manifold.cube([0.1, 0.1, 0.1]).translate([9, 9, 9]), "driven", dof="stem",
                       point=(9, 9, 9), direction=(0, 0, 1))
        w = E.World(bodies + [dummy])
        w.settle()
        q0 = W.q
        for _ in range(20):
            w.step("stem", dq=0.01)
        moved = math.degrees(W.q - q0)
        print("mainspring %s click: arbor moved %.2f deg" % ("with" if with_click else "without", moved))
        if with_click and abs(moved) > 2.0:
            return False
        if not with_click and moved > -5.0:
            return False
    return True


def detent():
    star = S.star_wheel(8, 1.6, 2.0, 0, 1.0)
    det, piv = S.detent_lever(8, 1.6, 2.0, 0, 1.0)
    W = E.Body("star", star, "driven", dof="stem", point=(0, 0, 0), direction=(0, 0, 1))
    D = E.Body("detent", det, "spring", dof="rot", point=piv, direction=(0, 0, 1), rest=math.inf)
    w = E.World([W, D])
    w.settle()
    qs = []
    for _ in range(45):                       # one tooth = 45 deg
        assert w.step("star", dq=math.radians(1.0)), "detent jammed"
        qs.append(D.q)
    lift = max(abs(q - qs[0]) for q in qs)
    back = abs(qs[-1] - qs[0])
    print("detent: lift %.3f rad, back to rest within %.4f rad" % (lift, back))
    return lift > 0.05 and back < 0.02


def _block(name, lo, hi, kind, **kw):
    return E.Body(name, S.box(lo, hi), kind, **kw)


def spring_through_link():
    """A returning spring pushes a free part on its rest side (a yoke spring returning the sliding
    pinion through the yoke): spring S (slide x, rest +x) -> free link L -> free block F, up to a wall.
    It must not push the mainspring body, and not push another spring away from that spring's rest."""
    wall = _block("wall", (3.0, -1, 0), (3.5, 1, 1), "fixed")
    spr = _block("spring", (0.0, -0.5, 0.2), (0.5, 0.5, 0.8), "spring", dof="slide", direction=(1, 0, 0), rest=math.inf)
    link = _block("link", (0.5, -0.5, 0.2), (1.0, 0.5, 0.8), "contact", dof="slide", direction=(1, 0, 0))
    blk = _block("block", (1.0, -0.5, 0.2), (1.5, 0.5, 0.8), "contact", dof="slide", direction=(1, 0, 0))
    w = E.World([wall, spr, link, blk])
    w.settle()
    ok1 = abs(blk.q - 1.5) < 0.02 and abs(link.q - 1.5) < 0.02 and abs(spr.q - 1.5) < 0.02
    # the same against the mainspring body (kind main): the spring stops at it
    m = _block("main", (1.0, -0.5, 0.2), (1.5, 0.5, 0.8), "main", dof="slide", direction=(1, 0, 0), rest=None)
    spr2 = _block("spring", (0.0, -0.5, 0.2), (0.5, 0.5, 0.8), "spring", dof="slide", direction=(1, 0, 0), rest=math.inf)
    link2 = _block("link", (0.5, -0.5, 0.2), (1.0, 0.5, 0.8), "contact", dof="slide", direction=(1, 0, 0))
    w2 = E.World([wall.__class__("wall", wall.man, "fixed"), spr2, link2, m])
    w2.settle()
    ok2 = abs(m.q) < 1e-9 and spr2.q < 0.01
    # against an opposing spring (rest -x): neither drives the other off its rest side
    s3 = _block("s3", (0.0, -0.5, 0.2), (0.5, 0.5, 0.8), "spring", dof="slide", direction=(1, 0, 0), rest=math.inf)
    s4 = _block("s4", (0.5, -0.5, 0.2), (1.0, 0.5, 0.8), "spring", dof="slide", direction=(1, 0, 0), rest=-math.inf)
    w3 = E.World([s3, s4, _block("w0", (-1.0, -1, 0), (0.0, 1, 1), "fixed"), _block("w1", (2.0, -1, 0), (2.5, 1, 1), "fixed")])
    w3.settle()
    ok3 = abs(s3.q) < 0.01 and abs(s4.q) < 0.01
    print("spring through a link: block %.3f link %.3f (expect 1.5); vs mainspring %s; opposing springs %s"
          % (blk.q, link.q, ok2, ok3))
    return ok1 and ok2 and ok3


def pull_moves_no_rider():
    """On a pure pull step (the stem slides, does not turn) a body riding on the stem is not counted as
    moved; on a turning step it is."""
    stem = E.Body("stem", S.cyl_x(0, 0, 0, 5, 0.5, 32), "driven", dof="stem", point=(0, 0, 0), direction=(1, 0, 0))
    rider = E.Body("rider", S.cyl_x(0, 0, 1, 2, 0.8, 32), "contact", dof="slide", direction=(1, 0, 0), carrier="stem")
    w = E.World([stem, rider])
    w.dqs = {"stem": (0.0, 0.03)}
    a = [o.name for o in w.moved_now()]
    w.dqs = {"stem": (0.05, 0.0)}
    b = [o.name for o in w.moved_now()]
    print("moved on a pull step: %s; on a turning step: %s" % (a, b))
    return a == ["stem"] and set(b) == {"stem", "rider"}


def rider_gives_way():
    """A free part carried by the turning stem into a fixed ramp slides back along its own freedom (as
    Breguet teeth push the sliding pinion off a winding pinion that cannot turn)."""
    stem = E.Body("stem", S.cyl_x(0, 0, 0, 5, 0.3, 48), "driven", dof="stem", point=(0, 0, 0), direction=(1, 0, 0))
    arm = E.Body("arm", S.box((1.0, 0.3, -0.1), (1.2, 1.5, 0.1)), "contact", dof="slide", direction=(1, 0, 0),
                 carrier="stem")
    pts = [(x, y, z) for y in (0.2, 1.6) for (x, z) in ((0.6, 0.92), (1.4, 0.12), (0.6, 1.2), (1.4, 1.2))]
    ramp = E.Body("ramp", m3.Manifold.hull_points(pts), "fixed")
    w = E.World([stem, arm, ramp])
    ok = all(w.step("stem", dq=math.radians(2.0)) for _ in range(15))
    print("rider on the stem pushed into a fixed 45 deg ramp: not blocked=%s, slid %.3f (expect < -0.1)" % (ok, arm.q))
    return ok and arm.q < -0.1


def rider_drives_steep_face():
    """...but against a face square to its motion it cannot give way along its freedom: it drives."""
    stem = E.Body("stem", S.cyl_x(0, 0, 0, 5, 0.3, 48), "driven", dof="stem", point=(0, 0, 0), direction=(1, 0, 0))
    arm = E.Body("arm", S.box((1.0, 0.3, -0.1), (1.2, 1.5, 0.1)), "contact", dof="slide", direction=(1, 0, 0),
                 carrier="stem")
    paddle = E.Body("paddle", S.box((0.5, 0.3, 0.1), (1.7, 1.5, 0.3)), "contact", dof="rot", point=(0, 0, 0),
                    direction=(1, 0, 0))
    w = E.World([stem, arm, paddle])
    ok = all(w.step("stem", dq=math.radians(2.0)) for _ in range(10))
    print("rider against a square face: not blocked=%s, paddle turned %.1f deg (expect ~20), rider slid %.3f"
          % (ok, math.degrees(paddle.q), arm.q))
    return ok and abs(math.degrees(paddle.q) - 20) < 2 and abs(arm.q) < 0.01


def rider_drives_when_chain_blocked():
    """...and where giving way would push a part behind it into something that cannot move (a sliding
    pinion backed by the yoke, the yoke by the setting lever), it does not give way: it drives."""
    stem = E.Body("stem", S.cyl_x(0, 0, 0, 5, 0.3, 48), "driven", dof="stem", point=(0, 0, 0), direction=(1, 0, 0))
    arm = E.Body("arm", S.box((1.0, 0.3, -0.1), (1.2, 1.5, 0.1)), "contact", dof="slide", direction=(1, 0, 0),
                 carrier="stem")
    link = _block("link", (0.9, 0.3, -0.1), (1.0, 1.5, 0.1), "contact", dof="slide", direction=(1, 0, 0))
    lever = _block("lever", (0.8, 0.3, -0.1), (0.9, 1.5, 0.1), "contact", dof="slide", direction=(1, 0, 0))
    wall = _block("wall", (0.7, 0.3, -0.1), (0.8, 1.5, 0.1), "fixed")
    pts = [(x, y, z) for y in (0.2, 1.6) for (x, z) in ((0.6, 0.92), (1.4, 0.12), (0.6, 1.2), (1.4, 1.2))]
    ramp = E.Body("ramp", m3.Manifold.hull_points(pts), "contact", dof="rot", point=(0, 0, 0), direction=(1, 0, 0))
    w = E.World([stem, arm, link, lever, wall, ramp])
    ok = all(w.step("stem", dq=math.radians(2.0)) for _ in range(10))
    print("rider on a ramp, backed by a link against a wall: not blocked=%s, ramp turned %.1f deg (expect ~8: "
          "contact from about 12 deg), rider slid %.3f" % (ok, math.degrees(ramp.q), arm.q))
    return ok and math.degrees(ramp.q) > 5 and abs(arm.q) < 0.02


def many_tiny_patches():
    """A light contact split over many tiny patches (40 tips, each under PATCH_FLOOR_FRAC x TOL, together
    above TOL) still counts when the engine works out how far the pushed part may move: it slides."""
    tips = None
    for k in range(40):
        y = -0.98 + 0.05 * k
        tip = S.box((-0.5, y, 0.4), (0.015, y + 0.02, 0.42))         # 0.015 x 0.02 x 0.02 into the block
        tips = tip if tips is None else tips + tip
    drv = E.Body("drv", tips, "driven", dof="stem", point=(0, 0, 0), direction=(1, 0, 0))
    blk = _block("blk", (0.0, -1.0, 0.0), (1.0, 1.0, 1.0), "contact", dof="slide", direction=(1, 0, 0))
    w = E.World([drv, blk])
    v = w.posed(drv) ^ w.posed(blk)
    sizes = [c.volume() for c in v.decompose()]
    ok = all(w.step("drv", dp=0.01) for _ in range(5))
    print("40 tiny patches (largest %.1e, total %.1e mm^3, TOL %.0e): pushed 0.05, ok=%s, block moved %.3f"
          % (max(sizes), sum(sizes), E.TOL, ok, blk.q))
    return max(sizes) < E.PATCH_FLOOR_FRAC * E.TOL and sum(sizes) > E.TOL and ok and blk.q > 0.04


def spring_carrier_stops_at_wheel_contact():
    """A returning spring that carries a wheel (a sprung setting-wheel lever) stops where the wheel meets
    a fixed part; it does not push the wheel through it (audit F1, probe p1)."""
    lever = E.Body("lever", S.box((-0.3, -0.3, 0), (0.3, 5.0, 0.5)), "spring", dof="rot", point=(0, 0, 0),
                   direction=(0, 0, 1), rest=math.inf)
    wheel = E.Body("wheel", S.cyl_z(0, 5.0, 0.5, 1.0, 1.0, 64), "contact", dof="rot", point=(0, 5.0, 0),
                   direction=(0, 0, 1), carrier="lever")
    wall = E.Body("wall", S.box((-3.0, 4.0, 0.6), (-1.2, 6.0, 0.9)), "fixed")
    w = E.World([lever, wheel, wall])
    for _ in range(6):
        w.relax(lever)
    v = w.pen(wheel)
    print("sprung lever carrying a wheel into a wall: lever %.4f rad, wheel/wall overlap %.2e (TOL %.0e)"
          % (lever.q, v, E.TOL))
    return v <= E.TOL and lever.q > 0.03


def spring_pushes_while_touching_plate():
    """A spring resting on a fixed plate with a legal touching overlap (TOL/2 < v <= TOL) still pushes a
    free part ahead of it (a yoke on the plate returning the sliding pinion; audit F2, probe p2)."""
    res = []
    for dz in (0.0, 3e-4):
        floor = _block("floor", (-1, -1, -1), (5, 1, 0.2 + dz), "fixed")
        spr = _block("spring", (0.0, -0.5, 0.2), (0.5, 0.5, 0.8), "spring", dof="slide", direction=(1, 0, 0),
                     rest=math.inf)
        blk = _block("block", (0.6, -0.5, 0.25), (1.1, 0.5, 0.8), "contact", dof="slide", direction=(1, 0, 0))
        wall = _block("wall", (3.0, -1, 0.25), (3.5, 1, 1), "fixed")
        w = E.World([floor, spr, blk, wall])
        v0 = w._pen1(spr, None, {"floor"})
        for _ in range(20):
            w.relax(spr)
        print("spring on a plate (overlap %.1e): block pushed to %.3f (expect 1.9)" % (v0, blk.q))
        res.append(abs(blk.q - 1.9) < 0.02)
    return all(res)


def main_try_from_constants():
    """The mainspring's try per step is the module's MAIN_TRY (from constants.py, as the brief states)."""
    import constants as C
    got = []
    for arc in (C.MAIN_TRY, 0.5 * C.MAIN_TRY):
        E.MAIN_TRY = arc
        drv = _block("drv", (5, 5, 5), (6, 6, 6), "driven", dof="stem", point=(0, 0, 0), direction=(1, 0, 0))
        bar = E.Body("barrel", S.cyl_z(0, 0, 0, 1, 2.0, 64), "main", dof="rot", point=(0, 0, 0), direction=(0, 0, 1),
                     rest=-math.inf)
        w = E.World([drv, bar])
        w.step("drv", dq=0.0)
        got.append(-bar.q * bar.radius)
    E.MAIN_TRY = C.MAIN_TRY
    print("mainspring try per step: %.4f and %.4f mm (MAIN_TRY %.3f, then half)" % (got[0], got[1], C.MAIN_TRY))
    return abs(got[0] - C.MAIN_TRY) < 1e-3 and abs(got[1] - 0.5 * C.MAIN_TRY) < 1e-3


def spring_push_switch():
    """World.spring_push (class attribute) switches spring pushing off for every new world."""
    def run():
        spr = _block("spring", (0.0, -0.5, 0.2), (0.5, 0.5, 0.8), "spring", dof="slide", direction=(1, 0, 0),
                     rest=math.inf)
        blk = _block("block", (0.6, -0.5, 0.2), (1.1, 0.5, 0.8), "contact", dof="slide", direction=(1, 0, 0))
        wall = _block("wall", (3.0, -1, 0), (3.5, 1, 1), "fixed")
        w = E.World([spr, blk, wall])
        for _ in range(20):
            w.relax(spr)
        return blk.q
    on = run()
    E.World.spring_push = False
    try:
        off = run()
    finally:
        E.World.spring_push = True
    print("spring pushing on: block to %.3f; off: %.3f" % (on, off))
    return abs(on - 1.9) < 0.02 and abs(off) < 1e-9


def resting_rub_lends_no_allowance():
    """A face steeper than the friction cone locks, even when the pushed part also rests (touching, within
    TOL) on a fast-moving surface of the driver far from its axis: only contacts that push in this step
    lend a friction allowance (audit P2-6, probe p4_budget)."""
    def box(lo, hi):
        return m3.Manifold.cube([hi[i] - lo[i] for i in range(3)]).translate(list(lo))
    out = []
    for rub in (False, True):
        slope, c = 0.3, 0.5
        face = m3.Manifold.extrude(m3.CrossSection([[(0.3, c - slope * 0.3), (1.0, c - slope * 1.0), (1.0, 1.5),
                                                     (0.3, 1.5)]]), 0.5)
        tooth = box((0.4, -0.5, 0.0), (0.9, 0.15, 0.5))
        ann = (m3.Manifold.cylinder(0.1, 5.0, 5.0, 512) - m3.Manifold.cylinder(0.1, 3.5, 3.5, 512)).translate([0, 0, 1.0])
        eps = 2.5e-4 if rub else -0.05
        P = face + box((0.3, 1.4, 0.0), (1.0, 2.0, 0.5)) + box((0.3, 1.5, 0.0), (1.0, 2.0, 1.3)) + \
            box((0.3, 1.5, 1.1 - eps), (4.2, 2.0, 1.3))
        D = E.Body("D", tooth + ann, "driven", dof="stem", point=(0, 0, 0), direction=(0, 0, 1))
        B = E.Body("P", P, "contact", dof="slide", direction=(1, 0, 0))
        w = E.World([D, B])
        blocked = 0
        for _ in range(40):
            if not w.step("D", dq=math.radians(0.5)):
                blocked += 1
                if blocked >= 3:
                    break
        print("locking face, rub=%s: driver %.1f deg, blocked %d, slid %.4f mm" % (rub, math.degrees(D.q), blocked, B.q))
        out.append((blocked, B.q))
    return all(bl >= 3 and q < 0.05 for bl, q in out)


def pull_without_spec():
    """grade.pull_of: no spec (a caller that builds the world itself) means the default pull."""
    import constants as C
    import grade as GR
    ok = GR.pull_of(None) == C.PULL and GR.pull_of({}) == C.PULL and GR.pull_of({"pull": 0.6}) == 0.6
    print("pull_of(None) = %s (PULL %s)" % (GR.pull_of(None), C.PULL))
    return ok


def phase_is_bounded():
    """phase() (coming to rest) stops at its cap on a grossly overlapping world and leaves the state as it
    is; the rest check then judges it."""
    bodies = []
    for k in range(3):
        g = G.spur(16, 0.2, 0, 1.0, thin=0.01).translate([1.2 * k, 0, 0])      # far too close: teeth deep in teeth
        bodies.append(E.Body("w%d" % k, g, "contact", dof="rot", point=(1.2 * k, 0, 0), direction=(0, 0, 1)))
    w = E.World(bodies)
    old = E.PHASE_MAX_RESOLVES
    E.PHASE_MAX_RESOLVES = 10
    try:
        t = time.time()
        ok = w.phase()
        dt = time.time() - t
    finally:
        E.PHASE_MAX_RESOLVES = old
    print("gross overlap (max %.3f mm^3): phase ok=%s %s in %.1f s" % (w.max_pen(), ok, w.phase_stats, dt))
    return w.phase_stats["capped"] and not ok and w.phase_stats["resolves"] < 10 + 30


def touching_can_be_pushed():
    """A part resting on a fixed face with an overlap between TOL/2 and TOL (touching) can still be
    pushed along that face: one threshold, TOL."""
    area = 1.0
    depth = 0.75 * E.TOL / area                        # overlap 0.75 TOL with the base
    base = _block("base", (-5, -1, -1), (5, 1, 0.0), "fixed")
    blk = _block("blk", (0, -0.5, -depth), (1, 0.5, 1 - depth), "contact", dof="slide", direction=(1, 0, 0))
    drv = _block("drv", (-1, -0.5, 0.1), (0.0, 0.5, 0.9), "driven", dof="stem", point=(0, 0, 0), direction=(1, 0, 0))
    w = E.World([base, blk, drv])
    ok = all(w.step("drv", dp=0.02) for _ in range(5))
    print("resting at 0.75 TOL, pushed 0.1 along the face: ok=%s, moved %.3f" % (ok, blk.q))
    return ok and abs(blk.q - 0.1) < 0.01


def fit_clearance():
    """A wheel drawn line to line on a fixed post (both faceted): the overlap is above TOL until the rig's
    fit rule widens the wheel's bore; then it turns."""
    import grade as GR
    post = S.cyl_z(0, 0, -1, 2, 0.5, 64)
    wheel = S.cyl_z(0, 0, 0, 1, 2.0, 64) - S.cyl_z(0, 0, -0.1, 1.1, 0.5, 64).rotate([0, 0, 360 / 128])
    before = (post ^ wheel).volume()
    parts, sup = {"wheel": wheel, "post": post}, {}
    defs = [dict(name="wheel", parts=["wheel"], kind="contact", dof="rot", point=(0, 0, 0), direction=(0, 0, 1)),
            dict(name="fixed", parts=["post"], kind="fixed")]
    GR.relieve_fits(parts, sup, defs)
    after = (parts["post"] ^ parts["wheel"]).volume()
    print("line-to-line fit: overlap %.6f -> %.6f mm^3 (TOL %.4f)" % (before, after, E.TOL))
    return before > E.TOL and after <= E.TOL


def phase_gears():
    """Two wheels drawn tooth through tooth are turned into their gaps before the rest check."""
    a = G.spur(12, 0.2, 0, 1.0, thin=0.01)
    b = G.spur(24, 0.2, 0, 1.0, thin=0.01).translate([3.6, 0, 0])      # unphased: teeth collide
    A = E.Body("a", a, "contact", dof="rot", point=(0, 0, 0), direction=(0, 0, 1))
    B = E.Body("b", b, "contact", dof="rot", point=(3.6, 0, 0), direction=(0, 0, 1))
    w = E.World([A, B])
    p0 = w.max_pen()
    ok = w.phase()
    print("phase: overlap %.5f -> %.6f, ok=%s" % (p0, w.max_pen(), ok))
    return p0 > E.TOL and ok


def carried_wheel():
    """A wheel riding on a swinging lever (carrier other than the stem) moves with the lever, and the
    lever answers for it: swinging the lever into a fixed wall is stopped by the wheel."""
    lever = E.Body("lever", S.box((-0.3, -0.3, 0), (0.3, 5.0, 0.5)), "contact", dof="rot", point=(0, 0, 0),
                   direction=(0, 0, 1))
    wheel = E.Body("wheel", S.cyl_z(0, 5.0, 0.5, 1.0, 1.0, 64), "contact", dof="rot", point=(0, 5.0, 0),
                   direction=(0, 0, 1), carrier="lever")
    wall = E.Body("wall", S.box((-3.0, 4.0, 0.6), (-1.2, 6.0, 0.9)), "fixed")
    drv = E.Body("drv", S.box((0.3, 2.0, 0.0), (0.8, 2.5, 0.5)), "driven", dof="stem", point=(0, 0, 0), direction=(-1, 0, 0))
    w = E.World([lever, wheel, wall, drv])
    moved_ok = w.step("drv", dp=0.05)
    centre = (w.matrix(wheel) @ np.array([0, 5.0, 0, 1.0]))[:3]
    swung = centre[0] < -0.05
    blocked = False
    for _ in range(40):
        if not w.step("drv", dp=0.05):
            blocked = True
            break
    print("carried wheel: follows the lever %s (centre x %.3f); stopped by the wall %s" % (swung, centre[0], blocked))
    return moved_ok and swung and blocked


def force_direction():
    """force_signs: the side a contact pushes a part to."""
    wall = _block("wall", (1.0, -1, 0), (2.0, 1, 1), "fixed")
    blk = _block("blk", (0.0, -0.5, 0.2), (1.01, 0.5, 0.8), "spring", dof="slide", direction=(1, 0, 0), rest=math.inf)
    w = E.World([wall, blk])
    s = w.force_signs(blk)
    print("contact pushes the block towards %s (expect -x)" % (s,))
    return s == (-1.0,)


def stem_protrudes_at_crown_end():
    """bounds_check: stem material outside the case counts only at the +x end."""
    import constants as C
    import grade as GR
    cx, cy = C.CASE_CENTRE
    zm = 0.5 * (C.CASE_Z[0] + C.CASE_Z[1])
    R = C.CASE_RADIUS
    spec = {"mobiles": {"stem": {"parts": ["stem"]}}}
    crown = S.cyl_x(cy, zm, cx + R - 2.0, cx + R + 1.0, 0.3, 32)
    wrong = S.cyl_x(cy, zm, cx - R - 1.0, cx - R + 2.0, 0.3, 32)
    ok_crown, d1 = GR.bounds_check(spec, {"stem": crown})
    ok_wrong, d2 = GR.bounds_check(spec, {"stem": wrong})
    print("stem out at +x: %s %s; out at -x only: %s %s" % (ok_crown, d1, ok_wrong, d2))
    return ok_crown and not ok_wrong


def early_stop_bound():
    """grade._cannot_exceed (anchor early stop): unrun steps count as passed, whole-build 0 after a failure."""
    import constants as C
    import grade as GR
    W = C.STEP_WEIGHTS
    b = 0.5 * (W["assemble"] + W["hold"])
    cases = [({"assemble": True}, b, False),                                  # nothing failed yet
             ({"assemble": True, "wind": False}, b, False),                   # 0.4 still possible
             ({"assemble": True, "wind": False, "hold": True, "run": False, "backward": False, "set": False}, b, False),
             ({"assemble": True, "wind": False, "hold": True, "run": False, "backward": False, "set": False,
               "return": False}, b, True),
             ({"assemble": False}, 0.5 * (1 - W["assemble"]), True),
             ({"assemble": True}, 0.99, False)]
    got = [GR._cannot_exceed(k, bound) == want for k, bound, want in cases]
    print("early stop bound cases: %s" % got)
    return all(got)


if __name__ == "__main__":

    t = time.time()
    res = {"gear": gear_pair(), "ratchet": ratchet_pawl(), "mainspring": mainspring_click(), "detent": detent(),
           "spring_through_link": spring_through_link(), "pull_moves_no_rider": pull_moves_no_rider(),
           "rider_gives_way": rider_gives_way(), "rider_drives_steep_face": rider_drives_steep_face(),
           "rider_drives_when_chain_blocked": rider_drives_when_chain_blocked(),
           "many_tiny_patches": many_tiny_patches(), "phase_is_bounded": phase_is_bounded(), "pull_without_spec": pull_without_spec(), "resting_rub_lends_no_allowance": resting_rub_lends_no_allowance(), "spring_push_switch": spring_push_switch(), "main_try_from_constants": main_try_from_constants(),
           "spring_carrier_stops_at_wheel_contact": spring_carrier_stops_at_wheel_contact(),
           "spring_pushes_while_touching_plate": spring_pushes_while_touching_plate(), "touching_can_be_pushed": touching_can_be_pushed(), "fit_clearance": fit_clearance(),
           "phase_gears": phase_gears(), "carried_wheel": carried_wheel(), "force_direction": force_direction(),
           "stem_protrudes_at_crown_end": stem_protrudes_at_crown_end(),
           "early_stop_bound": early_stop_bound()}
    print(res, "%.1f s" % (time.time() - t))
    sys.exit(0 if all(res.values()) else 1)
