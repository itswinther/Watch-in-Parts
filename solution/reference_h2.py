"""Reference design for instance H2.
    python solution/reference_h2.py OUT_DIR
writes OUT_DIR/base.stl, OUT_DIR/lid.stl, OUT_DIR/assembly.json.

Layout: board B and the speaker sit on the floor under board A (B is exactly as
tall as the space under A), board A rests on four posts and on B, the battery lies
on top of board A. Order: B, speaker, A, battery, lid.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
from geometry import constants as C
from geometry import h2_public as P
from geometry.core import box, cyl_z, cyl_x, union, write_stl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reference as h1

WALL = 1.6
GAP = 0.05
SLIDE = 1.55                              # how far board A overshoots toward +X while going in
X0, X1 = -GAP - WALL, 70.0 + SLIDE + GAP + WALL
Y0, Y1 = -GAP - WALL, 45.0 + GAP + WALL
UNDER = 6.8                               # board B height: 2.2 + 1.6 + 3.0
FLOOR_TOP = -UNDER
FLOOR_BOT = FLOOR_TOP - WALL
ZTOP = 12.1                               # top of C1
POST_R, PEG_R, PEG_H = 3.5, 1.5, 1.0
PEG_HOLES = (0, 2)
WIN_PAD = 0.05
J2_WIN_R, J2_WIN_Y, J2_WIN_Z = 4.05, (8.5, 15.5), (-6.0, 1.0)
T_B = (7.3, 0.1, FLOOR_TOP + 2.2)
T_SPK = (55.0, 30.0, FLOOR_TOP)
T_BATT = (21.0, 0.5, 1.6)
B_SLIDE = 1.3
STEP = 0.4


def build_base():
    tub = box((X0, Y0, FLOOR_BOT), (X1, Y1, ZTOP)) - box((X0 + WALL, Y0 + WALL, FLOOR_TOP), (X1 - WALL, Y1 - WALL, ZTOP + 1))
    posts = [cyl_z(x, y, FLOOR_TOP - 0.5, 0.0, POST_R) for x, y in C.HOLES]
    pegs = [cyl_z(C.HOLES[i][0], C.HOLES[i][1], -0.5, PEG_H, PEG_R) for i in PEG_HOLES]
    (ky0, kz0), (ky1, kz1) = C.J1_KEEPOUT_YZ
    p = WIN_PAD
    win1 = box((X0 - 1, ky0 - p, kz0 - p), (X0 + WALL + 0.5, ky1 + p, kz1 + p))
    cy, cz = C.J2_KEEPOUT_CENTRE_YZ
    win2 = union([cyl_x(cy, cz, X1 - WALL - 0.5, X1 + 1, J2_WIN_R, 96),
                  box((X1 - WALL - 0.5, J2_WIN_Y[0], J2_WIN_Z[0]), (X1 + 1, J2_WIN_Y[1], J2_WIN_Z[1]))])
    win3 = box((T_B[0] + 25.0 - p, Y0 - 1, T_B[2] + 1.2 - p), (T_B[0] + 38.0 + p, Y0 + WALL + 0.5, T_B[2] + 4.2 + p))
    return union([tub] + posts + pegs) - win1 - win2 - win3


def build_lid():
    return box((X0, Y0, ZTOP), (X1, Y1, ZTOP + P.LID_THICKNESS))


def straight(final, direction, dist, pre=None):
    """Straight approach along -direction ending at `final`; `pre` is an optional
    (direction, distance) side step done last."""
    out = []
    end = np.array(final, dtype=float)
    mid = end.copy()
    if pre:
        mid[:3, 3] += np.array(pre[0], float) * pre[1]
    n = int(math.ceil(dist / STEP))
    for i in range(n + 1):
        T = mid.copy()
        T[:3, 3] += np.array(direction, float) * dist * (1 - i / n)
        out.append(T)
    if pre:
        n = int(math.ceil(pre[1] / STEP))
        for i in range(1, n + 1):
            T = end.copy()
            T[:3, 3] += np.array(pre[0], float) * pre[1] * (1 - i / n)
            out.append(T)
    return out


def tr(t):
    T = np.eye(4)
    T[:3, 3] = t
    return T


def build_assembly():
    h1.X_PIVOT_IN = 70.0 + SLIDE
    return {"order": ["B", "speaker", "A", "battery"],
            "paths": {"B": straight(tr(T_B), (0, 0, 1), 50.0, pre=((0, 1, 0), B_SLIDE)),
                      "speaker": straight(tr(T_SPK), (0, 0, 1), 50.0),
                      "A": h1.board_path(),
                      "battery": straight(tr(T_BATT), (0, 0, 1), 45.0),
                      "lid": straight(np.eye(4), (0, 0, 1), 35.0)}}


def main(out):
    os.makedirs(out, exist_ok=True)
    base, lid = build_base(), build_lid()
    write_stl(os.path.join(out, "base.stl"), base)
    write_stl(os.path.join(out, "lid.stl"), lid)
    asm = build_assembly()
    doc = {"order": asm["order"], "paths": {k: [np.asarray(T).tolist() for T in v] for k, v in asm["paths"].items()}}
    with open(os.path.join(out, "assembly.json"), "w") as f:
        json.dump(doc, f)
    lo, hi = P.printed_bbox(base, lid)
    print("bounding box %s, volume %.1f mm3; poses %s" % (np.round(hi - lo, 3).tolist(), float(np.prod(hi - lo)),
                                                           {k: len(v) for k, v in doc["paths"].items()}))


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
