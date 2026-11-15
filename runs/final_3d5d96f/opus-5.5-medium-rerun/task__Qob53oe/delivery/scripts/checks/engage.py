import json, math, sys
import numpy as np
from vlib import *
build=sys.argv[1]
doc=json.load(open(os.path.join(DEL,build)))
names=list(doc['fixed'])+[p for m in doc['mobiles'].values() for p in m['parts']]
P=load_parts(names)
bodies={'barrel':barrel(doc['barrel'])}; axis={'barrel':(0.0,0.0)}
for k,m in doc['mobiles'].items():
    bodies[k]=kernel.union([P[n] for n in m['parts']]); axis[k]=tuple(m['axis'])
for e in doc['meshes']:
    a,b=e['driver'],e['driven']; za,zb=e['driver_teeth'],e['driven_teeth']
    # clip both bodies to the region near the mesh to speed up
    pa,pb=np.array(axis[a]),np.array(axis[b]); mid=pa+(pb-pa)*(za/(za+zb))
    box=kernel.box([mid[0]-1.5,mid[1]-1.5,-1],[mid[0]+1.5,mid[1]+1.5,5])
    A=bodies[a]; B=bodies[b]
    pitch=2*math.pi/za
    plays=[]
    for t in np.linspace(0,pitch,13)[:-1]:
        res=[]
        for sgn in (1,-1):
            lo,hi=0.0,pitch*0.6
            def hit(d):
                AA=rotz(A,t+sgn*d,axis[a])^box; BB=rotz(B,-t*za/zb,axis[b])^box
                return kernel.ivol(AA,BB)>1e-7
            if not hit(hi): res.append(float('inf')); continue
            for _ in range(18):
                m_=(lo+hi)/2
                if hit(m_): hi=m_
                else: lo=m_
            res.append(hi)
        plays.append(res)
    plays=np.array(plays)
    ra=0.5*za*(math.dist(pa,pb)/((za+zb)/2))  # pitch radius of driver
    print('%-13s->%-13s free play (arc at driver pitch, mm): fwd %.4f..%.4f  back %.4f..%.4f'%(a,b,
          plays[:,0].min()*ra,plays[:,0].max()*ra,plays[:,1].min()*ra,plays[:,1].max()*ra),flush=True)
