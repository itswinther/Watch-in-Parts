# builds work/assembly.json and checks it against rules 1-5 of stage 4
from common import *
from multiprocessing import Pool
doc, parts, mob = load_all()
names = list(parts)
bbs = {n: np.array(parts[n].bounding_box()) for n in names}
LO = np.min([bbs[n][:3] for n in names], axis=0) - 5.0
HI = np.max([bbs[n][3:] for n in names], axis=0) + 5.0
blk = json.load(open(os.path.join(ROOT, "cache", "block.json")))
STEP = 0.19
def line(p0, p1):
    p0, p1 = np.array(p0, float), np.array(p1, float)
    k = max(1, int(np.ceil(np.linalg.norm(p1 - p0) / STEP)))
    return [p0 + (p1 - p0) * i / k for i in range(k + 1)]
def vert(n, d, lateral=(0, 0)):
    b = bbs[n]
    D = (HI[2] - b[2] + 0.05) if d > 0 else (b[5] - LO[2] + 0.05)
    return line([lateral[0], lateral[1], d * D], [lateral[0], lateral[1], 0])
def greedy(first):
    # disassembly greedy; the parts in `first` stay present throughout (they are installed first)
    present = set(names); rev = []
    while present - set(first):
        for a in sorted(present - set(first)):
            ds = [d for d in (1, -1) if not (set(blk["%s|%d" % (a, d)]) & present)]
            if ds:
                rev.append((a, ds[0])); present.discard(a); break
        else:
            raise SystemExit("stuck %s" % sorted(present))
    return rev[::-1]
def check(args):
    n, path, before = args
    T = np.array(path)
    errs = []
    if not (2 <= len(T) <= 1500): errs.append("pose count")
    if not np.isfinite(T).all(): errs.append("nonfinite")
    for M in T:
        R = M[:3, :3]
        if abs(R.T @ R - np.eye(3)).max() > 1e-6 or abs(np.linalg.det(R) - 1) > 1e-6 or abs(M[3] - [0, 0, 0, 1]).max() > 1e-6:
            errs.append("not rigid"); break
    if abs(T[-1] - np.eye(4)).max() > 1e-6: errs.append("last not identity")
    V = kernel.verts(parts[n])
    W = np.einsum("pij,vj->pvi", T[:, :3, :3], V) + T[:, None, :3, 3]
    lo, hi = W[0].min(0), W[0].max(0)
    if not ((hi < LO).any() or (lo > HI).any()): errs.append("start inside box")
    mv = np.linalg.norm(W[1:] - W[:-1], axis=2).max()
    if mv > 0.2: errs.append("step %.4f" % mv)
    worst = (0.0, None, None)
    for i, M in enumerate(T):
        p = kernel.apply(parts[n], M)
        for b in before:
            if mob.get(b, "F:" + b) == mob.get(n, "F:" + n): continue
            v = kernel.ivol(p, parts[b])
            if v > worst[0]: worst = (v, b, i)
    if worst[0] > 0.01: errs.append("collides %s vol %.4f pose %d" % (worst[1], worst[0], worst[2]))
    return n, errs, mv, worst[0]
if __name__ == "__main__":
    ia, dw = "idler_arbor", "day_wheel_40t_m020"
    base = [(ia, -1)] + greedy([ia, dw])
    u = np.array(doc["mobiles"]["day"]["axis"]) - np.array(doc["mobiles"]["idler"]["axis"]); u /= np.linalg.norm(u)
    S = float(sys.argv[1]) if len(sys.argv) > 1 else 1.5
    d = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    order, paths = [], {}
    for n, dd in base:
        order.append(n); paths[n] = vert(n, dd)
        if n == ia:
            lat = u * S
            order.append(dw); paths[dw] = vert(dw, d, lat)[:-1] + line([lat[0], lat[1], 0], [0, 0, 0])
    P = {}
    for n in order:
        P[n] = [[[1, 0, 0, float(t[0])], [0, 1, 0, float(t[1])], [0, 0, 1, float(t[2])], [0, 0, 0, 1]] for t in paths[n]]
        P[n][-1] = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
    with Pool(4) as pool:
        res = pool.map(check, [(n, P[n], order[:i]) for i, n in enumerate(order)], chunksize=1)
    ok = 0
    for n, errs, mv, w in res:
        ok += not errs
        print("%-32s poses=%4d maxstep=%.4f worst_ivol=%.5f %s" % (n, len(P[n]), mv, w, "OK" if not errs else errs))
    print("installed", ok, "of", len(names), "order covers all:", set(order) == set(names))
    json.dump({"order": order, "paths": P}, open(os.path.join(ROOT, "work", "assembly.json"), "w"))
    print(order)
