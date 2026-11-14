import pickle, json
import numpy as np
from common import *
doc, parts, owner = load()
TB = total_bbox(parts)
order = pickle.load(open("order.pkl","rb"))
paths = {}
for n, d in order:
    bb = parts[n].bounding_box()
    dist = (TB[5] + 5.0 - bb[2] + 1.0) if d > 0 else (bb[5] - (TB[2] - 5.0) + 1.0)
    k = int(np.ceil(dist / 0.18))
    poses = []
    for i in range(k + 1):
        T = np.eye(4); T[2, 3] = d * dist * (1 - i / k)
        poses.append([[float(round(x, 9)) for x in r] for r in T])
    paths[n] = poses
json.dump({"order": [n for n, _ in order], "paths": paths}, open(os.path.join(ROOT, "work", "assembly.json"), "w"))
print("written", len(order))
