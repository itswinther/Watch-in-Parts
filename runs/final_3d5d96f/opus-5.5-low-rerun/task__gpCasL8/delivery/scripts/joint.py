from opt import *
GRP={'g1':['gH','dh','gT'],'g2':['gM','dm2'],'g3':['wA','pX','pX2'],'g4':['x2m','dm1'],'g5':['xs','y1'],'g6':['y2','pS'],'g7':['aq','q1'],'g8':['q2','dh1']}
TH={'g1':0.72,'g2':0.28,'g3':0.27,'g4':0.30,'g5':0.25,'g6':0.25,'g7':0.43,'g8':0.55}
FIX={'g1':0.74,'g2':2.27}
gi={g:(mo,r) for g,mo,r,_ in G}
g2grp={g:k for k,v in GRP.items() for g in v}
MOB={}
for g,mo,r,_ in G:
    if g in g2grp: MOB.setdefault(mo,set()).add(g2grp[g])
ZMIN,ZMAX,GAP=0.74,2.55,0.04
def conflicts(P):
    cf=set()
    for (g1,m1,r1,mt1),(g2,m2,r2,mt2) in itertools.combinations(G,2):
        if m1==m2 or g1 not in g2grp or g2 not in g2grp: continue
        k1,k2=g2grp[g1],g2grp[g2]
        if k1==k2: continue
        if np.linalg.norm(P[m1]-P[m2])<r1+r2+0.06: cf.add(tuple(sorted((k1,k2))))
    for mo,ks in MOB.items():
        for a,b in itertools.combinations(sorted(ks),2): cf.add((a,b))
    return cf
def postok(P,k,z0):
    z1=z0+TH[k]
    if z1<=1.5-0.03 or z0>=2.2273+0.03: return True
    for g in GRP[k]:
        mo,r=gi[g]
        if np.linalg.norm(P[mo]-B)<r+0.99+0.06: return False
    return True
def solve(P,step=0.01):
    cf=conflicts(P)
    order=['g8','g7','g4','g3','g5','g6']
    z={k:v for k,v in FIX.items()}
    def ok(k,z0):
        for a,b in cf:
            o=b if a==k else a if b==k else None
            if o is None or o not in z: continue
            if not (z0+TH[k]+GAP<=z[o] or z[o]+TH[o]+GAP<=z0): return False
        return postok(P,k,z0)
    def rec(i):
        if i==len(order): return True
        k=order[i]
        for z0 in np.arange(ZMIN,ZMAX-TH[k]+1e-9,step):
            if ok(k,z0):
                z[k]=round(z0,3)
                if rec(i+1): return True
                del z[k]
        return False
    if all(ok(k,FIX[k]) for k in FIX) and rec(0): return z
    return None
if __name__=="__main__":
    from scipy.optimize import differential_evolution
    import random
    best=None
    rng=np.random.default_rng(int(sys.argv[1]))
    for signs in itertools.product([-1,1],repeat=3):
      for trial in range(3):
        r=differential_evolution(f,[(0,90),(-40,0),(0,360),(0,360),(0,360),(5.5,7.5),(0,360)],args=(signs,),seed=int(rng.integers(1e6)),maxiter=200,popsize=25,tol=1e-8)
        if r.fun>-0.05: continue
        P=build2(r.x,signs)
        z=solve(P,0.02)
        print(signs,round(r.fun,3),np.round(r.x,2).tolist(),z,flush=True)
