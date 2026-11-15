import numpy as np, math, random, json, itertools, sys
from spec import *
C=np.array([0.,0.]); I=np.array([-DCD,0.])
def u(t): return np.array([math.cos(t),math.sin(t)])
LA='ABCD'; LI={c:i for i,c in enumerate(LA)}
MESH={('dd','f1'),('g1','f2'),('g2','f3'),('g3','h'),('p','q'),('r','s'),('s','k1'),('k2','w'),('c','d')}
def meshed(a,b): return (a,b) in MESH or (b,a) in MESH
def build(ang,cl,lay):
    # cl: dict layers of central gears: s,d,dd,p ; lay: g1,g2,g3,k2,r(J.r layer = layer of s)
    X1=C+D['dd']*u(ang[0]); X2=X1+D['g1']*u(ang[1]); X3=X2+D['g2']*u(ang[2]); S=X3+D['g3']*u(ang[3])
    J=C+D['pq']*u(ang[4]); K=C+D['sk']*u(ang[5]); Dm=K+D['kw']*u(ang[6])
    g=[('I',I,tip(40,M['cd']),cl['d'],'c'),
       ('M',C,max(tip(40,M['cd']),tip(48,M['cd6'])),cl['d'],'d'),
       ('M',C,tip(36,M['dd']),cl['dd'],'dd'),
       ('M',C,tip(14,M['pq']),cl['p'],'p'),
       ('H',C,tip(48,M['rs']),cl['s'],'s'),
       ('X1',X1,tip(12,M['dd']),cl['dd'],'f1'),('X1',X1,tip(36,M['g1']),lay[0],'g1'),
       ('X2',X2,tip(12,M['g1']),lay[0],'f2'),('X2',X2,tip(30,M['g2']),lay[1],'g2'),
       ('X3',X3,tip(12,M['g2']),lay[1],'f3'),('X3',X3,tip(32,M['g3']),lay[2],'g3'),
       ('S',S,tip(12,M['g3']),lay[2],'h'),
       ('J',J,tip(42,M['pq']),cl['p'],'q'),('J',J,tip(12,M['rs']),cl['s'],'r'),
       ('K',K,tip(24,M['sk']),cl['s'],'k1'),('K',K,tip(12,M['kw']),lay[3],'k2'),
       ('Dd',Dm,tip(48,M['kw']),lay[3],'w')]
    return g,S,Dm
CENT={'M','H'}
def score(ang,cl,lay,ext=None):
    g,S,Dm=build(ang,cl,lay)
    m=1e9
    for gi in g:
        if gi[4]!='c': m=min(m,12.6-(np.linalg.norm(gi[1])+gi[2]))
    m=min(m,7.0-np.linalg.norm(S)); dn=np.linalg.norm(Dm); m=min(m,dn-6.4,8.6-dn)
    m=min(m,(np.linalg.norm(S-Dm)-9.4)*0.5)
    mobs={}
    for gi in g: mobs.setdefault(gi[0],[]).append(gi)
    for i in range(len(g)):
        for j in range(i+1,len(g)):
            a,b=g[i],g[j]
            if a[0]==b[0]: continue
            if a[3]==b[3] and not meshed(a[4],b[4]):
                m=min(m,np.linalg.norm(a[1]-b[1])-a[2]-b[2]-0.15)
    for mob,gl in mobs.items():
        top=LI['D'] if (mob in CENT or mob in ('S','Dd') or (ext and mob in ext)) else max(LI[x[3]] for x in gl)
        r=0.9 if mob in CENT else 0.5
        if mob=='I': top=LI['D']
        pos=gl[0][1]
        for gi in g:
            if gi[0]==mob or (gi[0] in CENT and mob in CENT): continue
            if LI[gi[3]]<=top:
                d=np.linalg.norm(pos-gi[1])-gi[2]-r-0.12
                # meshed partner of same layer is checked above via mesh; its shaft is inside own gear hub only if same layer
                if gi[3] in [x[3] for x in gl] and any(meshed(gi[4],x[4]) for x in gl if x[3]==gi[3]): continue
                m=min(m,d)
    return m
def opt(cl,lay,rnd,n0=300,n1=300):
    best=(-99,None)
    for _ in range(n0):
        ang=[rnd.uniform(0,2*math.pi) for _ in range(7)]
        s=score(ang,cl,lay)
        if s>best[0]: best=(s,ang)
    s,ang=best; step=0.5
    for it in range(n1):
        a2=[x+rnd.gauss(0,step) for x in ang]
        s2=score(a2,cl,lay)
        if s2>s: s,ang=s2,a2
        if it%100==99: step*=0.5
    return s,ang
if __name__=="__main__":
    rnd=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 0)
    res=[]
    pats=[]
    for hs in ('A','D'):
        pass
    for hs in ('A','D'):
        others=[c for c in LA if c!=hs]
        for perm in itertools.permutations(others):
            pats.append(dict(s=hs,d=perm[0],dd=perm[1],p=perm[2]))
    best=(-99,)
    for ci in range(int(sys.argv[2]) if len(sys.argv)>2 else 400):
        cl=rnd.choice(pats)
        l0=rnd.choice(LA); l0=rnd.choice([x for x in LA if x!=cl['dd']])
        l1=rnd.choice([x for x in LA if x!=l0]); l2=rnd.choice([x for x in LA if x!=l1]); l3=rnd.choice([x for x in LA if x!=cl['s']])
        lay=[l0,l1,l2,l3]
        s,ang=opt(cl,lay,rnd,150,200)
        if s>best[0]:
            best=(s,cl,lay,ang); print(round(s,3),cl,lay,flush=True)
    json.dump([float(best[0]),best[1],best[2],[float(a) for a in best[3]]],open('lay_best_%s.json'%(sys.argv[1] if len(sys.argv)>1 else 0),'w'))
