import sys
from kcheck import *
def meshgaps(variant,nph=10):
    mob,fixed,meshes,k2m=definition(variant)
    rate=1/6 if variant else 1/8
    sp=speeds(meshes,rate)
    base={n:mk(n) for ns,_ in mob.values() for n in ns}
    bt=kernel.read_stl('/app/supplied/BR-096-30.stl',10**7,10**9)
    barrel=kernel.tris_to_manifold(bt)
    axis={m:tuple(P[key]) for m,(ns,key) in mob.items()}; axis['barrel']=(0,0)
    def part_of(m,layer_gear=None): return mob[m][0]
    out={}
    for d,zd,n,zn in meshes:
        pitch=1.0/zd   # turns of driver per tooth pitch
        mn=1e9
        for k in range(nph):
            ang=pitch*k/nph   # driver turns
            def pos(m,turns):
                if m=='barrel': return [rot(barrel,0,0,-2*math.pi*turns)]
                return [rot(base[p],axis[m][0],axis[m][1],-2*math.pi*turns) for p in mob[m][0]]
            tdrv=ang; tdn=ang*(-1)*zd/zn  # signed turns: cw positive; driven turns = -driver*zd/zn
            A=pos(d,tdrv) ; B=pos(n,tdn)
            for a in A:
                for b in B:
                    if kernel.ivol(a,b)>0.0: mn=min(mn,-1)
                    else: mn=min(mn,a.min_gap(b,0.3))
        out[(d,n)]=mn
    return out
if __name__=='__main__':
    for var in (False,True):
        r=meshgaps(var)
        print(var,{k:round(x,4) for k,x in r.items()})
