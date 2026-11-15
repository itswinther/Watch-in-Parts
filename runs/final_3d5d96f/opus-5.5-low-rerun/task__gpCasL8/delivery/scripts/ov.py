from opt import *
P=build2([25.44, -9.29, 3.98, 140.7, 176.21, 6.6, 288.5],[-1,1,-1])
for (g1,m1,r1,mt1),(g2,m2,r2,mt2) in itertools.combinations(G,2):
    if m1==m2: continue
    d=np.linalg.norm(P[m1]-P[m2])
    if d<r1+r2+0.05:
        mesh = g2 in mt1.split('|') or g1 in mt2.split('|')
        print(g1,g2,'MESH' if mesh else '', round(d,3))
for g,mo,r,mate in G:
    print(g, 'distB',round(np.linalg.norm(P[mo]-B)-r,2))
