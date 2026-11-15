import sys, os, json, math
sys.path.insert(0,'/app/tools'); sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cadquery as cq, kernel, gears
OUT='/app/delivery'; PD=OUT+'/parts'
C=np.array([2.8,0.]); O=np.zeros(2)
def inter(p1,r1,p2,r2,s):
    d=np.linalg.norm(p2-p1); a=(r1**2-r2**2+d**2)/(2*d); h=math.sqrt(r1**2-a**2)
    u=(p2-p1)/d; v=np.array([-u[1],u[0]]); return p1+a*u+s*h*v
def pol(c,r,a): return c+r*np.array([math.cos(a),math.sin(a)])
I8=inter(O,10.5,C,8.4,1); I6=inter(O,10.8,C,8.4,1)
T=pol(C,5.4,-1.6231562043547265); M=pol(C,3.0,-2.8797932657906435)
S=inter(T,5.1,C,6.2,-1); D=inter(M,5.25,C,7.5,1)
POS=dict(C=C,I8=I8,I6=I6,T=T,M=M,S=S,D=D,H=C)
# z levels
Z=dict(P=(-0.4545,-0.04), MP=(0.4945,0.6945), UP=(2.2673,2.5455), MB=(2.8255,3.0255), DIAL=(3.5455,3.7455),
       LOW=(0.7345,0.9345), L1=(2.5855,2.7855), L2=(3.0655,3.2655), L3=(3.3055,3.5055),
       H1=(3.7855,3.9855), H2=(4.0255,4.2255), H3=(4.2655,4.4655), DRUM=(0.0,0.4545))
RP=12.65  # plate radius about C
THIN=0.035
# gear definitions: (z, m, s or None)
G=dict(a8=(9,0.2,0.274), a6=(12,0.2,0.274), b=(48,0.15,None), c=(64,0.15,None), pt=(8,0.15,None),
       wt=(60,0.15,None), ps=(8,0.15,None), cp=(8,0.15,None), Mw=(32,0.15,None), Mp=(8,0.1875,None),
       H=(24,0.1875,None), Dw=(48,0.1875,None))
_cache={}
def gcs(key):
    if key not in _cache:
        z,m,s=G[key]; _cache[key]=gears.gear_cs(z,m,s=s,thin=THIN)
    return _cache[key]
# phases
ph={}
ph['c']=0.0
ph['a8']=gears.mate_phase(0.0,96,O,I8,9); ph['a6']=gears.mate_phase(0.0,96,O,I6,12)
ph['b8']=gears.mate_phase(ph['c'],64,C,I8,48); ph['b6']=gears.mate_phase(ph['c'],64,C,I6,48)
ph['pt']=gears.mate_phase(ph['c'],64,C,T,8); ph['wt']=0.0; ph['ps']=gears.mate_phase(ph['wt'],60,T,S,8)
ph['cp']=0.0; ph['Mw']=gears.mate_phase(ph['cp'],8,C,M,32); ph['Mp']=0.0
ph['H']=gears.mate_phase(ph['Mp'],8,M,C,24); ph['Dw']=gears.mate_phase(ph['Mp'],8,M,D,48)

def gear_solid(key,phk,center,zr):
    z=G[key][0]
    cs=gears.phased(gcs(key),z,ph[phk])
    pts=gears.outline(cs)
    w=cq.Workplane('XY').polyline([tuple(p) for p in pts]).close().extrude(zr[1]-zr[0])
    return w.translate((center[0],center[1],zr[0]))
def cyl(center,r,zr):
    return cq.Workplane('XY').circle(r).extrude(zr[1]-zr[0]).translate((center[0],center[1],zr[0]))
def disc_with_holes(zr,holes,blind=()):
    w=cyl(C,RP,zr)
    for (p,r) in holes: w=w.cut(cyl(p,r,(zr[0]-1,zr[1]+1)))
    for (p,r,z0,z1) in blind: w=w.cut(cyl(p,r,(z0,z1)))
    return w
def ring(zr,r0=12.3,r1=RP):
    return cyl(C,r1,zr).cut(cyl(C,r0,(zr[0]-1,zr[1]+1)))
def U(ws):
    w=ws[0]
    for x in ws[1:]: w=w.union(x)
    return w
def hand(center,zr,bore,hub,L,w,tail,ang=90.0):
    a=math.radians(ang); d=np.array([math.cos(a),math.sin(a)]); n=np.array([-d[1],d[0]])
    p0=center-d*tail; p1=center+d*L
    q=[p0+n*w/2,p1+n*w/2,p1-n*w/2,p0-n*w/2]
    bar=cq.Workplane('XY').polyline([tuple(x) for x in q]).close().extrude(zr[1]-zr[0]).translate((0,0,zr[0]))
    h=U([bar,cyl(center,hub,zr)])
    return h.cut(cyl(center,bore,(zr[0]-1,zr[1]+1)))
PILLARS=[np.array(p) for p in ((11.6,-1.0),(9.5,-5.8),(5.0,-10.2),(12.3,3.0))]
parts={}
# ---- frame ----
parts['plate']=U([disc_with_holes(Z['P'],[(O,0.54),(I8,0.34),(I6,0.34)])]+[cyl(p,0.45,(Z['P'][1],Z['MP'][0])) for p in PILLARS])
parts['midplate']=U([disc_with_holes(Z['MP'],[(O,1.05),(I8,0.5),(I6,0.5),(T,0.29),(S,0.29)]), ring((Z['MP'][1],Z['UP'][0]))])
parts['upperplate']=U([disc_with_holes(Z['UP'],[(O,0.54),(I8,0.44),(I6,0.44),(C,0.49),(T,0.84),(S,0.39)]), ring((Z['UP'][1],Z['MB'][0]))])
parts['motionplate']=U([disc_with_holes(Z['MB'],[(C,0.84),(S,0.39),(D,0.29)]), ring((Z['MB'][1],Z['DIAL'][0])), cyl(M,0.25,(Z['MB'][1],Z['DIAL'][0]))])
parts['dial']=disc_with_holes(Z['DIAL'],[(C,0.74),(S,0.39),(D,0.34)])
# ---- intermediate wheels ----
def iarb(pos,key,phk):
    return U([cyl(pos,0.3,(Z['P'][0],0.0)), gear_solid(key,phk,pos,Z['DRUM']), cyl(pos,0.4,(Z['DRUM'][1],Z['L1'][0])), cyl(pos,0.3,Z['L1'])])
def iwheel(pos,phk):
    return gear_solid('b',phk,pos,Z['L1']).cut(cyl(pos,0.3,(Z['L1'][0]-1,Z['L1'][1]+1)))
parts['inter8_arbor']=iarb(I8,'a8','a8'); parts['inter8_wheel']=iwheel(I8,'b8')
parts['inter6_arbor']=iarb(I6,'a6','a6'); parts['inter6_wheel']=iwheel(I6,'b6')
# ---- centre ----
parts['centre']=U([cyl(C,0.45,(Z['UP'][0],Z['L1'][0])), gear_solid('c','c',C,Z['L1']), cyl(C,0.8,(Z['L1'][1],Z['L2'][0]-0.04)), cyl(C,0.35,(Z['L2'][0]-0.04,Z['L2'][0])),
                   gear_solid('cp','cp',C,Z['L2']), cyl(C,0.3,(Z['L2'][1],Z['H2'][0])), cyl(C,0.2,Z['H2'])])
parts['hourwheel']=U([gear_solid('H','H',C,Z['L3']), cyl(C,0.7,(Z['L3'][1],Z['H1'][0])), cyl(C,0.6,Z['H1'])]).cut(cyl(C,0.34,(Z['L3'][0]-1,Z['H1'][1]+1)))
parts['third']=U([cyl(T,0.25,(Z['MP'][0],Z['LOW'][0])), gear_solid('wt','wt',T,Z['LOW']), cyl(T,0.8,(Z['LOW'][1],Z['L1'][0]-0.04)), cyl(T,0.35,(Z['L1'][0]-0.04,Z['L1'][0])), gear_solid('pt','pt',T,Z['L1'])])
parts['secondswheel']=U([cyl(S,0.25,(Z['MP'][0],Z['LOW'][0])), gear_solid('ps','ps',S,Z['LOW']), cyl(S,0.3,(Z['LOW'][1],Z['LOW'][1]+0.04)), cyl(S,0.5,(Z['LOW'][1]+0.04,Z['UP'][0]-0.04)),
                   cyl(S,0.35,(Z['UP'][0]-0.04,Z['H3'][0])), cyl(S,0.2,Z['H3'])])
parts['minutewheel']=U([gear_solid('Mw','Mw',M,Z['L2']), cyl(M,0.45,(Z['L2'][1],Z['L3'][0])), gear_solid('Mp','Mp',M,Z['L3'])]).cut(cyl(M,0.29,(Z['L2'][0]-1,Z['L3'][1]+1)))
parts['daywheel']=U([cyl(D,0.25,(Z['MB'][0],Z['L2'][0])), cyl(D,0.4,(Z['L2'][0],Z['L3'][0])), gear_solid('Dw','Dw',D,Z['L3']),
                   cyl(D,0.3,(Z['L3'][1],Z['H3'][0])), cyl(D,0.2,Z['H3'])])
# ---- hands ----
parts['hand_hour']=hand(C,Z['H1'],0.6,0.95,5.1,0.4,0.8)
parts['hand_minute']=hand(C,Z['H2'],0.2,0.5,5.6,0.35,0.8)
parts['hand_seconds']=hand(S,Z['H3'],0.2,0.5,5.3,0.3,1.2)
parts['hand_day']=hand(D,Z['H3'],0.2,0.5,3.3,0.35,0.6)

if __name__=='__main__':
    only=sys.argv[1:]
    for n,w in parts.items():
        if only and n not in only: continue
        sh=w.val()
        if hasattr(sh,'Solids') and len(sh.Solids())!=1: print('NOT ONE SOLID',n,len(sh.Solids()))
        if not sh.isValid(): print('INVALID',n)
        kernel.write_step(PD+'/%s.step'%n, w)
        print(n, os.path.getsize(PD+'/%s.step'%n), flush=True)
    json.dump(dict(POS={k:list(map(float,v)) for k,v in POS.items()},Z=Z), open(OUT+'/scripts/geom.json','w'),indent=1)
