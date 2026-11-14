"""Write the supplied parts (fixed plates, barrel arbor, minute-wheel stand-in) as binary STL.

    python supplied.py DATA_DIR
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import constants as C  # noqa: E402
import gears as G  # noqa: E402
import shapes as S  # noqa: E402


def build():
    cx, cy = C.CASE_CENTRE
    bx, by = C.BARREL_AXIS
    mx, my = C.MINUTE_AXIS
    R = C.CASE_RADIUS - 0.3
    main = S.cyl_z(cx, cy, 2.6, 3.2, R, 192) - S.cyl_z(bx, by, 2.0, 4.0, 0.65, 64)
    dial = S.cyl_z(cx, cy, -3.2, -2.6, R, 192)
    arbor = S.union([S.cyl_z(bx, by, 0.9, 3.35, 0.6, 64), S.cyl_z(bx, by, 3.22, 3.35, 0.9, 64)])
    mw = G.spur(36, 0.2, -2.4, -1.9, thin=0.004, phase=math.pi / 36).translate([mx, my, 0])
    mw = S.union([mw, S.cyl_z(mx, my, -2.4, -1.9, 1.0, 64)]) - S.cyl_z(mx, my, -3, 0, 0.36, 48)
    post = S.union([S.cyl_z(mx, my, -2.7, -1.75, 0.33, 48), S.cyl_z(mx, my, -1.85, -1.75, 0.6, 48)])
    return {"main_plate": main, "dial_plate": dial, "barrel_arbor": arbor, "minute_wheel": mw, "minute_post": post}


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for n, m in build().items():
        S.write_stl(os.path.join(out, n + ".stl"), m)
    print("wrote", sorted(build()))
