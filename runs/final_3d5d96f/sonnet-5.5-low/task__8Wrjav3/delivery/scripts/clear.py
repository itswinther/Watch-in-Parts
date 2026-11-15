import sys
from kcheck import *
def clearances(variant,thr=0.12):
    mob,fixed,meshes,k2m=definition(variant)
    base={}
    items=[]
    bt=kernel.read_stl('/app/supplied/BR-096-30.stl',10**7,10**9)
    items.append(('barrel','barrel',kernel.tris_to_manifold(bt)))
    for m,(ns,key) in mob.items():
        for n in ns: items.append((m,n,mk(n)))
    for n in fixed: items.append(('fixed',n,mk(n)))
    meshset={frozenset([d,n]) for d,_,n,_ in meshes}
    res=[]
    for (m1,n1,a),(m2,n2,b) in itertools.combinations(items,2):
        if m1==m2 or (m1=='fixed' and m2=='fixed'): continue
        if not kernel.bbox_overlap(a,b,thr): continue
        if frozenset([m1,m2]) in meshset: continue
        d=kernel.min_distance(a,b,thr)
        if d<thr: res.append((round(d,4),n1,n2))
    return sorted(res)
if __name__=='__main__':
    for var in (False,True):
        print(var,clearances(var)[:25])
