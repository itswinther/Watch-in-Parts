"""Planar (x, y, heading) A* used only to author reference paths for Moving Day."""
import heapq
import math
import numpy as np
import manifold3d as m3


def air_2d(inst, height, extra_free=(), blocked=()):
    """Free floor area for a body `height` tall: every air box at least that high,
    plus extra free rectangles (outside the block), minus blocked footprints."""
    rects = [(a[0][0], a[0][1], a[1][0], a[1][1]) for a in inst.air.values() if a[1][2] >= height - 1e-9 and a[0][2] <= 1e-9]
    rects += list(extra_free)
    cs = m3.CrossSection()
    for x0, y0, x1, y1 in rects:
        cs = cs + m3.CrossSection.square([x1 - x0, y1 - y0]).translate([x0, y0])
    for poly in blocked:
        cs = cs - m3.CrossSection([np.asarray(poly)])
    return cs


def footprint(verts):
    """Convex hull of the projected vertices, as a CrossSection."""
    return m3.CrossSection.hull_points(np.asarray(verts)[:, :2])


def plan(foot, free, start, goal_test, goal_point, dx=3.5, dth=2.0, radius=100.0, weight=2.5, limit=3_000_000):
    """foot: CrossSection in the body's canonical pose. State (x, y, heading in degrees) places it
    at Rz(heading) then translate (x, y). Returns the list of states from start to a goal state."""
    def ok(s):
        f = foot.rotate(s[2]).translate([s[0], s[1]])
        return (f - free).area() < 1e-6

    def key(s):
        return (round((s[0] - start[0]) / dx), round((s[1] - start[1]) / dx), round((s[2] - start[2]) / dth))

    def h(s):
        return math.hypot(s[0] - goal_point[0], s[1] - goal_point[1])

    if not ok(start):
        raise RuntimeError("start state collides")
    rot_cost = math.radians(dth) * radius
    moves = [(dx, 0, 0, dx), (-dx, 0, 0, dx), (0, dx, 0, dx), (0, -dx, 0, dx),
             (dx, dx, 0, dx * 1.4142), (dx, -dx, 0, dx * 1.4142), (-dx, dx, 0, dx * 1.4142), (-dx, -dx, 0, dx * 1.4142),
             (0, 0, dth, rot_cost), (0, 0, -dth, rot_cost)]
    openq = [(weight * h(start), 0.0, start)]
    best = {key(start): 0.0}
    parent = {key(start): None}
    states = {key(start): start}
    n = 0
    while openq:
        f, g, s = heapq.heappop(openq)
        k = key(s)
        if g > best[k] + 1e-9:
            continue
        if goal_test(s):
            out = []
            while k is not None:
                out.append(states[k])
                k = parent[k]
            return out[::-1]
        n += 1
        if n > limit:
            raise RuntimeError("planner limit reached")
        for mx, my, mt, c in moves:
            t = (s[0] + mx, s[1] + my, s[2] + mt)
            kt = key(t)
            ng = g + c
            if kt in best and best[kt] <= ng + 1e-9:
                continue
            if not ok(t):
                best[kt] = -1.0          # blocked forever
                continue
            best[kt], parent[kt], states[kt] = ng, k, t
            heapq.heappush(openq, (ng + weight * h(t), ng, t))
    raise RuntimeError("no path")
