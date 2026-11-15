import numpy as np, sys
sys.path.insert(0,'/app/work')
from design import *
from cad import Shape
RP=0.5
def tip(g,build='8h'):
    zt,m=spec(g,build); return zt*m/2+m
def clearance(p,zr):
    d=9
    for g in GEARS:
        z0,z1=gz(g)
        if z1<=zr[0] or z0>=zr[1]: continue
        t=max(tip(g,'8h'),tip(g,'6h'))
        d=min(d,np.linalg.norm(p-POS[GEARS[g][0]])-t-RP)
    for mob,c in POS.items():
        d=min(d,np.linalg.norm(p-c)-(0.62 if mob in 'MH' else BODY)-RP)
    if zr[1]>0.5: d=min(d,np.linalg.norm(p)-1.0-RP)
    if zr[1]>2.27: d=min(d,np.linalg.norm(p)-0.8-RP)
    else: d=min(d,np.linalg.norm(p)-9.8-RP)
    d=min(d,12.6-RP-np.linalg.norm(p-CC))
    return d
def pick(zr,n,minclr=0.15):
    pts=[]
    for r in np.arange(4,12.2,0.1):
        for a in np.arange(0,360,1.0):
            p=CC+r*np.array([np.cos(np.radians(a)),np.sin(np.radians(a))])
            c=clearance(p,zr)
            if c>=minclr: pts.append((p,c))
    chosen=[]
    for _ in range(n):
        best=None
        for p,c in pts:
            sep=min([np.linalg.norm(p-q) for q in chosen]+[99])
            sc=min(sep,8)+c
            if best is None or sc>best[0]: best=(sc,p,c)
        chosen.append(best[1]); print('pillar',zr,np.round(best[1],3),'clr',round(best[2],3))
    return chosen
UP=None; LO=None
def pillars():
    global UP,LO
    if UP is None:
        UP=pick((0.70,2.60),4); LO=pick((-0.05,0.50),3)
    return UP,LO
INSIDE=['X','X2','Y','S','DM','Q','DH','T','H']
def plate():
    s=Shape(); s.cyl(CC[0],CC[1],12.6,-0.4545,-0.05)
    s.cyl(0,0,0.55,-0.6,0.1,cut=True)
    for m in ('A','A2'): s.cyl(*POS[m],0.30,-0.6,0.1,cut=True)
    up,lo=pillars()
    for p in lo: s.cyl(p[0],p[1],RP,-0.05,0.50)
    return s
def plate2():
    s=Shape(); s.cyl(CC[0],CC[1],12.6,0.50,0.70)
    s.cyl(0,0,1.05,0.4,0.8,cut=True)
    s.cyl(*POS['A'],1.55,0.4,0.8,cut=True); s.cyl(*POS['A2'],2.75,0.4,0.8,cut=True)
    for m in INSIDE: s.cyl(*POS[m],0.30,0.4,0.8,cut=True)
    up,lo=pillars()
    for p in up: s.cyl(p[0],p[1],RP,0.70,2.60)
    return s
def dial():
    s=Shape(); s.cyl(CC[0],CC[1],12.6,2.60,2.82); s.cyl(0,0,0.80,2.27,2.60); s.cyl(0,0,0.55,2.0,2.71,cut=True)
    s.cyl(*POS['M'],0.67,2.5,2.9,cut=True)
    for m in ('S','T'): s.cyl(*POS[m],0.31,2.5,2.9,cut=True)
    for m in ('A','A2','X','X2','Y','DM','Q','DH'): s.cyl(*POS[m],0.30,2.5,2.71,cut=True)
    return s
if __name__=="__main__": pillars()
