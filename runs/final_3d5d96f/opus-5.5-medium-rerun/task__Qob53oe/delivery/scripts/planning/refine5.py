import random, math, json, sys
from plan5 import *
random.seed(int(sys.argv[2]))
p=json.load(open(sys.argv[1])); b,_=evaluate(p); print('start',b)
T=3.0
for it in range(20000):
    q=mutate(p,T); bq,_=evaluate(q)
    if bq<=b: p,b=q,bq
    if b==0: break
print(b); evaluate(p,True); json.dump(p,open(sys.argv[3],'w'))
