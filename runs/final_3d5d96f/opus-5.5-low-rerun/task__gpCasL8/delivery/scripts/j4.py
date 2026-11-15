from j3 import *
from scipy.optimize import differential_evolution
bounds=[(0,90),(-40,0)]+[(0,360)]*8+[(ZMIN,ZMAX-TH[k]) for k in FREE]
seed=int(sys.argv[1])
best=[1e9]
def cb(xk,convergence=None):
    v=F3(xk)
    if v<best[0]-1e-4:
        best[0]=v;print(round(v,4),np.round(xk,3).tolist(),flush=True)
r=differential_evolution(F3,bounds,seed=seed,maxiter=1500,popsize=30,tol=1e-12,mutation=(0.5,1.0),recombination=0.9,polish=False,callback=cb)
print('final',round(r.fun,4),np.round(r.x,3).tolist(),flush=True)
