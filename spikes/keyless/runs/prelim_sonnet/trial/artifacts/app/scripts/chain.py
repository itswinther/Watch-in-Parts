import sys,math,numpy as np
sys.path.insert(0,'/app/scripts')
from sim import *
w=World()
EPS=2e-4
def others(n,exclude=()):
    return [k for k in list(w.mob)+w.fixed if k!=n and k not in exclude]
cache_f={f:w.parts[f] for f in w.fixed}
def B(n,q=None,**kw):
    return w.body(n,q=q,**kw)
def ovl(n,q,bodies):
    m=B(n,q=q)
    return max([overlap(m,b) for b in bodies]+[0])
def resolve(n,bodies,maxd,step=0.05):
    """minimal displacement of mobile n (rot in deg) that clears overlap>EPS; returns delta or None"""
    q0=w.q[n]
    if ovl(n,q0,bodies)<=EPS: return 0.0
    d=0
    while d<maxd:
        d+=step
        for s in (1,-1):
            q=q0+s*math.radians(d)
            if ovl(n,q,bodies)<=EPS: return s*d
    return None
# chain: P (rotated), W, barrel
def state_bodies():
    return {n:B(n) for n in w.mob}
w.q['pinion']=0
tot=0
out=[]
for step in range(0,60):
    w.q['pinion']-=math.radians(3)
    cur={n:B(n) for n in ['pinion','crown_wheel','barrel','setting_wheel','minute_wheel']}
    fx=[cache_f[f] for f in w.fixed]
    for it in range(3):
        for n in ['crown_wheel','barrel']:
            bs=[cur[k] for k in (['pinion'] if n=='crown_wheel' else ['crown_wheel'])]+fx
            d=resolve(n,bs,8.0)
            if d is None: print('JAM',n,'step',step); break
            if d!=0:
                w.q[n]+=math.radians(d); cur[n]=B(n)
    if step%6==5: print(step,'pinion',round(math.degrees(w.q['pinion']),1),'W',round(math.degrees(w.q['crown_wheel']),2),'barrel',round(math.degrees(w.q['barrel']),2),flush=True)
