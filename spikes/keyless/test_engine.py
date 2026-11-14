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


if __name__ == "__main__":

    t = time.time()
    res = {"gear": gear_pair(), "ratchet": ratchet_pawl(), "mainspring": mainspring_click(), "detent": detent(),
           "spring_through_link": spring_through_link(), "pull_moves_no_rider": pull_moves_no_rider(),
           "rider_gives_way": rider_gives_way(),
           "touching_can_be_pushed": touching_can_be_pushed(), "fit_clearance": fit_clearance(),
           "phase_gears": phase_gears(), "carried_wheel": carried_wheel(), "force_direction": force_direction()}
    print(res, "%.1f s" % (time.time() - t))
    sys.exit(0 if all(res.values()) else 1)
