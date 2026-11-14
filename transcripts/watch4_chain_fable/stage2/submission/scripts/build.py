"""Stage 2: add idler + day mobiles. hour(48) -> idler(24), idler(10) -> day(40)."""
import shutil
from common import *
import cadquery as cq
C=np.array([10.85,0.0])
def pol(d,a): return C+d*np.array([np.cos(np.radians(a)),np.sin(np.radians(a))])
M1=0.32; M2=0.2
IDL=pol(M1*(48+24)/2,-121.0)
DAY=IDL+5.0*np.array([np.cos(np.radians(-60)),np.sin(np.radians(-60))])
PA=np.radians(25)
def inv(a): return np.tan(a)-a
def gear_pts(z,m,phase,bl,nf=7,nr=3):
    rp=m*z/2; rb=rp*np.cos(PA); ra=rp+m; rf=rp-1.25*m
    half=(np.pi*m/2-bl)/2/rp
    r0=max(rb,rf)
    rs=np.linspace(r0,ra,nf)
    hs=half+inv(PA)-inv(np.arccos(np.clip(rb/rs,-1,1)))
    pts=[]
    pitch=2*np.pi/z
    for i in range(z):
        t=phase+i*pitch
        # right flank (cw side) going up, then left going down
        if rf<r0: pts.append((rf,t-hs[0]))
        for r,h in zip(rs,hs): pts.append((r,t-h))
        for r,h in zip(rs[::-1],hs[::-1]): pts.append((r,t+h))
        if rf<r0: pts.append((rf,t+hs[0]))
        # root arc to next tooth
        a0=t+hs[0]; a1=t+pitch-hs[0]
        for k in range(1,nr+1): pts.append((rf,a0+(a1-a0)*k/(nr+1)))
    return [(r*np.cos(a),r*np.sin(a)) for r,a in pts]
def gear_man(z,m,phase,bl,axis,z0,z1):
    cs=m3.CrossSection([gear_pts(z,m,phase,bl)])
    return cs.extrude(z1-z0).translate([axis[0],axis[1],z0])
def gear_cq(z,m,phase,bl,axis,z0,z1,bore=0.5):
    w=cq.Workplane('XY').workplane(offset=z0).polyline(gear_pts(z,m,phase,bl)).close().extrude(z1-z0)
    w=w.cut(cq.Workplane('XY').workplane(offset=z0-1).circle(bore).extrude(z1-z0+2))
    return w.translate((axis[0],axis[1],0))
def phase_search(fixed,z,m,bl,axis,z0,z1):
    """phase (rad) of the new gear with the most clearance against `fixed`."""
    pitch=2*np.pi/z; N=120
    v=np.array([kernel.ivol(fixed,gear_man(z,m,pitch*k/N,bl,axis,z0,z1)) for k in range(N)])
    free=v<1e-9
    assert free.any() and not free.all(),(v.min(),v.max())
    # centre of the free run (circular)
    s=next(k for k in range(N) if free[k] and not free[k-1])
    n=0
    while free[(s+n)%N]: n+=1
    print('free run',n,'of',N)
    return pitch*(s+(n-1)/2)/N
def arbor(axis,ztop):
    w=cq.Workplane('XY').workplane(offset=-1.0).circle(0.5).extrude(ztop+1.0)
    for a,b in((0.05,0.6),(8.2,8.7)):
        w=w.union(cq.Workplane('XY').workplane(offset=a).circle(0.9).extrude(b-a))
    return w.translate((axis[0],axis[1],0))
def main():
    mv=json.load(open('previous/movement.json'))
    hw=load('previous/parts/hour_wheel_48t_m032.step')
    out={}
    BL1,BL2=0.04,0.03
    ph=phase_search(hw,24,M1,BL1,IDL,6.0,7.0)
    out['idler_wheel_24t_m032']=gear_cq(24,M1,ph,BL1,IDL,6.0,7.0)
    out['idler_pinion_10t_m020']=gear_cq(10,M2,0.0,BL2,IDL,7.0,8.0)
    pin=gear_man(10,M2,0.0,BL2,IDL,7.0,8.0)
    ph2=phase_search(pin,40,M2,BL2,DAY,7.2,8.0)
    out['day_wheel_40t_m020']=gear_cq(40,M2,ph2,BL2,DAY,7.2,8.0)
    out['idler_arbor']=arbor(IDL,9.5)
    out['day_arbor']=arbor(DAY,10.2)
    hand=(cq.Workplane('XY').workplane(offset=9.8).circle(0.9).extrude(0.4)
          .union(cq.Workplane('XY').workplane(offset=9.8).polyline([(-0.35,0),(0.35,0),(0.2,3.3),(-0.2,3.3)]).close().extrude(0.4))
          .cut(cq.Workplane('XY').workplane(offset=9).circle(0.5).extrude(2)))
    out['day_hand']=hand.translate((DAY[0],DAY[1],0))
    for n,(a,b) in (('bottom_plate',(-1.5,-0.0)),('top_plate',(8.5,10.0))):
        s=cq.importers.importStep('previous/parts/%s.step'%n)
        for ax in (IDL,DAY):
            # bottom: cut also a hair above 0 is not needed; holes are through the plate only
            s=s.cut(cq.Workplane('XY').workplane(offset=a).circle(0.56).extrude(b-a).translate((ax[0],ax[1],0)))
        out[n]=s
    for n,s in out.items():
        kernel.write_step('work/parts/%s.step'%n,s)
    mv['mobiles']['idler']={'axis':[float(IDL[0]),float(IDL[1])],'parts':['idler_arbor','idler_wheel_24t_m032','idler_pinion_10t_m020']}
    mv['mobiles']['day']={'axis':[float(DAY[0]),float(DAY[1])],'parts':['day_arbor','day_wheel_40t_m020','day_hand']}
    mv['meshes']+=[{'driver':'hour','driver_teeth':48,'driven':'idler','driven_teeth':24},
                   {'driver':'idler','driver_teeth':10,'driven':'day','driven_teeth':40}]
    mv['hands']['day']={'mobile':'day','part':'day_hand'}
    json.dump(mv,open('work/movement.json','w'),indent=1)
    print('IDL',IDL,'DAY',DAY)
if __name__=='__main__': main()
