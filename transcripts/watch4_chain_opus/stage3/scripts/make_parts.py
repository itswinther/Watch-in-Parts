import sys, math, json
sys.path.insert(0, 'tools'); sys.path.insert(0, 'scripts')
import kernel, gear
mv = json.load(open('work/movement.json'))
A = mv['mobiles']['third']['axis']; C = mv['mobiles']['centre']['axis']
ang_ac = math.degrees(math.atan2(C[1]-A[1], C[0]-A[0]))
ang_ca = ang_ac + 180
Z = 35; M = 0.2
print('dist', math.hypot(C[0]-A[0], C[1]-A[1]), 'needed', M*Z)
# a_wheel: tooth centred toward centre; m_pinion: gap centred toward third
aw = gear.gear_solid(Z, M, ang_ac, A[0], A[1], 1.2, 2.0)
mp = gear.gear_solid(Z, M, ang_ca + 180.0/Z, C[0], C[1], 1.2, 2.0)
kernel.write_step('work/parts/a_wheel.step', aw)
kernel.write_step('work/parts/m_pinion.step', mp)
