import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
blk = json.load(open(os.path.join(ROOT, "cache", "block.json")))
names = sorted({k.split("|")[0] for k in blk})
present = set(names); rev = []
while present:
    for a in sorted(present):
        ds = [d for d in (1, -1) if not (set(blk["%s|%d" % (a, d)]) & present)]
        if ds:
            rev.append((a, ds[0])); present.discard(a); break
    else:
        print("STUCK", sorted(present))
        for a in sorted(present):
            print(a, {d: sorted(set(blk["%s|%d" % (a, d)]) & present) for d in (1, -1)})
        break
print(rev[::-1])
