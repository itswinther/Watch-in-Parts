"""Reference keyless works: stem with a winding pinion, a face (contrate) crown wheel that also
carries a spur pinion, and a ratchet wheel on the supplied arbor square.

    python reference.py OUT_SUBMISSION_DIR

Writes OUT/parts/*.stl and OUT/winding.json. `build(opts)` returns the same with variations,
used by the anchors.
"""
import json
import math
import os
import sys

import manifold3d as m3

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
from geometry import core  # noqa: E402
import constants as C  # noqa: E402
import gears as G  # noqa: E402

DEFAULT = {
    "m_face": 0.15, "zp": 12, "zc": 36,          # stem pinion and face teeth
    "m_spur": 0.2, "zcs": 12, "zr": 36,          # crown's spur pinion and ratchet
    "backlash": 0.004,                            # per flank, along the pitch circle (fraction of the pitch is about 0.025)
    "thin_face": 0.0, "thin_spur": 0.0,           # extra thinning per flank for anchors (face teeth; ratchet only)
    "declare": {},                                # override declared tooth counts (anchor)
    "face_plain": False,                          # a toothless disc instead of the face teeth (anchor)
    "crown_shift": (0.0, 0.0),                    # move the crown wheel off its declared axis (anchor)
    "side": -1,                                   # stem pinion on the -x side of the crown wheel (+1: other side)
    "stem_x_out": -16.0,                          # outer end of the stem
    "spur_z": (-2.45, -1.95),
}


def build(opts=None):
    o = dict(DEFAULT)
    o.update(opts or {})
    parts, fixed = {}, []
    mf, zp, zc = o["m_face"], o["zp"], o["zc"]
    ms, zcs, zr = o["m_spur"], o["zcs"], o["zr"]
    bl = o["backlash"]
    xc = -ms * (zr + zcs) / 2.0                   # crown axis on the stem line, -x of the barrel
    R = mf * zc / 2.0                              # mean face-tooth radius
    r_in, r_out = R - 0.35, R + 0.35
    rp = mf * zp / 2.0
    zs = C.STEM_Z
    z_pitch = zs + rp                              # face gear pitch plane
    z_tip = z_pitch - 1.0 * mf
    z_root = z_pitch + 1.25 * mf
    s0, s1 = o["spur_z"]

    # ratchet on the arbor square (square hole with 0.02 clearance a side)
    sq = C.SQUARE_SIDE / 2 + 0.01
    ratchet = G.spur(zr, ms, s0, s1, thin=bl + o["thin_spur"])
    ratchet = ratchet - core.box([-sq, -sq, s0 - 1], [sq, sq, s1 + 1])
    # phase: ratchet tooth on +x; crown spur placed so a tooth gap faces +x (towards the ratchet)
    parts["ratchet"] = ratchet

    # crown wheel: face teeth ring + web + hub + spur pinion, bore for the post
    if o["face_plain"]:
        ring = core.cyl_z(0, 0, z_tip, z_root, r_out, 192) - core.cyl_z(0, 0, z_tip - 1, z_root + 1, r_in, 192)
        ring = ring.translate([xc, 0, 0])
    else:
        ring = G.face_gear(zc, zp, mf, (xc, 0.0), r_in, r_out, z_root, z_tip, zs,
                           cutter_thin=-(bl), steps_per_pitch=20)
        if o["thin_face"]:
            # thin the face teeth: cut again with a pinion fattened further
            ring2 = G.face_gear(zc, zp, mf, (xc, 0.0), r_in, r_out, z_root, z_tip, zs,
                                cutter_thin=-(bl + o["thin_face"]), steps_per_pitch=20)
            ring = ring2
    web = core.cyl_z(xc, 0, z_root, -2.6, r_out, 192)
    hub = core.cyl_z(xc, 0, -2.6, s0, 0.9)
    spur = G.spur(zcs, ms, s0, s1, thin=bl, phase=math.pi / zcs + math.pi).translate([xc, 0, 0])
    # (phase: rotate so that a gap faces +x; the extra pi turns the tooth-on-+x into tooth-on--x)
    crown = core.union([ring, web, hub, spur]) - core.cyl_z(xc, 0, -5, 0, 0.35)
    dx, dy = o["crown_shift"]
    parts["crown_wheel"] = crown.translate([dx, dy, 0])

    # crown post: from the main plate down through the crown bore, with a head below
    post = core.union([core.cyl_z(xc, 0, -3.3, -1.7, 0.33), core.cyl_z(xc, 0, -3.3, -2.95, 0.6)])
    parts["crown_post"] = post
    fixed.append("crown_post")

    # stem + pinion on the side of the crown wheel facing the case wall
    side = o["side"]
    xp = xc + side * R                              # pinion centre along x
    x_out = o["stem_x_out"]
    pin = G.pinion_along_x(zp, mf, xp - 0.45, xp + 0.45, C.STEM_Y, zs)
    # phase of the stem pinion: the face gear was cut with the pinion at phase 0 on the -x side
    if side > 0:
        # mirror placement: the pinion on +x meets the face teeth at angle 0, where (for zc even)
        # a tooth gap of the face gear also lies; a pinion tooth pointing +z fits it
        pass
    shaft = core.cyl_x(C.STEM_Y, zs, min(x_out, xp), max(x_out, xp), 0.45)
    collars = core.union([core.cyl_x(C.STEM_Y, zs, -12.35, -12.05, 0.8), core.cyl_x(C.STEM_Y, zs, -9.95, -9.65, 0.8)])
    parts["stem"] = core.union([shaft, collars])
    parts["winding_pinion"] = pin
    # stem bearing: block hanging from the main plate with a bore round the stem
    block = core.box([-12.0, -1.0, -4.6], [-10.0, 1.0, -1.7]) - core.cyl_x(C.STEM_Y, zs, -13, -9, 0.47)
    parts["stem_bridge"] = block
    fixed.append("stem_bridge")

    spec = {
        "mobiles": {
            "stem": {"point": [0.0, C.STEM_Y, zs], "direction": [1.0, 0.0, 0.0], "parts": ["stem", "winding_pinion"]},
            "crown": {"point": [xc, 0.0, 0.0], "direction": [0.0, 0.0, 1.0], "parts": ["crown_wheel"]},
            "arbor": {"parts": ["ratchet"]},
        },
        "fixed": fixed,
        "meshes": [
            {"driver": "stem", "driver_teeth": zp, "driven": "crown", "driven_teeth": zc,
             "sense": "same" if side < 0 else "opposite"},
            {"driver": "crown", "driver_teeth": zcs, "driven": "arbor", "driven_teeth": zr, "sense": "opposite"},
        ],
    }
    for k, v in o["declare"].items():
        i, key = k
        spec["meshes"][i][key] = v
    return parts, spec


def write(out, parts, spec):
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    for n, man in parts.items():
        core.write_stl(os.path.join(out, "parts", n + ".stl"), man)
    json.dump(spec, open(os.path.join(out, "winding.json"), "w"), indent=1)


if __name__ == "__main__":
    p, s = build()
    write(sys.argv[1], p, s)
    print("wrote", sys.argv[1], sorted(p))
