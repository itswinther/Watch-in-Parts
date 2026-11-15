import sys, math, pickle, json, os
import numpy as np
import cadquery as cq
sys.path.insert(0,'/app/tools')
import kernel
import layout as LO
from layout import positions, pillars_for, G as GT
from gears import gear_polygon

TG=0.3
ZL={0:(0.0,0.4545455),1:(1.01,1.31),2:(1.39,1.69),3:(1.77,2.07),4:(2.15,2.45)}
P1Z=(-0.4545455,-0.06); P2Z=(0.53,0.93); P3Z=(2.53,2.83)
BOSSZ=2.28
JTOP=2.76
THICK0=2.48
JR=0.3; HOLE=0.34
PLATE_R=12.55
HAND_T=0.26
HL={'sec':(3.23,3.49),'min':(3.59,3.85),'hour':(3.95,4.21),'day':(4.31,4.57)}
M=0.2

def cyl(cx,cy,r,z0,z1):
    return cq.Workplane('XY').workplane(offset=z0).center(cx,cy).circle(r).extrude(z1-z0)
def gear(cx,cy,z,layer,phase):
    pts=[(cx+x,cy+y) for x,y in gear_polygon(z,M,phase)]
    z0,z1=ZL[layer]
    return cq.Workplane('XY').workplane(offset=z0).polyline(pts).close().extrude(z1-z0)
def U(*s):
    r=s[0]
    for x in s[1:]: r=r.union(x)
    return r

def mesh_phases(P,teeth,L):
    """phase for each gear key (mobile,gear)."""
    ph={}
    def pos(key): return P[key[0]]
    def free(k):
        if k not in ph: ph[k]=0.0
        return ph[k]
    # barrel -> M1.p
    pa=0.0; pitch_a=2*math.pi/96
    Pa=np.zeros(2); Pb=P['M1']; za=96; zb=teeth[('M1','p')]
    def drive(phi_a,za,Pa,Pb,zb):
        alpha=math.atan2(Pb[1]-Pa[1],Pb[0]-Pa[0])
        pa=2*math.pi/za; pb=2*math.pi/zb
        da=((alpha-phi_a)/pa)%1.0
        db=(0.5-da)%1.0
        return alpha+math.pi-db*pb
    ph[('M1','p')]=drive(0.0,96,Pa,Pb,zb)
    for a,b in LO.MESH:
        phi_a=free(a)
        ph[b]=drive(phi_a,teeth[a],P[a[0]],P[b[0]],teeth[b])
    for m,gs in teeth_by_mobile(teeth).items():
        for g in gs: free((m,g))
    return ph
def teeth_by_mobile(teeth):
    d={}
    for (m,g) in teeth: d.setdefault(m,[]).append(g)
    return d

def hand_solid(cx,cy,zb,zt,hole_r,hub_r,length,width=0.5):
    h=zt-zb
    base=(cq.Workplane('XY').workplane(offset=zb).center(cx,cy).circle(hub_r).extrude(h))
    bar=(cq.Workplane('XY').workplane(offset=zb).center(cx,cy+length/2-0.0).rect(width,length).extrude(h))
    s=base.union(bar)
    return s.cut(cyl(cx,cy,hole_r,zb-0.1,zt+0.1))

def build_all(v,Lyr,variant=False,pillar_pos=None):
    P=positions(v)
    teeth={(m,g):z for m,gs in GT.items() for g,z in gs.items()}
    if variant:
        teeth[('M1','w')]=18; teeth[('X','a')]=24
    else:
        teeth[('M1','w')]=21; teeth[('X','a')]=21
    ph=mesh_phases(P,teeth,Lyr)
    C=P['C']
    parts={}
    def g(m,gk): 
        x,y=P[m]; return gear(x,y,teeth[(m,gk)],Lyr[(m,gk)],ph[(m,gk)])
    # plain mobiles
    plain={'M1':['p','w'],'X':['a','b','s'],'Y':['c'],'A':['w','p'],'B':['w','p'],'J':['j'],'I':['a','b'],
           'S1':['p','w'],'S2':['p','w'],'S3':['p','w']}
    noup=LO.upper_flags(P,Lyr); nolow=LO.lower_flags(P,Lyr)
    for m,gks in plain.items():
        x,y=P[m]
        lg=min(Lyr[(m,gk)] for gk in gks)
        zlo=-0.35 if m=='M1' else (0.62 if m not in nolow else ZL[lg][0])
        hg=max(Lyr[(m,gk)] for gk in gks)
        ztop=JTOP if m not in noup else ZL[hg][1]
        s=cyl(x,y,JR,zlo,ztop)
        for gk in gks: s=s.union(g(m,gk))
        parts[m.lower()]=s
    # hand mobiles D, S
    for m,gk,lev in (('D','w','day'),('S','p','sec')):
        x,y=P[m]; zb,zt=HL[lev]
        lg=Lyr[(m,gk)]
        zl=0.62 if m not in nolow else ZL[lg][0]
        s=cyl(x,y,JR,zl,THICK0).union(cyl(x,y,0.55,THICK0,zb)).union(cyl(x,y,JR,zb-0.01,zt))
        s=s.union(g(m,gk))
        parts[{'D':'d_wheel','S':'s_wheel'}[m]]=s
    # minute tube (outer) and hour tube (inner)
    cx,cy=C
    zmb,zmt=HL['min']; zhb,zht=HL['hour']
    mt=cyl(cx,cy,0.92,ZL[2][0],2.47).union(cyl(cx,cy,1.05,2.46,zmb)).union(cyl(cx,cy,0.9,zmb-0.01,zmt))
    mt=mt.union(g('C','w')).union(g('C','k'))
    mt=mt.cut(cyl(cx,cy,0.66,0.5,5))
    parts['minute_tube']=mt
    ht=cyl(cx,cy,0.62,ZL[1][0],zhb).union(cyl(cx,cy,0.5,zhb-0.01,zht)).union(g('H','h'))
    ht=ht.cut(cyl(cx,cy,0.26,0.5,5))
    parts['hour_tube']=ht
    # hands
    parts['hour_hand']=hand_solid(cx,cy,zhb,zht,0.5,0.85,5.2)
    parts['minute_hand']=hand_solid(cx,cy,zmb,zmt,0.9,1.25,5.7)
    x,y=P['S']; zb,zt=HL['sec']; parts['s_hand']=hand_solid(x,y,zb,zt,JR,0.8,5.3)
    x,y=P['D']; zb,zt=HL['day']; parts['d_hand']=hand_solid(x,y,zb,zt,JR,0.8,3.3)
    # plates
    pil=pillar_pos if pillar_pos is not None else pillars_for(C)
    PR=0.55
    zt_=P3Z[0]
    p1=cyl(cx,cy,PLATE_R,*P1Z)
    for q in pil: p1=p1.union(cyl(q[0],q[1],PR,P1Z[1]-0.01,zt_))
    p1=p1.cut(cyl(0,0,0.54,P1Z[0]-0.1,P1Z[1]+0.1))
    x,y=P['M1']; p1=p1.cut(cyl(x,y,HOLE,P1Z[0]-0.1,P1Z[1]+0.1))
    parts['plate_lower']=p1
    p2=cyl(cx,cy,PLATE_R,*P2Z)
    sq=cq.Workplane('XY').workplane(offset=P2Z[0]-0.1).rect(1.46,1.46).extrude(P2Z[1]-P2Z[0]+0.2)
    p2=p2.cut(sq)
    x,y=P['M1']; p2=p2.cut(cyl(x,y,1.5,P2Z[0]-0.1,P2Z[1]+0.1))
    for m in ('X','Y','A','B','J','I','S1','S2','S3','D','S'):
        if m in nolow: continue
        x,y=P[m]; p2=p2.cut(cyl(x,y,HOLE,P2Z[0]-0.1,P2Z[1]+0.1))
    for q in pil: p2=p2.cut(cyl(q[0],q[1],PR,P2Z[0]-0.1,P2Z[1]+0.1))
    p2=p2.union(cyl(cx,cy,0.22,P2Z[1]-0.01,3.45))
    parts['plate_mid']=p2
    p3=cyl(cx,cy,PLATE_R,*P3Z).union(cyl(0,0,1.0,BOSSZ,P3Z[0]+0.01))
    p3=p3.cut(cyl(0,0,0.54,BOSSZ-0.1,P3Z[1]+0.1))
    for m in ('M1','X','Y','A','B','J','I','S1','S2','S3'):
        if m in noup: continue
        x,y=P[m]; p3=p3.cut(cyl(x,y,HOLE,P3Z[0]-0.1,P3Z[1]+0.1))
    for m in ('D','S'):
        x,y=P[m]; p3=p3.cut(cyl(x,y,0.59,P3Z[0]-0.1,P3Z[1]+0.1))
    p3=p3.cut(cyl(cx,cy,1.09,P3Z[0]-0.1,P3Z[1]+0.1))
    parts['plate_top']=p3
    return P,teeth,ph,parts,pil,(noup,nolow)
