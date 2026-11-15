import math, itertools, random, sys, json
from plan4 import P, cc, C, A0, CASE, tip, BODY, build as build4
def build(p):
    pos=build4(p)
    if pos is None: return None
    for i in range(3):
        pos['PIL%d'%i]=P(C,p['pr%d'%i],p['pa%d'%i])
    pos['IPP']=P(C,p['ipr'],p['ipa'])
    return pos
T2=0.08; TA=0.10
def features(p):
    lv=p['lv']; F=[]
    def g(mob,name,m,z,zr): F.append((mob,name,tip(m,z),tuple(zr)))
    for mob in ['M2','X','Y','M3','M4','S','MW','I','D']:
        F.append((mob,'arb',0.33,BODY))
    F.append(('MIN','pipe',0.66,BODY)); g('MIN','GM',0.3,12,(0.7645,1.1645)); g('MIN','c',0.2,10,(1.1645,1.4445))
    F.append(('IP','ip',1.6,(1.4745,1.7245)))
    g('HOUR','col',0.2,14,(1.927,2.227)); F.append(('HOUR','pipe',1.03,(1.7545,2.227)))
    g('MW','Wmw',0.2,30,(1.1945,1.4445)); F.append(('MW','collar',1.3,(1.9,2.227)))
    g('I','I',0.2,p['zi'],(1.927,2.227)); g('D','WD',0.2,28,(1.927,2.227))
    g('X','zX',0.3,12,(0.7645,1.1645)); g('Y','Ydr',0.3,18,(0.7645,1.1645))
    g('M2','G2',0.33,14,lv['g2']); g('Y','Yd',0.33,16,lv['g2'])
    g('M2','W2',0.23,32,lv['w2']); g('M3','p3',0.23,10,lv['w2'])
    g('M3','W3',0.19,40,lv['w3']); g('M4','p4',0.19,8,lv['w3'])
    g('M4','W4',0.2,36,lv['w4']); g('S','pS',0.2,8,lv['w4'])
    for i in range(3): F.append(('PIL%d'%i,'pil',0.6,BODY))
    F.append(('IPP','pil',0.5,(0.7645,1.7245)))
    return F
MESH={frozenset(x) for x in [('GM','zX'),('zX','Ydr'),('c','Wmw'),('col','I'),('I','WD'),('G2','Yd'),('W2','p3'),('W3','p4'),('W4','pS')]}
FIXED={'IP','PIL0','PIL1','PIL2','IPP'}
def zov(a,b,gap=0.03): return a[0] < b[1]+gap-1e-9 and b[0] < a[1]+gap-1e-9
def segdist(p,a,b):
    ax,ay=a; bx,by=b; px,py=p; dx,dy=bx-ax,by-ay; L=dx*dx+dy*dy
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L)) if L>0 else 0
    return math.hypot(ax+t*dx-px, ay+t*dy-py)
def order_ok(F,pos):
    mobs=sorted({f[0] for f in F if f[0] not in FIXED and f[0] not in ('MIN','HOUR')}|{'MIN'})
    # MIN/HOUR special; just check mobiles pairwise
    must={}  # (A,B): A must be before B
    bad=0
    for A,B in itertools.combinations(mobs,2):
        a_after_b=True; b_after_a=True
        for fa in F:
            if fa[0]!=A: continue
            for fb in F:
                if fb[0]!=B: continue
                if frozenset((fa[1],fb[1])) in MESH: continue
                d=math.dist(pos[A],pos[B])
                if d>=fa[2]+fb[2]+0.02: continue
                if not (fb[3][1] <= fa[3][0]+1e-9): a_after_b=False
                if not (fa[3][1] <= fb[3][0]+1e-9): b_after_a=False
        if not a_after_b and not b_after_a: bad+=1
        elif not a_after_b: must[(A,B)]=1
        elif not b_after_a: must[(B,A)]=1
    # cycle check
    import collections
    adj=collections.defaultdict(list)
    for (a,b) in must: adj[a].append(b)
    color={}
    def dfs(u):
        color[u]=1
        for v in adj[u]:
            if color.get(v)==1: return True
            if color.get(v) is None and dfs(v): return True
        color[u]=2; return False
    for u in mobs:
        if color.get(u) is None and dfs(u): bad+=1
    return bad,must
def evaluate(p,verbose=False):
    pos=build(p)
    if pos is None: return 1e9,None
    pos['IP']=C
    F=features(p); bad=0.0; msgs=[]
    for A,B in itertools.combinations(F,2):
        if A[0]==B[0] or {A[0],B[0]}<= {'MIN','HOUR','IP'}: continue
        if A[0] in FIXED and B[0] in FIXED: continue
        if {A[0],B[0]}=={'IP','IPP'}: continue
        if not zov(A[3],B[3]): continue
        if frozenset((A[1],B[1])) in MESH: continue
        d=math.dist(pos[A[0]],pos[B[0]])
        tol=TA if ('arb' in (A[1],B[1]) or 'pil' in (A[1],B[1])) else T2
        need=A[2]+B[2]+tol
        if d<need: bad+=need-d; msgs.append((A[0],A[1],B[0],B[1],round(need-d,3)))
    # IP arm: segment C->IPP width 0.8 at IP level
    for f in F:
        if f[0] in FIXED or f[0] in ('MIN','HOUR'): continue
        if zov(f[3],(1.4745,1.7245)):
            d=segdist(pos[f[0]],C,pos['IPP'])
            need=f[2]+0.4+0.08
            if d<need: bad+=need-d; msgs.append(('IParm',f[0],f[1],round(need-d,3)))
    for f in F:
        c=pos[f[0]]; d=math.dist(c,C)+f[2]
        lim=CASE-0.1 if f[0].startswith('PIL') else CASE
        if d>lim: bad+=d-lim; msgs.append(('case',f[0],f[1],round(d-lim,3)))
        db=math.dist(c,A0)
        for (z0,z1,rr) in ((0.4545,1.5,0.5),(1.5,2.227,0.99)):
            if zov(f[3],(z0,z1)) and db<rr+f[2]+0.08:
                bad+=rr+f[2]+0.08-db; msgs.append(('barrel',f[0],f[1],round(rr+f[2]+0.08-db,3)))
    d=math.dist(pos['M2'],C)+tip(0.2,18)
    if d>CASE-0.1: bad+=d-CASE+0.1
    for f in F:
        if f[0] in FIXED or f[3][0] >= 1.5: continue
        c=pos[f[0]]; dx=c[0]-A0[0]; dy=c[1]-A0[1]; dd=math.hypot(dx,dy)
        ext=0.7/max(abs(dx)/dd,abs(dy)/dd)
        need=f[2]+ext+0.05
        if dd<need: bad+=need-dd; msgs.append(('square-insert',f[0],f[1],round(need-dd,3)))
    for k in ('S','D'):
        dd=math.dist(pos[k],C)
        if dd<3.4+0.6+0.08: bad+=3.4+0.68-dd; msgs.append((k,'vs H'))
        dm=math.dist(pos[k],pos['MW'])
        if dm<1.0+0.6+0.08: bad+=1.68-dm; msgs.append((k,'vs MWp'))
    hs=5.3; hd=3.3
    dS=math.dist(pos['S'],C); dD=math.dist(pos['D'],C)
    if dS+hs>12.45: bad+=dS+hs-12.45; msgs.append(('S hand out',round(dS,2)))
    if dD<6.1: bad+=6.1-dD; msgs.append(('D<6',round(dD,2)))
    if dD+hd>12.45: bad+=dD+hd-12.45; msgs.append(('D hand out',))
    dsd=math.dist(pos['S'],pos['D'])
    if dsd<hs+hd+0.5: bad+=hs+hd+0.5-dsd; msgs.append(('SD',round(dsd,2)))
    if dS-hs<1.4: bad+=1.4-(dS-hs); msgs.append(('S hand centre',))
    # pillars spread: pairwise angle >= 70 deg
    angs=sorted(math.degrees(math.atan2(pos['PIL%d'%i][1],pos['PIL%d'%i][0]))%360 for i in range(3))
    gaps=[(angs[(i+1)%3]-angs[i])%360 for i in range(3)]
    if max(gaps)>170: bad+=(max(gaps)-170)/50; msgs.append(('pillar spread',gaps))
    ob,must=order_ok(F,pos)
    if ob: bad+=ob*0.5; msgs.append(('order',ob))
    if verbose:
        for m in msgs: print(m)
        print('order constraints',sorted(must))
    return bad,pos
LZ4=[(0.7645,1.1645),(0.7645,1.2645),(1.1945,1.5945),(1.4745,1.8745),(1.4745,1.9445),(1.6,2.0),(1.827,2.227),(1.727,2.227)]
LZ2=LZ4+[(1.927,2.227),(1.1945,1.4445),(0.7645,1.0145),(1.4745,1.7245),(1.6,1.85)]
LZ3=[(0.7645,1.0145),(1.0945,1.3445),(1.1945,1.4445),(0.7645,1.1645),(1.4745,1.7245),(1.6,1.85),(1.927,2.227),(1.827,2.227)]
LVOPT=dict(g2=[(1.3945,1.7945)], w2=[(1.827,2.227)], w3=LZ3, w4=LZ3)
def rand_p():
    p=dict(t2=random.uniform(-15,15), fx=random.uniform(-180,180), sy=random.choice([1,-1]),
        t3=random.uniform(-180,180), t4=random.uniform(-180,180), ts=random.uniform(-180,180),
        fmw=random.uniform(-180,180), fi=random.uniform(-180,180), fd=random.uniform(-180,180), zi=random.choice([12,14,16,18,20]),
        ipr=random.uniform(2.2,4.5), ipa=random.uniform(-180,180),
        lv={k:random.choice(v) for k,v in LVOPT.items()})
    for i in range(3): p['pr%d'%i]=random.uniform(9,11.9); p['pa%d'%i]=random.uniform(-180,180)
    return p
def mutate(p,T):
    q=json.loads(json.dumps(p)); k=random.choice(list(q.keys()))
    if k=='lv':
        kk=random.choice(list(LVOPT)); q['lv'][kk]=random.choice(LVOPT[kk])
    elif k=='sy': q[k]=-q[k]
    elif k=='zi': q[k]=random.choice([12,14,16,18,20])
    elif k.startswith('pr') or k=='ipr': q[k]+=random.gauss(0,T/30)
    else: q[k]+=random.gauss(0,T)
    q['t2']=max(-15,min(15,q['t2']))
    for i in range(3): q['pr%d'%i]=max(8,min(11.95,q['pr%d'%i]))
    q['ipr']=max(2.0,min(5,q['ipr']))
    return q
if __name__=='__main__':
    seed=int(sys.argv[1]) if len(sys.argv)>1 else 0
    random.seed(seed); best=None
    init=json.load(open(sys.argv[2])) if len(sys.argv)>2 else None
    for restart in range(80):
        p=rand_p() if init is None or restart>0 else init
        b,_=evaluate(p)
        while b>=1e9: p=rand_p(); b,_=evaluate(p)
        T=30.0
        for it in range(6000):
            q=mutate(p,T); bq,_=evaluate(q)
            if bq<=b or random.random()<math.exp(-(bq-b)/max(1e-3,T/30)): p,b=q,bq
            T=max(0.3,T*0.999)
            if b==0: break
        if best is None or b<best[0]: best=(b,p); print('restart',restart,'best',round(b,3),flush=True)
        if best[0]==0: break
    b,p=best
    print(json.dumps(p)); bb,pos=evaluate(p,True)
    for k,v in pos.items(): print(k,'(%.3f, %.3f) dC %.2f'%(v[0],v[1],math.dist(v,C)))
