# pairwise blocking for straight insertion along +z / -z (the offsets used are the submitted poses)
from common import *
from multiprocessing import Pool
doc, parts, mob = load_all()
names = list(parts)
bbs = {n: parts[n].bounding_box() for n in names}
LO = np.min([bbs[n][:3] for n in names], axis=0) - 5.0
HI = np.max([bbs[n][3:] for n in names], axis=0) + 5.0
def offsets(n, d):
    b = bbs[n]
    D = (HI[2] - b[2] + 0.05) if d > 0 else (b[5] - LO[2] + 0.05)
    k = int(np.ceil(D / 0.19))
    return [d * D * (1 - i / k) for i in range(k + 1)]
def work(args):
    a, d = args
    res = {}
    for b in names:
        if b == a or mob.get(a, "F:" + a) == mob.get(b, "F:" + b):
            continue
        mx = 0.0
        for z in offsets(a, d):
            v = kernel.ivol(parts[a].translate([0, 0, z]), parts[b])
            mx = max(mx, v)
            if mx > 0.01: break
        if mx > 0.005:
            res[b] = mx
    return a, d, res
if __name__ == "__main__":
    print("bbox", LO, HI)
    with Pool(4) as p:
        out = p.map(work, [(a, d) for a in names for d in (1, -1)], chunksize=1)
    blk = {}
    for a, d, res in out:
        blk["%s|%d" % (a, d)] = res
        print(a, d, sorted(res))
    json.dump(blk, open(os.path.join(ROOT, "cache", "block.json"), "w"))
