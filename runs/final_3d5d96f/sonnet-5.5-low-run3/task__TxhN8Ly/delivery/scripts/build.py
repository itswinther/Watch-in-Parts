import sys, os, math, json, numpy as np
sys.path.insert(0,'/app/tools')
import cadquery as cq, kernel
from geom import *
OUT='/app/delivery/parts'
os.makedirs(OUT,exist_ok=True)
def cyl(cx,cy,z0,z1,r): return cq.Workplane("XY").workplane(offset=z0).center(cx+OFF[0],cy+OFF[1]).circle(r).extrude(z1-z0)
def gear(z,m,rho,pos,zr,bore=None):
    pts=[(x+pos[0]+OFF[0],y+pos[1]+OFF[1]) for x,y in profile(z,m,rho,tfrac=0.425)]
    g=cq.Workplane("XY").workplane(offset=zr[0]).polyline(pts).close().extrude(zr[1]-zr[0])
    return g
def uni(*s):
    r=s[0]
    for x in s[1:]: r=r.union(x)
    return r
def save(name,shape):
    shape=shape.clean() if hasattr(shape,'clean') else shape
    kernel.write_step(f'{OUT}/{name}.step',shape)
def ang(a,b): return math.atan2(b[1]-a[1],b[0]-a[0])
def rho_mesh(z1,m,rho1,p1,z2,p2): return mesh_rho(z1,m,rho1,z2,ang(p1,p2))
ZL=lambda l:LAYERS[l]
PIV=(2.30,2.5955)   # bottom pivot z range
def tshaft(pos,top,pivtop=True,rbody=0.45):
    s=[cyl(*pos,PIV[0],PIV[1],0.3),cyl(*pos,PIV[1],top,rbody)]
    if pivtop: s.append(cyl(*pos,top,4.05,0.3))
    return s
def build(variant6=False):
    parts={}
    # --- I ---
    mcd=M['cd6'] if variant6 else M['cd']; zc=T['c6'] if variant6 else T['c']; zd=T['d6'] if variant6 else T['d']
    rho_a=rho_mesh(96,0.2,0.0,POS['B'],12,I)
    sh=[cyl(*I,-0.40,-0.05,0.3),cyl(*I,-0.05,3.26,0.5),cyl(*I,3.26,3.85,0.4),cyl(*I,3.85,4.05,0.3),
        gear(12,0.2,rho_a,I,DRUM)]
    parts['I_shaft']=uni(*sh)
    # I.c with bore 0.4 at layer C
    LC=ZL(CL['d'])
    ic=gear(zc,mcd,0.0,I,LC).cut(cyl(*I,LC[0]-1,LC[1]+1,0.4))
    parts['I_c6' if variant6 else 'I_c']=ic
    # --- M ---
    rho_din=rho_mesh(zc,mcd,0.0,I,zd,C)
    ZA,ZB_,ZC=ZL(CL['dd']),ZL(CL['p']),ZL(CL['d'])
    ms=[cyl(*C,2.30,2.62,0.7),cyl(*C,2.62,2.94,0.6),cyl(*C,2.94,3.26,0.5),cyl(*C,3.26,5.05,0.4),cyl(*C,5.05,5.30,0.3)]
    parts['M_shaft']=uni(*ms)
    parts['M_dd']=gear(36,M['dd'],0.0,C,ZA).cut(cyl(*C,0,9,0.6))
    parts['M_p']=gear(14,M['pq'],0.0,C,ZB_).cut(cyl(*C,0,9,0.5))
    parts['M_din6' if variant6 else 'M_din']=gear(zd,mcd,rho_din,C,ZC).cut(cyl(*C,0,9,0.4))
    # --- X1 ---
    r_f1=rho_mesh(36,M['dd'],0.0,C,12,X1)
    parts['X1']=uni(*tshaft(X1,ZL(Lg1)[1],False),gear(12,M['dd'],r_f1,X1,ZA),gear(36,M['g1'],0.0,X1,ZL(Lg1)))
    # --- X2 ---
    r_f2=rho_mesh(36,M['g1'],0.0,X1,12,X2)
    parts['X2']=uni(*tshaft(X2,ZL(Lg2)[1],False),gear(12,M['g1'],r_f2,X2,ZL(Lg1)),gear(30,M['g2'],0.0,X2,ZL(Lg2)))
    # --- X3 ---
    r_f3=rho_mesh(30,M['g2'],0.0,X2,12,X3)
    parts['X3']=uni(*tshaft(X3,3.85,True),gear(12,M['g2'],r_f3,X3,ZL(Lg2)),gear(32,M['g3'],0.0,X3,ZL(Lg3)))
    # --- S ---
    r_h=rho_mesh(32,M['g3'],0.0,X3,12,S)
    parts['S_shaft']=uni(cyl(*S,*PIV,0.3),cyl(*S,PIV[1],4.45,0.45),cyl(*S,4.45,4.70,0.3),gear(12,M['g3'],r_h,S,ZL(Lg3)))
    # --- J ---
    r_q=rho_mesh(14,M['pq'],0.0,C,42,J)
    parts['J']=uni(*tshaft(J,3.85,True),gear(42,M['pq'],r_q,J,ZB_),gear(12,M['rs'],0.0,J,ZL(CL['s'])))
    # --- H ---
    r_s=rho_mesh(12,M['rs'],0.0,J,48,C)
    ZD=ZL(CL['s'])
    ht=uni(cyl(*C,ZD[0],4.75,0.8),cyl(*C,4.75,5.00,0.7),gear(48,M['rs'],r_s,C,ZD)).cut(cyl(*C,0,9,0.45))
    parts['H_tube']=ht
    # --- K ---
    r_k1=rho_mesh(48,M['rs'],r_s,C,24,K)
    parts['K']=uni(*tshaft(K,3.85,True),gear(24,M['sk'],r_k1,K,ZD),gear(12,M['kw'],0.0,K,ZL(Lk)))
    # --- D ---
    r_w=rho_mesh(12,M['kw'],0.0,K,48,DD)
    parts['D_shaft']=uni(cyl(*DD,*PIV,0.3),cyl(*DD,PIV[1],4.45,0.45),cyl(*DD,4.45,4.70,0.3),gear(48,M['kw'],r_w,DD,ZL(Lk)))
    return parts
def hand(pos,zr,bore,hub,L,w=0.4,theta=math.pi/2):
    c=cyl(*pos,zr[0],zr[1],hub)
    x0=hub*0.5; dx,dy=math.cos(theta),math.sin(theta); nx,ny=-dy*w/2,dx*w/2
    q0=pos[0]+OFF[0];q1=pos[1]+OFF[1]
    P=[(q0+dx*x0+nx,q1+dy*x0+ny),(q0+dx*L+nx,q1+dy*L+ny),(q0+dx*L-nx,q1+dy*L-ny),(q0+dx*x0-nx,q1+dy*x0-ny)]
    arm=cq.Workplane("XY").workplane(offset=zr[0]).polyline(P).close().extrude(zr[1]-zr[0])
    return c.union(arm).cut(cyl(*pos,zr[0]-1,zr[1]+1,bore))
def plates(posts,pillars):
    R=12.55
    # PL
    pl=cyl(0,0,PL[0],PL[1],R)
    for pos,r in ((POS['B'],0.55),(I,0.36)): pl=pl.cut(cyl(*pos,-1,1,r))
    for p in pillars: pl=pl.union(cyl(*p,PL[1],MP[0],0.6))
    mp=cyl(0,0,MP[0],MP[1],R)
    holes=[(POS['B'],0.56),(I,0.56),(C,0.76)]+[(POS[k],0.36) for k in ('X1','X2','X3','S','J','K','D')]
    for pos,r in holes: mp=mp.cut(cyl(*pos,0,9,r))
    for p in posts: mp=mp.union(cyl(*p,MP[1],TP[0],0.5))
    tp=cyl(0,0,TP[0],TP[1],R)
    holes=[(I,0.36),(POS['X3'],0.36),(POS['J'],0.36),(POS['K'],0.36),(POS['S'],0.51),(POS['D'],0.51),(C,0.86)]
    for pos,r in holes: tp=tp.cut(cyl(*pos,0,9,r))
    return pl,mp,tp
