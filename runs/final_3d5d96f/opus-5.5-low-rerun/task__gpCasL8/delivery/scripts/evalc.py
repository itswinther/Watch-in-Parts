from j3 import *
import json
cands=[json.loads(l[l.index('['):]) for l in sys.stdin if l.startswith('-0')]
for x in cands:
    P,pen=build3(x)
    zs={k:round(v/0.02)*0.02 for k,v in zip(FREE,x[10:])}
    z=dict(FIX);z.update(zs)
    # gear z ranges
    gz={g:(z[g2grp[g]],z[g2grp[g]]+TH[g2grp[g]]) for g in g2grp}
    gz['pA']=(0,0.4545);gz['pA2']=(0,0.4545)
    edges=set()
    for (g1,m1,r1,_),(g2,m2,r2,_) in itertools.combinations(G,2):
        if m1==m2: continue
        if np.linalg.norm(P[m1]-P[m2])<r1+r2+0.06:
            # mesh pairs same z: fine
            if gz[g1][0]>=gz[g2][1]: edges.add((m2,m1))   # g2 lower -> m2 first
            elif gz[g2][0]>=gz[g1][1]: edges.add((m1,m2))
    # cycle check
    import collections
    adj=collections.defaultdict(set)
    for a,b in edges: adj[a].add(b)
    order=[];state={}
    def dfs(u):
        state[u]=1
        for v in adj[u]:
            if state.get(v)==1: raise ValueError('cycle %s->%s'%(u,v))
            if v not in state: dfs(v)
        state[u]=2;order.append(u)
    try:
        for u in list(P):
            if u not in state: dfs(u)
        res='DAG '+str(order[::-1])
    except ValueError as e: res=str(e)
    b,m=viol(P)
    print(round(pen,4),b,{k:round(v,2) for k,v in z.items()},res)
