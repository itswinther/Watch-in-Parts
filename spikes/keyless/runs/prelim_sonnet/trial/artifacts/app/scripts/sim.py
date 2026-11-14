import sys, os, json, math, itertools, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import trimesh
from manifold3d import Manifold, Mesh

SUB = '/app/submission'
def loadm(path):
    t = trimesh.load(path)
    return Manifold(Mesh(vert_properties=np.array(t.vertices, dtype=np.float32), tri_verts=np.array(t.faces, dtype=np.uint32)))

def rotmat(point, axis, ang):
    a = np.array(axis, float); a /= np.linalg.norm(a); p = np.array(point, float)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    R = np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K
    t = p - R @ p
    return np.hstack([R, t[:, None]])

def transl(v):
    return np.hstack([np.eye(3), np.array(v, float)[:, None]])

def compose(A, B):  # A after B
    A4 = np.vstack([A, [0, 0, 0, 1]]); B4 = np.vstack([B, [0, 0, 0, 1]])
    return (A4 @ B4)[:3]

class World:
    def __init__(self):
        cfg = json.load(open(f'{SUB}/keyless.json'))
        self.cfg = cfg
        self.parts = {}
        for n in os.listdir(f'{SUB}/parts'):
            self.parts[n[:-4]] = loadm(f'{SUB}/parts/{n}')
        for n in ['main_plate', 'dial_plate', 'barrel_arbor', 'minute_wheel', 'minute_post']:
            self.parts[n] = loadm(f'/app/supplied/{n}.stl')
        self.mob = {}
        for n, d in cfg['mobiles'].items():
            self.mob[n] = dict(d)
        self.mob['barrel']['parts'] = self.mob['barrel']['parts'] + ['barrel_arbor']
        self.mob['minute_wheel'] = {'kind': 'free', 'dof': 'rot', 'point': [4.65, -4.157, 0], 'direction': [0, 0, 1], 'parts': ['minute_wheel']}
        self.mob['barrel'].update({'dof': 'rot', 'point': [2.15, 4.157, 0], 'direction': [0, 0, 1]})
        self.mob['stem'].update({'dof': 'stem'})
        self.fixed = cfg['fixed'] + ['main_plate', 'dial_plate', 'minute_post']
        self.q = {n: 0.0 for n in self.mob}   # own coordinate
        self.stem_x = 0.0; self.stem_a = 0.0   # stem pull, stem rot angle (about +x)
        self.cache = {}

    def T(self, n, q=None, sx=None, sa=None):
        q = self.q[n] if q is None else q
        sx = self.stem_x if sx is None else sx
        sa = self.stem_a if sa is None else sa
        d = self.mob[n]
        if n == 'stem':
            return compose(transl([sx, 0, 0]), rotmat([0, 0, 0], [1, 0, 0], sa))
        if d['dof'] == 'rot':
            return rotmat(d['point'], d['direction'], q)
        v = np.array(d['direction'], float); v /= np.linalg.norm(v)
        M = transl(v * q)
        if d.get('on_stem'):
            M = compose(M, rotmat([0, 0, 0], [1, 0, 0], sa))
        return M

    def body(self, n, **kw):
        T = self.T(n, **kw)
        ms = [self.parts[p].transform(T) for p in self.mob[n]['parts']]
        r = ms[0]
        for m in ms[1:]: r = r + m
        return r

    def fixedbody(self, n):
        return self.parts[n]

def overlap(a, b):
    return (a ^ b).volume()

if __name__ == '__main__':
    w = World()
    names = list(w.mob) 
    bodies = {n: w.body(n) for n in names}
    for f in w.fixed: bodies[f] = w.parts[f]
    ks = list(bodies)
    print('--- rest overlaps > 0.0002')
    for a, b in itertools.combinations(ks, 2):
        if a in ('barrel',) and b in () : continue
        v = overlap(bodies[a], bodies[b])
        if v > 1e-4: print(a, b, round(v, 5))
    print('--- held tests')
    for n in names:
        d = w.mob[n]
        if d['kind'] not in ('free', 'spring'): continue
        dirv = np.array(d['direction'], float); dirv /= np.linalg.norm(dirv)
        # perpendicular dirs
        a = np.cross(dirv, [0, 0, 1.0]); 
        if np.linalg.norm(a) < 1e-6: a = np.cross(dirv, [0, 1.0, 0])
        a /= np.linalg.norm(a); b = np.cross(dirv, a)
        tests = [a, -a, b, -b]
        if d['dof'] == 'rot': tests += [dirv, -dirv]
        res = []
        for t in tests:
            m = bodies[n].transform(transl(0.3 * t))
            mx = 0
            for k in ks:
                if k == n: continue
                mx = max(mx, overlap(m, bodies[k]))
            res.append(round(mx, 4))
        print(n, res)
