exec(open('/app/scripts/assemble.py').read().split('for n,s in solids.items():')[0])
from scipy.optimize import differential_evolution
from scipy.spatial.transform import Rotation
import time
n='reduction_input';s=solids[n];axis=np.array([*m['mobiles'][n]['axis'],1.05]);ob=solids['lower_bridge']
for angle in [0,3,5,8,12,20,30]:
 def objective(q):
  azi,dx,dy,dz=q
  rot=Rotation.from_rotvec(np.array([np.cos(azi),np.sin(azi),0])*np.deg2rad(angle)).as_matrix()
  T=np.eye(4);T[:3,:3]=rot;T[:3,3]=axis-rot@axis+np.array([dx,dy,dz])
  return k.ivol(k.apply(s,T),ob)
 t=time.time()
 res=differential_evolution(objective,[(0,2*np.pi),(-.5,.5),(-.5,.5),(-.2,.2)],maxiter=40,popsize=8,tol=.01,seed=123,polish=False)
 print('angle',angle,'minimum',res.fun,'params',res.x.tolist(),'seconds',time.time()-t,flush=True)
