import numpy as np
from scipy.optimize import minimize
def P(a,d,base=(0,0)): return np.array(base)+d*np.array([np.cos(a),np.sin(a)])
A=np.radians(np.arange(0,360,5))
cands=[]
gx,gy=np.meshgrid(np.linspace(-15,15,31),np.linspace(-15,15,31)); G=np.stack([gx.ravel(),gy.ravel()],1)
T=P(0,10.8)
for a2 in A:
  M=P(a2,6,T)
  if np.linalg.norm(M)<10.8: continue
  for a3 in A:
    S1=P(a3,10.8,M)
    if np.linalg.norm(S1)<10.8 or np.linalg.norm(S1-T)<4.2: continue
    for a4 in A:
      S=P(a4,10.2,S1)
      if np.linalg.norm(S)<10.8 or np.linalg.norm(S-M)<10.8 or np.linalg.norm(S-T)<4.2: continue
      circ=[((0,0),9.9),(M,9.9),(S1,9.3),(S,5.6),(T,3.3)]
      f=np.max([np.linalg.norm(G-np.array(p),axis=1)+r for p,r in circ],axis=0)
      i=f.argmin(); cands.append((f[i],a2,a3,a4,G[i],M,S1,S))
cands.sort(key=lambda c:c[0]); print(len(cands))
for c in cands[:3]: print(c)
