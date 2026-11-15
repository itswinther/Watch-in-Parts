import math
# ---- global numbers ----
ZB0=-0.4545454   # lowest
# layer z ranges (bottom, top)
GT=0.25
LAYERS={'A':(2.62,2.87),'B':(2.94,3.19),'C':(3.26,3.51),'D':(3.58,3.83)}
MP=(2.29,2.5455)
TP=(3.90,4.15)
PL=(-0.4545,-0.10)
DRUM=(0.0,0.4545)
H1=(4.45,4.70); H2=(4.75,5.00); H3=(5.05,5.30)
DCD=8.2          # I - C distance
BI=10.8
def tip(z,m): return m*(z/2+1)
def pr(z,m): return m*z/2
# meshes: name -> (driver gear, driven gear, module)  tooth counts
T=dict(a=12,c=40,d=40,c6=36,d6=48,dd=36,f1=12,g1=36,f2=12,g2=30,f3=12,g3=32,h=12,
       p=14,q=42,r=12,s=48,k1=24,k2=12,w=48)
M=dict(cd=2*DCD/80, cd6=2*DCD/84, dd=0.2, g1=0.15, g2=0.16, g3=0.16, pq=5.8/28, rs=5.8/30, sk=5.8/30, kw=0.16)
def dist(zt1,zt2,m): return m*(zt1+zt2)/2
D=dict(dd=dist(36,12,M['dd']), g1=dist(36,12,M['g1']), g2=dist(30,12,M['g2']), g3=dist(32,12,M['g3']),
       pq=dist(14,42,M['pq']), rs=dist(12,48,M['rs']), sk=dist(48,24,M['sk']), kw=dist(12,48,M['kw']))
if __name__=="__main__":
    print(D, abs(D['pq']-D['rs']))
