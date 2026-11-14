"""Reference keyless works, and the variations the anchors use.

    python reference.py OUT_SUBMISSION_DIR

Writes OUT/parts/*.stl and OUT/keyless.json.

Layout (position 1, stem pushed in), along the stem from the case centre outwards (+x):
  stem bridge | winding pinion (spur teeth, then Breguet face teeth facing +x) | sliding pinion
  (Breguet teeth facing -x, square bore, spur teeth at its outer end) | stem out through the case.
Above the stem: the crown wheel (face teeth down, spur pinion on top) drives the barrel gear and,
with it, the ratchet ring the click holds. Below the stem: the setting wheel (face teeth up, spur
pinion underneath) drives the supplied minute wheel. A collar on the stem sits in a counterbore of
the sliding pinion: pulling the stem drags the sliding pinion out of the Breguet teeth and into the
setting wheel; the sliding pinion's spring pushes it back in (towards -x).
"""
import json
import math
import os
import sys

import numpy as np
import manifold3d as m3

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import constants as C  # noqa: E402
import gears as G  # noqa: E402
import shapes as S  # noqa: E402

DEFAULT = {
    "breguet_n": 8, "breguet_h": 0.15, "breguet_steep": 0.03,  # steep fraction of the pitch (0.5 = symmetric)
    "clear": 0.012,
    "collar_gap": 0.15,
    "sp_teeth_x": (3.4, 3.9),          # sliding pinion spur teeth, x range at rest
    "click": True,
    "rest_sign_slider": -1, "rest_sign_click": 1,
    "shift": {},                       # part -> (dx, dy, dz) moved off its declared axis
}

M_FACE, ZP, ZC = 0.15, 12, 36
M_SPUR, ZS, ZB = 0.2, 12, 36
BL = 0.004


def warp_cyl_x(man, r_mean):
    """(u, x, r) -> (x, r cos(u/r_mean), r sin(u/r_mean)): unrolled band to a ring about +x."""
    def f(v):
        u, x, r = v
        t = u / r_mean
        return (x, r * math.cos(t), r * math.sin(t))
    out = man.refine_to_length(0.03).warp(f)
    if out.volume() < 0 or out.status() != m3.Error.NoError:
        raise RuntimeError("warp failed")
    return out


def breguet(o, x0, x1, r_in, r_out, sliding):
    """Sliding teeth (sliding=True) or the complementary winding-pinion teeth, x0 < x1 the band."""
    n, steep = o["breguet_n"], o["breguet_steep"]
    rm = 0.5 * (r_in + r_out)
    pu = 2 * math.pi * rm / n                       # pitch in unrolled mm
    tris = []
    for k in range(n):
        u0 = k * pu
        # sliding tooth: steep face at u0 (from x1 down to the tip x0), ramp back up to x1 by u0 + (1-steep) pu
        if o.get("breguet_square"):                 # dog teeth: vertical faces both ways
            tri = [(u0, x1), (u0, x0), (u0 + 0.45 * pu, x0), (u0 + 0.45 * pu, x1)]
        elif steep >= 0.49:                         # symmetric: tip in the middle
            tri = [(u0, x1), (u0 + 0.5 * pu, x0), (u0 + pu, x1)]
        else:
            tri = [(u0, x1), (u0 + steep * pu, x0), (u0 + pu * (1 - 0.0), x1)]
        tris.append(tri)
    cs = m3.CrossSection(tris, m3.FillRule.Positive) if all(S._area(t) > 0 for t in tris) else \
        m3.CrossSection([t[::-1] for t in tris], m3.FillRule.Positive)
    if sliding:
        prof = cs
        # base layer behind the teeth so the teeth join the pinion body
        prof = prof + m3.CrossSection.square([2 * math.pi * rm + 0.2, 0.05]).translate([-0.1, x1 - 0.001])
    else:
        band = m3.CrossSection.square([2 * math.pi * rm + 0.2, x1 - x0 + 0.05]).translate([-0.1, x0 - 0.05])
        prof = band - cs.offset(o["clear"], m3.JoinType.Miter)
    sol = m3.Manifold.extrude(prof, r_out - r_in).translate([0, 0, r_in])
    # clip to one turn exactly
    clip = m3.Manifold.cube([2 * math.pi * rm, 10, r_out - r_in]).translate([0, x0 - 2, r_in])
    sol = sol ^ clip
    return warp_cyl_x(sol, rm)


def build(opts=None):
    o = dict(DEFAULT)
    o.update(opts or {})
    ZS, ZB = o.get("zs_crown", 12), o.get("zb", 36)     # crown spur and barrel gear (same centre distance if ZS+ZB = 48)
    parts, spec_mob, fixed = {}, {}, []
    bx, by = C.BARREL_AXIS
    mx, my = C.MINUTE_AXIS

    # ---------- winding pinion: spur teeth x 1.6..2.1, hub to 2.45, Breguet band 2.45..2.6 ----------
    xw0, xw1 = 1.6, 2.1
    bx0, bx1 = 2.45, 2.45 + o["breguet_h"]
    r_in, r_out = 0.45, 0.85
    wp = G.pinion_along_x(ZP, M_FACE, xw0, xw1, 0.0, 0.0)
    hub = S.cyl_x(0, 0, xw1 - 0.01, bx0 + 0.01, 0.68, 64)
    wteeth = None if o.get("no_teeth") else breguet(o, bx0, bx1, r_in, r_out, sliding=False)
    wpin = S.union([wp, hub, wteeth]) - S.cyl_x(0, 0, 0, 5, 0.37, 48)
    parts["winding_pinion"] = wpin

    # ---------- sliding pinion ----------
    sx0 = bx1 + o["clear"]            # body starts just behind the teeth band
    st0, st1 = (v + o.get("teeth_shift", 0.0) for v in o["sp_teeth_x"])
    steeth = None if o.get("no_teeth") else breguet(o, bx0 + o["clear"] / 2, sx0, r_in, r_out, sliding=True)
    body = S.cyl_x(0, 0, sx0 - 0.002, st0 + 0.01, 0.85, 64)
    spur_t = G.pinion_along_x(ZP, M_FACE, st0, st1, 0.0, 0.0)
    sp = S.union([steeth, body, spur_t])
    # bore: counterbore r 0.55 from the teeth side to x 3.0, square 0.62 beyond
    ce = o.get("cbore_end", 3.0)
    sp = sp - S.cyl_x(0, 0, bx0 - 1, ce, 0.55, 48)
    sp = sp - S.box([ce - 0.1, -0.31, -0.31], [st1 + 1, 0.31, 0.31])
    parts["sliding_pinion"] = sp

    # ---------- stem ----------
    xc_ = 2.85 - (0.15 - o["collar_gap"])
    stem = S.union([
        S.cyl_x(0, 0, 0.6, xc_ - 0.2, 0.35, 48),
        S.cyl_x(0, 0, xc_ - 0.2, xc_, 0.5, 48),                    # collar in the counterbore
        S.box([xc_ - 0.01, -0.3, -0.3], [4.8, 0.3, 0.3]),          # square
        S.cyl_x(0, 0, 4.79, 12.6, 0.35, 48),
        S.cyl_x(0, 0, 12.6, 13.4, 1.0, 64),                       # crown, outside the case
    ])
    parts["stem"] = stem

    # ---------- stem bridge (winding pinion's inner side) ----------
    br = S.box([1.1, -0.8, -1.2], [1.48, 0.8, 1.2]) - S.cyl_x(0, 0, 0, 3, 0.37, 48)
    parts["stem_bridge"] = br
    fixed.append("stem_bridge")
    # outer stem guide near the case wall
    guide = S.box([11.4, -0.6, -0.8], [11.95, 0.6, 0.8]) - S.cyl_x(0, 0, 11, 13, 0.37, 48)
    parts["stem_guide"] = guide
    fixed.append("stem_guide")

    # ---------- crown wheel (face teeth down over the winding pinion, spur pinion on top) ----------
    R = M_FACE * ZC / 2.0
    xcw = (xw0 + xw1) / 2 + R
    ri, ro = R - 0.35, R + 0.35
    rp = M_FACE * ZP / 2
    zt, zr = rp - M_FACE, rp + 1.25 * M_FACE
    ring = G.face_gear(ZC, ZP, M_FACE, (xcw, 0.0), ri, ro, zr, zt, 0.0, cutter_thin=-BL, steps_per_pitch=16)
    web = S.cyl_z(xcw, 0, zr - 0.01, 1.3, ro, 128)
    chub = S.cyl_z(xcw, 0, 1.29, 2.5, min(0.9, M_SPUR * (ZS / 2 - 1.25) - 0.02), 64)
    cspur = G.spur(ZS, M_SPUR, 1.4, 1.9, thin=BL, phase=math.pi / ZS).translate([xcw, 0, 0])
    crown = S.union([ring, web, chub, cspur])
    crown = crown - S.cyl_z(xcw, 0, 1.0, 3.0, 0.36, 48) - S.cyl_z(xcw, 0, 1.4, 1.62, 0.66, 48)
    parts["crown_wheel"] = crown
    cpost = S.union([S.cyl_z(xcw, 0, 1.5, 2.7, 0.33, 48), S.cyl_z(xcw, 0, 1.45, 1.57, 0.6, 48)])
    parts["crown_post"] = cpost
    fixed.append("crown_post")

    # ---------- barrel gear + ratchet ring on the arbor ----------
    bgear = G.spur(ZB, M_SPUR, 1.4, 1.9, thin=BL).translate([bx, by, 0])
    bgear = S.union([bgear, S.cyl_z(bx, by, 1.4, 1.9, 1.5, 64)]) - S.cyl_z(bx, by, 0, 4, 0.6, 48)
    # phase so a barrel tooth faces the crown gap: rotate until no overlap
    for k in range(40):
        ph = k * 2 * math.pi / ZB / 40
        g = G.spur(ZB, M_SPUR, 1.4, 1.9, thin=BL, phase=ph).translate([bx, by, 0])
        if (g ^ cspur).volume() < 1e-6:
            bgear = S.union([g, S.cyl_z(bx, by, 1.4, 1.9, 1.5, 64)])
            break
    # sleeve that grips the arbor (the arbor is supplied; the sleeve overlaps it slightly = fitted)
    sleeve = S.cyl_z(bx, by, 1.38, 2.52, 0.75, 64)
    ring_r = S.ratchet_wheel(24, 2.5, 2.9, 2.0, 2.5) if not o.get("no_ratchet_teeth") else \
        S.cyl_z(0, 0, 2.0, 2.5, 2.45, 96)
    ring_r = ring_r.rotate([0, 0, 180]).translate([bx, by, 0])   # valley at angle 180 deg (towards -x)
    barrel_parts = S.union([bgear, sleeve, ring_r, S.cyl_z(bx, by, 1.89, 2.01, 1.5, 64)])
    barrel_parts = barrel_parts - S.cyl_z(bx, by, 0, 4, 0.6, 64)
    parts["barrel_wheel"] = barrel_parts

    # ---------- click ----------
    if o["click"]:
        ck, piv = S.click(24, 2.5, 2.9, 2.0, 2.5) if not o.get("sliver_click") else S.click(24, 2.5, 2.9, 2.249, 2.251)
        ck = ck.rotate([0, 0, 180]).translate([bx, by, 0])
        pv = (-piv[0] + bx, -piv[1] + by)
        ck = ck - S.cyl_z(pv[0], pv[1], 1.5, 3.0, 0.23, 48)
        # open it 1.5 deg outwards about its pivot so it starts clear of the ratchet
        ck = ck.translate([-pv[0], -pv[1], 0]).rotate([0, 0, -1.5]).translate([pv[0], pv[1], 0])
        parts["click"] = ck
        kpost = S.union([S.cyl_z(pv[0], pv[1], 1.92, 2.7, 0.2, 48), S.cyl_z(pv[0], pv[1], 1.92, 1.98, 0.4, 48)])
        parts["click_post"] = kpost
        fixed.append("click_post")

    # ---------- setting wheel (below the stem, face teeth up, engaged by the pulled sliding pinion) ----------
    d_pull = C.PULL - DEFAULT["collar_gap"]    # sliding pinion travel at position 2 (designed)
    xs_eng = sum(DEFAULT["sp_teeth_x"]) / 2 + d_pull   # sliding pinion spur teeth centre at position 2 (designed)
    rs_in, rs_out = R - 0.25, R + 0.25
    xsw = xs_eng + R + o.get("set_offset", 0.0)
    sring = G.face_gear(ZC, ZP, M_FACE, (0.0, 0.0), rs_in, rs_out, zr, zt, 0.0, cutter_thin=-BL, steps_per_pitch=16)
    sring = sring.mirror([0, 0, 1]).translate([xsw, 0, 0])
    sweb = S.cyl_z(xsw, 0, -1.3, -zr + 0.01, rs_out, 128)
    shub = S.cyl_z(xsw, 0, -2.5, -1.29, 0.9, 64)
    sspur = G.spur(12, M_SPUR, -2.4, -1.9, thin=BL, phase=0.0).translate([xsw, 0, 0])
    for k in range(40):
        ph = k * 2 * math.pi / 12 / 40
        g = G.spur(12, M_SPUR, -2.4, -1.9, thin=BL, phase=ph).translate([xsw, 0, 0])
        if (g ^ _minute_wheel()).volume() < 1e-6:
            sspur = g
            break
    setw = S.union([None if o.get("no_teeth") else sring, sweb, shub, sspur])
    setw = setw - S.cyl_z(xsw, 0, -3.0, -1.0, 0.36, 48) - S.cyl_z(xsw, 0, -1.62, -1.4, 0.66, 48)
    parts["setting_wheel"] = setw
    spost = S.union([S.cyl_z(xsw, 0, -2.7, -1.5, 0.33, 48), S.cyl_z(xsw, 0, -1.57, -1.45, 0.6, 48)])
    parts["setting_post"] = spost
    fixed.append("setting_post")

    for n, d in o["shift"].items():
        parts[n] = parts[n].translate(list(d))

    mobiles = {
        "stem": {"kind": "stem", "parts": ["stem"]},
        "winding_pinion": {"kind": "free", "dof": "rot", "point": [0, 0, 0], "direction": [1, 0, 0],
                           "parts": ["winding_pinion"]},
        "sliding_pinion": {"kind": "spring", "dof": "slide", "direction": [1, 0, 0], "on_stem": True,
                           "rest": o["rest_sign_slider"], "parts": ["sliding_pinion"]},
        "crown_wheel": {"kind": "free", "dof": "rot", "point": [xcw, 0, 0], "direction": [0, 0, 1],
                        "parts": ["crown_wheel"]},
        "barrel": {"kind": "barrel", "parts": ["barrel_wheel"]},
        "setting_wheel": {"kind": "free", "dof": "rot", "point": [xsw, 0, 0], "direction": [0, 0, 1],
                          "parts": ["setting_wheel"]},
    }
    if o["click"]:
        mobiles["click"] = {"kind": "spring", "dof": "rot", "point": [pv[0], pv[1], 0], "direction": [0, 0, 1],
                            "rest": o["rest_sign_click"], "parts": ["click"]}
    spec = {"mobiles": mobiles, "fixed": fixed}
    return parts, spec


def _minute_wheel():
    import supplied
    return supplied.build()["minute_wheel"]


def write(out, parts, spec, report=None):
    os.makedirs(os.path.join(out, "parts"), exist_ok=True)
    for n, man in parts.items():
        S.write_stl(os.path.join(out, "parts", n + ".stl"), man)
    json.dump(spec, open(os.path.join(out, "keyless.json"), "w"), indent=1)
    if report is None:      # the reference was checked with the grader's rules; it claims what it achieved
        report = {"steps": {k: "pass" for k in C.STEPS},
                  "summary": "Reference keyless works; every step checked with a contact simulation."}
    if report is not False:
        json.dump(report, open(os.path.join(out, "report.json"), "w"), indent=1)


if __name__ == "__main__":
    p, s = build()
    write(sys.argv[1], p, s)
    print("wrote", sys.argv[1], sorted(p))
