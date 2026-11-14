# negative control: flip main_plate's approach to +z in a copy; the verifier logic must flag it
import sys,json,numpy as np
sys.path.insert(0,'scripts'); sys.path.insert(0,'tools')
import kernel
from block import P,mob
a=json.load(open('work/assembly.json'))
n='main_plate'; i=a['order'].index(n); bad=0
for T in a['paths'][n]:
    T=np.array(T); T[2,3]*=-1
    for b in a['order'][:i]:
        if kernel.ivol(kernel.apply(P[n],T),P[b])>0.01: bad+=1
print('collisions flagged on wrong-way path:',bad)
