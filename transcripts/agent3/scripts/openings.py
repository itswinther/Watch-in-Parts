import sys, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import manifold3d as m3
from geometry.core import load_part, section_x
from geometry import bodies as B
base = load_part(os.path.join(ROOT, "work/base.stl"), 200000, 64 << 20, 0.005)
door = load_part(os.path.join(ROOT, "work/door.stl"), 200000, 64 << 20, 0.005)
pr = base + door
r1 = m3.CrossSection.square([18.5, 13.0]).translate([13.25, -3.25])
s1 = section_x(pr, -1.05)
print("J1 uncovered", (r1 - s1).area(), "of", r1.area())
c2 = m3.CrossSection.circle(7.0, 256).translate([12, -2.5])
s2 = section_x(pr, 72.55)
print("J2 uncovered", (c2 - s2).area(), "of", c2.area())
