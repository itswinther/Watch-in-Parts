import numpy as np, itertools
from geom import *
def gears_all():
    g=[(I,tip(40,M['cd']),0.5),(C,max(tip(40,M['cd']),tip(48,M['cd6'])),0.9),(C,tip(36,M['dd']),0),(C,tip(14,M['pq']),0),(C,tip(48,M['rs']),0),
       (X1,tip(12,M['dd']),0.5),(X1,tip(36,M['g1']),0),(X2,tip(12,M['g1']),0),(X2,tip(30,M['g2']),0),(X3,tip(12,M['g2']),0),(X3,tip(32,M['g3']),0),(S,tip(12,M['g3']),0.5),
       (J,tip(42,M['pq']),0.5),(J,tip(12,M['rs']),0),(K,tip(24,M['sk']),0.5),(K,tip(12,M['kw']),0),(DD,tip(48,M['kw']),0.5)]
    return g
G=gears_all()
def free_post(p,margin=0.35,r=0.5):
    if np.hypot(*p)>12.0: return False
    for pos,t,c in G:
        if np.hypot(*(p-pos))<t+r+margin: return False
    return True
def free_pillar(p,r=0.6):
    if np.hypot(*p)>12.0: return False
    if np.hypot(*(p-POS['B']))<9.8+r+0.3: return False
    if np.hypot(*(p-I))<1.6+r+0.3: return False
    if np.hypot(*(p-I))<0.5+r+0.3: return False
    return True
def pick(fn):
    pts=[np.array([x,y]) for x in np.arange(-12,12.01,0.25) for y in np.arange(-12,12.01,0.25) if fn(np.array([x,y]))]
    print(len(pts))
    best=None
    pts=np.array(pts)
    if len(pts)<3: return None
    import random
    rnd=random.Random(1)
    for _ in range(40000):
        a,b,c=[pts[rnd.randrange(len(pts))] for _ in range(3)]
        area=abs((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]))/2
        if best is None or area>best[0]: best=(area,[a,b,c])
    return best
if __name__=="__main__":
    print(pick(free_post)); print(pick(free_pillar))
