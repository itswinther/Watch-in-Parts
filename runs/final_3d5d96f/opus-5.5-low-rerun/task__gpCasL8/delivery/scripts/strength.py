import sys,re,numpy as np
sys.path.insert(0,'/app/work')
from design import *
txt=open('/app/datasheets/DS-W04_gear_rating.md').read()
Y={}
for line in txt.splitlines():
    m=re.match(r'\| (\d+) \|(.*)\|$',line)
    if m:
        base=int(m.group(1));vals=[v.strip() for v in m.group(2).split('|')]
        for i,v in enumerate(vals):
            if v not in('–',''): Y[base+i]=float(v)
TMAX=70.1
for b in ('8h','6h'):
    n=speeds(b); nB=abs(n['barrel'])
    print(b)
    for drv,dn in MESHES:
        if drv=='drum': zd,md,bd,mobd=96,0.2,(0,0.4545),'barrel'
        else: zd,md=spec(drv,b); bd=gz(drv); mobd=GEARS[drv][0]
        zn,mn=spec(dn,b); bn=gz(dn)
        face=min(bd[1],bn[1])-max(bd[0],bn[0])
        Td=TMAX*nB/abs(n[mobd]); W=Td/(zd*md/2)
        sd=W/(face*md*Y[zd]); sn=W/(face*mn*Y[zn])
        print('  %-5s->%-5s T=%7.2f W=%6.2f b=%.3f sig_drv=%6.0f sig_dn=%6.0f'%(drv,dn,Td,W,face,sd,sn))
