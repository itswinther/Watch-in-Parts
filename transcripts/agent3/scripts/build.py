import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import manifold3d as m3
from geometry.core import box, cyl_z, cyl_x, union, write_stl

# --- parameters ---
XO0, XO1, YO0, YO1 = -2.0, 73.5, -2.0, 47.0
W = 1.6
XI0, XI1, YI0, YI1 = XO0 + W, XO1 - W, YO0 + W, YO1 - W   # -0.4, 71.9, -0.4, 45.4
FLOOR_TOP = -5.5
FLOOR_BOT = FLOOR_TOP - W
ZTOP = 12.5
HOLES = ((3.5, 3.5), (66.5, 3.5), (3.5, 41.5), (66.5, 41.5))
PEG_R, PEG_H = 1.45, 0.8
LIFT = 0.9
# battery opening / door
OPEN_Y0, OPEN_Y1 = 13.4, YI1
OPEN_Z0, OPEN_Z1 = 3.25, 10.85
G = 0.02

def base():
    shell = box((XO0, YO0, FLOOR_BOT), (XO1, YO1, ZTOP)) - box((XI0, YI0, FLOOR_TOP), (XI1, YI1, ZTOP + 1))
    foot = box((70.3, 3.5, -8.6), (XO1, 20.5, FLOOR_TOP + 0.01))
    posts = [cyl_z(x, y, FLOOR_TOP - 0.5, 0.0, 3.5) for x, y in HOLES]
    pegs = [cyl_z(x, y, -0.1, PEG_H, PEG_R) for x, y in HOLES]
    b = union([shell, foot] + posts + pegs)
    # J1 window
    b = b - box((XO0 - 0.5, 16.2, -0.3), (XI0 + 0.1, 28.8, 6.8))
    # J2 window: union of circle (keep-out), final J2 + 0.4, lifted J2 + 0.15
    j2 = union([
        cyl_x(12.0, -2.5, XI1 - 0.1, XO1 + 0.5, 4.05, 128),
        box((XI1 - 0.1, 8.5, -5.5), (XO1 + 0.5, 15.5, 0.5)),
        box((XI1 - 0.1, 8.75, -4.25), (XO1 + 0.5, 15.25, LIFT + 0.25)),
    ])
    b = b - j2
    # battery opening
    b = b - box((XI1 - 0.1, OPEN_Y0, OPEN_Z0), (XO1 + 0.5, OPEN_Y1, OPEN_Z1))
    return b

def door():
    plate = box((XI1, OPEN_Y0 + G, OPEN_Z0 + G), (XO1, OPEN_Y1 - G, OPEN_Z1 - G))
    boss = box((68.05, 26.0, 5.0), (XI1 + 0.05, 34.0, 9.0))
    finger = box((40.0, OPEN_Y0 + G, OPEN_Z0 + G), (XI1 + 0.05, 15.33, 7.0))
    return union([plate, boss, finger])

if __name__ == "__main__":
    os.makedirs(os.path.join(ROOT, "work"), exist_ok=True)
    b, d = base(), door()
    print("base vol", b.volume(), "genus", b.genus(), "door vol", d.volume(), "sum", b.volume() + d.volume())
    write_stl(os.path.join(ROOT, "work", "base.stl"), b)
    write_stl(os.path.join(ROOT, "work", "door.stl"), d)
