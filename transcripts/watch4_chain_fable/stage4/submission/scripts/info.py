from common import *
doc, parts, mob = load_all()
for n, p in parts.items():
    b = p.bounding_box()
    print("%-32s %-12s %s tris=%d vol=%.2f" % (n, mob.get(n, "FIXED"), " ".join("%7.3f" % v for v in b), p.num_tri(), p.volume()))
