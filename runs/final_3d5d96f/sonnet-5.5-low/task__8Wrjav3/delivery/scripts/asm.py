import sys,json,math,time,numpy as np,itertools
sys.path.insert(0,'/app/tools')
import kernel, manifold3d as m3
sys.argv=['x','1']
import pickle
raw=pickle.load(open('/app/work/meshes.pkl','rb'))
def mk(name):
    vp,tv=raw[name]
    return m3.Manifold(m3.Mesh(vp.astype(np.float32),tv.astype(np.uint32)))
def barrel():
    return kernel.tris_to_manifold(kernel.read_stl('/app/supplied/BR-096-30.stl',10**7,10**9))
STEP=0.15
def sweep_hits(part, others, top_z, dirn=+1):
    """names in others hit by part translated by dirn*t for t in 0..T (T s.t. part's bbox clears top_z+5)."""
    bb=part.bounding_box()
    T=(top_z+5.5-bb[2]) if dirn>0 else None
    n=int(math.ceil(T/STEP))
    hits=set()
    for k in range(1,n+1):
        pm=part.translate([0,0,dirn*k*T/n])
        for name,o in others.items():
            if name in hits: continue
            if kernel.ivol(pm,o)>0.005: hits.add(name)
    return hits,T,n
def plan(parts, top_z):
    """parts: dict name->manifold. returns order, paths, edges"""
    edges={}
    for name,p in parts.items():
        others={k:v for k,v in parts.items() if k!=name}
        h,T,n=sweep_hits(p,others,top_z)
        edges[name]=h
    return edges
def toposort(edges):
    # edges[B] = parts that block B's path if placed before B => B before each of them
    names=list(edges); before={n:set() for n in names}  # before[A]: must be placed before A
    for b,hs in edges.items():
        for a in hs: before[a].add(b)
    order=[]; placed=set()
    rem=set(names)
    while rem:
        cand=[n for n in rem if before[n]<=placed]
        if not cand: return None,rem
        n=sorted(cand)[0]
        order.append(n); placed.add(n); rem.remove(n)
    return order,None
