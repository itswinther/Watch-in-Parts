import numpy as np, sys, json
sys.path.insert(0,'/app/work')
from layout import POS, Z, TH, CC
from gear import mesh_phase
from cad import Shape
BAR=np.zeros(2)
# gear spec: name -> (mobile, group or z-range, teeth8, teeth6, module8, module6)
GEARS={
 'pA':('A',(0.0,0.4545),12,12,0.2,0.2),
 'wA':('A','g3',48,45,1/6,1/6),
 'pX':('X','g3',12,15,1/6,1/6),
 'pX2':('X2','g3',12,15,1/6,1/6),
 'xs':('X','g5',45,45,0.15,0.15),
 'y1':('Y','g5',12,12,0.15,0.15),
 'y2':('Y','g6',48,48,0.15,0.15),
 'pS':('S','g6',12,12,0.15,0.15),
 'x2m':('X2','g4',12,12,0.15,0.15),
 'dm1':('DM','g4',24,24,0.15,0.15),
 'dm2':('DM','g2',12,12,0.15,0.15),
 'gM':('M','g2',24,24,0.15,0.15),
 'pA2':('A2',(0.0,0.4545),24,24,0.2,0.2),
 'aq':('A2','g7',15,12,0.15,0.15),
 'q1':('Q','g7',45,48,0.15,0.15),
 'q2':('Q','g8',12,12,0.25,0.25),
 'dh1':('DH','g8',24,24,0.25,0.25),
 'dh':('DH','g1',12,12,0.3,0.3),
 'gH':('H','g1',12,12,0.3,0.3),
 'gT':('T','g1',24,24,0.3,0.3),
}
# meshes in tree order: (driver gear, driven gear)
MESHES=[('drum','pA'),('drum','pA2'),('wA','pX'),('wA','pX2'),('xs','y1'),('y2','pS'),('x2m','dm1'),('dm2','gM'),
        ('aq','q1'),('q2','dh1'),('dh','gH'),('dh','gT')]
MOBILE_NAMES={'A':'a_wheel','X':'x_wheel','X2':'x2_wheel','Y':'y_wheel','S':'seconds_wheel','DM':'dm_wheel','M':'minute_wheel',
  'A2':'a2_wheel','Q':'q_wheel','DH':'dh_wheel','H':'hour_wheel','T':'day_wheel'}
VARIES={'A','X','X2','A2','Q'}     # mobiles whose body differs between the builds
HAND_Z={'minute':(2.87,3.09),'hour':(3.14,3.36),'seconds':(3.41,3.63),'day':(2.87,3.09)}
def gz(g):
    s=GEARS[g][1]
    return s if isinstance(s,tuple) else (Z[s],Z[s]+TH[s])
def spec(g,build):
    mob,_,z8,z6,m8,m6=GEARS[g]
    return (z8,m8) if build=='8h' else (z6,m6)
def phases(build):
    ph={'drum':0.0}
    pos=dict(POS); 
    for drv,dn in MESHES:
        if drv=='drum': zd,md,cd=96,0.2,BAR
        else:
            zd,md=spec(drv,build); cd=POS[GEARS[drv][0]]
            ph.setdefault(drv,0.0)
        zn,mn=spec(dn,build); assert abs(mn-md)<1e-9,(drv,dn)
        ph[dn]=mesh_phase(zd,md,ph[drv],cd,zn,POS[GEARS[dn][0]])
    return ph
def speeds(build):
    nB=1/8 if build=='8h' else 1/6
    n={'barrel':-nB}   # ccw positive; barrel turns clockwise
    mob=lambda g:'barrel' if g=='drum' else GEARS[g][0]
    for drv,dn in MESHES:
        zd=96 if drv=='drum' else spec(drv,build)[0]; zn=spec(dn,build)[0]
        n[mob(dn)]=-n[mob(drv)]*zd/zn
    return n   # turns per hour, ccw positive
# ---------------- mobile bodies -----------------
PIV=0.25; BODY=0.35
def body(mob,build):
    x,y=POS[mob]; s=Shape(); ph=phases(build)
    gears=[g for g in GEARS if GEARS[g][0]==mob]
    for g in gears:
        z0,z1=gz(g); zt,m=spec(g,build); s.gear(x,y,zt,m,ph[g],z0,z1)
    if mob in('A','A2'):
        s.cyl(x,y,PIV,-0.43,0.0); s.cyl(x,y,BODY,0.0,2.56); s.cyl(x,y,PIV,2.56,2.68)
    elif mob=='H':
        s.cyl(x,y,PIV,0.53,0.74); s.cyl(x,y,0.25,0.74,3.14); s.cyl(x,y,0.40,2.11,2.23); s.cyl(x,y,0.17,3.14,3.36)
    elif mob=='M':
        s.cyl(x,y,0.62,2.55,2.87); s.cyl(x,y,0.52,2.87,3.09)
        s.cyl(x,y,0.30,2.20,3.20,cut=True)
    else:
        s.cyl(x,y,PIV,0.53,0.74); s.cyl(x,y,BODY,0.74,2.56)
        if mob=='S': s.cyl(x,y,0.26,2.56,3.41); s.cyl(x,y,0.18,3.41,3.63)
        elif mob=='T': s.cyl(x,y,0.26,2.56,2.87); s.cyl(x,y,0.18,2.87,3.09)
        else: s.cyl(x,y,PIV,2.56,2.68)
    return s
# ---------------- hands -----------------
def hand(kind):
    mob={'minute':'M','hour':'H','seconds':'S','day':'T'}[kind]
    x,y=POS[mob]; z0,z1=HAND_Z[kind]
    hole={'minute':0.52,'hour':0.17,'seconds':0.18,'day':0.18}[kind]
    hub={'minute':0.80,'hour':0.42,'seconds':0.42,'day':0.42}[kind]
    L={'minute':5.05,'hour':5.05,'seconds':5.05,'day':3.05}[kind]
    tail={'minute':0.0,'hour':0.0,'seconds':1.2,'day':0.0}[kind]
    ang=np.radians({'minute':60,'hour':300,'seconds':135,'day':200}[kind])
    w0,w1=0.46,0.26
    u=np.array([np.cos(ang),np.sin(ang)]); v=np.array([-u[1],u[0]])
    c=np.array([x,y])
    pts=[c-u*tail+v*w0/2, c+u*(L-0.12)+v*w1/2, c+u*L, c+u*(L-0.12)-v*w1/2, c-u*tail-v*w0/2]
    s=Shape(); s.poly(np.array(pts),z0,z1); s.cyl(x,y,hub,z0,z1); s.cyl(x,y,hole,z0-0.1,z1+0.1,cut=True)
    return s
