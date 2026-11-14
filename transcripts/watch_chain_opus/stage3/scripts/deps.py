"""For each part and direction (+z/-z), which other parts does a straight sweep out of the assembly hit."""
import pickle, time
import numpy as np
from common import *

doc, parts, owner = load()
TB = total_bbox(parts)
print("total bbox", TB)
names = list(parts)
for n in names:
    print(n, owner[n], np.round(parts[n].bounding_box(), 2))
STEP = 0.2
res = {}
t0 = time.time()
for n in names:
    P = parts[n]
    bb = P.bounding_box()
    for d in (+1, -1):
        # distance needed so bbox clears grown total bbox in z
        if d > 0:
            dist = TB[5] + 5.0 - bb[2] + 0.5
        else:
            dist = bb[5] - (TB[2] - 5.0) + 0.5
        nsteps = int(np.ceil(dist / STEP))
        hits = {}
        for o in names:
            if o == n or owner[o] == owner[n]:
                continue
            Q = parts[o]
            qb = Q.bounding_box()
            # xy overlap?
            if not (bb[0] < qb[3] and qb[0] < bb[3] and bb[1] < qb[4] and qb[1] < bb[4]):
                continue
            mx = 0.0
            for i in range(nsteps + 1):
                dz = d * dist * i / nsteps
                if not (bb[2] + dz < qb[5] and qb[2] < bb[5] + dz):
                    continue
                v = kernel.ivol(P.translate([0, 0, dz]), Q)
                mx = max(mx, v)
                if mx > 0.01:
                    break
            if mx > 0.01:
                hits[o] = mx
        res[(n, d)] = sorted(hits)
        print(n, d, sorted(hits), round(time.time() - t0, 1), flush=True)
pickle.dump(res, open(os.path.join(ROOT, "scripts", "deps.pkl"), "wb"))
