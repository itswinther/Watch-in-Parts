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


if __name__ == "__main__":
    t = time.time()
    res = {"gear": gear_pair(), "ratchet": ratchet_pawl(), "mainspring": mainspring_click(), "detent": detent()}
    print(res, "%.1f s" % (time.time() - t))
    sys.exit(0 if all(res.values()) else 1)
