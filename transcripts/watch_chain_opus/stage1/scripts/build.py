import sys, os, json, numpy as np
sys.path.insert(0,'tools'); import kernel as K, manifold3d as m3
MOD=0.2; PA=np.radians(25)
def P(a,d,base=(0,0)): return np.array(base,float)+d*np.array([np.cos(a),np.sin(a)])
T=P(0,10.8); M=P(1.8325957145940461,6,T); S1=P(2.443460952792061,10.8,M); S=P(3.6651914291880923,10.2,S1)
C=np.array([3.0,6.0])
# MW: 6.0 from M, farthest from S, within case
best=None
for a in np.radians(np.arange(0,360,5)):
    q=P(a,6.0,M)
    sc=min(np.linalg.norm(q-S)-5.4, 22.0-np.linalg.norm(q-C)-4.8, np.linalg.norm(q)-11.0)
    if best is None or sc>best[0]: best=(sc,q)
MW=best[1]; print('MW margin',best[0])
AX={'T':T,'minute':M,'S1':S1,'seconds':S,'MW':MW,'hour':M}
def inv(a): return np.tan(a)-a
def gear2d(N, phase, m=MOD):
    r=m*N/2; rb=r*np.cos(PA); ra=r+m; rf=r-1.25*m
    psi=(np.pi*m/2-0.03)/(2*r)
    rs=np.linspace(max(rb,rf),ra,12)
    ang=psi+inv(PA)-inv(np.arccos(np.clip(rb/rs,-1,1)))
    flank_r=list(rs); flank_a=list(ang)
    if rf<rb: flank_r=[rf]+flank_r; flank_a=[ang[0]]+flank_a
    pts=[]; pitch=2*np.pi/N
    for k in range(N):
        c=phase+k*pitch
        for rr,aa in zip(flank_r,flank_a): pts.append((rr,c-aa))
        tip=np.linspace(-ang[-1],ang[-1],4)[1:-1]
        for aa in tip: pts.append((ra,c+aa))
        for rr,aa in reversed(list(zip(flank_r,flank_a))): pts.append((rr,c+aa))
        a0=c+flank_a[0]; a1=c+pitch-flank_a[0]
        for aa in np.linspace(a0,a1,6)[1:-1]: pts.append((rf,aa))
    return [(rr*np.cos(aa),rr*np.sin(aa)) for rr,aa in pts]
def gear(N,phase,xy,z0,z1,hole=None):
    cs=m3.CrossSection([gear2d(N,phase)])
    g=m3.Manifold.extrude(cs,z1-z0).translate([xy[0],xy[1],z0])
    if hole: g=g-K.cyl_z(xy[0],xy[1],z0-1,z1+1,hole)
    return g
def hand(xy,z0,z1,L,w,ang,hub=0.9,hole=None):
    h=K.cyl_z(0,0,z0,z1,hub)+K.box([0,-w/2,z0],[L,w/2,z1])
    h=h.rotate([0,0,np.degrees(ang)]).translate([xy[0],xy[1],0])
    if hole: h=h-K.cyl_z(xy[0],xy[1],z0-1,z1+1,hole)
    return h
R=0.5; RH=0.55
# gear table: (mobile, part, N, z0,z1, hole)
G={}
def ang(a,b): d=np.array(b)-np.array(a); return np.arctan2(d[1],d[0])
meshes=[('barrel',96,(0,0),'T','t_pinion',12),('T',30,T,'minute','m_pinion',30),
        ('minute',96,M,'S1','s1_pinion',12),('S1',90,S1,'seconds','s_pinion',12),
        ('minute',15,M,'MW','mw_wheel',45),('MW',12,MW,'hour','h_wheel',48)]
phase={}
for dm,Nd,dxy,nm,npart,Nn in meshes:
    b=ang(dxy,AX[nm]); pd=2*np.pi/Nd
    u=b-0.0; u=u-np.round(u/pd)*pd
    phase[npart]=b+np.pi+u*Nd/Nn+np.pi/Nn
parts={}
# fixed
parts['bottom_plate']=K.cyl_z(C[0],C[1],-1.6,-0.1,22.8,256)-K.union([K.cyl_z(p[0],p[1],-1.1,0.0,RH) for p in [(0,0),T,M,S1,S]])
parts['barrel_bridge']=K.cyl_z(0,0,1.1,2.0,6.5,128)-K.cyl_z(0,0,1.0,1.7,RH)
parts['t_cock']=K.cyl_z(T[0],T[1],2.1,2.8,1.5)-K.cyl_z(T[0],T[1],2.0,2.7,RH)
parts['top_plate']=K.cyl_z(C[0],C[1],4.7,5.7,22.8,256)-K.union([K.cyl_z(M[0],M[1],4,6,RH),K.cyl_z(S[0],S[1],4,6,RH),
     K.cyl_z(S1[0],S1[1],4.6,5.1,RH),K.cyl_z(MW[0],MW[1],5.3,5.8,RH)])
parts['mw_cock']=K.cyl_z(MW[0],MW[1],7.6,8.4,1.5)-K.cyl_z(MW[0],MW[1],7.5,8.0,RH)
# T
parts['t_arbor']=K.cyl_z(T[0],T[1],-1.0,2.6,R)
parts['t_pinion']=gear(12,phase['t_pinion'],T,0,1.0)
parts['t_wheel']=gear(30,0,T,1.2,2.0)
# minute
parts['m_arbor']=K.cyl_z(M[0],M[1],-1.0,9.7,R)
parts['m_pinion']=gear(30,phase['m_pinion'],M,1.2,2.0)
parts['m_wheel']=gear(96,0,M,2.9,3.7)
parts['m_collar']=K.cyl_z(M[0],M[1],3.7,4.6,1.0)
parts['cannon_pinion']=gear(15,0,M,5.8,6.6)
parts['minute_hand']=hand(M,9.4,9.7,8.0,0.4,np.pi/2)
# S1
parts['s1_arbor']=K.cyl_z(S1[0],S1[1],-1.0,5.0,R)
parts['s1_pinion']=gear(12,phase['s1_pinion'],S1,2.9,3.7)
parts['s1_wheel']=gear(90,0,S1,3.8,4.6)
# seconds
parts['s_arbor']=K.cyl_z(S[0],S[1],-1.0,8.9,R)
parts['s_pinion']=gear(12,phase['s_pinion'],S,3.8,4.6)
parts['seconds_hand']=hand(S,8.5,8.9,5.5,0.3,np.pi/2,hub=0.7)
# MW
parts['mw_arbor']=K.cyl_z(MW[0],MW[1],5.4,7.9,R)
parts['mw_wheel']=gear(45,phase['mw_wheel'],MW,5.8,6.6)
parts['mw_pinion']=gear(12,0,MW,6.7,7.5)
# hour
parts['h_wheel']=gear(48,phase['h_wheel'],M,6.7,7.5,hole=RH)
parts['h_tube']=K.cyl_z(M[0],M[1],6.7,9.3,1.0)-K.cyl_z(M[0],M[1],6,10,RH)
parts['hour_hand']=hand(M,9.0,9.3,6.0,0.6,np.pi/2,hub=1.2,hole=RH)
os.makedirs('work/parts',exist_ok=True)
for f in os.listdir('work/parts'): os.remove('work/parts/'+f)
for n,p in parts.items():
    assert p.status()==m3.Error.NoError and len(p.decompose())==1, n
    K.write_stl('work/parts/%s.stl'%n,p)
mob={'T':['t_arbor','t_pinion','t_wheel'],
     'minute':['m_arbor','m_pinion','m_wheel','m_collar','cannon_pinion','minute_hand'],
     'S1':['s1_arbor','s1_pinion','s1_wheel'],'seconds':['s_arbor','s_pinion','seconds_hand'],
     'MW':['mw_arbor','mw_wheel','mw_pinion'],'hour':['h_wheel','h_tube','hour_hand']}
doc={'case_centre':[float(C[0]),float(C[1])],
     'fixed':['bottom_plate','barrel_bridge','t_cock','top_plate','mw_cock'],
     'mobiles':{k:{'axis':[float(AX[k][0]),float(AX[k][1])],'parts':v} for k,v in mob.items()},
     'meshes':[{'driver':d,'driver_teeth':Nd,'driven':n,'driven_teeth':Nn} for d,Nd,_,n,_,Nn in meshes],
     'hands':{'hour':{'mobile':'hour','part':'hour_hand'},'minute':{'mobile':'minute','part':'minute_hand'},
              'seconds':{'mobile':'seconds','part':'seconds_hand'}}}
json.dump(doc,open('work/movement.json','w'),indent=1)
print('ok',len(parts))
