import numpy as np, math, random, json
from spec import *
C=np.array([0.,0.]); I=np.array([-DCD,0.])
def u(t): return np.array([math.cos(t),math.sin(t)])
LA='ABCD'
def build(ang,lay):
    X1=C+D['dd']*u(ang[0]); X2=X1+D['g1']*u(ang[1]); X3=X2+D['g2']*u(ang[2]); S=X3+D['g3']*u(ang[3])
    J=C+D['pq']*u(ang[4]); K=C+D['sk']*u(ang[5]); Dm=K+D['kw']*u(ang[6])
    # gears: (mobile, pos, tip, layer, key)
    g=[('I',I,tip(40,M['cd']),'A','c'),
       ('M',C,max(tip(40,M['cd']),tip(48,M['cd6'])),'A','d'),
       ('M',C,tip(36,M['dd']),'B','dd'),
       ('M',C,tip(12,M['pq']),'C','p'),
       ('H',C,tip(48,M['rs']),'D','s'),
       ('X1',X1,tip(12,M['dd']),'B','f1'),('X1',X1,tip(36,M['g1']),lay[0],'g1'),
       ('X2',X2,tip(12,M['g1']),lay[0],'f2'),('X2',X2,tip(30,M['g2']),lay[1],'g2'),
       ('X3',X3,tip(12,M['g2']),lay[1],'f3'),('X3',X3,tip(32,M['g3']),lay[2],'g3'),
       ('S',S,tip(12,M['g3']),lay[2],'h'),
       ('J',J,tip(36,M['pq']),'C','q'),('J',J,tip(12,M['rs']),'D','r'),
       ('K',K,tip(48,M['sk']),'D','k1'),('K',K,tip(12,M['kw']),lay[3],'k2'),
       ('Dd',Dm,tip(24,M['kw']),lay[3],'w')]
    sh=[('I',I,0.6),('M',C,0.95),('X1',X1,0.5),('X2',X2,0.5),('X3',X3,0.5),('S',S,0.5),('J',J,0.5),('K',K,0.5),('Dd',Dm,0.5)]
    return g,sh,S,Dm
MESH={('dd','f1'),('g1','f2'),('g2','f3'),('g3','h'),('p','q'),('r','s'),('s','k1'),('k2','w'),('c','d')}
def meshed(a,b): return (a,b) in MESH or (b,a) in MESH
def score(ang,lay):
    g,sh,S,Dm=build(ang,lay)
    m=1e9
    for gi in g:
        m=min(m,12.45-(np.linalg.norm(gi[1])+gi[2]))
    m=min(m,7.0-np.linalg.norm(S)); 
    dn=np.linalg.norm(Dm); m=min(m,dn-6.4, 9.0-dn)
    m=min(m,(np.linalg.norm(S-Dm)-9.4)*0.5)
    for i in range(len(g)):
        for j in range(i+1,len(g)):
            a,b=g[i],g[j]
            if a[0]==b[0]: continue
            d=np.linalg.norm(a[1]-b[1])
            if a[3]==b[3] and not meshed(a[4],b[4]):
                m=min(m,d-a[2]-b[2]-0.15)
    for (mob,p,r) in sh:
        for gi in g:
            if gi[0]==mob: continue
            if meshed_mob(mob,gi): continue
            d=np.linalg.norm(p-gi[1]); m=min(m,d-gi[2]-r-0.12)
    return m
def meshed_mob(mob,gi): return False
def solve(n=200000,seed=1):
    rnd=random.Random(seed); best=(-9,None)
    for it in range(n):
        ang=[rnd.uniform(0,2*math.pi) for _ in range(7)]
        l0=rnd.choice('ACD'); l1=rnd.choice([x for x in LA if x!=l0]); l2=rnd.choice([x for x in LA if x!=l1]); l3=rnd.choice('ABC')
        lay=[l0,l1,l2,l3]
        s=score(ang,lay)
        if s>best[0]: best=(s,(ang,lay)); 
    return best
if __name__=="__main__":
    b=solve(60000)
    print(b)
