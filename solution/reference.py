"""Reference design for instance H1. One parametric script.
    python solution/reference.py OUT_DIR
writes OUT_DIR/base.stl, OUT_DIR/door.stl, OUT_DIR/assembly.json.

Board path: tilt +X end down, slide along the board's own axis until J2 is in its
window and the PCB edge is near the +X wall, flatten about that edge to a small
residual tilt, slide back toward -X with the -X end still above the pegs, then
rotate the last degree down onto the pegs.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import numpy as np
from geometry import constants as C
from geometry.core import box, cyl_z, cyl_x, union, write_stl

# ---- parameters (mm) ----
WALL = 1.6
X0, X1 = -1.85, 73.35          # outer
Y0, Y1 = -1.85, 46.85
ZTOP = 12.5
FLOOR_BOT, FLOOR_TOP = -8.5, -6.9
DOOR_BOT = -10.1
BATT_XY = (9.0, 4.0)           # battery corner in the world
BATT_GAP = 0.3
POST_R = 3.5
PEG_R, PEG_H = 1.5, 1.0
PEG_HOLES = (0, 2)             # the two -X holes
J1_WIN_PAD = 0.05
J2_WIN_R = 4.05
J2_WIN_Y = (8.5, 15.5)
J2_WIN_Z = (-6.0, 1.0)
DOOR_LAP = 3.5

TILT = math.radians(15.0)
TILT_SEAT = math.radians(1.2)
X_PIVOT_IN = 71.55             # world x of the PCB top +X edge while inserted
SLIDE_LEN = 90.0
STEP = 0.4
ROT_STEP = math.radians(0.3)


def build_base():
    tub = box((X0, Y0, FLOOR_BOT), (X1, Y1, ZTOP)) - box((X0 + WALL, Y0 + WALL, FLOOR_TOP), (X1 - WALL, Y1 - WALL, ZTOP + 1))
    sx, sy, _ = C.BATTERY_SIZE
    bx, by = BATT_XY
    opening = box((bx - BATT_GAP, by - BATT_GAP, FLOOR_BOT - 1), (bx + sx + BATT_GAP, by + sy + BATT_GAP, FLOOR_TOP + 1))
    posts = [cyl_z(x, y, FLOOR_TOP - 0.5, 0.0, POST_R) for x, y in C.HOLES]
    pegs = [cyl_z(C.HOLES[i][0], C.HOLES[i][1], -0.5, PEG_H, PEG_R) for i in PEG_HOLES]
    (ky0, kz0), (ky1, kz1) = C.J1_KEEPOUT_YZ
    p = J1_WIN_PAD
    win1 = box((X0 - 1, ky0 - p, kz0 - p), (X0 + WALL + 0.5, ky1 + p, kz1 + p))
    cy, cz = C.J2_KEEPOUT_CENTRE_YZ
    win2 = union([cyl_x(cy, cz, X1 - WALL - 0.5, X1 + 1, J2_WIN_R, 96),
                  box((X1 - WALL - 0.5, J2_WIN_Y[0], J2_WIN_Z[0]), (X1 + 1, J2_WIN_Y[1], J2_WIN_Z[1]))])
    return union([tub - opening] + posts + pegs) - win1 - win2


def build_door():
    sx, sy, _ = C.BATTERY_SIZE
    bx, by = BATT_XY
    return box((bx - DOOR_LAP, by - DOOR_LAP, DOOR_BOT), (bx + sx + DOOR_LAP, by + sy + DOOR_LAP, FLOOR_BOT))


def board_pose(theta, xp):
    """PCB top +X edge (local x 70, z 1.6) at world x = xp, with the J2 axis
    (local z -2.5) passing through the window centre on the wall mid-plane."""
    c, s = math.cos(theta), math.sin(theta)
    a = C.J2_WALL_PLANE_X - xp
    zp = C.J2_KEEPOUT_CENTRE_YZ[1] + (a + 4.1 * s) * s / c + 4.1 * c
    R = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    pivot = np.array([70.0, 0.0, 1.6])
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = np.array([xp, 0.0, zp]) - R @ pivot
    return T


def board_path():
    poses = []
    n = int(math.ceil(SLIDE_LEN / STEP))
    for i in range(n + 1):
        poses.append(board_pose(TILT, X_PIVOT_IN - SLIDE_LEN * math.cos(TILT) * (1 - i / n)))
    n = int(math.ceil((TILT - TILT_SEAT) / ROT_STEP))
    for i in range(1, n + 1):
        poses.append(board_pose(TILT + (TILT_SEAT - TILT) * i / n, X_PIVOT_IN))
    n = int(math.ceil((X_PIVOT_IN - 70.0) / STEP))
    for i in range(1, n + 1):
        poses.append(board_pose(TILT_SEAT, X_PIVOT_IN + (70.0 - X_PIVOT_IN) * i / n))
    n = int(math.ceil(TILT_SEAT / ROT_STEP))
    for i in range(1, n + 1):
        poses.append(board_pose(TILT_SEAT * (1 - i / n), 70.0))
    poses[-1] = np.eye(4)
    return poses


def straight(final, direction, dist):
    n = int(math.ceil(dist / STEP))
    out = []
    for i in range(n + 1):
        T = np.array(final, dtype=float)
        T[:3, 3] += np.array(direction, float) * dist * (1 - i / n)
        out.append(T)
    return out


def build_assembly():
    Tb = np.eye(4)
    Tb[:3, 3] = (BATT_XY[0], BATT_XY[1], FLOOR_BOT)
    return {
        "board": board_path(),
        "lid": straight(np.eye(4), (0, 0, 1), 35.0),
        "battery": straight(Tb, (0, 0, -1), 40.0),
        "door": straight(np.eye(4), (0, 0, -1), 40.0),
    }


def main(out):
    os.makedirs(out, exist_ok=True)
    base, door = build_base(), build_door()
    write_stl(os.path.join(out, "base.stl"), base)
    write_stl(os.path.join(out, "door.stl"), door)
    asm = {k: [np.asarray(T).tolist() for T in v] for k, v in build_assembly().items()}
    with open(os.path.join(out, "assembly.json"), "w") as f:
        json.dump(asm, f)
    print("base volume %.2f, door volume %.2f, total %.2f mm3; poses %s"
          % (base.volume(), door.volume(), base.volume() + door.volume(), {k: len(v) for k, v in asm.items()}))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
