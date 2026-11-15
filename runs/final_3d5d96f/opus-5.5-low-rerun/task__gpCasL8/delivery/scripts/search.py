from lay import *
import itertools,sys
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 0)
B=np.array([-2.84,0.]);C=np.zeros(2)
G=[('pA','A',1.4,'drum'),('wA','A',4.17,'pX|pX2'),('pX','X',1.42,'wA'),('pX2','X2',1.42,'wA'),('x2m','X2',1.05,'dm1'),
('xs','X',3.525,'y1'),('dm1','DM',1.95,'x2m'),('dm2','DM',1.05,'gM'),('gM','M',1.95,'dm2'),('y1','Y',1.05,'xs'),('y2','Y',3.75,'pS'),('pS','S',1.05,'y2'),
('pA2','A2',2.6,'drum'),('aq','A2',1.275,'q1'),('q1','Q',3.75,'aq'),('q2','Q',1.75,'dh1'),('dh1','DH',3.25,'q2'),('dh','DH',2.25,'gH|gT'),('gH','H',2.25,'dh'),('gT','T',4.2,'dh')]
CEN={'M','H'}
def build(p):
    phA,phA2,thm,sx2,psx,psy,thh,st,sq=p
    P={}
    P['A']=B+pol(10.8,phA);P['A2']=B+pol(12.0,phA2)
    P['DM']=pol(2.7,thm);P['X2']=circ(P['A'],5.0,P['DM'],2.7,sx2)
    P['X']=P['A']+pol(5.0,psx);P['Y']=P['X']+pol(4.275,psy)
    # S: on circle around Y radius 4.5 with |S|=6.0
    P['S']=circ(C,6.2,P['Y'],4.5,st)
    P['DH']=pol(3.9,thh);P['T']=circ(C,8.35,P['DH'],5.85,st if False else sq)
    P['Q']=circ(P['A2'],4.5,P['DH'],4.5,-sq)
    P['M']=C;P['H']=C
    return P
def score(P):
    bad=0;m=9
    for k in('A2',):
        if np.linalg.norm(P[k])>10.0: bad+=np.linalg.norm(P[k])-10
    for g,mo,r,mate in G:
        c=P[mo]
        e=12.6-(np.linalg.norm(c)+r); m=min(m,e*3)
        if e<0: bad-=e
        for m2,c2 in P.items():
            if m2==mo or (mo in CEN and m2 in CEN): continue
            if m2 in CEN: ar=0.65 if g not in('gM','gH') else 0
            else: ar=0.4
            if g in('gM','gH') and m2 in CEN: continue
            d=np.linalg.norm(c-c2)-r-ar
            m=min(m,d)
            if d<0.05: bad+=0.05-d
        if mo not in CEN and g not in('pA','pA2'):
            d=np.linalg.norm(c-B)-r-(0.5 if g in ('gM','gH') else 1.0)
            if d<0.05: bad+=0.05-d
            m=min(m,d)
    # arbors vs post
    for mo,c in P.items():
        if mo in CEN: continue
        d=np.linalg.norm(c-B)-0.4-1.0
        if d<0.05: bad+=0.05-d
    # drum pinions vs each other
    d=np.linalg.norm(P['A']-P['A2'])-1.4-2.6
    if d<0.1: bad+=0.1-d
    # S hand clearance
    s=np.linalg.norm(P['S'])
    # T must be >=8.35
    return bad,m
if __name__=="__main__":
  pass
best=None
for it in (range(200000) if __name__=="__main__" else []):
    p=[rng.uniform(5,80),rng.uniform(-40,-5),rng.uniform(0,360),rng.choice([-1,1]),rng.uniform(0,360),rng.uniform(0,360),rng.uniform(0,360),rng.choice([-1,1]),rng.choice([-1,1])]
    try: P=build(p)
    except Exception: continue
    b,m=score(P)
    key=(b,-m)
    if best is None or key<best[0]:
        best=(key,p);print(it,key,np.round(p,2).tolist(),flush=True)
