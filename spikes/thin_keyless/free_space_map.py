"""Free-space map of a thin delivery (a/thin-po), per z band, 0.5 mm grid, case radius THIN_CASE_RADIUS; also the
supplied thin arbor profile. Docker only: WATCH_THIN_BARREL=1 THIN_CASE_RADIUS=12.36 python3 free_space_map.py DELIVERY.
Used by the thin keyless feasibility check (SESSION.md, A, thin keyless)."""
import sys, numpy as np
sys.path.insert(0, "/w")
from geometry import watch as W
import manifold3d as m3
m = W.load_movement(sys.argv[1])
parts = dict(m.fixed_parts)
for k, mo in m.mobiles.items():
    for n, s in mo["parts"].items(): parts[n] = s
for n, s in W.barrel_bodies().items(): parts[n] = s
# arbor profile
arb = parts["barrel_arbor"]
for z in np.arange(-0.45, 2.56, 0.1):
    sl = arb.slice(float(z)); 
    b = sl.bounds() if hasattr(sl,'bounds') else None
    print("arbor z %.2f bounds %s area %.3f" % (z, [round(v,3) for v in sl.bounds()] if b is not None else None, sl.area()))
cx, cy = m.case_centre; R = W.CASE_RADIUS
bands = [(0.0,0.455),(0.5,1.35),(1.4,2.0),(2.05,2.22),(2.27,2.88)]
xs = np.arange(-11, 15.01, 0.5); ys = np.arange(13, -12.01, -0.5)
for z0, z1 in bands:
    print("\nband", z0, z1, "rows y from 13 down, cols x from -11, step 0.5; '.' free, letter = part, ' ' outside case")
    secs = {n: [s.slice(float(z)) for z in np.linspace(z0, z1, 4)] for n, s in parts.items()
            if s.bounding_box()[2] < z1 and s.bounding_box()[5] > z0}
    keys = sorted(secs)
    print({k[:2] + str(i): k for i, k in enumerate(keys)})
    for y in ys:
        row = ""
        for x in xs:
            if np.hypot(x - cx, y - cy) > R: row += " "; continue
            ch = "."
            for i, n in enumerate(keys):
                pt = m3.CrossSection.square([0.01,0.01]).translate([x,y])
                if any((cs ^ pt).area() > 0 for cs in secs[n]):
                    ch = chr(ord('A') + i) if i < 26 else chr(ord('a') + i - 26); break
            row += ch
        print("%6.1f %s" % (y, row))
