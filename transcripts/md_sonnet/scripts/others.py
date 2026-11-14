import sys; sys.path.insert(0,'scripts')
from lib import *
import pickle,time
def Q(R,t): return np.concatenate([t,Rot.from_matrix(R[:3,:3]).as_rotvec()])
I=np.eye(4)
out={}
def chain(pl,wps,lo,hi,iters=20000):
    path=[wps[0]]
    for a,b in zip(wps[:-1],wps[1:]):
        r=pl.rrt(a,b,lo,hi,iters=iters,ext=15)
        assert r is not None,'fail'
        path+=pl.smooth(r,300)[1:]
    return pl.dense(path)
which=sys.argv[1]
lo=np.array([-450,0,-100]);hi=np.array([900,860,300])
if which=='chest':
    pl=Planner('chest')
    out=chain(pl,[Q(I,[-200,650,0]),Q(I,[63,650,0]),Q(I,[63,400,0])],lo,hi)
if which=='bookcase':
    pl=Planner('bookcase')
    out=chain(pl,[Q(I,[-200,640,0]),Q(I,[100,640,0]),Q(I,[100,595,0]),Q(I,[400,595,0])],lo,hi)
if which=='wardrobe':
    pl=Planner('wardrobe',seed=3)
    ry=md.rot('y',90);rx=md.rot('x',90)
    W0=Q(ry,[-300,650,60]);W1=Q(ry,[0,650,60])
    W2=Q(rx,[73,640,0]);W3=Q(rx,[73,440,0])
    fin=Q(inst.final('wardrobe'),[0,0,0]); fin[:3]=inst.final('wardrobe')[:3,3]
    for n,w in zip('W0 W1 W2 W3 fin'.split(),[W0,W1,W2,W3,fin]): print(n,pl.valid(w))
    out=chain(pl,[W0,W1,W2,W3,fin],lo,hi,iters=40000)
pickle.dump(out,open('work/%s.pkl'%which,'wb'));print(which,len(out))
