"""The drive test does not depend on where in its backlash the driven mobile is delivered (SESSION.md Decisions,
15 Nov 00:50, part 2): before each push the driver is turned in the push's sense to its first contact with the
held driven mobile (geometry.watch.drive_contact), and the push is measured from there.
    python3 tests/test_drive.py
Run from the repository root (about 3 to 6 minutes on 4 CPUs). Through the real STEP loader and mesh_run:
  - an honest 30/12 pair, module 0.2, with a large backlash (32 percent of a pitch, like ml01's intermediate and
    centre pinion), delivered mid-backlash, 90 percent of the way to the flank the push drives, and 90 percent of
    the way to the other flank: the same pass/fail and the same face width H; V, V / H and the strength check's
    split by part (drive_parts) within DELIVERY_TOL of mid-backlash; the contact turns found differ by about the
    backlash. Why not closer: every drive step is at a whole driver pitch, so all of them sample one roll
    position; turning D forward to contact moves that roll position by the contact turn, which depends on the
    delivered phase, and V varies a few percent over the roll (measured 4.1 percent on this pair; the old rule
    gave V 0 on the far flank);
  - the contact search at half its resolution (twice the scan steps; one more halving) moves V by < 0.1 percent;
  - a toothless disc 0.01 mm inside the driver's tip circle (nothing for D to reach within one pitch at any step,
    an unbounded backlash): no jam and engaged hold, every drive step finds no contact, the drive test fails.
Exits 1 if any case is off."""
import math
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
from geometry import watch as W                     # noqa: E402
from geometry import watch_gears_cad as GC          # noqa: E402
from test_exploit_rules import movement             # noqa: E402  (writes STEP parts, loads them like the grader)

BAD = []
DELIVERY_TOL = 0.05     # relative: see the docstring (measured 0.041 on this pair)
ZA, ZB, M, BACKLASH = 30, 12, 0.2, 0.1        # BACKLASH: tooth thinning of each gear on its pitch circle (mm)
X0, Z0, Z1 = 40.0, 3.0, 3.6                   # far from the supplied barrel


def check(label, ok, info=""):
    if not ok:
        BAD.append(label)
    print("%-4s %-78s %s" % ("ok" if ok else "OFF", label, info), flush=True)


def pair(turn_b_deg=0.0, extra_distance=0.0):
    """Driver a (ZA teeth) and driven b (ZB teeth plus an arbor part on top) at the meshing distance plus
    extra_distance; b's teeth centred in a's tooth space (mid-backlash), then turned by turn_b_deg."""
    c = M * (ZA + ZB) / 2.0 + extra_distance
    parts = {"wa": GC.gear(ZA, M, Z0, Z1, phase_deg=0.0, x=X0, y=0, backlash=BACKLASH),
             "wb": GC.gear(ZB, M, Z0, Z1, phase_deg=180.0 + 180.0 / ZB + turn_b_deg, x=X0 + c, y=0, backlash=BACKLASH),
             "arb": GC.cyl(X0 + c, 0, Z1, Z1 + 1.0, 0.3),
             "block": GC.box((X0 + 25, 0, 0), (X0 + 26, 1, 1))}
    return movement(parts, ["block"], {"a": ((X0, 0), ["wa"]), "b": ((X0 + c, 0), ["wb", "arb"])})


def summary(x):
    return "jam %.5f gap %.4f V %.6f ratio %.4f H %.3f contact %.4f no-contact steps %d pass %s" % (
        x["worst_volume"], x["largest_gap"], x["smallest_drive_overlap"], x["smallest_drive_ratio"],
        x["smallest_drive_height"], x["largest_drive_contact"], x["drive_steps_without_contact"], W.Movement.mesh_passes(x))


def close(a, b, rel):
    return abs(a - b) <= rel * max(abs(a), abs(b))


def test_backlash_phase():
    total = 2 * BACKLASH                              # circular backlash of the pair on the pitch circle (mm)
    print("backlash %.3f mm = %.0f percent of the pitch %.4f" % (total, 100 * total / (math.pi * M), math.pi * M))
    flank = math.degrees(0.45 * total / (M * ZB / 2.0))   # turn of b that takes it 90 percent of the way to a flank
    runs, parts = {}, {}
    for label, t in (("mid-backlash", 0.0), ("one flank", flank), ("other flank", -flank)):
        m = pair(t)
        runs[label] = x = m.mesh_run("a", ZA, "b", ZB)
        parts[label] = m.drive_parts("a", ZA, "b", ZB)["b"]
        print("     %-13s (b turned %+.3f deg): %s; drive_parts b %s" % (label, t, summary(x),
              {k: round(v, 6) for k, v in parts[label].items()}), flush=True)
    mid = runs["mid-backlash"]
    check("mid-backlash pair passes the mesh test", W.Movement.mesh_passes(mid), summary(mid))
    contacts = sorted(x["largest_drive_contact"] for x in runs.values())
    check("the three deliveries really differ: contact turns spread over > 0.25 of a pitch",
          contacts[-1] - contacts[0] > 0.25, "contacts %s" % ["%.4f" % c for c in contacts])
    for label in ("one flank", "other flank"):
        x = runs[label]
        check("%s: same pass/fail as mid-backlash" % label, W.Movement.mesh_passes(x) == W.Movement.mesh_passes(mid))
        check("%s: V within DELIVERY_TOL of mid-backlash" % label,
              close(x["smallest_drive_overlap"], mid["smallest_drive_overlap"], DELIVERY_TOL),
              "%.6f vs %.6f" % (x["smallest_drive_overlap"], mid["smallest_drive_overlap"]))
        check("%s: V / H ratio within DELIVERY_TOL of mid-backlash" % label,
              close(x["smallest_drive_ratio"], mid["smallest_drive_ratio"], DELIVERY_TOL),
              "%.4f vs %.4f" % (x["smallest_drive_ratio"], mid["smallest_drive_ratio"]))
        check("%s: face width H (strength b) the same" % label,
              abs(x["smallest_drive_height"] - mid["smallest_drive_height"]) <= 1e-6)
        check("%s: drive_parts split of the driven gear within DELIVERY_TOL" % label,
              close(parts[label]["wb"], parts["mid-backlash"]["wb"], DELIVERY_TOL) and parts[label]["arb"] == 0.0,
              "%.6f vs %.6f" % (parts[label]["wb"], parts["mid-backlash"]["wb"]))


def test_resolution():
    m = pair(0.0)
    keep = W.DRIVE_CONTACT_SCAN, W.DRIVE_CONTACT_HALVINGS
    out = {}
    try:
        for scan, hv in (keep, (2 * keep[0], keep[1]), (keep[0], keep[1] + 1)):
            W.DRIVE_CONTACT_SCAN, W.DRIVE_CONTACT_HALVINGS = scan, hv
            out[(scan, hv)] = m.mesh_run("a", ZA, "b", ZB)["smallest_drive_overlap"]
    finally:
        W.DRIVE_CONTACT_SCAN, W.DRIVE_CONTACT_HALVINGS = keep
    base = out[keep]
    for k, v in out.items():
        if k != keep:
            check("contact search at half the resolution (scan %d, halvings %d): V within 0.1 percent" % k,
                  close(v, base, 0.001), "%.6f vs %.6f" % (v, base))


def test_no_contact():
    # the driven mobile is a plain disc whose rim is 0.01 mm short of the driver's tip circle: D can turn any amount
    # without touching it, while the two stay within the engaged distance
    ra = M * ZA / 2.0 + M                      # driver tip radius (addendum 1.0 m)
    r_disc = 2.0
    c = ra + r_disc + 0.01
    parts = {"wa": GC.gear(ZA, M, Z0, Z1, phase_deg=0.0, x=X0, y=0, backlash=BACKLASH),
             "disc": GC.cyl(X0 + c, 0, Z0, Z1, r_disc), "block": GC.box((X0 + 25, 0, 0), (X0 + 26, 1, 1))}
    m = movement(parts, ["block"], {"a": ((X0, 0), ["wa"]), "b": ((X0 + c, 0), ["disc"])})
    x = m.mesh_run("a", ZA, "b", ZB)
    print("     disc short of the tips: %s" % summary(x), flush=True)
    check("disc short of the tips: no jam and engaged hold",
          x["worst_volume"] <= W.VOL_TOL and x["largest_gap"] <= W.ENGAGE_GAP)
    check("disc short of the tips: no contact within one pitch at every drive step",
          x["drive_steps_without_contact"] == x["steps"] // 8 and x["smallest_drive_overlap"] == 0.0)
    check("disc short of the tips: fails the mesh test (the drive test)", not W.Movement.mesh_passes(x)
          and not W.Movement.drive_passes(x))


if __name__ == "__main__":
    for t in (test_backlash_phase, test_resolution, test_no_contact):
        t()
    print("all ok" if not BAD else "OFF: %s" % BAD)
    sys.exit(1 if BAD else 0)
