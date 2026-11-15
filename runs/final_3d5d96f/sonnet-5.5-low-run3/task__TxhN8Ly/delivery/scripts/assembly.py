import sys, json, math, graphlib, numpy as np
sys.path.insert(0,'/app/tools'); sys.path.insert(0,'/app/work')
import kernel
from deps import mans, allnames, ztop
edges=json.load(open('edges.json'))
ts=graphlib.TopologicalSorter()
for p in allnames: ts.add(p)
for p,qs in edges.items():
    for q in qs: ts.add(q,p)    # q after p
order=list(ts.static_order())
print(order)
# verify with real path
step=0.15
paths={}
placed=[]
bad=0
for P in order:
    A=mans[P]; zmin=A.bounding_box()[2]
    s=ztop+5.0+0.3-zmin
    n=int(math.ceil(s/step))
    ts_=[s*(1-i/n) for i in range(n+1)]; ts_[-1]=0.0
    poses=[[[1,0,0,0],[0,1,0,0],[0,0,1,float(t)],[0,0,0,1]] for t in ts_]
    paths[P]=poses
    for Q in placed:
        B=mans[Q]
        if not kernel.bbox_overlap(A.translate([0,0,s]),B) and False: pass
        for t in ts_:
            if kernel.ivol(A.translate([0,0,t]),B)>1e-4:
                print('COLLISION',P,Q,t); bad+=1; break
    placed.append(P)
print('bad',bad)
json.dump(dict(order=order,paths=paths),open('/app/delivery/assembly.json','w'))
