import sys; sys.path.insert(0,'scripts')
from lib import *
import pickle,time
pl=Planner('sofa',seed=1)
def Q(R,t): return np.concatenate([t,Rot.from_matrix(R[:3,:3]).as_rotvec()])
roll=md.rot('x',90)
# stage: start outside, roll, y centre 673 (range 633..713 -> ty=713)
start=Q(roll,[-300,713,0])
wp1=Q(roll,[420,713,0])   # in corridor east
print(pl.valid(start),pl.valid(wp1))
print('straight',pl.edge_ok(start,wp1))
final=Q(np.eye(4),[520,40,0])
t0=time.time()
lo=np.array([300,0,-100]);hi=np.array([900,740,280])
path=pl.rrt(wp1,final,lo,hi,iters=30000,ext=20)
print('rrt',None if path is None else len(path),time.time()-t0)
if path:
    path=pl.smooth(path,400)
    pickle.dump(path,open('work/sofa_mid.pkl','wb'));print(len(path))
