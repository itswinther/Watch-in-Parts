"""As-made variant (modules 0.16 to 0.2, CL 0.13; a/thin-asmade). Layer-aware placement search for the small-case thin reference. Pure numpy/scipy."""
import math, random, sys, json
import numpy as np
from scipy.optimize import minimize
A,MP,B,C,D,BR,E,F,DI,H1,H2,H3 = range(12)
CL = 0.13           # radial clearance between non-meshing elements in one layer
HR = float(sys.argv[1]) if len(sys.argv) > 1 else 5.1   # hand reach
DR = HR - 2.0
# mobile -> list of (layers, radius)
def M(*items): return [(set(l), r) for l, r in items]
EL = {
 "barrel": M(([A], 9.8), ([MP,B,C,D,BR,H2,H3], 0.5), ([E,F,DI,H1], 1.0)),
 "third": M(([A], 1.4), ([B], 0.18*22), ([A,MP,B,C,D], 0.5)),
 "centre": M(([B], 0.18*25), ([C], 0.16*41), ([B,C,D,BR], 0.6), ([E], 0.16*7), ([F,DI,H1], 0.5), ([H2], HR + 0.02)),
 "hour": M(([F], 0.1536*21), ([DI], 1.0), ([H1], HR + 0.02)),
 "fourth": M(([C], 0.16*6), ([D], 0.16*38.5), ([B,C,D], 0.5)),
 "seconds": M(([D], 0.96), ([B,C,D,BR,E,F,DI,H1,H2], 0.5), ([H3], HR + 0.02)),
 "mw": M(([E], 0.16*19), ([F], 0.1536*6), ([E,F], 0.5)),
 "idler": M(([E], 1.2), ([F], 0.1536*11), ([E,F], 0.5)),
 "day": M(([E], 4.2), ([E,F], 0.8), ([DI,H1,H2], 0.5), ([H3], DR + 0.02)),
}
MESH = {("barrel","third"):A, ("third","centre"):B, ("centre","fourth"):C, ("fourth","seconds"):D,
        ("centre","mw"):E, ("mw","hour"):F, ("hour","idler"):F, ("idler","day"):E}
CD = {("barrel","third"):10.8, ("third","centre"):0.18*84/2, ("centre","fourth"):0.16*90/2, ("fourth","seconds"):0.16*85/2,
      ("centre","mw"):0.16*48/2, ("hour","idler"):0.1536*60/2, ("idler","day"):5.0}
def layer_r(m, L):
    return max([r for ls, r in EL[m] if L in ls], default=None)
def ok_pair(m1, m2, P):
    if {m1, m2} == {"centre", "hour"}: return True
    d = math.dist(P[m1], P[m2])
    ml = MESH.get((m1, m2), MESH.get((m2, m1)))
    for L in range(12):
        r1, r2 = layer_r(m1, L), layer_r(m2, L)
        if r1 is None or r2 is None or L == ml: continue
        if d < r1 + r2 + CL: return False
    if ml is not None:   # in the mesh layer, the gears mesh; each must still clear the other's arbor (checked by tooth sizes)
        pass
    return True
def reach(P, cc):
    return max(math.dist(P[m], cc) + max(r for _, r in EL[m]) for m in EL)
def build(th):
    P = {"barrel": (0.0, 0.0)}
    on = lambda c, r, a: (c[0] + r*math.cos(a), c[1] + r*math.sin(a))
    P["third"] = on(P["barrel"], CD[("barrel","third")], th[0])
    P["centre"] = on(P["third"], CD[("third","centre")], th[1])
    P["fourth"] = on(P["centre"], CD[("centre","fourth")], th[2])
    P["seconds"] = on(P["fourth"], CD[("fourth","seconds")], th[3])
    P["mw"] = on(P["centre"], CD[("centre","mw")], th[4])
    P["hour"] = P["centre"]
    P["idler"] = on(P["centre"], CD[("hour","idler")], th[5])
    P["day"] = on(P["idler"], CD[("idler","day")], th[6])
    return P
def valid(P):
    ms = list(EL)
    if math.dist(P["day"], P["centre"]) < 6.0: return False
    for i in range(len(ms)):
        for j in range(i+1, len(ms)):
            if not ok_pair(ms[i], ms[j], P): return False
    return True
def enclose(P):
    pts = [(P[m], max(r for _, r in EL[m])) for m in EL]
    f = lambda c: max(math.dist(p, c) + r for p, r in pts)
    best = min((minimize(f, x0, method="Nelder-Mead", options={"xatol":1e-5,"fatol":1e-6}) for x0 in [P["centre"], (3,0), (0,3), (-3,0), (0,-3)]), key=lambda r: r.fun)
    return best.fun, tuple(best.x)
def pillars(P, cc, R):
    """3 pillar spots (r 0.75, boss 0.85) inside R clear of every element in A..F by 0.15; best spread."""
    def clear(p):
        for m in EL:
            rr = max([r for ls, r in EL[m] if ls & {A,MP,B,C,D,BR,E,F}], default=0)
            if math.dist(p, P[m]) < rr + 0.75 + 0.15: return False
        return math.dist(p, cc) <= R - 0.85
    cands = []
    for a in range(0, 360, 2):
        for rr in np.arange(R - 0.85, 0, -0.1):
            p = (cc[0] + rr*math.cos(math.radians(a)), cc[1] + rr*math.sin(math.radians(a)))
            if clear(p): cands.append(p); break
    best, sc = None, -1
    for i in range(len(cands)):
        for j in range(i+1, len(cands)):
            for k in range(j+1, len(cands)):
                s = min(math.dist(cands[i], cands[j]), math.dist(cands[j], cands[k]), math.dist(cands[i], cands[k]))
                if s > sc: best, sc = (cands[i], cands[j], cands[k]), s
    return best, sc
rnd = random.Random(int(sys.argv[2]) if len(sys.argv) > 2 else 1)
N = int(sys.argv[3]) if len(sys.argv) > 3 else 200000
found = []
for it in range(N):
    th = [rnd.uniform(0, 2*math.pi) for _ in range(7)]
    P = build(th)
    # cheap prefilter: rough reach about the barrel-centre midpoint
    if not valid(P): continue
    R, cc = enclose(P)
    found.append((R, th))
found.sort()
print("valid", len(found))
out = []
for R, th in found[:4]:
    P = build(th)
    # local refine by random perturbation
    best = (R, th)
    for k in range(3000):
        t2 = [t + rnd.gauss(0, 0.05) for t in best[1]]
        P2 = build(t2)
        if not valid(P2): continue
        R2, _ = enclose(P2)
        if R2 < best[0]: best = (R2, t2)
    P = build(best[1]); R, cc = enclose(P)
    pl, sc = pillars(P, cc, R + 0.1)
    out.append((R, sc, best[1], cc))
    print("R %.3f pillar spread %.2f" % (R, sc), "th", ",".join("%.6f" % t for t in best[1]), "cc", cc, flush=True)
out.sort(key=lambda o: o[0] if o[1] > 3 else 99)
json.dump([{"R": o[0], "spread": o[1], "th": o[2], "cc": o[3]} for o in out], open("/t/layout2_%s.json" % (sys.argv[2] if len(sys.argv) > 2 else "1"), "w"))
