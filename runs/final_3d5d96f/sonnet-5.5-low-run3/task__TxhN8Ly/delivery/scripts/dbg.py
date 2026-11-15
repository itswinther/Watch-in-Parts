import json,sys,random
from layout2 import *
import layout2
def detail(ang,cl,lay):
    g,S,Dm=build(ang,cl,lay)
    out=[]
    for gi in g: out.append((12.45-(np.linalg.norm(gi[1])+gi[2]),'case',gi[4]))
    out.append((7.0-np.linalg.norm(S),'S'));dn=np.linalg.norm(Dm);out.append((dn-6.4,'Dmin'));out.append((9-dn,'Dmax'))
    for i in range(len(g)):
        for j in range(i+1,len(g)):
            a,b=g[i],g[j]
            if a[0]==b[0]: continue
            if a[3]==b[3] and not meshed(a[4],b[4]): out.append((np.linalg.norm(a[1]-b[1])-a[2]-b[2]-0.15,'same',a[4],b[4]))
    mobs={}
    for gi in g: mobs.setdefault(gi[0],[]).append(gi)
    for mob,gl in mobs.items():
        top=3 if mob in CENT or mob=='I' else max(LI[x[3]] for x in gl)
        r=0.95 if mob in CENT else 0.5
        for gi in g:
            if gi[0]==mob or (gi[0] in CENT and mob in CENT): continue
            if LI[gi[3]]<=top:
                if gi[3] in [x[3] for x in gl] and any(meshed(gi[4],x[4]) for x in gl if x[3]==gi[3]): continue
                out.append((np.linalg.norm(gl[0][1]-gi[1])-gi[2]-r-0.12,'col',mob,gi[4]))
    out.sort(key=lambda t:t[0]); return out[:8]
pass
