import numpy as np
def circ(p,r1,q,r2,sign=1):
    p=np.array(p,float);q=np.array(q,float);d=np.linalg.norm(q-p)
    a=(r1*r1-r2*r2+d*d)/(2*d);h=np.sqrt(max(r1*r1-a*a,-1))
    if r1*r1-a*a<0: raise ValueError("no intersect %s %s %g %g d=%g"%(p,q,r1,r2,d))
    e=(q-p)/d;n=np.array([-e[1],e[0]])
    return p+a*e+sign*h*n
def pol(r,deg): return np.array([r*np.cos(np.radians(deg)),r*np.sin(np.radians(deg))])
