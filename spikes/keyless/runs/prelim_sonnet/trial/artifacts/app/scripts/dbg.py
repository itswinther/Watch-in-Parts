import sys,math
sys.path.insert(0,'/app/scripts')
from sim import *
w=World()
for pa in (-1.0,-3.0):
    w.q['pinion']=math.radians(pa)
    P=w.body('pinion')
    print('P rot',pa)
    for d in np.arange(-3,3.01,0.5):
        W=w.body('crown_wheel',q=math.radians(d))
        print(' W',d,round(overlap(P,W),5))
