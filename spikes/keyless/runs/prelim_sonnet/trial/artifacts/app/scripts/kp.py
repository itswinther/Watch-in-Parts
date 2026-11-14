import sys,math
sys.path.insert(0,'/app/scripts')
from sim import *
w=World(); EPS=2e-4
P=w.body('pinion'); C=None
def kov(q,sa):
    return overlap(w.body('clutch',q=q,sa=sa),P)
for sgn,name in ((1,'backward(P locked)'),(-1,'forward(P locked)')):
    mx=0; blocked=0
    for st in range(1,121):
        sa=sgn*math.radians(3*st)
        ok=None
        for q in np.arange(0,0.3001,0.005):
            if kov(q,sa)<=EPS: ok=q;break
        if ok is None: blocked+=1
        else: mx=max(mx,ok)
    print(name,'max K lift',mx,'blocked steps',blocked)
