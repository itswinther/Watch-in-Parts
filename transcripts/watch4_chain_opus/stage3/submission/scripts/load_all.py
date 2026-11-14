import sys, os, json, numpy as np
sys.path.insert(0, 'tools'); import kernel, submit
from concurrent.futures import ProcessPoolExecutor
def one(n):
    m = submit.load('work/parts/%s.step' % n)
    mesh = m.to_mesh()
    np.savez('scripts/cache/%s.npz' % n, v=np.array(mesh.vert_properties)[:, :3], f=np.array(mesh.tri_verts))
    v = np.array(mesh.vert_properties)[:, :3]
    return n, v.min(0), v.max(0), m.volume()
names = sys.argv[1:] or [f[:-5] for f in sorted(os.listdir('work/parts'))]
with ProcessPoolExecutor(8) as ex:
    for n, lo, hi, vol in ex.map(one, names):
        print('%-14s lo %s hi %s vol %.3f' % (n, np.round(lo, 3), np.round(hi, 3), vol))
