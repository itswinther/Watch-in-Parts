import sys, os, json, pickle
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import kernel
CACHE = os.environ.get('WCACHE', '<host>/scratchpad')

def load(name, d='work'):
    import manifold3d as m3, hashlib
    p = os.path.join(ROOT, d, 'parts', name + '.step')
    h = hashlib.md5(open(p, 'rb').read()).hexdigest()
    c = os.path.join(CACHE, h + '.pkl')
    if os.path.exists(c):
        v, t = pickle.load(open(c, 'rb'))
        return m3.Manifold(m3.Mesh(vert_properties=v, tri_verts=t))
    man = kernel.load_step_part(p, 16777216, 200000, 0.001, 0.1, 500, 120, 4096, 0.005)
    if not hasattr(man, 'to_mesh'):
        man = man[0] if isinstance(man, tuple) else man
    me = man.to_mesh()
    pickle.dump((np.asarray(me.vert_properties, dtype=np.float32), np.asarray(me.tri_verts)), open(c, 'wb'))
    return man

def barrel():
    return kernel.tris_to_manifold(kernel.read_stl(os.path.join(ROOT, 'meshes/barrel.stl'), 200000, 33554432))
