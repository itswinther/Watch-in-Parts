import numpy as np
from scipy.signal import fftconvolve
from scipy import ndimage
from collections import deque

def plan2d(free_rects, piece_rects, thetas, bounds, res, start, goal, dil=1, pad=300):
    """free_rects/piece_rects: ((u0,v0),(u1,v1)). piece rotates by theta (deg, CCW) about its origin.
    start/goal: (u, v, theta_index). Returns list of (u, v, theta_deg)."""
    u0, u1, v0, v1 = bounds
    us = np.arange(u0, u1 + 1e-9, res); vs = np.arange(v0, v1 + 1e-9, res)
    U, Vv = np.meshgrid(us, vs, indexing="ij")
    free = np.zeros(U.shape, bool)
    for (a, b), (c, d) in free_rects:
        free |= (U >= a) & (U <= c) & (Vv >= b) & (Vv <= d)
    obs = ~free
    P = int(np.ceil(pad / res))
    obs_pad = np.pad(obs, P, constant_values=True)
    if dil: obs_pad = ndimage.binary_dilation(obs_pad, iterations=dil)
    obs_pad = obs_pad.astype(np.float32)
    Rm = max(np.hypot(x, y) for r in piece_rects for x in (r[0][0], r[1][0]) for y in (r[0][1], r[1][1]))
    K = int(np.ceil(Rm / res)) + 1
    assert K < P
    offs = np.arange(-K, K + 1) * res
    OU, OV = np.meshgrid(offs, offs, indexing="ij")
    F = np.zeros((len(thetas),) + U.shape, bool)
    for ti, th in enumerate(thetas):
        c, s = np.cos(np.radians(th)), np.sin(np.radians(th))
        # local coords of offset points
        lu = c * OU + s * OV; lv = -s * OU + c * OV
        ker = np.zeros(OU.shape, bool)
        h = res * 0.75
        for (a, b), (cc, d) in piece_rects:
            ker |= (lu >= a - h) & (lu <= cc + h) & (lv >= b - h) & (lv <= d + h)
        Kf = ker[::-1, ::-1].astype(np.float32)
        C = fftconvolve(obs_pad, Kf, mode="valid")
        # C[n] = sum_a obs_pad[n+a] ker[a]; config i -> n = i - K + P
        n0 = P - K
        F[ti] = C[n0:n0 + len(us), n0:n0 + len(vs)] < 0.5
    def idx(c):
        return (int(c[2]), int(round((c[0] - u0) / res)), int(round((c[1] - v0) / res)))
    s, g = idx(start), idx(goal)
    print("start free", F[s], "goal free", F[g], "free frac", F.mean())
    if not (F[s] and F[g]): return None
    prev = -np.ones(F.shape, np.int64)
    flat = np.ravel_multi_index
    sh = F.shape
    q = deque([s]); prev[s] = flat(s, sh)
    found = False
    while q:
        cur = q.popleft()
        if cur == g: found = True; break
        t, i, j = cur
        for dt, di, dj in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
            n = (t+dt, i+di, j+dj)
            if 0 <= n[0] < sh[0] and 0 <= n[1] < sh[1] and 0 <= n[2] < sh[2] and F[n] and prev[n] < 0:
                prev[n] = flat(cur, sh); q.append(n)
    if not found: print("no path"); return None
    path = [g]; cur = g
    while cur != s:
        cur = tuple(int(x) for x in np.unravel_index(prev[cur], sh)); path.append(cur)
    path.reverse()
    return [(u0 + i * res, v0 + j * res, thetas[t]) for t, i, j in path]

def simplify(path, ok):
    """greedy shortcut: ok(a,b) says straight segment between configs is fine."""
    out = [path[0]]; i = 0
    while i < len(path) - 1:
        j = len(path) - 1
        while j > i + 1 and not ok(path[i], path[j]): j = (i + j) // 2 if j - i > 8 else j - 1
        out.append(path[j]); i = j
    return out
