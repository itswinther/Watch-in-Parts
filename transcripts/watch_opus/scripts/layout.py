import numpy as np
rng=np.random.default_rng(0)
def P(r,a): return np.array([r*np.cos(a), r*np.sin(a)])
def encl(discs):
    # approximate min enclosing circle radius by grid on center
    best=(1e9,None)
    pts=np.array([d[0] for d in discs]); rs=np.array([d[1] for d in discs])
    c=pts.mean(0)
    for step in [2,1,0.5,0.25,0.1,0.05]:
        for _ in range(3):
            cands=[c+np.array([dx,dy])*step for dx in range(-4,5) for dy in range(-4,5)]
            vals=[(np.max(np.linalg.norm(pts-q,axis=1)+rs),tuple(q)) for q in cands]
            v,q=min(vals); c=np.array(q)
    return v,c
B=np.zeros(2)
best=(1e9,)
for it in range(20000):
    a,b,c,d=rng.uniform(0,2*np.pi,4)
    a=0.0
    S=B+P(10.8,a); C=S+P(9.6,b); T=C+P(9.0,c); M=C+P(6.0,d)
    n=np.linalg.norm
    if n(C-B)<11.4 or n(T-B)<18.4 or n(T-S)<10.0: continue
    if n(M-S)<5.9 or n(M-T)<5.9 or n(M-B)<6.6: continue
    v,cc=encl([(B,9.8),(S,5.0),(C,8.12),(T,8.17),(M,4.75)])
    if v<best[0]: best=(v,cc,S,C,T,M)
print(best)
