from joint import *
FREE=['g3','g4','g5','g6','g7','g8']
def zpen(P,zs):
    z=dict(FIX);z.update(zs)
    pen=0
    for k in z:
        if z[k]<ZMIN-1e-9 or z[k]+TH[k]>ZMAX+1e-9: pen+=1
        if not postok(P,k,z[k]): pen+=0.5
    def zov(a,b): return not (z[a]+TH[a]+GAP<=z[b]+1e-9 or z[b]+TH[b]+GAP<=z[a]+1e-9)
    for mo,ks in MOB.items():
        for a,b in itertools.combinations(sorted(ks),2):
            if zov(a,b): pen+=1
    for (g1,m1,r1,mt1),(g2,m2,r2,mt2) in itertools.combinations(G,2):
        if m1==m2 or g1 not in g2grp or g2 not in g2grp: continue
        k1,k2=g2grp[g1],g2grp[g2]
        if k1==k2 or not zov(k1,k2): continue
        d=np.linalg.norm(P[m1]-P[m2])-(r1+r2+0.06)
        if d<0: pen+=-d
    return pen
def F(x):
    p=x[:7];s=[1 if v>0 else -1 for v in x[7:10]];zz=x[10:]
    try: P=build2(p,s)
    except Exception: return 100
    b,m=viol(P)
    zs={k:round(v/0.02)*0.02 for k,v in zip(FREE,zz)}
    return 10*b+10*zpen(P,zs)-min(m,0.3)
if __name__=="__main__":
    from scipy.optimize import differential_evolution
    bounds=[(0,90),(-40,0),(0,360),(0,360),(0,360),(5.5,7.5),(0,360),(-1,1),(-1,1),(-1,1)]+[(ZMIN,ZMAX-TH[k]) for k in FREE]
    for seed in range(int(sys.argv[1]),int(sys.argv[1])+4):
        r=differential_evolution(F,bounds,seed=seed,maxiter=1500,popsize=40,tol=1e-10,mutation=(0.5,1.0),recombination=0.9)
        print(seed,round(r.fun,4),np.round(r.x,3).tolist(),flush=True)
