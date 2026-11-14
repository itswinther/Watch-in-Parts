"""Reference plan for Moving Day instance flat-1.
    python solution/reference_md.py OUT_DIR      writes OUT_DIR/plan.json
Uses only what the agent can see (geometry.md) plus a small planar planner."""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
import numpy as np
from geometry import md, core
from geometry.md import rot, trans
import planar

OUTSIDE = (-600, 300, 0, 900)          # free floor outside the front wall: x0, y0, x1, y1
STEP = 4.0


def verts_at(body, T):
    return core.verts(core.apply(body, T))


def lerp_move(T, d, step=STEP):
    """Poses translating pose T by vector d, excluding T itself."""
    n = max(1, int(math.ceil(np.linalg.norm(d) / step)))
    return [trans(np.array(d) * i / n) @ T for i in range(1, n + 1)]


def about_line(axis, point, deg):
    return trans(point) @ rot(axis, deg) @ trans(-np.array(point))


def swing(body, T, axis, point, total_deg, limit=4.5):
    """Poses rotating pose T about a world line, excluding T itself, with every vertex step under `limit`."""
    V = verts_at(body, T) - np.array(point)
    k = {"x": 0, "y": 1, "z": 2}[axis]
    r = np.sqrt((np.delete(V, k, axis=1) ** 2).sum(axis=1)).max()
    n = max(1, int(math.ceil(abs(math.radians(total_deg)) * r / limit)))
    return [about_line(axis, point, total_deg * i / n) @ T for i in range(1, n + 1)]


def planar_poses(C, states):
    return [trans((s[0], s[1], 0)) @ rot("z", s[2]) @ C for s in states]


def canonical(body, T):
    """Split pose T into a planar state and a canonical pose C with its footprint centred on the origin."""
    V = verts_at(body, T)
    c = (V[:, :2].min(axis=0) + V[:, :2].max(axis=0)) / 2
    C = trans((-c[0], -c[1], 0)) @ T
    return C, (float(c[0]), float(c[1]), 0.0)


def in_staging(inst, foot, s, margin=3.0):
    f = foot.rotate(s[2]).translate([s[0], s[1]])
    x0, y0, x1, y1 = f.bounds()
    return x1 < inst.staging[1][0] - margin and x0 > inst.staging[0][0] + margin and y0 > inst.staging[0][1] + margin and y1 < inst.staging[1][1] - margin


def sofa_path(inst, placed_polys=()):
    body = inst.piece("sofa")
    final = inst.final("sofa")
    # 1. final (flat) -> standing on end, about the floor edge x = 520
    pivot = (final[0, 3], 0.0, 0.0)
    up = swing(body, final, "y", pivot, -90.0)
    E = up[-1]
    # 2. standing: walk back to the east corridor, footprint long side along x
    C, s0 = canonical(body, E)
    foot = planar.footprint(verts_at(body, C))
    free = planar.air_2d(inst, 240.0, blocked=placed_polys)
    apartment = inst.apartment()

    def tip_from(state):
        """Poses from standing at `state` to lying on the back, or None if they do not fit."""
        T0 = planar_poses(C, [state])[0]
        V = verts_at(body, T0)
        for px in (V[:, 0].min(), V[:, 0].max()):
            for deg in (90.0, -90.0):
                poses = swing(body, T0, "y", (px, 0, 0), deg)
                zs = [verts_at(body, Q)[:, 2] for Q in poses]
                if min(z.min() for z in zs) < -1e-6 or zs[-1].max() > 161:
                    continue
                if all(core.ivol(core.apply(body, Q), apartment) <= 1e-6 for Q in poses[::4] + [poses[-1]]):
                    return poses
        return None

    tip, spot = None, None
    for heading in (90.0, 270.0):
        for xc in range(400, 600, 10):
            st = (float(xc), 673.0, heading)          # footprint y 633..713, inside the door band
            if (foot.rotate(st[2]).translate([st[0], st[1]]) - free).area() > 1e-6:
                continue
            tip = tip_from(st)
            if tip:
                spot = st
                break
        if tip:
            break
    if tip is None:
        raise RuntimeError("no place to tip the sofa")
    goal = lambda s: abs(((s[2] - spot[2]) + 180) % 360 - 180) < 1e-6 and abs(s[0] - spot[0]) <= 2.0 and abs(s[1] - spot[1]) <= 2.0
    walk = planar.plan(foot, free, s0, goal, spot[:2], radius=90.0)
    walk_poses = planar_poses(C, walk)
    T = walk_poses[-1]
    shift = lerp_move(T, (spot[0] - walk[-1][0], spot[1] - walk[-1][1], 0))
    best = tip
    T = best[-1]
    # 4. straight out west through the door to staging
    V = verts_at(body, T)
    out = lerp_move(T, (-(V[:, 0].max() + 60.0), 0, 0))
    seq = [final] + up + walk_poses[1:] + shift + best + out
    return seq[::-1]


def wardrobe_path(inst, placed_polys=()):
    body = inst.piece("wardrobe")
    final = inst.final("wardrobe")
    down = swing(body, final, "y", (70.0, 0, 0), 90.0)
    L = down[-1]
    C, s0 = canonical(body, L)
    foot = planar.footprint(verts_at(body, C))
    free = planar.air_2d(inst, 46.0, extra_free=[OUTSIDE], blocked=placed_polys)
    goal = lambda s: planar_in_staging(inst, foot, s)
    carry = planar.plan(foot, free, s0, goal, (-200, 670), radius=120.0)
    seq = [final] + down + planar_poses(C, carry)[1:]
    return seq[::-1]


def planar_in_staging(inst, foot, s):
    return in_staging(inst, foot, s)


def box_path(inst, name, waypoints):
    """Pure translations: final pose, then offsets (dx, dy) walked back to staging."""
    final = inst.final(name)
    seq, T = [final], final
    for d in waypoints:
        mv = lerp_move(T, (d[0], d[1], 0))
        seq += mv
        T = mv[-1]
    return seq[::-1]


def build(inst):
    paths = {}
    paths["sofa"] = sofa_path(inst)
    paths["bookcase"] = box_path(inst, "bookcase", [(0, 38, 0), (-(500 + 60), 0, 0)])
    paths["wardrobe"] = wardrobe_path(inst)
    paths["chest"] = box_path(inst, "chest", [(0, 240, 0), (-(143 + 60), 0, 0)])
    return {"order": ["sofa", "bookcase", "wardrobe", "chest"], "paths": paths}


def main(out):
    inst = md.flat_one()
    plan = build(inst)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "plan.json"), "w") as f:
        json.dump({"order": plan["order"], "paths": {k: [np.asarray(T).tolist() for T in v] for k, v in plan["paths"].items()}}, f)
    print("poses", {k: len(v) for k, v in plan["paths"].items()})


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "out")
