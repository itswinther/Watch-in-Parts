import sys, os, json
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from geometry import md, core

inst = md.flat_one()
APT = inst.apartment()
STEP = 4.0

def R_of(cols):
    """cols: images of local x,y,z as world vectors."""
    return np.array(cols, float).T

def pose(R, t):
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = t; return T

def rotm(axis, deg):
    return md.rot(axis, deg)[:3, :3]

class Path:
    def __init__(self, name, T0):
        self.name = name
        self.V = core.verts(inst.piece(name))
        self.poses = [np.array(T0, float)]
    @property
    def T(self): return self.poses[-1]
    def _wv(self, T): return self.V @ T[:3, :3].T + T[:3, 3]
    def goto(self, T1):
        """linear in translation, slerp-free: rotation about fixed axis via scipy."""
        from scipy.spatial.transform import Rotation as Rot, Slerp
        T0 = self.T
        d = np.abs(self._wv(T1) - self._wv(T0))
        dist = np.linalg.norm(self._wv(T1) - self._wv(T0), axis=1).max()
        # rotation angle bound
        ang = Rot.from_matrix(T1[:3, :3] @ T0[:3, :3].T).magnitude()
        r = np.linalg.norm(self.V, axis=1).max() + np.linalg.norm(T1[:3,3]-T0[:3,3])
        n = int(np.ceil(max(dist, ang * 300) / STEP)) or 1
        sl = Slerp([0, 1], Rot.from_matrix([T0[:3, :3], T1[:3, :3]]))
        for k in range(1, n + 1):
            s = k / n
            R = sl([s]).as_matrix()[0] if ang > 1e-12 else T0[:3, :3]
            self.poses.append(pose(R, (1 - s) * T0[:3, 3] + s * T1[:3, 3]))
        self.poses[-1] = np.array(T1, float)
    def move(self, d):
        T1 = self.T.copy(); T1[:3, 3] += d; self.goto(T1)
    def move_to(self, t):
        T1 = self.T.copy(); T1[:3, 3] = t; self.goto(T1)
    def rotate(self, axis, deg, pivot, d=(0, 0, 0), nsub=None):
        """rotate about world axis through pivot (pivot moves by d linearly)."""
        T0 = self.T.copy()
        pivot = np.asarray(pivot, float); d = np.asarray(d, float)
        r = np.linalg.norm(self._wv(T0) - pivot, axis=1).max()
        n = nsub or int(np.ceil((r * np.radians(abs(deg)) + np.linalg.norm(d)) / STEP)) or 1
        for k in range(1, n + 1):
            s = k / n
            Rr = rotm(axis, deg * s)
            p = pivot + s * d
            R = Rr @ T0[:3, :3]
            t = Rr @ (T0[:3, 3] - pivot) + p
            self.poses.append(pose(R, t))

def check(name, poses, placed, stride=1, verbose=True):
    body = inst.piece(name)
    worst = (0, -1, None)
    for i in range(0, len(poses), stride):
        mv = core.apply(body, poses[i])
        for pn, pm in placed.items():
            v = core.ivol(mv, pm)
            if v > worst[0]:
                worst = (v, i, pn)
    if verbose: print(name, len(poses), "worst", worst)
    return worst

def placed_dict(names):
    d = {"apartment": APT}
    for n in names:
        d[n] = core.apply(inst.piece(n), inst.final(n))
    return d

def fmt_messages(name, poses):
    return md.path_messages(inst, name, np.array(poses))

def save(order, paths):
    doc = {"order": order, "paths": {n: [np.round(T, 9).tolist() for T in p] for n, p in paths.items()}}
    with open(os.path.join(ROOT, "work", "plan.json"), "w") as f:
        json.dump(doc, f)
