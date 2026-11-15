import random, math, json, sys
from plan5 import *
random.seed(int(sys.argv[1]))
best=None
for restart in range(6):
    p=rand_p(); b,_=evaluate(p)
    while b>=1e9: p=rand_p(); b,_=evaluate(p)
    T=30.0
    for it in range(5000):
        q=mutate(p,T); bq,_=evaluate(q)
        if bq<=b or random.random()<math.exp(-(bq-b)/max(1e-3,T/30)): p,b=q,bq
        T=max(0.3,T*0.999)
        if b==0: break
    if best is None or b<best[0]: best=(b,p)
    if b==0: break
b,p=best; print(b); print(json.dumps(p)); evaluate(p,True)
json.dump(p,open('q5_%s.json'%sys.argv[1],'w'))
