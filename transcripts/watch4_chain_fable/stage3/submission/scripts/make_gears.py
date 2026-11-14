"""Stage 3: replace the 50t/25t pair (ratio 2) by 45t/30t (ratio 1.5), module 0.25,
same centre distance 9.375, same z slab 2.4..3.4, same bores."""
from common import *
import math
import cadquery as cq

def involute_gear_pts(N, m, pa_deg=25.0, add=1.0, ded=1.25, backlash=0.03, phase=0.0, nfl=10):
    r = N * m / 2; rb = r * math.cos(math.radians(pa_deg)); ra = r + add * m; rf = r - ded * m
    inv = lambda a: math.tan(a) - a
    half = (math.pi * m / 2 - backlash) / (2 * r)          # half tooth angle on pitch circle
    pa = math.radians(pa_deg)
    pts = []
    r0 = max(rb, rf)
    for k in range(N):
        c = phase + 2 * math.pi * k / N
        fl = []
        for i in range(nfl + 1):
            rr = r0 + (ra - r0) * i / nfl
            al = math.acos(rb / rr)
            fl.append((rr, half + inv(pa) - inv(al)))       # angular half-width at radius rr
        right = [(rr, c - h) for rr, h in fl]
        left = [(rr, c + h) for rr, h in reversed(fl)]
        seq = []
        if rf < r0 - 1e-9:
            seq.append((rf, c - fl[0][1]))
        else:
            pass
        seq += right + left
        if rf < r0 - 1e-9:
            seq.append((rf, c + fl[0][1]))
        # root arc midpoint to next tooth
        seq.append((rf, c + math.pi / N))
        if rf >= r0 - 1e-9:
            pass
        pts += seq
    return [(rr * math.cos(a), rr * math.sin(a)) for rr, a in pts]

def gear(N, m, axis, z0, z1, bore, phase):
    pts = involute_gear_pts(N, m, phase=phase)
    w = cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1 - z0)
    w = w.cut(cq.Workplane('XY').workplane(offset=z0 - 1).circle(bore).extrude(z1 - z0 + 2))
    return w.translate((axis[0], axis[1], 0))

if __name__ == '__main__':
    mv = json.load(open(os.path.join(ROOT, 'previous/movement.json')))
    a = np.array(mv['mobiles']['intermediate']['axis']); b = np.array(mv['mobiles']['minute']['axis'])
    d = b - a; print('centre distance', np.hypot(*d))
    th = math.atan2(d[1], d[0])
    wheel = gear(45, 0.25, a, 2.4, 3.4, 0.5, th)                       # tooth towards minute axis
    pin = gear(30, 0.25, b, 2.4, 3.4, 1.0, th + math.pi + math.pi / 30) # gap towards intermediate axis
    kernel.write_step(os.path.join(ROOT, 'work/parts/intermediate_wheel_45t_m025.step'), wheel)
    kernel.write_step(os.path.join(ROOT, 'work/parts/minute_drive_pinion_30t_m025.step'), pin)
    for old in ('intermediate_wheel_50t_m025', 'minute_drive_pinion_25t_m025'):
        p = os.path.join(ROOT, 'work/parts', old + '.step')
        if os.path.exists(p): os.remove(p)
    mv['mobiles']['intermediate']['parts'] = ['intermediate_arbor', 'intermediate_pinion_24t_m020', 'intermediate_wheel_45t_m025']
    mp = mv['mobiles']['minute']['parts']
    mp[mp.index('minute_drive_pinion_25t_m025')] = 'minute_drive_pinion_30t_m025'
    for g in mv['meshes']:
        if g['driver'] == 'intermediate' and g['driven'] == 'minute':
            g['driver_teeth'], g['driven_teeth'] = 45, 30
    json.dump(mv, open(os.path.join(ROOT, 'work/movement.json'), 'w'), indent=1)
