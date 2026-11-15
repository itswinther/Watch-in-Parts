import sys, json, itertools, numpy as np
sys.path.insert(0,'/app/tools'); sys.path.insert(0,'/app/work')
import kernel
from check import part, barrel
mv=json.load(open('/app/delivery/movement.json'))
names=list(mv['fixed'])+[p for m in mv['mobiles'].values() for p in m['parts']]
mans={n:part(n) for n in names}; mans['barrel']=barrel(mv['barrel'])
allnames=names+['barrel']
ztop=max(m.bounding_box()[5] for m in mans.values())
def blocks(P,Q,step=0.1):
    """does P descending from above hit Q (Q in final place)?"""
    A=mans[P];B=mans[Q];ba=A.bounding_box();bb=B.bounding_box()
    if ba[0]>bb[3] or bb[0]>ba[3] or ba[1]>bb[4] or bb[1]>ba[4]: return False
    t=0.0
    tmax=bb[5]-ba[2]+0.05
    while t<=tmax:
        if kernel.ivol(A.translate([0,0,t]),B)>1e-4: return True
        t+=step
    return False
if __name__=="__main__":
    edges={}
    for P in allnames:
        edges[P]=[Q for Q in allnames if Q!=P and blocks(P,Q)]
        print(P,'must precede',edges[P],flush=True)
    json.dump(edges,open('edges.json','w'))
