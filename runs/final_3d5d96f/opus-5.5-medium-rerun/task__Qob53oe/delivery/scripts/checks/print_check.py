import sys, math, json, time
import numpy as np
from vlib import *
from multiprocessing import Pool
H=0.05; OFF=0.0113
def check(name):
    _, v, f = load_one(name)
    man = to_man(v, f)
    bb = man.bounding_box()
    lo = np.array(bb[:3]) - 0.15; hi = np.array(bb[3:]) + 0.15
    k0 = np.floor((lo - OFF) / H)
    origin = OFF + k0 * H - H / 2
    shape = tuple(int(x) for x in np.ceil((hi - origin) / H).astype(int) + 1)
    t = time.time()
    n, dev = kernel.opening_test_slabs(man, tuple(origin), shape, H, 1.5, 1.0, 6.0)
    return name, n, dev, dev * H, time.time() - t
if __name__ == '__main__':
    names = sys.argv[1:]
    if not names:
        names = sorted({p for fn in ('movement.json','variant_6h.json') for d in [json.load(open(os.path.join(DEL,fn)))]
                        for p in list(d['fixed']) + [q for m in d['mobiles'].values() for q in m['parts']]})
    with Pool(8) as pool:
        for r in pool.imap_unordered(check, names):
            print('%-14s pieces %d  max dev %.2f vox = %.3f mm  %s  (%.0fs)' % (r[0], r[1], r[2], r[3], 'OK' if r[1]>=1 and r[3] <= 0.2+1e-9 else 'FAIL', r[4]), flush=True)
