import math, itertools, random, sys, json
def P(c,r,ang): return (c[0]+r*math.cos(math.radians(ang)), c[1]+r*math.sin(math.radians(ang)))
def cc(c1,r1,c2,r2,sign=1):
    d=math.dist(c1,c2)
    if d>r1+r2-1e-9 or d<abs(r1-r2)+1e-9: return None
    a=(r1*r1-r2*r2+d*d)/(2*d); h=math.sqrt(max(0,r1*r1-a*a))
    ex=((c2[0]-c1[0])/d,(c2[1]-c1[1])/d)
    return (c1[0]+a*ex[0]-sign*h*ex[1], c1[1]+a*ex[1]+sign*h*ex[0])
C=(0.0,0.0); A0=(-2.85,0.0); CASE=12.65
def tip(m,z): return m*(z+2)/2
BODY=(0.7645,2.227)
ZI=14  # idler teeth
def build(p):
    pos={'MIN':C,'HOUR':C}
    pos['M2']=P(A0,11.4,p['t2'])
    pos['X']=P(C,3.6,p['fx'])
    y=cc(pos['M2'],0.33*14,pos['X'],4.5,p['sy'])
    if y is None: return None
    pos['Y']=y
    pos['M3']=P(pos['M2'],0.23*40/2,p['t3'])
    pos['M4']=P(pos['M3'],0.19*48/2,p['t4'])
    pos['S']=P(pos['M4'],4.4,p['ts'])
    pos['MW']=P(C,4.0,p['fmw'])
    pos['I']=P(C,0.1*(14+p['zi']),p['fi'])
    pos['D']=P(pos['I'],0.1*(p['zi']+28),p['fd'])
    return pos
def features(p):
    lv=p['lv']; F=[]
    def g(mob,name,m,z,zr): F.append((mob,name,tip(m,z),tuple(zr)))
    for mob in ['M2','X','Y','M3','M4','S','MW','I','D']:
        F.append((mob,'arb',0.33,BODY))
    F.append(('MIN','pipe',0.66,BODY)); g('MIN','GM',0.3,12,(0.7645,1.1645)); g('MIN','c',0.2,10,(1.1645,1.4445))
    F.append(('IP','ip',1.6,(1.4745,1.7245)))
    g('HOUR','col',0.2,14,(1.927,2.227)); F.append(('HOUR','pipe',1.03,(1.6945,2.227)))
    g('MW','Wmw',0.2,30,(1.1945,1.4445)); F.append(('MW','collar',1.3,(1.9,2.227)))
    g('I','I',0.2,p['zi'],(1.927,2.227)); g('D','WD',0.2,28,(1.927,2.227))
    g('X','zX',0.3,12,(0.7645,1.1645)); g('Y','Ydr',0.3,18,(0.7645,1.1645))
    g('M2','G2',0.33,14,lv['g2']); g('Y','Yd',0.33,16,lv['g2'])
    g('M2','W2',0.24,32,lv['w2']); g('M3','p3',0.24,10,lv['w2'])
    g('M3','W3',0.2,40,lv['w3']); g('M4','p4',0.2,8,lv['w3'])
    g('M4','W4',0.2,36,lv['w4']); g('S','pS',0.2,8,lv['w4'])
    return F
MESH={frozenset(x) for x in [('GM','zX'),('zX','Ydr'),('c','Wmw'),('col','I'),('I','WD'),('G2','Yd'),('W2','p3'),('W3','p4'),('W4','pS')]}
def zov(a,b,gap=0.03): return a[0] < b[1]+gap-1e-9 and b[0] < a[1]+gap-1e-9
def evaluate(p,verbose=False):
    pos=build(p)
    if pos is None: return 1e9,None
    pos['IP']=C
    F=features(p); bad=0.0; msgs=[]
    for A,B in itertools.combinations(F,2):
        if A[0]==B[0] or {A[0],B[0]}<= {'MIN','HOUR','IP'}: continue
        if not zov(A[3],B[3]): continue
        if frozenset((A[1],B[1])) in MESH: continue
        d=math.dist(pos[A[0]],pos[B[0]]); need=A[2]+B[2]+0.05
        if d<need: bad+=need-d; msgs.append((A[0],A[1],B[0],B[1],round(need-d,3)))
    for f in F:
        c=pos[f[0]]; d=math.dist(c,C)+f[2]
        if d>CASE: bad+=d-CASE; msgs.append(('case',f[0],f[1],round(d-CASE,3)))
        db=math.dist(c,A0)
        for (z0,z1,rr) in ((0.4545,1.5,0.5),(1.5,2.227,0.99)):
            if zov(f[3],(z0,z1)) and db<rr+f[2]+0.05:
                bad+=rr+f[2]+0.05-db; msgs.append(('barrel',f[0],f[1],round(rr+f[2]+0.05-db,3)))
    d=math.dist(pos['M2'],C)+tip(0.2,18)
    if d>CASE: bad+=d-CASE
    # above top bridge: H r3.4 at C, MW pinion tip 1.0; S and D pipes r 0.6 must avoid
    for k in ('S','D'):
        dd=math.dist(pos[k],C)
        if dd<3.4+0.6+0.05: bad+=3.4+0.65-dd; msgs.append((k,'vs H'))
        dm=math.dist(pos[k],pos['MW'])
        if dm<1.0+0.6+0.05: bad+=1.65-dm; msgs.append((k,'vs MWp'))
    hs=5.3; hd=3.3
    dS=math.dist(pos['S'],C); dD=math.dist(pos['D'],C)
    if dS+hs>12.45: bad+=dS+hs-12.45; msgs.append(('S hand out',round(dS,2)))
    if dD<6.05: bad+=6.05-dD; msgs.append(('D<6',round(dD,2)))
    if dD+hd>12.45: bad+=dD+hd-12.45; msgs.append(('D hand out',))
    dsd=math.dist(pos['S'],pos['D'])
    if dsd<hs+hd+0.4: bad+=hs+hd+0.4-dsd; msgs.append(('SD',round(dsd,2)))
    if dS-hs<1.4: bad+=1.4-(dS-hs); msgs.append(('S hand centre',))
    if verbose:
        for m in msgs: print(m)
    return bad,pos
LZ=[(0.7645,1.1645),(0.7645,1.2645),(1.1945,1.5945),(1.4745,1.8745),(1.4745,1.9445),(1.6,2.0),(1.827,2.227),(1.927,2.227),(1.1945,1.4445),(0.7645,1.0145)]
LVOPT=dict(g2=LZ, w2=LZ, w3=LZ, w4=LZ)
def rand_p():
    return dict(t2=random.uniform(-15,15), fx=random.uniform(-180,180), sy=random.choice([1,-1]),
        t3=random.uniform(-180,180), t4=random.uniform(-180,180), ts=random.uniform(-180,180),
        fmw=random.uniform(-180,180), fi=random.uniform(-180,180), fd=random.uniform(-180,180), zi=random.choice([12,14,16,18,20]),
        lv={k:random.choice(v) for k,v in LVOPT.items()})
def mutate(p,T):
    q=json.loads(json.dumps(p)); k=random.choice(list(q.keys()))
    if k=='lv':
        kk=random.choice(list(LVOPT)); q['lv'][kk]=random.choice(LVOPT[kk])
    elif k=='sy': q[k]=-q[k]
    elif k=='zi': q[k]=random.choice([12,14,16,18,20])
    else: q[k]+=random.gauss(0,T)
    q['t2']=max(-15,min(15,q['t2']))
    return q
if __name__=='__main__':
    seed=int(sys.argv[1]) if len(sys.argv)>1 else 0
    random.seed(seed); best=None
    for restart in range(60):
        p=rand_p(); b,_=evaluate(p)
        while b>=1e9: p=rand_p(); b,_=evaluate(p)
        T=30.0
        for it in range(5000):
            q=mutate(p,T); bq,_=evaluate(q)
            if bq<=b or random.random()<math.exp(-(bq-b)/max(1e-3,T/30)): p,b=q,bq
            T=max(0.3,T*0.999)
            if b==0: break
        if best is None or b<best[0]: best=(b,p); print('restart',restart,'best',round(b,3),flush=True)
        if best[0]==0: break
    b,p=best
    print(json.dumps(p)); bb,pos=evaluate(p,True)
    for k,v in pos.items(): print(k,'(%.3f, %.3f) dC %.2f'%(v[0],v[1],math.dist(v,C)))
