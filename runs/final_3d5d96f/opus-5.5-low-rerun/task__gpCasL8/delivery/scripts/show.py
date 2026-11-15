from opt import *
import json,sys
p=json.loads(sys.argv[1]);signs=json.loads(sys.argv[2])
P=build2(p,signs)
for k,v in P.items(): print(k,np.round(v,2),round(np.linalg.norm(v),2))
for g,mo,r,mate in G:
    c=P[mo]
    e=12.6-(np.linalg.norm(c)+r)
    if e<0.05: print('case',g,e)
    for m2,c2 in P.items():
        if m2==mo or (mo in CEN and m2 in CEN): continue
        if g in('gM','gH') and m2 in CEN: continue
        ar=0.65 if m2 in CEN else 0.4
        d=np.linalg.norm(c-c2)-r-ar
        if d<0.05: print('cover',g,m2,round(d,2))
    if mo not in CEN and g not in('pA','pA2'):
        d=np.linalg.norm(c-B)-r-1.0
        if d<0.05: print('post',g,round(d,2))
