"""NOT-FOR-AGENT (realcad test material; never copy into a task image; tests/realcad is in build_task's NEVER_DIRS
and has a .harborignore of '*').

Fairness test: Marco Lang's ml01 going train through the one-job grader's Part 1 (REAL_WATCH_WORK.md section 9).
ml01 has NO LICENCE: this script downloads and converts it at run time into a scratch folder. Never commit the STEP,
the extracted solids, the converted parts or anything derived from them.

    python3 -I ml01_train.py fetch WORK                 download into WORK/dl, check sha256, extract to WORK/ext
    python3 -I ml01_train.py build WORK [--phases F]    write WORK/delivery (movement.json, parts/*.step) and
                                                        WORK/barrel_ml01.step; F: phases JSON {mobile: degrees}
    python3 -I ml01_train.py probe WORK                 fast measurements with the grader's engine (no mesh runs)
    python3 -I ml01_train.py phase WORK OUT.json        find the phase of every driven mobile (rest overlap)

Sequence used for REAL_ML01_FAIRNESS.md: fetch; build; phase WORK phases1.json; build --phases phases1.json;
fairness_ml01.py WORK (run 1); then phases2.json = phases1 with the centre turned +4.0 degrees and the mobiles it
drives turned with it (run 2); build --phases phases2.json; fairness_ml01.py WORK (run 2).

Frame: CAD point p -> 1.2 p + SHIFT. The movement centre (CAD origin) goes to case_centre; barrel II's axis
(CAD -6.2, 8.1) goes to (0, 0), because the engine puts the barrel mobile on (0, 0). +z is the dial side in the
CAD and in the grader. The wrapper fairness_ml01.py supplies barrel II as the barrel and its speed (3/20 turn per
hour, clockwise).
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

URL = "https://www.marcolangwatches.com/cad/001-ml01-werk-montiert-einbaufertig/?wpdmdl=1998&ind=1690622339023"
SHA256 = "34f001d6f98eeab4b9aacea1f0a47e145666c00a3549364959dbdf33d1f75991"
SCALE = 1.2
BARREL_CAD = (-6.2, 8.1)                    # barrel II axis (circle centres of drum, cover and arbor)
SHIFT = (-SCALE * BARREL_CAD[0], -SCALE * BARREL_CAD[1], 0.0)
CASE_CENTRE = (SHIFT[0], SHIFT[1])          # the CAD movement centre (plate centre)

# CAD solid ids from extract_step.py on the file with SHA256 above. Each part is the fusion of its ids
# (a CAD sub-assembly that is pressed, pinned or riveted together; see FUSED_WHY).
FIXED = {
    "plate": [139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 156],   # Werkplatte verstiftet versteint
    "train_bridge": [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],             # Raederbruecke montiert + cap plate
    "barrel_bridge": [180, 181, 182, 183, 184, 185, 186],                         # Federhausbruecke verstiftet
    "minute_bridge": [187, 188, 189, 190],                                        # Min_Bruecke versteint verstiftet
    "pallet_bridge": [52, 53, 54, 55],                                            # Ankerbruecke verstiftet versteint
    "cap_plate": [38, 39],                                                        # Deckplaettchen WPL versteint
    "barrel_one": [4, 5, 6],              # barrel I: drum, cover, arbor (its mainspring is left out)
    "arbor_two": [2],                     # barrel II's arbor: held while the train runs
    "ratchet_one": [50], "ratchet_two": [51],     # series ratchets z62 (barrel I to barrel II)
    "dial_washer": [40],                  # 'Flitter 200x400', over the hour wheel; the dial holds it down
    "dial": "dial",                       # NOT in the CAD: a minimal dial on three feet (DIAL below)
    "scr_minute_a": [41], "scr_minute_b": [119],  # minute-bridge screws
    "scr_barrel_a": [56], "scr_barrel_b": [58], "scr_barrel_c": [60],             # barrel-bridge screws
    "scr_train_a": [57], "scr_train_b": [61],     # train-bridge screws
    "scr_mw_post": [42],                  # minute wheel's post screw
    "scr_ratchet_one": [135], "scr_ratchet_two": [134],   # ratchet screws: into arbor I (+6.2) and arbor II (-6.2)
    "scr_pallet_a": [117], "scr_pallet_b": [118],
    "scr_cap_a": [209], "scr_cap_b": [210],
}
# mobile: (CAD axis, {part: CAD ids, or the name of a hand built here}); every mobile is declared AD-C100-HT (steel)
MOBILES = {
    "intermediate": ((-2.6791, 0.9722), {"inter_wheel": [11, 64]}),     # wheel + the screw threaded into its arbor
    "centre": ((0.0, 0.0), {"centre_pinion": [8], "centre_wheel": [9], "seconds_bush": [10], "cannon": [59],
                            "minute_hand": "minute"}),
    "third": ((3.1705, -3.6172), {"third_pinion": [194], "third_wheel": [195]}),
    "seconds": ((0.0, 0.0), {"seconds_pinion": [199], "seconds_wheel": [200], "seconds_hand": "seconds"}),
    "minute_wheel": ((4.2429, 0.246), {"mw_wheel": [157], "mw_pinion": [158]}),
    "hour_wheel": ((0.0, 0.0), {"hw_wheel": [65], "hw_pipe": [66], "hour_hand": "hour"}),
}
BARREL_IDS = [0, 1]                     # Federhaustrommel II z80 + Federhausdeckel II
MESHES = [  # driver, driver teeth, driven, driven teeth (tooth counts from the CAD names, counted by the research)
    ("barrel", 80, "intermediate", 26),
    ("intermediate", 26, "centre", 12),
    ("centre", 64, "third", 10),
    ("third", 75, "seconds", 8),
    ("centre", 12, "minute_wheel", 36),
    ("minute_wheel", 10, "hour_wheel", 40),
]
HANDS = {"hour": ("hour_wheel", "hour_hand"), "minute": ("centre", "minute_hand"), "seconds": ("seconds", "seconds_hand")}
STEEL, BRASS = "AD-C100-HT", "AD-CW614N"
# The hands (CAD units, before x1.2): collet tube (inner r, outer r, z0, z1) on the pipe or arbor that carries it,
# and a blade (z0, z1, inner r of its hub disc, hub r, reach, width) above it. ml01's CAD has no hands.
HAND_GEOM = {
    "hour": {"collet": (0.75, 0.95, 0.95, 1.25), "blade": (1.25, 1.50, 0.60, 0.95, 5.5, 0.4)},     # on the hour pipe (r 0.75, top 1.25)
    "minute": {"collet": (0.40, 0.60, 1.55, 1.83), "blade": (1.83, 2.08, 0.20, 0.60, 7.5, 0.4)},   # on the cannon (r 0.40, top 1.83)
    "seconds": {"collet": (0.116, 0.45, 2.13, 2.41), "blade": (2.41, 2.66, 0.0, 0.45, 8.0, 0.3)},  # on the seconds arbor (r 0.116, top 2.41)
}
# Adjustments to the CAD, each logged as a finding (REAL_ML01_FAIRNESS.md). Filled in as the probe shows the need.
# Screw threads are drawn at the major diameter in a tapped hole drawn at the minor diameter (0.02 to 0.32 mm3 of
# overlap at x1.2). Each screw is trimmed by the parts it is screwed into: the thread is then at the minor diameter.
CUTS = {"scr_barrel_a": ["plate"], "scr_barrel_b": ["plate"], "scr_barrel_c": ["plate"], "scr_train_a": ["plate"],
        "scr_train_b": ["plate"], "scr_minute_a": ["plate"], "scr_minute_b": ["plate"],
        "scr_pallet_a": ["plate", "pallet_bridge"], "scr_pallet_b": ["plate", "pallet_bridge"],
        "scr_cap_a": ["plate"], "scr_cap_b": ["plate"], "scr_ratchet_one": ["barrel_one"], "scr_ratchet_two": ["arbor_two"]}
# The two series ratchets are drawn tooth through tooth (0.105 mm3 at x1.2, both fixed parts). Barrel II's arbor,
# its ratchet and its screw are turned together about barrel II's axis into the middle of the clear range
# (clear from 13/48 to 17/48 of a ratchet tooth: 15/48 x 360/62 degrees).
FIXED_ROT = {"arbor_two": 15 / 48 * 360 / 62, "ratchet_two": 15 / 48 * 360 / 62, "scr_ratchet_two": 15 / 48 * 360 / 62}
# ml01's CAD has no dial. In the watch the dial presses the washer ('Flitter') onto the hour wheel. A minimal flat
# dial (CAD units): disc z 0.204 (the washer's top) to 0.45, outer r 14.0, centre hole r 0.95 (the hour wheel's pipe
# is r 0.90 below z 0.425), on three feet r 0.25 standing on the plate's dial face (z 0) where it is solid.
DIAL = {"z": (0.204, 0.45), "r": 14.0, "hole": 0.95, "feet_r": 0.25,
        "feet": [(12.083, 90.0), (12.083, 195.0), (13.333, 300.0)]}     # (radius, degrees) about the movement centre
BORES = {}         # part -> (CAD axis x, y, bore radius, radial clearance added to it, z0, z1)
# The main plate with its pressed jewels, pins and screws is one CAD sub-assembly, but tessellated as the grader does
# (0.001 mm, 0.1 rad) it has 391,259 triangles, over the 200,000 limit of a part file (the bare plate alone has
# 163,505). It is cut into pieces by planes x = const (CAD frame); the pieces touch along the cuts and their union is
# the sub-assembly unchanged.
# Pieces as boxes (x0, x1, y0, y1); the planes are placed clear of every fitting (a plane at x = -4.5 gave a solid
# that fails BRepCheck, so -4.6 is used).
SPLIT = {"plate": [(-100, -8.5, -100, 100), (-8.5, -4.6, -100, 100), (-4.6, 1.8, -2.5, 100), (-4.6, 1.8, -100, -2.5),
                   (1.8, 4.5, -100, 100), (4.5, 100, -100, 100)]}


# ---------------- OCP helpers ----------------
def _occ():
    from OCP.BRepTools import BRepTools
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Shape
    return BRepTools, BRep_Builder, TopoDS_Shape


def read_brep(ext, rows, i):
    BRepTools, BRep_Builder, TopoDS_Shape = _occ()
    s = TopoDS_Shape()
    BRepTools.Read_s(s, os.path.join(ext, "brep", rows[i]["file"] + ".brep"), BRep_Builder())
    return s


def solids_of(shape):
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopAbs import TopAbs_SOLID
    from OCP.TopoDS import TopoDS
    out, ex = [], TopExp_Explorer(shape, TopAbs_SOLID)
    while ex.More():
        out.append(TopoDS.Solid_s(ex.Current()))
        ex.Next()
    return out


def boolean(kind, a, others, fuzzy=1e-5):
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
    from OCP.TopTools import TopTools_ListOfShape
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    if not others:
        return a
    op = {"fuse": BRepAlgoAPI_Fuse, "cut": BRepAlgoAPI_Cut, "common": BRepAlgoAPI_Common}[kind]()
    la, lt = TopTools_ListOfShape(), TopTools_ListOfShape()
    la.Append(a)
    for o in others:
        lt.Append(o)
    op.SetArguments(la)
    op.SetTools(lt)
    op.SetFuzzyValue(fuzzy)
    op.SetRunParallel(False)
    op.Build()
    if not op.IsDone():
        raise RuntimeError("%s failed" % kind)
    u = ShapeUpgrade_UnifySameDomain(op.Shape(), True, True, False)
    u.Build()
    return u.Shape()


def transform(shape, rot_deg=0.0, axis=(0.0, 0.0)):
    """Turn rot_deg (counter-clockwise from +z) about the CAD axis, then scale x1.2 about the CAD origin and shift."""
    from OCP.gp import gp_Trsf, gp_Ax1, gp_Pnt, gp_Dir, gp_Vec
    from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
    if rot_deg:
        r = gp_Trsf()
        r.SetRotation(gp_Ax1(gp_Pnt(axis[0], axis[1], 0), gp_Dir(0, 0, 1)), math.radians(rot_deg))
        shape = BRepBuilderAPI_Transform(shape, r, True).Shape()
    s = gp_Trsf()
    s.SetScale(gp_Pnt(0, 0, 0), SCALE)
    shape = BRepBuilderAPI_Transform(shape, s, True).Shape()
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(*SHIFT))
    return BRepBuilderAPI_Transform(shape, t, True).Shape()


def cylinder(x, y, z0, z1, r):
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
    from OCP.gp import gp_Ax2, gp_Pnt, gp_Dir
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(x, y, z0), gp_Dir(0, 0, 1)), r, z1 - z0).Shape()


def box(x0, y0, z0, x1, y1, z1):
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.gp import gp_Pnt
    return BRepPrimAPI_MakeBox(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Shape()


def hand_shape(kind, axis):
    """A simple hand (CAD frame, on axis): a collet tube on its pipe plus a blade with a hub disc."""
    ci, co, cz0, cz1 = HAND_GEOM[kind]["collet"]
    bz0, bz1, hi, ho, reach, w = HAND_GEOM[kind]["blade"]
    x, y = axis
    collet = boolean("cut", cylinder(x, y, cz0, cz1, co), [cylinder(x, y, cz0 - 0.1, cz1 + 0.1, ci)])
    hub = cylinder(x, y, bz0, bz1, ho)
    blade = box(x + 0.5 * ho, y - w / 2, bz0, x + reach, y + w / 2, bz1)
    top = boolean("fuse", hub, [blade])
    if hi > 0:
        top = boolean("cut", top, [cylinder(x, y, bz0 - 0.1, bz1 + 0.1, hi)])
    return boolean("fuse", collet, [top])


def _vol(s):
    from OCP.GProp import GProp_GProps
    from OCP.BRepGProp import BRepGProp
    g = GProp_GProps()
    BRepGProp.VolumeProperties_s(s, g)
    return g.Mass()


VOIDS_FILLED = {}   # part -> volumes of the closed internal cavities removed (a fusion can enclose a cavity: the
                   # space under a screw's tip in a blind tapped hole; the grader's loader takes one shell only)


def dial_shape():
    z0, z1 = DIAL["z"]
    d = boolean("cut", cylinder(0, 0, z0, z1, DIAL["r"]), [cylinder(0, 0, z0 - 0.1, z1 + 0.1, DIAL["hole"])])
    feet = [cylinder(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), 0.0, z0, DIAL["feet_r"]) for r, a in DIAL["feet"]]
    return boolean("fuse", d, feet)


def one_solid(shape, what):
    from OCP.BRepCheck import BRepCheck_Analyzer
    from OCP.BRepClass3d import BRepClass3d
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    ss = solids_of(shape)
    if len(ss) != 1:
        raise RuntimeError("%s: %d solids after the boolean" % (what, len(ss)))
    ex, n_sh = TopExp_Explorer(ss[0], TopAbs_SHELL), 0
    while ex.More():
        n_sh += 1
        ex.Next()
    if n_sh > 1:
        before = _vol(ss[0])
        filled = BRepBuilderAPI_MakeSolid(BRepClass3d.OuterShell_s(ss[0])).Solid()
        VOIDS_FILLED[what] = round(_vol(filled) - before, 6)
        ss = [filled]
    if not BRepCheck_Analyzer(ss[0]).IsValid():
        from OCP.ShapeFix import ShapeFix_Solid
        f = ShapeFix_Solid(ss[0])
        f.Perform()
        s = solids_of(f.Shape())
        if len(s) != 1 or not BRepCheck_Analyzer(s[0]).IsValid():
            raise RuntimeError("%s: solid not valid (BRepCheck)" % what)
        return s[0]
    return ss[0]


# ---------------- fetch ----------------
def fetch(work):
    import hashlib
    dl = os.path.join(work, "dl")
    os.makedirs(dl, exist_ok=True)
    stp = os.path.join(dl, "ml01_werk.stp")
    if not os.path.isfile(stp):
        subprocess.run(["curl", "-sS", "-L", "--fail", "-o", stp, URL], check=True)
    h = hashlib.sha256(open(stp, "rb").read()).hexdigest()
    if h != SHA256:
        raise SystemExit("sha256 %s, expected %s" % (h, SHA256))
    print("sha256 ok", h)
    ext = os.path.join(work, "ext")
    if not os.path.isfile(os.path.join(ext, "solids.json")):
        subprocess.run([sys.executable, "-I", os.path.join(REPO, "spikes", "keyless", "realcad", "extract_step.py"),
                        stp, ext], check=True)


# ---------------- build ----------------
def build(work, phases=None, cuts=None, bores=None):
    from geometry.core import write_step
    phases = phases or {}
    cuts = CUTS if cuts is None else cuts
    bores = BORES if bores is None else bores
    ext = os.path.join(work, "ext")
    rows = {r["i"]: r for r in json.load(open(os.path.join(ext, "solids.json")))}
    out = os.path.join(work, "delivery")
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    for f in os.listdir(os.path.join(out, "parts")):
        os.remove(os.path.join(out, "parts", f))
    log = {"phases_deg": phases, "cuts": cuts, "bores": bores, "fixed_rot_deg": FIXED_ROT, "dial": DIAL, "split": {},
           "plate_pieces": SPLIT, "parts": {}}

    def cad_part(name, ids, rot=0.0, axis=(0.0, 0.0)):
        shapes = [read_brep(ext, rows, i) for i in ids]
        s = boolean("fuse", shapes[0], shapes[1:]) if len(shapes) > 1 else shapes[0]
        return s

    cad = {}
    for n, ids in FIXED.items():
        if ids == "dial":
            cad[n] = (dial_shape(), 0.0, (0.0, 0.0))
        else:
            cad[n] = (cad_part(n, ids), FIXED_ROT.get(n, 0.0), BARREL_CAD if n in FIXED_ROT else (0.0, 0.0))
    for mn, (axis, parts) in MOBILES.items():
        for pn, src in parts.items():
            s = hand_shape(src, axis) if isinstance(src, str) else cad_part(pn, src)
            cad[pn] = (s, float(phases.get(mn, 0.0)), axis)
    # adjustments in the CAD frame, before the phase turn (cuts use the other parts unturned: only fixed parts)
    for n, others in cuts.items():     # n and the parts it is cut by are turned alike (FIXED_ROT), or neither is
        s, rot, ax = cad[n]
        assert all(cad[o][1] == rot for o in others), n
        cad[n] = (boolean("cut", s, [cad[o][0] for o in others]), rot, ax)
    for n, (bx, by, r0, dr, z0, z1) in bores.items():
        s, rot, ax = cad[n]
        cad[n] = (boolean("cut", s, [cylinder(bx, by, z0, z1, r0 + dr)]), rot, ax)
    for n, xs in SPLIT.items():
        # the bare base solid is cut by the planes; each fitting is fused to the piece its centre lies in (the planes
        # pass clear of every fitting)
        cad.pop(n)
        base, fits = FIXED[n][0], FIXED[n][1:]
        b = read_brep(ext, rows, base)
        for k, (lo, hi, ylo, yhi) in enumerate(xs):
            mine = [i for i in fits if lo < 0.5 * (rows[i]["bbox"][0] + rows[i]["bbox"][3]) < hi
                    and ylo < 0.5 * (rows[i]["bbox"][1] + rows[i]["bbox"][4]) < yhi]
            for i in mine:
                bb = rows[i]["bbox"]
                assert lo < bb[0] and bb[3] < hi and ylo < bb[1] and bb[4] < yhi, ("a cut plane crosses solid", i)
            piece = boolean("common", b, [box(lo, ylo, -100, hi, yhi, 100)])
            cad["%s_%s" % (n, "abcdefgh"[k])] = (boolean("fuse", piece, [read_brep(ext, rows, i) for i in mine]), 0.0, (0.0, 0.0))
    names_of = {}                       # part -> the part names it became (a fusion that left touching pieces apart)
    for n, (s, rot, ax) in cad.items():
        t = transform(s, rot, ax)
        ss = sorted(solids_of(t), key=_vol, reverse=True)
        names_of[n] = [n] + ["%s_%d" % (n, k + 2) for k in range(len(ss) - 1)]
        for nn, solid in zip(names_of[n], ss):
            solid = one_solid(solid, nn)
            write_step(os.path.join(out, "parts", nn + ".step"), solid)
            log["parts"][nn] = {"from": n, "volume": round(_vol(solid), 5)}
        ids = FIXED.get(n.rsplit("_", 1)[0] if n not in FIXED and n.rsplit("_", 1)[0] in SPLIT else n) \
            or next(p[n] for _, p in MOBILES.values() if n in p)
        log["parts"][n]["ids"] = ids
        log["parts"][n]["cad_names"] = [rows[i]["name"] for i in ids] if isinstance(ids, list) else "not in the CAD: " + ids
        if len(ss) > 1:
            log.setdefault("split", {})[n] = names_of[n]
    bar = boolean("fuse", read_brep(ext, rows, BARREL_IDS[0]), [read_brep(ext, rows, i) for i in BARREL_IDS[1:]])
    write_step(os.path.join(work, "barrel_ml01.step"), one_solid(transform(bar, float(phases.get("barrel", 0.0)), BARREL_CAD), "barrel"))
    doc = {
        "case_centre": [round(CASE_CENTRE[0], 6), round(CASE_CENTRE[1], 6)],
        "fixed": [nn for n in FIXED for k in (["%s_%s" % (n, "abcdefgh"[j]) for j in range(len(SPLIT[n]))]
                                                if n in SPLIT else [n]) for nn in names_of[k]],
        "mobiles": {mn: {"axis": [round(SCALE * ax[0] + SHIFT[0], 6), round(SCALE * ax[1] + SHIFT[1], 6)],
                         "parts": [nn for p in parts for nn in names_of[p]], "material": STEEL}
                    for mn, (ax, parts) in MOBILES.items()},
        "meshes": [{"driver": a, "driver_teeth": ta, "driven": b, "driven_teeth": tb} for a, ta, b, tb in MESHES],
        "hands": {h: {"mobile": m, "part": p} for h, (m, p) in HANDS.items()},
    }
    json.dump(doc, open(os.path.join(out, "movement.json"), "w"), indent=1)
    log["voids_filled_mm3"] = VOIDS_FILLED
    json.dump(log, open(os.path.join(work, "build_log.json"), "w"), indent=1)
    print("built", len(cad), "parts into", out)


# ---------------- probe and phase (grader engine, fast parts only) ----------------
def load(work):
    import fairness_ml01 as F
    F.install(work)
    from geometry import watch as W
    return W.load_movement(os.path.join(work, "delivery"), materials=True), W


def probe(work):
    from geometry.core import ivol
    from geometry import watch as W
    m, W = load(work)
    out = {}
    n_tris = {n: s.num_tri() for n, s in m.all_parts().items()}
    out["max_triangles"] = max(n_tris.items(), key=lambda t: t[1])
    names = list(m.mobiles)
    pairs = []
    solids = [("fixed", m.fixed)] + [(n, m.mobiles[n]["solid"]) for n in names]
    for i in range(len(solids)):
        for j in range(i + 1, len(solids)):
            v = ivol(solids[i][1], solids[j][1])
            if v > 1e-5:
                pairs.append((solids[i][0] + "/" + solids[j][0], round(v, 5)))
    out["rest_overlaps_mobiles"] = pairs
    fp = []
    fn = list(m.fixed_parts)
    for i in range(len(fn)):
        for j in range(i + 1, len(fn)):
            v = ivol(m.fixed_parts[fn[i]], m.fixed_parts[fn[j]])
            if v > 1e-4:
                fp.append((fn[i] + "/" + fn[j], round(v, 5)))
    out["fixed_overlaps"] = fp
    mp = []
    for k, mo in m.mobiles.items():
        ps = list(mo["parts"])
        for i in range(len(ps)):
            for j in range(i + 1, len(ps)):
                v = ivol(mo["parts"][ps[i]], mo["parts"][ps[j]])
                if v > 1e-5:
                    mp.append((k + ":" + ps[i] + "/" + ps[j], round(v, 5)))
    out["mobile_part_overlaps"] = mp
    one, groups = m.frame()
    out["frame"] = {"one": one, "groups": groups}
    out["fixed_vs_each_mobile_part"] = []
    for k in names:
        for pn, ps in m.mobiles[k]["parts"].items():
            v = ivol(ps, m.fixed)
            if v > 1e-5:
                out["fixed_vs_each_mobile_part"].append((pn, round(v, 5)))
    if "--spin" in sys.argv:
        out["spin"] = {n: m.spin(n) for n in names}
    if "--held" in sys.argv:
        h = m.held_all()
        out["held"] = {n: {d: (round(x["fixed_volume"], 4), x["held"], x["via"]) for d, x in h[n].items()} for n in names}
    if "--seated" in sys.argv:
        out["seated"] = {n: m.seated(n) for n in names if n != "barrel"}
        out["pieces"] = {n: m.pieces(n) for n in names if n != "barrel"}
    if "--hands" in sys.argv:
        out["hands"] = {h: (m.hand_shape(h), m.hand_reach(h)) for h in ("hour", "minute", "seconds")}
        out["extent"] = m.extent()
    print(json.dumps(out, indent=1, default=str))


def phase(work, dest):
    """For each declared mesh in order (each driven mobile is driven once), the turn of the driven mobile that keeps
    it clear of its driver over one tooth of the driver: overlap sampled at 8 poses over a driver pitch; the phase is
    the middle of the widest run of clear turns (or the turn of least worst overlap if none is clear)."""
    from geometry.core import ivol
    m, W = load(work)
    res, ph = {}, {}
    for a, ta, b, tb in MESHES:
        A, ax_a = m.mobiles[a]["solid"], m.mobiles[a]["axis"]
        B, ax_b = m.mobiles[b]["solid"], m.mobiles[b]["axis"]
        if a in ph:                                       # the driver's own phase (it is turned when rebuilt)
            A = W.rot_about(A, ax_a, ph[a])
        A, B = W._near_cut(A, ax_a, B, ax_b), W._near_cut(B, ax_b, A, ax_a)
        pitch_b = 360.0 / tb
        n_th = 48
        da = 360.0 / ta / 8
        db = -da * ta / tb
        worst = []
        for k in range(n_th):
            th = pitch_b * k / n_th
            w = 0.0
            for i in range(8):
                w = max(w, ivol(W.rot_about(A, ax_a, da * i), W.rot_about(B, ax_b, th + db * i)))
            worst.append(w)
        clear = [w <= 1e-4 for w in worst]
        best, run = None, None
        for start in range(n_th):                          # longest cyclic run of clear turns
            if not clear[start] or clear[start - 1]:
                continue
            L = 0
            while L < n_th and clear[(start + L) % n_th]:
                L += 1
            if run is None or L > run:
                best, run = start, L
        if best is None and all(clear):
            best, run = 0, n_th
        if best is None:
            k = min(range(n_th), key=lambda k: worst[k])
            th = pitch_b * k / n_th
        else:
            th = pitch_b * ((best + (run - 1) / 2.0) % n_th) / n_th
        ph[b] = th
        res["%s/%s" % (a, b)] = {"phase_deg": th, "clear_run_deg": (run or 0) * pitch_b / n_th, "pitch_deg": pitch_b,
                                 "worst_at_0": worst[0], "min_worst": min(worst), "worst_profile": [round(w, 5) for w in worst]}
        print(a, b, json.dumps({k: v for k, v in res["%s/%s" % (a, b)].items() if k != "worst_profile"}), flush=True)
    json.dump({"phases": ph, "detail": res}, open(dest, "w"), indent=1)


if __name__ == "__main__":
    cmd, work = sys.argv[1], os.path.abspath(sys.argv[2])
    sys.path.insert(0, HERE)
    if cmd == "fetch":
        fetch(work)
    elif cmd == "build":
        opts = dict(zip(sys.argv[3:], sys.argv[4:]))
        ph = json.load(open(opts["--phases"]))["phases"] if "--phases" in opts else None
        adj = json.load(open(opts["--adjust"])) if "--adjust" in opts else {}
        build(work, ph, adj.get("cuts"), {k: tuple(v) for k, v in adj.get("bores", {}).items()} if "bores" in adj else None)
    elif cmd == "probe":
        probe(work)
    elif cmd == "phase":
        phase(work, sys.argv[3])
