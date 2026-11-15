import sys,json,numpy as np
sys.path.insert(0,'/app/work')
from load import *
build=sys.argv[1]
mv=json.load(open('/app/delivery/'+('movement.json' if build=='8h' else 'variant_6h.json')))
def mobpart(mn):
    if mn=='barrel': return barrel(),(0,0)
    return part(mv['mobiles'][mn]['parts'][0]),mv['mobiles'][mn]['axis']
for e in mv['meshes']:
    A,ca=mobpart(e['driver']);Bm,cb=mobpart(e['driven'])
    za,zb=e['driver_teeth'],e['driven_teeth']
    # restrict to bbox overlap region for speed: fine
    ratio=-za/zb
    mind=9;plays=[]
    for k,t in enumerate(np.linspace(0,2*np.pi/za,16,endpoint=False)):
        a=rotz(A,ca[0],ca[1],t);b0=t*ratio
        b=rotz(Bm,cb[0],cb[1],b0)
        v=kernel.ivol(a,b);d=kernel.min_distance(a,b,0.2) if v<1e-9 else -v
        mind=min(mind,d)
        if k%4==0:
            pl=[]
            for sgn in(1,-1):
                lo,hi=0,np.pi/zb
                for _ in range(14):
                    m=(lo+hi)/2
                    if kernel.ivol(a,rotz(Bm,cb[0],cb[1],b0+sgn*m))>1e-7: hi=m
                    else: lo=m
                pl.append(lo)
            plays.append(pl)
    pl=np.array(plays)
    print('%-14s->%-14s %3d/%3d mind=%.4f play(rad) min %.4f max %.4f'%(e['driver'],e['driven'],za,zb,mind,pl.min(),pl.max()),flush=True)
