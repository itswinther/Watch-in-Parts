exec(open('scripts/plan.py').read().split("ORDER=")[0])
import numpy as np
for a,(x,y) in (('arb_a',(5.456,4.059)),('arb_day',(3.86,2.8535))):
  m=S[a]
  for z in np.arange(BB[a][0][2]+0.05,BB[a][1][2],0.3):
    sl=m.slice(z); pts=np.concatenate([np.array(p) for p in sl.to_polygons()]) if sl.num_contour() else np.zeros((0,2))
    r=np.hypot(pts[:,0]-x,pts[:,1]-y) if len(pts) else [0]
    c=S['day_cock'].slice(z); 
    cp=np.concatenate([np.array(p) for p in c.to_polygons()]) if c.num_contour() else np.zeros((0,2))
    d=np.hypot(cp[:,0]-x,cp[:,1]-y).min() if len(cp) else -1
    print(a,round(z,2),'arb r',round(max(r),2),'cock nearest',round(d,2))
