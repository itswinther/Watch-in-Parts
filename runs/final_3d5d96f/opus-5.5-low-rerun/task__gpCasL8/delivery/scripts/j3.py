from joint import *
from joint2 import zpen, FREE
def build3(x):
    phA,phA2,thm,ax2,psx,psy,pss,thh,pst,psq=x[:10]
    P={}
    P['A']=B+pol(10.8,phA);P['A2']=B+pol(12.0,phA2)
    P['DM']=pol(2.7,thm);P['X2']=P['DM']+pol(2.7,ax2)
    P['X']=P['A']+pol(5.0,psx);P['Y']=P['X']+pol(4.275,psy);P['S']=P['Y']+pol(4.5,pss)
    P['DH']=pol(3.6,thh);P['T']=P['DH']+pol(5.4,pst);P['Q']=P['DH']+pol(4.5,psq)
    P['M']=C;P['H']=C
    pen=abs(np.linalg.norm(P['X2']-P['A'])-5.0)+abs(np.linalg.norm(P['Q']-P['A2'])-4.5)
    s=np.linalg.norm(P['S']);pen+=max(0,5.6-s)+max(0,s-7.5)
    pen+=max(0,8.35-np.linalg.norm(P['T']))
    return P,pen
def F3(x):
    P,pen=build3(x)
    b,m=viol(P)
    zs={k:round(v/0.02)*0.02 for k,v in zip(FREE,x[10:])}
    return 10*b+10*zpen(P,zs)+20*pen-min(m,0.3)
if __name__=="__main__":
    from scipy.optimize import differential_evolution
    bounds=[(0,90),(-40,0)]+[(0,360)]*8+[(ZMIN,ZMAX-TH[k]) for k in FREE]
    seed=int(sys.argv[1])
    r=differential_evolution(F3,bounds,seed=seed,maxiter=3000,popsize=50,tol=1e-12,mutation=(0.5,1.0),recombination=0.9,polish=False)
    print(seed,round(r.fun,4),np.round(r.x,3).tolist(),flush=True)
