import sys
from kin import *
def rot(m,ax,ay,th):
    c,s=math.cos(th),math.sin(th)
    T=[[c,-s,0,ax-c*ax+s*ay],[s,c,0,ay-s*ax-c*ay],[0,0,1,0]]
    return m.transform(T)
def run(variant,nsamp,seed=0):
    mob,fixed,meshes,k2m=definition(variant)
    rate=1/6 if variant else 1/8
    sp=speeds(meshes,rate)
    base={n:mk(n) for ns,_ in mob.values() for n in ns}
    for n in fixed: base[n]=mk(n)
    barrel=m3.Manifold(m3.Mesh(*[None]*0)) if False else None
    bt=kernel.read_stl('/app/supplied/BR-096-30.stl',10**7,10**9)
    barrel=kernel.tris_to_manifold(bt)
    axis={m:tuple(P[key]) for m,(ns,key) in mob.items()}
    rng=random.Random(seed)
    worst={}
    for it in range(nsamp):
        t=rng.uniform(0,24) if it>0 else 0.0
        objs={'barrel':[('barrel',rot(barrel,0,0,-2*math.pi*sp['barrel']*t),'barrel')]}
        items=[]
        items.append(('barrel','barrel',rot(barrel,0,0,-2*math.pi*sp['barrel']*t)))
        for m,(ns,key) in mob.items():
            for n in ns: items.append((m,n,rot(base[n],axis[m][0],axis[m][1],-2*math.pi*sp[m]*t)))
        for n in fixed: items.append(('fixed',n,base[n]))
        for (m1,n1,a),(m2,n2,b) in itertools.combinations(items,2):
            if m1==m2: continue
            if m1=='fixed' and m2=='fixed': continue
            vol=kernel.ivol(a,b)
            if vol>0.0:
                k=(n1,n2)
                if vol>worst.get(k,0): worst[k]=vol
    return worst
if __name__=='__main__':
    variant=sys.argv[1]=='6'
    w=run(variant,int(sys.argv[2]))
    print({k:round(x,4) for k,x in sorted(w.items(),key=lambda t:-t[1])})
