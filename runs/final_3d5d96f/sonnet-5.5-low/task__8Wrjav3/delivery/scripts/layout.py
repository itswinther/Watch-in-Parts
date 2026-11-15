import numpy as np, itertools, json, sys, math, pickle
seed=int(sys.argv[1]) if len(sys.argv)>1 else 1
rng=np.random.default_rng(seed)
M=0.2
def Rp(z): return M*z/2
def Rt(z): return M*(z+2)/2
def dist(z1,z2): return M*(z1+z2)/2
G={
 'M1':{'p':12,'w':21},
 'X':{'a':24,'b':12,'s':30},
 'Y':{'c':16},
 'C':{'w':12,'k':12},
 'A':{'w':48,'p':12},
 'B':{'w':27,'p':12},
 'J':{'j':12},
 'H':{'h':16},
 'I':{'a':16,'b':13},
 'D':{'w':26},
 'S1':{'p':12,'w':24},'S2':{'p':12,'w':36},'S3':{'p':12,'w':48},'S':{'p':12},
}
MESH=[(('M1','w'),('X','a')),(('X','b'),('Y','c')),(('Y','c'),('C','w')),
 (('C','k'),('A','w')),(('A','p'),('B','w')),(('B','p'),('J','j')),(('J','j'),('H','h')),
 (('H','h'),('I','a')),(('I','b'),('D','w')),
 (('X','s'),('S1','p')),(('S1','w'),('S2','p')),(('S2','w'),('S3','p')),(('S3','w'),('S','p'))]
NL=4
def _components():
    keys=[(m,g) for m,gs in G.items() for g in gs]
    par={k:k for k in keys}
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for a,b in MESH: par[f(a)]=f(b)
    comps={}
    for k in keys: comps.setdefault(f(k),[]).append(k)
    return list(comps.values())
COMPS=_components()
FIXED={('M1','p'):0,('C','w'):2,('C','k'):3,('H','h'):1}
def comp_constraints():
    cid={k:i for i,c in enumerate(COMPS) for k in c}
    conflicts=set()
    for m,gs in G.items():
        ids=[cid[(m,g)] for g in gs]
        for i in range(len(ids)):
            for j in range(i+1,len(ids)):
                conflicts.add((min(ids[i],ids[j]),max(ids[i],ids[j])))
    fixed={}
    for k,l in FIXED.items(): fixed[cid[k]]=l
    return cid,conflicts,fixed
CID,CONF,CFIX=comp_constraints()
def sample_layers():
    n=len(COMPS)
    for attempt in range(200):
        lay={}
        ok=True
        order=list(rng.permutation(n))
        for i in order:
            if i in CFIX:
                lay[i]=CFIX[i]; continue
            opts=[l for l in range(1,NL+1) if all(not((min(i,j),max(i,j)) in CONF and lay[j]==l) for j in lay)]
            if not opts: ok=False; break
            lay[i]=int(rng.choice(opts))
        if ok:
            # verify fixed conflicts
            if any((min(i,j),max(i,j)) in CONF and lay[i]==lay[j] for i in lay for j in lay if i<j): continue
            return {k:lay[CID[k]] for k in CID}
    return None
def mutate_layers(L,r):
    lay={i:L[COMPS[i][0]] for i in range(len(COMPS))}
    free=[i for i in lay if i not in CFIX]
    i=int(r.choice(free))
    opts=[l for l in range(1,NL+1) if l!=lay[i] and all(not((min(i,j),max(i,j)) in CONF and lay[j]==l) for j in lay if j!=i)]
    if not opts: return L
    lay[i]=int(r.choice(opts))
    return {k:lay[CID[k]] for k in CID}
def pol(c,r,a): return c+r*np.array([math.cos(a),math.sin(a)])
def circ2(P,r1,Q,r2,sgn):
    d=np.linalg.norm(Q-P)
    if d>r1+r2 or d<abs(r1-r2) or d<1e-9: return None
    a=(r1*r1-r2*r2+d*d)/(2*d); h2=r1*r1-a*a
    if h2<0: return None
    h=math.sqrt(h2); u=(Q-P)/d; n=np.array([-u[1],u[0]])
    return P+a*u+sgn*h*n
def positions(v):
    t1,rc,tc,ax,ys,aa,bb,js,ii,dd,s1,s2,s3,ss=v
    P={'B0':np.zeros(2)}
    P['M1']=10.8*np.array([math.cos(t1),math.sin(t1)])
    C=rc*np.array([math.cos(tc),math.sin(tc)]);P['C']=C;P['H']=C
    P['X']=pol(P['M1'],4.2,ax)
    Y=circ2(P['X'],2.8,C,2.8,ys)
    if Y is None: return None
    P['Y']=Y
    P['A']=pol(C,6.0,aa)
    P['B']=pol(P['A'],3.9,bb)
    J=circ2(P['B'],2.4,C,2.8,js)
    if J is None: return None
    P['J']=J
    P['I']=pol(C,3.2,ii)
    P['D']=pol(P['I'],3.9,dd)
    P['S1']=pol(P['X'],4.2,s1)
    P['S2']=pol(P['S1'],3.6,s2)
    P['S3']=pol(P['S2'],4.8,s3)
    P['S']=pol(P['S3'],6.0,ss)
    return P
CASE_R=12.7
PIL_R=0.55
SOFTPEN=0.4
def evaluate(P,L,pillars,verbose=False):
    viol=0.0; msgs=[]
    C=P['C']
    elems=[] # (mobile,gear,layer,R,pos)
    for m,gs in G.items():
        for g,z in gs.items():
            elems.append((m,g,L[(m,g)],Rt(z),P[m]))
    # shafts: (mobile, layers set, R)
    shafts=[]; soft=[]
    for m,gs in G.items():
        if m=='H': continue
        if m=='C':
            shafts.append((m,2,NL,0.93,P[m])); shafts.append((m,1,1,0.65,P[m])); continue
        ls=[L[(m,g)] for g in gs]
        lo_g=max(1,min(ls)); hg=max(ls)
        if m in ('D','S'): hg=NL
        shafts.append((m,lo_g,hg,0.3,P[m]))
        if hg<NL: soft.append((m,hg+1,NL,0.3,P[m],'up'))
        if lo_g>1 and m!='M1': soft.append((m,1,lo_g-1,0.3,P[m],'low'))
    def add(v,msg):
        nonlocal viol
        if v>0:
            viol+=v
            if verbose: msgs.append((round(v,3),msg))
    meshpairs={frozenset([a,b]) for a,b in MESH}
    n=len(elems)
    for i in range(n):
        m1,g1,l1,R1,p1=elems[i]
        # case
        add(np.linalg.norm(p1-C)+R1-(CASE_R-0.3),('case',m1,g1))
        # keepout origin
        ko={0:0.6,1:0.75,2:1.12,3:1.12,4:1.12}[l1]
        add(ko-(np.linalg.norm(p1)-R1),('arbor',m1,g1,l1))
        for pc in pillars:
            add(PIL_R+0.25-(np.linalg.norm(p1-pc)-R1),('pillar',m1,g1))
        for j in range(i+1,n):
            m2,g2,l2,R2,p2=elems[j]
            if m1==m2 or l1!=l2: continue
            d=np.linalg.norm(p1-p2)
            if frozenset([(m1,g1),(m2,g2)]) in meshpairs: continue
            add(R1+R2+0.2-d,('gear',m1,g1,m2,g2,l1))
    # gears vs other shafts
    mobmesh={}
    for a,b in MESH:
        mobmesh.setdefault((a[0],b[0]),set()).add((a,b)); mobmesh.setdefault((b[0],a[0]),set()).add((a,b))
    def partner(m,g,l,ms):
        for a,b in mobmesh.get((m,ms),()):
            if (m,g) in (a,b):
                o=b if a==(m,g) else a
                if L[o]==l: return True
        return False
    for (m,g,l,R,p) in elems:
        for (ms,lo,hi,Rs,ps) in shafts:
            if ms==m or (ms=='C' and m=='H') : continue
            if partner(m,g,l,ms): continue
            if lo<=l<=hi:
                add(R+Rs+0.2-np.linalg.norm(p-ps),('shaft',m,g,ms))
    missing={}
    for (ms,lo,hi,Rs,ps,kind) in soft:
        bad=False
        for (m,g,l,R,p) in elems:
            if m==ms or (ms=='C' and m=='H'): continue
            if partner(m,g,l,ms): continue
            if lo<=l<=hi and R+Rs+0.2-np.linalg.norm(p-ps)>0: bad=True
        for pc in pillars:
            if PIL_R+Rs+0.3-np.linalg.norm(ps-pc)>0: bad=True
        for (m2,lo2,hi2,Rs2,ps2) in shafts:
            if m2!=ms and not (lo>hi2 or hi<lo2) and Rs+Rs2+0.2-np.linalg.norm(ps-ps2)>0: bad=True
        if bad:
            add(SOFTPEN,('no'+kind,ms)); missing.setdefault(ms,set()).add(kind)
    for ms,ks in missing.items():
        if len(ks)==2: add(3.0,('nobearing',ms))
    # precedence cycles (vertical assembly)
    parts={}
    def addel(part,lo,hi,R,pos): parts.setdefault(part,[]).append((lo,hi,R,pos))
    for m,gs in G.items():
        for g,z in gs.items():
            part={'C':'minute_tube','H':'hour_tube'}.get(m,m)
            l=L[(m,g)]
            addel(part,l,l,Rt(z),P[m])
    for m,gs in G.items():
        if m=='H':
            addel('hour_tube',1,NL,0.65,P[m]); continue
        if m=='C':
            addel('minute_tube',2,NL,0.93,P[m]); continue
        ls=[L[(m,g)] for g in gs]
        lo_g=max(1,min(ls)); hg=max(ls)
        miss=missing.get(m,set())
        lo_e=1 if (m!='M1' and 'low' not in miss) else lo_g
        if m=='M1': lo_e=1
        hi_e=NL if ('up' not in miss) or m in('D','S') else hg
        addel(m,lo_e,hi_e,0.3,P[m])
    names=list(parts)
    adj={n:set() for n in names}
    for A in names:
        for B in names:
            if A==B: continue
            for (alo,ahi,aR,ap) in parts[A]:
                for (blo,bhi,bR,bp) in parts[B]:
                    if blo>ahi and np.linalg.norm(ap-bp)<aR+bR-1e-9:
                        adj[A].add(B)   # A before B
    # cycle nodes: SCC via reachability
    reach={}
    for n in names:
        seen=set(); st=[n]
        while st:
            x=st.pop()
            for y in adj[x]:
                if y not in seen: seen.add(y); st.append(y)
        reach[n]=seen
    cyc=[n for n in names if n in reach[n] or any((n in reach[o] and o in reach[n]) for o in reach[n])]
    cyc=[n for n in names if any(n in reach[o] and o in reach[n] for o in names if o!=n) or n in reach[n]]
    if cyc: add(1.0*len(cyc),('cycle',tuple(cyc)))
    # shaft vs pillars
    for (ms,lo,hi,Rs,ps) in shafts:
        for pc in pillars: add(PIL_R+Rs+0.3-np.linalg.norm(ps-pc),('shaftpil',ms))
    # hands constraints
    dD=np.linalg.norm(P['D']-C); dS=np.linalg.norm(P['S']-C)
    add(6.7-dD,'D near'); add(dD-7.3,'D far')
    add(6.5-dS,'S near'); add(dS-7.0,'S far')
    add(5.9-np.linalg.norm(P['S']-P['D']),'SD')
    # barrel clearance in case
    add(np.linalg.norm(C)-2.6,'barrel case'); add(2.5-np.linalg.norm(C),'cannon arbor')
    return (viol,msgs) if verbose else viol
def pillar_candidates(C):
    out=[]
    for a in np.radians(np.arange(0,360,5)):
        for r in (11.8,):
            p=C+r*np.array([math.cos(a),math.sin(a)])
            if np.linalg.norm(p)>10.4+0.0: out.append(p)
    return out
BOUNDS=[(0,2*math.pi),(2.5,2.6),(0,2*math.pi),(0,2*math.pi),(-1,1),(0,2*math.pi),(0,2*math.pi),(-1,1),(0,2*math.pi),(0,2*math.pi),(0,2*math.pi),(0,2*math.pi),(0,2*math.pi),(0,2*math.pi)]
def rand_v():
    v=[]
    for i,(lo,hi) in enumerate(BOUNDS):
        if i in (4,7): v.append(float(rng.choice([-1,1])))
        else: v.append(float(rng.uniform(lo,hi)))
    return v
def pillars_for(C):
    u=math.atan2(C[1],C[0])
    return [C+11.75*np.array([math.cos(u+math.radians(a)),math.sin(u+math.radians(a))]) for a in PIL_ANG]
PIL_ANG=[105,-105,45,-45]
if __name__=='__main__':
    best=None
    for it in range(int(sys.argv[2]) if len(sys.argv)>2 else 200000):
        L=sample_layers()
        v=rand_v()
        P=positions(v)
        if P is None: continue
        pil=pillars_for(P['C'])
        val=evaluate(P,L,pil)
        if best is None or val<best[0]:
            best=(val,v,L); 
            if val==0: break
    print(best[0])
    pickle.dump(best,open('best_%d.pkl'%seed,'wb'))

def upper_flags(P,L):
    val,msgs=evaluate(P,L,pillars_for(P['C']),True)
    return {m[1][1] for m in msgs if isinstance(m[1],tuple) and m[1][0]=='noup'}
def lower_flags(P,L):
    val,msgs=evaluate(P,L,pillars_for(P['C']),True)
    return {m[1][1] for m in msgs if isinstance(m[1],tuple) and m[1][0]=='nolow'}
