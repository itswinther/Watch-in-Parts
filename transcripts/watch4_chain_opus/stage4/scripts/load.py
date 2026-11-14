import sys, os, json, pickle
sys.path.insert(0, 'tools')
import kernel, submit
import numpy as np
mv = json.load(open('work/movement.json'))
names = list(mv['fixed']) + [p for m in mv['mobiles'].values() for p in m['parts']]
out = {}
for n in names:
    man = submit.load(os.path.join("work/parts", n + ".step"))
    out[n] = man
    print(n, np.round(man.bounding_box(),3), round(man.volume(),3), flush=True)
b = kernel.tris_to_manifold(kernel.read_stl('meshes/barrel.stl', 200000, 33554432))
out['barrel'] = b
print('barrel', np.round(b.bounding_box(),3))
mesh = {k: (np.asarray(v.to_mesh().vert_properties)[:, :3].copy(), np.asarray(v.to_mesh().tri_verts).copy()) for k, v in out.items()}
pickle.dump(mesh, open('scripts/cache.pkl', 'wb'))
