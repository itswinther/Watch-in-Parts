import json, math, numpy as np
from spec import *
from gearlib import *
lay=json.load(open('lay4_1.json'))
_,CL,LAY,ANG=lay
C=np.array([0.,0.]); I=np.array([-DCD,0.])
def u(t): return np.array([math.cos(t),math.sin(t)])
X1=C+D['dd']*u(ANG[0]); X2=X1+D['g1']*u(ANG[1]); X3=X2+D['g2']*u(ANG[2]); S=X3+D['g3']*u(ANG[3])
J=C+D['pq']*u(ANG[4]); K=C+D['sk']*u(ANG[5]); DD=K+D['kw']*u(ANG[6])
# barrel position
p=2.7; x=(BI**2-DCD**2-p**2)/(-2*DCD)*-1  # solve B.I = (p^2+DCD^2-BI^2)/2
BIdot=(p**2+DCD**2-BI**2)/2   # = B . I  = -DCD*x
Bx=BIdot/(-DCD); By=math.sqrt(p**2-Bx**2); B=np.array([Bx,By])
OFF=-B
POS=dict(B=B,I=I,M=C,H=C,X1=X1,X2=X2,X3=X3,S=S,J=J,K=K,D=DD)
LZ=lambda l:LAY_Z[l]
LAY_Z=dict(LAYERS)
Lg1,Lg2,Lg3,Lk=LAY
if __name__=="__main__":
    for k,v in POS.items(): print(k,np.round(v,3),round(float(np.linalg.norm(v)),3))
    print(LAY,CL, np.linalg.norm(B-I))
