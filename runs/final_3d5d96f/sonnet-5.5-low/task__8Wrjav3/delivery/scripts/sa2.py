import sys, pickle, math, numpy as np, time
import layout as lo
from layout import *
seed=int(sys.argv[1]); r2=np.random.default_rng(seed+5000)
def energy(v,L):
    P=positions(v)
    if P is None: return 1e3,None
    return evaluate(P,L,pillars_for(P['C'])),P
def mut_layers(L): return mutate_layers(L,r2)
best=(1e9,)
t0=time.time()
while time.time()-t0<float(sys.argv[2]):
    L=sample_layers()
    if L is None: continue
    v=rand_v(); e,P=energy(v,L); T=1.5
    for it in range(6000):
        v2=list(v); L2=L
        if r2.random()<0.08: L2=mut_layers(L)
        else:
            k=int(r2.integers(0,len(v2)))
            if k in (4,7):
                if r2.random()<0.2: v2[k]=-v2[k]
            else:
                v2[k]=float(v2[k]+r2.normal(0,0.3 if r2.random()<0.5 else 0.04))
                if k==1: v2[k]=min(2.6,max(2.5,v2[k]))
        e2,P2=energy(v2,L2)
        if e2<e or r2.random()<math.exp(-(e2-e)/T):
            v,e,L=v2,e2,L2
        T=max(0.005,T*0.9985)
        if e<best[0]:
            best=(e,list(v),dict(L)); pickle.dump(best,open('sb_%d.pkl'%seed,'wb'))
        if e==0: break
    if best[0]==0: break
print(best[0])
