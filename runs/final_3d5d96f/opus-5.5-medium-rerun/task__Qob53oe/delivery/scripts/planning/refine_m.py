import random, math, json, sys
import plan5
from plan5 import *
plan5.T2=float(sys.argv[4]); plan5.TA=float(sys.argv[5])
random.seed(int(sys.argv[2]))
p=json.load(open(sys.argv[1])); b,_=evaluate(p); print('start',b)
T=2.0
for it in range(15000):
    q=mutate(p,T); bq,_=evaluate(q)
    if bq<=b: p,b=q,bq
    if b==0: break
print(b); evaluate(p,True); json.dump(p,open(sys.argv[3],'w'))
