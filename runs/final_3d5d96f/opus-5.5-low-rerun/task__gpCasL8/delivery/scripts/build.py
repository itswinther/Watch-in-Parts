import numpy as np, sys, json, os, time
sys.path.insert(0,'/app/work'); sys.path.insert(0,'/app/tools')
from design import *
from frame import plate, plate2, dial
import kernel
OUT='/app/delivery'
HANDMOB={'minute':'M','hour':'H','seconds':'S','day':'T'}
def body_name(mob,build): return MOBILE_NAMES[mob]+('_'+build if mob in VARIES else '')
def all_shapes():
    S={'plate':plate(),'plate2':plate2(),'dial':dial()}
    for b in ('8h','6h'):
        for mob in MOBILE_NAMES:
            n=body_name(mob,b)
            if n not in S: S[n]=body(mob,b)
    for k in HANDMOB: S['hand_'+k]=hand(k)
    return S
def movement(build):
    mobs={}
    for mob,mn in MOBILE_NAMES.items():
        parts=[body_name(mob,build)]
        for k,v in HANDMOB.items():
            if v==mob: parts.append('hand_'+k)
        mobs[mn]={'axis':[round(float(POS[mob][0]),6),round(float(POS[mob][1]),6)],'parts':parts,'material':'AD-C100-HT'}
    meshes=[]
    for drv,dn in MESHES:
        dmob='barrel' if drv=='drum' else MOBILE_NAMES[GEARS[drv][0]]
        meshes.append({'driver':dmob,'driver_teeth':96 if drv=='drum' else spec(drv,build)[0],
                       'driven':MOBILE_NAMES[GEARS[dn][0]],'driven_teeth':spec(dn,build)[0]})
    hands={k:{'mobile':MOBILE_NAMES[v],'part':'hand_'+k} for k,v in HANDMOB.items()}
    return {'barrel':'BR-096-30','case_centre':[float(CC[0]),float(CC[1])],'fixed':['plate','plate2','dial'],
            'mobiles':mobs,'meshes':meshes,'hands':hands}
if __name__=="__main__":
    os.makedirs(OUT+'/parts',exist_ok=True)
    S=all_shapes()
    only=sys.argv[1:]
    for n,s in S.items():
        if only and n not in only: continue
        t=time.time()
        kernel.write_step(OUT+'/parts/%s.step'%n,s.cadquery())
        print(n,round(time.time()-t,1),os.path.getsize(OUT+'/parts/%s.step'%n),flush=True)
    json.dump(movement('8h'),open(OUT+'/movement.json','w'),indent=1)
    json.dump(movement('6h'),open(OUT+'/variant_6h.json','w'),indent=1)
