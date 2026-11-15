"""Quick tests of the gear strength check (one-job mode, check `strength`, SESSION.md Decisions 17:56 option 2).
    python3 tests/test_strength.py [--write-lewis]
Run from the repository root; a few minutes (real mesh runs of the barrel and 12-tooth pinions).
--write-lewis rebuilds geometry/data/lewis_y.json from geometry.watch.lewis_form_factor and exits.
Cases:
  sheets     the constants equal their supplier-sheet cells (DS-101 Table 2a, DS-201 sections 2 and 8)
  lewis      the frozen Y table holds every tooth count MIN_TEETH..MAX_TEETH and equals lewis_form_factor
  arithmetic a two-mesh going train with given module and face width: T, F and sigma by hand, to 1e-6; a
             motion-work mesh off the path to the seconds hand is not rated; a train mesh that fails the mesh test
             fails the check; a brass pinion on the barrel mesh fails where steel passes
  material   a mobile without "material", or with one that has no tensile allowable, is a format error in
             one-job mode (the grader's C1 gate "files" fails) and is ignored in stage mode
  barrel     the supplied barrel drives a real 12-tooth CAD pinion 0.8 thick: steel passes, brass fails
  part_materials  "part_materials" with a designation that does not qualify, a part not in that mobile, or not an
             object, is a format error in one-job mode (also through the grader's C1) and is ignored in stage mode
  per_part   a mobile of two CAD parts, a steel pinion ("pin", driven by the barrel) and a brass wheel ("wheel",
             driving a 12-tooth pinion on mobile q): the barrel mesh picks "pin" and rates it in steel, the q mesh
             picks "wheel" and rates it in brass (drive overlap by part, sigma by hand); without part_materials
             the brass mobile fails at its pinion
  weights    P1 totals 23 and P3 27"""
import json
import os
import shutil
import sys
import tempfile
from fractions import Fraction

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))
# the cases below place their pinions on main's 1.0 mm drum (z 0.1 to 0.9): run them on main's 6.6 mm barrel
# unless told otherwise (geometry/watch.py defaults to the thin barrel on b/thin-4mm)
os.environ.setdefault("WATCH_THIN_BARREL", "0")
from geometry import core            # noqa: E402
from geometry import watch as W      # noqa: E402
from geometry.core import FormatError  # noqa: E402
LEWIS_FILE = os.path.join(ROOT, "geometry", "data", "lewis_y.json")


def case_sheets():
    bad = W.check_strength_sheets()
    assert bad == [], bad
    assert W.MATERIAL_ALLOWABLE_MPA == {"AD-CW614N": 110.0, "AD-C100-HT": 725.0}, W.MATERIAL_ALLOWABLE_MPA
    return "BARREL_TORQUE_MAX_NMM %s, allowables %s" % (W.BARREL_TORQUE_MAX_NMM, W.MATERIAL_ALLOWABLE_MPA)


def case_lewis():
    doc = W.lewis_table_doc()
    with open(LEWIS_FILE) as f:
        frozen = json.load(f)
    assert frozen == doc, "geometry/data/lewis_y.json differs from lewis_form_factor (rebuild with --write-lewis)"
    assert sorted(W.LEWIS_Y) == list(range(W.MIN_TEETH, W.MAX_TEETH + 1))
    ys = [W.LEWIS_Y[z] for z in range(W.MIN_TEETH, W.MAX_TEETH + 1)]
    assert all(b >= a for a, b in zip(ys, ys[1:])), "Y must not fall as teeth are added"
    return "Y(12) %.4f, Y(24) %.4f, Y(96) %.4f, rack tip radius %.4f m" % (W.LEWIS_Y[12], W.LEWIS_Y[24], W.LEWIS_Y[96],
                                                                         W.rack_tip_radius())


class _Fake:
    """Just what strength_run reads from a Movement."""
    def __init__(self, meshes, materials, seconds):
        self.meshes = meshes
        self.barrel_speed = W.BARREL_TURNS_PER_HOUR
        self.mobiles = {k: {"material": v} for k, v in materials.items()}
        self.hands = {"seconds": (seconds, "hand")}


def _run(module, height):
    return {"module": module, "smallest_drive_height": height, "smallest_drive_overlap": 1.0, "smallest_drive_ratio": 10.0,
            "worst_volume": 0.0, "largest_gap": 0.0, "teeth_match": True}      # a mesh that passes the mesh test


def case_arithmetic():
    # barrel (96, 1/8 turn per hour) drives a 24-tooth pinion on mobile "a" (steel); a's 60-tooth wheel drives a
    # 30-tooth pinion on mobile "b" (brass), which carries the seconds hand. Speeds: a = 1/8 x 96/24 = 1/2,
    # b = 1/2 x 60/30 = 1 turn per hour. Mobile "c" (brass), driven by b's 12-tooth pinion with 36 teeth, is off the
    # going train (motion work): not rated, though its brass gears would fail.
    m = _Fake([("barrel", 96, "a", 24), ("a", 60, "b", 30), ("b", 12, "c", 36)],
              {"a": "AD-C100-HT", "b": "AD-CW614N", "c": "AD-CW614N"}, "b")
    driven = {"barrel": Fraction(1, 8), "a": Fraction(-1, 2), "b": Fraction(1), "c": Fraction(-1, 3)}
    runs = [_run(0.2, 0.8), _run(0.25, 0.45), _run(0.1, 0.2)]
    ok, d = W.strength_run(m, runs, driven)
    assert d["going_train"] == ["barrel/a", "a/b"], d["going_train"]
    Y24, Y30, Y60 = W.LEWIS_Y[24], W.LEWIS_Y[30], W.LEWIS_Y[60]
    # mesh 1: T = 70.1 x (1/8)/(1/8) = 70.1 N·mm at the barrel; F = 70.1 / (0.2 x 96 / 2) = 70.1 / 9.6 = 7.302083 N;
    #         pinion 24: sigma = F / (0.8 x 0.2 x Y24); the barrel's own teeth are not rated
    # mesh 2: T = 70.1 x (1/8)/(1/2) = 17.525 N·mm at a; F = 17.525 / (0.25 x 60 / 2) = 17.525 / 7.5 = 2.336667 N;
    #         wheel 60 (steel): F / (0.45 x 0.25 x Y60); pinion 30 (brass): F / (0.45 x 0.25 x Y30)
    # both loads times the load factor for dry meshing, W.TOOTH_LOAD_FACTOR (DS-W04 section 2)
    F1, F2 = W.TOOTH_LOAD_FACTOR * 70.1 / 9.6, W.TOOTH_LOAD_FACTOR * 17.525 / 7.5
    want = {("barrel/a", "a"): F1 / (0.8 * 0.2 * Y24), ("a/b", "a"): F2 / (0.45 * 0.25 * Y60),
            ("a/b", "b"): F2 / (0.45 * 0.25 * Y30)}
    got = {(e["pair"], g): v["sigma_mpa"] for e in d["meshes"] for g, v in e["gears"].items() if "sigma_mpa" in v}
    assert set(got) == set(want), got
    for k in want:
        assert abs(got[k] - want[k]) < 1e-6, (k, got[k], want[k])
    assert abs(d["meshes"][0]["torque_nmm"] - 70.1) < 1e-12 and abs(d["meshes"][1]["torque_nmm"] - 17.525) < 1e-9
    assert d["meshes"][0]["gears"]["barrel"] == {"teeth": 96, "rated": False}
    assert ok == all(want[k] <= W.MATERIAL_ALLOWABLE_MPA[m.mobiles[k[1]]["material"]] for k in want)
    # a mesh of the train that fails its drive test: the seconds hand's mobile is not reached, the check fails
    bad = dict(runs[1], smallest_drive_overlap=0.0)
    ok2, d2 = W.strength_run(m, [runs[0], bad, runs[2]], driven)
    assert not ok2 and "seconds hand" in d2["error"], d2
    # the seconds hand on c: the motion-work mesh b/c is now on the path and rated (brass pinion 12 at m 0.1 fails)
    m.hands["seconds"] = ("c", "hand")
    ok3, d3 = W.strength_run(m, runs, driven)
    assert d3["going_train"] == ["barrel/a", "a/b", "b/c"] and not ok3
    # a brass third pinion on the barrel mesh fails where steel passes
    m.hands["seconds"] = ("b", "hand")
    m.mobiles["a"]["material"] = "AD-CW614N"
    ok4, d4 = W.strength_run(m, runs, driven)
    assert ok and not ok4 and d4["meshes"][0]["gears"]["a"]["margin"] < 0
    return "sigma: pinion 24 %.6f, wheel 60 %.6f, pinion 30 %.6f MPa (F1 %.6f N, F2 %.6f N); passed %s; " \
           "pinion 24 in brass: margin %.4f, fails" % (want[("barrel/a", "a")], want[("a/b", "a")], want[("a/b", "b")],
                                                      F1, F2, ok, d4["meshes"][0]["gears"]["a"]["margin"])


def _doc(material):
    mob = {"axis": [5.0, 0.0], "parts": ["p"]}
    if material is not None:
        mob["material"] = material
    return {"barrel": W.DEFAULT_BARREL, "case_centre": [0, 0], "fixed": ["plate"], "mobiles": {"p": mob},
            "meshes": [{"driver": "barrel", "driver_teeth": 96, "driven": "p", "driven_teeth": 12}],
            "hands": {h: {"mobile": "p", "part": "p"} for h in ("hour", "minute", "seconds")}}


def case_material():
    solids = {"p": core.box((4, -1, 0), (6, 1, 1)), "plate": core.box((-12, -12, -3.0), (16, 12, -2.5))}
    load = lambda n: solids[n]
    out = []
    for mat in (None, "AD-AL2O3", "AD-C100S", "AD-CoNiCr-45", "steel", 7):
        try:
            W.Movement(_doc(mat), load, materials=True)
            raise AssertionError("material %r accepted" % (mat,))
        except FormatError as e:
            out.append("%r: %s" % (mat, e))
        W.Movement(_doc(mat), load)                     # stage mode: not read
    for mat in W.MATERIAL_ALLOWABLE_MPA:
        assert W.Movement(_doc(mat), load, materials=True).mobiles["p"]["material"] == mat
    # through the grader: the one-job loader's format gate (C1, "files") fails
    import grade_watch as G
    from geometry import watch_gears_cad as GC
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "parts"))
        GC.export(os.path.join(tmp, "parts", "plate.step"), GC.box((-12, -12, -3.0), (16, 12, -2.5)))
        GC.export(os.path.join(tmp, "parts", "p.step"), GC.box((4, -1, 0), (6, 1, 1)))
        with open(os.path.join(tmp, "movement.json"), "w") as f:
            json.dump(_doc(None), f)
        m, gates, checks, details = G._job_movement(tmp, "movement.json", W.BARREL_TURNS_PER_HOUR, {"strength": 2}, {},
                                                    G._run, {}, {})
        assert m is None and gates["files"] is False and "material" in details["files"]["error"], details
        out.append("grader C1: %s" % details["files"]["error"])
    finally:
        shutil.rmtree(tmp)
    return "\n    ".join(out)


def case_barrel():
    import test_tolerant as TT
    tmp = tempfile.mkdtemp()
    try:
        cd = W.BARREL_MODULE * (W.BARREL_TEETH + 12) / 2.0
        from geometry import watch_gears_cad as GC
        from test_cad_gears import phase_for
        pin = GC.gear(12, W.BARREL_MODULE, 0.1, 0.9, phase_deg=phase_for(12, W.BARREL_TEETH, 0.0, 180.0), x=cd, y=0.0)
        path = os.path.join(tmp, "pinion.step")
        GC.export(path, pin)
        solids = {"pinion": W.load_part_file(path), "plate": core.box((-12, -12, -3.0), (16, 12, -2.5))}
        res = {}
        x = None
        for mat in ("AD-C100-HT", "AD-CW614N"):
            doc = {"barrel": W.DEFAULT_BARREL, "case_centre": [0, 0], "fixed": ["plate"],
                   "mobiles": {"p": {"axis": [cd, 0.0], "parts": ["pinion"], "material": mat}},
                   "meshes": [{"driver": "barrel", "driver_teeth": W.BARREL_TEETH, "driven": "p", "driven_teeth": 12}],
                   "hands": {h: {"mobile": "p", "part": "pinion"} for h in ("hour", "minute", "seconds")}}
            m = W.Movement(doc, lambda n: solids[n], materials=True)
            if x is None:
                x = m.mesh_run("barrel", W.BARREL_TEETH, "p", 12)
                assert TT.passes(x), x
            driven, _ = m.speeds()
            res[mat] = W.strength_run(m, [x], driven)
        g = res["AD-C100-HT"][1]["meshes"][0]
        assert res["AD-C100-HT"][0] and not res["AD-CW614N"][0], res
        # F = K x 70.1 / (0.2 x 96 / 2) = K x 7.302083 N; b = the drive test's height (the pinion is 0.8 thick)
        assert abs(g["force_n"] - W.TOOTH_LOAD_FACTOR * 70.1 / 9.6) < 1e-9 and abs(g["module"] - 0.2) < 1e-9
        assert abs(g["nominal_force_n"] - 70.1 / 9.6) < 1e-9 and g["load_factor"] == W.TOOTH_LOAD_FACTOR
        assert 0.75 <= g["face_width"] <= 0.8 + 1e-6, g
        s = g["gears"]["p"]
        return "b %.4f mm, Y(12) %.4f, sigma %.2f MPa: steel allowable 725 margin %.3f passes, brass allowable 110 margin %.3f fails" % (
            g["face_width"], s["Y"], s["sigma_mpa"], s["margin"], res["AD-CW614N"][1]["meshes"][0]["gears"]["p"]["margin"])
    finally:
        shutil.rmtree(tmp)


def _doc2(part_materials, material="AD-CW614N"):
    """One mobile p of two parts (pin, wheel), its material and part_materials as given (None: no field)."""
    mob = {"axis": [5.0, 0.0], "parts": ["pin", "wheel"], "material": material}
    if part_materials is not None:
        mob["part_materials"] = part_materials
    return {"barrel": W.DEFAULT_BARREL, "case_centre": [0, 0], "fixed": ["plate"], "mobiles": {"p": mob},
            "meshes": [{"driver": "barrel", "driver_teeth": 96, "driven": "p", "driven_teeth": 12}],
            "hands": {h: {"mobile": "p", "part": "wheel"} for h in ("hour", "minute", "seconds")}}


def case_part_materials():
    solids = {"pin": core.box((4, -1, 0), (6, 1, 1)), "wheel": core.box((4, -1, 1), (6, 1, 1.5)),
              "plate": core.box((-12, -12, -3.0), (16, 12, -2.5))}
    load = lambda n: solids[n]
    out = []
    bad = ({"pin": "AD-AL2O3"}, {"pin": "AD-C100S"}, {"wheel": "brass"}, {"pin": 7}, {"plate": "AD-C100-HT"},
           {"barrel": "AD-C100-HT"}, {"nope": "AD-C100-HT"}, ["pin", "AD-C100-HT"], "AD-C100-HT")
    for pm in bad:
        try:
            W.Movement(_doc2(pm), load, materials=True)
            raise AssertionError("part_materials %r accepted" % (pm,))
        except FormatError as e:
            out.append("%r: %s" % (pm, e))
        W.Movement(_doc2(pm), load)                     # stage mode: not read
    # the material is still required with part_materials
    try:
        W.Movement(_doc2({"pin": "AD-C100-HT", "wheel": "AD-CW614N"}, material=None), load, materials=True)
        raise AssertionError("part_materials without material accepted")
    except FormatError as e:
        out.append("no material: %s" % e)
    for pm, want in ((None, {"pin": "AD-CW614N", "wheel": "AD-CW614N"}), ({}, {"pin": "AD-CW614N", "wheel": "AD-CW614N"}),
                     ({"pin": "AD-C100-HT"}, {"pin": "AD-C100-HT", "wheel": "AD-CW614N"}),
                     ({"pin": "AD-C100-HT", "wheel": "AD-C100-HT"}, {"pin": "AD-C100-HT", "wheel": "AD-C100-HT"})):
        got = W.Movement(_doc2(pm), load, materials=True).mobiles["p"]["part_materials"]
        assert got == want, (pm, got)
    # through the grader: the one-job loader's format gate (C1, "files") fails
    import grade_watch as G
    from geometry import watch_gears_cad as GC
    tmp = tempfile.mkdtemp()
    try:
        os.makedirs(os.path.join(tmp, "parts"))
        GC.export(os.path.join(tmp, "parts", "plate.step"), GC.box((-12, -12, -3.0), (16, 12, -2.5)))
        GC.export(os.path.join(tmp, "parts", "pin.step"), GC.box((4, -1, 0), (6, 1, 1)))
        GC.export(os.path.join(tmp, "parts", "wheel.step"), GC.box((4, -1, 1), (6, 1, 1.5)))
        for pm in ({"wheel": "AD-AL2O3"}, {"third": "AD-C100-HT"}):
            with open(os.path.join(tmp, "movement.json"), "w") as f:
                json.dump(_doc2(pm), f)
            m, gates, checks, details = G._job_movement(tmp, "movement.json", W.BARREL_TURNS_PER_HOUR, {"strength": 2},
                                                        {}, G._run, {}, {})
            assert m is None and gates["files"] is False and "part_materials" in details["files"]["error"], details
            out.append("grader C1: %s" % details["files"]["error"])
    finally:
        shutil.rmtree(tmp)
    return "\n    ".join(out)


def case_per_part():
    """The barrel (96, module 0.2) drives the steel pinion part "pin" (12 teeth, z 0.1 to 0.9, with its arbor) of
    mobile p; p's brass wheel part "wheel" (36 teeth, module 0.2, z 1.5 to 2.0, bored for the arbor) drives a
    12-tooth one-part steel pinion q (z 1.5 to 2.0), which carries the seconds hand. p's material is brass and
    part_materials makes "pin" steel."""
    import test_tolerant as TT
    from geometry import watch_gears_cad as GC
    from test_cad_gears import phase_for
    tmp = tempfile.mkdtemp()
    try:
        mod = W.BARREL_MODULE
        cd = mod * (W.BARREL_TEETH + 12) / 2.0                  # 10.8
        cq_ = mod * (36 + 12) / 2.0                             # 4.8
        px, qx = cd, cd + cq_
        pin = GC.union([GC.gear(12, mod, 0.1, 0.9, phase_deg=phase_for(12, W.BARREL_TEETH, 0.0, 180.0), x=px, y=0.0),
                        GC.cyl(px, 0.0, 0.1, 2.0, 0.4)])
        wheel = GC.cut(GC.gear(36, mod, 1.5, 2.0, phase_deg=0.0, x=px, y=0.0), GC.cyl(px, 0.0, 1.0, 2.5, 0.4))
        qpin = GC.gear(12, mod, 1.5, 2.0, phase_deg=phase_for(12, 36, 0.0, 180.0), x=qx, y=0.0)
        solids = {}
        for n, sol in (("pin", pin), ("wheel", wheel), ("q", qpin)):
            path = os.path.join(tmp, n + ".step")
            GC.export(path, sol)
            solids[n] = W.load_part_file(path)
        solids["plate"] = core.box((-12, -12, -3.0), (22, 12, -2.5))

        def movement(pm, material="AD-CW614N"):
            mob = {"axis": [px, 0.0], "parts": ["pin", "wheel"], "material": material}
            if pm is not None:
                mob["part_materials"] = pm
            doc = {"barrel": W.DEFAULT_BARREL, "case_centre": [0, 0], "fixed": ["plate"],
                   "mobiles": {"p": mob, "q": {"axis": [qx, 0.0], "parts": ["q"], "material": "AD-C100-HT"}},
                   "meshes": [{"driver": "barrel", "driver_teeth": W.BARREL_TEETH, "driven": "p", "driven_teeth": 12},
                              {"driver": "p", "driver_teeth": 36, "driven": "q", "driven_teeth": 12}],
                   "hands": {h: {"mobile": "q", "part": "q"} for h in ("hour", "minute", "seconds")}}
            return W.Movement(doc, lambda n: solids[n], materials=True)
        m = movement({"pin": "AD-C100-HT"})
        runs = [m.mesh_run(a, ta, b, tb) for a, ta, b, tb in m.meshes]
        assert all(TT.passes(x) for x in runs), runs
        driven, _ = m.speeds()
        ok, d = W.strength_run(m, runs, driven)
        assert d["going_train"] == ["barrel/p", "p/q"], d
        g1, g2 = d["meshes"][0]["gears"]["p"], d["meshes"][1]["gears"]["p"]
        # which part holds the teeth: all of the barrel mesh's drive overlap is in the pinion, all of the q mesh's
        # in the wheel
        assert g1["part"] == "pin" and g1["material"] == "AD-C100-HT" and g1["allowable_mpa"] == 725.0, g1
        assert g1["drive_overlap_by_part"]["pin"] > 0 and g1["drive_overlap_by_part"]["wheel"] == 0.0, g1
        assert g2["part"] == "wheel" and g2["material"] == "AD-CW614N" and g2["allowable_mpa"] == 110.0, g2
        assert g2["drive_overlap_by_part"]["wheel"] > 0 and g2["drive_overlap_by_part"]["pin"] == 0.0, g2
        gq = d["meshes"][1]["gears"]["q"]
        assert gq["part"] == "q" and gq["material"] == "AD-C100-HT" and "drive_overlap_by_part" not in gq, gq
        # sigma by hand: mesh 1, T = 70.1 at the barrel, F = 70.1 / (0.2 x 96 / 2); mesh 2, p turns 96/12 x 1/8 = 1
        # per hour, T = 70.1 x (1/8) / 1 = 8.7625 N·mm at p, F = 8.7625 / (0.2 x 36 / 2) = 2.434028 N
        F1, F2 = W.TOOTH_LOAD_FACTOR * 70.1 / 9.6, W.TOOTH_LOAD_FACTOR * 8.7625 / 3.6   # x the dry load factor
        b1, b2 = d["meshes"][0]["face_width"], d["meshes"][1]["face_width"]
        assert 0.75 <= b1 <= 0.8 + 1e-6 and 0.45 <= b2 <= 0.5 + 1e-6, (b1, b2)
        want = {"pin": F1 / (b1 * mod * W.LEWIS_Y[12]), "wheel": F2 / (b2 * mod * W.LEWIS_Y[36]),
                "q": F2 / (b2 * mod * W.LEWIS_Y[12])}
        for got, k in ((g1, "pin"), (g2, "wheel"), (gq, "q")):
            assert abs(got["sigma_mpa"] - want[k]) < 1e-6 * want[k], (k, got, want[k])
        assert abs(d["meshes"][1]["torque_nmm"] - 8.7625) < 1e-9 and abs(d["meshes"][1]["force_n"] - F2) < 1e-9
        assert ok and g1["margin"] > 0 and g2["margin"] > 0, d
        # the same mobile all in brass (no part_materials): the pinion is rated in brass and fails
        m2 = movement(None)
        ok2, d2 = W.strength_run(m2, runs, driven)
        h1 = d2["meshes"][0]["gears"]["p"]
        assert not ok2 and h1["part"] == "pin" and h1["material"] == "AD-CW614N" and h1["margin"] < 0, d2
        # steel by default with a brass wheel part: the same ratings as the first case
        m3 = movement({"wheel": "AD-CW614N"}, material="AD-C100-HT")
        ok3, d3 = W.strength_run(m3, runs, driven)
        assert ok3 and [(e["gears"]["p"]["part"], e["gears"]["p"]["material"]) for e in d3["meshes"]] == \
            [("pin", "AD-C100-HT"), ("wheel", "AD-CW614N")], d3
        return ("barrel/p: part pin (overlap by part %s) steel, b %.4f, sigma %.2f MPa, margin %.3f; p/q: part wheel "
                "(overlap by part %s) brass, b %.4f, sigma %.2f MPa, margin %.3f; q pinion steel sigma %.2f; all brass: "
                "pin margin %.3f, fails" % (
                    {k: round(v, 5) for k, v in g1["drive_overlap_by_part"].items()}, b1, g1["sigma_mpa"], g1["margin"],
                    {k: round(v, 5) for k, v in g2["drive_overlap_by_part"].items()}, b2, g2["sigma_mpa"], g2["margin"],
                    gq["sigma_mpa"], h1["margin"]))
    finally:
        shutil.rmtree(tmp)


def case_weights():
    import grade_watch as G
    w = {p[0]: p[4] for p in G.JOB_PARTS}
    assert sum(w["P1"].values()) == 23 and w["P1"]["strength"] == 2
    assert sum(w["P3"].values()) == 27 and w["P3"]["strength"] == 2
    assert "strength" not in G.stage_weights(1) and "strength" not in G.stage_weights(3)
    return "P1 %d, P3 %d; stage weights unchanged" % (sum(w["P1"].values()), sum(w["P3"].values()))


def main(argv):
    if "--write-lewis" in argv:
        doc = W.lewis_table_doc()
        with open(LEWIS_FILE, "w") as f:
            json.dump(doc, f, indent=0, sort_keys=False)
            f.write("\n")
        print("wrote", LEWIS_FILE, len(doc["Y"]), "tooth counts")
        return 0
    fails = 0
    for name, fn in (("sheets", case_sheets), ("lewis", case_lewis), ("arithmetic", case_arithmetic),
                     ("material", case_material), ("part_materials", case_part_materials), ("weights", case_weights),
                     ("barrel", case_barrel), ("per_part", case_per_part)):
        try:
            print("PASS %-10s %s" % (name, fn()))
        except Exception as e:      # noqa
            fails += 1
            print("FAIL %-10s %s: %s" % (name, type(e).__name__, e))
    print("all passed" if not fails else "%d failed" % fails)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
