from lay import *
import itertools
B=np.array([-2.84,0.])
C=np.array([0.,0.])
def ang(p): return np.degrees(np.arctan2(p[1],p[0]))
phA,phA2=25,-30
A=B+pol(10.8,phA); A2=B+pol(12.0,phA2)
th_h=-60
DH=pol(3.9,th_h); T=pol(8.35,th_h-38.9)
Q=circ(A2,4.5,DH,4.5,+1)
th_m=60; DM=pol(2.7,th_m)
X=circ(A,5.0,DM,2.7,+1)
S=pol(5.7,100)
Y=circ(X,4.275,S,4.5,+1)
P=dict(A=A,A2=A2,DH=DH,T=T,Q=Q,DM=DM,X=X,S=S,Y=Y,M=C,H=C)
for k,v in P.items(): print(k,np.round(v,3),round(np.linalg.norm(v),3), 'fromB',round(np.linalg.norm(v-B),3))
# gears: name, mobile, tip radius, mate
G=[('pA','A',1.4,'drum'),('wA','A',4.17,'pX'),('pX','X',1.42,'wA'),('xm','X',1.05,'dm1'),('xs','X',3.525,'y1'),
('dm1','DM',1.95,'xm'),('dm2','DM',1.05,'gM'),('gM','M',1.95,'dm2'),('y1','Y',1.05,'xs'),('y2','Y',3.75,'pS'),('pS','S',1.05,'y2'),
('pA2','A2',2.6,'drum'),('aq','A2',1.275,'q1'),('q1','Q',3.75,'aq'),('q2','Q',1.75,'dh1'),('dh1','DH',3.25,'q2'),('dh','DH',2.25,'gH|gT'),('gH','H',2.25,'dh'),('gT','T',4.2,'dh')]
AR=0.35
for g,m,r,mate in G:
    c=P[m]
    if np.linalg.norm(c)+r>12.6: print('CASE',g)
    for m2,c2 in P.items():
        if m2==m or (m in 'MH' and m2 in 'MH'): continue
        d=np.linalg.norm(c-c2)
        if d<r+AR+0.05: print('ARBOR',g,'covers',m2,round(d-r-AR,3))
    db=np.linalg.norm(c-B)
    if db<r+0.5+0.05: print('POST0.5',g,round(db-r-0.5,3))
    elif db<r+0.99+0.05: print('POSTsq',g,round(db-r-0.99,3))
    if db<r+9.8+0.05: pass
    else: print('outside drum ok:',g)
print('--- plan overlaps (need different layers)')
for (g1,m1,r1,mt1),(g2,m2,r2,mt2) in itertools.combinations(G,2):
    if m1==m2: continue
    d=np.linalg.norm(P[m1]-P[m2])
    if d<r1+r2+0.05:
        mesh = g2 in mt1.split('|') or g1 in mt2.split('|')
        print(g1,g2,'MESH' if mesh else '', round(d,3))
