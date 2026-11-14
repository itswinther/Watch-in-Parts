"""NOT-FOR-AGENT (realcad test material; never copy into a task image).

Phase the converted CAD: let the rig settle the mobiles once, then write the parts at the settled poses.

    python -I phase_ml01.py SUB_IN DATA_IN SUB_OUT DATA_OUT [MOBILE=DEG ...]

The STEP assembly shows meshing wheels unphased (tooth through tooth), as CAD assemblies often do.
A designer delivering parts "at rest" would turn each wheel into its gap; this does exactly that with
the rig's own settle (at most 0.3 mm of surface travel per mobile) and records every angle it applied.
The supplied barrel member (barrel_arbor) is turned with the barrel mobile.
"""
import json
import math
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import grade_real as R  # noqa: E402
import numpy as np  # noqa: E402
from convert_ml01 import man_tris, write_stl  # noqa: E402

src, data, dst, dout = sys.argv[1:5]
pre = {k: float(v) for k, v in (a.split("=") for a in sys.argv[5:])}   # turns applied before the settle
R.apply(dict(R.REAL, WIND_SENSE=1.0))
spec, parts, sup, defs = R.load(src, data)
w = R.make_world(parts, sup, defs)
before = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
for k, v in pre.items():
    w.bodies[k].q = math.radians(v)
w.settle()
# let the springs bring their parts home (several relax rounds: two springs in series follow each other)
for _ in range(60):
    q0 = {n: b.q for n, b in w.bodies.items()}
    for sb in w.order_spring:
        w.relax(sb)
    if all(abs(w.bodies[n].q - q0[n]) < 1e-9 for n in q0):
        break
after = {n: round(w.pen(b), 6) for n, b in w.bodies.items() if b.kind != "fixed"}
for a, b in ((src, dst), (data, dout)):
    if os.path.exists(b):
        shutil.rmtree(b)
    shutil.copytree(a, b)
moved = {}
for d in defs:
    b = w.bodies[d["name"]]
    carried = b.carrier and b.carrier != "stem" and abs(w.bodies[b.carrier].q) > 1e-12
    if b.kind == "fixed" or (abs(b.q) < 1e-12 and not carried):
        continue
    T = w.matrix(b)[:3, :4].tolist()
    if carried:     # a rider on a moved carrier: its axis point moves with the carrier
        c = w.bodies[b.carrier]
        Mc = R.E.rot_matrix(c.point, c.dir, c.q)
        newpt = (Mc @ np.r_[np.asarray(spec["mobiles"][d["name"]]["point"], float), 1.0])[:3]
        spec["mobiles"][d["name"]]["point"] = [round(float(v), 6) for v in newpt]
    for p in d["parts"]:
        if p.startswith("@"):
            if p == "@barrel_arbor":       # the supplied barrel member turns with the barrel
                write_stl(os.path.join(dout, "barrel_arbor.stl"), man_tris(sup["barrel_arbor"].transform(T)))
            continue
        write_stl(os.path.join(dst, "parts", p + ".stl"), man_tris(parts[p].transform(T)))
    moved[d["name"]] = round(math.degrees(b.q), 4) if b.dof == "rot" else round(b.q, 5)
json.dump(spec, open(os.path.join(dst, "keyless.json"), "w"), indent=1)
w2 = R.make_world(*R.load(dst, dout)[1:])
final = {n: round(w2.pen(b), 6) for n, b in w2.bodies.items() if b.kind != "fixed"}
print(json.dumps({"pre_turns_deg": pre, "final_rest_pen": final}, indent=1))
print(json.dumps({"pen_before": before, "pen_after_settle": after, "baked_deg_or_mm": moved}, indent=1))
